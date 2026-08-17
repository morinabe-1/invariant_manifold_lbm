from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cy_degree34_twelfth_individual_partition_audit as q011cy
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "4bb5f856813e30ea56a5c260c3103fdf12ac24bd1fd81bf2fc64de41d9ba2b16"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "7b30b02ebc84df1774ef4e357f9607013aa518063e8e14490fa36cd229dbfae8",
    "partition_input_digest_sha256": (
        "9526fcb859eeb26b688315d9a82e49c4cd18d097e706330e8be96effc190f15a"
    ),
    "allocation_audit_digest_sha256": (
        "075de2aa3118a803af3aa9e9991205f2d07bf52a4155af60554df751ceff4ed0"
    ),
    "result_digest_sha256": "2dabbfd5238f5b1aac2fb40f67be7f1944dfa286e5385f27a4a091f4b2694ed8",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "2620c3859a303a798cc08be27b20a10b6c4628c49f8f278ade9d119d38bff278"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c28de1513f367df3c6aacc2b26813e698dbc533f6830d82426e0a8181bf97654"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "9dbab563a088e4318266e0b9aec14ecdeb883ce6716c2cdc11f139a0aa9e5dbe"
    ),
    "allocation_classification_record_digest_sha256": (
        "b7f9d0b612dc0965d2f61ede6d6f428727f5a82f59325c2d3d1bc21742211585"
    ),
}


@pytest.fixture(scope="module")
def q011cy_study() -> dict[str, Any]:
    return q011cy.run_q011cy_study()


@pytest.fixture(scope="module")
def q011cy_cycle(q011cy_study: dict[str, Any]) -> dict[str, Any]:
    return q011cy_study["cycle"]


def test_q011cy_seals_q011cx_and_all_prior_inputs(
    q011cy_cycle: dict[str, Any],
) -> None:
    sealed = q011cy_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 81
    assert sealed["direct_digest_count"] == 377
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cx"]["digests"]) == q011cy.Q011CX_DIGESTS
    assert sealed["q011cx"]["artifact_sha256"] == q011cy.Q011CX_ARTIFACT_SHA256
    assert sealed["q011cx"]["runner_sha256"] == q011cy.Q011CX_RUNNER_SHA256
    assert sealed["q011cx"]["resolved_witness_digest_sha256"] == (
        q011cy.EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST
    )


def test_q011cy_selects_exactly_flatten_ordinal_eleven(
    q011cy_cycle: dict[str, Any],
) -> None:
    fixed = q011cy_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twelfth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 11
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(11))
    assert selection["ordinal_ten_resolution_digest_sha256"] == (
        q011cy.EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST
    )
    parent = selection["twelfth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 1_699
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011cy.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011cy.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011cy_reconstructs_registered_partition_and_inventory(
    q011cy_cycle: dict[str, Any],
) -> None:
    fixed = q011cy_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011cy.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011cy.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 30_240
    assert fixed["full_allocation_digest_sha256"] == q011cy.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_699
    assert fixed["compatible_allocation_digest_sha256"] == q011cy.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 30_120
    assert fixed["parent_witness_compatible_index"] == 1_698
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011cy_all_exact_intervals_are_parent_identical(
    q011cy_cycle: dict[str, Any],
) -> None:
    partition = q011cy_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_699
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_699
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_699))
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
        assert record["intersection_width_hex"] == q011cy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011cy.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cy_records_interval_inert_persistence(
    q011cy_cycle: dict[str, Any],
) -> None:
    assert q011cy_cycle["study_validity"] == "passed"
    assert q011cy_cycle["failed_validity_order"] == []
    assert q011cy_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cy_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cy_cycle["diagnostic_gates"].values())
    assert q011cy_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cy_cycle["diagnostic_classification"] == q011cy.INERT_CLASSIFICATION
    assert q011cy_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cy_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_699,
    }
    partition = q011cy_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cy_preserves_boundary_and_reproducible_digests(
    q011cy_cycle: dict[str, Any],
) -> None:
    theorem = q011cy_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twelfth_q011cb_witness"]
    assert not theorem["twelfth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cw_ordinal_ten_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 11" in q011cy_cycle["claim_boundary"]
    assert "later 44788 Q011cb refined signatures" in q011cy_cycle["claim_boundary"]
    assert "Q011cz" in q011cy_cycle["next_change"]
    json.dumps(q011cy_cycle, allow_nan=False)
    assert {name: q011cy_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011cy_cycle["result_digest_sha256"] == (
        q011cy.q011b._canonical_json_sha256(q011cy._result_digest_sections(q011cy_cycle))
    )
    assert q011cy._protocol_globals_are_restored()


def test_q011cy_study_metadata_and_optional_artifact_are_scoped(
    q011cy_study: dict[str, Any],
) -> None:
    assert q011cy_study["schema_version"] == 1
    assert q011cy_study["source"] == source_metadata()
    assert q011cy_study["study_gate"] == "passed"
    assert q011cy_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011cy_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_699
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cy_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 11
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cy_study, allow_nan=False)

    runner_path = Path(q011cy.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / "q011cy_degree34_twelfth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cy artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cy.q011b._canonical_json_sha256(q011cy._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
