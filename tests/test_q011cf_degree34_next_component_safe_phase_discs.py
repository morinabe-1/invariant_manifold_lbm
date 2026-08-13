from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cf_degree34_next_component_safe_phase_discs as q011cf
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "d6c7af8fa781d80ac0dfc5a446a810ed45c5d6981b64a9aa0eb33d0d6efdb94b"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "9f6817900b519a4c4305ca4e5f8cdedf1dfc7900532588f245907378e84c2c60",
    "phase_input_digest_sha256": (
        "7ffe9b7e9f4a0364aecec556249dad7ae91607c1f37a5d7cfa67d6fbefa1cb41"
    ),
    "allocation_digest_sha256": (
        "b6791697c4f0e6d0b6a966c01e35ae89ae0afd71e1cc07917358e0adae6cd267"
    ),
    "phase_comparison_digest_sha256": (
        "5242d2d9696585e2754013b14b5583f22c0f00d80503dbf8aa380a4ec07e94f9"
    ),
    "result_digest_sha256": "d7724710c591f1c63abec70cb7e9e37bfc1f45d3a4f1165b3f7b3ec6eed5c490",
}
EXPECTED_STREAM_DIGEST = "e96de25a6f164de2af6b78be68217dfb33deba343594621d550a0ec6dd2a24eb"
EXPECTED_MINIMUM_WITNESS_DIGEST = "57badc5d7675b78362958718cfc68036f87a34d11f88fe4cdd88c7c264932e3c"


@pytest.fixture(scope="module")
def q011cf_study() -> dict[str, Any]:
    return q011cf.run_q011cf_study()


@pytest.fixture(scope="module")
def q011cf_cycle(q011cf_study: dict[str, Any]) -> dict[str, Any]:
    return q011cf_study["cycle"]


def test_q011cf_seals_q011ce_and_all_prior_inputs(
    q011cf_cycle: dict[str, Any],
) -> None:
    sealed = q011cf_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 62
    assert sealed["direct_digest_count"] == 291
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ce"]["digests"]) == q011cf.Q011CE_DIGESTS
    assert sealed["q011ce"]["artifact_sha256"] == q011cf.Q011CE_ARTIFACT_SHA256
    assert sealed["q011ce"]["runner_sha256"] == q011cf.Q011CE_RUNNER_SHA256


def test_q011cf_reconstructs_component_safe_phase_discs(
    q011cf_cycle: dict[str, Any],
) -> None:
    fixed = q011cf_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 1
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cf.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cf.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011cf.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011cf.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011ce_compatible_wave_allocation_count"] == 665
    assert fixed["q011ce_compatible_wave_allocation_digest_sha256"] == (
        q011cf.q011ce.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]


def test_q011cf_enumerates_registered_label_free_phase_inventory(
    q011cf_cycle: dict[str, Any],
) -> None:
    allocation = q011cf_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == (q011cf.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cf.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cf.EXPECTED_WAVE_PROJECTION_DIGEST
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


def test_q011cf_certifies_all_complex_phase_product_discs(
    q011cf_cycle: dict[str, Any],
) -> None:
    comparison = q011cf_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 1
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
    assert comparison["comparison_stream_domain"] == ("q011cf-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signature_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cf_minimum_exact_phase_margin_is_fixed(
    q011cf_cycle: dict[str, Any],
) -> None:
    comparison = q011cf_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 9298
    assert witness["counts"] == [11, 2, 0, 8, 0, 1, 0, 5, 1, 0, 2, 4]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc84e1p-6")
    assert q011cf.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cf_records_scoped_resolution(q011cf_cycle: dict[str, Any]) -> None:
    assert q011cf_cycle["study_validity"] == "passed"
    assert q011cf_cycle["failed_validity_order"] == []
    assert q011cf_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cf_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cf_cycle["diagnostic_gates"].values())
    assert q011cf_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cf_cycle["diagnostic_classification"] == q011cf.RESOLVED_CLASSIFICATION
    assert q011cf_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cf_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011cg" in q011cf_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cf_cycle["next_change"]


def test_q011cf_preserves_scientific_boundary(q011cf_cycle: dict[str, Any]) -> None:
    theorem = q011cf_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_next_q011cb_witness"]
    assert not theorem["next_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011ce_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cd_first_witness_phase_resolution_is_preserved"]
    assert theorem["q011cb_persistent_diagnostic_is_preserved"]
    assert theorem["q011ca_first_family_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 1" in q011cf_cycle["claim_boundary"]
    assert "does not reevaluate ordinal 0" in q011cf_cycle["claim_boundary"]
    assert "later 44798 Q011cb refined signatures" in q011cf_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cf_cycle["claim_boundary"]


def test_q011cf_cycle_has_strict_reproducible_digests(
    q011cf_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cf_cycle, allow_nan=False)
    assert {
        name: q011cf_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cf_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cf_cycle["result_digest_sha256"] == (
        q011cf.q011b._canonical_json_sha256(q011cf._result_digest_sections(q011cf_cycle))
    )


def test_q011cf_study_metadata_and_optional_artifact_are_scoped(
    q011cf_study: dict[str, Any],
) -> None:
    assert q011cf_study["schema_version"] == 1
    assert q011cf_study["source"] == source_metadata()
    assert q011cf_study["study_gate"] == "passed"
    assert q011cf_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cf_study["scientific_outcome"] == "not_evaluated"
    assert q011cf_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cf_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["floating_point_used_for_gate_decisions"] is False
    scope = q011cf_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 1
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cf_study, allow_nan=False)

    runner_path = Path(q011cf.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / ("q011cf_degree34_next_component_safe_phase_discs.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cf artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cf_degree34_next_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cf.q011b._canonical_json_sha256(q011cf._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
