from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ad_degree10_refined_modulus as q011ad
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ad_study() -> dict[str, Any]:
    return q011ad.run_q011ad_study()


@pytest.fixture(scope="module")
def q011ad_cycle(q011ad_study: dict[str, Any]) -> dict[str, Any]:
    return q011ad_study["cycle"]


def test_q011ad_seals_q011ac_and_all_prior_inputs(
    q011ad_cycle: dict[str, Any],
) -> None:
    sealed = q011ad_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 43
    assert all(sealed["checks"].values())
    assert sealed["prior_q011ac_sealed_input_audit"]["passed"]
    assert sealed["prior_q011ac_sealed_input_audit"]["direct_digest_count"] == 38
    assert tuple(sealed["q011ac"]["digests"]) == q011ad.Q011AC_DIGESTS
    assert sealed["q011ac"]["artifact_sha256"] == q011ad.Q011AC_ARTIFACT_SHA256
    assert sealed["q011ac"]["runner_sha256"] == q011ad.Q011AC_RUNNER_SHA256


def test_q011ad_reconstructs_the_complete_degree_ten_inventory(
    q011ad_cycle: dict[str, Any],
) -> None:
    audit = q011ad_cycle["degree10_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 286
    assert audit["degree_expanded_product_control_count"] == 3003
    assert audit["old_modulus_separated_aggregate_count"] == 281
    assert audit["old_modulus_overlap_aggregate_count"] == 5
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011ad.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011ad.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 32
    assert audit["exact_inventory_digest_sha256"] == (
        "a222f54427d026b09bc3fc1fb53462ea708d3071b66bf6e5e9aebccf4011f38b"
    )


def test_q011ad_extends_the_uniform_envelope_to_68_identifiers(
    q011ad_cycle: dict[str, Any],
) -> None:
    audit = q011ad_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 56
    assert audit["relevant_identifier_count"] == 68
    assert audit["unique_center_modulus_evaluation_count"] == 42
    assert q011ad.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == (
        "ee182424edacab1b422588245109036bbf522c210a05df978d2fc397b5cb317b"
    )


def test_q011ad_enumerates_all_decic_fourier_comparisons(
    q011ad_cycle: dict[str, Any],
) -> None:
    audit = q011ad_cycle["fourier_output_sector_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert tuple(audit["aggregate_monomial_counts"]) == (q011ad.EXPECTED_MONOMIAL_COUNTS)
    assert audit["indexed_monomial_count"] == 339960
    assert audit["sector_compatible_monomial_count"] == 125512
    assert audit["sector_incompatible_monomial_count"] == 214448
    expected_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ad.EXPECTED_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["aggregate_sector_histograms"]) == expected_histograms
    expected_target_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ad.EXPECTED_TARGET_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["external_target_sector_histograms"]) == expected_target_histograms
    assert tuple(audit["aggregate_compatible_comparison_counts"]) == (
        q011ad.EXPECTED_COMPARISON_COUNTS
    )
    assert audit["sector_compatible_comparison_count"] == 466872
    framed = audit["framed_exact_record_digests"]
    assert framed["monomial_record_digest_sha256"] == (
        "2da222f1c15b482ff80805ba1b14ddd0d6d1a2bceb7d3929eb46e82ac11d42c3"
    )
    assert framed["compatible_pair_record_digest_sha256"] == (
        "930937d748264d0026cab92dfa1df9898cc6c039e7b16814eaecd279d336cf3e"
    )


