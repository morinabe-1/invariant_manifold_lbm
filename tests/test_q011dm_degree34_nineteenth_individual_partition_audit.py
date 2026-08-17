from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dm_degree34_nineteenth_individual_partition_audit as q011dm
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "06ec727ff92ee07bd2a8ada0fcad625076414932d64449a4355b92d0c15cb46e"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "9792f887398d82ecc307d2d87e5be94189fc0f8c56640d5de6d2b02c61c995e4",
    "partition_input_digest_sha256": "630c2778a3d839e9d730143847d730e933fee39583cfa92f6169649c1df91d4c",
    "allocation_audit_digest_sha256": "ab04a5a386d9811f32afcb0343252e39cbf0d0eb47192441c1d5b660ca124a0a",
    "result_digest_sha256": "c4587bf8d083d8a3281966fe2cdc92b8fbb0739b9d9ba8e2b364d5010c187f63",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "7240c4f43f4289a0e6423cf669b6aa5ae780c2c64360d12fa6171338110c39b7"
    ),
    "parent_center_product_interval_digest_sha256": (
        "dd1197814b82cce38ae98885831a3ca0a5752cccd45bedabefb2b38b37b0799b"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "7ec1f3d302506ddeb11ae89df22fc62ab3e8e3bc07a385391b4cc4768a9da03b"
    ),
    "allocation_classification_record_digest_sha256": (
        "bfa43d12ef238851729ef57dfb4a316885a4c5a17f892b473858406385a84702"
    ),
}


@pytest.fixture(scope="module")
def q011dm_study() -> dict[str, Any]:
    return q011dm.run_q011dm_study()


@pytest.fixture(scope="module")
def q011dm_cycle(q011dm_study: dict[str, Any]) -> dict[str, Any]:
    return q011dm_study["cycle"]


def test_q011dm_seals_q011dl_and_all_prior_inputs(
    q011dm_cycle: dict[str, Any],
) -> None:
    sealed = q011dm_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 95
    assert sealed["direct_digest_count"] == 440
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dl"]["digests"]) == q011dm.Q011DL_DIGESTS
    assert sealed["q011dl"]["artifact_sha256"] == q011dm.Q011DL_ARTIFACT_SHA256
    assert sealed["q011dl"]["runner_sha256"] == q011dm.Q011DL_RUNNER_SHA256
    assert sealed["q011dl"]["resolved_witness_digest_sha256"] == (
        q011dm.EXPECTED_ORDINAL_SEVENTEEN_RESOLUTION_DIGEST
    )


def test_q011dm_selects_exactly_flatten_ordinal_eighteen(
    q011dm_cycle: dict[str, Any],
) -> None:
    fixed = q011dm_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["nineteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 18
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(18))
    assert selection["ordinal_seventeen_resolution_digest_sha256"] == (
        q011dm.EXPECTED_ORDINAL_SEVENTEEN_RESOLUTION_DIGEST
    )
    parent = selection["nineteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 2_041
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dm.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dm.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dm.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dm_reconstructs_registered_partition_and_inventory(
    q011dm_cycle: dict[str, Any],
) -> None:
    fixed = q011dm_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dm.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dm.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 36_288
    assert fixed["full_allocation_digest_sha256"] == q011dm.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_041
    assert fixed["compatible_allocation_digest_sha256"] == (q011dm.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 36_180
    assert fixed["parent_witness_compatible_index"] == 2_040
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dm_all_exact_intervals_are_parent_identical(
    q011dm_cycle: dict[str, Any],
) -> None:
    partition = q011dm_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011dm.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dm.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dm_records_interval_inert_persistence(
    q011dm_cycle: dict[str, Any],
) -> None:
    assert q011dm_cycle["study_validity"] == "passed"
    assert q011dm_cycle["failed_validity_order"] == []
    assert q011dm_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dm_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dm_cycle["diagnostic_gates"].values())
    assert q011dm_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dm_cycle["diagnostic_classification"] == q011dm.INERT_CLASSIFICATION
    assert q011dm_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dm_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_041,
    }
    partition = q011dm_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dm_preserves_boundary_and_reproducible_digests(
    q011dm_cycle: dict[str, Any],
) -> None:
    theorem = q011dm_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_nineteenth_q011cb_witness"]
    assert not theorem["nineteenth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011dl_ordinal_seventeen_phase_resolution_is_preserved"]
    assert theorem["q011dk_ordinal_seventeen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dj_ordinal_sixteen_phase_resolution_is_preserved"]
    assert theorem["q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011df_ordinal_fourteen_phase_resolution_is_preserved"]
    assert theorem["q011dd_ordinal_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011db_ordinal_twelve_phase_resolution_is_preserved"]
    assert theorem["q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 18" in q011dm_cycle["claim_boundary"]
    assert "later 44781 Q011cb refined signatures" in q011dm_cycle["claim_boundary"]
    assert "Q011dn" in q011dm_cycle["next_change"]
    json.dumps(q011dm_cycle, allow_nan=False)
    assert {name: q011dm_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dm_cycle["result_digest_sha256"] == (
        q011dm.q011b._canonical_json_sha256(q011dm._result_digest_sections(q011dm_cycle))
    )
    assert q011dm._protocol_globals_are_restored()


def test_q011dm_study_metadata_and_optional_artifact_are_scoped(
    q011dm_study: dict[str, Any],
) -> None:
    assert q011dm_study["schema_version"] == 1
    assert q011dm_study["source"] == source_metadata()
    assert q011dm_study["study_gate"] == "passed"
    assert q011dm_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dm_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_041
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dm_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 18
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dm_study, allow_nan=False)

    runner_path = Path(q011dm.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dm_degree34_nineteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dm artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dm.q011b._canonical_json_sha256(q011dm._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
