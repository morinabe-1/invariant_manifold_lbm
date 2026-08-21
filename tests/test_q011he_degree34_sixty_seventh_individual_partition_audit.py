from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011he_degree34_sixty_seventh_individual_partition_audit as q011he
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "ebd97d6661d36d8d728370c8d837e9c4e37623cd82b5a119c242983fceefe186"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "c6e723b0d4f80d43755cfb542aad5631362818db9549151f45d739ce03477c43"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "7edc539e417e42df75cc8ae1f01c21b5cdf31a1982d1f24c583da6a745e803a2",
    "partition_input_digest_sha256": "e399866821c874da1491c2bbe0465d37016995d64bcd667f7a3ce756b43a6cf9",
    "allocation_audit_digest_sha256": "05976de961bd74f9209c83b05cd9212dcd6cc328d6ba593e21e76257f13aeee1",
    "result_digest_sha256": "07ee464c1147d6807ccfc562f2d98fbb427c782cdba45e549ed0fd4d2cc91a28",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "e528f2e7825b262e3622380ca5d0c02baf7860c7d908809353ca84e0017b0bf5",
    "parent_center_product_interval_digest_sha256": "bf1781360f2f883f22e6093e4b648415f3c9c9d42d25ba39d8b929c09937877a",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "7908d3244a1fa1934aad495d91a56e66318312ceee56a957d24c3d0a9973ae59",
    "allocation_classification_record_digest_sha256": "7695dbd014489081987dbd84d1fc6cffd1d7ac3028d085c34db7473ec9a3f835",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011he_structure() -> dict[str, Any]:
    sealed, artifacts = q011he._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011he._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011he_study() -> dict[str, Any]:
    return q011he.run_q011he_study()


@pytest.fixture(scope="module")
def q011he_cycle(q011he_study: dict[str, Any]) -> dict[str, Any]:
    return q011he_study["cycle"]


def test_q011he_seals_q011hd_and_all_prior_inputs(
    q011he_structure: dict[str, Any],
) -> None:
    sealed = q011he_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 191
    assert sealed["direct_digest_count"] == 872
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hd"]["digests"]) == q011he.Q011HD_DIGESTS
    assert sealed["q011hd"]["artifact_sha256"] == q011he.Q011HD_ARTIFACT_SHA256
    assert sealed["q011hd"]["runner_sha256"] == q011he.Q011HD_RUNNER_SHA256
    assert sealed["q011hd"]["resolved_witness_digest_sha256"] == (
        q011he.EXPECTED_ORDINAL_SIXTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011he_selects_exactly_flatten_ordinal_sixty_six(
    q011he_structure: dict[str, Any],
) -> None:
    fixed = q011he_structure["fixed"]
    selection = fixed["sixty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 66
    assert selection["selected_left_index"] == 8
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(66))
    assert selection["ordinal_sixty_five_resolution_digest_sha256"] == (
        q011he.EXPECTED_ORDINAL_SIXTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["sixty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [8, 1], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 1_531
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011he.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011he.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011he.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011he_reconstructs_registered_partition_and_inventory(
    q011he_structure: dict[str, Any],
) -> None:
    fixed = q011he_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [8, 1],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 8, 1, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011he.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011he.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 27_216
    assert fixed["full_allocation_digest_sha256"] == q011he.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_531
    assert q011he_structure["compatible_count"] == 1_531
    assert fixed["compatible_allocation_digest_sha256"] == q011he.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 8, 0, 1, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 8, 0, 1, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 27_108
    assert fixed["parent_witness_compatible_index"] == 1_530
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011he result is not sealed")
def test_q011he_classifies_every_registered_exact_interval(
    q011he_cycle: dict[str, Any],
) -> None:
    partition = q011he_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_531
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_531
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_531))
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
        assert record["intersection_width_hex"] == q011he.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011he.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_531,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011he result is not sealed")
def test_q011he_applies_the_registered_exclusive_stopping_rule(
    q011he_cycle: dict[str, Any],
) -> None:
    assert q011he_cycle["study_validity"] == "passed"
    assert q011he_cycle["failed_validity_order"] == []
    assert q011he_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011he_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011he_cycle["diagnostic_gates"].values())
    assert q011he_cycle["scientific_outcome"] == "not_evaluated"
    assert q011he_cycle["actual_resonance_outcome"] == "not_established"
    assert q011he_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011he_cycle["diagnostic_classification"] == q011he.INERT_CLASSIFICATION
    assert not q011he_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011he_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_seventh_q011cb_witness"],
        theorem["sixty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_seventh_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011he result is not sealed")
def test_q011he_preserves_boundary_and_reproducible_digests(
    q011he_cycle: dict[str, Any],
) -> None:
    theorem = q011he_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_seventh_q011cb_witness"],
        theorem["sixty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_seventh_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011hd_ordinal_sixty_five_phase_resolution_is_preserved"]
    assert theorem["q011hc_ordinal_sixty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hb_ordinal_sixty_four_phase_resolution_is_preserved"]
    assert theorem["q011ha_ordinal_sixty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gz_ordinal_sixty_three_phase_resolution_is_preserved"]
    assert theorem["q011gy_ordinal_sixty_three_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 66" in q011he_cycle["claim_boundary"]
    assert "ordinals 0 through 65" in q011he_cycle["claim_boundary"]
    assert "later 44733 Q011cb refined signatures" in q011he_cycle["claim_boundary"]
    assert "Q011hf" in q011he_cycle["next_change"]
    json.dumps(q011he_cycle, allow_nan=False)
    assert {name: q011he_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011he_cycle["result_digest_sha256"] == (
        q011he.q011b._canonical_json_sha256(q011he._result_digest_sections(q011he_cycle))
    )
    assert q011he._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011he result is not sealed")
def test_q011he_study_metadata_and_optional_artifact_are_scoped(
    q011he_study: dict[str, Any],
) -> None:
    assert q011he_study["schema_version"] == 1
    assert q011he_study["source"] == source_metadata()
    assert q011he_study["study_gate"] == "passed"
    assert q011he_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011he_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_531
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011he_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 66
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011he_study, allow_nan=False)

    runner_path = Path(q011he.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011he_degree34_sixty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011he artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011he_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011he.q011b._canonical_json_sha256(q011he._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
