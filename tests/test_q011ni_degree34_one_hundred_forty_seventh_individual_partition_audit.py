from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ni_degree34_one_hundred_forty_seventh_individual_partition_audit as q011ni
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "07ffeebee9e32c868bf1d726abe717fa4530903e4afef12245041a4b06be95aa"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "267c637818a036d83f68d6fa85c92c99ff03618c16cd1f9c0917f76610d899ec"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "19e93fb4aefd4eadcdb2396d4678dcc516c0599aa49a331c558de6342d4836cf",
    "partition_input_digest_sha256": (
        "d5bf50b66d3379f33aa6a19e47a996da80f775c9c36d1667a5cd77d3da04affa"
    ),
    "allocation_audit_digest_sha256": (
        "f600623ad4c9fa96bb6efa0a07eda47602e8479f7021a9b5e3adb187ff2485a1"
    ),
    "result_digest_sha256": "46a853f1009fb06ae4ce7f72c8371f4a96ee0005c23a1da0ab48c5edbd1dc5e9",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "1515374b8cc39a2ca2612f9f19f4734e2f6831e88de57dd2de7ef3b41582306c"
    ),
    "parent_center_product_interval_digest_sha256": (
        "9173dcd888c978c05198da502ad62ac6f9ee43330af3924498e92ebae7df8478"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "b19987d0b83cf33075a520e19de6f7dac8e3cdaf312f6a1a5c27953fb7af094f"
    ),
    "allocation_classification_record_digest_sha256": (
        "804129b6c135813785a7ac4b1bca9f94a8ee10d6e74f797e665e86163dc550d4"
    ),
    "allocation_classification_stream_digest_sha256": (
        "b140c69635a66c4d357b4c1a5f65b3db28d42af36b5a7e10c4bf9e1f6f932445"
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
def q011ni_structure() -> dict[str, Any]:
    sealed, artifacts = q011ni._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ni._fixed_individual_input_audit(
        artifacts
    )
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ni_study() -> dict[str, Any]:
    return q011ni.run_q011ni_study()


@pytest.fixture(scope="module")
def q011ni_cycle(q011ni_study: dict[str, Any]) -> dict[str, Any]:
    return q011ni_study["cycle"]


def test_q011ni_seals_q011nh_and_all_prior_inputs(
    q011ni_structure: dict[str, Any],
) -> None:
    sealed = q011ni_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 351
    assert sealed["direct_digest_count"] == 1_592
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011nh"]["digests"]) == q011ni.Q011NH_DIGESTS
    assert sealed["q011nh"]["artifact_sha256"] == q011ni.Q011NH_ARTIFACT_SHA256
    assert sealed["q011nh"]["runner_sha256"] == q011ni.Q011NH_RUNNER_SHA256
    assert sealed["q011nh"]["resolved_witness_digest_sha256"] == (
        q011ni.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST
    )
    repeated, repeated_artifacts = q011ni._sealed_input_audit()
    parent, parent_artifacts = q011ni.q011nh._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 351
    assert len(repeated_artifacts) == 351
    assert parent["passed"] and parent["artifact_count"] == 350
    assert len(parent_artifacts) == 350


def test_q011ni_selects_exactly_flatten_ordinal_one_hundred_forty_six(
    q011ni_structure: dict[str, Any],
) -> None:
    fixed = q011ni_structure["fixed"]
    selection = fixed["one_hundred_forty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 146
    assert selection["selected_left_index"] == 18
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(146))
    assert selection["ordinal_one_hundred_forty_five_resolution_digest_sha256"] == (
        q011ni.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 2_799
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ni.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ni.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ni.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ni_reconstructs_registered_partition_and_inventory(
    q011ni_structure: dict[str, Any],
) -> None:
    fixed = q011ni_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [2, 5]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 8, 1, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert (
        fixed["occupied_class_record_digest_sha256"]
        == q011ni.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011ni.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_544
    assert fixed["full_allocation_digest_sha256"] == q011ni.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_799
    assert q011ni_structure["compatible_count"] == 2_799
    assert (
        fixed["compatible_allocation_digest_sha256"]
        == q011ni.EXPECTED_COMPATIBLE_DIGEST
    )
    assert tuple(fixed["first_compatible_counts"]) == (
        q011ni.EXPECTED_FIRST_COMPATIBLE_COUNTS
    )
    assert tuple(fixed["last_compatible_counts"]) == q011ni.EXPECTED_SOURCE_COUNTS
    assert fixed["parent_witness_allocation_index"] == 50_436
    assert fixed["parent_witness_compatible_index"] == 2_798
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert q011ni._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ni result is not sealed")
def test_q011ni_classifies_every_registered_exact_interval_once(
    q011ni_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011ni_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_799
    assert partition["registered_class_totals"] == [1, 12, 8, 1, 5, 2, 5]
    assert partition["all_compatible_allocations_preserve_registered_class_totals"]
    assert partition["exact_product_evaluation_count"] == 1
    assert partition[
        "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_799
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(2_799)
    )
    assert all(
        record["class_totals"] == [1, 12, 8, 1, 5, 2, 5] for record in records
    )
    assert sum(partition["exact_relation_counts"].values()) == 2_799
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_799
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ni result is not sealed")
def test_q011ni_applies_registered_stopping_rule(
    q011ni_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011ni_cycle["study_validity"] == "passed"
    assert q011ni_cycle["failed_validity_order"] == []
    assert q011ni_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ni_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ni_cycle["diagnostic_gates"].values())
    assert q011ni_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ni_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ni_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ni.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ni.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ni.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ni_cycle["diagnostic_classification"] == expected
    assert not q011ni_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ni_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_seventh_q011cb_witness"
        ],
        theorem[
            "one_hundred_forty_seventh_q011cb_witness_is_resolved_by_individual_partition"
        ],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ni result is not sealed")
def test_q011ni_preserves_boundary_and_reproducible_digests(
    q011ni_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011ni_cycle["theorem_consequence"]
    assert theorem["q011nh_ordinal_one_hundred_forty_five_phase_resolution_is_preserved"]
    assert theorem["q011na_ordinal_one_hundred_forty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011my_ordinal_one_hundred_forty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mx_ordinal_one_hundred_forty_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 146" in q011ni_cycle["claim_boundary"]
    assert "ordinals 0 through 145" in q011ni_cycle["claim_boundary"]
    assert "later 44653 Q011cb refined signatures" in q011ni_cycle["claim_boundary"]
    assert "Q011nj" in q011ni_cycle["next_change"]
    assert {name: q011ni_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ni_cycle["result_digest_sha256"] == (
        q011ni.q011b._canonical_json_sha256(
            q011ni._result_digest_sections(q011ni_cycle)
        )
    )
    assert q011ni._protocol_globals_are_restored()
    json.dumps(q011ni_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ni result is not sealed")
def test_q011ni_study_metadata_and_optional_artifact_are_scoped(
    q011ni_study: dict[str, Any],
) -> None:
    assert q011ni_study["schema_version"] == 1
    assert q011ni_study["source"] == source_metadata()
    assert q011ni_study["study_gate"] == "passed"
    assert q011ni_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ni_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_799
    assert runtime["exact_product_evaluations"] == 1
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ni_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 146
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ni_study, allow_nan=False)

    runner_path = Path(q011ni.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ni_degree34_one_hundred_forty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ni artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ni_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ni.q011b._canonical_json_sha256(
            q011ni._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
