from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dr_degree34_twenty_first_component_safe_phase_discs as q011dr
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a29bb77eb012638148faa0360b2e9df91e3315bd70d0fb83128ea6f6882db8fd"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "5160dd25976232ab4af2a0e9ce7229c0c474ff5ebb2dcee8076dc445302de185"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "e3c651f18b591552d32489e3bb21f6b3b2a855e9346d5c4ae6d07a9e01691a7d",
    "phase_input_digest_sha256": (
        "67c0c0aaa6f7aeee0438fb55a2c182cca25662c33317834b03c37dca113d1060"
    ),
    "allocation_digest_sha256": (
        "d3ac506286a2c389e72377c2f5a467d81c0446b0eac0c3ef1b66eb5f8aab4a23"
    ),
    "phase_comparison_digest_sha256": (
        "b49a954498c7be6818e127aa5389a47aa0b415f90bd9f6661329a3c64b59f8c3"
    ),
    "result_digest_sha256": "3f4299d39fd16a7ac59200bb133ade3a803bf96e76897c75c1745a41a9402a20",
}
EXPECTED_STREAM_DIGEST = "93e215f05a4608bb821a6500c79359b49801efc6038d55d276f493be6378fc53"
EXPECTED_MINIMUM_WITNESS_DIGEST = "8c8cf6e53c96a08c4f432a201d6736541e31ce7940c2070ae4edcd68d8b31342"


@pytest.fixture(scope="module")
def q011dr_study() -> dict[str, Any]:
    return q011dr.run_q011dr_study()


@pytest.fixture(scope="module")
def q011dr_cycle(q011dr_study: dict[str, Any]) -> dict[str, Any]:
    return q011dr_study["cycle"]


def test_q011dr_seals_q011dq_and_all_prior_inputs(
    q011dr_cycle: dict[str, Any],
) -> None:
    sealed = q011dr_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 100
    assert sealed["direct_digest_count"] == 462
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dq"]["digests"]) == q011dr.Q011DQ_DIGESTS
    assert sealed["q011dq"]["artifact_sha256"] == q011dr.Q011DQ_ARTIFACT_SHA256
    assert sealed["q011dq"]["runner_sha256"] == q011dr.Q011DQ_RUNNER_SHA256


def test_q011dr_reconstructs_component_safe_phase_discs(
    q011dr_cycle: dict[str, Any],
) -> None:
    fixed = q011dr_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 20
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011dr.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011dr.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011dr.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011dr.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011dq_compatible_wave_allocation_count"] == 2_266
    assert fixed["q011dq_compatible_wave_allocation_digest_sha256"] == (
        q011dr.q011dq.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011dr._protocol_globals_are_restored()


def test_q011dr_enumerates_registered_label_free_phase_inventory(
    q011dr_cycle: dict[str, Any],
) -> None:
    allocation = q011dr_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == (q011dr.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011dr.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [
        0,
        13,
        0,
        0,
        0,
        9,
        0,
        5,
        2,
        2,
        3,
        0,
    ]
    assert allocation["last_compatible_counts"] == [
        13,
        0,
        9,
        0,
        0,
        0,
        0,
        5,
        0,
        4,
        0,
        3,
    ]
    assert allocation["individual_wave_allocation_count"] == 2_266
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011dr.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 191,
        "2": 187,
        "3": 567,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_266
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011dr.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011dr.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 191,
        "18": 187,
        "24": 187,
        "28": 189,
        "30": 191,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 20_786
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_twenty_totals"] == [13, 9, 5, 4, 3]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011dr_certifies_all_complex_phase_product_discs(
    q011dr_cycle: dict[str, Any],
) -> None:
    comparison = q011dr_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 20
    assert comparison["compatible_phase_allocation_count"] == 20_786
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 20_786,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 20_786,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 20_786
    assert comparison["comparison_stream_domain"] == ("q011dr-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011dr_minimum_exact_phase_margin_is_fixed(
    q011dr_cycle: dict[str, Any],
) -> None:
    comparison = q011dr_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 12_725
    assert witness["counts"] == [11, 2, 0, 5, 0, 4, 0, 5, 4, 0, 2, 1]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc865cp-6")
    assert q011dr.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011dr_records_scoped_resolution(q011dr_cycle: dict[str, Any]) -> None:
    assert q011dr_cycle["study_validity"] == "passed"
    assert q011dr_cycle["failed_validity_order"] == []
    assert q011dr_cycle["failed_diagnostic_order"] == []
    assert len(q011dr_cycle["validity_gates"]) == 7
    assert len(q011dr_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011dr_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dr_cycle["diagnostic_gates"].values())
    assert q011dr_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011dr_cycle["diagnostic_classification"] == q011dr.RESOLVED_CLASSIFICATION
    assert q011dr_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dr_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ds" in q011dr_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011dr_cycle["next_change"]


def test_q011dr_preserves_scientific_boundary(q011dr_cycle: dict[str, Any]) -> None:
    theorem = q011dr_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_twenty_first_q011cb_witness"]
    assert not theorem["twenty_first_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011dq_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dp_ordinal_nineteen_phase_resolution_is_preserved"]
    assert theorem["q011do_ordinal_nineteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dn_ordinal_eighteen_phase_resolution_is_preserved"]
    assert theorem["q011dm_ordinal_eighteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dl_ordinal_seventeen_phase_resolution_is_preserved"]
    assert theorem["q011dk_ordinal_seventeen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dj_ordinal_sixteen_phase_resolution_is_preserved"]
    assert theorem["q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011df_ordinal_fourteen_phase_resolution_is_preserved"]
    assert theorem["q011de_ordinal_fourteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dd_ordinal_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011dc_ordinal_thirteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011db_ordinal_twelve_phase_resolution_is_preserved"]
    assert theorem["q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
    assert theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
    assert theorem["q011cr_ordinal_seven_phase_resolution_is_preserved"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 20" in q011dr_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 19" in q011dr_cycle["claim_boundary"]
    assert "later 44779 Q011cb refined signatures" in q011dr_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011dr_cycle["claim_boundary"]


def test_q011dr_cycle_has_strict_reproducible_digests(
    q011dr_cycle: dict[str, Any],
) -> None:
    json.dumps(q011dr_cycle, allow_nan=False)
    assert {name: q011dr_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011dr_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011dr_cycle["result_digest_sha256"] == (
        q011dr.q011b._canonical_json_sha256(q011dr._result_digest_sections(q011dr_cycle))
    )
    assert q011dr._protocol_globals_are_restored()


def test_q011dr_study_metadata_and_optional_artifact_are_scoped(
    q011dr_study: dict[str, Any],
) -> None:
    assert q011dr_study["schema_version"] == 1
    assert q011dr_study["source"] == source_metadata()
    assert q011dr_study["study_gate"] == "passed"
    assert q011dr_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011dr_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dr_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 20
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dr_study, allow_nan=False)

    runner_path = Path(q011dr.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dr_degree34_twenty_first_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dr artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dr.q011b._canonical_json_sha256(q011dr._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
