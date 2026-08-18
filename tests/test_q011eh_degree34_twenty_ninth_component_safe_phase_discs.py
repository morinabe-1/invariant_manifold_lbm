from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011eh_degree34_twenty_ninth_component_safe_phase_discs as q011eh
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "3a56295bb198f3f84cdd748ee4b9118eccc24d84f820cc67b30e84fe737eb500"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "66b7526c34aaa489890647eebf8796057887c2e08b067bff9f1c3fcc57846b19"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "0dca6d9857709e464d9c234e7e39ed7b64a096d36699f1119dff9eeb11ef6236",
    "phase_input_digest_sha256": "f09386634f9925e15d5369f23e934996603d0906250b2feb45827340d5035195",
    "allocation_digest_sha256": "7e3b359318fb00fd68ac6c6b655bc1f9db794e522778118c4bcae2b985c9e4c3",
    "phase_comparison_digest_sha256": "b440b3de1af819c6ace569cbfeb6d4289c83a73c59088979732b2bcafab70d41",
    "result_digest_sha256": "cf91fa2904566316c198ac6c90d7d78393e24bf6f0b401d5c0e026845fc59fd4",
}
EXPECTED_STREAM_DIGEST = "23eebbbb522a0f8768fecca700505ea787c07e12cf58b9f2dc4996863dd9c8f3"
EXPECTED_MINIMUM_WITNESS_DIGEST = "8c8cf6e53c96a08c4f432a201d6736541e31ce7940c2070ae4edcd68d8b31342"
EXPECTED_MINIMUM_INDEX: int | None = 12_725
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 5, 0, 4, 0, 5, 4, 0, 2, 1]
EXPECTED_MINIMUM_MARGIN_HEX = "0x1.a8f10a6dc865cp-6"


@pytest.fixture(scope="module")
def q011eh_study() -> dict[str, Any]:
    return q011eh.run_q011eh_study()


@pytest.fixture(scope="module")
def q011eh_cycle(q011eh_study: dict[str, Any]) -> dict[str, Any]:
    return q011eh_study["cycle"]


def test_q011eh_seals_q011eg_and_all_prior_inputs(
    q011eh_cycle: dict[str, Any],
) -> None:
    sealed = q011eh_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 116
    assert sealed["direct_digest_count"] == 534
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011eg"]["digests"]) == q011eh.Q011EG_DIGESTS
    assert sealed["q011eg"]["artifact_sha256"] == q011eh.Q011EG_ARTIFACT_SHA256
    assert sealed["q011eg"]["runner_sha256"] == q011eh.Q011EG_RUNNER_SHA256


def test_q011eh_reconstructs_component_safe_phase_discs(
    q011eh_cycle: dict[str, Any],
) -> None:
    fixed = q011eh_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 28
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011eh.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011eh.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011eh.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011eh.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011eg_compatible_wave_allocation_count"] == 2_646
    assert fixed["q011eg_compatible_wave_allocation_digest_sha256"] == (
        q011eh.q011eg.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011eh._protocol_globals_are_restored()


def test_q011eh_enumerates_registered_label_free_phase_inventory(
    q011eh_cycle: dict[str, Any],
) -> None:
    allocation = q011eh_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == (q011eh.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011eh.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 2_646
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011eh.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 4
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 191,
        "2": 187,
        "3": 187,
        "4": 380,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_646
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011eh.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011eh.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_twenty_eight_totals"] == [13, 9, 5, 4, 3]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011eh_certifies_all_complex_phase_product_discs(
    q011eh_cycle: dict[str, Any],
) -> None:
    comparison = q011eh_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 28
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
    assert comparison["comparison_stream_domain"] == ("q011eh-component-safe-phase-comparisons-v1")
    if not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011eh comparison stream digest has not been sealed yet")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011eh_minimum_exact_phase_margin_is_fixed(
    q011eh_cycle: dict[str, Any],
) -> None:
    comparison = q011eh_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    if EXPECTED_MINIMUM_INDEX is None or EXPECTED_MINIMUM_COUNTS is None:
        pytest.skip("Q011eh minimum phase witness has not been sealed yet")
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011eh.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011eh_records_scoped_resolution(q011eh_cycle: dict[str, Any]) -> None:
    assert q011eh_cycle["study_validity"] == "passed"
    assert q011eh_cycle["failed_validity_order"] == []
    assert q011eh_cycle["failed_diagnostic_order"] == []
    assert len(q011eh_cycle["validity_gates"]) == 7
    assert len(q011eh_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011eh_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011eh_cycle["diagnostic_gates"].values())
    assert q011eh_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011eh_cycle["diagnostic_classification"] == q011eh.RESOLVED_CLASSIFICATION
    assert q011eh_cycle["scientific_outcome"] == "not_evaluated"
    assert q011eh_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ei" in q011eh_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011eh_cycle["next_change"]


def test_q011eh_preserves_scientific_boundary(q011eh_cycle: dict[str, Any]) -> None:
    theorem = q011eh_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_twenty_ninth_q011cb_witness"]
    assert not theorem["twenty_ninth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011eg_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 28" in q011eh_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 27" in q011eh_cycle["claim_boundary"]
    assert "later 44771 Q011cb refined signatures" in q011eh_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011eh_cycle["claim_boundary"]


def test_q011eh_cycle_has_strict_reproducible_digests(
    q011eh_cycle: dict[str, Any],
) -> None:
    json.dumps(q011eh_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011eh section digests have not been sealed yet")
    assert {name: q011eh_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011eh_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011eh_cycle["result_digest_sha256"] == (
        q011eh.q011b._canonical_json_sha256(q011eh._result_digest_sections(q011eh_cycle))
    )
    assert q011eh._protocol_globals_are_restored()


def test_q011eh_study_metadata_and_optional_artifact_are_scoped(
    q011eh_study: dict[str, Any],
) -> None:
    assert q011eh_study["schema_version"] == 1
    assert q011eh_study["source"] == source_metadata()
    assert q011eh_study["study_gate"] == "passed"
    assert q011eh_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011eh_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011eh_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 28
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011eh_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011eh runner hash has not been sealed yet")
    runner_path = Path(q011eh.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011eh_degree34_twenty_ninth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011eh artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011eh.q011b._canonical_json_sha256(q011eh._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
