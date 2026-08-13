from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ce_degree34_next_individual_partition_audit as q011ce
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "732cec8806d444105dbab7f58822a062e4d60d52571319492c232fb5b39e0674"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "92c443100511d6a9667709a846fcafd5e1749b11fafb46f9e944f88aad22c332",
    "partition_input_digest_sha256": (
        "63b40ea5b2b91dd30a70f8c284b903e9eaa6a2215ebce72bcf70df6eb1676da7"
    ),
    "allocation_audit_digest_sha256": (
        "aee34dfd055179c84ea99610ce7d3127daa151fb4d4715ff73dfd67268857f7e"
    ),
    "result_digest_sha256": "d0b90c1b41384ed7200871c727238e1056d5615de65ae1c063d469b7a6bb0e4b",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "d183ec7ddab4a55e3a9d87c7aa8f900be9e71f23b9cc932dcbf174582a7e7fc4"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "d2efd6ea013adda44df2a43f4bd9c84f9cbe789e663e8d1e362d84399ee8732c"
    ),
    "allocation_classification_record_digest_sha256": (
        "1b3dc935769d19e24be10148b435a20ce83b2165580f0bd8263d5d39f10378a4"
    ),
}


@pytest.fixture(scope="module")
def q011ce_study() -> dict[str, Any]:
    return q011ce.run_q011ce_study()


@pytest.fixture(scope="module")
def q011ce_cycle(q011ce_study: dict[str, Any]) -> dict[str, Any]:
    return q011ce_study["cycle"]


def test_q011ce_seals_q011cd_and_all_prior_inputs(
    q011ce_cycle: dict[str, Any],
) -> None:
    sealed = q011ce_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 61
    assert sealed["direct_digest_count"] == 287
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cd"]["digests"]) == q011ce.Q011CD_DIGESTS
    assert sealed["q011cd"]["artifact_sha256"] == q011ce.Q011CD_ARTIFACT_SHA256
    assert sealed["q011cd"]["runner_sha256"] == q011ce.Q011CD_RUNNER_SHA256
    assert sealed["q011cd"]["resolved_witness_digest_sha256"] == (
        q011ce.EXPECTED_PREVIOUS_RESOLUTION_DIGEST
    )


