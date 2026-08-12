from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ba_degree23_resource_estimate as q011ba
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ba_study() -> dict[str, Any]:
    return q011ba.run_q011ba_study()


@pytest.fixture(scope="module")
def q011ba_cycle(q011ba_study: dict[str, Any]) -> dict[str, Any]:
    return q011ba_study["cycle"]


def test_q011ba_seals_q011az_and_all_prior_inputs(q011ba_cycle: dict[str, Any]) -> None:
    sealed = q011ba_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 31
    assert sealed["direct_digest_count"] == 153
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011az"]["digests"]) == q011ba.Q011AZ_DIGESTS
    assert sealed["q011az"]["artifact_sha256"] == q011ba.Q011AZ_ARTIFACT_SHA256
    assert sealed["q011az"]["runner_sha256"] == q011ba.Q011AZ_RUNNER_SHA256


def test_q011ba_reconstructs_the_exact_degree_twenty_three_inventory(
    q011ba_cycle: dict[str, Any],
) -> None:
    inventory = q011ba_cycle["degree_twenty_three_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 23
    assert inventory["degree_aggregate_count"] == 2_600
    assert inventory["degree_expanded_product_control_count"] == 98_280
    assert inventory["old_modulus_separated_aggregate_count"] == 2_161
    assert inventory["old_modulus_overlap_aggregate_count"] == 439
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 26
    assert inventory["unique_external_target_count"] == 300
    assert inventory["multi_target_external_component_aggregate_count"] == 14
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["target_identifier_block_counts"] == list(
        q011ba.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 1, 16, 6]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [23, 0, 0, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == q011ba.EXPECTED_COUNT_TUPLE_DIGEST
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011ba.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == q011ba.EXPECTED_OVERLAP_RECORD_DIGEST
    assert inventory["external_target_record_digest_sha256"] == (
        q011ba.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011ba.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011ba_preserves_a_monotone_disc_inventory(q011ba_cycle: dict[str, Any]) -> None:
    envelope = q011ba_cycle["degree_twenty_three_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 300
    assert envelope["prior_q011ay_identifier_count"] == 308
    assert envelope["active_reused_q011ay_identifier_count"] == 276
    assert envelope["inactive_retained_q011ay_identifier_count"] == 32
    assert envelope["added_target_identifier_count"] == 48
    assert envelope["removed_q011ay_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 324
    assert envelope["final_monotone_identifier_count"] == 356
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011ba.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011ba.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011ba.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011ba.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011ba.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011ba.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011ba.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011ba.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011ba.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011ba_reproduces_the_design_only_resource_contract(
    q011ba_cycle: dict[str, Any],
) -> None:
    resource = q011ba_cycle["degree_twenty_three_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 124
    assert resource["group_pool_cache_key_count"] == 83
    assert resource["group_signature_record_count"] == 489
    assert resource["pair_pool_cache_key_count"] == 208
    assert resource["cached_pair_signature_entry_count"] == 7_149
    assert resource["exact_convolution_call_count"] == 8_085
    assert resource["modulus_signature_count"] == 16_792
    assert resource["peak_live_combined_signature_count"] == 144
    assert resource["peak_two_product_bound_array_bytes"] == 2_304
    assert resource["original_monomial_count"] == 1_010_254_243_160
    assert resource["maximum_aggregate_monomial_count"] == 18_688_750_080
    assert resource["safe_int64_convolution_crude_upper_bound"] == 317_708_751_360
    assert resource["distinct_comparison_upper_bound"] == 252_396
    assert resource["weighted_comparison_upper_bound"] == 18_941_796_258_208
    assert resource["class_power_key_digest_sha256"] == q011ba.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011ba.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011ba.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011ba.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_three_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011ba_all_unchanged_resource_limits_pass(q011ba_cycle: dict[str, Any]) -> None:
    assert q011ba_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011ba_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ba_cycle["resource_feasibility_gates"].values())
    assert q011ba_cycle["failed_validity_order"] == []
    assert q011ba_cycle["failed_resource_limit_order"] == []
    assert q011ba_cycle["resource_decision"] == q011ba.GO_DECISION
    assert q011ba_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ba_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011ba_preserves_the_scientific_boundary(q011ba_cycle: dict[str, Any]) -> None:
    theorem = q011ba_cycle["theorem_consequence"]
    assert theorem[
        "degree_twenty_three_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_twenty_three_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_three_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 23))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(23, 91))
    assert theorem["q011az_degree_twenty_two_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty-three product-target relation" in q011ba_cycle[
        "claim_boundary"
    ]


def test_q011ba_cycle_has_strict_reproducible_digests(q011ba_cycle: dict[str, Any]) -> None:
    json.dumps(q011ba_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "inventory_digest_sha256",
        "envelope_digest_sha256",
        "resource_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011ba_cycle[name]) == 64
    assert q011ba_cycle["result_digest_sha256"] == q011ba.q011b._canonical_json_sha256(
        q011ba._result_digest_sections(q011ba_cycle)
    )


def test_q011ba_study_metadata_and_optional_artifact_are_scoped(
    q011ba_study: dict[str, Any],
) -> None:
    assert q011ba_study["schema_version"] == 1
    assert q011ba_study["source"] == source_metadata()
    assert q011ba_study["study_gate"] == "passed"
    assert q011ba_study["resource_decision"] == q011ba.GO_DECISION
    assert q011ba_study["scientific_outcome"] == "not_evaluated"
    scope = q011ba_study["mathematical_scope"]
    assert scope["degree"] == 23
    assert scope["degree_twenty_three_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_three_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011ba_study, allow_nan=False)

    runner_path = Path(q011ba.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ba_degree23_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011ba artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011ba_degree23_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011ba.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011ba.q011b._canonical_json_sha256(
        q011ba._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
