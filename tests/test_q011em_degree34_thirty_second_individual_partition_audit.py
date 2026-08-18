from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011em_degree34_thirty_second_individual_partition_audit as q011em
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "21f675d85f3b928bd720c22516799c8f6a75d8ccb80c782a12126e3febf4c3c5"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "c8a87811e60f6c126c899ee5c7373c3c5422093f13419d81de0f98aa64f52a03"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "c8f6e37d3b0e3a8e2dfba2af9be34631b796ad62883d756bde5ecaf97a541832",
    "partition_input_digest_sha256": "efe6a7b2d0d56362418054f716383b1f121b27d79542f409da6107696206b430",
    "allocation_audit_digest_sha256": "08d7b475a52452711cfe663bffdce32a023a5ffb218111128ee598fa9ecacc70",
    "result_digest_sha256": "f1b6d56b365b412abf430a9b393047bcf57894dc0efd0a98a4c0625551dd2b51",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "30d3dd806afd7b3080f38db816a73b2b8419c7573be8270e6213befa163163b6"
    ),
    "parent_center_product_interval_digest_sha256": (
        "39dac6d825e5ff76e023dd4d12461ab76bbdc300183ee0aae171f992a5ce91f6"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "8ab1ad1fb5db5b0d5decd3d035fce8141ec1b8fd7693fe3cf3149c889ef6b89c"
    ),
    "allocation_classification_record_digest_sha256": (
        "02d297a84daa195a09453e82deee04e75cb7ae40ba9fe14f3d4e6552f0977512"
    ),
}


@pytest.fixture(scope="module")
def q011em_study() -> dict[str, Any]:
    return q011em.run_q011em_study()


@pytest.fixture(scope="module")
def q011em_cycle(q011em_study: dict[str, Any]) -> dict[str, Any]:
    return q011em_study["cycle"]


def test_q011em_seals_q011el_and_all_prior_inputs(
    q011em_cycle: dict[str, Any],
) -> None:
    sealed = q011em_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 121
    assert sealed["direct_digest_count"] == 557
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011el"]["digests"]) == q011em.Q011EL_DIGESTS
    assert sealed["q011el"]["artifact_sha256"] == q011em.Q011EL_ARTIFACT_SHA256
    assert sealed["q011el"]["runner_sha256"] == q011em.Q011EL_RUNNER_SHA256
    assert sealed["q011el"]["resolved_witness_digest_sha256"] == (
        q011em.EXPECTED_ORDINAL_THIRTY_RESOLUTION_DIGEST
    )


def test_q011em_selects_exactly_flatten_ordinal_thirty_one(
    q011em_cycle: dict[str, Any],
) -> None:
    fixed = q011em_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 31
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(31))
    assert selection["ordinal_thirty_resolution_digest_sha256"] == (
        q011em.EXPECTED_ORDINAL_THIRTY_RESOLUTION_DIGEST
    )
    parent = selection["thirty_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 1_061
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011em.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011em.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011em.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011em_reconstructs_registered_partition_and_inventory(
    q011em_cycle: dict[str, Any],
) -> None:
    fixed = q011em_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011em.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011em.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 18_816
    assert fixed["full_allocation_digest_sha256"] == q011em.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_061
    assert fixed["compatible_allocation_digest_sha256"] == (q011em.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 18_768
    assert fixed["parent_witness_compatible_index"] == 1_060
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011em_all_exact_intervals_are_parent_identical(
    q011em_cycle: dict[str, Any],
) -> None:
    partition = q011em_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_061
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_061
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_061))
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
        assert record["intersection_width_hex"] == (q011em.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011em.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011em partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011em_records_interval_inert_persistence(
    q011em_cycle: dict[str, Any],
) -> None:
    assert q011em_cycle["study_validity"] == "passed"
    assert q011em_cycle["failed_validity_order"] == []
    assert q011em_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011em_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011em_cycle["diagnostic_gates"].values())
    assert q011em_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011em_cycle["diagnostic_classification"] == q011em.INERT_CLASSIFICATION
    assert q011em_cycle["scientific_outcome"] == "not_evaluated"
    assert q011em_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_061,
    }
    partition = q011em_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011em_preserves_boundary_and_reproducible_digests(
    q011em_cycle: dict[str, Any],
) -> None:
    theorem = q011em_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_thirty_second_q011cb_witness"]
    assert not theorem["thirty_second_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011el_ordinal_thirty_phase_resolution_is_preserved"]
    assert theorem["q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ej_ordinal_twenty_nine_phase_resolution_is_preserved"]
    assert theorem["q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eh_ordinal_twenty_eight_phase_resolution_is_preserved"]
    assert theorem["q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eb_ordinal_twenty_five_phase_resolution_is_preserved"]
    assert theorem["q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dz_ordinal_twenty_four_phase_resolution_is_preserved"]
    assert theorem["q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 31" in q011em_cycle["claim_boundary"]
    assert "later 44768 Q011cb refined signatures" in q011em_cycle["claim_boundary"]
    assert "Q011en" in q011em_cycle["next_change"]
    json.dumps(q011em_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011em section digests have not been sealed yet")
    assert {name: q011em_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011em_cycle["result_digest_sha256"] == (
        q011em.q011b._canonical_json_sha256(q011em._result_digest_sections(q011em_cycle))
    )
    assert q011em._protocol_globals_are_restored()


def test_q011em_study_metadata_and_optional_artifact_are_scoped(
    q011em_study: dict[str, Any],
) -> None:
    assert q011em_study["schema_version"] == 1
    assert q011em_study["source"] == source_metadata()
    assert q011em_study["study_gate"] == "passed"
    assert q011em_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011em_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_061
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011em_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 31
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011em_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011em runner hash has not been sealed yet")
    runner_path = Path(q011em.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011em_degree34_thirty_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011em artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011em.q011b._canonical_json_sha256(q011em._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
