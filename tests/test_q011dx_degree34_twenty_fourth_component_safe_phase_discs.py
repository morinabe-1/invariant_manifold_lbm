from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dx_degree34_twenty_fourth_component_safe_phase_discs as q011dx
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "04a36f805a941e0745bb533092af10af40312c25de121c4b14617140629f6d93"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "7059c5c2396425f6aa1236cc68e7c19b754396b6520f00bd660cff6b2f13b21b",
    "phase_input_digest_sha256": (
        "724c246c6956b228433bb4c56f305eeab73a1b01754a2261ce1d5a7f3431ee32"
    ),
    "allocation_digest_sha256": (
        "508ec92baa0939e37208a4d9646c16d6bf8440b957c58a0db2db113204a3c09e"
    ),
    "phase_comparison_digest_sha256": (
        "661f61faefbf3ce6e0f042c76fa6a91e99ae6b78f04c91cb603d3d5f5c481f4d"
    ),
    "result_digest_sha256": "f644c8349915bc27880c963fc75bfcdc337cb26d92b1924ae99b3fdc7277b2d2",
}
EXPECTED_STREAM_DIGEST = "0e9f8481632aef522fd2daa7097d11ee9164f8fb0778fa14015bf5d6514a3143"
EXPECTED_MINIMUM_WITNESS_DIGEST = "df9e0c42e0cdb8d82a309c61e2bf95d5d6369af757654dbbf5ad38e822695d1a"


@pytest.fixture(scope="module")
def q011dx_study() -> dict[str, Any]:
    return q011dx.run_q011dx_study()


@pytest.fixture(scope="module")
def q011dx_cycle(q011dx_study: dict[str, Any]) -> dict[str, Any]:
    return q011dx_study["cycle"]


def test_q011dx_seals_q011dw_and_all_prior_inputs(
    q011dx_cycle: dict[str, Any],
) -> None:
    sealed = q011dx_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 106
    assert sealed["direct_digest_count"] == 489
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dw"]["digests"]) == q011dx.Q011DW_DIGESTS
    assert sealed["q011dw"]["artifact_sha256"] == q011dx.Q011DW_ARTIFACT_SHA256
    assert sealed["q011dw"]["runner_sha256"] == q011dx.Q011DW_RUNNER_SHA256


def test_q011dx_reconstructs_component_safe_phase_discs(
    q011dx_cycle: dict[str, Any],
) -> None:
    fixed = q011dx_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 23
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011dx.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011dx.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011dx.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011dx.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011dw_compatible_wave_allocation_count"] == 911
    assert fixed["q011dw_compatible_wave_allocation_digest_sha256"] == (
        q011dx.q011dw.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011dx._protocol_globals_are_restored()


def test_q011dx_enumerates_registered_label_free_phase_inventory(
    q011dx_cycle: dict[str, Any],
) -> None:
    allocation = q011dx_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011dx.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011dx.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        5,
        2,
        0,
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
        7,
        0,
        0,
    ]
    assert allocation["individual_wave_allocation_count"] == 911
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011dx.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 77,
        "3": 226,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 911
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011dx.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011dx.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 79,
        "18": 77,
        "24": 76,
        "28": 75,
        "30": 75,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 8_350
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_twenty_three_totals"] == [13, 9, 5, 7, 0]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011dx_certifies_all_complex_phase_product_discs(
    q011dx_cycle: dict[str, Any],
) -> None:
    comparison = q011dx_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 23
    assert comparison["compatible_phase_allocation_count"] == 8_350
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 8_350,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 8_350,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 8_350
    assert comparison["comparison_stream_domain"] == ("q011dx-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011dx_minimum_exact_phase_margin_is_fixed(
    q011dx_cycle: dict[str, Any],
) -> None:
    comparison = q011dx_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 5_408
    assert witness["counts"] == [11, 2, 0, 6, 0, 3, 0, 5, 5, 2, 0, 0]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc89e6p-6")
    assert q011dx.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011dx_records_scoped_resolution(q011dx_cycle: dict[str, Any]) -> None:
    assert q011dx_cycle["study_validity"] == "passed"
    assert q011dx_cycle["failed_validity_order"] == []
    assert q011dx_cycle["failed_diagnostic_order"] == []
    assert len(q011dx_cycle["validity_gates"]) == 7
    assert len(q011dx_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011dx_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dx_cycle["diagnostic_gates"].values())
    assert q011dx_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011dx_cycle["diagnostic_classification"] == q011dx.RESOLVED_CLASSIFICATION
    assert q011dx_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dx_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011dy" in q011dx_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011dx_cycle["next_change"]


def test_q011dx_preserves_scientific_boundary(q011dx_cycle: dict[str, Any]) -> None:
    theorem = q011dx_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_twenty_fourth_q011cb_witness"]
    assert not theorem["twenty_fourth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011dw_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dv_ordinal_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dt_ordinal_twenty_one_phase_resolution_is_preserved"]
    assert theorem["q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dr_ordinal_twenty_phase_resolution_is_preserved"]
    assert theorem["q011dq_ordinal_twenty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dp_ordinal_nineteen_phase_resolution_is_preserved"]
    assert theorem["q011do_ordinal_nineteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dn_ordinal_eighteen_phase_resolution_is_preserved"]
    assert theorem["q011dm_ordinal_eighteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dl_ordinal_seventeen_phase_resolution_is_preserved"]
    assert theorem["q011dk_ordinal_seventeen_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 23" in q011dx_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 22" in q011dx_cycle["claim_boundary"]
    assert "later 44776 Q011cb refined signatures" in q011dx_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011dx_cycle["claim_boundary"]


def test_q011dx_cycle_has_strict_reproducible_digests(
    q011dx_cycle: dict[str, Any],
) -> None:
    json.dumps(q011dx_cycle, allow_nan=False)
    assert {name: q011dx_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011dx_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011dx_cycle["result_digest_sha256"] == (
        q011dx.q011b._canonical_json_sha256(q011dx._result_digest_sections(q011dx_cycle))
    )
    assert q011dx._protocol_globals_are_restored()


def test_q011dx_study_metadata_and_optional_artifact_are_scoped(
    q011dx_study: dict[str, Any],
) -> None:
    assert q011dx_study["schema_version"] == 1
    assert q011dx_study["source"] == source_metadata()
    assert q011dx_study["study_gate"] == "passed"
    assert q011dx_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011dx_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dx_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 23
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dx_study, allow_nan=False)

    runner_path = Path(q011dx.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dx_degree34_twenty_fourth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dx artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dx.q011b._canonical_json_sha256(q011dx._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
