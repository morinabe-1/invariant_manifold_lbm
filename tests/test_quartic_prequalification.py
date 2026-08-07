from __future__ import annotations

import json

import pytest

from ttim_lbm.quartic_prequalification import (
    run_quartic_prequalification_audit,
)


@pytest.fixture(scope="module")
def quartic_prequalification():
    return run_quartic_prequalification_audit()


def test_q007c_reproduces_order_two_and_three_controls(
    quartic_prequalification,
) -> None:
    pair = quartic_prequalification["pair_control_summary"]
    triple = quartic_prequalification["triple_control_summary"]

    assert pair["record_count"] == 300
    assert pair["sector_counts"] == {
        "zero_wave_kinetic": 36,
        "internal_selected": 108,
        "external": 156,
    }
    assert pair["minimum_operator_singular_value"] == pytest.approx(
        0.00015502435597333105
    )
    assert pair["maximum_operator_condition_number"] == pytest.approx(
        14513.930547954875
    )
    assert triple["record_count"] == 2600
    assert triple["sector_counts"] == {
        "zero_wave_kinetic": 108,
        "internal_selected": 1044,
        "external": 1448,
    }
    assert triple["near_resonant_block_count"] == 24
    assert triple["minimum_operator_singular_value"] == pytest.approx(
        0.00020787972673242753
    )
    assert triple["maximum_operator_condition_number"] == pytest.approx(
        10821.814847751179
    )


def test_q007c_completely_enumerates_order_four_blocks(
    quartic_prequalification,
) -> None:
    summary = quartic_prequalification["quartic_summary"]

    assert summary["record_count"] == 17550
    assert summary["unique_input_index_count"] == 17550
    assert summary["duplicate_input_index_count"] == 0
    assert summary["sector_counts"] == {
        "zero_wave_kinetic": 846,
        "internal_selected": 4536,
        "external": 12168,
    }
    assert summary["permutation_multiplicity_sum"] == 24**4
    assert summary["permutation_multiplicity_values"] == [1, 4, 6, 12, 24]


def test_q007c_passes_conjugacy_and_wave_count_validity(
    quartic_prequalification,
) -> None:
    conjugacy = quartic_prequalification["conjugacy_audit"]
    wave_counts = quartic_prequalification["wave_count_audit"]

    assert quartic_prequalification["study_validity"] == "passed"
    assert all(
        gate["passed"]
        for gate in quartic_prequalification["validity_gates"].values()
    )
    assert conjugacy["missing_conjugate_count"] == 0
    assert conjugacy["output_wave_failure_count"] == 0
    assert conjugacy["output_kind_failure_count"] == 0
    assert conjugacy["maximum_multiplier_relative_error"] <= 1.0e-10
    assert conjugacy["maximum_singular_value_relative_error"] <= 1.0e-10
    assert wave_counts["output_wave_count"] == 81
    assert wave_counts["rotation_failure_count"] == 0
    assert wave_counts["conjugacy_failure_count"] == 0


def test_q007c_prequalifies_only_the_order_four_operator_family(
    quartic_prequalification,
) -> None:
    summary = quartic_prequalification["quartic_summary"]

    assert summary["numerically_singular_block_count"] == 0
    assert summary["near_resonant_block_count"] == 8
    assert summary["minimum_operator_singular_value"] == pytest.approx(
        6.485706497181907e-05
    )
    assert summary["maximum_operator_condition_number"] == pytest.approx(
        34673.915552593266
    )
    assert summary["maximum_operator_condition_number"] <= 1.0e9
    assert all(
        gate["passed"]
        for gate in quartic_prequalification["hypothesis_gates"].values()
    )
    assert quartic_prequalification["hypothesis_outcome"] == "accepted"
    assert quartic_prequalification["scientific_classification"] == (
        "order-four homological family prequalified on registered grid"
    )
    assert "does not construct" in quartic_prequalification["claim_boundary"]
    assert "not an invariant-manifold" in quartic_prequalification["claim_boundary"]


def test_q007c_result_is_strict_json(quartic_prequalification) -> None:
    json.dumps(quartic_prequalification, allow_nan=False)
