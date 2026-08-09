from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ab_degree8_refined_modulus as q011ab
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ab_study() -> dict[str, Any]:
    return q011ab.run_q011ab_study()


@pytest.fixture(scope="module")
def q011ab_cycle(q011ab_study: dict[str, Any]) -> dict[str, Any]:
    return q011ab_study["cycle"]


def test_q011ab_seals_q011aa_and_all_prior_inputs(
    q011ab_cycle: dict[str, Any],
) -> None:
    sealed = q011ab_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 33
    assert all(sealed["checks"].values())
    assert sealed["prior_q011aa_sealed_input_audit"]["passed"]
    assert sealed["prior_q011aa_sealed_input_audit"]["direct_digest_count"] == 28
    assert tuple(sealed["q011aa"]["digests"]) == q011ab.Q011AA_DIGESTS
    assert sealed["q011aa"]["artifact_sha256"] == q011ab.Q011AA_ARTIFACT_SHA256
    assert sealed["q011aa"]["runner_sha256"] == q011ab.Q011AA_RUNNER_SHA256


def test_q011ab_reconstructs_the_complete_degree_eight_inventory(
    q011ab_cycle: dict[str, Any],
) -> None:
    audit = q011ab_cycle["degree8_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 165
    assert audit["degree_expanded_product_control_count"] == 1287
    assert audit["old_modulus_separated_aggregate_count"] == 158
    assert audit["old_modulus_overlap_aggregate_count"] == 7
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011ab.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011ab.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 20
    assert audit["exact_inventory_digest_sha256"] == (
        "806add7159103ae1ffad9a36e9d1dcf2cd25f9f9061dc97e0aded8142b96304b"
    )


def test_q011ab_extends_the_uniform_envelope_to_36_identifiers(
    q011ab_cycle: dict[str, Any],
) -> None:
    audit = q011ab_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [1, 2, 3]
    assert audit["relevant_identifier_count"] == 36
    assert audit["unique_center_modulus_evaluation_count"] == 25
    assert q011ab.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == (
        "bf8b726536270d68abaf4eb3a5675efd513ff479ad076ef9a63c5648b908ff8f"
    )


def test_q011ab_enumerates_all_octic_fourier_comparisons(
    q011ab_cycle: dict[str, Any],
) -> None:
    audit = q011ab_cycle["fourier_output_sector_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert tuple(audit["aggregate_monomial_counts"]) == (q011ab.EXPECTED_MONOMIAL_COUNTS)
    assert audit["indexed_monomial_count"] == 110352
    assert audit["sector_compatible_monomial_count"] == 31479
    assert audit["sector_incompatible_monomial_count"] == 78873
    expected_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ab.EXPECTED_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["aggregate_sector_histograms"]) == expected_histograms
    expected_target_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ab.EXPECTED_TARGET_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["external_target_sector_histograms"]) == expected_target_histograms
    assert tuple(audit["aggregate_compatible_comparison_counts"]) == (
        q011ab.EXPECTED_COMPARISON_COUNTS
    )
    assert audit["sector_compatible_comparison_count"] == 86176
    framed = audit["framed_exact_record_digests"]
    assert framed["monomial_record_digest_sha256"] == (
        "d9f73a519d424484597bd7a17496ba0315f87c1bd7e8116c0bb588469c90e1e4"
    )
    assert framed["compatible_pair_record_digest_sha256"] == (
        "c1145c61b8e044d445fd4c56108d685e28af2a15bb6e88ac4912b8c632f8f6ad"
    )


