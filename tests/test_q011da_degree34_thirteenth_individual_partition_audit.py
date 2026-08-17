from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011da_degree34_thirteenth_individual_partition_audit as q011da
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "825e494e0a12ebba9ae0d6806fec153012fd612389fd914c9514b9f75bad6d1f"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "cbc87836bbaade43a1bf24ce38ac8608abea5e66da475a04969a41f119e35751"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "aa5a25299fcdb9cc467b57750bfb07b0da411d1aec11eb9d7c575203b6933a38",
    "partition_input_digest_sha256": (
        "6967ff08a45132db85d51b787268bc65b9cb26ca7bec92448b4b064a8b71337b"
    ),
    "allocation_audit_digest_sha256": (
        "ace3073578b6a8aeec052627a56e71c012981eb4d6d9bd28bf9c6d51f7ba037c"
    ),
    "result_digest_sha256": "69113d36717eced2218319d93b1f95e5b446c8d9a8987563cf4bf8a404e75027",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "28acb2d067ef73d3752efbbc8eeba3b38e34784b76291e9e324ae9786fc4dd3d"
    ),
    "parent_center_product_interval_digest_sha256": (
        "b8511a5aa092c36288e1b2538f47f2d30edf7957ddda9aa7057d2c9751e1e81b"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "1ebc04a0ec5edb82112f0791e327b67e3237530106a182ba0e1a28f752116a6a"
    ),
    "allocation_classification_record_digest_sha256": (
        "eb46ca3d8139968e6d3a0488388bd33a05c573d5720d2625ffda1bd0e73f44e8"
    ),
}


@pytest.fixture(scope="module")
def q011da_study() -> dict[str, Any]:
    return q011da.run_q011da_study()


@pytest.fixture(scope="module")
def q011da_cycle(q011da_study: dict[str, Any]) -> dict[str, Any]:
    return q011da_study["cycle"]


def test_q011da_seals_q011cz_and_all_prior_inputs(
    q011da_cycle: dict[str, Any],
) -> None:
    sealed = q011da_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 83
    assert sealed["direct_digest_count"] == 386
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cz"]["digests"]) == q011da.Q011CZ_DIGESTS
    assert sealed["q011cz"]["artifact_sha256"] == q011da.Q011CZ_ARTIFACT_SHA256
    assert sealed["q011cz"]["runner_sha256"] == q011da.Q011CZ_RUNNER_SHA256
    assert sealed["q011cz"]["resolved_witness_digest_sha256"] == (
        q011da.EXPECTED_ORDINAL_ELEVEN_RESOLUTION_DIGEST
    )


def test_q011da_selects_exactly_flatten_ordinal_twelve(
    q011da_cycle: dict[str, Any],
) -> None:
    fixed = q011da_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 12
    assert selection["selected_left_index"] == 1
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(12))
    assert selection["ordinal_eleven_resolution_digest_sha256"] == (
        q011da.EXPECTED_ORDINAL_ELEVEN_RESOLUTION_DIGEST
    )
    parent = selection["thirteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [1, 8], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 1_699
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011da.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011da.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011da.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011da_reconstructs_registered_partition_and_inventory(
    q011da_cycle: dict[str, Any],
) -> None:
    fixed = q011da_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [1, 8],
        [5],
        [4, 3],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 1, 8, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011da.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011da.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 30_240
    assert fixed["full_allocation_digest_sha256"] == q011da.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_699
    assert fixed["compatible_allocation_digest_sha256"] == q011da.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 1, 0, 8, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 1, 0, 8, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 30_120
    assert fixed["parent_witness_compatible_index"] == 1_698
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011da_all_exact_intervals_are_parent_identical(
    q011da_cycle: dict[str, Any],
) -> None:
    partition = q011da_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011da.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011da.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011da_records_interval_inert_persistence(
    q011da_cycle: dict[str, Any],
) -> None:
    assert q011da_cycle["study_validity"] == "passed"
    assert q011da_cycle["failed_validity_order"] == []
    assert q011da_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011da_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011da_cycle["diagnostic_gates"].values())
    assert q011da_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011da_cycle["diagnostic_classification"] == q011da.INERT_CLASSIFICATION
    assert q011da_cycle["scientific_outcome"] == "not_evaluated"
    assert q011da_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_699,
    }
    partition = q011da_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011da_preserves_boundary_and_reproducible_digests(
    q011da_cycle: dict[str, Any],
) -> None:
    theorem = q011da_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_thirteenth_q011cb_witness"]
    assert not theorem["thirteenth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011cz_ordinal_eleven_phase_resolution_is_preserved"]
    assert theorem["q011cy_ordinal_eleven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
    assert theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
    assert theorem["q011cr_ordinal_seven_phase_resolution_is_preserved"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 12" in q011da_cycle["claim_boundary"]
    assert "later 44787 Q011cb refined signatures" in q011da_cycle["claim_boundary"]
    assert "Q011db" in q011da_cycle["next_change"]
    json.dumps(q011da_cycle, allow_nan=False)
    assert {name: q011da_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011da_cycle["result_digest_sha256"] == (
        q011da.q011b._canonical_json_sha256(q011da._result_digest_sections(q011da_cycle))
    )
    assert q011da._protocol_globals_are_restored()


def test_q011da_study_metadata_and_optional_artifact_are_scoped(
    q011da_study: dict[str, Any],
) -> None:
    assert q011da_study["schema_version"] == 1
    assert q011da_study["source"] == source_metadata()
    assert q011da_study["study_gate"] == "passed"
    assert q011da_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011da_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_699
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011da_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 12
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011da_study, allow_nan=False)

    runner_path = Path(q011da.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011da_degree34_thirteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011da artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011da.q011b._canonical_json_sha256(q011da._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
