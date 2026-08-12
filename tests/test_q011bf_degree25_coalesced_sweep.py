from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bf_degree25_coalesced_sweep as q011bf
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011bf_study() -> dict[str, Any]:
    return q011bf.run_q011bf_study()


@pytest.fixture(scope="module")
def q011bf_cycle(q011bf_study: dict[str, Any]) -> dict[str, Any]:
    return q011bf_study["cycle"]


def test_q011bf_seals_q011be_and_all_prior_inputs(q011bf_cycle: dict[str, Any]) -> None:
    sealed = q011bf_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 36
    assert sealed["direct_digest_count"] == 176
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011be"]["digests"]) == q011bf.Q011BE_DIGESTS
    assert sealed["q011be"]["artifact_sha256"] == q011bf.Q011BE_ARTIFACT_SHA256
    assert sealed["q011be"]["runner_sha256"] == q011bf.Q011BE_RUNNER_SHA256
    assert sealed["q011be"]["degree_twenty_five_relation_evaluation_count"] == 0


def test_q011bf_reconstructs_registered_inputs_bitwise(q011bf_cycle: dict[str, Any]) -> None:
    fixed = q011bf_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 25
    assert fixed["degree_aggregate_count"] == 3_276
    assert fixed["old_modulus_separated_aggregate_count"] == 2_634
    assert fixed["direct_overlap_aggregate_count"] == 642
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 388
    assert fixed["active_identifier_count"] == 412
    assert fixed["monotone_identifier_count"] == 484
    assert fixed["inactive_retained_identifier_count"] == 72
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bf.q011be.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bf.q011be.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bf.q011be.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bf.q011be.EXPECTED_HULL_RECORD_DIGEST


def test_q011bf_processes_every_registered_aggregate_once(
    q011bf_cycle: dict[str, Any],
) -> None:
    sweep = q011bf_cycle["degree_twenty_five_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 25
    assert sweep["audited_overlap_aggregate_count"] == 642
    assert len(sweep["aggregate_records"]) == 642
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(642)
    )
    assert sweep["bound_matrix_record_count"] == 642
    assert sweep["fully_separated_overlap_aggregate_count"] <= 642


def test_q011bf_reproduces_preregistered_resource_identities(
    q011bf_cycle: dict[str, Any],
) -> None:
    sweep = q011bf_cycle["degree_twenty_five_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 141
    assert sweep["group_signature_record_count"] == 605
    assert sweep["pair_pool_record_count"] == 257
    assert sweep["convolution_call_count"] == 7_913
    assert sweep["original_monomial_count"] == 5_101_735_096_404
    assert sweep["modulus_signature_count"] == 24_845
    assert sweep["maximum_live_combined_signature_count"] == 132
    assert sweep["distinct_comparison_upper_bound"] == 438_196
    assert sweep["weighted_comparison_upper_bound"] == 110_329_304_013_568
    assert sweep["maximum_convolution_crude_int64_bound"] <= 1_489_259_772_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bf_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bf_applies_the_preregistered_stopping_rule(
    q011bf_cycle: dict[str, Any],
) -> None:
    assert q011bf_cycle["study_validity"] == "passed"
    assert q011bf_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bf_cycle["validity_gates"].values())
    assert q011bf_cycle["scientific_outcome"] in {"accepted", "rejected"}
    sweep = q011bf_cycle["degree_twenty_five_block_support_coalesced_sweep"]
    assert sum(sweep["distinct_relation_counts"].values()) == sweep[
        "distinct_comparison_count"
    ]
    assert sum(sweep["weighted_relation_counts"].values()) == sweep[
        "weighted_comparison_count"
    ]
    assert sweep["distinct_comparison_count"] <= 438_196
    assert sweep["weighted_comparison_count"] <= 110_329_304_013_568
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum is not None
    assert len(minimum["witness_digest_sha256"]) == 64
    if q011bf_cycle["scientific_outcome"] == "accepted":
        assert q011bf_cycle["failed_hypothesis_order"] == []
        assert all(gate["passed"] for gate in q011bf_cycle["hypothesis_gates"].values())
        assert sweep["fully_separated_overlap_aggregate_count"] == 642
        assert sweep["distinct_relation_counts"]["overlap"] == 0
        assert sweep["weighted_relation_counts"]["overlap"] == 0
        assert sweep["first_unresolved_witness"] is None
        assert minimum["relation"] != "overlap"
        assert minimum["outward_gap_lower"]["float"] > 0
        assert q011bf.q011z._fraction(minimum["exact_gap"]) > 0
        assert q011bf_cycle["scientific_classification"] == q011bf.ACCEPTED_CLASSIFICATION
        assert (
            q011bf_cycle["actual_resonance_outcome"]
            == q011bf.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
    else:
        assert q011bf_cycle["failed_hypothesis_order"]
        assert not all(gate["passed"] for gate in q011bf_cycle["hypothesis_gates"].values())
        assert q011bf_cycle["scientific_classification"] == q011bf.REJECTED_CLASSIFICATION
        assert q011bf_cycle["actual_resonance_outcome"] == "not_established"


def test_q011bf_preserves_the_scientific_boundary(q011bf_cycle: dict[str, Any]) -> None:
    theorem = q011bf_cycle["theorem_consequence"]
    accepted = q011bf_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_five_external_nonresonance_is_certified"] is accepted
    assert theorem[
        "an_actual_degree_twenty_five_external_resonance_is_ruled_out"
    ] is accepted
    assert theorem["registered_degree_twenty_five_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == (
        list(range(2, 26)) if accepted else list(range(2, 25))
    )
    assert theorem["missing_external_nonresonance_degrees"] == (
        list(range(26, 91)) if accepted else list(range(25, 91))
    )
    assert theorem["q011bd_degree_twenty_four_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 26--90" in q011bf_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bf_cycle[
        "claim_boundary"
    ]


def test_q011bf_cycle_has_strict_reproducible_digests(q011bf_cycle: dict[str, Any]) -> None:
    json.dumps(q011bf_cycle, allow_nan=False)
    digest_names = (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    )
    assert all(len(q011bf_cycle[name]) == 64 for name in digest_names)
    sweep = q011bf_cycle["degree_twenty_five_block_support_coalesced_sweep"]
    sweep_digest_names = (
        "aggregate_record_digest_sha256",
        "bound_matrix_digest_sha256",
        "coefficient_matrix_digest_sha256",
        "classification_matrix_digest_sha256",
    )
    assert all(len(sweep[name]) == 64 for name in sweep_digest_names)
    assert q011bf_cycle["result_digest_sha256"] == q011bf.q011b._canonical_json_sha256(
        q011bf._result_digest_sections(q011bf_cycle)
    )


def test_q011bf_study_metadata_and_optional_artifact_are_scoped(
    q011bf_study: dict[str, Any],
) -> None:
    assert q011bf_study["schema_version"] == 1
    assert q011bf_study["source"] == source_metadata()
    assert q011bf_study["study_gate"] == "passed"
    assert q011bf_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011bf_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bf_study["mathematical_scope"]
    assert scope["degree"] == 25
    assert scope["degree_twenty_six_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bf_study, allow_nan=False)

    runner_path = Path(q011bf.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bf_degree25_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bf artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bf_degree25_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bf_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bf_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bf.q011b._canonical_json_sha256(
        q011bf._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)
