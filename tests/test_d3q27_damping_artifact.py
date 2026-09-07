"""Audit the saved partial Q012c1 trial and its reproducible SVD obstruction.

The 108-condition protocol is incomplete and MUST remain inconclusive.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import svd

from research import d3q27_quadratic as q
from research import q012a_d3q27_foundation as q012a
from research import q012c1_d3q27_damping as runner
from research import q012c_d3q27_preflight as q012c
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

ARTIFACT = q012a.ARTIFACT_DIRECTORY / "q012c1_d3q27_damping.json"


@pytest.fixture(scope="module")
def artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tables(artifact: dict) -> list[tuple[dict, dict]]:
    directory = ARTIFACT.parent / artifact["table_directory"]
    records = []
    for summary in artifact["cycle"]["conditions"]:
        table = summary["table"]
        path = directory / table["filename"]
        assert path.parent == directory and path.suffix == ".json"
        assert _file_sha256(path) == table["sha256"]
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1
        assert (
            q012a._digest(data["cycle"])
            == data["result_digest_sha256"]
            == table["result_digest_sha256"]
        )
        assert _all_numeric_values_finite(data)
        records.append((summary, data["cycle"]))
    assert {path.name for path in directory.glob("*.json")} == {
        r[0]["table"]["filename"] for r in records
    }
    return records


def test_manifest_digest_source_seals_and_validity(artifact: dict) -> None:
    cycle = copy.deepcopy(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(runner.__file__))
    for name, module in runner.HELPERS:
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    assert artifact["study_gate"] == cycle["study_validity"] == "failed"
    assert artifact["scientific_outcome"] == "inconclusive"
    assert len(cycle["validity_gates"]) == 9
    assert {key for key, value in cycle["validity_gates"].items() if value} == {
        "sealed_inputs",
        "independent_map_hydrodynamic_hessian_grid_controls",
        "finite_evidence",
    }
    assert _all_numeric_values_finite(artifact)
    assert runner.input_audit()["passed"]


def test_partial_table_summaries_are_faithful_and_not_complete(tables: list) -> None:
    assert len(tables) == 4
    expected = {(17, 1.0, p, e) for p, e in runner.CONFIGURATIONS[:4]}
    assert {(r["size"], r["omega"], r["power"], r["eta"]) for _, r in tables} == expected
    for summary, cycle in tables:
        for key, value in cycle.items():
            if key == "coefficient_screen":
                value = {k: v for k, v in value.items() if k not in ("pair_columns", "pair_rows")}
            assert summary[key] == value
        assert cycle["real_coordinate_count"] == 104
        assert cycle["jointly_prequalified"] == (
            cycle["coefficient_screen"]["coefficient_prequalified"]
            and cycle["normal_ordering"]["normal_ordering_prequalified"]
            and cycle["map_control_passed"]
            and cycle["hydrodynamic_control_passed"]
            and cycle["hessian_control_passed"]
        )
    assert sum(c["coefficient_screen"]["pair_count"] for _, c in tables) == 12324
    assert sum(c["coefficient_screen"]["product_dimension_sum"] for _, c in tables) == 21840


def test_every_pair_is_present_and_each_gate_matches_raw_metrics(tables: list) -> None:
    blocks = [(w, label) for w in q.shell_waves(3) for label in q.LABELS]
    expected = list(combinations_with_replacement(blocks, 2))
    for _summary, cycle in tables:
        screen = cycle["coefficient_screen"]
        rows = q012c.unpack_pairs(screen)
        assert len(rows) == 3081 and screen["coverage_passed"]
        for row, (left, right) in zip(rows, expected):
            assert (tuple(row["left_wave"]), row["left_label"]) == left
            assert (tuple(row["right_wave"]), row["right_label"]) == right
            output = q.canonical_wave(
                tuple(a + b for a, b in zip(left[0], right[0])), cycle["size"]
            )
            assert tuple(row["output_wave"]) == output
            selected = output in q.shell_waves(3)
            assert row["output_is_selected"] == selected
            assert row["external_dimension"] == (23 if selected or output == (0, 0, 0) else 27)
            ld, rd = (2 if left[1] == "shear" else 1), (2 if right[1] == "shear" else 1)
            assert row["product_dimension"] == (ld * (ld + 1) // 2 if left == right else ld * rd)
            assert row["symmetric_square"] == (left == right)
            assert row["operator_dimension"] == row["external_dimension"] * row["product_dimension"]
            assert row["passed"] == (
                row["status"] == "nonsingular_practical"
                and row["solve_relative_residual"] <= 1e-10
                and max(row["graph_gauge_error"], row["zero_wave_moment_error"]) <= 5e-12
            )
            if row["status"].startswith("singular"):
                assert row["numerical_rank"] < row["operator_dimension"]
                assert row["condition_number"] is None and not row["passed"]
            else:
                assert row["numerical_rank"] == row["operator_dimension"]
                assert (row["status"] == "nonsingular_practical") == (
                    row["condition_number"] <= 1e8
                )
            assert row["structural_error"] <= 5e-12
            assert (
                row["response_global_l2_norm"] == row["response_local_norm"] / cycle["size"] ** 1.5
            )
        assert screen["status_counts"] == dict(Counter(r["status"] for r in rows))
        assert screen["coefficient_prequalified"] == all(r["passed"] for r in rows)
        assert screen["failed_pair_count"] == sum(not r["passed"] for r in rows)
        assert screen["residual_only_failure_count"] == sum(
            r["status"] == "nonsingular_practical"
            and r["solve_relative_residual"] > 1e-10
            and max(r["graph_gauge_error"], r["zero_wave_moment_error"]) <= 5e-12
            for r in rows
        )
        assert screen["maximum_solve_relative_residual"] == max(
            r["solve_relative_residual"] for r in rows
        )
        assert screen["maximum_response_global_l2_norm"] == max(
            r["response_global_l2_norm"] for r in rows
        )


def test_completed_original_bgk_baseline_is_preserved(tables: list) -> None:
    prior = runner.prior_baselines()
    baselines = [cycle for _, cycle in tables if cycle["eta"] == 0]
    assert len(baselines) == 1
    for cycle in baselines:
        original = prior[cycle["size"], cycle["omega"]]
        assert cycle["baseline_reproduction"]["passed"]
        for key, value in original["coefficient_screen"].items():
            assert cycle["coefficient_screen"][key] == value
        assert cycle["normal_ordering"] == original["normal_ordering"]
        assert not cycle["jointly_prequalified"]


def test_no_family_is_selected_or_replayed_from_partial_evidence(artifact: dict) -> None:
    cycle = artifact["cycle"]
    families, chosen = runner.classify_families(cycle["conditions"])
    assert len(families) == 32 and families == cycle["families"]
    assert chosen == cycle["selected_family"]
    assert artifact["scientific_outcome"] == "inconclusive"
    assert chosen is None and not any(f["jointly_viable"] for f in families)
    assert cycle["independent_replay"] is None
    assert "unmodified baseline rejection retained" in cycle["map"]
    assert "no SSM existence" in cycle["claim_boundary"]


def test_exact_failure_matrix_reproduces_without_altering_solver(artifact: dict) -> None:
    failure = artifact["cycle"]["numerical_failure"]
    assert (failure["size"], failure["omega"], failure["eta"], failure["power"]) == (
        17,
        1.0,
        0.1,
        1,
    )
    assert failure["left_wave"] == [-1, 1, 0] and failure["right_wave"] == [-1, 1, 1]
    assert failure["left_label"] == failure["right_label"] == "shear"
    assert failure["completed_pairs_in_failed_condition"] == 1431
    assert failure["finite_operator_and_forcing"] and failure["operator_dimension"] == 108
    matrix = np.asarray(failure["operator_real"]) + 1j * np.asarray(failure["operator_imag"])
    assert matrix.shape == (108, 108) and np.isfinite(matrix).all()
    for _ in range(3):
        with pytest.raises(np.linalg.LinAlgError, match="SVD did not converge"):
            svd(matrix, full_matrices=False, check_finite=False, lapack_driver="gesdd")
    u, singular, vh = svd(matrix, full_matrices=False, check_finite=False, lapack_driver="gesvd")
    assert 36 < singular[0] / singular[-1] < 37
    assert np.linalg.norm((u * singular) @ vh - matrix) / np.linalg.norm(matrix) < 1e-12
    assert len(failure["diagnostics"]) == 6
    assert not any(r["converged"] for r in failure["diagnostics"][:3])
    assert all(
        r["converged"] and r["solve_relative_residual"] < 1e-12 for r in failure["diagnostics"][3:]
    )
    assert "diagnostic only" in failure["scope"]
