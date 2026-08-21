from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hp_degree34_seventy_second_component_safe_phase_discs as q011hp
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "59fba8b39084e7fe021306ee7322d7019f58d580a22c11f2865851db3cd90cfa"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "0c5c3936897cb8566d1429e98048f190162f1b3bfdd4ff8a0a17174874dd1417"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "482d5e5a53fa2ecf0ba1e010874654f5f22945f2e6a6ce14773b05cfbaeef162",
    "phase_input_digest_sha256": "387dc4ee2d1d408d20acf8a64a603c1a7e3c5ca9df9e2341dab0026e43e64b92",
    "allocation_digest_sha256": "7ee65520beac32020ac1415831485706bdefaa00b7b8ae0ed1f12ff4ec4b5059",
    "phase_comparison_digest_sha256": "dd0c205f5084fae760be324ed0f08aed1b21f7a2f28e93ddbb5359edf03ca547",
    "result_digest_sha256": "ef4c8f0c832b6d8aa4c830d6a7d2fa8e0f8bb49da51a821471ea90dd9199f2d4",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "bcb4bb7dea439b8ccbeca642c38dbc5539cc97341e9a6cb557cce666707a794e"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "df9e0c42e0cdb8d82a309c61e2bf95d5d6369af757654dbbf5ad38e822695d1a"
)
EXPECTED_MINIMUM_INDEX: int | None = 5_408
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 6, 0, 3, 0, 5, 5, 2, 0, 0]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc89e6p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 8_350,
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
def q011hp_structure() -> dict[str, Any]:
    sealed, artifacts = q011hp._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011hp._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011hp._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011hp_study() -> dict[str, Any]:
    return q011hp.run_q011hp_study()


@pytest.fixture(scope="module")
def q011hp_cycle(q011hp_study: dict[str, Any]) -> dict[str, Any]:
    return q011hp_study["cycle"]


def test_q011hp_seals_q011ho_and_all_prior_inputs(q011hp_structure: dict[str, Any]) -> None:
    sealed = q011hp_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 202
    assert sealed["direct_digest_count"] == 921
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ho"]["digests"]) == q011hp.Q011HO_DIGESTS
    assert sealed["q011ho"]["artifact_sha256"] == q011hp.Q011HO_ARTIFACT_SHA256
    assert sealed["q011ho"]["runner_sha256"] == q011hp.Q011HO_RUNNER_SHA256


def test_q011hp_reconstructs_component_safe_phase_discs(
    q011hp_structure: dict[str, Any],
) -> None:
    fixed = q011hp_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 71
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011hp.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011hp.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011hp.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011hp.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships and [148] in memberships and [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ho_compatible_wave_allocation_count"] == 685
    assert fixed["q011ho_compatible_wave_allocation_digest_sha256"] == (
        q011hp.q011ho.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011hp._protocol_globals_are_restored()


def test_q011hp_enumerates_registered_label_free_phase_inventory(
    q011hp_structure: dict[str, Any],
) -> None:
    allocation = q011hp_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == q011hp.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011hp.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 5, 2, 0, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 7, 0, 0]
    assert allocation["individual_wave_allocation_count"] == 685
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011hp.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 303,
    }
    assert sum(
        record["individual_wave_allocation_count"]
        for record in allocation["individual_to_component_bridge_records"]
    ) == 685
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011hp.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011hp.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert sum(
        record["phase_allocation_count"] for record in allocation["wave_projection_records"]
    ) == 8_350
    assert q011hp_structure["compatible_count"] == 8_350
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_seventy_one_totals"] == [13, 9, 5, 7, 0]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hp result is not sealed")
def test_q011hp_classifies_all_complex_phase_product_discs(q011hp_cycle: dict[str, Any]) -> None:
    comparison = q011hp_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 8_350
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 8_350
    assert comparison["comparison_stream_count"] == 8_350
    assert comparison["comparison_stream_domain"] == "q011hp-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 8_350,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hp result is not sealed")
def test_q011hp_minimum_exact_phase_margin_is_fixed(q011hp_cycle: dict[str, Any]) -> None:
    witness = q011hp_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == EXPECTED_MINIMUM_MARGIN_HEX
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    margin = q011hp.q011z._fraction(witness["complex_separation_margin_lower"]["exact"])
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert margin > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hp result is not sealed")
def test_q011hp_records_scoped_outcome(q011hp_cycle: dict[str, Any]) -> None:
    assert q011hp_cycle["study_validity"] == "passed"
    assert q011hp_cycle["failed_validity_order"] == []
    assert q011hp_cycle["failed_diagnostic_order"] == []
    assert len(q011hp_cycle["validity_gates"]) == 7
    assert len(q011hp_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011hp_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hp_cycle["diagnostic_gates"].values())
    assert q011hp_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = (
        q011hp.RESOLVED_CLASSIFICATION
        if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
        else q011hp.PERSISTENT_CLASSIFICATION
    )
    assert q011hp_cycle["diagnostic_classification"] == expected
    assert q011hp_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hp_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011hq" in q011hp_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hp result is not sealed")
def test_q011hp_preserves_scientific_boundary(q011hp_cycle: dict[str, Any]) -> None:
    theorem = q011hp_cycle["theorem_consequence"]
    resolved = EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
    assert theorem[
        "component_safe_complex_phase_discs_resolve_seventy_second_q011cb_witness"
    ] is resolved
    assert theorem[
        "seventy_second_q011cb_witness_persists_under_component_safe_phase_discs"
    ] is (not resolved)
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hn_ordinal_seventy_phase_resolution_is_preserved"]
    assert theorem["q011hm_ordinal_seventy_interval_inert_diagnostic_is_preserved"]
    assert all(
        value
        for name, value in theorem.items()
        if name.endswith("_is_preserved") and isinstance(value, bool)
    )
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 71" in q011hp_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 70" in q011hp_cycle["claim_boundary"]
    assert "later 44728 Q011cb refined signatures" in q011hp_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011hp_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hp result is not sealed")
def test_q011hp_cycle_has_strict_reproducible_digests(q011hp_cycle: dict[str, Any]) -> None:
    json.dumps(q011hp_cycle, allow_nan=False)
    assert {name: q011hp_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011hp_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011hp_cycle["result_digest_sha256"] == (
        q011hp.q011b._canonical_json_sha256(q011hp._result_digest_sections(q011hp_cycle))
    )
    assert q011hp._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hp result is not sealed")
def test_q011hp_study_metadata_and_optional_artifact_are_scoped(
    q011hp_study: dict[str, Any],
) -> None:
    assert q011hp_study["schema_version"] == 1
    assert q011hp_study["source"] == source_metadata()
    assert q011hp_study["study_gate"] == "passed"
    assert q011hp_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hp_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hp_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 71
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hp_study, allow_nan=False)

    runner_path = Path(q011hp.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hp_degree34_seventy_second_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hp artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hp_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hp.q011b._canonical_json_sha256(q011hp._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
