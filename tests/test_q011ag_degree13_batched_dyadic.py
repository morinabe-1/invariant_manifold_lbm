from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ag_degree13_batched_dyadic as q011ag
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ag_study() -> dict[str, Any]:
    return q011ag.run_q011ag_study()


@pytest.fixture(scope="module")
def q011ag_cycle(q011ag_study: dict[str, Any]) -> dict[str, Any]:
    return q011ag_study["cycle"]


def test_q011ag_seals_q011af_and_all_prior_inputs(
    q011ag_cycle: dict[str, Any],
) -> None:
    sealed = q011ag_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 58
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011af_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 53
    assert tuple(sealed["q011af"]["digests"]) == q011ag.Q011AF_DIGESTS
    assert sealed["q011af"]["artifact_sha256"] == q011ag.Q011AF_ARTIFACT_SHA256
    assert sealed["q011af"]["runner_sha256"] == q011ag.Q011AF_RUNNER_SHA256


def test_q011ag_reconstructs_the_complete_degree_thirteen_inventory(
    q011ag_cycle: dict[str, Any],
) -> None:
    audit = q011ag_cycle["degree13_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 560
    assert audit["degree_expanded_product_control_count"] == 8_568
    assert audit["old_modulus_separated_aggregate_count"] == 516
    assert audit["old_modulus_overlap_aggregate_count"] == 44
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011ag.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011ag.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 44
    assert audit["exact_inventory_digest_sha256"] == q011ag.EXPECTED_INVENTORY_DIGEST


def test_q011ag_extends_the_uniform_envelope_monotonically(
    q011ag_cycle: dict[str, Any],
) -> None:
    audit = q011ag_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 68
    assert audit["relevant_identifier_count"] == 100
    assert audit["checks"]["all_q011af_92_uniform_records_are_preserved_exactly"]
    assert len(audit["new_group_156_identifiers"]) == 8
    assert audit["unique_center_modulus_evaluation_count"] == 60
    assert q011ag.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == q011ag.EXPECTED_UNIFORM_RECORD_DIGEST


def test_q011ag_batched_compression_reproduces_the_q011af_oracle(
    q011ag_cycle: dict[str, Any],
) -> None:
    audit = q011ag_cycle["batched_fourier_multiplicity_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["class_membership_digest_sha256"] == q011ag.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    oracle = audit["q011af_outward_dyadic_oracle"]
    assert oracle["passed"]
    assert all(oracle["checks"].values())
    assert oracle["original_monomial_count"] == 36_596_091
    assert oracle["modulus_signature_count"] == 213_618
    assert oracle["compatible_modulus_signature_count"] == 184_154
    assert oracle["compatible_original_monomial_count"] == 6_904_665
    assert oracle["weighted_comparison_count"] == 13_980_960
    assert oracle["distinct_comparison_count"] == 1_116_256
    assert oracle["weighted_relation_counts"]["overlap"] == 0
    assert oracle["minimum_certified_gap_lower"]["binary64_hex"] == (
        q011ag.EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX
    )


def test_q011ag_exactly_compresses_all_degree_thirteen_monomials(
    q011ag_cycle: dict[str, Any],
) -> None:
    audit = q011ag_cycle["batched_fourier_multiplicity_audit"]
    assert tuple(audit["aggregate_original_monomial_counts"]) == q011ag.EXPECTED_MONOMIAL_COUNTS
    assert audit["original_monomial_count"] == 218_102_520
    assert tuple(audit["aggregate_modulus_signature_counts"]) == q011ag.EXPECTED_SIGNATURE_COUNTS
    assert audit["modulus_signature_count"] == 1_116_561
    assert tuple(audit["aggregate_compatible_modulus_signature_counts"]) == (
        q011ag.EXPECTED_COMPATIBLE_SIGNATURE_COUNTS
    )
    assert audit["compatible_modulus_signature_count"] == 1_004_653
    assert tuple(audit["aggregate_compatible_original_monomial_counts"]) == (
        q011ag.EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
    )
    assert audit["compatible_original_monomial_count"] == 38_119_852
    assert audit["incompatible_original_monomial_count"] == 179_982_668
    assert tuple(audit["aggregate_weighted_comparison_counts"]) == (
        q011ag.EXPECTED_WEIGHTED_COMPARISON_COUNTS
    )
    assert audit["weighted_comparison_count"] == 77_400_104
    assert tuple(audit["aggregate_distinct_comparison_counts"]) == (
        q011ag.EXPECTED_DISTINCT_COMPARISON_COUNTS
    )
    assert audit["distinct_comparison_count"] == 6_290_384
    assert audit["group_signature_record_count"] == 8_818
    assert audit["factorization_digest_sha256"] == q011ag.EXPECTED_FACTORIZATION_DIGEST
    assert audit["aggregate_wave_histogram_digest_sha256"] == (
        q011ag.EXPECTED_WAVE_HISTOGRAM_DIGEST
    )


def test_q011ag_outward_products_are_complete_and_strict(
    q011ag_cycle: dict[str, Any],
) -> None:
    audit = q011ag_cycle["outward_dyadic_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["coefficient_matrix_record_count"] == 162
    assert audit["dyadic_bound_matrix_record_count"] == 44
    assert audit["classification_matrix_record_count"] == 340
    assert audit["coefficient_matrix_digest_sha256"] == (q011ag.EXPECTED_COEFFICIENT_MATRIX_DIGEST)
    assert audit["dyadic_bound_digest_sha256"] == q011ag.EXPECTED_DYADIC_BOUND_DIGEST
    assert audit["classification_matrix_digest_sha256"] == (
        q011ag.EXPECTED_CLASSIFICATION_MATRIX_DIGEST
    )
    assert audit["compact_pilot_digest_sha256"] == q011ag.EXPECTED_COMPACT_PILOT_DIGEST
    assert audit["weighted_comparison_count"] == 77_400_104
    assert audit["distinct_comparison_count"] == 6_290_384
    assert audit["weighted_relation_counts"] == {
        "product_below_target": 47_068_304,
        "target_below_product": 30_331_800,
        "overlap": 0,
    }
    assert audit["distinct_relation_counts"] == {
        "product_below_target": 3_874_124,
        "target_below_product": 2_416_260,
        "overlap": 0,
    }
    assert audit["minimum_certified_gap_lower"]["binary64_hex"] == (
        q011ag.EXPECTED_CERTIFIED_MINIMUM_HEX
    )
    assert audit["maximum_wave_coefficient"] == 213
    assert audit["maximum_crude_int64_dot_product_bound"] < 2**63
    streaming = audit["streaming_contract"]
    assert not streaming["full_original_monomial_list_retained"]
    assert not streaming["full_combined_signature_list_retained"]
    assert not streaming["full_comparison_list_retained"]
    assert streaming["peak_live_combined_signature_count"] == 95_256
    assert streaming["retained_exact_refinement_candidate_count"] == 138


def test_q011ag_refines_every_near_minimum_candidate_exactly(
    q011ag_cycle: dict[str, Any],
) -> None:
    product = q011ag_cycle["outward_dyadic_product_audit"]
    audit = product["exact_refinement_audit"]
    assert audit["candidate_comparison_count"] == 138
    assert audit["exact_global_minimum_tie_count"] == 2
    assert float(q011ag.q011z._fraction(audit["exact_global_minimum_gap"])).hex() == (
        q011ag.EXPECTED_EXACT_MINIMUM_FLOAT_HEX
    )
    assert audit["exact_global_minimum_gap_digest_sha256"] == (q011ag.EXPECTED_EXACT_MINIMUM_DIGEST)
    assert audit["tie_target_identifiers"] == [
        "block=14;center=146",
        "block=3;center=146",
    ]
    witness = audit["canonical_minimum_witness"]
    assert witness["aggregate_index"] == 4
    assert witness["source_modulus_class_counts"] == [
        [0, 0, 0, 0],
        [0, 5],
        [0, 0, 2],
        [0, 0, 0, 6, 0, 0],
    ]
    assert witness["source_identifiers"] == [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=1;center=152",
        "block=1;center=152",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
    ]
    assert witness["wave_multiplicity"] == 3
    assert witness["target_identifier"] == "block=14;center=146"
    assert witness["individual_modulus_relation"] == "product_below_target"
    assert audit["all_other_aggregate_lower_bounds_exceed_the_exact_cutoff"]


def test_q011ag_accepts_degree_thirteen_without_overclaiming(
    q011ag_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ag_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ag_cycle["hypothesis_gates"].values())
    assert q011ag_cycle["study_validity"] == "passed"
    assert q011ag_cycle["hypothesis_outcome"] == "accepted"
    assert q011ag_cycle["scientific_classification"] == q011ag.ACCEPTED_CLASSIFICATION
    theorem = q011ag_cycle["theorem_consequence"]
    assert theorem["uniform_transformed_residual_envelope_is_certified"]
    assert theorem["exact_fourier_multiplicity_and_outward_product_enclosure_is_certified"]
    assert theorem["degree_thirteen_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 14))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(14, 91))
    assert not theorem["degrees_14_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ag_cycle["claim_boundary"]
    assert "Q011ah" in q011ag_cycle["next_change"]


def test_q011ag_cycle_has_reproducible_strict_json_digests(
    q011ag_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ag_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("8a6156a2667469bd0c0666a344e79a04cbc761a3ab0bb134e0853baf6c432aa9"),
        "inventory_digest_sha256": (
            "a901dedf2014c6d6738160890b09bc55118724324b6624494971c1688550f0d7"
        ),
        "compression_digest_sha256": (
            "f117716264aac394b4e2de41bbbf5a0f5868a55bd3c12cc2f00afe4c87181e95"
        ),
        "product_digest_sha256": (
            "2b4b4d8315017fd162dcbf5aebeb4fd7c5c33ec34280564a36a9d8149f9a28f8"
        ),
        "result_digest_sha256": (
            "ebee85b19911947316a3aacf6710e928433e4d155bfc9620b1119003a34faab3"
        ),
    }
    assert {name: q011ag_cycle[name] for name in expected} == expected
    assert q011ag_cycle["result_digest_sha256"] == q011ag.q011b._canonical_json_sha256(
        q011ag._result_digest_sections(q011ag_cycle)
    )


def test_q011ag_study_metadata_and_generated_artifact_are_scoped(
    q011ag_study: dict[str, Any],
) -> None:
    assert q011ag_study["schema_version"] == 1
    assert q011ag_study["source"] == source_metadata()
    assert q011ag_study["study_gate"] == "passed"
    assert q011ag_study["scientific_outcome"] == "accepted"
    arithmetic = q011ag_study["arithmetic_runtime"]
    assert arithmetic["floating_point_used_for_gate_decisions"] is True
    assert arithmetic["floating_point_gate_is_rigorous_interval_logic"] is True
    scope = q011ag_study["mathematical_scope"]
    assert scope["degree_thirteen_external_nonresonance_claim"] is True
    assert scope["degrees_14_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ag_study, allow_nan=False)

    runner_path = Path(q011ag.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ag_degree13_batched_dyadic.json"
    if not artifact_path.exists():
        pytest.skip("Q011ag artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "76c162133c228aecf988fb121dafc86c1dfae5c44cab465772534d2c863393fb"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011ag_degree13_batched_dyadic.py",
        "sha256": ("cf27aba440b291ebfba5f020a1cf77537335520cfdc9490290de836069cfd11f"),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ag.q011b._canonical_json_sha256(q011ag._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
