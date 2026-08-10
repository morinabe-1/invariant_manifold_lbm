from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011as_block_support_resource_redesign as q011as
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011as_study() -> dict[str, Any]:
    return q011as.run_q011as_study()


@pytest.fixture(scope="module")
def q011as_cycle(q011as_study: dict[str, Any]) -> dict[str, Any]:
    return q011as_study["cycle"]


def test_q011as_seals_q011ar_and_all_prior_inputs(q011as_cycle: dict[str, Any]) -> None:
    sealed = q011as_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 23
    assert sealed["direct_digest_count"] == 117
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ar"]["digests"]) == q011as.Q011AR_DIGESTS
    assert sealed["q011ar"]["artifact_sha256"] == q011as.Q011AR_ARTIFACT_SHA256
    assert sealed["q011ar"]["runner_sha256"] == q011as.Q011AR_RUNNER_SHA256


def test_q011as_builds_the_registered_block_support_hulls(
    q011as_cycle: dict[str, Any],
) -> None:
    audit = q011as_cycle["degree_nineteen_coalescing_input_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree"] == 19
    assert audit["degree_aggregate_count"] == 1_540
    assert audit["old_modulus_separated_aggregate_count"] == 1_255
    assert audit["direct_overlap_aggregate_count"] == 285
    assert audit["target_identifier_count"] == 160
    assert not audit["target_lookup_changed"]
    assert audit["product_target_relation_evaluation_count"] == 0
    hull = audit["block_support_hull_coalescing_audit"]
    assert hull["passed"]
    assert all(hull["checks"].values())
    assert hull["old_class_counts"] == [4, 2, 3, 6]
    assert hull["merged_class_counts"] == [1, 1, 2, 2]
    assert hull["selected_identifier_count"] == 24
    assert hull["merged_class_record_count"] == 6
    assert hull["hull_record_digest_sha256"] == q011as.EXPECTED_HULL_RECORD_DIGEST
    assert hull["merged_class_membership_digest_sha256"] == (
        q011as.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert hull["maximum_width_inflation_ratio"] == pytest.approx(1.195361864035176)


def test_q011as_preserves_the_known_degree_eighteen_certificate(
    q011as_cycle: dict[str, Any],
) -> None:
    regression = q011as_cycle["degree_eighteen_coalesced_regression_audit"]
    assert regression["passed"]
    assert all(regression["checks"].values())
    sweep = regression["direct_regression_sweep"]
    assert sweep["degree"] == 18
    assert sweep["audited_overlap_aggregate_count"] == 252
    assert sweep["fully_separated_overlap_aggregate_count"] == 252
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["first_unresolved_witness"] is None
    assert sweep["original_monomial_count"] == 50_931_347_136
    assert sweep["modulus_signature_count"] == 6_075
    assert sweep["compatible_modulus_signature_count"] == 5_624
    assert sweep["compatible_original_monomial_count"] == 12_958_923_958
    assert sweep["weighted_comparison_count"] == 29_855_319_268
    assert sweep["distinct_comparison_count"] == 43_852
    assert sweep["weighted_relation_counts"] == q011as.EXPECTED_D18_WEIGHTED_RELATIONS
    assert sweep["distinct_relation_counts"] == q011as.EXPECTED_D18_DISTINCT_RELATIONS
    assert sweep["maximum_live_combined_signature_count"] == 84
    assert sweep["convolution_call_count"] == 3_001
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["outward_gap_lower"]["binary64_hex"] == (
        q011as.EXPECTED_D18_MINIMUM_OUTWARD_HEX
    )
    assert minimum["exact_gap_hex"] == q011as.EXPECTED_D18_MINIMUM_EXACT_HEX
    assert minimum["witness_digest_sha256"] == q011as.EXPECTED_D18_MINIMUM_WITNESS_DIGEST


def test_q011as_reproduces_the_degree_nineteen_resource_contract(
    q011as_cycle: dict[str, Any],
) -> None:
    resource = q011as_cycle["degree_nineteen_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 102
    assert resource["group_pool_cache_key_count"] == 66
    assert resource["group_signature_record_count"] == 372
    assert resource["pair_pool_cache_key_count"] == 140
    assert resource["cached_pair_signature_entry_count"] == 3_163
    assert resource["exact_convolution_call_count"] == 3_877
    assert resource["modulus_signature_count"] == 8_056
    assert resource["peak_live_combined_signature_count"] == 90
    assert resource["peak_two_product_bound_array_bytes"] == 1_440
    assert resource["original_monomial_count"] == 107_797_786_672
    assert resource["maximum_aggregate_monomial_count"] == 2_038_608_000
    assert resource["safe_int64_convolution_crude_upper_bound"] == 34_656_336_000
    assert resource["distinct_comparison_upper_bound"] == 80_256
    assert resource["weighted_comparison_upper_bound"] == 1_124_800_752_224
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011as.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert not resource["full_degree_nineteen_monomial_list_retained"]
    assert not resource["product_bound_matrix_constructed"]
    assert not resource["fourier_coefficient_matrix_constructed"]
    assert not resource["classification_matrix_constructed"]
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011as_all_unchanged_resource_limits_pass(q011as_cycle: dict[str, Any]) -> None:
    resource = q011as_cycle["degree_nineteen_coalesced_resource_audit"]
    projection = resource["calibrated_projection"]
    assert projection["wall_time_double_safety_upper_seconds"]["float"] == pytest.approx(
        0.07437891084327201
    )
    assert projection["process_memory_one_point_five_safety_upper_bytes"] == 183_970
    assert not projection["projection_is_a_scientific_acceptance_threshold"]
    assert q011as.RESOURCE_LIMITS == q011as.q011ap.RESOURCE_LIMITS
    assert all(gate["passed"] for gate in q011as_cycle["resource_feasibility_gates"].values())
    assert q011as_cycle["failed_resource_limit_order"] == []
    assert q011as_cycle["resource_decision"] == q011as.GO_DECISION


def test_q011as_preserves_the_scientific_boundary(q011as_cycle: dict[str, Any]) -> None:
    assert q011as_cycle["study_validity"] == "passed"
    assert q011as_cycle["scientific_outcome"] == "not_evaluated"
    assert q011as_cycle["actual_resonance_outcome"] == "not_evaluated"
    assert all(gate["passed"] for gate in q011as_cycle["validity_gates"].values())
    theorem = q011as_cycle["theorem_consequence"]
    assert theorem["block_support_hull_coalescing_is_resource_supported_for_preregistration"]
    assert theorem["known_degree_eighteen_certificate_is_preserved_by_regression"]
    assert not theorem["degree_nineteen_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_nineteen_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 19))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(19, 91))
    assert "evaluates no degree-nineteen" in q011as_cycle["claim_boundary"]
    assert "Q011at" in q011as_cycle["next_change"]


def test_q011as_cycle_has_strict_reproducible_digests(
    q011as_cycle: dict[str, Any],
) -> None:
    json.dumps(q011as_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "coalescing_digest_sha256",
        "regression_digest_sha256",
        "resource_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011as_cycle[name]) == 64
    assert q011as_cycle["result_digest_sha256"] == q011as.q011b._canonical_json_sha256(
        q011as._result_digest_sections(q011as_cycle)
    )


def test_q011as_study_metadata_and_optional_artifact_are_scoped(
    q011as_study: dict[str, Any],
) -> None:
    assert q011as_study["schema_version"] == 1
    assert q011as_study["source"] == source_metadata()
    assert q011as_study["study_gate"] == "passed"
    assert q011as_study["resource_decision"] == q011as.GO_DECISION
    assert q011as_study["scientific_outcome"] == "not_evaluated"
    assert q011as_study["actual_resonance_outcome"] == "not_evaluated"
    scope = q011as_study["mathematical_scope"]
    assert scope["design_degree"] == 19
    assert scope["known_regression_degree"] == 18
    assert scope["degree_nineteen_external_nonresonance_claim"] is False
    assert scope["degrees_19_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    assert q011as_study["arithmetic_runtime"][
        "degree_nineteen_relation_classification"
    ] == "not evaluated"
    json.dumps(q011as_study, allow_nan=False)

    runner_path = Path(q011as.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011as_block_support_resource_redesign.json"
    if not artifact_path.exists():
        pytest.skip("Q011as artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011as_block_support_resource_redesign.py"
    )
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011as.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011as.q011b._canonical_json_sha256(
        q011as._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
