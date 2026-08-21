from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hw_degree34_seventy_sixth_individual_partition_audit as q011hw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "92a74fecf2db4314a43cb28edfdce2d542e083b27d2c4e102748dc478182f555"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "ecb01790df087b8e9cfba4833c3eec24f40b412f03dffb8f6eb7a3666311d1df"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "a6216f4ed0618c1ca2da6f248d46f0ca7fc7f9999f129b31384f04d08b457cc7",
    "partition_input_digest_sha256": "848a98ae9b1d6cc22ec98f869f6dce802cedaa86c3ba3add747d3fc043697191",
    "allocation_audit_digest_sha256": "3d703253c70db441af317b9e9a72d33547772388cf5bc82e50756838f50224e5",
    "result_digest_sha256": "2e26b362531fb3b6b60b7219404e6264594f1a0b0166bd509fc1e79a543552cb",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "88bb11eba81de2a945483acdda607d2a46826d6d0e5525a7ab173b35eaea2ca6",
    "parent_center_product_interval_digest_sha256": "458aa20730649dcee571f253f95c5470c5c9f34eea4c269164c099b6e6d7f8bf",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "9694243d16b5e1b404c330e79ceabfe02c3229da4b31d9602b45237bbce7fef6",
    "allocation_classification_record_digest_sha256": "0dad595000752523afc3c79ded100fb7da024d97e9e8b86a796a0572e391f53c",
}
EXPECTED_REFINEMENT_OUTCOME: str | None = "partition_inert_persistent"
RESULT_EXPECTATIONS_FIXED = all(
    value is not None
    for value in (
        EXPECTED_RUNNER_SHA256,
        EXPECTED_ARTIFACT_SHA256,
        EXPECTED_SECTION_DIGESTS,
        EXPECTED_PARTITION_DIGESTS,
        EXPECTED_REFINEMENT_OUTCOME,
    )
)


@pytest.fixture(scope="module")
def q011hw_structure() -> dict[str, Any]:
    sealed, artifacts = q011hw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hw_study() -> dict[str, Any]:
    return q011hw.run_q011hw_study()


@pytest.fixture(scope="module")
def q011hw_cycle(q011hw_study: dict[str, Any]) -> dict[str, Any]:
    return q011hw_study["cycle"]


def test_q011hw_seals_q011hv_and_all_prior_inputs(q011hw_structure: dict[str, Any]) -> None:
    sealed = q011hw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 209
    assert sealed["direct_digest_count"] == 953
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hv"]["digests"]) == q011hw.Q011HV_DIGESTS
    assert sealed["q011hv"]["artifact_sha256"] == q011hw.Q011HV_ARTIFACT_SHA256
    assert sealed["q011hv"]["runner_sha256"] == q011hw.Q011HV_RUNNER_SHA256
    assert sealed["q011hv"]["resolved_witness_digest_sha256"] == (
        q011hw.EXPECTED_ORDINAL_SEVENTY_FOUR_RESOLUTION_DIGEST
    )


def test_q011hw_selects_exactly_flatten_ordinal_seventy_five(
    q011hw_structure: dict[str, Any],
) -> None:
    fixed = q011hw_structure["fixed"]
    selection = fixed["seventy_sixth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 75
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(75))
    assert selection["ordinal_seventy_four_resolution_digest_sha256"] == (
        q011hw.EXPECTED_ORDINAL_SEVENTY_FOUR_RESOLUTION_DIGEST
    )
    parent = selection["seventy_sixth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 945
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011hw.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011hw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hw_reconstructs_registered_partition_and_inventory(
    q011hw_structure: dict[str, Any],
) -> None:
    fixed = q011hw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [3, 4]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011hw.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011hw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 16_800
    assert fixed["full_allocation_digest_sha256"] == q011hw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 945
    assert q011hw_structure["compatible_count"] == 945
    assert fixed["compatible_allocation_digest_sha256"] == q011hw.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 16_680
    assert fixed["parent_witness_compatible_index"] == 944
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hw result is not sealed")
def test_q011hw_classifies_every_registered_exact_interval(q011hw_cycle: dict[str, Any]) -> None:
    partition = q011hw_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 945
    records = partition["allocation_classification_records"]
    assert len(records) == 945
    assert [record["compatible_allocation_index"] for record in records] == list(range(945))
    assert sum(partition["exact_relation_counts"].values()) == 945
    assert sum(partition["binary64_outward_relation_counts"].values()) == 945
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hw result is not sealed")
def test_q011hw_applies_the_registered_exclusive_stopping_rule(
    q011hw_cycle: dict[str, Any],
) -> None:
    assert q011hw_cycle["study_validity"] == "passed"
    assert q011hw_cycle["failed_validity_order"] == []
    assert q011hw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hw_cycle["diagnostic_gates"].values())
    assert q011hw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hw_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011hw.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011hw.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011hw.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011hw_cycle["diagnostic_classification"] == expected
    assert not q011hw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_sixth_q011cb_witness"],
        theorem["seventy_sixth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_sixth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hw result is not sealed")
def test_q011hw_preserves_boundary_and_reproducible_digests(
    q011hw_cycle: dict[str, Any],
) -> None:
    theorem = q011hw_cycle["theorem_consequence"]
    assert theorem["q011hv_ordinal_seventy_four_phase_resolution_is_preserved"]
    assert theorem["q011hu_ordinal_seventy_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hr_ordinal_seventy_two_phase_resolution_is_preserved"]
    assert theorem["q011hq_ordinal_seventy_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hp_ordinal_seventy_one_phase_resolution_is_preserved"]
    assert theorem["q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hn_ordinal_seventy_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 75" in q011hw_cycle["claim_boundary"]
    assert "ordinals 0 through 74" in q011hw_cycle["claim_boundary"]
    assert "later 44724 Q011cb refined signatures" in q011hw_cycle["claim_boundary"]
    assert "Q011hx" in q011hw_cycle["next_change"]
    json.dumps(q011hw_cycle, allow_nan=False)
    assert {name: q011hw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hw_cycle["result_digest_sha256"] == (
        q011hw.q011b._canonical_json_sha256(q011hw._result_digest_sections(q011hw_cycle))
    )
    assert q011hw._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hw result is not sealed")
def test_q011hw_study_metadata_and_optional_artifact_are_scoped(
    q011hw_study: dict[str, Any],
) -> None:
    assert q011hw_study["schema_version"] == 1
    assert q011hw_study["source"] == source_metadata()
    assert q011hw_study["study_gate"] == "passed"
    assert q011hw_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 945
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 75
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hw_study, allow_nan=False)

    runner_path = Path(q011hw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hw_degree34_seventy_sixth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hw.q011b._canonical_json_sha256(q011hw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
