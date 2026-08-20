from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fi_degree34_forty_third_individual_partition_audit as q011fi
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "01c4adfa9fbb4c8bceab2b7565a39051bd03f18abbfc6289fdb9a77154c646ac"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "c2ea4d33ecabb1b9997c33cd521046a6c3f304161e36fde3385d546681f783f3"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "0c127965dbbdd8bfbe3cec68bcbff6d44dcf8bc9a7d8ef9abfd6abf87b3337e9",
    "partition_input_digest_sha256": "6464f953f8a459e45f143edc40c37d67e3afe72d92dd75f0162283521e817ad7",
    "allocation_audit_digest_sha256": "7c6ce89361136c904acf3564a713817d4af5d8fa649ad30942b4480ee0433fa9",
    "result_digest_sha256": "708275e4c34e2c6c818f7c945c3e8cda15d0c6be0e2474660b2e86890f182453",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "09676abfc4c27aa18fb2ab0e9d9a76a8582a34dd992c5e99236a37ad491166f0"
    ),
    "parent_center_product_interval_digest_sha256": (
        "b8bd53f203d4bae560d68d5d76d4f07355688b13a99f5d37f64ef503a0e848d0"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "2a7d88c28609ae1048a8725bbd3daa649c25a8b89c65def54695e468585f4c45"
    ),
    "allocation_classification_record_digest_sha256": (
        "9216c50b1678158d0e7cc47663397845380996ad2542f67f73ecace30e8a862e"
    ),
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011fi_structure() -> dict[str, Any]:
    sealed, artifacts = q011fi._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011fi._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011fi_study() -> dict[str, Any]:
    return q011fi.run_q011fi_study()


@pytest.fixture(scope="module")
def q011fi_cycle(q011fi_study: dict[str, Any]) -> dict[str, Any]:
    return q011fi_study["cycle"]


def test_q011fi_seals_q011fh_and_all_prior_inputs(
    q011fi_structure: dict[str, Any],
) -> None:
    sealed = q011fi_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 143
    assert sealed["direct_digest_count"] == 656
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fh"]["digests"]) == q011fi.Q011FH_DIGESTS
    assert sealed["q011fh"]["artifact_sha256"] == q011fi.Q011FH_ARTIFACT_SHA256
    assert sealed["q011fh"]["runner_sha256"] == q011fi.Q011FH_RUNNER_SHA256
    assert sealed["q011fh"]["resolved_witness_digest_sha256"] == (
        q011fi.EXPECTED_ORDINAL_FORTY_ONE_RESOLUTION_DIGEST
    )


def test_q011fi_selects_exactly_flatten_ordinal_forty_two(
    q011fi_structure: dict[str, Any],
) -> None:
    fixed = q011fi_structure["fixed"]
    selection = fixed["forty_third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 42
    assert selection["selected_left_index"] == 5
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(42))
    assert selection["ordinal_forty_one_resolution_digest_sha256"] == (
        q011fi.EXPECTED_ORDINAL_FORTY_ONE_RESOLUTION_DIGEST
    )
    parent = selection["forty_third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [5, 4], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 2_553
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fi.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fi.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fi.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fi_reconstructs_registered_partition_and_inventory(
    q011fi_structure: dict[str, Any],
) -> None:
    fixed = q011fi_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [5, 4],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 5, 4, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fi.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fi.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 45_360
    assert fixed["full_allocation_digest_sha256"] == q011fi.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_553
    assert q011fi_structure["compatible_count"] == 2_553
    assert fixed["compatible_allocation_digest_sha256"] == (q011fi.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 5, 0, 4, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 5, 0, 4, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 45_252
    assert fixed["parent_witness_compatible_index"] == 2_552
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fi result is not sealed")
def test_q011fi_classifies_every_registered_exact_interval(
    q011fi_cycle: dict[str, Any],
) -> None:
    partition = q011fi_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == q011fi.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fi.EXPECTED_PARENT_CENTER_GAP_HEX
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fi result is not sealed")
def test_q011fi_applies_the_registered_exclusive_stopping_rule(
    q011fi_cycle: dict[str, Any],
) -> None:
    assert q011fi_cycle["study_validity"] == "passed"
    assert q011fi_cycle["failed_validity_order"] == []
    assert q011fi_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fi_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fi_cycle["diagnostic_gates"].values())
    assert q011fi_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fi_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fi_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fi_cycle["diagnostic_classification"] == q011fi.INERT_CLASSIFICATION
    assert not q011fi_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fi_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_third_q011cb_witness"],
        theorem["forty_third_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_third_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fi result is not sealed")
def test_q011fi_preserves_boundary_and_reproducible_digests(
    q011fi_cycle: dict[str, Any],
) -> None:
    theorem = q011fi_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_third_q011cb_witness"],
        theorem["forty_third_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_third_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 42" in q011fi_cycle["claim_boundary"]
    assert "ordinals 0 through 41" in q011fi_cycle["claim_boundary"]
    assert "later 44757 Q011cb refined signatures" in q011fi_cycle["claim_boundary"]
    assert "Q011fj" in q011fi_cycle["next_change"]
    json.dumps(q011fi_cycle, allow_nan=False)
    assert {name: q011fi_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fi_cycle["result_digest_sha256"] == (
        q011fi.q011b._canonical_json_sha256(q011fi._result_digest_sections(q011fi_cycle))
    )
    assert q011fi._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fi result is not sealed")
def test_q011fi_study_metadata_and_optional_artifact_are_scoped(
    q011fi_study: dict[str, Any],
) -> None:
    assert q011fi_study["schema_version"] == 1
    assert q011fi_study["source"] == source_metadata()
    assert q011fi_study["study_gate"] == "passed"
    assert q011fi_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fi_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_553
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fi_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 42
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fi_study, allow_nan=False)

    runner_path = Path(q011fi.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fi_degree34_forty_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fi artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fi_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fi.q011b._canonical_json_sha256(q011fi._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
