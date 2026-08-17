from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ct_degree34_ninth_component_safe_phase_discs as q011ct
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "ac486e1e32f5daad08bcd5e855c83601b0c8acb514c2c72ffe169f22764cf9c4"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "9ee6ca2aba63b0de57a326e626ab35bf4946a428b35b0184d641d0438dc34cfd",
    "phase_input_digest_sha256": (
        "b84c921032c0e2f364f0e17a0d876b5ce15190c356989f807255ac939acd822a"
    ),
    "allocation_digest_sha256": (
        "21794f52585eda6ccd748150c48595dc19c837f4f84cfce41e7d0f363354751b"
    ),
    "phase_comparison_digest_sha256": (
        "f2aca9a81fc184383cd757f9acb73a2eba50f303166bf303c6019d8bf796543b"
    ),
    "result_digest_sha256": "c122666108c78bd00be10f8e554ca2b0b63e94546916198960ec5c07e411ff9f",
}
EXPECTED_STREAM_DIGEST = "42fde0ab68b6552b19415aca917d295271815fe8c176ffc26e4d55a938cef790"
EXPECTED_MINIMUM_WITNESS_DIGEST = "0608c0d35f60903eea1f58ee9ea5f3f8fef345e97babcf53abee39f14fa1aa0d"


@pytest.fixture(scope="module")
def q011ct_study() -> dict[str, Any]:
    return q011ct.run_q011ct_study()


@pytest.fixture(scope="module")
def q011ct_cycle(q011ct_study: dict[str, Any]) -> dict[str, Any]:
    return q011ct_study["cycle"]


def test_q011ct_seals_q011cs_and_all_prior_inputs(
    q011ct_cycle: dict[str, Any],
) -> None:
    sealed = q011ct_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 76
    assert sealed["direct_digest_count"] == 354
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cs"]["digests"]) == q011ct.Q011CS_DIGESTS
    assert sealed["q011cs"]["artifact_sha256"] == q011ct.Q011CS_ARTIFACT_SHA256
    assert sealed["q011cs"]["runner_sha256"] == q011ct.Q011CS_RUNNER_SHA256


def test_q011ct_reconstructs_component_safe_phase_discs(
    q011ct_cycle: dict[str, Any],
) -> None:
    fixed = q011ct_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 8
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ct.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ct.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011ct.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011ct.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cs_compatible_wave_allocation_count"] == 685
    assert fixed["q011cs_compatible_wave_allocation_digest_sha256"] == (
        q011ct.q011cs.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ct._protocol_globals_are_restored()


def test_q011ct_enumerates_registered_label_free_phase_inventory(
    q011ct_cycle: dict[str, Any],
) -> None:
    allocation = q011ct_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011ct.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ct.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [
        0,
        13,
        0,
        0,
        0,
        9,
        0,
        5,
        0,
        0,
        5,
        2,
    ]
    assert allocation["last_compatible_counts"] == [
        13,
        0,
        9,
        0,
        0,
        0,
        0,
        5,
        0,
        0,
        0,
        7,
    ]
    assert allocation["individual_wave_allocation_count"] == 685
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ct.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 303,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 685
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ct.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ct.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False


def test_q011ct_certifies_all_complex_phase_product_discs(
    q011ct_cycle: dict[str, Any],
) -> None:
    comparison = q011ct_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 8
    assert comparison["compatible_phase_allocation_count"] == 8_350
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 8_350,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 8_350,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 8_350
    assert comparison["comparison_stream_domain"] == ("q011ct-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011ct_minimum_exact_phase_margin_is_fixed(
    q011ct_cycle: dict[str, Any],
) -> None:
    comparison = q011ct_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 5_455
    assert witness["counts"] == [11, 2, 0, 9, 0, 0, 0, 5, 0, 0, 2, 5]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8463p-6")
    assert q011ct.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ct_records_scoped_resolution(q011ct_cycle: dict[str, Any]) -> None:
    assert q011ct_cycle["study_validity"] == "passed"
    assert q011ct_cycle["failed_validity_order"] == []
    assert q011ct_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ct_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ct_cycle["diagnostic_gates"].values())
    assert q011ct_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ct_cycle["diagnostic_classification"] == q011ct.RESOLVED_CLASSIFICATION
    assert q011ct_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ct_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011cu" in q011ct_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011ct_cycle["next_change"]


def test_q011ct_preserves_scientific_boundary(q011ct_cycle: dict[str, Any]) -> None:
    theorem = q011ct_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_ninth_q011cb_witness"]
    assert not theorem["ninth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cs_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cr_ordinal_seven_phase_resolution_is_preserved"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert theorem["q011ch_ordinal_two_phase_resolution_is_preserved"]
    assert theorem["q011cf_ordinal_one_phase_resolution_is_preserved"]
    assert theorem["q011cd_ordinal_zero_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 8" in q011ct_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 7" in q011ct_cycle["claim_boundary"]
    assert "later 44791 Q011cb refined signatures" in q011ct_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ct_cycle["claim_boundary"]


def test_q011ct_cycle_has_strict_reproducible_digests(
    q011ct_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ct_cycle, allow_nan=False)
    assert {
        name: q011ct_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011ct_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ct_cycle["result_digest_sha256"] == (
        q011ct.q011b._canonical_json_sha256(q011ct._result_digest_sections(q011ct_cycle))
    )
    assert q011ct._protocol_globals_are_restored()


def test_q011ct_study_metadata_and_optional_artifact_are_scoped(
    q011ct_study: dict[str, Any],
) -> None:
    assert q011ct_study["schema_version"] == 1
    assert q011ct_study["source"] == source_metadata()
    assert q011ct_study["study_gate"] == "passed"
    assert q011ct_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ct_study["scientific_outcome"] == "not_evaluated"
    assert q011ct_study["actual_resonance_outcome"] == "not_established"
    runtime = q011ct_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ct_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 8
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ct_study, allow_nan=False)

    runner_path = Path(q011ct.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / ("q011ct_degree34_ninth_component_safe_phase_discs.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011ct artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011ct_degree34_ninth_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ct.q011b._canonical_json_sha256(q011ct._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
