"""Q012d1: separate-process, degree-resolved negative-control diagnosis."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import numpy as np

from research import d3q27_chart as chart
from research import d3q27_negative_control as diagnostic
from research import q012a_d3q27_foundation as q012a
from research import q012d_d3q27_quadratic_chart as prior
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012d_d3q27_quadratic_chart.json"
PRIOR_SHA256 = "d33ca861d7b51096e09de93550e24d33f0722fc12ac531ff591f56383dd4fea8"
PRIOR_RESULT = "c3d24a465f6d2f1050137c5bc5d4c3e91d5ebb1432a0cfbd72321f297edfa7a0"
PRIOR_NPZ_SHA256 = "0877235be7ec1619c0fcd3e982cb1863bee3fb13a62bd68f082f13e59d1b0d8d"
HELPERS = prior.HELPERS + (("quadratic_chart_runner", prior), ("negative_control", diagnostic))


def prior_artifact() -> dict:
    return json.loads(PRIOR_PATH.read_text(encoding="utf-8"))


def input_audit() -> dict:
    artifact = prior_artifact()
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    archive = cycle["coefficient_archive"]
    npz_path = PRIOR_PATH.parent / archive["filename"]
    checks = {
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA256,
        "result_digest": q012a._digest(cycle) == digest == PRIOR_RESULT,
        "package_source": artifact["source"] == source_metadata(),
        "runner_seal": _file_sha256(Path(prior.__file__)) == artifact["runner_source"]["sha256"],
        "prior_inputs": prior.input_audit()["passed"],
        "valid_rejection_preserved": artifact["study_gate"] == cycle["study_validity"] == "passed"
        and artifact["scientific_outcome"] == cycle["scientific_outcome"] == "rejected"
        and len(cycle["validity_gates"]) == 8
        and all(cycle["validity_gates"].values())
        and len(cycle["hypothesis_gates"]) == 8
        and [key for key, value in cycle["hypothesis_gates"].items() if not value]
        == ["nonzero_reduced_negative_control"],
        "four_original_failures": [
            r["direction_index"]
            for r in cycle["residual_campaign"]["generic_records"][:8]
            if not r["omitted_reduced_quadratic"]["passed"]
        ]
        == [0, 2, 4, 5],
        "archive_binary_seal": sha256(npz_path.read_bytes()).hexdigest()
        == archive["sha256"]
        == PRIOR_NPZ_SHA256,
    }
    for name, module in prior.HELPERS:
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
        )
    with np.load(npz_path, allow_pickle=False) as arrays:
        checks["all_twelve_arrays"] = len(arrays.files) == 12 and set(arrays.files) == set(
            archive["arrays"]
        )
        for name, metadata in archive["arrays"].items():
            checks["array_" + name] = chart.array_metadata(arrays[name]) == metadata
    return {"filename": PRIOR_PATH.name, "checks": checks, "passed": all(checks.values())}


def run_experiment(progress: Callable | None = None) -> dict:
    inputs = input_audit()
    rebuild, records = None, []
    if inputs["passed"]:
        old = prior_artifact()["cycle"]
        model = chart.build_chart()
        arrays = {
            name: chart.array_metadata(value) for name, value in model.archive_arrays().items()
        }
        rebuild = {
            "all_array_hashes_equal": arrays == old["coefficient_archive"]["arrays"],
            "pair_count": model.construction["pair_count"],
            "product_dimension_sum": model.construction["product_dimension_sum"],
            "passed": arrays == old["coefficient_archive"]["arrays"]
            and model.construction["coefficient_passed"]
            and model.construction["coverage_passed"],
        }
        if progress is not None:
            progress({"phase": "fresh_full_chart", **rebuild})
        known = np.asarray(old["residual_campaign"]["directions"])[:8]
        holdout = chart.normalized_directions(diagnostic.HOLDOUT_SEED, 32)
        for group, directions in (("known", known), ("holdout", holdout)):
            for index, u in enumerate(directions):
                legacy = (
                    old["residual_campaign"]["generic_records"][index] if group == "known" else None
                )
                row = diagnostic.diagnose_direction(model, u, group, index, legacy)
                records.append(row)
                if progress is not None and len(records) % 4 == 0:
                    progress(
                        {
                            "phase": "degree_diagnosis",
                            "completed": len(records),
                            "total": 40,
                            "last_group": group,
                            "last_gates": row["gates"],
                        }
                    )
    known = [r for r in records if r["group"] == "known"]
    coverage = (
        len(records) == 40
        and {(r["group"], r["direction_index"]) for r in records}
        == {
            (group, index)
            for group, count in (("known", 8), ("holdout", 32))
            for index in range(count)
        }
        and all(
            len(r["samples"]) == 14
            and {(s["amplitude"], s["sign"]) for s in r["samples"]}
            == {(amplitude, sign) for amplitude in diagnostic.AMPLITUDES for sign in (1, -1)}
            and len(r["parity"]) == 7
            for r in records
        )
    )
    validity = {
        "sealed_inputs": inputs["passed"],
        "fresh_all_coefficients_equal": rebuild is not None and rebuild["passed"],
        "registered_560_signed_samples": coverage,
        "finite_evidence": _all_numeric_values_finite((rebuild, records)),
    }
    hypotheses = {
        "original_eight_records_reproduced": len(known) == 8
        and all(r["legacy_reproduction"]["passed"] for r in known),
        "independent_nonzero_coefficients": coverage
        and all(r["gates"]["independent_nonzero_coefficients"] for r in records),
        "exact_chart_composition": coverage
        and all(r["gates"]["exact_chart_composition"] for r in records),
        "cubic_quartic_explanation_of_original_window": coverage
        and all(r["gates"]["original_window_vector_prediction"] for r in records)
        and all(r["legacy_slope_prediction"]["passed"] for r in known),
        "odd_part_independent_cubic": coverage
        and all(r["gates"]["odd_part_independent_cubic"] for r in records),
        "asymptotic_quadratic_behavior": coverage
        and all(r["gates"]["asymptotic_quadratic_behavior"] for r in records),
        "finite_positive_samples": coverage
        and all(r["gates"]["finite_positive_samples"] for r in records),
    }
    experiment = {
        "protocol": "Q012d1 degree-resolved negative control; original Q012d rejection retained",
        "configuration": {
            "size": chart.SIZE,
            "omega": chart.OMEGA,
            "eta": chart.ETA,
            "power": chart.POWER,
            "real_coordinate_count": 104,
            "known_direction_seed": 2026090711,
            "holdout_direction_seed": diagnostic.HOLDOUT_SEED,
        },
        "original_amplitudes": list(diagnostic.ORIGINAL_AMPLITUDES),
        "asymptotic_amplitudes": list(diagnostic.ASYMPTOTIC_AMPLITUDES),
        "input_audit": inputs,
        "coefficient_rebuild": rebuild,
        "records": records,
        "pre_replay_validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "asymptotic_resolved": coverage and all(r["asymptotic_resolved"] for r in records),
    }
    experiment["result_digest_sha256"] = q012a._digest(experiment)
    return experiment


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


def worker(progress: Callable | None = None) -> dict:
    return {
        **metadata(),
        "kind": "independent_experiment_worker",
        "experiment": run_experiment(progress),
    }


def replay_audit(path: Path, experiment: dict, current_metadata: dict) -> dict:
    stored = json.loads(path.read_text(encoding="utf-8"))
    cycle = dict(stored["experiment"])
    digest = cycle.pop("result_digest_sha256")
    checks = {
        "worker_kind": stored["kind"] == "independent_experiment_worker",
        "separate_process": stored["process_id"] != current_metadata["process_id"],
        "source_identity": stored["source"] == current_metadata["source"]
        and stored["runner_source"] == current_metadata["runner_source"]
        and stored["helper_sources"] == current_metadata["helper_sources"],
        "worker_digest": q012a._digest(cycle) == digest,
        "all_experiment_values_reproduced": digest == experiment["result_digest_sha256"]
        and stored["experiment"] == experiment,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "result_digest_sha256": digest,
        "worker_process_id": stored["process_id"],
        "checks": checks,
        "passed": all(checks.values()),
        "scope": "two separate processes, fresh charts and all 560 signed samples each; not a Q012d trajectory replay",
    }


def run_study(replay_path: Path, progress: Callable | None = None) -> dict:
    current = metadata()
    experiment = run_experiment(progress)
    replay = replay_audit(replay_path, experiment, current)
    validity = {
        **experiment["pre_replay_validity_gates"],
        "independent_full_experiment_replay": replay["passed"],
    }
    outcome = prior.classify(
        validity, experiment["hypothesis_gates"], experiment["asymptotic_resolved"]
    )
    cycle = {
        "experiment": experiment,
        "independent_replay": replay,
        "validity_gates": validity,
        "hypothesis_gates": experiment["hypothesis_gates"],
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite-amplitude diagnosis for an unchanged quadratic jet of the modified map; original Q012d remains rejected; no SSM existence, radius, normal-attraction or TT certificate",
        "next_question": "Q012e: practical amplitudes and the higher-degree/existence gap before Fourier-sparse versus TT costs"
        if outcome == "accepted"
        else "Diagnose the failed degree/parity/reproduction gate without changing this protocol",
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
                    "hypotheses": result["cycle"]["hypothesis_gates"],
                }
            ),
            flush=True,
        )
        if result["study_gate"] != "passed":
            raise SystemExit(1)
    else:
        print(
            json.dumps(
                {
                    "experiment_digest": result["experiment"]["result_digest_sha256"],
                    "hypotheses": result["experiment"]["hypothesis_gates"],
                }
            ),
            flush=True,
        )
        if not all(result["experiment"]["pre_replay_validity_gates"].values()):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
