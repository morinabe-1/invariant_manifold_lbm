from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dj_degree34_seventeenth_component_safe_phase_discs as q011dj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "59973034ab88e317a3d5541ae474d8b3eed4aecdd7a41da36ab3238911b9f82c"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "64900b2bd91ceb69c34aef4592bab523d513e0487e2d67cb6c41eab825985e5f"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "12e91935b8f07b1449d7ea78c06e9f5c4facb8424540f59f9e53eeb1e59d8d07",
    "phase_input_digest_sha256": (
        "fde4828d0dd2b9d1bf418f0550185e1b0f7da02c2332637c4078302f87b43d2d"
    ),
    "allocation_digest_sha256": (
        "6077d77bfbc98a47894d5ad83e5e2748409735defbed2ad032bca44c131df865"
    ),
    "phase_comparison_digest_sha256": (
        "6ea63be6fda4c1b17d019ec57415a8ca912a3df43e1acf53fb12e2eac82d7f7f"
    ),
    "result_digest_sha256": "a45f87e8ab5939440915423ba118622f713e6d5d985dca120290152daef94301",
}
EXPECTED_STREAM_DIGEST = "0bf39a8f57e3ed3c29d408e66b1a365994d59749afbd3c08223dcf51a7ea4940"
EXPECTED_MINIMUM_WITNESS_DIGEST = "0608c0d35f60903eea1f58ee9ea5f3f8fef345e97babcf53abee39f14fa1aa0d"


@pytest.fixture(scope="module")
def q011dj_study() -> dict[str, Any]:
    return q011dj.run_q011dj_study()


@pytest.fixture(scope="module")
def q011dj_cycle(q011dj_study: dict[str, Any]) -> dict[str, Any]:
    return q011dj_study["cycle"]


def test_q011dj_seals_q011di_and_all_prior_inputs(
    q011dj_cycle: dict[str, Any],
) -> None:
    sealed = q011dj_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 92
    assert sealed["direct_digest_count"] == 426
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011di"]["digests"]) == q011dj.Q011DI_DIGESTS
    assert sealed["q011di"]["artifact_sha256"] == q011dj.Q011DI_ARTIFACT_SHA256
    assert sealed["q011di"]["runner_sha256"] == q011dj.Q011DI_RUNNER_SHA256


def test_q011dj_reconstructs_component_safe_phase_discs(
    q011dj_cycle: dict[str, Any],
) -> None:
    fixed = q011dj_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 16
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011dj.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011dj.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011dj.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011dj.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011di_compatible_wave_allocation_count"] == 911
    assert fixed["q011di_compatible_wave_allocation_digest_sha256"] == (
        q011dj.q011di.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011dj._protocol_globals_are_restored()


def test_q011dj_enumerates_registered_label_free_phase_inventory(
    q011dj_cycle: dict[str, Any],
) -> None:
    allocation = q011dj_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011dj.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011dj.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
        q011dj.EXPECTED_BRIDGE_RECORD_DIGEST
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
        q011dj.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011dj.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_sixteen_totals"] == [13, 9, 5, 0, 7]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011dj_certifies_all_complex_phase_product_discs(
    q011dj_cycle: dict[str, Any],
) -> None:
    comparison = q011dj_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 16
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
    assert comparison["comparison_stream_domain"] == ("q011dj-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011dj_minimum_exact_phase_margin_is_fixed(
    q011dj_cycle: dict[str, Any],
) -> None:
    comparison = q011dj_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 5_455
    assert witness["counts"] == [11, 2, 0, 9, 0, 0, 0, 5, 0, 0, 2, 5]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8463p-6")
    assert q011dj.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011dj_records_scoped_resolution(q011dj_cycle: dict[str, Any]) -> None:
    assert q011dj_cycle["study_validity"] == "passed"
    assert q011dj_cycle["failed_validity_order"] == []
    assert q011dj_cycle["failed_diagnostic_order"] == []
    assert len(q011dj_cycle["validity_gates"]) == 7
    assert len(q011dj_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011dj_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dj_cycle["diagnostic_gates"].values())
    assert q011dj_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011dj_cycle["diagnostic_classification"] == q011dj.RESOLVED_CLASSIFICATION
    assert q011dj_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dj_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011dk" in q011dj_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011dj_cycle["next_change"]


def test_q011dj_preserves_scientific_boundary(q011dj_cycle: dict[str, Any]) -> None:
    theorem = q011dj_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_seventeenth_q011cb_witness"]
    assert not theorem["seventeenth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011di_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 16" in q011dj_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 through 15" in q011dj_cycle["claim_boundary"]
    assert "later 44783 Q011cb refined signatures" in q011dj_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011dj_cycle["claim_boundary"]


def test_q011dj_cycle_has_strict_reproducible_digests(
    q011dj_cycle: dict[str, Any],
) -> None:
    json.dumps(q011dj_cycle, allow_nan=False)
    assert {name: q011dj_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011dj_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011dj_cycle["result_digest_sha256"] == (
        q011dj.q011b._canonical_json_sha256(q011dj._result_digest_sections(q011dj_cycle))
    )
    assert q011dj._protocol_globals_are_restored()


def test_q011dj_study_metadata_and_optional_artifact_are_scoped(
    q011dj_study: dict[str, Any],
) -> None:
    assert q011dj_study["schema_version"] == 1
    assert q011dj_study["source"] == source_metadata()
    assert q011dj_study["study_gate"] == "passed"
    assert q011dj_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011dj_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dj_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 16
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dj_study, allow_nan=False)

    runner_path = Path(q011dj.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dj_degree34_seventeenth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dj.q011b._canonical_json_sha256(q011dj._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
