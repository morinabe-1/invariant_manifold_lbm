from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bw_degree34_resource_estimate as q011bw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "d47f9646896fe3ccee6652f9243f14de106321d084a8050492c057cbc8b986c7"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "d4f3f836e4dd2f89a22895768a0fba3b384e9d6dbcba0ac200cd3bc77f42baf4"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "bb76ff53530570648869b03373ef228708e2a93e7c57d870b890bbc1f2ed9ef9",
    "inventory_digest_sha256": (
        "774063733994c32575aefae52b534970e7d52678d545a104ca6b82678f1c87dd"
    ),
    "envelope_digest_sha256": (
        "85c25d7adb8b032a3031584d255be91ec698df77d186e4ea37f4692890f445db"
    ),
    "resource_digest_sha256": (
        "a8080e0de14dd55cb797c11fb2ecaf60eaa60ed2fdb26d263a489dfacf846bbd"
    ),
    "result_digest_sha256": "f2e37f874fbc9219aa6a6c0ba7d1f7284de7a87d3a328eb9681c28787f4e727c",
}


@pytest.fixture(scope="module")
def q011bw_study() -> dict[str, Any]:
    return q011bw.run_q011bw_study()


@pytest.fixture(scope="module")
def q011bw_cycle(q011bw_study: dict[str, Any]) -> dict[str, Any]:
    return q011bw_study["cycle"]


def test_q011bw_seals_q011bv_and_all_prior_inputs(q011bw_cycle: dict[str, Any]) -> None:
    sealed = q011bw_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 53
    assert sealed["direct_digest_count"] == 252
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bv"]["digests"]) == q011bw.Q011BV_DIGESTS
    assert sealed["q011bv"]["artifact_sha256"] == q011bw.Q011BV_ARTIFACT_SHA256
    assert sealed["q011bv"]["runner_sha256"] == q011bw.Q011BV_RUNNER_SHA256


