"""Q012g3: sealed directional defect diagnosis, worker first and main second.

No new chart coefficients are solved or repaired. Direction files are exclusive
checkpoints, not evidence of a live process and not an automatic resume token.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from time import perf_counter

import numpy as np

from research import d3q27_cubic_defect as defect
from research import d3q27_defect_evidence as evidence
from research import q012g1_d3q27_conservation as prior
from research import q012g2_cubic_defect_oracle as oracle
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

parent, require, read_json, digest = prior.parent, prior.require, prior.read_json, prior.digest
SIZES = evidence.SIZES
ROOT = Path(__file__).resolve().parents[1]
PRIOR_PATH = prior.PARENT_PATH.with_name("q012g1_d3q27_conservation.json")
ORACLE_PATH = prior.PARENT_PATH.with_name("q012g2_cubic_defect_oracle.json")
PRIOR_WORKER_PATH = prior.PARENT_PATH.with_name("q012g1_d3q27_conservation_replay.json")
INPUT_SEALS = {
    prior.PARENT_PATH: prior.PARENT_SHA,
    PRIOR_PATH: "ca6b15627880cbe390f6a53bc87eb9a6ba0833f1f370c5b9ea2c494625e75000",
    ORACLE_PATH: "493f78e85887821862dbfae135b30c019979369b285db5e114772eb71dd90b03",
    PRIOR_WORKER_PATH: "b745e66a011972ecd10a76429b827456c21690ddd5bd7291a643a5629cc7c1e5",
}
CONTROL_TESTS = (
    "tests/test_d3q27_cubic_defect.py",
    "tests/test_d3q27_defect_evidence.py",
    "tests/test_polynomial_path.py",
    "tests/test_q012g2_cubic_defect_oracle.py",
    "tests/test_q012g2_cubic_defect_oracle_artifact.py",
)
HELPERS = prior.HELPERS + (
    ("conservation_runner", prior),
    ("path_algebra", defect.poly),
    ("degree_oracle_runner", oracle),
    ("defect_profile", defect),
    ("defect_evidence", evidence),
)
WORKER_KIND = "Q012g3 independent 192-case degree-resolved worker"
MAIN_KIND = "Q012g3 full 960-case degree-resolved diagnosis"
BOUNDARY = "Existing W2/W3 only, not W9; unchanged Q012g rejection; no SSM existence, continuous ball, long-time or TT advantage claim."
ERRORS = prior.ERRORS + (IndexError, MemoryError)


def control_seals():
    return {p: _file_sha256(ROOT / p) for p in CONTROL_TESTS}


def metadata():
    current = prior.metadata()
    current["runner_source"] = {
        "filename": Path(__file__).name,
        "sha256": _file_sha256(Path(__file__)),
    }
    current["helper_sources"] = {
        name: {
            "filename": Path(module.__file__).name,
            "sha256": _file_sha256(Path(module.__file__)),
        }
        for name, module in HELPERS
    }
    current["control_test_sources"] = control_seals()
    return current


def source_equal(left, right):
    return (
        parent.source_equal(left, right)
        and left["control_test_sources"] == right["control_test_sources"]
    )


def source_digest(current):
    return digest({k: current[k] for k in (*parent.SOURCE_KEYS, "control_test_sources")})


def controls():
    """Execute the registered small-grid and prior-oracle controls, not a physical campaign."""
    before = control_seals()
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *CONTROL_TESTS, "-q", "-W", "error"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    match = re.search(r"(?:^|\s)(\d+) passed(?:\s|,)", completed.stdout)
    count = int(match.group(1)) if match else None
    science = {
        "test_sources": before,
        "exit_code": completed.returncode,
        "passed_tests": count,
        "sources_unchanged": before == control_seals(),
    }
    science["passed"] = completed.returncode == 0 and count == 177 and science["sources_unchanged"]
    return science, {"stdout": completed.stdout, "stderr": completed.stderr}


def input_audit():
    seals = {str(p): _file_sha256(p) for p in INPUT_SEALS}
    require(
        all(seals[str(p)] == value for p, value in INPUT_SEALS.items()),
        "a preregistered input seal changed",
    )
    parents = read_json(prior.PARENT_PATH)["cycle"]["grids"]
    conserved, manufactured = read_json(PRIOR_PATH), read_json(ORACLE_PATH)
    old_inputs = prior.input_audit()
    saved_audit = prior.audit_document(conserved, PRIOR_PATH, parents, worker=False)
    replay = prior.replay_audit(
        read_json(PRIOR_WORKER_PATH),
        PRIOR_WORKER_PATH,
        conserved,
        conserved["evidence"]["input_audit"],
        conserved["evidence"]["artificial_controls"],
        conserved["evidence"]["grids"],
        parents,
    )
    checks = {
        "all_input_seals": all(seals[str(p)] == v for p, v in INPUT_SEALS.items()),
        "unchanged_parent_sources": parent.source_equal(conserved, prior.metadata()),
        "full_parent_and_coefficient_chain": old_inputs["passed"]
        and old_inputs == conserved["evidence"]["input_audit"],
        "conservation_accepted": conserved["study_gate"] == "passed"
        and conserved["scientific_outcome"] == "accepted"
        and all(conserved["validity_gates"].values())
        and all(conserved["hypothesis_gates"].values()),
        "all_saved_conservation_values": saved_audit["passed"],
        "full_gmp_replay": replay["passed"] and replay == conserved["independent_replay"],
        "oracle_accepted_and_fully_audited": manufactured["decision"]["scientific_outcome"]
        == "accepted"
        and oracle.audit_document(manufactured),
    }
    return {
        "sha256": seals,
        "checks": checks,
        "previous_input_chain": old_inputs,
        "conservation_saved_audit": saved_audit,
        "conservation_replay": replay,
        "passed": all(checks.values()),
    }


def nonfinite_tags(value):
    """Preserve exceptional evidence explicitly; never replace it with zero."""
    if isinstance(value, dict):
        return {k: nonfinite_tags(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [nonfinite_tags(v) for v in value]
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return {"nonfinite_float": str(value)}
    return value


def save_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, allow_nan=False, separators=(",", ":"))
        handle.write("\n")
    restored = read_json(path)
    require(restored == value, "new artifact failed exact JSON readback")
    return {"filename": path.name, "sha256": _file_sha256(path)}


def direction_path(output, size, schedule):
    return output.with_name(
        f"{output.stem}_n{size}_{schedule['kind']}_{schedule['direction_index']:02d}.json"
    )


@contextmanager
def execution_lock(path):
    """An OS-held lock, automatically released on process exit; no stale-PID inference."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def original_fields(model, spec, degree, old):
    a = np.asarray(spec["a"], dtype=float)
    fields = {name: prior.regenerate(model, a, degree, name) for name in evidence.FIELDS}
    observed = {name: parent.quadratic.array_metadata(v) for name, v in fields.items()}
    require(
        observed == {name: old["fields"][name]["array"] for name in evidence.FIELDS},
        "fresh field differs from original shape/dtype/bytes/hash",
    )
    raw = fields["Phi_W"] - fields["W_R"]
    require(
        parent.quadratic.array_metadata(raw) == old["defect_array"]
        and defect.norm(raw) == old["defect_norm"],
        "fresh defect differs from the original",
    )
    return fields, observed


