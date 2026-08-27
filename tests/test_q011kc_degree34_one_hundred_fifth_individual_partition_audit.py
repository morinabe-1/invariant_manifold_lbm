from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011kc_degree34_one_hundred_fifth_individual_partition_audit as q011kc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "6049c02cbd66a11ee33a5cce0e0d3be2e8a690dc790f3e627ca7c648fb9aa929"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "840e09df18a47ce15a1b4e5d2b3b524af83a40bb979b68ad437614704868f7a5"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "b8310055a6276a3327031a0a59eee861a53ab1486bccf92a44ae1d30cca443a3",
    "partition_input_digest_sha256": (
        "0e73511f3862f8b033eaae45b58cb96ebdea7dfe97fbbb193f3c94c30f0b39a9"
    ),
    "allocation_audit_digest_sha256": (
        "561b98ae63a08ebbc246c739662c1c24958e006c3a9663d7c998e65a99a150d2"
    ),
    "result_digest_sha256": "16443435f09e8b9b009c5464a2457c2a4d6e8e90be0553424d13ce78a0120bdf",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "df72c36ed66f0faf136fa42c3e4a73771ceaae3a9a08ae71e98143fd466677db"
    ),
    "parent_center_product_interval_digest_sha256": (
        "85b7c141357775d248e7be431d646f39706f1e5ee669473a73c30ed2affea4f5"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "3a2128fe892ff91f2f164a678e06bf4a2879d775cd8525b0b30141dc6107dabc"
    ),
    "allocation_classification_record_digest_sha256": (
        "c0c8d32b0e6daf90cc28185a2edbbff6c57c0de21334777daf95544a2fac3af1"
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
def q011kc_structure() -> dict[str, Any]:
    sealed, artifacts = q011kc._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011kc._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011kc_study() -> dict[str, Any]:
    return q011kc.run_q011kc_study()


@pytest.fixture(scope="module")
def q011kc_cycle(q011kc_study: dict[str, Any]) -> dict[str, Any]:
    return q011kc_study["cycle"]


def test_q011kc_seals_q011kb_and_all_prior_inputs(
    q011kc_structure: dict[str, Any],
) -> None:
    sealed = q011kc_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 267
    assert sealed["direct_digest_count"] == 1_214
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011kb"]["digests"]) == q011kc.Q011KB_DIGESTS
    assert sealed["q011kb"]["artifact_sha256"] == q011kc.Q011KB_ARTIFACT_SHA256
    assert sealed["q011kb"]["runner_sha256"] == q011kc.Q011KB_RUNNER_SHA256
    assert sealed["q011kb"]["resolved_witness_digest_sha256"] == (
        q011kc.EXPECTED_ORDINAL_ONE_HUNDRED_THREE_RESOLUTION_DIGEST
    )


def test_q011kc_selects_exactly_flatten_ordinal_one_hundred_four(
    q011kc_structure: dict[str, Any],
) -> None:
    fixed = q011kc_structure["fixed"]
    selection = fixed["one_hundred_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 104
    assert selection["selected_left_index"] == 13
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(104))
    assert selection["ordinal_one_hundred_three_resolution_digest_sha256"] == (
        q011kc.EXPECTED_ORDINAL_ONE_HUNDRED_THREE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [3, 6], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_940
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011kc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011kc.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011kc.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011kc_reconstructs_registered_partition_and_inventory(
    q011kc_structure: dict[str, Any],
) -> None:
    fixed = q011kc_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [3, 6], [5], [0, 7]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 3, 6, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011kc.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011kc.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 34_944
    assert fixed["full_allocation_digest_sha256"] == q011kc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_940
    assert q011kc_structure["compatible_count"] == 1_940
    assert fixed["compatible_allocation_digest_sha256"] == q011kc.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [
        0,
        1,
        0,
        12,
        0,
        3,
        0,
        6,
        0,
        5,
        5,
        2,
    ]
    assert fixed["last_compatible_counts"] == [
        1,
        0,
        12,
        0,
        3,
        0,
        6,
        0,
        0,
        5,
        0,
        7,
    ]
    assert fixed["parent_witness_allocation_index"] == 34_896
    assert fixed["parent_witness_compatible_index"] == 1_939
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kc result is not sealed")
def test_q011kc_classifies_every_registered_exact_interval(
    q011kc_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011kc_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_940
    records = partition["allocation_classification_records"]
    assert len(records) == 1_940
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_940))
    assert sum(partition["exact_relation_counts"].values()) == 1_940
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_940
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kc result is not sealed")
def test_q011kc_applies_registered_stopping_rule(
    q011kc_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011kc_cycle["study_validity"] == "passed"
    assert q011kc_cycle["failed_validity_order"] == []
    assert q011kc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011kc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011kc_cycle["diagnostic_gates"].values())
    assert q011kc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011kc_cycle["actual_resonance_outcome"] == "not_established"
    assert q011kc_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011kc.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011kc.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011kc.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011kc_cycle["diagnostic_classification"] == expected
    assert not q011kc_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011kc_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_one_hundred_fifth_q011cb_witness"],
        theorem["one_hundred_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_fifth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kc result is not sealed")
def test_q011kc_preserves_boundary_and_reproducible_digests(
    q011kc_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011kc_cycle["theorem_consequence"]
    assert theorem["q011kb_ordinal_one_hundred_three_phase_resolution_is_preserved"]
    assert theorem["q011jw_ordinal_one_hundred_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ju_ordinal_one_hundred_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011js_ordinal_ninety_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jq_ordinal_ninety_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jp_ordinal_ninety_seven_phase_resolution_is_preserved"]
    assert theorem["q011jo_ordinal_ninety_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jn_ordinal_ninety_six_phase_resolution_is_preserved"]
    assert theorem["q011jm_ordinal_ninety_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jl_ordinal_ninety_five_phase_resolution_is_preserved"]
    assert theorem["q011jk_ordinal_ninety_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jj_ordinal_ninety_four_phase_resolution_is_preserved"]
    assert theorem["q011ji_ordinal_ninety_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jh_ordinal_ninety_three_phase_resolution_is_preserved"]
    assert theorem["q011jg_ordinal_ninety_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jf_ordinal_ninety_two_phase_resolution_is_preserved"]
    assert theorem["q011je_ordinal_ninety_two_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 104" in q011kc_cycle["claim_boundary"]
    assert "ordinals 0 through 103" in q011kc_cycle["claim_boundary"]
    assert "later 44695 Q011cb refined signatures" in q011kc_cycle["claim_boundary"]
    assert "Q011kd" in q011kc_cycle["next_change"]
    assert {name: q011kc_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011kc_cycle["result_digest_sha256"] == (
        q011kc.q011b._canonical_json_sha256(q011kc._result_digest_sections(q011kc_cycle))
    )
    assert q011kc._protocol_globals_are_restored()
    json.dumps(q011kc_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kc result is not sealed")
def test_q011kc_study_metadata_and_optional_artifact_are_scoped(
    q011kc_study: dict[str, Any],
) -> None:
    assert q011kc_study["schema_version"] == 1
    assert q011kc_study["source"] == source_metadata()
    assert q011kc_study["study_gate"] == "passed"
    assert q011kc_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011kc_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_940
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011kc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 104
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011kc_study, allow_nan=False)

    runner_path = Path(q011kc.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011kc_degree34_one_hundred_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011kc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011kc_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011kc.q011b._canonical_json_sha256(q011kc._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
