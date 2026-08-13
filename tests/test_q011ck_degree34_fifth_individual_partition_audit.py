from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ck_degree34_fifth_individual_partition_audit as q011ck
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "0a43924bc024efaf42c851672f149c4d19ef27ebaff0bfb5fde3effe188afa2c"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "675f2f5f690320a0760d51a30063766cff760f51ddb3db8d44896c295e674588",
    "partition_input_digest_sha256": (
        "701272e5b15409ec797e851275fa7e03f8ee457da6acc97033ef4382a9c75e23"
    ),
    "allocation_audit_digest_sha256": (
        "38d186f7ec6b72249aae97e384d6c2d4f9878597bcc2a1a7f298f61a7d340fb3"
    ),
    "result_digest_sha256": "b474e9870de508954bb4cc5e7c3df147bdbbce1bac633e07ec624193e147075c",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "f16158ac437ae98ff451d55a50088cd40a8804a4bf9ed39132e3311cc9b395b2"
    ),
    "parent_center_product_interval_digest_sha256": (
        "8cf01b452271f6133e263692b44f1fa685139ecaafc5b7847b93d65706733cf4"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "2923f4423a2281c735c708b60abb8fc5286706f6a9e8a6711b1e68abbb42fbc7"
    ),
    "allocation_classification_record_digest_sha256": (
        "848069f29045bc56bf2f6cc2c8246b8a86ec5d52891fadf949ffab638fa9e6c1"
    ),
}


@pytest.fixture(scope="module")
def q011ck_study() -> dict[str, Any]:
    return q011ck.run_q011ck_study()


@pytest.fixture(scope="module")
def q011ck_cycle(q011ck_study: dict[str, Any]) -> dict[str, Any]:
    return q011ck_study["cycle"]


def test_q011ck_seals_q011cj_and_all_prior_inputs(
    q011ck_cycle: dict[str, Any],
) -> None:
    sealed = q011ck_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 67
    assert sealed["direct_digest_count"] == 314
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cj"]["digests"]) == q011ck.Q011CJ_DIGESTS
    assert sealed["q011cj"]["artifact_sha256"] == q011ck.Q011CJ_ARTIFACT_SHA256
    assert sealed["q011cj"]["runner_sha256"] == q011ck.Q011CJ_RUNNER_SHA256
    assert sealed["q011cj"]["resolved_witness_digest_sha256"] == (
        q011ck.EXPECTED_ORDINAL_THREE_RESOLUTION_DIGEST
    )


def test_q011ck_selects_exactly_flatten_ordinal_four(
    q011ck_cycle: dict[str, Any],
) -> None:
    fixed = q011ck_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 4
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2, 3]
    assert selection["ordinal_three_resolution_digest_sha256"] == (
        q011ck.EXPECTED_ORDINAL_THREE_RESOLUTION_DIGEST
    )
    parent = selection["fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 945
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ck.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ck.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ck.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ck_reconstructs_registered_partition_and_inventory(
    q011ck_cycle: dict[str, Any],
) -> None:
    fixed = q011ck_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [4, 3],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011ck.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == (
        q011ck.EXPECTED_IDENTIFIER_ORDER
    )
    assert fixed["full_allocation_count"] == 16_800
    assert fixed["full_allocation_digest_sha256"] == q011ck.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 945
    assert fixed["compatible_allocation_digest_sha256"] == (
        q011ck.EXPECTED_COMPATIBLE_DIGEST
    )
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 16_680
    assert fixed["parent_witness_compatible_index"] == 944
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ck_all_exact_intervals_are_parent_identical(
    q011ck_cycle: dict[str, Any],
) -> None:
    partition = q011ck_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 945
    assert partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 945
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(945)
    )
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
        assert record["intersection_width_hex"] == q011ck.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011ck.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ck_records_interval_inert_persistence(
    q011ck_cycle: dict[str, Any],
) -> None:
    assert q011ck_cycle["study_validity"] == "passed"
    assert q011ck_cycle["failed_validity_order"] == []
    assert q011ck_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ck_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ck_cycle["diagnostic_gates"].values())
    assert q011ck_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ck_cycle["diagnostic_classification"] == q011ck.INERT_CLASSIFICATION
    assert q011ck_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ck_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 945,
    }
    partition = q011ck_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ck_preserves_boundary_and_reproducible_digests(
    q011ck_cycle: dict[str, Any],
) -> None:
    theorem = q011ck_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_fifth_q011cb_witness"]
    assert not theorem["fifth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert theorem["q011ch_ordinal_two_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 4" in q011ck_cycle["claim_boundary"]
    assert "later 44795 Q011cb refined signatures" in q011ck_cycle["claim_boundary"]
    json.dumps(q011ck_cycle, allow_nan=False)
    assert {
        name: q011ck_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011ck_cycle["result_digest_sha256"] == (
        q011ck.q011b._canonical_json_sha256(
            q011ck._result_digest_sections(q011ck_cycle)
        )
    )
    assert q011ck._protocol_globals_are_restored()


def test_q011ck_study_metadata_and_optional_artifact_are_scoped(
    q011ck_study: dict[str, Any],
) -> None:
    assert q011ck_study["schema_version"] == 1
    assert q011ck_study["source"] == source_metadata()
    assert q011ck_study["study_gate"] == "passed"
    assert q011ck_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ck_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 945
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ck_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 4
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ck_study, allow_nan=False)

    runner_path = Path(q011ck.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011ck_degree34_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ck artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ck.q011b._canonical_json_sha256(
            q011ck._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
