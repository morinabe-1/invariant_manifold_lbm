from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011df_degree34_fifteenth_component_safe_phase_discs as q011df
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a197268699d2eab6bb5e0cc77f0d8cd43db30cdc31e1b115c10818906321509b"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "f7729394914efb5c94f2ddb0b19383f3c59fc0f99111647782918826330d1365"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "7d148dba55f0579f18f5a497f1c362c6f92e9361b153596bff811f13366b829c",
    "phase_input_digest_sha256": (
        "d1ce2186292a85d48b6b2892d2616ed23ed5f46474626785a5d16830e5ac1c83"
    ),
    "allocation_digest_sha256": (
        "e38218885f9b6ab6e50c8237606020aa8d78567c3d4809b6e119e36ff2c6146a"
    ),
    "phase_comparison_digest_sha256": (
        "b69f85a87b9c97778511e96528775ad188070b6a881f8b55bffc92fa44c17b92"
    ),
    "result_digest_sha256": "7d72070108c2225780c59ef2076f68344ba4e2e2ca134ece4cf19a8d91f6c41d",
}
EXPECTED_STREAM_DIGEST = "293d6e0e309cc6f0af82494af56890d7f78baf8c97f30f5ef1d7e08bc705b0f3"
EXPECTED_MINIMUM_WITNESS_DIGEST = "1b7f6cc19a74cdefa602f28a6251f0c9b874cdd0a3a9b6f7ee438ea4618fea8d"


@pytest.fixture(scope="module")
def q011df_study() -> dict[str, Any]:
    return q011df.run_q011df_study()


@pytest.fixture(scope="module")
def q011df_cycle(q011df_study: dict[str, Any]) -> dict[str, Any]:
    return q011df_study["cycle"]


def test_q011df_seals_q011de_and_all_prior_inputs(
    q011df_cycle: dict[str, Any],
) -> None:
    sealed = q011df_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 88
    assert sealed["direct_digest_count"] == 408
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011de"]["digests"]) == q011df.Q011DE_DIGESTS
    assert sealed["q011de"]["artifact_sha256"] == q011df.Q011DE_ARTIFACT_SHA256
    assert sealed["q011de"]["runner_sha256"] == q011df.Q011DE_RUNNER_SHA256


def test_q011df_reconstructs_component_safe_phase_discs(
    q011df_cycle: dict[str, Any],
) -> None:
    fixed = q011df_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 14
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011df.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011df.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011df.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011df.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011de_compatible_wave_allocation_count"] == 1_194
    assert fixed["q011de_compatible_wave_allocation_digest_sha256"] == (
        q011df.q011de.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011df._protocol_globals_are_restored()


def test_q011df_enumerates_registered_label_free_phase_inventory(
    q011df_cycle: dict[str, Any],
) -> None:
    allocation = q011df_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == (q011df.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011df.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        4,
        2,
        1,
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
        6,
        0,
        1,
    ]
    assert allocation["individual_wave_allocation_count"] == 1_194
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011df.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 136,
        "2": 529,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_194
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011df.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011df.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_fourteen_totals"] == [13, 9, 5, 6, 1]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011df_certifies_all_complex_phase_product_discs(
    q011df_cycle: dict[str, Any],
) -> None:
    comparison = q011df_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 14
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
    assert comparison["comparison_stream_domain"] == ("q011df-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011df_minimum_exact_phase_margin_is_fixed(
    q011df_cycle: dict[str, Any],
) -> None:
    comparison = q011df_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 9_166
    assert witness["counts"] == [11, 2, 0, 5, 0, 4, 0, 5, 5, 1, 1, 0]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8860p-6")
    assert q011df.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011df_records_scoped_resolution(q011df_cycle: dict[str, Any]) -> None:
    assert q011df_cycle["study_validity"] == "passed"
    assert q011df_cycle["failed_validity_order"] == []
    assert q011df_cycle["failed_diagnostic_order"] == []
    assert len(q011df_cycle["validity_gates"]) == 7
    assert len(q011df_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011df_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011df_cycle["diagnostic_gates"].values())
    assert q011df_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011df_cycle["diagnostic_classification"] == q011df.RESOLVED_CLASSIFICATION
    assert q011df_cycle["scientific_outcome"] == "not_evaluated"
    assert q011df_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011dg" in q011df_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011df_cycle["next_change"]


def test_q011df_preserves_scientific_boundary(q011df_cycle: dict[str, Any]) -> None:
    theorem = q011df_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_fifteenth_q011cb_witness"]
    assert not theorem["fifteenth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011de_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 14" in q011df_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 13" in q011df_cycle["claim_boundary"]
    assert "later 44785 Q011cb refined signatures" in q011df_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011df_cycle["claim_boundary"]


def test_q011df_cycle_has_strict_reproducible_digests(
    q011df_cycle: dict[str, Any],
) -> None:
    json.dumps(q011df_cycle, allow_nan=False)
    assert {name: q011df_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011df_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011df_cycle["result_digest_sha256"] == (
        q011df.q011b._canonical_json_sha256(q011df._result_digest_sections(q011df_cycle))
    )
    assert q011df._protocol_globals_are_restored()


def test_q011df_study_metadata_and_optional_artifact_are_scoped(
    q011df_study: dict[str, Any],
) -> None:
    assert q011df_study["schema_version"] == 1
    assert q011df_study["source"] == source_metadata()
    assert q011df_study["study_gate"] == "passed"
    assert q011df_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011df_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011df_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 14
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011df_study, allow_nan=False)

    runner_path = Path(q011df.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011df_degree34_fifteenth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011df artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011df.q011b._canonical_json_sha256(q011df._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
