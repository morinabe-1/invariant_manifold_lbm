from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ie_degree34_eightieth_individual_partition_audit as q011ie
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "20ef6da22835a12ab4a38e739bf0c78dd934eda6360e875e7a96185df74166a6"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "76db43e71ae464b299b82f50d86c6aeee89fb5f0123e2d7ab2de451e74691ccd"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "76aca6d8d712f6418f03b11f1bf60eb8fe528a4a7f379d03e93e6d278f52e58e",
    "partition_input_digest_sha256": (
        "bdddcb6d4e0dcef525304170dd1e6f9341817e40c4dd345edaccbbd1726bf124"
    ),
    "allocation_audit_digest_sha256": (
        "6414f4bced8c72e4d61395dfa838418906e20293334c3f55cd72b685eed344b2"
    ),
    "result_digest_sha256": "c0284763fc7364b6cf5723ad1af25e0144e25b6795a1d88a6afe8c492e129ab8",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "75d9292d1c2f76f4becb25bf9cf3f0516492657cca9cfcc33b736e7cbeb77d76"
    ),
    "parent_center_product_interval_digest_sha256": (
        "fa3ebe8615a2562e4c7fd328cc7ff791b15da65c03e3f5719a8ce2eadfd05c70"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "2de9df73a86a016de7a252a71bb5137d69d49d13b651bbb2747387273e5aed52"
    ),
    "allocation_classification_record_digest_sha256": (
        "1d9c94e079a1a48e367f8c561e77381a2e0cd90a5ac8ad14d887ad7677e9a6c0"
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
def q011ie_structure() -> dict[str, Any]:
    sealed, artifacts = q011ie._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ie._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ie_study() -> dict[str, Any]:
    return q011ie.run_q011ie_study()


@pytest.fixture(scope="module")
def q011ie_cycle(q011ie_study: dict[str, Any]) -> dict[str, Any]:
    return q011ie_study["cycle"]


def test_q011ie_seals_q011id_and_all_prior_inputs(q011ie_structure: dict[str, Any]) -> None:
    sealed = q011ie_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 217
    assert sealed["direct_digest_count"] == 989
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011id"]["digests"]) == q011ie.Q011ID_DIGESTS
    assert sealed["q011id"]["artifact_sha256"] == q011ie.Q011ID_ARTIFACT_SHA256
    assert sealed["q011id"]["runner_sha256"] == q011ie.Q011ID_RUNNER_SHA256
    assert sealed["q011id"]["resolved_witness_digest_sha256"] == (
        q011ie.EXPECTED_ORDINAL_SEVENTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011ie_selects_exactly_flatten_ordinal_seventy_nine(
    q011ie_structure: dict[str, Any],
) -> None:
    fixed = q011ie_structure["fixed"]
    selection = fixed["eightieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 79
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(79))
    assert selection["ordinal_seventy_eight_resolution_digest_sha256"] == (
        q011ie.EXPECTED_ORDINAL_SEVENTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["eightieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 382
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ie.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ie.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ie.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ie_reconstructs_registered_partition_and_inventory(
    q011ie_structure: dict[str, Any],
) -> None:
    fixed = q011ie_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [7, 0]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011ie.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011ie.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 6_720
    assert fixed["full_allocation_digest_sha256"] == q011ie.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 382
    assert q011ie_structure["compatible_count"] == 382
    assert fixed["compatible_allocation_digest_sha256"] == q011ie.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 6_672
    assert fixed["parent_witness_compatible_index"] == 381
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ie result is not sealed")
def test_q011ie_classifies_every_registered_exact_interval(q011ie_cycle: dict[str, Any]) -> None:
    partition = q011ie_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 382
    records = partition["allocation_classification_records"]
    assert len(records) == 382
    assert [record["compatible_allocation_index"] for record in records] == list(range(382))
    assert sum(partition["exact_relation_counts"].values()) == 382
    assert sum(partition["binary64_outward_relation_counts"].values()) == 382
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ie result is not sealed")
def test_q011ie_applies_the_registered_exclusive_stopping_rule(
    q011ie_cycle: dict[str, Any],
) -> None:
    assert q011ie_cycle["study_validity"] == "passed"
    assert q011ie_cycle["failed_validity_order"] == []
    assert q011ie_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ie_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ie_cycle["diagnostic_gates"].values())
    assert q011ie_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ie_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ie_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ie.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ie.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ie.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ie_cycle["diagnostic_classification"] == expected
    assert not q011ie_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ie_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_eightieth_q011cb_witness"],
        theorem["eightieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_eightieth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ie result is not sealed")
def test_q011ie_preserves_boundary_and_reproducible_digests(
    q011ie_cycle: dict[str, Any],
) -> None:
    theorem = q011ie_cycle["theorem_consequence"]
    assert theorem["q011id_ordinal_seventy_eight_phase_resolution_is_preserved"]
    assert theorem["q011ic_ordinal_seventy_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ib_ordinal_seventy_seven_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 79" in q011ie_cycle["claim_boundary"]
    assert "ordinals 0 through 78" in q011ie_cycle["claim_boundary"]
    assert "later 44720 Q011cb refined signatures" in q011ie_cycle["claim_boundary"]
    assert "Q011if" in q011ie_cycle["next_change"]
    json.dumps(q011ie_cycle, allow_nan=False)
    assert {name: q011ie_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ie_cycle["result_digest_sha256"] == (
        q011ie.q011b._canonical_json_sha256(q011ie._result_digest_sections(q011ie_cycle))
    )
    assert q011ie._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ie result is not sealed")
def test_q011ie_study_metadata_and_optional_artifact_are_scoped(
    q011ie_study: dict[str, Any],
) -> None:
    assert q011ie_study["schema_version"] == 1
    assert q011ie_study["source"] == source_metadata()
    assert q011ie_study["study_gate"] == "passed"
    assert q011ie_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ie_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 382
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ie_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 79
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ie_study, allow_nan=False)

    runner_path = Path(q011ie.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ie_degree34_eightieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ie artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ie_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ie.q011b._canonical_json_sha256(q011ie._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
