from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gl_degree34_fifty_seventh_component_safe_phase_discs as q011gl
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = None
EXPECTED_STREAM_DIGEST: str | None = None
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = None
EXPECTED_MINIMUM_INDEX: int | None = None
EXPECTED_MINIMUM_COUNTS: list[int] | None = None
EXPECTED_MINIMUM_MARGIN_HEX: str | None = None
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
def q011gl_structure() -> dict[str, Any]:
    sealed, artifacts = q011gl._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011gl._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011gl._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011gl_study() -> dict[str, Any]:
    return q011gl.run_q011gl_study()


@pytest.fixture(scope="module")
def q011gl_cycle(q011gl_study: dict[str, Any]) -> dict[str, Any]:
    return q011gl_study["cycle"]


def test_q011gl_seals_q011gk_and_all_prior_inputs(
    q011gl_structure: dict[str, Any],
) -> None:
    sealed = q011gl_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 172
    assert sealed["direct_digest_count"] == 786
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gk"]["digests"]) == q011gl.Q011GK_DIGESTS
    assert sealed["q011gk"]["artifact_sha256"] == q011gl.Q011GK_ARTIFACT_SHA256
    assert sealed["q011gk"]["runner_sha256"] == q011gl.Q011GK_RUNNER_SHA256


def test_q011gl_reconstructs_component_safe_phase_discs(
    q011gl_structure: dict[str, Any],
) -> None:
    fixed = q011gl_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 56
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011gl.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011gl.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011gl.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011gl.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011gk_compatible_wave_allocation_count"] == 911
    assert fixed["q011gk_compatible_wave_allocation_digest_sha256"] == (
        q011gl.q011gk.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011gl._protocol_globals_are_restored()


def test_q011gl_enumerates_registered_label_free_phase_inventory(
    q011gl_structure: dict[str, Any],
) -> None:
    allocation = q011gl_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011gl.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011gl.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 911
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011gl.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 77,
        "3": 226,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 911
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011gl.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011gl.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_fifty_six_totals"] == [13, 9, 5, 0, 7]
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gl result is not sealed")
def test_q011gl_certifies_all_complex_phase_product_discs(
    q011gl_cycle: dict[str, Any],
) -> None:
    comparison = q011gl_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 56
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
    assert comparison["comparison_stream_domain"] == ("q011gl-component-safe-phase-comparisons-v1")
    if not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011gl comparison stream digest has not been sealed yet")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gl result is not sealed")
def test_q011gl_minimum_exact_phase_margin_is_fixed(
    q011gl_cycle: dict[str, Any],
) -> None:
    comparison = q011gl_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    if EXPECTED_MINIMUM_INDEX is None or EXPECTED_MINIMUM_COUNTS is None:
        pytest.skip("Q011gl minimum phase witness has not been sealed yet")
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert q011gl.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gl result is not sealed")
def test_q011gl_records_scoped_resolution(q011gl_cycle: dict[str, Any]) -> None:
    assert q011gl_cycle["study_validity"] == "passed"
    assert q011gl_cycle["failed_validity_order"] == []
    assert q011gl_cycle["failed_diagnostic_order"] == []
    assert len(q011gl_cycle["validity_gates"]) == 7
    assert len(q011gl_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011gl_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gl_cycle["diagnostic_gates"].values())
    assert q011gl_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011gl_cycle["diagnostic_classification"] == q011gl.RESOLVED_CLASSIFICATION
    assert q011gl_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gl_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011gm" in q011gl_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011gl_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gl result is not sealed")
def test_q011gl_preserves_scientific_boundary(q011gl_cycle: dict[str, Any]) -> None:
    theorem = q011gl_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_fifty_seventh_q011cb_witness"]
    assert not theorem["fifty_seventh_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011gk_ordinal_fifty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gj_ordinal_fifty_five_phase_resolution_is_preserved"]
    assert theorem["q011gi_ordinal_fifty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gh_ordinal_fifty_four_phase_resolution_is_preserved"]
    assert theorem["q011gg_ordinal_fifty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gf_ordinal_fifty_three_phase_resolution_is_preserved"]
    assert theorem["q011ge_ordinal_fifty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gd_ordinal_fifty_two_phase_resolution_is_preserved"]
    assert theorem["q011gc_ordinal_fifty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gb_ordinal_fifty_one_phase_resolution_is_preserved"]
    assert theorem["q011ga_ordinal_fifty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fz_ordinal_fifty_phase_resolution_is_preserved"]
    assert theorem["q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fx_ordinal_forty_nine_phase_resolution_is_preserved"]
    assert theorem["q011fw_ordinal_forty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fv_ordinal_forty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ft_ordinal_forty_seven_phase_resolution_is_preserved"]
    assert theorem["q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fr_ordinal_forty_six_phase_resolution_is_preserved"]
    assert theorem["q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fp_ordinal_forty_five_phase_resolution_is_preserved"]
    assert theorem["q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fn_ordinal_forty_four_phase_resolution_is_preserved"]
    assert theorem["q011fm_ordinal_forty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fl_ordinal_forty_three_phase_resolution_is_preserved"]
    assert theorem["q011fk_ordinal_forty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fj_ordinal_forty_two_phase_resolution_is_preserved"]
    assert theorem["q011fi_ordinal_forty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fh_ordinal_forty_one_phase_resolution_is_preserved"]
    assert theorem["q011fg_ordinal_forty_one_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 56" in q011gl_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 55" in q011gl_cycle["claim_boundary"]
    assert "later 44743 Q011cb refined signatures" in q011gl_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011gl_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gl result is not sealed")
def test_q011gl_cycle_has_strict_reproducible_digests(
    q011gl_cycle: dict[str, Any],
) -> None:
    json.dumps(q011gl_cycle, allow_nan=False)
    assert EXPECTED_SECTION_DIGESTS is not None
    assert {name: q011gl_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011gl_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011gl_cycle["result_digest_sha256"] == (
        q011gl.q011b._canonical_json_sha256(q011gl._result_digest_sections(q011gl_cycle))
    )
    assert q011gl._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gl result is not sealed")
def test_q011gl_study_metadata_and_optional_artifact_are_scoped(
    q011gl_study: dict[str, Any],
) -> None:
    assert q011gl_study["schema_version"] == 1
    assert q011gl_study["source"] == source_metadata()
    assert q011gl_study["study_gate"] == "passed"
    assert q011gl_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011gl_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gl_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 56
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gl_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011gl runner hash has not been sealed yet")
    runner_path = Path(q011gl.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gl_degree34_fifty_seventh_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gl artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gl.q011b._canonical_json_sha256(q011gl._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
