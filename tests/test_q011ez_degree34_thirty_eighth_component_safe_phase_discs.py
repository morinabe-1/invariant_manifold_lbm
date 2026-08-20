from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ez_degree34_thirty_eighth_component_safe_phase_discs as q011ez
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "175e9813034286faeb506f0b6a2e53501dd3129e1f2468afcf091fe344cb6c20"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "6b8f0f5f787b79aacffad7295497e3b4441a1892f9828f75f96c1c79c3b479c8"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "54caf476f36291da64d9849680ebb4621420c9427b208d7bf63102d406cd2249",
    "phase_input_digest_sha256": "9ce7b5489e53442355e0c396f8f03a65a71d002d5705617e1b0a08ceaa1f615e",
    "allocation_digest_sha256": "26170c8323f3a4b5f2ec499f75b00bc5e3a84199e2d74990f340a65af0f6ba68",
    "phase_comparison_digest_sha256": "524ac5d27846f54c6f82017887fa0a81da740bfee792d103e3c3531b06497bb3",
    "result_digest_sha256": "a19a8cd95774b1d3ae0557a7a2bf88e5717a0414266e18f2e5c33701593e07ca",
}
EXPECTED_STREAM_DIGEST = "fb269a5c1b4d56f246f20a2dcaffbfd41ef774ee4ec739b00ad9bad48cecb3f2"
EXPECTED_MINIMUM_WITNESS_DIGEST = "514c3194347c4be6775cc7a53518fbee0c3d97586a962c6e2b63378ce8a8614f"
EXPECTED_MINIMUM_INDEX: int | None = 11_474
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 4, 0, 5, 0, 5, 5, 0, 2, 0]
EXPECTED_MINIMUM_MARGIN_HEX = "0x1.a8f10a6dc86dap-6"


@pytest.fixture(scope="module")
def q011ez_study() -> dict[str, Any]:
    return q011ez.run_q011ez_study()


@pytest.fixture(scope="module")
def q011ez_cycle(q011ez_study: dict[str, Any]) -> dict[str, Any]:
    return q011ez_study["cycle"]


def test_q011ez_seals_q011ey_and_all_prior_inputs(
    q011ez_cycle: dict[str, Any],
) -> None:
    sealed = q011ez_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 134
    assert sealed["direct_digest_count"] == 615
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ey"]["digests"]) == q011ez.Q011EY_DIGESTS
    assert sealed["q011ey"]["artifact_sha256"] == q011ez.Q011EY_ARTIFACT_SHA256
    assert sealed["q011ey"]["runner_sha256"] == q011ez.Q011EY_RUNNER_SHA256


def test_q011ez_reconstructs_component_safe_phase_discs(
    q011ez_cycle: dict[str, Any],
) -> None:
    fixed = q011ez_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 37
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ez.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ez.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011ez.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011ez.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ey_compatible_wave_allocation_count"] == 2_553
    assert fixed["q011ey_compatible_wave_allocation_digest_sha256"] == (
        q011ez.q011ey.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ez._protocol_globals_are_restored()


def test_q011ez_enumerates_registered_label_free_phase_inventory(
    q011ez_cycle: dict[str, Any],
) -> None:
    allocation = q011ez_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == (q011ez.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ez.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 2_553
    assert allocation["component_wave_projection_count"] == 852
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ez.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 173,
        "2": 169,
        "3": 169,
        "4": 170,
        "5": 171,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_553
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ez.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ez.EXPECTED_WAVE_PROJECTION_DIGEST
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
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_thirty_seven_totals"] == [13, 9, 5, 5, 2]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011ez_certifies_all_complex_phase_product_discs(
    q011ez_cycle: dict[str, Any],
) -> None:
    comparison = q011ez_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 37
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
    assert comparison["comparison_stream_domain"] == ("q011ez-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011ez_minimum_exact_phase_margin_is_fixed(
    q011ez_cycle: dict[str, Any],
) -> None:
    comparison = q011ez_cycle["complex_phase_product_disc_audit"]
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
    assert q011ez.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ez_records_scoped_resolution(q011ez_cycle: dict[str, Any]) -> None:
    assert q011ez_cycle["study_validity"] == "passed"
    assert q011ez_cycle["failed_validity_order"] == []
    assert q011ez_cycle["failed_diagnostic_order"] == []
    assert len(q011ez_cycle["validity_gates"]) == 7
    assert len(q011ez_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011ez_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ez_cycle["diagnostic_gates"].values())
    assert q011ez_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ez_cycle["diagnostic_classification"] == q011ez.RESOLVED_CLASSIFICATION
    assert q011ez_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ez_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011fa" in q011ez_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011ez_cycle["next_change"]


def test_q011ez_preserves_scientific_boundary(q011ez_cycle: dict[str, Any]) -> None:
    theorem = q011ez_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_thirty_eighth_q011cb_witness"],
        theorem["thirty_eighth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert flags == (True, False)
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011ey_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 37" in q011ez_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 36" in q011ez_cycle["claim_boundary"]
    assert "later 44762 Q011cb refined signatures" in q011ez_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ez_cycle["claim_boundary"]


def test_q011ez_cycle_has_strict_reproducible_digests(
    q011ez_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ez_cycle, allow_nan=False)
    assert {name: q011ez_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011ez_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ez_cycle["result_digest_sha256"] == (
        q011ez.q011b._canonical_json_sha256(q011ez._result_digest_sections(q011ez_cycle))
    )
    assert q011ez._protocol_globals_are_restored()


def test_q011ez_study_metadata_and_optional_artifact_are_scoped(
    q011ez_study: dict[str, Any],
) -> None:
    assert q011ez_study["schema_version"] == 1
    assert q011ez_study["source"] == source_metadata()
    assert q011ez_study["study_gate"] == "passed"
    assert q011ez_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011ez_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ez_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 37
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ez_study, allow_nan=False)

    runner_path = Path(q011ez.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ez_degree34_thirty_eighth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ez artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ez_study["refinement_outcome"]
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ez.q011b._canonical_json_sha256(q011ez._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
