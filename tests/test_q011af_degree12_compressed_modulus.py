from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011af_degree12_compressed_modulus as q011af
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011af_study() -> dict[str, Any]:
    return q011af.run_q011af_study()


@pytest.fixture(scope="module")
def q011af_cycle(q011af_study: dict[str, Any]) -> dict[str, Any]:
    return q011af_study["cycle"]


def test_q011af_seals_q011ae_and_all_prior_inputs(
    q011af_cycle: dict[str, Any],
) -> None:
    sealed = q011af_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 53
    assert all(sealed["checks"].values())
    assert sealed["prior_q011ae_sealed_input_audit"]["passed"]
    assert sealed["prior_q011ae_sealed_input_audit"]["direct_digest_count"] == 48
    assert tuple(sealed["q011ae"]["digests"]) == q011af.Q011AE_DIGESTS
    assert sealed["q011ae"]["artifact_sha256"] == q011af.Q011AE_ARTIFACT_SHA256
    assert sealed["q011ae"]["runner_sha256"] == q011af.Q011AE_RUNNER_SHA256


def test_q011af_reconstructs_the_complete_degree_twelve_inventory(
    q011af_cycle: dict[str, Any],
) -> None:
    audit = q011af_cycle["degree12_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 455
    assert audit["degree_expanded_product_control_count"] == 6188
    assert audit["old_modulus_separated_aggregate_count"] == 426
    assert audit["old_modulus_overlap_aggregate_count"] == 29
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011af.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011af.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 36
    assert len(audit["exact_inventory_digest_sha256"]) == 64


def test_q011af_extends_the_uniform_envelope_to_92_identifiers(
    q011af_cycle: dict[str, Any],
) -> None:
    audit = q011af_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 60
    assert audit["relevant_identifier_count"] == 92
    assert audit["unique_center_modulus_evaluation_count"] == 56
    assert q011af.q011z._fraction(audit["uniform_radius"]) == Fraction(
        1, 20_000_000
    )
    assert len(audit["uniform_record_digest_sha256"]) == 64


def test_q011af_compression_reproduces_the_q011ae_full_stream_oracle(
    q011af_cycle: dict[str, Any],
) -> None:
    audit = q011af_cycle["multiplicity_compression_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["class_membership_digest_sha256"] == (
        q011af.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    oracle = audit["q011ae_full_stream_compression_oracle"]
    assert oracle["passed"]
    assert all(oracle["checks"].values())
    assert tuple(oracle["aggregate_signature_counts"]) == (
        q011af.Q011AE_ORACLE_SIGNATURE_COUNTS
    )
    assert tuple(oracle["aggregate_compatible_signature_counts"]) == (
        q011af.Q011AE_ORACLE_COMPATIBLE_SIGNATURE_COUNTS
    )
    assert sum(oracle["aggregate_signature_counts"]) == 20_361
    assert sum(oracle["aggregate_compatible_signature_counts"]) == 14_497
    assert oracle["full_stream_monomial_record_count"] == 2_299_104
    assert oracle["full_stream_comparison_record_count"] == 820_492


def test_q011af_exactly_compresses_all_degree_twelve_monomials(
    q011af_cycle: dict[str, Any],
) -> None:
    audit = q011af_cycle["multiplicity_compression_audit"]
    assert tuple(audit["aggregate_original_monomial_counts"]) == (
        q011af.EXPECTED_MONOMIAL_COUNTS
    )
    assert audit["original_monomial_count"] == 36_596_091
    assert tuple(audit["aggregate_modulus_signature_counts"]) == (
        q011af.EXPECTED_SIGNATURE_COUNTS
    )
    assert audit["modulus_signature_count"] == 213_618
    assert tuple(audit["aggregate_compatible_modulus_signature_counts"]) == (
        q011af.EXPECTED_COMPATIBLE_SIGNATURE_COUNTS
    )
    assert audit["compatible_modulus_signature_count"] == 184_154
    assert tuple(audit["aggregate_compatible_original_monomial_counts"]) == (
        q011af.EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
    )
    assert audit["compatible_original_monomial_count"] == 6_904_665
    assert audit["incompatible_original_monomial_count"] == 29_691_426
    assert tuple(audit["aggregate_weighted_comparison_counts"]) == (
        q011af.EXPECTED_WEIGHTED_COMPARISON_COUNTS
    )
    assert audit["weighted_comparison_count"] == 13_980_960
    assert tuple(audit["aggregate_distinct_comparison_counts"]) == (
        q011af.EXPECTED_DISTINCT_COMPARISON_COUNTS
    )
    assert audit["distinct_comparison_count"] == 1_116_256
    assert audit["aggregate_wave_histogram_digest_sha256"] == (
        q011af.EXPECTED_WAVE_HISTOGRAM_DIGEST
    )
    framed = audit["framed_exact_record_digests"]
    assert framed["signature_record_count"] == 213_618
    assert framed["signature_record_digest_sha256"] == (
        q011af.EXPECTED_SIGNATURE_RECORD_DIGEST
    )
    assert framed["distinct_pair_record_count"] == 1_116_256
    streaming = audit["streaming_contract"]
    assert not streaming["full_original_monomial_record_list_retained"]
    assert not streaming["full_combined_signature_record_list_retained"]
    assert streaming["peak_live_combined_signature_record_count"] == 1
    assert streaming["retained_boundary_record_count"] == 58


def test_q011af_separates_all_compressed_products_with_registered_margin(
    q011af_cycle: dict[str, Any],
) -> None:
    audit = q011af_cycle["compressed_indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["compressed_product_record_count"] == 184_154
    assert audit["distinct_comparison_record_count"] == 1_116_256
    assert audit["weighted_comparison_count"] == 13_980_960
    assert audit["weighted_individual_modulus_separation_count"] == 13_980_960
    assert audit["weighted_unresolved_interval_overlap_count"] == 0
    assert audit["distinct_individual_modulus_separation_count"] == 1_116_256
    assert audit["distinct_unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["weighted_individual_modulus_relation_counts"] == {
        "product_below_target": 7_676_904,
        "target_below_product": 6_304_056,
    }
    assert audit["distinct_individual_modulus_relation_counts"] == {
        "product_below_target": 648_656,
        "target_below_product": 467_600,
    }
    minima = [
        float(q011af.q011z._fraction(record))
        for record in audit["aggregate_minimum_modulus_gaps"]
    ]
    assert minima == pytest.approx(
        [
            7.644395795970946e-4,
            8.244604958480301e-4,
            5.198343594182929e-5,
            5.935468013051209e-6,
            6.500319018529858e-5,
            8.112156130773629e-4,
            7.535941667249237e-4,
            5.120425071653584e-4,
            4.5444144857722163e-4,
            3.9684431533124585e-4,
            3.392511071599305e-4,
            1.8030979331334064e-4,
            9.781782330845996e-5,
            4.024499291014315e-5,
            1.6194629345745302e-5,
            7.375968580270664e-5,
            2.2305549481696136e-4,
            3.1507490728910597e-4,
            3.7261958522085044e-4,
            4.301603570775591e-4,
            4.8769720299054147e-4,
            7.288941646490601e-4,
            7.864106420236008e-4,
            7.590017676925743e-4,
            7.020238520476087e-4,
            6.450498146134928e-4,
            3.4925825533753705e-4,
            2.9230826250263423e-4,
            2.3536214597801069e-4,
        ]
    )
    assert min(minima) >= float(q011af.MINIMUM_MODULUS_GAP)
    witness = audit["minimum_gap_witness"]
    assert witness["aggregate_index"] == 3
    assert witness["selected_type_counts"] == [0, 6, 2, 4]
    assert witness["source_modulus_class_counts"] == [
        [0, 0, 0, 0],
        [0, 6],
        [0, 1, 1],
        [0, 0, 0, 4, 0, 0],
    ]
    assert witness["source_identifiers"] == [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=1;center=151",
        "block=0;center=149",
        "block=1;center=152",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
    ]
    assert witness["output_block"] == 14
    assert witness["target_identifier"] == "block=14;center=146"
    assert witness["individual_modulus_relation"] == "product_below_target"
    assert witness["modulus_gap"] == audit["minimum_modulus_gap"]


def test_q011af_four_compressed_streams_are_complete(
    q011af_cycle: dict[str, Any],
) -> None:
    compression = q011af_cycle["multiplicity_compression_audit"]
    product = q011af_cycle["compressed_indexed_modulus_product_audit"]
    compressed_framed = compression["framed_exact_record_digests"]
    product_framed = product["framed_exact_record_digests"]
    assert compressed_framed["signature_record_count"] == 213_618
    assert compressed_framed["distinct_pair_record_count"] == 1_116_256
    assert product_framed["exact_product_record_count"] == 184_154
    assert product_framed["exact_comparison_record_count"] == 1_116_256
    for digest in (
        compressed_framed["signature_record_digest_sha256"],
        compressed_framed["distinct_pair_record_digest_sha256"],
        product_framed["exact_product_record_digest_sha256"],
        product_framed["exact_comparison_record_digest_sha256"],
        compression["compact_compression_digest_sha256"],
        product["compact_product_digest_sha256"],
    ):
        assert len(digest) == 64
    streaming = product["streaming_contract"]
    assert not streaming["full_product_record_list_retained"]
    assert not streaming["full_comparison_record_list_retained"]
    assert streaming["peak_live_product_record_count"] == 1


def test_q011af_accepts_degree_twelve_without_overclaiming(
    q011af_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011af_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011af_cycle["hypothesis_gates"].values())
    assert q011af_cycle["study_validity"] == "passed"
    assert q011af_cycle["hypothesis_outcome"] == "accepted"
    assert q011af_cycle["scientific_classification"] == q011af.ACCEPTED_CLASSIFICATION
    theorem = q011af_cycle["theorem_consequence"]
    assert theorem["multiplicity_compression_is_exact_and_oracle_validated"]
    assert theorem["degree_twelve_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 13))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(13, 91))
    assert not theorem["degrees_13_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011af_cycle["claim_boundary"]
    assert "Q011ag" in q011af_cycle["next_change"]


def test_q011af_cycle_has_reproducible_strict_json_digests(
    q011af_cycle: dict[str, Any],
) -> None:
    json.dumps(q011af_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "inventory_digest_sha256",
        "compression_digest_sha256",
        "product_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011af_cycle[name]) == 64
    assert q011af_cycle["result_digest_sha256"] == q011af.q011b._canonical_json_sha256(
        q011af._result_digest_sections(q011af_cycle)
    )


def test_q011af_study_metadata_and_generated_artifact_are_scoped(
    q011af_study: dict[str, Any],
) -> None:
    assert q011af_study["schema_version"] == 1
    assert q011af_study["source"] == source_metadata()
    assert q011af_study["study_gate"] == "passed"
    assert q011af_study["scientific_outcome"] == "accepted"
    assert q011af_study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    scope = q011af_study["mathematical_scope"]
    assert scope["degree_twelve_external_nonresonance_claim"] is True
    assert scope["degrees_13_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011af_study, allow_nan=False)

    runner_path = Path(q011af.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q011af_degree12_compressed_modulus.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011af artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011af_degree12_compressed_modulus.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011af.q011b._canonical_json_sha256(
            q011af._result_digest_sections(artifact["cycle"])
        )
    )
    json.dumps(artifact, allow_nan=False)
