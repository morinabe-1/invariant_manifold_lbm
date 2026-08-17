from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dg_degree34_sixteenth_individual_partition_audit as q011dg
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "09faef7a03b467c5f5e00955fae7f387bfc2bb489b54bff2a66e5eb66ac41167"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "fa7c45162ec9d0d001abcd83b598ce9dacd2e81b52fc4fa742820bb46ded6545"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "eeee9b3cfa50c0a10d1c86f87d28cb6020039a59da58186e866627c21e538fe1",
    "partition_input_digest_sha256": (
        "43fb1e12db51467d02ed82cac69514aed76b7d3810db68fe42e1492dfae07e01"
    ),
    "allocation_audit_digest_sha256": (
        "4a3c3b333af16bb0c2441ee59e27f911cc6597f7b821316e274859edc458aa9e"
    ),
    "result_digest_sha256": "305e0c1df9e9674fec311522f9131e758a72df37be50844050d3774028b3ba4b",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "d824ef74ca7a22fce544b99cf0a1cf82f7504fbf9240facff6acf4a96ec7e446"
    ),
    "parent_center_product_interval_digest_sha256": (
        "7eab4691f6bb13ec2a9bc5a429e28e33e6800af737c576356c3eff9e8fa0efce"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "2fb2b7536ae95fe85d11d8faac5c05849d553ac2d45e9f2c141a0b670b00c136"
    ),
    "allocation_classification_record_digest_sha256": (
        "cae8c83ac2c28aeafb11618cda64fd52326d958319bd065f78efb9f6b2d4bcdf"
    ),
}


@pytest.fixture(scope="module")
def q011dg_study() -> dict[str, Any]:
    return q011dg.run_q011dg_study()


@pytest.fixture(scope="module")
def q011dg_cycle(q011dg_study: dict[str, Any]) -> dict[str, Any]:
    return q011dg_study["cycle"]


def test_q011dg_seals_q011df_and_all_prior_inputs(
    q011dg_cycle: dict[str, Any],
) -> None:
    sealed = q011dg_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 89
    assert sealed["direct_digest_count"] == 413
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011df"]["digests"]) == q011dg.Q011DF_DIGESTS
    assert sealed["q011df"]["artifact_sha256"] == q011dg.Q011DF_ARTIFACT_SHA256
    assert sealed["q011df"]["runner_sha256"] == q011dg.Q011DF_RUNNER_SHA256
    assert sealed["q011df"]["resolved_witness_digest_sha256"] == (
        q011dg.EXPECTED_ORDINAL_FOURTEEN_RESOLUTION_DIGEST
    )


def test_q011dg_selects_exactly_flatten_ordinal_fifteen(
    q011dg_cycle: dict[str, Any],
) -> None:
    fixed = q011dg_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["sixteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 15
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(15))
    assert selection["ordinal_fourteen_resolution_digest_sha256"] == (
        q011dg.EXPECTED_ORDINAL_FOURTEEN_RESOLUTION_DIGEST
    )
    parent = selection["sixteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 685
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dg.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dg.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dg_reconstructs_registered_partition_and_inventory(
    q011dg_cycle: dict[str, Any],
) -> None:
    fixed = q011dg_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dg.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dg.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 12_096
    assert fixed["full_allocation_digest_sha256"] == q011dg.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 685
    assert fixed["compatible_allocation_digest_sha256"] == q011dg.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 12_048
    assert fixed["parent_witness_compatible_index"] == 684
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dg_all_exact_intervals_are_parent_identical(
    q011dg_cycle: dict[str, Any],
) -> None:
    partition = q011dg_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 685
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 685
    assert [record["compatible_allocation_index"] for record in records] == list(range(685))
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
        assert record["intersection_width_hex"] == (q011dg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dg.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dg_records_interval_inert_persistence(
    q011dg_cycle: dict[str, Any],
) -> None:
    assert q011dg_cycle["study_validity"] == "passed"
    assert q011dg_cycle["failed_validity_order"] == []
    assert q011dg_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dg_cycle["diagnostic_gates"].values())
    assert q011dg_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dg_cycle["diagnostic_classification"] == q011dg.INERT_CLASSIFICATION
    assert q011dg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dg_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 685,
    }
    partition = q011dg_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dg_preserves_boundary_and_reproducible_digests(
    q011dg_cycle: dict[str, Any],
) -> None:
    theorem = q011dg_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_sixteenth_q011cb_witness"]
    assert not theorem["sixteenth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011df_ordinal_fourteen_phase_resolution_is_preserved"]
    assert theorem["q011de_ordinal_fourteen_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 15" in q011dg_cycle["claim_boundary"]
    assert "later 44784 Q011cb refined signatures" in q011dg_cycle["claim_boundary"]
    assert "Q011dh" in q011dg_cycle["next_change"]
    json.dumps(q011dg_cycle, allow_nan=False)
    assert {name: q011dg_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dg_cycle["result_digest_sha256"] == (
        q011dg.q011b._canonical_json_sha256(q011dg._result_digest_sections(q011dg_cycle))
    )
    assert q011dg._protocol_globals_are_restored()


def test_q011dg_study_metadata_and_optional_artifact_are_scoped(
    q011dg_study: dict[str, Any],
) -> None:
    assert q011dg_study["schema_version"] == 1
    assert q011dg_study["source"] == source_metadata()
    assert q011dg_study["study_gate"] == "passed"
    assert q011dg_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dg_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 685
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dg_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 15
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dg_study, allow_nan=False)

    runner_path = Path(q011dg.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dg_degree34_sixteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dg.q011b._canonical_json_sha256(q011dg._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
