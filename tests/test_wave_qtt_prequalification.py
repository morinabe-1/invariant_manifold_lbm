from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.tensor_train import tt_svd
from ttim_lbm.tt_storage_prequalification import _dense_action
from ttim_lbm.wave_qtt_prequalification import (
    CANDIDATE_IDS,
    _dense_candidate_action,
    _tensorize_wave_qtt,
    _tt_candidate_action,
    _untensorize_wave_qtt,
    run_wave_qtt_prequalification_audit,
)


@pytest.fixture(scope="module")
def wave_qtt_audit():
    return run_wave_qtt_prequalification_audit()


def test_registered_tensorizations_are_bitwise_invertible_and_preserve_actions() -> None:
    rng = np.random.default_rng(20260829)
    tensor = np.asarray(
        rng.normal(size=(9, 24, 24)) + 1j * rng.normal(size=(9, 24, 24)),
        dtype=np.complex128,
    )
    vector = np.asarray(
        rng.normal(size=24) + 1j * rng.normal(size=24),
        dtype=np.complex128,
    )
    expected = _dense_action(tensor, vector)

    for candidate_id in CANDIDATE_IDS:
        candidate = _tensorize_wave_qtt(tensor, candidate_id)
        assert np.array_equal(
            _untensorize_wave_qtt(candidate, candidate_id),
            tensor,
        )
        np.testing.assert_allclose(
            _dense_candidate_action(candidate, vector, candidate_id),
            expected,
            rtol=2.0e-13,
            atol=2.0e-13,
        )
        cores = tt_svd(candidate)
        np.testing.assert_allclose(
            _tt_candidate_action(cores, vector, candidate_id),
            expected,
            rtol=2.0e-13,
            atol=2.0e-12,
        )


def test_q008c_passes_all_validity_gates(wave_qtt_audit) -> None:
    assert wave_qtt_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in wave_qtt_audit["validity_gates"].values())
    assert wave_qtt_audit["hypothesis_outcome"] == "rejected"
    assert wave_qtt_audit["selected_candidate"] is None
    assert wave_qtt_audit["scientific_classification"] == (
        "registered wave-factorized TTs do not beat natural quartic sparse-fiber storage"
    )


def test_q008c_reproduces_registered_inputs_and_flat_control(wave_qtt_audit) -> None:
    assert wave_qtt_audit["input_registration"][
        "action_direction_duplicate_count_vs_q008a"
    ] == 0
    records = {record["degree"]: record for record in wave_qtt_audit["degree_records"]}
    assert {degree: records[degree]["fiber_count"] for degree in records} == {
        2: 300,
        3: 2600,
        4: 17550,
    }
    assert all(
        record["flat_q_last_control"]["registered_identity_exact"]
        and record["flat_q_last_control"]["fidelity_passed"]
        for record in records.values()
    )


def test_q008c_preserves_all_mapping_tensor_and_action_bounds(wave_qtt_audit) -> None:
    candidates = [
        candidate
        for degree in wave_qtt_audit["degree_records"]
        for candidate in degree["candidate_records"]
    ]
    assert all(candidate["mapping_roundtrip_bitwise_equal"] for candidate in candidates)
    assert max(
        candidate["maximum_relative_dense_mapping_action_error"]
        for candidate in candidates
    ) <= 5.0e-14
    assert all(candidate["fidelity_passed"] for candidate in candidates)
    assert max(
        candidate["relative_tensor_reconstruction_error"] for candidate in candidates
    ) <= 2.0e-13
    assert max(
        candidate["maximum_relative_action_error_vs_sparse"]
        for candidate in candidates
    ) <= 1.0e-11


def test_q008c_records_valid_quartic_storage_rejection(wave_qtt_audit) -> None:
    quartic = next(
        record for record in wave_qtt_audit["degree_records"] if record["degree"] == 4
    )
    sparse = quartic["natural_sparse_fiber_storage"]
    candidates = {record["candidate_id"]: record for record in quartic["candidate_records"]}

    assert sparse["coefficient_stored_real_scalar_count"] == 315900
    assert sparse["uncompressed_npz_serialized_bytes"] == 2615734
    assert candidates["wave-branch-tuple-major"]["storage"][
        "core_stored_real_scalar_count"
    ] == 4465748
    assert candidates["wave-qtt-tuple-major"]["storage"][
        "core_stored_real_scalar_count"
    ] == 8121540
    assert all(
        candidate["storage"]["core_stored_real_scalar_count"] > 14 * 315900
        and candidate["storage"]["uncompressed_npz_serialized_bytes"]
        > 13 * sparse["uncompressed_npz_serialized_bytes"]
        and not candidate["storage_hypothesis_passed"]
        for candidate in candidates.values()
    )


def test_q008c_timing_is_diagnostic_only(wave_qtt_audit) -> None:
    timing = wave_qtt_audit["evaluation_benchmark"]

    assert timing["direction_count"] == 128
    assert timing["warmup_block_count"] == 2
    assert timing["measured_block_count"] == 7
    assert timing["acceptance_role"] == "diagnostic only"
    assert set(timing["method_records"]) == {
        "sparse-fiber",
        "flat-q-last-control",
        *CANDIDATE_IDS,
    }
    assert all(
        record["median_nanoseconds_per_sample"] > 0.0
        and len(record["nanoseconds_per_sample_by_block"]) == 7
        and record["median_checksum_relative_error_vs_sparse"] <= 1.0e-11
        for record in timing["method_records"].values()
    )
