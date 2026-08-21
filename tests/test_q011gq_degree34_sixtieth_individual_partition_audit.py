from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gq_degree34_sixtieth_individual_partition_audit as q011gq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = None
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = None
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011gq_structure() -> dict[str, Any]:
    sealed, artifacts = q011gq._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011gq._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011gq_study() -> dict[str, Any]:
    return q011gq.run_q011gq_study()


@pytest.fixture(scope="module")
def q011gq_cycle(q011gq_study: dict[str, Any]) -> dict[str, Any]:
    return q011gq_study["cycle"]


def test_q011gq_seals_q011gp_and_all_prior_inputs(
    q011gq_structure: dict[str, Any],
) -> None:
    sealed = q011gq_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 177
    assert sealed["direct_digest_count"] == 809
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gp"]["digests"]) == q011gq.Q011GP_DIGESTS
    assert sealed["q011gp"]["artifact_sha256"] == q011gq.Q011GP_ARTIFACT_SHA256
    assert sealed["q011gp"]["runner_sha256"] == q011gq.Q011GP_RUNNER_SHA256
    assert sealed["q011gp"]["resolved_witness_digest_sha256"] == (
        q011gq.EXPECTED_ORDINAL_FIFTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011gq_selects_exactly_flatten_ordinal_fifty_nine(
    q011gq_structure: dict[str, Any],
) -> None:
    fixed = q011gq_structure["fixed"]
    selection = fixed["sixtieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 59
    assert selection["selected_left_index"] == 7
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(59))
    assert selection["ordinal_fifty_eight_resolution_digest_sha256"] == (
        q011gq.EXPECTED_ORDINAL_FIFTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["sixtieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [7, 2], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 2_266
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011gq.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011gq.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011gq.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011gq_reconstructs_registered_partition_and_inventory(
    q011gq_structure: dict[str, Any],
) -> None:
    fixed = q011gq_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [7, 2],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 7, 2, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011gq.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011gq.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 40_320
    assert fixed["full_allocation_digest_sha256"] == q011gq.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_266
    assert q011gq_structure["compatible_count"] == 2_266
    assert fixed["compatible_allocation_digest_sha256"] == q011gq.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 7, 0, 2, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 7, 0, 2, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 40_200
    assert fixed["parent_witness_compatible_index"] == 2_265
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gq result is not sealed")
def test_q011gq_classifies_every_registered_exact_interval(
    q011gq_cycle: dict[str, Any],
) -> None:
    partition = q011gq_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_266
    assert len(partition["allocation_classification_records"]) == 2_266
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gq result is not sealed")
def test_q011gq_applies_the_registered_exclusive_stopping_rule(
    q011gq_cycle: dict[str, Any],
) -> None:
    assert q011gq_cycle["study_validity"] == "passed"
    assert q011gq_cycle["failed_validity_order"] == []
    assert q011gq_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011gq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gq_cycle["diagnostic_gates"].values())
    assert q011gq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gq_cycle["actual_resonance_outcome"] == "not_established"
    assert not q011gq_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gq result is not sealed")
def test_q011gq_preserves_boundary_and_reproducible_digests(
    q011gq_cycle: dict[str, Any],
) -> None:
    theorem = q011gq_cycle["theorem_consequence"]
    assert theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
    assert theorem["q011go_ordinal_fifty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 59" in q011gq_cycle["claim_boundary"]
    assert "ordinals 0 through 58" in q011gq_cycle["claim_boundary"]
    assert "later 44740 Q011cb refined signatures" in q011gq_cycle["claim_boundary"]
    assert "Q011gr" in q011gq_cycle["next_change"]
    json.dumps(q011gq_cycle, allow_nan=False)
    assert {name: q011gq_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011gq_cycle["result_digest_sha256"] == (
        q011gq.q011b._canonical_json_sha256(q011gq._result_digest_sections(q011gq_cycle))
    )
    assert q011gq._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gq result is not sealed")
def test_q011gq_study_metadata_and_optional_artifact_are_scoped(
    q011gq_study: dict[str, Any],
) -> None:
    assert q011gq_study["schema_version"] == 1
    assert q011gq_study["source"] == source_metadata()
    assert q011gq_study["study_gate"] == "passed"
    runtime = q011gq_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_266
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gq_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 59
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gq_study, allow_nan=False)

    runner_path = Path(q011gq.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gq_degree34_sixtieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gq_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gq.q011b._canonical_json_sha256(q011gq._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
