"""Sealed Q006o anchor-free arithmetic-policy audit."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import numpy.typing as npt

from .conservation_drift import (
    INDEPENDENT_SUM_TOLERANCE,
    REGISTERED_AMPLITUDE,
    REGISTERED_STAGE_RECORD_COUNT,
    REGISTERED_STEPS,
    REGISTERED_TRAJECTORY_COUNT,
    run_conservation_drift_audit,
)
from .d2q9 import conserved_moment_matrix
from .full2d_chart import Full2DQuadraticModel, build_full2d_quadratic_model

Array = npt.NDArray[np.float64]

REGISTERED_COMPONENT_CHECK_COUNT = 19200
REGISTERED_STANDARD_DRIFT = 2.7285041507210106e-12
REGISTERED_UNIFORM_DRIFT = 2.1600518690316044e-12
REPRODUCTION_TOLERANCE = 5.0e-15
CONSERVATION_SENSITIVE_STAGE_COUNT = 2
MAXIMUM_FINAL_BUDGET = 1.2e-11
MINIMUM_UNIFORM_IMPROVEMENT_FACTOR = 2.0
COMPONENT_NAMES = ("mass", "momentum_x", "momentum_y")


def _component_scales(state: Array, moment_matrix: Array) -> Array:
    contributions = (
        moment_matrix[:, None, None, :] * state[None, :, :, :]
    )
    return np.asarray(
        np.sum(np.abs(contributions), axis=(1, 2, 3)),
        dtype=np.float64,
    )


def _initial_state(
    model: Full2DQuadraticModel,
    trajectory: dict[str, Any],
) -> Array:
    chart = model.chart if trajectory["chart"] == "quadratic" else model.linear_chart
    direction = np.asarray(trajectory["direction"], dtype=np.float64)
    return chart.evaluate(REGISTERED_AMPLITUDE * direction).reshape(
        model.size,
        model.size,
        9,
    )


def _trajectory_budget_record(
    model: Full2DQuadraticModel,
    trajectory: dict[str, Any],
    moment_matrix: Array,
) -> dict[str, Any]:
    initial = _initial_state(model, trajectory)
    scales = _component_scales(initial, moment_matrix)
    component_ulps = np.spacing(scales)
    if np.any(component_ulps <= 0.0):
        raise ValueError("registered component scales must have positive ULPs")

    maximum_utilization = {
        component: {
            "value": 0.0,
            "step": 0,
            "signed_drift": 0.0,
            "absolute_drift": 0.0,
            "budget": 0.0,
        }
        for component in COMPONENT_NAMES
    }
    violation_count = 0
    budget_records = []
    for stage_record in trajectory["stage_records"]:
        step = int(stage_record["step"])
        drift = np.asarray(stage_record["total_fsum_drift"], dtype=np.float64)
        budgets = CONSERVATION_SENSITIVE_STAGE_COUNT * step * component_ulps
        absolute_drift = np.abs(drift)
        utilization = absolute_drift / budgets
        passed = absolute_drift <= budgets
        violation_count += int(np.count_nonzero(~passed))
        for component_index, component in enumerate(COMPONENT_NAMES):
            value = float(utilization[component_index])
            if value > maximum_utilization[component]["value"]:
                maximum_utilization[component] = {
                    "value": value,
                    "step": step,
                    "signed_drift": float(drift[component_index]),
                    "absolute_drift": float(absolute_drift[component_index]),
                    "budget": float(budgets[component_index]),
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

    final_budget = (
        CONSERVATION_SENSITIVE_STAGE_COUNT
        * REGISTERED_STEPS
        * component_ulps
    )
    return {
        "chart": trajectory["chart"],
        "direction_index": trajectory["direction_index"],
        "direction": trajectory["direction"],
        "component_scale": scales.tolist(),
        "component_ulp": component_ulps.tolist(),
        "final_budget": final_budget.tolist(),
        "budget_records": budget_records,
        "summary": {
            "component_check_count": 3 * len(budget_records),
            "budget_violation_count": violation_count,
            "maximum_utilization": maximum_utilization,
            "minimum_standard_population": trajectory["summary"][
                "minimum_population"
            ],
        },
    }


def _maximum_utilization_witness(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    witnesses = []
    for record in records:
        for component, witness in record["summary"]["maximum_utilization"].items():
            witnesses.append(
                {
                    "chart": record["chart"],
                    "direction_index": record["direction_index"],
                    "component": component,
                    **witness,
                }
            )
    return max(witnesses, key=lambda witness: witness["value"])


def _uniform_projection_summary(
    q006j_cycle: dict[str, Any],
) -> dict[str, Any]:
    standard_drift = q006j_cycle["summary"]["maximum_fsum_conservation_drift"][
        "norm"
    ]
    uniform_drift = q006j_cycle["summary"]["projection_control"][
        "maximum_compensated_conservation_drift"
    ]
    zero_remaining_count = 0
    step_count = 0
    maximum_remaining = {
        "norm": 0.0,
        "chart": "linear",
        "direction_index": 0,
        "step": 0,
        "signed_drift": [0.0, 0.0, 0.0],
    }
    for trajectory in q006j_cycle["projection_control_records"]:
        for correction in trajectory["correction_records"]:
            remaining = np.asarray(
                correction["remaining_local_fsum_drift"],
                dtype=np.float64,
            )
            norm = float(np.linalg.norm(remaining))
            step_count += 1
            if bool(np.all(remaining == 0.0)):
                zero_remaining_count += 1
            if norm > maximum_remaining["norm"]:
                maximum_remaining = {
                    "norm": norm,
                    "chart": trajectory["chart"],
                    "direction_index": trajectory["direction_index"],
                    "step": correction["step"],
                    "signed_drift": remaining.tolist(),
                }
    return {
        "standard_maximum_drift": standard_drift,
        "uniform_maximum_drift": uniform_drift,
        "worst_drift_improvement_factor": standard_drift / uniform_drift,
        "projection_step_count": step_count,
        "exact_zero_remaining_drift_count": zero_remaining_count,
        "nonzero_remaining_drift_count": step_count - zero_remaining_count,
        "maximum_remaining_local_drift": maximum_remaining,
        "maximum_single_correction_norm": q006j_cycle["summary"][
            "projection_control"
        ]["maximum_single_correction_norm"],
        "maximum_standard_state_difference": q006j_cycle["summary"][
            "projection_control"
        ]["maximum_standard_state_difference"],
        "minimum_uniform_population": q006j_cycle["summary"][
            "projection_control"
        ]["minimum_population"],
    }


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_forward_error_budget_audit() -> dict[str, Any]:
    """Run the sealed Q006o standard-map budget and uniform-control audit."""

    q006j_cycle = run_conservation_drift_audit()
    model = build_full2d_quadratic_model()
    moment_matrix = conserved_moment_matrix()
    records = [
        _trajectory_budget_record(model, trajectory, moment_matrix)
        for trajectory in q006j_cycle["trajectory_records"]
    ]
    uniform = _uniform_projection_summary(q006j_cycle)
    maximum_utilization = _maximum_utilization_witness(records)
    trajectory_step_count = sum(
        len(record["budget_records"]) for record in records
    )
    component_check_count = sum(
        record["summary"]["component_check_count"] for record in records
    )
    budget_violation_count = sum(
        record["summary"]["budget_violation_count"] for record in records
    )
    maximum_final_budget = max(
        max(record["final_budget"]) for record in records
    )
    minimum_standard_population = min(
        record["summary"]["minimum_standard_population"] for record in records
    )
    minimum_population = min(
        minimum_standard_population,
        uniform["minimum_uniform_population"],
    )
    maximum_independent_sum_difference = max(
        q006j_cycle["summary"]["maximum_independent_sum_component_difference"],
        q006j_cycle["summary"]["projection_control"][
            "maximum_independent_sum_component_difference"
        ],
    )
    summary = {
        "trajectory_count": len(records),
        "trajectory_step_count": trajectory_step_count,
        "component_budget_check_count": component_check_count,
        "budget_violation_count": budget_violation_count,
        "maximum_budget_utilization": maximum_utilization,
        "maximum_final_component_budget": maximum_final_budget,
        "minimum_population": minimum_population,
        "maximum_independent_sum_component_difference": (
            maximum_independent_sum_difference
        ),
        "maximum_streaming_fsum_increment": q006j_cycle["summary"][
            "maximum_streaming_fsum_drift"
        ],
        "uniform_projection": uniform,
    }
    serializable_probe = {
        "trajectory_budget_records": records,
        "summary": summary,
    }
    validity_gates = {
        "q006j_validity_reproduction": {
            "value": {
                "study_validity": q006j_cycle["study_validity"],
                "all_validity_gates_passed": all(
                    gate["passed"]
                    for gate in q006j_cycle["validity_gates"].values()
                ),
            },
            "threshold": {
                "study_validity": "passed",
                "all_validity_gates_passed": True,
            },
            "passed": (
                q006j_cycle["study_validity"] == "passed"
                and all(
                    gate["passed"]
                    for gate in q006j_cycle["validity_gates"].values()
                )
            ),
        },
        "registered_enumeration": {
            "value": {
                "trajectory_count": len(records),
                "trajectory_step_count": trajectory_step_count,
                "component_budget_check_count": component_check_count,
                "projection_step_count": uniform["projection_step_count"],
            },
            "threshold": {
                "trajectory_count": REGISTERED_TRAJECTORY_COUNT,
                "trajectory_step_count": REGISTERED_STAGE_RECORD_COUNT,
                "component_budget_check_count": REGISTERED_COMPONENT_CHECK_COUNT,
                "projection_step_count": REGISTERED_STAGE_RECORD_COUNT,
            },
            "passed": (
                len(records) == REGISTERED_TRAJECTORY_COUNT
                and trajectory_step_count == REGISTERED_STAGE_RECORD_COUNT
                and component_check_count == REGISTERED_COMPONENT_CHECK_COUNT
                and uniform["projection_step_count"]
                == REGISTERED_STAGE_RECORD_COUNT
            ),
        },
        "q006j_drift_reproduction": {
            "value": {
                "standard_absolute_error": abs(
                    uniform["standard_maximum_drift"]
                    - REGISTERED_STANDARD_DRIFT
                ),
                "uniform_absolute_error": abs(
                    uniform["uniform_maximum_drift"]
                    - REGISTERED_UNIFORM_DRIFT
                ),
            },
            "threshold": REPRODUCTION_TOLERANCE,
            "passed": (
                abs(
                    uniform["standard_maximum_drift"]
                    - REGISTERED_STANDARD_DRIFT
                )
                <= REPRODUCTION_TOLERANCE
                and abs(
                    uniform["uniform_maximum_drift"]
                    - REGISTERED_UNIFORM_DRIFT
                )
                <= REPRODUCTION_TOLERANCE
            ),
        },
        "exact_streaming_permutation": {
            "value": summary["maximum_streaming_fsum_increment"],
            "threshold": 0.0,
            "passed": summary["maximum_streaming_fsum_increment"] == 0.0,
        },
        "independent_compensated_sums": {
            "value": maximum_independent_sum_difference,
            "threshold": INDEPENDENT_SUM_TOLERANCE,
            "passed": maximum_independent_sum_difference
            <= INDEPENDENT_SUM_TOLERANCE,
        },
        "positive_registered_states": {
            "value": minimum_population,
            "threshold": 0.0,
            "passed": minimum_population > 0.0,
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    standard_policy_gates = {
        "componentwise_budget_coverage": {
            "value": {
                "budget_violation_count": budget_violation_count,
                "maximum_utilization": maximum_utilization["value"],
            },
            "threshold": {
                "budget_violation_count": 0,
                "maximum_utilization": 1.0,
            },
            "passed": (
                budget_violation_count == 0
                and maximum_utilization["value"] <= 1.0
            ),
        },
        "nonvacuous_final_budget": {
            "value": maximum_final_budget,
            "threshold": MAXIMUM_FINAL_BUDGET,
            "passed": maximum_final_budget <= MAXIMUM_FINAL_BUDGET,
        },
    }
    uniform_policy_gates = {
        "minimum_worst_drift_improvement": {
            "value": uniform["worst_drift_improvement_factor"],
            "threshold": MINIMUM_UNIFORM_IMPROVEMENT_FACTOR,
            "passed": uniform["worst_drift_improvement_factor"]
            >= MINIMUM_UNIFORM_IMPROVEMENT_FACTOR,
        },
        "exact_remaining_local_drift": {
            "value": uniform["exact_zero_remaining_drift_count"],
            "threshold": REGISTERED_STAGE_RECORD_COUNT,
            "passed": uniform["exact_zero_remaining_drift_count"]
            == REGISTERED_STAGE_RECORD_COUNT,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    standard_policy_passed = all(
        gate["passed"] for gate in standard_policy_gates.values()
    )
    uniform_policy_passed = all(
        gate["passed"] for gate in uniform_policy_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006o arithmetic-policy validity failure"
        decision = (
            "A Q006j reproduction, enumeration, streaming, independent-sum, "
            "positivity, finiteness, or serialization validity gate failed."
        )
        next_change = "Repair the first Q006o validity failure without tuning it."
    elif uniform_policy_passed:
        outcome = "accepted"
        classification = "smooth uniform correction preferred"
        decision = (
            "The anchor-free uniform projection meets both the registered exact-"
            "realization and two-fold worst-drift improvement requirements."
        )
        next_change = (
            "Preregister a full-chart residual and shadow audit for the smooth "
            "uniformly projected map."
        )
    elif standard_policy_passed:
        outcome = "accepted"
        classification = (
            "unmodified equivariant map with registered forward-error budget "
            "preferred"
        )
        decision = (
            "Every standard-map component drift lies within the registered two-"
            "sensitive-stage ULP envelope, while the uniform projection fails "
            "its preregistered selection requirements."
        )
        next_change = (
            "Preregister a Q006i dual-reporting audit that preserves the original "
            "1e-12 outcome and separately applies this finite-trajectory budget."
        )
    else:
        outcome = "rejected"
        classification = "neither anchor-free arithmetic policy passes"
        decision = (
            "The standard map violates its registered ULP envelope and the "
            "uniform projection does not meet both selection requirements."
        )
        next_change = "Stop continuation and isolate the first failed Q006o gate."
    return {
        "question": (
            "Should the anchor-free uniform projection replace the standard map, "
            "or does an explicit forward-error budget support leaving the smooth "
            "equivariant map unmodified?"
        ),
        "hypothesis": (
            "The unmodified standard map stays within a two-sensitive-stage ULP "
            "envelope, while the uniform projection fails its exact-realization "
            "or two-fold-improvement selection requirement."
        ),
        "registered_setup": {
            "size": model.size,
            "omega": model.omega,
            "eta": model.eta,
            "chart_types": ["linear", "quadratic"],
            "trajectory_count": REGISTERED_TRAJECTORY_COUNT,
            "amplitude": REGISTERED_AMPLITUDE,
            "steps": REGISTERED_STEPS,
            "controls": ["unmodified_standard", "uniform_projection"],
            "primary_measurement": "math.fsum",
            "independent_measurement": "Neumaier compensated sum",
            "conservation_sensitive_stages": ["collision", "filter"],
            "streaming_treatment": "exact periodic permutation",
            "component_scale": "sum_xq abs(C_cq * f0_xq)",
            "component_budget": "2 * step * spacing(component_scale)",
            "maximum_final_component_budget": MAXIMUM_FINAL_BUDGET,
            "minimum_uniform_improvement_factor": (
                MINIMUM_UNIFORM_IMPROVEMENT_FACTOR
            ),
            "uniform_exact_remaining_drift_required": True,
        },
        "trajectory_budget_records": records,
        "summary": summary,
        "validity_gates": validity_gates,
        "standard_policy_gates": standard_policy_gates,
        "uniform_policy_gates": uniform_policy_gates,
        "study_validity": "passed" if study_valid else "failed",
        "standard_policy_outcome": (
            "passed" if standard_policy_passed else "failed"
        ),
        "uniform_policy_outcome": (
            "passed" if uniform_policy_passed else "failed"
        ),
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "The ULP envelope is an operational finite-trajectory policy, not an "
            "all-state or all-horizon roundoff theorem. This audit does not revise "
            "the sealed Q006i or Q006j 1e-12 outcomes and does not adopt the Q006l "
            "unique-anchor or Q006k fixed-site controls."
        ),
    }
