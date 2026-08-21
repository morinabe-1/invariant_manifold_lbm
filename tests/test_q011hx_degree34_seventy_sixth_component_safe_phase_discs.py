from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hx_degree34_seventy_sixth_component_safe_phase_discs as q011hx
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "8f7ecd64a27de0806601c00604bc60d33992b38a986f065b826f2f50b7fc01a2"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "9136b63e1e2717ff54125450a8fa2b47f18f33666e3ae19838a760af19c071f5"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "9244fb36c4ccba1e39e0348f4914088f4c64c84a2c162459e74fe32acfd027c3",
    "phase_input_digest_sha256": "4471e673ddea55899b35753d04cf4fb0675a4792dca9ef18f0ebe862c84d2ffa",
    "allocation_digest_sha256": "d0e94d89e23b1c75888a0ad0412600b2a262415db0ba51f102343425da381ced",
    "phase_comparison_digest_sha256": "2e2072ab3ca42eb4a16e2e999408ed25b92661d507617aa9d0d5814d8592deeb",
    "result_digest_sha256": "9e9b73e6c4e045e57674ae3e1a23d8840a38b73f362ca71c658c5ab4f4c73891",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "cf9f3bee1f0a9a625b9e7254f1f4d657a23c6adf603b20534e4ec7d354f9bf7d"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "4d81a833f38342bf959039d0b9e3f85fd2fc2edae6f7fde6aa7fe9f8f46e3a71"
)
EXPECTED_MINIMUM_INDEX: int | None = 12_816
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 6, 0, 3, 0, 5, 3, 0, 2, 2]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc85dep-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 20_786,
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
def q011hx_structure() -> dict[str, Any]:
    sealed, artifacts = q011hx._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011hx._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011hx._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011hx_study() -> dict[str, Any]:
    return q011hx.run_q011hx_study()


@pytest.fixture(scope="module")
def q011hx_cycle(q011hx_study: dict[str, Any]) -> dict[str, Any]:
    return q011hx_study["cycle"]


def test_q011hx_seals_q011hw_and_all_prior_inputs(q011hx_structure: dict[str, Any]) -> None:
    sealed = q011hx_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 210
    assert sealed["direct_digest_count"] == 957
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hw"]["digests"]) == q011hx.Q011HW_DIGESTS
    assert sealed["q011hw"]["artifact_sha256"] == q011hx.Q011HW_ARTIFACT_SHA256
    assert sealed["q011hw"]["runner_sha256"] == q011hx.Q011HW_RUNNER_SHA256


def test_q011hx_reconstructs_component_safe_phase_discs(
    q011hx_structure: dict[str, Any],
) -> None:
    fixed = q011hx_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 75
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011hx.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011hx.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011hx.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011hx.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships and [148] in memberships and [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011hw_compatible_wave_allocation_count"] == 945
    assert fixed["q011hw_compatible_wave_allocation_digest_sha256"] == (
        q011hx.q011hw.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011hx._protocol_globals_are_restored()


def test_q011hx_enumerates_registered_label_free_phase_inventory(
    q011hx_structure: dict[str, Any],
) -> None:
    allocation = q011hx_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == q011hx.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011hx.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 1, 2, 4, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 3, 0, 4]
    assert allocation["individual_wave_allocation_count"] == 945
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011hx.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 945,
    }
    assert sum(
        record["individual_wave_allocation_count"]
        for record in allocation["individual_to_component_bridge_records"]
    ) == 945
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011hx.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011hx.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert sum(
        record["phase_allocation_count"] for record in allocation["wave_projection_records"]
    ) == 20_786
    assert q011hx_structure["compatible_count"] == 20_786
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_seventy_five_totals"] == [13, 9, 5, 3, 4]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hx result is not sealed")
def test_q011hx_classifies_all_complex_phase_product_discs(q011hx_cycle: dict[str, Any]) -> None:
    comparison = q011hx_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 20_786
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 20_786
    assert comparison["comparison_stream_count"] == 20_786
    assert comparison["comparison_stream_domain"] == "q011hx-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 20_786,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hx result is not sealed")
def test_q011hx_minimum_exact_phase_margin_is_fixed(q011hx_cycle: dict[str, Any]) -> None:
    witness = q011hx_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == EXPECTED_MINIMUM_MARGIN_HEX
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    margin = q011hx.q011z._fraction(witness["complex_separation_margin_lower"]["exact"])
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert margin > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hx result is not sealed")
def test_q011hx_records_scoped_outcome(q011hx_cycle: dict[str, Any]) -> None:
    assert q011hx_cycle["study_validity"] == "passed"
    assert q011hx_cycle["failed_validity_order"] == []
    assert q011hx_cycle["failed_diagnostic_order"] == []
    assert len(q011hx_cycle["validity_gates"]) == 7
    assert len(q011hx_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011hx_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hx_cycle["diagnostic_gates"].values())
    assert q011hx_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = (
        q011hx.RESOLVED_CLASSIFICATION
        if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
        else q011hx.PERSISTENT_CLASSIFICATION
    )
    assert q011hx_cycle["diagnostic_classification"] == expected
    assert q011hx_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hx_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011hy" in q011hx_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hx result is not sealed")
def test_q011hx_preserves_scientific_boundary(q011hx_cycle: dict[str, Any]) -> None:
    theorem = q011hx_cycle["theorem_consequence"]
    resolved = EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
    assert theorem[
        "component_safe_complex_phase_discs_resolve_seventy_sixth_q011cb_witness"
    ] is resolved
    assert theorem[
        "seventy_sixth_q011cb_witness_persists_under_component_safe_phase_discs"
    ] is (not resolved)
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011hw_ordinal_seventy_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hv_ordinal_seventy_four_phase_resolution_is_preserved"]
    assert theorem["q011hu_ordinal_seventy_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ht_ordinal_seventy_three_phase_resolution_is_preserved"]
    assert theorem["q011hs_ordinal_seventy_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hr_ordinal_seventy_two_phase_resolution_is_preserved"]
    assert theorem["q011hq_ordinal_seventy_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hp_ordinal_seventy_one_phase_resolution_is_preserved"]
    assert theorem["q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved"]
    assert all(
        value
        for name, value in theorem.items()
        if name.endswith("_is_preserved") and isinstance(value, bool)
    )
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 75" in q011hx_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 74" in q011hx_cycle["claim_boundary"]
    assert "later 44724 Q011cb refined signatures" in q011hx_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011hx_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hx result is not sealed")
def test_q011hx_cycle_has_strict_reproducible_digests(q011hx_cycle: dict[str, Any]) -> None:
    json.dumps(q011hx_cycle, allow_nan=False)
    assert {name: q011hx_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011hx_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011hx_cycle["result_digest_sha256"] == (
        q011hx.q011b._canonical_json_sha256(q011hx._result_digest_sections(q011hx_cycle))
    )
    assert q011hx._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hx result is not sealed")
def test_q011hx_study_metadata_and_optional_artifact_are_scoped(
    q011hx_study: dict[str, Any],
) -> None:
    assert q011hx_study["schema_version"] == 1
    assert q011hx_study["source"] == source_metadata()
    assert q011hx_study["study_gate"] == "passed"
    assert q011hx_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hx_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hx_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 75
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hx_study, allow_nan=False)

    runner_path = Path(q011hx.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hx_degree34_seventy_sixth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hx artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hx_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hx.q011b._canonical_json_sha256(q011hx._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
