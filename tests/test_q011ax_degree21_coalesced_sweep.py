from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ax_degree21_coalesced_sweep as q011ax
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ax_study() -> dict[str, Any]:
    return q011ax.run_q011ax_study()


@pytest.fixture(scope="module")
def q011ax_cycle(q011ax_study: dict[str, Any]) -> dict[str, Any]:
    return q011ax_study["cycle"]


def test_q011ax_seals_q011aw_and_all_prior_inputs(q011ax_cycle: dict[str, Any]) -> None:
    sealed = q011ax_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 28
    assert sealed["direct_digest_count"] == 140
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011aw"]["digests"]) == q011ax.Q011AW_DIGESTS
    assert sealed["q011aw"]["artifact_sha256"] == q011ax.Q011AW_ARTIFACT_SHA256
    assert sealed["q011aw"]["runner_sha256"] == q011ax.Q011AW_RUNNER_SHA256
    assert sealed["q011aw"]["degree_twenty_one_relation_evaluation_count"] == 0


def test_q011ax_reconstructs_registered_inputs_bitwise(q011ax_cycle: dict[str, Any]) -> None:
    fixed = q011ax_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 21
    assert fixed["degree_aggregate_count"] == 2_024
    assert fixed["old_modulus_separated_aggregate_count"] == 1_660
    assert fixed["direct_overlap_aggregate_count"] == 364
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 228
    assert fixed["final_identifier_count"] == 252
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011ax.q011aw.EXPECTED_INVENTORY_DIGEST
    assert fixed["final_disc_record_digest_sha256"] == (
        q011ax.q011aw.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011ax.q011aw.EXPECTED_HULL_RECORD_DIGEST
    assert fixed["merged_class_membership_digest_sha256"] == (
        q011ax.q011aw.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )


def test_q011ax_processes_every_registered_aggregate_once(
    q011ax_cycle: dict[str, Any],
) -> None:
    sweep = q011ax_cycle["degree_twenty_one_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 21
    assert sweep["audited_overlap_aggregate_count"] == 364
    assert len(sweep["aggregate_records"]) == 364
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(364)
    )
    assert sweep["bound_matrix_record_count"] == 364
    assert sweep["fully_separated_overlap_aggregate_count"] <= 364


def test_q011ax_reproduces_preregistered_resource_identities(
    q011ax_cycle: dict[str, Any],
) -> None:
    sweep = q011ax_cycle["degree_twenty_one_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 121
    assert sweep["group_signature_record_count"] == 482
    assert sweep["pair_pool_record_count"] == 192
    assert sweep["convolution_call_count"] == 6_448
    assert sweep["original_monomial_count"] == 294_674_427_372
    assert sweep["modulus_signature_count"] == 12_458
    assert sweep["maximum_live_combined_signature_count"] == 126
    assert sweep["distinct_comparison_upper_bound"] == 146_928
    assert sweep["weighted_comparison_upper_bound"] == 3_951_865_509_552
    assert sweep["maximum_convolution_crude_int64_bound"] <= 133_491_072_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011ax_cycle["registered_parameters"]
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011ax_validity_and_preregistered_stopping_rule(
    q011ax_cycle: dict[str, Any],
) -> None:
    assert q011ax_cycle["study_validity"] == "passed"
    assert q011ax_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011ax_cycle["validity_gates"].values())
    assert q011ax_cycle["scientific_outcome"] in {"accepted", "rejected"}
    sweep = q011ax_cycle["degree_twenty_one_block_support_coalesced_sweep"]
    if q011ax_cycle["scientific_outcome"] == "accepted":
        assert q011ax_cycle["failed_hypothesis_order"] == []
        assert all(gate["passed"] for gate in q011ax_cycle["hypothesis_gates"].values())
        assert sweep["distinct_relation_counts"]["overlap"] == 0
        assert sweep["fully_separated_overlap_aggregate_count"] == 364
        assert q011ax_cycle["scientific_classification"] == q011ax.ACCEPTED_CLASSIFICATION
        assert q011ax_cycle["actual_resonance_outcome"] == (
            q011ax.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
    else:
        assert q011ax_cycle["failed_hypothesis_order"]
        assert sweep["distinct_relation_counts"]["overlap"] > 0
        assert q011ax_cycle["scientific_classification"] == q011ax.REJECTED_CLASSIFICATION
        assert q011ax_cycle["actual_resonance_outcome"] == "not_established"


def test_q011ax_preserves_the_scientific_boundary(q011ax_cycle: dict[str, Any]) -> None:
    theorem = q011ax_cycle["theorem_consequence"]
    accepted = q011ax_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_one_external_nonresonance_is_certified"] is accepted
    assert theorem[
        "an_actual_degree_twenty_one_external_resonance_is_ruled_out"
    ] is accepted
    assert theorem["registered_degree_twenty_one_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == (
        list(range(2, 22)) if accepted else list(range(2, 21))
    )
    assert theorem["missing_external_nonresonance_degrees"] == (
        list(range(22, 91)) if accepted else list(range(21, 91))
    )
    assert theorem["q011av_degree_twenty_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 22--90" in q011ax_cycle["claim_boundary"]


def test_q011ax_cycle_has_strict_reproducible_digests(q011ax_cycle: dict[str, Any]) -> None:
    json.dumps(q011ax_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011ax_cycle[name]) == 64
    assert q011ax_cycle["result_digest_sha256"] == q011ax.q011b._canonical_json_sha256(
        q011ax._result_digest_sections(q011ax_cycle)
    )


def test_q011ax_study_metadata_and_optional_artifact_are_scoped(
    q011ax_study: dict[str, Any],
) -> None:
    assert q011ax_study["schema_version"] == 1
    assert q011ax_study["source"] == source_metadata()
    assert q011ax_study["study_gate"] == "passed"
    assert q011ax_study["scientific_outcome"] in {"accepted", "rejected"}
    scope = q011ax_study["mathematical_scope"]
    assert scope["degree"] == 21
    assert scope["degree_twenty_two_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ax_study, allow_nan=False)

    runner_path = Path(q011ax.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ax_degree21_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011ax artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011ax_degree21_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] in {"accepted", "rejected"}
    assert artifact["cycle"]["result_digest_sha256"] == q011ax.q011b._canonical_json_sha256(
        q011ax._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
