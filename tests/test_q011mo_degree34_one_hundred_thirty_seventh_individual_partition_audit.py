from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mo_degree34_one_hundred_thirty_seventh_individual_partition_audit as q011mo
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "7e4b877ad479938079517b2f90bbd3d6b31cf7cfd119b01384dbe10dce3a39ae"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "b6cc899aea0290697201a661ca5bd4dcb2939fcb4367a0414816e06715a58421"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "a77b96f32263c738b80437482e748eaab86d8d87d49b48f8e1e680ad8a631c96",
    "partition_input_digest_sha256": (
        "8e96390f74ac7b472a927f3670976b322224001cbb0957bac9f2096b027b6a10"
    ),
    "allocation_audit_digest_sha256": (
        "8efc143c7249f43fc306ff3ce4014745d146b6df8da3e52a96ecbd5ab4e25be3"
    ),
    "result_digest_sha256": "e00687da06b7224478d4944d21b0cbb2912a290c208ca6874ffa91ac6e1bd036",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "5d01f5f0ddd84669c9aea65c7b59fc777f59d65d1f46e7d40c5fb7437d7b0b2a"
    ),
    "parent_center_product_interval_digest_sha256": (
        "8e2eb300b288a76ea8c12cab263a4d7c0038ed8ba8308d0d6ace07057b16794a"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "902f32def2a9b6e06e2c437e1b18c2ab67c92dbf4a479bf9866bbff11c57c144"
    ),
    "allocation_classification_record_digest_sha256": (
        "b6a01b1a6602d40f58d8257573492d60ab09ec7f4bdf347d67c300a728783201"
    ),
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
def q011mo_structure() -> dict[str, Any]:
    sealed, artifacts = q011mo._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011mo._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011mo_study() -> dict[str, Any]:
    return q011mo.run_q011mo_study()


@pytest.fixture(scope="module")
def q011mo_cycle(q011mo_study: dict[str, Any]) -> dict[str, Any]:
    return q011mo_study["cycle"]


def test_q011mo_seals_q011mn_and_all_prior_inputs(q011mo_structure: dict[str, Any]) -> None:
    sealed = q011mo_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 331
    assert sealed["direct_digest_count"] == 1_502
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mn"]["digests"]) == q011mo.Q011MN_DIGESTS
    assert sealed["q011mn"]["artifact_sha256"] == q011mo.Q011MN_ARTIFACT_SHA256
    assert sealed["q011mn"]["runner_sha256"] == q011mo.Q011MN_RUNNER_SHA256
    assert sealed["q011mn"]["resolved_witness_digest_sha256"] == (
        q011mo.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011mo_selects_exactly_flatten_ordinal_one_hundred_thirty_six(
    q011mo_structure: dict[str, Any],
) -> None:
    fixed = q011mo_structure["fixed"]
    selection = fixed["one_hundred_thirty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 136
    assert selection["selected_left_index"] == 17
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(136))
    assert selection["ordinal_one_hundred_thirty_five_resolution_digest_sha256"] == (
        q011mo.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_thirty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_667
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011mo.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == q011mo.EXPECTED_PARENT_CENTER_GAP_HEX
    assert parent["witness_digest_sha256"] == q011mo.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011mo_reconstructs_registered_partition_and_inventory(
    q011mo_structure: dict[str, Any],
) -> None:
    fixed = q011mo_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [0, 7]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 7, 2, 5, 7]
    assert any(
        identifier.endswith("center=149")
        for record in occupied
        for identifier in record["identifiers"]
    )
    assert all(
        not identifier.endswith("center=148")
        for record in occupied
        for identifier in record["identifiers"]
    )
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011mo.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011mo.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 29_952
    assert fixed["full_allocation_digest_sha256"] == q011mo.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_667
    assert q011mo_structure["compatible_count"] == 1_667
    assert fixed["compatible_allocation_digest_sha256"] == q011mo.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 7, 0, 2, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 7, 0, 2, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 29_904
    assert fixed["parent_witness_compatible_index"] == 1_666
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mo result is not sealed")
def test_q011mo_classifies_every_registered_exact_interval(
    q011mo_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011mo_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_667
    records = partition["allocation_classification_records"]
    assert len(records) == 1_667
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_667))
    assert sum(partition["exact_relation_counts"].values()) == 1_667
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_667
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mo result is not sealed")
def test_q011mo_applies_registered_stopping_rule(q011mo_cycle: dict[str, Any]) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011mo_cycle["study_validity"] == "passed"
    assert q011mo_cycle["failed_validity_order"] == []
    assert q011mo_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mo_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mo_cycle["diagnostic_gates"].values())
    assert q011mo_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mo_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mo_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011mo.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011mo.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011mo.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mo_cycle["diagnostic_classification"] == expected
    assert not q011mo_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011mo_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_thirty_seventh_q011cb_witness"
        ],
        theorem["one_hundred_thirty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_thirty_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mo result is not sealed")
def test_q011mo_preserves_boundary_and_reproducible_digests(
    q011mo_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011mo_cycle["theorem_consequence"]
    assert theorem["q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 136" in q011mo_cycle["claim_boundary"]
    assert "ordinals 0 through 135" in q011mo_cycle["claim_boundary"]
    assert "later 44663 " in q011mo_cycle["claim_boundary"]
    assert "Q011mp" in q011mo_cycle["next_change"]
    assert {name: q011mo_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mo_cycle["result_digest_sha256"] == (
        q011mo.q011b._canonical_json_sha256(q011mo._result_digest_sections(q011mo_cycle))
    )
    assert q011mo._protocol_globals_are_restored()
    json.dumps(q011mo_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mo result is not sealed")
def test_q011mo_study_metadata_and_optional_artifact_are_scoped(
    q011mo_study: dict[str, Any],
) -> None:
    assert q011mo_study["schema_version"] == 1
    assert q011mo_study["source"] == source_metadata()
    assert q011mo_study["study_gate"] == "passed"
    assert q011mo_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mo_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_667
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mo_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 136
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mo_study, allow_nan=False)

    runner_path = Path(q011mo.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mo_degree34_one_hundred_thirty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mo artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mo_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mo.q011b._canonical_json_sha256(q011mo._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
