"""Run the preregistered Q012e rational-tail and finite-amplitude study."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from research import d3q27_amplitude as amplitude
from research import d3q27_chart as chart
from research import q012a_d3q27_foundation as q012a
from research import q012d1_d3q27_negative_control as previous
from research import q012d_d3q27_quadratic_chart as prior
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012d1_d3q27_negative_control.json"
PRIOR_SHA256 = "812cda7e30678029b91f2a2a56f1ec2cc8cad73ba170d42c3c805769f15c5190"
PRIOR_RESULT = "a78e8e61b7a5bd185ab579ae4ecc032154229b627a070c18e90a3494ee363075"
HELPERS = previous.HELPERS + (("negative_control_runner", previous), ("amplitude", amplitude))


def input_audit() -> dict:
    old = json.loads(PRIOR_PATH.read_text(encoding="utf-8"))
    cycle = dict(old["cycle"])
    digest = cycle.pop("result_digest_sha256")
    experiment = dict(cycle["experiment"])
    experiment_digest = experiment.pop("result_digest_sha256")
    replay_path = PRIOR_PATH.parent / cycle["independent_replay"]["filename"]
    worker = json.loads(replay_path.read_text(encoding="utf-8"))
    checks = {
        "prior_input_chain": previous.input_audit()["passed"],
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA256,
        "result_digest": q012a._digest(cycle) == digest == PRIOR_RESULT,
        "experiment_digest": q012a._digest(experiment) == experiment_digest,
        "package_source": old["source"] == source_metadata(),
        "runner_seal": _file_sha256(Path(previous.__file__)) == old["runner_source"]["sha256"],
        "prior_replay_seal": _file_sha256(replay_path) == cycle["independent_replay"]["sha256"],
        "prior_replay_science": worker["experiment"] == cycle["experiment"]
        and cycle["independent_replay"]["passed"],
        "cubic_rejection_retained": old["study_gate"] == cycle["study_validity"] == "passed"
        and old["scientific_outcome"] == cycle["scientific_outcome"] == "rejected"
        and all(cycle["validity_gates"].values())
        and [k for k, v in cycle["hypothesis_gates"].items() if not v]
        == ["cubic_quartic_explanation_of_original_window"],
    }
    for name, module in previous.HELPERS:
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == old["helper_sources"][name]["sha256"]
        )
    return {"filename": PRIOR_PATH.name, "checks": checks, "passed": all(checks.values())}


def fresh_chart() -> tuple[chart.QuadraticChart, dict]:
    model = chart.build_chart()
    arrays = {name: chart.array_metadata(value) for name, value in model.archive_arrays().items()}
    expected = previous.prior_artifact()["cycle"]["coefficient_archive"]["arrays"]
    return model, {
        "arrays": arrays,
        "all_twelve_arrays_equal": len(arrays) == 12 and arrays == expected,
        "passed": len(arrays) == 12
        and arrays == expected
        and model.construction["coefficient_passed"]
        and model.construction["coverage_passed"],
    }


def metadata() -> dict:
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


def guarded_case(
    model: chart.QuadraticChart,
    terms: amplitude.PathTerms,
    group: str,
    index: int,
    value: float,
    sign: int,
) -> dict:
    try:
        return amplitude.evaluate_case(model, terms, group, index, value, sign)
    except (ArithmeticError, ValueError, RuntimeError) as error:
        # Keep the case in coverage and fail validity; never replace it with a pass.
        return {
            "group": group,
            "direction_index": index,
            "amplitude": value,
            "sign": sign,
            "execution_error": {"type": type(error).__name__, "message": str(error)},
            "usage_passed": False,
            "usage_gates": {"execution_completed": False},
        }


def replay_evidence(inputs: dict, rebuild: dict | None, records: list[dict]) -> dict:
    indexed = {amplitude.case_key(r): r for r in records}
    return {
        "input_audit": inputs,
        "coefficient_rebuild": rebuild,
        "records": [indexed[key] for key in amplitude.REPLAY_CASES if key in indexed],
    }


def worker(progress: Callable | None = None) -> dict:
    current, inputs = metadata(), input_audit()
    rebuild, records = None, []
    if inputs["passed"]:
        model, rebuild = fresh_chart()
        terms = {
            group: amplitude.path_terms(model, chart.normalized_directions(seed, 8)[0])
            for group, seed in amplitude.SEEDS.items()
        }
        for group, index, value, sign in amplitude.REPLAY_CASES:
            records.append(guarded_case(model, terms[group], group, index, value, sign))
            if progress is not None:
                progress(
                    {
                        "phase": "independent_replay",
                        "completed": len(records),
                        "case": (group, index, value, sign),
                    }
                )
    evidence = replay_evidence(inputs, rebuild, records)
    return {
        **current,
        "kind": "independent_four_case_worker",
        "evidence": evidence,
        "evidence_digest_sha256": q012a._digest(evidence),
    }


def replay_audit(path: Path, expected: dict, current: dict) -> dict:
    old = json.loads(path.read_text(encoding="utf-8"))
    checks = {
        "kind": old["kind"] == "independent_four_case_worker",
        "separate_process": old["process_id"] != current["process_id"],
        "source_identity": all(
            old[key] == current[key] for key in ("source", "runner_source", "helper_sources")
        ),
        "worker_digest": q012a._digest(old["evidence"]) == old["evidence_digest_sha256"],
        "registered_four_cases": [amplitude.case_key(r) for r in old["evidence"]["records"]]
        == list(amplitude.REPLAY_CASES),
        "all_values_reproduced": old["evidence"] == expected,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "worker_process_id": old["process_id"],
        "evidence_digest_sha256": old["evidence_digest_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
        "scope": "fresh full coefficient rebuild and all one-step/trajectory values for four preregistered cases only",
    }


def run_study(replay_path: Path, progress: Callable | None = None) -> dict:
    current, inputs = metadata(), input_audit()
    rebuild, records, directions, prefix = None, [], [], []
    if inputs["passed"]:
        model, rebuild = fresh_chart()
        for group, seed in amplitude.SEEDS.items():
            for index, u in enumerate(chart.normalized_directions(seed, 8)):
                terms = amplitude.path_terms(model, u)
                directions.append(
                    {
                        "group": group,
                        "direction_index": index,
                        "direction": u.tolist(),
                        "coefficient_audit": terms.audit,
                    }
                )
                for value in amplitude.AMPLITUDES:
                    for sign in (1, -1):
                        row = guarded_case(model, terms, group, index, value, sign)
                        records.append(row)
                        if progress is not None:
                            progress(
                                {
                                    "phase": "finite_amplitude",
                                    "completed": len(records),
                                    "total": 224,
                                    "case": amplitude.case_key(row),
                                    "usage_passed": row["usage_passed"],
                                }
                            )
            if group == "calibration":
                prefix = amplitude.select_prefix(
                    amplitude.amplitude_inventory(records, "calibration")
                )
                if progress is not None:
                    progress(
                        {"phase": "calibration_selection_before_holdout", "locked_prefix": prefix}
                    )
    inventory = {group: amplitude.amplitude_inventory(records, group) for group in amplitude.SEEDS}
    replay = replay_audit(replay_path, replay_evidence(inputs, rebuild, records), current)
    keys = {
        (group, index, value, sign)
        for group in amplitude.SEEDS
        for index in range(8)
        for value in amplitude.AMPLITUDES
        for sign in (1, -1)
    }
    coverage = (
        len(records) == 224
        and {amplitude.case_key(r) for r in records} == keys
        and len(directions) == 16
    )
    validity = {
        "sealed_input_chain": inputs["passed"],
        "fresh_all_coefficients_equal": rebuild is not None and rebuild["passed"],
        "registered_224_cases": coverage,
        "no_numerical_execution_failures": coverage
        and all(
            "execution_error" not in r and r["trajectory"]["execution_error"] is None
            for r in records
        ),
        "finite_evidence": _all_numeric_values_finite((rebuild, records, directions)),
        "independent_four_case_replay": replay["passed"],
        "calibration_selection_unchanged": prefix
        == amplitude.select_prefix(inventory["calibration"]),
    }
    evaluable = [r for r in records if "one_step" in r and r["one_step"]["in_domain"]]
    hypotheses = {
        "rational_decomposition": bool(evaluable)
        and all(r["one_step"]["identity_passed"] for r in evaluable),
        "nonempty_calibration_prefix": bool(prefix),
        "selected_prefix_holdout": bool(prefix)
        and all(row["passed"] for row in inventory["holdout"] if row["amplitude"] in prefix),
    }
    outcome = prior.classify(validity, hypotheses, True)
    cycle = {
        "protocol": "Q012e; same initial state, finite registered directions only; Q012d/Q012d1 rejections retained",
        "configuration": {
            "size": chart.SIZE,
            "omega": chart.OMEGA,
            "eta": chart.ETA,
            "power": chart.POWER,
            "real_coordinates": 104,
            "amplitudes": list(amplitude.AMPLITUDES),
            "seeds": amplitude.SEEDS,
            "steps": amplitude.STEPS,
        },
        "initialization": "all trajectories start at W2(a0); linear oracle is base + A^n(W2(a0)-base), not a 104-coordinate cost comparator",
        "input_audit": inputs,
        "coefficient_rebuild": rebuild,
        "directions": directions,
        "records": records,
        "amplitude_inventory": inventory,
        "selection": {
            "calibration_prefix": prefix,
            "selected_amplitude": prefix[-1] if prefix else None,
            "fixed_before_holdout": True,
            "holdout_passed": hypotheses["selected_prefix_holdout"],
        },
        "independent_replay": replay,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite 64-step sampled-use criterion for the unchanged quadratic chart of a modified map; no continuous-ball radius, SSM existence, grid-uniform result, W4/R4, or TT claim",
        "next_question": "Use degree-resolved failure evidence to choose cubic homological preflight versus tail/density diagnosis; preserve all failed amplitudes",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    return {
        **current,
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--worker-output", type=Path)
    targets.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    path = args.worker_output if args.worker_output is not None else args.output
    if path.exists():
        parser.error("use a fresh path; sealed evidence is not overwritten")
    if (args.output is not None) != (args.replay is not None):
        parser.error("--output requires --replay; --worker-output does not use --replay")
    progress = lambda row: print(json.dumps(row), flush=True)
    result = (
        worker(progress) if args.worker_output is not None else run_study(args.replay, progress)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, allow_nan=False, separators=(",", ":")) + "\n")
    if args.output is not None:
        print(
            json.dumps(
                {
                    "study_gate": result["study_gate"],
                    "scientific_outcome": result["scientific_outcome"],
                    "selection": result["cycle"]["selection"],
                }
            ),
            flush=True,
        )
        if result["study_gate"] != "passed":
            raise SystemExit(1)
    elif not result["evidence"]["input_audit"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
