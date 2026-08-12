from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bg_degree26_resource_estimate as q011bg
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "d67038df358cf636011d85d58fe1f5fd7541008443904f7019aca6e74622d857"
EXPECTED_ARTIFACT_SHA256 = "c0501905dcd50807492e99a4ecac25520209aad10a15e0f253c80508613f2b68"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "00f8d11b7ff9ab7acc90ca5c8611d9eb3ed2b72ccdd98eec88564b1e7fb882be",
    "inventory_digest_sha256": (
        "9946663f12a1edec3469799102bde0424606d3e0c981677bedbd71a9fb7b9a60"
    ),
    "envelope_digest_sha256": (
        "5a6fdb92df21d64cc1e29b4500ffff85e396a26771ba859f57e2280842a20c28"
    ),
    "resource_digest_sha256": (
        "7949f6adb8226fe5d19f189978912b562ddff07fb4b091d915c12d68a5f20d78"
    ),
    "result_digest_sha256": "fffce6dd6ed9beacaa22199f3d83cf3037ceb83f8142e3e9eccfdf1620f18d82",
}


@pytest.fixture(scope="module")
def q011bg_study() -> dict[str, Any]:
    return q011bg.run_q011bg_study()


@pytest.fixture(scope="module")
def q011bg_cycle(q011bg_study: dict[str, Any]) -> dict[str, Any]:
    return q011bg_study["cycle"]


def test_q011bg_seals_q011bf_and_all_prior_inputs(q011bg_cycle: dict[str, Any]) -> None:
    sealed = q011bg_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 37
    assert sealed["direct_digest_count"] == 180
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bf"]["digests"]) == q011bg.Q011BF_DIGESTS
    assert sealed["q011bf"]["artifact_sha256"] == q011bg.Q011BF_ARTIFACT_SHA256
    assert sealed["q011bf"]["runner_sha256"] == q011bg.Q011BF_RUNNER_SHA256


def test_q011bg_reconstructs_the_exact_degree_twenty_six_inventory(
    q011bg_cycle: dict[str, Any],
) -> None:
    inventory = q011bg_cycle["degree_twenty_six_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 26
    assert inventory["degree_aggregate_count"] == 3_654
    assert inventory["degree_expanded_product_control_count"] == 169_911
    assert inventory["old_modulus_separated_aggregate_count"] == 2_875
    assert inventory["old_modulus_overlap_aggregate_count"] == 779
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 35
    assert inventory["unique_external_target_count"] == 460
    assert inventory["multi_target_external_component_aggregate_count"] == 0
    assert inventory["maximum_external_component_count"] == 1
    assert inventory["target_identifier_block_counts"] == list(
        q011bg.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 0, 26, 0]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [26, 0, 0, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bg.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bg.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bg.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bg.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bg.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bg_preserves_a_monotone_disc_inventory(q011bg_cycle: dict[str, Any]) -> None:
    envelope = q011bg_cycle["degree_twenty_six_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 460
    assert envelope["prior_q011be_identifier_count"] == 484
    assert envelope["active_reused_q011be_identifier_count"] == 400
    assert envelope["inactive_retained_q011be_identifier_count"] == 84
    assert envelope["added_target_identifier_count"] == 84
    assert envelope["removed_q011be_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 484
    assert envelope["final_monotone_identifier_count"] == 568
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bg.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bg.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bg.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bg.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bg.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bg.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bg.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bg.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bg.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bg_reproduces_the_design_only_resource_contract(
    q011bg_cycle: dict[str, Any],
) -> None:
    resource = q011bg_cycle["degree_twenty_six_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 150
    assert resource["group_pool_cache_key_count"] == 99
    assert resource["group_signature_record_count"] == 632
    assert resource["pair_pool_cache_key_count"] == 290
    assert resource["cached_pair_signature_entry_count"] == 8_262
    assert resource["exact_convolution_call_count"] == 9_474
    assert resource["modulus_signature_count"] == 32_455
    assert resource["peak_live_combined_signature_count"] == 156
    assert resource["peak_two_product_bound_array_bytes"] == 2_496
    assert resource["original_monomial_count"] == 11_279_576_045_274
    assert resource["maximum_aggregate_monomial_count"] == 160_320_160_000
    assert resource["safe_int64_convolution_crude_upper_bound"] == 2_725_442_720_000
    assert resource["distinct_comparison_upper_bound"] == 576_636
    assert resource["weighted_comparison_upper_bound"] == 241_078_715_222_912
    assert resource["class_power_key_digest_sha256"] == q011bg.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bg.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bg.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bg.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_twenty_six_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bg_all_unchanged_resource_limits_pass(q011bg_cycle: dict[str, Any]) -> None:
    assert q011bg_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bg_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bg_cycle["resource_feasibility_gates"].values())
    assert q011bg_cycle["failed_validity_order"] == []
    assert q011bg_cycle["failed_resource_limit_order"] == []
    assert q011bg_cycle["resource_decision"] == q011bg.GO_DECISION
    assert q011bg_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bg_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bg_preserves_the_scientific_boundary(q011bg_cycle: dict[str, Any]) -> None:
    theorem = q011bg_cycle["theorem_consequence"]
    assert theorem[
        "degree_twenty_six_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_twenty_six_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_twenty_six_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 26))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(26, 91))
    assert theorem["q011bf_degree_twenty_five_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-twenty-six product-target relation" in q011bg_cycle[
        "claim_boundary"
    ]


def test_q011bg_cycle_has_strict_reproducible_digests(q011bg_cycle: dict[str, Any]) -> None:
    json.dumps(q011bg_cycle, allow_nan=False)
    assert {
        name: q011bg_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011bg_cycle["result_digest_sha256"] == q011bg.q011b._canonical_json_sha256(
        q011bg._result_digest_sections(q011bg_cycle)
    )


def test_q011bg_study_metadata_and_optional_artifact_are_scoped(
    q011bg_study: dict[str, Any],
) -> None:
    assert q011bg_study["schema_version"] == 1
    assert q011bg_study["source"] == source_metadata()
    assert q011bg_study["study_gate"] == "passed"
    assert q011bg_study["resource_decision"] == q011bg.GO_DECISION
    assert q011bg_study["scientific_outcome"] == "not_evaluated"
    scope = q011bg_study["mathematical_scope"]
    assert scope["degree"] == 26
    assert scope["degree_twenty_six_external_nonresonance_claim"] is False
    assert scope["actual_degree_twenty_six_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bg_study, allow_nan=False)

    runner_path = Path(q011bg.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bg_degree26_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bg artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bg_degree26_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bg.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bg.q011b._canonical_json_sha256(
        q011bg._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
