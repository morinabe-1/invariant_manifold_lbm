"""Read-only, full-column audit of the saved H1 comparison and its failures.

Compensated scalar norm sums are independent of the runner's NumPy vector
norms. This diagnoses stored discrepancies; it does not prove their cause or
repair, re-solve, project, or reclassify the original forcing calculation.
"""

from math import fsum, isclose, sqrt

import numpy as np

from research import q012h2_d3q27_quartic_forcing as run


def norm(vector):
    value = np.asarray(vector)
    if value.shape != (27,) or not np.isfinite(value).all():
        raise ValueError("all 27 finite population entries required")
    return sqrt(fsum(float(z.real) ** 2 + float(z.imag) ** 2 for z in value))


def column(left, right, index):
    a, b = left["forcing"][:, index], right["forcing"][:, index]
    terms = left["terms"].reshape(7, 27, -1)[:, :, index]
    reference_norm = norm(b)
    difference = norm(a - b)
    error = difference / max(1e-14, reference_norm)
    return {
        "column": index,
        "coordinates": left["keys"][index].tolist(),
        "reference_norm": reference_norm,
        "primary_norm": norm(a),
        "difference_norm": difference,
        "relative_error": error,
        "reference_below_floor": reference_norm < 1e-14,
        "failed_original_H1_bound": error > 1e-8,
        "collision_difference_norm": norm(
            left["collision"][:, index] - right["collision"][:, index]
        ),
        "composition_difference_norm": norm(
            left["composition"][:, index] - right["composition"][:, index]
        ),
        "reference_collision_norm": norm(right["collision"][:, index]),
        "reference_composition_norm": norm(right["composition"][:, index]),
        "seven_term_norms": [norm(term) for term in terms],
    }


def summarize(rows):
    if not rows:
        raise ValueError("nonempty complete column evidence required")
    failed = [r for r in rows if r["failed_original_H1_bound"]]
    below = [r for r in rows if r["reference_below_floor"]]
    location = lambda r: {k: r[k] for k in ("group", "column", "coordinates")}
    worst = max(rows, key=lambda r: r["relative_error"])
    largest = max(rows, key=lambda r: r["difference_norm"])
    return {
        "columns": len(rows),
        "failed_columns": len(failed),
        "below_floor_columns": len(below),
        "failed_below_floor_columns": sum(r["reference_below_floor"] for r in failed),
        "failed_at_or_above_floor_columns": sum(not r["reference_below_floor"] for r in failed),
        "maximum_relative_error": worst["relative_error"],
        "maximum_relative_error_location": location(worst),
        "maximum_absolute_difference": largest["difference_norm"],
        "maximum_absolute_difference_location": location(largest),
        "maximum_failed_reference_norm": max((r["reference_norm"] for r in failed), default=0.0),
        "maximum_relative_at_or_above_floor": max(
            (r["relative_error"] for r in rows if not r["reference_below_floor"]), default=None
        ),
        "failure_cause": "not_established_by_stored_vector_comparison",
    }


def audit(output):
    saved = run.common.read_json(output)
    run.common.unseal(saved)
    state = run.inputs.selection_state()
    groups = tuple(tuple(r["group"]) for r in state["selection"]["groups"])
    run.require([g["size"] for g in saved["grids"]] == [17, 33, 65], "all three H1 grids required")
    run.require(
        saved["decision"]["stage"] == "H1_forcing_only"
        and saved["decision"]["q012h2_outcome"] == "not_evaluated",
        "original H1-only boundary differs",
    )
    results = []
    for grid in saved["grids"]:
        size = grid["size"]
        _, p = run.read_grid(output, size, "primary")
        _, w = run.read_grid(output, size, "worker")
        rows = []
        run.require(len(grid["comparisons"]) == len(groups), "all registered tuples required")
        with (
            run.archive.Archive(p, "r", run.names(698, "primary")) as left,
            run.archive.Archive(w, "r", run.names(698, "worker")) as right,
        ):
            for ordinal, (group, old) in enumerate(zip(groups, grid["comparisons"], strict=True)):
                run.require(run.same(old["group"], group), "saved group order differs")
                a, b = (
                    left.arrays(f"tuple_{ordinal:04d}.npz"),
                    right.arrays(f"tuple_{ordinal:04d}.npz"),
                )
                expected = np.asarray(
                    [ids for ids, _ in run.reference.columns(group, run.inputs.BLOCK_INDICES)],
                    dtype=np.int64,
                )
                run.require(
                    np.array_equal(a["keys"], expected) and np.array_equal(b["keys"], expected),
                    "saved monomial coverage differs",
                )
                run.require(
                    len(old["column_errors"]["forcing"]) == len(expected),
                    "saved error count differs",
                )
                for j, previous in enumerate(old["column_errors"]["forcing"]):
                    current = column(a, b, j)
                    run.require(
                        isclose(current["relative_error"], previous, rel_tol=2e-14, abs_tol=0),
                        "compensated norm differs from original error",
                    )
                    run.require(
                        current["failed_original_H1_bound"] == (previous > 1e-8),
                        "original per-column classification changed",
                    )
                    rows.append({"group": group, **current})
        run.require(len(rows) == 1826, "all 1826 columns required")
        results.append({"size": size, "summary": summarize(rows), "columns": rows})
    return {
        "scope": "full saved H1 vectors and unchanged per-column bounds; no new F4 evaluation or arithmetic-cause proof",
        "parent_filename": output.name,
        "parent_file_sha256": run.archive.file_sha(output),
        "selection_sha256": run.inputs.SELECTION_SHA,
        "grids": results,
        "columns": sum(g["summary"]["columns"] for g in results),
        "original_H1_decision": saved["decision"],
        "all_saved_column_errors_and_classifications_reproduced": True,
        "q012h2_outcome": "not_evaluated",
    }
