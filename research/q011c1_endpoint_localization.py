"""Sealed Q011c1 conjugacy-orbit endpoint reproducibility localization."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy import linalg

import research.q011b_zero_mean_forced_fixed_point as q011b
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
ORBIT_PARTITION = (
    (0,),
    (1, 16),
    (2, 15),
    (3, 14),
    (4, 13),
    (5, 12),
    (6, 11),
    (7, 10),
    (8, 9),
)
WINNING_RESOLVENT_ORBIT = (1, 16)
WINNING_RADIUS_ORBIT = (0,)

Q011C_ARTIFACT_SHA256 = "dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3"
Q011C_RUNNER_SHA256 = "10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13"
Q011C_INPUT_DIGEST = "7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee"
Q011C_PATH_DIGEST = "06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92"
Q011C_SPECTRUM_DIGEST = "5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c"
Q011C_RESULT_DIGEST = "4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751"
Q011B_STORED_STATE_SHA256 = "612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613"
Q011C_CONTINUED_STATE_SHA256 = "275726b73e03e9d5cb8300b672233f7497abc6b607c1f76c2ef4b176e3788be7"
SEALED_PACKAGE_SOURCE_SHA256 = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"

SVD_STRUCTURAL_TOLERANCE = 1.0e-10
MATRIX_CONJUGACY_TOLERANCE = 1.0e-12
CONTROL_REPRODUCTION_TOLERANCE = 1.0e-12
ROUNDING_PADDING_FACTOR = 64.0


def _orbit_for_index(index: int) -> tuple[int, ...]:
    for orbit in ORBIT_PARTITION:
        if index in orbit:
            return orbit
    raise ValueError(f"wave index {index} is outside the registered orbit partition")


def _sealed_replay_audit() -> tuple[
    dict[str, Any],
    Array,
    Array,
    Array,
    dict[str, Any],
    dict[str, Any],
]:
    artifact_directory = Path(__file__).resolve().parent / "artifacts"
    q011c_artifact_path = artifact_directory / "q011c_forced_spectral_cluster.json"
    q011b_artifact_path = artifact_directory / "q011b_zero_mean_forced_fixed_point.json"
    q011c_runner_path = Path(q011c.__file__).resolve()
    q011c_artifact = json.loads(q011c_artifact_path.read_text(encoding="utf-8"))
    q011b_artifact = json.loads(q011b_artifact_path.read_text(encoding="utf-8"))
    fresh_cycle = q011c.run_forced_spectral_cluster_audit()

    stored_state = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    _conservation, basis, basis_audit = q011b._fixed_leaf_basis()
    forward_states, _backward_states, path_audit = q011c._fixed_point_path_audit(
        stored_state,
        basis,
    )
    continued_state = forward_states[1.0]

    failed_validity = [
        name for name, gate in fresh_cycle["validity_gates"].items() if not gate["passed"]
    ]
    raw_cluster = fresh_cycle["cluster_path_audit"]
    raw_checkpoint = fresh_cycle["checkpoint_spectrum_audit"]
    checks = {
        "q011c_artifact_sha256_matches": (
            _file_sha256(q011c_artifact_path) == Q011C_ARTIFACT_SHA256
        ),
        "q011c_runner_sha256_matches": (_file_sha256(q011c_runner_path) == Q011C_RUNNER_SHA256),
        "q011c_cycle_replays_exactly": q011c_artifact["cycle"] == fresh_cycle,
        "q011c_digests_match": (
            fresh_cycle["input_digest_sha256"] == Q011C_INPUT_DIGEST
            and fresh_cycle["path_digest_sha256"] == Q011C_PATH_DIGEST
            and fresh_cycle["spectrum_digest_sha256"] == Q011C_SPECTRUM_DIGEST
            and fresh_cycle["result_digest_sha256"] == Q011C_RESULT_DIGEST
        ),
        "q011c_registered_inconclusive_outcome_reproduces": (
            fresh_cycle["study_validity"] == "failed"
            and fresh_cycle["hypothesis_outcome"] == "inconclusive"
            and fresh_cycle["scientific_classification"]
            == "registered forced spectral-cluster audit is invalid"
            and failed_validity == ["checkpoint_spectrum_and_q011b_endpoint_reproduce"]
        ),
        "q011c_raw_scientific_diagnostics_reproduce": (
            fresh_cycle["fixed_point_path_audit"]["passed"]
            and raw_cluster["structural_passed"]
            and raw_cluster["hypothesis_passed"]
            and raw_checkpoint["hypothesis_passed"]
            and all(raw_cluster["hypothesis_checks"].values())
            and all(raw_checkpoint["hypothesis_checks"].values())
        ),
        "fixed_leaf_basis_reproduces": (
            basis_audit == fresh_cycle["fixed_leaf_basis_audit"] and basis_audit["passed"]
        ),
        "fixed_point_path_reconstructs_exactly": (
            path_audit == fresh_cycle["fixed_point_path_audit"]
        ),
        "stored_state_sha256_matches": (
            q011c._array_sha256(stored_state) == Q011B_STORED_STATE_SHA256
        ),
        "continued_state_sha256_matches": (
            q011c._array_sha256(continued_state) == Q011C_CONTINUED_STATE_SHA256
        ),
        "package_source_sha256_matches": (
            source_metadata()["package_source_sha256"] == SEALED_PACKAGE_SOURCE_SHA256
        ),
    }
    audit = {
        "q011c_artifact": {
            "filename": q011c_artifact_path.name,
            "sha256": _file_sha256(q011c_artifact_path),
            "runner_filename": q011c_runner_path.name,
            "runner_sha256": _file_sha256(q011c_runner_path),
            "input_digest_sha256": fresh_cycle["input_digest_sha256"],
            "path_digest_sha256": fresh_cycle["path_digest_sha256"],
            "spectrum_digest_sha256": fresh_cycle["spectrum_digest_sha256"],
            "result_digest_sha256": fresh_cycle["result_digest_sha256"],
            "failed_validity_gates": failed_validity,
            "study_validity": fresh_cycle["study_validity"],
            "hypothesis_outcome": fresh_cycle["hypothesis_outcome"],
            "scientific_classification": fresh_cycle["scientific_classification"],
        },
        "q011b_artifact": {
            "filename": q011b_artifact_path.name,
            "sha256": _file_sha256(q011b_artifact_path),
            "stored_state_sha256": q011c._array_sha256(stored_state),
        },
        "continued_state_sha256": q011c._array_sha256(continued_state),
        "endpoint_population_l2_distance": path_audit["endpoint_population_l2_distance"],
        "endpoint_relative_distance": path_audit["endpoint_relative_distance"],
        "raw_q011c_diagnostics": {
            "fixed_point_path_passed": fresh_cycle["fixed_point_path_audit"]["passed"],
            "cluster_structural_passed": raw_cluster["structural_passed"],
            "cluster_hypothesis_passed": raw_cluster["hypothesis_passed"],
            "checkpoint_hypothesis_passed": raw_checkpoint["hypothesis_passed"],
            "cluster_hypothesis_checks": raw_cluster["hypothesis_checks"],
            "checkpoint_hypothesis_checks": raw_checkpoint["hypothesis_checks"],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        stored_state,
        continued_state,
        basis,
        q011c_artifact,
        q011b_artifact,
    )


def _svd_block_record(
    state: Array,
    block_index: int,
    basis: Array,
) -> tuple[dict[str, Any], ComplexArray, ComplexArray]:
    matrix = q011c._active_matrix(state, block_index, basis)
    resolvent = np.eye(matrix.shape[0], dtype=np.complex128) - matrix
    left, singular_values, right_adjoint = linalg.svd(
        resolvent,
        full_matrices=True,
        compute_uv=True,
        overwrite_a=False,
        check_finite=True,
        lapack_driver="gesdd",
    )
    reconstructed = (left * singular_values[None, :]) @ right_adjoint
    scale = max(float(np.linalg.norm(resolvent)), np.finfo(float).tiny)
    reconstruction = float(np.linalg.norm(reconstructed - resolvent) / scale)
    left_unitarity = float(
        np.linalg.norm(
            left.conj().T @ left - np.eye(left.shape[1], dtype=np.complex128),
        )
    )
    right_unitarity = float(
        np.linalg.norm(
            right_adjoint @ right_adjoint.conj().T
            - np.eye(right_adjoint.shape[0], dtype=np.complex128),
        )
    )
    eigenvalues = linalg.eigvals(matrix, check_finite=True)
    minimum = float(singular_values[-1])
    maximum = float(singular_values[0])
    condition = float(maximum / minimum)
    metrics = {
        "spectral_radius": float(np.max(np.abs(eigenvalues))),
        "minimum_singular_value": minimum,
        "maximum_singular_value": maximum,
        "condition_number": condition,
    }
    record = {
        "block_index": block_index,
        "active_dimension": int(matrix.shape[0]),
        "matrix_sha256": q011c._array_sha256(matrix),
        "resolvent_sha256": q011c._array_sha256(resolvent),
        "singular_spectrum_sha256": q011c._array_sha256(singular_values),
        "metrics_sha256": q011c._canonical_json_sha256(metrics),
        **metrics,
        "resolvent_frobenius_norm": float(np.linalg.norm(resolvent)),
        "svd_reconstruction_relative_residual": reconstruction,
        "left_unitarity_frobenius_residual": left_unitarity,
        "right_unitarity_frobenius_residual": right_unitarity,
        "structural_passed": bool(
            reconstruction <= SVD_STRUCTURAL_TOLERANCE
            and left_unitarity <= SVD_STRUCTURAL_TOLERANCE
            and right_unitarity <= SVD_STRUCTURAL_TOLERANCE
        ),
    }
    return record, matrix, resolvent


def _endpoint_block_audit(
    name: str,
    state: Array,
    basis: Array,
) -> tuple[
    dict[str, Any],
    dict[int, ComplexArray],
    dict[int, ComplexArray],
]:
    records: list[dict[str, Any]] = []
    matrices: dict[int, ComplexArray] = {}
    resolvents: dict[int, ComplexArray] = {}
    for block_index in range(SIZE):
        record, matrix, resolvent = _svd_block_record(
            state,
            block_index,
            basis,
        )
        records.append(record)
        matrices[block_index] = matrix
        resolvents[block_index] = resolvent

    radius_witness = max(records, key=lambda record: record["spectral_radius"])
    minimum_witness = min(
        records,
        key=lambda record: record["minimum_singular_value"],
    )
    condition_witness = max(
        records,
        key=lambda record: record["condition_number"],
    )
    maximum_reconstruction = max(
        record["svd_reconstruction_relative_residual"] for record in records
    )
    maximum_unitarity = max(
        max(
            record["left_unitarity_frobenius_residual"],
            record["right_unitarity_frobenius_residual"],
        )
        for record in records
    )
    checks = {
        "block_count_is_seventeen": len(records) == SIZE,
        "active_dimensions_are_registered": all(
            record["active_dimension"]
            == (
                q011c.FIXED_LEAF_DIMENSION if record["block_index"] == 0 else q011c.STRIPE_DIMENSION
            )
            for record in records
        ),
        "all_svd_structural_checks_pass": all(record["structural_passed"] for record in records),
        "all_values_are_finite": bool(_all_numeric_values_finite(records)),
    }
    return (
        {
            "endpoint": name,
            "state_sha256": q011c._array_sha256(state),
            "block_records": records,
            "maximum_svd_reconstruction_relative_residual": maximum_reconstruction,
            "maximum_svd_unitarity_frobenius_residual": maximum_unitarity,
            "spectral_radius": radius_witness["spectral_radius"],
            "spectral_radius_witness_index": radius_witness["block_index"],
            "minimum_singular_value": minimum_witness["minimum_singular_value"],
            "minimum_singular_witness_index": minimum_witness["block_index"],
            "maximum_condition_number": condition_witness["condition_number"],
            "maximum_condition_witness_index": condition_witness["block_index"],
            "checks": checks,
            "passed": all(checks.values()),
        },
        matrices,
        resolvents,
    )


def _matrix_conjugacy_audit(
    endpoint_name: str,
    matrices: dict[int, ComplexArray],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for positive in range(1, SIZE // 2 + 1):
        negative = SIZE - positive
        left = matrices[positive]
        right = np.conjugate(matrices[negative])
        relative = float(
            np.linalg.norm(left - right) / max(float(np.linalg.norm(left)), np.finfo(float).tiny)
        )
        records.append(
            {
                "orbit": [positive, negative],
                "matrix_conjugacy_relative_frobenius_residual": relative,
                "passed": relative <= MATRIX_CONJUGACY_TOLERANCE,
            }
        )
    checks = {
        "registered_nonzero_orbit_count_is_eight": len(records) == 8,
        "all_matrix_conjugacy_residuals_pass": all(record["passed"] for record in records),
        "all_values_are_finite": bool(_all_numeric_values_finite(records)),
    }
    return {
        "endpoint": endpoint_name,
        "records": records,
        "maximum_matrix_conjugacy_relative_frobenius_residual": max(
            record["matrix_conjugacy_relative_frobenius_residual"] for record in records
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _endpoint_control_audit(
    stored_state: Array,
    continued_state: Array,
    basis: Array,
    stored_matrices: dict[int, ComplexArray],
    continued_matrices: dict[int, ComplexArray],
    q011c_artifact: dict[str, Any],
    q011b_artifact: dict[str, Any],
) -> dict[str, Any]:
    q011b_spectrum = q011b_artifact["cycle"]["spectrum_audit"]
    targets = {
        "zero_wave_unrestricted_unit_eigenvalue_count": q011b_spectrum[
            "zero_wave_unrestricted_unit_eigenvalue_count"
        ],
        "maximum_fixed_leaf_eigenvalue_modulus": q011b_spectrum[
            "maximum_fixed_leaf_eigenvalue_modulus"
        ],
        "maximum_modulus_wave_index": q011b_spectrum["maximum_modulus_wave_index"],
        "minimum_i_minus_j_singular_value": q011b_spectrum["minimum_i_minus_j_singular_value"],
        "minimum_singular_value_wave_index": q011b_spectrum["minimum_singular_value_wave_index"],
        "maximum_i_minus_j_condition_number": q011b_spectrum["maximum_i_minus_j_condition_number"],
        "maximum_condition_number_wave_index": q011b_spectrum[
            "maximum_condition_number_wave_index"
        ],
    }
    stored_control = q011c._endpoint_resolvent_audit(
        stored_matrices,
        q011b._block_matrix(stored_state, 0.0),
        targets,
    )
    continued_control = q011c._endpoint_resolvent_audit(
        continued_matrices,
        q011b._block_matrix(continued_state, 0.0),
        targets,
    )
    artifact_control = q011c_artifact["cycle"]["checkpoint_spectrum_audit"]["checkpoint_records"][
        -1
    ]["q011b_endpoint_reproduction"]
    shared_keys = tuple(continued_control)
    artifact_subset = {key: artifact_control[key] for key in shared_keys}
    stored_witnesses = {
        "spectral_radius": stored_control["maximum_modulus_wave_index"],
        "minimum_singular_value": stored_control["minimum_singular_value_wave_index"],
        "maximum_condition_number": stored_control["maximum_condition_number_wave_index"],
    }
    continued_witnesses = {
        "spectral_radius": continued_control["maximum_modulus_wave_index"],
        "minimum_singular_value": continued_control["minimum_singular_value_wave_index"],
        "maximum_condition_number": continued_control["maximum_condition_number_wave_index"],
    }
    checks = {
        "stored_q011b_control_passes_original_tolerance": stored_control["passed"],
        "stored_original_witness_indices_reproduce": (
            stored_witnesses
            == {
                "spectral_radius": 0,
                "minimum_singular_value": 16,
                "maximum_condition_number": 16,
            }
        ),
        "continued_control_reproduces_q011c_exactly": (continued_control == artifact_subset),
        "continued_original_failure_reproduces": (
            not continued_control["passed"]
            and continued_control["checks"]["spectral_radius_reproduces"]
            and continued_control["checks"]["minimum_singular_value_reproduces"]
            and not continued_control["checks"]["maximum_condition_number_reproduces"]
            and not continued_control["checks"]["minimum_singular_witness_matches"]
            and not continued_control["checks"]["maximum_condition_witness_matches"]
        ),
        "all_values_are_finite": bool(
            _all_numeric_values_finite(stored_control)
            and _all_numeric_values_finite(continued_control)
        ),
    }
    return {
        "control_reproduction_tolerance": CONTROL_REPRODUCTION_TOLERANCE,
        "q011b_targets": targets,
        "stored_endpoint_control": stored_control,
        "continued_endpoint_control": continued_control,
        "stored_witness_indices": stored_witnesses,
        "continued_witness_indices": continued_witnesses,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _record_by_index(endpoint_audit: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(record["block_index"]): record for record in endpoint_audit["block_records"]}


def _perturbation_enclosure_audit(
    stored_audit: dict[str, Any],
    continued_audit: dict[str, Any],
    stored_resolvents: dict[int, ComplexArray],
    continued_resolvents: dict[int, ComplexArray],
    control_audit: dict[str, Any],
    raw_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    stored_records = _record_by_index(stored_audit)
    continued_records = _record_by_index(continued_audit)
    block_records: list[dict[str, Any]] = []
    for block_index in range(SIZE):
        stored = stored_records[block_index]
        continued = continued_records[block_index]
        stored_matrix = stored_resolvents[block_index]
        continued_matrix = continued_resolvents[block_index]
        rounding_padding = float(
            ROUNDING_PADDING_FACTOR
            * np.finfo(float).eps
            * max(
                1.0,
                float(np.linalg.norm(stored_matrix)),
                float(np.linalg.norm(continued_matrix)),
            )
        )
        perturbation_frobenius = float(np.linalg.norm(continued_matrix - stored_matrix))
        bound = perturbation_frobenius + rounding_padding
        stored_minimum = stored["minimum_singular_value"]
        stored_maximum = stored["maximum_singular_value"]
        minimum_interval = [
            max(0.0, stored_minimum - bound),
            stored_minimum + bound,
        ]
        maximum_interval = [
            max(0.0, stored_maximum - bound),
            stored_maximum + bound,
        ]
        denominator_positive = stored_minimum > bound
        if denominator_positive:
            condition_interval = [
                maximum_interval[0] / minimum_interval[1],
                maximum_interval[1] / minimum_interval[0],
            ]
        else:
            condition_interval = [0.0, float(np.finfo(float).max)]
        minimum_passed = (
            minimum_interval[0] <= continued["minimum_singular_value"] <= minimum_interval[1]
        )
        maximum_passed = (
            maximum_interval[0] <= continued["maximum_singular_value"] <= maximum_interval[1]
        )
        condition_passed = (
            condition_interval[0] <= continued["condition_number"] <= condition_interval[1]
        )
        block_records.append(
            {
                "block_index": block_index,
                "resolvent_difference_frobenius_norm": perturbation_frobenius,
                "rounding_padding": rounding_padding,
                "registered_perturbation_bound": bound,
                "stored_minimum_singular_value": stored_minimum,
                "continued_minimum_singular_value": continued["minimum_singular_value"],
                "minimum_singular_interval": minimum_interval,
                "stored_maximum_singular_value": stored_maximum,
                "continued_maximum_singular_value": continued["maximum_singular_value"],
                "maximum_singular_interval": maximum_interval,
                "stored_condition_number": stored["condition_number"],
                "continued_condition_number": continued["condition_number"],
                "condition_interval": condition_interval,
                "minimum_singular_change_utilization": (
                    abs(continued["minimum_singular_value"] - stored_minimum) / bound
                ),
                "maximum_singular_change_utilization": (
                    abs(continued["maximum_singular_value"] - stored_maximum) / bound
                ),
                "checks": {
                    "denominator_remains_positive": denominator_positive,
                    "minimum_singular_value_is_enclosed": minimum_passed,
                    "maximum_singular_value_is_enclosed": maximum_passed,
                    "condition_number_is_enclosed": condition_passed,
                },
                "passed": bool(
                    denominator_positive and minimum_passed and maximum_passed and condition_passed
                ),
            }
        )

    block_map = {record["block_index"]: record for record in block_records}
    winner_minimum_upper = min(
        block_map[index]["minimum_singular_interval"][1] for index in WINNING_RESOLVENT_ORBIT
    )
    external_minimum_lower = min(
        block_map[index]["minimum_singular_interval"][0]
        for index in range(SIZE)
        if index not in WINNING_RESOLVENT_ORBIT
    )
    minimum_orbit_margin = external_minimum_lower - winner_minimum_upper
    winner_condition_lower = max(
        block_map[index]["condition_interval"][0] for index in WINNING_RESOLVENT_ORBIT
    )
    external_condition_upper = max(
        block_map[index]["condition_interval"][1]
        for index in range(SIZE)
        if index not in WINNING_RESOLVENT_ORBIT
    )
    condition_orbit_margin = winner_condition_lower - external_condition_upper

    stored_orbits = {
        "spectral_radius": list(_orbit_for_index(stored_audit["spectral_radius_witness_index"])),
        "minimum_singular_value": list(
            _orbit_for_index(stored_audit["minimum_singular_witness_index"])
        ),
        "maximum_condition_number": list(
            _orbit_for_index(stored_audit["maximum_condition_witness_index"])
        ),
    }
    continued_orbits = {
        "spectral_radius": list(_orbit_for_index(continued_audit["spectral_radius_witness_index"])),
        "minimum_singular_value": list(
            _orbit_for_index(continued_audit["minimum_singular_witness_index"])
        ),
        "maximum_condition_number": list(
            _orbit_for_index(continued_audit["maximum_condition_witness_index"])
        ),
    }
    stored_control_witnesses = control_audit["stored_witness_indices"]
    continued_control_witnesses = control_audit["continued_witness_indices"]
    exact_exchange = {
        "stored_minimum_singular_witness": stored_control_witnesses["minimum_singular_value"],
        "continued_minimum_singular_witness": continued_control_witnesses["minimum_singular_value"],
        "stored_maximum_condition_witness": stored_control_witnesses["maximum_condition_number"],
        "continued_maximum_condition_witness": continued_control_witnesses[
            "maximum_condition_number"
        ],
    }
    all_enclosed = all(record["passed"] for record in block_records)
    orbit_identity = bool(
        stored_orbits["spectral_radius"] == list(WINNING_RADIUS_ORBIT)
        and continued_orbits["spectral_radius"] == list(WINNING_RADIUS_ORBIT)
        and stored_orbits["minimum_singular_value"] == list(WINNING_RESOLVENT_ORBIT)
        and continued_orbits["minimum_singular_value"] == list(WINNING_RESOLVENT_ORBIT)
        and stored_orbits["maximum_condition_number"] == list(WINNING_RESOLVENT_ORBIT)
        and continued_orbits["maximum_condition_number"] == list(WINNING_RESOLVENT_ORBIT)
    )
    orbit_separation = bool(minimum_orbit_margin > 0.0 and condition_orbit_margin > 0.0)
    exchange_is_registered = exact_exchange == {
        "stored_minimum_singular_witness": 16,
        "continued_minimum_singular_witness": 1,
        "stored_maximum_condition_witness": 16,
        "continued_maximum_condition_witness": 1,
    }
    raw_q011c_checks_pass = bool(
        raw_diagnostics["fixed_point_path_passed"]
        and raw_diagnostics["cluster_structural_passed"]
        and raw_diagnostics["cluster_hypothesis_passed"]
        and raw_diagnostics["checkpoint_hypothesis_passed"]
        and all(raw_diagnostics["cluster_hypothesis_checks"].values())
        and all(raw_diagnostics["checkpoint_hypothesis_checks"].values())
    )
    checks = {
        "all_block_metric_changes_are_enclosed": all_enclosed,
        "registered_extremal_orbits_are_stable": orbit_identity,
        "winning_resolvent_orbit_is_interval_separated": orbit_separation,
        "exact_witness_exchange_is_inside_registered_orbit": exchange_is_registered,
        "raw_q011c_scientific_diagnostics_remain_true": raw_q011c_checks_pass,
        "all_values_are_finite": bool(_all_numeric_values_finite(block_records)),
    }
    return {
        "rounding_padding_factor": ROUNDING_PADDING_FACTOR,
        "machine_epsilon": float(np.finfo(float).eps),
        "block_records": block_records,
        "maximum_resolvent_difference_frobenius_norm": max(
            record["resolvent_difference_frobenius_norm"] for record in block_records
        ),
        "maximum_registered_perturbation_bound": max(
            record["registered_perturbation_bound"] for record in block_records
        ),
        "maximum_minimum_singular_change_utilization": max(
            record["minimum_singular_change_utilization"] for record in block_records
        ),
        "maximum_maximum_singular_change_utilization": max(
            record["maximum_singular_change_utilization"] for record in block_records
        ),
        "stored_extremal_orbits": stored_orbits,
        "continued_extremal_orbits": continued_orbits,
        "minimum_singular_winning_orbit_interval_upper": winner_minimum_upper,
        "minimum_singular_external_orbit_interval_lower": external_minimum_lower,
        "minimum_singular_orbit_separation_margin": minimum_orbit_margin,
        "maximum_condition_winning_orbit_interval_lower": winner_condition_lower,
        "maximum_condition_external_orbit_interval_upper": external_condition_upper,
        "maximum_condition_orbit_separation_margin": condition_orbit_margin,
        "exact_control_witness_exchange": exact_exchange,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011c.OMEGA,
        "eta": q011c.ETA,
        "conservation_leaf": "total mass 289 and total momenta zero",
        "endpoint_names": ["q011b_stored", "q011c_forward_continued"],
        "orbit_partition": [list(orbit) for orbit in ORBIT_PARTITION],
        "winning_radius_orbit": list(WINNING_RADIUS_ORBIT),
        "winning_resolvent_orbit": list(WINNING_RESOLVENT_ORBIT),
        "svd_structural_tolerance": SVD_STRUCTURAL_TOLERANCE,
        "matrix_conjugacy_tolerance": MATRIX_CONJUGACY_TOLERANCE,
        "stored_control_reproduction_tolerance": CONTROL_REPRODUCTION_TOLERANCE,
        "rounding_padding_factor": ROUNDING_PADDING_FACTOR,
        "perturbation_norm": ("resolvent Frobenius difference plus registered binary64 padding"),
        "q011c_is_regraded": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "metric_digest_sha256": cycle["metric_digest_sha256"],
        "enclosure_digest_sha256": cycle["enclosure_digest_sha256"],
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


def run_endpoint_localization_audit() -> dict[str, Any]:
    """Run the preregistered Q011c1 endpoint-localization gate."""

    registered_parameters = _registered_parameters()
    (
        sealed_replay,
        stored_state,
        continued_state,
        basis,
        q011c_artifact,
        q011b_artifact,
    ) = _sealed_replay_audit()
    (
        stored_block_audit,
        stored_matrices,
        stored_resolvents,
    ) = _endpoint_block_audit("q011b_stored", stored_state, basis)
    (
        continued_block_audit,
        continued_matrices,
        continued_resolvents,
    ) = _endpoint_block_audit("q011c_forward_continued", continued_state, basis)
    stored_conjugacy = _matrix_conjugacy_audit(
        "q011b_stored",
        stored_matrices,
    )
    continued_conjugacy = _matrix_conjugacy_audit(
        "q011c_forward_continued",
        continued_matrices,
    )
    control_audit = _endpoint_control_audit(
        stored_state,
        continued_state,
        basis,
        stored_matrices,
        continued_matrices,
        q011c_artifact,
        q011b_artifact,
    )
    enclosure_audit = _perturbation_enclosure_audit(
        stored_block_audit,
        continued_block_audit,
        stored_resolvents,
        continued_resolvents,
        control_audit,
        sealed_replay["raw_q011c_diagnostics"],
    )

    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_replay_audit": sealed_replay,
    }
    metric_sections = {
        "stored_endpoint_block_audit": stored_block_audit,
        "continued_endpoint_block_audit": continued_block_audit,
        "stored_matrix_conjugacy_audit": stored_conjugacy,
        "continued_matrix_conjugacy_audit": continued_conjugacy,
        "endpoint_control_audit": control_audit,
    }
    enclosure_sections = {
        "perturbation_enclosure_audit": enclosure_audit,
    }
    input_digest = q011c._canonical_json_sha256(input_sections)
    metric_digest = q011c._canonical_json_sha256(metric_sections)
    enclosure_digest = q011c._canonical_json_sha256(enclosure_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **metric_sections,
        **enclosure_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011c._canonical_json_sha256(input_sections)
        and metric_digest == q011c._canonical_json_sha256(metric_sections)
        and enclosure_digest == q011c._canonical_json_sha256(enclosure_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )

    block_structural = bool(
        stored_block_audit["passed"]
        and continued_block_audit["passed"]
        and stored_conjugacy["passed"]
        and continued_conjugacy["passed"]
    )
    state_reconstruction = bool(
        sealed_replay["checks"]["stored_state_sha256_matches"]
        and sealed_replay["checks"]["continued_state_sha256_matches"]
        and sealed_replay["checks"]["fixed_point_path_reconstructs_exactly"]
        and control_audit["checks"]["continued_control_reproduces_q011c_exactly"]
        and control_audit["checks"]["continued_original_failure_reproduces"]
    )
    validity_gates = {
        "sealed_q011c_and_q011b_inputs_replay": {
            "passed": sealed_replay["passed"],
            "threshold": (
                "Q011c artifact, runner, four digests and exact cycle plus "
                "Q011b endpoint and package source reproduce"
            ),
            "value": sealed_replay["checks"],
        },
        "stored_and_continued_endpoint_states_reconstruct": {
            "passed": state_reconstruction,
            "threshold": (
                "sealed state hashes, exact Q011c path and original endpoint "
                "failure record reproduce"
            ),
            "value": {
                "stored_state_sha256": sealed_replay["q011b_artifact"]["stored_state_sha256"],
                "continued_state_sha256": sealed_replay["continued_state_sha256"],
                "endpoint_population_l2_distance": sealed_replay["endpoint_population_l2_distance"],
                "endpoint_relative_distance": sealed_replay["endpoint_relative_distance"],
                "control_checks": control_audit["checks"],
            },
        },
        "all_block_svds_and_conjugacy_are_structural": {
            "passed": block_structural,
            "threshold": (
                "34 full SVDs have registered dimensions, reconstruction "
                "and unitarity <=1e-10; conjugacy residuals <=1e-12"
            ),
            "value": {
                "stored_checks": stored_block_audit["checks"],
                "continued_checks": continued_block_audit["checks"],
                "stored_conjugacy_checks": stored_conjugacy["checks"],
                "continued_conjugacy_checks": continued_conjugacy["checks"],
            },
        },
        "stored_q011b_endpoint_control_reproduces": {
            "passed": bool(
                control_audit["checks"]["stored_q011b_control_passes_original_tolerance"]
                and control_audit["checks"]["stored_original_witness_indices_reproduce"]
            ),
            "threshold": (
                "stored Q011b radius, unit count and resolvent metrics "
                "reproduce within the original absolute 1e-12 tolerance"
            ),
            "value": control_audit["stored_endpoint_control"],
        },
        "finite_strict_json_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "all values finite strict JSON; input, metric and enclosure "
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

    enclosure_checks = enclosure_audit["checks"]
    raw_hypotheses = {
        "all_block_metric_changes_are_perturbation_enclosed": enclosure_checks[
            "all_block_metric_changes_are_enclosed"
        ],
        "registered_extremal_conjugacy_orbits_are_stable": enclosure_checks[
            "registered_extremal_orbits_are_stable"
        ],
        "winning_resolvent_orbit_is_interval_separated": enclosure_checks[
            "winning_resolvent_orbit_is_interval_separated"
        ],
        "witness_exchange_is_local_and_raw_q011c_checks_remain_true": bool(
            enclosure_checks["exact_witness_exchange_is_inside_registered_orbit"]
            and enclosure_checks["raw_q011c_scientific_diagnostics_remain_true"]
        ),
    }
    hypothesis_gates = {
        name: {
            "passed": bool(validity_passed and passed),
            "threshold": {
                "all_block_metric_changes_are_perturbation_enclosed": (
                    "all 17 continued m, M and kappa values lie in the "
                    "registered Frobenius-Weyl intervals"
                ),
                "registered_extremal_conjugacy_orbits_are_stable": (
                    "radius orbit {0}; minimum-singular and "
                    "maximum-condition orbit {1,16} at both endpoints"
                ),
                "winning_resolvent_orbit_is_interval_separated": (
                    "winning minimum-singular upper is below every external "
                    "lower and winning condition lower is above every external upper"
                ),
                "witness_exchange_is_local_and_raw_q011c_checks_remain_true": (
                    "exact 16-to-1 exchange remains in {1,16} and all raw "
                    "Q011c cluster/checkpoint diagnostics remain true"
                ),
            }[name],
            "value": {
                "all_block_metric_changes_are_perturbation_enclosed": {
                    "maximum_perturbation_bound": enclosure_audit[
                        "maximum_registered_perturbation_bound"
                    ],
                    "maximum_minimum_singular_change_utilization": enclosure_audit[
                        "maximum_minimum_singular_change_utilization"
                    ],
                    "maximum_maximum_singular_change_utilization": enclosure_audit[
                        "maximum_maximum_singular_change_utilization"
                    ],
                },
                "registered_extremal_conjugacy_orbits_are_stable": {
                    "stored": enclosure_audit["stored_extremal_orbits"],
                    "continued": enclosure_audit["continued_extremal_orbits"],
                },
                "winning_resolvent_orbit_is_interval_separated": {
                    "minimum_singular_margin": enclosure_audit[
                        "minimum_singular_orbit_separation_margin"
                    ],
                    "maximum_condition_margin": enclosure_audit[
                        "maximum_condition_orbit_separation_margin"
                    ],
                },
                "witness_exchange_is_local_and_raw_q011c_checks_remain_true": {
                    "exchange": enclosure_audit["exact_control_witness_exchange"],
                    "raw_diagnostics": sealed_replay["raw_q011c_diagnostics"],
                },
            }[name],
        }
        for name, passed in raw_hypotheses.items()
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011c endpoint-localization audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the Q011c endpoint failure is localized to perturbation-"
            "consistent conjugate-witness tie instability"
        )
    else:
        outcome = "rejected"
        classification = (
            "the Q011c endpoint discrepancy is not explained by conjugate-witness tie instability"
        )

    cycle: dict[str, Any] = {
        "question": (
            "Is the sole Q011c endpoint-reproduction failure explained by "
            "a perturbation-consistent witness exchange inside the "
            "conjugacy orbit {1,16}?"
        ),
        **pre_gate_sections,
        "input_digest_sha256": input_digest,
        "metric_digest_sha256": metric_digest,
        "enclosure_digest_sha256": enclosure_digest,
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
        "q011c_endpoint_failure_is_localized": bool(validity_passed and hypotheses_passed),
        "q011c_cluster_is_regraded_as_accepted": False,
        "forced_spectral_cluster_is_selected": False,
        "forced_external_nonresonance_is_certified": False,
        "forced_invariant_manifold_is_constructed": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result localizes one binary64 endpoint-reproduction "
        "failure using the same two states, 17 fixed-leaf blocks, "
        "conjugacy-orbit semantics and conservative Frobenius-Weyl "
        "intervals. It does not regrade Q011c, provide rigorous SVD "
        "enclosures, select a forced spectral cluster, label individual "
        "forced modes, prove continuous-amplitude continuation, external "
        "nonresonance, invariant-manifold existence, normal attraction, "
        "other-grid behavior or wall-boundary behavior."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011c_inconclusive_outcome_changed": False,
        "q011b_accepted_fixed_point_changed": False,
        "q011a_nonzero_mean_obstruction_changed": False,
        "q006h_unforced_selected_family_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011c2 with conjugacy-orbit endpoint semantics and "
        "held-out force-amplitude nodes."
        if outcome == "accepted"
        else (
            "Decompose the endpoint Jacobian discrepancy by block and "
            "state component without proceeding to Q011d."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011c1 cycle failed strict serialization or digest")
    return cycle


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def run_q011c1_study() -> dict[str, Any]:
    cycle = run_endpoint_localization_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 conjugacy-orbit endpoint reproducibility "
                "localization with Frobenius-Weyl perturbation intervals"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011c.OMEGA,
            "eta": q011c.ETA,
            "endpoint_count": 2,
            "fixed_leaf_block_count_per_endpoint": SIZE,
            "conjugacy_orbit_count": len(ORBIT_PARTITION),
            "q011c_is_regraded": False,
            "claim": (
                "failure localization only; no forced spectral-cluster "
                "selection or invariant-manifold claim"
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
    result = run_q011c1_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
