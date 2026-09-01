from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011nd_degree34_one_hundred_forty_fourth_component_safe_phase_discs as q011nd
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "739242cf7319818f54bfbc1b71a4ebf688fd2ce07ff622c505bde52931c6a49a"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "530191ecd05f1b8d7e56e0431c06c536ee27e38332023ea5b8d10caff5c52410"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "adf0feed3dc29c96c65bbe805c0ed52a621e509442ccb38bb82e3e8fca5d956c",
    "phase_input_digest_sha256": (
        "c945b9d578e8a21d071d839ba2fc6bd9b2e66e7f80dd16527947c4694684dce8"
    ),
    "allocation_digest_sha256": (
        "416af7178c001c913c4cb3a09b1d0b32c1349d81b5f7d2fc7460ab3df4ac95c1"
    ),
    "phase_comparison_digest_sha256": (
        "d908faa1183d5b7e6a901658e0c22d63d938d1304f0e537dbbf6ba37a4b9c133"
    ),
    "result_digest_sha256": "84f95a6f365b83f3c7f615312cfa42b22c0aca951d5ec28fdeeeaa7653825522",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "12bf0b57ebf63bf48f83a262abdcfff7e5857a40eed3cbdec3304f2955905abc"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "cba06ceb15335a288a1ea6e0d24caf4f450a26e54b3b51f5e46e84b7526d6868"
)
EXPECTED_MINIMUM_INDEX: int | None = 4_390
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 7, 0, 2, 0, 5, 5, 2, 0, 0]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8a74p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 15_278,
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
def q011nd_structure() -> dict[str, Any]:
    sealed, artifacts = q011nd._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011nd._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011nd._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011nd_study() -> dict[str, Any]:
    return q011nd.run_q011nd_study()


@pytest.fixture(scope="module")
def q011nd_cycle(q011nd_study: dict[str, Any]) -> dict[str, Any]:
    return q011nd_study["cycle"]


def test_q011nd_seals_q011nc_and_all_prior_inputs(
    q011nd_structure: dict[str, Any],
) -> None:
    sealed = q011nd_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 346
    assert sealed["direct_digest_count"] == 1_569
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011nc"]["digests"]) == q011nd.Q011NC_DIGESTS
    assert sealed["q011nc"]["artifact_sha256"] == q011nd.Q011NC_ARTIFACT_SHA256
    assert sealed["q011nc"]["runner_sha256"] == q011nd.Q011NC_RUNNER_SHA256
    repeated, repeated_artifacts = q011nd._sealed_input_audit()
    parent, parent_artifacts = q011nd.q011nc._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 346
    assert len(repeated_artifacts) == 346
    assert parent["passed"] and parent["artifact_count"] == 345
    assert len(parent_artifacts) == 345


def test_q011nd_reconstructs_component_safe_phase_discs(
    q011nd_structure: dict[str, Any],
) -> None:
    fixed = q011nd_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 143
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 12
    assert fixed["inactive_zero_power_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert q011nd.SOURCE_POWER_MAXIMUM_COUNTS[12:14] == (0, 0)
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011nd.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011nd.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011nd.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011nd.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011nc_compatible_wave_allocation_count"] == 1_667
    assert fixed["q011nc_compatible_wave_allocation_digest_sha256"] == (
        q011nd.q011nc.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011nd._protocol_globals_are_restored()


def test_q011nd_enumerates_registered_label_free_phase_inventory(
    q011nd_structure: dict[str, Any],
) -> None:
    allocation = q011nd_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 274_560
    assert allocation["full_allocation_digest_sha256"] == q011nd.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 15_278
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011nd.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011nd.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011nd.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 1_667
    assert allocation["component_wave_projection_count"] == 701
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011nd.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 147,
        "2": 142,
        "3": 412,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011nd.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 701
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011nd.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 147,
        "18": 142,
        "24": 139,
        "28": 137,
        "30": 136,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 15_278
    )
    assert q011nd_structure["compatible_count"] == 15_278
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_forty_three_active_totals"] == [1, 12, 9, 5, 7]
    assert adapter["canonical_zero_power_indices"] == [12, 13]
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nd result is not sealed")
def test_q011nd_classifies_all_complex_phase_product_discs(
    q011nd_cycle: dict[str, Any],
) -> None:
    comparison = q011nd_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 15_278
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 15_278
    assert comparison["comparison_stream_count"] == 15_278
    assert comparison["comparison_stream_domain"] == ("q011nd-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 15_278,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nd result is not sealed")
def test_q011nd_minimum_exact_phase_margin_is_fixed(
    q011nd_cycle: dict[str, Any],
) -> None:
    witness = q011nd_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nd result is not sealed")
def test_q011nd_applies_stopping_rule_and_preserves_boundary(
    q011nd_cycle: dict[str, Any],
) -> None:
    assert q011nd_cycle["study_validity"] == "passed"
    assert q011nd_cycle["failed_validity_order"] == []
    assert q011nd_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011nd_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011nd_cycle["diagnostic_gates"].values())
    assert q011nd_cycle["scientific_outcome"] == "not_evaluated"
    assert q011nd_cycle["actual_resonance_outcome"] == "not_established"
    assert q011nd_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011nd.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011nd.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011nd_cycle["diagnostic_classification"] == expected
    theorem = q011nd_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_forty_fourth_q011cb_witness"
        ],
        theorem["one_hundred_forty_fourth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011nc_ordinal_one_hundred_forty_three_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 143" in q011nd_cycle["claim_boundary"]
    assert "ordinals 0 through 142" in q011nd_cycle["claim_boundary"]
    assert "later 44656 Q011cb refined signatures" in q011nd_cycle["claim_boundary"]
    assert "Q011ne" in q011nd_cycle["next_change"]
    assert {name: q011nd_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011nd_cycle["result_digest_sha256"] == (
        q011nd.q011b._canonical_json_sha256(q011nd._result_digest_sections(q011nd_cycle))
    )
    assert q011nd._protocol_globals_are_restored()
    json.dumps(q011nd_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nd result is not sealed")
def test_q011nd_study_metadata_and_optional_artifact_are_scoped(
    q011nd_study: dict[str, Any],
) -> None:
    assert q011nd_study["schema_version"] == 1
    assert q011nd_study["source"] == source_metadata()
    assert q011nd_study["study_gate"] == "passed"
    assert q011nd_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011nd_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 15_278
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011nd_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 143
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011nd_study, allow_nan=False)

    runner_path = Path(q011nd.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011nd_degree34_one_hundred_forty_fourth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011nd artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011nd_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011nd.q011b._canonical_json_sha256(q011nd._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
