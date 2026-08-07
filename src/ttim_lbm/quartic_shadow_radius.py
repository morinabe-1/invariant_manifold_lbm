"""Sealed Q007c2 quartic shadow amplitude-horizon localization audit."""

from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from .cubic_continuation import (
    C4_DIRECTION_COUNT as CUBIC_C4_DIRECTION_COUNT,
)
from .cubic_continuation import C4_SEED as CUBIC_C4_SEED
from .cubic_continuation import (
    DERIVATIVE_DIRECTION_COUNT as CUBIC_DERIVATIVE_DIRECTION_COUNT,
)
from .cubic_continuation import DERIVATIVE_SEED as CUBIC_DERIVATIVE_SEED
from .cubic_continuation import (
    RESIDUAL_DIRECTION_COUNT as CUBIC_RESIDUAL_DIRECTION_COUNT,
)
from .cubic_continuation import RESIDUAL_ORDER_SEED as CUBIC_RESIDUAL_SEED
from .cubic_continuation import (
    SHADOWING_DIRECTION_COUNT as CUBIC_SHADOW_DIRECTION_COUNT,
)
from .cubic_continuation import SHADOWING_SEED as CUBIC_SHADOW_SEED
from .cubic_continuation import (
    _all_numeric_values_finite,
    _array_hash,
    _normalized_directions,
    _relative_scalar_error,
    _strict_json_serializable,
)
from .cubic_radius import (
    RADIUS_DIRECTION_COUNT,
    RADIUS_SEED,
    SHADOW_RADIUS_DIRECTION_COUNT,
    SHADOW_RADIUS_SEED,
    _jacobian_directions,
)
from .forward_error_budget import COMPONENT_NAMES
from .full2d_chart import HESSIAN_SEED, REDUCED_DIMENSION, RESIDUAL_SEED, SHADOW_SEED
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model
from .quartic_continuation import (
    C4_DIRECTION_COUNT as QUARTIC_C4_DIRECTION_COUNT,
)
from .quartic_continuation import C4_SEED_Q007C1 as QUARTIC_C4_SEED
from .quartic_continuation import (
    FORCING_DERIVATIVE_DIRECTION_COUNT,
    FORCING_DERIVATIVE_SEED,
    MAP_DERIVATIVE_DIRECTION_COUNT,
    MAP_DERIVATIVE_SEED,
    _shadow_rollout,
)
from .quartic_continuation import (
    RESIDUAL_DIRECTION_COUNT as QUARTIC_RESIDUAL_DIRECTION_COUNT,
)
from .quartic_continuation import (
    RESIDUAL_SEED_Q007C1 as QUARTIC_RESIDUAL_SEED,
)
from .quartic_continuation import (
    SHADOW_DIRECTION_COUNT as QUARTIC_SHADOW_DIRECTION_COUNT,
)
from .quartic_continuation import (
    SHADOW_SEED_Q007C1 as QUARTIC_SHADOW_SEED,
)

Array = npt.NDArray[np.float64]

REGISTERED_QUARTIC_COEFFICIENT_HASHES = {
    "quartet_indices_sha256": (
        "968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16"
    ),
    "output_waves_sha256": (
        "9f9720e1114cc489ef7bbca81562e7d4cf211999e8d4a4958c06c02ee0df1fe8"
    ),
    "chart_coefficients_sha256": (
        "9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b"
    ),
    "reduced_coefficients_sha256": (
        "061cd66caf83850a45eeec05ed0f62fafb748a3076d7a6eb591bc69be2e008f7"
    ),
    "forcing_coefficients_sha256": (
        "6ab2337ea60b87dbe404e1aeb6b9c090fa8f950d43815966e0933879901b8eef"
    ),
}

CONTROL_DIRECTION_INDEX = 14
CONTROL_AMPLITUDE = 0.01
CONTROL_STEPS = 100
CONTROL_RATIOS = {
    "maximum_absolute_error_ratio": 0.7464493651463932,
    "final_absolute_error_ratio": 1.3715310087581642,
    "maximum_perturbation_relative_error_ratio": 0.8914189366016195,
}
CONTROL_RELATIVE_TOLERANCE = 1.0e-10

