from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dq_degree34_twenty_first_individual_partition_audit as q011dq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "0fe8f9d99572c1c1406e796877f39084a7a3276bfdf5d027a821361cf7b8a043"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "1bd0fdc5bd0e0439280546c9174b09616413c38c8447622c57b176e6428695fb"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "d9c7309eea2a8f98545d6766f4735465453b86cdbf10315c1a3d98b5c60688f9",
    "partition_input_digest_sha256": "a18084acfb2136d82030029941a212cd45bbd6c33fd896061581ec7d132b405b",
    "allocation_audit_digest_sha256": "b0dd901688d59add15cd6c4864a73265923e6b8e2819bff05a33d27b03978633",
    "result_digest_sha256": "5b3835a3ffde2ff43814644b010a739fa7dc8a3cca3408759f80c42ada38d8f7",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "c1338d55c00bea804f5a409dfc3db9f25a3e265565f5cd986fe9a2ce67ee082d"
    ),
    "parent_center_product_interval_digest_sha256": (
        "90476365b83a67e78e47b11d82b664f9e0362f484de1b09d63a0979dabe04d27"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "fc80a308e6f3b8923125657f9cc1c0dd75d9a3bf0fb5c8c958889aec3b809afa"
    ),
    "allocation_classification_record_digest_sha256": (
        "06714821b56544c1f1d3ee59be2511464faedd1895e86365ed66adb8b94840fa"
    ),
}


@pytest.fixture(scope="module")
def q011dq_study() -> dict[str, Any]:
    return q011dq.run_q011dq_study()


@pytest.fixture(scope="module")
def q011dq_cycle(q011dq_study: dict[str, Any]) -> dict[str, Any]:
    return q011dq_study["cycle"]


def test_q011dq_seals_q011dp_and_all_prior_inputs(
    q011dq_cycle: dict[str, Any],
) -> None:
    sealed = q011dq_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 99
    assert sealed["direct_digest_count"] == 458
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dp"]["digests"]) == q011dq.Q011DP_DIGESTS
    assert sealed["q011dp"]["artifact_sha256"] == q011dq.Q011DP_ARTIFACT_SHA256
    assert sealed["q011dp"]["runner_sha256"] == q011dq.Q011DP_RUNNER_SHA256
    assert sealed["q011dp"]["resolved_witness_digest_sha256"] == (
        q011dq.EXPECTED_ORDINAL_NINETEEN_RESOLUTION_DIGEST
    )


def test_q011dq_selects_exactly_flatten_ordinal_twenty(
    q011dq_cycle: dict[str, Any],
) -> None:
    fixed = q011dq_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 20
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(20))
    assert selection["ordinal_nineteen_resolution_digest_sha256"] == (
        q011dq.EXPECTED_ORDINAL_NINETEEN_RESOLUTION_DIGEST
    )
    parent = selection["twenty_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 2_266
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dq_reconstructs_registered_partition_and_inventory(
    q011dq_cycle: dict[str, Any],
) -> None:
    fixed = q011dq_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [4, 3],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dq.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dq.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 40_320
    assert fixed["full_allocation_digest_sha256"] == q011dq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_266
    assert fixed["compatible_allocation_digest_sha256"] == (q011dq.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 40_200
    assert fixed["parent_witness_compatible_index"] == 2_265
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dq_all_exact_intervals_are_parent_identical(
    q011dq_cycle: dict[str, Any],
) -> None:
    partition = q011dq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_266
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_266
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_266))
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
        assert record["intersection_width_hex"] == (q011dq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dq.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dq_records_interval_inert_persistence(
    q011dq_cycle: dict[str, Any],
) -> None:
    assert q011dq_cycle["study_validity"] == "passed"
    assert q011dq_cycle["failed_validity_order"] == []
    assert q011dq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dq_cycle["diagnostic_gates"].values())
    assert q011dq_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dq_cycle["diagnostic_classification"] == q011dq.INERT_CLASSIFICATION
    assert q011dq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dq_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_266,
    }
    partition = q011dq_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dq_preserves_boundary_and_reproducible_digests(
    q011dq_cycle: dict[str, Any],
) -> None:
    theorem = q011dq_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_first_q011cb_witness"]
    assert not theorem["twenty_first_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 20" in q011dq_cycle["claim_boundary"]
    assert "later 44779 Q011cb refined signatures" in q011dq_cycle["claim_boundary"]
    assert "Q011dr" in q011dq_cycle["next_change"]
    json.dumps(q011dq_cycle, allow_nan=False)
    assert {name: q011dq_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dq_cycle["result_digest_sha256"] == (
        q011dq.q011b._canonical_json_sha256(q011dq._result_digest_sections(q011dq_cycle))
    )
    assert q011dq._protocol_globals_are_restored()


def test_q011dq_study_metadata_and_optional_artifact_are_scoped(
    q011dq_study: dict[str, Any],
) -> None:
    assert q011dq_study["schema_version"] == 1
    assert q011dq_study["source"] == source_metadata()
    assert q011dq_study["study_gate"] == "passed"
    assert q011dq_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_266
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 20
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dq_study, allow_nan=False)

    runner_path = Path(q011dq.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dq_degree34_twenty_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dq.q011b._canonical_json_sha256(q011dq._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
