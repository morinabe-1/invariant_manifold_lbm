from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ai_degree15_dual_outcome as q011ai
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ai_study() -> dict[str, Any]:
    return q011ai.run_q011ai_study()


@pytest.fixture(scope="module")
def q011ai_cycle(q011ai_study: dict[str, Any]) -> dict[str, Any]:
    return q011ai_study["cycle"]


def test_q011ai_seals_q011ah_and_all_prior_inputs(
    q011ai_cycle: dict[str, Any],
) -> None:
    sealed = q011ai_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 68
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011ah_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 63
    assert tuple(sealed["q011ah"]["digests"]) == q011ai.Q011AH_DIGESTS
    assert sealed["q011ah"]["artifact_sha256"] == q011ai.Q011AH_ARTIFACT_SHA256
    assert sealed["q011ah"]["runner_sha256"] == q011ai.Q011AH_RUNNER_SHA256


def test_q011ai_reconstructs_the_complete_degree_fifteen_inventory(
    q011ai_cycle: dict[str, Any],
) -> None:
    audit = q011ai_cycle["degree15_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 816
    assert audit["degree_expanded_product_control_count"] == 15_504
    assert audit["old_modulus_separated_aggregate_count"] == 713
    assert audit["old_modulus_overlap_aggregate_count"] == 103
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert len(audit["overlap_records"]) == 103
    assert all(len(record["external_group_indices"]) == 1 for record in audit["overlap_records"])
    assert tuple(audit["unique_external_group_indices"]) == (q011ai.EXPECTED_EXTERNAL_GROUP_INDICES)
    assert audit["unique_external_target_count"] == 80
    assert audit["exact_inventory_digest_sha256"] == q011ai.EXPECTED_INVENTORY_DIGEST


def test_q011ai_extends_the_uniform_envelope_monotonically(
    q011ai_cycle: dict[str, Any],
) -> None:
    audit = q011ai_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 104
    assert audit["relevant_identifier_count"] == 144
    assert audit["checks"]["all_q011ah_112_uniform_records_are_preserved_exactly"]
    assert len(audit["new_group_152_153_154_identifiers"]) == 32
    assert audit["unique_center_modulus_evaluation_count"] == 83
    assert q011ai.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == q011ai.EXPECTED_UNIFORM_RECORD_DIGEST


def test_q011ai_batched_compression_reproduces_the_q011ah_oracle(
    q011ai_cycle: dict[str, Any],
) -> None:
    audit = q011ai_cycle["batched_fourier_multiplicity_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["class_membership_digest_sha256"] == q011ai.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    oracle = audit["q011ah_outward_dyadic_oracle"]
    assert oracle["passed"]
    assert all(oracle["checks"].values())
    assert oracle["original_monomial_count"] == 893_043_240
    assert oracle["modulus_signature_count"] == 4_091_730
    assert oracle["compatible_modulus_signature_count"] == 3_543_001
    assert oracle["compatible_original_monomial_count"] == 152_292_218
    assert oracle["weighted_comparison_count"] == 310_135_908
    assert oracle["distinct_comparison_count"] == 21_891_420
    assert oracle["weighted_relation_counts"]["overlap"] == 0
    assert oracle["minimum_certified_gap_lower"]["binary64_hex"] == (
        q011ai.EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX
    )


def test_q011ai_seals_all_six_count_vectors_and_totals(
    q011ai_cycle: dict[str, Any],
) -> None:
    audit = q011ai_cycle["batched_fourier_multiplicity_audit"]
    assert tuple(audit["count_vectors"]) == q011ai.COUNT_VECTOR_KEYS
    assert all(len(audit["count_vectors"][key]) == 103 for key in q011ai.COUNT_VECTOR_KEYS)
    assert audit["count_vector_digest_sha256"] == q011ai.EXPECTED_COUNT_VECTOR_DIGEST
    assert audit["aggregate_record_digest_sha256"] == q011ai.EXPECTED_AGGREGATE_RECORD_DIGEST
    assert audit["original_monomial_count"] == 2_813_485_588
    assert audit["modulus_signature_count"] == 12_188_436
    assert audit["compatible_modulus_signature_count"] == 10_399_739
    assert audit["compatible_original_monomial_count"] == 529_597_352
    assert audit["incompatible_original_monomial_count"] == 2_283_888_236
    assert audit["weighted_comparison_count"] == 1_103_228_296
    assert audit["distinct_comparison_count"] == 61_611_952
    assert audit["group_signature_record_count"] == 42_095
    assert audit["factorization_digest_sha256"] == q011ai.EXPECTED_FACTORIZATION_DIGEST
    assert audit["aggregate_wave_histogram_digest_sha256"] == (
        q011ai.EXPECTED_WAVE_HISTOGRAM_DIGEST
    )


def test_q011ai_outward_products_are_complete_and_strict(
    q011ai_cycle: dict[str, Any],
) -> None:
    audit = q011ai_cycle["outward_dyadic_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["coefficient_matrix_record_count"] == 383
    assert audit["dyadic_bound_matrix_record_count"] == 103
    assert audit["classification_matrix_record_count"] == 816
    assert audit["coefficient_matrix_digest_sha256"] == (q011ai.EXPECTED_COEFFICIENT_MATRIX_DIGEST)
    assert audit["dyadic_bound_digest_sha256"] == q011ai.EXPECTED_DYADIC_BOUND_DIGEST
    assert audit["classification_matrix_digest_sha256"] == (
        q011ai.EXPECTED_CLASSIFICATION_MATRIX_DIGEST
    )
    assert audit["compact_pilot_digest_sha256"] == q011ai.EXPECTED_COMPACT_PILOT_DIGEST
    assert audit["weighted_comparison_count"] == 1_103_228_296
    assert audit["distinct_comparison_count"] == 61_611_952
    assert audit["weighted_relation_counts"] == {
        "product_below_target": 669_413_248,
        "target_below_product": 433_815_048,
        "overlap": 0,
    }
    assert audit["distinct_relation_counts"] == {
        "product_below_target": 37_189_092,
        "target_below_product": 24_422_860,
        "overlap": 0,
    }
    assert audit["minimum_certified_gap_lower"]["binary64_hex"] == (
        q011ai.EXPECTED_CERTIFIED_MINIMUM_HEX
    )
    assert audit["maximum_wave_coefficient"] == 839
    assert audit["maximum_crude_int64_dot_product_bound"] == 6_528
    streaming = audit["streaming_contract"]
    assert not streaming["full_original_monomial_list_retained"]
    assert not streaming["full_combined_signature_list_retained"]
    assert not streaming["full_comparison_list_retained"]
    assert streaming["peak_live_combined_signature_count"] == 532_224
    assert streaming["retained_exact_refinement_candidate_count"] == 16


def test_q011ai_refines_the_minimum_and_rejects_only_the_legacy_margin(
    q011ai_cycle: dict[str, Any],
) -> None:
    product = q011ai_cycle["outward_dyadic_product_audit"]
    audit = product["exact_refinement_audit"]
    assert audit["candidate_comparison_count"] == 16
    assert audit["candidate_exact_record_digest_sha256"] == (q011ai.EXPECTED_EXACT_CANDIDATE_DIGEST)
    assert audit["exact_global_minimum_tie_count"] == 2
    assert float(q011ai.q011z._fraction(audit["exact_global_minimum_gap"])).hex() == (
        q011ai.EXPECTED_EXACT_MINIMUM_FLOAT_HEX
    )
    assert audit["exact_global_minimum_gap_digest_sha256"] == (q011ai.EXPECTED_EXACT_MINIMUM_DIGEST)
    assert audit["tie_target_identifiers"] == ["block=13;center=1", "block=4;center=1"]
    witness = audit["canonical_minimum_witness"]
    assert witness["aggregate_index"] == 31
    assert witness["source_modulus_class_counts"] == [
        [3, 0, 0, 0],
        [0, 3],
        [0, 0, 9],
        [0, 0, 0, 0, 0, 0],
    ]
    assert witness["source_identifiers"] == [
        "block=16;center=142",
        "block=1;center=142",
        "block=1;center=142",
        "block=1;center=151",
        "block=1;center=151",
        "block=1;center=151",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
        "block=1;center=152",
    ]
    assert witness["wave_multiplicity"] == 3
    assert witness["target_identifier"] == "block=13;center=1"
    assert witness["individual_modulus_relation"] == "product_below_target"
    assert audit["all_other_aggregate_lower_bounds_exceed_the_exact_cutoff"]

    legacy = product["legacy_margin_benchmark_audit"]
    assert not legacy["benchmark_satisfied"]
    assert legacy["outcome"] == "rejected"
    assert legacy["registered_rejection_reproduced"]
    assert not legacy["replacement_margin_threshold_was_introduced"]


def test_q011ai_accepts_nonresonance_and_rejects_the_legacy_benchmark(
    q011ai_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ai_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ai_cycle["hypothesis_gates"].values())
    assert q011ai_cycle["study_validity"] == "passed"
    assert q011ai_cycle["hypothesis_outcome"] == "accepted"
    assert q011ai_cycle["legacy_margin_outcome"] == "rejected"
    assert q011ai_cycle["scientific_classification"] == (q011ai.COMBINED_ACCEPTED_CLASSIFICATION)
    theorem = q011ai_cycle["theorem_consequence"]
    assert theorem["degree_fifteen_external_nonresonance_is_certified"]
    assert not theorem["legacy_5e_6_certified_margin_benchmark_is_satisfied"]
    assert theorem["legacy_5e_6_certified_margin_benchmark_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 16))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(16, 91))
    assert not theorem["degrees_16_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ai_cycle["claim_boundary"]
    assert "Q011aj" in q011ai_cycle["next_change"]


def test_q011ai_cycle_has_reproducible_strict_json_digests(
    q011ai_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ai_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("54f599a25c3bde94887c47f93f926e79798151877548f0ea98c29d73d0c67c0e"),
        "inventory_digest_sha256": (
            "14b04d7d05d719e112661f69009224169e9722626991f11ebd43aa456c2043a5"
        ),
        "compression_digest_sha256": (
            "7d74819f4cfcd5a00ce04e3e55c086dd7a88035ca2ba7b09a387988514b89225"
        ),
        "product_digest_sha256": (
            "2b4fd586a9f478df3e9f4f007badceca293b0658388e9cde2a2d60e2a8d3adcf"
        ),
        "result_digest_sha256": (
            "7981bff291a3aa5b5c518b189047c80fb73711bb2c6dd23aad55668ef96eda91"
        ),
    }
    assert {name: q011ai_cycle[name] for name in expected} == expected
    assert q011ai_cycle["result_digest_sha256"] == q011ai.q011b._canonical_json_sha256(
        q011ai._result_digest_sections(q011ai_cycle)
    )


def test_q011ai_study_metadata_and_generated_artifact_are_scoped(
    q011ai_study: dict[str, Any],
) -> None:
    assert q011ai_study["schema_version"] == 1
    assert q011ai_study["source"] == source_metadata()
    assert q011ai_study["study_gate"] == "passed"
    assert q011ai_study["scientific_outcome"] == "accepted"
    assert q011ai_study["legacy_margin_outcome"] == "rejected"
    arithmetic = q011ai_study["arithmetic_runtime"]
    assert arithmetic["floating_point_used_for_gate_decisions"] is True
    assert arithmetic["floating_point_gate_is_rigorous_interval_logic"] is True
    scope = q011ai_study["mathematical_scope"]
    assert scope["degree_fifteen_external_nonresonance_claim"] is True
    assert scope["legacy_5e_6_margin_claim"] is False
    assert scope["degrees_16_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ai_study, allow_nan=False)

    runner_path = Path(q011ai.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ai_degree15_dual_outcome.json"
    if not artifact_path.exists():
        pytest.skip("Q011ai artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["legacy_margin_outcome"] == "rejected"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ai.q011b._canonical_json_sha256(q011ai._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
