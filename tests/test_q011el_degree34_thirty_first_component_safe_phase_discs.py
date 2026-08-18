from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011el_degree34_thirty_first_component_safe_phase_discs as q011el
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "2d0712601af1a4c3505faf2060a8b9fae1740ff2d8377a492d2069e04832ce07"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "13f47529233d706318bd3171f122b22e2a6b21c7c611ff4ff030fcf212a7f0f6"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "14c09c58e19e19f8e8497444fc949b88bc0d621f9fde29f90a02baed1422f614",
    "phase_input_digest_sha256": "e8df8faf02e742e090906e3ab90c8c00e9fb5ed72474716405a2ac98b7c65f0c",
    "allocation_digest_sha256": "efd2509b751f189526f5029f6b5bb8d8186049a4c281bc2cccf4b7079aa72b7c",
    "phase_comparison_digest_sha256": "aacee20b4c9e3153661e5bd91e58480626e8a86c08c9422e708d7cdeb8c45eb2",
    "result_digest_sha256": "0397890c3b89964e659888833e05d2715297e0d3ce0c687c04086ed60bd1235e",
}
EXPECTED_STREAM_DIGEST = "3570d0e33480e6d77898999035dd032d171fa223dbaaefdf732e517b5f07ddd9"
EXPECTED_MINIMUM_WITNESS_DIGEST = "1b7f6cc19a74cdefa602f28a6251f0c9b874cdd0a3a9b6f7ee438ea4618fea8d"
EXPECTED_MINIMUM_INDEX: int | None = 9_166
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 5, 0, 4, 0, 5, 5, 1, 1, 0]
EXPECTED_MINIMUM_MARGIN_HEX = "0x1.a8f10a6dc8860p-6"


@pytest.fixture(scope="module")
def q011el_study() -> dict[str, Any]:
    return q011el.run_q011el_study()


@pytest.fixture(scope="module")
def q011el_cycle(q011el_study: dict[str, Any]) -> dict[str, Any]:
    return q011el_study["cycle"]


def test_q011el_seals_q011ek_and_all_prior_inputs(
    q011el_cycle: dict[str, Any],
) -> None:
    sealed = q011el_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 120
    assert sealed["direct_digest_count"] == 552
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ek"]["digests"]) == q011el.Q011EK_DIGESTS
    assert sealed["q011ek"]["artifact_sha256"] == q011el.Q011EK_ARTIFACT_SHA256
    assert sealed["q011ek"]["runner_sha256"] == q011el.Q011EK_RUNNER_SHA256


def test_q011el_reconstructs_component_safe_phase_discs(
    q011el_cycle: dict[str, Any],
) -> None:
    fixed = q011el_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 30
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011el.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011el.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011el.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011el.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ek_compatible_wave_allocation_count"] == 1_854
    assert fixed["q011ek_compatible_wave_allocation_digest_sha256"] == (
        q011el.q011ek.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011el._protocol_globals_are_restored()


def test_q011el_enumerates_registered_label_free_phase_inventory(
    q011el_cycle: dict[str, Any],
) -> None:
    allocation = q011el_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == (q011el.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011el.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        4,
        2,
        1,
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
        6,
        0,
        1,
    ]
    assert allocation["individual_wave_allocation_count"] == 1_854
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011el.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 4
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 136,
        "2": 133,
        "3": 132,
        "4": 264,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_854
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011el.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011el.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 136,
        "18": 133,
        "24": 132,
        "28": 132,
        "30": 132,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 14_578
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_thirty_totals"] == [13, 9, 5, 6, 1]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011el_certifies_all_complex_phase_product_discs(
    q011el_cycle: dict[str, Any],
) -> None:
    comparison = q011el_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 30
    assert comparison["compatible_phase_allocation_count"] == 14_578
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 14_578,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 14_578,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 14_578
    assert comparison["comparison_stream_domain"] == ("q011el-component-safe-phase-comparisons-v1")
    if not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011el comparison stream digest has not been sealed yet")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011el_minimum_exact_phase_margin_is_fixed(
    q011el_cycle: dict[str, Any],
) -> None:
    comparison = q011el_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    if EXPECTED_MINIMUM_INDEX is None or EXPECTED_MINIMUM_COUNTS is None:
        pytest.skip("Q011el minimum phase witness has not been sealed yet")
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011el.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011el_records_scoped_resolution(q011el_cycle: dict[str, Any]) -> None:
    assert q011el_cycle["study_validity"] == "passed"
    assert q011el_cycle["failed_validity_order"] == []
    assert q011el_cycle["failed_diagnostic_order"] == []
    assert len(q011el_cycle["validity_gates"]) == 7
    assert len(q011el_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011el_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011el_cycle["diagnostic_gates"].values())
    assert q011el_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011el_cycle["diagnostic_classification"] == q011el.RESOLVED_CLASSIFICATION
    assert q011el_cycle["scientific_outcome"] == "not_evaluated"
    assert q011el_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011em" in q011el_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011el_cycle["next_change"]


def test_q011el_preserves_scientific_boundary(q011el_cycle: dict[str, Any]) -> None:
    theorem = q011el_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_thirty_first_q011cb_witness"]
    assert not theorem["thirty_first_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011ek_interval_inert_diagnostic_is_preserved"]
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
    assert theorem["q011dz_ordinal_twenty_four_phase_resolution_is_preserved"]
    assert theorem["q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert theorem["q011dw_ordinal_twenty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dv_ordinal_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dt_ordinal_twenty_one_phase_resolution_is_preserved"]
    assert theorem["q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dj_ordinal_sixteen_phase_resolution_is_preserved"]
    assert theorem["q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011df_ordinal_fourteen_phase_resolution_is_preserved"]
    assert theorem["q011de_ordinal_fourteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dd_ordinal_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011dc_ordinal_thirteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011db_ordinal_twelve_phase_resolution_is_preserved"]
    assert theorem["q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
    assert theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
    assert theorem["q011cr_ordinal_seven_phase_resolution_is_preserved"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 30" in q011el_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 29" in q011el_cycle["claim_boundary"]
    assert "later 44769 Q011cb refined signatures" in q011el_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011el_cycle["claim_boundary"]


def test_q011el_cycle_has_strict_reproducible_digests(
    q011el_cycle: dict[str, Any],
) -> None:
    json.dumps(q011el_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011el section digests have not been sealed yet")
    assert {name: q011el_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011el_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011el_cycle["result_digest_sha256"] == (
        q011el.q011b._canonical_json_sha256(q011el._result_digest_sections(q011el_cycle))
    )
    assert q011el._protocol_globals_are_restored()


def test_q011el_study_metadata_and_optional_artifact_are_scoped(
    q011el_study: dict[str, Any],
) -> None:
    assert q011el_study["schema_version"] == 1
    assert q011el_study["source"] == source_metadata()
    assert q011el_study["study_gate"] == "passed"
    assert q011el_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011el_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011el_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 30
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011el_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011el runner hash has not been sealed yet")
    runner_path = Path(q011el.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011el_degree34_thirty_first_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011el artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011el.q011b._canonical_json_sha256(q011el._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
