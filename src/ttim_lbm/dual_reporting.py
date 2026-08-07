"""Sealed Q006p integration audit for Q006i/Q006o dual reporting."""

from __future__ import annotations

import copy
import json
from typing import Any

import numpy as np

from .forward_error_budget import (
    MAXIMUM_FINAL_BUDGET,
    REGISTERED_STANDARD_DRIFT,
    REPRODUCTION_TOLERANCE,
    run_forward_error_budget_audit,
)
from .full2d_chart import SHADOW_SEED, run_full2d_quadratic_audit

REGISTERED_Q006I_DRIFT = 2.728496323152741e-12
REGISTERED_ORIGINAL_THRESHOLD = 1.0e-12
REGISTERED_DIRECTION_COUNT_PER_CHART = 32
REGISTERED_TOTAL_DIRECTION_COUNT = 64
REGISTERED_AMPLITUDE = 0.01
REGISTERED_STEPS = 100


def _direction_alignment(
    q006i_cycle: dict[str, Any],
    q006o_cycle: dict[str, Any],
) -> tuple[list[dict[str, Any]], float]:
    q006o_lookup = {
        (record["chart"], record["direction_index"]): record
        for record in q006o_cycle["trajectory_budget_records"]
    }
    records = []
    maximum_error = 0.0
    for chart in ("linear", "quadratic"):
        q006i_records = q006i_cycle["shadowing_campaign"][chart][
            "direction_records"
        ]
        for direction_index, q006i_record in enumerate(q006i_records):
            q006o_record = q006o_lookup[(chart, direction_index)]
            q006i_direction = np.asarray(q006i_record["direction"], dtype=np.float64)
            q006o_direction = np.asarray(q006o_record["direction"], dtype=np.float64)
            error = float(np.max(np.abs(q006i_direction - q006o_direction)))
            maximum_error = max(maximum_error, error)
            records.append(
                {
                    "chart": chart,
                    "direction_index": direction_index,
                    "maximum_absolute_difference": error,
                }
            )
    return records, maximum_error


def _setup_alignment(
    q006i_cycle: dict[str, Any],
    q006o_cycle: dict[str, Any],
) -> dict[str, Any]:
    scope = q006i_cycle["registered_scope"]
    setup = q006o_cycle["registered_setup"]
    q006i_shadow = q006i_cycle["shadowing_campaign"]
    values = {
        "q006i_grid": scope["grid"],
        "q006o_grid": [setup["size"], setup["size"]],
        "q006i_omega": scope["omega"],
        "q006o_omega": setup["omega"],
        "q006i_eta": scope["eta"],
        "q006o_eta": setup["eta"],
        "q006i_scope_shadow_seed": scope["shadow_seed"],
        "q006i_linear_shadow_seed": q006i_shadow["linear"]["seed"],
        "q006i_quadratic_shadow_seed": q006i_shadow["quadratic"]["seed"],
        "q006o_runner_direction_seed": SHADOW_SEED,
        "q006i_linear_amplitude": q006i_shadow["linear"]["amplitude"],
        "q006i_quadratic_amplitude": q006i_shadow["quadratic"]["amplitude"],
        "q006o_amplitude": setup["amplitude"],
        "q006i_linear_steps": q006i_shadow["linear"]["steps"],
        "q006i_quadratic_steps": q006i_shadow["quadratic"]["steps"],
        "q006o_steps": setup["steps"],
        "q006o_chart_types": setup["chart_types"],
    }
    passed = (
        values["q006i_grid"] == values["q006o_grid"] == [17, 17]
        and values["q006i_omega"] == values["q006o_omega"] == 1.5
        and values["q006i_eta"] == values["q006o_eta"] == 0.01
        and values["q006i_scope_shadow_seed"]
        == values["q006i_linear_shadow_seed"]
        == values["q006i_quadratic_shadow_seed"]
        == values["q006o_runner_direction_seed"]
        == SHADOW_SEED
        and values["q006i_linear_amplitude"]
        == values["q006i_quadratic_amplitude"]
        == values["q006o_amplitude"]
        == REGISTERED_AMPLITUDE
        and values["q006i_linear_steps"]
        == values["q006i_quadratic_steps"]
        == values["q006o_steps"]
        == REGISTERED_STEPS
        and values["q006o_chart_types"] == ["linear", "quadratic"]
    )
    return {"value": values, "passed": passed}


