from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dz_degree34_twenty_fifth_component_safe_phase_discs as q011dz
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "fdf8238a5215edd278ff910aa0f39173ebf62ff7f58959a8dbf7de948baa91a2"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "dc96fcc57e79780133c9ad44d2be9950f9e7cbe33c16534422f4d5b70e4fb17c"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "0ed79c2ceaea369a3583ada6f3d016cc5d3fb15c4cc41655722a49e2dc98a6ec",
    "phase_input_digest_sha256": (
        "9d724622303028bbcebd1dd46bdf619d7f92ac1633a7a26ee839bc5584045d57"
    ),
    "allocation_digest_sha256": (
        "a184330c67820dbf4cbbd6b9ddc6377b2e841cb26378c3074b854f39902a3c0f"
    ),
    "phase_comparison_digest_sha256": (
        "9e675472c48393a58153866b38deeb095265e985bb97a18ecea0a76e6906e1a8"
    ),
    "result_digest_sha256": "dcc3c4a5297015f76a414aae72925d7353429a9dc5579fe8729c33e3cd3a9696",
}
EXPECTED_STREAM_DIGEST = "f52202a2ca770f0eb89148d6468c1aaa3a9e79a039af2cece5c6faaa39c217d0"
EXPECTED_MINIMUM_WITNESS_DIGEST = "0608c0d35f60903eea1f58ee9ea5f3f8fef345e97babcf53abee39f14fa1aa0d"
EXPECTED_MINIMUM_INDEX: int | None = 5_455
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 9, 0, 0, 0, 5, 0, 0, 2, 5]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8463p-6"


@pytest.fixture(scope="module")
def q011dz_study() -> dict[str, Any]:
    return q011dz.run_q011dz_study()


@pytest.fixture(scope="module")
def q011dz_cycle(q011dz_study: dict[str, Any]) -> dict[str, Any]:
    return q011dz_study["cycle"]


def test_q011dz_seals_q011dy_and_all_prior_inputs(
    q011dz_cycle: dict[str, Any],
) -> None:
    sealed = q011dz_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 108
    assert sealed["direct_digest_count"] == 498
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dy"]["digests"]) == q011dz.Q011DY_DIGESTS
    assert sealed["q011dy"]["artifact_sha256"] == q011dz.Q011DY_ARTIFACT_SHA256
    assert sealed["q011dy"]["runner_sha256"] == q011dz.Q011DY_RUNNER_SHA256


def test_q011dz_reconstructs_component_safe_phase_discs(
    q011dz_cycle: dict[str, Any],
) -> None:
    fixed = q011dz_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 24
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011dz.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011dz.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011dz.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011dz.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011dy_compatible_wave_allocation_count"] == 1_061
    assert fixed["q011dy_compatible_wave_allocation_digest_sha256"] == (
        q011dz.q011dy.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011dz._protocol_globals_are_restored()


def test_q011dz_enumerates_registered_label_free_phase_inventory(
    q011dz_cycle: dict[str, Any],
) -> None:
    allocation = q011dz_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011dz.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011dz.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
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
    assert allocation["individual_wave_allocation_count"] == 1_061
    assert allocation["component_wave_projection_count"] == 382
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011dz.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 4
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 79,
        "2": 77,
        "3": 76,
        "4": 150,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 1_061
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011dz.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011dz.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert adapter["ordinal_twenty_four_totals"] == [13, 9, 5, 0, 7]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


def test_q011dz_certifies_all_complex_phase_product_discs(
    q011dz_cycle: dict[str, Any],
) -> None:
    comparison = q011dz_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 24
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
    assert comparison["comparison_stream_domain"] == ("q011dz-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011dz_minimum_exact_phase_margin_is_fixed(
    q011dz_cycle: dict[str, Any],
) -> None:
    if (
        EXPECTED_MINIMUM_INDEX is None
        or EXPECTED_MINIMUM_COUNTS is None
        or EXPECTED_MINIMUM_MARGIN_HEX is None
    ):
        pytest.skip("Q011dz minimum witness has not been sealed yet")
    comparison = q011dz_cycle["complex_phase_product_disc_audit"]
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
    assert q011dz.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011dz_records_scoped_resolution(q011dz_cycle: dict[str, Any]) -> None:
    assert q011dz_cycle["study_validity"] == "passed"
    assert q011dz_cycle["failed_validity_order"] == []
    assert q011dz_cycle["failed_diagnostic_order"] == []
    assert len(q011dz_cycle["validity_gates"]) == 7
    assert len(q011dz_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011dz_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dz_cycle["diagnostic_gates"].values())
    assert q011dz_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011dz_cycle["diagnostic_classification"] == q011dz.RESOLVED_CLASSIFICATION
    assert q011dz_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dz_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ea" in q011dz_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011dz_cycle["next_change"]


def test_q011dz_preserves_scientific_boundary(q011dz_cycle: dict[str, Any]) -> None:
    theorem = q011dz_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_twenty_fifth_q011cb_witness"]
    assert not theorem["twenty_fifth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011dy_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert theorem["q011dw_ordinal_twenty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dv_ordinal_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 24" in q011dz_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 23" in q011dz_cycle["claim_boundary"]
    assert "later 44775 Q011cb refined signatures" in q011dz_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011dz_cycle["claim_boundary"]


def test_q011dz_cycle_has_strict_reproducible_digests(
    q011dz_cycle: dict[str, Any],
) -> None:
    if not all(EXPECTED_SECTION_DIGESTS.values()) or not EXPECTED_STREAM_DIGEST:
        pytest.skip("Q011dz section digests have not been sealed yet")
    json.dumps(q011dz_cycle, allow_nan=False)
    assert {name: q011dz_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011dz_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011dz_cycle["result_digest_sha256"] == (
        q011dz.q011b._canonical_json_sha256(q011dz._result_digest_sections(q011dz_cycle))
    )
    assert q011dz._protocol_globals_are_restored()


def test_q011dz_study_metadata_and_optional_artifact_are_scoped(
    q011dz_study: dict[str, Any],
) -> None:
    assert q011dz_study["schema_version"] == 1
    assert q011dz_study["source"] == source_metadata()
    assert q011dz_study["study_gate"] == "passed"
    assert q011dz_study["refinement_outcome"] == "component_safe_phase_resolved"
    runtime = q011dz_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["full_comparison_records_retained"] is False
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dz_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 24
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dz_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011dz runner hash has not been sealed yet")
    runner_path = Path(q011dz.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dz_degree34_twenty_fifth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dz artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert (
        artifact["cycle"]["complex_phase_product_disc_audit"]["comparison_stream_digest_sha256"]
        == EXPECTED_STREAM_DIGEST
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dz.q011b._canonical_json_sha256(q011dz._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
