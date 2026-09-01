from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011no_degree34_one_hundred_fiftieth_individual_partition_audit as q011no
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = None
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = None
EXPECTED_REFINEMENT_OUTCOME: str | None = None
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
def q011no_structure() -> dict[str, Any]:
    sealed, artifacts = q011no._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011no._fixed_individual_input_audit(
        artifacts
    )
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011no_study() -> dict[str, Any]:
    return q011no.run_q011no_study()


@pytest.fixture(scope="module")
def q011no_cycle(q011no_study: dict[str, Any]) -> dict[str, Any]:
    return q011no_study["cycle"]


def test_q011no_seals_q011nn_and_all_prior_inputs(
    q011no_structure: dict[str, Any],
) -> None:
    sealed = q011no_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 357
    assert sealed["direct_digest_count"] == 1_619
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011nn"]["digests"]) == q011no.Q011NN_DIGESTS
    assert sealed["q011nn"]["artifact_sha256"] == q011no.Q011NN_ARTIFACT_SHA256
    assert sealed["q011nn"]["runner_sha256"] == q011no.Q011NN_RUNNER_SHA256
    assert sealed["q011nn"]["resolved_witness_digest_sha256"] == (
        q011no.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_EIGHT_RESOLUTION_DIGEST
    )
    repeated, repeated_artifacts = q011no._sealed_input_audit()
    parent, parent_artifacts = q011no.q011nn._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 357
    assert len(repeated_artifacts) == 357
    assert parent["passed"] and parent["artifact_count"] == 356
    assert len(parent_artifacts) == 356


def test_q011no_selects_exactly_flatten_ordinal_one_hundred_forty_nine(
    q011no_structure: dict[str, Any],
) -> None:
    fixed = q011no_structure["fixed"]
    selection = fixed["one_hundred_fiftieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 149
    assert selection["selected_left_index"] == 18
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(149))
    assert selection["ordinal_one_hundred_forty_eight_resolution_digest_sha256"] == (
        q011no.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_fiftieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_799
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011no.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011no.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011no.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011no_reconstructs_registered_partition_and_inventory(
    q011no_structure: dict[str, Any],
) -> None:
    fixed = q011no_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [5, 2]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 8, 1, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert (
        fixed["occupied_class_record_digest_sha256"]
        == q011no.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011no.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_544
    assert fixed["full_allocation_digest_sha256"] == q011no.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_799
    assert q011no_structure["compatible_count"] == 2_799
    assert (
        fixed["compatible_allocation_digest_sha256"]
        == q011no.EXPECTED_COMPATIBLE_DIGEST
    )
    assert tuple(fixed["first_compatible_counts"]) == (
        q011no.EXPECTED_FIRST_COMPATIBLE_COUNTS
    )
    assert tuple(fixed["last_compatible_counts"]) == q011no.EXPECTED_SOURCE_COUNTS
    assert fixed["parent_witness_allocation_index"] == 50_436
    assert fixed["parent_witness_compatible_index"] == 2_798
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert q011no._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011no result is not sealed")
def test_q011no_classifies_every_registered_exact_interval_once(
    q011no_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011no_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_799
    assert partition["registered_class_totals"] == [1, 12, 8, 1, 5, 5, 2]
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
        record["class_totals"] == [1, 12, 8, 1, 5, 5, 2] for record in records
    )
    assert sum(partition["exact_relation_counts"].values()) == 2_799
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_799
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011no result is not sealed")
def test_q011no_applies_registered_stopping_rule(
    q011no_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011no_cycle["study_validity"] == "passed"
    assert q011no_cycle["failed_validity_order"] == []
    assert q011no_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011no_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011no_cycle["diagnostic_gates"].values())
    assert q011no_cycle["scientific_outcome"] == "not_evaluated"
    assert q011no_cycle["actual_resonance_outcome"] == "not_established"
    assert q011no_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011no.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011no.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011no.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011no_cycle["diagnostic_classification"] == expected
    assert not q011no_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011no_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_fiftieth_q011cb_witness"
        ],
        theorem[
            "one_hundred_fiftieth_q011cb_witness_is_resolved_by_individual_partition"
        ],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_fiftieth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011no result is not sealed")
def test_q011no_preserves_boundary_and_reproducible_digests(
    q011no_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011no_cycle["theorem_consequence"]
    assert theorem["q011nn_ordinal_one_hundred_forty_eight_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 149" in q011no_cycle["claim_boundary"]
    assert "ordinals 0 through 148" in q011no_cycle["claim_boundary"]
    assert "later 44650 Q011cb refined signatures" in q011no_cycle["claim_boundary"]
    assert "Q011np" in q011no_cycle["next_change"]
    assert {name: q011no_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011no_cycle["result_digest_sha256"] == (
        q011no.q011b._canonical_json_sha256(
            q011no._result_digest_sections(q011no_cycle)
        )
    )
    assert q011no._protocol_globals_are_restored()
    json.dumps(q011no_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011no result is not sealed")
def test_q011no_study_metadata_and_optional_artifact_are_scoped(
    q011no_study: dict[str, Any],
) -> None:
    assert q011no_study["schema_version"] == 1
    assert q011no_study["source"] == source_metadata()
    assert q011no_study["study_gate"] == "passed"
    assert q011no_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011no_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_799
    assert runtime["exact_product_evaluations"] == 1
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011no_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 149
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011no_study, allow_nan=False)

    runner_path = Path(q011no.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011no_degree34_one_hundred_fiftieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011no artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011no_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011no.q011b._canonical_json_sha256(
            q011no._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
