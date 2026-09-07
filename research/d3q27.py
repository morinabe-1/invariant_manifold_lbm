"""Experimental D3Q27 BGK oracle; axes are z,y,x and velocities are x,y,z.

The frozen D2Q9 package remains the comparison oracle. This module has its own
source seal in Q012a; no spectral-manifold existence claim is attached to it.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations, product
from math import prod
from numbers import Integral

import numpy as np
import numpy.typing as npt

from ttim_lbm.d2q9 import D2Q9_VELOCITIES

D1Q3_VELOCITIES = (-1, 0, 1)
D1Q3_WEIGHTS = (Fraction(1, 6), Fraction(2, 3), Fraction(1, 6))
VELOCITIES = np.array(list(product(D1Q3_VELOCITIES, repeat=3)), dtype=np.int64)
EXACT_WEIGHTS = tuple(prod(D1Q3_WEIGHTS[c + 1] for c in v) for v in VELOCITIES)
WEIGHTS = np.array([float(w) for w in EXACT_WEIGHTS], dtype=np.float64)
CS2 = 1.0 / 3.0
VELOCITIES.setflags(write=False)
WEIGHTS.setflags(write=False)


def _real_array(value: npt.ArrayLike) -> np.ndarray:
    raw = np.asarray(value)
    if np.iscomplexobj(raw):
        raise ValueError("real populations or conserved coordinates are required")
    array = np.asarray(raw, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError("all entries must be finite")
    return array


def _state(value: npt.ArrayLike, *, allow_complex: bool = False) -> np.ndarray:
    if allow_complex and np.iscomplexobj(value):
        array = np.asarray(value, dtype=np.complex128)
        if not np.all(np.isfinite(array)):
            raise ValueError("all entries must be finite")
    else:
        array = _real_array(value)
    if array.ndim != 4 or array.shape[-1] != 27 or min(array.shape[:3]) <= 0:
        raise ValueError("D3Q27 state must have shape (nz, ny, nx, 27) with nonempty axes")
    return array


def _omega(value: float) -> float:
    omega = float(value)
    if not np.isfinite(omega) or not 0.0 < omega < 2.0:
        raise ValueError("omega must lie in (0, 2)")
    return omega


def _grid(shape: tuple[int, int, int]) -> tuple[int, int, int]:
    if len(shape) != 3 or any(
        isinstance(n, bool) or not isinstance(n, Integral) or n <= 0 for n in shape
    ):
        raise ValueError("grid must be three positive integer sizes (nz, ny, nx)")
    return tuple(int(n) for n in shape)


def macroscopic(state: npt.ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    f = _state(state)
    return f.sum(axis=-1), np.einsum("...q,qd->...d", f, VELOCITIES)


def conserved_moment_matrix() -> np.ndarray:
    return np.vstack((np.ones(27), VELOCITIES.T))


def equilibrium_tangent_matrix() -> np.ndarray:
    return np.column_stack((WEIGHTS, 3.0 * WEIGHTS[:, None] * VELOCITIES))


def equilibrium(density: npt.ArrayLike, momentum: npt.ArrayLike) -> np.ndarray:
    rho, j = _real_array(density), _real_array(momentum)
    if j.shape != rho.shape + (3,):
        raise ValueError("momentum must have shape density.shape + (3,)")
    if np.any(rho <= 0.0):
        raise ValueError("density must be strictly positive")
    cj = np.einsum("...d,qd->...q", j, VELOCITIES)
    jj = np.sum(j * j, axis=-1)
    return WEIGHTS * (
        rho[..., None] + 3.0 * cj + (4.5 * cj * cj - 1.5 * jj[..., None]) / rho[..., None]
    )


def equilibrium_hessian_at_rest() -> np.ndarray:
    """D² f_eq with respect to (delta rho, jx, jy, jz), at (1,0,0,0)."""
    hessian = np.zeros((27, 4, 4))
    hessian[:, 1:, 1:] = WEIGHTS[:, None, None] * (
        9.0 * np.einsum("qi,qj->qij", VELOCITIES, VELOCITIES) - 3.0 * np.eye(3)
    )
    return hessian


def uniform_equilibrium(shape: tuple[int, int, int], coordinates: npt.ArrayLike) -> np.ndarray:
    shape = _grid(shape)
    a = _real_array(coordinates)
    if a.shape != (4,):
        raise ValueError("coordinates must be (delta rho, jx, jy, jz)")
    local = equilibrium(1.0 + a[0], a[1:])
    return np.broadcast_to(local, shape + (27,)).copy()


def uniform_center_basis(shape: tuple[int, int, int]) -> tuple[np.ndarray, np.ndarray]:
    sites = prod(_grid(shape))
    return (
        np.tile(equilibrium_tangent_matrix(), (sites, 1)),
        np.tile(conserved_moment_matrix(), (1, sites)) / sites,
    )


def global_conserved_quantities(state: npt.ArrayLike) -> np.ndarray:
    f = _state(state)
    return conserved_moment_matrix() @ f.sum(axis=(0, 1, 2))


def project_to_fixed_leaf(perturbation: npt.ArrayLike) -> np.ndarray:
    """Remove four uniform conserved components; this is a floating projection."""
    delta = _state(perturbation)
    mean = global_conserved_quantities(delta) / prod(delta.shape[:3])
    return delta - equilibrium_tangent_matrix() @ mean


def collide_bgk(state: npt.ArrayLike, omega: float) -> np.ndarray:
    rate, f = _omega(omega), _state(state)
    rho, j = macroscopic(f)
    return f + rate * (equilibrium(rho, j) - f)


def stream_periodic(state: npt.ArrayLike) -> np.ndarray:
    f = _state(state, allow_complex=True)
    result = np.empty_like(f)
    for q, (cx, cy, cz) in enumerate(VELOCITIES):
        result[..., q] = np.roll(f[..., q], shift=(cz, cy, cx), axis=(0, 1, 2))
    return result


def bgk_periodic_step(state: npt.ArrayLike, omega: float) -> np.ndarray:
    return stream_periodic(collide_bgk(state, omega))


def collision_symbol(omega: float) -> np.ndarray:
    rate = _omega(omega)
    return (1.0 - rate) * np.eye(27) + rate * (
        equilibrium_tangent_matrix() @ conserved_moment_matrix()
    )


def fourier_symbol(wavevector: npt.ArrayLike, omega: float) -> np.ndarray:
    k = _real_array(wavevector)
    if k.shape != (3,):
        raise ValueError("wavevector must be (kx, ky, kz)")
    return np.exp(-1j * (VELOCITIES @ k))[:, None] * collision_symbol(omega)


def linearized_periodic_step(delta: npt.ArrayLike, omega: float) -> np.ndarray:
    f = _state(delta, allow_complex=True)
    return stream_periodic(np.einsum("qr,...r->...q", collision_symbol(omega), f))


def d2q9_lift_matrix() -> np.ndarray:
    """J: R^9 -> R^27 using the existing D2Q9 population order and z weights."""
    lookup = {tuple(v.astype(int)): q for q, v in enumerate(D2Q9_VELOCITIES)}
    lift = np.zeros((27, 9))
    for row, (cx, cy, cz) in enumerate(VELOCITIES):
        lift[row, lookup[(cx, cy)]] = float(D1Q3_WEIGHTS[cz + 1])
    return lift


def lift_d2q9(state: npt.ArrayLike, nz: int) -> np.ndarray:
    f = _real_array(state)
    if f.ndim != 3 or f.shape[-1] != 9 or min(f.shape[:2]) <= 0:
        raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
    shape = _grid((nz, f.shape[0], f.shape[1]))
    layer = np.einsum("qr,...r->...q", d2q9_lift_matrix(), f)
    return np.broadcast_to(layer, shape + (27,)).copy()


def d2q9_marginal(state: npt.ArrayLike) -> np.ndarray:
    """Sum over cz at every z plane; no z averaging or layer discarding."""
    f = _state(state)
    lookup = {tuple(v.astype(int)): q for q, v in enumerate(D2Q9_VELOCITIES)}
    result = np.zeros(f.shape[:3] + (9,))
    for q, (cx, cy, _cz) in enumerate(VELOCITIES):
        result[..., lookup[(cx, cy)]] += f[..., q]
    return result


def cubic_symmetries() -> tuple[np.ndarray, ...]:
    """All 48 signed permutation matrices, including 24 proper rotations."""
    matrices = []
    for axes in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            matrix = np.zeros((3, 3), dtype=np.int64)
            matrix[np.arange(3), axes] = signs
            matrices.append(matrix)
    return tuple(matrices)


def population_permutation(rotation: npt.ArrayLike) -> np.ndarray:
    matrix = _real_array(rotation)
    if (
        matrix.shape != (3, 3)
        or not np.all(np.isin(matrix, (-1, 0, 1)))
        or not np.array_equal(matrix @ matrix.T, np.eye(3))
    ):
        raise ValueError("rotation must be a signed axis permutation")
    lookup = {tuple(v): q for q, v in enumerate(VELOCITIES)}
    targets = [lookup[tuple(v)] for v in VELOCITIES @ matrix.T]
    result = np.zeros((27, 27))
    result[targets, np.arange(27)] = 1.0
    return result


def rotate_periodic_state(state: npt.ArrayLike, rotation: npt.ArrayLike) -> np.ndarray:
    f = _state(state)
    if len(set(f.shape[:3])) != 1:
        raise ValueError("full cubic rotations require equal spatial extents")
    matrix = _real_array(rotation)
    targets = np.argmax(population_permutation(matrix), axis=0)
    z, y, x = np.indices(f.shape[:3])
    moved = np.einsum("ij,j...->i...", matrix, np.stack((x, y, z))).astype(int)
    moved %= f.shape[0]
    result = np.empty_like(f)
    for q, target in enumerate(targets):
        result[moved[2], moved[1], moved[0], target] = f[..., q]
    return result
