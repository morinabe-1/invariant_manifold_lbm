from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011av_degree20_coalesced_sweep as q011av
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011av_study() -> dict[str, Any]:
    return q011av.run_q011av_study()


@pytest.fixture(scope="module")
def q011av_cycle(q011av_study: dict[str, Any]) -> dict[str, Any]:
    return q011av_study["cycle"]


def test_q011av_seals_q011au_and_all_prior_inputs(q011av_cycle: dict[str, Any]) -> None:
    sealed = q011av_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 26
    assert sealed["direct_digest_count"] == 131
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011au"]["digests"]) == q011av.Q011AU_DIGESTS
    assert sealed["q011au"]["artifact_sha256"] == q011av.Q011AU_ARTIFACT_SHA256
    assert sealed["q011au"]["runner_sha256"] == q011av.Q011AU_RUNNER_SHA256
    assert sealed["q011au"]["degree_twenty_relation_evaluation_count"] == 0


def test_q011av_reconstructs_the_fixed_coalesced_inputs(q011av_cycle: dict[str, Any]) -> None:
    fixed = q011av_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 20
    assert fixed["degree_aggregate_count"] == 1_771
    assert fixed["old_modulus_separated_aggregate_count"] == 1_450
    assert fixed["direct_overlap_aggregate_count"] == 321
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 220
    assert fixed["final_identifier_count"] == 244
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011av.q011au.EXPECTED_INVENTORY_DIGEST
    assert fixed["final_disc_record_digest_sha256"] == (
        q011av.q011au.EXPECTED_FINAL_RECORD_DIGEST
    )


def test_q011av_full_sweep_reproduces_registered_resources(
    q011av_cycle: dict[str, Any],
) -> None:
    sweep = q011av_cycle["degree_twenty_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 20
    assert sweep["audited_overlap_aggregate_count"] == 321
    assert len(sweep["aggregate_records"]) == 321
    assert sweep["original_monomial_count"] == 184_398_553_391
    assert sweep["modulus_signature_count"] == 10_287
    assert sweep["maximum_live_combined_signature_count"] == 110
    assert sweep["convolution_call_count"] == 5_211
    assert sweep["class_power_record_count"] == 111
    assert sweep["group_signature_record_count"] == 400
    assert sweep["pair_pool_record_count"] == 172
    assert sweep["distinct_comparison_upper_bound"] == 109_992
    assert sweep["weighted_comparison_upper_bound"] == 2_182_943_190_492
    assert sweep["distinct_comparison_count"] <= 109_992
    assert sweep["weighted_comparison_count"] <= 2_182_943_190_492
    assert sweep["bound_matrix_record_count"] == 321
    assert sweep["coefficient_matrix_record_count"] > 0
    assert sweep["classification_matrix_record_count"] > 0


def test_q011av_registered_outcome_logic_is_consistent(q011av_cycle: dict[str, Any]) -> None:
    assert q011av_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011av_cycle["validity_gates"].values())
    sweep = q011av_cycle["degree_twenty_block_support_coalesced_sweep"]
    overlap = sweep["distinct_relation_counts"]["overlap"]
    if overlap == 0:
        assert q011av_cycle["scientific_outcome"] == "accepted"
        assert q011av_cycle["scientific_classification"] == q011av.ACCEPTED_CLASSIFICATION
        assert q011av_cycle["actual_resonance_outcome"] == (
            q011av.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
        assert all(gate["passed"] for gate in q011av_cycle["hypothesis_gates"].values())
    else:
        assert q011av_cycle["scientific_outcome"] == "rejected"
        assert q011av_cycle["scientific_classification"] == q011av.REJECTED_CLASSIFICATION
        assert q011av_cycle["actual_resonance_outcome"] == "not_established"
        assert sweep["first_unresolved_witness"] is not None


def test_q011av_witnesses_and_claim_boundary_are_scoped(q011av_cycle: dict[str, Any]) -> None:
    sweep = q011av_cycle["degree_twenty_block_support_coalesced_sweep"]
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["relation"] in {"product_below_target", "target_below_product"}
    assert minimum["outward_gap_lower"]["float"] > 0
    assert q011av.q011z._fraction(minimum["exact_gap"]) > 0
    assert len(minimum["witness_digest_sha256"]) == 64
    theorem = q011av_cycle["theorem_consequence"]
    if q011av_cycle["scientific_outcome"] == "accepted":
        assert theorem["degree_twenty_external_nonresonance_is_certified"]
        assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 21))
        assert theorem["missing_external_nonresonance_degrees"] == list(range(21, 91))
    else:
        assert not theorem["degree_twenty_external_nonresonance_is_certified"]
        assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 20))
        assert theorem["missing_external_nonresonance_degrees"] == list(range(20, 91))
    assert theorem["q011at_degree_nineteen_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 21--90" in q011av_cycle["claim_boundary"]


def test_q011av_cycle_has_strict_reproducible_digests(q011av_cycle: dict[str, Any]) -> None:
    json.dumps(q011av_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011av_cycle[name]) == 64
    assert q011av_cycle["result_digest_sha256"] == q011av.q011b._canonical_json_sha256(
        q011av._result_digest_sections(q011av_cycle)
    )


def test_q011av_study_metadata_and_optional_artifact_are_scoped(
    q011av_study: dict[str, Any],
) -> None:
    assert q011av_study["schema_version"] == 1
    assert q011av_study["source"] == source_metadata()
    assert q011av_study["study_gate"] == "passed"
    assert q011av_study["scientific_outcome"] in {"accepted", "rejected"}
    scope = q011av_study["mathematical_scope"]
    assert scope["degree"] == 20
    assert scope["degree_twenty_one_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011av_study, allow_nan=False)

    runner_path = Path(q011av.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011av_degree20_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011av artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011av_degree20_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["cycle"]["result_digest_sha256"] == q011av.q011b._canonical_json_sha256(
        q011av._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
