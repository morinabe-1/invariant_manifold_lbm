from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cj_degree34_fourth_component_safe_phase_discs as q011cj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "28ec0986f7960a1f1fc200b2637d1a7fb6f4fbf6418655127df4d4a7e276eff5"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "d3ab02eba750af162063bf965070c507f91b935c6b75cc1c43aac0931219b229",
    "phase_input_digest_sha256": (
        "d4c887f40b560777b01d138bce3c00ead60c5bc95f96c951ceb37240f52205dc"
    ),
    "allocation_digest_sha256": (
        "054c4afbeb381805643a423e5fd076f03860e03e6baa4f6da9eb168532374b51"
    ),
    "phase_comparison_digest_sha256": (
        "393299a9d43545eedbb5466b4114094d50a6c9440d63db4d9e3177409480e17a"
    ),
    "result_digest_sha256": "ffc6753ac0bdca0caf08200e14dd3ae03f631de57746a38aee0f3b887120baa4",
}
EXPECTED_STREAM_DIGEST = "161e3be5a8ffa0a8b0dcc74a5c28ac0a56162769dcb25b70bd0af45682d4a7e0"
EXPECTED_MINIMUM_WITNESS_DIGEST = (
    "4d81a833f38342bf959039d0b9e3f85fd2fc2edae6f7fde6aa7fe9f8f46e3a71"
)


@pytest.fixture(scope="module")
def q011cj_study() -> dict[str, Any]:
    return q011cj.run_q011cj_study()


@pytest.fixture(scope="module")
def q011cj_cycle(q011cj_study: dict[str, Any]) -> dict[str, Any]:
    return q011cj_study["cycle"]


def test_q011cj_seals_q011ci_and_all_prior_inputs(
    q011cj_cycle: dict[str, Any],
) -> None:
    sealed = q011cj_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 66
    assert sealed["direct_digest_count"] == 309
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ci"]["digests"]) == q011cj.Q011CI_DIGESTS
    assert sealed["q011ci"]["artifact_sha256"] == q011cj.Q011CI_ARTIFACT_SHA256
    assert sealed["q011ci"]["runner_sha256"] == q011cj.Q011CI_RUNNER_SHA256


def test_q011cj_reconstructs_component_safe_phase_discs(
    q011cj_cycle: dict[str, Any],
) -> None:
    fixed = q011cj_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 3
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (
        q011cj.EXPECTED_SOURCE_RECORD_DIGEST
    )
    assert fixed["target_phase_disc_record_digest_sha256"] == (
        q011cj.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert tuple(fixed["source_radius_binary64_hex"]) == (
        q011cj.EXPECTED_SOURCE_RADIUS_HEX
    )
    assert fixed["target_radius_binary64_hex"] == q011cj.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ci_compatible_wave_allocation_count"] == 945
    assert fixed["q011ci_compatible_wave_allocation_digest_sha256"] == (
        q011cj.q011ci.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cj._protocol_globals_are_restored()


def test_q011cj_enumerates_registered_label_free_phase_inventory(
    q011cj_cycle: dict[str, Any],
) -> None:
    allocation = q011cj_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == (
        q011cj.EXPECTED_FULL_ALLOCATION_DIGEST
    )
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cj.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        1,
        2,
        4,
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
        3,
        0,
        4,
    ]
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cj.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 191,
        "18": 187,
        "24": 187,
        "28": 189,
        "30": 191,
    }
    assert (
        sum(
            record["phase_allocation_count"]
            for record in allocation["wave_projection_records"]
        )
        == 20_786
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False


def test_q011cj_certifies_all_complex_phase_product_discs(
    q011cj_cycle: dict[str, Any],
) -> None:
    comparison = q011cj_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 3
    assert comparison["compatible_phase_allocation_count"] == 20_786
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 20_786,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 20_786,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 20_786
    assert comparison["comparison_stream_domain"] == (
        "q011cj-component-safe-phase-comparisons-v1"
    )
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cj_minimum_exact_phase_margin_is_fixed(
    q011cj_cycle: dict[str, Any],
) -> None:
    comparison = q011cj_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 12_816
    assert witness["counts"] == [11, 2, 0, 6, 0, 3, 0, 5, 3, 0, 2, 2]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        "0x1.a8f10a6dc85dep-6"
    )
    assert q011cj.q011z._fraction(
        witness["complex_separation_margin_lower"]["exact"]
    ) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cj_records_scoped_resolution(q011cj_cycle: dict[str, Any]) -> None:
    assert q011cj_cycle["study_validity"] == "passed"
    assert q011cj_cycle["failed_validity_order"] == []
    assert q011cj_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cj_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cj_cycle["diagnostic_gates"].values())
    assert q011cj_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cj_cycle["diagnostic_classification"] == q011cj.RESOLVED_CLASSIFICATION
    assert q011cj_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cj_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ck" in q011cj_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cj_cycle["next_change"]


def test_q011cj_preserves_scientific_boundary(q011cj_cycle: dict[str, Any]) -> None:
    theorem = q011cj_cycle["theorem_consequence"]
    assert theorem[
        "component_safe_complex_phase_discs_resolve_fourth_q011cb_witness"
    ]
    assert not theorem[
        "fourth_q011cb_witness_persists_under_component_safe_phase_discs"
    ]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011ci_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 3" in q011cj_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 2" in q011cj_cycle["claim_boundary"]
    assert "later 44796 Q011cb refined signatures" in q011cj_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cj_cycle["claim_boundary"]


def test_q011cj_cycle_has_strict_reproducible_digests(
    q011cj_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cj_cycle, allow_nan=False)
    assert {
        name: q011cj_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cj_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cj_cycle["result_digest_sha256"] == (
        q011cj.q011b._canonical_json_sha256(
            q011cj._result_digest_sections(q011cj_cycle)
        )
    )
    assert q011cj._protocol_globals_are_restored()


def test_q011cj_study_metadata_and_optional_artifact_are_scoped(
    q011cj_study: dict[str, Any],
) -> None:
    assert q011cj_study["schema_version"] == 1
    assert q011cj_study["source"] == source_metadata()
    assert q011cj_study["study_gate"] == "passed"
    assert q011cj_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cj_study["scientific_outcome"] == "not_evaluated"
    assert q011cj_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cj_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cj_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 3
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cj_study, allow_nan=False)

    runner_path = Path(q011cj.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011cj_degree34_fourth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cj_degree34_fourth_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cj.q011b._canonical_json_sha256(
            q011cj._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
