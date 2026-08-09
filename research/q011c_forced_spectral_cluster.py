"""Sealed Q011c forced fixed-leaf spectral-cluster continuation study."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy import linalg
from scipy.optimize import linear_sum_assignment

import research.q011b_zero_mean_forced_fixed_point as q011b
from ttim_lbm.checkerboard_filter import filter_multiplier
from ttim_lbm.nonresonance import (
    simple_hydrodynamic_modes,
    wave_vector_from_index,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

SIZE = q011b.SIZE
STRIPE_DIMENSION = q011b.STRIPE_DIMENSION
FIXED_LEAF_DIMENSION = q011b.FIXED_LEAF_DIMENSION
OMEGA = q011b.OMEGA
ETA = q011b.ETA

Q011B_ARTIFACT_SHA256 = "477202184694da1386c6b5bc0f0441e004a7a44f7a7b064f1d060d50adc66c27"
Q011B_RUNNER_SHA256 = "bac9448f280ce2dfb2e1627ce1558b792cb53e05746b94246baa6c329b8c8ef0"
Q011B_INPUT_DIGEST = "53dea81353ed4bcd77ab0c06533528f6d867d8b1bfa80d3d2ac3eddd7cf7dfbb"
Q011B_FIXED_POINT_DIGEST = "8db05ad1e7ae7806b70b6330d798f6dad05bc8718027ba13cb315116b021b17c"
Q011B_SPECTRUM_DIGEST = "3ab8866e141b64a4d1d81bdfae1a70c61d8e7964d8480e2bd7ec7c7e174850fc"
Q011B_RESULT_DIGEST = "66c4b579dbd7d7c391fd2017f165c2de251ecf850b7c485cb936b9742c8addf6"
Q006H_ARTIFACT_SHA256 = "71ff668cbc247450029840bf5de71e6ecbd364c5fcca21c9e8ec8085a5ee956c"
SEALED_PACKAGE_SOURCE_SHA256 = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"

AMPLITUDE_FACTORS = tuple(index / 8.0 for index in range(9))
CHECKPOINT_FACTORS = (0.0, 0.5, 1.0)
SELECTED_BLOCKS = {
    0: (-1, 1),
    1: (-1, 0, 1),
    16: (-1, 0, 1),
}
SELECTED_DIMENSIONS = {0: 6, 1: 9, 16: 9}
MODE_ORDER = ("shear", "acoustic_positive", "acoustic_negative")

STATE_DISTANCE_TOLERANCE = 1.0e-11
STATE_RELATIVE_DISTANCE_TOLERANCE = 1.0e-8
ADJACENT_ANGLE_TOLERANCE = 0.05
REFERENCE_ALIGNMENT_FLOOR = 0.95
EXTERNAL_EIGENVALUE_SEPARATION_FLOOR = 1.0e-6
PROJECTOR_NORM_CEILING = 100.0
STRUCTURAL_RESIDUAL_TOLERANCE = 1.0e-10
REVERSAL_ANGLE_TOLERANCE = 1.0e-6
DIRECT_ENDPOINT_ANGLE_TOLERANCE = 1.0e-6
CONJUGACY_RELATIVE_TOLERANCE = 1.0e-10
CONJUGACY_ANGLE_TOLERANCE = 1.0e-6
SYLVESTER_SEPARATION_FLOOR = 1.0e-5
NORMAL_DOMINANCE_GAP_FLOOR = 1.0e-6
ENDPOINT_REPRODUCTION_TOLERANCE = 1.0e-12


def _canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _array_sha256(value: npt.ArrayLike) -> str:
    array = np.ascontiguousarray(value)
    digest = sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(b"\0")
    digest.update(json.dumps(array.shape).encode("ascii"))
    digest.update(b"\0")
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _relative_error(left: npt.ArrayLike, right: npt.ArrayLike) -> float:
    left_array = np.asarray(left)
    right_array = np.asarray(right)
    denominator = max(float(np.linalg.norm(right_array)), np.finfo(float).tiny)
    return float(np.linalg.norm(left_array - right_array) / denominator)


def _complex_records(values: npt.ArrayLike) -> list[dict[str, float]]:
    entries = [complex(value) for value in np.asarray(values).ravel()]
    entries.sort(key=lambda value: (value.real, value.imag))
    return [{"real": float(value.real), "imag": float(value.imag)} for value in entries]


def _hausdorff(left: npt.ArrayLike, right: npt.ArrayLike) -> float:
    left_values = np.asarray(left, dtype=np.complex128).ravel()
    right_values = np.asarray(right, dtype=np.complex128).ravel()
    distances = np.abs(left_values[:, None] - right_values[None, :])
    return float(
        max(
            np.max(np.min(distances, axis=1)),
            np.max(np.min(distances, axis=0)),
        )
    )


def _orthonormal_basis(value: npt.ArrayLike) -> ComplexArray:
    matrix = np.asarray(value, dtype=np.complex128)
    basis, triangular = np.linalg.qr(matrix, mode="reduced")
    diagonal = np.abs(np.diag(triangular))
    if (
        matrix.ndim != 2
        or matrix.shape[1] == 0
        or diagonal.size != matrix.shape[1]
        or float(np.min(diagonal))
        <= 1.0e-12 * max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    ):
        raise np.linalg.LinAlgError("reference columns do not span the requested cluster")
    return np.asarray(basis)


def _maximum_principal_angle(
    left: npt.ArrayLike,
    right: npt.ArrayLike,
) -> float:
    left_basis = _orthonormal_basis(left)
    right_basis = _orthonormal_basis(right)
    if left_basis.shape != right_basis.shape:
        raise ValueError("subspaces have different dimensions")
    return float(np.max(linalg.subspace_angles(left_basis, right_basis)))


def _subspace_alignment(
    left: npt.ArrayLike,
    right: npt.ArrayLike,
) -> float:
    left_basis = _orthonormal_basis(left)
    right_basis = _orthonormal_basis(right)
    singular_values = linalg.svdvals(left_basis.conj().T @ right_basis)
    return float(np.clip(singular_values[-1], 0.0, 1.0))


def _sealed_input_audit() -> tuple[dict[str, Any], Array]:
    artifact_directory = Path(__file__).resolve().parent / "artifacts"
    q011b_artifact_path = artifact_directory / "q011b_zero_mean_forced_fixed_point.json"
    q006h_artifact_path = artifact_directory / "q006h_cluster_complete.json"
    q011b_runner_path = Path(q011b.__file__).resolve()
    q011b_artifact = json.loads(q011b_artifact_path.read_text(encoding="utf-8"))
    q006h_artifact = json.loads(q006h_artifact_path.read_text(encoding="utf-8"))
    fresh_q011b_cycle = q011b.run_zero_mean_forced_fixed_point_audit()
    selected_family = q006h_artifact["cycle"]["selected_family"]
    stored_endpoint = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    current_source = source_metadata()
    checks = {
        "q011b_artifact_sha256_matches": (
            _file_sha256(q011b_artifact_path) == Q011B_ARTIFACT_SHA256
        ),
        "q011b_runner_sha256_matches": (_file_sha256(q011b_runner_path) == Q011B_RUNNER_SHA256),
        "q011b_cycle_replays_exactly": (q011b_artifact["cycle"] == fresh_q011b_cycle),
        "q011b_gate_and_outcome_reproduce": (
            q011b_artifact["study_gate"] == "passed"
            and q011b_artifact["scientific_outcome"] == "accepted"
            and len(fresh_q011b_cycle["validity_gates"]) == 6
            and len(fresh_q011b_cycle["hypothesis_gates"]) == 4
            and all(gate["passed"] for gate in fresh_q011b_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in fresh_q011b_cycle["hypothesis_gates"].values())
        ),
        "q011b_digests_match": (
            fresh_q011b_cycle["input_digest_sha256"] == Q011B_INPUT_DIGEST
            and fresh_q011b_cycle["fixed_point_digest_sha256"] == Q011B_FIXED_POINT_DIGEST
            and fresh_q011b_cycle["spectrum_digest_sha256"] == Q011B_SPECTRUM_DIGEST
            and fresh_q011b_cycle["result_digest_sha256"] == Q011B_RESULT_DIGEST
        ),
        "q006h_artifact_sha256_matches": (
            _file_sha256(q006h_artifact_path) == Q006H_ARTIFACT_SHA256
        ),
        "q006h_package_source_matches": (
            q006h_artifact["source"]["package_source_sha256"] == SEALED_PACKAGE_SOURCE_SHA256
            and current_source["package_source_sha256"] == SEALED_PACKAGE_SOURCE_SHA256
        ),
        "q006h_selected_family_reproduces": (
            q006h_artifact["study_gate"] == "passed"
            and q006h_artifact["scientific_outcome"] == "accepted"
            and q006h_artifact["cycle"]["scientific_classification"]
            == "cluster-complete filtered finite-ladder prequalification passed"
            and selected_family["eta"] == ETA
            and selected_family["omega"] == OMEGA
            and selected_family["viable"]
            and selected_family["spectral_gates"]["normal_dominance_gap"]["threshold"] == 1.0e-6
            and selected_family["spectral_gates"]["selected_riesz_projector_norm"]["threshold"]
            == 100.0
        ),
        "stored_endpoint_is_finite_and_positive": bool(
            np.all(np.isfinite(stored_endpoint)) and np.min(stored_endpoint) > 0.0
        ),
    }
    return {
        "q011b_artifact": {
            "filename": q011b_artifact_path.name,
            "sha256": _file_sha256(q011b_artifact_path),
            "runner_filename": q011b_runner_path.name,
            "runner_sha256": _file_sha256(q011b_runner_path),
            "input_digest_sha256": fresh_q011b_cycle["input_digest_sha256"],
            "fixed_point_digest_sha256": fresh_q011b_cycle["fixed_point_digest_sha256"],
            "spectrum_digest_sha256": fresh_q011b_cycle["spectrum_digest_sha256"],
            "result_digest_sha256": fresh_q011b_cycle["result_digest_sha256"],
            "endpoint_state_sha256": _array_sha256(stored_endpoint),
            "endpoint_spectrum_targets": {
                "zero_wave_unrestricted_unit_eigenvalue_count": (
                    fresh_q011b_cycle["spectrum_audit"][
                        "zero_wave_unrestricted_unit_eigenvalue_count"
                    ]
                ),
                "maximum_fixed_leaf_eigenvalue_modulus": (
                    fresh_q011b_cycle["spectrum_audit"]["maximum_fixed_leaf_eigenvalue_modulus"]
                ),
                "maximum_modulus_wave_index": fresh_q011b_cycle["spectrum_audit"][
                    "maximum_modulus_wave_index"
                ],
                "minimum_i_minus_j_singular_value": fresh_q011b_cycle["spectrum_audit"][
                    "minimum_i_minus_j_singular_value"
                ],
                "minimum_singular_value_wave_index": fresh_q011b_cycle["spectrum_audit"][
                    "minimum_singular_value_wave_index"
                ],
                "maximum_i_minus_j_condition_number": fresh_q011b_cycle["spectrum_audit"][
                    "maximum_i_minus_j_condition_number"
                ],
                "maximum_condition_number_wave_index": fresh_q011b_cycle["spectrum_audit"][
                    "maximum_condition_number_wave_index"
                ],
            },
        },
        "q006h_artifact": {
            "filename": q006h_artifact_path.name,
            "sha256": _file_sha256(q006h_artifact_path),
            "package_source_sha256": q006h_artifact["source"]["package_source_sha256"],
            "classification": q006h_artifact["cycle"]["scientific_classification"],
            "selected_eta": selected_family["eta"],
            "selected_omega": selected_family["omega"],
            "selected_minimum_normal_dominance_gap": selected_family[
                "minimum_normal_dominance_gap"
            ],
            "selected_minimum_local_sylvester_separation": (
                selected_family["spectral_gates"]["local_sylvester_separation"]["value"]
            ),
            "selected_maximum_projector_norm": selected_family["spectral_gates"][
                "selected_riesz_projector_norm"
            ]["value"],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }, stored_endpoint


def _scaled_step(state: Array, factor: float) -> Array:
    return q011b.zero_mean_forced_filtered_bgk_periodic_step(
        state,
        OMEGA,
        ETA,
        factor * q011b._stripe_force(),
    )


def _scaled_residual_metrics(
    state: Array,
    factor: float,
    basis: Array,
) -> tuple[Array, Array, dict[str, float]]:
    residual = (_scaled_step(state, factor) - state).ravel()
    projected = basis.T @ residual
    return (
        residual,
        projected,
        {
            "projected_l2": float(np.linalg.norm(projected)),
            "full_l2": float(np.linalg.norm(residual)),
            "maximum_component": float(np.max(np.abs(residual))),
        },
    )


def _solve_fixed_point(
    factor: float,
    initial_coordinate: Array,
    rest: Array,
    basis: Array,
) -> tuple[Array, Array, dict[str, Any]]:
    coordinate = np.asarray(initial_coordinate, dtype=np.float64).copy()
    trace: list[dict[str, Any]] = []
    status = "maximum_steps_reached"
    for iteration in range(q011b.NEWTON_MAXIMUM_STEPS + 1):
        state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
        residual, projected, metrics = _scaled_residual_metrics(
            state,
            factor,
            basis,
        )
        record: dict[str, Any] = {
            "iteration": iteration,
            **metrics,
        }
        if (
            not np.all(np.isfinite(coordinate))
            or not np.all(np.isfinite(residual))
            or not np.all(np.isfinite(projected))
        ):
            record["decision"] = "nonfinite_failure"
            trace.append(record)
            status = "nonfinite_failure"
            break
        if metrics["projected_l2"] <= q011b.PROJECTED_RESIDUAL_TOLERANCE:
            record["decision"] = "projected_tolerance_reached"
            trace.append(record)
            status = "projected_tolerance_reached"
            break
        if iteration == q011b.NEWTON_MAXIMUM_STEPS:
            record["decision"] = "maximum_steps_reached"
            trace.append(record)
            break

        jacobian = q011b.RectangularFilteredBGKJacobian.at_state(
            state,
            OMEGA,
            ETA,
        )
        reduced_derivative = basis.T @ (jacobian.matmat(basis) - basis)
        record["reduced_jacobian_condition_number"] = float(np.linalg.cond(reduced_derivative))
        try:
            newton_step = linalg.solve(
                reduced_derivative,
                -projected,
                assume_a="gen",
                check_finite=True,
            )
        except linalg.LinAlgError:
            record["decision"] = "linear_solve_failure"
            trace.append(record)
            status = "linear_solve_failure"
            break
        record["newton_step_l2"] = float(np.linalg.norm(newton_step))
        trial_records: list[dict[str, float]] = []
        accepted_factor: float | None = None
        accepted_norm: float | None = None
        for line_factor in q011b.LINE_SEARCH_FACTORS:
            trial_coordinate = coordinate + line_factor * newton_step
            trial_state = rest + (basis @ trial_coordinate).reshape(
                SIZE,
                1,
                9,
            )
            _, trial_projected, _ = _scaled_residual_metrics(
                trial_state,
                factor,
                basis,
            )
            trial_norm = float(np.linalg.norm(trial_projected))
            trial_records.append(
                {
                    "factor": line_factor,
                    "projected_l2": trial_norm,
                }
            )
            if np.isfinite(trial_norm) and trial_norm < metrics["projected_l2"]:
                coordinate = trial_coordinate
                accepted_factor = line_factor
                accepted_norm = trial_norm
                break
        record["line_search_trials"] = trial_records
        record["accepted_factor"] = accepted_factor
        record["accepted_projected_l2"] = accepted_norm
        if accepted_factor is None:
            record["decision"] = "line_search_failure"
            trace.append(record)
            status = "line_search_failure"
            break
        record["decision"] = "accepted_step"
        trace.append(record)

    state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
    residual, _, metrics = _scaled_residual_metrics(state, factor, basis)
    checks = {
        "values_are_finite": bool(
            np.all(np.isfinite(coordinate))
            and np.all(np.isfinite(state))
            and np.all(np.isfinite(residual))
        ),
        "projected_residual_within_tolerance": (
            metrics["projected_l2"] <= q011b.PROJECTED_RESIDUAL_TOLERANCE
        ),
        "full_residual_within_tolerance": (metrics["full_l2"] <= q011b.FULL_RESIDUAL_TOLERANCE),
        "component_residual_within_tolerance": (
            metrics["maximum_component"] <= q011b.COMPONENT_RESIDUAL_TOLERANCE
        ),
    }
    return (
        coordinate,
        state,
        {
            "amplitude_factor": factor,
            "status": status,
            "accepted_newton_steps": sum(record["decision"] == "accepted_step" for record in trace),
            "trace": trace,
            "terminal_coordinate_sha256": _array_sha256(coordinate),
            "terminal_state_sha256": _array_sha256(state),
            "terminal_metrics": metrics,
            "checks": checks,
            "converged": all(checks.values()),
        },
    )


def _fixed_point_path_audit(
    stored_endpoint: Array,
    basis: Array,
) -> tuple[dict[float, Array], dict[float, Array], dict[str, Any]]:
    rest = q011b.uniform_equilibrium(SIZE, 1, np.zeros(3))
    forward_states: dict[float, Array] = {}
    backward_states: dict[float, Array] = {}
    forward_records: list[dict[str, Any]] = []
    backward_records: list[dict[str, Any]] = []

    coordinate = np.zeros(FIXED_LEAF_DIMENSION, dtype=np.float64)
    for factor in AMPLITUDE_FACTORS:
        coordinate, state, record = _solve_fixed_point(
            factor,
            coordinate,
            rest,
            basis,
        )
        forward_states[factor] = state
        forward_records.append(record)

    coordinate = basis.T @ (stored_endpoint - rest).ravel()
    for factor in reversed(AMPLITUDE_FACTORS):
        coordinate, state, record = _solve_fixed_point(
            factor,
            coordinate,
            rest,
            basis,
        )
        backward_states[factor] = state
        backward_records.append(record)

    comparison_records: list[dict[str, Any]] = []
    for factor in AMPLITUDE_FACTORS:
        forward = forward_states[factor]
        backward = backward_states[factor]
        distance = float(np.linalg.norm(forward - backward))
        scale = max(
            float(np.linalg.norm(forward - rest)),
            float(np.linalg.norm(backward - rest)),
            np.finfo(float).tiny,
        )
        relative = distance / scale
        relative_applicable = factor > 0.0
        comparison_records.append(
            {
                "amplitude_factor": factor,
                "population_l2_distance": distance,
                "departure_scale": scale,
                "relative_distance": relative,
                "relative_gate_applicable": relative_applicable,
                "absolute_passed": distance <= STATE_DISTANCE_TOLERANCE,
                "relative_passed": (
                    not relative_applicable or relative <= STATE_RELATIVE_DISTANCE_TOLERANCE
                ),
            }
        )

    endpoint_distance = float(np.linalg.norm(forward_states[1.0] - stored_endpoint))
    endpoint_scale = max(
        float(np.linalg.norm(forward_states[1.0] - rest)),
        float(np.linalg.norm(stored_endpoint - rest)),
        np.finfo(float).tiny,
    )
    endpoint_relative = endpoint_distance / endpoint_scale
    checks = {
        "registered_forward_node_count_is_nine": len(forward_records) == 9,
        "registered_backward_node_count_is_nine": len(backward_records) == 9,
        "all_forward_solves_converged": all(record["converged"] for record in forward_records),
        "all_backward_solves_converged": all(record["converged"] for record in backward_records),
        "all_node_absolute_distances_pass": all(
            record["absolute_passed"] for record in comparison_records
        ),
        "all_nonzero_node_relative_distances_pass": all(
            record["relative_passed"] for record in comparison_records
        ),
        "endpoint_absolute_distance_passes": (endpoint_distance <= STATE_DISTANCE_TOLERANCE),
        "endpoint_relative_distance_passes": (
            endpoint_relative <= STATE_RELATIVE_DISTANCE_TOLERANCE
        ),
        "all_path_records_are_finite": bool(
            _all_numeric_values_finite(forward_records)
            and _all_numeric_values_finite(backward_records)
            and _all_numeric_values_finite(comparison_records)
        ),
    }
    return (
        forward_states,
        backward_states,
        {
            "amplitude_factors": list(AMPLITUDE_FACTORS),
            "forward_records": forward_records,
            "backward_records": backward_records,
            "forward_backward_comparisons": comparison_records,
            "endpoint_population_l2_distance": endpoint_distance,
            "endpoint_departure_scale": endpoint_scale,
            "endpoint_relative_distance": endpoint_relative,
            "forward_state_sha256": {
                str(factor): _array_sha256(forward_states[factor]) for factor in AMPLITUDE_FACTORS
            },
            "backward_state_sha256": {
                str(factor): _array_sha256(backward_states[factor]) for factor in AMPLITUDE_FACTORS
            },
            "checks": checks,
            "passed": all(checks.values()),
        },
    )


def _canonical_kx_index(index: int) -> int:
    return index if index <= SIZE // 2 else index - SIZE


def _active_matrix(state: Array, block_index: int, basis: Array) -> ComplexArray:
    kx = 2.0 * np.pi * block_index / SIZE
    block = q011b._block_matrix(state, kx)
    if block_index == 0:
        return np.asarray(basis.T @ block @ basis, dtype=np.complex128)
    return np.asarray(block, dtype=np.complex128)


def _reference_cluster(
    block_index: int,
    basis: Array,
) -> tuple[ComplexArray, ComplexArray, dict[str, Any]]:
    canonical_kx = _canonical_kx_index(block_index)
    columns: list[ComplexArray] = []
    target_values: list[complex] = []
    y = np.arange(SIZE, dtype=np.float64)
    mode_records: list[dict[str, Any]] = []
    for ky_index in SELECTED_BLOCKS[block_index]:
        wave_vector = wave_vector_from_index(
            (canonical_kx, ky_index),
            SIZE,
        )
        modes = simple_hydrodynamic_modes(*wave_vector, OMEGA)
        multiplier = filter_multiplier(*wave_vector, ETA)
        phase = np.exp(1j * wave_vector[1] * y) / np.sqrt(SIZE)
        for label in MODE_ORDER:
            mode = modes[label]
            physical = (phase[:, None] * mode.right_eigenvector[None, :]).reshape(STRIPE_DIMENSION)
            active_column = basis.T @ physical if block_index == 0 else physical
            columns.append(np.asarray(active_column))
            target_values.append(multiplier * mode.eigenvalue)
            mode_records.append(
                {
                    "wave_index": [canonical_kx, ky_index],
                    "label": label,
                    "eigenvalue": {
                        "real": float((multiplier * mode.eigenvalue).real),
                        "imag": float((multiplier * mode.eigenvalue).imag),
                    },
                }
            )
    raw = np.column_stack(columns)
    reference_basis = _orthonormal_basis(raw)
    targets = np.asarray(target_values, dtype=np.complex128)
    rest = q011b.uniform_equilibrium(SIZE, 1, np.zeros(3))
    active = _active_matrix(rest, block_index, basis)
    reference_dynamics = reference_basis.conj().T @ active @ reference_basis
    invariance = float(
        np.linalg.norm(active @ reference_basis - reference_basis @ reference_dynamics)
        / max(float(np.linalg.norm(active)), np.finfo(float).tiny)
    )
    return (
        reference_basis,
        targets,
        {
            "block_index": block_index,
            "canonical_kx_index": canonical_kx,
            "selected_ky_indices": list(SELECTED_BLOCKS[block_index]),
            "selected_dimension": reference_basis.shape[1],
            "reference_basis_sha256": _array_sha256(reference_basis),
            "target_eigenvalues": _complex_records(targets),
            "target_eigenvalues_sha256": _array_sha256(targets),
            "reference_invariance_relative_residual": invariance,
            "mode_records": mode_records,
        },
    )


@dataclass(frozen=True)
class OrderedCluster:
    basis: ComplexArray
    selected_dynamics: ComplexArray
    excluded_dynamics: ComplexArray
    projector: ComplexArray
    selected_eigenvalues: ComplexArray
    excluded_eigenvalues: ComplexArray
    selected_dimension: int
    selector_count: int
    external_eigenvalue_separation: float
    projector_norm: float
    schur_reconstruction_relative_residual: float
    schur_unitarity_frobenius_residual: float
    invariance_relative_residual: float
    projector_idempotency_frobenius_residual: float
    projector_commutator_relative_residual: float


def _ordered_cluster(
    matrix: npt.ArrayLike,
    target_eigenvalues: npt.ArrayLike,
) -> OrderedCluster:
    value = np.asarray(matrix, dtype=np.complex128)
    targets = np.asarray(target_eigenvalues, dtype=np.complex128).ravel()
    if (
        value.ndim != 2
        or value.shape[0] != value.shape[1]
        or targets.size == 0
        or targets.size >= value.shape[0]
    ):
        raise ValueError("ordered cluster inputs have invalid dimensions")
    all_values = linalg.eigvals(value, check_finite=True)
    rows, columns = linear_sum_assignment(np.abs(targets[:, None] - all_values[None, :]))
    if rows.size != targets.size:
        raise np.linalg.LinAlgError("Hungarian cluster match is incomplete")
    selected_indices = {int(index) for index in columns}
    selected_reference = all_values[sorted(selected_indices)]
    excluded_reference = all_values[
        [index for index in range(all_values.size) if index not in selected_indices]
    ]

    def selector(eigenvalue: complex) -> bool:
        selected_distance = float(np.min(np.abs(eigenvalue - selected_reference)))
        excluded_distance = float(np.min(np.abs(eigenvalue - excluded_reference)))
        return selected_distance < excluded_distance

    triangular, unitary, count = linalg.schur(
        value,
        output="complex",
        sort=selector,
        check_finite=True,
    )
    selected_dimension = targets.size
    if count != selected_dimension:
        raise np.linalg.LinAlgError("ordered Schur selector changed the registered dimension")
    selected = np.asarray(triangular[:selected_dimension, :selected_dimension])
    coupling = triangular[:selected_dimension, selected_dimension:]
    excluded = np.asarray(triangular[selected_dimension:, selected_dimension:])
    projector_coupling = linalg.solve_sylvester(
        selected,
        -excluded,
        coupling,
    )
    schur_projector = np.zeros_like(triangular)
    schur_projector[:selected_dimension, :selected_dimension] = np.eye(selected_dimension)
    schur_projector[
        :selected_dimension,
        selected_dimension:,
    ] = projector_coupling
    projector = unitary @ schur_projector @ unitary.conj().T
    cluster_basis = np.asarray(unitary[:, :selected_dimension])
    selected_values = linalg.eigvals(selected, check_finite=True)
    excluded_values = linalg.eigvals(excluded, check_finite=True)
    external_separation = float(np.min(np.abs(selected_values[:, None] - excluded_values[None, :])))
    matrix_scale = max(float(np.linalg.norm(value)), np.finfo(float).tiny)
    reconstruction = float(
        np.linalg.norm(
            value - unitary @ triangular @ unitary.conj().T,
            ord="fro",
        )
        / matrix_scale
    )
    unitarity = float(
        np.linalg.norm(
            unitary.conj().T @ unitary - np.eye(value.shape[0]),
            ord="fro",
        )
    )
    invariance = float(
        np.linalg.norm(
            value @ cluster_basis - cluster_basis @ selected,
            ord="fro",
        )
        / matrix_scale
    )
    idempotency = float(np.linalg.norm(projector @ projector - projector, ord="fro"))
    commutator = float(
        np.linalg.norm(value @ projector - projector @ value, ord="fro") / matrix_scale
    )
    return OrderedCluster(
        basis=cluster_basis,
        selected_dynamics=selected,
        excluded_dynamics=excluded,
        projector=np.asarray(projector),
        selected_eigenvalues=np.asarray(selected_values),
        excluded_eigenvalues=np.asarray(excluded_values),
        selected_dimension=int(selected_dimension),
        selector_count=int(count),
        external_eigenvalue_separation=external_separation,
        projector_norm=float(np.linalg.norm(projector, ord=2)),
        schur_reconstruction_relative_residual=reconstruction,
        schur_unitarity_frobenius_residual=unitarity,
        invariance_relative_residual=invariance,
        projector_idempotency_frobenius_residual=idempotency,
        projector_commutator_relative_residual=commutator,
    )


def _cluster_record(
    factor: float,
    block_index: int,
    cluster: OrderedCluster,
    reference_basis: ComplexArray,
    previous_basis: ComplexArray | None,
) -> dict[str, Any]:
    adjacent_angle = (
        0.0 if previous_basis is None else _maximum_principal_angle(previous_basis, cluster.basis)
    )
    structural_maximum = max(
        cluster.schur_reconstruction_relative_residual,
        cluster.schur_unitarity_frobenius_residual,
        cluster.invariance_relative_residual,
        cluster.projector_idempotency_frobenius_residual,
        cluster.projector_commutator_relative_residual,
    )
    return {
        "amplitude_factor": factor,
        "block_index": block_index,
        "selected_dimension": cluster.selected_dimension,
        "selector_count": cluster.selector_count,
        "selected_eigenvalues": _complex_records(cluster.selected_eigenvalues),
        "selected_eigenvalues_sha256": _array_sha256(cluster.selected_eigenvalues),
        "excluded_eigenvalues_sha256": _array_sha256(cluster.excluded_eigenvalues),
        "basis_sha256": _array_sha256(cluster.basis),
        "projector_sha256": _array_sha256(cluster.projector),
        "adjacent_maximum_principal_angle": adjacent_angle,
        "reference_minimum_singular_value_alignment": (
            _subspace_alignment(reference_basis, cluster.basis)
        ),
        "external_eigenvalue_absolute_separation": (cluster.external_eigenvalue_separation),
        "projector_two_norm": cluster.projector_norm,
        "schur_reconstruction_relative_residual": (cluster.schur_reconstruction_relative_residual),
        "schur_unitarity_frobenius_residual": (cluster.schur_unitarity_frobenius_residual),
        "selected_invariance_relative_residual": (cluster.invariance_relative_residual),
        "projector_idempotency_frobenius_residual": (
            cluster.projector_idempotency_frobenius_residual
        ),
        "projector_commutator_relative_residual": (cluster.projector_commutator_relative_residual),
        "maximum_structural_residual": structural_maximum,
    }


def _reference_audit(
    basis: Array,
) -> tuple[
    dict[int, ComplexArray],
    dict[int, ComplexArray],
    dict[str, Any],
]:
    reference_bases: dict[int, ComplexArray] = {}
    target_values: dict[int, ComplexArray] = {}
    records: list[dict[str, Any]] = []
    for block_index in SELECTED_BLOCKS:
        reference, targets, record = _reference_cluster(
            block_index,
            basis,
        )
        reference_bases[block_index] = reference
        target_values[block_index] = targets
        records.append(record)
    checks = {
        "selected_block_indices_are_registered": (tuple(SELECTED_BLOCKS) == (0, 1, 16)),
        "selected_dimensions_are_six_nine_nine": all(
            reference_bases[index].shape[1] == SELECTED_DIMENSIONS[index]
            for index in SELECTED_BLOCKS
        ),
        "total_complex_dimension_is_twenty_four": (
            sum(reference.shape[1] for reference in reference_bases.values()) == 24
        ),
        "reference_invariance_within_tolerance": all(
            record["reference_invariance_relative_residual"] <= STRUCTURAL_RESIDUAL_TOLERANCE
            for record in records
        ),
        "all_reference_values_are_finite": bool(
            all(
                np.all(np.isfinite(reference_bases[index]))
                and np.all(np.isfinite(target_values[index]))
                for index in SELECTED_BLOCKS
            )
        ),
    }
    return (
        reference_bases,
        target_values,
        {
            "records": records,
            "total_selected_complex_dimension": sum(
                reference.shape[1] for reference in reference_bases.values()
            ),
            "physical_real_dimension_under_conjugacy": 24,
            "checks": checks,
            "passed": all(checks.values()),
        },
    )


def _track_one_direction(
    factors: tuple[float, ...],
    states: dict[float, Array],
    basis: Array,
    reference_bases: dict[int, ComplexArray],
    initial_targets: dict[int, ComplexArray],
) -> tuple[
    dict[float, dict[int, OrderedCluster]],
    list[dict[str, Any]],
]:
    targets = {
        index: np.asarray(values, dtype=np.complex128).copy()
        for index, values in initial_targets.items()
    }
    previous_bases: dict[int, ComplexArray | None] = {index: None for index in SELECTED_BLOCKS}
    clusters: dict[float, dict[int, OrderedCluster]] = {}
    node_records: list[dict[str, Any]] = []
    for factor in factors:
        block_clusters: dict[int, OrderedCluster] = {}
        block_records: list[dict[str, Any]] = []
        for block_index in SELECTED_BLOCKS:
            active = _active_matrix(states[factor], block_index, basis)
            cluster = _ordered_cluster(active, targets[block_index])
            block_clusters[block_index] = cluster
            block_records.append(
                _cluster_record(
                    factor,
                    block_index,
                    cluster,
                    reference_bases[block_index],
                    previous_bases[block_index],
                )
            )
            targets[block_index] = cluster.selected_eigenvalues.copy()
            previous_bases[block_index] = cluster.basis
        clusters[factor] = block_clusters
        node_records.append(
            {
                "amplitude_factor": factor,
                "block_records": block_records,
            }
        )
    return clusters, node_records


def _cluster_path_audit(
    forward_states: dict[float, Array],
    backward_states: dict[float, Array],
    basis: Array,
    reference_bases: dict[int, ComplexArray],
    reference_targets: dict[int, ComplexArray],
) -> tuple[
    dict[float, dict[int, OrderedCluster]],
    dict[str, Any],
]:
    forward_clusters, forward_records = _track_one_direction(
        AMPLITUDE_FACTORS,
        forward_states,
        basis,
        reference_bases,
        reference_targets,
    )
    endpoint_targets = {
        index: forward_clusters[1.0][index].selected_eigenvalues for index in SELECTED_BLOCKS
    }
    backward_clusters, backward_records = _track_one_direction(
        tuple(reversed(AMPLITUDE_FACTORS)),
        backward_states,
        basis,
        reference_bases,
        endpoint_targets,
    )

    reversal_records: list[dict[str, Any]] = []
    for factor in AMPLITUDE_FACTORS:
        for block_index in SELECTED_BLOCKS:
            angle = _maximum_principal_angle(
                forward_clusters[factor][block_index].basis,
                backward_clusters[factor][block_index].basis,
            )
            reversal_records.append(
                {
                    "amplitude_factor": factor,
                    "block_index": block_index,
                    "maximum_principal_angle": angle,
                    "passed": angle <= REVERSAL_ANGLE_TOLERANCE,
                }
            )

    direct_records: list[dict[str, Any]] = []
    for block_index in SELECTED_BLOCKS:
        active = _active_matrix(
            forward_states[1.0],
            block_index,
            basis,
        )
        direct = _ordered_cluster(
            active,
            reference_targets[block_index],
        )
        continued = forward_clusters[1.0][block_index]
        angle = _maximum_principal_angle(
            continued.basis,
            direct.basis,
        )
        direct_records.append(
            {
                "block_index": block_index,
                "maximum_principal_angle": angle,
                "selected_spectrum_absolute_hausdorff_error": _hausdorff(
                    continued.selected_eigenvalues,
                    direct.selected_eigenvalues,
                ),
                "continued_projector_sha256": _array_sha256(continued.projector),
                "direct_projector_sha256": _array_sha256(direct.projector),
                "passed": angle <= DIRECT_ENDPOINT_ANGLE_TOLERANCE,
            }
        )

    conjugacy_records: list[dict[str, Any]] = []
    for factor in AMPLITUDE_FACTORS:
        positive = forward_clusters[factor][1]
        negative = forward_clusters[factor][16]
        projector_error = _relative_error(
            positive.projector,
            np.conjugate(negative.projector),
        )
        spectrum_error = _hausdorff(
            positive.selected_eigenvalues,
            np.conjugate(negative.selected_eigenvalues),
        )
        angle = _maximum_principal_angle(
            positive.basis,
            np.conjugate(negative.basis),
        )
        zero_projector = forward_clusters[factor][0].projector
        zero_imaginary = float(
            np.linalg.norm(zero_projector.imag)
            / max(
                float(np.linalg.norm(zero_projector)),
                np.finfo(float).tiny,
            )
        )
        conjugacy_records.append(
            {
                "amplitude_factor": factor,
                "plus_minus_projector_relative_error": projector_error,
                "plus_minus_spectrum_absolute_hausdorff_error": (spectrum_error),
                "plus_minus_subspace_maximum_principal_angle": angle,
                "zero_block_projector_imaginary_relative_norm": (zero_imaginary),
                "passed": bool(
                    projector_error <= CONJUGACY_RELATIVE_TOLERANCE
                    and spectrum_error <= CONJUGACY_RELATIVE_TOLERANCE
                    and angle <= CONJUGACY_ANGLE_TOLERANCE
                    and zero_imaginary <= CONJUGACY_RELATIVE_TOLERANCE
                ),
            }
        )

    all_block_records = [record for node in forward_records for record in node["block_records"]]
    initial_reproduction_records: list[dict[str, Any]] = []
    for block_index in SELECTED_BLOCKS:
        cluster = forward_clusters[0.0][block_index]
        initial_reproduction_records.append(
            {
                "block_index": block_index,
                "reference_range_maximum_principal_angle": (
                    _maximum_principal_angle(
                        reference_bases[block_index],
                        cluster.basis,
                    )
                ),
                "target_spectrum_absolute_hausdorff_error": _hausdorff(
                    reference_targets[block_index],
                    cluster.selected_eigenvalues,
                ),
            }
        )

    maximum_structural = max(record["maximum_structural_residual"] for record in all_block_records)
    maximum_adjacent = max(
        record["adjacent_maximum_principal_angle"] for record in all_block_records
    )
    minimum_alignment = min(
        record["reference_minimum_singular_value_alignment"] for record in all_block_records
    )
    minimum_external_separation = min(
        record["external_eigenvalue_absolute_separation"] for record in all_block_records
    )
    maximum_projector_norm = max(record["projector_two_norm"] for record in all_block_records)
    maximum_reversal = max(record["maximum_principal_angle"] for record in reversal_records)
    maximum_direct = max(record["maximum_principal_angle"] for record in direct_records)
    maximum_projector_conjugacy = max(
        record["plus_minus_projector_relative_error"] for record in conjugacy_records
    )
    maximum_spectrum_conjugacy = max(
        record["plus_minus_spectrum_absolute_hausdorff_error"] for record in conjugacy_records
    )
    maximum_conjugacy_angle = max(
        record["plus_minus_subspace_maximum_principal_angle"] for record in conjugacy_records
    )
    maximum_zero_imaginary = max(
        record["zero_block_projector_imaginary_relative_norm"] for record in conjugacy_records
    )

    structural_checks = {
        "node_and_block_count_is_registered": (
            len(forward_records) == 9
            and len(backward_records) == 9
            and len(all_block_records) == 27
        ),
        "all_selector_dimensions_are_registered": all(
            record["selected_dimension"] == SELECTED_DIMENSIONS[record["block_index"]]
            and record["selector_count"] == SELECTED_DIMENSIONS[record["block_index"]]
            for record in all_block_records
        ),
        "all_structural_residuals_within_tolerance": (
            maximum_structural <= STRUCTURAL_RESIDUAL_TOLERANCE
        ),
        "all_conjugacy_diagnostics_within_tolerance": all(
            record["passed"] for record in conjugacy_records
        ),
        "all_path_values_are_finite": bool(
            _all_numeric_values_finite(forward_records)
            and _all_numeric_values_finite(backward_records)
            and _all_numeric_values_finite(reversal_records)
            and _all_numeric_values_finite(direct_records)
            and _all_numeric_values_finite(conjugacy_records)
        ),
    }
    hypothesis_checks = {
        "adjacent_angles_within_tolerance": (maximum_adjacent <= ADJACENT_ANGLE_TOLERANCE),
        "reference_alignment_above_floor": (minimum_alignment >= REFERENCE_ALIGNMENT_FLOOR),
        "external_eigenvalue_separation_above_floor": (
            minimum_external_separation >= EXTERNAL_EIGENVALUE_SEPARATION_FLOOR
        ),
        "projector_norm_below_ceiling": (maximum_projector_norm <= PROJECTOR_NORM_CEILING),
        "path_reversal_angles_within_tolerance": (maximum_reversal <= REVERSAL_ANGLE_TOLERANCE),
        "direct_endpoint_angles_within_tolerance": (
            maximum_direct <= DIRECT_ENDPOINT_ANGLE_TOLERANCE
        ),
        "conjugacy_closure_passes": all(record["passed"] for record in conjugacy_records),
    }
    return forward_clusters, {
        "forward_node_records": forward_records,
        "backward_node_records": backward_records,
        "initial_reproduction_records": initial_reproduction_records,
        "path_reversal_records": reversal_records,
        "direct_endpoint_records": direct_records,
        "conjugacy_records": conjugacy_records,
        "summary": {
            "maximum_structural_residual": maximum_structural,
            "maximum_adjacent_principal_angle": maximum_adjacent,
            "minimum_reference_alignment": minimum_alignment,
            "minimum_external_eigenvalue_separation": (minimum_external_separation),
            "maximum_projector_two_norm": maximum_projector_norm,
            "maximum_path_reversal_principal_angle": maximum_reversal,
            "maximum_direct_endpoint_principal_angle": maximum_direct,
            "maximum_projector_conjugacy_relative_error": (maximum_projector_conjugacy),
            "maximum_spectrum_conjugacy_hausdorff_error": (maximum_spectrum_conjugacy),
            "maximum_conjugacy_principal_angle": maximum_conjugacy_angle,
            "maximum_zero_block_projector_imaginary_relative_norm": (maximum_zero_imaginary),
        },
        "structural_checks": structural_checks,
        "structural_passed": all(structural_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _sylvester_separation(cluster: OrderedCluster) -> float:
    selected_dimension = cluster.selected_dynamics.shape[0]
    excluded_dimension = cluster.excluded_dynamics.shape[0]
    operator = np.kron(
        np.eye(excluded_dimension, dtype=np.complex128),
        cluster.selected_dynamics,
    ) - np.kron(
        cluster.excluded_dynamics.T,
        np.eye(selected_dimension, dtype=np.complex128),
    )
    singular_values = linalg.svdvals(
        operator,
        overwrite_a=True,
        check_finite=True,
    )
    return float(singular_values[-1])


def _endpoint_resolvent_audit(
    stability_matrices: dict[int, ComplexArray],
    unrestricted_zero: ComplexArray,
    targets: dict[str, Any],
) -> dict[str, Any]:
    maximum_radius = -np.inf
    maximum_radius_index = -1
    minimum_singular = np.inf
    minimum_singular_index = -1
    maximum_condition = -np.inf
    maximum_condition_index = -1
    for block_index, matrix in stability_matrices.items():
        block_values = linalg.eigvals(matrix, check_finite=True)
        block_radius = float(np.max(np.abs(block_values)))
        if block_radius > maximum_radius:
            maximum_radius = block_radius
            maximum_radius_index = block_index
        singular_values = linalg.svdvals(
            np.eye(matrix.shape[0], dtype=np.complex128) - matrix,
            check_finite=True,
        )
        block_minimum = float(singular_values[-1])
        block_condition = float(singular_values[0] / singular_values[-1])
        if block_minimum < minimum_singular:
            minimum_singular = block_minimum
            minimum_singular_index = block_index
        if block_condition > maximum_condition:
            maximum_condition = block_condition
            maximum_condition_index = block_index
    zero_values = linalg.eigvals(unrestricted_zero, check_finite=True)
    unit_count = int(np.count_nonzero(np.abs(zero_values - 1.0) <= q011b.UNIT_EIGENVALUE_TOLERANCE))
    differences = {
        "unit_count": abs(unit_count - targets["zero_wave_unrestricted_unit_eigenvalue_count"]),
        "spectral_radius": abs(maximum_radius - targets["maximum_fixed_leaf_eigenvalue_modulus"]),
        "minimum_singular_value": abs(
            minimum_singular - targets["minimum_i_minus_j_singular_value"]
        ),
        "maximum_condition_number": abs(
            maximum_condition - targets["maximum_i_minus_j_condition_number"]
        ),
    }
    checks = {
        "unit_count_matches": differences["unit_count"] == 0,
        "spectral_radius_reproduces": (
            differences["spectral_radius"] <= ENDPOINT_REPRODUCTION_TOLERANCE
        ),
        "spectral_radius_witness_matches": (
            maximum_radius_index == targets["maximum_modulus_wave_index"]
        ),
        "minimum_singular_value_reproduces": (
            differences["minimum_singular_value"] <= ENDPOINT_REPRODUCTION_TOLERANCE
        ),
        "maximum_condition_number_reproduces": (
            differences["maximum_condition_number"] <= ENDPOINT_REPRODUCTION_TOLERANCE
        ),
        "minimum_singular_witness_matches": (
            minimum_singular_index == targets["minimum_singular_value_wave_index"]
        ),
        "maximum_condition_witness_matches": (
            maximum_condition_index == targets["maximum_condition_number_wave_index"]
        ),
    }
    return {
        "zero_wave_unrestricted_unit_eigenvalue_count": unit_count,
        "maximum_fixed_leaf_eigenvalue_modulus": maximum_radius,
        "maximum_modulus_wave_index": maximum_radius_index,
        "minimum_i_minus_j_singular_value": minimum_singular,
        "minimum_singular_value_wave_index": minimum_singular_index,
        "maximum_i_minus_j_condition_number": maximum_condition,
        "maximum_condition_number_wave_index": maximum_condition_index,
        "absolute_differences_from_q011b": differences,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _checkpoint_audit(
    forward_states: dict[float, Array],
    forward_clusters: dict[float, dict[int, OrderedCluster]],
    basis: Array,
    sealed_input: dict[str, Any],
) -> dict[str, Any]:
    checkpoint_records: list[dict[str, Any]] = []
    for factor in CHECKPOINT_FACTORS:
        state = forward_states[factor]
        clusters = forward_clusters[factor]
        sylvester_records: list[dict[str, Any]] = []
        selected_values: list[ComplexArray] = []
        external_values: list[ComplexArray] = []
        stability_matrices: dict[int, ComplexArray] = {}
        for block_index in range(SIZE):
            active = _active_matrix(state, block_index, basis)
            stability_matrices[block_index] = active
            if block_index in SELECTED_BLOCKS:
                cluster = clusters[block_index]
                separation = _sylvester_separation(cluster)
                sylvester_records.append(
                    {
                        "block_index": block_index,
                        "operator_shape": [
                            cluster.selected_dimension * cluster.excluded_dynamics.shape[0],
                            cluster.selected_dimension * cluster.excluded_dynamics.shape[0],
                        ],
                        "minimum_singular_value": separation,
                        "passed": (separation >= SYLVESTER_SEPARATION_FLOOR),
                    }
                )
                selected_values.append(cluster.selected_eigenvalues)
                external_values.append(cluster.excluded_eigenvalues)
            else:
                external_values.append(linalg.eigvals(active, check_finite=True))
        selected_spectrum = np.concatenate(selected_values)
        external_spectrum = np.concatenate(external_values)
        selected_minimum_modulus = float(np.min(np.abs(selected_spectrum)))
        external_maximum_modulus = float(np.max(np.abs(external_spectrum)))
        normal_gap = selected_minimum_modulus - external_maximum_modulus
        full_spectrum = np.concatenate((selected_spectrum, external_spectrum))
        full_radius = float(np.max(np.abs(full_spectrum)))
        spectral_quotient = float(
            np.log(external_maximum_modulus) / np.log(selected_minimum_modulus)
        )
        record: dict[str, Any] = {
            "amplitude_factor": factor,
            "selected_eigenvalue_count": int(selected_spectrum.size),
            "external_eigenvalue_count": int(external_spectrum.size),
            "full_fixed_leaf_eigenvalue_count": int(full_spectrum.size),
            "selected_spectrum_sha256": _array_sha256(selected_spectrum),
            "external_spectrum_sha256": _array_sha256(external_spectrum),
            "selected_minimum_eigenvalue_modulus": (selected_minimum_modulus),
            "external_maximum_eigenvalue_modulus": (external_maximum_modulus),
            "global_modulus_normal_dominance_gap": normal_gap,
            "full_fixed_leaf_spectral_radius": full_radius,
            "logarithmic_spectral_quotient_diagnostic": (spectral_quotient),
            "sylvester_records": sylvester_records,
            "minimum_sylvester_separation": min(
                item["minimum_singular_value"] for item in sylvester_records
            ),
            "checks": {
                "spectrum_count_is_2598": (full_spectrum.size == SIZE * SIZE * 9 - 3),
                "selected_count_is_24": selected_spectrum.size == 24,
                "external_count_is_2574": (external_spectrum.size == SIZE * SIZE * 9 - 27),
                "all_sylvester_values_are_finite": all(
                    np.isfinite(item["minimum_singular_value"]) for item in sylvester_records
                ),
                "all_spectrum_values_are_finite": bool(np.all(np.isfinite(full_spectrum))),
            },
            "hypothesis_checks": {
                "all_sylvester_separations_above_floor": all(
                    item["passed"] for item in sylvester_records
                ),
                "normal_dominance_gap_above_floor": (normal_gap >= NORMAL_DOMINANCE_GAP_FLOOR),
                "full_fixed_leaf_spectrum_is_stable": (
                    full_radius <= q011b.SPECTRAL_RADIUS_CEILING
                ),
            },
        }
        if factor == 1.0:
            unrestricted_zero = q011b._block_matrix(state, 0.0)
            endpoint = _endpoint_resolvent_audit(
                stability_matrices,
                unrestricted_zero,
                sealed_input["q011b_artifact"]["endpoint_spectrum_targets"],
            )
            radius_target = sealed_input["q011b_artifact"]["endpoint_spectrum_targets"][
                "maximum_fixed_leaf_eigenvalue_modulus"
            ]
            radius_difference = abs(full_radius - radius_target)
            endpoint["full_fixed_leaf_spectral_radius"] = full_radius
            endpoint["spectral_radius_absolute_difference"] = radius_difference
            endpoint["full_spectrum_radius_reproduces"] = (
                radius_difference <= ENDPOINT_REPRODUCTION_TOLERANCE
            )
            endpoint["passed"] = bool(
                endpoint["passed"] and endpoint["full_spectrum_radius_reproduces"]
            )
            record["q011b_endpoint_reproduction"] = endpoint
        checkpoint_records.append(record)

    minimum_sylvester = min(record["minimum_sylvester_separation"] for record in checkpoint_records)
    minimum_normal_gap = min(
        record["global_modulus_normal_dominance_gap"] for record in checkpoint_records
    )
    maximum_full_radius = max(
        record["full_fixed_leaf_spectral_radius"] for record in checkpoint_records
    )
    validity_checks = {
        "checkpoint_factors_are_registered": tuple(
            record["amplitude_factor"] for record in checkpoint_records
        )
        == CHECKPOINT_FACTORS,
        "all_checkpoint_enumerations_are_complete": all(
            all(record["checks"].values()) for record in checkpoint_records
        ),
        "q011b_endpoint_spectrum_reproduces": checkpoint_records[-1]["q011b_endpoint_reproduction"][
            "passed"
        ],
        "all_checkpoint_records_are_finite": bool(_all_numeric_values_finite(checkpoint_records)),
    }
    hypothesis_checks = {
        "all_sylvester_separations_above_floor": (minimum_sylvester >= SYLVESTER_SEPARATION_FLOOR),
        "all_normal_dominance_gaps_above_floor": (minimum_normal_gap >= NORMAL_DOMINANCE_GAP_FLOOR),
        "all_full_fixed_leaf_spectra_are_stable": (
            maximum_full_radius <= q011b.SPECTRAL_RADIUS_CEILING
        ),
    }
    return {
        "checkpoint_factors": list(CHECKPOINT_FACTORS),
        "checkpoint_records": checkpoint_records,
        "minimum_sylvester_separation": minimum_sylvester,
        "minimum_global_modulus_normal_dominance_gap": (minimum_normal_gap),
        "maximum_full_fixed_leaf_spectral_radius": maximum_full_radius,
        "validity_checks": validity_checks,
        "validity_passed": all(validity_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": OMEGA,
        "eta": ETA,
        "endpoint_force_amplitude": q011b.AMPLITUDE,
        "amplitude_factors": list(AMPLITUDE_FACTORS),
        "checkpoint_factors": list(CHECKPOINT_FACTORS),
        "selected_blocks": {
            str(index): {
                "selected_ky_indices": list(SELECTED_BLOCKS[index]),
                "selected_complex_dimension": SELECTED_DIMENSIONS[index],
                "active_dimension": (FIXED_LEAF_DIMENSION if index == 0 else STRIPE_DIMENSION),
            }
            for index in SELECTED_BLOCKS
        },
        "total_selected_complex_dimension": 24,
        "physical_real_dimension_under_conjugacy": 24,
        "fixed_point_protocol": {
            "maximum_newton_steps": q011b.NEWTON_MAXIMUM_STEPS,
            "line_search_factors": list(q011b.LINE_SEARCH_FACTORS),
            "projected_residual_tolerance": (q011b.PROJECTED_RESIDUAL_TOLERANCE),
            "full_residual_tolerance": q011b.FULL_RESIDUAL_TOLERANCE,
            "component_residual_tolerance": (q011b.COMPONENT_RESIDUAL_TOLERANCE),
            "state_distance_tolerance": STATE_DISTANCE_TOLERANCE,
            "nonzero_state_relative_distance_tolerance": (STATE_RELATIVE_DISTANCE_TOLERANCE),
        },
        "cluster_thresholds": {
            "adjacent_principal_angle": ADJACENT_ANGLE_TOLERANCE,
            "reference_alignment": REFERENCE_ALIGNMENT_FLOOR,
            "external_eigenvalue_separation": (EXTERNAL_EIGENVALUE_SEPARATION_FLOOR),
            "projector_norm": PROJECTOR_NORM_CEILING,
            "structural_residual": STRUCTURAL_RESIDUAL_TOLERANCE,
            "reversal_principal_angle": REVERSAL_ANGLE_TOLERANCE,
            "direct_endpoint_principal_angle": (DIRECT_ENDPOINT_ANGLE_TOLERANCE),
            "conjugacy_relative": CONJUGACY_RELATIVE_TOLERANCE,
            "conjugacy_principal_angle": CONJUGACY_ANGLE_TOLERANCE,
            "sylvester_separation": SYLVESTER_SEPARATION_FLOOR,
            "normal_dominance_gap": NORMAL_DOMINANCE_GAP_FLOOR,
            "full_fixed_leaf_spectral_radius": (q011b.SPECTRAL_RADIUS_CEILING),
            "q011b_endpoint_reproduction": (ENDPOINT_REPRODUCTION_TOLERANCE),
        },
        "tracking_rule": (
            "Hungarian nearest eigenvalue-set assignment followed by "
            "nearest selected/excluded ordered complex Schur selection"
        ),
        "individual_mode_labels_at_forced_nodes": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "path_digest_sha256": cycle["path_digest_sha256"],
        "spectrum_digest_sha256": cycle["spectrum_digest_sha256"],
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


def run_forced_spectral_cluster_audit() -> dict[str, Any]:
    """Run the preregistered Q011c forced spectral-cluster gate."""

    registered_parameters = _registered_parameters()
    sealed_input, stored_endpoint = _sealed_input_audit()
    _conservation, basis, basis_audit = q011b._fixed_leaf_basis()
    (
        forward_states,
        backward_states,
        fixed_point_path,
    ) = _fixed_point_path_audit(stored_endpoint, basis)
    (
        reference_bases,
        reference_targets,
        reference_audit,
    ) = _reference_audit(basis)
    forward_clusters, cluster_path = _cluster_path_audit(
        forward_states,
        backward_states,
        basis,
        reference_bases,
        reference_targets,
    )
    checkpoint_audit = _checkpoint_audit(
        forward_states,
        forward_clusters,
        basis,
        sealed_input,
    )

    initial_angle = max(
        record["reference_range_maximum_principal_angle"]
        for record in cluster_path["initial_reproduction_records"]
    )
    initial_spectrum_error = max(
        record["target_spectrum_absolute_hausdorff_error"]
        for record in cluster_path["initial_reproduction_records"]
    )
    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_input_audit": sealed_input,
        "fixed_leaf_basis_audit": basis_audit,
        "unforced_reference_audit": reference_audit,
    }
    path_sections = {
        "fixed_point_path_audit": fixed_point_path,
        "cluster_path_audit": cluster_path,
    }
    spectrum_sections = {
        "checkpoint_spectrum_audit": checkpoint_audit,
    }
    input_digest = _canonical_json_sha256(input_sections)
    path_digest = _canonical_json_sha256(path_sections)
    spectrum_digest = _canonical_json_sha256(spectrum_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **path_sections,
        **spectrum_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == _canonical_json_sha256(input_sections)
        and path_digest == _canonical_json_sha256(path_sections)
        and spectrum_digest == _canonical_json_sha256(spectrum_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )
    initial_reference_reproduces = bool(
        initial_angle <= 1.0e-8 and initial_spectrum_error <= STRUCTURAL_RESIDUAL_TOLERANCE
    )
    validity_gates = {
        "sealed_q011b_and_q006h_inputs_replay": {
            "passed": sealed_input["passed"],
            "threshold": (
                "Q011b artifact, runner, four digests and exact cycle plus "
                "Q006h artifact, selected family and package source reproduce"
            ),
            "value": sealed_input["checks"],
        },
        "registered_fixed_point_amplitude_paths_close": {
            "passed": bool(basis_audit["passed"] and fixed_point_path["passed"]),
            "threshold": (
                "nine forward and backward nodes converge within Q011b "
                "residual thresholds and state agreement gates"
            ),
            "value": {
                "basis_passed": basis_audit["passed"],
                "path_checks": fixed_point_path["checks"],
            },
        },
        "unforced_reference_and_partition_reproduce": {
            "passed": bool(reference_audit["passed"] and initial_reference_reproduces),
            "threshold": (
                "eight first-shell waves times three modes reproduce "
                "6/9/9 ordered ranges with initial angle <=1e-8"
            ),
            "value": {
                "reference_checks": reference_audit["checks"],
                "maximum_initial_reference_angle": initial_angle,
                "maximum_initial_spectrum_error": (initial_spectrum_error),
            },
        },
        "ordered_schur_projector_and_conjugacy_are_structural": {
            "passed": cluster_path["structural_passed"],
            "threshold": (
                "27 ordered selections have registered dimensions, "
                "structural residuals <=1e-10, conjugacy closure, finite data"
            ),
            "value": cluster_path["structural_checks"],
        },
        "checkpoint_spectrum_and_q011b_endpoint_reproduce": {
            "passed": checkpoint_audit["validity_passed"],
            "threshold": (
                "three complete 2598-eigenvalue enumerations and endpoint "
                "radius, unit count and resolvent witnesses reproduce"
            ),
            "value": checkpoint_audit["validity_checks"],
        },
        "finite_strict_json_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "all values finite strict JSON; input, path and spectrum "
                "digests plus runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_provenance_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    cluster_hypotheses = cluster_path["hypothesis_checks"]
    checkpoint_hypotheses = checkpoint_audit["hypothesis_checks"]
    raw_hypotheses = {
        "fixed_point_paths_connect_to_the_same_endpoint": (fixed_point_path["passed"]),
        "twenty_four_dimensional_conjugacy_closed_cluster_continues": bool(
            cluster_hypotheses["adjacent_angles_within_tolerance"]
            and cluster_hypotheses["reference_alignment_above_floor"]
            and cluster_hypotheses["path_reversal_angles_within_tolerance"]
            and cluster_hypotheses["direct_endpoint_angles_within_tolerance"]
            and cluster_hypotheses["conjugacy_closure_passes"]
        ),
        "cluster_remains_separated_and_projector_conditioned": bool(
            cluster_hypotheses["external_eigenvalue_separation_above_floor"]
            and cluster_hypotheses["projector_norm_below_ceiling"]
            and checkpoint_hypotheses["all_sylvester_separations_above_floor"]
        ),
        "global_linear_normal_dominance_and_stability_hold": bool(
            checkpoint_hypotheses["all_normal_dominance_gaps_above_floor"]
            and checkpoint_hypotheses["all_full_fixed_leaf_spectra_are_stable"]
        ),
    }
    hypothesis_gates = {
        "fixed_point_paths_connect_to_the_same_endpoint": {
            "passed": bool(
                validity_passed and raw_hypotheses["fixed_point_paths_connect_to_the_same_endpoint"]
            ),
            "threshold": (
                "forward/backward absolute <=1e-11, nonzero relative "
                "<=1e-8, Q011b endpoint agreement"
            ),
            "value": fixed_point_path["checks"],
        },
        "twenty_four_dimensional_conjugacy_closed_cluster_continues": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["twenty_four_dimensional_conjugacy_closed_cluster_continues"]
            ),
            "threshold": (
                "dimensions 6/9/9, alignment >=0.95, adjacent <=0.05, "
                "reversal/direct/conjugacy angles <=1e-6"
            ),
            "value": {
                key: cluster_hypotheses[key]
                for key in (
                    "adjacent_angles_within_tolerance",
                    "reference_alignment_above_floor",
                    "path_reversal_angles_within_tolerance",
                    "direct_endpoint_angles_within_tolerance",
                    "conjugacy_closure_passes",
                )
            },
        },
        "cluster_remains_separated_and_projector_conditioned": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["cluster_remains_separated_and_projector_conditioned"]
            ),
            "threshold": (
                "external eigenvalue gap >=1e-6, projector norm <=100, "
                "checkpoint Sylvester separation >=1e-5"
            ),
            "value": {
                "minimum_external_eigenvalue_separation": cluster_path["summary"][
                    "minimum_external_eigenvalue_separation"
                ],
                "maximum_projector_two_norm": cluster_path["summary"]["maximum_projector_two_norm"],
                "minimum_sylvester_separation": checkpoint_audit["minimum_sylvester_separation"],
            },
        },
        "global_linear_normal_dominance_and_stability_hold": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["global_linear_normal_dominance_and_stability_hold"]
            ),
            "threshold": (
                "all checkpoint normal gaps >=1e-6 and full fixed-leaf spectral radii <=0.9999"
            ),
            "value": {
                "minimum_normal_gap": checkpoint_audit[
                    "minimum_global_modulus_normal_dominance_gap"
                ],
                "maximum_full_spectral_radius": checkpoint_audit[
                    "maximum_full_fixed_leaf_spectral_radius"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered forced spectral-cluster audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the Q006h first-shell hydrodynamic subspace continues to a "
            "separated linearly normally dominant forced fixed-leaf "
            "spectral cluster"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered first-shell cluster does not remain spectrally separated under forcing"
        )

    cycle: dict[str, Any] = {
        "question": (
            "Does the Q006h first-shell hydrodynamic subspace continue "
            "to the Q011b forced fixed point as a separated, conjugacy-"
            "closed, linearly normally dominant fixed-leaf cluster?"
        ),
        **pre_gate_sections,
        "input_digest_sha256": input_digest,
        "path_digest_sha256": path_digest,
        "spectrum_digest_sha256": spectrum_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = _canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["numerical_consequence"] = {
        "registered_forced_cluster_is_linearly_selected": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_forced_cluster_is_conjugacy_closed": bool(
            validity_passed
            and raw_hypotheses["twenty_four_dimensional_conjugacy_closed_cluster_continues"]
        ),
        "registered_forced_cluster_is_linearly_normally_dominant": bool(
            validity_passed and raw_hypotheses["global_linear_normal_dominance_and_stability_hold"]
        ),
        "individual_forced_modes_are_labeled": False,
        "forced_external_nonresonance_is_certified": False,
        "forced_invariant_manifold_is_constructed": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 nine-node amplitude-continuation "
        "and three-checkpoint linear spectral prequalification on one "
        "17x17 grid. It is not a continuous-parameter theorem, rigorous "
        "projector enclosure, individual forced-mode labeling, external "
        "nonresonance, spectral-quotient smoothness result, forced SSM "
        "existence or uniqueness theorem, quadratic chart, nonlinear normal "
        "attraction, basin, other-grid, other-amplitude, or wall-boundary "
        "result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011b_forced_fixed_point_changed": False,
        "q011a_nonzero_mean_obstruction_changed": False,
        "q006h_unforced_selected_family_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011d for quadratic external nonresonance and the "
        "homological operator on the forced selected cluster."
        if outcome == "accepted"
        else (
            "Localize the first failed path, separation, projector, or "
            "normal-gap gate without changing the sealed amplitude path."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == _canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011c cycle failed strict serialization or digest")
    return cycle


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }


def run_q011c_study() -> dict[str, Any]:
    cycle = run_forced_spectral_cluster_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 forced fixed-leaf ordered-Schur cluster "
                "continuation and linear normal-dominance audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "endpoint_force_amplitude": q011b.AMPLITUDE,
            "amplitude_node_count": len(AMPLITUDE_FACTORS),
            "checkpoint_count": len(CHECKPOINT_FACTORS),
            "selected_complex_dimension": 24,
            "selected_physical_real_dimension": 24,
            "conservation_leaf": ("total mass 289 and total momenta zero"),
            "claim": (
                "finite linear spectral prequalification only; no forced "
                "invariant-manifold or nonlinear-attraction claim"
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
    result = run_q011c_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
