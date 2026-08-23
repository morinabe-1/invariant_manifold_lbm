from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ih_degree34_eighty_first_component_safe_phase_discs as q011ih
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "9a1ce5375b199064670dc4726ae93697bddda65af7af3d2e4917c57a54ed9baf"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "79863cceef6d9ed7b22d3f818307b22818709f03a8f088cb034bb7508a7cbf84"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "48b5d6de85bc16a135b0d85384fad34416f96cdaf67bbe2ed734238901ccab2e",
    "phase_input_digest_sha256": (
        "521bb99ca05b15e8351dcf66b5a6db70d41913546e0ba001d5e90a12437773ca"
    ),
    "allocation_digest_sha256": (
        "49c9ed1e3baaf9602cc51d021349fbf4d44b333e5a1de8c36f37cc9800ee063f"
    ),
    "phase_comparison_digest_sha256": (
        "e82095c3b4fa33db5cefe7f7184f3d69607b7c5253d73ef7b2d6ef80ea780e64"
    ),
    "result_digest_sha256": (
        "3003424238da882e43012693d7211e48e5cdd03725f75d0dee18b32c473da5bf"
    ),
}
EXPECTED_STREAM_DIGEST: str | None = (
    "f4842dcdc5a0a98dcfa8ad79f1ef192fd224125947912eab17eaf9d3bfff6727"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "e56c1012985dec3148f724f74f3a19f365a0766d6fbddcce1448ea1d4cbaf8cf"
)
EXPECTED_MINIMUM_INDEX: int | None = 4_419
EXPECTED_MINIMUM_COUNTS: list[int] | None = [
    0,
    1,
    10,
    2,
    0,
    9,
    0,
    0,
    1,
    4,
    0,
    0,
    2,
    5,
]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8516p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 15_278,
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
def q011ih_structure() -> dict[str, Any]:
    sealed, artifacts = q011ih._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011ih._fixed_phase_input_audit(
        artifacts
    )
    allocation, compatible = q011ih._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011ih_study() -> dict[str, Any]:
    return q011ih.run_q011ih_study()


@pytest.fixture(scope="module")
def q011ih_cycle(q011ih_study: dict[str, Any]) -> dict[str, Any]:
    return q011ih_study["cycle"]


def test_q011ih_seals_q011ig_and_all_prior_inputs(
    q011ih_structure: dict[str, Any],
) -> None:
    sealed = q011ih_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 220
    assert sealed["direct_digest_count"] == 1_002
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ig"]["digests"]) == q011ih.Q011IG_DIGESTS
    assert sealed["q011ig"]["artifact_sha256"] == q011ih.Q011IG_ARTIFACT_SHA256
    assert sealed["q011ig"]["runner_sha256"] == q011ih.Q011IG_RUNNER_SHA256


