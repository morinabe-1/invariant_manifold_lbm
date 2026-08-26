from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jq_degree34_ninety_ninth_individual_partition_audit as q011jq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "860a2be641c33f500d7c5deda8ca09c327e2f2abf70ce0f62c90bd43934e55b5"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "f7ff521516ade5ffa424a997a2d48572a0a1893986f1f67807ae9124be51a856"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "c4bfa1ffddecdc770bee310962937748eef55baf617b189b7c7d3956f39cd8b5",
    "partition_input_digest_sha256": (
        "19cc527ee32d21c2700545e3f0f40d83742fc47944c7dc5e778e34599f400a93"
    ),
    "allocation_audit_digest_sha256": (
        "4054565aaa779ccdf629401d3bd20b0db89837b572f7e8c5b6379e6a297ce91f"
    ),
    "result_digest_sha256": "fb2211ff22496299e96129a0c71e5e52ef196dd816a280fcd229229b261a9e58",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "4c5d2bbd3e5e78877e4dd4e59728c76a787cf6a3a4419347a77cd61b7a99dc7a"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c54dfe2579a411f2e2d3651e8d283718b475fbcb0e03367885fed4b06473cd08"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "7187e9d3b305621ef130fe15f32f2f58090f93af310bbe668f15065cb62f67dc"
    ),
    "allocation_classification_record_digest_sha256": (
        "eda7eeb947d04cb8034459eb06b5c61fd1a74fdc6caf7a5548aa09d9dab78f28"
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
def q011jq_structure() -> dict[str, Any]:
    sealed, artifacts = q011jq._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011jq._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011jq_study() -> dict[str, Any]:
    return q011jq.run_q011jq_study()


@pytest.fixture(scope="module")
def q011jq_cycle(q011jq_study: dict[str, Any]) -> dict[str, Any]:
    return q011jq_study["cycle"]


def test_q011jq_seals_q011jp_and_all_prior_inputs(
    q011jq_structure: dict[str, Any],
) -> None:
    sealed = q011jq_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 255
    assert sealed["direct_digest_count"] == 1_160
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jp"]["digests"]) == q011jq.Q011JP_DIGESTS
    assert sealed["q011jp"]["artifact_sha256"] == q011jq.Q011JP_ARTIFACT_SHA256
    assert sealed["q011jp"]["runner_sha256"] == q011jq.Q011JP_RUNNER_SHA256
    assert sealed["q011jp"]["resolved_witness_digest_sha256"] == (
        q011jq.EXPECTED_ORDINAL_NINETY_SEVEN_RESOLUTION_DIGEST
    )


def test_q011jq_selects_exactly_flatten_ordinal_ninety_eight(
    q011jq_structure: dict[str, Any],
) -> None:
    fixed = q011jq_structure["fixed"]
    selection = fixed["ninety_ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 98
    assert selection["selected_left_index"] == 12
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(98))
    assert selection["ordinal_ninety_seven_resolution_digest_sha256"] == (
        q011jq.EXPECTED_ORDINAL_NINETY_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["ninety_ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 3_727
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011jq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011jq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011jq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011jq_reconstructs_registered_partition_and_inventory(
    q011jq_structure: dict[str, Any],
) -> None:
    fixed = q011jq_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [2, 5]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 2, 7, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011jq.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011jq.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 67_392
    assert fixed["full_allocation_digest_sha256"] == q011jq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_727
    assert q011jq_structure["compatible_count"] == 3_727
    assert fixed["compatible_allocation_digest_sha256"] == q011jq.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [
        0,
        1,
        0,
        12,
        0,
        2,
        0,
        7,
        0,
        5,
        0,
        2,
        5,
        0,
    ]
    assert fixed["last_compatible_counts"] == [
        1,
        0,
        12,
        0,
        2,
        0,
        7,
        0,
        0,
        5,
        0,
        2,
        0,
        5,
    ]
    assert fixed["parent_witness_allocation_index"] == 67_284
    assert fixed["parent_witness_compatible_index"] == 3_726
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jq result is not sealed")
def test_q011jq_classifies_every_registered_exact_interval(
    q011jq_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011jq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 3_727
    records = partition["allocation_classification_records"]
    assert len(records) == 3_727
    assert [record["compatible_allocation_index"] for record in records] == list(range(3_727))
    assert sum(partition["exact_relation_counts"].values()) == 3_727
    assert sum(partition["binary64_outward_relation_counts"].values()) == 3_727
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jq result is not sealed")
def test_q011jq_applies_registered_stopping_rule(
    q011jq_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011jq_cycle["study_validity"] == "passed"
    assert q011jq_cycle["failed_validity_order"] == []
    assert q011jq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jq_cycle["diagnostic_gates"].values())
    assert q011jq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jq_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jq_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011jq.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011jq.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011jq.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jq_cycle["diagnostic_classification"] == expected
    assert not q011jq_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011jq_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_ninth_q011cb_witness"],
        theorem["ninety_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninety_ninth_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jq result is not sealed")
def test_q011jq_preserves_boundary_and_reproducible_digests(
    q011jq_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011jq_cycle["theorem_consequence"]
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
    assert "flatten ordinal 98" in q011jq_cycle["claim_boundary"]
    assert "ordinals 0 through 97" in q011jq_cycle["claim_boundary"]
    assert "later 44701 Q011cb refined signatures" in q011jq_cycle["claim_boundary"]
    assert "Q011jr" in q011jq_cycle["next_change"]
    assert {name: q011jq_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jq_cycle["result_digest_sha256"] == (
        q011jq.q011b._canonical_json_sha256(q011jq._result_digest_sections(q011jq_cycle))
    )
    assert q011jq._protocol_globals_are_restored()
    json.dumps(q011jq_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jq result is not sealed")
def test_q011jq_study_metadata_and_optional_artifact_are_scoped(
    q011jq_study: dict[str, Any],
) -> None:
    assert q011jq_study["schema_version"] == 1
    assert q011jq_study["source"] == source_metadata()
    assert q011jq_study["study_gate"] == "passed"
    assert q011jq_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_727
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 98
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jq_study, allow_nan=False)

    runner_path = Path(q011jq.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jq_degree34_ninety_ninth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jq_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jq.q011b._canonical_json_sha256(q011jq._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
