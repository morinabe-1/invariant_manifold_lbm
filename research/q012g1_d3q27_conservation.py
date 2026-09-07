"""Q012g1: same sealed binary64 fields, independently audited conserved sums.

Run the GMP 48-case worker to completion before the integer 192-case primary.
This diagnoses conservation gates only; it never changes the parent verdict.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter

import numpy as np

from research import d3q27_conservation_audit as exact
from research import q012g_d3q27_cubic_chart as parent
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PARENT_PATH = parent.foundation.ARTIFACT_DIRECTORY / "q012g_d3q27_cubic_chart.json"
PARENT_SHA = "6a201f212b321d8d7b3d4d143306633608c9df4c50c763e05dcd044695002944"
PARENT_DIGEST = "aea8c955e3b258766bc516f6ebcc3130ff6a477ac0901bad9dcc656236676b8e"
PARENT_WORKER_SHA = "84e4d6f9ce241b0eab4a6eda380dbf242a83c084e4fc4bc872291bb48ef56891"
PARENT_CHILD_SHAS = {
    17: "369b471c53f01b8e3a88ae7451e5d93bdaef3c10345186b90e092cf27bb1e2e4",
    33: "d859b3ea1d39e9c3f3a9d07f03642b2fa95ea1b6e4b62eb87b266f04d31f63bc",
    65: "1b5b6248ad2b60b4bf67baa70bfd59615e63a6c59a3328b64f8f3dde31d5a01f",
}
SIZES = (17, 33, 65)
FIELDS = ("W", "Phi_W", "W_R")
COMPARISONS = {
    "W_leaf": ("W", "baseline"),
    "W_R_leaf": ("W_R", "baseline"),
    "Phi_conservation": ("Phi_W", "W"),
}
HELPERS = parent.HELPERS + (("cubic_chart_runner", parent), ("conservation_audit", exact))
WORKER_KIND = "Q012g1 independent GMP 48-case conservation worker"
MAIN_KIND = "Q012g1 integer 192-case conservation diagnosis"
ERRORS = parent.ERRORS + (AssertionError, OverflowError)
read_json, write_json, digest = (
    parent.prior.read_json,
    parent.prior.previous.write_json,
    parent.foundation._digest,
)


def metadata():
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "process_id": os.getpid(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "runner_source": {"filename": Path(__file__).name, "sha256": _file_sha256(Path(__file__))},
        "helper_sources": {
            name: {
                "filename": Path(module.__file__).name,
                "sha256": _file_sha256(Path(module.__file__)),
            }
            for name, module in HELPERS
        },
    }


def require(condition, message):
    if not condition:
        raise ValueError(message)


def specifications(*, worker=False):
    return [s for s in parent.case_specifications(worker=worker) if s["kind"] == "amplitude"]


def input_audit():
    saved = read_json(PARENT_PATH)
    cycle = dict(saved["cycle"])
    recorded_digest = cycle.pop("result_digest_sha256")
    old_inputs, old_controls = parent.input_audit(), parent.controls()
    checks = {
        "parent_seal": _file_sha256(PARENT_PATH) == PARENT_SHA,
        "parent_cycle_digest": digest(cycle) == recorded_digest == PARENT_DIGEST,
        "parent_source_chain": parent.source_equal(saved, parent.metadata()),
        "parent_valid_and_resolved": saved["study_gate"] == "passed"
        and cycle["study_validity"] == "passed"
        and cycle["generic_and_holdout_resolved"]
        and len(cycle["validity_gates"]) == 12
        and all(cycle["validity_gates"].values()),
        "parent_rejection_retained": saved["scientific_outcome"]
        == cycle["scientific_outcome"]
        == "rejected"
        and list(cycle["hypothesis_gates"].values()) == [True, True, True, False, False],
        "previous_inputs": old_inputs == cycle["input_audit"] and old_inputs["passed"],
        "previous_controls": old_controls == cycle["controls"] and old_controls["passed"],
        "parent_grids": [g["size"] for g in cycle["grids"]] == list(SIZES),
    }
    children = []
    for grid, entry in zip(cycle["grids"], cycle["grid_artifacts"], strict=True):
        size = grid["size"]
        path = parent.prior.sibling(PARENT_PATH.parent, entry["filename"])
        child = read_json(path)
        child_checks = {
            "name_and_seal": path.name == f"q012g_d3q27_cubic_chart_n{size}.json"
            and _file_sha256(path) == entry["sha256"] == PARENT_CHILD_SHAS[size],
            "all_saved_values": {**child["grid"], "roundtrip_passed": True} == grid
            and child["grid_digest_sha256"] == digest(child["grid"]),
            "source_and_process": parent.source_equal(child, saved)
            and child["process_id"] == saved["process_id"],
            "complete_parent_evidence": parent.coverage(grid, worker=False)
            and parent.diagnostic_coverage(grid),
            "all_holdout_cases": [
                parent.record_specification(r) for r in grid["records"] if r["kind"] == "amplitude"
            ]
            == specifications(),
        }
        children.append(
            {
                "size": size,
                "filename": path.name,
                "sha256": _file_sha256(path),
                "checks": child_checks,
                "passed": all(child_checks.values()),
            }
        )
    worker_path = PARENT_PATH.with_name("q012g_d3q27_cubic_chart_replay.json")
    replay = parent.replay_audit(worker_path, old_inputs, old_controls, cycle["grids"], saved)
    checks["all_parent_children"] = len(children) == 3 and all(c["passed"] for c in children)
    checks["parent_144_replay"] = (
        _file_sha256(worker_path) == PARENT_WORKER_SHA
        and replay["passed"]
        and cycle["independent_replay"] == {"status": "computed", **replay}
    )
    counterexamples = [
        {
            "size": g["size"],
            "direction_index": r["direction_index"],
            "amplitude": r["amplitude"],
            "degree": d,
            "comparison": name,
            "component": i,
            "legacy_site_average_error": value,
        }
        for g in cycle["grids"]
        for r in g["records"]
        if r["kind"] == "amplitude"
        for d in ("2", "3")
        for name in COMPARISONS
        for i, value in enumerate(r["models"][d]["site_average_conservation_errors"][name])
        if abs(value) > exact.THRESHOLD_FLOAT
    ]
    checks["registered_conservation_counterexamples_remain"] = bool(counterexamples)
    return {
        "filename": PARENT_PATH.name,
        "sha256": _file_sha256(PARENT_PATH),
        "result_digest_sha256": recorded_digest,
        "checks": checks,
        "children": children,
        "prior_input_audit": old_inputs,
        "prior_controls": old_controls,
        "prior_replay": replay,
        "legacy_counterexamples": counterexamples,
        "passed": all(checks.values()),
    }


def regenerate(model, a, degree, name):
    if name == "W":
        return model.embed(a, degree=degree)
    if name == "Phi_W":
        w = model.embed(a, degree=degree)
        return parent.physical.map_step(model.quadratic, w)
    if name == "W_R":
        return model.embed(model.reduced(a, degree=degree), degree=degree)
    raise ValueError("unregistered physical field")


def diagnose_case(model, spec, original, baseline, *, backend, progress=None):
    result = {"specification": spec, "status": "incomplete", "models": {}}
    location = "original_case_replay"
    try:
        fresh = parent.physical_case(model, spec)
        result["original"] = fresh
        result["original_record_digest_sha256"] = digest(fresh)
        result["original_record_reproduced"] = fresh == original
        require(
            fresh == original and fresh["finite"],
            "fresh original case differs from its sealed parent",
        )
        a = np.asarray(spec["a"], dtype=np.float64)
        for degree in (2, 3):
            model_record = {"fields": {}, "comparisons": {}}
            result["models"][str(degree)] = model_record
            old = fresh["models"][str(degree)]
            for name in FIELDS:
                location = f"degree={degree}/field={name}"
                field = regenerate(model, a, degree, name)
                observed = parent.quadratic.array_metadata(field)
                model_record["fields"][name] = {"observed_array": observed}
                require(
                    observed == old["fields"][name]["array"],
                    "regenerated field differs from the original binary64 field",
                )
                measured = exact.field_record(field, backend=backend)
                del field
                model_record["fields"][name] = measured
                require(
                    measured["legacy_conserved_sums"]
                    == old["fields"][name]["global_conserved_sums"],
                    "regenerated legacy sums differ from the original",
                )
                if progress:
                    progress(
                        {
                            "phase": "exact_field",
                            "size": model.quadratic.size,
                            "direction_index": spec["direction_index"],
                            "amplitude": spec["amplitude"],
                            "degree": degree,
                            "field": name,
                            "backend": backend,
                        }
                    )
            for name, (a_name, b_name) in COMPARISONS.items():
                location = f"degree={degree}/comparison={name}"
                fields = model_record["fields"]
                b = baseline["field"] if b_name == "baseline" else fields[b_name]
                model_record["comparisons"][name] = exact.comparison(
                    fields[a_name],
                    b,
                    old["global_conservation_errors"][name],
                    old["site_average_conservation_errors"][name],
                    leaf=b_name == "baseline",
                )
        result["status"] = "computed"
    except ERRORS as exc:
        # Retain original/partial field evidence and its exact failure location.
        result.update(
            status="error", failure_location=location, error_type=type(exc).__name__, error=str(exc)
        )
    return result


def validate_baseline(baseline, size):
    field = baseline["field"]
    exact.validate_field_record(field)
    require(field["array"]["shape"] == [size, size, size, 27], "baseline grid shape mismatch")
    sites = size**3
    expected_populations = [Fraction.from_float(float(w)) * sites for w in parent.d3.WEIGHTS]
    require(
        list(map(exact.decode, field["population_sums"])) == expected_populations,
        "rounded uniform equilibrium exact sums differ",
    )
    analytic = [Fraction(sites), Fraction(0), Fraction(0), Fraction(0)]
    require(
        list(map(exact.decode, baseline["analytic_conserved_sums"])) == analytic,
        "analytic baseline differs",
    )
    expected = [
        (exact.decode(v) - a) / sites
        for v, a in zip(field["conserved_sums"], analytic, strict=True)
    ]
    require(
        list(map(exact.decode, baseline["rounded_baseline_minus_analytic_site_average"]))
        == expected,
        "rounded-versus-analytic baseline difference differs",
    )


def validate_negative_controls(controls, baseline):
    require(
        controls["delta"] == exact.DELTA and controls["passed"] is True, "negative controls failed"
    )
    rows = controls["records"]
    require([r["component"] for r in rows] == list(range(4)), "incomplete negative controls")
    sites = baseline["field"]["site_count"]
    velocity = parent.d3.VELOCITIES
    for component, row in enumerate(rows):
        field = row["field"]
        exact.validate_field_record(field)
        require(
            field["array"]["shape"] == baseline["field"]["array"]["shape"],
            "negative control grid differs",
        )
        expected_population_changes = [Fraction(0)] * 27
        if component == 0:
            expected_population_changes[int(np.flatnonzero(np.all(velocity == 0, axis=1))[0])] = (
                Fraction.from_float(exact.DELTA) * sites
            )
        else:
            axis = np.eye(3, dtype=int)[component - 1]
            for sign in (1, -1):
                q = int(np.flatnonzero(np.all(velocity == sign * axis, axis=1))[0])
                expected_population_changes[q] = sign * Fraction.from_float(exact.DELTA) * sites
        population_changes = [
            exact.decode(a) - exact.decode(b)
            for a, b in zip(
                field["population_sums"], baseline["field"]["population_sums"], strict=True
            )
        ]
        require(
            population_changes == expected_population_changes,
            "negative control population change differs",
        )
        expected = [Fraction(0)] * 4
        expected[component] = Fraction.from_float(exact.DELTA) * (1 if component == 0 else 2)
        actual = [
            (exact.decode(a) - exact.decode(b)) / sites
            for a, b in zip(
                field["conserved_sums"], baseline["field"]["conserved_sums"], strict=True
            )
        ]
        require(
            actual
            == expected
            == list(map(exact.decode, row["expected_site_average_change"]))
            == list(map(exact.decode, row["actual_site_average_change"])),
            "negative control moments differ",
        )
        require(
            row["additions_exact"] is True
            and row["detected_violation"] is True
            and row["passed"] is True
            and max(map(abs, actual)) > exact.THRESHOLD,
            "negative control did not detect known violation",
        )


def validate_case(row, original, baseline):
    require(
        row["status"] == "computed" and row["original_record_reproduced"] is True,
        "case was not fully computed/replayed",
    )
    require(
        row["original"] == original and row["original_record_digest_sha256"] == digest(original),
        "case original evidence mismatch",
    )
    require(
        row["specification"] == parent.record_specification(original), "case specification mismatch"
    )
    require(set(row["models"]) == {"2", "3"}, "missing model degree")
    for degree in ("2", "3"):
        data, old = row["models"][degree], original["models"][degree]
        require(
            set(data["fields"]) == set(FIELDS) and set(data["comparisons"]) == set(COMPARISONS),
            "incomplete fields or comparisons",
        )
        for name in FIELDS:
            field = data["fields"][name]
            exact.validate_field_record(field)
            require(
                field["array"] == old["fields"][name]["array"]
                and field["array"]["shape"] == baseline["field"]["array"]["shape"],
                "saved field metadata differs from the original",
            )
            require(
                field["legacy_conserved_sums"] == old["fields"][name]["global_conserved_sums"],
                "original conserved sums differ",
            )
        for name, (a_name, b_name) in COMPARISONS.items():
            fields = data["fields"]
            b = baseline["field"] if b_name == "baseline" else fields[b_name]
            expected = exact.comparison(
                fields[a_name],
                b,
                old["global_conservation_errors"][name],
                old["site_average_conservation_errors"][name],
                leaf=b_name == "baseline",
            )
            require(
                data["comparisons"][name] == expected
                and all(c["identity_exact"] for c in expected),
                "exact decomposition, counterfactual or gate mismatch",
            )


def audit_grid(grid, parent_grid, *, worker):
    location = "grid_coverage"
    try:
        require(
            grid["size"] == parent_grid["size"] and grid["status"] == "computed",
            "grid failed or changed",
        )
        require(
            grid["input_rebuild"] == parent_grid["input_rebuild"]
            and grid["input_rebuild"]["passed"]
            and grid["fiber_load"] == parent_grid["fiber_load"]
            and grid["fiber_load"]["passed"],
            "fresh source fibers or paired rebuild changed",
        )
        require(
            [r["specification"] for r in grid["records"]] == specifications(worker=worker),
            "incomplete or reordered case coverage",
        )
        require(_all_numeric_values_finite(grid), "nonfinite display evidence")
        location = "rounded_and_analytic_baseline"
        validate_baseline(grid["baseline"], grid["size"])
        location = "negative_controls"
        validate_negative_controls(grid["negative_controls"], grid["baseline"])
        originals = {
            (r["direction_index"], r["amplitude"]): r
            for r in parent_grid["records"]
            if r["kind"] == "amplitude"
        }
        for index, row in enumerate(grid["records"]):
            location = f"case={index}"
            spec = row["specification"]
            validate_case(
                row, originals[spec["direction_index"], spec["amplitude"]], grid["baseline"]
            )
        count = len(grid["records"])
        return {
            "passed": True,
            "cases": count,
            "fields": count * 6,
            "population_sums": count * 6 * 27,
            "component_comparisons": count * 24,
            "negative_controls": 4,
        }
    except ERRORS as exc:
        return {
            "passed": False,
            "failure_location": location,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def grid_campaign(size, parent_grid, *, worker, progress=None):
    backend = "gmp" if worker else "integer"
    grid = {"size": size, "status": "incomplete", "records": []}
    location = "fresh_original_model"
    try:
        model, arrays, rebuilt, _costs = parent.fresh_model(size)
        grid.update(rebuilt)
        del arrays
        gc.collect()
        location = "baseline"
        grid["baseline"] = exact.baseline_record(model.quadratic.base, backend=backend)
        location = "negative_controls"
        grid["negative_controls"] = exact.negative_controls(
            model.quadratic.base, grid["baseline"], backend=backend
        )
        if progress:
            progress(
                {
                    "phase": "baseline_and_negative_controls",
                    "size": size,
                    "backend": backend,
                    "passed": grid["negative_controls"]["passed"],
                }
            )
        originals = {
            (r["direction_index"], r["amplitude"]): r
            for r in parent_grid["records"]
            if r["kind"] == "amplitude"
        }
        for spec in specifications(worker=worker):
            location = f"case={len(grid['records'])}"
            original = originals[spec["direction_index"], spec["amplitude"]]
            row = diagnose_case(
                model, spec, original, grid["baseline"], backend=backend, progress=progress
            )
            grid["records"].append(row)
            if progress:
                progress(
                    {
                        "phase": "case_complete",
                        "size": size,
                        "case": len(grid["records"]),
                        "backend": backend,
                        "status": row["status"],
                    }
                )
        grid["status"] = "computed"
        del model
    except ERRORS as exc:
        grid.update(
            status="error", failure_location=location, error_type=type(exc).__name__, error=str(exc)
        )
    return grid


def summary(grids):
    """Descriptive maxima and all failures, never a gate for baseline-only repair."""
    categories = ("legacy", "exact_field", "sum_only", "base_only")
    result = {
        k: {"components": 0, "maximum_absolute_site_average_error": 0.0, "failures": []}
        for k in categories
    }
    for grid in grids:
        for row in grid.get("records", []):
            if row.get("status") != "computed":
                continue
            for degree, data in row["models"].items():
                for name, comparison in data["comparisons"].items():
                    for component in comparison:
                        values = {
                            "legacy": (
                                exact.exact_float(component["legacy_site_average_error"]),
                                component["legacy_passed"],
                            ),
                            "exact_field": (
                                exact.decode(component["terms"]["exact_field_error"]),
                                component["exact_field_error_passed"],
                            ),
                            "sum_only": (
                                exact.exact_float(
                                    component["sum_only_counterfactual"]["site_average_error"]
                                ),
                                component["sum_only_counterfactual"]["passed"],
                            ),
                        }
                        if component["base_only_counterfactual"] is not None:
                            values["base_only"] = (
                                exact.exact_float(
                                    component["base_only_counterfactual"]["site_average_error"]
                                ),
                                component["base_only_counterfactual"]["passed"],
                            )
                        for key, (error, passed) in values.items():
                            target = result[key]
                            target["components"] += 1
                            target["maximum_absolute_site_average_error"] = max(
                                target["maximum_absolute_site_average_error"], float(abs(error))
                            )
                            if not passed:
                                target["failures"].append(
                                    {
                                        "size": grid["size"],
                                        "direction_index": row["specification"]["direction_index"],
                                        "amplitude": row["specification"]["amplitude"],
                                        "degree": int(degree),
                                        "comparison": name,
                                        "component": component["component"],
                                        "site_average_error": exact.encode(error),
                                    }
                                )
    for target in result.values():
        target["failed_components"] = len(target["failures"])
    return result


def saved_grid(path, grid, current, parent_grid, *, worker):
    document = {
        **current,
        "kind": "Q012g1 exact conservation grid",
        "backend": "gmp" if worker else "integer",
        "grid": grid,
        "grid_digest_sha256": digest(grid),
    }
    write_json(path, document)
    restored = read_json(path)
    audit = audit_grid(restored["grid"], parent_grid, worker=worker)
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "roundtrip_passed": restored == document
        and restored["grid_digest_sha256"] == digest(restored["grid"])
        and _all_numeric_values_finite(restored),
        "full_saved_audit": audit,
    }


def audit_document(saved, path, parent_grids, *, worker):
    """Read every canonical rational and every saved case; fail closed on omission."""
    try:
        require(saved["kind"] == (WORKER_KIND if worker else MAIN_KIND), "wrong campaign kind")
        require(saved["backend"] == ("gmp" if worker else "integer"), "wrong exact backend")
        evidence = saved["evidence"]
        require(digest(evidence) == saved["evidence_digest_sha256"], "campaign digest mismatch")
        require(_all_numeric_values_finite(saved), "nonfinite campaign evidence")
        require([g["size"] for g in evidence["grids"]] == list(SIZES), "missing campaign grid")
        require(len(saved["grid_artifacts"]) == len(SIZES), "missing child artifact")
        audits = []
        for grid, entry, previous in zip(
            evidence["grids"], saved["grid_artifacts"], parent_grids, strict=True
        ):
            audit = audit_grid(grid, previous, worker=worker)
            require(audit["passed"], "full saved grid validation failed: " + str(audit))
            child_path = parent.prior.sibling(path.parent, entry["filename"])
            require(
                child_path == parent.grid_path(path, grid["size"])
                and _file_sha256(child_path) == entry["sha256"],
                "saved child name/seal mismatch",
            )
            child = read_json(child_path)
            require(
                child["grid"] == grid and child["grid_digest_sha256"] == digest(grid),
                "parent/child scientific values mismatch",
            )
            require(
                parent.source_equal(child, saved)
                and child["process_id"] == saved["process_id"]
                and child["backend"] == saved["backend"],
                "parent/child source, process or backend mismatch",
            )
            require(
                entry["roundtrip_passed"] is True and entry["full_saved_audit"] == audit,
                "saved full audit mismatch",
            )
            audits.append(audit)
        require(saved["summary"] == summary(evidence["grids"]), "saved failure summary mismatch")
        return {
            "passed": True,
            "grids": audits,
            "cases": sum(a["cases"] for a in audits),
            "fields": sum(a["fields"] for a in audits),
            "component_comparisons": sum(a["component_comparisons"] for a in audits),
        }
    except ERRORS as exc:
        return {"passed": False, "error_type": type(exc).__name__, "error": str(exc)}


def worker_readiness(saved, path, current, inputs, controls, parent_grids):
    audit = audit_document(saved, path, parent_grids, worker=True)
    checks = {
        "complete_saved_exact_audit": audit["passed"],
        "different_process": saved.get("process_id") != current["process_id"],
        "unchanged_sources": parent.source_equal(saved, current)
        and saved.get("source_unchanged_after") is True,
        "same_inputs_and_controls": saved.get("evidence", {}).get("input_audit") == inputs
        and inputs["passed"]
        and saved.get("evidence", {}).get("artificial_controls") == controls
        and controls["passed"],
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "worker_process_id": saved.get("process_id"),
        "checks": checks,
        "full_saved_audit": audit,
        "passed": all(checks.values()),
    }


def replay_audit(saved, path, current, inputs, controls, grids, parent_grids):
    ready = worker_readiness(saved, path, current, inputs, controls, parent_grids)
    expected_grids = [
        {
            **grid,
            "records": [r for r in grid["records"] if r["specification"]["direction_index"] < 8],
        }
        for grid in grids
    ]
    expected = {"input_audit": inputs, "artificial_controls": controls, "grids": expected_grids}
    matched = saved["evidence"] == expected
    return {
        **ready,
        "all_48_cases_288_fields_1152_components_and_12_controls_exactly_equal": matched,
        "passed": ready["passed"] and matched,
    }


def decision(inputs, controls, grids, files, replay, unchanged):
    complete = [g.get("size") for g in grids] == list(SIZES) and all(
        [r.get("specification") for r in g.get("records", [])] == specifications() for g in grids
    )
    validity = {
        "sealed_parent_and_coefficients": inputs["passed"],
        "artificial_exact_arithmetic_controls": controls["passed"],
        "unchanged_sources": unchanged,
        "full_192_case_coverage": complete,
        "all_original_fields_and_exact_decompositions_audited": len(files) == len(SIZES)
        and all(f["full_saved_audit"]["passed"] for f in files),
        "finite_saved_evidence": _all_numeric_values_finite(grids),
        "all_grid_roundtrips": len(files) == len(SIZES)
        and all(f["roundtrip_passed"] for f in files),
        "independent_gmp_replay": replay.get("passed", False),
    }
    measured = summary(grids)
    hypotheses = {
        "H1_same_fields_conserved_and_sum_only_repair": complete
        and measured["exact_field"]["components"] == 4608
        and measured["sum_only"]["components"] == 4608
        and measured["exact_field"]["failed_components"] == 0
        and measured["sum_only"]["failed_components"] == 0
    }
    valid = all(validity.values())
    outcome = (
        "inconclusive" if not valid else "accepted" if all(hypotheses.values()) else "rejected"
    )
    return validity, hypotheses, outcome


def run(output, *, worker, replay_path=None, progress=None):
    current = metadata()
    inputs, controls = input_audit(), exact.artificial_controls()
    require(
        inputs["passed"] and controls["passed"],
        "parent seals or artificial controls failed before physical work",
    )
    parent_grids = read_json(PARENT_PATH)["cycle"]["grids"]
    witness = None
    if not worker:
        witness = read_json(replay_path)
        require(
            worker_readiness(witness, replay_path, current, inputs, controls, parent_grids)[
                "passed"
            ],
            "a completed separately run full GMP worker is required first",
        )
    grids, files = [], []
    for size, old_grid in zip(SIZES, parent_grids, strict=True):
        if progress:
            progress({"phase": "fresh_grid", "size": size, "worker": worker})
        start = perf_counter()
        grid = grid_campaign(size, old_grid, worker=worker, progress=progress)
        files.append(
            saved_grid(parent.grid_path(output, size), grid, current, old_grid, worker=worker)
        )
        grids.append(grid)
        if progress:
            progress(
                {
                    "phase": "grid_saved",
                    "size": size,
                    "wall_seconds": perf_counter() - start,
                    "audit": files[-1]["full_saved_audit"],
                }
            )
        gc.collect()
    unchanged = parent.source_equal(current, metadata())
    evidence = {"input_audit": inputs, "artificial_controls": controls, "grids": grids}
    result = {
        **current,
        "kind": WORKER_KIND if worker else MAIN_KIND,
        "backend": "gmp" if worker else "integer",
        "evidence": evidence,
        "evidence_digest_sha256": digest(evidence),
        "grid_artifacts": files,
        "source_unchanged_after": unchanged,
        "summary": summary(grids),
        "claim_boundary": "exact rational sums of the same rounded binary64 fields, not exact-real LBM or SSM existence; Q012g rejection, defect-ratio failures and order failures remain unchanged; no TT advantage claim",
    }
    if not worker:
        replay = replay_audit(witness, replay_path, current, inputs, controls, grids, parent_grids)
        validity, hypotheses, outcome = decision(inputs, controls, grids, files, replay, unchanged)
        result.update(
            independent_replay=replay,
            validity_gates=validity,
            hypothesis_gates=hypotheses,
            study_gate="passed" if all(validity.values()) else "failed",
            scientific_outcome=outcome,
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--worker-output", type=Path)
    targets.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    output = args.worker_output or args.output
    worker = args.worker_output is not None
    if (args.output is not None) != (args.replay is not None):
        parser.error("--output requires --replay; --worker-output does not use --replay")
    if any(p.exists() for p in [output, *(parent.grid_path(output, s) for s in SIZES)]):
        parser.error("use fresh paths; existing full or partial evidence is never overwritten")
    progress = lambda row: print(json.dumps(row, allow_nan=False), flush=True)
    result = run(output, worker=worker, replay_path=args.replay, progress=progress)
    write_json(output, result)
    restored = read_json(output)
    post_save = audit_document(
        restored, output, read_json(PARENT_PATH)["cycle"]["grids"], worker=worker
    )
    require(restored == result, "final campaign readback differs from in-memory evidence")
    progress(
        {
            "phase": "final_saved_audit",
            "audit": post_save,
            "source_unchanged_after": result["source_unchanged_after"],
            "scientific_outcome": result.get("scientific_outcome", "worker_only"),
        }
    )
    if (
        not post_save["passed"]
        or not result["source_unchanged_after"]
        or (not worker and result["study_gate"] != "passed")
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
