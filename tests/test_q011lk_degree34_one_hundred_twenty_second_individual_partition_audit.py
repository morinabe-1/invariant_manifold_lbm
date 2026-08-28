from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011lk_degree34_one_hundred_twenty_second_individual_partition_audit as q011lk
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "5795aba8d6e92a644beabc928cbbc52f84226d407f3302c6bb9eac47234414a0"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "b23174a03cc731dd7c3f484916e5ee40c92c55e5084d891e9aff1da730c3b3d7"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "bb6746339f3467d8db9f250b7ac806c4521d44cf31340f990703f5c8f0ec8046",
    "partition_input_digest_sha256": (
        "a739d1c07bafa63bb00e599e6581c3efb8db05301795ca90f0c8669ff3067c7f"
    ),
    "allocation_audit_digest_sha256": (
        "eac613af996f118c80f082dc727c4bfa01e3e47c5d625bf16845ae555f79bdcd"
    ),
    "result_digest_sha256": "6f25c899e4abaadcf4c12ed3ad756df9c0ad60c232534533cbd8509df14c6160",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "371f89967562b2097d01fed76cc2c71f1fa0427fd1931f4239e5f301cc6e5fcd"
    ),
    "parent_center_product_interval_digest_sha256": (
        "7de6e11147a99ac5bd2c1f76f7369238bbc5607edbbc0866c6d2fe6d81714dd5"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "ee6ad58b05b7e3610ef0f7a88c8c5c3a9b74f4acf7f80fa514edf5a1d72391fd"
    ),
    "allocation_classification_record_digest_sha256": (
        "0718ed4ecb575cb3e171933f7d8eefc86711fdac02c86929eecdfb9bd086b8b1"
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
def q011lk_structure() -> dict[str, Any]:
    sealed, artifacts = q011lk._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011lk._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011lk_study() -> dict[str, Any]:
    return q011lk.run_q011lk_study()


@pytest.fixture(scope="module")
def q011lk_cycle(q011lk_study: dict[str, Any]) -> dict[str, Any]:
    return q011lk_study["cycle"]


def test_q011lk_seals_q011lj_and_all_prior_inputs(
    q011lk_structure: dict[str, Any],
) -> None:
    sealed = q011lk_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 301
    assert sealed["direct_digest_count"] == 1_367
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011lj"]["digests"]) == q011lk.Q011LJ_DIGESTS
    assert sealed["q011lj"]["artifact_sha256"] == q011lk.Q011LJ_ARTIFACT_SHA256
    assert sealed["q011lj"]["runner_sha256"] == q011lk.Q011LJ_RUNNER_SHA256
    assert sealed["q011lj"]["resolved_witness_digest_sha256"] == (
        q011lk.EXPECTED_ORDINAL_ONE_HUNDRED_TWENTY_RESOLUTION_DIGEST
    )


def test_q011lk_selects_exactly_flatten_ordinal_one_hundred_twenty_one(
    q011lk_structure: dict[str, Any],
) -> None:
    fixed = q011lk_structure["fixed"]
    selection = fixed["one_hundred_twenty_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 121
    assert selection["selected_left_index"] == 15
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(121))
    assert selection["ordinal_one_hundred_twenty_resolution_digest_sha256"] == (
        q011lk.EXPECTED_ORDINAL_ONE_HUNDRED_TWENTY_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_twenty_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [5, 4], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 3_626
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011lk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011lk.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011lk.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011lk_reconstructs_registered_partition_and_inventory(
    q011lk_structure: dict[str, Any],
) -> None:
    fixed = q011lk_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [5, 4], [5], [1, 6]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 5, 4, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011lk.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011lk.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 65_520
    assert fixed["full_allocation_digest_sha256"] == q011lk.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_626
    assert q011lk_structure["compatible_count"] == 3_626
    assert fixed["compatible_allocation_digest_sha256"] == q011lk.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 5, 0, 4, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 5, 0, 4, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 65_436
    assert fixed["parent_witness_compatible_index"] == 3_625
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lk result is not sealed")
def test_q011lk_classifies_every_registered_exact_interval(
    q011lk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011lk_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 3_626
    records = partition["allocation_classification_records"]
    assert len(records) == 3_626
    assert [record["compatible_allocation_index"] for record in records] == list(range(3_626))
    assert sum(partition["exact_relation_counts"].values()) == 3_626
    assert sum(partition["binary64_outward_relation_counts"].values()) == 3_626
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lk result is not sealed")
def test_q011lk_applies_registered_stopping_rule(
    q011lk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011lk_cycle["study_validity"] == "passed"
    assert q011lk_cycle["failed_validity_order"] == []
    assert q011lk_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011lk_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011lk_cycle["diagnostic_gates"].values())
    assert q011lk_cycle["scientific_outcome"] == "not_evaluated"
    assert q011lk_cycle["actual_resonance_outcome"] == "not_established"
    assert q011lk_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011lk.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011lk.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011lk.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011lk_cycle["diagnostic_classification"] == expected
    assert not q011lk_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011lk_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_twenty_second_q011cb_witness"
        ],
        theorem["one_hundred_twenty_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_twenty_second_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lk result is not sealed")
def test_q011lk_preserves_boundary_and_reproducible_digests(
    q011lk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011lk_cycle["theorem_consequence"]
    assert theorem["q011lj_ordinal_one_hundred_twenty_phase_resolution_is_preserved"]
    assert theorem["q011lh_ordinal_one_hundred_nineteen_phase_resolution_is_preserved"]
    assert theorem["q011lg_ordinal_one_hundred_nineteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011le_ordinal_one_hundred_eighteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011lc_ordinal_one_hundred_seventeen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ku_ordinal_one_hundred_thirteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kq_ordinal_one_hundred_eleven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011km_ordinal_one_hundred_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kj_ordinal_one_hundred_seven_phase_resolution_is_preserved"]
    assert theorem["q011ke_ordinal_one_hundred_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kd_ordinal_one_hundred_four_phase_resolution_is_preserved"]
    assert theorem["q011kc_ordinal_one_hundred_four_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 121" in q011lk_cycle["claim_boundary"]
    assert "ordinals 0 through 120" in q011lk_cycle["claim_boundary"]
    assert "later 44678 Q011cb refined signatures" in q011lk_cycle["claim_boundary"]
    assert "Q011ll" in q011lk_cycle["next_change"]
    assert {name: q011lk_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011lk_cycle["result_digest_sha256"] == (
        q011lk.q011b._canonical_json_sha256(q011lk._result_digest_sections(q011lk_cycle))
    )
    assert q011lk._protocol_globals_are_restored()
    json.dumps(q011lk_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lk result is not sealed")
def test_q011lk_study_metadata_and_optional_artifact_are_scoped(
    q011lk_study: dict[str, Any],
) -> None:
    assert q011lk_study["schema_version"] == 1
    assert q011lk_study["source"] == source_metadata()
    assert q011lk_study["study_gate"] == "passed"
    assert q011lk_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011lk_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_626
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011lk_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 121
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011lk_study, allow_nan=False)

    runner_path = Path(q011lk.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011lk_degree34_one_hundred_twenty_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011lk artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011lk_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011lk.q011b._canonical_json_sha256(q011lk._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
