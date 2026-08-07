from __future__ import annotations

import json

import pytest

from ttim_lbm.cubic_prequalification import run_cubic_prequalification_audit


@pytest.fixture(scope="module")
def cubic_prequalification():
    return run_cubic_prequalification_audit()


def test_q007a_reproduces_the_q006i_pair_operators(cubic_prequalification) -> None:
    summary = cubic_prequalification["pair_control_summary"]

    assert summary["record_count"] == 300
    assert summary["sector_counts"] == {
        "zero_wave_kinetic": 36,
        "internal_selected": 108,
        "external": 156,
    }
    assert summary["numerically_singular_block_count"] == 0
    assert summary["minimum_operator_singular_value"] == pytest.approx(
        0.00015502435597333105
    )
    assert summary["maximum_operator_condition_number"] == pytest.approx(
        14513.930547954875
    )


def test_q007a_completely_enumerates_cubic_triples(cubic_prequalification) -> None:
    summary = cubic_prequalification["triple_summary"]
    records = cubic_prequalification["triple_records"]

    assert summary["record_count"] == 2600
    assert summary["unique_input_index_count"] == 2600
    assert summary["duplicate_input_index_count"] == 0
    assert summary["sector_counts"] == {
        "zero_wave_kinetic": 108,
        "internal_selected": 1044,
        "external": 1448,
    }
    assert sum(record["permutation_multiplicity"] for record in records) == 24**3
    assert {record["permutation_multiplicity"] for record in records} == {1, 3, 6}


def test_q007a_passes_conjugacy_and_wave_count_validity(
    cubic_prequalification,
) -> None:
    conjugacy = cubic_prequalification["conjugacy_audit"]
    wave_counts = cubic_prequalification["wave_count_audit"]

    assert cubic_prequalification["study_validity"] == "passed"
    assert all(
        gate["passed"] for gate in cubic_prequalification["validity_gates"].values()
    )
    assert conjugacy["missing_conjugate_count"] == 0
    assert conjugacy["output_wave_failure_count"] == 0
    assert conjugacy["maximum_multiplier_relative_error"] <= 1.0e-10
    assert conjugacy["maximum_singular_value_relative_error"] <= 1.0e-10
    assert wave_counts["output_wave_count"] == 49
    assert wave_counts["rotation_failure_count"] == 0
    assert wave_counts["conjugacy_failure_count"] == 0


def test_q007a_prequalifies_only_the_operator_family(cubic_prequalification) -> None:
    summary = cubic_prequalification["triple_summary"]

    assert summary["numerically_singular_block_count"] == 0
    assert summary["near_resonant_block_count"] == 24
    assert summary["minimum_operator_singular_value"] == pytest.approx(
        0.00020787972673242753
    )
    assert summary["maximum_operator_condition_number"] == pytest.approx(
        10821.814847751179
    )
    assert summary["maximum_operator_condition_number"] <= 1.0e9
    assert all(
        gate["passed"]
        for gate in cubic_prequalification["hypothesis_gates"].values()
    )
    assert cubic_prequalification["hypothesis_outcome"] == "accepted"
    assert cubic_prequalification["scientific_classification"] == (
        "order-three homological family prequalified on registered grid"
    )
    assert "does not construct" in cubic_prequalification["claim_boundary"]
    assert "not an SSM" in cubic_prequalification["claim_boundary"]


def test_q007a_result_is_strict_json(cubic_prequalification) -> None:
    json.dumps(cubic_prequalification, allow_nan=False)
