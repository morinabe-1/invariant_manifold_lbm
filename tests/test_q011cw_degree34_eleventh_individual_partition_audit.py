from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cw_degree34_eleventh_individual_partition_audit as q011cw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "4053f6f3738331414e2b1620a7892b1cadfbbdd98f104c3bb52a676e3291093e"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "88f4f7b05675c58c523f58910b1c795507c92cceea89006658862722be7be355"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "6a59a48d974eb6d42af91ee12bfe9b927b4d7ce477340748bc85ca805233882d",
    "partition_input_digest_sha256": (
        "53acd6d0d2638c5939ee367de45d3e4a260346e4f9edde4f2ae5a362389f44c8"
    ),
    "allocation_audit_digest_sha256": (
        "023b5b1c20f87a84eb63ac43b5ebe47cb3a62e05adbb31a0d46d6add5ddee66b"
    ),
    "result_digest_sha256": "5b34510714ab89816f2f1e1830f2b4fa4d91c678b0401821aa11baff31da4da5",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "3bbe3ec02e7cba2b11a1366a1a870cf68ccde865f2e1551bc99006a0944192bd"
    ),
    "parent_center_product_interval_digest_sha256": (
        "42c093253eb97338e39c877c32559c45d2022fa565930b410fc4a67dcfa2e337"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "24e97be7c31849f25214711cd101dbb9f9dd2f060600d7c057beb98f4bcdeab0"
    ),
    "allocation_classification_record_digest_sha256": (
        "4998d8e6dc452f53f25b80ef8484d0326e02e20de22550891ae2ff924375fa95"
    ),
}


@pytest.fixture(scope="module")
def q011cw_study() -> dict[str, Any]:
    return q011cw.run_q011cw_study()


@pytest.fixture(scope="module")
def q011cw_cycle(q011cw_study: dict[str, Any]) -> dict[str, Any]:
    return q011cw_study["cycle"]


def test_q011cw_seals_q011cv_and_all_prior_inputs(
    q011cw_cycle: dict[str, Any],
) -> None:
    sealed = q011cw_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 79
    assert sealed["direct_digest_count"] == 368
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cv"]["digests"]) == q011cw.Q011CV_DIGESTS
    assert sealed["q011cv"]["artifact_sha256"] == q011cw.Q011CV_ARTIFACT_SHA256
    assert sealed["q011cv"]["runner_sha256"] == q011cw.Q011CV_RUNNER_SHA256
    assert sealed["q011cv"]["resolved_witness_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_NINE_RESOLUTION_DIGEST
    )


def test_q011cw_selects_exactly_flatten_ordinal_ten(
    q011cw_cycle: dict[str, Any],
) -> None:
    fixed = q011cw_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["eleventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 10
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(10))
    assert selection["ordinal_four_resolution_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    assert selection["ordinal_five_resolution_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )
    assert selection["ordinal_six_resolution_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
    )
    assert selection["ordinal_seven_resolution_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_SEVEN_RESOLUTION_DIGEST
    )
    assert selection["ordinal_eight_resolution_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_EIGHT_RESOLUTION_DIGEST
    )
    assert selection["ordinal_nine_resolution_digest_sha256"] == (
        q011cw.EXPECTED_ORDINAL_NINE_RESOLUTION_DIGEST
    )
    parent = selection["eleventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 1_531
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011cw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011cw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011cw_reconstructs_registered_partition_and_inventory(
    q011cw_cycle: dict[str, Any],
) -> None:
    fixed = q011cw_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011cw.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == (q011cw.EXPECTED_IDENTIFIER_ORDER)
    assert fixed["full_allocation_count"] == 27_216
    assert fixed["full_allocation_digest_sha256"] == q011cw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_531
    assert fixed["compatible_allocation_digest_sha256"] == (q011cw.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 27_108
    assert fixed["parent_witness_compatible_index"] == 1_530
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011cw_all_exact_intervals_are_parent_identical(
    q011cw_cycle: dict[str, Any],
) -> None:
    partition = q011cw_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011cw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011cw.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cw_records_interval_inert_persistence(
    q011cw_cycle: dict[str, Any],
) -> None:
    assert q011cw_cycle["study_validity"] == "passed"
    assert q011cw_cycle["failed_validity_order"] == []
    assert q011cw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cw_cycle["diagnostic_gates"].values())
    assert q011cw_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cw_cycle["diagnostic_classification"] == q011cw.INERT_CLASSIFICATION
    assert q011cw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cw_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_531,
    }
    partition = q011cw_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cw_preserves_boundary_and_reproducible_digests(
    q011cw_cycle: dict[str, Any],
) -> None:
    theorem = q011cw_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_eleventh_q011cb_witness"]
    assert not theorem["eleventh_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 10" in q011cw_cycle["claim_boundary"]
    assert "later 44789 Q011cb refined signatures" in q011cw_cycle["claim_boundary"]
    json.dumps(q011cw_cycle, allow_nan=False)
    assert {
        name: q011cw_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011cw_cycle["result_digest_sha256"] == (
        q011cw.q011b._canonical_json_sha256(q011cw._result_digest_sections(q011cw_cycle))
    )
    assert q011cw._protocol_globals_are_restored()


def test_q011cw_study_metadata_and_optional_artifact_are_scoped(
    q011cw_study: dict[str, Any],
) -> None:
    assert q011cw_study["schema_version"] == 1
    assert q011cw_study["source"] == source_metadata()
    assert q011cw_study["study_gate"] == "passed"
    assert q011cw_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011cw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_531
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 10
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cw_study, allow_nan=False)

    runner_path = Path(q011cw.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / ("q011cw_degree34_eleventh_individual_partition_audit.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cw.q011b._canonical_json_sha256(q011cw._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
