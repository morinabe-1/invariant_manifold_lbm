"""Q012f2 paired/refined coefficients with exact external residual decisions."""

from __future__ import annotations

import gzip
import json
from collections import Counter
from hashlib import file_digest, sha256

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_cubic_precision as precision
from research import d3q27_damping as damping
from research import d3q27_exact_residual as exact
from ttim_lbm.rational_spectrum import _all_numeric_values_finite


def candidate_gates(reference, refined, proof):
    return {
        "rank_and_condition": reference["status"] == "nonsingular_practical"
        and reference["numerical_rank"] == reference["operator_dimension"]
        and reference["condition_number"] is not None
        and reference["condition_number"] <= 1e8,
        "svd_backend_integrity": reference["backend"]["passed"],
        **{k: proof["gates"][k] for k in exact.EXACT_GATES},
        "full_population_equation": refined["full_relative_residual"] <= 1e-9,
        "fixed_leaf_and_structure": refined["structural_error"] <= 5e-12,
    }


def solve_case(context, ordinal, kernel=exact.audit_integer):
    jet = cubic.solve_triple(context, ordinal)
    a, d, f, sector = precision.problem(context, ordinal, jet)
    solutions, history = precision.structured_solutions(a, d, f)
    x = solutions["refined"]
    r64 = a @ x - x @ d + f
    r128 = precision.residual_mpc(a, d, f, x)
    denominator = max(1e-14, float(np.linalg.norm(f)))
    proof = kernel(a, d, f, x, r64, r128, denominator)
    response = sector.basis @ x
    model = context.model
    frame = model.frames.get(jet.wave)
    selected = frame.basis @ jet.reduced if frame is not None else np.zeros_like(jet.forcing)
    symbol = damping.fourier_symbol(
        2 * np.pi * np.asarray(jet.wave) / model.size, model.omega, model.eta, model.power
    )
    full = float(
        np.linalg.norm(symbol @ response - response @ d + jet.forcing - selected)
        / max(1e-14, np.linalg.norm(jet.forcing))
    )
    gauge = float(
        np.linalg.norm(sector.selected_projector @ response) / max(1, np.linalg.norm(response))
    )
    mean = (
        float(
            np.linalg.norm(d3.conserved_moment_matrix() @ response)
            / max(1, np.linalg.norm(response))
        )
        if jet.wave == (0, 0, 0)
        else 0.0
    )
    structure = max(
        gauge,
        mean,
        sector.structural_error,
        jet.record["symmetric_product_error"],
        jet.record["zero_wave_forcing_moment_error"],
    )
    refined = {
        "external_relative_residual": float(np.linalg.norm(r64) / denominator),
        "mp128_relative_residual": float(np.linalg.norm(r128) / denominator),
        "full_relative_residual": full,
        "structural_error": structure,
        "response_norm": float(np.linalg.norm(response)),
        "arrays": {
            "external_solution": chart.array_metadata(x),
            "population_response": chart.array_metadata(response),
        },
        "passed": jet.record["status"] == "nonsingular_practical"
        and proof["gates"]["legacy"]
        and full <= 1e-9
        and structure <= 5e-12,
    }
    fields = {
        "forcing": (jet.forcing * jet.factors).T,
        "response": (response * jet.factors).T,
        "reduced": (jet.reduced * jet.factors).T,
    }
    gates = candidate_gates(jet.record, refined, proof)
    row = {
        "ordinal": ordinal,
        "paired_svd_reference": jet.record,
        "problem_arrays": {
            name: chart.array_metadata(value)
            for name, value in (
                ("external_dynamics", a),
                ("input_dynamics", d),
                ("external_forcing", f),
                ("forcing", jet.forcing),
            )
        },
        "refined": refined,
        "refinement_history": history,
        "graph_gauge_error": gauge,
        "zero_wave_response_moment_error": mean,
        "stored_denominator": denominator,
        "exact_residual": proof,
        "coefficient_arrays": {k: chart.array_metadata(v) for k, v in fields.items()},
        "candidate_gates": gates,
        "passed": all(gates.values()),
    }
    return row, {"triples": jet.input_triples, "wave": jet.wave, **fields}


