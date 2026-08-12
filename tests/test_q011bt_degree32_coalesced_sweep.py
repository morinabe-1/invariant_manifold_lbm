from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bt_degree32_coalesced_sweep as q011bt
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a19c79c4e36b6114567c2c7c3db26c20372b5114dd5e932e1f48252433b8f7a5"
EXPECTED_ARTIFACT_SHA256 = "d48b4f965586299462df4fb3cc0361c7bd6b47b18533f6980f234c26b3ff65fb"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "a253dd46a214fbf54600c6faca342b64064742f38c42bec0c2aeb34c9d28a180",
    "preparation_digest_sha256": (
        "aafa61683eeab80e96cb0dfcba1b0ea57355f14da501fdb8242e2a10f09e1642"
    ),
    "sweep_digest_sha256": "f5388a8f724fde95698ee993c0454c44f1e23004cdb5d122a84707c053aa5c81",
    "result_digest_sha256": "abc989675e3509881b312415c402a3efd958b098bedaa440c520c16275fb2c67",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "5ef25f31f6160bbf4c305c72ad8d0c5e8344a2edef0ea56ae36b5da59a9c64a3"
    ),
    "bound_matrix_digest_sha256": (
        "3597de22ba5e3f6244f47e7e82fedf7df2aa77bc0e7cc21a4852fef7b13c1b81"
    ),
    "coefficient_matrix_digest_sha256": (
        "fa8e137b5a19ecb081892aa3180632748c29bde8170f36b0ba6237b004e318da"
    ),
    "classification_matrix_digest_sha256": (
        "2819db9c82b12db30dd22d4768f3feaec92888b33948c52aa900f45b7987734b"
    ),
}


@pytest.fixture(scope="module")
def q011bt_study() -> dict[str, Any]:
    return q011bt.run_q011bt_study()


@pytest.fixture(scope="module")
def q011bt_cycle(q011bt_study: dict[str, Any]) -> dict[str, Any]:
    return q011bt_study["cycle"]


def test_q011bt_seals_q011bs_and_all_prior_inputs(q011bt_cycle: dict[str, Any]) -> None:
    sealed = q011bt_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 50
    assert sealed["direct_digest_count"] == 239
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bs"]["digests"]) == q011bt.Q011BS_DIGESTS
    assert sealed["q011bs"]["artifact_sha256"] == q011bt.Q011BS_ARTIFACT_SHA256
    assert sealed["q011bs"]["runner_sha256"] == q011bt.Q011BS_RUNNER_SHA256
    assert sealed["q011bs"]["degree_thirty_two_relation_evaluation_count"] == 0


def test_q011bt_reconstructs_registered_inputs_bitwise(q011bt_cycle: dict[str, Any]) -> None:
    fixed = q011bt_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 32
    assert fixed["degree_aggregate_count"] == 6_545
    assert fixed["old_modulus_separated_aggregate_count"] == 4_238
    assert fixed["direct_overlap_aggregate_count"] == 2_307
    assert fixed["multi_target_aggregate_count"] == 13
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 1_024
    assert fixed["active_identifier_count"] == 1_048
    assert fixed["monotone_identifier_count"] == 1_188
    assert fixed["inactive_retained_identifier_count"] == 140
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bt.q011bs.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bt.q011bs.EXPECTED_ACTIVE_RECORD_DIGEST
    )

    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bt.q011bs.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bt.q011bs.EXPECTED_HULL_RECORD_DIGEST


def test_q011bt_processes_every_registered_aggregate_once(
    q011bt_cycle: dict[str, Any],
) -> None:
    sweep = q011bt_cycle["degree_thirty_two_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 32
    assert sweep["audited_overlap_aggregate_count"] == 2_307
    assert len(sweep["aggregate_records"]) == 2_307
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(2_307)
    )
    assert sweep["bound_matrix_record_count"] == 2_307
    assert sweep["fully_separated_overlap_aggregate_count"] <= 2_307


