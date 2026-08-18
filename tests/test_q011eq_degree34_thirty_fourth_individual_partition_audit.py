from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011eq_degree34_thirty_fourth_individual_partition_audit as q011eq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "95854f9450577db3104e491ed40df940c2474e2bde96a87f6f8c92c3cd7b6fa4"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8e3cd9dd82d4f437be1a27247395e9cb8c79ab582215ff40386534e9b1c07d15"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "175f2cdf23caaf13ddcf01f9c0b49dee7188f73d824960625836d7c121cf4ea8",
    "partition_input_digest_sha256": "03af0604db08ebc10653064ccf97fd9312d68b619509736f2313e4b1e942cfd1",
    "allocation_audit_digest_sha256": "cdf2f796346166e9a05869cc83439c666c5f206b45c9106baf2426468a79a482",
    "result_digest_sha256": "1f0bf41d4d9f32cbf6b1306bebc811d1297266e4595f95060a77c9f262cb4f88",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "fdfdccffc0444550486f630a4423822f10fc2d592bc1aacb1d9900ae7da4afea"
    ),
    "parent_center_product_interval_digest_sha256": (
        "38c981b15155ecc849c0012f537989783596b5d453706210a32307069b31d7f0"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "d7d55bcc157c0158020f378468b753343c1c8cbf6c40f268ed903ba0f8a3b4a9"
    ),
    "allocation_classification_record_digest_sha256": (
        "0dc620408d34946749e70e9c42142a66f6e0514323190840a17286cc4df36cd4"
    ),
}


@pytest.fixture(scope="module")
def q011eq_study() -> dict[str, Any]:
    return q011eq.run_q011eq_study()


@pytest.fixture(scope="module")
def q011eq_cycle(q011eq_study: dict[str, Any]) -> dict[str, Any]:
    return q011eq_study["cycle"]


def test_q011eq_seals_q011ep_and_all_prior_inputs(
    q011eq_cycle: dict[str, Any],
) -> None:
    sealed = q011eq_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 125
    assert sealed["direct_digest_count"] == 575
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ep"]["digests"]) == q011eq.Q011EP_DIGESTS
    assert sealed["q011ep"]["artifact_sha256"] == q011eq.Q011EP_ARTIFACT_SHA256
    assert sealed["q011ep"]["runner_sha256"] == q011eq.Q011EP_RUNNER_SHA256
    assert sealed["q011ep"]["resolved_witness_digest_sha256"] == (
        q011eq.EXPECTED_ORDINAL_THIRTY_TWO_RESOLUTION_DIGEST
    )


def test_q011eq_selects_exactly_flatten_ordinal_thirty_three(
    q011eq_cycle: dict[str, Any],
) -> None:
    fixed = q011eq_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 33
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(33))
    assert selection["ordinal_thirty_two_resolution_digest_sha256"] == (
        q011eq.EXPECTED_ORDINAL_THIRTY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["thirty_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 1_986
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011eq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011eq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011eq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011eq_reconstructs_registered_partition_and_inventory(
    q011eq_cycle: dict[str, Any],
) -> None:
    fixed = q011eq_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [1, 6],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011eq.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011eq.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 35_280
    assert fixed["full_allocation_digest_sha256"] == q011eq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_986
    assert fixed["compatible_allocation_digest_sha256"] == (q011eq.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 35_196
    assert fixed["parent_witness_compatible_index"] == 1_985
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011eq_all_exact_intervals_are_parent_identical(
    q011eq_cycle: dict[str, Any],
) -> None:
    partition = q011eq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_986
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_986
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_986))
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
        assert record["intersection_width_hex"] == (q011eq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011eq.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011eq partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011eq_records_interval_inert_persistence(
    q011eq_cycle: dict[str, Any],
) -> None:
    assert q011eq_cycle["study_validity"] == "passed"
    assert q011eq_cycle["failed_validity_order"] == []
    assert q011eq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011eq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011eq_cycle["diagnostic_gates"].values())
    assert q011eq_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011eq_cycle["diagnostic_classification"] == q011eq.INERT_CLASSIFICATION
    assert q011eq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011eq_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_986,
    }
    partition = q011eq_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011eq_preserves_boundary_and_reproducible_digests(
    q011eq_cycle: dict[str, Any],
) -> None:
    theorem = q011eq_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_thirty_fourth_q011cb_witness"]
    assert not theorem["thirty_fourth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011ep_ordinal_thirty_two_phase_resolution_is_preserved"]
    assert theorem["q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011en_ordinal_thirty_one_phase_resolution_is_preserved"]
    assert theorem["q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 33" in q011eq_cycle["claim_boundary"]
    assert "later 44766 Q011cb refined signatures" in q011eq_cycle["claim_boundary"]
    assert "Q011er" in q011eq_cycle["next_change"]
    json.dumps(q011eq_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011eq section digests have not been sealed yet")
    assert {name: q011eq_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011eq_cycle["result_digest_sha256"] == (
        q011eq.q011b._canonical_json_sha256(q011eq._result_digest_sections(q011eq_cycle))
    )
    assert q011eq._protocol_globals_are_restored()


def test_q011eq_study_metadata_and_optional_artifact_are_scoped(
    q011eq_study: dict[str, Any],
) -> None:
    assert q011eq_study["schema_version"] == 1
    assert q011eq_study["source"] == source_metadata()
    assert q011eq_study["study_gate"] == "passed"
    assert q011eq_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011eq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_986
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011eq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 33
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011eq_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011eq runner hash has not been sealed yet")
    runner_path = Path(q011eq.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011eq_degree34_thirty_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011eq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011eq.q011b._canonical_json_sha256(q011eq._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
