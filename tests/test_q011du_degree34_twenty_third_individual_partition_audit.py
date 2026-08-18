from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011du_degree34_twenty_third_individual_partition_audit as q011du
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "9237f8c118f6a5720a1cfeeff4ddb5f5a0754f75641def0e59c77283ee237060"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "3ad1915eb6910097deb659c97a0926e5f9e4df791b2695a8010dfdcc8ad0133f"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "1b3967e56a5d74ea4f240f07301774df3f4ee07f4d0c441fd946a5ebeda8580f",
    "partition_input_digest_sha256": "3cc948f8d5cd9658d2d8af59bea5624f2b288d4b7ddffd1ed2bbcd82c7dd1ad6",
    "allocation_audit_digest_sha256": "162682b50683fa5e428d146a03dd25d59d4cfdb55c0f6bae1f748c2efa98d6bd",
    "result_digest_sha256": "f9ada7833604eed63a0cc179ccc93b454d4dc8f076230b4d578285cd5ede70ac",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "2d5fa308855a20734861394dcb4bed192d096cafb7198a9abc6ed465c49f3d3b"
    ),
    "parent_center_product_interval_digest_sha256": (
        "23c1decb0c278e51aeeb6d8e54b317d2693d4c2d5f45cdb720d48faf9656ed72"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "3f91d44ef6251c9b9caf0cc445bce2ba13e4dcea76d4202c9a4d3759441b98a1"
    ),
    "allocation_classification_record_digest_sha256": (
        "289bd169085710566b6f33856626fe32d01756be5ed80feed6c345e2e16e30f5"
    ),
}


@pytest.fixture(scope="module")
def q011du_study() -> dict[str, Any]:
    return q011du.run_q011du_study()


@pytest.fixture(scope="module")
def q011du_cycle(q011du_study: dict[str, Any]) -> dict[str, Any]:
    return q011du_study["cycle"]


def test_q011du_seals_q011dt_and_all_prior_inputs(
    q011du_cycle: dict[str, Any],
) -> None:
    sealed = q011du_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 103
    assert sealed["direct_digest_count"] == 476
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dt"]["digests"]) == q011du.Q011DT_DIGESTS
    assert sealed["q011dt"]["artifact_sha256"] == q011du.Q011DT_ARTIFACT_SHA256
    assert sealed["q011dt"]["runner_sha256"] == q011du.Q011DT_RUNNER_SHA256
    assert sealed["q011dt"]["resolved_witness_digest_sha256"] == (
        q011du.EXPECTED_ORDINAL_TWENTY_ONE_RESOLUTION_DIGEST
    )


def test_q011du_selects_exactly_flatten_ordinal_twenty_two(
    q011du_cycle: dict[str, Any],
) -> None:
    fixed = q011du_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 22
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(22))
    assert selection["ordinal_twenty_one_resolution_digest_sha256"] == (
        q011du.EXPECTED_ORDINAL_TWENTY_ONE_RESOLUTION_DIGEST
    )
    parent = selection["twenty_third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_590
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011du.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011du.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011du.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011du_reconstructs_registered_partition_and_inventory(
    q011du_cycle: dict[str, Any],
) -> None:
    fixed = q011du_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011du.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011du.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 28_224
    assert fixed["full_allocation_digest_sha256"] == q011du.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_590
    assert fixed["compatible_allocation_digest_sha256"] == (q011du.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 28_140
    assert fixed["parent_witness_compatible_index"] == 1_589
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011du_all_exact_intervals_are_parent_identical(
    q011du_cycle: dict[str, Any],
) -> None:
    partition = q011du_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011du.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011du.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011du_records_interval_inert_persistence(
    q011du_cycle: dict[str, Any],
) -> None:
    assert q011du_cycle["study_validity"] == "passed"
    assert q011du_cycle["failed_validity_order"] == []
    assert q011du_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011du_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011du_cycle["diagnostic_gates"].values())
    assert q011du_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011du_cycle["diagnostic_classification"] == q011du.INERT_CLASSIFICATION
    assert q011du_cycle["scientific_outcome"] == "not_evaluated"
    assert q011du_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_590,
    }
    partition = q011du_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011du_preserves_boundary_and_reproducible_digests(
    q011du_cycle: dict[str, Any],
) -> None:
    theorem = q011du_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_third_q011cb_witness"]
    assert not theorem["twenty_third_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 22" in q011du_cycle["claim_boundary"]
    assert "later 44777 Q011cb refined signatures" in q011du_cycle["claim_boundary"]
    assert "Q011dv" in q011du_cycle["next_change"]
    json.dumps(q011du_cycle, allow_nan=False)
    assert {name: q011du_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011du_cycle["result_digest_sha256"] == (
        q011du.q011b._canonical_json_sha256(q011du._result_digest_sections(q011du_cycle))
    )
    assert q011du._protocol_globals_are_restored()


def test_q011du_study_metadata_and_optional_artifact_are_scoped(
    q011du_study: dict[str, Any],
) -> None:
    assert q011du_study["schema_version"] == 1
    assert q011du_study["source"] == source_metadata()
    assert q011du_study["study_gate"] == "passed"
    assert q011du_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011du_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_590
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011du_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 22
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011du_study, allow_nan=False)

    runner_path = Path(q011du.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011du_degree34_twenty_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011du artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011du.q011b._canonical_json_sha256(q011du._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
