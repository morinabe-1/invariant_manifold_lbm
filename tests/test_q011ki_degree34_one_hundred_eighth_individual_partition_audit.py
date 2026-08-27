from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ki_degree34_one_hundred_eighth_individual_partition_audit as q011ki
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "a8b68dac1ab18f97e7825836b9ef1624c9304db0ea1aea719fd8880c0dbed1d1"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "afe3c1b37db330e290cd2f03bf2aea0c93750233c0a229d86ce051ef83a7a022"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "2f4cf37555f35934355c26e587339904af6e57dfcdf9d5a5ea8fc302f3f40a7b",
    "partition_input_digest_sha256": (
        "9a3e375112eba749fc4b9dfd5ddae7f71e587dc9ba37f3fd4a85d835b746eb0f"
    ),
    "allocation_audit_digest_sha256": (
        "296cbb3835ff57fe1b3f249745f22960f06b2deceb876a9ee6a56288c054c445"
    ),
    "result_digest_sha256": "7dfb48aa0a3c6cd54e33bef9bf793a8802b6e2e4f1ef606c78c74efb05f32da9",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "5c6c6f53062b8b5250e5fab9bed2bf4c5a15e1b04ffd373a82a7e8a83487c5c0"
    ),
    "parent_center_product_interval_digest_sha256": (
        "d8c442a9089d6905c747c0ca743b6b04168873cb26c20bf74c7401956ab352f9"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "188ded38fb93ec3f2a84fa2d84d489ee5f95a68f59226f193d714402f6c2537a"
    ),
    "allocation_classification_record_digest_sha256": (
        "daa72146e13e760f087944086ec681a11239ba1608dcc058590b07b7a10d6f5e"
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
def q011ki_structure() -> dict[str, Any]:
    sealed, artifacts = q011ki._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ki._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ki_study() -> dict[str, Any]:
    return q011ki.run_q011ki_study()


@pytest.fixture(scope="module")
def q011ki_cycle(q011ki_study: dict[str, Any]) -> dict[str, Any]:
    return q011ki_study["cycle"]


def test_q011ki_seals_q011kh_and_all_prior_inputs(
    q011ki_structure: dict[str, Any],
) -> None:
    sealed = q011ki_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 273
    assert sealed["direct_digest_count"] == 1_241
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011kh"]["digests"]) == q011ki.Q011KH_DIGESTS
    assert sealed["q011kh"]["artifact_sha256"] == q011ki.Q011KH_ARTIFACT_SHA256
    assert sealed["q011kh"]["runner_sha256"] == q011ki.Q011KH_RUNNER_SHA256
    assert sealed["q011kh"]["resolved_witness_digest_sha256"] == (
        q011ki.EXPECTED_ORDINAL_ONE_HUNDRED_SIX_RESOLUTION_DIGEST
    )


def test_q011ki_selects_exactly_flatten_ordinal_one_hundred_seven(
    q011ki_structure: dict[str, Any],
) -> None:
    fixed = q011ki_structure["fixed"]
    selection = fixed["one_hundred_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 107
    assert selection["selected_left_index"] == 13
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(107))
    assert selection["ordinal_one_hundred_six_resolution_digest_sha256"] == (
        q011ki.EXPECTED_ORDINAL_ONE_HUNDRED_SIX_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [3, 6], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 4_827
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ki.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ki.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ki.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ki_reconstructs_registered_partition_and_inventory(
    q011ki_structure: dict[str, Any],
) -> None:
    fixed = q011ki_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [3, 6], [5], [3, 4]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 3, 6, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011ki.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011ki.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 87_360
    assert fixed["full_allocation_digest_sha256"] == q011ki.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 4_827
    assert q011ki_structure["compatible_count"] == 4_827
    assert fixed["compatible_allocation_digest_sha256"] == q011ki.EXPECTED_COMPATIBLE_DIGEST
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
        1,
        2,
        4,
        0,
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
        3,
        0,
        4,
    ]
    assert fixed["parent_witness_allocation_index"] == 87_240
    assert fixed["parent_witness_compatible_index"] == 4_826
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ki result is not sealed")
def test_q011ki_classifies_every_registered_exact_interval(
    q011ki_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011ki_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 4_827
    records = partition["allocation_classification_records"]
    assert len(records) == 4_827
    assert [record["compatible_allocation_index"] for record in records] == list(range(4_827))
    assert sum(partition["exact_relation_counts"].values()) == 4_827
    assert sum(partition["binary64_outward_relation_counts"].values()) == 4_827
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ki result is not sealed")
def test_q011ki_applies_registered_stopping_rule(
    q011ki_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011ki_cycle["study_validity"] == "passed"
    assert q011ki_cycle["failed_validity_order"] == []
    assert q011ki_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ki_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ki_cycle["diagnostic_gates"].values())
    assert q011ki_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ki_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ki_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ki.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ki.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ki.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ki_cycle["diagnostic_classification"] == expected
    assert not q011ki_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ki_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_one_hundred_eighth_q011cb_witness"],
        theorem["one_hundred_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_eighth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ki result is not sealed")
def test_q011ki_preserves_boundary_and_reproducible_digests(
    q011ki_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011ki_cycle["theorem_consequence"]
    assert theorem["q011kh_ordinal_one_hundred_six_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 107" in q011ki_cycle["claim_boundary"]
    assert "ordinals 0 through 106" in q011ki_cycle["claim_boundary"]
    assert "later 44692 Q011cb refined signatures" in q011ki_cycle["claim_boundary"]
    assert "Q011kj" in q011ki_cycle["next_change"]
    assert {name: q011ki_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ki_cycle["result_digest_sha256"] == (
        q011ki.q011b._canonical_json_sha256(q011ki._result_digest_sections(q011ki_cycle))
    )
    assert q011ki._protocol_globals_are_restored()
    json.dumps(q011ki_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ki result is not sealed")
def test_q011ki_study_metadata_and_optional_artifact_are_scoped(
    q011ki_study: dict[str, Any],
) -> None:
    assert q011ki_study["schema_version"] == 1
    assert q011ki_study["source"] == source_metadata()
    assert q011ki_study["study_gate"] == "passed"
    assert q011ki_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ki_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 4_827
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ki_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 107
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ki_study, allow_nan=False)

    runner_path = Path(q011ki.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ki_degree34_one_hundred_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ki artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ki_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ki.q011b._canonical_json_sha256(q011ki._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
