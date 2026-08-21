from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hc_degree34_sixty_sixth_individual_partition_audit as q011hc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = None
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = None
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011hc_structure() -> dict[str, Any]:
    sealed, artifacts = q011hc._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hc._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hc_study() -> dict[str, Any]:
    return q011hc.run_q011hc_study()


@pytest.fixture(scope="module")
def q011hc_cycle(q011hc_study: dict[str, Any]) -> dict[str, Any]:
    return q011hc_study["cycle"]


def test_q011hc_seals_q011hb_and_all_prior_inputs(
    q011hc_structure: dict[str, Any],
) -> None:
    sealed = q011hc_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 189
    assert sealed["direct_digest_count"] == 863
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hb"]["digests"]) == q011hc.Q011HB_DIGESTS
    assert sealed["q011hb"]["artifact_sha256"] == q011hc.Q011HB_ARTIFACT_SHA256
    assert sealed["q011hb"]["runner_sha256"] == q011hc.Q011HB_RUNNER_SHA256
    assert sealed["q011hb"]["resolved_witness_digest_sha256"] == (
        q011hc.EXPECTED_ORDINAL_SIXTY_FOUR_RESOLUTION_DIGEST
    )


def test_q011hc_selects_exactly_flatten_ordinal_sixty_five(
    q011hc_structure: dict[str, Any],
) -> None:
    fixed = q011hc_structure["fixed"]
    selection = fixed["sixty_sixth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 65
    assert selection["selected_left_index"] == 8
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(65))
    assert selection["ordinal_sixty_four_resolution_digest_sha256"] == (
        q011hc.EXPECTED_ORDINAL_SIXTY_FOUR_RESOLUTION_DIGEST
    )
    parent = selection["sixty_sixth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [8, 1], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 1_194
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011hc.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011hc.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hc_reconstructs_registered_partition_and_inventory(
    q011hc_structure: dict[str, Any],
) -> None:
    fixed = q011hc_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [8, 1],
        [5],
        [1, 6],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 8, 1, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011hc.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011hc.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 21_168
    assert fixed["full_allocation_digest_sha256"] == q011hc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_194
    assert q011hc_structure["compatible_count"] == 1_194
    assert fixed["compatible_allocation_digest_sha256"] == q011hc.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 8, 0, 1, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 8, 0, 1, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 21_084
    assert fixed["parent_witness_compatible_index"] == 1_193
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hc result is not sealed")
def test_q011hc_classifies_every_registered_exact_interval(
    q011hc_cycle: dict[str, Any],
) -> None:
    partition = q011hc_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_194
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_194
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_194))
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
        assert record["intersection_width_hex"] == q011hc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011hc.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_194,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hc result is not sealed")
def test_q011hc_applies_the_registered_exclusive_stopping_rule(
    q011hc_cycle: dict[str, Any],
) -> None:
    assert q011hc_cycle["study_validity"] == "passed"
    assert q011hc_cycle["failed_validity_order"] == []
    assert q011hc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hc_cycle["diagnostic_gates"].values())
    assert q011hc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hc_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hc_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011hc_cycle["diagnostic_classification"] == q011hc.INERT_CLASSIFICATION
    assert not q011hc_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hc_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_sixth_q011cb_witness"],
        theorem["sixty_sixth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_sixth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hc result is not sealed")
def test_q011hc_preserves_boundary_and_reproducible_digests(
    q011hc_cycle: dict[str, Any],
) -> None:
    theorem = q011hc_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_sixth_q011cb_witness"],
        theorem["sixty_sixth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_sixth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 65" in q011hc_cycle["claim_boundary"]
    assert "ordinals 0 through 64" in q011hc_cycle["claim_boundary"]
    assert "later 44734 Q011cb refined signatures" in q011hc_cycle["claim_boundary"]
    assert "Q011hd" in q011hc_cycle["next_change"]
    json.dumps(q011hc_cycle, allow_nan=False)
    assert {name: q011hc_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hc_cycle["result_digest_sha256"] == (
        q011hc.q011b._canonical_json_sha256(q011hc._result_digest_sections(q011hc_cycle))
    )
    assert q011hc._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hc result is not sealed")
def test_q011hc_study_metadata_and_optional_artifact_are_scoped(
    q011hc_study: dict[str, Any],
) -> None:
    assert q011hc_study["schema_version"] == 1
    assert q011hc_study["source"] == source_metadata()
    assert q011hc_study["study_gate"] == "passed"
    assert q011hc_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011hc_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_194
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 65
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hc_study, allow_nan=False)

    runner_path = Path(q011hc.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hc_degree34_sixty_sixth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hc_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hc.q011b._canonical_json_sha256(q011hc._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
