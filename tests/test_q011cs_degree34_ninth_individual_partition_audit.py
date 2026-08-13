from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cs_degree34_ninth_individual_partition_audit as q011cs
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a2e7490202164704574d29ead3567765ac6da90d50ff0d0a8439a4a707a6f47f"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "8eb02dd122b16ffdd812bc0a7a0596a34dda00b9df10ee1a161de83290ecf9e4",
    "partition_input_digest_sha256": (
        "7ea731075f2bb4697425a85cf1356e59caaf425a4cb0ce471f1503be9f7b2ee2"
    ),
    "allocation_audit_digest_sha256": (
        "f55170c64af0d81e80063adae0005038d83c3bcba16b7ae10d1a1838dc7fb855"
    ),
    "result_digest_sha256": "fbb1707d8f0cb382754be45fa950ae3ce288e6946d891c3682b5f194691d667c",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "fa9d0693334f6489c842ff89d408ca0f6e7a6ac95d990bb221bb6765b128b564"
    ),
    "parent_center_product_interval_digest_sha256": (
        "9eb38cc5d3a5a8f8837c6d71a30627cd522dd30b4800c039ab45cc2b1ccfc992"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "f27cf4c21ae59f189ba1cd9c3f7fe71a83b10abd390df1484814b30ff888e051"
    ),
    "allocation_classification_record_digest_sha256": (
        "f8451f0ea15a7b4280b88bebdce76c40722af5f094b058a7c40d8d52c4bed8a7"
    ),
}


@pytest.fixture(scope="module")
def q011cs_study() -> dict[str, Any]:
    return q011cs.run_q011cs_study()


@pytest.fixture(scope="module")
def q011cs_cycle(q011cs_study: dict[str, Any]) -> dict[str, Any]:
    return q011cs_study["cycle"]


def test_q011cs_seals_q011cr_and_all_prior_inputs(
    q011cs_cycle: dict[str, Any],
) -> None:
    sealed = q011cs_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 75
    assert sealed["direct_digest_count"] == 350
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cr"]["digests"]) == q011cs.Q011CR_DIGESTS
    assert sealed["q011cr"]["artifact_sha256"] == q011cs.Q011CR_ARTIFACT_SHA256
    assert sealed["q011cr"]["runner_sha256"] == q011cs.Q011CR_RUNNER_SHA256
    assert sealed["q011cr"]["resolved_witness_digest_sha256"] == (
        q011cs.EXPECTED_ORDINAL_SEVEN_RESOLUTION_DIGEST
    )


def test_q011cs_selects_exactly_flatten_ordinal_eight(
    q011cs_cycle: dict[str, Any],
) -> None:
    fixed = q011cs_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 8
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2, 3, 4, 5, 6, 7]
    assert selection["ordinal_four_resolution_digest_sha256"] == (
        q011cs.EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    assert selection["ordinal_five_resolution_digest_sha256"] == (
        q011cs.EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )
    assert selection["ordinal_six_resolution_digest_sha256"] == (
        q011cs.EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
    )
    assert selection["ordinal_seven_resolution_digest_sha256"] == (
        q011cs.EXPECTED_ORDINAL_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 685
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011cs.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011cs.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011cs.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011cs_reconstructs_registered_partition_and_inventory(
    q011cs_cycle: dict[str, Any],
) -> None:
    fixed = q011cs_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [0, 7],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011cs.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == (q011cs.EXPECTED_IDENTIFIER_ORDER)
    assert fixed["full_allocation_count"] == 12_096
    assert fixed["full_allocation_digest_sha256"] == q011cs.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 685
    assert fixed["compatible_allocation_digest_sha256"] == (q011cs.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 12_048
    assert fixed["parent_witness_compatible_index"] == 684
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011cs_all_exact_intervals_are_parent_identical(
    q011cs_cycle: dict[str, Any],
) -> None:
    partition = q011cs_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011cs.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011cs.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011cs_records_interval_inert_persistence(
    q011cs_cycle: dict[str, Any],
) -> None:
    assert q011cs_cycle["study_validity"] == "passed"
    assert q011cs_cycle["failed_validity_order"] == []
    assert q011cs_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cs_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cs_cycle["diagnostic_gates"].values())
    assert q011cs_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011cs_cycle["diagnostic_classification"] == q011cs.INERT_CLASSIFICATION
    assert q011cs_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cs_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 685,
    }
    partition = q011cs_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011cs_preserves_boundary_and_reproducible_digests(
    q011cs_cycle: dict[str, Any],
) -> None:
    theorem = q011cs_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_ninth_q011cb_witness"]
    assert not theorem["ninth_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 8" in q011cs_cycle["claim_boundary"]
    assert "later 44791 Q011cb refined signatures" in q011cs_cycle["claim_boundary"]
    json.dumps(q011cs_cycle, allow_nan=False)
    assert {
        name: q011cs_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011cs_cycle["result_digest_sha256"] == (
        q011cs.q011b._canonical_json_sha256(q011cs._result_digest_sections(q011cs_cycle))
    )
    assert q011cs._protocol_globals_are_restored()


def test_q011cs_study_metadata_and_optional_artifact_are_scoped(
    q011cs_study: dict[str, Any],
) -> None:
    assert q011cs_study["schema_version"] == 1
    assert q011cs_study["source"] == source_metadata()
    assert q011cs_study["study_gate"] == "passed"
    assert q011cs_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011cs_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 685
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011cs_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 8
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011cs_study, allow_nan=False)

    runner_path = Path(q011cs.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent / "artifacts" / ("q011cs_degree34_ninth_individual_partition_audit.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cs artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cs.q011b._canonical_json_sha256(q011cs._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
