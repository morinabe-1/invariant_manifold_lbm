from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ho_degree34_seventy_second_individual_partition_audit as q011ho
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
def q011ho_structure() -> dict[str, Any]:
    sealed, artifacts = q011ho._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ho._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ho_study() -> dict[str, Any]:
    return q011ho.run_q011ho_study()


@pytest.fixture(scope="module")
def q011ho_cycle(q011ho_study: dict[str, Any]) -> dict[str, Any]:
    return q011ho_study["cycle"]


def test_q011ho_seals_q011hn_and_all_prior_inputs(
    q011ho_structure: dict[str, Any],
) -> None:
    sealed = q011ho_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 201
    assert sealed["direct_digest_count"] == 917
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hn"]["digests"]) == q011ho.Q011HN_DIGESTS
    assert sealed["q011hn"]["artifact_sha256"] == q011ho.Q011HN_ARTIFACT_SHA256
    assert sealed["q011hn"]["runner_sha256"] == q011ho.Q011HN_RUNNER_SHA256
    assert sealed["q011hn"]["resolved_witness_digest_sha256"] == (
        q011ho.EXPECTED_ORDINAL_SEVENTY_RESOLUTION_DIGEST
    )


def test_q011ho_selects_exactly_flatten_ordinal_seventy_one(
    q011ho_structure: dict[str, Any],
) -> None:
    fixed = q011ho_structure["fixed"]
    selection = fixed["seventy_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 71
    assert selection["selected_left_index"] == 8
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(71))
    assert selection["ordinal_seventy_resolution_digest_sha256"] == (
        q011ho.EXPECTED_ORDINAL_SEVENTY_RESOLUTION_DIGEST
    )
    parent = selection["seventy_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [8, 1], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 685
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ho.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ho.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ho.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ho_reconstructs_registered_partition_and_inventory(
    q011ho_structure: dict[str, Any],
) -> None:
    fixed = q011ho_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [8, 1],
        [5],
        [7, 0],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 8, 1, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011ho.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011ho.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 12_096
    assert fixed["full_allocation_digest_sha256"] == q011ho.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 685
    assert q011ho_structure["compatible_count"] == 685
    assert fixed["compatible_allocation_digest_sha256"] == q011ho.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 8, 0, 1, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 8, 0, 1, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 12_048
    assert fixed["parent_witness_compatible_index"] == 684
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ho result is not sealed")
def test_q011ho_classifies_every_registered_exact_interval(
    q011ho_cycle: dict[str, Any],
) -> None:
    partition = q011ho_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 685
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 685
    assert [record["compatible_allocation_index"] for record in records] == list(range(685))
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
        assert record["intersection_width_hex"] == q011ho.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011ho.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 685,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ho result is not sealed")
def test_q011ho_applies_the_registered_exclusive_stopping_rule(
    q011ho_cycle: dict[str, Any],
) -> None:
    assert q011ho_cycle["study_validity"] == "passed"
    assert q011ho_cycle["failed_validity_order"] == []
    assert q011ho_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ho_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ho_cycle["diagnostic_gates"].values())
    assert q011ho_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ho_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ho_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ho_cycle["diagnostic_classification"] == q011ho.INERT_CLASSIFICATION
    assert not q011ho_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ho_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_second_q011cb_witness"],
        theorem["seventy_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_second_q011cb_witness_persists"
        ],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ho result is not sealed")
def test_q011ho_preserves_boundary_and_reproducible_digests(
    q011ho_cycle: dict[str, Any],
) -> None:
    theorem = q011ho_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_second_q011cb_witness"],
        theorem["seventy_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_second_q011cb_witness_persists"
        ],
    )
    assert flags == (True, False, False)
    assert theorem["q011hn_ordinal_seventy_phase_resolution_is_preserved"]
    assert theorem["q011hm_ordinal_seventy_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hl_ordinal_sixty_nine_phase_resolution_is_preserved"]
    assert theorem["q011hk_ordinal_sixty_nine_interval_inert_diagnostic_is_preserved"]
    assert all(
        value
        for name, value in theorem.items()
        if name.endswith("_is_preserved") and isinstance(value, bool)
    )
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 71" in q011ho_cycle["claim_boundary"]
    assert "ordinals 0 through 70" in q011ho_cycle["claim_boundary"]
    assert "later 44728 Q011cb refined signatures" in q011ho_cycle["claim_boundary"]
    assert "Q011hp" in q011ho_cycle["next_change"]
    json.dumps(q011ho_cycle, allow_nan=False)
    assert {name: q011ho_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ho_cycle["result_digest_sha256"] == (
        q011ho.q011b._canonical_json_sha256(q011ho._result_digest_sections(q011ho_cycle))
    )
    assert q011ho._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ho result is not sealed")
def test_q011ho_study_metadata_and_optional_artifact_are_scoped(
    q011ho_study: dict[str, Any],
) -> None:
    assert q011ho_study["schema_version"] == 1
    assert q011ho_study["source"] == source_metadata()
    assert q011ho_study["study_gate"] == "passed"
    assert q011ho_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ho_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 685
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ho_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 71
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ho_study, allow_nan=False)

    runner_path = Path(q011ho.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ho_degree34_seventy_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ho artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ho_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ho.q011b._canonical_json_sha256(q011ho._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
