from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011be_degree25_resource_estimate as q011be
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "f6b35e6f6f845db31a7adcbb57e21a4407daf6d4eaa004584d124c78a32ce7a8"
EXPECTED_ARTIFACT_SHA256 = "3a0910b5868c9f3c9a92f58833db4b7a856a9b789d8716b6aee09794efeb6825"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "078ad563285bbad781c69be860085c1634ecd1cf6dbb145fe20781b59e593aa9",
    "inventory_digest_sha256": (
        "86fe9208f4a39dfe34ad5a1282c1d95005bfffd20758782f993214c14a334cc2"
    ),
    "envelope_digest_sha256": (
        "485bcbaa0959347ff205d28a00ef616ab2e252a5d150bce88f8f0fc0669d5b60"
    ),
    "resource_digest_sha256": (
        "1876303981d327c34c00b0eb4259d1e3ced76ac65923303d83c5d8498cbc8108"
    ),
    "result_digest_sha256": "ac89b7d19b54f5489f342a8f3ef4240a2680362272b2d5e7f71cf874e38ee6c0",
}


@pytest.fixture(scope="module")
def q011be_study() -> dict[str, Any]:
    return q011be.run_q011be_study()


@pytest.fixture(scope="module")
def q011be_cycle(q011be_study: dict[str, Any]) -> dict[str, Any]:
    return q011be_study["cycle"]


def test_q011be_seals_q011bd_and_all_prior_inputs(q011be_cycle: dict[str, Any]) -> None:
    sealed = q011be_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 35
    assert sealed["direct_digest_count"] == 171
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bd"]["digests"]) == q011be.Q011BD_DIGESTS
    assert sealed["q011bd"]["artifact_sha256"] == q011be.Q011BD_ARTIFACT_SHA256
    assert sealed["q011bd"]["runner_sha256"] == q011be.Q011BD_RUNNER_SHA256


def test_q011be_reconstructs_the_exact_degree_twenty_five_inventory(
    q011be_cycle: dict[str, Any],
) -> None:
    inventory = q011be_cycle["degree_twenty_five_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 25
    assert inventory["degree_aggregate_count"] == 3_276
    assert inventory["degree_expanded_product_control_count"] == 142_506
    assert inventory["old_modulus_separated_aggregate_count"] == 2_634
    assert inventory["old_modulus_overlap_aggregate_count"] == 642
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 31
    assert inventory["unique_external_target_count"] == 388
    assert inventory["multi_target_external_component_aggregate_count"] == 5
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["target_identifier_block_counts"] == list(
        q011be.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 6, 4, 15]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [23, 1, 1, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011be.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011be.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011be.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011be.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011be.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011be_preserves_a_monotone_disc_inventory(q011be_cycle: dict[str, Any]) -> None:
    envelope = q011be_cycle["degree_twenty_five_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 388
    assert envelope["prior_q011bc_identifier_count"] == 444
    assert envelope["active_reused_q011bc_identifier_count"] == 372
    assert envelope["inactive_retained_q011bc_identifier_count"] == 72
    assert envelope["added_target_identifier_count"] == 40
    assert envelope["removed_q011bc_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 412
    assert envelope["final_monotone_identifier_count"] == 484
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011be.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011be.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011be.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011be.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011be.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011be.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011be.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011be.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011be.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011be_reproduces_the_design_only_resource_contract(
    q011be_cycle: dict[str, Any],
) -> None:
    resource = q011be_cycle["degree_twenty_five_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 141
    assert resource["group_pool_cache_key_count"] == 95
    assert resource["group_signature_record_count"] == 605
    assert resource["pair_pool_cache_key_count"] == 257
    assert resource["cached_pair_signature_entry_count"] == 6_752
    assert resource["exact_convolution_call_count"] == 7_913
    assert resource["modulus_signature_count"] == 24_845
    assert resource["peak_live_combined_signature_count"] == 132
    assert resource["peak_two_product_bound_array_bytes"] == 2_112
    assert resource["original_monomial_count"] == 5_101_735_096_404
    assert resource["maximum_aggregate_monomial_count"] == 87_603_516_000
    assert resource["safe_int64_convolution_crude_upper_bound"] == 1_489_259_772_000
    assert resource["distinct_comparison_upper_bound"] == 438_196
    assert resource["weighted_comparison_upper_bound"] == 110_329_304_013_568
    assert resource["class_power_key_digest_sha256"] == q011be.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011be.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011be.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011be.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_five_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011be_all_unchanged_resource_limits_pass(q011be_cycle: dict[str, Any]) -> None:
    assert q011be_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011be_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011be_cycle["resource_feasibility_gates"].values())
    assert q011be_cycle["failed_validity_order"] == []
    assert q011be_cycle["failed_resource_limit_order"] == []
    assert q011be_cycle["resource_decision"] == q011be.GO_DECISION
    assert q011be_cycle["scientific_outcome"] == "not_evaluated"
    assert q011be_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011be_preserves_the_scientific_boundary(q011be_cycle: dict[str, Any]) -> None:
    theorem = q011be_cycle["theorem_consequence"]
    assert theorem[
        "degree_twenty_five_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_twenty_five_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_five_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 25))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(25, 91))
    assert theorem["q011bd_degree_twenty_four_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty-five product-target relation" in q011be_cycle[
        "claim_boundary"
    ]


def test_q011be_cycle_has_strict_reproducible_digests(q011be_cycle: dict[str, Any]) -> None:
    json.dumps(q011be_cycle, allow_nan=False)
    assert {
        name: q011be_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011be_cycle["result_digest_sha256"] == q011be.q011b._canonical_json_sha256(
        q011be._result_digest_sections(q011be_cycle)
    )


def test_q011be_study_metadata_and_optional_artifact_are_scoped(
    q011be_study: dict[str, Any],
) -> None:
    assert q011be_study["schema_version"] == 1
    assert q011be_study["source"] == source_metadata()
    assert q011be_study["study_gate"] == "passed"
    assert q011be_study["resource_decision"] == q011be.GO_DECISION
    assert q011be_study["scientific_outcome"] == "not_evaluated"
    scope = q011be_study["mathematical_scope"]
    assert scope["degree"] == 25
    assert scope["degree_twenty_five_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_five_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011be_study, allow_nan=False)

    runner_path = Path(q011be.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011be_degree25_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011be artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011be_degree25_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011be.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011be.q011b._canonical_json_sha256(
        q011be._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
