from __future__ import annotations

import json

import pytest

from ttim_lbm.forward_error_holdout import run_forward_error_holdout_audit


@pytest.fixture(scope="module")
def holdout_audit():
    return run_forward_error_holdout_audit()


def test_q006q_uses_only_registered_independent_directions(holdout_audit) -> None:
    direction_audit = holdout_audit["direction_audit"]

    assert direction_audit["q006o_reference_seed"] == 20260810
    assert direction_audit["duplicate_count"] == 0
    assert direction_audit["all_direction_hashes_distinct"]
    assert direction_audit["maximum_norm_error"] <= 5.0e-15
    assert [
        record["direction_seed"]
        for record in direction_audit["scenario_records"]
    ] == [20260811, 20260812]


def test_q006q_completely_enumerates_both_scenarios(holdout_audit) -> None:
    summary = holdout_audit["summary"]

    assert summary["trajectory_count"] == 128
    assert summary["trajectory_step_count"] == 16000
    assert summary["component_budget_check_count"] == 48000
    assert len(holdout_audit["trajectory_records"]) == 128
    assert [
        (record["scenario"], record["amplitude"], record["steps"])
        for record in holdout_audit["scenario_records"]
    ] == [
        ("long_horizon", 0.005, 200),
        ("large_amplitude", 0.02, 50),
    ]


def test_q006q_passes_all_validity_gates(holdout_audit) -> None:
    summary = holdout_audit["summary"]

    assert holdout_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in holdout_audit["validity_gates"].values())
    assert summary["maximum_stage_map_identity_error"] == 0.0
    assert summary["maximum_streaming_fsum_increment"] == 0.0
    assert summary["maximum_independent_sum_component_difference"] <= 5.0e-14
    assert summary["minimum_population"] > 0.0


def test_q006q_applies_the_frozen_budget_to_every_component(holdout_audit) -> None:
    for trajectory in holdout_audit["trajectory_records"]:
        component_ulps = trajectory["component_ulp"]
        for record in trajectory["budget_records"]:
            expected = [
                2 * record["step"] * component_ulp
                for component_ulp in component_ulps
            ]
            assert record["budget"] == expected
            assert all(record["passed"])


def test_q006q_accepts_the_independent_holdout_only(holdout_audit) -> None:
    summary = holdout_audit["summary"]

    assert all(
        gate["passed"] for gate in holdout_audit["scenario_policy_gates"].values()
    )
    assert all(
        gate["passed"] for gate in holdout_audit["holdout_policy_gates"].values()
    )
    assert summary["budget_violation_count"] == 0
    assert summary["maximum_budget_utilization"]["value"] == pytest.approx(0.5)
    assert summary["maximum_final_component_budget"] == pytest.approx(
        2.2737367544323206e-11
    )
    assert summary["maximum_final_component_budget"] <= 2.4e-11
    assert holdout_audit["hypothesis_outcome"] == "accepted"
    assert holdout_audit["scientific_classification"] == (
        "independent holdout supports registered forward-error policy"
    )
    assert "not an all-state" in holdout_audit["claim_boundary"]
    assert "amplitude 0.02" in holdout_audit["claim_boundary"]


def test_q006q_result_is_strict_json(holdout_audit) -> None:
    json.dumps(holdout_audit, allow_nan=False)
