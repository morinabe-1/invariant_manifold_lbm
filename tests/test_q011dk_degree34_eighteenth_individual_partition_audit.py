from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dk_degree34_eighteenth_individual_partition_audit as q011dk
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "e1a7332ad528bb43d23ffd68b5ca90cb4531f324694dad1273f963be3a7d0ac9"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "1897ed9e410c543f2671b75828b93f6595c956de6feb02a9634e1c04fdb518b7",
    "partition_input_digest_sha256": (
        "84ba9a3a9654315624612c8519547cda36f6cc1ac1c7f56c5baaf18a13f266d4"
    ),
    "allocation_audit_digest_sha256": (
        "ef85bb1946cc61bc3dd3aea6cd5fc78c77dd641bcadfe44f05b2e83b915660e6"
    ),
    "result_digest_sha256": "4c5e3074a13bc2e1af21e6e9e3f31c2db7b57d32557d2283cdf0c01177ab13bb",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "56114131ff489ebeab5f5c8837204ef3e752c666f82586139f04c8314b460423"
    ),
    "parent_center_product_interval_digest_sha256": (
        "ce2d1bd31abc4f74e5c5ad65c53bb1b912c8705712be48dcf0c496953afd663b"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "bcf452a6cf19089bb6e6a5060216a7301eb423d5a495148af74ea930a2ea9bea"
    ),
    "allocation_classification_record_digest_sha256": (
        "d13ab89231e4fd3665c531f640be2e8c03b5e0a5c9d04cba7bfa5395f24cd94b"
    ),
}


@pytest.fixture(scope="module")
def q011dk_study() -> dict[str, Any]:
    return q011dk.run_q011dk_study()


@pytest.fixture(scope="module")
def q011dk_cycle(q011dk_study: dict[str, Any]) -> dict[str, Any]:
    return q011dk_study["cycle"]


def test_q011dk_seals_q011dj_and_all_prior_inputs(
    q011dk_cycle: dict[str, Any],
) -> None:
    sealed = q011dk_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 93
    assert sealed["direct_digest_count"] == 431
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dj"]["digests"]) == q011dk.Q011DJ_DIGESTS
    assert sealed["q011dj"]["artifact_sha256"] == q011dk.Q011DJ_ARTIFACT_SHA256
    assert sealed["q011dj"]["runner_sha256"] == q011dk.Q011DJ_RUNNER_SHA256
    assert sealed["q011dj"]["resolved_witness_digest_sha256"] == (
        q011dk.EXPECTED_ORDINAL_SIXTEEN_RESOLUTION_DIGEST
    )


def test_q011dk_selects_exactly_flatten_ordinal_seventeen(
    q011dk_cycle: dict[str, Any],
) -> None:
    fixed = q011dk_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["eighteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 17
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(17))
    assert selection["ordinal_sixteen_resolution_digest_sha256"] == (
        q011dk.EXPECTED_ORDINAL_SIXTEEN_RESOLUTION_DIGEST
    )
    parent = selection["eighteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 1_590
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dk.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dk.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dk_reconstructs_registered_partition_and_inventory(
    q011dk_cycle: dict[str, Any],
) -> None:
    fixed = q011dk_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [1, 6],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dk.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dk.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 28_224
    assert fixed["full_allocation_digest_sha256"] == q011dk.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_590
    assert fixed["compatible_allocation_digest_sha256"] == (q011dk.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 28_140
    assert fixed["parent_witness_compatible_index"] == 1_589
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dk_all_exact_intervals_are_parent_identical(
    q011dk_cycle: dict[str, Any],
) -> None:
    partition = q011dk_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_590
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_590
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_590))
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
        assert record["intersection_width_hex"] == (q011dk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dk.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dk_records_interval_inert_persistence(
    q011dk_cycle: dict[str, Any],
) -> None:
    assert q011dk_cycle["study_validity"] == "passed"
    assert q011dk_cycle["failed_validity_order"] == []
    assert q011dk_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dk_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dk_cycle["diagnostic_gates"].values())
    assert q011dk_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dk_cycle["diagnostic_classification"] == q011dk.INERT_CLASSIFICATION
    assert q011dk_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dk_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_590,
    }
    partition = q011dk_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dk_preserves_boundary_and_reproducible_digests(
    q011dk_cycle: dict[str, Any],
) -> None:
    theorem = q011dk_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_eighteenth_q011cb_witness"]
    assert not theorem["eighteenth_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 17" in q011dk_cycle["claim_boundary"]
    assert "later 44782 Q011cb refined signatures" in q011dk_cycle["claim_boundary"]
    assert "Q011dl" in q011dk_cycle["next_change"]
    json.dumps(q011dk_cycle, allow_nan=False)
    assert {name: q011dk_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dk_cycle["result_digest_sha256"] == (
        q011dk.q011b._canonical_json_sha256(q011dk._result_digest_sections(q011dk_cycle))
    )
    assert q011dk._protocol_globals_are_restored()


def test_q011dk_study_metadata_and_optional_artifact_are_scoped(
    q011dk_study: dict[str, Any],
) -> None:
    assert q011dk_study["schema_version"] == 1
    assert q011dk_study["source"] == source_metadata()
    assert q011dk_study["study_gate"] == "passed"
    assert q011dk_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dk_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_590
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dk_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 17
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dk_study, allow_nan=False)

    runner_path = Path(q011dk.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dk_degree34_eighteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dk artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dk.q011b._canonical_json_sha256(q011dk._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
