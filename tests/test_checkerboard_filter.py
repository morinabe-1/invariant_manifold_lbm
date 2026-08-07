from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.checkerboard_filter import (
    audit_filter_condition,
    conservative_checkerboard_filter,
    filter_multiplier,
    filtered_fourier_symbol,
    run_checkerboard_filter_audit,
)
from ttim_lbm.coefficient_scaling import audit_scaling_condition
from ttim_lbm.d2q9 import (
    fourier_symbol,
    global_conserved_quantities,
    uniform_equilibrium,
)
from ttim_lbm.nonresonance import wave_vector_from_index


@pytest.fixture(scope="module")
def filter_audit() -> dict[str, object]:
    return run_checkerboard_filter_audit()


def test_physical_filter_matches_its_scalar_fourier_multiplier() -> None:
    size = 17
    eta = 0.03
    kx, ky = wave_vector_from_index((3, -5), size)
    y, x = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
    plane = np.exp(1j * (kx * x + ky * y))
    state = np.zeros((size, size, 9), dtype=np.complex128)
    state[..., 4] = plane

    filtered = conservative_checkerboard_filter(state, eta)

    assert filtered == pytest.approx(filter_multiplier(kx, ky, eta) * state)


def test_filter_preserves_conservation_constants_and_the_global_minimum() -> None:
    rng = np.random.default_rng(20260809)
    state = rng.uniform(0.01, 1.0, size=(7, 9, 9))
    equilibrium = uniform_equilibrium(7, 9, np.array([0.04, 0.01, -0.01]))

    for eta in (0.0, 0.01, 0.02, 0.03, 0.05):
        filtered = conservative_checkerboard_filter(state, eta)
        assert global_conserved_quantities(filtered) == pytest.approx(
            global_conserved_quantities(state),
            abs=1.0e-12,
        )
        assert conservative_checkerboard_filter(equilibrium, eta) == pytest.approx(
            equilibrium,
            abs=1.0e-15,
        )
        assert np.min(filtered) >= np.min(state) - 1.0e-15


def test_filtered_symbol_is_the_registered_scalar_multiple() -> None:
    kx, ky = 0.37, -1.13
    omega = 1.5
    eta = 0.02

    assert filtered_fourier_symbol(kx, ky, omega, eta) == pytest.approx(
        filter_multiplier(kx, ky, eta) * fourier_symbol(kx, ky, omega)
    )


def test_unfiltered_condition_reproduces_the_q006c_reference_oracle() -> None:
    filtered = audit_filter_condition(17, 1.2, 0.0)
    reference = audit_scaling_condition(17, 1.2)

    assert filtered["pair_count"] == reference["pair_count"] == 136
    assert filtered["target_pair_count"] == reference["target_pair_count"] == 16
    assert filtered["maximum_condition_number"] == pytest.approx(
        reference["maximum_condition_number"],
        rel=1.0e-12,
    )
    assert filtered["spectral"]["normal_dominance_gap"] == pytest.approx(
        -0.013096403424400549,
        abs=1.0e-14,
    )
    for target_class, summary in reference["orbit_summaries"].items():
        assert filtered["orbit_summaries"][target_class][
            "medians"
        ] == pytest.approx(summary["medians"], rel=1.0e-12)


def test_sealed_campaign_validly_rejects_every_registered_family(
    filter_audit: dict[str, object],
) -> None:
    audit = filter_audit

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "rejected"
    assert audit["scientific_classification"] == (
        "no viable registered filtered family"
    )
    assert audit["selected_family"] is None
    assert audit["summary"]["viable_family_count"] == 0
    assert len(audit["conditions"]) == 100
    assert len(audit["fits"]) == 40
    assert len(audit["families"]) == 20
    assert all(gate["passed"] for gate in audit["validity_gates"].values())


def test_normal_gap_is_the_only_failed_family_gate(
    filter_audit: dict[str, object],
) -> None:
    families = filter_audit["families"]

    assert all(family["coefficient_passed"] for family in families)
    for family in families:
        failed_spectral = {
            name
            for name, gate in family["spectral_gates"].items()
            if not gate["passed"]
        }
        assert failed_spectral == {"normal_dominance_gap"}
    assert sum(
        family["minimum_normal_dominance_gap"] > 0.0
        for family in families
    ) == 11
    assert max(
        family["minimum_normal_dominance_gap"] for family in families
    ) == pytest.approx(9.55714807293617e-09, rel=1.0e-8)


def test_filtered_bottleneck_moves_to_the_diagonal_low_wave_cluster(
    filter_audit: dict[str, object],
) -> None:
    conditions = sorted(
        (
            condition
            for condition in filter_audit["conditions"]
            if condition["eta"] == 0.02 and condition["omega"] == 1.2
        ),
        key=lambda condition: condition["grid_size"],
    )
    sizes = np.asarray([condition["grid_size"] for condition in conditions])
    gaps = np.asarray(
        [
            condition["spectral"]["normal_dominance_gap"]
            for condition in conditions
        ]
    )
    slope = np.polyfit(np.log(sizes), np.log(gaps), 1)[0]

    assert all(gap > 0.0 for gap in gaps)
    assert -4.2 < slope < -3.8
    assert all(
        sorted(
            abs(value)
            for value in condition["spectral"]["minimum_selected_wave_index"]
        )
        == [1, 1]
        and sorted(
            abs(value)
            for value in condition["spectral"]["maximum_excluded_wave_index"]
        )
        == [1, 1]
        for condition in conditions
    )


def test_campaign_record_is_strict_json(
    filter_audit: dict[str, object],
) -> None:
    rendered = json.dumps(filter_audit, allow_nan=False)
    assert "no viable registered filtered family" in rendered
    assert "maximum_checkerboard_anchor_error" in rendered


@pytest.mark.parametrize(
    ("size", "omega", "eta"),
    [(9, 1.2, 0.02), (17, 1.1, 0.02), (17, 1.2, 0.015)],
)
def test_condition_audit_rejects_unregistered_parameters(
    size: int,
    omega: float,
    eta: float,
) -> None:
    with pytest.raises(ValueError, match="sealed Q006f"):
        audit_filter_condition(size, omega, eta)
