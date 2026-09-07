"""Post-stream scalar damping for a *modified*, fixed-leaf D3Q27 map.

The sealed unmodified BGK and quadratic solvers are reused without edits.
The biharmonic filter preserves leading viscosity, not finite-wave dynamics
or global population positivity. All coefficient solves retain Q012c's tests.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from itertools import combinations_with_replacement, product
from numbers import Integral
from typing import Any

import numpy as np
from scipy.linalg import svd

from research import d3q27 as d3
from research import d3q27_quadratic as q
from research import d3q27_spectra as spectra
from research import q012b_d3q27_spectral as q012b

ETAS = (0.01, 0.02, 0.05, 0.1)
POWERS = (1, 2)
RADII = (0.04, 0.02, 0.01, 0.005)


def parameters(eta: float, power: int) -> tuple[float, int]:
    if isinstance(eta, bool) or not np.isfinite(eta) or not 0 <= eta <= 0.1:
        raise ValueError("eta must be finite and in [0, 0.1]")
    if isinstance(power, bool) or not isinstance(power, Integral) or power not in POWERS:
        raise ValueError("filter power must be one or two")
    return float(eta), int(power)


def multiplier(wavevector: np.ndarray, eta: float, power: int) -> float:
    eta, power = parameters(eta, power)
    k = d3._real_array(wavevector)
    if k.shape != (3,):
        raise ValueError("wavevector must have three components")
    return float(1 - eta * np.sum(np.sin(k / 2) ** 2) ** power)


def wave_multiplier(wave: q.Wave, size: int, eta: float, power: int) -> float:
    wave = q.canonical_wave(wave, size)
    return multiplier(2 * np.pi * np.asarray(wave) / size, eta, power)


def scaled_laplacian(state: np.ndarray) -> np.ndarray:
    f = d3._state(state, allow_complex=True)
    result = np.zeros_like(f)
    for axis in range(3):
        result += (2 * f - np.roll(f, 1, axis) - np.roll(f, -1, axis)) / 4
    return result


def apply_filter(state: np.ndarray, eta: float, power: int) -> np.ndarray:
    eta, power = parameters(eta, power)
    f = d3._state(state, allow_complex=True)
    if eta == 0:
        return f.copy()
    derivative = scaled_laplacian(f)
    if power == 2:
        # Square of the SUM of directional operators, including cross terms.
        derivative = scaled_laplacian(derivative)
    return f - eta * derivative


def periodic_step(state: np.ndarray, omega: float, eta: float, power: int) -> np.ndarray:
    parameters(eta, power)
    return apply_filter(d3.bgk_periodic_step(state, omega), eta, power)


def fourier_symbol(k: np.ndarray, omega: float, eta: float, power: int) -> np.ndarray:
    return multiplier(k, eta, power) * d3.fourier_symbol(k, omega)


def mixed_hessian(left: np.ndarray, right: np.ndarray, omega: float) -> np.ndarray:
    moments = d3.conserved_moment_matrix()
    return d3.stream_periodic(
        omega
        * np.einsum(
            "qab,...a,...b->...q",
            d3.equilibrium_hessian_at_rest(),
            np.einsum("aq,...q->...a", moments, left),
            np.einsum("aq,...q->...a", moments, right),
        )
    )


def relative_error(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(1e-14, float(np.linalg.norm(right))))


def fft_filter(state: np.ndarray, eta: float, power: int) -> np.ndarray:
    """Independent Fourier evaluation used only as a physical-filter oracle."""
    axes = (0, 1, 2)
    kz, ky, kx = np.meshgrid(
        *(2 * np.pi * np.fft.fftfreq(n) for n in state.shape[:3]), indexing="ij"
    )
    symbol = 1 - eta * (np.sin(kx / 2) ** 2 + np.sin(ky / 2) ** 2 + np.sin(kz / 2) ** 2) ** power
    return np.fft.ifftn(np.fft.fftn(state, axes=axes) * symbol[..., None], axes=axes)


def _d2_filter(state: np.ndarray, eta: float, power: int) -> np.ndarray:
    # Explicit independent two-axis stencil, not a collapsed D3 invocation.
    def stencil(f: np.ndarray) -> np.ndarray:
        return (
            4 * f - np.roll(f, 1, 0) - np.roll(f, -1, 0) - np.roll(f, 1, 1) - np.roll(f, -1, 1)
        ) / 4

    derivative = stencil(state)
    return state - eta * (derivative if power == 1 else stencil(derivative))


def map_controls() -> dict[str, Any]:
    rng = np.random.default_rng(2026090707)
    noncube = rng.standard_normal((3, 5, 7, 27))
    cube = rng.standard_normal((5, 5, 5, 27))
    d2 = rng.standard_normal((5, 7, 9))
    lifted = d3.lift_d2q9(d2, 3)
    impulse = np.zeros((7, 7, 7, 27))
    impulse[0, 0, 0, 0] = 1
    base = d3.uniform_equilibrium((5, 5, 5), np.zeros(4))
    initial = base + 1e-4 * np.random.default_rng(2026090708).standard_normal(base.shape)
    records = []
    for power, eta in product(POWERS, ETAS):
        filtered = apply_filter(noncube, eta, power)
        fourier_error = relative_error(filtered, fft_filter(noncube, eta, power))
        mean_error = float(np.max(np.abs(filtered.mean((0, 1, 2)) - noncube.mean((0, 1, 2)))))
        moment_error = float(
            np.max(
                np.abs(
                    d3.global_conserved_quantities(filtered)
                    - d3.global_conserved_quantities(noncube)
                )
            )
            / np.prod(noncube.shape[:3])
        )
        streaming_error = relative_error(
            apply_filter(d3.stream_periodic(noncube), eta, power),
            d3.stream_periodic(filtered),
        )
        filtered_cube = apply_filter(cube, eta, power)
        covariance_error = max(
            relative_error(
                apply_filter(d3.rotate_periodic_state(cube, rotation), eta, power),
                d3.rotate_periodic_state(filtered_cube, rotation),
            )
            for rotation in d3.cubic_symmetries()
        )
        lift_error = relative_error(
            apply_filter(lifted, eta, power), d3.lift_d2q9(_d2_filter(d2, eta, power), 3)
        )
        stencil = apply_filter(impulse, eta, power)[..., 0]
        expected_l1 = 1 if power == 1 else 1 + 15 * eta / 4
        stencil_audit = {
            "sum": float(stencil.sum()),
            "l1_norm": float(np.abs(stencil).sum()),
            "expected_l1_norm": expected_l1,
            "negative_count": int(np.count_nonzero(stencil < 0)),
            "nonzero_count": int(np.count_nonzero(stencil)),
        }
        rollouts = []
        for omega in q012b.OMEGAS:
            state = initial.copy()
            conserved = d3.global_conserved_quantities(state) / 125
            minimum, drift, finite = float(state.min()), 0.0, True
            for _ in range(32):
                state = periodic_step(state, omega, eta, power)
                finite = finite and bool(np.all(np.isfinite(state)))
                minimum = min(minimum, float(state.min()))
                drift = max(
                    drift,
                    float(np.max(np.abs(d3.global_conserved_quantities(state) / 125 - conserved))),
                )
            rollouts.append(
                {
                    "omega": omega,
                    "steps": 32,
                    "finite": finite,
                    "minimum_population": minimum,
                    "maximum_site_average_conservation_drift": drift,
                    "passed": finite and minimum > 0 and drift <= 2e-13,
                }
            )
        identity = np.array_equal(apply_filter(noncube, 0, power), noncube) and np.array_equal(
            periodic_step(initial, 1.2, 0, power), d3.bgk_periodic_step(initial, 1.2)
        )
        gates = {
            "zero_eta_bitwise_identity": identity,
            "independent_fft": fourier_error <= 5e-13,
            "mean_and_four_moments": max(mean_error, moment_error) <= 5e-12,
            "stream_commutation": streaming_error <= 5e-12,
            "all_48_cubic_operations": covariance_error <= 5e-12,
            "independent_d2_lift": lift_error <= 5e-12,
            "stencil": abs(stencil_audit["sum"] - 1) <= 5e-13
            and abs(stencil_audit["l1_norm"] - expected_l1) <= 5e-13
            and stencil_audit["negative_count"] == (0 if power == 1 else 18)
            and stencil_audit["nonzero_count"] == (7 if power == 1 else 25),
            "finite_positive_sample_rollouts": all(r["passed"] for r in rollouts),
        }
        records.append(
            {
                "power": power,
                "eta": eta,
                "fft_relative_error": fourier_error,
                "mean_error": mean_error,
                "moment_error": moment_error,
                "stream_relative_error": streaming_error,
                "cubic_relative_error": covariance_error,
                "d2_lift_relative_error": lift_error,
                "stencil": stencil_audit,
                "rollouts": rollouts,
                "gates": gates,
                "passed": all(gates.values()),
            }
        )
    return {"records": records, "passed": len(records) == 8 and all(r["passed"] for r in records)}


def hydrodynamic_controls() -> dict[str, Any]:
    points = {}
    for omega, (name, raw_direction), radius in product(q012b.OMEGAS, q012b.RAYS.items(), RADII):
        direction = np.array(raw_direction, dtype=float)
        direction /= np.linalg.norm(direction)
        points[omega, name, radius] = spectra.cluster_point(radius * direction, omega)
    records, nyquist = [], []
    for power, eta, omega, name in product(POWERS, ETAS, q012b.OMEGAS, q012b.RAYS):
        viscosity = (1 / omega - 0.5) / 3
        expected_viscosity = viscosity + (eta / 4 if power == 1 else 0)
        samples = []
        for radius in RADII:
            point = points[omega, name, radius]
            s = float(np.sum(np.sin(point.wavevector / 2) ** 2))
            extra_decay = float(-np.log1p(-eta * s**power))
            shear_rates = (-np.log(np.abs(point.shear_values)) + extra_decay) / radius**2
            speeds = np.abs(np.angle(point.acoustic_values)) / radius
            samples.append(
                {
                    "radius": radius,
                    "cluster_passed": point.passed,
                    "shear_decay_rates": shear_rates.tolist(),
                    "acoustic_speeds": speeds.tolist(),
                    "maximum_shear_relative_error": float(
                        np.max(np.abs(shear_rates / expected_viscosity - 1))
                    ),
                    "maximum_acoustic_relative_error": float(
                        np.max(np.abs(speeds * np.sqrt(3) - 1))
                    ),
                    "additional_decay": extra_decay,
                    "quartic_coefficient_relative_error": None
                    if power == 1
                    else abs(extra_decay / radius**4 / (eta / 16) - 1),
                }
            )
        last = samples[-1]
        records.append(
            {
                "power": power,
                "eta": eta,
                "omega": omega,
                "ray": name,
                "bgk_viscosity": viscosity,
                "expected_effective_viscosity": expected_viscosity,
                "samples": samples,
                "passed": all(s["cluster_passed"] for s in samples)
                and last["maximum_shear_relative_error"] <= 1e-4
                and last["maximum_acoustic_relative_error"] <= 1e-5
                and (power == 1 or last["quartic_coefficient_relative_error"] <= 1e-4),
            }
        )
    for power, eta, omega, axis in product(POWERS, ETAS, q012b.OMEGAS, range(3)):
        k = np.zeros(3)
        k[axis] = np.pi
        values = np.linalg.eigvals(fourier_symbol(k, omega, eta, power))
        error = float(np.min(np.abs(values + (1 - eta))))
        nyquist.append(
            {
                "power": power,
                "eta": eta,
                "omega": omega,
                "axis": axis,
                "eigenvalue_error": error,
                "passed": error <= 5e-12,
            }
        )
    return {
        "records": records,
        "direct_nyquist": nyquist,
        "passed": len(records) == 128
        and len(nyquist) == 96
        and all(r["passed"] for r in records + nyquist),
    }


def hessian_controls() -> dict[str, Any]:
    rng = np.random.default_rng(2026090709)
    base = d3.uniform_equilibrium((3, 3, 3), np.zeros(4))
    left, right = rng.standard_normal((2,) + base.shape)
    left /= np.linalg.norm(left)
    right /= np.linalg.norm(right)
    physical_hessian = mixed_hessian(left, right, 1.2)
    records = []
    for power, eta in product(POWERS, ETAS):
        analytic = apply_filter(physical_hessian, eta, power)
        samples = []
        for step in (1e-3, 5e-4, 2.5e-4):
            mixed = (
                periodic_step(base + step * (left + right), 1.2, eta, power)
                - periodic_step(base + step * (left - right), 1.2, eta, power)
                - periodic_step(base + step * (-left + right), 1.2, eta, power)
                + periodic_step(base - step * (left + right), 1.2, eta, power)
            ) / (4 * step**2)
            samples.append({"step": step, "relative_error": relative_error(mixed, analytic)})
        wrong = mixed_hessian(apply_filter(left, eta, power), apply_filter(right, eta, power), 1.2)
        wrong_error = relative_error(wrong, analytic)
        records.append(
            {
                "power": power,
                "eta": eta,
                "samples": samples,
                "wrong_input_filter_relative_error": wrong_error,
                "passed": samples[-1]["relative_error"] <= 1e-5 and wrong_error > 1e-3,
            }
        )
    return {"records": records, "passed": len(records) == 8 and all(r["passed"] for r in records)}


@dataclass(frozen=True)
class CoefficientContext:
    size: int
    omega: float
    frames: dict[q.Wave, q.HydroFrame]
    frame_audit: dict[str, Any]
    blocks: tuple[q.InputBlock, ...]
    sectors: dict[q.Wave, q.ExternalSector]
    grid: dict[str, Any]


class HomologicalSvdFailure(np.linalg.LinAlgError):
    """A reproducible numerical obstruction, never an accepted coefficient."""

    def __init__(self, evidence: dict[str, Any]):
        super().__init__("registered homological SVD did not converge")
        self.evidence = evidence


def svd_failure_evidence(
    left: q.InputBlock, right: q.InputBlock, context: CoefficientContext, eta: float, power: int
) -> dict[str, Any]:
    wave = q.canonical_wave(tuple(a + b for a, b in zip(left.wave, right.wave)), context.size)
    sector = context.sectors[wave]
    ml = wave_multiplier(left.wave, context.size, eta, power)
    mr = wave_multiplier(right.wave, context.size, eta, power)
    mo = wave_multiplier(wave, context.size, eta, power)
    inputs, forcing, _ = q.product_forcing(
        replace(left, dynamics=ml * left.dynamics),
        replace(right, dynamics=mr * right.dynamics),
        wave,
        context.size,
        context.omega * mo,
    )
    external = mo * sector.dynamics
    forcing = sector.basis.conj().T @ sector.projection @ forcing
    operator = q.homological_operator(external, inputs)
    diagnostics = []
    for driver in ("gesdd", "gesvd"):
        for repeat in range(3):
            try:
                u, singular, vh = svd(
                    operator, full_matrices=False, check_finite=False, lapack_driver=driver
                )
                retained = singular > 100 * np.finfo(float).eps * len(operator) * singular[0]
                solution = -(
                    vh[retained].conj().T
                    @ (
                        (u[:, retained].conj().T @ forcing.reshape(-1, order="F"))
                        / singular[retained]
                    )
                ).reshape(forcing.shape, order="F")
                diagnostics.append(
                    {
                        "driver": driver,
                        "repeat": repeat,
                        "converged": True,
                        "condition_number": float(singular[0] / singular[-1])
                        if all(retained)
                        else None,
                        "reconstruction_relative_error": relative_error(
                            (u * singular) @ vh, operator
                        ),
                        "left_orthogonality_error": float(
                            np.linalg.norm(u.conj().T @ u - np.eye(len(operator)))
                        ),
                        "right_orthogonality_error": float(
                            np.linalg.norm(vh @ vh.conj().T - np.eye(len(operator)))
                        ),
                        "solve_relative_residual": float(
                            np.linalg.norm(external @ solution - solution @ inputs + forcing)
                            / max(1e-14, np.linalg.norm(forcing))
                        ),
                    }
                )
            except np.linalg.LinAlgError as error:
                diagnostics.append(
                    {"driver": driver, "repeat": repeat, "converged": False, "error": str(error)}
                )
    return {
        "size": context.size,
        "omega": context.omega,
        "eta": eta,
        "power": power,
        "left_wave": list(left.wave),
        "left_label": left.label,
        "right_wave": list(right.wave),
        "right_label": right.label,
        "output_wave": list(wave),
        "operator_dimension": len(operator),
        "finite_operator_and_forcing": bool(
            np.isfinite(operator).all() and np.isfinite(forcing).all()
        ),
        "operator_real": operator.real.tolist(),
        "operator_imag": operator.imag.tolist(),
        "forcing_real": forcing.real.tolist(),
        "forcing_imag": forcing.imag.tolist(),
        "diagnostics": diagnostics,
        "scope": "alternative driver is diagnostic only; it does not replace the registered solver or qualify this condition",
    }


def build_context(size: int, omega: float) -> CoefficientContext:
    frames, audit = q.build_frames(size, omega)
    waves = q.shell_waves(3)
    blocks = tuple(b for wave in waves for b in frames[wave].blocks)
    outputs = {
        q.canonical_wave(tuple(a + b for a, b in zip(left.wave, right.wave)), size)
        for left, right in combinations_with_replacement(blocks, 2)
    }
    sectors = {w: q.external_sector(w, size, omega, frames.get(w)) for w in sorted(outputs)}
    return CoefficientContext(
        size, omega, frames, audit, blocks, sectors, q.grid_spectrum(size, omega, frames)
    )


def audit_scaled_pair(
    left: q.InputBlock, right: q.InputBlock, context: CoefficientContext, eta: float, power: int
) -> dict[str, Any]:
    wave = q.canonical_wave(tuple(a + b for a, b in zip(left.wave, right.wave)), context.size)
    sector = context.sectors[wave]
    if eta == 0:
        return q.audit_pair(
            left, right, context.size, context.omega, sector, context.frames.get(wave)
        )
    mu_left = wave_multiplier(left.wave, context.size, eta, power)
    mu_right = wave_multiplier(right.wave, context.size, eta, power)
    mu_output = wave_multiplier(wave, context.size, eta, power)
    # audit_pair's omega argument is used ONLY in product_forcing as the
    # Hessian prefactor. It does not construct or alter a collision symbol.
    # Passing omega*mu_output therefore scales B at the OUTPUT wave, while
    # each input and output linear dynamics below receives its own multiplier.
    return q.audit_pair(
        replace(left, dynamics=mu_left * left.dynamics),
        replace(right, dynamics=mu_right * right.dynamics),
        context.size,
        context.omega * mu_output,
        replace(sector, dynamics=mu_output * sector.dynamics),
        context.frames.get(wave),
    )


def coefficient_screen(context: CoefficientContext, eta: float, power: int) -> dict[str, Any]:
    parameters(eta, power)
    records = []
    for left, right in combinations_with_replacement(context.blocks, 2):
        try:
            records.append(audit_scaled_pair(left, right, context, eta, power))
        except np.linalg.LinAlgError as error:
            evidence = svd_failure_evidence(left, right, context, eta, power)
            evidence["completed_pairs_in_failed_condition"] = len(records)
            raise HomologicalSvdFailure(evidence) from error
    return summarize_pairs(records, len(context.blocks))


def summarize_pairs(records: list[dict[str, Any]], block_count: int) -> dict[str, Any]:
    conditioned = [r for r in records if r["condition_number"] is not None]
    return {
        "shell": 3,
        "wave_count": 26,
        "real_coordinate_count": 104,
        "input_block_count": block_count,
        "pair_count": len(records),
        "product_dimension_sum": sum(r["product_dimension"] for r in records),
        "coverage_passed": block_count == 78
        and len(records) == 3081
        and sum(r["product_dimension"] for r in records) == 5460,
        "status_counts": dict(sorted(Counter(r["status"] for r in records).items())),
        "maximum_structural_error": max(r["structural_error"] for r in records),
        "worst_nonsingular_condition": max(conditioned, key=lambda r: r["condition_number"]),
        "first_singular_pair": next((r for r in records if r["condition_number"] is None), None),
        "pair_records": records,
        "coefficient_prequalified": all(r["passed"] for r in records),
        "failed_pair_count": sum(not r["passed"] for r in records),
        "residual_only_failure_count": sum(
            r["status"] == "nonsingular_practical"
            and r["solve_relative_residual"] > 1e-10
            and max(r["graph_gauge_error"], r["zero_wave_moment_error"]) <= 5e-12
            for r in records
        ),
        "maximum_solve_relative_residual": max(r["solve_relative_residual"] for r in records),
        "maximum_response_global_l2_norm": max(r["response_global_l2_norm"] for r in records),
    }


def scaled_grid(grid: dict[str, Any], eta: float, power: int) -> dict[str, Any]:
    parameters(eta, power)
    if eta == 0:
        return grid
    rows = []
    for original in grid["rows"]:
        mu = wave_multiplier(original["wave"], grid["size"], eta, power)
        row = dict(original)
        for key in (
            "full_values",
            "full_norm",
            "selected_values",
            "external_values",
            "external_norm",
            "local_schur_sep",
        ):
            if key in row:
                row[key] = mu * row[key]
        rows.append(row)
    return {**grid, "rows": rows}


def direct_grid_control() -> dict[str, Any]:
    """Full 17^3 eigensolves of the modified symbol, not scaled base eigenspectra."""
    size, omega, eta, power = 17, 1.2, 0.05, 2
    frames, _ = q.build_frames(size, omega)
    quotient = q.normal_ordering(scaled_grid(q.grid_spectrum(size, omega, frames), eta, power), 3)
    rows = []
    for wave in product(range(-8, 9), repeat=3):
        k = 2 * np.pi * np.asarray(wave) / size
        matrix = fourier_symbol(k, omega, eta, power)
        if wave == (0, 0, 0):
            basis = q.external_sector(wave, size, omega, None).basis
            restriction = basis.conj().T @ matrix @ basis
        else:
            restriction = matrix
        row = {
            "wave": wave,
            "multiplicity": 1,
            "full_values": np.linalg.eigvals(restriction),
            "full_norm": float(np.linalg.norm(restriction, ord=2)),
        }
        if wave in frames:
            frame = frames[wave]
            basis = q.external_sector(wave, size, omega, frame).basis
            external = basis.conj().T @ matrix @ basis
            row.update(
                {
                    "selected_values": np.linalg.eigvals(frame.dual @ matrix @ frame.basis),
                    "external_values": np.linalg.eigvals(external),
                    "external_norm": float(np.linalg.norm(external, ord=2)),
                    "projector_norm": frame.diagnostics["projector_norm"],
                    "local_schur_sep": multiplier(k, eta, power)
                    * frame.diagnostics["local_schur_sep"],
                }
            )
        rows.append(row)
    grid = {
        "size": size,
        "omega": omega,
        "orbit_count": len(rows),
        "represented_wave_count": len(rows),
        "fixed_leaf_dimension": 27 * size**3 - 4,
        "rows": rows,
    }
    direct = q.normal_ordering(grid, 3)
    errors = {
        "selected_modulus": abs(
            quotient["fastest_selected"]["modulus"] - direct["fastest_selected"]["modulus"]
        ),
        "external_modulus": abs(
            quotient["slowest_external"]["modulus"] - direct["slowest_external"]["modulus"]
        ),
        "external_norm": abs(
            quotient["maximum_external_one_step_norm"] - direct["maximum_external_one_step_norm"]
        ),
    }
    return {
        "size": size,
        "omega": omega,
        "eta": eta,
        "power": power,
        "scaled_orbit": quotient,
        "direct": direct,
        "errors": errors,
        "passed": quotient["coverage_passed"]
        and direct["coverage_passed"]
        and direct["selected_dimension"] == 104
        and max(errors.values()) <= 5e-12,
    }
