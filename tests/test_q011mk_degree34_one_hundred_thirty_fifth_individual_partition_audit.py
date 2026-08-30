from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mk_degree34_one_hundred_thirty_fifth_individual_partition_audit as q011mk
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "7dc4e7719a1bdab8c8357b97db70a427648f6f1a120690381cc080e2bccc3796"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "3f4ca6c692a57d1f64a66a2cd0b20db100f5d945080c97a205c7642dd17368a4"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "c7152d0e713b3a3589fa3f966b882bb97f60a08128a5b704165623cb890c6f46",
    "partition_input_digest_sha256": (
        "a0e20d35648a9445de9380573216d316f0c37f02354b6051a4c18c364394708b"
    ),
    "allocation_audit_digest_sha256": (
        "0c98776b65c110c80d0115c57699a24be30735b523efeb9683cabdb77ae1c98e"
    ),
    "result_digest_sha256": "d8dd4778cb33dfc7481c814c3a2ca3ae43a160749c6ba1a8d9e7f2f8200d9aa1",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "0d29ce5d02ce4183cf206c9a3454bb71d15382898cc9f8aae69b8d73ed09bb73"
    ),
    "parent_center_product_interval_digest_sha256": (
        "e951f615c0b96e1e454f93f1a36add376321541f21dac78335e25636eda32fea"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "7b1b85a6b5cfdab282715121299f20c91d7b137b6fb098e246ef42b4c6659a8d"
    ),
    "allocation_classification_record_digest_sha256": (
        "067fa62e0d74522b157fcf01c8a217c660da5b2d8e626b77c028188ddb90fbaf"
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
def q011mk_structure() -> dict[str, Any]:
    sealed, artifacts = q011mk._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011mk._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011mk_study() -> dict[str, Any]:
    return q011mk.run_q011mk_study()


@pytest.fixture(scope="module")
def q011mk_cycle(q011mk_study: dict[str, Any]) -> dict[str, Any]:
    return q011mk_study["cycle"]


def test_q011mk_seals_q011mj_and_all_prior_inputs(q011mk_structure: dict[str, Any]) -> None:
    sealed = q011mk_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 327
    assert sealed["direct_digest_count"] == 1_484
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mj"]["digests"]) == q011mk.Q011MJ_DIGESTS
    assert sealed["q011mj"]["artifact_sha256"] == q011mk.Q011MJ_ARTIFACT_SHA256
    assert sealed["q011mj"]["runner_sha256"] == q011mk.Q011MJ_RUNNER_SHA256
    assert sealed["q011mj"]["resolved_witness_digest_sha256"] == (
        q011mk.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_THREE_RESOLUTION_DIGEST
    )


def test_q011mk_selects_exactly_flatten_ordinal_one_hundred_thirty_four(
    q011mk_structure: dict[str, Any],
) -> None:
    fixed = q011mk_structure["fixed"]
    selection = fixed["one_hundred_thirty_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 134
    assert selection["selected_left_index"] == 16
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(134))
    assert selection["ordinal_one_hundred_thirty_three_resolution_digest_sha256"] == (
        q011mk.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_thirty_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [6, 3], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 3_386
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011mk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == q011mk.EXPECTED_PARENT_CENTER_GAP_HEX
    assert parent["witness_digest_sha256"] == q011mk.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011mk_reconstructs_registered_partition_and_inventory(
    q011mk_structure: dict[str, Any],
) -> None:
    fixed = q011mk_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [6, 3], [5], [6, 1]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 6, 3, 5, 6, 1]
    assert any(
        identifier.endswith("center=148")
        for record in occupied
        for identifier in record["identifiers"]
    )
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011mk.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011mk.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 61_152
    assert fixed["full_allocation_digest_sha256"] == q011mk.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_386
    assert q011mk_structure["compatible_count"] == 3_386
    assert fixed["compatible_allocation_digest_sha256"] == q011mk.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 6, 0, 3, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 6, 0, 3, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 61_068
    assert fixed["parent_witness_compatible_index"] == 3_385
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mk result is not sealed")
def test_q011mk_classifies_every_registered_exact_interval(
    q011mk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011mk_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 3_386
    records = partition["allocation_classification_records"]
    assert len(records) == 3_386
    assert [record["compatible_allocation_index"] for record in records] == list(range(3_386))
    assert sum(partition["exact_relation_counts"].values()) == 3_386
    assert sum(partition["binary64_outward_relation_counts"].values()) == 3_386
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mk result is not sealed")
def test_q011mk_applies_registered_stopping_rule(q011mk_cycle: dict[str, Any]) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011mk_cycle["study_validity"] == "passed"
    assert q011mk_cycle["failed_validity_order"] == []
    assert q011mk_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mk_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mk_cycle["diagnostic_gates"].values())
    assert q011mk_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mk_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mk_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011mk.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011mk.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011mk.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mk_cycle["diagnostic_classification"] == expected
    assert not q011mk_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011mk_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_thirty_fifth_q011cb_witness"
        ],
        theorem["one_hundred_thirty_fifth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_thirty_fifth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mk result is not sealed")
def test_q011mk_preserves_boundary_and_reproducible_digests(
    q011mk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011mk_cycle["theorem_consequence"]
    assert theorem["q011mj_ordinal_one_hundred_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011me_ordinal_one_hundred_thirty_one_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 134" in q011mk_cycle["claim_boundary"]
    assert "ordinals 0 through 133" in q011mk_cycle["claim_boundary"]
    assert "later 44665 " in q011mk_cycle["claim_boundary"]
    assert "Q011ml" in q011mk_cycle["next_change"]
    assert {name: q011mk_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mk_cycle["result_digest_sha256"] == (
        q011mk.q011b._canonical_json_sha256(q011mk._result_digest_sections(q011mk_cycle))
    )
    assert q011mk._protocol_globals_are_restored()
    json.dumps(q011mk_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mk result is not sealed")
def test_q011mk_study_metadata_and_optional_artifact_are_scoped(
    q011mk_study: dict[str, Any],
) -> None:
    assert q011mk_study["schema_version"] == 1
    assert q011mk_study["source"] == source_metadata()
    assert q011mk_study["study_gate"] == "passed"
    assert q011mk_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mk_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_386
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mk_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 134
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mk_study, allow_nan=False)

    runner_path = Path(q011mk.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mk_degree34_one_hundred_thirty_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mk artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mk_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mk.q011b._canonical_json_sha256(q011mk._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
