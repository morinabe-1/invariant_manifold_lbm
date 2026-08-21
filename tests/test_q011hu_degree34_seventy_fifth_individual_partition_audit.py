from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011hu_degree34_seventy_fifth_individual_partition_audit as q011hu
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d2ad64ec7a7dc410f3b3cd180eaf2259bf61af04399c15e4957d74431ea3fea6"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "caa55b26ad77236fb9e69b50c233820eb4ab70c2c99225d2876dcaf72bd8ab79"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "489e5670d1343d1c878ab6a23e75e8bc758c818a8bbe1c42a58c916ab132b107",
    "partition_input_digest_sha256": "46e5ea430ac5f8de4da9618818f73db4cb9d0dde7af027c9c33317319d825bff",
    "allocation_audit_digest_sha256": "a0d8ccb488df039f61c1b4829314f02eea7fde64d627b6a5ceb9c903c36069ec",
    "result_digest_sha256": "f9fde6e0278693c664361128a84b40b8279c59bf551609b53fe0b40b52e2b7af",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "f06c8b4fea03ec54b067698bc35638f00a9a14ec581953151d75f132a900755c",
    "parent_center_product_interval_digest_sha256": "d51ac6701e1ef3cbdd7e480a31ce60b592d7efddc48db8fab0982f06cfc94a0a",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "90a053cde68acf8087d649a09a90d6b7e5783a3110ac8eac05585aca1f7448ac",
    "allocation_classification_record_digest_sha256": "6191fd85ccb914d06545bc3432c520aa94604c6b8ea08c4cc2da9e011ccae793",
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
def q011hu_structure() -> dict[str, Any]:
    sealed, artifacts = q011hu._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011hu._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011hu_study() -> dict[str, Any]:
    return q011hu.run_q011hu_study()


@pytest.fixture(scope="module")
def q011hu_cycle(q011hu_study: dict[str, Any]) -> dict[str, Any]:
    return q011hu_study["cycle"]


def test_q011hu_seals_q011ht_and_all_prior_inputs(q011hu_structure: dict[str, Any]) -> None:
    sealed = q011hu_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 207
    assert sealed["direct_digest_count"] == 944
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ht"]["digests"]) == q011hu.Q011HT_DIGESTS
    assert sealed["q011ht"]["artifact_sha256"] == q011hu.Q011HT_ARTIFACT_SHA256
    assert sealed["q011ht"]["runner_sha256"] == q011hu.Q011HT_RUNNER_SHA256
    assert sealed["q011ht"]["resolved_witness_digest_sha256"] == (
        q011hu.EXPECTED_ORDINAL_SEVENTY_THREE_RESOLUTION_DIGEST
    )


def test_q011hu_selects_exactly_flatten_ordinal_seventy_four(
    q011hu_structure: dict[str, Any],
) -> None:
    fixed = q011hu_structure["fixed"]
    selection = fixed["seventy_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 74
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(74))
    assert selection["ordinal_seventy_three_resolution_digest_sha256"] == (
        q011hu.EXPECTED_ORDINAL_SEVENTY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["seventy_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 852
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011hu.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011hu.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011hu.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011hu_reconstructs_registered_partition_and_inventory(
    q011hu_structure: dict[str, Any],
) -> None:
    fixed = q011hu_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [2, 5]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011hu.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011hu.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 15_120
    assert fixed["full_allocation_digest_sha256"] == q011hu.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 852
    assert q011hu_structure["compatible_count"] == 852
    assert fixed["compatible_allocation_digest_sha256"] == q011hu.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 15_012
    assert fixed["parent_witness_compatible_index"] == 851
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hu result is not sealed")
def test_q011hu_classifies_every_registered_exact_interval(q011hu_cycle: dict[str, Any]) -> None:
    partition = q011hu_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 852
    records = partition["allocation_classification_records"]
    assert len(records) == 852
    assert [record["compatible_allocation_index"] for record in records] == list(range(852))
    assert sum(partition["exact_relation_counts"].values()) == 852
    assert sum(partition["binary64_outward_relation_counts"].values()) == 852
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hu result is not sealed")
def test_q011hu_applies_the_registered_exclusive_stopping_rule(
    q011hu_cycle: dict[str, Any],
) -> None:
    assert q011hu_cycle["study_validity"] == "passed"
    assert q011hu_cycle["failed_validity_order"] == []
    assert q011hu_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011hu_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011hu_cycle["diagnostic_gates"].values())
    assert q011hu_cycle["scientific_outcome"] == "not_evaluated"
    assert q011hu_cycle["actual_resonance_outcome"] == "not_established"
    assert q011hu_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011hu.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011hu.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011hu.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011hu_cycle["diagnostic_classification"] == expected
    assert not q011hu_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011hu_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_fifth_q011cb_witness"],
        theorem["seventy_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_fifth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hu result is not sealed")
def test_q011hu_preserves_boundary_and_reproducible_digests(
    q011hu_cycle: dict[str, Any],
) -> None:
    theorem = q011hu_cycle["theorem_consequence"]
    assert theorem["q011ht_ordinal_seventy_three_phase_resolution_is_preserved"]
    assert theorem["q011hs_ordinal_seventy_three_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 74" in q011hu_cycle["claim_boundary"]
    assert "ordinals 0 through 73" in q011hu_cycle["claim_boundary"]
    assert "later 44725 Q011cb refined signatures" in q011hu_cycle["claim_boundary"]
    assert "Q011hv" in q011hu_cycle["next_change"]
    json.dumps(q011hu_cycle, allow_nan=False)
    assert {name: q011hu_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011hu_cycle["result_digest_sha256"] == (
        q011hu.q011b._canonical_json_sha256(q011hu._result_digest_sections(q011hu_cycle))
    )
    assert q011hu._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011hu result is not sealed")
def test_q011hu_study_metadata_and_optional_artifact_are_scoped(
    q011hu_study: dict[str, Any],
) -> None:
    assert q011hu_study["schema_version"] == 1
    assert q011hu_study["source"] == source_metadata()
    assert q011hu_study["study_gate"] == "passed"
    assert q011hu_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011hu_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 852
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011hu_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 74
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011hu_study, allow_nan=False)

    runner_path = Path(q011hu.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011hu_degree34_seventy_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011hu artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011hu_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011hu.q011b._canonical_json_sha256(q011hu._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
