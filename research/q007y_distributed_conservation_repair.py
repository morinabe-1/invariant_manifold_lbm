"""Sealed Q007y distributed dyadic conservation-repair audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np

import research.q007w_ideal_precision_threshold as q007w
import research.q007x_mpfr_backend as backend
import research.q007x_mpfr_fixed_leaf as q007x
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = q007x.SIZE
WAVE_COUNT = SIZE * SIZE
REPAIR_QUANTUM = Fraction(1, 2**90)
DIAGONAL_POPULATIONS = (5, 6, 7, 8)
DIAGONAL_BIN_LOWER = Fraction(1, 2**6)
DIAGONAL_BIN_UPPER = Fraction(1, 2**5)
TARGET_CONSERVED = (Fraction(WAVE_COUNT), Fraction(0), Fraction(0))

Q007X_ARTIFACT = "q007x_mpfr_fixed_leaf.json"
REGISTERED_Q007X_ARTIFACT_SHA256 = (
    "20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566"
)
REGISTERED_Q007X_RUNNER_SHA256 = (
    "de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b"
)
REGISTERED_Q007X_BACKEND_SHA256 = (
    "25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc"
)
REGISTERED_Q007X_PROBE_DIGEST = (
    "a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329"
)

ExactArray = np.ndarray
MPFRArray = np.ndarray


@dataclass(frozen=True)
class DiagonalRepairSolution:
    """Integer Hadamard solution for populations 5 through 8."""

    mass_units: int
    momentum_x_units: int
    momentum_y_units: int
    free_unit: int
    diagonal_units: tuple[int, int, int, int]
    objective: tuple[int, int, int, int]
    search_limit: int


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _digest_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_fraction(value: Fraction) -> str:
    return f"{value.numerator:x}/{value.denominator:x}"


def _ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _require_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def solve_diagonal_repair_units(
    mass_units: int,
    momentum_x_units: int,
    momentum_y_units: int,
) -> DiagonalRepairSolution:
    """Solve the preregistered integer Hadamard repair problem."""

    mass_units = _require_integer(mass_units, "mass_units")
    momentum_x_units = _require_integer(
        momentum_x_units,
        "momentum_x_units",
    )
    momentum_y_units = _require_integer(
        momentum_y_units,
        "momentum_y_units",
    )
    if not (
        (mass_units - momentum_x_units) % 2 == 0
        and (mass_units - momentum_y_units) % 2 == 0
    ):
        raise ValueError("mass and momentum repair units must have one parity")

    search_limit = (
        abs(mass_units)
        + abs(momentum_x_units)
        + abs(momentum_y_units)
        + 4
    )
    best: tuple[
        tuple[int, int, int, int],
        int,
        tuple[int, int, int, int],
    ] | None = None
    for free_unit in range(-search_limit, search_limit + 1):
        numerators = (
            mass_units + momentum_x_units + momentum_y_units + free_unit,
            mass_units - momentum_x_units + momentum_y_units - free_unit,
            mass_units - momentum_x_units - momentum_y_units + free_unit,
            mass_units + momentum_x_units - momentum_y_units - free_unit,
        )
        if any(numerator % 4 for numerator in numerators):
            continue
        diagonal_units = tuple(numerator // 4 for numerator in numerators)
        objective = (
            sum(abs(value) for value in diagonal_units),
            max(abs(value) for value in diagonal_units),
            abs(free_unit),
            free_unit,
        )
        candidate = (objective, free_unit, diagonal_units)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:  # pragma: no cover - parity is sufficient
        raise RuntimeError("no compatible diagonal repair solution")

    objective, free_unit, diagonal_units = best
    a, b, c, d = diagonal_units
    reproduced = (
        a + b + c + d,
        a - b - c + d,
        a + b - c - d,
    )
    requested = (mass_units, momentum_x_units, momentum_y_units)
    if reproduced != requested:  # pragma: no cover - algebraic guard
        raise RuntimeError("diagonal repair does not reproduce its moments")
    registered_l1_upper = (
        abs(mass_units)
        + abs(momentum_x_units)
        + abs(momentum_y_units)
        + 2
    )
    if objective[0] > registered_l1_upper:  # pragma: no cover
        raise RuntimeError("diagonal repair violates the registered l1 bound")
    return DiagonalRepairSolution(
        mass_units=mass_units,
        momentum_x_units=momentum_x_units,
        momentum_y_units=momentum_y_units,
        free_unit=free_unit,
        diagonal_units=diagonal_units,
        objective=objective,
        search_limit=search_limit,
    )


def balanced_unit_distribution(total_units: int, site_count: int) -> tuple[int, ...]:
    """Distribute an integer over row-major sites with spread at most one."""

    total_units = _require_integer(total_units, "total_units")
    site_count = _require_integer(site_count, "site_count")
    if site_count <= 0:
        raise ValueError("site_count must be positive")
    quotient, remainder = divmod(total_units, site_count)
    values = (quotient + 1,) * remainder + (quotient,) * (
        site_count - remainder
    )
    if sum(values) != total_units:  # pragma: no cover
        raise RuntimeError("balanced distribution changed the total")
    if max(values) - min(values) > 1:  # pragma: no cover
        raise RuntimeError("balanced distribution spread exceeds one")
    return values


def _global_conserved_mpfr(
    state: MPFRArray,
) -> tuple[Fraction, Fraction, Fraction]:
    return q007x._global_conserved(q007x._mpfr_to_fraction_array(state))


def _difference(
    current: tuple[Fraction, Fraction, Fraction],
    reference: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(current[index] - reference[index] for index in range(3))


def _conserved_record(
    values: tuple[Fraction, Fraction, Fraction],
) -> dict[str, dict[str, Any]]:
    return {
        name: _fraction_record(value)
        for name, value in zip(("mass", "momentum_x", "momentum_y"), values)
    }


def _integer_units(value: Fraction) -> int:
    units = value / REPAIR_QUANTUM
    if units.denominator != 1:
        raise ValueError("conservation defect is not on the repair lattice")
    return units.numerator


def _context_flags(context: gmpy2.context) -> dict[str, bool]:
    return {
        "underflow": bool(context.underflow),
        "overflow": bool(context.overflow),
        "invalid": bool(context.invalid),
        "division_by_zero": bool(context.divzero),
        "inexact": bool(context.inexact),
        "erange": bool(context.erange),
    }


def repair_conserved_state(
    state: MPFRArray,
    target: tuple[Fraction, Fraction, Fraction] = TARGET_CONSERVED,
) -> tuple[MPFRArray, dict[str, Any]]:
    """Apply the registered diagonal repair to an encoded MPFR state."""

    array = np.asarray(state, dtype=object)
    if array.shape != (SIZE, SIZE, 9):
        raise ValueError("repair requires the registered 17x17 D2Q9 state")
    for value in array.flat:
        if not isinstance(value, gmpy2.mpfr):
            raise TypeError("repair state values must be gmpy2.mpfr")
        if value.precision != backend.MPFR_PRECISION_BITS:
            raise ValueError("repair state values must have 85-bit precision")

    raw_conserved = _global_conserved_mpfr(array)
    defect = _difference(raw_conserved, target)
    requested_units = tuple(_integer_units(-value) for value in defect)
    solution = solve_diagonal_repair_units(*requested_units)
    output = array.copy()
    distributions = {
        population: balanced_unit_distribution(total, WAVE_COUNT)
        for population, total in zip(
            DIAGONAL_POPULATIONS,
            solution.diagonal_units,
            strict=True,
        )
    }

    digest = hashlib.sha256()
    addition_count = 0
    exact_addition_count = 0
    same_binade_count = 0
    positive_count = 0
    maximum_component_correction = Fraction(0)
    minimum_repaired_population: Fraction | None = None
    with backend.mpfr_context() as context:
        for population in DIAGONAL_POPULATIONS:
            distribution = distributions[population]
            for site, units in enumerate(distribution):
                y, x = divmod(site, SIZE)
                correction = units * REPAIR_QUANTUM
                correction_mpfr = gmpy2.mpfr(
                    gmpy2.mpq(correction.numerator, correction.denominator)
                )
                before = output[y, x, population]
                before_fraction = backend.fraction_from_mpfr(before)
                after = before + correction_mpfr
                after_fraction = backend.fraction_from_mpfr(after)
                expected = before_fraction + correction
                correction_exact = (
                    backend.fraction_from_mpfr(correction_mpfr) == correction
                )
                addition_exact = after_fraction == expected
                same_binade = bool(
                    DIAGONAL_BIN_LOWER <= before_fraction < DIAGONAL_BIN_UPPER
                    and DIAGONAL_BIN_LOWER <= after_fraction < DIAGONAL_BIN_UPPER
                )
                positive = after_fraction > 0
                output[y, x, population] = after
                addition_count += 1
                exact_addition_count += int(correction_exact and addition_exact)
                same_binade_count += int(same_binade)
                positive_count += int(positive)
                maximum_component_correction = max(
                    maximum_component_correction,
                    abs(correction),
                )
                minimum_repaired_population = (
                    after_fraction
                    if minimum_repaired_population is None
                    else min(minimum_repaired_population, after_fraction)
                )
                digest.update(
                    f"{population},{y},{x}:{units}\n".encode("ascii")
                )
        flags = _context_flags(context)

    repaired_conserved = _global_conserved_mpfr(output)
    repaired_defect = _difference(repaired_conserved, target)
    physical_l1 = REPAIR_QUANTUM * sum(
        abs(value) for value in solution.diagonal_units
    )
    registered_l1_upper = (
        sum((abs(value) for value in defect), Fraction(0))
        + 2 * REPAIR_QUANTUM
    )
    distribution_records = []
    for population in DIAGONAL_POPULATIONS:
        values = distributions[population]
        quotient, remainder = divmod(
            solution.diagonal_units[population - DIAGONAL_POPULATIONS[0]],
            WAVE_COUNT,
        )
        distribution_records.append(
            {
                "population": population,
                "total_units": sum(values),
                "quotient": quotient,
                "remainder": remainder,
                "minimum_site_units": min(values),
                "maximum_site_units": max(values),
                "spread_at_most_one": max(values) - min(values) <= 1,
            }
        )
    dangerous_flags_clear = not any(
        flags[name]
        for name in (
            "underflow",
            "overflow",
            "invalid",
            "division_by_zero",
            "erange",
        )
    )
    solver_passed = bool(
        physical_l1 <= registered_l1_upper
        and all(
            record["total_units"] == solution.diagonal_units[index]
            and record["spread_at_most_one"]
            for index, record in enumerate(distribution_records)
        )
    )
    operation_passed = bool(
        addition_count == 4 * WAVE_COUNT
        and exact_addition_count == addition_count
        and same_binade_count == addition_count
        and positive_count == addition_count
        and dangerous_flags_clear
        and not flags["inexact"]
    )
    conservation_passed = all(value == 0 for value in repaired_defect)
    return output, {
        "target": _conserved_record(target),
        "raw_conserved": _conserved_record(raw_conserved),
        "raw_minus_target": _conserved_record(defect),
        "requested_units": {
            name: value
            for name, value in zip(
                ("mass", "momentum_x", "momentum_y"),
                requested_units,
            )
        },
        "solution": {
            "free_unit": solution.free_unit,
            "diagonal_units": list(solution.diagonal_units),
            "objective": list(solution.objective),
            "search_limit": solution.search_limit,
            "hadamard_moments_reproduced": True,
        },
        "distributions": distribution_records,
        "distribution_digest_sha256": digest.hexdigest(),
        "physical_l1": _fraction_record(physical_l1),
        "registered_l1_upper": _fraction_record(registered_l1_upper),
        "l1_bound_passed": physical_l1 <= registered_l1_upper,
        "maximum_component_correction": _fraction_record(
            maximum_component_correction
        ),
        "addition_count": addition_count,
        "exact_addition_count": exact_addition_count,
        "same_binade_count": same_binade_count,
        "strict_positive_count": positive_count,
        "minimum_repaired_population": _fraction_record(
            minimum_repaired_population
            if minimum_repaired_population is not None
            else Fraction(0)
        ),
        "context_flags": flags,
        "dangerous_flags_clear": dangerous_flags_clear,
        "repaired_conserved": _conserved_record(repaired_conserved),
        "repaired_minus_target": _conserved_record(repaired_defect),
        "solver_and_distribution_passed": solver_passed,
        "operations_exact_and_positive": operation_passed,
        "exact_conservation_restored": conservation_passed,
        "passed": bool(
            solver_passed and operation_passed and conservation_passed
        ),
    }


def _load_registered_q007x(directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007X_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha = _file_sha256(artifact_path)
    runner_path = Path(q007x.__file__).resolve()
    backend_path = Path(backend.__file__).resolve()
    cycle = payload.get("cycle", {})
    probe_digest = cycle.get("probe_registration", {}).get(
        "probe_digest_sha256"
    )
    hypothesis_gates = cycle.get("hypothesis_gates", {})
    scope = payload.get("mathematical_scope", {})
    scope_match = bool(
        scope.get("diagnostic")
        == "concrete MPFR-85 operation bridge and fixed-leaf closure audit"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and scope.get("conservation_treatment")
        == "exact global mass and momentum equality on the fixed leaf"
    )
    record = {
        "filename": Q007X_ARTIFACT,
        "registered_sha256": REGISTERED_Q007X_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha,
        "sha256_matches": observed_artifact_sha
        == REGISTERED_Q007X_ARTIFACT_SHA256,
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": scope_match,
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(hypothesis_gates),
        "passing_hypothesis_gate_count": sum(
            bool(gate.get("passed", False)) for gate in hypothesis_gates.values()
        ),
        "probe_digest_sha256": probe_digest,
        "probe_digest_matches": probe_digest == REGISTERED_Q007X_PROBE_DIGEST,
        "registered_runner_sha256": REGISTERED_Q007X_RUNNER_SHA256,
        "artifact_runner_sha256": payload.get("runner_source", {}).get("sha256"),
        "observed_runner_sha256": _file_sha256(runner_path),
        "runner_sha_matches": bool(
            payload.get("runner_source", {}).get("sha256")
            == REGISTERED_Q007X_RUNNER_SHA256
            and _file_sha256(runner_path) == REGISTERED_Q007X_RUNNER_SHA256
        ),
        "registered_backend_sha256": REGISTERED_Q007X_BACKEND_SHA256,
        "artifact_backend_sha256": cycle.get("source_audit", {})
        .get("files", {})
        .get("backend", {})
        .get("sha256"),
        "observed_backend_sha256": _file_sha256(backend_path),
        "backend_sha_matches": bool(
            cycle.get("source_audit", {})
            .get("files", {})
            .get("backend", {})
            .get("sha256")
            == REGISTERED_Q007X_BACKEND_SHA256
            and _file_sha256(backend_path) == REGISTERED_Q007X_BACKEND_SHA256
        ),
        "q007w_input_passed": cycle.get("input_artifact", {}).get(
            "passed", False
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "not_certified"
        and record["validity_gate_count"] == 8
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 6
        and record["passing_hypothesis_gate_count"] == 2
        and record["probe_digest_matches"]
        and record["runner_sha_matches"]
        and record["backend_sha_matches"]
        and record["q007w_input_passed"]
    )
    return payload, record


def _registered_input_audit(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    q007x_payload, q007x_record = _load_registered_q007x(directory)
    q007w_payload, q007w_record, q007w_exact = q007x._load_registered_q007w(
        directory
    )
    q007x_source = q007x._source_audit(q007w_exact)
    context = q007x._context_audit()
    return q007x_payload, q007w_payload, q007w_exact, {
        "q007x_artifact": q007x_record,
        "q007w_artifact": q007w_record,
        "q007x_source_audit": q007x_source,
        "mpfr_context_audit": context,
        "passed": bool(
            q007x_record["passed"]
            and q007w_record["passed"]
            and q007x_source["passed"]
            and context["passed"]
        ),
    }


def _population_binade(population: int) -> tuple[Fraction, Fraction, Fraction]:
    if population == 0:
        return Fraction(1, 4), Fraction(1, 2), Fraction(1, 2**86)
    if population <= 4:
        return Fraction(1, 16), Fraction(1, 8), Fraction(1, 2**88)
    return DIAGONAL_BIN_LOWER, DIAGONAL_BIN_UPPER, REPAIR_QUANTUM


def _tube_stage_repair_bound(
    name: str,
    quantities: list[q007w.PairedQuantity],
) -> dict[str, Any]:
    population_records = []
    errors = []
    all_binades_pass = True
    all_lattices_contain_h = True
    for population, quantity in enumerate(quantities):
        lower, upper, lattice_quantum = _population_binade(population)
        binade_passed = bool(
            lower <= quantity.computed_lower
            and quantity.computed_upper < upper
        )
        lattice_contains_h = (
            lattice_quantum / REPAIR_QUANTUM
        ).denominator == 1
        all_binades_pass = bool(all_binades_pass and binade_passed)
        all_lattices_contain_h = bool(
            all_lattices_contain_h and lattice_contains_h
        )
        errors.append(quantity.error)
        population_records.append(
            {
                "population": population,
                "computed_lower": _fraction_record(quantity.computed_lower),
                "computed_upper": _fraction_record(quantity.computed_upper),
                "component_error_upper": _fraction_record(quantity.error),
                "binade_lower": _fraction_record(lower),
                "binade_upper": _fraction_record(upper),
                "lattice_quantum": _fraction_record(lattice_quantum),
                "lattice_units_per_repair_quantum": int(
                    lattice_quantum / REPAIR_QUANTUM
                ),
                "binade_passed": binade_passed,
                "lattice_contains_repair_quantum": lattice_contains_h,
            }
        )

    mass_defect = WAVE_COUNT * sum(errors, Fraction(0))
    momentum_x_defect = WAVE_COUNT * sum(
        (
            abs(backend.D2Q9_INTEGER_VELOCITIES[q][0]) * errors[q]
            for q in range(9)
        ),
        Fraction(0),
    )
    momentum_y_defect = WAVE_COUNT * sum(
        (
            abs(backend.D2Q9_INTEGER_VELOCITIES[q][1]) * errors[q]
            for q in range(9)
        ),
        Fraction(0),
    )
    correction_l1 = (
        mass_defect
        + momentum_x_defect
        + momentum_y_defect
        + 2 * REPAIR_QUANTUM
    )
    maximum_site_correction = (
        _ceil_fraction(correction_l1 / REPAIR_QUANTUM / WAVE_COUNT)
        * REPAIR_QUANTUM
    )
    diagonal_records = population_records[5:]
    corrected_binade_passed = all(
        _fraction_from_record(record["computed_lower"])
        - maximum_site_correction
        >= DIAGONAL_BIN_LOWER
        and _fraction_from_record(record["computed_upper"])
        + maximum_site_correction
        < DIAGONAL_BIN_UPPER
        for record in diagonal_records
    )
    non_diagonal_lattice_units_even = all(
        record["lattice_units_per_repair_quantum"] % 2 == 0
        for record in population_records[:5]
    )
    target_units = tuple(_integer_units(value) for value in TARGET_CONSERVED)
    target_parity_compatible = bool(
        (target_units[0] - target_units[1]) % 2 == 0
        and (target_units[0] - target_units[2]) % 2 == 0
    )
    passed = bool(
        all_binades_pass
        and all_lattices_contain_h
        and corrected_binade_passed
        and non_diagonal_lattice_units_even
        and target_parity_compatible
    )
    return {
        "name": name,
        "population_records": population_records,
        "mass_defect_upper": _fraction_record(mass_defect),
        "momentum_x_defect_upper": _fraction_record(momentum_x_defect),
        "momentum_y_defect_upper": _fraction_record(momentum_y_defect),
        "repair_l1_upper": _fraction_record(correction_l1),
        "maximum_site_correction_upper": _fraction_record(
            maximum_site_correction
        ),
        "all_raw_population_binades_pass": all_binades_pass,
        "all_population_lattices_contain_repair_quantum": (
            all_lattices_contain_h
        ),
        "non_diagonal_lattice_units_even": (
            non_diagonal_lattice_units_even
        ),
        "target_units": list(target_units),
        "target_parity_compatible": target_parity_compatible,
        "repaired_diagonal_binade_and_positivity_passed": (
            corrected_binade_passed
        ),
        "passed": passed,
    }


def _tube_wide_audit(
    q007w_payload: dict[str, Any],
    q007w_exact: dict[str, Any],
) -> dict[str, Any]:
    fixed = q007w_payload["cycle"]["fixed_q007v_values"]
    selected_analysis = _fraction_from_record(fixed["selected_analysis_upper"])
    external_analysis = _fraction_from_record(fixed["external_analysis_upper"])
    summary, exact = q007w._evaluate_precision(
        backend.MPFR_PRECISION_BITS,
        q007w_exact["state_radius"],
        selected_analysis,
        external_analysis,
        q007w_exact["base_margin"],
        q007w_exact["normal_margin"],
    )
    registered = q007w_payload["cycle"]["selection"]["selected_candidate"]
    replay_matches = summary == registered
    input_bound = _tube_stage_repair_bound("input_encoding", exact["inputs"])
    postfilter_bound = _tube_stage_repair_bound(
        "post_filter",
        exact["filtered"],
    )
    raw_wiener = _fraction_from_record(
        postfilter_bound["mass_defect_upper"]
    )
    repair_wiener = _fraction_from_record(
        postfilter_bound["repair_l1_upper"]
    )
    repaired_wiener = raw_wiener + repair_wiener
    base_error = selected_analysis * repaired_wiener
    normal_error = external_analysis * repaired_wiener
    base_passed = base_error < q007w_exact["base_margin"]
    normal_passed = normal_error < q007w_exact["normal_margin"]
    original_wiener_matches = raw_wiener == exact["wiener_error"]
    arithmetic_identity_passed = bool(
        raw_wiener
        == WAVE_COUNT
        * sum((quantity.error for quantity in exact["filtered"]), Fraction(0))
        and repair_wiener
        == raw_wiener
        + _fraction_from_record(postfilter_bound["momentum_x_defect_upper"])
        + _fraction_from_record(postfilter_bound["momentum_y_defect_upper"])
        + 2 * REPAIR_QUANTUM
        and repaired_wiener == raw_wiener + repair_wiener
    )
    passed = bool(
        replay_matches
        and input_bound["passed"]
        and postfilter_bound["passed"]
        and original_wiener_matches
        and arithmetic_identity_passed
    )
    return {
        "q007w_p85_replay_matches_artifact": replay_matches,
        "input_encoding": input_bound,
        "post_filter": postfilter_bound,
        "raw_wiener_error_upper": _fraction_record(raw_wiener),
        "repair_wiener_addition_upper": _fraction_record(repair_wiener),
        "repaired_wiener_error_upper": _fraction_record(repaired_wiener),
        "repair_addition_to_raw_ratio": _fraction_record(
            repair_wiener / raw_wiener
        ),
        "repaired_to_raw_ratio": _fraction_record(
            repaired_wiener / raw_wiener
        ),
        "selected_analysis_upper": _fraction_record(selected_analysis),
        "external_analysis_upper": _fraction_record(external_analysis),
        "base_coordinate_error_upper": _fraction_record(base_error),
        "base_margin": _fraction_record(q007w_exact["base_margin"]),
        "base_margin_utilization": _fraction_record(
            base_error / q007w_exact["base_margin"]
        ),
        "base_reentry_passed": base_passed,
        "normal_coordinate_error_upper": _fraction_record(normal_error),
        "normal_margin": _fraction_record(q007w_exact["normal_margin"]),
        "normal_margin_utilization": _fraction_record(
            normal_error / q007w_exact["normal_margin"]
        ),
        "normal_reentry_passed": normal_passed,
        "original_wiener_matches_q007w": original_wiener_matches,
        "registered_arithmetic_identity_passed": arithmetic_identity_passed,
        "triangle_bound_uses_center_cancellation": False,
        "triangle_bound_uses_spatial_fourier_phase": False,
        "repair_map_well_defined_on_registered_tube": bool(
            input_bound["passed"] and postfilter_bound["passed"]
        ),
        "passed": passed,
    }


def _component_error_record(
    observed: MPFRArray,
    exact: ExactArray,
) -> dict[str, Any]:
    per_population = []
    maximum = Fraction(0)
    for population in range(9):
        error = max(
            abs(
                backend.fraction_from_mpfr(observed[y, x, population])
                - Fraction(exact[y, x, population])
            )
            for y in range(SIZE)
            for x in range(SIZE)
        )
        maximum = max(maximum, error)
        per_population.append(
            {
                "population": population,
                "maximum_component_error": _fraction_record(error),
            }
        )
    return {
        "per_population": per_population,
        "maximum_component_error": _fraction_record(maximum),
    }


def _evaluate_probe(
    name: str,
    exact_input: ExactArray,
    q007w_exact: dict[str, Any],
) -> dict[str, Any]:
    concrete = backend.MPFRD2Q9Backend()
    encoded, encoding_audit = concrete.encode_fraction_state(exact_input)
    repaired_input, input_repair = repair_conserved_state(
        encoded,
        TARGET_CONSERVED,
    )
    repaired_input_exact = q007x._mpfr_to_fraction_array(repaired_input)
    exact_stages = q007x._exact_stages(repaired_input_exact)
    stages = concrete.evaluate_encoded_stages(repaired_input)
    raw_stages = {
        "equilibrium": stages.equilibrium,
        "post_collision": stages.post_collision,
        "post_streaming": stages.post_streaming,
        "post_filter": stages.post_filter,
    }
    stage_comparisons = {
        stage_name: q007x._stage_comparison(
            observed,
            exact_stages[stage_name],
            q007w_exact["stage_error_bounds"][stage_name],
        )
        for stage_name, observed in raw_stages.items()
    }
    repaired_output, output_repair = repair_conserved_state(
        stages.post_filter,
        TARGET_CONSERVED,
    )
    repaired_output_comparison = q007x._stage_comparison(
        repaired_output,
        exact_stages["post_filter"],
        q007w_exact["stage_error_bounds"]["post_filter"],
    )

    exact_input_conserved = q007x._global_conserved(exact_input)
    repaired_input_conserved = _global_conserved_mpfr(repaired_input)
    collision_conserved = _global_conserved_mpfr(stages.post_collision)
    streaming_conserved = _global_conserved_mpfr(stages.post_streaming)
    raw_output_conserved = _global_conserved_mpfr(stages.post_filter)
    repaired_output_conserved = _global_conserved_mpfr(repaired_output)
    exact_output_conserved = q007x._global_conserved(
        exact_stages["post_filter"]
    )
    expected_counts = backend.expected_operation_counts(
        WAVE_COUNT,
        include_input_roundings=False,
    )
    dangerous_flags_clear = not any(
        stages.context_flags[key]
        for key in (
            "underflow",
            "overflow",
            "invalid",
            "division_by_zero",
            "erange",
        )
    )
    operation_domain_passed = bool(
        encoding_audit.counts["input_roundings"] == 9 * WAVE_COUNT
        and stages.operation_counts == expected_counts
        and stages.minimum_density_divisor > 0
        and stages.all_results_finite
        and dangerous_flags_clear
    )
    raw_stage_passed = all(
        comparison["passed"] for comparison in stage_comparisons.values()
    )
    repair_passed = bool(input_repair["passed"] and output_repair["passed"])
    conservation_passed = bool(
        exact_input_conserved == TARGET_CONSERVED
        and repaired_input_conserved == TARGET_CONSERVED
        and exact_output_conserved == TARGET_CONSERVED
        and repaired_output_conserved == TARGET_CONSERVED
    )
    finite_bound_passed = bool(
        raw_stage_passed and repaired_output_comparison["passed"]
    )
    return {
        "name": name,
        "input_encoding_error": _component_error_record(
            repaired_input,
            exact_input,
        ),
        "input_repair": input_repair,
        "backend_operation_domain": {
            "encoding_input_rounding_count": encoding_audit.counts[
                "input_roundings"
            ],
            "expected_encoding_input_rounding_count": 9 * WAVE_COUNT,
            "map_operation_counts": stages.operation_counts,
            "expected_map_operation_counts": expected_counts,
            "minimum_density_divisor": _fraction_record(
                stages.minimum_density_divisor
            ),
            "maximum_intermediate_magnitude": _fraction_record(
                stages.maximum_intermediate_magnitude
            ),
            "all_results_finite": stages.all_results_finite,
            "context_flags": stages.context_flags,
            "dangerous_flags_clear": dangerous_flags_clear,
            "passed": operation_domain_passed,
        },
        "raw_stage_comparisons": stage_comparisons,
        "raw_stages_pass_q007w_bounds_and_positivity": raw_stage_passed,
        "output_repair": output_repair,
        "repaired_output_comparison": repaired_output_comparison,
        "conservation": {
            "exact_input": _conserved_record(exact_input_conserved),
            "repaired_input": _conserved_record(repaired_input_conserved),
            "post_collision": _conserved_record(collision_conserved),
            "post_streaming": _conserved_record(streaming_conserved),
            "raw_post_filter": _conserved_record(raw_output_conserved),
            "repaired_post_filter": _conserved_record(
                repaired_output_conserved
            ),
            "exact_post_filter": _conserved_record(exact_output_conserved),
            "streaming_minus_collision": _conserved_record(
                _difference(streaming_conserved, collision_conserved)
            ),
            "repaired_input_exact": (
                repaired_input_conserved == TARGET_CONSERVED
            ),
            "exact_map_preserves_leaf": exact_output_conserved
            == TARGET_CONSERVED,
            "repaired_output_exact": repaired_output_conserved
            == TARGET_CONSERVED,
        },
        "repair_solver_and_operations_passed": repair_passed,
        "exact_conservation_restored": conservation_passed,
        "finite_stage_bound_and_positivity_passed": finite_bound_passed,
        "passed": bool(
            operation_domain_passed
            and repair_passed
            and conservation_passed
            and finite_bound_passed
        ),
    }


def _finite_campaign(
    probes: list[tuple[str, ExactArray]],
    q007w_exact: dict[str, Any],
) -> dict[str, Any]:
    records = [
        _evaluate_probe(name, state, q007w_exact) for name, state in probes
    ]
    digest = _digest_payload(records)
    summary = {
        "all_input_repairs_conserve": all(
            record["conservation"]["repaired_input_exact"]
            for record in records
        ),
        "all_exact_maps_preserve_leaf": all(
            record["conservation"]["exact_map_preserves_leaf"]
            for record in records
        ),
        "all_output_repairs_conserve": all(
            record["conservation"]["repaired_output_exact"]
            for record in records
        ),
        "all_repairs_solve_and_add_exactly": all(
            record["repair_solver_and_operations_passed"]
            for record in records
        ),
        "all_backend_operation_domains_pass": all(
            record["backend_operation_domain"]["passed"]
            for record in records
        ),
        "all_finite_stage_bounds_and_positivity_pass": all(
            record["finite_stage_bound_and_positivity_passed"]
            for record in records
        ),
        "all_streaming_steps_conserve": all(
            all(
                _fraction_from_record(
                    record["conservation"]["streaming_minus_collision"][name]
                )
                == 0
                for name in ("mass", "momentum_x", "momentum_y")
            )
            for record in records
        ),
    }
    return {
        "probe_count": len(records),
        "result_digest_sha256": digest,
        "summary": summary,
        "probes": records,
        "passed": bool(all(record["passed"] for record in records)),
    }


def run_distributed_repair_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    (
        q007x_payload,
        q007w_payload,
        q007w_exact,
        input_audit,
    ) = _registered_input_audit(directory)
    probe_audit, probes = q007x._probe_registration_audit(
        q007w_exact["state_radius"]
    )
    registered_probe_digest = q007x_payload["cycle"]["probe_registration"][
        "probe_digest_sha256"
    ]
    probe_match = bool(
        probe_audit["passed"]
        and probe_audit["probe_digest_sha256"] == registered_probe_digest
        and registered_probe_digest == REGISTERED_Q007X_PROBE_DIGEST
    )
    tube_audit = _tube_wide_audit(q007w_payload, q007w_exact)
    campaign = _finite_campaign(probes, q007w_exact)

    repair_integer_lattice_passed = bool(
        tube_audit["input_encoding"]["passed"]
        and tube_audit["post_filter"]["passed"]
        and all(
            probe["input_repair"]["solver_and_distribution_passed"]
            and probe["output_repair"]["solver_and_distribution_passed"]
            for probe in campaign["probes"]
        )
    )
    repair_operations_passed = bool(
        campaign["summary"]["all_repairs_solve_and_add_exactly"]
    )
    backend_stage_passed = bool(
        campaign["summary"]["all_backend_operation_domains_pass"]
        and campaign["summary"][
            "all_finite_stage_bounds_and_positivity_pass"
        ]
    )
    preliminary = {
        "input_audit": input_audit,
        "probe_registration": probe_audit,
        "tube_wide_repair_bound": tube_audit,
        "finite_campaign": campaign,
    }
    strict_json = bool(
        _all_numeric_values_finite(preliminary)
        and _strict_json_serializable(preliminary)
    )
    digests_reproducible = bool(
        len(probe_audit["probe_digest_sha256"]) == 64
        and len(campaign["result_digest_sha256"]) == 64
        and all(
            len(probe[stage]["distribution_digest_sha256"]) == 64
            for probe in campaign["probes"]
            for stage in ("input_repair", "output_repair")
        )
    )
    validity_gates = {
        "registered_q007w_q007x_inputs": {
            "passed": input_audit["passed"],
            "threshold": (
                "registered Q007w/Q007x artifact and runner SHA, source, "
                "scope, and upstream decisions all match"
            ),
            "value": input_audit["passed"],
        },
        "sealed_backend_and_context": {
            "passed": bool(
                input_audit["q007x_source_audit"]["passed"]
                and input_audit["mpfr_context_audit"]["passed"]
            ),
            "threshold": (
                "Q007x backend/source SHA and registered MPFR-85 context "
                "remain unchanged"
            ),
            "value": {
                "source": input_audit["q007x_source_audit"]["passed"],
                "context": input_audit["mpfr_context_audit"]["passed"],
            },
        },
        "registered_probe_replay": {
            "passed": probe_match,
            "threshold": (
                "all four Q007x recipes, fixed-leaf checks, and probe digest "
                "match"
            ),
            "value": probe_audit["probe_digest_sha256"],
        },
        "repair_lattice_and_parity": {
            "passed": repair_integer_lattice_passed,
            "threshold": (
                "registered binades imply the h=2^-90 lattice/parity and "
                "every finite defect is integral"
            ),
            "value": repair_integer_lattice_passed,
        },
        "integer_solver_and_balanced_distribution": {
            "passed": repair_integer_lattice_passed,
            "threshold": (
                "Hadamard equations, registered l1 objective/bound, and "
                "row-major balanced distributions pass"
            ),
            "value": repair_integer_lattice_passed,
        },
        "exact_mpfr_repair_operations": {
            "passed": repair_operations_passed,
            "threshold": (
                "all repair additions are exact, same-binade, positive, "
                "finite, and clear dangerous/inexact flags"
            ),
            "value": repair_operations_passed,
        },
        "backend_stage_enclosure_and_domain": {
            "passed": backend_stage_passed,
            "threshold": (
                "registered operation counts/domain plus every raw/repaired "
                "finite stage bound and positivity check pass"
            ),
            "value": backend_stage_passed,
        },
        "tube_bound_strict_json_and_digests": {
            "passed": bool(
                tube_audit["passed"] and strict_json and digests_reproducible
            ),
            "threshold": (
                "Q007w p85 replay and exact tube arithmetic pass with finite "
                "strict JSON and reproducible digests"
            ),
            "value": {
                "tube_bound": tube_audit["passed"],
                "strict_json": strict_json,
                "digests": digests_reproducible,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    input_conservation = campaign["summary"]["all_input_repairs_conserve"]
    output_conservation = campaign["summary"]["all_output_repairs_conserve"]
    finite_repairs = bool(
        campaign["summary"]["all_repairs_solve_and_add_exactly"]
        and campaign["summary"][
            "all_finite_stage_bounds_and_positivity_pass"
        ]
    )
    tube_defined = tube_audit["repair_map_well_defined_on_registered_tube"]
    normal_passed = tube_audit["normal_reentry_passed"]
    base_passed = tube_audit["base_reentry_passed"]
    hypothesis_gates = {
        "repaired_encoding_restores_fixed_leaf_probes": {
            "passed": bool(validity_passed and input_conservation),
            "threshold": "all four repaired inputs equal target M/Px/Py exactly",
            "value": input_conservation,
        },
        "repaired_postfilter_restores_fixed_leaf_probes": {
            "passed": bool(validity_passed and output_conservation),
            "threshold": (
                "all four repaired post-filter outputs equal target M/Px/Py "
                "exactly"
            ),
            "value": output_conservation,
        },
        "finite_repairs_are_exact_positive_and_enclosed": {
            "passed": bool(validity_passed and finite_repairs),
            "threshold": (
                "every finite repair is exactly representable, positive, "
                "and remains inside Q007w component bounds"
            ),
            "value": finite_repairs,
        },
        "repair_map_is_defined_on_registered_tube": {
            "passed": bool(validity_passed and tube_defined),
            "threshold": (
                "lattice, parity, binade, and worst-case site correction "
                "prove the repair is defined throughout the registered tube"
            ),
            "value": tube_defined,
        },
        "repair_aware_normal_budget_closes": {
            "passed": bool(validity_passed and normal_passed),
            "threshold": "repair-aware normal error is below Q007w margin",
            "value": normal_passed,
        },
        "repair_aware_base_budget_closes": {
            "passed": bool(validity_passed and base_passed),
            "threshold": "repair-aware base error is below Q007w margin",
            "value": base_passed,
        },
        "repaired_fixed_leaf_all_iterate_induction_closes": {
            "passed": False,
            "threshold": "all six preceding hypotheses pass",
            "value": False,
        },
    }
    first_six_pass = all(
        gate["passed"]
        for name, gate in hypothesis_gates.items()
        if name != "repaired_fixed_leaf_all_iterate_induction_closes"
    )
    induction_passed = bool(validity_passed and first_six_pass)
    hypothesis_gates["repaired_fixed_leaf_all_iterate_induction_closes"][
        "passed"
    ] = induction_passed
    hypothesis_gates["repaired_fixed_leaf_all_iterate_induction_closes"][
        "value"
    ] = induction_passed
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )

    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007y distributed repair audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "distributed MPFR-85 repair closes the Q007w fixed-leaf tube "
            "induction"
        )
    elif all(
        hypothesis_gates[name]["passed"]
        for name in (
            "repaired_encoding_restores_fixed_leaf_probes",
            "repaired_postfilter_restores_fixed_leaf_probes",
            "finite_repairs_are_exact_positive_and_enclosed",
            "repair_map_is_defined_on_registered_tube",
            "repair_aware_normal_budget_closes",
        )
    ) and not hypothesis_gates["repair_aware_base_budget_closes"]["passed"]:
        outcome = "not_certified"
        classification = (
            "distributed MPFR-85 repair restores the registered fixed-leaf "
            "probes but not the Q007w tube-wide base budget"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered distributed MPFR-85 repair does not restore the "
            "fixed conservation leaf"
        )

    return {
        "question": (
            "Does a deterministic diagonal dyadic correction restore the "
            "MPFR-85 fixed leaf and still fit the unchanged Q007w tube-wide "
            "base and normal error budgets?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "wave_count": WAVE_COUNT,
            "precision_bits": backend.MPFR_PRECISION_BITS,
            "repair_quantum": _fraction_record(REPAIR_QUANTUM),
            "diagonal_populations": list(DIAGONAL_POPULATIONS),
            "diagonal_binade": {
                "lower": _fraction_record(DIAGONAL_BIN_LOWER),
                "upper": _fraction_record(DIAGONAL_BIN_UPPER),
            },
            "target_conserved": _conserved_record(TARGET_CONSERVED),
            "solver_objective": [
                "sum_abs_diagonal_units",
                "max_abs_diagonal_units",
                "abs_free_unit",
                "free_unit",
            ],
            "distribution": "Python divmod over 289 row-major sites",
            "probe_names": list(q007x.PROBE_NAMES),
        },
        "input_audit": input_audit,
        "probe_registration": probe_audit,
        "tube_wide_repair_bound": tube_audit,
        "finite_campaign": campaign,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_finite_input_repairs_restore_exact_fixed_leaf": bool(
                validity_passed and input_conservation
            ),
            "registered_finite_output_repairs_restore_exact_fixed_leaf": bool(
                validity_passed and output_conservation
            ),
            "distributed_repair_is_defined_on_registered_q007s_tube": bool(
                validity_passed and tube_defined
            ),
            "repair_aware_normal_reentry_is_certified": bool(
                validity_passed and normal_passed
            ),
            "repair_aware_base_reentry_is_certified": bool(
                validity_passed and base_passed
            ),
            "all_iterate_repaired_mpfr85_q007s_tube_invariance": bool(
                validity_passed and hypotheses_passed
            ),
        },
        "claim_boundary": (
            "The integer/lattice proof makes the registered repair well "
            "defined on the fixed-leaf Q007s tube, and the four probes audit "
            "its concrete MPFR implementation. Finite probes alone are not "
            "a tube sampling proof. The repair-aware Wiener estimate is a "
            "coarse triangle bound that uses neither cancellation of the "
            "conserved center error nor spatial Fourier phase. Failure of its "
            "base gate does not prove that a projector-aware bound or another "
            "repair cannot close. No center-slow, trajectory, performance, "
            "parallel reduction, other MPFR build, or D3Q27 claim is made."
        ),
        "preserved_prior_outcomes": {
            "q007x_fixed_leaf_rejection_changed": False,
            "q007w_ideal_precision_acceptance_changed": False,
            "q007v_binary64_reentry_rejection_changed": False,
            "q007u_exact_stagewise_acceptance_changed": False,
            "q007s_exact_fixed_leaf_invariance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If the finite repair and normal budget pass but the coarse base "
            "budget fails, preregister a projector-aware repair estimate that "
            "uses exact center cancellation and the balanced repair's Fourier "
            "phase without changing the sealed backend or finite repair."
        ),
    }


def run_q007y_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_distributed_repair_audit(artifact_directory)
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
                "distributed dyadic fixed-leaf repair and repair-aware "
                "Wiener-budget audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(backend.EXACT_OMEGA),
            "eta": float(backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "post-stage repair"
            ),
            "repair_lattice": "four diagonal populations on h=2^-90",
            "rounding_model": (
                "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
            ),
            "claim": (
                "separate finite exact repair feasibility from the unchanged "
                "Q007w tube-wide base and normal margin decisions"
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
    result = run_q007y_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
