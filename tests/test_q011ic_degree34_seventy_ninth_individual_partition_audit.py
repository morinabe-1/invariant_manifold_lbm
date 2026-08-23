from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ic_degree34_seventy_ninth_individual_partition_audit as q011ic
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "94f4bcc0ac761481aba738c663a68a064da81ea24abd07becf66ea4d33d0ceec"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "160e07f6dc878c4308031fa99304e7a36342a6f212854f6108fc791e2cbdb318"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "8c282b0dda2f38ca717e947d276a52654984476a6b1329baf3f1aa78b5fa2a66",
    "partition_input_digest_sha256": (
        "dc4dceac718db4d86ad4d79823022aee0af30d500a95419c9a13614d9157bd70"
    ),
    "allocation_audit_digest_sha256": (
        "94c6413ab22f5cc77e42d6ea0682ee7ccca75f39065f8501f06eaba50c8739f6"
    ),
    "result_digest_sha256": "39e8221c78ef452a6384e9f193913e95f319ad762e237e7caa43fbd14bb0db3b",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "b01222e1866533adf415b86266472d8ee716dfa77502079406fa7b5507998d54"
    ),
    "parent_center_product_interval_digest_sha256": (
        "7274fd0a8334714b8cec746c26472d377147e743dbff6d16a63248ecccea6a56"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "da72f0c3297092d29262ac724ae579225f8e6590ddc022a0e8f1e56638da0583"
    ),
    "allocation_classification_record_digest_sha256": (
        "00d80a8734e71164b1acb5c7396aeb1dae07946280ed0df7707fe015787236a9"
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
def q011ic_structure() -> dict[str, Any]:
    sealed, artifacts = q011ic._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ic._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ic_study() -> dict[str, Any]:
    return q011ic.run_q011ic_study()


@pytest.fixture(scope="module")
def q011ic_cycle(q011ic_study: dict[str, Any]) -> dict[str, Any]:
    return q011ic_study["cycle"]


def test_q011ic_seals_q011ib_and_all_prior_inputs(q011ic_structure: dict[str, Any]) -> None:
    sealed = q011ic_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 215
    assert sealed["direct_digest_count"] == 980
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ib"]["digests"]) == q011ic.Q011IB_DIGESTS
    assert sealed["q011ib"]["artifact_sha256"] == q011ic.Q011IB_ARTIFACT_SHA256
    assert sealed["q011ib"]["runner_sha256"] == q011ic.Q011IB_RUNNER_SHA256
    assert sealed["q011ib"]["resolved_witness_digest_sha256"] == (
        q011ic.EXPECTED_ORDINAL_SEVENTY_SEVEN_RESOLUTION_DIGEST
    )


def test_q011ic_selects_exactly_flatten_ordinal_seventy_eight(
    q011ic_structure: dict[str, Any],
) -> None:
    fixed = q011ic_structure["fixed"]
    selection = fixed["seventy_ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 78
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(78))
    assert selection["ordinal_seventy_seven_resolution_digest_sha256"] == (
        q011ic.EXPECTED_ORDINAL_SEVENTY_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["seventy_ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 665
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ic.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ic.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ic.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ic_reconstructs_registered_partition_and_inventory(
    q011ic_structure: dict[str, Any],
) -> None:
    fixed = q011ic_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [6, 1]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011ic.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011ic.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 11_760
    assert fixed["full_allocation_digest_sha256"] == q011ic.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 665
    assert q011ic_structure["compatible_count"] == 665
    assert fixed["compatible_allocation_digest_sha256"] == q011ic.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 11_676
    assert fixed["parent_witness_compatible_index"] == 664
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ic result is not sealed")
def test_q011ic_classifies_every_registered_exact_interval(q011ic_cycle: dict[str, Any]) -> None:
    partition = q011ic_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 665
    records = partition["allocation_classification_records"]
    assert len(records) == 665
    assert [record["compatible_allocation_index"] for record in records] == list(range(665))
    assert sum(partition["exact_relation_counts"].values()) == 665
    assert sum(partition["binary64_outward_relation_counts"].values()) == 665
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ic result is not sealed")
def test_q011ic_applies_the_registered_exclusive_stopping_rule(
    q011ic_cycle: dict[str, Any],
) -> None:
    assert q011ic_cycle["study_validity"] == "passed"
    assert q011ic_cycle["failed_validity_order"] == []
    assert q011ic_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ic_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ic_cycle["diagnostic_gates"].values())
    assert q011ic_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ic_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ic_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ic.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ic.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ic.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ic_cycle["diagnostic_classification"] == expected
    assert not q011ic_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ic_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_ninth_q011cb_witness"],
        theorem["seventy_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_ninth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ic result is not sealed")
def test_q011ic_preserves_boundary_and_reproducible_digests(
    q011ic_cycle: dict[str, Any],
) -> None:
    theorem = q011ic_cycle["theorem_consequence"]
    assert theorem["q011ib_ordinal_seventy_seven_phase_resolution_is_preserved"]
    assert theorem["q011ia_ordinal_seventy_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hz_ordinal_seventy_six_phase_resolution_is_preserved"]
    assert theorem["q011hy_ordinal_seventy_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hx_ordinal_seventy_five_phase_resolution_is_preserved"]
    assert theorem["q011hw_ordinal_seventy_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hv_ordinal_seventy_four_phase_resolution_is_preserved"]
    assert theorem["q011hu_ordinal_seventy_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hr_ordinal_seventy_two_phase_resolution_is_preserved"]
    assert theorem["q011hq_ordinal_seventy_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hp_ordinal_seventy_one_phase_resolution_is_preserved"]
    assert theorem["q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hn_ordinal_seventy_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 78" in q011ic_cycle["claim_boundary"]
    assert "ordinals 0 through 77" in q011ic_cycle["claim_boundary"]
    assert "later 44721 Q011cb refined signatures" in q011ic_cycle["claim_boundary"]
    assert "Q011id" in q011ic_cycle["next_change"]
    json.dumps(q011ic_cycle, allow_nan=False)
    assert {name: q011ic_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ic_cycle["result_digest_sha256"] == (
        q011ic.q011b._canonical_json_sha256(q011ic._result_digest_sections(q011ic_cycle))
    )
    assert q011ic._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ic result is not sealed")
def test_q011ic_study_metadata_and_optional_artifact_are_scoped(
    q011ic_study: dict[str, Any],
) -> None:
    assert q011ic_study["schema_version"] == 1
    assert q011ic_study["source"] == source_metadata()
    assert q011ic_study["study_gate"] == "passed"
    assert q011ic_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ic_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 665
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ic_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 78
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ic_study, allow_nan=False)

    runner_path = Path(q011ic.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ic_degree34_seventy_ninth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ic artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ic_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ic.q011b._canonical_json_sha256(q011ic._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
