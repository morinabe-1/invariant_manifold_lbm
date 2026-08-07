from __future__ import annotations

import json

import pytest

from ttim_lbm.normal_refinement import (
    audit_fixed_family_condition,
    run_normal_gap_refinement_audit,
)


@pytest.fixture(scope="module")
def refinement_audit() -> dict[str, object]:
    return run_normal_gap_refinement_audit()


def test_reference_condition_reproduces_the_q006r_split_verdict() -> None:
    condition = audit_fixed_family_condition(17, 1.2)

    assert condition["pair_count"] == 136
    assert condition["selected_real_dimension"] == 16
    assert condition["coefficient_passed"]
    assert condition["blockwise_projector_passed"]
    assert not condition["normal_dominance_passed"]
    assert condition["numerically_singular_external_block_count"] == 0
    assert condition["near_singular_external_block_count"] == 0
    assert condition["normal_dominance_gap"] == pytest.approx(
        -0.013096403424400549,
        abs=1.0e-14,
    )
    assert condition["maximum_condition_number"] == pytest.approx(
        1894.2921350767735,
        rel=1.0e-12,
    )


def test_registered_campaign_records_the_preregistered_mixed_outcome(
    refinement_audit: dict[str, object],
) -> None:
    audit = refinement_audit
    summary = audit["summary"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "inconclusive"
    assert len(audit["conditions"]) == 20
    assert summary["refinement_condition_count"] == 16
    assert summary["refinement_coefficient_and_blockwise_pass_count"] == 13
    assert summary["refinement_negative_gap_count"] == 16
    assert summary["refinement_axial_near_nyquist_worst_count"] == 16
    assert summary["coarse_grid_passes"] == []
    assert summary["nyquist_anchor_passed"]
    assert not summary["registered_obstruction_supported"]
    assert summary["viable_omegas"] == []
    assert summary["selected_viable_omega"] is None
    assert all(gate["passed"] for gate in audit["validity_gates"].values())


def test_all_registered_normal_gaps_are_negative_and_near_nyquist(
    refinement_audit: dict[str, object],
) -> None:
    conditions = refinement_audit["conditions"]

    assert all(condition["normal_dominance_gap"] < 0.0 for condition in conditions)
    assert all(
        condition["worst_external_is_axial_near_nyquist"]
        for condition in conditions
    )
    for omega in (1.0, 1.2, 1.5, 1.8):
        scaled = [
            condition["scaled_normal_dominance_gap_n_squared"]
            for condition in conditions
            if condition["omega"] == omega
        ]
        assert all(value < -0.6 for value in scaled)
        assert abs(scaled[-1] - scaled[-2]) < 0.01


def test_only_three_high_resolution_conditions_fail_the_coefficient_gate(
    refinement_audit: dict[str, object],
) -> None:
    failures = {
        (condition["grid_size"], condition["omega"])
        for condition in refinement_audit["conditions"]
        if not condition["coefficient_passed"]
    }

    assert failures == {(65, 1.8), (129, 1.5), (129, 1.8)}
    for condition in refinement_audit["conditions"]:
        if (condition["grid_size"], condition["omega"]) not in failures:
            continue
        assert condition["numerically_singular_external_block_count"] == 0
        assert condition["maximum_materially_forced_near_condition_number"] > 1.0e4
        assert condition["maximum_condition_number"] < 1.0e8
        material_pairs = [
            pair
            for pair in condition["pair_table"]
            if pair["near_singular_count"] > 0
            and pair["near_forcing_sensitivity"] is not None
            and pair["near_forcing_sensitivity"] >= 1.0e-10
        ]
        assert material_pairs
        assert any(abs(pair["output_wave_index"][0]) == 2 for pair in material_pairs) or any(
            abs(pair["output_wave_index"][1]) == 2 for pair in material_pairs
        )


def test_direct_nyquist_anchors_recover_minus_one(
    refinement_audit: dict[str, object],
) -> None:
    for anchor in refinement_audit["nyquist_anchors"]:
        for direction in anchor["directions"].values():
            assert direction["minimum_distance_to_minus_one"] < 1.0e-12
            assert direction["minus_one_count_at_tolerance"] >= 1


def test_refinement_record_is_strict_json(
    refinement_audit: dict[str, object],
) -> None:
    rendered = json.dumps(refinement_audit, allow_nan=False)
    assert "mixed coefficient/normal-gap obstruction" in rendered


@pytest.mark.parametrize(
    ("size", "omega"),
    [(7, 1.2), (17, 1.1), (257, 1.8)],
)
def test_condition_audit_rejects_unregistered_parameters(
    size: int,
    omega: float,
) -> None:
    with pytest.raises(ValueError, match="sealed Q006n"):
        audit_fixed_family_condition(size, omega)
