from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011x_degree5_phase_disks as q011x
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011x_cycle() -> dict[str, Any]:
    return q011x.run_degree5_phase_disk_audit()


def test_q011x_seals_four_inputs_twenty_two_digests_and_helpers(
    q011x_cycle: dict[str, Any],
) -> None:
    audit = q011x_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 22
    assert {
        label: audit[label]["hypothesis_outcome"] for label in ("q011k", "q011u", "q011v", "q011w")
    } == {
        "q011k": "accepted",
        "q011u": "rejected",
        "q011v": "accepted",
        "q011w": "accepted",
    }
    assert audit["helper_sources"] == {
        "q011l": {
            "filename": "q011l_interval_homological_inverse.py",
            "sha256": q011x.q011w.Q011L_SOURCE_SHA256,
        },
        "q011o": {
            "filename": "q011o_graph_transform_setup.py",
            "sha256": q011x.q011w.Q011O_SOURCE_SHA256,
        },
    }
    assert audit["checks"]["q011k_eigendisc_scope_is_preserved"]
    assert audit["checks"]["q011u_c91_tail_and_valid_rejection_scope_is_preserved"]
    assert audit["checks"]["q011v_degree_three_certificate_is_preserved"]
    assert audit["checks"]["q011w_degree_four_certificate_and_boundary_are_preserved"]


def test_q011x_reproduces_the_complete_degree_five_modulus_inventory(
    q011x_cycle: dict[str, Any],
) -> None:
    audit = q011x_cycle["degree5_modulus_inventory_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree"] == 5
    assert audit["degree_modulus_aggregate_count"] == 56
    assert audit["degree_expanded_product_control_count"] == 252
    assert audit["modulus_separated_aggregate_count"] == 54
    assert audit["modulus_overlap_aggregate_count"] == 2
    assert [
        (
            record["selected_type_counts"],
            record["external_group_indices"],
        )
        for record in audit["overlap_records"]
    ] == [
        ([0, 3, 1, 1], [178]),
        ([0, 4, 1, 0], [177]),
    ]
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert [
        (record["external_group_index"], len(record["identifiers"]))
        for record in audit["external_target_groups"]
    ] == [(178, 4), (177, 8)]
    assert audit["eigencenter_reconstruction"]["eigencenter_count"] == 2598
    assert audit["eigencenter_reconstruction"]["selected_count"] == 24
    assert audit["eigencenter_reconstruction"]["external_count"] == 2574
    assert (
        audit["eigencenter_reconstruction"]["exact_modulus_interval_digest_sha256"]
        == "120d9214caa90d3eff168fca272ce8da3ee47eb5e11cbd65b0d462139b2d73fb"
    )
    assert len(audit["exact_inventory_digest_sha256"]) == 64


