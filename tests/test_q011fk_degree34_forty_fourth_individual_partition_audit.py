from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fk_degree34_forty_fourth_individual_partition_audit as q011fk
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "0ce17573faa18a2d4299d2a907761be8c1b1559d9c6e5746e16ed4e1febaf87e"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "145bc93a67591306d483d646e2423040c56a60efcf3f125b0d95fc4df7fbfc2a"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "7c9704b201ec86b74d9737e1efdd9bf007217a1466498cc21724351063478d97",
    "partition_input_digest_sha256": "a21d04abc763e923a88009f8bb755354e09869ab92a2500c00777a8201917a5c",
    "allocation_audit_digest_sha256": "742ef9b11aad1f2a65704c9749c226bcecf8b625ba71721ee95ef08868d1b7ae",
    "result_digest_sha256": "8faf2f5056a293a629a6d6878b22ff78e65e847822f8c8d6874cdffb443cd7ad",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "e0ab6133955521075050b048ce351ea163d1623543b7a88c735a22b0980062b2"
    ),
    "parent_center_product_interval_digest_sha256": (
        "2ec6affd0bc463695a177670cf11884bb916b052e1348ab4a8779e82d5e85169"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "4e6f71665e3b6630509430027e265730a6daf031ff28b1b2a01fbb670915d5dc"
    ),
    "allocation_classification_record_digest_sha256": (
        "d86c62faa097b2c79a9a5ce22887cdb40ca0cff729d79429f20d997e86142fce"
    ),
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011fk_structure() -> dict[str, Any]:
    sealed, artifacts = q011fk._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011fk._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011fk_study() -> dict[str, Any]:
    return q011fk.run_q011fk_study()


@pytest.fixture(scope="module")
def q011fk_cycle(q011fk_study: dict[str, Any]) -> dict[str, Any]:
    return q011fk_study["cycle"]


def test_q011fk_seals_q011fj_and_all_prior_inputs(
    q011fk_structure: dict[str, Any],
) -> None:
    sealed = q011fk_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 145
    assert sealed["direct_digest_count"] == 665
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fj"]["digests"]) == q011fk.Q011FJ_DIGESTS
    assert sealed["q011fj"]["artifact_sha256"] == q011fk.Q011FJ_ARTIFACT_SHA256
    assert sealed["q011fj"]["runner_sha256"] == q011fk.Q011FJ_RUNNER_SHA256
    assert sealed["q011fj"]["resolved_witness_digest_sha256"] == (
        q011fk.EXPECTED_ORDINAL_FORTY_TWO_RESOLUTION_DIGEST
    )


def test_q011fk_selects_exactly_flatten_ordinal_forty_three(
    q011fk_structure: dict[str, Any],
) -> None:
    fixed = q011fk_structure["fixed"]
    selection = fixed["forty_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 43
    assert selection["selected_left_index"] == 5
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(43))
    assert selection["ordinal_forty_two_resolution_digest_sha256"] == (
        q011fk.EXPECTED_ORDINAL_FORTY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["forty_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [5, 4], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 2_837
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fk.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fk.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fk_reconstructs_registered_partition_and_inventory(
    q011fk_structure: dict[str, Any],
) -> None:
    fixed = q011fk_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [5, 4],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 5, 4, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fk.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fk.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_400
    assert fixed["full_allocation_digest_sha256"] == q011fk.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_837
    assert q011fk_structure["compatible_count"] == 2_837
    assert fixed["compatible_allocation_digest_sha256"] == (q011fk.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 5, 0, 4, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 5, 0, 4, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 50_280
    assert fixed["parent_witness_compatible_index"] == 2_836
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fk result is not sealed")
def test_q011fk_classifies_every_registered_exact_interval(
    q011fk_cycle: dict[str, Any],
) -> None:
    partition = q011fk_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_837
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_837
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_837))
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
        assert record["intersection_width_hex"] == q011fk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fk.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_837,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fk result is not sealed")
def test_q011fk_applies_the_registered_exclusive_stopping_rule(
    q011fk_cycle: dict[str, Any],
) -> None:
    assert q011fk_cycle["study_validity"] == "passed"
    assert q011fk_cycle["failed_validity_order"] == []
    assert q011fk_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fk_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fk_cycle["diagnostic_gates"].values())
    assert q011fk_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fk_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fk_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fk_cycle["diagnostic_classification"] == q011fk.INERT_CLASSIFICATION
    assert not q011fk_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fk_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_fourth_q011cb_witness"],
        theorem["forty_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_fourth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fk result is not sealed")
def test_q011fk_preserves_boundary_and_reproducible_digests(
    q011fk_cycle: dict[str, Any],
) -> None:
    theorem = q011fk_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_fourth_q011cb_witness"],
        theorem["forty_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_fourth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 43" in q011fk_cycle["claim_boundary"]
    assert "ordinals 0 through 42" in q011fk_cycle["claim_boundary"]
    assert "later 44756 Q011cb refined signatures" in q011fk_cycle["claim_boundary"]
    assert "Q011fl" in q011fk_cycle["next_change"]
    json.dumps(q011fk_cycle, allow_nan=False)
    assert {name: q011fk_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fk_cycle["result_digest_sha256"] == (
        q011fk.q011b._canonical_json_sha256(q011fk._result_digest_sections(q011fk_cycle))
    )
    assert q011fk._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fk result is not sealed")
def test_q011fk_study_metadata_and_optional_artifact_are_scoped(
    q011fk_study: dict[str, Any],
) -> None:
    assert q011fk_study["schema_version"] == 1
    assert q011fk_study["source"] == source_metadata()
    assert q011fk_study["study_gate"] == "passed"
    assert q011fk_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fk_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_837
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fk_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 43
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fk_study, allow_nan=False)

    runner_path = Path(q011fk.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fk_degree34_forty_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fk artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fk_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fk.q011b._canonical_json_sha256(q011fk._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
