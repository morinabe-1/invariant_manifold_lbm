from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011di_degree34_seventeenth_individual_partition_audit as q011di
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "18d4bfc349b132d4cba403d29a6119a9241021bfc63ddf931aff7efa7d161438"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "d8f6145a3c58e11fe3c47facfe4ada251acb6a6fc862c37d4bb4fd2961327d5b",
    "partition_input_digest_sha256": (
        "471cca1dc9615b7a1b825eecd9b0fd39f8469067f23eb43177817021108c8ad6"
    ),
    "allocation_audit_digest_sha256": (
        "2d1e0e1af7bcf96ca79736125b17fde462f13066fc83e399883d898fdde43f31"
    ),
    "result_digest_sha256": "a6ce0eb9c3e8076ee4de93032aa518a9cb3a874bdd077fc465df154583197131",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "7dc04437c78a8ebfb87ffe7779541dfe4aba5d02b07f317a80ac035ffdaf6e7b"
    ),
    "parent_center_product_interval_digest_sha256": (
        "b79a91b60531f959013e0392b2137dc8e274f0c2ab816a621421f61622e62939"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "078d620134ca9846e97737bad2de872c560d9f402f1e5995c30fb227e83f096c"
    ),
    "allocation_classification_record_digest_sha256": (
        "92d3ddb36c40c2b790ca30164e0fa350a60f6ebea8dfc98504f5555da0f7e7e9"
    ),
}


@pytest.fixture(scope="module")
def q011di_study() -> dict[str, Any]:
    return q011di.run_q011di_study()


@pytest.fixture(scope="module")
def q011di_cycle(q011di_study: dict[str, Any]) -> dict[str, Any]:
    return q011di_study["cycle"]


def test_q011di_seals_q011dh_and_all_prior_inputs(
    q011di_cycle: dict[str, Any],
) -> None:
    sealed = q011di_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 91
    assert sealed["direct_digest_count"] == 422
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dh"]["digests"]) == q011di.Q011DH_DIGESTS
    assert sealed["q011dh"]["artifact_sha256"] == q011di.Q011DH_ARTIFACT_SHA256
    assert sealed["q011dh"]["runner_sha256"] == q011di.Q011DH_RUNNER_SHA256
    assert sealed["q011dh"]["resolved_witness_digest_sha256"] == (
        q011di.EXPECTED_ORDINAL_FIFTEEN_RESOLUTION_DIGEST
    )


def test_q011di_selects_exactly_flatten_ordinal_sixteen(
    q011di_cycle: dict[str, Any],
) -> None:
    fixed = q011di_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["seventeenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 16
    assert selection["selected_left_index"] == 2
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(16))
    assert selection["ordinal_fifteen_resolution_digest_sha256"] == (
        q011di.EXPECTED_ORDINAL_FIFTEEN_RESOLUTION_DIGEST
    )
    parent = selection["seventeenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [2, 7], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 911
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011di.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011di.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011di.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011di_reconstructs_registered_partition_and_inventory(
    q011di_cycle: dict[str, Any],
) -> None:
    fixed = q011di_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [2, 7],
        [5],
        [0, 7],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 2, 7, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011di.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011di.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 16_128
    assert fixed["full_allocation_digest_sha256"] == q011di.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 911
    assert fixed["compatible_allocation_digest_sha256"] == (q011di.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 2, 0, 7, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 2, 0, 7, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 16_080
    assert fixed["parent_witness_compatible_index"] == 910
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011di_all_exact_intervals_are_parent_identical(
    q011di_cycle: dict[str, Any],
) -> None:
    partition = q011di_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 911
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 911
    assert [record["compatible_allocation_index"] for record in records] == list(range(911))
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
        assert record["intersection_width_hex"] == (q011di.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011di.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011di_records_interval_inert_persistence(
    q011di_cycle: dict[str, Any],
) -> None:
    assert q011di_cycle["study_validity"] == "passed"
    assert q011di_cycle["failed_validity_order"] == []
    assert q011di_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011di_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011di_cycle["diagnostic_gates"].values())
    assert q011di_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011di_cycle["diagnostic_classification"] == q011di.INERT_CLASSIFICATION
    assert q011di_cycle["scientific_outcome"] == "not_evaluated"
    assert q011di_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 911,
    }
    partition = q011di_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011di_preserves_boundary_and_reproducible_digests(
    q011di_cycle: dict[str, Any],
) -> None:
    theorem = q011di_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_seventeenth_q011cb_witness"]
    assert not theorem["seventeenth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011df_ordinal_fourteen_phase_resolution_is_preserved"]
    assert theorem["q011dd_ordinal_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011db_ordinal_twelve_phase_resolution_is_preserved"]
    assert theorem["q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 16" in q011di_cycle["claim_boundary"]
    assert "later 44783 Q011cb refined signatures" in q011di_cycle["claim_boundary"]
    assert "Q011dj" in q011di_cycle["next_change"]
    json.dumps(q011di_cycle, allow_nan=False)
    assert {name: q011di_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011di_cycle["result_digest_sha256"] == (
        q011di.q011b._canonical_json_sha256(q011di._result_digest_sections(q011di_cycle))
    )
    assert q011di._protocol_globals_are_restored()


def test_q011di_study_metadata_and_optional_artifact_are_scoped(
    q011di_study: dict[str, Any],
) -> None:
    assert q011di_study["schema_version"] == 1
    assert q011di_study["source"] == source_metadata()
    assert q011di_study["study_gate"] == "passed"
    assert q011di_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011di_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 911
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011di_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 16
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011di_study, allow_nan=False)

    runner_path = Path(q011di.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011di_degree34_seventeenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011di artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011di.q011b._canonical_json_sha256(q011di._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
