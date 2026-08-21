from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gy_degree34_sixty_fourth_individual_partition_audit as q011gy
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d5456ab7d6552837afea1e5661b53700900ffe1c36fcc4a9f2a2b01db4cdc96d"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "eda57c1c9f48b016479ffc7518aac825223c1f9e634c4597526152c9ec2b8ede"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "1da84d95564923a3e1c7320622290ef076e277aa5bf3413e7962851e31af0971",
    "partition_input_digest_sha256": "7f9ee085d36cd7e353bd4ba0879f99c1464c61309c3033777edb00eba5580e06",
    "allocation_audit_digest_sha256": "df8981cd4fd8d38e78a6979b17874839990b3fca1c30f042ffbc8ef81067d5a1",
    "result_digest_sha256": "f766d59e8e0d4baffccb95415a8c0b76b36a3a508c1be36268df5b62990cf96b",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "31a0663c3f61e91de003de5bcad029f88027fb026d5cf8f8f3f3d042b0221e35",
    "parent_center_product_interval_digest_sha256": "cee02ddd51515bca25a8ba9d3945153df4878244cd08ecb3e31b826ef7e1328c",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "46852875cdcf55bd880854afb5f3b3b9d4cb5422a1ddc2ab1c02ce9cb8609eba",
    "allocation_classification_record_digest_sha256": "4aaa8777175cae6b7224dae7f2c6181e3f05ab640eab5d87fef3a258ab0580ab",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011gy_structure() -> dict[str, Any]:
    sealed, artifacts = q011gy._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011gy._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011gy_study() -> dict[str, Any]:
    return q011gy.run_q011gy_study()


@pytest.fixture(scope="module")
def q011gy_cycle(q011gy_study: dict[str, Any]) -> dict[str, Any]:
    return q011gy_study["cycle"]


def test_q011gy_seals_q011gx_and_all_prior_inputs(
    q011gy_structure: dict[str, Any],
) -> None:
    sealed = q011gy_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 185
    assert sealed["direct_digest_count"] == 845
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gx"]["digests"]) == q011gy.Q011GX_DIGESTS
    assert sealed["q011gx"]["artifact_sha256"] == q011gy.Q011GX_ARTIFACT_SHA256
    assert sealed["q011gx"]["runner_sha256"] == q011gy.Q011GX_RUNNER_SHA256
    assert sealed["q011gx"]["resolved_witness_digest_sha256"] == (
        q011gy.EXPECTED_ORDINAL_SIXTY_TWO_RESOLUTION_DIGEST
    )


def test_q011gy_selects_exactly_flatten_ordinal_sixty_three(
    q011gy_structure: dict[str, Any],
) -> None:
    fixed = q011gy_structure["fixed"]
    selection = fixed["sixty_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 63
    assert selection["selected_left_index"] == 7
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(63))
    assert selection["ordinal_sixty_two_resolution_digest_sha256"] == (
        q011gy.EXPECTED_ORDINAL_SIXTY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["sixty_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [7, 2], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 911
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011gy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011gy.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011gy.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011gy_reconstructs_registered_partition_and_inventory(
    q011gy_structure: dict[str, Any],
) -> None:
    fixed = q011gy_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [7, 2],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 7, 2, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011gy.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011gy.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 16_128
    assert fixed["full_allocation_digest_sha256"] == q011gy.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 911
    assert q011gy_structure["compatible_count"] == 911
    assert fixed["compatible_allocation_digest_sha256"] == q011gy.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 7, 0, 2, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 7, 0, 2, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 16_080
    assert fixed["parent_witness_compatible_index"] == 910
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gy result is not sealed")
def test_q011gy_classifies_every_registered_exact_interval(
    q011gy_cycle: dict[str, Any],
) -> None:
    partition = q011gy_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 911
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 911
    assert [record["compatible_allocation_index"] for record in records] == list(range(911))
    for record in records:
        assert record["degree"] == 34
        assert record["output_block"] == 7
        assert record["exact_relation"] == "overlap"
        assert record["binary64_outward_relation"] == "overlap"
        assert not record["exact_gap_positive"]
        assert not record["binary64_outward_gap_positive"]
        assert record["product_equals_parent"]
        assert record["center_product_equals_parent"]
        assert record["target_equals_parent"]
        assert record["intersection_equals_parent"]
        assert record["center_diagnostic_equals_parent"]
        assert record["intersection_width_hex"] == q011gy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011gy.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 911,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gy result is not sealed")
def test_q011gy_applies_the_registered_exclusive_stopping_rule(
    q011gy_cycle: dict[str, Any],
) -> None:
    assert q011gy_cycle["study_validity"] == "passed"
    assert q011gy_cycle["failed_validity_order"] == []
    assert q011gy_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011gy_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gy_cycle["diagnostic_gates"].values())
    assert q011gy_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gy_cycle["actual_resonance_outcome"] == "not_established"
    assert q011gy_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011gy_cycle["diagnostic_classification"] == q011gy.INERT_CLASSIFICATION
    assert not q011gy_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011gy_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_fourth_q011cb_witness"],
        theorem["sixty_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_fourth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gy result is not sealed")
def test_q011gy_preserves_boundary_and_reproducible_digests(
    q011gy_cycle: dict[str, Any],
) -> None:
    theorem = q011gy_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_fourth_q011cb_witness"],
        theorem["sixty_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_fourth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011gx_ordinal_sixty_two_phase_resolution_is_preserved"]
    assert theorem["q011gw_ordinal_sixty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gv_ordinal_sixty_one_phase_resolution_is_preserved"]
    assert theorem["q011gu_ordinal_sixty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gt_ordinal_sixty_phase_resolution_is_preserved"]
    assert theorem["q011gs_ordinal_sixty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gr_ordinal_fifty_nine_phase_resolution_is_preserved"]
    assert theorem["q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
    assert theorem["q011go_ordinal_fifty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 63" in q011gy_cycle["claim_boundary"]
    assert "ordinals 0 through 62" in q011gy_cycle["claim_boundary"]
    assert "later 44736 Q011cb refined signatures" in q011gy_cycle["claim_boundary"]
    assert "Q011gz" in q011gy_cycle["next_change"]
    json.dumps(q011gy_cycle, allow_nan=False)
    assert {name: q011gy_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011gy_cycle["result_digest_sha256"] == (
        q011gy.q011b._canonical_json_sha256(q011gy._result_digest_sections(q011gy_cycle))
    )
    assert q011gy._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gy result is not sealed")
def test_q011gy_study_metadata_and_optional_artifact_are_scoped(
    q011gy_study: dict[str, Any],
) -> None:
    assert q011gy_study["schema_version"] == 1
    assert q011gy_study["source"] == source_metadata()
    assert q011gy_study["study_gate"] == "passed"
    assert q011gy_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011gy_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 911
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gy_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 63
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gy_study, allow_nan=False)

    runner_path = Path(q011gy.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gy_degree34_sixty_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gy artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gy_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gy.q011b._canonical_json_sha256(q011gy._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
