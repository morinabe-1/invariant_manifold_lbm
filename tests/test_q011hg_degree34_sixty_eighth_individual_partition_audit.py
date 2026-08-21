from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hg_degree34_sixty_eighth_individual_partition_audit as q011hg
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
def q011hg_structure() -> dict[str, Any]:
    sealed, artifacts = q011hg._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hg._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hg_study() -> dict[str, Any]:
    return q011hg.run_q011hg_study()


@pytest.fixture(scope="module")
def q011hg_cycle(q011hg_study: dict[str, Any]) -> dict[str, Any]:
    return q011hg_study["cycle"]


def test_q011hg_seals_q011hf_and_all_prior_inputs(
    q011hg_structure: dict[str, Any],
) -> None:
    sealed = q011hg_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 193
    assert sealed["direct_digest_count"] == 881
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hf"]["digests"]) == q011hg.Q011HF_DIGESTS
    assert sealed["q011hf"]["artifact_sha256"] == q011hg.Q011HF_ARTIFACT_SHA256
    assert sealed["q011hf"]["runner_sha256"] == q011hg.Q011HF_RUNNER_SHA256
    assert sealed["q011hf"]["resolved_witness_digest_sha256"] == (
        q011hg.EXPECTED_ORDINAL_SIXTY_SIX_RESOLUTION_DIGEST
    )


def test_q011hg_selects_exactly_flatten_ordinal_sixty_seven(
    q011hg_structure: dict[str, Any],
) -> None:
    fixed = q011hg_structure["fixed"]
    selection = fixed["sixty_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 67
    assert selection["selected_left_index"] == 8
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(67))
    assert selection["ordinal_sixty_six_resolution_digest_sha256"] == (
        q011hg.EXPECTED_ORDINAL_SIXTY_SIX_RESOLUTION_DIGEST
    )
    parent = selection["sixty_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [8, 1], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 1_699
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011hg.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011hg.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hg_reconstructs_registered_partition_and_inventory(
    q011hg_structure: dict[str, Any],
) -> None:
    fixed = q011hg_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [8, 1],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 8, 1, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011hg.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011hg.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 30_240
    assert fixed["full_allocation_digest_sha256"] == q011hg.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_699
    assert q011hg_structure["compatible_count"] == 1_699
    assert fixed["compatible_allocation_digest_sha256"] == q011hg.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 8, 0, 1, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 8, 0, 1, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 30_120
    assert fixed["parent_witness_compatible_index"] == 1_698
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hg result is not sealed")
def test_q011hg_classifies_every_registered_exact_interval(
    q011hg_cycle: dict[str, Any],
) -> None:
    partition = q011hg_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == q011hg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011hg.EXPECTED_PARENT_CENTER_GAP_HEX
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hg result is not sealed")
def test_q011hg_applies_the_registered_exclusive_stopping_rule(
    q011hg_cycle: dict[str, Any],
) -> None:
    assert q011hg_cycle["study_validity"] == "passed"
    assert q011hg_cycle["failed_validity_order"] == []
    assert q011hg_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hg_cycle["diagnostic_gates"].values())
    assert q011hg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hg_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hg_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011hg_cycle["diagnostic_classification"] == q011hg.INERT_CLASSIFICATION
    assert not q011hg_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hg_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_eighth_q011cb_witness"],
        theorem["sixty_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_eighth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hg result is not sealed")
def test_q011hg_preserves_boundary_and_reproducible_digests(
    q011hg_cycle: dict[str, Any],
) -> None:
    theorem = q011hg_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_sixty_eighth_q011cb_witness"],
        theorem["sixty_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_sixty_eighth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 67" in q011hg_cycle["claim_boundary"]
    assert "ordinals 0 through 66" in q011hg_cycle["claim_boundary"]
    assert "later 44732 Q011cb refined signatures" in q011hg_cycle["claim_boundary"]
    assert "Q011hh" in q011hg_cycle["next_change"]
    json.dumps(q011hg_cycle, allow_nan=False)
    assert {name: q011hg_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hg_cycle["result_digest_sha256"] == (
        q011hg.q011b._canonical_json_sha256(q011hg._result_digest_sections(q011hg_cycle))
    )
    assert q011hg._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hg result is not sealed")
def test_q011hg_study_metadata_and_optional_artifact_are_scoped(
    q011hg_study: dict[str, Any],
) -> None:
    assert q011hg_study["schema_version"] == 1
    assert q011hg_study["source"] == source_metadata()
    assert q011hg_study["study_gate"] == "passed"
    assert q011hg_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011hg_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_699
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hg_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 67
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hg_study, allow_nan=False)

    runner_path = Path(q011hg.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hg_degree34_sixty_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hg_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hg.q011b._canonical_json_sha256(q011hg._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
