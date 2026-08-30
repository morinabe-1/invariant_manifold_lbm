from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mb_degree34_one_hundred_thirtieth_component_safe_phase_discs as q011mb
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "40e73e0d210c5c1ce2e35db1d1a11b64282534ccb5e28e4364d48dd48deb1698"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "6077ac31ad7d13bb5af38c6bf8ea0a235345c2a629a32471742925224f862653"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "e8e9a22c85ebb20d207e0c7447fb02d41993a336f74d588a5fa9b172c89777e0",
    "phase_input_digest_sha256": "5811a1b5186154f93c5876e3b849b276e4a04e53b3959aeac7d800933ad60669",
    "allocation_digest_sha256": "ebb192fe342035b5157afe04f1ce89858f365cc798f20c145d6c01a309437ade",
    "phase_comparison_digest_sha256": "2da1608f2dadb4e28dba5e5cf415ac2aa077d8be98ad2a6f4f8ce511a5156df6",
    "result_digest_sha256": "ef86fc4b99e4e4c5e83fd960899a763bde95ef03957a23c924fc71e9819c95a6",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "6d4436b8ac367475210824702431412c119fa247f2ff959753fdca89a745afe8"
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
def q011mb_structure() -> dict[str, Any]:
    sealed, artifacts = q011mb._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011mb._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011mb._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011mb_study() -> dict[str, Any]:
    return q011mb.run_q011mb_study()


@pytest.fixture(scope="module")
def q011mb_cycle(q011mb_study: dict[str, Any]) -> dict[str, Any]:
    return q011mb_study["cycle"]


def test_q011mb_seals_q011ma_and_all_prior_inputs(
    q011mb_structure: dict[str, Any],
) -> None:
    sealed = q011mb_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 318
    assert sealed["direct_digest_count"] == 1_443
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ma"]["digests"]) == q011mb.Q011MA_DIGESTS
    assert sealed["q011ma"]["artifact_sha256"] == q011mb.Q011MA_ARTIFACT_SHA256
    assert sealed["q011ma"]["runner_sha256"] == q011mb.Q011MA_RUNNER_SHA256


def test_q011mb_reconstructs_component_safe_phase_discs(
    q011mb_structure: dict[str, Any],
) -> None:
    fixed = q011mb_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 129
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["canonical_source_variant_count"] == 14
    assert fixed["active_source_variant_count"] == 14
    assert fixed["inactive_zero_power_identifiers"] == []
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011mb.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011mb.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == q011mb.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011mb.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011ma_compatible_wave_allocation_count"] == 3_386
    assert fixed["q011ma_compatible_wave_allocation_digest_sha256"] == (
        q011mb.q011ma.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011mb._protocol_globals_are_restored()


def test_q011mb_enumerates_registered_label_free_phase_inventory(
    q011mb_structure: dict[str, Any],
) -> None:
    allocation = q011mb_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 480_480
    assert allocation["full_allocation_digest_sha256"] == q011mb.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 26_644
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011mb.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == q011mb.EXPECTED_FIRST_COMPATIBLE_COUNTS
    assert tuple(allocation["last_compatible_counts"]) == q011mb.EXPECTED_LAST_COMPATIBLE_COUNTS
    assert allocation["individual_wave_allocation_count"] == 3_386
    assert allocation["component_wave_projection_count"] == 1_219
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011mb.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 4
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 253,
        "2": 245,
        "3": 241,
        "4": 480,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011mb.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 1_219
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011mb.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011mb_structure["compatible_count"] == 26_644
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_one_hundred_twenty_nine_component_totals"] == [
        1,
        12,
        9,
        5,
        1,
        6,
    ]
    assert adapter["inactive_zero_power_totals"] == []
    assert adapter["all_active_singleton_component_wave_pairs_are_active"] is True
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mb result is not sealed")
def test_q011mb_classifies_all_complex_phase_product_discs(
    q011mb_cycle: dict[str, Any],
) -> None:
    comparison = q011mb_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 26_644
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 26_644
    assert comparison["comparison_stream_count"] == 26_644
    assert comparison["comparison_stream_domain"] == ("q011mb-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 26_644,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mb result is not sealed")
def test_q011mb_minimum_exact_phase_margin_is_fixed(
    q011mb_cycle: dict[str, Any],
) -> None:
    witness = q011mb_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mb result is not sealed")
def test_q011mb_applies_stopping_rule_and_preserves_boundary(
    q011mb_cycle: dict[str, Any],
) -> None:
    assert q011mb_cycle["study_validity"] == "passed"
    assert q011mb_cycle["failed_validity_order"] == []
    assert q011mb_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mb_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mb_cycle["diagnostic_gates"].values())
    assert q011mb_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mb_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mb_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011mb.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011mb.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mb_cycle["diagnostic_classification"] == expected
    theorem = q011mb_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_one_hundred_thirtieth_q011cb_witness"],
        theorem["one_hundred_thirtieth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
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
    assert "flatten ordinal 129" in q011mb_cycle["claim_boundary"]
    assert "ordinals 0 through 128" in q011mb_cycle["claim_boundary"]
    assert "later 44670 Q011cb refined signatures" in q011mb_cycle["claim_boundary"]
    assert "Q011mc" in q011mb_cycle["next_change"]
    assert {name: q011mb_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mb_cycle["result_digest_sha256"] == (
        q011mb.q011b._canonical_json_sha256(q011mb._result_digest_sections(q011mb_cycle))
    )
    assert q011mb._protocol_globals_are_restored()
    json.dumps(q011mb_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mb result is not sealed")
def test_q011mb_study_metadata_and_optional_artifact_are_scoped(
    q011mb_study: dict[str, Any],
) -> None:
    assert q011mb_study["schema_version"] == 1
    assert q011mb_study["source"] == source_metadata()
    assert q011mb_study["study_gate"] == "passed"
    assert q011mb_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mb_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 26_644
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mb_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 129
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mb_study, allow_nan=False)

    runner_path = Path(q011mb.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mb_degree34_one_hundred_thirtieth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mb artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mb_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mb.q011b._canonical_json_sha256(q011mb._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
