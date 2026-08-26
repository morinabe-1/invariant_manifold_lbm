from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jg_degree34_ninety_fourth_individual_partition_audit as q011jg
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
def q011jg_structure() -> dict[str, Any]:
    sealed, artifacts = q011jg._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011jg._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011jg_study() -> dict[str, Any]:
    return q011jg.run_q011jg_study()


@pytest.fixture(scope="module")
def q011jg_cycle(q011jg_study: dict[str, Any]) -> dict[str, Any]:
    return q011jg_study["cycle"]


def test_q011jg_seals_q011jf_and_all_prior_inputs(
    q011jg_structure: dict[str, Any],
) -> None:
    sealed = q011jg_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 245
    assert sealed["direct_digest_count"] == 1_115
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jf"]["digests"]) == q011jg.Q011JF_DIGESTS
    assert sealed["q011jf"]["artifact_sha256"] == q011jg.Q011JF_ARTIFACT_SHA256
    assert sealed["q011jf"]["runner_sha256"] == q011jg.Q011JF_RUNNER_SHA256
    assert sealed["q011jf"]["resolved_witness_digest_sha256"] == (
        q011jg.EXPECTED_ORDINAL_NINETY_TWO_RESOLUTION_DIGEST
    )


def test_q011jg_selects_exactly_flatten_ordinal_ninety_three(
    q011jg_structure: dict[str, Any],
) -> None:
    fixed = q011jg_structure["fixed"]
    selection = fixed["ninety_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 93
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(93))
    assert selection["ordinal_ninety_two_resolution_digest_sha256"] == (
        q011jg.EXPECTED_ORDINAL_NINETY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["ninety_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 2_799
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011jg.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011jg.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011jg.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011jg_reconstructs_registered_partition_and_inventory(
    q011jg_structure: dict[str, Any],
) -> None:
    fixed = q011jg_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [5, 2]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011jg.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011jg.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_544
    assert fixed["full_allocation_digest_sha256"] == q011jg.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_799
    assert q011jg_structure["compatible_count"] == 2_799
    assert fixed["compatible_allocation_digest_sha256"] == q011jg.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 50_436
    assert fixed["parent_witness_compatible_index"] == 2_798
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jg result is not sealed")
def test_q011jg_classifies_every_registered_exact_interval(
    q011jg_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011jg_cycle["individual_allocation_interval_audit"]
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


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jg result is not sealed")
def test_q011jg_applies_registered_stopping_rule(
    q011jg_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011jg_cycle["study_validity"] == "passed"
    assert q011jg_cycle["failed_validity_order"] == []
    assert q011jg_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jg_cycle["diagnostic_gates"].values())
    assert q011jg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jg_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jg_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011jg.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011jg.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011jg.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jg_cycle["diagnostic_classification"] == expected
    assert not q011jg_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011jg_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_fourth_q011cb_witness"],
        theorem["ninety_fourth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_ninety_fourth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jg result is not sealed")
def test_q011jg_preserves_boundary_and_reproducible_digests(
    q011jg_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011jg_cycle["theorem_consequence"]
    assert theorem["q011jf_ordinal_ninety_two_phase_resolution_is_preserved"]
    assert theorem["q011je_ordinal_ninety_two_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 93" in q011jg_cycle["claim_boundary"]
    assert "ordinals 0 through 92" in q011jg_cycle["claim_boundary"]
    assert "later 44706 Q011cb refined signatures" in q011jg_cycle["claim_boundary"]
    assert "Q011jh" in q011jg_cycle["next_change"]
    assert {name: q011jg_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jg_cycle["result_digest_sha256"] == (
        q011jg.q011b._canonical_json_sha256(q011jg._result_digest_sections(q011jg_cycle))
    )
    assert q011jg._protocol_globals_are_restored()
    json.dumps(q011jg_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jg result is not sealed")
def test_q011jg_study_metadata_and_optional_artifact_are_scoped(
    q011jg_study: dict[str, Any],
) -> None:
    assert q011jg_study["schema_version"] == 1
    assert q011jg_study["source"] == source_metadata()
    assert q011jg_study["study_gate"] == "passed"
    assert q011jg_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jg_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_799
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jg_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 93
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jg_study, allow_nan=False)

    runner_path = Path(q011jg.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jg_degree34_ninety_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jg_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jg.q011b._canonical_json_sha256(q011jg._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
