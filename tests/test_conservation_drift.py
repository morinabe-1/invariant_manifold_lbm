from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.conservation_drift import (
    compensated_conserved_quantities,
    run_conservation_drift_audit,
)


@pytest.fixture(scope="module")
def conservation_audit():
    return run_conservation_drift_audit()


def test_compensated_conserved_quantities_resolves_cancellation() -> None:
    state = np.zeros((1, 3, 9), dtype=np.float64)
    state[0, :, 0] = [1.0e16, 1.0, -1.0e16]

    faithful, neumaier = compensated_conserved_quantities(state)

    np.testing.assert_array_equal(faithful, [1.0, 0.0, 0.0])
    np.testing.assert_array_equal(neumaier, faithful)


def test_compensated_conserved_quantities_checks_state_shape() -> None:
    with pytest.raises(ValueError, match="shape"):
        compensated_conserved_quantities(np.zeros((17, 17, 8)))


def test_q006j_reproduces_q006i_and_passes_every_validity_gate(
    conservation_audit,
) -> None:
    summary = conservation_audit["summary"]

    assert conservation_audit["study_validity"] == "passed"
    assert all(
        gate["passed"] for gate in conservation_audit["validity_gates"].values()
    )
    assert summary["trajectory_count"] == 64
    assert summary["stage_record_count"] == 6400
    assert summary["checkpoint_record_count"] == 512
    assert summary["maximum_numpy_conservation_drift"]["norm"] == pytest.approx(
        2.728496323152741e-12
    )
    assert summary["maximum_independent_sum_component_difference"] == 0.0
    assert summary["maximum_stage_map_identity_error"] == 0.0
    assert summary["maximum_stage_reconstruction_error"] == 0.0


def test_q006j_localizes_state_drift_but_rejects_the_projection_control(
    conservation_audit,
) -> None:
    summary = conservation_audit["summary"]

    assert conservation_audit["hypothesis_outcome"] == "rejected"
    assert conservation_audit["scientific_classification"] == (
        "structural or unresolved conservation defect"
    )
    assert summary["maximum_fsum_conservation_drift"]["norm"] > 1.0e-12
    assert summary["maximum_streaming_fsum_drift"] == 0.0
    assert summary["stage_statistics"]["collision"][
        "maximum_cumulative_signed_norm"
    ] == pytest.approx(2.671642026004203e-12)
    assert summary["stage_statistics"]["filter"][
        "maximum_cumulative_signed_norm"
    ] == pytest.approx(5.11594502419624e-13)
    failed_projection_gates = [
        name
        for name, gate in conservation_audit["projection_gates"].items()
        if not gate["passed"]
    ]
    assert failed_projection_gates == ["projected_conservation"]
    assert summary["projection_control"][
        "maximum_compensated_conservation_drift"
    ] == pytest.approx(2.1600518690316044e-12)
    assert summary["projection_control"]["minimum_population"] > 0.0


def test_q006j_result_is_strict_json(conservation_audit) -> None:
    json.dumps(conservation_audit, allow_nan=False)
