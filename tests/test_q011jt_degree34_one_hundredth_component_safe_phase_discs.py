from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jt_degree34_one_hundredth_component_safe_phase_discs as q011jt
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "01348e01b757238cdc46883f20273205c5a77a8751c25b916fa32d8081853960"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "775f4b2a1c32b739658efad5512656a796e302a5317f302e435d96ce06756efa"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "b48bd46a8a77bb2ca18e86a7e1fc2b65eb7ce90f422da9b1e3ef54cc3c564b94",
    "phase_input_digest_sha256": (
        "3e5434eec9ff1513ebbdd9975e5e6d4cbfd8e7a6cfaa5b5b066f3b6914595e71"
    ),
    "allocation_digest_sha256": (
        "3b4d7aacbc8d9c2e07354f303cc87ba2a51142da8d9576580fc372af737411c6"
    ),
    "phase_comparison_digest_sha256": (
        "e7e632e122849f8ba4f352f6ae204363207f52dc92708d7ed837d0c057e7a02d"
    ),
    "result_digest_sha256": "c989c4315b299de87f64aa3b82cf19c59c5ea900379965b8f3ee4491b8258d2e",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "0046ba335ce7afe2e37e2dae65bf7483efe908ea924f37d251105e787e6c7e1e"
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
def q011jt_structure() -> dict[str, Any]:
    sealed, artifacts = q011jt._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011jt._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011jt._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011jt_study() -> dict[str, Any]:
    return q011jt.run_q011jt_study()


@pytest.fixture(scope="module")
def q011jt_cycle(q011jt_study: dict[str, Any]) -> dict[str, Any]:
    return q011jt_study["cycle"]


def test_q011jt_seals_q011js_and_all_prior_inputs(
    q011jt_structure: dict[str, Any],
) -> None:
    sealed = q011jt_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 258
    assert sealed["direct_digest_count"] == 1_173
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011js"]["digests"]) == q011jt.Q011JS_DIGESTS
    assert sealed["q011js"]["artifact_sha256"] == q011jt.Q011JS_ARTIFACT_SHA256
    assert sealed["q011js"]["runner_sha256"] == q011jt.Q011JS_RUNNER_SHA256


def test_q011jt_reconstructs_component_safe_phase_discs(
    q011jt_structure: dict[str, Any],
) -> None:
    fixed = q011jt_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 99
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011jt.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011jt.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011jt.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011jt.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011js_compatible_wave_allocation_count"] == 4_136
    assert fixed["q011js_compatible_wave_allocation_digest_sha256"] == (
        q011jt.q011js.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011jt._protocol_globals_are_restored()


def test_q011jt_enumerates_registered_label_free_phase_inventory(
    q011jt_structure: dict[str, Any],
) -> None:
    allocation = q011jt_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 686_400
    assert allocation["full_allocation_digest_sha256"] == q011jt.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 37_940
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011jt.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011jt.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011jt.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 4_136
    assert allocation["component_wave_projection_count"] == 1_729
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011jt.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 354,
        "2": 343,
        "3": 1_032,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011jt.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_729
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011jt.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011jt_structure["compatible_count"] == 37_940
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_ninety_nine_active_totals"] == [1, 12, 9, 5, 3, 4]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jt result is not sealed")
def test_q011jt_classifies_all_complex_phase_product_discs(
    q011jt_cycle: dict[str, Any],
) -> None:
    comparison = q011jt_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 37_940
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 37_940
    assert comparison["comparison_stream_count"] == 37_940
    assert comparison["comparison_stream_domain"] == ("q011jt-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 37_940,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jt result is not sealed")
def test_q011jt_minimum_exact_phase_margin_is_fixed(
    q011jt_cycle: dict[str, Any],
) -> None:
    witness = q011jt_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jt result is not sealed")
def test_q011jt_applies_stopping_rule_and_preserves_boundary(
    q011jt_cycle: dict[str, Any],
) -> None:
    assert q011jt_cycle["study_validity"] == "passed"
    assert q011jt_cycle["failed_validity_order"] == []
    assert q011jt_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jt_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jt_cycle["diagnostic_gates"].values())
    assert q011jt_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jt_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jt_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011jt.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011jt.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jt_cycle["diagnostic_classification"] == expected
    theorem = q011jt_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_one_hundredth_q011cb_witness"],
        theorem["one_hundredth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011js_ordinal_ninety_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jr_ordinal_ninety_eight_phase_resolution_is_preserved"]
    assert theorem["q011jq_ordinal_ninety_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jn_ordinal_ninety_six_phase_resolution_is_preserved"]
    assert theorem["q011jk_ordinal_ninety_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jj_ordinal_ninety_four_phase_resolution_is_preserved"]
    assert theorem["q011ji_ordinal_ninety_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 99" in q011jt_cycle["claim_boundary"]
    assert "ordinals 0 through 98" in q011jt_cycle["claim_boundary"]
    assert "later 44700 Q011cb refined signatures" in q011jt_cycle["claim_boundary"]
    assert "Q011ju" in q011jt_cycle["next_change"]
    assert {name: q011jt_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jt_cycle["result_digest_sha256"] == (
        q011jt.q011b._canonical_json_sha256(q011jt._result_digest_sections(q011jt_cycle))
    )
    assert q011jt._protocol_globals_are_restored()
    json.dumps(q011jt_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jt result is not sealed")
def test_q011jt_study_metadata_and_optional_artifact_are_scoped(
    q011jt_study: dict[str, Any],
) -> None:
    assert q011jt_study["schema_version"] == 1
    assert q011jt_study["source"] == source_metadata()
    assert q011jt_study["study_gate"] == "passed"
    assert q011jt_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jt_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 37_940
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jt_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 99
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jt_study, allow_nan=False)

    runner_path = Path(q011jt.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jt_degree34_one_hundredth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jt artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jt_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jt.q011b._canonical_json_sha256(q011jt._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
