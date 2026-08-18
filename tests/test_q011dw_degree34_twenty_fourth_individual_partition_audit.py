from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dw_degree34_twenty_fourth_individual_partition_audit as q011dw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a83eabce61793053cfbce2561289c77ecd8516219ba8a6f470e641fdbc393a68"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "76db99e4bf8bee173fefd1b11eaeee3de2a0390eacedbc48593e0719a6b2c795"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "28ff75ff10a69a936bf454cdac0d39dbe8c6edab37a6a47450ca9485f3894431",
    "partition_input_digest_sha256": "cb4d78ef5a5487088eafcc380b5d427b7f6ae5237dbd59ca66081e7f29a81692",
    "allocation_audit_digest_sha256": "da80fbac9ce70b7a35078f37638d2337702a70ca91bbff99babab4d9b7dee1b2",
    "result_digest_sha256": "74bb6f9722eb6de84ee5d9fa61702bc52959d83b02381fc7bdf756ea0659be45",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "4f4e384d91c66abf15a612487b3bb40889b92566bb955806dc3f890d39b5f032"
    ),
    "parent_center_product_interval_digest_sha256": (
        "7b8d7f7ab3f05b60536a34d0554ffe157fc8d17d5e7bb88b0e9c8bb53ef24e67"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "707d56c7625c9571783f90d1dbbdb04b0cf3fec2f22e0a32fcd9dae90448f3fc"
    ),
    "allocation_classification_record_digest_sha256": (
        "2c1cec27a7e15694f93d366e31b223a3ee4657b9fec279a1dd8e02180d3d6528"
    ),
}


@pytest.fixture(scope="module")
def q011dw_study() -> dict[str, Any]:
    return q011dw.run_q011dw_study()


@pytest.fixture(scope="module")
def q011dw_cycle(q011dw_study: dict[str, Any]) -> dict[str, Any]:
    return q011dw_study["cycle"]


def test_q011dw_seals_q011dv_and_all_prior_inputs(
    q011dw_cycle: dict[str, Any],
) -> None:
    sealed = q011dw_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 105
    assert sealed["direct_digest_count"] == 485
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dv"]["digests"]) == q011dw.Q011DV_DIGESTS
    assert sealed["q011dv"]["artifact_sha256"] == q011dw.Q011DV_ARTIFACT_SHA256
    assert sealed["q011dv"]["runner_sha256"] == q011dw.Q011DV_RUNNER_SHA256
    assert sealed["q011dv"]["resolved_witness_digest_sha256"] == (
        q011dw.EXPECTED_ORDINAL_TWENTY_TWO_RESOLUTION_DIGEST
    )


def test_q011dw_selects_exactly_flatten_ordinal_twenty_three(
    q011dw_cycle: dict[str, Any],
) -> None:
    fixed = q011dw_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 23
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(23))
    assert selection["ordinal_twenty_two_resolution_digest_sha256"] == (
        q011dw.EXPECTED_ORDINAL_TWENTY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["twenty_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 911
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dw_reconstructs_registered_partition_and_inventory(
    q011dw_cycle: dict[str, Any],
) -> None:
    fixed = q011dw_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dw.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 16_128
    assert fixed["full_allocation_digest_sha256"] == q011dw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 911
    assert fixed["compatible_allocation_digest_sha256"] == (q011dw.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 16_080
    assert fixed["parent_witness_compatible_index"] == 910
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dw_all_exact_intervals_are_parent_identical(
    q011dw_cycle: dict[str, Any],
) -> None:
    partition = q011dw_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011dw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dw.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dw_records_interval_inert_persistence(
    q011dw_cycle: dict[str, Any],
) -> None:
    assert q011dw_cycle["study_validity"] == "passed"
    assert q011dw_cycle["failed_validity_order"] == []
    assert q011dw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dw_cycle["diagnostic_gates"].values())
    assert q011dw_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dw_cycle["diagnostic_classification"] == q011dw.INERT_CLASSIFICATION
    assert q011dw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dw_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 911,
    }
    partition = q011dw_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dw_preserves_boundary_and_reproducible_digests(
    q011dw_cycle: dict[str, Any],
) -> None:
    theorem = q011dw_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_fourth_q011cb_witness"]
    assert not theorem["twenty_fourth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011dv_ordinal_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dt_ordinal_twenty_one_phase_resolution_is_preserved"]
    assert theorem["q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dr_ordinal_twenty_phase_resolution_is_preserved"]
    assert theorem["q011dq_ordinal_twenty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dp_ordinal_nineteen_phase_resolution_is_preserved"]
    assert theorem["q011do_ordinal_nineteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dn_ordinal_eighteen_phase_resolution_is_preserved"]
    assert theorem["q011dm_ordinal_eighteen_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 23" in q011dw_cycle["claim_boundary"]
    assert "later 44776 Q011cb refined signatures" in q011dw_cycle["claim_boundary"]
    assert "Q011dx" in q011dw_cycle["next_change"]
    json.dumps(q011dw_cycle, allow_nan=False)
    assert {name: q011dw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dw_cycle["result_digest_sha256"] == (
        q011dw.q011b._canonical_json_sha256(q011dw._result_digest_sections(q011dw_cycle))
    )
    assert q011dw._protocol_globals_are_restored()


def test_q011dw_study_metadata_and_optional_artifact_are_scoped(
    q011dw_study: dict[str, Any],
) -> None:
    assert q011dw_study["schema_version"] == 1
    assert q011dw_study["source"] == source_metadata()
    assert q011dw_study["study_gate"] == "passed"
    assert q011dw_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 911
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 23
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dw_study, allow_nan=False)

    runner_path = Path(q011dw.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dw_degree34_twenty_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dw.q011b._canonical_json_sha256(q011dw._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
