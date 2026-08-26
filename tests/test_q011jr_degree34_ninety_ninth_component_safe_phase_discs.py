from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jr_degree34_ninety_ninth_component_safe_phase_discs as q011jr
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "47f71d575569abfc05c3b445ab8d99cadeffb8a65753afd79297c77282bb3aa4"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "0d27f31ae41ef42ecdcb03d55291e7c04bd95cb12b92024a8413d58dcac3f7cf"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "fac5d3a760f5eec17d81577a671c2709cf4c3ec872811aeef10edbb755824de0",
    "phase_input_digest_sha256": (
        "f6ebb11e6710a5f2a188e276be5776f43e1b6d8f9516ea932c906c4ee4f08b2d"
    ),
    "allocation_digest_sha256": (
        "b92797241ac70ace2793e884caa04fc7026efd12d4977d4d17a2d4bd1df913a8"
    ),
    "phase_comparison_digest_sha256": (
        "42237bd37324a3ca15d5053b753cb9125c0b8fdaeaf1d307d49372c9ca41878a"
    ),
    "result_digest_sha256": "48c7699bdafa34989850cc03d6c2e8068e6017d949791df61af5813c33b7db64",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "a83765d384cf8e70a6790da6b0f936ad1cacecd1e985bc2f119cdf2b74477867"
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
def q011jr_structure() -> dict[str, Any]:
    sealed, artifacts = q011jr._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011jr._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011jr._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011jr_study() -> dict[str, Any]:
    return q011jr.run_q011jr_study()


@pytest.fixture(scope="module")
def q011jr_cycle(q011jr_study: dict[str, Any]) -> dict[str, Any]:
    return q011jr_study["cycle"]


def test_q011jr_seals_q011jq_and_all_prior_inputs(
    q011jr_structure: dict[str, Any],
) -> None:
    sealed = q011jr_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 256
    assert sealed["direct_digest_count"] == 1_164
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jq"]["digests"]) == q011jr.Q011JQ_DIGESTS
    assert sealed["q011jq"]["artifact_sha256"] == q011jr.Q011JQ_ARTIFACT_SHA256
    assert sealed["q011jq"]["runner_sha256"] == q011jr.Q011JQ_RUNNER_SHA256


def test_q011jr_reconstructs_component_safe_phase_discs(
    q011jr_structure: dict[str, Any],
) -> None:
    fixed = q011jr_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 98
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011jr.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011jr.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011jr.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011jr.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011jq_compatible_wave_allocation_count"] == 3_727
    assert fixed["q011jq_compatible_wave_allocation_digest_sha256"] == (
        q011jr.q011jq.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011jr._protocol_globals_are_restored()


def test_q011jr_enumerates_registered_label_free_phase_inventory(
    q011jr_structure: dict[str, Any],
) -> None:
    allocation = q011jr_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == q011jr.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011jr.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011jr.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011jr.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 3_727
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011jr.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 321,
        "2": 311,
        "3": 928,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011jr.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011jr.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011jr_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_ninety_eight_active_totals"] == [1, 12, 9, 5, 2, 5]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jr result is not sealed")
def test_q011jr_classifies_all_complex_phase_product_discs(
    q011jr_cycle: dict[str, Any],
) -> None:
    comparison = q011jr_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011jr-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jr result is not sealed")
def test_q011jr_minimum_exact_phase_margin_is_fixed(
    q011jr_cycle: dict[str, Any],
) -> None:
    witness = q011jr_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jr result is not sealed")
def test_q011jr_applies_stopping_rule_and_preserves_boundary(
    q011jr_cycle: dict[str, Any],
) -> None:
    assert q011jr_cycle["study_validity"] == "passed"
    assert q011jr_cycle["failed_validity_order"] == []
    assert q011jr_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jr_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jr_cycle["diagnostic_gates"].values())
    assert q011jr_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jr_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jr_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011jr.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011jr.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jr_cycle["diagnostic_classification"] == expected
    theorem = q011jr_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_ninety_ninth_q011cb_witness"],
        theorem["ninety_ninth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
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
    assert "flatten ordinal 98" in q011jr_cycle["claim_boundary"]
    assert "ordinals 0 through 97" in q011jr_cycle["claim_boundary"]
    assert "later 44701 Q011cb refined signatures" in q011jr_cycle["claim_boundary"]
    assert "Q011js" in q011jr_cycle["next_change"]
    assert {name: q011jr_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jr_cycle["result_digest_sha256"] == (
        q011jr.q011b._canonical_json_sha256(q011jr._result_digest_sections(q011jr_cycle))
    )
    assert q011jr._protocol_globals_are_restored()
    json.dumps(q011jr_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jr result is not sealed")
def test_q011jr_study_metadata_and_optional_artifact_are_scoped(
    q011jr_study: dict[str, Any],
) -> None:
    assert q011jr_study["schema_version"] == 1
    assert q011jr_study["source"] == source_metadata()
    assert q011jr_study["study_gate"] == "passed"
    assert q011jr_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jr_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jr_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 98
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jr_study, allow_nan=False)

    runner_path = Path(q011jr.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jr_degree34_ninety_ninth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jr artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jr_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jr.q011b._canonical_json_sha256(q011jr._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
