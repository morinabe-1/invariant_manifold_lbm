"""Audit Q012f1 diagnostic coverage, retained failures, source seals and fresh cases."""

import json
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_cubic_precision as precision
from research import q012a_d3q27_foundation as q012a
from research import q012f1_d3q27_cubic_precision as runner
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = q012a.ARTIFACT_DIRECTORY / "q012f1_d3q27_cubic_precision.json"


@pytest.fixture(scope="module")
def artifact():
    return json.loads(PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=(17, 33, 65))
def grid(artifact, request):
    meta = next(g for g in artifact["cycle"]["grids"] if g["size"] == request.param)
    return meta, runner.previous.read_records(PATH.parent / meta["record_archive"]["filename"])


def test_sources_cycles_and_independent_replay(artifact):
    assert _file_sha256(PATH) == "5bc0db745c8846196feec53bcbacddc069b8b257e5bcb89503b7b41e44c403a7"
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert _file_sha256(Path(runner.__file__)) == artifact["runner_source"]["sha256"]
    for name, module in runner.HELPERS:
        assert _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
    assert runner.input_audit() == cycle["input_audit"]
    assert runner.selection() == cycle["selection"]
    replay = runner.replay_audit(
        PATH.parent / cycle["independent_replay"]["filename"],
        cycle["input_audit"],
        cycle["selection"],
        cycle["grids"],
        artifact,
    )
    assert replay == cycle["independent_replay"] and replay["passed"]
    assert replay["triples_per_grid"] == 32


def test_manufactured_controls_and_decision_recomputed(artifact):
    cycle = artifact["cycle"]
    assert precision.known_controls() == cycle["controls"]
    assert all(cycle["validity_gates"].values())
    grids = cycle["grids"]
    assert [g["size"] for g in grids] == [17, 33, 65]
    hypotheses = {
        "H1_precision_repairs_original_272_residual_failures": not grids[2][
            "original_failure_refined_failed"
        ],
        "H2_input_real_structure_is_separate": all(
            not g["conjugacy"]["raw"]["refined"]["fields"]["response"]["passed"] for g in grids[1:]
        )
        and all(g["conjugacy"]["paired"]["refined"]["passed"] for g in grids),
        "H3_paired_refined_candidate_passes_diagnosis": all(
            g["input_rebuild"]["paired_quadratic_equations"]["passed"]
            and g["summary"]["paired"]["refined"]["passed"]
            and g["conjugacy"]["paired"]["refined"]["passed"]
            for g in grids
        ),
    }
    assert hypotheses == cycle["hypothesis_gates"]
    assert not any(hypotheses.values())
    assert artifact["scientific_outcome"] == "rejected"
    assert [g["conjugacy"]["raw"]["refined"]["passed"] for g in grids] == [True, True, False]
    assert all(g["conjugacy"]["paired"]["refined"]["passed"] for g in grids)
    assert all(g["input_rebuild"]["paired_quadratic_equations"]["passed"] for g in grids)
    assert {
        v: [grids[2]["summary"][v][s]["failed_count"] for s in precision.SOLVERS]
        for v in precision.INPUTS
    } == {"raw": [272, 278, 20], "paired": [270, 278, 17]}
    assert (
        runner.previous.classifier.classify(cycle["validity_gates"], hypotheses, True)
        == artifact["scientific_outcome"]
        == cycle["scientific_outcome"]
    )


def test_complete_selected_archives_and_summaries(grid, artifact):
    meta, rows = grid
    archive = meta["record_archive"]
    path = PATH.parent / archive["filename"]
    assert sha256(path.read_bytes()).hexdigest() == archive["sha256"]
    assert path.stat().st_size == archive["bytes"]
    assert len(rows) == archive["record_count"] == 324
    assert runner.previous.record_digest(rows) == archive["records_digest_sha256"]
    assert _all_numeric_values_finite(rows)
    assert [r["ordinal"] for r in rows] == artifact["cycle"]["selection"]["ordinals"]
    assert runner.row_summary(rows) == meta["summary"]
    assert [
        r for r in rows if r["ordinal"] in artifact["cycle"]["selection"]["replay_ordinals"]
    ] == meta["replay_records"]


