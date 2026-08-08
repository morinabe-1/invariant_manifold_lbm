from __future__ import annotations

from fractions import Fraction

import pytest

import research.q007aa_initialization_interior as q007aa


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007aa_cycle() -> dict:
    return q007aa.run_initialization_interior_audit()


def test_q007aa_registered_interior_has_exact_preregistered_margins() -> None:
    assert q007aa.OUTER_BASE_RADIUS == Fraction(9, 10**19)
    assert q007aa.OUTER_NORMAL_RADIUS == Fraction(5, 10**12)
    assert q007aa.INITIAL_BASE_RADIUS == Fraction(89_998, 10**23)
    assert q007aa.INITIAL_NORMAL_RADIUS == Fraction(
        4_999_999_999,
        10**21,
    )
    assert q007aa.REGISTERED_BASE_INWARD_MARGIN == Fraction(2, 10**23)
    assert q007aa.REGISTERED_NORMAL_INWARD_MARGIN == Fraction(1, 10**21)


def test_q007aa_exact_encoding_and_graph_shift_arithmetic(
    q007aa_cycle: dict,
) -> None:
    bound = q007aa_cycle["initialization_bound"]
    raw = _fraction(bound["raw_encoding_wiener_upper"])
    repair = _fraction(bound["repair_physical_wiener_upper"])
    total = _fraction(bound["total_encoding_repair_wiener_upper"])
    raw_base = _fraction(bound["raw_base_coordinate_increment_upper"])
    repair_base = _fraction(
        bound["repair_base_coordinate_increment_upper"]
    )
    base = _fraction(bound["base_coordinate_increment_upper"])
    direct = _fraction(
        bound["direct_external_coordinate_increment_upper"]
    )
    graph = _fraction(
        bound["graph_shift_external_coordinate_increment_upper"]
    )
    normal = _fraction(bound["normal_coordinate_increment_upper"])

    assert total == raw + repair
    assert base == raw_base + repair_base
    assert normal == direct + graph
    assert graph > 0
    assert bound["chart_derivative_dominates_registered_value"]
    assert bound["exact_arithmetic_identities_passed"]


def test_q007aa_registered_inward_margins_are_strict(
    q007aa_cycle: dict,
) -> None:
    bound = q007aa_cycle["initialization_bound"]
    base = _fraction(bound["base_coordinate_increment_upper"])
    normal = _fraction(bound["normal_coordinate_increment_upper"])
    tight_base = _fraction(bound["tight_base_initialization_radius"])
    tight_normal = _fraction(bound["tight_normal_initialization_radius"])

    assert base < q007aa.REGISTERED_BASE_INWARD_MARGIN
    assert normal < q007aa.REGISTERED_NORMAL_INWARD_MARGIN
    assert tight_base == q007aa.OUTER_BASE_RADIUS - base
    assert tight_normal == q007aa.OUTER_NORMAL_RADIUS - normal
    assert q007aa.INITIAL_BASE_RADIUS < tight_base
    assert q007aa.INITIAL_NORMAL_RADIUS < tight_normal
    assert bound["base_inward_margin_utilization"]["float"] == pytest.approx(
        0.5652372594521056
    )
    assert bound["normal_inward_margin_utilization"][
        "float"
    ] == pytest.approx(0.596035575932445)


def test_q007aa_connects_initial_encoding_to_q007z_induction(
    q007aa_cycle: dict,
) -> None:
    assert q007aa_cycle["study_validity"] == "passed"
    assert q007aa_cycle["hypothesis_outcome"] == "accepted"
    assert q007aa_cycle["scientific_classification"] == (
        "registered exact-state interior survives MPFR-85 encoding and "
        "repair"
    )
    assert len(q007aa_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"] for gate in q007aa_cycle["validity_gates"].values()
    )
    assert len(q007aa_cycle["hypothesis_gates"]) == 6
    assert all(
        gate["passed"] for gate in q007aa_cycle["hypothesis_gates"].values()
    )
    assert all(q007aa_cycle["theorem_consequence"].values())
    assert q007aa_cycle["input_audit"]["artifacts"]["q007y"][
        "fresh_cycle_matches"
    ]
    assert q007aa_cycle["input_audit"]["artifacts"]["q007z"][
        "fresh_cycle_matches"
    ]
    assert "trajectory accuracy or shadowing time" in q007aa_cycle[
        "claim_boundary"
    ]
