from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.tensor_train import reconstruct, tt_svd
from ttim_lbm.tt_storage_prequalification import (
    TENSORIZATION_IDS,
    _candidate_decomposition,
    _dense_action,
    _ordered_tensor,
    _permutation_multiplicity,
    _relative_norm,
    _sparse_action,
    _tensorize,
    _tt_action,
    run_tt_storage_prequalification_audit,
)


@pytest.fixture(scope="module")
def tt_storage_audit():
    return run_tt_storage_prequalification_audit()


def test_ordered_expansion_and_all_registered_tt_actions_match_sparse_fibers() -> None:
    rng = np.random.default_rng(20260827)
    indices = np.asarray([[0, 0], [0, 1], [2, 3], [4, 4]], dtype=np.int64)
    multiplicities = np.asarray(
        [_permutation_multiplicity(index) for index in indices],
        dtype=np.int64,
    )
    coefficients = rng.normal(size=(len(indices), 9)) + 1j * rng.normal(
        size=(len(indices), 9)
    )
    vector = rng.normal(size=24) + 1j * rng.normal(size=24)
    tensor = _ordered_tensor(indices, coefficients, degree=2)
    expected = _sparse_action(indices, multiplicities, coefficients, vector)

    np.testing.assert_allclose(_dense_action(tensor, vector), expected, atol=2.0e-13)
    for candidate_id in TENSORIZATION_IDS:
        cores = tt_svd(_tensorize(tensor, candidate_id))
        np.testing.assert_allclose(
            _tt_action(cores, vector, candidate_id),
            expected,
            atol=5.0e-12,
        )


def test_d1q3_candidates_split_the_corresponding_flat_output_core() -> None:
    rng = np.random.default_rng(20260828)
    tensor = rng.normal(size=(9, 24, 24)) + 1j * rng.normal(size=(9, 24, 24))

    for candidate_id in ("d1q3-q-first", "d1q3-q-last"):
        candidate, cores, diagnostics = _candidate_decomposition(
            np.asarray(tensor, dtype=np.complex128),
            candidate_id,
        )

        assert "full-rank D1Q3 output-core split" in diagnostics[
            "construction_method"
        ]
        assert diagnostics["output_core_split"]["discarded_frobenius_norm"] == 0.0
        assert _relative_norm(reconstruct(cores) - candidate, candidate) <= 2.0e-13


def test_q008a_passes_all_validity_gates_and_rejects_storage_hypothesis(
    tt_storage_audit,
) -> None:
    assert tt_storage_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in tt_storage_audit["validity_gates"].values())
    assert tt_storage_audit["hypothesis_outcome"] == "rejected"
    assert tt_storage_audit["selected_candidate"] is None
    assert tt_storage_audit["scientific_classification"] == (
        "registered TT tensorizations do not beat natural quartic sparse-fiber storage"
    )


def test_q008a_records_registered_degree_counts_and_quartic_storage_loss(
    tt_storage_audit,
) -> None:
    records = {record["degree"]: record for record in tt_storage_audit["degree_records"]}

    assert {degree: records[degree]["fiber_count"] for degree in records} == {
        2: 300,
        3: 2600,
        4: 17550,
    }
    quartic = records[4]
    sparse = quartic["natural_sparse_fiber_storage"]
    assert sparse["coefficient_stored_real_scalar_count"] == 315900
    assert all(
        candidate["storage"]["core_stored_real_scalar_count"] > 10 * 315900
        and candidate["storage"]["uncompressed_npz_serialized_bytes"]
        > 10 * sparse["uncompressed_npz_serialized_bytes"]
        and not candidate["storage_hypothesis_passed"]
        for candidate in quartic["candidate_records"]
    )


def test_q008a_preserves_all_tensor_and_action_fidelity_bounds(
    tt_storage_audit,
) -> None:
    assert tt_storage_audit["validity_gates"]["ordered_dense_expansion"][
        "value"
    ] <= 5.0e-14
    candidates = [
        candidate
        for degree in tt_storage_audit["degree_records"]
        for candidate in degree["candidate_records"]
    ]
    assert all(candidate["fidelity_passed"] for candidate in candidates)
    assert max(
        candidate["relative_tensor_reconstruction_error"]
        for candidate in candidates
    ) <= 2.0e-13
    assert max(
        candidate["maximum_relative_action_error_vs_sparse"]
        for candidate in candidates
    ) <= 1.0e-11


def test_q008a_timing_is_recorded_as_diagnostic_only(tt_storage_audit) -> None:
    timing = tt_storage_audit["evaluation_benchmark"]

    assert timing["direction_count"] == 128
    assert timing["warmup_block_count"] == 2
    assert timing["measured_block_count"] == 7
    assert timing["acceptance_role"] == "diagnostic only"
    assert set(timing["method_records"]) == {"sparse-fiber", *TENSORIZATION_IDS}
    assert all(
        record["median_nanoseconds_per_sample"] > 0.0
        and len(record["nanoseconds_per_sample_by_block"]) == 7
        and record["median_checksum_relative_error_vs_sparse"] <= 1.0e-11
        for record in timing["method_records"].values()
    )
