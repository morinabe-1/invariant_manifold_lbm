"""Audit complete Q012f compressed records, decisions, and fresh witnesses."""

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import q012a_d3q27_foundation as q012a
from research import q012f_d3q27_cubic_preflight as runner
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = q012a.ARTIFACT_DIRECTORY / "q012f_d3q27_cubic_preflight.json"


@pytest.fixture(scope="module")
def artifact():
    return json.loads(PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=(17, 33, 65))
def grid(artifact, request):
    result = next(g for g in artifact["cycle"]["grids"] if g["size"] == request.param)
    return result, runner.read_records(PATH.parent / result["record_archive"]["filename"])


@pytest.fixture(scope="module")
def independently_enumerated_layout():
    offsets = np.r_[0, np.cumsum([2, 1, 1] * 26)]
    monomials = []
    for left, middle, right in cubic.BLOCK_TRIPLES:
        local = []
        for k in range(offsets[right], offsets[right + 1]):
            for j in range(offsets[middle], offsets[middle + 1]):
                for i in range(offsets[left], offsets[left + 1]):
                    key = tuple(sorted((i, j, k)))
                    if key not in local:
                        local.append(key)
        monomials.extend(local)
    triples = np.asarray(monomials, dtype=np.int64)
    coordinate_waves = np.repeat(np.asarray(chart.WAVES, dtype=np.int64), 4, axis=0)
    waves = np.sum(coordinate_waves[triples], axis=1)
    assert len(set(monomials)) == len(monomials) == 192920
    return chart.array_metadata(triples), chart.array_metadata(waves)


def test_sealed_sources_cycle_and_independent_48_triples(artifact):
    assert _file_sha256(PATH) == "d3b778ed339c9629dbac57264291aceb32c795a1e6d12e3becb20cf333c57089"
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert _file_sha256(Path(runner.__file__)) == artifact["runner_source"]["sha256"]
    for name, module in runner.HELPERS:
        assert _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
    assert runner.input_audit() == cycle["input_audit"]
    replay = runner.replay_audit(
        PATH.parent / cycle["independent_replay"]["filename"],
        cycle["input_audit"],
        cycle["grids"],
        artifact,
    )
    assert replay == cycle["independent_replay"]
    assert replay["passed"]
    assert "not full-triple replay" in replay["scope"]


def test_known_controls_and_all_grid_decision_recomputed(artifact):
    cycle = artifact["cycle"]
    assert runner.manufactured_controls() == cycle["manufactured_controls"]
    assert [g["size"] for g in cycle["grids"]] == [17, 33, 65]
    assert sum(g["summary"]["completed_count"] for g in cycle["grids"]) == 246480
    assert sum(g["summary"]["product_dimension_sum"] for g in cycle["grids"]) == 578760
    assert all(cycle["validity_gates"].values())
    hypotheses = {
        "all_three_grid_cubic_solves": all(
            g["summary"]["all_solves_passed"] for g in cycle["grids"]
        ),
        "full_cubic_real_structure": all(g["conjugacy"]["passed"] for g in cycle["grids"]),
    }
    assert hypotheses == cycle["hypothesis_gates"]
    assert not any(hypotheses.values())
    assert artifact["scientific_outcome"] == "rejected"
    assert [g["summary"]["failed_count"] for g in cycle["grids"]] == [0, 0, 272]
    assert [g["conjugacy"]["passed"] for g in cycle["grids"]] == [True, False, False]
    assert (
        runner.classifier.classify(cycle["validity_gates"], hypotheses, True)
        == cycle["scientific_outcome"]
        == artifact["scientific_outcome"]
    )


def test_full_archive_seal_order_and_summary(grid):
    meta, rows = grid
    archive = meta["record_archive"]
    path = PATH.parent / archive["filename"]
    assert sha256(path.read_bytes()).hexdigest() == archive["sha256"]
    assert path.stat().st_size == archive["bytes"]
    assert runner.record_digest(rows) == archive["records_digest_sha256"]
    assert len(rows) == archive["record_count"] == 82160
    assert [r["ordinal"] for r in rows] == list(range(82160))
    assert _all_numeric_values_finite(rows)
    assert cubic.summarize_records(rows) == meta["summary"]
    assert (
        dict(sorted(Counter(r["status"] for r in rows).items())) == meta["summary"]["status_counts"]
    )
    assert [r for r in rows if r["ordinal"] in cubic.REPLAY_ORDINALS] == meta["replay_records"]


def test_independent_all_monomial_layout_and_fourier_selection(
    grid, independently_enumerated_layout
):
    meta, _ = grid
    triples, waves = independently_enumerated_layout
    assert triples == meta["coefficient_arrays"]["input_triples"]
    assert waves == meta["coefficient_arrays"]["output_waves"]
    for name, width in (("forcing", 27), ("response", 27), ("reduced", 4)):
        info = meta["coefficient_arrays"][name]
        assert info["shape"] == [192920, width]
        assert info["bytes"] == 192920 * width * 16


