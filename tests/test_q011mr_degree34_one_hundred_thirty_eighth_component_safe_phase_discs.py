from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mr_degree34_one_hundred_thirty_eighth_component_safe_phase_discs as q011mr
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "fac1bcaa26028ef10eccf5458685919496d4881d38beeda51ff2b0b2f1e73a7b"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "9b0b28b7b7825f641d50bce65164b13e27709b91ead3a280f906602139cecc2d"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "257b4bd4c5399741929a7cec5c1b938cd0250bb6fa285a8db7f3fd3605bf02f1",
    "phase_input_digest_sha256": (
        "328b6126590409f631f5dbba9d720782555175f6ade98450e9f554a516a3dde5"
    ),
    "allocation_digest_sha256": (
        "c3f7ed307fd129e8dcf40bd4605eae7f299885ed72a19cd99b46962facd306c5"
    ),
    "phase_comparison_digest_sha256": (
        "fff03687602c38edc87a9ad4e9adfd82de6b312c7a1c0658584ad9048d01a207"
    ),
    "result_digest_sha256": "84a81fcce73bc7c68dbafa49913db60d8f46d8b7a68fb9c2d7cf6e6e7cd54237",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "97694244c1cdbd36bfa47cf10d8f428b690296dc732d3f6418e2dad59d822686"
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
def q011mr_structure() -> dict[str, Any]:
    sealed, artifacts = q011mr._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011mr._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011mr._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011mr_study() -> dict[str, Any]:
    return q011mr.run_q011mr_study()


@pytest.fixture(scope="module")
def q011mr_cycle(q011mr_study: dict[str, Any]) -> dict[str, Any]:
    return q011mr_study["cycle"]


def test_q011mr_seals_q011mq_and_all_prior_inputs(
    q011mr_structure: dict[str, Any],
) -> None:
    sealed = q011mr_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 334
    assert sealed["direct_digest_count"] == 1_515
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mq"]["digests"]) == q011mr.Q011MQ_DIGESTS
    assert sealed["q011mq"]["artifact_sha256"] == q011mr.Q011MQ_ARTIFACT_SHA256
    assert sealed["q011mq"]["runner_sha256"] == q011mr.Q011MQ_RUNNER_SHA256


def test_q011mr_reconstructs_component_safe_phase_discs(
    q011mr_structure: dict[str, Any],
) -> None:
    fixed = q011mr_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 137
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011mr.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011mr.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011mr.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011mr.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011mq_compatible_wave_allocation_count"] == 2_906
    assert fixed["q011mq_compatible_wave_allocation_digest_sha256"] == (
        q011mr.q011mq.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011mr._protocol_globals_are_restored()


def test_q011mr_enumerates_registered_label_free_phase_inventory(
    q011mr_structure: dict[str, Any],
) -> None:
    allocation = q011mr_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == q011mr.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011mr.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011mr.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011mr.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 2_906
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011mr.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 253,
        "2": 245,
        "3": 721,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011mr.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011mr.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011mr_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_thirty_seven_active_totals"] == [1, 12, 9, 5, 1, 6]
    assert adapter["canonical_zero_power_indices"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mr result is not sealed")
def test_q011mr_classifies_all_complex_phase_product_discs(
    q011mr_cycle: dict[str, Any],
) -> None:
    comparison = q011mr_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011mr-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mr result is not sealed")
def test_q011mr_minimum_exact_phase_margin_is_fixed(
    q011mr_cycle: dict[str, Any],
) -> None:
    witness = q011mr_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mr result is not sealed")
def test_q011mr_applies_stopping_rule_and_preserves_boundary(
    q011mr_cycle: dict[str, Any],
) -> None:
    assert q011mr_cycle["study_validity"] == "passed"
    assert q011mr_cycle["failed_validity_order"] == []
    assert q011mr_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mr_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mr_cycle["diagnostic_gates"].values())
    assert q011mr_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mr_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mr_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011mr.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011mr.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mr_cycle["diagnostic_classification"] == expected
    theorem = q011mr_cycle["theorem_consequence"]
    flags = (
        theorem[
            "component_safe_complex_phase_discs_resolve_one_hundred_thirty_eighth_q011cb_witness"
        ],
        theorem[
            "one_hundred_thirty_eighth_q011cb_witness_persists_under_component_safe_phase_discs"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mp_ordinal_one_hundred_thirty_six_phase_resolution_is_preserved"]
    assert theorem["q011mo_ordinal_one_hundred_thirty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 137" in q011mr_cycle["claim_boundary"]
    assert "ordinals 0 through 136" in q011mr_cycle["claim_boundary"]
    assert "later 44662 Q011cb refined signatures" in q011mr_cycle["claim_boundary"]
    assert "Q011ms" in q011mr_cycle["next_change"]
    assert {name: q011mr_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mr_cycle["result_digest_sha256"] == (
        q011mr.q011b._canonical_json_sha256(q011mr._result_digest_sections(q011mr_cycle))
    )
    assert q011mr._protocol_globals_are_restored()
    json.dumps(q011mr_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mr result is not sealed")
def test_q011mr_study_metadata_and_optional_artifact_are_scoped(
    q011mr_study: dict[str, Any],
) -> None:
    assert q011mr_study["schema_version"] == 1
    assert q011mr_study["source"] == source_metadata()
    assert q011mr_study["study_gate"] == "passed"
    assert q011mr_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mr_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mr_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 137
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mr_study, allow_nan=False)

    runner_path = Path(q011mr.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mr_degree34_one_hundred_thirty_eighth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mr artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mr_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mr.q011b._canonical_json_sha256(q011mr._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
