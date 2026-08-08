"""Sealed Q007r exact stagewise-positivity certificate for the Q007p tube."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from ttim_lbm.checkerboard_filter import (
    conservative_checkerboard_filter,
    filtered_bgk_periodic_step,
)
from ttim_lbm.d2q9 import collide_bgk, stream_periodic
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    VELOCITIES,
    WEIGHTS,
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
    rational_collision_symbol,
)

SIZE = 17
OMEGA = Fraction(3, 2)
ETA = Fraction(1, 100)
BASE_RADIUS = Fraction(1, 10**19)
NORMAL_RADIUS = Fraction(1, 10**20)
Q007Q_ARTIFACT = "q007q_population_positivity.json"
REGISTERED_Q007Q_ARTIFACT_SHA256 = (
    "e8c763419f6e803f102f81a3beb957261b736754ab490ca3cb914dc9247269cb"
)
REGISTERED_Q007Q_RUNNER_SHA256 = (
    "026b4d549e92bf74ac29393244a4400fb7a8d1bb3eb263ee729d81432c8290e5"
)
REGISTERED_EQUILIBRIUM_LINEAR_NORM = Fraction(13, 6)
REGISTERED_COLLISION_LINEAR_NORM = Fraction(19, 6)
REGISTERED_EQUILIBRIUM_NONLINEAR_CONSTANT = Fraction(7)
REGISTERED_COLLISION_NONLINEAR_CONSTANT = Fraction(21, 2)

RationalMatrix = tuple[tuple[Fraction, ...], ...]


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


def _load_registered_q007q(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007Q_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007q_population_positivity.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    scope = payload.get("mathematical_scope", {})
    scope_match = bool(
        scope.get("diagnostic") == "rational population-positivity certificate"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == float(OMEGA)
        and float(scope.get("eta", np.nan)) == float(ETA)
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and float(scope.get("base_modal_l1_radius", np.nan))
        == float(BASE_RADIUS)
        and float(scope.get("normal_coordinate_radius", np.nan))
        == float(NORMAL_RADIUS)
        and scope.get("sampling_times") == "full one-step map input/output only"
    )
    theorem = payload.get("cycle", {}).get("theorem_consequence", {})
    theorem_flags_match = bool(len(theorem) == 3 and all(theorem.values()))
    q007p_input_passed = bool(
        payload.get("cycle", {}).get("input_artifact", {}).get("passed", False)
    )
    record = {
        "filename": Q007Q_ARTIFACT,
        "registered_sha256": REGISTERED_Q007Q_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007Q_ARTIFACT_SHA256
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": scope_match,
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload, "hypothesis_gates"
        ),
        "theorem_consequence_count": len(theorem),
        "all_theorem_consequences_true": theorem_flags_match,
        "q007p_input_passed": q007p_input_passed,
        "registered_runner_sha256": REGISTERED_Q007Q_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007Q_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007Q_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["all_validity_gates_pass"]
        and record["all_hypothesis_gates_pass"]
        and theorem_flags_match
        and q007p_input_passed
        and record["runner_sha_matches"]
    )
    return payload, record


def _matrix_product(left: RationalMatrix, right: RationalMatrix) -> RationalMatrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible rational matrix dimensions")
    return tuple(
        tuple(
            sum(
                (left[row][inner] * right[inner][column] for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def _column_l1_sums(matrix: RationalMatrix) -> tuple[Fraction, ...]:
    return tuple(
        sum((abs(matrix[row][column]) for row in range(len(matrix))), Fraction(0))
        for column in range(len(matrix[0]))
    )


def _linear_operator_audit() -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    moment: RationalMatrix = (
        tuple(Fraction(1) for _ in VELOCITIES),
        tuple(Fraction(cx) for cx, _ in VELOCITIES),
        tuple(Fraction(cy) for _, cy in VELOCITIES),
    )
    tangent: RationalMatrix = tuple(
        (
            weight,
            3 * weight * cx,
            3 * weight * cy,
        )
        for (cx, cy), weight in zip(VELOCITIES, WEIGHTS, strict=True)
    )
    projector = _matrix_product(tangent, moment)
    identity: RationalMatrix = tuple(
        tuple(Fraction(row == column) for column in range(9))
        for row in range(9)
    )
    collision: RationalMatrix = tuple(
        tuple(
            (1 - OMEGA) * identity[row][column]
            + OMEGA * projector[row][column]
            for column in range(9)
        )
        for row in range(9)
    )
    registered_collision = rational_collision_symbol()
    projector_columns = _column_l1_sums(projector)
    collision_columns = _column_l1_sums(collision)
    projector_norm = max(projector_columns)
    collision_norm = max(collision_columns)
    passed = bool(
        len(moment) == 3
        and len(tangent) == 9
        and collision == registered_collision
        and projector_norm == REGISTERED_EQUILIBRIUM_LINEAR_NORM
        and collision_norm == REGISTERED_COLLISION_LINEAR_NORM
    )
    serializable = {
        "moment_matrix_shape": [3, 9],
        "equilibrium_tangent_shape": [9, 3],
        "equilibrium_projector_formula": "P = E M",
        "collision_formula": "C = (1-omega) I + omega E M",
        "omega": _fraction_record(OMEGA),
        "equilibrium_projector_column_l1_sums": [
            _fraction_record(value) for value in projector_columns
        ],
        "collision_column_l1_sums": [
            _fraction_record(value) for value in collision_columns
        ],
        "equilibrium_projector_l1_norm": _fraction_record(projector_norm),
        "collision_l1_norm": _fraction_record(collision_norm),
        "registered_equilibrium_projector_l1_norm": _fraction_record(
            REGISTERED_EQUILIBRIUM_LINEAR_NORM
        ),
        "registered_collision_l1_norm": _fraction_record(
            REGISTERED_COLLISION_LINEAR_NORM
        ),
        "collision_matches_rational_map": collision == registered_collision,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "equilibrium_linear_norm": projector_norm,
        "collision_linear_norm": collision_norm,
        "passed": passed,
    }
    return serializable, exact


def _nonlinear_majorant_audit(
    state_radius: Fraction,
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    weight_sum = sum(WEIGHTS, Fraction(0))
    velocity_quadratic = sum(
        (
            weight * (abs(cx) + abs(cy)) ** 2
            for (cx, cy), weight in zip(VELOCITIES, WEIGHTS, strict=True)
        ),
        Fraction(0),
    )
    momentum_square_component_count = 2
    equilibrium_constant = (
        Fraction(9, 2) * velocity_quadratic
        + Fraction(3, 2) * momentum_square_component_count
    )
    collision_constant = OMEGA * equilibrium_constant
    density_buffer = 1 - state_radius
    equilibrium_nonlinear = (
        equilibrium_constant * state_radius**2 / density_buffer
        if density_buffer > 0
        else Fraction(0)
    )
    collision_nonlinear = OMEGA * equilibrium_nonlinear
    passed = bool(
        weight_sum == 1
        and velocity_quadratic == Fraction(8, 9)
        and equilibrium_constant == REGISTERED_EQUILIBRIUM_NONLINEAR_CONSTANT
        and collision_constant == REGISTERED_COLLISION_NONLINEAR_CONSTANT
        and density_buffer > 0
    )
    serializable = {
        "cyclic_fourier_convolution_l1_constant": 1,
        "d2q9_weight_sum": _fraction_record(weight_sum),
        "weighted_absolute_velocity_quadratic": _fraction_record(
            velocity_quadratic
        ),
        "momentum_square_component_count": momentum_square_component_count,
        "equilibrium_nonlinear_majorant_constant": _fraction_record(
            equilibrium_constant
        ),
        "collision_nonlinear_majorant_constant": _fraction_record(
            collision_constant
        ),
        "state_wiener_l1_upper": _fraction_record(state_radius),
        "density_denominator_lower": _fraction_record(density_buffer),
        "equilibrium_nonlinear_remainder_upper": _fraction_record(
            equilibrium_nonlinear
        ),
        "collision_nonlinear_remainder_upper": _fraction_record(
            collision_nonlinear
        ),
        "equilibrium_formula": "7*x_*^2/(1-x_*)",
        "collision_formula": "(21/2)*x_*^2/(1-x_*)",
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "density_buffer": density_buffer,
        "equilibrium_constant": equilibrium_constant,
        "collision_constant": collision_constant,
        "equilibrium_nonlinear": equilibrium_nonlinear,
        "collision_nonlinear": collision_nonlinear,
        "passed": passed,
    }
    return serializable, exact


def _stage_structure_audit() -> dict[str, Any]:
    site_count = SIZE * SIZE
    streaming_records: list[dict[str, Any]] = []
    implementation_replays: list[bool] = []
    center_y = SIZE // 2
    center_x = SIZE // 2
    for population, (cx, cy) in enumerate(VELOCITIES):
        targets = {
            ((y + cy) % SIZE, (x + cx) % SIZE)
            for y in range(SIZE)
            for x in range(SIZE)
        }
        basis = np.zeros((SIZE, SIZE, 9), dtype=np.float64)
        basis[center_y, center_x, population] = 1.0
        expected = np.zeros_like(basis)
        expected[
            (center_y + cy) % SIZE,
            (center_x + cx) % SIZE,
            population,
        ] = 1.0
        replayed = bool(np.array_equal(stream_periodic(basis), expected))
        implementation_replays.append(replayed)
        streaming_records.append(
            {
                "population": population,
                "velocity": [cx, cy],
                "unique_periodic_target_count": len(targets),
                "bijective": len(targets) == site_count,
                "implementation_basis_replayed": replayed,
            }
        )

    filter_coefficients = (1 - ETA, ETA / 4, ETA / 4, ETA / 4, ETA / 4)
    filter_replays: list[bool] = []
    for population in range(9):
        basis = np.zeros((SIZE, SIZE, 9), dtype=np.float64)
        basis[center_y, center_x, population] = 1.0
        expected = np.zeros_like(basis)
        expected[center_y, center_x, population] = float(filter_coefficients[0])
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            expected[
                (center_y + dy) % SIZE,
                (center_x + dx) % SIZE,
                population,
            ] = float(filter_coefficients[1])
        filter_replays.append(
            bool(
                np.array_equal(
                    conservative_checkerboard_filter(basis, float(ETA)),
                    expected,
                )
            )
        )

    rest = np.broadcast_to(
        np.asarray([float(weight) for weight in WEIGHTS]),
        (SIZE, SIZE, 9),
    ).copy()
    explicit_composition = conservative_checkerboard_filter(
        stream_periodic(collide_bgk(rest, float(OMEGA))),
        float(ETA),
    )
    wrapped_composition = filtered_bgk_periodic_step(
        rest,
        float(OMEGA),
        float(ETA),
    )
    composition_replayed = bool(
        np.array_equal(explicit_composition, wrapped_composition)
    )
    all_streaming_bijective = all(
        record["bijective"] for record in streaming_records
    )
    all_streaming_replayed = all(implementation_replays)
    all_filter_replayed = all(filter_replays)
    filter_sum = sum(filter_coefficients, Fraction(0))
    filter_nonnegative = all(value >= 0 for value in filter_coefficients)
    passed = bool(
        len(streaming_records) == 9
        and all_streaming_bijective
        and all_streaming_replayed
        and filter_coefficients
        == (
            Fraction(99, 100),
            Fraction(1, 400),
            Fraction(1, 400),
            Fraction(1, 400),
            Fraction(1, 400),
        )
        and filter_sum == 1
        and filter_nonnegative
        and all_filter_replayed
        and composition_replayed
    )
    return {
        "stage_order": [
            "equilibrium evaluation",
            "BGK collision",
            "periodic streaming",
            "five-point filter",
        ],
        "streaming_records": streaming_records,
        "streaming_population_permutation_count": len(streaming_records),
        "periodic_site_count": site_count,
        "all_streaming_maps_bijective": all_streaming_bijective,
        "all_streaming_implementation_basis_replays": all_streaming_replayed,
        "filter_coefficients": [
            _fraction_record(value) for value in filter_coefficients
        ],
        "filter_coefficient_sum": _fraction_record(filter_sum),
        "all_filter_coefficients_nonnegative": filter_nonnegative,
        "all_filter_implementation_basis_replays": all_filter_replayed,
        "wrapped_stage_composition_replayed": composition_replayed,
        "passed": passed,
    }


def run_stagewise_positivity_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007q, input_record = _load_registered_q007q(directory)
    q007q_cycle = q007q["cycle"]
    tube = q007q_cycle["q007p_tube_reuse"]
    q007q_bounds = q007q_cycle["positivity_bounds"]
    state_radius = _fraction_from_record(tube["tube_state_wiener_l1_upper"])
    base_radius = _fraction_from_record(tube["base_modal_l1_radius"])
    normal_radius = _fraction_from_record(tube["normal_coordinate_radius"])
    q007q_population_lower = _fraction_from_record(
        q007q_bounds["registered_population_lower"]
    )

    linear_section, linear_exact = _linear_operator_audit()
    nonlinear_section, nonlinear_exact = _nonlinear_majorant_audit(
        state_radius
    )
    structure = _stage_structure_audit()
    equilibrium_linear_norm = linear_exact["equilibrium_linear_norm"]
    collision_linear_norm = linear_exact["collision_linear_norm"]
    equilibrium_nonlinear = nonlinear_exact["equilibrium_nonlinear"]
    collision_nonlinear = nonlinear_exact["collision_nonlinear"]
    assert isinstance(equilibrium_linear_norm, Fraction)
    assert isinstance(collision_linear_norm, Fraction)
    assert isinstance(equilibrium_nonlinear, Fraction)
    assert isinstance(collision_nonlinear, Fraction)

    minimum_weight = Fraction(1, 36)
    equilibrium_deviation = (
        equilibrium_linear_norm * state_radius + equilibrium_nonlinear
    )
    collision_deviation = (
        collision_linear_norm * state_radius + collision_nonlinear
    )
    equilibrium_lower = minimum_weight - equilibrium_deviation
    collision_lower = minimum_weight - collision_deviation
    stream_lower = collision_lower
    filter_lower = collision_lower
    full_map_lower = q007q_population_lower
    forward_invariance = bool(tube["q007p_forward_invariance"])
    tube_reused = bool(
        base_radius == BASE_RADIUS
        and normal_radius == NORMAL_RADIUS
        and q007q_population_lower == minimum_weight - state_radius
        and tube["state_radius_reproduced_exactly"]
        and forward_invariance
        and tube["passed"]
    )
    stage_bounds = {
        "input_state_wiener_l1_upper": _fraction_record(state_radius),
        "minimum_rest_population": _fraction_record(minimum_weight),
        "q007q_input_population_lower": _fraction_record(
            q007q_population_lower
        ),
        "equilibrium_deviation_wiener_l1_upper": _fraction_record(
            equilibrium_deviation
        ),
        "equilibrium_population_lower": _fraction_record(equilibrium_lower),
        "post_collision_deviation_wiener_l1_upper": _fraction_record(
            collision_deviation
        ),
        "post_collision_population_lower": _fraction_record(collision_lower),
        "post_streaming_population_lower": _fraction_record(stream_lower),
        "post_filter_population_lower": _fraction_record(filter_lower),
        "q007q_full_map_output_population_lower": _fraction_record(
            full_map_lower
        ),
        "equilibrium_deviation_formula": "(13/6)*x_* + 7*x_*^2/(1-x_*)",
        "collision_deviation_formula": "(19/6)*x_* + (21/2)*x_*^2/(1-x_*)",
        "streaming_lower_identity": "p_stream = p_coll",
        "filter_lower_identity": "p_filter = p_coll",
    }
    tube_reuse = {
        "base_modal_l1_radius": _fraction_record(base_radius),
        "normal_coordinate_radius": _fraction_record(normal_radius),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "q007q_population_lower": _fraction_record(q007q_population_lower),
        "q007p_forward_invariance": forward_invariance,
        "state_radius_reproduced_exactly": tube[
            "state_radius_reproduced_exactly"
        ],
        "passed": tube_reused,
    }

    serializable_sections = {
        "input_artifact": input_record,
        "linear_operator_audit": linear_section,
        "nonlinear_majorant_audit": nonlinear_section,
        "stage_structure_audit": structure,
        "registered_tube_reuse": tube_reuse,
        "stage_bounds": stage_bounds,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007q_input": {
            "passed": input_record["passed"],
            "threshold": (
                "Q007q artifact/runner SHA, source, scope, all gates, three "
                "theorem flags, and transitive Q007p input match"
            ),
            "value": input_record["passed"],
        },
        "exact_linear_stage_operators": {
            "passed": linear_section["passed"],
            "threshold": (
                "exact P=EM and C=(1-omega)I+omega EM reproduce the map "
                "with induced l1 norms 13/6 and 19/6"
            ),
            "value": {
                "equilibrium_norm": float(equilibrium_linear_norm),
                "collision_norm": float(collision_linear_norm),
            },
        },
        "exact_equilibrium_nonlinear_majorant": {
            "passed": nonlinear_section["passed"],
            "threshold": (
                "weight sum 1, velocity quadratic 8/9, nonlinear constants "
                "7 and 21/2, and positive density denominator"
            ),
            "value": {
                "equilibrium_constant": float(
                    nonlinear_exact["equilibrium_constant"]
                ),
                "collision_constant": float(
                    nonlinear_exact["collision_constant"]
                ),
                "density_buffer": float(nonlinear_exact["density_buffer"]),
            },
        },
        "streaming_and_filter_structure": {
            "passed": structure["passed"],
            "threshold": (
                "nine periodic streaming permutations and the exact "
                "99/100 plus four 1/400 convex filter reproduce the map"
            ),
            "value": {
                "streaming_permutations": structure[
                    "streaming_population_permutation_count"
                ],
                "filter_sum": structure["filter_coefficient_sum"]["float"],
                "composition_replayed": structure[
                    "wrapped_stage_composition_replayed"
                ],
            },
        },
        "registered_tube_reused": {
            "passed": tube_reuse["passed"],
            "threshold": (
                "Q007q x_*, p_*, r, zeta, and Q007p forward invariance "
                "reproduce exactly"
            ),
            "value": tube_reuse["passed"],
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all exact bounds are finite and strict JSON serializable",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "equilibrium_evaluation_positive": {
            "passed": equilibrium_lower > 0,
            "threshold": "p_eq = 1/36 - e_* > 0",
            "value": float(equilibrium_lower),
        },
        "post_collision_positive": {
            "passed": collision_lower > 0,
            "threshold": "p_coll = 1/36 - c_* > 0",
            "value": float(collision_lower),
        },
        "post_streaming_positive": {
            "passed": bool(structure["all_streaming_maps_bijective"] and stream_lower > 0),
            "threshold": "population-wise streaming permutations preserve p_coll",
            "value": float(stream_lower),
        },
        "post_filter_positive": {
            "passed": bool(
                structure["all_filter_coefficients_nonnegative"]
                and _fraction_from_record(structure["filter_coefficient_sum"])
                == 1
                and filter_lower > 0
            ),
            "threshold": "the five-point convex filter preserves p_coll",
            "value": float(filter_lower),
        },
        "all_iterate_stagewise_positive": {
            "passed": bool(
                forward_invariance
                and equilibrium_lower > 0
                and collision_lower > 0
                and structure["passed"]
            ),
            "threshold": (
                "Q007p forward invariance reapplies all four strict stage "
                "bounds at every one-step iterate"
            ),
            "value": {
                "forward_invariance": forward_invariance,
                "minimum_stage_lower": float(
                    min(equilibrium_lower, collision_lower, stream_lower, filter_lower)
                ),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007r stagewise-positivity audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered Q007p tube is population-positive at every exact BGK, "
            "streaming, and filter stage"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered Q007p tube did not certify exact stagewise population "
            "positivity"
        )

    return {
        "question": (
            "Is every exact equilibrium, BGK collision, streaming, and filter "
            "stage population-positive on the registered Q007p tube?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": _fraction_record(OMEGA),
            "eta": _fraction_record(ETA),
            "base_radius": _fraction_record(BASE_RADIUS),
            "normal_radius": _fraction_record(NORMAL_RADIUS),
        },
        "input_artifact": input_record,
        "linear_operator_audit": linear_section,
        "nonlinear_majorant_audit": nonlinear_section,
        "stage_structure_audit": structure,
        "registered_tube_reuse": tube_reuse,
        "stage_bounds": stage_bounds,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "equilibrium_evaluation_population_strictly_positive": (
                hypotheses_passed
            ),
            "post_collision_population_strictly_positive": hypotheses_passed,
            "post_streaming_population_strictly_positive": hypotheses_passed,
            "post_filter_population_strictly_positive": hypotheses_passed,
            "all_iterates_exact_stagewise_population_strictly_positive": (
                hypotheses_passed
            ),
        },
        "claim_boundary": (
            "This certifies strict population positivity for the exact "
            "mathematical equilibrium evaluation, BGK collision output, "
            "periodic streaming output, and five-point filter output on the "
            "fixed Q007p tube at every iterate. It does not enclose every "
            "IEEE-754 intermediate operation or certify entropy, monotonicity, "
            "a maximum principle, a larger tube, a global basin, grid-"
            "uniformity, a continuum limit, Q007c1 finite-amplitude "
            "performance, or Q007d Euclidean contraction."
        ),
        "preserved_prior_outcomes": {
            "q007q_full_map_positivity_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, keep the fixed tube and treat IEEE-754 roundoff or "
            "tube enlargement as separate preregistered gates."
        ),
    }


def run_q007r_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_stagewise_positivity_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational exact stagewise-positivity certificate",
            "construction_grid": [SIZE, SIZE],
            "omega": float(OMEGA),
            "eta": float(ETA),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "stages": [
                "equilibrium evaluation",
                "BGK collision output",
                "periodic streaming output",
                "five-point filter output",
            ],
            "arithmetic_scope": (
                "exact mathematical map; no IEEE-754 intermediate roundoff enclosure"
            ),
            "claim": (
                "strict D2Q9 population positivity at every exact internal "
                "one-step stage on the fixed Q007p tube only"
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
    result = run_q007r_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
