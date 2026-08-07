from __future__ import annotations

import json

import pytest

from ttim_lbm.checkerboard_filter import filter_multiplier
from ttim_lbm.low_wave_tangency import (
    audit_tangency_condition,
    run_low_wave_tangency_audit,
)
from ttim_lbm.nonresonance import wave_vector_from_index


@pytest.fixture(scope="module")
def tangency_audit() -> dict[str, object]:
    return run_low_wave_tangency_audit()


def test_reference_condition_has_a_resolved_positive_diagonal_gap() -> None:
    condition = audit_tangency_condition(129, 1.2, 0.02)

    assert condition["wave_record_count"] == 4
    assert condition["median_signed_gap"] > 0.0
    assert condition["orbit_gap_absolute_spread"] < 5.0e-13
    assert condition["maximum_eigensystem_residual"] < 1.0e-11
    assert condition["maximum_eigenvalue_matching_relative_residual"] < 1.0e-11
    assert condition["maximum_scalar_gap_identity_absolute_error"] < 5.0e-13
    assert all(
        record["modes"]["shear"]["direct_transverse_fraction"] > 0.5
        for record in condition["wave_records"]
    )


def test_scalar_filter_multiplies_but_does_not_reorder_the_gap() -> None:
    size = 257
    omega = 1.5
    baseline = audit_tangency_condition(size, omega, 0.0)
    filtered = audit_tangency_condition(size, omega, 0.05)
    multiplier = filter_multiplier(
        *wave_vector_from_index((1, 1), size),
        0.05,
    )

    assert filtered["median_signed_gap"] == pytest.approx(
        multiplier * baseline["median_signed_gap"],
        abs=5.0e-13,
    )
    assert filtered["median_signed_gap"] > 0.0


def test_registered_relaxations_have_opposite_diagonal_ordering() -> None:
    negative = audit_tangency_condition(257, 1.0, 0.05)
    positive = audit_tangency_condition(257, 1.2, 0.05)

    assert negative["median_signed_gap"] < 0.0
    assert positive["median_signed_gap"] > 0.0


def test_sealed_campaign_confirms_the_registered_fourth_order_tangency(
    tangency_audit: dict[str, object],
) -> None:
    audit = tangency_audit

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "same-sector hydrodynamic fourth-order tangency confirmed"
    )
    assert len(audit["conditions"]) == 140
    assert len(audit["fits"]) == 20
    assert audit["summary"]["fit_pass_count"] == 20
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())


def test_all_registered_fits_have_the_expected_sign_and_scaling(
    tangency_audit: dict[str, object],
) -> None:
    fits = tangency_audit["fits"]

    assert all(fit["passed"] for fit in fits)
    assert all(
        -4.25 <= fit["metrics"]["median_absolute_gap"]["slope"] <= -3.75
        and -4.25
        <= fit["metrics"]["median_relative_absolute_gap"]["slope"]
        <= -3.75
        and fit["scaled_gap_plateau"]["relative_spread"] <= 0.10
        and fit["gates"]["registered_sign_pattern"]["passed"]
        for fit in fits
    )
    assert tangency_audit["summary"][
        "maximum_scaled_gap_relative_spread"
    ] == pytest.approx(0.001803560762627789, rel=1.0e-8)


def test_campaign_record_is_strict_json(
    tangency_audit: dict[str, object],
) -> None:
    rendered = json.dumps(tangency_audit, allow_nan=False)
    assert "same-sector hydrodynamic fourth-order tangency confirmed" in rendered
    assert "scalar_gap_identity_absolute_error" in rendered


@pytest.mark.parametrize(
    ("size", "omega", "eta"),
    [(17, 1.2, 0.02), (129, 1.1, 0.02), (129, 1.2, 0.015)],
)
def test_condition_audit_rejects_unregistered_parameters(
    size: int,
    omega: float,
    eta: float,
) -> None:
    with pytest.raises(ValueError, match="sealed Q006g"):
        audit_tangency_condition(size, omega, eta)
