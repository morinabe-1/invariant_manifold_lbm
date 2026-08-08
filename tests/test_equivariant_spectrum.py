from __future__ import annotations

import json

import pytest

from ttim_lbm.equivariant_spectrum import (
    EXPECTED_NONZERO_MEMBER_COUNT,
    EXPECTED_NONZERO_ORBIT_COUNT,
    EXPECTED_ORBIT_COUNT,
    _c4_orbits,
    _rotate_interval_matrix,
    rotate_wave,
    run_equivariant_rational_spectral_audit,
)
from ttim_lbm.rational_spectrum import (
    _wave_indices,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)


@pytest.fixture(scope="module")
def equivariant_spectral_audit():
    return run_equivariant_rational_spectral_audit()


def test_q007h1_partitions_the_grid_into_registered_c4_orbits() -> None:
    orbits = _c4_orbits()
    members = [wave for orbit in orbits for wave in orbit.members]

    assert len(orbits) == EXPECTED_ORBIT_COUNT
    assert sum(orbit.representative != (0, 0) for orbit in orbits) == (
        EXPECTED_NONZERO_ORBIT_COUNT
    )
    assert sum(
        len(orbit.members)
        for orbit in orbits
        if orbit.representative != (0, 0)
    ) == EXPECTED_NONZERO_MEMBER_COUNT
    assert sorted(members) == sorted(_wave_indices())
    assert all(orbit.representative == min(orbit.members) for orbit in orbits)
    assert all(
        rotate_wave(orbit.members[index])
        == orbit.members[(index + 1) % len(orbit.members)]
        for orbit in orbits
        for index in range(len(orbit.members))
    )


def test_q007h1_rational_symbols_are_entrywise_c4_covariant() -> None:
    trig = trigonometric_intervals(machin_pi_interval())
    collision = rational_collision_symbol()
    symbols = {
        wave: rational_fourier_symbol(wave, trig, collision)
        for wave in _wave_indices()
    }

    assert all(
        _rotate_interval_matrix(symbol) == symbols[rotate_wave(wave)]
        for wave, symbol in symbols.items()
    )


def test_q007h1_accepts_the_equivariant_linear_certificate(
    equivariant_spectral_audit,
) -> None:
    audit = equivariant_spectral_audit

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "registered symmetry-equivariant linear spectral split and "
        "degree-90 tail certified"
    )
    assert len(audit["validity_gates"]) == 10
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())
    assert audit["symbol_covariance"]["mismatch_entry_count"] == 0
    assert audit["symmetry"]["maximum_conjugate_endpoint_difference"]["float"] == 0.0
    assert audit["symmetry"]["maximum_quarter_turn_endpoint_difference"]["float"] == 0.0
    assert audit["orbit_transport"][
        "maximum_exact_transport_parameter_difference"
    ]["float"] == 0.0
    json.dumps(audit, allow_nan=False)


def test_q007h1_certifies_only_the_registered_linear_layer(
    equivariant_spectral_audit,
) -> None:
    audit = equivariant_spectral_audit
    eigen = audit["eigencertification"]
    bounds = audit["global_bounds"]

    assert eigen["nonzero_block_count"] == 288
    assert eigen["selected_count"] == 24
    assert eigen["excluded_count"] == 2574
    assert eigen["fixed_leaf_count"] == 2598
    assert eigen["maximum_inverse_defect_epsilon"]["float"] <= 1.0e-10
    assert eigen["maximum_bauer_fike_radius"]["float"] <= 1.0e-8
    assert bounds["selected_spectral_radius"]["float"] < 1.0
    assert bounds["excluded_minimum_modulus"]["float"] > 0.0
    assert bounds["normal_gap"]["float"] > 0.0
    assert bounds["tail_ratio"]["float"] < 1.0
    assert not any(audit["preserved_prior_outcomes"].values())
    assert "does not certify degrees 2--89" in audit["claim_boundary"]
