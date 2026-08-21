from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gu_degree34_sixty_second_individual_partition_audit as q011gu
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "c133e1a7deccbe2875f78c76e6518fc29aade1184be822119e25fc3c585f1b46"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "2724bc7e2e01aa86e779efebe40ca2fd7f3e2189e5d74a9c91c5ac87cc42043a"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "a47e8d9cf8310fa92479f698f3be8778dcfc6c60ab509a4c7132f0153863fca9",
    "partition_input_digest_sha256": "a2e39ee465ae2372c470c6d4d6c76d5d538d97aee9a3fb2774e44d524d744621",
    "allocation_audit_digest_sha256": "0ee582e681e4ea3844abcf198918cb062bdf5443479e1b5b98ee3a8f20dde439",
    "result_digest_sha256": "7742e5b7efa83bef7c9fa53eed863e1abd2ab563af656f77f0957e8d0309dcff",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "201e0cdf13bc12b0751f4ec9e996047aa8aa53b5b2a234632db756bb8d5f823f",
    "parent_center_product_interval_digest_sha256": "4055c0b83145577431edd6d1e4ec82e9b0b4d3af0a214067b2185ccdb2619f85",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "9274a61c41f05c636069223dc6367d1388d70d4c713178fe636d68cbb1650aa7",
    "allocation_classification_record_digest_sha256": "aa9e480b2c8752a0dccb632b36ad84fba0b475ca13315554b36ee70590201738",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011gu_structure() -> dict[str, Any]:
    sealed, artifacts = q011gu._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011gu._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011gu_study() -> dict[str, Any]:
    return q011gu.run_q011gu_study()


@pytest.fixture(scope="module")
def q011gu_cycle(q011gu_study: dict[str, Any]) -> dict[str, Any]:
    return q011gu_study["cycle"]


def test_q011gu_seals_q011gt_and_all_prior_inputs(
    q011gu_structure: dict[str, Any],
) -> None:
    sealed = q011gu_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 181
    assert sealed["direct_digest_count"] == 827
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gt"]["digests"]) == q011gu.Q011GT_DIGESTS
    assert sealed["q011gt"]["artifact_sha256"] == q011gu.Q011GT_ARTIFACT_SHA256
    assert sealed["q011gt"]["runner_sha256"] == q011gu.Q011GT_RUNNER_SHA256
    assert sealed["q011gt"]["resolved_witness_digest_sha256"] == (
        q011gu.EXPECTED_ORDINAL_SIXTY_RESOLUTION_DIGEST
    )


def test_q011gu_selects_exactly_flatten_ordinal_sixty_one(
    q011gu_structure: dict[str, Any],
) -> None:
    fixed = q011gu_structure["fixed"]
    selection = fixed["sixty_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 61
    assert selection["selected_left_index"] == 7
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(61))
    assert selection["ordinal_sixty_resolution_digest_sha256"] == (
        q011gu.EXPECTED_ORDINAL_SIXTY_RESOLUTION_DIGEST
    )
    parent = selection["sixty_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [7, 2], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_041
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011gu.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011gu.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011gu.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011gu_reconstructs_registered_partition_and_inventory(
    q011gu_structure: dict[str, Any],
) -> None:
    fixed = q011gu_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [7, 2],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 7, 2, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011gu.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011gu.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 36_288
    assert fixed["full_allocation_digest_sha256"] == q011gu.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_041
    assert q011gu_structure["compatible_count"] == 2_041
    assert fixed["compatible_allocation_digest_sha256"] == q011gu.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 7, 0, 2, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 7, 0, 2, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 36_180
    assert fixed["parent_witness_compatible_index"] == 2_040
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gu result is not sealed")
def test_q011gu_classifies_every_registered_exact_interval(
    q011gu_cycle: dict[str, Any],
) -> None:
    partition = q011gu_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_041
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_041
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_041))
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
        assert record["intersection_width_hex"] == q011gu.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011gu.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_041,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gu result is not sealed")
def test_q011gu_applies_the_registered_exclusive_stopping_rule(
    q011gu_cycle: dict[str, Any],
) -> None:
    assert q011gu_cycle["study_validity"] == "passed"
    assert q011gu_cycle["failed_validity_order"] == []
    assert q011gu_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011gu_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gu_cycle["diagnostic_gates"].values())
    assert q011gu_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gu_cycle["actual_resonance_outcome"] == "not_established"
    assert q011gu_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011gu_cycle["diagnostic_classification"] == q011gu.INERT_CLASSIFICATION
    assert not q011gu_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011gu_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_second_q011cb_witness"],
        theorem["sixty_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_second_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gu result is not sealed")
def test_q011gu_preserves_boundary_and_reproducible_digests(
    q011gu_cycle: dict[str, Any],
) -> None:
    theorem = q011gu_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_second_q011cb_witness"],
        theorem["sixty_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_second_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 61" in q011gu_cycle["claim_boundary"]
    assert "ordinals 0 through 60" in q011gu_cycle["claim_boundary"]
    assert "later 44738 Q011cb refined signatures" in q011gu_cycle["claim_boundary"]
    assert "Q011gv" in q011gu_cycle["next_change"]
    json.dumps(q011gu_cycle, allow_nan=False)
    assert {name: q011gu_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011gu_cycle["result_digest_sha256"] == (
        q011gu.q011b._canonical_json_sha256(q011gu._result_digest_sections(q011gu_cycle))
    )
    assert q011gu._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gu result is not sealed")
def test_q011gu_study_metadata_and_optional_artifact_are_scoped(
    q011gu_study: dict[str, Any],
) -> None:
    assert q011gu_study["schema_version"] == 1
    assert q011gu_study["source"] == source_metadata()
    assert q011gu_study["study_gate"] == "passed"
    assert q011gu_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011gu_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_041
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gu_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 61
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gu_study, allow_nan=False)

    runner_path = Path(q011gu.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gu_degree34_sixty_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gu artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gu_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gu.q011b._canonical_json_sha256(q011gu._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
