from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011lt_degree34_one_hundred_twenty_sixth_component_safe_phase_discs as q011lt
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "a498f2428046959b560bae739337575a68a1955bc9102c638daf41b99335ca74"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "3530c2f9a3164ae07e0c3b24c793494c964d82b030df25669da346fd9edb9123"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "49b567a2482c157ec6f2d8f3ebde2121f9cf1384502343e48d247ff20a5f189f",
    "phase_input_digest_sha256": "55bf5844b32eee637fb0bef8c4931413365e942336c3d64502a5fcab1468e876",
    "allocation_digest_sha256": "c5be941b243efe8ae73e64d0c8d4ae2ab5819c7c5f0e228a88e7f4c1659c418a",
    "phase_comparison_digest_sha256": "9643d57d18b7749b508cfa4d403b8ecb0702b04235ca479f5870358b70bde690",
    "result_digest_sha256": "915d5f007b36a0db1e772c272fe5965c5640a44d54b353eaa68701546c3a2f86",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "9c7ba99bafd0ede26a97143ff91a9a8aac4f1bfe07cf6d2ff845858827f477ff"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "2b11f4fdc60ea6f0713250d7f9f39b488ad0feaa9fff007de6ac7a61313262cd"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_070
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 5, 0, 4, 0, 5, 5, 0, 2, 0]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8768p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 34_182,
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
def q011lt_structure() -> dict[str, Any]:
    sealed, artifacts = q011lt._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011lt._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011lt._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011lt_study() -> dict[str, Any]:
    return q011lt.run_q011lt_study()


@pytest.fixture(scope="module")
def q011lt_cycle(q011lt_study: dict[str, Any]) -> dict[str, Any]:
    return q011lt_study["cycle"]


def test_q011lt_seals_q011ls_and_all_prior_inputs(
    q011lt_structure: dict[str, Any],
) -> None:
    sealed = q011lt_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 310
    assert sealed["direct_digest_count"] == 1_407
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ls"]["digests"]) == q011lt.Q011LS_DIGESTS
    assert sealed["q011ls"]["artifact_sha256"] == q011lt.Q011LS_ARTIFACT_SHA256
    assert sealed["q011ls"]["runner_sha256"] == q011lt.Q011LS_RUNNER_SHA256


def test_q011lt_reconstructs_component_safe_phase_discs(
    q011lt_structure: dict[str, Any],
) -> None:
    fixed = q011lt_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 125
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011lt.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011lt.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011lt.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011lt.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ls_compatible_wave_allocation_count"] == 4_658
    assert fixed["q011ls_compatible_wave_allocation_digest_sha256"] == (
        q011lt.q011ls.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011lt._protocol_globals_are_restored()


def test_q011lt_enumerates_registered_label_free_phase_inventory(
    q011lt_structure: dict[str, Any],
) -> None:
    allocation = q011lt_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == q011lt.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011lt.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011lt.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011lt.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 4_658
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011lt.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 321,
        "2": 311,
        "3": 308,
        "4": 309,
        "5": 311,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011lt.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011lt.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 321,
        "18": 311,
        "24": 308,
        "28": 309,
        "30": 311,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 34_182
    )
    assert q011lt_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_twenty_five_active_totals"] == [1, 12, 9, 5, 5, 2]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lt result is not sealed")
def test_q011lt_classifies_all_complex_phase_product_discs(
    q011lt_cycle: dict[str, Any],
) -> None:
    comparison = q011lt_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011lt-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lt result is not sealed")
def test_q011lt_minimum_exact_phase_margin_is_fixed(
    q011lt_cycle: dict[str, Any],
) -> None:
    witness = q011lt_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lt result is not sealed")
def test_q011lt_applies_stopping_rule_and_preserves_boundary(
    q011lt_cycle: dict[str, Any],
) -> None:
    assert q011lt_cycle["study_validity"] == "passed"
    assert q011lt_cycle["failed_validity_order"] == []
    assert q011lt_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011lt_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011lt_cycle["diagnostic_gates"].values())
    assert q011lt_cycle["scientific_outcome"] == "not_evaluated"
    assert q011lt_cycle["actual_resonance_outcome"] == "not_established"
    assert q011lt_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011lt.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011lt.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011lt_cycle["diagnostic_classification"] == expected
    theorem = q011lt_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_twenty_sixth_q011cb_witness"
        ],
        theorem[
            "one_hundred_twenty_sixth_q011cb_witness_persists_under_component_safe_phase_discs"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011ls_ordinal_one_hundred_twenty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011lp_ordinal_one_hundred_twenty_three_phase_resolution_is_preserved"]
    assert theorem["q011ln_ordinal_one_hundred_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011ll_ordinal_one_hundred_twenty_one_phase_resolution_is_preserved"]
    assert theorem["q011lj_ordinal_one_hundred_twenty_phase_resolution_is_preserved"]
    assert theorem["q011jv_ordinal_one_hundred_phase_resolution_is_preserved"]
    assert theorem["q011jt_ordinal_ninety_nine_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 125" in q011lt_cycle["claim_boundary"]
    assert "ordinals 0 through 124" in q011lt_cycle["claim_boundary"]
    assert "later 44674 Q011cb refined signatures" in q011lt_cycle["claim_boundary"]
    assert "Q011lu" in q011lt_cycle["next_change"]
    assert {name: q011lt_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011lt_cycle["result_digest_sha256"] == (
        q011lt.q011b._canonical_json_sha256(q011lt._result_digest_sections(q011lt_cycle))
    )
    assert q011lt._protocol_globals_are_restored()
    json.dumps(q011lt_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lt result is not sealed")
def test_q011lt_study_metadata_and_optional_artifact_are_scoped(
    q011lt_study: dict[str, Any],
) -> None:
    assert q011lt_study["schema_version"] == 1
    assert q011lt_study["source"] == source_metadata()
    assert q011lt_study["study_gate"] == "passed"
    assert q011lt_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011lt_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011lt_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 125
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011lt_study, allow_nan=False)

    runner_path = Path(q011lt.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011lt_degree34_one_hundred_twenty_sixth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011lt artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011lt_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011lt.q011b._canonical_json_sha256(q011lt._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
