from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cp_degree34_seventh_component_safe_phase_discs as q011cp
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "5b678936cc1095faa7cb43d8e66900d0698a59cf317d12ddce55d37b5fb3ab18"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "06dc34b9f2aaf8fc1b6d41a6d55905056886fa3f8a1149b52d10203b7d381e96"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "d9c6a7d5b041b7bd6d9450909057c661953cbb34d601f9f877608b64e2eae5d1",
    "phase_input_digest_sha256": (
        "cfa6cfacbf58246791fdf7cbc89b3b05ec0a261bd226c4adce08105688a3280e"
    ),
    "allocation_digest_sha256": (
        "1e5ca23bb127c01ec823f65012d05821ff3de229289155d4f4ec89d062a82075"
    ),
    "phase_comparison_digest_sha256": (
        "eaaac30c1fc4ba318ef0c6fd9ec2241a2b517934af8c29eebf4cd7b247864dc6"
    ),
    "result_digest_sha256": "66205c3fe78eb873817cfcbd3c06ed3e1f15aae8f2a668791523402deb59b301",
}
EXPECTED_STREAM_DIGEST = "a4f98b1f04ba8060597dcf31fbce4d5408304082a77020744cb59cb1807aed21"
EXPECTED_MINIMUM_WITNESS_DIGEST = "1b7f6cc19a74cdefa602f28a6251f0c9b874cdd0a3a9b6f7ee438ea4618fea8d"


@pytest.fixture(scope="module")
def q011cp_study() -> dict[str, Any]:
    return q011cp.run_q011cp_study()


@pytest.fixture(scope="module")
def q011cp_cycle(q011cp_study: dict[str, Any]) -> dict[str, Any]:
    return q011cp_study["cycle"]


def test_q011cp_seals_q011co_and_all_prior_inputs(
    q011cp_cycle: dict[str, Any],
) -> None:
    sealed = q011cp_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 72
    assert sealed["direct_digest_count"] == 336
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011co"]["digests"]) == q011cp.Q011CO_DIGESTS
    assert sealed["q011co"]["artifact_sha256"] == q011cp.Q011CO_ARTIFACT_SHA256
    assert sealed["q011co"]["runner_sha256"] == q011cp.Q011CO_RUNNER_SHA256


def test_q011cp_reconstructs_component_safe_phase_discs(
    q011cp_cycle: dict[str, Any],
) -> None:
    fixed = q011cp_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 6
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cp.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cp.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011cp.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011cp.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011co_compatible_wave_allocation_count"] == 665
    assert fixed["q011co_compatible_wave_allocation_digest_sha256"] == (
        q011cp.q011co.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cp._protocol_globals_are_restored()


def test_q011cp_enumerates_registered_label_free_phase_inventory(
    q011cp_cycle: dict[str, Any],
) -> None:
    allocation = q011cp_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == (q011cp.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cp.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cp.EXPECTED_WAVE_PROJECTION_DIGEST
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


def test_q011cp_certifies_all_complex_phase_product_discs(
    q011cp_cycle: dict[str, Any],
) -> None:
    comparison = q011cp_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 6
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
    assert comparison["comparison_stream_domain"] == ("q011cp-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cp_minimum_exact_phase_margin_is_fixed(
    q011cp_cycle: dict[str, Any],
) -> None:
    comparison = q011cp_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 9_166
    assert witness["counts"] == [11, 2, 0, 5, 0, 4, 0, 5, 5, 1, 1, 0]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8860p-6")
    assert q011cp.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cp_records_scoped_resolution(q011cp_cycle: dict[str, Any]) -> None:
    assert q011cp_cycle["study_validity"] == "passed"
    assert q011cp_cycle["failed_validity_order"] == []
    assert q011cp_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cp_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cp_cycle["diagnostic_gates"].values())
    assert q011cp_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cp_cycle["diagnostic_classification"] == q011cp.RESOLVED_CLASSIFICATION
    assert q011cp_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cp_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011cq" in q011cp_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cp_cycle["next_change"]


def test_q011cp_preserves_scientific_boundary(q011cp_cycle: dict[str, Any]) -> None:
    theorem = q011cp_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_seventh_q011cb_witness"]
    assert not theorem["seventh_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011co_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 6" in q011cp_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 5" in q011cp_cycle["claim_boundary"]
    assert "later 44793 Q011cb refined signatures" in q011cp_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cp_cycle["claim_boundary"]


def test_q011cp_cycle_has_strict_reproducible_digests(
    q011cp_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cp_cycle, allow_nan=False)
    assert {
        name: q011cp_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cp_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cp_cycle["result_digest_sha256"] == (
        q011cp.q011b._canonical_json_sha256(q011cp._result_digest_sections(q011cp_cycle))
    )
    assert q011cp._protocol_globals_are_restored()


def test_q011cp_study_metadata_and_optional_artifact_are_scoped(
    q011cp_study: dict[str, Any],
) -> None:
    assert q011cp_study["schema_version"] == 1
    assert q011cp_study["source"] == source_metadata()
    assert q011cp_study["study_gate"] == "passed"
    assert q011cp_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cp_study["scientific_outcome"] == "not_evaluated"
    assert q011cp_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cp_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cp_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 6
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cp_study, allow_nan=False)

    runner_path = Path(q011cp.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / ("q011cp_degree34_seventh_component_safe_phase_discs.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cp artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cp_degree34_seventh_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cp.q011b._canonical_json_sha256(q011cp._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