def test_q011ih_reconstructs_component_safe_phase_discs(
    q011ih_structure: dict[str, Any],
) -> None:
    fixed = q011ih_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 80
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 14
    assert fixed["source_phase_disc_record_digest_sha256"] == (
        q011ih.EXPECTED_SOURCE_RECORD_DIGEST
    )
    assert fixed["target_phase_disc_record_digest_sha256"] == (
        q011ih.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert tuple(fixed["source_radius_binary64_hex"]) == (
        q011ih.EXPECTED_SOURCE_RADIUS_HEX
    )
    assert fixed["target_radius_binary64_hex"] == q011ih.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [144] in memberships and [145] in memberships
    assert [148] in memberships and [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ig_compatible_wave_allocation_count"] == 701
    assert fixed["q011ig_compatible_wave_allocation_digest_sha256"] == (
        q011ih.q011ig.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ih._protocol_globals_are_restored()


def test_q011ih_enumerates_registered_label_free_phase_inventory(
    q011ih_structure: dict[str, Any],
) -> None:
    allocation = q011ih_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 274_560
    assert allocation["full_allocation_digest_sha256"] == (
        q011ih.EXPECTED_FULL_ALLOCATION_DIGEST
    )
    assert allocation["compatible_allocation_count"] == 15_278
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ih.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [
        0,
        1,
        0,
        12,
        0,
        0,
        0,
        9,
        0,
        5,
        0,
        0,
        5,
        2,
    ]
    assert allocation["last_compatible_counts"] == [
        1,
        0,
        12,
        0,
        9,
        0,
        0,
        0,
        0,
        5,
        0,
        0,
        0,
        7,
    ]
    assert allocation["individual_wave_allocation_count"] == 701
    assert allocation["component_wave_projection_count"] == 701
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ih.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 701,
    }
    assert sum(
        record["individual_wave_allocation_count"]
        for record in allocation["individual_to_component_bridge_records"]
    ) == 701
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ih.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 701
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ih.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 147,
        "18": 142,
        "24": 139,
        "28": 137,
        "30": 136,
    }
    assert sum(
        record["phase_allocation_count"]
        for record in allocation["wave_projection_records"]
    ) == 15_278
    assert q011ih_structure["compatible_count"] == 15_278
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_eighty_totals"] == [1, 12, 9, 5, 0, 7]
    assert adapter["new_active_singleton_component_wave_identifiers"] == [
        "block=16;center=144",
        "block=1;center=144",
    ]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=144",
        "block=1;center=144",
        "block=16;center=145",
        "block=1;center=145",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ih result is not sealed")
def test_q011ih_classifies_all_complex_phase_product_discs(
    q011ih_cycle: dict[str, Any],
) -> None:
    comparison = q011ih_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 15_278
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 15_278
    assert comparison["comparison_stream_count"] == 15_278
    assert comparison["comparison_stream_domain"] == (
        "q011ih-component-safe-phase-comparisons-v1"
    )
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 15_278,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ih result is not sealed")
def test_q011ih_minimum_exact_phase_margin_is_fixed(
    q011ih_cycle: dict[str, Any],
) -> None:
    witness = q011ih_cycle["complex_phase_product_disc_audit"][
        "global_minimum_margin_witness"
    ]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    margin = q011ih.q011z._fraction(
        witness["complex_separation_margin_lower"]["exact"]
    )
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert margin > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ih result is not sealed")
def test_q011ih_records_scoped_outcome(q011ih_cycle: dict[str, Any]) -> None:
    assert q011ih_cycle["study_validity"] == "passed"
    assert q011ih_cycle["failed_validity_order"] == []
    assert q011ih_cycle["failed_diagnostic_order"] == []
    assert len(q011ih_cycle["validity_gates"]) == 7
    assert len(q011ih_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ih_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ih_cycle["diagnostic_gates"].values())
    assert q011ih_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = (
        q011ih.RESOLVED_CLASSIFICATION
        if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
        else q011ih.PERSISTENT_CLASSIFICATION
    )
    assert q011ih_cycle["diagnostic_classification"] == expected
    assert q011ih_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ih_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ii" in q011ih_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ih result is not sealed")
def test_q011ih_preserves_scientific_boundary(q011ih_cycle: dict[str, Any]) -> None:
    theorem = q011ih_cycle["theorem_consequence"]
    resolved = EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
    assert theorem[
        "component_safe_complex_phase_discs_resolve_eighty_first_q011cb_witness"
    ] is resolved
    assert theorem[
        "eighty_first_q011cb_witness_persists_under_component_safe_phase_discs"
    ] is (not resolved)
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011ig_ordinal_eighty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011if_ordinal_seventy_nine_phase_resolution_is_preserved"]
    assert theorem["q011ie_ordinal_seventy_nine_interval_inert_diagnostic_is_preserved"]
    assert all(
        value
        for name, value in theorem.items()
        if name.endswith("_is_preserved") and isinstance(value, bool)
    )
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 80" in q011ih_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 79" in q011ih_cycle["claim_boundary"]
    assert "later 44719 Q011cb refined signatures" in q011ih_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ih_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ih result is not sealed")
def test_q011ih_cycle_has_strict_reproducible_digests(
    q011ih_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ih_cycle, allow_nan=False)
    assert EXPECTED_SECTION_DIGESTS is not None
    assert {name: q011ih_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ih_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ih_cycle["result_digest_sha256"] == (
        q011ih.q011b._canonical_json_sha256(
            q011ih._result_digest_sections(q011ih_cycle)
        )
    )
    assert q011ih._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ih result is not sealed")
def test_q011ih_study_metadata_and_optional_artifact_are_scoped(
    q011ih_study: dict[str, Any],
) -> None:
    assert q011ih_study["schema_version"] == 1
    assert q011ih_study["source"] == source_metadata()
    assert q011ih_study["study_gate"] == "passed"
    assert q011ih_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ih_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 15_278
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ih_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 80
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ih_study, allow_nan=False)

    runner_path = Path(q011ih.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ih_degree34_eighty_first_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ih artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ih_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ih.q011b._canonical_json_sha256(
            q011ih._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
