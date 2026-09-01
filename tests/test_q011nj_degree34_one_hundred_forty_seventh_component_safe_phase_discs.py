from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011nj_degree34_one_hundred_forty_seventh_component_safe_phase_discs as q011nj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "19b7791cb16c4d318026934cd5f19dcc51f533849e4a361e5d59001972ec668b"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8037fe32e6a9be3f22d3ea02ca1db4aafc7edc67ab6b625865d3ce643784b239"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "1a87e706aca2da16fa81510ae1feef263006c6716553d6ba27ff26865e748042",
    "phase_input_digest_sha256": (
        "9831a11a32cabb5e4cc342e00ff910b22f4a2d2f227f3f1c6b9d0085773ad962"
    ),
    "allocation_digest_sha256": (
        "87822957db402f76e9937eb19f236657259178b27475c9d8c9a2a73a532f734e"
    ),
    "phase_comparison_digest_sha256": (
        "146b17e12275b0a410654880e38a947f978f5dfd79cbc754341bb2d8d2d4bdce"
    ),
    "result_digest_sha256": "4710adae6f73c2cc40a12e415933e66264366236fc54ff2c3f463ac6a3e50ac1",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "24ee9aa9a109dea45cd16ae5cee2ce4f2b3ee9221187851d5b8974f23b03451c"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "205aeac7dcb616fcd85ad87e4567d590f9b0b906422e3fd814ad9b05a08f1281"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_256
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 8, 0, 1, 0, 5, 2, 0, 2, 3]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc85edp-6"
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
def q011nj_structure() -> dict[str, Any]:
    sealed, artifacts = q011nj._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011nj._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011nj._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011nj_study() -> dict[str, Any]:
    return q011nj.run_q011nj_study()


@pytest.fixture(scope="module")
def q011nj_cycle(q011nj_study: dict[str, Any]) -> dict[str, Any]:
    return q011nj_study["cycle"]


def test_q011nj_seals_q011ni_and_all_prior_inputs(
    q011nj_structure: dict[str, Any],
) -> None:
    sealed = q011nj_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 352
    assert sealed["direct_digest_count"] == 1_596
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ni"]["digests"]) == q011nj.Q011NI_DIGESTS
    assert sealed["q011ni"]["artifact_sha256"] == q011nj.Q011NI_ARTIFACT_SHA256
    assert sealed["q011ni"]["runner_sha256"] == q011nj.Q011NI_RUNNER_SHA256
    repeated, repeated_artifacts = q011nj._sealed_input_audit()
    parent, parent_artifacts = q011nj.q011ni._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 352
    assert len(repeated_artifacts) == 352
    assert parent["passed"] and parent["artifact_count"] == 351
    assert len(parent_artifacts) == 351


def test_q011nj_reconstructs_component_safe_phase_discs(
    q011nj_structure: dict[str, Any],
) -> None:
    fixed = q011nj_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 146
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert all(count > 0 for count in q011nj.SOURCE_POWER_MAXIMUM_COUNTS)
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011nj.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011nj.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011nj.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011nj.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ni_compatible_wave_allocation_count"] == 2_799
    assert fixed["q011ni_compatible_wave_allocation_digest_sha256"] == (
        q011nj.q011ni.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011nj._protocol_globals_are_restored()


def test_q011nj_enumerates_registered_label_free_phase_inventory(
    q011nj_structure: dict[str, Any],
) -> None:
    allocation = q011nj_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == q011nj.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011nj.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011nj.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011nj.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 2_799
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011nj.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 321,
        "2": 1_239,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011nj.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011nj.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011nj_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_forty_six_active_totals"] == [1, 12, 9, 5, 2, 5]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nj result is not sealed")
def test_q011nj_classifies_all_complex_phase_product_discs(
    q011nj_cycle: dict[str, Any],
) -> None:
    comparison = q011nj_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011nj-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nj result is not sealed")
def test_q011nj_minimum_exact_phase_margin_is_fixed(
    q011nj_cycle: dict[str, Any],
) -> None:
    witness = q011nj_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nj result is not sealed")
def test_q011nj_applies_stopping_rule_and_preserves_boundary(
    q011nj_cycle: dict[str, Any],
) -> None:
    assert q011nj_cycle["study_validity"] == "passed"
    assert q011nj_cycle["failed_validity_order"] == []
    assert q011nj_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011nj_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011nj_cycle["diagnostic_gates"].values())
    assert q011nj_cycle["scientific_outcome"] == "not_evaluated"
    assert q011nj_cycle["actual_resonance_outcome"] == "not_established"
    assert q011nj_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011nj.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011nj.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011nj_cycle["diagnostic_classification"] == expected
    theorem = q011nj_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_forty_seventh_q011cb_witness"
        ],
        theorem["one_hundred_forty_seventh_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011ni_ordinal_one_hundred_forty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mz_ordinal_one_hundred_forty_one_phase_resolution_is_preserved"]
    assert theorem["q011my_ordinal_one_hundred_forty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mx_ordinal_one_hundred_forty_phase_resolution_is_preserved"]
    assert theorem["q011mw_ordinal_one_hundred_forty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mv_ordinal_one_hundred_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011mu_ordinal_one_hundred_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mt_ordinal_one_hundred_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011mr_ordinal_one_hundred_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 146" in q011nj_cycle["claim_boundary"]
    assert "ordinals 0 through 145" in q011nj_cycle["claim_boundary"]
    assert "later 44653 Q011cb refined signatures" in q011nj_cycle["claim_boundary"]
    assert "Q011nk" in q011nj_cycle["next_change"]
    assert {name: q011nj_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011nj_cycle["result_digest_sha256"] == (
        q011nj.q011b._canonical_json_sha256(q011nj._result_digest_sections(q011nj_cycle))
    )
    assert q011nj._protocol_globals_are_restored()
    json.dumps(q011nj_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nj result is not sealed")
def test_q011nj_study_metadata_and_optional_artifact_are_scoped(
    q011nj_study: dict[str, Any],
) -> None:
    assert q011nj_study["schema_version"] == 1
    assert q011nj_study["source"] == source_metadata()
    assert q011nj_study["study_gate"] == "passed"
    assert q011nj_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011nj_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011nj_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 146
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011nj_study, allow_nan=False)

    runner_path = Path(q011nj.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011nj_degree34_one_hundred_forty_seventh_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011nj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011nj_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011nj.q011b._canonical_json_sha256(q011nj._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
