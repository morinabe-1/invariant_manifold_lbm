from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import research.q011i_exact_zero_mean_repair as q011i
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011i_cycle() -> dict[str, object]:
    return q011i.run_exact_zero_mean_repair_audit()


def test_q011i_reproduces_the_raw_exact_obstruction() -> None:
    _, artifact = q011i._sealed_q011b_artifact_audit()
    audit = q011i._raw_obstruction_audit(artifact)

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["raw_waveform_sha256"] == q011i.RAW_WAVEFORM_SHA256
    assert audit["raw_source_sha256"] == q011i.RAW_SOURCE_SHA256
    assert audit["raw_exact_waveform_sum"] == {
        "numerator_base16": "-0x47",
        "denominator_base16": "0x40000000000000000000",
        "float": float(q011i.RAW_EXACT_WAVEFORM_SUM),
    }
    assert audit["raw_exact_global_source_moments"][1]["numerator_base16"] != "0x0"
    assert not audit["raw_exact_fixed_point_is_compatible_with_global_momentum_ledger"]
    assert not audit["q011b_numerical_outcome_is_regraded"]


def test_q011i_registered_waveform_search_is_exact_and_reproducible() -> None:
    waveform, audit = q011i._waveform_repair_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["candidate_count"] == 8 * (1 + 2 * q011i.WAVEFORM_SEARCH_MAXIMUM_ULPS)
    assert audit["selected_pair"] == [
        q011i.REGISTERED_WAVEFORM_PAIR,
        q011i.SIZE - q011i.REGISTERED_WAVEFORM_PAIR,
    ]
    assert audit["selected_ulp_shift"] == q011i.REGISTERED_WAVEFORM_ULP_SHIFT
    assert audit["repaired_waveform_sha256"] == q011i.REPAIRED_WAVEFORM_SHA256
    assert audit["repaired_exact_sum"]["numerator_base16"] == "0x0"
    assert audit["changed_entry_count"] <= q011i.MAXIMUM_WAVEFORM_CHANGED_ENTRY_COUNT
    assert audit["maximum_component_perturbation"] <= (
        q011i.MAXIMUM_WAVEFORM_COMPONENT_PERTURBATION
    )
    assert audit["relative_l2_perturbation"] <= q011i.MAXIMUM_WAVEFORM_RELATIVE_PERTURBATION
    assert audit["fft_relative_leakage_outside_plus_minus_one"] <= (
        q011i.MAXIMUM_WAVEFORM_FOURIER_LEAKAGE
    )
    assert waveform[0] == q011i.q011b.force_waveform()[0]
    np.testing.assert_array_equal(waveform[1:9], waveform[:8:-1])


def test_q011i_repaired_source_has_exact_local_and_global_moments() -> None:
    waveform, _ = q011i._waveform_repair_audit()
    source, audit = q011i._source_repair_audit(waveform)

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert source.shape == (q011i.SIZE, 1, 9)
    assert np.count_nonzero(source) == 102
    assert audit["source_sha256"] == q011i.REPAIRED_SOURCE_SHA256
    assert audit["maximum_selected_ulp_shift"] <= q011i.MAXIMUM_SOURCE_ULP_SHIFT
    assert audit["maximum_component_perturbation_vs_raw"] <= (
        q011i.MAXIMUM_SOURCE_COMPONENT_PERTURBATION
    )
    assert audit["relative_l2_perturbation_vs_raw"] <= (q011i.MAXIMUM_SOURCE_RELATIVE_PERTURBATION)
    assert all(
        moment[0]["numerator_base16"] == "0x0" and moment[2]["numerator_base16"] == "0x0"
        for moment in audit["local_exact_moment_ledger"]
    )
    assert all(
        moment["numerator_base16"] == "0x0" for moment in audit["global_exact_moment_ledger"]
    )


def test_q011i_seals_q011b_q011h_and_prior_claim_boundaries() -> None:
    q011b_audit, _ = q011i._sealed_q011b_artifact_audit()
    q011h_audit, _ = q011i._sealed_q011h_artifact_audit()

    assert q011b_audit["passed"]
    assert all(q011b_audit["checks"].values())
    assert q011b_audit["artifact"]["hypothesis_outcome"] == "accepted"
    assert q011h_audit["passed"]
    assert all(q011h_audit["checks"].values())
    assert q011h_audit["artifact"]["hypothesis_outcome"] == "accepted"


