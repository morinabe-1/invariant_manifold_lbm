from __future__ import annotations

import json
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest

import research.q011d_forced_quadratic_homological as q011d
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011d_cycle() -> dict:
    return q011d.run_forced_quadratic_homological_audit()


def test_q011d_registered_pair_partition_is_complete() -> None:
    coordinate_sectors = q011d._selected_coordinate_sectors()
    pairs = tuple(
        combinations_with_replacement(
            range(q011d.EXPECTED_SELECTED_DIMENSION),
            2,
        )
    )
    sectors = [
        (coordinate_sectors[left] + coordinate_sectors[right]) % q011d.SIZE for left, right in pairs
    ]

    assert coordinate_sectors == (0,) * 6 + (1,) * 9 + (16,) * 9
    assert len(pairs) == q011d.EXPECTED_PAIR_COUNT == 300
    assert {
        sector: sectors.count(sector) for sector in q011d.OUTPUT_SECTOR_ORDER
    } == q011d.EXPECTED_SECTOR_PAIR_COUNTS
    assert set(sectors) == set(q011d.OUTPUT_SECTOR_ORDER)


def test_q011d_symmetric_product_assembly_has_the_registered_action() -> None:
    generator = np.random.default_rng(20260809)
    blocks = [
        np.triu(
            generator.standard_normal((dimension, dimension))
            + 1j * generator.standard_normal((dimension, dimension))
        )
        for dimension in (6, 9, 9)
    ]
    selected = np.zeros((24, 24), dtype=np.complex128)
    offset = 0
    for block in blocks:
        width = block.shape[0]
        selected[offset : offset + width, offset : offset + width] = block
        offset += width
    pairs = tuple(combinations_with_replacement(range(24), 2))
    action = q011d._assemble_symmetric_product(selected, pairs)
    direction = generator.standard_normal(24) + 1j * generator.standard_normal(24)

    expected = q011d._monomial_vector(selected @ direction, pairs)
    observed = action @ q011d._monomial_vector(direction, pairs)
    np.testing.assert_allclose(observed, expected, rtol=2.0e-14, atol=2.0e-13)


def test_q011d_replays_all_sealed_inputs(q011d_cycle: dict) -> None:
    audit = q011d_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["q011c2_artifact"]["study_validity"] == "passed"
    assert audit["q011c2_artifact"]["hypothesis_outcome"] == "accepted"
    assert audit["preserved_prior_outcomes"] == {
        "q011c1_study_validity": "passed",
        "q011c1_hypothesis_outcome": "accepted",
        "q011c_study_validity": "failed",
        "q011c_hypothesis_outcome": "inconclusive",
    }
    calibration = audit["q006i_calibration"]
    assert calibration["pair_count"] == 300
    assert calibration["minimum_operator_singular_value"] == pytest.approx(
        q011d.Q006I_MINIMUM_OPERATOR_SINGULAR_VALUE
    )
    assert calibration["maximum_operator_condition_number"] == pytest.approx(
        q011d.Q006I_MAXIMUM_CONDITION_NUMBER
    )
    assert calibration["numerical_singular_block_count"] == 0


def test_q011d_canonical_forced_linear_split_is_structural(
    q011d_cycle: dict,
) -> None:
    audit = q011d_cycle["canonical_linear_split_audit"]

    assert [record["selected_dimension"] for record in audit["selected_block_records"]] == [
        6,
        9,
        9,
    ]
    assert {
        record["block_index"]: record["external_dimension"]
        for record in audit["selected_block_records"]
    } == {0: 144, 1: 144, 16: 144}
    assert {
        record["block_index"]: record["external_dimension"]
        for record in audit["external_sector_records"]
    } == {2: 153, 15: 153}
    assert audit["selected_eigenvalue_count"] == 24
    assert audit["external_eigenvalue_count"] == 2574
    assert audit["full_fixed_leaf_eigenvalue_count"] == 2598
    assert audit["maximum_structural_residual"] <= q011d.STRUCTURAL_TOLERANCE
    assert audit["maximum_conjugate_spectrum_hausdorff_error"] <= q011d.STRUCTURAL_TOLERANCE
    assert audit["global_modulus_normal_dominance_gap"] >= (q011d.NORMAL_DOMINANCE_GAP_FLOOR)
    assert audit["full_fixed_leaf_spectral_radius"] <= (q011d.FULL_SPECTRAL_RADIUS_CEILING)
    assert 1.0 < audit["logarithmic_spectral_quotient_diagnostic"] < 2.0
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]


