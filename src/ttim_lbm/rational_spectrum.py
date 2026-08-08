"""Sealed Q007h rational-interval certification of the linear spectrum.

Floating-point eigendecompositions are used only to propose a diagonalizing
matrix.  Every error bound and every hypothesis gate is evaluated with exact
``fractions.Fraction`` endpoints.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from .adapted_metric import (
    ETA,
    EXPECTED_SELECTED_WAVE_COUNT,
    FIXED_LEAF_DIMENSION,
    OMEGA,
    SELECTED_COMPLEX_DIMENSION,
    SIZE,
)
from .checkerboard_filter import filtered_fourier_symbol
from .provenance import source_metadata

ComplexArray = npt.NDArray[np.complex128]
WaveIndex = tuple[int, int]

MACHIN_TERMS = 96
TRIGONOMETRIC_TERMS = 64
INTERVAL_DECIMAL_DIGITS = 140
SQRT_DECIMAL_DIGITS = 100

MAXIMUM_PI_TRIGONOMETRIC_WIDTH = Fraction(1, 10**120)
MAXIMUM_SYMBOL_ENTRY_WIDTH = Fraction(1, 10**110)
MAXIMUM_INVERSE_DEFECT = Fraction(1, 10**10)
MAXIMUM_BAUER_FIKE_RADIUS = Fraction(1, 10**8)
MINIMUM_SELECTED_GROUP_GAP = Fraction(1, 10**6)
MAXIMUM_FLOAT_REPRODUCTION_RELATIVE_ERROR = 1.0e-10
MAXIMUM_SYMMETRY_ENDPOINT_DIFFERENCE = Fraction(1, 10**12)

Q007G_ARTIFACT = "q007g_theorem_readiness.json"
EXPECTED_SELECTED_COUNT = 24
EXPECTED_EXCLUDED_COUNT = 2574
EXPECTED_FIXED_LEAF_COUNT = 2598
TAIL_DEGREE = 90

VELOCITIES: tuple[tuple[int, int], ...] = (
    (0, 0),
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, 1),
    (-1, 1),
    (-1, -1),
    (1, -1),
)
WEIGHTS: tuple[Fraction, ...] = (
    Fraction(4, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 36),
    Fraction(1, 36),
    Fraction(1, 36),
    Fraction(1, 36),
)
SELECTED_WAVES = frozenset(
    (nx, ny)
    for nx in (-1, 0, 1)
    for ny in (-1, 0, 1)
    if (nx, ny) != (0, 0)
)


def _as_fraction(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _floor_scaled(value: Fraction, scale: int) -> int:
    return value.numerator * scale // value.denominator


def _ceil_scaled(value: Fraction, scale: int) -> int:
    return -((-value.numerator * scale) // value.denominator)


@dataclass(frozen=True, slots=True)
class RationalInterval:
    """A closed real interval with exact rational endpoints."""

    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "lower", _as_fraction(self.lower))
        object.__setattr__(self, "upper", _as_fraction(self.upper))
        if self.lower > self.upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    @classmethod
    def point(cls, value: int | Fraction) -> RationalInterval:
        endpoint = _as_fraction(value)
        return cls(endpoint, endpoint)

    @property
    def width(self) -> Fraction:
        return self.upper - self.lower

    @property
    def maximum_absolute_value(self) -> Fraction:
        return max(abs(self.lower), abs(self.upper))

    def __add__(self, other: RationalInterval) -> RationalInterval:
        return RationalInterval(
            self.lower + other.lower,
            self.upper + other.upper,
        )

    def __neg__(self) -> RationalInterval:
        return RationalInterval(-self.upper, -self.lower)

    def __sub__(self, other: RationalInterval) -> RationalInterval:
        return self + (-other)

    def __mul__(self, other: RationalInterval) -> RationalInterval:
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return RationalInterval(min(products), max(products))

    def scale(self, scalar: int | Fraction) -> RationalInterval:
        value = _as_fraction(scalar)
        if value >= 0:
            return RationalInterval(self.lower * value, self.upper * value)
        return RationalInterval(self.upper * value, self.lower * value)

    def rounded_outward(self, digits: int = INTERVAL_DECIMAL_DIGITS) -> RationalInterval:
        """Round to a decimal rational grid without losing containment."""

        if digits <= 0:
            raise ValueError("digits must be positive")
        scale = 10**digits
        return RationalInterval(
            Fraction(_floor_scaled(self.lower, scale), scale),
            Fraction(_ceil_scaled(self.upper, scale), scale),
        )


@dataclass(frozen=True, slots=True)
class ComplexRationalInterval:
    """A closed complex rectangle with rational real and imaginary parts."""

    real: RationalInterval
    imag: RationalInterval

    @classmethod
    def zero(cls) -> ComplexRationalInterval:
        zero = RationalInterval.point(0)
        return cls(zero, zero)

    @classmethod
    def point(
        cls,
        real: int | Fraction,
        imag: int | Fraction = 0,
    ) -> ComplexRationalInterval:
        return cls(RationalInterval.point(real), RationalInterval.point(imag))

    def __add__(self, other: ComplexRationalInterval) -> ComplexRationalInterval:
        return ComplexRationalInterval(
            self.real + other.real,
            self.imag + other.imag,
        )

    def __neg__(self) -> ComplexRationalInterval:
        return ComplexRationalInterval(-self.real, -self.imag)

    def __sub__(self, other: ComplexRationalInterval) -> ComplexRationalInterval:
        return self + (-other)

    def __mul__(self, other: ComplexRationalInterval) -> ComplexRationalInterval:
        return ComplexRationalInterval(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    def scale(self, scalar: int | Fraction) -> ComplexRationalInterval:
        return ComplexRationalInterval(
            self.real.scale(scalar),
            self.imag.scale(scalar),
        )


ComplexIntervalMatrix = list[list[ComplexRationalInterval]]


def _fraction_from_float(value: float) -> Fraction:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("cannot convert a non-finite float to a rational")
    return Fraction.from_float(value)


def _complex_point(value: complex) -> ComplexRationalInterval:
    number = complex(value)
    return ComplexRationalInterval.point(
        _fraction_from_float(number.real),
        _fraction_from_float(number.imag),
    )


def _sqrt_bounds(
    value: Fraction,
    digits: int = SQRT_DECIMAL_DIGITS,
) -> RationalInterval:
    """Enclose a nonnegative rational square root using integer ``isqrt``."""

    if value < 0:
        raise ValueError("square root requires a nonnegative rational")
    if value == 0:
        return RationalInterval.point(0)
    scale = 10**digits
    scaled_floor = value.numerator * scale * scale // value.denominator
    root_floor = math.isqrt(scaled_floor)
    return RationalInterval(
        Fraction(root_floor, scale),
        Fraction(root_floor + 1, scale),
    )


def _complex_absolute_bounds(value: ComplexRationalInterval) -> RationalInterval:
    if value.real.width != 0 or value.imag.width != 0:
        raise ValueError("point complex interval required")
    square = value.real.lower**2 + value.imag.lower**2
    return _sqrt_bounds(square)


def _complex_rectangle_absolute_upper(value: ComplexRationalInterval) -> Fraction:
    real_maximum = value.real.maximum_absolute_value
    imaginary_maximum = value.imag.maximum_absolute_value
    return _sqrt_bounds(real_maximum**2 + imaginary_maximum**2).upper


def _matrix_from_numpy(value: ComplexArray) -> ComplexIntervalMatrix:
    array = np.asarray(value, dtype=np.complex128)
    if array.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    return [[_complex_point(array[row, column]) for column in range(array.shape[1])] for row in range(array.shape[0])]


def _identity_matrix(dimension: int) -> ComplexIntervalMatrix:
    return [
        [ComplexRationalInterval.point(int(row == column)) for column in range(dimension)]
        for row in range(dimension)
    ]


def _diagonal_matrix(values: Sequence[complex]) -> ComplexIntervalMatrix:
    dimension = len(values)
    return [
        [
            _complex_point(values[row])
            if row == column
            else ComplexRationalInterval.zero()
            for column in range(dimension)
        ]
        for row in range(dimension)
    ]


def _matrix_multiply(
    left: ComplexIntervalMatrix,
    right: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    rows = len(left)
    inner = len(right)
    columns = len(right[0])
    output: ComplexIntervalMatrix = []
    for row in range(rows):
        output_row = []
        for column in range(columns):
            total = ComplexRationalInterval.zero()
            for index in range(inner):
                total = total + left[row][index] * right[index][column]
            output_row.append(total)
        output.append(output_row)
    return output


def _matrix_subtract(
    left: ComplexIntervalMatrix,
    right: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    if len(left) != len(right) or any(
        len(left_row) != len(right_row)
        for left_row, right_row in zip(left, right, strict=True)
    ):
        raise ValueError("matrix shapes differ")
    return [
        [
            left_value - right_value
            for left_value, right_value in zip(left_row, right_row, strict=True)
        ]
        for left_row, right_row in zip(left, right, strict=True)
    ]


def _matrix_infinity_norm_upper(matrix: ComplexIntervalMatrix) -> Fraction:
    return max(
        sum((_complex_rectangle_absolute_upper(value) for value in row), Fraction(0))
        for row in matrix
    )


def _atan_reciprocal_interval(denominator: int) -> RationalInterval:
    inverse = Fraction(1, denominator)
    inverse_square = inverse * inverse
    power = inverse
    partial_sum = Fraction(0)
    for index in range(MACHIN_TERMS):
        term = power / (2 * index + 1)
        partial_sum = partial_sum + term if index % 2 == 0 else partial_sum - term
        power *= inverse_square
    next_term = power / (2 * MACHIN_TERMS + 1)
    if MACHIN_TERMS % 2 == 0:
        return RationalInterval(partial_sum, partial_sum + next_term)
    return RationalInterval(partial_sum - next_term, partial_sum)


def machin_pi_interval() -> RationalInterval:
    """Return the registered 96-term Machin enclosure of pi."""

    atan_fifth = _atan_reciprocal_interval(5)
    atan_239th = _atan_reciprocal_interval(239)
    return (
        atan_fifth.scale(16) - atan_239th.scale(4)
    ).rounded_outward()


def _taylor_polynomial(
    x: RationalInterval,
    coefficients: Sequence[Fraction],
    first_power: int,
) -> RationalInterval:
    if x.lower < 0:
        raise ValueError("the registered Taylor evaluation expects x >= 0")
    result = RationalInterval.point(0)
    for index, coefficient in enumerate(coefficients):
        power = first_power + 2 * index
        power_interval = RationalInterval(
            x.lower**power,
            x.upper**power,
        ).rounded_outward()
        result = (result + power_interval.scale(coefficient)).rounded_outward()
    return result


def trigonometric_intervals(
    pi_interval: RationalInterval | None = None,
) -> dict[int, tuple[RationalInterval, RationalInterval]]:
    """Enclose sine and cosine at all canonical seventeenth-root angles."""

    pi_enclosure = machin_pi_interval() if pi_interval is None else pi_interval
    sine_coefficients = tuple(
        Fraction(-1 if index % 2 else 1, math.factorial(2 * index + 1))
        for index in range(TRIGONOMETRIC_TERMS)
    )
    cosine_coefficients = tuple(
        Fraction(-1 if index % 2 else 1, math.factorial(2 * index))
        for index in range(TRIGONOMETRIC_TERMS)
    )
    positive: dict[int, tuple[RationalInterval, RationalInterval]] = {}
    for index in range(SIZE // 2 + 1):
        x = pi_enclosure.scale(Fraction(2 * index, SIZE))
        if index == 0:
            positive[index] = (
                RationalInterval.point(0),
                RationalInterval.point(1),
            )
            continue
        remainder = x.maximum_absolute_value**128 / math.factorial(128)
        remainder_interval = RationalInterval(-remainder, remainder)
        sine = (
            _taylor_polynomial(x, sine_coefficients, 1) + remainder_interval
        ).rounded_outward()
        cosine = (
            _taylor_polynomial(x, cosine_coefficients, 0) + remainder_interval
        ).rounded_outward()
        positive[index] = (sine, cosine)
    table = dict(positive)
    for index in range(1, SIZE // 2 + 1):
        sine, cosine = positive[index]
        table[-index] = (-sine, cosine)
    return table


def _canonical_index(value: int) -> int:
    half = SIZE // 2
    return (int(value) + half) % SIZE - half


def _wave_indices() -> tuple[WaveIndex, ...]:
    half = SIZE // 2
    return tuple(
        (nx, ny)
        for nx in range(-half, half + 1)
        for ny in range(-half, half + 1)
    )


def rational_collision_symbol() -> tuple[tuple[Fraction, ...], ...]:
    """Construct the exact omega=3/2 D2Q9 collision derivative."""

    rows = []
    for output, ((cx, cy), weight) in enumerate(zip(VELOCITIES, WEIGHTS, strict=True)):
        row = []
        for source, (sx, sy) in enumerate(VELOCITIES):
            projection = weight * (1 + 3 * (cx * sx + cy * sy))
            row.append(
                -Fraction(1, 2) * int(output == source)
                + Fraction(3, 2) * projection
            )
        rows.append(tuple(row))
    return tuple(rows)


def rational_fourier_symbol(
    wave_index: WaveIndex,
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
    collision: tuple[tuple[Fraction, ...], ...],
) -> ComplexIntervalMatrix:
    """Enclose one filtered D2Q9 Fourier block."""

    nx, ny = wave_index
    cosine_x = trig[nx][1]
    cosine_y = trig[ny][1]
    multiplier = (
        RationalInterval.point(Fraction(99, 100))
        + (cosine_x + cosine_y).scale(Fraction(1, 200))
    )
    matrix: ComplexIntervalMatrix = []
    for (cx, cy), collision_row in zip(VELOCITIES, collision, strict=True):
        phase_index = _canonical_index(nx * cx + ny * cy)
        sine, cosine = trig[phase_index]
        phase = ComplexRationalInterval(cosine, -sine)
        matrix.append(
            [
                ComplexRationalInterval(
                    phase.real * multiplier.scale(entry),
                    phase.imag * multiplier.scale(entry),
                )
                for entry in collision_row
            ]
        )
    return matrix


def _relative_scalar_error(observed: float, expected: float) -> float:
    return abs(float(observed) - float(expected)) / max(
        abs(float(expected)),
        np.finfo(float).eps,
    )


def _fraction_record(value: Fraction) -> dict[str, str | float]:
    return {
        "numerator_base16": hex(value.numerator),
        "denominator_base16": hex(value.denominator),
        "float": float(value),
    }


def _interval_record(value: RationalInterval) -> dict[str, Any]:
    return {
        "lower": _fraction_record(value.lower),
        "upper": _fraction_record(value.upper),
        "width": _fraction_record(value.width),
    }


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("r", encoding="utf-8", newline=None) as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), ""):
            digest.update(chunk.encode("utf-8"))
    return digest.hexdigest()


def _default_artifact_directory() -> Path:
    return Path(__file__).resolve().parents[2] / "research" / "artifacts"


def _load_q007g(artifact_directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    path = artifact_directory / Q007G_ARTIFACT
    payload = json.loads(path.read_text(encoding="utf-8"))
    scope = payload.get("mathematical_scope", {})
    cycle = payload.get("cycle", {})
    spectral = cycle.get("spectral_audit", {})
    parameter_match = (
        scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", math.nan)) == OMEGA
        and float(scope.get("eta", math.nan)) == ETA
    )
    dimension_match = (
        spectral.get("selected_complex_dimension") == SELECTED_COMPLEX_DIMENSION
        and spectral.get("excluded_complex_dimension") == EXPECTED_EXCLUDED_COUNT
        and spectral.get("fixed_leaf_complex_dimension") == FIXED_LEAF_DIMENSION
    )
    source_match = payload.get("source") == source_metadata()
    passed = bool(
        payload.get("schema_version") == 1
        and payload.get("study_gate") == "passed"
        and payload.get("scientific_outcome") == "not_ready"
        and parameter_match
        and dimension_match
        and source_match
    )
    return payload, {
        "filename": Q007G_ARTIFACT,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": source_match,
        "parameter_match": parameter_match,
        "dimension_match": dimension_match,
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "passed": passed,
    }


def _proof_digest(values: Iterable[Fraction]) -> str:
    digest = sha256()
    for value in values:
        digest.update(str(value.numerator).encode("ascii"))
        digest.update(b"/")
        digest.update(str(value.denominator).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class _BlockProof:
    wave_index: WaveIndex
    epsilon: Fraction
    beta: Fraction
    bauer_fike_radius: Fraction
    selected_intervals: tuple[RationalInterval, ...]
    excluded_intervals: tuple[RationalInterval, ...]
    selected_group_gap: Fraction | None
    center_selected_moduli: tuple[float, ...]
    center_excluded_moduli: tuple[float, ...]
    maximum_symbol_entry_width: Fraction
    proof_digest: str

    @property
    def selected_count(self) -> int:
        return len(self.selected_intervals)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded_intervals)


def _modulus_disk_interval(center: complex, radius: Fraction) -> RationalInterval:
    center_bounds = _complex_absolute_bounds(_complex_point(center))
    return RationalInterval(
        max(Fraction(0), center_bounds.lower - radius),
        center_bounds.upper + radius,
    )


def _center_distance_lower(left: complex, right: complex) -> Fraction:
    difference = _complex_point(left) - _complex_point(right)
    return _complex_absolute_bounds(difference).lower


def _certify_nonzero_block(
    wave_index: WaveIndex,
    symbol: ComplexIntervalMatrix,
    center: ComplexArray,
) -> _BlockProof:
    eigenvalues, eigenvectors = np.linalg.eig(center)
    inverse_candidate = np.linalg.inv(eigenvectors)
    eigenvector_matrix = _matrix_from_numpy(eigenvectors)
    inverse_matrix = _matrix_from_numpy(inverse_candidate)
    diagonal = _diagonal_matrix(eigenvalues)
    inverse_defect = _matrix_subtract(
        _identity_matrix(9),
        _matrix_multiply(inverse_matrix, eigenvector_matrix),
    )
    epsilon = _matrix_infinity_norm_upper(inverse_defect)
    if epsilon >= 1:
        beta = Fraction(10**1000)
    else:
        beta = _matrix_infinity_norm_upper(inverse_matrix) / (1 - epsilon)
    residual = _matrix_subtract(
        _matrix_multiply(symbol, eigenvector_matrix),
        _matrix_multiply(eigenvector_matrix, diagonal),
    )
    residual_norm = _matrix_infinity_norm_upper(residual)
    eigenvector_norm = _matrix_infinity_norm_upper(eigenvector_matrix)
    radius = eigenvector_norm * beta * beta * residual_norm

    center_moduli = np.abs(eigenvalues)
    if wave_index in SELECTED_WAVES:
        ordered = np.argsort(center_moduli)[::-1]
        selected_indices = frozenset(int(index) for index in ordered[:3])
    else:
        selected_indices = frozenset()
    excluded_indices = tuple(
        index for index in range(9) if index not in selected_indices
    )
    selected_indices_ordered = tuple(sorted(selected_indices))
    selected_intervals = tuple(
        _modulus_disk_interval(eigenvalues[index], radius)
        for index in selected_indices_ordered
    )
    excluded_intervals = tuple(
        _modulus_disk_interval(eigenvalues[index], radius)
        for index in excluded_indices
    )
    selected_group_gap = None
    if selected_indices_ordered:
        selected_group_gap = min(
            _center_distance_lower(eigenvalues[left], eigenvalues[right]) - 2 * radius
            for left in selected_indices_ordered
            for right in excluded_indices
        )
    maximum_symbol_entry_width = max(
        max(value.real.width, value.imag.width)
        for row in symbol
        for value in row
    )
    digest_values = [epsilon, beta, radius, maximum_symbol_entry_width]
    for value in eigenvalues:
        point = _complex_point(value)
        digest_values.extend((point.real.lower, point.imag.lower))
    for value in (*selected_intervals, *excluded_intervals):
        digest_values.extend((value.lower, value.upper))
    return _BlockProof(
        wave_index=wave_index,
        epsilon=epsilon,
        beta=beta,
        bauer_fike_radius=radius,
        selected_intervals=selected_intervals,
        excluded_intervals=excluded_intervals,
        selected_group_gap=selected_group_gap,
        center_selected_moduli=tuple(
            float(center_moduli[index]) for index in selected_indices_ordered
        ),
        center_excluded_moduli=tuple(
            float(center_moduli[index]) for index in excluded_indices
        ),
        maximum_symbol_entry_width=maximum_symbol_entry_width,
        proof_digest=_proof_digest(digest_values),
    )


def _zero_block_proof() -> _BlockProof:
    exact = RationalInterval.point(Fraction(1, 2))
    return _BlockProof(
        wave_index=(0, 0),
        epsilon=Fraction(0),
        beta=Fraction(0),
        bauer_fike_radius=Fraction(0),
        selected_intervals=(),
        excluded_intervals=(exact,) * 6,
        selected_group_gap=None,
        center_selected_moduli=(),
        center_excluded_moduli=(0.5,) * 6,
        maximum_symbol_entry_width=Fraction(0),
        proof_digest=_proof_digest((Fraction(-1, 2), Fraction(6))),
    )


def _sorted_intervals(values: Sequence[RationalInterval]) -> tuple[RationalInterval, ...]:
    return tuple(sorted(values, key=lambda value: (value.lower + value.upper, value.lower)))


def _interval_sequence_difference(
    left: Sequence[RationalInterval],
    right: Sequence[RationalInterval],
) -> Fraction:
    if len(left) != len(right):
        raise ValueError("symmetry-related interval sequences have different sizes")
    left_sorted = _sorted_intervals(left)
    right_sorted = _sorted_intervals(right)
    return max(
        (
            max(
                abs(left_value.lower - right_value.lower),
                abs(left_value.upper - right_value.upper),
            )
            for left_value, right_value in zip(left_sorted, right_sorted, strict=True)
        ),
        default=Fraction(0),
    )


def _symmetry_audit(proofs: dict[WaveIndex, _BlockProof]) -> dict[str, Any]:
    maximum_conjugate = Fraction(0)
    maximum_quarter_turn = Fraction(0)
    worst_conjugate: dict[str, Any] | None = None
    worst_quarter_turn: dict[str, Any] | None = None
    for wave_index, proof in proofs.items():
        nx, ny = wave_index
        conjugate_index = (_canonical_index(-nx), _canonical_index(-ny))
        quarter_turn_index = (_canonical_index(-ny), _canonical_index(nx))
        conjugate = proofs[conjugate_index]
        quarter_turn = proofs[quarter_turn_index]
        conjugate_selected = _interval_sequence_difference(
            proof.selected_intervals,
            conjugate.selected_intervals,
        )
        conjugate_excluded = _interval_sequence_difference(
            proof.excluded_intervals,
            conjugate.excluded_intervals,
        )
        conjugate_difference = max(conjugate_selected, conjugate_excluded)
        if conjugate_difference > maximum_conjugate:
            maximum_conjugate = conjugate_difference
            worst_conjugate = {
                "source_wave": list(wave_index),
                "target_wave": list(conjugate_index),
                "group": (
                    "selected"
                    if conjugate_selected >= conjugate_excluded
                    else "excluded"
                ),
            }
        quarter_turn_selected = _interval_sequence_difference(
            proof.selected_intervals,
            quarter_turn.selected_intervals,
        )
        quarter_turn_excluded = _interval_sequence_difference(
            proof.excluded_intervals,
            quarter_turn.excluded_intervals,
        )
        quarter_turn_difference = max(
            quarter_turn_selected,
            quarter_turn_excluded,
        )
        if quarter_turn_difference > maximum_quarter_turn:
            maximum_quarter_turn = quarter_turn_difference
            worst_quarter_turn = {
                "source_wave": list(wave_index),
                "target_wave": list(quarter_turn_index),
                "group": (
                    "selected"
                    if quarter_turn_selected >= quarter_turn_excluded
                    else "excluded"
                ),
            }
    return {
        "conjugate_comparison_count": len(proofs),
        "quarter_turn_comparison_count": len(proofs),
        "maximum_conjugate_endpoint_difference": _fraction_record(maximum_conjugate),
        "maximum_quarter_turn_endpoint_difference": _fraction_record(
            maximum_quarter_turn
        ),
        "worst_conjugate_comparison": worst_conjugate,
        "worst_quarter_turn_comparison": worst_quarter_turn,
        "maximum_conjugate_endpoint_difference_exact": maximum_conjugate,
        "maximum_quarter_turn_endpoint_difference_exact": maximum_quarter_turn,
    }


def _block_record(proof: _BlockProof) -> dict[str, Any]:
    selected_lower = min(
        (value.lower for value in proof.selected_intervals),
        default=None,
    )
    selected_upper = max(
        (value.upper for value in proof.selected_intervals),
        default=None,
    )
    excluded_lower = min(value.lower for value in proof.excluded_intervals)
    excluded_upper = max(value.upper for value in proof.excluded_intervals)
    return {
        "wave_index": list(proof.wave_index),
        "epsilon": _fraction_record(proof.epsilon),
        "beta": _fraction_record(proof.beta),
        "bauer_fike_radius": _fraction_record(proof.bauer_fike_radius),
        "selected_count": proof.selected_count,
        "excluded_count": proof.excluded_count,
        "selected_modulus_lower": (
            None if selected_lower is None else float(selected_lower)
        ),
        "selected_modulus_upper": (
            None if selected_upper is None else float(selected_upper)
        ),
        "excluded_modulus_lower": float(excluded_lower),
        "excluded_modulus_upper": float(excluded_upper),
        "selected_group_gap": (
            None
            if proof.selected_group_gap is None
            else _fraction_record(proof.selected_group_gap)
        ),
        "maximum_symbol_entry_rectangle_width": _fraction_record(
            proof.maximum_symbol_entry_width
        ),
        "exact_proof_digest_sha256": proof.proof_digest,
    }


def _all_numeric_values_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_numeric_values_finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_all_numeric_values_finite(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return bool(np.isfinite(value))
    return True


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_rational_spectral_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the preregistered Q007h rational-interval linear audit."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007g, q007g_record = _load_q007g(directory)
    registered_spectral = q007g["cycle"]["spectral_audit"]

    pi_enclosure = machin_pi_interval()
    trig = trigonometric_intervals(pi_enclosure)
    collision = rational_collision_symbol()
    proofs: dict[WaveIndex, _BlockProof] = {(0, 0): _zero_block_proof()}
    for wave_index in _wave_indices():
        if wave_index == (0, 0):
            continue
        symbol = rational_fourier_symbol(wave_index, trig, collision)
        kx = 2.0 * np.pi * wave_index[0] / SIZE
        ky = 2.0 * np.pi * wave_index[1] / SIZE
        center = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
        proofs[wave_index] = _certify_nonzero_block(wave_index, symbol, center)

    selected_intervals = tuple(
        value for proof in proofs.values() for value in proof.selected_intervals
    )
    excluded_intervals = tuple(
        value for proof in proofs.values() for value in proof.excluded_intervals
    )
    center_selected = tuple(
        value for proof in proofs.values() for value in proof.center_selected_moduli
    )
    center_excluded = tuple(
        value for proof in proofs.values() for value in proof.center_excluded_moduli
    )
    selected_minimum = min(value.lower for value in selected_intervals)
    selected_maximum = max(value.upper for value in selected_intervals)
    excluded_minimum = min(value.lower for value in excluded_intervals)
    excluded_maximum = max(value.upper for value in excluded_intervals)
    normal_gap = selected_minimum - excluded_maximum
    tail_ratio = selected_maximum**TAIL_DEGREE / excluded_minimum

    nonzero_proofs = tuple(
        proof for wave_index, proof in proofs.items() if wave_index != (0, 0)
    )
    selected_proofs = tuple(proofs[wave] for wave in sorted(SELECTED_WAVES))
    maximum_trig_width = max(
        value.width
        for pair in trig.values()
        for value in pair
    )
    maximum_symbol_width = max(
        proof.maximum_symbol_entry_width for proof in nonzero_proofs
    )
    maximum_epsilon = max(proof.epsilon for proof in nonzero_proofs)
    maximum_radius = max(proof.bauer_fike_radius for proof in nonzero_proofs)
    minimum_group_gap = min(
        proof.selected_group_gap
        for proof in selected_proofs
        if proof.selected_group_gap is not None
    )
    symmetry_internal = _symmetry_audit(proofs)
    maximum_symmetry_difference = max(
        symmetry_internal["maximum_conjugate_endpoint_difference_exact"],
        symmetry_internal["maximum_quarter_turn_endpoint_difference_exact"],
    )
    symmetry = {
        key: value
        for key, value in symmetry_internal.items()
        if not key.endswith("_exact")
    }

    observed_float = {
        "selected_minimum_modulus": min(center_selected),
        "selected_maximum_modulus": max(center_selected),
        "excluded_minimum_modulus": min(center_excluded),
        "excluded_maximum_modulus": max(center_excluded),
    }
    reproduction = {
        key: _relative_scalar_error(observed, registered_spectral[key])
        for key, observed in observed_float.items()
    }

    interval_construction = {
        "endpoint_type": "fractions.Fraction",
        "machin_terms_per_arctangent": MACHIN_TERMS,
        "trigonometric_taylor_terms": TRIGONOMETRIC_TERMS,
        "taylor_remainder": "degree-127 Lagrange bound |x|^128 / 128!",
        "outward_decimal_grid_digits": INTERVAL_DECIMAL_DIGITS,
        "sqrt_integer_isqrt_decimal_digits": SQRT_DECIMAL_DIGITS,
        "pi_interval": _interval_record(pi_enclosure),
        "maximum_trigonometric_interval_width": _fraction_record(
            maximum_trig_width
        ),
        "maximum_symbol_entry_rectangle_width": _fraction_record(
            maximum_symbol_width
        ),
    }
    eigencertification = {
        "nonzero_block_count": len(nonzero_proofs),
        "selected_wave_count": len(selected_proofs),
        "maximum_inverse_defect_epsilon": _fraction_record(maximum_epsilon),
        "all_inverse_defects_strictly_below_one": all(
            proof.epsilon < 1 for proof in nonzero_proofs
        ),
        "maximum_bauer_fike_radius": _fraction_record(maximum_radius),
        "minimum_selected_excluded_disc_group_gap": _fraction_record(
            minimum_group_gap
        ),
        "float_center_extrema": observed_float,
        "q007g_relative_reproduction_errors": reproduction,
        "selected_count": len(selected_intervals),
        "excluded_count": len(excluded_intervals),
        "fixed_leaf_count": len(selected_intervals) + len(excluded_intervals),
        "zero_wave_fixed_leaf_spectrum": {
            "eigenvalue": "-1/2",
            "multiplicity": 6,
            "derivation": "exact kinetic eigenspace of the rational collision symbol",
        },
        "homotopy_count_argument": (
            "V Lambda V^-1 to A remains in the Bauer--Fike disc unions; "
            "the selected and excluded unions are disjoint at every selected wave"
        ),
        "block_records": [_block_record(proofs[wave]) for wave in _wave_indices()],
    }
    global_bounds = {
        "selected_minimum_modulus": _fraction_record(selected_minimum),
        "selected_spectral_radius": _fraction_record(selected_maximum),
        "excluded_minimum_modulus": _fraction_record(excluded_minimum),
        "excluded_maximum_modulus": _fraction_record(excluded_maximum),
        "normal_gap": _fraction_record(normal_gap),
        "tail_degree": TAIL_DEGREE,
        "tail_ratio": _fraction_record(tail_ratio),
    }

    serializable_sections = {
        "q007g_input": q007g_record,
        "interval_construction": interval_construction,
        "eigencertification": eigencertification,
        "global_bounds": global_bounds,
        "symmetry": symmetry,
    }
    finite_and_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007g_input": {
            "passed": q007g_record["passed"],
            "threshold": "Q007g source, scope, outcome, and 24/2574/2598 dimensions match",
            "value": q007g_record["passed"],
        },
        "rational_interval_widths": {
            "passed": bool(
                pi_enclosure.width <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_trig_width <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_symbol_width <= MAXIMUM_SYMBOL_ENTRY_WIDTH
            ),
            "threshold": "pi/trig <= 1e-120 and symbol rectangles <= 1e-110",
            "value": {
                "pi_width": float(pi_enclosure.width),
                "maximum_trig_width": float(maximum_trig_width),
                "maximum_symbol_width": float(maximum_symbol_width),
            },
        },
        "inverse_preconditioners": {
            "passed": bool(
                all(proof.epsilon < 1 for proof in nonzero_proofs)
                and maximum_epsilon <= MAXIMUM_INVERSE_DEFECT
            ),
            "threshold": "all epsilon < 1 and maximum epsilon <= 1e-10",
            "value": float(maximum_epsilon),
        },
        "bauer_fike_enclosures": {
            "passed": bool(
                all(math.isfinite(float(proof.bauer_fike_radius)) for proof in nonzero_proofs)
                and maximum_radius <= MAXIMUM_BAUER_FIKE_RADIUS
            ),
            "threshold": "all finite and maximum radius <= 1e-8",
            "value": float(maximum_radius),
        },
        "selected_disc_group_separation": {
            "passed": bool(
                len(selected_proofs) == EXPECTED_SELECTED_WAVE_COUNT
                and all(proof.selected_count == 3 for proof in selected_proofs)
                and minimum_group_gap >= MINIMUM_SELECTED_GROUP_GAP
            ),
            "threshold": "8 waves, 3 selected centers each, group gap >= 1e-6",
            "value": {
                "selected_wave_count": len(selected_proofs),
                "minimum_group_gap": float(minimum_group_gap),
            },
        },
        "q007g_float_center_reproduction": {
            "passed": max(reproduction.values())
            <= MAXIMUM_FLOAT_REPRODUCTION_RELATIVE_ERROR,
            "threshold": "all four extrema relative errors <= 1e-10",
            "value": max(reproduction.values()),
        },
        "conjugate_and_c4_symmetry": {
            "passed": maximum_symmetry_difference
            <= MAXIMUM_SYMMETRY_ENDPOINT_DIFFERENCE,
            "threshold": "maximum certified modulus endpoint difference <= 1e-12",
            "value": float(maximum_symmetry_difference),
        },
        "finite_strict_json": {
            "passed": finite_and_json,
            "threshold": "all numeric summaries finite and strict JSON serializable",
            "value": finite_and_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    hypothesis_gates = {
        "selected_spectrum_strictly_stable": {
            "passed": selected_maximum < 1,
            "threshold": "rational selected spectral-radius upper bound < 1",
            "value": float(selected_maximum),
        },
        "excluded_spectrum_invertible": {
            "passed": excluded_minimum > 0,
            "threshold": "rational excluded minimum-modulus lower bound > 0",
            "value": float(excluded_minimum),
        },
        "normal_gap_positive": {
            "passed": normal_gap > 0,
            "threshold": "selected minimum lower - excluded maximum upper > 0",
            "value": float(normal_gap),
        },
        "degree_90_tail": {
            "passed": tail_ratio < 1,
            "threshold": "rho_selected_upper^90 / mu_excluded_lower < 1",
            "value": float(tail_ratio),
        },
        "fixed_leaf_spectral_count": {
            "passed": bool(
                len(selected_intervals) == EXPECTED_SELECTED_COUNT
                and len(excluded_intervals) == EXPECTED_EXCLUDED_COUNT
                and len(selected_intervals) + len(excluded_intervals)
                == EXPECTED_FIXED_LEAF_COUNT
                and all(
                    proof.selected_group_gap is not None
                    and proof.selected_group_gap > 0
                    for proof in selected_proofs
                )
            ),
            "threshold": "disc-separated counts equal 24 selected and 2574 excluded",
            "value": {
                "selected": len(selected_intervals),
                "excluded": len(excluded_intervals),
                "fixed_leaf": len(selected_intervals) + len(excluded_intervals),
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered rational-interval audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = "registered linear spectral split and degree-90 tail certified"
    else:
        outcome = "not_certified"
        classification = "registered rational-interval linear certification failed"

    return {
        "question": (
            "Can the 17x17 fixed-leaf linear spectral split, excluded "
            "invertibility, normal gap, and degree-90 tail be certified by "
            "rational interval bounds?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "selected_waves": [list(wave) for wave in sorted(SELECTED_WAVES)],
            "tail_degree": TAIL_DEGREE,
        },
        "q007g_input": q007g_record,
        "interval_construction": interval_construction,
        "eigencertification": eigencertification,
        "global_bounds": global_bounds,
        "symmetry": symmetry,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "claim_boundary": (
            "This certifies only the linear layer of the fixed 17x17 filtered "
            "map. It does not certify degrees 2--89 nonresonance, a Riesz "
            "projector norm, a nonlinear proof radius, manifold existence or "
            "uniqueness, or grid-uniform attraction."
        ),
        "preserved_prior_outcomes": {
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
            "q007g_theorem_readiness_classification_changed": False,
        },
        "next_change": (
            "Q007i will separate direct full-spectrum from "
            "translation-equivariant external nonresonance at degrees 2--89."
        ),
    }
