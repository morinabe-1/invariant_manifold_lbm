"""Sealed Q011e1 independent enlarged residual-window reissue."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

import research.q011e_forced_quadratic_chart as q011e
from ttim_lbm.d2q9 import global_conserved_quantities
from ttim_lbm.manifold import log_log_slope
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

SIZE = q011e.SIZE
SELECTED_DIMENSION = q011e.SELECTED_DIMENSION

Q011E_ARTIFACT_SHA256 = "45d563103678d790aa3df4db692bbe781c9c86ed550c7499c61b397688666fca"
Q011E_RUNNER_SHA256 = "3aa608852be7a1df7dbe37b4d3c7e1bb3fbf125eae115260fc45a223e0757955"
Q011E_INPUT_DIGEST = "f0bd65361d0cdc39e6499b8b0065ce6d7705945927ed77af5d2b231d0572bc9c"
Q011E_DERIVATIVE_DIGEST = "d017d3ea204ad337f538b6f1819e215b6ab8a69f89090cc51ca9eb4885b75fce"
Q011E_CHART_DIGEST = "6d4ee0102a6df052fac857890468ed911cff994e07c573dde837eb54a4a22e05"
Q011E_RESIDUAL_DIGEST = "5570cb7acfc465f57850f960c6c9d68770182856b6a9aba62e81256c77e84948"
Q011E_RESULT_DIGEST = "89b39a6a6a80452142a2c9288780a08c1b24b49614080b5412fff82171a8188e"
SEALED_PACKAGE_SOURCE_SHA256 = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"

REAL_TANGENT_SHA256 = "e0b6fb929d49a1371d1eebf836308a795a7f0e9dbad44f55b2386add9f3d0628"
REAL_EXTRACTOR_SHA256 = "e77d149787d187ca756a23efcf6b833cfd6ab15b5fd617b5d3ae3ba5c0859f6f"
REAL_LINEAR_SHA256 = "b6521e3090b61c72d0689b765e1fad0a0318029a0ab5767bd3c7679d4ce2c525"
ANALYTIC_SECOND_DERIVATIVE_SHA256 = (
    "6bfea17a7bbfa1dcdded5dadec15296ec2f478aefe7984dd1e4885498a186221"
)
REAL_CHART_HESSIAN_SHA256 = "ab55a8b50f2565be494fcf3d5f140f93fc0112484da56e1333ce58dfd220a6c2"
REAL_REDUCED_HESSIAN_SHA256 = "7ae45cbabda8da17ec73d6779761077a67e19fae4dc53ca11fe98b78bcf074e2"

DIRECTION_SEED = 20260825
DIRECTION_COUNT = 32
AMPLITUDES = (1.6e-4, 3.2e-4, 6.4e-4, 1.28e-3, 2.56e-3)
NOISE_FLOOR = q011e.RESIDUAL_NOISE_FLOOR
MINIMUM_ELIGIBLE_DIRECTION_COUNT = q011e.MINIMUM_ELIGIBLE_DIRECTION_COUNT
LINEAR_SLOPE_INTERVAL = q011e.LINEAR_SLOPE_INTERVAL
QUADRATIC_SLOPE_INTERVAL = q011e.QUADRATIC_SLOPE_INTERVAL
MAXIMUM_SLOPE_WINDOW_DIFFERENCE = 0.15
MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO = q011e.MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO
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
        "residual_campaign": {
            "seed": DIRECTION_SEED,
            "direction_count": DIRECTION_COUNT,
            "amplitudes": list(AMPLITUDES),
            "bridge_amplitude": AMPLITUDES[0],
            "unobserved_enlarged_amplitudes": list(AMPLITUDES[1:]),
            "noise_floor": NOISE_FLOOR,
            "minimum_fit_point_count": 4,
            "minimum_eligible_direction_count": MINIMUM_ELIGIBLE_DIRECTION_COUNT,
        },
        "thresholds": {
            "linear_slope_interval": list(LINEAR_SLOPE_INTERVAL),
            "quadratic_slope_interval": list(QUADRATIC_SLOPE_INTERVAL),
            "maximum_primary_secondary_slope_difference": (MAXIMUM_SLOPE_WINDOW_DIFFERENCE),
            "maximum_largest_amplitude_residual_ratio": (MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO),
            "minimum_population": 0.0,
            "maximum_global_conservation_drift": CONSERVATION_TOLERANCE,
        },
    }


def _sealed_q011e_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011e.__file__).resolve().parent / "artifacts" / ("q011e_forced_quadratic_chart.json")
    )
    runner_path = Path(q011e.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    failed_validity = [name for name, gate in cycle["validity_gates"].items() if not gate["passed"]]
    failed_hypotheses = [
        name for name, gate in cycle["hypothesis_gates"].items() if not gate["passed"]
    ]
    digests = (
        cycle["input_digest_sha256"],
        cycle["derivative_digest_sha256"],
        cycle["chart_digest_sha256"],
        cycle["residual_digest_sha256"],
        cycle["result_digest_sha256"],
    )
    checks = {
        "q011e_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011E_ARTIFACT_SHA256),
        "q011e_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011E_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011E_RUNNER_SHA256
        ),
        "q011e_package_source_sha256_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "q011e_five_digests_match": (
            digests
            == (
                Q011E_INPUT_DIGEST,
                Q011E_DERIVATIVE_DIGEST,
                Q011E_CHART_DIGEST,
                Q011E_RESIDUAL_DIGEST,
                Q011E_RESULT_DIGEST,
            )
        ),
        "q011e_valid_rejected_outcome_is_preserved": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "rejected"
            and not failed_validity
            and failed_hypotheses == ["linear_and_quadratic_residual_orders_pass"]
        ),
        "q011e_underresolved_classification_is_preserved": (
            cycle["scientific_classification"]
            == (
                "the forced fixed-leaf quadratic chart is constructed, but the "
                "registered residual-order window is underresolved"
            )
            and cycle["residual_order_audit"]["seed"] == q011e.RESIDUAL_SEED
            and cycle["residual_order_audit"]["amplitudes"] == list(q011e.RESIDUAL_AMPLITUDES)
            and cycle["residual_order_audit"]["slope_eligible_direction_count"] == 0
        ),
        "q011e_artifact_is_strict_finite_json": bool(
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
            "derivative_digest_sha256": cycle["derivative_digest_sha256"],
            "chart_digest_sha256": cycle["chart_digest_sha256"],
            "residual_digest_sha256": cycle["residual_digest_sha256"],
            "result_digest_sha256": cycle["result_digest_sha256"],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
            "failed_validity_gates": failed_validity,
            "failed_hypothesis_gates": failed_hypotheses,
        },
        "q011e_original_residual_campaign": {
            "seed": cycle["residual_order_audit"]["seed"],
            "amplitudes": cycle["residual_order_audit"]["amplitudes"],
            "noise_floor": cycle["residual_order_audit"]["noise_floor"],
            "slope_eligible_direction_count": cycle["residual_order_audit"][
                "slope_eligible_direction_count"
            ],
            "degenerate_direction_count": cycle["residual_order_audit"][
                "degenerate_direction_count"
            ],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifact


def _reconstruct_q011e_chart(
    artifact: dict[str, Any],
) -> tuple[q011e.RealForcedQuadraticModel, dict[str, Any]]:
    artifact_cycle = artifact["cycle"]
    (
        sealed_input,
        stripe_state,
        fixed_leaf_basis,
        q011d_artifact,
    ) = q011e._sealed_input_audit()
    linear = q011e._complex_linear_data(
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
    ) = q011e._real_linear_coordinates(linear)
    (
        analytic_hessian,
        chart_hessian,
        reduced_hessian,
        quadratic_construction,
    ) = q011e._quadratic_construction(linear)
    model, real_quadratic_audit = q011e._realify_quadratic_model(
        linear,
        real_tangent,
        real_extractor,
        real_reduced_linear,
        coordinate_map,
        analytic_hessian,
        chart_hessian,
        reduced_hessian,
    )
    independent_hessian = q011e._independent_hessian_audit(model)

    input_sections = q011e._json_native(
        {
            "registered_parameters": q011e._registered_parameters(),
            "sealed_input_audit": sealed_input,
        }
    )
    derivative_sections = q011e._json_native(
        {
            "complex_linear_coordinate_audit": linear.audit,
            "real_linear_coordinate_audit": real_linear_audit,
            "independent_hessian_audit": independent_hessian,
        }
    )
    chart_sections = q011e._json_native(
        {
            "quadratic_construction_audit": quadratic_construction,
            "real_quadratic_audit": real_quadratic_audit,
        }
    )
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    derivative_digest = q011e.q011c._canonical_json_sha256(derivative_sections)
    chart_digest = q011e.q011c._canonical_json_sha256(chart_sections)
    observed_hashes = {
        "real_tangent_sha256": q011e.q011c._array_sha256(model.tangent),
        "real_extractor_sha256": q011e.q011c._array_sha256(model.extractor),
        "real_reduced_linear_sha256": q011e.q011c._array_sha256(model.reduced_linear),
        "analytic_second_derivative_sha256": q011e.q011c._array_sha256(model.second_derivative),
        "real_chart_hessian_sha256": q011e.q011c._array_sha256(model.hessian),
        "real_reduced_hessian_sha256": q011e.q011c._array_sha256(model.reduced_hessian),
    }
    expected_hashes = {
        "real_tangent_sha256": REAL_TANGENT_SHA256,
        "real_extractor_sha256": REAL_EXTRACTOR_SHA256,
        "real_reduced_linear_sha256": REAL_LINEAR_SHA256,
        "analytic_second_derivative_sha256": ANALYTIC_SECOND_DERIVATIVE_SHA256,
        "real_chart_hessian_sha256": REAL_CHART_HESSIAN_SHA256,
        "real_reduced_hessian_sha256": REAL_REDUCED_HESSIAN_SHA256,
    }
    checks = {
        "q011e_input_sections_reproduce": (
            input_digest == Q011E_INPUT_DIGEST
            and input_sections["registered_parameters"] == artifact_cycle["registered_parameters"]
            and input_sections["sealed_input_audit"] == artifact_cycle["sealed_input_audit"]
        ),
        "q011e_derivative_sections_reproduce": (
            derivative_digest == Q011E_DERIVATIVE_DIGEST
            and derivative_sections["complex_linear_coordinate_audit"]
            == artifact_cycle["complex_linear_coordinate_audit"]
            and derivative_sections["real_linear_coordinate_audit"]
            == artifact_cycle["real_linear_coordinate_audit"]
            and derivative_sections["independent_hessian_audit"]
            == artifact_cycle["independent_hessian_audit"]
        ),
        "q011e_chart_sections_reproduce": (
            chart_digest == Q011E_CHART_DIGEST
            and chart_sections["quadratic_construction_audit"]
            == artifact_cycle["quadratic_construction_audit"]
            and chart_sections["real_quadratic_audit"] == artifact_cycle["real_quadratic_audit"]
        ),
        "six_registered_chart_array_hashes_reproduce": (observed_hashes == expected_hashes),
        "complex_and_real_linear_construction_passes": (
            linear.audit["passed"] and real_linear_audit["passed"]
        ),
        "analytic_hessian_campaign_passes": (
            independent_hessian["structural_passed"] and independent_hessian["hypothesis_passed"]
        ),
        "complex_quadratic_construction_passes": (
            quadratic_construction["structural_passed"]
            and quadratic_construction["hypothesis_passed"]
        ),
        "real_quadratic_construction_passes": (
            real_quadratic_audit["structural_passed"] and real_quadratic_audit["hypothesis_passed"]
        ),
    }
    audit = {
        "input_digest_sha256": input_digest,
        "derivative_digest_sha256": derivative_digest,
        "chart_digest_sha256": chart_digest,
        "array_hashes": observed_hashes,
        "maximum_complex_linear_structural_residual": linear.audit["maximum_structural_residual"],
        "real_linear_invariance_relative_residual": real_linear_audit[
            "real_linear_invariance_relative_residual"
        ],
        "maximum_independent_hessian_relative_discrepancy": independent_hessian[
            "maximum_analytic_relative_discrepancy"
        ],
        "maximum_sector_sylvester_relative_residual": quadratic_construction[
            "maximum_sector_sylvester_relative_residual"
        ],
        "full_homological_relative_residual": quadratic_construction[
            "full_homological_relative_residual"
        ],
        "maximum_pairwise_homological_relative_residual": quadratic_construction[
            "maximum_pairwise_homological_relative_residual"
        ],
        "real_graph_gauge_relative_residual": real_quadratic_audit[
            "real_graph_gauge_relative_residual"
        ],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return model, q011e._json_native(audit)


def _secondary_slope(
    amplitudes: np.ndarray,
    residuals: np.ndarray,
    mask: np.ndarray,
) -> tuple[float, list[int]]:
    indices = np.flatnonzero(mask).tolist()
    if len(indices) == len(amplitudes):
        indices = indices[1:]
    if len(indices) == 4:
        return (
            float(log_log_slope(amplitudes[indices], residuals[indices])),
            indices,
        )
    return 0.0, []


def _enlarged_residual_audit(
    model: q011e.RealForcedQuadraticModel,
) -> dict[str, Any]:
    generator = np.random.default_rng(DIRECTION_SEED)
    directions = generator.standard_normal((DIRECTION_COUNT, SELECTED_DIMENSION))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    amplitudes = np.asarray(AMPLITUDES, dtype=np.float64)
    base_conserved = global_conserved_quantities(model.base.reshape(SIZE, SIZE, 9))
    records: list[dict[str, Any]] = []

    for direction_index, direction in enumerate(directions):
        samples: list[dict[str, Any]] = []
        for amplitude in amplitudes:
            coordinates = amplitude * direction
            linear_state = model.chart(coordinates, quadratic=False)
            quadratic_state = model.chart(coordinates, quadratic=True)
            linear_reduced = model.reduced_map(coordinates, quadratic=False)
            quadratic_reduced = model.reduced_map(coordinates, quadratic=True)
            linear_reduced_state = model.chart(linear_reduced, quadratic=False)
            quadratic_reduced_state = model.chart(quadratic_reduced, quadratic=True)
            linear_mapped = model.full_map(linear_state)
            quadratic_mapped = model.full_map(quadratic_state)
            linear_residual = float(np.linalg.norm(linear_mapped - linear_reduced_state))
            quadratic_residual = float(np.linalg.norm(quadratic_mapped - quadratic_reduced_state))
            full_states = (
                linear_state,
                quadratic_state,
                linear_reduced_state,
                quadratic_reduced_state,
                linear_mapped,
                quadratic_mapped,
            )
            minimum_population = min(float(np.min(state)) for state in full_states)
            maximum_conservation_drift = max(
                float(
                    np.linalg.norm(
                        global_conserved_quantities(state.reshape(SIZE, SIZE, 9)) - base_conserved
                    )
                )
                for state in full_states
            )
            samples.append(
                {
                    "amplitude": float(amplitude),
                    "linear_residual": linear_residual,
                    "quadratic_residual": quadratic_residual,
                    "linear_chart_state_sha256": q011e.q011c._array_sha256(linear_state),
                    "quadratic_chart_state_sha256": q011e.q011c._array_sha256(quadratic_state),
                    "linear_reduced_coordinate_sha256": q011e.q011c._array_sha256(linear_reduced),
                    "quadratic_reduced_coordinate_sha256": q011e.q011c._array_sha256(
                        quadratic_reduced
                    ),
                    "linear_reduced_chart_state_sha256": q011e.q011c._array_sha256(
                        linear_reduced_state
                    ),
                    "quadratic_reduced_chart_state_sha256": q011e.q011c._array_sha256(
                        quadratic_reduced_state
                    ),
                    "linear_mapped_state_sha256": q011e.q011c._array_sha256(linear_mapped),
                    "quadratic_mapped_state_sha256": q011e.q011c._array_sha256(quadratic_mapped),
                    "minimum_population": minimum_population,
                    "maximum_global_conservation_drift": maximum_conservation_drift,
                }
            )

        linear_residuals = np.asarray(
            [sample["linear_residual"] for sample in samples], dtype=np.float64
        )
        quadratic_residuals = np.asarray(
            [sample["quadratic_residual"] for sample in samples], dtype=np.float64
        )
        linear_mask = linear_residuals >= NOISE_FLOOR
        quadratic_mask = quadratic_residuals >= NOISE_FLOOR
        linear_count = int(np.count_nonzero(linear_mask))
        quadratic_count = int(np.count_nonzero(quadratic_mask))
        eligible = bool(linear_count >= 4 and quadratic_count >= 4)
        linear_primary = (
            float(log_log_slope(amplitudes[linear_mask], linear_residuals[linear_mask]))
            if eligible
            else 0.0
        )
        quadratic_primary = (
            float(
                log_log_slope(
                    amplitudes[quadratic_mask],
                    quadratic_residuals[quadratic_mask],
                )
            )
            if eligible
            else 0.0
        )
        linear_secondary, linear_secondary_indices = (
            _secondary_slope(amplitudes, linear_residuals, linear_mask) if eligible else (0.0, [])
        )
        quadratic_secondary, quadratic_secondary_indices = (
            _secondary_slope(amplitudes, quadratic_residuals, quadratic_mask)
            if eligible
            else (0.0, [])
        )
        secondary_defined = bool(
            len(linear_secondary_indices) == 4 and len(quadratic_secondary_indices) == 4
        )
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "direction_norm": float(np.linalg.norm(direction)),
                "samples": samples,
                "linear_fit_mask": linear_mask.tolist(),
                "quadratic_fit_mask": quadratic_mask.tolist(),
                "linear_fit_point_count": linear_count,
                "quadratic_fit_point_count": quadratic_count,
                "slope_eligible": eligible,
                "linear_primary_slope": linear_primary,
                "quadratic_primary_slope": quadratic_primary,
                "linear_secondary_fit_indices": linear_secondary_indices,
                "quadratic_secondary_fit_indices": quadratic_secondary_indices,
                "secondary_slopes_defined": secondary_defined,
                "linear_secondary_slope": linear_secondary,
                "quadratic_secondary_slope": quadratic_secondary,
                "linear_primary_secondary_difference": (
                    abs(linear_primary - linear_secondary) if secondary_defined else 0.0
                ),
                "quadratic_primary_secondary_difference": (
                    abs(quadratic_primary - quadratic_secondary) if secondary_defined else 0.0
                ),
                "largest_amplitude_residual_ratio": float(
                    quadratic_residuals[-1] / max(linear_residuals[-1], np.finfo(float).tiny)
                ),
                "minimum_population": min(sample["minimum_population"] for sample in samples),
                "maximum_global_conservation_drift": max(
                    sample["maximum_global_conservation_drift"] for sample in samples
                ),
            }
        )

    eligible_records = [record for record in records if record["slope_eligible"]]

    def extrema(key: str) -> tuple[float, float]:
        if not eligible_records:
            return 0.0, 0.0
        values = [record[key] for record in eligible_records]
        return min(values), max(values)

    linear_primary_minimum, linear_primary_maximum = extrema("linear_primary_slope")
    quadratic_primary_minimum, quadratic_primary_maximum = extrema("quadratic_primary_slope")
    linear_secondary_minimum, linear_secondary_maximum = extrema("linear_secondary_slope")
    quadratic_secondary_minimum, quadratic_secondary_maximum = extrema("quadratic_secondary_slope")
    maximum_linear_window_difference = max(
        (record["linear_primary_secondary_difference"] for record in eligible_records),
        default=0.0,
    )
    maximum_quadratic_window_difference = max(
        (record["quadratic_primary_secondary_difference"] for record in eligible_records),
        default=0.0,
    )
    maximum_ratio = max(record["largest_amplitude_residual_ratio"] for record in records)
    minimum_population = min(record["minimum_population"] for record in records)
    maximum_conservation = max(record["maximum_global_conservation_drift"] for record in records)
    sample_count = sum(len(record["samples"]) for record in records)
    checks = {
        "registered_campaign_is_complete": (
            len(records) == DIRECTION_COUNT
            and sample_count == DIRECTION_COUNT * len(AMPLITUDES)
            and all(len(record["samples"]) == len(AMPLITUDES) for record in records)
        ),
        "directions_are_finite_and_unit_normalized": bool(
            np.all(np.isfinite(directions))
            and np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0)) <= 1.0e-14
        ),
        "registered_amplitudes_are_reproduced": all(
            [sample["amplitude"] for sample in record["samples"]] == list(AMPLITUDES)
            for record in records
        ),
        "all_measurements_are_finite": bool(_all_numeric_values_finite(records)),
        "fit_masks_match_the_registered_noise_floor": all(
            record["linear_fit_mask"]
            == [sample["linear_residual"] >= NOISE_FLOOR for sample in record["samples"]]
            and record["quadratic_fit_mask"]
            == [sample["quadratic_residual"] >= NOISE_FLOOR for sample in record["samples"]]
            for record in records
        ),
        "degenerate_directions_are_not_slope_gated": all(
            (record["linear_fit_point_count"] < 4 or record["quadratic_fit_point_count"] < 4)
            == (not record["slope_eligible"])
            for record in records
        ),
        "eligible_secondary_windows_are_defined": all(
            record["secondary_slopes_defined"] for record in eligible_records
        ),
        "sample_hashes_are_complete": all(
            all(len(value) == 64 for key, value in sample.items() if key.endswith("_sha256"))
            and sum(key.endswith("_sha256") for key in sample) == 8
            for record in records
            for sample in record["samples"]
        ),
    }
    hypothesis_checks = {
        "at_least_twenty_eight_directions_are_slope_eligible": (
            len(eligible_records) >= MINIMUM_ELIGIBLE_DIRECTION_COUNT
        ),
        "linear_primary_and_secondary_slopes_are_second_order": (
            LINEAR_SLOPE_INTERVAL[0]
            <= linear_primary_minimum
            <= linear_primary_maximum
            <= LINEAR_SLOPE_INTERVAL[1]
            and LINEAR_SLOPE_INTERVAL[0]
            <= linear_secondary_minimum
            <= linear_secondary_maximum
            <= LINEAR_SLOPE_INTERVAL[1]
        ),
        "quadratic_primary_and_secondary_slopes_are_third_order": (
            QUADRATIC_SLOPE_INTERVAL[0]
            <= quadratic_primary_minimum
            <= quadratic_primary_maximum
            <= QUADRATIC_SLOPE_INTERVAL[1]
            and QUADRATIC_SLOPE_INTERVAL[0]
            <= quadratic_secondary_minimum
            <= quadratic_secondary_maximum
            <= QUADRATIC_SLOPE_INTERVAL[1]
        ),
        "primary_secondary_slope_differences_are_stable": (
            maximum_linear_window_difference <= MAXIMUM_SLOPE_WINDOW_DIFFERENCE
            and maximum_quadratic_window_difference <= MAXIMUM_SLOPE_WINDOW_DIFFERENCE
        ),
        "largest_amplitude_residual_improves_in_every_direction": (
            maximum_ratio <= MAXIMUM_RESIDUAL_IMPROVEMENT_RATIO
        ),
        "all_states_are_positive_and_conservation_drift_is_bounded": (
            minimum_population > 0.0 and maximum_conservation <= CONSERVATION_TOLERANCE
        ),
    }
    return q011e._json_native(
        {
            "seed": DIRECTION_SEED,
            "direction_count": len(records),
            "direction_sha256": q011e.q011c._array_sha256(directions),
            "amplitudes": list(AMPLITUDES),
            "noise_floor": NOISE_FLOOR,
            "sample_count": sample_count,
            "direction_records": records,
            "slope_eligible_direction_count": len(eligible_records),
            "degenerate_direction_count": len(records) - len(eligible_records),
            "minimum_linear_primary_slope": linear_primary_minimum,
            "maximum_linear_primary_slope": linear_primary_maximum,
            "minimum_linear_secondary_slope": linear_secondary_minimum,
            "maximum_linear_secondary_slope": linear_secondary_maximum,
            "minimum_quadratic_primary_slope": quadratic_primary_minimum,
            "maximum_quadratic_primary_slope": quadratic_primary_maximum,
            "minimum_quadratic_secondary_slope": quadratic_secondary_minimum,
            "maximum_quadratic_secondary_slope": quadratic_secondary_maximum,
            "maximum_linear_primary_secondary_slope_difference": (maximum_linear_window_difference),
            "maximum_quadratic_primary_secondary_slope_difference": (
                maximum_quadratic_window_difference
            ),
            "maximum_largest_amplitude_residual_ratio": maximum_ratio,
            "minimum_chart_reduced_or_mapped_population": minimum_population,
            "maximum_global_conservation_drift": maximum_conservation,
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
        "residual_window_digest_sha256": cycle["residual_window_digest_sha256"],
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


def run_enlarged_residual_window_audit() -> dict[str, Any]:
    """Run the preregistered Q011e1 enlarged residual-window reissue."""

    registered_parameters = _registered_parameters()
    sealed_q011e, artifact = _sealed_q011e_artifact_audit()
    model, chart_reconstruction = _reconstruct_q011e_chart(artifact)
    residual_window = _enlarged_residual_audit(model)

    input_sections = {
        "registered_parameters": registered_parameters,
        "sealed_q011e_artifact_audit": sealed_q011e,
    }
    chart_sections = {
        "q011e_chart_reconstruction_audit": chart_reconstruction,
    }
    residual_sections = {
        "enlarged_residual_window_audit": residual_window,
    }
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    chart_digest = q011e.q011c._canonical_json_sha256(chart_sections)
    residual_digest = q011e.q011c._canonical_json_sha256(residual_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **chart_sections,
        **residual_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == q011e.q011c._canonical_json_sha256(input_sections)
        and chart_digest == q011e.q011c._canonical_json_sha256(chart_sections)
        and residual_digest == q011e.q011c._canonical_json_sha256(residual_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )
    residual_checks = residual_window["checks"]
    validity_gates = {
        "sealed_q011e_artifact_and_outcome_reproduce": {
            "passed": sealed_q011e["passed"],
            "threshold": (
                "Q011e artifact, runner, package source, five digests, valid/rejected "
                "outcome and sole residual-order failure reproduce exactly"
            ),
            "value": sealed_q011e["checks"],
        },
        "q011e_chart_reconstructs_once_without_refitting": {
            "passed": chart_reconstruction["passed"],
            "threshold": (
                "fresh Q011e input/derivative/chart sections, six array hashes and "
                "all construction thresholds reproduce"
            ),
            "value": chart_reconstruction["checks"],
        },
        "registered_independent_campaign_is_complete": {
            "passed": bool(
                residual_checks["registered_campaign_is_complete"]
                and residual_checks["directions_are_finite_and_unit_normalized"]
                and residual_checks["registered_amplitudes_are_reproduced"]
            ),
            "threshold": (
                "seed 20260825 gives 32 unit directions and five registered "
                "amplitudes for 160 complete samples"
            ),
            "value": {
                "seed": residual_window["seed"],
                "direction_count": residual_window["direction_count"],
                "sample_count": residual_window["sample_count"],
                "direction_sha256": residual_window["direction_sha256"],
                "amplitudes": residual_window["amplitudes"],
            },
        },
        "residual_fit_and_state_diagnostics_are_complete": {
            "passed": bool(
                residual_window["structural_passed"]
                and residual_checks["all_measurements_are_finite"]
                and residual_checks["fit_masks_match_the_registered_noise_floor"]
                and residual_checks["degenerate_directions_are_not_slope_gated"]
                and residual_checks["sample_hashes_are_complete"]
            ),
            "threshold": (
                "all residuals, fit masks, primary/secondary slopes, state hashes, "
                "positivity and conservation diagnostics are finite and complete"
            ),
            "value": residual_checks,
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "strict finite JSON plus deterministic input/chart/residual digests "
                "and newline-normalized runner SHA-256"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    raw_hypotheses = residual_window["hypothesis_checks"]
    hypothesis_gates = {
        "at_least_twenty_eight_directions_are_slope_eligible": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["at_least_twenty_eight_directions_are_slope_eligible"]
            ),
            "threshold": ">=28 of 32 directions have at least four fit points for both charts",
            "value": residual_window["slope_eligible_direction_count"],
        },
        "linear_primary_and_secondary_slopes_are_second_order": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["linear_primary_and_secondary_slopes_are_second_order"]
            ),
            "threshold": "all eligible primary and secondary slopes are in [1.85, 2.15]",
            "value": {
                "primary": [
                    residual_window["minimum_linear_primary_slope"],
                    residual_window["maximum_linear_primary_slope"],
                ],
                "secondary": [
                    residual_window["minimum_linear_secondary_slope"],
                    residual_window["maximum_linear_secondary_slope"],
                ],
            },
        },
        "quadratic_primary_and_secondary_slopes_are_third_order": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["quadratic_primary_and_secondary_slopes_are_third_order"]
            ),
            "threshold": "all eligible primary and secondary slopes are in [2.70, 3.30]",
            "value": {
                "primary": [
                    residual_window["minimum_quadratic_primary_slope"],
                    residual_window["maximum_quadratic_primary_slope"],
                ],
                "secondary": [
                    residual_window["minimum_quadratic_secondary_slope"],
                    residual_window["maximum_quadratic_secondary_slope"],
                ],
            },
        },
        "primary_secondary_slope_differences_are_stable": {
            "passed": bool(
                validity_passed and raw_hypotheses["primary_secondary_slope_differences_are_stable"]
            ),
            "threshold": "maximum linear and quadratic slope-window difference <=0.15",
            "value": {
                "linear": residual_window["maximum_linear_primary_secondary_slope_difference"],
                "quadratic": residual_window[
                    "maximum_quadratic_primary_secondary_slope_difference"
                ],
            },
        },
        "largest_amplitude_residual_improves_in_every_direction": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["largest_amplitude_residual_improves_in_every_direction"]
            ),
            "threshold": "maximum largest-amplitude quadratic/linear residual ratio <=0.25",
            "value": residual_window["maximum_largest_amplitude_residual_ratio"],
        },
        "positivity_and_conservation_hold": {
            "passed": bool(
                validity_passed
                and raw_hypotheses["all_states_are_positive_and_conservation_drift_is_bounded"]
            ),
            "threshold": "minimum population >0 and maximum conservation drift <=1e-10",
            "value": {
                "minimum_population": residual_window["minimum_chart_reduced_or_mapped_population"],
                "maximum_global_conservation_drift": residual_window[
                    "maximum_global_conservation_drift"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011e1 enlarged residual-window reissue is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the independent enlarged window resolves second- and third-order "
            "forced chart residuals"
        )
    else:
        outcome = "rejected"
        classification = (
            "the enlarged residual window does not confirm the registered forced chart orders"
        )

    cycle: dict[str, Any] = q011e._json_native(
        {
            "question": (
                "Does an independent enlarged amplitude window resolve the second- "
                "and third-order residuals of the sealed Q011e forced chart?"
            ),
            **pre_gate_sections,
            "input_digest_sha256": input_digest,
            "chart_reconstruction_digest_sha256": chart_digest,
            "residual_window_digest_sha256": residual_digest,
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
        "q011e_original_residual_campaign_regraded": False,
        "q011e_dense_quadratic_chart_changed": False,
        "independent_enlarged_window_confirms_residual_orders": bool(
            validity_passed and hypotheses_passed
        ),
        "uniform_taylor_remainder_is_certified": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
        "tt_compression_is_evaluated": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 one-step residual holdout on one 17x17 "
        "forced endpoint, 32 independent directions and five registered amplitudes. "
        "It does not regrade Q011e, prove a uniform Taylor remainder, continuous-"
        "amplitude family, forced SSM existence or uniqueness, nonlinear normal "
        "attraction or a basin, evaluate TT compression, or cover other grids, "
        "forces or wall boundaries."
    )
    cycle["preserved_prior_outcomes"] = {
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
        "Preregister Q011f for an independent multi-step forced-chart shadowing window."
        if outcome == "accepted"
        else (
            "Localize the first failed enlarged-window eligibility, slope, stability, "
            "improvement, positivity or conservation gate."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011e1 cycle failed strict serialization or digest")
    return cycle


def run_q011e1_study() -> dict[str, Any]:
    cycle = run_enlarged_residual_window_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 independent enlarged one-step residual window for the "
                "sealed dense forced fixed-leaf quadratic chart"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011e.q011c.OMEGA,
            "eta": q011e.q011c.ETA,
            "selected_real_dimension": SELECTED_DIMENSION,
            "direction_count": DIRECTION_COUNT,
            "amplitude_count": len(AMPLITUDES),
            "sample_count": DIRECTION_COUNT * len(AMPLITUDES),
            "q011e_is_regraded": False,
            "claim": (
                "finite independent residual-order holdout only; no uniform Taylor, "
                "forced-SSM existence or nonlinear-attraction claim"
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
    result = run_q011e1_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
