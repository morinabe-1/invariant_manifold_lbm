from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cx_degree34_eleventh_component_safe_phase_discs as q011cx
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "c0f599af9e873e8a17e44eecd74de0e4765c35a02b177c14f7f86dd388566c11"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "0ec1b9ac8a32a7952a3fe6362b2842de489d7d416c540b82127902d08dd6062b"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "6aa64d524e0d4e415ac3e4ce274bd8f5f5148b56799a6eda9859b59af3d1eaa3",
    "phase_input_digest_sha256": (
        "ea5033fb9d5e1ce850afc545587caadd909a925b6458b3c4c10a607310cb3257"
    ),
    "allocation_digest_sha256": (
        "8ff676de72da7d00b19a40b30d809014fa3f2d4bd5e6d799c6fa0359fc11abdc"
    ),
    "phase_comparison_digest_sha256": (
        "05c4e2a4c9a62caaa083790416f468ffc81cf10fa52815e14f9d9feb860023f1"
    ),
    "result_digest_sha256": "d9f73a50463e117521ed7da2b531333db015d9672265f7f8c7d0e58571a5fb47",
}
EXPECTED_STREAM_DIGEST = "2c0339e4a7ae797d9fcdc0b154cc07d8f9fcfb7fc7199e2190b1fc7e192bdabf"
EXPECTED_MINIMUM_WITNESS_DIGEST = "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"


@pytest.fixture(scope="module")
def q011cx_study() -> dict[str, Any]:
    return q011cx.run_q011cx_study()


@pytest.fixture(scope="module")
def q011cx_cycle(q011cx_study: dict[str, Any]) -> dict[str, Any]:
    return q011cx_study["cycle"]


def test_q011cx_seals_q011cw_and_all_prior_inputs(
    q011cx_cycle: dict[str, Any],
) -> None:
    sealed = q011cx_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 80
    assert sealed["direct_digest_count"] == 372
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cw"]["digests"]) == q011cx.Q011CW_DIGESTS
    assert sealed["q011cw"]["artifact_sha256"] == q011cx.Q011CW_ARTIFACT_SHA256
    assert sealed["q011cw"]["runner_sha256"] == q011cx.Q011CW_RUNNER_SHA256


def test_q011cx_reconstructs_component_safe_phase_discs(
    q011cx_cycle: dict[str, Any],
) -> None:
    fixed = q011cx_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 10
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cx.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cx.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011cx.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011cx.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cw_compatible_wave_allocation_count"] == 1_531
    assert fixed["q011cw_compatible_wave_allocation_digest_sha256"] == (
        q011cx.q011cw.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cx._protocol_globals_are_restored()


def test_q011cx_enumerates_registered_label_free_phase_inventory(
    q011cx_cycle: dict[str, Any],
) -> None:
    allocation = q011cx_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == (q011cx.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cx.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        2,
        5,
        0,
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
        2,
        0,
        5,
    ]
    assert allocation["individual_wave_allocation_count"] == 1_531
    assert allocation["component_wave_projection_count"] == 852
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011cx.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 173,
        "2": 679,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_531
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011cx.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cx.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 173,
        "18": 169,
        "24": 169,
        "28": 170,
        "30": 171,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 18_718
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    assert allocation["allocation_protocol_adapter"]["protocol_globals_modified"] is False


def test_q011cx_certifies_all_complex_phase_product_discs(
    q011cx_cycle: dict[str, Any],
) -> None:
    comparison = q011cx_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 10
    assert comparison["compatible_phase_allocation_count"] == 18_718
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 18_718,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 18_718,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 18_718
    assert comparison["comparison_stream_domain"] == ("q011cx-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cx_minimum_exact_phase_margin_is_fixed(
    q011cx_cycle: dict[str, Any],
) -> None:
    comparison = q011cx_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 11_706
    assert witness["counts"] == [11, 2, 0, 7, 0, 2, 0, 5, 2, 0, 2, 3]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8560p-6")
    assert q011cx.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cx_records_scoped_resolution(q011cx_cycle: dict[str, Any]) -> None:
    assert q011cx_cycle["study_validity"] == "passed"
    assert q011cx_cycle["failed_validity_order"] == []
    assert q011cx_cycle["failed_diagnostic_order"] == []
    assert len(q011cx_cycle["validity_gates"]) == 7
    assert len(q011cx_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011cx_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cx_cycle["diagnostic_gates"].values())
    assert q011cx_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cx_cycle["diagnostic_classification"] == q011cx.RESOLVED_CLASSIFICATION
    assert q011cx_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cx_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011cy" in q011cx_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cx_cycle["next_change"]


def test_q011cx_preserves_scientific_boundary(q011cx_cycle: dict[str, Any]) -> None:
    theorem = q011cx_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_eleventh_q011cb_witness"]
    assert not theorem["eleventh_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cw_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
    assert theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 10" in q011cx_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 9" in q011cx_cycle["claim_boundary"]
    assert "later 44789 Q011cb refined signatures" in q011cx_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cx_cycle["claim_boundary"]


def test_q011cx_cycle_has_strict_reproducible_digests(
    q011cx_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cx_cycle, allow_nan=False)
    assert {
        name: q011cx_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cx_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cx_cycle["result_digest_sha256"] == (
        q011cx.q011b._canonical_json_sha256(q011cx._result_digest_sections(q011cx_cycle))
    )
    assert q011cx._protocol_globals_are_restored()


def test_q011cx_study_metadata_and_optional_artifact_are_scoped(
    q011cx_study: dict[str, Any],
) -> None:
    assert q011cx_study["schema_version"] == 1
    assert q011cx_study["source"] == source_metadata()
    assert q011cx_study["study_gate"] == "passed"
    assert q011cx_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cx_study["scientific_outcome"] == "not_evaluated"
    assert q011cx_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cx_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cx_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 10
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cx_study, allow_nan=False)

    runner_path = Path(q011cx.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011cx_degree34_eleventh_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cx artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cx_degree34_eleventh_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cx.q011b._canonical_json_sha256(q011cx._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
