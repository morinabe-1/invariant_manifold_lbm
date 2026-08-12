from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

import research.q011cb_degree34_second_overlap_refinement as q011cb
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = (
    "d7828cb2aef583ff82bd421212837534169ba42ad1962961cf0003e9f812b085"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "9e191ead642e398ccd013c783b0ddeae78e6e7e4c3bf443e08bd64c9e826aa5b"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "cee7e83699027ea5d12ba79b05e06d19c1a8bff5400d06807d52b1f4ac9f4f1e",
    "refinement_input_digest_sha256": (
        "bdd175e1b065849077bcb15ab16f2cb2dd0011308a4a8c7748ba7c10d88278cc"
    ),
    "targeted_sweep_digest_sha256": (
        "0dd5d08276fd5f4246a912ace617e4b6ec72007e3994b508d13d875917a40924"
    ),
    "result_digest_sha256": "eb5011b3a2767f9618bc71c31c1cb889a0a108f819592a6a8addc169abe855e5",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "5163889870c144df4cea0f5ff232db156d4920bba80bb7220241e7663580b0aa"
    ),
    "class_power_record_digest_sha256": (
        "4f3f082ab45e8b743a22d9315a472a6a11bfe4504e569d8743117e7dff49e438"
    ),
    "group_signature_digest_sha256": (
        "f5477dcb209f78f4614867753385d89fc96ea921e39f91b5d9faa7268c0f8ef9"
    ),
    "pair_pool_record_digest_sha256": (
        "dbdffe49d1db1768ba071671e0469ec4efa0246cfa5f6047849b7099ae2cae62"
    ),
    "bound_matrix_digest_sha256": (
        "6faeb3b928d2d825afb4422ced9a8ca6fda187f661cd23122139932015eb2060"
    ),
    "coefficient_matrix_digest_sha256": (
        "140768950c770970b6c8295fd3159a6e70aff122b3383d0d9e2dad0a2abb82d8"
    ),
    "classification_matrix_digest_sha256": (
        "63f916d5a53585ec8830f7a54b40396172c192febd5c83548f94f36e1c8c57dd"
    ),
}


@pytest.fixture(scope="module")
def q011cb_study() -> dict[str, Any]:
    return q011cb.run_q011cb_study()


@pytest.fixture(scope="module")
def q011cb_cycle(q011cb_study: dict[str, Any]) -> dict[str, Any]:
    return q011cb_study["cycle"]


def test_q011cb_seals_q011ca_and_all_prior_inputs(
    q011cb_cycle: dict[str, Any],
) -> None:
    sealed = q011cb_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 58
    assert sealed["direct_digest_count"] == 274
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ca"]["digests"]) == q011cb.Q011CA_DIGESTS
    assert sealed["q011ca"]["artifact_sha256"] == q011cb.Q011CA_ARTIFACT_SHA256
    assert sealed["q011ca"]["runner_sha256"] == q011cb.Q011CA_RUNNER_SHA256


def test_q011cb_reconstructs_the_registered_parent_and_refinement(
    q011cb_cycle: dict[str, Any],
) -> None:
    fixed = q011cb_cycle["fixed_blockwise_refinement_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_aggregate_index"] == 2340
    assert fixed["selected_type_counts"] == [13, 9, 5, 7]
    assert fixed["parent_external_group_indices"] == [97]
    assert fixed["parent_target_identifier_count"] == 16
    assert fixed["parent_target_group_digest_sha256"] == (
        q011cb.EXPECTED_PARENT_TARGET_GROUP_DIGEST
    )
    assert fixed["parent_aggregate_record_digest_sha256"] == (
        q011cb.EXPECTED_PARENT_AGGREGATE_RECORD_DIGEST
    )
    parent = fixed["parent_first_overlap_witness"]
    assert parent["target_identifier"] == "block=7;center=44"
    assert parent["wave_multiplicity"] == 629_841_280
    assert parent["intersection_interval"]["width_hex"] == (
        "0x1.2ce2f11752629p-31"
    )
    assert parent["witness_digest_sha256"] == q011cb.EXPECTED_PARENT_WITNESS_DIGEST
    assert fixed["refined_class_counts"] == [4, 2, 1, 2]
    assert fixed["selected_identifier_count"] == 18
    assert fixed["refined_class_membership_digest_sha256"] == (
        q011cb.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    assert fixed["selected_identifier_digest_sha256"] == (
        q011cb.EXPECTED_SELECTED_IDENTIFIER_DIGEST
    )
    assert fixed["selected_record_digest_sha256"] == (
        q011cb.EXPECTED_SELECTED_RECORD_DIGEST
    )
    assert fixed["target_record_digest_sha256"] == (
        q011cb.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert fixed["other_parent_targets_recomputed"] is False
    assert fixed["other_parent_overlap_signatures_recomputed"] is False
    assert fixed["aggregate_972_recomputed"] is False


def test_q011cb_processes_only_the_registered_parent_witness_family(
    q011cb_cycle: dict[str, Any],
) -> None:
    sweep = q011cb_cycle["targeted_blockwise_refinement_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 34
    assert sweep["parent_q011bx_aggregate_index"] == 2340
    assert sweep["audited_parent_witness_family_count"] == 1
    assert sweep["aggregate_records"][0]["target_identifier_count"] == 1
    assert sweep["original_monomial_count"] == 12_279_168_000
    assert sweep["modulus_signature_count"] == 44_800
    assert sweep["compatible_modulus_signature_count"] == 44_800
    assert sweep["compatible_original_monomial_count"] == 629_841_280
    assert sweep["weighted_comparison_count"] == 629_841_280
    assert sweep["distinct_comparison_count"] == 44_800
    assert sweep["class_power_record_count"] == 93
    assert sweep["group_signature_record_count"] == 579
    assert sweep["pair_pool_record_count"] == 2
    assert sweep["convolution_call_count"] == 7_885
    assert sweep["two_product_bound_array_bytes"] == 716_800
    assert sweep["parent_wave_multiplicity_is_exactly_partitioned"]


def test_q011cb_records_persistence_without_a_resonance_claim(
    q011cb_cycle: dict[str, Any],
) -> None:
    assert q011cb_cycle["study_validity"] == "passed"
    assert q011cb_cycle["failed_validity_order"] == []
    assert q011cb_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cb_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cb_cycle["diagnostic_gates"].values())
    assert q011cb_cycle["refinement_outcome"] == "persistent"
    assert q011cb_cycle["diagnostic_classification"] == (
        q011cb.PERSISTENT_CLASSIFICATION
    )
    assert q011cb_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cb_cycle["actual_resonance_outcome"] == "not_established"
    sweep = q011cb_cycle["targeted_blockwise_refinement_sweep"]
    assert sweep["fully_separated_parent_witness_family_count"] == 0
    assert sweep["remaining_overlap_parent_witness_family_count"] == 1
    assert sweep["separated_comparison_exists"] is False
    assert sweep["global_minimum_separated_witness"] is None
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 44_800,
    }
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 629_841_280,
    }


