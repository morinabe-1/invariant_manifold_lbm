"""Small, dependency-free TT-SVD oracle for parameterization coefficients."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import pairwise
from numbers import Integral

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]
NumericArray = npt.NDArray[np.float64] | npt.NDArray[np.complex128]


def _stable_frobenius_norm(array: npt.ArrayLike) -> float:
    raw = np.asarray(array)
    dtype = np.complex128 if np.iscomplexobj(raw) else np.float64
    values = np.asarray(raw, dtype=dtype)
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


def _tt_svd_impl(
    tensor: npt.ArrayLike,
    relative_tolerance: float = 0.0,
    max_rank: int | None = None,
) -> tuple[list[NumericArray], dict[str, object]]:
    raw = np.asarray(tensor)
    dtype = np.complex128 if np.iscomplexobj(raw) else np.float64
    dense = np.asarray(raw, dtype=dtype)
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
    diagnostics: dict[str, object] = {
        "input_dtype": str(dense.dtype),
        "mode_shape": list(dense.shape),
        "tensor_frobenius_norm": norm,
        "requested_relative_tolerance": float(relative_tolerance),
        "maximum_rank": max_rank,
        "split_records": [],
        "all_singular_values_finite": True,
    }
    if norm == 0.0:
        cores = [
            np.ones((1, mode_size, 1), dtype=dense.dtype)
            for mode_size in dense.shape
        ]
        cores[0].fill(0.0)
        diagnostics.update(
            {
                "discarded_frobenius_norm": 0.0,
                "relative_discarded_frobenius_norm": 0.0,
                "tt_ranks": tt_ranks(cores),
            }
        )
        return cores, diagnostics
    if dense.ndim == 1:
        cores = [dense.reshape(1, dense.shape[0], 1)]
        diagnostics.update(
            {
                "discarded_frobenius_norm": 0.0,
                "relative_discarded_frobenius_norm": 0.0,
                "tt_ranks": tt_ranks(cores),
            }
        )
        return cores, diagnostics

    local_threshold = relative_tolerance * norm / np.sqrt(dense.ndim - 1)
    cores: list[NumericArray] = []
    unfolding = dense
    left_rank = 1
    discarded_norm = 0.0
    split_records = []
    for mode_index, mode_size in enumerate(dense.shape[:-1]):
        matrix = unfolding.reshape(left_rank * mode_size, -1)
        u, singular_values, vh = np.linalg.svd(matrix, full_matrices=False)
        singular_values_finite = bool(np.all(np.isfinite(singular_values)))
        if not singular_values_finite:
            raise ValueError("TT-SVD produced non-finite singular values")
        rank = _truncation_rank(singular_values, local_threshold, max_rank)
        local_discarded_norm = _stable_frobenius_norm(singular_values[rank:])
        discarded_norm = float(np.hypot(discarded_norm, local_discarded_norm))
        split_records.append(
            {
                "mode_index": mode_index,
                "matrix_shape": list(matrix.shape),
                "singular_value_count": int(singular_values.size),
                "maximum_singular_value": float(singular_values[0]),
                "minimum_singular_value": float(singular_values[-1]),
                "retained_rank": rank,
                "discarded_frobenius_norm": local_discarded_norm,
                "all_singular_values_finite": singular_values_finite,
            }
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
    diagnostics.update(
        {
            "split_records": split_records,
            "discarded_frobenius_norm": discarded_norm,
            "relative_discarded_frobenius_norm": discarded_norm / norm,
            "tt_ranks": tt_ranks(cores),
        }
    )
    return cores, diagnostics


def tt_svd(
    tensor: npt.ArrayLike,
    relative_tolerance: float = 0.0,
    max_rank: int | None = None,
) -> list[NumericArray]:
    """Decompose a real or complex tensor with a discarded-value budget.

    The tolerance controls the accumulated Frobenius norm of singular values
    discarded by the sequential SVDs.  It is not an end-to-end floating-point
    reconstruction guarantee; callers that need one must reconstruct or use an
    independent held-out validation gate.
    """

    cores, _ = _tt_svd_impl(tensor, relative_tolerance, max_rank)
    return cores


def tt_svd_with_diagnostics(
    tensor: npt.ArrayLike,
    relative_tolerance: float = 0.0,
    max_rank: int | None = None,
) -> tuple[list[NumericArray], dict[str, object]]:
    """Return TT-SVD cores together with split-level numerical diagnostics."""

    return _tt_svd_impl(tensor, relative_tolerance, max_rank)


def reconstruct(cores: Sequence[npt.ArrayLike]) -> NumericArray:
    """Reconstruct a dense tensor from TT cores."""

    if not cores:
        raise ValueError("at least one TT core is required")
    dtype = np.complex128 if any(np.iscomplexobj(core) for core in cores) else np.float64
    converted = [np.asarray(core, dtype=dtype) for core in cores]
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


def contract_tt(
    cores: Sequence[npt.ArrayLike],
    mode_vectors: Sequence[npt.ArrayLike | None],
) -> NumericArray:
    """Contract selected TT modes and retain modes whose vector is ``None``."""

    if not cores:
        raise ValueError("at least one TT core is required")
    if len(cores) != len(mode_vectors):
        raise ValueError("expected one mode vector or None per TT core")
    values = [value for value in (*cores, *mode_vectors) if value is not None]
    dtype = np.complex128 if any(np.iscomplexobj(value) for value in values) else np.float64
    converted = [np.asarray(core, dtype=dtype) for core in cores]
    if any(core.ndim != 3 for core in converted):
        raise ValueError("each TT core must have shape (left_rank, mode, right_rank)")
    if converted[0].shape[0] != 1 or converted[-1].shape[2] != 1:
        raise ValueError("boundary TT ranks must equal one")
    for left, right in pairwise(converted):
        if left.shape[2] != right.shape[0]:
            raise ValueError("adjacent TT ranks do not match")

    result = np.ones(1, dtype=dtype)
    for core, vector in zip(converted, mode_vectors, strict=True):
        if vector is None:
            result = np.tensordot(result, core, axes=([-1], [0]))
            continue
        feature = np.asarray(vector, dtype=dtype)
        if feature.shape != (core.shape[1],):
            raise ValueError("mode vector length does not match its TT core")
        transfer = np.einsum("lnr,n->lr", core, feature)
        result = np.tensordot(result, transfer, axes=([-1], [0]))
    if result.shape[-1] != 1:
        raise ValueError("final TT rank must equal one")
    return np.asarray(result[..., 0], dtype=dtype)


def tt_ranks(cores: Sequence[npt.ArrayLike]) -> list[int]:
    """Return the TT bond ranks including both unit boundary ranks."""

    converted = [np.asarray(core) for core in cores]
    if not converted:
        raise ValueError("at least one core is required")
    return [int(converted[0].shape[0])] + [int(core.shape[2]) for core in converted]
