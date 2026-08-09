from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ae_degree11_streaming_modulus as q011ae
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ae_study() -> dict[str, Any]:
    return q011ae.run_q011ae_study()


@pytest.fixture(scope="module")
def q011ae_cycle(q011ae_study: dict[str, Any]) -> dict[str, Any]:
    return q011ae_study["cycle"]


def test_q011ae_seals_q011ad_and_all_prior_inputs(
    q011ae_cycle: dict[str, Any],
) -> None:
    sealed = q011ae_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 48
    assert all(sealed["checks"].values())
    assert sealed["prior_q011ad_sealed_input_audit"]["passed"]
    assert sealed["prior_q011ad_sealed_input_audit"]["direct_digest_count"] == 43
    assert tuple(sealed["q011ad"]["digests"]) == q011ae.Q011AD_DIGESTS
    assert sealed["q011ad"]["artifact_sha256"] == q011ae.Q011AD_ARTIFACT_SHA256
    assert sealed["q011ad"]["runner_sha256"] == q011ae.Q011AD_RUNNER_SHA256


def test_q011ae_reconstructs_the_complete_degree_eleven_inventory(
    q011ae_cycle: dict[str, Any],
) -> None:
    audit = q011ae_cycle["degree11_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 364
    assert audit["degree_expanded_product_control_count"] == 4368
    assert audit["old_modulus_separated_aggregate_count"] == 350
    assert audit["old_modulus_overlap_aggregate_count"] == 14
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011ae.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011ae.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 28
    assert audit["exact_inventory_digest_sha256"] == (
        "a42cb2a862f2c33db629374e5ad479ddf33275a3fbbc5cb392a8d2d830408f6a"
    )


def test_q011ae_extends_the_uniform_envelope_to_84_identifiers(
    q011ae_cycle: dict[str, Any],
) -> None:
    audit = q011ae_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 52
    assert audit["relevant_identifier_count"] == 84
    assert audit["unique_center_modulus_evaluation_count"] == 50
    assert q011ae.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == (
        "b099c8294d2ff14bbf36886f085e39cddffaaf2220b9c0e47206404cee023391"
    )


def test_q011ae_streams_all_undecic_fourier_records(
    q011ae_cycle: dict[str, Any],
) -> None:
    audit = q011ae_cycle["fourier_output_sector_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert tuple(audit["aggregate_monomial_counts"]) == q011ae.EXPECTED_MONOMIAL_COUNTS
    assert audit["indexed_monomial_count"] == 2_299_104
    assert tuple(audit["aggregate_sector_compatible_monomial_counts"]) == (
        q011ae.EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
    )
    assert audit["sector_compatible_monomial_count"] == 383_062
    assert audit["sector_incompatible_monomial_count"] == 1_916_042
    expected_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ae.EXPECTED_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["aggregate_sector_histograms"]) == expected_histograms
    expected_target_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ae.EXPECTED_TARGET_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["external_target_sector_histograms"]) == expected_target_histograms
    assert tuple(audit["aggregate_compatible_comparison_counts"]) == (
        q011ae.EXPECTED_COMPARISON_COUNTS
    )
    assert audit["sector_compatible_comparison_count"] == 820_492
    assert audit["fourier_empty_aggregate_indices"] == [11, 12, 13]
    streaming = audit["streaming_contract"]
    assert not streaming["full_monomial_record_list_retained"]
    assert not streaming["full_compatible_pair_record_list_retained"]
    assert streaming["peak_live_monomial_record_count"] == 1
    assert streaming["retained_boundary_record_count"] == 28


