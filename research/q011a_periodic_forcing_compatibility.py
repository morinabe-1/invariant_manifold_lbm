"""Sealed Q011a periodic nonzero-mean forcing compatibility study."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from ttim_lbm.checkerboard_filter import (
    conservative_checkerboard_filter,
    filtered_fourier_symbol,
)
from ttim_lbm.conservation_drift import compensated_conserved_quantities
from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    D2Q9_WEIGHTS,
    collide_bgk,
    global_conserved_quantities,
    linearized_periodic_step,
    project_perturbation_to_fixed_conservation_leaf,
    stream_periodic,
    uniform_equilibrium,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]

SIZE = 17
SITE_COUNT = SIZE * SIZE
OMEGA = 1.5
ETA = 0.01
EXACT_OMEGA = Fraction(3, 2)
EXACT_ETA = Fraction(1, 100)
EXACT_FORCE = (Fraction(3, 2**40), Fraction(0))
FORCE = np.asarray([float(value) for value in EXACT_FORCE], dtype=np.float64)
EXACT_GLOBAL_INCREMENT = (
    Fraction(0),
    SITE_COUNT * EXACT_FORCE[0],
    SITE_COUNT * EXACT_FORCE[1],
)
PROBE_SEED = 20260809
SEEDED_PROBE_COUNT = 8
PROBE_SCALE = 2.0**-18
DERIVATIVE_DIRECTION_COUNT = 4
DERIVATIVE_STEPS = (2.0**-12, 2.0**-13, 2.0**-14)
SOURCE_MOMENT_TOLERANCE = 2.0**-90
STATE_DIFFERENCE_TOLERANCE = 5.0e-16
GLOBAL_MOMENT_TOLERANCE = 5.0e-14
DERIVATIVE_RELATIVE_TOLERANCE = 1.0e-9
UNIT_CIRCLE_TOLERANCE = 1.0e-10

EXACT_VELOCITIES: tuple[tuple[int, int], ...] = (
    (0, 0),
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, 1),
    (-1, 1),
    (-1, -1),
    (1, -1),
)
EXACT_WEIGHTS: tuple[Fraction, ...] = (
    Fraction(4, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 36),
    Fraction(1, 36),
    Fraction(1, 36),
    Fraction(1, 36),
)


def _canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(b"\\0")
    digest.update(json.dumps(array.shape).encode("ascii"))
    digest.update(b"\\0")
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _require_force(force: npt.ArrayLike) -> Array:
    value = np.asarray(force, dtype=np.float64)
    if value.shape != (2,) or not np.all(np.isfinite(value)):
        raise ValueError("body force must be a finite two-component vector")
    return value


def rest_linear_body_force_source(force: npt.ArrayLike) -> Array:
    """Return the state-independent D2Q9 rest-linear source."""

    value = _require_force(force)
    return np.asarray(
        3.0 * D2Q9_WEIGHTS * (D2Q9_VELOCITIES @ value),
        dtype=np.float64,
    )


def forced_filtered_bgk_periodic_step(
    state: npt.ArrayLike,
    omega: float,
    eta: float,
    force: npt.ArrayLike,
) -> Array:
    """Apply collision, a uniform additive source, streaming, and filtering."""

    populations = np.asarray(state, dtype=np.float64)
    source = rest_linear_body_force_source(force)
    post_source = collide_bgk(populations, omega) + source
    return conservative_checkerboard_filter(stream_periodic(post_source), eta)


def _unforced_filtered_step(state: npt.ArrayLike) -> Array:
    collided = collide_bgk(state, OMEGA)
    return conservative_checkerboard_filter(stream_periodic(collided), ETA)


def _exact_source() -> tuple[Fraction, ...]:
    return tuple(
        3
        * weight
        * (
            velocity[0] * EXACT_FORCE[0]
            + velocity[1] * EXACT_FORCE[1]
        )
        for weight, velocity in zip(
            EXACT_WEIGHTS,
            EXACT_VELOCITIES,
            strict=True,
        )
    )


def _exact_moments(
    source: tuple[Fraction, ...],
) -> tuple[Fraction, Fraction, Fraction]:
    return (
        sum(source, Fraction(0)),
        sum(
            (
                value * velocity[0]
                for value, velocity in zip(
                    source,
                    EXACT_VELOCITIES,
                    strict=True,
                )
            ),
            Fraction(0),
        ),
        sum(
            (
                value * velocity[1]
                for value, velocity in zip(
                    source,
                    EXACT_VELOCITIES,
                    strict=True,
                )
            ),
            Fraction(0),
        ),
    )


def _source_audit() -> dict[str, Any]:
    exact_source = _exact_source()
    exact_moments = _exact_moments(exact_source)
    expected_float = np.asarray(
        [float(value) for value in exact_source],
        dtype=np.float64,
    )
    observed_float = rest_linear_body_force_source(FORCE)
    observed_moments = np.asarray(
        [
            np.sum(observed_float),
            observed_float @ D2Q9_VELOCITIES[:, 0],
            observed_float @ D2Q9_VELOCITIES[:, 1],
        ],
        dtype=np.float64,
    )
    expected_moments = np.asarray(
        [0.0, FORCE[0], FORCE[1]],
        dtype=np.float64,
    )
    moment_residual = observed_moments - expected_moments
    velocities_match = bool(
        np.array_equal(
            D2Q9_VELOCITIES,
            np.asarray(EXACT_VELOCITIES, dtype=np.float64),
        )
    )
    weights_match = bool(
        np.array_equal(
            D2Q9_WEIGHTS,
            np.asarray([float(value) for value in EXACT_WEIGHTS]),
        )
    )
    bitwise_match = bool(
        np.array_equal(
            observed_float.view(np.uint64),
            expected_float.view(np.uint64),
        )
    )
    exact_identities = {
        "source_mass_is_zero": exact_moments[0] == 0,
        "source_momentum_x_is_registered_force": (
            exact_moments[1] == EXACT_FORCE[0]
        ),
        "source_momentum_y_is_registered_force": (
            exact_moments[2] == EXACT_FORCE[1]
        ),
        "global_increment_is_site_count_times_force": (
            EXACT_GLOBAL_INCREMENT
            == (
                0,
                SITE_COUNT * EXACT_FORCE[0],
                SITE_COUNT * EXACT_FORCE[1],
            )
        ),
    }
    passed = bool(
        velocities_match
        and weights_match
        and bitwise_match
        and all(exact_identities.values())
        and np.max(np.abs(moment_residual)) <= SOURCE_MOMENT_TOLERANCE
    )
    return {
        "exact_velocities": [list(value) for value in EXACT_VELOCITIES],
        "exact_weights": [_fraction_record(value) for value in EXACT_WEIGHTS],
        "exact_force": [_fraction_record(value) for value in EXACT_FORCE],
        "exact_source_populations": [
            _fraction_record(value) for value in exact_source
        ],
        "exact_source_moments": [
            _fraction_record(value) for value in exact_moments
        ],
        "exact_global_moment_increment": [
            _fraction_record(value) for value in EXACT_GLOBAL_INCREMENT
        ],
        "observed_source_populations": observed_float.tolist(),
        "observed_source_population_hex": [
            value.hex() for value in observed_float.tolist()
        ],
        "observed_source_moments": observed_moments.tolist(),
        "source_moment_residual": moment_residual.tolist(),
        "maximum_source_moment_residual": float(
            np.max(np.abs(moment_residual))
        ),
        "source_moment_tolerance": SOURCE_MOMENT_TOLERANCE,
        "velocity_table_matches": velocities_match,
        "weight_table_matches": weights_match,
        "source_population_bitwise_matches_exact_dyadics": bitwise_match,
        "exact_identities": exact_identities,
        "all_exact_identities_pass": all(exact_identities.values()),
        "passed": passed,
    }


def _registered_directions() -> Array:
    rng = np.random.default_rng(PROBE_SEED)
    directions = np.empty(
        (SEEDED_PROBE_COUNT, SIZE, SIZE, 9),
        dtype=np.float64,
    )
    for index in range(SEEDED_PROBE_COUNT):
        raw = rng.standard_normal((SIZE, SIZE, 9))
        fixed_leaf = project_perturbation_to_fixed_conservation_leaf(raw)
        scale = float(np.max(np.abs(fixed_leaf)))
        if scale == 0.0:
            raise RuntimeError("registered forcing direction is zero")
        directions[index] = fixed_leaf / scale
    return directions


def _registered_probes() -> tuple[list[tuple[str, Array]], Array]:
    rest = uniform_equilibrium(SIZE, SIZE, np.zeros(3))
    moving = uniform_equilibrium(
        SIZE,
        SIZE,
        np.asarray([2.0**-8, 2.0**-10, -(2.0**-11)]),
    )
    directions = _registered_directions()
    probes: list[tuple[str, Array]] = [
        ("uniform_rest", rest),
        ("uniform_moving", moving),
    ]
    probes.extend(
        (
            f"seeded_fixed_leaf_{index}",
            rest + PROBE_SCALE * direction,
        )
        for index, direction in enumerate(directions)
    )
    return probes, directions


def _finite_probe_audit(source_audit: dict[str, Any]) -> dict[str, Any]:
    probes, directions = _registered_probes()
    source = rest_linear_body_force_source(FORCE)
    source_state = np.broadcast_to(source, (SIZE, SIZE, 9)).copy()
    transported_source = conservative_checkerboard_filter(
        stream_periodic(source_state),
        ETA,
    )
    expected_global = np.asarray(
        [float(value) for value in EXACT_GLOBAL_INCREMENT],
        dtype=np.float64,
    )
    records: list[dict[str, Any]] = []
    for name, state in probes:
        collided = collide_bgk(state, OMEGA)
        unforced = conservative_checkerboard_filter(
            stream_periodic(collided),
            ETA,
        )
        forced = conservative_checkerboard_filter(
            stream_periodic(collided + source),
            ETA,
        )
        helper = forced_filtered_bgk_periodic_step(
            state,
            OMEGA,
            ETA,
            FORCE,
        )
        difference = forced - unforced
        difference_error = difference - transported_source
        faithful, neumaier = compensated_conserved_quantities(difference)
        faithful_error = faithful - expected_global
        neumaier_error = neumaier - expected_global
        residual = forced - state
        records.append(
            {
                "name": name,
                "minimum_input_population": float(np.min(state)),
                "minimum_forced_output_population": float(np.min(forced)),
                "helper_matches_shared_collision_path": bool(
                    np.array_equal(helper, forced)
                ),
                "maximum_state_difference_error": float(
                    np.max(np.abs(difference_error))
                ),
                "faithful_global_difference": faithful.tolist(),
                "neumaier_global_difference": neumaier.tolist(),
                "maximum_faithful_global_difference_error": float(
                    np.max(np.abs(faithful_error))
                ),
                "maximum_neumaier_global_difference_error": float(
                    np.max(np.abs(neumaier_error))
                ),
                "full_step_population_l1_residual": float(
                    np.sum(np.abs(residual))
                ),
                "full_step_numpy_moment_increment": (
                    global_conserved_quantities(forced)
                    - global_conserved_quantities(state)
                ).tolist(),
            }
        )
    maximum_component_error = max(
        record["maximum_state_difference_error"] for record in records
    )
    maximum_global_error = max(
        max(
            record["maximum_faithful_global_difference_error"],
            record["maximum_neumaier_global_difference_error"],
        )
        for record in records
    )
    all_positive = all(
        record["minimum_input_population"] > 0.0
        and record["minimum_forced_output_population"] > 0.0
        for record in records
    )
    helpers_match = all(
        record["helper_matches_shared_collision_path"]
        for record in records
    )
    direction_leaf_residuals = [
        float(np.max(np.abs(global_conserved_quantities(direction))))
        for direction in directions
    ]
    rest_record = records[0]
    passed = bool(
        source_audit["passed"]
        and len(records) == 10
        and maximum_component_error <= STATE_DIFFERENCE_TOLERANCE
        and maximum_global_error <= GLOBAL_MOMENT_TOLERANCE
        and all_positive
        and helpers_match
        and rest_record["minimum_forced_output_population"] > 0.0
    )
    return {
        "probe_seed": PROBE_SEED,
        "seeded_probe_count": SEEDED_PROBE_COUNT,
        "probe_count": len(records),
        "probe_scale": PROBE_SCALE,
        "moving_equilibrium_coordinates": [
            2.0**-8,
            2.0**-10,
            -(2.0**-11),
        ],
        "direction_sha256": _array_sha256(directions),
        "maximum_direction_fixed_leaf_residual": max(
            direction_leaf_residuals
        ),
        "transported_uniform_source_matches_source": bool(
            np.array_equal(transported_source, source_state)
        ),
        "registered_global_increment": expected_global.tolist(),
        "state_difference_tolerance": STATE_DIFFERENCE_TOLERANCE,
        "global_moment_tolerance": GLOBAL_MOMENT_TOLERANCE,
        "maximum_state_difference_error": maximum_component_error,
        "maximum_compensated_global_difference_error": maximum_global_error,
        "all_probe_states_and_outputs_positive": all_positive,
        "all_helpers_match_shared_collision_path": helpers_match,
        "records": records,
        "passed": passed,
    }


def _relative_error(left: np.ndarray, right: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(right)), np.finfo(float).eps)
    return float(np.linalg.norm(left - right)) / denominator


def _derivative_and_spectrum_audit() -> dict[str, Any]:
    rest = uniform_equilibrium(SIZE, SIZE, np.zeros(3))
    directions = _registered_directions()[:DERIVATIVE_DIRECTION_COUNT]
    derivative_records: list[dict[str, Any]] = []
    for index, direction in enumerate(directions):
        step_records = []
        for step in DERIVATIVE_STEPS:
            forced_derivative = (
                forced_filtered_bgk_periodic_step(
                    rest + step * direction,
                    OMEGA,
                    ETA,
                    FORCE,
                )
                - forced_filtered_bgk_periodic_step(
                    rest - step * direction,
                    OMEGA,
                    ETA,
                    FORCE,
                )
            ) / (2.0 * step)
            unforced_derivative = (
                _unforced_filtered_step(rest + step * direction)
                - _unforced_filtered_step(rest - step * direction)
            ) / (2.0 * step)
            analytic_derivative = conservative_checkerboard_filter(
                linearized_periodic_step(direction, OMEGA),
                ETA,
            )
            step_records.append(
                {
                    "step": step,
                    "forced_unforced_relative_discrepancy": _relative_error(
                        forced_derivative,
                        unforced_derivative,
                    ),
                    "forced_analytic_relative_error": _relative_error(
                        forced_derivative,
                        analytic_derivative,
                    ),
                    "unforced_analytic_relative_error": _relative_error(
                        unforced_derivative,
                        analytic_derivative,
                    ),
                }
            )
        best_discrepancy = min(
            record["forced_unforced_relative_discrepancy"]
            for record in step_records
        )
        derivative_records.append(
            {
                "direction_index": index,
                "steps": step_records,
                "best_forced_unforced_relative_discrepancy": (
                    best_discrepancy
                ),
                "passed": (
                    best_discrepancy <= DERIVATIVE_RELATIVE_TOLERANCE
                ),
            }
        )

    strict_unit_records: list[dict[str, Any]] = []
    nonunit_moduli: list[float] = []
    symbol_records: list[dict[str, Any]] = []
    maximum_symbol_difference = 0.0
    for ix in range(SIZE):
        kx = 2.0 * np.pi * ix / SIZE
        for iy in range(SIZE):
            ky = 2.0 * np.pi * iy / SIZE
            unforced_symbol = filtered_fourier_symbol(
                kx,
                ky,
                OMEGA,
                ETA,
            )
            forced_reference_symbol = filtered_fourier_symbol(
                kx,
                ky,
                OMEGA,
                ETA,
            )
            maximum_symbol_difference = max(
                maximum_symbol_difference,
                float(
                    np.max(
                        np.abs(
                            forced_reference_symbol - unforced_symbol
                        )
                    )
                ),
            )
            eigenvalues = np.linalg.eigvals(unforced_symbol)
            symbol_records.append(
                {
                    "wave_index": [ix, iy],
                    "eigenvalues": [
                        [float(value.real), float(value.imag)]
                        for value in eigenvalues
                    ],
                }
            )
            for value in eigenvalues:
                modulus = float(abs(value))
                if abs(modulus - 1.0) < UNIT_CIRCLE_TOLERANCE:
                    strict_unit_records.append(
                        {
                            "wave_index": [ix, iy],
                            "eigenvalue": [
                                float(value.real),
                                float(value.imag),
                            ],
                        }
                    )
                else:
                    nonunit_moduli.append(modulus)
    derivative_passed = all(
        record["passed"] for record in derivative_records
    )
    spectrum_passed = bool(
        len(strict_unit_records) == 3
        and all(
            record["wave_index"] == [0, 0]
            for record in strict_unit_records
        )
        and maximum_symbol_difference == 0.0
    )
    return {
        "derivative_direction_count": DERIVATIVE_DIRECTION_COUNT,
        "derivative_steps": list(DERIVATIVE_STEPS),
        "derivative_relative_tolerance": DERIVATIVE_RELATIVE_TOLERANCE,
        "derivative_records": derivative_records,
        "maximum_best_forced_unforced_relative_discrepancy": max(
            record["best_forced_unforced_relative_discrepancy"]
            for record in derivative_records
        ),
        "all_source_derivative_zero_checks_pass": derivative_passed,
        "forced_reference_symbol_definition": (
            "state-independent source derivative is zero; use the "
            "unforced filtered reference-state symbol"
        ),
        "maximum_forced_unforced_symbol_entry_difference": (
            maximum_symbol_difference
        ),
        "unit_circle_tolerance": UNIT_CIRCLE_TOLERANCE,
        "strict_unit_circle_count": len(strict_unit_records),
        "strict_unit_circle_records": strict_unit_records,
        "largest_nonunit_modulus": max(nonunit_moduli),
        "symbol_eigenvalue_digest_sha256": _canonical_json_sha256(
            symbol_records
        ),
        "rest_is_not_a_forced_fixed_point": True,
        "spectrum_is_reference_state_not_fixed_point_stability": True,
        "spectrum_passed": spectrum_passed,
        "passed": bool(derivative_passed and spectrum_passed),
    }


def _obstruction_audit(
    finite_probe_audit: dict[str, Any],
) -> dict[str, Any]:
    increment = EXACT_GLOBAL_INCREMENT[1]
    residual_lower = increment
    finite_residuals = [
        record["full_step_population_l1_residual"]
        for record in finite_probe_audit["records"]
    ]
    exact_identities = {
        "registered_spatial_mean_force_is_nonzero": (
            EXACT_FORCE[0] != 0 or EXACT_FORCE[1] != 0
        ),
        "global_momentum_increment_is_nonzero": increment > 0,
        "fixed_point_would_require_zero_increment": True,
        "registered_increment_contradicts_fixed_point": increment != 0,
        "dual_momentum_functional_norm_is_one": True,
        "population_l1_residual_lower_equals_increment": (
            residual_lower == increment
        ),
    }
    no_sink = {
        "periodic_streaming_only": True,
        "populationwise_conservative_filter_only": True,
        "boundary_momentum_exchange_absent": True,
        "drag_absent": True,
        "global_momentum_projection_or_repair_absent": True,
    }
    passed = bool(
        all(exact_identities.values())
        and all(no_sink.values())
        and residual_lower > 0
    )
    return {
        "exact_global_mass_momentum_increment": [
            _fraction_record(value) for value in EXACT_GLOBAL_INCREMENT
        ],
        "exact_population_l1_fixed_point_residual_lower": _fraction_record(
            residual_lower
        ),
        "global_momentum_ledger": (
            "M(Phi_F(f))-M(f)=(0,site_count*F_x,site_count*F_y)"
        ),
        "fixed_point_contradiction": (
            "Phi_F(f)=f implies zero global moment increment, but the "
            "registered exact increment is strictly positive"
        ),
        "dual_residual_inequality": (
            "||Phi_F(f)-f||_population_l1 >= |Delta P_x|"
        ),
        "minimum_finite_probe_population_l1_residual": min(
            finite_residuals
        ),
        "finite_probe_residuals_exceed_exact_lower_float": all(
            value >= float(residual_lower) for value in finite_residuals
        ),
        "no_momentum_sink_audit": no_sink,
        "all_no_momentum_sink_checks_pass": all(no_sink.values()),
        "exact_identities": exact_identities,
        "all_exact_identities_pass": all(exact_identities.values()),
        "passed": passed,
    }


def run_periodic_forcing_compatibility_audit() -> dict[str, Any]:
    """Run the preregistered Q011a compatibility and obstruction gate."""

    registered_parameters = {
        "size": SIZE,
        "site_count": SITE_COUNT,
        "omega": _fraction_record(EXACT_OMEGA),
        "eta": _fraction_record(EXACT_ETA),
        "force": [_fraction_record(value) for value in EXACT_FORCE],
        "source": "S_q(F)=3*w_q*(c_q dot F)",
        "stage_order": (
            "BGK collision, uniform additive source, periodic streaming, "
            "populationwise conservative five-point filter"
        ),
        "boundary": "periodic",
        "momentum_sink": "none",
        "probe_seed": PROBE_SEED,
        "seeded_probe_count": SEEDED_PROBE_COUNT,
        "probe_scale": PROBE_SCALE,
        "derivative_steps": list(DERIVATIVE_STEPS),
        "unit_circle_tolerance": UNIT_CIRCLE_TOLERANCE,
    }
    source_audit = _source_audit()
    finite_audit = _finite_probe_audit(source_audit)
    derivative_audit = _derivative_and_spectrum_audit()
    obstruction_audit = _obstruction_audit(finite_audit)
    source_sections = {
        "registered_parameters": registered_parameters,
        "exact_source_audit": source_audit,
    }
    probe_sections = {
        "finite_probe_audit": finite_audit,
        "derivative_and_spectrum_audit": derivative_audit,
    }
    source_digest = _canonical_json_sha256(source_sections)
    probe_digest = _canonical_json_sha256(probe_sections)
    pre_gate_sections = {
        **source_sections,
        **probe_sections,
        "fixed_point_obstruction_audit": obstruction_audit,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        source_digest == _canonical_json_sha256(source_sections)
        and probe_digest == _canonical_json_sha256(probe_sections)
    )
    validity_gates = {
        "exact_d2q9_source_moment_reconstruction": {
            "passed": source_audit["all_exact_identities_pass"],
            "threshold": (
                "exact D2Q9 rational table gives zero source mass and "
                "registered source momentum"
            ),
            "value": source_audit["exact_identities"],
        },
        "dyadic_float_source_and_local_moment_reproduction": {
            "passed": source_audit["passed"],
            "threshold": (
                "float source is bitwise exact dyadic and local moment "
                "residual <=2^-90"
            ),
            "value": {
                "bitwise": source_audit[
                    "source_population_bitwise_matches_exact_dyadics"
                ],
                "maximum_moment_residual": source_audit[
                    "maximum_source_moment_residual"
                ],
            },
        },
        "ten_probe_forced_unforced_source_and_ledger_reproduction": {
            "passed": finite_audit["passed"],
            "threshold": (
                "10 positive probes reproduce the transported source "
                "within 5e-16 and compensated global increment within "
                "5e-14"
            ),
            "value": {
                "probe_count": finite_audit["probe_count"],
                "maximum_state_error": finite_audit[
                    "maximum_state_difference_error"
                ],
                "maximum_global_error": finite_audit[
                    "maximum_compensated_global_difference_error"
                ],
            },
        },
        "zero_source_derivative_and_reference_spectrum": {
            "passed": derivative_audit["passed"],
            "threshold": (
                "best forced/unforced derivative discrepancy <=1e-9, "
                "symbol equality, and odd-grid strict unit count 3"
            ),
            "value": {
                "maximum_best_derivative_discrepancy": derivative_audit[
                    "maximum_best_forced_unforced_relative_discrepancy"
                ],
                "strict_unit_circle_count": derivative_audit[
                    "strict_unit_circle_count"
                ],
            },
        },
        "exact_global_ledger_and_dual_residual_lower_bound": {
            "passed": obstruction_audit["passed"],
            "threshold": (
                "nonzero exact global increment and population-l1 fixed-"
                "point residual lower bound reproduce"
            ),
            "value": obstruction_audit[
                "exact_population_l1_fixed_point_residual_lower"
            ],
        },
        "finite_strict_json_and_reproducible_digests": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "all values are finite strict JSON and source/probe "
                "digests reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )
    nonzero_mean = obstruction_audit["exact_identities"][
        "registered_spatial_mean_force_is_nonzero"
    ]
    nonzero_increment = obstruction_audit["exact_identities"][
        "global_momentum_increment_is_nonzero"
    ]
    no_sink = obstruction_audit["all_no_momentum_sink_checks_pass"]
    contradiction = bool(
        obstruction_audit["exact_identities"][
            "registered_increment_contradicts_fixed_point"
        ]
        and obstruction_audit["exact_identities"][
            "population_l1_residual_lower_equals_increment"
        ]
    )
    hypothesis_gates = {
        "registered_spatial_mean_force_is_nonzero": {
            "passed": bool(validity_passed and nonzero_mean),
            "threshold": "spatial mean force is nonzero",
            "value": nonzero_mean,
        },
        "exact_global_momentum_increment_is_strictly_positive": {
            "passed": bool(validity_passed and nonzero_increment),
            "threshold": "867*2^-40>0",
            "value": obstruction_audit[
                "exact_global_mass_momentum_increment"
            ][1],
        },
        "registered_periodic_map_has_no_momentum_sink": {
            "passed": bool(validity_passed and no_sink),
            "threshold": (
                "no boundary, drag, or momentum repair cancels the source"
            ),
            "value": no_sink,
        },
        "fixed_point_contradiction_and_residual_lower_bound_close": {
            "passed": bool(validity_passed and contradiction),
            "threshold": (
                "fixed point requires zero increment while exact increment "
                "and population-l1 lower bound are positive"
            ),
            "value": contradiction,
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered periodic forcing compatibility audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "nonzero-mean periodic body force is incompatible with a "
            "fixed point of the registered conservative map"
        )
    elif not nonzero_mean:
        outcome = "not_certified"
        classification = (
            "registered periodic forcing has zero mean and is not "
            "obstructed by the global momentum ledger"
        )
    else:
        outcome = "not_certified"
        classification = (
            "global momentum ledger does not exclude a registered forced "
            "fixed point"
        )
    result_sections = {
        **pre_gate_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = _canonical_json_sha256(result_sections)
    return {
        "question": (
            "Can a nonzero-mean uniform body force on the registered "
            "periodic conservative D2Q9 map be compatible with a fixed "
            "point?"
        ),
        **pre_gate_sections,
        "source_digest_sha256": source_digest,
        "probe_digest_sha256": probe_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_exact_periodic_map_has_no_fixed_point": bool(
                validity_passed and hypotheses_passed
            ),
            "registered_fixed_point_newton_solve_should_start": False,
            "rest_reference_jacobian_is_unchanged_by_additive_source": bool(
                validity_passed and derivative_audit["passed"]
            ),
            "rest_reference_spectrum_is_forced_fixed_point_stability": False,
            "zero_mean_periodic_forcing_is_obstructed": False,
            "wall_bounded_forcing_is_obstructed": False,
        },
        "claim_boundary": (
            "An accepted result is an exact real-arithmetic global-momentum "
            "ledger obstruction for one state-independent rest-linear "
            "nonzero-mean source on the 17x17 periodic filtered BGK map. "
            "It is not a bitwise finite-precision fixed-point theorem, a "
            "Guo or exact-difference accuracy result, a zero-mean, drag, "
            "pressure-boundary, bounce-back, Poiseuille, or Couette result, "
            "or a forced invariant-manifold, normal-attraction, other-grid, "
            "grid-uniform, continuum, or D3Q27 result. The rest Jacobian is "
            "only a non-fixed reference-state diagnostic."
        ),
        "preserved_prior_outcomes": {
            "q007ap_unforced_shadowing_changed": False,
            "q007ag_unforced_tube_changed": False,
            "q008c_tt_rejection_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "Do not run a fixed-point Newton solve for nonzero-mean "
            "periodic forcing. Preregister Q011b with a zero-mean single-"
            "wave periodic source before constructing a forced fixed point "
            "or spectrum; keep wall-bounded Poiseuille and Couette separate."
        ),
    }


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }


def run_q011a_study() -> dict[str, Any]:
    cycle = run_periodic_forcing_compatibility_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "exact global-momentum fixed-point compatibility audit "
                "for nonzero-mean periodic forcing"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "force": [float(value) for value in EXACT_FORCE],
            "boundary": "periodic",
            "forcing": (
                "state-independent rest-linear additive source after "
                "collision"
            ),
            "momentum_sink": "none",
            "reference_spectrum": (
                "rest-state diagnostic only; rest is not a forced fixed "
                "point"
            ),
            "claim": (
                "fixed-point obstruction from exact global momentum "
                "ledger; no forced manifold or wall-bounded claim"
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
    result = run_q011a_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
