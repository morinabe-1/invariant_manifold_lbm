from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011co_degree34_seventh_individual_partition_audit as q011co
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a4de9650b41b0eb9668abd52cd87fe4fe1ffd7ef361a4667ac1c0210bc053f71"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "46acbd33138d694c655bba86056e096def9fcd0585a958051440a9393b0bb201"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "115fe27f40ab005b028229b5e17462bcd8e4813ad9afc0fe7568ea5382840ef2",
    "partition_input_digest_sha256": (
        "02bab6d3f596dfe6ad3ca14cc8cce593c19f8348dcc91a0614bf6479335b32f7"
    ),
    "allocation_audit_digest_sha256": (
        "c5f9e0feeb15bc7518318a5b947c72f36b712e952c175c12026eb987eb97ec9b"
    ),
    "result_digest_sha256": "8a21404d10845e139ca457fabaa96df347ea4c2a5cb66bf72d4fcafe66071690",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "3b1386389a353cbae907c5a3de1d33732c3637e6fa82efe520f3361dad6d6be3"
    ),
    "parent_center_product_interval_digest_sha256": (
        "b0b9beea2008fd5e91eb84f4f0779122fccdae44407f760f0c3eef7cd798f520"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "c9dab9030cbaa97435aefce1c471278b5d382fc2b304c8c7450af6f41ee4c156"
    ),
    "allocation_classification_record_digest_sha256": (
        "f88afc7a2ae3f395ab86e294cd5add020004ff753c6d4385f9a8d1e0186bd0b7"
    ),
}


@pytest.fixture(scope="module")
def q011co_study() -> dict[str, Any]:
    return q011co.run_q011co_study()


@pytest.fixture(scope="module")
def q011co_cycle(q011co_study: dict[str, Any]) -> dict[str, Any]:
    return q011co_study["cycle"]


def test_q011co_seals_q011cn_and_all_prior_inputs(
    q011co_cycle: dict[str, Any],
) -> None:
    sealed = q011co_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 71
    assert sealed["direct_digest_count"] == 332
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cn"]["digests"]) == q011co.Q011CN_DIGESTS
    assert sealed["q011cn"]["artifact_sha256"] == q011co.Q011CN_ARTIFACT_SHA256
    assert sealed["q011cn"]["runner_sha256"] == q011co.Q011CN_RUNNER_SHA256
    assert sealed["q011cn"]["resolved_witness_digest_sha256"] == (
        q011co.EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )


def test_q011co_selects_exactly_flatten_ordinal_six(
    q011co_cycle: dict[str, Any],
) -> None:
    fixed = q011co_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 6
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2, 3, 4, 5]
    assert selection["ordinal_four_resolution_digest_sha256"] == (
        q011co.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    assert selection["ordinal_five_resolution_digest_sha256"] == (
        q011co.EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 665
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011co.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011co.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011co.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011co_reconstructs_registered_partition_and_inventory(
    q011co_cycle: dict[str, Any],
) -> None:
    fixed = q011co_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011co.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == (q011co.EXPECTED_IDENTIFIER_ORDER)
    assert fixed["full_allocation_count"] == 11_760
    assert fixed["full_allocation_digest_sha256"] == q011co.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 665
    assert fixed["compatible_allocation_digest_sha256"] == (q011co.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 11_676
    assert fixed["parent_witness_compatible_index"] == 664
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011co_all_exact_intervals_are_parent_identical(
    q011co_cycle: dict[str, Any],
) -> None:
    partition = q011co_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 665
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 665
    assert [record["compatible_allocation_index"] for record in records] == list(range(665))
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
        assert record["intersection_width_hex"] == (q011co.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011co.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011co_records_interval_inert_persistence(
    q011co_cycle: dict[str, Any],
) -> None:
    assert q011co_cycle["study_validity"] == "passed"
    assert q011co_cycle["failed_validity_order"] == []
    assert q011co_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011co_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011co_cycle["diagnostic_gates"].values())
    assert q011co_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011co_cycle["diagnostic_classification"] == q011co.INERT_CLASSIFICATION
    assert q011co_cycle["scientific_outcome"] == "not_evaluated"
    assert q011co_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 665,
    }
    partition = q011co_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011co_preserves_boundary_and_reproducible_digests(
    q011co_cycle: dict[str, Any],
) -> None:
    theorem = q011co_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_seventh_q011cb_witness"]
    assert not theorem["seventh_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 6" in q011co_cycle["claim_boundary"]
    assert "later 44793 Q011cb refined signatures" in q011co_cycle["claim_boundary"]
    json.dumps(q011co_cycle, allow_nan=False)
    assert {
        name: q011co_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011co_cycle["result_digest_sha256"] == (
        q011co.q011b._canonical_json_sha256(q011co._result_digest_sections(q011co_cycle))
    )
    assert q011co._protocol_globals_are_restored()


def test_q011co_study_metadata_and_optional_artifact_are_scoped(
    q011co_study: dict[str, Any],
) -> None:
    assert q011co_study["schema_version"] == 1
    assert q011co_study["source"] == source_metadata()
    assert q011co_study["study_gate"] == "passed"
    assert q011co_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011co_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 665
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011co_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 6
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011co_study, allow_nan=False)

    runner_path = Path(q011co.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / ("q011co_degree34_seventh_individual_partition_audit.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011co artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011co.q011b._canonical_json_sha256(q011co._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
