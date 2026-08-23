from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ix_degree34_eighty_ninth_component_safe_phase_discs as q011ix
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "dd6e0bb426bfc1f8d7817fbfcda5957627b2502e54dd43f2076ed25c79d3ae5d"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "2af530198b7e75f860b6efcfbd12930ac1223c7bb3b320d51fea83959aa32360"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "cd27f3beab460d361f6ddc8ca583ce11514fa7bf58d090b9a7495b6bcbce999c",
    "phase_input_digest_sha256": (
        "c1a5a165794412a3154d774d18a8ee24bd4beabb41b1d27509af999921033fcd"
    ),
    "allocation_digest_sha256": (
        "48e1f3205affdc8a0162ed1b95913f8c9358145b46ee0a1ea8278b7e6ba79cfb"
    ),
    "phase_comparison_digest_sha256": (
        "ae88e1e46f35c8d8f4579d5de3c3946d5ef62cc5e11e76187127603a5f8ee6a9"
    ),
    "result_digest_sha256": "bc02ee2c7176a130de89cfa7ddf75ba489083ff3dfba2135e1bfd9736d29d473",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "2dd7f325568228b77b592fbeca974c89d96212c10a74658ae07db8676ecba026"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "e56c1012985dec3148f724f74f3a19f365a0766d6fbddcce1448ea1d4cbaf8cf"
)
EXPECTED_MINIMUM_INDEX: int | None = 4_419
EXPECTED_MINIMUM_COUNTS: list[int] | None = [
    0,
    1,
    10,
    2,
    0,
    9,
    0,
    0,
    1,
    4,
    0,
    0,
    2,
    5,
]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc8516p-6"
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
def q011ix_structure() -> dict[str, Any]:
    sealed, artifacts = q011ix._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011ix._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011ix._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011ix_study() -> dict[str, Any]:
    return q011ix.run_q011ix_study()


@pytest.fixture(scope="module")
def q011ix_cycle(q011ix_study: dict[str, Any]) -> dict[str, Any]:
    return q011ix_study["cycle"]


def test_q011ix_seals_q011iw_and_all_prior_inputs(
    q011ix_structure: dict[str, Any],
) -> None:
    sealed = q011ix_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 236
    assert sealed["direct_digest_count"] == 1_074
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011iw"]["digests"]) == q011ix.Q011IW_DIGESTS
    assert sealed["q011iw"]["artifact_sha256"] == q011ix.Q011IW_ARTIFACT_SHA256
    assert sealed["q011iw"]["runner_sha256"] == q011ix.Q011IW_RUNNER_SHA256


def test_q011ix_reconstructs_component_safe_phase_discs(
    q011ix_structure: dict[str, Any],
) -> None:
    fixed = q011ix_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2_340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 88
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 14
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011ix.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011ix.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011ix.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011ix.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert all(component in memberships for component in ([144], [145], [148], [149], [150, 151]))
    assert fixed["q011iw_compatible_wave_allocation_count"] == 1_255
    assert fixed["q011iw_compatible_wave_allocation_digest_sha256"] == (
        q011ix.q011iw.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011ix._protocol_globals_are_restored()


def test_q011ix_enumerates_registered_label_free_phase_inventory(
    q011ix_structure: dict[str, Any],
) -> None:
    allocation = q011ix_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 274_560
    assert allocation["full_allocation_digest_sha256"] == (q011ix.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 15_278
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ix.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert tuple(allocation["first_compatible_counts"]) == (q011ix.EXPECTED_FIRST_COMPATIBLE_COUNTS)
    assert tuple(allocation["last_compatible_counts"]) == (q011ix.EXPECTED_LAST_COMPATIBLE_COUNTS)
    assert allocation["individual_wave_allocation_count"] == 1_255
    assert allocation["component_wave_projection_count"] == 701
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011ix.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 2
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 147,
        "2": 554,
    }
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011ix.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 701
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ix.EXPECTED_WAVE_PROJECTION_DIGEST
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
    assert q011ix_structure["compatible_count"] == 15_278
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_eighty_eight_totals"] == [1, 12, 9, 5, 0, 7]
    assert adapter["inactive_zero_count_source_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ix result is not sealed")
def test_q011ix_classifies_all_complex_phase_product_discs(
    q011ix_cycle: dict[str, Any],
) -> None:
    comparison = q011ix_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"] and all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 15_278
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 15_278
    assert comparison["comparison_stream_count"] == 15_278
    assert comparison["comparison_stream_domain"] == ("q011ix-component-safe-phase-comparisons-v1")
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 15_278,
    }
    assert comparison["unique_product_radius_count"] == 10
    if EXPECTED_REFINEMENT_OUTCOME == "component_safe_phase_resolved":
        assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ix result is not sealed")
def test_q011ix_minimum_exact_phase_margin_is_fixed(
    q011ix_cycle: dict[str, Any],
) -> None:
    witness = q011ix_cycle["complex_phase_product_disc_audit"]["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ix result is not sealed")
def test_q011ix_applies_stopping_rule_and_preserves_boundary(
    q011ix_cycle: dict[str, Any],
) -> None:
    assert q011ix_cycle["study_validity"] == "passed"
    assert q011ix_cycle["failed_validity_order"] == []
    assert q011ix_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ix_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ix_cycle["diagnostic_gates"].values())
    assert q011ix_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ix_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ix_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "component_safe_phase_resolved": q011ix.RESOLVED_CLASSIFICATION,
        "component_safe_phase_persistent": q011ix.PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ix_cycle["diagnostic_classification"] == expected
    theorem = q011ix_cycle["theorem_consequence"]
    flags = (
        theorem["component_safe_complex_phase_discs_resolve_eighty_ninth_q011cb_witness"],
        theorem["eighty_ninth_q011cb_witness_persists_under_component_safe_phase_discs"],
    )
    assert sum(flags) == 1
    assert theorem["q011iw_ordinal_eighty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011iv_ordinal_eighty_seven_phase_resolution_is_preserved"]
    assert theorem["q011it_ordinal_eighty_six_phase_resolution_is_preserved"]
    assert theorem["q011is_ordinal_eighty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 88" in q011ix_cycle["claim_boundary"]
    assert "ordinals 0 through 87" in q011ix_cycle["claim_boundary"]
    assert "later 44711 Q011cb refined signatures" in q011ix_cycle["claim_boundary"]
    assert "Q011iy" in q011ix_cycle["next_change"]
    assert {name: q011ix_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ix_cycle["result_digest_sha256"] == (
        q011ix.q011b._canonical_json_sha256(q011ix._result_digest_sections(q011ix_cycle))
    )
    assert q011ix._protocol_globals_are_restored()
    json.dumps(q011ix_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ix result is not sealed")
def test_q011ix_study_metadata_and_optional_artifact_are_scoped(
    q011ix_study: dict[str, Any],
) -> None:
    assert q011ix_study["schema_version"] == 1
    assert q011ix_study["source"] == source_metadata()
    assert q011ix_study["study_gate"] == "passed"
    assert q011ix_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ix_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 15_278
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ix_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 88
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ix_study, allow_nan=False)

    runner_path = Path(q011ix.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ix_degree34_eighty_ninth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ix artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ix_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ix.q011b._canonical_json_sha256(q011ix._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
