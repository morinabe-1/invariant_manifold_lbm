from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cq_degree34_eighth_individual_partition_audit as q011cq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "db9be5e8652b16ebe42ff8d46e9b7f4703ca4cdf4ae93d98d6eaf138cb0a0595"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "7f07489552736b5c5105aa64929870f5cf22bdd430be012ced1acb8eb0282e0b"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "bc327d381eee5a285d5fc35b0543e16050c65e57dcd4e43a405c97edab3732e3",
    "partition_input_digest_sha256": (
        "c42fa3b0729531f0123498591ae56ded15526347a3ae680d59486d10929bc4b7"
    ),
    "allocation_audit_digest_sha256": (
        "d24be289597289e30edc367825e37b89526659aebe9c055e10139aef94b8d7f9"
    ),
    "result_digest_sha256": "72c1bb458bb8ce2b77f152922e9c96a69de33ffc2df30948ed6a1a56ee73aff2",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "e9d957944f564935b6f3b0ab1bd38fd14534201b180f9d075be0d6d81f4052a8"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c1fc6160f171274904add68c4401e687492d0c3eb2d0745200217d71e8f87a6d"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "f6878297ed8400dc4a0a40dc1cd3a497d17343746400231e2bf3102baadd56df"
    ),
    "allocation_classification_record_digest_sha256": (
        "21e135468c9c03c73927cdb423dfbd258ad15a54b56cd2a589da723fbd53b855"
    ),
}


@pytest.fixture(scope="module")
def q011cq_study() -> dict[str, Any]:
    return q011cq.run_q011cq_study()


@pytest.fixture(scope="module")
def q011cq_cycle(q011cq_study: dict[str, Any]) -> dict[str, Any]:
    return q011cq_study["cycle"]


def test_q011cq_seals_q011cp_and_all_prior_inputs(
    q011cq_cycle: dict[str, Any],
) -> None:
    sealed = q011cq_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 73
    assert sealed["direct_digest_count"] == 341
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cp"]["digests"]) == q011cq.Q011CP_DIGESTS
    assert sealed["q011cp"]["artifact_sha256"] == q011cq.Q011CP_ARTIFACT_SHA256
    assert sealed["q011cp"]["runner_sha256"] == q011cq.Q011CP_RUNNER_SHA256
    assert sealed["q011cp"]["resolved_witness_digest_sha256"] == (
        q011cq.EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
    )


def test_q011cq_selects_exactly_flatten_ordinal_seven(
    q011cq_cycle: dict[str, Any],
) -> None:
    fixed = q011cq_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 7
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2, 3, 4, 5, 6]
    assert selection["ordinal_four_resolution_digest_sha256"] == (
        q011cq.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    assert selection["ordinal_five_resolution_digest_sha256"] == (
        q011cq.EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )
    assert selection["ordinal_six_resolution_digest_sha256"] == (
        q011cq.EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
    )
    parent = selection["eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 382
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011cq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011cq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011cq_reconstructs_registered_partition_and_inventory(
    q011cq_cycle: dict[str, Any],
) -> None:
    fixed = q011cq_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011cq.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == (q011cq.EXPECTED_IDENTIFIER_ORDER)
    assert fixed["full_allocation_count"] == 6_720
    assert fixed["full_allocation_digest_sha256"] == q011cq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 382
    assert fixed["compatible_allocation_digest_sha256"] == (q011cq.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 6_672
    assert fixed["parent_witness_compatible_index"] == 381
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011cq_all_exact_intervals_are_parent_identical(
    q011cq_cycle: dict[str, Any],
) -> None:
    partition = q011cq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 382
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 382
    assert [record["compatible_allocation_index"] for record in records] == list(range(382))
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
        assert record["intersection_width_hex"] == (q011cq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011cq.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cq_records_interval_inert_persistence(
    q011cq_cycle: dict[str, Any],
) -> None:
    assert q011cq_cycle["study_validity"] == "passed"
    assert q011cq_cycle["failed_validity_order"] == []
    assert q011cq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cq_cycle["diagnostic_gates"].values())
    assert q011cq_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cq_cycle["diagnostic_classification"] == q011cq.INERT_CLASSIFICATION
    assert q011cq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cq_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 382,
    }
    partition = q011cq_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cq_preserves_boundary_and_reproducible_digests(
    q011cq_cycle: dict[str, Any],
) -> None:
    theorem = q011cq_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_eighth_q011cb_witness"]
    assert not theorem["eighth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 7" in q011cq_cycle["claim_boundary"]
    assert "later 44792 Q011cb refined signatures" in q011cq_cycle["claim_boundary"]
    json.dumps(q011cq_cycle, allow_nan=False)
    assert {
        name: q011cq_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011cq_cycle["result_digest_sha256"] == (
        q011cq.q011b._canonical_json_sha256(q011cq._result_digest_sections(q011cq_cycle))
    )
    assert q011cq._protocol_globals_are_restored()


def test_q011cq_study_metadata_and_optional_artifact_are_scoped(
    q011cq_study: dict[str, Any],
) -> None:
    assert q011cq_study["schema_version"] == 1
    assert q011cq_study["source"] == source_metadata()
    assert q011cq_study["study_gate"] == "passed"
    assert q011cq_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011cq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 382
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 7
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cq_study, allow_nan=False)

    runner_path = Path(q011cq.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / ("q011cq_degree34_eighth_individual_partition_audit.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cq.q011b._canonical_json_sha256(q011cq._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
