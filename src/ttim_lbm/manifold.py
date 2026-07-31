"""Low-order parameterization-method primitives for discrete maps."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]
FlatMap = Callable[[Array], Array]


@dataclass(frozen=True)
class QuadraticChart:
    """Chart W(a) = base + V a + 1/2 H[a,a]."""

    base: Array
    tangent: Array
    hessian: Array

    def __post_init__(self) -> None:
        base = np.asarray(self.base, dtype=np.float64)
        tangent = np.asarray(self.tangent, dtype=np.float64)
        hessian = np.asarray(self.hessian, dtype=np.float64)
        if base.ndim != 1 or tangent.ndim != 2 or hessian.ndim != 3:
            raise ValueError("base, tangent, hessian must have ranks 1, 2, 3")
        if tangent.shape[0] != base.size:
            raise ValueError("tangent output dimension must match base")
        if hessian.shape != (base.size, tangent.shape[1], tangent.shape[1]):
            raise ValueError("hessian shape must be (output, reduced, reduced)")
        object.__setattr__(self, "base", base)
        object.__setattr__(self, "tangent", tangent)
        object.__setattr__(self, "hessian", hessian)

    @property
    def reduced_dimension(self) -> int:
        return int(self.tangent.shape[1])

    def evaluate(self, coordinates: npt.ArrayLike) -> Array:
        a = np.asarray(coordinates, dtype=np.float64)
        if a.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match chart")
        quadratic = 0.5 * np.einsum("ijk,j,k->i", self.hessian, a, a)
        return self.base + self.tangent @ a + quadratic


@dataclass(frozen=True)
class HomologicalDiagnostics:
    """Solvability and post-symmetrization checks for a quadratic solve."""

    augmented_rank: int
    augmented_dimension: int
    smallest_singular_value: float
    condition_number: float
    tangent_relative_residual: float
    left_invariance_relative_residual: float
    raw_symmetry_relative_residual: float
    global_equation_relative_residual: float
    maximum_equation_residual: float
    maximum_gauge_residual: float


def invariance_defect(full_map: FlatMap, chart: QuadraticChart, coordinates: npt.ArrayLike) -> Array:
    """Return E(a) = Phi(W(a)) - W(a) for an identity reduced map."""

    lifted = chart.evaluate(coordinates)
    return np.asarray(full_map(lifted), dtype=np.float64) - lifted


def invariance_residual(
    full_map: FlatMap,
    chart: QuadraticChart,
    coordinates: npt.ArrayLike,
) -> float:
    """Euclidean norm of the identity-center invariance defect."""

    return float(np.linalg.norm(invariance_defect(full_map, chart, coordinates)))


def second_derivative_tensor(
    full_map: FlatMap,
    base: npt.ArrayLike,
    tangent: npt.ArrayLike,
    step: float | npt.ArrayLike = 2.0e-4,
) -> Array:
    """Centered finite-difference approximation to D²Phi(base)[V., V.]."""

    fixed = np.asarray(base, dtype=np.float64)
    basis = np.asarray(tangent, dtype=np.float64)
    if fixed.ndim != 1 or basis.ndim != 2 or basis.shape[0] != fixed.size:
        raise ValueError("base and tangent shapes are inconsistent")

    reduced = basis.shape[1]
    steps = np.asarray(step, dtype=np.float64)
    if steps.ndim == 0:
        steps = np.full(reduced, float(steps), dtype=np.float64)
    if steps.shape != (reduced,) or not np.all(np.isfinite(steps)) or np.any(steps <= 0.0):
        raise ValueError(
            "finite-difference step must be positive and scalar or one per coordinate"
        )
    result = np.empty((fixed.size, reduced, reduced), dtype=np.float64)
    mapped_fixed = full_map(fixed)
    for j in range(reduced):
        for k in range(j, reduced):
            v = steps[j] * basis[:, j]
            if j == k:
                mixed = (
                    full_map(fixed + v)
                    - 2.0 * mapped_fixed
                    + full_map(fixed - v)
                ) / (steps[j] * steps[j])
            else:
                w = steps[k] * basis[:, k]
                mixed = (
                    full_map(fixed + v + w)
                    - full_map(fixed + v - w)
                    - full_map(fixed - v + w)
                    + full_map(fixed - v - w)
                ) / (4.0 * steps[j] * steps[k])
            result[:, j, k] = mixed
            result[:, k, j] = mixed
    return result


def solve_identity_center_quadratic(
    jacobian: npt.ArrayLike,
    tangent: npt.ArrayLike,
    extractor: npt.ArrayLike,
    second_derivative: npt.ArrayLike,
) -> tuple[Array, Array, HomologicalDiagnostics]:
    """Solve the quadratic homological equation for Lambda = identity.

    The gauge is L H = 0. The returned reduced Hessian G is retained rather
    than assumed zero, so the routine also exposes resonant center dynamics.
    """

    linear = np.asarray(jacobian, dtype=np.float64)
    basis = np.asarray(tangent, dtype=np.float64)
    left = np.asarray(extractor, dtype=np.float64)
    bilinear = np.asarray(second_derivative, dtype=np.float64)
    output, reduced = basis.shape
    if linear.shape != (output, output):
        raise ValueError("jacobian shape is inconsistent with tangent")
    if left.shape != (reduced, output) or bilinear.shape != (
        output,
        reduced,
        reduced,
    ):
        raise ValueError("extractor or second derivative shape is inconsistent")
    if not np.allclose(
        left @ basis,
        np.eye(reduced),
        atol=1.0e-11,
        rtol=0.0,
    ):
        raise ValueError("extractor and tangent must satisfy L @ V = I")

    augmented = np.block(
        [
            [linear - np.eye(output), -basis],
            [left, np.zeros((reduced, reduced))],
        ]
    )
    singular_values = np.linalg.svd(augmented, compute_uv=False)
    augmented_rank = int(np.linalg.matrix_rank(augmented))
    augmented_dimension = int(augmented.shape[1])
    if augmented_rank < augmented_dimension:
        raise np.linalg.LinAlgError(
            "quadratic homological system is rank deficient; "
            "the selected center complement is unresolved"
        )
    smallest_singular_value = float(singular_values[-1])
    condition_number = float(singular_values[0] / singular_values[-1])
    hessian = np.empty_like(bilinear)
    reduced_hessian = np.empty((reduced, reduced, reduced), dtype=np.float64)
    for j in range(reduced):
        for k in range(reduced):
            rhs = np.concatenate([-bilinear[:, j, k], np.zeros(reduced)])
            solution, *_ = np.linalg.lstsq(augmented, rhs, rcond=None)
            hessian[:, j, k] = solution[:output]
            reduced_hessian[:, j, k] = solution[output:]

    raw_symmetry_denominator = max(
        float(np.linalg.norm(hessian)),
        float(np.linalg.norm(reduced_hessian)),
        np.finfo(float).eps,
    )
    raw_symmetry_residual = max(
        float(np.linalg.norm(hessian - hessian.swapaxes(1, 2))),
        float(
            np.linalg.norm(
                reduced_hessian - reduced_hessian.swapaxes(1, 2)
            )
        ),
    ) / raw_symmetry_denominator
    hessian = 0.5 * (hessian + hessian.swapaxes(1, 2))
    reduced_hessian = 0.5 * (
        reduced_hessian + reduced_hessian.swapaxes(1, 2)
    )

    equation_tensor = np.empty_like(bilinear)
    maximum_gauge_residual = 0.0
    for j in range(reduced):
        for k in range(reduced):
            equation = (
                (linear - np.eye(output)) @ hessian[:, j, k]
                - basis @ reduced_hessian[:, j, k]
                + bilinear[:, j, k]
            )
            equation_tensor[:, j, k] = equation
            maximum_gauge_residual = max(
                maximum_gauge_residual,
                float(np.linalg.norm(left @ hessian[:, j, k])),
            )
    global_equation_residual = float(
        np.linalg.norm(equation_tensor)
        / max(float(np.linalg.norm(bilinear)), np.finfo(float).eps)
    )
    maximum_equation_residual = float(
        max(
            np.linalg.norm(equation_tensor[:, j, k])
            for j in range(reduced)
            for k in range(reduced)
        )
    )

    tangent_relative_residual = float(
        np.linalg.norm(linear @ basis - basis)
        / max(float(np.linalg.norm(basis)), np.finfo(float).eps)
    )
    left_invariance_relative_residual = float(
        np.linalg.norm(left @ linear - left)
        / max(float(np.linalg.norm(left)), np.finfo(float).eps)
    )
    diagnostics = HomologicalDiagnostics(
        augmented_rank=augmented_rank,
        augmented_dimension=augmented_dimension,
        smallest_singular_value=smallest_singular_value,
        condition_number=condition_number,
        tangent_relative_residual=tangent_relative_residual,
        left_invariance_relative_residual=left_invariance_relative_residual,
        raw_symmetry_relative_residual=raw_symmetry_residual,
        global_equation_relative_residual=global_equation_residual,
        maximum_equation_residual=maximum_equation_residual,
        maximum_gauge_residual=maximum_gauge_residual,
    )
    return hessian, reduced_hessian, diagnostics


def solve_general_quadratic_parameterization(
    jacobian: npt.ArrayLike,
    tangent: npt.ArrayLike,
    extractor: npt.ArrayLike,
    reduced_linear: npt.ArrayLike,
    second_derivative: npt.ArrayLike,
) -> tuple[Array, Array, HomologicalDiagnostics]:
    """Solve the dense quadratic homological equation for a general real block.

    This explicit Kronecker oracle materializes the coefficient operator and is
    intended for small manufactured problems.  Large LBM systems require a
    sector-aware sparse or matrix-free implementation.
    """

    raw_inputs = {
        "jacobian": np.asarray(jacobian),
        "tangent": np.asarray(tangent),
        "extractor": np.asarray(extractor),
        "reduced_linear": np.asarray(reduced_linear),
        "second_derivative": np.asarray(second_derivative),
    }
    if any(np.iscomplexobj(array) for array in raw_inputs.values()):
        raise ValueError(
            "general quadratic solver requires an explicit real-block representation"
        )
    linear = np.asarray(raw_inputs["jacobian"], dtype=np.float64)
    basis = np.asarray(raw_inputs["tangent"], dtype=np.float64)
    left = np.asarray(raw_inputs["extractor"], dtype=np.float64)
    reduced_map = np.asarray(raw_inputs["reduced_linear"], dtype=np.float64)
    bilinear = np.asarray(raw_inputs["second_derivative"], dtype=np.float64)
    if basis.ndim != 2:
        raise ValueError("tangent must be a matrix")
    output, reduced = basis.shape
    if linear.shape != (output, output):
        raise ValueError("jacobian shape is inconsistent with tangent")
    if left.shape != (reduced, output):
        raise ValueError("extractor shape is inconsistent with tangent")
    if reduced_map.shape != (reduced, reduced):
        raise ValueError("reduced linear map must be square on reduced coordinates")
    if bilinear.shape != (output, reduced, reduced):
        raise ValueError("second derivative shape is inconsistent with tangent")
    if not all(
        np.all(np.isfinite(array))
        for array in (linear, basis, left, reduced_map, bilinear)
    ):
        raise ValueError("homological inputs must be finite")
    if not np.allclose(
        left @ basis,
        np.eye(reduced),
        atol=1.0e-11,
        rtol=0.0,
    ):
        raise ValueError("extractor and tangent must satisfy L @ V = I")

    hessian_size = output * reduced * reduced
    reduced_hessian_size = reduced * reduced * reduced
    unknown_size = hessian_size + reduced_hessian_size

    def apply_operator(hessian: Array, reduced_hessian: Array) -> Array:
        equation = (
            np.einsum("il,ljk->ijk", linear, hessian)
            - np.einsum(
                "ipq,pj,qk->ijk",
                hessian,
                reduced_map,
                reduced_map,
            )
            - np.einsum("ir,rjk->ijk", basis, reduced_hessian)
        )
        gauge = np.einsum("ri,ijk->rjk", left, hessian)
        return np.concatenate([equation.ravel(), gauge.ravel()])

    operator = np.empty((unknown_size, unknown_size), dtype=np.float64)
    for column in range(unknown_size):
        hessian = np.zeros((output, reduced, reduced), dtype=np.float64)
        reduced_hessian = np.zeros((reduced, reduced, reduced), dtype=np.float64)
        if column < hessian_size:
            hessian.ravel()[column] = 1.0
        else:
            reduced_hessian.ravel()[column - hessian_size] = 1.0
        operator[:, column] = apply_operator(hessian, reduced_hessian)

    singular_values = np.linalg.svd(operator, compute_uv=False)
    augmented_rank = int(np.linalg.matrix_rank(operator))
    if augmented_rank < unknown_size:
        raise np.linalg.LinAlgError(
            "quadratic homological operator is rank deficient; "
            "the selected spectral subspace is resonant or unresolved"
        )
    right_hand_side = np.concatenate(
        [-bilinear.ravel(), np.zeros(reduced_hessian_size)]
    )
    solution, *_ = np.linalg.lstsq(operator, right_hand_side, rcond=None)
    hessian = solution[:hessian_size].reshape(output, reduced, reduced)
    reduced_hessian = solution[hessian_size:].reshape(
        reduced,
        reduced,
        reduced,
    )
    raw_symmetry_denominator = max(
        float(np.linalg.norm(hessian)),
        float(np.linalg.norm(reduced_hessian)),
        np.finfo(float).eps,
    )
    raw_symmetry_residual = max(
        float(np.linalg.norm(hessian - hessian.swapaxes(1, 2))),
        float(
            np.linalg.norm(
                reduced_hessian - reduced_hessian.swapaxes(1, 2)
            )
        ),
    ) / raw_symmetry_denominator
    hessian = 0.5 * (hessian + hessian.swapaxes(1, 2))
    reduced_hessian = 0.5 * (
        reduced_hessian + reduced_hessian.swapaxes(1, 2)
    )

    residual = apply_operator(hessian, reduced_hessian) - right_hand_side
    equation_residual = residual[:hessian_size].reshape(
        output,
        reduced,
        reduced,
    )
    gauge_residual = residual[hessian_size:].reshape(
        reduced,
        reduced,
        reduced,
    )
    global_equation_residual = float(
        np.linalg.norm(equation_residual)
        / max(float(np.linalg.norm(bilinear)), np.finfo(float).eps)
    )
    maximum_equation_residual = float(
        max(
            np.linalg.norm(equation_residual[:, j, k])
            for j in range(reduced)
            for k in range(reduced)
        )
    )
    tangent_relative_residual = float(
        np.linalg.norm(linear @ basis - basis @ reduced_map)
        / max(float(np.linalg.norm(basis)), np.finfo(float).eps)
    )
    left_invariance_relative_residual = float(
        np.linalg.norm(left @ linear - reduced_map @ left)
        / max(float(np.linalg.norm(left)), np.finfo(float).eps)
    )
    diagnostics = HomologicalDiagnostics(
        augmented_rank=augmented_rank,
        augmented_dimension=unknown_size,
        smallest_singular_value=float(singular_values[-1]),
        condition_number=float(singular_values[0] / singular_values[-1]),
        tangent_relative_residual=tangent_relative_residual,
        left_invariance_relative_residual=left_invariance_relative_residual,
        raw_symmetry_relative_residual=raw_symmetry_residual,
        global_equation_relative_residual=global_equation_residual,
        maximum_equation_residual=maximum_equation_residual,
        maximum_gauge_residual=float(
            max(
                np.linalg.norm(gauge_residual[:, j, k])
                for j in range(reduced)
                for k in range(reduced)
            )
        ),
    )
    return hessian, reduced_hessian, diagnostics


def log_log_slope(amplitudes: npt.ArrayLike, residuals: npt.ArrayLike) -> float:
    """Fit the observed residual order over positive finite samples."""

    x = np.asarray(amplitudes, dtype=np.float64)
    y = np.asarray(residuals, dtype=np.float64)
    mask = (x > 0.0) & (y > 0.0) & np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(mask) < 2:
        raise ValueError("at least two positive finite samples are required")
    return float(np.polyfit(np.log(x[mask]), np.log(y[mask]), deg=1)[0])
