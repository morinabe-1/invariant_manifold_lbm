from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dc_degree34_fourteenth_individual_partition_audit as q011dc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "c24467858a54434fc54c863acb32a2d043ab2c701ee8457ba18df532f4786102"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "8abc214ada1d1dc3d3edf54b0ae16409366d7266ce8effde6049599e7db61450",
    "partition_input_digest_sha256": (
        "d107dd6a3b0b3d4abee3737c9e640ff915e25f0d3b2f8efd530d689c691c8594"
    ),
    "allocation_audit_digest_sha256": (
        "b5b5ba2b3e2d19ae316cb4177d08f565b4e8287ebda227474e132c0400bdf5fc"
    ),
    "result_digest_sha256": "3fb836e8fe50670ab0ce285ffdfb2eae537a1d0a4b291f36e2f97fa5b519bb9e",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "047226e587d048e8e254671789102b5e3200aa9ea5283a6e871d90feaf299a2f"
    ),
    "parent_center_product_interval_digest_sha256": (
        "8e9ccd49dd40c87a30ebb45f44031b8fcacbfc4b93b6d0e90470bf0ac369b5b8"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "780e6f02fa8fc6e4d49488391995e7f7e66b3944068eb34db0f10a680f5e703c"
    ),
    "allocation_classification_record_digest_sha256": (
        "8253f54f0bf026832b2afa3d7ce31b4a9645cc7aa44d0f88db8b95d78ccf3081"
    ),
}


@pytest.fixture(scope="module")
def q011dc_study() -> dict[str, Any]:
    return q011dc.run_q011dc_study()


@pytest.fixture(scope="module")
def q011dc_cycle(q011dc_study: dict[str, Any]) -> dict[str, Any]:
    return q011dc_study["cycle"]


def test_q011dc_seals_q011db_and_all_prior_inputs(
    q011dc_cycle: dict[str, Any],
) -> None:
    sealed = q011dc_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 85
    assert sealed["direct_digest_count"] == 395
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011db"]["digests"]) == q011dc.Q011DB_DIGESTS
    assert sealed["q011db"]["artifact_sha256"] == q011dc.Q011DB_ARTIFACT_SHA256
    assert sealed["q011db"]["runner_sha256"] == q011dc.Q011DB_RUNNER_SHA256
    assert sealed["q011db"]["resolved_witness_digest_sha256"] == (
        q011dc.EXPECTED_ORDINAL_TWELVE_RESOLUTION_DIGEST
    )


def test_q011dc_selects_exactly_flatten_ordinal_thirteen(
    q011dc_cycle: dict[str, Any],
) -> None:
    fixed = q011dc_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["fourteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 13
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(13))
    assert selection["ordinal_twelve_resolution_digest_sha256"] == (
        q011dc.EXPECTED_ORDINAL_TWELVE_RESOLUTION_DIGEST
    )
    parent = selection["fourteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 1_531
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dc.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dc.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dc_reconstructs_registered_partition_and_inventory(
    q011dc_cycle: dict[str, Any],
) -> None:
    fixed = q011dc_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dc.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dc.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 27_216
    assert fixed["full_allocation_digest_sha256"] == q011dc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_531
    assert fixed["compatible_allocation_digest_sha256"] == q011dc.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 27_108
    assert fixed["parent_witness_compatible_index"] == 1_530
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dc_all_exact_intervals_are_parent_identical(
    q011dc_cycle: dict[str, Any],
) -> None:
    partition = q011dc_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011dc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dc.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dc_records_interval_inert_persistence(
    q011dc_cycle: dict[str, Any],
) -> None:
    assert q011dc_cycle["study_validity"] == "passed"
    assert q011dc_cycle["failed_validity_order"] == []
    assert q011dc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dc_cycle["diagnostic_gates"].values())
    assert q011dc_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dc_cycle["diagnostic_classification"] == q011dc.INERT_CLASSIFICATION
    assert q011dc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dc_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_531,
    }
    partition = q011dc_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dc_preserves_boundary_and_reproducible_digests(
    q011dc_cycle: dict[str, Any],
) -> None:
    theorem = q011dc_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_fourteenth_q011cb_witness"]
    assert not theorem["fourteenth_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 13" in q011dc_cycle["claim_boundary"]
    assert "later 44786 Q011cb refined signatures" in q011dc_cycle["claim_boundary"]
    assert "Q011dd" in q011dc_cycle["next_change"]
    json.dumps(q011dc_cycle, allow_nan=False)
    assert {name: q011dc_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dc_cycle["result_digest_sha256"] == (
        q011dc.q011b._canonical_json_sha256(q011dc._result_digest_sections(q011dc_cycle))
    )
    assert q011dc._protocol_globals_are_restored()


def test_q011dc_study_metadata_and_optional_artifact_are_scoped(
    q011dc_study: dict[str, Any],
) -> None:
    assert q011dc_study["schema_version"] == 1
    assert q011dc_study["source"] == source_metadata()
    assert q011dc_study["study_gate"] == "passed"
    assert q011dc_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dc_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_531
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 13
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dc_study, allow_nan=False)

    runner_path = Path(q011dc.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dc_degree34_fourteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dc.q011b._canonical_json_sha256(q011dc._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