def test_q011cb_records_the_first_exact_persistent_witness(
    q011cb_cycle: dict[str, Any],
) -> None:
    witness = q011cb_cycle["targeted_blockwise_refinement_sweep"][
        "first_unresolved_witness"
    ]
    assert witness is not None
    assert witness["aggregate_index"] == 0
    assert witness["selected_type_counts"] == [13, 9, 5, 7]
    assert witness["target_identifier"] == "block=7;center=44"
    assert witness["output_block"] == 7
    assert witness["left_index"] == witness["right_index"] == 0
    assert witness["wave_multiplicity"] == 382
    assert witness["relation"] == "overlap"
    assert witness["block_zero_multiplicity"] == 0
    assert witness["class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [0, 7],
    ]
    assert Counter(witness["source_identifiers"]) == {
        "block=16;center=145": 13,
        "block=16;center=151": 9,
        "block=1;center=152": 5,
        "block=1;center=149": 7,
    }
    assert witness["intersection_interval"]["width_hex"] == (
        "0x1.9d49c4083b31ep-32"
    )
    assert witness["center_only_diagnostic"]["relation"] == (
        "target_below_product"
    )
    assert witness["center_only_diagnostic"]["gap_hex"] == (
        "0x1.3aa0404d55937p-28"
    )
    assert witness["witness_digest_sha256"] == (
        "de9435001e9603c4488945d9077e45abfa30e1c267271a27ae41d01b84993442"
    )


def test_q011cb_preserves_the_scientific_boundary(
    q011cb_cycle: dict[str, Any],
) -> None:
    theorem = q011cb_cycle["theorem_consequence"]
    assert not theorem[
        "second_q011bx_aggregate_first_overlap_is_resolved_by_registered_partition"
    ]
    assert theorem[
        "second_q011bx_aggregate_first_overlap_persists_under_registered_partition"
    ]
    assert not theorem["second_q011bx_aggregate_is_fully_audited"]
    assert not theorem["remaining_parent_coalesced_overlaps_are_audited"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "other 31 parent coalesced overlaps" in q011cb_cycle["claim_boundary"]
    assert "actual resonance" in q011cb_cycle["claim_boundary"]


def test_q011cb_cycle_has_strict_reproducible_digests(
    q011cb_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cb_cycle, allow_nan=False)
    assert {
        name: q011cb_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011cb_cycle["targeted_blockwise_refinement_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == (
        EXPECTED_SWEEP_DIGESTS
    )
    assert q011cb_cycle["result_digest_sha256"] == q011cb.q011b._canonical_json_sha256(
        q011cb._result_digest_sections(q011cb_cycle)
    )


def test_q011cb_study_metadata_and_optional_artifact_are_scoped(
    q011cb_study: dict[str, Any],
) -> None:
    assert q011cb_study["schema_version"] == 1
    assert q011cb_study["source"] == source_metadata()
    assert q011cb_study["study_gate"] == "passed"
    assert q011cb_study["refinement_outcome"] == "persistent"
    assert q011cb_study["scientific_outcome"] == "not_evaluated"
    assert q011cb_study["actual_resonance_outcome"] == "not_established"
    scope = q011cb_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["other_parent_coalesced_overlaps_audited"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cb_study, allow_nan=False)

    runner_path = Path(q011cb.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011cb_degree34_second_overlap_refinement.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011cb artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == runner_path.name
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        EXPECTED_SECTION_DIGESTS["result_digest_sha256"]
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