def diagnose_direction(
    model, schedule, originals, original_fit, conserved_rows, *, worker, progress=None
):
    row = {
        "schedule": schedule,
        "status": "incomplete",
        "profiles": {},
        "cases": [],
        "fit_prediction": None,
    }
    costs, location = {}, "original_record_replay"
    start = perf_counter()
    try:
        for spec in schedule["specifications"]:
            old = originals[evidence.case_key(spec)]
            fresh = parent.physical_case(model, spec)
            case = {
                "specification": spec,
                "status": "incomplete",
                "original": fresh,
                "original_record_digest_sha256": digest(fresh),
                "original_record_reproduced": fresh == old,
                "models": {},
                "holdout_prediction": None,
            }
            row["cases"].append(case)
            require(fresh == old and fresh["finite"], "fresh whole original case changed")
            require(
                spec["a"] == (spec["amplitude"] * np.asarray(schedule["direction"])).tolist(),
                "direction must be the original RNG-normalized u",
            )
        costs["original_records_seconds"] = perf_counter() - start
        for degree in (2, 3):
            location = f"degree={degree}/primary_profile"
            start = perf_counter()
            primary = defect.build_profile(model, schedule["direction"], degree)
            profiles = row["profiles"][str(degree)] = {"primary": primary.audit}
            costs[f"degree_{degree}_primary_profile_seconds"] = perf_counter() - start
            for arm in ("primary", "independent") if worker else ("primary",):
                if arm == "independent":
                    location = f"degree={degree}/independent_profile"
                    start = perf_counter()
                    # All primary sample tails have already been evaluated. Only
                    # these disposable buffers are released; maps/coefficients stay unchanged.
                    primary = replace(primary, local=replace(primary.local, remainder=()))
                    gc.collect()
                    profile = defect.build_profile(model, schedule["direction"], degree, arm=arm)
                    profiles[arm] = profile.audit
                    profiles["comparison"] = defect.compare_profiles(primary, profile)
                    costs[f"degree_{degree}_independent_profile_and_comparison_seconds"] = (
                        perf_counter() - start
                    )
                    del primary
                    gc.collect()
                else:
                    profile = primary
                start = perf_counter()
                for case in row["cases"]:
                    spec, old = case["specification"], case["original"]["models"][str(degree)]
                    location = f"degree={degree}/arm={arm}/amplitude={spec['amplitude']}"
                    fields, observed = original_fields(model, spec, degree, old)
                    if arm == "primary":
                        conserved = None
                        if spec["kind"] == "amplitude":
                            conserved = {
                                name: prior.exact.field_record(v, backend="integer")
                                for name, v in fields.items()
                            }
                            require(
                                conserved
                                == conserved_rows[evidence.case_key(spec)]["models"][str(degree)][
                                    "fields"
                                ],
                                "fresh exact holdout fields differ from Q012g1",
                            )
                        case["models"][str(degree)] = {
                            "original_fields": observed,
                            "defect_array": old["defect_array"],
                            "conservation_fields": conserved,
                            "samples": {},
                            "R_path_difference_norms": {},
                        }
                    sample = defect.sample_diagnostics(profile, spec["amplitude"], fields)
                    data = case["models"][str(degree)]
                    data["samples"][arm] = sample
                    data["R_path_difference_norms"][arm] = defect.norm(
                        np.asarray(sample["reconstructed_reduced_coordinates"])
                        - old["reduced_coordinates"]
                    )
                    del fields
                    if progress:
                        progress(
                            {
                                "phase": "sample",
                                "size": model.quadratic.size,
                                "kind": spec["kind"],
                                "direction_index": spec["direction_index"],
                                "degree": degree,
                                "arm": arm,
                                "amplitude": spec["amplitude"],
                                "H1": sample["H1_reconstruction_passed"],
                            }
                        )
                costs[f"degree_{degree}_{arm}_samples_seconds"] = perf_counter() - start
                if arm == "primary" and worker:
                    del profile  # Otherwise it would keep the released tail buffers alive.
            del profile
            if not worker:
                del primary
            gc.collect()
        for case in row["cases"]:
            case["status"] = "computed"
            if schedule["kind"] == "amplitude":
                case["holdout_prediction"] = evidence.holdout_prediction(
                    case["original"],
                    {d: v["samples"]["primary"] for d, v in case["models"].items()},
                )
        if schedule["kind"] == "order":
            row["fit_prediction"] = evidence.fit_prediction(
                [c["original"] for c in row["cases"]],
                [
                    {d: v["samples"]["primary"] for d, v in c["models"].items()}
                    for c in row["cases"]
                ],
                original_fit,
            )
        require(_all_numeric_values_finite(row), "nonfinite directional evidence")
        row["status"] = "computed"
    except ERRORS as exc:
        row.update(
            status="error", failure_location=location, error_type=type(exc).__name__, error=str(exc)
        )
    return nonfinite_tags(row), costs


