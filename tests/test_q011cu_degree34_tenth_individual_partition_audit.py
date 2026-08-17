from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cu_degree34_tenth_individual_partition_audit as q011cu
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "14c443c2af74eac1d4a4a150f1cdb3cc5b3f880deb0560c9a1fcf7edaecf5519"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "3d23713704c5f504bb7603fa6ebedb5562e0613da00557c2ea2d2953d29d712c"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "faa189a62c5bc6f72725351d63ab116ab56124efd3425fce93f5b5c9dc78e524",
    "partition_input_digest_sha256": (
        "7f2886dec624a101845736154f308c7daf733c1a336f96f696c723b68fc8a4ff"
    ),
    "allocation_audit_digest_sha256": (
        "f0efb18ad8dffd86e15c1f521f02ce1f63de631d347fb04dae951c05ae6a13ee"
    ),
    "result_digest_sha256": "b478dacccdf0eb40cb16bda7c8c3dabb13e58ce09075a14d7825c2c5bf05e68c",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "3a14d87253f5088af7c0dea52a6e68cbfb1075c8fc758ac0d3370e044c73907c"
    ),
    "parent_center_product_interval_digest_sha256": (
        "2e24a4fe96c6e9552dd3579019cb41060b86a488787b62a0f4c0779424baa4ba"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "2f377ffb8684a6c3bbacad4ce6f9b2691114d474ee8a97a1e60b0de0689841e3"
    ),
    "allocation_classification_record_digest_sha256": (
        "023d95194355d1fbc112571b3349bb32ecd61842f8f3fda56546fb7b19889357"
    ),
}


@pytest.fixture(scope="module")
def q011cu_study() -> dict[str, Any]:
    return q011cu.run_q011cu_study()


@pytest.fixture(scope="module")
def q011cu_cycle(q011cu_study: dict[str, Any]) -> dict[str, Any]:
    return q011cu_study["cycle"]


def test_q011cu_seals_q011ct_and_all_prior_inputs(
    q011cu_cycle: dict[str, Any],
) -> None:
    sealed = q011cu_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 77
    assert sealed["direct_digest_count"] == 359
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ct"]["digests"]) == q011cu.Q011CT_DIGESTS
    assert sealed["q011ct"]["artifact_sha256"] == q011cu.Q011CT_ARTIFACT_SHA256
    assert sealed["q011ct"]["runner_sha256"] == q011cu.Q011CT_RUNNER_SHA256
    assert sealed["q011ct"]["resolved_witness_digest_sha256"] == (
        q011cu.EXPECTED_ORDINAL_EIGHT_RESOLUTION_DIGEST
    )


def test_q011cu_selects_exactly_flatten_ordinal_nine(
    q011cu_cycle: dict[str, Any],
) -> None:
    fixed = q011cu_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["tenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 9
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    assert selection["ordinal_four_resolution_digest_sha256"] == (
        q011cu.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    assert selection["ordinal_five_resolution_digest_sha256"] == (
        q011cu.EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )
    assert selection["ordinal_six_resolution_digest_sha256"] == (
        q011cu.EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
    )
    assert selection["ordinal_seven_resolution_digest_sha256"] == (
        q011cu.EXPECTED_ORDINAL_SEVEN_RESOLUTION_DIGEST
    )
    assert selection["ordinal_eight_resolution_digest_sha256"] == (
        q011cu.EXPECTED_ORDINAL_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["tenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 1_194
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cu.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011cu.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011cu.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011cu_reconstructs_registered_partition_and_inventory(
    q011cu_cycle: dict[str, Any],
) -> None:
    fixed = q011cu_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [1, 6],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011cu.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == (q011cu.EXPECTED_IDENTIFIER_ORDER)
    assert fixed["full_allocation_count"] == 21_168
    assert fixed["full_allocation_digest_sha256"] == q011cu.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_194
    assert fixed["compatible_allocation_digest_sha256"] == (q011cu.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 21_084
    assert fixed["parent_witness_compatible_index"] == 1_193
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011cu_all_exact_intervals_are_parent_identical(
    q011cu_cycle: dict[str, Any],
) -> None:
    partition = q011cu_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_194
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_194
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_194))
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
        assert record["intersection_width_hex"] == (q011cu.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011cu.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cu_records_interval_inert_persistence(
    q011cu_cycle: dict[str, Any],
) -> None:
    assert q011cu_cycle["study_validity"] == "passed"
    assert q011cu_cycle["failed_validity_order"] == []
    assert q011cu_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cu_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cu_cycle["diagnostic_gates"].values())
    assert q011cu_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cu_cycle["diagnostic_classification"] == q011cu.INERT_CLASSIFICATION
    assert q011cu_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cu_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_194,
    }
    partition = q011cu_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cu_preserves_boundary_and_reproducible_digests(
    q011cu_cycle: dict[str, Any],
) -> None:
    theorem = q011cu_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_tenth_q011cb_witness"]
    assert not theorem["tenth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
    assert theorem["q011cr_ordinal_seven_phase_resolution_is_preserved"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 9" in q011cu_cycle["claim_boundary"]
    assert "later 44790 Q011cb refined signatures" in q011cu_cycle["claim_boundary"]
    json.dumps(q011cu_cycle, allow_nan=False)
    assert {
        name: q011cu_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011cu_cycle["result_digest_sha256"] == (
        q011cu.q011b._canonical_json_sha256(q011cu._result_digest_sections(q011cu_cycle))
    )
    assert q011cu._protocol_globals_are_restored()


def test_q011cu_study_metadata_and_optional_artifact_are_scoped(
    q011cu_study: dict[str, Any],
) -> None:
    assert q011cu_study["schema_version"] == 1
    assert q011cu_study["source"] == source_metadata()
    assert q011cu_study["study_gate"] == "passed"
    assert q011cu_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011cu_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_194
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cu_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 9
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cu_study, allow_nan=False)

    runner_path = Path(q011cu.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / ("q011cu_degree34_tenth_individual_partition_audit.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cu artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cu.q011b._canonical_json_sha256(q011cu._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
