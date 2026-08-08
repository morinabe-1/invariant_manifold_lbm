from __future__ import annotations

from fractions import Fraction

import pytest

import research.q007ad_asymmetric_phase_resolvent as q007ad


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ad_cycle() -> dict:
    return q007ad.run_asymmetric_phase_resolvent_audit()


def test_q007ad_registered_target_is_above_exact_critical_gap() -> None:
    assert q007ad.REGISTERED_CRITICAL_GAP == Fraction(
        q007ad.REGISTERED_CRITICAL_GAP_NUMERATOR,
        q007ad.REGISTERED_CRITICAL_GAP_DENOMINATOR,
    )
    assert q007ad.PHASE_GAP == Fraction(21, 10**9)
    assert q007ad.PHASE_GAP > q007ad.REGISTERED_CRITICAL_GAP
    assert q007ad.PHASE_GAP / q007ad.REGISTERED_CRITICAL_GAP > Fraction(
        104, 100
    )


def test_q007ad_preserves_q007ac_invalid_stop_and_uses_original_discs(
    q007ad_cycle: dict,
) -> None:
    prior = q007ad_cycle["q007ac_invalid_input_audit"]
    discs = q007ad_cycle["original_selected_disc_audit"]

    assert prior["passed"]
    assert prior["study_gate"] == "failed"
    assert prior["scientific_outcome"] == "inconclusive"
    assert prior["failed_validity_gates"] == [
        "spectral_disc_reconstruction"
    ]
    assert prior["failed_hypothesis_gates"] == [
        "registered_phase_gap_certified"
    ]
    assert discs["disc_count"] == 6
    assert discs["all_original_discs_within_q007n_working_sigma"]
    assert discs["paired_acoustic_radii_equal"]
    assert _fraction(
        discs["product_factor_modulus_inflation_over_q007n"]
    ) == 0
    assert _fraction(discs["minimum_sigma_slack"]) > 0


def test_q007ad_reproduces_screen_and_completes_original_phase_expansion(
    q007ad_cycle: dict,
) -> None:
    separation = q007ad_cycle["phase_aware_separation_audit"]
    screen = separation["screen"]
    phase = separation["phase"]

    assert separation["q007ac_screen_reproduced_exactly"]
    assert separation["target_log_digest_matches_q007ac"]
    assert screen["aggregate_count"] == q007ad.q007ac.EXPECTED_AGGREGATE_COUNT
    assert screen["dangerous_aggregate_count"] == 826
    assert screen["dangerous_expanded_product_count"] == 108_273
    assert screen["phase_comparison_count"] == 287_929
    assert phase["complete"]
    assert phase["expanded_product_count"] == 108_273
    assert phase["comparison_count"] == 287_929
    assert phase["threshold_outward_binary_bits"] == 256
    assert _fraction(phase["maximum_threshold_rounding_increment"]) < (
        Fraction(1, 2**256)
    )
    assert phase["failed_comparison_count"] == 0
    assert phase["all_phase_comparisons_strict"]
    assert _fraction(phase["minimum_squared_margin"]) > 0
    assert _fraction(
        phase["minimum_margin_witness"][
            "certified_complex_distance_lower"
        ]
    ) > q007ad.PHASE_GAP


def test_q007ad_external_inverse_becomes_internal_limited(
    q007ad_cycle: dict,
) -> None:
    critical = q007ad_cycle["critical_gap_audit"]
    inverse = q007ad_cycle["inverse_refinement"]

    assert critical["critical_gap_matches_registration"]
    assert critical["target_strictly_exceeds_critical"]
    assert critical[
        "working_external_inverse_strictly_below_internal"
    ]
    assert _fraction(
        inverse["working_asymmetric_phase_external_inverse_upper"]
    ) < _fraction(inverse["q007o_working_internal_pair_inverse_upper"])
    assert inverse["new_total_is_internal_limited"]
    assert inverse["total_inverse_improvement_factor"]["float"] == (
        pytest.approx(125.28856057411295)
    )
    assert inverse["q007ac_counterfactual_inverse_not_reused"]


def test_q007ad_accepts_registered_radius_boundary(
    q007ad_cycle: dict,
) -> None:
    search = q007ad_cycle["radius_comparison"][
        "asymmetric_phase_refined_radius_search"
    ]

    assert q007ad_cycle["study_validity"] == "passed"
    assert q007ad_cycle["hypothesis_outcome"] == "accepted"
    assert q007ad_cycle["scientific_classification"] == (
        "original asymmetric discs certify the critical "
        "external-output phase gap"
    )
    assert all(
        gate["passed"]
        for gate in q007ad_cycle["validity_gates"].values()
    )
    assert all(
        gate["passed"]
        for gate in q007ad_cycle["hypothesis_gates"].values()
    )
    assert q007ad_cycle["radius_comparison"][
        "registered_radius_boundary_matches"
    ]
    assert search["selected_candidate"]["modal_radius_decimal"] == "1e-16"
    assert search["previous_larger_candidate"][
        "modal_radius_decimal"
    ] == "1e-15"
    assert not search["previous_larger_candidate"]["passed"]
    consequence = q007ad_cycle["theorem_consequence"]
    assert consequence[
        "registered_modal_l1_radius_1e_minus_16_certified"
    ]
    assert not consequence[
        "q007p_through_q007ab_tube_constants_enlarged"
    ]
