from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ap_degree18_resource_estimate as q011ap
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ap_study() -> dict[str, Any]:
    return q011ap.run_q011ap_study()


@pytest.fixture(scope="module")
def q011ap_cycle(q011ap_study: dict[str, Any]) -> dict[str, Any]:
    return q011ap_study["cycle"]


def test_q011ap_seals_q011ao_and_all_prior_inputs(q011ap_cycle: dict[str, Any]) -> None:
    sealed = q011ap_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 20
    assert sealed["direct_digest_count"] == 103
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ao"]["digests"]) == q011ap.Q011AO_DIGESTS
    assert sealed["q011ao"]["artifact_sha256"] == q011ap.Q011AO_ARTIFACT_SHA256
    assert sealed["q011ao"]["runner_sha256"] == q011ap.Q011AO_RUNNER_SHA256


def test_q011ap_reconstructs_the_exact_degree_eighteen_inventory(
    q011ap_cycle: dict[str, Any],
) -> None:
    inventory = q011ap_cycle["degree_eighteen_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree_aggregate_count"] == 1_330
    assert inventory["degree_expanded_product_control_count"] == 33_649
    assert inventory["old_modulus_separated_aggregate_count"] == 1_078
    assert inventory["old_modulus_overlap_aggregate_count"] == 252
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 18
    assert inventory["unique_external_target_count"] == 164
    assert inventory["multi_target_external_component_aggregate_count"] == 4
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["target_identifier_block_counts"] == list(
        q011ap.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011ap.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011ap.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011ap.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011ap.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011ap.EXPECTED_INVENTORY_DIGEST


def test_q011ap_builds_only_the_registered_degree_eighteen_disc_inventory(
    q011ap_cycle: dict[str, Any],
) -> None:
    envelope = q011ap_cycle["degree_eighteen_envelope_inventory_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 164
    assert envelope["reused_q011ao_identifier_count"] == 160
    assert envelope["reused_q011ao_selected_identifier_count"] == 24
    assert envelope["reused_q011ao_target_identifier_count"] == 136
    assert envelope["new_q011ak_target_identifier_count"] == 28
    assert envelope["final_identifier_count"] == 188
    assert tuple(envelope["new_q011ak_target_identifiers"]) == q011ap.NEW_TARGET_IDENTIFIERS
    assert envelope["new_target_identifier_digest_sha256"] == (
        q011ap.EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST
    )
    assert envelope["new_q011ak_target_record_digest_sha256"] == (
        q011ap.EXPECTED_NEW_TARGET_RECORD_DIGEST
    )
    assert envelope["final_disc_record_digest_sha256"] == q011ap.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert envelope["selected_class_membership_digest_sha256"] == (
        q011ap.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    assert envelope["q011ak_formula_replay_record_count"] == 204
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011ap_reproduces_the_deterministic_resource_contract(
    q011ap_cycle: dict[str, Any],
) -> None:
    resource = q011ap_cycle["degree_eighteen_hierarchical_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 268
    assert resource["group_pool_cache_key_count"] == 66
    assert resource["group_signature_record_count"] == 139_922
    assert resource["pair_pool_cache_key_count"] == 125
    assert resource["cached_pair_signature_entry_count"] == 1_450_127
    assert resource["exact_convolution_call_count"] == 2_277_951
    assert resource["modulus_signature_count"] == 112_289_821
    assert resource["peak_live_combined_signature_count"] == 2_102_100
    assert resource["peak_two_product_bound_array_bytes"] == 33_633_600
    assert resource["original_monomial_count"] == 50_931_347_136
    assert resource["distinct_comparison_upper_bound"] == 996_565_068
    assert resource["weighted_comparison_upper_bound"] == 485_076_664_408
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011ap.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["safe_int64_convolution_crude_upper_bound"] == 20_023_660_800
    assert not resource["full_degree_eighteen_monomial_list_retained"]
    assert not resource["product_bound_matrix_constructed"]
    assert not resource["fourier_coefficient_matrix_constructed"]
    assert not resource["classification_matrix_constructed"]
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011ap_projection_and_all_registered_resource_limits_pass(
    q011ap_cycle: dict[str, Any],
) -> None:
    resource = q011ap_cycle["degree_eighteen_hierarchical_resource_audit"]
    projection = resource["calibrated_projection"]
    ratios = resource["q011ao_workload_ratios"]
    assert ratios["peak_live_signature"] == {
        "numerator": 7,
        "denominator": 4,
        "float": 1.75,
    }
    assert projection["projected_wall_seconds"]["float"] == pytest.approx(461.793662419578)
    assert projection["wall_time_double_safety_upper_seconds"]["float"] == pytest.approx(
        923.587324839156
    )
    assert projection["tracemalloc_one_point_five_safety_upper_bytes"] == 1_556_992_514
    assert projection["process_memory_one_point_five_safety_upper_bytes"] == 4_296_907_776
    assert not projection["projection_is_a_scientific_acceptance_threshold"]
    assert all(gate["passed"] for gate in q011ap_cycle["resource_feasibility_gates"].values())
    assert q011ap_cycle["failed_resource_limit_order"] == []
    assert q011ap_cycle["resource_decision"] == q011ap.GO_DECISION


def test_q011ap_preserves_the_scientific_boundary(q011ap_cycle: dict[str, Any]) -> None:
    assert q011ap_cycle["study_validity"] == "passed"
    assert q011ap_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ap_cycle["actual_resonance_outcome"] == "not_evaluated"
    assert all(gate["passed"] for gate in q011ap_cycle["validity_gates"].values())
    theorem = q011ap_cycle["theorem_consequence"]
    assert theorem["degree_eighteen_full_sweep_preregistration_is_resource_supported"]
    assert not theorem["degree_eighteen_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_eighteen_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 18))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(18, 91))
    assert "evaluates no product-target relation" in q011ap_cycle["claim_boundary"]
    assert "Q011aq" in q011ap_cycle["next_change"]


def test_q011ap_cycle_has_strict_reproducible_digests(
    q011ap_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ap_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": "e39b183a97916bb1c108a23ea6cf9ae3328f7423c8d83199154f37e4e1dc306c",
        "inventory_digest_sha256": (
            "ffc0d158333068d535a71f2dbb1cfaec3d495c7a2ee169dda9aff5cf07727141"
        ),
        "envelope_digest_sha256": (
            "9cdc661ff2354b1dfb7655c5819ec7ecdb655dd8369886af0609cc7df3b68379"
        ),
        "resource_digest_sha256": (
            "87679bf4427084316b0686cf362c03e25fdb0b7f57be01f9fd34d310381c386b"
        ),
        "result_digest_sha256": (
            "90139ef58140152924ba0629094dd21099ef0d4df05f26651a719d1877c181d4"
        ),
    }
    assert {name: q011ap_cycle[name] for name in expected} == expected
    assert q011ap_cycle["result_digest_sha256"] == q011ap.q011b._canonical_json_sha256(
        q011ap._result_digest_sections(q011ap_cycle)
    )


def test_q011ap_study_metadata_and_generated_artifact_are_scoped(
    q011ap_study: dict[str, Any],
) -> None:
    assert q011ap_study["schema_version"] == 1
    assert q011ap_study["source"] == source_metadata()
    assert q011ap_study["study_gate"] == "passed"
    assert q011ap_study["resource_decision"] == q011ap.GO_DECISION
    assert q011ap_study["scientific_outcome"] == "not_evaluated"
    assert q011ap_study["actual_resonance_outcome"] == "not_evaluated"
    scope = q011ap_study["mathematical_scope"]
    assert scope["degree"] == 18
    assert scope["degree_eighteen_external_nonresonance_claim"] is False
    assert scope["degrees_18_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    assert q011ap_study["arithmetic_runtime"]["relation_classification"] == "not evaluated"
    json.dumps(q011ap_study, allow_nan=False)

    runner_path = Path(q011ap.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ap_degree18_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011ap artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011ap_degree18_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011ap.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011ap.q011b._canonical_json_sha256(
        q011ap._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)
