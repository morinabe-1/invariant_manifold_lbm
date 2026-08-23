from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011il_degree34_eighty_third_component_safe_phase_discs as q011il
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "5767494916b6ad0d01ad7aafe74882cd064e6c3e8a99aa4a8f07e8a1a6237fbd"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "cd455c9ee825b7a73a8b10891ad4deaff4991abdcd7b4d5756186e9f64b890fd"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "b3b08c7d75a29a1c2123985ba55ca56170ae0a65f1a82bc8bbbbefbedaa240a3",
    "phase_input_digest_sha256": (
        "f420e6f0bf417f69b87ae37db4c48c9369ee9a1f665244d14acc9cc18f035919"
    ),
    "allocation_digest_sha256": (
        "377a59852525603af2eb10ebf0f9b37c74cbb872ee3adb33497cc99851d6b2c0"
    ),
    "phase_comparison_digest_sha256": (
        "be9200823248d783ea1a03634cbfd32764c1308cd438b8295235767de628cb21"
    ),
    "result_digest_sha256": ("46b7c0c47cd3573783d17a73e04952bd556d2224096ca1bacd6154f906ab4902"),
}
EXPECTED_STREAM_DIGEST: str | None = (
    "f98ed058291899c5e346c5ce54724fe0e84d6df67c91ad4016ca9ebd60e1aec0"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "205aeac7dcb616fcd85ad87e4567d590f9b0b906422e3fd814ad9b05a08f1281"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_256
EXPECTED_MINIMUM_COUNTS: list[int] | None = [
    0,
    1,
    10,
    2,
    0,
    8,
    0,
    1,
    0,
    5,
    2,
    0,
    2,
    3,
]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc85edp-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 34_182,
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
def q011il_structure() -> dict[str, Any]:
    sealed, artifacts = q011il._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011il._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011il._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011il_study() -> dict[str, Any]:
    return q011il.run_q011il_study()


@pytest.fixture(scope="module")
def q011il_cycle(q011il_study: dict[str, Any]) -> dict[str, Any]:
    return q011il_study["cycle"]


def test_q011il_seals_q011ik_and_all_prior_inputs(
    q011il_structure: dict[str, Any],
) -> None:
    sealed = q011il_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 224
    assert sealed["direct_digest_count"] == 1_020
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ik"]["digests"]) == q011il.Q011IK_DIGESTS
    assert sealed["q011ik"]["artifact_sha256"] == q011il.Q011IK_ARTIFACT_SHA256
    assert sealed["q011ik"]["runner_sha256"] == q011il.Q011IK_RUNNER_SHA256


def test_q011il_reconstructs_component_safe_phase_discs(
    q011il_structure: dict[str, Any],
) -> None:
    fixed = q011il_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 82
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 14
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011il.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011il.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011il.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011il.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ik_compatible_wave_allocation_count"] == 1_560
    assert fixed["q011ik_compatible_wave_allocation_digest_sha256"] == (
        q011il.q011ik.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011il._protocol_globals_are_restored()


def test_q011il_enumerates_registered_label_free_phase_inventory(
    q011il_structure: dict[str, Any],
) -> None:
    allocation = q011il_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == (q011il.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011il.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == (q011il.EXPECTED_FIRST_COMPATIBLE_COUNTS)
    assert tuple(allocation["last_compatible_counts"]) == (q011il.EXPECTED_LAST_COMPATIBLE_COUNTS)
    assert allocation["individual_wave_allocation_count"] == 1_560
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011il.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 1_560,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011il.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011il.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 321,
        "18": 311,
        "24": 308,
        "28": 309,
        "30": 311,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 34_182
    )
    assert q011il_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_eighty_two_totals"] == [1, 12, 9, 5, 2, 5]
    assert adapter["all_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011il result is not sealed")
def test_q011il_classifies_all_complex_phase_product_discs(
    q011il_cycle: dict[str, Any],
) -> None:
    comparison = q011il_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011il-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011il result is not sealed")
def test_q011il_minimum_exact_phase_margin_is_fixed(
    q011il_cycle: dict[str, Any],
) -> None:
    witness = q011il_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011il result is not sealed")
def test_q011il_applies_stopping_rule_and_preserves_boundary(
    q011il_cycle: dict[str, Any],
) -> None:
    assert q011il_cycle["study_validity"] == "passed"
    assert q011il_cycle["failed_validity_order"] == []
    assert q011il_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011il_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011il_cycle["diagnostic_gates"].values())
    assert q011il_cycle["scientific_outcome"] == "not_evaluated"
    assert q011il_cycle["actual_resonance_outcome"] == "not_established"
    assert q011il_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011il.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011il.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011il_cycle["diagnostic_classification"] == expected
    theorem = q011il_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_eighty_third_q011cb_witness"],
        theorem["eighty_third_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011ik_ordinal_eighty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 82" in q011il_cycle["claim_boundary"]
    assert "ordinals 0 through 81" in q011il_cycle["claim_boundary"]
    assert "later 44717 Q011cb refined signatures" in q011il_cycle["claim_boundary"]
    assert "Q011im" in q011il_cycle["next_change"]
    assert {name: q011il_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011il_cycle["result_digest_sha256"] == (
        q011il.q011b._canonical_json_sha256(q011il._result_digest_sections(q011il_cycle))
    )
    assert q011il._protocol_globals_are_restored()
    json.dumps(q011il_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011il result is not sealed")
def test_q011il_study_metadata_and_optional_artifact_are_scoped(
    q011il_study: dict[str, Any],
) -> None:
    assert q011il_study["schema_version"] == 1
    assert q011il_study["source"] == source_metadata()
    assert q011il_study["study_gate"] == "passed"
    assert q011il_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011il_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011il_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 82
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011il_study, allow_nan=False)

    runner_path = Path(q011il.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011il_degree34_eighty_third_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011il artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011il_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011il.q011b._canonical_json_sha256(q011il._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
