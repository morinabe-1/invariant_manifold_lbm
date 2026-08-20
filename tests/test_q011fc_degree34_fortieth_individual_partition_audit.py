from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fc_degree34_fortieth_individual_partition_audit as q011fc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "5ca0a2cf6519091d043903643d071900bc42682065888e72c020fc3ca7638a70"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "c5b7531971aa03dcc46ba1c91eb621c023977bebfe5a242b277b52bcd7afb0b1"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "085df4a0e9d576ba01e4519ec1f80135b63914cdd68b159d322ce2e2324f3971",
    "partition_input_digest_sha256": "46b85eb8d027e50a6e4d2449ecbf52f4d9740d84b2ad805f819e1f918a72ab2f",
    "allocation_audit_digest_sha256": "b54e07a55d32184bd833c77f881eb26372393d4693a1511f96f2f387fd2f3d0e",
    "result_digest_sha256": "0abcb28c14ed1c66b9ec35f1878bfb5966cc45f3bdb299f6d5220de5c28470d3",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "291a9047d55b8e86570f801c72ea25f59a76ca9a11eefc42c117323c16c0dc51"
    ),
    "parent_center_product_interval_digest_sha256": (
        "1ab98ad56bef924c80b6d42c03dc40fa6e9df85aef7780e2e01c2033e1427f14"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "4f111de01c9ab2355cbac03aaba0206258aea4c794e8d18512c34717f721c53c"
    ),
    "allocation_classification_record_digest_sha256": (
        "06d42f03a510d731ded1689af043d709af3ef5e542e12d13b78dcef0a12123b8"
    ),
}


@pytest.fixture(scope="module")
def q011fc_study() -> dict[str, Any]:
    return q011fc.run_q011fc_study()


@pytest.fixture(scope="module")
def q011fc_cycle(q011fc_study: dict[str, Any]) -> dict[str, Any]:
    return q011fc_study["cycle"]


def test_q011fc_seals_q011fb_and_all_prior_inputs(
    q011fc_cycle: dict[str, Any],
) -> None:
    sealed = q011fc_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 137
    assert sealed["direct_digest_count"] == 629
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fb"]["digests"]) == q011fc.Q011FB_DIGESTS
    assert sealed["q011fb"]["artifact_sha256"] == q011fc.Q011FB_ARTIFACT_SHA256
    assert sealed["q011fb"]["runner_sha256"] == q011fc.Q011FB_RUNNER_SHA256
    assert sealed["q011fb"]["resolved_witness_digest_sha256"] == (
        q011fc.EXPECTED_ORDINAL_THIRTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011fc_selects_exactly_flatten_ordinal_thirty_nine(
    q011fc_cycle: dict[str, Any],
) -> None:
    fixed = q011fc_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["fortieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 39
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(39))
    assert selection["ordinal_thirty_eight_resolution_digest_sha256"] == (
        q011fc.EXPECTED_ORDINAL_THIRTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["fortieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 1_136
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fc.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fc.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fc_reconstructs_registered_partition_and_inventory(
    q011fc_cycle: dict[str, Any],
) -> None:
    fixed = q011fc_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fc.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fc.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 20_160
    assert fixed["full_allocation_digest_sha256"] == q011fc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_136
    assert fixed["compatible_allocation_digest_sha256"] == (q011fc.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 20_112
    assert fixed["parent_witness_compatible_index"] == 1_135
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011fc_classifies_every_registered_exact_interval(
    q011fc_cycle: dict[str, Any],
) -> None:
    partition = q011fc_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_136
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_136
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_136))
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
        assert record["intersection_width_hex"] == q011fc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fc.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_136,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011fc_applies_the_registered_exclusive_stopping_rule(
    q011fc_cycle: dict[str, Any],
) -> None:
    assert q011fc_cycle["study_validity"] == "passed"
    assert q011fc_cycle["failed_validity_order"] == []
    assert q011fc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fc_cycle["diagnostic_gates"].values())
    assert q011fc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fc_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fc_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fc_cycle["diagnostic_classification"] == q011fc.INERT_CLASSIFICATION
    assert not q011fc_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fc_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fortieth_q011cb_witness"],
        theorem["fortieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fortieth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


def test_q011fc_preserves_boundary_and_reproducible_digests(
    q011fc_cycle: dict[str, Any],
) -> None:
    theorem = q011fc_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fortieth_q011cb_witness"],
        theorem["fortieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fortieth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 39" in q011fc_cycle["claim_boundary"]
    assert "later 44760 Q011cb refined signatures" in q011fc_cycle["claim_boundary"]
    assert "Q011fd" in q011fc_cycle["next_change"]
    json.dumps(q011fc_cycle, allow_nan=False)
    assert {name: q011fc_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fc_cycle["result_digest_sha256"] == (
        q011fc.q011b._canonical_json_sha256(q011fc._result_digest_sections(q011fc_cycle))
    )
    assert q011fc._protocol_globals_are_restored()


def test_q011fc_study_metadata_and_optional_artifact_are_scoped(
    q011fc_study: dict[str, Any],
) -> None:
    assert q011fc_study["schema_version"] == 1
    assert q011fc_study["source"] == source_metadata()
    assert q011fc_study["study_gate"] == "passed"
    assert q011fc_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fc_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_136
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 39
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fc_study, allow_nan=False)

    runner_path = Path(q011fc.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fc_degree34_fortieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fc_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fc.q011b._canonical_json_sha256(q011fc._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
