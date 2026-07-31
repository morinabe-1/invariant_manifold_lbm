"""Manufactured non-center map for validating general homological solvers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from .manifold import QuadraticChart

Array = npt.NDArray[np.float64]


def _rotation_contraction(radius: float, angle: float) -> Array:
    if not np.isfinite(radius) or not 0.0 < radius < 1.0:
        raise ValueError("radius must be finite and in (0, 1)")
    if not np.isfinite(angle):
        raise ValueError("angle must be finite")
    cosine = np.cos(angle)
    sine = np.sin(angle)
    return radius * np.array([[cosine, -sine], [sine, cosine]])


@dataclass(frozen=True)
class ManufacturedQuadraticMap:
    """Five-state map with a known quadratic invariant manifold.

    The two master coordinates form a stable real rotation block.  The three
    complementary coordinates represent one mean-like scalar and one real
    second-harmonic pair.  The reduced dynamics has a nonzero quadratic term.
    """

    reduced_linear: Array
    reduced_hessian: Array
    chart_hessian: Array
    complement_linear: Array
    state_transform: Array

    def __post_init__(self) -> None:
        reduced_linear = np.asarray(self.reduced_linear, dtype=np.float64)
        reduced_hessian = np.asarray(self.reduced_hessian, dtype=np.float64)
        chart_hessian = np.asarray(self.chart_hessian, dtype=np.float64)
        complement_linear = np.asarray(self.complement_linear, dtype=np.float64)
        state_transform = np.asarray(self.state_transform, dtype=np.float64)
        if reduced_linear.shape != (2, 2):
            raise ValueError("reduced_linear must have shape (2, 2)")
        if reduced_hessian.shape != (2, 2, 2):
            raise ValueError("reduced_hessian must have shape (2, 2, 2)")
        if chart_hessian.shape != (5, 2, 2):
            raise ValueError("chart_hessian must have shape (5, 2, 2)")
        if complement_linear.shape != (3, 3):
            raise ValueError("complement_linear must have shape (3, 3)")
        if state_transform.shape != (5, 5):
            raise ValueError("state_transform must have shape (5, 5)")
        if not all(
            np.all(np.isfinite(array))
            for array in (
                reduced_linear,
                reduced_hessian,
                chart_hessian,
                complement_linear,
                state_transform,
            )
        ):
            raise ValueError("manufactured coefficients must be finite")
        if np.linalg.matrix_rank(state_transform) != 5:
            raise ValueError("state_transform must be invertible")
        if not np.allclose(
            reduced_hessian,
            reduced_hessian.swapaxes(1, 2),
            atol=1.0e-14,
            rtol=0.0,
        ):
            raise ValueError("reduced_hessian must be symmetric in its inputs")
        if not np.allclose(
            chart_hessian,
            chart_hessian.swapaxes(1, 2),
            atol=1.0e-14,
            rtol=0.0,
        ):
            raise ValueError("chart_hessian must be symmetric in its inputs")
        object.__setattr__(self, "reduced_linear", reduced_linear)
        object.__setattr__(self, "reduced_hessian", reduced_hessian)
        object.__setattr__(self, "chart_hessian", chart_hessian)
        object.__setattr__(self, "complement_linear", complement_linear)
        object.__setattr__(self, "state_transform", state_transform)
        if not np.allclose(
            self.extractor @ chart_hessian.reshape(5, -1),
            0.0,
            atol=1.0e-13,
            rtol=0.0,
        ):
            raise ValueError("chart_hessian must satisfy the graph gauge L @ H = 0")

    @property
    def tangent(self) -> Array:
        return self.state_transform[:, :2].copy()

    @property
    def extractor(self) -> Array:
        return np.linalg.inv(self.state_transform)[:2, :]

    @property
    def jacobian(self) -> Array:
        canonical = np.zeros((5, 5), dtype=np.float64)
        canonical[:2, :2] = self.reduced_linear
        canonical[2:, 2:] = self.complement_linear
        return self.state_transform @ canonical @ np.linalg.inv(self.state_transform)

    @property
    def second_derivative(self) -> Array:
        transported = np.einsum(
            "ipq,pj,qk->ijk",
            self.chart_hessian,
            self.reduced_linear,
            self.reduced_linear,
        )
        complement_action = np.einsum(
            "il,ljk->ijk",
            self.jacobian,
            self.chart_hessian,
        )
        return (
            np.einsum("ir,rjk->ijk", self.tangent, self.reduced_hessian)
            + transported
            - complement_action
        )

    @property
    def chart(self) -> QuadraticChart:
        return QuadraticChart(
            np.zeros(5, dtype=np.float64),
            self.tangent,
            self.chart_hessian,
        )

    def reduced_map(self, coordinates: npt.ArrayLike) -> Array:
        a = np.asarray(coordinates, dtype=np.float64)
        if a.shape != (2,):
            raise ValueError("manufactured reduced coordinates must have shape (2,)")
        return self.reduced_linear @ a + 0.5 * np.einsum(
            "ijk,j,k->i",
            self.reduced_hessian,
            a,
            a,
        )

    def full_map(self, state: npt.ArrayLike) -> Array:
        x = np.asarray(state, dtype=np.float64)
        if x.shape != (5,):
            raise ValueError("manufactured state must have shape (5,)")
        coordinates = self.extractor @ x
        on_manifold = self.chart.evaluate(coordinates)
        lifted_next = self.chart.evaluate(self.reduced_map(coordinates))
        complement = x - on_manifold
        return lifted_next + self.jacobian @ complement


def make_manufactured_quadratic_map(
    mean_multiplier: float = 0.25,
) -> ManufacturedQuadraticMap:
    """Create the default oracle, with a tunable mean-sector near resonance."""

    if not np.isfinite(mean_multiplier) or abs(mean_multiplier) >= 1.0:
        raise ValueError("mean_multiplier must be finite with modulus below one")
    reduced_linear = _rotation_contraction(0.82, 0.37)
    reduced_hessian = np.array(
        [
            [[0.12, -0.04], [-0.04, 0.05]],
            [[-0.03, 0.08], [0.08, -0.06]],
        ],
        dtype=np.float64,
    )
    canonical_chart_hessian = np.zeros((5, 2, 2), dtype=np.float64)
    canonical_chart_hessian[2] = 0.30 * np.eye(2)
    canonical_chart_hessian[3] = 0.20 * np.diag([1.0, -1.0])
    canonical_chart_hessian[4] = np.array([[0.0, 0.20], [0.20, 0.0]])
    complement_linear = np.zeros((3, 3), dtype=np.float64)
    complement_linear[0, 0] = mean_multiplier
    complement_linear[1:, 1:] = _rotation_contraction(0.35, 0.70)
    state_transform = np.array(
        [
            [1.00, 0.25, 0.15, 0.00, 0.05],
            [0.00, 1.00, -0.12, 0.08, 0.00],
            [0.20, 0.00, 1.00, 0.15, 0.00],
            [0.00, 0.10, 0.00, 1.00, 0.20],
            [0.05, 0.00, 0.10, 0.00, 1.00],
        ],
        dtype=np.float64,
    )
    chart_hessian = np.einsum(
        "il,ljk->ijk",
        state_transform,
        canonical_chart_hessian,
    )
    return ManufacturedQuadraticMap(
        reduced_linear=reduced_linear,
        reduced_hessian=reduced_hessian,
        chart_hessian=chart_hessian,
        complement_linear=complement_linear,
        state_transform=state_transform,
    )


@dataclass(frozen=True)
class RealBiorthogonalPair:
    """Real right/left representation of one complex-conjugate invariant pair."""

    right_basis: Array
    left_extractor: Array
    block: Array
    right_invariance_residual: float
    left_invariance_residual: float
    duality_residual: float
    conjugacy_error: float


def real_basis_from_dominant_complex_pair(
    matrix: npt.ArrayLike,
) -> RealBiorthogonalPair:
    """Convert the dominant complex pair to a normalized real biorthogonal block."""

    raw_matrix = np.asarray(matrix)
    if np.iscomplexobj(raw_matrix):
        raise ValueError("matrix must be real before real-block conversion")
    linear = np.asarray(raw_matrix, dtype=np.float64)
    if linear.ndim != 2 or linear.shape[0] != linear.shape[1]:
        raise ValueError("matrix must be square")
    eigenvalues, eigenvectors = np.linalg.eig(linear)
    candidates = [
        index for index, value in enumerate(eigenvalues) if value.imag > 1.0e-10
    ]
    if not candidates:
        raise ValueError("matrix has no resolved positive-imaginary eigenvalue")
    index = max(candidates, key=lambda item: abs(eigenvalues[item]))
    eigenvalue = complex(eigenvalues[index])
    eigenvector = eigenvectors[:, index]
    try:
        left_eigenvectors = np.linalg.inv(eigenvectors).conj().T
    except np.linalg.LinAlgError as error:
        raise np.linalg.LinAlgError(
            "eigenvector matrix is singular; the complex pair is unresolved"
        ) from error
    left_eigenvector = left_eigenvectors[:, index]
    basis = np.column_stack([eigenvector.real, -eigenvector.imag])
    extractor = np.vstack(
        [2.0 * left_eigenvector.real, -2.0 * left_eigenvector.imag]
    )
    common_scale = max(float(np.linalg.norm(basis[:, 0])), np.finfo(float).eps)
    basis /= common_scale
    extractor *= common_scale
    block = np.array(
        [
            [eigenvalue.real, -eigenvalue.imag],
            [eigenvalue.imag, eigenvalue.real],
        ]
    )
    right_residual = float(
        np.linalg.norm(linear @ basis - basis @ block)
        / max(float(np.linalg.norm(basis)), np.finfo(float).eps)
    )
    left_residual = float(
        np.linalg.norm(extractor @ linear - block @ extractor)
        / max(float(np.linalg.norm(extractor)), np.finfo(float).eps)
    )
    duality_residual = float(np.linalg.norm(extractor @ basis - np.eye(2)))
    conjugacy_error = float(
        min(abs(value - eigenvalue.conjugate()) for value in eigenvalues)
    )
    return RealBiorthogonalPair(
        right_basis=basis,
        left_extractor=extractor,
        block=block,
        right_invariance_residual=right_residual,
        left_invariance_residual=left_residual,
        duality_residual=duality_residual,
        conjugacy_error=conjugacy_error,
    )
