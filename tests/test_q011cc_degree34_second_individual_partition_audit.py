from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cc_degree34_second_individual_partition_audit as q011cc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "20d5a741d100649927053314cf1e6347972568b444db7ed0ed4c793fa9296c30"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "84043cf3a41cb479a35da321b03df1fa09f04aede305215f3c582875ba7c555a"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "3fd7d65bbd0afc7facf4104c62087eec59a8ad5b7cdb589121a28cf7eec0edac",
    "partition_input_digest_sha256": (
        "93718c41e0fe0fdd9c5ca40823be13fcb98ab444fedbc3993ce9dda89f9dc81a"
    ),
    "allocation_audit_digest_sha256": (
        "b584ec6a2f1e4bf3b96318ba6ad46b9b544d722c80d3773e74d34c7d3e0ab7bf"
    ),
    "result_digest_sha256": "7701d380b4ea8640c4bb142cc2aee45c002aadb48d02d902629da500c7a3fc5d",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "8a9c1583fe51e24292e65211b7d53099b2f7e724b93cdadcac61f916dd479a58"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "cc5ca69070a20623c45139bc596262504c3e726986d4220f39082ef0d13abdfc"
    ),
    "allocation_classification_record_digest_sha256": (
        "d7fbc193a8cf9c3f62fa1871df8afefbcee11bb2710a0cd780d7102959149f6b"
    ),
}


@pytest.fixture(scope="module")
def q011cc_study() -> dict[str, Any]:
    return q011cc.run_q011cc_study()


@pytest.fixture(scope="module")
def q011cc_cycle(q011cc_study: dict[str, Any]) -> dict[str, Any]:
    return q011cc_study["cycle"]


def test_q011cc_seals_q011cb_and_all_prior_inputs(
    q011cc_cycle: dict[str, Any],
) -> None:
    sealed = q011cc_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 59
    assert sealed["direct_digest_count"] == 278
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cb"]["digests"]) == q011cc.Q011CB_DIGESTS
    assert sealed["q011cb"]["artifact_sha256"] == q011cc.Q011CB_ARTIFACT_SHA256
    assert sealed["q011cb"]["runner_sha256"] == q011cc.Q011CB_RUNNER_SHA256
    parent = sealed["q011cb"]["parent_witness"]
    assert parent["witness_digest_sha256"] == q011cc.EXPECTED_PARENT_WITNESS_DIGEST
    assert parent["wave_multiplicity"] == 382
    assert parent["intersection_interval"]["width_hex"] == (
        q011cc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )


def test_q011cc_reconstructs_registered_occupied_classes(
    q011cc_cycle: dict[str, Any],
) -> None:
    fixed = q011cc_cycle["fixed_individual_partition_input_audit"]
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
        [0, 7],
    ]
    assert [record["source_count"] for record in fixed["occupied_class_records"]] == [
        13,
        9,
        5,
        7,
    ]
    assert all(
        record["all_member_intervals_equal"]
        for record in fixed["occupied_class_records"]
    )
    assert tuple(
        record["common_interval_digest_sha256"]
        for record in fixed["occupied_class_records"]
    ) == q011cc.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011cc.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == (
        q011cc.EXPECTED_IDENTIFIER_ORDER
    )
    assert fixed["singleton_identifier_order_digest_sha256"] == (
        q011cc.EXPECTED_IDENTIFIER_ORDER_DIGEST
    )


def test_q011cc_reconstructs_exact_individual_allocation_inventory(
    q011cc_cycle: dict[str, Any],
) -> None:
    fixed = q011cc_cycle["fixed_individual_partition_input_audit"]
    assert fixed["full_allocation_count"] == 6720
    assert fixed["full_allocation_digest_sha256"] == q011cc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 382
    assert fixed["compatible_allocation_digest_sha256"] == (
        q011cc.EXPECTED_COMPATIBLE_DIGEST
    )
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_individual_counts"] == [13, 0, 9, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 6672
    assert fixed["parent_witness_compatible_index"] == 381
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert fixed["other_q011cb_refined_signatures_recomputed"] is False
    assert fixed["other_parent_targets_recomputed"] is False
    assert fixed["other_parent_overlap_signatures_recomputed"] is False


