"""Sealed Q011e dense forced quadratic fixed-leaf chart study."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy import linalg
from scipy.optimize import linear_sum_assignment

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011c_forced_spectral_cluster as q011c
import research.q011d_forced_quadratic_homological as q011d
from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    D2Q9_WEIGHTS,
    conserved_moment_matrix,
    global_conserved_quantities,
    macroscopic,
)
from ttim_lbm.manifold import log_log_slope
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

SIZE = q011d.SIZE
STATE_DIMENSION = SIZE * SIZE * 9
STRIPE_DIMENSION = SIZE * 9
SELECTED_DIMENSION = q011d.EXPECTED_SELECTED_DIMENSION
PAIR_COUNT = q011d.EXPECTED_PAIR_COUNT
SELECTED_BLOCK_ORDER = q011d.SELECTED_BLOCK_ORDER
OUTPUT_SECTOR_ORDER = q011d.OUTPUT_SECTOR_ORDER

Q011D_ARTIFACT_SHA256 = "c3acb9b7acc6e3121cb6e48a04bb060b5c95d7b128fe15fb11b67ee456337fd0"
Q011D_RUNNER_SHA256 = "815fe7e0101cc05cc44fcb224534762f0ef7625f8c9604ff0a822c13171a617d"
Q011D_INPUT_DIGEST = "ee2713e8169ea0f475ddee1b1233964ba40739d2276b78db3fff5410158dd2f8"
Q011D_LINEAR_DIGEST = "7208875ff95f3a768e4b822cf9be854228d6664800dfc69218c0e6a030a0c63e"
Q011D_PAIR_DIGEST = "f9caee5b591e74b40b497ca7eb8244f1bbaeba71d239684c47d8215c46c2fb0b"
Q011D_PROBE_DIGEST = "feb864e2725e0cf726b43c443bb48b53f34ba0ac54693bb97a2b986f598a1414"
Q011D_RESULT_DIGEST = "a6941371e54a5e4d4abbea2f835196ddd7cce35c7c266ce399020764ed5b9dd7"
Q011B_STORED_STATE_SHA256 = q011d.Q011B_STORED_STATE_SHA256
SEALED_PACKAGE_SOURCE_SHA256 = q011d.SEALED_PACKAGE_SOURCE_SHA256

STRUCTURAL_TOLERANCE = 1.0e-10
SYLVESTER_RESIDUAL_TOLERANCE = 1.0e-10
HOMOLOGICAL_RELATIVE_TOLERANCE = 1.0e-10
PAIRWISE_HOMOLOGICAL_TOLERANCE = 1.0e-9
GRAPH_GAUGE_TOLERANCE = 1.0e-10
CONSERVATION_TOLERANCE = 1.0e-10
SYMMETRY_TOLERANCE = 1.0e-12
FOURIER_LEAKAGE_TOLERANCE = 1.0e-12
NONTRIVIAL_NORM_FLOOR = 1.0e-12

HESSIAN_SEED = 20260823
HESSIAN_DIRECTION_PAIR_COUNT = 16
HESSIAN_COARSE_STEP = 0.004
HESSIAN_FINE_STEP = 0.002
HESSIAN_DISCREPANCY_TOLERANCE = 1.0e-6
HESSIAN_STEP_CHANGE_TOLERANCE = 1.0e-4
HESSIAN_DIRECTIONAL_NORM_FLOOR = 1.0e-8

RESIDUAL_SEED = 20260824
RESIDUAL_DIRECTION_COUNT = 32
RESIDUAL_AMPLITUDES = (1.0e-5, 2.0e-5, 4.0e-5, 8.0e-5, 1.6e-4)
RESIDUAL_NOISE_FLOOR = 1.0e-13
MINIMUM_ELIGIBLE_DIRECTION_COUNT = 28
LINEAR_SLOPE_INTERVAL = (1.85, 2.15)
QUADRATIC_SLOPE_INTERVAL = (2.70, 3.30)
MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO = 0.25


def _json_native(value: Any) -> Any:
    """Recursively replace NumPy scalars with strict-JSON native scalars."""

    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_native(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_native(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_json_native(item) for item in value)
    return value


@dataclass(frozen=True)
class InvariantSchurSplit:
    active_matrix: ComplexArray
    selected_basis: ComplexArray
    external_basis: ComplexArray
    selected_left: ComplexArray
    external_left: ComplexArray
    selected_dynamics: ComplexArray
    external_dynamics: ComplexArray
    projector: ComplexArray
    schur_unitary: ComplexArray
    coupling_solution: ComplexArray
    record: dict[str, Any]


@dataclass(frozen=True)
class ComplexLinearData:
    base: Array
    stripe_state: Array
    fixed_leaf_basis: Array
    selected_tangent: ComplexArray
    selected_left: ComplexArray
    selected_dynamics: ComplexArray
    selected_coordinate_eigenvalues: ComplexArray
    selected_splits: dict[int, InvariantSchurSplit]
    external_splits: dict[int, InvariantSchurSplit]
    pairs: tuple[tuple[int, int], ...]
    sector_indices: dict[int, list[int]]
    sector_actions: dict[int, ComplexArray]
    pair_action: ComplexArray
    audit: dict[str, Any]


@dataclass(frozen=True)
class RealForcedQuadraticModel:
    base: Array
    tangent: Array
    extractor: Array
    reduced_linear: Array
    hessian: Array
    reduced_hessian: Array
    second_derivative: Array

    def full_map(self, state: npt.ArrayLike) -> Array:
        value = np.asarray(state, dtype=np.float64)
        if value.shape != (STATE_DIMENSION,):
            raise ValueError("Q011e state has the wrong dimension")
        return q011b.zero_mean_forced_filtered_bgk_periodic_step(
            value.reshape(SIZE, SIZE, 9),
            q011c.OMEGA,
            q011c.ETA,
            q011b._full_force(),
        ).ravel()

    def chart(self, coordinates: npt.ArrayLike, *, quadratic: bool) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (SELECTED_DIMENSION,):
            raise ValueError("Q011e coordinate has the wrong dimension")
        result = self.base + self.tangent @ value
        if quadratic:
            result = result + 0.5 * np.einsum(
                "nij,i,j->n",
                self.hessian,
                value,
                value,
                optimize=True,
            )
        return np.asarray(result, dtype=np.float64)

    def reduced_map(
        self,
        coordinates: npt.ArrayLike,
        *,
        quadratic: bool,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (SELECTED_DIMENSION,):
            raise ValueError("Q011e coordinate has the wrong dimension")
        result = self.reduced_linear @ value
        if quadratic:
            result = result + 0.5 * np.einsum(
                "rij,i,j->r",
                self.reduced_hessian,
                value,
                value,
                optimize=True,
            )
        return np.asarray(result, dtype=np.float64)

    def invariance_defect(
        self,
        coordinates: npt.ArrayLike,
        *,
        quadratic: bool,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        return self.full_map(self.chart(value, quadratic=quadratic)) - self.chart(
            self.reduced_map(value, quadratic=quadratic),
            quadratic=quadratic,
        )


def _relative_norm(
    numerator: npt.ArrayLike,
    denominator: npt.ArrayLike,
) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).tiny)
    )


def _sealed_input_audit() -> tuple[dict[str, Any], Array, Array, dict[str, Any]]:
    artifact_directory = Path(__file__).resolve().parent / "artifacts"
    q011d_artifact_path = artifact_directory / "q011d_forced_quadratic_homological.json"
    q011b_artifact_path = artifact_directory / "q011b_zero_mean_forced_fixed_point.json"
    q011d_runner_path = Path(q011d.__file__).resolve()
    q011d_artifact = json.loads(q011d_artifact_path.read_text(encoding="utf-8"))
    q011b_artifact = json.loads(q011b_artifact_path.read_text(encoding="utf-8"))
    fresh_q011d_cycle = q011d.run_forced_quadratic_homological_audit()

    stripe_state = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    _conservation, fixed_leaf_basis, basis_audit = q011b._fixed_leaf_basis()
    digests = (
        fresh_q011d_cycle["input_digest_sha256"],
        fresh_q011d_cycle["linear_split_digest_sha256"],
        fresh_q011d_cycle["pair_family_digest_sha256"],
        fresh_q011d_cycle["sector_probe_digest_sha256"],
        fresh_q011d_cycle["result_digest_sha256"],
    )
    preserved = fresh_q011d_cycle["sealed_input_audit"]["preserved_prior_outcomes"]
    checks = {
        "q011d_artifact_sha256_matches": (
            _file_sha256(q011d_artifact_path) == Q011D_ARTIFACT_SHA256
        ),
        "q011d_runner_sha256_matches": (_file_sha256(q011d_runner_path) == Q011D_RUNNER_SHA256),
        "q011d_cycle_replays_exactly": q011d_artifact["cycle"] == fresh_q011d_cycle,
        "q011d_digests_match": (
            digests
            == (
                Q011D_INPUT_DIGEST,
                Q011D_LINEAR_DIGEST,
                Q011D_PAIR_DIGEST,
                Q011D_PROBE_DIGEST,
                Q011D_RESULT_DIGEST,
            )
        ),
        "q011d_accepted_outcome_reproduces": (
            fresh_q011d_cycle["study_validity"] == "passed"
            and fresh_q011d_cycle["hypothesis_outcome"] == "accepted"
            and fresh_q011d_cycle["scientific_classification"]
            == (
                "the forced quadratic external homological family is "
                "numerically nonresonant and solvable"
            )
            and all(gate["passed"] for gate in fresh_q011d_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in fresh_q011d_cycle["hypothesis_gates"].values())
        ),
        "prior_q011c_outcomes_remain_sealed": (
            preserved["q011c1_study_validity"] == "passed"
            and preserved["q011c1_hypothesis_outcome"] == "accepted"
            and preserved["q011c_study_validity"] == "failed"
            and preserved["q011c_hypothesis_outcome"] == "inconclusive"
        ),
        "stored_endpoint_sha256_matches": (
            q011c._array_sha256(stripe_state) == Q011B_STORED_STATE_SHA256
        ),
        "fixed_leaf_basis_reconstructs": basis_audit["passed"],
        "package_source_sha256_matches": (
            source_metadata()["package_source_sha256"] == SEALED_PACKAGE_SOURCE_SHA256
        ),
    }
    audit = {
        "q011d_artifact": {
            "filename": q011d_artifact_path.name,
            "sha256": _file_sha256(q011d_artifact_path),
            "runner_filename": q011d_runner_path.name,
            "runner_sha256": _file_sha256(q011d_runner_path),
            "input_digest_sha256": fresh_q011d_cycle["input_digest_sha256"],
            "linear_split_digest_sha256": fresh_q011d_cycle["linear_split_digest_sha256"],
            "pair_family_digest_sha256": fresh_q011d_cycle["pair_family_digest_sha256"],
            "sector_probe_digest_sha256": fresh_q011d_cycle["sector_probe_digest_sha256"],
            "result_digest_sha256": fresh_q011d_cycle["result_digest_sha256"],
            "study_validity": fresh_q011d_cycle["study_validity"],
            "hypothesis_outcome": fresh_q011d_cycle["hypothesis_outcome"],
            "scientific_classification": fresh_q011d_cycle["scientific_classification"],
        },
        "preserved_prior_outcomes": preserved,
        "q011b_endpoint": {
            "artifact_filename": q011b_artifact_path.name,
            "stored_state_sha256": q011c._array_sha256(stripe_state),
            "fixed_leaf_basis_audit": basis_audit,
        },
        "package_source_sha256": source_metadata()["package_source_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, stripe_state, fixed_leaf_basis, q011d_artifact


def _ordered_invariant_split(
    matrix: npt.ArrayLike,
    target_eigenvalues: npt.ArrayLike,
) -> InvariantSchurSplit:
    value = np.asarray(matrix, dtype=np.complex128)
    targets = np.asarray(target_eigenvalues, dtype=np.complex128).ravel()
    all_values = linalg.eigvals(value, check_finite=True)
    rows, columns = linear_sum_assignment(np.abs(targets[:, None] - all_values[None, :]))
    if rows.size != targets.size:
        raise np.linalg.LinAlgError("Q011e Hungarian cluster match is incomplete")
    selected_indices = {int(index) for index in columns}
    selected_reference = all_values[sorted(selected_indices)]
    excluded_reference = all_values[
        [index for index in range(all_values.size) if index not in selected_indices]
    ]

    def selector(eigenvalue: complex) -> bool:
        return float(np.min(np.abs(eigenvalue - selected_reference))) < float(
            np.min(np.abs(eigenvalue - excluded_reference))
        )

    triangular, unitary, count = linalg.schur(
        value,
        output="complex",
        sort=selector,
        check_finite=True,
    )
    selected_dimension = targets.size
    if count != selected_dimension:
        raise np.linalg.LinAlgError("Q011e ordered Schur dimension changed")
    triangular = np.asarray(triangular, dtype=np.complex128)
    unitary = np.asarray(unitary, dtype=np.complex128)
    selected = triangular[:selected_dimension, :selected_dimension]
    coupling = triangular[:selected_dimension, selected_dimension:]
    external = triangular[selected_dimension:, selected_dimension:]
    coupling_solution = linalg.solve_sylvester(
        selected,
        -external,
        coupling,
    )
    selected_basis = unitary[:, :selected_dimension]
    orthogonal_external = unitary[:, selected_dimension:]
    external_basis = orthogonal_external - selected_basis @ coupling_solution
    selected_left = selected_basis.conj().T + coupling_solution @ orthogonal_external.conj().T
    external_left = orthogonal_external.conj().T
    projector = selected_basis @ selected_left
    scale = max(float(np.linalg.norm(value, ord="fro")), np.finfo(float).tiny)
    metrics = {
        "schur_reconstruction_relative_residual": float(
            np.linalg.norm(
                value - unitary @ triangular @ unitary.conj().T,
                ord="fro",
            )
            / scale
        ),
        "schur_unitarity_frobenius_residual": float(
            np.linalg.norm(
                unitary.conj().T @ unitary - np.eye(value.shape[0]),
                ord="fro",
            )
        ),
        "selected_invariance_relative_residual": float(
            np.linalg.norm(
                value @ selected_basis - selected_basis @ selected,
                ord="fro",
            )
            / scale
        ),
        "external_invariance_relative_residual": float(
            np.linalg.norm(
                value @ external_basis - external_basis @ external,
                ord="fro",
            )
            / scale
        ),
        "selected_duality_frobenius_residual": float(
            np.linalg.norm(
                selected_left @ selected_basis - np.eye(selected_dimension),
                ord="fro",
            )
        ),
        "external_duality_frobenius_residual": float(
            np.linalg.norm(
                external_left @ external_basis - np.eye(external.shape[0]),
                ord="fro",
            )
        ),
        "selected_annihilates_external_frobenius_residual": float(
            np.linalg.norm(selected_left @ external_basis, ord="fro")
        ),
        "external_annihilates_selected_frobenius_residual": float(
            np.linalg.norm(external_left @ selected_basis, ord="fro")
        ),
        "projector_idempotency_frobenius_residual": float(
            np.linalg.norm(projector @ projector - projector, ord="fro")
        ),
        "projector_commutator_relative_residual": float(
            np.linalg.norm(value @ projector - projector @ value, ord="fro") / scale
        ),
    }
    record = {
        "active_dimension": int(value.shape[0]),
        "selected_dimension": int(selected_dimension),
        "external_dimension": int(external.shape[0]),
        "selected_dynamics_sha256": q011c._array_sha256(selected),
        "external_dynamics_sha256": q011c._array_sha256(external),
        "selected_basis_sha256": q011c._array_sha256(selected_basis),
        "external_basis_sha256": q011c._array_sha256(external_basis),
        "selected_left_sha256": q011c._array_sha256(selected_left),
        "external_left_sha256": q011c._array_sha256(external_left),
        "projector_sha256": q011c._array_sha256(projector),
        "coupling_solution_sha256": q011c._array_sha256(coupling_solution),
        **metrics,
        "maximum_structural_residual": max(metrics.values()),
    }
    return InvariantSchurSplit(
        active_matrix=value,
        selected_basis=np.asarray(selected_basis),
        external_basis=np.asarray(external_basis),
        selected_left=np.asarray(selected_left),
        external_left=np.asarray(external_left),
        selected_dynamics=np.asarray(selected),
        external_dynamics=np.asarray(external),
        projector=np.asarray(projector),
        schur_unitary=np.asarray(unitary),
        coupling_solution=np.asarray(coupling_solution),
        record=record,
    )


def _full_external_split(matrix: npt.ArrayLike) -> InvariantSchurSplit:
    value = np.asarray(matrix, dtype=np.complex128)
    triangular, unitary = linalg.schur(
        value,
        output="complex",
        check_finite=True,
    )
    triangular = np.asarray(triangular, dtype=np.complex128)
    unitary = np.asarray(unitary, dtype=np.complex128)
    scale = max(float(np.linalg.norm(value, ord="fro")), np.finfo(float).tiny)
    reconstruction = float(
        np.linalg.norm(
            value - unitary @ triangular @ unitary.conj().T,
            ord="fro",
        )
        / scale
    )
    unitarity = float(
        np.linalg.norm(
            unitary.conj().T @ unitary - np.eye(value.shape[0]),
            ord="fro",
        )
    )
    record = {
        "active_dimension": int(value.shape[0]),
        "selected_dimension": 0,
        "external_dimension": int(value.shape[0]),
        "external_dynamics_sha256": q011c._array_sha256(triangular),
        "external_basis_sha256": q011c._array_sha256(unitary),
        "external_left_sha256": q011c._array_sha256(unitary.conj().T),
        "schur_reconstruction_relative_residual": reconstruction,
        "schur_unitarity_frobenius_residual": unitarity,
        "maximum_structural_residual": max(reconstruction, unitarity),
    }
    empty_basis = np.zeros((value.shape[0], 0), dtype=np.complex128)
    empty_left = np.zeros((0, value.shape[0]), dtype=np.complex128)
    return InvariantSchurSplit(
        active_matrix=value,
        selected_basis=empty_basis,
        external_basis=unitary,
        selected_left=empty_left,
        external_left=unitary.conj().T,
        selected_dynamics=np.zeros((0, 0), dtype=np.complex128),
        external_dynamics=triangular,
        projector=np.zeros_like(value),
        schur_unitary=unitary,
        coupling_solution=np.zeros((0, value.shape[0]), dtype=np.complex128),
        record=record,
    )


def _embed_block(value: npt.ArrayLike, block_index: int) -> ComplexArray:
    columns = np.asarray(value, dtype=np.complex128)
    if columns.ndim == 1:
        columns = columns[:, None]
    field = columns.reshape(SIZE, 9, columns.shape[1])
    x = np.arange(SIZE, dtype=np.float64)
    phase = np.exp(2j * np.pi * block_index * x / SIZE) / np.sqrt(SIZE)
    return np.einsum("yqm,x->yxqm", field, phase).reshape(
        STATE_DIMENSION,
        columns.shape[1],
    )


def _selected_left_full_grid(
    stripe_left: npt.ArrayLike,
    block_index: int,
) -> ComplexArray:
    rows = np.asarray(stripe_left, dtype=np.complex128)
    field = rows.reshape(rows.shape[0], SIZE, 9)
    x = np.arange(SIZE, dtype=np.float64)
    phase = np.exp(-2j * np.pi * block_index * x / SIZE) / np.sqrt(SIZE)
    return np.einsum("ryq,x->ryxq", field, phase).reshape(
        rows.shape[0],
        STATE_DIMENSION,
    )


def _complex_linear_data(
    stripe_state: Array,
    fixed_leaf_basis: Array,
    q011d_artifact: dict[str, Any],
) -> ComplexLinearData:
    reference_bases, reference_targets, reference_audit = q011c._reference_audit(fixed_leaf_basis)
    del reference_bases
    selected_splits: dict[int, InvariantSchurSplit] = {}
    external_splits: dict[int, InvariantSchurSplit] = {}
    selected_tangent_blocks: list[ComplexArray] = []
    selected_left_blocks: list[ComplexArray] = []
    selected_records: list[dict[str, Any]] = []

    for block_index in SELECTED_BLOCK_ORDER:
        active = q011c._active_matrix(
            stripe_state,
            block_index,
            fixed_leaf_basis,
        )
        split = _ordered_invariant_split(
            active,
            reference_targets[block_index],
        )
        selected_splits[block_index] = split
        external_splits[block_index] = split
        if block_index == 0:
            physical_selected = fixed_leaf_basis @ split.selected_basis
            physical_left = split.selected_left @ fixed_leaf_basis.T
        else:
            physical_selected = split.selected_basis
            physical_left = split.selected_left
        selected_tangent_blocks.append(_embed_block(physical_selected, block_index))
        selected_left_blocks.append(_selected_left_full_grid(physical_left, block_index))
        selected_records.append({"block_index": block_index, **split.record})

    external_records: list[dict[str, Any]] = []
    for block_index in (2, 15):
        active = q011c._active_matrix(
            stripe_state,
            block_index,
            fixed_leaf_basis,
        )
        split = _full_external_split(active)
        external_splits[block_index] = split
        external_records.append({"block_index": block_index, **split.record})

    selected_tangent = np.column_stack(selected_tangent_blocks)
    selected_left = np.vstack(selected_left_blocks)
    selected_dynamics = np.asarray(
        linalg.block_diag(
            *(selected_splits[index].selected_dynamics for index in SELECTED_BLOCK_ORDER)
        ),
        dtype=np.complex128,
    )
    selected_eigenvalues = np.concatenate(
        [np.diag(selected_splits[index].selected_dynamics) for index in SELECTED_BLOCK_ORDER]
    )
    quadratic_action, pairs, sector_indices, sector_actions, _products = (
        q011d._quadratic_input_action_audit(
            selected_dynamics,
            selected_eigenvalues,
        )
    )
    pair_action = q011d._assemble_symmetric_product(
        selected_dynamics,
        pairs,
    )
    stripe_full = np.repeat(stripe_state, SIZE, axis=1)
    base = np.asarray(stripe_full, dtype=np.float64).ravel()
    jacobian = q011b.RectangularFilteredBGKJacobian.at_state(
        stripe_full,
        q011c.OMEGA,
        q011c.ETA,
    )
    tangent_scale = max(
        float(np.linalg.norm(selected_tangent, ord="fro")),
        np.finfo(float).tiny,
    )
    linear_invariance = float(
        np.linalg.norm(
            jacobian.matmat(selected_tangent) - selected_tangent @ selected_dynamics,
            ord="fro",
        )
        / tangent_scale
    )
    orthonormality = float(
        np.linalg.norm(
            selected_tangent.conj().T @ selected_tangent - np.eye(SELECTED_DIMENSION),
            ord="fro",
        )
    )
    duality = float(
        np.linalg.norm(
            selected_left @ selected_tangent - np.eye(SELECTED_DIMENSION),
            ord="fro",
        )
    )
    conjugacy_closure = float(
        np.linalg.norm(
            np.conjugate(selected_tangent)
            - selected_tangent @ (selected_tangent.conj().T @ np.conjugate(selected_tangent)),
            ord="fro",
        )
        / tangent_scale
    )

    q011d_linear = q011d_artifact["cycle"]["canonical_linear_split_audit"]
    q011d_action = q011d_artifact["cycle"]["quadratic_input_action_audit"]
    q011d_selected_hashes = q011d_linear["selected_block_record_hashes"]
    q011d_external_hashes = q011d_linear["full_external_sector_hashes"]
    structural_maximum = max(
        max(record["maximum_structural_residual"] for record in selected_records),
        max(record["maximum_structural_residual"] for record in external_records),
        linear_invariance,
        orthonormality,
        duality,
        conjugacy_closure,
    )
    checks = {
        "unforced_reference_reconstructs": reference_audit["passed"],
        "selected_dimensions_are_six_nine_nine": (
            [record["selected_dimension"] for record in selected_records] == [6, 9, 9]
        ),
        "external_dimensions_are_registered": all(
            external_splits[index].external_dynamics.shape[0]
            == q011d.EXTERNAL_SECTOR_DIMENSIONS[index]
            for index in OUTPUT_SECTOR_ORDER
        ),
        "q011d_selected_dynamics_hashes_reproduce": all(
            selected_splits[index].record["selected_dynamics_sha256"]
            == q011d_selected_hashes[str(index)]
            for index in SELECTED_BLOCK_ORDER
        ),
        "q011d_external_dynamics_hashes_reproduce": all(
            external_splits[index].record["external_dynamics_sha256"]
            == (
                next(
                    record["external_dynamics_sha256"]
                    for record in q011d_linear["selected_block_records"]
                    if record["block_index"] == index
                )
                if index in SELECTED_BLOCK_ORDER
                else q011d_external_hashes[str(index)]
            )
            for index in OUTPUT_SECTOR_ORDER
        ),
        "q011d_pair_enumeration_reproduces": (
            quadratic_action["pair_enumeration_sha256"] == q011d_action["pair_enumeration_sha256"]
            and quadratic_action["symmetric_product_sha256"]
            == q011d_action["symmetric_product_sha256"]
        ),
        "unitary_fourier_tangent_is_orthonormal": (orthonormality <= STRUCTURAL_TOLERANCE),
        "complex_linear_invariance_is_within_tolerance": (
            linear_invariance <= STRUCTURAL_TOLERANCE
        ),
        "spectral_left_duality_is_within_tolerance": (duality <= STRUCTURAL_TOLERANCE),
        "selected_range_is_conjugacy_closed": (conjugacy_closure <= STRUCTURAL_TOLERANCE),
        "all_invariant_complement_residuals_are_within_tolerance": (
            structural_maximum <= STRUCTURAL_TOLERANCE
        ),
        "all_linear_values_are_finite": bool(
            np.all(np.isfinite(selected_tangent))
            and np.all(np.isfinite(selected_left))
            and np.all(np.isfinite(selected_dynamics))
            and _all_numeric_values_finite(selected_records)
            and _all_numeric_values_finite(external_records)
        ),
    }
    audit = {
        "fourier_embedding": ("E_k(v)(y,x,q)=N^(-1/2)*exp(2*pi*i*k*x/N)*v(y,q)"),
        "selected_block_records": selected_records,
        "external_full_schur_records": external_records,
        "selected_tangent_shape": list(selected_tangent.shape),
        "selected_tangent_sha256": q011c._array_sha256(selected_tangent),
        "selected_left_sha256": q011c._array_sha256(selected_left),
        "selected_dynamics_sha256": q011c._array_sha256(selected_dynamics),
        "pair_enumeration_sha256": quadratic_action["pair_enumeration_sha256"],
        "pair_action_sha256": q011c._array_sha256(pair_action),
        "complex_tangent_orthonormality_frobenius_residual": orthonormality,
        "complex_linear_invariance_relative_residual": linear_invariance,
        "spectral_left_duality_frobenius_residual": duality,
        "selected_conjugacy_closure_relative_residual": conjugacy_closure,
        "maximum_structural_residual": structural_maximum,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return ComplexLinearData(
        base=base,
        stripe_state=stripe_state,
        fixed_leaf_basis=fixed_leaf_basis,
        selected_tangent=selected_tangent,
        selected_left=selected_left,
        selected_dynamics=selected_dynamics,
        selected_coordinate_eigenvalues=selected_eigenvalues,
        selected_splits=selected_splits,
        external_splits=external_splits,
        pairs=pairs,
        sector_indices=sector_indices,
        sector_actions=sector_actions,
        pair_action=pair_action,
        audit=audit,
    )


def _filter_tensor(field: npt.ArrayLike) -> np.ndarray:
    value = np.asarray(field)
    neighbours = (
        np.roll(value, 1, axis=0)
        + np.roll(value, -1, axis=0)
        + np.roll(value, 1, axis=1)
        + np.roll(value, -1, axis=1)
    )
    return (1.0 - q011c.ETA) * value + 0.25 * q011c.ETA * neighbours


def _local_equilibrium_hessian(state: npt.ArrayLike) -> Array:
    populations = np.asarray(state, dtype=np.float64)
    density, momentum = macroscopic(populations)
    velocity_projection = np.einsum(
        "yxd,qd->yxq",
        momentum,
        D2Q9_VELOCITIES,
    )
    momentum_square = np.sum(momentum * momentum, axis=-1)
    quadratic = 4.5 * velocity_projection * velocity_projection - 1.5 * momentum_square[..., None]
    gradient = (
        9.0 * velocity_projection[..., None] * D2Q9_VELOCITIES[None, None, :, :]
        - 3.0 * momentum[:, :, None, :]
    )
    hessian = np.zeros((*populations.shape, 3, 3), dtype=np.float64)
    hessian[..., 0, 0] = 2.0 * D2Q9_WEIGHTS[None, None, :] * quadratic / density[..., None] ** 3
    cross = -D2Q9_WEIGHTS[None, None, :, None] * gradient / density[..., None, None] ** 2
    hessian[..., 0, 1:] = cross
    hessian[..., 1:, 0] = cross
    velocity_outer = np.einsum(
        "qd,qe->qde",
        D2Q9_VELOCITIES,
        D2Q9_VELOCITIES,
    )
    momentum_block = D2Q9_WEIGHTS[:, None, None] * (
        9.0 * velocity_outer - 3.0 * np.eye(2)[None, :, :]
    )
    hessian[..., 1:, 1:] = momentum_block[None, None, :, :, :] / density[..., None, None, None]
    return hessian


def _analytic_second_derivative(
    base: npt.ArrayLike,
    tangent: npt.ArrayLike,
) -> np.ndarray:
    state = np.asarray(base, dtype=np.float64).reshape(SIZE, SIZE, 9)
    columns = np.asarray(tangent)
    if columns.ndim != 2 or columns.shape[0] != STATE_DIMENSION:
        raise ValueError("Q011e tangent has the wrong shape")
    field = columns.reshape(SIZE, SIZE, 9, columns.shape[1])
    moments = np.einsum(
        "aq,yxqj->yxaj",
        conserved_moment_matrix(),
        field,
    )
    local = q011c.OMEGA * np.einsum(
        "yxqab,yxai,yxbj->yxqij",
        _local_equilibrium_hessian(state),
        moments,
        moments,
        optimize=True,
    )
    streamed = np.empty_like(local)
    for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(np.int64)):
        streamed[:, :, population] = np.roll(
            local[:, :, population],
            shift=(int(cy), int(cx)),
            axis=(0, 1),
        )
    return _filter_tensor(streamed).reshape(
        STATE_DIMENSION,
        columns.shape[1],
        columns.shape[1],
    )


def _real_linear_coordinates(
    linear: ComplexLinearData,
) -> tuple[Array, Array, Array, ComplexArray, dict[str, Any]]:
    candidate = np.column_stack((linear.selected_tangent.real, linear.selected_tangent.imag))
    unitary, triangular, pivots = linalg.qr(
        candidate,
        mode="economic",
        pivoting=True,
        check_finite=True,
    )
    tangent = np.asarray(unitary[:, :SELECTED_DIMENSION], dtype=np.float64)
    signs: list[int] = []
    for column in range(SELECTED_DIMENSION):
        witness = int(np.argmax(np.abs(tangent[:, column])))
        sign = 1 if tangent[witness, column] >= 0.0 else -1
        tangent[:, column] *= sign
        signs.append(sign)
    coordinate_map = linear.selected_tangent.conj().T @ tangent
    reduced_linear_complex = coordinate_map.conj().T @ linear.selected_dynamics @ coordinate_map
    extractor_complex = coordinate_map.conj().T @ linear.selected_left
    extractor = np.asarray(extractor_complex.real, dtype=np.float64)
    reduced_linear = np.asarray(reduced_linear_complex.real, dtype=np.float64)
    jacobian = q011b.RectangularFilteredBGKJacobian.at_state(
        linear.base.reshape(SIZE, SIZE, 9),
        q011c.OMEGA,
        q011c.ETA,
    )
    candidate_singular_values = linalg.svdvals(candidate, check_finite=True)
    range_residual = _relative_norm(
        tangent - linear.selected_tangent @ coordinate_map,
        tangent,
    )
    coordinate_unitarity = float(
        np.linalg.norm(
            coordinate_map.conj().T @ coordinate_map - np.eye(SELECTED_DIMENSION),
            ord="fro",
        )
    )
    tangent_orthonormality = float(
        np.linalg.norm(
            tangent.T @ tangent - np.eye(SELECTED_DIMENSION),
            ord="fro",
        )
    )
    extractor_duality = float(
        np.linalg.norm(
            extractor @ tangent - np.eye(SELECTED_DIMENSION),
            ord="fro",
        )
    )
    linear_invariance = _relative_norm(
        jacobian.matmat(tangent) - tangent @ reduced_linear,
        tangent,
    )
    reduced_imaginary = _relative_norm(
        reduced_linear_complex.imag,
        reduced_linear_complex.real,
    )
    extractor_imaginary = _relative_norm(
        extractor_complex.imag,
        extractor_complex.real,
    )
    checks = {
        "real_candidate_rank_is_twenty_four": (
            np.count_nonzero(
                candidate_singular_values
                > (
                    100.0
                    * np.finfo(float).eps
                    * max(candidate.shape)
                    * candidate_singular_values[0]
                )
            )
            == SELECTED_DIMENSION
        ),
        "real_tangent_is_orthonormal": (tangent_orthonormality <= STRUCTURAL_TOLERANCE),
        "real_tangent_lies_in_complex_selected_range": (range_residual <= STRUCTURAL_TOLERANCE),
        "complex_coordinate_map_is_unitary": (coordinate_unitarity <= STRUCTURAL_TOLERANCE),
        "real_extractor_is_dual": extractor_duality <= STRUCTURAL_TOLERANCE,
        "real_linear_dynamics_is_invariant": (linear_invariance <= STRUCTURAL_TOLERANCE),
        "reduced_linear_imaginary_leakage_is_small": (reduced_imaginary <= STRUCTURAL_TOLERANCE),
        "extractor_imaginary_leakage_is_small": (extractor_imaginary <= STRUCTURAL_TOLERANCE),
        "all_real_linear_values_are_finite": bool(
            np.all(np.isfinite(tangent))
            and np.all(np.isfinite(extractor))
            and np.all(np.isfinite(reduced_linear))
            and np.all(np.isfinite(coordinate_map))
        ),
    }
    audit = {
        "candidate_shape": list(candidate.shape),
        "candidate_sha256": q011c._array_sha256(candidate),
        "candidate_singular_values": [float(value) for value in candidate_singular_values],
        "qr_pivots": [int(value) for value in pivots],
        "qr_column_signs": signs,
        "qr_triangular_sha256": q011c._array_sha256(triangular),
        "real_tangent_sha256": q011c._array_sha256(tangent),
        "coordinate_map_sha256": q011c._array_sha256(coordinate_map),
        "real_extractor_sha256": q011c._array_sha256(extractor),
        "real_reduced_linear_sha256": q011c._array_sha256(reduced_linear),
        "real_tangent_orthonormality_frobenius_residual": (tangent_orthonormality),
        "complex_range_relative_residual": range_residual,
        "coordinate_map_unitarity_frobenius_residual": coordinate_unitarity,
        "real_extractor_duality_frobenius_residual": extractor_duality,
        "real_linear_invariance_relative_residual": linear_invariance,
        "reduced_linear_imaginary_leakage_relative_norm": reduced_imaginary,
        "extractor_imaginary_leakage_relative_norm": extractor_imaginary,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return tangent, extractor, reduced_linear, coordinate_map, audit


def _extract_block_columns(
    columns: npt.ArrayLike,
    block_index: int,
) -> ComplexArray:
    value = np.asarray(columns, dtype=np.complex128)
    if value.ndim == 1:
        value = value[:, None]
    field = value.reshape(SIZE, SIZE, 9, value.shape[1])
    transformed = np.fft.fft(field, axis=1) / np.sqrt(SIZE)
    return np.asarray(
        transformed[:, block_index, :, :].reshape(
            STRIPE_DIMENSION,
            value.shape[1],
        )
    )


def _fourier_leakage(
    columns: npt.ArrayLike,
    included_sectors: tuple[int, ...],
) -> float:
    value = np.asarray(columns)
    field = value.reshape(SIZE, SIZE, 9, -1)
    transformed = np.fft.fft(field, axis=1) / np.sqrt(SIZE)
    mask = np.ones(SIZE, dtype=bool)
    mask[list(included_sectors)] = False
    return _relative_norm(transformed[:, mask], transformed)


def _quadratic_construction(
    linear: ComplexLinearData,
) -> tuple[ComplexArray, ComplexArray, ComplexArray, dict[str, Any]]:
    analytic_hessian = np.asarray(
        _analytic_second_derivative(
            linear.base,
            linear.selected_tangent,
        ),
        dtype=np.complex128,
    )
    pairs = linear.pairs
    forcing_polynomial = np.empty(
        (STATE_DIMENSION, PAIR_COUNT),
        dtype=np.complex128,
    )
    for pair_index, (left, right) in enumerate(pairs):
        factor = 0.5 if left == right else 1.0
        forcing_polynomial[:, pair_index] = factor * analytic_hessian[:, left, right]

    chart_polynomial = np.zeros_like(forcing_polynomial)
    reduced_polynomial = np.zeros(
        (SELECTED_DIMENSION, PAIR_COUNT),
        dtype=np.complex128,
    )
    selected_offsets = {0: slice(0, 6), 1: slice(6, 15), 16: slice(15, 24)}
    sector_records: list[dict[str, Any]] = []
    for sector in OUTPUT_SECTOR_ORDER:
        pair_indices = linear.sector_indices[sector]
        split = linear.external_splits[sector]
        block_forcing = _extract_block_columns(
            forcing_polynomial[:, pair_indices],
            sector,
        )
        if sector == 0:
            active_forcing = linear.fixed_leaf_basis.T @ block_forcing
        else:
            active_forcing = block_forcing
        external_forcing = split.external_left @ active_forcing
        selected_forcing = split.selected_left @ active_forcing
        pair_action = linear.sector_actions[sector]
        external_solution = linalg.solve_sylvester(
            split.external_dynamics,
            -pair_action,
            -external_forcing,
        )
        equation_residual = (
            split.external_dynamics @ external_solution
            - external_solution @ pair_action
            + external_forcing
        )
        solve_residual = _relative_norm(
            equation_residual,
            external_forcing,
        )
        active_chart = split.external_basis @ external_solution
        if sector == 0:
            physical_chart = linear.fixed_leaf_basis @ active_chart
        else:
            physical_chart = active_chart
        chart_polynomial[:, pair_indices] = _embed_block(
            physical_chart,
            sector,
        )
        if sector in selected_offsets:
            reduced_polynomial[
                selected_offsets[sector],
                pair_indices,
            ] = selected_forcing
        sector_records.append(
            {
                "output_sector": sector,
                "pair_count": len(pair_indices),
                "external_dimension": int(split.external_dynamics.shape[0]),
                "operator_scalar_dimension": int(
                    split.external_dynamics.shape[0] * len(pair_indices)
                ),
                "forcing_frobenius_norm": float(np.linalg.norm(active_forcing, ord="fro")),
                "external_forcing_frobenius_norm": float(
                    np.linalg.norm(external_forcing, ord="fro")
                ),
                "selected_forcing_frobenius_norm": float(
                    np.linalg.norm(selected_forcing, ord="fro")
                ),
                "external_solution_frobenius_norm": float(
                    np.linalg.norm(external_solution, ord="fro")
                ),
                "equation_relative_residual": solve_residual,
                "external_solution_sha256": q011c._array_sha256(external_solution),
                "selected_polynomial_sha256": q011c._array_sha256(selected_forcing),
                "passed": solve_residual <= SYLVESTER_RESIDUAL_TOLERANCE,
            }
        )

    jacobian = q011b.RectangularFilteredBGKJacobian.at_state(
        linear.base.reshape(SIZE, SIZE, 9),
        q011c.OMEGA,
        q011c.ETA,
    )
    homological = (
        jacobian.matmat(chart_polynomial)
        + forcing_polynomial
        - linear.selected_tangent @ reduced_polynomial
        - chart_polynomial @ linear.pair_action
    )
    component_scales = np.maximum.reduce(
        [
            np.linalg.norm(
                jacobian.matmat(chart_polynomial),
                axis=0,
            ),
            np.linalg.norm(forcing_polynomial, axis=0),
            np.linalg.norm(
                linear.selected_tangent @ reduced_polynomial,
                axis=0,
            ),
            np.linalg.norm(chart_polynomial @ linear.pair_action, axis=0),
            np.full(PAIR_COUNT, np.finfo(float).tiny),
        ]
    )
    pairwise_residuals = np.linalg.norm(homological, axis=0) / component_scales
    graph_gauge = _relative_norm(
        linear.selected_left @ chart_polynomial,
        chart_polynomial,
    )
    conservation = np.tile(
        conserved_moment_matrix(),
        (1, SIZE * SIZE),
    )
    tangent_conservation = _relative_norm(
        conservation @ linear.selected_tangent,
        linear.selected_tangent,
    )
    chart_conservation = _relative_norm(
        conservation @ chart_polynomial,
        chart_polynomial,
    )
    zero_indices = linear.sector_indices[0]
    zero_conservation = _relative_norm(
        conservation @ chart_polynomial[:, zero_indices],
        chart_polynomial[:, zero_indices],
    )
    forcing_leakage = _fourier_leakage(
        forcing_polynomial,
        OUTPUT_SECTOR_ORDER,
    )
    chart_leakage = _fourier_leakage(
        chart_polynomial,
        OUTPUT_SECTOR_ORDER,
    )

    chart_hessian = np.zeros(
        (STATE_DIMENSION, SELECTED_DIMENSION, SELECTED_DIMENSION),
        dtype=np.complex128,
    )
    reduced_hessian = np.zeros(
        (SELECTED_DIMENSION, SELECTED_DIMENSION, SELECTED_DIMENSION),
        dtype=np.complex128,
    )
    pair_records: list[dict[str, Any]] = []
    for pair_index, (left, right) in enumerate(pairs):
        factor = 2.0 if left == right else 1.0
        chart_coefficient = factor * chart_polynomial[:, pair_index]
        reduced_coefficient = factor * reduced_polynomial[:, pair_index]
        chart_hessian[:, left, right] = chart_coefficient
        chart_hessian[:, right, left] = chart_coefficient
        reduced_hessian[:, left, right] = reduced_coefficient
        reduced_hessian[:, right, left] = reduced_coefficient
        pair_records.append(
            {
                "pair_index": pair_index,
                "coordinate_indices": [left, right],
                "output_sector": next(
                    sector
                    for sector, indices in linear.sector_indices.items()
                    if pair_index in indices
                ),
                "diagonal_polynomial_factor": (0.5 if left == right else 1.0),
                "forcing_polynomial_norm": float(np.linalg.norm(forcing_polynomial[:, pair_index])),
                "chart_polynomial_norm": float(np.linalg.norm(chart_polynomial[:, pair_index])),
                "reduced_polynomial_norm": float(np.linalg.norm(reduced_polynomial[:, pair_index])),
                "homological_relative_residual": float(pairwise_residuals[pair_index]),
            }
        )

    chart_symmetry = _relative_norm(
        chart_hessian - chart_hessian.swapaxes(1, 2),
        chart_hessian,
    )
    reduced_symmetry = _relative_norm(
        reduced_hessian - reduced_hessian.swapaxes(1, 2),
        reduced_hessian,
    )
    full_homological = _relative_norm(homological, forcing_polynomial)
    maximum_pairwise = float(np.max(pairwise_residuals))
    maximum_sector_residual = max(record["equation_relative_residual"] for record in sector_records)
    analytic_norm = float(np.linalg.norm(analytic_hessian))
    chart_norm = float(np.linalg.norm(chart_hessian))
    reduced_norm = float(np.linalg.norm(reduced_hessian))
    structural_checks = {
        "all_three_hundred_pairs_are_enumerated": (
            len(pair_records) == PAIR_COUNT
            and [record["pair_index"] for record in pair_records] == list(range(PAIR_COUNT))
        ),
        "sector_pair_counts_are_registered": all(
            len(linear.sector_indices[sector]) == q011d.EXPECTED_SECTOR_PAIR_COUNTS[sector]
            for sector in OUTPUT_SECTOR_ORDER
        ),
        "all_quadratic_values_are_finite": bool(
            np.all(np.isfinite(analytic_hessian))
            and np.all(np.isfinite(chart_hessian))
            and np.all(np.isfinite(reduced_hessian))
            and _all_numeric_values_finite(sector_records)
            and _all_numeric_values_finite(pair_records)
        ),
    }
    hypothesis_checks = {
        "all_five_sector_sylvester_solves_pass": all(record["passed"] for record in sector_records),
        "full_homological_residual_is_within_tolerance": (
            full_homological <= HOMOLOGICAL_RELATIVE_TOLERANCE
        ),
        "pairwise_homological_residuals_are_within_tolerance": (
            maximum_pairwise <= PAIRWISE_HOMOLOGICAL_TOLERANCE
        ),
        "graph_gauge_is_within_tolerance": (graph_gauge <= GRAPH_GAUGE_TOLERANCE),
        "tangent_and_chart_preserve_fixed_leaf": (
            tangent_conservation <= CONSERVATION_TOLERANCE
            and chart_conservation <= CONSERVATION_TOLERANCE
            and zero_conservation <= CONSERVATION_TOLERANCE
        ),
        "hessian_symmetries_are_within_tolerance": (
            chart_symmetry <= SYMMETRY_TOLERANCE and reduced_symmetry <= SYMMETRY_TOLERANCE
        ),
        "kx_selection_rules_are_within_tolerance": (
            forcing_leakage <= FOURIER_LEAKAGE_TOLERANCE
            and chart_leakage <= FOURIER_LEAKAGE_TOLERANCE
        ),
        "quadratic_objects_are_nontrivial": (
            analytic_norm >= NONTRIVIAL_NORM_FLOOR
            and chart_norm >= NONTRIVIAL_NORM_FLOOR
            and reduced_norm >= NONTRIVIAL_NORM_FLOOR
        ),
    }
    audit = {
        "coefficient_convention": (
            "off-diagonal polynomial coefficient equals Hessian entry; "
            "diagonal polynomial coefficient equals one half Hessian entry"
        ),
        "pair_count": len(pair_records),
        "sector_records": sector_records,
        "pair_records": pair_records,
        "analytic_hessian_shape": list(analytic_hessian.shape),
        "chart_hessian_shape": list(chart_hessian.shape),
        "reduced_hessian_shape": list(reduced_hessian.shape),
        "analytic_hessian_sha256": q011c._array_sha256(analytic_hessian),
        "forcing_polynomial_sha256": q011c._array_sha256(forcing_polynomial),
        "chart_polynomial_sha256": q011c._array_sha256(chart_polynomial),
        "reduced_polynomial_sha256": q011c._array_sha256(reduced_polynomial),
        "chart_hessian_sha256": q011c._array_sha256(chart_hessian),
        "reduced_hessian_sha256": q011c._array_sha256(reduced_hessian),
        "analytic_hessian_frobenius_norm": analytic_norm,
        "chart_hessian_frobenius_norm": chart_norm,
        "reduced_hessian_frobenius_norm": reduced_norm,
        "maximum_sector_sylvester_relative_residual": (maximum_sector_residual),
        "full_homological_relative_residual": full_homological,
        "maximum_pairwise_homological_relative_residual": (maximum_pairwise),
        "graph_gauge_relative_residual": graph_gauge,
        "tangent_global_conservation_relative_residual": (tangent_conservation),
        "hessian_global_conservation_relative_residual": chart_conservation,
        "zero_kx_hessian_global_conservation_relative_residual": (zero_conservation),
        "chart_hessian_symmetry_relative_residual": chart_symmetry,
        "reduced_hessian_symmetry_relative_residual": reduced_symmetry,
        "analytic_forcing_kx_leakage_relative_norm": forcing_leakage,
        "chart_hessian_kx_leakage_relative_norm": chart_leakage,
        "structural_checks": structural_checks,
        "structural_passed": all(structural_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }
    return analytic_hessian, chart_hessian, reduced_hessian, audit


def _realify_quadratic_model(
    linear: ComplexLinearData,
    real_tangent: Array,
    real_extractor: Array,
    real_reduced_linear: Array,
    coordinate_map: ComplexArray,
    analytic_hessian: ComplexArray,
    chart_hessian: ComplexArray,
    reduced_hessian: ComplexArray,
) -> tuple[RealForcedQuadraticModel, dict[str, Any]]:
    analytic_real_complex = np.einsum(
        "nij,ia,jb->nab",
        analytic_hessian,
        coordinate_map,
        coordinate_map,
        optimize=True,
    )
    chart_real_complex = np.einsum(
        "nij,ia,jb->nab",
        chart_hessian,
        coordinate_map,
        coordinate_map,
        optimize=True,
    )
    reduced_input_transform = np.einsum(
        "rij,ia,jb->rab",
        reduced_hessian,
        coordinate_map,
        coordinate_map,
        optimize=True,
    )
    reduced_real_complex = np.einsum(
        "ar,rij->aij",
        coordinate_map.conj().T,
        reduced_input_transform,
        optimize=True,
    )
    analytic_real = np.asarray(analytic_real_complex.real, dtype=np.float64)
    chart_real = np.asarray(chart_real_complex.real, dtype=np.float64)
    reduced_real = np.asarray(reduced_real_complex.real, dtype=np.float64)

    analytic_imaginary = _relative_norm(
        analytic_real_complex.imag,
        analytic_real_complex.real,
    )
    chart_imaginary = _relative_norm(
        chart_real_complex.imag,
        chart_real_complex.real,
    )
    reduced_imaginary = _relative_norm(
        reduced_real_complex.imag,
        reduced_real_complex.real,
    )
    independent_analytic = _analytic_second_derivative(
        linear.base,
        real_tangent,
    )
    analytic_transform_residual = _relative_norm(
        analytic_real - independent_analytic,
        independent_analytic,
    )
    graph_gauge = _relative_norm(
        real_extractor @ chart_real.reshape(STATE_DIMENSION, -1),
        chart_real,
    )
    conservation = np.tile(
        conserved_moment_matrix(),
        (1, SIZE * SIZE),
    )
    tangent_conservation = _relative_norm(
        conservation @ real_tangent,
        real_tangent,
    )
    hessian_conservation = _relative_norm(
        conservation @ chart_real.reshape(STATE_DIMENSION, -1),
        chart_real,
    )
    chart_symmetry = _relative_norm(
        chart_real - chart_real.swapaxes(1, 2),
        chart_real,
    )
    reduced_symmetry = _relative_norm(
        reduced_real - reduced_real.swapaxes(1, 2),
        reduced_real,
    )
    structural_checks = {
        "real_quadratic_shapes_are_registered": (
            analytic_real.shape == (STATE_DIMENSION, SELECTED_DIMENSION, SELECTED_DIMENSION)
            and chart_real.shape == (STATE_DIMENSION, SELECTED_DIMENSION, SELECTED_DIMENSION)
            and reduced_real.shape == (SELECTED_DIMENSION, SELECTED_DIMENSION, SELECTED_DIMENSION)
        ),
        "all_real_quadratic_values_are_finite": bool(
            np.all(np.isfinite(analytic_real))
            and np.all(np.isfinite(chart_real))
            and np.all(np.isfinite(reduced_real))
        ),
    }
    hypothesis_checks = {
        "analytic_hessian_realification_is_independent": (
            analytic_transform_residual <= STRUCTURAL_TOLERANCE
        ),
        "all_quadratic_imaginary_leakages_are_small": (
            max(analytic_imaginary, chart_imaginary, reduced_imaginary) <= STRUCTURAL_TOLERANCE
        ),
        "real_graph_gauge_is_within_tolerance": (graph_gauge <= GRAPH_GAUGE_TOLERANCE),
        "real_tangent_and_hessian_preserve_fixed_leaf": (
            tangent_conservation <= CONSERVATION_TOLERANCE
            and hessian_conservation <= CONSERVATION_TOLERANCE
        ),
        "real_hessian_symmetries_are_within_tolerance": (
            chart_symmetry <= SYMMETRY_TOLERANCE and reduced_symmetry <= SYMMETRY_TOLERANCE
        ),
    }
    audit = {
        "analytic_second_derivative_sha256": q011c._array_sha256(analytic_real),
        "real_chart_hessian_sha256": q011c._array_sha256(chart_real),
        "real_reduced_hessian_sha256": q011c._array_sha256(reduced_real),
        "analytic_hessian_imaginary_leakage_relative_norm": (analytic_imaginary),
        "chart_hessian_imaginary_leakage_relative_norm": chart_imaginary,
        "reduced_hessian_imaginary_leakage_relative_norm": (reduced_imaginary),
        "analytic_transform_relative_residual": analytic_transform_residual,
        "real_graph_gauge_relative_residual": graph_gauge,
        "real_tangent_global_conservation_relative_residual": (tangent_conservation),
        "real_hessian_global_conservation_relative_residual": (hessian_conservation),
        "real_chart_hessian_symmetry_relative_residual": chart_symmetry,
        "real_reduced_hessian_symmetry_relative_residual": reduced_symmetry,
        "structural_checks": structural_checks,
        "structural_passed": all(structural_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }
    model = RealForcedQuadraticModel(
        base=linear.base,
        tangent=real_tangent,
        extractor=real_extractor,
        reduced_linear=real_reduced_linear,
        hessian=chart_real,
        reduced_hessian=reduced_real,
        second_derivative=analytic_real,
    )
    return model, audit


def _independent_hessian_audit(
    model: RealForcedQuadraticModel,
) -> dict[str, Any]:
    generator = np.random.default_rng(HESSIAN_SEED)
    left_directions = generator.standard_normal((HESSIAN_DIRECTION_PAIR_COUNT, SELECTED_DIMENSION))
    right_directions = generator.standard_normal((HESSIAN_DIRECTION_PAIR_COUNT, SELECTED_DIMENSION))
    left_directions /= np.linalg.norm(left_directions, axis=1)[:, None]
    right_directions /= np.linalg.norm(right_directions, axis=1)[:, None]
    records: list[dict[str, Any]] = []

    for direction_index, (left, right) in enumerate(
        zip(left_directions, right_directions, strict=True)
    ):
        analytic = np.einsum(
            "nij,i,j->n",
            model.second_derivative,
            left,
            right,
            optimize=True,
        )

        def centered(
            step: float,
            left_direction: Array = left,
            right_direction: Array = right,
        ) -> tuple[Array, float]:
            left_state = step * (model.tangent @ left_direction)
            right_state = step * (model.tangent @ right_direction)
            input_states = (
                model.base + left_state + right_state,
                model.base + left_state - right_state,
                model.base - left_state + right_state,
                model.base - left_state - right_state,
            )
            mapped_states = tuple(model.full_map(state) for state in input_states)
            difference = (
                mapped_states[0] - mapped_states[1] - mapped_states[2] + mapped_states[3]
            ) / (4.0 * step * step)
            minimum_population = min(
                *(float(np.min(state)) for state in input_states),
                *(float(np.min(state)) for state in mapped_states),
            )
            return np.asarray(difference), minimum_population

        coarse, coarse_minimum = centered(HESSIAN_COARSE_STEP)
        fine, fine_minimum = centered(HESSIAN_FINE_STEP)
        richardson = (4.0 * fine - coarse) / 3.0
        discrepancy = _relative_norm(richardson - analytic, analytic)
        step_change = _relative_norm(fine - coarse, richardson)
        records.append(
            {
                "direction_index": direction_index,
                "left_direction": left.tolist(),
                "right_direction": right.tolist(),
                "analytic_norm": float(np.linalg.norm(analytic)),
                "analytic_relative_discrepancy": discrepancy,
                "coarse_to_fine_relative_change": step_change,
                "minimum_input_or_mapped_population": min(
                    coarse_minimum,
                    fine_minimum,
                ),
            }
        )

    maximum_discrepancy = max(record["analytic_relative_discrepancy"] for record in records)
    maximum_step_change = max(record["coarse_to_fine_relative_change"] for record in records)
    minimum_norm = min(record["analytic_norm"] for record in records)
    minimum_population = min(record["minimum_input_or_mapped_population"] for record in records)
    checks = {
        "sixteen_direction_pairs_are_enumerated": (len(records) == HESSIAN_DIRECTION_PAIR_COUNT),
        "all_direction_records_are_finite": bool(_all_numeric_values_finite(records)),
    }
    hypothesis_checks = {
        "analytic_relative_discrepancy_is_within_tolerance": (
            maximum_discrepancy <= HESSIAN_DISCREPANCY_TOLERANCE
        ),
        "coarse_to_fine_change_is_within_tolerance": (
            maximum_step_change <= HESSIAN_STEP_CHANGE_TOLERANCE
        ),
        "directional_hessian_norms_are_nontrivial": (
            minimum_norm >= HESSIAN_DIRECTIONAL_NORM_FLOOR
        ),
        "perturbed_and_mapped_states_are_strictly_positive": (minimum_population > 0.0),
    }
    return {
        "seed": HESSIAN_SEED,
        "direction_pair_count": len(records),
        "coarse_step": HESSIAN_COARSE_STEP,
        "fine_step": HESSIAN_FINE_STEP,
        "method": "centered mixed map difference with Richardson extrapolation",
        "direction_records": records,
        "maximum_analytic_relative_discrepancy": maximum_discrepancy,
        "maximum_coarse_to_fine_relative_change": maximum_step_change,
        "minimum_analytic_directional_hessian_norm": minimum_norm,
        "minimum_input_or_mapped_population": minimum_population,
        "checks": checks,
        "structural_passed": all(checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _residual_order_audit(
    model: RealForcedQuadraticModel,
) -> dict[str, Any]:
    generator = np.random.default_rng(RESIDUAL_SEED)
    directions = generator.standard_normal((RESIDUAL_DIRECTION_COUNT, SELECTED_DIMENSION))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    amplitudes = np.asarray(RESIDUAL_AMPLITUDES, dtype=np.float64)
    base_conserved = global_conserved_quantities(model.base.reshape(SIZE, SIZE, 9))
    records: list[dict[str, Any]] = []

    for direction_index, direction in enumerate(directions):
        linear_residuals: list[float] = []
        quadratic_residuals: list[float] = []
        minimum_population = np.inf
        maximum_conservation_drift = 0.0
        for amplitude in amplitudes:
            coordinates = amplitude * direction
            linear_state = model.chart(coordinates, quadratic=False)
            quadratic_state = model.chart(coordinates, quadratic=True)
            linear_mapped = model.full_map(linear_state)
            quadratic_mapped = model.full_map(quadratic_state)
            linear_residuals.append(
                float(
                    np.linalg.norm(
                        linear_mapped
                        - model.chart(
                            model.reduced_map(
                                coordinates,
                                quadratic=False,
                            ),
                            quadratic=False,
                        )
                    )
                )
            )
            quadratic_residuals.append(
                float(
                    np.linalg.norm(
                        quadratic_mapped
                        - model.chart(
                            model.reduced_map(
                                coordinates,
                                quadratic=True,
                            ),
                            quadratic=True,
                        )
                    )
                )
            )
            for state in (
                linear_state,
                quadratic_state,
                linear_mapped,
                quadratic_mapped,
            ):
                minimum_population = min(
                    minimum_population,
                    float(np.min(state)),
                )
                maximum_conservation_drift = max(
                    maximum_conservation_drift,
                    float(
                        np.linalg.norm(
                            global_conserved_quantities(state.reshape(SIZE, SIZE, 9))
                            - base_conserved
                        )
                    ),
                )

        linear_mask = np.asarray(linear_residuals) >= RESIDUAL_NOISE_FLOOR
        quadratic_mask = np.asarray(quadratic_residuals) >= RESIDUAL_NOISE_FLOOR
        eligible = bool(
            np.count_nonzero(linear_mask) >= 4 and np.count_nonzero(quadratic_mask) >= 4
        )
        linear_slope = (
            log_log_slope(
                amplitudes[linear_mask],
                np.asarray(linear_residuals)[linear_mask],
            )
            if eligible
            else 0.0
        )
        quadratic_slope = (
            log_log_slope(
                amplitudes[quadratic_mask],
                np.asarray(quadratic_residuals)[quadratic_mask],
            )
            if eligible
            else 0.0
        )
        largest_ratio = quadratic_residuals[-1] / max(linear_residuals[-1], np.finfo(float).tiny)
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "linear_residuals": linear_residuals,
                "quadratic_residuals": quadratic_residuals,
                "linear_fit_point_count": int(np.count_nonzero(linear_mask)),
                "quadratic_fit_point_count": int(np.count_nonzero(quadratic_mask)),
                "slope_eligible": eligible,
                "linear_slope": float(linear_slope),
                "quadratic_slope": float(quadratic_slope),
                "largest_amplitude_residual_ratio": float(largest_ratio),
                "minimum_population": float(minimum_population),
                "maximum_global_conservation_drift": (maximum_conservation_drift),
            }
        )

    eligible_records = [record for record in records if record["slope_eligible"]]
    eligible_count = len(eligible_records)
    minimum_linear_slope = (
        min(record["linear_slope"] for record in eligible_records) if eligible_records else 0.0
    )
    maximum_linear_slope = (
        max(record["linear_slope"] for record in eligible_records) if eligible_records else 0.0
    )
    minimum_quadratic_slope = (
        min(record["quadratic_slope"] for record in eligible_records) if eligible_records else 0.0
    )
    maximum_quadratic_slope = (
        max(record["quadratic_slope"] for record in eligible_records) if eligible_records else 0.0
    )
    maximum_ratio = max(record["largest_amplitude_residual_ratio"] for record in records)
    minimum_population = min(record["minimum_population"] for record in records)
    maximum_conservation = max(record["maximum_global_conservation_drift"] for record in records)
    checks = {
        "thirty_two_directions_and_five_amplitudes_are_complete": (
            len(records) == RESIDUAL_DIRECTION_COUNT
            and all(
                len(record["linear_residuals"]) == len(RESIDUAL_AMPLITUDES)
                and len(record["quadratic_residuals"]) == len(RESIDUAL_AMPLITUDES)
                for record in records
            )
        ),
        "all_residual_values_are_finite": bool(_all_numeric_values_finite(records)),
        "degenerate_directions_are_not_slope_gated": all(
            (record["linear_fit_point_count"] < 4 or record["quadratic_fit_point_count"] < 4)
            == (not record["slope_eligible"])
            for record in records
        ),
    }
    hypothesis_checks = {
        "at_least_twenty_eight_directions_are_slope_eligible": (
            eligible_count >= MINIMUM_ELIGIBLE_DIRECTION_COUNT
        ),
        "eligible_linear_slopes_are_second_order": (
            LINEAR_SLOPE_INTERVAL[0]
            <= minimum_linear_slope
            <= maximum_linear_slope
            <= LINEAR_SLOPE_INTERVAL[1]
        ),
        "eligible_quadratic_slopes_are_third_order": (
            QUADRATIC_SLOPE_INTERVAL[0]
            <= minimum_quadratic_slope
            <= maximum_quadratic_slope
            <= QUADRATIC_SLOPE_INTERVAL[1]
        ),
        "largest_amplitude_residual_improves": (
            maximum_ratio <= MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO
        ),
        "all_chart_and_mapped_states_are_positive": minimum_population > 0.0,
        "global_conservation_drift_is_within_tolerance": (
            maximum_conservation <= CONSERVATION_TOLERANCE
        ),
    }
    return {
        "seed": RESIDUAL_SEED,
        "direction_count": len(records),
        "amplitudes": list(RESIDUAL_AMPLITUDES),
        "noise_floor": RESIDUAL_NOISE_FLOOR,
        "direction_records": records,
        "slope_eligible_direction_count": eligible_count,
        "degenerate_direction_count": len(records) - eligible_count,
        "minimum_eligible_linear_slope": minimum_linear_slope,
        "maximum_eligible_linear_slope": maximum_linear_slope,
        "minimum_eligible_quadratic_slope": minimum_quadratic_slope,
        "maximum_eligible_quadratic_slope": maximum_quadratic_slope,
        "maximum_largest_amplitude_residual_ratio": maximum_ratio,
        "minimum_chart_or_mapped_population": minimum_population,
        "maximum_global_conservation_drift": maximum_conservation,
        "checks": checks,
        "structural_passed": all(checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011c.OMEGA,
        "eta": q011c.ETA,
        "state_dimension": STATE_DIMENSION,
        "selected_dimension": SELECTED_DIMENSION,
        "pair_count": PAIR_COUNT,
        "fixed_conservation_leaf": {
            "delta_mass": 0.0,
            "delta_momentum_x": 0.0,
            "delta_momentum_y": 0.0,
            "zero_wave_center_coordinates_included": False,
        },
        "selected_block_order": list(SELECTED_BLOCK_ORDER),
        "output_sector_order": list(OUTPUT_SECTOR_ORDER),
        "sector_pair_counts": {
            str(key): value for key, value in q011d.EXPECTED_SECTOR_PAIR_COUNTS.items()
        },
        "coefficient_convention": {
            "chart": "W(a)=x_star+W1*a+one_half*W2[a,a]",
            "reduced": "R(a)=R1*a+one_half*R2[a,a]",
            "diagonal_polynomial_factor": 0.5,
            "off_diagonal_polynomial_factor": 1.0,
        },
        "hessian_campaign": {
            "seed": HESSIAN_SEED,
            "direction_pair_count": HESSIAN_DIRECTION_PAIR_COUNT,
            "coarse_step": HESSIAN_COARSE_STEP,
            "fine_step": HESSIAN_FINE_STEP,
        },
        "residual_campaign": {
            "seed": RESIDUAL_SEED,
            "direction_count": RESIDUAL_DIRECTION_COUNT,
            "amplitudes": list(RESIDUAL_AMPLITUDES),
            "noise_floor": RESIDUAL_NOISE_FLOOR,
            "minimum_eligible_direction_count": (MINIMUM_ELIGIBLE_DIRECTION_COUNT),
        },
        "thresholds": {
            "structural": STRUCTURAL_TOLERANCE,
            "sector_sylvester_residual": SYLVESTER_RESIDUAL_TOLERANCE,
            "full_homological_relative": HOMOLOGICAL_RELATIVE_TOLERANCE,
            "pairwise_homological_relative": PAIRWISE_HOMOLOGICAL_TOLERANCE,
            "graph_gauge_relative": GRAPH_GAUGE_TOLERANCE,
            "conservation_relative": CONSERVATION_TOLERANCE,
            "symmetry_relative": SYMMETRY_TOLERANCE,
            "fourier_leakage_relative": FOURIER_LEAKAGE_TOLERANCE,
            "nontrivial_norm": NONTRIVIAL_NORM_FLOOR,
            "hessian_discrepancy": HESSIAN_DISCREPANCY_TOLERANCE,
            "hessian_step_change": HESSIAN_STEP_CHANGE_TOLERANCE,
            "hessian_directional_norm": HESSIAN_DIRECTIONAL_NORM_FLOOR,
            "linear_slope_interval": list(LINEAR_SLOPE_INTERVAL),
            "quadratic_slope_interval": list(QUADRATIC_SLOPE_INTERVAL),
            "maximum_largest_amplitude_residual_ratio": (MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO),
        },
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "derivative_digest_sha256": cycle["derivative_digest_sha256"],
        "chart_digest_sha256": cycle["chart_digest_sha256"],
        "residual_digest_sha256": cycle["residual_digest_sha256"],
        "validity_gate_passes": {
            name: gate["passed"] for name, gate in cycle["validity_gates"].items()
        },
        "hypothesis_gate_passes": {
            name: gate["passed"] for name, gate in cycle["hypothesis_gates"].items()
        },
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def run_forced_quadratic_chart_audit() -> dict[str, Any]:
    """Run the preregistered Q011e dense forced quadratic chart audit."""

    registered_parameters = _registered_parameters()
    (
        sealed_input,
        stripe_state,
        fixed_leaf_basis,
        q011d_artifact,
    ) = _sealed_input_audit()
    linear = _complex_linear_data(
        stripe_state,
        fixed_leaf_basis,
        q011d_artifact,
    )
    (
        real_tangent,
        real_extractor,
        real_reduced_linear,
        coordinate_map,
        real_linear_audit,
    ) = _real_linear_coordinates(linear)
    (
        analytic_hessian,
        chart_hessian,
        reduced_hessian,
        quadratic_construction,
    ) = _quadratic_construction(linear)
    model, real_quadratic_audit = _realify_quadratic_model(
        linear,
        real_tangent,
        real_extractor,
        real_reduced_linear,
        coordinate_map,
        analytic_hessian,
        chart_hessian,
        reduced_hessian,
    )
    independent_hessian = _independent_hessian_audit(model)
    residual_order = _residual_order_audit(model)

    input_sections = _json_native(
        {
            "registered_parameters": registered_parameters,
            "sealed_input_audit": sealed_input,
        }
    )
    derivative_sections = _json_native(
        {
            "complex_linear_coordinate_audit": linear.audit,
            "real_linear_coordinate_audit": real_linear_audit,
            "independent_hessian_audit": independent_hessian,
        }
    )
    chart_sections = _json_native(
        {
            "quadratic_construction_audit": quadratic_construction,
            "real_quadratic_audit": real_quadratic_audit,
        }
    )
    residual_sections = _json_native(
        {
            "residual_order_audit": residual_order,
        }
    )
    input_digest = q011c._canonical_json_sha256(input_sections)
    derivative_digest = q011c._canonical_json_sha256(derivative_sections)
    chart_digest = q011c._canonical_json_sha256(chart_sections)
    residual_digest = q011c._canonical_json_sha256(residual_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **derivative_sections,
        **chart_sections,
        **residual_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011c._canonical_json_sha256(input_sections)
        and derivative_digest == q011c._canonical_json_sha256(derivative_sections)
        and chart_digest == q011c._canonical_json_sha256(chart_sections)
        and residual_digest == q011c._canonical_json_sha256(residual_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )

    validity_gates = {
        "sealed_q011d_and_prior_inputs_replay": {
            "passed": sealed_input["passed"],
            "threshold": (
                "Q011d artifact, runner, five digests and accepted cycle "
                "replay; Q011c outcomes, Q011b endpoint and package reproduce"
            ),
            "value": sealed_input["checks"],
        },
        "complex_and_real_linear_coordinates_are_structural": {
            "passed": bool(
                linear.audit["passed"]
                and real_linear_audit["passed"]
                and real_quadratic_audit["structural_passed"]
            ),
            "threshold": (
                "invariant Schur complement, unitary Fourier embedding, "
                "complex/real tangent dimensions and finite values reproduce"
            ),
            "value": {
                "complex_checks": linear.audit["checks"],
                "real_linear_checks": real_linear_audit["checks"],
                "real_quadratic_structural_checks": real_quadratic_audit["structural_checks"],
            },
        },
        "analytic_and_independent_hessian_campaign_is_complete": {
            "passed": independent_hessian["structural_passed"],
            "threshold": (
                "analytic forced Hessian and 16 two-step mixed-map "
                "finite-difference direction pairs are finite and complete"
            ),
            "value": independent_hessian["checks"],
        },
        "all_three_hundred_quadratic_pairs_are_complete": {
            "passed": quadratic_construction["structural_passed"],
            "threshold": (
                "300 pair forcing coefficients, five sector solves and "
                "W2/R2 arrays have registered dimensions and finite values"
            ),
            "value": quadratic_construction["structural_checks"],
        },
        "homological_graph_conservation_and_support_diagnostics_exist": {
            "passed": bool(
                all(
                    key in quadratic_construction
                    for key in (
                        "full_homological_relative_residual",
                        "maximum_pairwise_homological_relative_residual",
                        "graph_gauge_relative_residual",
                        "hessian_global_conservation_relative_residual",
                        "zero_kx_hessian_global_conservation_relative_residual",
                        "chart_hessian_kx_leakage_relative_norm",
                    )
                )
                and _all_numeric_values_finite(quadratic_construction)
            ),
            "threshold": (
                "homological, graph-gauge, conservation, symmetry and "
                "kx-support diagnostics are completely recorded"
            ),
            "value": {
                "diagnostic_keys_present": True,
                "all_values_finite": bool(_all_numeric_values_finite(quadratic_construction)),
            },
        },
        "thirty_two_direction_residual_campaign_is_complete": {
            "passed": residual_order["structural_passed"],
            "threshold": (
                "32 directions times five amplitudes record finite linear/"
                "quadratic residuals and exclude degenerate slopes"
            ),
            "value": residual_order["checks"],
        },
        "finite_strict_json_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "all values finite strict JSON; input, derivative, chart "
                "and residual digests plus runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_provenance_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    construction_checks = quadratic_construction["hypothesis_checks"]
    real_checks = real_quadratic_audit["hypothesis_checks"]
    residual_checks = residual_order["hypothesis_checks"]
    raw_hypotheses = {
        "independent_hessian_and_positivity_pass": independent_hessian["hypothesis_passed"],
        "sector_solves_and_homological_residuals_pass": bool(
            construction_checks["all_five_sector_sylvester_solves_pass"]
            and construction_checks["full_homological_residual_is_within_tolerance"]
            and construction_checks["pairwise_homological_residuals_are_within_tolerance"]
        ),
        "graph_leaf_symmetry_and_fourier_support_pass": bool(
            construction_checks["graph_gauge_is_within_tolerance"]
            and construction_checks["tangent_and_chart_preserve_fixed_leaf"]
            and construction_checks["hessian_symmetries_are_within_tolerance"]
            and construction_checks["kx_selection_rules_are_within_tolerance"]
            and construction_checks["quadratic_objects_are_nontrivial"]
        ),
        "complex_to_real_chart_and_linear_invariance_pass": bool(
            real_linear_audit["passed"] and real_quadratic_audit["hypothesis_passed"]
        ),
        "linear_and_quadratic_residual_orders_pass": bool(
            residual_checks["at_least_twenty_eight_directions_are_slope_eligible"]
            and residual_checks["eligible_linear_slopes_are_second_order"]
            and residual_checks["eligible_quadratic_slopes_are_third_order"]
        ),
        "residual_improvement_positivity_and_conservation_pass": bool(
            residual_checks["largest_amplitude_residual_improves"]
            and residual_checks["all_chart_and_mapped_states_are_positive"]
            and residual_checks["global_conservation_drift_is_within_tolerance"]
        ),
    }
    hypothesis_gates = {
        "independent_hessian_and_positivity_pass": {
            "passed": bool(
                validity_passed and raw_hypotheses["independent_hessian_and_positivity_pass"]
            ),
            "threshold": (
                "Richardson discrepancy <=1e-6, step change <=1e-4, "
                "directional norm >=1e-8 and all states positive"
            ),
            "value": {
                "checks": independent_hessian["hypothesis_checks"],
                "maximum_analytic_relative_discrepancy": independent_hessian[
                    "maximum_analytic_relative_discrepancy"
                ],
                "maximum_coarse_to_fine_relative_change": independent_hessian[
                    "maximum_coarse_to_fine_relative_change"
                ],
                "minimum_analytic_directional_hessian_norm": (
                    independent_hessian["minimum_analytic_directional_hessian_norm"]
                ),
                "minimum_population": independent_hessian["minimum_input_or_mapped_population"],
            },
        },
        "sector_solves_and_homological_residuals_pass": {
            "passed": bool(
                validity_passed and raw_hypotheses["sector_solves_and_homological_residuals_pass"]
            ),
            "threshold": (
                "five sector residuals <=1e-10, full homological <=1e-10 "
                "and all pairwise homological residuals <=1e-9"
            ),
            "value": {
                "maximum_sector_sylvester_relative_residual": (
                    quadratic_construction["maximum_sector_sylvester_relative_residual"]
                ),
                "full_homological_relative_residual": (
                    quadratic_construction["full_homological_relative_residual"]
                ),
                "maximum_pairwise_homological_relative_residual": (
                    quadratic_construction["maximum_pairwise_homological_relative_residual"]
                ),
            },
        },
        "graph_leaf_symmetry_and_fourier_support_pass": {
            "passed": bool(
                validity_passed and raw_hypotheses["graph_leaf_symmetry_and_fourier_support_pass"]
            ),
            "threshold": (
                "graph gauge and conservation <=1e-10, symmetry <=1e-12, "
                "kx leakage <=1e-12 and all quadratic objects nontrivial"
            ),
            "value": {
                "checks": {
                    name: construction_checks[name]
                    for name in (
                        "graph_gauge_is_within_tolerance",
                        "tangent_and_chart_preserve_fixed_leaf",
                        "hessian_symmetries_are_within_tolerance",
                        "kx_selection_rules_are_within_tolerance",
                        "quadratic_objects_are_nontrivial",
                    )
                },
                "graph_gauge_relative_residual": quadratic_construction[
                    "graph_gauge_relative_residual"
                ],
                "zero_kx_conservation_relative_residual": (
                    quadratic_construction["zero_kx_hessian_global_conservation_relative_residual"]
                ),
                "maximum_kx_leakage_relative_norm": max(
                    quadratic_construction["analytic_forcing_kx_leakage_relative_norm"],
                    quadratic_construction["chart_hessian_kx_leakage_relative_norm"],
                ),
            },
        },
        "complex_to_real_chart_and_linear_invariance_pass": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["complex_to_real_chart_and_linear_invariance_pass"]
            ),
            "threshold": (
                "complex/real tangent, linear dynamics, extractor and "
                "quadratic realification residuals <=1e-10"
            ),
            "value": {
                "real_linear_checks": real_linear_audit["checks"],
                "real_quadratic_checks": real_checks,
            },
        },
        "linear_and_quadratic_residual_orders_pass": {
            "passed": bool(
                validity_passed and raw_hypotheses["linear_and_quadratic_residual_orders_pass"]
            ),
            "threshold": (
                "at least 28 eligible directions; linear slopes in "
                "[1.85,2.15] and quadratic slopes in [2.70,3.30]"
            ),
            "value": {
                "eligible_direction_count": residual_order["slope_eligible_direction_count"],
                "minimum_linear_slope": residual_order["minimum_eligible_linear_slope"],
                "maximum_linear_slope": residual_order["maximum_eligible_linear_slope"],
                "minimum_quadratic_slope": residual_order["minimum_eligible_quadratic_slope"],
                "maximum_quadratic_slope": residual_order["maximum_eligible_quadratic_slope"],
            },
        },
        "residual_improvement_positivity_and_conservation_pass": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["residual_improvement_positivity_and_conservation_pass"]
            ),
            "threshold": (
                "largest-amplitude residual ratio <=0.25, all populations "
                "positive and conservation drift <=1e-10"
            ),
            "value": {
                "maximum_residual_ratio": residual_order[
                    "maximum_largest_amplitude_residual_ratio"
                ],
                "minimum_population": residual_order["minimum_chart_or_mapped_population"],
                "maximum_global_conservation_drift": residual_order[
                    "maximum_global_conservation_drift"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    failed_hypotheses = [name for name, gate in hypothesis_gates.items() if not gate["passed"]]
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered dense forced quadratic fixed-leaf chart audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the forced fixed-leaf quadratic chart satisfies the registered "
            "homological and residual-order tests"
        )
    elif (
        failed_hypotheses == ["linear_and_quadratic_residual_orders_pass"]
        and residual_order["slope_eligible_direction_count"] < MINIMUM_ELIGIBLE_DIRECTION_COUNT
    ):
        outcome = "rejected"
        classification = (
            "the forced fixed-leaf quadratic chart is constructed, but the "
            "registered residual-order window is underresolved"
        )
    else:
        outcome = "rejected"
        classification = (
            "the forced fixed-leaf quadratic chart fails the registered construction tests"
        )

    cycle: dict[str, Any] = _json_native(
        {
            "question": (
                "Does the dense forced fixed-leaf quadratic chart satisfy the "
                "registered derivative, homological and residual-order tests?"
            ),
            **pre_gate_sections,
            "input_digest_sha256": input_digest,
            "derivative_digest_sha256": derivative_digest,
            "chart_digest_sha256": chart_digest,
            "residual_digest_sha256": residual_digest,
            "validity_gates": validity_gates,
            "hypothesis_gates": hypothesis_gates,
            "study_validity": "passed" if validity_passed else "failed",
            "hypothesis_outcome": outcome,
            "scientific_classification": classification,
        }
    )
    result_digest = q011c._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["numerical_consequence"] = {
        "q011c_original_inconclusive_outcome_changed": False,
        "q011c1_localization_outcome_changed": False,
        "q011c2_cluster_selection_changed": False,
        "q011d_operator_prequalification_changed": False,
        "fixed_conservation_leaf_is_used": True,
        "zero_wave_center_coordinates_are_included": False,
        "dense_forced_quadratic_chart_is_constructed": bool(
            validity_passed
            and quadratic_construction["hypothesis_passed"]
            and real_quadratic_audit["hypothesis_passed"]
        ),
        "registered_residual_order_is_confirmed": bool(
            validity_passed and raw_hypotheses["linear_and_quadratic_residual_orders_pass"]
        ),
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
        "tt_compression_is_evaluated": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 dense quadratic chart at one "
        "forced fixed point on one 17x17 fixed-conservation leaf, with "
        "finite derivative and residual-order campaigns. It does not "
        "prove a continuous-amplitude family, rigorously enclose the "
        "derivative or inverse, establish SSM existence, uniqueness or "
        "a uniform Taylor remainder, certify nonlinear normal attraction "
        "or a basin, evaluate TT compression, or cover other grids, "
        "forces or wall boundaries."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011c_inconclusive_outcome_changed": False,
        "q011c1_accepted_localization_changed": False,
        "q011c2_accepted_reissue_changed": False,
        "q011d_accepted_prequalification_changed": False,
        "q011b_accepted_fixed_point_changed": False,
        "q011a_nonzero_mean_obstruction_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011f using the observed Q011e chart to choose "
        "amplitude/multi-step holdout before any TT or sparse cost study."
        if outcome == "accepted"
        else (
            "Preregister Q011e1 with a larger independent residual-amplitude "
            "window while preserving the Q011e noise floor and slope thresholds."
            if classification
            == (
                "the forced fixed-leaf quadratic chart is constructed, but the "
                "registered residual-order window is underresolved"
            )
            else (
                "Localize the first failed derivative, graph-gauge, "
                "homological, realification or residual-order gate."
            )
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011e cycle failed strict serialization or digest")
    return cycle


def run_q011e_study() -> dict[str, Any]:
    cycle = run_forced_quadratic_chart_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 dense forced quadratic fixed-leaf chart, "
                "independent Hessian and finite residual-order audit"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011c.OMEGA,
            "eta": q011c.ETA,
            "state_dimension": STATE_DIMENSION,
            "selected_real_dimension": SELECTED_DIMENSION,
            "quadratic_pair_count": PAIR_COUNT,
            "fixed_conservation_leaf": True,
            "zero_wave_center_coordinates_included": False,
            "claim": (
                "finite dense local quadratic-chart verification only; "
                "no forced SSM existence or nonlinear-attraction claim"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011e_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