def record_line(row):
    return (json.dumps(row, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def file_hash(path):
    with path.open("rb") as source:
        return file_digest(source, "sha256").hexdigest()


def iter_records(path):
    with gzip.open(path, "rt", encoding="utf-8") as source:
        for line in source:
            yield json.loads(line)


class RecordWriter:
    """Bounded-memory, nonoverwriting gzip writer; no numerical failure is skipped."""

    def __init__(self, path):
        self.path = path
        self.digest = sha256()
        self.count = 0
        self.closed = False

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.target = self.path.open("xb")
        self.zipped = gzip.GzipFile(filename="", mode="wb", fileobj=self.target, mtime=0)
        return self

    def append(self, row):
        data = record_line(row)
        self.zipped.write(data)
        self.digest.update(data)
        self.count += 1
        if self.count % 1024 == 0:
            self.zipped.flush()
            self.target.flush()

    def __exit__(self, *_):
        try:
            self.zipped.close()
        finally:
            self.target.close()
            self.closed = True

    def metadata(self):
        if not self.closed:
            raise ValueError("close the record archive before sealing it")
        digest, count = sha256(), 0
        for row in iter_records(self.path):
            digest.update(record_line(row))
            count += 1
        return {
            "filename": self.path.name,
            "bytes": self.path.stat().st_size,
            "sha256": file_hash(self.path),
            "record_count": self.count,
            "records_digest_sha256": self.digest.hexdigest(),
            "roundtrip_passed": count == self.count
            and digest.hexdigest() == self.digest.hexdigest(),
        }


class Summary:
    def __init__(self):
        self.records = self.count = self.columns = 0
        self.ordered = self.finite = True
        self.status = Counter()
        self.failures = Counter()
        self.families = Counter()
        self.legacy_families = Counter()
        self.failed_ordinals = []
        self.legacy_failed_ordinals = []
        self.mismatch_ordinals = []
        self.fallback_ordinals = []
        self.execution_errors = []
        self.previous_count = self.previous_failed = self.mp128_failed = 0
        self.worst = {}
        self.worst_values = {}

    def add(self, row):
        self.records += 1
        self.finite &= _all_numeric_values_finite(row)
        if "execution_error" in row:
            self.execution_errors.append(row)
            self.ordered = False
            return
        self.ordered &= row["ordinal"] == self.count
        self.count += 1
        reference, refined, proof = (
            row["paired_svd_reference"],
            row["refined"],
            row["exact_residual"],
        )
        self.columns += reference["product_dimension"]
        self.status[reference["status"]] += 1
        for key, value in row["candidate_gates"].items():
            self.failures[key] += not value
        for key, value in proof["gates"].items():
            self.failures["residual_column_" + key] += not value
        family = "/".join(sorted(reference["input_labels"]))
        if not row["passed"]:
            self.failed_ordinals.append(row["ordinal"])
            self.families[family] += 1
        if not refined["passed"]:
            self.legacy_failed_ordinals.append(row["ordinal"])
            self.legacy_families[family] += 1
        if proof["evaluation_only_mismatch"]:
            self.mismatch_ordinals.append(row["ordinal"])
        if reference["backend"]["fallback"]:
            self.fallback_ordinals.append(row["ordinal"])
        self.mp128_failed += not proof["mp128_agrees"]
        if row.get("previous_match") is not None:
            self.previous_count += 1
            self.previous_failed += not row["previous_match"]["passed"]
        values = {
            "condition": reference["condition_number"],
            "full_residual": refined["full_relative_residual"],
            "structural_error": refined["structural_error"],
            "response_norm": refined["response_norm"],
            "legacy_external_residual": refined["external_relative_residual"],
            "exact_residual": exact.rational(proof["norms_squared"]["exact_residual_norm_squared"])
            / exact.rational(proof["exact_denominator_squared"]),
        }
        for key, value in values.items():
            if value is not None and (key not in self.worst or value > self.worst_values[key]):
                self.worst[key], self.worst_values[key] = row, value

    def result(self):
        coverage = (
            self.records == self.count == cubic.TRIPLE_COUNT
            and self.columns == cubic.COLUMN_COUNT
            and self.ordered
        )
        return {
            "record_count": self.records,
            "completed_count": self.count,
            "product_dimension_sum": self.columns,
            "coverage_passed": coverage,
            "finite": bool(self.finite),
            "status_counts": dict(sorted(self.status.items())),
            "gate_failure_counts": dict(sorted(self.failures.items())),
            "candidate_failed_count": len(self.failed_ordinals),
            "candidate_failed_ordinals": self.failed_ordinals,
            "candidate_failed_families": dict(sorted(self.families.items())),
            "legacy_failed_count": len(self.legacy_failed_ordinals),
            "legacy_failed_ordinals": self.legacy_failed_ordinals,
            "legacy_failed_families": dict(sorted(self.legacy_families.items())),
            "evaluation_only_mismatch_ordinals": self.mismatch_ordinals,
            "fallback_ordinals": self.fallback_ordinals,
            "mp128_agreement_failures": self.mp128_failed,
            "previous_selected_count": self.previous_count,
            "previous_selected_failures": self.previous_failed,
            "worst_cases": self.worst,
            "execution_errors": self.execution_errors,
            "all_candidates_passed": coverage and not self.failed_ordinals,
        }


def summarize(rows):
    summary = Summary()
    for row in rows:
        summary.add(row)
    return summary.result()


def save_fibers(path, arrays):
    if not arrays or not all(
        np.asarray(value).dtype in (np.dtype("int64"), np.dtype("complex128"))
        and np.all(np.isfinite(value))
        for value in arrays.values()
    ):
        raise ValueError("only finite int64/complex128 fiber arrays can be saved")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        np.savez_compressed(target, **arrays)
    entries = {k: chart.array_metadata(v) for k, v in arrays.items()}
    with np.load(path, allow_pickle=False) as restored:
        equal = set(restored.files) == set(entries) and all(
            chart.array_metadata(restored[k]) == v for k, v in entries.items()
        )
    return {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": file_hash(path),
        "entries": entries,
        "roundtrip_passed": equal,
    }
