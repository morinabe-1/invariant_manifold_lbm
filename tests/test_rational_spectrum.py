from __future__ import annotations

import json
from fractions import Fraction

import numpy as np
import pytest

from ttim_lbm.d2q9 import collision_symbol
from ttim_lbm.rational_spectrum import (
    MAXIMUM_PI_TRIGONOMETRIC_WIDTH,
    MAXIMUM_SYMBOL_ENTRY_WIDTH,
    SELECTED_WAVES,
    machin_pi_interval,
    rational_collision_symbol,
    run_rational_spectral_audit,
    trigonometric_intervals,
)


@pytest.fixture(scope="module")
def rational_spectral_audit():
    return run_rational_spectral_audit()


def test_q007h_constructs_narrow_fraction_only_angle_intervals() -> None:
    pi_enclosure = machin_pi_interval()
    trig = trigonometric_intervals(pi_enclosure)

    assert Fraction(3) < pi_enclosure.lower < pi_enclosure.upper < Fraction(22, 7)
    assert pi_enclosure.width <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
    assert set(trig) == set(range(-8, 9))
    assert max(value.width for pair in trig.values() for value in pair) <= (
        MAXIMUM_PI_TRIGONOMETRIC_WIDTH
    )
    for index in range(1, 9):
        assert trig[-index][0] == -trig[index][0]
        assert trig[-index][1] == trig[index][1]


def test_q007h_exact_collision_reproduces_the_float_oracle() -> None:
    exact = rational_collision_symbol()
    observed = np.asarray(exact, dtype=np.float64)

    assert all(isinstance(value, Fraction) for row in exact for value in row)
    assert np.max(np.abs(observed - collision_symbol(1.5))) <= 3.0e-16


def test_q007h_records_the_registered_inconclusive_symmetry_result(
    rational_spectral_audit,
) -> None:
    audit = rational_spectral_audit
    gates = audit["validity_gates"]

    assert audit["study_validity"] == "failed"
    assert audit["hypothesis_outcome"] == "inconclusive"
    assert audit["scientific_classification"] == (
        "registered rational-interval audit invalid"
    )
    assert len(gates) == 8
    assert not gates["conjugate_and_c4_symmetry"]["passed"]
    assert all(
        gate["passed"]
        for name, gate in gates.items()
        if name != "conjugate_and_c4_symmetry"
    )
    assert gates["conjugate_and_c4_symmetry"]["value"] > 1.0e-12
    assert gates["conjugate_and_c4_symmetry"]["value"] < 1.0e-10
    assert all(
        gate["passed"] for gate in audit["hypothesis_gates"].values()
    )
    json.dumps(audit, allow_nan=False)


def test_q007h_certifies_every_block_before_the_symmetry_gate(
    rational_spectral_audit,
) -> None:
    audit = rational_spectral_audit
    intervals = audit["interval_construction"]
    eigen = audit["eigencertification"]
    bounds = audit["global_bounds"]

    assert eigen["nonzero_block_count"] == 288
    assert eigen["selected_wave_count"] == len(SELECTED_WAVES) == 8
    assert eigen["selected_count"] == 24
    assert eigen["excluded_count"] == 2574
    assert eigen["fixed_leaf_count"] == 2598
    assert eigen["all_inverse_defects_strictly_below_one"]
    assert eigen["maximum_inverse_defect_epsilon"]["float"] <= 1.0e-10
    assert eigen["maximum_bauer_fike_radius"]["float"] <= 1.0e-8
    assert eigen["minimum_selected_excluded_disc_group_gap"]["float"] >= 1.0e-6
    assert intervals["maximum_symbol_entry_rectangle_width"]["float"] <= float(
        MAXIMUM_SYMBOL_ENTRY_WIDTH
    )
    assert bounds["selected_spectral_radius"]["float"] < 1.0
    assert bounds["excluded_minimum_modulus"]["float"] > 0.0
    assert bounds["normal_gap"]["float"] > 0.0
    assert bounds["tail_ratio"]["float"] < 1.0
    assert "does not certify degrees 2--89" in audit["claim_boundary"]
