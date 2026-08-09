from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011aa_degree7_refined_modulus as q011aa
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011aa_study() -> dict[str, Any]:
    return q011aa.run_q011aa_study()


@pytest.fixture(scope="module")
def q011aa_cycle(q011aa_study: dict[str, Any]) -> dict[str, Any]:
    return q011aa_study["cycle"]


def test_q011aa_seals_q011z_and_its_four_prior_inputs(
    q011aa_cycle: dict[str, Any],
) -> None:
    sealed = q011aa_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 28
    assert all(sealed["checks"].values())
    assert sealed["prior_q011z_sealed_input_audit"]["passed"]
    assert sealed["prior_q011z_sealed_input_audit"]["direct_digest_count"] == 23
    assert tuple(sealed["q011z"]["digests"]) == q011aa.Q011Z_DIGESTS
    assert sealed["q011z"]["artifact_sha256"] == q011aa.Q011Z_ARTIFACT_SHA256
    assert sealed["q011z"]["runner_sha256"] == q011aa.Q011Z_RUNNER_SHA256


def test_q011aa_reconstructs_the_complete_degree_seven_inventory(
    q011aa_cycle: dict[str, Any],
) -> None:
    audit = q011aa_cycle["degree7_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 120
    assert audit["degree_expanded_product_control_count"] == 792
    assert audit["old_modulus_separated_aggregate_count"] == 115
    assert audit["old_modulus_overlap_aggregate_count"] == 5
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011aa.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011aa.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 12
    assert audit["exact_inventory_digest_sha256"] == (
        "5188c5259996de2269a0d68751d94ae3050c51fe7cbc00432da6b4fc82ec5c36"
    )


def test_q011aa_reuses_the_contained_uniform_refined_envelope(
    q011aa_cycle: dict[str, Any],
) -> None:
    audit = q011aa_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_seven_active_selected_group_indices"] == [1, 2, 3]
    assert audit["relevant_identifier_count"] == 28
    assert audit["unique_center_modulus_evaluation_count"] == 19
    assert q011aa.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == (
        "98696e0608f682321efdc5918649fa24a2f264755cb2983d2c4e5c6460b7723f"
    )


def test_q011aa_enumerates_all_septic_fourier_comparisons(
    q011aa_cycle: dict[str, Any],
) -> None:
    audit = q011aa_cycle["fourier_output_sector_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert tuple(audit["aggregate_monomial_counts"]) == (q011aa.EXPECTED_MONOMIAL_COUNTS)
    assert audit["indexed_monomial_count"] == 58992
    assert audit["sector_compatible_monomial_count"] == 16878
    assert audit["sector_incompatible_monomial_count"] == 42114
    expected_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011aa.EXPECTED_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["aggregate_sector_histograms"]) == expected_histograms
    expected_target_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011aa.EXPECTED_TARGET_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["external_target_sector_histograms"]) == expected_target_histograms
    assert tuple(audit["aggregate_compatible_comparison_counts"]) == (
        q011aa.EXPECTED_COMPARISON_COUNTS
    )
    assert audit["sector_compatible_comparison_count"] == 44380
    framed = audit["framed_exact_record_digests"]
    assert framed["monomial_record_digest_sha256"] == (
        "5e2a0d986b63eb77a4f67ae2c79c0f1ed6acb3531317f530bf82b95ebb45c43b"
    )
    assert framed["compatible_pair_record_digest_sha256"] == (
        "36bb54954525bf0867d5fdf31523bd20bd72971acbbd6d5135f7e70523d403c1"
    )


