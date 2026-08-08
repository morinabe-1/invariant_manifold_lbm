"""Sealed Q007ac phase-aware external-output resolvent refinement.

The Q007o selected-output inverse, Q007n zero-wave inverse, scalar majorants,
and 119-candidate radius grid are held fixed.  Only the nonzero nonselected
output resolvent is replaced by a complex-phase disc separation certificate.
"""

from __future__ import annotations

import argparse
import json
import math
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from math import comb
from pathlib import Path
from typing import Any

from research.q007n_explicit_local_radius import (
    CANDIDATE_EXPONENTS,
    MAJORANT_DECIMAL_DIGITS,
    MAXIMUM_CONTRACTION,
    _round_up,
)
from research.q007o_external_complement_radius import (
    _radius_scan,
    _working_coefficients_from_q007n,
)
from ttim_lbm.direct_nonresonance import (
    EXPECTED_AGGREGATE_COUNT,
    EXPECTED_DEGREE_COUNT,
    EXPECTED_EXPANDED_PRODUCT_COUNT,
    LOG_FINAL_DECIMAL_DIGITS,
    LOG_INTERNAL_DECIMAL_DIGITS,
    LOG_SERIES_TERMS,
    _ExternalDisk,
    _log_enclosures,
    _merge_external_logs,
    _rebuild_representative_proofs,
    _selected_types_and_external_disks,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _complex_point,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _modulus_disk_interval,
    _sqrt_bounds,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
REPRESENTATIVE_COUNT = 72
SELECTED_REPRESENTATIVE_COUNT = 2
NONSELECTED_REPRESENTATIVE_COUNT = 70
TARGET_DISC_COUNT = 630
SCREEN_LOG_GAP = Fraction(1, 10**6)
PHASE_GAP = Fraction(1, 10**7)
PHASE_THRESHOLD_OUTWARD_BINARY_BITS = 256
MINIMUM_TOTAL_IMPROVEMENT_FACTOR = Fraction(100)
LOG_SCALE = 10**LOG_FINAL_DECIMAL_DIGITS
SCREEN_SCALED = SCREEN_LOG_GAP * LOG_SCALE
if SCREEN_SCALED.denominator != 1:
    raise RuntimeError("registered screen gap is not on the Q007i log grid")
SCREEN_SCALED_INTEGER = int(SCREEN_SCALED)

SELECTED_REPRESENTATIVES = {
    "axis": {
        "wave_index": (-1, 0),
        "acoustic_indices": (0, 1),
        "shear_index": 4,
    },
    "diagonal": {
        "wave_index": (-1, -1),
        "acoustic_indices": (0, 1),
        "shear_index": 6,
    },
}

ARTIFACT_FILENAMES = {
    "q007h1": "q007h1_equivariant_spectrum.json",
    "q007i": "q007i_direct_nonresonance.json",
    "q007n": "q007n_explicit_local_radius.json",
    "q007o": "q007o_external_complement_radius.json",
}
REGISTERED_INPUT_SHA256 = {
    "q007h1": (
        "caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4"
    ),
    "q007i": (
        "c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f"
    ),
    "q007n": (
        "7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36"
    ),
    "q007o": (
        "36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd"
    ),
}
IMPLEMENTATION_SOURCE_PATHS = {
    "q007i": Path("src/ttim_lbm/direct_nonresonance.py"),
    "q007h1": Path("src/ttim_lbm/equivariant_spectrum.py"),
    "q007n": Path("research/q007n_explicit_local_radius.py"),
    "q007o": Path("research/q007o_external_complement_radius.py"),
}
REGISTERED_IMPLEMENTATION_SHA256 = {
    "q007i": (
        "22209c56184eff9556db13b553cb89644eea11ffd77a3af69d0316a747118294"
    ),
    "q007h1": (
        "d2d857c1b9ac20f88c9b1a1a44e59bd1d15dad043d5e96fde5069ea0c1865a94"
    ),
    "q007n": (
        "6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9"
    ),
    "q007o": (
        "d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7"
    ),
}

ComplexFraction = tuple[Fraction, Fraction]


@dataclass(frozen=True, slots=True)
class _DyadicComplex:
    real_numerator: int
    imaginary_numerator: int
    denominator_exponent: int


@dataclass(frozen=True, slots=True)
class _DyadicScalar:
    numerator: int
    denominator_exponent: int


@dataclass(frozen=True, slots=True)
class _NominalDisc:
    name: str
    center: ComplexFraction
    radius: Fraction
    original_center: ComplexFraction
    original_radius: Fraction


@dataclass(frozen=True, slots=True)
class _TargetDisc:
    identifier: str
    wave_index: tuple[int, int]
    eigenvalue_index: int
    center: ComplexFraction
    center_complex: complex
    radius: Fraction


@dataclass(frozen=True, slots=True)
class _DangerousAggregate:
    degree: int
    counts: tuple[int, int, int, int]
    merged_indices: tuple[int, ...]
    external_identifiers: tuple[str, ...]

    @property
    def expanded_product_count(self) -> int:
        return (self.counts[0] + 1) * (self.counts[2] + 1)

    @property
    def comparison_count(self) -> int:
        return self.expanded_product_count * len(self.external_identifiers)


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _canonical_json_sha256(value: Any) -> str:
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return sha256(serialized.encode("utf-8")).hexdigest()


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    current_source = source_metadata()
    for name, filename in ARTIFACT_FILENAMES.items():
        path = directory / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        scope = payload.get("mathematical_scope", {})
        scope_match = bool(
            scope.get("construction_grid") == [SIZE, SIZE]
            and float(scope.get("omega", math.nan)) == OMEGA
            and float(scope.get("eta", math.nan)) == ETA
        )
        observed = _file_sha256(path)
        record = {
            "filename": filename,
            "sha256": observed,
            "registered_sha256": REGISTERED_INPUT_SHA256[name],
            "sha256_matches": observed == REGISTERED_INPUT_SHA256[name],
            "source_match": payload.get("source") == current_source,
            "scope_match": scope_match,
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "all_validity_gates_passed": _all_gates_pass(
                payload, "validity_gates"
            ),
            "all_hypothesis_gates_passed": _all_gates_pass(
                payload, "hypothesis_gates"
            ),
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["source_match"]
            and record["scope_match"]
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == "accepted"
            and record["all_validity_gates_passed"]
            and record["all_hypothesis_gates_passed"]
        )
        payloads[name] = payload
        records[name] = record
    return payloads, records


def _implementation_source_audit() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    records = {}
    for name, relative in IMPLEMENTATION_SOURCE_PATHS.items():
        path = root / relative
        observed = _file_sha256(path)
        records[name] = {
            "path": relative.as_posix(),
            "sha256": observed,
            "registered_sha256": REGISTERED_IMPLEMENTATION_SHA256[name],
            "passed": observed == REGISTERED_IMPLEMENTATION_SHA256[name],
        }
    return {
        "records": records,
        "all_registered_implementation_sha256_match": all(
            record["passed"] for record in records.values()
        ),
    }


def _complex_fraction(value: complex) -> ComplexFraction:
    point = _complex_point(value)
    if point.real.width != 0 or point.imag.width != 0:
        raise RuntimeError("dyadic complex center is not a point")
    return point.real.lower, point.imag.lower


def _complex_conjugate(value: ComplexFraction) -> ComplexFraction:
    return value[0], -value[1]


def _complex_multiply(
    left: ComplexFraction,
    right: ComplexFraction,
) -> ComplexFraction:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _complex_squared_modulus(value: ComplexFraction) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def _complex_squared_distance(
    left: ComplexFraction,
    right: ComplexFraction,
) -> Fraction:
    return (left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2


def _complex_power_table(
    value: ComplexFraction,
    maximum_degree: int,
) -> tuple[ComplexFraction, ...]:
    output: list[ComplexFraction] = [(Fraction(1), Fraction(0))]
    for _ in range(maximum_degree):
        output.append(_complex_multiply(output[-1], value))
    return tuple(output)


def _power_of_two_exponent(value: int) -> int:
    if value <= 0 or value & (value - 1):
        raise ValueError("registered dyadic denominator is not a power of two")
    return value.bit_length() - 1


def _two_adic_valuation(value: int, maximum: int) -> int:
    if value == 0:
        return maximum
    absolute = abs(value)
    return min(maximum, (absolute & -absolute).bit_length() - 1)


def _normalize_dyadic_complex(
    real_numerator: int,
    imaginary_numerator: int,
    denominator_exponent: int,
) -> _DyadicComplex:
    if real_numerator == 0 and imaginary_numerator == 0:
        return _DyadicComplex(0, 0, 0)
    shift = min(
        _two_adic_valuation(real_numerator, denominator_exponent),
        _two_adic_valuation(imaginary_numerator, denominator_exponent),
    )
    return _DyadicComplex(
        real_numerator >> shift,
        imaginary_numerator >> shift,
        denominator_exponent - shift,
    )


def _dyadic_complex(value: ComplexFraction) -> _DyadicComplex:
    real_exponent = _power_of_two_exponent(value[0].denominator)
    imaginary_exponent = _power_of_two_exponent(value[1].denominator)
    exponent = max(real_exponent, imaginary_exponent)
    return _normalize_dyadic_complex(
        value[0].numerator << (exponent - real_exponent),
        value[1].numerator << (exponent - imaginary_exponent),
        exponent,
    )


def _dyadic_to_complex_fraction(value: _DyadicComplex) -> ComplexFraction:
    denominator = 1 << value.denominator_exponent
    return (
        Fraction(value.real_numerator, denominator),
        Fraction(value.imaginary_numerator, denominator),
    )


def _dyadic_multiply(
    left: _DyadicComplex,
    right: _DyadicComplex,
) -> _DyadicComplex:
    return _normalize_dyadic_complex(
        left.real_numerator * right.real_numerator
        - left.imaginary_numerator * right.imaginary_numerator,
        left.real_numerator * right.imaginary_numerator
        + left.imaginary_numerator * right.real_numerator,
        left.denominator_exponent + right.denominator_exponent,
    )


def _dyadic_power_table(
    value: _DyadicComplex,
    maximum_degree: int,
) -> tuple[_DyadicComplex, ...]:
    output = [_DyadicComplex(1, 0, 0)]
    for _ in range(maximum_degree):
        output.append(_dyadic_multiply(output[-1], value))
    return tuple(output)


def _dyadic_squared_distance(
    left: _DyadicComplex,
    right: _DyadicComplex,
) -> _DyadicScalar:
    exponent = max(
        left.denominator_exponent,
        right.denominator_exponent,
    )
    left_real = left.real_numerator << (
        exponent - left.denominator_exponent
    )
    left_imaginary = left.imaginary_numerator << (
        exponent - left.denominator_exponent
    )
    right_real = right.real_numerator << (
        exponent - right.denominator_exponent
    )
    right_imaginary = right.imaginary_numerator << (
        exponent - right.denominator_exponent
    )
    real_difference = left_real - right_real
    imaginary_difference = left_imaginary - right_imaginary
    numerator = real_difference**2 + imaginary_difference**2
    denominator_exponent = 2 * exponent
    shift = _two_adic_valuation(numerator, denominator_exponent)
    return _DyadicScalar(
        numerator >> shift,
        denominator_exponent - shift,
    )


def _dyadic_to_fraction(value: _DyadicScalar) -> Fraction:
    return Fraction(value.numerator, 1 << value.denominator_exponent)


def _normalize_dyadic_scalar(
    numerator: int,
    denominator_exponent: int,
) -> _DyadicScalar:
    if numerator == 0:
        return _DyadicScalar(0, 0)
    shift = _two_adic_valuation(numerator, denominator_exponent)
    return _DyadicScalar(
        numerator >> shift,
        denominator_exponent - shift,
    )


def _round_fraction_up_to_dyadic(
    value: Fraction,
    binary_bits: int,
) -> _DyadicScalar:
    scaled_numerator = value.numerator << binary_bits
    quotient, remainder = divmod(scaled_numerator, value.denominator)
    if remainder:
        quotient += 1
    return _normalize_dyadic_scalar(quotient, binary_bits)


def _square_dyadic(value: _DyadicScalar) -> _DyadicScalar:
    return _normalize_dyadic_scalar(
        value.numerator * value.numerator,
        2 * value.denominator_exponent,
    )


def _subtract_dyadic(
    left: _DyadicScalar,
    right: _DyadicScalar,
) -> _DyadicScalar:
    exponent = max(left.denominator_exponent, right.denominator_exponent)
    numerator = (
        left.numerator << (exponent - left.denominator_exponent)
    ) - (right.numerator << (exponent - right.denominator_exponent))
    return _normalize_dyadic_scalar(numerator, exponent)


def _dyadic_less(left: _DyadicScalar, right: _DyadicScalar) -> bool:
    exponent = max(left.denominator_exponent, right.denominator_exponent)
    return (
        left.numerator << (exponent - left.denominator_exponent)
    ) < (right.numerator << (exponent - right.denominator_exponent))


def _complex_fraction_record(value: ComplexFraction) -> dict[str, Any]:
    return {
        "real": _fraction_record(value[0]),
        "imaginary": _fraction_record(value[1]),
    }


def _distance_upper(left: ComplexFraction, right: ComplexFraction) -> Fraction:
    return _sqrt_bounds(_complex_squared_distance(left, right)).upper


def _modulus_upper(value: ComplexFraction) -> Fraction:
    return _sqrt_bounds(_complex_squared_modulus(value)).upper


def _nominal_selected_discs(
    representatives: tuple[Any, ...],
    selected_radius_upper: Fraction,
) -> tuple[dict[str, _NominalDisc], dict[str, Any], bool]:
    by_wave = {proof.wave_index: proof for proof in representatives}
    discs: dict[str, _NominalDisc] = {}
    records = []
    indices_match = True
    all_contained = True
    all_within_radius = True
    for family, registration in SELECTED_REPRESENTATIVES.items():
        proof = by_wave[registration["wave_index"]]
        acoustic_indices = registration["acoustic_indices"]
        shear_index = registration["shear_index"]
        expected_indices = {*acoustic_indices, shear_index}
        indices_match = indices_match and set(proof.selected_indices) == expected_indices

        positive_original = _complex_fraction(
            proof.eigenvalues[acoustic_indices[0]]
        )
        negative_original = _complex_fraction(
            proof.eigenvalues[acoustic_indices[1]]
        )
        shear_original = _complex_fraction(proof.eigenvalues[shear_index])
        positive_nominal = positive_original
        negative_nominal = _complex_conjugate(positive_original)
        shear_nominal = (shear_original[0], Fraction(0))
        acoustic_mismatch = _distance_upper(
            negative_original, negative_nominal
        )
        shear_mismatch = _distance_upper(shear_original, shear_nominal)
        acoustic_radius = proof.radius + acoustic_mismatch
        shear_radius = proof.radius + shear_mismatch

        family_discs = {
            f"{family}_acoustic_positive": _NominalDisc(
                name=f"{family}_acoustic_positive",
                center=positive_nominal,
                radius=acoustic_radius,
                original_center=positive_original,
                original_radius=proof.radius,
            ),
            f"{family}_acoustic_negative": _NominalDisc(
                name=f"{family}_acoustic_negative",
                center=negative_nominal,
                radius=acoustic_radius,
                original_center=negative_original,
                original_radius=proof.radius,
            ),
            f"{family}_shear": _NominalDisc(
                name=f"{family}_shear",
                center=shear_nominal,
                radius=shear_radius,
                original_center=shear_original,
                original_radius=proof.radius,
            ),
        }
        discs.update(family_discs)
        acoustic_contained = bool(
            _distance_upper(positive_original, positive_nominal)
            + proof.radius
            <= acoustic_radius
            and _distance_upper(negative_original, negative_nominal)
            + proof.radius
            <= acoustic_radius
        )
        shear_contained = bool(
            _distance_upper(shear_original, shear_nominal) + proof.radius
            <= shear_radius
        )
        within = all(
            _modulus_upper(disc.center) + disc.radius <= selected_radius_upper
            for disc in family_discs.values()
        )
        all_contained = all_contained and acoustic_contained and shear_contained
        all_within_radius = all_within_radius and within
        records.append(
            {
                "family": family,
                "wave_index": list(proof.wave_index),
                "selected_indices": list(proof.selected_indices),
                "registered_acoustic_indices": list(acoustic_indices),
                "registered_shear_index": shear_index,
                "proof_digest_matches": proof.digest_matches,
                "bauer_fike_radius": _fraction_record(proof.radius),
                "acoustic_center_mismatch_upper": _fraction_record(
                    acoustic_mismatch
                ),
                "shear_center_mismatch_upper": _fraction_record(
                    shear_mismatch
                ),
                "acoustic_nominal_radius": _fraction_record(acoustic_radius),
                "shear_nominal_radius": _fraction_record(shear_radius),
                "original_discs_contained": acoustic_contained
                and shear_contained,
                "nominal_discs_within_working_spectral_radius": within,
            }
        )
    coverage_passed = bool(
        indices_match
        and all_contained
        and all_within_radius
        and all(proof.digest_matches for proof in representatives)
    )
    return discs, {
        "representative_records": records,
        "nominal_discs": {
            name: {
                "center": _complex_fraction_record(disc.center),
                "radius": _fraction_record(disc.radius),
            }
            for name, disc in discs.items()
        },
        "selected_index_registration_matches": indices_match,
        "all_original_selected_discs_contained": all_contained,
        "all_nominal_discs_within_working_spectral_radius": all_within_radius,
        "c4_selected_mode_coverage": 24,
    }, coverage_passed


def _target_external_discs(
    representatives: tuple[Any, ...],
) -> tuple[tuple[_TargetDisc, ...], dict[str, Any], bool]:
    targets = []
    representative_records = []
    for proof in representatives:
        if proof.selected_indices:
            continue
        identifiers = []
        for index, eigenvalue in enumerate(proof.eigenvalues):
            identifier = (
                f"wave={proof.wave_index[0]},{proof.wave_index[1]};"
                f"eigenvalue_index={index}"
            )
            identifiers.append(identifier)
            targets.append(
                _TargetDisc(
                    identifier=identifier,
                    wave_index=proof.wave_index,
                    eigenvalue_index=index,
                    center=_complex_fraction(eigenvalue),
                    center_complex=complex(eigenvalue),
                    radius=proof.radius,
                )
            )
        representative_records.append(
            {
                "wave_index": list(proof.wave_index),
                "disc_count": len(identifiers),
                "proof_digest_matches": proof.digest_matches,
                "first_identifier": identifiers[0],
                "last_identifier": identifiers[-1],
            }
        )
    passed = bool(
        len(representative_records) == NONSELECTED_REPRESENTATIVE_COUNT
        and len(targets) == TARGET_DISC_COUNT
        and all(record["proof_digest_matches"] for record in representative_records)
    )
    return tuple(targets), {
        "nonselected_representative_count": len(representative_records),
        "target_disc_count": len(targets),
        "selected_output_complement_excluded": True,
        "zero_wave_excluded": True,
        "fourier_wave_sum_restriction_used": False,
        "representative_records": representative_records,
    }, passed


def _target_log_inputs(
    targets: tuple[_TargetDisc, ...],
) -> tuple[_ExternalDisk, ...]:
    return tuple(
        _ExternalDisk(
            interval=_modulus_disk_interval(target.center_complex, target.radius),
            identifier=target.identifier,
        )
        for target in targets
    )


def _screen_aggregates(
    selected_logs: tuple[Any, ...],
    merged_external: tuple[Any, ...],
) -> tuple[
    tuple[_DangerousAggregate, ...],
    dict[str, Any],
    bool,
]:
    starts = [interval.lower for interval in merged_external]
    ends = [interval.upper for interval in merged_external]
    dangerous: list[_DangerousAggregate] = []
    degree_records = []
    total_aggregates = 0
    total_expanded = 0
    dangerous_expanded = 0
    comparison_count = 0
    minimum_safe_gap: int | None = None

    for degree in range(2, 90):
        degree_aggregate_count = 0
        degree_expanded_count = 0
        degree_dangerous_count = 0
        degree_dangerous_expanded = 0
        degree_comparison_count = 0
        for axis_acoustic in range(degree + 1):
            for axis_shear in range(degree - axis_acoustic + 1):
                for diagonal_acoustic in range(
                    degree - axis_acoustic - axis_shear + 1
                ):
                    diagonal_shear = (
                        degree
                        - axis_acoustic
                        - axis_shear
                        - diagonal_acoustic
                    )
                    counts = (
                        axis_acoustic,
                        axis_shear,
                        diagonal_acoustic,
                        diagonal_shear,
                    )
                    lower = sum(
                        count * interval.lower
                        for count, interval in zip(
                            counts, selected_logs, strict=True
                        )
                    )
                    upper = sum(
                        count * interval.upper
                        for count, interval in zip(
                            counts, selected_logs, strict=True
                        )
                    )
                    expanded = (axis_acoustic + 1) * (
                        diagonal_acoustic + 1
                    )
                    left = bisect_right(
                        ends, lower - SCREEN_SCALED_INTEGER
                    )
                    right = bisect_left(
                        starts, upper + SCREEN_SCALED_INTEGER
                    )
                    nearby_indices = tuple(range(left, right))
                    if nearby_indices:
                        identifiers = tuple(
                            sorted(
                                {
                                    identifier
                                    for index in nearby_indices
                                    for identifier in merged_external[
                                        index
                                    ].identifiers
                                }
                            )
                        )
                        record = _DangerousAggregate(
                            degree=degree,
                            counts=counts,
                            merged_indices=nearby_indices,
                            external_identifiers=identifiers,
                        )
                        dangerous.append(record)
                        degree_dangerous_count += 1
                        degree_dangerous_expanded += expanded
                        degree_comparison_count += record.comparison_count
                    else:
                        insertion = bisect_right(starts, upper)
                        gaps = []
                        if insertion:
                            gaps.append(
                                lower - merged_external[insertion - 1].upper
                            )
                        if insertion < len(merged_external):
                            gaps.append(
                                merged_external[insertion].lower - upper
                            )
                        if not gaps:
                            raise RuntimeError(
                                "screen aggregate has no external neighbor"
                            )
                        gap = min(gaps)
                        minimum_safe_gap = (
                            gap
                            if minimum_safe_gap is None
                            else min(minimum_safe_gap, gap)
                        )
                    degree_aggregate_count += 1
                    degree_expanded_count += expanded
        expected_aggregates = comb(degree + 3, 3)
        expected_expanded = comb(degree + 5, 5)
        degree_records.append(
            {
                "degree": degree,
                "aggregate_count": degree_aggregate_count,
                "expected_aggregate_count": expected_aggregates,
                "expanded_product_count": degree_expanded_count,
                "expected_expanded_product_count": expected_expanded,
                "dangerous_aggregate_count": degree_dangerous_count,
                "dangerous_expanded_product_count": degree_dangerous_expanded,
                "phase_comparison_count": degree_comparison_count,
                "count_checks_passed": bool(
                    degree_aggregate_count == expected_aggregates
                    and degree_expanded_count == expected_expanded
                ),
            }
        )
        total_aggregates += degree_aggregate_count
        total_expanded += degree_expanded_count
        dangerous_expanded += degree_dangerous_expanded
        comparison_count += degree_comparison_count

    dangerous_records = [
        {
            "degree": record.degree,
            "counts": list(record.counts),
            "nearby_merged_external_indices": list(record.merged_indices),
            "external_identifiers": list(record.external_identifiers),
            "expanded_product_count": record.expanded_product_count,
            "phase_comparison_count": record.comparison_count,
        }
        for record in dangerous
    ]
    counts_passed = bool(
        len(degree_records) == EXPECTED_DEGREE_COUNT
        and total_aggregates == EXPECTED_AGGREGATE_COUNT
        and total_expanded == EXPECTED_EXPANDED_PRODUCT_COUNT
        and all(record["count_checks_passed"] for record in degree_records)
        and dangerous_expanded
        == sum(record.expanded_product_count for record in dangerous)
        and comparison_count
        == sum(record.comparison_count for record in dangerous)
        and minimum_safe_gap is not None
        and minimum_safe_gap >= SCREEN_SCALED_INTEGER
    )
    return tuple(dangerous), {
        "degree_count": len(degree_records),
        "aggregate_count": total_aggregates,
        "expanded_product_count": total_expanded,
        "safe_aggregate_count": total_aggregates - len(dangerous),
        "dangerous_aggregate_count": len(dangerous),
        "dangerous_expanded_product_count": dangerous_expanded,
        "phase_comparison_count": comparison_count,
        "minimum_safe_log_gap": _fraction_record(
            Fraction(minimum_safe_gap or 0, LOG_SCALE)
        ),
        "degree_records": degree_records,
        "dangerous_records": dangerous_records,
        "counts_and_partition_passed": counts_passed,
    }, counts_passed


def _phase_certificate(
    dangerous: tuple[_DangerousAggregate, ...],
    nominal: dict[str, _NominalDisc],
    targets: tuple[_TargetDisc, ...],
    product_factor_modulus_upper: Fraction,
) -> tuple[dict[str, Any], bool]:
    target_lookup = {target.identifier: target for target in targets}
    dyadic_targets = {
        target.identifier: _dyadic_complex(target.center)
        for target in targets
    }
    maximum_degree = 89
    dyadic_nominal = {
        name: _dyadic_complex(disc.center) for name, disc in nominal.items()
    }
    powers = {
        name: _dyadic_power_table(value, maximum_degree)
        for name, value in dyadic_nominal.items()
    }
    acoustic_products = {
        "axis": tuple(
            tuple(
                _dyadic_multiply(
                    powers["axis_acoustic_positive"][positive],
                    powers["axis_acoustic_negative"][total - positive],
                )
                for positive in range(total + 1)
            )
            for total in range(maximum_degree + 1)
        ),
        "diagonal": tuple(
            tuple(
                _dyadic_multiply(
                    powers["diagonal_acoustic_positive"][positive],
                    powers["diagonal_acoustic_negative"][total - positive],
                )
                for positive in range(total + 1)
            )
            for total in range(maximum_degree + 1)
        ),
    }
    digest = sha256()
    digest.update(
        _canonical_json_sha256(
            [
                {
                    "degree": aggregate.degree,
                    "counts": list(aggregate.counts),
                    "external_identifiers": list(
                        aggregate.external_identifiers
                    ),
                }
                for aggregate in dangerous
            ]
        ).encode("ascii")
    )
    digest.update(b"\0")
    comparison_count = 0
    expanded_count = 0
    failed_count = 0
    minimum_margin: _DyadicScalar | None = None
    minimum_context: dict[str, Any] | None = None
    maximum_product_uncertainty = Fraction(0)
    maximum_threshold_rounding_increment = Fraction(0)

    for aggregate in dangerous:
        aa, axis_shear, da, diagonal_shear = aggregate.counts
        uncertainty = product_factor_modulus_upper ** (aggregate.degree - 1) * (
            aa * nominal["axis_acoustic_positive"].radius
            + axis_shear * nominal["axis_shear"].radius
            + da * nominal["diagonal_acoustic_positive"].radius
            + diagonal_shear * nominal["diagonal_shear"].radius
        )
        maximum_product_uncertainty = max(
            maximum_product_uncertainty, uncertainty
        )
        thresholds = {}
        for identifier in aggregate.external_identifiers:
            exact_threshold = (
                PHASE_GAP
                + uncertainty
                + target_lookup[identifier].radius
            )
            working_threshold = _round_fraction_up_to_dyadic(
                exact_threshold, PHASE_THRESHOLD_OUTWARD_BINARY_BITS
            )
            working_threshold_fraction = _dyadic_to_fraction(
                working_threshold
            )
            maximum_threshold_rounding_increment = max(
                maximum_threshold_rounding_increment,
                working_threshold_fraction - exact_threshold,
            )
            thresholds[identifier] = (
                exact_threshold**2,
                _square_dyadic(working_threshold),
            )
        shear_product = _dyadic_multiply(
            powers["axis_shear"][axis_shear],
            powers["diagonal_shear"][diagonal_shear],
        )
        for axis_positive in range(aa + 1):
            axis_negative = aa - axis_positive
            axis_product = acoustic_products["axis"][aa][axis_positive]
            for diagonal_positive in range(da + 1):
                diagonal_negative = da - diagonal_positive
                diagonal_product = acoustic_products["diagonal"][da][
                    diagonal_positive
                ]
                center = _dyadic_multiply(
                    shear_product,
                    _dyadic_multiply(axis_product, diagonal_product),
                )
                expanded_count += 1
                for identifier in aggregate.external_identifiers:
                    target = target_lookup[identifier]
                    distance_squared = _dyadic_squared_distance(
                        center, dyadic_targets[identifier]
                    )
                    (
                        exact_threshold_squared,
                        working_threshold_squared,
                    ) = thresholds[identifier]
                    margin = _subtract_dyadic(
                        distance_squared, working_threshold_squared
                    )
                    passed = margin.numerator > 0
                    comparison_count += 1
                    if not passed:
                        failed_count += 1
                    digest.update(b"\x01" if passed else b"\x00")
                    if minimum_margin is None or _dyadic_less(
                        margin, minimum_margin
                    ):
                        minimum_margin = margin
                        minimum_context = {
                            "degree": aggregate.degree,
                            "counts": list(aggregate.counts),
                            "axis_acoustic_positive_count": axis_positive,
                            "axis_acoustic_negative_count": axis_negative,
                            "diagonal_acoustic_positive_count": (
                                diagonal_positive
                            ),
                            "diagonal_acoustic_negative_count": (
                                diagonal_negative
                            ),
                            "external_identifier": identifier,
                            "_center": center,
                            "_external_center": target.center,
                            "_uncertainty": uncertainty,
                            "_external_radius": target.radius,
                            "_distance_squared": distance_squared,
                            "_exact_threshold_squared": (
                                exact_threshold_squared
                            ),
                            "_working_threshold_squared": (
                                working_threshold_squared
                            ),
                        }

    expected_expanded = sum(
        aggregate.expanded_product_count for aggregate in dangerous
    )
    expected_comparisons = sum(
        aggregate.comparison_count for aggregate in dangerous
    )
    complete = bool(
        expanded_count == expected_expanded
        and comparison_count == expected_comparisons
        and minimum_margin is not None
        and minimum_context is not None
    )
    passed = bool(complete and failed_count == 0 and minimum_margin.numerator > 0)
    minimum_witness = None
    minimum_margin_fraction = Fraction(0)
    if minimum_context is not None and minimum_margin is not None:
        minimum_margin_fraction = _dyadic_to_fraction(minimum_margin)
        distance_squared_fraction = _dyadic_to_fraction(
            minimum_context["_distance_squared"]
        )
        certified_distance_lower = (
            _sqrt_bounds(distance_squared_fraction).lower
            - minimum_context["_uncertainty"]
            - minimum_context["_external_radius"]
        )
        minimum_witness = {
            key: value
            for key, value in minimum_context.items()
            if not key.startswith("_")
        }
        minimum_witness.update(
            {
                "nominal_product_center": _complex_fraction_record(
                    _dyadic_to_complex_fraction(minimum_context["_center"])
                ),
                "external_center": _complex_fraction_record(
                    minimum_context["_external_center"]
                ),
                "product_uncertainty_upper": _fraction_record(
                    minimum_context["_uncertainty"]
                ),
                "external_radius": _fraction_record(
                    minimum_context["_external_radius"]
                ),
                "distance_squared": _fraction_record(
                    distance_squared_fraction
                ),
                "exact_threshold_squared": _fraction_record(
                    minimum_context["_exact_threshold_squared"]
                ),
                "working_outward_dyadic_threshold_squared": _fraction_record(
                    _dyadic_to_fraction(
                        minimum_context["_working_threshold_squared"]
                    )
                ),
                "squared_margin": _fraction_record(minimum_margin_fraction),
                "certified_complex_distance_lower": _fraction_record(
                    certified_distance_lower
                ),
            }
        )
    return {
        "target_phase_gap": _fraction_record(PHASE_GAP),
        "product_factor_modulus_upper": _fraction_record(
            product_factor_modulus_upper
        ),
        "dangerous_aggregate_count": len(dangerous),
        "expanded_product_count": expanded_count,
        "expected_expanded_product_count": expected_expanded,
        "comparison_count": comparison_count,
        "expected_comparison_count": expected_comparisons,
        "failed_comparison_count": failed_count,
        "maximum_product_uncertainty_upper": _fraction_record(
            maximum_product_uncertainty
        ),
        "threshold_outward_binary_bits": (
            PHASE_THRESHOLD_OUTWARD_BINARY_BITS
        ),
        "maximum_threshold_rounding_increment": _fraction_record(
            maximum_threshold_rounding_increment
        ),
        "minimum_squared_margin": _fraction_record(
            minimum_margin_fraction
        ),
        "minimum_margin_witness": minimum_witness,
        "comparison_digest_sha256": digest.hexdigest(),
        "complete": complete,
        "all_phase_comparisons_strict": passed,
    }, passed


def run_phase_aware_resolvent_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    implementation_audit = _implementation_source_audit()
    q007h1 = payloads["q007h1"]
    q007n_cycle = payloads["q007n"]["cycle"]
    q007o_cycle = payloads["q007o"]["cycle"]
    q007n_spectral = q007n_cycle["spectral_separation_and_inverse"]
    q007o_refinement = q007o_cycle[
        "external_complement_inverse_refinement"
    ]

    representatives, reconstruction = _rebuild_representative_proofs(q007h1)
    selected_radius_upper = _fraction_from_record(
        q007n_spectral["working_selected_spectral_radius_upper"]
    )
    nominal, nominal_audit, nominal_passed = _nominal_selected_discs(
        representatives, selected_radius_upper
    )
    nominal_product_radius_upper = max(
        selected_radius_upper,
        *(
            _modulus_upper(disc.center) + disc.radius
            for disc in nominal.values()
        ),
    )
    nominal_audit["working_product_factor_modulus_upper"] = _fraction_record(
        nominal_product_radius_upper
    )
    nominal_audit["working_product_factor_modulus_inflation_over_q007n"] = (
        _fraction_record(nominal_product_radius_upper - selected_radius_upper)
    )
    targets, target_audit, target_passed = _target_external_discs(
        representatives
    )
    selected_types, _unused_external, _classification_internal = (
        _selected_types_and_external_disks(representatives)
    )
    target_log_inputs = _target_log_inputs(targets)
    selected_logs, external_logs, logarithms_internal = _log_enclosures(
        selected_types, target_log_inputs
    )
    merged_external = _merge_external_logs(external_logs)
    dangerous, screen_audit, screen_passed = _screen_aggregates(
        selected_logs, merged_external
    )
    phase_audit, phase_passed = _phase_certificate(
        dangerous, nominal, targets, nominal_product_radius_upper
    )

    finite_modulus_floor = _fraction_from_record(
        q007n_spectral["finite_degree_minimum_modulus"]
    )
    safe_absolute_gap = finite_modulus_floor * SCREEN_LOG_GAP
    tail_gap = _fraction_from_record(
        q007n_spectral["degree_90_tail_absolute_gap_lower"]
    )
    beta_maximum = _fraction_from_record(
        q007n_spectral["working_maximum_beta_upper"]
    )
    raw_external_inverse = 81 * beta_maximum / PHASE_GAP
    working_external_inverse = _round_up(
        raw_external_inverse, MAJORANT_DECIMAL_DIGITS
    )
    internal_inverse = _fraction_from_record(
        q007o_refinement["working_internal_pair_inverse_upper"]
    )
    zero_inverse = _fraction_from_record(
        q007n_spectral["zero_wave_fixed_leaf_inverse_upper"]
    )
    old_total_inverse = _fraction_from_record(
        q007o_refinement["working_total_pair_inverse_upper"]
    )
    raw_total_inverse = max(
        working_external_inverse, internal_inverse, zero_inverse
    )
    working_total_inverse = _round_up(
        raw_total_inverse, MAJORANT_DECIMAL_DIGITS
    )
    total_improvement_factor = old_total_inverse / working_total_inverse

    coefficients = _working_coefficients_from_q007n(q007n_cycle)
    old_scan, _old_exact = _radius_scan(
        coefficients, selected_radius_upper, old_total_inverse
    )
    stored_old_scan = q007o_cycle["radius_comparison"][
        "refined_radius_search"
    ]
    old_records_reproduced = old_scan["records"] == stored_old_scan["records"]
    new_scan, new_exact = _radius_scan(
        coefficients, selected_radius_upper, working_total_inverse
    )
    old_selected = stored_old_scan["selected_candidate"]
    new_selected = new_scan["selected_candidate"]
    previous = new_scan["previous_larger_candidate"]
    old_exponent = int(old_selected["candidate_exponent"])
    old_exact_index = old_exponent - CANDIDATE_EXPONENTS[0]
    old_radius_still_passes = bool(new_exact[old_exact_index]["passed"])
    radius_strictly_improved = bool(
        new_selected is not None
        and int(new_selected["candidate_exponent"]) < old_exponent
    )
    new_boundary_passed = bool(
        new_selected is not None
        and new_selected["passed"]
        and new_selected["density_buffer_positive"]
        and new_selected["reduced_range_buffer_positive"]
        and new_selected["contraction_strictly_below_one_half"]
        and new_selected["radii_inequality_strict"]
        and (previous is None or not previous["passed"])
    )

    logarithms = {
        key: value
        for key, value in logarithms_internal.items()
        if not key.endswith("_exact")
    }
    merged_records = [
        {
            "merged_index": index,
            "lower_scaled_integer": str(interval.lower),
            "upper_scaled_integer": str(interval.upper),
            "source_disc_count": len(interval.identifiers),
            "identifiers": list(interval.identifiers),
        }
        for index, interval in enumerate(merged_external)
    ]
    separation_audit = {
        "log_series_terms": LOG_SERIES_TERMS,
        "log_internal_decimal_digits": LOG_INTERNAL_DECIMAL_DIGITS,
        "log_final_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
        "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
        "phase_gap": _fraction_record(PHASE_GAP),
        "finite_modulus_floor_reused_from_q007n": _fraction_record(
            finite_modulus_floor
        ),
        "safe_absolute_gap_lower": _fraction_record(safe_absolute_gap),
        "degree_90_tail_gap_reused_from_q007n": _fraction_record(tail_gap),
        "safe_screen_exceeds_phase_gap": safe_absolute_gap > PHASE_GAP,
        "tail_exceeds_phase_gap": tail_gap > PHASE_GAP,
        "selected_log_records": logarithms["selected_type_records"],
        "target_external_log_digest_sha256": logarithms[
            "external_disk_log_digest_sha256"
        ],
        "merged_external_interval_count": len(merged_external),
        "merged_external_intervals": merged_records,
        "screen": screen_audit,
        "phase": phase_audit,
    }
    inverse_audit = {
        "norm_formula": "81 * beta_maximum / phase_gap",
        "q007n_working_beta_maximum": _fraction_record(beta_maximum),
        "raw_phase_aware_external_inverse_upper": _fraction_record(
            raw_external_inverse
        ),
        "working_phase_aware_external_inverse_upper": _fraction_record(
            working_external_inverse
        ),
        "q007o_working_internal_pair_inverse_upper": _fraction_record(
            internal_inverse
        ),
        "q007n_zero_wave_inverse_upper": _fraction_record(zero_inverse),
        "raw_new_total_pair_inverse_upper": _fraction_record(
            raw_total_inverse
        ),
        "working_new_total_pair_inverse_upper": _fraction_record(
            working_total_inverse
        ),
        "q007o_working_total_pair_inverse_upper": _fraction_record(
            old_total_inverse
        ),
        "total_inverse_improvement_factor": _fraction_record(
            total_improvement_factor
        ),
        "new_total_is_internal_limited": (
            working_total_inverse == internal_inverse
        ),
        "only_external_output_inverse_changed": True,
    }
    radius_comparison = {
        "q007o_old_candidate_records_reproduced_exactly": (
            old_records_reproduced
        ),
        "q007o_selected_candidate_exponent": old_exponent,
        "q007o_selected_modal_radius_decimal": old_selected[
            "modal_radius_decimal"
        ],
        "q007o_candidate_passes_with_phase_inverse": old_radius_still_passes,
        "phase_refined_radius_search": new_scan,
    }

    input_digest = _canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "implementation_source_audit": implementation_audit,
            "registered_parameters": {
                "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
                "phase_gap": _fraction_record(PHASE_GAP),
                "phase_threshold_outward_binary_bits": (
                    PHASE_THRESHOLD_OUTWARD_BINARY_BITS
                ),
                "target_disc_count": TARGET_DISC_COUNT,
                "candidate_exponents": list(CANDIDATE_EXPONENTS),
            },
        }
    )
    result_digest = _canonical_json_sha256(
        {
            "nominal_selected_disc_audit": nominal_audit,
            "target_external_disc_audit": target_audit,
            "separation_summary": {
                "target_external_log_digest_sha256": separation_audit[
                    "target_external_log_digest_sha256"
                ],
                "screen": {
                    key: value
                    for key, value in screen_audit.items()
                    if key not in {"degree_records", "dangerous_records"}
                },
                "phase": phase_audit,
            },
            "inverse_refinement": inverse_audit,
            "radius_comparison": radius_comparison,
        }
    )

    serializable_sections = {
        "input_artifacts": input_records,
        "implementation_source_audit": implementation_audit,
        "spectral_reconstruction": reconstruction,
        "nominal_selected_disc_audit": nominal_audit,
        "target_external_disc_audit": target_audit,
        "phase_aware_separation_audit": separation_audit,
        "inverse_refinement": inverse_audit,
        "radius_comparison": radius_comparison,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    input_passed = bool(
        all(record["passed"] for record in input_records.values())
        and implementation_audit[
            "all_registered_implementation_sha256_match"
        ]
    )
    reconstruction_passed = bool(
        reconstruction["representative_count"] == REPRESENTATIVE_COUNT
        and reconstruction["proof_digest_mismatch_count"] == 0
        and nominal_passed
        and target_passed
    )
    screen_floor_passed = bool(
        screen_passed
        and safe_absolute_gap > PHASE_GAP
        and screen_audit["aggregate_count"] == EXPECTED_AGGREGATE_COUNT
    )
    phase_execution_passed = bool(
        phase_audit["complete"] and tail_gap > PHASE_GAP
    )
    reuse_passed = bool(
        old_records_reproduced
        and q007n_cycle["radius_search"]["candidate_exponents"]
        == list(CANDIDATE_EXPONENTS)
        and q007o_cycle["q007n_reuse_audit"]["only_pair_inverse_changed_in_new_scan"]
        and working_total_inverse == max(
            working_external_inverse, internal_inverse, zero_inverse
        )
    )
    validity_gates = {
        "registered_inputs_and_implementation": {
            "passed": input_passed,
            "threshold": (
                "four artifact SHA/source/scope/sealed outcomes and four "
                "implementation SHA values match"
            ),
            "value": input_passed,
        },
        "spectral_disc_reconstruction": {
            "passed": reconstruction_passed,
            "threshold": (
                "72 proof digests, registered selected discs, 70 "
                "nonselected representatives, and 630 target discs match"
            ),
            "value": {
                "representative_count": reconstruction[
                    "representative_count"
                ],
                "proof_digest_mismatch_count": reconstruction[
                    "proof_digest_mismatch_count"
                ],
                "target_disc_count": target_audit["target_disc_count"],
            },
        },
        "complete_modulus_screen": {
            "passed": screen_floor_passed,
            "threshold": (
                "2,919,730 aggregates partitioned and m_* 1e-6 > 1e-7"
            ),
            "value": {
                "aggregate_count": screen_audit["aggregate_count"],
                "dangerous_aggregate_count": screen_audit[
                    "dangerous_aggregate_count"
                ],
                "safe_absolute_gap": float(safe_absolute_gap),
            },
        },
        "complete_phase_expansion_and_tail": {
            "passed": phase_execution_passed,
            "threshold": (
                "all dangerous splits and nearby target discs compared; "
                "degree-90 tail >1e-7"
            ),
            "value": {
                "expanded_product_count": phase_audit[
                    "expanded_product_count"
                ],
                "comparison_count": phase_audit["comparison_count"],
                "tail_gap": float(tail_gap),
            },
        },
        "q007o_majorant_and_candidate_reuse": {
            "passed": reuse_passed,
            "threshold": (
                "Q007o records, internal/zero bounds, majorants, and 119 "
                "candidates are unchanged"
            ),
            "value": reuse_passed,
        },
        "finite_strict_json_and_digests": {
            "passed": finite_strict_json,
            "threshold": "finite strict JSON with input/phase/result digests",
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest,
                "phase_certificate_digest_sha256": phase_audit[
                    "comparison_digest_sha256"
                ],
                "result_digest_sha256": result_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    external_no_longer_limits = working_external_inverse < internal_inverse
    improvement_passed = (
        total_improvement_factor >= MINIMUM_TOTAL_IMPROVEMENT_FACTOR
    )
    hypothesis_gates = {
        "registered_phase_gap_certified": {
            "passed": bool(phase_passed and tail_gap > PHASE_GAP),
            "threshold": (
                "every screened finite-degree pair and the degree-90 tail "
                "strictly exceed 1e-7"
            ),
            "value": {
                "failed_comparison_count": phase_audit[
                    "failed_comparison_count"
                ],
                "minimum_squared_margin": phase_audit[
                    "minimum_squared_margin"
                ]["float"],
            },
        },
        "external_output_no_longer_limits": {
            "passed": external_no_longer_limits,
            "threshold": "phase-aware external inverse < Q007o internal inverse",
            "value": {
                "external": float(working_external_inverse),
                "internal": float(internal_inverse),
            },
        },
        "total_inverse_improves_by_one_hundred": {
            "passed": improvement_passed,
            "threshold": "Q007o total / new total >=100",
            "value": float(total_improvement_factor),
        },
        "registered_radius_strictly_improves": {
            "passed": bool(
                old_radius_still_passes and radius_strictly_improved
            ),
            "threshold": (
                "Q007o 1e-18 remains passing and the new maximum is larger"
            ),
            "value": {
                "old_radius_still_passes": old_radius_still_passes,
                "new_selected_exponent": (
                    None
                    if new_selected is None
                    else new_selected["candidate_exponent"]
                ),
            },
        },
        "new_boundary_is_strict_and_maximal": {
            "passed": new_boundary_passed,
            "threshold": (
                "new selected candidate has strict buffers/contraction/"
                "radii margin and the preceding larger candidate fails"
            ),
            "value": {
                "selected_passed": (
                    False if new_selected is None else new_selected["passed"]
                ),
                "previous_passed": (
                    None if previous is None else previous["passed"]
                ),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007ac phase-aware audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "phase-aware external-output discs remove the registered "
            "resolvent bottleneck"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered phase-aware external-output refinement did not "
            "remove the bottleneck"
        )

    return {
        "question": (
            "Can a complete phase-aware disc screen remove Q007n's "
            "external-output resolvent bottleneck while keeping Q007o's "
            "internal inverse and all radius majorants fixed?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
            "phase_gap": _fraction_record(PHASE_GAP),
            "phase_threshold_outward_binary_bits": (
                PHASE_THRESHOLD_OUTWARD_BINARY_BITS
            ),
            "minimum_total_improvement_factor": _fraction_record(
                MINIMUM_TOTAL_IMPROVEMENT_FACTOR
            ),
            "target_disc_count": TARGET_DISC_COUNT,
            "fourier_wave_sum_restriction_used": False,
            "candidate_exponents": list(CANDIDATE_EXPONENTS),
            "maximum_contraction": _fraction_record(MAXIMUM_CONTRACTION),
        },
        "input_artifacts": input_records,
        "implementation_source_audit": implementation_audit,
        "spectral_reconstruction": reconstruction,
        "nominal_selected_disc_audit": nominal_audit,
        "target_external_disc_audit": target_audit,
        "phase_aware_separation_audit": separation_audit,
        "inverse_refinement": inverse_audit,
        "radius_comparison": radius_comparison,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "q007o_explicit_radius_preserved": bool(
                validity_passed and old_radius_still_passes
            ),
            "external_output_resolvent_bottleneck_removed": bool(
                validity_passed and external_no_longer_limits
            ),
            "larger_registered_explicit_modal_l1_radius_certified": (
                hypotheses_passed
            ),
            "identified_with_q007i_theorem_manifold": hypotheses_passed,
        },
        "claim_boundary": (
            "This sharpens only the registered analytic existence radius for "
            "the fixed 17x17 filtered map on one conservation leaf and in "
            "the fixed modal/Wiener norms. The phase gap is a registered "
            "lower bound, not an optimum. The audit intentionally ignores "
            "the Fourier wave-sum restriction and does not improve Q007o's "
            "selected-output inverse or Q007n's zero-wave inverse. It does "
            "not enlarge or reinterpret Q007p--Q007ab, certify continuous "
            "optimization, Euclidean or grid-uniform attraction, a global "
            "basin, Q007c1 finite-amplitude performance, boundaries, "
            "forcing, or D3Q27."
        ),
        "preserved_prior_outcomes": {
            "q007o_explicit_radius_acceptance_changed": False,
            "q007p_through_q007ab_tube_results_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
            "q010_sparse_cost_dominance_changed": False,
        },
        "next_change": (
            "If accepted, the external-output bottleneck is closed at the "
            "registered threshold; the remaining existence-radius "
            "bottleneck is Q007o's selected-output internal inverse. Treat "
            "any further internal phase refinement as a separate gate."
        ),
    }


def run_q007ac_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_phase_aware_resolvent_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational phase-aware nonselected-output resolvent refinement"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": SELECTED_COMPLEX_DIMENSION,
            "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
            "claim": (
                "sharper explicit analytic existence radius only; no "
                "enlargement of the certified tube, attraction, positivity, "
                "MPFR, grid-uniform, or continuum claims"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q007ac_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
