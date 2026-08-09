"""Sealed Q011f independent multi-step forced-chart shadowing window."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

import research.q011e1_enlarged_residual_window as q011e1
from ttim_lbm.d2q9 import global_conserved_quantities
from ttim_lbm.manifold import log_log_slope
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011e = q011e1.q011e
SIZE = q011e.SIZE
SELECTED_DIMENSION = q011e.SELECTED_DIMENSION

Q011E1_ARTIFACT_SHA256 = "989801d1e4e1396ebba279e11c396f7f6d4e9616d2aa170f5687f9ba08a95840"
Q011E1_RUNNER_SHA256 = "bb8a052f387d2748fee823af10f2ab4ea4a9a08ebe62e8b4ff87d68d55c2929f"
Q011E1_INPUT_DIGEST = "8e979deeed0e5f4151addb5f3b06c1a9815a28f4e0c5762726d7c29a03d035c0"
Q011E1_CHART_DIGEST = "2e739657032352d7d0496568a216b761000a68beb6d00749e1e427e6447598fb"
Q011E1_RESIDUAL_DIGEST = "20267150710538f797f21cc2846ee6be14060ad9ea6bef98ef29e4731121410b"
Q011E1_RESULT_DIGEST = "0370a24ce7a74da71ee978b3892ea23412c3d18adb110e2b2b53aaf02ccdf039"
Q011E1_DIRECTION_SHA256 = "64b017fb5a3c55378ccee4d457b4d2a8c75a92cd5b421897f9b7de1ad6a77b1d"
SEALED_PACKAGE_SOURCE_SHA256 = q011e1.SEALED_PACKAGE_SOURCE_SHA256

DIRECTION_SEED = 20260826
DIRECTION_COUNT = 32
AMPLITUDES = q011e1.AMPLITUDES
MAXIMUM_STEP = 64
HORIZONS = (1, 2, 4, 8, 16, 32, 64)
SHADOW_SLOPE_NOISE_FLOOR = 1.0e-12
EXPECTED_FIT_COUNT = DIRECTION_COUNT * len(HORIZONS)
LINEAR_SHADOW_SLOPE_INTERVAL = (1.75, 2.25)
QUADRATIC_SHADOW_SLOPE_INTERVAL = (2.50, 3.50)
MAXIMUM_CHECKPOINT_RESIDUAL_RATIO = 0.05
MAXIMUM_FINAL_RELATIVE_QUADRATIC_ERROR = 1.0e-3
CONSERVATION_TOLERANCE = q011e.CONSERVATION_TOLERANCE


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
        "zero_wave_center_coordinates_included": False,
        "q011e_is_regraded": False,
        "q011e1_is_regraded": False,
        "trajectory_campaign": {
            "seed": DIRECTION_SEED,
            "direction_count": DIRECTION_COUNT,
            "amplitudes": list(AMPLITUDES),
            "maximum_step": MAXIMUM_STEP,
            "horizons": list(HORIZONS),
            "trajectory_count_per_chart": DIRECTION_COUNT * len(AMPLITUDES),
            "step_record_count": DIRECTION_COUNT * len(AMPLITUDES) * MAXIMUM_STEP,
            "checkpoint_record_count": (DIRECTION_COUNT * len(AMPLITUDES) * len(HORIZONS)),
            "slope_fit_count": EXPECTED_FIT_COUNT,
            "slope_noise_floor": SHADOW_SLOPE_NOISE_FLOOR,
        },
        "thresholds": {
            "linear_shadow_slope_interval": list(LINEAR_SHADOW_SLOPE_INTERVAL),
            "quadratic_shadow_slope_interval": list(QUADRATIC_SHADOW_SLOPE_INTERVAL),
            "maximum_checkpoint_quadratic_linear_error_ratio": (MAXIMUM_CHECKPOINT_RESIDUAL_RATIO),
            "maximum_final_quadratic_error_over_initial_amplitude": (
                MAXIMUM_FINAL_RELATIVE_QUADRATIC_ERROR
            ),
            "minimum_population": 0.0,
            "maximum_global_conservation_drift": CONSERVATION_TOLERANCE,
        },
        "initial_state_semantics": {
            "same_reduced_coordinate": True,
            "same_physical_state_across_linear_and_quadratic_charts": False,
            "linear_full_initial_state": "W_linear(a0)",
            "quadratic_full_initial_state": "W_quadratic(a0)",
        },
    }


def _sealed_q011e1_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011e1.__file__).resolve().parent
        / "artifacts"
        / ("q011e1_enlarged_residual_window.json")
    )
    runner_path = Path(q011e1.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = (
        cycle["input_digest_sha256"],
        cycle["chart_reconstruction_digest_sha256"],
        cycle["residual_window_digest_sha256"],
        cycle["result_digest_sha256"],
    )
    checks = {
        "q011e1_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011E1_ARTIFACT_SHA256),
        "q011e1_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011E1_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011E1_RUNNER_SHA256
        ),
        "q011e1_package_source_sha256_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "q011e1_four_digests_match": (
            digests
            == (
                Q011E1_INPUT_DIGEST,
                Q011E1_CHART_DIGEST,
                Q011E1_RESIDUAL_DIGEST,
                Q011E1_RESULT_DIGEST,
            )
        ),
        "q011e1_accepted_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and cycle["scientific_classification"]
            == (
                "the independent enlarged window resolves second- and third-order "
                "forced chart residuals"
            )
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        ),
        "q011e1_direction_hash_matches": (
            cycle["enlarged_residual_window_audit"]["direction_sha256"] == Q011E1_DIRECTION_SHA256
        ),
        "q011e_original_outcome_remains_rejected": (
            not cycle["numerical_consequence"]["q011e_original_rejected_outcome_changed"]
            and not cycle["numerical_consequence"]["q011e_original_residual_campaign_regraded"]
            and cycle["sealed_q011e_artifact_audit"]["artifact"]["hypothesis_outcome"] == "rejected"
        ),
        "q011e1_artifact_is_strict_finite_json": bool(
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
            "residual_window_digest_sha256": cycle["residual_window_digest_sha256"],
            "result_digest_sha256": cycle["result_digest_sha256"],
            "direction_sha256": cycle["enlarged_residual_window_audit"]["direction_sha256"],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        },
        "preserved_q011e_outcome": {
            "study_validity": cycle["sealed_q011e_artifact_audit"]["artifact"]["study_validity"],
            "hypothesis_outcome": cycle["sealed_q011e_artifact_audit"]["artifact"][
                "hypothesis_outcome"
            ],
            "failed_hypothesis_gates": cycle["sealed_q011e_artifact_audit"]["artifact"][
                "failed_hypothesis_gates"
            ],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifact


def _reconstruct_chart_once(
    q011e1_artifact: dict[str, Any],
) -> tuple[q011e.RealForcedQuadraticModel, dict[str, Any]]:
    sealed_q011e, q011e_artifact = q011e1._sealed_q011e_artifact_audit()
    model, reconstruction = q011e1._reconstruct_q011e_chart(q011e_artifact)
    stored_cycle = q011e1_artifact["cycle"]
    checks = {
        "q011e_sealed_input_audit_reproduces": (
            sealed_q011e == stored_cycle["sealed_q011e_artifact_audit"]
        ),
        "q011e_chart_reconstruction_audit_reproduces": (
            reconstruction == stored_cycle["q011e_chart_reconstruction_audit"]
        ),
        "q011e_chart_reconstruction_digest_reproduces": (
            q011e.q011c._canonical_json_sha256({"q011e_chart_reconstruction_audit": reconstruction})
            == Q011E1_CHART_DIGEST
        ),
        "q011e_six_array_hashes_reproduce": (
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
        "q011e_chart_construction_passes": reconstruction["passed"],
    }
    audit = {
        **reconstruction,
        "q011e1_chart_reconstruction_digest_sha256": Q011E1_CHART_DIGEST,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return model, q011e._json_native(audit)


def _state_conservation_drift(
    state: np.ndarray,
    base_conserved: np.ndarray,
) -> float:
    return float(
        np.linalg.norm(global_conserved_quantities(state.reshape(SIZE, SIZE, 9)) - base_conserved)
    )


def _trajectory_campaign(
    model: q011e.RealForcedQuadraticModel,
) -> dict[str, Any]:
    generator = np.random.default_rng(DIRECTION_SEED)
    directions = generator.standard_normal((DIRECTION_COUNT, SELECTED_DIMENSION))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    base_conserved = global_conserved_quantities(model.base.reshape(SIZE, SIZE, 9))
    horizon_set = set(HORIZONS)
    trajectories: list[dict[str, Any]] = []

    for direction_index, direction in enumerate(directions):
        for amplitude_index, amplitude in enumerate(AMPLITUDES):
            initial_coordinate = amplitude * direction
            linear_coordinate = initial_coordinate.copy()
            quadratic_coordinate = initial_coordinate.copy()
            linear_full = model.chart(initial_coordinate, quadratic=False)
            quadratic_full = model.chart(initial_coordinate, quadratic=True)
            initial_states = (linear_full, quadratic_full)
            minimum_population = min(float(np.min(state)) for state in initial_states)
            maximum_conservation = max(
                _state_conservation_drift(state, base_conserved) for state in initial_states
            )
            maximum_linear_coordinate_norm = float(np.linalg.norm(linear_coordinate))
            maximum_quadratic_coordinate_norm = float(np.linalg.norm(quadratic_coordinate))
            steps: list[dict[str, Any]] = []

            for step in range(1, MAXIMUM_STEP + 1):
                linear_full = model.full_map(linear_full)
                quadratic_full = model.full_map(quadratic_full)
                linear_coordinate = model.reduced_map(
                    linear_coordinate,
                    quadratic=False,
                )
                quadratic_coordinate = model.reduced_map(
                    quadratic_coordinate,
                    quadratic=True,
                )
                linear_lifted = model.chart(linear_coordinate, quadratic=False)
                quadratic_lifted = model.chart(quadratic_coordinate, quadratic=True)
                linear_error = float(np.linalg.norm(linear_full - linear_lifted))
                quadratic_error = float(np.linalg.norm(quadratic_full - quadratic_lifted))
                ratio = quadratic_error / max(linear_error, np.finfo(float).tiny)
                states = (
                    linear_full,
                    linear_lifted,
                    quadratic_full,
                    quadratic_lifted,
                )
                step_minimum_population = min(float(np.min(state)) for state in states)
                step_maximum_conservation = max(
                    _state_conservation_drift(state, base_conserved) for state in states
                )
                linear_coordinate_norm = float(np.linalg.norm(linear_coordinate))
                quadratic_coordinate_norm = float(np.linalg.norm(quadratic_coordinate))
                minimum_population = min(
                    minimum_population,
                    step_minimum_population,
                )
                maximum_conservation = max(
                    maximum_conservation,
                    step_maximum_conservation,
                )
                maximum_linear_coordinate_norm = max(
                    maximum_linear_coordinate_norm,
                    linear_coordinate_norm,
                )
                maximum_quadratic_coordinate_norm = max(
                    maximum_quadratic_coordinate_norm,
                    quadratic_coordinate_norm,
                )
                checkpoint_hashes = (
                    {
                        "linear_full_state_sha256": q011e.q011c._array_sha256(linear_full),
                        "linear_lifted_state_sha256": q011e.q011c._array_sha256(linear_lifted),
                        "quadratic_full_state_sha256": q011e.q011c._array_sha256(quadratic_full),
                        "quadratic_lifted_state_sha256": q011e.q011c._array_sha256(
                            quadratic_lifted
                        ),
                    }
                    if step in horizon_set
                    else None
                )
                steps.append(
                    {
                        "step": step,
                        "linear_shadowing_error": linear_error,
                        "quadratic_shadowing_error": quadratic_error,
                        "quadratic_linear_error_ratio": float(ratio),
                        "linear_reduced_coordinate_norm": linear_coordinate_norm,
                        "quadratic_reduced_coordinate_norm": quadratic_coordinate_norm,
                        "minimum_population": step_minimum_population,
                        "maximum_global_conservation_drift": (step_maximum_conservation),
                        "checkpoint_state_hashes": checkpoint_hashes,
                    }
                )

            final_record = steps[-1]
            trajectories.append(
                {
                    "direction_index": direction_index,
                    "amplitude_index": amplitude_index,
                    "amplitude": amplitude,
                    "initial_coordinate_norm": float(np.linalg.norm(initial_coordinate)),
                    "initial_coordinate_sha256": q011e.q011c._array_sha256(initial_coordinate),
                    "step_records": steps,
                    "minimum_population": minimum_population,
                    "maximum_global_conservation_drift": maximum_conservation,
                    "maximum_linear_reduced_coordinate_norm": (maximum_linear_coordinate_norm),
                    "maximum_quadratic_reduced_coordinate_norm": (
                        maximum_quadratic_coordinate_norm
                    ),
                    "maximum_checkpoint_quadratic_linear_error_ratio": max(
                        record["quadratic_linear_error_ratio"]
                        for record in steps
                        if record["step"] in horizon_set
                    ),
                    "final_quadratic_error_over_initial_amplitude": (
                        final_record["quadratic_shadowing_error"] / amplitude
                    ),
                }
            )

    fits: list[dict[str, Any]] = []
    amplitudes_array = np.asarray(AMPLITUDES, dtype=np.float64)
    for direction_index in range(DIRECTION_COUNT):
        direction_trajectories = sorted(
            (record for record in trajectories if record["direction_index"] == direction_index),
            key=lambda record: record["amplitude_index"],
        )
        for horizon in HORIZONS:
            linear_errors = np.asarray(
                [
                    record["step_records"][horizon - 1]["linear_shadowing_error"]
                    for record in direction_trajectories
                ],
                dtype=np.float64,
            )
            quadratic_errors = np.asarray(
                [
                    record["step_records"][horizon - 1]["quadratic_shadowing_error"]
                    for record in direction_trajectories
                ],
                dtype=np.float64,
            )
            linear_mask = linear_errors >= SHADOW_SLOPE_NOISE_FLOOR
            quadratic_mask = quadratic_errors >= SHADOW_SLOPE_NOISE_FLOOR
            eligible = bool(
                np.count_nonzero(linear_mask) >= 4 and np.count_nonzero(quadratic_mask) >= 4
            )
            fits.append(
                {
                    "direction_index": direction_index,
                    "horizon": horizon,
                    "linear_errors": linear_errors.tolist(),
                    "quadratic_errors": quadratic_errors.tolist(),
                    "linear_fit_mask": linear_mask.tolist(),
                    "quadratic_fit_mask": quadratic_mask.tolist(),
                    "linear_fit_point_count": int(np.count_nonzero(linear_mask)),
                    "quadratic_fit_point_count": int(np.count_nonzero(quadratic_mask)),
                    "slope_eligible": eligible,
                    "linear_slope": (
                        float(
                            log_log_slope(
                                amplitudes_array[linear_mask],
                                linear_errors[linear_mask],
                            )
                        )
                        if eligible
                        else 0.0
                    ),
                    "quadratic_slope": (
                        float(
                            log_log_slope(
                                amplitudes_array[quadratic_mask],
                                quadratic_errors[quadratic_mask],
                            )
                        )
                        if eligible
                        else 0.0
                    ),
                    "quadratic_linear_error_ratios": (
                        quadratic_errors / np.maximum(linear_errors, np.finfo(float).tiny)
                    ).tolist(),
                }
            )

    eligible_fits = [record for record in fits if record["slope_eligible"]]
    minimum_linear_slope = min(
        (record["linear_slope"] for record in eligible_fits),
        default=0.0,
    )
    maximum_linear_slope = max(
        (record["linear_slope"] for record in eligible_fits),
        default=0.0,
    )
    minimum_quadratic_slope = min(
        (record["quadratic_slope"] for record in eligible_fits),
        default=0.0,
    )
    maximum_quadratic_slope = max(
        (record["quadratic_slope"] for record in eligible_fits),
        default=0.0,
    )
    maximum_checkpoint_ratio = max(
        record["maximum_checkpoint_quadratic_linear_error_ratio"] for record in trajectories
    )
    maximum_final_relative_error = max(
        record["final_quadratic_error_over_initial_amplitude"] for record in trajectories
    )
    minimum_population = min(record["minimum_population"] for record in trajectories)
    maximum_conservation = max(
        record["maximum_global_conservation_drift"] for record in trajectories
    )
    maximum_linear_coordinate_amplification = max(
        record["maximum_linear_reduced_coordinate_norm"] / record["amplitude"]
        for record in trajectories
    )
    maximum_quadratic_coordinate_amplification = max(
        record["maximum_quadratic_reduced_coordinate_norm"] / record["amplitude"]
        for record in trajectories
    )
    step_record_count = sum(len(record["step_records"]) for record in trajectories)
    checkpoint_record_count = sum(
        record["checkpoint_state_hashes"] is not None
        for trajectory in trajectories
        for record in trajectory["step_records"]
    )
    checks = {
        "registered_trajectory_campaign_is_complete": (
            len(trajectories) == DIRECTION_COUNT * len(AMPLITUDES)
            and step_record_count == DIRECTION_COUNT * len(AMPLITUDES) * MAXIMUM_STEP
            and checkpoint_record_count == DIRECTION_COUNT * len(AMPLITUDES) * len(HORIZONS)
        ),
        "directions_are_finite_and_unit_normalized": bool(
            np.all(np.isfinite(directions))
            and np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0)) <= 1.0e-14
        ),
        "registered_amplitudes_and_steps_reproduce": all(
            record["amplitude"] == AMPLITUDES[record["amplitude_index"]]
            and [step["step"] for step in record["step_records"]]
            == list(range(1, MAXIMUM_STEP + 1))
            for record in trajectories
        ),
        "all_trajectory_values_are_finite": bool(_all_numeric_values_finite(trajectories)),
        "checkpoint_hashes_are_complete": all(
            (
                record["checkpoint_state_hashes"] is not None
                and len(record["checkpoint_state_hashes"]) == 4
                and all(len(value) == 64 for value in record["checkpoint_state_hashes"].values())
            )
            == (record["step"] in horizon_set)
            for trajectory in trajectories
            for record in trajectory["step_records"]
        ),
        "all_direction_horizon_fits_are_complete": (
            len(fits) == EXPECTED_FIT_COUNT
            and all(
                len(record["linear_errors"]) == len(AMPLITUDES)
                and len(record["quadratic_errors"]) == len(AMPLITUDES)
                for record in fits
            )
        ),
        "fit_masks_match_the_registered_noise_floor": all(
            record["linear_fit_mask"]
            == [value >= SHADOW_SLOPE_NOISE_FLOOR for value in record["linear_errors"]]
            and record["quadratic_fit_mask"]
            == [value >= SHADOW_SLOPE_NOISE_FLOOR for value in record["quadratic_errors"]]
            for record in fits
        ),
        "degenerate_fits_are_not_slope_gated": all(
            (record["linear_fit_point_count"] < 4 or record["quadratic_fit_point_count"] < 4)
            == (not record["slope_eligible"])
            for record in fits
        ),
    }
    hypothesis_checks = {
        "all_direction_horizon_fits_are_slope_eligible": (len(eligible_fits) == EXPECTED_FIT_COUNT),
        "linear_shadow_errors_are_second_order": (
            LINEAR_SHADOW_SLOPE_INTERVAL[0]
            <= minimum_linear_slope
            <= maximum_linear_slope
            <= LINEAR_SHADOW_SLOPE_INTERVAL[1]
        ),
        "quadratic_shadow_errors_are_third_order": (
            QUADRATIC_SHADOW_SLOPE_INTERVAL[0]
            <= minimum_quadratic_slope
            <= maximum_quadratic_slope
            <= QUADRATIC_SHADOW_SLOPE_INTERVAL[1]
        ),
        "quadratic_error_improves_at_every_checkpoint": (
            maximum_checkpoint_ratio <= MAXIMUM_CHECKPOINT_RESIDUAL_RATIO
        ),
        "final_quadratic_error_is_within_relative_cap": (
            maximum_final_relative_error <= MAXIMUM_FINAL_RELATIVE_QUADRATIC_ERROR
        ),
        "all_states_are_positive_and_conservation_drift_is_bounded": (
            minimum_population > 0.0 and maximum_conservation <= CONSERVATION_TOLERANCE
        ),
    }
    return q011e._json_native(
        {
            "seed": DIRECTION_SEED,
            "direction_count": DIRECTION_COUNT,
            "direction_sha256": q011e.q011c._array_sha256(directions),
            "amplitudes": list(AMPLITUDES),
            "maximum_step": MAXIMUM_STEP,
            "horizons": list(HORIZONS),
            "slope_noise_floor": SHADOW_SLOPE_NOISE_FLOOR,
            "trajectory_count_per_chart": len(trajectories),
            "step_record_count": step_record_count,
            "checkpoint_record_count": checkpoint_record_count,
            "trajectory_records": trajectories,
            "direction_horizon_fit_records": fits,
            "slope_eligible_direction_horizon_count": len(eligible_fits),
            "degenerate_direction_horizon_count": len(fits) - len(eligible_fits),
            "minimum_linear_shadow_error_slope": minimum_linear_slope,
            "maximum_linear_shadow_error_slope": maximum_linear_slope,
            "minimum_quadratic_shadow_error_slope": minimum_quadratic_slope,
            "maximum_quadratic_shadow_error_slope": maximum_quadratic_slope,
            "maximum_checkpoint_quadratic_linear_error_ratio": (maximum_checkpoint_ratio),
            "maximum_final_quadratic_error_over_initial_amplitude": (maximum_final_relative_error),
            "minimum_full_or_lifted_population": minimum_population,
            "maximum_global_conservation_drift": maximum_conservation,
            "maximum_linear_reduced_coordinate_amplification": (
                maximum_linear_coordinate_amplification
            ),
            "maximum_quadratic_reduced_coordinate_amplification": (
                maximum_quadratic_coordinate_amplification
            ),
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
        "trajectory_digest_sha256": cycle["trajectory_digest_sha256"],
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


def run_multistep_shadowing_audit() -> dict[str, Any]:
    """Run the preregistered Q011f finite multi-step shadowing audit."""

    registered_parameters = _registered_parameters()
    sealed_q011e1, q011e1_artifact = _sealed_q011e1_artifact_audit()
    model, chart_reconstruction = _reconstruct_chart_once(q011e1_artifact)
    trajectory = _trajectory_campaign(model)

    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_q011e1_artifact_audit": sealed_q011e1,
    }
    chart_sections = {
        "q011e_chart_reconstruction_audit": chart_reconstruction,
    }
    trajectory_sections = {
        "multistep_trajectory_audit": trajectory,
    }
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    chart_digest = q011e.q011c._canonical_json_sha256(chart_sections)
    trajectory_digest = q011e.q011c._canonical_json_sha256(trajectory_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **chart_sections,
        **trajectory_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011e.q011c._canonical_json_sha256(input_sections)
        and chart_digest == q011e.q011c._canonical_json_sha256(chart_sections)
        and trajectory_digest == q011e.q011c._canonical_json_sha256(trajectory_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )
    trajectory_checks = trajectory["checks"]
    validity_gates = {
        "sealed_q011e1_and_q011e_outcomes_reproduce": {
            "passed": sealed_q011e1["passed"],
            "threshold": (
                "Q011e1 artifact, runner, package source, four digests, accepted "
                "outcome and direction hash reproduce while Q011e remains rejected"
            ),
            "value": sealed_q011e1["checks"],
        },
        "q011e_chart_reconstructs_once_without_refitting": {
            "passed": chart_reconstruction["passed"],
            "threshold": (
                "fresh Q011e sealed input, construction audit, chart digest and "
                "six array hashes reproduce"
            ),
            "value": chart_reconstruction["checks"],
        },
        "registered_trajectory_campaign_is_complete": {
            "passed": bool(
                trajectory_checks["registered_trajectory_campaign_is_complete"]
                and trajectory_checks["directions_are_finite_and_unit_normalized"]
                and trajectory_checks["registered_amplitudes_and_steps_reproduce"]
            ),
            "threshold": (
                "seed 20260826, 32 unit directions, five amplitudes, 160 trajectories "
                "per chart and all 64 steps are complete"
            ),
            "value": {
                "direction_count": trajectory["direction_count"],
                "direction_sha256": trajectory["direction_sha256"],
                "trajectory_count_per_chart": trajectory["trajectory_count_per_chart"],
                "step_record_count": trajectory["step_record_count"],
            },
        },
        "all_step_and_checkpoint_diagnostics_are_complete": {
            "passed": bool(
                trajectory_checks["all_trajectory_values_are_finite"]
                and trajectory_checks["checkpoint_hashes_are_complete"]
            ),
            "threshold": (
                "all 10,240 step diagnostics and 1,120 checkpoint state-hash "
                "records are finite and complete"
            ),
            "value": {
                "step_record_count": trajectory["step_record_count"],
                "checkpoint_record_count": trajectory["checkpoint_record_count"],
            },
        },
        "all_direction_horizon_fits_are_complete": {
            "passed": bool(
                trajectory_checks["all_direction_horizon_fits_are_complete"]
                and trajectory_checks["fit_masks_match_the_registered_noise_floor"]
                and trajectory_checks["degenerate_fits_are_not_slope_gated"]
            ),
            "threshold": (
                "all 224 direction-horizon error arrays, masks, slopes and ratios "
                "are complete under the 1e-12 fit floor"
            ),
            "value": {
                key: trajectory_checks[key]
                for key in (
                    "all_direction_horizon_fits_are_complete",
                    "fit_masks_match_the_registered_noise_floor",
                    "degenerate_fits_are_not_slope_gated",
                )
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "strict finite JSON plus deterministic input/chart/trajectory "
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
    raw_hypotheses = trajectory["hypothesis_checks"]
    hypothesis_gates = {
        "all_direction_horizon_fits_are_slope_eligible": {
            "passed": bool(
                validity_passed and raw_hypotheses["all_direction_horizon_fits_are_slope_eligible"]
            ),
            "threshold": "224 / 224 direction-horizon fits are slope eligible",
            "value": trajectory["slope_eligible_direction_horizon_count"],
        },
        "linear_shadow_errors_are_second_order": {
            "passed": bool(
                validity_passed and raw_hypotheses["linear_shadow_errors_are_second_order"]
            ),
            "threshold": "all eligible linear slopes are in [1.75, 2.25]",
            "value": [
                trajectory["minimum_linear_shadow_error_slope"],
                trajectory["maximum_linear_shadow_error_slope"],
            ],
        },
        "quadratic_shadow_errors_are_third_order": {
            "passed": bool(
                validity_passed and raw_hypotheses["quadratic_shadow_errors_are_third_order"]
            ),
            "threshold": "all eligible quadratic slopes are in [2.50, 3.50]",
            "value": [
                trajectory["minimum_quadratic_shadow_error_slope"],
                trajectory["maximum_quadratic_shadow_error_slope"],
            ],
        },
        "quadratic_error_improves_at_every_checkpoint": {
            "passed": bool(
                validity_passed and raw_hypotheses["quadratic_error_improves_at_every_checkpoint"]
            ),
            "threshold": "every checkpoint quadratic/linear error ratio <=0.05",
            "value": trajectory["maximum_checkpoint_quadratic_linear_error_ratio"],
        },
        "final_quadratic_error_is_within_relative_cap": {
            "passed": bool(
                validity_passed and raw_hypotheses["final_quadratic_error_is_within_relative_cap"]
            ),
            "threshold": "every horizon-64 quadratic error / initial amplitude <=1e-3",
            "value": trajectory["maximum_final_quadratic_error_over_initial_amplitude"],
        },
        "positivity_and_conservation_hold": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["all_states_are_positive_and_conservation_drift_is_bounded"]
            ),
            "threshold": "minimum population >0 and maximum conservation drift <=1e-10",
            "value": {
                "minimum_population": trajectory["minimum_full_or_lifted_population"],
                "maximum_global_conservation_drift": trajectory[
                    "maximum_global_conservation_drift"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011f multi-step shadowing audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the sealed forced quadratic chart passes the registered 64-step shadowing window"
        )
    else:
        outcome = "rejected"
        classification = "the forced quadratic chart fails the registered finite shadowing window"

    cycle: dict[str, Any] = q011e._json_native(
        {
            "question": (
                "Does the sealed forced quadratic chart pass an independent "
                "64-step finite shadowing window?"
            ),
            **pre_gate_sections,
            "input_digest_sha256": input_digest,
            "chart_reconstruction_digest_sha256": chart_digest,
            "trajectory_digest_sha256": trajectory_digest,
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
        "q011e_original_rejected_outcome_changed": False,
        "q011e1_accepted_residual_window_changed": False,
        "q011e_dense_quadratic_chart_changed": False,
        "registered_finite_multistep_shadowing_window_passes": bool(
            validity_passed and hypotheses_passed
        ),
        "all_time_shadowing_is_certified": False,
        "uniform_taylor_remainder_is_certified": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
        "tt_compression_is_evaluated": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 finite shadowing campaign for 160 "
        "same-chart initial conditions, 64 steps and seven registered horizons "
        "on one 17x17 forced endpoint. It does not give an all-time shadowing "
        "lemma, uniform Taylor remainder, basin, nonlinear normal attraction, "
        "forced SSM existence or uniqueness, evaluate TT compression, or cover "
        "other grids, forces or wall boundaries."
    )
    cycle["preserved_prior_outcomes"] = {
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
            "Localize the first failed multi-step eligibility, slope, improvement, "
            "relative-error, positivity or conservation gate."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011f cycle failed strict serialization or digest")
    return cycle


def run_q011f_study() -> dict[str, Any]:
    cycle = run_multistep_shadowing_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 finite multi-step shadowing window for the sealed dense "
                "forced fixed-leaf quadratic chart"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011e.q011c.OMEGA,
            "eta": q011e.q011c.ETA,
            "selected_real_dimension": SELECTED_DIMENSION,
            "direction_count": DIRECTION_COUNT,
            "amplitude_count": len(AMPLITUDES),
            "trajectory_count_per_chart": DIRECTION_COUNT * len(AMPLITUDES),
            "maximum_step": MAXIMUM_STEP,
            "horizons": list(HORIZONS),
            "q011e_is_regraded": False,
            "q011e1_is_regraded": False,
            "claim": (
                "finite binary64 multi-step trajectory evidence only; no all-time "
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
    result = run_q011f_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
