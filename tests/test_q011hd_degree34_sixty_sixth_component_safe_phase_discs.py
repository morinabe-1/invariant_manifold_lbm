from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hd_degree34_sixty_sixth_component_safe_phase_discs as q011hd
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "56cb62520d3705002a340c6ed87d92bfe56cd0af678b0c6e0256064450e76273"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "655c411c045e164d6b1cf178ed39fb90008059272e2be3485d6e56c604fc2bd3"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "da1c49a13be67d0d195b020c311bb3d035ca955abe9c9874e3e9fe0484fce6cc",
    "phase_input_digest_sha256": "3c139be557ecd72d38d83fbbae340bc40115264dbac3bf9625614e5cc8cb4dde",
    "allocation_digest_sha256": "783ec3db7be03734c7fa51eb2ca17dbad5ee45cd2f75beb42c69df8340647c01",
    "phase_comparison_digest_sha256": "337341dfdc553fbf705beafb25d0fbc59b5a9c2b72697737465195debd02ffc6",
    "result_digest_sha256": "5b543aa4bb6bcfb0267986d1f9b040664f6592254fb0dd0a1d169cccedcd4519",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "de9ff8ccfc8de4fdd2b89260a85582233b37a623bca548f9b36ec751c308bb35"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "57badc5d7675b78362958718cfc68036f87a34d11f88fe4cdd88c7c264932e3c"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_298
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 8, 0, 1, 0, 5, 1, 0, 2, 4]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc84e1p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 14_578,
    "unresolved_product_disk_overlap": 0,
}
EXPECTED_REFINEMENT_OUTCOME: str | None = "component_safe_phase_resolved"
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
        EXPECTED_CATEGORY_COUNTS,
        EXPECTED_REFINEMENT_OUTCOME,
    )
)


@pytest.fixture(scope="module")
def q011hd_structure() -> dict[str, Any]:
    sealed, artifacts = q011hd._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011hd._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011hd._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011hd_study() -> dict[str, Any]:
    return q011hd.run_q011hd_study()


@pytest.fixture(scope="module")
def q011hd_cycle(q011hd_study: dict[str, Any]) -> dict[str, Any]:
    return q011hd_study["cycle"]


def test_q011hd_seals_q011hc_and_all_prior_inputs(
    q011hd_structure: dict[str, Any],
) -> None:
    sealed = q011hd_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 190
    assert sealed["direct_digest_count"] == 867
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hc"]["digests"]) == q011hd.Q011HC_DIGESTS
    assert sealed["q011hc"]["artifact_sha256"] == q011hd.Q011HC_ARTIFACT_SHA256
    assert sealed["q011hc"]["runner_sha256"] == q011hd.Q011HC_RUNNER_SHA256


def test_q011hd_reconstructs_component_safe_phase_discs(
    q011hd_structure: dict[str, Any],
) -> None:
    fixed = q011hd_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 65
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011hd.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011hd.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011hd.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011hd.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011hc_compatible_wave_allocation_count"] == 1_194
    assert fixed["q011hc_compatible_wave_allocation_digest_sha256"] == (
        q011hd.q011hc.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011hd._protocol_globals_are_restored()


def test_q011hd_enumerates_registered_label_free_phase_inventory(
    q011hd_structure: dict[str, Any],
) -> None:
    allocation = q011hd_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 258_720
    assert allocation["full_allocation_digest_sha256"] == q011hd.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 14_578
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011hd.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 0, 1, 5, 1]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 1, 0, 6]
    assert allocation["individual_wave_allocation_count"] == 1_194
    assert allocation["component_wave_projection_count"] == 665
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011hd.EXPECTED_BRIDGE_RECORD_DIGEST
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
        q011hd.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 665
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011hd.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011hd_structure["compatible_count"] == 14_578
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_sixty_five_totals"] == [13, 9, 5, 1, 6]
    assert adapter["zero_multiplicity_component_wave_identifiers"] == []
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hd result is not sealed")
def test_q011hd_classifies_all_complex_phase_product_discs(
    q011hd_cycle: dict[str, Any],
) -> None:
    comparison = q011hd_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 14_578
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 14_578
    assert comparison["comparison_stream_count"] == 14_578
    assert comparison["comparison_stream_domain"] == "q011hd-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 14_578,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hd result is not sealed")
def test_q011hd_minimum_exact_phase_margin_is_fixed(
    q011hd_cycle: dict[str, Any],
) -> None:
    comparison = q011hd_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    assert q011hd.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hd result is not sealed")
def test_q011hd_records_scoped_outcome(q011hd_cycle: dict[str, Any]) -> None:
    assert q011hd_cycle["study_validity"] == "passed"
    assert q011hd_cycle["failed_validity_order"] == []
    assert q011hd_cycle["failed_diagnostic_order"] == []
    assert len(q011hd_cycle["validity_gates"]) == 7
    assert len(q011hd_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011hd_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hd_cycle["diagnostic_gates"].values())
    assert q011hd_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    assert q011hd_cycle["diagnostic_classification"] == q011hd.RESOLVED_CLASSIFICATION
    assert q011hd_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hd_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011he" in q011hd_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011hd_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hd result is not sealed")
def test_q011hd_preserves_scientific_boundary(q011hd_cycle: dict[str, Any]) -> None:
    theorem = q011hd_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_sixty_sixth_q011cb_witness"]
    assert not theorem["sixty_sixth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011hc_ordinal_sixty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hb_ordinal_sixty_four_phase_resolution_is_preserved"]
    assert theorem["q011ha_ordinal_sixty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gz_ordinal_sixty_three_phase_resolution_is_preserved"]
    assert theorem["q011gy_ordinal_sixty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gx_ordinal_sixty_two_phase_resolution_is_preserved"]
    assert theorem["q011gw_ordinal_sixty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gv_ordinal_sixty_one_phase_resolution_is_preserved"]
    assert theorem["q011gu_ordinal_sixty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gt_ordinal_sixty_phase_resolution_is_preserved"]
    assert theorem["q011gs_ordinal_sixty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gr_ordinal_fifty_nine_phase_resolution_is_preserved"]
    assert theorem["q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 65" in q011hd_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 64" in q011hd_cycle["claim_boundary"]
    assert "later 44734 Q011cb refined signatures" in q011hd_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011hd_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hd result is not sealed")
def test_q011hd_cycle_has_strict_reproducible_digests(
    q011hd_cycle: dict[str, Any],
) -> None:
    json.dumps(q011hd_cycle, allow_nan=False)
    assert {name: q011hd_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011hd_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011hd_cycle["result_digest_sha256"] == (
        q011hd.q011b._canonical_json_sha256(q011hd._result_digest_sections(q011hd_cycle))
    )
    assert q011hd._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hd result is not sealed")
def test_q011hd_study_metadata_and_optional_artifact_are_scoped(
    q011hd_study: dict[str, Any],
) -> None:
    assert q011hd_study["schema_version"] == 1
    assert q011hd_study["source"] == source_metadata()
    assert q011hd_study["study_gate"] == "passed"
    assert q011hd_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hd_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 14_578
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hd_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 65
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hd_study, allow_nan=False)

    runner_path = Path(q011hd.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hd_degree34_sixty_sixth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hd artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hd_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hd.q011b._canonical_json_sha256(q011hd._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
