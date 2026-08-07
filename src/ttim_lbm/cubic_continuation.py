"""Sealed Q007b cubic-coefficient, residual, and shadowing audit."""

from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from typing import Any

import numpy as np
import numpy.typing as npt

from .conservation_drift import compensated_conserved_quantities
from .cubic_chart import Full2DCubicModel, build_full2d_cubic_model
from .cubic_prequalification import REGISTERED_TRIPLE_COUNT
from .d2q9 import conserved_moment_matrix
from .forward_error_budget import COMPONENT_NAMES
from .full2d_chart import (
    REDUCED_DIMENSION,
    RESIDUAL_SEED,
    SHADOW_SEED,
    _conjugate_mode_indices,
    _quarter_turn_field,
)
from .manifold import log_log_slope

Array = npt.NDArray[np.float64]

DERIVATIVE_SEED = 20260814
DERIVATIVE_DIRECTION_COUNT = 16
DERIVATIVE_STEPS = (0.02, 0.01, 0.005, 0.0025, 0.00125)
MINIMUM_ANALYTIC_DERIVATIVE_NORM = 1.0e-12
MAXIMUM_DERIVATIVE_RELATIVE_ERROR = 5.0e-4

REGISTERED_TRIPLE_SECTOR_COUNTS = {
    "zero_wave_kinetic": 108,
    "internal_selected": 1044,
    "external": 1448,
}
REGISTERED_MAXIMUM_CONDITION_NUMBER = 10821.814847751179
REPRODUCTION_RELATIVE_TOLERANCE = 1.0e-10
COEFFICIENT_RELATIVE_TOLERANCE = 1.0e-10

C4_SEED = 20260817
C4_DIRECTION_COUNT = 16
C4_AMPLITUDE = 0.01
C4_RELATIVE_TOLERANCE = 1.0e-10

RESIDUAL_ORDER_SEED = 20260815
RESIDUAL_DIRECTION_COUNT = 32
RESIDUAL_AMPLITUDES = (0.00125, 0.0025, 0.005, 0.0075, 0.01)
QUADRATIC_SLOPE_RANGE = (2.9, 3.1)
CUBIC_SLOPE_RANGE = (3.85, 4.15)
MAXIMUM_RESIDUAL_RATIO = 0.10

SHADOWING_SEED = 20260816
SHADOWING_DIRECTION_COUNT = 32
SHADOWING_AMPLITUDE = 0.01
SHADOWING_STEPS = 100
MAXIMUM_SHADOWING_RATIO = 0.8
MAXIMUM_FINAL_COMPONENT_BUDGET = 1.2e-11
CONSERVATION_SENSITIVE_STAGE_COUNT = 2

DIRECTION_NORM_TOLERANCE = 5.0e-15


def _normalized_directions(seed: int, count: int, dimension: int) -> Array:
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, dimension))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
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


def _relative_scalar_error(value: float, reference: float) -> float:
    return float(
        abs(float(value) - float(reference))
        / max(abs(float(reference)), np.finfo(float).eps)
    )


def _all_numeric_values_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_numeric_values_finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_all_numeric_values_finite(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return bool(np.isfinite(value))
    if isinstance(value, (complex, np.complexfloating)):
        return bool(np.isfinite(value.real) and np.isfinite(value.imag))
    return True


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def _direction_registration() -> dict[str, Any]:
    specifications = (
        ("derivative", DERIVATIVE_SEED, DERIVATIVE_DIRECTION_COUNT),
        ("c4", C4_SEED, C4_DIRECTION_COUNT),
        ("residual", RESIDUAL_ORDER_SEED, RESIDUAL_DIRECTION_COUNT),
        ("shadowing", SHADOWING_SEED, SHADOWING_DIRECTION_COUNT),
    )
    records = []
    directions_by_name: dict[str, Array] = {}
    for name, seed, count in specifications:
        directions = _normalized_directions(seed, count, REDUCED_DIMENSION)
        directions_by_name[name] = directions
        records.append(
            {
                "campaign": name,
                "seed": seed,
                "direction_count": count,
                "direction_sha256": _array_hash(directions),
                "maximum_norm_error": float(
                    np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0))
                ),
            }
        )

    reference_groups = {
        "q006i_residual": _normalized_directions(
            RESIDUAL_SEED,
            64,
            REDUCED_DIMENSION,
        ),
        "q006i_shadowing": _normalized_directions(
            SHADOW_SEED,
            32,
            REDUCED_DIMENSION,
        ),
    }
    duplicate_records = []
    seen: list[tuple[str, int, Array]] = []
    for group_name, directions in {
        **reference_groups,
        **directions_by_name,
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
        "campaign_records": records,
        "q006i_reference_seeds": {
            "residual": RESIDUAL_SEED,
            "shadowing": SHADOW_SEED,
        },
        "q006i_reference_hashes": {
            name: _array_hash(directions)
            for name, directions in reference_groups.items()
        },
        "maximum_norm_error": max(
            record["maximum_norm_error"] for record in records
        ),
        "duplicate_count": len(duplicate_records),
        "duplicate_records": duplicate_records,
    }