def _dual_columns(
    q006i_cycle: dict[str, Any],
    q006o_cycle: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    original_gates = copy.deepcopy(q006i_cycle["hypothesis_gates"])
    policy_gates = copy.deepcopy(original_gates)
    standard_summary = q006o_cycle["summary"]
    standard_policy_passed = q006o_cycle["standard_policy_outcome"] == "passed"
    policy_gates["global_conservation"] = {
        "measurement": "Q006o registered componentwise forward-error policy",
        "value": {
            "budget_violation_count": standard_summary["budget_violation_count"],
            "maximum_utilization": standard_summary[
                "maximum_budget_utilization"
            ]["value"],
            "maximum_final_component_budget": standard_summary[
                "maximum_final_component_budget"
            ],
        },
        "threshold": {
            "budget_violation_count": 0,
            "maximum_utilization": 1.0,
            "maximum_final_component_budget": MAXIMUM_FINAL_BUDGET,
        },
        "passed": standard_policy_passed,
        "original_gate_preserved_separately": True,
    }
    original_failed = [
        name for name, gate in original_gates.items() if not gate["passed"]
    ]
    policy_failed = [
        name for name, gate in policy_gates.items() if not gate["passed"]
    ]
    original = {
        "gates": original_gates,
        "failed_gate_names": original_failed,
        "failed_gate_count": len(original_failed),
        "sealed_study_validity": q006i_cycle["study_validity"],
        "sealed_hypothesis_outcome": q006i_cycle["hypothesis_outcome"],
        "sealed_scientific_classification": q006i_cycle[
            "scientific_classification"
        ],
    }
    policy = {
        "gates": policy_gates,
        "failed_gate_names": policy_failed,
        "failed_gate_count": len(policy_failed),
        "global_gate_replacement_only": all(
            policy_gates[name] == original_gates[name]
            for name in original_gates
            if name != "global_conservation"
        ),
    }
    return original, policy


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_dual_reporting_audit() -> dict[str, Any]:
    """Run the sealed Q006p dual-reporting integration audit."""

    q006i_cycle = run_full2d_quadratic_audit()
    q006o_cycle = run_forward_error_budget_audit()
    direction_records, maximum_direction_error = _direction_alignment(
        q006i_cycle,
        q006o_cycle,
    )
    setup_alignment = _setup_alignment(q006i_cycle, q006o_cycle)
    original, policy = _dual_columns(q006i_cycle, q006o_cycle)
    q006i_drift = q006i_cycle["hypothesis_gates"]["global_conservation"][
        "value"
    ]
    q006o_drift = q006o_cycle["summary"]["uniform_projection"][
        "standard_maximum_drift"
    ]
    drift_difference = abs(q006i_drift - q006o_drift)
    summary = {
        "direction_alignment_record_count": len(direction_records),
        "maximum_direction_alignment_error": maximum_direction_error,
        "q006i_original_maximum_drift": q006i_drift,
        "q006o_fsum_maximum_drift": q006o_drift,
        "q006i_q006o_drift_difference": drift_difference,
        "original_failed_gate_count": original["failed_gate_count"],
        "original_failed_gate_names": original["failed_gate_names"],
        "policy_failed_gate_count": policy["failed_gate_count"],
        "policy_failed_gate_names": policy["failed_gate_names"],
        "q006o_standard_policy_outcome": q006o_cycle[
            "standard_policy_outcome"
        ],
        "q006o_uniform_policy_outcome": q006o_cycle[
            "uniform_policy_outcome"
        ],
        "budget_violation_count": q006o_cycle["summary"][
            "budget_violation_count"
        ],
        "maximum_budget_utilization": q006o_cycle["summary"][
            "maximum_budget_utilization"
        ]["value"],
        "maximum_final_component_budget": q006o_cycle["summary"][
            "maximum_final_component_budget"
        ],
    }
    serializable_probe = {
        "setup_alignment": setup_alignment,
        "direction_alignment_records": direction_records,
        "original_column": original,
        "policy_column": policy,
        "summary": summary,
    }
    q006i_all_validity = all(
        gate["passed"] for gate in q006i_cycle["validity_gates"].values()
    )
    q006o_all_validity = all(
        gate["passed"] for gate in q006o_cycle["validity_gates"].values()
    )
    original_global_gate = original["gates"]["global_conservation"]
    validity_gates = {
        "sealed_study_validity": {
            "value": {
                "q006i_study_validity": q006i_cycle["study_validity"],
                "q006i_all_validity_gates_passed": q006i_all_validity,
                "q006o_study_validity": q006o_cycle["study_validity"],
                "q006o_all_validity_gates_passed": q006o_all_validity,
            },
            "threshold": {
                "study_validity": "passed",
                "all_validity_gates_passed": True,
            },
            "passed": (
                q006i_cycle["study_validity"] == "passed"
                and q006i_all_validity
                and q006o_cycle["study_validity"] == "passed"
                and q006o_all_validity
            ),
        },
        "registered_setup_alignment": {
            "value": setup_alignment["value"],
            "threshold": "all registered Q006i/Q006o setup fields agree",
            "passed": setup_alignment["passed"],
        },
        "registered_direction_alignment": {
            "value": {
                "record_count": len(direction_records),
                "maximum_absolute_difference": maximum_direction_error,
            },
            "threshold": {
                "record_count": REGISTERED_TOTAL_DIRECTION_COUNT,
                "maximum_absolute_difference": 0.0,
            },
            "passed": (
                len(direction_records) == REGISTERED_TOTAL_DIRECTION_COUNT
                and maximum_direction_error == 0.0
            ),
        },
        "registered_drift_reproduction": {
            "value": {
                "q006i_absolute_error": abs(
                    q006i_drift - REGISTERED_Q006I_DRIFT
                ),
                "q006o_absolute_error": abs(
                    q006o_drift - REGISTERED_STANDARD_DRIFT
                ),
                "cross_measurement_difference": drift_difference,
            },
            "threshold": REPRODUCTION_TOLERANCE,
            "passed": (
                abs(q006i_drift - REGISTERED_Q006I_DRIFT)
                <= REPRODUCTION_TOLERANCE
                and abs(q006o_drift - REGISTERED_STANDARD_DRIFT)
                <= REPRODUCTION_TOLERANCE
                and drift_difference <= REPRODUCTION_TOLERANCE
            ),
        },
        "original_global_gate_preserved": {
            "value": {
                "threshold": original_global_gate["threshold"],
                "passed": original_global_gate["passed"],
                "q006i_hypothesis_outcome": q006i_cycle[
                    "hypothesis_outcome"
                ],
            },
            "threshold": {
                "threshold": REGISTERED_ORIGINAL_THRESHOLD,
                "passed": False,
                "q006i_hypothesis_outcome": "rejected",
            },
            "passed": (
                original_global_gate["threshold"]
                == REGISTERED_ORIGINAL_THRESHOLD
                and not original_global_gate["passed"]
                and q006i_cycle["hypothesis_outcome"] == "rejected"
            ),
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    dual_decision_gates = {
        "original_single_failure": {
            "value": {
                "failed_gate_count": original["failed_gate_count"],
                "failed_gate_names": original["failed_gate_names"],
            },
            "threshold": {
                "failed_gate_count": 1,
                "failed_gate_names": ["global_conservation"],
            },
            "passed": (
                original["failed_gate_count"] == 1
                and original["failed_gate_names"] == ["global_conservation"]
            ),
        },
        "policy_column_all_passed": {
            "value": {
                "failed_gate_count": policy["failed_gate_count"],
                "global_gate_replacement_only": policy[
                    "global_gate_replacement_only"
                ],
            },
            "threshold": {
                "failed_gate_count": 0,
                "global_gate_replacement_only": True,
            },
            "passed": (
                policy["failed_gate_count"] == 0
                and policy["global_gate_replacement_only"]
            ),
        },
        "q006o_policy_selection": {
            "value": {
                "standard": q006o_cycle["standard_policy_outcome"],
                "uniform": q006o_cycle["uniform_policy_outcome"],
            },
            "threshold": {"standard": "passed", "uniform": "failed"},
            "passed": (
                q006o_cycle["standard_policy_outcome"] == "passed"
                and q006o_cycle["uniform_policy_outcome"] == "failed"
            ),
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    dual_decision_passed = all(
        gate["passed"] for gate in dual_decision_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006p dual-reporting validity failure"
        decision = (
            "A sealed-study, setup, direction, drift, original-gate, or "
            "serialization validity gate failed."
        )
        next_change = "Repair the first Q006p validity failure without tuning it."
    elif dual_decision_passed:
        outcome = "accepted"
        classification = "dual reporting supports unmodified-map chart continuation"
        decision = (
            "The original Q006i column retains its sole conservation failure, "
            "while the aligned policy column replaces only that gate and passes "
            "all eight checks under the selected Q006o standard-map policy."
        )
        next_change = (
            "Preregister an independent-seed, amplitude, and horizon holdout "
            "audit for the operational forward-error budget."
        )
    else:
        outcome = "rejected"
        classification = "forward-error policy does not clear Q006i continuation"
        decision = (
            "The valid dual report does not preserve exactly one original failure "
            "or does not pass all policy-column and policy-selection gates."
        )
        next_change = "Stop continuation and isolate the first failed Q006p gate."
    return {
        "question": (
            "Can Q006i retain its original conservation rejection while an "
            "aligned Q006o policy column supports conditional chart continuation?"
        ),
        "hypothesis": (
            "The original column keeps exactly the global-conservation failure, "
            "whereas replacing only that gate with the aligned Q006o standard-map "
            "budget yields a fully passed policy column."
        ),
        "registered_setup": {
            "grid": [17, 17],
            "omega": 1.5,
            "eta": 0.01,
            "reduced_dimension": 24,
            "state_dimension": 2601,
            "quadratic_pair_count": 300,
            "shadow_seed": SHADOW_SEED,
            "direction_count_per_chart": REGISTERED_DIRECTION_COUNT_PER_CHART,
            "chart_types": ["linear", "quadratic"],
            "amplitude": REGISTERED_AMPLITUDE,
            "steps": REGISTERED_STEPS,
            "original_conservation_threshold": REGISTERED_ORIGINAL_THRESHOLD,
            "policy_component_budget": "2 * step * spacing(component_scale)",
            "map_modification": "none",
        },
        "setup_alignment": setup_alignment,
        "direction_alignment_records": direction_records,
        "original_column": original,
        "policy_column": policy,
        "summary": summary,
        "validity_gates": validity_gates,
        "dual_decision_gates": dual_decision_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "This integration result is limited to the same 64 registered "
            "trajectories. It preserves the sealed Q006i rejection, is not an "
            "all-state conservation or SSM-existence theorem, and requires an "
            "independent holdout before degree continuation."
        ),
    }