def test_q011ad_separates_all_products_with_the_registered_margin(
    q011ad_cycle: dict[str, Any],
) -> None:
    audit = q011ad_cycle["indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 339960
    assert audit["comparison_record_count"] == 466872
    assert audit["individual_modulus_separation_count"] == 466872
    assert audit["unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["individual_modulus_relation_counts"] == {
        "product_below_target": 44232,
        "target_below_product": 422640,
    }
    minima = [q011ad.q011z._fraction(record) for record in audit["aggregate_minimum_modulus_gaps"]]
    assert minima == pytest.approx(
        [
            7.647290131921562e-4,
            8.247499097190439e-4,
            6.220305127304349e-6,
            7.611385436459371e-4,
            7.02298069679118e-4,
        ]
    )
    assert min(minima) >= q011ad.MINIMUM_MODULUS_GAP
    assert audit["minimum_gap_witness"] == {
        "aggregate_index": 2,
        "selected_type_counts": [0, 8, 2, 0],
        "source_identifiers": [
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=1;center=151",
            "block=1;center=151",
            "block=0;center=149",
            "block=1;center=152",
        ],
        "output_block": 14,
        "target_identifier": "block=14;center=146",
        "individual_modulus_relation": "product_below_target",
        "modulus_gap": audit["minimum_modulus_gap"],
    }


def test_q011ad_exact_product_streams_have_fixed_digests(
    q011ad_cycle: dict[str, Any],
) -> None:
    audit = q011ad_cycle["indexed_modulus_product_audit"]
    framed = audit["framed_exact_record_digests"]
    assert framed["exact_product_record_count"] == 339960
    assert framed["exact_product_record_digest_sha256"] == (
        "722500d189481311cfdd28edf8b17f2a1dc27754969a905d143009d57bbc583d"
    )
    assert framed["exact_comparison_record_count"] == 466872
    assert framed["exact_comparison_record_digest_sha256"] == (
        "142087f4ef4024aa5fa1adb6423719c1dfc98b3d38cd1e026d710d66cb15db55"
    )
    assert audit["compact_product_digest_sha256"] == (
        "621d8cd79bacbdf44e25d3ce0043f3cc7412da805d3038582994b9e586071803"
    )


def test_q011ad_accepts_degree_ten_without_overclaiming(
    q011ad_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ad_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ad_cycle["hypothesis_gates"].values())
    assert q011ad_cycle["study_validity"] == "passed"
    assert q011ad_cycle["hypothesis_outcome"] == "accepted"
    assert q011ad_cycle["scientific_classification"] == q011ad.ACCEPTED_CLASSIFICATION
    theorem = q011ad_cycle["theorem_consequence"]
    assert theorem["degree_ten_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 11))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(11, 91))
    assert not theorem["degrees_11_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ad_cycle["claim_boundary"]
    assert "Q011ae" in q011ad_cycle["next_change"]


def test_q011ad_cycle_has_reproducible_strict_json_digests(
    q011ad_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ad_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("7dd67186b06547d59e08f531192d3c1a58183a5f92121f9567f9aca5ce28303f"),
        "inventory_digest_sha256": (
            "bd9537e8b182fde2ccbd3ff3ae347d85eba673ed93c3e21451069ff1f8b9cac1"
        ),
        "sector_digest_sha256": (
            "440afad1b33c896451a458b62855a71269c1cbef728ea3ecb5b9a75a3fa71d6f"
        ),
        "product_digest_sha256": (
            "29fea1d86fdd06b124df677e3b4cf02a4828355e63e91a7cc14ece63c03c524d"
        ),
        "result_digest_sha256": (
            "e3618fed4c565e76e59653b7affc86c045a617fc463666c7dc468aba302a05f9"
        ),
    }
    assert {name: q011ad_cycle[name] for name in expected} == expected
    assert q011ad_cycle["result_digest_sha256"] == q011ad.q011b._canonical_json_sha256(
        q011ad._result_digest_sections(q011ad_cycle)
    )


def test_q011ad_study_metadata_and_generated_artifact_are_scoped(
    q011ad_study: dict[str, Any],
) -> None:
    assert q011ad_study["schema_version"] == 1
    assert q011ad_study["source"] == source_metadata()
    assert q011ad_study["study_gate"] == "passed"
    assert q011ad_study["scientific_outcome"] == "accepted"
    assert q011ad_study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    scope = q011ad_study["mathematical_scope"]
    assert scope["degree_ten_external_nonresonance_claim"] is True
    assert scope["degrees_11_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ad_study, allow_nan=False)

    runner_path = Path(q011ad.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ad_degree10_refined_modulus.json"
    if not artifact_path.exists():
        pytest.skip("Q011ad artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "018fab41465f4fefcd3df03a05bcd7ad2445f2e840eae66cd8ff0f1d4522f773"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011ad_degree10_refined_modulus.py",
        "sha256": ("666b33f38e773efda70d498c7e4068d108630be31f4be52a64f0640122f95d3b"),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ad.q011b._canonical_json_sha256(q011ad._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
