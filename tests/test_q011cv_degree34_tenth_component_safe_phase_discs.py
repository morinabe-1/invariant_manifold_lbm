from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cv_degree34_tenth_component_safe_phase_discs as q011cv
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "3f88ba3957e7264dc3022064b18253345a8734809acae3ac67bb7a19d3aa7e93"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "814dded17756cac9789135a02ff47f45c0f9c2c8b4b8d150615d88d0e3f487a1"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "962c6f314491a754d7aa81ba0301dd27f4b581827f88900ba85cb3b3d20bbfb1",
    "phase_input_digest_sha256": (
        "b8687cb4c045ecf8c04f6c5e78805f768a9c95387b9f7c28290b3c16792a8f22"
    ),
    "allocation_digest_sha256": (
        "b7b7c8b3b4b664becc1c742a6d93306e4a47cf0daf2aa7ef353d0e5d2428990d"
    ),
    "phase_comparison_digest_sha256": (
        "12ab16379754c563c29fc33e19b8b95b5608c6867e8f0e09df6b92259107ce89"
    ),
    "result_digest_sha256": "bed61f2d914a190bf44a8acb8a17c3267ab88850bfae60c0d54cde9b4836a4bc",
}
EXPECTED_STREAM_DIGEST = "6e0b2f61a2d1e81a9d7225c27e2b6be115b5b2c45709b35da9216f74d3543378"
EXPECTED_MINIMUM_WITNESS_DIGEST = "57badc5d7675b78362958718cfc68036f87a34d11f88fe4cdd88c7c264932e3c"


@pytest.fixture(scope="module")
def q011cv_study() -> dict[str, Any]:
    return q011cv.run_q011cv_study()


@pytest.fixture(scope="module")
def q011cv_cycle(q011cv_study: dict[str, Any]) -> dict[str, Any]:
    return q011cv_study["cycle"]


def test_q011cv_seals_q011cu_and_all_prior_inputs(
    q011cv_cycle: dict[str, Any],
) -> None:
    sealed = q011cv_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 78
    assert sealed["direct_digest_count"] == 363
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cu"]["digests"]) == q011cv.Q011CU_DIGESTS
    assert sealed["q011cu"]["artifact_sha256"] == q011cv.Q011CU_ARTIFACT_SHA256
    assert sealed["q011cu"]["runner_sha256"] == q011cv.Q011CU_RUNNER_SHA256


def test_q011cv_reconstructs_component_safe_phase_discs(
    q011cv_cycle: dict[str, Any],
) -> None:
    fixed = q011cv_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 9
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cv.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cv.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011cv.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011cv.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cu_compatible_wave_allocation_count"] == 1_194
    assert fixed["q011cu_compatible_wave_allocation_digest_sha256"] == (
        q011cv.q011cu.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011cv._protocol_globals_are_restored()


def test_q011cv_enumerates_registered_label_free_phase_inventory(
    q011cv_cycle: dict[str, Any],
) -> None:
    allocation = q011cv_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == q011cv.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cv.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 0, 1, 5, 1]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 1, 0, 6]
    assert allocation["individual_wave_allocation_count"] == 1_194
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011cv.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 136,
        "2": 529,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_194
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011cv.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cv.EXPECTED_WAVE_PROJECTION_DIGEST
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


def test_q011cv_certifies_all_complex_phase_product_discs(
    q011cv_cycle: dict[str, Any],
) -> None:
    comparison = q011cv_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 9
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
    assert comparison["comparison_stream_domain"] == ("q011cv-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011cv_minimum_exact_phase_margin_is_fixed(
    q011cv_cycle: dict[str, Any],
) -> None:
    comparison = q011cv_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 9_298
    assert witness["counts"] == [11, 2, 0, 8, 0, 1, 0, 5, 1, 0, 2, 4]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc84e1p-6")
    assert q011cv.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cv_records_scoped_resolution(q011cv_cycle: dict[str, Any]) -> None:
    assert q011cv_cycle["study_validity"] == "passed"
    assert q011cv_cycle["failed_validity_order"] == []
    assert q011cv_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cv_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cv_cycle["diagnostic_gates"].values())
    assert q011cv_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cv_cycle["diagnostic_classification"] == q011cv.RESOLVED_CLASSIFICATION
    assert q011cv_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cv_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011cw" in q011cv_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cv_cycle["next_change"]


def test_q011cv_preserves_scientific_boundary(q011cv_cycle: dict[str, Any]) -> None:
    theorem = q011cv_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_tenth_q011cb_witness"]
    assert not theorem["tenth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cu_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 9" in q011cv_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 8" in q011cv_cycle["claim_boundary"]
    assert "later 44790 Q011cb refined signatures" in q011cv_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cv_cycle["claim_boundary"]


def test_q011cv_cycle_has_strict_reproducible_digests(
    q011cv_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cv_cycle, allow_nan=False)
    assert {
        name: q011cv_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cv_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cv_cycle["result_digest_sha256"] == (
        q011cv.q011b._canonical_json_sha256(q011cv._result_digest_sections(q011cv_cycle))
    )
    assert q011cv._protocol_globals_are_restored()


def test_q011cv_study_metadata_and_optional_artifact_are_scoped(
    q011cv_study: dict[str, Any],
) -> None:
    assert q011cv_study["schema_version"] == 1
    assert q011cv_study["source"] == source_metadata()
    assert q011cv_study["study_gate"] == "passed"
    assert q011cv_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cv_study["scientific_outcome"] == "not_evaluated"
    assert q011cv_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cv_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cv_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 9
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cv_study, allow_nan=False)

    runner_path = Path(q011cv.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / ("q011cv_degree34_tenth_component_safe_phase_discs.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cv artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cv_degree34_tenth_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cv.q011b._canonical_json_sha256(q011cv._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