def maps(old_grid, conserved_grid):
    originals = {
        evidence.case_key(r): r for r in old_grid["records"] if r["kind"] in ("order", "amplitude")
    }
    conserved = {evidence.case_key(r["specification"]): r for r in conserved_grid["records"]}
    fits = {r["direction_key"]: r for r in old_grid["generic_fits"]}
    return originals, conserved, fits


def audit_grid(grid, old_grid, conserved_grid, *, worker):
    location = "coverage"
    try:
        require(
            grid["status"] == "computed"
            and grid["size"] == old_grid["size"] == conserved_grid["size"],
            "grid incomplete or size changed",
        )
        require(
            grid["input_rebuild"] == old_grid["input_rebuild"]
            and grid["input_rebuild"]["passed"]
            and grid["fiber_load"] == old_grid["fiber_load"]
            and grid["fiber_load"]["passed"],
            "fresh rebuild or fibers differ",
        )
        schedule = evidence.direction_schedule(worker=worker)
        require(
            [r["schedule"] for r in grid["directions"]] == schedule,
            "direction coverage missing, duplicated or reordered",
        )
        require(_all_numeric_values_finite(grid), "nonfinite grid")
        originals, conserved, fits = maps(old_grid, conserved_grid)
        audits, gates = [], []
        for row, spec in zip(grid["directions"], schedule, strict=True):
            location = f"{spec['kind']}/{spec['direction_index']}"
            audits.append(
                evidence.validate_direction(
                    row,
                    spec,
                    originals,
                    fits.get(spec["direction_index"]),
                    conserved,
                    size=grid["size"],
                    worker=worker,
                )
            )
            gates.append(evidence.direction_gates(row, worker=worker))
        return {
            "passed": True,
            "cases": sum(r["cases"] for r in audits),
            "profiles": sum(r["profiles"] for r in audits),
            "original_fields": sum(r["original_fields"] for r in audits),
            "original_defects": sum(r["original_defects"] for r in audits),
            "independent_vector_comparisons": sum(
                r["independent_vector_comparisons"] for r in audits
            ),
            "direction_gates": gates,
        }
    except ERRORS as exc:
        return {
            "passed": False,
            "failure_location": location,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def header(current):
    return {
        "process_id": current["process_id"],
        "generated_at_utc": current["generated_at_utc"],
        "source_digest_sha256": source_digest(current),
    }


def grid_campaign(output, size, old_grid, conserved_grid, current, *, worker, progress=None):
    grid = {"size": size, "status": "incomplete", "directions": []}
    entries, costs, location = [], {}, "fresh_model"
    try:
        model, arrays, rebuilt, costs = parent.fresh_model(size)
        grid.update(rebuilt)
        del arrays
        gc.collect()
        originals, conserved, fits = maps(old_grid, conserved_grid)
        for spec in evidence.direction_schedule(worker=worker):
            location = f"{spec['kind']}/{spec['direction_index']}"
            row, measured = diagnose_direction(
                model,
                spec,
                originals,
                fits.get(spec["direction_index"]),
                conserved,
                worker=worker,
                progress=progress,
            )
            grid["directions"].append(row)
            path = direction_path(output, size, spec)
            entries.append(
                save_new(
                    path,
                    {
                        **header(current),
                        "size": size,
                        "direction": row,
                        "direction_digest_sha256": digest(row),
                        "diagnosis_costs": measured,
                    },
                )
            )
            if progress:
                progress(
                    {
                        "phase": "direction_saved",
                        "size": size,
                        "kind": spec["kind"],
                        "direction_index": spec["direction_index"],
                        "status": row["status"],
                        "artifact": entries[-1],
                    }
                )
        grid["status"] = "computed"
    except ERRORS as exc:
        grid.update(
            status="error", failure_location=location, error_type=type(exc).__name__, error=str(exc)
        )
    grid = nonfinite_tags(grid)
    audit = audit_grid(grid, old_grid, conserved_grid, worker=worker)
    child = {
        **header(current),
        "worker": worker,
        "grid": grid,
        "grid_digest_sha256": digest(grid),
        "direction_artifacts": entries,
        "fresh_input_costs": costs,
        "full_saved_audit": audit,
    }
    entry = save_new(parent.grid_path(output, size), child)
    entry.update(roundtrip_passed=True, full_saved_audit=audit)
    return grid, entry


def summary(grids):
    counts = {"directions": 0, "cases": 0, "profiles": 0}
    failures = {k: [] for k in ("incomplete", "H1", "H2", "H3", "Gram", "independent")}
    leading, maxima = [], {}
    for grid in grids:
        for row in grid.get("directions", []):
            key = {
                "size": grid["size"],
                "kind": row["schedule"]["kind"],
                "direction_index": row["schedule"]["direction_index"],
            }
            if row["status"] != "computed":
                failures["incomplete"].append(
                    {
                        **key,
                        "failure_location": row.get("failure_location"),
                        "error": row.get("error"),
                    }
                )
                continue
            counts["directions"] += 1
            counts["profiles"] += 2
            counts["cases"] += len(row["cases"])
            c3 = row["profiles"]["2"]["primary"]["defect_coefficients"][3]["norm"]
            c4 = row["profiles"]["3"]["primary"]["defect_coefficients"][4]["norm"]
            leading.append(
                {
                    **key,
                    "C3_norm": c3,
                    "C4_norm": c4,
                    "C4_to_C3_norm_ratio": c4 / c3 if c3 > 0 else None,
                }
            )
            for d, profile in row["profiles"].items():
                if "comparison" in profile:
                    for r in profile["comparison"]["rows"]:
                        if not r["passed"]:
                            failures["independent"].append(
                                {**key, "degree": int(d), "comparison": r}
                            )
            for case in row["cases"]:
                for d, data in case["models"].items():
                    for arm, sample in data["samples"].items():
                        sample_key = {
                            **key,
                            "degree": int(d),
                            "arm": arm,
                            "amplitude": case["specification"]["amplitude"],
                        }
                        for name, value in sample["reconstruction_errors"].items():
                            record = {
                                **sample_key,
                                "comparison": name,
                                "error_norm": value,
                                "roundoff_floor": sample["roundoff_floor"],
                            }
                            if name not in maxima or value > maxima[name]["error_norm"]:
                                maxima[name] = record
                            if value > sample["roundoff_floor"]:
                                failures["H1"].append(record)
                        for r in sample["truncations"]:
                            if not r["gram_passed"]:
                                failures["Gram"].append({**sample_key, "truncation": r})
                predicted = case["holdout_prediction"]
                if predicted is not None and not predicted["H2_passed"]:
                    failures["H2"].append(
                        {
                            **key,
                            "amplitude": case["specification"]["amplitude"],
                            "prediction": predicted,
                            "models": {
                                d: {
                                    "vector_relative_error": v["samples"]["primary"][
                                        "P9_vector_relative_error"
                                    ],
                                    "vector_passed": v["samples"]["primary"]["P9_vector_passed"],
                                }
                                for d, v in case["models"].items()
                            },
                        }
                    )
            if row["fit_prediction"] is not None and not row["fit_prediction"]["H3_passed"]:
                failures["H3"].append({**key, "prediction": row["fit_prediction"]})
    return {
        "counts": counts,
        "failures": failures,
        "failure_counts": {k: len(v) for k, v in failures.items()},
        "maximum_reconstruction_error": maxima,
        "descriptive_leading_ratios": leading,
    }


def decision(inputs, controls, grids, entries, replay, unchanged, *, worker, inputs_unchanged):
    complete = [g.get("size") for g in grids] == list(SIZES) and all(
        [r.get("schedule") for r in g.get("directions", [])]
        == evidence.direction_schedule(worker=worker)
        for g in grids
    )
    audited = len(entries) == 3 and all(e["full_saved_audit"]["passed"] for e in entries)
    gates = [
        g
        for entry in entries
        if entry["full_saved_audit"]["passed"]
        for g in entry["full_saved_audit"]["direction_gates"]
    ]
    validity = {
        "sealed_inputs_and_coefficients": inputs["passed"],
        "artificial_controls": controls["passed"],
        "unchanged_sources": unchanged,
        "unchanged_inputs_after": inputs_unchanged,
        "full_registered_coverage": complete,
        "all_original_records_fields_and_exact_holdouts_audited": audited,
        "finite_evidence": _all_numeric_values_finite(grids),
        "all_grid_roundtrips": len(entries) == 3 and all(e["roundtrip_passed"] for e in entries),
        "all_gram_comparisons": audited and all(g["all_gram_comparisons_passed"] for g in gates),
        "independent_vectors_and_both_arm_H1": audited
        and all(
            g["independent_vectors_passed"] and g["worker_both_arm_reconstruction_passed"]
            for g in gates
        )
        if worker
        else replay.get("passed", False),
    }
    hypotheses = {
        f"H{i}": complete
        and audited
        and all(g[f"H{i}"] is True for g in gates if g[f"H{i}"] is not None)
        for i in (1, 2, 3)
    }
    valid = all(validity.values())
    return {
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_gate": "passed" if valid else "failed",
        "scientific_outcome": "inconclusive"
        if not valid
        else "worker_only"
        if worker
        else "accepted"
        if all(hypotheses.values())
        else "rejected",
    }


def audit_document(saved, output, old_grids, conserved_grids, *, worker):
    try:
        require(
            saved["kind"] == (WORKER_KIND if worker else MAIN_KIND)
            and saved["claim_boundary"] == BOUNDARY,
            "campaign kind/scope differs",
        )
        require(
            source_equal(saved, metadata()) and saved["source_unchanged_after"] is True,
            "campaign source differs",
        )
        require(_all_numeric_values_finite(saved), "nonfinite saved campaign")
        body = saved["evidence"]
        fresh_inputs = input_audit()
        require(
            fresh_inputs == body["input_audit"] == saved["input_audit_after"]
            and fresh_inputs["passed"]
            and saved["inputs_unchanged_after"] is True,
            "campaign inputs changed before final readback",
        )
        control = body["controls"]
        require(
            control
            == {
                "test_sources": control_seals(),
                "exit_code": 0,
                "passed_tests": 177,
                "sources_unchanged": True,
                "passed": True,
            },
            "registered control result or sources differ",
        )
        require(saved["evidence_digest_sha256"] == digest(body), "campaign digest differs")
        require(
            [g["size"] for g in body["grids"]] == list(SIZES) and len(saved["grid_artifacts"]) == 3,
            "campaign grid coverage incomplete",
        )
        audits = []
        for grid, entry, old, conserved in zip(
            body["grids"], saved["grid_artifacts"], old_grids, conserved_grids, strict=True
        ):
            audit = audit_grid(grid, old, conserved, worker=worker)
            require(
                audit["passed"]
                and audit == entry["full_saved_audit"]
                and entry["roundtrip_passed"] is True,
                "saved grid audit failed or differs",
            )
            path = parent.grid_path(output, grid["size"])
            require(
                entry["filename"] == path.name and entry["sha256"] == _file_sha256(path),
                "grid artifact name/seal differs",
            )
            child = read_json(path)
            require(
                child["grid"] == grid
                and child["grid_digest_sha256"] == digest(grid)
                and child["full_saved_audit"] == audit
                and child["worker"] is worker
                and all(child[k] == v for k, v in header(saved).items()),
                "grid child values/source/process differ",
            )
            require(
                len(child["direction_artifacts"]) == len(grid["directions"]),
                "missing direction artifacts",
            )
            for row, reference in zip(
                grid["directions"], child["direction_artifacts"], strict=True
            ):
                path = direction_path(output, grid["size"], row["schedule"])
                require(
                    reference["filename"] == path.name
                    and reference["sha256"] == _file_sha256(path),
                    "direction artifact name/seal differs",
                )
                restored = read_json(path)
                require(
                    restored["size"] == grid["size"]
                    and restored["direction"] == row
                    and restored["direction_digest_sha256"] == digest(row)
                    and all(restored[k] == v for k, v in header(saved).items())
                    and _all_numeric_values_finite(restored),
                    "direction readback differs",
                )
            audits.append(audit)
        require(saved["summary"] == summary(body["grids"]), "saved failure summary differs")
        if not worker:
            reference = saved["independent_replay"]
            replay_path = parent.prior.sibling(output.parent, reference["filename"])
            actual = replay_audit(
                read_json(replay_path),
                replay_path,
                saved,
                body["input_audit"],
                body["controls"],
                body["grids"],
                old_grids,
                conserved_grids,
            )
            require(actual == reference and actual["passed"], "saved independent replay differs")
        expected = decision(
            body["input_audit"],
            body["controls"],
            body["grids"],
            saved["grid_artifacts"],
            saved["independent_replay"],
            saved["source_unchanged_after"],
            worker=worker,
            inputs_unchanged=saved["inputs_unchanged_after"],
        )
        require(saved["decision"] == expected, "saved decision differs")
        return {
            "passed": True,
            "cases": sum(a["cases"] for a in audits),
            "profiles": sum(a["profiles"] for a in audits),
            "independent_vector_comparisons": sum(
                a["independent_vector_comparisons"] for a in audits
            ),
            "grids": audits,
        }
    except ERRORS as exc:
        return {"passed": False, "error_type": type(exc).__name__, "error": str(exc)}


def worker_readiness(saved, path, current, inputs, control, old_grids, conserved_grids):
    audit = audit_document(saved, path, old_grids, conserved_grids, worker=True)
    checks = {
        "complete_worker_readback": audit["passed"],
        "separate_process": saved.get("process_id") != current["process_id"],
        "same_sources": source_equal(saved, current),
        "same_inputs_and_controls": saved["evidence"]["input_audit"] == inputs
        and inputs["passed"]
        and saved["evidence"]["controls"] == control
        and control["passed"],
        "worker_all_validity_gates": saved.get("decision", {}).get("study_gate") == "passed",
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "worker_process_id": saved.get("process_id"),
        "checks": checks,
        "full_saved_audit": audit,
        "passed": all(checks.values()),
    }


def replay_audit(witness, path, current, inputs, control, grids, old_grids, conserved_grids):
    ready = worker_readiness(witness, path, current, inputs, control, old_grids, conserved_grids)
    comparisons = []
    for saved, main in zip(witness["evidence"]["grids"], grids, strict=True):
        selected = {
            (d["kind"], d["direction_index"]) for d in evidence.direction_schedule(worker=True)
        }
        chosen = [
            r
            for r in main["directions"]
            if (r["schedule"]["kind"], r["schedule"]["direction_index"]) in selected
        ]
        matched = len(chosen) == len(saved["directions"]) and all(
            evidence.primary_record(a) == evidence.primary_record(b)
            for a, b in zip(chosen, saved["directions"], strict=True)
        )
        comparisons.append({"size": main["size"], "all_primary_scientific_records_equal": matched})
    return {
        **ready,
        "main_correspondence": comparisons,
        "passed": ready["passed"]
        and len(comparisons) == 3
        and all(r["all_primary_scientific_records_equal"] for r in comparisons),
    }


def run(output, *, worker, replay_path=None, progress=None):
    output = Path(output).resolve()
    replay_path = Path(replay_path).resolve() if replay_path is not None else None
    current = metadata()
    targets = [
        output,
        *(parent.grid_path(output, s) for s in SIZES),
        *(
            direction_path(output, s, d)
            for s in SIZES
            for d in evidence.direction_schedule(worker=worker)
        ),
    ]
    require(
        not any(p.exists() for p in targets),
        "fresh output paths required; never overwrite full or partial evidence",
    )
    require(worker == (replay_path is None), "main requires replay and worker must not take replay")
    require(
        worker or replay_path.parent == output.parent,
        "worker and main artifacts must share a directory for audited replay links",
    )
    if progress:
        progress({"phase": "input_audit", "process_id": os.getpid(), "worker": worker})
    inputs = input_audit()
    control, control_output = controls()
    require(
        inputs["passed"] and control["passed"],
        "sealed inputs or artificial controls failed before physical work",
    )
    old_grids = read_json(prior.PARENT_PATH)["cycle"]["grids"]
    conserved_grids = read_json(PRIOR_PATH)["evidence"]["grids"]
    witness, replay = None, {"scope": "independent worker; main correspondence not yet applicable"}
    if not worker:
        witness = read_json(replay_path)
        ready = worker_readiness(
            witness, replay_path, current, inputs, control, old_grids, conserved_grids
        )
        require(
            ready["passed"], "completed independently audited 192-case worker required before main"
        )
    grids, entries = [], []
    for size, old, conserved in zip(SIZES, old_grids, conserved_grids, strict=True):
        if progress:
            progress({"phase": "fresh_grid", "size": size, "worker": worker})
        grid, entry = grid_campaign(
            output, size, old, conserved, current, worker=worker, progress=progress
        )
        grids.append(grid)
        entries.append(entry)
        if progress:
            progress({"phase": "grid_saved", "size": size, "audit": entry["full_saved_audit"]})
        gc.collect()
    if not worker:
        try:
            replay = replay_audit(
                witness, replay_path, current, inputs, control, grids, old_grids, conserved_grids
            )
        except ERRORS as exc:
            replay = {"passed": False, "error_type": type(exc).__name__, "error": str(exc)}
    unchanged = source_equal(current, metadata())
    try:
        after = input_audit()
        inputs_unchanged = after == inputs and after["passed"]
    except ERRORS as exc:
        after = {"passed": False, "error_type": type(exc).__name__, "error": str(exc)}
        inputs_unchanged = False
    body = {"input_audit": inputs, "controls": control, "grids": grids}
    result = {
        **current,
        "kind": WORKER_KIND if worker else MAIN_KIND,
        "claim_boundary": BOUNDARY,
        "evidence": body,
        "evidence_digest_sha256": digest(body),
        "grid_artifacts": entries,
        "source_unchanged_after": unchanged,
        "input_audit_after": after,
        "inputs_unchanged_after": inputs_unchanged,
        "independent_replay": replay,
        "control_execution_output": control_output,
        "summary": summary(grids),
        "decision": decision(
            inputs,
            control,
            grids,
            entries,
            replay,
            unchanged,
            worker=worker,
            inputs_unchanged=inputs_unchanged,
        ),
    }
    save_new(output, result)
    audit = audit_document(read_json(output), output, old_grids, conserved_grids, worker=worker)
    if progress:
        progress({"phase": "final_saved_audit", "audit": audit, "decision": result["decision"]})
    return result, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--worker-output", type=Path)
    targets.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    worker = args.worker_output is not None
    if worker != (args.replay is None):
        parser.error("--output requires --replay; --worker-output does not use --replay")
    output = args.worker_output or args.output
    progress = lambda row: print(json.dumps(row, allow_nan=False), flush=True)
    with execution_lock(parent.foundation.ARTIFACT_DIRECTORY / ".q012g3.execution.lock"):
        result, audit = run(output, worker=worker, replay_path=args.replay, progress=progress)
    if not audit["passed"] or result["decision"]["study_gate"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
