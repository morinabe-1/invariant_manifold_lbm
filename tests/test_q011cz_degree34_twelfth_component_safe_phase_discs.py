from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cz_degree34_twelfth_component_safe_phase_discs as q011cz
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "6824854848d81d0deb5ea3e90a67626e831cb9095f0316307a0500f31650e30e"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "e267a7028fdca60748825ddf40eff75cf96fd89ed6fba54351aa91509bc19f95",
    "phase_input_digest_sha256": (
        "e52ba2043f5c4e775849db9632ea9e5aa7d2a67d5e2116b86fdc18d6c5d3742b"
    ),
    "allocation_digest_sha256": (
        "ba3fa474e3efa0d813636cd16d36582a99225c5314fe4c92f3cc494b8598bcd5"
    ),
    "phase_comparison_digest_sha256": (
        "6cb6bcbf87e12a5cadc33c05526dbfa509c41e045e7d4496545d20b7ed080aeb"
    ),
    "result_digest_sha256": "af5f97f570c101fce046d431e8e65ceb8b19fa0240aa8bb6649e117d5493a918",
}
EXPECTED_STREAM_DIGEST = "742091df2e6a60107803b68f69febb595ef6f0773848725180a89d6433cbf587"
EXPECTED_MINIMUM_WITNESS_DIGEST = "4d81a833f38342bf959039d0b9e3f85fd2fc2edae6f7fde6aa7fe9f8f46e3a71"


@pytest.fixture(scope="module")
def q011cz_study() -> dict[str, Any]:
    return q011cz.run_q011cz_study()


@pytest.fixture(scope="module")
def q011cz_cycle(q011cz_study: dict[str, Any]) -> dict[str, Any]:
    return q011cz_study["cycle"]


def test_q011cz_seals_q011cy_and_all_prior_inputs(
    q011cz_cycle: dict[str, Any],
) -> None:
    sealed = q011cz_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 82
    assert sealed["direct_digest_count"] == 381
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cy"]["digests"]) == q011cz.Q011CY_DIGESTS
    assert sealed["q011cy"]["artifact_sha256"] == q011cz.Q011CY_ARTIFACT_SHA256
    assert sealed["q011cy"]["runner_sha256"] == q011cz.Q011CY_RUNNER_SHA256


def test_q011cz_reconstructs_component_safe_phase_discs(
    q011cz_cycle: dict[str, Any],
) -> None:
    fixed = q011cz_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 11
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cz.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cz.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011cz.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011cz.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cy_compatible_wave_allocation_count"] == 1_699
    assert fixed["q011cy_compatible_wave_allocation_digest_sha256"] == (
        q011cz.q011cy.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cz._protocol_globals_are_restored()


def test_q011cz_enumerates_registered_label_free_phase_inventory(
    q011cz_cycle: dict[str, Any],
) -> None:
    allocation = q011cz_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == q011cz.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cz.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 1, 2, 4, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 3, 0, 4]
    assert allocation["individual_wave_allocation_count"] == 1_699
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011cz.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 191,
        "2": 754,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_699
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011cz.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cz.EXPECTED_WAVE_PROJECTION_DIGEST
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
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 20_786
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    assert allocation["allocation_protocol_adapter"]["protocol_globals_modified"] is False


def test_q011cz_certifies_all_complex_phase_product_discs(
    q011cz_cycle: dict[str, Any],
) -> None:
    comparison = q011cz_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 11
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
    assert comparison["comparison_stream_domain"] == ("q011cz-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cz_minimum_exact_phase_margin_is_fixed(
    q011cz_cycle: dict[str, Any],
) -> None:
    comparison = q011cz_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 12_816
    assert witness["counts"] == [11, 2, 0, 6, 0, 3, 0, 5, 3, 0, 2, 2]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc85dep-6")
    assert q011cz.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cz_records_scoped_resolution(q011cz_cycle: dict[str, Any]) -> None:
    assert q011cz_cycle["study_validity"] == "passed"
    assert q011cz_cycle["failed_validity_order"] == []
    assert q011cz_cycle["failed_diagnostic_order"] == []
    assert len(q011cz_cycle["validity_gates"]) == 7
    assert len(q011cz_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011cz_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cz_cycle["diagnostic_gates"].values())
    assert q011cz_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cz_cycle["diagnostic_classification"] == q011cz.RESOLVED_CLASSIFICATION
    assert q011cz_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cz_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011da" in q011cz_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cz_cycle["next_change"]


def test_q011cz_preserves_scientific_boundary(q011cz_cycle: dict[str, Any]) -> None:
    theorem = q011cz_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_twelfth_q011cb_witness"]
    assert not theorem["twelfth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cy_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cw_ordinal_ten_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 11" in q011cz_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 10" in q011cz_cycle["claim_boundary"]
    assert "later 44788 Q011cb refined signatures" in q011cz_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cz_cycle["claim_boundary"]


def test_q011cz_cycle_has_strict_reproducible_digests(
    q011cz_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cz_cycle, allow_nan=False)
    assert {name: q011cz_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011cz_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cz_cycle["result_digest_sha256"] == (
        q011cz.q011b._canonical_json_sha256(q011cz._result_digest_sections(q011cz_cycle))
    )
    assert q011cz._protocol_globals_are_restored()


def test_q011cz_study_metadata_and_optional_artifact_are_scoped(
    q011cz_study: dict[str, Any],
) -> None:
    assert q011cz_study["schema_version"] == 1
    assert q011cz_study["source"] == source_metadata()
    assert q011cz_study["study_gate"] == "passed"
    assert q011cz_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011cz_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cz_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 11
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cz_study, allow_nan=False)

    runner_path = Path(q011cz.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / "q011cz_degree34_twelfth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cz artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cz.q011b._canonical_json_sha256(q011cz._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
