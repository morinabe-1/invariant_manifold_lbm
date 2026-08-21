from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gw_degree34_sixty_third_individual_partition_audit as q011gw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "8807529558678b8b6c273870b6d392d7fe3f4fe95c8703135e79a15dd221bd79"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8020b17c66b37fd0a6d47354b48f0833cbc4b74fb153014acdd80b49d8b2d4ca"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "7bcc4360ced514c2f11263d2b5aa66f851d6df195413f5f73eb2cb6c14ec3c10",
    "partition_input_digest_sha256": "716b608f3fd3e6e52231ff01363b2030329e3c065b00ec06e00a299256f99aca",
    "allocation_audit_digest_sha256": "6ef7f46dfedb45ba7b65a2740081c5629a4ca28d74e38bf9ae1719782bcda0fd",
    "result_digest_sha256": "79783408a4d7e4360f28722bb36dd4c0a4db7374cdcf7155319e44966db93d02",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "d324447e8d430f466bd481d7df373fec16db25c2ad5b76f61d3b398ad18f16d3",
    "parent_center_product_interval_digest_sha256": "633e8a6cc6986a67eaf05732a08b0eae5e76ef479084e2209fdd9c34e5e28469",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "c3ef2b169c3847cd2b2ca7d7dea312104ff3db1597bb08d48ea26af6e394066f",
    "allocation_classification_record_digest_sha256": "bc50e808a2c3ceae3d1a2ade1cc107d2a96cc2bb923f2a4e304ec4f545cdc7d4",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011gw_structure() -> dict[str, Any]:
    sealed, artifacts = q011gw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011gw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011gw_study() -> dict[str, Any]:
    return q011gw.run_q011gw_study()


@pytest.fixture(scope="module")
def q011gw_cycle(q011gw_study: dict[str, Any]) -> dict[str, Any]:
    return q011gw_study["cycle"]


def test_q011gw_seals_q011gv_and_all_prior_inputs(
    q011gw_structure: dict[str, Any],
) -> None:
    sealed = q011gw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 183
    assert sealed["direct_digest_count"] == 836
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gv"]["digests"]) == q011gw.Q011GV_DIGESTS
    assert sealed["q011gv"]["artifact_sha256"] == q011gw.Q011GV_ARTIFACT_SHA256
    assert sealed["q011gv"]["runner_sha256"] == q011gw.Q011GV_RUNNER_SHA256
    assert sealed["q011gv"]["resolved_witness_digest_sha256"] == (
        q011gw.EXPECTED_ORDINAL_SIXTY_ONE_RESOLUTION_DIGEST
    )


def test_q011gw_selects_exactly_flatten_ordinal_sixty_two(
    q011gw_structure: dict[str, Any],
) -> None:
    fixed = q011gw_structure["fixed"]
    selection = fixed["sixty_third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 62
    assert selection["selected_left_index"] == 7
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(62))
    assert selection["ordinal_sixty_one_resolution_digest_sha256"] == (
        q011gw.EXPECTED_ORDINAL_SIXTY_ONE_RESOLUTION_DIGEST
    )
    parent = selection["sixty_third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [7, 2], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_590
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011gw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011gw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011gw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011gw_reconstructs_registered_partition_and_inventory(
    q011gw_structure: dict[str, Any],
) -> None:
    fixed = q011gw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [7, 2],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 7, 2, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011gw.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011gw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 28_224
    assert fixed["full_allocation_digest_sha256"] == q011gw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_590
    assert q011gw_structure["compatible_count"] == 1_590
    assert fixed["compatible_allocation_digest_sha256"] == q011gw.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 7, 0, 2, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 7, 0, 2, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 28_140
    assert fixed["parent_witness_compatible_index"] == 1_589
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gw result is not sealed")
def test_q011gw_classifies_every_registered_exact_interval(
    q011gw_cycle: dict[str, Any],
) -> None:
    partition = q011gw_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_590
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_590
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_590))
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
        assert record["intersection_width_hex"] == q011gw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011gw.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_590,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gw result is not sealed")
def test_q011gw_applies_the_registered_exclusive_stopping_rule(
    q011gw_cycle: dict[str, Any],
) -> None:
    assert q011gw_cycle["study_validity"] == "passed"
    assert q011gw_cycle["failed_validity_order"] == []
    assert q011gw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011gw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gw_cycle["diagnostic_gates"].values())
    assert q011gw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011gw_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011gw_cycle["diagnostic_classification"] == q011gw.INERT_CLASSIFICATION
    assert not q011gw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011gw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_third_q011cb_witness"],
        theorem["sixty_third_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_third_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gw result is not sealed")
def test_q011gw_preserves_boundary_and_reproducible_digests(
    q011gw_cycle: dict[str, Any],
) -> None:
    theorem = q011gw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_third_q011cb_witness"],
        theorem["sixty_third_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_third_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 62" in q011gw_cycle["claim_boundary"]
    assert "ordinals 0 through 61" in q011gw_cycle["claim_boundary"]
    assert "later 44737 Q011cb refined signatures" in q011gw_cycle["claim_boundary"]
    assert "Q011gx" in q011gw_cycle["next_change"]
    json.dumps(q011gw_cycle, allow_nan=False)
    assert {name: q011gw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011gw_cycle["result_digest_sha256"] == (
        q011gw.q011b._canonical_json_sha256(q011gw._result_digest_sections(q011gw_cycle))
    )
    assert q011gw._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gw result is not sealed")
def test_q011gw_study_metadata_and_optional_artifact_are_scoped(
    q011gw_study: dict[str, Any],
) -> None:
    assert q011gw_study["schema_version"] == 1
    assert q011gw_study["source"] == source_metadata()
    assert q011gw_study["study_gate"] == "passed"
    assert q011gw_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011gw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_590
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 62
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gw_study, allow_nan=False)

    runner_path = Path(q011gw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gw_degree34_sixty_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gw.q011b._canonical_json_sha256(q011gw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
