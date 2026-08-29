from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011lq_degree34_one_hundred_twenty_fifth_individual_partition_audit as q011lq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "2e7d0614997bd86795db387c895e3af8335a77d26f17241b91766fa8db987598"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "0aa1d6108a6355aa329ad9beaf8ba65ab3009bd6faeb03e2701f2e1268ce9a12"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "34de8f054eb007d19458da8e5a4f67bf977c95a4341e69156e64f02137bdd777",
    "partition_input_digest_sha256": "fd35abb49e3e96626202e51b4fb74d53fb38f6145fd446777571e3c4ed247bcc",
    "allocation_audit_digest_sha256": "5381a027a9d23c6fe7471b52ba5798f62c565b5c21f01a602a9bda8e3a0f9972",
    "result_digest_sha256": "6dade117828d06af1b30c493ca05a71935154b67e8def75bf46382b6c4390e83",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "48745acb2b047c8593336d0f47241f5cebd0bfa3a9f563c9bb1ff6b49e9dc8e1",
    "parent_center_product_interval_digest_sha256": "0ac71e3353dbb010db519d8cea216e729ccffee5dbe977ef6491abbfd293d895",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "37d31bebcf5ec22bb1476715854d87f14704e083caeaff666781d6f8c5c85106",
    "allocation_classification_record_digest_sha256": "7e96d1a3a5a4eff2d7051c650a74e59a6e59c5bbe271084a9593cc5499e70c83",
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
def q011lq_structure() -> dict[str, Any]:
    sealed, artifacts = q011lq._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011lq._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011lq_study() -> dict[str, Any]:
    return q011lq.run_q011lq_study()


@pytest.fixture(scope="module")
def q011lq_cycle(q011lq_study: dict[str, Any]) -> dict[str, Any]:
    return q011lq_study["cycle"]


def test_q011lq_seals_q011lp_and_all_prior_inputs(
    q011lq_structure: dict[str, Any],
) -> None:
    sealed = q011lq_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 307
    assert sealed["direct_digest_count"] == 1_394
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011lp"]["digests"]) == q011lq.Q011LP_DIGESTS
    assert sealed["q011lp"]["artifact_sha256"] == q011lq.Q011LP_ARTIFACT_SHA256
    assert sealed["q011lp"]["runner_sha256"] == q011lq.Q011LP_RUNNER_SHA256
    assert sealed["q011lp"]["resolved_witness_digest_sha256"] == (
        q011lq.EXPECTED_ORDINAL_ONE_HUNDRED_TWENTY_THREE_RESOLUTION_DIGEST
    )


def test_q011lq_selects_exactly_flatten_ordinal_one_hundred_twenty_four(
    q011lq_structure: dict[str, Any],
) -> None:
    fixed = q011lq_structure["fixed"]
    selection = fixed["one_hundred_twenty_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 124
    assert selection["selected_left_index"] == 15
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(124))
    assert selection["ordinal_one_hundred_twenty_three_resolution_digest_sha256"] == (
        q011lq.EXPECTED_ORDINAL_ONE_HUNDRED_TWENTY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_twenty_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [5, 4], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 5_174
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011lq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011lq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011lq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011lq_reconstructs_registered_partition_and_inventory(
    q011lq_structure: dict[str, Any],
) -> None:
    fixed = q011lq_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [5, 4], [5], [4, 3]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 5, 4, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011lq.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011lq.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 93_600
    assert fixed["full_allocation_digest_sha256"] == q011lq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 5_174
    assert q011lq_structure["compatible_count"] == 5_174
    assert fixed["compatible_allocation_digest_sha256"] == q011lq.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 5, 0, 4, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 5, 0, 4, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 93_480
    assert fixed["parent_witness_compatible_index"] == 5_173
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lq result is not sealed")
def test_q011lq_classifies_every_registered_exact_interval(
    q011lq_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011lq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 5_174
    records = partition["allocation_classification_records"]
    assert len(records) == 5_174
    assert [record["compatible_allocation_index"] for record in records] == list(range(5_174))
    assert sum(partition["exact_relation_counts"].values()) == 5_174
    assert sum(partition["binary64_outward_relation_counts"].values()) == 5_174
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lq result is not sealed")
def test_q011lq_applies_registered_stopping_rule(
    q011lq_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011lq_cycle["study_validity"] == "passed"
    assert q011lq_cycle["failed_validity_order"] == []
    assert q011lq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011lq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011lq_cycle["diagnostic_gates"].values())
    assert q011lq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011lq_cycle["actual_resonance_outcome"] == "not_established"
    assert q011lq_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011lq.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011lq.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011lq.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011lq_cycle["diagnostic_classification"] == expected
    assert not q011lq_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011lq_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_twenty_fifth_q011cb_witness"
        ],
        theorem["one_hundred_twenty_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_twenty_fifth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lq result is not sealed")
def test_q011lq_preserves_boundary_and_reproducible_digests(
    q011lq_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011lq_cycle["theorem_consequence"]
    assert theorem["q011lp_ordinal_one_hundred_twenty_three_phase_resolution_is_preserved"]
    assert theorem["q011lm_ordinal_one_hundred_twenty_two_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 124" in q011lq_cycle["claim_boundary"]
    assert "ordinals 0 through 123" in q011lq_cycle["claim_boundary"]
    assert "later 44675 Q011cb refined signatures" in q011lq_cycle["claim_boundary"]
    assert "Q011lr" in q011lq_cycle["next_change"]
    assert {name: q011lq_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011lq_cycle["result_digest_sha256"] == (
        q011lq.q011b._canonical_json_sha256(q011lq._result_digest_sections(q011lq_cycle))
    )
    assert q011lq._protocol_globals_are_restored()
    json.dumps(q011lq_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lq result is not sealed")
def test_q011lq_study_metadata_and_optional_artifact_are_scoped(
    q011lq_study: dict[str, Any],
) -> None:
    assert q011lq_study["schema_version"] == 1
    assert q011lq_study["source"] == source_metadata()
    assert q011lq_study["study_gate"] == "passed"
    assert q011lq_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011lq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 5_174
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011lq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 124
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011lq_study, allow_nan=False)

    runner_path = Path(q011lq.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011lq_degree34_one_hundred_twenty_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011lq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011lq_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011lq.q011b._canonical_json_sha256(q011lq._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