def test_q011aa_separates_all_products_with_the_registered_margin(
    q011aa_cycle: dict[str, Any],
) -> None:
    audit = q011aa_cycle["indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 58992
    assert audit["comparison_record_count"] == 44380
    assert audit["individual_modulus_separation_count"] == 44380
    assert audit["unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["individual_modulus_relation_counts"] == {
        "product_below_target": 30764,
        "target_below_product": 13616,
    }
    minima = [q011aa.q011z._fraction(record) for record in audit["aggregate_minimum_modulus_gaps"]]
    assert minima == pytest.approx(
        [
            1.6371355291399596e-5,
            4.681636472938023e-5,
            5.608507807101488e-5,
            6.603546614599508e-6,
            7.004874435925448e-5,
        ]
    )
    assert min(minima) >= q011aa.MINIMUM_MODULUS_GAP
    assert audit["minimum_gap_witness"] == {
        "aggregate_index": 3,
        "selected_type_counts": [0, 2, 1, 4],
        "source_identifiers": [
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=152",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
        ],
        "output_block": 14,
        "target_identifier": "block=14;center=143",
        "individual_modulus_relation": "product_below_target",
        "modulus_gap": audit["minimum_modulus_gap"],
    }


def test_q011aa_exact_product_streams_have_fixed_digests(
    q011aa_cycle: dict[str, Any],
) -> None:
    audit = q011aa_cycle["indexed_modulus_product_audit"]
    framed = audit["framed_exact_record_digests"]
    assert framed["exact_product_record_count"] == 58992
    assert framed["exact_product_record_digest_sha256"] == (
        "ff476eaf7cb575058d7a43002ce56e4f7e5bd733c52347832237f4b8d4c2f0a3"
    )
    assert framed["exact_comparison_record_count"] == 44380
    assert framed["exact_comparison_record_digest_sha256"] == (
        "348a32179485b1f5766787262ea163d36f951eb76bc049070a8d3c0074844c73"
    )
    assert audit["compact_product_digest_sha256"] == (
        "ade0521a2e87d30a51573810a769eae7f78d2bd693c860688fa8449d7bd29ed4"
    )


def test_q011aa_accepts_degree_seven_without_overclaiming(
    q011aa_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011aa_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011aa_cycle["hypothesis_gates"].values())
    assert q011aa_cycle["study_validity"] == "passed"
    assert q011aa_cycle["hypothesis_outcome"] == "accepted"
    assert q011aa_cycle["scientific_classification"] == q011aa.ACCEPTED_CLASSIFICATION
    theorem = q011aa_cycle["theorem_consequence"]
    assert theorem["degree_seven_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == [
        2,
        3,
        4,
        5,
        6,
        7,
    ]
    assert theorem["missing_external_nonresonance_degrees"] == list(range(8, 91))
    assert not theorem["degrees_8_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011aa_cycle["claim_boundary"]
    assert "Q011ab" in q011aa_cycle["next_change"]


def test_q011aa_cycle_has_reproducible_strict_json_digests(
    q011aa_cycle: dict[str, Any],
) -> None:
    json.dumps(q011aa_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("9d460085b29b9a3e094bc6ed19fd94908a0f9d5507f5c1901b0f8b5e7da3cb76"),
        "inventory_digest_sha256": (
            "c7c6d89542c1b8d563e091530b2bd07aadbd2e4eedf5db3be7b86a9d68b97a65"
        ),
        "sector_digest_sha256": (
            "4c70de8129596fa631392014f44514290906efa9d2000bf865a9a8700f65d080"
        ),
        "product_digest_sha256": (
            "ca37525b63f7e906b352dd86bf0b16b79954b88fd7b6066f880f8b00e474b7fb"
        ),
        "result_digest_sha256": (
            "c136c7e2963ef5700a1d1c969ea67f7463db390f6141427a517092ac9e0b44e4"
        ),
    }
    assert {name: q011aa_cycle[name] for name in expected} == expected
    assert q011aa_cycle["result_digest_sha256"] == q011aa.q011b._canonical_json_sha256(
        q011aa._result_digest_sections(q011aa_cycle)
    )


def test_q011aa_study_metadata_and_generated_artifact_are_scoped(
    q011aa_study: dict[str, Any],
) -> None:
    assert q011aa_study["schema_version"] == 1
    assert q011aa_study["source"] == source_metadata()
    assert q011aa_study["study_gate"] == "passed"
    assert q011aa_study["scientific_outcome"] == "accepted"
    assert q011aa_study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    scope = q011aa_study["mathematical_scope"]
    assert scope["degree_seven_external_nonresonance_claim"] is True
    assert scope["degrees_8_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011aa_study, allow_nan=False)

    runner_path = Path(q011aa.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011aa_degree7_refined_modulus.json"
    if not artifact_path.exists():
        pytest.skip("Q011aa artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011aa_degree7_refined_modulus.py",
        "sha256": ("d5db6eb414ebc0479fbf91e62b9a3618c675556aa80df2e693a39171ee838c70"),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011aa.q011b._canonical_json_sha256(q011aa._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
