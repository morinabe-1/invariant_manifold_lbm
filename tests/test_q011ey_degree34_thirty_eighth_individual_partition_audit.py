from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ey_degree34_thirty_eighth_individual_partition_audit as q011ey
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "0861c122814c6cd7399ce92c3d2e3e6134df3e52b1d44f0e975ed711eb309514"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "90080ab0eb1482445c72d9ddb491f22a13f7fe91991b6276973f48df26acbc7a"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "eaf5423709731ae0d59abcb2f0bee2dfcd56b3ac0d34041ab5ba9252ec379789",
    "partition_input_digest_sha256": "59a1018cb675a4395bececb2c9d5d0dd4a472b1423170c6462f4fb72deedd4b6",
    "allocation_audit_digest_sha256": "2f99538a87ad53480e3865f4d03d5064856bb535516494611f8021e8b64adaca",
    "result_digest_sha256": "aeaee268ac9eaa4d175a13a4437596eeff23f5db8cc5ed9c36f8d86f84cf2f9a",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "e429694718c1b4d69290bfa37b7ac40585e0a0876219c090eca7aea547eca7c1"
    ),
    "parent_center_product_interval_digest_sha256": (
        "3c88b1469a2eddcba8d4a4505fe4f8aa2f1335088b08274fe592aab4ea27f4d0"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "9ac1b9ce084fdcc5f99cc5cf9211c41992f47a0985cd8109746b4460e517fb80"
    ),
    "allocation_classification_record_digest_sha256": (
        "2ef05b13ff6094aadfa68a21ea3b3adc8e7b628fbab7a4060872508902cdac08"
    ),
}


@pytest.fixture(scope="module")
def q011ey_study() -> dict[str, Any]:
    return q011ey.run_q011ey_study()


@pytest.fixture(scope="module")
def q011ey_cycle(q011ey_study: dict[str, Any]) -> dict[str, Any]:
    return q011ey_study["cycle"]


def test_q011ey_seals_q011ex_and_all_prior_inputs(
    q011ey_cycle: dict[str, Any],
) -> None:
    sealed = q011ey_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 133
    assert sealed["direct_digest_count"] == 611
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ex"]["digests"]) == q011ey.Q011EX_DIGESTS
    assert sealed["q011ex"]["artifact_sha256"] == q011ey.Q011EX_ARTIFACT_SHA256
    assert sealed["q011ex"]["runner_sha256"] == q011ey.Q011EX_RUNNER_SHA256
    assert sealed["q011ex"]["resolved_witness_digest_sha256"] == (
        q011ey.EXPECTED_ORDINAL_THIRTY_SIX_RESOLUTION_DIGEST
    )


def test_q011ey_selects_exactly_flatten_ordinal_thirty_seven(
    q011ey_cycle: dict[str, Any],
) -> None:
    fixed = q011ey_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 37
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(37))
    assert selection["ordinal_thirty_six_resolution_digest_sha256"] == (
        q011ey.EXPECTED_ORDINAL_THIRTY_SIX_RESOLUTION_DIGEST
    )
    parent = selection["thirty_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_553
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ey.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ey.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ey.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ey_reconstructs_registered_partition_and_inventory(
    q011ey_cycle: dict[str, Any],
) -> None:
    fixed = q011ey_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ey.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ey.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 45_360
    assert fixed["full_allocation_digest_sha256"] == q011ey.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_553
    assert fixed["compatible_allocation_digest_sha256"] == (q011ey.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 45_252
    assert fixed["parent_witness_compatible_index"] == 2_552
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ey_classifies_every_registered_exact_interval(
    q011ey_cycle: dict[str, Any],
) -> None:
    partition = q011ey_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == q011ey.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011ey.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ey_applies_the_registered_exclusive_stopping_rule(
    q011ey_cycle: dict[str, Any],
) -> None:
    assert q011ey_cycle["study_validity"] == "passed"
    assert q011ey_cycle["failed_validity_order"] == []
    assert q011ey_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ey_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ey_cycle["diagnostic_gates"].values())
    assert q011ey_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ey_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ey_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ey_cycle["diagnostic_classification"] == q011ey.INERT_CLASSIFICATION
    partition = q011ey_cycle["individual_allocation_interval_audit"]
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_553,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]
    theorem = q011ey_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_eighth_q011cb_witness"],
        theorem["thirty_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_thirty_eighth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


def test_q011ey_preserves_boundary_and_reproducible_digests(
    q011ey_cycle: dict[str, Any],
) -> None:
    theorem = q011ey_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_eighth_q011cb_witness"],
        theorem["thirty_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_thirty_eighth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011ex_ordinal_thirty_six_phase_resolution_is_preserved"]
    assert theorem["q011ew_ordinal_thirty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ev_ordinal_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011et_ordinal_thirty_four_phase_resolution_is_preserved"]
    assert theorem["q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011er_ordinal_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ep_ordinal_thirty_two_phase_resolution_is_preserved"]
    assert theorem["q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011en_ordinal_thirty_one_phase_resolution_is_preserved"]
    assert theorem["q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011el_ordinal_thirty_phase_resolution_is_preserved"]
    assert theorem["q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ej_ordinal_twenty_nine_phase_resolution_is_preserved"]
    assert theorem["q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eh_ordinal_twenty_eight_phase_resolution_is_preserved"]
    assert theorem["q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eb_ordinal_twenty_five_phase_resolution_is_preserved"]
    assert theorem["q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dz_ordinal_twenty_four_phase_resolution_is_preserved"]
    assert theorem["q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 37" in q011ey_cycle["claim_boundary"]
    assert "later 44762 Q011cb refined signatures" in q011ey_cycle["claim_boundary"]
    assert "Q011ez" in q011ey_cycle["next_change"]
    json.dumps(q011ey_cycle, allow_nan=False)
    assert {name: q011ey_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ey_cycle["result_digest_sha256"] == (
        q011ey.q011b._canonical_json_sha256(q011ey._result_digest_sections(q011ey_cycle))
    )
    assert q011ey._protocol_globals_are_restored()


def test_q011ey_study_metadata_and_optional_artifact_are_scoped(
    q011ey_study: dict[str, Any],
) -> None:
    assert q011ey_study["schema_version"] == 1
    assert q011ey_study["source"] == source_metadata()
    assert q011ey_study["study_gate"] == "passed"
    assert q011ey_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ey_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_553
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ey_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 37
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ey_study, allow_nan=False)

    runner_path = Path(q011ey.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ey_degree34_thirty_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ey artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ey_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ey.q011b._canonical_json_sha256(q011ey._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
