from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ja_degree34_ninety_first_individual_partition_audit as q011ja
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "bfb4a4984e1445f01b10f5e7dfb864b775afe8ba6cc3a1df6bb047eb42e5236a"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "845bc184a5ef4726e40012fe9c2d4a61d715be04f7670a52d85dc6483e918019"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "4738821eb282320c343df3c88f823ad954fa81fa21c96fbc9725c20b949540c6",
    "partition_input_digest_sha256": (
        "b94cdebe7dba33caa276475957bcb5ec1407e82e3e664f503f19f092d7251b16"
    ),
    "allocation_audit_digest_sha256": (
        "a38427e2cd61cff872e1a40f9d4410d4339b091bfb8dd35fd4ea014ee1c05a66"
    ),
    "result_digest_sha256": "26da53ed923abd0cc7b2137abbb3ca00cf07f24fceb34bff8708f0b40639d42e",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "32c64a76fbe3d3e8d8b3fd4b073e413d103a898d224e43e93888b73201d54aaa"
    ),
    "parent_center_product_interval_digest_sha256": (
        "83cd8ec14e7a6d97fe9b54820b974424050b416375a209149e9934e8ceaa6e7d"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "452d9a8688dc34cb8ece9dfd307acdc2c4a4f269a5e49af75c541299808f311f"
    ),
    "allocation_classification_record_digest_sha256": (
        "cdb1ce05d6e4bb3fec53c19bff0b24016b26f9bc6886f6e740a17571f364c2ea"
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
def q011ja_structure() -> dict[str, Any]:
    sealed, artifacts = q011ja._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ja._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ja_study() -> dict[str, Any]:
    return q011ja.run_q011ja_study()


@pytest.fixture(scope="module")
def q011ja_cycle(q011ja_study: dict[str, Any]) -> dict[str, Any]:
    return q011ja_study["cycle"]


def test_q011ja_seals_q011iz_and_all_prior_inputs(
    q011ja_structure: dict[str, Any],
) -> None:
    sealed = q011ja_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 239
    assert sealed["direct_digest_count"] == 1_088
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011iz"]["digests"]) == q011ja.Q011IZ_DIGESTS
    assert sealed["q011iz"]["artifact_sha256"] == q011ja.Q011IZ_ARTIFACT_SHA256
    assert sealed["q011iz"]["runner_sha256"] == q011ja.Q011IZ_RUNNER_SHA256
    assert sealed["q011iz"]["resolved_witness_digest_sha256"] == (
        q011ja.EXPECTED_ORDINAL_EIGHTY_NINE_RESOLUTION_DIGEST
    )


def test_q011ja_selects_exactly_flatten_ordinal_ninety(
    q011ja_structure: dict[str, Any],
) -> None:
    fixed = q011ja_structure["fixed"]
    selection = fixed["ninety_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 90
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(90))
    assert selection["ordinal_eighty_nine_resolution_digest_sha256"] == (
        q011ja.EXPECTED_ORDINAL_EIGHTY_NINE_RESOLUTION_DIGEST
    )
    parent = selection["ninety_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 2_799
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ja.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ja.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ja.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ja_reconstructs_registered_partition_and_inventory(
    q011ja_structure: dict[str, Any],
) -> None:
    fixed = q011ja_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [2, 5]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011ja.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011ja.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_544
    assert fixed["full_allocation_digest_sha256"] == q011ja.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_799
    assert q011ja_structure["compatible_count"] == 2_799
    assert fixed["compatible_allocation_digest_sha256"] == q011ja.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 50_436
    assert fixed["parent_witness_compatible_index"] == 2_798
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ja result is not sealed")
def test_q011ja_classifies_every_registered_exact_interval(
    q011ja_cycle: dict[str, Any],
) -> None:
    partition = q011ja_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_799
    records = partition["allocation_classification_records"]
    assert len(records) == 2_799
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_799))
    assert sum(partition["exact_relation_counts"].values()) == 2_799
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_799
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ja result is not sealed")
def test_q011ja_applies_registered_stopping_rule(
    q011ja_cycle: dict[str, Any],
) -> None:
    assert q011ja_cycle["study_validity"] == "passed"
    assert q011ja_cycle["failed_validity_order"] == []
    assert q011ja_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ja_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ja_cycle["diagnostic_gates"].values())
    assert q011ja_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ja_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ja_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ja.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ja.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ja.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ja_cycle["diagnostic_classification"] == expected
    assert not q011ja_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ja_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_first_q011cb_witness"],
        theorem["ninety_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninety_first_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ja result is not sealed")
def test_q011ja_preserves_boundary_and_reproducible_digests(
    q011ja_cycle: dict[str, Any],
) -> None:
    theorem = q011ja_cycle["theorem_consequence"]
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
    assert "flatten ordinal 90" in q011ja_cycle["claim_boundary"]
    assert "ordinals 0 through 89" in q011ja_cycle["claim_boundary"]
    assert "later 44709 Q011cb refined signatures" in q011ja_cycle["claim_boundary"]
    assert "Q011jb" in q011ja_cycle["next_change"]
    assert {name: q011ja_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ja_cycle["result_digest_sha256"] == (
        q011ja.q011b._canonical_json_sha256(q011ja._result_digest_sections(q011ja_cycle))
    )
    assert q011ja._protocol_globals_are_restored()
    json.dumps(q011ja_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ja result is not sealed")
def test_q011ja_study_metadata_and_optional_artifact_are_scoped(
    q011ja_study: dict[str, Any],
) -> None:
    assert q011ja_study["schema_version"] == 1
    assert q011ja_study["source"] == source_metadata()
    assert q011ja_study["study_gate"] == "passed"
    assert q011ja_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ja_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_799
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ja_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 90
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ja_study, allow_nan=False)

    runner_path = Path(q011ja.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ja_degree34_ninety_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ja artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ja_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ja.q011b._canonical_json_sha256(q011ja._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
