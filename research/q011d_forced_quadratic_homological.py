"""Sealed Q011d forced quadratic external homological-family prequalification."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy import linalg

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011c2_heldout_cluster_reissue as q011c2
import research.q011c_forced_spectral_cluster as q011c
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

SIZE = q011c.SIZE
SELECTED_BLOCK_ORDER = (0, 1, 16)
OUTPUT_SECTOR_ORDER = (0, 1, 16, 2, 15)
SELECTED_BLOCK_DIMENSIONS = {0: 6, 1: 9, 16: 9}
EXTERNAL_SECTOR_DIMENSIONS = {0: 144, 1: 144, 16: 144, 2: 153, 15: 153}
EXPECTED_SECTOR_PAIR_COUNTS = {0: 102, 1: 54, 16: 54, 2: 45, 15: 45}
EXPECTED_PAIR_COUNT = 300
EXPECTED_SELECTED_DIMENSION = 24
EXPECTED_EXTERNAL_DIMENSION = 2574
EXPECTED_FULL_FIXED_LEAF_DIMENSION = 2598

Q011C2_ARTIFACT_SHA256 = "c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a"
Q011C2_RUNNER_SHA256 = "87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2"
Q011C2_INPUT_DIGEST = "de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2"
Q011C2_PATH_DIGEST = "36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d"
Q011C2_HOLDOUT_DIGEST = "d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72"
Q011C2_ENDPOINT_DIGEST = "8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8"
Q011C2_RESULT_DIGEST = "8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c"
Q011B_STORED_STATE_SHA256 = "612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613"
Q006I_ARTIFACT_SHA256 = "347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89"
SEALED_PACKAGE_SOURCE_SHA256 = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"

Q006I_PAIR_COUNT = 300
Q006I_MINIMUM_OPERATOR_SINGULAR_VALUE = 0.00015502435597333105
Q006I_MAXIMUM_CONDITION_NUMBER = 14513.930547954875
Q006I_SINGULAR_BLOCK_COUNT = 0

STRUCTURAL_TOLERANCE = 1.0e-10
SECTOR_LEAKAGE_TOLERANCE = 1.0e-12
ACTION_RELATIVE_TOLERANCE = 1.0e-12
PRODUCT_SPECTRUM_TOLERANCE = 1.0e-10
MINIMUM_OPERATOR_SINGULAR_VALUE = 1.0e-5
MINIMUM_SPECTRAL_DISTANCE = 1.0e-5
MAXIMUM_OPERATOR_CONDITION_NUMBER = 1.0e6
MAXIMUM_DIRECT_SOLVE_RESIDUAL = 1.0e-10
CONJUGATE_DIAGNOSTIC_TOLERANCE = 1.0e-8
MAXIMUM_SYLVESTER_PROBE_RESIDUAL = 1.0e-10
MAXIMUM_SYLVESTER_RESPONSE_AMPLIFICATION = 1.0e6
NORMAL_DOMINANCE_GAP_FLOOR = 1.0e-6
FULL_SPECTRAL_RADIUS_CEILING = 0.9999
SPECTRAL_QUOTIENT_LOWER = 1.0
SPECTRAL_QUOTIENT_UPPER = 2.0

DIRECT_SOLVE_SEED = 20260820
ACTION_SEED = 20260821
SYLVESTER_PROBE_SEED = 20260822
ACTION_DIRECTION_COUNT = 8
SYLVESTER_PROBES_PER_SECTOR = 4
RANK_THRESHOLD_FACTOR = 100.0


def _complex_record(value: complex) -> dict[str, float]:
    scalar = complex(value)
    return {"real": float(scalar.real), "imag": float(scalar.imag)}


def _relative_multiset_hausdorff(
    left: npt.ArrayLike,
    right: npt.ArrayLike,
) -> float:
    left_values = np.asarray(left, dtype=np.complex128).ravel()
    right_values = np.asarray(right, dtype=np.complex128).ravel()
    scale = max(
        float(np.max(np.abs(left_values))),
        float(np.max(np.abs(right_values))),
        np.finfo(float).tiny,
    )
    return q011c._hausdorff(left_values, right_values) / scale


def _sealed_input_audit() -> tuple[dict[str, Any], Array, Array]:
    artifact_directory = Path(__file__).resolve().parent / "artifacts"
    q011c2_artifact_path = artifact_directory / "q011c2_heldout_cluster_reissue.json"
    q011b_artifact_path = artifact_directory / "q011b_zero_mean_forced_fixed_point.json"
    q006i_artifact_path = artifact_directory / "q006i_full2d_quadratic.json"
    q011c2_runner_path = Path(q011c2.__file__).resolve()

    q011c2_artifact = json.loads(q011c2_artifact_path.read_text(encoding="utf-8"))
    q011b_artifact = json.loads(q011b_artifact_path.read_text(encoding="utf-8"))
    q006i_artifact = json.loads(q006i_artifact_path.read_text(encoding="utf-8"))
    fresh_q011c2_cycle = q011c2.run_heldout_cluster_reissue_audit()

    stored_state = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    _conservation, basis, basis_audit = q011b._fixed_leaf_basis()
    q006i_diagnostics = q006i_artifact["cycle"]["construction"]["diagnostics"]
    q011c2_digests = (
        fresh_q011c2_cycle["input_digest_sha256"],
        fresh_q011c2_cycle["path_digest_sha256"],
        fresh_q011c2_cycle["holdout_spectrum_digest_sha256"],
        fresh_q011c2_cycle["endpoint_digest_sha256"],
        fresh_q011c2_cycle["result_digest_sha256"],
    )
    sealed_q011c2_replay = fresh_q011c2_cycle["sealed_replay_audit"]
    checks = {
        "q011c2_artifact_sha256_matches": (
            _file_sha256(q011c2_artifact_path) == Q011C2_ARTIFACT_SHA256
        ),
        "q011c2_runner_sha256_matches": (_file_sha256(q011c2_runner_path) == Q011C2_RUNNER_SHA256),
        "q011c2_cycle_replays_exactly": (q011c2_artifact["cycle"] == fresh_q011c2_cycle),
        "q011c2_digests_match": (
            q011c2_digests
            == (
                Q011C2_INPUT_DIGEST,
                Q011C2_PATH_DIGEST,
                Q011C2_HOLDOUT_DIGEST,
                Q011C2_ENDPOINT_DIGEST,
                Q011C2_RESULT_DIGEST,
            )
        ),
        "q011c2_accepted_outcome_reproduces": (
            fresh_q011c2_cycle["study_validity"] == "passed"
            and fresh_q011c2_cycle["hypothesis_outcome"] == "accepted"
            and fresh_q011c2_cycle["scientific_classification"]
            == (
                "the forced first-shell cluster passes a conjugacy-orbit "
                "reissue with eight held-out amplitude nodes"
            )
            and all(gate["passed"] for gate in fresh_q011c2_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in fresh_q011c2_cycle["hypothesis_gates"].values())
        ),
        "q011c1_and_q011c_outcomes_remain_sealed": (
            sealed_q011c2_replay["q011c1_artifact"]["study_validity"] == "passed"
            and sealed_q011c2_replay["q011c1_artifact"]["hypothesis_outcome"] == "accepted"
            and sealed_q011c2_replay["q011c_artifact"]["study_validity"] == "failed"
            and sealed_q011c2_replay["q011c_artifact"]["hypothesis_outcome"] == "inconclusive"
        ),
        "stored_endpoint_sha256_matches": (
            q011c._array_sha256(stored_state) == Q011B_STORED_STATE_SHA256
        ),
        "fixed_leaf_basis_reconstructs": basis_audit["passed"],
        "q006i_artifact_sha256_matches": (
            _file_sha256(q006i_artifact_path) == Q006I_ARTIFACT_SHA256
        ),
        "q006i_calibration_reproduces": (
            q006i_diagnostics["pair_count"] == Q006I_PAIR_COUNT
            and q006i_diagnostics["minimum_operator_singular_value"]
            == Q006I_MINIMUM_OPERATOR_SINGULAR_VALUE
            and q006i_diagnostics["maximum_operator_condition_number"]
            == Q006I_MAXIMUM_CONDITION_NUMBER
            and q006i_diagnostics["numerical_singular_block_count"] == Q006I_SINGULAR_BLOCK_COUNT
        ),
        "package_source_sha256_matches": (
            source_metadata()["package_source_sha256"] == SEALED_PACKAGE_SOURCE_SHA256
        ),
    }
    audit = {
        "q011c2_artifact": {
            "filename": q011c2_artifact_path.name,
            "sha256": _file_sha256(q011c2_artifact_path),
            "runner_filename": q011c2_runner_path.name,
            "runner_sha256": _file_sha256(q011c2_runner_path),
            "input_digest_sha256": fresh_q011c2_cycle["input_digest_sha256"],
            "path_digest_sha256": fresh_q011c2_cycle["path_digest_sha256"],
            "holdout_spectrum_digest_sha256": fresh_q011c2_cycle["holdout_spectrum_digest_sha256"],
            "endpoint_digest_sha256": fresh_q011c2_cycle["endpoint_digest_sha256"],
            "result_digest_sha256": fresh_q011c2_cycle["result_digest_sha256"],
            "study_validity": fresh_q011c2_cycle["study_validity"],
            "hypothesis_outcome": fresh_q011c2_cycle["hypothesis_outcome"],
            "scientific_classification": fresh_q011c2_cycle["scientific_classification"],
        },
        "preserved_prior_outcomes": {
            "q011c1_study_validity": sealed_q011c2_replay["q011c1_artifact"]["study_validity"],
            "q011c1_hypothesis_outcome": sealed_q011c2_replay["q011c1_artifact"][
                "hypothesis_outcome"
            ],
            "q011c_study_validity": sealed_q011c2_replay["q011c_artifact"]["study_validity"],
            "q011c_hypothesis_outcome": sealed_q011c2_replay["q011c_artifact"][
                "hypothesis_outcome"
            ],
        },
        "q011b_endpoint": {
            "artifact_filename": q011b_artifact_path.name,
            "stored_state_sha256": q011c._array_sha256(stored_state),
            "fixed_leaf_basis_audit": basis_audit,
        },
        "q006i_calibration": {
            "artifact_filename": q006i_artifact_path.name,
            "artifact_sha256": _file_sha256(q006i_artifact_path),
            "study_validity": q006i_artifact["cycle"]["study_validity"],
            "hypothesis_outcome": q006i_artifact["cycle"]["hypothesis_outcome"],
            "pair_count": q006i_diagnostics["pair_count"],
            "minimum_operator_singular_value": q006i_diagnostics["minimum_operator_singular_value"],
            "maximum_operator_condition_number": q006i_diagnostics[
                "maximum_operator_condition_number"
            ],
            "numerical_singular_block_count": q006i_diagnostics["numerical_singular_block_count"],
        },
        "package_source_sha256": source_metadata()["package_source_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, stored_state, basis


def _schur_record(
    matrix: ComplexArray,
    triangular: ComplexArray,
    unitary: ComplexArray,
) -> dict[str, float]:
    scale = max(float(np.linalg.norm(matrix, ord="fro")), np.finfo(float).tiny)
    reconstruction = float(
        np.linalg.norm(matrix - unitary @ triangular @ unitary.conj().T, ord="fro") / scale
    )
    unitarity = float(
        np.linalg.norm(
            unitary.conj().T @ unitary - np.eye(matrix.shape[0]),
            ord="fro",
        )
    )
    return {
        "schur_reconstruction_relative_residual": reconstruction,
        "schur_unitarity_frobenius_residual": unitarity,
        "maximum_structural_residual": max(reconstruction, unitarity),
    }


def _canonical_linear_split(
    state: Array,
    basis: Array,
) -> tuple[dict[str, Any], ComplexArray, dict[int, ComplexArray], ComplexArray]:
    _reference_bases, reference_targets, reference_audit = q011c._reference_audit(basis)
    clusters: dict[int, q011c.OrderedCluster] = {}
    active_matrices: dict[int, ComplexArray] = {}
    external_matrices: dict[int, ComplexArray] = {}
    selected_records: list[dict[str, Any]] = []
    external_sector_records: list[dict[str, Any]] = []

    for block_index in SELECTED_BLOCK_ORDER:
        active = q011c._active_matrix(state, block_index, basis)
        active_matrices[block_index] = active
        cluster = q011c._ordered_cluster(active, reference_targets[block_index])
        clusters[block_index] = cluster
        external_matrices[block_index] = cluster.excluded_dynamics
        structural_values = [
            cluster.schur_reconstruction_relative_residual,
            cluster.schur_unitarity_frobenius_residual,
            cluster.invariance_relative_residual,
            cluster.projector_idempotency_frobenius_residual,
            cluster.projector_commutator_relative_residual,
        ]
        selected_records.append(
            {
                "block_index": block_index,
                "selected_dimension": cluster.selected_dimension,
                "external_dimension": int(cluster.excluded_dynamics.shape[0]),
                "selected_dynamics_sha256": q011c._array_sha256(cluster.selected_dynamics),
                "external_dynamics_sha256": q011c._array_sha256(cluster.excluded_dynamics),
                "projector_sha256": q011c._array_sha256(cluster.projector),
                "selected_eigenvalues": q011c._complex_records(cluster.selected_eigenvalues),
                "external_eigenvalues": q011c._complex_records(cluster.excluded_eigenvalues),
                "external_eigenvalue_absolute_separation": (cluster.external_eigenvalue_separation),
                "projector_two_norm": cluster.projector_norm,
                "schur_reconstruction_relative_residual": (
                    cluster.schur_reconstruction_relative_residual
                ),
                "schur_unitarity_frobenius_residual": (cluster.schur_unitarity_frobenius_residual),
                "selected_invariance_relative_residual": (cluster.invariance_relative_residual),
                "projector_idempotency_frobenius_residual": (
                    cluster.projector_idempotency_frobenius_residual
                ),
                "projector_commutator_relative_residual": (
                    cluster.projector_commutator_relative_residual
                ),
                "maximum_structural_residual": max(structural_values),
            }
        )

    for block_index in (2, 15):
        active = q011c._active_matrix(state, block_index, basis)
        active_matrices[block_index] = active
        triangular, unitary = linalg.schur(
            active,
            output="complex",
            check_finite=True,
        )
        triangular = np.asarray(triangular, dtype=np.complex128)
        unitary = np.asarray(unitary, dtype=np.complex128)
        external_matrices[block_index] = triangular
        record = _schur_record(active, triangular, unitary)
        external_sector_records.append(
            {
                "block_index": block_index,
                "external_dimension": int(triangular.shape[0]),
                "external_dynamics_sha256": q011c._array_sha256(triangular),
                "external_eigenvalues": q011c._complex_records(np.diag(triangular)),
                **record,
            }
        )

    selected_dynamics = np.asarray(
        linalg.block_diag(*(clusters[index].selected_dynamics for index in SELECTED_BLOCK_ORDER)),
        dtype=np.complex128,
    )
    selected_coordinate_eigenvalues = np.concatenate(
        [np.diag(clusters[index].selected_dynamics) for index in SELECTED_BLOCK_ORDER]
    )

    selected_spectra = [clusters[index].selected_eigenvalues for index in SELECTED_BLOCK_ORDER]
    external_spectra: list[ComplexArray] = []
    full_block_records: list[dict[str, Any]] = []
    for block_index in range(SIZE):
        if block_index in clusters:
            selected_values = clusters[block_index].selected_eigenvalues
            external_values = clusters[block_index].excluded_eigenvalues
            full_values = np.concatenate((selected_values, external_values))
        else:
            active = active_matrices.get(block_index)
            if active is None:
                active = q011c._active_matrix(state, block_index, basis)
                active_matrices[block_index] = active
            if block_index in external_matrices:
                external_values = np.diag(external_matrices[block_index])
            else:
                external_values = linalg.eigvals(active, check_finite=True)
            full_values = external_values
        external_spectra.append(np.asarray(external_values, dtype=np.complex128))
        full_block_records.append(
            {
                "block_index": block_index,
                "fixed_leaf_dimension": int(full_values.size),
                "selected_eigenvalue_count": (
                    int(selected_values.size) if block_index in clusters else 0
                ),
                "external_eigenvalue_count": int(external_values.size),
                "fixed_leaf_eigenvalues": q011c._complex_records(full_values),
                "fixed_leaf_spectrum_sha256": q011c._array_sha256(full_values),
                "maximum_eigenvalue_modulus": float(np.max(np.abs(full_values))),
            }
        )

    selected_spectrum = np.concatenate(selected_spectra)
    external_spectrum = np.concatenate(external_spectra)
    full_spectrum = np.concatenate((selected_spectrum, external_spectrum))
    selected_minimum_modulus = float(np.min(np.abs(selected_spectrum)))
    external_maximum_modulus = float(np.max(np.abs(external_spectrum)))
    normal_gap = selected_minimum_modulus - external_maximum_modulus
    full_radius = float(np.max(np.abs(full_spectrum)))
    spectral_quotient = float(np.log(external_maximum_modulus) / np.log(selected_minimum_modulus))

    selected_record_by_index = {record["block_index"]: record for record in selected_records}
    external_record_by_index = {record["block_index"]: record for record in external_sector_records}
    conjugacy_records = [
        {
            "left_sector": 1,
            "right_sector": 16,
            "selected_spectrum_absolute_hausdorff_error": q011c._hausdorff(
                clusters[1].selected_eigenvalues,
                np.conjugate(clusters[16].selected_eigenvalues),
            ),
            "external_spectrum_absolute_hausdorff_error": q011c._hausdorff(
                clusters[1].excluded_eigenvalues,
                np.conjugate(clusters[16].excluded_eigenvalues),
            ),
        },
        {
            "left_sector": 2,
            "right_sector": 15,
            "selected_spectrum_absolute_hausdorff_error": 0.0,
            "external_spectrum_absolute_hausdorff_error": q011c._hausdorff(
                np.diag(external_matrices[2]),
                np.conjugate(np.diag(external_matrices[15])),
            ),
        },
    ]
    maximum_structural = max(
        max(record["maximum_structural_residual"] for record in selected_records),
        max(record["maximum_structural_residual"] for record in external_sector_records),
    )
    maximum_conjugate_error = max(
        max(
            record["selected_spectrum_absolute_hausdorff_error"],
            record["external_spectrum_absolute_hausdorff_error"],
        )
        for record in conjugacy_records
    )
    checks = {
        "reference_cluster_is_registered": reference_audit["passed"],
        "selected_dimensions_are_six_nine_nine": all(
            clusters[index].selected_dimension == SELECTED_BLOCK_DIMENSIONS[index]
            for index in SELECTED_BLOCK_ORDER
        ),
        "selected_dimension_is_twenty_four": (
            selected_dynamics.shape == (EXPECTED_SELECTED_DIMENSION, EXPECTED_SELECTED_DIMENSION)
        ),
        "external_sector_dimensions_are_registered": all(
            external_matrices[index].shape
            == (
                EXTERNAL_SECTOR_DIMENSIONS[index],
                EXTERNAL_SECTOR_DIMENSIONS[index],
            )
            for index in OUTPUT_SECTOR_ORDER
        ),
        "all_schur_and_projector_residuals_are_within_tolerance": (
            maximum_structural <= STRUCTURAL_TOLERANCE
        ),
        "conjugate_sector_spectra_are_within_tolerance": (
            maximum_conjugate_error <= STRUCTURAL_TOLERANCE
        ),
        "fixed_leaf_spectrum_counts_are_registered": (
            selected_spectrum.size == EXPECTED_SELECTED_DIMENSION
            and external_spectrum.size == EXPECTED_EXTERNAL_DIMENSION
            and full_spectrum.size == EXPECTED_FULL_FIXED_LEAF_DIMENSION
        ),
        "all_linear_values_are_finite": bool(
            np.all(np.isfinite(selected_dynamics))
            and np.all(np.isfinite(full_spectrum))
            and _all_numeric_values_finite(selected_records)
            and _all_numeric_values_finite(external_sector_records)
        ),
    }
    hypothesis_checks = {
        "global_normal_dominance_gap_above_floor": (normal_gap >= NORMAL_DOMINANCE_GAP_FLOOR),
        "full_fixed_leaf_spectrum_is_stable": (full_radius <= FULL_SPECTRAL_RADIUS_CEILING),
        "spectral_quotient_is_between_one_and_two": (
            np.isfinite(spectral_quotient)
            and SPECTRAL_QUOTIENT_LOWER < spectral_quotient < SPECTRAL_QUOTIENT_UPPER
        ),
    }
    audit = {
        "selected_block_order": list(SELECTED_BLOCK_ORDER),
        "output_sector_order": list(OUTPUT_SECTOR_ORDER),
        "reference_audit": reference_audit,
        "selected_block_records": selected_records,
        "external_sector_records": external_sector_records,
        "selected_dynamics_shape": list(selected_dynamics.shape),
        "selected_dynamics_sha256": q011c._array_sha256(selected_dynamics),
        "selected_coordinate_eigenvalues": q011c._complex_records(selected_coordinate_eigenvalues),
        "selected_coordinate_eigenvalues_sha256": q011c._array_sha256(
            selected_coordinate_eigenvalues
        ),
        "full_block_records": full_block_records,
        "selected_spectrum_sha256": q011c._array_sha256(selected_spectrum),
        "external_spectrum_sha256": q011c._array_sha256(external_spectrum),
        "selected_eigenvalue_count": int(selected_spectrum.size),
        "external_eigenvalue_count": int(external_spectrum.size),
        "full_fixed_leaf_eigenvalue_count": int(full_spectrum.size),
        "selected_minimum_eigenvalue_modulus": selected_minimum_modulus,
        "external_maximum_eigenvalue_modulus": external_maximum_modulus,
        "global_modulus_normal_dominance_gap": normal_gap,
        "full_fixed_leaf_spectral_radius": full_radius,
        "logarithmic_spectral_quotient_diagnostic": spectral_quotient,
        "conjugate_sector_records": conjugacy_records,
        "maximum_structural_residual": maximum_structural,
        "maximum_conjugate_spectrum_hausdorff_error": maximum_conjugate_error,
        "selected_block_record_hashes": {
            str(index): selected_record_by_index[index]["selected_dynamics_sha256"]
            for index in SELECTED_BLOCK_ORDER
        },
        "full_external_sector_hashes": {
            str(index): external_record_by_index[index]["external_dynamics_sha256"]
            for index in (2, 15)
        },
        "checks": checks,
        "structural_passed": all(checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }
    return audit, selected_dynamics, external_matrices, selected_coordinate_eigenvalues


def _selected_coordinate_sectors() -> tuple[int, ...]:
    return tuple(
        sector for sector in SELECTED_BLOCK_ORDER for _ in range(SELECTED_BLOCK_DIMENSIONS[sector])
    )


def _monomial_vector(
    coordinates: npt.ArrayLike,
    pairs: tuple[tuple[int, int], ...],
) -> ComplexArray:
    values = np.asarray(coordinates, dtype=np.complex128).ravel()
    return np.asarray([values[left] * values[right] for left, right in pairs])


def _assemble_symmetric_product(
    selected_dynamics: ComplexArray,
    pairs: tuple[tuple[int, int], ...],
) -> ComplexArray:
    pair_action = np.empty((len(pairs), len(pairs)), dtype=np.complex128)
    for row, (output_left, output_right) in enumerate(pairs):
        left_row = selected_dynamics[output_left]
        right_row = selected_dynamics[output_right]
        for column, (input_left, input_right) in enumerate(pairs):
            coefficient = left_row[input_left] * right_row[input_right]
            if input_left != input_right:
                coefficient += left_row[input_right] * right_row[input_left]
            pair_action[row, column] = coefficient
    return pair_action


def _quadratic_input_action_audit(
    selected_dynamics: ComplexArray,
    selected_eigenvalues: ComplexArray,
) -> tuple[
    dict[str, Any],
    tuple[tuple[int, int], ...],
    dict[int, list[int]],
    dict[int, ComplexArray],
    ComplexArray,
]:
    coordinate_sectors = _selected_coordinate_sectors()
    pairs = tuple(combinations_with_replacement(range(EXPECTED_SELECTED_DIMENSION), 2))
    pair_sectors = tuple(
        (coordinate_sectors[left] + coordinate_sectors[right]) % SIZE for left, right in pairs
    )
    sector_indices = {
        sector: [
            index for index, output_sector in enumerate(pair_sectors) if output_sector == sector
        ]
        for sector in OUTPUT_SECTOR_ORDER
    }
    pair_products = np.asarray(
        [selected_eigenvalues[left] * selected_eigenvalues[right] for left, right in pairs],
        dtype=np.complex128,
    )
    pair_records = [
        {
            "pair_index": index,
            "coordinate_indices": [left, right],
            "input_sectors": [
                coordinate_sectors[left],
                coordinate_sectors[right],
            ],
            "output_sector": pair_sectors[index],
            "eigenvalue_product": _complex_record(pair_products[index]),
        }
        for index, (left, right) in enumerate(pairs)
    ]
    pair_action = _assemble_symmetric_product(selected_dynamics, pairs)

    same_sector_mask = np.equal.outer(pair_sectors, pair_sectors)
    leakage = np.where(same_sector_mask, 0.0, pair_action)
    leakage_frobenius = float(np.linalg.norm(leakage, ord="fro"))
    leakage_relative = leakage_frobenius / max(
        float(np.linalg.norm(pair_action, ord="fro")),
        np.finfo(float).tiny,
    )
    leakage_maximum = float(np.max(np.abs(leakage)))

    action_generator = np.random.default_rng(ACTION_SEED)
    action_records: list[dict[str, Any]] = []
    for direction_index in range(ACTION_DIRECTION_COUNT):
        direction = action_generator.standard_normal(EXPECTED_SELECTED_DIMENSION) + 1j * (
            action_generator.standard_normal(EXPECTED_SELECTED_DIMENSION)
        )
        direction /= np.linalg.norm(direction)
        expected = _monomial_vector(selected_dynamics @ direction, pairs)
        observed = pair_action @ _monomial_vector(direction, pairs)
        relative_error = float(
            np.linalg.norm(observed - expected)
            / max(float(np.linalg.norm(expected)), np.finfo(float).tiny)
        )
        action_records.append(
            {
                "direction_index": direction_index,
                "direction_sha256": q011c._array_sha256(direction),
                "relative_error": relative_error,
                "passed": relative_error <= ACTION_RELATIVE_TOLERANCE,
            }
        )

    sector_actions: dict[int, ComplexArray] = {}
    sector_records: list[dict[str, Any]] = []
    for sector in OUTPUT_SECTOR_ORDER:
        indices = sector_indices[sector]
        sector_action = np.asarray(
            pair_action[np.ix_(indices, indices)],
            dtype=np.complex128,
        )
        sector_actions[sector] = sector_action
        action_spectrum = linalg.eigvals(sector_action, check_finite=True)
        product_spectrum = pair_products[indices]
        spectrum_error = q011c._hausdorff(action_spectrum, product_spectrum)
        sector_records.append(
            {
                "output_sector": sector,
                "pair_count": len(indices),
                "pair_indices": indices,
                "action_shape": list(sector_action.shape),
                "action_sha256": q011c._array_sha256(sector_action),
                "action_eigenvalues": q011c._complex_records(action_spectrum),
                "product_eigenvalues": q011c._complex_records(product_spectrum),
                "product_spectrum_absolute_hausdorff_error": spectrum_error,
                "passed": spectrum_error <= PRODUCT_SPECTRUM_TOLERANCE,
            }
        )

    checks = {
        "selected_coordinate_sector_counts_are_registered": (
            coordinate_sectors.count(0) == 6
            and coordinate_sectors.count(1) == 9
            and coordinate_sectors.count(16) == 9
        ),
        "pair_count_is_three_hundred": len(pairs) == EXPECTED_PAIR_COUNT,
        "sector_pair_counts_are_registered": all(
            len(sector_indices[sector]) == EXPECTED_SECTOR_PAIR_COUNTS[sector]
            for sector in OUTPUT_SECTOR_ORDER
        ),
        "only_registered_output_sectors_occur": (set(pair_sectors) == set(OUTPUT_SECTOR_ORDER)),
        "sector_leakage_is_within_tolerance": (
            leakage_relative <= SECTOR_LEAKAGE_TOLERANCE
            and leakage_maximum <= SECTOR_LEAKAGE_TOLERANCE
        ),
        "all_eight_action_directions_pass": all(record["passed"] for record in action_records),
        "all_sector_product_spectra_reproduce": all(record["passed"] for record in sector_records),
        "all_pair_action_values_are_finite": bool(
            np.all(np.isfinite(pair_action))
            and np.all(np.isfinite(pair_products))
            and _all_numeric_values_finite(action_records)
            and _all_numeric_values_finite(sector_records)
        ),
    }
    audit = {
        "selected_coordinate_sectors": list(coordinate_sectors),
        "pair_count": len(pairs),
        "pair_records": pair_records,
        "pair_enumeration_sha256": q011c._canonical_json_sha256(pair_records),
        "pair_product_sha256": q011c._array_sha256(pair_products),
        "symmetric_product_shape": list(pair_action.shape),
        "symmetric_product_sha256": q011c._array_sha256(pair_action),
        "sector_pair_counts": {
            str(sector): len(sector_indices[sector]) for sector in OUTPUT_SECTOR_ORDER
        },
        "sector_scalar_dimensions": {
            str(sector): (len(sector_indices[sector]) * EXTERNAL_SECTOR_DIMENSIONS[sector])
            for sector in OUTPUT_SECTOR_ORDER
        },
        "sector_leakage_frobenius_norm": leakage_frobenius,
        "sector_leakage_relative_frobenius_norm": leakage_relative,
        "sector_leakage_maximum_absolute_entry": leakage_maximum,
        "action_seed": ACTION_SEED,
        "action_direction_count": ACTION_DIRECTION_COUNT,
        "action_records": action_records,
        "maximum_action_relative_error": max(record["relative_error"] for record in action_records),
        "sector_records": sector_records,
        "maximum_product_spectrum_absolute_hausdorff_error": max(
            record["product_spectrum_absolute_hausdorff_error"] for record in sector_records
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, pairs, sector_indices, sector_actions, pair_products


def _external_homological_block_audit(
    pairs: tuple[tuple[int, int], ...],
    sector_indices: dict[int, list[int]],
    pair_products: ComplexArray,
    external_matrices: dict[int, ComplexArray],
) -> dict[str, Any]:
    pair_to_sector = {
        pair_index: sector for sector, indices in sector_indices.items() for pair_index in indices
    }
    external_spectra = {
        sector: linalg.eigvals(matrix, check_finite=True)
        for sector, matrix in external_matrices.items()
    }
    generator = np.random.default_rng(DIRECT_SOLVE_SEED)
    records: list[dict[str, Any]] = []
    sector_smallest_singular: dict[int, list[float]] = {
        sector: [] for sector in OUTPUT_SECTOR_ORDER
    }
    sector_conditions: dict[int, list[float]] = {sector: [] for sector in OUTPUT_SECTOR_ORDER}
    sector_products: dict[int, list[complex]] = {sector: [] for sector in OUTPUT_SECTOR_ORDER}

    for pair_index, (left, right) in enumerate(pairs):
        sector = pair_to_sector[pair_index]
        product = complex(pair_products[pair_index])
        external = external_matrices[sector]
        operator = external - product * np.eye(
            external.shape[0],
            dtype=np.complex128,
        )
        singular_values = linalg.svdvals(operator, check_finite=True)
        maximum_singular = float(singular_values[0])
        minimum_singular = float(singular_values[-1])
        rank_threshold = float(
            RANK_THRESHOLD_FACTOR * np.finfo(float).eps * max(operator.shape) * maximum_singular
        )
        numerical_rank = int(np.count_nonzero(singular_values > rank_threshold))
        spectral_distance = float(np.min(np.abs(external_spectra[sector] - product)))
        condition = float(maximum_singular / minimum_singular)
        right_hand_side = generator.standard_normal(external.shape[0]) + 1j * (
            generator.standard_normal(external.shape[0])
        )
        right_hand_side /= np.linalg.norm(right_hand_side)
        solution = linalg.solve(
            operator,
            right_hand_side,
            assume_a="gen",
            check_finite=True,
        )
        solve_residual = float(
            np.linalg.norm(operator @ solution - right_hand_side)
            / max(float(np.linalg.norm(right_hand_side)), np.finfo(float).tiny)
        )
        full_rank = numerical_rank == operator.shape[0]
        record = {
            "pair_index": pair_index,
            "coordinate_indices": [left, right],
            "output_sector": sector,
            "operator_shape": list(operator.shape),
            "eigenvalue_product": _complex_record(product),
            "right_hand_side_sha256": q011c._array_sha256(right_hand_side),
            "singular_values": [float(value) for value in singular_values],
            "singular_values_sha256": q011c._array_sha256(singular_values),
            "rank_threshold": rank_threshold,
            "numerical_rank": numerical_rank,
            "full_rank": full_rank,
            "minimum_singular_value": minimum_singular,
            "maximum_singular_value": maximum_singular,
            "spectral_distance": spectral_distance,
            "condition_number": condition,
            "direct_solve_relative_residual": solve_residual,
            "checks": {
                "full_rank": full_rank,
                "minimum_singular_value_above_floor": (
                    minimum_singular >= MINIMUM_OPERATOR_SINGULAR_VALUE
                ),
                "spectral_distance_above_floor": (spectral_distance >= MINIMUM_SPECTRAL_DISTANCE),
                "condition_number_below_ceiling": (condition <= MAXIMUM_OPERATOR_CONDITION_NUMBER),
                "solve_residual_below_ceiling": (solve_residual <= MAXIMUM_DIRECT_SOLVE_RESIDUAL),
            },
        }
        records.append(record)
        sector_smallest_singular[sector].append(minimum_singular)
        sector_conditions[sector].append(condition)
        sector_products[sector].append(product)

    conjugacy_records: list[dict[str, Any]] = []
    for left_sector, right_sector in ((1, 16), (2, 15)):
        product_error = _relative_multiset_hausdorff(
            sector_products[left_sector],
            np.conjugate(sector_products[right_sector]),
        )
        singular_error = _relative_multiset_hausdorff(
            sector_smallest_singular[left_sector],
            sector_smallest_singular[right_sector],
        )
        condition_error = _relative_multiset_hausdorff(
            sector_conditions[left_sector],
            sector_conditions[right_sector],
        )
        conjugacy_records.append(
            {
                "left_sector": left_sector,
                "right_sector": right_sector,
                "pair_product_relative_hausdorff_error": product_error,
                "minimum_singular_relative_hausdorff_error": singular_error,
                "condition_relative_hausdorff_error": condition_error,
                "passed": max(product_error, singular_error, condition_error)
                <= CONJUGATE_DIAGNOSTIC_TOLERANCE,
            }
        )

    singular_block_count = sum(not record["full_rank"] for record in records)
    minimum_singular = min(record["minimum_singular_value"] for record in records)
    minimum_distance = min(record["spectral_distance"] for record in records)
    maximum_condition = max(record["condition_number"] for record in records)
    maximum_residual = max(record["direct_solve_relative_residual"] for record in records)
    checks = {
        "all_three_hundred_blocks_are_enumerated": (
            len(records) == EXPECTED_PAIR_COUNT
            and [record["pair_index"] for record in records] == list(range(EXPECTED_PAIR_COUNT))
        ),
        "all_operator_shapes_match_output_sectors": all(
            record["operator_shape"]
            == [
                EXTERNAL_SECTOR_DIMENSIONS[record["output_sector"]],
                EXTERNAL_SECTOR_DIMENSIONS[record["output_sector"]],
            ]
            for record in records
        ),
        "all_full_singular_spectra_are_stored": all(
            len(record["singular_values"]) == EXTERNAL_SECTOR_DIMENSIONS[record["output_sector"]]
            for record in records
        ),
        "all_rank_thresholds_use_registered_formula": all(
            record["rank_threshold"]
            == (
                RANK_THRESHOLD_FACTOR
                * np.finfo(float).eps
                * max(record["operator_shape"])
                * record["maximum_singular_value"]
            )
            for record in records
        ),
        "conjugate_sector_diagnostics_are_within_tolerance": all(
            record["passed"] for record in conjugacy_records
        ),
        "all_block_values_are_finite": bool(
            _all_numeric_values_finite(records) and _all_numeric_values_finite(conjugacy_records)
        ),
    }
    hypothesis_checks = {
        "no_numerically_singular_blocks": singular_block_count == 0,
        "minimum_singular_value_above_floor": (minimum_singular >= MINIMUM_OPERATOR_SINGULAR_VALUE),
        "minimum_spectral_distance_above_floor": (minimum_distance >= MINIMUM_SPECTRAL_DISTANCE),
        "maximum_condition_number_below_ceiling": (
            maximum_condition <= MAXIMUM_OPERATOR_CONDITION_NUMBER
        ),
        "maximum_direct_solve_residual_below_ceiling": (
            maximum_residual <= MAXIMUM_DIRECT_SOLVE_RESIDUAL
        ),
    }
    return {
        "direct_solve_seed": DIRECT_SOLVE_SEED,
        "rank_threshold_formula": (
            "100 * machine_epsilon * max(operator_shape) * maximum_singular_value"
        ),
        "block_count": len(records),
        "block_records": records,
        "numerically_singular_block_count": singular_block_count,
        "minimum_operator_singular_value": minimum_singular,
        "minimum_spectral_distance": minimum_distance,
        "maximum_operator_condition_number": maximum_condition,
        "maximum_direct_solve_relative_residual": maximum_residual,
        "conjugate_sector_records": conjugacy_records,
        "maximum_conjugate_diagnostic_relative_error": max(
            max(
                record["pair_product_relative_hausdorff_error"],
                record["minimum_singular_relative_hausdorff_error"],
                record["condition_relative_hausdorff_error"],
            )
            for record in conjugacy_records
        ),
        "checks": checks,
        "structural_passed": all(checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _sector_sylvester_probe_audit(
    sector_actions: dict[int, ComplexArray],
    external_matrices: dict[int, ComplexArray],
) -> dict[str, Any]:
    generator = np.random.default_rng(SYLVESTER_PROBE_SEED)
    sector_records: list[dict[str, Any]] = []
    failure_count = 0
    maximum_float = np.finfo(float).max

    for sector in OUTPUT_SECTOR_ORDER:
        external = external_matrices[sector]
        pair_action = sector_actions[sector]
        probe_records: list[dict[str, Any]] = []
        for probe_index in range(SYLVESTER_PROBES_PER_SECTOR):
            right_hand_side = generator.standard_normal(
                (external.shape[0], pair_action.shape[0])
            ) + 1j * generator.standard_normal((external.shape[0], pair_action.shape[0]))
            right_hand_side /= np.linalg.norm(right_hand_side, ord="fro")
            failed = False
            try:
                solution = linalg.solve_sylvester(
                    external,
                    -pair_action,
                    right_hand_side,
                )
                residual = float(
                    np.linalg.norm(
                        external @ solution - solution @ pair_action - right_hand_side,
                        ord="fro",
                    )
                    / max(
                        float(np.linalg.norm(right_hand_side, ord="fro")),
                        np.finfo(float).tiny,
                    )
                )
                amplification = float(
                    np.linalg.norm(solution, ord="fro")
                    / max(
                        float(np.linalg.norm(right_hand_side, ord="fro")),
                        np.finfo(float).tiny,
                    )
                )
                if not (
                    np.all(np.isfinite(solution))
                    and np.isfinite(residual)
                    and np.isfinite(amplification)
                ):
                    failed = True
            except (ValueError, np.linalg.LinAlgError):
                failed = True
                residual = maximum_float
                amplification = maximum_float
                solution = np.zeros_like(right_hand_side)
            if failed:
                failure_count += 1
                residual = maximum_float
                amplification = maximum_float
            probe_records.append(
                {
                    "probe_index": probe_index,
                    "right_hand_side_shape": list(right_hand_side.shape),
                    "right_hand_side_sha256": q011c._array_sha256(right_hand_side),
                    "solution_sha256": q011c._array_sha256(solution),
                    "relative_equation_residual": residual,
                    "response_amplification": amplification,
                    "solver_failed": failed,
                    "passed": (
                        not failed
                        and residual <= MAXIMUM_SYLVESTER_PROBE_RESIDUAL
                        and amplification <= MAXIMUM_SYLVESTER_RESPONSE_AMPLIFICATION
                    ),
                }
            )
        sector_records.append(
            {
                "output_sector": sector,
                "external_dimension": int(external.shape[0]),
                "pair_count": int(pair_action.shape[0]),
                "operator_scalar_dimension": int(external.shape[0] * pair_action.shape[0]),
                "probe_records": probe_records,
                "maximum_relative_equation_residual": max(
                    record["relative_equation_residual"] for record in probe_records
                ),
                "maximum_response_amplification": max(
                    record["response_amplification"] for record in probe_records
                ),
                "passed": all(record["passed"] for record in probe_records),
            }
        )

    maximum_residual = max(
        record["maximum_relative_equation_residual"] for record in sector_records
    )
    maximum_amplification = max(
        record["maximum_response_amplification"] for record in sector_records
    )
    checks = {
        "all_five_sectors_are_enumerated": (
            [record["output_sector"] for record in sector_records] == list(OUTPUT_SECTOR_ORDER)
        ),
        "twenty_registered_probes_are_enumerated": (
            sum(len(record["probe_records"]) for record in sector_records)
            == len(OUTPUT_SECTOR_ORDER) * SYLVESTER_PROBES_PER_SECTOR
        ),
        "sector_dimensions_are_registered": all(
            record["external_dimension"] == EXTERNAL_SECTOR_DIMENSIONS[record["output_sector"]]
            and record["pair_count"] == EXPECTED_SECTOR_PAIR_COUNTS[record["output_sector"]]
            for record in sector_records
        ),
        "all_probe_values_are_finite": bool(_all_numeric_values_finite(sector_records)),
    }
    hypothesis_checks = {
        "no_solver_or_nonfinite_failures": failure_count == 0,
        "maximum_equation_residual_below_ceiling": (
            maximum_residual <= MAXIMUM_SYLVESTER_PROBE_RESIDUAL
        ),
        "maximum_response_amplification_below_ceiling": (
            maximum_amplification <= MAXIMUM_SYLVESTER_RESPONSE_AMPLIFICATION
        ),
    }
    return {
        "seed": SYLVESTER_PROBE_SEED,
        "probes_per_sector": SYLVESTER_PROBES_PER_SECTOR,
        "probe_count": sum(len(record["probe_records"]) for record in sector_records),
        "sector_records": sector_records,
        "solver_or_nonfinite_failure_count": failure_count,
        "maximum_relative_equation_residual": maximum_residual,
        "maximum_response_amplification": maximum_amplification,
        "checks": checks,
        "structural_passed": all(checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
        "interpretation": (
            "Registered finite right-hand-side probes of the full nonnormal "
            "sector action; not a rigorous inverse-operator norm bound."
        ),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011c.OMEGA,
        "eta": q011c.ETA,
        "base_point": "Q011b stored forced fixed point at registered amplitude",
        "selected_block_order": list(SELECTED_BLOCK_ORDER),
        "selected_block_dimensions": {
            str(key): value for key, value in SELECTED_BLOCK_DIMENSIONS.items()
        },
        "selected_complex_dimension": EXPECTED_SELECTED_DIMENSION,
        "output_sector_order": list(OUTPUT_SECTOR_ORDER),
        "external_sector_dimensions": {
            str(key): value for key, value in EXTERNAL_SECTOR_DIMENSIONS.items()
        },
        "expected_sector_pair_counts": {
            str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()
        },
        "expected_pair_count": EXPECTED_PAIR_COUNT,
        "expected_external_dimension": EXPECTED_EXTERNAL_DIMENSION,
        "expected_full_fixed_leaf_dimension": EXPECTED_FULL_FIXED_LEAF_DIMENSION,
        "rank_threshold_factor": RANK_THRESHOLD_FACTOR,
        "direct_solve_seed": DIRECT_SOLVE_SEED,
        "action_seed": ACTION_SEED,
        "action_direction_count": ACTION_DIRECTION_COUNT,
        "sylvester_probe_seed": SYLVESTER_PROBE_SEED,
        "sylvester_probes_per_sector": SYLVESTER_PROBES_PER_SECTOR,
        "thresholds": {
            "structural": STRUCTURAL_TOLERANCE,
            "sector_leakage": SECTOR_LEAKAGE_TOLERANCE,
            "action_relative": ACTION_RELATIVE_TOLERANCE,
            "product_spectrum_hausdorff": PRODUCT_SPECTRUM_TOLERANCE,
            "minimum_operator_singular_value": MINIMUM_OPERATOR_SINGULAR_VALUE,
            "minimum_spectral_distance": MINIMUM_SPECTRAL_DISTANCE,
            "maximum_operator_condition_number": (MAXIMUM_OPERATOR_CONDITION_NUMBER),
            "maximum_direct_solve_residual": MAXIMUM_DIRECT_SOLVE_RESIDUAL,
            "conjugate_diagnostic_relative": (CONJUGATE_DIAGNOSTIC_TOLERANCE),
            "maximum_sylvester_probe_residual": (MAXIMUM_SYLVESTER_PROBE_RESIDUAL),
            "maximum_sylvester_response_amplification": (MAXIMUM_SYLVESTER_RESPONSE_AMPLIFICATION),
            "normal_dominance_gap": NORMAL_DOMINANCE_GAP_FLOOR,
            "full_fixed_leaf_spectral_radius": FULL_SPECTRAL_RADIUS_CEILING,
            "spectral_quotient_open_interval": [
                SPECTRAL_QUOTIENT_LOWER,
                SPECTRAL_QUOTIENT_UPPER,
            ],
        },
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "linear_split_digest_sha256": cycle["linear_split_digest_sha256"],
        "pair_family_digest_sha256": cycle["pair_family_digest_sha256"],
        "sector_probe_digest_sha256": cycle["sector_probe_digest_sha256"],
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


def run_forced_quadratic_homological_audit() -> dict[str, Any]:
    """Run the preregistered Q011d homological-family prequalification."""

    registered_parameters = _registered_parameters()
    sealed_input, stored_state, basis = _sealed_input_audit()
    (
        linear_split,
        selected_dynamics,
        external_matrices,
        selected_eigenvalues,
    ) = _canonical_linear_split(stored_state, basis)
    (
        quadratic_action,
        pairs,
        sector_indices,
        sector_actions,
        pair_products,
    ) = _quadratic_input_action_audit(
        selected_dynamics,
        selected_eigenvalues,
    )
    external_blocks = _external_homological_block_audit(
        pairs,
        sector_indices,
        pair_products,
        external_matrices,
    )
    sector_probes = _sector_sylvester_probe_audit(
        sector_actions,
        external_matrices,
    )

    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_input_audit": sealed_input,
    }
    linear_sections = {
        "canonical_linear_split_audit": linear_split,
    }
    pair_sections = {
        "quadratic_input_action_audit": quadratic_action,
        "external_homological_block_audit": external_blocks,
    }
    probe_sections = {
        "sector_sylvester_probe_audit": sector_probes,
    }
    input_digest = q011c._canonical_json_sha256(input_sections)
    linear_digest = q011c._canonical_json_sha256(linear_sections)
    pair_digest = q011c._canonical_json_sha256(pair_sections)
    probe_digest = q011c._canonical_json_sha256(probe_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **linear_sections,
        **pair_sections,
        **probe_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011c._canonical_json_sha256(input_sections)
        and linear_digest == q011c._canonical_json_sha256(linear_sections)
        and pair_digest == q011c._canonical_json_sha256(pair_sections)
        and probe_digest == q011c._canonical_json_sha256(probe_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )

    validity_gates = {
        "sealed_prior_inputs_replay": {
            "passed": sealed_input["passed"],
            "threshold": (
                "Q011c2 fresh replay, Q011c1 and Q011c outcomes, Q011b "
                "stored endpoint, Q006i calibration and package source reproduce"
            ),
            "value": sealed_input["checks"],
        },
        "canonical_linear_split_is_structural": {
            "passed": linear_split["structural_passed"],
            "threshold": (
                "selected dimensions 6/9/9, external dimensions "
                "144/144/144/153/153, residuals and conjugacy <=1e-10, "
                "fixed-leaf counts 24+2574"
            ),
            "value": linear_split["checks"],
        },
        "pair_enumeration_and_dimensions_reproduce": {
            "passed": bool(
                quadratic_action["checks"]["selected_coordinate_sector_counts_are_registered"]
                and quadratic_action["checks"]["pair_count_is_three_hundred"]
                and quadratic_action["checks"]["sector_pair_counts_are_registered"]
                and quadratic_action["checks"]["only_registered_output_sectors_occur"]
            ),
            "threshold": (
                "300 lexicographic pairs with sector counts "
                "102/54/54/45/45 and registered scalar dimensions"
            ),
            "value": {
                "pair_count": quadratic_action["pair_count"],
                "sector_pair_counts": quadratic_action["sector_pair_counts"],
                "sector_scalar_dimensions": quadratic_action["sector_scalar_dimensions"],
                "pair_enumeration_sha256": quadratic_action["pair_enumeration_sha256"],
            },
        },
        "symmetric_product_action_is_structural": {
            "passed": quadratic_action["passed"],
            "threshold": (
                "sector leakage <=1e-12, eight action errors <=1e-12 "
                "and five product-spectrum errors <=1e-10"
            ),
            "value": quadratic_action["checks"],
        },
        "all_blocks_and_sector_probes_are_enumerated": {
            "passed": bool(
                external_blocks["structural_passed"]
                and sector_probes["structural_passed"]
                and external_blocks["block_count"] == EXPECTED_PAIR_COUNT
                and sector_probes["probe_count"]
                == len(OUTPUT_SECTOR_ORDER) * SYLVESTER_PROBES_PER_SECTOR
            ),
            "threshold": (
                "300 complete SVD/rank/direct solves and 20 finite sector-wide Sylvester probes"
            ),
            "value": {
                "block_checks": external_blocks["checks"],
                "probe_checks": sector_probes["checks"],
                "block_count": external_blocks["block_count"],
                "probe_count": sector_probes["probe_count"],
            },
        },
        "conjugate_sector_scalar_diagnostics_close": {
            "passed": external_blocks["checks"][
                "conjugate_sector_diagnostics_are_within_tolerance"
            ],
            "threshold": (
                "pair-product, smallest-singular and condition multiset "
                "relative discrepancies <=1e-8 for 1/16 and 2/15"
            ),
            "value": external_blocks["conjugate_sector_records"],
        },
        "finite_strict_json_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "all values finite strict JSON; input, linear-split, "
                "pair-family and sector-probe digests plus runner reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_provenance_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    raw_hypotheses = {
        "all_external_blocks_are_full_rank_and_separated": bool(
            external_blocks["hypothesis_checks"]["no_numerically_singular_blocks"]
            and external_blocks["hypothesis_checks"]["minimum_singular_value_above_floor"]
            and external_blocks["hypothesis_checks"]["minimum_spectral_distance_above_floor"]
        ),
        "all_external_block_solves_are_conditioned": bool(
            external_blocks["hypothesis_checks"]["maximum_condition_number_below_ceiling"]
            and external_blocks["hypothesis_checks"]["maximum_direct_solve_residual_below_ceiling"]
        ),
        "symmetric_product_spectra_and_conjugacy_close": bool(
            quadratic_action["checks"]["sector_leakage_is_within_tolerance"]
            and quadratic_action["checks"]["all_sector_product_spectra_reproduce"]
            and external_blocks["checks"]["conjugate_sector_diagnostics_are_within_tolerance"]
        ),
        "all_sector_sylvester_probes_pass": sector_probes["hypothesis_passed"],
        "global_normal_dominance_stability_and_quotient_hold": linear_split["hypothesis_passed"],
    }
    hypothesis_gates = {
        "all_external_blocks_are_full_rank_and_separated": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["all_external_blocks_are_full_rank_and_separated"]
            ),
            "threshold": (
                "zero singular blocks; minimum singular value and spectral distance >=1e-5"
            ),
            "value": {
                "numerically_singular_block_count": external_blocks[
                    "numerically_singular_block_count"
                ],
                "minimum_operator_singular_value": external_blocks[
                    "minimum_operator_singular_value"
                ],
                "minimum_spectral_distance": external_blocks["minimum_spectral_distance"],
            },
        },
        "all_external_block_solves_are_conditioned": {
            "passed": bool(
                validity_passed and raw_hypotheses["all_external_block_solves_are_conditioned"]
            ),
            "threshold": ("maximum condition <=1e6 and direct-solve residual <=1e-10"),
            "value": {
                "maximum_operator_condition_number": external_blocks[
                    "maximum_operator_condition_number"
                ],
                "maximum_direct_solve_relative_residual": external_blocks[
                    "maximum_direct_solve_relative_residual"
                ],
            },
        },
        "symmetric_product_spectra_and_conjugacy_close": {
            "passed": bool(
                validity_passed and raw_hypotheses["symmetric_product_spectra_and_conjugacy_close"]
            ),
            "threshold": (
                "five K spectra reproduce pair products and conjugate sector diagnostics close"
            ),
            "value": {
                "maximum_product_spectrum_error": quadratic_action[
                    "maximum_product_spectrum_absolute_hausdorff_error"
                ],
                "maximum_conjugate_diagnostic_relative_error": (
                    external_blocks["maximum_conjugate_diagnostic_relative_error"]
                ),
            },
        },
        "all_sector_sylvester_probes_pass": {
            "passed": bool(validity_passed and raw_hypotheses["all_sector_sylvester_probes_pass"]),
            "threshold": (
                "20 probe residuals <=1e-10, response amplifications <=1e6 "
                "and no solver/nonfinite failure"
            ),
            "value": {
                "solver_or_nonfinite_failure_count": sector_probes[
                    "solver_or_nonfinite_failure_count"
                ],
                "maximum_relative_equation_residual": sector_probes[
                    "maximum_relative_equation_residual"
                ],
                "maximum_response_amplification": sector_probes["maximum_response_amplification"],
            },
        },
        "global_normal_dominance_stability_and_quotient_hold": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["global_normal_dominance_stability_and_quotient_hold"]
            ),
            "threshold": (
                "normal gap >=1e-6, radius <=0.9999 and 1<logarithmic spectral quotient<2"
            ),
            "value": {
                "global_modulus_normal_dominance_gap": linear_split[
                    "global_modulus_normal_dominance_gap"
                ],
                "full_fixed_leaf_spectral_radius": linear_split["full_fixed_leaf_spectral_radius"],
                "logarithmic_spectral_quotient_diagnostic": linear_split[
                    "logarithmic_spectral_quotient_diagnostic"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered forced quadratic external homological-family prequalification is invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the forced quadratic external homological family is "
            "numerically nonresonant and solvable"
        )
    else:
        outcome = "rejected"
        classification = "the forced quadratic external homological family fails prequalification"

    cycle: dict[str, Any] = {
        "question": (
            "Are all 300 forced quadratic external homological blocks "
            "numerically nonresonant, and do the five nonnormal sector "
            "operators solve the registered probes?"
        ),
        **pre_gate_sections,
        "input_digest_sha256": input_digest,
        "linear_split_digest_sha256": linear_digest,
        "pair_family_digest_sha256": pair_digest,
        "sector_probe_digest_sha256": probe_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = q011c._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["numerical_consequence"] = {
        "q011c_original_inconclusive_outcome_changed": False,
        "q011c1_localization_outcome_changed": False,
        "q011c2_cluster_selection_changed": False,
        "forced_quadratic_external_family_is_prequalified": bool(
            validity_passed and hypotheses_passed
        ),
        "individual_forced_modes_are_labeled": False,
        "forced_map_hessian_is_computed": False,
        "forced_quadratic_chart_is_constructed": False,
        "forced_invariant_manifold_exists": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 numerical prequalification of "
        "the complete quadratic external spectrum and registered finite "
        "Sylvester probes at one canonical forced endpoint. It is not a "
        "rigorous inverse-norm bound or a theorem on nonresonance, does "
        "not label individual forced modes, compute the forced-map "
        "Hessian or quadratic forcing, solve W2 or R2, verify a "
        "homological or invariance residual, construct an invariant "
        "manifold, prove existence, uniqueness, smoothness, nonlinear "
        "normal attraction or a basin, or cover other grids, amplitudes "
        "or boundary conditions."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011c_inconclusive_outcome_changed": False,
        "q011c1_accepted_localization_changed": False,
        "q011c2_accepted_reissue_changed": False,
        "q011b_accepted_fixed_point_changed": False,
        "q011a_nonzero_mean_obstruction_changed": False,
        "q006i_unforced_chart_outcome_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011e for the forced-map Hessian, quadratic forcing, "
        "dense W2/R2 chart and independent residual-order verification."
        if outcome == "accepted"
        else (
            "Localize the first failed linear split, pair block, "
            "conjugacy or sector-probe gate before constructing Q011e."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011d cycle failed strict serialization or digest")
    return cycle


def run_q011d_study() -> dict[str, Any]:
    cycle = run_forced_quadratic_homological_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 forced quadratic external homological-family "
                "nonresonance and finite sector-Sylvester probe audit"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011c.OMEGA,
            "eta": q011c.ETA,
            "selected_complex_dimension": EXPECTED_SELECTED_DIMENSION,
            "quadratic_pair_count": EXPECTED_PAIR_COUNT,
            "output_sector_count": len(OUTPUT_SECTOR_ORDER),
            "sector_probe_count": (len(OUTPUT_SECTOR_ORDER) * SYLVESTER_PROBES_PER_SECTOR),
            "claim": (
                "finite linear/quadratic-input operator prequalification "
                "only; no forced quadratic chart or invariant-manifold claim"
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
    result = run_q011d_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
