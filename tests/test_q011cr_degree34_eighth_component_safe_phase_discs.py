from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cr_degree34_eighth_component_safe_phase_discs as q011cr
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "d265da23bd141cdb5443d3e5bcb54bebb7b5ed1ad8304985d4318a5a6ddf57eb"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "6e853a3741d3991a59f6b7d8c7411093644632aa1ba5b7aabd3b7202a64f74a6",
    "phase_input_digest_sha256": (
        "cef9571348256c679e762bf37fba8c6faeeb4a2b548579a19bd1b552d5120bef"
    ),
    "allocation_digest_sha256": (
        "2707b2abb6dc62941875df0e8668d6ffb9806c0bb0f74881f09ffe43d5e13624"
    ),
    "phase_comparison_digest_sha256": (
        "efee535088f9346da34e5bc34422dbaa44cc3e4336c8688567e77855ca45c278"
    ),
    "result_digest_sha256": "f0970e264e06ba3823e8eceda49ff5f25119103bdcd022799172ef2758b4b751",
}
EXPECTED_STREAM_DIGEST = "ace864d2f117bc109141bbc5f901e9effd3581c86e422f149d8c7bd1534e842f"
EXPECTED_MINIMUM_WITNESS_DIGEST = "df9e0c42e0cdb8d82a309c61e2bf95d5d6369af757654dbbf5ad38e822695d1a"


@pytest.fixture(scope="module")
def q011cr_study() -> dict[str, Any]:
    return q011cr.run_q011cr_study()


@pytest.fixture(scope="module")
def q011cr_cycle(q011cr_study: dict[str, Any]) -> dict[str, Any]:
    return q011cr_study["cycle"]


def test_q011cr_seals_q011cq_and_all_prior_inputs(
    q011cr_cycle: dict[str, Any],
) -> None:
    sealed = q011cr_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 74
    assert sealed["direct_digest_count"] == 345
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cq"]["digests"]) == q011cr.Q011CQ_DIGESTS
    assert sealed["q011cq"]["artifact_sha256"] == q011cr.Q011CQ_ARTIFACT_SHA256
    assert sealed["q011cq"]["runner_sha256"] == q011cr.Q011CQ_RUNNER_SHA256


def test_q011cr_reconstructs_component_safe_phase_discs(
    q011cr_cycle: dict[str, Any],
) -> None:
    fixed = q011cr_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 7
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cr.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cr.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011cr.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011cr.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cq_compatible_wave_allocation_count"] == 382
    assert fixed["q011cq_compatible_wave_allocation_digest_sha256"] == (
        q011cr.q011cq.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cr._protocol_globals_are_restored()


def test_q011cr_enumerates_registered_label_free_phase_inventory(
    q011cr_cycle: dict[str, Any],
) -> None:
    allocation = q011cr_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011cr.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cr.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cr.EXPECTED_WAVE_PROJECTION_DIGEST
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


def test_q011cr_certifies_all_complex_phase_product_discs(
    q011cr_cycle: dict[str, Any],
) -> None:
    comparison = q011cr_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 7
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
    assert comparison["comparison_stream_domain"] == ("q011cr-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cr_minimum_exact_phase_margin_is_fixed(
    q011cr_cycle: dict[str, Any],
) -> None:
    comparison = q011cr_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 5_408
    assert witness["counts"] == [11, 2, 0, 6, 0, 3, 0, 5, 5, 2, 0, 0]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc89e6p-6")
    assert q011cr.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cr_records_scoped_resolution(q011cr_cycle: dict[str, Any]) -> None:
    assert q011cr_cycle["study_validity"] == "passed"
    assert q011cr_cycle["failed_validity_order"] == []
    assert q011cr_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cr_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cr_cycle["diagnostic_gates"].values())
    assert q011cr_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cr_cycle["diagnostic_classification"] == q011cr.RESOLVED_CLASSIFICATION
    assert q011cr_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cr_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011cs" in q011cr_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cr_cycle["next_change"]


def test_q011cr_preserves_scientific_boundary(q011cr_cycle: dict[str, Any]) -> None:
    theorem = q011cr_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_eighth_q011cb_witness"]
    assert not theorem["eighth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cq_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 7" in q011cr_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 6" in q011cr_cycle["claim_boundary"]
    assert "later 44792 Q011cb refined signatures" in q011cr_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cr_cycle["claim_boundary"]


def test_q011cr_cycle_has_strict_reproducible_digests(
    q011cr_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cr_cycle, allow_nan=False)
    assert {
        name: q011cr_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cr_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cr_cycle["result_digest_sha256"] == (
        q011cr.q011b._canonical_json_sha256(q011cr._result_digest_sections(q011cr_cycle))
    )
    assert q011cr._protocol_globals_are_restored()


def test_q011cr_study_metadata_and_optional_artifact_are_scoped(
    q011cr_study: dict[str, Any],
) -> None:
    assert q011cr_study["schema_version"] == 1
    assert q011cr_study["source"] == source_metadata()
    assert q011cr_study["study_gate"] == "passed"
    assert q011cr_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cr_study["scientific_outcome"] == "not_evaluated"
    assert q011cr_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cr_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cr_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 7
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cr_study, allow_nan=False)

    runner_path = Path(q011cr.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / ("q011cr_degree34_eighth_component_safe_phase_discs.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cr artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cr_degree34_eighth_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cr.q011b._canonical_json_sha256(q011cr._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
