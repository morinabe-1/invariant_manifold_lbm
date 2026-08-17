from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dl_degree34_eighteenth_component_safe_phase_discs as q011dl
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "2017ab06177312ab93994aedc9717223cdca6714078368946d3980d38633f6ab"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "81c60b5911eb37289b82f9f2c41e908b2373f9e78b55d481d273657ef7f36b00",
    "phase_input_digest_sha256": (
        "601f59275b82a84f3eb4d140d48af331df108d5238ad367b366689d931cb2cdc"
    ),
    "allocation_digest_sha256": (
        "def02aac2ab84f9679d8068060f09292c8ca763ed4f5c695e0063e5dcf48d02b"
    ),
    "phase_comparison_digest_sha256": (
        "4453a226a2cefe84c3aa1a71d4f1dbbc619301be508dbf2f59f450b551f39b75"
    ),
    "result_digest_sha256": "51186e5204192fc7d338aa7c54662475bd5c3d0b352ebb61205bfa56e0dbb4aa",
}
EXPECTED_STREAM_DIGEST = "4c6873fc3dc507331739629bd49303199b552e37d5eb26d046f2d3794490e726"
EXPECTED_MINIMUM_WITNESS_DIGEST = "57badc5d7675b78362958718cfc68036f87a34d11f88fe4cdd88c7c264932e3c"


@pytest.fixture(scope="module")
def q011dl_study() -> dict[str, Any]:
    return q011dl.run_q011dl_study()


@pytest.fixture(scope="module")
def q011dl_cycle(q011dl_study: dict[str, Any]) -> dict[str, Any]:
    return q011dl_study["cycle"]


def test_q011dl_seals_q011dk_and_all_prior_inputs(
    q011dl_cycle: dict[str, Any],
) -> None:
    sealed = q011dl_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 94
    assert sealed["direct_digest_count"] == 435
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dk"]["digests"]) == q011dl.Q011DK_DIGESTS
    assert sealed["q011dk"]["artifact_sha256"] == q011dl.Q011DK_ARTIFACT_SHA256
    assert sealed["q011dk"]["runner_sha256"] == q011dl.Q011DK_RUNNER_SHA256


def test_q011dl_reconstructs_component_safe_phase_discs(
    q011dl_cycle: dict[str, Any],
) -> None:
    fixed = q011dl_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 17
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011dl.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011dl.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011dl.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011dl.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011dk_compatible_wave_allocation_count"] == 1_590
    assert fixed["q011dk_compatible_wave_allocation_digest_sha256"] == (
        q011dl.q011dk.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011dl._protocol_globals_are_restored()


def test_q011dl_enumerates_registered_label_free_phase_inventory(
    q011dl_cycle: dict[str, Any],
) -> None:
    allocation = q011dl_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == (q011dl.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011dl.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        1,
        5,
        1,
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
        1,
        0,
        6,
    ]
    assert allocation["individual_wave_allocation_count"] == 1_590
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011dl.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 136,
        "2": 133,
        "3": 396,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_590
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011dl.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011dl.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 136,
        "18": 133,
        "24": 132,
        "28": 132,
        "30": 132,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 14_578
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_seventeen_totals"] == [13, 9, 5, 1, 6]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011dl_certifies_all_complex_phase_product_discs(
    q011dl_cycle: dict[str, Any],
) -> None:
    comparison = q011dl_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 17
    assert comparison["compatible_phase_allocation_count"] == 14_578
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 14_578,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 14_578,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 14_578
    assert comparison["comparison_stream_domain"] == ("q011dl-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011dl_minimum_exact_phase_margin_is_fixed(
    q011dl_cycle: dict[str, Any],
) -> None:
    comparison = q011dl_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 9_298
    assert witness["counts"] == [11, 2, 0, 8, 0, 1, 0, 5, 1, 0, 2, 4]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc84e1p-6")
    assert q011dl.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011dl_records_scoped_resolution(q011dl_cycle: dict[str, Any]) -> None:
    assert q011dl_cycle["study_validity"] == "passed"
    assert q011dl_cycle["failed_validity_order"] == []
    assert q011dl_cycle["failed_diagnostic_order"] == []
    assert len(q011dl_cycle["validity_gates"]) == 7
    assert len(q011dl_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011dl_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dl_cycle["diagnostic_gates"].values())
    assert q011dl_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011dl_cycle["diagnostic_classification"] == q011dl.RESOLVED_CLASSIFICATION
    assert q011dl_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dl_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011dm" in q011dl_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011dl_cycle["next_change"]


def test_q011dl_preserves_scientific_boundary(q011dl_cycle: dict[str, Any]) -> None:
    theorem = q011dl_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_eighteenth_q011cb_witness"]
    assert not theorem["eighteenth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011dk_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 17" in q011dl_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 16" in q011dl_cycle["claim_boundary"]
    assert "later 44782 Q011cb refined signatures" in q011dl_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011dl_cycle["claim_boundary"]


def test_q011dl_cycle_has_strict_reproducible_digests(
    q011dl_cycle: dict[str, Any],
) -> None:
    json.dumps(q011dl_cycle, allow_nan=False)
    assert {name: q011dl_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011dl_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011dl_cycle["result_digest_sha256"] == (
        q011dl.q011b._canonical_json_sha256(q011dl._result_digest_sections(q011dl_cycle))
    )
    assert q011dl._protocol_globals_are_restored()


def test_q011dl_study_metadata_and_optional_artifact_are_scoped(
    q011dl_study: dict[str, Any],
) -> None:
    assert q011dl_study["schema_version"] == 1
    assert q011dl_study["source"] == source_metadata()
    assert q011dl_study["study_gate"] == "passed"
    assert q011dl_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011dl_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dl_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 17
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dl_study, allow_nan=False)

    runner_path = Path(q011dl.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dl_degree34_eighteenth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dl artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dl.q011b._canonical_json_sha256(q011dl._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
