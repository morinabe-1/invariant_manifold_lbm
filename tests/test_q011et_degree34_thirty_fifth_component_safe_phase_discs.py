from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011et_degree34_thirty_fifth_component_safe_phase_discs as q011et
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "1f55ee1dbfd8d9e060e7d901aa69a5ac10942cbeb221434864fd180a398ff839"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "c24dd34c22fb8f12a8db8c3aa8c7b20b2f9997aaec2bd36dd828f54e2c4479de"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "f20cafbeb729bcaa4db92ed862ebce05850bb095dfc21d5b4563f853d6200767",
    "phase_input_digest_sha256": "09a826ad73b2a3918d5b54b49d0c24cc81c59845224f5ef8e3fd37aa1167d014",
    "allocation_digest_sha256": "715e92e6b496c3c48da1aad361f2068a28588052861c00dad6144f9d4ffc43f9",
    "phase_comparison_digest_sha256": "f6dae4b2b23abcb3d97d4808bf93b09a6e78b6f27f01901dce89c6fe1b83fd71",
    "result_digest_sha256": "7393abc0ff33dddf6157eee357705e459ef05701ab4372c2a89884ac4f700a27",
}
EXPECTED_STREAM_DIGEST = "6198f55391458b8f307e572f6a9764b743365b3d033caf5ace7c4b56098d9228"
EXPECTED_MINIMUM_WITNESS_DIGEST = "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"
EXPECTED_MINIMUM_INDEX: int | None = 11_706
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 7, 0, 2, 0, 5, 2, 0, 2, 3]
EXPECTED_MINIMUM_MARGIN_HEX = "0x1.a8f10a6dc8560p-6"


@pytest.fixture(scope="module")
def q011et_study() -> dict[str, Any]:
    return q011et.run_q011et_study()


@pytest.fixture(scope="module")
def q011et_cycle(q011et_study: dict[str, Any]) -> dict[str, Any]:
    return q011et_study["cycle"]


def test_q011et_seals_q011es_and_all_prior_inputs(
    q011et_cycle: dict[str, Any],
) -> None:
    sealed = q011et_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 128
    assert sealed["direct_digest_count"] == 588
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011es"]["digests"]) == q011et.Q011ES_DIGESTS
    assert sealed["q011es"]["artifact_sha256"] == q011et.Q011ES_ARTIFACT_SHA256
    assert sealed["q011es"]["runner_sha256"] == q011et.Q011ES_RUNNER_SHA256


def test_q011et_reconstructs_component_safe_phase_discs(
    q011et_cycle: dict[str, Any],
) -> None:
    fixed = q011et_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 34
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011et.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011et.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011et.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011et.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011es_compatible_wave_allocation_count"] == 2_553
    assert fixed["q011es_compatible_wave_allocation_digest_sha256"] == (
        q011et.q011es.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011et._protocol_globals_are_restored()


def test_q011et_enumerates_registered_label_free_phase_inventory(
    q011et_cycle: dict[str, Any],
) -> None:
    allocation = q011et_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == (q011et.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011et.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 2_553
    assert allocation["component_wave_projection_count"] == 852
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011et.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 173,
        "2": 169,
        "3": 169,
        "4": 170,
        "5": 171,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_553
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011et.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011et.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_thirty_four_totals"] == [13, 9, 5, 2, 5]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011et_certifies_all_complex_phase_product_discs(
    q011et_cycle: dict[str, Any],
) -> None:
    comparison = q011et_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 34
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
    assert comparison["comparison_stream_domain"] == ("q011et-component-safe-phase-comparisons-v1")
    if not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011et comparison stream digest has not been sealed yet")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011et_minimum_exact_phase_margin_is_fixed(
    q011et_cycle: dict[str, Any],
) -> None:
    comparison = q011et_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    if EXPECTED_MINIMUM_INDEX is None or EXPECTED_MINIMUM_COUNTS is None:
        pytest.skip("Q011et minimum phase witness has not been sealed yet")
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011et.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011et_records_scoped_resolution(q011et_cycle: dict[str, Any]) -> None:
    assert q011et_cycle["study_validity"] == "passed"
    assert q011et_cycle["failed_validity_order"] == []
    assert q011et_cycle["failed_diagnostic_order"] == []
    assert len(q011et_cycle["validity_gates"]) == 7
    assert len(q011et_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011et_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011et_cycle["diagnostic_gates"].values())
    assert q011et_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011et_cycle["diagnostic_classification"] == q011et.RESOLVED_CLASSIFICATION
    assert q011et_cycle["scientific_outcome"] == "not_evaluated"
    assert q011et_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011eu" in q011et_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011et_cycle["next_change"]


def test_q011et_preserves_scientific_boundary(q011et_cycle: dict[str, Any]) -> None:
    theorem = q011et_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_thirty_fifth_q011cb_witness"]
    assert not theorem["thirty_fifth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011es_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 34" in q011et_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 33" in q011et_cycle["claim_boundary"]
    assert "later 44765 Q011cb refined signatures" in q011et_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011et_cycle["claim_boundary"]


def test_q011et_cycle_has_strict_reproducible_digests(
    q011et_cycle: dict[str, Any],
) -> None:
    json.dumps(q011et_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011et section digests have not been sealed yet")
    assert {name: q011et_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011et_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011et_cycle["result_digest_sha256"] == (
        q011et.q011b._canonical_json_sha256(q011et._result_digest_sections(q011et_cycle))
    )
    assert q011et._protocol_globals_are_restored()


def test_q011et_study_metadata_and_optional_artifact_are_scoped(
    q011et_study: dict[str, Any],
) -> None:
    assert q011et_study["schema_version"] == 1
    assert q011et_study["source"] == source_metadata()
    assert q011et_study["study_gate"] == "passed"
    assert q011et_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011et_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011et_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 34
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011et_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011et runner hash has not been sealed yet")
    runner_path = Path(q011et.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011et_degree34_thirty_fifth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011et artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011et.q011b._canonical_json_sha256(q011et._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
