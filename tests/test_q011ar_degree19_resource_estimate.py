from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ar_degree19_resource_estimate as q011ar
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ar_study() -> dict[str, Any]:
    return q011ar.run_q011ar_study()


@pytest.fixture(scope="module")
def q011ar_cycle(q011ar_study: dict[str, Any]) -> dict[str, Any]:
    return q011ar_study["cycle"]


def test_q011ar_seals_q011aq_and_all_prior_inputs(q011ar_cycle: dict[str, Any]) -> None:
    sealed = q011ar_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 22
    assert sealed["direct_digest_count"] == 112
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011aq"]["digests"]) == q011ar.Q011AQ_DIGESTS
    assert sealed["q011aq"]["artifact_sha256"] == q011ar.Q011AQ_ARTIFACT_SHA256
    assert sealed["q011aq"]["runner_sha256"] == q011ar.Q011AQ_RUNNER_SHA256


def test_q011ar_reconstructs_the_exact_degree_nineteen_inventory(
    q011ar_cycle: dict[str, Any],
) -> None:
    inventory = q011ar_cycle["degree_nineteen_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree_aggregate_count"] == 1_540
    assert inventory["degree_expanded_product_control_count"] == 42_504
    assert inventory["old_modulus_separated_aggregate_count"] == 1_255
    assert inventory["old_modulus_overlap_aggregate_count"] == 285
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 17
    assert inventory["unique_external_target_count"] == 160
    assert inventory["multi_target_external_component_aggregate_count"] == 8
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["target_identifier_block_counts"] == list(
        q011ar.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011ar.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011ar.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011ar.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011ar.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011ar.EXPECTED_INVENTORY_DIGEST


def test_q011ar_builds_only_the_registered_degree_nineteen_disc_inventory(
    q011ar_cycle: dict[str, Any],
) -> None:
    envelope = q011ar_cycle["degree_nineteen_envelope_inventory_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 160
    assert envelope["reused_q011ao_identifier_count"] == 156
    assert envelope["reused_q011ao_selected_identifier_count"] == 24
    assert envelope["reused_q011ao_target_identifier_count"] == 132
    assert envelope["new_q011ak_target_identifier_count"] == 28
    assert envelope["final_identifier_count"] == 184
    assert tuple(envelope["new_q011ak_target_identifiers"]) == q011ar.NEW_TARGET_IDENTIFIERS
    assert envelope["new_target_identifier_digest_sha256"] == (
        q011ar.EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST
    )
    assert envelope["new_q011ak_target_record_digest_sha256"] == (
        q011ar.EXPECTED_NEW_TARGET_RECORD_DIGEST
    )
    assert envelope["final_disc_record_digest_sha256"] == q011ar.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert envelope["selected_class_membership_digest_sha256"] == (
        q011ar.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    assert envelope["q011ak_formula_replay_record_count"] == 204
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011ar_reproduces_the_deterministic_resource_contract(
    q011ar_cycle: dict[str, Any],
) -> None:
    resource = q011ar_cycle["degree_nineteen_hierarchical_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 276
    assert resource["group_pool_cache_key_count"] == 66
    assert resource["group_signature_record_count"] == 105_979
    assert resource["pair_pool_cache_key_count"] == 140
    assert resource["cached_pair_signature_entry_count"] == 1_646_172
    assert resource["exact_convolution_call_count"] == 2_270_568
    assert resource["modulus_signature_count"] == 204_937_508
    assert resource["peak_live_combined_signature_count"] == 3_363_360
    assert resource["peak_two_product_bound_array_bytes"] == 53_813_760
    assert resource["original_monomial_count"] == 107_797_786_672
    assert resource["maximum_aggregate_monomial_count"] == 2_038_608_000
    assert resource["safe_int64_convolution_crude_upper_bound"] == 34_656_336_000
    assert resource["distinct_comparison_upper_bound"] == 1_974_912_192
    assert resource["weighted_comparison_upper_bound"] == 1_124_800_752_224
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011ar.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert not resource["full_degree_nineteen_monomial_list_retained"]
    assert not resource["product_bound_matrix_constructed"]
    assert not resource["fourier_coefficient_matrix_constructed"]
    assert not resource["classification_matrix_constructed"]
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011ar_projection_and_registered_stop_decision(
    q011ar_cycle: dict[str, Any],
) -> None:
    resource = q011ar_cycle["degree_nineteen_hierarchical_resource_audit"]
    projection = resource["calibrated_projection"]
    assert resource["q011ao_workload_ratios"]["peak_live_signature"] == {
        "numerator": 14,
        "denominator": 5,
        "float": 2.8,
    }
    assert projection["projected_wall_seconds"]["float"] == pytest.approx(
        915.145396307185
    )
    assert projection["wall_time_double_safety_upper_seconds"]["float"] == pytest.approx(
        1_830.29079261437
    )
    assert projection["tracemalloc_one_point_five_safety_upper_bytes"] == 2_491_188_021
    assert projection["process_memory_one_point_five_safety_upper_bytes"] == 6_875_052_442
    assert not projection["projection_is_a_scientific_acceptance_threshold"]
    assert q011ar.RESOURCE_LIMITS == q011ar.q011ap.RESOURCE_LIMITS

    gates = q011ar_cycle["resource_feasibility_gates"]
    assert gates["exact_convolution_count_is_within_limit"]["passed"]
    expected_failures = [
        "modulus_signature_count_is_within_limit",
        "peak_live_signature_count_is_within_limit",
        "two_product_bound_arrays_are_within_limit",
        "distinct_comparison_upper_bound_is_within_limit",
        "calibrated_double_wall_time_upper_is_within_limit",
        "calibrated_process_memory_upper_is_within_limit",
    ]
    assert q011ar_cycle["failed_resource_limit_order"] == expected_failures
    assert q011ar_cycle["resource_decision"] == q011ar.STOP_DECISION


def test_q011ar_preserves_the_scientific_boundary(q011ar_cycle: dict[str, Any]) -> None:
    assert q011ar_cycle["study_validity"] == "passed"
    assert q011ar_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ar_cycle["actual_resonance_outcome"] == "not_evaluated"
    assert all(gate["passed"] for gate in q011ar_cycle["validity_gates"].values())
    theorem = q011ar_cycle["theorem_consequence"]
    assert not theorem["degree_nineteen_full_sweep_preregistration_is_resource_supported"]
    assert not theorem["degree_nineteen_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_nineteen_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 19))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(19, 91))
    assert theorem["q011aq_degree_eighteen_certificate_is_preserved"]
    assert "evaluates no product-target relation" in q011ar_cycle["claim_boundary"]
    assert "Q011as" in q011ar_cycle["next_change"]
    assert "resource redesign" in q011ar_cycle["next_change"]


def test_q011ar_cycle_has_strict_reproducible_digests(
    q011ar_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ar_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "2be0835736f234a9df83af63fd836aca5196eb6b4e8c54dc86d72723b7b995f6"
        ),
        "inventory_digest_sha256": (
            "9fd64f430ca0f5231e97ec13338aaaf037909d35c2e5a294ed6246d4f87f8848"
        ),
        "envelope_digest_sha256": (
            "b33a4d036c244ed17fb5b708307759883439eef6172e473303fc4ea726c0a70c"
        ),
        "resource_digest_sha256": (
            "c93fb9cb96a91474cbba67aad1b12ad699fd189c537a4ac54305a1b3daf0f328"
        ),
        "result_digest_sha256": (
            "2823bb2101e57bfd277e18e621c17ef850488ec5743083a10f8246e5e61d8f27"
        ),
    }
    assert {name: q011ar_cycle[name] for name in expected} == expected
    assert q011ar_cycle["result_digest_sha256"] == q011ar.q011b._canonical_json_sha256(
        q011ar._result_digest_sections(q011ar_cycle)
    )


def test_q011ar_study_metadata_and_optional_artifact_are_scoped(
    q011ar_study: dict[str, Any],
) -> None:
    assert q011ar_study["schema_version"] == 1
    assert q011ar_study["source"] == source_metadata()
    assert q011ar_study["study_gate"] == "passed"
    assert q011ar_study["resource_decision"] == q011ar.STOP_DECISION
    assert q011ar_study["scientific_outcome"] == "not_evaluated"
    assert q011ar_study["actual_resonance_outcome"] == "not_evaluated"
    scope = q011ar_study["mathematical_scope"]
    assert scope["degree"] == 19
    assert scope["degree_nineteen_external_nonresonance_claim"] is False
    assert scope["degrees_19_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    assert q011ar_study["arithmetic_runtime"]["relation_classification"] == "not evaluated"
    json.dumps(q011ar_study, allow_nan=False)

    runner_path = Path(q011ar.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ar_degree19_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011ar artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "8e0f2cca4c4db357587595ba315aa4fa84121c358e988f4cdcadc8720621e67a"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011ar_degree19_resource_estimate.py",
        "sha256": "4a3faebafd0404f449e1410e98a25bce659a2c4c80c641bdbd642bbd487443aa",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011ar.STOP_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011ar.q011b._canonical_json_sha256(
        q011ar._result_digest_sections(artifact["cycle"])
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
