"""Sealed Q011f1 held-out-amplitude multi-step shadowing reissue."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

import research.q011f_multistep_shadowing as q011f
from ttim_lbm.d2q9 import global_conserved_quantities
from ttim_lbm.manifold import log_log_slope
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011e = q011f.q011e
q011e1 = q011f.q011e1
SIZE = q011f.SIZE
SELECTED_DIMENSION = q011f.SELECTED_DIMENSION

Q011F_ARTIFACT_SHA256 = "9c091dbafd60617850cd3168f3ad9235a353b0990cbd003df9be0b487ead1591"
Q011F_RUNNER_SHA256 = "e9c0a8e38b94dbe693855dc836f8cf02393675b417ff3f43fc43059ab361a741"
Q011F_INPUT_DIGEST = "e9b29c95d41af0062259d3aab19ab2c58175cd98582ed82f3af36863f023bc53"
Q011F_CHART_DIGEST = "aa1da452db8ff6b84e88a32f7a7119c63816b12e283147daaa303e9e09c3ae42"
Q011F_TRAJECTORY_DIGEST = "aa62fc11a36bef881bbcdb05919818f6db167f3f95eee396fcdaf79fead5e182"
Q011F_RESULT_DIGEST = "629a5a7a3d3bfed12a590646c375d4977db1726ddc521ddb86394786b1005f22"
Q011F_DIRECTION_SHA256 = "4d0bef57236d4f70a8a8f422b1bdfa39cd5737c88401c2441decdd98d886d2f9"
SEALED_PACKAGE_SOURCE_SHA256 = q011f.SEALED_PACKAGE_SOURCE_SHA256

HELDOUT_AMPLITUDE = 4.8e-4
MERGED_AMPLITUDES = (
    q011f.AMPLITUDES[0],
    q011f.AMPLITUDES[1],
    HELDOUT_AMPLITUDE,
    *q011f.AMPLITUDES[2:],
)
ORIGINAL_DEGENERATE_WITNESSES = ((4, 1), (4, 2))


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011e.q011c.OMEGA,
        "eta": q011e.q011c.ETA,
        "selected_dimension": SELECTED_DIMENSION,
        "fixed_conservation_leaf": True,
        "q011e_is_regraded": False,
        "q011e1_is_regraded": False,
        "q011f_is_regraded": False,
        "direction_seed": q011f.DIRECTION_SEED,
        "direction_count": q011f.DIRECTION_COUNT,
        "direction_sha256": Q011F_DIRECTION_SHA256,
        "original_amplitudes": list(q011f.AMPLITUDES),
        "heldout_amplitude": HELDOUT_AMPLITUDE,
        "merged_amplitudes": list(MERGED_AMPLITUDES),
        "maximum_step": q011f.MAXIMUM_STEP,
        "horizons": list(q011f.HORIZONS),
        "heldout_trajectory_count_per_chart": q011f.DIRECTION_COUNT,
        "heldout_step_record_count": q011f.DIRECTION_COUNT * q011f.MAXIMUM_STEP,
        "heldout_checkpoint_record_count": (q011f.DIRECTION_COUNT * len(q011f.HORIZONS)),
        "merged_fit_count": q011f.EXPECTED_FIT_COUNT,
        "slope_noise_floor": q011f.SHADOW_SLOPE_NOISE_FLOOR,
        "thresholds": {
            "linear_shadow_slope_interval": list(q011f.LINEAR_SHADOW_SLOPE_INTERVAL),
            "quadratic_shadow_slope_interval": list(q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL),
            "maximum_checkpoint_quadratic_linear_error_ratio": (
                q011f.MAXIMUM_CHECKPOINT_RESIDUAL_RATIO
            ),
            "maximum_final_quadratic_error_over_initial_amplitude": (
                q011f.MAXIMUM_FINAL_RELATIVE_QUADRATIC_ERROR
            ),
            "minimum_population": 0.0,
            "maximum_global_conservation_drift": q011f.CONSERVATION_TOLERANCE,
        },
        "original_degenerate_witnesses": [
            list(witness) for witness in ORIGINAL_DEGENERATE_WITNESSES
        ],
    }


def _sealed_q011f_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011f.__file__).resolve().parent / "artifacts" / ("q011f_multistep_shadowing.json")
    )
    runner_path = Path(q011f.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    trajectory = cycle["multistep_trajectory_audit"]
    failed_hypotheses = [
        name for name, gate in cycle["hypothesis_gates"].items() if not gate["passed"]
    ]
    degenerate = [
        record
        for record in trajectory["direction_horizon_fit_records"]
        if not record["slope_eligible"]
    ]
    checks = {
        "q011f_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011F_ARTIFACT_SHA256),
        "q011f_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011F_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011F_RUNNER_SHA256
        ),
        "q011f_package_source_sha256_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "q011f_four_digests_match": (
            (
                cycle["input_digest_sha256"],
                cycle["chart_reconstruction_digest_sha256"],
                cycle["trajectory_digest_sha256"],
                cycle["result_digest_sha256"],
            )
            == (
                Q011F_INPUT_DIGEST,
                Q011F_CHART_DIGEST,
                Q011F_TRAJECTORY_DIGEST,
                Q011F_RESULT_DIGEST,
            )
        ),
        "q011f_valid_rejected_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "rejected"
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and failed_hypotheses == ["all_direction_horizon_fits_are_slope_eligible"]
        ),
        "q011f_direction_hash_matches": (trajectory["direction_sha256"] == Q011F_DIRECTION_SHA256),
        "q011f_two_degenerate_witnesses_reproduce": (
            [(record["direction_index"], record["horizon"]) for record in degenerate]
            == list(ORIGINAL_DEGENERATE_WITNESSES)
            and all(
                record["linear_fit_point_count"] == 5
                and record["quadratic_fit_point_count"] == 3
                and record["quadratic_fit_mask"] == [False, False, True, True, True]
                for record in degenerate
            )
        ),
        "q011e1_and_q011e_outcomes_are_preserved": (
            cycle["sealed_q011e1_artifact_audit"]["artifact"]["hypothesis_outcome"] == "accepted"
            and cycle["sealed_q011e1_artifact_audit"]["preserved_q011e_outcome"][
                "hypothesis_outcome"
            ]
            == "rejected"
        ),
        "q011f_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact) and _strict_json_serializable(artifact)
        ),
    }
    audit = {
        "artifact": {
            "filename": artifact_path.name,
            "sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "input_digest_sha256": cycle["input_digest_sha256"],
            "chart_reconstruction_digest_sha256": cycle["chart_reconstruction_digest_sha256"],
            "trajectory_digest_sha256": cycle["trajectory_digest_sha256"],
            "result_digest_sha256": cycle["result_digest_sha256"],
            "direction_sha256": trajectory["direction_sha256"],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
            "failed_hypothesis_gates": failed_hypotheses,
        },
        "degenerate_witnesses": [
            {
                "direction_index": record["direction_index"],
                "horizon": record["horizon"],
                "linear_fit_point_count": record["linear_fit_point_count"],
                "quadratic_fit_point_count": record["quadratic_fit_point_count"],
                "quadratic_fit_mask": record["quadratic_fit_mask"],
                "linear_errors": record["linear_errors"],
                "quadratic_errors": record["quadratic_errors"],
            }
            for record in degenerate
        ],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifact


def _reconstruct_chart_once(
    q011f_artifact: dict[str, Any],
) -> tuple[q011e.RealForcedQuadraticModel, dict[str, Any]]:
    sealed_q011e1, q011e1_artifact = q011f._sealed_q011e1_artifact_audit()
    model, reconstruction = q011f._reconstruct_chart_once(q011e1_artifact)
    stored_cycle = q011f_artifact["cycle"]
    checks = {
        "q011e1_sealed_audit_reproduces": (
            sealed_q011e1 == stored_cycle["sealed_q011e1_artifact_audit"]
        ),
        "q011e_chart_reconstruction_reproduces": (
            reconstruction == stored_cycle["q011e_chart_reconstruction_audit"]
        ),
        "q011f_chart_reconstruction_digest_reproduces": (
            q011e.q011c._canonical_json_sha256({"q011e_chart_reconstruction_audit": reconstruction})
            == Q011F_CHART_DIGEST
        ),
        "six_chart_array_hashes_reproduce": (
            reconstruction["array_hashes"]
            == {
                "real_tangent_sha256": q011e1.REAL_TANGENT_SHA256,
                "real_extractor_sha256": q011e1.REAL_EXTRACTOR_SHA256,
                "real_reduced_linear_sha256": q011e1.REAL_LINEAR_SHA256,
                "analytic_second_derivative_sha256": (q011e1.ANALYTIC_SECOND_DERIVATIVE_SHA256),
                "real_chart_hessian_sha256": q011e1.REAL_CHART_HESSIAN_SHA256,
                "real_reduced_hessian_sha256": (q011e1.REAL_REDUCED_HESSIAN_SHA256),
            }
        ),
        "chart_construction_passes": reconstruction["passed"],
    }
    audit = {
        **reconstruction,
        "q011f_chart_reconstruction_digest_sha256": Q011F_CHART_DIGEST,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return model, q011e._json_native(audit)


def _heldout_trajectory_campaign(
    model: q011e.RealForcedQuadraticModel,
) -> dict[str, Any]:
    generator = np.random.default_rng(q011f.DIRECTION_SEED)
    directions = generator.standard_normal((q011f.DIRECTION_COUNT, SELECTED_DIMENSION))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    base_conserved = global_conserved_quantities(model.base.reshape(SIZE, SIZE, 9))
    horizon_set = set(q011f.HORIZONS)
    trajectories: list[dict[str, Any]] = []

    for direction_index, direction in enumerate(directions):
        initial_coordinate = HELDOUT_AMPLITUDE * direction
        linear_coordinate = initial_coordinate.copy()
        quadratic_coordinate = initial_coordinate.copy()
        linear_full = model.chart(initial_coordinate, quadratic=False)
        quadratic_full = model.chart(initial_coordinate, quadratic=True)
        minimum_population = min(
            float(np.min(linear_full)),
            float(np.min(quadratic_full)),
        )
        maximum_conservation = max(
            q011f._state_conservation_drift(linear_full, base_conserved),
            q011f._state_conservation_drift(quadratic_full, base_conserved),
        )
        steps: list[dict[str, Any]] = []

        for step in range(1, q011f.MAXIMUM_STEP + 1):
            linear_full = model.full_map(linear_full)
            quadratic_full = model.full_map(quadratic_full)
            linear_coordinate = model.reduced_map(linear_coordinate, quadratic=False)
            quadratic_coordinate = model.reduced_map(
                quadratic_coordinate,
                quadratic=True,
            )
            linear_lifted = model.chart(linear_coordinate, quadratic=False)
            quadratic_lifted = model.chart(quadratic_coordinate, quadratic=True)
            linear_error = float(np.linalg.norm(linear_full - linear_lifted))
            quadratic_error = float(np.linalg.norm(quadratic_full - quadratic_lifted))
            states = (
                linear_full,
                linear_lifted,
                quadratic_full,
                quadratic_lifted,
            )
            step_minimum_population = min(float(np.min(state)) for state in states)
            step_maximum_conservation = max(
                q011f._state_conservation_drift(state, base_conserved) for state in states
            )
            minimum_population = min(minimum_population, step_minimum_population)
            maximum_conservation = max(
                maximum_conservation,
                step_maximum_conservation,
            )
            hashes = (
                {
                    "linear_full_state_sha256": q011e.q011c._array_sha256(linear_full),
                    "linear_lifted_state_sha256": q011e.q011c._array_sha256(linear_lifted),
                    "quadratic_full_state_sha256": q011e.q011c._array_sha256(quadratic_full),
                    "quadratic_lifted_state_sha256": q011e.q011c._array_sha256(quadratic_lifted),
                }
                if step in horizon_set
                else None
            )
            steps.append(
                {
                    "step": step,
                    "linear_shadowing_error": linear_error,
                    "quadratic_shadowing_error": quadratic_error,
                    "quadratic_linear_error_ratio": float(
                        quadratic_error / max(linear_error, np.finfo(float).tiny)
                    ),
                    "linear_reduced_coordinate_norm": float(np.linalg.norm(linear_coordinate)),
                    "quadratic_reduced_coordinate_norm": float(
                        np.linalg.norm(quadratic_coordinate)
                    ),
                    "minimum_population": step_minimum_population,
                    "maximum_global_conservation_drift": step_maximum_conservation,
                    "checkpoint_state_hashes": hashes,
                }
            )

        trajectories.append(
            {
                "direction_index": direction_index,
                "amplitude": HELDOUT_AMPLITUDE,
                "initial_coordinate_norm": float(np.linalg.norm(initial_coordinate)),
                "initial_coordinate_sha256": q011e.q011c._array_sha256(initial_coordinate),
                "step_records": steps,
                "minimum_population": minimum_population,
                "maximum_global_conservation_drift": maximum_conservation,
                "maximum_checkpoint_quadratic_linear_error_ratio": max(
                    record["quadratic_linear_error_ratio"]
                    for record in steps
                    if record["step"] in horizon_set
                ),
                "final_quadratic_error_over_initial_amplitude": (
                    steps[-1]["quadratic_shadowing_error"] / HELDOUT_AMPLITUDE
                ),
            }
        )

    step_count = sum(len(record["step_records"]) for record in trajectories)
    checkpoint_count = sum(
        step["checkpoint_state_hashes"] is not None
        for record in trajectories
        for step in record["step_records"]
    )
    minimum_population = min(record["minimum_population"] for record in trajectories)
    maximum_conservation = max(
        record["maximum_global_conservation_drift"] for record in trajectories
    )
    maximum_ratio = max(
        record["maximum_checkpoint_quadratic_linear_error_ratio"] for record in trajectories
    )
    maximum_final_relative_error = max(
        record["final_quadratic_error_over_initial_amplitude"] for record in trajectories
    )
    checks = {
        "q011f_direction_set_reproduces": (
            q011e.q011c._array_sha256(directions) == Q011F_DIRECTION_SHA256
        ),
        "heldout_campaign_is_complete": (
            len(trajectories) == q011f.DIRECTION_COUNT
            and step_count == q011f.DIRECTION_COUNT * q011f.MAXIMUM_STEP
            and checkpoint_count == q011f.DIRECTION_COUNT * len(q011f.HORIZONS)
        ),
        "heldout_amplitude_and_steps_reproduce": all(
            record["amplitude"] == HELDOUT_AMPLITUDE
            and [step["step"] for step in record["step_records"]]
            == list(range(1, q011f.MAXIMUM_STEP + 1))
            for record in trajectories
        ),
        "heldout_values_are_finite": bool(_all_numeric_values_finite(trajectories)),
        "checkpoint_hashes_are_complete": all(
            (
                step["checkpoint_state_hashes"] is not None
                and len(step["checkpoint_state_hashes"]) == 4
                and all(len(value) == 64 for value in step["checkpoint_state_hashes"].values())
            )
            == (step["step"] in horizon_set)
            for record in trajectories
            for step in record["step_records"]
        ),
    }
    return q011e._json_native(
        {
            "direction_seed": q011f.DIRECTION_SEED,
            "direction_count": q011f.DIRECTION_COUNT,
            "direction_sha256": q011e.q011c._array_sha256(directions),
            "heldout_amplitude": HELDOUT_AMPLITUDE,
            "maximum_step": q011f.MAXIMUM_STEP,
            "horizons": list(q011f.HORIZONS),
            "trajectory_count_per_chart": len(trajectories),
            "step_record_count": step_count,
            "checkpoint_record_count": checkpoint_count,
            "trajectory_records": trajectories,
            "minimum_full_or_lifted_population": minimum_population,
            "maximum_global_conservation_drift": maximum_conservation,
            "maximum_checkpoint_quadratic_linear_error_ratio": maximum_ratio,
            "maximum_final_quadratic_error_over_initial_amplitude": (maximum_final_relative_error),
            "checks": checks,
            "passed": all(checks.values()),
        }
    )


def _merged_fit_audit(
    q011f_artifact: dict[str, Any],
    heldout: dict[str, Any],
) -> dict[str, Any]:
    original = q011f_artifact["cycle"]["multistep_trajectory_audit"]
    original_fits = {
        (record["direction_index"], record["horizon"]): record
        for record in original["direction_horizon_fit_records"]
    }
    heldout_trajectories = {
        record["direction_index"]: record for record in heldout["trajectory_records"]
    }
    merged_amplitudes = np.asarray(MERGED_AMPLITUDES, dtype=np.float64)
    records: list[dict[str, Any]] = []

    for direction_index in range(q011f.DIRECTION_COUNT):
        heldout_trajectory = heldout_trajectories[direction_index]
        for horizon in q011f.HORIZONS:
            original_fit = original_fits[(direction_index, horizon)]
            heldout_step = heldout_trajectory["step_records"][horizon - 1]
            linear_errors = [
                original_fit["linear_errors"][0],
                original_fit["linear_errors"][1],
                heldout_step["linear_shadowing_error"],
                *original_fit["linear_errors"][2:],
            ]
            quadratic_errors = [
                original_fit["quadratic_errors"][0],
                original_fit["quadratic_errors"][1],
                heldout_step["quadratic_shadowing_error"],
                *original_fit["quadratic_errors"][2:],
            ]
            linear_array = np.asarray(linear_errors, dtype=np.float64)
            quadratic_array = np.asarray(quadratic_errors, dtype=np.float64)
            linear_mask = linear_array >= q011f.SHADOW_SLOPE_NOISE_FLOOR
            quadratic_mask = quadratic_array >= q011f.SHADOW_SLOPE_NOISE_FLOOR
            linear_count = int(np.count_nonzero(linear_mask))
            quadratic_count = int(np.count_nonzero(quadratic_mask))
            eligible = bool(linear_count >= 4 and quadratic_count >= 4)
            records.append(
                {
                    "direction_index": direction_index,
                    "horizon": horizon,
                    "amplitudes": list(MERGED_AMPLITUDES),
                    "linear_errors": linear_errors,
                    "quadratic_errors": quadratic_errors,
                    "linear_fit_mask": linear_mask.tolist(),
                    "quadratic_fit_mask": quadratic_mask.tolist(),
                    "linear_fit_point_count": linear_count,
                    "quadratic_fit_point_count": quadratic_count,
                    "heldout_linear_point_is_fit_eligible": bool(linear_mask[2]),
                    "heldout_quadratic_point_is_fit_eligible": bool(quadratic_mask[2]),
                    "slope_eligible": eligible,
                    "linear_slope": (
                        float(
                            log_log_slope(
                                merged_amplitudes[linear_mask],
                                linear_array[linear_mask],
                            )
                        )
                        if eligible
                        else 0.0
                    ),
                    "quadratic_slope": (
                        float(
                            log_log_slope(
                                merged_amplitudes[quadratic_mask],
                                quadratic_array[quadratic_mask],
                            )
                        )
                        if eligible
                        else 0.0
                    ),
                    "quadratic_linear_error_ratios": (
                        quadratic_array / np.maximum(linear_array, np.finfo(float).tiny)
                    ).tolist(),
                }
            )

    eligible_records = [record for record in records if record["slope_eligible"]]
    repaired_records = [
        record
        for record in records
        if (record["direction_index"], record["horizon"]) in ORIGINAL_DEGENERATE_WITNESSES
    ]
    minimum_linear_slope = min(
        (record["linear_slope"] for record in eligible_records),
        default=0.0,
    )
    maximum_linear_slope = max(
        (record["linear_slope"] for record in eligible_records),
        default=0.0,
    )
    minimum_quadratic_slope = min(
        (record["quadratic_slope"] for record in eligible_records),
        default=0.0,
    )
    maximum_quadratic_slope = max(
        (record["quadratic_slope"] for record in eligible_records),
        default=0.0,
    )
    maximum_ratio = max(max(record["quadratic_linear_error_ratios"]) for record in records)
    maximum_final_relative_error = max(
        original["maximum_final_quadratic_error_over_initial_amplitude"],
        heldout["maximum_final_quadratic_error_over_initial_amplitude"],
    )
    minimum_population = min(
        original["minimum_full_or_lifted_population"],
        heldout["minimum_full_or_lifted_population"],
    )
    maximum_conservation = max(
        original["maximum_global_conservation_drift"],
        heldout["maximum_global_conservation_drift"],
    )
    checks = {
        "all_224_merged_fits_are_complete": (
            len(records) == q011f.EXPECTED_FIT_COUNT
            and all(
                record["amplitudes"] == list(MERGED_AMPLITUDES)
                and len(record["linear_errors"]) == len(MERGED_AMPLITUDES)
                and len(record["quadratic_errors"]) == len(MERGED_AMPLITUDES)
                for record in records
            )
        ),
        "original_five_errors_are_preserved_exactly": all(
            [record["linear_errors"][0], record["linear_errors"][1], *record["linear_errors"][3:]]
            == original_fits[(record["direction_index"], record["horizon"])]["linear_errors"]
            and [
                record["quadratic_errors"][0],
                record["quadratic_errors"][1],
                *record["quadratic_errors"][3:],
            ]
            == original_fits[(record["direction_index"], record["horizon"])]["quadratic_errors"]
            for record in records
        ),
        "merged_masks_match_registered_floor": all(
            record["linear_fit_mask"]
            == [value >= q011f.SHADOW_SLOPE_NOISE_FLOOR for value in record["linear_errors"]]
            and record["quadratic_fit_mask"]
            == [value >= q011f.SHADOW_SLOPE_NOISE_FLOOR for value in record["quadratic_errors"]]
            for record in records
        ),
        "degenerate_fits_are_not_slope_gated": all(
            (record["linear_fit_point_count"] < 4 or record["quadratic_fit_point_count"] < 4)
            == (not record["slope_eligible"])
            for record in records
        ),
        "all_merged_values_are_finite": bool(_all_numeric_values_finite(records)),
    }
    hypothesis_checks = {
        "two_original_witnesses_are_repaired_by_heldout_points": (
            len(repaired_records) == 2
            and all(
                record["heldout_quadratic_point_is_fit_eligible"]
                and record["quadratic_fit_point_count"] >= 4
                for record in repaired_records
            )
        ),
        "all_direction_horizon_fits_are_slope_eligible": (
            len(eligible_records) == q011f.EXPECTED_FIT_COUNT
        ),
        "linear_shadow_errors_are_second_order": (
            q011f.LINEAR_SHADOW_SLOPE_INTERVAL[0]
            <= minimum_linear_slope
            <= maximum_linear_slope
            <= q011f.LINEAR_SHADOW_SLOPE_INTERVAL[1]
        ),
        "quadratic_shadow_errors_are_third_order": (
            q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL[0]
            <= minimum_quadratic_slope
            <= maximum_quadratic_slope
            <= q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL[1]
        ),
        "merged_checkpoint_and_final_errors_pass": (
            maximum_ratio <= q011f.MAXIMUM_CHECKPOINT_RESIDUAL_RATIO
            and maximum_final_relative_error <= q011f.MAXIMUM_FINAL_RELATIVE_QUADRATIC_ERROR
        ),
        "heldout_and_original_states_are_positive_and_conservative": (
            minimum_population > 0.0 and maximum_conservation <= q011f.CONSERVATION_TOLERANCE
        ),
    }
    return q011e._json_native(
        {
            "original_amplitudes": list(q011f.AMPLITUDES),
            "heldout_amplitude": HELDOUT_AMPLITUDE,
            "merged_amplitudes": list(MERGED_AMPLITUDES),
            "fit_count": len(records),
            "fit_records": records,
            "repaired_witness_records": repaired_records,
            "slope_eligible_direction_horizon_count": len(eligible_records),
            "degenerate_direction_horizon_count": len(records) - len(eligible_records),
            "minimum_linear_shadow_error_slope": minimum_linear_slope,
            "maximum_linear_shadow_error_slope": maximum_linear_slope,
            "minimum_quadratic_shadow_error_slope": minimum_quadratic_slope,
            "maximum_quadratic_shadow_error_slope": maximum_quadratic_slope,
            "maximum_merged_checkpoint_quadratic_linear_error_ratio": (maximum_ratio),
            "maximum_merged_final_quadratic_error_over_initial_amplitude": (
                maximum_final_relative_error
            ),
            "minimum_merged_full_or_lifted_population": minimum_population,
            "maximum_merged_global_conservation_drift": maximum_conservation,
            "checks": checks,
            "structural_passed": all(checks.values()),
            "hypothesis_checks": hypothesis_checks,
            "hypothesis_passed": all(hypothesis_checks.values()),
        }
    )


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "chart_reconstruction_digest_sha256": cycle["chart_reconstruction_digest_sha256"],
        "heldout_trajectory_digest_sha256": cycle["heldout_trajectory_digest_sha256"],
        "merged_fit_digest_sha256": cycle["merged_fit_digest_sha256"],
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


def run_heldout_amplitude_reissue_audit() -> dict[str, Any]:
    """Run the preregistered Q011f1 held-out-amplitude reissue."""

    registered_parameters = _registered_parameters()
    sealed_q011f, q011f_artifact = _sealed_q011f_artifact_audit()
    model, chart_reconstruction = _reconstruct_chart_once(q011f_artifact)
    heldout = _heldout_trajectory_campaign(model)
    merged = _merged_fit_audit(q011f_artifact, heldout)

    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_q011f_artifact_audit": sealed_q011f,
    }
    chart_sections = {
        "q011e_chart_reconstruction_audit": chart_reconstruction,
    }
    heldout_sections = {
        "heldout_trajectory_audit": heldout,
    }
    merged_sections = {
        "merged_fit_audit": merged,
    }
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    chart_digest = q011e.q011c._canonical_json_sha256(chart_sections)
    heldout_digest = q011e.q011c._canonical_json_sha256(heldout_sections)
    merged_digest = q011e.q011c._canonical_json_sha256(merged_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **chart_sections,
        **heldout_sections,
        **merged_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011e.q011c._canonical_json_sha256(input_sections)
        and chart_digest == q011e.q011c._canonical_json_sha256(chart_sections)
        and heldout_digest == q011e.q011c._canonical_json_sha256(heldout_sections)
        and merged_digest == q011e.q011c._canonical_json_sha256(merged_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )
    heldout_checks = heldout["checks"]
    merged_checks = merged["checks"]
    validity_gates = {
        "sealed_q011f_failure_and_prior_outcomes_reproduce": {
            "passed": sealed_q011f["passed"],
            "threshold": (
                "Q011f artifact, runner, package source, four digests, direction "
                "hash, valid/rejected outcome and two witnesses reproduce"
            ),
            "value": sealed_q011f["checks"],
        },
        "q011e_chart_reconstructs_once_without_refitting": {
            "passed": chart_reconstruction["passed"],
            "threshold": (
                "Q011e1/Q011e outcomes, fresh chart construction audit, chart "
                "digest and six array hashes reproduce"
            ),
            "value": chart_reconstruction["checks"],
        },
        "heldout_trajectory_campaign_is_complete": {
            "passed": bool(
                heldout_checks["q011f_direction_set_reproduces"]
                and heldout_checks["heldout_campaign_is_complete"]
                and heldout_checks["heldout_amplitude_and_steps_reproduce"]
            ),
            "threshold": (
                "the Q011f 32-direction set and 32 held-out 4.8e-4 trajectories "
                "through step 64 reproduce completely"
            ),
            "value": {
                "direction_sha256": heldout["direction_sha256"],
                "trajectory_count_per_chart": heldout["trajectory_count_per_chart"],
                "step_record_count": heldout["step_record_count"],
            },
        },
        "heldout_step_and_checkpoint_diagnostics_are_complete": {
            "passed": bool(
                heldout["passed"]
                and heldout_checks["heldout_values_are_finite"]
                and heldout_checks["checkpoint_hashes_are_complete"]
            ),
            "threshold": (
                "all 2,048 held-out step diagnostics and 224 checkpoint hashes "
                "are finite and complete"
            ),
            "value": heldout_checks,
        },
        "six_amplitude_merged_fits_are_complete": {
            "passed": bool(merged["structural_passed"] and all(merged_checks.values())),
            "threshold": (
                "the original five Q011f errors remain exact and all 224 six-"
                "amplitude merged masks, slopes and ratios are complete"
            ),
            "value": merged_checks,
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "strict finite JSON plus deterministic input/chart/heldout/merged "
                "digests and newline-normalized runner SHA-256"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    raw_hypotheses = merged["hypothesis_checks"]
    hypothesis_gates = {
        "two_original_witnesses_are_repaired_by_heldout_points": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["two_original_witnesses_are_repaired_by_heldout_points"]
            ),
            "threshold": (
                "both original witnesses include the held-out quadratic point "
                "above 1e-12 and have at least four fit points"
            ),
            "value": merged["repaired_witness_records"],
        },
        "all_direction_horizon_fits_are_slope_eligible": {
            "passed": bool(
                validity_passed and raw_hypotheses["all_direction_horizon_fits_are_slope_eligible"]
            ),
            "threshold": "224 / 224 merged direction-horizon fits are slope eligible",
            "value": merged["slope_eligible_direction_horizon_count"],
        },
        "linear_shadow_errors_are_second_order": {
            "passed": bool(
                validity_passed and raw_hypotheses["linear_shadow_errors_are_second_order"]
            ),
            "threshold": "all eligible merged linear slopes are in [1.75, 2.25]",
            "value": [
                merged["minimum_linear_shadow_error_slope"],
                merged["maximum_linear_shadow_error_slope"],
            ],
        },
        "quadratic_shadow_errors_are_third_order": {
            "passed": bool(
                validity_passed and raw_hypotheses["quadratic_shadow_errors_are_third_order"]
            ),
            "threshold": "all eligible merged quadratic slopes are in [2.50, 3.50]",
            "value": [
                merged["minimum_quadratic_shadow_error_slope"],
                merged["maximum_quadratic_shadow_error_slope"],
            ],
        },
        "merged_checkpoint_and_final_errors_pass": {
            "passed": bool(
                validity_passed and raw_hypotheses["merged_checkpoint_and_final_errors_pass"]
            ),
            "threshold": (
                "all merged checkpoint ratios <=0.05 and all horizon-64 "
                "quadratic errors / initial amplitudes <=1e-3"
            ),
            "value": {
                "maximum_checkpoint_ratio": merged[
                    "maximum_merged_checkpoint_quadratic_linear_error_ratio"
                ],
                "maximum_final_relative_error": merged[
                    "maximum_merged_final_quadratic_error_over_initial_amplitude"
                ],
            },
        },
        "heldout_and_original_positivity_and_conservation_hold": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["heldout_and_original_states_are_positive_and_conservative"]
            ),
            "threshold": ("merged minimum population >0 and maximum conservation drift <=1e-10"),
            "value": {
                "minimum_population": merged["minimum_merged_full_or_lifted_population"],
                "maximum_global_conservation_drift": merged[
                    "maximum_merged_global_conservation_drift"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011f1 held-out-amplitude reissue is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the forced quadratic chart passes a held-out-amplitude 64-step shadowing reissue"
        )
    else:
        outcome = "rejected"
        classification = (
            "the held-out amplitude does not repair the registered finite shadowing window"
        )

    cycle: dict[str, Any] = q011e._json_native(
        {
            "question": (
                "Does one held-out midpoint amplitude repair all 224 fits in the "
                "sealed Q011f 64-step shadowing window?"
            ),
            **pre_gate_sections,
            "input_digest_sha256": input_digest,
            "chart_reconstruction_digest_sha256": chart_digest,
            "heldout_trajectory_digest_sha256": heldout_digest,
            "merged_fit_digest_sha256": merged_digest,
            "validity_gates": validity_gates,
            "hypothesis_gates": hypothesis_gates,
            "study_validity": "passed" if validity_passed else "failed",
            "hypothesis_outcome": outcome,
            "scientific_classification": classification,
        }
    )
    result_digest = q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["numerical_consequence"] = {
        "q011f_original_rejected_outcome_changed": False,
        "q011e1_accepted_residual_window_changed": False,
        "q011e_original_rejected_outcome_changed": False,
        "heldout_amplitude_reissue_confirms_finite_shadowing_window": bool(
            validity_passed and hypotheses_passed
        ),
        "all_time_shadowing_is_certified": False,
        "uniform_taylor_remainder_is_certified": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
        "tt_compression_is_evaluated": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 six-amplitude reissue formed from the "
        "sealed Q011f five-node data plus 32 held-out 4.8e-4 trajectories, 64 "
        "steps and seven horizons. It does not regrade Q011f, give an all-time "
        "shadowing lemma, uniform remainder, basin, nonlinear normal attraction, "
        "forced SSM existence or uniqueness, evaluate TT compression, or cover "
        "other grids, forces or wall boundaries."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011f_rejected_outcome_changed": False,
        "q011e1_accepted_outcome_changed": False,
        "q011e_rejected_outcome_changed": False,
        "q011d_accepted_prequalification_changed": False,
        "q011c2_accepted_cluster_selection_changed": False,
        "q011c_original_inconclusive_outcome_changed": False,
        "q011b_accepted_fixed_point_changed": False,
        "q011a_nonzero_mean_obstruction_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011g for natural Fourier-sparse storage and TT-SVD comparison "
        "of the sealed forced quadratic coefficient tensors."
        if outcome == "accepted"
        else (
            "Localize the first failed held-out repair, merged eligibility, slope, "
            "performance, positivity or conservation gate."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011f1 cycle failed strict serialization or digest")
    return cycle


def run_q011f1_study() -> dict[str, Any]:
    cycle = run_heldout_amplitude_reissue_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 held-out-amplitude reissue of the sealed finite "
                "multi-step forced-chart shadowing window"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011e.q011c.OMEGA,
            "eta": q011e.q011c.ETA,
            "selected_real_dimension": SELECTED_DIMENSION,
            "direction_count": q011f.DIRECTION_COUNT,
            "heldout_amplitude": HELDOUT_AMPLITUDE,
            "merged_amplitude_count": len(MERGED_AMPLITUDES),
            "heldout_trajectory_count_per_chart": q011f.DIRECTION_COUNT,
            "maximum_step": q011f.MAXIMUM_STEP,
            "horizons": list(q011f.HORIZONS),
            "q011f_is_regraded": False,
            "claim": (
                "finite held-out-amplitude shadowing reissue only; no all-time "
                "shadowing, basin, forced-SSM or nonlinear-attraction claim"
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
    result = run_q011f1_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
