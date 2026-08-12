from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bc_degree24_resource_estimate as q011bc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "f34211ca52a08845a7453737b1c29c63ee0b5ba9d540b7c47e04c6308ba650a6"
EXPECTED_ARTIFACT_SHA256 = "a6e0ab8762fecc9ed006a1692b634cc5ad6937a3fcb909554ab8e352c0a74a2e"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "0109bd6dcac3685c4a414d4018779b1f013472fbb44b444eb33edab4a73bb358",
    "inventory_digest_sha256": (
        "41ee0d1a6e37236f920436fce19dc4a32db1f112afe7ed3ad33d2c83a596171f"
    ),
    "envelope_digest_sha256": (
        "8391403853a090ed93999aedc337dd6f6904db548679cf03f88b07c956e2c3a1"
    ),
    "resource_digest_sha256": (
        "3d7c25527cd76b4b3d69ad50a800b5cd6dcd3dcdfa68df5b2e0a91ce45d4ea92"
    ),
    "result_digest_sha256": "ad9f3e0286ef977602ce8472ab9ed3a6970f8d4b1932cee3403095990c6be289",
}


@pytest.fixture(scope="module")
def q011bc_study() -> dict[str, Any]:
    return q011bc.run_q011bc_study()


@pytest.fixture(scope="module")
def q011bc_cycle(q011bc_study: dict[str, Any]) -> dict[str, Any]:
    return q011bc_study["cycle"]


def test_q011bc_seals_q011bb_and_all_prior_inputs(q011bc_cycle: dict[str, Any]) -> None:
    sealed = q011bc_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 33
    assert sealed["direct_digest_count"] == 162
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bb"]["digests"]) == q011bc.Q011BB_DIGESTS
    assert sealed["q011bb"]["artifact_sha256"] == q011bc.Q011BB_ARTIFACT_SHA256
    assert sealed["q011bb"]["runner_sha256"] == q011bc.Q011BB_RUNNER_SHA256


def test_q011bc_reconstructs_the_exact_degree_twenty_four_inventory(
    q011bc_cycle: dict[str, Any],
) -> None:
    inventory = q011bc_cycle["degree_twenty_four_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 24
    assert inventory["degree_aggregate_count"] == 2_925
    assert inventory["degree_expanded_product_control_count"] == 118_755
    assert inventory["old_modulus_separated_aggregate_count"] == 2_401
    assert inventory["old_modulus_overlap_aggregate_count"] == 524
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 31
    assert inventory["unique_external_target_count"] == 372
    assert inventory["multi_target_external_component_aggregate_count"] == 9
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["target_identifier_block_counts"] == list(
        q011bc.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 0, 16, 8]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [24, 0, 0, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bc.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bc.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bc.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bc.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bc.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bc_preserves_a_monotone_disc_inventory(q011bc_cycle: dict[str, Any]) -> None:
    envelope = q011bc_cycle["degree_twenty_four_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 372
    assert envelope["prior_q011ba_identifier_count"] == 356
    assert envelope["active_reused_q011ba_identifier_count"] == 308
    assert envelope["inactive_retained_q011ba_identifier_count"] == 48
    assert envelope["added_target_identifier_count"] == 88
    assert envelope["removed_q011ba_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 396
    assert envelope["final_monotone_identifier_count"] == 444
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bc.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bc.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bc.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bc.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bc.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bc.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bc.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bc.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bc.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bc_reproduces_the_design_only_resource_contract(
    q011bc_cycle: dict[str, Any],
) -> None:
    resource = q011bc_cycle["degree_twenty_four_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 135
    assert resource["group_pool_cache_key_count"] == 90
    assert resource["group_signature_record_count"] == 580
    assert resource["pair_pool_cache_key_count"] == 230
    assert resource["cached_pair_signature_entry_count"] == 6_939
    assert resource["exact_convolution_call_count"] == 8_054
    assert resource["modulus_signature_count"] == 19_942
    assert resource["peak_live_combined_signature_count"] == 153
    assert resource["peak_two_product_bound_array_bytes"] == 2_448
    assert resource["original_monomial_count"] == 2_246_535_043_109
    assert resource["maximum_aggregate_monomial_count"] == 38_476_838_400
    assert resource["safe_int64_convolution_crude_upper_bound"] == 654_106_252_800
    assert resource["distinct_comparison_upper_bound"] == 331_524
    assert resource["weighted_comparison_upper_bound"] == 46_505_597_729_848
    assert resource["class_power_key_digest_sha256"] == q011bc.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bc.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bc.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bc.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_four_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bc_all_unchanged_resource_limits_pass(q011bc_cycle: dict[str, Any]) -> None:
    assert q011bc_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bc_cycle["resource_feasibility_gates"].values())
    assert q011bc_cycle["failed_validity_order"] == []
    assert q011bc_cycle["failed_resource_limit_order"] == []
    assert q011bc_cycle["resource_decision"] == q011bc.GO_DECISION
    assert q011bc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bc_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bc_preserves_the_scientific_boundary(q011bc_cycle: dict[str, Any]) -> None:
    theorem = q011bc_cycle["theorem_consequence"]
    assert theorem[
        "degree_twenty_four_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_twenty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_four_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 24))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(24, 91))
    assert theorem["q011bb_degree_twenty_three_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty-four product-target relation" in q011bc_cycle[
        "claim_boundary"
    ]


def test_q011bc_cycle_has_strict_reproducible_digests(q011bc_cycle: dict[str, Any]) -> None:
    json.dumps(q011bc_cycle, allow_nan=False)
    for name, digest in EXPECTED_SECTION_DIGESTS.items():
        assert q011bc_cycle[name] == digest
    assert q011bc_cycle["result_digest_sha256"] == q011bc.q011b._canonical_json_sha256(
        q011bc._result_digest_sections(q011bc_cycle)
    )


def test_q011bc_study_metadata_and_optional_artifact_are_scoped(
    q011bc_study: dict[str, Any],
) -> None:
    assert q011bc_study["schema_version"] == 1
    assert q011bc_study["source"] == source_metadata()
    assert q011bc_study["study_gate"] == "passed"
    assert q011bc_study["resource_decision"] == q011bc.GO_DECISION
    assert q011bc_study["scientific_outcome"] == "not_evaluated"
    scope = q011bc_study["mathematical_scope"]
    assert scope["degree"] == 24
    assert scope["degree_twenty_four_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_four_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bc_study, allow_nan=False)

    runner_path = Path(q011bc.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bc_degree24_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bc_degree24_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bc.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bc.q011b._canonical_json_sha256(
        q011bc._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
