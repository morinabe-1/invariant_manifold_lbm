from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fo_degree34_forty_sixth_individual_partition_audit as q011fo
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "fa621c675c04f278a578f4f790b2db3557df1e55bc62e989e9a18a523a4b018e"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "801a48b9151f722d8f6520227620b2e9294f11c585faa593b89a1a891c6bd068"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "7c37b2f97768c34a2104bb9b257a826e28d098091d7ebc555b806a9b6b65213b",
    "partition_input_digest_sha256": "c36705fa7510b8f203c8dac2e593ee4105a9be12726d7de488cf88519220aa03",
    "allocation_audit_digest_sha256": "70a1178ab6fa6d96c0def2a0a39d8eea88724c334714754b43d07854bb80bea4",
    "result_digest_sha256": "f4505596c9d708ac2bcd4864d1ca8aa58aaef3a7b8107cf7296465f7aba0ef95",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "8edba1408f3dba0f7979d60865ebf1ecb436a4968bbabd9be29ec42627193c35"
    ),
    "parent_center_product_interval_digest_sha256": (
        "47d3539b956bfe7e869993e2246fe49f2491ff3b101fef978171c09b75b37342"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "03ec813cf4725959aef4cf80a01743f4fc80856e9b56bd84fd0bda87f03500ed"
    ),
    "allocation_classification_record_digest_sha256": (
        "244617ac6f4a8458099b5975ecf426c00bcc937e3b65afa1c585bbf65faec4d0"
    ),
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011fo_structure() -> dict[str, Any]:
    sealed, artifacts = q011fo._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011fo._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011fo_study() -> dict[str, Any]:
    return q011fo.run_q011fo_study()


@pytest.fixture(scope="module")
def q011fo_cycle(q011fo_study: dict[str, Any]) -> dict[str, Any]:
    return q011fo_study["cycle"]


def test_q011fo_seals_q011fn_and_all_prior_inputs(
    q011fo_structure: dict[str, Any],
) -> None:
    sealed = q011fo_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 149
    assert sealed["direct_digest_count"] == 683
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fn"]["digests"]) == q011fo.Q011FN_DIGESTS
    assert sealed["q011fn"]["artifact_sha256"] == q011fo.Q011FN_ARTIFACT_SHA256
    assert sealed["q011fn"]["runner_sha256"] == q011fo.Q011FN_RUNNER_SHA256
    assert sealed["q011fn"]["resolved_witness_digest_sha256"] == (
        q011fo.EXPECTED_ORDINAL_FORTY_FOUR_RESOLUTION_DIGEST
    )


def test_q011fo_selects_exactly_flatten_ordinal_forty_five(
    q011fo_structure: dict[str, Any],
) -> None:
    fixed = q011fo_structure["fixed"]
    selection = fixed["forty_sixth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 45
    assert selection["selected_left_index"] == 5
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(45))
    assert selection["ordinal_forty_four_resolution_digest_sha256"] == (
        q011fo.EXPECTED_ORDINAL_FORTY_FOUR_RESOLUTION_DIGEST
    )
    parent = selection["forty_sixth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [5, 4], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_553
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fo.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fo.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fo.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fo_reconstructs_registered_partition_and_inventory(
    q011fo_structure: dict[str, Any],
) -> None:
    fixed = q011fo_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [5, 4],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 5, 4, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fo.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fo.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 45_360
    assert fixed["full_allocation_digest_sha256"] == q011fo.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_553
    assert q011fo_structure["compatible_count"] == 2_553
    assert fixed["compatible_allocation_digest_sha256"] == (q011fo.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 5, 0, 4, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 5, 0, 4, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 45_252
    assert fixed["parent_witness_compatible_index"] == 2_552
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fo result is not sealed")
def test_q011fo_classifies_every_registered_exact_interval(
    q011fo_cycle: dict[str, Any],
) -> None:
    partition = q011fo_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_553
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_553
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_553))
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
        assert record["intersection_width_hex"] == q011fo.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fo.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_553,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fo result is not sealed")
def test_q011fo_applies_the_registered_exclusive_stopping_rule(
    q011fo_cycle: dict[str, Any],
) -> None:
    assert q011fo_cycle["study_validity"] == "passed"
    assert q011fo_cycle["failed_validity_order"] == []
    assert q011fo_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fo_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fo_cycle["diagnostic_gates"].values())
    assert q011fo_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fo_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fo_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fo_cycle["diagnostic_classification"] == q011fo.INERT_CLASSIFICATION
    assert not q011fo_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fo_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_sixth_q011cb_witness"],
        theorem["forty_sixth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_sixth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fo result is not sealed")
def test_q011fo_preserves_boundary_and_reproducible_digests(
    q011fo_cycle: dict[str, Any],
) -> None:
    theorem = q011fo_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_sixth_q011cb_witness"],
        theorem["forty_sixth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_sixth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 45" in q011fo_cycle["claim_boundary"]
    assert "ordinals 0 through 44" in q011fo_cycle["claim_boundary"]
    assert "later 44754 Q011cb refined signatures" in q011fo_cycle["claim_boundary"]
    assert "Q011fp" in q011fo_cycle["next_change"]
    json.dumps(q011fo_cycle, allow_nan=False)
    assert {name: q011fo_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fo_cycle["result_digest_sha256"] == (
        q011fo.q011b._canonical_json_sha256(q011fo._result_digest_sections(q011fo_cycle))
    )
    assert q011fo._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fo result is not sealed")
def test_q011fo_study_metadata_and_optional_artifact_are_scoped(
    q011fo_study: dict[str, Any],
) -> None:
    assert q011fo_study["schema_version"] == 1
    assert q011fo_study["source"] == source_metadata()
    assert q011fo_study["study_gate"] == "passed"
    assert q011fo_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fo_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_553
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fo_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 45
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fo_study, allow_nan=False)

    runner_path = Path(q011fo.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fo_degree34_forty_sixth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fo artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fo_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fo.q011b._canonical_json_sha256(q011fo._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