def _independent_derivative_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    base = model.quadratic.chart.base
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        physical_direction = model.quadratic.chart.tangent @ direction
        analytic = model.analytic_map_third_action(direction)
        step_records = []
        for step in DERIVATIVE_STEPS:
            states = {
                multiplier: base + multiplier * step * physical_direction
                for multiplier in (2, 1, -1, -2)
            }
            mapped = {
                multiplier: model.quadratic.full_map(state)
                for multiplier, state in states.items()
            }
            finite_difference = (
                mapped[2]
                - 2.0 * mapped[1]
                + 2.0 * mapped[-1]
                - mapped[-2]
            ) / (2.0 * step**3)
            relative_error = _relative_norm(
                finite_difference - analytic,
                analytic,
            )
            trial_minimum = min(
                *(float(np.min(state)) for state in states.values()),
                *(float(np.min(state)) for state in mapped.values()),
            )
            minimum_population = min(minimum_population, trial_minimum)
            finite = bool(
                all(np.all(np.isfinite(state)) for state in states.values())
                and all(np.all(np.isfinite(state)) for state in mapped.values())
                and np.all(np.isfinite(finite_difference))
                and np.isfinite(relative_error)
            )
            all_values_finite = all_values_finite and finite
            step_records.append(
                {
                    "step": step,
                    "finite_difference_norm": float(
                        np.linalg.norm(finite_difference)
                    ),
                    "relative_error": relative_error,
                    "minimum_population": trial_minimum,
                    "all_values_finite": finite,
                }
            )
        best = min(step_records, key=lambda record: record["relative_error"])
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "analytic_derivative_norm": float(np.linalg.norm(analytic)),
                "best_step": best["step"],
                "minimum_relative_error": best["relative_error"],
                "step_records": step_records,
            }
        )
    return {
        "seed": DERIVATIVE_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "steps": list(DERIVATIVE_STEPS),
        "formula": (
            "(Phi(f+2hv)-2Phi(f+hv)+2Phi(f-hv)-Phi(f-2hv))/(2h^3)"
        ),
        "direction_records": records,
        "summary": {
            "minimum_analytic_derivative_norm": min(
                record["analytic_derivative_norm"] for record in records
            ),
            "maximum_best_relative_error": max(
                record["minimum_relative_error"] for record in records
            ),
            "worst_direction_index": int(
                max(
                    range(len(records)),
                    key=lambda index: records[index]["minimum_relative_error"],
                )
            ),
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _coefficient_conjugacy_audit(model: Full2DCubicModel) -> dict[str, Any]:
    conjugate_indices = _conjugate_mode_indices(
        list(model.modes),
        model.lookup,
        model.size,
    )
    triple_lookup = {
        tuple(int(value) for value in triple): triple_index
        for triple_index, triple in enumerate(model.triple_indices)
    }
    conjugate_triple_indices = []
    missing_records = []
    for triple_index, triple in enumerate(model.triple_indices):
        conjugate_triple = tuple(
            sorted(int(conjugate_indices[index]) for index in triple)
        )
        if conjugate_triple not in triple_lookup:
            missing_records.append(
                {
                    "triple_index": triple_index,
                    "conjugate_input_indices": list(conjugate_triple),
                }
            )
        else:
            conjugate_triple_indices.append(triple_lookup[conjugate_triple])
    if missing_records:
        return {
            "missing_conjugate_count": len(missing_records),
            "missing_conjugate_records": missing_records,
            "chart_coefficient_relative_residual": float("inf"),
            "reduced_coefficient_relative_residual": float("inf"),
            "forcing_relative_residual": float("inf"),
            "maximum_coefficient_conjugacy_relative_residual": float("inf"),
        }

    conjugate_triples = np.asarray(conjugate_triple_indices, dtype=np.int64)
    chart_error = (
        model.cubic_coefficients[conjugate_triples]
        - np.conjugate(model.cubic_coefficients)
    )
    forcing_error = (
        model.forcing_coefficients[conjugate_triples]
        - np.conjugate(model.forcing_coefficients)
    )
    reduced_error = (
        model.reduced_cubic_coefficients[conjugate_triples][
            :, conjugate_indices
        ]
        - np.conjugate(model.reduced_cubic_coefficients)
    )
    chart_residual = _relative_norm(chart_error, model.cubic_coefficients)
    reduced_residual = _relative_norm(
        reduced_error,
        model.reduced_cubic_coefficients,
    )
    forcing_residual = _relative_norm(forcing_error, model.forcing_coefficients)
    return {
        "missing_conjugate_count": 0,
        "missing_conjugate_records": [],
        "chart_coefficient_relative_residual": chart_residual,
        "reduced_coefficient_relative_residual": reduced_residual,
        "forcing_relative_residual": forcing_residual,
        "maximum_coefficient_conjugacy_relative_residual": max(
            chart_residual,
            reduced_residual,
        ),
    }


def _coefficient_campaign(model: Full2DCubicModel) -> dict[str, Any]:
    records = list(model.coefficient_records)
    sector_counts = dict(
        Counter(record["output_kind"] for record in records)
    )
    singular_count = sum(record["numerically_singular"] for record in records)
    condition_numbers = [
        float(record["condition_number"])
        for record in records
        if record["condition_number"] is not None
    ]
    maximum_condition_number = max(condition_numbers)
    condition_relative_error = _relative_scalar_error(
        maximum_condition_number,
        REGISTERED_MAXIMUM_CONDITION_NUMBER,
    )
    conjugacy = _coefficient_conjugacy_audit(model)
    arrays_finite = bool(
        np.all(np.isfinite(model.cubic_coefficients))
        and np.all(np.isfinite(model.reduced_cubic_coefficients))
        and np.all(np.isfinite(model.forcing_coefficients))
    )
    summary = {
        "triple_count": len(records),
        "sector_counts": sector_counts,
        "numerically_singular_block_count": int(singular_count),
        "maximum_condition_number": maximum_condition_number,
        "registered_maximum_condition_number": (
            REGISTERED_MAXIMUM_CONDITION_NUMBER
        ),
        "maximum_condition_number_relative_error": condition_relative_error,
        "maximum_solve_relative_residual": max(
            record["solve_relative_residual"] for record in records
        ),
        "maximum_homological_relative_residual": max(
            record["homological_relative_residual"] for record in records
        ),
        "maximum_graph_gauge_relative_residual": max(
            record["graph_gauge_relative_residual"] for record in records
        ),
        "maximum_zero_wave_forcing_conservation_relative_residual": max(
            record["zero_wave_forcing_conservation_relative_residual"]
            for record in records
        ),
        "maximum_zero_wave_coefficient_conservation_relative_residual": max(
            record["zero_wave_coefficient_conservation_relative_residual"]
            for record in records
        ),
        "maximum_fixed_leaf_subspace_invariance_residual": max(
            record["fixed_leaf_subspace_invariance_residual"]
            for record in records
        ),
        "forcing_frobenius_norm": float(
            np.linalg.norm(model.forcing_coefficients)
        ),
        "chart_coefficient_frobenius_norm": float(
            np.linalg.norm(model.cubic_coefficients)
        ),
        "reduced_coefficient_frobenius_norm": float(
            np.linalg.norm(model.reduced_cubic_coefficients)
        ),
        "maximum_forcing_norm": max(
            record["forcing_norm"] for record in records
        ),
        "maximum_chart_coefficient_norm": max(
            record["coefficient_norm"] for record in records
        ),
        "maximum_reduced_coefficient_norm": max(
            record["reduced_coefficient_norm"] for record in records
        ),
        "all_coefficient_arrays_finite": arrays_finite,
        "all_coefficient_records_finite": _all_numeric_values_finite(records),
    }
    return {
        "representation": (
            "symmetric complex Fourier fibers with unordered triples and "
            "permutation multiplicities; no full physical dense cubic tensor"
        ),
        "coefficient_hashes": model.coefficient_hashes(),
        "conjugacy_audit": conjugacy,
        "summary": summary,
        "triple_records": records,
    }


def _c4_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    size = model.size
    tangent = model.quadratic.chart.tangent
    rotated_tangent = _quarter_turn_field(
        tangent.reshape(size, size, 9, model.reduced_dimension),
        size,
    ).reshape(size * size * 9, model.reduced_dimension)
    coordinate_rotation = model.quadratic.extractor @ rotated_tangent
    base = model.quadratic.chart.base
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        coordinates = C4_AMPLITUDE * direction
        rotated_coordinates = coordinate_rotation @ coordinates
        chart_value = model.chart_evaluate(coordinates)
        rotated_chart = _quarter_turn_field(
            chart_value.reshape(size, size, 9),
            size,
        ).ravel()
        transformed_chart = model.chart_evaluate(rotated_coordinates)
        chart_error = _relative_norm(
            rotated_chart - transformed_chart,
            transformed_chart - base,
        )
        reduced_value = model.reduced_map(coordinates)
        rotated_reduced = coordinate_rotation @ reduced_value
        transformed_reduced = model.reduced_map(rotated_coordinates)
        reduced_error = _relative_norm(
            rotated_reduced - transformed_reduced,
            transformed_reduced,
        )
        complex_field = model.complex_cubic_field(coordinates)
        imaginary_leakage = _relative_norm(
            complex_field.imag,
            complex_field.real,
        )
        mapped_chart = model.quadratic.full_map(chart_value)
        mapped_transformed = model.quadratic.full_map(transformed_chart)
        trial_minimum = min(
            float(np.min(chart_value)),
            float(np.min(rotated_chart)),
            float(np.min(transformed_chart)),
            float(np.min(mapped_chart)),
            float(np.min(mapped_transformed)),
        )
        minimum_population = min(minimum_population, trial_minimum)
        finite = bool(
            all(
                np.all(np.isfinite(value))
                for value in (
                    chart_value,
                    rotated_chart,
                    transformed_chart,
                    reduced_value,
                    rotated_reduced,
                    transformed_reduced,
                    complex_field,
                    mapped_chart,
                    mapped_transformed,
                )
            )
            and np.isfinite(chart_error)
            and np.isfinite(reduced_error)
            and np.isfinite(imaginary_leakage)
        )
        all_values_finite = all_values_finite and finite
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "chart_relative_error": chart_error,
                "reduced_map_relative_error": reduced_error,
                "cubic_field_imaginary_leakage_relative_norm": (
                    imaginary_leakage
                ),
                "minimum_population": trial_minimum,
                "all_values_finite": finite,
            }
        )
    orthogonality_error = float(
        np.linalg.norm(
            coordinate_rotation.T @ coordinate_rotation
            - np.eye(model.reduced_dimension)
        )
    )
    order_four_error = float(
        np.linalg.norm(
            np.linalg.matrix_power(coordinate_rotation, 4)
            - np.eye(model.reduced_dimension)
        )
    )
    return {
        "seed": C4_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitude": C4_AMPLITUDE,
        "coordinate_rotation_orthogonality_error": orthogonality_error,
        "coordinate_rotation_order_four_error": order_four_error,
        "direction_records": records,
        "summary": {
            "maximum_chart_relative_error": max(
                record["chart_relative_error"] for record in records
            ),
            "maximum_reduced_map_relative_error": max(
                record["reduced_map_relative_error"] for record in records
            ),
            "maximum_cubic_field_imaginary_leakage_relative_norm": max(
                record["cubic_field_imaginary_leakage_relative_norm"]
                for record in records
            ),
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _residual_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    amplitudes = np.asarray(RESIDUAL_AMPLITUDES, dtype=np.float64)
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        quadratic_residuals = []
        cubic_residuals = []
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
            quadratic_residuals.append(
                float(np.linalg.norm(quadratic_mapped - quadratic_predicted))
            )
            cubic_residuals.append(
                float(np.linalg.norm(cubic_mapped - cubic_predicted))
            )
            values = (
                quadratic_lifted,
                quadratic_mapped,
                quadratic_predicted,
                cubic_lifted,
                cubic_mapped,
                cubic_predicted,
            )
            direction_minimum = min(
                direction_minimum,
                *(float(np.min(value)) for value in values),
            )
            direction_finite = direction_finite and all(
                np.all(np.isfinite(value)) for value in values
            )
        quadratic_slope = log_log_slope(
            amplitudes[1:],
            quadratic_residuals[1:],
        )
        cubic_slope = log_log_slope(
            amplitudes[1:],
            cubic_residuals[1:],
        )
        ratio = float(cubic_residuals[-1] / quadratic_residuals[-1])
        direction_finite = bool(
            direction_finite
            and np.isfinite(quadratic_slope)
            and np.isfinite(cubic_slope)
            and np.isfinite(ratio)
        )
        minimum_population = min(minimum_population, direction_minimum)
        all_values_finite = all_values_finite and direction_finite
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "quadratic_residuals": quadratic_residuals,
                "cubic_residuals": cubic_residuals,
                "quadratic_slope_last_four": quadratic_slope,
                "cubic_slope_last_four": cubic_slope,
                "maximum_amplitude_cubic_to_quadratic_ratio": ratio,
                "minimum_population": float(direction_minimum),
                "all_values_finite": direction_finite,
            }
        )
    worst_ratio_index = max(
        range(len(records)),
        key=lambda index: records[index][
            "maximum_amplitude_cubic_to_quadratic_ratio"
        ],
    )
    return {
        "seed": RESIDUAL_ORDER_SEED,
        "q006i_seed_reused": RESIDUAL_ORDER_SEED == RESIDUAL_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitudes": amplitudes.tolist(),
        "slope_fit_amplitudes": amplitudes[1:].tolist(),
        "direction_records": records,
        "summary": {
            "minimum_quadratic_slope": min(
                record["quadratic_slope_last_four"] for record in records
            ),
            "maximum_quadratic_slope": max(
                record["quadratic_slope_last_four"] for record in records
            ),
            "minimum_cubic_slope": min(
                record["cubic_slope_last_four"] for record in records
            ),
            "maximum_cubic_slope": max(
                record["cubic_slope_last_four"] for record in records
            ),
            "maximum_directional_residual_ratio": records[worst_ratio_index][
                "maximum_amplitude_cubic_to_quadratic_ratio"
            ],
            "worst_residual_ratio_direction_index": worst_ratio_index,
            "residual_ratio_failure_count": sum(
                record["maximum_amplitude_cubic_to_quadratic_ratio"]
                > MAXIMUM_RESIDUAL_RATIO
                for record in records
            ),
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _component_scales(state: Array, moment_matrix: Array) -> Array:
    tensor = np.asarray(state, dtype=np.float64).reshape(state.shape[0], -1, 9)
    contributions = moment_matrix[:, None, None, :] * tensor[None, :, :, :]
    return np.asarray(
        np.sum(np.abs(contributions), axis=(1, 2, 3)),
        dtype=np.float64,
    )


def _shadow_rollout(
    model: Full2DCubicModel,
    direction: Array,
    direction_index: int,
    *,
    cubic: bool,
) -> dict[str, Any]:
    coordinates = SHADOWING_AMPLITUDE * direction
    state = model.chart_evaluate(coordinates, cubic=cubic)
    base = model.quadratic.chart.base
    minimum_population = np.inf
    maximum_absolute_error = 0.0
    maximum_relative_error = 0.0
    maximum_absolute_error_step = 0
    maximum_relative_error_step = 0
    final_absolute_error = 0.0
    final_relative_error = 0.0
    all_values_finite = True
    absolute_errors = []
    relative_errors = []

    moment_matrix = conserved_moment_matrix()
    budget_records = []
    budget_violation_count = 0
    maximum_budget_utilization = 0.0
    maximum_absolute_conservation_drift = 0.0
    maximum_independent_sum_difference = 0.0
    final_component_budgets = np.zeros(3, dtype=np.float64)
    if cubic:
        initial_tensor = state.reshape(model.size, model.size, 9)
        initial_fsum, initial_neumaier = compensated_conserved_quantities(
            initial_tensor
        )
        component_scales = _component_scales(initial_tensor, moment_matrix)
        component_ulps = np.spacing(component_scales)
        maximum_independent_sum_difference = float(
            np.max(np.abs(initial_fsum - initial_neumaier))
        )
        if np.any(component_ulps <= 0.0):
            raise ValueError("Q007b component scales must have positive ULPs")

    for step in range(SHADOWING_STEPS + 1):
        predicted = model.chart_evaluate(coordinates, cubic=cubic)
        absolute_error = float(np.linalg.norm(state - predicted))
        perturbation_scale = max(
            float(np.linalg.norm(state - base)),
            float(np.linalg.norm(predicted - base)),
            np.finfo(float).eps,
        )
        relative_error = absolute_error / perturbation_scale
        absolute_errors.append(absolute_error)
        relative_errors.append(relative_error)
        if absolute_error > maximum_absolute_error:
            maximum_absolute_error = absolute_error
            maximum_absolute_error_step = step
        if relative_error > maximum_relative_error:
            maximum_relative_error = relative_error
            maximum_relative_error_step = step
        minimum_population = min(
            minimum_population,
            float(np.min(state)),
            float(np.min(predicted)),
        )
        all_values_finite = bool(
            all_values_finite
            and np.all(np.isfinite(state))
            and np.all(np.isfinite(predicted))
            and np.all(np.isfinite(coordinates))
            and np.isfinite(absolute_error)
            and np.isfinite(relative_error)
        )
        if cubic and step > 0:
            tensor = state.reshape(model.size, model.size, 9)
            current_fsum, current_neumaier = compensated_conserved_quantities(
                tensor
            )
            drift = current_fsum - initial_fsum
            absolute_drift = np.abs(drift)
            budgets = (
                CONSERVATION_SENSITIVE_STAGE_COUNT * step * component_ulps
            )
            utilizations = absolute_drift / budgets
            violations = absolute_drift > budgets
            budget_violation_count += int(np.count_nonzero(violations))
            maximum_budget_utilization = max(
                maximum_budget_utilization,
                float(np.max(utilizations)),
            )
            maximum_absolute_conservation_drift = max(
                maximum_absolute_conservation_drift,
                float(np.max(absolute_drift)),
            )
            maximum_independent_sum_difference = max(
                maximum_independent_sum_difference,
                float(np.max(np.abs(current_fsum - current_neumaier))),
            )
            budget_records.append(
                {
                    "step": step,
                    "signed_drift": drift.tolist(),
                    "absolute_drift": absolute_drift.tolist(),
                    "component_budget": budgets.tolist(),
                    "budget_utilization": utilizations.tolist(),
                    "violation_components": [
                        COMPONENT_NAMES[index]
                        for index in np.flatnonzero(violations)
                    ],
                }
            )
            if step == SHADOWING_STEPS:
                final_component_budgets = budgets
        if step == SHADOWING_STEPS:
            final_absolute_error = absolute_error
            final_relative_error = relative_error
        else:
            state = model.quadratic.full_map(state)
            coordinates = model.reduced_map(coordinates, cubic=cubic)

    result = {
        "chart": "cubic" if cubic else "quadratic",
        "direction_index": direction_index,
        "direction": direction.tolist(),
        "maximum_absolute_error": maximum_absolute_error,
        "maximum_absolute_error_step": maximum_absolute_error_step,
        "maximum_perturbation_relative_error": maximum_relative_error,
        "maximum_relative_error_step": maximum_relative_error_step,
        "final_absolute_error": final_absolute_error,
        "final_perturbation_relative_error": final_relative_error,
        "minimum_population": float(minimum_population),
        "all_values_finite": all_values_finite,
        "absolute_error_by_step": absolute_errors,
        "perturbation_relative_error_by_step": relative_errors,
    }
    if cubic:
        result["conservation_budget"] = {
            "component_names": list(COMPONENT_NAMES),
            "component_scale": component_scales.tolist(),
            "component_ulp": component_ulps.tolist(),
            "step_records": budget_records,
            "component_check_count": len(budget_records) * len(COMPONENT_NAMES),
            "violation_count": budget_violation_count,
            "maximum_budget_utilization": maximum_budget_utilization,
            "maximum_absolute_drift": maximum_absolute_conservation_drift,
            "maximum_independent_sum_difference": (
                maximum_independent_sum_difference
            ),
            "final_component_budgets": final_component_budgets.tolist(),
            "maximum_final_component_budget": float(
                np.max(final_component_budgets)
            ),
        }
    return result


def _shadowing_campaign(
    model: Full2DCubicModel,
    directions: Array,
) -> dict[str, Any]:
    records = []
    total_budget_violations = 0
    total_component_checks = 0
    maximum_final_component_budget = 0.0
    maximum_budget_utilization = 0.0
    maximum_absolute_drift = 0.0
    maximum_independent_sum_difference = 0.0
    for direction_index, direction in enumerate(directions):
        quadratic = _shadow_rollout(
            model,
            direction,
            direction_index,
            cubic=False,
        )
        cubic = _shadow_rollout(
            model,
            direction,
            direction_index,
            cubic=True,
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
        maximum_absolute_drift = max(
            maximum_absolute_drift,
            budget["maximum_absolute_drift"],
        )
        maximum_independent_sum_difference = max(
            maximum_independent_sum_difference,
            budget["maximum_independent_sum_difference"],
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
        "seed": SHADOWING_SEED,
        "q006i_seed_reused": SHADOWING_SEED == SHADOW_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitude": SHADOWING_AMPLITUDE,
        "steps": SHADOWING_STEPS,
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
                    record["improvement_ratios"][key]
                    > MAXIMUM_SHADOWING_RATIO
                    for record in records
                )
                for key in ratio_keys
            },
            "cubic_budget_component_check_count": total_component_checks,
            "cubic_budget_violation_count": total_budget_violations,
            "maximum_cubic_budget_utilization": maximum_budget_utilization,
            "maximum_cubic_absolute_conservation_drift": (
                maximum_absolute_drift
            ),
            "maximum_independent_sum_difference": (
                maximum_independent_sum_difference
            ),
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


def run_cubic_continuation_audit() -> dict[str, Any]:
    """Run the fully sealed Q007b construction and held-out campaigns."""

    model = build_full2d_cubic_model()
    direction_registration = _direction_registration()
    derivative_directions = _normalized_directions(
        DERIVATIVE_SEED,
        DERIVATIVE_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    c4_directions = _normalized_directions(
        C4_SEED,
        C4_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    residual_directions = _normalized_directions(
        RESIDUAL_ORDER_SEED,
        RESIDUAL_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    shadowing_directions = _normalized_directions(
        SHADOWING_SEED,
        SHADOWING_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    derivative = _independent_derivative_campaign(model, derivative_directions)
    coefficients = _coefficient_campaign(model)
    c4 = _c4_campaign(model, c4_directions)
    residual = _residual_campaign(model, residual_directions)
    shadowing = _shadowing_campaign(model, shadowing_directions)

    coefficient_summary = coefficients["summary"]
    conjugacy = coefficients["conjugacy_audit"]
    residual_summary = residual["summary"]
    shadowing_summary = shadowing["summary"]
    minimum_population = min(
        derivative["summary"]["minimum_population"],
        c4["summary"]["minimum_population"],
        residual_summary["minimum_population"],
        shadowing_summary["minimum_population"],
    )
    serializable_probe = {
        "direction_registration": direction_registration,
        "independent_derivative": derivative,
        "coefficients": coefficients,
        "c4_equivariance": c4,
        "residual_order": residual,
        "shadowing": shadowing,
    }
    finite_probe = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)

    validity_gates = {
        "registered_direction_integrity": {
            "value": {
                "maximum_norm_error": direction_registration[
                    "maximum_norm_error"
                ],
                "duplicate_count": direction_registration["duplicate_count"],
                "q006i_residual_seed_reused": residual[
                    "q006i_seed_reused"
                ],
                "q006i_shadow_seed_reused": shadowing[
                    "q006i_seed_reused"
                ],
            },
            "threshold": {
                "maximum_norm_error": DIRECTION_NORM_TOLERANCE,
                "duplicate_count": 0,
                "q006i_residual_seed_reused": False,
                "q006i_shadow_seed_reused": False,
            },
            "passed": (
                direction_registration["maximum_norm_error"]
                <= DIRECTION_NORM_TOLERANCE
                and direction_registration["duplicate_count"] == 0
                and not residual["q006i_seed_reused"]
                and not shadowing["q006i_seed_reused"]
            ),
        },
        "independent_third_derivative": {
            "value": {
                "minimum_analytic_derivative_norm": derivative["summary"][
                    "minimum_analytic_derivative_norm"
                ],
                "maximum_best_relative_error": derivative["summary"][
                    "maximum_best_relative_error"
                ],
            },
            "threshold": {
                "minimum_analytic_derivative_norm_strictly_greater_than": (
                    MINIMUM_ANALYTIC_DERIVATIVE_NORM
                ),
                "maximum_best_relative_error": (
                    MAXIMUM_DERIVATIVE_RELATIVE_ERROR
                ),
            },
            "passed": (
                derivative["summary"]["minimum_analytic_derivative_norm"]
                > MINIMUM_ANALYTIC_DERIVATIVE_NORM
                and derivative["summary"]["maximum_best_relative_error"]
                <= MAXIMUM_DERIVATIVE_RELATIVE_ERROR
            ),
        },
        "q007a_triple_reproduction": {
            "value": {
                "triple_count": coefficient_summary["triple_count"],
                "sector_counts": coefficient_summary["sector_counts"],
                "numerically_singular_block_count": coefficient_summary[
                    "numerically_singular_block_count"
                ],
                "maximum_condition_number_relative_error": coefficient_summary[
                    "maximum_condition_number_relative_error"
                ],
            },
            "threshold": {
                "triple_count": REGISTERED_TRIPLE_COUNT,
                "sector_counts": REGISTERED_TRIPLE_SECTOR_COUNTS,
                "numerically_singular_block_count": 0,
                "maximum_condition_number_relative_error": (
                    REPRODUCTION_RELATIVE_TOLERANCE
                ),
            },
            "passed": (
                coefficient_summary["triple_count"] == REGISTERED_TRIPLE_COUNT
                and coefficient_summary["sector_counts"]
                == REGISTERED_TRIPLE_SECTOR_COUNTS
                and coefficient_summary["numerically_singular_block_count"] == 0
                and coefficient_summary[
                    "maximum_condition_number_relative_error"
                ]
                <= REPRODUCTION_RELATIVE_TOLERANCE
            ),
        },
        "coefficient_solve_and_homological_residuals": {
            "value": {
                "maximum_solve_relative_residual": coefficient_summary[
                    "maximum_solve_relative_residual"
                ],
                "maximum_homological_relative_residual": coefficient_summary[
                    "maximum_homological_relative_residual"
                ],
            },
            "threshold": COEFFICIENT_RELATIVE_TOLERANCE,
            "passed": (
                coefficient_summary["maximum_solve_relative_residual"]
                <= COEFFICIENT_RELATIVE_TOLERANCE
                and coefficient_summary["maximum_homological_relative_residual"]
                <= COEFFICIENT_RELATIVE_TOLERANCE
            ),
        },
        "coefficient_gauge_conjugacy_and_fixed_leaf": {
            "value": {
                "maximum_graph_gauge_relative_residual": coefficient_summary[
                    "maximum_graph_gauge_relative_residual"
                ],
                "maximum_coefficient_conjugacy_relative_residual": conjugacy[
                    "maximum_coefficient_conjugacy_relative_residual"
                ],
                "maximum_zero_wave_forcing_conservation_relative_residual": (
                    coefficient_summary[
                        "maximum_zero_wave_forcing_conservation_relative_residual"
                    ]
                ),
                "maximum_zero_wave_coefficient_conservation_relative_residual": (
                    coefficient_summary[
                        "maximum_zero_wave_coefficient_conservation_relative_residual"
                    ]
                ),
                "maximum_fixed_leaf_subspace_invariance_residual": (
                    coefficient_summary[
                        "maximum_fixed_leaf_subspace_invariance_residual"
                    ]
                ),
            },
            "threshold": COEFFICIENT_RELATIVE_TOLERANCE,
            "passed": (
                conjugacy["missing_conjugate_count"] == 0
                and coefficient_summary[
                    "maximum_graph_gauge_relative_residual"
                ]
                <= COEFFICIENT_RELATIVE_TOLERANCE
                and conjugacy[
                    "maximum_coefficient_conjugacy_relative_residual"
                ]
                <= COEFFICIENT_RELATIVE_TOLERANCE
                and coefficient_summary[
                    "maximum_zero_wave_forcing_conservation_relative_residual"
                ]
                <= COEFFICIENT_RELATIVE_TOLERANCE
                and coefficient_summary[
                    "maximum_zero_wave_coefficient_conservation_relative_residual"
                ]
                <= COEFFICIENT_RELATIVE_TOLERANCE
                and coefficient_summary[
                    "maximum_fixed_leaf_subspace_invariance_residual"
                ]
                <= COEFFICIENT_RELATIVE_TOLERANCE
            ),
        },
        "c4_chart_and_reduced_map_equivariance": {
            "value": {
                "maximum_chart_relative_error": c4["summary"][
                    "maximum_chart_relative_error"
                ],
                "maximum_reduced_map_relative_error": c4["summary"][
                    "maximum_reduced_map_relative_error"
                ],
            },
            "threshold": C4_RELATIVE_TOLERANCE,
            "passed": (
                c4["summary"]["maximum_chart_relative_error"]
                <= C4_RELATIVE_TOLERANCE
                and c4["summary"]["maximum_reduced_map_relative_error"]
                <= C4_RELATIVE_TOLERANCE
            ),
        },
        "finite_positive_and_strict_json": {
            "value": {
                "minimum_population": minimum_population,
                "all_coefficient_arrays_finite": coefficient_summary[
                    "all_coefficient_arrays_finite"
                ],
                "all_campaign_values_finite": finite_probe,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "minimum_population_strictly_greater_than": 0.0,
                "all_coefficient_arrays_finite": True,
                "all_campaign_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": (
                minimum_population > 0.0
                and coefficient_summary["all_coefficient_arrays_finite"]
                and finite_probe
                and strict_json
            ),
        },
    }

    residual_slopes_passed = (
        residual_summary["minimum_quadratic_slope"]
        >= QUADRATIC_SLOPE_RANGE[0]
        and residual_summary["maximum_quadratic_slope"]
        <= QUADRATIC_SLOPE_RANGE[1]
        and residual_summary["minimum_cubic_slope"] >= CUBIC_SLOPE_RANGE[0]
        and residual_summary["maximum_cubic_slope"] <= CUBIC_SLOPE_RANGE[1]
    )
    maximum_shadow_ratios = shadowing_summary[
        "maximum_directional_improvement_ratios"
    ]
    hypothesis_gates = {
        "held_out_residual_orders": {
            "value": {
                "quadratic_slope_range": [
                    residual_summary["minimum_quadratic_slope"],
                    residual_summary["maximum_quadratic_slope"],
                ],
                "cubic_slope_range": [
                    residual_summary["minimum_cubic_slope"],
                    residual_summary["maximum_cubic_slope"],
                ],
            },
            "threshold": {
                "quadratic_slope_range": list(QUADRATIC_SLOPE_RANGE),
                "cubic_slope_range": list(CUBIC_SLOPE_RANGE),
            },
            "passed": residual_slopes_passed,
        },
        "held_out_residual_ratio": {
            "value": residual_summary["maximum_directional_residual_ratio"],
            "threshold": MAXIMUM_RESIDUAL_RATIO,
            "passed": residual_summary["maximum_directional_residual_ratio"]
            <= MAXIMUM_RESIDUAL_RATIO,
        },
        "held_out_directional_shadowing_ratios": {
            "value": maximum_shadow_ratios,
            "threshold": {
                key: MAXIMUM_SHADOWING_RATIO for key in maximum_shadow_ratios
            },
            "passed": all(
                value <= MAXIMUM_SHADOWING_RATIO
                for value in maximum_shadow_ratios.values()
            ),
        },
        "cubic_shadowing_forward_error_budget": {
            "value": {
                "component_check_count": shadowing_summary[
                    "cubic_budget_component_check_count"
                ],
                "violation_count": shadowing_summary[
                    "cubic_budget_violation_count"
                ],
                "maximum_final_component_budget": shadowing_summary[
                    "maximum_final_component_budget"
                ],
            },
            "threshold": {
                "component_check_count": (
                    SHADOWING_DIRECTION_COUNT
                    * SHADOWING_STEPS
                    * len(COMPONENT_NAMES)
                ),
                "violation_count": 0,
                "maximum_final_component_budget": (
                    MAXIMUM_FINAL_COMPONENT_BUDGET
                ),
            },
            "passed": (
                shadowing_summary["cubic_budget_component_check_count"]
                == SHADOWING_DIRECTION_COUNT
                * SHADOWING_STEPS
                * len(COMPONENT_NAMES)
                and shadowing_summary["cubic_budget_violation_count"] == 0
                and shadowing_summary["maximum_final_component_budget"]
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
        classification = "Q007b cubic-continuation validity failure"
        decision = (
            "An independent derivative, coefficient assembly, symmetry, "
            "fixed-leaf, finiteness, positivity, direction, or serialization "
            "validity gate failed."
        )
        next_change = (
            "Repair the first Q007b validity failure without tuning the sealed "
            "performance gates."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "cubic chart improves registered finite-grid invariance and shadowing"
        )
        decision = (
            "The cubic chart passes the registered residual-order, directional "
            "residual-ratio, shadowing-ratio, and forward-error gates."
        )
        next_change = (
            "Preregister Q007c quartic continuation before constructing any "
            "fourth-order coefficient."
        )
    else:
        outcome = "rejected"
        classification = "cubic continuation does not improve the registered chart"
        decision = (
            "The cubic construction is valid, but at least one preregistered "
            "residual or shadowing improvement gate fails."
        )
        next_change = (
            "Freeze the first Q007b performance witnesses and diagnose finite-"
            "radius, near-resonant, or chart-fold effects before increasing degree."
        )
    return {
        "question": (
            "Do all cubic coefficients pass independent construction checks and "
            "improve held-out residual order and 100-step shadowing over Q006i?"
        ),
        "hypothesis": (
            "The registered cubic chart has fourth-order defects, residual ratio "
            "at most 0.10, shadowing ratios at most 0.8, and no Q006o-budget "
            "violation on all held-out directions."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.quadratic.omega,
            "eta": model.quadratic.eta,
            "real_reduced_dimension": model.reduced_dimension,
            "complex_mode_count": len(model.modes),
            "unordered_triple_count": REGISTERED_TRIPLE_COUNT,
            "chart_convention": "W3(a)=W2(a)+T[a,a,a]/6",
            "reduced_map_convention": "R3(a)=R2(a)+K[a,a,a]/6",
            "full_map": "unmodified standard filtered D2Q9 map",
            "physical_dense_cubic_tensor_materialized": False,
        },
        "direction_registration": direction_registration,
        "independent_derivative": derivative,
        "coefficient_construction": coefficients,
        "c4_equivariance": c4,
        "residual_order_campaign": residual,
        "shadowing_campaign": shadowing,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "preserved_prior_outcome": {
            "q006i_scientific_outcome": "rejected",
            "q006i_original_global_conservation_threshold": 1.0e-12,
            "revised": False,
        },
        "claim_boundary": (
            "The outcome is limited to the registered finite grid, directions, "
            "amplitudes, and 100-step horizon. It is not a quartic, TT-compression, "
            "all-radius, grid-uniform, existence, uniqueness, or normal-attraction "
            "claim, and it does not revise the sealed Q006i rejection."
        ),
    }
