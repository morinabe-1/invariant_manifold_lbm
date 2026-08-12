from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bj_degree27_coalesced_sweep as q011bj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011bj_study() -> dict[str, Any]:
    return q011bj.run_q011bj_study()


@pytest.fixture(scope="module")
def q011bj_cycle(q011bj_study: dict[str, Any]) -> dict[str, Any]:
    return q011bj_study["cycle"]


def test_q011bj_seals_q011bi_and_all_prior_inputs(q011bj_cycle: dict[str, Any]) -> None:
    sealed = q011bj_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 40
    assert sealed["direct_digest_count"] == 194
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bi"]["digests"]) == q011bj.Q011BI_DIGESTS
    assert sealed["q011bi"]["artifact_sha256"] == q011bj.Q011BI_ARTIFACT_SHA256
    assert sealed["q011bi"]["runner_sha256"] == q011bj.Q011BI_RUNNER_SHA256
    assert sealed["q011bi"]["degree_twenty_seven_relation_evaluation_count"] == 0


def test_q011bj_reconstructs_registered_inputs_bitwise(q011bj_cycle: dict[str, Any]) -> None:
    fixed = q011bj_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 27
    assert fixed["degree_aggregate_count"] == 4_060
    assert fixed["old_modulus_separated_aggregate_count"] == 3_101
    assert fixed["direct_overlap_aggregate_count"] == 959
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 488
    assert fixed["active_identifier_count"] == 512
    assert fixed["monotone_identifier_count"] == 604
    assert fixed["inactive_retained_identifier_count"] == 92
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bj.q011bi.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bj.q011bi.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bj.q011bi.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bj.q011bi.EXPECTED_HULL_RECORD_DIGEST


def test_q011bj_processes_every_registered_aggregate_once(
    q011bj_cycle: dict[str, Any],
) -> None:
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 27
    assert sweep["audited_overlap_aggregate_count"] == 959
    assert len(sweep["aggregate_records"]) == 959
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(959)
    )
    assert sweep["bound_matrix_record_count"] == 959
    assert sweep["fully_separated_overlap_aggregate_count"] <= 959


def test_q011bj_reproduces_preregistered_resource_identities(
    q011bj_cycle: dict[str, Any],
) -> None:
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 154
    assert sweep["group_signature_record_count"] == 705
    assert sweep["pair_pool_record_count"] == 341
    assert sweep["convolution_call_count"] == 11_649
    assert sweep["original_monomial_count"] == 25_561_324_661_692
    assert sweep["modulus_signature_count"] == 43_285
    assert sweep["maximum_live_combined_signature_count"] == 180
    assert sweep["distinct_comparison_upper_bound"] == 763_404
    assert sweep["weighted_comparison_upper_bound"] == 502_998_748_050_560
    assert sweep["maximum_convolution_crude_int64_bound"] <= 4_633_252_624_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bj_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bj_applies_the_preregistered_stopping_rule(
    q011bj_cycle: dict[str, Any],
) -> None:
    assert q011bj_cycle["study_validity"] == "passed"
    assert q011bj_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bj_cycle["validity_gates"].values())
    assert q011bj_cycle["scientific_outcome"] in {"accepted", "rejected"}
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert sweep["distinct_comparison_count"] == sum(
        sweep["distinct_relation_counts"].values()
    )
    assert sweep["weighted_comparison_count"] == sum(
        sweep["weighted_relation_counts"].values()
    )
    assert sweep["distinct_comparison_count"] <= sweep["distinct_comparison_upper_bound"]
    assert sweep["weighted_comparison_count"] <= sweep["weighted_comparison_upper_bound"]
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum is not None
    assert len(minimum["witness_digest_sha256"]) == 64
    if q011bj_cycle["scientific_outcome"] == "accepted":
        assert q011bj_cycle["failed_hypothesis_order"] == []
        assert all(gate["passed"] for gate in q011bj_cycle["hypothesis_gates"].values())
        assert sweep["fully_separated_overlap_aggregate_count"] == 959
        assert sweep["distinct_relation_counts"]["overlap"] == 0
        assert sweep["weighted_relation_counts"]["overlap"] == 0
        assert sweep["first_unresolved_witness"] is None
        assert minimum["relation"] != "overlap"
        assert minimum["outward_gap_lower"]["float"] > 0
        assert q011bj_cycle["scientific_classification"] == q011bj.ACCEPTED_CLASSIFICATION
        assert (
            q011bj_cycle["actual_resonance_outcome"]
            == q011bj.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
    else:
        assert q011bj_cycle["failed_hypothesis_order"]
        assert not all(gate["passed"] for gate in q011bj_cycle["hypothesis_gates"].values())
        assert q011bj_cycle["scientific_classification"] == q011bj.REJECTED_CLASSIFICATION
        assert q011bj_cycle["actual_resonance_outcome"] == "not_established"


def test_q011bj_preserves_the_scientific_boundary(q011bj_cycle: dict[str, Any]) -> None:
    theorem = q011bj_cycle["theorem_consequence"]
    accepted = q011bj_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_seven_external_nonresonance_is_certified"] is accepted
    assert theorem["an_actual_degree_twenty_seven_external_resonance_is_ruled_out"] is accepted
    assert theorem["registered_degree_twenty_seven_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == list(
        range(2, 28 if accepted else 27)
    )
    assert theorem["missing_external_nonresonance_degrees"] == list(
        range(28 if accepted else 27, 91)
    )
    assert theorem["q011bh_degree_twenty_six_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 28--90" in q011bj_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bj_cycle[
        "claim_boundary"
    ]


def test_q011bj_cycle_has_strict_reproducible_digests(q011bj_cycle: dict[str, Any]) -> None:
    json.dumps(q011bj_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011bj_cycle[name]) == 64
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    for name in (
        "aggregate_record_digest_sha256",
        "bound_matrix_digest_sha256",
        "coefficient_matrix_digest_sha256",
        "classification_matrix_digest_sha256",
    ):
        assert len(sweep[name]) == 64
    assert q011bj_cycle["result_digest_sha256"] == q011bj.q011b._canonical_json_sha256(
        q011bj._result_digest_sections(q011bj_cycle)
    )


def test_q011bj_study_metadata_and_optional_artifact_are_scoped(
    q011bj_study: dict[str, Any],
) -> None:
    assert q011bj_study["schema_version"] == 1
    assert q011bj_study["source"] == source_metadata()
    assert q011bj_study["study_gate"] == "passed"
    assert q011bj_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011bj_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bj_study["mathematical_scope"]
    assert scope["degree"] == 27
    assert scope["degree_twenty_eight_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bj_study, allow_nan=False)

    runner_path = Path(q011bj.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bj_degree27_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bj_degree27_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bj_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bj_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bj.q011b._canonical_json_sha256(
        q011bj._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)
