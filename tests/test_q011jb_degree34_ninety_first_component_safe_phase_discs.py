from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jb_degree34_ninety_first_component_safe_phase_discs as q011jb
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "cb911374946d872cdd17598a8aa2fd7e2b820e41e54e38d1c2a026ec6a1e4f0e"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "acc4957e4c6fe64ff3da832d6906c886d1554bfc140365f35f89f96771952f16"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "81ebbb3dd333a23511238e8234e93c094dc32dff7a0e3b564ad4f2ba9ac21569",
    "phase_input_digest_sha256": (
        "b31b3c0b60670b172e3d66871135f50906a5aabcd41da242cc4938ac6ae0ab9e"
    ),
    "allocation_digest_sha256": (
        "a9559cff708f1f3207ab752d52e39b159cdd05701c1cd37b9cc45d4fb7cba84b"
    ),
    "phase_comparison_digest_sha256": (
        "4f1bfed6b77166ad239fd9fab2f7dfea7aa3f109724b132e55506118f82805b0"
    ),
    "result_digest_sha256": "7cea3318b5c52b966e2b3354f982df0cb05266bab163bf72ed37f318a38b182d",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "971f40ec965e4b65c8125ca4f763c88ec88d23f815d69e2cd53b7d415d85e2c6"
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
def q011jb_structure() -> dict[str, Any]:
    sealed, artifacts = q011jb._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011jb._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011jb._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011jb_study() -> dict[str, Any]:
    return q011jb.run_q011jb_study()


@pytest.fixture(scope="module")
def q011jb_cycle(q011jb_study: dict[str, Any]) -> dict[str, Any]:
    return q011jb_study["cycle"]


def test_q011jb_seals_q011ja_and_all_prior_inputs(
    q011jb_structure: dict[str, Any],
) -> None:
    sealed = q011jb_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 240
    assert sealed["direct_digest_count"] == 1_092
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ja"]["digests"]) == q011jb.Q011JA_DIGESTS
    assert sealed["q011ja"]["artifact_sha256"] == q011jb.Q011JA_ARTIFACT_SHA256
    assert sealed["q011ja"]["runner_sha256"] == q011jb.Q011JA_RUNNER_SHA256


def test_q011jb_reconstructs_component_safe_phase_discs(
    q011jb_structure: dict[str, Any],
) -> None:
    fixed = q011jb_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 90
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 14
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011jb.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011jb.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011jb.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011jb.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ja_compatible_wave_allocation_count"] == 2_799
    assert fixed["q011ja_compatible_wave_allocation_digest_sha256"] == (
        q011jb.q011ja.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011jb._protocol_globals_are_restored()


def test_q011jb_enumerates_registered_label_free_phase_inventory(
    q011jb_structure: dict[str, Any],
) -> None:
    allocation = q011jb_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == q011jb.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011jb.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011jb.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011jb.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 2_799
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011jb.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 321,
        "2": 1_239,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011jb.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011jb.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011jb_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_ninety_totals"] == [1, 12, 9, 5, 2, 5]
    assert adapter["all_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jb result is not sealed")
def test_q011jb_classifies_all_complex_phase_product_discs(
    q011jb_cycle: dict[str, Any],
) -> None:
    comparison = q011jb_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011jb-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jb result is not sealed")
def test_q011jb_minimum_exact_phase_margin_is_fixed(
    q011jb_cycle: dict[str, Any],
) -> None:
    witness = q011jb_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jb result is not sealed")
def test_q011jb_applies_stopping_rule_and_preserves_boundary(
    q011jb_cycle: dict[str, Any],
) -> None:
    assert q011jb_cycle["study_validity"] == "passed"
    assert q011jb_cycle["failed_validity_order"] == []
    assert q011jb_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jb_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jb_cycle["diagnostic_gates"].values())
    assert q011jb_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jb_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jb_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011jb.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011jb.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jb_cycle["diagnostic_classification"] == expected
    theorem = q011jb_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_ninety_first_q011cb_witness"],
        theorem["ninety_first_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011ja_ordinal_ninety_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011iz_ordinal_eighty_nine_phase_resolution_is_preserved"]
    assert theorem["q011iy_ordinal_eighty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ix_ordinal_eighty_eight_phase_resolution_is_preserved"]
    assert theorem["q011iw_ordinal_eighty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011iv_ordinal_eighty_seven_phase_resolution_is_preserved"]
    assert theorem["q011it_ordinal_eighty_six_phase_resolution_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 90" in q011jb_cycle["claim_boundary"]
    assert "ordinals 0 through 89" in q011jb_cycle["claim_boundary"]
    assert "later 44709 Q011cb refined signatures" in q011jb_cycle["claim_boundary"]
    assert "Q011jc" in q011jb_cycle["next_change"]
    assert {name: q011jb_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jb_cycle["result_digest_sha256"] == (
        q011jb.q011b._canonical_json_sha256(q011jb._result_digest_sections(q011jb_cycle))
    )
    assert q011jb._protocol_globals_are_restored()
    json.dumps(q011jb_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jb result is not sealed")
def test_q011jb_study_metadata_and_optional_artifact_are_scoped(
    q011jb_study: dict[str, Any],
) -> None:
    assert q011jb_study["schema_version"] == 1
    assert q011jb_study["source"] == source_metadata()
    assert q011jb_study["study_gate"] == "passed"
    assert q011jb_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jb_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jb_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 90
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jb_study, allow_nan=False)

    runner_path = Path(q011jb.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jb_degree34_ninety_first_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jb artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jb_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jb.q011b._canonical_json_sha256(q011jb._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
