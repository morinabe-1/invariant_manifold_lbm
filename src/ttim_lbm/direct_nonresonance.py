"""Sealed Q007i rational-log direct external nonresonance audit."""

from __future__ import annotations

import json
import math
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from hashlib import sha256
from math import comb
from pathlib import Path
from typing import Any

import numpy as np

from .adapted_metric import (
    ETA,
    FIXED_LEAF_DIMENSION,
    OMEGA,
    SELECTED_COMPLEX_DIMENSION,
    SIZE,
)
from .checkerboard_filter import filtered_fourier_symbol
from .equivariant_spectrum import (
    EXPECTED_NONZERO_ORBIT_COUNT,
    _c4_orbits,
    _certify_transported_block,
)
from .provenance import source_metadata
from .rational_spectrum import (
    EXPECTED_EXCLUDED_COUNT,
    EXPECTED_FIXED_LEAF_COUNT,
    EXPECTED_SELECTED_COUNT,
    Q007G_ARTIFACT,
    SELECTED_WAVES,
    RationalInterval,
    WaveIndex,
    _all_numeric_values_finite,
    _complex_point,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _modulus_disk_interval,
    _strict_json_serializable,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)

Q007H1_ARTIFACT = "q007h1_equivariant_spectrum.json"

LOG_SERIES_TERMS = 96
LOG_INTERNAL_DECIMAL_DIGITS = 110
LOG_FINAL_DECIMAL_DIGITS = 60
EXPECTED_DEGREE_COUNT = 88
EXPECTED_AGGREGATE_COUNT = 2_919_730
EXPECTED_EXPANDED_PRODUCT_COUNT = 869_107_778
EXPECTED_SELECTED_REPRESENTATIVE_COUNT = 2
EXPECTED_SELECTED_DISK_COUNT = 6
EXPECTED_SELECTED_MODULUS_TYPE_COUNT = 4
EXPECTED_EXTERNAL_REPRESENTATIVE_DISK_COUNT = 643
MINIMUM_CLASSIFICATION_MARGIN = Fraction(1, 10)
MAXIMUM_LOG_TAIL_BOUND = Fraction(1, 10**90)
MINIMUM_LOG_GAP = Fraction(1, 10**12)

THEOREM_REFERENCE = {
    "authors": "Xavier Cabre, Ernest Fontich, and Rafael de la Llave",
    "title": (
        "The Parameterization Method for Invariant Manifolds I: "
        "Manifolds Associated to Non-Resonant Subspaces"
    ),
    "result": "Theorem 1.2",
    "url": "https://upcommons.upc.edu/bitstream/handle/2117/876/0202cabre.pdf",
}


@dataclass(frozen=True, slots=True)
class _LogPointProof:
    interval: RationalInterval
    tail_bound: Fraction


@dataclass(frozen=True, slots=True)
class _RepresentativeProof:
    wave_index: WaveIndex
    eigenvalues: np.ndarray
    selected_indices: tuple[int, ...]
    radius: Fraction
    proof_digest: str
    artifact_digest: str

    @property
    def digest_matches(self) -> bool:
        return self.proof_digest == self.artifact_digest


@dataclass(frozen=True, slots=True)
class _SelectedModulusType:
    name: str
    interval: RationalInterval
    wave_index: WaveIndex
    eigenvalue_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class _ExternalDisk:
    interval: RationalInterval
    identifier: str


@dataclass(frozen=True, slots=True)
class _ScaledLogInterval:
    lower: int
    upper: int


@dataclass(slots=True)
class _MergedExternalLogInterval:
    lower: int
    upper: int
    identifiers: list[str]


