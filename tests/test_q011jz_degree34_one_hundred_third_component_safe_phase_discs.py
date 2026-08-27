from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jz_degree34_one_hundred_third_component_safe_phase_discs as q011jz
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "c4b93cad997de7efd8dba05026be0988f43042d40ad5817c2df9e53bc422daa9"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "75519ae59521404eb959d96e081c6c858a52b436b55307efff7627fe0bb842e3"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "703c60cb4b32167c5040faa6505e2474f3920087ee8c43621806ce70897b59cf",
    "phase_input_digest_sha256": (
        "77a1339e491f13bcf91f17abbefcf9ba911c4e64f12fc4c41f2aadfda4c1a3a1"
    ),
    "allocation_digest_sha256": (
        "31206726d46eab501d20bad124f4b3dfe91e4306661582000f054eedb9b89c24"
    ),
    "phase_comparison_digest_sha256": (
        "a643bc725692ef0a5210b122dd58648ab9c003143fb9cf0daa8d6e9f5941be13"
    ),
    "result_digest_sha256": "3535d520c5b97ef43e1be31137d3ea1e9b03ec5329ff0fe01e551b1926113cc2",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "7f5b6e959ed5771a00f729bbcbef31cfc255eb661f6f68bbdbcac334ffe35bf1"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "d16bd69692ef992ecc675d954307992f26d80c0cacc57e0fa3a33053e4a3fd2c"
)
EXPECTED_MINIMUM_INDEX: int | None = 7_329
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 6, 0, 3, 0, 5, 5, 1, 1, 0]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc88eep-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 26_644,
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
def q011jz_structure() -> dict[str, Any]:
    sealed, artifacts = q011jz._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011jz._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011jz._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011jz_study() -> dict[str, Any]:
    return q011jz.run_q011jz_study()


@pytest.fixture(scope="module")
def q011jz_cycle(q011jz_study: dict[str, Any]) -> dict[str, Any]:
    return q011jz_study["cycle"]


def test_q011jz_seals_q011jy_and_all_prior_inputs(
    q011jz_structure: dict[str, Any],
) -> None:
    sealed = q011jz_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 264
    assert sealed["direct_digest_count"] == 1_200
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jy"]["digests"]) == q011jz.Q011JY_DIGESTS
    assert sealed["q011jy"]["artifact_sha256"] == q011jz.Q011JY_ARTIFACT_SHA256
    assert sealed["q011jy"]["runner_sha256"] == q011jz.Q011JY_RUNNER_SHA256


def test_q011jz_reconstructs_component_safe_phase_discs(
    q011jz_structure: dict[str, Any],
) -> None:
    fixed = q011jz_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 102
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011jz.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011jz.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011jz.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011jz.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011jy_compatible_wave_allocation_count"] == 2_906
    assert fixed["q011jy_compatible_wave_allocation_digest_sha256"] == (
        q011jz.q011jy.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011jz._protocol_globals_are_restored()


def test_q011jz_enumerates_registered_label_free_phase_inventory(
    q011jz_structure: dict[str, Any],
) -> None:
    allocation = q011jz_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == q011jz.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011jz.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011jz.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011jz.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 2_906
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011jz.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 253,
        "2": 245,
        "3": 721,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011jz.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011jz.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011jz_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_two_active_totals"] == [1, 12, 9, 5, 6, 1]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jz result is not sealed")
def test_q011jz_classifies_all_complex_phase_product_discs(
    q011jz_cycle: dict[str, Any],
) -> None:
    comparison = q011jz_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011jz-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jz result is not sealed")
def test_q011jz_minimum_exact_phase_margin_is_fixed(
    q011jz_cycle: dict[str, Any],
) -> None:
    witness = q011jz_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jz result is not sealed")
def test_q011jz_applies_stopping_rule_and_preserves_boundary(
    q011jz_cycle: dict[str, Any],
) -> None:
    assert q011jz_cycle["study_validity"] == "passed"
    assert q011jz_cycle["failed_validity_order"] == []
    assert q011jz_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jz_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jz_cycle["diagnostic_gates"].values())
    assert q011jz_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jz_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jz_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011jz.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011jz.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jz_cycle["diagnostic_classification"] == expected
    theorem = q011jz_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_one_hundred_third_q011cb_witness"],
        theorem["one_hundred_third_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011jy_ordinal_one_hundred_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jx_ordinal_one_hundred_one_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 102" in q011jz_cycle["claim_boundary"]
    assert "ordinals 0 through 101" in q011jz_cycle["claim_boundary"]
    assert "later 44697 Q011cb refined signatures" in q011jz_cycle["claim_boundary"]
    assert "Q011ka" in q011jz_cycle["next_change"]
    assert {name: q011jz_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jz_cycle["result_digest_sha256"] == (
        q011jz.q011b._canonical_json_sha256(q011jz._result_digest_sections(q011jz_cycle))
    )
    assert q011jz._protocol_globals_are_restored()
    json.dumps(q011jz_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jz result is not sealed")
def test_q011jz_study_metadata_and_optional_artifact_are_scoped(
    q011jz_study: dict[str, Any],
) -> None:
    assert q011jz_study["schema_version"] == 1
    assert q011jz_study["source"] == source_metadata()
    assert q011jz_study["study_gate"] == "passed"
    assert q011jz_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jz_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jz_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 102
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jz_study, allow_nan=False)

    runner_path = Path(q011jz.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jz_degree34_one_hundred_third_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jz artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jz_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jz.q011b._canonical_json_sha256(q011jz._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
