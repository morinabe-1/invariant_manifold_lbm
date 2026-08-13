from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cn_degree34_sixth_component_safe_phase_discs as q011cn
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "bc506ea76eefa4a84d2cf19c8f92b6fcd197c5a0ea28873c1d0eb4d51a3a6b6e"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "e8b714a50eedadd3a9ac8e5556586c95167573a51c853c5f491b4660112d80c3"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "07b46cf876293a6067a81d25b46a14cfe4e2a1a20f5ee223a2132fd6a4a7a87e",
    "phase_input_digest_sha256": (
        "e1cc6364bc6882c3d6768e0dea40de260e9b7a7142d563c9d25b501125fbbd15"
    ),
    "allocation_digest_sha256": (
        "18fbba9e20f12a0fbba3b3e6593cea3453079ab541753264d02eb6089692b17c"
    ),
    "phase_comparison_digest_sha256": (
        "7428c19a264f67bd134792b9d64b3ce621b3ca56356fe80a683f95ed05ea7b0f"
    ),
    "result_digest_sha256": "32b4a2e64fcf491c365814737e34ec716bc88c97655c42a532cc66b7ffebe8c7",
}
EXPECTED_STREAM_DIGEST = "9e2a0c5a47749cf103dcf3595aa043d522e14aaa70763bf5a412ba294a82858a"
EXPECTED_MINIMUM_WITNESS_DIGEST = (
    "514c3194347c4be6775cc7a53518fbee0c3d97586a962c6e2b63378ce8a8614f"
)


@pytest.fixture(scope="module")
def q011cn_study() -> dict[str, Any]:
    return q011cn.run_q011cn_study()


@pytest.fixture(scope="module")
def q011cn_cycle(q011cn_study: dict[str, Any]) -> dict[str, Any]:
    return q011cn_study["cycle"]


def test_q011cn_seals_q011cm_and_all_prior_inputs(
    q011cn_cycle: dict[str, Any],
) -> None:
    sealed = q011cn_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 70
    assert sealed["direct_digest_count"] == 327
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cm"]["digests"]) == q011cn.Q011CM_DIGESTS
    assert sealed["q011cm"]["artifact_sha256"] == q011cn.Q011CM_ARTIFACT_SHA256
    assert sealed["q011cm"]["runner_sha256"] == q011cn.Q011CM_RUNNER_SHA256


def test_q011cn_reconstructs_component_safe_phase_discs(
    q011cn_cycle: dict[str, Any],
) -> None:
    fixed = q011cn_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 5
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (
        q011cn.EXPECTED_SOURCE_RECORD_DIGEST
    )
    assert fixed["target_phase_disc_record_digest_sha256"] == (
        q011cn.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert tuple(fixed["source_radius_binary64_hex"]) == (
        q011cn.EXPECTED_SOURCE_RADIUS_HEX
    )
    assert fixed["target_radius_binary64_hex"] == q011cn.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cm_compatible_wave_allocation_count"] == 852
    assert fixed["q011cm_compatible_wave_allocation_digest_sha256"] == (
        q011cn.q011cm.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cn._protocol_globals_are_restored()


def test_q011cn_enumerates_registered_label_free_phase_inventory(
    q011cn_cycle: dict[str, Any],
) -> None:
    allocation = q011cn_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == (
        q011cn.EXPECTED_FULL_ALLOCATION_DIGEST
    )
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cn.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        3,
        2,
        2,
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
        5,
        0,
        2,
    ]
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cn.EXPECTED_WAVE_PROJECTION_DIGEST
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
        sum(
            record["phase_allocation_count"]
            for record in allocation["wave_projection_records"]
        )
        == 18_718
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False


def test_q011cn_certifies_all_complex_phase_product_discs(
    q011cn_cycle: dict[str, Any],
) -> None:
    comparison = q011cn_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 5
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
    assert comparison["comparison_stream_domain"] == (
        "q011cn-component-safe-phase-comparisons-v1"
    )
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cn_minimum_exact_phase_margin_is_fixed(
    q011cn_cycle: dict[str, Any],
) -> None:
    comparison = q011cn_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 11_474
    assert witness["counts"] == [11, 2, 0, 4, 0, 5, 0, 5, 5, 0, 2, 0]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        "0x1.a8f10a6dc86dap-6"
    )
    assert q011cn.q011z._fraction(
        witness["complex_separation_margin_lower"]["exact"]
    ) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cn_records_scoped_resolution(q011cn_cycle: dict[str, Any]) -> None:
    assert q011cn_cycle["study_validity"] == "passed"
    assert q011cn_cycle["failed_validity_order"] == []
    assert q011cn_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cn_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cn_cycle["diagnostic_gates"].values())
    assert q011cn_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cn_cycle["diagnostic_classification"] == q011cn.RESOLVED_CLASSIFICATION
    assert q011cn_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cn_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011co" in q011cn_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cn_cycle["next_change"]


def test_q011cn_preserves_scientific_boundary(q011cn_cycle: dict[str, Any]) -> None:
    theorem = q011cn_cycle["theorem_consequence"]
    assert theorem[
        "component_safe_complex_phase_discs_resolve_sixth_q011cb_witness"
    ]
    assert not theorem[
        "sixth_q011cb_witness_persists_under_component_safe_phase_discs"
    ]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cm_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert theorem["q011ch_ordinal_two_phase_resolution_is_preserved"]
    assert theorem["q011cf_ordinal_one_phase_resolution_is_preserved"]
    assert theorem["q011cd_ordinal_zero_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem[
        "an_actual_degree_thirty_four_external_resonance_is_established"
    ]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 5" in q011cn_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 4" in q011cn_cycle["claim_boundary"]
    assert "later 44794 Q011cb refined signatures" in q011cn_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cn_cycle["claim_boundary"]


def test_q011cn_cycle_has_strict_reproducible_digests(
    q011cn_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cn_cycle, allow_nan=False)
    assert {
        name: q011cn_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cn_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cn_cycle["result_digest_sha256"] == (
        q011cn.q011b._canonical_json_sha256(
            q011cn._result_digest_sections(q011cn_cycle)
        )
    )
    assert q011cn._protocol_globals_are_restored()


def test_q011cn_study_metadata_and_optional_artifact_are_scoped(
    q011cn_study: dict[str, Any],
) -> None:
    assert q011cn_study["schema_version"] == 1
    assert q011cn_study["source"] == source_metadata()
    assert q011cn_study["study_gate"] == "passed"
    assert q011cn_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cn_study["scientific_outcome"] == "not_evaluated"
    assert q011cn_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cn_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cn_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 5
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cn_study, allow_nan=False)

    runner_path = Path(q011cn.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011cn_degree34_sixth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cn artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cn_degree34_sixth_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cn.q011b._canonical_json_sha256(
            q011cn._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
