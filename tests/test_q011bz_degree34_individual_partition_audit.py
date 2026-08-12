from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bz_degree34_individual_partition_audit as q011bz
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "dbb1c3157e774e337b59b86c7d26997095e4d0deae70bef4f01fd2c94f3b27b5"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8da2a7b86599b5a287a92dd62804d46665c4fa2a1416a11b04ebe43c27efa569"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "ad62c8a085db60925b250d81a212bd9ee66792d539522ee1e5edb4dec45196ae",
    "partition_input_digest_sha256": (
        "758844d52532616264901f6fe07d9c7e12bf836337c98c80539ea9a41f11b2f2"
    ),
    "allocation_audit_digest_sha256": (
        "d0df75d838daf7f9822bb98486184544cc660120cea3645f7d9b3f0b869dc551"
    ),
    "result_digest_sha256": "56102d2a66116d06614698771689760507f6bf2f23f98410a1f592442a2c76a2",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "8321b06eb574dca32c1a0861dcc8c2fbcf2dd0034e0216bf1b0bcf7b8bd254cc"
    ),
    "parent_target_interval_digest_sha256": (
        "b35461ebf211bc7e539bb7171a1f0a448cdfb47327edb1f064b03739ed22c35a"
    ),
    "parent_intersection_interval_digest_sha256": (
        "c8aea46a677f6476c322d602b2256e7be67e5a57d860996f446879b6272cef35"
    ),
    "allocation_classification_record_digest_sha256": (
        "1807f40743fe6d9be351c2dfa878889222e8a9608f17b5c273e21f2b59a2f18d"
    ),
}


@pytest.fixture(scope="module")
def q011bz_study() -> dict[str, Any]:
    return q011bz.run_q011bz_study()


@pytest.fixture(scope="module")
def q011bz_cycle(q011bz_study: dict[str, Any]) -> dict[str, Any]:
    return q011bz_study["cycle"]


def test_q011bz_seals_q011by_and_all_prior_inputs(q011bz_cycle: dict[str, Any]) -> None:
    sealed = q011bz_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 56
    assert sealed["direct_digest_count"] == 265
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011by"]["digests"]) == q011bz.Q011BY_DIGESTS
    assert sealed["q011by"]["artifact_sha256"] == q011bz.Q011BY_ARTIFACT_SHA256
    assert sealed["q011by"]["runner_sha256"] == q011bz.Q011BY_RUNNER_SHA256
    parent = sealed["q011by"]["parent_witness"]
    assert parent["witness_digest_sha256"] == q011bz.EXPECTED_PARENT_WITNESS_DIGEST
    assert parent["intersection_interval"]["width_hex"] == (
        q011bz.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )


def test_q011bz_reconstructs_registered_occupied_classes(
    q011bz_cycle: dict[str, Any],
) -> None:
    fixed = q011bz_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 972
    assert fixed["target_identifier"] == "block=12;center=124"
    assert fixed["output_block"] == 12
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 4],
        [0, 27],
        [0, 0, 3],
        [0, 0, 0, 0, 0, 0],
    ]
    assert [record["source_count"] for record in fixed["occupied_class_records"]] == [
        4,
        27,
        3,
    ]
    assert all(
        record["all_member_intervals_equal"]
        for record in fixed["occupied_class_records"]
    )
    assert tuple(
        record["common_interval_digest_sha256"]
        for record in fixed["occupied_class_records"]
    ) == q011bz.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011bz.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011bz.EXPECTED_IDENTIFIER_ORDER
    assert fixed["singleton_identifier_order_digest_sha256"] == (
        q011bz.EXPECTED_IDENTIFIER_ORDER_DIGEST
    )