def test_q011x_combination_with_replacement_and_sector_filter_are_complete(
    q011x_cycle: dict[str, Any],
) -> None:
    audit = q011x_cycle["fourier_output_sector_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["structural_proof"].values())
    assert audit["output_sector_law"] == ("b_out=(b_1+b_2+b_3+b_4+b_5) mod 17")
    assert audit["indexed_monomial_count"] == 780
    assert audit["aggregate_monomial_counts"] == [640, 140]
    assert audit["aggregate_sector_histograms"] == [
        {
            "0": 96,
            "1": 92,
            "2": 80,
            "3": 60,
            "4": 32,
            "5": 8,
            "12": 8,
            "13": 32,
            "14": 60,
            "15": 80,
            "16": 92,
        },
        {
            "0": 18,
            "1": 17,
            "2": 16,
            "3": 13,
            "4": 10,
            "5": 5,
            "12": 5,
            "13": 10,
            "14": 13,
            "15": 16,
            "16": 17,
        },
    ]
    assert audit["external_target_counts"] == [4, 8]
    assert audit["external_target_sector_histograms"] == [
        {"2": 2, "15": 2},
        {"0": 4, "3": 2, "14": 2},
    ]
    assert audit["aggregate_compatible_comparison_counts"] == [320, 124]
    assert audit["sector_compatible_comparison_count"] == 444
    assert len(audit["monomial_records"]) == 780
    assert len(audit["compatible_pairs"]) == 444
    assert len(audit["exact_sector_record_digest_sha256"]) == 64


def test_q011x_framed_digests_cover_every_exact_product_and_comparison(
    q011x_cycle: dict[str, Any],
) -> None:
    audit = q011x_cycle["phase_sensitive_product_disk_audit"]
    framed = audit["framed_exact_record_digests"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 780
    assert audit["comparison_record_count"] == 444
    assert framed["exact_product_record_count"] == 780
    assert framed["exact_comparison_record_count"] == 444
    assert framed["exact_product_record_digest_sha256"] == (
        "c8bf3fa77eea40b0f2384a543cb56d6b2f1b1f714b72cee7d3fd664648f4967f"
    )
    assert framed["exact_comparison_record_digest_sha256"] == (
        "ae94f63d4b8ea7217e60c39c2aed7626436f0b136c7baabffba76bb1a410e62a"
    )
    assert "8-byte big-endian" in framed["algorithm"]
    assert len(audit["comparison_records"]) == 444


def test_q011x_indexed_modulus_and_phase_resolve_both_aggregates(
    q011x_cycle: dict[str, Any],
) -> None:
    audit = q011x_cycle["phase_sensitive_product_disk_audit"]

    assert audit["individual_modulus_separation_count"] == 372
    assert audit["complex_phase_separation_count"] == 72
    assert audit["unresolved_product_disk_overlap_count"] == 0
    assert audit["first_unresolved_product_disk_overlap"] is None
    assert audit["aggregate_category_counts"] == [
        {
            "aggregate_index": 0,
            "selected_type_counts": [0, 3, 1, 1],
            "external_group_index": 178,
            "individual_modulus_separation_count": 320,
            "complex_phase_separation_count": 0,
            "unresolved_product_disk_overlap_count": 0,
        },
        {
            "aggregate_index": 1,
            "selected_type_counts": [0, 4, 1, 0],
            "external_group_index": 177,
            "individual_modulus_separation_count": 52,
            "complex_phase_separation_count": 72,
            "unresolved_product_disk_overlap_count": 0,
        },
    ]
    assert {record["classification"] for record in audit["comparison_records"]} == {
        "individual_modulus_separation",
        "complex_phase_separation",
    }


def test_q011x_minimum_separations_exceed_the_registered_margin(
    q011x_cycle: dict[str, Any],
) -> None:
    audit = q011x_cycle["phase_sensitive_product_disk_audit"]
    minimum = _fraction(audit["minimum_complex_separation_lower"])
    phase_minimum = _fraction(audit["minimum_phase_only_separation_lower"])
    witness = audit["minimum_margin_witness"]
    phase_witness = audit["minimum_phase_witness"]

    assert minimum >= Fraction(1, 10)
    assert 0.1992 < float(minimum) < 0.1993
    assert 0.5682 < float(phase_minimum) < 0.5683
    assert witness["selected_type_counts"] == [0, 3, 1, 1]
    assert witness["source_identifiers"] == [
        "block=16;center=150",
        "block=16;center=150",
        "block=16;center=150",
        "block=0;center=148",
        "block=1;center=149",
    ]
    assert witness["target_identifier"] == "block=15;center=148"
    assert witness["classification"] == "individual_modulus_separation"
    assert phase_witness["selected_type_counts"] == [0, 4, 1, 0]
    assert phase_witness["target_identifier"] == "block=0;center=130"
    assert phase_witness["classification"] == "complex_phase_separation"


def test_q011x_accepts_exactly_the_degree_five_nonresonance_claim(
    q011x_cycle: dict[str, Any],
) -> None:
    theorem = q011x_cycle["theorem_consequence"]

    assert q011x_cycle["study_validity"] == "passed"
    assert q011x_cycle["hypothesis_outcome"] == "accepted"
    assert q011x_cycle["scientific_classification"] == q011x.ACCEPTED_CLASSIFICATION
    assert len(q011x_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011x_cycle["validity_gates"].values())
    assert len(q011x_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011x_cycle["hypothesis_gates"].values())
    assert q011x_cycle["failed_hypothesis_order"] == []
    assert theorem["both_degree_five_modulus_overlaps_are_eliminated"]
    assert theorem["degree_five_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == [2, 3, 4, 5]
    assert theorem["missing_external_nonresonance_degrees"] == list(range(6, 91))
    assert theorem["degree_91_and_higher_modulus_tail_is_preserved"]
    assert not theorem["degrees_6_through_90_are_certified"]
    assert not theorem["an_actual_complex_resonance_is_established"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "no degree from 6 through 90" in q011x_cycle["claim_boundary"]
    assert "Q011y" in q011x_cycle["next_change"]


def test_q011x_cycle_has_reproducible_strict_json_digests(
    q011x_cycle: dict[str, Any],
) -> None:
    json.dumps(q011x_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("9d13fa470f4c0bd8efa13868af90c6931025d7f3007e600c66af05bd0037a7ed"),
        "inventory_digest_sha256": (
            "717c4eadbd0e5f160a87de8846968933b8c5fbe604d769f215b6dcc65dacc955"
        ),
        "sector_digest_sha256": (
            "d31b7ea3cfcd7eca9d936cded13a1dc316e64dc2fc088bda745ea927d15ce52c"
        ),
        "product_digest_sha256": (
            "add9d07725802c5fba84b68a207d5adc6f3f405a152a22f88059259f9a255222"
        ),
        "result_digest_sha256": (
            "608bb3a7aee34a833e7980dbd18f4a3e641426966352126833f298e282437b31"
        ),
    }
    assert {name: q011x_cycle[name] for name in expected} == expected
    assert q011x_cycle["result_digest_sha256"] == (
        q011x.q011v.q011b._canonical_json_sha256(q011x._result_digest_sections(q011x_cycle))
    )


def test_q011x_artifact_records_degree_five_nonresonance_if_generated() -> None:
    runner_path = Path(q011x.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011x_degree5_phase_disks.json"
    if not artifact_path.exists():
        pytest.skip("Q011x artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == ("q011x_degree5_phase_disks.py")
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["scientific_classification"] == q011x.ACCEPTED_CLASSIFICATION
    assert cycle["result_digest_sha256"] == (
        q011x.q011v.q011b._canonical_json_sha256(q011x._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
