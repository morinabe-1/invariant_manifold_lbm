from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ac_degree9_refined_modulus as q011ac
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ac_study() -> dict[str, Any]:
    return q011ac.run_q011ac_study()


@pytest.fixture(scope="module")
def q011ac_cycle(q011ac_study: dict[str, Any]) -> dict[str, Any]:
    return q011ac_study["cycle"]


def test_q011ac_seals_q011ab_and_all_prior_inputs(
    q011ac_cycle: dict[str, Any],
) -> None:
    sealed = q011ac_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 38
    assert all(sealed["checks"].values())
    assert sealed["prior_q011ab_sealed_input_audit"]["passed"]
    assert sealed["prior_q011ab_sealed_input_audit"]["direct_digest_count"] == 33
    assert tuple(sealed["q011ab"]["digests"]) == q011ac.Q011AB_DIGESTS
    assert sealed["q011ab"]["artifact_sha256"] == q011ac.Q011AB_ARTIFACT_SHA256
    assert sealed["q011ab"]["runner_sha256"] == q011ac.Q011AB_RUNNER_SHA256


def test_q011ac_reconstructs_the_complete_degree_nine_inventory(
    q011ac_cycle: dict[str, Any],
) -> None:
    audit = q011ac_cycle["degree9_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 220
    assert audit["degree_expanded_product_control_count"] == 2002
    assert audit["old_modulus_separated_aggregate_count"] == 215
    assert audit["old_modulus_overlap_aggregate_count"] == 5
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert (
        tuple(tuple(record["selected_type_counts"]) for record in audit["overlap_records"])
        == q011ac.OVERLAP_COUNTS
    )
    assert (
        tuple(record["external_group_indices"][0] for record in audit["overlap_records"])
        == q011ac.EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 36
    assert audit["exact_inventory_digest_sha256"] == (
        "d56ca0e3d3311487c8e39afb786bcd159ff36e4b38667c18fbf01cb80e853641"
    )


def test_q011ac_extends_the_uniform_envelope_to_64_identifiers(
    q011ac_cycle: dict[str, Any],
) -> None:
    audit = q011ac_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 60
    assert audit["relevant_identifier_count"] == 64
    assert audit["unique_center_modulus_evaluation_count"] == 40
    assert q011ac.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["uniform_record_digest_sha256"] == (
        "686812fcf2eaee7eab3766bd23405dd747cc7440ac762e10ce7c2abad3b51b6a"
    )


def test_q011ac_enumerates_all_nonic_fourier_comparisons(
    q011ac_cycle: dict[str, Any],
) -> None:
    audit = q011ac_cycle["fourier_output_sector_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert tuple(audit["aggregate_monomial_counts"]) == (q011ac.EXPECTED_MONOMIAL_COUNTS)
    assert audit["indexed_monomial_count"] == 87260
    assert audit["sector_compatible_monomial_count"] == 26578
    assert audit["sector_incompatible_monomial_count"] == 60682
    expected_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ac.EXPECTED_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["aggregate_sector_histograms"]) == expected_histograms
    expected_target_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011ac.EXPECTED_TARGET_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["external_target_sector_histograms"]) == expected_target_histograms
    assert tuple(audit["aggregate_compatible_comparison_counts"]) == (
        q011ac.EXPECTED_COMPARISON_COUNTS
    )
    assert audit["sector_compatible_comparison_count"] == 82872
    framed = audit["framed_exact_record_digests"]
    assert framed["monomial_record_digest_sha256"] == (
        "ce7c15884773b2eac4c3f2ca499f2698b5a9eecddc9cb915624c63adb764b455"
    )
    assert framed["compatible_pair_record_digest_sha256"] == (
        "5f1330d1b2f8b404e4c7fce7d629521c756b33d5f2ca735b018c50e0abd7a308"
    )


def test_q011ac_separates_all_products_with_the_registered_margin(
    q011ac_cycle: dict[str, Any],
) -> None:
    audit = q011ac_cycle["indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 87260
    assert audit["comparison_record_count"] == 82872
    assert audit["individual_modulus_separation_count"] == 82872
    assert audit["unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["individual_modulus_relation_counts"] == {
        "product_below_target": 57120,
        "target_below_product": 25752,
    }
    minima = [q011ac.q011z._fraction(record) for record in audit["aggregate_minimum_modulus_gaps"]]
    assert minima == pytest.approx(
        [
            5.620482708927926e-5,
            6.297629130186793e-6,
            6.974283071507663e-5,
            7.648737435877863e-4,
            4.589058211328851e-4,
        ]
    )
    assert min(minima) >= q011ac.MINIMUM_MODULUS_GAP
    assert audit["minimum_gap_witness"] == {
        "aggregate_index": 1,
        "selected_type_counts": [0, 0, 1, 8],
        "source_identifiers": [
            "block=16;center=152",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=0;center=147",
            "block=16;center=149",
            "block=16;center=149",
        ],
        "output_block": 14,
        "target_identifier": "block=14;center=143",
        "individual_modulus_relation": "product_below_target",
        "modulus_gap": audit["minimum_modulus_gap"],
    }


def test_q011ac_exact_product_streams_have_fixed_digests(
    q011ac_cycle: dict[str, Any],
) -> None:
    audit = q011ac_cycle["indexed_modulus_product_audit"]
    framed = audit["framed_exact_record_digests"]
    assert framed["exact_product_record_count"] == 87260
    assert framed["exact_product_record_digest_sha256"] == (
        "4de9bbef5a45e751d772f4c68425cb3bc5d6f8614dedd051663e07992775e98d"
    )
    assert framed["exact_comparison_record_count"] == 82872
    assert framed["exact_comparison_record_digest_sha256"] == (
        "a2dd6eb42b9067d8671653ac7912b202ac417f55c01bcd23e4251fafc7413c9e"
    )
    assert audit["compact_product_digest_sha256"] == (
        "b1c5cada4122a189fafbf1fc714918a4a178f884d07febb2c806d10f1824d62b"
    )


def test_q011ac_accepts_degree_nine_without_overclaiming(
    q011ac_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ac_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ac_cycle["hypothesis_gates"].values())
    assert q011ac_cycle["study_validity"] == "passed"
    assert q011ac_cycle["hypothesis_outcome"] == "accepted"
    assert q011ac_cycle["scientific_classification"] == q011ac.ACCEPTED_CLASSIFICATION
    theorem = q011ac_cycle["theorem_consequence"]
    assert theorem["degree_nine_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 10))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(10, 91))
    assert not theorem["degrees_10_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011ac_cycle["claim_boundary"]
    assert "Q011ad" in q011ac_cycle["next_change"]


def test_q011ac_cycle_has_reproducible_strict_json_digests(
    q011ac_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ac_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("9736be0479a5bea455a48fc1723eb92400a34c332c0484f6eb5ee8f01cf1de83"),
        "inventory_digest_sha256": (
            "0c54f22e4907d676d014a8b512a4eff07d55adc5b9a20905b085a8548158f15e"
        ),
        "sector_digest_sha256": (
            "b877b5db479071043c52605725e44a350efdf402ff70795c9bcf9cf664cdb02a"
        ),
        "product_digest_sha256": (
            "29fe385171af17292a0afa303e0bf406b678a02f41367932a12395948e9b47b7"
        ),
        "result_digest_sha256": (
            "7fd97a88d2fb3d0c20098cca73702b376493bd5635b98f7cb17494c518dd7173"
        ),
    }
    assert {name: q011ac_cycle[name] for name in expected} == expected
    assert q011ac_cycle["result_digest_sha256"] == q011ac.q011b._canonical_json_sha256(
        q011ac._result_digest_sections(q011ac_cycle)
    )


def test_q011ac_study_metadata_and_generated_artifact_are_scoped(
    q011ac_study: dict[str, Any],
) -> None:
    assert q011ac_study["schema_version"] == 1
    assert q011ac_study["source"] == source_metadata()
    assert q011ac_study["study_gate"] == "passed"
    assert q011ac_study["scientific_outcome"] == "accepted"
    assert q011ac_study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    scope = q011ac_study["mathematical_scope"]
    assert scope["degree_nine_external_nonresonance_claim"] is True
    assert scope["degrees_10_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ac_study, allow_nan=False)

    runner_path = Path(q011ac.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ac_degree9_refined_modulus.json"
    if not artifact_path.exists():
        pytest.skip("Q011ac artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "18a6e146d0d24af9e9bab22f45668bec6c5bc25efcdb05faee2a7228e1870a98"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011ac_degree9_refined_modulus.py",
        "sha256": ("d028f83bf45c18977fccd58091007507a69a0c725a6f4f22d3527246d8344277"),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ac.q011b._canonical_json_sha256(q011ac._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
