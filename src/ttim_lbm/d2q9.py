"""Dense D2Q9 oracle and its linearization about a rest equilibrium."""

from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

D2Q9_VELOCITIES: Array = np.array(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [-1.0, 0.0],
        [0.0, -1.0],
        [1.0, 1.0],
        [-1.0, 1.0],
        [-1.0, -1.0],
        [1.0, -1.0],
    ],
    dtype=np.float64,
)
D2Q9_WEIGHTS: Array = np.array(
    [4.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0]
    + [1.0 / 36.0] * 4,
    dtype=np.float64,
)
D2Q9_CS2 = 1.0 / 3.0


def _require_omega(omega: float) -> float:
    value = float(omega)
    if not np.isfinite(value) or not 0.0 < value < 2.0:
        raise ValueError(
            "omega must be finite and in the positive-viscosity interval (0, 2)"
        )
    return value


def _require_grid(ny: int, nx: int) -> tuple[int, int]:
    if (
        isinstance(ny, bool)
        or isinstance(nx, bool)
        or not isinstance(ny, Integral)
        or not isinstance(nx, Integral)
        or ny <= 0
        or nx <= 0
    ):
        raise ValueError("grid sizes must be positive integers")
    return int(ny), int(nx)


def _require_state(state: npt.ArrayLike) -> Array:
    array = np.asarray(state, dtype=np.float64)
    if array.ndim != 3 or array.shape[-1] != 9:
        raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
    return array


def macroscopic(state: npt.ArrayLike) -> tuple[Array, Array]:
    """Return density and momentum, with momentum in the final axis."""

    populations = _require_state(state)
    density = populations.sum(axis=-1)
    momentum = np.einsum("...q,qd->...d", populations, D2Q9_VELOCITIES)
    return density, momentum


def equilibrium(density: npt.ArrayLike, momentum: npt.ArrayLike) -> Array:
    """Second-order isothermal D2Q9 equilibrium in conserved coordinates."""

    rho = np.asarray(density, dtype=np.float64)
    j = np.asarray(momentum, dtype=np.float64)
    if j.shape != rho.shape + (2,):
        raise ValueError("momentum must have shape density.shape + (2,)")
    if np.any(rho <= 0.0):
        raise ValueError("density must be strictly positive")

    velocity = j / rho[..., None]
    cu = np.einsum("...d,qd->...q", velocity, D2Q9_VELOCITIES)
    speed_squared = np.sum(velocity * velocity, axis=-1)
    return (
        rho[..., None]
        * D2Q9_WEIGHTS
        * (1.0 + 3.0 * cu + 4.5 * cu * cu - 1.5 * speed_squared[..., None])
    )


def collide_bgk(state: npt.ArrayLike, omega: float) -> Array:
    """Apply a local BGK collision without forcing."""

    omega = _require_omega(omega)
    populations = _require_state(state)
    density, momentum = macroscopic(populations)
    return populations + omega * (equilibrium(density, momentum) - populations)


def stream_periodic(post_collision: npt.ArrayLike) -> Array:
    """Stream populations on a two-dimensional periodic lattice."""

    post = _require_state(post_collision)
    streamed = np.empty_like(post)
    for q, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
        streamed[..., q] = np.roll(post[..., q], shift=(cy, cx), axis=(0, 1))
    return streamed


def bgk_periodic_step(state: npt.ArrayLike, omega: float) -> Array:
    """One collide-then-stream D2Q9 step with periodic boundaries."""

    return stream_periodic(collide_bgk(state, omega))


def uniform_equilibrium(ny: int, nx: int, coordinates: npt.ArrayLike) -> Array:
    """Exact three-dimensional homogeneous equilibrium family near rho=1, u=0."""

    ny, nx = _require_grid(ny, nx)
    a = np.asarray(coordinates, dtype=np.float64)
    if a.shape != (3,):
        raise ValueError("coordinates must be [delta_rho, momentum_x, momentum_y]")
    density = np.full((ny, nx), 1.0 + a[0], dtype=np.float64)
    momentum = np.empty((ny, nx, 2), dtype=np.float64)
    momentum[..., 0] = a[1]
    momentum[..., 1] = a[2]
    return equilibrium(density, momentum)


def uniform_center_basis(ny: int, nx: int) -> tuple[Array, Array]:
    """Return tangent V and conserved-coordinate extractor L with L @ V = I."""

    ny, nx = _require_grid(ny, nx)
    local_tangent = np.column_stack(
        [
            D2Q9_WEIGHTS,
            3.0 * D2Q9_WEIGHTS * D2Q9_VELOCITIES[:, 0],
            3.0 * D2Q9_WEIGHTS * D2Q9_VELOCITIES[:, 1],
        ]
    )
    tangent = np.tile(local_tangent, (ny * nx, 1))

    site_extractor = np.vstack(
        [
            np.ones(9),
            D2Q9_VELOCITIES[:, 0],
            D2Q9_VELOCITIES[:, 1],
        ]
    )
    extractor = np.tile(site_extractor, (1, ny * nx)) / float(ny * nx)
    return tangent, extractor


def exact_uniform_hessian(ny: int, nx: int) -> Array:
    """Analytic Hessian of the homogeneous equilibrium chart at the rest state."""

    ny, nx = _require_grid(ny, nx)
    local = np.zeros((9, 3, 3), dtype=np.float64)
    cx = D2Q9_VELOCITIES[:, 0]
    cy = D2Q9_VELOCITIES[:, 1]
    local[:, 1, 1] = D2Q9_WEIGHTS * (9.0 * cx * cx - 3.0)
    local[:, 2, 2] = D2Q9_WEIGHTS * (9.0 * cy * cy - 3.0)
    local[:, 1, 2] = 9.0 * D2Q9_WEIGHTS * cx * cy
    local[:, 2, 1] = local[:, 1, 2]
    return np.tile(local, (ny * nx, 1, 1))


