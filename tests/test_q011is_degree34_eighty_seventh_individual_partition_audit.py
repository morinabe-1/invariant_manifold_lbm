from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011is_degree34_eighty_seventh_individual_partition_audit as q011is
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d6ed26a9e6830e72bd8f1b09f4c38012d5f4602609d61e2ef4807da124cc89a9"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8a751b36dd45065851bc609b079acf77f1163490c2edef442f809075162844c7"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "ad3d4290cf939707deb82cfee2ad6e618275094e80c4fbbe178093f76cd96178",
    "partition_input_digest_sha256": (
        "1939736d5695529815e8669d27b641702921a8e76399bc052e95507bfbf6d911"
    ),
    "allocation_audit_digest_sha256": (
        "73605157bb3da08680fa63f2dc95427f60824e0e78ee0234cb1bda1d7eff51b5"
    ),
    "result_digest_sha256": "cd3e93f9f994d2c497662a7ae21da925928b7fdcdc7c7e6d305604a1b7d7e17e",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "1f5e765d60afa626669195c32dd8e3e8c43c09a72e77a0603b48afe26e085903"
    ),
    "parent_center_product_interval_digest_sha256": (
        "a63816799b7d94b6b55f7dcf64562dd9eedad56602fbc98941b81559008dde07"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "be34373c6d3666b9b46521cc66edc3c6b0a8e89eb612818a8ad21f99f2578d30"
    ),
    "allocation_classification_record_digest_sha256": (
        "fada4460044b125a5596a2cd82c07aab5a38e1c7755eabbb04702d489114513b"
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
def q011is_structure() -> dict[str, Any]:
    sealed, artifacts = q011is._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011is._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011is_study() -> dict[str, Any]:
    return q011is.run_q011is_study()


@pytest.fixture(scope="module")
def q011is_cycle(q011is_study: dict[str, Any]) -> dict[str, Any]:
    return q011is_study["cycle"]


def test_q011is_seals_q011ir_and_all_prior_inputs(
    q011is_structure: dict[str, Any],
) -> None:
    sealed = q011is_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 231
    assert sealed["direct_digest_count"] == 1_052
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ir"]["digests"]) == q011is.Q011IR_DIGESTS
    assert sealed["q011ir"]["artifact_sha256"] == q011is.Q011IR_ARTIFACT_SHA256
    assert sealed["q011ir"]["runner_sha256"] == q011is.Q011IR_RUNNER_SHA256
    assert sealed["q011ir"]["resolved_witness_digest_sha256"] == (
        q011is.EXPECTED_ORDINAL_EIGHTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011is_selects_exactly_flatten_ordinal_eighty_six(
    q011is_structure: dict[str, Any],
) -> None:
    fixed = q011is_structure["fixed"]
    selection = fixed["eighty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 86
    assert selection["selected_left_index"] == 10
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(86))
    assert selection["ordinal_eighty_five_resolution_digest_sha256"] == (
        q011is.EXPECTED_ORDINAL_EIGHTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["eighty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [0, 9], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_219
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011is.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011is.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011is.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011is_reconstructs_registered_partition_and_inventory(
    q011is_structure: dict[str, Any],
) -> None:
    fixed = q011is_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [0, 9], [5], [6, 1]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 9, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011is.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011is.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 21_840
    assert fixed["full_allocation_digest_sha256"] == q011is.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_219
    assert q011is_structure["compatible_count"] == 1_219
    assert fixed["compatible_allocation_digest_sha256"] == (q011is.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 9, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 9, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 21_756
    assert fixed["parent_witness_compatible_index"] == 1_218
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011is result is not sealed")
def test_q011is_classifies_every_registered_exact_interval(
    q011is_cycle: dict[str, Any],
) -> None:
    partition = q011is_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_219
    records = partition["allocation_classification_records"]
    assert len(records) == 1_219
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_219))
    assert sum(partition["exact_relation_counts"].values()) == 1_219
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_219
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011is result is not sealed")
def test_q011is_applies_registered_stopping_rule(
    q011is_cycle: dict[str, Any],
) -> None:
    assert q011is_cycle["study_validity"] == "passed"
    assert q011is_cycle["failed_validity_order"] == []
    assert q011is_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011is_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011is_cycle["diagnostic_gates"].values())
    assert q011is_cycle["scientific_outcome"] == "not_evaluated"
    assert q011is_cycle["actual_resonance_outcome"] == "not_established"
    assert q011is_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011is.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011is.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011is.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011is_cycle["diagnostic_classification"] == expected
    assert not q011is_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011is_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_eighty_seventh_q011cb_witness"],
        theorem["eighty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_eighty_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011is result is not sealed")
def test_q011is_preserves_boundary_and_reproducible_digests(
    q011is_cycle: dict[str, Any],
) -> None:
    theorem = q011is_cycle["theorem_consequence"]
    assert theorem["q011ir_ordinal_eighty_five_phase_resolution_is_preserved"]
    assert theorem["q011iq_ordinal_eighty_five_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 86" in q011is_cycle["claim_boundary"]
    assert "ordinals 0 through 85" in q011is_cycle["claim_boundary"]
    assert "later 44713 Q011cb refined signatures" in q011is_cycle["claim_boundary"]
    assert "Q011it" in q011is_cycle["next_change"]
    assert {name: q011is_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011is_cycle["result_digest_sha256"] == (
        q011is.q011b._canonical_json_sha256(q011is._result_digest_sections(q011is_cycle))
    )
    assert q011is._protocol_globals_are_restored()
    json.dumps(q011is_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011is result is not sealed")
def test_q011is_study_metadata_and_optional_artifact_are_scoped(
    q011is_study: dict[str, Any],
) -> None:
    assert q011is_study["schema_version"] == 1
    assert q011is_study["source"] == source_metadata()
    assert q011is_study["study_gate"] == "passed"
    assert q011is_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011is_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_219
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011is_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 86
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011is_study, allow_nan=False)

    runner_path = Path(q011is.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011is_degree34_eighty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011is artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011is_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011is.q011b._canonical_json_sha256(q011is._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
