"""Q012d: registered, full-grid tests of the 104-real-coordinate quadratic jet."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import q012a_d3q27_foundation as q012a
from research import q012c1a_d3q27_damping as prior
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012c1a_d3q27_damping.json"
PRIOR_SHA256 = "b254057450e1deaaa2cd2791fa4547455e27a76352c99b5923e5de2a9434ddbe"
PRIOR_RESULT = "f652b5b9d6c0f3fc151d4de6927f36445d518f4cff993cdbbfc5b1a848f6587e"
HELPERS = prior.HELPERS + (("complete_damping_runner", prior), ("chart", chart))
AMPLITUDES = (0.008, 0.004, 0.002, 0.001)
TRAJECTORY_AMPLITUDES = AMPLITUDES[:3]
FD_STEPS = (0.01, 0.005, 0.0025)
TRAJECTORY_STEPS = 64


def input_audit() -> dict:
    artifact = json.loads(PRIOR_PATH.read_text(encoding="utf-8"))
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    configuration = {"power": chart.POWER, "eta": chart.ETA, "omega": chart.OMEGA}
    selected = cycle["selected_family"]
    checks = {
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA256,
        "result_digest": q012a._digest(cycle) == digest == PRIOR_RESULT,
        "package_source": artifact["source"] == source_metadata(),
        "runner_seal": _file_sha256(Path(prior.__file__)) == artifact["runner_source"]["sha256"],
        "prior_accepted": artifact["study_gate"] == cycle["study_validity"] == "passed"
        and artifact["scientific_outcome"] == cycle["scientific_outcome"] == "accepted",
        "eleven_prior_validity_gates": len(cycle["validity_gates"]) == 11
        and all(cycle["validity_gates"].values()),
        "prior_input_checker": prior.input_audit()["passed"],
        "registered_selected_family": selected is not None
        and all(selected[key] == value for key, value in configuration.items())
        and selected["real_coordinate_count"] == 104
        and selected["leading_viscosity_preserved"]
        and selected["jointly_viable"],
    }
    for name, module in prior.HELPERS:
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
        )
    selected_tables = [
        row
        for row in cycle["conditions"]
        if all(row[key] == value for key, value in configuration.items())
    ]
    checks["selected_three_grids"] = len(selected_tables) == 3 and {
        row["size"] for row in selected_tables
    } == {17, 33, 65}
    replay = cycle["independent_replay"]
    checks["sealed_three_grid_replay"] = (
        replay["passed"]
        and replay["configuration"] == configuration
        and len(replay["records"]) == 3
        and {r["size"] for r in replay["records"]} == {17, 33, 65}
    )
    for row in selected_tables:
        table = row["table"]
        path = PRIOR_PATH.parent / artifact["table_directory"] / table["filename"]
        stored = json.loads(path.read_text(encoding="utf-8"))
        reproduced = [r for r in replay["records"] if r["size"] == row["size"]]
        checks[table["filename"]] = (
            _file_sha256(path) == table["sha256"]
            and q012a._digest(stored["cycle"])
            == stored["result_digest_sha256"]
            == table["result_digest_sha256"]
            and stored["cycle"]["jointly_prequalified"]
            and stored["cycle"]["coefficient_screen"]["pair_count"] == 3081
            and len(reproduced) == 1
            and reproduced[0]["passed"]
            and reproduced[0]["result_digest_sha256"] == table["result_digest_sha256"]
        )
    return {"filename": PRIOR_PATH.name, "checks": checks, "passed": all(checks.values())}


def map_step(model: chart.QuadraticChart, state: np.ndarray) -> np.ndarray:
    return damping.periodic_step(state, model.omega, model.eta, model.power)


def linear_step(model: chart.QuadraticChart, field: np.ndarray) -> np.ndarray:
    return damping.apply_filter(
        d3.linearized_periodic_step(field, model.omega), model.eta, model.power
    )


def construction_gates(construction: dict) -> dict:
    c = construction
    return {
        "all_frames": c["frame_audit"]["passed"],
        "all_coefficient_equations": c["coefficient_passed"],
        "real_linear_coordinates": max(
            c["realification_unitarity_error"], c["real_linear_imaginary_error"]
        )
        <= 5e-12,
        "conjugate_real_symmetric_quadratics": max(
            c["hessian_conjugacy_relative_error"],
            c["forcing_conjugacy_relative_error"],
            c["reduced_conjugacy_relative_error"],
            c["real_hessian_imaginary_relative_error"],
            c["real_hessian_symmetry_error"],
        )
        <= 1e-9,
        "nonzero_reduced_quadratic": c["reduced_hessian_frobenius_norm"] > 1e-6,
        "mean_kinetic_not_conserved_generation": c["zero_wave_kinetic_norm"] > 1e-8
        and c["zero_wave_moment_error"] <= 5e-12,
    }


def evaluation_controls(model: chart.QuadraticChart) -> dict:
    seed = 2026090713
    directions = chart.normalized_directions(seed, 8)
    records = []
    for index, a in enumerate(directions):
        h, b, g = model.pair_loop(a)
        expected_g = 0.5 * np.einsum("ijk,j,k->i", model.reduced_hessian, a, a)
        errors = {
            "pair_hessian_vs_fiber": damping.relative_error(h, model.quadratic_fourier(a)),
            "pair_forcing_vs_fiber": damping.relative_error(
                b, model.quadratic_fourier(a, forcing=True)
            ),
            "pair_reduced_vs_fiber": damping.relative_error(g, model.reduced_quadratic_fourier(a)),
            "complex_vs_real_reduced": damping.relative_error(
                model.transform.conj().T @ g, expected_g
            ),
            "projection_inverse": damping.relative_error(
                model.project(model.embed(a) - model.base), a
            ),
            "quadratic_graph_gauge": float(np.linalg.norm(model.project(model.quadratic_field(a)))),
            "linear_map_intertwining": damping.relative_error(
                linear_step(model, model.linear_field(a)), model.linear_field(model.real_linear @ a)
            ),
        }
        records.append(
            {"direction_index": index, "errors": errors, "passed": max(errors.values()) <= 1e-10}
        )
    return {
        "seed": seed,
        "directions": directions.tolist(),
        "records": records,
        "passed": len(records) == 8 and all(r["passed"] for r in records),
    }


def hessian_controls(model: chart.QuadraticChart) -> dict:
    seed = 2026090714
    directions = chart.normalized_directions(seed, 16).reshape(8, 2, 104)
    records = []
    for index, (u, v) in enumerate(directions):
        left, right = model.linear_field(u), model.linear_field(v)
        exact = damping.apply_filter(
            damping.mixed_hessian(left, right, model.omega), model.eta, model.power
        )
        fourier = model.physical(
            model.quadratic_fourier(u + v, forcing=True)
            - model.quadratic_fourier(u, forcing=True)
            - model.quadratic_fourier(v, forcing=True)
        )
        h = model.quadratic_field(u + v) - model.quadratic_field(u) - model.quadratic_field(v)
        lu, lv = model.real_linear @ u, model.real_linear @ v
        composed_h = (
            model.quadratic_field(lu + lv) - model.quadratic_field(lu) - model.quadratic_field(lv)
        )
        g = np.einsum("ijk,j,k->i", model.reduced_hessian, u, v)
        residual = linear_step(model, h) - composed_h + exact - model.linear_field(g)
        identity_error = float(np.linalg.norm(residual) / max(1e-14, np.linalg.norm(exact)))
        finite_differences = []
        for step in FD_STEPS:
            measured = (
                map_step(model, model.base + step * (left + right))
                - map_step(model, model.base + step * (left - right))
                - map_step(model, model.base + step * (-left + right))
                + map_step(model, model.base - step * (left + right))
            ) / (4 * step**2)
            finite_differences.append(
                {"step": step, "relative_error": damping.relative_error(measured, exact)}
            )
        analytic_error = damping.relative_error(fourier, exact)
        records.append(
            {
                "direction_pair_index": index,
                "analytic_hessian_norm": float(np.linalg.norm(exact)),
                "fourier_vs_physical_relative_error": analytic_error,
                "physical_homological_relative_error": identity_error,
                "finite_differences": finite_differences,
                "passed": analytic_error <= 1e-10
                and identity_error <= 1e-9
                and finite_differences[-1]["relative_error"] <= 1e-5,
            }
        )
    return {
        "seed": seed,
        "direction_pairs": directions.tolist(),
        "records": records,
        "passed": len(records) == 8 and all(r["passed"] for r in records),
    }


def symmetry_controls(model: chart.QuadraticChart) -> dict:
    seed = 2026090715
    directions = chart.normalized_directions(seed, 4)
    originals = [
        (
            model.linear_field(a),
            model.quadratic_field(a),
            model.reduced(a),
            model.reduced(a) - model.real_linear @ a,
        )
        for a in directions
    ]
    records = []
    for rotation_index, rotation in enumerate(d3.cubic_symmetries()):
        action = model.rotation_action(rotation)
        for direction_index, a in enumerate(directions):
            transformed = action @ a
            w1, w2, reduced, g = originals[direction_index]
            errors = {
                "linear_embedding": damping.relative_error(
                    model.linear_field(transformed), d3.rotate_periodic_state(w1, rotation)
                ),
                "quadratic_embedding": damping.relative_error(
                    model.quadratic_field(transformed), d3.rotate_periodic_state(w2, rotation)
                ),
                "reduced_map": damping.relative_error(model.reduced(transformed), action @ reduced),
                "reduced_quadratic": damping.relative_error(
                    model.reduced(transformed) - model.real_linear @ transformed, action @ g
                ),
            }
            records.append(
                {
                    "rotation_index": rotation_index,
                    "rotation": rotation.tolist(),
                    "direction_index": direction_index,
                    "errors": errors,
                    "passed": max(errors.values()) <= 1e-9,
                }
            )
    return {
        "seed": seed,
        "directions": directions.tolist(),
        "records": records,
        "passed": len(records) == 192 and all(r["passed"] for r in records),
    }


def order_record(amplitudes: tuple, defects: list[float], floor: float) -> dict:
    resolved = bool(np.all(np.asarray(defects) > floor))
    # Slopes buried in roundoff are explicitly withheld, not used as evidence.
    slope = float(np.polyfit(np.log(amplitudes), np.log(defects), 1)[0]) if resolved else None
    return {"defects": defects, "above_roundoff_floor": resolved, "slope": slope}


def residual_direction(
    model: chart.QuadraticChart, direction: np.ndarray, *, drop_g: bool = False
) -> dict:
    floor = float(100 * np.finfo(float).eps * max(1, np.linalg.norm(model.base)))
    linear, quadratic, omitted = [], [], []
    for amplitude in AMPLITUDES:
        a = amplitude * direction
        la, ra = model.reduced(a, quadratic=False), model.reduced(a)
        f1, f2 = model.embed(a, quadratic=False), model.embed(a)
        advanced2 = map_step(model, f2)
        linear.append(float(np.linalg.norm(map_step(model, f1) - model.embed(la, quadratic=False))))
        quadratic.append(float(np.linalg.norm(advanced2 - model.embed(ra))))
        if drop_g:
            omitted.append(float(np.linalg.norm(advanced2 - model.embed(la))))
    first, second = (
        order_record(AMPLITUDES, linear, floor),
        order_record(AMPLITUDES, quadratic, floor),
    )
    ratio = quadratic[-1] / max(1e-300, linear[-1])
    resolved = first["above_roundoff_floor"] and second["above_roundoff_floor"]
    result = {
        "linear": first,
        "quadratic": second,
        "smallest_amplitude_ratio": ratio,
        "roundoff_floor": floor,
        "resolved": resolved,
        "passed": resolved
        and 1.9 <= first["slope"] <= 2.1
        and 2.9 <= second["slope"] <= 3.1
        and ratio <= 0.1,
    }
    if drop_g:
        control = order_record(AMPLITUDES, omitted, floor)
        control["passed"] = control["above_roundoff_floor"] and 1.9 <= control["slope"] <= 2.1
        result["omitted_reduced_quadratic"] = control
    return result


def residual_campaign(model: chart.QuadraticChart, progress: Callable | None = None) -> dict:
    seed = 2026090711
    directions = chart.normalized_directions(seed, 64)
    records = []
    for index, direction in enumerate(directions):
        record = {
            "direction_index": index,
            **residual_direction(model, direction, drop_g=index < 8),
        }
        records.append(record)
        if progress is not None and (index + 1) % 16 == 0:
            progress(
                {
                    "phase": "residual_orders",
                    "completed": index + 1,
                    "total": 64,
                    "passed_so_far": all(r["passed"] for r in records),
                }
            )
    special = []
    for wave in ((1, 0, 0), (1, 1, 0), (1, 1, 1)):
        representative = chart.POSITIVE_WAVES.index(wave)
        for component in range(8):
            direction = np.eye(104)[8 * representative + component]
            special.append(
                {
                    "wave": list(wave),
                    "real_component": component,
                    **residual_direction(model, direction),
                }
            )
    return {
        "seed": seed,
        "directions": directions.tolist(),
        "amplitudes": list(AMPLITUDES),
        "generic_records": records,
        "special_records": special,
        "special_scope": "24 pure-mode diagnostics only; unresolved slopes are not order evidence",
        "coverage_passed": len(records) == 64 and len(special) == 24,
        "generic_orders_resolved": all(r["resolved"] for r in records),
        "generic_orders_passed": all(r["passed"] for r in records),
        "nonzero_reduced_negative_control_passed": all(
            r["omitted_reduced_quadratic"]["passed"] for r in records[:8]
        ),
    }


def trajectory_case(model: chart.QuadraticChart, a0: np.ndarray) -> dict:
    modes = {}
    for name, quadratic in (("linear", False), ("quadratic", True)):
        a = a0.copy()
        reconstructed = model.embed(a, quadratic=quadratic)
        state = reconstructed.copy()
        initial_moments = d3.global_conserved_quantities(state)
        base_moments = d3.global_conserved_quantities(model.base)
        errors, full_minimum, chart_minimum, full_drift, chart_drift = [], [], [], [], []
        finite = True
        for step in range(TRAJECTORY_STEPS + 1):
            if step:
                state = map_step(model, state)
                a = model.reduced(a, quadratic=quadratic)
                reconstructed = model.embed(a, quadratic=quadratic)
            finite = (
                finite
                and bool(np.all(np.isfinite(state)))
                and bool(np.all(np.isfinite(reconstructed)))
            )
            errors.append(float(np.linalg.norm(state - reconstructed)))
            full_minimum.append(float(state.min()))
            chart_minimum.append(float(reconstructed.min()))
            full_drift.append((d3.global_conserved_quantities(state) - initial_moments).tolist())
            chart_drift.append(
                (d3.global_conserved_quantities(reconstructed) - initial_moments).tolist()
            )
        global_drift = float(np.max(np.abs((full_drift, chart_drift))))
        mean_drift = global_drift / model.size**3
        initial_leaf_error = float(np.max(np.abs(initial_moments - base_moments)) / model.size**3)
        modes[name] = {
            "state_error_by_step": errors,
            "full_minimum_population_by_step": full_minimum,
            "chart_minimum_population_by_step": chart_minimum,
            "full_global_conservation_drift_by_step": full_drift,
            "chart_global_conservation_drift_by_step": chart_drift,
            "initial_global_conserved_quantities": initial_moments.tolist(),
            "initial_site_average_leaf_error": initial_leaf_error,
            "maximum_state_error": max(errors),
            "final_state_error": errors[-1],
            "maximum_global_conservation_drift": global_drift,
            "maximum_site_average_conservation_drift": mean_drift,
            "finite": finite,
            "positive": min(full_minimum + chart_minimum) > 0,
            "conservation_passed": mean_drift <= 5e-13 and initial_leaf_error <= 5e-13,
        }
    ratios = {
        key: modes["quadratic"][key] / max(1e-300, modes["linear"][key])
        for key in ("maximum_state_error", "final_state_error")
    }
    return {
        "modes": modes,
        "quadratic_to_linear_ratios": ratios,
        "accuracy_passed": max(ratios.values()) <= 0.5,
        "positive_finite_conservation_passed": all(
            v["finite"] and v["positive"] and v["conservation_passed"] for v in modes.values()
        ),
    }


def trajectory_campaign(model: chart.QuadraticChart, progress: Callable | None = None) -> dict:
    seed = 2026090712
    directions = chart.normalized_directions(seed, 16)
    records = []
    for index, direction in enumerate(directions):
        for amplitude in TRAJECTORY_AMPLITUDES:
            record = {
                "direction_index": index,
                "amplitude": amplitude,
                **trajectory_case(model, amplitude * direction),
            }
            records.append(record)
            if progress is not None:
                progress(
                    {
                        "phase": "trajectory",
                        "completed": len(records),
                        "total": 48,
                        "direction": index,
                        "amplitude": amplitude,
                        "ratios": record["quadratic_to_linear_ratios"],
                        "conservation_positive_finite": record[
                            "positive_finite_conservation_passed"
                        ],
                    }
                )
    return {
        "seed": seed,
        "directions": directions.tolist(),
        "amplitudes": list(TRAJECTORY_AMPLITUDES),
        "steps": TRAJECTORY_STEPS,
        "initialization": "each full trajectory starts at its own W_degree(a0); linear and quadratic physical initial states differ",
        "records": records,
        "coverage_passed": len(records) == 48,
        "accuracy_passed": all(r["accuracy_passed"] for r in records),
        "positive_finite_conservation_passed": all(
            r["positive_finite_conservation_passed"] for r in records
        ),
    }


def write_archive(path: Path, arrays: dict[str, np.ndarray]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Fail closed instead of silently overwriting a sealed coefficient archive.
    with path.open("xb") as output:
        np.savez_compressed(output, **arrays)
    metadata = {name: chart.array_metadata(value) for name, value in arrays.items()}
    with np.load(path, allow_pickle=False) as saved:
        roundtrip = set(saved.files) == set(arrays) and all(
            chart.array_metadata(saved[name]) == value for name, value in metadata.items()
        )
    return {
        "filename": path.name,
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "serialized_bytes": path.stat().st_size,
        "arrays": metadata,
        "roundtrip_passed": roundtrip,
        "all_arrays_finite": all(bool(np.all(np.isfinite(value))) for value in arrays.values()),
    }


def classify(validity: dict, hypotheses: dict, orders_resolved: bool) -> str:
    if not all(validity.values()) or not orders_resolved:
        return "inconclusive"
    return "accepted" if all(hypotheses.values()) else "rejected"


def run_study(archive_path: Path, progress: Callable | None = None) -> dict:
    inputs = input_audit()
    construction, controls, residuals, trajectories, archive, replay = {}, {}, {}, {}, None, None
    if inputs["passed"]:
        model = chart.build_chart()
        construction = model.construction
        construction["gates"] = construction_gates(construction)
        if progress is not None:
            progress({"phase": "construction", "gates": construction["gates"]})
        for name, function in (
            ("evaluation", evaluation_controls),
            ("hessian", hessian_controls),
            ("symmetry", symmetry_controls),
        ):
            controls[name] = function(model)
            if progress is not None:
                progress(
                    {
                        "phase": "independent_controls",
                        "control": name,
                        "passed": controls[name]["passed"],
                    }
                )
        residuals = residual_campaign(model, progress)
        trajectories = trajectory_campaign(model, progress)
        arrays = model.archive_arrays()
        rebuilt = chart.build_chart()
        repeated = rebuilt.archive_arrays()
        array_checks = {
            name: chart.array_metadata(value) == chart.array_metadata(repeated[name])
            for name, value in arrays.items()
        }
        replay = {
            "scope": "fresh 26 frames and all 3081 pair solves with bitwise array hashes; not a rerun of the trajectory campaign",
            "array_checks": array_checks,
            "coverage_passed": rebuilt.construction["coverage_passed"],
            "coefficient_passed": rebuilt.construction["coefficient_passed"],
            "passed": all(array_checks.values())
            and rebuilt.construction["coverage_passed"]
            and rebuilt.construction["coefficient_passed"],
        }
        archive = write_archive(archive_path, arrays)
        if progress is not None:
            progress(
                {
                    "phase": "independent_coefficient_rebuild",
                    "passed": replay["passed"],
                    "archive_bytes": archive["serialized_bytes"],
                }
            )
    validity = {
        "sealed_inputs": inputs["passed"],
        "all_104_coordinates_and_5460_products": bool(construction)
        and construction["coverage_passed"],
        "registered_independent_controls": len(controls) == 3
        and len(controls["evaluation"]["records"]) == 8
        and len(controls["hessian"]["records"]) == 8
        and len(controls["symmetry"]["records"]) == 192,
        "registered_residual_coverage": bool(residuals) and residuals["coverage_passed"],
        "registered_trajectory_coverage": bool(trajectories) and trajectories["coverage_passed"],
        "archive_roundtrip": archive is not None and archive["roundtrip_passed"],
        "independent_all_coefficient_rebuild": replay is not None and replay["passed"],
        "finite_evidence": archive is not None
        and archive["all_arrays_finite"]
        and _all_numeric_values_finite(
            (construction, controls, residuals, trajectories, archive, replay)
        ),
    }
    hypotheses = {
        "quadratic_structure_and_nontrivial_R2": bool(construction)
        and all(construction["gates"].values()),
        "independent_coefficient_evaluations": bool(controls) and controls["evaluation"]["passed"],
        "independent_physical_hessian_and_equation": bool(controls)
        and controls["hessian"]["passed"],
        "all_48_cubic_operations": bool(controls) and controls["symmetry"]["passed"],
        "all_64_generic_orders_and_defect_reduction": bool(residuals)
        and residuals["generic_orders_passed"],
        "nonzero_reduced_negative_control": bool(residuals)
        and residuals["nonzero_reduced_negative_control_passed"],
        "all_48_trajectory_improvements": bool(trajectories) and trajectories["accuracy_passed"],
        "finite_positive_conserved_trajectory_samples": bool(trajectories)
        and trajectories["positive_finite_conservation_passed"],
    }
    outcome = classify(
        validity, hypotheses, bool(residuals) and residuals["generic_orders_resolved"]
    )
    cycle = {
        "protocol": "Q012d full 104-real-coordinate quadratic W/R on the fixed-four-moment leaf",
        "configuration": {
            "size": chart.SIZE,
            "omega": chart.OMEGA,
            "eta": chart.ETA,
            "power": chart.POWER,
            "real_coordinate_count": 104,
            "fft_normalization": "ortho",
        },
        "map": "modified D3Q27 Phi=(I-eta D^2) Phi_BGK; not original BGK",
        "input_audit": inputs,
        "construction": construction,
        "controls": controls,
        "residual_campaign": residuals,
        "trajectory_campaign": trajectories,
        "coefficient_archive": archive,
        "independent_rebuild": replay,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite quadratic jet and registered finite samples only; no SSM existence, uniqueness, positive-radius or nonlinear normal-attraction certificate, no grid-uniform chart and no TT advantage",
        "next_question": "Practical amplitude and higher-degree/existence gap, then mandatory Fourier-sparse versus TT cost audit"
        if outcome == "accepted"
        else "Diagnose failed or unresolved gates in a separate registered question without changing Q012d thresholds",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
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
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive_path = args.output.with_suffix(".npz")
    if args.output.exists() or archive_path.exists():
        parser.error("use a fresh output path; sealed evidence is never overwritten")
    result = run_study(archive_path, lambda row: print(json.dumps(row), flush=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, allow_nan=False, separators=(",", ":")) + "\n")
    print(
        json.dumps(
            {
                "study_gate": result["study_gate"],
                "scientific_outcome": result["scientific_outcome"],
                "hypotheses": result["cycle"]["hypothesis_gates"],
            }
        ),
        flush=True,
    )
    if result["study_gate"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