def linearized_collision(delta: npt.ArrayLike, omega: float) -> Array:
    """Derivative of BGK collision at the homogeneous rho=1, u=0 state."""

    omega = _require_omega(omega)
    perturbation = _require_state(delta)
    delta_rho, delta_momentum = macroscopic(perturbation)
    equilibrium_tangent = D2Q9_WEIGHTS * (
        delta_rho[..., None]
        + 3.0
        * np.einsum("...d,qd->...q", delta_momentum, D2Q9_VELOCITIES)
    )
    return (1.0 - omega) * perturbation + omega * equilibrium_tangent


def linearized_periodic_step(delta: npt.ArrayLike, omega: float) -> Array:
    """Derivative of the full periodic collide-stream map at rest."""

    return stream_periodic(linearized_collision(delta, omega))


def dense_linearized_map(ny: int, nx: int, omega: float) -> Array:
    """Materialize the dense Jacobian for small-grid verification only."""

    ny, nx = _require_grid(ny, nx)
    omega = _require_omega(omega)
    dimension = ny * nx * 9
    jacobian = np.empty((dimension, dimension), dtype=np.float64)
    for column in range(dimension):
        basis = np.zeros(dimension, dtype=np.float64)
        basis[column] = 1.0
        jacobian[:, column] = linearized_periodic_step(
            basis.reshape(ny, nx, 9), omega
        ).ravel()
    return jacobian


def conserved_moment_matrix() -> Array:
    """Map one site's populations to density and two momentum components."""

    return np.vstack(
        [
            np.ones(9),
            D2Q9_VELOCITIES[:, 0],
            D2Q9_VELOCITIES[:, 1],
        ]
    )


def equilibrium_tangent_matrix() -> Array:
    """Map conserved perturbations to the equilibrium tangent at rest."""

    return np.column_stack(
        [
            D2Q9_WEIGHTS,
            3.0 * D2Q9_WEIGHTS * D2Q9_VELOCITIES[:, 0],
            3.0 * D2Q9_WEIGHTS * D2Q9_VELOCITIES[:, 1],
        ]
    )


def collision_symbol(omega: float) -> Array:
    """Nine-by-nine local Jacobian of BGK collision at rest."""

    omega = _require_omega(omega)
    projector = equilibrium_tangent_matrix() @ conserved_moment_matrix()
    return (1.0 - omega) * np.eye(9) + omega * projector


def fourier_symbol(kx: float, ky: float, omega: float) -> ComplexArray:
    """Fourier block of the linearized collide-stream map."""

    phase = np.exp(
        -1j
        * (
            kx * D2Q9_VELOCITIES[:, 0]
            + ky * D2Q9_VELOCITIES[:, 1]
        )
    )
    return np.diag(phase) @ collision_symbol(omega)


def spectrum_audit(size: int, omega: float, unit_tolerance: float = 1.0e-10) -> dict[str, Any]:
    """Audit unit-modulus and slow eigenvalues on a square periodic grid."""

    if (
        isinstance(size, bool)
        or not isinstance(size, Integral)
        or size <= 1
    ):
        raise ValueError("size must be an integer exceeding one")
    size = int(size)
    omega = _require_omega(omega)
    if (
        not np.isfinite(unit_tolerance)
        or not 0.0 < unit_tolerance < 1.0
    ):
        raise ValueError("unit_tolerance must be finite and in (0, 1)")
    unit_separation = min(omega, 2.0 - omega)
    if unit_separation <= 10.0 * unit_tolerance:
        raise ValueError(
            "unit-circle separation is unresolved at this omega and tolerance"
        )
    records: list[tuple[int, int, complex]] = []
    all_values: list[complex] = []
    for ix in range(size):
        kx = 2.0 * np.pi * ix / size
        for iy in range(size):
            ky = 2.0 * np.pi * iy / size
            eigenvalues = np.linalg.eigvals(fourier_symbol(kx, ky, omega))
            all_values.extend(eigenvalues)
            records.extend(
                (ix, iy, complex(value))
                for value in eigenvalues
                if abs(abs(value) - 1.0) < unit_tolerance
            )

    values = np.asarray(all_values, dtype=np.complex128)
    expected_strict_unit_count = 5 if size % 2 == 0 else 3
    if len(records) != expected_strict_unit_count:
        raise ValueError(
            "unit-circle classification is unresolved for this grid, omega, "
            "and tolerance; use physical branch tracking or revise the tolerance"
        )
    nonunit = values[np.abs(np.abs(values) - 1.0) >= unit_tolerance]
    wavevectors = sorted({(ix, iy) for ix, iy, _ in records})
    return {
        "grid": [size, size],
        "state_dimension": int(size * size * 9),
        "strict_unit_count": len(records),
        "expected_strict_unit_count": expected_strict_unit_count,
        "strict_unit_wavevectors": [[ix, iy] for ix, iy in wavevectors],
        "zero_wave_unit_count": sum(ix == 0 and iy == 0 for ix, iy, _ in records),
        "nonzero_wave_unit_count": sum(not (ix == 0 and iy == 0) for ix, iy, _ in records),
        "slow_count_modulus_gt_0_9": int(np.count_nonzero(np.abs(values) > 0.9)),
        "largest_nonunit_modulus": (
            float(np.max(np.abs(nonunit))) if nonunit.size else None
        ),
        "unit_eigenvalues": [
            {
                "wave_index": [ix, iy],
                "real": float(value.real),
                "imag": float(value.imag),
            }
            for ix, iy, value in records
        ],
    }
