from __future__ import annotations

from fractions import Fraction

import pytest

import research.q007ag_tube_radius_propagation as q007ag


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ag_cycle() -> dict:
    return q007ag.run_tube_radius_propagation_audit()


def test_q007ag_reproduces_all_sealed_inputs_and_q007s(
    q007ag_cycle: dict,
) -> None:
    inputs = q007ag_cycle["input_artifacts"]
    implementations = q007ag_cycle["implementation_source_audit"]
    old = q007ag_cycle["q007s_exact_reproduction"]

    assert set(inputs) == {"q007p", "q007s", "q007ae", "q007af"}
    assert all(record["passed"] for record in inputs.values())
    assert implementations[
        "all_registered_implementation_sha256_match"
    ]
    assert len(implementations["records"]) == 6
    assert old["passed"]
    assert old["stored_cycle_reproduced_exactly"]
    assert old["candidate_count"] == 891
    assert old["passing_candidate_count"] == 676
    assert old["candidate_digest_sha256"] == (
        q007ag.EXPECTED_OLD_CANDIDATE_DIGEST
    )
    assert old["selected_candidate_matches"]
    assert old["selection_boundary_reproduced"]


def test_q007ag_reproduces_q007ae_and_changes_only_rho_tau(
    q007ag_cycle: dict,
) -> None:
    boundary = q007ag_cycle["q007ae_radius_boundary_reproduction"]
    update = q007ag_cycle["constant_update_audit"]

    assert boundary["passed"]
    assert boundary["candidate_count"] == 119
    assert boundary["candidate_records_reproduced_exactly"]
    assert boundary["selected_modal_radius_decimal"] == "1e-16"
    assert boundary["selected_passed"]
    assert boundary["previous_modal_radius_decimal"] == "1e-15"
    assert not boundary["previous_passed"]
    assert _fraction(boundary["new_analytic_radius"]) == Fraction(
        1, 10**16
    )
    assert _fraction(
        boundary["analytic_radius_improvement_factor"]
    ) == 100
    assert update["passed"]
    assert update["changed_constant_names"] == ["rho", "tau"]
    assert update["only_rho_and_tau_changed"]
    assert update["q007s_selected_control_passes_with_new_constants"]


def test_q007ag_evaluates_the_preregistered_scaled_grid_exactly(
    q007ag_cycle: dict,
) -> None:
    grid = q007ag_cycle["scaled_candidate_grid_audit"]

    assert grid["passed"]
    assert grid["base_radius_count"] == 9
    assert grid["normal_radius_count"] == 99
    assert grid["candidate_count"] == 891
    assert grid["unique_cartesian_product"]
    assert grid["decision_arithmetic"] == (
        "exact fractions.Fraction signs only"
    )
    assert grid["passing_candidate_count"] == 757
    assert grid["canonical_candidate_digest_sha256"] == (
        q007ag.EXPECTED_NEW_CANDIDATE_DIGEST
    )
    assert len(grid["candidate_summaries"]) == 891
    assert len(grid["base_slice_boundaries"]) == 9


def test_q007ag_selects_a_strictly_larger_tube(
    q007ag_cycle: dict,
) -> None:
    selection = q007ag_cycle["selection"]
    selected = selection["selected_candidate"]

    assert selection["passed"]
    assert _fraction(selected["base_radius"]) == (
        q007ag.EXPECTED_SELECTED_BASE_RADIUS
    )
    assert _fraction(selected["normal_radius"]) == (
        q007ag.EXPECTED_SELECTED_NORMAL_RADIUS
    )
    assert selected["passed"]
    assert all(selected["gates"].values())
    assert _fraction(selection["base_radius_improvement_factor"]) == 100
    assert _fraction(selection["normal_radius_improvement_factor"]) == 10
    assert _fraction(
        selected["strict_margins"]["base_forward_invariance"]
    ) > 0
    assert _fraction(selected["normal_contraction"]) < Fraction(99, 100)
    assert _fraction(selected["tangent_conorm"]) > 0
    assert _fraction(selected["domination_ratio"]) < Fraction(999, 1000)


def test_q007ag_reproduces_the_registered_selection_boundary(
    q007ag_cycle: dict,
) -> None:
    selection = q007ag_cycle["selection"]
    first_larger = selection["first_larger_normal_candidate"]

    assert selection["registered_selection_boundary_reproduced"]
    assert selection["selected_slice_larger_candidate_count"] > 0
    assert selection["all_larger_normals_on_selected_slice_fail"]
    assert selection["larger_base_candidate_count"] == 0
    assert selection["all_larger_bases_fail_or_absent"]
    assert _fraction(first_larger["normal_radius"]) == (
        q007ag.EXPECTED_FIRST_LARGER_NORMAL_RADIUS
    )
    assert not first_larger["passed"]
    assert selection["first_larger_normal_failed_gate_names"] == [
        "base_forward_invariance"
    ]


def test_q007ag_accepts_only_the_fixed_grid_tube_enlargement(
    q007ag_cycle: dict,
) -> None:
    assert q007ag_cycle["study_validity"] == "passed"
    assert q007ag_cycle["hypothesis_outcome"] == "accepted"
    assert q007ag_cycle["scientific_classification"] == (
        "Q007ae analytic radius enlarges the registered "
        "external-coordinate tube"
    )
    assert len(q007ag_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"]
        for gate in q007ag_cycle["validity_gates"].values()
    )
    assert len(q007ag_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"]
        for gate in q007ag_cycle["hypothesis_gates"].values()
    )
    consequence = q007ag_cycle["theorem_consequence"]
    assert consequence["selected_registered_tube_forward_invariant"]
    assert consequence[
        "selected_registered_tube_uniformly_normal_contracting"
    ]
    assert consequence[
        "selected_registered_tube_strictly_normally_dominating"
    ]
    assert consequence[
        "both_q007s_registered_tube_radii_strictly_enlarged"
    ]
    assert not consequence["new_tube_population_positivity_certified"]
    assert not consequence["new_tube_stagewise_positivity_certified"]
    assert not consequence[
        "new_tube_binary64_or_mpfr_induction_certified"
    ]
