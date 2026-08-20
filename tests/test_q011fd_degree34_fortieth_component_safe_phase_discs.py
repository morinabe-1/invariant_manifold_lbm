from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fd_degree34_fortieth_component_safe_phase_discs as q011fd
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
RESULT_EXPECTATIONS_FIXED = EXPECTED_SECTION_DIGESTS is not None


@pytest.fixture(scope="module")
def q011fd_structure() -> dict[str, Any]:
    sealed, artifacts = q011fd._sealed_input_audit()
    fixed, sources, _target, waves = q011fd._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011fd._allocation_inventory(sources, waves)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011fd_study() -> dict[str, Any]:
    return q011fd.run_q011fd_study()


@pytest.fixture(scope="module")
def q011fd_cycle(q011fd_study: dict[str, Any]) -> dict[str, Any]:
    return q011fd_study["cycle"]


def test_q011fd_seals_q011fc_and_all_prior_inputs(
    q011fd_structure: dict[str, Any],
) -> None:
    sealed = q011fd_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 138
    assert sealed["direct_digest_count"] == 633
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fc"]["digests"]) == q011fd.Q011FC_DIGESTS
    assert sealed["q011fc"]["artifact_sha256"] == q011fd.Q011FC_ARTIFACT_SHA256
    assert sealed["q011fc"]["runner_sha256"] == q011fd.Q011FC_RUNNER_SHA256


def test_q011fd_reconstructs_component_safe_phase_discs(
    q011fd_structure: dict[str, Any],
) -> None:
    fixed = q011fd_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 39
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011fd.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011fd.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011fd.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011fd.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011fc_compatible_wave_allocation_count"] == 1_136
    assert fixed["q011fc_compatible_wave_allocation_digest_sha256"] == (
        q011fd.q011fc.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011fd._protocol_globals_are_restored()


def test_q011fd_enumerates_registered_label_free_phase_inventory(
    q011fd_structure: dict[str, Any],
) -> None:
    allocation = q011fd_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == q011fd.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 8_350
    assert q011fd_structure["compatible_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011fd.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        5,
        2,
        0,
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
        7,
        0,
        0,
    ]
    assert allocation["individual_wave_allocation_count"] == 1_136
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011fd.EXPECTED_BRIDGE_RECORD_DIGEST
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
        q011fd.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011fd.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_thirty_nine_totals"] == [13, 9, 5, 7, 0]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    assert adapter["inactive_zero_count_source_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fd result is not sealed")
def test_q011fd_certifies_all_complex_phase_product_discs(
    q011fd_cycle: dict[str, Any],
) -> None:
    comparison = q011fd_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 38
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
    assert comparison["comparison_stream_domain"] == ("q011fd-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fd result is not sealed")
def test_q011fd_minimum_exact_phase_margin_is_fixed(
    q011fd_cycle: dict[str, Any],
) -> None:
    comparison = q011fd_cycle["complex_phase_product_disc_audit"]
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
    assert q011fd.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fd result is not sealed")
def test_q011fd_records_scoped_resolution(
    q011fd_cycle: dict[str, Any],
) -> None:
    assert q011fd_cycle["study_validity"] == "passed"
    assert q011fd_cycle["failed_validity_order"] == []
    assert q011fd_cycle["failed_diagnostic_order"] == []
    assert len(q011fd_cycle["validity_gates"]) == 7
    assert len(q011fd_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011fd_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fd_cycle["diagnostic_gates"].values())
    assert q011fd_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011fd_cycle["diagnostic_classification"] == q011fd.RESOLVED_CLASSIFICATION
    assert q011fd_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fd_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011fc" in q011fd_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011fd_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fd result is not sealed")
def test_q011fd_preserves_scientific_boundary(q011fd_cycle: dict[str, Any]) -> None:
    theorem = q011fd_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_fortieth_q011cb_witness"],
        theorem["fortieth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert flags == (True, False)
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011fc_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 39" in q011fd_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 37" in q011fd_cycle["claim_boundary"]
    assert "later 44761 Q011cb refined signatures" in q011fd_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011fd_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fd result is not sealed")
def test_q011fd_cycle_has_strict_reproducible_digests(
    q011fd_cycle: dict[str, Any],
) -> None:
    json.dumps(q011fd_cycle, allow_nan=False)
    assert {name: q011fd_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011fd_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011fd_cycle["result_digest_sha256"] == (
        q011fd.q011b._canonical_json_sha256(q011fd._result_digest_sections(q011fd_cycle))
    )
    assert q011fd._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fd result is not sealed")
def test_q011fd_study_metadata_and_optional_artifact_are_scoped(
    q011fd_study: dict[str, Any],
) -> None:
    assert q011fd_study["schema_version"] == 1
    assert q011fd_study["source"] == source_metadata()
    assert q011fd_study["study_gate"] == "passed"
    assert q011fd_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011fd_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fd_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 38
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fd_study, allow_nan=False)

    runner_path = Path(q011fd.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fd_degree34_fortieth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fd artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fd_study["refinement_outcome"]
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fd.q011b._canonical_json_sha256(q011fd._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
