from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011it_degree34_eighty_seventh_component_safe_phase_discs as q011it
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = None
EXPECTED_STREAM_DIGEST: str | None = None
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = None
EXPECTED_MINIMUM_INDEX: int | None = None
EXPECTED_MINIMUM_COUNTS: list[int] | None = None
EXPECTED_MINIMUM_MARGIN_HEX: str | None = None
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = None
EXPECTED_REFINEMENT_OUTCOME: str | None = None
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
def q011it_structure() -> dict[str, Any]:
    sealed, artifacts = q011it._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011it._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011it._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011it_study() -> dict[str, Any]:
    return q011it.run_q011it_study()


@pytest.fixture(scope="module")
def q011it_cycle(q011it_study: dict[str, Any]) -> dict[str, Any]:
    return q011it_study["cycle"]


def test_q011it_seals_q011is_and_all_prior_inputs(
    q011it_structure: dict[str, Any],
) -> None:
    sealed = q011it_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 232
    assert sealed["direct_digest_count"] == 1_056
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011is"]["digests"]) == q011it.Q011IS_DIGESTS
    assert sealed["q011is"]["artifact_sha256"] == q011it.Q011IS_ARTIFACT_SHA256
    assert sealed["q011is"]["runner_sha256"] == q011it.Q011IS_RUNNER_SHA256


def test_q011it_reconstructs_component_safe_phase_discs(
    q011it_structure: dict[str, Any],
) -> None:
    fixed = q011it_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 86
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 14
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011it.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011it.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011it.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011it.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011is_compatible_wave_allocation_count"] == 1_219
    assert fixed["q011is_compatible_wave_allocation_digest_sha256"] == (
        q011it.q011is.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011it._protocol_globals_are_restored()


def test_q011it_enumerates_registered_label_free_phase_inventory(
    q011it_structure: dict[str, Any],
) -> None:
    allocation = q011it_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == (q011it.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011it.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == (q011it.EXPECTED_FIRST_COMPATIBLE_COUNTS)
    assert tuple(allocation["last_compatible_counts"]) == (q011it.EXPECTED_LAST_COMPATIBLE_COUNTS)
    assert allocation["individual_wave_allocation_count"] == 1_219
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011it.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 1_219,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011it.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011it.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 253,
        "18": 245,
        "24": 241,
        "28": 240,
        "30": 240,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 26_644
    )
    assert q011it_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_eighty_six_totals"] == [1, 12, 9, 5, 6, 1]
    assert adapter["all_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011it result is not sealed")
def test_q011it_classifies_all_complex_phase_product_discs(
    q011it_cycle: dict[str, Any],
) -> None:
    comparison = q011it_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011it-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011it result is not sealed")
def test_q011it_minimum_exact_phase_margin_is_fixed(
    q011it_cycle: dict[str, Any],
) -> None:
    witness = q011it_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011it result is not sealed")
def test_q011it_applies_stopping_rule_and_preserves_boundary(
    q011it_cycle: dict[str, Any],
) -> None:
    assert q011it_cycle["study_validity"] == "passed"
    assert q011it_cycle["failed_validity_order"] == []
    assert q011it_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011it_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011it_cycle["diagnostic_gates"].values())
    assert q011it_cycle["scientific_outcome"] == "not_evaluated"
    assert q011it_cycle["actual_resonance_outcome"] == "not_established"
    assert q011it_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011it.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011it.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011it_cycle["diagnostic_classification"] == expected
    theorem = q011it_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_eighty_seventh_q011cb_witness"],
        theorem["eighty_seventh_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011is_ordinal_eighty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ir_ordinal_eighty_five_phase_resolution_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 86" in q011it_cycle["claim_boundary"]
    assert "ordinals 0 through 85" in q011it_cycle["claim_boundary"]
    assert "later 44713 Q011cb refined signatures" in q011it_cycle["claim_boundary"]
    assert "Q011iu" in q011it_cycle["next_change"]
    assert {name: q011it_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011it_cycle["result_digest_sha256"] == (
        q011it.q011b._canonical_json_sha256(q011it._result_digest_sections(q011it_cycle))
    )
    assert q011it._protocol_globals_are_restored()
    json.dumps(q011it_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011it result is not sealed")
def test_q011it_study_metadata_and_optional_artifact_are_scoped(
    q011it_study: dict[str, Any],
) -> None:
    assert q011it_study["schema_version"] == 1
    assert q011it_study["source"] == source_metadata()
    assert q011it_study["study_gate"] == "passed"
    assert q011it_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011it_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011it_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 86
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011it_study, allow_nan=False)

    runner_path = Path(q011it.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011it_degree34_eighty_seventh_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011it artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011it_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011it.q011b._canonical_json_sha256(q011it._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
