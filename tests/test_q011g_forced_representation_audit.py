from __future__ import annotations

import json
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest

import research.q011g_forced_representation_audit as q011g
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011g_data() -> q011g.CoefficientData:
    sealed, artifact = q011g._sealed_q011f1_artifact_audit()
    assert sealed["passed"]
    return q011g._coefficient_data(artifact)


def test_q011g_seals_the_accepted_shadowing_reissue() -> None:
    audit, artifact = q011g._sealed_q011f1_artifact_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["artifact"]["hypothesis_outcome"] == "accepted"
    assert audit["preserved_q011f_artifact"]["hypothesis_outcome"] == "rejected"
    assert artifact["source"]["package_source_sha256"] == (q011g.SEALED_PACKAGE_SOURCE_SHA256)


def test_q011g_natural_fourier_projection_has_registered_storage(
    q011g_data: q011g.CoefficientData,
) -> None:
    audit = q011g_data.coefficient_audit
    storage = audit["natural_storage"]

    assert q011g_data.reconstruction_audit["passed"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["sector_pair_counts"] == {
        "0": 102,
        "1": 54,
        "16": 54,
        "2": 45,
        "15": 45,
    }
    assert storage["coefficient_complex_entry_count"] == 47_484
    assert storage["coefficient_stored_real_scalar_count"] == 94_968
    assert storage["raw_array_payload_bytes"] == 760_644
    assert storage["serialization_roundtrip_bitwise_equal"]


def test_q011g_polynomial_and_hessian_conventions_roundtrip() -> None:
    pairs = np.asarray(
        list(combinations_with_replacement(range(q011g.SELECTED_DIMENSION), 2)),
        dtype=np.int64,
    )
    generator = np.random.default_rng(20260904)
    raw = generator.standard_normal((3, 24, 24)) + 1j * generator.standard_normal((3, 24, 24))
    hessian = np.asarray(0.5 * (raw + raw.swapaxes(1, 2)), dtype=np.complex128)

    polynomial = q011g._polynomial_coefficients(hessian, pairs)
    reconstructed = q011g._hessian_from_polynomial(polynomial, pairs, (3,))

    assert np.array_equal(reconstructed, hessian)


def test_q011g_all_registered_tensorizations_are_bitwise_reversible(
    q011g_data: q011g.CoefficientData,
) -> None:
    for candidate_id in q011g.TT_CANDIDATE_IDS:
        w_tensorized = q011g._tensorize_w(q011g_data.w_tensor, candidate_id)
        r_tensorized = q011g._tensorize_r(q011g_data.r_tensor, candidate_id)

        assert np.array_equal(
            q011g._untensorize_w(w_tensorized, candidate_id),
            q011g_data.w_tensor,
        )
        assert np.array_equal(
            q011g._untensorize_r(r_tensorized, candidate_id),
            q011g_data.r_tensor,
        )


def test_q011g_natural_and_dense_joint_actions_match_real_chart(
    q011g_data: q011g.CoefficientData,
) -> None:
    direction = q011g._normalized_directions(20260905, 1)[0]
    complex_direction = q011g_data.coordinate_map @ direction
    sparse = q011g._natural_action(q011g_data, complex_direction)
    dense = q011g._dense_action(q011g_data, complex_direction)
    w_real, r_real, imaginary = q011g._physical_actions(q011g_data, sparse)
    expected_w = 0.5 * np.einsum(
        "nij,i,j->n",
        q011g_data.model.hessian,
        direction,
        direction,
        optimize=True,
    )
    expected_r = 0.5 * np.einsum(
        "rij,i,j->r",
        q011g_data.model.reduced_hessian,
        direction,
        direction,
        optimize=True,
    )

    assert q011g._joint_relative_error(dense, sparse) <= (q011g.MAXIMUM_SPARSE_DENSE_ACTION_ERROR)
    assert q011g._joint_relative_error((w_real, r_real), (expected_w, expected_r)) <= (
        q011g.MAXIMUM_REALIFICATION_ACTION_ERROR
    )
    assert imaginary <= q011g.MAXIMUM_REALIFICATION_ACTION_ERROR


def test_q011g_conservative_break_even_uses_adverse_envelopes() -> None:
    assert q011g._conservative_break_even(100.0, 3.0, 20.0, 5.0) == 40
    assert q011g._conservative_break_even(10.0, 3.0, 20.0, 5.0) == 0
    assert q011g._conservative_break_even(100.0, 5.0, 20.0, 5.0) is None


def test_q011g_tt_memory_footprint_counts_owned_core_payload() -> None:
    w_cores = [np.ones((1, 3, 2)), np.ones((2, 4, 1))]
    r_cores = [np.ones((1, 5, 1))]

    storage = q011g._tt_bundle_storage(w_cores, r_cores)

    assert storage["in_memory_object_bytes"] > storage["raw_array_payload_bytes"]
    assert storage["core_payload_bytes"] == sum(core.nbytes for core in (*w_cores, *r_cores))


def test_q011g_artifact_seals_the_registered_representation_campaign() -> None:
    runner_path = Path(q011g.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / ("q011g_forced_representation_audit.json")
    if not artifact_path.exists():
        pytest.skip("Q011g artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "842ddbae2a28ccd2f11a112f23205cb049668b82691fdd180edc5ac20fecaa25"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011g_forced_representation_audit.py",
        "sha256": ("84ed56dabd0b0f870f1c6b27c9907c9566439ff03affe5aacc61ba611f4678fe"),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["scientific_classification"] == (
        "registered TT-SVD bundles do not beat the natural Fourier-sparse forced-quadratic baseline"
    )
    assert len(cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 4
    assert [name for name, gate in cycle["hypothesis_gates"].items() if gate["passed"]] == [
        "all_candidate_fidelity_and_residual_gates_pass"
    ]
    assert cycle["selection_audit"]["natural_sparse_baseline_remains_mandatory"]
    assert cycle["selection_audit"]["storage_winner_ids"] == []
    assert cycle["selection_audit"]["robust_timing_winner_ids"] == [
        "flat-output-last",
        "fourier-output-last",
        "d1q3-output-last",
    ]
    assert cycle["selection_audit"]["joint_winner_ids"] == []
    assert cycle["selection_audit"]["selected_candidate_id"] is None
    assert (
        cycle["natural_fourier_coefficient_audit"]["natural_storage"][
            "coefficient_stored_real_scalar_count"
        ]
        == 94_968
    )
    assert all(
        record["storage"]["in_memory_object_bytes"] > record["storage"]["raw_array_payload_bytes"]
        for method_id, record in cycle["offline_cost_campaign"]["method_records"].items()
        if method_id in q011g.TT_CANDIDATE_IDS
    )
    assert cycle["input_digest_sha256"] == (
        "0632be40fccc212f23a271fa00ed80696f9a146a1b107e513b3a47edb9870a20"
    )
    assert cycle["coefficient_digest_sha256"] == (
        "fc9edec10ee22abfaa2b763be9f69c9d72bfc59543aa34faea6ab206c35ab264"
    )
    assert cycle["fidelity_digest_sha256"] == (
        "30dabea285da9070e2ebc0b351afde4695deb275d5f96ee66de1b1ca0468fcad"
    )
    assert cycle["cost_digest_sha256"] == (
        "222a42321f4ae814478cc65102afcbc8926754d8cb7c48ed8ca2952e350767a7"
    )
    assert cycle["result_digest_sha256"] == (
        "e0874eabe2c5b924d0b5d7b56533cd695406166d4370b493a0dabdc0b22dbb2a"
    )
    assert cycle["result_digest_sha256"] == (
        q011g.q011e.q011c._canonical_json_sha256(q011g._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