def test_each_operator_sector_rank_condition_and_gate(grid):
    meta, rows = grid
    for row, ids in zip(rows, cubic.BLOCK_TRIPLES, strict=True):
        assert row["block_ordinals"] == list(ids)
        dims = tuple((2, 1, 1)[i % 3] for i in ids)
        symmetric, _, _ = cubic.symmetric_product(tuple(ids.index(b) for b in ids), dims)
        assert row["product_dimension"] == symmetric.shape[1]
        wave = tuple(row["output_wave"])
        external = 23 if wave == (0, 0, 0) or wave in chart.WAVES else 27
        assert row["external_dimension"] == external
        assert row["operator_dimension"] == external * row["product_dimension"]
        assert (
            row["rank_threshold"]
            == 100 * np.finfo(float).eps * row["operator_dimension"] * row["largest_singular_value"]
        )
        fullrank = row["numerical_rank"] == row["operator_dimension"]
        assert fullrank == (row["smallest_singular_value"] > row["rank_threshold"])
        if fullrank:
            assert (
                row["condition_number"]
                == row["largest_singular_value"] / row["smallest_singular_value"]
            )
            expected_status = (
                "nonsingular_practical"
                if row["condition_number"] <= 1e8
                else "nonsingular_ill_conditioned"
            )
        else:
            assert row["condition_number"] is None
            expected_status = (
                "singular_compatible"
                if row["left_null_forcing_norm"] <= 1e-10 * max(1, row["forcing_norm"])
                else "singular_incompatible"
            )
        assert row["status"] == expected_status
        expected_pass = (
            expected_status == "nonsingular_practical"
            and row["solve_relative_residual"] <= 1e-10
            and row["backend"]["passed"]
            and row["structural_error"] <= 5e-12
            and row["full_homological_relative_residual"] <= 1e-9
        )
        assert row["passed"] == expected_pass
        if wave != (0, 0, 0):
            assert (
                row["zero_wave_response_moment_error"] == row["zero_wave_forcing_moment_error"] == 0
            )
        if row["backend"]["fallback"]:
            assert row["backend"]["driver"] == "gesvd"
            assert row["backend"]["original_error"] == "SVD did not converge"
    assert sum(not r["passed"] for r in rows) == meta["summary"]["failed_count"]
    assert Counter(r["status"] for r in rows) == {"nonsingular_practical": 82160}
    failures = [r for r in rows if not r["passed"]]
    fallbacks = [r for r in rows if r["backend"]["fallback"]]
    if meta["size"] == 65:
        assert len(failures) == 272
        assert all(r["solve_relative_residual"] > 1e-10 for r in failures)
        assert all(not r["backend"]["fallback"] for r in failures)
        assert Counter(tuple(sorted(i % 3 for i in r["block_ordinals"])) for r in failures) == {
            (0, 0, 0): 264,
            (0, 1, 2): 8,
        }
        assert [r["ordinal"] for r in rows if r["full_homological_relative_residual"] > 1e-9] == [
            55031,
            62968,
            63622,
        ]
        assert [r["ordinal"] for r in fallbacks] == [45729, 55289]
        assert all(r["passed"] for r in fallbacks)
    else:
        assert not failures and not fallbacks


def test_independent_104_direction_forcing_and_all_conjugacy(grid):
    meta, _ = grid
    direction = meta["directional_forcing"]
    np.testing.assert_array_equal(
        direction["directions"], chart.normalized_directions(2026090719, 8)
    )
    assert len(direction["records"]) == 8
    for row in direction["records"]:
        assert row["passed"] == (row["relative_error"] <= 1e-8)
        assert row["direct_norm"] > 1e-14
    conju = meta["conjugacy"]
    assert conju["coverage"] and conju["opposite_output_waves"]
    assert set(conju["fields"]) == {"forcing", "response", "reduced"}
    for row in conju["fields"].values():
        assert row["passed"] == (row["maximum_scaled_error"] <= 1e-8)
    assert conju["passed"] == all(r["passed"] for r in conju["fields"].values())


def test_fresh_quadratic_arrays_and_worst_cubic_witness(grid):
    meta, rows = grid
    model, rebuild = runner.fresh_model(meta["size"])
    assert rebuild == meta["quadratic_rebuild"]
    context = cubic.build_context(model)
    ordinals = {0, meta["summary"]["worst_condition"]["ordinal"]}
    if meta["summary"]["first_failure"] is not None:
        ordinals.add(meta["summary"]["first_failure"]["ordinal"])
    for ordinal in sorted(ordinals):
        assert cubic.solve_triple(context, ordinal).record == rows[ordinal]
