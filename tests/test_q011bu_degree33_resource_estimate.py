from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bu_degree33_resource_estimate as q011bu
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "8dcdcc8cf0604c479389bfcb45b5b19f043cc40c365b4d92f526a4078bd141c8"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "e3228fa06b67266c0f8d37ea78487d781d43f5aa1a99d38965027a7006b8dd86"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "c7c1f68706bdb00723ffdf35ba31edb185b4032c57400536dca8e53eaeedb13c",
    "inventory_digest_sha256": (
        "8f6070b00f376c6372545f0cdde892ff2f86edbf069642a854a2e2798f9b3c69"
    ),
    "envelope_digest_sha256": (
        "4aadbc1eeb9e96414d562420a60d5694d22801ddc974ccdc86ccb05be8474726"
    ),
    "resource_digest_sha256": (
        "4b3df14371829e2127ca4a2bbde0a05cc2936d9cd236d3ff155afb4b221a5634"
    ),
    "result_digest_sha256": "a217bd08728f6ec2f37dcb626bcdf0eb19e76e66e44dc536afac47650e180657",
}


@pytest.fixture(scope="module")
def q011bu_study() -> dict[str, Any]:
    return q011bu.run_q011bu_study()


@pytest.fixture(scope="module")
def q011bu_cycle(q011bu_study: dict[str, Any]) -> dict[str, Any]:
    return q011bu_study["cycle"]


def test_q011bu_seals_q011bt_and_all_prior_inputs(q011bu_cycle: dict[str, Any]) -> None:
    sealed = q011bu_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 51
    assert sealed["direct_digest_count"] == 243
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bt"]["digests"]) == q011bu.Q011BT_DIGESTS
    assert sealed["q011bt"]["artifact_sha256"] == q011bu.Q011BT_ARTIFACT_SHA256
    assert sealed["q011bt"]["runner_sha256"] == q011bu.Q011BT_RUNNER_SHA256


def test_q011bu_reconstructs_the_exact_degree_thirty_three_inventory(
    q011bu_cycle: dict[str, Any],
) -> None:
    inventory = q011bu_cycle["degree_thirty_three_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 33
    assert inventory["degree_aggregate_count"] == 7_140
    assert inventory["degree_expanded_product_control_count"] == 501_942
    assert inventory["old_modulus_separated_aggregate_count"] == 4_454
    assert inventory["old_modulus_overlap_aggregate_count"] == 2_686
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 74
    assert inventory["unique_external_target_count"] == 1_128
    assert inventory["multi_target_external_component_aggregate_count"] == 25
    assert inventory["maximum_external_component_count"] == 3
    assert inventory["target_identifier_block_counts"] == list(
        q011bu.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 2, 11, 20]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [32, 0, 1, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bu.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bu.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bu.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bu.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bu.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bu_preserves_a_monotone_disc_inventory(q011bu_cycle: dict[str, Any]) -> None:
    envelope = q011bu_cycle["degree_thirty_three_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 1_128
    assert envelope["prior_q011bs_identifier_count"] == 1_188
    assert envelope["active_reused_q011bs_identifier_count"] == 1_048
    assert envelope["inactive_retained_q011bs_identifier_count"] == 140
    assert envelope["added_target_identifier_count"] == 104
    assert envelope["removed_q011bs_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 1_152
    assert envelope["final_monotone_identifier_count"] == 1_292
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bu.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bu.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bu.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bu.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bu.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bu.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bu.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bu.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bu.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bu_reproduces_the_design_only_resource_contract(
    q011bu_cycle: dict[str, Any],
) -> None:
    resource = q011bu_cycle["degree_thirty_three_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 193
    assert resource["group_pool_cache_key_count"] == 129
    assert resource["group_signature_record_count"] == 1_121
    assert resource["pair_pool_cache_key_count"] == 771
    assert resource["cached_pair_signature_entry_count"] == 39_643
    assert resource["exact_convolution_call_count"] == 41_820
    assert resource["modulus_signature_count"] == 181_711
    assert resource["peak_live_combined_signature_count"] == 272
    assert resource["peak_two_product_bound_array_bytes"] == 4_352
    assert resource["original_monomial_count"] == 1_182_191_544_739_044
    assert resource["maximum_aggregate_monomial_count"] == 4_835_313_100_800
    assert resource["safe_int64_convolution_crude_upper_bound"] == 82_200_322_713_600
    assert resource["distinct_comparison_upper_bound"] == 2_754_464
    assert resource["weighted_comparison_upper_bound"] == 16_429_979_607_740_272
    assert resource["class_power_key_digest_sha256"] == q011bu.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bu.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bu.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bu.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_thirty_three_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bu_all_unchanged_resource_limits_pass(q011bu_cycle: dict[str, Any]) -> None:
    assert q011bu_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bu_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bu_cycle["resource_feasibility_gates"].values())
    assert q011bu_cycle["failed_validity_order"] == []
    assert q011bu_cycle["failed_resource_limit_order"] == []
    assert q011bu_cycle["resource_decision"] == q011bu.GO_DECISION
    assert q011bu_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bu_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bu_preserves_the_scientific_boundary(q011bu_cycle: dict[str, Any]) -> None:
    theorem = q011bu_cycle["theorem_consequence"]
    assert theorem[
        "degree_thirty_three_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_thirty_three_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_three_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 33))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(33, 91))
    assert theorem["q011bt_degree_thirty_two_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-thirty-three product-target relation" in q011bu_cycle[
        "claim_boundary"
    ]


def test_q011bu_cycle_has_strict_reproducible_digests(q011bu_cycle: dict[str, Any]) -> None:
    json.dumps(q011bu_cycle, allow_nan=False)
    assert {
        name: q011bu_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011bu_cycle["result_digest_sha256"] == q011bu.q011b._canonical_json_sha256(
        q011bu._result_digest_sections(q011bu_cycle)
    )


def test_q011bu_study_metadata_and_optional_artifact_are_scoped(
    q011bu_study: dict[str, Any],
) -> None:
    assert q011bu_study["schema_version"] == 1
    assert q011bu_study["source"] == source_metadata()
    assert q011bu_study["study_gate"] == "passed"
    assert q011bu_study["resource_decision"] == q011bu.GO_DECISION
    assert q011bu_study["scientific_outcome"] == "not_evaluated"
    scope = q011bu_study["mathematical_scope"]
    assert scope["degree"] == 33
    assert scope["degree_thirty_three_external_nonresonance_claim"] is False
    assert scope["actual_degree_thirty_three_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bu_study, allow_nan=False)

    runner_path = Path(q011bu.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bu_degree33_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bu artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bu_degree33_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bu.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bu.q011b._canonical_json_sha256(
        q011bu._result_digest_sections(artifact["cycle"])
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
