"""Exact residual controls including both directions of floating-point misclassification."""

import subprocess
import sys
from fractions import Fraction

import numpy as np
import pytest

from research import d3q27_cubic as cubic
from research import d3q27_exact_residual as exact
from research import q012f1a_d3q27_exact_residual as runner


def test_prior_sealed_inputs():
    assert runner.input_audit()["passed"]


def test_all_registered_exact_controls_and_both_false_decisions():
    result = exact.known_controls()
    assert result["passed"] and len(result["records"]) == 10
    rows = {r["name"]: r for r in result["records"]}
    assert rows["false_float_acceptance"]["proof"]["gates"]["legacy"]
    assert not rows["false_float_acceptance"]["proof"]["gates"]["exact_residual_exact_denominator"]
    assert rows["false_float_rejection"]["proof"]["evaluation_only_mismatch"]
    assert rows["binary_boundary"]["proof"]["gates"]["exact_residual_exact_denominator"]
    assert not rows["binary_boundary"]["proof"]["gates"]["exact_decimal_constants"]


def test_ieee_decoder_against_independent_builtin_ratio():
    values = [
        0.0,
        -0.0,
        1.0,
        -1.0,
        np.nextafter(0.0, 1.0),
        -np.nextafter(0.0, 1.0),
        np.finfo(float).max,
        exact.TOLERANCE,
    ]
    rng = np.random.default_rng(2026090724)
    for bits in rng.integers(0, np.iinfo(np.uint64).max, 256, dtype=np.uint64):
        value = np.array([bits], dtype=np.uint64).view(np.float64)[0]
        if np.isfinite(value):
            values.append(value)
    for value in values:
        numerator, exponent = exact.binary64_parts(value)
        assert Fraction(numerator, 2**exponent) == Fraction.from_float(float(value))
    for value in (np.inf, -np.inf, np.nan):
        with pytest.raises(ValueError):
            exact.binary64_parts(value)


@pytest.mark.parametrize("shape", [(1, 1), (3, 2), (5, 4)])
def test_independent_kernels_on_complex_dyadic_problems(shape):
    n, m = shape
    rng = np.random.default_rng(2026090725)
    array = lambda s: (rng.integers(-31, 32, s) + 1j * rng.integers(-31, 32, s)) / 16
    a, d, f, x = array((n, n)), array((m, m)), array((n, m)), array((n, m))
    low = a @ x - x @ d + f
    high = exact.precision.residual_mpc(a, d, f, x)
    denominator = max(exact.FLOOR, float(np.linalg.norm(f)))
    first = exact.audit_gmp(a, d, f, x, low, high, denominator)
    second = exact.audit_integer(a, d, f, x, low, high, denominator)
    assert first == second
    assert first["mp128_agrees"]


def test_integer_kernel_does_not_call_gmp_conversion_or_residual(monkeypatch):
    def forbidden(*_):
        raise AssertionError("GMP path must not be reused")

    monkeypatch.setattr(exact, "gmp_parts", forbidden)
    monkeypatch.setattr(exact, "audit_gmp", forbidden)
    a = np.array([[1 + 2**-52]], dtype=complex)
    zero = np.zeros((1, 1), dtype=complex)
    f = np.array([[-(1 + 2**-51)]], dtype=complex)
    high = np.array([[2**-104]], dtype=complex)
    proof = exact.audit_integer(a, zero, f, a, zero, high, float(np.linalg.norm(f)))
    assert exact.rational(proof["norms_squared"]["exact_residual_norm_squared"]) == Fraction(
        1, 2**208
    )


@pytest.mark.parametrize("kernel", [exact.audit_gmp, exact.audit_integer])
def test_invalid_shapes_and_nonfinite_values_fail_closed(kernel):
    scalar = np.ones((1, 1), dtype=complex)
    with pytest.raises(ValueError):
        kernel(np.ones((1, 2)), scalar, scalar, scalar, scalar, scalar, 1.0)
    with pytest.raises(ValueError):
        kernel(np.full((1, 1), np.inf), scalar, scalar, scalar, scalar, scalar, 1.0)
    with pytest.raises(ValueError):
        kernel(scalar, scalar, scalar, scalar, scalar, scalar, 0.0)


def test_npz_is_nonpickled_byte_verified_and_nonoverwriting(tmp_path):
    path = tmp_path / "arrays.npz"
    arrays = {"complex": np.array([[1 + 2j, -0j]]), "real": np.array([1.0, -0.0])}
    meta = runner.save_arrays(path, arrays)
    assert meta["roundtrip_passed"]
    with np.load(path, allow_pickle=False) as saved:
        assert set(saved.files) == set(arrays)
        assert all(np.array_equal(saved[k], v) for k, v in arrays.items())
    with pytest.raises(FileExistsError):
        runner.save_arrays(path, arrays)
    for name, data in (("object", np.array([{}], dtype=object)), ("nan", np.array([np.nan]))):
        with pytest.raises(ValueError):
            runner.save_arrays(tmp_path / (name + ".npz"), {"invalid": data})
        assert not (tmp_path / (name + ".npz")).exists()


def test_json_nonfinite_and_overwrite_fail_without_data_loss(tmp_path):
    path = tmp_path / "data.json"
    with pytest.raises(ValueError):
        runner.write_json(path, {"bad": float("nan")})
    assert not path.exists()
    runner.write_json(path, {"valid": True})
    with pytest.raises(FileExistsError):
        runner.write_json(path, {"changed": True})
    assert runner.read_json(path) == {"valid": True}


def test_invalid_prior_stops_preparation(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": False})
    with pytest.raises(ValueError, match="not started"):
        runner.prepare(tmp_path / "prepared.json")
    assert not list(tmp_path.iterdir())


def test_cli_protects_existing_npz(tmp_path):
    path = tmp_path / "prepared.json"
    path.with_suffix(".npz").write_bytes(b"preserved")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.q012f1a_d3q27_exact_residual",
            "--prepare-output",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert path.with_suffix(".npz").read_bytes() == b"preserved"
    assert not path.exists()


def test_actual_refined_case_is_unchanged_and_exact_backends_agree():
    old = runner.read_json(runner.PRIOR_PATH)
    grid = next(g for g in old["cycle"]["grids"] if g["size"] == 65)
    rows = runner.previous.previous.read_records(
        runner.PRIOR_PATH.parent / grid["record_archive"]["filename"]
    )
    prior = next(r for r in rows if r["ordinal"] == 0)
    models, _ = runner.previous.build_inputs(65)
    context = cubic.build_context(models["paired"])
    arrays, denominator, audit = runner.rebuild_case(context, 0, prior["inputs"]["paired"])
    assert audit["passed"]
    values = [arrays[k] for k in exact.ARRAY_NAMES]
    assert exact.audit_gmp(*values, denominator) == exact.audit_integer(*values, denominator)
