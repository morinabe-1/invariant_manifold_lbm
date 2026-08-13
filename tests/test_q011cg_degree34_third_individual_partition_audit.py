from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cg_degree34_third_individual_partition_audit as q011cg
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "2b3891a48840d62fa227a95aa6ed13e102056751d59ac969bc9e5a73d9e98600"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "ba8189bc52e59644298b9e9587d7468c5035f861667b9e2847522b9e4ce4d32e"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "3a9bf134093d72dfa3a9fce972eea9213f5d2221c8a96796849dc714efd16e04",
    "partition_input_digest_sha256": (
        "b675a240f2d7d8ec553ba905dc69104d1ab580cd7ad582044e62be4bc31bee38"
    ),
    "allocation_audit_digest_sha256": (
        "30167e3024dc9dd61b70a72bc45426cc702ac47d251954ecf68f8a19532a0f88"
    ),
    "result_digest_sha256": "f99176bee9bec4e82530ce33227a1950949986f83112f5eca9cd917b03af1d15",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "64a3064807e315faf5184bd356b6b91d62d2b5e6972fb0acbb7bfecb699fac24"
    ),
    "parent_center_product_interval_digest_sha256": (
        "1be6580f390528ca757c27bcbc619a6f5d0c8d61a88afe3338ed9e7af3f06bae"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "33bfbc4d6a92965fcc7f33795b0d062539f205cebad0c558842580cb1727e97e"
    ),
    "allocation_classification_record_digest_sha256": (
        "b3b578822153dac0f180c7a341aeb744bcd054ac680de3cac336a19c03fedc87"
    ),
}


@pytest.fixture(scope="module")
def q011cg_study() -> dict[str, Any]:
    return q011cg.run_q011cg_study()


@pytest.fixture(scope="module")
def q011cg_cycle(q011cg_study: dict[str, Any]) -> dict[str, Any]:
    return q011cg_study["cycle"]


def test_q011cg_seals_q011cf_and_all_prior_inputs(
    q011cg_cycle: dict[str, Any],
) -> None:
    sealed = q011cg_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 63
    assert sealed["direct_digest_count"] == 296
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cf"]["digests"]) == q011cg.Q011CF_DIGESTS
    assert sealed["q011cf"]["artifact_sha256"] == q011cg.Q011CF_ARTIFACT_SHA256
    assert sealed["q011cf"]["runner_sha256"] == q011cg.Q011CF_RUNNER_SHA256
    assert sealed["q011cf"]["resolved_witness_digest_sha256"] == (
        q011cg.EXPECTED_ORDINAL_ONE_RESOLUTION_DIGEST
    )


def test_q011cg_selects_exactly_flatten_ordinal_two(
    q011cg_cycle: dict[str, Any],
) -> None:
    fixed = q011cg_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["compatible_refined_signature_count"] == 44_800
    assert selection["stored_overlap_signature_count"] == 44_800
    assert selection["selected_flat_ordinal"] == 2
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == [0, 1]
    assert selection["ordinal_zero_witness_digest_sha256"] == (
        q011cg.EXPECTED_ORDINAL_ZERO_WITNESS_DIGEST
    )
    assert selection["ordinal_one_resolution_digest_sha256"] == (
        q011cg.EXPECTED_ORDINAL_ONE_RESOLUTION_DIGEST
    )
    parent = selection["third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 852
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011cg.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011cg.EXPECTED_PARENT_WITNESS_DIGEST
    assert not selection["previous_q011cb_refined_signatures_classified_again"]
    assert not selection["later_q011cb_refined_signatures_classified_again"]


def test_q011cg_reconstructs_registered_partition_and_inventory(
    q011cg_cycle: dict[str, Any],
) -> None:
    fixed = q011cg_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["output_block"] == 7
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert tuple(
        record["common_interval_digest_sha256"] for record in occupied
    ) == q011cg.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011cg.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == (
        q011cg.EXPECTED_IDENTIFIER_ORDER
    )
    assert fixed["singleton_identifier_order_digest_sha256"] == (
        q011cg.EXPECTED_IDENTIFIER_ORDER_DIGEST
    )
    assert fixed["full_allocation_count"] == 15_120
    assert fixed["full_allocation_digest_sha256"] == q011cg.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 852
    assert fixed["compatible_allocation_digest_sha256"] == (
        q011cg.EXPECTED_COMPATIBLE_DIGEST
    )
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_individual_counts"] == [
        13,
        0,
        9,
        0,
        0,
        5,
        0,
        2,
        0,
        5,
    ]
    assert fixed["parent_witness_allocation_index"] == 15_012
    assert fixed["parent_witness_compatible_index"] == 851
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert not fixed["previous_q011cb_refined_signatures_recomputed"]
    assert not fixed["later_q011cb_refined_signatures_recomputed"]
    assert not fixed["other_parent_targets_recomputed"]
    assert not fixed["other_parent_overlap_signatures_recomputed"]