def test_q011i_fixed_point_and_spectrum_bridge_are_accepted(
    q011i_cycle: dict[str, object],
) -> None:
    fixed_point = q011i_cycle["repaired_fixed_point_bridge_audit"]
    spectrum = q011i_cycle["repaired_spectrum_bridge_audit"]

    assert fixed_point["passed"]
    assert all(fixed_point["checks"].values())
    assert set(fixed_point["primary_runs"]) == {"zero", "sealed-q011b-coordinate"}
    for run in fixed_point["primary_runs"].values():
        assert run["converged"]
        assert run["terminal_metrics"]["projected_l2"] <= q011i.MAXIMUM_PROJECTED_RESIDUAL
        assert run["terminal_metrics"]["full_l2"] <= q011i.MAXIMUM_FULL_RESIDUAL
        assert run["terminal_metrics"]["maximum_component"] <= (q011i.MAXIMUM_COMPONENT_RESIDUAL)
    assert fixed_point["two_start_solution_l2_distance"] <= q011i.MAXIMUM_TWO_START_DISTANCE
    assert fixed_point["two_start_solution_relative_distance"] <= (
        q011i.MAXIMUM_TWO_START_RELATIVE_DISTANCE
    )
    assert fixed_point["repaired_vs_sealed_state_l2_distance"] <= (
        q011i.MAXIMUM_SEALED_STATE_DISTANCE
    )
    assert fixed_point["repaired_vs_sealed_state_relative_distance"] <= (
        q011i.MAXIMUM_SEALED_STATE_RELATIVE_DISTANCE
    )
    assert fixed_point["physical_fourier_audit"]["minimum_population"] > 0.0

    assert spectrum["passed"]
    assert all(spectrum["checks"].values())
    assert len(spectrum["block_bridge_records"]) == q011i.SIZE
    assert spectrum["maximum_block_matrix_relative_perturbation"] <= (
        q011i.MAXIMUM_BLOCK_MATRIX_RELATIVE_PERTURBATION
    )
    assert spectrum["maximum_block_spectrum_absolute_hausdorff_distance"] <= (
        q011i.MAXIMUM_BLOCK_SPECTRUM_HAUSDORFF_DISTANCE
    )
    fresh = spectrum["fresh_spectrum_audit"]
    assert fresh["maximum_fixed_leaf_eigenvalue_modulus"] <= q011i.q011b.SPECTRAL_RADIUS_CEILING
    assert fresh["minimum_i_minus_j_singular_value"] >= (
        q011i.q011b.MINIMUM_RESOLVENT_SINGULAR_VALUE
    )
    assert fresh["maximum_i_minus_j_condition_number"] <= (
        q011i.q011b.MAXIMUM_RESOLVENT_CONDITION_NUMBER
    )


def test_q011i_accepts_only_the_registered_bridge(
    q011i_cycle: dict[str, object],
) -> None:
    assert q011i_cycle["study_validity"] == "passed"
    assert q011i_cycle["hypothesis_outcome"] == "accepted"
    assert q011i_cycle["scientific_classification"] == (
        "the exact-dyadic zero-mean repair preserves the numerical forced "
        "fixed-point and linear-spectrum baseline"
    )
    assert len(q011i_cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in q011i_cycle["validity_gates"].values())
    assert len(q011i_cycle["hypothesis_gates"]) == 4
    assert all(gate["passed"] for gate in q011i_cycle["hypothesis_gates"].values())
    consequence = q011i_cycle["decision_consequence"]
    assert consequence["repaired_source_is_the_target_for_rigorous_fixed_point_work"]
    assert consequence["interval_fixed_point_proof_is_authorized"]
    assert not consequence["q011b_numerical_accepted_outcome_changed"]
    assert not consequence["q011e_through_q011h_coefficients_transfer_to_repaired_map"]
    assert not consequence["forced_ssm_exists_or_is_unique"]


def test_q011i_cycle_is_strict_json_with_reproducible_digests(
    q011i_cycle: dict[str, object],
) -> None:
    json.dumps(q011i_cycle, allow_nan=False)
    assert q011i_cycle["input_digest_sha256"] == (
        "81a1dc3f9fe934d8e9391dbfe6b80701d68c04b7db954da2f62e92b581dd5b51"
    )
    assert q011i_cycle["repair_digest_sha256"] == (
        "910a82fa1485ce8ad6b488c5bb71ad0c8bcb12b98b6202ebc3805caa8f4a3239"
    )
    assert q011i_cycle["fixed_point_digest_sha256"] == (
        "3adfbcfc7d5e9c3396bbfb60b8d10dce6ff080b90097b82f40b4c057b8518f1e"
    )
    assert q011i_cycle["spectrum_digest_sha256"] == (
        "5e63b9cc22a662238391dc83b8de1a81eb259af25b3ad2335e481bb0cf83466d"
    )
    assert q011i_cycle["result_digest_sha256"] == (
        "ac94658b95d2ae1f190fab57af3bd80dbf50a4addd37f6bb7bee27d6aa1d2398"
    )
    assert q011i_cycle["result_digest_sha256"] == q011i.q011b._canonical_json_sha256(
        q011i._result_digest_sections(q011i_cycle)
    )


def test_q011i_artifact_records_the_exact_zero_mean_repair() -> None:
    runner_path = Path(q011i.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011i_exact_zero_mean_repair.json"
    if not artifact_path.exists():
        pytest.skip("Q011i artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011i_exact_zero_mean_repair.py",
        "sha256": "2cec0472422ba02bb925e8c90336000058def7c36303479a4037405f873b9b88",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == q011i.q011b._canonical_json_sha256(
        q011i._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
