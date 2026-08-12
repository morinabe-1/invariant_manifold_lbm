from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bi_degree27_resource_estimate as q011bi
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "b6b84bf50d0f02793a74caffdc48a04a52d8af67b3aa3b712eba9eb7440fd328"
EXPECTED_ARTIFACT_SHA256 = "61e4f1fd790674e8365013c3e43391c83d5ddfe39c4c48869bc70e90ed088e63"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "057af0c2ee831420b8b97790d7fbcf21429656da6935201a1b8293f0082a6345",
    "inventory_digest_sha256": (
        "b044c0833d2471a9a630a4deabb9dcc8fdebcedf5998483d88188aeb48914134"
    ),
    "envelope_digest_sha256": (
        "403e31aeb201e9f0dd40a07949b1f563c07ab858e9a40080cff8b8b5938264e0"
    ),
    "resource_digest_sha256": (
        "679ba25402815b46ded29807a054273bde6c95a09515d70c0e957f015cba4bad"
    ),
    "result_digest_sha256": "332c9f8f39cd3b024dd70b463e031df851984d8d3bec6b82f35ec89382a38048",
}


@pytest.fixture(scope="module")
def q011bi_study() -> dict[str, Any]:
    return q011bi.run_q011bi_study()


@pytest.fixture(scope="module")
def q011bi_cycle(q011bi_study: dict[str, Any]) -> dict[str, Any]:
    return q011bi_study["cycle"]


def test_q011bi_seals_q011bh_and_all_prior_inputs(q011bi_cycle: dict[str, Any]) -> None:
    sealed = q011bi_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 39
    assert sealed["direct_digest_count"] == 189
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bh"]["digests"]) == q011bi.Q011BH_DIGESTS
    assert sealed["q011bh"]["artifact_sha256"] == q011bi.Q011BH_ARTIFACT_SHA256
    assert sealed["q011bh"]["runner_sha256"] == q011bi.Q011BH_RUNNER_SHA256


def test_q011bi_reconstructs_the_exact_degree_twenty_seven_inventory(
    q011bi_cycle: dict[str, Any],
) -> None:
    inventory = q011bi_cycle["degree_twenty_seven_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 27
    assert inventory["degree_aggregate_count"] == 4_060
    assert inventory["degree_expanded_product_control_count"] == 201_376
    assert inventory["old_modulus_separated_aggregate_count"] == 3_101
    assert inventory["old_modulus_overlap_aggregate_count"] == 959
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 38
    assert inventory["unique_external_target_count"] == 488
    assert inventory["multi_target_external_component_aggregate_count"] == 0
    assert inventory["maximum_external_component_count"] == 1
    assert inventory["target_identifier_block_counts"] == list(
        q011bi.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 4, 3, 20]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [26, 0, 1, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bi.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bi.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bi.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bi.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bi.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bi_preserves_a_monotone_disc_inventory(q011bi_cycle: dict[str, Any]) -> None:
    envelope = q011bi_cycle["degree_twenty_seven_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 488
    assert envelope["prior_q011bg_identifier_count"] == 568
    assert envelope["active_reused_q011bg_identifier_count"] == 476
    assert envelope["inactive_retained_q011bg_identifier_count"] == 92
    assert envelope["added_target_identifier_count"] == 36
    assert envelope["removed_q011bg_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 512
    assert envelope["final_monotone_identifier_count"] == 604
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bi.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bi.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bi.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bi.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bi.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bi.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bi.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bi.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bi.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bi_reproduces_the_design_only_resource_contract(
    q011bi_cycle: dict[str, Any],
) -> None:
    resource = q011bi_cycle["degree_twenty_seven_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 154
    assert resource["group_pool_cache_key_count"] == 104
    assert resource["group_signature_record_count"] == 705
    assert resource["pair_pool_cache_key_count"] == 341
    assert resource["cached_pair_signature_entry_count"] == 10_293
    assert resource["exact_convolution_call_count"] == 11_649
    assert resource["modulus_signature_count"] == 43_285
    assert resource["peak_live_combined_signature_count"] == 180
    assert resource["peak_two_product_bound_array_bytes"] == 2_880
    assert resource["original_monomial_count"] == 25_561_324_661_692
    assert resource["maximum_aggregate_monomial_count"] == 272_544_272_000
    assert resource["safe_int64_convolution_crude_upper_bound"] == 4_633_252_624_000
    assert resource["distinct_comparison_upper_bound"] == 763_404
    assert resource["weighted_comparison_upper_bound"] == 502_998_748_050_560
    assert resource["class_power_key_digest_sha256"] == q011bi.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bi.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bi.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bi.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_seven_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bi_all_unchanged_resource_limits_pass(q011bi_cycle: dict[str, Any]) -> None:
    assert q011bi_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bi_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bi_cycle["resource_feasibility_gates"].values())
    assert q011bi_cycle["failed_validity_order"] == []
    assert q011bi_cycle["failed_resource_limit_order"] == []
    assert q011bi_cycle["resource_decision"] == q011bi.GO_DECISION
    assert q011bi_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bi_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bi_preserves_the_scientific_boundary(q011bi_cycle: dict[str, Any]) -> None:
    theorem = q011bi_cycle["theorem_consequence"]
    assert theorem[
        "degree_twenty_seven_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_twenty_seven_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_seven_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 27))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(27, 91))
    assert theorem["q011bh_degree_twenty_six_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty-seven product-target relation" in q011bi_cycle[
        "claim_boundary"
    ]


def test_q011bi_cycle_has_strict_reproducible_digests(q011bi_cycle: dict[str, Any]) -> None:
    json.dumps(q011bi_cycle, allow_nan=False)
    assert {
        name: q011bi_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011bi_cycle["result_digest_sha256"] == q011bi.q011b._canonical_json_sha256(
        q011bi._result_digest_sections(q011bi_cycle)
    )


def test_q011bi_study_metadata_and_optional_artifact_are_scoped(
    q011bi_study: dict[str, Any],
) -> None:
    assert q011bi_study["schema_version"] == 1
    assert q011bi_study["source"] == source_metadata()
    assert q011bi_study["study_gate"] == "passed"
    assert q011bi_study["resource_decision"] == q011bi.GO_DECISION
    assert q011bi_study["scientific_outcome"] == "not_evaluated"
    scope = q011bi_study["mathematical_scope"]
    assert scope["degree"] == 27
    assert scope["degree_twenty_seven_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_seven_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bi_study, allow_nan=False)

    runner_path = Path(q011bi.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bi_degree27_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bi artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bi_degree27_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bi.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bi.q011b._canonical_json_sha256(
        q011bi._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
