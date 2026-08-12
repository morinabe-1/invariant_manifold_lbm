from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bs_degree32_resource_estimate as q011bs
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "29762a6340bab65a7529be5e9a7daa2551d2dd7f9e7cb2de0ba7c380686dc915"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "4ad7d33e537ab02b8804f73dbd7e4fa8ca244b38445acd9adc5214e6b87551cc"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "34e0b713ad0867929277aeb9a93ed105881cef02c7e83ee440ef4b4945031aef",
    "inventory_digest_sha256": (
        "0afd42a9908c0837f7a7b4fec3717696d0d7e0393e77965fa51c8e78f67ac0d0"
    ),
    "envelope_digest_sha256": (
        "a01c77f6c21dae7324bbc9c0c2e40aa02f2f53a10ee566bc74eb9973900842ff"
    ),
    "resource_digest_sha256": (
        "f115e235d3fce9c9d07866f7d29b41b36ee5fea0adb17468723f6e4138a13516"
    ),
    "result_digest_sha256": "33f1eccaf1f3ac12138d39bfeb498b0540c8892977ee2c011e4706b7c9455e20",
}


@pytest.fixture(scope="module")
def q011bs_study() -> dict[str, Any]:
    return q011bs.run_q011bs_study()


@pytest.fixture(scope="module")
def q011bs_cycle(q011bs_study: dict[str, Any]) -> dict[str, Any]:
    return q011bs_study["cycle"]


def test_q011bs_seals_q011br_and_all_prior_inputs(q011bs_cycle: dict[str, Any]) -> None:
    sealed = q011bs_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 49
    assert sealed["direct_digest_count"] == 234
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011br"]["digests"]) == q011bs.Q011BR_DIGESTS
    assert sealed["q011br"]["artifact_sha256"] == q011bs.Q011BR_ARTIFACT_SHA256
    assert sealed["q011br"]["runner_sha256"] == q011bs.Q011BR_RUNNER_SHA256


def test_q011bs_reconstructs_the_exact_degree_thirty_two_inventory(
    q011bs_cycle: dict[str, Any],
) -> None:
    inventory = q011bs_cycle["degree_thirty_two_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 32
    assert inventory["degree_aggregate_count"] == 6_545
    assert inventory["degree_expanded_product_control_count"] == 435_897
    assert inventory["old_modulus_separated_aggregate_count"] == 4_238
    assert inventory["old_modulus_overlap_aggregate_count"] == 2_307
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 71
    assert inventory["unique_external_target_count"] == 1_024
    assert inventory["multi_target_external_component_aggregate_count"] == 13
    assert inventory["maximum_external_component_count"] == 3
    assert inventory["target_identifier_block_counts"] == list(
        q011bs.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 3, 11, 18]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [32, 0, 0, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bs.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bs.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bs.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bs.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bs.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bs_preserves_a_monotone_disc_inventory(q011bs_cycle: dict[str, Any]) -> None:
    envelope = q011bs_cycle["degree_thirty_two_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 1_024
    assert envelope["prior_q011bq_identifier_count"] == 1_032
    assert envelope["active_reused_q011bq_identifier_count"] == 892
    assert envelope["inactive_retained_q011bq_identifier_count"] == 140
    assert envelope["added_target_identifier_count"] == 156
    assert envelope["removed_q011bq_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 1_048
    assert envelope["final_monotone_identifier_count"] == 1_188
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bs.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bs.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bs.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bs.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bs.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bs.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bs.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bs.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bs.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bs_reproduces_the_design_only_resource_contract(
    q011bs_cycle: dict[str, Any],
) -> None:
    resource = q011bs_cycle["degree_thirty_two_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 186
    assert resource["group_pool_cache_key_count"] == 126
    assert resource["group_signature_record_count"] == 996
    assert resource["pair_pool_cache_key_count"] == 691
    assert resource["cached_pair_signature_entry_count"] == 30_749
    assert resource["exact_convolution_call_count"] == 32_675
    assert resource["modulus_signature_count"] == 147_064
    assert resource["peak_live_combined_signature_count"] == 240
    assert resource["peak_two_product_bound_array_bytes"] == 3_840
    assert resource["original_monomial_count"] == 652_055_297_357_287
    assert resource["maximum_aggregate_monomial_count"] == 3_073_110_104_064
    assert resource["safe_int64_convolution_crude_upper_bound"] == 52_242_871_769_088
    assert resource["distinct_comparison_upper_bound"] == 2_197_696
    assert resource["weighted_comparison_upper_bound"] == 9_099_502_713_798_428
    assert resource["class_power_key_digest_sha256"] == q011bs.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bs.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bs.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bs.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_thirty_two_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bs_all_unchanged_resource_limits_pass(q011bs_cycle: dict[str, Any]) -> None:
    assert q011bs_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bs_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bs_cycle["resource_feasibility_gates"].values())
    assert q011bs_cycle["failed_validity_order"] == []
    assert q011bs_cycle["failed_resource_limit_order"] == []
    assert q011bs_cycle["resource_decision"] == q011bs.GO_DECISION
    assert q011bs_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bs_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bs_preserves_the_scientific_boundary(q011bs_cycle: dict[str, Any]) -> None:
    theorem = q011bs_cycle["theorem_consequence"]
    assert theorem[
        "degree_thirty_two_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_thirty_two_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_two_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 32))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(32, 91))
    assert theorem["q011br_degree_thirty_one_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-thirty-two product-target relation" in q011bs_cycle[
        "claim_boundary"
    ]


def test_q011bs_cycle_has_strict_reproducible_digests(q011bs_cycle: dict[str, Any]) -> None:
    json.dumps(q011bs_cycle, allow_nan=False)
    assert {
        name: q011bs_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011bs_cycle["result_digest_sha256"] == q011bs.q011b._canonical_json_sha256(
        q011bs._result_digest_sections(q011bs_cycle)
    )


def test_q011bs_study_metadata_and_optional_artifact_are_scoped(
    q011bs_study: dict[str, Any],
) -> None:
    assert q011bs_study["schema_version"] == 1
    assert q011bs_study["source"] == source_metadata()
    assert q011bs_study["study_gate"] == "passed"
    assert q011bs_study["resource_decision"] == q011bs.GO_DECISION
    assert q011bs_study["scientific_outcome"] == "not_evaluated"
    scope = q011bs_study["mathematical_scope"]
    assert scope["degree"] == 32
    assert scope["degree_thirty_two_external_nonresonance_claim"] is False
    assert scope["actual_degree_thirty_two_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bs_study, allow_nan=False)

    runner_path = Path(q011bs.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bs_degree32_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bs artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bs_degree32_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bs.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bs.q011b._canonical_json_sha256(
        q011bs._result_digest_sections(artifact["cycle"])
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
