from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hi_degree34_sixty_ninth_individual_partition_audit as q011hi
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "f89e194b3e162fa1e8e844556cf980d3651ca197c40397226edc19070cf53e56"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "84911a757621d76ca0d5ebaf1e9ee8f8b333edd2b7b7bcef3085c0ac188b457c"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "d68a0bf8dc563ed8cd6534a2d44f23f36084044729f62fe994627715460814c1",
    "partition_input_digest_sha256": "f499c40216a2c11d70cb435fbb724c5e12fb27fed2347c235613441f83b4dcbe",
    "allocation_audit_digest_sha256": "d7795a8a9cd159d3cdc1916c32cad870db0c68550f0fdf3173a2abaf2493b2ae",
    "result_digest_sha256": "1a16008fa0c0cd358b69a7b12da61195d3dcd18d8e49c1bb2bf334654583fe41",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "7729789d02718ee441fa0da8f3cb97b6caea7daf0ed9fc73123427fbecadf92b",
    "parent_center_product_interval_digest_sha256": "790d0ee8f1e895f344fe94531f906fb31e641c45a6744fd2bd20a503c70021d5",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "c252d6c14c23ad0598b912c916cce36a81c2d9ce8bb2f869bd5446e984ca90fb",
    "allocation_classification_record_digest_sha256": "c70986282df96dc1f8aa7e9e0fa101d7ad05680b930a074a7198292c47a3a6ed",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011hi_structure() -> dict[str, Any]:
    sealed, artifacts = q011hi._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hi._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hi_study() -> dict[str, Any]:
    return q011hi.run_q011hi_study()


@pytest.fixture(scope="module")
def q011hi_cycle(q011hi_study: dict[str, Any]) -> dict[str, Any]:
    return q011hi_study["cycle"]


def test_q011hi_seals_q011hh_and_all_prior_inputs(
    q011hi_structure: dict[str, Any],
) -> None:
    sealed = q011hi_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 195
    assert sealed["direct_digest_count"] == 890
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hh"]["digests"]) == q011hi.Q011HH_DIGESTS
    assert sealed["q011hh"]["artifact_sha256"] == q011hi.Q011HH_ARTIFACT_SHA256
    assert sealed["q011hh"]["runner_sha256"] == q011hi.Q011HH_RUNNER_SHA256
    assert sealed["q011hh"]["resolved_witness_digest_sha256"] == (
        q011hi.EXPECTED_ORDINAL_SIXTY_SEVEN_RESOLUTION_DIGEST
    )


def test_q011hi_selects_exactly_flatten_ordinal_sixty_eight(
    q011hi_structure: dict[str, Any],
) -> None:
    fixed = q011hi_structure["fixed"]
    selection = fixed["sixty_ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 68
    assert selection["selected_left_index"] == 8
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(68))
    assert selection["ordinal_sixty_seven_resolution_digest_sha256"] == (
        q011hi.EXPECTED_ORDINAL_SIXTY_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["sixty_ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [8, 1], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 1_699
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hi.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011hi.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011hi.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hi_reconstructs_registered_partition_and_inventory(
    q011hi_structure: dict[str, Any],
) -> None:
    fixed = q011hi_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [8, 1],
        [5],
        [4, 3],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 8, 1, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011hi.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011hi.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 30_240
    assert fixed["full_allocation_digest_sha256"] == q011hi.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_699
    assert q011hi_structure["compatible_count"] == 1_699
    assert fixed["compatible_allocation_digest_sha256"] == q011hi.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 8, 0, 1, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 8, 0, 1, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 30_120
    assert fixed["parent_witness_compatible_index"] == 1_698
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hi result is not sealed")
def test_q011hi_classifies_every_registered_exact_interval(
    q011hi_cycle: dict[str, Any],
) -> None:
    partition = q011hi_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_699
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_699
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_699))
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
        assert record["intersection_width_hex"] == q011hi.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011hi.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_699,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hi result is not sealed")
def test_q011hi_applies_the_registered_exclusive_stopping_rule(
    q011hi_cycle: dict[str, Any],
) -> None:
    assert q011hi_cycle["study_validity"] == "passed"
    assert q011hi_cycle["failed_validity_order"] == []
    assert q011hi_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hi_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hi_cycle["diagnostic_gates"].values())
    assert q011hi_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hi_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hi_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011hi_cycle["diagnostic_classification"] == q011hi.INERT_CLASSIFICATION
    assert not q011hi_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hi_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_ninth_q011cb_witness"],
        theorem["sixty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_ninth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hi result is not sealed")
def test_q011hi_preserves_boundary_and_reproducible_digests(
    q011hi_cycle: dict[str, Any],
) -> None:
    theorem = q011hi_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_ninth_q011cb_witness"],
        theorem["sixty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_ninth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011hh_ordinal_sixty_seven_phase_resolution_is_preserved"]
    assert theorem["q011hg_ordinal_sixty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hf_ordinal_sixty_six_phase_resolution_is_preserved"]
    assert theorem["q011he_ordinal_sixty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hd_ordinal_sixty_five_phase_resolution_is_preserved"]
    assert theorem["q011hc_ordinal_sixty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hb_ordinal_sixty_four_phase_resolution_is_preserved"]
    assert theorem["q011ha_ordinal_sixty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gz_ordinal_sixty_three_phase_resolution_is_preserved"]
    assert theorem["q011gy_ordinal_sixty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gx_ordinal_sixty_two_phase_resolution_is_preserved"]
    assert theorem["q011gw_ordinal_sixty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gv_ordinal_sixty_one_phase_resolution_is_preserved"]
    assert theorem["q011gu_ordinal_sixty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gt_ordinal_sixty_phase_resolution_is_preserved"]
    assert theorem["q011gs_ordinal_sixty_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 68" in q011hi_cycle["claim_boundary"]
    assert "ordinals 0 through 67" in q011hi_cycle["claim_boundary"]
    assert "later 44731 Q011cb refined signatures" in q011hi_cycle["claim_boundary"]
    assert "Q011hj" in q011hi_cycle["next_change"]
    json.dumps(q011hi_cycle, allow_nan=False)
    assert {name: q011hi_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hi_cycle["result_digest_sha256"] == (
        q011hi.q011b._canonical_json_sha256(q011hi._result_digest_sections(q011hi_cycle))
    )
    assert q011hi._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hi result is not sealed")
def test_q011hi_study_metadata_and_optional_artifact_are_scoped(
    q011hi_study: dict[str, Any],
) -> None:
    assert q011hi_study["schema_version"] == 1
    assert q011hi_study["source"] == source_metadata()
    assert q011hi_study["study_gate"] == "passed"
    assert q011hi_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011hi_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_699
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hi_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 68
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hi_study, allow_nan=False)

    runner_path = Path(q011hi.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hi_degree34_sixty_ninth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hi artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hi_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hi.q011b._canonical_json_sha256(q011hi._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
