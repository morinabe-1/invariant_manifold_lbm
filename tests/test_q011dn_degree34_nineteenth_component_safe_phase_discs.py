from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dn_degree34_nineteenth_component_safe_phase_discs as q011dn
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "096212f2695a94240876b8a04977fe3be9e2ea5e0532cf0f9703594400ae0f83"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "daea7090b318ec18411f4d78200403f499b618607b7d066ab296185e5fb0d804"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "76197a55b0d2c03ab7e78a255e2efe7823527cecc87dcb2aa0194aee9379b0b2",
    "phase_input_digest_sha256": (
        "2e4b80b2d07e30b315f04d1a96de0a596782e0edb308bceb964803a3bb7e8c33"
    ),
    "allocation_digest_sha256": (
        "ba9be103f630678d9a53768a753a65e82fa1e3feac3712793d7794790df4dd09"
    ),
    "phase_comparison_digest_sha256": (
        "65dd5afbdb831886cecb20c279d3073a7bbe606e6bdd3fb56b1b31cbcc4b4f85"
    ),
    "result_digest_sha256": "a0186870e494c3566f617fc0f513c4c212b73bfdb22d206ce542e54ef5d3f09e",
}
EXPECTED_STREAM_DIGEST = "5678faeb9731a58760663effee9eb925b6d900778d782d4b38a471d5b316d247"
EXPECTED_MINIMUM_WITNESS_DIGEST = "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"


@pytest.fixture(scope="module")
def q011dn_study() -> dict[str, Any]:
    return q011dn.run_q011dn_study()


@pytest.fixture(scope="module")
def q011dn_cycle(q011dn_study: dict[str, Any]) -> dict[str, Any]:
    return q011dn_study["cycle"]


def test_q011dn_seals_q011dm_and_all_prior_inputs(
    q011dn_cycle: dict[str, Any],
) -> None:
    sealed = q011dn_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 96
    assert sealed["direct_digest_count"] == 444
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dm"]["digests"]) == q011dn.Q011DM_DIGESTS
    assert sealed["q011dm"]["artifact_sha256"] == q011dn.Q011DM_ARTIFACT_SHA256
    assert sealed["q011dm"]["runner_sha256"] == q011dn.Q011DM_RUNNER_SHA256


def test_q011dn_reconstructs_component_safe_phase_discs(
    q011dn_cycle: dict[str, Any],
) -> None:
    fixed = q011dn_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 18
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011dn.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011dn.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011dn.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011dn.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011dm_compatible_wave_allocation_count"] == 2_041
    assert fixed["q011dm_compatible_wave_allocation_digest_sha256"] == (
        q011dn.q011dm.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011dn._protocol_globals_are_restored()


def test_q011dn_enumerates_registered_label_free_phase_inventory(
    q011dn_cycle: dict[str, Any],
) -> None:
    allocation = q011dn_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == (q011dn.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011dn.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        0,
        2,
        5,
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
        2,
        0,
        5,
    ]
    assert allocation["individual_wave_allocation_count"] == 2_041
    assert allocation["component_wave_projection_count"] == 852
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011dn.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 173,
        "2": 169,
        "3": 510,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_041
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011dn.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011dn.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 173,
        "18": 169,
        "24": 169,
        "28": 170,
        "30": 171,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 18_718
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_eighteen_totals"] == [13, 9, 5, 2, 5]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011dn_certifies_all_complex_phase_product_discs(
    q011dn_cycle: dict[str, Any],
) -> None:
    comparison = q011dn_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 18
    assert comparison["compatible_phase_allocation_count"] == 18_718
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 18_718,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 18_718,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 18_718
    assert comparison["comparison_stream_domain"] == ("q011dn-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011dn_minimum_exact_phase_margin_is_fixed(
    q011dn_cycle: dict[str, Any],
) -> None:
    comparison = q011dn_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 11_706
    assert witness["counts"] == [11, 2, 0, 7, 0, 2, 0, 5, 2, 0, 2, 3]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8560p-6")
    assert q011dn.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011dn_records_scoped_resolution(q011dn_cycle: dict[str, Any]) -> None:
    assert q011dn_cycle["study_validity"] == "passed"
    assert q011dn_cycle["failed_validity_order"] == []
    assert q011dn_cycle["failed_diagnostic_order"] == []
    assert len(q011dn_cycle["validity_gates"]) == 7
    assert len(q011dn_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011dn_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dn_cycle["diagnostic_gates"].values())
    assert q011dn_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011dn_cycle["diagnostic_classification"] == q011dn.RESOLVED_CLASSIFICATION
    assert q011dn_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dn_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011do" in q011dn_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011dn_cycle["next_change"]


def test_q011dn_preserves_scientific_boundary(q011dn_cycle: dict[str, Any]) -> None:
    theorem = q011dn_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_nineteenth_q011cb_witness"]
    assert not theorem["nineteenth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011dm_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 18" in q011dn_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 17" in q011dn_cycle["claim_boundary"]
    assert "later 44781 Q011cb refined signatures" in q011dn_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011dn_cycle["claim_boundary"]


def test_q011dn_cycle_has_strict_reproducible_digests(
    q011dn_cycle: dict[str, Any],
) -> None:
    json.dumps(q011dn_cycle, allow_nan=False)
    assert {name: q011dn_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011dn_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011dn_cycle["result_digest_sha256"] == (
        q011dn.q011b._canonical_json_sha256(q011dn._result_digest_sections(q011dn_cycle))
    )
    assert q011dn._protocol_globals_are_restored()


def test_q011dn_study_metadata_and_optional_artifact_are_scoped(
    q011dn_study: dict[str, Any],
) -> None:
    assert q011dn_study["schema_version"] == 1
    assert q011dn_study["source"] == source_metadata()
    assert q011dn_study["study_gate"] == "passed"
    assert q011dn_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011dn_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dn_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 18
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dn_study, allow_nan=False)

    runner_path = Path(q011dn.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dn_degree34_nineteenth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dn artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dn.q011b._canonical_json_sha256(q011dn._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
