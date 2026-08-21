from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hs_degree34_seventy_fourth_individual_partition_audit as q011hs
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "42ee75bb0204881b0d0b15d3cf2c0878238b84a84e3defc2a74ff2556f6a4348"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "88a6e5ab4bde5175ba33f9c0f1607ce993c00a073cd8e8e867c46e45e68ee8a7"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "69857496b0aa196325647e6d9e8dd3db1aa13641b3f55d8b1a297119f0e3036a",
    "partition_input_digest_sha256": "f3ee16dc23dc7bd0ba5423b12fe60d6e62d658db3ee40e2097e9455e792f861a",
    "allocation_audit_digest_sha256": "d95aa944036c54cf8825b072bc0fcc02b56084d7e2b10e98a0d1dd45b78c6591",
    "result_digest_sha256": "2e14ca590269c24ef6703a5da174367fed49fa80c8992db844fa62602269b622",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "3caf81863989c2c18d65ed5a7f346cfb117f6c7166c5f80ea6374cf061f63d9b",
    "parent_center_product_interval_digest_sha256": "adeaead3526a5c9db3be3aebde1151fbcbdcf438c94b5c2838f8919b2e60a30e",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "66661fbf6f59f6358979d6a1ad3ad3cc10d3e44a5ee4f4ce69c2e5e4e4cf9cbc",
    "allocation_classification_record_digest_sha256": "a67eae5a712bf9a929b2d9847429be72b9d1d8448e6d775ec3810bedaec4e39b",
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
def q011hs_structure() -> dict[str, Any]:
    sealed, artifacts = q011hs._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hs._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hs_study() -> dict[str, Any]:
    return q011hs.run_q011hs_study()


@pytest.fixture(scope="module")
def q011hs_cycle(q011hs_study: dict[str, Any]) -> dict[str, Any]:
    return q011hs_study["cycle"]


def test_q011hs_seals_q011hr_and_all_prior_inputs(q011hs_structure: dict[str, Any]) -> None:
    sealed = q011hs_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 205
    assert sealed["direct_digest_count"] == 935
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hr"]["digests"]) == q011hs.Q011HR_DIGESTS
    assert sealed["q011hr"]["artifact_sha256"] == q011hs.Q011HR_ARTIFACT_SHA256
    assert sealed["q011hr"]["runner_sha256"] == q011hs.Q011HR_RUNNER_SHA256
    assert sealed["q011hr"]["resolved_witness_digest_sha256"] == (
        q011hs.EXPECTED_ORDINAL_SEVENTY_TWO_RESOLUTION_DIGEST
    )


def test_q011hs_selects_exactly_flatten_ordinal_seventy_three(
    q011hs_structure: dict[str, Any],
) -> None:
    fixed = q011hs_structure["fixed"]
    selection = fixed["seventy_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 73
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(73))
    assert selection["ordinal_seventy_two_resolution_digest_sha256"] == (
        q011hs.EXPECTED_ORDINAL_SEVENTY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["seventy_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 665
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hs.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011hs.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011hs.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hs_reconstructs_registered_partition_and_inventory(
    q011hs_structure: dict[str, Any],
) -> None:
    fixed = q011hs_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [1, 6]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011hs.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011hs.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 11_760
    assert fixed["full_allocation_digest_sha256"] == q011hs.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 665
    assert q011hs_structure["compatible_count"] == 665
    assert fixed["compatible_allocation_digest_sha256"] == q011hs.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 11_676
    assert fixed["parent_witness_compatible_index"] == 664
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hs result is not sealed")
def test_q011hs_classifies_every_registered_exact_interval(q011hs_cycle: dict[str, Any]) -> None:
    partition = q011hs_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 665
    records = partition["allocation_classification_records"]
    assert len(records) == 665
    assert [record["compatible_allocation_index"] for record in records] == list(range(665))
    assert sum(partition["exact_relation_counts"].values()) == 665
    assert sum(partition["binary64_outward_relation_counts"].values()) == 665
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hs result is not sealed")
def test_q011hs_applies_the_registered_exclusive_stopping_rule(
    q011hs_cycle: dict[str, Any],
) -> None:
    assert q011hs_cycle["study_validity"] == "passed"
    assert q011hs_cycle["failed_validity_order"] == []
    assert q011hs_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hs_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hs_cycle["diagnostic_gates"].values())
    assert q011hs_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hs_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hs_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011hs.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011hs.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011hs.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011hs_cycle["diagnostic_classification"] == expected
    assert not q011hs_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hs_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_fourth_q011cb_witness"],
        theorem["seventy_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_fourth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hs result is not sealed")
def test_q011hs_preserves_boundary_and_reproducible_digests(
    q011hs_cycle: dict[str, Any],
) -> None:
    theorem = q011hs_cycle["theorem_consequence"]
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
    assert "flatten ordinal 73" in q011hs_cycle["claim_boundary"]
    assert "ordinals 0 through 72" in q011hs_cycle["claim_boundary"]
    assert "later 44726 Q011cb refined signatures" in q011hs_cycle["claim_boundary"]
    assert "Q011ht" in q011hs_cycle["next_change"]
    json.dumps(q011hs_cycle, allow_nan=False)
    assert {name: q011hs_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hs_cycle["result_digest_sha256"] == (
        q011hs.q011b._canonical_json_sha256(q011hs._result_digest_sections(q011hs_cycle))
    )
    assert q011hs._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hs result is not sealed")
def test_q011hs_study_metadata_and_optional_artifact_are_scoped(
    q011hs_study: dict[str, Any],
) -> None:
    assert q011hs_study["schema_version"] == 1
    assert q011hs_study["source"] == source_metadata()
    assert q011hs_study["study_gate"] == "passed"
    assert q011hs_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hs_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 665
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hs_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 73
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hs_study, allow_nan=False)

    runner_path = Path(q011hs.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hs_degree34_seventy_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hs artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hs_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hs.q011b._canonical_json_sha256(q011hs._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