SHADOW_DOMAIN_SEED = 20260826
SHADOW_DOMAIN_DIRECTION_COUNT = 64
AMPLITUDES = (0.004, 0.007, 0.01)
PREFIX_HORIZONS = (10, 25, 50, 100)
MAXIMUM_STEPS = 100
MAXIMUM_SHADOW_RATIO = 0.8
MAXIMUM_BUDGET_UTILIZATION = 1.0
MAXIMUM_FINAL_COMPONENT_BUDGET = 1.2e-11
DIRECTION_NORM_TOLERANCE = 5.0e-15


def _reference_direction_groups() -> dict[str, Array]:
    hessian_rng = np.random.default_rng(HESSIAN_SEED)
    hessian_left = hessian_rng.normal(size=(32, REDUCED_DIMENSION))
    hessian_right = hessian_rng.normal(size=(32, REDUCED_DIMENSION))
    hessian_left /= np.linalg.norm(hessian_left, axis=1)[:, None]
    hessian_right /= np.linalg.norm(hessian_right, axis=1)[:, None]
    jacobian_points, jacobian_actions = _jacobian_directions(REDUCED_DIMENSION)
    specifications = (
        ("q006i_residual", RESIDUAL_SEED, 64),
        ("q006i_shadow", SHADOW_SEED, 32),
        (
            "q007b_derivative",
            CUBIC_DERIVATIVE_SEED,
            CUBIC_DERIVATIVE_DIRECTION_COUNT,
        ),
        ("q007b_c4", CUBIC_C4_SEED, CUBIC_C4_DIRECTION_COUNT),
        ("q007b_residual", CUBIC_RESIDUAL_SEED, CUBIC_RESIDUAL_DIRECTION_COUNT),
        ("q007b_shadow", CUBIC_SHADOW_SEED, CUBIC_SHADOW_DIRECTION_COUNT),
        ("q007b1_radius", RADIUS_SEED, RADIUS_DIRECTION_COUNT),
        ("q007b1_shadow", SHADOW_RADIUS_SEED, SHADOW_RADIUS_DIRECTION_COUNT),
        (
            "q007c1_map_derivative",
            MAP_DERIVATIVE_SEED,
            MAP_DERIVATIVE_DIRECTION_COUNT,
        ),
        (
            "q007c1_forcing_derivative",
            FORCING_DERIVATIVE_SEED,
            FORCING_DERIVATIVE_DIRECTION_COUNT,
        ),
        (
            "q007c1_residual",
            QUARTIC_RESIDUAL_SEED,
            QUARTIC_RESIDUAL_DIRECTION_COUNT,
        ),
        ("q007c1_c4", QUARTIC_C4_SEED, QUARTIC_C4_DIRECTION_COUNT),
        (
            "q007c1_shadow",
            QUARTIC_SHADOW_SEED,
            QUARTIC_SHADOW_DIRECTION_COUNT,
        ),
    )
    return {
        "q006i_hessian_left": np.asarray(hessian_left, dtype=np.float64),
        "q006i_hessian_right": np.asarray(hessian_right, dtype=np.float64),
        "q007b1_jacobian_points": jacobian_points,
        "q007b1_jacobian_actions": jacobian_actions,
        **{
            name: _normalized_directions(seed, count, REDUCED_DIMENSION)
            for name, seed, count in specifications
        },
    }


def _direction_registration(directions: Array) -> dict[str, Any]:
    references = _reference_direction_groups()
    duplicate_records = []
    for direction_index, direction in enumerate(directions):
        for group_name, group in references.items():
            for prior_index, prior_direction in enumerate(group):
                if np.array_equal(direction, prior_direction):
                    duplicate_records.append(
                        {
                            "direction_index": direction_index,
                            "prior_group": group_name,
                            "prior_direction_index": prior_index,
                        }
                    )
        for prior_index in range(direction_index):
            if np.array_equal(direction, directions[prior_index]):
                duplicate_records.append(
                    {
                        "direction_index": direction_index,
                        "prior_group": "q007c2_shadow_domain",
                        "prior_direction_index": prior_index,
                    }
                )
    return {
        "seed": SHADOW_DOMAIN_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "maximum_norm_error": float(
            np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0))
        ),
        "reference_group_hashes": {
            name: _array_hash(group) for name, group in references.items()
        },
        "duplicate_count": len(duplicate_records),
        "duplicate_records": duplicate_records,
    }


