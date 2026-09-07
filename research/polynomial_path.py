"""Ascending-power path algebra; coefficients already include Taylor factorials.

These operations do not fit sampled values, realify complex data, truncate small
coefficients, or mutate a chart. Trailing axes are pointwise output dimensions.
"""

from __future__ import annotations

from numbers import Integral

import numpy as np


def _numeric(value: np.ndarray) -> np.ndarray:
    array = np.asarray(value)
    if array.dtype.kind not in "iufc" or not np.all(np.isfinite(array)):
        raise ValueError("finite numeric values are required")
    with np.errstate(over="raise", invalid="raise"):
        result = np.array(array, dtype=np.complex128 if np.iscomplexobj(array) else np.float64)
    return _finite(result)


def _finite(value: np.ndarray) -> np.ndarray:
    if not np.all(np.isfinite(value)):
        raise ValueError("nonfinite polynomial result")
    return value


def _series(value: np.ndarray) -> np.ndarray:
    array = _numeric(value)
    if array.ndim == 0 or array.shape[0] == 0:
        raise ValueError("a nonempty leading coefficient axis is required")
    return array


def _order(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
        raise ValueError("order must be a nonnegative integer")
    return int(value)


def _broadcast(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left, right = _series(left), _series(right)
    shape = np.broadcast_shapes(left.shape[1:], right.shape[1:])

    def expand(value):
        leading = (1,) * (len(shape) - value.ndim + 1)
        return np.broadcast_to(
            value.reshape((len(value),) + leading + value.shape[1:]), (len(value),) + shape
        )

    return expand(left), expand(right)


def add(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left, right = _broadcast(left, right)
    result = np.zeros(
        (max(len(left), len(right)),) + left.shape[1:], dtype=np.result_type(left, right)
    )
    with np.errstate(over="raise", invalid="raise"):
        result[: len(left)] += left
        result[: len(right)] += right
    return _finite(result)


def evaluate(coefficients: np.ndarray, parameter: complex) -> np.ndarray:
    coefficients, parameter = _series(coefficients), _numeric(parameter)
    if parameter.ndim != 0:
        raise ValueError("the path parameter must be scalar")
    result = np.zeros(coefficients.shape[1:], dtype=np.result_type(coefficients, parameter))
    with np.errstate(over="raise", invalid="raise"):
        for coefficient in coefficients[::-1]:
            result = result * parameter + coefficient
    return _finite(result)


def convolve(left: np.ndarray, right: np.ndarray, *, order: int | None = None) -> np.ndarray:
    left, right = _broadcast(left, right)
    degree = len(left) + len(right) - 2 if order is None else _order(order)
    result = np.zeros((degree + 1,) + left.shape[1:], dtype=np.result_type(left, right))
    with np.errstate(over="raise", invalid="raise"):
        for i in range(min(len(left), degree + 1)):
            for j in range(min(len(right), degree + 1 - i)):
                result[i + j] += left[i] * right[j]
    return _finite(result)


def quotient(numerator: np.ndarray, denominator: np.ndarray, *, order: int) -> np.ndarray:
    """Formal division with arbitrary nonzero constant denominator, pointwise."""
    numerator, denominator = _broadcast(numerator, denominator)
    degree = _order(order)
    if np.any(denominator[0] == 0):
        raise ValueError("a zero constant denominator has no ordinary Taylor quotient")
    result = np.zeros(
        (degree + 1,) + numerator.shape[1:], dtype=np.result_type(numerator, denominator)
    )
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        for n in range(degree + 1):
            rhs = numerator[n].copy() if n < len(numerator) else np.zeros_like(result[n])
            for j in range(1, min(n + 1, len(denominator))):
                rhs = rhs - denominator[j] * result[n - j]
            result[n] = rhs / denominator[0]
    return _finite(result)


def remainder_numerator(
    numerator: np.ndarray, denominator: np.ndarray, approximation: np.ndarray
) -> np.ndarray:
    """Q - rho P in full, including nonzero low-degree floating-point residues."""
    return add(numerator, -convolve(denominator, approximation))


def homogeneous_composition(
    indices: np.ndarray,
    groups: np.ndarray,
    coefficients: np.ndarray,
    coordinate_path: np.ndarray,
    *,
    group_count: int,
) -> np.ndarray:
    """Substitute a polynomial path into grouped homogeneous sparse monomials.

    Return shape (path_degree * monomial_degree + 1, group_count, width).
    Empty support and absent groups retain explicit zeros. Repeated indices and
    duplicate rows are legitimate terms, not grounds to rescale or deduplicate.
    """
    path = _series(coordinate_path)
    indices, groups = np.asarray(indices), np.asarray(groups)
    coefficients = _numeric(coefficients)
    if path.ndim != 2 or path.shape[1] < 1:
        raise ValueError("coordinate path must have shape (degree + 1, dimension)")
    if isinstance(group_count, bool) or not isinstance(group_count, Integral) or group_count < 1:
        raise ValueError("group_count must be a positive integer")
    if (
        indices.ndim != 2
        or indices.shape[1] < 1
        or indices.dtype.kind not in "iu"
        or np.any(indices < 0)
        or np.any(indices >= path.shape[1])
    ):
        raise ValueError("monomial indices must be an in-range integer matrix")
    if (
        groups.shape != (len(indices),)
        or groups.dtype.kind not in "iu"
        or np.any(groups < 0)
        or np.any(groups >= group_count)
    ):
        raise ValueError("groups must be an in-range integer vector")
    if coefficients.ndim != 2 or coefficients.shape[0] != len(indices) or coefficients.shape[1] < 1:
        raise ValueError("coefficient rows must match monomials and have positive width")
    degree = (len(path) - 1) * indices.shape[1]
    result = np.zeros(
        (degree + 1, group_count, coefficients.shape[1]), dtype=np.result_type(path, coefficients)
    )
    if not len(indices):
        return result
    weights = np.ones((1, len(indices)), dtype=path.dtype)
    for slot in range(indices.shape[1]):
        weights = convolve(weights, path[:, indices[:, slot]])
    permutation = np.argsort(groups, kind="stable")
    sorted_groups = groups[permutation]
    starts = np.r_[0, np.flatnonzero(np.diff(sorted_groups)) + 1]
    outputs = sorted_groups[starts]
    sorted_coefficients = coefficients[permutation]
    with np.errstate(over="raise", invalid="raise"):
        for n in range(degree + 1):
            result[n, outputs] = np.add.reduceat(
                sorted_coefficients * weights[n, permutation, None], starts, axis=0
            )
    return _finite(result)
