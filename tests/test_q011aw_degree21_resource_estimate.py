from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011aw_degree21_resource_estimate as q011aw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "ece845c00b7a49bd9bd12e7c30b763150d18b64fa68539b03c43c3748ca827cc"
EXPECTED_ARTIFACT_SHA256 = "0228b387f0308e98051085bdf68e16c7baef4326467c102e152e7ae3f189425e"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "9e76ca9a07ca6eb442a9fdb397f72ace03084f7e3f2c0b30fa312660c49455c2",
    "inventory_digest_sha256": (
        "2d1cdd3aaff4b3b224b212b8baf719293ce4595552a2da40da54d7e3592af0ce"
    ),
    "envelope_digest_sha256": (
        "e4e7435a47e12a262a7ca6f2fc56125d4d18cbf3f0c0b348f3ff6cbee3c2ad49"
    ),
    "resource_digest_sha256": (
        "16ae0966509a3f9d4a608b025dfac11de996f9613e1a2f8f198a41e495d5f488"
    ),
    "result_digest_sha256": "599143be7991dbebfe6f2da0cc1d3883d5a83985e02fd3685a71cca82aae3f71",
}


@pytest.fixture(scope="module")
def q011aw_study() -> dict[str, Any]:
    return q011aw.run_q011aw_study()


@pytest.fixture(scope="module")
def q011aw_cycle(q011aw_study: dict[str, Any]) -> dict[str, Any]:
    return q011aw_study["cycle"]


def test_q011aw_seals_q011av_and_all_prior_inputs(q011aw_cycle: dict[str, Any]) -> None:
    sealed = q011aw_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 27
    assert sealed["direct_digest_count"] == 135
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011av"]["digests"]) == q011aw.Q011AV_DIGESTS
    assert sealed["q011av"]["artifact_sha256"] == q011aw.Q011AV_ARTIFACT_SHA256
    assert sealed["q011av"]["runner_sha256"] == q011aw.Q011AV_RUNNER_SHA256


def test_q011aw_reconstructs_the_exact_degree_twenty_one_inventory(
    q011aw_cycle: dict[str, Any],
) -> None:
    inventory = q011aw_cycle["degree_twenty_one_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 21
    assert inventory["degree_aggregate_count"] == 2_024
    assert inventory["degree_expanded_product_control_count"] == 65_780
    assert inventory["old_modulus_separated_aggregate_count"] == 1_660
    assert inventory["old_modulus_overlap_aggregate_count"] == 364
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 20
    assert inventory["unique_external_target_count"] == 228
    assert inventory["multi_target_external_component_aggregate_count"] == 12
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 0, 13, 8]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [19, 0, 2, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == q011aw.EXPECTED_COUNT_TUPLE_DIGEST
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011aw.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == q011aw.EXPECTED_OVERLAP_RECORD_DIGEST
    assert inventory["external_target_record_digest_sha256"] == (
        q011aw.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011aw.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011aw_preserves_prior_discs_and_source_hulls(q011aw_cycle: dict[str, Any]) -> None:
    envelope = q011aw_cycle["degree_twenty_one_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 228
    assert envelope["prior_q011au_identifier_count"] == 244
    assert envelope["reused_q011au_identifier_count"] == 244
    assert envelope["added_target_identifier_count"] == 8
    assert envelope["removed_q011au_identifier_count"] == 0
    assert envelope["final_identifier_count"] == 252
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011aw.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011aw.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011aw.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["final_disc_record_digest_sha256"] == q011aw.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011aw.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011aw.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011aw_reproduces_the_design_only_resource_contract(
    q011aw_cycle: dict[str, Any],
) -> None:
    resource = q011aw_cycle["degree_twenty_one_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 121
    assert resource["group_pool_cache_key_count"] == 80
    assert resource["group_signature_record_count"] == 482
    assert resource["pair_pool_cache_key_count"] == 192
    assert resource["cached_pair_signature_entry_count"] == 5_523
    assert resource["exact_convolution_call_count"] == 6_448
    assert resource["modulus_signature_count"] == 12_458
    assert resource["peak_live_combined_signature_count"] == 126
    assert resource["peak_two_product_bound_array_bytes"] == 2_016
    assert resource["original_monomial_count"] == 294_674_427_372
    assert resource["maximum_aggregate_monomial_count"] == 7_852_416_000
    assert resource["safe_int64_convolution_crude_upper_bound"] == 133_491_072_000
    assert resource["distinct_comparison_upper_bound"] == 146_928
    assert resource["weighted_comparison_upper_bound"] == 3_951_865_509_552
    assert resource["class_power_key_digest_sha256"] == q011aw.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011aw.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011aw.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011aw.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_one_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011aw_all_unchanged_resource_limits_pass(q011aw_cycle: dict[str, Any]) -> None:
    assert q011aw_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011aw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011aw_cycle["resource_feasibility_gates"].values())
    assert q011aw_cycle["failed_validity_order"] == []
    assert q011aw_cycle["failed_resource_limit_order"] == []
    assert q011aw_cycle["resource_decision"] == q011aw.GO_DECISION
    assert q011aw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011aw_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011aw_preserves_the_scientific_boundary(q011aw_cycle: dict[str, Any]) -> None:
    theorem = q011aw_cycle["theorem_consequence"]
    assert theorem[
        "degree_twenty_one_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_twenty_one_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_one_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 21))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(21, 91))
    assert theorem["q011av_degree_twenty_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty-one product-target relation" in q011aw_cycle[
        "claim_boundary"
    ]


def test_q011aw_cycle_has_strict_reproducible_digests(q011aw_cycle: dict[str, Any]) -> None:
    json.dumps(q011aw_cycle, allow_nan=False)
    for name, digest in EXPECTED_SECTION_DIGESTS.items():
        assert q011aw_cycle[name] == digest
    assert q011aw_cycle["result_digest_sha256"] == q011aw.q011b._canonical_json_sha256(
        q011aw._result_digest_sections(q011aw_cycle)
    )


def test_q011aw_study_metadata_and_optional_artifact_are_scoped(
    q011aw_study: dict[str, Any],
) -> None:
    assert q011aw_study["schema_version"] == 1
    assert q011aw_study["source"] == source_metadata()
    assert q011aw_study["study_gate"] == "passed"
    assert q011aw_study["resource_decision"] == q011aw.GO_DECISION
    assert q011aw_study["scientific_outcome"] == "not_evaluated"
    scope = q011aw_study["mathematical_scope"]
    assert scope["degree"] == 21
    assert scope["degree_twenty_one_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_one_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011aw_study, allow_nan=False)

    runner_path = Path(q011aw.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011aw_degree21_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011aw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011aw_degree21_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011aw.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011aw.q011b._canonical_json_sha256(
        q011aw._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