def test_q011ae_separates_all_streamed_products_with_registered_margin(
    q011ae_cycle: dict[str, Any],
) -> None:
    audit = q011ae_cycle["indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["compatible_product_record_count"] == 383_062
    assert audit["product_record_count"] == 383_062
    assert audit["fourier_incompatible_product_interval_count"] == 0
    assert audit["comparison_record_count"] == 820_492
    assert audit["individual_modulus_separation_count"] == 820_492
    assert audit["unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["individual_modulus_relation_counts"] == {
        "product_below_target": 630_112,
        "target_below_product": 190_380,
    }
    minima = [
        None if record is None else float(q011ae.q011z._fraction(record))
        for record in audit["aggregate_minimum_modulus_gaps"]
    ]
    assert minima[:11] == pytest.approx(
        [
            7.64584310040286e-4,
            8.24605200339048e-4,
            6.077884164345725e-6,
            5.119881515674461e-4,
            4.543870966834832e-4,
            9.7763494348257e-5,
            4.019066765229879e-5,
            3.1521364059060536e-4,
            3.727583244935288e-4,
            7.290328299624059e-4,
            7.865493133051993e-4,
        ]
    )
    assert minima[11:] == [None, None, None]
    assert min(value for value in minima if value is not None) >= float(
        q011ae.MINIMUM_MODULUS_GAP
    )
    assert audit["minimum_gap_witness"] == {
        "aggregate_index": 2,
        "selected_type_counts": [0, 7, 2, 2],
        "source_identifiers": [
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=1;center=151",
            "block=1;center=152",
            "block=1;center=152",
            "block=0;center=147",
            "block=0;center=147",
        ],
        "output_block": 14,
        "target_identifier": "block=14;center=146",
        "individual_modulus_relation": "product_below_target",
        "modulus_gap": audit["minimum_modulus_gap"],
    }


def test_q011ae_four_exact_streams_are_complete_and_constant_memory(
    q011ae_cycle: dict[str, Any],
) -> None:
    sector = q011ae_cycle["fourier_output_sector_audit"]
    product = q011ae_cycle["indexed_modulus_product_audit"]
    sector_framed = sector["framed_exact_record_digests"]
    product_framed = product["framed_exact_record_digests"]
    assert sector_framed["monomial_record_count"] == 2_299_104
    assert sector_framed["monomial_record_digest_sha256"] == (
        "34be940e350535f5e8461033e9fda32f5c065c8545f561f1652c10af26e473c9"
    )
    assert sector_framed["compatible_pair_record_count"] == 820_492
    assert sector_framed["compatible_pair_record_digest_sha256"] == (
        "314a2408cc7719b64a8d452a54b45020b50b1ff08731b0140dc1bbb30a24d9df"
    )
    assert product_framed["exact_product_record_count"] == 383_062
    assert product_framed["exact_product_record_digest_sha256"] == (
        "2260b7904ec46a76f4da0e7ec83e0af84d763adb28c2985f3ca4140915015fe3"
    )
    assert product_framed["exact_comparison_record_count"] == 820_492
    assert product_framed["exact_comparison_record_digest_sha256"] == (
        "cdca67557036eddb40900058d0501cf622cfd811e7bbf80cb972997395edcbaa"
    )
    assert sector["compact_sector_digest_sha256"] == (
        "832b9c3035f0cc28cfed683b6f779f04fe85693c7d137d64b287ec1dac69d077"
    )
    assert product["compact_product_digest_sha256"] == (
        "0cd3f3a92881776baf5d298f282985fee66d0f26d8221373db10ca3dfbd34029"
    )
    streaming = product["streaming_contract"]
    assert not streaming["full_product_record_list_retained"]
    assert not streaming["full_comparison_record_list_retained"]
    assert streaming["peak_live_product_record_count"] == 1


def test_q011ae_accepts_degree_eleven_without_overclaiming(
    q011ae_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ae_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ae_cycle["hypothesis_gates"].values())
    assert q011ae_cycle["study_validity"] == "passed"
    assert q011ae_cycle["hypothesis_outcome"] == "accepted"
    assert q011ae_cycle["scientific_classification"] == q011ae.ACCEPTED_CLASSIFICATION
    theorem = q011ae_cycle["theorem_consequence"]
    assert theorem["degree_eleven_external_nonresonance_is_certified"]
    assert theorem["eleven_overlaps_are_eliminated_by_streamed_indexed_products"]
    assert theorem["three_overlaps_are_eliminated_by_exact_fourier_structure"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 12))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(12, 91))
    assert not theorem["degrees_12_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ae_cycle["claim_boundary"]
    assert "Q011af" in q011ae_cycle["next_change"]


def test_q011ae_cycle_has_reproducible_strict_json_digests(
    q011ae_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ae_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "c3a18a891f037c01134871aa876441df4c56bb6ce2b1657420b54fa0ae72fc99"
        ),
        "inventory_digest_sha256": (
            "261284bc4cd18048228af34a1897ba00b89b930fd118afc3f7ce4dba77bf380d"
        ),
        "sector_digest_sha256": (
            "afeea956028309574d5f23c5a8da10c427b981bf7d54c8194265f75de8370d11"
        ),
        "product_digest_sha256": (
            "40024743d9a6e193461dc5a7eb7821356b14da2a54793d126afe9b8ec2e58921"
        ),
        "result_digest_sha256": (
            "90223809a06a85733d36c53b7278c9ba36e83ce2bc49a87b090945b26a638560"
        ),
    }
    assert {name: q011ae_cycle[name] for name in expected} == expected
    assert q011ae_cycle["result_digest_sha256"] == q011ae.q011b._canonical_json_sha256(
        q011ae._result_digest_sections(q011ae_cycle)
    )


def test_q011ae_study_metadata_and_generated_artifact_are_scoped(
    q011ae_study: dict[str, Any],
) -> None:
    assert q011ae_study["schema_version"] == 1
    assert q011ae_study["source"] == source_metadata()
    assert q011ae_study["study_gate"] == "passed"
    assert q011ae_study["scientific_outcome"] == "accepted"
    assert q011ae_study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    scope = q011ae_study["mathematical_scope"]
    assert scope["degree_eleven_external_nonresonance_claim"] is True
    assert scope["degrees_12_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ae_study, allow_nan=False)

    runner_path = Path(q011ae.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ae_degree11_streaming_modulus.json"
    if not artifact_path.exists():
        pytest.skip("Q011ae artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "7da61f31c9a00017c2ab0665bb58b75b157f4b7f0ffad1194f07cac4ed51ff71"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011ae_degree11_streaming_modulus.py",
        "sha256": (
            "2bc97a29a1ae73924a61059c7f1de7b96e35b325479874cf28325946aa7e4286"
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ae.q011b._canonical_json_sha256(
            q011ae._result_digest_sections(artifact["cycle"])
        )
    )
    json.dumps(artifact, allow_nan=False)
