"""Sealed Q011c2 held-out forced spectral-cluster reissue."""

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
import research.q011c1_endpoint_localization as q011c1
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
FINE_FACTORS = tuple(index / 16.0 for index in range(17))
TRAINING_FACTORS = q011c.AMPLITUDE_FACTORS
HELDOUT_FACTORS = tuple((2 * index + 1) / 16.0 for index in range(8))

Q011C1_ARTIFACT_SHA256 = "939baa85fa4db1efaf701985d81665f863e5f77f6ec2c95cfc2bacf004c0c45c"
Q011C1_RUNNER_SHA256 = "1f777dc50c6748cb8d8a64d643822b55733ac247b5de7d08b119d628b63c52a6"
Q011C1_INPUT_DIGEST = "e9ea01348fe839dd745c3ccb7cf2e622bec3c0a4f080a1ab1c62a92a02ced064"
Q011C1_METRIC_DIGEST = "fca5a81f3fc47e24a6f17578065adb527d892400d5d88c8eb18cf7089e234a9e"
Q011C1_ENCLOSURE_DIGEST = "7a6cd761f88b328c2ffa74de5b9fb7952f454b86a99630d6266973e8fa6fea20"
Q011C1_RESULT_DIGEST = "ad8b47548ebc04595246301864314502158e686520197377b3a33d30db1d4f86"
Q011C_ARTIFACT_SHA256 = q011c1.Q011C_ARTIFACT_SHA256
Q011C_RUNNER_SHA256 = q011c1.Q011C_RUNNER_SHA256
Q011C_INPUT_DIGEST = q011c1.Q011C_INPUT_DIGEST
Q011C_PATH_DIGEST = q011c1.Q011C_PATH_DIGEST
Q011C_SPECTRUM_DIGEST = q011c1.Q011C_SPECTRUM_DIGEST
Q011C_RESULT_DIGEST = q011c1.Q011C_RESULT_DIGEST
Q011B_STORED_STATE_SHA256 = q011c1.Q011B_STORED_STATE_SHA256
SEALED_PACKAGE_SOURCE_SHA256 = q011c1.SEALED_PACKAGE_SOURCE_SHA256

STATE_DISTANCE_TOLERANCE = q011c.STATE_DISTANCE_TOLERANCE
STATE_RELATIVE_DISTANCE_TOLERANCE = q011c.STATE_RELATIVE_DISTANCE_TOLERANCE
TRAINING_CLUSTER_ANGLE_TOLERANCE = 1.0e-6
TRAINING_SPECTRUM_TOLERANCE = 1.0e-10
CANONICAL_ENDPOINT_ANGLE_TOLERANCE = 1.0e-6


