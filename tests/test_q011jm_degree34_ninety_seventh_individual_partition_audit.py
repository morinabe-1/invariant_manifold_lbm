from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jm_degree34_ninety_seventh_individual_partition_audit as q011jm
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "0f92eb7127b734fc929554c67fdf82fa0349b3db0204a6cd5ed3552e7c3df228"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "f28bb4afc96c330b7588b9aaf8c76b3cc8b9f2e1518b10d2dfe6faa4614ad13d"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "13896f08b1fa89e3dc1794c9e4b09f507ec020b69c7d65de520d789a50de9418",
    "partition_input_digest_sha256": "de769c1c338a2d50b406aba10fee210a615dc6dc26f40f3624ec7387c17f97d0",
    "allocation_audit_digest_sha256": "97b85afa15b054e67e03e4cb2e2bb26899084f21884287676c581d0e870f5b08",
    "result_digest_sha256": "f969aea37ef74ca2bbbef6d96c8d85afbceb46ea3fcabffaff090a2c2674e869",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "81ab70b20a9ab8cc71883890243f654d11044746547930a4787a2536555ea54c",
    "parent_center_product_interval_digest_sha256": "c0262bd3b88a05fabb93995f61af7afa8cbed39c946dad8094245cb5304463d5",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "1317a5ed4ee76447130dfb4a4d688cfd60a166703faaea9606d78a49dc66291a",
    "allocation_classification_record_digest_sha256": "45007a1939813601a87f7e9791faa2fb10277911a4f50ed14b0303bd9bbe8476",
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
def q011jm_structure() -> dict[str, Any]:
    sealed, artifacts = q011jm._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011jm._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011jm_study() -> dict[str, Any]:
    return q011jm.run_q011jm_study()


@pytest.fixture(scope="module")
def q011jm_cycle(q011jm_study: dict[str, Any]) -> dict[str, Any]:
    return q011jm_study["cycle"]


def test_q011jm_seals_q011jl_and_all_prior_inputs(
    q011jm_structure: dict[str, Any],
) -> None:
    sealed = q011jm_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 251
    assert sealed["direct_digest_count"] == 1_142
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jl"]["digests"]) == q011jm.Q011JL_DIGESTS
    assert sealed["q011jl"]["artifact_sha256"] == q011jm.Q011JL_ARTIFACT_SHA256
    assert sealed["q011jl"]["runner_sha256"] == q011jm.Q011JL_RUNNER_SHA256
    assert sealed["q011jl"]["resolved_witness_digest_sha256"] == (
        q011jm.EXPECTED_ORDINAL_NINETY_FIVE_RESOLUTION_DIGEST
    )


def test_q011jm_selects_exactly_flatten_ordinal_ninety_six(
    q011jm_structure: dict[str, Any],
) -> None:
    fixed = q011jm_structure["fixed"]
    selection = fixed["ninety_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 96
    assert selection["selected_left_index"] == 12
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(96))
    assert selection["ordinal_ninety_five_resolution_digest_sha256"] == (
        q011jm.EXPECTED_ORDINAL_NINETY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["ninety_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_667
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011jm.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011jm.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011jm.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011jm_reconstructs_registered_partition_and_inventory(
    q011jm_structure: dict[str, Any],
) -> None:
    fixed = q011jm_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [0, 7]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 2, 7, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011jm.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011jm.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 29_952
    assert fixed["full_allocation_digest_sha256"] == q011jm.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_667
    assert q011jm_structure["compatible_count"] == 1_667
    assert fixed["compatible_allocation_digest_sha256"] == q011jm.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 2, 0, 7, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 2, 0, 7, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 29_904
    assert fixed["parent_witness_compatible_index"] == 1_666
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jm result is not sealed")
def test_q011jm_classifies_every_registered_exact_interval(
    q011jm_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011jm_cycle["individual_allocation_interval_audit"]
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jm result is not sealed")
def test_q011jm_applies_registered_stopping_rule(
    q011jm_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011jm_cycle["study_validity"] == "passed"
    assert q011jm_cycle["failed_validity_order"] == []
    assert q011jm_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jm_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jm_cycle["diagnostic_gates"].values())
    assert q011jm_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jm_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jm_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011jm.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011jm.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011jm.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jm_cycle["diagnostic_classification"] == expected
    assert not q011jm_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011jm_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_seventh_q011cb_witness"],
        theorem["ninety_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_ninety_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jm result is not sealed")
def test_q011jm_preserves_boundary_and_reproducible_digests(
    q011jm_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011jm_cycle["theorem_consequence"]
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
    assert "flatten ordinal 96" in q011jm_cycle["claim_boundary"]
    assert "ordinals 0 through 95" in q011jm_cycle["claim_boundary"]
    assert "later 44703 Q011cb refined signatures" in q011jm_cycle["claim_boundary"]
    assert "Q011jn" in q011jm_cycle["next_change"]
    assert {name: q011jm_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jm_cycle["result_digest_sha256"] == (
        q011jm.q011b._canonical_json_sha256(q011jm._result_digest_sections(q011jm_cycle))
    )
    assert q011jm._protocol_globals_are_restored()
    json.dumps(q011jm_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jm result is not sealed")
def test_q011jm_study_metadata_and_optional_artifact_are_scoped(
    q011jm_study: dict[str, Any],
) -> None:
    assert q011jm_study["schema_version"] == 1
    assert q011jm_study["source"] == source_metadata()
    assert q011jm_study["study_gate"] == "passed"
    assert q011jm_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jm_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_667
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jm_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 96
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jm_study, allow_nan=False)

    runner_path = Path(q011jm.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jm_degree34_ninety_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jm artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jm_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jm.q011b._canonical_json_sha256(q011jm._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
