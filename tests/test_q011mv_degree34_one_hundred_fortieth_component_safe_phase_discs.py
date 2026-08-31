from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mv_degree34_one_hundred_fortieth_component_safe_phase_discs as q011mv
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "9c84020ef514647b899e1a90c9ae68f751f19fc9e497c0bd47bb1addf85d6cc3"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "37d1a3dba4d8f7990376e42b9448e582fa62ddb44c60135df4d84ecd9bace3d0"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "09fa09356a4cbbc494b29b12ee4ec19dfcd73a73749ad54a76c6da15f2d71c98",
    "phase_input_digest_sha256": (
        "e97cabacf47c7bf27a25d9101adf056cce641398709387bd8a7f13e7ee6c9b09"
    ),
    "allocation_digest_sha256": (
        "a9a54993eebce96f919a353676604a920ccb975b646e7b9c970ecbb6b91e1410"
    ),
    "phase_comparison_digest_sha256": (
        "7985084e9fa10284c9aabc70ca28d6af023225408e16905c1c96b6f3493e8263"
    ),
    "result_digest_sha256": "c2ea50d1f5676e422f195ad998e589484e4836f6af09747b2bffaa70f1cf1dcf",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "c3490cfb845c595976f5d844b6743f2a5ac8605b455f51e14135a933221b32d2"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "5230fd7936461e9a4b0c7c22bece80b21c02827e9ec05805b4ac2135b88fa34e"
)
EXPECTED_MINIMUM_INDEX: int | None = 10_076
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 7, 0, 2, 0, 5, 3, 0, 2, 2]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc866bp-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 37_940,
    "unresolved_product_disk_overlap": 0,
}
EXPECTED_REFINEMENT_OUTCOME: str | None = "component_safe_phase_resolved"
RESULT_EXPECTATIONS_FIXED = all(
    value is not None
    for value in (
        EXPECTED_RUNNER_SHA256,
        EXPECTED_ARTIFACT_SHA256,
        EXPECTED_SECTION_DIGESTS,
        EXPECTED_STREAM_DIGEST,
        EXPECTED_MINIMUM_WITNESS_DIGEST,
        EXPECTED_MINIMUM_INDEX,
        EXPECTED_MINIMUM_COUNTS,
        EXPECTED_MINIMUM_MARGIN_HEX,
        EXPECTED_CATEGORY_COUNTS,
        EXPECTED_REFINEMENT_OUTCOME,
    )
)


@pytest.fixture(scope="module")
def q011mv_structure() -> dict[str, Any]:
    sealed, artifacts = q011mv._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011mv._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011mv._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011mv_study() -> dict[str, Any]:
    return q011mv.run_q011mv_study()


@pytest.fixture(scope="module")
def q011mv_cycle(q011mv_study: dict[str, Any]) -> dict[str, Any]:
    return q011mv_study["cycle"]


def test_q011mv_seals_q011mu_and_all_prior_inputs(
    q011mv_structure: dict[str, Any],
) -> None:
    sealed = q011mv_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 338
    assert sealed["direct_digest_count"] == 1_533
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mu"]["digests"]) == q011mv.Q011MU_DIGESTS
    assert sealed["q011mu"]["artifact_sha256"] == q011mv.Q011MU_ARTIFACT_SHA256
    assert sealed["q011mu"]["runner_sha256"] == q011mv.Q011MU_RUNNER_SHA256


def test_q011mv_reconstructs_component_safe_phase_discs(
    q011mv_structure: dict[str, Any],
) -> None:
    fixed = q011mv_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 139
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011mv.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011mv.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011mv.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011mv.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011mu_compatible_wave_allocation_count"] == 4_136
    assert fixed["q011mu_compatible_wave_allocation_digest_sha256"] == (
        q011mv.q011mu.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011mv._protocol_globals_are_restored()


def test_q011mv_enumerates_registered_label_free_phase_inventory(
    q011mv_structure: dict[str, Any],
) -> None:
    allocation = q011mv_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 686_400
    assert allocation["full_allocation_digest_sha256"] == q011mv.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 37_940
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011mv.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011mv.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011mv.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 4_136
    assert allocation["component_wave_projection_count"] == 1_729
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011mv.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 354,
        "2": 343,
        "3": 1_032,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011mv.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_729
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011mv.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 354,
        "18": 343,
        "24": 341,
        "28": 344,
        "30": 347,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 37_940
    )
    assert q011mv_structure["compatible_count"] == 37_940
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_thirty_nine_active_totals"] == [1, 12, 9, 5, 3, 4]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mv result is not sealed")
def test_q011mv_classifies_all_complex_phase_product_discs(
    q011mv_cycle: dict[str, Any],
) -> None:
    comparison = q011mv_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 37_940
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 37_940
    assert comparison["comparison_stream_count"] == 37_940
    assert comparison["comparison_stream_domain"] == ("q011mv-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 37_940,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mv result is not sealed")
def test_q011mv_minimum_exact_phase_margin_is_fixed(
    q011mv_cycle: dict[str, Any],
) -> None:
    witness = q011mv_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mv result is not sealed")
def test_q011mv_applies_stopping_rule_and_preserves_boundary(
    q011mv_cycle: dict[str, Any],
) -> None:
    assert q011mv_cycle["study_validity"] == "passed"
    assert q011mv_cycle["failed_validity_order"] == []
    assert q011mv_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mv_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mv_cycle["diagnostic_gates"].values())
    assert q011mv_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mv_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mv_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011mv.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011mv.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mv_cycle["diagnostic_classification"] == expected
    theorem = q011mv_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_one_hundred_fortieth_q011cb_witness"],
        theorem["one_hundred_fortieth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011mu_ordinal_one_hundred_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mt_ordinal_one_hundred_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011mr_ordinal_one_hundred_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 139" in q011mv_cycle["claim_boundary"]
    assert "ordinals 0 through 138" in q011mv_cycle["claim_boundary"]
    assert "later 44660 Q011cb refined signatures" in q011mv_cycle["claim_boundary"]
    assert "Q011mw" in q011mv_cycle["next_change"]
    assert {name: q011mv_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mv_cycle["result_digest_sha256"] == (
        q011mv.q011b._canonical_json_sha256(q011mv._result_digest_sections(q011mv_cycle))
    )
    assert q011mv._protocol_globals_are_restored()
    json.dumps(q011mv_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mv result is not sealed")
def test_q011mv_study_metadata_and_optional_artifact_are_scoped(
    q011mv_study: dict[str, Any],
) -> None:
    assert q011mv_study["schema_version"] == 1
    assert q011mv_study["source"] == source_metadata()
    assert q011mv_study["study_gate"] == "passed"
    assert q011mv_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mv_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 37_940
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mv_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 139
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mv_study, allow_nan=False)

    runner_path = Path(q011mv.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mv_degree34_one_hundred_fortieth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mv artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mv_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mv.q011b._canonical_json_sha256(q011mv._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