def test_q011bz_reconstructs_exact_individual_allocation_inventory(
    q011bz_cycle: dict[str, Any],
) -> None:
    fixed = q011bz_cycle["fixed_individual_partition_input_audit"]
    assert fixed["full_allocation_count"] == 560
    assert fixed["full_allocation_digest_sha256"] == q011bz.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 39
    assert fixed["compatible_allocation_digest_sha256"] == (
        q011bz.EXPECTED_COMPATIBLE_DIGEST
    )
    assert fixed["first_compatible_counts"] == [0, 4, 8, 19, 3, 0]
    assert fixed["last_compatible_counts"] == [4, 0, 24, 3, 0, 3]
    assert fixed["parent_witness_individual_counts"] == [4, 0, 24, 3, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 544
    assert fixed["other_parent_class_signatures_recomputed"] is False
    assert fixed["other_parent_targets_recomputed"] is False
    assert fixed["second_q011bx_overlap_recomputed"] is False


def test_q011bz_all_exact_intervals_are_parent_identical(
    q011bz_cycle: dict[str, Any],
) -> None:
    partition = q011bz_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 39
    records = partition["allocation_classification_records"]
    assert len(records) == 39
    assert [record["compatible_allocation_index"] for record in records] == list(range(39))
    for record in records:
        assert record["degree"] == 34
        assert record["output_block"] == 12
        assert record["product_equals_parent"]
        assert record["center_product_equals_parent"]
        assert record["target_equals_parent"]
        assert record["intersection_equals_parent"]
        assert record["center_diagnostic_equals_parent"]
        assert record["intersection_width_hex"] == "0x1.3a21ae03356a4p-28"
        assert record["center_only_relation"] == "target_below_product"
        assert record["center_only_gap_hex"] == "0x1.b808da9a742c2p-27"
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011bz_records_interval_inert_persistence(
    q011bz_cycle: dict[str, Any],
) -> None:
    assert q011bz_cycle["study_validity"] == "passed"
    assert q011bz_cycle["failed_validity_order"] == []
    assert q011bz_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011bz_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bz_cycle["diagnostic_gates"].values())
    assert q011bz_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011bz_cycle["diagnostic_classification"] == q011bz.INERT_CLASSIFICATION
    assert q011bz_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bz_cycle["actual_resonance_outcome"] == "not_established"
    partition = q011bz_cycle["individual_allocation_interval_audit"]
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 39,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert partition["complex_phase_product_evaluated"] is False


def test_q011bz_endpoint_records_are_fixed(q011bz_cycle: dict[str, Any]) -> None:
    partition = q011bz_cycle["individual_allocation_interval_audit"]
    first = partition["first_allocation_record"]
    last = partition["last_allocation_record"]
    assert first["individual_counts"] == [0, 4, 8, 19, 3, 0]
    assert last["individual_counts"] == [4, 0, 24, 3, 0, 3]
    assert first["compatible_allocation_index"] == 0
    assert last["compatible_allocation_index"] == 38
    for record in (first, last):
        assert record["exact_relation"] == "overlap"
        assert record["binary64_outward_relation"] == "overlap"
        assert record["product_interval_digest_sha256"] == (
            "8321b06eb574dca32c1a0861dcc8c2fbcf2dd0034e0216bf1b0bcf7b8bd254cc"
        )
        assert record["center_product_interval_digest_sha256"] == (
            "557aa38b48e431a7b076fee3725bf72602ffb1670d368244c4fa7b59ad567c74"
        )
        assert record["target_interval_digest_sha256"] == (
            "b35461ebf211bc7e539bb7171a1f0a448cdfb47327edb1f064b03739ed22c35a"
        )


def test_q011bz_preserves_the_scientific_boundary(q011bz_cycle: dict[str, Any]) -> None:
    theorem = q011bz_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_first_q011by_witness"]
    assert not theorem["first_q011by_witness_is_resolved_by_individual_partition"]
    assert theorem["q011by_persistent_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["complex_phase_product_is_audited"] is False
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "does not evaluate complex phase" in q011bz_cycle["claim_boundary"]
    assert "other 9799 Q011by class signatures" in q011bz_cycle["claim_boundary"]


def test_q011bz_cycle_has_strict_reproducible_digests(q011bz_cycle: dict[str, Any]) -> None:
    json.dumps(q011bz_cycle, allow_nan=False)
    assert {
        name: q011bz_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    partition = q011bz_cycle["individual_allocation_interval_audit"]
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )
    assert q011bz_cycle["result_digest_sha256"] == q011bz.q011b._canonical_json_sha256(
        q011bz._result_digest_sections(q011bz_cycle)
    )


def test_q011bz_study_metadata_and_optional_artifact_are_scoped(
    q011bz_study: dict[str, Any],
) -> None:
    assert q011bz_study["schema_version"] == 1
    assert q011bz_study["source"] == source_metadata()
    assert q011bz_study["study_gate"] == "passed"
    assert q011bz_study["refinement_outcome"] == "partition_inert_persistent"
    assert q011bz_study["scientific_outcome"] == "not_evaluated"
    assert q011bz_study["actual_resonance_outcome"] == "not_established"
    assert q011bz_study["arithmetic_runtime"]["target_comparisons"] == 39
    assert q011bz_study["arithmetic_runtime"]["complex_phase_product_evaluated"] is False
    scope = q011bz_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 972
    assert scope["target_identifier"] == "block=12;center=124"
    assert scope["complex_phase_claim"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bz_study, allow_nan=False)

    runner_path = Path(q011bz.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011bz_degree34_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011bz artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011bz_degree34_individual_partition_audit.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011bz.q011b._canonical_json_sha256(q011bz._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
