from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ei_degree34_thirtieth_individual_partition_audit as q011ei
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "411c2747dd9ab211be6f2edb0101751dfae74899be6507c8576db691e81fc207"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "dab9d2b83c6e362fb9a59fea1aaac9d6e8782e555adcb320afe52afec292516d"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "badd184241abf8a65b1d4eda3e6bb6db28aebccf808a93c1a9363e82fdac2ea4",
    "partition_input_digest_sha256": "d62ae9a02d2baa507b4f5d2f90bcd22389f75e8ab5f16510c05ebbf9af283f0b",
    "allocation_audit_digest_sha256": "2989e090053f6f7bc05a9f7d0e145683731a317a22eb0df5dde3714d197e632f",
    "result_digest_sha256": "dd5b7f66f60c3380524e04c2c314d999088cb9f891ad11ec32fcdb27a44a47c4",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "8969e5f9bbe60d6480babf8fa460b5f1ea72b3594a93d11719d7afc6a07be2ed"
    ),
    "parent_center_product_interval_digest_sha256": (
        "544de171e9e8f5cff6aeeb153f2a3effca777e509b83862a1f2787b9cdefaee7"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "dc656aab5d8af468c145988cf8d1147d4f9cd9a0971b6f1631e3cf6f56d4a081"
    ),
    "allocation_classification_record_digest_sha256": (
        "12ce88dd94366a1caa4b3a032c7910d91bb3369d20730bdeca5bf05081f80bd3"
    ),
}


@pytest.fixture(scope="module")
def q011ei_study() -> dict[str, Any]:
    return q011ei.run_q011ei_study()


@pytest.fixture(scope="module")
def q011ei_cycle(q011ei_study: dict[str, Any]) -> dict[str, Any]:
    return q011ei_study["cycle"]


def test_q011ei_seals_q011eh_and_all_prior_inputs(
    q011ei_cycle: dict[str, Any],
) -> None:
    sealed = q011ei_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 117
    assert sealed["direct_digest_count"] == 539
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011eh"]["digests"]) == q011ei.Q011EH_DIGESTS
    assert sealed["q011eh"]["artifact_sha256"] == q011ei.Q011EH_ARTIFACT_SHA256
    assert sealed["q011eh"]["runner_sha256"] == q011ei.Q011EH_RUNNER_SHA256
    assert sealed["q011eh"]["resolved_witness_digest_sha256"] == (
        q011ei.EXPECTED_ORDINAL_TWENTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011ei_selects_exactly_flatten_ordinal_twenty_nine(
    q011ei_cycle: dict[str, Any],
) -> None:
    fixed = q011ei_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirtieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 29
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(29))
    assert selection["ordinal_twenty_eight_resolution_digest_sha256"] == (
        q011ei.EXPECTED_ORDINAL_TWENTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["thirtieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_382
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ei.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ei.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ei.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ei_reconstructs_registered_partition_and_inventory(
    q011ei_cycle: dict[str, Any],
) -> None:
    fixed = q011ei_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ei.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ei.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 42_336
    assert fixed["full_allocation_digest_sha256"] == q011ei.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_382
    assert fixed["compatible_allocation_digest_sha256"] == (q011ei.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 42_228
    assert fixed["parent_witness_compatible_index"] == 2_381
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ei_all_exact_intervals_are_parent_identical(
    q011ei_cycle: dict[str, Any],
) -> None:
    partition = q011ei_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_382
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_382
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_382))
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
        assert record["intersection_width_hex"] == (q011ei.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011ei.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011ei partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ei_records_interval_inert_persistence(
    q011ei_cycle: dict[str, Any],
) -> None:
    assert q011ei_cycle["study_validity"] == "passed"
    assert q011ei_cycle["failed_validity_order"] == []
    assert q011ei_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ei_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ei_cycle["diagnostic_gates"].values())
    assert q011ei_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ei_cycle["diagnostic_classification"] == q011ei.INERT_CLASSIFICATION
    assert q011ei_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ei_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_382,
    }
    partition = q011ei_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ei_preserves_boundary_and_reproducible_digests(
    q011ei_cycle: dict[str, Any],
) -> None:
    theorem = q011ei_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_thirtieth_q011cb_witness"]
    assert not theorem["thirtieth_q011cb_witness_is_resolved_by_individual_partition"]
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
    assert "flatten ordinal 29" in q011ei_cycle["claim_boundary"]
    assert "later 44770 Q011cb refined signatures" in q011ei_cycle["claim_boundary"]
    assert "Q011ej" in q011ei_cycle["next_change"]
    json.dumps(q011ei_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ei section digests have not been sealed yet")
    assert {name: q011ei_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ei_cycle["result_digest_sha256"] == (
        q011ei.q011b._canonical_json_sha256(q011ei._result_digest_sections(q011ei_cycle))
    )
    assert q011ei._protocol_globals_are_restored()


def test_q011ei_study_metadata_and_optional_artifact_are_scoped(
    q011ei_study: dict[str, Any],
) -> None:
    assert q011ei_study["schema_version"] == 1
    assert q011ei_study["source"] == source_metadata()
    assert q011ei_study["study_gate"] == "passed"
    assert q011ei_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ei_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_382
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ei_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 29
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ei_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ei runner hash has not been sealed yet")
    runner_path = Path(q011ei.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ei_degree34_thirtieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ei artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ei.q011b._canonical_json_sha256(q011ei._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
