from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fh_degree34_forty_second_component_safe_phase_discs as q011fh
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "bc4656524897ef9ff457cea747474a5c6d84715de1680ad625f33ca7a13592e3"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "533487fcbbd4bd38748d5ad5d1adbe7527ade1f03fe321664a5ba8720f322c64"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "9c0915cc2a590469e35bf5886ef8f7d964ea55df45987d35643a9dd2dc603c03",
    "phase_input_digest_sha256": "cd5a929b5641689add26cb8fd4dcd4b3a0a65d7357eeca7fe6aa6295a30ef912",
    "allocation_digest_sha256": "ce4bd3c0ec4f15406a46ffa762438df1793b763d019618c062ecd0a068f6141b",
    "phase_comparison_digest_sha256": "23c9e78c9e3877deeca35c7120064e0b446560bb618fd6ad9b589480e635f385",
    "result_digest_sha256": "7290a35a21fb208aaa4dbe0c5dfab2a0762c8be6c920dc9bf556d6becaa1bee3",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "8f8e51942609b792f126ce30f06a28f32dcdbfc0b9b0df6b6ec174c60cfaa8b9"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "57badc5d7675b78362958718cfc68036f87a34d11f88fe4cdd88c7c264932e3c"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_298
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 8, 0, 1, 0, 5, 1, 0, 2, 4]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc84e1p-6"
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
    )
)


@pytest.fixture(scope="module")
def q011fh_structure() -> dict[str, Any]:
    sealed, artifacts = q011fh._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011fh._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011fh._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011fh_study() -> dict[str, Any]:
    return q011fh.run_q011fh_study()


@pytest.fixture(scope="module")
def q011fh_cycle(q011fh_study: dict[str, Any]) -> dict[str, Any]:
    return q011fh_study["cycle"]


def test_q011fh_seals_q011fg_and_all_prior_inputs(
    q011fh_structure: dict[str, Any],
) -> None:
    sealed = q011fh_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 142
    assert sealed["direct_digest_count"] == 651
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fg"]["digests"]) == q011fh.Q011FG_DIGESTS
    assert sealed["q011fg"]["artifact_sha256"] == q011fh.Q011FG_ARTIFACT_SHA256
    assert sealed["q011fg"]["runner_sha256"] == q011fh.Q011FG_RUNNER_SHA256


def test_q011fh_reconstructs_component_safe_phase_discs(
    q011fh_structure: dict[str, Any],
) -> None:
    fixed = q011fh_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 41
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011fh.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011fh.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011fh.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011fh.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011fg_compatible_wave_allocation_count"] == 1_986
    assert fixed["q011fg_compatible_wave_allocation_digest_sha256"] == (
        q011fh.q011fg.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011fh._protocol_globals_are_restored()


def test_q011fh_enumerates_registered_label_free_phase_inventory(
    q011fh_structure: dict[str, Any],
) -> None:
    allocation = q011fh_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == (q011fh.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011fh.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        1,
        5,
        1,
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
        1,
        0,
        6,
    ]
    assert allocation["individual_wave_allocation_count"] == 1_986
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011fh.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 136,
        "2": 133,
        "3": 132,
        "4": 132,
        "5": 132,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_986
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011fh.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011fh.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_forty_one_totals"] == [13, 9, 5, 1, 6]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fh result is not sealed")
def test_q011fh_certifies_all_complex_phase_product_discs(
    q011fh_cycle: dict[str, Any],
) -> None:
    comparison = q011fh_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 41
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
    assert comparison["comparison_stream_domain"] == ("q011fh-component-safe-phase-comparisons-v1")
    if not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011fh comparison stream digest has not been sealed yet")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fh result is not sealed")
def test_q011fh_minimum_exact_phase_margin_is_fixed(
    q011fh_cycle: dict[str, Any],
) -> None:
    comparison = q011fh_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    if EXPECTED_MINIMUM_INDEX is None or EXPECTED_MINIMUM_COUNTS is None:
        pytest.skip("Q011fh minimum phase witness has not been sealed yet")
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011fh.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fh result is not sealed")
def test_q011fh_records_scoped_resolution(q011fh_cycle: dict[str, Any]) -> None:
    assert q011fh_cycle["study_validity"] == "passed"
    assert q011fh_cycle["failed_validity_order"] == []
    assert q011fh_cycle["failed_diagnostic_order"] == []
    assert len(q011fh_cycle["validity_gates"]) == 7
    assert len(q011fh_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011fh_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fh_cycle["diagnostic_gates"].values())
    assert q011fh_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011fh_cycle["diagnostic_classification"] == q011fh.RESOLVED_CLASSIFICATION
    assert q011fh_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fh_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011fi" in q011fh_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011fh_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fh result is not sealed")
def test_q011fh_preserves_scientific_boundary(q011fh_cycle: dict[str, Any]) -> None:
    theorem = q011fh_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_forty_second_q011cb_witness"]
    assert not theorem["forty_second_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011fg_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ff_ordinal_forty_phase_resolution_is_preserved"]
    assert theorem["q011fe_ordinal_forty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fd_ordinal_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fb_ordinal_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ez_ordinal_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 41" in q011fh_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 40" in q011fh_cycle["claim_boundary"]
    assert "later 44758 Q011cb refined signatures" in q011fh_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011fh_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fh result is not sealed")
def test_q011fh_cycle_has_strict_reproducible_digests(
    q011fh_cycle: dict[str, Any],
) -> None:
    json.dumps(q011fh_cycle, allow_nan=False)
    assert EXPECTED_SECTION_DIGESTS is not None
    assert {name: q011fh_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011fh_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011fh_cycle["result_digest_sha256"] == (
        q011fh.q011b._canonical_json_sha256(q011fh._result_digest_sections(q011fh_cycle))
    )
    assert q011fh._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fh result is not sealed")
def test_q011fh_study_metadata_and_optional_artifact_are_scoped(
    q011fh_study: dict[str, Any],
) -> None:
    assert q011fh_study["schema_version"] == 1
    assert q011fh_study["source"] == source_metadata()
    assert q011fh_study["study_gate"] == "passed"
    assert q011fh_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011fh_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fh_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 41
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fh_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011fh runner hash has not been sealed yet")
    runner_path = Path(q011fh.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fh_degree34_forty_second_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fh artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fh.q011b._canonical_json_sha256(q011fh._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
