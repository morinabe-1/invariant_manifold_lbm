from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011eo_degree34_thirty_third_individual_partition_audit as q011eo
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "",
    "partition_input_digest_sha256": "",
    "allocation_audit_digest_sha256": "",
    "result_digest_sha256": "",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "0ac45c95ff6acee7359ab7f24fa5bdc7664aee375ab2117c2bd9d0c95ce7d9dd"
    ),
    "parent_center_product_interval_digest_sha256": (
        "4750cc56979e965720a510b97370da24f17f83044fd4a6f3477aac34982ce6e1"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "b413e782cbde5e4f8e4ecf6d2f20544590b1e4277de6dd6c7483214c2ee4e195"
    ),
    "allocation_classification_record_digest_sha256": "",
}


@pytest.fixture(scope="module")
def q011eo_study() -> dict[str, Any]:
    return q011eo.run_q011eo_study()


@pytest.fixture(scope="module")
def q011eo_cycle(q011eo_study: dict[str, Any]) -> dict[str, Any]:
    return q011eo_study["cycle"]


def test_q011eo_seals_q011en_and_all_prior_inputs(
    q011eo_cycle: dict[str, Any],
) -> None:
    sealed = q011eo_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 123
    assert sealed["direct_digest_count"] == 566
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011en"]["digests"]) == q011eo.Q011EN_DIGESTS
    assert sealed["q011en"]["artifact_sha256"] == q011eo.Q011EN_ARTIFACT_SHA256
    assert sealed["q011en"]["runner_sha256"] == q011eo.Q011EN_RUNNER_SHA256
    assert sealed["q011en"]["resolved_witness_digest_sha256"] == (
        q011eo.EXPECTED_ORDINAL_THIRTY_ONE_RESOLUTION_DIGEST
    )


def test_q011eo_selects_exactly_flatten_ordinal_thirty_two(
    q011eo_cycle: dict[str, Any],
) -> None:
    fixed = q011eo_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 32
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(32))
    assert selection["ordinal_thirty_one_resolution_digest_sha256"] == (
        q011eo.EXPECTED_ORDINAL_THIRTY_ONE_RESOLUTION_DIGEST
    )
    parent = selection["thirty_third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_136
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011eo.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011eo.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011eo.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011eo_reconstructs_registered_partition_and_inventory(
    q011eo_cycle: dict[str, Any],
) -> None:
    fixed = q011eo_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [0, 7],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011eo.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011eo.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 20_160
    assert fixed["full_allocation_digest_sha256"] == q011eo.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_136
    assert fixed["compatible_allocation_digest_sha256"] == (q011eo.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 20_112
    assert fixed["parent_witness_compatible_index"] == 1_135
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011eo_all_exact_intervals_are_parent_identical(
    q011eo_cycle: dict[str, Any],
) -> None:
    partition = q011eo_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_136
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_136
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_136))
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
        assert record["intersection_width_hex"] == (q011eo.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011eo.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011eo partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011eo_records_interval_inert_persistence(
    q011eo_cycle: dict[str, Any],
) -> None:
    assert q011eo_cycle["study_validity"] == "passed"
    assert q011eo_cycle["failed_validity_order"] == []
    assert q011eo_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011eo_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011eo_cycle["diagnostic_gates"].values())
    assert q011eo_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011eo_cycle["diagnostic_classification"] == q011eo.INERT_CLASSIFICATION
    assert q011eo_cycle["scientific_outcome"] == "not_evaluated"
    assert q011eo_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_136,
    }
    partition = q011eo_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011eo_preserves_boundary_and_reproducible_digests(
    q011eo_cycle: dict[str, Any],
) -> None:
    theorem = q011eo_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_thirty_third_q011cb_witness"]
    assert not theorem["thirty_third_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 32" in q011eo_cycle["claim_boundary"]
    assert "later 44767 Q011cb refined signatures" in q011eo_cycle["claim_boundary"]
    assert "Q011ep" in q011eo_cycle["next_change"]
    json.dumps(q011eo_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011eo section digests have not been sealed yet")
    assert {name: q011eo_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011eo_cycle["result_digest_sha256"] == (
        q011eo.q011b._canonical_json_sha256(q011eo._result_digest_sections(q011eo_cycle))
    )
    assert q011eo._protocol_globals_are_restored()


def test_q011eo_study_metadata_and_optional_artifact_are_scoped(
    q011eo_study: dict[str, Any],
) -> None:
    assert q011eo_study["schema_version"] == 1
    assert q011eo_study["source"] == source_metadata()
    assert q011eo_study["study_gate"] == "passed"
    assert q011eo_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011eo_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_136
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011eo_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 32
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011eo_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011eo runner hash has not been sealed yet")
    runner_path = Path(q011eo.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011eo_degree34_thirty_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011eo artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011eo.q011b._canonical_json_sha256(q011eo._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
