from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ff_degree34_forty_first_component_safe_phase_discs as q011ff
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d23f687858dd35824c9f516da4c97dffd256f85a5042a66ebea87d60573786a3"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "382defe5dc094ca811ebf42e31acc7bfd8bfdc490d5b93c509960e7bdf128c68"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "5a42100b653ed03cf177b35d6e13660c0be9bf5d9d7413715b9a79c96de5e186",
    "phase_input_digest_sha256": "731867fe950ace6f55a5a6bf9b88d62356f4b16687dacb80bcb0b49c2b4ba7d2",
    "allocation_digest_sha256": "595be6c5a5cc7a2df346efaf40acee92110885a60b70f451ff226464a68159c8",
    "phase_comparison_digest_sha256": "208ee6447a5792b6560e8f62aac29a28aa85d73054c10ed9bc8cdd39c4fcb1d8",
    "result_digest_sha256": "fa0b8377bf4b975254c8861bf5005539772d6b1f8a0d19ad7a6a93d3a670cbbd",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "1a9b5534db03bfea3ea0d1b342de8312e5d53cf3702a2200cd7a40bdcba4ec11"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "0608c0d35f60903eea1f58ee9ea5f3f8fef345e97babcf53abee39f14fa1aa0d"
)
EXPECTED_MINIMUM_INDEX: int | None = 5_455
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 9, 0, 0, 0, 5, 0, 0, 2, 5]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8463p-6"
RESULT_EXPECTATIONS_FIXED = EXPECTED_SECTION_DIGESTS is not None


@pytest.fixture(scope="module")
def q011ff_structure(q011ff_study: dict[str, Any]) -> dict[str, Any]:
    cycle = q011ff_study["cycle"]
    allocation = cycle["component_safe_phase_allocation_audit"]
    return {
        "sealed": cycle["sealed_input_audit"],
        "fixed": cycle["fixed_component_safe_phase_input_audit"],
        "allocation": allocation,
        "compatible_count": allocation["compatible_allocation_count"],
    }


@pytest.fixture(scope="module")
def q011ff_study() -> dict[str, Any]:
    return q011ff.run_q011ff_study()


@pytest.fixture(scope="module")
def q011ff_cycle(q011ff_study: dict[str, Any]) -> dict[str, Any]:
    return q011ff_study["cycle"]


def test_q011ff_seals_q011fe_and_all_prior_inputs(
    q011ff_structure: dict[str, Any],
) -> None:
    sealed = q011ff_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 140
    assert sealed["direct_digest_count"] == 642
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fe"]["digests"]) == q011ff.Q011FE_DIGESTS
    assert sealed["q011fe"]["artifact_sha256"] == q011ff.Q011FE_ARTIFACT_SHA256
    assert sealed["q011fe"]["runner_sha256"] == q011ff.Q011FE_RUNNER_SHA256


def test_q011ff_reconstructs_component_safe_phase_discs(
    q011ff_structure: dict[str, Any],
) -> None:
    fixed = q011ff_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 40
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ff.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ff.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011ff.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011ff.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011fe_compatible_wave_allocation_count"] == 1_136
    assert fixed["q011fe_compatible_wave_allocation_digest_sha256"] == (
        q011ff.q011fe.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ff._protocol_globals_are_restored()


def test_q011ff_enumerates_registered_label_free_phase_inventory(
    q011ff_structure: dict[str, Any],
) -> None:
    allocation = q011ff_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == q011ff.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 8_350
    assert q011ff_structure["compatible_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ff.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 1_136
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ff.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 77,
        "3": 76,
        "4": 75,
        "5": 75,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_136
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ff.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ff.EXPECTED_WAVE_PROJECTION_DIGEST
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
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_forty_totals"] == [13, 9, 5, 0, 7]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ff result is not sealed")
def test_q011ff_certifies_all_complex_phase_product_discs(
    q011ff_cycle: dict[str, Any],
) -> None:
    comparison = q011ff_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 40
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
    assert comparison["comparison_stream_domain"] == ("q011ff-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ff result is not sealed")
def test_q011ff_minimum_exact_phase_margin_is_fixed(
    q011ff_cycle: dict[str, Any],
) -> None:
    comparison = q011ff_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011ff.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ff result is not sealed")
def test_q011ff_records_scoped_resolution(
    q011ff_cycle: dict[str, Any],
) -> None:
    assert q011ff_cycle["study_validity"] == "passed"
    assert q011ff_cycle["failed_validity_order"] == []
    assert q011ff_cycle["failed_diagnostic_order"] == []
    assert len(q011ff_cycle["validity_gates"]) == 7
    assert len(q011ff_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ff_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ff_cycle["diagnostic_gates"].values())
    assert q011ff_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ff_cycle["diagnostic_classification"] == q011ff.RESOLVED_CLASSIFICATION
    assert q011ff_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ff_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011fg" in q011ff_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011ff_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ff result is not sealed")
def test_q011ff_preserves_scientific_boundary(q011ff_cycle: dict[str, Any]) -> None:
    theorem = q011ff_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_forty_first_q011cb_witness"],
        theorem["forty_first_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert flags == (True, False)
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011fe_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fd_ordinal_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fb_ordinal_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ez_ordinal_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ex_ordinal_thirty_six_phase_resolution_is_preserved"]
    assert theorem["q011ew_ordinal_thirty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ev_ordinal_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011et_ordinal_thirty_four_phase_resolution_is_preserved"]
    assert theorem["q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011er_ordinal_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ep_ordinal_thirty_two_phase_resolution_is_preserved"]
    assert theorem["q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011en_ordinal_thirty_one_phase_resolution_is_preserved"]
    assert theorem["q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011el_ordinal_thirty_phase_resolution_is_preserved"]
    assert theorem["q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ej_ordinal_twenty_nine_phase_resolution_is_preserved"]
    assert theorem["q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eh_ordinal_twenty_eight_phase_resolution_is_preserved"]
    assert theorem["q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ef_ordinal_twenty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ed_ordinal_twenty_six_phase_resolution_is_preserved"]
    assert theorem["q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eb_ordinal_twenty_five_phase_resolution_is_preserved"]
    assert theorem["q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 40" in q011ff_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 39" in q011ff_cycle["claim_boundary"]
    assert "later 44759 Q011cb refined signatures" in q011ff_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ff_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ff result is not sealed")
def test_q011ff_cycle_has_strict_reproducible_digests(
    q011ff_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ff_cycle, allow_nan=False)
    assert {name: q011ff_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ff_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ff_cycle["result_digest_sha256"] == (
        q011ff.q011b._canonical_json_sha256(q011ff._result_digest_sections(q011ff_cycle))
    )
    assert q011ff._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ff result is not sealed")
def test_q011ff_study_metadata_and_optional_artifact_are_scoped(
    q011ff_study: dict[str, Any],
) -> None:
    assert q011ff_study["schema_version"] == 1
    assert q011ff_study["source"] == source_metadata()
    assert q011ff_study["study_gate"] == "passed"
    assert q011ff_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011ff_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ff_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 40
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ff_study, allow_nan=False)

    runner_path = Path(q011ff.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ff_degree34_forty_first_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ff artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ff_study["refinement_outcome"]
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ff.q011b._canonical_json_sha256(q011ff._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
