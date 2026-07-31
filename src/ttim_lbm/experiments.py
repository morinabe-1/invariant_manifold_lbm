"""Reproducible baseline questions for the D2Q9 research line."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

import numpy as np

from .d2q9 import (
    bgk_periodic_step,
    dense_linearized_map,
    exact_uniform_hessian,
    spectrum_audit,
    uniform_center_basis,
    uniform_equilibrium,
)
from .manifold import (
    QuadraticChart,
    invariance_residual,
    log_log_slope,
    second_derivative_tensor,
    solve_identity_center_quadratic,
)
from .provenance import runtime_metadata, source_metadata
from .spectra import classify_low_wave_hydrodynamic_modes
from .tensor_train import (
    evaluate_polynomial,
    polynomial_coefficient_tensor,
    reconstruct,
    tt_ranks,
    tt_svd,
)


def _relative_error(actual: np.ndarray, expected: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(expected)), np.finfo(float).eps)
    return float(np.linalg.norm(actual - expected) / denominator)


def _spectral_cycle(omega: float) -> dict[str, Any]:
    unit_tolerance = 1.0e-10
    even = spectrum_audit(size=8, omega=omega, unit_tolerance=unit_tolerance)
    odd = spectrum_audit(size=9, omega=omega, unit_tolerance=unit_tolerance)
    gates = {
        "even_grid_alias_detected": {
            "value": even["nonzero_wave_unit_count"],
            "threshold": 1,
            "passed": even["nonzero_wave_unit_count"] >= 1,
        },
        "odd_grid_only_conserved_unit_modes": {
            "value": odd["strict_unit_count"],
            "threshold": 3,
            "passed": odd["strict_unit_count"] == 3,
        },
    }
    accepted = all(gate["passed"] for gate in gates.values())
    return {
        "question": (
            "Does a strict |lambda|=1 selector isolate only the three conserved "
            "D2Q9 modes on a finite periodic grid?"
        ),
        "hypothesis": "It does, independently of grid parity.",
        "unit_tolerance": unit_tolerance,
        "even_grid": even,
        "odd_grid": odd,
        "gates": gates,
        "outcome": "rejected" if accepted else "inconclusive",
        "analysis": (
            "Even grids contain Nyquist checkerboard modes on the unit circle. "
            "A physical selector must track hydrodynamic branches from k=0 and "
            "apply a low-wave-number admissibility rule; modulus alone is unsafe."
        ),
        "next_change": (
            "Use odd grids for the strict-center oracle and use branch identity "
            "plus a k cutoff for the future slow-manifold model."
        ),
    }


def _parameterization_cycle(omega: float) -> tuple[dict[str, Any], QuadraticChart]:
    ny = nx = 3
    base_state = uniform_equilibrium(ny, nx, np.zeros(3))
    base = base_state.ravel()
    tangent, extractor = uniform_center_basis(ny, nx)
    jacobian = dense_linearized_map(ny, nx, omega)
    derivative_step = 1.0e-2
    analytic_hessian = exact_uniform_hessian(ny, nx)

    def full_map(flat_state: np.ndarray) -> np.ndarray:
        state = np.asarray(flat_state, dtype=np.float64).reshape(ny, nx, 9)
        return bgk_periodic_step(state, omega).ravel()

    derivative_sweep = []
    selected_solution = None
    for candidate_step in [1.0e-1, derivative_step, 2.0e-4, 1.0e-6, 1.0e-8]:
        candidate_bilinear = second_derivative_tensor(
            full_map, base, tangent, step=candidate_step
        )
        candidate_solution = solve_identity_center_quadratic(
            jacobian, tangent, extractor, candidate_bilinear
        )
        candidate_hessian, candidate_reduced, candidate_diagnostics = candidate_solution
        derivative_sweep.append(
            {
                "step": candidate_step,
                "hessian_relative_error": _relative_error(
                    candidate_hessian, analytic_hessian
                ),
                "reduced_quadratic_dynamics_norm": float(
                    np.linalg.norm(candidate_reduced)
                ),
                "homological_equation_relative_residual": (
                    candidate_diagnostics.global_equation_relative_residual
                ),
                "homological_condition_number": (
                    candidate_diagnostics.condition_number
                ),
            }
        )
        if candidate_step == derivative_step:
            selected_solution = candidate_solution
    if selected_solution is None:
        raise RuntimeError("selected derivative step was not included in its sweep")
    hessian, reduced_hessian, homological_diagnostics = selected_solution

    linear_chart = QuadraticChart(base, tangent, np.zeros_like(hessian))
    quadratic_chart = QuadraticChart(base, tangent, hessian)
    direction = np.array([0.35, 0.72, -0.48], dtype=np.float64)
    direction /= np.linalg.norm(direction)
    amplitudes = np.array([0.0025, 0.005, 0.01, 0.02], dtype=np.float64)
    linear_residuals = np.array(
        [
            invariance_residual(full_map, linear_chart, amplitude * direction)
            for amplitude in amplitudes
        ]
    )
    quadratic_residuals = np.array(
        [
            invariance_residual(full_map, quadratic_chart, amplitude * direction)
            for amplitude in amplitudes
        ]
    )
    exact_residuals = np.array(
        [
            np.linalg.norm(
                full_map(uniform_equilibrium(ny, nx, amplitude * direction).ravel())
                - uniform_equilibrium(ny, nx, amplitude * direction).ravel()
            )
            for amplitude in amplitudes
        ]
    )
    linear_order = log_log_slope(amplitudes, linear_residuals)
    quadratic_order = log_log_slope(amplitudes, quadratic_residuals)
    direction_seed = 20260731
    rng = np.random.default_rng(direction_seed)
    direction_orders: list[tuple[float, float]] = []
    for candidate_direction in rng.normal(size=(64, 3)):
        candidate_direction /= np.linalg.norm(candidate_direction)
        candidate_linear = [
            invariance_residual(
                full_map, linear_chart, amplitude * candidate_direction
            )
            for amplitude in amplitudes
        ]
        candidate_quadratic = [
            invariance_residual(
                full_map, quadratic_chart, amplitude * candidate_direction
            )
            for amplitude in amplitudes
        ]
        direction_orders.append(
            (
                log_log_slope(amplitudes, candidate_linear),
                log_log_slope(amplitudes, candidate_quadratic),
            )
        )
    linear_orders = np.array([item[0] for item in direction_orders])
    quadratic_orders = np.array([item[1] for item in direction_orders])
    hessian_relative_error = _relative_error(hessian, analytic_hessian)
    reduced_hessian_norm = float(np.linalg.norm(reduced_hessian))
    exact_residual_maximum = float(np.max(exact_residuals))
    gate_values = {
        "single_direction_linear_order": (linear_order, 1.8 <= linear_order <= 2.2),
        "single_direction_quadratic_order": (quadratic_order, quadratic_order >= 2.7),
        "direction_sweep_linear_order": (
            float(np.max(np.abs(linear_orders - 2.0))),
            bool(np.all((linear_orders >= 1.8) & (linear_orders <= 2.2))),
        ),
        "direction_sweep_quadratic_minimum": (
            float(np.min(quadratic_orders)),
            bool(np.all(quadratic_orders >= 2.7)),
        ),
        "hessian_relative_error": (hessian_relative_error, hessian_relative_error < 1.0e-10),
        "homological_equation_relative_residual": (
            homological_diagnostics.global_equation_relative_residual,
            homological_diagnostics.global_equation_relative_residual < 1.0e-9,
        ),
        "homological_condition_number": (
            homological_diagnostics.condition_number,
            homological_diagnostics.condition_number < 1.0e8,
        ),
        "gauge_residual": (
            homological_diagnostics.maximum_gauge_residual,
            homological_diagnostics.maximum_gauge_residual < 1.0e-11,
        ),
        "tangent_residual": (
            homological_diagnostics.tangent_relative_residual,
            homological_diagnostics.tangent_relative_residual < 1.0e-11,
        ),
        "left_invariance_residual": (
            homological_diagnostics.left_invariance_relative_residual,
            homological_diagnostics.left_invariance_relative_residual < 1.0e-11,
        ),
        "reduced_quadratic_dynamics_norm": (
            reduced_hessian_norm,
            reduced_hessian_norm < 1.0e-8,
        ),
        "exact_fixed_family_residual": (
            exact_residual_maximum,
            exact_residual_maximum < 1.0e-13,
        ),
        "largest_amplitude_improvement": (
            float(quadratic_residuals[-1] / linear_residuals[-1]),
            bool(quadratic_residuals[-1] < linear_residuals[-1]),
        ),
    }
    gates = {
        name: {"value": value, "passed": passed}
        for name, (value, passed) in gate_values.items()
    }
    improved = all(item["passed"] for item in gates.values())

    result = {
        "question": (
            "Does solving the quadratic homological equation improve the local "
            "invariance defect from second to third order?"
        ),
        "hypothesis": "The linear chart is O(|a|^2) and the quadratic chart is O(|a|^3).",
        "grid": [ny, nx],
        "reduced_dimension": 3,
        "second_derivative_step": derivative_step,
        "second_derivative_step_sweep": derivative_sweep,
        "amplitudes": amplitudes.tolist(),
        "linear_residuals": linear_residuals.tolist(),
        "quadratic_residuals": quadratic_residuals.tolist(),
        "exact_equilibrium_residuals": exact_residuals.tolist(),
        "observed_linear_order": linear_order,
        "observed_quadratic_order": quadratic_order,
        "direction_sweep": {
            "seed": direction_seed,
            "count": len(direction_orders),
            "minimum_linear_order": float(np.min(linear_orders)),
            "maximum_linear_order": float(np.max(linear_orders)),
            "minimum_quadratic_order": float(np.min(quadratic_orders)),
            "maximum_quadratic_order": float(np.max(quadratic_orders)),
        },
        "homological_equation_relative_residual": (
            homological_diagnostics.global_equation_relative_residual
        ),
        "homological_diagnostics": asdict(homological_diagnostics),
        "reduced_quadratic_dynamics_norm": reduced_hessian_norm,
        "hessian_relative_error_against_analytic_equilibrium": hessian_relative_error,
        "gates": gates,
        "outcome": "accepted" if improved else "rejected",
        "analysis": (
            "The exact homogeneous equilibrium family has identity reduced dynamics. "
            "Its curvature is kinetic, satisfies the gauge L H = 0, and is recovered "
            "by the coefficient-level homological solve."
        ),
        "next_change": (
            "After Q004b/Q005, repeat on a fixed-conservation-leaf nonzero Fourier "
            "candidate subspace, where R is not the identity and interactions "
            "generate zero-wave-number kinetic and second-harmonic corrections."
        ),
    }
    return result, quadratic_chart


def _low_wave_cycle(omega: float) -> dict[str, Any]:
    magnitudes = np.array([0.02, 0.04, 0.08, 0.12], dtype=np.float64)
    angles = np.array([0.0, np.pi / 8.0, np.pi / 4.0], dtype=np.float64)
    observations: list[dict[str, float]] = []
    for magnitude in magnitudes:
        for angle in angles:
            kx = float(magnitude * np.cos(angle))
            ky = float(magnitude * np.sin(angle))
            modes = classify_low_wave_hydrodynamic_modes(kx, ky, omega)
            shear = modes["shear"]
            acoustic_positive = modes["acoustic_positive"]
            acoustic_negative = modes["acoustic_negative"]
            effective_viscosity = -np.log(abs(shear.eigenvalue)) / magnitude**2
            positive_speed = abs(np.angle(acoustic_positive.eigenvalue)) / magnitude
            negative_speed = abs(np.angle(acoustic_negative.eigenvalue)) / magnitude
            observations.append(
                {
                    "wave_magnitude": float(magnitude),
                    "angle_radians": float(angle),
                    "effective_shear_viscosity": float(effective_viscosity),
                    "positive_acoustic_speed": float(positive_speed),
                    "negative_acoustic_speed": float(negative_speed),
                    "acoustic_conjugacy_error": float(
                        abs(
                            acoustic_positive.eigenvalue
                            - acoustic_negative.eigenvalue.conjugate()
                        )
                    ),
                    "minimum_hydrodynamic_score": min(
                        mode.hydrodynamic_score for mode in modes.values()
                    ),
                    "shear_transverse_fraction": shear.transverse_fraction,
                }
            )

    squared_wave = np.array(
        [item["wave_magnitude"] ** 2 for item in observations]
    )
    viscosities = np.array(
        [item["effective_shear_viscosity"] for item in observations]
    )
    acoustic_speeds = np.array(
        [
            0.5
            * (
                item["positive_acoustic_speed"]
                + item["negative_acoustic_speed"]
            )
            for item in observations
        ]
    )
    viscosity_intercept = float(np.polyfit(squared_wave, viscosities, 1)[1])
    sound_speed_intercept = float(
        np.polyfit(squared_wave, acoustic_speeds, 1)[1]
    )
    expected_viscosity = (1.0 / 3.0) * (1.0 / omega - 0.5)
    expected_sound_speed = 1.0 / np.sqrt(3.0)
    viscosity_relative_error = abs(viscosity_intercept - expected_viscosity) / abs(
        expected_viscosity
    )
    sound_speed_relative_error = abs(
        sound_speed_intercept - expected_sound_speed
    ) / expected_sound_speed
    gates = {
        "shear_viscosity_relative_error": {
            "value": viscosity_relative_error,
            "threshold": 1.0e-5,
            "passed": viscosity_relative_error < 1.0e-5,
        },
        "sound_speed_relative_error": {
            "value": sound_speed_relative_error,
            "threshold": 1.0e-5,
            "passed": bool(sound_speed_relative_error < 1.0e-5),
        },
        "acoustic_conjugacy_error": {
            "value": max(
                item["acoustic_conjugacy_error"] for item in observations
            ),
            "threshold": 1.0e-12,
            "passed": max(
                item["acoustic_conjugacy_error"] for item in observations
            )
            < 1.0e-12,
        },
        "minimum_hydrodynamic_score": {
            "value": min(
                item["minimum_hydrodynamic_score"] for item in observations
            ),
            "threshold": 0.99,
            "passed": min(
                item["minimum_hydrodynamic_score"] for item in observations
            )
            > 0.99,
        },
    }
    accepted = all(gate["passed"] for gate in gates.values())
    return {
        "question": (
            "Does moment-based low-k mode classification recover the physical "
            "D2Q9 shear viscosity and acoustic speed?"
        ),
        "hypothesis": (
            "The three modes with largest equilibrium-tangent participation are "
            "one transverse shear mode and one acoustic conjugate pair."
        ),
        "wave_magnitudes": magnitudes.tolist(),
        "angles_radians": angles.tolist(),
        "observations": observations,
        "expected_shear_viscosity": expected_viscosity,
        "extrapolated_shear_viscosity": viscosity_intercept,
        "shear_viscosity_relative_error": viscosity_relative_error,
        "expected_sound_speed": expected_sound_speed,
        "extrapolated_sound_speed": sound_speed_intercept,
        "sound_speed_relative_error": sound_speed_relative_error,
        "gates": gates,
        "outcome": "accepted" if accepted else "rejected",
        "analysis": (
            "Moment content identifies the physical cluster near k=0 and its "
            "small-k limits. This local result does not establish mode identity "
            "through eigenvalue collisions at larger wave number."
        ),
        "next_change": (
            "Add biorthogonal-overlap continuation and cluster tracking before "
            "choosing the slow-subspace cutoff."
        ),
    }


def _tt_cycle(chart: QuadraticChart, omega: float) -> dict[str, Any]:
    coefficients = polynomial_coefficient_tensor(
        chart.base, chart.tangent, chart.hessian
    )
    relative_tolerance = 1.0e-13
    cores = tt_svd(coefficients, relative_tolerance=relative_tolerance)
    dense_reconstruction = reconstruct(cores)
    coordinate = np.array([0.01, -0.015, 0.007], dtype=np.float64)
    dense_value = chart.evaluate(coordinate)
    tt_value = evaluate_polynomial(cores, coordinate)
    reconstruction_error = _relative_error(dense_reconstruction, coefficients)
    evaluation_error = _relative_error(tt_value, dense_value)
    full_map = lambda flat: bgk_periodic_step(
        np.asarray(flat).reshape(3, 3, 9), omega
    ).ravel()
    validation_coordinates = [
        coordinate,
        np.array([0.02, 0.01, -0.01]),
        np.array([-0.015, 0.012, 0.008]),
    ]
    invariance_residual_changes = []
    for validation_coordinate in validation_coordinates:
        dense_lift = chart.evaluate(validation_coordinate)
        tt_lift = evaluate_polynomial(cores, validation_coordinate)
        dense_defect = np.linalg.norm(full_map(dense_lift) - dense_lift)
        tt_defect = np.linalg.norm(full_map(tt_lift) - tt_lift)
        invariance_residual_changes.append(abs(float(tt_defect - dense_defect)))

    box_dense_parameters = int(coefficients.size)
    output = chart.base.size
    reduced = chart.reduced_dimension
    symmetric_quadratic_parameters = int(
        output * (1 + reduced + reduced * (reduced + 1) // 2)
    )
    full_hessian_parameters = int(output * (1 + reduced + reduced * reduced))
    coefficient_scale = float(np.max(np.abs(coefficients)))
    structural_threshold = 1.0e-12 * coefficient_scale
    nonzero_mask = np.abs(coefficients) > structural_threshold
    nonzero_scalar_count = int(np.count_nonzero(nonzero_mask))
    nonzero_fiber_count = int(np.count_nonzero(np.any(nonzero_mask, axis=0)))
    nonzero_fiber_parameters = int(nonzero_fiber_count * output)
    tt_core_stored_scalars = int(sum(core.size for core in cores))
    gates = {
        "coefficient_reconstruction": {
            "value": reconstruction_error,
            "threshold": 1.0e-11,
            "passed": reconstruction_error < 1.0e-11,
        },
        "chart_evaluation": {
            "value": evaluation_error,
            "threshold": 1.0e-11,
            "passed": evaluation_error < 1.0e-11,
        },
        "post_tt_invariance_change": {
            "value": max(invariance_residual_changes),
            "threshold": 1.0e-11,
            "passed": max(invariance_residual_changes) < 1.0e-11,
        },
    }
    accepted = all(gate["passed"] for gate in gates.values())
    return {
        "question": (
            "Can the verified quadratic chart be represented as an output-block "
            "polynomial TT without changing its invariance calculation?"
        ),
        "hypothesis": "TT-SVD preserves the dense chart within the requested tolerance.",
        "coefficient_shape": list(coefficients.shape),
        "requested_relative_tolerance": relative_tolerance,
        "tolerance_semantics": "discarded singular-value budget, not a reconstruction guarantee",
        "tt_ranks": tt_ranks(cores),
        "storage_baselines": {
            "box_dense_stored_scalar_count": box_dense_parameters,
            "full_hessian_stored_scalar_count": full_hessian_parameters,
            "symmetric_quadratic_stored_scalar_count": symmetric_quadratic_parameters,
            "fiber_sparse_stored_value_count": nonzero_fiber_parameters,
            "fiber_sparse_multi_index_count": nonzero_fiber_count,
            "scalar_sparse_stored_value_count_excluding_indices": nonzero_scalar_count,
            "scalar_sparse_multi_index_count": nonzero_scalar_count,
            "structural_zero_threshold": structural_threshold,
        },
        "tt_core_stored_scalar_count": tt_core_stored_scalars,
        "storage_ratios_over_tt_core_stored_scalars": {
            "box_dense": box_dense_parameters / tt_core_stored_scalars,
            "full_hessian": full_hessian_parameters / tt_core_stored_scalars,
            "symmetric_quadratic": symmetric_quadratic_parameters / tt_core_stored_scalars,
            "nonzero_fibers": nonzero_fiber_parameters / tt_core_stored_scalars,
            "nonzero_scalars_excluding_indices": (
                nonzero_scalar_count / tt_core_stored_scalars
            ),
        },
        "relative_reconstruction_error": reconstruction_error,
        "relative_evaluation_error": evaluation_error,
        "maximum_post_tt_invariance_residual_change": max(
            invariance_residual_changes
        ),
        "gates": gates,
        "outcome": "accepted" if accepted else "rejected",
        "analysis": (
            "This establishes representation equivalence only. TT core storage is smaller "
            "than a box-dense tensor but not than the thresholded fiber-sparse baseline. "
            "Stored scalar slots are not intrinsic degrees of freedom because TT cores "
            "have gauge freedom; index metadata, bytes, and evaluation cost are separate. "
            "The requested TT-SVD tolerance controls discarded singular values; "
            "the reported reconstruction, evaluation, and invariance gates are "
            "independent end-to-end checks. It does not yet establish that TT-cross "
            "can discover the chart or that ranks stay "
            "bounded for spatially varying slow modes."
        ),
        "next_change": (
            "Keep the Fourier-selection-rule sparse chart as a required baseline; "
            "after Q005/Q006, compare it with dense, TT-SVD, and held-out TT-cross "
            "representations before attempting an all-TT solve."
        ),
    }


def run_d2q9_baseline(omega: float = 1.2) -> dict[str, Any]:
    """Run the four baseline question-test-analysis-improvement cycles."""

    spectral = _spectral_cycle(omega)
    low_wave = _low_wave_cycle(omega)
    parameterization, chart = _parameterization_cycle(omega)
    tensor_train = _tt_cycle(chart, omega)
    all_accepted_or_informative = (
        spectral["outcome"] == "rejected"
        and low_wave["outcome"] == "accepted"
        and parameterization["outcome"] == "accepted"
        and tensor_train["outcome"] == "accepted"
    )
    return {
        "schema_version": 2,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "model": {
            "lattice": "D2Q9",
            "collision": "BGK",
            "omega": omega,
            "boundary": "periodic",
            "reference_state": "rho=1, momentum=(0,0)",
        },
        "parameterization_contract": {
            "chart_convention": "full state W(a)",
            "coordinates": ["delta_rho", "momentum_x", "momentum_y"],
            "gauge": "L @ (W(a) - f_star) = a",
            "strict_center_reduced_map": "R(a) = a",
            "grid_scope": "3x3 odd periodic square grid",
            "conservation_treatment": (
                "this uniform oracle crosses conserved leaves; future nonzero-mode "
                "charts are restricted to fixed global mass and momentum"
            ),
        },
        "cycles": [spectral, low_wave, parameterization, tensor_train],
        "baseline_gate": "passed" if all_accepted_or_informative else "failed",
        "interpretation": (
            "The strict homogeneous center is a valid coefficient-solver oracle, "
            "but spatial fluid reduction requires a deliberately selected candidate "
            "slow hydrodynamic subspace rather than a raw unit-circle eigenspace."
        ),
    }
