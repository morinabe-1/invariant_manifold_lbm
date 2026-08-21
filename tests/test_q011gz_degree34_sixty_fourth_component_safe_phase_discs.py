from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gz_degree34_sixty_fourth_component_safe_phase_discs as q011gz
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
def q011gz_structure() -> dict[str, Any]:
    sealed, artifacts = q011gz._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011gz._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011gz._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011gz_study() -> dict[str, Any]:
    return q011gz.run_q011gz_study()


@pytest.fixture(scope="module")
def q011gz_cycle(q011gz_study: dict[str, Any]) -> dict[str, Any]:
    return q011gz_study["cycle"]


def test_q011gz_seals_q011gy_and_all_prior_inputs(
    q011gz_structure: dict[str, Any],
) -> None:
    sealed = q011gz_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 186
    assert sealed["direct_digest_count"] == 849
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gy"]["digests"]) == q011gz.Q011GY_DIGESTS
    assert sealed["q011gy"]["artifact_sha256"] == q011gz.Q011GY_ARTIFACT_SHA256
    assert sealed["q011gy"]["runner_sha256"] == q011gz.Q011GY_RUNNER_SHA256


def test_q011gz_reconstructs_component_safe_phase_discs(
    q011gz_structure: dict[str, Any],
) -> None:
    fixed = q011gz_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 63
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011gz.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011gz.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011gz.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011gz.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011gy_compatible_wave_allocation_count"] == 911
    assert fixed["q011gy_compatible_wave_allocation_digest_sha256"] == (
        q011gz.q011gy.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011gz._protocol_globals_are_restored()


def test_q011gz_enumerates_registered_label_free_phase_inventory(
    q011gz_structure: dict[str, Any],
) -> None:
    allocation = q011gz_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == q011gz.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011gz.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 5, 2, 0, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 7, 0, 0]
    assert allocation["individual_wave_allocation_count"] == 911
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011gz.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 77,
        "3": 226,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 911
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011gz.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011gz.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 8_350
    )
    assert q011gz_structure["compatible_count"] == 8_350
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_sixty_three_totals"] == [13, 9, 5, 7, 0]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gz result is not sealed")
def test_q011gz_classifies_all_complex_phase_product_discs(
    q011gz_cycle: dict[str, Any],
) -> None:
    comparison = q011gz_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 8_350
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 8_350
    assert comparison["comparison_stream_count"] == 8_350
    assert comparison["comparison_stream_domain"] == "q011gz-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 8_350,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gz result is not sealed")
def test_q011gz_minimum_exact_phase_margin_is_fixed(
    q011gz_cycle: dict[str, Any],
) -> None:
    comparison = q011gz_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    assert q011gz.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gz result is not sealed")
def test_q011gz_records_scoped_outcome(q011gz_cycle: dict[str, Any]) -> None:
    assert q011gz_cycle["study_validity"] == "passed"
    assert q011gz_cycle["failed_validity_order"] == []
    assert q011gz_cycle["failed_diagnostic_order"] == []
    assert len(q011gz_cycle["validity_gates"]) == 7
    assert len(q011gz_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011gz_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gz_cycle["diagnostic_gates"].values())
    assert q011gz_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    assert q011gz_cycle["diagnostic_classification"] == q011gz.RESOLVED_CLASSIFICATION
    assert q011gz_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gz_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ha" in q011gz_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011gz_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gz result is not sealed")
def test_q011gz_preserves_scientific_boundary(q011gz_cycle: dict[str, Any]) -> None:
    theorem = q011gz_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_sixty_fourth_q011cb_witness"]
    assert not theorem["sixty_fourth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011gy_ordinal_sixty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gx_ordinal_sixty_two_phase_resolution_is_preserved"]
    assert theorem["q011gw_ordinal_sixty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gv_ordinal_sixty_one_phase_resolution_is_preserved"]
    assert theorem["q011gu_ordinal_sixty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gt_ordinal_sixty_phase_resolution_is_preserved"]
    assert theorem["q011gs_ordinal_sixty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gr_ordinal_fifty_nine_phase_resolution_is_preserved"]
    assert theorem["q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 63" in q011gz_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 62" in q011gz_cycle["claim_boundary"]
    assert "later 44736 Q011cb refined signatures" in q011gz_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011gz_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gz result is not sealed")
def test_q011gz_cycle_has_strict_reproducible_digests(
    q011gz_cycle: dict[str, Any],
) -> None:
    json.dumps(q011gz_cycle, allow_nan=False)
    assert {name: q011gz_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011gz_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011gz_cycle["result_digest_sha256"] == (
        q011gz.q011b._canonical_json_sha256(q011gz._result_digest_sections(q011gz_cycle))
    )
    assert q011gz._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gz result is not sealed")
def test_q011gz_study_metadata_and_optional_artifact_are_scoped(
    q011gz_study: dict[str, Any],
) -> None:
    assert q011gz_study["schema_version"] == 1
    assert q011gz_study["source"] == source_metadata()
    assert q011gz_study["study_gate"] == "passed"
    assert q011gz_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011gz_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gz_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 63
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gz_study, allow_nan=False)

    runner_path = Path(q011gz.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gz_degree34_sixty_fourth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gz artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gz_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gz.q011b._canonical_json_sha256(q011gz._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
