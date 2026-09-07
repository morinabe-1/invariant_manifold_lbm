"""Independent algebra, guard, selection, and same-initial controls for Q012e."""

import copy
from fractions import Fraction

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_amplitude as a
from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import d3q27_negative_control as degree
from research import q012d_d3q27_quadratic_chart as prior
from research import q012e_d3q27_amplitude as runner


@pytest.fixture(scope="module")
def model():
    return chart.build_chart()


def test_sealed_previous_rejections_and_all_coefficient_inputs():
    assert runner.input_audit()["passed"]


@pytest.mark.parametrize("t", [0.03, -0.04, 0.7, -0.6])
def test_exact_local_rational_remainder_independent_direct_equilibrium(t):
    rng = np.random.default_rng(601)
    v, h = rng.normal(scale=0.01, size=(2, 3, 4, 5, 27))
    path = a.rational_path(v, h)
    first, second = a.moments(v), a.moments(h)
    rho = 1 + t * first[..., 0] + t**2 * second[..., 0]
    j = t * first[..., 1:] + t**2 * second[..., 1:]
    direct = degree.momentum_quadratic(j, j) / rho[..., None]
    polynomial = t**2 * path.a2 + t**3 * path.a3 + t**4 * path.a4
    np.testing.assert_allclose(polynomial + path.tail(t), direct, atol=2e-19, rtol=2e-14)
    equilibrium = d3.equilibrium(rho, j)
    linear = d3.WEIGHTS * (rho[..., None] + 3 * np.einsum("...d,qd->...q", j, d3.VELOCITIES))
    np.testing.assert_allclose(equilibrium - linear, direct, atol=2e-16, rtol=1e-9)


def test_density_guard_and_unresolved_ratios_are_not_success():
    shape = (1, 1, 1, 27)
    path = a.RationalPath(
        np.array([[[[-2.0]]]]), np.zeros((1, 1, 1, 1)), *(np.zeros(shape) for _ in range(3))
    )
    with pytest.raises(ValueError, match="nonpositive"):
        path.tail(1)
    assert a.ratio(0, 0, 1e-12) is None
    assert a.ratio(1, 1e-13, 1e-12) is None
    assert a.ratio(0, 1, 1e-12) == 0


def test_rational_tail_identity_in_exact_arithmetic_all_27_populations():
    r, s = Fraction(1, 7), Fraction(-2, 9)
    j1 = [Fraction(1, 11), Fraction(-2, 13), Fraction(3, 17)]
    j2 = [Fraction(-1, 19), Fraction(1, 23), Fraction(2, 29)]
    dot = lambda left, right: sum(x * y for x, y in zip(left, right, strict=True))
    for velocity, weight in zip(d3.VELOCITIES, d3.EXACT_WEIGHTS, strict=True):
        c = [int(v) for v in velocity]
        q = lambda left, right, c=c, weight=weight: (
            weight
            * (Fraction(9, 2) * dot(c, left) * dot(c, right) - Fraction(3, 2) * dot(left, right))
        )
        a2, q12, q22 = q(j1, j1), q(j1, j2), q(j2, j2)
        a3, a4 = 2 * q12 - r * a2, q22 - 2 * r * q12 + (r * r - s) * a2
        for t in (Fraction(3, 4), Fraction(-1, 2)):
            rho = 1 + t * r + t * t * s
            j = [t * x + t * t * y for x, y in zip(j1, j2, strict=True)]
            tail = -(t**5) * (r * a4 + s * a3 + t * s * a4) / rho
            assert rho > 0
            assert t * t * a2 + t**3 * a3 + t**4 * a4 + tail == q(j, j) / rho


def test_macro_norm_weights_and_observables():
    dm = np.array([[2.0, 1.0, 2.0, 2.0]])
    assert a.macro_norm(dm) == pytest.approx(np.sqrt(31))
    rho = np.ones((2, 3, 4))
    j = np.broadcast_to([0.03, 0.0, 0.0], (2, 3, 4, 3))
    obs, _ = a.observables(d3.equilibrium(rho, j))
    assert obs["maximum_mach"] == pytest.approx(0.03 / np.sqrt(d3.CS2))


def test_full_defect_rational_identity_and_degree_parity(model):
    u = chart.normalized_directions(a.SEEDS["calibration"], 8)[0]
    terms = a.path_terms(model, u)
    for t in (0.008, -0.032, 0.128):
        row = a.one_step(model, terms, t)
        assert row["in_domain"] and row["identity_passed"]
        assert row["term_norms"][1] == pytest.approx(abs(t) ** 3 * degree.norm(terms.c3))
        assert row["term_norms"][2] == pytest.approx(t**4 * degree.norm(terms.c4))
        gram = np.array(row["term_gram"])
        np.testing.assert_allclose(np.diag(gram), np.array(row["term_norms"]) ** 2, rtol=1e-13)


