from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jw_degree34_one_hundred_second_individual_partition_audit as q011jw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "e5a89621e785c3cc63066c1e1ae8a49a45f2d2f7eec0b3aebcbd9e5eefd569ca"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "f6d0e61522d673879d3be00eee5e4a60164146cf22286ac899296a06604a5304"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "3d855f40f442764bab6152ad6426d7758c66bf1a0184b9e0c4727120768c46aa",
    "partition_input_digest_sha256": (
        "5557219c0d744cdf8292a61d0f0892231baf91cfe7ff79bddc47db8648ec1195"
    ),
    "allocation_audit_digest_sha256": (
        "3c19f2c87c493c3bfbb68e6b46714a7318430d507b27cc428239efad68d6a3c2"
    ),
    "result_digest_sha256": "df7ad62796d67c24337ef699eb33e7a7ce469e8c1514b8eef6ff0fa0053ceeef",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "2b701f2799ed702f52d2efbb6aad1af02c61800f98c06d52bcbcc7c4d671743b"
    ),
    "parent_center_product_interval_digest_sha256": (
        "dfa5e932a8b904d5c110214dca797e93f1afaffd6c6cfb4f6b88524e08c7a444"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "b75ced7655468bc6d74f5ed79a2bed2a228c920d83eb4ac4140d9fba568b3924"
    ),
    "allocation_classification_record_digest_sha256": (
        "91fc26731cd07dd06310b8c7691aa01313b03ea9304f48a97a5ca36b79b6cb0f"
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
def q011jw_structure() -> dict[str, Any]:
    sealed, artifacts = q011jw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011jw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011jw_study() -> dict[str, Any]:
    return q011jw.run_q011jw_study()


@pytest.fixture(scope="module")
def q011jw_cycle(q011jw_study: dict[str, Any]) -> dict[str, Any]:
    return q011jw_study["cycle"]


def test_q011jw_seals_q011jv_and_all_prior_inputs(
    q011jw_structure: dict[str, Any],
) -> None:
    sealed = q011jw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 261
    assert sealed["direct_digest_count"] == 1_187
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jv"]["digests"]) == q011jw.Q011JV_DIGESTS
    assert sealed["q011jv"]["artifact_sha256"] == q011jw.Q011JV_ARTIFACT_SHA256
    assert sealed["q011jv"]["runner_sha256"] == q011jw.Q011JV_RUNNER_SHA256
    assert sealed["q011jv"]["resolved_witness_digest_sha256"] == (
        q011jw.EXPECTED_ORDINAL_ONE_HUNDRED_RESOLUTION_DIGEST
    )


def test_q011jw_selects_exactly_flatten_ordinal_one_hundred_one(
    q011jw_structure: dict[str, Any],
) -> None:
    fixed = q011jw_structure["fixed"]
    selection = fixed["one_hundred_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 101
    assert selection["selected_left_index"] == 12
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(101))
    assert selection["ordinal_one_hundred_resolution_digest_sha256"] == (
        q011jw.EXPECTED_ORDINAL_ONE_HUNDRED_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 3_727
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011jw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011jw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011jw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011jw_reconstructs_registered_partition_and_inventory(
    q011jw_structure: dict[str, Any],
) -> None:
    fixed = q011jw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [5, 2]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 2, 7, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011jw.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011jw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 67_392
    assert fixed["full_allocation_digest_sha256"] == q011jw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_727
    assert q011jw_structure["compatible_count"] == 3_727
    assert fixed["compatible_allocation_digest_sha256"] == q011jw.EXPECTED_COMPATIBLE_DIGEST
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
        3,
        2,
        2,
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
        5,
        0,
        2,
    ]
    assert fixed["parent_witness_allocation_index"] == 67_284
    assert fixed["parent_witness_compatible_index"] == 3_726
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jw result is not sealed")
def test_q011jw_classifies_every_registered_exact_interval(
    q011jw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011jw_cycle["individual_allocation_interval_audit"]
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jw result is not sealed")
def test_q011jw_applies_registered_stopping_rule(
    q011jw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011jw_cycle["study_validity"] == "passed"
    assert q011jw_cycle["failed_validity_order"] == []
    assert q011jw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jw_cycle["diagnostic_gates"].values())
    assert q011jw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jw_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011jw.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011jw.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011jw.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jw_cycle["diagnostic_classification"] == expected
    assert not q011jw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011jw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_one_hundred_second_q011cb_witness"],
        theorem["one_hundred_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_second_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jw result is not sealed")
def test_q011jw_preserves_boundary_and_reproducible_digests(
    q011jw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011jw_cycle["theorem_consequence"]
    assert theorem["q011jv_ordinal_one_hundred_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 101" in q011jw_cycle["claim_boundary"]
    assert "ordinals 0 through 100" in q011jw_cycle["claim_boundary"]
    assert "later 44698 Q011cb refined signatures" in q011jw_cycle["claim_boundary"]
    assert "Q011jx" in q011jw_cycle["next_change"]
    assert {name: q011jw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jw_cycle["result_digest_sha256"] == (
        q011jw.q011b._canonical_json_sha256(q011jw._result_digest_sections(q011jw_cycle))
    )
    assert q011jw._protocol_globals_are_restored()
    json.dumps(q011jw_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jw result is not sealed")
def test_q011jw_study_metadata_and_optional_artifact_are_scoped(
    q011jw_study: dict[str, Any],
) -> None:
    assert q011jw_study["schema_version"] == 1
    assert q011jw_study["source"] == source_metadata()
    assert q011jw_study["study_gate"] == "passed"
    assert q011jw_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_727
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 101
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jw_study, allow_nan=False)

    runner_path = Path(q011jw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jw_degree34_one_hundred_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jw.q011b._canonical_json_sha256(q011jw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
