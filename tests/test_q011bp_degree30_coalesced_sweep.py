from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bp_degree30_coalesced_sweep as q011bp
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011bp_study() -> dict[str, Any]:
    return q011bp.run_q011bp_study()


@pytest.fixture(scope="module")
def q011bp_cycle(q011bp_study: dict[str, Any]) -> dict[str, Any]:
    return q011bp_study["cycle"]


def test_q011bp_seals_q011bo_and_all_prior_inputs(q011bp_cycle: dict[str, Any]) -> None:
    sealed = q011bp_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 46
    assert sealed["direct_digest_count"] == 221
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bo"]["digests"]) == q011bp.Q011BO_DIGESTS
    assert sealed["q011bo"]["artifact_sha256"] == q011bp.Q011BO_ARTIFACT_SHA256
    assert sealed["q011bo"]["runner_sha256"] == q011bp.Q011BO_RUNNER_SHA256
    assert sealed["q011bo"]["degree_thirty_relation_evaluation_count"] == 0


def test_q011bp_reconstructs_registered_inputs_bitwise(q011bp_cycle: dict[str, Any]) -> None:
    fixed = q011bp_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 30
    assert fixed["degree_aggregate_count"] == 5_456
    assert fixed["old_modulus_separated_aggregate_count"] == 3_781
    assert fixed["direct_overlap_aggregate_count"] == 1_675
    assert fixed["multi_target_aggregate_count"] == 2
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 772
    assert fixed["active_identifier_count"] == 796
    assert fixed["monotone_identifier_count"] == 912
    assert fixed["inactive_retained_identifier_count"] == 116
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bp.q011bo.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bp.q011bo.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bp.q011bo.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bp.q011bo.EXPECTED_HULL_RECORD_DIGEST


def test_q011bp_processes_every_registered_aggregate_once(
    q011bp_cycle: dict[str, Any],
) -> None:
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 30
    assert sweep["audited_overlap_aggregate_count"] == 1_675
    assert len(sweep["aggregate_records"]) == 1_675
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(1_675)
    )
    assert sweep["bound_matrix_record_count"] == 1_675
    assert sweep["fully_separated_overlap_aggregate_count"] <= 1_675


def test_q011bp_reproduces_preregistered_resource_identities(
    q011bp_cycle: dict[str, Any],
) -> None:
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 179
    assert sweep["group_signature_record_count"] == 989
    assert sweep["pair_pool_record_count"] == 536
    assert sweep["convolution_call_count"] == 24_223
    assert sweep["original_monomial_count"] == 199_600_479_347_738
    assert sweep["modulus_signature_count"] == 97_583
    assert sweep["maximum_live_combined_signature_count"] == 240
    assert sweep["distinct_comparison_upper_bound"] == 1_552_420
    assert sweep["weighted_comparison_upper_bound"] == 3_078_782_483_959_528
    assert sweep["maximum_convolution_crude_int64_bound"] <= 20_622_186_224_640
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bp_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 2
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bp_applies_the_preregistered_stopping_rule(
    q011bp_cycle: dict[str, Any],
) -> None:
    assert q011bp_cycle["study_validity"] == "passed"
    assert q011bp_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bp_cycle["validity_gates"].values())
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert sweep["distinct_comparison_count"] == sum(
        sweep["distinct_relation_counts"].values()
    )
    assert sweep["weighted_comparison_count"] == sum(
        sweep["weighted_relation_counts"].values()
    )
    separated = sweep["distinct_relation_counts"]["overlap"] == 0
    accepted = all(gate["passed"] for gate in q011bp_cycle["hypothesis_gates"].values())
    assert q011bp_cycle["scientific_outcome"] == (
        "accepted" if accepted else "rejected"
    )
    assert q011bp_cycle["hypothesis_gates"][
        "every_direct_comparison_is_strictly_separated"
    ]["passed"] is separated
    assert (sweep["first_unresolved_witness"] is None) is separated
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["relation"] != "overlap"
    assert minimum["outward_gap_lower"]["float"] > 0
    assert q011bp_cycle["scientific_classification"] == (
        q011bp.ACCEPTED_CLASSIFICATION if accepted else q011bp.REJECTED_CLASSIFICATION
    )
    assert q011bp_cycle["actual_resonance_outcome"] == (
        q011bp.ACCEPTED_ACTUAL_RESONANCE_OUTCOME if accepted else "not_established"
    )


def test_q011bp_preserves_the_scientific_boundary(q011bp_cycle: dict[str, Any]) -> None:
    theorem = q011bp_cycle["theorem_consequence"]
    accepted = q011bp_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_thirty_external_nonresonance_is_certified"] is accepted
    assert theorem["an_actual_degree_thirty_external_resonance_is_ruled_out"] is accepted
    assert theorem["registered_degree_thirty_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == list(
        range(2, 31) if accepted else range(2, 30)
    )
    assert theorem["missing_external_nonresonance_degrees"] == list(
        range(31, 91) if accepted else range(30, 91)
    )
    assert theorem["q011bn_degree_twenty_nine_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 31--90" in q011bp_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bp_cycle[
        "claim_boundary"
    ]


def test_q011bp_cycle_has_strict_reproducible_digests(q011bp_cycle: dict[str, Any]) -> None:
    json.dumps(q011bp_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011bp_cycle[name]) == 64
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    for name in (
        "aggregate_record_digest_sha256",
        "bound_matrix_digest_sha256",
        "coefficient_matrix_digest_sha256",
        "classification_matrix_digest_sha256",
    ):
        assert len(sweep[name]) == 64
    assert q011bp_cycle["result_digest_sha256"] == q011bp.q011b._canonical_json_sha256(
        q011bp._result_digest_sections(q011bp_cycle)
    )


def test_q011bp_study_metadata_and_optional_artifact_are_scoped(
    q011bp_study: dict[str, Any],
) -> None:
    assert q011bp_study["schema_version"] == 1
    assert q011bp_study["source"] == source_metadata()
    assert q011bp_study["study_gate"] == "passed"
    assert q011bp_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011bp_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bp_study["mathematical_scope"]
    assert scope["degree"] == 30
    assert scope["degree_thirty_one_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bp_study, allow_nan=False)

    runner_path = Path(q011bp.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bp_degree30_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bp artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bp_degree30_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bp_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bp_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bp.q011b._canonical_json_sha256(
        q011bp._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)
