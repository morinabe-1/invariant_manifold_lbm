from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mh_degree34_one_hundred_thirty_third_component_safe_phase_discs as q011mh
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "2161fee1c8751da0f56a284a3e19b8251f9a41b90ae028496e0d598b77729745"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "13e85763fd0f80e0d847536f797f6403b298b832c7eaeacb67d54fa9b56df650"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": ("ae6564b6cbe0ddc62e2ceb5a8933f31e6b700d9b5421dfebc68be9f258de458d"),
    "phase_input_digest_sha256": (
        "eeecd7f0038fec7be338f1fed75d2f22b10ee66e81ed5220a1b000e3bdb2f24a"
    ),
    "allocation_digest_sha256": (
        "98f25f90e936cb35dc89208dedcb0e1f3f09b7fa78278d6a58786e9a13ed4f6f"
    ),
    "phase_comparison_digest_sha256": (
        "ac7e8b16f42130507c3f3c43c8df2d16103dacca46fd5aff326962ab25cc4224"
    ),
    "result_digest_sha256": ("ad1abf594cec96ccce7591ca32d280943401b170798e6a04249d5793ce68ef03"),
}
EXPECTED_STREAM_DIGEST: str | None = (
    "ed04f542a6925fb2d3eb7149f9eb89e7940407e3fea10834835254124e2e603d"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "dbcb91daec5078181ab5b178b925fd81e3308422eafd9a9f8e22e60a9ff0ab5c"
)
EXPECTED_MINIMUM_INDEX: int | None = 10003
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 6, 0, 3, 0, 5, 4, 0, 2, 1]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc86eap-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 37940,
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
def q011mh_structure() -> dict[str, Any]:
    sealed, artifacts = q011mh._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011mh._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011mh._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011mh_study() -> dict[str, Any]:
    return q011mh.run_q011mh_study()


@pytest.fixture(scope="module")
def q011mh_cycle(q011mh_study: dict[str, Any]) -> dict[str, Any]:
    return q011mh_study["cycle"]


def test_q011mh_seals_q011mg_and_all_prior_inputs(
    q011mh_structure: dict[str, Any],
) -> None:
    sealed = q011mh_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 324
    assert sealed["direct_digest_count"] == 1_470
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mg"]["digests"]) == q011mh.Q011MG_DIGESTS
    assert sealed["q011mg"]["artifact_sha256"] == q011mh.Q011MG_ARTIFACT_SHA256
    assert sealed["q011mg"]["runner_sha256"] == q011mh.Q011MG_RUNNER_SHA256


def test_q011mh_reconstructs_component_safe_phase_discs(
    q011mh_structure: dict[str, Any],
) -> None:
    fixed = q011mh_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 132
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011mh.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011mh.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011mh.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011mh.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011mg_compatible_wave_allocation_count"] == 4_827
    assert fixed["q011mg_compatible_wave_allocation_digest_sha256"] == (
        q011mh.q011mg.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011mh._protocol_globals_are_restored()


def test_q011mh_enumerates_registered_label_free_phase_inventory(
    q011mh_structure: dict[str, Any],
) -> None:
    allocation = q011mh_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 686_400
    assert allocation["full_allocation_digest_sha256"] == q011mh.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 37_940
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011mh.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011mh.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011mh.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 4_827
    assert allocation["component_wave_projection_count"] == 1_729
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011mh.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 4
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 354,
        "2": 343,
        "3": 341,
        "4": 691,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011mh.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_729
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011mh.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 354,
        "18": 343,
        "24": 341,
        "28": 344,
        "30": 347,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 37_940
    )
    assert q011mh_structure["compatible_count"] == 37_940
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_thirty_two_component_totals"] == [
        1,
        12,
        9,
        5,
        4,
        3,
    ]
    assert adapter["inactive_zero_power_totals"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mh result is not sealed")
def test_q011mh_classifies_all_complex_phase_product_discs(
    q011mh_cycle: dict[str, Any],
) -> None:
    comparison = q011mh_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 37_940
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 37_940
    assert comparison["comparison_stream_count"] == 37_940
    assert comparison["comparison_stream_domain"] == ("q011mh-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 37_940,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mh result is not sealed")
def test_q011mh_minimum_exact_phase_margin_is_fixed(
    q011mh_cycle: dict[str, Any],
) -> None:
    witness = q011mh_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mh result is not sealed")
def test_q011mh_applies_stopping_rule_and_preserves_boundary(
    q011mh_cycle: dict[str, Any],
) -> None:
    assert q011mh_cycle["study_validity"] == "passed"
    assert q011mh_cycle["failed_validity_order"] == []
    assert q011mh_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mh_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mh_cycle["diagnostic_gates"].values())
    assert q011mh_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mh_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mh_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011mh.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011mh.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mh_cycle["diagnostic_classification"] == expected
    theorem = q011mh_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_thirty_third_q011cb_witness"
        ],
        theorem[
            "one_hundred_thirty_third_q011cb_witness_persists_under_component_safe_phase_discs"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011mg_ordinal_one_hundred_thirty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mf_ordinal_one_hundred_thirty_one_phase_resolution_is_preserved"]
    assert theorem["q011me_ordinal_one_hundred_thirty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011lz_ordinal_one_hundred_twenty_eight_phase_resolution_is_preserved"]
    assert theorem["q011ly_ordinal_one_hundred_twenty_eight_interval_inert_diagnostic_is_preserved"]
    assert all(
        value
        for name, value in theorem.items()
        if name.endswith("_is_preserved") and isinstance(value, bool)
    )
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 132" in q011mh_cycle["claim_boundary"]
    assert "ordinals 0 through 131" in q011mh_cycle["claim_boundary"]
    assert "later 44667 Q011cb refined signatures" in q011mh_cycle["claim_boundary"]
    assert "Q011mi" in q011mh_cycle["next_change"]
    assert {name: q011mh_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mh_cycle["result_digest_sha256"] == (
        q011mh.q011b._canonical_json_sha256(q011mh._result_digest_sections(q011mh_cycle))
    )
    assert q011mh._protocol_globals_are_restored()
    json.dumps(q011mh_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mh result is not sealed")
def test_q011mh_study_metadata_and_optional_artifact_are_scoped(
    q011mh_study: dict[str, Any],
) -> None:
    assert q011mh_study["schema_version"] == 1
    assert q011mh_study["source"] == source_metadata()
    assert q011mh_study["study_gate"] == "passed"
    assert q011mh_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mh_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 37_940
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mh_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 132
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mh_study, allow_nan=False)

    runner_path = Path(q011mh.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mh_degree34_one_hundred_thirty_third_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mh artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mh_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mh.q011b._canonical_json_sha256(q011mh._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
