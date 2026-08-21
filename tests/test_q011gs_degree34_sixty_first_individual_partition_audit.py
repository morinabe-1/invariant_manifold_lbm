from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gs_degree34_sixty_first_individual_partition_audit as q011gs
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "958ce4daaeaed447807b52477171db322fd77149d4fbcdbd3833434aecea0c67"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "bb9842899415182b79c860393d3814c57274b108e53cabb47b0c062d6401e8c9"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "488a9e7f9919ac6e872351a6999b850173200ad63183d93f1bb81967d9027a55",
    "partition_input_digest_sha256": "2944ed4de87ad59d33c11562e31bec13cd02a2e73783a6640a6209a355b2155c",
    "allocation_audit_digest_sha256": "44a783bf60bccc24c095b2efb2203c040c5de816037da5274038501972dce666",
    "result_digest_sha256": "6ef48e6cbea1a145abcd62f142a4c3303ff677436f5b123b1fed429b27df2772",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "e67086ef32cb0322a0d4063b40ffb8fa3cc47da03b379dbfc4bea175a37ec2a8",
    "parent_center_product_interval_digest_sha256": "32c8ef63f713de671e902187e4840e20aa182ba9426ac43952eb8994ef20486d",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "30bbecbc45a4e2c1f461cd29971cd4487113a37a64b8c707994139edc2e069af",
    "allocation_classification_record_digest_sha256": "807e717780e477f852d3e578c0a8e0268ac72fab2a1c77c8ba2ce96d6a57374f",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011gs_structure() -> dict[str, Any]:
    sealed, artifacts = q011gs._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011gs._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011gs_study() -> dict[str, Any]:
    return q011gs.run_q011gs_study()


@pytest.fixture(scope="module")
def q011gs_cycle(q011gs_study: dict[str, Any]) -> dict[str, Any]:
    return q011gs_study["cycle"]


def test_q011gs_seals_q011gr_and_all_prior_inputs(
    q011gs_structure: dict[str, Any],
) -> None:
    sealed = q011gs_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 179
    assert sealed["direct_digest_count"] == 818
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gr"]["digests"]) == q011gs.Q011GR_DIGESTS
    assert sealed["q011gr"]["artifact_sha256"] == q011gs.Q011GR_ARTIFACT_SHA256
    assert sealed["q011gr"]["runner_sha256"] == q011gs.Q011GR_RUNNER_SHA256
    assert sealed["q011gr"]["resolved_witness_digest_sha256"] == (
        q011gs.EXPECTED_ORDINAL_FIFTY_NINE_RESOLUTION_DIGEST
    )


def test_q011gs_selects_exactly_flatten_ordinal_sixty(
    q011gs_structure: dict[str, Any],
) -> None:
    fixed = q011gs_structure["fixed"]
    selection = fixed["sixty_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 60
    assert selection["selected_left_index"] == 7
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(60))
    assert selection["ordinal_fifty_nine_resolution_digest_sha256"] == (
        q011gs.EXPECTED_ORDINAL_FIFTY_NINE_RESOLUTION_DIGEST
    )
    parent = selection["sixty_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [7, 2], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 2_266
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011gs.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011gs.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011gs.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011gs_reconstructs_registered_partition_and_inventory(
    q011gs_structure: dict[str, Any],
) -> None:
    fixed = q011gs_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [7, 2],
        [5],
        [4, 3],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 7, 2, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011gs.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011gs.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 40_320
    assert fixed["full_allocation_digest_sha256"] == q011gs.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_266
    assert q011gs_structure["compatible_count"] == 2_266
    assert fixed["compatible_allocation_digest_sha256"] == q011gs.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 7, 0, 2, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 7, 0, 2, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 40_200
    assert fixed["parent_witness_compatible_index"] == 2_265
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gs result is not sealed")
def test_q011gs_classifies_every_registered_exact_interval(
    q011gs_cycle: dict[str, Any],
) -> None:
    partition = q011gs_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_266
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_266
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_266))
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
        assert record["intersection_width_hex"] == q011gs.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011gs.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_266,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gs result is not sealed")
def test_q011gs_applies_the_registered_exclusive_stopping_rule(
    q011gs_cycle: dict[str, Any],
) -> None:
    assert q011gs_cycle["study_validity"] == "passed"
    assert q011gs_cycle["failed_validity_order"] == []
    assert q011gs_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011gs_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gs_cycle["diagnostic_gates"].values())
    assert q011gs_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gs_cycle["actual_resonance_outcome"] == "not_established"
    assert q011gs_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011gs_cycle["diagnostic_classification"] == q011gs.INERT_CLASSIFICATION
    assert not q011gs_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011gs_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_first_q011cb_witness"],
        theorem["sixty_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_first_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gs result is not sealed")
def test_q011gs_preserves_boundary_and_reproducible_digests(
    q011gs_cycle: dict[str, Any],
) -> None:
    theorem = q011gs_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_first_q011cb_witness"],
        theorem["sixty_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_first_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011gr_ordinal_fifty_nine_phase_resolution_is_preserved"]
    assert theorem["q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
    assert theorem["q011go_ordinal_fifty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 60" in q011gs_cycle["claim_boundary"]
    assert "ordinals 0 through 59" in q011gs_cycle["claim_boundary"]
    assert "later 44739 Q011cb refined signatures" in q011gs_cycle["claim_boundary"]
    assert "Q011gt" in q011gs_cycle["next_change"]
    json.dumps(q011gs_cycle, allow_nan=False)
    assert {name: q011gs_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011gs_cycle["result_digest_sha256"] == (
        q011gs.q011b._canonical_json_sha256(q011gs._result_digest_sections(q011gs_cycle))
    )
    assert q011gs._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gs result is not sealed")
def test_q011gs_study_metadata_and_optional_artifact_are_scoped(
    q011gs_study: dict[str, Any],
) -> None:
    assert q011gs_study["schema_version"] == 1
    assert q011gs_study["source"] == source_metadata()
    assert q011gs_study["study_gate"] == "passed"
    assert q011gs_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011gs_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_266
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gs_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 60
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gs_study, allow_nan=False)

    runner_path = Path(q011gs.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gs_degree34_sixty_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gs artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gs_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gs.q011b._canonical_json_sha256(q011gs._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
