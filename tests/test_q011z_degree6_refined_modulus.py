from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011z_degree6_refined_modulus as q011z
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011z_cycle() -> dict[str, Any]:
    return q011z.run_degree6_refined_modulus_audit()


def test_q011z_seals_four_prior_certificates_and_two_helpers(
    q011z_cycle: dict[str, Any],
) -> None:
    sealed = q011z_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 23
    assert sealed["helper_sources"] == {
        "q011l": {
            "filename": "q011l_interval_homological_inverse.py",
            "sha256": q011z.Q011L_SOURCE_SHA256,
        },
        "q011o": {
            "filename": "q011o_graph_transform_setup.py",
            "sha256": q011z.Q011O_SOURCE_SHA256,
        },
    }
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011k"]["digests"]) == q011z.Q011K_DIGESTS
    assert tuple(sealed["q011u"]["digests"]) == q011z.Q011U_DIGESTS
    assert tuple(sealed["q011x"]["digests"]) == q011z.Q011X_DIGESTS
    assert tuple(sealed["q011y"]["digests"]) == q011z.Q011Y_DIGESTS


def test_q011z_reconstructs_the_complete_degree_six_inventory(
    q011z_cycle: dict[str, Any],
) -> None:
    audit = q011z_cycle["degree6_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 84
    assert audit["degree_expanded_product_control_count"] == 462
    assert audit["old_modulus_separated_aggregate_count"] == 81
    assert audit["old_modulus_overlap_aggregate_count"] == 3
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert [record["selected_type_counts"] for record in audit["overlap_records"]] == [
        [0, 2, 1, 3],
        [0, 2, 2, 2],
        [0, 3, 1, 2],
    ]
    assert [record["external_group_indices"] for record in audit["overlap_records"]] == [
        [178],
        [178],
        [177],
    ]
    assert audit["unique_external_target_count"] == 12


def test_q011z_builds_a_contained_uniform_refined_envelope(
    q011z_cycle: dict[str, Any],
) -> None:
    audit = q011z_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [1, 2, 3]
    assert audit["relevant_identifier_count"] == 28
    assert audit["unique_center_modulus_evaluation_count"] == 19
    assert q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert q011z._fraction(audit["maximum_transformed_residual_radius"]) == pytest.approx(
        4.7369170150175137e-8
    )
    assert q011z._fraction(audit["minimum_q011k_old_radius"]) == pytest.approx(
        3.8891601146814717e-7
    )
    assert audit["uniform_record_digest_sha256"] == (
        "98696e0608f682321efdc5918649fa24a2f264755cb2983d2c4e5c6460b7723f"
    )


def test_q011z_enumerates_all_fourier_compatible_sextic_comparisons(
    q011z_cycle: dict[str, Any],
) -> None:
    audit = q011z_cycle["fourier_output_sector_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["aggregate_monomial_counts"] == [4800, 3600, 2880]
    assert audit["indexed_monomial_count"] == 11280
    expected_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011z.EXPECTED_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["aggregate_sector_histograms"]) == expected_histograms
    expected_target_histograms = tuple(
        {str(key): value for key, value in histogram.items()}
        for histogram in q011z.EXPECTED_TARGET_SECTOR_HISTOGRAMS
    )
    assert tuple(audit["external_target_sector_histograms"]) == expected_target_histograms
    assert audit["aggregate_compatible_comparison_counts"] == [2400, 1836, 2720]
    assert audit["sector_compatible_comparison_count"] == 6956
    framed = audit["framed_exact_record_digests"]
    assert framed["monomial_record_digest_sha256"] == (
        "2115b6f7affd09687908eb6dc6193d20701167102dbfdf138359091799e06d70"
    )
    assert framed["compatible_pair_record_digest_sha256"] == (
        "aa30254a73d854d1d654e749abd863b11a4d87a624593c436397eb77880a411f"
    )


def test_q011z_separates_every_indexed_product_with_registered_margin(
    q011z_cycle: dict[str, Any],
) -> None:
    audit = q011z_cycle["indexed_modulus_product_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 11280
    assert audit["comparison_record_count"] == 6956
    assert audit["individual_modulus_separation_count"] == 6956
    assert audit["unresolved_interval_overlap_count"] == 0
    assert audit["first_unresolved_interval_overlap"] is None
    assert audit["individual_modulus_relation_counts"] == {
        "product_below_target": 4556,
        "target_below_product": 2400,
    }
    minima = [q011z._fraction(record) for record in audit["aggregate_minimum_modulus_gaps"]]
    assert minima == pytest.approx(
        [
            1.6311010454743865e-5,
            4.6970543553274824e-5,
            6.7565223274027445e-6,
        ]
    )
    assert min(minima) >= q011z.MINIMUM_MODULUS_GAP
    assert audit["minimum_gap_witness"] == {
        "aggregate_index": 2,
        "selected_type_counts": [0, 3, 1, 2],
        "source_identifiers": [
            "block=16;center=151",
            "block=16;center=151",
            "block=16;center=151",
            "block=0;center=149",
            "block=0;center=147",
            "block=0;center=147",
        ],
        "output_block": 14,
        "target_identifier": "block=14;center=143",
        "individual_modulus_relation": "product_below_target",
        "modulus_gap": audit["minimum_modulus_gap"],
    }


def test_q011z_exact_product_streams_have_fixed_digests(
    q011z_cycle: dict[str, Any],
) -> None:
    audit = q011z_cycle["indexed_modulus_product_audit"]
    framed = audit["framed_exact_record_digests"]
    assert framed["exact_product_record_count"] == 11280
    assert framed["exact_product_record_digest_sha256"] == (
        "b9cc4cbab096815f81c15ffeae3b7e78accb0ff68fd15ee6c93549c85e1c2dfd"
    )
    assert framed["exact_comparison_record_count"] == 6956
    assert framed["exact_comparison_record_digest_sha256"] == (
        "6a61466b0efc2a170d3d43d43b5cc899f1aae198870abc98e80640f543c39ea0"
    )
    assert audit["compact_product_digest_sha256"] == (
        "57e6a380570b9826c86d3be1654fc518950a6d680e0f12d0e449a9cf4237777d"
    )


def test_q011z_accepts_degree_six_without_overclaiming_higher_results(
    q011z_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011z_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011z_cycle["hypothesis_gates"].values())
    assert q011z_cycle["study_validity"] == "passed"
    assert q011z_cycle["hypothesis_outcome"] == "accepted"
    assert q011z_cycle["scientific_classification"] == q011z.ACCEPTED_CLASSIFICATION
    theorem = q011z_cycle["theorem_consequence"]
    assert theorem["degree_six_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == [2, 3, 4, 5, 6]
    assert theorem["missing_external_nonresonance_degrees"] == list(range(7, 91))
    assert not theorem["degrees_7_through_90_are_certified"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011z_cycle["claim_boundary"]
    assert "Q011aa" in q011z_cycle["next_change"]


def test_q011z_cycle_has_reproducible_strict_json_digests(
    q011z_cycle: dict[str, Any],
) -> None:
    json.dumps(q011z_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("394728b15820900b642776843b96b7383b31fec27bede2274d97ee9c635054bb"),
        "inventory_digest_sha256": (
            "46248ce31e7e04039eb9eb1788d42f04d19dd949b026a921e61812ab3d37e8cc"
        ),
        "sector_digest_sha256": (
            "b172439520fa25bba82fa936564ebc0ae51763a57006cb279d1e3fe9f0ed0a3c"
        ),
        "product_digest_sha256": (
            "148acb302034412498638201703eee8722f90afa093adcf6215094170e4a8c1e"
        ),
        "result_digest_sha256": (
            "a695e5c632e6dda8114377f33824ca6b234ebadae7c25d6b8aa1c3d3774c4aff"
        ),
    }
    assert {name: q011z_cycle[name] for name in expected} == expected
    assert q011z_cycle["result_digest_sha256"] == q011z.q011b._canonical_json_sha256(
        q011z._result_digest_sections(q011z_cycle)
    )


def test_q011z_study_metadata_and_generated_artifact_are_scoped() -> None:
    study = q011z.run_q011z_study()
    assert study["schema_version"] == 1
    assert study["source"] == source_metadata()
    assert study["study_gate"] == "passed"
    assert study["scientific_outcome"] == "accepted"
    assert study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    assert study["mathematical_scope"]["degree_six_external_nonresonance_claim"] is True
    assert study["mathematical_scope"]["degrees_7_through_90_claim"] is False
    assert study["mathematical_scope"]["ssm_uniqueness_claim"] is False
    json.dumps(study, allow_nan=False)

    runner_path = Path(q011z.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011z_degree6_refined_modulus.json"
    if not artifact_path.exists():
        pytest.skip("Q011z artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "bd435ceea3795475f6b17619e13626ba936f8fcbd15da749a39a4e2b034a4e23"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011z_degree6_refined_modulus.py",
        "sha256": "6e6d7327e4b85b307098203fe882434bf77f3920a1da7323b1c89d118df3ae87",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011z.q011b._canonical_json_sha256(q011z._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
