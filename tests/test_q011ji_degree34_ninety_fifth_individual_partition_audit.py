from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ji_degree34_ninety_fifth_individual_partition_audit as q011ji
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "effbef429b14e3e89f0ec0f7fbfa61c2c034eac58b801b430ea2b6fb9b7f9c2a"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "450df38fb3816300e41d9580fbadfb344bcf11dd71644e8734f675c37f3f1521"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "a1f8585cfd97f65941761b956887d788db077e2fd7e62842821f88bc5ee4f664",
    "partition_input_digest_sha256": "f1ae5c575264fa458b0c43e25fa04b9bb024a38d50e0a180a3b36b3df73a4d45",
    "allocation_audit_digest_sha256": "5bcfce74077960d93616ad2b2c2f78db177fa90d04e8195a53acae220f5f6b3d",
    "result_digest_sha256": "bd411706ba4cdc4f13f005b9f0e8a556fa8dcd2bd201cdcd4975fdeec80f9a9b",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "8d2472a3ee3e18c814cdc3a0f40643b782757311c520234c7fb3daa3849abe8e",
    "parent_center_product_interval_digest_sha256": "78dde37482af2af0bd0ab845a6543c49bb028a0a1033c3f87d1b667c6b813ba5",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "aca10a869a2840aa3c6235ab1f82772f3609af16befa5aabec181f165074d257",
    "allocation_classification_record_digest_sha256": "74a74e31672205f2ee090ae9cc3f47ae914ea85796d97d2b82dbc196fa680a8a",
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
def q011ji_structure() -> dict[str, Any]:
    sealed, artifacts = q011ji._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ji._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ji_study() -> dict[str, Any]:
    return q011ji.run_q011ji_study()


@pytest.fixture(scope="module")
def q011ji_cycle(q011ji_study: dict[str, Any]) -> dict[str, Any]:
    return q011ji_study["cycle"]


def test_q011ji_seals_q011jh_and_all_prior_inputs(
    q011ji_structure: dict[str, Any],
) -> None:
    sealed = q011ji_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 247
    assert sealed["direct_digest_count"] == 1_124
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jh"]["digests"]) == q011ji.Q011JH_DIGESTS
    assert sealed["q011jh"]["artifact_sha256"] == q011ji.Q011JH_ARTIFACT_SHA256
    assert sealed["q011jh"]["runner_sha256"] == q011ji.Q011JH_RUNNER_SHA256
    assert sealed["q011jh"]["resolved_witness_digest_sha256"] == (
        q011ji.EXPECTED_ORDINAL_NINETY_THREE_RESOLUTION_DIGEST
    )


def test_q011ji_selects_exactly_flatten_ordinal_ninety_four(
    q011ji_structure: dict[str, Any],
) -> None:
    fixed = q011ji_structure["fixed"]
    selection = fixed["ninety_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 94
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(94))
    assert selection["ordinal_ninety_three_resolution_digest_sha256"] == (
        q011ji.EXPECTED_ORDINAL_NINETY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["ninety_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 2_185
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ji.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ji.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ji.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ji_reconstructs_registered_partition_and_inventory(
    q011ji_structure: dict[str, Any],
) -> None:
    fixed = q011ji_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [6, 1]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011ji.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011ji.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 39_312
    assert fixed["full_allocation_digest_sha256"] == q011ji.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_185
    assert q011ji_structure["compatible_count"] == 2_185
    assert fixed["compatible_allocation_digest_sha256"] == q011ji.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 39_228
    assert fixed["parent_witness_compatible_index"] == 2_184
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ji result is not sealed")
def test_q011ji_classifies_every_registered_exact_interval(
    q011ji_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011ji_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_185
    records = partition["allocation_classification_records"]
    assert len(records) == 2_185
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_185))
    assert sum(partition["exact_relation_counts"].values()) == 2_185
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_185
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ji result is not sealed")
def test_q011ji_applies_registered_stopping_rule(
    q011ji_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011ji_cycle["study_validity"] == "passed"
    assert q011ji_cycle["failed_validity_order"] == []
    assert q011ji_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ji_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ji_cycle["diagnostic_gates"].values())
    assert q011ji_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ji_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ji_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ji.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ji.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ji.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ji_cycle["diagnostic_classification"] == expected
    assert not q011ji_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ji_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_fifth_q011cb_witness"],
        theorem["ninety_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninety_fifth_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ji result is not sealed")
def test_q011ji_preserves_boundary_and_reproducible_digests(
    q011ji_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011ji_cycle["theorem_consequence"]
    assert theorem["q011jh_ordinal_ninety_three_phase_resolution_is_preserved"]
    assert theorem["q011jg_ordinal_ninety_three_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 94" in q011ji_cycle["claim_boundary"]
    assert "ordinals 0 through 93" in q011ji_cycle["claim_boundary"]
    assert "later 44705 Q011cb refined signatures" in q011ji_cycle["claim_boundary"]
    assert "Q011jj" in q011ji_cycle["next_change"]
    assert {name: q011ji_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ji_cycle["result_digest_sha256"] == (
        q011ji.q011b._canonical_json_sha256(q011ji._result_digest_sections(q011ji_cycle))
    )
    assert q011ji._protocol_globals_are_restored()
    json.dumps(q011ji_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ji result is not sealed")
def test_q011ji_study_metadata_and_optional_artifact_are_scoped(
    q011ji_study: dict[str, Any],
) -> None:
    assert q011ji_study["schema_version"] == 1
    assert q011ji_study["source"] == source_metadata()
    assert q011ji_study["study_gate"] == "passed"
    assert q011ji_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ji_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_185
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ji_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 94
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ji_study, allow_nan=False)

    runner_path = Path(q011ji.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ji_degree34_ninety_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ji artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ji_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ji.q011b._canonical_json_sha256(q011ji._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
