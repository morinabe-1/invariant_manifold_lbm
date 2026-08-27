from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ka_degree34_one_hundred_fourth_individual_partition_audit as q011ka
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "057b32091b8f07c4b450f4bc38dc9c47cf4547eedb9f5e44676292576a24e817"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "811b47be1d7a872a0bf1d95ccc834743ed06cf7acd5787230da203b91775eee0"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "6bc7a84a664cafca922533026b2dbe8de25f909813cd130373b1367731ed10b9",
    "partition_input_digest_sha256": (
        "a93a73247db5f6ecc5ae8cf24c5f6afebaf45a06bc8be1b199fd70bc5f81c719"
    ),
    "allocation_audit_digest_sha256": (
        "919a692abfba20afacc1c0099c5cb94ed6bea3d595b58891918e9e9f27eab4da"
    ),
    "result_digest_sha256": "cef3e0a65758a8f54c2cc2b760fdaede8e9d775d2ef18bab36e8cb7bb9868efb",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "493d8b8af22a616b4c0e2744a6082480d347d55b549622acf1cc63e838135c1c"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c2699fe675d05f868af96bd60279be56f7e11d8c9d72309015fe1c86d9249785"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "a5f72151878790813dac74c8c31164bce6bc560d9f4c537bbbe0c92f84d46f99"
    ),
    "allocation_classification_record_digest_sha256": (
        "6f40bfdd9bc128c59f4e4044789a9e34347a8569095bd5aac926e3be74d6ec4a"
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
def q011ka_structure() -> dict[str, Any]:
    sealed, artifacts = q011ka._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ka._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ka_study() -> dict[str, Any]:
    return q011ka.run_q011ka_study()


@pytest.fixture(scope="module")
def q011ka_cycle(q011ka_study: dict[str, Any]) -> dict[str, Any]:
    return q011ka_study["cycle"]


def test_q011ka_seals_q011jz_and_all_prior_inputs(
    q011ka_structure: dict[str, Any],
) -> None:
    sealed = q011ka_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 265
    assert sealed["direct_digest_count"] == 1_205
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jz"]["digests"]) == q011ka.Q011JZ_DIGESTS
    assert sealed["q011jz"]["artifact_sha256"] == q011ka.Q011JZ_ARTIFACT_SHA256
    assert sealed["q011jz"]["runner_sha256"] == q011ka.Q011JZ_RUNNER_SHA256
    assert sealed["q011jz"]["resolved_witness_digest_sha256"] == (
        q011ka.EXPECTED_ORDINAL_ONE_HUNDRED_TWO_RESOLUTION_DIGEST
    )


def test_q011ka_selects_exactly_flatten_ordinal_one_hundred_three(
    q011ka_structure: dict[str, Any],
) -> None:
    fixed = q011ka_structure["fixed"]
    selection = fixed["one_hundred_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 103
    assert selection["selected_left_index"] == 12
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(103))
    assert selection["ordinal_one_hundred_two_resolution_digest_sha256"] == (
        q011ka.EXPECTED_ORDINAL_ONE_HUNDRED_TWO_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 1_667
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ka.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ka.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ka.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ka_reconstructs_registered_partition_and_inventory(
    q011ka_structure: dict[str, Any],
) -> None:
    fixed = q011ka_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [7, 0]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 2, 7, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011ka.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011ka.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 29_952
    assert fixed["full_allocation_digest_sha256"] == q011ka.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_667
    assert q011ka_structure["compatible_count"] == 1_667
    assert fixed["compatible_allocation_digest_sha256"] == q011ka.EXPECTED_COMPATIBLE_DIGEST
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
        5,
        2,
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
        7,
    ]
    assert fixed["parent_witness_allocation_index"] == 29_904
    assert fixed["parent_witness_compatible_index"] == 1_666
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ka result is not sealed")
def test_q011ka_classifies_every_registered_exact_interval(
    q011ka_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011ka_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_667
    records = partition["allocation_classification_records"]
    assert len(records) == 1_667
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_667))
    assert sum(partition["exact_relation_counts"].values()) == 1_667
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_667
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ka result is not sealed")
def test_q011ka_applies_registered_stopping_rule(
    q011ka_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011ka_cycle["study_validity"] == "passed"
    assert q011ka_cycle["failed_validity_order"] == []
    assert q011ka_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ka_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ka_cycle["diagnostic_gates"].values())
    assert q011ka_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ka_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ka_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ka.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ka.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ka.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ka_cycle["diagnostic_classification"] == expected
    assert not q011ka_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ka_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_one_hundred_fourth_q011cb_witness"],
        theorem["one_hundred_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_fourth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ka result is not sealed")
def test_q011ka_preserves_boundary_and_reproducible_digests(
    q011ka_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011ka_cycle["theorem_consequence"]
    assert theorem["q011jz_ordinal_one_hundred_two_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 103" in q011ka_cycle["claim_boundary"]
    assert "ordinals 0 through 102" in q011ka_cycle["claim_boundary"]
    assert "later 44696 Q011cb refined signatures" in q011ka_cycle["claim_boundary"]
    assert "Q011kb" in q011ka_cycle["next_change"]
    assert {name: q011ka_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ka_cycle["result_digest_sha256"] == (
        q011ka.q011b._canonical_json_sha256(q011ka._result_digest_sections(q011ka_cycle))
    )
    assert q011ka._protocol_globals_are_restored()
    json.dumps(q011ka_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ka result is not sealed")
def test_q011ka_study_metadata_and_optional_artifact_are_scoped(
    q011ka_study: dict[str, Any],
) -> None:
    assert q011ka_study["schema_version"] == 1
    assert q011ka_study["source"] == source_metadata()
    assert q011ka_study["study_gate"] == "passed"
    assert q011ka_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ka_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_667
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ka_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 103
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ka_study, allow_nan=False)

    runner_path = Path(q011ka.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ka_degree34_one_hundred_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ka artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ka_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ka.q011b._canonical_json_sha256(q011ka._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