def test_q011bt_reproduces_preregistered_resource_identities(
    q011bt_cycle: dict[str, Any],
) -> None:
    sweep = q011bt_cycle["degree_thirty_two_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 186
    assert sweep["group_signature_record_count"] == 996
    assert sweep["pair_pool_record_count"] == 691
    assert sweep["convolution_call_count"] == 32_675
    assert sweep["original_monomial_count"] == 652_055_297_357_287
    assert sweep["modulus_signature_count"] == 147_064
    assert sweep["maximum_live_combined_signature_count"] == 240
    assert sweep["distinct_comparison_upper_bound"] == 2_197_696
    assert sweep["weighted_comparison_upper_bound"] == 9_099_502_713_798_428
    assert sweep["maximum_convolution_crude_int64_bound"] <= 52_242_871_769_088
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bt_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 13
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bt_applies_the_preregistered_stopping_rule(
    q011bt_cycle: dict[str, Any],
) -> None:
    assert q011bt_cycle["study_validity"] == "passed"
    assert q011bt_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bt_cycle["validity_gates"].values())
    assert q011bt_cycle["scientific_outcome"] == "accepted"
    assert q011bt_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bt_cycle["hypothesis_gates"].values())
    sweep = q011bt_cycle["degree_thirty_two_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 2_307
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["distinct_comparison_count"] == 2_123_656
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 936_268,
        "target_below_product": 1_187_388,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 532_138_097_562_518
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 298_056_268_376_626,
        "target_below_product": 234_081_829_185_892,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 1_796
    assert minimum["selected_type_counts"] == [13, 11, 5, 3]
    assert minimum["target_identifier"] == "block=10;center=44"
    assert minimum["relation"] == "product_below_target"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.23a2d2bffffffp-23"
    assert minimum["exact_gap_hex"] == "0x1.23a2d48c417bbp-23"
    assert minimum["witness_digest_sha256"] == (
        "28ec4e98b8e8714b4cf99ce11e398d9f0c13e8aa8e6421b21f5a3abc24d12c9a"
    )
    assert q011bt_cycle["scientific_classification"] == q011bt.ACCEPTED_CLASSIFICATION
    assert q011bt_cycle["actual_resonance_outcome"] == q011bt.ACCEPTED_ACTUAL_RESONANCE_OUTCOME


def test_q011bt_preserves_the_scientific_boundary(q011bt_cycle: dict[str, Any]) -> None:
    theorem = q011bt_cycle["theorem_consequence"]
    assert theorem["degree_thirty_two_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_thirty_two_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_thirty_two_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 33))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(33, 91))
    assert theorem["q011br_degree_thirty_one_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 33--90" in q011bt_cycle["claim_boundary"]
    assert (
        "inactive monotone proof records are retained but not compared"
        in q011bt_cycle["claim_boundary"]
    )


def test_q011bt_cycle_has_strict_reproducible_digests(q011bt_cycle: dict[str, Any]) -> None:
    json.dumps(q011bt_cycle, allow_nan=False)
    assert {
        name: q011bt_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bt_cycle["degree_thirty_two_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bt_cycle["result_digest_sha256"] == q011bt.q011b._canonical_json_sha256(
        q011bt._result_digest_sections(q011bt_cycle)
    )


def test_q011bt_study_metadata_and_optional_artifact_are_scoped(
    q011bt_study: dict[str, Any],
) -> None:
    assert q011bt_study["schema_version"] == 1
    assert q011bt_study["source"] == source_metadata()
    assert q011bt_study["study_gate"] == "passed"
    assert q011bt_study["scientific_outcome"] == "accepted"
    assert q011bt_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bt_study["mathematical_scope"]
    assert scope["degree"] == 32
    assert scope["degree_thirty_three_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bt_study, allow_nan=False)

    runner_path = Path(q011bt.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bt_degree32_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bt artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bt_degree32_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bt_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bt_study["actual_resonance_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == q011bt.q011b._canonical_json_sha256(
        q011bt._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