def _rollout_ratios(cubic: dict[str, Any], quartic: dict[str, Any]) -> dict[str, float]:
    return {
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


def _control_reproduction(model: Full2DQuarticModel) -> dict[str, Any]:
    directions = _normalized_directions(
        QUARTIC_SHADOW_SEED,
        QUARTIC_SHADOW_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    direction = directions[CONTROL_DIRECTION_INDEX]
    cubic = _shadow_rollout(
        model,
        direction,
        CONTROL_DIRECTION_INDEX,
        quartic=False,
        amplitude=CONTROL_AMPLITUDE,
        steps=CONTROL_STEPS,
    )
    quartic = _shadow_rollout(
        model,
        direction,
        CONTROL_DIRECTION_INDEX,
        quartic=True,
        amplitude=CONTROL_AMPLITUDE,
        steps=CONTROL_STEPS,
    )
    ratios = _rollout_ratios(cubic, quartic)
    relative_errors = {
        key: _relative_scalar_error(ratios[key], registered)
        for key, registered in CONTROL_RATIOS.items()
    }
    observed_hashes = model.coefficient_hashes()
    return {
        "coefficient_hashes": {
            "registered": REGISTERED_QUARTIC_COEFFICIENT_HASHES,
            "observed": observed_hashes,
            "match": observed_hashes == REGISTERED_QUARTIC_COEFFICIENT_HASHES,
        },
        "direction_seed": QUARTIC_SHADOW_SEED,
        "direction_index": CONTROL_DIRECTION_INDEX,
        "direction": direction.tolist(),
        "direction_sha256": _array_hash(direction),
        "amplitude": CONTROL_AMPLITUDE,
        "steps": CONTROL_STEPS,
        "registered_ratios": CONTROL_RATIOS,
        "observed_ratios": ratios,
        "relative_errors": relative_errors,
        "maximum_relative_error": max(relative_errors.values()),
        "cubic": cubic,
        "quartic": quartic,
    }


def _prefix_metrics(
    cubic: dict[str, Any],
    quartic: dict[str, Any],
    horizon: int,
) -> dict[str, Any]:
    stop = int(horizon) + 1
    cubic_absolute = np.asarray(cubic["absolute_error_by_step"][:stop])
    quartic_absolute = np.asarray(quartic["absolute_error_by_step"][:stop])
    cubic_relative = np.asarray(
        cubic["perturbation_relative_error_by_step"][:stop]
    )
    quartic_relative = np.asarray(
        quartic["perturbation_relative_error_by_step"][:stop]
    )
    ratios = {
        "maximum_absolute_error_ratio": float(
            np.max(quartic_absolute)
            / max(float(np.max(cubic_absolute)), np.finfo(float).eps)
        ),
        "final_absolute_error_ratio": float(
            quartic_absolute[-1]
            / max(float(cubic_absolute[-1]), np.finfo(float).eps)
        ),
        "maximum_perturbation_relative_error_ratio": float(
            np.max(quartic_relative)
            / max(float(np.max(cubic_relative)), np.finfo(float).eps)
        ),
    }
    return {
        "horizon": int(horizon),
        "ratios": ratios,
        "cubic": {
            "maximum_absolute_error": float(np.max(cubic_absolute)),
            "final_absolute_error": float(cubic_absolute[-1]),
            "maximum_perturbation_relative_error": float(
                np.max(cubic_relative)
            ),
        },
        "quartic": {
            "maximum_absolute_error": float(np.max(quartic_absolute)),
            "final_absolute_error": float(quartic_absolute[-1]),
            "maximum_perturbation_relative_error": float(
                np.max(quartic_relative)
            ),
        },
    }


def _first_exceedance(values: Array, threshold: float) -> int | None:
    indices = np.flatnonzero(values > threshold)
    return None if len(indices) == 0 else int(indices[0])


def _shadow_domain_campaign(
    model: Full2DQuarticModel,
    directions: Array,
) -> dict[str, Any]:
    amplitude_records = []
    total_component_checks = 0
    total_budget_violations = 0
    maximum_budget_utilization = 0.0
    maximum_final_component_budget = 0.0
    minimum_population = np.inf
    all_values_finite = True
    ratio_keys = tuple(CONTROL_RATIOS)
    for amplitude in AMPLITUDES:
        direction_records = []
        for direction_index, direction in enumerate(directions):
            cubic = _shadow_rollout(
                model,
                direction,
                direction_index,
                quartic=False,
                amplitude=amplitude,
                steps=MAXIMUM_STEPS,
            )
            quartic = _shadow_rollout(
                model,
                direction,
                direction_index,
                quartic=True,
                amplitude=amplitude,
                steps=MAXIMUM_STEPS,
            )
            prefix_records = [
                _prefix_metrics(cubic, quartic, horizon)
                for horizon in PREFIX_HORIZONS
            ]
            cubic_absolute = np.asarray(cubic["absolute_error_by_step"])
            quartic_absolute = np.asarray(quartic["absolute_error_by_step"])
            cubic_relative = np.asarray(
                cubic["perturbation_relative_error_by_step"]
            )
            quartic_relative = np.asarray(
                quartic["perturbation_relative_error_by_step"]
            )
            instantaneous_absolute_ratios = quartic_absolute / np.maximum(
                cubic_absolute,
                np.finfo(float).eps,
            )
            instantaneous_relative_ratios = quartic_relative / np.maximum(
                cubic_relative,
                np.finfo(float).eps,
            )
            budget = quartic["conservation_budget"]
            total_component_checks += budget["component_check_count"]
            total_budget_violations += budget["violation_count"]
            maximum_budget_utilization = max(
                maximum_budget_utilization,
                budget["maximum_budget_utilization"],
            )
            maximum_final_component_budget = max(
                maximum_final_component_budget,
                budget["maximum_final_component_budget"],
            )
            minimum_population = min(
                minimum_population,
                cubic["minimum_population"],
                quartic["minimum_population"],
            )
            finite = bool(
                cubic["all_values_finite"]
                and quartic["all_values_finite"]
                and np.all(np.isfinite(instantaneous_absolute_ratios))
                and np.all(np.isfinite(instantaneous_relative_ratios))
                and all(
                    all(np.isfinite(value) for value in record["ratios"].values())
                    for record in prefix_records
                )
            )
            all_values_finite = all_values_finite and finite
            direction_records.append(
                {
                    "direction_index": direction_index,
                    "direction": direction.tolist(),
                    "cubic": cubic,
                    "quartic": quartic,
                    "prefix_records": prefix_records,
                    "instantaneous_absolute_error_ratios": (
                        instantaneous_absolute_ratios.tolist()
                    ),
                    "instantaneous_perturbation_relative_error_ratios": (
                        instantaneous_relative_ratios.tolist()
                    ),
                    "first_absolute_ratio_exceedance_step": _first_exceedance(
                        instantaneous_absolute_ratios,
                        MAXIMUM_SHADOW_RATIO,
                    ),
                    "first_relative_ratio_exceedance_step": _first_exceedance(
                        instantaneous_relative_ratios,
                        MAXIMUM_SHADOW_RATIO,
                    ),
                    "all_values_finite": finite,
                }
            )

        prefix_summaries = []
        for prefix_index, horizon in enumerate(PREFIX_HORIZONS):
            prefix_summaries.append(
                {
                    "horizon": horizon,
                    "maximum_directional_ratios": {
                        key: max(
                            record["prefix_records"][prefix_index]["ratios"][key]
                            for record in direction_records
                        )
                        for key in ratio_keys
                    },
                    "ratio_failure_counts": {
                        key: sum(
                            record["prefix_records"][prefix_index]["ratios"][key]
                            > MAXIMUM_SHADOW_RATIO
                            for record in direction_records
                        )
                        for key in ratio_keys
                    },
                }
            )
        amplitude_records.append(
            {
                "amplitude": amplitude,
                "direction_count": len(direction_records),
                "direction_records": direction_records,
                "prefix_summaries": prefix_summaries,
            }
        )
    return {
        "seed": SHADOW_DOMAIN_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "amplitudes": list(AMPLITUDES),
        "prefix_horizons": list(PREFIX_HORIZONS),
        "maximum_steps": MAXIMUM_STEPS,
        "trajectory_count": len(directions) * len(AMPLITUDES) * 2,
        "chart_step_count": (
            len(directions) * len(AMPLITUDES) * 2 * MAXIMUM_STEPS
        ),
        "amplitude_records": amplitude_records,
        "summary": {
            "quartic_budget_component_check_count": total_component_checks,
            "quartic_budget_violation_count": total_budget_violations,
            "maximum_quartic_budget_utilization": maximum_budget_utilization,
            "maximum_final_component_budget": maximum_final_component_budget,
            "minimum_population": float(minimum_population),
            "all_values_finite": all_values_finite,
        },
    }


def _cell_summary(
    campaign: dict[str, Any],
    amplitude: float,
    horizon: int,
) -> dict[str, Any]:
    amplitude_record = next(
        record
        for record in campaign["amplitude_records"]
        if record["amplitude"] == amplitude
    )
    return next(
        record
        for record in amplitude_record["prefix_summaries"]
        if record["horizon"] == horizon
    )


def run_quartic_shadow_radius_audit() -> dict[str, Any]:
    """Run the preregistered Q007c2 amplitude-horizon shadow audit."""

    model = build_full2d_quartic_model()
    directions = _normalized_directions(
        SHADOW_DOMAIN_SEED,
        SHADOW_DOMAIN_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    direction_registration = _direction_registration(directions)
    control = _control_reproduction(model)
    campaign = _shadow_domain_campaign(model, directions)
    short_large = _cell_summary(campaign, 0.01, 10)
    long_small = _cell_summary(campaign, 0.004, 100)
    campaign_summary = campaign["summary"]

    serializable_probe = {
        "direction_registration": direction_registration,
        "control_reproduction": control,
        "shadow_domain_campaign": campaign,
    }
    finite_probe = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)
    expected_component_checks = (
        SHADOW_DOMAIN_DIRECTION_COUNT
        * len(AMPLITUDES)
        * MAXIMUM_STEPS
        * len(COMPONENT_NAMES)
    )
    expected_chart_steps = (
        SHADOW_DOMAIN_DIRECTION_COUNT * len(AMPLITUDES) * 2 * MAXIMUM_STEPS
    )
    control_passed = bool(
        control["coefficient_hashes"]["match"]
        and control["maximum_relative_error"] <= CONTROL_RELATIVE_TOLERANCE
    )
    structure_passed = bool(
        campaign["direction_count"] == SHADOW_DOMAIN_DIRECTION_COUNT
        and campaign["amplitudes"] == list(AMPLITUDES)
        and campaign["prefix_horizons"] == list(PREFIX_HORIZONS)
        and campaign["trajectory_count"]
        == SHADOW_DOMAIN_DIRECTION_COUNT * len(AMPLITUDES) * 2
        and campaign["chart_step_count"] == expected_chart_steps
        and all(
            record["direction_count"] == SHADOW_DOMAIN_DIRECTION_COUNT
            for record in campaign["amplitude_records"]
        )
    )
    validity_gates = {
        "q007c1_coefficient_and_witness_reproduction": {
            "value": {
                "coefficient_hashes_match": control["coefficient_hashes"]["match"],
                "maximum_ratio_relative_error": control["maximum_relative_error"],
            },
            "threshold": {
                "coefficient_hashes_match": True,
                "maximum_ratio_relative_error": CONTROL_RELATIVE_TOLERANCE,
            },
            "passed": control_passed,
        },
        "independent_direction_integrity": {
            "value": {
                "direction_count": direction_registration["direction_count"],
                "maximum_norm_error": direction_registration["maximum_norm_error"],
                "duplicate_count": direction_registration["duplicate_count"],
            },
            "threshold": {
                "direction_count": SHADOW_DOMAIN_DIRECTION_COUNT,
                "maximum_norm_error": DIRECTION_NORM_TOLERANCE,
                "duplicate_count": 0,
            },
            "passed": (
                direction_registration["direction_count"]
                == SHADOW_DOMAIN_DIRECTION_COUNT
                and direction_registration["maximum_norm_error"]
                <= DIRECTION_NORM_TOLERANCE
                and direction_registration["duplicate_count"] == 0
            ),
        },
        "campaign_structure": {
            "value": {
                "trajectory_count": campaign["trajectory_count"],
                "chart_step_count": campaign["chart_step_count"],
                "amplitudes": campaign["amplitudes"],
                "prefix_horizons": campaign["prefix_horizons"],
            },
            "threshold": {
                "trajectory_count": (
                    SHADOW_DOMAIN_DIRECTION_COUNT * len(AMPLITUDES) * 2
                ),
                "chart_step_count": expected_chart_steps,
                "amplitudes": list(AMPLITUDES),
                "prefix_horizons": list(PREFIX_HORIZONS),
            },
            "passed": structure_passed,
        },
        "finite_positive_and_strict_json": {
            "value": {
                "minimum_population": campaign_summary["minimum_population"],
                "all_campaign_values_finite": finite_probe,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "minimum_population_strictly_greater_than": 0.0,
                "all_campaign_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": (
                campaign_summary["minimum_population"] > 0.0
                and finite_probe
                and strict_json
            ),
        },
    }

    short_large_passed = all(
        value <= MAXIMUM_SHADOW_RATIO
        for value in short_large["maximum_directional_ratios"].values()
    )
    long_small_passed = all(
        value <= MAXIMUM_SHADOW_RATIO
        for value in long_small["maximum_directional_ratios"].values()
    )
    budget_passed = bool(
        campaign_summary["quartic_budget_component_check_count"]
        == expected_component_checks
        and campaign_summary["quartic_budget_violation_count"] == 0
        and campaign_summary["maximum_quartic_budget_utilization"]
        <= MAXIMUM_BUDGET_UTILIZATION
        and campaign_summary["maximum_final_component_budget"]
        <= MAXIMUM_FINAL_COMPONENT_BUDGET
    )
    hypothesis_gates = {
        "radius_0p01_horizon_10_shadow_ratios": {
            "value": short_large["maximum_directional_ratios"],
            "failure_counts": short_large["ratio_failure_counts"],
            "threshold": {
                key: MAXIMUM_SHADOW_RATIO
                for key in short_large["maximum_directional_ratios"]
            },
            "passed": short_large_passed,
        },
        "radius_0p004_horizon_100_shadow_ratios": {
            "value": long_small["maximum_directional_ratios"],
            "failure_counts": long_small["ratio_failure_counts"],
            "threshold": {
                key: MAXIMUM_SHADOW_RATIO
                for key in long_small["maximum_directional_ratios"]
            },
            "passed": long_small_passed,
        },
        "quartic_forward_error_budget": {
            "value": {
                "component_check_count": campaign_summary[
                    "quartic_budget_component_check_count"
                ],
                "violation_count": campaign_summary[
                    "quartic_budget_violation_count"
                ],
                "maximum_budget_utilization": campaign_summary[
                    "maximum_quartic_budget_utilization"
                ],
                "maximum_final_component_budget": campaign_summary[
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
        classification = "Q007c2 shadow-domain validity failure"
        decision = (
            "A coefficient, Q007c1 witness, direction, campaign-structure, "
            "positivity, finiteness, or serialization validity gate failed."
        )
        next_change = (
            "Repair the first validity failure without changing the sealed "
            "amplitude, horizon, ratio, or budget gates."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "quartic shadowing domain localized on independent directions"
        )
        decision = (
            "Both preregistered operating points pass all three shadow ratios, "
            "and every quartic trajectory stays within the forward-error budget."
        )
        next_change = (
            "Freeze the accepted finite shadow domain and preregister Q008 sparse-"
            "fiber versus TT storage and evaluation benchmarks."
        )
    else:
        outcome = "rejected"
        classification = "registered quartic shadowing domain not reproduced"
        decision = (
            "The campaign is valid, but at least one preregistered operating "
            "point or forward-error-budget gate fails."
        )
        next_change = (
            "Freeze the first independent performance witnesses before changing "
            "the chart degree, radius, horizon, or reduced coordinate set."
        )
    return {
        "question": (
            "Does the fixed Q007c1 quartic chart reproduce short-horizon radius-"
            "0.01 and long-horizon radius-0.004 shadow improvement on independent "
            "directions?"
        ),
        "hypothesis": (
            "All three quartic/cubic shadow ratios are at most 0.8 for radius "
            "0.01 at 10 steps and radius 0.004 at 100 steps, with no forward-"
            "error-budget violation."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.cubic.quadratic.omega,
            "eta": model.cubic.quadratic.eta,
            "real_reduced_dimension": model.reduced_dimension,
            "direction_count": SHADOW_DOMAIN_DIRECTION_COUNT,
            "amplitudes": list(AMPLITUDES),
            "prefix_horizons": list(PREFIX_HORIZONS),
            "maximum_steps": MAXIMUM_STEPS,
            "full_map": "unmodified standard filtered D2Q9 map",
        },
        "direction_registration": direction_registration,
        "q007c1_control_reproduction": control,
        "shadow_domain_campaign": campaign,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "preserved_prior_outcomes": {
            "q007b_scientific_outcome": "rejected",
            "q007b1_scientific_outcome": "accepted",
            "q007c1_scientific_outcome": "rejected",
            "q007c1_radius_0p01_horizon_100_revised": False,
        },
        "claim_boundary": (
            "The outcome is limited to 64 registered directions and the two "
            "preregistered amplitude-horizon operating points. It is not an all-"
            "ball, other-horizon, global-injectivity, grid-uniform, invariant-"
            "manifold existence, or TT-compression claim, and it does not revise "
            "the Q007c1 radius-0.01 100-step rejection."
        ),
    }