def test_same_initial_linear_and_quadratic_trace_has_no_initial_error(model):
    a0 = 0.008 * chart.normalized_directions(a.SEEDS["calibration"], 8)[0]
    record = a.trajectory_case(model, a0, steps=2)
    assert record["complete"]
    first = record["trace"][0]
    assert first["population_error"] == first["linear_population_error"] == 0
    assert first["macro_error"] == first["linear_macro_error"] == 0
    f0 = model.embed(a0)
    full1 = prior.map_step(model, f0)
    lin1 = model.base + prior.linear_step(model, f0 - model.base)
    second = record["trace"][1]
    assert second["linear_population_error"] == degree.norm(full1 - lin1)
    assert second["population_error"] == degree.norm(full1 - model.embed(model.reduced(a0)))
    assert record["initial_population_perturbation_norm"] == degree.norm(f0 - model.base)


def test_full_linear_baseline_is_derivative_not_bgk_map(model):
    rng = np.random.default_rng(611)
    h = rng.normal(scale=0.01, size=model.base.shape)
    eps = 1e-4
    direct = (
        prior.map_step(model, model.base + eps * h) - prior.map_step(model, model.base - eps * h)
    ) / (2 * eps)
    assert damping.relative_error(direct, prior.linear_step(model, h)) < 1e-8


def test_initial_guard_stops_without_fabricated_future_steps(model, monkeypatch):
    fake = model.base.copy()
    fake[0, 0, 0, 0] = -0.01
    monkeypatch.setattr(model, "embed", lambda _a: fake.copy())
    row = a.trajectory_case(model, np.zeros(104))
    assert len(row["trace"]) == 1
    assert not row["complete"]
    assert row["stop_reason"]["step"] == 0
    assert row["execution_error"] is None


def test_numerical_failure_is_distinct_from_domain_failure(model, monkeypatch):
    def fail(*_):
        raise FloatingPointError("manufactured overflow")

    monkeypatch.setattr(prior, "map_step", fail)
    row = a.trajectory_case(model, np.zeros(104))
    assert not row["complete"]
    assert len(row["trace"]) == 1
    assert row["execution_error"]["type"] == "FloatingPointError"


def test_calibration_prefix_does_not_jump_over_failed_or_missing_case():
    rows = [
        {
            "group": "calibration",
            "direction_index": i,
            "amplitude": value,
            "sign": sign,
            "usage_passed": value != 0.128,
            "usage_gates": {"synthetic": value != 0.128},
        }
        for value in a.AMPLITUDES
        for i in range(8)
        for sign in (1, -1)
    ]
    inventory = a.amplitude_inventory(rows, "calibration")
    assert a.select_prefix(inventory) == [0.008, 0.032]
    assert inventory[-1]["passed"]
    rows.pop(0)
    assert a.select_prefix(a.amplitude_inventory(rows, "calibration")) == []
    assert a.select_prefix(a.amplitude_inventory(rows, "holdout")) == []


def test_execution_exception_preserves_failed_case(monkeypatch):
    def fail(*_):
        raise ValueError("manufactured failure")

    monkeypatch.setattr(a, "evaluate_case", fail)
    row = runner.guarded_case(None, None, "holdout", 4, 0.128, -1)
    assert a.case_key(row) == ("holdout", 4, 0.128, -1)
    assert not row["usage_passed"]
    assert row["execution_error"]["type"] == "ValueError"


def test_replay_rejects_same_process_and_altered_science(tmp_path):
    import json

    metadata = runner.metadata()
    records = [
        {"group": group, "direction_index": i, "amplitude": value, "sign": sign}
        for group, i, value, sign in a.REPLAY_CASES
    ]
    evidence = runner.replay_evidence({}, {}, records)
    stored = {
        **metadata,
        "kind": "independent_four_case_worker",
        "evidence": evidence,
        "evidence_digest_sha256": runner.q012a._digest(evidence),
    }
    path = tmp_path / "worker.json"
    path.write_text(json.dumps(stored), encoding="utf-8")
    assert not runner.replay_audit(path, evidence, metadata)["passed"]
    current = {**metadata, "process_id": metadata["process_id"] + 1}
    assert runner.replay_audit(path, evidence, current)["passed"]
    changed = copy.deepcopy(evidence)
    changed["records"][0]["sign"] = -1
    assert not runner.replay_audit(path, changed, current)["passed"]
