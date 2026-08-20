from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ex_degree34_thirty_seventh_component_safe_phase_discs as q011ex
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "ad8230519a1038fb811dd960c47c962eb9a645e02553cf6e5f3717746c44564f"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "df0e896e0a94f294625ffa691a2ee348f2a227b8bd34e35476be13a987ae1b82"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "c5e36927392513a4b0b8213a8403f24f02b40eba7c4ef9f64a2d37714f7cefac",
    "phase_input_digest_sha256": "c3a83195eaf1244d972c8664ae39bddfc366503c4217f2bb4bc28441d1910e1f",
    "allocation_digest_sha256": "b01655ec0171593fc33fc485b34295bb9e93340d6eca0a3e1289fccb7c9af06c",
    "phase_comparison_digest_sha256": "1bd5709a7f8ff86bb612b4573202c67b6d28fea4025d44409c755fe38df54444",
    "result_digest_sha256": "9ae086e18f5d714bee3ef5b8d99973552d9a4d4d438d60bf48279276cf24c1a9",
}
EXPECTED_STREAM_DIGEST = "ffc5d8c1e1b1fe9f5f3c488b1098163a62124a86bb783b6ac37440be2b33358f"
EXPECTED_MINIMUM_WITNESS_DIGEST = "8c8cf6e53c96a08c4f432a201d6736541e31ce7940c2070ae4edcd68d8b31342"
EXPECTED_MINIMUM_INDEX: int | None = 12_725
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 5, 0, 4, 0, 5, 4, 0, 2, 1]
EXPECTED_MINIMUM_MARGIN_HEX = "0x1.a8f10a6dc865cp-6"


@pytest.fixture(scope="module")
def q011ex_study() -> dict[str, Any]:
    return q011ex.run_q011ex_study()


@pytest.fixture(scope="module")
def q011ex_cycle(q011ex_study: dict[str, Any]) -> dict[str, Any]:
    return q011ex_study["cycle"]


def test_q011ex_seals_q011ew_and_all_prior_inputs(
    q011ex_cycle: dict[str, Any],
) -> None:
    sealed = q011ex_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 132
    assert sealed["direct_digest_count"] == 606
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ew"]["digests"]) == q011ex.Q011EW_DIGESTS
    assert sealed["q011ew"]["artifact_sha256"] == q011ex.Q011EW_ARTIFACT_SHA256
    assert sealed["q011ew"]["runner_sha256"] == q011ex.Q011EW_RUNNER_SHA256


def test_q011ex_reconstructs_component_safe_phase_discs(
    q011ex_cycle: dict[str, Any],
) -> None:
    fixed = q011ex_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 36
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ex.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ex.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011ex.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011ex.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ew_compatible_wave_allocation_count"] == 2_837
    assert fixed["q011ew_compatible_wave_allocation_digest_sha256"] == (
        q011ex.q011ew.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ex._protocol_globals_are_restored()


def test_q011ex_enumerates_registered_label_free_phase_inventory(
    q011ex_cycle: dict[str, Any],
) -> None:
    allocation = q011ex_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == (q011ex.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ex.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 2_837
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ex.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 191,
        "2": 187,
        "3": 187,
        "4": 189,
        "5": 191,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_837
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ex.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ex.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_thirty_six_totals"] == [13, 9, 5, 4, 3]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011ex_certifies_all_complex_phase_product_discs(
    q011ex_cycle: dict[str, Any],
) -> None:
    comparison = q011ex_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 36
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
    assert comparison["comparison_stream_domain"] == ("q011ex-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011ex_minimum_exact_phase_margin_is_fixed(
    q011ex_cycle: dict[str, Any],
) -> None:
    comparison = q011ex_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011ex.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ex_records_scoped_resolution(q011ex_cycle: dict[str, Any]) -> None:
    assert q011ex_cycle["study_validity"] == "passed"
    assert q011ex_cycle["failed_validity_order"] == []
    assert q011ex_cycle["failed_diagnostic_order"] == []
    assert len(q011ex_cycle["validity_gates"]) == 7
    assert len(q011ex_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ex_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ex_cycle["diagnostic_gates"].values())
    assert q011ex_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ex_cycle["diagnostic_classification"] == q011ex.RESOLVED_CLASSIFICATION
    assert q011ex_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ex_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ey" in q011ex_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011ex_cycle["next_change"]


def test_q011ex_preserves_scientific_boundary(q011ex_cycle: dict[str, Any]) -> None:
    theorem = q011ex_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_thirty_seventh_q011cb_witness"]
    assert not theorem["thirty_seventh_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011ew_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ev_ordinal_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011et_ordinal_thirty_four_phase_resolution_is_preserved"]
    assert theorem["q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011er_ordinal_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ep_ordinal_thirty_two_phase_resolution_is_preserved"]
    assert theorem["q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011en_ordinal_thirty_one_phase_resolution_is_preserved"]
    assert theorem["q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011el_ordinal_thirty_phase_resolution_is_preserved"]
    assert theorem["q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ej_ordinal_twenty_nine_phase_resolution_is_preserved"]
    assert theorem["q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eh_ordinal_twenty_eight_phase_resolution_is_preserved"]
    assert theorem["q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ef_ordinal_twenty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ed_ordinal_twenty_six_phase_resolution_is_preserved"]
    assert theorem["q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eb_ordinal_twenty_five_phase_resolution_is_preserved"]
    assert theorem["q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dz_ordinal_twenty_four_phase_resolution_is_preserved"]
    assert theorem["q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert theorem["q011dw_ordinal_twenty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dv_ordinal_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dt_ordinal_twenty_one_phase_resolution_is_preserved"]
    assert theorem["q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dj_ordinal_sixteen_phase_resolution_is_preserved"]
    assert theorem["q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 36" in q011ex_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 35" in q011ex_cycle["claim_boundary"]
    assert "later 44763 Q011cb refined signatures" in q011ex_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ex_cycle["claim_boundary"]


def test_q011ex_cycle_has_strict_reproducible_digests(
    q011ex_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ex_cycle, allow_nan=False)
    assert {name: q011ex_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ex_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ex_cycle["result_digest_sha256"] == (
        q011ex.q011b._canonical_json_sha256(q011ex._result_digest_sections(q011ex_cycle))
    )
    assert q011ex._protocol_globals_are_restored()


def test_q011ex_study_metadata_and_optional_artifact_are_scoped(
    q011ex_study: dict[str, Any],
) -> None:
    assert q011ex_study["schema_version"] == 1
    assert q011ex_study["source"] == source_metadata()
    assert q011ex_study["study_gate"] == "passed"
    assert q011ex_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011ex_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ex_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 36
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ex_study, allow_nan=False)

    runner_path = Path(q011ex.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ex_degree34_thirty_seventh_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ex artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ex_study["refinement_outcome"]
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ex.q011b._canonical_json_sha256(q011ex._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
