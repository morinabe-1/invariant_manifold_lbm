"""Sealed Q007c1 quartic-coefficient, residual, and shadowing audit."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from typing import Any

import numpy as np
import numpy.typing as npt

from .conservation_drift import compensated_conserved_quantities
from .cubic_continuation import (
    C4_DIRECTION_COUNT as CUBIC_C4_DIRECTION_COUNT,
)
from .cubic_continuation import (
    C4_SEED as CUBIC_C4_SEED,
)
from .cubic_continuation import (
    DERIVATIVE_DIRECTION_COUNT as CUBIC_DERIVATIVE_DIRECTION_COUNT,
)
from .cubic_continuation import (
    DERIVATIVE_SEED as CUBIC_DERIVATIVE_SEED,
)
from .cubic_continuation import (
    RESIDUAL_DIRECTION_COUNT as CUBIC_RESIDUAL_DIRECTION_COUNT,
)
from .cubic_continuation import (
    RESIDUAL_ORDER_SEED as CUBIC_RESIDUAL_SEED,
)
from .cubic_continuation import (
    SHADOWING_DIRECTION_COUNT as CUBIC_SHADOW_DIRECTION_COUNT,
)
from .cubic_continuation import (
    SHADOWING_SEED as CUBIC_SHADOW_SEED,
)
from .cubic_continuation import (
    _all_numeric_values_finite,
    _array_hash,
    _component_scales,
    _normalized_directions,
    _relative_norm,
    _relative_scalar_error,
    _strict_json_serializable,
)
from .cubic_prequalification import (
    REGISTERED_PAIR_COUNT,
    REGISTERED_PAIR_MAXIMUM_CONDITION_NUMBER,
    REGISTERED_PAIR_MINIMUM_SINGULAR_VALUE,
    REGISTERED_PAIR_SECTOR_COUNTS,
    REGISTERED_TRIPLE_COUNT,
    _enumerate_records,
    _record_summary,
)
from .cubic_radius import (
    RADIUS_DIRECTION_COUNT,
    RADIUS_SEED,
    REGISTERED_COEFFICIENT_HASHES,
    SHADOW_RADIUS_DIRECTION_COUNT,
    SHADOW_RADIUS_SEED,
    _jacobian_directions,
)
from .d2q9 import conserved_moment_matrix
from .forward_error_budget import COMPONENT_NAMES
from .full2d_chart import (
    HESSIAN_SEED,
    REDUCED_DIMENSION,
    RESIDUAL_SEED,
    SHADOW_SEED,
    _conjugate_mode_indices,
    _quarter_turn_field,
)
from .manifold import log_log_slope
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model
from .quartic_prequalification import (
    REGISTERED_QUARTIC_COUNT,
    REGISTERED_QUARTIC_MULTIPLICITIES,
    REGISTERED_QUARTIC_MULTIPLICITY_SUM,
    REGISTERED_TRIPLE_MAXIMUM_CONDITION_NUMBER,
    REGISTERED_TRIPLE_MINIMUM_SINGULAR_VALUE,
    REGISTERED_TRIPLE_NEAR_RESONANT_COUNT,
    REGISTERED_TRIPLE_SECTOR_COUNTS,
)

Array = npt.NDArray[np.float64]

MAP_DERIVATIVE_SEED = 20260821
MAP_DERIVATIVE_DIRECTION_COUNT = 16
FORCING_DERIVATIVE_SEED = 20260822
FORCING_DERIVATIVE_DIRECTION_COUNT = 16
FOURTH_DIFFERENCE_STEPS = (0.02, 0.015, 0.01, 0.0075, 0.005)
MINIMUM_ANALYTIC_DERIVATIVE_NORM = 1.0e-12
MAXIMUM_MAP_DERIVATIVE_RELATIVE_ERROR = 5.0e-3
MINIMUM_ANALYTIC_FORCING_NORM = 1.0e-12
MAXIMUM_FORCING_DERIVATIVE_RELATIVE_ERROR = 2.0e-2

RESIDUAL_SEED_Q007C1 = 20260823
RESIDUAL_DIRECTION_COUNT = 32
RESIDUAL_AMPLITUDES = (0.00125, 0.0025, 0.005, 0.0075, 0.01)
CUBIC_SLOPE_RANGE = (3.85, 4.15)
QUARTIC_SLOPE_RANGE = (4.70, 5.30)
MAXIMUM_QUARTIC_TO_CUBIC_RESIDUAL_RATIO = 0.8
MAXIMUM_QUARTIC_TO_QUADRATIC_RESIDUAL_RATIO = 0.10

C4_SEED_Q007C1 = 20260824
C4_DIRECTION_COUNT = 16
C4_AMPLITUDE = 0.01
C4_RELATIVE_TOLERANCE = 1.0e-10

SHADOW_SEED_Q007C1 = 20260825
SHADOW_DIRECTION_COUNT = 32
SHADOW_AMPLITUDE = 0.01
SHADOW_STEPS = 100
MAXIMUM_SHADOW_RATIO = 0.8
MAXIMUM_BUDGET_UTILIZATION = 1.0
MAXIMUM_FINAL_COMPONENT_BUDGET = 1.2e-11
CONSERVATION_SENSITIVE_STAGE_COUNT = 2

COEFFICIENT_RELATIVE_TOLERANCE = 1.0e-10
REPRODUCTION_RELATIVE_TOLERANCE = 1.0e-10
DIRECTION_NORM_TOLERANCE = 5.0e-15

REGISTERED_QUARTIC_SECTOR_COUNTS = {
    "zero_wave_kinetic": 846,
    "internal_selected": 4536,
    "external": 12168,
}
REGISTERED_QUARTIC_MINIMUM_SINGULAR_VALUE = 6.485706497181907e-05
REGISTERED_QUARTIC_MAXIMUM_CONDITION_NUMBER = 34673.915552593266


def _direction_registration() -> dict[str, Any]:
    hessian_rng = np.random.default_rng(HESSIAN_SEED)
    hessian_left = hessian_rng.normal(size=(32, REDUCED_DIMENSION))
    hessian_right = hessian_rng.normal(size=(32, REDUCED_DIMENSION))
    hessian_left /= np.linalg.norm(hessian_left, axis=1)[:, None]
    hessian_right /= np.linalg.norm(hessian_right, axis=1)[:, None]
    jacobian_points, jacobian_actions = _jacobian_directions(REDUCED_DIMENSION)
    reference_groups = {
        "q006i_hessian_left": np.asarray(hessian_left, dtype=np.float64),
        "q006i_hessian_right": np.asarray(hessian_right, dtype=np.float64),
        "q006i_residual": _normalized_directions(
            RESIDUAL_SEED, 64, REDUCED_DIMENSION
        ),
        "q006i_shadow": _normalized_directions(
            SHADOW_SEED, 32, REDUCED_DIMENSION
        ),
        "q007b_derivative": _normalized_directions(
            CUBIC_DERIVATIVE_SEED,
            CUBIC_DERIVATIVE_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b_c4": _normalized_directions(
            CUBIC_C4_SEED,
            CUBIC_C4_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b_residual": _normalized_directions(
            CUBIC_RESIDUAL_SEED,
            CUBIC_RESIDUAL_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "q007b_shadow": _normalized_directions(
            CUBIC_SHADOW_SEED,
            CUBIC_SHADOW_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
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
        "q007b1_jacobian_points": jacobian_points,
        "q007b1_jacobian_actions": jacobian_actions,
    }
    registered_groups = {
        "map_fourth_derivative": _normalized_directions(
            MAP_DERIVATIVE_SEED,
            MAP_DERIVATIVE_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "assembled_forcing": _normalized_directions(
            FORCING_DERIVATIVE_SEED,
            FORCING_DERIVATIVE_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "residual": _normalized_directions(
            RESIDUAL_SEED_Q007C1,
            RESIDUAL_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "c4": _normalized_directions(
            C4_SEED_Q007C1,
            C4_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
        "shadow": _normalized_directions(
            SHADOW_SEED_Q007C1,
            SHADOW_DIRECTION_COUNT,
            REDUCED_DIMENSION,
        ),
    }
    registered_records = [
        {
            "campaign": name,
            "direction_count": len(directions),
            "direction_sha256": _array_hash(directions),
            "maximum_norm_error": float(
                np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0))
            ),
        }
        for name, directions in registered_groups.items()
    ]
    duplicate_records = []
    seen: list[tuple[str, int, Array]] = []
    for group_name, directions in {**reference_groups, **registered_groups}.items():
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
        "registered_campaigns": registered_records,
        "reference_group_hashes": {
            name: _array_hash(directions)
            for name, directions in reference_groups.items()
        },
        "maximum_norm_error": max(
            record["maximum_norm_error"] for record in registered_records
        ),
        "duplicate_count": len(duplicate_records),
        "duplicate_records": duplicate_records,
    }


def _fourth_difference(
    function: Callable[[float], Array],
    step: float,
) -> Array:
    return np.asarray(
        (
            function(2.0 * step)
            - 4.0 * function(step)
            + 6.0 * function(0.0)
            - 4.0 * function(-step)
            + function(-2.0 * step)
        )
        / step**4,
        dtype=np.float64,
    )


def _map_fourth_derivative_campaign(
    model: Full2DQuarticModel,
    directions: Array,
) -> dict[str, Any]:
    base = model.cubic.quadratic.chart.base
    tangent = model.cubic.quadratic.chart.tangent
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        physical_direction = tangent @ direction
        analytic = model.analytic_map_fourth_action(direction)
        step_records = []
        for step in FOURTH_DIFFERENCE_STEPS:
            states = {
                multiplier: base + multiplier * step * physical_direction
                for multiplier in (2, 1, 0, -1, -2)
            }
            mapped = {
                multiplier: model.cubic.quadratic.full_map(state)
                for multiplier, state in states.items()
            }
            finite_difference = (
                mapped[2]
                - 4.0 * mapped[1]
                + 6.0 * mapped[0]
                - 4.0 * mapped[-1]
                + mapped[-2]
            ) / step**4
            relative_error = _relative_norm(finite_difference - analytic, analytic)
            trial_minimum = min(
                *(float(np.min(value)) for value in states.values()),
                *(float(np.min(value)) for value in mapped.values()),
            )
            finite = bool(
                all(np.all(np.isfinite(value)) for value in states.values())
                and all(np.all(np.isfinite(value)) for value in mapped.values())
                and np.all(np.isfinite(finite_difference))
                and np.isfinite(relative_error)
            )
            minimum_population = min(minimum_population, trial_minimum)
            all_values_finite = all_values_finite and finite
            step_records.append(
                {
                    "step": step,
                    "finite_difference_norm": float(np.linalg.norm(finite_difference)),
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
        "seed": MAP_DERIVATIVE_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "steps": list(FOURTH_DIFFERENCE_STEPS),
        "formula": "(f(2h)-4f(h)+6f(0)-4f(-h)+f(-2h))/h^4",
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


def _forcing_derivative_campaign(
    model: Full2DQuarticModel,
    directions: Array,
) -> dict[str, Any]:
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        analytic = model.forcing_field(direction)
        step_records = []
        for step in FOURTH_DIFFERENCE_STEPS:
            defects: dict[int, Array] = {}
            trial_values = []
            for multiplier in (2, 1, 0, -1, -2):
                coordinates = multiplier * step * direction
                lifted = model.cubic.chart_evaluate(coordinates, cubic=True)
                mapped = model.cubic.quadratic.full_map(lifted)
                reduced = model.cubic.reduced_map(coordinates, cubic=True)
                predicted = model.cubic.chart_evaluate(reduced, cubic=True)
                defects[multiplier] = mapped - predicted
                trial_values.extend((lifted, mapped, predicted))
            finite_difference = (
                defects[2]
                - 4.0 * defects[1]
                + 6.0 * defects[0]
                - 4.0 * defects[-1]
                + defects[-2]
            ) / step**4
            relative_error = _relative_norm(finite_difference - analytic, analytic)
            trial_minimum = min(float(np.min(value)) for value in trial_values)
            finite = bool(
                all(np.all(np.isfinite(value)) for value in trial_values)
                and all(np.all(np.isfinite(value)) for value in defects.values())
                and np.all(np.isfinite(finite_difference))
                and np.isfinite(relative_error)
            )
            minimum_population = min(minimum_population, trial_minimum)
            all_values_finite = all_values_finite and finite
            step_records.append(
                {
                    "step": step,
                    "finite_difference_norm": float(np.linalg.norm(finite_difference)),
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
                "analytic_forcing_norm": float(np.linalg.norm(analytic)),
                "best_step": best["step"],
                "minimum_relative_error": best["relative_error"],
                "step_records": step_records,
            }
        )
    return {
        "seed": FORCING_DERIVATIVE_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "steps": list(FOURTH_DIFFERENCE_STEPS),
        "differenced_function": "Phi(W3(a))-W3(R3(a))",
        "direction_records": records,
        "summary": {
            "minimum_analytic_forcing_norm": min(
                record["analytic_forcing_norm"] for record in records
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


def _coefficient_conjugacy_audit(model: Full2DQuarticModel) -> dict[str, Any]:
    conjugate_indices = _conjugate_mode_indices(
        list(model.modes),
        model.lookup,
        model.size,
    )

    quartet_lookup = {
        tuple(int(value) for value in quartet): quartet_index
        for quartet_index, quartet in enumerate(model.quartet_indices)
    }
    conjugate_quartet_indices = []
    missing_records = []
    for quartet_index, quartet in enumerate(model.quartet_indices):
        conjugate_quartet = tuple(
            sorted(int(conjugate_indices[index]) for index in quartet)
        )
        if conjugate_quartet not in quartet_lookup:
            missing_records.append(
                {
                    "quartet_index": quartet_index,
                    "conjugate_input_indices": list(conjugate_quartet),
                }
            )
        else:
            conjugate_quartet_indices.append(quartet_lookup[conjugate_quartet])
    if missing_records:
        return {
            "missing_conjugate_count": len(missing_records),
            "missing_conjugate_records": missing_records,
            "chart_coefficient_relative_residual": float("inf"),
            "reduced_coefficient_relative_residual": float("inf"),
            "forcing_relative_residual": float("inf"),
            "maximum_relative_residual": float("inf"),
        }

    conjugate_quartets = np.asarray(conjugate_quartet_indices, dtype=np.int64)
    chart_error = (
        model.quartic_coefficients[conjugate_quartets]
        - np.conjugate(model.quartic_coefficients)
    )
    forcing_error = (
        model.forcing_coefficients[conjugate_quartets]
        - np.conjugate(model.forcing_coefficients)
    )
    reduced_error = (
        model.reduced_quartic_coefficients[conjugate_quartets][
            :, conjugate_indices
        ]
        - np.conjugate(model.reduced_quartic_coefficients)
    )
    chart_residual = _relative_norm(chart_error, model.quartic_coefficients)
    reduced_residual = _relative_norm(
        reduced_error,
        model.reduced_quartic_coefficients,
    )
    forcing_residual = _relative_norm(forcing_error, model.forcing_coefficients)
    return {
        "missing_conjugate_count": 0,
        "missing_conjugate_records": [],
        "chart_coefficient_relative_residual": chart_residual,
        "reduced_coefficient_relative_residual": reduced_residual,
        "forcing_relative_residual": forcing_residual,
        "maximum_relative_residual": max(
            chart_residual,
            reduced_residual,
            forcing_residual,
        ),
    }


def _upstream_reproduction(model: Full2DQuarticModel) -> dict[str, Any]:
    modes = list(model.modes)
    pair_records = _enumerate_records(
        2,
        modes,
        model.lookup,
        model.size,
        model.cubic.quadratic.omega,
        model.cubic.quadratic.eta,
    )
    triple_records = _enumerate_records(
        3,
        modes,
        model.lookup,
        model.size,
        model.cubic.quadratic.omega,
        model.cubic.quadratic.eta,
    )
    pair_summary = _record_summary(pair_records)
    triple_summary = _record_summary(triple_records)
    records = list(model.coefficient_records)
    quartet_sector_counts = dict(Counter(record["output_kind"] for record in records))
    quartet_conditions = [
        float(record["condition_number"])
        for record in records
        if record["condition_number"] is not None
    ]
    quartet_summary = {
        "record_count": len(records),
        "unique_tuple_count": len(
            {tuple(int(value) for value in row) for row in model.quartet_indices}
        ),
        "duplicate_tuple_count": len(records)
        - len({tuple(int(value) for value in row) for row in model.quartet_indices}),
        "sector_counts": quartet_sector_counts,
        "numerically_singular_block_count": sum(
            record["numerically_singular"] for record in records
        ),
        "minimum_operator_singular_value": min(
            record["smallest_singular_value"] for record in records
        ),
        "maximum_operator_condition_number": max(quartet_conditions),
        "permutation_multiplicity_sum": int(np.sum(model.multiplicities)),
        "permutation_multiplicity_values": sorted(
            int(value) for value in np.unique(model.multiplicities)
        ),
    }

    pair_errors = {
        "minimum_singular_value_relative_error": _relative_scalar_error(
            pair_summary["minimum_operator_singular_value"],
            REGISTERED_PAIR_MINIMUM_SINGULAR_VALUE,
        ),
        "maximum_condition_relative_error": _relative_scalar_error(
            pair_summary["maximum_operator_condition_number"],
            REGISTERED_PAIR_MAXIMUM_CONDITION_NUMBER,
        ),
    }
    triple_errors = {
        "minimum_singular_value_relative_error": _relative_scalar_error(
            triple_summary["minimum_operator_singular_value"],
            REGISTERED_TRIPLE_MINIMUM_SINGULAR_VALUE,
        ),
        "maximum_condition_relative_error": _relative_scalar_error(
            triple_summary["maximum_operator_condition_number"],
            REGISTERED_TRIPLE_MAXIMUM_CONDITION_NUMBER,
        ),
    }
    quartet_errors = {
        "minimum_singular_value_relative_error": _relative_scalar_error(
            quartet_summary["minimum_operator_singular_value"],
            REGISTERED_QUARTIC_MINIMUM_SINGULAR_VALUE,
        ),
        "maximum_condition_relative_error": _relative_scalar_error(
            quartet_summary["maximum_operator_condition_number"],
            REGISTERED_QUARTIC_MAXIMUM_CONDITION_NUMBER,
        ),
    }
    cubic_hashes = model.cubic.coefficient_hashes()
    return {
        "pair_summary": pair_summary,
        "triple_summary": triple_summary,
        "quartet_summary": quartet_summary,
        "spectral_relative_errors": {
            "order_two": pair_errors,
            "order_three": triple_errors,
            "order_four": quartet_errors,
        },
        "registered_cubic_coefficient_hashes": REGISTERED_COEFFICIENT_HASHES,
        "observed_cubic_coefficient_hashes": cubic_hashes,
        "cubic_hashes_match": cubic_hashes == REGISTERED_COEFFICIENT_HASHES,
    }


def _coefficient_campaign(model: Full2DQuarticModel) -> dict[str, Any]:
    records = list(model.coefficient_records)
    conjugacy = _coefficient_conjugacy_audit(model)
    arrays_finite = bool(
        np.all(np.isfinite(model.quartic_coefficients))
        and np.all(np.isfinite(model.reduced_quartic_coefficients))
        and np.all(np.isfinite(model.forcing_coefficients))
    )
    summary = {
        "quartet_count": len(records),
        "sector_counts": dict(Counter(record["output_kind"] for record in records)),
        "numerically_singular_block_count": sum(
            record["numerically_singular"] for record in records
        ),
        "maximum_condition_number": max(
            float(record["condition_number"])
            for record in records
            if record["condition_number"] is not None
        ),
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
            record["fixed_leaf_subspace_invariance_residual"] for record in records
        ),
        "forcing_frobenius_norm": float(np.linalg.norm(model.forcing_coefficients)),
        "chart_coefficient_frobenius_norm": float(
            np.linalg.norm(model.quartic_coefficients)
        ),
        "reduced_coefficient_frobenius_norm": float(
            np.linalg.norm(model.reduced_quartic_coefficients)
        ),
        "minimum_forcing_norm": min(record["forcing_norm"] for record in records),
        "maximum_forcing_norm": max(record["forcing_norm"] for record in records),
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
            "symmetric complex Fourier fibers with unordered quartets and "
            "permutation multiplicities; no full physical dense quartic tensor"
        ),
        "coefficient_hashes": model.coefficient_hashes(),
        "conjugacy_audit": conjugacy,
        "summary": summary,
        "quartet_records": records,
    }


def _c4_campaign(
    model: Full2DQuarticModel,
    directions: Array,
) -> dict[str, Any]:
    size = model.size
    tangent = model.cubic.quadratic.chart.tangent
    rotated_tangent = _quarter_turn_field(
        tangent.reshape(size, size, 9, model.reduced_dimension),
        size,
    ).reshape(size * size * 9, model.reduced_dimension)
    coordinate_rotation = model.cubic.quadratic.extractor @ rotated_tangent
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        coordinates = C4_AMPLITUDE * direction
        rotated_coordinates = coordinate_rotation @ coordinates

        chart_term = model.quartic_chart_term(coordinates).reshape(size, size, 9)
        rotated_chart_term = _quarter_turn_field(chart_term, size).ravel()
        transformed_chart_term = model.quartic_chart_term(rotated_coordinates)
        chart_error = _relative_norm(
            rotated_chart_term - transformed_chart_term,
            transformed_chart_term,
        )

        reduced_term = model.reduced_quartic_term(coordinates)
        rotated_reduced_term = coordinate_rotation @ reduced_term
        transformed_reduced_term = model.reduced_quartic_term(rotated_coordinates)
        reduced_error = _relative_norm(
            rotated_reduced_term - transformed_reduced_term,
            transformed_reduced_term,
        )

        forcing_field = model.forcing_field(coordinates).reshape(size, size, 9)
        rotated_forcing_field = _quarter_turn_field(forcing_field, size).ravel()
        transformed_forcing_field = model.forcing_field(rotated_coordinates)
        forcing_error = _relative_norm(
            rotated_forcing_field - transformed_forcing_field,
            transformed_forcing_field,
        )
        complex_chart_field = model.complex_quartic_field(coordinates)
        imaginary_leakage = _relative_norm(
            complex_chart_field.imag,
            complex_chart_field.real,
        )
        global_moments = conserved_moment_matrix() @ np.sum(
            chart_term,
            axis=(0, 1),
        )
        conservation_residual = _relative_norm(global_moments, chart_term)

        chart_value = model.chart_evaluate(coordinates, quartic=True)
        transformed_chart_value = model.chart_evaluate(
            rotated_coordinates,
            quartic=True,
        )
        mapped_chart = model.cubic.quadratic.full_map(chart_value)
        mapped_transformed = model.cubic.quadratic.full_map(transformed_chart_value)
        trial_minimum = min(
            float(np.min(chart_value)),
            float(np.min(transformed_chart_value)),
            float(np.min(mapped_chart)),
            float(np.min(mapped_transformed)),
        )
        finite = bool(
            all(
                np.all(np.isfinite(value))
                for value in (
                    chart_term,
                    rotated_chart_term,
                    transformed_chart_term,
                    reduced_term,
                    rotated_reduced_term,
                    transformed_reduced_term,
                    forcing_field,
                    rotated_forcing_field,
                    transformed_forcing_field,
                    complex_chart_field,
                    chart_value,
                    transformed_chart_value,
                    mapped_chart,
                    mapped_transformed,
                )
            )
            and all(
                np.isfinite(value)
                for value in (
                    chart_error,
                    reduced_error,
                    forcing_error,
                    imaginary_leakage,
                    conservation_residual,
                )
            )
        )
        minimum_population = min(minimum_population, trial_minimum)
        all_values_finite = all_values_finite and finite
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "chart_term_relative_error": chart_error,
                "reduced_term_relative_error": reduced_error,
                "forcing_field_relative_error": forcing_error,
                "chart_field_imaginary_leakage_relative_norm": imaginary_leakage,
                "chart_term_global_conservation_relative_residual": (
                    conservation_residual
                ),
                "minimum_population": trial_minimum,
                "all_values_finite": finite,
            }
        )
    return {
        "seed": C4_SEED_Q007C1,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitude": C4_AMPLITUDE,
        "coordinate_rotation_orthogonality_error": float(
            np.linalg.norm(
                coordinate_rotation.T @ coordinate_rotation
                - np.eye(model.reduced_dimension)
            )
        ),
        "coordinate_rotation_order_four_error": float(
            np.linalg.norm(
                np.linalg.matrix_power(coordinate_rotation, 4)
                - np.eye(model.reduced_dimension)
            )
        ),
        "direction_records": records,
        "summary": {
            "maximum_chart_term_relative_error": max(
                record["chart_term_relative_error"] for record in records
            ),
            "maximum_reduced_term_relative_error": max(
                record["reduced_term_relative_error"] for record in records
            ),
            "maximum_forcing_field_relative_error": max(
                record["forcing_field_relative_error"] for record in records
            ),
            "maximum_chart_field_imaginary_leakage_relative_norm": max(
                record["chart_field_imaginary_leakage_relative_norm"]
                for record in records
            ),
            "maximum_chart_term_global_conservation_relative_residual": max(
                record["chart_term_global_conservation_relative_residual"]
                for record in records
            ),
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _residual_campaign(
    model: Full2DQuarticModel,
    directions: Array,
) -> dict[str, Any]:
    amplitudes = np.asarray(RESIDUAL_AMPLITUDES, dtype=np.float64)
    records = []
    minimum_population = np.inf
    all_values_finite = True
    for direction_index, direction in enumerate(directions):
        quadratic_residuals = []
        cubic_residuals = []
        quartic_residuals = []
        direction_minimum = np.inf
        direction_finite = True
        for amplitude in amplitudes:
            coordinates = amplitude * direction

            quadratic_lifted = model.cubic.chart_evaluate(
                coordinates,
                cubic=False,
            )
            quadratic_mapped = model.cubic.quadratic.full_map(quadratic_lifted)
            quadratic_predicted = model.cubic.chart_evaluate(
                model.cubic.reduced_map(coordinates, cubic=False),
                cubic=False,
            )

            cubic_lifted = model.chart_evaluate(coordinates, quartic=False)
            cubic_mapped = model.cubic.quadratic.full_map(cubic_lifted)
            cubic_predicted = model.chart_evaluate(
                model.reduced_map(coordinates, quartic=False),
                quartic=False,
            )

            quartic_lifted = model.chart_evaluate(coordinates, quartic=True)
            quartic_mapped = model.cubic.quadratic.full_map(quartic_lifted)
            quartic_predicted = model.chart_evaluate(
                model.reduced_map(coordinates, quartic=True),
                quartic=True,
            )

            quadratic_residuals.append(
                float(np.linalg.norm(quadratic_mapped - quadratic_predicted))
            )
            cubic_residuals.append(
                float(np.linalg.norm(cubic_mapped - cubic_predicted))
            )
            quartic_residuals.append(
                float(np.linalg.norm(quartic_mapped - quartic_predicted))
            )
            values = (
                quadratic_lifted,
                quadratic_mapped,
                quadratic_predicted,
                cubic_lifted,
                cubic_mapped,
                cubic_predicted,
                quartic_lifted,
                quartic_mapped,
                quartic_predicted,
            )
            direction_minimum = min(
                direction_minimum,
                *(float(np.min(value)) for value in values),
            )
            direction_finite = direction_finite and all(
                np.all(np.isfinite(value)) for value in values
            )

        cubic_slope = log_log_slope(amplitudes[1:], cubic_residuals[1:])
        quartic_slope = log_log_slope(amplitudes[1:], quartic_residuals[1:])
        quartic_to_cubic = float(quartic_residuals[-1] / cubic_residuals[-1])
        quartic_to_quadratic = float(
            quartic_residuals[-1] / quadratic_residuals[-1]
        )
        direction_finite = bool(
            direction_finite
            and np.isfinite(cubic_slope)
            and np.isfinite(quartic_slope)
            and np.isfinite(quartic_to_cubic)
            and np.isfinite(quartic_to_quadratic)
        )
        minimum_population = min(minimum_population, direction_minimum)
        all_values_finite = all_values_finite and direction_finite
        records.append(
            {
                "direction_index": direction_index,
                "direction": direction.tolist(),
                "quadratic_residuals": quadratic_residuals,
                "cubic_residuals": cubic_residuals,
                "quartic_residuals": quartic_residuals,
                "cubic_slope_last_four": cubic_slope,
                "quartic_slope_last_four": quartic_slope,
                "maximum_amplitude_quartic_to_cubic_ratio": quartic_to_cubic,
                "maximum_amplitude_quartic_to_quadratic_ratio": (
                    quartic_to_quadratic
                ),
                "minimum_population": float(direction_minimum),
                "all_values_finite": direction_finite,
            }
        )
    return {
        "seed": RESIDUAL_SEED_Q007C1,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitudes": amplitudes.tolist(),
        "slope_fit_amplitudes": amplitudes[1:].tolist(),
        "direction_records": records,
        "summary": {
            "minimum_cubic_slope": min(
                record["cubic_slope_last_four"] for record in records
            ),
            "maximum_cubic_slope": max(
                record["cubic_slope_last_four"] for record in records
            ),
            "minimum_quartic_slope": min(
                record["quartic_slope_last_four"] for record in records
            ),
            "maximum_quartic_slope": max(
                record["quartic_slope_last_four"] for record in records
            ),
            "maximum_quartic_to_cubic_residual_ratio": max(
                record["maximum_amplitude_quartic_to_cubic_ratio"]
                for record in records
            ),
            "quartic_to_cubic_failure_count": sum(
                record["maximum_amplitude_quartic_to_cubic_ratio"]
                > MAXIMUM_QUARTIC_TO_CUBIC_RESIDUAL_RATIO
                for record in records
            ),
            "maximum_quartic_to_quadratic_residual_ratio": max(
                record["maximum_amplitude_quartic_to_quadratic_ratio"]
                for record in records
            ),
            "quartic_to_quadratic_failure_count": sum(
                record["maximum_amplitude_quartic_to_quadratic_ratio"]
                > MAXIMUM_QUARTIC_TO_QUADRATIC_RESIDUAL_RATIO
                for record in records
            ),
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _shadow_rollout(
    model: Full2DQuarticModel,
    direction: Array,
    direction_index: int,
    *,
    quartic: bool,
    amplitude: float = SHADOW_AMPLITUDE,
    steps: int = SHADOW_STEPS,
) -> dict[str, Any]:
    coordinates = float(amplitude) * direction
    state = model.chart_evaluate(coordinates, quartic=quartic)
    base = model.cubic.quadratic.chart.base
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
    if quartic:
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
            raise ValueError("Q007c1 component scales must have positive ULPs")

    for step in range(int(steps) + 1):
        predicted = model.chart_evaluate(coordinates, quartic=quartic)
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
        if quartic and step > 0:
            tensor = state.reshape(model.size, model.size, 9)
            current_fsum, current_neumaier = compensated_conserved_quantities(
                tensor
            )
            drift = current_fsum - initial_fsum
            absolute_drift = np.abs(drift)
            budgets = CONSERVATION_SENSITIVE_STAGE_COUNT * step * component_ulps
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
            if step == steps:
                final_component_budgets = budgets
        if step == steps:
            final_absolute_error = absolute_error
            final_relative_error = relative_error
        else:
            state = model.cubic.quadratic.full_map(state)
            coordinates = model.reduced_map(coordinates, quartic=quartic)

    result = {
        "chart": "quartic" if quartic else "cubic",
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
    if quartic:
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
    model: Full2DQuarticModel,
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
        cubic = _shadow_rollout(
            model,
            direction,
            direction_index,
            quartic=False,
        )
        quartic = _shadow_rollout(
            model,
            direction,
            direction_index,
            quartic=True,
        )
        ratios = {
            "maximum_absolute_error_ratio": float(
                quartic["maximum_absolute_error"]
                / max(cubic["maximum_absolute_error"], np.finfo(float).eps)
            ),
            "final_absolute_error_ratio": float(
                quartic["final_absolute_error"]
                / max(cubic["final_absolute_error"], np.finfo(float).eps)
            ),
            "maximum_perturbation_relative_error_ratio": float(
                quartic["maximum_perturbation_relative_error"]
                / max(
                    cubic["maximum_perturbation_relative_error"],
                    np.finfo(float).eps,
                )
            ),
        }
        budget = quartic["conservation_budget"]
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
                "cubic": cubic,
                "quartic": quartic,
                "improvement_ratios": ratios,
            }
        )
    ratio_keys = (
        "maximum_absolute_error_ratio",
        "final_absolute_error_ratio",
        "maximum_perturbation_relative_error_ratio",
    )
    return {
        "seed": SHADOW_SEED_Q007C1,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitude": SHADOW_AMPLITUDE,
        "steps": SHADOW_STEPS,
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
            "quartic_budget_component_check_count": total_component_checks,
            "quartic_budget_violation_count": total_budget_violations,
            "maximum_quartic_budget_utilization": maximum_budget_utilization,
            "maximum_quartic_absolute_conservation_drift": maximum_absolute_drift,
            "maximum_independent_sum_difference": maximum_independent_sum_difference,
            "maximum_final_component_budget": maximum_final_component_budget,
            "minimum_population": min(
                min(
                    record["cubic"]["minimum_population"],
                    record["quartic"]["minimum_population"],
                )
                for record in records
            ),
            "all_values_finite": all(
                record["cubic"]["all_values_finite"]
                and record["quartic"]["all_values_finite"]
                for record in records
            ),
        },
    }


def run_quartic_continuation_audit() -> dict[str, Any]:
    """Run the fully sealed Q007c1 construction and held-out campaigns."""

    model = build_full2d_quartic_model()
    direction_registration = _direction_registration()
    map_derivative = _map_fourth_derivative_campaign(
        model,
        _normalized_directions(
            MAP_DERIVATIVE_SEED,
            MAP_DERIVATIVE_DIRECTION_COUNT,
            model.reduced_dimension,
        ),
    )
    forcing_derivative = _forcing_derivative_campaign(
        model,
        _normalized_directions(
            FORCING_DERIVATIVE_SEED,
            FORCING_DERIVATIVE_DIRECTION_COUNT,
            model.reduced_dimension,
        ),
    )
    upstream = _upstream_reproduction(model)
    coefficients = _coefficient_campaign(model)
    c4 = _c4_campaign(
        model,
        _normalized_directions(
            C4_SEED_Q007C1,
            C4_DIRECTION_COUNT,
            model.reduced_dimension,
        ),
    )
    residual = _residual_campaign(
        model,
        _normalized_directions(
            RESIDUAL_SEED_Q007C1,
            RESIDUAL_DIRECTION_COUNT,
            model.reduced_dimension,
        ),
    )
    shadowing = _shadowing_campaign(
        model,
        _normalized_directions(
            SHADOW_SEED_Q007C1,
            SHADOW_DIRECTION_COUNT,
            model.reduced_dimension,
        ),
    )

    pair_summary = upstream["pair_summary"]
    triple_summary = upstream["triple_summary"]
    quartet_reproduction = upstream["quartet_summary"]
    spectral_errors = upstream["spectral_relative_errors"]
    coefficient_summary = coefficients["summary"]
    conjugacy = coefficients["conjugacy_audit"]
    c4_summary = c4["summary"]
    residual_summary = residual["summary"]
    shadow_summary = shadowing["summary"]

    serializable_probe = {
        "direction_registration": direction_registration,
        "map_fourth_derivative": map_derivative,
        "assembled_forcing_derivative": forcing_derivative,
        "upstream_reproduction": upstream,
        "coefficient_construction": coefficients,
        "c4_equivariance": c4,
        "residual_order": residual,
        "shadowing": shadowing,
    }
    finite_probe = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)
    minimum_population = min(
        map_derivative["summary"]["minimum_population"],
        forcing_derivative["summary"]["minimum_population"],
        c4_summary["minimum_population"],
        residual_summary["minimum_population"],
        shadow_summary["minimum_population"],
    )

    operator_reproduction_passed = bool(
        pair_summary["record_count"] == REGISTERED_PAIR_COUNT
        and pair_summary["sector_counts"] == REGISTERED_PAIR_SECTOR_COUNTS
        and pair_summary["numerically_singular_block_count"] == 0
        and all(
            value <= REPRODUCTION_RELATIVE_TOLERANCE
            for value in spectral_errors["order_two"].values()
        )
        and triple_summary["record_count"] == REGISTERED_TRIPLE_COUNT
        and triple_summary["sector_counts"] == REGISTERED_TRIPLE_SECTOR_COUNTS
        and triple_summary["numerically_singular_block_count"] == 0
        and triple_summary["near_resonant_block_count"]
        == REGISTERED_TRIPLE_NEAR_RESONANT_COUNT
        and all(
            value <= REPRODUCTION_RELATIVE_TOLERANCE
            for value in spectral_errors["order_three"].values()
        )
        and quartet_reproduction["record_count"] == REGISTERED_QUARTIC_COUNT
        and quartet_reproduction["unique_tuple_count"] == REGISTERED_QUARTIC_COUNT
        and quartet_reproduction["duplicate_tuple_count"] == 0
        and quartet_reproduction["sector_counts"]
        == REGISTERED_QUARTIC_SECTOR_COUNTS
        and quartet_reproduction["numerically_singular_block_count"] == 0
        and quartet_reproduction["permutation_multiplicity_sum"]
        == REGISTERED_QUARTIC_MULTIPLICITY_SUM
        and set(quartet_reproduction["permutation_multiplicity_values"])
        == REGISTERED_QUARTIC_MULTIPLICITIES
        and all(
            value <= REPRODUCTION_RELATIVE_TOLERANCE
            for value in spectral_errors["order_four"].values()
        )
        and upstream["cubic_hashes_match"]
    )
    coefficient_equations_passed = bool(
        coefficient_summary["maximum_solve_relative_residual"]
        <= COEFFICIENT_RELATIVE_TOLERANCE
        and coefficient_summary["maximum_homological_relative_residual"]
        <= COEFFICIENT_RELATIVE_TOLERANCE
    )
    coefficient_structure_passed = bool(
        conjugacy["missing_conjugate_count"] == 0
        and conjugacy["maximum_relative_residual"]
        <= COEFFICIENT_RELATIVE_TOLERANCE
        and coefficient_summary["maximum_graph_gauge_relative_residual"]
        <= COEFFICIENT_RELATIVE_TOLERANCE
        and coefficient_summary[
            "maximum_zero_wave_forcing_conservation_relative_residual"
        ]
        <= COEFFICIENT_RELATIVE_TOLERANCE
        and coefficient_summary[
            "maximum_zero_wave_coefficient_conservation_relative_residual"
        ]
        <= COEFFICIENT_RELATIVE_TOLERANCE
        and coefficient_summary["maximum_fixed_leaf_subspace_invariance_residual"]
        <= COEFFICIENT_RELATIVE_TOLERANCE
    )
    c4_passed = all(
        c4_summary[key] <= C4_RELATIVE_TOLERANCE
        for key in (
            "maximum_chart_term_relative_error",
            "maximum_reduced_term_relative_error",
            "maximum_forcing_field_relative_error",
            "maximum_chart_field_imaginary_leakage_relative_norm",
            "maximum_chart_term_global_conservation_relative_residual",
        )
    )
    validity_gates = {
        "registered_direction_integrity": {
            "value": {
                "maximum_norm_error": direction_registration["maximum_norm_error"],
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
        "q007b_q007c_upstream_reproduction": {
            "value": {
                "pair_count": pair_summary["record_count"],
                "pair_sector_counts": pair_summary["sector_counts"],
                "triple_count": triple_summary["record_count"],
                "triple_sector_counts": triple_summary["sector_counts"],
                "triple_near_resonant_count": triple_summary[
                    "near_resonant_block_count"
                ],
                "quartet_count": quartet_reproduction["record_count"],
                "quartet_sector_counts": quartet_reproduction["sector_counts"],
                "quartet_singular_count": quartet_reproduction[
                    "numerically_singular_block_count"
                ],
                "spectral_relative_errors": spectral_errors,
                "cubic_hashes_match": upstream["cubic_hashes_match"],
            },
            "threshold": {
                "pair_count": REGISTERED_PAIR_COUNT,
                "triple_count": REGISTERED_TRIPLE_COUNT,
                "quartet_count": REGISTERED_QUARTIC_COUNT,
                "maximum_spectral_relative_error": (
                    REPRODUCTION_RELATIVE_TOLERANCE
                ),
                "cubic_hashes_match": True,
            },
            "passed": operator_reproduction_passed,
        },
        "independent_map_fourth_derivative": {
            "value": {
                "minimum_analytic_derivative_norm": map_derivative["summary"][
                    "minimum_analytic_derivative_norm"
                ],
                "maximum_best_relative_error": map_derivative["summary"][
                    "maximum_best_relative_error"
                ],
            },
            "threshold": {
                "minimum_analytic_derivative_norm_strictly_greater_than": (
                    MINIMUM_ANALYTIC_DERIVATIVE_NORM
                ),
                "maximum_best_relative_error": (
                    MAXIMUM_MAP_DERIVATIVE_RELATIVE_ERROR
                ),
            },
            "passed": (
                map_derivative["summary"]["minimum_analytic_derivative_norm"]
                > MINIMUM_ANALYTIC_DERIVATIVE_NORM
                and map_derivative["summary"]["maximum_best_relative_error"]
                <= MAXIMUM_MAP_DERIVATIVE_RELATIVE_ERROR
            ),
        },
        "independent_assembled_forcing_derivative": {
            "value": {
                "minimum_analytic_forcing_norm": forcing_derivative["summary"][
                    "minimum_analytic_forcing_norm"
                ],
                "maximum_best_relative_error": forcing_derivative["summary"][
                    "maximum_best_relative_error"
                ],
            },
            "threshold": {
                "minimum_analytic_forcing_norm_strictly_greater_than": (
                    MINIMUM_ANALYTIC_FORCING_NORM
                ),
                "maximum_best_relative_error": (
                    MAXIMUM_FORCING_DERIVATIVE_RELATIVE_ERROR
                ),
            },
            "passed": (
                forcing_derivative["summary"]["minimum_analytic_forcing_norm"]
                > MINIMUM_ANALYTIC_FORCING_NORM
                and forcing_derivative["summary"]["maximum_best_relative_error"]
                <= MAXIMUM_FORCING_DERIVATIVE_RELATIVE_ERROR
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
            "passed": coefficient_equations_passed,
        },
        "coefficient_gauge_conjugacy_and_fixed_leaf": {
            "value": {
                "maximum_conjugacy_relative_residual": conjugacy[
                    "maximum_relative_residual"
                ],
                "maximum_graph_gauge_relative_residual": coefficient_summary[
                    "maximum_graph_gauge_relative_residual"
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
            },
            "threshold": COEFFICIENT_RELATIVE_TOLERANCE,
            "passed": coefficient_structure_passed,
        },
        "quartic_c4_realification_and_conservation": {
            "value": {
                key: c4_summary[key]
                for key in (
                    "maximum_chart_term_relative_error",
                    "maximum_reduced_term_relative_error",
                    "maximum_forcing_field_relative_error",
                    "maximum_chart_field_imaginary_leakage_relative_norm",
                    "maximum_chart_term_global_conservation_relative_residual",
                )
            },
            "threshold": C4_RELATIVE_TOLERANCE,
            "passed": c4_passed,
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

    residual_orders_passed = bool(
        residual_summary["minimum_cubic_slope"] >= CUBIC_SLOPE_RANGE[0]
        and residual_summary["maximum_cubic_slope"] <= CUBIC_SLOPE_RANGE[1]
        and residual_summary["minimum_quartic_slope"] >= QUARTIC_SLOPE_RANGE[0]
        and residual_summary["maximum_quartic_slope"] <= QUARTIC_SLOPE_RANGE[1]
    )
    residual_ratios_passed = bool(
        residual_summary["maximum_quartic_to_cubic_residual_ratio"]
        <= MAXIMUM_QUARTIC_TO_CUBIC_RESIDUAL_RATIO
        and residual_summary["maximum_quartic_to_quadratic_residual_ratio"]
        <= MAXIMUM_QUARTIC_TO_QUADRATIC_RESIDUAL_RATIO
    )
    maximum_shadow_ratios = shadow_summary["maximum_directional_improvement_ratios"]
    shadow_ratios_passed = all(
        value <= MAXIMUM_SHADOW_RATIO for value in maximum_shadow_ratios.values()
    )
    expected_component_checks = (
        SHADOW_DIRECTION_COUNT * SHADOW_STEPS * len(COMPONENT_NAMES)
    )
    budget_passed = bool(
        shadow_summary["quartic_budget_component_check_count"]
        == expected_component_checks
        and shadow_summary["quartic_budget_violation_count"] == 0
        and shadow_summary["maximum_quartic_budget_utilization"]
        <= MAXIMUM_BUDGET_UTILIZATION
        and shadow_summary["maximum_final_component_budget"]
        <= MAXIMUM_FINAL_COMPONENT_BUDGET
    )
    hypothesis_gates = {
        "held_out_residual_orders": {
            "value": {
                "cubic_slope_range": [
                    residual_summary["minimum_cubic_slope"],
                    residual_summary["maximum_cubic_slope"],
                ],
                "quartic_slope_range": [
                    residual_summary["minimum_quartic_slope"],
                    residual_summary["maximum_quartic_slope"],
                ],
            },
            "threshold": {
                "cubic_slope_range": list(CUBIC_SLOPE_RANGE),
                "quartic_slope_range": list(QUARTIC_SLOPE_RANGE),
            },
            "passed": residual_orders_passed,
        },
        "held_out_radius_residual_ratios": {
            "value": {
                "maximum_quartic_to_cubic_ratio": residual_summary[
                    "maximum_quartic_to_cubic_residual_ratio"
                ],
                "maximum_quartic_to_quadratic_ratio": residual_summary[
                    "maximum_quartic_to_quadratic_residual_ratio"
                ],
            },
            "threshold": {
                "maximum_quartic_to_cubic_ratio": (
                    MAXIMUM_QUARTIC_TO_CUBIC_RESIDUAL_RATIO
                ),
                "maximum_quartic_to_quadratic_ratio": (
                    MAXIMUM_QUARTIC_TO_QUADRATIC_RESIDUAL_RATIO
                ),
            },
            "passed": residual_ratios_passed,
        },
        "held_out_directional_shadowing_ratios": {
            "value": maximum_shadow_ratios,
            "threshold": {
                key: MAXIMUM_SHADOW_RATIO for key in maximum_shadow_ratios
            },
            "passed": shadow_ratios_passed,
        },
        "quartic_shadowing_forward_error_budget": {
            "value": {
                "component_check_count": shadow_summary[
                    "quartic_budget_component_check_count"
                ],
                "violation_count": shadow_summary[
                    "quartic_budget_violation_count"
                ],
                "maximum_budget_utilization": shadow_summary[
                    "maximum_quartic_budget_utilization"
                ],
                "maximum_final_component_budget": shadow_summary[
                    "maximum_final_component_budget"
                ],
            },
            "threshold": {
                "component_check_count": expected_component_checks,
                "violation_count": 0,
                "maximum_budget_utilization": MAXIMUM_BUDGET_UTILIZATION,
                "maximum_final_component_budget": MAXIMUM_FINAL_COMPONENT_BUDGET,
            },
            "passed": budget_passed,
        },
    }

    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q007c1 quartic-continuation validity failure"
        decision = (
            "A registered direction, upstream reproduction, derivative, forcing, "
            "coefficient, symmetry, fixed-leaf, positivity, finiteness, or "
            "serialization validity gate failed."
        )
        next_change = (
            "Repair the first Q007c1 validity failure without tuning the sealed "
            "performance gates."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "quartic chart restores registered sampled radius-0.01 improvement"
        )
        decision = (
            "The validated quartic chart raises residual order to five and passes "
            "all registered radius-0.01 residual, shadowing, and forward-error gates."
        )
        next_change = (
            "Freeze Q007c1 and preregister the sparse-fiber versus TT storage and "
            "evaluation comparison before compression."
        )
    else:
        outcome = "rejected"
        classification = "quartic continuation does not restore registered radius"
        decision = (
            "The quartic construction is valid, but at least one preregistered "
            "residual-order, radius, shadowing, or forward-error gate fails."
        )
        next_change = (
            "Freeze the first Q007c1 performance witness and diagnose the finite-"
            "radius truncation without changing the registered thresholds."
        )

    return {
        "question": (
            "Do all quartic forcing and coefficients pass independent checks, "
            "raise the defect order from four to five, and restore the sampled "
            "radius-0.01 residual and shadowing improvement?"
        ),
        "hypothesis": (
            "The registered quartic chart has fifth-order defects, quartic/cubic "
            "residual ratio at most 0.8, quartic/quadratic ratio at most 0.10, "
            "shadowing ratios at most 0.8, and no forward-error-budget violation."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.cubic.quadratic.omega,
            "eta": model.cubic.quadratic.eta,
            "real_reduced_dimension": model.reduced_dimension,
            "complex_mode_count": len(model.modes),
            "unordered_quartet_count": REGISTERED_QUARTIC_COUNT,
            "chart_convention": "W4(a)=W3(a)+U[a,a,a,a]/24",
            "reduced_map_convention": "R4(a)=R3(a)+L[a,a,a,a]/24",
            "full_map": "unmodified standard filtered D2Q9 map",
            "physical_dense_quartic_tensor_materialized": False,
        },
        "direction_registration": direction_registration,
        "independent_map_fourth_derivative": map_derivative,
        "independent_assembled_forcing_derivative": forcing_derivative,
        "upstream_reproduction": upstream,
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
        "preserved_prior_outcomes": {
            "q006i_scientific_outcome": "rejected",
            "q007b_scientific_outcome": "rejected",
            "q007b1_scientific_outcome": "accepted",
            "revised": False,
        },
        "claim_boundary": (
            "The outcome is limited to the registered finite grid, 32 residual "
            "directions, 32 shadow directions, sampled amplitudes, and 100-step "
            "horizon. It is not an all-ball, global-injectivity, TT-compression, "
            "grid-uniform, existence, uniqueness, or normal-attraction claim, and "
            "it does not revise Q006i, Q007b, or Q007b1."
        ),
    }
