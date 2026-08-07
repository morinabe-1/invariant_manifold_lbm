"""Sealed Q007b1 independent cubic-radius and immersion audit."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.stats import spearmanr

from .cubic_chart import Full2DCubicModel, build_full2d_cubic_model
from .cubic_continuation import (
    C4_DIRECTION_COUNT,
    C4_SEED,
    DERIVATIVE_DIRECTION_COUNT,
    DERIVATIVE_SEED,
    RESIDUAL_DIRECTION_COUNT,
    RESIDUAL_ORDER_SEED,
    SHADOWING_DIRECTION_COUNT,
    SHADOWING_SEED,
    _all_numeric_values_finite,
    _shadow_rollout,
    _strict_json_serializable,
)
from .forward_error_budget import COMPONENT_NAMES
from .full2d_chart import REDUCED_DIMENSION, RESIDUAL_SEED, SHADOW_SEED
from .manifold import log_log_slope

Array = npt.NDArray[np.float64]

RADIUS_SEED = 20260818
RADIUS_DIRECTION_COUNT = 64
RADIUS_AMPLITUDES = (0.00125, 0.002, 0.003, 0.004, 0.006, 0.008, 0.01)
RADIUS_ACCEPTANCE_AMPLITUDE = 0.004
RADIUS_SLOPE_FIT_COUNT = 4
QUADRATIC_SLOPE_RANGE = (2.9, 3.1)
CUBIC_SLOPE_RANGE = (3.85, 4.15)
RATIO_SLOPE_RANGE = (0.9, 1.1)
MAXIMUM_RADIUS_RESIDUAL_RATIO = 0.10

SHADOW_RADIUS_SEED = 20260819
SHADOW_RADIUS_DIRECTION_COUNT = 32
SHADOW_RADIUS_AMPLITUDE = 0.004
SHADOW_RADIUS_STEPS = 100
MAXIMUM_SHADOW_RATIO = 0.8
MAXIMUM_FINAL_COMPONENT_BUDGET = 1.2e-11

JACOBIAN_SEED = 20260820
JACOBIAN_DIRECTION_PAIR_COUNT = 16
JACOBIAN_POINT_AMPLITUDES = (0.004, 0.01)
JACOBIAN_DIFFERENCE_STEPS = (1.0e-5, 5.0e-6, 2.5e-6)
MAXIMUM_JACOBIAN_RELATIVE_ERROR = 1.0e-7
MINIMUM_JACOBIAN_ACTION_NORM = 1.0e-12
IMMERSION_AMPLITUDES = (0.0, 0.002, 0.004, 0.006, 0.008, 0.01)
MINIMUM_NORMALIZED_SINGULAR_VALUE = 0.8

NEAR_RESONANT_CONDITION_THRESHOLD = 1.0e4
REGISTERED_NEAR_RESONANT_TRIPLE_COUNT = 24
DIRECTION_NORM_TOLERANCE = 5.0e-15

REGISTERED_COEFFICIENT_HASHES = {
    "triple_indices_sha256": (
        "e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c"
    ),
    "output_waves_sha256": (
        "d431bfabad714d9d7ee9d8bfaf779eb2362ab27c916740494a379610c1389a6f"
    ),
    "chart_coefficients_sha256": (
        "ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b"
    ),
    "reduced_coefficients_sha256": (
        "4ca5a953833d5913f160e9fc36061e31697c7531865c4ef06d7517898f7c597e"
    ),
    "forcing_coefficients_sha256": (
        "6e2559a194d2b1e6a96f01653c1bccbe1852db00233700e16b3b980ae96df8eb"
    ),
}


def _normalized_directions(seed: int, count: int, dimension: int) -> Array:
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, dimension))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
    )


def _jacobian_directions(dimension: int) -> tuple[Array, Array]:
    rng = np.random.default_rng(JACOBIAN_SEED)
    point_directions = rng.normal(size=(JACOBIAN_DIRECTION_PAIR_COUNT, dimension))
    action_directions = rng.normal(size=(JACOBIAN_DIRECTION_PAIR_COUNT, dimension))
    point_directions /= np.linalg.norm(point_directions, axis=1)[:, None]
    action_directions /= np.linalg.norm(action_directions, axis=1)[:, None]
    return (
        np.asarray(point_directions, dtype=np.float64),
        np.asarray(action_directions, dtype=np.float64),
    )


def _array_hash(value: npt.ArrayLike) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    digest = sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def _relative_norm(
    numerator: npt.ArrayLike,
    denominator: npt.ArrayLike,
) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).eps)
    )


def _direction_registration() -> dict[str, Any]:
    point_directions, action_directions = _jacobian_directions(REDUCED_DIMENSION)
    registered_groups = {
        "q007b1_radius": _normalized_directions(
            RADIUS_SEED,
            RADIUS_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b1_shadow": _normalized_directions(
            SHADOW_RADIUS_SEED,
            SHADOW_RADIUS_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b1_jacobian_points": point_directions,
        "q007b1_jacobian_actions": action_directions,
    }
    reference_groups = {
        "q006i_residual": _normalized_directions(
            RESIDUAL_SEED,
            64,
            REDUCED_DIMENSION,
        ),
        "q006i_shadow": _normalized_directions(
            SHADOW_SEED,
            32,
            REDUCED_DIMENSION,
        ),
        "q007b_derivative": _normalized_directions(
            DERIVATIVE_SEED,
            DERIVATIVE_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b_c4": _normalized_directions(
            C4_SEED,
            C4_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b_residual": _normalized_directions(
            RESIDUAL_ORDER_SEED,
            RESIDUAL_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b_shadow": _normalized_directions(
            SHADOWING_SEED,
            SHADOWING_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
    }
    records = []
    for name, directions in registered_groups.items():
        records.append(
            {
                "group": name,
                "direction_count": len(directions),
                "direction_sha256": _array_hash(directions),
                "maximum_norm_error": float(
                    np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0))
                ),
            }
        )
    duplicate_records = []
    seen: list[tuple[str, int, Array]] = []
    for group_name, directions in {
        **reference_groups,
        **registered_groups,
    }.items():
        for direction_index, direction in enumerate(directions):
            for prior_group, prior_index, prior_direction in seen:
                if np.array_equal(direction, prior_direction):
                    duplicate_records.append(
                        {
                            "group": group_name,
                            "direction_index": direction_index,
                            "prior_group": prior_group,
                            "prior_direction_index": prior_index,
                        }
                    )
            seen.append((group_name, direction_index, direction))
    return {
        "registered_group_records": records,
        "reference_group_hashes": {
            name: _array_hash(directions)
            for name, directions in reference_groups.items()
        },
        "maximum_norm_error": max(
            record["maximum_norm_error"] for record in records
        ),
        "duplicate_count": len(duplicate_records),
        "duplicate_records": duplicate_records,
    }


def _radius_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    amplitudes = np.asarray(RADIUS_AMPLITUDES, dtype=np.float64)
    fit_amplitudes = amplitudes[:RADIUS_SLOPE_FIT_COUNT]
    acceptance_index = int(
        np.flatnonzero(amplitudes == RADIUS_ACCEPTANCE_AMPLITUDE)[0]
    )
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        quadratic_residuals = []
        cubic_residuals = []
        ratios = []
        direction_minimum = np.inf
        direction_finite = True
        for amplitude in amplitudes:
            coordinates = amplitude * direction
            quadratic_lifted = model.chart_evaluate(coordinates, cubic=False)
            quadratic_mapped = model.quadratic.full_map(quadratic_lifted)
            quadratic_predicted = model.chart_evaluate(
                model.reduced_map(coordinates, cubic=False),
                cubic=False,
            )
            cubic_lifted = model.chart_evaluate(coordinates, cubic=True)
            cubic_mapped = model.quadratic.full_map(cubic_lifted)
            cubic_predicted = model.chart_evaluate(
                model.reduced_map(coordinates, cubic=True),
                cubic=True,
            )
            quadratic_residual = float(
                np.linalg.norm(quadratic_mapped - quadratic_predicted)
            )
            cubic_residual = float(
                np.linalg.norm(cubic_mapped - cubic_predicted)
            )
            quadratic_residuals.append(quadratic_residual)
            cubic_residuals.append(cubic_residual)
            ratios.append(cubic_residual / quadratic_residual)
            states = (
                quadratic_lifted,
                quadratic_mapped,
                quadratic_predicted,
                cubic_lifted,
                cubic_mapped,
                cubic_predicted,
            )
            direction_minimum = min(
                direction_minimum,
                *(float(np.min(state)) for state in states),
            )
            direction_finite = direction_finite and all(
                np.all(np.isfinite(state)) for state in states
            )
        quadratic_slope = log_log_slope(
            fit_amplitudes,
            quadratic_residuals[:RADIUS_SLOPE_FIT_COUNT],
        )
        cubic_slope = log_log_slope(
            fit_amplitudes,
            cubic_residuals[:RADIUS_SLOPE_FIT_COUNT],
        )
        ratio_slope = log_log_slope(amplitudes, ratios)
        direction_finite = bool(
            direction_finite
            and np.all(np.isfinite(quadratic_residuals))
            and np.all(np.isfinite(cubic_residuals))
            and np.all(np.isfinite(ratios))
            and np.isfinite(quadratic_slope)
            and np.isfinite(cubic_slope)
            and np.isfinite(ratio_slope)
        )
        all_values_finite = all_values_finite and direction_finite
        minimum_population = min(minimum_population, direction_minimum)
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "quadratic_residuals": quadratic_residuals,
                "cubic_residuals": cubic_residuals,
                "cubic_to_quadratic_ratios": ratios,
                "quadratic_slope_first_four": quadratic_slope,
                "cubic_slope_first_four": cubic_slope,
                "ratio_slope_all_seven": ratio_slope,
                "acceptance_radius_ratio": ratios[acceptance_index],
                "minimum_population": float(direction_minimum),
                "all_values_finite": direction_finite,
            }
        )
    worst_radius_index = max(
        range(len(records)),
        key=lambda index: records[index]["acceptance_radius_ratio"],
    )
    maximum_ratios_by_amplitude = [
        max(record["cubic_to_quadratic_ratios"][index] for record in records)
        for index in range(len(amplitudes))
    ]
    failure_counts_by_amplitude = [
        sum(
            record["cubic_to_quadratic_ratios"][index]
            > MAXIMUM_RADIUS_RESIDUAL_RATIO
            for record in records
        )
        for index in range(len(amplitudes))
    ]
    return {
        "seed": RADIUS_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitudes": amplitudes.tolist(),
        "slope_fit_amplitudes": fit_amplitudes.tolist(),
        "acceptance_amplitude": RADIUS_ACCEPTANCE_AMPLITUDE,
        "direction_records": records,
        "summary": {
            "minimum_quadratic_slope": min(
                record["quadratic_slope_first_four"] for record in records
            ),
            "maximum_quadratic_slope": max(
                record["quadratic_slope_first_four"] for record in records
            ),
            "minimum_cubic_slope": min(
                record["cubic_slope_first_four"] for record in records
            ),
            "maximum_cubic_slope": max(
                record["cubic_slope_first_four"] for record in records
            ),
            "minimum_ratio_slope": min(
                record["ratio_slope_all_seven"] for record in records
            ),
            "maximum_ratio_slope": max(
                record["ratio_slope_all_seven"] for record in records
            ),
            "maximum_acceptance_radius_ratio": records[worst_radius_index][
                "acceptance_radius_ratio"
            ],
            "worst_acceptance_radius_direction_index": worst_radius_index,
            "acceptance_radius_failure_count": sum(
                record["acceptance_radius_ratio"]
                > MAXIMUM_RADIUS_RESIDUAL_RATIO
                for record in records
            ),
            "maximum_ratios_by_amplitude": maximum_ratios_by_amplitude,
            "ratio_failure_counts_by_amplitude": failure_counts_by_amplitude,
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _jacobian_validity_campaign(
    model: Full2DCubicModel,
    point_directions: Array,
    action_directions: Array,
) -> dict[str, Any]:
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for pair_index, (point, action) in enumerate(
        zip(point_directions, action_directions, strict=True)
    ):
        for amplitude in JACOBIAN_POINT_AMPLITUDES:
            coordinates = amplitude * point
            analytic = model.chart_jacobian_action(coordinates, action)
            step_records = []
            for step in JACOBIAN_DIFFERENCE_STEPS:
                plus = model.chart_evaluate(coordinates + step * action)
                minus = model.chart_evaluate(coordinates - step * action)
                finite_difference = (plus - minus) / (2.0 * step)
                error = _relative_norm(finite_difference - analytic, analytic)
                trial_minimum = min(float(np.min(plus)), float(np.min(minus)))
                finite = bool(
                    np.all(np.isfinite(plus))
                    and np.all(np.isfinite(minus))
                    and np.all(np.isfinite(finite_difference))
                    and np.isfinite(error)
                )
                minimum_population = min(minimum_population, trial_minimum)
                all_values_finite = all_values_finite and finite
                step_records.append(
                    {
                        "step": step,
                        "finite_difference_norm": float(
                            np.linalg.norm(finite_difference)
                        ),
                        "relative_error": error,
                        "minimum_population": trial_minimum,
                        "all_values_finite": finite,
                    }
                )
            best = min(
                step_records,
                key=lambda record: record["relative_error"],
            )
            records.append(
                {
                    "pair_index": pair_index,
                    "point_amplitude": amplitude,
                    "point_direction": point.tolist(),
                    "action_direction": action.tolist(),
                    "analytic_action_norm": float(np.linalg.norm(analytic)),
                    "best_step": best["step"],
                    "minimum_relative_error": best["relative_error"],
                    "step_records": step_records,
                }
            )
    return {
        "seed": JACOBIAN_SEED,
        "direction_pair_count": len(point_directions),
        "evaluation_count": len(records),
        "point_direction_sha256": _array_hash(point_directions),
        "action_direction_sha256": _array_hash(action_directions),
        "point_amplitudes": list(JACOBIAN_POINT_AMPLITUDES),
        "difference_steps": list(JACOBIAN_DIFFERENCE_STEPS),
        "records": records,
        "summary": {
            "minimum_analytic_action_norm": min(
                record["analytic_action_norm"] for record in records
            ),
            "maximum_best_relative_error": max(
                record["minimum_relative_error"] for record in records
            ),
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _immersion_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    base_singular_values = np.linalg.svd(
        model.quadratic.chart.tangent,
        compute_uv=False,
    )
    base_minimum = float(base_singular_values[-1])
    records = [
        {
            "direction_index": None,
            "amplitude": 0.0,
            "singular_values": base_singular_values.tolist(),
            "minimum_singular_value": base_minimum,
            "normalized_minimum_singular_value": 1.0,
            "condition_number": float(
                base_singular_values[0] / base_singular_values[-1]
            ),
            "minimum_population": float(np.min(model.quadratic.chart.base)),
            "all_values_finite": bool(np.all(np.isfinite(base_singular_values))),
        }
    ]
    minimum_population = float(np.min(model.quadratic.chart.base))
    all_values_finite = records[0]["all_values_finite"]
    for direction_index, direction in enumerate(directions):
        for amplitude in IMMERSION_AMPLITUDES[1:]:
            coordinates = amplitude * direction
            jacobian = model.chart_jacobian(coordinates)
            singular_values = np.linalg.svd(jacobian, compute_uv=False)
            minimum_singular = float(singular_values[-1])
            normalized = minimum_singular / base_minimum
            chart_value = model.chart_evaluate(coordinates)
            mapped = model.quadratic.full_map(chart_value)
            trial_minimum = min(
                float(np.min(chart_value)),
                float(np.min(mapped)),
            )
            finite = bool(
                np.all(np.isfinite(jacobian))
                and np.all(np.isfinite(singular_values))
                and np.all(np.isfinite(chart_value))
                and np.all(np.isfinite(mapped))
                and np.isfinite(normalized)
            )
            minimum_population = min(minimum_population, trial_minimum)
            all_values_finite = all_values_finite and finite
            records.append(
                {
                    "direction_index": direction_index,
                    "amplitude": amplitude,
                    "singular_values": singular_values.tolist(),
                    "minimum_singular_value": minimum_singular,
                    "normalized_minimum_singular_value": normalized,
                    "condition_number": float(
                        singular_values[0] / singular_values[-1]
                    ),
                    "minimum_population": trial_minimum,
                    "all_values_finite": finite,
                }
            )
    worst_index = min(
        range(len(records)),
        key=lambda index: records[index]["normalized_minimum_singular_value"],
    )
    return {
        "direction_seed": RADIUS_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitudes": list(IMMERSION_AMPLITUDES),
        "base_singular_values": base_singular_values.tolist(),
        "unique_sample_count": len(records),
        "records": records,
        "summary": {
            "minimum_normalized_singular_value": records[worst_index][
                "normalized_minimum_singular_value"
            ],
            "worst_record_index": worst_index,
            "maximum_condition_number": max(
                record["condition_number"] for record in records
            ),
            "minimum_population": minimum_population,
            "all_values_finite": all_values_finite,
        },
    }


def _spearman_record(left: Array, right: Array) -> dict[str, Any]:
    left_constant = bool(np.all(left == left[0]))
    right_constant = bool(np.all(right == right[0]))
    if left_constant or right_constant:
        return {
            "defined": False,
            "correlation": None,
            "p_value": None,
            "left_input_constant": left_constant,
            "right_input_constant": right_constant,
        }
    statistic = spearmanr(left, right)
    return {
        "defined": True,
        "correlation": float(statistic.statistic),
        "p_value": float(statistic.pvalue),
        "left_input_constant": False,
        "right_input_constant": False,
    }


def _quartile_enrichment(target: Array, score: Array) -> float:
    count = len(score) // 4
    ordering = np.argsort(score)
    selected = ordering[-count:]
    remainder = ordering[:-count]
    return float(
        np.mean(target[selected])
        / max(float(np.mean(target[remainder])), np.finfo(float).eps)
    )


def _near_resonant_campaign(
    model: Full2DCubicModel,
    directions: Array,
    radius_campaign: dict[str, Any],
) -> dict[str, Any]:
    near_mask = np.asarray(
        [
            record["condition_number"] is not None
            and record["condition_number"]
            >= NEAR_RESONANT_CONDITION_THRESHOLD
            for record in model.coefficient_records
        ],
        dtype=bool,
    )
    near_indices = np.flatnonzero(near_mask)
    amplitude_indices = {
        amplitude: radius_campaign["amplitudes"].index(amplitude)
        for amplitude in (RADIUS_ACCEPTANCE_AMPLITUDE, 0.01)
    }
    records = []
    summaries = {}
    for amplitude, residual_index in amplitude_indices.items():
        amplitude_records = []
        for direction_index, direction in enumerate(directions):
            coordinates = amplitude * direction
            full_chart = model.cubic_chart_term(coordinates)
            near_chart = model.cubic_chart_term(
                coordinates,
                triple_mask=near_mask,
            )
            full_reduced = model.reduced_cubic_term(coordinates)
            near_reduced = model.reduced_cubic_term(
                coordinates,
                triple_mask=near_mask,
            )
            quadratic_chart = 0.5 * np.einsum(
                "ijk,j,k->i",
                model.quadratic.chart.hessian,
                coordinates,
                coordinates,
            )
            quadratic_reduced = 0.5 * np.einsum(
                "ijk,j,k->i",
                model.quadratic.reduced_hessian,
                coordinates,
                coordinates,
            )
            residual_ratio = radius_campaign["direction_records"][
                direction_index
            ]["cubic_to_quadratic_ratios"][residual_index]
            amplitude_records.append(
                {
                    "direction_index": direction_index,
                    "chart_near_fraction": _relative_norm(
                        near_chart,
                        full_chart,
                    ),
                    "reduced_near_fraction": _relative_norm(
                        near_reduced,
                        full_reduced,
                    ),
                    "chart_cubic_to_quadratic_correction_ratio": _relative_norm(
                        full_chart / 6.0,
                        quadratic_chart,
                    ),
                    "reduced_cubic_to_quadratic_correction_ratio": (
                        _relative_norm(full_reduced / 6.0, quadratic_reduced)
                    ),
                    "residual_ratio": residual_ratio,
                }
            )
        records.extend(
            {"amplitude": amplitude, **record}
            for record in amplitude_records
        )
        residual_ratios = np.asarray(
            [record["residual_ratio"] for record in amplitude_records]
        )
        chart_fractions = np.asarray(
            [record["chart_near_fraction"] for record in amplitude_records]
        )
        reduced_fractions = np.asarray(
            [record["reduced_near_fraction"] for record in amplitude_records]
        )
        chart_correction_ratios = np.asarray(
            [
                record["chart_cubic_to_quadratic_correction_ratio"]
                for record in amplitude_records
            ]
        )
        summaries[str(amplitude)] = {
            "chart_near_fraction_range": [
                float(np.min(chart_fractions)),
                float(np.max(chart_fractions)),
            ],
            "reduced_near_fraction_range": [
                float(np.min(reduced_fractions)),
                float(np.max(reduced_fractions)),
            ],
            "chart_near_fraction_residual_ratio_spearman": _spearman_record(
                chart_fractions,
                residual_ratios,
            ),
            "reduced_near_fraction_residual_ratio_spearman": _spearman_record(
                reduced_fractions,
                residual_ratios,
            ),
            "chart_correction_residual_ratio_spearman": _spearman_record(
                chart_correction_ratios,
                residual_ratios,
            ),
            "chart_near_fraction_top_residual_quartile_enrichment": (
                _quartile_enrichment(chart_fractions, residual_ratios)
            ),
            "reduced_near_fraction_top_residual_quartile_enrichment": (
                _quartile_enrichment(reduced_fractions, residual_ratios)
            ),
        }
    return {
        "condition_threshold": NEAR_RESONANT_CONDITION_THRESHOLD,
        "near_resonant_triple_count": int(np.count_nonzero(near_mask)),
        "near_resonant_triple_indices": near_indices.tolist(),
        "near_resonant_triple_identifiers": [
            model.coefficient_records[index]["triple_identifier"]
            for index in near_indices
        ],
        "amplitudes": [RADIUS_ACCEPTANCE_AMPLITUDE, 0.01],
        "records": records,
        "summary_by_amplitude": summaries,
        "all_values_finite": _all_numeric_values_finite(
            {"records": records, "summaries": summaries}
        ),
    }


def _shadow_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    records = []
    total_budget_violations = 0
    total_component_checks = 0
    maximum_final_component_budget = 0.0
    maximum_budget_utilization = 0.0
    for direction_index, direction in enumerate(directions):
        quadratic = _shadow_rollout(
            model,
            direction,
            direction_index,
            cubic=False,
            amplitude=SHADOW_RADIUS_AMPLITUDE,
            steps=SHADOW_RADIUS_STEPS,
        )
        cubic = _shadow_rollout(
            model,
            direction,
            direction_index,
            cubic=True,
            amplitude=SHADOW_RADIUS_AMPLITUDE,
            steps=SHADOW_RADIUS_STEPS,
        )
        ratios = {
            "maximum_absolute_error_ratio": float(
                cubic["maximum_absolute_error"]
                / max(quadratic["maximum_absolute_error"], np.finfo(float).eps)
            ),
            "final_absolute_error_ratio": float(
                cubic["final_absolute_error"]
                / max(quadratic["final_absolute_error"], np.finfo(float).eps)
            ),
            "maximum_perturbation_relative_error_ratio": float(
                cubic["maximum_perturbation_relative_error"]
                / max(
                    quadratic["maximum_perturbation_relative_error"],
                    np.finfo(float).eps,
                )
            ),
        }
        budget = cubic["conservation_budget"]
        total_budget_violations += budget["violation_count"]
        total_component_checks += budget["component_check_count"]
        maximum_final_component_budget = max(
            maximum_final_component_budget,
            budget["maximum_final_component_budget"],
        )
        maximum_budget_utilization = max(
            maximum_budget_utilization,
            budget["maximum_budget_utilization"],
        )
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "quadratic": quadratic,
                "cubic": cubic,
                "improvement_ratios": ratios,
            }
        )
    ratio_keys = (
        "maximum_absolute_error_ratio",
        "final_absolute_error_ratio",
        "maximum_perturbation_relative_error_ratio",
    )
    return {
        "seed": SHADOW_RADIUS_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitude": SHADOW_RADIUS_AMPLITUDE,
        "steps": SHADOW_RADIUS_STEPS,
        "direction_records": records,
        "summary": {
            "maximum_directional_improvement_ratios": {
                key: max(
                    record["improvement_ratios"][key] for record in records
                )
                for key in ratio_keys
            },
            "directional_ratio_failure_counts": {
                key: sum(
                    record["improvement_ratios"][key] > MAXIMUM_SHADOW_RATIO
                    for record in records
                )
                for key in ratio_keys
            },
            "cubic_budget_component_check_count": total_component_checks,
            "cubic_budget_violation_count": total_budget_violations,
            "maximum_cubic_budget_utilization": maximum_budget_utilization,
            "maximum_final_component_budget": maximum_final_component_budget,
            "minimum_population": min(
                min(
                    record["quadratic"]["minimum_population"],
                    record["cubic"]["minimum_population"],
                )
                for record in records
            ),
            "all_values_finite": all(
                record["quadratic"]["all_values_finite"]
                and record["cubic"]["all_values_finite"]
                for record in records
            ),
        },
    }


def run_cubic_radius_audit() -> dict[str, Any]:
    """Run the sealed Q007b1 independent radius and immersion audit."""

    model = build_full2d_cubic_model()
    coefficient_hashes = model.coefficient_hashes()
    direction_registration = _direction_registration()
    radius_directions = _normalized_directions(
        RADIUS_SEED,
        RADIUS_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    shadow_directions = _normalized_directions(
        SHADOW_RADIUS_SEED,
        SHADOW_RADIUS_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    point_directions, action_directions = _jacobian_directions(
        model.reduced_dimension
    )
    radius = _radius_campaign(model, radius_directions)
    jacobian = _jacobian_validity_campaign(
        model,
        point_directions,
        action_directions,
    )
    immersion = _immersion_campaign(model, radius_directions)
    near_resonance = _near_resonant_campaign(
        model,
        radius_directions,
        radius,
    )
    shadowing = _shadow_campaign(model, shadow_directions)

    radius_summary = radius["summary"]
    jacobian_summary = jacobian["summary"]
    immersion_summary = immersion["summary"]
    shadow_summary = shadowing["summary"]
    minimum_population = min(
        radius_summary["minimum_population"],
        jacobian_summary["minimum_population"],
        immersion_summary["minimum_population"],
        shadow_summary["minimum_population"],
    )
    serializable_probe = {
        "coefficient_hashes": coefficient_hashes,
        "direction_registration": direction_registration,
        "radius": radius,
        "jacobian": jacobian,
        "immersion": immersion,
        "near_resonance": near_resonance,
        "shadowing": shadowing,
    }
    finite_probe = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)
    validity_gates = {
        "sealed_coefficient_identity": {
            "value": coefficient_hashes,
            "threshold": REGISTERED_COEFFICIENT_HASHES,
            "passed": coefficient_hashes == REGISTERED_COEFFICIENT_HASHES,
        },
        "registered_direction_integrity": {
            "value": {
                "maximum_norm_error": direction_registration[
                    "maximum_norm_error"
                ],
                "duplicate_count": direction_registration["duplicate_count"],
            },
            "threshold": {
                "maximum_norm_error": DIRECTION_NORM_TOLERANCE,
                "duplicate_count": 0,
            },
            "passed": (
                direction_registration["maximum_norm_error"]
                <= DIRECTION_NORM_TOLERANCE
                and direction_registration["duplicate_count"] == 0
            ),
        },
        "analytic_chart_jacobian": {
            "value": {
                "minimum_analytic_action_norm": jacobian_summary[
                    "minimum_analytic_action_norm"
                ],
                "maximum_best_relative_error": jacobian_summary[
                    "maximum_best_relative_error"
                ],
            },
            "threshold": {
                "minimum_analytic_action_norm_strictly_greater_than": (
                    MINIMUM_JACOBIAN_ACTION_NORM
                ),
                "maximum_best_relative_error": (
                    MAXIMUM_JACOBIAN_RELATIVE_ERROR
                ),
            },
            "passed": (
                jacobian_summary["minimum_analytic_action_norm"]
                > MINIMUM_JACOBIAN_ACTION_NORM
                and jacobian_summary["maximum_best_relative_error"]
                <= MAXIMUM_JACOBIAN_RELATIVE_ERROR
            ),
        },
        "near_resonant_subset_reproduction": {
            "value": near_resonance["near_resonant_triple_count"],
            "threshold": REGISTERED_NEAR_RESONANT_TRIPLE_COUNT,
            "passed": near_resonance["near_resonant_triple_count"]
            == REGISTERED_NEAR_RESONANT_TRIPLE_COUNT,
        },
        "finite_positive_and_strict_json": {
            "value": {
                "minimum_population": minimum_population,
                "all_values_finite": finite_probe,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "minimum_population_strictly_greater_than": 0.0,
                "all_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": minimum_population > 0.0 and finite_probe and strict_json,
        },
    }

    residual_slopes_passed = (
        radius_summary["minimum_quadratic_slope"]
        >= QUADRATIC_SLOPE_RANGE[0]
        and radius_summary["maximum_quadratic_slope"]
        <= QUADRATIC_SLOPE_RANGE[1]
        and radius_summary["minimum_cubic_slope"] >= CUBIC_SLOPE_RANGE[0]
        and radius_summary["maximum_cubic_slope"] <= CUBIC_SLOPE_RANGE[1]
    )
    ratio_slopes_passed = (
        radius_summary["minimum_ratio_slope"] >= RATIO_SLOPE_RANGE[0]
        and radius_summary["maximum_ratio_slope"] <= RATIO_SLOPE_RANGE[1]
    )
    maximum_shadow_ratios = shadow_summary[
        "maximum_directional_improvement_ratios"
    ]
    hypothesis_gates = {
        "independent_residual_orders": {
            "value": {
                "quadratic_slope_range": [
                    radius_summary["minimum_quadratic_slope"],
                    radius_summary["maximum_quadratic_slope"],
                ],
                "cubic_slope_range": [
                    radius_summary["minimum_cubic_slope"],
                    radius_summary["maximum_cubic_slope"],
                ],
            },
            "threshold": {
                "quadratic_slope_range": list(QUADRATIC_SLOPE_RANGE),
                "cubic_slope_range": list(CUBIC_SLOPE_RANGE),
            },
            "passed": residual_slopes_passed,
        },
        "linear_residual_ratio_scaling": {
            "value": [
                radius_summary["minimum_ratio_slope"],
                radius_summary["maximum_ratio_slope"],
            ],
            "threshold": list(RATIO_SLOPE_RANGE),
            "passed": ratio_slopes_passed,
        },
        "acceptance_radius_residual_ratio": {
            "value": radius_summary["maximum_acceptance_radius_ratio"],
            "threshold": MAXIMUM_RADIUS_RESIDUAL_RATIO,
            "passed": radius_summary["maximum_acceptance_radius_ratio"]
            <= MAXIMUM_RADIUS_RESIDUAL_RATIO,
        },
        "registered_radial_immersion": {
            "value": immersion_summary[
                "minimum_normalized_singular_value"
            ],
            "threshold": MINIMUM_NORMALIZED_SINGULAR_VALUE,
            "passed": immersion_summary["minimum_normalized_singular_value"]
            >= MINIMUM_NORMALIZED_SINGULAR_VALUE,
        },
        "independent_shadowing_ratios": {
            "value": maximum_shadow_ratios,
            "threshold": {
                key: MAXIMUM_SHADOW_RATIO for key in maximum_shadow_ratios
            },
            "passed": all(
                value <= MAXIMUM_SHADOW_RATIO
                for value in maximum_shadow_ratios.values()
            ),
        },
        "shadowing_forward_error_budget": {
            "value": {
                "component_check_count": shadow_summary[
                    "cubic_budget_component_check_count"
                ],
                "violation_count": shadow_summary[
                    "cubic_budget_violation_count"
                ],
                "maximum_final_component_budget": shadow_summary[
                    "maximum_final_component_budget"
                ],
            },
            "threshold": {
                "component_check_count": (
                    SHADOW_RADIUS_DIRECTION_COUNT
                    * SHADOW_RADIUS_STEPS
                    * len(COMPONENT_NAMES)
                ),
                "violation_count": 0,
                "maximum_final_component_budget": (
                    MAXIMUM_FINAL_COMPONENT_BUDGET
                ),
            },
            "passed": (
                shadow_summary["cubic_budget_component_check_count"]
                == SHADOW_RADIUS_DIRECTION_COUNT
                * SHADOW_RADIUS_STEPS
                * len(COMPONENT_NAMES)
                and shadow_summary["cubic_budget_violation_count"] == 0
                and shadow_summary["maximum_final_component_budget"]
                <= MAXIMUM_FINAL_COMPONENT_BUDGET
            ),
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q007b1 cubic-radius validity failure"
        decision = (
            "A coefficient-identity, direction, analytic-Jacobian, near-"
            "resonant subset, finiteness, positivity, or serialization gate failed."
        )
        next_change = (
            "Repair the first Q007b1 validity failure without tuning the sealed "
            "radius or immersion gates."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "registered cubic improvement radius localized without fold signature"
        )
        decision = (
            "Independent directions support the registered radius, linear ratio "
            "scaling, radial immersion, shadowing, and forward-error gates."
        )
        next_change = (
            "Use the frozen near-resonant diagnostic to preregister the next "
            "mechanism gate; do not revise Q007b or start quartic fitting yet."
        )
    else:
        outcome = "rejected"
        classification = "registered cubic radius not supported"
        decision = (
            "The audit is valid, but at least one independent radius, scaling, "
            "immersion, shadowing, or forward-error gate fails."
        )
        next_change = (
            "Freeze the first Q007b1 performance witness and reassess the cubic "
            "chart before any degree continuation."
        )
    return {
        "question": (
            "Do independent directions support tenfold cubic residual improvement "
            "through radius 0.004 and radial immersion through radius 0.01?"
        ),
        "hypothesis": (
            "The sealed cubic chart passes residual, linear-ratio, immersion, "
            "shadowing, and forward-error gates on the registered holdouts."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.quadratic.omega,
            "eta": model.quadratic.eta,
            "real_reduced_dimension": model.reduced_dimension,
            "calibration_source": "Q007b post-hoc maximum-ratio ladder only",
            "calibration_directions_reused_for_gates": False,
            "acceptance_radius": RADIUS_ACCEPTANCE_AMPLITUDE,
            "physical_dense_cubic_tensor_materialized": False,
        },
        "coefficient_hashes": coefficient_hashes,
        "direction_registration": direction_registration,
        "radius_campaign": radius,
        "jacobian_validity_campaign": jacobian,
        "immersion_campaign": immersion,
        "near_resonant_diagnostic": near_resonance,
        "shadowing_campaign": shadowing,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "preserved_prior_outcomes": {
            "q006i": "rejected",
            "q007b_at_amplitude_0_01": "rejected",
            "revised": False,
        },
        "claim_boundary": (
            "The result concerns only 64 residual/immersion and 32 shadowing "
            "directions on one finite grid. It does not cover the full radius-"
            "0.004 ball, does not revise Q007b at amplitude 0.01, and is not a "
            "quartic, TT, grid-uniform, existence, uniqueness, injectivity, or "
            "normal-attraction claim."
        ),
    }
