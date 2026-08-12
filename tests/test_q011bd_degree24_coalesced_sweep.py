from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bd_degree24_coalesced_sweep as q011bd
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011bd_study() -> dict[str, Any]:
    return q011bd.run_q011bd_study()


@pytest.fixture(scope="module")
def q011bd_cycle(q011bd_study: dict[str, Any]) -> dict[str, Any]:
    return q011bd_study["cycle"]


def test_q011bd_seals_q011bc_and_all_prior_inputs(q011bd_cycle: dict[str, Any]) -> None:
    sealed = q011bd_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 34
    assert sealed["direct_digest_count"] == 167
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bc"]["digests"]) == q011bd.Q011BC_DIGESTS
    assert sealed["q011bc"]["artifact_sha256"] == q011bd.Q011BC_ARTIFACT_SHA256
    assert sealed["q011bc"]["runner_sha256"] == q011bd.Q011BC_RUNNER_SHA256
    assert sealed["q011bc"]["degree_twenty_four_relation_evaluation_count"] == 0


def test_q011bd_reconstructs_registered_inputs_bitwise(q011bd_cycle: dict[str, Any]) -> None:
    fixed = q011bd_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 24
    assert fixed["degree_aggregate_count"] == 2_925
    assert fixed["old_modulus_separated_aggregate_count"] == 2_401
    assert fixed["direct_overlap_aggregate_count"] == 524
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 372
    assert fixed["active_identifier_count"] == 396
    assert fixed["monotone_identifier_count"] == 444
    assert fixed["inactive_retained_identifier_count"] == 48
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bd.q011bc.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bd.q011bc.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bd.q011bc.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bd.q011bc.EXPECTED_HULL_RECORD_DIGEST


def test_q011bd_processes_every_registered_aggregate_once(
    q011bd_cycle: dict[str, Any],
) -> None:
    sweep = q011bd_cycle["degree_twenty_four_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 24
    assert sweep["audited_overlap_aggregate_count"] == 524
    assert len(sweep["aggregate_records"]) == 524
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(524)
    )
    assert sweep["bound_matrix_record_count"] == 524
    assert sweep["fully_separated_overlap_aggregate_count"] <= 524


def test_q011bd_reproduces_preregistered_resource_identities(
    q011bd_cycle: dict[str, Any],
) -> None:
    sweep = q011bd_cycle["degree_twenty_four_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 135
    assert sweep["group_signature_record_count"] == 580
    assert sweep["pair_pool_record_count"] == 230
    assert sweep["convolution_call_count"] == 8_054
    assert sweep["original_monomial_count"] == 2_246_535_043_109
    assert sweep["modulus_signature_count"] == 19_942
    assert sweep["maximum_live_combined_signature_count"] == 153
    assert sweep["distinct_comparison_upper_bound"] == 331_524
    assert sweep["weighted_comparison_upper_bound"] == 46_505_597_729_848
    assert sweep["maximum_convolution_crude_int64_bound"] <= 654_106_252_800
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bd_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bd_validity_and_preregistered_stopping_rule(
    q011bd_cycle: dict[str, Any],
) -> None:
    assert q011bd_cycle["study_validity"] == "passed"
    assert q011bd_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bd_cycle["validity_gates"].values())
    sweep = q011bd_cycle["degree_twenty_four_block_support_coalesced_sweep"]
    accepted = q011bd_cycle["scientific_outcome"] == "accepted"
    assert q011bd_cycle["scientific_outcome"] in {"accepted", "rejected"}
    assert (q011bd_cycle["failed_hypothesis_order"] == []) is accepted
    assert all(gate["passed"] for gate in q011bd_cycle["hypothesis_gates"].values()) is accepted
    assert (sweep["fully_separated_overlap_aggregate_count"] == 524) is accepted
    assert sum(sweep["distinct_relation_counts"].values()) == sweep[
        "distinct_comparison_count"
    ]
    assert sum(sweep["weighted_relation_counts"].values()) == sweep[
        "weighted_comparison_count"
    ]
    assert (sweep["distinct_relation_counts"]["overlap"] == 0) is accepted
    assert (sweep["first_unresolved_witness"] is None) is accepted
    for name in (
        "aggregate_record_digest_sha256",
        "bound_matrix_digest_sha256",
        "coefficient_matrix_digest_sha256",
        "classification_matrix_digest_sha256",
    ):
        assert len(sweep[name]) == 64
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["relation"] in {"product_below_target", "target_below_product"}
    assert minimum["outward_gap_lower"]["float"] > 0
    assert len(minimum["witness_digest_sha256"]) == 64
    assert q011bd_cycle["scientific_classification"] == (
        q011bd.ACCEPTED_CLASSIFICATION if accepted else q011bd.REJECTED_CLASSIFICATION
    )
    assert q011bd_cycle["actual_resonance_outcome"] == (
        q011bd.ACCEPTED_ACTUAL_RESONANCE_OUTCOME if accepted else "not_established"
    )


def test_q011bd_preserves_the_scientific_boundary(q011bd_cycle: dict[str, Any]) -> None:
    theorem = q011bd_cycle["theorem_consequence"]
    accepted = q011bd_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_four_external_nonresonance_is_certified"] is accepted
    assert theorem[
        "an_actual_degree_twenty_four_external_resonance_is_ruled_out"
    ] is accepted
    assert theorem["registered_degree_twenty_four_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == (
        list(range(2, 25)) if accepted else list(range(2, 24))
    )
    assert theorem["missing_external_nonresonance_degrees"] == (
        list(range(25, 91)) if accepted else list(range(24, 91))
    )
    assert theorem["q011bb_degree_twenty_three_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 25--90" in q011bd_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bd_cycle[
        "claim_boundary"
    ]


def test_q011bd_cycle_has_strict_reproducible_digests(q011bd_cycle: dict[str, Any]) -> None:
    json.dumps(q011bd_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011bd_cycle[name]) == 64
    assert q011bd_cycle["result_digest_sha256"] == q011bd.q011b._canonical_json_sha256(
        q011bd._result_digest_sections(q011bd_cycle)
    )


def test_q011bd_study_metadata_and_optional_artifact_are_scoped(
    q011bd_study: dict[str, Any],
) -> None:
    assert q011bd_study["schema_version"] == 1
    assert q011bd_study["source"] == source_metadata()
    assert q011bd_study["study_gate"] == "passed"
    assert q011bd_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011bd_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bd_study["mathematical_scope"]
    assert scope["degree"] == 24
    assert scope["degree_twenty_five_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bd_study, allow_nan=False)

    runner_path = Path(q011bd.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bd_degree24_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bd artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bd_degree24_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bd_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bd_study["actual_resonance_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == q011bd.q011b._canonical_json_sha256(
        q011bd._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)
