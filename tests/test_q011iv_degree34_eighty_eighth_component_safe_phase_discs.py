from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011iv_degree34_eighty_eighth_component_safe_phase_discs as q011iv
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "65f5c84a12f2386de0fc45199d8378a1e9cfee918457f7a8e011700f451f8560"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "6add6acae4c214752ccad6e6e036df9efac1e2d6f9c3ab597ba9a4dafe0938b7"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "6a4fb12f03354c0bfb41ca0a2fe2bb28a4537c0190656feab52de9d63f8784a8",
    "phase_input_digest_sha256": (
        "627479d1d29b93777423739d67bfdf41367ec4d009b2d57054f22a333526c63e"
    ),
    "allocation_digest_sha256": (
        "49810352c6db0ca3652e59090caaa4edee57c406d03d4e145bbbcc5ac9405b62"
    ),
    "phase_comparison_digest_sha256": (
        "217499546b708b407bdff35f1db2715cafb6c63f80c455fd1127ad297bed668d"
    ),
    "result_digest_sha256": "f4ea5df6cbacdd3a33f1b8c6321ea3f866b74ef42d996e2d0478c8cba1796280",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "95202c011ffefe974fdbb239c15aa0888573f5cb671a561878fe76a7b64162a2"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "cba06ceb15335a288a1ea6e0d24caf4f450a26e54b3b51f5e46e84b7526d6868"
)
EXPECTED_MINIMUM_INDEX: int | None = 4_390
EXPECTED_MINIMUM_COUNTS: list[int] | None = [
    0,
    1,
    10,
    2,
    0,
    7,
    0,
    2,
    0,
    5,
    5,
    2,
    0,
    0,
]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8a74p-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 15_278,
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
def q011iv_structure() -> dict[str, Any]:
    sealed, artifacts = q011iv._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011iv._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011iv._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011iv_study() -> dict[str, Any]:
    return q011iv.run_q011iv_study()


@pytest.fixture(scope="module")
def q011iv_cycle(q011iv_study: dict[str, Any]) -> dict[str, Any]:
    return q011iv_study["cycle"]


def test_q011iv_seals_q011iu_and_all_prior_inputs(
    q011iv_structure: dict[str, Any],
) -> None:
    sealed = q011iv_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 234
    assert sealed["direct_digest_count"] == 1_065
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011iu"]["digests"]) == q011iv.Q011IU_DIGESTS
    assert sealed["q011iu"]["artifact_sha256"] == q011iv.Q011IU_ARTIFACT_SHA256
    assert sealed["q011iu"]["runner_sha256"] == q011iv.Q011IU_RUNNER_SHA256


def test_q011iv_reconstructs_component_safe_phase_discs(
    q011iv_structure: dict[str, Any],
) -> None:
    fixed = q011iv_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 87
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 14
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011iv.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011iv.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011iv.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011iv.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011iu_compatible_wave_allocation_count"] == 701
    assert fixed["q011iu_compatible_wave_allocation_digest_sha256"] == (
        q011iv.q011iu.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011iv._protocol_globals_are_restored()


def test_q011iv_enumerates_registered_label_free_phase_inventory(
    q011iv_structure: dict[str, Any],
) -> None:
    allocation = q011iv_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 274_560
    assert allocation["full_allocation_digest_sha256"] == (q011iv.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 15_278
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011iv.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == (q011iv.EXPECTED_FIRST_COMPATIBLE_COUNTS)
    assert tuple(allocation["last_compatible_counts"]) == (q011iv.EXPECTED_LAST_COMPATIBLE_COUNTS)
    assert allocation["individual_wave_allocation_count"] == 701
    assert allocation["component_wave_projection_count"] == 701
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011iv.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 1
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 701,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011iv.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 701
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011iv.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 147,
        "18": 142,
        "24": 139,
        "28": 137,
        "30": 136,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 15_278
    )
    assert q011iv_structure["compatible_count"] == 15_278
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_eighty_seven_totals"] == [1, 12, 9, 5, 7, 0]
    assert adapter["inactive_zero_count_source_identifiers"] == [
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iv result is not sealed")
def test_q011iv_classifies_all_complex_phase_product_discs(
    q011iv_cycle: dict[str, Any],
) -> None:
    comparison = q011iv_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 15_278
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 15_278
    assert comparison["comparison_stream_count"] == 15_278
    assert comparison["comparison_stream_domain"] == ("q011iv-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 15_278,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iv result is not sealed")
def test_q011iv_minimum_exact_phase_margin_is_fixed(
    q011iv_cycle: dict[str, Any],
) -> None:
    witness = q011iv_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iv result is not sealed")
def test_q011iv_applies_stopping_rule_and_preserves_boundary(
    q011iv_cycle: dict[str, Any],
) -> None:
    assert q011iv_cycle["study_validity"] == "passed"
    assert q011iv_cycle["failed_validity_order"] == []
    assert q011iv_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011iv_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011iv_cycle["diagnostic_gates"].values())
    assert q011iv_cycle["scientific_outcome"] == "not_evaluated"
    assert q011iv_cycle["actual_resonance_outcome"] == "not_established"
    assert q011iv_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011iv.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011iv.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011iv_cycle["diagnostic_classification"] == expected
    theorem = q011iv_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_eighty_eighth_q011cb_witness"],
        theorem["eighty_eighth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011iu_ordinal_eighty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011it_ordinal_eighty_six_phase_resolution_is_preserved"]
    assert theorem["q011is_ordinal_eighty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 87" in q011iv_cycle["claim_boundary"]
    assert "ordinals 0 through 86" in q011iv_cycle["claim_boundary"]
    assert "later 44712 Q011cb refined signatures" in q011iv_cycle["claim_boundary"]
    assert "Q011iw" in q011iv_cycle["next_change"]
    assert {name: q011iv_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011iv_cycle["result_digest_sha256"] == (
        q011iv.q011b._canonical_json_sha256(q011iv._result_digest_sections(q011iv_cycle))
    )
    assert q011iv._protocol_globals_are_restored()
    json.dumps(q011iv_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iv result is not sealed")
def test_q011iv_study_metadata_and_optional_artifact_are_scoped(
    q011iv_study: dict[str, Any],
) -> None:
    assert q011iv_study["schema_version"] == 1
    assert q011iv_study["source"] == source_metadata()
    assert q011iv_study["study_gate"] == "passed"
    assert q011iv_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011iv_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 15_278
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011iv_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 87
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011iv_study, allow_nan=False)

    runner_path = Path(q011iv.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011iv_degree34_eighty_eighth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011iv artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011iv_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011iv.q011b._canonical_json_sha256(q011iv._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
