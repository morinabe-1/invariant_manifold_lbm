"""TT-parameterized invariant-manifold tools for lattice Boltzmann maps."""

from ._version import __version__
from .d2q9 import (
    D2Q9_CS2,
    D2Q9_VELOCITIES,
    D2Q9_WEIGHTS,
    bgk_periodic_step,
    equilibrium,
    macroscopic,
)
from .manifold import QuadraticChart, invariance_residual
from .stripe import StripeQuadraticModel, build_stripe_quadratic_model

__all__ = [
    "D2Q9_CS2",
    "D2Q9_VELOCITIES",
    "D2Q9_WEIGHTS",
    "QuadraticChart",
    "StripeQuadraticModel",
    "__version__",
    "bgk_periodic_step",
    "build_stripe_quadratic_model",
    "equilibrium",
    "invariance_residual",
    "macroscopic",
]
