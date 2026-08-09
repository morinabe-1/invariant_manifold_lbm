"""Q011k rigorous interval spectrum for the repaired forced fixed point."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np
import numpy.typing as npt
from scipy.optimize import linear_sum_assignment

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011j_interval_fixed_point as q011j
from research.q007x_mpfr_backend import fraction_from_mpfr
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    ComplexRationalInterval,
    RationalInterval,
    _all_numeric_values_finite,
    _canonical_index,
    _complex_absolute_bounds,
    _complex_point,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
    machin_pi_interval,
    trigonometric_intervals,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
ExactMatrix = list[list[Fraction]]
IntervalMatrix = list[list[RationalInterval]]

SIZE = 17
STRIPE_DIMENSION = 153
COORDINATE_DIMENSION = 150
FIXED_LEAF_DIMENSION = 2598
REPRESENTATIVE_BLOCKS = tuple(range(9))
SELECTED_BLOCK_DIMENSIONS = {0: 6, 1: 9, 16: 9}
EXPECTED_SELECTED_COUNT = 24
EXPECTED_EXTERNAL_COUNT = 2574
EXPECTED_QUADRATIC_PAIR_COUNT = 300

PRIMARY_PRECISION_BITS = 256
REPLAY_PRECISION_BITS = 384
ROOT_RADIUS_CAP = Fraction(2, 10**15)
MAXIMUM_INVERSE_DEFECT = Fraction(1, 10**8)
SPECTRAL_RADIUS_CEILING = Fraction(9999, 10000)
MINIMUM_DISC_SPLIT_GAP = Fraction(1, 10**6)
MINIMUM_NORMAL_DOMINANCE_GAP = Fraction(1, 10**6)
MINIMUM_QUADRATIC_DISTANCE = Fraction(1, 10**6)
MAXIMUM_SELECTED_MATCHING_DISTANCE = 1.0e-10
MAXIMUM_POINT_BLOCK_DISCREPANCY = Fraction(1, 10**12)
MAXIMUM_CONJUGATE_BLOCK_DISCREPANCY = 1.0e-12
MAXIMUM_CONJUGATE_SPECTRUM_DISCREPANCY = 1.0e-10

Q011J_ARTIFACT_SHA256 = "74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a"
Q011J_RUNNER_SHA256 = "23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5"
Q011J_DIGESTS = (
    "a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799",
    "adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b",
    "177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f",
    "1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0",
    "ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934",
)
Q011C2_ARTIFACT_SHA256 = "c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a"
Q011C2_RUNNER_SHA256 = "87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2"
Q011C2_DIGESTS = (
    "de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2",
    "36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d",
    "d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72",
    "8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8",
    "8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c",
)


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _maximum_absolute(interval: RationalInterval) -> Fraction:
    return max(abs(interval.lower), abs(interval.upper))


def _complex_rectangle_l1_upper(value: ComplexRationalInterval) -> Fraction:
    """Cheap exact upper for the complex modulus of one rectangle."""

    return value.real.maximum_absolute_value + value.imag.maximum_absolute_value


def _complex_record(value: complex) -> dict[str, float]:
    number = complex(value)
    return {"real": float(number.real), "imag": float(number.imag)}


def _complex_from_record(record: dict[str, Any]) -> complex:
    return complex(float(record["real"]), float(record["imag"]))


def _selected_endpoint_records(q011c2_artifact: dict[str, Any]) -> dict[int, ComplexArray]:
    endpoint = q011c2_artifact["cycle"]["fine_cluster_path_audit"]["forward_node_records"][-1]
    if float(endpoint["amplitude_factor"]) != 1.0:
        raise ValueError("Q011c2 final endpoint is not the registered factor one")
    records: dict[int, ComplexArray] = {}
    for block in endpoint["block_records"]:
        index = int(block["block_index"])
        records[index] = np.asarray(
            [_complex_from_record(value) for value in block["selected_eigenvalues"]],
            dtype=np.complex128,
        )
    return records


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    directory = _artifact_directory()
    q011j_path = directory / "q011j_interval_fixed_point.json"
    q011c2_path = directory / "q011c2_heldout_cluster_reissue.json"
    q011j_artifact = json.loads(q011j_path.read_text(encoding="utf-8"))
    q011c2_artifact = json.loads(q011c2_path.read_text(encoding="utf-8"))
    q011j_cycle = q011j_artifact["cycle"]
    q011c2_cycle = q011c2_artifact["cycle"]
    q011j_digests = tuple(
        q011j_cycle[name]
        for name in (
            "input_digest_sha256",
            "coordinate_digest_sha256",
            "oracle_digest_sha256",
            "proof_digest_sha256",
            "result_digest_sha256",
        )
    )
    q011c2_digests = tuple(
        q011c2_cycle[name]
        for name in (
            "input_digest_sha256",
            "path_digest_sha256",
            "holdout_spectrum_digest_sha256",
            "endpoint_digest_sha256",
            "result_digest_sha256",
        )
    )
    selected = _selected_endpoint_records(q011c2_artifact)
    selected_dimensions = {index: int(values.size) for index, values in selected.items()}
    q011j_claim = q011j_cycle.get("claim_boundary", "")
    q011c2_claim = q011c2_cycle.get("claim_boundary", "")
    checks = {
        "q011j_artifact_sha256_matches": _file_sha256(q011j_path) == Q011J_ARTIFACT_SHA256,
        "q011j_runner_sha256_matches": (
            q011j_cycle["runner_source"]["sha256"] == Q011J_RUNNER_SHA256
        ),
        "q011j_digests_match": q011j_digests == Q011J_DIGESTS,
        "q011j_accepted_fixed_point_proof_reproduces": (
            q011j_cycle["study_validity"] == "passed"
            and q011j_cycle["hypothesis_outcome"] == "accepted"
            and len(q011j_cycle["validity_gates"]) == 6
            and len(q011j_cycle["hypothesis_gates"]) == 4
            and all(gate["passed"] for gate in q011j_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in q011j_cycle["hypothesis_gates"].values())
        ),
        "q011j_claim_boundary_reproduces": (
            "does not certify the raw" in q011j_claim
            and "enclose the spectrum" in q011j_claim
            and "normal attraction" in q011j_claim
        ),
        "q011c2_artifact_sha256_matches": (_file_sha256(q011c2_path) == Q011C2_ARTIFACT_SHA256),
        "q011c2_runner_sha256_matches": (
            q011c2_cycle["runner_source"]["sha256"] == Q011C2_RUNNER_SHA256
        ),
        "q011c2_digests_match": q011c2_digests == Q011C2_DIGESTS,
        "q011c2_accepted_cluster_reissue_reproduces": (
            q011c2_cycle["study_validity"] == "passed"
            and q011c2_cycle["hypothesis_outcome"] == "accepted"
            and all(gate["passed"] for gate in q011c2_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in q011c2_cycle["hypothesis_gates"].values())
        ),
        "q011c2_selected_endpoint_dimensions_match": (
            selected_dimensions == SELECTED_BLOCK_DIMENSIONS
            and sum(selected_dimensions.values()) == EXPECTED_SELECTED_COUNT
        ),
        "q011c2_claim_boundary_reproduces": (
            "does not alter Q011c" in q011c2_claim
            and "rigorous projector" in q011c2_claim
            and "normal attraction" in q011c2_claim
        ),
        "package_source_matches_both_inputs": (
            q011j_artifact["source"] == source_metadata()
            and q011c2_artifact["source"] == source_metadata()
        ),
    }
    audit = {
        "q011j_artifact": {
            "filename": q011j_path.name,
            "sha256": _file_sha256(q011j_path),
            "runner_sha256": q011j_cycle["runner_source"]["sha256"],
            "digests": list(q011j_digests),
            "study_validity": q011j_cycle["study_validity"],
            "hypothesis_outcome": q011j_cycle["hypothesis_outcome"],
            "scientific_classification": q011j_cycle["scientific_classification"],
        },
        "q011c2_artifact": {
            "filename": q011c2_path.name,
            "sha256": _file_sha256(q011c2_path),
            "runner_sha256": q011c2_cycle["runner_source"]["sha256"],
            "digests": list(q011c2_digests),
            "study_validity": q011c2_cycle["study_validity"],
            "hypothesis_outcome": q011c2_cycle["hypothesis_outcome"],
            "scientific_classification": q011c2_cycle["scientific_classification"],
            "selected_endpoint_dimensions": {
                str(index): dimension for index, dimension in selected_dimensions.items()
            },
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, q011j_artifact, q011c2_artifact


def _root_enclosure_audit(
    q011j_artifact: dict[str, Any],
) -> tuple[
    list[Fraction],
    list[Fraction],
    npt.NDArray[np.int64],
    list[RationalInterval],
    Fraction,
    dict[str, Any],
]:
    proof = q011j_artifact["cycle"]["interval_krawczyk_proof_audit"]
    primary = proof["primary_precision_audit"]
    replay = proof["replay_precision_audit"]
    selected_radius = _fraction_from_record(proof["selected_radius"])

    def derived_radius(precision_audit: dict[str, Any]) -> tuple[Fraction, Fraction, Fraction]:
        correction = _fraction_from_record(precision_audit["center_correction_infinity_norm_upper"])
        record = next(
            item
            for item in precision_audit["radius_records"]
            if _fraction_from_record(item["radius"]) == selected_radius
        )
        contraction = _fraction_from_record(record["contraction_upper"])
        return correction / (1 - contraction), correction, contraction

    primary_radius, primary_correction, primary_contraction = derived_radius(primary)
    replay_radius, replay_correction, replay_contraction = derived_radius(replay)
    q011i_audit, q011i_artifact = q011j._sealed_q011i_artifact_audit()
    coordinate, lifted, _, lift_matrix, coordinate_audit = q011j._coordinate_audit(q011i_artifact)
    coordinate_box = [
        RationalInterval(value - primary_radius, value + primary_radius) for value in coordinate
    ]
    state_box = q011j._lift_interval(coordinate_box)
    _, densities = q011j._equilibrium_derivative_blocks(state_box)
    minimum_population = min(value.lower for value in state_box)
    minimum_density = min(value.lower for value in densities)
    checks = {
        "q011j_internal_inputs_reproduce": q011i_audit["passed"] and coordinate_audit["passed"],
        "selected_radius_is_registered": selected_radius == Fraction(1, 10**8),
        "primary_contraction_is_strict": primary_contraction < 1,
        "replay_contraction_is_strict": replay_contraction < 1,
        "primary_root_radius_is_within_registered_cap": primary_radius <= ROOT_RADIUS_CAP,
        "replay_root_radius_is_contained": replay_radius <= primary_radius,
        "replay_correction_and_contraction_are_contained": (
            replay_correction <= primary_correction and replay_contraction <= primary_contraction
        ),
        "lifted_root_box_has_positive_population": minimum_population > 0,
        "lifted_root_box_has_positive_density": minimum_density > 0,
        "lift_infinity_norm_reproduces": (int(np.max(np.sum(np.abs(lift_matrix), axis=1))) == 186),
    }
    audit = {
        "selected_q011j_radius": _fraction_record(selected_radius),
        "primary_center_correction_upper": _fraction_record(primary_correction),
        "primary_contraction_upper": _fraction_record(primary_contraction),
        "primary_root_coordinate_radius_upper": _fraction_record(primary_radius),
        "replay_center_correction_upper": _fraction_record(replay_correction),
        "replay_contraction_upper": _fraction_record(replay_contraction),
        "replay_root_coordinate_radius_upper": _fraction_record(replay_radius),
        "ambient_population_component_radius_upper": _fraction_record(186 * primary_radius),
        "minimum_population_lower": _fraction_record(minimum_population),
        "minimum_density_lower": _fraction_record(minimum_density),
        "coordinate_exact_sha256": q011j._fraction_sequence_sha256(coordinate),
        "lifted_center_exact_sha256": q011j._fraction_sequence_sha256(lifted),
        "lift_matrix_sha256": q011j.q011i.q011b._array_sha256(lift_matrix),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return coordinate, lifted, lift_matrix, state_box, primary_radius, audit


def _collision_derivative_blocks(
    state: list[RationalInterval],
) -> tuple[list[list[list[RationalInterval]]], list[RationalInterval]]:
    equilibrium, densities = q011j._equilibrium_derivative_blocks(state)
    collision = []
    for block in equilibrium:
        collision.append(
            [
                [
                    value.scale(q011j.OMEGA)
                    + RationalInterval.point((Fraction(1) - q011j.OMEGA) * int(row == column))
                    for column, value in enumerate(output_row)
                ]
                for row, output_row in enumerate(block)
            ]
        )
    return collision, densities


def _complex_interval_difference(
    interval: ComplexRationalInterval,
    point: complex,
) -> ComplexRationalInterval:
    number = complex(point)
    return ComplexRationalInterval(
        interval.real - RationalInterval.point(Fraction.from_float(number.real)),
        interval.imag - RationalInterval.point(Fraction.from_float(number.imag)),
    )


def _zero_block_distances(
    family: IntervalMatrix,
    point: ExactMatrix,
    proposal: ComplexArray,
) -> tuple[Fraction, Fraction]:
    family_rows: list[Fraction] = []
    point_rows: list[Fraction] = []
    for row_index, (family_row, point_row) in enumerate(zip(family, point, strict=True)):
        family_sum = Fraction(0)
        point_sum = Fraction(0)
        for column, (family_value, point_value) in enumerate(
            zip(family_row, point_row, strict=True)
        ):
            identity = Fraction(int(row_index == column))
            proposal_value = Fraction.from_float(float(proposal[row_index, column].real))
            family_shifted = family_value + RationalInterval.point(identity)
            exact_shifted = point_value + identity
            family_sum += max(
                abs(family_shifted.lower - proposal_value),
                abs(family_shifted.upper - proposal_value),
            )
            point_sum += abs(exact_shifted - proposal_value)
        family_rows.append(family_sum)
        point_rows.append(point_sum)
    return max(family_rows), max(point_rows)


def _nonzero_block_distances(
    block_index: int,
    family_collision: list[list[list[RationalInterval]]],
    point_collision: list[list[list[RationalInterval]]],
    proposal: ComplexArray,
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
) -> tuple[Fraction, Fraction, int, int]:
    sine, cosine = trig[block_index]
    del sine
    filter_center = RationalInterval.point(Fraction(1) - q011j.ETA) + cosine.scale(q011j.ETA / 2)
    filter_neighbour = RationalInterval.point(q011j.ETA / 4)
    phases = []
    for cx, _ in q011j.VELOCITIES:
        phase_sine, phase_cosine = trig[_canonical_index(block_index * cx)]
        phases.append(ComplexRationalInterval(phase_cosine, -phase_sine))

    family_maximum = Fraction(0)
    point_maximum = Fraction(0)
    minimum_nonzeros = STRIPE_DIMENSION
    maximum_nonzeros = 0
    zero = ComplexRationalInterval.zero()
    for site in range(SIZE):
        for population, (_, cy) in enumerate(q011j.VELOCITIES):
            output_row = site * 9 + population
            family_entries: dict[int, ComplexRationalInterval] = {}
            point_entries: dict[int, ComplexRationalInterval] = {}
            sources = (
                ((site - cy) % SIZE, filter_center),
                ((site - 1 - cy) % SIZE, filter_neighbour),
                ((site + 1 - cy) % SIZE, filter_neighbour),
            )
            for source_site, filter_weight in sources:
                for input_population in range(9):
                    column = source_site * 9 + input_population
                    family_real = (
                        family_collision[source_site][population][input_population] * filter_weight
                    )
                    point_real = (
                        point_collision[source_site][population][input_population] * filter_weight
                    )
                    family_entries[column] = phases[population] * ComplexRationalInterval(
                        family_real, RationalInterval.point(0)
                    )
                    point_entries[column] = phases[population] * ComplexRationalInterval(
                        point_real, RationalInterval.point(0)
                    )
            minimum_nonzeros = min(minimum_nonzeros, len(family_entries))
            maximum_nonzeros = max(maximum_nonzeros, len(family_entries))
            family_sum = Fraction(0)
            point_sum = Fraction(0)
            for column, interval in family_entries.items():
                difference = _complex_interval_difference(interval, proposal[output_row, column])
                family_sum += _complex_rectangle_l1_upper(difference)
                point_difference = _complex_interval_difference(
                    point_entries[column], proposal[output_row, column]
                )
                point_sum += _complex_rectangle_l1_upper(point_difference)
            for column in range(STRIPE_DIMENSION):
                if column in family_entries:
                    continue
                value = complex(proposal[output_row, column])
                family_sum += abs(Fraction.from_float(value.real)) + abs(
                    Fraction.from_float(value.imag)
                )
                point_sum += _complex_rectangle_l1_upper(_complex_interval_difference(zero, value))
            family_maximum = max(family_maximum, family_sum)
            point_maximum = max(point_maximum, point_sum)
    return family_maximum, point_maximum, minimum_nonzeros, maximum_nonzeros


def _spectrum_hausdorff(left: ComplexArray, right: ComplexArray) -> float:
    distances = np.abs(left[:, None] - right[None, :])
    return float(
        max(
            np.max(np.min(distances, axis=1)),
            np.max(np.min(distances, axis=0)),
        )
    )


def _block_family_audit(
    coordinate: list[Fraction],
    lifted: list[Fraction],
    lift_matrix: npt.NDArray[np.int64],
    state_box: list[RationalInterval],
) -> tuple[dict[int, ComplexArray], dict[int, Fraction], dict[str, Any]]:
    point_state = [RationalInterval.point(value) for value in lifted]
    family_collision, family_densities = _collision_derivative_blocks(state_box)
    point_collision, point_densities = _collision_derivative_blocks(point_state)
    family_sparse, family_pivot, _ = q011j._reduced_derivative_factors(state_box)
    point_sparse, point_pivot, _ = q011j._reduced_derivative_factors(point_state)
    family_zero = q011j._combine_reduced_factors(family_sparse, family_pivot, lift_matrix)
    point_zero = q011j._point_matrix(
        q011j._combine_reduced_factors(point_sparse, point_pivot, lift_matrix)
    )

    source_exact, source_float, source_audit = q011j._repaired_source_exact()
    _, oracle_jacobian, _, _, oracle_audit = q011j._oracle_audit(
        coordinate,
        lifted,
        lift_matrix,
        source_exact,
        source_float,
    )
    point_zero_matches_oracle = point_zero == oracle_jacobian
    zero_proposal = np.asarray(point_zero, dtype=np.float64) + np.eye(
        COORDINATE_DIMENSION, dtype=np.float64
    )
    state_float = np.asarray([float(value) for value in lifted], dtype=np.float64).reshape(
        SIZE, 1, 9
    )
    proposals: dict[int, ComplexArray] = {0: zero_proposal.astype(np.complex128)}
    for block_index in range(1, SIZE):
        proposals[block_index] = q011b._block_matrix(
            state_float,
            2.0 * np.pi * block_index / SIZE,
        )

    zero_family_distance, zero_point_distance = _zero_block_distances(
        family_zero,
        point_zero,
        proposals[0],
    )
    trig = trigonometric_intervals(machin_pi_interval())
    deltas: dict[int, Fraction] = {0: zero_family_distance}
    records: list[dict[str, Any]] = [
        {
            "block_index": 0,
            "transported_from": None,
            "dimension": COORDINATE_DIMENSION,
            "interval_family_distance_infinity_upper": _fraction_record(zero_family_distance),
            "point_proposal_distance_infinity_upper": _fraction_record(zero_point_distance),
            "minimum_sparse_nonzeros_per_row": None,
            "maximum_sparse_nonzeros_per_row": None,
            "proposal_sha256": q011b._array_sha256(proposals[0]),
        }
    ]
    representative_point_distances = [zero_point_distance]
    for block_index in range(1, 9):
        family_distance, point_distance, minimum_nonzeros, maximum_nonzeros = (
            _nonzero_block_distances(
                block_index,
                family_collision,
                point_collision,
                proposals[block_index],
                trig,
            )
        )
        deltas[block_index] = family_distance
        conjugate_index = SIZE - block_index
        deltas[conjugate_index] = family_distance
        representative_point_distances.append(point_distance)
        records.append(
            {
                "block_index": block_index,
                "transported_from": None,
                "dimension": STRIPE_DIMENSION,
                "interval_family_distance_infinity_upper": _fraction_record(family_distance),
                "point_proposal_distance_infinity_upper": _fraction_record(point_distance),
                "minimum_sparse_nonzeros_per_row": minimum_nonzeros,
                "maximum_sparse_nonzeros_per_row": maximum_nonzeros,
                "proposal_sha256": q011b._array_sha256(proposals[block_index]),
            }
        )
        records.append(
            {
                "block_index": conjugate_index,
                "transported_from": block_index,
                "dimension": STRIPE_DIMENSION,
                "interval_family_distance_infinity_upper": _fraction_record(family_distance),
                "point_proposal_distance_infinity_upper": _fraction_record(point_distance),
                "minimum_sparse_nonzeros_per_row": minimum_nonzeros,
                "maximum_sparse_nonzeros_per_row": maximum_nonzeros,
                "proposal_sha256": q011b._array_sha256(proposals[conjugate_index]),
            }
        )
    records.sort(key=lambda record: int(record["block_index"]))

    conjugate_matrix_discrepancies = []
    conjugate_spectrum_discrepancies = []
    for block_index in range(1, 9):
        conjugate_index = SIZE - block_index
        conjugate_matrix_discrepancies.append(
            float(
                np.linalg.norm(
                    proposals[conjugate_index] - np.conjugate(proposals[block_index]),
                    ord=np.inf,
                )
            )
        )
        conjugate_spectrum_discrepancies.append(
            _spectrum_hausdorff(
                np.linalg.eigvals(proposals[conjugate_index]),
                np.conjugate(np.linalg.eigvals(proposals[block_index])),
            )
        )
    maximum_conjugate_matrix = max(conjugate_matrix_discrepancies)
    maximum_conjugate_spectrum = max(conjugate_spectrum_discrepancies)
    maximum_point_distance = max(representative_point_distances)
    maximum_trigonometric_width = max(value.width for pair in trig.values() for value in pair)
    trigonometric_conjugacy_exact = all(
        trig[-index][0] == -trig[index][0] and trig[-index][1] == trig[index][1]
        for index in range(1, 9)
    )
    dimension_count = COORDINATE_DIMENSION + (SIZE - 1) * STRIPE_DIMENSION
    checks = {
        "source_and_exact_oracle_reproduce": source_audit["passed"] and oracle_audit["passed"],
        "zero_block_point_matrix_matches_q011j_oracle": point_zero_matches_oracle,
        "all_seventeen_blocks_are_present": (
            sorted(proposals) == list(range(SIZE))
            and sorted(deltas) == list(range(SIZE))
            and len(records) == SIZE
        ),
        "fixed_leaf_dimension_is_registered": dimension_count == FIXED_LEAF_DIMENSION,
        "all_family_distances_are_finite_and_positive": all(
            value > 0 and np.isfinite(float(value)) for value in deltas.values()
        ),
        "all_point_proposal_distances_are_within_threshold": (
            maximum_point_distance <= MAXIMUM_POINT_BLOCK_DISCREPANCY
        ),
        "nonzero_blocks_have_registered_sparse_row_structure": all(
            record["minimum_sparse_nonzeros_per_row"] == 27
            and record["maximum_sparse_nonzeros_per_row"] == 27
            for record in records
            if record["block_index"] != 0
        ),
        "conjugate_block_matrices_reproduce": (
            maximum_conjugate_matrix <= MAXIMUM_CONJUGATE_BLOCK_DISCREPANCY
        ),
        "conjugate_block_spectra_reproduce": (
            maximum_conjugate_spectrum <= MAXIMUM_CONJUGATE_SPECTRUM_DISCREPANCY
        ),
        "transported_interval_distances_are_exact": all(
            deltas[index] == deltas[SIZE - index] for index in range(1, 9)
        ),
        "trigonometric_conjugacy_is_exact": trigonometric_conjugacy_exact,
        "root_box_density_is_strictly_positive": (
            min(value.lower for value in family_densities) > 0
            and min(value.lower for value in point_densities) > 0
        ),
    }
    audit = {
        "block_count": len(proposals),
        "zero_block_dimension": COORDINATE_DIMENSION,
        "nonzero_block_dimension": STRIPE_DIMENSION,
        "fixed_leaf_dimension": dimension_count,
        "representative_blocks": list(REPRESENTATIVE_BLOCKS),
        "transported_conjugate_blocks": list(range(9, SIZE)),
        "trigonometric_protocol": {
            "machin_terms_per_arctangent": 96,
            "trigonometric_taylor_terms": 64,
            "taylor_remainder": "degree-127 Lagrange bound |x|^128 / 128!",
            "maximum_interval_width": _fraction_record(maximum_trigonometric_width),
        },
        "maximum_point_proposal_distance_infinity_upper": _fraction_record(maximum_point_distance),
        "maximum_interval_family_distance_infinity_upper": _fraction_record(max(deltas.values())),
        "maximum_conjugate_block_infinity_discrepancy": maximum_conjugate_matrix,
        "maximum_conjugate_spectrum_hausdorff_discrepancy": maximum_conjugate_spectrum,
        "block_records": records,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return proposals, deltas, audit


def _canonical_eigendecomposition(
    matrix: ComplexArray,
) -> tuple[ComplexArray, ComplexArray, ComplexArray, dict[str, Any]]:
    eigenvalues, eigenvectors = np.linalg.eig(np.asarray(matrix, dtype=np.complex128))
    order = sorted(
        range(eigenvalues.size),
        key=lambda index: (
            float(eigenvalues[index].real),
            float(eigenvalues[index].imag),
            index,
        ),
    )
    values = np.asarray(eigenvalues[order], dtype=np.complex128)
    vectors = np.asarray(eigenvectors[:, order], dtype=np.complex128).copy()
    pivot_indices = []
    for column in range(vectors.shape[1]):
        vector = vectors[:, column]
        pivot = int(np.argmax(np.abs(vector)))
        pivot_indices.append(pivot)
        pivot_value = complex(vector[pivot])
        if pivot_value == 0:
            raise ValueError("eigenvector phase pivot is zero")
        phase = pivot_value / abs(pivot_value)
        vectors[:, column] = vector / phase
        vectors[pivot, column] = complex(abs(pivot_value), 0.0)
    inverse = np.linalg.inv(vectors)
    replay_values, replay_vectors, replay_inverse, _ = _canonical_eigendecomposition_once(matrix)
    checks = {
        "all_values_and_vectors_are_finite": bool(
            np.all(np.isfinite(values))
            and np.all(np.isfinite(vectors))
            and np.all(np.isfinite(inverse))
        ),
        "pivot_entries_are_nonnegative_real": all(
            vectors[pivot, column].real >= 0.0 and vectors[pivot, column].imag == 0.0
            for column, pivot in enumerate(pivot_indices)
        ),
        "deterministic_replay_is_bitwise": (
            np.array_equal(values, replay_values)
            and np.array_equal(vectors, replay_vectors)
            and np.array_equal(inverse, replay_inverse)
        ),
    }
    audit = {
        "dimension": int(values.size),
        "eigenvalues_sha256": q011b._array_sha256(values),
        "eigenvectors_sha256": q011b._array_sha256(vectors),
        "inverse_candidate_sha256": q011b._array_sha256(inverse),
        "pivot_indices_sha256": q011b._array_sha256(np.asarray(pivot_indices, dtype=np.int64)),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return values, vectors, inverse, audit


def _canonical_eigendecomposition_once(
    matrix: ComplexArray,
) -> tuple[ComplexArray, ComplexArray, ComplexArray, tuple[int, ...]]:
    eigenvalues, eigenvectors = np.linalg.eig(np.asarray(matrix, dtype=np.complex128))
    order = sorted(
        range(eigenvalues.size),
        key=lambda index: (
            float(eigenvalues[index].real),
            float(eigenvalues[index].imag),
            index,
        ),
    )
    values = np.asarray(eigenvalues[order], dtype=np.complex128)
    vectors = np.asarray(eigenvectors[:, order], dtype=np.complex128).copy()
    pivots = []
    for column in range(vectors.shape[1]):
        vector = vectors[:, column]
        pivot = int(np.argmax(np.abs(vector)))
        pivots.append(pivot)
        pivot_value = complex(vector[pivot])
        phase = pivot_value / abs(pivot_value)
        vectors[:, column] = vector / phase
        vectors[pivot, column] = complex(abs(pivot_value), 0.0)
    return values, vectors, np.linalg.inv(vectors), tuple(pivots)


def _complex_mpfr_endpoints(
    array: npt.ArrayLike,
    precision: int,
) -> tuple[
    list[list[gmpy2.mpfr]],
    list[list[gmpy2.mpfr]],
    dict[str, dict[str, bool]],
    bool,
]:
    values = np.asarray(array, dtype=np.complex128)
    if values.ndim == 1:
        values = values.reshape(1, -1)
    if values.ndim != 2:
        raise ValueError("complex MPFR conversion expects a vector or matrix")
    real_fractions = [Fraction.from_float(float(value.real)) for value in values.ravel()]
    imag_fractions = [Fraction.from_float(float(value.imag)) for value in values.ravel()]
    real_lower, real_upper, real_flags = q011j._bulk_endpoint_pairs(real_fractions, precision)
    imag_lower, imag_upper, imag_flags = q011j._bulk_endpoint_pairs(imag_fractions, precision)
    exact = all(
        lower == upper for lower, upper in zip(real_lower, real_upper, strict=True)
    ) and all(lower == upper for lower, upper in zip(imag_lower, imag_upper, strict=True))
    columns = values.shape[1]
    real = [real_lower[row * columns : (row + 1) * columns] for row in range(values.shape[0])]
    imag = [imag_lower[row * columns : (row + 1) * columns] for row in range(values.shape[0])]
    flags = {
        **{f"real_{name}": value for name, value in real_flags.items()},
        **{f"imag_{name}": value for name, value in imag_flags.items()},
    }
    return real, imag, flags, exact


def _complex_sparse_mpfr_endpoints(
    rows: list[list[tuple[int, complex]]],
    precision: int,
) -> tuple[
    list[list[tuple[int, gmpy2.mpfr, gmpy2.mpfr]]],
    dict[str, dict[str, bool]],
    bool,
]:
    flat = [value for row in rows for _, value in row]
    converted_real, converted_imag, flags, exact = _complex_mpfr_endpoints(
        np.asarray(flat, dtype=np.complex128), precision
    )
    real = converted_real[0]
    imag = converted_imag[0]
    output: list[list[tuple[int, gmpy2.mpfr, gmpy2.mpfr]]] = []
    offset = 0
    for row in rows:
        converted_row = []
        for column, _ in row:
            converted_row.append((column, real[offset], imag[offset]))
            offset += 1
        output.append(converted_row)
    return output, flags, exact


def _complex_infinity_norm_upper(
    real: list[list[gmpy2.mpfr]],
    imag: list[list[gmpy2.mpfr]],
    precision: int,
) -> tuple[Fraction, dict[str, bool]]:
    context = q011j._proof_context(precision, gmpy2.RoundUp)
    with context:
        maximum = gmpy2.mpfr(0)
        for real_row, imag_row in zip(real, imag, strict=True):
            total = gmpy2.mpfr(0)
            for real_value, imag_value in zip(real_row, imag_row, strict=True):
                total += gmpy2.sqrt(real_value * real_value + imag_value * imag_value)
            maximum = max(maximum, total)
    return fraction_from_mpfr(maximum), q011j._context_flags(context)


def _directed_inverse_defect(
    inverse_real: list[list[gmpy2.mpfr]],
    inverse_imag: list[list[gmpy2.mpfr]],
    vector_real: list[list[gmpy2.mpfr]],
    vector_imag: list[list[gmpy2.mpfr]],
    precision: int,
) -> tuple[Fraction, str, dict[str, dict[str, bool]], bool]:
    dimension = len(inverse_real)
    lower_context = q011j._proof_context(precision, gmpy2.RoundDown)
    upper_context = q011j._proof_context(precision, gmpy2.RoundUp)
    with lower_context:
        lower_real: list[list[gmpy2.mpfr]] = []
        lower_imag: list[list[gmpy2.mpfr]] = []
        for row in range(dimension):
            real_row = []
            imag_row = []
            for column in range(dimension):
                real_total = gmpy2.mpfr(-int(row == column))
                imag_total = gmpy2.mpfr(0)
                for inner in range(dimension):
                    wr = inverse_real[row][inner]
                    wi = inverse_imag[row][inner]
                    vr = vector_real[inner][column]
                    vi = vector_imag[inner][column]
                    real_total += wr * vr + (-wi) * vi
                    imag_total += wr * vi + wi * vr
                real_row.append(real_total)
                imag_row.append(imag_total)
            lower_real.append(real_row)
            lower_imag.append(imag_row)
    with upper_context:
        upper_real: list[list[gmpy2.mpfr]] = []
        upper_imag: list[list[gmpy2.mpfr]] = []
        for row in range(dimension):
            real_row = []
            imag_row = []
            for column in range(dimension):
                real_total = gmpy2.mpfr(-int(row == column))
                imag_total = gmpy2.mpfr(0)
                for inner in range(dimension):
                    wr = inverse_real[row][inner]
                    wi = inverse_imag[row][inner]
                    vr = vector_real[inner][column]
                    vi = vector_imag[inner][column]
                    real_total += wr * vr + (-wi) * vi
                    imag_total += wr * vi + wi * vr
                real_row.append(real_total)
                imag_row.append(imag_total)
            upper_real.append(real_row)
            upper_imag.append(imag_row)
    norm_context = q011j._proof_context(precision, gmpy2.RoundUp)
    ordered = True
    digest = sha256()
    with norm_context:
        maximum = gmpy2.mpfr(0)
        for row in range(dimension):
            total = gmpy2.mpfr(0)
            for column in range(dimension):
                real_lower = lower_real[row][column]
                real_upper = upper_real[row][column]
                imag_lower = lower_imag[row][column]
                imag_upper = upper_imag[row][column]
                ordered = ordered and real_lower <= real_upper and imag_lower <= imag_upper
                real_absolute = max(-real_lower, real_upper)
                imag_absolute = max(-imag_lower, imag_upper)
                total += gmpy2.sqrt(real_absolute * real_absolute + imag_absolute * imag_absolute)
                for endpoint in (real_lower, real_upper, imag_lower, imag_upper):
                    numerator, denominator = endpoint.as_integer_ratio()
                    digest.update(str(numerator).encode("ascii"))
                    digest.update(b"/")
                    digest.update(str(denominator).encode("ascii"))
                    digest.update(b"\0")
            maximum = max(maximum, total)
    return (
        fraction_from_mpfr(maximum),
        digest.hexdigest(),
        {
            "dot_round_down": q011j._context_flags(lower_context),
            "dot_round_up": q011j._context_flags(upper_context),
            "norm_round_up": q011j._context_flags(norm_context),
        },
        ordered,
    )


def _directed_eigen_residual(
    sparse_matrix: list[list[tuple[int, gmpy2.mpfr, gmpy2.mpfr]]],
    vector_real: list[list[gmpy2.mpfr]],
    vector_imag: list[list[gmpy2.mpfr]],
    value_real: list[gmpy2.mpfr],
    value_imag: list[gmpy2.mpfr],
    precision: int,
) -> tuple[Fraction, str, dict[str, dict[str, bool]], bool]:
    dimension = len(sparse_matrix)
    lower_context = q011j._proof_context(precision, gmpy2.RoundDown)
    upper_context = q011j._proof_context(precision, gmpy2.RoundUp)
    with lower_context:
        lower_real: list[list[gmpy2.mpfr]] = []
        lower_imag: list[list[gmpy2.mpfr]] = []
        for row, sparse_row in enumerate(sparse_matrix):
            real_row = []
            imag_row = []
            for column in range(dimension):
                real_total = gmpy2.mpfr(0)
                imag_total = gmpy2.mpfr(0)
                for inner, ar, ai in sparse_row:
                    vr = vector_real[inner][column]
                    vi = vector_imag[inner][column]
                    real_total += ar * vr + (-ai) * vi
                    imag_total += ar * vi + ai * vr
                vr = vector_real[row][column]
                vi = vector_imag[row][column]
                lr = value_real[column]
                li = value_imag[column]
                real_total += (-vr) * lr + vi * li
                imag_total += (-vr) * li + (-vi) * lr
                real_row.append(real_total)
                imag_row.append(imag_total)
            lower_real.append(real_row)
            lower_imag.append(imag_row)
    with upper_context:
        upper_real: list[list[gmpy2.mpfr]] = []
        upper_imag: list[list[gmpy2.mpfr]] = []
        for row, sparse_row in enumerate(sparse_matrix):
            real_row = []
            imag_row = []
            for column in range(dimension):
                real_total = gmpy2.mpfr(0)
                imag_total = gmpy2.mpfr(0)
                for inner, ar, ai in sparse_row:
                    vr = vector_real[inner][column]
                    vi = vector_imag[inner][column]
                    real_total += ar * vr + (-ai) * vi
                    imag_total += ar * vi + ai * vr
                vr = vector_real[row][column]
                vi = vector_imag[row][column]
                lr = value_real[column]
                li = value_imag[column]
                real_total += (-vr) * lr + vi * li
                imag_total += (-vr) * li + (-vi) * lr
                real_row.append(real_total)
                imag_row.append(imag_total)
            upper_real.append(real_row)
            upper_imag.append(imag_row)
    norm_context = q011j._proof_context(precision, gmpy2.RoundUp)
    ordered = True
    digest = sha256()
    with norm_context:
        maximum = gmpy2.mpfr(0)
        for row in range(dimension):
            total = gmpy2.mpfr(0)
            for column in range(dimension):
                real_lower = lower_real[row][column]
                real_upper = upper_real[row][column]
                imag_lower = lower_imag[row][column]
                imag_upper = upper_imag[row][column]
                ordered = ordered and real_lower <= real_upper and imag_lower <= imag_upper
                real_absolute = max(-real_lower, real_upper)
                imag_absolute = max(-imag_lower, imag_upper)
                total += gmpy2.sqrt(real_absolute * real_absolute + imag_absolute * imag_absolute)
                for endpoint in (real_lower, real_upper, imag_lower, imag_upper):
                    numerator, denominator = endpoint.as_integer_ratio()
                    digest.update(str(numerator).encode("ascii"))
                    digest.update(b"/")
                    digest.update(str(denominator).encode("ascii"))
                    digest.update(b"\0")
            maximum = max(maximum, total)
    return (
        fraction_from_mpfr(maximum),
        digest.hexdigest(),
        {
            "dot_round_down": q011j._context_flags(lower_context),
            "dot_round_up": q011j._context_flags(upper_context),
            "norm_round_up": q011j._context_flags(norm_context),
        },
        ordered,
    )


def _forbidden_flags_clear(flag_groups: dict[str, dict[str, bool]]) -> bool:
    forbidden = ("underflow", "overflow", "invalid", "division_by_zero", "erange")
    return all(not flags[name] for flags in flag_groups.values() for name in forbidden)


def _precision_block_proof(
    proposal: ComplexArray,
    values: ComplexArray,
    vectors: ComplexArray,
    inverse: ComplexArray,
    family_distance: Fraction,
    precision: int,
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    caller_signature = q011j._context_signature(gmpy2.get_context())
    vector_real, vector_imag, vector_flags, vector_exact = _complex_mpfr_endpoints(
        vectors, precision
    )
    inverse_real, inverse_imag, inverse_flags, inverse_exact = _complex_mpfr_endpoints(
        inverse, precision
    )
    values_real_matrix, values_imag_matrix, value_flags, values_exact = _complex_mpfr_endpoints(
        values, precision
    )
    value_real = values_real_matrix[0]
    value_imag = values_imag_matrix[0]
    sparse_rows = [
        [
            (column, complex(value))
            for column, value in enumerate(proposal[row])
            if complex(value) != 0j
        ]
        for row in range(proposal.shape[0])
    ]
    sparse_mpfr, sparse_flags, sparse_exact = _complex_sparse_mpfr_endpoints(sparse_rows, precision)
    vector_norm, vector_norm_flags = _complex_infinity_norm_upper(
        vector_real, vector_imag, precision
    )
    inverse_norm, inverse_norm_flags = _complex_infinity_norm_upper(
        inverse_real, inverse_imag, precision
    )
    inverse_defect, inverse_digest, inverse_product_flags, inverse_ordered = (
        _directed_inverse_defect(
            inverse_real,
            inverse_imag,
            vector_real,
            vector_imag,
            precision,
        )
    )
    point_residual, residual_digest, residual_flags, residual_ordered = _directed_eigen_residual(
        sparse_mpfr,
        vector_real,
        vector_imag,
        value_real,
        value_imag,
        precision,
    )
    if inverse_defect >= 1:
        beta = Fraction(10**1000)
    else:
        beta = inverse_norm / (1 - inverse_defect)
    family_residual = point_residual + family_distance * vector_norm
    bauer_fike_radius = vector_norm * beta * beta * family_residual
    flag_groups = {
        **{f"vector_{name}": value for name, value in vector_flags.items()},
        **{f"inverse_{name}": value for name, value in inverse_flags.items()},
        **{f"value_{name}": value for name, value in value_flags.items()},
        **{f"sparse_{name}": value for name, value in sparse_flags.items()},
        "vector_norm_round_up": vector_norm_flags,
        "inverse_norm_round_up": inverse_norm_flags,
        **{f"inverse_product_{name}": value for name, value in inverse_product_flags.items()},
        **{f"residual_{name}": value for name, value in residual_flags.items()},
    }
    conversions_exact = vector_exact and inverse_exact and values_exact and sparse_exact
    caller_unchanged = q011j._context_signature(gmpy2.get_context()) == caller_signature
    checks = {
        "all_binary64_inputs_convert_exactly": conversions_exact,
        "inverse_defect_intervals_are_ordered": inverse_ordered,
        "eigen_residual_intervals_are_ordered": residual_ordered,
        "no_forbidden_mpfr_flags": _forbidden_flags_clear(flag_groups),
        "caller_context_is_unchanged": caller_unchanged,
        "inverse_defect_is_strictly_below_one": inverse_defect < 1,
    }
    record = {
        "precision_bits": precision,
        "vector_infinity_norm_upper": _fraction_record(vector_norm),
        "inverse_candidate_infinity_norm_upper": _fraction_record(inverse_norm),
        "inverse_defect_infinity_norm_upper": _fraction_record(inverse_defect),
        "certified_inverse_infinity_norm_upper": _fraction_record(beta),
        "point_eigendecomposition_residual_infinity_upper": _fraction_record(point_residual),
        "interval_family_distance_infinity_upper": _fraction_record(family_distance),
        "family_eigendecomposition_residual_infinity_upper": _fraction_record(family_residual),
        "bauer_fike_radius_upper": _fraction_record(bauer_fike_radius),
        "inverse_defect_interval_sha256": inverse_digest,
        "eigen_residual_interval_sha256": residual_digest,
        "nonzero_proposal_entry_count": sum(len(row) for row in sparse_rows),
        "mpfr_flag_groups": flag_groups,
        "checks": checks,
        "passed": all(checks.values()),
    }
    exact = {
        "vector_norm": vector_norm,
        "inverse_norm": inverse_norm,
        "inverse_defect": inverse_defect,
        "beta": beta,
        "point_residual": point_residual,
        "family_residual": family_residual,
        "bauer_fike_radius": bauer_fike_radius,
    }
    return record, exact


def _precision_containment(
    primary: dict[str, Fraction],
    replay: dict[str, Fraction],
) -> bool:
    return all(replay[name] <= primary[name] for name in primary)


def _spectral_proof_audit(
    proposals: dict[int, ComplexArray],
    family_distances: dict[int, Fraction],
) -> tuple[dict[int, ComplexArray], dict[int, Fraction], dict[str, Any]]:
    representative_values: dict[int, ComplexArray] = {}
    representative_radii: dict[int, Fraction] = {}
    records: list[dict[str, Any]] = []
    primary_exact_records: dict[int, dict[str, Fraction]] = {}
    replay_exact_records: dict[int, dict[str, Fraction]] = {}
    all_eigendecompositions_pass = True
    for block_index in REPRESENTATIVE_BLOCKS:
        values, vectors, inverse, eig_audit = _canonical_eigendecomposition(proposals[block_index])
        primary, primary_exact = _precision_block_proof(
            proposals[block_index],
            values,
            vectors,
            inverse,
            family_distances[block_index],
            PRIMARY_PRECISION_BITS,
        )
        replay, replay_exact = _precision_block_proof(
            proposals[block_index],
            values,
            vectors,
            inverse,
            family_distances[block_index],
            REPLAY_PRECISION_BITS,
        )
        containment = _precision_containment(primary_exact, replay_exact)
        representative_values[block_index] = values
        representative_radii[block_index] = primary_exact["bauer_fike_radius"]
        primary_exact_records[block_index] = primary_exact
        replay_exact_records[block_index] = replay_exact
        all_eigendecompositions_pass = all_eigendecompositions_pass and eig_audit["passed"]
        checks = {
            "canonical_eigendecomposition_reproduces": eig_audit["passed"],
            "primary_outward_protocol_passes": primary["passed"],
            "replay_outward_protocol_passes": replay["passed"],
            "higher_precision_uppers_are_contained": containment,
        }
        records.append(
            {
                "block_index": block_index,
                "dimension": int(values.size),
                "eigendecomposition": eig_audit,
                "eigenvalue_centers": [_complex_record(value) for value in values],
                "primary_precision_proof": primary,
                "replay_precision_proof": replay,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    centers: dict[int, ComplexArray] = {0: representative_values[0]}
    radii: dict[int, Fraction] = {0: representative_radii[0]}
    for block_index in range(1, 9):
        centers[block_index] = representative_values[block_index]
        radii[block_index] = representative_radii[block_index]
        conjugate_index = SIZE - block_index
        centers[conjugate_index] = np.conjugate(representative_values[block_index])
        radii[conjugate_index] = representative_radii[block_index]

    maximum_inverse_defect = max(
        exact["inverse_defect"] for exact in primary_exact_records.values()
    )
    maximum_radius = max(representative_radii.values())
    maximum_family_distance = max(family_distances.values())
    maximum_point_residual = max(
        exact["point_residual"] for exact in primary_exact_records.values()
    )
    worst_radius_block = max(representative_radii, key=lambda index: representative_radii[index])
    all_protocols_pass = all(record["passed"] for record in records)
    all_inverse_defects_within_bound = all(
        exact["inverse_defect"] <= MAXIMUM_INVERSE_DEFECT
        for exact in primary_exact_records.values()
    ) and all(
        exact["inverse_defect"] <= MAXIMUM_INVERSE_DEFECT for exact in replay_exact_records.values()
    )
    protocol_checks = {
        "all_nine_representative_eigendecompositions_are_complete": (
            len(records) == len(REPRESENTATIVE_BLOCKS) == 9 and all_eigendecompositions_pass
        ),
        "all_primary_and_replay_protocols_pass": all_protocols_pass,
        "all_higher_precision_uppers_are_contained": all(
            record["checks"]["higher_precision_uppers_are_contained"] for record in records
        ),
        "all_seventeen_center_and_radius_sets_are_present": (
            sorted(centers) == list(range(SIZE))
            and sorted(radii) == list(range(SIZE))
            and sum(values.size for values in centers.values()) == FIXED_LEAF_DIMENSION
        ),
        "transported_radii_match_exactly": all(
            radii[index] == radii[SIZE - index] for index in range(1, 9)
        ),
    }
    hypothesis_checks = {
        "all_inverse_defects_are_within_registered_bound": (all_inverse_defects_within_bound),
    }
    audit = {
        "representative_block_count": len(records),
        "transported_block_count": 8,
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "replay_precision_bits": REPLAY_PRECISION_BITS,
        "maximum_inverse_defect_infinity_norm_upper": _fraction_record(maximum_inverse_defect),
        "maximum_interval_family_distance_infinity_upper": _fraction_record(
            maximum_family_distance
        ),
        "maximum_point_eigendecomposition_residual_infinity_upper": _fraction_record(
            maximum_point_residual
        ),
        "maximum_bauer_fike_radius_upper": _fraction_record(maximum_radius),
        "maximum_bauer_fike_radius_block": worst_radius_block,
        "representative_block_records": records,
        "protocol_checks": protocol_checks,
        "hypothesis_checks": hypothesis_checks,
        "protocol_passed": all(protocol_checks.values()),
        "hypothesis_passed": all(hypothesis_checks.values()),
        "passed": all(protocol_checks.values()),
    }
    return centers, radii, audit


def _exact_complex_point(value: complex) -> ComplexRationalInterval:
    number = complex(value)
    return ComplexRationalInterval.point(
        Fraction.from_float(number.real),
        Fraction.from_float(number.imag),
    )


def _component_maximum_distance_lower(
    left: ComplexRationalInterval,
    right: ComplexRationalInterval,
) -> Fraction:
    difference = left - right
    if difference.real.width != 0 or difference.imag.width != 0:
        raise ValueError("point complex intervals required")
    return max(abs(difference.real.lower), abs(difference.imag.lower))


def _center_modulus_bounds(value: complex) -> RationalInterval:
    return _complex_absolute_bounds(_complex_point(complex(value)))


def _match_selected_centers(
    centers: ComplexArray,
    targets: ComplexArray,
) -> tuple[tuple[int, ...], float, float]:
    distances = np.abs(targets[:, None] - centers[None, :])
    target_rows, center_columns = linear_sum_assignment(distances)
    if sorted(int(value) for value in target_rows) != list(range(targets.size)):
        raise RuntimeError("selected matching did not cover every target")
    selected = tuple(sorted(int(value) for value in center_columns))
    matched = distances[target_rows, center_columns]
    return selected, float(np.max(matched)), float(np.sum(matched))


def _spectral_split_audit(
    centers: dict[int, ComplexArray],
    radii: dict[int, Fraction],
    q011c2_artifact: dict[str, Any],
) -> tuple[dict[str, Any], dict[int, tuple[int, ...]]]:
    endpoint_targets = _selected_endpoint_records(q011c2_artifact)
    selected_indices: dict[int, tuple[int, ...]] = {}
    matching_records = []
    for block_index in sorted(SELECTED_BLOCK_DIMENSIONS):
        indices, maximum_distance, total_distance = _match_selected_centers(
            centers[block_index], endpoint_targets[block_index]
        )
        selected_indices[block_index] = indices
        matching_records.append(
            {
                "block_index": block_index,
                "registered_selected_dimension": SELECTED_BLOCK_DIMENSIONS[block_index],
                "matched_selected_dimension": len(indices),
                "selected_center_indices": list(indices),
                "maximum_matching_distance": maximum_distance,
                "total_matching_distance": total_distance,
                "passed": (
                    len(indices) == SELECTED_BLOCK_DIMENSIONS[block_index]
                    and maximum_distance <= MAXIMUM_SELECTED_MATCHING_DISTANCE
                ),
            }
        )

    modulus_bounds: dict[tuple[int, int], RationalInterval] = {}
    selected_keys: list[tuple[int, int]] = []
    external_keys: list[tuple[int, int]] = []
    maximum_modulus_upper = Fraction(0)
    maximum_modulus_key = (-1, -1)
    for block_index in range(SIZE):
        selected_set = frozenset(selected_indices.get(block_index, ()))
        for center_index, center in enumerate(centers[block_index]):
            center_modulus = _center_modulus_bounds(complex(center))
            radius = radii[block_index]
            interval = RationalInterval(
                max(Fraction(0), center_modulus.lower - radius),
                center_modulus.upper + radius,
            )
            key = (block_index, center_index)
            modulus_bounds[key] = interval
            if center_index in selected_set:
                selected_keys.append(key)
            else:
                external_keys.append(key)
            if interval.upper > maximum_modulus_upper:
                maximum_modulus_upper = interval.upper
                maximum_modulus_key = key

    selected_minimum = min(modulus_bounds[key].lower for key in selected_keys)
    external_maximum = max(modulus_bounds[key].upper for key in external_keys)
    normal_gap = selected_minimum - external_maximum
    split_records = []
    minimum_split_gap: Fraction | None = None
    minimum_split_witness: dict[str, Any] | None = None
    for block_index, selected in sorted(selected_indices.items()):
        external = tuple(
            index for index in range(centers[block_index].size) if index not in selected
        )
        block_minimum: Fraction | None = None
        block_witness = None
        for selected_index in selected:
            selected_center = _exact_complex_point(complex(centers[block_index][selected_index]))
            for external_index in external:
                external_center = _exact_complex_point(
                    complex(centers[block_index][external_index])
                )
                gap = (
                    _component_maximum_distance_lower(selected_center, external_center)
                    - 2 * radii[block_index]
                )
                if block_minimum is None or gap < block_minimum:
                    block_minimum = gap
                    block_witness = {
                        "selected_center_index": selected_index,
                        "external_center_index": external_index,
                    }
        if block_minimum is None or block_witness is None:
            raise RuntimeError("selected split block is empty")
        split_records.append(
            {
                "block_index": block_index,
                "selected_count": len(selected),
                "external_count": len(external),
                "minimum_component_lower_disc_gap": _fraction_record(block_minimum),
                "witness": block_witness,
                "passed": block_minimum >= MINIMUM_DISC_SPLIT_GAP,
            }
        )
        if minimum_split_gap is None or block_minimum < minimum_split_gap:
            minimum_split_gap = block_minimum
            minimum_split_witness = {"block_index": block_index, **block_witness}
    if minimum_split_gap is None:
        raise RuntimeError("no selected split gap was evaluated")

    selected_count = len(selected_keys)
    external_count = len(external_keys)
    maximum_matching = max(record["maximum_matching_distance"] for record in matching_records)
    protocol_checks = {
        "all_three_selected_endpoint_matchings_pass": all(
            record["passed"] for record in matching_records
        ),
        "selected_and_external_counts_are_registered": (
            selected_count == EXPECTED_SELECTED_COUNT
            and external_count == EXPECTED_EXTERNAL_COUNT
            and selected_count + external_count == FIXED_LEAF_DIMENSION
        ),
        "all_modulus_intervals_are_ordered": all(
            interval.lower <= interval.upper for interval in modulus_bounds.values()
        ),
    }
    hypothesis_checks = {
        "all_selected_block_disc_unions_are_separated": all(
            record["passed"] for record in split_records
        ),
    }
    audit = {
        "matching_records": matching_records,
        "maximum_selected_matching_distance": maximum_matching,
        "selected_eigenvalue_count": selected_count,
        "external_eigenvalue_count": external_count,
        "fixed_leaf_eigenvalue_count": selected_count + external_count,
        "maximum_fixed_leaf_modulus_upper": _fraction_record(maximum_modulus_upper),
        "maximum_fixed_leaf_modulus_witness": {
            "block_index": maximum_modulus_key[0],
            "center_index": maximum_modulus_key[1],
        },
        "selected_minimum_modulus_lower": _fraction_record(selected_minimum),
        "external_maximum_modulus_upper": _fraction_record(external_maximum),
        "normal_dominance_gap_lower": _fraction_record(normal_gap),
        "minimum_selected_external_disc_gap_lower": _fraction_record(minimum_split_gap),
        "minimum_selected_external_disc_gap_witness": minimum_split_witness,
        "split_records": split_records,
        "modulus_interval_digest_sha256": q011b._canonical_json_sha256(
            [
                {
                    "block_index": key[0],
                    "center_index": key[1],
                    "lower": _fraction_record(modulus_bounds[key].lower),
                    "upper": _fraction_record(modulus_bounds[key].upper),
                }
                for key in sorted(modulus_bounds)
            ]
        ),
        "protocol_checks": protocol_checks,
        "hypothesis_checks": hypothesis_checks,
        "protocol_passed": all(protocol_checks.values()),
        "hypothesis_passed": all(hypothesis_checks.values()),
        "passed": all(protocol_checks.values()),
    }
    return audit, selected_indices


def _quadratic_nonresonance_audit(
    centers: dict[int, ComplexArray],
    radii: dict[int, Fraction],
    selected_indices: dict[int, tuple[int, ...]],
) -> dict[str, Any]:
    selected = [
        (block_index, center_index, complex(centers[block_index][center_index]))
        for block_index in sorted(selected_indices)
        for center_index in selected_indices[block_index]
    ]
    external_by_block: dict[int, list[tuple[int, complex]]] = {}
    for block_index in range(SIZE):
        selected_set = frozenset(selected_indices.get(block_index, ()))
        external_by_block[block_index] = [
            (center_index, complex(center))
            for center_index, center in enumerate(centers[block_index])
            if center_index not in selected_set
        ]

    selected_modulus_upper = {
        (block_index, center_index): _center_modulus_bounds(center).upper
        for block_index, center_index, center in selected
    }
    pair_records = []
    exact_pair_records = []
    global_minimum: Fraction | None = None
    global_witness: dict[str, Any] | None = None
    comparison_count = 0
    for left_position, left in enumerate(selected):
        left_block, left_index, left_center = left
        left_point = _exact_complex_point(left_center)
        for right in selected[left_position:]:
            right_block, right_index, right_center = right
            right_point = _exact_complex_point(right_center)
            output_block = (left_block + right_block) % SIZE
            product = left_point * right_point
            product_radius = (
                selected_modulus_upper[(left_block, left_index)] * radii[right_block]
                + selected_modulus_upper[(right_block, right_index)] * radii[left_block]
                + radii[left_block] * radii[right_block]
            )
            pair_minimum: Fraction | None = None
            pair_external_index = -1
            for external_index, external_center in external_by_block[output_block]:
                distance = (
                    _component_maximum_distance_lower(
                        product, _exact_complex_point(external_center)
                    )
                    - product_radius
                    - radii[output_block]
                )
                comparison_count += 1
                if pair_minimum is None or distance < pair_minimum:
                    pair_minimum = distance
                    pair_external_index = external_index
            if pair_minimum is None:
                raise RuntimeError("quadratic output sector has no external eigenvalues")
            exact_record = {
                "pair_index": len(pair_records),
                "left": {"block_index": left_block, "center_index": left_index},
                "right": {"block_index": right_block, "center_index": right_index},
                "output_block_index": output_block,
                "external_comparison_count": len(external_by_block[output_block]),
                "product_center": {
                    "real": _fraction_record(product.real.lower),
                    "imag": _fraction_record(product.imag.lower),
                },
                "product_disc_radius_upper": _fraction_record(product_radius),
                "minimum_external_distance_lower": _fraction_record(pair_minimum),
                "minimum_external_center_index": pair_external_index,
                "passed": pair_minimum >= MINIMUM_QUADRATIC_DISTANCE,
            }
            exact_pair_records.append(exact_record)
            record = {
                "pair_index": exact_record["pair_index"],
                "left": exact_record["left"],
                "right": exact_record["right"],
                "output_block_index": output_block,
                "external_comparison_count": exact_record["external_comparison_count"],
                "product_center": {
                    "real": float(product.real.lower),
                    "imag": float(product.imag.lower),
                },
                "product_disc_radius_upper": float(product_radius),
                "minimum_external_distance_lower": float(pair_minimum),
                "minimum_external_center_index": pair_external_index,
                "passed": exact_record["passed"],
            }
            pair_records.append(record)
            if global_minimum is None or pair_minimum < global_minimum:
                global_minimum = pair_minimum
                global_witness = {
                    "pair_index": record["pair_index"],
                    "left": record["left"],
                    "right": record["right"],
                    "output_block_index": output_block,
                    "external_center_index": pair_external_index,
                }
    if global_minimum is None:
        raise RuntimeError("no quadratic pair was evaluated")
    checks = {
        "selected_input_count_is_registered": len(selected) == EXPECTED_SELECTED_COUNT,
        "all_three_hundred_unordered_pairs_are_complete": (
            len(pair_records) == EXPECTED_QUADRATIC_PAIR_COUNT
        ),
        "all_external_comparisons_are_complete": comparison_count
        == sum(record["external_comparison_count"] for record in pair_records),
        "all_pair_distance_records_are_finite": all(
            np.isfinite(record["minimum_external_distance_lower"]) for record in pair_records
        ),
    }
    return {
        "selected_eigenvalue_count": len(selected),
        "unordered_pair_count": len(pair_records),
        "external_comparison_count": comparison_count,
        "minimum_quadratic_external_spectral_distance_lower": _fraction_record(global_minimum),
        "minimum_distance_witness": global_witness,
        "exact_pair_digest_sha256": q011b._canonical_json_sha256(exact_pair_records),
        "pair_records": pair_records,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "stripe_dimension": STRIPE_DIMENSION,
        "zero_block_fixed_leaf_dimension": COORDINATE_DIMENSION,
        "full_fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "representative_blocks": list(REPRESENTATIVE_BLOCKS),
        "selected_block_dimensions": {
            str(index): value for index, value in SELECTED_BLOCK_DIMENSIONS.items()
        },
        "expected_selected_count": EXPECTED_SELECTED_COUNT,
        "expected_external_count": EXPECTED_EXTERNAL_COUNT,
        "expected_quadratic_pair_count": EXPECTED_QUADRATIC_PAIR_COUNT,
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "replay_precision_bits": REPLAY_PRECISION_BITS,
        "root_coordinate_radius_cap": _fraction_record(ROOT_RADIUS_CAP),
        "maximum_inverse_defect": _fraction_record(MAXIMUM_INVERSE_DEFECT),
        "spectral_radius_ceiling": _fraction_record(SPECTRAL_RADIUS_CEILING),
        "minimum_disc_split_gap": _fraction_record(MINIMUM_DISC_SPLIT_GAP),
        "minimum_normal_dominance_gap": _fraction_record(MINIMUM_NORMAL_DOMINANCE_GAP),
        "minimum_quadratic_distance": _fraction_record(MINIMUM_QUADRATIC_DISTANCE),
        "maximum_selected_matching_distance": MAXIMUM_SELECTED_MATCHING_DISTANCE,
        "maximum_point_block_discrepancy": _fraction_record(MAXIMUM_POINT_BLOCK_DISCREPANCY),
        "maximum_conjugate_block_discrepancy": MAXIMUM_CONJUGATE_BLOCK_DISCREPANCY,
        "maximum_conjugate_spectrum_discrepancy": (MAXIMUM_CONJUGATE_SPECTRUM_DISCREPANCY),
        "complex_rectangle_modulus_upper": "|Re|_max + |Im|_max",
        "complex_distance_lower": "max(|Re|, |Im|) for exact point differences",
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "root_digest_sha256": cycle["root_digest_sha256"],
        "block_digest_sha256": cycle["block_digest_sha256"],
        "proof_digest_sha256": cycle["proof_digest_sha256"],
    }


def run_interval_spectral_split_audit() -> dict[str, Any]:
    sealed_audit, q011j_artifact, q011c2_artifact = _sealed_input_audit()
    coordinate, lifted, lift_matrix, state_box, _, root_audit = _root_enclosure_audit(
        q011j_artifact
    )
    proposals, family_distances, block_audit = _block_family_audit(
        coordinate,
        lifted,
        lift_matrix,
        state_box,
    )
    centers, radii, spectral_proof = _spectral_proof_audit(proposals, family_distances)
    split_audit, selected_indices = _spectral_split_audit(centers, radii, q011c2_artifact)
    quadratic_audit = _quadratic_nonresonance_audit(centers, radii, selected_indices)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed_audit,
    }
    root_sections = {"contraction_derived_root_enclosure_audit": root_audit}
    block_sections = {"exact_interval_block_family_audit": block_audit}
    proof_sections = {
        "dual_precision_bauer_fike_audit": spectral_proof,
        "selected_external_split_audit": split_audit,
        "quadratic_spectral_nonresonance_audit": quadratic_audit,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    root_digest = q011b._canonical_json_sha256(root_sections)
    block_digest = q011b._canonical_json_sha256(block_sections)
    proof_digest = q011b._canonical_json_sha256(proof_sections)
    strict_payload = {
        **input_sections,
        **root_sections,
        **block_sections,
        **proof_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and root_digest == q011b._canonical_json_sha256(root_sections)
        and block_digest == q011b._canonical_json_sha256(block_sections)
        and proof_digest == q011b._canonical_json_sha256(proof_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )

    eig_proposals_complete = all(
        record["eigendecomposition"]["passed"]
        for record in spectral_proof["representative_block_records"]
    )
    validity_gates = {
        "q011j_and_q011c2_inputs_and_claim_boundaries_are_sealed": {
            "passed": sealed_audit["passed"],
            "threshold": "both artifact/runner hashes, ten digests, accepted outcomes and claim boundaries reproduce",
            "value": sealed_audit["checks"],
        },
        "contraction_derived_root_enclosure_is_exact_and_positive": {
            "passed": root_audit["passed"],
            "threshold": "z/(1-q)<=2e-15, replay containment, affine lift and positive population/density reproduce",
            "value": root_audit["checks"],
        },
        "all_exact_interval_fourier_block_families_are_complete": {
            "passed": block_audit["passed"],
            "threshold": "17 blocks, dimension 2598, exact interval action, point discrepancy, sparsity and conjugacy reproduce",
            "value": block_audit["checks"],
        },
        "all_deterministic_eigendecomposition_proposals_are_complete": {
            "passed": eig_proposals_complete,
            "threshold": "nine representative stable-sort/phase-normalized eigendecompositions and inverses replay bitwise",
            "value": [
                record["eigendecomposition"]["checks"]
                for record in spectral_proof["representative_block_records"]
            ],
        },
        "dual_precision_outward_bauer_fike_protocol_is_complete": {
            "passed": spectral_proof["protocol_passed"],
            "threshold": "256/384-bit directed MPFR products, ordered intervals, containment and conjugate transport complete",
            "value": spectral_proof["protocol_checks"],
        },
        "selected_matching_counts_and_quadratic_enumeration_are_complete": {
            "passed": bool(split_audit["protocol_passed"] and quadratic_audit["passed"]),
            "threshold": "Q011c2 matching, 24/2574 count, 300 pairs and every output-sector external comparison complete",
            "value": {
                "split_protocol": split_audit["protocol_checks"],
                "quadratic_protocol": quadratic_audit["checks"],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": "finite strict JSON, four section digests and runner provenance reproduce",
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    maximum_modulus = _fraction_from_record(split_audit["maximum_fixed_leaf_modulus_upper"])
    minimum_split_gap = _fraction_from_record(
        split_audit["minimum_selected_external_disc_gap_lower"]
    )
    normal_gap = _fraction_from_record(split_audit["normal_dominance_gap_lower"])
    quadratic_gap = _fraction_from_record(
        quadratic_audit["minimum_quadratic_external_spectral_distance_lower"]
    )
    count_passed = bool(
        split_audit["selected_eigenvalue_count"] == EXPECTED_SELECTED_COUNT
        and split_audit["external_eigenvalue_count"] == EXPECTED_EXTERNAL_COUNT
    )
    hypothesis_gates = {
        "all_inverse_defects_and_dual_precision_transports_are_certified": {
            "passed": bool(
                validity_passed
                and spectral_proof["hypothesis_passed"]
                and spectral_proof["protocol_passed"]
            ),
            "threshold": "all representative inverse defects <=1e-8 with dual-precision containment and conjugate transport",
            "value": {
                "maximum_inverse_defect": spectral_proof[
                    "maximum_inverse_defect_infinity_norm_upper"
                ],
                "checks": spectral_proof["hypothesis_checks"],
            },
        },
        "all_fixed_leaf_eigenvalue_discs_are_strictly_stable": {
            "passed": bool(validity_passed and maximum_modulus <= SPECTRAL_RADIUS_CEILING),
            "threshold": "maximum of all 2598 eigenvalue-disc modulus uppers <=0.9999",
            "value": split_audit["maximum_fixed_leaf_modulus_upper"],
        },
        "selected_and_external_disc_unions_are_separated_with_registered_counts": {
            "passed": bool(
                validity_passed
                and count_passed
                and split_audit["hypothesis_passed"]
                and minimum_split_gap >= MINIMUM_DISC_SPLIT_GAP
            ),
            "threshold": "counts 24/2574 and minimum selected/external complex disc gap >=1e-6",
            "value": {
                "selected_count": split_audit["selected_eigenvalue_count"],
                "external_count": split_audit["external_eigenvalue_count"],
                "minimum_gap": split_audit["minimum_selected_external_disc_gap_lower"],
            },
        },
        "selected_moduli_normally_dominate_external_moduli": {
            "passed": bool(validity_passed and normal_gap >= MINIMUM_NORMAL_DOMINANCE_GAP),
            "threshold": "selected minimum modulus lower minus external maximum modulus upper >=1e-6",
            "value": split_audit["normal_dominance_gap_lower"],
        },
        "all_selected_quadratic_products_are_spectrally_external_nonresonant": {
            "passed": bool(validity_passed and quadratic_gap >= MINIMUM_QUADRATIC_DISTANCE),
            "threshold": "minimum over 300 selected products and output-sector external discs >=1e-6",
            "value": quadratic_audit["minimum_quadratic_external_spectral_distance_lower"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011k interval spectral-split proof is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the exact repaired fixed point has a rigorously stable and quadratically "
            "nonresonant selected/external spectral split"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered Bauer--Fike enclosures do not certify the repaired "
            "selected/external spectral split"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Does the exact repaired fixed point have a rigorously stable "
            "fixed-leaf spectrum with the Q011c2-selected cluster separated "
            "from external modes and their quadratic products?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "root_digest_sha256": root_digest,
        "block_digest_sha256": block_digest,
        "proof_digest_sha256": proof_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["theorem_consequence"] = {
        "exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable": bool(
            validity_passed and hypotheses_passed
        ),
        "q011c2_designated_selected_cluster_has_rigorous_dimension_24": bool(
            validity_passed and hypotheses_passed
        ),
        "rigorous_external_dimension_is_2574": bool(validity_passed and hypotheses_passed),
        "selected_and_external_spectral_unions_do_not_exchange": bool(
            validity_passed and hypotheses_passed
        ),
        "selected_quadratic_eigenvalue_products_are_external_nonresonant": bool(
            validity_passed and hypotheses_passed
        ),
        "raw_q011b_exact_map_spectrum_is_certified": False,
        "q011c2_continuous_amplitude_path_is_rigorous": False,
        "nonnormal_homological_inverse_is_certified": False,
        "q011e_through_q011h_coefficients_transfer_to_repaired_map": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This computer-assisted proof concerns the unique x-independent fixed point "
        "of the fixed 17x17 periodic repaired exact map, its fixed-leaf linear "
        "spectrum, the Q011c2-designated selected/external cluster count, and "
        "eigenvalue-level quadratic external nonresonance. It does not certify the "
        "raw Q011b exact map, make the Q011c2 amplitude continuation rigorous, "
        "bound a nonnormal homological inverse, transfer Q011e--Q011h coefficients, "
        "prove a forced SSM, nonlinear normal attraction or a basin, or cover "
        "another grid, force, wall boundary, or D3Q27. The modulus gap is not a "
        "nonlinear normal-attraction theorem."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011j_fixed_point_acceptance_changed": False,
        "q011c2_numerical_cluster_acceptance_changed": False,
        "q011d_numerical_homological_acceptance_changed": False,
        "q011e_through_q011h_raw_map_results_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011l for a rigorous interval Sylvester/homological "
            "inverse bound on the repaired selected/external split."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Localize the first inverse-defect, disc-radius, stability, split, "
            "normal-gap or quadratic-pair failure; use an ordered Schur/Riesz "
            "cluster enclosure or a certified root recentering without changing "
            "the registered Q011k thresholds."
        )
    else:
        cycle["next_change"] = (
            "Localize the first failed sealing, root, block, eigendecomposition, "
            "directed-rounding, matching, enumeration or serialization validity gate."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011k cycle failed strict serialization or digest")
    return cycle


def run_q011k_study() -> dict[str, Any]:
    cycle = run_interval_spectral_split_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "interval_runtime": {
            "gmpy2_version": gmpy2.version(),
            "mpfr_version": gmpy2.mpfr_version(),
            "gmp_version": gmpy2.mp_version(),
            "primary_precision_bits": PRIMARY_PRECISION_BITS,
            "replay_precision_bits": REPLAY_PRECISION_BITS,
        },
        "mathematical_scope": {
            "diagnostic": (
                "outward interval fixed-leaf spectrum, selected/external split "
                "and eigenvalue-level quadratic nonresonance proof"
            ),
            "grid": [SIZE, SIZE],
            "x_independent_fixed_point": True,
            "fixed_conservation_leaf": True,
            "exact_rational_repaired_map": True,
            "claim": (
                "local fixed-point spectrum and eigenvalue-level quadratic nonresonance only"
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
    result = run_q011k_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
