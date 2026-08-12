from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bb_degree23_coalesced_sweep as q011bb
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011bb_study() -> dict[str, Any]:
    return q011bb.run_q011bb_study()


@pytest.fixture(scope="module")
def q011bb_cycle(q011bb_study: dict[str, Any]) -> dict[str, Any]:
    return q011bb_study["cycle"]


def test_q011bb_seals_q011ba_and_all_prior_inputs(q011bb_cycle: dict[str, Any]) -> None:
    sealed = q011bb_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 32
    assert sealed["direct_digest_count"] == 158
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ba"]["digests"]) == q011bb.Q011BA_DIGESTS
    assert sealed["q011ba"]["artifact_sha256"] == q011bb.Q011BA_ARTIFACT_SHA256
    assert sealed["q011ba"]["runner_sha256"] == q011bb.Q011BA_RUNNER_SHA256
    assert sealed["q011ba"]["degree_twenty_three_relation_evaluation_count"] == 0


def test_q011bb_reconstructs_registered_inputs_bitwise(q011bb_cycle: dict[str, Any]) -> None:
    fixed = q011bb_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 23
    assert fixed["degree_aggregate_count"] == 2_600
    assert fixed["old_modulus_separated_aggregate_count"] == 2_161
    assert fixed["direct_overlap_aggregate_count"] == 439
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 300
    assert fixed["active_identifier_count"] == 324
    assert fixed["monotone_identifier_count"] == 356
    assert fixed["inactive_retained_identifier_count"] == 32
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bb.q011ba.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bb.q011ba.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bb.q011ba.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bb.q011ba.EXPECTED_HULL_RECORD_DIGEST


def test_q011bb_processes_every_registered_aggregate_once(
    q011bb_cycle: dict[str, Any],
) -> None:
    sweep = q011bb_cycle["degree_twenty_three_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 23
    assert sweep["audited_overlap_aggregate_count"] == 439
    assert len(sweep["aggregate_records"]) == 439
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(439)
    )
    assert sweep["bound_matrix_record_count"] == 439
    assert sweep["fully_separated_overlap_aggregate_count"] <= 439


def test_q011bb_reproduces_preregistered_resource_identities(
    q011bb_cycle: dict[str, Any],
) -> None:
    sweep = q011bb_cycle["degree_twenty_three_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 124
    assert sweep["group_signature_record_count"] == 489
    assert sweep["pair_pool_record_count"] == 208
    assert sweep["convolution_call_count"] == 8_085
    assert sweep["original_monomial_count"] == 1_010_254_243_160
    assert sweep["modulus_signature_count"] == 16_792
    assert sweep["maximum_live_combined_signature_count"] == 144
    assert sweep["distinct_comparison_upper_bound"] == 252_396
    assert sweep["weighted_comparison_upper_bound"] == 18_941_796_258_208
    assert sweep["maximum_convolution_crude_int64_bound"] <= 317_708_751_360
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bb_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bb_validity_and_preregistered_stopping_rule(
    q011bb_cycle: dict[str, Any],
) -> None:
    assert q011bb_cycle["study_validity"] == "passed"
    assert q011bb_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bb_cycle["validity_gates"].values())
    assert q011bb_cycle["scientific_outcome"] in {"accepted", "rejected"}
    sweep = q011bb_cycle["degree_twenty_three_block_support_coalesced_sweep"]
    if q011bb_cycle["scientific_outcome"] == "accepted":
        assert q011bb_cycle["failed_hypothesis_order"] == []
        assert all(gate["passed"] for gate in q011bb_cycle["hypothesis_gates"].values())
        assert sweep["distinct_relation_counts"]["overlap"] == 0
        assert sweep["fully_separated_overlap_aggregate_count"] == 439
        assert q011bb_cycle["scientific_classification"] == q011bb.ACCEPTED_CLASSIFICATION
        assert q011bb_cycle["actual_resonance_outcome"] == (
            q011bb.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
    else:
        assert q011bb_cycle["failed_hypothesis_order"]
        assert sweep["distinct_relation_counts"]["overlap"] > 0
        assert q011bb_cycle["scientific_classification"] == q011bb.REJECTED_CLASSIFICATION
        assert q011bb_cycle["actual_resonance_outcome"] == "not_established"


def test_q011bb_preserves_the_scientific_boundary(q011bb_cycle: dict[str, Any]) -> None:
    theorem = q011bb_cycle["theorem_consequence"]
    accepted = q011bb_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_three_external_nonresonance_is_certified"] is accepted
    assert theorem[
        "an_actual_degree_twenty_three_external_resonance_is_ruled_out"
    ] is accepted
    assert theorem["registered_degree_twenty_three_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == (
        list(range(2, 24)) if accepted else list(range(2, 23))
    )
    assert theorem["missing_external_nonresonance_degrees"] == (
        list(range(24, 91)) if accepted else list(range(23, 91))
    )
    assert theorem["q011az_degree_twenty_two_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 24--90" in q011bb_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bb_cycle[
        "claim_boundary"
    ]


def test_q011bb_cycle_has_strict_reproducible_digests(q011bb_cycle: dict[str, Any]) -> None:
    json.dumps(q011bb_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011bb_cycle[name]) == 64
    assert q011bb_cycle["result_digest_sha256"] == q011bb.q011b._canonical_json_sha256(
        q011bb._result_digest_sections(q011bb_cycle)
    )


def test_q011bb_study_metadata_and_optional_artifact_are_scoped(
    q011bb_study: dict[str, Any],
) -> None:
    assert q011bb_study["schema_version"] == 1
    assert q011bb_study["source"] == source_metadata()
    assert q011bb_study["study_gate"] == "passed"
    assert q011bb_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011bb_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bb_study["mathematical_scope"]
    assert scope["degree"] == 23
    assert scope["degree_twenty_four_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bb_study, allow_nan=False)

    runner_path = Path(q011bb.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bb_degree23_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bb artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bb_degree23_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] in {"accepted", "rejected"}
    assert artifact["cycle"]["result_digest_sha256"] == q011bb.q011b._canonical_json_sha256(
        q011bb._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