def test_same_operator_six_arms_and_fixed_refinement(grid, artifact):
    meta, rows = grid
    old = next(g for g in runner.prior_artifact()["cycle"]["grids"] if g["size"] == meta["size"])
    old_rows = runner.previous.read_records(PATH.parent / old["record_archive"]["filename"])
    for row in rows:
        assert row["original_record_equal"] and row["identical_operators"]
        assert row["inputs"]["raw"]["original_record"] == old_rows[row["ordinal"]]
        for key in ("external_dynamics", "input_dynamics"):
            assert (
                row["inputs"]["raw"]["problem_arrays"][key]
                == row["inputs"]["paired"]["problem_arrays"][key]
            )
        for variant in precision.INPUTS:
            source = row["inputs"][variant]
            assert [r["iteration"] for r in source["refinement_history"]] == [0, 1, 2, 3]
            assert all("correction_norm" in r for r in source["refinement_history"][:3])
            assert "correction_norm" not in source["refinement_history"][3]
            for solver in precision.SOLVERS:
                data = source["solvers"][solver]
                expected = (
                    source["original_record"]["status"] == "nonsingular_practical"
                    and data["external_relative_residual"] <= 1e-10
                    and data["full_relative_residual"] <= 1e-9
                    and data["structural_error"] <= 5e-12
                )
                assert data["passed"] == expected
                if (
                    solver == "refined"
                    and row["ordinal"] in artifact["cycle"]["selection"]["replay_ordinals"]
                ):
                    assert data["precision_crosscheck"]["mp128_mp192_scaled_difference"] <= 1e-24
    failures = [
        r["ordinal"]
        for r in rows
        if r["ordinal"] in artifact["cycle"]["selection"]["original_failure_ordinals"]
        and not r["inputs"]["raw"]["solvers"]["refined"]["passed"]
    ]
    assert failures == meta["original_failure_refined_failed"]
    if meta["size"] == 65:
        assert sum(not r["inputs"]["raw"]["original_record"]["passed"] for r in rows) == 272
        for variant, count in (("raw", 20), ("paired", 17)):
            failed = [r for r in rows if not r["inputs"][variant]["solvers"]["refined"]["passed"]]
            assert len(failed) == count
            assert all(
                r["inputs"][variant]["solvers"]["refined"]["external_relative_residual"] > 1e-10
                for r in failed
            )
            assert all(
                r["inputs"][variant]["solvers"]["refined"]["full_relative_residual"] <= 1e-9
                for r in rows
            )
            assert all(
                r["inputs"][variant]["solvers"]["refined"]["mp128_relative_residual"] <= 1e-10
                for r in rows
            )
            assert all(
                r["inputs"][variant]["original_record"]["input_labels"] == ["shear"] * 3
                for r in failed
            )


def test_full_quadratic_input_and_independent_full_forcing(grid):
    meta, _ = grid
    qa = meta["input_rebuild"]["paired_quadratic_equations"]
    assert len(qa["records"]) == 3081
    assert q012a._digest(qa["records"]) == qa["record_digest_sha256"]
    assert qa["failed_count"] == sum(not r["passed"] for r in qa["records"])
    for row in qa["records"]:
        assert row["forcing_equal"]
        assert row["passed"] == (
            row["external_relative_residual"] <= 1e-10
            and row["full_relative_residual"] <= 1e-9
            and row["structural_error"] <= 5e-12
        )
    old = next(g for g in runner.prior_artifact()["cycle"]["grids"] if g["size"] == meta["size"])
    for variant in precision.INPUTS:
        forcing = meta["full_forcing"][variant]
        assert forcing["arrays"]["forcing"]["shape"] == [192920, 27]
        np.testing.assert_array_equal(
            forcing["directional"]["directions"],
            chart.normalized_directions(cubic.DIRECTION_SEED, 8),
        )
        assert len(forcing["directional"]["records"]) == 8
        assert all(r["relative_error"] <= 1e-8 for r in forcing["directional"]["records"])
    assert all(
        meta["full_forcing"]["raw"]["arrays"][k] == old["coefficient_arrays"][k]
        for k in ("input_triples", "output_waves", "forcing")
    )


def test_conjugacy_gates_keep_both_inputs_and_all_solvers(grid):
    meta, _ = grid
    for variant in precision.INPUTS:
        for solver in precision.SOLVERS:
            data = meta["conjugacy"][variant][solver]
            assert data["coverage"] and all(data["checks"].values())
            for row in data["fields"].values():
                assert (
                    row["passed"]
                    == (row["maximum_scaled_error"] <= 1e-8)
                    == (row["failed_count"] == 0)
                )
            assert data["passed"] == all(row["passed"] for row in data["fields"].values())


def test_fresh_two_input_six_solver_witness(grid, artifact):
    meta, rows = grid
    models, rebuild = runner.build_inputs(meta["size"])
    assert rebuild == meta["input_rebuild"]
    row = next(r for r in rows if r["ordinal"] == 0)
    for variant in precision.INPUTS:
        result, _ = precision.solve_case(cubic.build_context(models[variant]), 0, True)
        assert result == row["inputs"][variant]
