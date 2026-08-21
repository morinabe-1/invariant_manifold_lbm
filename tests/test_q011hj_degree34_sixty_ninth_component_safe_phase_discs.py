from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hj_degree34_sixty_ninth_component_safe_phase_discs as q011hj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d0daa3542ceb9858adac8f431ca41d06109d5b949c3564b8ad091c28ed67a33c"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "61f13a208c64119479b6abaed9fcc48cad808f9a0c22750b5674a4c6aa0f0d1e"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "930103e2130c0f8e042e16f327ed4bbdd25fd10d93dc957aa79e0d8595613abb",
    "phase_input_digest_sha256": "47073cbf60b3d43c04902e1ec84484fbe94d7fc7c3cbe36a6d8c47ab10a04663",
    "allocation_digest_sha256": "1a6f6f0f1b8178fb5205e37101bdc54ad90614758b2815a0ada6b679fdefaa9b",
    "phase_comparison_digest_sha256": "1ae3bfbc686cef1eb559a73a6fa3b77a874499a4b1ee8fc29510f8c085d72647",
    "result_digest_sha256": "9c64d9e9ab07dcf6f69e5addb90d383dccb37bf0f6e43be5bb7247ce76d32ffa",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "95075b7e24b0aeaeb915b9d8b6371548acc6d162d831ff89221643f34e8f790a"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "8c8cf6e53c96a08c4f432a201d6736541e31ce7940c2070ae4edcd68d8b31342"
)
EXPECTED_MINIMUM_INDEX: int | None = 12_725
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 5, 0, 4, 0, 5, 4, 0, 2, 1]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc865cp-6"
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
def q011hj_structure() -> dict[str, Any]:
    sealed, artifacts = q011hj._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011hj._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011hj._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011hj_study() -> dict[str, Any]:
    return q011hj.run_q011hj_study()


@pytest.fixture(scope="module")
def q011hj_cycle(q011hj_study: dict[str, Any]) -> dict[str, Any]:
    return q011hj_study["cycle"]


def test_q011hj_seals_q011hi_and_all_prior_inputs(
    q011hj_structure: dict[str, Any],
) -> None:
    sealed = q011hj_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 196
    assert sealed["direct_digest_count"] == 894
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hi"]["digests"]) == q011hj.Q011HI_DIGESTS
    assert sealed["q011hi"]["artifact_sha256"] == q011hj.Q011HI_ARTIFACT_SHA256
    assert sealed["q011hi"]["runner_sha256"] == q011hj.Q011HI_RUNNER_SHA256


def test_q011hj_reconstructs_component_safe_phase_discs(
    q011hj_structure: dict[str, Any],
) -> None:
    fixed = q011hj_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 68
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011hj.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011hj.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011hj.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011hj.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011hi_compatible_wave_allocation_count"] == 1_699
    assert fixed["q011hi_compatible_wave_allocation_digest_sha256"] == (
        q011hj.q011hi.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011hj._protocol_globals_are_restored()


def test_q011hj_enumerates_registered_label_free_phase_inventory(
    q011hj_structure: dict[str, Any],
) -> None:
    allocation = q011hj_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == q011hj.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011hj.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 2, 2, 3, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 4, 0, 3]
    assert allocation["individual_wave_allocation_count"] == 1_699
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011hj.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 191,
        "2": 754,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_699
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011hj.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011hj.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 20_786
    )
    assert q011hj_structure["compatible_count"] == 20_786
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_sixty_eight_totals"] == [13, 9, 5, 4, 3]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hj result is not sealed")
def test_q011hj_classifies_all_complex_phase_product_discs(
    q011hj_cycle: dict[str, Any],
) -> None:
    comparison = q011hj_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 20_786
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 20_786
    assert comparison["comparison_stream_count"] == 20_786
    assert comparison["comparison_stream_domain"] == "q011hj-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 20_786,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hj result is not sealed")
def test_q011hj_minimum_exact_phase_margin_is_fixed(
    q011hj_cycle: dict[str, Any],
) -> None:
    comparison = q011hj_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    margin = q011hj.q011z._fraction(witness["complex_separation_margin_lower"]["exact"])
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert margin > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hj result is not sealed")
def test_q011hj_records_scoped_outcome(q011hj_cycle: dict[str, Any]) -> None:
    assert q011hj_cycle["study_validity"] == "passed"
    assert q011hj_cycle["failed_validity_order"] == []
    assert q011hj_cycle["failed_diagnostic_order"] == []
    assert len(q011hj_cycle["validity_gates"]) == 7
    assert len(q011hj_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011hj_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hj_cycle["diagnostic_gates"].values())
    assert q011hj_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected_classification = (
        q011hj.RESOLVED_CLASSIFICATION
        if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
        else q011hj.PERSISTENT_CLASSIFICATION
    )
    assert q011hj_cycle["diagnostic_classification"] == expected_classification
    assert q011hj_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hj_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011hk" in q011hj_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hj result is not sealed")
def test_q011hj_preserves_scientific_boundary(q011hj_cycle: dict[str, Any]) -> None:
    theorem = q011hj_cycle["theorem_consequence"]
    resolved = EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved"
    assert theorem["component_safe_complex_phase_discs_resolve_sixty_ninth_q011cb_witness"] is resolved
    assert theorem["sixty_ninth_q011cb_witness_persists_under_component_safe_phase_discs"] is (
        not resolved
    )
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011hi_ordinal_sixty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hh_ordinal_sixty_seven_phase_resolution_is_preserved"]
    assert theorem["q011hg_ordinal_sixty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hf_ordinal_sixty_six_phase_resolution_is_preserved"]
    assert theorem["q011he_ordinal_sixty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hd_ordinal_sixty_five_phase_resolution_is_preserved"]
    assert theorem["q011hc_ordinal_sixty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hb_ordinal_sixty_four_phase_resolution_is_preserved"]
    assert theorem["q011ha_ordinal_sixty_four_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 68" in q011hj_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 67" in q011hj_cycle["claim_boundary"]
    assert "later 44731 Q011cb refined signatures" in q011hj_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011hj_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hj result is not sealed")
def test_q011hj_cycle_has_strict_reproducible_digests(
    q011hj_cycle: dict[str, Any],
) -> None:
    json.dumps(q011hj_cycle, allow_nan=False)
    assert {name: q011hj_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011hj_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011hj_cycle["result_digest_sha256"] == (
        q011hj.q011b._canonical_json_sha256(q011hj._result_digest_sections(q011hj_cycle))
    )
    assert q011hj._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hj result is not sealed")
def test_q011hj_study_metadata_and_optional_artifact_are_scoped(
    q011hj_study: dict[str, Any],
) -> None:
    assert q011hj_study["schema_version"] == 1
    assert q011hj_study["source"] == source_metadata()
    assert q011hj_study["study_gate"] == "passed"
    assert q011hj_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hj_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hj_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 68
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hj_study, allow_nan=False)

    runner_path = Path(q011hj.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hj_degree34_sixty_ninth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hj_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hj.q011b._canonical_json_sha256(q011hj._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
