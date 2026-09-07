from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from research import d3q27_damping as damping
from research import d3q27_quadratic as q
from research import d3q27_svd_fallback as f
from research import q012c1a_d3q27_damping as runner


@pytest.fixture(scope="module")
def context() -> damping.CoefficientContext:
    return damping.build_context(17, 1.0)


def test_input_seals_preserve_prior_inconclusive() -> None:
    assert runner.input_audit()["passed"]


def test_registered_backend_controls() -> None:
    control = f.backend_controls(runner.prior_artifact()["cycle"]["numerical_failure"])
    assert control["passed"] and len(control["gates"]) == 4
    assert len(control["repetitions"]) == 3
    assert all(r["backend"]["driver"] == "gesvd" for r in control["repetitions"])


def test_normal_pairs_retain_original_metrics_exactly(context: damping.CoefficientContext) -> None:
    for eta in (0.0, 0.05):
        for left, right in (
            (context.blocks[0], context.blocks[1]),
            (context.blocks[0], context.blocks[0]),
            (context.blocks[20], context.blocks[-1]),
        ):
            original = damping.audit_scaled_pair(left, right, context, eta, 2)
            actual, backend = f.audit_pair(left, right, context, eta, 2)
            assert actual == original
            assert backend == {"driver": "gesdd", "fallback": False, "passed": True}


def test_only_actual_obstruction_uses_fallback(context: damping.CoefficientContext) -> None:
    left = context.frames[(-1, 1, 0)].blocks[0]
    right = context.frames[(-1, 1, 1)].blocks[0]
    with pytest.raises(np.linalg.LinAlgError, match="SVD did not converge"):
        damping.audit_scaled_pair(left, right, context, 0.1, 1)
    record, backend = f.audit_pair(left, right, context, 0.1, 1)
    assert record["passed"] and backend["passed"] and backend["fallback"]
    assert 36 < record["condition_number"] < 37
    assert record["solve_relative_residual"] < 1e-12
    assert backend["original_error"] == "SVD did not converge"
    assert backend["reconstruction_relative_error"] < 1e-12
    assert record["left_wave"] == [-1, 1, 0] and record["right_wave"] == [-1, 1, 1]


def test_normal_failure_does_not_switch_for_a_better_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("no alternative allowed after normal convergence")

    monkeypatch.setattr(f, "svd", forbidden)
    _, record, backend = f.solve_with_fallback(
        np.diag((0.49 + 1e-11, 0.2)), np.array([[0.49]]), np.ones((2, 1))
    )
    assert not record["passed"] and record["condition_number"] > 1e8
    assert not backend["fallback"]
    residual_failure = {
        "status": "nonsingular_practical",
        "solve_relative_residual": 1e-9,
        "passed": False,
    }
    monkeypatch.setattr(q, "solve_homological", lambda *a: (np.zeros((2, 1)), residual_failure))
    _, record, backend = f.solve_with_fallback(np.eye(2), np.eye(1), np.ones((2, 1)))
    assert record is residual_failure and not record["passed"] and not backend["fallback"]


def test_injected_nonconvergence_uses_same_operator_and_only_one_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_svd = f.svd
    calls = []
    output, inputs, forcing = np.diag((0.2, 0.3)), np.array([[0.49]]), np.ones((2, 1))
    operator = q.homological_operator(output, inputs)

    def fail(*args):
        raise np.linalg.LinAlgError("SVD did not converge")

    def tracked(matrix, **kwargs):
        assert matrix.tobytes() == operator.tobytes()
        calls.append(kwargs["lapack_driver"])
        return original_svd(matrix, **kwargs)

    monkeypatch.setattr(q, "solve_homological", fail)
    monkeypatch.setattr(f, "svd", tracked)
    _, record, backend = f.solve_with_fallback(output, inputs, forcing)
    assert record["passed"] and backend["fallback"] and calls == ["gesvd"]


def test_unrelated_error_is_not_misclassified_as_svd_nonconvergence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args):
        raise np.linalg.LinAlgError("eigenvalues did not converge")

    monkeypatch.setattr(q, "solve_homological", fail)
    with pytest.raises(np.linalg.LinAlgError, match="eigenvalues did not converge"):
        f.solve_with_fallback(np.eye(2), np.eye(1), np.ones((2, 1)))


def test_two_failed_drivers_do_not_produce_a_solution(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args, **kwargs):
        raise np.linalg.LinAlgError("SVD did not converge")

    monkeypatch.setattr(q, "solve_homological", fail)
    monkeypatch.setattr(f, "svd", fail)
    with pytest.raises(np.linalg.LinAlgError, match="SVD did not converge"):
        f.solve_with_fallback(np.eye(2), np.eye(1), np.ones((2, 1)))


def test_corrupt_factors_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    original = f.svd

    def corrupt(*args, **kwargs):
        u, s, vh = original(*args, **kwargs)
        return 2 * u, s, vh

    monkeypatch.setattr(f, "svd", corrupt)
    with pytest.raises(np.linalg.LinAlgError, match="factor integrity"):
        f.solve_gesvd(np.diag((0.2, 0.3)), np.array([[0.49]]), np.ones((2, 1)))


@pytest.mark.parametrize(
    "rhs,status", [([0.0, 1.0], "singular_compatible"), ([1.0, 0.0], "singular_incompatible")]
)
def test_alternative_cannot_cure_true_singular_cases(rhs: list, status: str) -> None:
    _, record, integrity = f.solve_gesvd(
        np.diag((0.49, 0.2)), np.array([[0.49]]), np.array(rhs)[:, None]
    )
    assert record["status"] == status and not record["passed"] and integrity["passed"]


def test_invalid_inputs_do_not_produce_tables(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": False})
    result = runner.run_study(tmp_path / "tables")
    assert result["study_gate"] == "failed" and result["scientific_outcome"] == "inconclusive"
    assert result["cycle"]["conditions"] == [] and not (tmp_path / "tables").exists()
