from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ds_degree34_twenty_second_individual_partition_audit as q011ds
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "748d40006680ce1c9e48ccdd2da54c318e90475553f5969addfca3fd6000e990"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "950e4897abf3a497e5df89d7d78175ff4ac73d2f877038c502a5122dfe1f8bcb",
    "partition_input_digest_sha256": "b11b2695118e78240af575f1641bb242c0ee302c149f20896972ec508ff4e370",
    "allocation_audit_digest_sha256": "994b9fd79a93d5dcd8d13b4f43abbd3ba977a451b06ffa09b9bb8556126fdd5d",
    "result_digest_sha256": "06c62852aba7b6b64a818178ed2c6f236925753e375cea00d484af4ca53088bb",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "21356aa321976c33795653cdb4b7621fed64c647010082a3b040041cca284fe4"
    ),
    "parent_center_product_interval_digest_sha256": (
        "d9921dcd5e8349b8fe7ab22e68387ce6f826469bc46c95ac9edecf687e9f02b5"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "5687e9119d4180fa33a63c9add44cc462bdacc77041b65d74418a5c4f0544b53"
    ),
    "allocation_classification_record_digest_sha256": (
        "841a38c865a31fbbef3aedd2036dbb36d7623bd3d10691d9f4ed7b65b9814a22"
    ),
}


@pytest.fixture(scope="module")
def q011ds_study() -> dict[str, Any]:
    return q011ds.run_q011ds_study()


@pytest.fixture(scope="module")
def q011ds_cycle(q011ds_study: dict[str, Any]) -> dict[str, Any]:
    return q011ds_study["cycle"]


def test_q011ds_seals_q011dr_and_all_prior_inputs(
    q011ds_cycle: dict[str, Any],
) -> None:
    sealed = q011ds_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 101
    assert sealed["direct_digest_count"] == 467
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dr"]["digests"]) == q011ds.Q011DR_DIGESTS
    assert sealed["q011dr"]["artifact_sha256"] == q011ds.Q011DR_ARTIFACT_SHA256
    assert sealed["q011dr"]["runner_sha256"] == q011ds.Q011DR_RUNNER_SHA256
    assert sealed["q011dr"]["resolved_witness_digest_sha256"] == (
        q011ds.EXPECTED_ORDINAL_TWENTY_RESOLUTION_DIGEST
    )


def test_q011ds_selects_exactly_flatten_ordinal_twenty_one(
    q011ds_cycle: dict[str, Any],
) -> None:
    fixed = q011ds_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 21
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(21))
    assert selection["ordinal_twenty_resolution_digest_sha256"] == (
        q011ds.EXPECTED_ORDINAL_TWENTY_RESOLUTION_DIGEST
    )
    parent = selection["twenty_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_041
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ds.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ds.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ds.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ds_reconstructs_registered_partition_and_inventory(
    q011ds_cycle: dict[str, Any],
) -> None:
    fixed = q011ds_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ds.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ds.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 36_288
    assert fixed["full_allocation_digest_sha256"] == q011ds.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_041
    assert fixed["compatible_allocation_digest_sha256"] == (q011ds.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 36_180
    assert fixed["parent_witness_compatible_index"] == 2_040
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ds_all_exact_intervals_are_parent_identical(
    q011ds_cycle: dict[str, Any],
) -> None:
    partition = q011ds_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011ds.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011ds.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ds_records_interval_inert_persistence(
    q011ds_cycle: dict[str, Any],
) -> None:
    assert q011ds_cycle["study_validity"] == "passed"
    assert q011ds_cycle["failed_validity_order"] == []
    assert q011ds_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ds_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ds_cycle["diagnostic_gates"].values())
    assert q011ds_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ds_cycle["diagnostic_classification"] == q011ds.INERT_CLASSIFICATION
    assert q011ds_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ds_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_041,
    }
    partition = q011ds_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ds_preserves_boundary_and_reproducible_digests(
    q011ds_cycle: dict[str, Any],
) -> None:
    theorem = q011ds_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_second_q011cb_witness"]
    assert not theorem["twenty_second_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 21" in q011ds_cycle["claim_boundary"]
    assert "later 44778 Q011cb refined signatures" in q011ds_cycle["claim_boundary"]
    assert "Q011dt" in q011ds_cycle["next_change"]
    json.dumps(q011ds_cycle, allow_nan=False)
    assert {name: q011ds_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ds_cycle["result_digest_sha256"] == (
        q011ds.q011b._canonical_json_sha256(q011ds._result_digest_sections(q011ds_cycle))
    )
    assert q011ds._protocol_globals_are_restored()


def test_q011ds_study_metadata_and_optional_artifact_are_scoped(
    q011ds_study: dict[str, Any],
) -> None:
    assert q011ds_study["schema_version"] == 1
    assert q011ds_study["source"] == source_metadata()
    assert q011ds_study["study_gate"] == "passed"
    assert q011ds_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ds_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_041
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ds_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 21
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ds_study, allow_nan=False)

    runner_path = Path(q011ds.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ds_degree34_twenty_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ds artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ds.q011b._canonical_json_sha256(q011ds._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
