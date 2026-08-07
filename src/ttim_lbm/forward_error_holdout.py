"""Sealed Q006q independent holdout for the Q006o forward-error policy."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import conservative_checkerboard_filter
from .conservation_drift import (
    INDEPENDENT_SUM_TOLERANCE,
    compensated_conserved_quantities,
)
from .d2q9 import (
    collide_bgk,
    conserved_moment_matrix,
    stream_periodic,
)
from .forward_error_budget import (
    COMPONENT_NAMES,
    CONSERVATION_SENSITIVE_STAGE_COUNT,
)
from .full2d_chart import (
    SHADOW_SEED,
    Full2DQuadraticModel,
    build_full2d_quadratic_model,
)

Array = npt.NDArray[np.float64]

REGISTERED_DIRECTION_COUNT_PER_CHART = 32
REGISTERED_SCENARIOS = (
    {
        "name": "long_horizon",
        "direction_seed": 20260811,
        "amplitude": 0.005,
        "steps": 200,
    },
    {
        "name": "large_amplitude",
        "direction_seed": 20260812,
        "amplitude": 0.02,
        "steps": 50,
    },
)
REGISTERED_TRAJECTORY_COUNT = 128
REGISTERED_TRAJECTORY_STEP_COUNT = 16000
REGISTERED_COMPONENT_CHECK_COUNT = 48000
DIRECTION_NORM_TOLERANCE = 5.0e-15
MAXIMUM_FINAL_BUDGET = 2.4e-11


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


def _direction_audit(dimension: int) -> tuple[dict[str, Array], dict[str, Any]]:
    reference = _normalized_directions(
        SHADOW_SEED,
        REGISTERED_DIRECTION_COUNT_PER_CHART,
        dimension,
    )
    directions = {
        scenario["name"]: _normalized_directions(
            int(scenario["direction_seed"]),
            REGISTERED_DIRECTION_COUNT_PER_CHART,
            dimension,
        )
        for scenario in REGISTERED_SCENARIOS
    }
    seen = [
        ("q006o_reference", index, direction)
        for index, direction in enumerate(reference)
    ]
    duplicate_records = []
    for scenario in REGISTERED_SCENARIOS:
        name = str(scenario["name"])
        for direction_index, direction in enumerate(directions[name]):
            for prior_name, prior_index, prior_direction in seen:
                if np.array_equal(direction, prior_direction):
                    duplicate_records.append(
                        {
                            "scenario": name,
                            "direction_index": direction_index,
                            "duplicate_group": prior_name,
                            "duplicate_direction_index": prior_index,
                        }
                    )
            seen.append((name, direction_index, direction))

    scenario_records = []
    for scenario in REGISTERED_SCENARIOS:
        name = str(scenario["name"])
        values = directions[name]
        norm_errors = np.abs(np.linalg.norm(values, axis=1) - 1.0)
        scenario_records.append(
            {
                "scenario": name,
                "direction_seed": scenario["direction_seed"],
                "direction_count": len(values),
                "direction_hash": _array_hash(values),
                "maximum_norm_error": float(np.max(norm_errors)),
            }
        )
    return directions, {
        "q006o_reference_seed": SHADOW_SEED,
        "q006o_reference_direction_hash": _array_hash(reference),
        "scenario_records": scenario_records,
        "duplicate_count": len(duplicate_records),
        "duplicate_records": duplicate_records,
        "all_direction_hashes_distinct": len(
            {
                _array_hash(reference),
                *(_array_hash(values) for values in directions.values()),
            }
        )
        == 1 + len(directions),
        "maximum_norm_error": max(
            record["maximum_norm_error"] for record in scenario_records
        ),
    }


def _component_scales(state: Array, moment_matrix: Array) -> Array:
    contributions = moment_matrix[:, None, None, :] * state[None, :, :, :]
    return np.asarray(
        np.sum(np.abs(contributions), axis=(1, 2, 3)),
        dtype=np.float64,
    )


def _empty_component_witnesses() -> dict[str, dict[str, Any]]:
    return {
        component: {
            "value": 0.0,
            "step": 0,
            "signed_drift": 0.0,
            "absolute_drift": 0.0,
            "budget": 0.0,
        }
        for component in COMPONENT_NAMES
    }


def _trajectory_record(
    model: Full2DQuadraticModel,
    scenario: dict[str, Any],
    chart_name: str,
    direction: Array,
    direction_index: int,
    moment_matrix: Array,
) -> dict[str, Any]:
    chart = model.chart if chart_name == "quadratic" else model.linear_chart
    amplitude = float(scenario["amplitude"])
    steps = int(scenario["steps"])
    state = chart.evaluate(amplitude * direction).reshape(
        model.size,
        model.size,
        9,
    )
    initial_fsum, initial_neumaier = compensated_conserved_quantities(state)
    scales = _component_scales(state, moment_matrix)
    component_ulps = np.spacing(scales)
    if np.any(component_ulps <= 0.0):
        raise ValueError("holdout component scales must have positive ULPs")

    maximum_utilization = _empty_component_witnesses()
    maximum_absolute_drift = _empty_component_witnesses()
    maximum_independent_sum_difference = float(
        np.max(np.abs(initial_fsum - initial_neumaier))
    )
    maximum_streaming_fsum_increment = 0.0
    maximum_streaming_fsum_component_increment = 0.0
    maximum_stage_map_identity_error = 0.0
    minimum_population = float(np.min(state))
    all_values_finite = bool(
        np.all(np.isfinite(state))
        and np.all(np.isfinite(initial_fsum))
        and np.all(np.isfinite(initial_neumaier))
        and np.all(np.isfinite(scales))
        and np.all(np.isfinite(component_ulps))
    )
    violation_count = 0
    first_violation: dict[str, Any] | None = None
    budget_records = []

    for step in range(1, steps + 1):
        collided = collide_bgk(state, model.omega)
        collision_fsum, collision_neumaier = compensated_conserved_quantities(
            collided
        )
        streamed = stream_periodic(collided)
        streaming_fsum, streaming_neumaier = compensated_conserved_quantities(
            streamed
        )
        filtered = conservative_checkerboard_filter(streamed, model.eta)
        filter_fsum, filter_neumaier = compensated_conserved_quantities(filtered)
        mapped = model.full_map(state.ravel()).reshape(state.shape)

        stage_map_error = float(np.max(np.abs(filtered - mapped)))
        maximum_stage_map_identity_error = max(
            maximum_stage_map_identity_error,
            stage_map_error,
        )
        streaming_increment = streaming_fsum - collision_fsum
        maximum_streaming_fsum_increment = max(
            maximum_streaming_fsum_increment,
            float(np.linalg.norm(streaming_increment)),
        )
        maximum_streaming_fsum_component_increment = max(
            maximum_streaming_fsum_component_increment,
            float(np.max(np.abs(streaming_increment))),
        )
        maximum_independent_sum_difference = max(
            maximum_independent_sum_difference,
            float(np.max(np.abs(collision_fsum - collision_neumaier))),
            float(np.max(np.abs(streaming_fsum - streaming_neumaier))),
            float(np.max(np.abs(filter_fsum - filter_neumaier))),
        )

        drift = filter_fsum - initial_fsum
        budgets = (
            CONSERVATION_SENSITIVE_STAGE_COUNT * step * component_ulps
        )
        absolute_drift = np.abs(drift)
        utilization = absolute_drift / budgets
        passed = absolute_drift <= budgets
        violation_count += int(np.count_nonzero(~passed))

        for component_index, component in enumerate(COMPONENT_NAMES):
            utilization_value = float(utilization[component_index])
            witness = {
                "value": utilization_value,
                "step": step,
                "signed_drift": float(drift[component_index]),
                "absolute_drift": float(absolute_drift[component_index]),
                "budget": float(budgets[component_index]),
            }
            if utilization_value > maximum_utilization[component]["value"]:
                maximum_utilization[component] = witness
            if (
                float(absolute_drift[component_index])
                > maximum_absolute_drift[component]["absolute_drift"]
            ):
                maximum_absolute_drift[component] = witness
            if not bool(passed[component_index]) and first_violation is None:
                first_violation = {
                    "step": step,
                    "component": component,
                    "signed_drift": float(drift[component_index]),
                    "absolute_drift": float(absolute_drift[component_index]),
                    "budget": float(budgets[component_index]),
                    "utilization": utilization_value,
                }

        budget_records.append(
            {
                "step": step,
                "signed_drift": drift.tolist(),
                "absolute_drift": absolute_drift.tolist(),
                "budget": budgets.tolist(),
                "utilization": utilization.tolist(),
                "passed": passed.tolist(),
            }
        )
        state = mapped
        minimum_population = min(minimum_population, float(np.min(state)))
        all_values_finite = bool(
            all_values_finite
            and np.all(np.isfinite(collided))
            and np.all(np.isfinite(streamed))
            and np.all(np.isfinite(filtered))
            and np.all(np.isfinite(mapped))
            and np.all(np.isfinite(collision_fsum))
            and np.all(np.isfinite(collision_neumaier))
            and np.all(np.isfinite(streaming_fsum))
            and np.all(np.isfinite(streaming_neumaier))
            and np.all(np.isfinite(filter_fsum))
            and np.all(np.isfinite(filter_neumaier))
            and np.all(np.isfinite(drift))
            and np.all(np.isfinite(budgets))
            and np.all(np.isfinite(utilization))
        )

    final_budget = (
        CONSERVATION_SENSITIVE_STAGE_COUNT * steps * component_ulps
    )
    return {
        "scenario": scenario["name"],
        "direction_seed": scenario["direction_seed"],
        "amplitude": amplitude,
        "steps": steps,
        "chart": chart_name,
        "direction_index": direction_index,
        "direction": direction.tolist(),
        "initial_measurement": {
            "fsum": initial_fsum.tolist(),
            "neumaier": initial_neumaier.tolist(),
        },
        "component_scale": scales.tolist(),
        "component_ulp": component_ulps.tolist(),
        "final_budget": final_budget.tolist(),
        "budget_records": budget_records,
        "summary": {
            "component_check_count": 3 * len(budget_records),
            "budget_violation_count": violation_count,
            "first_violation": first_violation,
            "maximum_utilization": maximum_utilization,
            "maximum_absolute_drift": maximum_absolute_drift,
            "maximum_independent_sum_component_difference": (
                maximum_independent_sum_difference
            ),
            "maximum_streaming_fsum_increment": (
                maximum_streaming_fsum_increment
            ),
            "maximum_streaming_fsum_component_increment": (
                maximum_streaming_fsum_component_increment
            ),
            "maximum_stage_map_identity_error": maximum_stage_map_identity_error,
            "minimum_population": minimum_population,
            "all_values_finite": all_values_finite,
        },
    }


def _maximum_witness(
    records: list[dict[str, Any]],
    field: str,
    value_key: str,
) -> dict[str, Any]:
    witnesses = []
    for record in records:
        for component, witness in record["summary"][field].items():
            witnesses.append(
                {
                    "scenario": record["scenario"],
                    "chart": record["chart"],
                    "direction_index": record["direction_index"],
                    "component": component,
                    **witness,
                }
            )
    return max(witnesses, key=lambda witness: witness[value_key])


def _first_violation(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    for record in records:
        violation = record["summary"]["first_violation"]
        if violation is not None:
            return {
                "scenario": record["scenario"],
                "chart": record["chart"],
                "direction_index": record["direction_index"],
                **violation,
            }
    return None


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "trajectory_count": len(records),
        "trajectory_step_count": sum(record["steps"] for record in records),
        "component_budget_check_count": sum(
            record["summary"]["component_check_count"] for record in records
        ),
        "budget_violation_count": sum(
            record["summary"]["budget_violation_count"] for record in records
        ),
        "first_budget_violation": _first_violation(records),
        "maximum_budget_utilization": _maximum_witness(
            records,
            "maximum_utilization",
            "value",
        ),
        "maximum_absolute_drift": _maximum_witness(
            records,
            "maximum_absolute_drift",
            "absolute_drift",
        ),
        "maximum_final_component_budget": max(
            max(record["final_budget"]) for record in records
        ),
        "maximum_independent_sum_component_difference": max(
            record["summary"]["maximum_independent_sum_component_difference"]
            for record in records
        ),
        "maximum_streaming_fsum_increment": max(
            record["summary"]["maximum_streaming_fsum_increment"]
            for record in records
        ),
        "maximum_streaming_fsum_component_increment": max(
            record["summary"]["maximum_streaming_fsum_component_increment"]
            for record in records
        ),
        "maximum_stage_map_identity_error": max(
            record["summary"]["maximum_stage_map_identity_error"]
            for record in records
        ),
        "minimum_population": min(
            record["summary"]["minimum_population"] for record in records
        ),
        "all_values_finite": all(
            record["summary"]["all_values_finite"] for record in records
        ),
    }


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_forward_error_holdout_audit() -> dict[str, Any]:
    """Run the preregistered Q006q independent forward-error holdout."""

    model = build_full2d_quadratic_model()
    directions, direction_audit = _direction_audit(model.reduced_dimension)
    moment_matrix = conserved_moment_matrix()
    records = [
        _trajectory_record(
            model,
            scenario,
            chart_name,
            direction,
            direction_index,
            moment_matrix,
        )
        for scenario in REGISTERED_SCENARIOS
        for chart_name in ("linear", "quadratic")
        for direction_index, direction in enumerate(
            directions[str(scenario["name"])]
        )
    ]
    scenario_records = []
    for scenario in REGISTERED_SCENARIOS:
        name = str(scenario["name"])
        selected = [record for record in records if record["scenario"] == name]
        scenario_records.append(
            {
                "scenario": name,
                "direction_seed": scenario["direction_seed"],
                "amplitude": scenario["amplitude"],
                "steps": scenario["steps"],
                "summary": _summary(selected),
            }
        )
    summary = _summary(records)

    serializable_probe = {
        "direction_audit": direction_audit,
        "trajectory_records": records,
        "scenario_records": scenario_records,
        "summary": summary,
    }
    strict_json = _strict_json_serializable(serializable_probe)
    setup_value = {
        "grid": [model.size, model.size],
        "omega": model.omega,
        "eta": model.eta,
        "reduced_dimension": model.reduced_dimension,
        "chart_types": ["linear", "quadratic"],
        "scenarios": [dict(scenario) for scenario in REGISTERED_SCENARIOS],
        "q006o_reference_seed": SHADOW_SEED,
    }
    setup_threshold = {
        "grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "reduced_dimension": 24,
        "chart_types": ["linear", "quadratic"],
        "scenarios": [dict(scenario) for scenario in REGISTERED_SCENARIOS],
        "q006o_reference_seed": 20260810,
    }
    validity_gates = {
        "registered_setup": {
            "value": setup_value,
            "threshold": setup_threshold,
            "passed": setup_value == setup_threshold,
        },
        "registered_enumeration": {
            "value": {
                "trajectory_count": summary["trajectory_count"],
                "trajectory_step_count": summary["trajectory_step_count"],
                "component_budget_check_count": summary[
                    "component_budget_check_count"
                ],
            },
            "threshold": {
                "trajectory_count": REGISTERED_TRAJECTORY_COUNT,
                "trajectory_step_count": REGISTERED_TRAJECTORY_STEP_COUNT,
                "component_budget_check_count": REGISTERED_COMPONENT_CHECK_COUNT,
            },
            "passed": (
                summary["trajectory_count"] == REGISTERED_TRAJECTORY_COUNT
                and summary["trajectory_step_count"]
                == REGISTERED_TRAJECTORY_STEP_COUNT
                and summary["component_budget_check_count"]
                == REGISTERED_COMPONENT_CHECK_COUNT
            ),
        },
        "independent_direction_sets": {
            "value": {
                "duplicate_count": direction_audit["duplicate_count"],
                "all_direction_hashes_distinct": direction_audit[
                    "all_direction_hashes_distinct"
                ],
                "maximum_norm_error": direction_audit["maximum_norm_error"],
            },
            "threshold": {
                "duplicate_count": 0,
                "all_direction_hashes_distinct": True,
                "maximum_norm_error": DIRECTION_NORM_TOLERANCE,
            },
            "passed": (
                direction_audit["duplicate_count"] == 0
                and direction_audit["all_direction_hashes_distinct"]
                and direction_audit["maximum_norm_error"]
                <= DIRECTION_NORM_TOLERANCE
            ),
        },
        "exact_stage_map_identity": {
            "value": summary["maximum_stage_map_identity_error"],
            "threshold": 0.0,
            "passed": summary["maximum_stage_map_identity_error"] == 0.0,
        },
        "exact_streaming_permutation": {
            "value": {
                "maximum_norm": summary["maximum_streaming_fsum_increment"],
                "maximum_component": summary[
                    "maximum_streaming_fsum_component_increment"
                ],
            },
            "threshold": {"maximum_norm": 0.0, "maximum_component": 0.0},
            "passed": (
                summary["maximum_streaming_fsum_increment"] == 0.0
                and summary["maximum_streaming_fsum_component_increment"] == 0.0
            ),
        },
        "independent_compensated_sums": {
            "value": summary["maximum_independent_sum_component_difference"],
            "threshold": INDEPENDENT_SUM_TOLERANCE,
            "passed": summary["maximum_independent_sum_component_difference"]
            <= INDEPENDENT_SUM_TOLERANCE,
        },
        "positive_holdout_states": {
            "value": summary["minimum_population"],
            "threshold": 0.0,
            "passed": summary["minimum_population"] > 0.0,
        },
        "finite_and_strict_json": {
            "value": {
                "all_values_finite": summary["all_values_finite"],
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "all_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": summary["all_values_finite"] and strict_json,
        },
    }

    scenario_policy_gates = {}
    for scenario in scenario_records:
        scenario_summary = scenario["summary"]
        scenario_policy_gates[str(scenario["scenario"])] = {
            "value": {
                "budget_violation_count": scenario_summary[
                    "budget_violation_count"
                ],
                "maximum_utilization": scenario_summary[
                    "maximum_budget_utilization"
                ]["value"],
            },
            "threshold": {
                "budget_violation_count": 0,
                "maximum_utilization": 1.0,
            },
            "passed": (
                scenario_summary["budget_violation_count"] == 0
                and scenario_summary["maximum_budget_utilization"]["value"]
                <= 1.0
            ),
        }
    holdout_policy_gates = {
        "scenario_budget_coverage": {
            "value": {
                name: gate["passed"] for name, gate in scenario_policy_gates.items()
            },
            "threshold": {
                scenario["name"]: True for scenario in REGISTERED_SCENARIOS
            },
            "passed": all(
                gate["passed"] for gate in scenario_policy_gates.values()
            ),
        },
        "aggregate_budget_coverage": {
            "value": {
                "budget_violation_count": summary["budget_violation_count"],
                "maximum_utilization": summary["maximum_budget_utilization"][
                    "value"
                ],
            },
            "threshold": {
                "budget_violation_count": 0,
                "maximum_utilization": 1.0,
            },
            "passed": (
                summary["budget_violation_count"] == 0
                and summary["maximum_budget_utilization"]["value"] <= 1.0
            ),
        },
        "nonvacuous_final_budget": {
            "value": summary["maximum_final_component_budget"],
            "threshold": MAXIMUM_FINAL_BUDGET,
            "passed": summary["maximum_final_component_budget"]
            <= MAXIMUM_FINAL_BUDGET,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    policy_passed = all(
        gate["passed"] for gate in holdout_policy_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006q independent-holdout validity failure"
        decision = (
            "A setup, enumeration, direction-independence, stage-map, streaming, "
            "summation, positivity, finiteness, or serialization validity gate "
            "failed."
        )
        next_change = "Repair the first Q006q validity failure without tuning policy gates."
    elif policy_passed:
        outcome = "accepted"
        classification = "independent holdout supports registered forward-error policy"
        decision = (
            "Both independent scenarios and their aggregate stay inside the "
            "unchanged Q006o componentwise ULP envelope with a nonvacuous final "
            "budget."
        )
        next_change = (
            "Preregister the Q007 degree-continuation domain, degrees, residual "
            "holdout, and rollout gates."
        )
    else:
        outcome = "rejected"
        classification = "registered forward-error policy rejected by independent holdout"
        decision = (
            "At least one valid independent scenario violates the frozen Q006o "
            "componentwise envelope or the registered final-budget ceiling."
        )
        next_change = (
            "Freeze the first violation witness and diagnose the arithmetic "
            "envelope without changing its coefficient or ceiling."
        )
    return {
        "question": (
            "Does the frozen Q006o forward-error budget cover unmodified-map "
            "drift on independent seeds, amplitudes, and horizons?"
        ),
        "hypothesis": (
            "Both independent scenarios stay inside the unchanged two-sensitive-"
            "stage componentwise ULP envelope."
        ),
        "registered_setup": {
            **setup_threshold,
            "direction_count_per_chart": REGISTERED_DIRECTION_COUNT_PER_CHART,
            "trajectory_count": REGISTERED_TRAJECTORY_COUNT,
            "trajectory_step_count": REGISTERED_TRAJECTORY_STEP_COUNT,
            "component_check_count": REGISTERED_COMPONENT_CHECK_COUNT,
            "component_scale": "sum_xq abs(C_cq * f0_xq)",
            "component_budget": "2 * step * spacing(component_scale)",
            "maximum_final_component_budget": MAXIMUM_FINAL_BUDGET,
            "primary_measurement": "math.fsum",
            "independent_measurement": "Neumaier compensated sum",
            "map_modification": "none",
        },
        "direction_audit": direction_audit,
        "trajectory_records": records,
        "scenario_records": scenario_records,
        "summary": summary,
        "validity_gates": validity_gates,
        "scenario_policy_gates": scenario_policy_gates,
        "holdout_policy_gates": holdout_policy_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "This result is limited to the two registered finite-trajectory "
            "holdout scenarios. It is not an all-state or all-horizon roundoff "
            "theorem, does not establish chart existence or uniqueness, and does "
            "not validate invariance or shadowing at amplitude 0.02."
        ),
    }
