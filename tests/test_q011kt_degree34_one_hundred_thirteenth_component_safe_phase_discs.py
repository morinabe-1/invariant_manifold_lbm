from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011kt_degree34_one_hundred_thirteenth_component_safe_phase_discs as q011kt
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d7443d1fc6030bf80179cf14498e95ef2c014b03f83fa882ab3afe574c75f671"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "2cc51362c28ddd23eb46eadecd07970bc271fd3b85c6f014c83252fff31f7c45"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "990484d4a6c3eac99894714db05e8e8970e88af4424daae6fbdb61a20d2f6765",
    "phase_input_digest_sha256": (
        "d5f5e45cf4ad930c9b5cee4262cbfdaed8644f8db19735583faa398f305130fb"
    ),
    "allocation_digest_sha256": (
        "05338226164a5f8a5da394970abb09d1de8d02be9ab051ace71f8c9efce1e27c"
    ),
    "phase_comparison_digest_sha256": (
        "93f8ebd9035f85a709f78a4969b2347535fa17408eea8a72415ba55dc1b3dcb3"
    ),
    "result_digest_sha256": "290c84c5d5dde8f21c69613e9e8526de8ef6610765c9d617d8b76d437eb82d3e",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "948a2d6ae63642b5c42d9edc79fade869680793281776d7fc3a2312d75d10e60"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "e56c1012985dec3148f724f74f3a19f365a0766d6fbddcce1448ea1d4cbaf8cf"
)
EXPECTED_MINIMUM_INDEX: int | None = 4_419
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 9, 0, 0, 1, 4, 0, 0, 2, 5]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8516p-6"
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
def q011kt_structure() -> dict[str, Any]:
    sealed, artifacts = q011kt._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011kt._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011kt._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011kt_study() -> dict[str, Any]:
    return q011kt.run_q011kt_study()


@pytest.fixture(scope="module")
def q011kt_cycle(q011kt_study: dict[str, Any]) -> dict[str, Any]:
    return q011kt_study["cycle"]


def test_q011kt_seals_q011ks_and_all_prior_inputs(
    q011kt_structure: dict[str, Any],
) -> None:
    sealed = q011kt_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 284
    assert sealed["direct_digest_count"] == 1_290
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ks"]["digests"]) == q011kt.Q011KS_DIGESTS
    assert sealed["q011ks"]["artifact_sha256"] == q011kt.Q011KS_ARTIFACT_SHA256
    assert sealed["q011ks"]["runner_sha256"] == q011kt.Q011KS_RUNNER_SHA256


def test_q011kt_reconstructs_component_safe_phase_discs(
    q011kt_structure: dict[str, Any],
) -> None:
    fixed = q011kt_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 112
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 12
    assert fixed["inactive_zero_power_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    canonical_order = [record[0] for record in q011kt.SOURCE_VARIANTS]
    assert q011kt_structure["allocation"]["active_source_variant_order"] == [
        canonical_order[index] for index in q011kt.ACTIVE_SOURCE_INDICES
    ]
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011kt.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011kt.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011kt.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011kt.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ks_compatible_wave_allocation_count"] == 2_076
    assert fixed["q011ks_compatible_wave_allocation_digest_sha256"] == (
        q011kt.q011ks.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011kt._protocol_globals_are_restored()


def test_q011kt_enumerates_registered_label_free_phase_inventory(
    q011kt_structure: dict[str, Any],
) -> None:
    allocation = q011kt_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 274_560
    assert allocation["full_allocation_digest_sha256"] == q011kt.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 15_278
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011kt.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011kt.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011kt.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 2_076
    assert allocation["component_wave_projection_count"] == 701
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011kt.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 147,
        "2": 142,
        "3": 139,
        "4": 137,
        "5": 136,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011kt.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 701
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011kt.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011kt_structure["compatible_count"] == 15_278
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_twelve_active_totals"] == [1, 12, 9, 5, 7]
    assert adapter["canonical_zero_power_totals"] == [0, 0]
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kt result is not sealed")
def test_q011kt_classifies_all_complex_phase_product_discs(
    q011kt_cycle: dict[str, Any],
) -> None:
    comparison = q011kt_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 15_278
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 15_278
    assert comparison["comparison_stream_count"] == 15_278
    assert comparison["comparison_stream_domain"] == ("q011kt-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 15_278,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kt result is not sealed")
def test_q011kt_minimum_exact_phase_margin_is_fixed(
    q011kt_cycle: dict[str, Any],
) -> None:
    witness = q011kt_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kt result is not sealed")
def test_q011kt_applies_stopping_rule_and_preserves_boundary(
    q011kt_cycle: dict[str, Any],
) -> None:
    assert q011kt_cycle["study_validity"] == "passed"
    assert q011kt_cycle["failed_validity_order"] == []
    assert q011kt_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011kt_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011kt_cycle["diagnostic_gates"].values())
    assert q011kt_cycle["scientific_outcome"] == "not_evaluated"
    assert q011kt_cycle["actual_resonance_outcome"] == "not_established"
    assert q011kt_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011kt.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011kt.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011kt_cycle["diagnostic_classification"] == expected
    theorem = q011kt_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_one_hundred_thirteenth_q011cb_witness"],
        theorem["one_hundred_thirteenth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011ks_ordinal_one_hundred_twelve_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kp_ordinal_one_hundred_ten_phase_resolution_is_preserved"]
    assert theorem["q011ko_ordinal_one_hundred_ten_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ji_ordinal_ninety_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jh_ordinal_ninety_three_phase_resolution_is_preserved"]
    assert theorem["q011jg_ordinal_ninety_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jf_ordinal_ninety_two_phase_resolution_is_preserved"]
    assert theorem["q011je_ordinal_ninety_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jd_ordinal_ninety_one_phase_resolution_is_preserved"]
    assert theorem["q011jc_ordinal_ninety_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jb_ordinal_ninety_phase_resolution_is_preserved"]
    assert theorem["q011ja_ordinal_ninety_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011iz_ordinal_eighty_nine_phase_resolution_is_preserved"]
    assert theorem["q011iy_ordinal_eighty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ix_ordinal_eighty_eight_phase_resolution_is_preserved"]
    assert theorem["q011iw_ordinal_eighty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 112" in q011kt_cycle["claim_boundary"]
    assert "ordinals 0 through 111" in q011kt_cycle["claim_boundary"]
    assert "later 44687 Q011cb refined signatures" in q011kt_cycle["claim_boundary"]
    assert "Q011ku" in q011kt_cycle["next_change"]
    assert {name: q011kt_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011kt_cycle["result_digest_sha256"] == (
        q011kt.q011b._canonical_json_sha256(q011kt._result_digest_sections(q011kt_cycle))
    )
    assert q011kt._protocol_globals_are_restored()
    json.dumps(q011kt_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kt result is not sealed")
def test_q011kt_study_metadata_and_optional_artifact_are_scoped(
    q011kt_study: dict[str, Any],
) -> None:
    assert q011kt_study["schema_version"] == 1
    assert q011kt_study["source"] == source_metadata()
    assert q011kt_study["study_gate"] == "passed"
    assert q011kt_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011kt_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 15_278
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011kt_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 112
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011kt_study, allow_nan=False)

    runner_path = Path(q011kt.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011kt_degree34_one_hundred_thirteenth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011kt artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011kt_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011kt.q011b._canonical_json_sha256(q011kt._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
