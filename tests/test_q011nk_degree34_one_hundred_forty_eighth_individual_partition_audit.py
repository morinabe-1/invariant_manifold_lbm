from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011nk_degree34_one_hundred_forty_eighth_individual_partition_audit as q011nk
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
def q011nk_structure() -> dict[str, Any]:
    sealed, artifacts = q011nk._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011nk._fixed_individual_input_audit(
        artifacts
    )
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011nk_study() -> dict[str, Any]:
    return q011nk.run_q011nk_study()


@pytest.fixture(scope="module")
def q011nk_cycle(q011nk_study: dict[str, Any]) -> dict[str, Any]:
    return q011nk_study["cycle"]


def test_q011nk_seals_q011nj_and_all_prior_inputs(
    q011nk_structure: dict[str, Any],
) -> None:
    sealed = q011nk_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 353
    assert sealed["direct_digest_count"] == 1_601
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011nj"]["digests"]) == q011nk.Q011NJ_DIGESTS
    assert sealed["q011nj"]["artifact_sha256"] == q011nk.Q011NJ_ARTIFACT_SHA256
    assert sealed["q011nj"]["runner_sha256"] == q011nk.Q011NJ_RUNNER_SHA256
    assert sealed["q011nj"]["resolved_witness_digest_sha256"] == (
        q011nk.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_SIX_RESOLUTION_DIGEST
    )
    repeated, repeated_artifacts = q011nk._sealed_input_audit()
    parent, parent_artifacts = q011nk.q011nj._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 353
    assert len(repeated_artifacts) == 353
    assert parent["passed"] and parent["artifact_count"] == 352
    assert len(parent_artifacts) == 352


def test_q011nk_selects_exactly_flatten_ordinal_one_hundred_forty_seven(
    q011nk_structure: dict[str, Any],
) -> None:
    fixed = q011nk_structure["fixed"]
    selection = fixed["one_hundred_forty_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 147
    assert selection["selected_left_index"] == 18
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(147))
    assert selection["ordinal_one_hundred_forty_six_resolution_digest_sha256"] == (
        q011nk.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_SIX_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 3_104
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011nk.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011nk.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011nk.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011nk_reconstructs_registered_partition_and_inventory(
    q011nk_structure: dict[str, Any],
) -> None:
    fixed = q011nk_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [8, 1], [5], [3, 4]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 8, 1, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert (
        fixed["occupied_class_record_digest_sha256"]
        == q011nk.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011nk.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 56_160
    assert fixed["full_allocation_digest_sha256"] == q011nk.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_104
    assert q011nk_structure["compatible_count"] == 3_104
    assert (
        fixed["compatible_allocation_digest_sha256"]
        == q011nk.EXPECTED_COMPATIBLE_DIGEST
    )
    assert tuple(fixed["first_compatible_counts"]) == (
        q011nk.EXPECTED_FIRST_COMPATIBLE_COUNTS
    )
    assert tuple(fixed["last_compatible_counts"]) == q011nk.EXPECTED_SOURCE_COUNTS
    assert fixed["parent_witness_allocation_index"] == 56_040
    assert fixed["parent_witness_compatible_index"] == 3_103
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert q011nk._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nk result is not sealed")
def test_q011nk_classifies_every_registered_exact_interval_once(
    q011nk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011nk_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 3_104
    assert partition["registered_class_totals"] == [1, 12, 8, 1, 5, 3, 4]
    assert partition["all_compatible_allocations_preserve_registered_class_totals"]
    assert partition["exact_product_evaluation_count"] == 1
    assert partition[
        "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 3_104
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(3_104)
    )
    assert all(
        record["class_totals"] == [1, 12, 8, 1, 5, 3, 4] for record in records
    )
    assert sum(partition["exact_relation_counts"].values()) == 3_104
    assert sum(partition["binary64_outward_relation_counts"].values()) == 3_104
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nk result is not sealed")
def test_q011nk_applies_registered_stopping_rule(
    q011nk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011nk_cycle["study_validity"] == "passed"
    assert q011nk_cycle["failed_validity_order"] == []
    assert q011nk_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011nk_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011nk_cycle["diagnostic_gates"].values())
    assert q011nk_cycle["scientific_outcome"] == "not_evaluated"
    assert q011nk_cycle["actual_resonance_outcome"] == "not_established"
    assert q011nk_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011nk.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011nk.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011nk.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011nk_cycle["diagnostic_classification"] == expected
    assert not q011nk_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011nk_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_eighth_q011cb_witness"
        ],
        theorem[
            "one_hundred_forty_eighth_q011cb_witness_is_resolved_by_individual_partition"
        ],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_eighth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nk result is not sealed")
def test_q011nk_preserves_boundary_and_reproducible_digests(
    q011nk_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011nk_cycle["theorem_consequence"]
    assert theorem["q011nj_ordinal_one_hundred_forty_six_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 147" in q011nk_cycle["claim_boundary"]
    assert "ordinals 0 through 146" in q011nk_cycle["claim_boundary"]
    assert "later 44652 Q011cb refined signatures" in q011nk_cycle["claim_boundary"]
    assert "Q011nl" in q011nk_cycle["next_change"]
    assert {name: q011nk_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011nk_cycle["result_digest_sha256"] == (
        q011nk.q011b._canonical_json_sha256(
            q011nk._result_digest_sections(q011nk_cycle)
        )
    )
    assert q011nk._protocol_globals_are_restored()
    json.dumps(q011nk_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nk result is not sealed")
def test_q011nk_study_metadata_and_optional_artifact_are_scoped(
    q011nk_study: dict[str, Any],
) -> None:
    assert q011nk_study["schema_version"] == 1
    assert q011nk_study["source"] == source_metadata()
    assert q011nk_study["study_gate"] == "passed"
    assert q011nk_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011nk_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_104
    assert runtime["exact_product_evaluations"] == 1
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011nk_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 147
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011nk_study, allow_nan=False)

    runner_path = Path(q011nk.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011nk_degree34_one_hundred_forty_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011nk artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011nk_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011nk.q011b._canonical_json_sha256(
            q011nk._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
