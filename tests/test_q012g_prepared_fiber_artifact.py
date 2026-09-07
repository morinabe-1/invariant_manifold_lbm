"""Exact whole-array input-to-preparation audit, independent of CubicChart.

This reads pinned input fibers and CLOSED worker/main preparation fingerprints.
It does not instantiate the production grouped engine, solve any coefficients,
or evaluate a physical campaign concurrently with the live main process.
"""

from copy import deepcopy
from hashlib import file_digest, sha256
from itertools import product
from math import comb

import numpy as np
import pytest

from research import q012g_d3q27_cubic_chart as runner
from ttim_lbm.rational_spectrum import _file_sha256

DIRECTORY = runner.foundation.ARTIFACT_DIRECTORY
WORKER_SHA = "84e4d6f9ce241b0eab4a6eda380dbf242a83c084e4fc4bc872291bb48ef56891"
MAIN_PINS = {
    17: "369b471c53f01b8e3a88ae7451e5d93bdaef3c10345186b90e092cf27bb1e2e4",
    33: "d859b3ea1d39e9c3f3a9d07f03642b2fa95ea1b6e4b62eb87b266f04d31f63bc",
}
SHELL = np.array([w for w in product((-1, 0, 1), repeat=3) if any(w)], dtype=np.int64)


def fingerprint(value):
    array = np.ascontiguousarray(value)
    return {
        "shape": list(array.shape),
        "dtype": array.dtype.str,
        "bytes": array.nbytes,
        "sha256": sha256(memoryview(array).cast("B")).hexdigest(),
    }