def test_q011cc_all_exact_intervals_are_parent_identical(
    q011cc_cycle: dict[str, Any],
) -> None:
    partition = q011cc_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 382
    assert partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 382
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(382)
    )
    for record in records:
        assert record["degree"] == 34
        assert record["output_block"] == 7
        assert record["product_equals_parent"]
        assert record["center_product_equals_parent"]
        assert record["target_equals_parent"]
        assert record["intersection_equals_parent"]
        assert record["center_diagnostic_equals_parent"]
        assert record["intersection_width_hex"] == "0x1.9d49c4083b31ep-32"
        assert record["center_only_relation"] == "target_below_product"
        assert record["center_only_gap_hex"] == "0x1.3aa0404d55937p-28"
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cc_records_interval_inert_persistence(
    q011cc_cycle: dict[str, Any],
) -> None:
    assert q011cc_cycle["study_validity"] == "passed"
    assert q011cc_cycle["failed_validity_order"] == []
    assert q011cc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cc_cycle["diagnostic_gates"].values())
    assert q011cc_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cc_cycle["diagnostic_classification"] == q011cc.INERT_CLASSIFICATION
    assert q011cc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cc_cycle["actual_resonance_outcome"] == "not_established"
    partition = q011cc_cycle["individual_allocation_interval_audit"]
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 382,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert partition["complex_phase_product_evaluated"] is False


def test_q011cc_endpoint_records_are_fixed(q011cc_cycle: dict[str, Any]) -> None:
    partition = q011cc_cycle["individual_allocation_interval_audit"]
    first = partition["first_allocation_record"]
    last = partition["last_allocation_record"]
    assert first["individual_counts"] == [0, 13, 0, 9, 0, 5, 5, 2]
    assert last["individual_counts"] == [13, 0, 9, 0, 0, 5, 0, 7]
    assert first["compatible_allocation_index"] == 0
    assert last["compatible_allocation_index"] == 381
    for record in (first, last):
        assert record["exact_relation"] == "overlap"
        assert record["binary64_outward_relation"] == "overlap"
        assert record["exact_gap_positive"] is False
        assert record["binary64_outward_gap_positive"] is False
        assert record["product_interval_digest_sha256"] == (
            "8a9c1583fe51e24292e65211b7d53099b2f7e724b93cdadcac61f916dd479a58"
        )
        assert record["center_product_interval_digest_sha256"] == (
            "fb6b5484336fbc1693a17550eeaf8cfd4b4f23ecbfce9f5e264e93c6f39f6004"
        )
        assert record["target_interval_digest_sha256"] == (
            "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
        )


def test_q011cc_preserves_the_scientific_boundary(
    q011cc_cycle: dict[str, Any],
) -> None:
    theorem = q011cc_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_first_q011cb_witness"]
    assert not theorem["first_q011cb_witness_is_resolved_by_individual_partition"]
    assert not theorem[
        "individual_partition_changes_intervals_but_first_q011cb_witness_persists"
    ]
    assert theorem["q011cb_persistent_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["complex_phase_product_is_audited"] is False
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "does not evaluate complex phase" in q011cc_cycle["claim_boundary"]
    assert "other 44799 Q011cb refined signatures" in q011cc_cycle["claim_boundary"]


def test_q011cc_cycle_has_strict_reproducible_digests(
    q011cc_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cc_cycle, allow_nan=False)
    assert {
        name: q011cc_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    partition = q011cc_cycle["individual_allocation_interval_audit"]
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )
    assert q011cc_cycle["result_digest_sha256"] == (
        q011cc.q011b._canonical_json_sha256(q011cc._result_digest_sections(q011cc_cycle))
    )


def test_q011cc_study_metadata_and_optional_artifact_are_scoped(
    q011cc_study: dict[str, Any],
) -> None:
    assert q011cc_study["schema_version"] == 1
    assert q011cc_study["source"] == source_metadata()
    assert q011cc_study["study_gate"] == "passed"
    assert q011cc_study["refinement_outcome"] == "partition_inert_persistent"
    assert q011cc_study["scientific_outcome"] == "not_evaluated"
    assert q011cc_study["actual_resonance_outcome"] == "not_established"
    assert q011cc_study["arithmetic_runtime"]["target_comparisons"] == 382
    assert q011cc_study["arithmetic_runtime"]["complex_phase_product_evaluated"] is False
    scope = q011cc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["complex_phase_claim"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cc_study, allow_nan=False)

    runner_path = Path(q011cc.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011cc_degree34_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cc_degree34_second_individual_partition_audit.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cc.q011b._canonical_json_sha256(
            q011cc._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
