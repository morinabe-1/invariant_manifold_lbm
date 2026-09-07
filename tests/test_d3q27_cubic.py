"""Independent cubic multiplicity, forcing, solver, and archival controls."""

import subprocess
import sys
from itertools import combinations_with_replacement
from math import factorial

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_damping as damping
from research import q012f_d3q27_cubic_preflight as runner


@pytest.fixture(scope="module")
def context():
    return cubic.build_context(chart.build_chart())


def test_sealed_q012e_and_previous_rejections():
    assert runner.input_audit()["passed"]


@pytest.mark.parametrize("groups", [(0, 1, 2), (0, 0, 1), (0, 1, 1), (0, 0, 0)])
def test_symmetric_cubic_product_and_taylor_multiplicity(groups):
    rng = np.random.default_rng(730)
    symmetric, triples, factors = cubic.symmetric_product(groups, (2, 2, 2))
    np.testing.assert_allclose(symmetric.T @ symmetric, np.eye(len(triples)), atol=3e-16)
    vectors = [rng.normal(size=2) for _ in range(3)]
    x, y, z = [vectors[g] for g in groups]
    product = np.kron(z, np.kron(y, x))
    monomials = np.array([x[i] * y[j] * z[k] for i, j, k in triples])
    raw = rng.normal(size=(5, 8)) @ symmetric @ symmetric.T
    divisor = np.prod([factorial(groups.count(g)) for g in set(groups)])
    np.testing.assert_allclose(
        (raw @ symmetric * factors) @ monomials, raw @ product / divisor, atol=2e-15
    )
    # Independent evaluation of the transformed polynomial product.
    matrices = [rng.normal(size=(2, 2)) for _ in range(3)]
    dx, dy, dz = [matrices[g] for g in groups]
    dynamics = symmetric.T @ np.kron(dz, np.kron(dy, dx)) @ symmetric
    np.testing.assert_allclose(
        dynamics @ (symmetric.T @ product),
        symmetric.T @ np.kron(dz @ z, np.kron(dy @ y, dx @ x)),
        atol=4e-15,
    )


def test_all_block_triples_cover_all_symmetric_coordinates():
    dims = [2, 1, 1] * 26
    offset = np.r_[0, np.cumsum(dims)]
    seen = set()
    for ids in cubic.BLOCK_TRIPLES:
        groups = tuple(ids.index(b) for b in ids)
        _, local, _ = cubic.symmetric_product(groups, tuple(dims[b] for b in ids))
        for values in local:
            key = tuple(int(offset[b] + value) for b, value in zip(ids, values, strict=True))
            assert key not in seen
            seen.add(key)
    assert len(cubic.BLOCK_TRIPLES) == 82160
    assert len(seen) == 192920
    assert seen == set(combinations_with_replacement(range(104), 3))


def test_invalid_product_and_ordinal_fail_closed(context):
    with pytest.raises(ValueError):
        cubic.symmetric_product((0, 0, 1), (1, 2, 2))
    with pytest.raises(ValueError):
        cubic.symmetric_product((0, 1), (2, 2))
    with pytest.raises(ValueError):
        cubic.solve_triple(context, -1)
    with pytest.raises(ValueError):
        cubic.solve_triple(context, True)


def test_known_complex_cubic_and_resonant_negative_controls():
    result = runner.manufactured_controls()
    assert result["passed"]
    assert [r["product_dimension"] for r in result["records"]] == [8, 6, 6, 4]
    assert all(not r["solve"]["passed"] for r in result["negative_controls"])


@pytest.mark.parametrize("ids", [(0, 0, 0), (0, 1, 2), (0, 3, 6), (7, 15, 22)])
def test_raw_forcing_is_symmetric_in_input_arguments(context, ids):
    wave = tuple(sum(context.blocks[b].wave[axis] for b in ids) for axis in range(3))
    dims = [context.blocks[b].dimension for b in ids]
    original = cubic.raw_forcing(context, ids, wave).reshape((27, *dims), order="F")
    permuted = cubic.raw_forcing(context, (ids[1], ids[0], ids[2]), wave).reshape(
        (27, dims[1], dims[0], dims[2]), order="F"
    )
    assert damping.relative_error(original, permuted.swapaxes(1, 2)) < 1e-12


