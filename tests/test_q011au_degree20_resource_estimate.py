from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011au_degree20_resource_estimate as q011au
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "0d393a9a04ac034f4e714b6dee2b71d817cdb3605feeaebdad65bfcbe7098032"
EXPECTED_ARTIFACT_SHA256 = "029229b9e02584ac2000e50aab8a7ac36a19e16099effb97223c04f79d44327a"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "1da477970508fec8465b8982c2465a837ae686cce262f5ee3aedbd431bdc75e6",
    "inventory_digest_sha256": (
        "3ff79ea56b49a1d16886582c7d661edbfed49474fee6300c51133b9af7b2f47b"
    ),
    "envelope_digest_sha256": (
        "64ead411e78c0993380f7ab3d05772adc4b8658d2e905a4fce3cc744dc6c87c7"
    ),
    "resource_digest_sha256": (
        "eaf79c72235430d1996f4318b2815929f57267ae8f3867da1bc2f06a9a0c473e"
    ),
    "result_digest_sha256": "bac8c480dd06fe03971aad75f6866210b13c109fe2ef6aece4cc86fecfe04c7b",
}


@pytest.fixture(scope="module")
def q011au_study() -> dict[str, Any]:
    return q011au.run_q011au_study()


@pytest.fixture(scope="module")
def q011au_cycle(q011au_study: dict[str, Any]) -> dict[str, Any]:
    return q011au_study["cycle"]


def test_q011au_seals_q011at_and_all_prior_inputs(q011au_cycle: dict[str, Any]) -> None:
    sealed = q011au_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 25
    assert sealed["direct_digest_count"] == 126
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011at"]["digests"]) == q011au.Q011AT_DIGESTS
    assert sealed["q011at"]["artifact_sha256"] == q011au.Q011AT_ARTIFACT_SHA256
    assert sealed["q011at"]["runner_sha256"] == q011au.Q011AT_RUNNER_SHA256


def test_q011au_reconstructs_the_exact_degree_twenty_inventory(
    q011au_cycle: dict[str, Any],
) -> None:
    inventory = q011au_cycle["degree_twenty_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 20
    assert inventory["degree_aggregate_count"] == 1_771
    assert inventory["degree_expanded_product_control_count"] == 53_130
    assert inventory["old_modulus_separated_aggregate_count"] == 1_450
    assert inventory["old_modulus_overlap_aggregate_count"] == 321
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 19
    assert inventory["unique_external_target_count"] == 220
    assert inventory["multi_target_external_component_aggregate_count"] == 8
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 1, 14, 5]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [20, 0, 0, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == q011au.EXPECTED_COUNT_TUPLE_DIGEST
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011au.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == q011au.EXPECTED_OVERLAP_RECORD_DIGEST
    assert inventory["external_target_record_digest_sha256"] == (
        q011au.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011au.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011au_preserves_prior_discs_and_source_hulls(q011au_cycle: dict[str, Any]) -> None:
    envelope = q011au_cycle["degree_twenty_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 220
    assert envelope["prior_q011ar_identifier_count"] == 184
    assert envelope["reused_q011ar_identifier_count"] == 184
    assert envelope["added_target_identifier_count"] == 60
    assert envelope["removed_q011ar_identifier_count"] == 0
    assert envelope["final_identifier_count"] == 244
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011au.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011au.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011au.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["final_disc_record_digest_sha256"] == q011au.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011au.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011au.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011au_reproduces_the_design_only_resource_contract(
    q011au_cycle: dict[str, Any],
) -> None:
    resource = q011au_cycle["degree_twenty_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 111
    assert resource["group_pool_cache_key_count"] == 74
    assert resource["group_signature_record_count"] == 400
    assert resource["pair_pool_cache_key_count"] == 172
    assert resource["cached_pair_signature_entry_count"] == 4_448
    assert resource["exact_convolution_call_count"] == 5_211
    assert resource["modulus_signature_count"] == 10_287
    assert resource["peak_live_combined_signature_count"] == 110
    assert resource["peak_two_product_bound_array_bytes"] == 1_760
    assert resource["original_monomial_count"] == 184_398_553_391
    assert resource["maximum_aggregate_monomial_count"] == 4_122_518_400
    assert resource["safe_int64_convolution_crude_upper_bound"] == 70_082_812_800
    assert resource["distinct_comparison_upper_bound"] == 109_992
    assert resource["weighted_comparison_upper_bound"] == 2_182_943_190_492
    assert resource["class_power_key_digest_sha256"] == q011au.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011au.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011au.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011au.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011au_all_unchanged_resource_limits_pass(q011au_cycle: dict[str, Any]) -> None:
    assert q011au_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011au_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011au_cycle["resource_feasibility_gates"].values())
    assert q011au_cycle["failed_validity_order"] == []
    assert q011au_cycle["failed_resource_limit_order"] == []
    assert q011au_cycle["resource_decision"] == q011au.GO_DECISION
    assert q011au_cycle["scientific_outcome"] == "not_evaluated"
    assert q011au_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011au_preserves_the_scientific_boundary(q011au_cycle: dict[str, Any]) -> None:
    theorem = q011au_cycle["theorem_consequence"]
    assert theorem["degree_twenty_coalesced_full_sweep_preregistration_is_resource_supported"]
    assert not theorem["degree_twenty_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 20))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(20, 91))
    assert theorem["q011at_degree_nineteen_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty product-target relation" in q011au_cycle["claim_boundary"]


def test_q011au_cycle_has_strict_reproducible_digests(q011au_cycle: dict[str, Any]) -> None:
    json.dumps(q011au_cycle, allow_nan=False)
    for name, digest in EXPECTED_SECTION_DIGESTS.items():
        assert q011au_cycle[name] == digest
    assert q011au_cycle["result_digest_sha256"] == q011au.q011b._canonical_json_sha256(
        q011au._result_digest_sections(q011au_cycle)
    )


def test_q011au_study_metadata_and_optional_artifact_are_scoped(
    q011au_study: dict[str, Any],
) -> None:
    assert q011au_study["schema_version"] == 1
    assert q011au_study["source"] == source_metadata()
    assert q011au_study["study_gate"] == "passed"
    assert q011au_study["resource_decision"] == q011au.GO_DECISION
    assert q011au_study["scientific_outcome"] == "not_evaluated"
    scope = q011au_study["mathematical_scope"]
    assert scope["degree"] == 20
    assert scope["degree_twenty_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011au_study, allow_nan=False)

    runner_path = Path(q011au.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011au_degree20_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011au artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011au_degree20_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011au.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011au.q011b._canonical_json_sha256(
        q011au._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
