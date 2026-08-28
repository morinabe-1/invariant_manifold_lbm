from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011lg_degree34_one_hundred_twentieth_individual_partition_audit as q011lg
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "019b39ec303444f668708b5c8d814ee335a232a13894d2f4fe3087a5230ffa6b"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "ef4a7efa7a2c876aa590e73b31c588875a21847d8f6eab6a08f858c4b4fbc09e"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "cbc5ec97f98e803814a6615d454889406baf8aab3699359f59acc1aec8e39284",
    "partition_input_digest_sha256": (
        "fa7fa779e1390101149d19c77e7c1a667dd4261c50384ceee95869046deb5b41"
    ),
    "allocation_audit_digest_sha256": (
        "8670399bea4e0d686750c9a1d4c3a3ab57595eed6b1e2f46867ab12afb8e9280"
    ),
    "result_digest_sha256": "f1463b2bf4ca9d66e514a880e096cdda95cdd9daa7a5be6def86f7b0ab5984b0",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "dd2e520bf05a14d05dc9f3ecea5d55d2c99e4420390950777f284c720b517a4d"
    ),
    "parent_center_product_interval_digest_sha256": (
        "757bbc77e85b4f34e7334b1441fa4968eec6fe7a069b2348d77743e848219221"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "839733fbd8ec12e99d24fae801b59ef34dca2906c25dd04a21f2cc2ed1e7dbfa"
    ),
    "allocation_classification_record_digest_sha256": (
        "67e7d01f78410ebf91cbcf0e76d9d5e5d7c8620500334998e9b6ddfa3c9fc99f"
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
def q011lg_structure() -> dict[str, Any]:
    sealed, artifacts = q011lg._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011lg._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011lg_study() -> dict[str, Any]:
    return q011lg.run_q011lg_study()


@pytest.fixture(scope="module")
def q011lg_cycle(q011lg_study: dict[str, Any]) -> dict[str, Any]:
    return q011lg_study["cycle"]


def test_q011lg_seals_q011lf_and_all_prior_inputs(
    q011lg_structure: dict[str, Any],
) -> None:
    sealed = q011lg_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 297
    assert sealed["direct_digest_count"] == 1_349
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011lf"]["digests"]) == q011lg.Q011LF_DIGESTS
    assert sealed["q011lf"]["artifact_sha256"] == q011lg.Q011LF_ARTIFACT_SHA256
    assert sealed["q011lf"]["runner_sha256"] == q011lg.Q011LF_RUNNER_SHA256
    assert sealed["q011lf"]["resolved_witness_digest_sha256"] == (
        q011lg.EXPECTED_ORDINAL_ONE_HUNDRED_EIGHTEEN_RESOLUTION_DIGEST
    )


def test_q011lg_selects_exactly_flatten_ordinal_one_hundred_nineteen(
    q011lg_structure: dict[str, Any],
) -> None:
    fixed = q011lg_structure["fixed"]
    selection = fixed["one_hundred_twentieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 119
    assert selection["selected_left_index"] == 14
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(119))
    assert selection["ordinal_one_hundred_eighteen_resolution_digest_sha256"] == (
        q011lg.EXPECTED_ORDINAL_ONE_HUNDRED_EIGHTEEN_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_twentieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [4, 5], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 2_076
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011lg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011lg.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011lg.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011lg_reconstructs_registered_partition_and_inventory(
    q011lg_structure: dict[str, Any],
) -> None:
    fixed = q011lg_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [4, 5], [5], [7, 0]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 4, 5, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011lg.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011lg.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 37_440
    assert fixed["full_allocation_digest_sha256"] == q011lg.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_076
    assert q011lg_structure["compatible_count"] == 2_076
    assert fixed["compatible_allocation_digest_sha256"] == q011lg.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 4, 0, 5, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 4, 0, 5, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 37_392
    assert fixed["parent_witness_compatible_index"] == 2_075
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lg result is not sealed")
def test_q011lg_classifies_every_registered_exact_interval(
    q011lg_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011lg_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_076
    records = partition["allocation_classification_records"]
    assert len(records) == 2_076
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_076))
    assert sum(partition["exact_relation_counts"].values()) == 2_076
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_076
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lg result is not sealed")
def test_q011lg_applies_registered_stopping_rule(
    q011lg_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011lg_cycle["study_validity"] == "passed"
    assert q011lg_cycle["failed_validity_order"] == []
    assert q011lg_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011lg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011lg_cycle["diagnostic_gates"].values())
    assert q011lg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011lg_cycle["actual_resonance_outcome"] == "not_established"
    assert q011lg_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011lg.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011lg.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011lg.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011lg_cycle["diagnostic_classification"] == expected
    assert not q011lg_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011lg_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_one_hundred_twentieth_q011cb_witness"],
        theorem["one_hundred_twentieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_twentieth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lg result is not sealed")
def test_q011lg_preserves_boundary_and_reproducible_digests(
    q011lg_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011lg_cycle["theorem_consequence"]
    assert theorem["q011lf_ordinal_one_hundred_eighteen_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 119" in q011lg_cycle["claim_boundary"]
    assert "ordinals 0 through 118" in q011lg_cycle["claim_boundary"]
    assert "later 44680 Q011cb refined signatures" in q011lg_cycle["claim_boundary"]
    assert "Q011lh" in q011lg_cycle["next_change"]
    assert {name: q011lg_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011lg_cycle["result_digest_sha256"] == (
        q011lg.q011b._canonical_json_sha256(q011lg._result_digest_sections(q011lg_cycle))
    )
    assert q011lg._protocol_globals_are_restored()
    json.dumps(q011lg_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011lg result is not sealed")
def test_q011lg_study_metadata_and_optional_artifact_are_scoped(
    q011lg_study: dict[str, Any],
) -> None:
    assert q011lg_study["schema_version"] == 1
    assert q011lg_study["source"] == source_metadata()
    assert q011lg_study["study_gate"] == "passed"
    assert q011lg_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011lg_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_076
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011lg_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 119
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011lg_study, allow_nan=False)

    runner_path = Path(q011lg.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011lg_degree34_one_hundred_twentieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011lg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011lg_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011lg.q011b._canonical_json_sha256(q011lg._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
