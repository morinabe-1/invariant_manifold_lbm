from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bq_degree31_resource_estimate as q011bq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011bq_study() -> dict[str, Any]:
    return q011bq.run_q011bq_study()


@pytest.fixture(scope="module")
def q011bq_cycle(q011bq_study: dict[str, Any]) -> dict[str, Any]:
    return q011bq_study["cycle"]


def test_q011bq_seals_q011bp_and_all_prior_inputs(q011bq_cycle: dict[str, Any]) -> None:
    sealed = q011bq_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 47
    assert sealed["direct_digest_count"] == 225
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bp"]["digests"]) == q011bq.Q011BP_DIGESTS
    assert sealed["q011bp"]["artifact_sha256"] == q011bq.Q011BP_ARTIFACT_SHA256
    assert sealed["q011bp"]["runner_sha256"] == q011bq.Q011BP_RUNNER_SHA256


def test_q011bq_reconstructs_the_exact_degree_thirty_one_inventory(
    q011bq_cycle: dict[str, Any],
) -> None:
    inventory = q011bq_cycle["degree_thirty_one_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 31
    assert inventory["degree_aggregate_count"] == 5_984
    assert inventory["degree_expanded_product_control_count"] == 376_992
    assert inventory["old_modulus_separated_aggregate_count"] == 3_995
    assert inventory["old_modulus_overlap_aggregate_count"] == 1_989
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 66
    assert inventory["unique_external_target_count"] == 892
    assert inventory["multi_target_external_component_aggregate_count"] == 8
    assert inventory["maximum_external_component_count"] == 3
    assert inventory["target_identifier_block_counts"] == list(
        q011bq.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 0, 1, 30]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [28, 2, 1, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bq.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bq.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bq.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bq.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bq.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bq_preserves_a_monotone_disc_inventory(q011bq_cycle: dict[str, Any]) -> None:
    envelope = q011bq_cycle["degree_thirty_one_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 892
    assert envelope["prior_q011bo_identifier_count"] == 912
    assert envelope["active_reused_q011bo_identifier_count"] == 796
    assert envelope["inactive_retained_q011bo_identifier_count"] == 116
    assert envelope["added_target_identifier_count"] == 120
    assert envelope["removed_q011bo_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 916
    assert envelope["final_monotone_identifier_count"] == 1_032
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bq.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bq.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bq.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bq.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bq.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bq.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bq.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bq.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bq.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bq_reproduces_the_design_only_resource_contract(
    q011bq_cycle: dict[str, Any],
) -> None:
    resource = q011bq_cycle["degree_thirty_one_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 186
    assert resource["group_pool_cache_key_count"] == 123
    assert resource["group_signature_record_count"] == 1_084
    assert resource["pair_pool_cache_key_count"] == 626
    assert resource["cached_pair_signature_entry_count"] == 29_300
    assert resource["exact_convolution_call_count"] == 31_408
    assert resource["modulus_signature_count"] == 121_932
    assert resource["peak_live_combined_signature_count"] == 272
    assert resource["peak_two_product_bound_array_bytes"] == 4_352
    assert resource["original_monomial_count"] == 364_024_527_216_492
    assert resource["maximum_aggregate_monomial_count"] == 1_985_023_272_960
    assert resource["safe_int64_convolution_crude_upper_bound"] == 33_745_395_640_320
    assert resource["distinct_comparison_upper_bound"] == 1_869_852
    assert resource["weighted_comparison_upper_bound"] == 5_248_950_250_612_032
    assert resource["class_power_key_digest_sha256"] == q011bq.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bq.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bq.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bq.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_thirty_one_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bq_all_unchanged_resource_limits_pass(q011bq_cycle: dict[str, Any]) -> None:
    assert q011bq_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bq_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bq_cycle["resource_feasibility_gates"].values())
    assert q011bq_cycle["failed_validity_order"] == []
    assert q011bq_cycle["failed_resource_limit_order"] == []
    assert q011bq_cycle["resource_decision"] == q011bq.GO_DECISION
    assert q011bq_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bq_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bq_preserves_the_scientific_boundary(q011bq_cycle: dict[str, Any]) -> None:
    theorem = q011bq_cycle["theorem_consequence"]
    assert theorem[
        "degree_thirty_one_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_thirty_one_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_one_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 31))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(31, 91))
    assert theorem["q011bp_degree_thirty_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-thirty-one product-target relation" in q011bq_cycle[
        "claim_boundary"
    ]


def test_q011bq_cycle_has_strict_reproducible_digests(q011bq_cycle: dict[str, Any]) -> None:
    json.dumps(q011bq_cycle, allow_nan=False)
    digest_names = (
        "input_digest_sha256",
        "inventory_digest_sha256",
        "envelope_digest_sha256",
        "resource_digest_sha256",
        "result_digest_sha256",
    )
    assert all(len(q011bq_cycle[name]) == 64 for name in digest_names)
    assert q011bq_cycle["result_digest_sha256"] == q011bq.q011b._canonical_json_sha256(
        q011bq._result_digest_sections(q011bq_cycle)
    )


def test_q011bq_study_metadata_and_optional_artifact_are_scoped(
    q011bq_study: dict[str, Any],
) -> None:
    assert q011bq_study["schema_version"] == 1
    assert q011bq_study["source"] == source_metadata()
    assert q011bq_study["study_gate"] == "passed"
    assert q011bq_study["resource_decision"] == q011bq.GO_DECISION
    assert q011bq_study["scientific_outcome"] == "not_evaluated"
    scope = q011bq_study["mathematical_scope"]
    assert scope["degree"] == 31
    assert scope["degree_thirty_one_external_nonresonance_claim"] is False
    assert scope["actual_degree_thirty_one_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bq_study, allow_nan=False)

    runner_path = Path(q011bq.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bq_degree31_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bq artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bq_degree31_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bq.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bq.q011b._canonical_json_sha256(
        q011bq._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)
