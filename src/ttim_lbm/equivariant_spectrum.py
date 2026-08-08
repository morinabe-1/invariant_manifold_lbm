"""Sealed Q007h1 C4-equivariant rational spectral certification."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

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
from .rational_spectrum import (
    EXPECTED_EXCLUDED_COUNT,
    EXPECTED_FIXED_LEAF_COUNT,
    EXPECTED_SELECTED_COUNT,
    INTERVAL_DECIMAL_DIGITS,
    MACHIN_TERMS,
    MAXIMUM_BAUER_FIKE_RADIUS,
    MAXIMUM_FLOAT_REPRODUCTION_RELATIVE_ERROR,
    MAXIMUM_INVERSE_DEFECT,
    MAXIMUM_PI_TRIGONOMETRIC_WIDTH,
    MAXIMUM_SYMBOL_ENTRY_WIDTH,
    MINIMUM_SELECTED_GROUP_GAP,
    Q007G_ARTIFACT,
    SELECTED_WAVES,
    SQRT_DECIMAL_DIGITS,
    TAIL_DEGREE,
    TRIGONOMETRIC_TERMS,
    VELOCITIES,
    ComplexIntervalMatrix,
    ComplexRationalInterval,
    WaveIndex,
    _all_numeric_values_finite,
    _block_record,
    _BlockProof,
    _center_distance_lower,
    _complex_point,
    _default_artifact_directory,
    _diagonal_matrix,
    _file_sha256,
    _fraction_record,
    _identity_matrix,
    _interval_record,
    _matrix_from_numpy,
    _matrix_infinity_norm_upper,
    _matrix_multiply,
    _matrix_subtract,
    _modulus_disk_interval,
    _proof_digest,
    _relative_scalar_error,
    _strict_json_serializable,
    _symmetry_audit,
    _wave_indices,
    _zero_block_proof,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)

Q007H_ARTIFACT = "q007h_rational_spectrum.json"
EXPECTED_ORBIT_COUNT = 73
EXPECTED_NONZERO_ORBIT_COUNT = 72
EXPECTED_NONZERO_MEMBER_COUNT = 288


def rotate_wave(wave_index: WaveIndex) -> WaveIndex:
    """Apply the registered counter-clockwise quarter turn modulo 17."""

    half = SIZE // 2
    nx, ny = wave_index
    return (
        (-ny + half) % SIZE - half,
        (nx + half) % SIZE - half,
    )


def _quarter_turn_mapping() -> tuple[int, ...]:
    index = {velocity: position for position, velocity in enumerate(VELOCITIES)}
    return tuple(index[(-cy, cx)] for cx, cy in VELOCITIES)


QUARTER_TURN_MAPPING = _quarter_turn_mapping()


def _mapping_power(power: int) -> tuple[int, ...]:
    if power < 0:
        raise ValueError("permutation power must be nonnegative")
    mapping = tuple(range(9))
    for _ in range(power % 4):
        mapping = tuple(QUARTER_TURN_MAPPING[index] for index in mapping)
    return mapping


def _permutation_matrix() -> list[list[int]]:
    matrix = [[0 for _ in range(9)] for _ in range(9)]
    for source, target in enumerate(QUARTER_TURN_MAPPING):
        matrix[target][source] = 1
    return matrix


def _rotate_interval_matrix(
    matrix: ComplexIntervalMatrix,
    power: int = 1,
) -> ComplexIntervalMatrix:
    mapping = _mapping_power(power)
    output = [
        [ComplexRationalInterval.zero() for _ in range(9)]
        for _ in range(9)
    ]
    for source_row, target_row in enumerate(mapping):
        for source_column, target_column in enumerate(mapping):
            output[target_row][target_column] = matrix[source_row][source_column]
    return output


def _transport_preconditioner(
    eigenvectors: np.ndarray,
    inverse_candidate: np.ndarray,
    power: int,
) -> tuple[np.ndarray, np.ndarray]:
    mapping = _mapping_power(power)
    transported_vectors = np.empty_like(eigenvectors)
    transported_inverse = np.empty_like(inverse_candidate)
    for source, target in enumerate(mapping):
        transported_vectors[target, :] = eigenvectors[source, :]
        transported_inverse[:, target] = inverse_candidate[:, source]
    return transported_vectors, transported_inverse


@dataclass(frozen=True, slots=True)
class _Orbit:
    representative: WaveIndex
    members: tuple[WaveIndex, ...]


def _c4_orbits() -> tuple[_Orbit, ...]:
    unassigned = set(_wave_indices())
    orbits: list[_Orbit] = []
    while unassigned:
        seed = min(unassigned)
        members = []
        current = seed
        for _ in range(4):
            if current not in members:
                members.append(current)
            current = rotate_wave(current)
        representative = min(members)
        ordered = []
        current = representative
        for _ in range(len(members)):
            ordered.append(current)
            current = rotate_wave(current)
        orbit = _Orbit(representative, tuple(ordered))
        orbits.append(orbit)
        unassigned.difference_update(orbit.members)
    return tuple(sorted(orbits, key=lambda orbit: orbit.representative))


def _input_artifact_record(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
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
    q007h, q007h_record = _input_artifact_record(
        artifact_directory / Q007H_ARTIFACT
    )
    q007g, q007g_record = _input_artifact_record(
        artifact_directory / Q007G_ARTIFACT
    )
    q007h_scope = q007h.get("mathematical_scope", {})
    q007h_cycle = q007h.get("cycle", {})
    q007h_failed_validity = sorted(
        name
        for name, gate in q007h_cycle.get("validity_gates", {}).items()
        if not gate.get("passed", False)
    )
    q007h_scope_match = (
        q007h_scope.get("construction_grid") == [SIZE, SIZE]
        and float(q007h_scope.get("omega", math.nan)) == OMEGA
        and float(q007h_scope.get("eta", math.nan)) == ETA
        and q007h_scope.get("selected_complex_dimension")
        == SELECTED_COMPLEX_DIMENSION
        and q007h_scope.get("excluded_complex_dimension")
        == EXPECTED_EXCLUDED_COUNT
        and q007h_scope.get("fixed_leaf_complex_dimension")
        == FIXED_LEAF_DIMENSION
    )
    q007h_hypotheses_passed = bool(
        len(q007h_cycle.get("hypothesis_gates", {})) == 5
        and all(
            gate.get("passed", False)
            for gate in q007h_cycle.get("hypothesis_gates", {}).values()
        )
    )
    q007h_record.update(
        {
            "scope_match": q007h_scope_match,
            "failed_validity_gates": q007h_failed_validity,
            "all_five_hypothesis_gates_passed": q007h_hypotheses_passed,
        }
    )
    q007h_record["passed"] = bool(
        q007h.get("schema_version") == 1
        and q007h_record["source_match"]
        and q007h.get("study_gate") == "failed"
        and q007h.get("scientific_outcome") == "inconclusive"
        and q007h_scope_match
        and q007h_failed_validity == ["conjugate_and_c4_symmetry"]
        and q007h_hypotheses_passed
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
    q007g_record["scope_match"] = q007g_scope_match
    q007g_record["passed"] = bool(
        q007g.get("schema_version") == 1
        and q007g_record["source_match"]
        and q007g.get("study_gate") == "passed"
        and q007g.get("scientific_outcome") == "not_ready"
        and q007g_scope_match
    )
    return q007h, q007g, {"q007h": q007h_record, "q007g": q007g_record}


def _certify_transported_block(
    wave_index: WaveIndex,
    symbol: ComplexIntervalMatrix,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    inverse_candidate: np.ndarray,
    selected_indices: Sequence[int],
) -> _BlockProof:
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

    selected_indices_ordered = tuple(sorted(int(index) for index in selected_indices))
    selected_index_set = frozenset(selected_indices_ordered)
    excluded_indices = tuple(
        index for index in range(9) if index not in selected_index_set
    )
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
            _center_distance_lower(eigenvalues[left], eigenvalues[right])
            - 2 * radius
            for left in selected_indices_ordered
            for right in excluded_indices
        )
    maximum_symbol_entry_width = max(
        max(value.real.width, value.imag.width)
        for row in symbol
        for value in row
    )
    center_moduli = np.abs(eigenvalues)
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


def _symbol_covariance_audit(
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
) -> dict[str, Any]:
    mismatch_edge_count = 0
    mismatch_entry_count = 0
    first_mismatch: dict[str, Any] | None = None
    for wave_index, symbol in symbols.items():
        target = rotate_wave(wave_index)
        transported = _rotate_interval_matrix(symbol)
        entry_mismatches = sum(
            transported[row][column] != symbols[target][row][column]
            for row in range(9)
            for column in range(9)
        )
        if entry_mismatches:
            mismatch_edge_count += 1
            mismatch_entry_count += entry_mismatches
            if first_mismatch is None:
                first_mismatch = {
                    "source_wave": list(wave_index),
                    "target_wave": list(target),
                    "entry_mismatch_count": entry_mismatches,
                }
    return {
        "edge_count": len(symbols),
        "mismatch_edge_count": mismatch_edge_count,
        "mismatch_entry_count": mismatch_entry_count,
        "first_mismatch": first_mismatch,
        "entrywise_exact": mismatch_entry_count == 0,
    }


def _orbit_consistency_audit(
    orbits: Sequence[_Orbit],
    proofs: dict[WaveIndex, _BlockProof],
) -> tuple[dict[str, Any], Fraction]:
    maximum_exact_difference = Fraction(0)
    records = []
    for orbit in orbits:
        orbit_proofs = [proofs[wave] for wave in orbit.members]
        epsilon_values = [proof.epsilon for proof in orbit_proofs]
        radius_values = [proof.bauer_fike_radius for proof in orbit_proofs]
        beta_values = [proof.beta for proof in orbit_proofs]
        orbit_difference = max(
            max(epsilon_values) - min(epsilon_values),
            max(radius_values) - min(radius_values),
            max(beta_values) - min(beta_values),
        )
        maximum_exact_difference = max(maximum_exact_difference, orbit_difference)
        records.append(
            {
                "representative": list(orbit.representative),
                "members": [list(wave) for wave in orbit.members],
                "member_count": len(orbit.members),
                "epsilon": _fraction_record(epsilon_values[0]),
                "bauer_fike_radius": _fraction_record(radius_values[0]),
                "exact_transport_parameter_difference": _fraction_record(
                    orbit_difference
                ),
            }
        )
    return {
        "orbit_count": len(orbits),
        "nonzero_orbit_count": sum(orbit.representative != (0, 0) for orbit in orbits),
        "nonzero_member_count": sum(
            len(orbit.members)
            for orbit in orbits
            if orbit.representative != (0, 0)
        ),
        "maximum_exact_transport_parameter_difference": _fraction_record(
            maximum_exact_difference
        ),
        "records": records,
    }, maximum_exact_difference


def run_equivariant_rational_spectral_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the preregistered Q007h1 C4-transported rational audit."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007h, q007g, input_records = _load_registered_inputs(directory)
    registered_spectral = q007g["cycle"]["spectral_audit"]

    pi_enclosure = machin_pi_interval()
    trig = trigonometric_intervals(pi_enclosure)
    collision = rational_collision_symbol()
    symbols = {
        wave: rational_fourier_symbol(wave, trig, collision)
        for wave in _wave_indices()
    }
    covariance = _symbol_covariance_audit(symbols)
    orbits = _c4_orbits()
    proofs: dict[WaveIndex, _BlockProof] = {(0, 0): _zero_block_proof()}
    for orbit in orbits:
        representative = orbit.representative
        if representative == (0, 0):
            continue
        kx = 2.0 * np.pi * representative[0] / SIZE
        ky = 2.0 * np.pi * representative[1] / SIZE
        center = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
        eigenvalues, eigenvectors = np.linalg.eig(center)
        inverse_candidate = np.linalg.inv(eigenvectors)
        if representative in SELECTED_WAVES:
            selected_indices = tuple(
                int(index)
                for index in np.argsort(np.abs(eigenvalues))[::-1][:3]
            )
        else:
            selected_indices = ()
        for power, wave_index in enumerate(orbit.members):
            transported_vectors, transported_inverse = _transport_preconditioner(
                eigenvectors,
                inverse_candidate,
                power,
            )
            proofs[wave_index] = _certify_transported_block(
                wave_index,
                symbols[wave_index],
                eigenvalues,
                transported_vectors,
                transported_inverse,
                selected_indices,
            )

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
        proof for wave, proof in proofs.items() if wave != (0, 0)
    )
    selected_proofs = tuple(proofs[wave] for wave in sorted(SELECTED_WAVES))
    maximum_trig_width = max(
        value.width for pair in trig.values() for value in pair
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
    orbit_transport, maximum_transport_difference = _orbit_consistency_audit(
        orbits,
        proofs,
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
        },
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
        "input_artifacts": input_records,
        "orbit_transport": orbit_transport,
        "symbol_covariance": covariance,
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
        "registered_inputs": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": "Q007h sealed failure and Q007g source/scope records match",
            "value": {
                name: record["passed"] for name, record in input_records.items()
            },
        },
        "registered_orbit_partition": {
            "passed": bool(
                orbit_transport["orbit_count"] == EXPECTED_ORBIT_COUNT
                and orbit_transport["nonzero_orbit_count"]
                == EXPECTED_NONZERO_ORBIT_COUNT
                and orbit_transport["nonzero_member_count"]
                == EXPECTED_NONZERO_MEMBER_COUNT
            ),
            "threshold": "73 total orbits, 72 nonzero representatives, 288 members",
            "value": {
                "orbit_count": orbit_transport["orbit_count"],
                "nonzero_orbit_count": orbit_transport["nonzero_orbit_count"],
                "nonzero_member_count": orbit_transport["nonzero_member_count"],
            },
        },
        "exact_symbol_covariance": {
            "passed": covariance["entrywise_exact"],
            "threshold": "all 289 C4 symbol edges match entrywise as rational rectangles",
            "value": covariance["mismatch_entry_count"],
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
                all(
                    math.isfinite(float(proof.bauer_fike_radius))
                    for proof in nonzero_proofs
                )
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
        "exact_c4_transport": {
            "passed": bool(
                maximum_transport_difference == 0
                and maximum_symmetry_difference == 0
            ),
            "threshold": "transported epsilon/beta/radius and all symmetry endpoints equal exactly",
            "value": {
                "maximum_transport_parameter_difference": float(
                    maximum_transport_difference
                ),
                "maximum_symmetry_endpoint_difference": float(
                    maximum_symmetry_difference
                ),
            },
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
        classification = "registered symmetry-equivariant rational audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered symmetry-equivariant linear spectral split and "
            "degree-90 tail certified"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered symmetry-equivariant linear certification failed"
        )

    return {
        "question": (
            "Does exact C4 transport remove the independent-preconditioner "
            "mismatch while preserving every Q007h rational spectral gate?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "tail_degree": TAIL_DEGREE,
            "quarter_turn_mapping": list(QUARTER_TURN_MAPPING),
            "quarter_turn_permutation_matrix": _permutation_matrix(),
        },
        "input_artifacts": input_records,
        "orbit_transport": orbit_transport,
        "symbol_covariance": covariance,
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
            "This certifies only the linear spectral layer of the fixed 17x17 "
            "filtered map. It does not certify degrees 2--89 nonresonance, a "
            "Riesz projector norm, a nonlinear proof radius, manifold existence "
            "or uniqueness, or grid-uniform attraction."
        ),
        "preserved_prior_outcomes": {
            "q007h_inconclusive_result_changed": False,
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
            "q007g_theorem_readiness_classification_changed": False,
        },
        "next_change": (
            "Q007i will distinguish direct full-spectrum from "
            "translation-equivariant external nonresonance at degrees 2--89."
        ),
        "sealed_predecessor_outcome": {
            "q007h_study_gate": q007h["study_gate"],
            "q007h_scientific_outcome": q007h["scientific_outcome"],
        },
    }
