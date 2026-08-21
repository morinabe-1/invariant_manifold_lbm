from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ht_degree34_seventy_fourth_component_safe_phase_discs as q011ht
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "39d6b40f3d368306a287e16f3cf8627bfcd0096cb671374c71d6b7425dbdc20b"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "c7f913d0b05cc8e83fdee2664b159f1d8b12b4d9c8d461c65d57a3e324c3c23b"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "6607a4c4525cbef32cbd01a15dffa9e9856eec55b2bfe76343e363b516e21965",
    "phase_input_digest_sha256": "d563bba9ff13e726e585036643481f874392d32bd003e53fe7ca26c524d9807a",
    "allocation_digest_sha256": "b69113c99eeee5ed5052323a3b0409782dad8f0821b4aeafc12bca2d0b941982",
    "phase_comparison_digest_sha256": "58bc9f2439a26fce593d6d1ada96698d2cd34bf24b317f1bc4a08f617780e47e",
    "result_digest_sha256": "21efa9db0ca031583de4ba0e2a2ea04605b3efe7eb98063b1aaed7421894d709",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "323f9a3950171c9b8e2aea5e2e6a44c2910f04e05508c5e82d9b75b348ae225d"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "57badc5d7675b78362958718cfc68036f87a34d11f88fe4cdd88c7c264932e3c"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_298
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 8, 0, 1, 0, 5, 1, 0, 2, 4]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc84e1p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 14_578,
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
def q011ht_structure() -> dict[str, Any]:
    sealed, artifacts = q011ht._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011ht._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011ht._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011ht_study() -> dict[str, Any]:
    return q011ht.run_q011ht_study()


@pytest.fixture(scope="module")
def q011ht_cycle(q011ht_study: dict[str, Any]) -> dict[str, Any]:
    return q011ht_study["cycle"]


def test_q011ht_seals_q011hs_and_all_prior_inputs(q011ht_structure: dict[str, Any]) -> None:
    sealed = q011ht_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 206
    assert sealed["direct_digest_count"] == 939
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hs"]["digests"]) == q011ht.Q011HS_DIGESTS
    assert sealed["q011hs"]["artifact_sha256"] == q011ht.Q011HS_ARTIFACT_SHA256
    assert sealed["q011hs"]["runner_sha256"] == q011ht.Q011HS_RUNNER_SHA256


def test_q011ht_reconstructs_component_safe_phase_discs(
    q011ht_structure: dict[str, Any],
) -> None:
    fixed = q011ht_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 73
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011ht.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011ht.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011ht.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011ht.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships and [148] in memberships and [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011hs_compatible_wave_allocation_count"] == 665
    assert fixed["q011hs_compatible_wave_allocation_digest_sha256"] == (
        q011ht.q011hs.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ht._protocol_globals_are_restored()


def test_q011ht_enumerates_registered_label_free_phase_inventory(
    q011ht_structure: dict[str, Any],
) -> None:
    allocation = q011ht_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == q011ht.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ht.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 0, 1, 5, 1]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 1, 0, 6]
    assert allocation["individual_wave_allocation_count"] == 665
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ht.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 665,
    }
    assert sum(
        record["individual_wave_allocation_count"]
        for record in allocation["individual_to_component_bridge_records"]
    ) == 665
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ht.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ht.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert sum(
        record["phase_allocation_count"] for record in allocation["wave_projection_records"]
    ) == 14_578
    assert q011ht_structure["compatible_count"] == 14_578
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_seventy_three_totals"] == [13, 9, 5, 1, 6]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ht result is not sealed")
def test_q011ht_classifies_all_complex_phase_product_discs(q011ht_cycle: dict[str, Any]) -> None:
    comparison = q011ht_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 14_578
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 14_578
    assert comparison["comparison_stream_count"] == 14_578
    assert comparison["comparison_stream_domain"] == "q011ht-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 14_578,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ht result is not sealed")
def test_q011ht_minimum_exact_phase_margin_is_fixed(q011ht_cycle: dict[str, Any]) -> None:
    witness = q011ht_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == EXPECTED_MINIMUM_MARGIN_HEX
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    margin = q011ht.q011z._fraction(witness["complex_separation_margin_lower"]["exact"])
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert margin > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ht result is not sealed")
def test_q011ht_records_scoped_outcome(q011ht_cycle: dict[str, Any]) -> None:
    assert q011ht_cycle["study_validity"] == "passed"
    assert q011ht_cycle["failed_validity_order"] == []
    assert q011ht_cycle["failed_diagnostic_order"] == []
    assert len(q011ht_cycle["validity_gates"]) == 7
    assert len(q011ht_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ht_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ht_cycle["diagnostic_gates"].values())
    assert q011ht_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = (
        q011ht.RESOLVED_CLASSIFICATION
        if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
        else q011ht.PERSISTENT_CLASSIFICATION
    )
    assert q011ht_cycle["diagnostic_classification"] == expected
    assert q011ht_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ht_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011hu" in q011ht_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ht result is not sealed")
def test_q011ht_preserves_scientific_boundary(q011ht_cycle: dict[str, Any]) -> None:
    theorem = q011ht_cycle["theorem_consequence"]
    resolved = EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
    assert theorem[
        "component_safe_complex_phase_discs_resolve_seventy_fourth_q011cb_witness"
    ] is resolved
    assert theorem[
        "seventy_fourth_q011cb_witness_persists_under_component_safe_phase_discs"
    ] is (not resolved)
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
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
    assert "flatten ordinal 73" in q011ht_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 72" in q011ht_cycle["claim_boundary"]
    assert "later 44726 Q011cb refined signatures" in q011ht_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ht_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ht result is not sealed")
def test_q011ht_cycle_has_strict_reproducible_digests(q011ht_cycle: dict[str, Any]) -> None:
    json.dumps(q011ht_cycle, allow_nan=False)
    assert {name: q011ht_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ht_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ht_cycle["result_digest_sha256"] == (
        q011ht.q011b._canonical_json_sha256(q011ht._result_digest_sections(q011ht_cycle))
    )
    assert q011ht._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ht result is not sealed")
def test_q011ht_study_metadata_and_optional_artifact_are_scoped(
    q011ht_study: dict[str, Any],
) -> None:
    assert q011ht_study["schema_version"] == 1
    assert q011ht_study["source"] == source_metadata()
    assert q011ht_study["study_gate"] == "passed"
    assert q011ht_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ht_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ht_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 73
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ht_study, allow_nan=False)

    runner_path = Path(q011ht.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ht_degree34_seventy_fourth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ht artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ht_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ht.q011b._canonical_json_sha256(q011ht._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
