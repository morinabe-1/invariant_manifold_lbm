from __future__ import annotations

import json

import pytest

from ttim_lbm.forward_error_budget import run_forward_error_budget_audit


@pytest.fixture(scope="module")
def budget_audit():
    return run_forward_error_budget_audit()


def test_q006o_reproduces_q006j_and_registered_enumeration(budget_audit) -> None:
    summary = budget_audit["summary"]

    assert budget_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in budget_audit["validity_gates"].values())
    assert summary["trajectory_count"] == 64
    assert summary["trajectory_step_count"] == 6400
    assert summary["component_budget_check_count"] == 19200
    assert summary["uniform_projection"]["projection_step_count"] == 6400
    assert summary["uniform_projection"]["standard_maximum_drift"] == pytest.approx(
        2.7285041507210106e-12
    )
    assert summary["uniform_projection"]["uniform_maximum_drift"] == pytest.approx(
        2.1600518690316044e-12
    )


def test_q006o_standard_map_passes_the_registered_ulp_budget(budget_audit) -> None:
    summary = budget_audit["summary"]

    assert budget_audit["standard_policy_outcome"] == "passed"
    assert all(
        gate["passed"] for gate in budget_audit["standard_policy_gates"].values()
    )
    assert summary["budget_violation_count"] == 0
    assert summary["maximum_budget_utilization"]["value"] == pytest.approx(0.5)
    assert summary["maximum_final_component_budget"] == pytest.approx(
        1.1368683772161603e-11
    )
    assert summary["maximum_streaming_fsum_increment"] == 0.0


def test_q006o_does_not_select_the_uniform_projection(budget_audit) -> None:
    uniform = budget_audit["summary"]["uniform_projection"]

    assert budget_audit["uniform_policy_outcome"] == "failed"
    assert not any(
        gate["passed"] for gate in budget_audit["uniform_policy_gates"].values()
    )
    assert uniform["worst_drift_improvement_factor"] == pytest.approx(
        1.2631660331120913
    )
    assert uniform["exact_zero_remaining_drift_count"] == 0
    assert uniform["nonzero_remaining_drift_count"] == 6400


def test_q006o_accepts_the_unmodified_map_policy_without_revising_q006i(
    budget_audit,
) -> None:
    assert budget_audit["hypothesis_outcome"] == "accepted"
    assert budget_audit["scientific_classification"] == (
        "unmodified equivariant map with registered forward-error budget preferred"
    )
    assert budget_audit["summary"]["minimum_population"] > 0.0
    assert "does not revise" in budget_audit["claim_boundary"]
    assert "not an all-state" in budget_audit["claim_boundary"]


def test_q006o_result_is_strict_json(budget_audit) -> None:
    json.dumps(budget_audit, allow_nan=False)