def _input_artifact(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload, {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
    }


def _load_registered_inputs(
    artifact_directory: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    q007g, q007g_record = _input_artifact(artifact_directory / Q007G_ARTIFACT)
    q007h1, q007h1_record = _input_artifact(
        artifact_directory / Q007H1_ARTIFACT
    )

    q007g_scope = q007g.get("mathematical_scope", {})
    q007g_spectral = q007g.get("cycle", {}).get("spectral_audit", {})
    q007g_scope_match = (
        q007g_scope.get("construction_grid") == [SIZE, SIZE]
        and float(q007g_scope.get("omega", math.nan)) == OMEGA
        and float(q007g_scope.get("eta", math.nan)) == ETA
        and q007g_spectral.get("selected_complex_dimension")
        == SELECTED_COMPLEX_DIMENSION
        and q007g_spectral.get("excluded_complex_dimension")
        == EXPECTED_EXCLUDED_COUNT
        and q007g_spectral.get("fixed_leaf_complex_dimension")
        == FIXED_LEAF_DIMENSION
    )
    q007g_structure = q007g.get("cycle", {}).get("map_structure", {})
    q007g_record.update(
        {
            "scope_match": q007g_scope_match,
            "map_structure_proved": q007g_structure.get(
                "local_diffeomorphism_structurally_proved",
                False,
            ),
        }
    )
    q007g_record["passed"] = bool(
        q007g.get("schema_version") == 1
        and q007g_record["source_match"]
        and q007g.get("study_gate") == "passed"
        and q007g.get("scientific_outcome") == "not_ready"
        and q007g_scope_match
        and q007g_record["map_structure_proved"]
    )

    q007h1_scope = q007h1.get("mathematical_scope", {})
    q007h1_cycle = q007h1.get("cycle", {})
    q007h1_scope_match = (
        q007h1_scope.get("construction_grid") == [SIZE, SIZE]
        and float(q007h1_scope.get("omega", math.nan)) == OMEGA
        and float(q007h1_scope.get("eta", math.nan)) == ETA
        and q007h1_scope.get("selected_complex_dimension")
        == EXPECTED_SELECTED_COUNT
        and q007h1_scope.get("excluded_complex_dimension")
        == EXPECTED_EXCLUDED_COUNT
        and q007h1_scope.get("fixed_leaf_complex_dimension")
        == EXPECTED_FIXED_LEAF_COUNT
        and q007h1_scope.get("nonzero_c4_representative_count")
        == EXPECTED_NONZERO_ORBIT_COUNT
    )
    q007h1_validity_passed = bool(
        len(q007h1_cycle.get("validity_gates", {})) == 10
        and all(
            gate.get("passed", False)
            for gate in q007h1_cycle.get("validity_gates", {}).values()
        )
    )
    q007h1_hypotheses_passed = bool(
        len(q007h1_cycle.get("hypothesis_gates", {})) == 5
        and all(
            gate.get("passed", False)
            for gate in q007h1_cycle.get("hypothesis_gates", {}).values()
        )
    )
    q007h1_record.update(
        {
            "scope_match": q007h1_scope_match,
            "all_ten_validity_gates_passed": q007h1_validity_passed,
            "all_five_hypothesis_gates_passed": q007h1_hypotheses_passed,
        }
    )
    q007h1_record["passed"] = bool(
        q007h1.get("schema_version") == 1
        and q007h1_record["source_match"]
        and q007h1.get("study_gate") == "passed"
        and q007h1.get("scientific_outcome") == "accepted"
        and q007h1_scope_match
        and q007h1_validity_passed
        and q007h1_hypotheses_passed
    )
    return q007g, q007h1, {"q007g": q007g_record, "q007h1": q007h1_record}


def _rebuild_representative_proofs(
    q007h1: dict[str, Any],
) -> tuple[tuple[_RepresentativeProof, ...], dict[str, Any]]:
    block_records = {
        tuple(record["wave_index"]): record
        for record in q007h1["cycle"]["eigencertification"]["block_records"]
    }
    trig = trigonometric_intervals(machin_pi_interval())
    collision = rational_collision_symbol()
    representatives = []
    reconstruction_records = []
    for orbit in _c4_orbits():
        wave_index = orbit.representative
        if wave_index == (0, 0):
            continue
        kx = 2.0 * np.pi * wave_index[0] / SIZE
        ky = 2.0 * np.pi * wave_index[1] / SIZE
        center = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
        eigenvalues, eigenvectors = np.linalg.eig(center)
        inverse_candidate = np.linalg.inv(eigenvectors)
        selected_indices = (
            tuple(
                int(index)
                for index in np.argsort(np.abs(eigenvalues))[::-1][:3]
            )
            if wave_index in SELECTED_WAVES
            else ()
        )
        symbol = rational_fourier_symbol(wave_index, trig, collision)
        proof = _certify_transported_block(
            wave_index,
            symbol,
            eigenvalues,
            eigenvectors,
            inverse_candidate,
            selected_indices,
        )
        artifact_digest = block_records[wave_index]["exact_proof_digest_sha256"]
        representative = _RepresentativeProof(
            wave_index=wave_index,
            eigenvalues=eigenvalues,
            selected_indices=selected_indices,
            radius=proof.bauer_fike_radius,
            proof_digest=proof.proof_digest,
            artifact_digest=artifact_digest,
        )
        representatives.append(representative)
        reconstruction_records.append(
            {
                "wave_index": list(wave_index),
                "selected_count": len(selected_indices),
                "external_count": 9 - len(selected_indices),
                "proof_digest_sha256": proof.proof_digest,
                "artifact_digest_sha256": artifact_digest,
                "digest_matches": representative.digest_matches,
                "bauer_fike_radius": _fraction_record(proof.bauer_fike_radius),
            }
        )
    result = tuple(representatives)
    mismatch_count = sum(not proof.digest_matches for proof in result)
    return result, {
        "representative_count": len(result),
        "proof_digest_mismatch_count": mismatch_count,
        "all_proof_digests_match": mismatch_count == 0,
        "records": reconstruction_records,
    }


def _selected_types_and_external_disks(
    representatives: tuple[_RepresentativeProof, ...],
) -> tuple[
    tuple[_SelectedModulusType, ...],
    tuple[_ExternalDisk, ...],
    dict[str, Any],
]:
    selected_representatives = tuple(
        proof for proof in representatives if proof.selected_indices
    )
    selected_types: dict[str, _SelectedModulusType] = {}
    classification_records = []
    minimum_margin: Fraction | None = None
    selected_disk_count = 0
    for proof in selected_representatives:
        imaginary_moduli = {
            index: abs(_complex_point(proof.eigenvalues[index]).imag.lower)
            for index in proof.selected_indices
        }
        shear_index = min(imaginary_moduli, key=imaginary_moduli.__getitem__)
        acoustic_indices = tuple(
            index for index in proof.selected_indices if index != shear_index
        )
        margin = min(imaginary_moduli[index] for index in acoustic_indices) - (
            imaginary_moduli[shear_index]
        )
        minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
        disk_intervals = {
            index: _modulus_disk_interval(
                proof.eigenvalues[index],
                proof.radius,
            )
            for index in proof.selected_indices
        }
        acoustic_hull = RationalInterval(
            min(disk_intervals[index].lower for index in acoustic_indices),
            max(disk_intervals[index].upper for index in acoustic_indices),
        )
        axis_or_diagonal = "axis" if 0 in proof.wave_index else "diagonal"
        selected_types[f"{axis_or_diagonal}_acoustic"] = _SelectedModulusType(
            name=f"{axis_or_diagonal}_acoustic",
            interval=acoustic_hull,
            wave_index=proof.wave_index,
            eigenvalue_indices=tuple(sorted(acoustic_indices)),
        )
        selected_types[f"{axis_or_diagonal}_shear"] = _SelectedModulusType(
            name=f"{axis_or_diagonal}_shear",
            interval=disk_intervals[shear_index],
            wave_index=proof.wave_index,
            eigenvalue_indices=(shear_index,),
        )
        selected_disk_count += len(proof.selected_indices)
        classification_records.append(
            {
                "wave_index": list(proof.wave_index),
                "shear_index": shear_index,
                "acoustic_indices": sorted(acoustic_indices),
                "imaginary_classification_margin": _fraction_record(margin),
            }
        )

    ordered_names = (
        "axis_acoustic",
        "axis_shear",
        "diagonal_acoustic",
        "diagonal_shear",
    )
    ordered_types = tuple(selected_types[name] for name in ordered_names)

    external_disks = []
    for proof in representatives:
        selected_set = frozenset(proof.selected_indices)
        for index, eigenvalue in enumerate(proof.eigenvalues):
            if index in selected_set:
                continue
            external_disks.append(
                _ExternalDisk(
                    interval=_modulus_disk_interval(eigenvalue, proof.radius),
                    identifier=(
                        f"wave={proof.wave_index[0]},{proof.wave_index[1]};"
                        f"eigenvalue_index={index}"
                    ),
                )
            )
    external_disks.append(
        _ExternalDisk(
            interval=RationalInterval.point(Fraction(1, 2)),
            identifier="wave=0,0;kinetic_eigenvalue=-1/2",
        )
    )
    assert minimum_margin is not None
    return ordered_types, tuple(external_disks), {
        "selected_representative_count": len(selected_representatives),
        "selected_disk_count": selected_disk_count,
        "selected_modulus_type_count": len(ordered_types),
        "external_representative_disk_count": len(external_disks),
        "minimum_acoustic_shear_classification_margin": _fraction_record(
            minimum_margin
        ),
        "minimum_acoustic_shear_classification_margin_exact": minimum_margin,
        "classification_records": classification_records,
    }


@cache
def rational_log_point(value: Fraction) -> _LogPointProof:
    """Enclose log(value) for a positive rational below one."""

    if not 0 < value < 1:
        raise ValueError("registered rational logarithm requires 0 < value < 1")
    z = (value - 1) / (value + 1)
    z_interval = RationalInterval.point(z).rounded_outward(
        LOG_INTERNAL_DECIMAL_DIGITS
    )
    z_squared = (z_interval * z_interval).rounded_outward(
        LOG_INTERNAL_DECIMAL_DIGITS
    )
    power = z_interval
    partial = RationalInterval.point(0)
    for index in range(LOG_SERIES_TERMS):
        partial = (
            partial + power.scale(Fraction(1, 2 * index + 1))
        ).rounded_outward(LOG_INTERNAL_DECIMAL_DIGITS)
        if index + 1 < LOG_SERIES_TERMS:
            power = (power * z_squared).rounded_outward(
                LOG_INTERNAL_DECIMAL_DIGITS
            )
    next_power = (power * z_squared).rounded_outward(
        LOG_INTERNAL_DECIMAL_DIGITS
    )
    z_absolute_upper = z_interval.maximum_absolute_value
    denominator_lower = 1 - z_absolute_upper * z_absolute_upper
    if denominator_lower <= 0:
        raise RuntimeError("atanh remainder denominator is not positive")
    tail_bound = (
        2
        * next_power.maximum_absolute_value
        / ((2 * LOG_SERIES_TERMS + 1) * denominator_lower)
    )
    raw = partial.scale(2) + RationalInterval(-tail_bound, tail_bound)
    return _LogPointProof(
        interval=raw.rounded_outward(LOG_FINAL_DECIMAL_DIGITS),
        tail_bound=tail_bound,
    )


def _log_modulus_interval(
    modulus: RationalInterval,
) -> tuple[RationalInterval, Fraction]:
    lower = rational_log_point(modulus.lower)
    upper = rational_log_point(modulus.upper)
    return (
        RationalInterval(lower.interval.lower, upper.interval.upper),
        max(lower.tail_bound, upper.tail_bound),
    )


def _scaled_log_interval(value: RationalInterval) -> _ScaledLogInterval:
    scale = 10**LOG_FINAL_DECIMAL_DIGITS
    lower = value.lower * scale
    upper = value.upper * scale
    if lower.denominator != 1 or upper.denominator != 1:
        raise RuntimeError("final logarithm endpoint is not on the registered grid")
    return _ScaledLogInterval(int(lower), int(upper))


def _scaled_interval_record(value: _ScaledLogInterval) -> dict[str, Any]:
    scale = 10**LOG_FINAL_DECIMAL_DIGITS
    return {
        "lower_scaled_integer": str(value.lower),
        "upper_scaled_integer": str(value.upper),
        "scale_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
        "lower_float": value.lower / scale,
        "upper_float": value.upper / scale,
    }


def _log_enclosures(
    selected_types: tuple[_SelectedModulusType, ...],
    external_disks: tuple[_ExternalDisk, ...],
) -> tuple[
    tuple[_ScaledLogInterval, ...],
    tuple[tuple[_ScaledLogInterval, str], ...],
    dict[str, Any],
]:
    maximum_tail_bound = Fraction(0)
    selected_logs = []
    selected_records = []
    for selected_type in selected_types:
        log_interval, tail_bound = _log_modulus_interval(selected_type.interval)
        maximum_tail_bound = max(maximum_tail_bound, tail_bound)
        scaled = _scaled_log_interval(log_interval)
        selected_logs.append(scaled)
        selected_records.append(
            {
                "name": selected_type.name,
                "source_wave": list(selected_type.wave_index),
                "source_eigenvalue_indices": list(
                    selected_type.eigenvalue_indices
                ),
                "modulus_interval": {
                    "lower": _fraction_record(selected_type.interval.lower),
                    "upper": _fraction_record(selected_type.interval.upper),
                },
                "log_interval": _scaled_interval_record(scaled),
                "maximum_endpoint_tail_bound": _fraction_record(tail_bound),
            }
        )

    external_logs = []
    digest = sha256()
    for disk in external_disks:
        log_interval, tail_bound = _log_modulus_interval(disk.interval)
        maximum_tail_bound = max(maximum_tail_bound, tail_bound)
        scaled = _scaled_log_interval(log_interval)
        external_logs.append((scaled, disk.identifier))
        digest.update(disk.identifier.encode("utf-8"))
        digest.update(b"\0")
        for endpoint in (disk.interval.lower, disk.interval.upper):
            digest.update(hex(endpoint.numerator).encode("ascii"))
            digest.update(b"/")
            digest.update(hex(endpoint.denominator).encode("ascii"))
            digest.update(b"\0")
    return tuple(selected_logs), tuple(external_logs), {
        "series_terms": LOG_SERIES_TERMS,
        "internal_outward_decimal_digits": LOG_INTERNAL_DECIMAL_DIGITS,
        "final_outward_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
        "maximum_tail_bound": _fraction_record(maximum_tail_bound),
        "maximum_tail_bound_exact": maximum_tail_bound,
        "selected_type_records": selected_records,
        "external_disk_log_digest_sha256": digest.hexdigest(),
    }


def _merge_external_logs(
    external_logs: tuple[tuple[_ScaledLogInterval, str], ...],
) -> tuple[_MergedExternalLogInterval, ...]:
    ordered = sorted(
        external_logs,
        key=lambda record: (record[0].lower, record[0].upper, record[1]),
    )
    merged: list[_MergedExternalLogInterval] = []
    for interval, identifier in ordered:
        if merged and interval.lower <= merged[-1].upper:
            merged[-1].upper = max(merged[-1].upper, interval.upper)
            merged[-1].identifiers.append(identifier)
        else:
            merged.append(
                _MergedExternalLogInterval(
                    lower=interval.lower,
                    upper=interval.upper,
                    identifiers=[identifier],
                )
            )
    return tuple(merged)


def _enumerate_aggregates(
    selected_logs: tuple[_ScaledLogInterval, ...],
    merged_external: tuple[_MergedExternalLogInterval, ...],
) -> dict[str, Any]:
    if len(selected_logs) != EXPECTED_SELECTED_MODULUS_TYPE_COUNT:
        raise ValueError("four selected log-modulus types are required")
    starts = [interval.lower for interval in merged_external]
    total_aggregates = 0
    total_expanded = 0
    total_overlaps = 0
    global_minimum_gap: int | None = None
    global_witness: dict[str, Any] | None = None
    first_overlap: dict[str, Any] | None = None
    degree_records = []

    for degree in range(2, 90):
        degree_aggregates = 0
        degree_expanded = 0
        degree_overlaps = 0
        degree_minimum_gap: int | None = None
        degree_witness: dict[str, Any] | None = None
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
                            counts,
                            selected_logs,
                            strict=True,
                        )
                    )
                    upper = sum(
                        count * interval.upper
                        for count, interval in zip(
                            counts,
                            selected_logs,
                            strict=True,
                        )
                    )
                    degree_aggregates += 1
                    degree_expanded += (axis_acoustic + 1) * (
                        diagonal_acoustic + 1
                    )

                    insertion = bisect_right(starts, upper)
                    overlap_index = (
                        insertion - 1
                        if insertion
                        and merged_external[insertion - 1].upper >= lower
                        else None
                    )
                    if overlap_index is not None:
                        degree_overlaps += 1
                        if first_overlap is None:
                            first_overlap = {
                                "degree": degree,
                                "counts": list(counts),
                                "merged_external_index": overlap_index,
                                "external_identifiers": merged_external[
                                    overlap_index
                                ].identifiers[:8],
                            }
                        continue

                    candidates = []
                    if insertion:
                        candidates.append(
                            (
                                lower - merged_external[insertion - 1].upper,
                                "left",
                                insertion - 1,
                            )
                        )
                    if insertion < len(merged_external):
                        candidates.append(
                            (
                                merged_external[insertion].lower - upper,
                                "right",
                                insertion,
                            )
                        )
                    if not candidates:
                        raise RuntimeError("no external interval neighbors found")
                    gap, side, external_index = min(candidates)
                    witness = {
                        "degree": degree,
                        "counts": list(counts),
                        "external_side": side,
                        "merged_external_index": external_index,
                        "external_identifier_count": len(
                            merged_external[external_index].identifiers
                        ),
                        "external_identifiers": merged_external[
                            external_index
                        ].identifiers[:8],
                    }
                    if degree_minimum_gap is None or gap < degree_minimum_gap:
                        degree_minimum_gap = gap
                        degree_witness = witness
                    if global_minimum_gap is None or gap < global_minimum_gap:
                        global_minimum_gap = gap
                        global_witness = witness

        expected_aggregates = comb(degree + 3, 3)
        expected_expanded = comb(degree + 5, 5)
        degree_records.append(
            {
                "degree": degree,
                "aggregate_count": degree_aggregates,
                "expected_aggregate_count": expected_aggregates,
                "expanded_product_count": degree_expanded,
                "expected_expanded_product_count": expected_expanded,
                "overlap_count": degree_overlaps,
                "minimum_log_gap": (
                    None
                    if degree_minimum_gap is None
                    else _fraction_record(
                        Fraction(
                            degree_minimum_gap,
                            10**LOG_FINAL_DECIMAL_DIGITS,
                        )
                    )
                ),
                "minimum_gap_witness": degree_witness,
                "count_checks_passed": bool(
                    degree_aggregates == expected_aggregates
                    and degree_expanded == expected_expanded
                ),
            }
        )
        total_aggregates += degree_aggregates
        total_expanded += degree_expanded
        total_overlaps += degree_overlaps

    if global_minimum_gap is None:
        minimum_gap_record = None
        minimum_gap_fraction = Fraction(0)
    else:
        minimum_gap_fraction = Fraction(
            global_minimum_gap,
            10**LOG_FINAL_DECIMAL_DIGITS,
        )
        minimum_gap_record = _fraction_record(minimum_gap_fraction)
    return {
        "degree_count": len(degree_records),
        "aggregate_count": total_aggregates,
        "expanded_product_count": total_expanded,
        "overlap_count": total_overlaps,
        "global_minimum_log_gap": minimum_gap_record,
        "global_minimum_log_gap_exact": minimum_gap_fraction,
        "global_minimum_gap_witness": global_witness,
        "first_overlap": first_overlap,
        "degree_records": degree_records,
    }


