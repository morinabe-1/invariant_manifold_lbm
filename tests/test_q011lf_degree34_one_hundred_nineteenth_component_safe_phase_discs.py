from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011lf_degree34_one_hundred_nineteenth_component_safe_phase_discs as q011lf
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "1cb1c355f3fa79d94dbace3bed1a800e4a3390035e1fcccda300b41ab15e3d68"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8dcfd20aaa97e5e3835cb19c9b1240a2b732ff5f082d89de28176631e6ec7ee7"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "19c1dfae017cbc40ee897a735ba521bdbc156f302964839ed788fbe813e785a5",
    "phase_input_digest_sha256": "8b675e9b75c6952571115b65e8f547dba65a2d97967086d6598daec781c53261",
    "allocation_digest_sha256": "1425148083f01464ddce03cc05d04fe26610a3256a3bb6f24f27b2a889b29be9",
    "phase_comparison_digest_sha256": "f0f5bf1b0043794c8069e5abc7e39dcf7ac2232ccc587f40bcac9351b763ce32",
    "result_digest_sha256": "91ae132ffd1b2c183b90691738393ac969ad4a2d29368e6896f5b8f5e14b4e3b",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "137f3356e4c168f9a42dd465036892bffe40025f45f32405ac9ae6c1a99900b7"
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
def q011lf_structure() -> dict[str, Any]:
    sealed, artifacts = q011lf._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011lf._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011lf._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011lf_study() -> dict[str, Any]:
    return q011lf.run_q011lf_study()


@pytest.fixture(scope="module")
def q011lf_cycle(q011lf_study: dict[str, Any]) -> dict[str, Any]:
    return q011lf_study["cycle"]


def test_q011lf_seals_q011le_and_all_prior_inputs(
    q011lf_structure: dict[str, Any],
) -> None:
    sealed = q011lf_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 296
    assert sealed["direct_digest_count"] == 1_344
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011le"]["digests"]) == q011lf.Q011LE_DIGESTS
    assert sealed["q011le"]["artifact_sha256"] == q011lf.Q011LE_ARTIFACT_SHA256
    assert sealed["q011le"]["runner_sha256"] == q011lf.Q011LE_RUNNER_SHA256


def test_q011lf_reconstructs_component_safe_phase_discs(
    q011lf_structure: dict[str, Any],
) -> None:
    fixed = q011lf_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 118
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011lf.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011lf.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011lf.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011lf.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011le_compatible_wave_allocation_count"] == 3_626
    assert fixed["q011le_compatible_wave_allocation_digest_sha256"] == (
        q011lf.q011le.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011lf._protocol_globals_are_restored()


def test_q011lf_enumerates_registered_label_free_phase_inventory(
    q011lf_structure: dict[str, Any],
) -> None:
    allocation = q011lf_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == q011lf.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011lf.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011lf.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011lf.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 3_626
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011lf.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 253,
        "2": 245,
        "3": 241,
        "4": 240,
        "5": 240,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011lf.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011lf.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011lf_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_eighteen_active_totals"] == [1, 12, 9, 5, 6, 1]
    assert adapter["inactive_zero_power_totals"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lf result is not sealed")
def test_q011lf_classifies_all_complex_phase_product_discs(
    q011lf_cycle: dict[str, Any],
) -> None:
    comparison = q011lf_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011lf-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lf result is not sealed")
def test_q011lf_minimum_exact_phase_margin_is_fixed(
    q011lf_cycle: dict[str, Any],
) -> None:
    witness = q011lf_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lf result is not sealed")
def test_q011lf_applies_stopping_rule_and_preserves_boundary(
    q011lf_cycle: dict[str, Any],
) -> None:
    assert q011lf_cycle["study_validity"] == "passed"
    assert q011lf_cycle["failed_validity_order"] == []
    assert q011lf_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011lf_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011lf_cycle["diagnostic_gates"].values())
    assert q011lf_cycle["scientific_outcome"] == "not_evaluated"
    assert q011lf_cycle["actual_resonance_outcome"] == "not_established"
    assert q011lf_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011lf.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011lf.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011lf_cycle["diagnostic_classification"] == expected
    theorem = q011lf_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_one_hundred_nineteenth_q011cb_witness"],
        theorem["one_hundred_nineteenth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011le_ordinal_one_hundred_eighteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ld_ordinal_one_hundred_seventeen_phase_resolution_is_preserved"]
    assert theorem["q011kz_ordinal_one_hundred_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011kv_ordinal_one_hundred_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011kt_ordinal_one_hundred_twelve_phase_resolution_is_preserved"]
    assert theorem["q011jz_ordinal_one_hundred_two_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 118" in q011lf_cycle["claim_boundary"]
    assert "ordinals 0 through 117" in q011lf_cycle["claim_boundary"]
    assert "later 44681 Q011cb refined signatures" in q011lf_cycle["claim_boundary"]
    assert "Q011lg" in q011lf_cycle["next_change"]
    assert {name: q011lf_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011lf_cycle["result_digest_sha256"] == (
        q011lf.q011b._canonical_json_sha256(q011lf._result_digest_sections(q011lf_cycle))
    )
    assert q011lf._protocol_globals_are_restored()
    json.dumps(q011lf_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lf result is not sealed")
def test_q011lf_study_metadata_and_optional_artifact_are_scoped(
    q011lf_study: dict[str, Any],
) -> None:
    assert q011lf_study["schema_version"] == 1
    assert q011lf_study["source"] == source_metadata()
    assert q011lf_study["study_gate"] == "passed"
    assert q011lf_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011lf_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011lf_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 118
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011lf_study, allow_nan=False)

    runner_path = Path(q011lf.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011lf_degree34_one_hundred_nineteenth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011lf artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011lf_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011lf.q011b._canonical_json_sha256(q011lf._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
