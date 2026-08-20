from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ev_degree34_thirty_sixth_component_safe_phase_discs as q011ev
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d630e78b3ef8cd9ec3b6fb4261217264ee59a7227d171489cba41f550f7a9d98"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "1ed27ada0a8fc1a694e8a77a215718648a59841e5feb9fe53acbcc1f4e4808c1"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "ae9eba91d9ac1ec3362151b34ad11973f403343bfe163dc75268d13a38d91721",
    "phase_input_digest_sha256": "8019dc365ea4d22d9a6bb7c351267d7bad0bb92ef464e711e2b1e37041cb0a64",
    "allocation_digest_sha256": "2b03743bb7b66413fd5587c7fbf97e8aa036f81c59fc60a0ac95a33bd41cf42d",
    "phase_comparison_digest_sha256": "7783971e48f98494c00125fa2f8073b931c8fc326ee5664a3e615349125ed59b",
    "result_digest_sha256": "184d6770b9de124bbb524e8afe467982a4432fec9da135625dfeaae98fe449ee",
}
EXPECTED_STREAM_DIGEST = "3e013f42b3db82bb4a5af9bda219e236429af28ca36bb92a649072f3e86f6fb3"
EXPECTED_MINIMUM_WITNESS_DIGEST = "4d81a833f38342bf959039d0b9e3f85fd2fc2edae6f7fde6aa7fe9f8f46e3a71"
EXPECTED_MINIMUM_INDEX: int | None = 12_816
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 6, 0, 3, 0, 5, 3, 0, 2, 2]
EXPECTED_MINIMUM_MARGIN_HEX = "0x1.a8f10a6dc85dep-6"


@pytest.fixture(scope="module")
def q011ev_study() -> dict[str, Any]:
    return q011ev.run_q011ev_study()


@pytest.fixture(scope="module")
def q011ev_cycle(q011ev_study: dict[str, Any]) -> dict[str, Any]:
    return q011ev_study["cycle"]


def test_q011ev_seals_q011eu_and_all_prior_inputs(
    q011ev_cycle: dict[str, Any],
) -> None:
    sealed = q011ev_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 130
    assert sealed["direct_digest_count"] == 597
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011eu"]["digests"]) == q011ev.Q011EU_DIGESTS
    assert sealed["q011eu"]["artifact_sha256"] == q011ev.Q011EU_ARTIFACT_SHA256
    assert sealed["q011eu"]["runner_sha256"] == q011ev.Q011EU_RUNNER_SHA256


def test_q011ev_reconstructs_component_safe_phase_discs(
    q011ev_cycle: dict[str, Any],
) -> None:
    fixed = q011ev_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 35
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ev.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ev.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011ev.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011ev.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011eu_compatible_wave_allocation_count"] == 2_837
    assert fixed["q011eu_compatible_wave_allocation_digest_sha256"] == (
        q011ev.q011eu.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ev._protocol_globals_are_restored()


def test_q011ev_enumerates_registered_label_free_phase_inventory(
    q011ev_cycle: dict[str, Any],
) -> None:
    allocation = q011ev_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == (q011ev.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ev.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        1,
        2,
        4,
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
        3,
        0,
        4,
    ]
    assert allocation["individual_wave_allocation_count"] == 2_837
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ev.EXPECTED_BRIDGE_RECORD_DIGEST
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
        q011ev.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ev.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_thirty_five_totals"] == [13, 9, 5, 3, 4]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011ev_certifies_all_complex_phase_product_discs(
    q011ev_cycle: dict[str, Any],
) -> None:
    comparison = q011ev_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 35
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
    assert comparison["comparison_stream_domain"] == ("q011ev-component-safe-phase-comparisons-v1")
    if not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011ev comparison stream digest has not been sealed yet")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011ev_minimum_exact_phase_margin_is_fixed(
    q011ev_cycle: dict[str, Any],
) -> None:
    comparison = q011ev_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    if EXPECTED_MINIMUM_INDEX is None or EXPECTED_MINIMUM_COUNTS is None:
        pytest.skip("Q011ev minimum phase witness has not been sealed yet")
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011ev.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ev_records_scoped_resolution(q011ev_cycle: dict[str, Any]) -> None:
    assert q011ev_cycle["study_validity"] == "passed"
    assert q011ev_cycle["failed_validity_order"] == []
    assert q011ev_cycle["failed_diagnostic_order"] == []
    assert len(q011ev_cycle["validity_gates"]) == 7
    assert len(q011ev_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ev_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ev_cycle["diagnostic_gates"].values())
    assert q011ev_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ev_cycle["diagnostic_classification"] == q011ev.RESOLVED_CLASSIFICATION
    assert q011ev_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ev_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ew" in q011ev_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011ev_cycle["next_change"]


def test_q011ev_preserves_scientific_boundary(q011ev_cycle: dict[str, Any]) -> None:
    theorem = q011ev_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_thirty_sixth_q011cb_witness"]
    assert not theorem["thirty_sixth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011eu_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 35" in q011ev_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 34" in q011ev_cycle["claim_boundary"]
    assert "later 44764 Q011cb refined signatures" in q011ev_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ev_cycle["claim_boundary"]


def test_q011ev_cycle_has_strict_reproducible_digests(
    q011ev_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ev_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ev section digests have not been sealed yet")
    assert {name: q011ev_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ev_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ev_cycle["result_digest_sha256"] == (
        q011ev.q011b._canonical_json_sha256(q011ev._result_digest_sections(q011ev_cycle))
    )
    assert q011ev._protocol_globals_are_restored()


def test_q011ev_study_metadata_and_optional_artifact_are_scoped(
    q011ev_study: dict[str, Any],
) -> None:
    assert q011ev_study["schema_version"] == 1
    assert q011ev_study["source"] == source_metadata()
    assert q011ev_study["study_gate"] == "passed"
    assert q011ev_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011ev_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ev_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 35
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ev_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ev runner hash has not been sealed yet")
    runner_path = Path(q011ev.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ev_degree34_thirty_sixth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ev artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ev_study["refinement_outcome"]
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ev.q011b._canonical_json_sha256(q011ev._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