def _sealed_replay_audit() -> tuple[
    dict[str, Any],
    Array,
    Array,
    dict[float, Array],
    dict[float, dict[int, q011c.OrderedCluster]],
    dict[int, ComplexArray],
    dict[int, ComplexArray],
]:
    artifact_directory = Path(__file__).resolve().parent / "artifacts"
    q011c1_artifact_path = artifact_directory / "q011c1_endpoint_localization.json"
    q011c_artifact_path = artifact_directory / "q011c_forced_spectral_cluster.json"
    q011b_artifact_path = artifact_directory / "q011b_zero_mean_forced_fixed_point.json"
    q011c1_runner_path = Path(q011c1.__file__).resolve()
    q011c_runner_path = Path(q011c.__file__).resolve()
    q011c1_artifact = json.loads(q011c1_artifact_path.read_text(encoding="utf-8"))
    q011c_artifact = json.loads(q011c_artifact_path.read_text(encoding="utf-8"))
    q011b_artifact = json.loads(q011b_artifact_path.read_text(encoding="utf-8"))
    fresh_q011c1_cycle = q011c1.run_endpoint_localization_audit()

    stored_state = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    _conservation, basis, basis_audit = q011b._fixed_leaf_basis()
    (
        original_forward_states,
        _original_backward_states,
        original_path_audit,
    ) = q011c._fixed_point_path_audit(stored_state, basis)
    (
        reference_bases,
        reference_targets,
        reference_audit,
    ) = q011c._reference_audit(basis)
    original_forward_clusters, original_cluster_audit = q011c._cluster_path_audit(
        original_forward_states,
        _original_backward_states,
        basis,
        reference_bases,
        reference_targets,
    )

    q011c1_digests = (
        fresh_q011c1_cycle["input_digest_sha256"],
        fresh_q011c1_cycle["metric_digest_sha256"],
        fresh_q011c1_cycle["enclosure_digest_sha256"],
        fresh_q011c1_cycle["result_digest_sha256"],
    )
    q011c_digests = (
        q011c_artifact["cycle"]["input_digest_sha256"],
        q011c_artifact["cycle"]["path_digest_sha256"],
        q011c_artifact["cycle"]["spectrum_digest_sha256"],
        q011c_artifact["cycle"]["result_digest_sha256"],
    )
    checks = {
        "q011c1_artifact_sha256_matches": (
            _file_sha256(q011c1_artifact_path) == Q011C1_ARTIFACT_SHA256
        ),
        "q011c1_runner_sha256_matches": (_file_sha256(q011c1_runner_path) == Q011C1_RUNNER_SHA256),
        "q011c1_cycle_replays_exactly": (q011c1_artifact["cycle"] == fresh_q011c1_cycle),
        "q011c1_digests_match": (
            q011c1_digests
            == (
                Q011C1_INPUT_DIGEST,
                Q011C1_METRIC_DIGEST,
                Q011C1_ENCLOSURE_DIGEST,
                Q011C1_RESULT_DIGEST,
            )
        ),
        "q011c1_accepted_localization_reproduces": (
            fresh_q011c1_cycle["study_validity"] == "passed"
            and fresh_q011c1_cycle["hypothesis_outcome"] == "accepted"
            and fresh_q011c1_cycle["scientific_classification"]
            == (
                "the Q011c endpoint failure is localized to perturbation-"
                "consistent conjugate-witness tie instability"
            )
            and all(gate["passed"] for gate in fresh_q011c1_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in fresh_q011c1_cycle["hypothesis_gates"].values())
        ),
        "q011c_artifact_sha256_matches": (
            _file_sha256(q011c_artifact_path) == Q011C_ARTIFACT_SHA256
        ),
        "q011c_runner_sha256_matches": (_file_sha256(q011c_runner_path) == Q011C_RUNNER_SHA256),
        "q011c_digests_match": (
            q011c_digests
            == (
                Q011C_INPUT_DIGEST,
                Q011C_PATH_DIGEST,
                Q011C_SPECTRUM_DIGEST,
                Q011C_RESULT_DIGEST,
            )
        ),
        "q011c_original_outcome_remains_inconclusive": (
            q011c_artifact["cycle"]["study_validity"] == "failed"
            and q011c_artifact["cycle"]["hypothesis_outcome"] == "inconclusive"
            and q011c_artifact["cycle"]["scientific_classification"]
            == "registered forced spectral-cluster audit is invalid"
            and sum(
                not gate["passed"] for gate in q011c_artifact["cycle"]["validity_gates"].values()
            )
            == 1
            and not q011c_artifact["cycle"]["validity_gates"][
                "checkpoint_spectrum_and_q011b_endpoint_reproduce"
            ]["passed"]
        ),
        "q011c_raw_diagnostics_remain_true": (
            q011c_artifact["cycle"]["fixed_point_path_audit"]["passed"]
            and q011c_artifact["cycle"]["cluster_path_audit"]["structural_passed"]
            and q011c_artifact["cycle"]["cluster_path_audit"]["hypothesis_passed"]
            and q011c_artifact["cycle"]["checkpoint_spectrum_audit"]["hypothesis_passed"]
        ),
        "original_path_reconstructs_exactly": (
            original_path_audit == q011c_artifact["cycle"]["fixed_point_path_audit"]
        ),
        "original_cluster_path_reconstructs_exactly": (
            original_cluster_audit == q011c_artifact["cycle"]["cluster_path_audit"]
        ),
        "reference_and_basis_reconstruct_exactly": (
            reference_audit == q011c_artifact["cycle"]["unforced_reference_audit"]
            and basis_audit == q011c_artifact["cycle"]["fixed_leaf_basis_audit"]
        ),
        "stored_endpoint_sha256_matches": (
            q011c._array_sha256(stored_state) == Q011B_STORED_STATE_SHA256
        ),
        "package_source_sha256_matches": (
            source_metadata()["package_source_sha256"] == SEALED_PACKAGE_SOURCE_SHA256
        ),
    }
    audit = {
        "q011c1_artifact": {
            "filename": q011c1_artifact_path.name,
            "sha256": _file_sha256(q011c1_artifact_path),
            "runner_filename": q011c1_runner_path.name,
            "runner_sha256": _file_sha256(q011c1_runner_path),
            "input_digest_sha256": fresh_q011c1_cycle["input_digest_sha256"],
            "metric_digest_sha256": fresh_q011c1_cycle["metric_digest_sha256"],
            "enclosure_digest_sha256": fresh_q011c1_cycle["enclosure_digest_sha256"],
            "result_digest_sha256": fresh_q011c1_cycle["result_digest_sha256"],
            "study_validity": fresh_q011c1_cycle["study_validity"],
            "hypothesis_outcome": fresh_q011c1_cycle["hypothesis_outcome"],
            "scientific_classification": fresh_q011c1_cycle["scientific_classification"],
        },
        "q011c_artifact": {
            "filename": q011c_artifact_path.name,
            "sha256": _file_sha256(q011c_artifact_path),
            "runner_filename": q011c_runner_path.name,
            "runner_sha256": _file_sha256(q011c_runner_path),
            "input_digest_sha256": q011c_artifact["cycle"]["input_digest_sha256"],
            "path_digest_sha256": q011c_artifact["cycle"]["path_digest_sha256"],
            "spectrum_digest_sha256": q011c_artifact["cycle"]["spectrum_digest_sha256"],
            "result_digest_sha256": q011c_artifact["cycle"]["result_digest_sha256"],
            "study_validity": q011c_artifact["cycle"]["study_validity"],
            "hypothesis_outcome": q011c_artifact["cycle"]["hypothesis_outcome"],
        },
        "q011b_artifact": {
            "filename": q011b_artifact_path.name,
            "sha256": _file_sha256(q011b_artifact_path),
            "stored_endpoint_sha256": q011c._array_sha256(stored_state),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        stored_state,
        basis,
        original_forward_states,
        original_forward_clusters,
        reference_bases,
        reference_targets,
    )


def _positive_state_record(
    direction: str,
    factor: float,
    state: Array,
) -> dict[str, Any]:
    minimum_population = float(np.min(state))
    minimum_density = float(np.min(np.sum(state, axis=-1)))
    return {
        "direction": direction,
        "amplitude_factor": factor,
        "minimum_population": minimum_population,
        "minimum_density": minimum_density,
        "passed": bool(minimum_population > 0.0 and minimum_density > 0.0),
    }


def _fine_fixed_point_path_audit(
    stored_endpoint: Array,
    basis: Array,
    original_forward_states: dict[float, Array],
) -> tuple[dict[float, Array], dict[float, Array], dict[str, Any]]:
    rest = q011b.uniform_equilibrium(SIZE, 1, np.zeros(3))
    forward_states: dict[float, Array] = {}
    backward_states: dict[float, Array] = {}
    forward_records: list[dict[str, Any]] = []
    backward_records: list[dict[str, Any]] = []

    coordinate = np.zeros(q011c.FIXED_LEAF_DIMENSION, dtype=np.float64)
    for factor in FINE_FACTORS:
        coordinate, state, record = q011c._solve_fixed_point(
            factor,
            coordinate,
            rest,
            basis,
        )
        forward_states[factor] = state
        forward_records.append(record)

    coordinate = basis.T @ (stored_endpoint - rest).ravel()
    for factor in reversed(FINE_FACTORS):
        coordinate, state, record = q011c._solve_fixed_point(
            factor,
            coordinate,
            rest,
            basis,
        )
        backward_states[factor] = state
        backward_records.append(record)

    comparison_records: list[dict[str, Any]] = []
    for factor in FINE_FACTORS:
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
                "relative_passed": bool(
                    not relative_applicable or relative <= STATE_RELATIVE_DISTANCE_TOLERANCE
                ),
            }
        )

    training_records: list[dict[str, Any]] = []
    for factor in TRAINING_FACTORS:
        reissued = forward_states[factor]
        original = original_forward_states[factor]
        distance = float(np.linalg.norm(reissued - original))
        scale = max(
            float(np.linalg.norm(reissued - rest)),
            float(np.linalg.norm(original - rest)),
            np.finfo(float).tiny,
        )
        relative = distance / scale
        relative_applicable = factor > 0.0
        training_records.append(
            {
                "amplitude_factor": factor,
                "population_l2_distance": distance,
                "departure_scale": scale,
                "relative_distance": relative,
                "relative_gate_applicable": relative_applicable,
                "absolute_passed": distance <= STATE_DISTANCE_TOLERANCE,
                "relative_passed": bool(
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
    positivity_records = [
        _positive_state_record("forward", factor, forward_states[factor]) for factor in FINE_FACTORS
    ] + [
        _positive_state_record("backward", factor, backward_states[factor])
        for factor in FINE_FACTORS
    ]
    checks = {
        "registered_forward_node_count_is_seventeen": (len(forward_records) == 17),
        "registered_backward_node_count_is_seventeen": (len(backward_records) == 17),
        "all_forward_solves_converged": all(record["converged"] for record in forward_records),
        "all_backward_solves_converged": all(record["converged"] for record in backward_records),
        "all_forward_backward_absolute_distances_pass": all(
            record["absolute_passed"] for record in comparison_records
        ),
        "all_nonzero_forward_backward_relative_distances_pass": all(
            record["relative_passed"] for record in comparison_records
        ),
        "all_training_absolute_distances_pass": all(
            record["absolute_passed"] for record in training_records
        ),
        "all_nonzero_training_relative_distances_pass": all(
            record["relative_passed"] for record in training_records
        ),
        "endpoint_absolute_distance_passes": (endpoint_distance <= STATE_DISTANCE_TOLERANCE),
        "endpoint_relative_distance_passes": (
            endpoint_relative <= STATE_RELATIVE_DISTANCE_TOLERANCE
        ),
        "all_states_are_strictly_positive": all(record["passed"] for record in positivity_records),
        "all_values_are_finite": bool(
            _all_numeric_values_finite(forward_records)
            and _all_numeric_values_finite(backward_records)
            and _all_numeric_values_finite(comparison_records)
            and _all_numeric_values_finite(training_records)
            and _all_numeric_values_finite(positivity_records)
        ),
    }
    return (
        forward_states,
        backward_states,
        {
            "amplitude_factors": list(FINE_FACTORS),
            "training_factors": list(TRAINING_FACTORS),
            "heldout_factors": list(HELDOUT_FACTORS),
            "forward_records": forward_records,
            "backward_records": backward_records,
            "forward_backward_comparisons": comparison_records,
            "training_state_comparisons": training_records,
            "positivity_records": positivity_records,
            "endpoint_population_l2_distance": endpoint_distance,
            "endpoint_departure_scale": endpoint_scale,
            "endpoint_relative_distance": endpoint_relative,
            "forward_state_sha256": {
                str(factor): q011c._array_sha256(forward_states[factor]) for factor in FINE_FACTORS
            },
            "backward_state_sha256": {
                str(factor): q011c._array_sha256(backward_states[factor]) for factor in FINE_FACTORS
            },
            "minimum_population": min(
                record["minimum_population"] for record in positivity_records
            ),
            "minimum_density": min(record["minimum_density"] for record in positivity_records),
            "checks": checks,
            "passed": all(checks.values()),
        },
    )


def _fine_cluster_path_audit(
    forward_states: dict[float, Array],
    backward_states: dict[float, Array],
    stored_endpoint: Array,
    basis: Array,
    reference_bases: dict[int, ComplexArray],
    reference_targets: dict[int, ComplexArray],
    original_forward_clusters: dict[
        float,
        dict[int, q011c.OrderedCluster],
    ],
) -> tuple[
    dict[float, dict[int, q011c.OrderedCluster]],
    dict[str, Any],
]:
    forward_clusters, forward_records = q011c._track_one_direction(
        FINE_FACTORS,
        forward_states,
        basis,
        reference_bases,
        reference_targets,
    )
    endpoint_targets = {
        index: forward_clusters[1.0][index].selected_eigenvalues for index in q011c.SELECTED_BLOCKS
    }
    backward_clusters, backward_records = q011c._track_one_direction(
        tuple(reversed(FINE_FACTORS)),
        backward_states,
        basis,
        reference_bases,
        endpoint_targets,
    )

    reversal_records: list[dict[str, Any]] = []
    for factor in FINE_FACTORS:
        for block_index in q011c.SELECTED_BLOCKS:
            angle = q011c._maximum_principal_angle(
                forward_clusters[factor][block_index].basis,
                backward_clusters[factor][block_index].basis,
            )
            reversal_records.append(
                {
                    "amplitude_factor": factor,
                    "block_index": block_index,
                    "maximum_principal_angle": angle,
                    "passed": angle <= q011c.REVERSAL_ANGLE_TOLERANCE,
                }
            )

    direct_records: list[dict[str, Any]] = []
    canonical_records: list[dict[str, Any]] = []
    for block_index in q011c.SELECTED_BLOCKS:
        forward_active = q011c._active_matrix(
            forward_states[1.0],
            block_index,
            basis,
        )
        direct = q011c._ordered_cluster(
            forward_active,
            reference_targets[block_index],
        )
        continued = forward_clusters[1.0][block_index]
        direct_angle = q011c._maximum_principal_angle(
            continued.basis,
            direct.basis,
        )
        direct_records.append(
            {
                "block_index": block_index,
                "maximum_principal_angle": direct_angle,
                "selected_spectrum_absolute_hausdorff_error": q011c._hausdorff(
                    continued.selected_eigenvalues,
                    direct.selected_eigenvalues,
                ),
                "passed": direct_angle <= q011c.DIRECT_ENDPOINT_ANGLE_TOLERANCE,
            }
        )

        canonical_active = q011c._active_matrix(
            stored_endpoint,
            block_index,
            basis,
        )
        canonical = q011c._ordered_cluster(
            canonical_active,
            reference_targets[block_index],
        )
        canonical_angle = q011c._maximum_principal_angle(
            continued.basis,
            canonical.basis,
        )
        canonical_records.append(
            {
                "block_index": block_index,
                "maximum_principal_angle": canonical_angle,
                "selected_spectrum_absolute_hausdorff_error": q011c._hausdorff(
                    continued.selected_eigenvalues,
                    canonical.selected_eigenvalues,
                ),
                "passed": (canonical_angle <= CANONICAL_ENDPOINT_ANGLE_TOLERANCE),
            }
        )

    training_records: list[dict[str, Any]] = []
    for factor in TRAINING_FACTORS:
        for block_index in q011c.SELECTED_BLOCKS:
            reissued = forward_clusters[factor][block_index]
            original = original_forward_clusters[factor][block_index]
            angle = q011c._maximum_principal_angle(
                reissued.basis,
                original.basis,
            )
            spectrum_error = q011c._hausdorff(
                reissued.selected_eigenvalues,
                original.selected_eigenvalues,
            )
            training_records.append(
                {
                    "amplitude_factor": factor,
                    "block_index": block_index,
                    "maximum_principal_angle": angle,
                    "selected_spectrum_absolute_hausdorff_error": spectrum_error,
                    "angle_passed": (angle <= TRAINING_CLUSTER_ANGLE_TOLERANCE),
                    "spectrum_passed": (spectrum_error <= TRAINING_SPECTRUM_TOLERANCE),
                    "passed": bool(
                        angle <= TRAINING_CLUSTER_ANGLE_TOLERANCE
                        and spectrum_error <= TRAINING_SPECTRUM_TOLERANCE
                    ),
                }
            )

    conjugacy_records: list[dict[str, Any]] = []
    for factor in FINE_FACTORS:
        positive = forward_clusters[factor][1]
        negative = forward_clusters[factor][16]
        projector_error = q011c._relative_error(
            positive.projector,
            np.conjugate(negative.projector),
        )
        spectrum_error = q011c._hausdorff(
            positive.selected_eigenvalues,
            np.conjugate(negative.selected_eigenvalues),
        )
        angle = q011c._maximum_principal_angle(
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
                "plus_minus_spectrum_absolute_hausdorff_error": spectrum_error,
                "plus_minus_subspace_maximum_principal_angle": angle,
                "zero_block_projector_imaginary_relative_norm": zero_imaginary,
                "passed": bool(
                    projector_error <= q011c.CONJUGACY_RELATIVE_TOLERANCE
                    and spectrum_error <= q011c.CONJUGACY_RELATIVE_TOLERANCE
                    and angle <= q011c.CONJUGACY_ANGLE_TOLERANCE
                    and zero_imaginary <= q011c.CONJUGACY_RELATIVE_TOLERANCE
                ),
            }
        )

    initial_records: list[dict[str, Any]] = []
    for block_index in q011c.SELECTED_BLOCKS:
        cluster = forward_clusters[0.0][block_index]
        initial_records.append(
            {
                "block_index": block_index,
                "reference_range_maximum_principal_angle": (
                    q011c._maximum_principal_angle(
                        reference_bases[block_index],
                        cluster.basis,
                    )
                ),
                "target_spectrum_absolute_hausdorff_error": q011c._hausdorff(
                    reference_targets[block_index],
                    cluster.selected_eigenvalues,
                ),
            }
        )

    all_records = [record for node in forward_records for record in node["block_records"]]
    maximum_structural = max(record["maximum_structural_residual"] for record in all_records)
    maximum_adjacent = max(record["adjacent_maximum_principal_angle"] for record in all_records)
    minimum_alignment = min(
        record["reference_minimum_singular_value_alignment"] for record in all_records
    )
    minimum_external = min(
        record["external_eigenvalue_absolute_separation"] for record in all_records
    )
    maximum_projector = max(record["projector_two_norm"] for record in all_records)
    maximum_reversal = max(record["maximum_principal_angle"] for record in reversal_records)
    maximum_direct = max(record["maximum_principal_angle"] for record in direct_records)
    maximum_canonical = max(record["maximum_principal_angle"] for record in canonical_records)
    maximum_training_angle = max(record["maximum_principal_angle"] for record in training_records)
    maximum_training_spectrum = max(
        record["selected_spectrum_absolute_hausdorff_error"] for record in training_records
    )
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
            len(forward_records) == 17 and len(backward_records) == 17 and len(all_records) == 51
        ),
        "all_selector_dimensions_are_registered": all(
            record["selected_dimension"] == q011c.SELECTED_DIMENSIONS[record["block_index"]]
            and record["selector_count"] == q011c.SELECTED_DIMENSIONS[record["block_index"]]
            for record in all_records
        ),
        "all_structural_residuals_within_tolerance": (
            maximum_structural <= q011c.STRUCTURAL_RESIDUAL_TOLERANCE
        ),
        "all_conjugacy_diagnostics_within_tolerance": all(
            record["passed"] for record in conjugacy_records
        ),
        "all_values_are_finite": bool(
            _all_numeric_values_finite(forward_records)
            and _all_numeric_values_finite(backward_records)
            and _all_numeric_values_finite(reversal_records)
            and _all_numeric_values_finite(direct_records)
            and _all_numeric_values_finite(canonical_records)
            and _all_numeric_values_finite(training_records)
            and _all_numeric_values_finite(conjugacy_records)
        ),
    }
    control_checks = {
        "all_reversal_angles_pass": all(record["passed"] for record in reversal_records),
        "all_direct_endpoint_angles_pass": all(record["passed"] for record in direct_records),
        "all_canonical_endpoint_angles_pass": all(record["passed"] for record in canonical_records),
        "all_training_cluster_controls_pass": all(record["passed"] for record in training_records),
        "initial_reference_reproduces": all(
            record["reference_range_maximum_principal_angle"] <= 1.0e-8
            and record["target_spectrum_absolute_hausdorff_error"]
            <= q011c.STRUCTURAL_RESIDUAL_TOLERANCE
            for record in initial_records
        ),
    }
    hypothesis_checks = {
        "adjacent_angles_within_tolerance": (maximum_adjacent <= q011c.ADJACENT_ANGLE_TOLERANCE),
        "reference_alignment_above_floor": (minimum_alignment >= q011c.REFERENCE_ALIGNMENT_FLOOR),
        "external_eigenvalue_separation_above_floor": (
            minimum_external >= q011c.EXTERNAL_EIGENVALUE_SEPARATION_FLOOR
        ),
        "projector_norm_below_ceiling": (maximum_projector <= q011c.PROJECTOR_NORM_CEILING),
        "path_and_control_angles_within_tolerance": all(list(control_checks.values())),
        "conjugacy_closure_passes": all(record["passed"] for record in conjugacy_records),
    }
    return forward_clusters, {
        "forward_node_records": forward_records,
        "backward_node_records": backward_records,
        "initial_reproduction_records": initial_records,
        "path_reversal_records": reversal_records,
        "direct_endpoint_records": direct_records,
        "canonical_stored_endpoint_records": canonical_records,
        "training_cluster_comparisons": training_records,
        "conjugacy_records": conjugacy_records,
        "summary": {
            "maximum_structural_residual": maximum_structural,
            "maximum_adjacent_principal_angle": maximum_adjacent,
            "minimum_reference_alignment": minimum_alignment,
            "minimum_external_eigenvalue_separation": minimum_external,
            "maximum_projector_two_norm": maximum_projector,
            "maximum_path_reversal_principal_angle": maximum_reversal,
            "maximum_direct_endpoint_principal_angle": maximum_direct,
            "maximum_canonical_endpoint_principal_angle": maximum_canonical,
            "maximum_training_cluster_principal_angle": maximum_training_angle,
            "maximum_training_spectrum_hausdorff_error": (maximum_training_spectrum),
            "maximum_projector_conjugacy_relative_error": (maximum_projector_conjugacy),
            "maximum_spectrum_conjugacy_hausdorff_error": (maximum_spectrum_conjugacy),
            "maximum_conjugacy_principal_angle": maximum_conjugacy_angle,
            "maximum_zero_block_projector_imaginary_relative_norm": (maximum_zero_imaginary),
        },
        "structural_checks": structural_checks,
        "structural_passed": all(structural_checks.values()),
        "control_checks": control_checks,
        "control_passed": all(control_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _heldout_checkpoint_audit(
    forward_states: dict[float, Array],
    forward_clusters: dict[float, dict[int, q011c.OrderedCluster]],
    basis: Array,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for factor in HELDOUT_FACTORS:
        state = forward_states[factor]
        clusters = forward_clusters[factor]
        sylvester_records: list[dict[str, Any]] = []
        selected_values: list[ComplexArray] = []
        external_values: list[ComplexArray] = []
        for block_index in range(SIZE):
            active = q011c._active_matrix(state, block_index, basis)
            if block_index in q011c.SELECTED_BLOCKS:
                cluster = clusters[block_index]
                separation = q011c._sylvester_separation(cluster)
                sylvester_records.append(
                    {
                        "block_index": block_index,
                        "operator_shape": [
                            cluster.selected_dimension * cluster.excluded_dynamics.shape[0],
                            cluster.selected_dimension * cluster.excluded_dynamics.shape[0],
                        ],
                        "minimum_singular_value": separation,
                        "passed": (separation >= q011c.SYLVESTER_SEPARATION_FLOOR),
                    }
                )
                selected_values.append(cluster.selected_eigenvalues)
                external_values.append(cluster.excluded_eigenvalues)
            else:
                external_values.append(linalg.eigvals(active, check_finite=True))
        selected_spectrum = np.concatenate(selected_values)
        external_spectrum = np.concatenate(external_values)
        selected_minimum = float(np.min(np.abs(selected_spectrum)))
        external_maximum = float(np.max(np.abs(external_spectrum)))
        normal_gap = selected_minimum - external_maximum
        full_spectrum = np.concatenate((selected_spectrum, external_spectrum))
        full_radius = float(np.max(np.abs(full_spectrum)))
        quotient = float(np.log(external_maximum) / np.log(selected_minimum))
        checks = {
            "spectrum_count_is_2598": (full_spectrum.size == SIZE * SIZE * 9 - 3),
            "selected_count_is_24": selected_spectrum.size == 24,
            "external_count_is_2574": (external_spectrum.size == SIZE * SIZE * 9 - 27),
            "sylvester_block_count_is_three": len(sylvester_records) == 3,
            "all_values_are_finite": bool(
                np.all(np.isfinite(full_spectrum)) and _all_numeric_values_finite(sylvester_records)
            ),
        }
        hypothesis_checks = {
            "all_sylvester_separations_above_floor": all(
                item["passed"] for item in sylvester_records
            ),
            "normal_dominance_gap_above_floor": (normal_gap >= q011c.NORMAL_DOMINANCE_GAP_FLOOR),
            "full_fixed_leaf_spectrum_is_stable": (full_radius <= q011b.SPECTRAL_RADIUS_CEILING),
        }
        records.append(
            {
                "amplitude_factor": factor,
                "selected_eigenvalue_count": int(selected_spectrum.size),
                "external_eigenvalue_count": int(external_spectrum.size),
                "full_fixed_leaf_eigenvalue_count": int(full_spectrum.size),
                "selected_spectrum_sha256": q011c._array_sha256(selected_spectrum),
                "external_spectrum_sha256": q011c._array_sha256(external_spectrum),
                "selected_minimum_eigenvalue_modulus": selected_minimum,
                "external_maximum_eigenvalue_modulus": external_maximum,
                "global_modulus_normal_dominance_gap": normal_gap,
                "full_fixed_leaf_spectral_radius": full_radius,
                "logarithmic_spectral_quotient_diagnostic": quotient,
                "sylvester_records": sylvester_records,
                "minimum_sylvester_separation": min(
                    item["minimum_singular_value"] for item in sylvester_records
                ),
                "checks": checks,
                "hypothesis_checks": hypothesis_checks,
            }
        )

    validity_checks = {
        "heldout_factors_are_registered": tuple(record["amplitude_factor"] for record in records)
        == HELDOUT_FACTORS,
        "all_eight_checkpoint_enumerations_are_complete": (
            len(records) == 8 and all(all(record["checks"].values()) for record in records)
        ),
        "all_records_are_finite": bool(_all_numeric_values_finite(records)),
    }
    hypothesis_checks = {
        "all_twenty_four_sylvester_separations_above_floor": all(
            record["hypothesis_checks"]["all_sylvester_separations_above_floor"]
            for record in records
        ),
        "all_eight_normal_dominance_gaps_above_floor": all(
            record["hypothesis_checks"]["normal_dominance_gap_above_floor"] for record in records
        ),
        "all_eight_full_fixed_leaf_spectra_are_stable": all(
            record["hypothesis_checks"]["full_fixed_leaf_spectrum_is_stable"] for record in records
        ),
    }
    return {
        "heldout_factors": list(HELDOUT_FACTORS),
        "checkpoint_records": records,
        "minimum_sylvester_separation": min(
            record["minimum_sylvester_separation"] for record in records
        ),
        "minimum_global_modulus_normal_dominance_gap": min(
            record["global_modulus_normal_dominance_gap"] for record in records
        ),
        "maximum_full_fixed_leaf_spectral_radius": max(
            record["full_fixed_leaf_spectral_radius"] for record in records
        ),
        "validity_checks": validity_checks,
        "validity_passed": all(validity_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _endpoint_orbit_semantics_audit(
    stored_state: Array,
    continued_state: Array,
    basis: Array,
) -> dict[str, Any]:
    (
        stored_audit,
        stored_matrices,
        stored_resolvents,
    ) = q011c1._endpoint_block_audit(
        "q011b_stored",
        stored_state,
        basis,
    )
    (
        continued_audit,
        continued_matrices,
        continued_resolvents,
    ) = q011c1._endpoint_block_audit(
        "q011c2_forward_continued",
        continued_state,
        basis,
    )
    stored_conjugacy = q011c1._matrix_conjugacy_audit(
        "q011b_stored",
        stored_matrices,
    )
    continued_conjugacy = q011c1._matrix_conjugacy_audit(
        "q011c2_forward_continued",
        continued_matrices,
    )
    stored_records = q011c1._record_by_index(stored_audit)
    continued_records = q011c1._record_by_index(continued_audit)
    records: list[dict[str, Any]] = []
    for block_index in range(SIZE):
        stored = stored_records[block_index]
        continued = continued_records[block_index]
        stored_matrix = stored_resolvents[block_index]
        continued_matrix = continued_resolvents[block_index]
        padding = float(
            q011c1.ROUNDING_PADDING_FACTOR
            * np.finfo(float).eps
            * max(
                1.0,
                float(np.linalg.norm(stored_matrix)),
                float(np.linalg.norm(continued_matrix)),
            )
        )
        difference = float(np.linalg.norm(continued_matrix - stored_matrix))
        bound = difference + padding
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
        records.append(
            {
                "block_index": block_index,
                "resolvent_difference_frobenius_norm": difference,
                "rounding_padding": padding,
                "registered_perturbation_bound": bound,
                "minimum_singular_interval": minimum_interval,
                "maximum_singular_interval": maximum_interval,
                "condition_interval": condition_interval,
                "stored_minimum_singular_value": stored_minimum,
                "continued_minimum_singular_value": continued["minimum_singular_value"],
                "stored_maximum_singular_value": stored_maximum,
                "continued_maximum_singular_value": continued["maximum_singular_value"],
                "stored_condition_number": stored["condition_number"],
                "continued_condition_number": continued["condition_number"],
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

    record_map = {record["block_index"]: record for record in records}
    winner_minimum_upper = min(
        record_map[index]["minimum_singular_interval"][1]
        for index in q011c1.WINNING_RESOLVENT_ORBIT
    )
    external_minimum_lower = min(
        record_map[index]["minimum_singular_interval"][0]
        for index in range(SIZE)
        if index not in q011c1.WINNING_RESOLVENT_ORBIT
    )
    minimum_margin = external_minimum_lower - winner_minimum_upper
    winner_condition_lower = max(
        record_map[index]["condition_interval"][0] for index in q011c1.WINNING_RESOLVENT_ORBIT
    )
    external_condition_upper = max(
        record_map[index]["condition_interval"][1]
        for index in range(SIZE)
        if index not in q011c1.WINNING_RESOLVENT_ORBIT
    )
    condition_margin = winner_condition_lower - external_condition_upper
    stored_orbits = {
        "spectral_radius": list(
            q011c1._orbit_for_index(stored_audit["spectral_radius_witness_index"])
        ),
        "minimum_singular_value": list(
            q011c1._orbit_for_index(stored_audit["minimum_singular_witness_index"])
        ),
        "maximum_condition_number": list(
            q011c1._orbit_for_index(stored_audit["maximum_condition_witness_index"])
        ),
    }
    continued_orbits = {
        "spectral_radius": list(
            q011c1._orbit_for_index(continued_audit["spectral_radius_witness_index"])
        ),
        "minimum_singular_value": list(
            q011c1._orbit_for_index(continued_audit["minimum_singular_witness_index"])
        ),
        "maximum_condition_number": list(
            q011c1._orbit_for_index(continued_audit["maximum_condition_witness_index"])
        ),
    }
    structural_checks = {
        "stored_endpoint_full_svd_is_structural": stored_audit["passed"],
        "continued_endpoint_full_svd_is_structural": continued_audit["passed"],
        "stored_matrix_conjugacy_passes": stored_conjugacy["passed"],
        "continued_matrix_conjugacy_passes": continued_conjugacy["passed"],
        "all_interval_records_are_finite": bool(_all_numeric_values_finite(records)),
    }
    hypothesis_checks = {
        "all_block_metric_changes_are_enclosed": all(record["passed"] for record in records),
        "registered_extremal_orbits_are_stable": (
            stored_orbits
            == {
                "spectral_radius": [0],
                "minimum_singular_value": [1, 16],
                "maximum_condition_number": [1, 16],
            }
            and continued_orbits == stored_orbits
        ),
        "minimum_singular_winning_orbit_is_interval_separated": (minimum_margin > 0.0),
        "maximum_condition_winning_orbit_is_interval_separated": (condition_margin > 0.0),
    }
    return {
        "rounding_padding_factor": q011c1.ROUNDING_PADDING_FACTOR,
        "stored_endpoint_block_audit": stored_audit,
        "continued_endpoint_block_audit": continued_audit,
        "stored_matrix_conjugacy_audit": stored_conjugacy,
        "continued_matrix_conjugacy_audit": continued_conjugacy,
        "perturbation_records": records,
        "maximum_resolvent_difference_frobenius_norm": max(
            record["resolvent_difference_frobenius_norm"] for record in records
        ),
        "maximum_registered_perturbation_bound": max(
            record["registered_perturbation_bound"] for record in records
        ),
        "stored_extremal_orbits": stored_orbits,
        "continued_extremal_orbits": continued_orbits,
        "minimum_singular_orbit_separation_margin": minimum_margin,
        "maximum_condition_orbit_separation_margin": condition_margin,
        "structural_checks": structural_checks,
        "structural_passed": all(structural_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011c.OMEGA,
        "eta": q011c.ETA,
        "fine_amplitude_factors": list(FINE_FACTORS),
        "training_amplitude_factors": list(TRAINING_FACTORS),
        "heldout_amplitude_factors": list(HELDOUT_FACTORS),
        "training_node_count": len(TRAINING_FACTORS),
        "heldout_node_count": len(HELDOUT_FACTORS),
        "selected_blocks": {
            str(index): {
                "selected_ky_indices": list(q011c.SELECTED_BLOCKS[index]),
                "selected_complex_dimension": q011c.SELECTED_DIMENSIONS[index],
            }
            for index in q011c.SELECTED_BLOCKS
        },
        "total_selected_complex_dimension": 24,
        "physical_real_dimension_under_conjugacy": 24,
        "fixed_point_thresholds": {
            "projected_residual": q011b.PROJECTED_RESIDUAL_TOLERANCE,
            "full_residual": q011b.FULL_RESIDUAL_TOLERANCE,
            "component_residual": q011b.COMPONENT_RESIDUAL_TOLERANCE,
            "state_absolute": STATE_DISTANCE_TOLERANCE,
            "nonzero_state_relative": STATE_RELATIVE_DISTANCE_TOLERANCE,
        },
        "cluster_thresholds": {
            "adjacent_angle": q011c.ADJACENT_ANGLE_TOLERANCE,
            "reference_alignment": q011c.REFERENCE_ALIGNMENT_FLOOR,
            "external_eigenvalue_separation": (q011c.EXTERNAL_EIGENVALUE_SEPARATION_FLOOR),
            "projector_norm": q011c.PROJECTOR_NORM_CEILING,
            "structural_residual": q011c.STRUCTURAL_RESIDUAL_TOLERANCE,
            "reversal_angle": q011c.REVERSAL_ANGLE_TOLERANCE,
            "direct_endpoint_angle": (q011c.DIRECT_ENDPOINT_ANGLE_TOLERANCE),
            "canonical_endpoint_angle": (CANONICAL_ENDPOINT_ANGLE_TOLERANCE),
            "training_cluster_angle": (TRAINING_CLUSTER_ANGLE_TOLERANCE),
            "training_spectrum_hausdorff": TRAINING_SPECTRUM_TOLERANCE,
            "conjugacy_relative": q011c.CONJUGACY_RELATIVE_TOLERANCE,
            "conjugacy_angle": q011c.CONJUGACY_ANGLE_TOLERANCE,
            "sylvester_separation": q011c.SYLVESTER_SEPARATION_FLOOR,
            "normal_dominance_gap": q011c.NORMAL_DOMINANCE_GAP_FLOOR,
            "full_fixed_leaf_spectral_radius": (q011b.SPECTRAL_RADIUS_CEILING),
        },
        "endpoint_orbit_semantics": {
            "orbit_partition": [list(orbit) for orbit in q011c1.ORBIT_PARTITION],
            "winning_radius_orbit": [0],
            "winning_resolvent_orbit": [1, 16],
            "rounding_padding_factor": q011c1.ROUNDING_PADDING_FACTOR,
            "individual_witness_index_is_gated": False,
            "absolute_condition_reproduction_is_gated": False,
        },
        "q011c_original_is_regraded": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "path_digest_sha256": cycle["path_digest_sha256"],
        "holdout_spectrum_digest_sha256": cycle["holdout_spectrum_digest_sha256"],
        "endpoint_digest_sha256": cycle["endpoint_digest_sha256"],
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


def run_heldout_cluster_reissue_audit() -> dict[str, Any]:
    """Run the preregistered Q011c2 held-out cluster reissue."""

    registered_parameters = _registered_parameters()
    (
        sealed_replay,
        stored_endpoint,
        basis,
        original_forward_states,
        original_forward_clusters,
        reference_bases,
        reference_targets,
    ) = _sealed_replay_audit()
    forward_states, backward_states, fixed_point_path = _fine_fixed_point_path_audit(
        stored_endpoint,
        basis,
        original_forward_states,
    )
    forward_clusters, cluster_path = _fine_cluster_path_audit(
        forward_states,
        backward_states,
        stored_endpoint,
        basis,
        reference_bases,
        reference_targets,
        original_forward_clusters,
    )
    heldout_spectrum = _heldout_checkpoint_audit(
        forward_states,
        forward_clusters,
        basis,
    )
    endpoint_semantics = _endpoint_orbit_semantics_audit(
        stored_endpoint,
        forward_states[1.0],
        basis,
    )

    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_replay_audit": sealed_replay,
    }
    path_sections = {
        "fine_fixed_point_path_audit": fixed_point_path,
        "fine_cluster_path_audit": cluster_path,
    }
    holdout_sections = {
        "heldout_checkpoint_audit": heldout_spectrum,
    }
    endpoint_sections = {
        "endpoint_orbit_semantics_audit": endpoint_semantics,
    }
    input_digest = q011c._canonical_json_sha256(input_sections)
    path_digest = q011c._canonical_json_sha256(path_sections)
    holdout_digest = q011c._canonical_json_sha256(holdout_sections)
    endpoint_digest = q011c._canonical_json_sha256(endpoint_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **path_sections,
        **holdout_sections,
        **endpoint_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011c._canonical_json_sha256(input_sections)
        and path_digest == q011c._canonical_json_sha256(path_sections)
        and holdout_digest == q011c._canonical_json_sha256(holdout_sections)
        and endpoint_digest == q011c._canonical_json_sha256(endpoint_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )
    validity_gates = {
        "sealed_q011c1_q011c_and_q011b_inputs_replay": {
            "passed": sealed_replay["passed"],
            "threshold": (
                "Q011c1 and Q011c artifacts, runners, all digests, exact "
                "cycles, Q011b endpoint and package source reproduce"
            ),
            "value": sealed_replay["checks"],
        },
        "seventeen_node_fixed_point_paths_are_valid": {
            "passed": fixed_point_path["passed"],
            "threshold": (
                "17-node forward/backward Newton paths, nine training "
                "controls, positivity and endpoint agreement pass"
            ),
            "value": fixed_point_path["checks"],
        },
        "seventeen_node_cluster_construction_is_structural": {
            "passed": cluster_path["structural_passed"],
            "threshold": (
                "51 ordered selections have dimensions 6/9/9, structural "
                "residuals <=1e-10 and conjugacy closure"
            ),
            "value": cluster_path["structural_checks"],
        },
        "training_direct_and_canonical_cluster_controls_reproduce": {
            "passed": cluster_path["control_passed"],
            "threshold": (
                "nine training nodes, path reversal, direct endpoint and "
                "stored canonical endpoint controls pass registered angles"
            ),
            "value": cluster_path["control_checks"],
        },
        "eight_heldout_sylvester_and_full_spectra_are_complete": {
            "passed": heldout_spectrum["validity_passed"],
            "threshold": (
                "eight held-out nodes enumerate 24 Sylvester operators and "
                "eight complete 2598-eigenvalue fixed-leaf spectra"
            ),
            "value": heldout_spectrum["validity_checks"],
        },
        "endpoint_orbit_intervals_are_structural": {
            "passed": endpoint_semantics["structural_passed"],
            "threshold": (
                "34 endpoint SVDs and matrix conjugacy are structural and "
                "17 finite intervals use the registered formula"
            ),
            "value": endpoint_semantics["structural_checks"],
        },
        "finite_strict_json_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "all values finite strict JSON; input, path, held-out "
                "spectrum and endpoint digests plus runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_provenance_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    cluster_checks = cluster_path["hypothesis_checks"]
    heldout_checks = heldout_spectrum["hypothesis_checks"]
    raw_hypotheses = {
        "seventeen_node_positive_fixed_point_branch_connects": (fixed_point_path["passed"]),
        "twenty_four_dimensional_conjugacy_closed_cluster_continues": bool(
            cluster_checks["adjacent_angles_within_tolerance"]
            and cluster_checks["reference_alignment_above_floor"]
            and cluster_checks["path_and_control_angles_within_tolerance"]
            and cluster_checks["conjugacy_closure_passes"]
        ),
        "cluster_and_heldout_sylvester_separations_hold": bool(
            cluster_checks["external_eigenvalue_separation_above_floor"]
            and cluster_checks["projector_norm_below_ceiling"]
            and heldout_checks["all_twenty_four_sylvester_separations_above_floor"]
        ),
        "heldout_global_normal_dominance_and_stability_hold": bool(
            heldout_checks["all_eight_normal_dominance_gaps_above_floor"]
            and heldout_checks["all_eight_full_fixed_leaf_spectra_are_stable"]
        ),
        "endpoint_conjugacy_orbit_semantics_hold": (endpoint_semantics["hypothesis_passed"]),
    }
    hypothesis_gates = {
        "seventeen_node_positive_fixed_point_branch_connects": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["seventeen_node_positive_fixed_point_branch_connects"]
            ),
            "threshold": (
                "17 forward/backward state distances <=1e-11, nonzero "
                "relative distances <=1e-8, all states positive"
            ),
            "value": {
                "maximum_forward_backward_distance": max(
                    record["population_l2_distance"]
                    for record in fixed_point_path["forward_backward_comparisons"]
                ),
                "endpoint_distance": fixed_point_path["endpoint_population_l2_distance"],
                "minimum_population": fixed_point_path["minimum_population"],
                "minimum_density": fixed_point_path["minimum_density"],
            },
        },
        "twenty_four_dimensional_conjugacy_closed_cluster_continues": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["twenty_four_dimensional_conjugacy_closed_cluster_continues"]
            ),
            "threshold": (
                "dimensions 6/9/9, alignment >=0.95, adjacent <=0.05, "
                "all reversal/training/direct/canonical/conjugacy controls pass"
            ),
            "value": cluster_path["summary"],
        },
        "cluster_and_heldout_sylvester_separations_hold": {
            "passed": bool(
                validity_passed and raw_hypotheses["cluster_and_heldout_sylvester_separations_hold"]
            ),
            "threshold": (
                "all 17-node external gaps >=1e-6, projector norms <=100 "
                "and 24 held-out Sylvester separations >=1e-5"
            ),
            "value": {
                "minimum_external_eigenvalue_separation": cluster_path["summary"][
                    "minimum_external_eigenvalue_separation"
                ],
                "maximum_projector_two_norm": cluster_path["summary"]["maximum_projector_two_norm"],
                "minimum_heldout_sylvester_separation": heldout_spectrum[
                    "minimum_sylvester_separation"
                ],
            },
        },
        "heldout_global_normal_dominance_and_stability_hold": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["heldout_global_normal_dominance_and_stability_hold"]
            ),
            "threshold": (
                "all eight held-out normal gaps >=1e-6 and fixed-leaf spectral radii <=0.9999"
            ),
            "value": {
                "minimum_normal_gap": heldout_spectrum[
                    "minimum_global_modulus_normal_dominance_gap"
                ],
                "maximum_full_spectral_radius": heldout_spectrum[
                    "maximum_full_fixed_leaf_spectral_radius"
                ],
            },
        },
        "endpoint_conjugacy_orbit_semantics_hold": {
            "passed": bool(
                validity_passed and raw_hypotheses["endpoint_conjugacy_orbit_semantics_hold"]
            ),
            "threshold": (
                "all endpoint resolvent metrics are enclosed; winner "
                "orbits {0} and {1,16} are stable and interval-separated"
            ),
            "value": {
                "checks": endpoint_semantics["hypothesis_checks"],
                "minimum_singular_orbit_margin": endpoint_semantics[
                    "minimum_singular_orbit_separation_margin"
                ],
                "maximum_condition_orbit_margin": endpoint_semantics[
                    "maximum_condition_orbit_separation_margin"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011c2 held-out cluster reissue is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the forced first-shell cluster passes a conjugacy-orbit "
            "reissue with eight held-out amplitude nodes"
        )
    else:
        outcome = "rejected"
        classification = "the forced first-shell cluster fails the registered held-out reissue"

    cycle: dict[str, Any] = {
        "question": (
            "Does the forced first-shell cluster pass a conjugacy-orbit "
            "reissue on a 17-node path with eight held-out amplitude midpoints?"
        ),
        **pre_gate_sections,
        "input_digest_sha256": input_digest,
        "path_digest_sha256": path_digest,
        "holdout_spectrum_digest_sha256": holdout_digest,
        "endpoint_digest_sha256": endpoint_digest,
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
        "forced_candidate_spectral_cluster_is_selected": bool(
            validity_passed and hypotheses_passed
        ),
        "individual_forced_modes_are_labeled": False,
        "forced_external_nonresonance_is_certified": False,
        "forced_invariant_manifold_is_constructed": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 finite prequalification on one "
        "17x17 grid, one endpoint force and 17 registered amplitude nodes, "
        "including eight held-out midpoints. It does not alter Q011c, "
        "prove continuous-amplitude continuation, provide rigorous "
        "projector or SVD enclosures, label individual forced modes, "
        "certify external nonresonance or spectral-quotient smoothness, "
        "construct a forced invariant manifold, prove nonlinear normal "
        "attraction or a basin, or cover other grids, amplitudes or walls."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011c_inconclusive_outcome_changed": False,
        "q011c1_accepted_localization_changed": False,
        "q011b_accepted_fixed_point_changed": False,
        "q011a_nonzero_mean_obstruction_changed": False,
        "q006h_unforced_selected_family_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011d for quadratic external nonresonance and the "
        "forced-cluster homological operator."
        if outcome == "accepted"
        else (
            "Localize the first failed held-out path, cluster, Sylvester, "
            "normal-gap or endpoint-orbit gate without proceeding to Q011d."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011c2 cycle failed strict serialization or digest")
    return cycle


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def run_q011c2_study() -> dict[str, Any]:
    cycle = run_heldout_cluster_reissue_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 held-out forced spectral-cluster continuation, "
                "Sylvester separation and orbit-semantic endpoint audit"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011c.OMEGA,
            "eta": q011c.ETA,
            "amplitude_node_count": len(FINE_FACTORS),
            "training_node_count": len(TRAINING_FACTORS),
            "heldout_node_count": len(HELDOUT_FACTORS),
            "heldout_sylvester_operator_count": (len(HELDOUT_FACTORS) * len(q011c.SELECTED_BLOCKS)),
            "heldout_fixed_leaf_spectrum_count": len(HELDOUT_FACTORS),
            "selected_complex_dimension": 24,
            "selected_physical_real_dimension": 24,
            "q011c_is_regraded": False,
            "claim": (
                "finite held-out linear spectral prequalification only; "
                "no forced invariant-manifold or nonlinear-attraction claim"
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
    result = run_q011c2_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