def test_q011ab_separates_all_products_with_the_registered_margin(
    q011ab_cycle: dict[str, Any],
) -> None:
    audit = q011ab_cycle["indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 110352
    assert audit["comparison_record_count"] == 86176
    assert audit["individual_modulus_separation_count"] == 86176
    assert audit["unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["individual_modulus_relation_counts"] == {
        "product_below_target": 64568,
        "target_below_product": 21608,
    }
    minima = [q011ab.q011z._fraction(record) for record in audit["aggregate_minimum_modulus_gaps"]]
    assert minima == pytest.approx(
        [
            8.038671735506002e-5,
            1.6431705364740245e-5,
            4.666218064574062e-5,
            5.614493817136191e-5,
            6.450587884958278e-6,
            6.989577904616183e-5,
            7.650184466921042e-4,
        ]
    )
    assert min(minima) >= q011ab.MINIMUM_MODULUS_GAP
    assert audit["minimum_gap_witness"] == {
        "aggregate_index": 4,
        "selected_type_counts": [0, 1, 1, 6],
        "source_identifiers": [
            "block=16;center=151",
            "block=16;center=152",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=16;center=149",
        ],
        "output_block": 14,
        "target_identifier": "block=14;center=143",
        "individual_modulus_relation": "product_below_target",
        "modulus_gap": audit["minimum_modulus_gap"],
    }


def test_q011ab_exact_product_streams_have_fixed_digests(
    q011ab_cycle: dict[str, Any],
) -> None:
    audit = q011ab_cycle["indexed_modulus_product_audit"]
    framed = audit["framed_exact_record_digests"]
    assert framed["exact_product_record_count"] == 110352
    assert framed["exact_product_record_digest_sha256"] == (
        "127f856813ba1910b35d367880e021e6ffbc42b9bb33ae4789ebfd35cac907ff"
    )
    assert framed["exact_comparison_record_count"] == 86176
    assert framed["exact_comparison_record_digest_sha256"] == (
        "3b1df1e1a54a1e9c27c5f3c829b6ca119669c53a9249fee109c407b0da4d1e0f"
    )
    assert audit["compact_product_digest_sha256"] == (
        "1d9e048b49181b39fa17495de2a1be16061c57c84fb4574121799cd2c3d15aa5"
    )


def test_q011ab_accepts_degree_eight_without_overclaiming(
    q011ab_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ab_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ab_cycle["hypothesis_gates"].values())
    assert q011ab_cycle["study_validity"] == "passed"
    assert q011ab_cycle["hypothesis_outcome"] == "accepted"
    assert q011ab_cycle["scientific_classification"] == q011ab.ACCEPTED_CLASSIFICATION
    theorem = q011ab_cycle["theorem_consequence"]
    assert theorem["degree_eight_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 9))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(9, 91))
    assert not theorem["degrees_9_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ab_cycle["claim_boundary"]
    assert "Q011ac" in q011ab_cycle["next_change"]


def test_q011ab_cycle_has_reproducible_strict_json_digests(
    q011ab_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ab_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("cbb93d239d4f23ec2ca3fb4dd2bb1bdc89af5756c5f2918ccb303c3442f233d9"),
        "inventory_digest_sha256": (
            "dd22f821362306d7c7bf9513a8f990253134f989a997ec5fb2677b6a1b9ad967"
        ),
        "sector_digest_sha256": (
            "3d523a17677d993113d9d17a515485db00759e490514bdbe287c6927c6525c9f"
        ),
        "product_digest_sha256": (
            "c12cee86ac5e4a9aa56a9e86996eb40756c3d327a9838aba5443b67a42177663"
        ),
        "result_digest_sha256": (
            "73c7d110f06596d5b03eead1d2b36b5975a2ca0b451c1c0b4ee13c1d4bb3f949"
        ),
    }
    assert {name: q011ab_cycle[name] for name in expected} == expected
    assert q011ab_cycle["result_digest_sha256"] == q011ab.q011b._canonical_json_sha256(
        q011ab._result_digest_sections(q011ab_cycle)
    )


def test_q011ab_study_metadata_and_generated_artifact_are_scoped(
    q011ab_study: dict[str, Any],
) -> None:
    assert q011ab_study["schema_version"] == 1
    assert q011ab_study["source"] == source_metadata()
    assert q011ab_study["study_gate"] == "passed"
    assert q011ab_study["scientific_outcome"] == "accepted"
    assert q011ab_study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    scope = q011ab_study["mathematical_scope"]
    assert scope["degree_eight_external_nonresonance_claim"] is True
    assert scope["degrees_9_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ab_study, allow_nan=False)

    runner_path = Path(q011ab.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ab_degree8_refined_modulus.json"
    if not artifact_path.exists():
        pytest.skip("Q011ab artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011ab_degree8_refined_modulus.py",
        "sha256": ("dc4511ea76419b065c5de7b84d02e040b98f50c31e863b6232afdfaedf0f677b"),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ab.q011b._canonical_json_sha256(q011ab._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
