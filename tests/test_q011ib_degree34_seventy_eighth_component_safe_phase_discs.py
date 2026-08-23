from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ib_degree34_seventy_eighth_component_safe_phase_discs as q011ib
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "bc32fc405cbb741eb921ff2eaedafe38537c5c9ea2635ebe2a47f5562deee706"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "3e600337101acad30a428769f41c5b8c7e53b5a290dbc3e477eed15cef9d1208"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "366387954524c7cc63480ccc0f31a26e0f3fa181e5ad7646ed12049d2939290a",
    "phase_input_digest_sha256": "18b83b589670fd4bdea53bd457cf4d96a6d253b85f7f9523e8a87f7cc0aa7840",
    "allocation_digest_sha256": "776a169d84ce955923b28a70c419f25989d3415968710f159b1bb5156bc4d0bc",
    "phase_comparison_digest_sha256": (
        "d26a6cc64a8c98c3bea96d09f2dd056b046b3f0ab3266e6c77eb795abffd15fb"
    ),
    "result_digest_sha256": "5fa40623098b5e0b6d1864198611ecb78541bbbad747ad1f645d8a6202556daa",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "1d8ac9ded0d77ca03be0afa70c71d446ad422f485cf2a5f461df0c5a2ebf8985"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "514c3194347c4be6775cc7a53518fbee0c3d97586a962c6e2b63378ce8a8614f"
)
EXPECTED_MINIMUM_INDEX: int | None = 11_474
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 4, 0, 5, 0, 5, 5, 0, 2, 0]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc86dap-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 18_718,
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
def q011ib_structure() -> dict[str, Any]:
    sealed, artifacts = q011ib._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011ib._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011ib._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011ib_study() -> dict[str, Any]:
    return q011ib.run_q011ib_study()


@pytest.fixture(scope="module")
def q011ib_cycle(q011ib_study: dict[str, Any]) -> dict[str, Any]:
    return q011ib_study["cycle"]


def test_q011ib_seals_q011ia_and_all_prior_inputs(q011ib_structure: dict[str, Any]) -> None:
    sealed = q011ib_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 214
    assert sealed["direct_digest_count"] == 975
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ia"]["digests"]) == q011ib.Q011IA_DIGESTS
    assert sealed["q011ia"]["artifact_sha256"] == q011ib.Q011IA_ARTIFACT_SHA256
    assert sealed["q011ia"]["runner_sha256"] == q011ib.Q011IA_RUNNER_SHA256


def test_q011ib_reconstructs_component_safe_phase_discs(
    q011ib_structure: dict[str, Any],
) -> None:
    fixed = q011ib_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 77
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011ib.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011ib.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011ib.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011ib.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships and [148] in memberships and [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ia_compatible_wave_allocation_count"] == 852
    assert fixed["q011ia_compatible_wave_allocation_digest_sha256"] == (
        q011ib.q011ia.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ib._protocol_globals_are_restored()


def test_q011ib_enumerates_registered_label_free_phase_inventory(
    q011ib_structure: dict[str, Any],
) -> None:
    allocation = q011ib_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == q011ib.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ib.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 3, 2, 2, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 5, 0, 2]
    assert allocation["individual_wave_allocation_count"] == 852
    assert allocation["component_wave_projection_count"] == 852
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ib.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 852,
    }
    assert sum(
        record["individual_wave_allocation_count"]
        for record in allocation["individual_to_component_bridge_records"]
    ) == 852
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ib.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ib.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert sum(
        record["phase_allocation_count"] for record in allocation["wave_projection_records"]
    ) == 18_718
    assert q011ib_structure["compatible_count"] == 18_718
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_seventy_seven_totals"] == [13, 9, 5, 5, 2]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ib result is not sealed")
def test_q011ib_classifies_all_complex_phase_product_discs(q011ib_cycle: dict[str, Any]) -> None:
    comparison = q011ib_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 18_718
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 18_718
    assert comparison["comparison_stream_count"] == 18_718
    assert comparison["comparison_stream_domain"] == "q011ib-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 18_718,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ib result is not sealed")
def test_q011ib_minimum_exact_phase_margin_is_fixed(q011ib_cycle: dict[str, Any]) -> None:
    witness = q011ib_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == EXPECTED_MINIMUM_MARGIN_HEX
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    margin = q011ib.q011z._fraction(witness["complex_separation_margin_lower"]["exact"])
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert margin > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ib result is not sealed")
def test_q011ib_records_scoped_outcome(q011ib_cycle: dict[str, Any]) -> None:
    assert q011ib_cycle["study_validity"] == "passed"
    assert q011ib_cycle["failed_validity_order"] == []
    assert q011ib_cycle["failed_diagnostic_order"] == []
    assert len(q011ib_cycle["validity_gates"]) == 7
    assert len(q011ib_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ib_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ib_cycle["diagnostic_gates"].values())
    assert q011ib_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = (
        q011ib.RESOLVED_CLASSIFICATION
        if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
        else q011ib.PERSISTENT_CLASSIFICATION
    )
    assert q011ib_cycle["diagnostic_classification"] == expected
    assert q011ib_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ib_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ic" in q011ib_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ib result is not sealed")
def test_q011ib_preserves_scientific_boundary(q011ib_cycle: dict[str, Any]) -> None:
    theorem = q011ib_cycle["theorem_consequence"]
    resolved = EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
    assert theorem[
        "component_safe_complex_phase_discs_resolve_seventy_eighth_q011cb_witness"
    ] is resolved
    assert theorem[
        "seventy_eighth_q011cb_witness_persists_under_component_safe_phase_discs"
    ] is (not resolved)
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011ia_ordinal_seventy_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hz_ordinal_seventy_six_phase_resolution_is_preserved"]
    assert theorem["q011hy_ordinal_seventy_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hx_ordinal_seventy_five_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 77" in q011ib_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 76" in q011ib_cycle["claim_boundary"]
    assert "later 44722 Q011cb refined signatures" in q011ib_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ib_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ib result is not sealed")
def test_q011ib_cycle_has_strict_reproducible_digests(q011ib_cycle: dict[str, Any]) -> None:
    json.dumps(q011ib_cycle, allow_nan=False)
    assert {name: q011ib_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ib_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ib_cycle["result_digest_sha256"] == (
        q011ib.q011b._canonical_json_sha256(q011ib._result_digest_sections(q011ib_cycle))
    )
    assert q011ib._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ib result is not sealed")
def test_q011ib_study_metadata_and_optional_artifact_are_scoped(
    q011ib_study: dict[str, Any],
) -> None:
    assert q011ib_study["schema_version"] == 1
    assert q011ib_study["source"] == source_metadata()
    assert q011ib_study["study_gate"] == "passed"
    assert q011ib_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ib_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ib_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 77
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ib_study, allow_nan=False)

    runner_path = Path(q011ib.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ib_degree34_seventy_eighth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ib artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ib_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ib.q011b._canonical_json_sha256(q011ib._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