def test_q011ce_selects_exactly_flatten_ordinal_one(
    q011ce_cycle: dict[str, Any],
) -> None:
    fixed = q011ce_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["next_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["compatible_refined_signature_count"] == 44_800
    assert selection["stored_overlap_signature_count"] == 44_800
    assert selection["selected_flat_ordinal"] == 1
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 1
    assert selection["previous_witness_phase_resolved"]
    assert selection["previous_witness_digest_sha256"] == (q011ce.EXPECTED_PREVIOUS_WITNESS_DIGEST)
    assert selection["later_q011cb_refined_signatures_classified_again"] is False
    parent = selection["next_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 665
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ce.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ce.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ce.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ce_reconstructs_registered_occupied_classes(
    q011ce_cycle: dict[str, Any],
) -> None:
    fixed = q011ce_cycle["fixed_individual_partition_input_audit"]
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
        [1, 6],
    ]
    assert [record["source_count"] for record in fixed["occupied_class_records"]] == [
        13,
        9,
        5,
        1,
        6,
    ]
    assert all(record["all_member_intervals_equal"] for record in fixed["occupied_class_records"])
    assert (
        tuple(record["common_interval_digest_sha256"] for record in fixed["occupied_class_records"])
        == q011ce.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
    )
    assert fixed["occupied_class_record_digest_sha256"] == (q011ce.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == (q011ce.EXPECTED_IDENTIFIER_ORDER)
    assert fixed["singleton_identifier_order_digest_sha256"] == (
        q011ce.EXPECTED_IDENTIFIER_ORDER_DIGEST
    )


def test_q011ce_reconstructs_exact_individual_allocation_inventory(
    q011ce_cycle: dict[str, Any],
) -> None:
    fixed = q011ce_cycle["fixed_individual_partition_input_audit"]
    assert fixed["full_allocation_count"] == 11_760
    assert fixed["full_allocation_digest_sha256"] == q011ce.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 665
    assert fixed["compatible_allocation_digest_sha256"] == (q011ce.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_individual_counts"] == [
        13,
        0,
        9,
        0,
        0,
        5,
        0,
        1,
        0,
        6,
    ]
    assert fixed["parent_witness_allocation_index"] == 11_676
    assert fixed["parent_witness_compatible_index"] == 664
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert fixed["previous_q011cb_refined_signature_recomputed"] is False
    assert fixed["later_q011cb_refined_signatures_recomputed"] is False
    assert fixed["other_parent_targets_recomputed"] is False
    assert fixed["other_parent_overlap_signatures_recomputed"] is False


def test_q011ce_all_exact_intervals_are_parent_identical(
    q011ce_cycle: dict[str, Any],
) -> None:
    partition = q011ce_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 665
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 665
    assert [record["compatible_allocation_index"] for record in records] == list(range(665))
    for record in records:
        assert record["degree"] == 34
        assert record["output_block"] == 7
        assert record["product_equals_parent"]
        assert record["center_product_equals_parent"]
        assert record["target_equals_parent"]
        assert record["intersection_equals_parent"]
        assert record["center_diagnostic_equals_parent"]
        assert record["intersection_width_hex"] == "0x1.9d49a876ef97dp-32"
        assert record["center_only_relation"] == "target_below_product"
        assert record["center_only_gap_hex"] == "0x1.3aa03df19c2a0p-28"
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ce_records_interval_inert_persistence(
    q011ce_cycle: dict[str, Any],
) -> None:
    assert q011ce_cycle["study_validity"] == "passed"
    assert q011ce_cycle["failed_validity_order"] == []
    assert q011ce_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ce_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ce_cycle["diagnostic_gates"].values())
    assert q011ce_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ce_cycle["diagnostic_classification"] == q011ce.INERT_CLASSIFICATION
    assert q011ce_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ce_cycle["actual_resonance_outcome"] == "not_established"
    partition = q011ce_cycle["individual_allocation_interval_audit"]
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 665,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert partition["complex_phase_product_evaluated"] is False


def test_q011ce_endpoint_records_are_fixed(q011ce_cycle: dict[str, Any]) -> None:
    partition = q011ce_cycle["individual_allocation_interval_audit"]
    first = partition["first_allocation_record"]
    last = partition["last_allocation_record"]
    assert first["individual_counts"] == [0, 13, 0, 9, 0, 5, 0, 1, 5, 1]
    assert last["individual_counts"] == [13, 0, 9, 0, 0, 5, 0, 1, 0, 6]
    assert first["compatible_allocation_index"] == 0
    assert last["compatible_allocation_index"] == 664
    for record in (first, last):
        assert record["exact_relation"] == "overlap"
        assert record["binary64_outward_relation"] == "overlap"
        assert record["exact_gap_positive"] is False
        assert record["binary64_outward_gap_positive"] is False
        assert record["product_interval_digest_sha256"] == (
            "d183ec7ddab4a55e3a9d87c7aa8f900be9e71f23b9cc932dcbf174582a7e7fc4"
        )
        assert record["center_product_interval_digest_sha256"] == (
            "3b6acc43267cad068361fbc5022c4222f148baa151fe21b7e577f0836a5dc435"
        )
        assert record["target_interval_digest_sha256"] == (
            "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
        )


def test_q011ce_preserves_the_scientific_boundary_and_digests(
    q011ce_cycle: dict[str, Any],
) -> None:
    theorem = q011ce_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_next_q011cb_witness"]
    assert not theorem["next_q011cb_witness_is_resolved_by_individual_partition"]
    assert not theorem["individual_partition_changes_intervals_but_next_q011cb_witness_persists"]
    assert theorem["q011cd_first_witness_phase_resolution_is_preserved"]
    assert theorem["q011cb_persistent_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["complex_phase_product_is_audited"] is False
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "flatten ordinal 1" in q011ce_cycle["claim_boundary"]
    assert "later 44798 Q011cb refined signatures" in q011ce_cycle["claim_boundary"]
    json.dumps(q011ce_cycle, allow_nan=False)
    assert {
        name: q011ce_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011ce_cycle["result_digest_sha256"] == (
        q011ce.q011b._canonical_json_sha256(q011ce._result_digest_sections(q011ce_cycle))
    )


def test_q011ce_study_metadata_and_optional_artifact_are_scoped(
    q011ce_study: dict[str, Any],
) -> None:
    assert q011ce_study["schema_version"] == 1
    assert q011ce_study["source"] == source_metadata()
    assert q011ce_study["study_gate"] == "passed"
    assert q011ce_study["refinement_outcome"] == "partition_inert_persistent"
    assert q011ce_study["scientific_outcome"] == "not_evaluated"
    assert q011ce_study["actual_resonance_outcome"] == "not_established"
    assert q011ce_study["arithmetic_runtime"]["target_comparisons"] == 665
    assert q011ce_study["arithmetic_runtime"]["complex_phase_product_evaluated"] is False
    scope = q011ce_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 1
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["complex_phase_claim"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ce_study, allow_nan=False)

    runner_path = Path(q011ce.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / ("q011ce_degree34_next_individual_partition_audit.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011ce artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011ce_degree34_next_individual_partition_audit.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ce.q011b._canonical_json_sha256(q011ce._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