def _merged_external_records(
    merged: tuple[_MergedExternalLogInterval, ...],
) -> list[dict[str, Any]]:
    return [
        {
            "merged_index": index,
            "log_interval": _scaled_interval_record(
                _ScaledLogInterval(interval.lower, interval.upper)
            ),
            "source_disk_count": len(interval.identifiers),
            "first_identifiers": interval.identifiers[:8],
        }
        for index, interval in enumerate(merged)
    ]


def run_direct_nonresonance_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the preregistered Q007i direct nonresonance certification."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007g, q007h1, input_records = _load_registered_inputs(directory)
    representatives, reconstruction = _rebuild_representative_proofs(q007h1)
    selected_types, external_disks, classification_internal = (
        _selected_types_and_external_disks(representatives)
    )
    classification_margin = classification_internal[
        "minimum_acoustic_shear_classification_margin_exact"
    ]
    classification = {
        key: value
        for key, value in classification_internal.items()
        if not key.endswith("_exact")
    }
    selected_logs, external_logs, logarithms_internal = _log_enclosures(
        selected_types,
        external_disks,
    )
    maximum_tail_bound = logarithms_internal["maximum_tail_bound_exact"]
    logarithms = {
        key: value
        for key, value in logarithms_internal.items()
        if not key.endswith("_exact")
    }
    merged_external = _merge_external_logs(external_logs)
    enumeration_internal = _enumerate_aggregates(
        selected_logs,
        merged_external,
    )
    minimum_log_gap = enumeration_internal["global_minimum_log_gap_exact"]
    enumeration = {
        key: value
        for key, value in enumeration_internal.items()
        if not key.endswith("_exact")
    }

    spectral_reconstruction = {
        **reconstruction,
        **classification,
        "external_merged_log_interval_count": len(merged_external),
        "merged_external_log_intervals": _merged_external_records(
            merged_external
        ),
    }
    serializable_sections = {
        "input_artifacts": input_records,
        "spectral_reconstruction": spectral_reconstruction,
        "rational_logarithms": logarithms,
        "enumeration": enumeration,
    }
    finite_and_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )

    validity_gates = {
        "registered_inputs": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": "Q007g and Q007h1 source, scope, and sealed outcomes match",
            "value": {
                name: record["passed"] for name, record in input_records.items()
            },
        },
        "representative_proof_reconstruction": {
            "passed": bool(
                reconstruction["representative_count"]
                == EXPECTED_NONZERO_ORBIT_COUNT
                and reconstruction["proof_digest_mismatch_count"] == 0
            ),
            "threshold": "72 representatives and zero proof-digest mismatches",
            "value": {
                "representative_count": reconstruction["representative_count"],
                "proof_digest_mismatch_count": reconstruction[
                    "proof_digest_mismatch_count"
                ],
            },
        },
        "registered_disk_compression": {
            "passed": bool(
                classification["selected_representative_count"]
                == EXPECTED_SELECTED_REPRESENTATIVE_COUNT
                and classification["selected_disk_count"]
                == EXPECTED_SELECTED_DISK_COUNT
                and classification["selected_modulus_type_count"]
                == EXPECTED_SELECTED_MODULUS_TYPE_COUNT
                and classification["external_representative_disk_count"]
                == EXPECTED_EXTERNAL_REPRESENTATIVE_DISK_COUNT
            ),
            "threshold": "2 selected representatives, 6 disks, 4 types, 643 external disks",
            "value": {
                "selected_representative_count": classification[
                    "selected_representative_count"
                ],
                "selected_disk_count": classification["selected_disk_count"],
                "selected_modulus_type_count": classification[
                    "selected_modulus_type_count"
                ],
                "external_representative_disk_count": classification[
                    "external_representative_disk_count"
                ],
            },
        },
        "acoustic_shear_classification": {
            "passed": classification_margin >= MINIMUM_CLASSIFICATION_MARGIN,
            "threshold": "minimum imaginary-part classification margin >= 0.1",
            "value": float(classification_margin),
        },
        "rational_log_enclosure": {
            "passed": maximum_tail_bound <= MAXIMUM_LOG_TAIL_BOUND,
            "threshold": "96 terms, 110/60 digit outward grids, tail <= 1e-90",
            "value": float(maximum_tail_bound),
        },
        "registered_enumeration_counts": {
            "passed": bool(
                enumeration["degree_count"] == EXPECTED_DEGREE_COUNT
                and enumeration["aggregate_count"] == EXPECTED_AGGREGATE_COUNT
                and enumeration["expanded_product_count"]
                == EXPECTED_EXPANDED_PRODUCT_COUNT
                and all(
                    record["count_checks_passed"]
                    for record in enumeration["degree_records"]
                )
            ),
            "threshold": "88 degrees, 2,919,730 aggregates, 869,107,778 products",
            "value": {
                "degree_count": enumeration["degree_count"],
                "aggregate_count": enumeration["aggregate_count"],
                "expanded_product_count": enumeration[
                    "expanded_product_count"
                ],
            },
        },
        "finite_strict_json": {
            "passed": finite_and_json,
            "threshold": "all numeric summaries finite and strict JSON serializable",
            "value": finite_and_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    q007h1_hypotheses = q007h1["cycle"]["hypothesis_gates"]
    q007g_structure = q007g["cycle"]["map_structure"]
    predecessor_tail_and_structure = bool(
        q007h1_hypotheses["degree_90_tail"]["passed"]
        and q007h1_hypotheses["selected_spectrum_strictly_stable"]["passed"]
        and q007h1_hypotheses["excluded_spectrum_invertible"]["passed"]
        and q007g_structure["local_diffeomorphism_structurally_proved"]
    )
    hypothesis_gates = {
        "zero_direct_modulus_overlaps": {
            "passed": enumeration["overlap_count"] == 0,
            "threshold": "zero aggregate/external merged-log overlaps",
            "value": enumeration["overlap_count"],
        },
        "all_aggregates_checked": {
            "passed": enumeration["aggregate_count"]
            == EXPECTED_AGGREGATE_COUNT,
            "threshold": "all 2,919,730 aggregate intervals checked",
            "value": enumeration["aggregate_count"],
        },
        "minimum_log_gap": {
            "passed": minimum_log_gap >= MINIMUM_LOG_GAP,
            "threshold": "global rational log-gap lower bound >= 1e-12",
            "value": float(minimum_log_gap),
        },
        "predecessor_tail_and_map_structure": {
            "passed": predecessor_tail_and_structure,
            "threshold": "Q007h1 degree-90 tail/stability/invertibility and Q007g map structure pass",
            "value": predecessor_tail_and_structure,
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered rational-log direct nonresonance audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered direct external nonresonance through degree 89 certified"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered modulus-only direct nonresonance certification failed"
        )

    theorem_assumptions = {
        "analytic_fixed_leaf_map": q007g_structure["checks"][
            "equilibrium_analytic_near_unit_density"
        ],
        "local_diffeomorphism": q007g_structure[
            "local_diffeomorphism_structurally_proved"
        ],
        "selected_subspace_invariant": input_records["q007h1"]["passed"],
        "selected_spectrum_strictly_stable": q007h1_hypotheses[
            "selected_spectrum_strictly_stable"
        ]["passed"],
        "excluded_spectrum_invertible": q007h1_hypotheses[
            "excluded_spectrum_invertible"
        ]["passed"],
        "degree_90_tail": q007h1_hypotheses["degree_90_tail"]["passed"],
        "degrees_2_through_89_direct_nonresonance": bool(
            validity_passed and hypotheses_passed
        ),
        "analytic_regularity_exceeds_L_plus_one": True,
    }
    theorem_applies = bool(
        validity_passed
        and hypotheses_passed
        and all(theorem_assumptions.values())
    )
    theorem_consequence = {
        "reference": THEOREM_REFERENCE,
        "registered_L": 89,
        "assumptions": theorem_assumptions,
        "theorem_applies": theorem_applies,
        "existence_conclusion": theorem_applies,
        "conclusion": (
            "a local analytic invariant manifold on the fixed conservation "
            "leaf tangent to the selected 24-real-dimensional spectral "
            "subspace, with analytic K and R"
            if theorem_applies
            else "no theorem conclusion because a registered gate failed"
        ),
        "uniqueness_conclusion": (
            "locally unique among C^90 locally invariant manifolds tangent "
            "to the same selected subspace"
            if theorem_applies
            else "not established"
        ),
        "explicit_neighborhood_radius_available": False,
        "registered_quartic_chart_identified_with_the_theorem_manifold": False,
    }

    return {
        "question": (
            "Can direct external nonresonance for every degree 2 through 89 "
            "be certified by rational log-modulus separation?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "degree_range": [2, 89],
            "selected_modulus_type_order": [
                "axis_acoustic",
                "axis_shear",
                "diagonal_acoustic",
                "diagonal_shear",
            ],
            "log_series_terms": LOG_SERIES_TERMS,
            "log_internal_decimal_digits": LOG_INTERNAL_DECIMAL_DIGITS,
            "log_final_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
        },
        "input_artifacts": input_records,
        "spectral_reconstruction": spectral_reconstruction,
        "rational_logarithms": logarithms,
        "enumeration": enumeration,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": theorem_consequence,
        "claim_boundary": (
            "The theorem conclusion is qualitative and local for the fixed "
            "17x17 filtered map on one conservation leaf. It supplies no "
            "explicit neighborhood radius, no rigorous identification of the "
            "stored quartic coefficients, no finite-ball normal-attraction "
            "bound, and no grid-uniform or continuum-limit result."
        ),
        "preserved_prior_outcomes": {
            "q007h1_linear_acceptance_changed": False,
            "q007h_independent_preconditioner_inconclusive_changed": False,
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "The next gate will identify the numerical quartic jet with the "
            "unique theorem manifold and seek an explicit validated radius."
        ),
    }