def reconstruct_prepared_fingerprints(arrays):
    """Lexicographic waves + original row ordinal, not production group argsort."""
    count = comb(106, 3)
    assert count == 192920
    assert set(arrays) == {"input_triples", "output_waves", "response", "forcing", "reduced"}
    for name, value in arrays.items():
        width = 3 if name in ("input_triples", "output_waves") else 4 if name == "reduced" else 27
        assert value.shape == (count, width) and np.all(np.isfinite(value))
        assert value.dtype == np.dtype("int64" if width == 3 else "complex128")
    triples, waves = arrays["input_triples"], arrays["output_waves"]
    assert np.all((0 <= triples) & (triples < 104))
    assert np.all(triples[:, 0] <= triples[:, 1]) and np.all(triples[:, 1] <= triples[:, 2])
    identifiers = (triples[:, 0] * 104 + triples[:, 1]) * 104 + triples[:, 2]
    assert (
        len(set(identifiers.tolist())) == count
    )  # Completeness of all ordered degree-3 monomials.
    np.testing.assert_array_equal(waves, SHELL[triples // 4].sum(axis=1))
    selected = np.all((-1 <= waves) & (waves <= 1), axis=1) & np.any(waves, axis=1)
    assert np.count_nonzero(selected) == 61008
    assert np.count_nonzero(~selected) == 131912
    assert np.count_nonzero(arrays["reduced"][~selected]) == 0  # No numerical drop tolerance.
    fingerprints = {}
    for name, field in (("response", "response"), ("forcing", "forcing"), ("internal", "reduced")):
        ordinal = np.flatnonzero(selected) if name == "internal" else np.arange(count)
        output = waves[ordinal]
        perm = ordinal[np.lexsort((ordinal, output[:, 2], output[:, 1], output[:, 0]))]
        ordered_waves = waves[perm]
        starts = np.flatnonzero(
            np.r_[True, np.any(ordered_waves[1:] != ordered_waves[:-1], axis=1)]
        )
        expected_waves = (
            SHELL if name == "internal" else np.array(list(product(range(-3, 4), repeat=3)))
        )
        np.testing.assert_array_equal(ordered_waves[starts], expected_waves)
        prepared = {
            "indices": fingerprint(triples[perm]),
            "coefficients": fingerprint(arrays[field][perm]),
            "starts": fingerprint(starts.astype(np.int64)),
            "outputs": fingerprint(np.arange(len(starts), dtype=np.int64)),
        }
        fingerprints[name] = {
            "monomial_rows": len(perm),
            "degree": 3,
            "coefficient_scalars": len(perm) * arrays[field].shape[1],
            "coefficient_bytes": prepared["coefficients"]["bytes"],
            "sparse_index_bytes": sum(
                prepared[k]["bytes"] for k in ("indices", "starts", "outputs")
            ),
            "prepared_arrays": prepared,
        }
    return fingerprints


@pytest.fixture(scope="module", params=(17, 33, 65), ids=lambda n: f"n{n}")
def fibers(request):
    assert _file_sha256(runner.PRIOR_PATH) == runner.PRIOR_SHA
    previous = runner.prior.read_json(runner.PRIOR_PATH)
    original = next(g for g in previous["cycle"]["grids"] if g["size"] == request.param)
    manifest = original["fiber_archive"]
    path = DIRECTORY / manifest["filename"]
    assert path.stat().st_size == manifest["bytes"]
    with path.open("rb") as stream:
        assert file_digest(stream, "sha256").hexdigest() == manifest["sha256"]
    with np.load(path, allow_pickle=False) as archive:
        assert len(archive.files) == 5 and len(set(archive.files)) == 5
        arrays = {name: archive[name] for name in archive.files}
    assert {name: fingerprint(value) for name, value in arrays.items()} == manifest["entries"]
    for value in arrays.values():
        value.setflags(write=False)
    return request.param, arrays


def test_every_saved_prepared_scalar_and_index_matches_unchanged_input(fibers):
    size, arrays = fibers
    expected = reconstruct_prepared_fingerprints(arrays)
    worker_path = DIRECTORY / "q012g_d3q27_cubic_chart_replay.json"
    assert _file_sha256(worker_path) == WORKER_SHA
    worker = runner.prior.read_json(worker_path)
    child = next(v for v in worker["grid_artifacts"] if v["filename"].endswith(f"_n{size}.json"))
    paths = [(DIRECTORY / child["filename"], child["sha256"], worker["process_id"])]
    if size in MAIN_PINS:
        paths.append((DIRECTORY / f"q012g_d3q27_cubic_chart_n{size}.json", MAIN_PINS[size], 29360))
    assert len(paths) == (2 if size in (17, 33) else 1)
    for path, seal, process in paths:
        assert _file_sha256(path) == seal
        document = runner.prior.read_json(path)
        assert document["process_id"] == process and document["grid"]["size"] == size
        assert runner.source_equal(document, runner.metadata())
        assert document["grid_digest_sha256"] == runner.foundation._digest(document["grid"])
        assert document["grid"]["offline_cost"]["prepared_cubic_buffers"]["engines"] == expected
        loaded = document["grid"]["fiber_load"]
        assert loaded["complete_monomials"] == 192920 and loaded["output_wave_count"] == 343
        assert (
            loaded["reduced_first_shell_rows"] == 61008
            and loaded["reduced_exact_zero_rows_omitted"] == 131912
        )


def test_independent_fingerprint_comparison_detects_one_ulp_and_index_changes():
    # Deliberately tiny changes in memory only; no artifact or scientific source is edited.
    values = np.array([[1 + 2j, 3 + 4j]], dtype=np.complex128)
    reference = fingerprint(values)
    changed = values.copy()
    changed.real[0, 0] = np.nextafter(changed.real[0, 0], np.inf)
    assert np.linalg.norm(changed - values) < 1e-14
    assert fingerprint(changed) != reference
    indices = np.array([[0, 1, 2], [0, 1, 3]], dtype=np.int64)
    assert fingerprint(indices[::-1]) != fingerprint(indices)
    falsely_relabelled = deepcopy(reference)
    falsely_relabelled["shape"] = [2, 1]
    assert fingerprint(values) != falsely_relabelled


def test_full_input_audit_rejects_a_subnormal_outside_reduced_support(fibers):
    _, arrays = fibers
    corrupted = dict(arrays)
    corrupted["reduced"] = arrays["reduced"].copy()
    outside = np.flatnonzero(np.any(np.abs(arrays["output_waves"]) > 1, axis=1))[0]
    corrupted["reduced"][outside, 0] = np.nextafter(0.0, 1.0)
    assert corrupted["reduced"][outside, 0] != 0
    with pytest.raises(AssertionError):
        reconstruct_prepared_fingerprints(corrupted)
