"""Q012g registered cubic evaluator, full-map defects, and sequential replay.

Run the independent 144-case worker before the three-grid main campaign. No
coefficient solves are repeated or changed here except the registered fresh
quadratic input rebuild. Existing artifacts and sources are read-only inputs.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from dataclasses import is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as quadratic
from research import d3q27_cubic as cubic
from research import d3q27_cubic_chart as chart
from research import d3q27_refined_cubic as refined
from research import q012a_d3q27_foundation as foundation
from research import q012d_d3q27_quadratic_chart as physical
from research import q012f2_d3q27_refined_cubic as prior
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = foundation.ARTIFACT_DIRECTORY / "q012f2_d3q27_refined_cubic.json"
PRIOR_SHA = "65a0046d2b54c1192a84fbce481da0e804364cf62566d2e9c18204e372158ec1"
PRIOR_DIGEST = "ca64e1235a4dc94a4736bc051f9bbd780835a77d3ed0718bf886f93064c1ef7f"
HELPERS = prior.HELPERS + (("refined_runner", prior), ("cubic_chart", chart))
SOURCE_KEYS = ("source", "runner_source", "helper_sources")
ORDER_SEED, AMPLITUDE_SEED, SYMMETRY_SEED, COST_SEED = range(2026090724, 2026090728)
AMPLITUDES = (0.008, 0.004, 0.002, 0.001)
HOLDOUT_AMPLITUDES = (0.008, 0.032)
ERRORS = prior.ERRORS + (TypeError, KeyError)
METHODS = ("W2", "W3", "R2", "R3", "Phi_W3")


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


def source_equal(left, right):
    return all(left[k] == right[k] for k in SOURCE_KEYS)


def input_audit():
    saved = prior.read_json(PRIOR_PATH)
    cycle = dict(saved["cycle"])
    digest = cycle.pop("result_digest_sha256")
    old_inputs, old_controls = prior.input_audit(), prior.controls()
    checks = {
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA,
        "cycle_digest": foundation._digest(cycle) == digest == PRIOR_DIGEST,
        "accepted_preflight": saved["study_gate"] == "passed"
        and saved["scientific_outcome"] == "accepted",
        "all_11_validity_gates": len(cycle["validity_gates"]) == 11
        and all(cycle["validity_gates"].values()),
        "all_2_hypotheses": len(cycle["hypothesis_gates"]) == 2
        and all(cycle["hypothesis_gates"].values()),
        "preflight_sources": source_equal(saved, prior.metadata()),
        "previous_input_chain": old_inputs == cycle["input_audit"] and old_inputs["passed"],
        "previous_controls": old_controls == cycle["controls"] and old_controls["passed"],
        "registered_grids": [g["size"] for g in cycle["grids"]] == list(cubic.SIZES),
    }
    archives = []
    for grid, registered in zip(cycle["grids"], cycle["grid_artifacts"], strict=True):
        grid_path = prior.sibling(PRIOR_PATH.parent, registered["filename"])
        document = prior.read_json(grid_path)
        core = dict(grid)
        grid_digest = core.pop("result_digest_sha256")
        record = grid["record_archive"]
        record_path = prior.sibling(PRIOR_PATH.parent, record["filename"])
        fiber = grid["fiber_archive"]
        fiber_path = prior.sibling(PRIOR_PATH.parent, fiber["filename"])
        arrays, fiber_audit = chart.load_fibers(fiber_path, fiber)
        del arrays
        row_checks = {
            "grid_result_seal": _file_sha256(grid_path) == registered["sha256"],
            "grid_source_and_values": source_equal(saved, document) and document["grid"] == grid,
            "grid_digest": foundation._digest(core) == grid_digest,
            "previously_all_row_audited_record_bytes": record_path.stat().st_size == record["bytes"]
            and refined.file_hash(record_path) == record["sha256"],
            "all_fiber_metadata_and_support": fiber_audit["passed"],
        }
        archives.append(
            {
                "size": grid["size"],
                "checks": row_checks,
                "fibers": fiber_audit,
                "passed": all(row_checks.values()),
            }
        )
    replay = prior.replay_audit(
        prior.sibling(PRIOR_PATH.parent, cycle["independent_replay"]["filename"]),
        old_inputs,
        old_controls,
        cycle["grids"],
        saved,
    )
    checks["all_three_archive_seals"] = len(archives) == 3 and all(g["passed"] for g in archives)
    checks["full_972_replay_evidence"] = replay == cycle["independent_replay"] and replay["passed"]
    return {
        "filename": PRIOR_PATH.name,
        "checks": checks,
        "archives": archives,
        "replay": replay,
        "scope": "unchanged previously all-row-audited record bytes; fresh full fiber shape/support/hash checks and all 972 saved replay witnesses, not new cubic solves",
        "passed": all(checks.values()),
    }


def fresh_model(size):
    start = perf_counter()
    model, rebuild, _, _ = prior.fresh_input(size)
    rebuild_seconds = perf_counter() - start
    grid = next(g for g in prior.read_json(PRIOR_PATH)["cycle"]["grids"] if g["size"] == size)
    if rebuild != grid["input_rebuild"] or not rebuild["passed"]:
        raise ValueError("fresh paired quadratic input differs from the sealed preflight")
    start = perf_counter()
    arrays, loaded = chart.load_fibers(
        prior.sibling(PRIOR_PATH.parent, grid["fiber_archive"]["filename"]),
        grid["fiber_archive"],
    )
    load_seconds = perf_counter() - start
    start = perf_counter()
    evaluator = chart.CubicChart(model, arrays)
    prepared_storage = evaluator.storage()
    preparation_seconds = perf_counter() - start
    return (
        evaluator,
        arrays,
        {"input_rebuild": rebuild, "fiber_load": loaded},
        {
            "fresh_quadratic_rebuild_seconds": rebuild_seconds,
            "cubic_archive_load_and_audit_seconds": load_seconds,
            "cubic_evaluator_preparation_seconds": preparation_seconds,
            "cubic_serialized_bytes": grid["fiber_archive"]["bytes"],
            "cubic_original_array_bytes": sum(a.nbytes for a in arrays.values()),
            "cubic_original_coefficient_bytes": sum(
                arrays[k].nbytes for k in ("response", "forcing", "reduced")
            ),
            "cubic_original_sparse_index_bytes": arrays["input_triples"].nbytes
            + arrays["output_waves"].nbytes,
            "prepared_cubic_buffers": prepared_storage,
            "resident_numpy_buffers": buffer_inventory(evaluator, arrays),
            "memory_scope": "NumPy buffer bytes only; preparation copies, original fibers, and serialized bytes are separated; Python overhead, quadratic/base fields, transient FFT and full-map fields are not a claimed total RSS",
        },
    )


def relative(actual, reference):
    return float(np.linalg.norm(actual - reference) / max(1e-14, np.linalg.norm(reference)))


def scaled(actual, reference):
    return float(np.linalg.norm(actual - reference) / max(1.0, np.linalg.norm(reference)))


def hashes(**arrays):
    return {name: quadratic.array_metadata(value) for name, value in arrays.items()}


def evaluation_controls(model, arrays, progress=None):
    q = model.quadratic
    directions = quadratic.normalized_directions(chart.EVALUATION_SEED, 8)
    records = []
    for index, a in enumerate(directions):
        actual_h = model.cubic_fourier(a)
        reference_h, reference_g = chart.direct_cubic_sum(arrays, a, q.size)
        actual_g, g_real = model.reduced_cubic_with_audit(a)
        manual_g, manual_real = chart.manual_real_coordinates(reference_g)
        pair_h, _, pair_g = q.pair_loop(a)
        fiber_h, fiber_g = q.quadratic_fourier(a), q.reduced_quadratic_fourier(a)
        dense_g = 0.5 * np.einsum("ijk,j,k->i", q.reduced_hessian, a, a)
        errors = {
            "cubic_H3_direct_sum": relative(actual_h, reference_h),
            "cubic_G3_manual_realification": relative(actual_g, manual_g),
            "paired_H2_loop": relative(fiber_h, pair_h),
            "paired_G2_loop": relative(fiber_g, pair_g),
            "paired_G2_real_hessian": relative(q.transform.conj().T @ fiber_g, dense_g),
        }
        row = {
            "direction_index": index,
            "errors": errors,
            "realification": {"grouped": g_real, "manual": manual_real},
            "fields": hashes(
                actual_h=actual_h,
                reference_h=reference_h,
                actual_g=actual_g,
                reference_complex_g=reference_g,
                manual_g=manual_g,
                pair_h=pair_h,
                fiber_h=fiber_h,
                pair_g=pair_g,
                fiber_g=fiber_g,
                dense_g=dense_g,
            ),
            "passed": max(errors.values()) <= 1e-10,
        }
        records.append(row)
        if progress:
            progress(
                {
                    "phase": "independent_evaluation",
                    "size": q.size,
                    "direction": index,
                    "passed": row["passed"],
                }
            )
    return {
        "seed": chart.EVALUATION_SEED,
        "directions": directions.tolist(),
        "records": records,
        "passed": len(records) == 8 and all(r["passed"] for r in records),
    }


def buffer_inventory(model, arrays):
    """Unique owning NumPy buffers, with no claim to include Python/process overhead."""
    roots, seen = {}, set()

    def visit(value, skip=None):
        if id(value) in seen or value is skip:
            return
        seen.add(id(value))
        if isinstance(value, np.ndarray):
            root = value
            while isinstance(root.base, np.ndarray):
                root = root.base
            roots[id(root)] = root
        elif isinstance(value, dict):
            for item in value.values():
                visit(item, skip)
        elif isinstance(value, (tuple, list)):
            for item in value:
                visit(item, skip)
        elif is_dataclass(value) or isinstance(value, (chart.CubicChart, chart.GroupedPolynomial)):
            visit(vars(value), skip)

    groups = {}
    for name, value in (
        ("quadratic_including_base_and_caches", model.quadratic),
        ("cubic_prepared", model),
        ("original_cubic_archives", arrays),
    ):
        old = set(roots)
        visit(value)
        added = [v for key, v in roots.items() if key not in old]
        groups[name] = {
            "unique_buffers_added": len(added),
            "bytes_added": sum(v.nbytes for v in added),
        }
    return {
        "groups": groups,
        "unique_buffers": len(roots),
        "bytes": sum(v.nbytes for v in roots.values()),
        "scope": "deduplicated owning NumPy buffers reachable from prepared models and original fibers; includes quadratic base/caches, excludes Python objects, transient evaluation/FFT/full-map arrays, and allocator overhead",
    }


def homogeneity_controls(model):
    generic = quadratic.normalized_directions(chart.EVALUATION_SEED, 8)
    directions = np.vstack((generic, np.eye(104)))
    records = []
    for index, a in enumerate(directions):
        z = model.quadratic.complex_coordinates(a)
        values, errors = {}, {}
        for name, engine in (("H3", model.response), ("G3", model.internal)):
            # Orthonormal FFT preserves this norm; no physical field is needed for homogeneity.
            reference, negative, doubled = (engine.evaluate(scale * z) for scale in (1, -1, 2))
            errors[name + "_odd"] = scaled(negative, -reference)
            errors[name + "_cubic"] = scaled(doubled, 8 * reference)
            values[name] = hashes(reference=reference, negative=negative, doubled=doubled)
        records.append(
            {
                "kind": "generic" if index < 8 else "coordinate_axis",
                "direction_index": index if index < 8 else index - 8,
                "errors": errors,
                "fields": values,
                "passed": max(errors.values()) <= 1e-12,
            }
        )
    return {
        "seed": chart.EVALUATION_SEED,
        "generic_directions": generic.tolist(),
        "records": records,
        "representation": "complex Fourier output fibers for H3, conjugate internal slots for G3; no averaging",
        "passed": len(records) == 112 and all(r["passed"] for r in records),
    }


def structural_physical_controls(model, progress=None):
    q = model.quadratic
    directions = quadratic.normalized_directions(chart.EVALUATION_SEED, 8)
    records = []
    for index, a in enumerate(directions):
        h, realness = model.cubic_field_with_audit(a)
        g, reduced_realness = model.reduced_cubic_with_audit(a)
        gauge = q.project(h)
        moments = d3.global_conserved_quantities(h)
        scale = max(1.0, np.linalg.norm(h))
        structural = {
            "graph_gauge": float(np.linalg.norm(gauge) / scale),
            "zero_wave_conserved_moment": float(np.linalg.norm(moments) / q.size**1.5 / scale),
        }
        forcing_spectrum = model.cubic_fourier(a, forcing=True)
        contracted = np.fft.ifftn(forcing_spectrum, axes=(0, 1, 2), norm="ortho")
        del forcing_spectrum
        direct = cubic.direct_physical_forcing(q, a)  # Includes -DH2(Lambda a) G2(a).
        forcing_error = relative(contracted, direct)
        identity = physical.linear_step(q, h) - model.cubic_field(q.real_linear @ a)
        identity += direct - q.linear_field(g)
        identity_error = float(np.linalg.norm(identity) / max(1e-14, np.linalg.norm(direct)))
        row = {
            "direction_index": index,
            "structural_errors": structural,
            "realification": {"H3": realness, "G3": reduced_realness},
            "global_H3_conserved_sums": moments.tolist(),
            "zero_wave_H3_conserved_moments": (moments / q.size**1.5).tolist(),
            "forcing_relative_error": forcing_error,
            "physical_homological_relative_error": identity_error,
            "fields": hashes(
                h=h,
                g=g,
                gauge=gauge,
                contracted_forcing=contracted,
                direct_forcing=direct,
                homological_defect=identity,
            ),
            "structure_passed": max(structural.values()) <= 1e-9
            and realness["passed"]
            and reduced_realness["passed"],
            "physics_passed": forcing_error <= 1e-8 and identity_error <= 1e-9,
        }
        records.append(row)
        if progress:
            progress(
                {
                    "phase": "physical_cubic_identity",
                    "size": q.size,
                    "direction": index,
                    "structure_passed": row["structure_passed"],
                    "physics_passed": row["physics_passed"],
                }
            )
    return {
        "seed": chart.EVALUATION_SEED,
        "directions": directions.tolist(),
        "records": records,
        "structure_passed": len(records) == 8 and all(r["structure_passed"] for r in records),
        "physics_passed": len(records) == 8 and all(r["physics_passed"] for r in records),
    }


def symmetry_controls(model, progress=None):
    q = model.quadratic
    directions = quadratic.normalized_directions(SYMMETRY_SEED, 4)
    rotations = d3.cubic_symmetries()
    records = []
    # Keep only ONE reference physical field, not all four 65^3 states.
    for index, a in enumerate(directions):
        h, g = model.cubic_field(a), model.reduced_cubic(a)
        for rotation_index, rotation in enumerate(rotations):
            action = q.rotation_action(rotation)
            transformed = action @ a
            actual_h, real_h = model.cubic_field_with_audit(transformed)
            actual_g, real_g = model.reduced_cubic_with_audit(transformed)
            reference_h = d3.rotate_periodic_state(h, rotation)
            reference_g = action @ g
            errors = {"H3": relative(actual_h, reference_h), "G3": relative(actual_g, reference_g)}
            records.append(
                {
                    "direction_index": index,
                    "rotation_index": rotation_index,
                    "rotation": rotation.tolist(),
                    "errors": errors,
                    "realification": {"H3": real_h, "G3": real_g},
                    "fields": hashes(
                        actual_h=actual_h,
                        reference_h=reference_h,
                        actual_g=actual_g,
                        reference_g=reference_g,
                    ),
                    "passed": max(errors.values()) <= 1e-8,
                }
            )
            del actual_h, reference_h
        if progress:
            progress(
                {
                    "phase": "cubic_symmetry",
                    "size": q.size,
                    "direction": index,
                    "rotations": len(rotations),
                }
            )
    return {
        "seed": SYMMETRY_SEED,
        "directions": directions.tolist(),
        "records": records,
        "passed": len(records) == 192 and all(r["passed"] for r in records),
    }


def case_specifications(*, worker=False):
    for kind, seed, count, amplitudes in (
        ("order", ORDER_SEED, 64, AMPLITUDES),
        ("amplitude", AMPLITUDE_SEED, 32, HOLDOUT_AMPLITUDES),
    ):
        directions = quadratic.normalized_directions(seed, count)
        for index, direction in enumerate(directions[:8] if worker else directions):
            for amplitude in amplitudes:
                yield {
                    "kind": kind,
                    "direction_index": index,
                    "amplitude": amplitude,
                    "a": (amplitude * direction).tolist(),
                }
    if not worker:
        for wave in ((1, 0, 0), (1, 1, 0), (1, 1, 1)):
            representative = quadratic.POSITIVE_WAVES.index(wave)
            for component in range(8):
                direction = np.eye(104)[8 * representative + component]
                for amplitude in AMPLITUDES:
                    yield {
                        "kind": "special",
                        "wave": list(wave),
                        "real_component": component,
                        "amplitude": amplitude,
                        "a": (amplitude * direction).tolist(),
                    }


def field_metrics(field, base):
    if field.shape != base.shape or not np.all(np.isfinite(field)):
        raise ValueError("nonfinite or wrongly shaped full-map evidence")
    density = np.sum(field, axis=-1)
    return {
        "array": quadratic.array_metadata(field),
        "norm": float(np.linalg.norm(field)),
        "perturbation_norm": float(np.linalg.norm(field - base)),
        "maximum_local_density_deviation": float(np.max(np.abs(density - 1))),
        "minimum_population": float(np.min(field)),
        "global_conserved_sums": d3.global_conserved_quantities(field).tolist(),
        "finite": True,
    }


def one_model_case(model, a, degree):
    q = model.quadratic
    r, reduced_real = model.reduced_with_audit(a, degree=degree)
    w, w_real = model.embed_with_audit(a, degree=degree)
    advanced = physical.map_step(q, w)
    composed, composed_real = model.embed_with_audit(r, degree=degree)
    fields = {
        "W": field_metrics(w, q.base),
        "Phi_W": field_metrics(advanced, q.base),
        "W_R": field_metrics(composed, q.base),
    }
    defect = advanced - composed
    defect_norm = float(np.linalg.norm(defect))
    base_sums = d3.global_conserved_quantities(q.base)
    global_errors = {
        "W_leaf": np.asarray(fields["W"]["global_conserved_sums"]) - base_sums,
        "W_R_leaf": np.asarray(fields["W_R"]["global_conserved_sums"]) - base_sums,
        "Phi_conservation": np.asarray(fields["Phi_W"]["global_conserved_sums"])
        - fields["W"]["global_conserved_sums"],
    }
    mean_errors = {k: v / q.size**3 for k, v in global_errors.items()}
    return {
        "status": "computed",
        "degree": degree,
        "defect_norm": defect_norm,
        "defect_array": quadratic.array_metadata(defect),
        "reduced_coordinates": r.tolist(),
        "realification": {"W": w_real, "W_R": composed_real, "R": reduced_real},
        "fields": fields,
        "global_conservation_errors": {k: v.tolist() for k, v in global_errors.items()},
        "site_average_conservation_errors": {k: v.tolist() for k, v in mean_errors.items()},
        "maximum_site_average_conservation_error": max(
            float(np.max(np.abs(v))) for v in mean_errors.values()
        ),
        "positive": all(v["minimum_population"] > 0 for v in fields.values()),
    }


def physical_case(model, specification):
    a = np.asarray(specification["a"], dtype=float)
    results = {}
    for degree in (2, 3):
        try:
            row = one_model_case(model, a, degree)
            if not _all_numeric_values_finite(row):
                raise ValueError("nonfinite numeric case evidence")
            results[str(degree)] = row
        except ERRORS as exc:
            results[str(degree)] = {
                "status": "error",
                "degree": degree,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
    finite = all(r["status"] == "computed" for r in results.values())
    floor = float(100 * np.finfo(float).eps * max(1, np.linalg.norm(model.quadratic.base)))
    resolved = finite and all(r["defect_norm"] > floor for r in results.values())
    ratio = results["3"]["defect_norm"] / results["2"]["defect_norm"] if resolved else None
    return {
        **specification,
        "models": results,
        "finite": finite,
        "roundoff_floor": floor,
        "resolved": resolved,
        "cubic_to_quadratic_defect_ratio": ratio,
        "amplitude_passed": bool(
            resolved
            and ratio <= 0.5
            and all(
                r["positive"] and r["maximum_site_average_conservation_error"] <= 5e-13
                for r in results.values()
            )
        )
        if specification["kind"] == "amplitude"
        else None,
    }


def fits(records, *, special=False):
    keys = (
        [(list(w), component) for w in ((1, 0, 0), (1, 1, 0), (1, 1, 1)) for component in range(8)]
        if special
        else list(range(64))
    )
    result = []
    for key in keys:
        rows = [
            r
            for r in records
            if (
                r["kind"] == "special" and r["wave"] == key[0] and r["real_component"] == key[1]
                if special
                else r["kind"] == "order" and r["direction_index"] == key
            )
        ]
        complete = len(rows) == 4 and tuple(r["amplitude"] for r in rows) == AMPLITUDES
        resolved = complete and all(r["resolved"] for r in rows)
        slopes = {
            str(d): float(
                np.polyfit(
                    np.log(AMPLITUDES),
                    np.log([r["models"][str(d)]["defect_norm"] for r in rows]),
                    1,
                )[0]
            )
            if resolved
            else None
            for d in (2, 3)
        }
        ratio = rows[-1]["cubic_to_quadratic_defect_ratio"] if resolved else None
        passed = bool(
            resolved and 2.9 <= slopes["2"] <= 3.1 and 3.9 <= slopes["3"] <= 4.1 and ratio <= 0.1
        )
        result.append(
            {
                "direction_key": list(key) if special else key,
                "complete": complete,
                "resolved": resolved,
                "slopes": slopes,
                "smallest_amplitude_ratio": ratio,
                "passed": passed if not special else None,
                "scope": "diagnostic only" if special else "registered generic gate",
            }
        )
    return result


def timed_call(model, method, a, phi_input):
    if method in ("W2", "W3"):
        return model.embed(a, degree=int(method[-1]))
    if method in ("R2", "R3"):
        return model.reduced(a, degree=int(method[-1]))
    if method == "Phi_W3":
        return physical.map_step(model.quadratic, phi_input)
    raise ValueError("unregistered timing method")


def timing_study(model, progress=None):
    directions = quadratic.normalized_directions(COST_SEED, 8)
    coordinates = 0.008 * directions
    warmups, records, references = [], [], {}
    for repetition in range(3):
        a = coordinates[repetition]
        phi_input = model.embed(a)
        for method in METHODS:
            value = timed_call(model, method, a, phi_input)
            warmups.append(
                {
                    "repetition": repetition,
                    "method": method,
                    "output": quadratic.array_metadata(value),
                }
            )
            if not np.all(np.isfinite(value)):
                raise ValueError("nonfinite timing warmup")
            del value
        del phi_input
    for repetition in range(11):
        order = METHODS if repetition % 2 == 0 else METHODS[::-1]
        for index, a in enumerate(coordinates):
            # Preparation excluded from Phi timing; never retain all eight physical inputs.
            phi_input = model.embed(a)
            for method in order:
                start = perf_counter()
                value = timed_call(model, method, a, phi_input)
                elapsed = perf_counter() - start
                output = quadratic.array_metadata(value)  # Hash, norm, checks OUTSIDE timed call.
                value_norm = float(np.linalg.norm(value))
                finite = bool(np.all(np.isfinite(value))) and np.isfinite(value_norm)
                key = method, index
                if key not in references:
                    references[key] = output
                records.append(
                    {
                        "repetition": repetition,
                        "direction_index": index,
                        "method": method,
                        "wall_seconds": elapsed,
                        "output": output,
                        "output_norm": value_norm,
                        "finite": bool(finite),
                        "same_output": references[key] == output,
                    }
                )
                del value
            del phi_input
        if progress:
            progress(
                {
                    "phase": "separated_cost",
                    "size": model.quadratic.size,
                    "round": repetition + 1,
                    "total": 11,
                }
            )
    return {
        "seed": COST_SEED,
        "directions": directions.tolist(),
        "amplitude": 0.008,
        "warmups": warmups,
        "records": records,
        "median_wall_seconds": {
            method: float(np.median([r["wall_seconds"] for r in records if r["method"] == method]))
            for method in METHODS
        },
        "valid": len(warmups) == 15
        and len(records) == 440
        and all(r["finite"] and r["same_output"] for r in records),
        "scope": "descriptive natural Fourier-sparse costs; no timing threshold, TT comparison, or speedup gate",
    }


def guarded(call):
    try:
        result = call()
        if not _all_numeric_values_finite(result):
            raise ValueError("nonfinite saved evidence")
        return {"status": "computed", **result}
    except ERRORS as exc:
        details = {}
        traceback = exc.__traceback__
        phases = {
            "evaluation_controls",
            "homogeneity_controls",
            "structural_physical_controls",
            "symmetry_controls",
            "timing_study",
        }
        while traceback is not None:
            frame = traceback.tb_frame
            if frame.f_code.co_name in phases:
                local = frame.f_locals
                partial = local.get("records", [])
                partial_finite = _all_numeric_values_finite(partial)
                details = {
                    "phase": frame.f_code.co_name,
                    "failed_context": {
                        key: int(local[key])
                        for key in ("index", "rotation_index", "repetition")
                        if key in local and isinstance(local[key], (int, np.integer))
                    },
                    "partial_records": partial if partial_finite else None,
                    "partial_records_finite": partial_finite,
                    "partial_scope": "completed rows before an exception; never full-coverage success",
                }
            traceback = traceback.tb_next
        return {"status": "error", "error_type": type(exc).__name__, "error": str(exc), **details}


def grid_campaign(size, *, worker, progress=None):
    model, arrays, inputs, offline = fresh_model(size)
    result = {"size": size, **inputs, "offline_cost": offline}
    if not worker:
        result["evaluation"] = guarded(
            lambda arrays=arrays: evaluation_controls(model, arrays, progress)
        )
        result["homogeneity"] = guarded(lambda: homogeneity_controls(model))
        result["physical_structure"] = guarded(
            lambda: structural_physical_controls(model, progress)
        )
        result["symmetry"] = guarded(lambda: symmetry_controls(model, progress))
    del arrays
    gc.collect()
    rows = []
    for index, specification in enumerate(case_specifications(worker=worker)):
        row = physical_case(model, specification)
        rows.append(row)
        if progress:
            progress(
                {
                    "phase": "worker_case" if worker else "full_map_case",
                    "size": size,
                    "case": index + 1,
                    "kind": row["kind"],
                    "finite": row["finite"],
                    "resolved": row["resolved"],
                }
            )
    result["records"] = rows
    if not worker:
        result["generic_fits"] = fits(rows)
        result["special_fits"] = fits(rows, special=True)
        result["timing"] = guarded(lambda: timing_study(model, progress))
    return result


def grid_path(output, size):
    return output.with_name(output.stem + f"_n{size}.json")


def record_specification(row):
    return {
        k: v
        for k, v in row.items()
        if k in ("kind", "direction_index", "wave", "real_component", "amplitude", "a")
    }


def coverage(grid, *, worker):
    rows = grid.get("records", [])
    return [record_specification(r) for r in rows] == list(case_specifications(worker=worker))


def diagnostic_coverage(grid):
    """Check actual ordered witnesses, not their self-reported pass/count fields."""
    expected_directions = quadratic.normalized_directions(chart.EVALUATION_SEED, 8).tolist()
    for name in ("evaluation", "physical_structure"):
        data = grid.get(name, {})
        if (
            data.get("seed") != chart.EVALUATION_SEED
            or data.get("directions") != expected_directions
            or [r.get("direction_index") for r in data.get("records", [])] != list(range(8))
        ):
            return False
    homogeneity = grid.get("homogeneity", {})
    if (
        homogeneity.get("seed") != chart.EVALUATION_SEED
        or homogeneity.get("generic_directions") != expected_directions
        or [(r.get("kind"), r.get("direction_index")) for r in homogeneity.get("records", [])]
        != [("generic", i) for i in range(8)] + [("coordinate_axis", i) for i in range(104)]
    ):
        return False
    symmetry = grid.get("symmetry", {})
    if (
        symmetry.get("seed") != SYMMETRY_SEED
        or symmetry.get("directions") != quadratic.normalized_directions(SYMMETRY_SEED, 4).tolist()
        or [
            (r.get("direction_index"), r.get("rotation_index"), r.get("rotation"))
            for r in symmetry.get("records", [])
        ]
        != [
            (i, j, rotation.tolist())
            for i in range(4)
            for j, rotation in enumerate(d3.cubic_symmetries())
        ]
    ):
        return False
    timing = grid.get("timing", {})
    return (
        timing.get("seed") == COST_SEED
        and timing.get("amplitude") == 0.008
        and timing.get("directions") == quadratic.normalized_directions(COST_SEED, 8).tolist()
        and [(r.get("repetition"), r.get("method")) for r in timing.get("warmups", [])]
        == [(r, method) for r in range(3) for method in METHODS]
        and [
            (r.get("repetition"), r.get("direction_index"), r.get("method"))
            for r in timing.get("records", [])
        ]
        == [
            (r, i, method)
            for r in range(11)
            for i in range(8)
            for method in (METHODS if r % 2 == 0 else METHODS[::-1])
        ]
    )


def scientific_worker_grid(grid):
    # Exclude measured cost and process metadata, not any scientific numeric value.
    return {k: grid[k] for k in ("size", "input_rebuild", "fiber_load", "records")}


def replay_audit(path, inputs, controls, grids, current):
    saved = prior.read_json(path)
    actual = saved["evidence"]
    expected_grids = []
    for grid in grids:
        rows = [
            r
            for r in grid.get("records", [])
            if r["kind"] in ("order", "amplitude") and r["direction_index"] < 8
        ]
        expected_grids.append(
            {
                "size": grid["size"],
                "input_rebuild": grid.get("input_rebuild"),
                "fiber_load": grid.get("fiber_load"),
                "records": rows,
            }
        )
    expected = {"input_audit": inputs, "controls": controls, "grids": expected_grids}
    checks = {
        "kind": saved["kind"] == "Q012g independent 144-case full-map worker",
        "separate_process": saved["process_id"] != current["process_id"],
        "unchanged_sources": source_equal(saved, current) and saved["source_unchanged_after"],
        "evidence_digest": foundation._digest(actual) == saved["evidence_digest_sha256"],
        "complete_144_cases": [g["size"] for g in actual["grids"]] == list(cubic.SIZES)
        and all(coverage(g, worker=True) for g in actual["grids"]),
        "all_registered_values_and_field_hashes": actual == expected,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "checks": checks,
        "worker_process_id": saved["process_id"],
        "passed": all(checks.values()),
        "scope": "fresh full quadratic inputs; first 8 order and 8 holdout directions per grid, 144 cases, both degrees; not full-case or cubic-solver replay",
    }


def decision(inputs, controls, grids, replay, source_unchanged):
    complete = [g.get("size") for g in grids] == list(cubic.SIZES) and all(
        coverage(g, worker=False) for g in grids
    )
    control_names = ("evaluation", "homogeneity", "physical_structure", "symmetry", "timing")
    validity = {
        "sealed_preflight_inputs": inputs["passed"],
        "manufactured_and_retained_solver_controls": controls["passed"],
        "source_unchanged_after": source_unchanged,
        "full_registered_three_grid_case_coverage": complete,
        "fresh_paired_inputs": complete
        and all(g["input_rebuild"]["passed"] and g["fiber_load"]["passed"] for g in grids),
        "all_diagnostic_phases_computed": complete
        and all(g.get(k, {}).get("status") == "computed" for g in grids for k in control_names),
        "full_registered_diagnostic_coverage": complete
        and all(diagnostic_coverage(g) for g in grids),
        "saved_order_summaries_match_cases": complete
        and all(
            g.get("generic_fits") == fits(g["records"])
            and g.get("special_fits") == fits(g["records"], special=True)
            for g in grids
        ),
        "finite_full_map_evidence": complete
        and all(r["finite"] for g in grids for r in g["records"])
        and _all_numeric_values_finite(grids),
        "complete_separated_timing_measurements": complete
        and all(g.get("timing", {}).get("valid", False) for g in grids),
        "independent_144_case_replay": replay.get("passed", False),
        "grid_evidence_roundtrip": complete
        and all(g.get("roundtrip_passed", False) for g in grids),
    }
    ready = complete and validity["all_diagnostic_phases_computed"]
    hypotheses = {
        "H1_real_sparse_evaluation_and_fixed_leaf_structure": ready
        and all(
            g["evaluation"]["passed"]
            and g["homogeneity"]["passed"]
            and g["physical_structure"]["structure_passed"]
            for g in grids
        ),
        "H2_all_48_cubic_symmetries": ready and all(g["symmetry"]["passed"] for g in grids),
        "H3_independent_physical_cubic_identity": ready
        and all(g["physical_structure"]["physics_passed"] for g in grids),
        "H4_order_three_to_four": complete
        and all(
            len(g.get("generic_fits", [])) == 64 and all(r["passed"] for r in g["generic_fits"])
            for g in grids
        ),
        "H5_finite_holdout_improvement_positive_and_conserved": complete
        and all(
            r["amplitude_passed"] for g in grids for r in g["records"] if r["kind"] == "amplitude"
        ),
    }
    resolved = complete and all(
        r["resolved"] for g in grids for r in g["records"] if r["kind"] in ("order", "amplitude")
    )
    outcome = physical.classify(validity, hypotheses, bool(resolved))
    return validity, hypotheses, bool(resolved), outcome


def controls():
    results = {
        "manufactured_graph_evaluation": chart.manufactured_controls(),
        "retained_homological_controls": prior.controls(),
    }
    return {"results": results, "passed": all(r["passed"] for r in results.values())}


def write_grid(path, grid, current):
    # Read back the FULL saved numerical grid evidence, not only its summary flags.
    document = {
        **current,
        "kind": "Q012g grid evidence",
        "grid": grid,
        "grid_digest_sha256": foundation._digest(grid),
    }
    prior.previous.write_json(path, document)
    restored = prior.read_json(path)
    passed = (
        restored == document
        and foundation._digest(restored["grid"]) == restored["grid_digest_sha256"]
    )
    return {"filename": path.name, "sha256": _file_sha256(path), "roundtrip_passed": passed}


def worker_readiness(saved, current, inputs, control):
    evidence = saved.get("evidence", {})
    grids = evidence.get("grids", [])
    return (
        saved.get("kind") == "Q012g independent 144-case full-map worker"
        and source_equal(saved, current)
        and saved.get("source_unchanged_after", False)
        and saved.get("process_id") != current["process_id"]
        and foundation._digest(evidence) == saved.get("evidence_digest_sha256")
        and evidence.get("input_audit") == inputs
        and evidence.get("controls") == control
        and [g.get("size") for g in grids] == list(cubic.SIZES)
        and all(coverage(g, worker=True) for g in grids)
        and _all_numeric_values_finite(evidence)
    )


def run(output, *, worker, replay_path=None, progress=None):
    current, inputs, control = metadata(), input_audit(), controls()
    if not inputs["passed"] or not control["passed"]:
        raise ValueError("sealed inputs or manufactured controls failed before the campaign")
    if not worker:
        witness = prior.read_json(replay_path)
        if not worker_readiness(witness, current, inputs, control):
            raise ValueError(
                "a complete sealed 144-case worker is required before the main campaign"
            )
    grids, files = [], []
    for size in cubic.SIZES:
        if progress:
            progress({"phase": "fresh_grid", "size": size, "worker": worker})
        try:
            grid = grid_campaign(size, worker=worker, progress=progress)
        except ERRORS as exc:
            grid = {
                "size": size,
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        saved = write_grid(grid_path(output, size), grid, current)
        grid["roundtrip_passed"] = saved["roundtrip_passed"]
        grids.append(grid)
        files.append(saved)
        gc.collect()
    unchanged = source_equal(current, metadata())
    if worker:
        if not all(coverage(g, worker=True) and g["roundtrip_passed"] for g in grids):
            # Preserve failed grid evidence but never fabricate missing worker rows.
            return {
                **current,
                "kind": "Q012g incomplete worker",
                "grids": grids,
                "grid_artifacts": files,
                "source_unchanged_after": unchanged,
            }
        evidence = {
            "input_audit": inputs,
            "controls": control,
            "grids": [scientific_worker_grid(g) for g in grids],
        }
        return {
            **current,
            "kind": "Q012g independent 144-case full-map worker",
            "evidence": evidence,
            "evidence_digest_sha256": foundation._digest(evidence),
            "grid_artifacts": files,
            "source_unchanged_after": unchanged,
        }
    replay = guarded(lambda: replay_audit(replay_path, inputs, control, grids, current))
    validity, hypotheses, resolved, outcome = decision(inputs, control, grids, replay, unchanged)
    cycle = {
        "protocol": "Q012g fixed real cubic evaluation and full-map finite-amplitude validation",
        "configuration": {
            "sizes": list(cubic.SIZES),
            "omega": 1.5,
            "eta": 0.02,
            "power": 2,
            "real_coordinates": 104,
            "order_seed": ORDER_SEED,
            "amplitude_seed": AMPLITUDE_SEED,
            "symmetry_seed": SYMMETRY_SEED,
            "cost_seed": COST_SEED,
            "amplitudes": list(AMPLITUDES),
            "holdout_amplitudes": list(HOLDOUT_AMPLITUDES),
        },
        "input_audit": inputs,
        "controls": control,
        "grids": grids,
        "grid_artifacts": files,
        "independent_replay": replay,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "generic_and_holdout_resolved": resolved,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "registered finite samples of the modified D3Q27 map and full cubic jet; own-chart 1-step defects, not common-initial trajectories, SSM existence, a continuous-ball or grid-uniform radius, or TT advantage",
    }
    cycle["result_digest_sha256"] = foundation._digest(cycle)
    return {
        **current,
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--worker-output", type=Path)
    targets.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    output = args.worker_output or args.output
    if (args.output is not None) != (args.replay is not None):
        parser.error("--output requires --replay; --worker-output does not use --replay")
    if any(p.exists() for p in [output, *(grid_path(output, size) for size in cubic.SIZES)]):
        parser.error("use fresh paths; existing full or partial evidence is never overwritten")
    progress = lambda row: print(json.dumps(row), flush=True)
    result = run(
        output, worker=args.worker_output is not None, replay_path=args.replay, progress=progress
    )
    prior.previous.write_json(output, result)
    if args.output is not None:
        print(
            json.dumps(
                {
                    "study_gate": result["study_gate"],
                    "scientific_outcome": result["scientific_outcome"],
                }
            ),
            flush=True,
        )
        if result["study_gate"] != "passed":
            raise SystemExit(1)
    elif result["kind"] != "Q012g independent 144-case full-map worker":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
