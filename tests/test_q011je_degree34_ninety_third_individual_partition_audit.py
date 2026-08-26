from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011je_degree34_ninety_third_individual_partition_audit as q011je
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "be4ce8eff51fc7762ad8cc77f45b3205827db0621c0c07b4b0b96b92b7c96a54"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "73da97f0f52bd028239578a5f98a0cc19523d2afd0decb83cc2df4b82b463ce0"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "d649fe6ed7ccd3cc92e67c7787acf7eb859995092dec97ed2a2a3a787624cc68",
    "partition_input_digest_sha256": "02b729940f1324d8ccd818e78765c478f8c775d391e913ee2ded2940cf28913e",
    "allocation_audit_digest_sha256": "a971dbbaed748216dfc0949f7ea64f5993babe9fc9c977ce94e247f08e075372",
    "result_digest_sha256": "c554589f49c3743d0f22d6fb45e50d30bffcf27e620ca19dd121290e8d31a3fc",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "feb1c0dfa787fb11598d6afc9fb24cf625c49016d6bb2302e748ff9dc9b870d3",
    "parent_center_product_interval_digest_sha256": "5f830b28915f0d5f8230436a9ce0baa1d239f132e87cef5946c240f7d600e52d",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "3efaf376cb871dba02df5be2bd7e506eb4760b3f9ecede3c776a3e76c5948057",
    "allocation_classification_record_digest_sha256": "e1e8baf8d04d94260b982b4e2e87d386ad4012351cb96547f7f590904f76aae9",
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
def q011je_structure() -> dict[str, Any]:
    sealed, artifacts = q011je._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011je._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011je_study() -> dict[str, Any]:
    return q011je.run_q011je_study()


@pytest.fixture(scope="module")
def q011je_cycle(q011je_study: dict[str, Any]) -> dict[str, Any]:
    return q011je_study["cycle"]


def test_q011je_seals_q011jd_and_all_prior_inputs(
    q011je_structure: dict[str, Any],
) -> None:
    sealed = q011je_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 243
    assert sealed["direct_digest_count"] == 1_106
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jd"]["digests"]) == q011je.Q011JD_DIGESTS
    assert sealed["q011jd"]["artifact_sha256"] == q011je.Q011JD_ARTIFACT_SHA256
    assert sealed["q011jd"]["runner_sha256"] == q011je.Q011JD_RUNNER_SHA256
    assert sealed["q011jd"]["resolved_witness_digest_sha256"] == (
        q011je.EXPECTED_ORDINAL_NINETY_ONE_RESOLUTION_DIGEST
    )


def test_q011je_selects_exactly_flatten_ordinal_ninety_two(
    q011je_structure: dict[str, Any],
) -> None:
    fixed = q011je_structure["fixed"]
    selection = fixed["ninety_third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 92
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(92))
    assert selection["ordinal_ninety_one_resolution_digest_sha256"] == (
        q011je.EXPECTED_ORDINAL_NINETY_ONE_RESOLUTION_DIGEST
    )
    parent = selection["ninety_third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 3_104
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011je.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011je.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011je.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011je_reconstructs_registered_partition_and_inventory(
    q011je_structure: dict[str, Any],
) -> None:
    fixed = q011je_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [4, 3]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011je.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011je.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 56_160
    assert fixed["full_allocation_digest_sha256"] == q011je.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_104
    assert q011je_structure["compatible_count"] == 3_104
    assert fixed["compatible_allocation_digest_sha256"] == q011je.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 56_040
    assert fixed["parent_witness_compatible_index"] == 3_103
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011je result is not sealed")
def test_q011je_classifies_every_registered_exact_interval(
    q011je_cycle: dict[str, Any],
) -> None:
    partition = q011je_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 3_104
    records = partition["allocation_classification_records"]
    assert len(records) == 3_104
    assert [record["compatible_allocation_index"] for record in records] == list(range(3_104))
    assert sum(partition["exact_relation_counts"].values()) == 3_104
    assert sum(partition["binary64_outward_relation_counts"].values()) == 3_104
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011je result is not sealed")
def test_q011je_applies_registered_stopping_rule(
    q011je_cycle: dict[str, Any],
) -> None:
    assert q011je_cycle["study_validity"] == "passed"
    assert q011je_cycle["failed_validity_order"] == []
    assert q011je_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011je_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011je_cycle["diagnostic_gates"].values())
    assert q011je_cycle["scientific_outcome"] == "not_evaluated"
    assert q011je_cycle["actual_resonance_outcome"] == "not_established"
    assert q011je_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011je.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011je.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011je.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011je_cycle["diagnostic_classification"] == expected
    assert not q011je_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011je_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_third_q011cb_witness"],
        theorem["ninety_third_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninety_third_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011je result is not sealed")
def test_q011je_preserves_boundary_and_reproducible_digests(
    q011je_cycle: dict[str, Any],
) -> None:
    theorem = q011je_cycle["theorem_consequence"]
    assert theorem["q011jd_ordinal_ninety_one_phase_resolution_is_preserved"]
    assert theorem["q011jc_ordinal_ninety_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jb_ordinal_ninety_phase_resolution_is_preserved"]
    assert theorem["q011ja_ordinal_ninety_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011iz_ordinal_eighty_nine_phase_resolution_is_preserved"]
    assert theorem["q011iy_ordinal_eighty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ix_ordinal_eighty_eight_phase_resolution_is_preserved"]
    assert theorem["q011iw_ordinal_eighty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 92" in q011je_cycle["claim_boundary"]
    assert "ordinals 0 through 91" in q011je_cycle["claim_boundary"]
    assert "later 44707 Q011cb refined signatures" in q011je_cycle["claim_boundary"]
    assert "Q011jf" in q011je_cycle["next_change"]
    assert {name: q011je_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011je_cycle["result_digest_sha256"] == (
        q011je.q011b._canonical_json_sha256(q011je._result_digest_sections(q011je_cycle))
    )
    assert q011je._protocol_globals_are_restored()
    json.dumps(q011je_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011je result is not sealed")
def test_q011je_study_metadata_and_optional_artifact_are_scoped(
    q011je_study: dict[str, Any],
) -> None:
    assert q011je_study["schema_version"] == 1
    assert q011je_study["source"] == source_metadata()
    assert q011je_study["study_gate"] == "passed"
    assert q011je_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011je_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_104
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011je_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 92
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011je_study, allow_nan=False)

    runner_path = Path(q011je.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011je_degree34_ninety_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011je artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011je_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011je.q011b._canonical_json_sha256(q011je._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
