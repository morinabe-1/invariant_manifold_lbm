from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fq_degree34_forty_seventh_individual_partition_audit as q011fq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "1e0f712562cc3daf104a345fe43361d9266007ef9db91c45793fa4d5715fe486"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "771ffef1ceb876752322941823a8c58888f464f948958f11cb12d7c4f79a9620"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "ebedd94cadee88b6acbcbc0c620778ed316e7fdccc9a65ed567541dc66f563cb",
    "partition_input_digest_sha256": "e9c5a1b86679a185d01cdf58c01f3af570ac4cb02bc564fe357e88510dc5fae2",
    "allocation_audit_digest_sha256": "99a4ca238b57c93d8e367074e57a5b87f45aed0a407cce95b3c3a389e60bffc7",
    "result_digest_sha256": "c73d039fb94c41967424a4c7004fb7f83b3ee2b08b7cfe82053daba7d65f360f",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "bf2aa37adef357fafd3713777739db1749a784674e2a7b119b894828a5655f04"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c027465888cea2e88d5ef97885822e40b0b28733f0edac74d592c2886240ea20"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "71b133757273675a849b76dbc45f0d7a70a6348619d47ddb3124207e87c4950c"
    ),
    "allocation_classification_record_digest_sha256": (
        "72e751715f581798342d0cfa046b2f5bd6af89de06163bd380f4045f7d582f04"
    ),
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011fq_structure() -> dict[str, Any]:
    sealed, artifacts = q011fq._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011fq._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011fq_study() -> dict[str, Any]:
    return q011fq.run_q011fq_study()


@pytest.fixture(scope="module")
def q011fq_cycle(q011fq_study: dict[str, Any]) -> dict[str, Any]:
    return q011fq_study["cycle"]


def test_q011fq_seals_q011fp_and_all_prior_inputs(
    q011fq_structure: dict[str, Any],
) -> None:
    sealed = q011fq_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 151
    assert sealed["direct_digest_count"] == 692
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fp"]["digests"]) == q011fq.Q011FP_DIGESTS
    assert sealed["q011fp"]["artifact_sha256"] == q011fq.Q011FP_ARTIFACT_SHA256
    assert sealed["q011fp"]["runner_sha256"] == q011fq.Q011FP_RUNNER_SHA256
    assert sealed["q011fp"]["resolved_witness_digest_sha256"] == (
        q011fq.EXPECTED_ORDINAL_FORTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011fq_selects_exactly_flatten_ordinal_forty_six(
    q011fq_structure: dict[str, Any],
) -> None:
    fixed = q011fq_structure["fixed"]
    selection = fixed["forty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 46
    assert selection["selected_left_index"] == 5
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(46))
    assert selection["ordinal_forty_five_resolution_digest_sha256"] == (
        q011fq.EXPECTED_ORDINAL_FORTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["forty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [5, 4], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_986
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fq_reconstructs_registered_partition_and_inventory(
    q011fq_structure: dict[str, Any],
) -> None:
    fixed = q011fq_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [5, 4],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 5, 4, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fq.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fq.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 35_280
    assert fixed["full_allocation_digest_sha256"] == q011fq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_986
    assert q011fq_structure["compatible_count"] == 1_986
    assert fixed["compatible_allocation_digest_sha256"] == (q011fq.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 5, 0, 4, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 5, 0, 4, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 35_196
    assert fixed["parent_witness_compatible_index"] == 1_985
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fq result is not sealed")
def test_q011fq_classifies_every_registered_exact_interval(
    q011fq_cycle: dict[str, Any],
) -> None:
    partition = q011fq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_986
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_986
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_986))
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
        assert record["intersection_width_hex"] == q011fq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fq.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_986,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fq result is not sealed")
def test_q011fq_applies_the_registered_exclusive_stopping_rule(
    q011fq_cycle: dict[str, Any],
) -> None:
    assert q011fq_cycle["study_validity"] == "passed"
    assert q011fq_cycle["failed_validity_order"] == []
    assert q011fq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fq_cycle["diagnostic_gates"].values())
    assert q011fq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fq_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fq_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fq_cycle["diagnostic_classification"] == q011fq.INERT_CLASSIFICATION
    assert not q011fq_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fq_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_seventh_q011cb_witness"],
        theorem["forty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_seventh_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fq result is not sealed")
def test_q011fq_preserves_boundary_and_reproducible_digests(
    q011fq_cycle: dict[str, Any],
) -> None:
    theorem = q011fq_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_seventh_q011cb_witness"],
        theorem["forty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_seventh_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 46" in q011fq_cycle["claim_boundary"]
    assert "ordinals 0 through 45" in q011fq_cycle["claim_boundary"]
    assert "later 44753 Q011cb refined signatures" in q011fq_cycle["claim_boundary"]
    assert "Q011fr" in q011fq_cycle["next_change"]
    json.dumps(q011fq_cycle, allow_nan=False)
    assert {name: q011fq_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fq_cycle["result_digest_sha256"] == (
        q011fq.q011b._canonical_json_sha256(q011fq._result_digest_sections(q011fq_cycle))
    )
    assert q011fq._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fq result is not sealed")
def test_q011fq_study_metadata_and_optional_artifact_are_scoped(
    q011fq_study: dict[str, Any],
) -> None:
    assert q011fq_study["schema_version"] == 1
    assert q011fq_study["source"] == source_metadata()
    assert q011fq_study["study_gate"] == "passed"
    assert q011fq_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_986
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 46
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fq_study, allow_nan=False)

    runner_path = Path(q011fq.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fq_degree34_forty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fq_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fq.q011b._canonical_json_sha256(q011fq._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
