"""Algebra, finite-map remainder and fail-closed checks for Q012d1."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import d3q27_negative_control as diagnostic
from research import q012a_d3q27_foundation as q012a
from research import q012d1_d3q27_negative_control as runner


def test_prior_full_chart_and_failed_control_remain_sealed() -> None:
    audit = runner.input_audit()
    assert audit["passed"], audit


def test_momentum_quadratic_matches_equilibrium_hessian() -> None:
    rng = np.random.default_rng(2026090716)
    left, right = rng.standard_normal((2, 3, 5, 7, 4))
    expected = np.einsum("qab,...a,...b->...q", d3.equilibrium_hessian_at_rest(), left, right) / 2
    np.testing.assert_allclose(
        diagnostic.momentum_quadratic(left[..., 1:], right[..., 1:]), expected, atol=2e-15
    )


def test_cubic_and_quartic_path_coefficients_with_independent_map_remainder() -> None:
    rng = np.random.default_rng(1234)
    shape = (3, 5, 7, 27)
    v, h = 0.1 * rng.standard_normal(shape), 0.05 * rng.standard_normal(shape)
    c3, c4, independent = diagnostic.nonlinear_path_coefficients(v, h, 1.5, 0.02, 2)
    np.testing.assert_allclose(c3, independent, atol=2e-15)
    base = d3.uniform_equilibrium(shape[:3], np.zeros(4))
    mapped_base = damping.periodic_step(base, 1.5, 0.02, 2)
    c1 = damping.apply_filter(d3.linearized_periodic_step(v, 1.5), 0.02, 2)
    c2 = damping.apply_filter(
        d3.linearized_periodic_step(h, 1.5) + 0.5 * damping.mixed_hessian(v, v, 1.5), 0.02, 2
    )
    amplitudes = (0.08, 0.04, 0.02)
    defects = []
    for t in amplitudes:
        actual = damping.periodic_step(base + t * v + t**2 * h, 1.5, 0.02, 2)
        predicted = mapped_base + t * c1 + t**2 * c2 + t**3 * c3 + t**4 * c4
        defects.append(np.linalg.norm(actual - predicted))
    slope = np.polyfit(np.log(amplitudes), np.log(defects), 1)[0]
    assert 4.8 < slope < 5.2, (slope, defects)


def test_analytic_cubic_is_odd_and_quartic_is_even() -> None:
    rng = np.random.default_rng(333)
    v, h = rng.standard_normal((2, 3, 3, 3, 27))
    positive = diagnostic.nonlinear_path_coefficients(v, h, 1.5, 0.02, 2)
    negative = diagnostic.nonlinear_path_coefficients(-v, h, 1.5, 0.02, 2)
    np.testing.assert_allclose(positive[0], -negative[0], atol=1e-12)
    np.testing.assert_allclose(positive[1], negative[1], atol=1e-12)


def test_density_only_paths_have_no_nonlinear_cubic_or_quartic() -> None:
    moments = np.zeros((3, 5, 7, 4))
    moments[..., 0] = 0.2
    v = np.einsum("qa,...a->...q", d3.equilibrium_tangent_matrix(), moments)
    results = diagnostic.nonlinear_path_coefficients(v, 2 * v, 1.5, 0.02, 2)
    assert max(np.linalg.norm(value) for value in results) < 1e-30


def test_gram_preserves_cross_term_signs_and_polynomial_norms() -> None:
    fields = (np.array([1.0, 2.0]), np.array([-2.0, 0.5]), np.array([3.0, -1.0]))
    gram = diagnostic.gram(fields)
    assert gram[0, 1] < 0
    for t in (0.08, -0.08):
        powers = np.array([t**2, t**3, t**4])
        vector = sum(power * value for power, value in zip(powers, fields))
        assert np.isclose(powers @ gram @ powers, np.linalg.norm(vector) ** 2, rtol=1e-14)


def test_fit_window_does_not_use_other_amplitudes_or_signs() -> None:
    samples = [
        {
            "amplitude": a,
            "sign": sign,
            "roundoff_floor": 1e-15,
            "dropped_norm": a ** (2 if sign == 1 else 3),
        }
        for a in diagnostic.AMPLITUDES
        for sign in (1, -1)
    ]
    positive = diagnostic.fit_window(samples, diagnostic.ASYMPTOTIC_AMPLITUDES, 1, "dropped_norm")
    negative = diagnostic.fit_window(samples, diagnostic.ORIGINAL_AMPLITUDES, -1, "dropped_norm")
    assert positive["passed"] and abs(positive["slope"] - 2) < 1e-12
    assert not negative["passed"] and abs(negative["slope"] - 3) < 1e-12


def test_roundoff_buried_raw_control_is_not_accepted() -> None:
    samples = [
        {"amplitude": a, "sign": 1, "roundoff_floor": 1e-13, "dropped_norm": 1e-15}
        for a in diagnostic.AMPLITUDES
    ]
    result = diagnostic.fit_window(samples, diagnostic.ASYMPTOTIC_AMPLITUDES, 1, "dropped_norm")
    assert result["slope"] is None and not result["passed"]


def test_invalid_inputs_do_not_rebuild_the_chart(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": False})

    def forbidden():
        raise AssertionError("sealed input failure must stop computation")

    monkeypatch.setattr(chart, "build_chart", forbidden)
    result = runner.run_experiment()
    assert result["records"] == [] and result["coefficient_rebuild"] is None
    assert not result["asymptotic_resolved"] and not any(result["hypothesis_gates"].values())


def test_replay_rejects_same_process_and_modified_experiment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    experiment = {"value": 1}
    experiment["result_digest_sha256"] = q012a._digest(experiment)
    metadata = {"process_id": 12, "source": {}, "runner_source": {}, "helper_sources": {}}
    stored = {**metadata, "kind": "independent_experiment_worker", "experiment": experiment}
    monkeypatch.setattr(runner, "_file_sha256", lambda path: "test-only")
    monkeypatch.setattr(runner.json, "loads", lambda value: copy.deepcopy(stored))
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: "mock worker")
    same = runner.replay_audit(Path("worker.json"), experiment, metadata)
    assert not same["passed"] and not same["checks"]["separate_process"]
    metadata["process_id"] = 13
    assert runner.replay_audit(Path("worker.json"), experiment, metadata)["passed"]
    changed = {"value": 2}
    changed["result_digest_sha256"] = q012a._digest(changed)
    result = runner.replay_audit(Path("worker.json"), changed, metadata)
    assert not result["passed"] and not result["checks"]["all_experiment_values_reproduced"]