def test_q011bw_reconstructs_the_exact_degree_thirty_four_inventory(
    q011bw_cycle: dict[str, Any],
) -> None:
    inventory = q011bw_cycle["degree_thirty_four_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree"] == 34
    assert inventory["degree_aggregate_count"] == 7_770
    assert inventory["degree_expanded_product_control_count"] == 575_757
    assert inventory["old_modulus_separated_aggregate_count"] == 4_632
    assert inventory["old_modulus_overlap_aggregate_count"] == 3_138
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 81
    assert inventory["unique_external_target_count"] == 1_300
    assert inventory["multi_target_external_component_aggregate_count"] == 48
    assert inventory["maximum_external_component_count"] == 3
    assert inventory["target_identifier_block_counts"] == list(
        q011bw.EXPECTED_TARGET_BLOCK_COUNTS
    )
    assert inventory["overlap_records"][0]["selected_type_counts"] == [0, 1, 10, 23]
    assert inventory["overlap_records"][-1]["selected_type_counts"] == [33, 0, 1, 0]
    assert inventory["overlap_count_tuple_digest_sha256"] == (
        q011bw.EXPECTED_COUNT_TUPLE_DIGEST
    )
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011bw.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (
        q011bw.EXPECTED_OVERLAP_RECORD_DIGEST
    )
    assert inventory["external_target_record_digest_sha256"] == (
        q011bw.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011bw.EXPECTED_INVENTORY_DIGEST
    assert inventory["product_target_relation_evaluation_count"] == 0


def test_q011bw_preserves_a_monotone_disc_inventory(q011bw_cycle: dict[str, Any]) -> None:
    envelope = q011bw_cycle["degree_thirty_four_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 1_300
    assert envelope["prior_q011bu_identifier_count"] == 1_292
    assert envelope["active_reused_q011bu_identifier_count"] == 1_152
    assert envelope["inactive_retained_q011bu_identifier_count"] == 140
    assert envelope["added_target_identifier_count"] == 172
    assert envelope["removed_q011bu_identifier_count"] == 0
    assert envelope["active_identifier_count"] == 1_324
    assert envelope["final_monotone_identifier_count"] == 1_464
    assert envelope["old_source_class_counts"] == [4, 2, 3, 6]
    assert envelope["merged_source_class_counts"] == [1, 1, 2, 2]
    assert envelope["prior_record_digest_sha256"] == q011bw.EXPECTED_PRIOR_RECORD_DIGEST
    assert envelope["active_reused_record_digest_sha256"] == (
        q011bw.EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
    )
    assert envelope["inactive_retained_identifier_digest_sha256"] == (
        q011bw.EXPECTED_INACTIVE_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_identifier_digest_sha256"] == (
        q011bw.EXPECTED_ADDED_IDENTIFIER_DIGEST
    )
    assert envelope["added_target_record_digest_sha256"] == (
        q011bw.EXPECTED_ADDED_RECORD_DIGEST
    )
    assert envelope["active_disc_record_digest_sha256"] == q011bw.EXPECTED_ACTIVE_RECORD_DIGEST
    assert envelope["final_disc_record_digest_sha256"] == q011bw.EXPECTED_FINAL_RECORD_DIGEST
    assert envelope["source_hull_record_digest_sha256"] == q011bw.EXPECTED_HULL_RECORD_DIGEST
    assert envelope["source_merged_membership_digest_sha256"] == (
        q011bw.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )
    assert envelope["target_lookup_changed"] is False
    assert envelope["product_target_relation_evaluation_count"] == 0


def test_q011bw_reproduces_the_design_only_resource_contract(
    q011bw_cycle: dict[str, Any],
) -> None:
    resource = q011bw_cycle["degree_thirty_four_coalesced_resource_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 200
    assert resource["group_pool_cache_key_count"] == 134
    assert resource["group_signature_record_count"] == 1_191
    assert resource["pair_pool_cache_key_count"] == 885
    assert resource["cached_pair_signature_entry_count"] == 50_282
    assert resource["exact_convolution_call_count"] == 52_596
    assert resource["modulus_signature_count"] == 221_676
    assert resource["peak_live_combined_signature_count"] == 306
    assert resource["peak_two_product_bound_array_bytes"] == 4_896
    assert resource["original_monomial_count"] == 2_119_833_971_218_270
    assert resource["maximum_aggregate_monomial_count"] == 7_252_969_651_200
    assert resource["safe_int64_convolution_crude_upper_bound"] == 123_300_484_070_400
    assert resource["distinct_comparison_upper_bound"] == 3_448_960
    assert resource["weighted_comparison_upper_bound"] == 30_455_371_778_893_216
    assert resource["class_power_key_digest_sha256"] == q011bw.EXPECTED_CLASS_POWER_KEY_DIGEST
    assert resource["group_pool_key_digest_sha256"] == q011bw.EXPECTED_GROUP_POOL_KEY_DIGEST
    assert resource["pair_pool_key_digest_sha256"] == q011bw.EXPECTED_PAIR_POOL_KEY_DIGEST
    assert resource["aggregate_resource_record_digest_sha256"] == (
        q011bw.EXPECTED_RESOURCE_RECORD_DIGEST
    )
    assert resource["full_degree_thirty_four_monomial_list_retained"] is False
    assert resource["product_bound_matrix_constructed"] is False
    assert resource["fourier_coefficient_matrix_constructed"] is False
    assert resource["classification_matrix_constructed"] is False
    assert resource["product_target_relation_evaluation_count"] == 0


def test_q011bw_all_unchanged_resource_limits_pass(q011bw_cycle: dict[str, Any]) -> None:
    assert q011bw_cycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in q011bw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011bw_cycle["resource_feasibility_gates"].values())
    assert q011bw_cycle["failed_validity_order"] == []
    assert q011bw_cycle["failed_resource_limit_order"] == []
    assert q011bw_cycle["resource_decision"] == q011bw.GO_DECISION
    assert q011bw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011bw_cycle["actual_resonance_outcome"] == "not_evaluated"


def test_q011bw_preserves_the_scientific_boundary(q011bw_cycle: dict[str, Any]) -> None:
    theorem = q011bw_cycle["theorem_consequence"]
    assert theorem[
        "degree_thirty_four_coalesced_full_sweep_preregistration_is_resource_supported"
    ]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["q011bv_degree_thirty_three_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "evaluates no degree-thirty-four product-target relation" in q011bw_cycle[
        "claim_boundary"
    ]


def test_q011bw_cycle_has_strict_reproducible_digests(q011bw_cycle: dict[str, Any]) -> None:
    json.dumps(q011bw_cycle, allow_nan=False)
    assert {
        name: q011bw_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011bw_cycle["result_digest_sha256"] == q011bw.q011b._canonical_json_sha256(
        q011bw._result_digest_sections(q011bw_cycle)
    )


def test_q011bw_study_metadata_and_optional_artifact_are_scoped(
    q011bw_study: dict[str, Any],
) -> None:
    assert q011bw_study["schema_version"] == 1
    assert q011bw_study["source"] == source_metadata()
    assert q011bw_study["study_gate"] == "passed"
    assert q011bw_study["resource_decision"] == q011bw.GO_DECISION
    assert q011bw_study["scientific_outcome"] == "not_evaluated"
    scope = q011bw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["degree_thirty_four_external_nonresonance_claim"] is False
    assert scope["actual_degree_thirty_four_external_resonance_ruled_out_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_existence_or_uniqueness_claim"] is False
    json.dumps(q011bw_study, allow_nan=False)

    runner_path = Path(q011bw.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bw_degree34_resource_estimate.json"
    if not artifact_path.exists():
        pytest.skip("Q011bw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bw_degree34_resource_estimate.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["resource_decision"] == q011bw.GO_DECISION
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_evaluated"
    assert artifact["cycle"]["result_digest_sha256"] == q011bw.q011b._canonical_json_sha256(
        q011bw._result_digest_sections(artifact["cycle"])
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
