from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011de_degree34_fifteenth_individual_partition_audit as q011de
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "5ed9580cbea7afc77734eb84a31a4d6c98545e63565c15b8fcb7ac3ad3c3e43a"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "964def5891d20989a78b3c0c150f6eb8588457d552c1906ec3fc7a20723387be"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "0664c154666899765cf27c1d3a349ee7a2fd9cffa9ea03eb985443036f92bcd9",
    "partition_input_digest_sha256": (
        "a3dd6b86e42e0db6e62d4633704c01d48d6deeae4be5c4b76cc20d32a6f3cbc3"
    ),
    "allocation_audit_digest_sha256": (
        "56e9c71c45d03f63e4428215cc9c04eece5cbdb1318d4de41ad4d5cfb21b17a2"
    ),
    "result_digest_sha256": "154a2e5892d8b95d123819242b3ef7706f8d54c94a367f39ec91bb69654078e4",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "56a515ad3e4fcd505da70b574fa8fa2f37b3db2136a04509a6d1476d63444aad"
    ),
    "parent_center_product_interval_digest_sha256": (
        "8f93d8a9f7daed0fdcd5a90a1e901eddbca903060d21eccd2fb53699f634f7d9"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "ea01781e7b01c0bc1592b3141c532cdc8703ed7c64202699fd87809880b6cc2c"
    ),
    "allocation_classification_record_digest_sha256": (
        "393fe41a05d000900a2fc9612491fda3027bc9ac76406fc259f3311d35249ce7"
    ),
}


@pytest.fixture(scope="module")
def q011de_study() -> dict[str, Any]:
    return q011de.run_q011de_study()


@pytest.fixture(scope="module")
def q011de_cycle(q011de_study: dict[str, Any]) -> dict[str, Any]:
    return q011de_study["cycle"]


def test_q011de_seals_q011dd_and_all_prior_inputs(
    q011de_cycle: dict[str, Any],
) -> None:
    sealed = q011de_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 87
    assert sealed["direct_digest_count"] == 404
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dd"]["digests"]) == q011de.Q011DD_DIGESTS
    assert sealed["q011dd"]["artifact_sha256"] == q011de.Q011DD_ARTIFACT_SHA256
    assert sealed["q011dd"]["runner_sha256"] == q011de.Q011DD_RUNNER_SHA256
    assert sealed["q011dd"]["resolved_witness_digest_sha256"] == (
        q011de.EXPECTED_ORDINAL_THIRTEEN_RESOLUTION_DIGEST
    )


def test_q011de_selects_exactly_flatten_ordinal_fourteen(
    q011de_cycle: dict[str, Any],
) -> None:
    fixed = q011de_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["fifteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 14
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(14))
    assert selection["ordinal_thirteen_resolution_digest_sha256"] == (
        q011de.EXPECTED_ORDINAL_THIRTEEN_RESOLUTION_DIGEST
    )
    parent = selection["fifteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_194
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011de.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011de.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011de.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011de_reconstructs_registered_partition_and_inventory(
    q011de_cycle: dict[str, Any],
) -> None:
    fixed = q011de_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011de.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011de.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 21_168
    assert fixed["full_allocation_digest_sha256"] == q011de.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_194
    assert fixed["compatible_allocation_digest_sha256"] == q011de.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 21_084
    assert fixed["parent_witness_compatible_index"] == 1_193
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011de_all_exact_intervals_are_parent_identical(
    q011de_cycle: dict[str, Any],
) -> None:
    partition = q011de_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_194
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_194
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_194))
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
        assert record["intersection_width_hex"] == (q011de.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011de.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011de_records_interval_inert_persistence(
    q011de_cycle: dict[str, Any],
) -> None:
    assert q011de_cycle["study_validity"] == "passed"
    assert q011de_cycle["failed_validity_order"] == []
    assert q011de_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011de_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011de_cycle["diagnostic_gates"].values())
    assert q011de_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011de_cycle["diagnostic_classification"] == q011de.INERT_CLASSIFICATION
    assert q011de_cycle["scientific_outcome"] == "not_evaluated"
    assert q011de_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_194,
    }
    partition = q011de_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011de_preserves_boundary_and_reproducible_digests(
    q011de_cycle: dict[str, Any],
) -> None:
    theorem = q011de_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_fifteenth_q011cb_witness"]
    assert not theorem["fifteenth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011dd_ordinal_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011dc_ordinal_thirteen_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 14" in q011de_cycle["claim_boundary"]
    assert "later 44785 Q011cb refined signatures" in q011de_cycle["claim_boundary"]
    assert "Q011df" in q011de_cycle["next_change"]
    json.dumps(q011de_cycle, allow_nan=False)
    assert {name: q011de_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011de_cycle["result_digest_sha256"] == (
        q011de.q011b._canonical_json_sha256(q011de._result_digest_sections(q011de_cycle))
    )
    assert q011de._protocol_globals_are_restored()


def test_q011de_study_metadata_and_optional_artifact_are_scoped(
    q011de_study: dict[str, Any],
) -> None:
    assert q011de_study["schema_version"] == 1
    assert q011de_study["source"] == source_metadata()
    assert q011de_study["study_gate"] == "passed"
    assert q011de_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011de_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_194
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011de_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 14
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011de_study, allow_nan=False)

    runner_path = Path(q011de.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011de_degree34_fifteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011de artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011de.q011b._canonical_json_sha256(q011de._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
