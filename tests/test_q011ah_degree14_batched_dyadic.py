from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ah_degree14_batched_dyadic as q011ah
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ah_study() -> dict[str, Any]:
    return q011ah.run_q011ah_study()


@pytest.fixture(scope="module")
def q011ah_cycle(q011ah_study: dict[str, Any]) -> dict[str, Any]:
    return q011ah_study["cycle"]


def test_q011ah_seals_q011ag_and_all_prior_inputs(
    q011ah_cycle: dict[str, Any],
) -> None:
    sealed = q011ah_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 63
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011ag_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 58
    assert tuple(sealed["q011ag"]["digests"]) == q011ah.Q011AG_DIGESTS
    assert sealed["q011ag"]["artifact_sha256"] == q011ah.Q011AG_ARTIFACT_SHA256
    assert sealed["q011ag"]["runner_sha256"] == q011ah.Q011AG_RUNNER_SHA256


def test_q011ah_reconstructs_the_complete_degree_fourteen_inventory(
    q011ah_cycle: dict[str, Any],
) -> None:
    audit = q011ah_cycle["degree14_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 680
    assert audit["degree_expanded_product_control_count"] == 11_628
    assert audit["old_modulus_separated_aggregate_count"] == 617
    assert audit["old_modulus_overlap_aggregate_count"] == 63
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011ah.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011ah.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 56
    assert audit["exact_inventory_digest_sha256"] == q011ah.EXPECTED_INVENTORY_DIGEST


def test_q011ah_extends_the_uniform_envelope_monotonically(
    q011ah_cycle: dict[str, Any],
) -> None:
    audit = q011ah_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 80
    assert audit["relevant_identifier_count"] == 112
    assert audit["checks"]["all_q011ag_100_uniform_records_are_preserved_exactly"]
    assert len(audit["new_group_157_158_identifiers"]) == 12
    assert audit["unique_center_modulus_evaluation_count"] == 67
    assert q011ah.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == q011ah.EXPECTED_UNIFORM_RECORD_DIGEST


def test_q011ah_batched_compression_reproduces_the_q011ag_oracle(
    q011ah_cycle: dict[str, Any],
) -> None:
    audit = q011ah_cycle["batched_fourier_multiplicity_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["class_membership_digest_sha256"] == q011ah.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    oracle = audit["q011ag_outward_dyadic_oracle"]
    assert oracle["passed"]
    assert all(oracle["checks"].values())
    assert oracle["original_monomial_count"] == 218_102_520
    assert oracle["modulus_signature_count"] == 1_116_561
    assert oracle["compatible_modulus_signature_count"] == 1_004_653
    assert oracle["compatible_original_monomial_count"] == 38_119_852
    assert oracle["weighted_comparison_count"] == 77_400_104
    assert oracle["distinct_comparison_count"] == 6_290_384
    assert oracle["weighted_relation_counts"]["overlap"] == 0
    assert oracle["minimum_certified_gap_lower"]["binary64_hex"] == (
        q011ah.EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX
    )


def test_q011ah_exactly_compresses_all_degree_fourteen_monomials(
    q011ah_cycle: dict[str, Any],
) -> None:
    audit = q011ah_cycle["batched_fourier_multiplicity_audit"]
    assert tuple(audit["aggregate_original_monomial_counts"]) == q011ah.EXPECTED_MONOMIAL_COUNTS
    assert audit["original_monomial_count"] == 893_043_240
    assert tuple(audit["aggregate_modulus_signature_counts"]) == q011ah.EXPECTED_SIGNATURE_COUNTS
    assert audit["modulus_signature_count"] == 4_091_730
    assert tuple(audit["aggregate_compatible_modulus_signature_counts"]) == (
        q011ah.EXPECTED_COMPATIBLE_SIGNATURE_COUNTS
    )
    assert audit["compatible_modulus_signature_count"] == 3_543_001
    assert tuple(audit["aggregate_compatible_original_monomial_counts"]) == (
        q011ah.EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
    )
    assert audit["compatible_original_monomial_count"] == 152_292_218
    assert audit["incompatible_original_monomial_count"] == 740_751_022
    assert tuple(audit["aggregate_weighted_comparison_counts"]) == (
        q011ah.EXPECTED_WEIGHTED_COMPARISON_COUNTS
    )
    assert audit["weighted_comparison_count"] == 310_135_908
    assert tuple(audit["aggregate_distinct_comparison_counts"]) == (
        q011ah.EXPECTED_DISTINCT_COMPARISON_COUNTS
    )
    assert audit["distinct_comparison_count"] == 21_891_420
    assert audit["group_signature_record_count"] == 19_440
    assert audit["factorization_digest_sha256"] == q011ah.EXPECTED_FACTORIZATION_DIGEST
    assert audit["aggregate_wave_histogram_digest_sha256"] == (
        q011ah.EXPECTED_WAVE_HISTOGRAM_DIGEST
    )


def test_q011ah_outward_products_are_complete_and_strict(
    q011ah_cycle: dict[str, Any],
) -> None:
    audit = q011ah_cycle["outward_dyadic_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["coefficient_matrix_record_count"] == 232
    assert audit["dyadic_bound_matrix_record_count"] == 63
    assert audit["classification_matrix_record_count"] == 480
    assert audit["coefficient_matrix_digest_sha256"] == (q011ah.EXPECTED_COEFFICIENT_MATRIX_DIGEST)
    assert audit["dyadic_bound_digest_sha256"] == q011ah.EXPECTED_DYADIC_BOUND_DIGEST
    assert audit["classification_matrix_digest_sha256"] == (
        q011ah.EXPECTED_CLASSIFICATION_MATRIX_DIGEST
    )
    assert audit["compact_pilot_digest_sha256"] == q011ah.EXPECTED_COMPACT_PILOT_DIGEST
    assert audit["weighted_comparison_count"] == 310_135_908
    assert audit["distinct_comparison_count"] == 21_891_420
    assert audit["weighted_relation_counts"] == {
        "product_below_target": 204_194_352,
        "target_below_product": 105_941_556,
        "overlap": 0,
    }
    assert audit["distinct_relation_counts"] == {
        "product_below_target": 14_247_584,
        "target_below_product": 7_643_836,
        "overlap": 0,
    }
    assert audit["minimum_certified_gap_lower"]["binary64_hex"] == (
        q011ah.EXPECTED_CERTIFIED_MINIMUM_HEX
    )
    assert audit["maximum_wave_coefficient"] == 548
    assert audit["maximum_crude_int64_dot_product_bound"] == 4_794
    streaming = audit["streaming_contract"]
    assert not streaming["full_original_monomial_list_retained"]
    assert not streaming["full_combined_signature_list_retained"]
    assert not streaming["full_comparison_list_retained"]
    assert streaming["peak_live_combined_signature_count"] == 254_016
    assert streaming["retained_exact_refinement_candidate_count"] == 278


def test_q011ah_refines_every_near_minimum_candidate_exactly(
    q011ah_cycle: dict[str, Any],
) -> None:
    product = q011ah_cycle["outward_dyadic_product_audit"]
    audit = product["exact_refinement_audit"]
    assert audit["candidate_comparison_count"] == 278
    assert audit["candidate_exact_record_digest_sha256"] == (q011ah.EXPECTED_EXACT_CANDIDATE_DIGEST)
    assert audit["exact_global_minimum_tie_count"] == 2
    assert float(q011ah.q011z._fraction(audit["exact_global_minimum_gap"])).hex() == (
        q011ah.EXPECTED_EXACT_MINIMUM_FLOAT_HEX
    )
    assert audit["exact_global_minimum_gap_digest_sha256"] == (q011ah.EXPECTED_EXACT_MINIMUM_DIGEST)
    assert audit["tie_target_identifiers"] == [
        "block=14;center=146",
        "block=3;center=146",
    ]
    witness = audit["canonical_minimum_witness"]
    assert witness["aggregate_index"] == 5
    assert witness["source_modulus_class_counts"] == [
        [0, 0, 0, 0],
        [0, 4],
        [0, 1, 1],
        [0, 0, 0, 8, 0, 0],
    ]
    assert witness["source_identifiers"] == [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=0;center=149",
        "block=1;center=152",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
    ]
    assert witness["wave_multiplicity"] == 2
    assert witness["target_identifier"] == "block=14;center=146"
    assert witness["individual_modulus_relation"] == "product_below_target"
    assert audit["all_other_aggregate_lower_bounds_exceed_the_exact_cutoff"]


def test_q011ah_accepts_degree_fourteen_without_overclaiming(
    q011ah_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ah_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ah_cycle["hypothesis_gates"].values())
    assert q011ah_cycle["study_validity"] == "passed"
    assert q011ah_cycle["hypothesis_outcome"] == "accepted"
    assert q011ah_cycle["scientific_classification"] == q011ah.ACCEPTED_CLASSIFICATION
    theorem = q011ah_cycle["theorem_consequence"]
    assert theorem["uniform_transformed_residual_envelope_is_certified"]
    assert theorem["exact_fourier_multiplicity_and_outward_product_enclosure_is_certified"]
    assert theorem["degree_fourteen_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 15))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(15, 91))
    assert not theorem["degrees_15_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ah_cycle["claim_boundary"]
    assert "Q011ai" in q011ah_cycle["next_change"]


def test_q011ah_cycle_has_reproducible_strict_json_digests(
    q011ah_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ah_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("f9b56d7c946e87637efb31736eeccb12bfba8649dc174eb625f461fe9fd07be1"),
        "inventory_digest_sha256": (
            "84470f689b8d102fa3710a392444a7624ff00b6e5581be767155b27069693d80"
        ),
        "compression_digest_sha256": (
            "8968069139fcfa41bed5128d8f561afd3f68eab2bd48035243d2b7736951345b"
        ),
        "product_digest_sha256": (
            "370e36d8d088b6e4900c312ff16dc7656f250f1b67420d729936ad88ac971558"
        ),
        "result_digest_sha256": (
            "f16b601ad207edd7b9bf19152385d304148a1b9f767ab1d087af039ef49177fa"
        ),
    }
    assert {name: q011ah_cycle[name] for name in expected} == expected
    assert q011ah_cycle["result_digest_sha256"] == q011ah.q011b._canonical_json_sha256(
        q011ah._result_digest_sections(q011ah_cycle)
    )


def test_q011ah_study_metadata_and_generated_artifact_are_scoped(
    q011ah_study: dict[str, Any],
) -> None:
    assert q011ah_study["schema_version"] == 1
    assert q011ah_study["source"] == source_metadata()
    assert q011ah_study["study_gate"] == "passed"
    assert q011ah_study["scientific_outcome"] == "accepted"
    arithmetic = q011ah_study["arithmetic_runtime"]
    assert arithmetic["floating_point_used_for_gate_decisions"] is True
    assert arithmetic["floating_point_gate_is_rigorous_interval_logic"] is True
    scope = q011ah_study["mathematical_scope"]
    assert scope["degree_fourteen_external_nonresonance_claim"] is True
    assert scope["degrees_15_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ah_study, allow_nan=False)

    runner_path = Path(q011ah.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ah_degree14_batched_dyadic.json"
    if not artifact_path.exists():
        pytest.skip("Q011ah artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ah.q011b._canonical_json_sha256(q011ah._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
