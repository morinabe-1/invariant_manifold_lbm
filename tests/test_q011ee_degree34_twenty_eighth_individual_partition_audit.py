from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ee_degree34_twenty_eighth_individual_partition_audit as q011ee
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
        "284d82756fe8af2bbd6fd182127cfb6953d17d2d879da5b5cdf908c8b6b97ba3"
    ),
    "parent_center_product_interval_digest_sha256": (
        "f76b3263f1999ffa9ebf5fe859592e8dad10da1c6a93ea5b14e72e2467516565"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "b84bb644df4e89c7297c974279f7439cf943c2897c59d24e1fe555e1de8b8a71"
    ),
    "allocation_classification_record_digest_sha256": "",
}


@pytest.fixture(scope="module")
def q011ee_study() -> dict[str, Any]:
    return q011ee.run_q011ee_study()


@pytest.fixture(scope="module")
def q011ee_cycle(q011ee_study: dict[str, Any]) -> dict[str, Any]:
    return q011ee_study["cycle"]


def test_q011ee_seals_q011ed_and_all_prior_inputs(
    q011ee_cycle: dict[str, Any],
) -> None:
    sealed = q011ee_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 113
    assert sealed["direct_digest_count"] == 521
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ed"]["digests"]) == q011ee.Q011ED_DIGESTS
    assert sealed["q011ed"]["artifact_sha256"] == q011ee.Q011ED_ARTIFACT_SHA256
    assert sealed["q011ed"]["runner_sha256"] == q011ee.Q011ED_RUNNER_SHA256
    assert sealed["q011ed"]["resolved_witness_digest_sha256"] == (
        q011ee.EXPECTED_ORDINAL_TWENTY_SIX_RESOLUTION_DIGEST
    )


def test_q011ee_selects_exactly_flatten_ordinal_twenty_seven(
    q011ee_cycle: dict[str, Any],
) -> None:
    fixed = q011ee_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 27
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(27))
    assert selection["ordinal_twenty_six_resolution_digest_sha256"] == (
        q011ee.EXPECTED_ORDINAL_TWENTY_SIX_RESOLUTION_DIGEST
    )
    parent = selection["twenty_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 2_646
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ee.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ee.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ee.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ee_reconstructs_registered_partition_and_inventory(
    q011ee_cycle: dict[str, Any],
) -> None:
    fixed = q011ee_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ee.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ee.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 47_040
    assert fixed["full_allocation_digest_sha256"] == q011ee.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_646
    assert fixed["compatible_allocation_digest_sha256"] == (q011ee.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 46_920
    assert fixed["parent_witness_compatible_index"] == 2_645
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ee_all_exact_intervals_are_parent_identical(
    q011ee_cycle: dict[str, Any],
) -> None:
    partition = q011ee_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_646
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_646
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_646))
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
        assert record["intersection_width_hex"] == (q011ee.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011ee.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011ee partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ee_records_interval_inert_persistence(
    q011ee_cycle: dict[str, Any],
) -> None:
    assert q011ee_cycle["study_validity"] == "passed"
    assert q011ee_cycle["failed_validity_order"] == []
    assert q011ee_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ee_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ee_cycle["diagnostic_gates"].values())
    assert q011ee_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ee_cycle["diagnostic_classification"] == q011ee.INERT_CLASSIFICATION
    assert q011ee_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ee_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_646,
    }
    partition = q011ee_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ee_preserves_boundary_and_reproducible_digests(
    q011ee_cycle: dict[str, Any],
) -> None:
    theorem = q011ee_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_eighth_q011cb_witness"]
    assert not theorem["twenty_eighth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011ed_ordinal_twenty_six_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 27" in q011ee_cycle["claim_boundary"]
    assert "later 44772 Q011cb refined signatures" in q011ee_cycle["claim_boundary"]
    assert "Q011ef" in q011ee_cycle["next_change"]
    json.dumps(q011ee_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ee section digests have not been sealed yet")
    assert {name: q011ee_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ee_cycle["result_digest_sha256"] == (
        q011ee.q011b._canonical_json_sha256(q011ee._result_digest_sections(q011ee_cycle))
    )
    assert q011ee._protocol_globals_are_restored()


def test_q011ee_study_metadata_and_optional_artifact_are_scoped(
    q011ee_study: dict[str, Any],
) -> None:
    assert q011ee_study["schema_version"] == 1
    assert q011ee_study["source"] == source_metadata()
    assert q011ee_study["study_gate"] == "passed"
    assert q011ee_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ee_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_646
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ee_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 27
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ee_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ee runner hash has not been sealed yet")
    runner_path = Path(q011ee.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ee_degree34_twenty_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ee artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ee.q011b._canonical_json_sha256(q011ee._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
