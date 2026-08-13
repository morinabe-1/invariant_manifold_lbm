from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cm_degree34_sixth_individual_partition_audit as q011cm
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "47e81246cc6e091a7a173e7142629cfda81e6366d180d65aa9f18810e13bdbfa"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "5e960b6377a50e0ac609372810d46b4886b7476963b6fd2ce5d5054f9c1c3601",
    "partition_input_digest_sha256": (
        "e54bbb6e88d032d6c0c3a5c18ad4ae6cd746eaa0f9fcb8ab5cafa516b8b6c902"
    ),
    "allocation_audit_digest_sha256": (
        "b2e446405ccef8db32dbcc60f55d229527ba8bf9575b44d801ac847afdefb2f2"
    ),
    "result_digest_sha256": "7a743070e57327e82b72bc74b10a8b59ded71dd7e73a19507777fad7325383c5",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "fa265af983a68669f09037ecd2a2621fbdfbfb4639e281efd446f3f41f8a9aee"
    ),
    "parent_center_product_interval_digest_sha256": (
        "66163890ee0a0c8693e87682535847e5410184b3f2817553918a56764474d971"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "c8942190274715d605b6eac57c37c9c8c98da665d11f46cf0431745e09635e49"
    ),
    "allocation_classification_record_digest_sha256": (
        "c6d0506868264b9de7ac784730f02bd09f61c57b1bacd4cccbdc4dac1c9c3dff"
    ),
}


@pytest.fixture(scope="module")
def q011cm_study() -> dict[str, Any]:
    return q011cm.run_q011cm_study()


@pytest.fixture(scope="module")
def q011cm_cycle(q011cm_study: dict[str, Any]) -> dict[str, Any]:
    return q011cm_study["cycle"]


def test_q011cm_seals_q011cl_and_all_prior_inputs(
    q011cm_cycle: dict[str, Any],
) -> None:
    sealed = q011cm_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 69
    assert sealed["direct_digest_count"] == 323
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cl"]["digests"]) == q011cm.Q011CL_DIGESTS
    assert sealed["q011cl"]["artifact_sha256"] == q011cm.Q011CL_ARTIFACT_SHA256
    assert sealed["q011cl"]["runner_sha256"] == q011cm.Q011CL_RUNNER_SHA256
    assert sealed["q011cl"]["resolved_witness_digest_sha256"] == (
        q011cm.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )


def test_q011cm_selects_exactly_flatten_ordinal_five(
    q011cm_cycle: dict[str, Any],
) -> None:
    fixed = q011cm_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["sixth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 5
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2, 3, 4]
    assert selection["ordinal_four_resolution_digest_sha256"] == (
        q011cm.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    parent = selection["sixth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 852
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cm.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011cm.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011cm.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011cm_reconstructs_registered_partition_and_inventory(
    q011cm_cycle: dict[str, Any],
) -> None:
    fixed = q011cm_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011cm.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == (
        q011cm.EXPECTED_IDENTIFIER_ORDER
    )
    assert fixed["full_allocation_count"] == 15_120
    assert fixed["full_allocation_digest_sha256"] == q011cm.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 852
    assert fixed["compatible_allocation_digest_sha256"] == (
        q011cm.EXPECTED_COMPATIBLE_DIGEST
    )
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 15_012
    assert fixed["parent_witness_compatible_index"] == 851
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011cm_all_exact_intervals_are_parent_identical(
    q011cm_cycle: dict[str, Any],
) -> None:
    partition = q011cm_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 852
    assert partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 852
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(852)
    )
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
        assert record["intersection_width_hex"] == (
            q011cm.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        )
        assert record["center_only_gap_hex"] == q011cm.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cm_records_interval_inert_persistence(
    q011cm_cycle: dict[str, Any],
) -> None:
    assert q011cm_cycle["study_validity"] == "passed"
    assert q011cm_cycle["failed_validity_order"] == []
    assert q011cm_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cm_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cm_cycle["diagnostic_gates"].values())
    assert q011cm_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cm_cycle["diagnostic_classification"] == q011cm.INERT_CLASSIFICATION
    assert q011cm_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cm_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 852,
    }
    partition = q011cm_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cm_preserves_boundary_and_reproducible_digests(
    q011cm_cycle: dict[str, Any],
) -> None:
    theorem = q011cm_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_sixth_q011cb_witness"]
    assert not theorem["sixth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 5" in q011cm_cycle["claim_boundary"]
    assert "later 44794 Q011cb refined signatures" in q011cm_cycle["claim_boundary"]
    json.dumps(q011cm_cycle, allow_nan=False)
    assert {
        name: q011cm_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011cm_cycle["result_digest_sha256"] == (
        q011cm.q011b._canonical_json_sha256(
            q011cm._result_digest_sections(q011cm_cycle)
        )
    )
    assert q011cm._protocol_globals_are_restored()


def test_q011cm_study_metadata_and_optional_artifact_are_scoped(
    q011cm_study: dict[str, Any],
) -> None:
    assert q011cm_study["schema_version"] == 1
    assert q011cm_study["source"] == source_metadata()
    assert q011cm_study["study_gate"] == "passed"
    assert q011cm_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011cm_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 852
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cm_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 5
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cm_study, allow_nan=False)

    runner_path = Path(q011cm.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011cm_degree34_sixth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cm artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cm.q011b._canonical_json_sha256(
            q011cm._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
