from __future__ import annotations

import json

import pytest

from ttim_lbm.cubic_radius import run_cubic_radius_audit


@pytest.fixture(scope="module")
def cubic_radius():
    return run_cubic_radius_audit()


def test_q007b1_accepts_the_registered_independent_radius(cubic_radius) -> None:
    result = cubic_radius

    assert result["study_validity"] == "passed"
    assert result["hypothesis_outcome"] == "accepted"
    assert result["scientific_classification"] == (
        "registered cubic improvement radius localized without fold signature"
    )
    assert all(gate["passed"] for gate in result["validity_gates"].values())
    assert all(gate["passed"] for gate in result["hypothesis_gates"].values())
    assert not result["preserved_prior_outcomes"]["revised"]
    json.dumps(result, allow_nan=False)


def test_q007b1_reproduces_coefficients_and_independent_directions(
    cubic_radius,
) -> None:
    result = cubic_radius

    assert result["validity_gates"]["sealed_coefficient_identity"]["passed"]
    registration = result["direction_registration"]
    assert registration["duplicate_count"] == 0
    assert registration["maximum_norm_error"] <= 5.0e-15


def test_q007b1_radius_orders_and_effect_size_pass(cubic_radius) -> None:
    result = cubic_radius
    summary = result["radius_campaign"]["summary"]

    assert 2.9 <= summary["minimum_quadratic_slope"]
    assert summary["maximum_quadratic_slope"] <= 3.1
    assert 3.85 <= summary["minimum_cubic_slope"]
    assert summary["maximum_cubic_slope"] <= 4.15
    assert 0.9 <= summary["minimum_ratio_slope"]
    assert summary["maximum_ratio_slope"] <= 1.1
    assert summary["maximum_acceptance_radius_ratio"] <= 0.10
    assert summary["acceptance_radius_failure_count"] == 0
    assert summary["ratio_failure_counts_by_amplitude"][3] == 0
    assert summary["ratio_failure_counts_by_amplitude"][-1] > 0


def test_q007b1_validates_the_jacobian_and_radial_immersion(
    cubic_radius,
) -> None:
    result = cubic_radius
    jacobian = result["jacobian_validity_campaign"]["summary"]
    immersion = result["immersion_campaign"]["summary"]

    assert jacobian["minimum_analytic_action_norm"] > 1.0e-12
    assert jacobian["maximum_best_relative_error"] <= 1.0e-7
    assert immersion["minimum_normalized_singular_value"] >= 0.8
    assert result["immersion_campaign"]["unique_sample_count"] == 321


def test_q007b1_records_near_resonance_as_a_non_gate_diagnostic(
    cubic_radius,
) -> None:
    result = cubic_radius
    diagnostic = result["near_resonant_diagnostic"]
    summary = diagnostic["summary_by_amplitude"]["0.004"]

    assert diagnostic["near_resonant_triple_count"] == 24
    assert summary["reduced_near_fraction_range"] == [0.0, 0.0]
    assert not summary[
        "reduced_near_fraction_residual_ratio_spearman"
    ]["defined"]
    assert summary["chart_correction_residual_ratio_spearman"]["defined"]
    assert (
        summary["chart_correction_residual_ratio_spearman"]["correlation"]
        > 0.9
    )
    assert "near_resonant_diagnostic" not in result["hypothesis_gates"]


def test_q007b1_shadowing_and_forward_error_pass(cubic_radius) -> None:
    result = cubic_radius
    summary = result["shadowing_campaign"]["summary"]

    assert all(
        ratio <= 0.8
        for ratio in summary[
            "maximum_directional_improvement_ratios"
        ].values()
    )
    assert summary["cubic_budget_component_check_count"] == 9600
    assert summary["cubic_budget_violation_count"] == 0
    assert summary["maximum_final_component_budget"] <= 1.2e-11