def test_q011d_quadratic_input_action_closes_by_sector(
    q011d_cycle: dict,
) -> None:
    audit = q011d_cycle["quadratic_input_action_audit"]

    assert audit["pair_count"] == 300
    assert audit["symmetric_product_shape"] == [300, 300]
    assert audit["sector_pair_counts"] == {
        "0": 102,
        "1": 54,
        "16": 54,
        "2": 45,
        "15": 45,
    }
    assert audit["sector_scalar_dimensions"] == {
        "0": 14688,
        "1": 7776,
        "16": 7776,
        "2": 6885,
        "15": 6885,
    }
    assert audit["sector_leakage_relative_frobenius_norm"] <= q011d.SECTOR_LEAKAGE_TOLERANCE
    assert audit["maximum_action_relative_error"] <= (q011d.ACTION_RELATIVE_TOLERANCE)
    assert audit["maximum_product_spectrum_absolute_hausdorff_error"] <= (
        q011d.PRODUCT_SPECTRUM_TOLERANCE
    )
    assert len(audit["action_records"]) == 8
    assert len(audit["sector_records"]) == 5
    assert all(audit["checks"].values())
    assert audit["passed"]


def test_q011d_all_three_hundred_external_blocks_pass(
    q011d_cycle: dict,
) -> None:
    audit = q011d_cycle["external_homological_block_audit"]

    assert audit["block_count"] == 300
    assert len(audit["block_records"]) == 300
    assert audit["numerically_singular_block_count"] == 0
    assert audit["minimum_operator_singular_value"] >= (q011d.MINIMUM_OPERATOR_SINGULAR_VALUE)
    assert audit["minimum_spectral_distance"] >= (q011d.MINIMUM_SPECTRAL_DISTANCE)
    assert audit["maximum_operator_condition_number"] <= (q011d.MAXIMUM_OPERATOR_CONDITION_NUMBER)
    assert audit["maximum_direct_solve_relative_residual"] <= (q011d.MAXIMUM_DIRECT_SOLVE_RESIDUAL)
    assert audit["maximum_conjugate_diagnostic_relative_error"] <= (
        q011d.CONJUGATE_DIAGNOSTIC_TOLERANCE
    )
    assert all(
        len(record["singular_values"]) == record["operator_shape"][0]
        for record in audit["block_records"]
    )
    assert all(audit["checks"].values())
    assert all(audit["hypothesis_checks"].values())
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]


def test_q011d_all_twenty_sector_sylvester_probes_pass(
    q011d_cycle: dict,
) -> None:
    audit = q011d_cycle["sector_sylvester_probe_audit"]

    assert audit["probe_count"] == 20
    assert len(audit["sector_records"]) == 5
    assert audit["solver_or_nonfinite_failure_count"] == 0
    assert audit["maximum_relative_equation_residual"] <= (q011d.MAXIMUM_SYLVESTER_PROBE_RESIDUAL)
    assert audit["maximum_response_amplification"] <= (
        q011d.MAXIMUM_SYLVESTER_RESPONSE_AMPLIFICATION
    )
    assert all(len(record["probe_records"]) == 4 for record in audit["sector_records"])
    assert all(audit["checks"].values())
    assert all(audit["hypothesis_checks"].values())
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]


def test_q011d_accepts_only_the_operator_prequalification(
    q011d_cycle: dict,
) -> None:
    assert len(q011d_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011d_cycle["validity_gates"].values())
    assert len(q011d_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011d_cycle["hypothesis_gates"].values())
    assert q011d_cycle["study_validity"] == "passed"
    assert q011d_cycle["hypothesis_outcome"] == "accepted"
    assert q011d_cycle["scientific_classification"] == (
        "the forced quadratic external homological family is numerically nonresonant and solvable"
    )
    consequence = q011d_cycle["numerical_consequence"]
    assert consequence["forced_quadratic_external_family_is_prequalified"]
    assert not consequence["forced_map_hessian_is_computed"]
    assert not consequence["forced_quadratic_chart_is_constructed"]
    assert not consequence["forced_invariant_manifold_exists"]
    assert not any(q011d_cycle["preserved_prior_outcomes"].values())


def test_q011d_records_reproducible_digests_and_provenance(
    q011d_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011d_cycle["registered_parameters"],
        "sealed_input_audit": q011d_cycle["sealed_input_audit"],
    }
    linear_sections = {
        "canonical_linear_split_audit": q011d_cycle["canonical_linear_split_audit"],
    }
    pair_sections = {
        "quadratic_input_action_audit": q011d_cycle["quadratic_input_action_audit"],
        "external_homological_block_audit": q011d_cycle["external_homological_block_audit"],
    }
    probe_sections = {
        "sector_sylvester_probe_audit": q011d_cycle["sector_sylvester_probe_audit"],
    }

    assert q011d_cycle["input_digest_sha256"] == (
        q011d.q011c._canonical_json_sha256(input_sections)
    )
    assert q011d_cycle["linear_split_digest_sha256"] == (
        q011d.q011c._canonical_json_sha256(linear_sections)
    )
    assert q011d_cycle["pair_family_digest_sha256"] == (
        q011d.q011c._canonical_json_sha256(pair_sections)
    )
    assert q011d_cycle["sector_probe_digest_sha256"] == (
        q011d.q011c._canonical_json_sha256(probe_sections)
    )
    assert q011d_cycle["result_digest_sha256"] == (
        q011d.q011c._canonical_json_sha256(q011d._result_digest_sections(q011d_cycle))
    )
    runner_path = Path(q011d.__file__).resolve()
    assert q011d_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    json.dumps(q011d_cycle, allow_nan=False)
