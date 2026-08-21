from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hk_degree34_seventieth_individual_partition_audit as q011hk
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
def q011hk_structure() -> dict[str, Any]:
    sealed, artifacts = q011hk._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hk._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hk_study() -> dict[str, Any]:
    return q011hk.run_q011hk_study()


@pytest.fixture(scope="module")
def q011hk_cycle(q011hk_study: dict[str, Any]) -> dict[str, Any]:
    return q011hk_study["cycle"]


def test_q011hk_seals_q011hj_and_all_prior_inputs(
    q011hk_structure: dict[str, Any],
) -> None:
    sealed = q011hk_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 197
    assert sealed["direct_digest_count"] == 899
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hj"]["digests"]) == q011hk.Q011HJ_DIGESTS
    assert sealed["q011hj"]["artifact_sha256"] == q011hk.Q011HJ_ARTIFACT_SHA256
    assert sealed["q011hj"]["runner_sha256"] == q011hk.Q011HJ_RUNNER_SHA256
    assert sealed["q011hj"]["resolved_witness_digest_sha256"] == (
        q011hk.EXPECTED_ORDINAL_SIXTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011hk_selects_exactly_flatten_ordinal_sixty_nine(
    q011hk_structure: dict[str, Any],
) -> None:
    fixed = q011hk_structure["fixed"]
    selection = fixed["seventieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 69
    assert selection["selected_left_index"] == 8
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(69))
    assert selection["ordinal_sixty_eight_resolution_digest_sha256"] == (
        q011hk.EXPECTED_ORDINAL_SIXTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["seventieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [8, 1], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 1_531
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011hk.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011hk.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hk_reconstructs_registered_partition_and_inventory(
    q011hk_structure: dict[str, Any],
) -> None:
    fixed = q011hk_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [8, 1],
        [5],
        [5, 2],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 8, 1, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011hk.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011hk.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 27_216
    assert fixed["full_allocation_digest_sha256"] == q011hk.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_531
    assert q011hk_structure["compatible_count"] == 1_531
    assert fixed["compatible_allocation_digest_sha256"] == q011hk.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 8, 0, 1, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 8, 0, 1, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 27_108
    assert fixed["parent_witness_compatible_index"] == 1_530
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hk result is not sealed")
def test_q011hk_classifies_every_registered_exact_interval(
    q011hk_cycle: dict[str, Any],
) -> None:
    partition = q011hk_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_531
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_531
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_531))
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
        assert record["intersection_width_hex"] == q011hk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011hk.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_531,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hk result is not sealed")
def test_q011hk_applies_the_registered_exclusive_stopping_rule(
    q011hk_cycle: dict[str, Any],
) -> None:
    assert q011hk_cycle["study_validity"] == "passed"
    assert q011hk_cycle["failed_validity_order"] == []
    assert q011hk_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hk_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hk_cycle["diagnostic_gates"].values())
    assert q011hk_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hk_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hk_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011hk_cycle["diagnostic_classification"] == q011hk.INERT_CLASSIFICATION
    assert not q011hk_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hk_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventieth_q011cb_witness"],
        theorem["seventieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_seventieth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hk result is not sealed")
def test_q011hk_preserves_boundary_and_reproducible_digests(
    q011hk_cycle: dict[str, Any],
) -> None:
    theorem = q011hk_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventieth_q011cb_witness"],
        theorem["seventieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_seventieth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011hj_ordinal_sixty_eight_phase_resolution_is_preserved"]
    assert theorem["q011hi_ordinal_sixty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hh_ordinal_sixty_seven_phase_resolution_is_preserved"]
    assert theorem["q011hg_ordinal_sixty_seven_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 69" in q011hk_cycle["claim_boundary"]
    assert "ordinals 0 through 68" in q011hk_cycle["claim_boundary"]
    assert "later 44730 Q011cb refined signatures" in q011hk_cycle["claim_boundary"]
    assert "Q011hl" in q011hk_cycle["next_change"]
    json.dumps(q011hk_cycle, allow_nan=False)
    assert {name: q011hk_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hk_cycle["result_digest_sha256"] == (
        q011hk.q011b._canonical_json_sha256(q011hk._result_digest_sections(q011hk_cycle))
    )
    assert q011hk._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hk result is not sealed")
def test_q011hk_study_metadata_and_optional_artifact_are_scoped(
    q011hk_study: dict[str, Any],
) -> None:
    assert q011hk_study["schema_version"] == 1
    assert q011hk_study["source"] == source_metadata()
    assert q011hk_study["study_gate"] == "passed"
    assert q011hk_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011hk_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_531
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hk_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 69
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hk_study, allow_nan=False)

    runner_path = Path(q011hk.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hk_degree34_seventieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hk artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hk_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hk.q011b._canonical_json_sha256(q011hk._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
