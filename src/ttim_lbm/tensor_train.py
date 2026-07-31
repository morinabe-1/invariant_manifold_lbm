"""Small, dependency-free TT-SVD oracle for parameterization coefficients."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import pairwise
from numbers import Integral

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]


def _stable_frobenius_norm(array: npt.ArrayLike) -> float:
    values = np.asarray(array, dtype=np.float64)
    scale = float(np.max(np.abs(values), initial=0.0))
    if scale == 0.0:
        return 0.0
    normalized_norm = float(np.linalg.norm(values / scale))
    if scale > np.finfo(np.float64).max / normalized_norm:
        return float("inf")
    return float(scale * normalized_norm)


def _truncation_rank(singular_values: Array, threshold: float, max_rank: int | None) -> int:
    rank = singular_values.size
    if threshold > 0.0:
        for candidate in range(1, singular_values.size + 1):
            if _stable_frobenius_norm(singular_values[candidate:]) <= threshold:
                rank = candidate
                break
    if max_rank is not None:
        rank = min(rank, max_rank)
    return max(1, rank)


def tt_svd(
    tensor: npt.ArrayLike,
    relative_tolerance: float = 0.0,
    max_rank: int | None = None,
) -> list[Array]:
    """Decompose a dense tensor with a relative discarded-singular-value budget.

    The tolerance controls the accumulated Frobenius norm of singular values
    discarded by the sequential SVDs.  It is not an end-to-end floating-point
    reconstruction guarantee; callers that need one must reconstruct or use an
    independent held-out validation gate.
    """

    dense = np.asarray(tensor, dtype=np.float64)
    if dense.ndim == 0:
        raise ValueError("tensor must have at least one mode")
    if not np.all(np.isfinite(dense)):
        raise ValueError("tensor entries must be finite")
    if not np.isfinite(relative_tolerance) or relative_tolerance < 0.0:
        raise ValueError("relative_tolerance must be finite and nonnegative")
    tolerance_floor = 10.0 * np.finfo(np.float64).eps
    if 0.0 < relative_tolerance < tolerance_floor:
        raise ValueError(
            "relative_tolerance is too close to float64 roundoff for this implementation"
        )
    if max_rank is not None:
        if isinstance(max_rank, bool) or not isinstance(max_rank, Integral) or max_rank <= 0:
            raise ValueError("max_rank must be a positive integer")
        max_rank = int(max_rank)
    norm = _stable_frobenius_norm(dense)
    if not np.isfinite(norm):
        raise ValueError(
            "tensor Frobenius norm is not representable in float64; rescale it"
        )
    if norm == 0.0:
        cores = [
            np.ones((1, mode_size, 1), dtype=np.float64)
            for mode_size in dense.shape
        ]
        cores[0].fill(0.0)
        return cores
    if dense.ndim == 1:
        return [dense.reshape(1, dense.shape[0], 1)]

    local_threshold = relative_tolerance * norm / np.sqrt(dense.ndim - 1)
    cores: list[Array] = []
    unfolding = dense
    left_rank = 1
    discarded_norm = 0.0
    for mode_size in dense.shape[:-1]:
        matrix = unfolding.reshape(left_rank * mode_size, -1)
        u, singular_values, vh = np.linalg.svd(matrix, full_matrices=False)
        rank = _truncation_rank(singular_values, local_threshold, max_rank)
        discarded_norm = float(
            np.hypot(
                discarded_norm,
                _stable_frobenius_norm(singular_values[rank:]),
            )
        )
        cores.append(u[:, :rank].reshape(left_rank, mode_size, rank))
        unfolding = singular_values[:rank, None] * vh[:rank, :]
        left_rank = rank
    cores.append(unfolding.reshape(left_rank, dense.shape[-1], 1))
    if (
        relative_tolerance > 0.0
        and discarded_norm > relative_tolerance * norm * (1.0 + 1.0e-12)
    ):
        raise ValueError(
            "max_rank prevents TT-SVD from meeting relative_tolerance; "
            "increase max_rank or set relative_tolerance=0 for best-effort truncation"
        )
    return cores


def reconstruct(cores: Sequence[npt.ArrayLike]) -> Array:
    """Reconstruct a dense tensor from TT cores."""

    if not cores:
        raise ValueError("at least one TT core is required")
    converted = [np.asarray(core, dtype=np.float64) for core in cores]
    if any(core.ndim != 3 for core in converted):
        raise ValueError("each TT core must have shape (left_rank, mode, right_rank)")
    if converted[0].shape[0] != 1 or converted[-1].shape[2] != 1:
        raise ValueError("boundary TT ranks must equal one")
    for left, right in pairwise(converted):
        if left.shape[2] != right.shape[0]:
            raise ValueError("adjacent TT ranks do not match")

    contracted = converted[0][0, :, :]
    mode_shape = [converted[0].shape[1]]
    for core in converted[1:]:
        contracted = np.tensordot(contracted, core, axes=([-1], [0]))
        mode_shape.append(core.shape[1])
    return contracted.reshape(mode_shape)


def polynomial_coefficient_tensor(
    base: npt.ArrayLike,
    tangent: npt.ArrayLike,
    hessian: npt.ArrayLike,
) -> Array:
    """Build C[:, alpha_1, ..., alpha_m] for a quadratic multivariate chart."""

    fixed = np.asarray(base, dtype=np.float64)
    basis = np.asarray(tangent, dtype=np.float64)
    curvature = np.asarray(hessian, dtype=np.float64)
    if fixed.ndim != 1 or basis.ndim != 2:
        raise ValueError("base and tangent ranks must be one and two")
    output, reduced = basis.shape
    if fixed.size != output or curvature.shape != (output, reduced, reduced):
        raise ValueError("coefficient shapes are inconsistent")

    coefficients = np.zeros((output,) + (3,) * reduced, dtype=np.float64)
    zero = (slice(None),) + (0,) * reduced
    coefficients[zero] = fixed
    for j in range(reduced):
        index = [0] * reduced
        index[j] = 1
        coefficients[(slice(None), *index)] += basis[:, j]
    for j in range(reduced):
        for k in range(reduced):
            index = [0] * reduced
            index[j] += 1
            index[k] += 1
            coefficients[(slice(None), *index)] += 0.5 * curvature[:, j, k]
    return coefficients


def evaluate_polynomial(cores: Sequence[npt.ArrayLike], coordinates: npt.ArrayLike) -> Array:
    """Evaluate a block-output polynomial TT using [1, a_j, a_j²] features."""

    a = np.asarray(coordinates, dtype=np.float64)
    converted = [np.asarray(core, dtype=np.float64) for core in cores]
    if len(converted) != a.size + 1:
        raise ValueError("expected one output core followed by one core per coordinate")
    output_core = converted[0]
    if output_core.shape[0] != 1:
        raise ValueError("output core must have unit left rank")
    value = output_core[0, :, :]
    for coordinate, core in zip(a, converted[1:], strict=True):
        if core.shape[1] != 3:
            raise ValueError("polynomial coordinate modes must have size three")
        feature = np.array([1.0, coordinate, coordinate * coordinate])
        transfer = np.einsum("lnr,n->lr", core, feature)
        value = value @ transfer
    if value.shape[1] != 1:
        raise ValueError("final TT rank must equal one")
    return value[:, 0]


def tt_ranks(cores: Sequence[npt.ArrayLike]) -> list[int]:
    """Return the TT bond ranks including both unit boundary ranks."""

    converted = [np.asarray(core) for core in cores]
    if not converted:
        raise ValueError("at least one core is required")
    return [int(converted[0].shape[0])] + [int(core.shape[2]) for core in converted]
