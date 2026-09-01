from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ne_degree34_one_hundred_forty_fifth_individual_partition_audit as q011ne
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "60e8eac73f536daeda9366d8a962cb9f79cf5561a2293030422adbd80d63f6d9"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "2985f88d4c03533b7239ac84d7291cf5eeb648a198d4f409e6dd681f88ff42dd"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "a647475c93a4c108c021fc51d8f690605e23e8e770734638f38133e67fadeb18",
    "partition_input_digest_sha256": (
        "3def8c279301e7cb8af73bc33540c1ef68771f445f79ab9611bc724e0e6ae5bc"
    ),
    "allocation_audit_digest_sha256": (
        "a4bef3db3b7bf71e27799a41ee7bb01e0e860c9e43c473840cc2877dcd2ec32f"
    ),
    "result_digest_sha256": "4f7e22b772641ddec4d5255fae262c70d3fe834325c476e511f90a7a8b239d81",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "e860877829b63e5ae7e430b127d179c9f8ca1951887e2a22582ddb16e9c0fcbc"
    ),
    "parent_center_product_interval_digest_sha256": (
        "6acdc01a958a68c3f452f7d1eae7db0ad18cc54b5e4239dc386274a476d92dc1"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "754b465a9edf1e11c4da5402b718253d40497fd9c3ca0dc44c74bff195949c04"
    ),
    "allocation_classification_record_digest_sha256": (
        "6a81c8059eff77fba68297b5e4dabcb801be0e132f5339be5511ba1b695d9d9c"
    ),
    "allocation_classification_stream_digest_sha256": (
        "d8213615489009aeb8716e6158ff9e53b860b0fe39dd09d00e3d79b21d223335"
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
def q011ne_structure() -> dict[str, Any]:
    sealed, artifacts = q011ne._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ne._fixed_individual_input_audit(
        artifacts
    )
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ne_study() -> dict[str, Any]:
    return q011ne.run_q011ne_study()


@pytest.fixture(scope="module")
def q011ne_cycle(q011ne_study: dict[str, Any]) -> dict[str, Any]:
    return q011ne_study["cycle"]


def test_q011ne_seals_q011nd_and_all_prior_inputs(
    q011ne_structure: dict[str, Any],
) -> None:
    sealed = q011ne_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 347
    assert sealed["direct_digest_count"] == 1_574
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011nd"]["digests"]) == q011ne.Q011ND_DIGESTS
    assert sealed["q011nd"]["artifact_sha256"] == q011ne.Q011ND_ARTIFACT_SHA256
    assert sealed["q011nd"]["runner_sha256"] == q011ne.Q011ND_RUNNER_SHA256
    assert sealed["q011nd"]["resolved_witness_digest_sha256"] == (
        q011ne.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_THREE_RESOLUTION_DIGEST
    )
    repeated, repeated_artifacts = q011ne._sealed_input_audit()
    parent, parent_artifacts = q011ne.q011nd._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 347
    assert len(repeated_artifacts) == 347
    assert parent["passed"] and parent["artifact_count"] == 346
    assert len(parent_artifacts) == 346


def test_q011ne_selects_exactly_flatten_ordinal_one_hundred_forty_four(
    q011ne_structure: dict[str, Any],
) -> None:
    fixed = q011ne_structure["fixed"]
    selection = fixed["one_hundred_forty_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 144
    assert selection["selected_left_index"] == 18
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(144))
    assert selection["ordinal_one_hundred_forty_three_resolution_digest_sha256"] == (
        q011ne.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_255
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ne.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ne.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ne.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ne_reconstructs_registered_partition_and_inventory(
    q011ne_structure: dict[str, Any],
) -> None:
    fixed = q011ne_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [0, 7]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 8, 1, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert (
        fixed["occupied_class_record_digest_sha256"]
        == q011ne.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011ne.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 22_464
    assert fixed["full_allocation_digest_sha256"] == q011ne.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_255
    assert q011ne_structure["compatible_count"] == 1_255
    assert (
        fixed["compatible_allocation_digest_sha256"]
        == q011ne.EXPECTED_COMPATIBLE_DIGEST
    )
    assert tuple(fixed["first_compatible_counts"]) == (
        q011ne.EXPECTED_FIRST_COMPATIBLE_COUNTS
    )
    assert tuple(fixed["last_compatible_counts"]) == q011ne.EXPECTED_SOURCE_COUNTS
    assert fixed["parent_witness_allocation_index"] == 22_416
    assert fixed["parent_witness_compatible_index"] == 1_254
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert q011ne._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ne result is not sealed")
def test_q011ne_classifies_every_registered_exact_interval_once(
    q011ne_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011ne_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_255
    assert partition["registered_class_totals"] == [1, 12, 8, 1, 5, 7]
    assert partition["all_compatible_allocations_preserve_registered_class_totals"]
    assert partition["exact_product_evaluation_count"] == 1
    assert partition[
        "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_255
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(1_255)
    )
    assert all(
        record["class_totals"] == [1, 12, 8, 1, 5, 7] for record in records
    )
    assert sum(partition["exact_relation_counts"].values()) == 1_255
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_255
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ne result is not sealed")
def test_q011ne_applies_registered_stopping_rule(
    q011ne_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011ne_cycle["study_validity"] == "passed"
    assert q011ne_cycle["failed_validity_order"] == []
    assert q011ne_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ne_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ne_cycle["diagnostic_gates"].values())
    assert q011ne_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ne_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ne_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ne.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ne.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ne.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ne_cycle["diagnostic_classification"] == expected
    assert not q011ne_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ne_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_fifth_q011cb_witness"
        ],
        theorem[
            "one_hundred_forty_fifth_q011cb_witness_is_resolved_by_individual_partition"
        ],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_fifth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ne result is not sealed")
def test_q011ne_preserves_boundary_and_reproducible_digests(
    q011ne_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011ne_cycle["theorem_consequence"]
    assert theorem["q011nd_ordinal_one_hundred_forty_three_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 144" in q011ne_cycle["claim_boundary"]
    assert "ordinals 0 through 143" in q011ne_cycle["claim_boundary"]
    assert "later 44655 Q011cb refined signatures" in q011ne_cycle["claim_boundary"]
    assert "Q011nf" in q011ne_cycle["next_change"]
    assert {name: q011ne_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ne_cycle["result_digest_sha256"] == (
        q011ne.q011b._canonical_json_sha256(
            q011ne._result_digest_sections(q011ne_cycle)
        )
    )
    assert q011ne._protocol_globals_are_restored()
    json.dumps(q011ne_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ne result is not sealed")
def test_q011ne_study_metadata_and_optional_artifact_are_scoped(
    q011ne_study: dict[str, Any],
) -> None:
    assert q011ne_study["schema_version"] == 1
    assert q011ne_study["source"] == source_metadata()
    assert q011ne_study["study_gate"] == "passed"
    assert q011ne_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ne_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_255
    assert runtime["exact_product_evaluations"] == 1
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ne_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 144
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ne_study, allow_nan=False)

    runner_path = Path(q011ne.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ne_degree34_one_hundred_forty_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ne artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ne_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ne.q011b._canonical_json_sha256(
            q011ne._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
