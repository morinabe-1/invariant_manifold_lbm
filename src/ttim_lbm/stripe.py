"""Fixed-conservation-leaf quadratic oracle on a y-independent D2Q9 stripe."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_sylvester

from .d2q9 import (
    D2Q9_VELOCITIES,
    bgk_periodic_step,
    conserved_moment_matrix,
    dense_linearized_map,
    exact_uniform_hessian,
    uniform_equilibrium,
)
from .manifold import QuadraticChart
from .nonresonance import fixed_leaf_kinetic_restriction, simple_hydrodynamic_modes

Array = npt.NDArray[np.float64]

MODE_ORDER = ("shear", "acoustic_positive", "acoustic_negative")


@dataclass(frozen=True)
class StripeHomologicalDiagnostics:
    """Independent algebraic checks for the restricted stripe solve."""

    smallest_singular_value: float
    condition_number: float
    tangent_relative_residual: float
    left_invariance_relative_residual: float
    duality_residual: float
    raw_symmetry_relative_residual: float
    homological_relative_residual: float
    maximum_homological_residual: float
    graph_gauge_relative_residual: float
    tangent_conservation_relative_residual: float
    hessian_conservation_relative_residual: float
    zero_wave_conserved_moment_relative_residual: float
    predicted_reduced_hessian_relative_norm: float
    output_sector_invariance_relative_residual: float
    forcing_sector_leakage_relative_norm: float
    hessian_fourier_leakage_relative_norm: float
    zero_wave_hessian_frobenius_norm: float
    positive_second_harmonic_hessian_frobenius_norm: float
    negative_second_harmonic_hessian_frobenius_norm: float


@dataclass(frozen=True)
class StripeQuadraticModel:
    """Dense quadratic chart and linear reduced map for one Fourier stripe."""

    size: int
    omega: float
    wave_number: float
    mode_order: tuple[str, str, str]
    chart: QuadraticChart
    linear_chart: QuadraticChart
    extractor: Array
    reduced_linear: Array
    jacobian: Array
    second_derivative: Array
    diagnostics: StripeHomologicalDiagnostics

    @property
    def reduced_dimension(self) -> int:
        return self.chart.reduced_dimension

    def full_map(self, state: npt.ArrayLike) -> Array:
        """Apply one nonlinear step to a flattened 1 x N stripe state."""

        flat = np.asarray(state, dtype=np.float64)
        if flat.shape != self.chart.base.shape:
            raise ValueError("state dimension does not match the stripe chart")
        return bgk_periodic_step(flat.reshape(1, self.size, 9), self.omega).ravel()

    def reduced_map(self, coordinates: npt.ArrayLike) -> Array:
        """Apply the registered linear reduced dynamics (R2 is zero)."""

        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match the stripe chart")
        return self.reduced_linear @ value

    def invariance_defect(
        self,
        coordinates: npt.ArrayLike,
        *,
        quadratic: bool = True,
    ) -> Array:
        """Return Phi(W(a)) - W(Lambda a) for either registered chart."""

        chart = self.chart if quadratic else self.linear_chart
        value = np.asarray(coordinates, dtype=np.float64)
        return self.full_map(chart.evaluate(value)) - chart.evaluate(
            self.reduced_map(value)
        )


def _require_stripe_size(size: int) -> int:
    if (
        isinstance(size, bool)
        or not isinstance(size, Integral)
        or size < 5
        or size % 2 == 0
    ):
        raise ValueError("stripe size must be an odd integer of at least five")
    return int(size)


def _real_tangent_and_extractor(
    size: int,
    wave_number: float,
    right_modes: npt.NDArray[np.complex128],
    left_modes: npt.NDArray[np.complex128],
) -> tuple[Array, Array]:
    """Realify conjugate Fourier pairs in interleaved real/imag coordinates."""

    scale = 1.0 / np.sqrt(2.0 * size)
    phase = np.exp(1j * wave_number * np.arange(size))
    tangent = np.empty((size * 9, 6), dtype=np.float64)
    extractor = np.empty((6, size * 9), dtype=np.float64)
    for mode_index in range(3):
        field = scale * phase[:, None] * right_modes[:, mode_index][None, :]
        tangent[:, 2 * mode_index] = (2.0 * field.real).ravel()
        tangent[:, 2 * mode_index + 1] = (-2.0 * field.imag).ravel()

        coefficient = (
            np.exp(-1j * wave_number * np.arange(size))[:, None]
            * np.conjugate(left_modes[:, mode_index])[None, :]
            / (size * scale)
        )
        extractor[2 * mode_index] = coefficient.real.ravel()
        extractor[2 * mode_index + 1] = coefficient.imag.ravel()
    return tangent, extractor


def _real_reduced_linear(eigenvalues: npt.NDArray[np.complex128]) -> Array:
    reduced = np.zeros((6, 6), dtype=np.float64)
    for mode_index, eigenvalue in enumerate(eigenvalues):
        block = np.array(
            [
                [eigenvalue.real, -eigenvalue.imag],
                [eigenvalue.imag, eigenvalue.real],
            ],
            dtype=np.float64,
        )
        start = 2 * mode_index
        reduced[start : start + 2, start : start + 2] = block
    return reduced


def _analytic_second_derivative(tangent: Array, size: int, omega: float) -> Array:
    """Assemble D2 Phi(base)[V., V.] by moments, equilibrium, and streaming."""

    field = tangent.reshape(size, 9, 6)
    moments = np.einsum("aq,xqj->xaj", conserved_moment_matrix(), field)
    local = omega * np.einsum(
        "qab,xaj,xbk->xqjk",
        exact_uniform_hessian(1, 1),
        moments,
        moments,
    )
    streamed = np.empty_like(local)
    for population, (cx, _) in enumerate(D2Q9_VELOCITIES.astype(int)):
        streamed[:, population] = np.roll(
            local[:, population],
            shift=int(cx),
            axis=0,
        )
    return streamed.reshape(size * 9, 6, 6)


def _output_sector_basis(size: int, wave_number: float, omega: float) -> Array:
    """Orthonormal real basis for zero-wave kinetic and +/-2k population sectors."""

    kinetic, _, _ = fixed_leaf_kinetic_restriction(omega)
    if np.linalg.norm(kinetic.imag) > 1.0e-13:
        raise np.linalg.LinAlgError("zero-wave kinetic basis did not realify")
    basis = np.zeros((size * 9, 24), dtype=np.float64)
    basis[:, :6] = np.tile(kinetic.real / np.sqrt(size), (size, 1))

    phase = 2.0 * wave_number * np.arange(size)
    cosine = np.sqrt(2.0 / size) * np.cos(phase)
    sine = -np.sqrt(2.0 / size) * np.sin(phase)
    for population in range(9):
        basis[population::9, 6 + population] = cosine
        basis[population::9, 15 + population] = sine
    return basis


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(numerator)
        / max(float(np.linalg.norm(denominator)), np.finfo(float).eps)
    )


def build_stripe_quadratic_model(
    size: int = 17,
    omega: float = 1.2,
) -> StripeQuadraticModel:
    """Construct the registered fixed-leaf stripe chart by a sector solve."""

    size = _require_stripe_size(size)
    omega = float(omega)
    wave_number = 2.0 * np.pi / size
    modes = simple_hydrodynamic_modes(wave_number, 0.0, omega)
    right_modes = np.column_stack(
        [modes[label].right_eigenvector for label in MODE_ORDER]
    )
    left_modes = np.column_stack(
        [modes[label].left_eigenvector for label in MODE_ORDER]
    )
    eigenvalues = np.asarray(
        [modes[label].eigenvalue for label in MODE_ORDER],
        dtype=np.complex128,
    )

    tangent, extractor = _real_tangent_and_extractor(
        size,
        wave_number,
        right_modes,
        left_modes,
    )
    reduced_linear = _real_reduced_linear(eigenvalues)
    jacobian = dense_linearized_map(1, size, omega)
    second_derivative = _analytic_second_derivative(tangent, size, omega)

    output_basis = _output_sector_basis(size, wave_number, omega)
    output_linear = output_basis.T @ jacobian @ output_basis
    reduced_quadratic = np.kron(reduced_linear, reduced_linear)
    restricted_forcing = output_basis.T @ second_derivative.reshape(size * 9, 36)
    restricted_hessian = solve_sylvester(
        output_linear,
        -reduced_quadratic,
        -restricted_forcing,
    )
    raw_hessian = (output_basis @ restricted_hessian).reshape(size * 9, 6, 6)
    raw_symmetry = _relative_norm(
        raw_hessian - raw_hessian.swapaxes(1, 2),
        raw_hessian,
    )
    hessian = 0.5 * (raw_hessian + raw_hessian.swapaxes(1, 2))

    hessian_matrix = hessian.reshape(size * 9, 36)
    transformed_hessian = (hessian_matrix @ reduced_quadratic).reshape(
        size * 9,
        6,
        6,
    )
    equation = (
        np.einsum("il,ljk->ijk", jacobian, hessian)
        - transformed_hessian
        + second_derivative
    )
    operator = np.kron(np.eye(36), output_linear) - np.kron(
        reduced_quadratic.T,
        np.eye(24),
    )
    singular_values = np.linalg.svd(operator, compute_uv=False)

    conservation = np.tile(conserved_moment_matrix(), (1, size))
    zero_wave = hessian.reshape(size, 9, 6, 6).mean(axis=0)
    zero_wave_conservation = np.einsum(
        "aq,qjk->ajk",
        conserved_moment_matrix(),
        zero_wave,
    )
    hessian_fourier = np.fft.fft(
        hessian.reshape(size, 9, 6, 6),
        axis=0,
    ) / size
    excluded = [index for index in range(size) if index not in (0, 2, size - 2)]
    fourier_leakage = _relative_norm(hessian_fourier[excluded], hessian_fourier)

    forcing_matrix = second_derivative.reshape(size * 9, 36)
    forcing_projection = output_basis @ (output_basis.T @ forcing_matrix)
    base = uniform_equilibrium(1, size, np.zeros(3)).ravel()
    chart = QuadraticChart(base=base, tangent=tangent, hessian=hessian)
    linear_chart = QuadraticChart(
        base=base,
        tangent=tangent,
        hessian=np.zeros_like(hessian),
    )
    diagnostics = StripeHomologicalDiagnostics(
        smallest_singular_value=float(singular_values[-1]),
        condition_number=float(singular_values[0] / singular_values[-1]),
        tangent_relative_residual=_relative_norm(
            jacobian @ tangent - tangent @ reduced_linear,
            tangent,
        ),
        left_invariance_relative_residual=_relative_norm(
            extractor @ jacobian - reduced_linear @ extractor,
            extractor,
        ),
        duality_residual=float(np.linalg.norm(extractor @ tangent - np.eye(6))),
        raw_symmetry_relative_residual=raw_symmetry,
        homological_relative_residual=_relative_norm(equation, second_derivative),
        maximum_homological_residual=float(
            max(np.linalg.norm(equation[:, j, k]) for j in range(6) for k in range(6))
        ),
        graph_gauge_relative_residual=_relative_norm(
            extractor @ hessian_matrix,
            hessian_matrix,
        ),
        tangent_conservation_relative_residual=_relative_norm(
            conservation @ tangent,
            tangent,
        ),
        hessian_conservation_relative_residual=_relative_norm(
            conservation @ hessian_matrix,
            hessian_matrix,
        ),
        zero_wave_conserved_moment_relative_residual=_relative_norm(
            zero_wave_conservation,
            zero_wave,
        ),
        predicted_reduced_hessian_relative_norm=_relative_norm(
            extractor @ forcing_matrix,
            forcing_matrix,
        ),
        output_sector_invariance_relative_residual=_relative_norm(
            jacobian @ output_basis - output_basis @ output_linear,
            jacobian @ output_basis,
        ),
        forcing_sector_leakage_relative_norm=_relative_norm(
            forcing_matrix - forcing_projection,
            forcing_matrix,
        ),
        hessian_fourier_leakage_relative_norm=fourier_leakage,
        zero_wave_hessian_frobenius_norm=float(np.linalg.norm(hessian_fourier[0])),
        positive_second_harmonic_hessian_frobenius_norm=float(
            np.linalg.norm(hessian_fourier[2])
        ),
        negative_second_harmonic_hessian_frobenius_norm=float(
            np.linalg.norm(hessian_fourier[size - 2])
        ),
    )
    return StripeQuadraticModel(
        size=size,
        omega=omega,
        wave_number=wave_number,
        mode_order=MODE_ORDER,
        chart=chart,
        linear_chart=linear_chart,
        extractor=extractor,
        reduced_linear=reduced_linear,
        jacobian=jacobian,
        second_derivative=second_derivative,
        diagnostics=diagnostics,
    )
