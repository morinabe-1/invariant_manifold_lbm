from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011na_degree34_one_hundred_forty_third_individual_partition_audit as q011na
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "4d42c4ca5b633a215d9607a4db466e6b9892353078dc4635c56cad722182ca6f"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "838895008ae7a637c2e5a6b5c05267e06ce9808632d9420f68cd09a92d97c2d8"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "78cae3a8d1422662baf797932fe7277d5bd0705e734829bbaa1ebb3218065eb2",
    "partition_input_digest_sha256": (
        "062bc93da816ed43a08c57bb20780d1ecb8a614ea2877eb31014cfba3829253d"
    ),
    "allocation_audit_digest_sha256": (
        "2c119fb511138f4ed05fc29d1b4a9e8a4c6b8bdd52311662f0ab258f85408053"
    ),
    "result_digest_sha256": "c34474308e0cbc175c0e783d207ee2a2f327a076508471831fb02c715ef03f7c",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "ad400250d7aa18a8099806bd79389c6a7fffe9b90b96b1e9efa4c8c15b721126"
    ),
    "parent_center_product_interval_digest_sha256": (
        "3d91fd5d3f73cda6823a608ef055e4f01605d6f7774b082df42d65ea107380f1"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "1ee52152a95c51d3d2467d8f56b468b9607fa376057939561dc25fe74978325b"
    ),
    "allocation_classification_record_digest_sha256": (
        "51c1191e84773e90f81f1bfb6b3d1ba4282f9876138830d4a01cf8743689dd0f"
    ),
    "allocation_classification_stream_digest_sha256": (
        "9fc3783f159d4143789edf9bf553e0e1cc679d30ce3094d2a87ce0b0ab6fe368"
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
def q011na_structure() -> dict[str, Any]:
    sealed, artifacts = q011na._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011na._fixed_individual_input_audit(
        artifacts
    )
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011na_study() -> dict[str, Any]:
    return q011na.run_q011na_study()


@pytest.fixture(scope="module")
def q011na_cycle(q011na_study: dict[str, Any]) -> dict[str, Any]:
    return q011na_study["cycle"]


def test_q011na_seals_q011mz_and_all_prior_inputs(
    q011na_structure: dict[str, Any],
) -> None:
    sealed = q011na_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 343
    assert sealed["direct_digest_count"] == 1_556
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mz"]["digests"]) == q011na.Q011MZ_DIGESTS
    assert sealed["q011mz"]["artifact_sha256"] == q011na.Q011MZ_ARTIFACT_SHA256
    assert sealed["q011mz"]["runner_sha256"] == q011na.Q011MZ_RUNNER_SHA256
    assert sealed["q011mz"]["resolved_witness_digest_sha256"] == (
        q011na.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_ONE_RESOLUTION_DIGEST
    )


def test_q011na_selects_exactly_flatten_ordinal_one_hundred_forty_two(
    q011na_structure: dict[str, Any],
) -> None:
    fixed = q011na_structure["fixed"]
    selection = fixed["one_hundred_forty_third_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 142
    assert selection["selected_left_index"] == 17
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(142))
    assert selection["ordinal_one_hundred_forty_one_resolution_digest_sha256"] == (
        q011na.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_ONE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_third_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 2_906
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011na.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011na.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011na.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011na_reconstructs_registered_partition_and_inventory(
    q011na_structure: dict[str, Any],
) -> None:
    fixed = q011na_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [6, 1]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 7, 2, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert (
        fixed["occupied_class_record_digest_sha256"]
        == q011na.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011na.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 52_416
    assert fixed["full_allocation_digest_sha256"] == q011na.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_906
    assert q011na_structure["compatible_count"] == 2_906
    assert (
        fixed["compatible_allocation_digest_sha256"]
        == q011na.EXPECTED_COMPATIBLE_DIGEST
    )
    assert tuple(fixed["first_compatible_counts"]) == (
        q011na.EXPECTED_FIRST_COMPATIBLE_COUNTS
    )
    assert tuple(fixed["last_compatible_counts"]) == q011na.EXPECTED_SOURCE_COUNTS
    assert fixed["parent_witness_allocation_index"] == 52_332
    assert fixed["parent_witness_compatible_index"] == 2_905
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert q011na._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011na result is not sealed")
def test_q011na_classifies_every_registered_exact_interval_once(
    q011na_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011na_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_906
    assert partition["registered_class_totals"] == [1, 12, 7, 2, 5, 6, 1]
    assert partition["all_compatible_allocations_preserve_registered_class_totals"]
    assert partition["exact_product_evaluation_count"] == 1
    assert partition[
        "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_906
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(2_906)
    )
    assert all(
        record["class_totals"] == [1, 12, 7, 2, 5, 6, 1] for record in records
    )
    assert sum(partition["exact_relation_counts"].values()) == 2_906
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_906
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011na result is not sealed")
def test_q011na_applies_registered_stopping_rule(
    q011na_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011na_cycle["study_validity"] == "passed"
    assert q011na_cycle["failed_validity_order"] == []
    assert q011na_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011na_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011na_cycle["diagnostic_gates"].values())
    assert q011na_cycle["scientific_outcome"] == "not_evaluated"
    assert q011na_cycle["actual_resonance_outcome"] == "not_established"
    assert q011na_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011na.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011na.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011na.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011na_cycle["diagnostic_classification"] == expected
    assert not q011na_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011na_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_third_q011cb_witness"
        ],
        theorem[
            "one_hundred_forty_third_q011cb_witness_is_resolved_by_individual_partition"
        ],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_third_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011na result is not sealed")
def test_q011na_preserves_boundary_and_reproducible_digests(
    q011na_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011na_cycle["theorem_consequence"]
    assert theorem["q011mz_ordinal_one_hundred_forty_one_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 142" in q011na_cycle["claim_boundary"]
    assert "ordinals 0 through 141" in q011na_cycle["claim_boundary"]
    assert "later 44657 Q011cb refined signatures" in q011na_cycle["claim_boundary"]
    assert "Q011nb" in q011na_cycle["next_change"]
    assert {name: q011na_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011na_cycle["result_digest_sha256"] == (
        q011na.q011b._canonical_json_sha256(
            q011na._result_digest_sections(q011na_cycle)
        )
    )
    assert q011na._protocol_globals_are_restored()
    json.dumps(q011na_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011na result is not sealed")
def test_q011na_study_metadata_and_optional_artifact_are_scoped(
    q011na_study: dict[str, Any],
) -> None:
    assert q011na_study["schema_version"] == 1
    assert q011na_study["source"] == source_metadata()
    assert q011na_study["study_gate"] == "passed"
    assert q011na_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011na_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_906
    assert runtime["exact_product_evaluations"] == 1
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011na_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 142
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011na_study, allow_nan=False)

    runner_path = Path(q011na.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011na_degree34_one_hundred_forty_third_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011na artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011na_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011na.q011b._canonical_json_sha256(
            q011na._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
