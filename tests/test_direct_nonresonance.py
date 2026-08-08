from __future__ import annotations

import json
from fractions import Fraction

import pytest

from ttim_lbm.direct_nonresonance import (
    EXPECTED_AGGREGATE_COUNT,
    EXPECTED_EXPANDED_PRODUCT_COUNT,
    MAXIMUM_LOG_TAIL_BOUND,
    MINIMUM_LOG_GAP,
    rational_log_point,
    run_direct_nonresonance_audit,
)


@pytest.fixture(scope="module")
def direct_nonresonance_audit():
    return run_direct_nonresonance_audit()


def test_q007i_rational_log_encloses_one_half_on_the_registered_grid() -> None:
    proof = rational_log_point(Fraction(1, 2))

    assert Fraction(-7, 10) < proof.interval.lower
    assert proof.interval.lower < proof.interval.upper < Fraction(-69, 100)
    assert proof.interval.width <= Fraction(2, 10**60)
    assert proof.tail_bound <= MAXIMUM_LOG_TAIL_BOUND


def test_q007i_certifies_every_registered_direct_product_degree(
    direct_nonresonance_audit,
) -> None:
    audit = direct_nonresonance_audit
    enumeration = audit["enumeration"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "registered direct external nonresonance through degree 89 certified"
    )
    assert len(audit["validity_gates"]) == 7
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())
    assert enumeration["degree_count"] == 88
    assert enumeration["aggregate_count"] == EXPECTED_AGGREGATE_COUNT
    assert enumeration["expanded_product_count"] == (
        EXPECTED_EXPANDED_PRODUCT_COUNT
    )
    assert enumeration["overlap_count"] == 0
    assert enumeration["global_minimum_log_gap"]["float"] >= float(
        MINIMUM_LOG_GAP
    )
    assert enumeration["global_minimum_gap_witness"]["degree"] == 51
    assert enumeration["global_minimum_gap_witness"]["counts"] == [1, 19, 27, 4]
    assert all(
        record["overlap_count"] == 0 and record["count_checks_passed"]
        for record in enumeration["degree_records"]
    )
    json.dumps(audit, allow_nan=False)


def test_q007i_reconstructs_every_registered_representative_disk(
    direct_nonresonance_audit,
) -> None:
    reconstruction = direct_nonresonance_audit["spectral_reconstruction"]
    logarithms = direct_nonresonance_audit["rational_logarithms"]

    assert reconstruction["representative_count"] == 72
    assert reconstruction["proof_digest_mismatch_count"] == 0
    assert reconstruction["selected_representative_count"] == 2
    assert reconstruction["selected_disk_count"] == 6
    assert reconstruction["selected_modulus_type_count"] == 4
    assert reconstruction["external_representative_disk_count"] == 643
    assert reconstruction["external_merged_log_interval_count"] > 0
    assert reconstruction[
        "minimum_acoustic_shear_classification_margin"
    ]["float"] >= 0.1
    assert logarithms["maximum_tail_bound"]["float"] <= float(
        MAXIMUM_LOG_TAIL_BOUND
    )


def test_q007i_applies_only_the_qualitative_local_theorem(
    direct_nonresonance_audit,
) -> None:
    audit = direct_nonresonance_audit
    theorem = audit["theorem_consequence"]

    assert theorem["theorem_applies"]
    assert theorem["existence_conclusion"]
    assert all(theorem["assumptions"].values())
    assert "local analytic invariant manifold" in theorem["conclusion"]
    assert "C^90" in theorem["uniqueness_conclusion"]
    assert not theorem["explicit_neighborhood_radius_available"]
    assert not theorem[
        "registered_quartic_chart_identified_with_the_theorem_manifold"
    ]
    assert not any(audit["preserved_prior_outcomes"].values())
    assert "no explicit neighborhood radius" in audit["claim_boundary"]