def test_q011cg_all_exact_intervals_are_parent_identical(
    q011cg_cycle: dict[str, Any],
) -> None:
    partition = q011cg_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 852
    assert partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 852
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(852)
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
        assert record["intersection_width_hex"] == "0x1.9d498ce5a3fdcp-32"
        assert record["center_only_relation"] == "target_below_product"
        assert record["center_only_gap_hex"] == "0x1.3aa03b95e2c0ap-28"
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cg_records_interval_inert_persistence(
    q011cg_cycle: dict[str, Any],
) -> None:
    assert q011cg_cycle["study_validity"] == "passed"
    assert q011cg_cycle["failed_validity_order"] == []
    assert q011cg_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cg_cycle["diagnostic_gates"].values())
    assert q011cg_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cg_cycle["diagnostic_classification"] == q011cg.INERT_CLASSIFICATION
    assert q011cg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cg_cycle["actual_resonance_outcome"] == "not_established"
    partition = q011cg_cycle["individual_allocation_interval_audit"]
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 852,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cg_preserves_boundary_and_reproducible_digests(
    q011cg_cycle: dict[str, Any],
) -> None:
    theorem = q011cg_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_third_q011cb_witness"]
    assert not theorem["third_q011cb_witness_is_resolved_by_individual_partition"]
    assert not theorem[
        "individual_partition_changes_intervals_but_third_q011cb_witness_persists"
    ]
    assert theorem["q011cf_ordinal_one_phase_resolution_is_preserved"]
    assert theorem["q011cd_ordinal_zero_phase_resolution_is_preserved"]
    assert theorem["q011cb_persistent_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem[
        "an_actual_degree_thirty_four_external_resonance_is_established"
    ]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "flatten ordinal 2" in q011cg_cycle["claim_boundary"]
    assert "later 44797 Q011cb refined signatures" in q011cg_cycle["claim_boundary"]
    json.dumps(q011cg_cycle, allow_nan=False)
    assert {
        name: q011cg_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011cg_cycle["result_digest_sha256"] == (
        q011cg.q011b._canonical_json_sha256(
            q011cg._result_digest_sections(q011cg_cycle)
        )
    )


def test_q011cg_study_metadata_and_optional_artifact_are_scoped(
    q011cg_study: dict[str, Any],
) -> None:
    assert q011cg_study["schema_version"] == 1
    assert q011cg_study["source"] == source_metadata()
    assert q011cg_study["study_gate"] == "passed"
    assert q011cg_study["refinement_outcome"] == "partition_inert_persistent"
    assert q011cg_study["scientific_outcome"] == "not_evaluated"
    assert q011cg_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cg_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 852
    assert runtime["complex_phase_product_evaluated"] is False
    scope = q011cg_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 2
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["complex_phase_claim"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cg_study, allow_nan=False)

    runner_path = Path(q011cg.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011cg_degree34_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cg_degree34_third_individual_partition_audit.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cg.q011b._canonical_json_sha256(
            q011cg._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
