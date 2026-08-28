from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ll_degree34_one_hundred_twenty_second_component_safe_phase_discs as q011ll
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "31bdeefe6afa3e3c29283e2522d3b511f008082c14dcc8518162ff4f4df4aa8b"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "6b541b93bdc4fb7433eb896f1225ee769839da63e7e255e53cc7f67f5f43fb01"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "b2b72c677bfac80db85a83962da179d171f85b6ebe76e44f9ec2e0331bfcc64d",
    "phase_input_digest_sha256": (
        "c95322ede06a16c9ed80d4252370162e9d887527f15ad83cbec0b396853d5121"
    ),
    "allocation_digest_sha256": (
        "78b081d4c55e16000202dbc32994267a4a5bde562e16b9eafbf391c435d1e434"
    ),
    "phase_comparison_digest_sha256": (
        "2abf3833f428450284e6f6f754058677d6bd811f06c5409aded1f96fa6de452c"
    ),
    "result_digest_sha256": "77a5dd12a61b73f54c3a0081793276f0d33f84b21dada267781b50abcb4481ba",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "85264842452459d3798d04036fefff4f432867aa80f109215ee2bebf5b8c51a2"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "9d542b49c39fd1540ca85a454354fb568fed3d9fabd5fb55e44188171d03875d"
)
EXPECTED_MINIMUM_INDEX: int | None = 7_429
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 9, 0, 0, 0, 5, 1, 0, 2, 4]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc856fp-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 26_644,
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
def q011ll_structure() -> dict[str, Any]:
    sealed, artifacts = q011ll._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011ll._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011ll._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011ll_study() -> dict[str, Any]:
    return q011ll.run_q011ll_study()


@pytest.fixture(scope="module")
def q011ll_cycle(q011ll_study: dict[str, Any]) -> dict[str, Any]:
    return q011ll_study["cycle"]


def test_q011ll_seals_q011lk_and_all_prior_inputs(
    q011ll_structure: dict[str, Any],
) -> None:
    sealed = q011ll_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 302
    assert sealed["direct_digest_count"] == 1_371
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011lk"]["digests"]) == q011ll.Q011LK_DIGESTS
    assert sealed["q011lk"]["artifact_sha256"] == q011ll.Q011LK_ARTIFACT_SHA256
    assert sealed["q011lk"]["runner_sha256"] == q011ll.Q011LK_RUNNER_SHA256


def test_q011ll_reconstructs_component_safe_phase_discs(
    q011ll_structure: dict[str, Any],
) -> None:
    fixed = q011ll_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 121
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ll.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ll.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011ll.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011ll.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011lk_compatible_wave_allocation_count"] == 3_626
    assert fixed["q011lk_compatible_wave_allocation_digest_sha256"] == (
        q011ll.q011lk.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ll._protocol_globals_are_restored()


def test_q011ll_enumerates_registered_label_free_phase_inventory(
    q011ll_structure: dict[str, Any],
) -> None:
    allocation = q011ll_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == q011ll.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ll.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011ll.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011ll.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 3_626
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ll.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 5
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 253,
        "2": 245,
        "3": 241,
        "4": 240,
        "5": 240,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ll.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ll.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 253,
        "18": 245,
        "24": 241,
        "28": 240,
        "30": 240,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 26_644
    )
    assert q011ll_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_twenty_one_active_totals"] == [1, 12, 9, 5, 1, 6]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ll result is not sealed")
def test_q011ll_classifies_all_complex_phase_product_discs(
    q011ll_cycle: dict[str, Any],
) -> None:
    comparison = q011ll_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011ll-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ll result is not sealed")
def test_q011ll_minimum_exact_phase_margin_is_fixed(
    q011ll_cycle: dict[str, Any],
) -> None:
    witness = q011ll_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ll result is not sealed")
def test_q011ll_applies_stopping_rule_and_preserves_boundary(
    q011ll_cycle: dict[str, Any],
) -> None:
    assert q011ll_cycle["study_validity"] == "passed"
    assert q011ll_cycle["failed_validity_order"] == []
    assert q011ll_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ll_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ll_cycle["diagnostic_gates"].values())
    assert q011ll_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ll_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ll_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011ll.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011ll.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ll_cycle["diagnostic_classification"] == expected
    theorem = q011ll_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_twenty_second_q011cb_witness"
        ],
        theorem[
            "one_hundred_twenty_second_q011cb_witness_persists_under_component_safe_phase_discs"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011lk_ordinal_one_hundred_twenty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011lj_ordinal_one_hundred_twenty_phase_resolution_is_preserved"]
    assert theorem["q011jv_ordinal_one_hundred_phase_resolution_is_preserved"]
    assert theorem["q011jt_ordinal_ninety_nine_phase_resolution_is_preserved"]
    assert theorem["q011jr_ordinal_ninety_eight_phase_resolution_is_preserved"]
    assert theorem["q011jq_ordinal_ninety_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jn_ordinal_ninety_six_phase_resolution_is_preserved"]
    assert theorem["q011jk_ordinal_ninety_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jj_ordinal_ninety_four_phase_resolution_is_preserved"]
    assert theorem["q011ji_ordinal_ninety_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 121" in q011ll_cycle["claim_boundary"]
    assert "ordinals 0 through 120" in q011ll_cycle["claim_boundary"]
    assert "later 44678 Q011cb refined signatures" in q011ll_cycle["claim_boundary"]
    assert "Q011lm" in q011ll_cycle["next_change"]
    assert {name: q011ll_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ll_cycle["result_digest_sha256"] == (
        q011ll.q011b._canonical_json_sha256(q011ll._result_digest_sections(q011ll_cycle))
    )
    assert q011ll._protocol_globals_are_restored()
    json.dumps(q011ll_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ll result is not sealed")
def test_q011ll_study_metadata_and_optional_artifact_are_scoped(
    q011ll_study: dict[str, Any],
) -> None:
    assert q011ll_study["schema_version"] == 1
    assert q011ll_study["source"] == source_metadata()
    assert q011ll_study["study_gate"] == "passed"
    assert q011ll_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ll_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ll_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 121
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ll_study, allow_nan=False)

    runner_path = Path(q011ll.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ll_degree34_one_hundred_twenty_second_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ll artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ll_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ll.q011b._canonical_json_sha256(q011ll._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
