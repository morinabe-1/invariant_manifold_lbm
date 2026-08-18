from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ec_degree34_twenty_seventh_individual_partition_audit as q011ec
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "f025c27a6a206f992990d14fc4c4688445665c75a5d57517e3bd8c5c7b2432f6"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "b8ddd1e26a53988602f37085b29d73dca1c3740d3ccc7663cf98fa1c5b5d6ff8"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "f2db6d0dbf69817510b3daf0abd999096fdfbd66e15d9057564afcd18b977d76",
    "partition_input_digest_sha256": "2b186dc1bdd8713724b5e4ce059d7cbaa06552a2908c05e617e1ed3f64a78941",
    "allocation_audit_digest_sha256": "29b19db2398959867041e1c2f674c1c94b680fc273c1c7a8fe98fd81d5d000e4",
    "result_digest_sha256": "350199df4b0d05270f4e0dbf8131ec73472ca533dc2752d9fc870cd7f6ab7e4a",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "13017e1b8a052ec0475c127248b30f7a1be21be0b66613a66309e34e0f9b6682"
    ),
    "parent_center_product_interval_digest_sha256": (
        "1ddca96e0f7254e32fc3c7ace564fdb186b0a3cf2c189faa255e36174bd007d4"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "d09464d3f85a0b3e3673b424f301473ab3d9ce9dfde21fa2cfac4ec4702dc7dd"
    ),
    "allocation_classification_record_digest_sha256": (
        "09f6003915d511ba0fde8a9d92a0df1ac2accd284bc7df5900b69b5d4934314b"
    ),
}


@pytest.fixture(scope="module")
def q011ec_study() -> dict[str, Any]:
    return q011ec.run_q011ec_study()


@pytest.fixture(scope="module")
def q011ec_cycle(q011ec_study: dict[str, Any]) -> dict[str, Any]:
    return q011ec_study["cycle"]


def test_q011ec_seals_q011eb_and_all_prior_inputs(
    q011ec_cycle: dict[str, Any],
) -> None:
    sealed = q011ec_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 111
    assert sealed["direct_digest_count"] == 512
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011eb"]["digests"]) == q011ec.Q011EB_DIGESTS
    assert sealed["q011eb"]["artifact_sha256"] == q011ec.Q011EB_ARTIFACT_SHA256
    assert sealed["q011eb"]["runner_sha256"] == q011ec.Q011EB_RUNNER_SHA256
    assert sealed["q011eb"]["resolved_witness_digest_sha256"] == (
        q011ec.EXPECTED_ORDINAL_TWENTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011ec_selects_exactly_flatten_ordinal_twenty_six(
    q011ec_cycle: dict[str, Any],
) -> None:
    fixed = q011ec_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 26
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(26))
    assert selection["ordinal_twenty_five_resolution_digest_sha256"] == (
        q011ec.EXPECTED_ORDINAL_TWENTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["twenty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 2_382
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ec.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ec.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ec.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ec_reconstructs_registered_partition_and_inventory(
    q011ec_cycle: dict[str, Any],
) -> None:
    fixed = q011ec_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ec.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ec.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 42_336
    assert fixed["full_allocation_digest_sha256"] == q011ec.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_382
    assert fixed["compatible_allocation_digest_sha256"] == (q011ec.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 42_228
    assert fixed["parent_witness_compatible_index"] == 2_381
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ec_all_exact_intervals_are_parent_identical(
    q011ec_cycle: dict[str, Any],
) -> None:
    partition = q011ec_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_382
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_382
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_382))
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
        assert record["intersection_width_hex"] == (q011ec.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011ec.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011ec partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ec_records_interval_inert_persistence(
    q011ec_cycle: dict[str, Any],
) -> None:
    assert q011ec_cycle["study_validity"] == "passed"
    assert q011ec_cycle["failed_validity_order"] == []
    assert q011ec_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ec_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ec_cycle["diagnostic_gates"].values())
    assert q011ec_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ec_cycle["diagnostic_classification"] == q011ec.INERT_CLASSIFICATION
    assert q011ec_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ec_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_382,
    }
    partition = q011ec_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ec_preserves_boundary_and_reproducible_digests(
    q011ec_cycle: dict[str, Any],
) -> None:
    theorem = q011ec_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_seventh_q011cb_witness"]
    assert not theorem["twenty_seventh_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 26" in q011ec_cycle["claim_boundary"]
    assert "later 44773 Q011cb refined signatures" in q011ec_cycle["claim_boundary"]
    assert "Q011ed" in q011ec_cycle["next_change"]
    json.dumps(q011ec_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ec section digests have not been sealed yet")
    assert {name: q011ec_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ec_cycle["result_digest_sha256"] == (
        q011ec.q011b._canonical_json_sha256(q011ec._result_digest_sections(q011ec_cycle))
    )
    assert q011ec._protocol_globals_are_restored()


def test_q011ec_study_metadata_and_optional_artifact_are_scoped(
    q011ec_study: dict[str, Any],
) -> None:
    assert q011ec_study["schema_version"] == 1
    assert q011ec_study["source"] == source_metadata()
    assert q011ec_study["study_gate"] == "passed"
    assert q011ec_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ec_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_382
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ec_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 26
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ec_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ec runner hash has not been sealed yet")
    runner_path = Path(q011ec.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ec_degree34_twenty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ec artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ec.q011b._canonical_json_sha256(q011ec._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
