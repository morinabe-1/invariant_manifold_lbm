from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011nb_degree34_one_hundred_forty_third_component_safe_phase_discs as q011nb
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "617e311a391283303dcf9edc41249a0f2db9e6064a4f07bf07b45205179835b8"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "bb6e8adcc92740beb99a9ce42adcc7b0b5fed009aa0841ec5860987fe84ecb06"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "737fe6360a7162d2835ee775124d3e93a382995f852ad8fb8a6e32563430081c",
    "phase_input_digest_sha256": (
        "6ddad4b467381c1e18aa87799658ecc02b781bfdc334c0e43764363f6af1422c"
    ),
    "allocation_digest_sha256": (
        "19e027f1f063e2d870ee30a69393541b5be42ffd8dada65611f1b04e20f28fac"
    ),
    "phase_comparison_digest_sha256": (
        "7982229b7d5f723abd54726f44dc11c2b40906024f2c707f1c986f9945ac7bd0"
    ),
    "result_digest_sha256": "e2f13738250d09743e494b78df7adecfbf1e5fb7d5addae1f5ac3d4179e223bb",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "9629a42bdb674440b63b30eebf63cad8292d29a719e4d708fcf65e4d9dfe5d92"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "d16bd69692ef992ecc675d954307992f26d80c0cacc57e0fa3a33053e4a3fd2c"
)
EXPECTED_MINIMUM_INDEX: int | None = 7_329
EXPECTED_MINIMUM_COUNTS: list[int] | None = [0, 1, 10, 2, 0, 6, 0, 3, 0, 5, 5, 1, 1, 0]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc88eep-6"
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
def q011nb_structure() -> dict[str, Any]:
    sealed, artifacts = q011nb._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011nb._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011nb._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011nb_study() -> dict[str, Any]:
    return q011nb.run_q011nb_study()


@pytest.fixture(scope="module")
def q011nb_cycle(q011nb_study: dict[str, Any]) -> dict[str, Any]:
    return q011nb_study["cycle"]


def test_q011nb_seals_q011na_and_all_prior_inputs(
    q011nb_structure: dict[str, Any],
) -> None:
    sealed = q011nb_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 344
    assert sealed["direct_digest_count"] == 1_560
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011na"]["digests"]) == q011nb.Q011NA_DIGESTS
    assert sealed["q011na"]["artifact_sha256"] == q011nb.Q011NA_ARTIFACT_SHA256
    assert sealed["q011na"]["runner_sha256"] == q011nb.Q011NA_RUNNER_SHA256
    repeated, repeated_artifacts = q011nb._sealed_input_audit()
    parent, parent_artifacts = q011nb.q011na._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 344
    assert len(repeated_artifacts) == 344
    assert parent["passed"] and parent["artifact_count"] == 343
    assert len(parent_artifacts) == 343


def test_q011nb_reconstructs_component_safe_phase_discs(
    q011nb_structure: dict[str, Any],
) -> None:
    fixed = q011nb_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 142
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011nb.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011nb.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011nb.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011nb.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011na_compatible_wave_allocation_count"] == 2_906
    assert fixed["q011na_compatible_wave_allocation_digest_sha256"] == (
        q011nb.q011na.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011nb._protocol_globals_are_restored()


def test_q011nb_enumerates_registered_label_free_phase_inventory(
    q011nb_structure: dict[str, Any],
) -> None:
    allocation = q011nb_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == q011nb.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011nb.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011nb.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011nb.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 2_906
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011nb.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 253,
        "2": 245,
        "3": 721,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011nb.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011nb.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011nb_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_forty_two_active_totals"] == [1, 12, 9, 5, 6, 1]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nb result is not sealed")
def test_q011nb_classifies_all_complex_phase_product_discs(
    q011nb_cycle: dict[str, Any],
) -> None:
    comparison = q011nb_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011nb-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nb result is not sealed")
def test_q011nb_minimum_exact_phase_margin_is_fixed(
    q011nb_cycle: dict[str, Any],
) -> None:
    witness = q011nb_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nb result is not sealed")
def test_q011nb_applies_stopping_rule_and_preserves_boundary(
    q011nb_cycle: dict[str, Any],
) -> None:
    assert q011nb_cycle["study_validity"] == "passed"
    assert q011nb_cycle["failed_validity_order"] == []
    assert q011nb_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011nb_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011nb_cycle["diagnostic_gates"].values())
    assert q011nb_cycle["scientific_outcome"] == "not_evaluated"
    assert q011nb_cycle["actual_resonance_outcome"] == "not_established"
    assert q011nb_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011nb.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011nb.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011nb_cycle["diagnostic_classification"] == expected
    theorem = q011nb_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_forty_third_q011cb_witness"
        ],
        theorem["one_hundred_forty_third_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011na_ordinal_one_hundred_forty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mz_ordinal_one_hundred_forty_one_phase_resolution_is_preserved"]
    assert theorem["q011my_ordinal_one_hundred_forty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mx_ordinal_one_hundred_forty_phase_resolution_is_preserved"]
    assert theorem["q011mw_ordinal_one_hundred_forty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mv_ordinal_one_hundred_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011mu_ordinal_one_hundred_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mt_ordinal_one_hundred_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011mr_ordinal_one_hundred_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 142" in q011nb_cycle["claim_boundary"]
    assert "ordinals 0 through 141" in q011nb_cycle["claim_boundary"]
    assert "later 44657 Q011cb refined signatures" in q011nb_cycle["claim_boundary"]
    assert "Q011nc" in q011nb_cycle["next_change"]
    assert {name: q011nb_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011nb_cycle["result_digest_sha256"] == (
        q011nb.q011b._canonical_json_sha256(q011nb._result_digest_sections(q011nb_cycle))
    )
    assert q011nb._protocol_globals_are_restored()
    json.dumps(q011nb_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nb result is not sealed")
def test_q011nb_study_metadata_and_optional_artifact_are_scoped(
    q011nb_study: dict[str, Any],
) -> None:
    assert q011nb_study["schema_version"] == 1
    assert q011nb_study["source"] == source_metadata()
    assert q011nb_study["study_gate"] == "passed"
    assert q011nb_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011nb_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011nb_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 142
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011nb_study, allow_nan=False)

    runner_path = Path(q011nb.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011nb_degree34_one_hundred_forty_third_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011nb artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011nb_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011nb.q011b._canonical_json_sha256(q011nb._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