@pytest.mark.parametrize("active_real_count", [8, 24])
def test_independent_physical_forcing_all_active_monomials(context, active_real_count):
    model = context.model
    u = np.zeros(104)
    u[:active_real_count] = np.random.default_rng(731).normal(size=active_real_count)
    u /= np.linalg.norm(u)
    z = model.complex_coordinates(u)
    active = [i for i, indices in enumerate(context.indices) if np.linalg.norm(z[indices]) > 0]
    spectrum = np.zeros(model.base.shape, dtype=complex)
    for ids in combinations_with_replacement(active, 3):
        blocks = [context.blocks[b] for b in ids]
        groups = tuple(ids.index(b) for b in ids)
        symmetric, local, factors = cubic.symmetric_product(
            groups, tuple(b.dimension for b in blocks)
        )
        triples = np.column_stack([context.indices[ids[axis]][local[:, axis]] for axis in range(3)])
        wave = tuple(sum(b.wave[axis] for b in blocks) for axis in range(3))
        forcing = cubic.raw_forcing(context, ids, wave) @ symmetric
        spectrum[chart.wave_slot(wave, model.size)] += (forcing * factors) @ np.prod(
            z[triples], axis=1
        )
    predicted = np.fft.ifftn(spectrum, axes=(0, 1, 2), norm="ortho")
    direct = cubic.direct_physical_forcing(model, u)
    assert damping.relative_error(predicted, direct) < 1e-8


def test_first_triple_full_equation_and_orthonormal_fft_scaling(context):
    jet = cubic.solve_triple(context, 0)
    assert jet.record["product_dimension"] == 4
    assert jet.record["full_homological_relative_residual"] <= 1e-9
    assert jet.record["structural_error"] <= 5e-12
    assert jet.record["array_hashes"]["forcing"] == chart.array_metadata(jet.forcing)
    # Reconstruct the raw quadratic derivative independently from PairJet.
    pair = context.model.pair_jets[0]
    # A diagonal component of H is twice its stored Taylor coefficient.
    i = context.indices[0][0]
    column = next(c for c, ij in enumerate(context.model.input_pairs) if tuple(ij) == (i, i))
    expected = 2 * context.model.hessian_fibers[column]
    np.testing.assert_allclose(pair.hessian[:, 0], expected, rtol=1e-14, atol=1e-16)


def test_record_archive_is_exact_deterministic_and_nonoverwriting(tmp_path):
    rows = [
        {"ordinal": 0, "value": 1.0 / 3, "condition_number": None},
        {"ordinal": 1, "value": -2.5, "passed": False},
    ]
    first = runner.write_records(tmp_path / "a.jsonl.gz", rows)
    second = runner.write_records(tmp_path / "b.jsonl.gz", rows)
    assert first["roundtrip_passed"] and second["roundtrip_passed"]
    assert first["sha256"] == second["sha256"]
    assert first["records_digest_sha256"] == runner.record_digest(rows)
    assert runner.read_records(tmp_path / "a.jsonl.gz") == rows
    with pytest.raises(FileExistsError):
        runner.write_records(tmp_path / "a.jsonl.gz", [])


def test_incomplete_and_failed_records_never_pass_coverage(context):
    good = cubic.solve_triple(context, 0).record
    rows = [good, {"ordinal": 1, "execution_error": {"type": "ValueError"}, "passed": False}]
    summary = cubic.summarize_records(rows)
    assert not summary["coverage_passed"] and not summary["all_solves_passed"]
    assert summary["record_count"] == 2 and summary["completed_count"] == 1
    assert summary["first_failure"] == rows[1]


def test_fixed_replay_ordinals_include_endpoints_without_duplicates():
    expected = sorted(
        [0, 82159]
        + np.random.default_rng(2026090720).choice(np.arange(1, 82159), 14, replace=False).tolist()
    )
    assert list(cubic.REPLAY_ORDINALS) == expected
    assert len(set(expected)) == 16


def test_unexpected_linear_algebra_failure_is_recorded(tmp_path, monkeypatch):
    def fail(*args):
        raise np.linalg.LinAlgError("manufactured backend failure")

    monkeypatch.setattr(runner, "scan_grid", fail)
    result = runner.guarded_scan_grid(17, tmp_path / "missing.jsonl.gz")
    assert result["execution_error"]["type"] == "LinAlgError"
    assert not result["finite"] and not result["summary"]["coverage_passed"]
    assert result["record_archive"] is None


def test_late_validation_failure_preserves_completed_archive(context, tmp_path, monkeypatch):
    row = cubic.solve_triple(context, 0).record
    path = tmp_path / "saved.jsonl.gz"
    archive = runner.write_records(path, [row])

    def fail(*args):
        raise ValueError("manufactured validation failure")

    monkeypatch.setattr(runner, "scan_grid", fail)
    result = runner.guarded_scan_grid(17, path)
    assert result["execution_error"]["type"] == "ValueError"
    assert result["summary"]["completed_count"] == 1
    assert result["record_archive"]["sha256"] == archive["sha256"]
    assert result["replay_records"] == [row]
    assert not result["finite"]


def test_cli_refuses_partial_archive_overwrite(tmp_path):
    partial = tmp_path / "study_n33.jsonl.gz"
    partial.write_bytes(b"existing evidence")
    target = tmp_path / "study.json"
    command = [
        sys.executable,
        "-m",
        "research.q012f_d3q27_cubic_preflight",
        "--output",
        str(target),
        "--replay",
        str(tmp_path / "worker.json"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 2 and "sealed evidence is not overwritten" in result.stderr
    assert partial.read_bytes() == b"existing evidence"
    assert not target.exists()
