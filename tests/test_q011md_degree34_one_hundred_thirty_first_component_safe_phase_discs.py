from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011md_degree34_one_hundred_thirty_first_component_safe_phase_discs as q011md
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "424a0090da1a8f5a89c7c58b096da03ae3c8f1c302139f26a1b72d1fe4902463"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "4a341618d2919ab06558c0f0f9d56a70e70f994b6209fae75dd25b5e90b24ee7"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "d7e8ab8e6d99a6278570fc5cf32874451f98547d1de68f3a3f728af1803a7f19",
    "phase_input_digest_sha256": "5f5ffa4f2e0a1feca3e08641070efa175ec83546e8ab42c5cf5982d5a8078060",
    "allocation_digest_sha256": "73c26f6ab1b14238ed27e686dfb0e4312bb1d252841708d165989b6f94fa616c",
    "phase_comparison_digest_sha256": "df7432a4c9f95c873d449dee5100dcffe5efbf8d4261f977fd7ae31d2399e0c9",
    "result_digest_sha256": "a49ab4d6252ca74d57bb37416798ddeadf3daafc7ae03bfd6dd63bbd4c5a0a1c",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "22f3c6621764f9709b32e66d9e9a6fdfd10fe54f5a841d3c81ddaeb4ca211735"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "205aeac7dcb616fcd85ad87e4567d590f9b0b906422e3fd814ad9b05a08f1281"
)
EXPECTED_MINIMUM_INDEX: int | None = 9_256
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 8, 0, 1, 0, 5, 2, 0, 2, 3]
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
def q011md_structure() -> dict[str, Any]:
    sealed, artifacts = q011md._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011md._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011md._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011md_study() -> dict[str, Any]:
    return q011md.run_q011md_study()


@pytest.fixture(scope="module")
def q011md_cycle(q011md_study: dict[str, Any]) -> dict[str, Any]:
    return q011md_study["cycle"]


def test_q011md_seals_q011mc_and_all_prior_inputs(
    q011md_structure: dict[str, Any],
) -> None:
    sealed = q011md_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 320
    assert sealed["direct_digest_count"] == 1_452
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mc"]["digests"]) == q011md.Q011MC_DIGESTS
    assert sealed["q011mc"]["artifact_sha256"] == q011md.Q011MC_ARTIFACT_SHA256
    assert sealed["q011mc"]["runner_sha256"] == q011md.Q011MC_RUNNER_SHA256


def test_q011md_reconstructs_component_safe_phase_discs(
    q011md_structure: dict[str, Any],
) -> None:
    fixed = q011md_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 130
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011md.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011md.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011md.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011md.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011mc_compatible_wave_allocation_count"] == 4_347
    assert fixed["q011mc_compatible_wave_allocation_digest_sha256"] == (
        q011md.q011mc.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011md._protocol_globals_are_restored()


def test_q011md_enumerates_registered_label_free_phase_inventory(
    q011md_structure: dict[str, Any],
) -> None:
    allocation = q011md_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 617_760
    assert allocation["full_allocation_digest_sha256"] == q011md.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 34_182
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011md.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011md.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011md.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 4_347
    assert allocation["component_wave_projection_count"] == 1_560
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011md.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 4
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 321,
        "2": 311,
        "3": 308,
        "4": 620,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011md.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_560
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011md.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011md_structure["compatible_count"] == 34_182
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_thirty_component_totals"] == [
        1,
        12,
        9,
        5,
        2,
        5,
    ]
    assert adapter["inactive_zero_power_totals"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011md result is not sealed")
def test_q011md_classifies_all_complex_phase_product_discs(
    q011md_cycle: dict[str, Any],
) -> None:
    comparison = q011md_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 34_182
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 34_182
    assert comparison["comparison_stream_count"] == 34_182
    assert comparison["comparison_stream_domain"] == ("q011md-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 34_182,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011md result is not sealed")
def test_q011md_minimum_exact_phase_margin_is_fixed(
    q011md_cycle: dict[str, Any],
) -> None:
    witness = q011md_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011md result is not sealed")
def test_q011md_applies_stopping_rule_and_preserves_boundary(
    q011md_cycle: dict[str, Any],
) -> None:
    assert q011md_cycle["study_validity"] == "passed"
    assert q011md_cycle["failed_validity_order"] == []
    assert q011md_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011md_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011md_cycle["diagnostic_gates"].values())
    assert q011md_cycle["scientific_outcome"] == "not_evaluated"
    assert q011md_cycle["actual_resonance_outcome"] == "not_established"
    assert q011md_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011md.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011md.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011md_cycle["diagnostic_classification"] == expected
    theorem = q011md_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_thirty_first_q011cb_witness"
        ],
        theorem[
            "one_hundred_thirty_first_q011cb_witness_persists_under_component_safe_phase_discs"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011mc_ordinal_one_hundred_thirty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mb_ordinal_one_hundred_twenty_nine_phase_resolution_is_preserved"]
    assert theorem["q011ma_ordinal_one_hundred_twenty_nine_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 130" in q011md_cycle["claim_boundary"]
    assert "ordinals 0 through 129" in q011md_cycle["claim_boundary"]
    assert "later 44669 Q011cb refined signatures" in q011md_cycle["claim_boundary"]
    assert "Q011me" in q011md_cycle["next_change"]
    assert {name: q011md_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011md_cycle["result_digest_sha256"] == (
        q011md.q011b._canonical_json_sha256(q011md._result_digest_sections(q011md_cycle))
    )
    assert q011md._protocol_globals_are_restored()
    json.dumps(q011md_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011md result is not sealed")
def test_q011md_study_metadata_and_optional_artifact_are_scoped(
    q011md_study: dict[str, Any],
) -> None:
    assert q011md_study["schema_version"] == 1
    assert q011md_study["source"] == source_metadata()
    assert q011md_study["study_gate"] == "passed"
    assert q011md_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011md_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 34_182
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011md_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 130
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011md_study, allow_nan=False)

    runner_path = Path(q011md.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011md_degree34_one_hundred_thirty_first_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011md artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011md_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011md.q011b._canonical_json_sha256(q011md._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
