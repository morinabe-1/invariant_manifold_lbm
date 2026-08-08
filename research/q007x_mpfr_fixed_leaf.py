"""Sealed Q007x concrete MPFR-85 backend and fixed-leaf audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np

import research.q007w_ideal_precision_threshold as q007w
import research.q007x_mpfr_backend as backend
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
WAVE_COUNT = SIZE * SIZE
PROBE_DELTA = Fraction(1, 10**13)
PROBE_NAMES = (
    "rest",
    "axial_x_pair",
    "axial_y_pair",
    "all_populations_paired",
)
Q007W_ARTIFACT = "q007w_ideal_precision_threshold.json"
REGISTERED_Q007W_ARTIFACT_SHA256 = (
    "bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af"
)
REGISTERED_Q007W_RUNNER_SHA256 = (
    "86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8"
)
REGISTERED_BACKEND_SOURCE_SHA256 = (
    "25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc"
)
REGISTERED_PYPROJECT_SHA256 = (
    "97e8ed6af7906243a656191f96c80b8f7c1ef4b737587c888092c476be508d94"
)
REGISTERED_D2Q9_SOURCE_SHA256 = (
    "6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53"
)
REGISTERED_FILTER_SOURCE_SHA256 = (
    "5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea"
)
REGISTERED_GMPY2_VERSION = "2.3.1"
REGISTERED_MPFR_VERSION = "MPFR 4.2.2"
REGISTERED_GMP_VERSION = "GMP 6.3.0"
EXPECTED_CONSTRUCTION_TRACE_COUNT = 19
EXPECTED_MAP_TRACE_PER_SITE = 245
EXPECTED_MAP_TRACE_COUNT = EXPECTED_MAP_TRACE_PER_SITE * WAVE_COUNT
EXPECTED_TOTAL_TRACE_PER_PROBE = (
    EXPECTED_CONSTRUCTION_TRACE_COUNT + EXPECTED_MAP_TRACE_COUNT
)

ExactArray = np.ndarray


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _canonical_fraction(value: Fraction) -> str:
    return f"{value.numerator:x}/{value.denominator:x}"


def _digest_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_registered_q007w(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007W_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007w_ideal_precision_threshold.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    cycle = payload.get("cycle", {})
    scope = payload.get("mathematical_scope", {})
    selection = cycle.get("selection", {})
    selected = selection.get("selected_candidate", {})
    previous = selection.get("previous_precision_candidate", {})
    fixed = cycle.get("fixed_q007v_values", {})
    scope_match = bool(
        scope.get("diagnostic")
        == "rational ideal-binary precision-threshold certificate"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == 1.5
        and float(scope.get("eta", np.nan)) == 0.01
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("rounding_model")
        == "ideal binary round-to-nearest ties-to-even"
    )
    selection_match = bool(
        selection.get("candidate_count") == 76
        and selection.get("passing_candidate_count") == 44
        and selection.get("selected_precision_bits") == 85
        and selection.get("first_pass_matches_selection", False)
        and selection.get("selection_boundary_reproduced", False)
        and selected.get("precision_bits") == 85
        and selected.get("passed", False)
        and selected.get("base_reentry_passed", False)
        and selected.get("normal_reentry_passed", False)
        and previous.get("precision_bits") == 84
        and not previous.get("base_reentry_passed", True)
        and previous.get("normal_reentry_passed", False)
        and not previous.get("passed", True)
    )
    transitive_match = bool(
        cycle.get("input_artifact", {}).get("passed", False)
        and fixed.get("passed", False)
        and fixed.get("operation_counts_match", False)
        and fixed.get("normalized_dft_wave_count") == WAVE_COUNT
        and fixed.get("d2q9_source_sha256")
        == REGISTERED_D2Q9_SOURCE_SHA256
        and fixed.get("filter_source_sha256")
        == REGISTERED_FILTER_SOURCE_SHA256
    )
    record = {
        "filename": Q007W_ARTIFACT,
        "registered_sha256": REGISTERED_Q007W_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007W_ARTIFACT_SHA256
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": scope_match,
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload,
            "hypothesis_gates",
        ),
        "all_theorem_consequences_true": bool(
            cycle.get("theorem_consequence", {})
            and all(cycle["theorem_consequence"].values())
        ),
        "selection_match": selection_match,
        "transitive_inputs_match": transitive_match,
        "registered_runner_sha256": REGISTERED_Q007W_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007W_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007W_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["validity_gate_count"] == 7
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 6
        and record["all_hypothesis_gates_pass"]
        and record["all_theorem_consequences_true"]
        and selection_match
        and transitive_match
        and record["runner_sha_matches"]
    )
    exact = {
        "state_radius": _fraction_from_record(
            fixed["state_wiener_l1_upper"]
        ),
        "base_margin": _fraction_from_record(
            fixed["base_forward_invariance_margin"]
        ),
        "normal_margin": _fraction_from_record(
            fixed["normal_tube_forward_invariance_margin"]
        ),
        "base_error": _fraction_from_record(
            selected["base_coordinate_error_upper"]
        ),
        "normal_error": _fraction_from_record(
            selected["normal_coordinate_error_upper"]
        ),
        "stage_error_bounds": {
            name: _fraction_from_record(stage["maximum_component_error"])
            for name, stage in selected["stage_bounds"].items()
        },
        "stage_population_lowers": {
            name: _fraction_from_record(stage["population_lower"])
            for name, stage in selected["stage_bounds"].items()
        },
        "rounded_constants": selected["rounded_constants"],
        "registered_operation_counts": fixed["operation_counts"],
    }
    return payload, record, exact


def _source_audit(q007w_exact: dict[str, Any]) -> dict[str, Any]:
    repository = Path(__file__).resolve().parents[1]
    backend_path = Path(backend.__file__).resolve()
    pyproject_path = repository / "pyproject.toml"
    d2q9_path = repository / "src" / "ttim_lbm" / "d2q9.py"
    filter_path = repository / "src" / "ttim_lbm" / "checkerboard_filter.py"
    observed = {
        "backend": _file_sha256(backend_path),
        "pyproject": _file_sha256(pyproject_path),
        "d2q9": _file_sha256(d2q9_path),
        "filter": _file_sha256(filter_path),
    }
    registered = {
        "backend": REGISTERED_BACKEND_SOURCE_SHA256,
        "pyproject": REGISTERED_PYPROJECT_SHA256,
        "d2q9": REGISTERED_D2Q9_SOURCE_SHA256,
        "filter": REGISTERED_FILTER_SOURCE_SHA256,
    }
    backend_text = backend_path.read_text(encoding="utf-8")
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    schedule_tokens = (
        "evaluate_fraction_stages",
        "_reduce",
        "_multiply",
        "_divide",
        "post_collision",
        "post_streaming",
        "post_filter",
        "filter_center",
        "filter_neighbour",
    )
    passed = bool(
        observed == registered
        and pyproject_text.count('"gmpy2==2.3.1"') == 1
        and all(token in backend_text for token in schedule_tokens)
        and "np.sum" not in backend_text
        and "einsum" not in backend_text
        and "fma" not in backend_text.lower()
        and q007w_exact["registered_operation_counts"]
        == backend.PER_SITE_OPERATION_COUNTS
    )
    return {
        "files": {
            name: {
                "registered_sha256": registered[name],
                "sha256": observed[name],
                "sha256_matches": observed[name] == registered[name],
            }
            for name in registered
        },
        "dependency_pin_count": pyproject_text.count('"gmpy2==2.3.1"'),
        "required_schedule_tokens": list(schedule_tokens),
        "all_required_schedule_tokens_present": all(
            token in backend_text for token in schedule_tokens
        ),
        "forbidden_implicit_or_fused_operations_absent": bool(
            "np.sum" not in backend_text
            and "einsum" not in backend_text
            and "fma" not in backend_text.lower()
        ),
        "q007w_operation_schedule_matches_backend": (
            q007w_exact["registered_operation_counts"]
            == backend.PER_SITE_OPERATION_COUNTS
        ),
        "passed": passed,
    }


def _context_signature(context: gmpy2.context) -> tuple[Any, ...]:
    return (
        context.precision,
        context.round,
        context.emin,
        context.emax,
        context.subnormalize,
        context.trap_underflow,
        context.trap_overflow,
        context.trap_divzero,
        context.trap_invalid,
        context.trap_inexact,
        context.allow_complex,
        context.rational_division,
        context.allow_release_gil,
    )


def _context_audit() -> dict[str, Any]:
    before = _context_signature(gmpy2.get_context())
    runtime = backend.backend_runtime_metadata()
    registered_context = backend.mpfr_context()
    constructed = backend.MPFRD2Q9Backend()
    after = _context_signature(gmpy2.get_context())
    smallest_positive = Fraction(1, 2**1106)
    half_smallest = Fraction(1, 2**1107)
    fallback_match = bool(
        half_smallest
        == q007w.PrecisionModel.from_bits(85).subnormal_fallback
    )
    expected_runtime = {
        "gmpy2_version": REGISTERED_GMPY2_VERSION,
        "mpfr_version": REGISTERED_MPFR_VERSION,
        "gmp_version": REGISTERED_GMP_VERSION,
        "mpc_version": "MPC 1.4.0",
        "precision_bits": 85,
        "rounding": "RoundToNearest",
        "rounding_code": int(gmpy2.RoundToNearest),
        "emin": -1105,
        "emax": 1024,
        "subnormalize": True,
        "trap_underflow": True,
        "trap_overflow": True,
        "trap_divzero": True,
        "trap_invalid": True,
        "trap_inexact": False,
        "allow_complex": False,
        "rational_division": False,
        "allow_release_gil": False,
    }
    dangerous_flags = {
        name: value
        for name, value in constructed.construction_context_flags.items()
        if name
        in {
            "underflow",
            "overflow",
            "invalid",
            "division_by_zero",
            "erange",
        }
    }
    passed = bool(
        importlib.metadata.version("gmpy2") == REGISTERED_GMPY2_VERSION
        and runtime == expected_runtime
        and registered_context.round == gmpy2.RoundToNearest
        and before == after
        and not any(dangerous_flags.values())
        and constructed.construction_all_results_finite
        and constructed.construction_trace_record_count
        == EXPECTED_CONSTRUCTION_TRACE_COUNT
        and smallest_positive / 2 == half_smallest
        and fallback_match
    )
    return {
        "registered_runtime": expected_runtime,
        "runtime": runtime,
        "installed_distribution_version": importlib.metadata.version("gmpy2"),
        "context_restored": before == after,
        "smallest_positive_subnormal": _fraction_record(smallest_positive),
        "half_smallest_subnormal": _fraction_record(half_smallest),
        "q007w_subnormal_fallback_match": fallback_match,
        "construction_context_flags": constructed.construction_context_flags,
        "dangerous_construction_flags": dangerous_flags,
        "construction_trace_record_count": (
            constructed.construction_trace_record_count
        ),
        "construction_all_results_finite": (
            constructed.construction_all_results_finite
        ),
        "passed": passed,
    }


def _rest_state() -> ExactArray:
    state = np.empty((SIZE, SIZE, 9), dtype=object)
    for y in range(SIZE):
        for x in range(SIZE):
            state[y, x, :] = backend.D2Q9_EXACT_WEIGHTS
    return state


def _build_probes() -> list[tuple[str, ExactArray]]:
    probes: list[tuple[str, ExactArray]] = []
    probes.append(("rest", _rest_state()))

    axial_x = _rest_state()
    axial_x[0, 0, 1] += PROBE_DELTA
    axial_x[0, 1, 1] -= PROBE_DELTA
    probes.append(("axial_x_pair", axial_x))

    axial_y = _rest_state()
    axial_y[1, 0, 2] += PROBE_DELTA
    axial_y[2, 0, 2] -= PROBE_DELTA
    probes.append(("axial_y_pair", axial_y))

    all_populations = _rest_state()
    for population in range(9):
        sign = 1 if population % 2 == 0 else -1
        amplitude = sign * Fraction(population + 1, 10) * PROBE_DELTA
        plus = (2 * population % SIZE, 3 * population % SIZE)
        minus = (
            (2 * population + 1) % SIZE,
            (3 * population + 5) % SIZE,
        )
        all_populations[plus[0], plus[1], population] += amplitude
        all_populations[minus[0], minus[1], population] -= amplitude
    probes.append(("all_populations_paired", all_populations))
    return probes


def _global_conserved(state: ExactArray) -> tuple[Fraction, Fraction, Fraction]:
    mass = Fraction(0)
    momentum_x = Fraction(0)
    momentum_y = Fraction(0)
    for y in range(state.shape[0]):
        for x in range(state.shape[1]):
            for population, (cx, cy) in enumerate(
                backend.D2Q9_INTEGER_VELOCITIES
            ):
                value = Fraction(state[y, x, population])
                mass += value
                momentum_x += cx * value
                momentum_y += cy * value
    return mass, momentum_x, momentum_y


def _mpfr_to_fraction_array(state: np.ndarray) -> ExactArray:
    exact = np.empty(state.shape, dtype=object)
    for index in np.ndindex(state.shape):
        exact[index] = backend.fraction_from_mpfr(state[index])
    return exact


def _conserved_record(
    values: tuple[Fraction, Fraction, Fraction],
) -> dict[str, dict[str, Any]]:
    return {
        name: _fraction_record(value)
        for name, value in zip(("mass", "momentum_x", "momentum_y"), values)
    }


def _difference(
    current: tuple[Fraction, Fraction, Fraction],
    reference: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(
        current[index] - reference[index] for index in range(3)
    )


def _all_zero(values: tuple[Fraction, Fraction, Fraction]) -> bool:
    return all(value == 0 for value in values)


def _probe_digest(probes: list[tuple[str, ExactArray]]) -> str:
    digest = hashlib.sha256()
    for name, state in probes:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        for index in np.ndindex(state.shape):
            value = Fraction(state[index])
            digest.update(
                (
                    f"{index[0]},{index[1]},{index[2]}:"
                    f"{_canonical_fraction(value)}\n"
                ).encode("ascii")
            )
    return digest.hexdigest()


def _probe_registration_audit(
    state_radius: Fraction,
) -> tuple[dict[str, Any], list[tuple[str, ExactArray]]]:
    probes = _build_probes()
    expected_conserved = (Fraction(WAVE_COUNT), Fraction(0), Fraction(0))
    records = []
    for name, state in probes:
        conserved = _global_conserved(state)
        maximum_deviation = max(
            abs(
                Fraction(state[y, x, population])
                - backend.D2Q9_EXACT_WEIGHTS[population]
            )
            for y in range(SIZE)
            for x in range(SIZE)
            for population in range(9)
        )
        minimum_population = min(Fraction(value) for value in state.flat)
        minimum_density = min(
            sum(
                (
                    Fraction(state[y, x, population])
                    for population in range(9)
                ),
                Fraction(0),
            )
            for y in range(SIZE)
            for x in range(SIZE)
        )
        nonzero_perturbations = sum(
            Fraction(state[y, x, population])
            != backend.D2Q9_EXACT_WEIGHTS[population]
            for y in range(SIZE)
            for x in range(SIZE)
            for population in range(9)
        )
        passed = bool(
            state.shape == (SIZE, SIZE, 9)
            and conserved == expected_conserved
            and maximum_deviation < state_radius
            and minimum_population > 0
            and minimum_density > 0
        )
        records.append(
            {
                "name": name,
                "shape": list(state.shape),
                "global_conserved": _conserved_record(conserved),
                "fixed_leaf_exact": conserved == expected_conserved,
                "maximum_component_deviation": _fraction_record(
                    maximum_deviation
                ),
                "registered_component_radius": _fraction_record(state_radius),
                "component_box_strict": maximum_deviation < state_radius,
                "minimum_population": _fraction_record(minimum_population),
                "minimum_density": _fraction_record(minimum_density),
                "nonzero_perturbation_count": nonzero_perturbations,
                "passed": passed,
            }
        )
    digest = _probe_digest(probes)
    passed = bool(
        [name for name, _ in probes] == list(PROBE_NAMES)
        and len(records) == 4
        and all(record["passed"] for record in records)
    )
    return {
        "delta": _fraction_record(PROBE_DELTA),
        "registered_names": list(PROBE_NAMES),
        "probe_count": len(probes),
        "probe_digest_sha256": digest,
        "probes": records,
        "passed": passed,
    }, probes


def _exact_local_stages(
    populations: tuple[Fraction, ...],
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    density = sum(populations, Fraction(0))
    momentum = tuple(
        sum(
            (
                populations[population]
                * backend.D2Q9_INTEGER_VELOCITIES[population][dimension]
                for population in range(9)
            ),
            Fraction(0),
        )
        for dimension in range(2)
    )
    velocity = (momentum[0] / density, momentum[1] / density)
    speed_squared = velocity[0] ** 2 + velocity[1] ** 2
    equilibria = []
    collisions = []
    for population, (cx, cy) in enumerate(
        backend.D2Q9_INTEGER_VELOCITIES
    ):
        dot = cx * velocity[0] + cy * velocity[1]
        equilibrium = (
            density
            * backend.D2Q9_EXACT_WEIGHTS[population]
            * (
                1
                + 3 * dot
                + Fraction(9, 2) * dot**2
                - Fraction(3, 2) * speed_squared
            )
        )
        equilibria.append(equilibrium)
        collisions.append(
            populations[population]
            + backend.EXACT_OMEGA
            * (equilibrium - populations[population])
        )
    return tuple(equilibria), tuple(collisions)


def _exact_stages(state: ExactArray) -> dict[str, ExactArray]:
    ny, nx, _ = state.shape
    equilibrium = np.empty(state.shape, dtype=object)
    collision = np.empty(state.shape, dtype=object)
    cache: dict[
        tuple[Fraction, ...],
        tuple[tuple[Fraction, ...], tuple[Fraction, ...]],
    ] = {}
    for y in range(ny):
        for x in range(nx):
            populations = tuple(
                Fraction(state[y, x, population])
                for population in range(9)
            )
            local = cache.get(populations)
            if local is None:
                local = _exact_local_stages(populations)
                cache[populations] = local
            equilibrium[y, x, :] = local[0]
            collision[y, x, :] = local[1]

    streamed = np.empty(state.shape, dtype=object)
    for y in range(ny):
        for x in range(nx):
            for population, (cx, cy) in enumerate(
                backend.D2Q9_INTEGER_VELOCITIES
            ):
                streamed[
                    (y + cy) % ny,
                    (x + cx) % nx,
                    population,
                ] = collision[y, x, population]

    filtered = np.empty(state.shape, dtype=object)
    for y in range(ny):
        for x in range(nx):
            for population in range(9):
                neighbours = (
                    streamed[(y - 1) % ny, x, population]
                    + streamed[(y + 1) % ny, x, population]
                    + streamed[y, (x - 1) % nx, population]
                    + streamed[y, (x + 1) % nx, population]
                )
                filtered[y, x, population] = (
                    (1 - backend.EXACT_ETA)
                    * streamed[y, x, population]
                    + backend.EXACT_ETA / 4 * neighbours
                )
    return {
        "equilibrium": equilibrium,
        "post_collision": collision,
        "post_streaming": streamed,
        "post_filter": filtered,
    }


def _rounded_result(
    operation: str,
    operands: tuple[Fraction, ...],
) -> Fraction:
    if operation in {"constant_rounding", "input_rounding"}:
        exact = operands[0]
    elif operation in {"constant_subtraction", "binary_subtraction"}:
        exact = operands[0] - operands[1]
    elif operation in {"constant_division", "binary_division"}:
        exact = operands[0] / operands[1]
    elif operation in {"binary_addition", "reduction_addition"}:
        exact = operands[0] + operands[1]
    elif operation == "binary_multiplication":
        exact = operands[0] * operands[1]
    elif operation == "exact_identity":
        return operands[0]
    elif operation == "exact_negation":
        return -operands[0]
    elif operation == "exact_zero":
        return Fraction(0)
    else:
        raise ValueError(f"unregistered trace operation: {operation}")
    return q007w._round_to_binary_precision(exact, 85)


@dataclass
class TraceOracle:
    digest: Any = field(default_factory=hashlib.sha256)
    operation_counts: dict[str, int] = field(default_factory=dict)
    record_count: int = 0
    mismatch_count: int = 0
    first_mismatch: dict[str, Any] | None = None

    def __call__(
        self,
        operation: str,
        operands: tuple[Fraction, ...],
        result: Fraction,
    ) -> None:
        expected = _rounded_result(operation, operands)
        self.record_count += 1
        self.operation_counts[operation] = (
            self.operation_counts.get(operation, 0) + 1
        )
        self.digest.update(operation.encode("ascii"))
        self.digest.update(b"\0")
        for operand in operands:
            self.digest.update(_canonical_fraction(operand).encode("ascii"))
            self.digest.update(b";")
        self.digest.update(b"\0")
        self.digest.update(_canonical_fraction(result).encode("ascii"))
        self.digest.update(b"\n")
        if result != expected:
            self.mismatch_count += 1
            if self.first_mismatch is None:
                self.first_mismatch = {
                    "operation": operation,
                    "operands": [
                        _fraction_record(operand) for operand in operands
                    ],
                    "result": _fraction_record(result),
                    "expected": _fraction_record(expected),
                }

    @property
    def hexdigest(self) -> str:
        return self.digest.hexdigest()


def _stage_comparison(
    observed: np.ndarray,
    exact: ExactArray,
    error_bound: Fraction,
) -> dict[str, Any]:
    maximum_error = Fraction(0)
    maximum_index = (0, 0, 0)
    minimum_population: Fraction | None = None
    digest = hashlib.sha256()
    for index in np.ndindex(observed.shape):
        observed_fraction = backend.fraction_from_mpfr(observed[index])
        exact_fraction = Fraction(exact[index])
        error = abs(observed_fraction - exact_fraction)
        if error > maximum_error:
            maximum_error = error
            maximum_index = index
        minimum_population = (
            observed_fraction
            if minimum_population is None
            else min(minimum_population, observed_fraction)
        )
        digest.update(
            (
                f"{index[0]},{index[1]},{index[2]}:"
                f"{_canonical_fraction(observed_fraction)}\n"
            ).encode("ascii")
        )
    if minimum_population is None:
        raise RuntimeError("empty stage")
    return {
        "maximum_observed_component_error": _fraction_record(maximum_error),
        "registered_component_error_upper": _fraction_record(error_bound),
        "error_bound_utilization": _fraction_record(
            maximum_error / error_bound
        ),
        "maximum_error_index": list(maximum_index),
        "error_enclosed": maximum_error <= error_bound,
        "minimum_mpfr_population": _fraction_record(minimum_population),
        "strictly_positive": minimum_population > 0,
        "stage_digest_sha256": digest.hexdigest(),
        "passed": bool(maximum_error <= error_bound and minimum_population > 0),
    }


def _constant_algebra_audit(
    constants: backend.MPFRConstants,
    q007w_exact: dict[str, Any],
) -> dict[str, Any]:
    weights = tuple(
        backend.fraction_from_mpfr(value) for value in constants.weights
    )
    eta = backend.fraction_from_mpfr(constants.eta)
    center = backend.fraction_from_mpfr(constants.filter_center)
    neighbour = backend.fraction_from_mpfr(constants.filter_neighbour)
    weight_sum_defect = sum(weights, Fraction(0)) - 1
    weight_momentum_x = sum(
        (
            weights[index] * backend.D2Q9_INTEGER_VELOCITIES[index][0]
            for index in range(9)
        ),
        Fraction(0),
    )
    weight_momentum_y = sum(
        (
            weights[index] * backend.D2Q9_INTEGER_VELOCITIES[index][1]
            for index in range(9)
        ),
        Fraction(0),
    )
    filter_partition_defect = center + 4 * neighbour - 1
    registered = q007w_exact["rounded_constants"]
    registered_weights = tuple(
        _fraction_from_record(record) for record in registered["weights"]
    )
    constants_match = bool(
        weights == registered_weights
        and eta == _fraction_from_record(registered["eta"])
        and center == _fraction_from_record(registered["filter_center"])
        and neighbour
        == _fraction_from_record(registered["filter_neighbour"])
    )
    passed = bool(
        constants_match
        and weight_sum_defect != 0
        and weight_momentum_x == 0
        and weight_momentum_y == 0
        and filter_partition_defect != 0
    )
    return {
        "constants_match_q007w_selected_candidate": constants_match,
        "weight_sum_defect": _fraction_record(weight_sum_defect),
        "weight_momentum_x_defect": _fraction_record(weight_momentum_x),
        "weight_momentum_y_defect": _fraction_record(weight_momentum_y),
        "filter_partition_of_unity_defect": _fraction_record(
            filter_partition_defect
        ),
        "rest_grid_encoding_mass_defect_prediction": _fraction_record(
            WAVE_COUNT * weight_sum_defect
        ),
        "rounded_eta": _fraction_record(eta),
        "rounded_filter_center": _fraction_record(center),
        "rounded_filter_neighbour": _fraction_record(neighbour),
        "nonzero_mass_and_filter_obstructions_reproduced": passed,
        "passed": passed,
    }


def _evaluate_probe(
    name: str,
    state: ExactArray,
    q007w_exact: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, bool]]:
    trace = TraceOracle()
    concrete = backend.MPFRD2Q9Backend(trace=trace)
    stages = concrete.evaluate_fraction_stages(state)
    exact_stages = _exact_stages(state)
    observed_stages = {
        "equilibrium": stages.equilibrium,
        "post_collision": stages.post_collision,
        "post_streaming": stages.post_streaming,
        "post_filter": stages.post_filter,
    }
    comparisons = {
        stage_name: _stage_comparison(
            observed,
            exact_stages[stage_name],
            q007w_exact["stage_error_bounds"][stage_name],
        )
        for stage_name, observed in observed_stages.items()
    }

    exact_input_conserved = _global_conserved(state)
    encoded_conserved = _global_conserved(
        _mpfr_to_fraction_array(stages.encoded_input)
    )
    collision_conserved = _global_conserved(
        _mpfr_to_fraction_array(stages.post_collision)
    )
    streaming_conserved = _global_conserved(
        _mpfr_to_fraction_array(stages.post_streaming)
    )
    filter_conserved = _global_conserved(
        _mpfr_to_fraction_array(stages.post_filter)
    )
    encoding_defect = _difference(encoded_conserved, exact_input_conserved)
    collision_defect = _difference(collision_conserved, encoded_conserved)
    streaming_defect = _difference(streaming_conserved, collision_conserved)
    filter_defect = _difference(filter_conserved, streaming_conserved)
    full_step_defect = _difference(filter_conserved, encoded_conserved)
    conservation_flags = {
        "encoding_exact": _all_zero(encoding_defect),
        "collision_exact": _all_zero(collision_defect),
        "streaming_exact": _all_zero(streaming_defect),
        "filter_exact": _all_zero(filter_defect),
        "full_step_exact": _all_zero(full_step_defect),
    }
    expected_counts = backend.expected_operation_counts(WAVE_COUNT)
    dangerous_flags_clear = not any(
        stages.context_flags[name]
        for name in (
            "underflow",
            "overflow",
            "invalid",
            "division_by_zero",
            "erange",
        )
    )
    trace_passed = bool(
        trace.record_count == EXPECTED_TOTAL_TRACE_PER_PROBE
        and stages.trace_record_count == EXPECTED_MAP_TRACE_COUNT
        and trace.mismatch_count == 0
    )
    operation_passed = bool(
        stages.operation_counts == expected_counts
        and stages.minimum_density_divisor > 0
        and stages.all_results_finite
        and dangerous_flags_clear
    )
    stage_passed = all(
        comparison["passed"] for comparison in comparisons.values()
    )
    record = {
        "name": name,
        "trace": {
            "record_count": trace.record_count,
            "expected_record_count": EXPECTED_TOTAL_TRACE_PER_PROBE,
            "map_record_count": stages.trace_record_count,
            "expected_map_record_count": EXPECTED_MAP_TRACE_COUNT,
            "operation_kind_counts": trace.operation_counts,
            "mismatch_count": trace.mismatch_count,
            "first_mismatch": trace.first_mismatch,
            "trace_digest_sha256": trace.hexdigest,
            "passed": trace_passed,
        },
        "operation_domain": {
            "operation_counts": stages.operation_counts,
            "expected_operation_counts": expected_counts,
            "operation_counts_match": stages.operation_counts
            == expected_counts,
            "minimum_density_divisor": _fraction_record(
                stages.minimum_density_divisor
            ),
            "maximum_intermediate_magnitude": _fraction_record(
                stages.maximum_intermediate_magnitude
            ),
            "all_results_finite": stages.all_results_finite,
            "context_flags": stages.context_flags,
            "dangerous_flags_clear": dangerous_flags_clear,
            "passed": operation_passed,
        },
        "stage_comparisons": comparisons,
        "all_stage_bounds_and_positivity_pass": stage_passed,
        "conservation": {
            "exact_input": _conserved_record(exact_input_conserved),
            "encoded_input": _conserved_record(encoded_conserved),
            "post_collision": _conserved_record(collision_conserved),
            "post_streaming": _conserved_record(streaming_conserved),
            "post_filter": _conserved_record(filter_conserved),
            "encoding_minus_exact_input": _conserved_record(encoding_defect),
            "collision_minus_encoded_input": _conserved_record(
                collision_defect
            ),
            "streaming_minus_collision": _conserved_record(streaming_defect),
            "filter_minus_streaming": _conserved_record(filter_defect),
            "post_filter_minus_encoded_input": _conserved_record(
                full_step_defect
            ),
            **conservation_flags,
        },
        "passed": bool(trace_passed and operation_passed and stage_passed),
    }
    return record, conservation_flags


def _backend_campaign(
    probes: list[tuple[str, ExactArray]],
    q007w_exact: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, bool]]:
    before = _context_signature(gmpy2.get_context())
    records = []
    flags_by_probe = {}
    for name, state in probes:
        record, flags = _evaluate_probe(name, state, q007w_exact)
        records.append(record)
        flags_by_probe[name] = flags
    after = _context_signature(gmpy2.get_context())
    trace_digest = _digest_payload(
        [
            {
                "name": record["name"],
                "trace": record["trace"]["trace_digest_sha256"],
            }
            for record in records
        ]
    )
    result_digest = _digest_payload(records)
    summary_flags = {
        "all_traces_match": all(
            record["trace"]["passed"] for record in records
        ),
        "all_operation_domains_pass": all(
            record["operation_domain"]["passed"] for record in records
        ),
        "all_stage_bounds_and_positivity_pass": all(
            record["all_stage_bounds_and_positivity_pass"]
            for record in records
        ),
        "all_encodings_conserve": all(
            flags["encoding_exact"] for flags in flags_by_probe.values()
        ),
        "all_collisions_conserve": all(
            flags["collision_exact"] for flags in flags_by_probe.values()
        ),
        "all_streaming_conserves": all(
            flags["streaming_exact"] for flags in flags_by_probe.values()
        ),
        "all_filters_conserve": all(
            flags["filter_exact"] for flags in flags_by_probe.values()
        ),
        "all_full_steps_conserve": all(
            flags["full_step_exact"] for flags in flags_by_probe.values()
        ),
        "context_restored": before == after,
    }
    passed = bool(
        summary_flags["all_traces_match"]
        and summary_flags["all_operation_domains_pass"]
        and summary_flags["all_stage_bounds_and_positivity_pass"]
        and summary_flags["context_restored"]
    )
    return {
        "probe_count": len(records),
        "expected_trace_records_per_probe": EXPECTED_TOTAL_TRACE_PER_PROBE,
        "expected_map_trace_records_per_probe": EXPECTED_MAP_TRACE_COUNT,
        "aggregate_trace_digest_sha256": trace_digest,
        "result_digest_sha256": result_digest,
        "summary": summary_flags,
        "probes": records,
        "passed": passed,
    }, summary_flags


def run_mpfr_fixed_leaf_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    _q007w_payload, input_record, q007w_exact = _load_registered_q007w(
        directory
    )
    source_audit = _source_audit(q007w_exact)
    context_audit = _context_audit()
    probe_audit, probes = _probe_registration_audit(
        q007w_exact["state_radius"]
    )
    constant_audit = _constant_algebra_audit(
        backend.MPFRD2Q9Backend().constants,
        q007w_exact,
    )
    campaign, conservation = _backend_campaign(probes, q007w_exact)

    trace_passed = campaign["summary"]["all_traces_match"]
    operation_passed = campaign["summary"]["all_operation_domains_pass"]
    stage_passed = campaign["summary"][
        "all_stage_bounds_and_positivity_pass"
    ]
    q007w_reentry_passed = bool(
        q007w_exact["base_error"] < q007w_exact["base_margin"]
        and q007w_exact["normal_error"] < q007w_exact["normal_margin"]
    )
    semantic_bridge_passed = bool(
        source_audit["passed"]
        and context_audit["passed"]
        and trace_passed
        and operation_passed
    )
    one_step_bound_passed = bool(
        semantic_bridge_passed
        and stage_passed
        and q007w_reentry_passed
    )

    preliminary_sections = {
        "input_artifact": input_record,
        "source_audit": source_audit,
        "context_audit": context_audit,
        "probe_registration": probe_audit,
        "constant_algebra": constant_audit,
        "backend_campaign": campaign,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(preliminary_sections)
        and _strict_json_serializable(preliminary_sections)
    )
    digest_reproducible = bool(
        len(probe_audit["probe_digest_sha256"]) == 64
        and len(campaign["aggregate_trace_digest_sha256"]) == 64
        and len(campaign["result_digest_sha256"]) == 64
    )
    validity_gates = {
        "registered_q007w_input": {
            "passed": input_record["passed"],
            "threshold": (
                "registered artifact/runner SHA, source, scope, all 7+6 "
                "gates, p*=85, p=84 boundary, and transitive inputs match"
            ),
            "value": input_record["passed"],
        },
        "registered_mpfr_context": {
            "passed": context_audit["passed"],
            "threshold": (
                "gmpy2/MPFR/GMP versions, 85-bit nearest-even context, "
                "exponent/subnormal/trap settings, and restoration match"
            ),
            "value": context_audit["passed"],
        },
        "registered_backend_sources": {
            "passed": source_audit["passed"],
            "threshold": (
                "backend, pyproject, D2Q9, and filter SHA plus dependency "
                "and explicit operation schedule match"
            ),
            "value": source_audit["passed"],
        },
        "registered_fixed_leaf_probes": {
            "passed": probe_audit["passed"],
            "threshold": (
                "all 4 exact recipes cancel global conserved moments, lie "
                "strictly in the registered component box, and stay positive"
            ),
            "value": probe_audit["passed"],
        },
        "operationwise_ties_to_even_trace": {
            "passed": trace_passed,
            "threshold": (
                "every constant, input, exact sign, reduction, and binary "
                "operation matches the Q007w exact p=85 oracle bitwise"
            ),
            "value": {
                "all_traces_match": trace_passed,
                "digest": campaign["aggregate_trace_digest_sha256"],
            },
        },
        "operation_schedule_and_domain": {
            "passed": operation_passed,
            "threshold": (
                "per-site Q007w counts scale to 289 sites, divisors are "
                "positive, results finite, and dangerous MPFR flags clear"
            ),
            "value": operation_passed,
        },
        "q007w_stage_enclosure_replay": {
            "passed": stage_passed,
            "threshold": (
                "all exact-Fraction stage discrepancies are enclosed by "
                "the selected Q007w component bounds and populations positive"
            ),
            "value": stage_passed,
        },
        "finite_strict_json_and_digests": {
            "passed": bool(finite_strict_json and digest_reproducible),
            "threshold": (
                "all records are finite strict JSON and probe/trace/result "
                "digests are present"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "digest_reproducible": digest_reproducible,
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )
    hypothesis_gates = {
        "mpfr_backend_realizes_q007w_85bit_semantics": {
            "passed": bool(validity_passed and semantic_bridge_passed),
            "threshold": (
                "registered context/source plus every traced operation match "
                "the ideal p=85 semantics"
            ),
            "value": semantic_bridge_passed,
        },
        "q007w_one_step_bounds_apply_to_backend": {
            "passed": bool(validity_passed and one_step_bound_passed),
            "threshold": (
                "all concrete stage errors/positivity and Q007w base/normal "
                "strict re-entry bounds pass"
            ),
            "value": one_step_bound_passed,
        },
        "componentwise_encoding_preserves_fixed_leaf": {
            "passed": bool(
                validity_passed
                and conservation["all_encodings_conserve"]
            ),
            "threshold": (
                "exact rational and componentwise MPFR input have identical "
                "M, Px, Py on all 4 probes"
            ),
            "value": conservation["all_encodings_conserve"],
        },
        "collision_preserves_fixed_leaf": {
            "passed": bool(
                validity_passed
                and conservation["all_collisions_conserve"]
            ),
            "threshold": (
                "post-collision and encoded input have identical M, Px, Py "
                "on all 4 probes"
            ),
            "value": conservation["all_collisions_conserve"],
        },
        "streaming_and_filter_preserve_fixed_leaf": {
            "passed": bool(
                validity_passed
                and conservation["all_streaming_conserves"]
                and conservation["all_filters_conserve"]
                and conservation["all_full_steps_conserve"]
            ),
            "threshold": (
                "streaming equals collision and filter/full step conserve "
                "M, Px, Py exactly on all 4 probes"
            ),
            "value": {
                "streaming": conservation["all_streaming_conserves"],
                "filter": conservation["all_filters_conserve"],
                "full_step": conservation["all_full_steps_conserve"],
            },
        },
        "fixed_leaf_all_iterate_induction_closes": {
            "passed": False,
            "threshold": (
                "all five preceding semantic, bound, encoding, collision, "
                "and streaming/filter hypotheses pass"
            ),
            "value": False,
        },
    }
    first_five_pass = all(
        gate["passed"]
        for name, gate in hypothesis_gates.items()
        if name != "fixed_leaf_all_iterate_induction_closes"
    )
    hypothesis_gates["fixed_leaf_all_iterate_induction_closes"][
        "passed"
    ] = bool(validity_passed and first_five_pass)
    hypothesis_gates["fixed_leaf_all_iterate_induction_closes"][
        "value"
    ] = bool(validity_passed and first_five_pass)
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007x MPFR fixed-leaf audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered MPFR-85 backend closes the Q007w roundoff-robust "
            "fixed-leaf induction"
        )
    elif (
        hypothesis_gates[
            "mpfr_backend_realizes_q007w_85bit_semantics"
        ]["passed"]
        and hypothesis_gates[
            "q007w_one_step_bounds_apply_to_backend"
        ]["passed"]
    ):
        outcome = "not_certified"
        classification = (
            "MPFR-85 realizes the Q007w one-step arithmetic bound but not "
            "the fixed conservation leaf"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered MPFR-85 backend does not realize the Q007w "
            "one-step arithmetic bridge"
        )

    return {
        "question": (
            "Does a fixed gmpy2/MPFR 85-bit backend realize Q007w operation "
            "semantics and preserve the exact fixed conservation leaf needed "
            "to iterate its re-entry conclusion?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "wave_count": WAVE_COUNT,
            "precision_bits": backend.MPFR_PRECISION_BITS,
            "emin": backend.MPFR_EMIN,
            "emax": backend.MPFR_EMAX,
            "rounding": backend.MPFR_ROUNDING_NAME,
            "omega": _fraction_record(backend.EXACT_OMEGA),
            "eta": _fraction_record(backend.EXACT_ETA),
            "probe_delta": _fraction_record(PROBE_DELTA),
            "probe_names": list(PROBE_NAMES),
            "expected_construction_trace_count": (
                EXPECTED_CONSTRUCTION_TRACE_COUNT
            ),
            "expected_map_trace_per_site": EXPECTED_MAP_TRACE_PER_SITE,
            "expected_map_trace_count": EXPECTED_MAP_TRACE_COUNT,
        },
        "input_artifact": input_record,
        "source_audit": source_audit,
        "context_audit": context_audit,
        "probe_registration": probe_audit,
        "constant_algebra": constant_audit,
        "backend_campaign": campaign,
        "q007w_reentry_bridge": {
            "base_error": _fraction_record(q007w_exact["base_error"]),
            "base_margin": _fraction_record(q007w_exact["base_margin"]),
            "normal_error": _fraction_record(q007w_exact["normal_error"]),
            "normal_margin": _fraction_record(q007w_exact["normal_margin"]),
            "strict_base_and_normal_reentry": q007w_reentry_passed,
            "semantic_bridge_passed": semantic_bridge_passed,
            "one_step_bound_passed": one_step_bound_passed,
        },
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "concrete_backend_realizes_q007w_85bit_semantics": bool(
                validity_passed and semantic_bridge_passed
            ),
            "concrete_backend_one_step_stages_strictly_positive": bool(
                validity_passed and one_step_bound_passed
            ),
            "componentwise_encoding_preserves_fixed_conservation_leaf": bool(
                validity_passed and conservation["all_encodings_conserve"]
            ),
            "one_step_backend_preserves_fixed_conservation_leaf": bool(
                validity_passed
                and conservation["all_collisions_conserve"]
                and conservation["all_streaming_conserves"]
                and conservation["all_filters_conserve"]
                and conservation["all_full_steps_conserve"]
            ),
            "all_iterate_mpfr85_q007s_tube_invariance": bool(
                validity_passed and hypotheses_passed
            ),
        },
        "claim_boundary": (
            "The operationwise bridge and finite exact probes validate the "
            "registered MPFR-85 implementation and one-step Q007w enclosure. "
            "They do not turn finite conservation probes into a tube-wide "
            "sampling proof. If encoding or the map fails exact M/Px/Py "
            "preservation, the fixed-leaf induction is not certified even "
            "when complement-coordinate errors fit the Q007w margins. No "
            "performance, multi-step trajectory, GPU, threaded reduction, "
            "other MPFR build, or D3Q27 claim is made."
        ),
        "preserved_prior_outcomes": {
            "q007w_ideal_precision_acceptance_changed": False,
            "q007v_binary64_reentry_rejection_changed": False,
            "q007u_exact_stagewise_acceptance_changed": False,
            "q007s_exact_fixed_leaf_invariance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If fixed-leaf closure fails while the semantic bridge passes, "
            "preregister a conservation-exact encoding and post-stage repair "
            "that preserves the Q007w error budget, then audit it separately."
        ),
    }


def run_q007x_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_mpfr_fixed_leaf_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": {
            **runtime_metadata(),
            **backend.backend_runtime_metadata(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "concrete MPFR-85 operation bridge and fixed-leaf closure audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(backend.EXACT_OMEGA),
            "eta": float(backend.EXACT_ETA),
            "conservation_treatment": (
                "exact global mass and momentum equality on the fixed leaf"
            ),
            "input_encoding": (
                "Fraction to exact mpq to 85-bit MPFR componentwise rounding"
            ),
            "rounding_model": (
                "gmpy2 2.3.1 with MPFR 4.2.2 round-to-nearest ties-to-even"
            ),
            "claim": (
                "separate operation-semantic, one-step-bound, and exact "
                "fixed-leaf closure decisions for the registered backend"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q007x_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
