from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mt_degree34_one_hundred_thirty_ninth_component_safe_phase_discs as q011mt
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "1158e9eefa8af7207ea052f58ec81b99f61a60b1b3b11bd89269c46c00ab9851"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "7578f91add8a80e143d07099c7b57ad5de104bc90d45cba22abaa1870d9c7602"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "1657e8e7bc1f323cfee0617fc6813e824552925994d4fcefda009e07bb7dd92e",
    "phase_input_digest_sha256": (
        "5faed48213cb00e7ffcca461bdacc4f1d3844b950e0b64061819c4293eb8fc9c"
    ),
    "allocation_digest_sha256": (
        "7e8542e435b805ce57469dc518630ba586bfcea8d5e93c91063d9d1a1e785cb5"
    ),
    "phase_comparison_digest_sha256": (
        "561c6fc9d972e72daed348f65acec4aac1c789b7340ce563fb6f5c06a07dfbc6"
    ),
    "result_digest_sha256": "f076b52d165179aaca0011c19c31f5bbdd0fdd1201951fe5a418e02d65e04d6a",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "2bb91dfa45419c1edd192dab1cdaea9bd266aff828d9ea70617bd0245ab6ff50"
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
def q011mt_structure() -> dict[str, Any]:
    sealed, artifacts = q011mt._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011mt._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011mt._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011mt_study() -> dict[str, Any]:
    return q011mt.run_q011mt_study()


@pytest.fixture(scope="module")
def q011mt_cycle(q011mt_study: dict[str, Any]) -> dict[str, Any]:
    return q011mt_study["cycle"]


def test_q011mt_seals_q011ms_and_all_prior_inputs(
    q011mt_structure: dict[str, Any],
) -> None:
    sealed = q011mt_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 336
    assert sealed["direct_digest_count"] == 1_524
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ms"]["digests"]) == q011mt.Q011MS_DIGESTS
    assert sealed["q011ms"]["artifact_sha256"] == q011mt.Q011MS_ARTIFACT_SHA256
    assert sealed["q011ms"]["runner_sha256"] == q011mt.Q011MS_RUNNER_SHA256


def test_q011mt_reconstructs_component_safe_phase_discs(
    q011mt_structure: dict[str, Any],
) -> None:
    fixed = q011mt_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 138
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011mt.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011mt.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011mt.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011mt.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ms_compatible_wave_allocation_count"] == 3_727
    assert fixed["q011ms_compatible_wave_allocation_digest_sha256"] == (
        q011mt.q011ms.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011mt._protocol_globals_are_restored()


def test_q011mt_enumerates_registered_label_free_phase_inventory(
    q011mt_structure: dict[str, Any],
) -> None:
    allocation = q011mt_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == q011mt.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011mt.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011mt.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011mt.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 3_727
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011mt.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 321,
        "2": 311,
        "3": 928,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011mt.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011mt.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011mt_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_thirty_eight_active_totals"] == [1, 12, 9, 5, 2, 5]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mt result is not sealed")
def test_q011mt_classifies_all_complex_phase_product_discs(
    q011mt_cycle: dict[str, Any],
) -> None:
    comparison = q011mt_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011mt-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mt result is not sealed")
def test_q011mt_minimum_exact_phase_margin_is_fixed(
    q011mt_cycle: dict[str, Any],
) -> None:
    witness = q011mt_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mt result is not sealed")
def test_q011mt_applies_stopping_rule_and_preserves_boundary(
    q011mt_cycle: dict[str, Any],
) -> None:
    assert q011mt_cycle["study_validity"] == "passed"
    assert q011mt_cycle["failed_validity_order"] == []
    assert q011mt_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mt_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mt_cycle["diagnostic_gates"].values())
    assert q011mt_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mt_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mt_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011mt.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011mt.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mt_cycle["diagnostic_classification"] == expected
    theorem = q011mt_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_thirty_ninth_q011cb_witness"
        ],
        theorem[
            "one_hundred_thirty_ninth_q011cb_witness_persists_under_component_safe_phase_discs"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011ms_ordinal_one_hundred_thirty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mr_ordinal_one_hundred_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 138" in q011mt_cycle["claim_boundary"]
    assert "ordinals 0 through 137" in q011mt_cycle["claim_boundary"]
    assert "later 44661 Q011cb refined signatures" in q011mt_cycle["claim_boundary"]
    assert "Q011mu" in q011mt_cycle["next_change"]
    assert {name: q011mt_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mt_cycle["result_digest_sha256"] == (
        q011mt.q011b._canonical_json_sha256(q011mt._result_digest_sections(q011mt_cycle))
    )
    assert q011mt._protocol_globals_are_restored()
    json.dumps(q011mt_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mt result is not sealed")
def test_q011mt_study_metadata_and_optional_artifact_are_scoped(
    q011mt_study: dict[str, Any],
) -> None:
    assert q011mt_study["schema_version"] == 1
    assert q011mt_study["source"] == source_metadata()
    assert q011mt_study["study_gate"] == "passed"
    assert q011mt_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mt_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mt_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 138
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mt_study, allow_nan=False)

    runner_path = Path(q011mt.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mt_degree34_one_hundred_thirty_ninth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mt artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mt_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mt.q011b._canonical_json_sha256(q011mt._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
