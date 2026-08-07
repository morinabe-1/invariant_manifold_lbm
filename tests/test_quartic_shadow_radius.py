from __future__ import annotations

import json

import pytest

from ttim_lbm.quartic_shadow_radius import run_quartic_shadow_radius_audit


@pytest.fixture(scope="module")
def quartic_shadow_radius():
    return run_quartic_shadow_radius_audit()


def _cell(campaign, amplitude: float, horizon: int):
    amplitude_record = next(
        record
        for record in campaign["amplitude_records"]
        if record["amplitude"] == amplitude
    )
    return next(
        record
        for record in amplitude_record["prefix_summaries"]
        if record["horizon"] == horizon
    )


def test_q007c2_reproduces_coefficients_and_failed_q007c1_witness(
    quartic_shadow_radius,
) -> None:
    control = quartic_shadow_radius["q007c1_control_reproduction"]

    assert control["coefficient_hashes"]["match"]
    assert control["maximum_relative_error"] <= 1.0e-10
    assert control["observed_ratios"] == {
        "maximum_absolute_error_ratio": pytest.approx(0.7464493651463932),
        "final_absolute_error_ratio": pytest.approx(1.3715310087581642),
        "maximum_perturbation_relative_error_ratio": pytest.approx(
            0.8914189366016195
        ),
    }


def test_q007c2_passes_validity_and_campaign_structure(
    quartic_shadow_radius,
) -> None:
    campaign = quartic_shadow_radius["shadow_domain_campaign"]

    assert quartic_shadow_radius["study_validity"] == "passed"
    assert all(
        gate["passed"] for gate in quartic_shadow_radius["validity_gates"].values()
    )
    assert quartic_shadow_radius["direction_registration"]["duplicate_count"] == 0
    assert campaign["trajectory_count"] == 384
    assert campaign["chart_step_count"] == 38400
    assert campaign["amplitudes"] == [0.004, 0.007, 0.01]
    assert campaign["prefix_horizons"] == [10, 25, 50, 100]


def test_q007c2_localizes_both_registered_operating_points(
    quartic_shadow_radius,
) -> None:
    campaign = quartic_shadow_radius["shadow_domain_campaign"]
    short_large = _cell(campaign, 0.01, 10)
    long_small = _cell(campaign, 0.004, 100)

    assert all(
        ratio <= 0.8 for ratio in short_large["maximum_directional_ratios"].values()
    )
    assert all(
        count == 0 for count in short_large["ratio_failure_counts"].values()
    )
    assert all(
        ratio <= 0.8 for ratio in long_small["maximum_directional_ratios"].values()
    )
    assert all(
        count == 0 for count in long_small["ratio_failure_counts"].values()
    )
    assert quartic_shadow_radius["hypothesis_gates"][
        "radius_0p01_horizon_10_shadow_ratios"
    ]["passed"]
    assert quartic_shadow_radius["hypothesis_gates"][
        "radius_0p004_horizon_100_shadow_ratios"
    ]["passed"]


def test_q007c2_preserves_the_long_large_boundary_failure(
    quartic_shadow_radius,
) -> None:
    boundary = _cell(
        quartic_shadow_radius["shadow_domain_campaign"],
        0.01,
        100,
    )

    assert boundary["maximum_directional_ratios"][
        "final_absolute_error_ratio"
    ] > 0.8
    assert boundary["ratio_failure_counts"]["final_absolute_error_ratio"] == 2
    assert not quartic_shadow_radius["preserved_prior_outcomes"][
        "q007c1_radius_0p01_horizon_100_revised"
    ]


def test_q007c2_passes_budget_and_records_finite_sample_acceptance(
    quartic_shadow_radius,
) -> None:
    summary = quartic_shadow_radius["shadow_domain_campaign"]["summary"]

    assert summary["quartic_budget_component_check_count"] == 57600
    assert summary["quartic_budget_violation_count"] == 0
    assert summary["maximum_quartic_budget_utilization"] <= 1.0
    assert summary["maximum_final_component_budget"] <= 1.2e-11
    assert quartic_shadow_radius["hypothesis_outcome"] == "accepted"
    assert quartic_shadow_radius["scientific_classification"] == (
        "quartic shadowing domain localized on independent directions"
    )
    assert "64 registered directions" in quartic_shadow_radius["claim_boundary"]
    json.dumps(quartic_shadow_radius, allow_nan=False)
