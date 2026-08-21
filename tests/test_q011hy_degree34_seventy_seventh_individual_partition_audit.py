from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hy_degree34_seventy_seventh_individual_partition_audit as q011hy
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "07a095c112833b39226022512325eac5d7b376239b26e3e71f0a66ab80b8abfd"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "08c62964ad4e398279c7637910d739890193859513992499c8f1428ea00e540e"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "6b24866f6aff79bd7d0c972aaae502866c0fff00b17cba716419a40566d54312",
    "partition_input_digest_sha256": "c68754b2f560f515ad5edf735e2eb8e172c7fd57570a4b60324bec538f815682",
    "allocation_audit_digest_sha256": "72d45f2ce45b13c55838ebcb706815f5d0c4c7715a76df19b7355cda80ced709",
    "result_digest_sha256": "595e38bf5e856d357bc7d96d0a401eac129d25b2412a2491b1425b986a28ee00",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "52b6eb737b63ebb38e142ac3caa2283bbadc435c9fb9b8b289e04eab81a388e1",
    "parent_center_product_interval_digest_sha256": "87a28d53b90714c72828e064046fe9cd49f4e69dfe8b1a9955213edfc445798d",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "352cfaf5794d1f6118fbaec140b400f1b468b1fdc96cef5cc8883354910a88ba",
    "allocation_classification_record_digest_sha256": "dc68f0778cfca4b6bd7c5ee87003b5d3f0f9dd816e29954c7f1e3d2ebd4e0d31",
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
def q011hy_structure() -> dict[str, Any]:
    sealed, artifacts = q011hy._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hy._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hy_study() -> dict[str, Any]:
    return q011hy.run_q011hy_study()


@pytest.fixture(scope="module")
def q011hy_cycle(q011hy_study: dict[str, Any]) -> dict[str, Any]:
    return q011hy_study["cycle"]


def test_q011hy_seals_q011hx_and_all_prior_inputs(q011hy_structure: dict[str, Any]) -> None:
    sealed = q011hy_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 211
    assert sealed["direct_digest_count"] == 962
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hx"]["digests"]) == q011hy.Q011HX_DIGESTS
    assert sealed["q011hx"]["artifact_sha256"] == q011hy.Q011HX_ARTIFACT_SHA256
    assert sealed["q011hx"]["runner_sha256"] == q011hy.Q011HX_RUNNER_SHA256
    assert sealed["q011hx"]["resolved_witness_digest_sha256"] == (
        q011hy.EXPECTED_ORDINAL_SEVENTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011hy_selects_exactly_flatten_ordinal_seventy_six(
    q011hy_structure: dict[str, Any],
) -> None:
    fixed = q011hy_structure["fixed"]
    selection = fixed["seventy_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 76
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(76))
    assert selection["ordinal_seventy_five_resolution_digest_sha256"] == (
        q011hy.EXPECTED_ORDINAL_SEVENTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["seventy_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 945
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011hy.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011hy.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hy_reconstructs_registered_partition_and_inventory(
    q011hy_structure: dict[str, Any],
) -> None:
    fixed = q011hy_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [4, 3]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011hy.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011hy.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 16_800
    assert fixed["full_allocation_digest_sha256"] == q011hy.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 945
    assert q011hy_structure["compatible_count"] == 945
    assert fixed["compatible_allocation_digest_sha256"] == q011hy.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 16_680
    assert fixed["parent_witness_compatible_index"] == 944
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hy result is not sealed")
def test_q011hy_classifies_every_registered_exact_interval(q011hy_cycle: dict[str, Any]) -> None:
    partition = q011hy_cycle["individual_allocation_interval_audit"]
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hy result is not sealed")
def test_q011hy_applies_the_registered_exclusive_stopping_rule(
    q011hy_cycle: dict[str, Any],
) -> None:
    assert q011hy_cycle["study_validity"] == "passed"
    assert q011hy_cycle["failed_validity_order"] == []
    assert q011hy_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hy_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hy_cycle["diagnostic_gates"].values())
    assert q011hy_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hy_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hy_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011hy.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011hy.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011hy.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011hy_cycle["diagnostic_classification"] == expected
    assert not q011hy_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hy_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_seventh_q011cb_witness"],
        theorem["seventy_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hy result is not sealed")
def test_q011hy_preserves_boundary_and_reproducible_digests(
    q011hy_cycle: dict[str, Any],
) -> None:
    theorem = q011hy_cycle["theorem_consequence"]
    assert theorem["q011hx_ordinal_seventy_five_phase_resolution_is_preserved"]
    assert theorem["q011hw_ordinal_seventy_five_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 76" in q011hy_cycle["claim_boundary"]
    assert "ordinals 0 through 75" in q011hy_cycle["claim_boundary"]
    assert "later 44723 Q011cb refined signatures" in q011hy_cycle["claim_boundary"]
    assert "Q011hz" in q011hy_cycle["next_change"]
    json.dumps(q011hy_cycle, allow_nan=False)
    assert {name: q011hy_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hy_cycle["result_digest_sha256"] == (
        q011hy.q011b._canonical_json_sha256(q011hy._result_digest_sections(q011hy_cycle))
    )
    assert q011hy._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hy result is not sealed")
def test_q011hy_study_metadata_and_optional_artifact_are_scoped(
    q011hy_study: dict[str, Any],
) -> None:
    assert q011hy_study["schema_version"] == 1
    assert q011hy_study["source"] == source_metadata()
    assert q011hy_study["study_gate"] == "passed"
    assert q011hy_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hy_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 945
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hy_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 76
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hy_study, allow_nan=False)

    runner_path = Path(q011hy.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hy_degree34_seventy_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hy artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hy_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hy.q011b._canonical_json_sha256(q011hy._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
