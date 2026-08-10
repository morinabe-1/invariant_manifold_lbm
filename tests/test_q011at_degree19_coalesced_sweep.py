from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011at_degree19_coalesced_sweep as q011at
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011at_study() -> dict[str, Any]:
    return q011at.run_q011at_study()


@pytest.fixture(scope="module")
def q011at_cycle(q011at_study: dict[str, Any]) -> dict[str, Any]:
    return q011at_study["cycle"]


def test_q011at_seals_q011as_and_all_prior_inputs(q011at_cycle: dict[str, Any]) -> None:
    sealed = q011at_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 24
    assert sealed["direct_digest_count"] == 122
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011as"]["digests"]) == q011at.Q011AS_DIGESTS
    assert sealed["q011as"]["artifact_sha256"] == q011at.Q011AS_ARTIFACT_SHA256
    assert sealed["q011as"]["runner_sha256"] == q011at.Q011AS_RUNNER_SHA256


def test_q011at_reconstructs_the_fixed_coalesced_inputs(q011at_cycle: dict[str, Any]) -> None:
    fixed = q011at_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 19
    assert fixed["degree_aggregate_count"] == 1_540
    assert fixed["old_modulus_separated_aggregate_count"] == 1_255
    assert fixed["direct_overlap_aggregate_count"] == 285
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 160
    assert fixed["final_identifier_count"] == 184
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["hull_record_digest_sha256"] == q011at.q011as.EXPECTED_HULL_RECORD_DIGEST
    assert fixed["merged_class_membership_digest_sha256"] == (
        q011at.q011as.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )


def test_q011at_full_sweep_reproduces_registered_resources(
    q011at_cycle: dict[str, Any],
) -> None:
    sweep = q011at_cycle["degree_nineteen_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 19
    assert sweep["audited_overlap_aggregate_count"] == 285
    assert len(sweep["aggregate_records"]) == 285
    assert sweep["original_monomial_count"] == 107_797_786_672
    assert sweep["modulus_signature_count"] == 8_056
    assert sweep["maximum_live_combined_signature_count"] == 90
    assert sweep["convolution_call_count"] == 3_877
    assert sweep["class_power_record_count"] == 102
    assert sweep["group_signature_record_count"] == 372
    assert sweep["pair_pool_record_count"] == 140
    assert sweep["distinct_comparison_upper_bound"] == 80_256
    assert sweep["weighted_comparison_upper_bound"] == 1_124_800_752_224
    assert sweep["distinct_comparison_count"] <= 80_256
    assert sweep["weighted_comparison_count"] <= 1_124_800_752_224
    assert sweep["bound_matrix_record_count"] == 285
    assert sweep["coefficient_matrix_record_count"] > 0
    assert sweep["classification_matrix_record_count"] > 0


def test_q011at_registered_outcome_logic_is_consistent(q011at_cycle: dict[str, Any]) -> None:
    assert q011at_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011at_cycle["validity_gates"].values())
    sweep = q011at_cycle["degree_nineteen_block_support_coalesced_sweep"]
    overlap = sweep["distinct_relation_counts"]["overlap"]
    if overlap == 0:
        assert q011at_cycle["scientific_outcome"] == "accepted"
        assert q011at_cycle["scientific_classification"] == q011at.ACCEPTED_CLASSIFICATION
        assert q011at_cycle["actual_resonance_outcome"] == (
            q011at.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
        assert all(gate["passed"] for gate in q011at_cycle["hypothesis_gates"].values())
    else:
        assert q011at_cycle["scientific_outcome"] == "rejected"
        assert q011at_cycle["scientific_classification"] == q011at.REJECTED_CLASSIFICATION
        assert q011at_cycle["actual_resonance_outcome"] == "not_established"
        assert sweep["first_unresolved_witness"] is not None


def test_q011at_witnesses_and_claim_boundary_are_scoped(q011at_cycle: dict[str, Any]) -> None:
    sweep = q011at_cycle["degree_nineteen_block_support_coalesced_sweep"]
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["relation"] in {"product_below_target", "target_below_product"}
    assert minimum["outward_gap_lower"]["float"] > 0
    assert q011at.q011z._fraction(minimum["exact_gap"]) > 0
    assert len(minimum["witness_digest_sha256"]) == 64
    theorem = q011at_cycle["theorem_consequence"]
    if q011at_cycle["scientific_outcome"] == "accepted":
        assert theorem["degree_nineteen_external_nonresonance_is_certified"]
        assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 20))
        assert theorem["missing_external_nonresonance_degrees"] == list(range(20, 91))
    else:
        assert not theorem["degree_nineteen_external_nonresonance_is_certified"]
        assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 19))
        assert theorem["missing_external_nonresonance_degrees"] == list(range(19, 91))
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 20--90" in q011at_cycle["claim_boundary"]


def test_q011at_cycle_has_strict_reproducible_digests(q011at_cycle: dict[str, Any]) -> None:
    json.dumps(q011at_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "preparation_digest_sha256",
        "sweep_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011at_cycle[name]) == 64
    assert q011at_cycle["result_digest_sha256"] == q011at.q011b._canonical_json_sha256(
        q011at._result_digest_sections(q011at_cycle)
    )


def test_q011at_study_metadata_and_optional_artifact_are_scoped(
    q011at_study: dict[str, Any],
) -> None:
    assert q011at_study["schema_version"] == 1
    assert q011at_study["source"] == source_metadata()
    assert q011at_study["study_gate"] == "passed"
    assert q011at_study["scientific_outcome"] in {"accepted", "rejected"}
    scope = q011at_study["mathematical_scope"]
    assert scope["degree"] == 19
    assert scope["degree_twenty_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011at_study, allow_nan=False)

    runner_path = Path(q011at.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011at_degree19_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011at artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011at_degree19_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["cycle"]["result_digest_sha256"] == q011at.q011b._canonical_json_sha256(
        q011at._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
