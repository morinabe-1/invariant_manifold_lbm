from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jc_degree34_ninety_second_individual_partition_audit as q011jc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "a4ef2301bd334bdb5499ecd262b1de1518918a95ae9fd9ec3f38a717465cc069"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "32af92d335732846a1d645ae4a5568b13c811e3dcb32fb64eeecc03f0fe80453"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "56332a9e9bb82c113d53d2ea14bd04d260a7637d2f00ba80615845b4deb6ac72",
    "partition_input_digest_sha256": "dfe3a7f5a7177cfedda6007aeb54fa260cc2bf52d593d37e275d461880bb379f",
    "allocation_audit_digest_sha256": "9f2f68fd87692176af66b23baff0571725f6197a14a94b417ca54f9270b42b65",
    "result_digest_sha256": "7b1acdbf842579b6ead1495e19c744376d1ef22e7e943a2ca6683c180e13f9a7",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "f7baa7108a22d9a01899b435da11765daabb71654697e67435cf10fbf4e3d0e7",
    "parent_center_product_interval_digest_sha256": "9ad6a32bacce9ecdb8474525449985776fc278b578cb8d768b58fdac46883e4d",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "45ce5b1d80669dd9de6750e5efb27c3df49abb069f1ab54a2c9e0894437a83b2",
    "allocation_classification_record_digest_sha256": "0f29b16bd26d3f937eed8723d3ee272e33fe4b0233536b51ab3e14e7e02ba294",
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
def q011jc_structure() -> dict[str, Any]:
    sealed, artifacts = q011jc._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011jc._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011jc_study() -> dict[str, Any]:
    return q011jc.run_q011jc_study()


@pytest.fixture(scope="module")
def q011jc_cycle(q011jc_study: dict[str, Any]) -> dict[str, Any]:
    return q011jc_study["cycle"]


def test_q011jc_seals_q011jb_and_all_prior_inputs(
    q011jc_structure: dict[str, Any],
) -> None:
    sealed = q011jc_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 241
    assert sealed["direct_digest_count"] == 1_097
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jb"]["digests"]) == q011jc.Q011JB_DIGESTS
    assert sealed["q011jb"]["artifact_sha256"] == q011jc.Q011JB_ARTIFACT_SHA256
    assert sealed["q011jb"]["runner_sha256"] == q011jc.Q011JB_RUNNER_SHA256
    assert sealed["q011jb"]["resolved_witness_digest_sha256"] == (
        q011jc.EXPECTED_ORDINAL_NINETY_RESOLUTION_DIGEST
    )


def test_q011jc_selects_exactly_flatten_ordinal_ninety_one(
    q011jc_structure: dict[str, Any],
) -> None:
    fixed = q011jc_structure["fixed"]
    selection = fixed["ninety_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 91
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(91))
    assert selection["ordinal_ninety_resolution_digest_sha256"] == (
        q011jc.EXPECTED_ORDINAL_NINETY_RESOLUTION_DIGEST
    )
    parent = selection["ninety_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 3_104
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011jc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011jc.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011jc.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011jc_reconstructs_registered_partition_and_inventory(
    q011jc_structure: dict[str, Any],
) -> None:
    fixed = q011jc_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [3, 4]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011jc.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011jc.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 56_160
    assert fixed["full_allocation_digest_sha256"] == q011jc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_104
    assert q011jc_structure["compatible_count"] == 3_104
    assert fixed["compatible_allocation_digest_sha256"] == q011jc.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 56_040
    assert fixed["parent_witness_compatible_index"] == 3_103
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jc result is not sealed")
def test_q011jc_classifies_every_registered_exact_interval(
    q011jc_cycle: dict[str, Any],
) -> None:
    partition = q011jc_cycle["individual_allocation_interval_audit"]
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jc result is not sealed")
def test_q011jc_applies_registered_stopping_rule(
    q011jc_cycle: dict[str, Any],
) -> None:
    assert q011jc_cycle["study_validity"] == "passed"
    assert q011jc_cycle["failed_validity_order"] == []
    assert q011jc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jc_cycle["diagnostic_gates"].values())
    assert q011jc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jc_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jc_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011jc.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011jc.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011jc.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jc_cycle["diagnostic_classification"] == expected
    assert not q011jc_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011jc_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_second_q011cb_witness"],
        theorem["ninety_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninety_second_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jc result is not sealed")
def test_q011jc_preserves_boundary_and_reproducible_digests(
    q011jc_cycle: dict[str, Any],
) -> None:
    theorem = q011jc_cycle["theorem_consequence"]
    assert theorem["q011jb_ordinal_ninety_phase_resolution_is_preserved"]
    assert theorem["q011ja_ordinal_ninety_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 91" in q011jc_cycle["claim_boundary"]
    assert "ordinals 0 through 90" in q011jc_cycle["claim_boundary"]
    assert "later 44708 Q011cb refined signatures" in q011jc_cycle["claim_boundary"]
    assert "Q011jd" in q011jc_cycle["next_change"]
    assert {name: q011jc_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jc_cycle["result_digest_sha256"] == (
        q011jc.q011b._canonical_json_sha256(q011jc._result_digest_sections(q011jc_cycle))
    )
    assert q011jc._protocol_globals_are_restored()
    json.dumps(q011jc_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jc result is not sealed")
def test_q011jc_study_metadata_and_optional_artifact_are_scoped(
    q011jc_study: dict[str, Any],
) -> None:
    assert q011jc_study["schema_version"] == 1
    assert q011jc_study["source"] == source_metadata()
    assert q011jc_study["study_gate"] == "passed"
    assert q011jc_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jc_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_104
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 91
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jc_study, allow_nan=False)

    runner_path = Path(q011jc.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jc_degree34_ninety_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jc_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jc.q011b._canonical_json_sha256(q011jc._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
