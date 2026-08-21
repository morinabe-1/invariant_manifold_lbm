from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gg_degree34_fifty_fifth_individual_partition_audit as q011gg
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
def q011gg_structure() -> dict[str, Any]:
    sealed, artifacts = q011gg._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011gg._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011gg_study() -> dict[str, Any]:
    return q011gg.run_q011gg_study()


@pytest.fixture(scope="module")
def q011gg_cycle(q011gg_study: dict[str, Any]) -> dict[str, Any]:
    return q011gg_study["cycle"]


def test_q011gg_seals_q011gf_and_all_prior_inputs(
    q011gg_structure: dict[str, Any],
) -> None:
    sealed = q011gg_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 167
    assert sealed["direct_digest_count"] == 764
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gf"]["digests"]) == q011gg.Q011GF_DIGESTS
    assert sealed["q011gf"]["artifact_sha256"] == q011gg.Q011GF_ARTIFACT_SHA256
    assert sealed["q011gf"]["runner_sha256"] == q011gg.Q011GF_RUNNER_SHA256
    assert sealed["q011gf"]["resolved_witness_digest_sha256"] == (
        q011gg.EXPECTED_ORDINAL_FIFTY_THREE_RESOLUTION_DIGEST
    )


def test_q011gg_selects_exactly_flatten_ordinal_fifty_four(
    q011gg_structure: dict[str, Any],
) -> None:
    fixed = q011gg_structure["fixed"]
    selection = fixed["fifty_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 54
    assert selection["selected_left_index"] == 6
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(54))
    assert selection["ordinal_fifty_three_resolution_digest_sha256"] == (
        q011gg.EXPECTED_ORDINAL_FIFTY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["fifty_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [6, 3], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_854
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011gg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011gg.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011gg.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011gg_reconstructs_registered_partition_and_inventory(
    q011gg_structure: dict[str, Any],
) -> None:
    fixed = q011gg_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [6, 3],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 6, 3, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011gg.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011gg.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 32_928
    assert fixed["full_allocation_digest_sha256"] == q011gg.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_854
    assert q011gg_structure["compatible_count"] == 1_854
    assert fixed["compatible_allocation_digest_sha256"] == (q011gg.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 6, 0, 3, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 6, 0, 3, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 32_844
    assert fixed["parent_witness_compatible_index"] == 1_853
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gg result is not sealed")
def test_q011gg_classifies_every_registered_exact_interval(
    q011gg_cycle: dict[str, Any],
) -> None:
    partition = q011gg_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_854
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_854
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_854))
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
        assert record["intersection_width_hex"] == q011gg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011gg.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_854,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gg result is not sealed")
def test_q011gg_applies_the_registered_exclusive_stopping_rule(
    q011gg_cycle: dict[str, Any],
) -> None:
    assert q011gg_cycle["study_validity"] == "passed"
    assert q011gg_cycle["failed_validity_order"] == []
    assert q011gg_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011gg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gg_cycle["diagnostic_gates"].values())
    assert q011gg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gg_cycle["actual_resonance_outcome"] == "not_established"
    assert q011gg_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011gg_cycle["diagnostic_classification"] == q011gg.INERT_CLASSIFICATION
    assert not q011gg_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011gg_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fifty_fifth_q011cb_witness"],
        theorem["fifty_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fifty_fifth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gg result is not sealed")
def test_q011gg_preserves_boundary_and_reproducible_digests(
    q011gg_cycle: dict[str, Any],
) -> None:
    theorem = q011gg_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fifty_fifth_q011cb_witness"],
        theorem["fifty_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fifty_fifth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011gf_ordinal_fifty_three_phase_resolution_is_preserved"]
    assert theorem["q011ge_ordinal_fifty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gd_ordinal_fifty_two_phase_resolution_is_preserved"]
    assert theorem["q011gc_ordinal_fifty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gb_ordinal_fifty_one_phase_resolution_is_preserved"]
    assert theorem["q011ga_ordinal_fifty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fz_ordinal_fifty_phase_resolution_is_preserved"]
    assert theorem["q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fx_ordinal_forty_nine_phase_resolution_is_preserved"]
    assert theorem["q011fw_ordinal_forty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fv_ordinal_forty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ft_ordinal_forty_seven_phase_resolution_is_preserved"]
    assert theorem["q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fr_ordinal_forty_six_phase_resolution_is_preserved"]
    assert theorem["q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fp_ordinal_forty_five_phase_resolution_is_preserved"]
    assert theorem["q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fn_ordinal_forty_four_phase_resolution_is_preserved"]
    assert theorem["q011fm_ordinal_forty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fl_ordinal_forty_three_phase_resolution_is_preserved"]
    assert theorem["q011fk_ordinal_forty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fj_ordinal_forty_two_phase_resolution_is_preserved"]
    assert theorem["q011fi_ordinal_forty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fh_ordinal_forty_one_phase_resolution_is_preserved"]
    assert theorem["q011fg_ordinal_forty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ff_ordinal_forty_phase_resolution_is_preserved"]
    assert theorem["q011fe_ordinal_forty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fd_ordinal_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fb_ordinal_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ez_ordinal_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ex_ordinal_thirty_six_phase_resolution_is_preserved"]
    assert theorem["q011ew_ordinal_thirty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ev_ordinal_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011et_ordinal_thirty_four_phase_resolution_is_preserved"]
    assert theorem["q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011er_ordinal_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 54" in q011gg_cycle["claim_boundary"]
    assert "ordinals 0 through 53" in q011gg_cycle["claim_boundary"]
    assert "later 44745 Q011cb refined signatures" in q011gg_cycle["claim_boundary"]
    assert "Q011gh" in q011gg_cycle["next_change"]
    json.dumps(q011gg_cycle, allow_nan=False)
    assert {name: q011gg_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011gg_cycle["result_digest_sha256"] == (
        q011gg.q011b._canonical_json_sha256(q011gg._result_digest_sections(q011gg_cycle))
    )
    assert q011gg._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gg result is not sealed")
def test_q011gg_study_metadata_and_optional_artifact_are_scoped(
    q011gg_study: dict[str, Any],
) -> None:
    assert q011gg_study["schema_version"] == 1
    assert q011gg_study["source"] == source_metadata()
    assert q011gg_study["study_gate"] == "passed"
    assert q011gg_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011gg_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_854
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gg_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 54
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gg_study, allow_nan=False)

    runner_path = Path(q011gg.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gg_degree34_fifty_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gg_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gg.q011b._canonical_json_sha256(q011gg._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
