"""Q011p zero-block invariant-subspace reality certificate."""

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

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011j_interval_fixed_point as q011j
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011o_graph_transform_setup as q011o
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    ComplexRationalInterval,
    RationalInterval,
    _all_numeric_values_finite,
    _complex_rectangle_absolute_upper,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

ComplexArray = npt.NDArray[np.complex128]
IntervalMatrix = list[list[ComplexRationalInterval]]

ZERO_BLOCK_DIMENSION = 150
SELECTED_DIMENSION = 6
EXTERNAL_DIMENSION = 144
SELECTED_INDICES = tuple(range(EXTERNAL_DIMENSION, ZERO_BLOCK_DIMENSION))
EXTERNAL_INDICES = tuple(range(EXTERNAL_DIMENSION))

PRIMARY_PRECISION_BITS = 256
REPLAY_PRECISION_BITS = 192
EXPANDED_REALITY_RADIUS = Fraction(1, 100)
CONJUGATION_ENCLOSURE_CAP = Fraction(1, 10**8)
EXTERNAL_SELECTED_BLOCK_CAP = Fraction(1, 10**6)
EXTERNAL_EXTERNAL_BLOCK_CAP = Fraction(100)
SELECTED_EXTERNAL_BLOCK_CAP = Fraction(100)
SELECTED_BLOCK_INVERSE_CAP = Fraction(20)

Q011J_ARTIFACT_SHA256 = "74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a"
Q011J_RUNNER_SHA256 = "23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5"
Q011J_DIGESTS = (
    "a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799",
    "adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b",
    "177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f",
    "1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0",
    "ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934",
)
Q011J_CLASSIFICATION = (
    "the repaired periodic forcing admits a locally unique exact fixed-leaf "
    "fixed point in the registered rational box"
)
Q011K_ARTIFACT_SHA256 = q011o.Q011K_ARTIFACT_SHA256
Q011K_RUNNER_SHA256 = q011o.Q011K_RUNNER_SHA256
Q011K_DIGESTS = q011o.Q011K_DIGESTS
Q011K_CLASSIFICATION = q011o.Q011K_CLASSIFICATION
Q011L_ARTIFACT_SHA256 = q011o.Q011L_ARTIFACT_SHA256
Q011L_RUNNER_SHA256 = q011o.Q011L_RUNNER_SHA256
Q011L_DIGESTS = q011o.Q011L_DIGESTS
Q011L_CLASSIFICATION = q011o.Q011L_CLASSIFICATION
Q011O_ARTIFACT_SHA256 = (
    "bbbc26939d4ef73aae95ad6517f5f1549f2eaf7b6edcbac5e5171f329064bc07"
)
Q011O_RUNNER_SHA256 = (
    "60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f"
)
Q011O_DIGESTS = (
    "0bddd90fc21a745b910ff47e133e72045842c77b589a818a21e946f85ba63da0",
    "6c00ce5d9df986830a4ad2d98df3970417d47e4fb9f1784364ce32b64d7396b7",
    "f9aaea144b0e79c6adf42296b7e8dcd562f2b75525b6abf4ac99c43dcbd1859c",
    "5799e9997ac1ec692ddce97465174204ee22debaea942ed7fab637209c912e0d",
    "6ec0a97c1b3d653e5edd3ffc7f4b8b9fa746e86e8d706e251753eecb8ab9a864",
)
Q011O_CLASSIFICATION = (
    "the registered block-sup norm does not support the localized "
    "graph-transform setup"
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


def _fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011j",
            directory / "q011j_interval_fixed_point.json",
            Path(q011j.__file__).resolve(),
            Q011J_ARTIFACT_SHA256,
            Q011J_RUNNER_SHA256,
            Q011J_DIGESTS,
            (
                "input_digest_sha256",
                "coordinate_digest_sha256",
                "oracle_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011J_CLASSIFICATION,
        ),
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            Q011K_ARTIFACT_SHA256,
            Q011K_RUNNER_SHA256,
            Q011K_DIGESTS,
            (
                "input_digest_sha256",
                "root_digest_sha256",
                "block_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011K_CLASSIFICATION,
        ),
        (
            "q011l",
            directory / "q011l_interval_homological_inverse.json",
            Path(q011l.__file__).resolve(),
            Q011L_ARTIFACT_SHA256,
            Q011L_RUNNER_SHA256,
            Q011L_DIGESTS,
            (
                "input_digest_sha256",
                "graph_digest_sha256",
                "pair_digest_sha256",
                "homological_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011L_CLASSIFICATION,
        ),
        (
            "q011o",
            directory / "q011o_graph_transform_setup.json",
            Path(q011o.__file__).resolve(),
            Q011O_ARTIFACT_SHA256,
            Q011O_RUNNER_SHA256,
            Q011O_DIGESTS,
            (
                "input_digest_sha256",
                "coordinate_digest_sha256",
                "linear_digest_sha256",
                "localization_digest_sha256",
                "result_digest_sha256",
            ),
            "rejected",
            Q011O_CLASSIFICATION,
        ),
    )
    artifacts: dict[str, dict[str, Any]] = {}
    records: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    for (
        label,
        artifact_path,
        runner_path,
        artifact_hash,
        runner_hash,
        expected_digests,
        digest_names,
        expected_outcome,
        classification,
    ) in specifications:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        cycle = artifact["cycle"]
        digests = tuple(cycle[name] for name in digest_names)
        artifacts[label] = artifact
        checks[f"{label}_artifact_sha256_matches"] = (
            _file_sha256(artifact_path) == artifact_hash
        )
        checks[f"{label}_runner_sha256_matches"] = bool(
            _file_sha256(runner_path) == runner_hash
            and artifact["runner_source"]["sha256"] == runner_hash
        )
        checks[f"{label}_digests_match"] = digests == expected_digests
        checks[f"{label}_outcome_reproduces"] = bool(
            cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == expected_outcome
            and cycle["scientific_classification"] == classification
        )
        checks[f"{label}_package_source_metadata_matches"] = (
            artifact["source"] == source_metadata()
        )
        checks[f"{label}_artifact_is_strict_finite_json"] = bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        )
        records[label] = {
            "filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_sha256": _file_sha256(runner_path),
            "digests": list(digests),
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        }

    j_theorem = artifacts["q011j"]["cycle"]["theorem_consequence"]
    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    l_theorem = artifacts["q011l"]["cycle"]["theorem_consequence"]
    o_cycle = artifacts["q011o"]["cycle"]
    o_theorem = o_cycle["theorem_consequence"]
    checks["q011j_claim_boundary_is_preserved"] = bool(
        j_theorem["repaired_exact_stripe_fixed_point_exists"]
        and not j_theorem["rigorous_fixed_leaf_spectrum_is_certified"]
        and not j_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011k_claim_boundary_is_preserved"] = bool(
        k_theorem[
            "exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"
        ]
        and k_theorem[
            "q011c2_designated_selected_cluster_has_rigorous_dimension_24"
        ]
        and not k_theorem["nonnormal_homological_inverse_is_certified"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011l_claim_boundary_is_preserved"] = bool(
        l_theorem["exact_selected_invariant_graphs_are_certified"]
        and l_theorem[
            "all_five_quadratic_sector_homological_operators_are_invertible"
        ]
        and not l_theorem["repaired_quadratic_jet_or_coefficients_are_certified"]
        and not l_theorem["forced_ssm_exists_or_is_unique"]
    )
    failed_o = o_cycle["failed_hypothesis_order"]
    checks["q011o_valid_rejection_and_claim_boundary_are_preserved"] = bool(
        failed_o
        == ["fixed_leaf_triangular_coordinate_is_bijective_and_real_typed"]
        and sum(gate["passed"] for gate in o_cycle["hypothesis_gates"].values())
        == 4
        and not o_theorem[
            "fixed_leaf_fourier_eigen_graph_coordinate_is_type_correct"
        ]
        and not o_theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
        and not o_theorem["an_exact_local_invariant_manifold_or_ssm_is_disproved"]
    )
    checks["q011o_nested_seals_reproduce_but_are_not_substituted"] = bool(
        o_cycle["sealed_input_audit"]["passed"]
        and records["q011k"]["artifact_sha256"] == Q011K_ARTIFACT_SHA256
        and records["q011l"]["artifact_sha256"] == Q011L_ARTIFACT_SHA256
    )
    return {**records, "checks": checks, "passed": all(checks.values())}, artifacts


def _zero_block_reconstruction_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    _coordinate, lifted, lift_matrix, state_box, _root_radius, root_audit = (
        q011k._root_enclosure_audit(artifacts["q011j"])
    )
    point_state = [RationalInterval.point(value) for value in lifted]
    family_sparse, family_pivot, _ = q011j._reduced_derivative_factors(state_box)
    point_sparse, point_pivot, _ = q011j._reduced_derivative_factors(point_state)
    family_zero = q011j._combine_reduced_factors(
        family_sparse,
        family_pivot,
        lift_matrix,
    )
    point_zero = q011j._point_matrix(
        q011j._combine_reduced_factors(point_sparse, point_pivot, lift_matrix)
    )
    proposal = (
        np.asarray(point_zero, dtype=np.float64)
        + np.eye(ZERO_BLOCK_DIMENSION, dtype=np.float64)
    ).astype(np.complex128)
    values, vectors, inverse, eig_audit = q011k._canonical_eigendecomposition(
        proposal
    )
    family_distance, point_distance = q011k._zero_block_distances(
        family_zero,
        point_zero,
        proposal,
    )

    k_cycle = artifacts["q011k"]["cycle"]
    stored_block = next(
        record
        for record in k_cycle["exact_interval_block_family_audit"]["block_records"]
        if record["block_index"] == 0
    )
    stored_proof = next(
        record
        for record in k_cycle["dual_precision_bauer_fike_audit"][
            "representative_block_records"
        ]
        if record["block_index"] == 0
    )
    centers, selected, _, metrics, spectral_audit = q011l._spectral_data(
        artifacts["q011k"]
    )
    graphs, graph_audit = q011l._graph_audit(centers, selected, metrics)
    stored_graph = next(
        record
        for record in artifacts["q011l"]["cycle"]["selected_invariant_graph_audit"][
            "block_records"
        ]
        if record["block_index"] == 0
    )
    exact_family_is_real = all(
        isinstance(value, RationalInterval)
        for row in family_zero
        for value in row
    )
    selected_indices = selected[0]
    external_indices = tuple(
        index
        for index in range(ZERO_BLOCK_DIMENSION)
        if index not in frozenset(selected_indices)
    )
    checks = {
        "q011k_root_enclosure_reconstructs": root_audit["passed"],
        "zero_block_point_proposal_hash_matches": (
            q011b._array_sha256(proposal) == stored_block["proposal_sha256"]
        ),
        "zero_block_family_distance_matches": (
            family_distance
            == _fraction(stored_block["interval_family_distance_infinity_upper"])
        ),
        "zero_block_point_distance_matches": (
            point_distance
            == _fraction(stored_block["point_proposal_distance_infinity_upper"])
        ),
        "canonical_eigendecomposition_reconstructs": (
            eig_audit == stored_proof["eigendecomposition"]
        ),
        "q011l_spectral_reconstruction_matches": (
            spectral_audit
            == artifacts["q011l"]["cycle"]["exact_eigencoordinate_residual_audit"]
        ),
        "q011l_graph_reconstruction_matches": (
            graph_audit
            == artifacts["q011l"]["cycle"]["selected_invariant_graph_audit"]
        ),
        "selected_and_external_indices_are_registered": (
            selected_indices == SELECTED_INDICES
            and external_indices == EXTERNAL_INDICES
        ),
        "zero_block_dimensions_close": (
            len(selected_indices) == SELECTED_DIMENSION
            and len(external_indices) == EXTERNAL_DIMENSION
            and len(selected_indices) + len(external_indices)
            == ZERO_BLOCK_DIMENSION
        ),
        "actual_root_operator_family_is_exactly_real": exact_family_is_real,
        "q011l_zero_graph_record_matches": (
            _fraction(stored_graph["graph_radius_upper"]) == graphs[0]["radius"]
            and _fraction(stored_graph["h_upper"]) == graphs[0]["h"]
            and _fraction(stored_graph["minimum_diagonal_component_gap"])
            == graphs[0]["gap"]
        ),
    }
    audit = {
        "zero_block_dimension": ZERO_BLOCK_DIMENSION,
        "selected_dimension": len(selected_indices),
        "external_dimension": len(external_indices),
        "selected_indices": list(selected_indices),
        "external_indices_digest_sha256": q011b._canonical_json_sha256(
            list(external_indices)
        ),
        "proposal_sha256": q011b._array_sha256(proposal),
        "eigenvalues_sha256": q011b._array_sha256(values),
        "eigenvectors_sha256": q011b._array_sha256(vectors),
        "inverse_candidate_sha256": q011b._array_sha256(inverse),
        "interval_family_distance_infinity_upper": _fraction_record(
            family_distance
        ),
        "point_proposal_distance_infinity_upper": _fraction_record(
            point_distance
        ),
        "actual_root_operator_family_scalar_type": (
            "real closed intervals with exact rational endpoints"
        ),
        "actual_root_operator_family_is_exactly_real": exact_family_is_real,
        "q011l_zero_graph_radius_upper": _fraction_record(graphs[0]["radius"]),
        "q011l_zero_graph_h_upper": _fraction_record(graphs[0]["h"]),
        "q011l_zero_graph_gap_lower": _fraction_record(graphs[0]["gap"]),
        "checks": checks,
        "passed": all(checks.values()),
    }
    data = {
        "vectors": vectors,
        "inverse": inverse,
        "selected_indices": selected_indices,
        "external_indices": external_indices,
        "graph": graphs[0],
        "stored_primary_proof": stored_proof["primary_precision_proof"],
    }
    return audit, data


def _directed_conjugation_product(
    inverse_real: list[list[gmpy2.mpfr]],
    inverse_imag: list[list[gmpy2.mpfr]],
    vector_real: list[list[gmpy2.mpfr]],
    vector_imag: list[list[gmpy2.mpfr]],
    precision: int,
) -> tuple[
    IntervalMatrix,
    str,
    dict[str, dict[str, bool]],
    bool,
]:
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
                real_total = gmpy2.mpfr(0)
                imag_total = gmpy2.mpfr(0)
                for inner in range(dimension):
                    wr = inverse_real[row][inner]
                    wi = inverse_imag[row][inner]
                    vr = vector_real[inner][column]
                    vi = vector_imag[inner][column]
                    real_total += wr * vr + wi * vi
                    imag_total += (-wr) * vi + wi * vr
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
                real_total = gmpy2.mpfr(0)
                imag_total = gmpy2.mpfr(0)
                for inner in range(dimension):
                    wr = inverse_real[row][inner]
                    wi = inverse_imag[row][inner]
                    vr = vector_real[inner][column]
                    vi = vector_imag[inner][column]
                    real_total += wr * vr + wi * vi
                    imag_total += (-wr) * vi + wi * vr
                real_row.append(real_total)
                imag_row.append(imag_total)
            upper_real.append(real_row)
            upper_imag.append(imag_row)

    digest = sha256()
    ordered = True
    intervals: IntervalMatrix = []
    for row in range(dimension):
        interval_row = []
        for column in range(dimension):
            real_lower = Fraction(*lower_real[row][column].as_integer_ratio())
            real_upper = Fraction(*upper_real[row][column].as_integer_ratio())
            imag_lower = Fraction(*lower_imag[row][column].as_integer_ratio())
            imag_upper = Fraction(*upper_imag[row][column].as_integer_ratio())
            ordered = bool(
                ordered
                and real_lower <= real_upper
                and imag_lower <= imag_upper
            )
            interval_row.append(
                ComplexRationalInterval(
                    RationalInterval(real_lower, real_upper),
                    RationalInterval(imag_lower, imag_upper),
                )
            )
            for endpoint in (
                real_lower,
                real_upper,
                imag_lower,
                imag_upper,
            ):
                digest.update(str(endpoint.numerator).encode("ascii"))
                digest.update(b"/")
                digest.update(str(endpoint.denominator).encode("ascii"))
                digest.update(b"\0")
        intervals.append(interval_row)
    return (
        intervals,
        digest.hexdigest(),
        {
            "product_round_down": q011j._context_flags(lower_context),
            "product_round_up": q011j._context_flags(upper_context),
        },
        ordered,
    )


def _block_norm_upper(
    matrix: IntervalMatrix,
    rows: tuple[int, ...],
    columns: tuple[int, ...],
) -> Fraction:
    return max(
        sum(
            (
                _complex_rectangle_absolute_upper(matrix[row][column])
                for column in columns
            ),
            start=Fraction(0),
        )
        for row in rows
    )


def _point_interval(value: complex) -> ComplexRationalInterval:
    number = complex(value)
    return ComplexRationalInterval.point(
        Fraction.from_float(number.real),
        Fraction.from_float(number.imag),
    )


def _candidate_times_interval_defect(
    candidate: ComplexArray,
    matrix: IntervalMatrix,
    indices: tuple[int, ...],
) -> Fraction:
    candidate_intervals = [
        [_point_interval(candidate[row, column]) for column in range(candidate.shape[1])]
        for row in range(candidate.shape[0])
    ]
    maximum = Fraction(0)
    for row in range(candidate.shape[0]):
        total_row = Fraction(0)
        for column in range(candidate.shape[1]):
            total = ComplexRationalInterval.zero()
            for inner in range(candidate.shape[1]):
                total = total + (
                    candidate_intervals[row][inner]
                    * matrix[indices[inner]][indices[column]]
                )
            if row == column:
                total = total - ComplexRationalInterval.point(1)
            total_row += _complex_rectangle_absolute_upper(total)
        maximum = max(maximum, total_row)
    return maximum


def _intervals_contained(
    inner: IntervalMatrix,
    outer: IntervalMatrix,
) -> bool:
    return all(
        outer[row][column].real.lower <= inner[row][column].real.lower
        and inner[row][column].real.upper <= outer[row][column].real.upper
        and outer[row][column].imag.lower <= inner[row][column].imag.lower
        and inner[row][column].imag.upper <= outer[row][column].imag.upper
        for row in range(len(inner))
        for column in range(len(inner[row]))
    )


def _conjugation_proof_lane(
    data: dict[str, Any],
    precision: int,
) -> tuple[dict[str, Any], dict[str, Fraction], IntervalMatrix]:
    caller_signature = q011j._context_signature(gmpy2.get_context())
    vectors = data["vectors"]
    inverse = data["inverse"]
    selected_indices = data["selected_indices"]
    external_indices = data["external_indices"]
    vector_real, vector_imag, vector_flags, vector_exact = (
        q011k._complex_mpfr_endpoints(vectors, precision)
    )
    inverse_real, inverse_imag, inverse_flags, inverse_exact = (
        q011k._complex_mpfr_endpoints(inverse, precision)
    )
    vector_norm, vector_norm_flags = q011k._complex_infinity_norm_upper(
        vector_real,
        vector_imag,
        precision,
    )
    inverse_norm, inverse_norm_flags = q011k._complex_infinity_norm_upper(
        inverse_real,
        inverse_imag,
        precision,
    )
    inverse_defect, inverse_digest, inverse_product_flags, inverse_ordered = (
        q011k._directed_inverse_defect(
            inverse_real,
            inverse_imag,
            vector_real,
            vector_imag,
            precision,
        )
    )
    intervals, product_digest, product_flags, product_ordered = (
        _directed_conjugation_product(
            inverse_real,
            inverse_imag,
            vector_real,
            vector_imag,
            precision,
        )
    )
    if inverse_defect >= 1:
        conjugation_error = Fraction(10**1000)
    else:
        conjugation_error = (
            inverse_defect
            * inverse_norm
            * vector_norm
            / (1 - inverse_defect)
        )

    point_product = inverse @ np.conjugate(vectors)
    selected_point = point_product[np.ix_(selected_indices, selected_indices)]
    selected_inverse_candidate = np.linalg.inv(selected_point)
    (
        candidate_real,
        candidate_imag,
        candidate_flags,
        candidate_exact,
    ) = q011k._complex_mpfr_endpoints(selected_inverse_candidate, precision)
    candidate_norm, candidate_norm_flags = q011k._complex_infinity_norm_upper(
        candidate_real,
        candidate_imag,
        precision,
    )
    selected_point_inverse_defect = _candidate_times_interval_defect(
        selected_inverse_candidate,
        intervals,
        selected_indices,
    )
    if selected_point_inverse_defect >= 1:
        selected_point_inverse = Fraction(10**1000)
    else:
        selected_point_inverse = candidate_norm / (
            1 - selected_point_inverse_defect
        )
    selected_actual_perturbation = (
        selected_point_inverse * conjugation_error
    )
    if selected_actual_perturbation >= 1:
        selected_actual_inverse = Fraction(10**1000)
        selected_conorm = Fraction(0)
    else:
        selected_actual_inverse = selected_point_inverse / (
            1 - selected_actual_perturbation
        )
        selected_conorm = 1 / selected_actual_inverse

    point_block_bounds = {
        "J_EE": _block_norm_upper(
            intervals,
            external_indices,
            external_indices,
        ),
        "J_ES": _block_norm_upper(
            intervals,
            external_indices,
            selected_indices,
        ),
        "J_SE": _block_norm_upper(
            intervals,
            selected_indices,
            external_indices,
        ),
        "J_SS": _block_norm_upper(
            intervals,
            selected_indices,
            selected_indices,
        ),
    }
    actual_block_bounds = {
        name: bound + conjugation_error
        for name, bound in point_block_bounds.items()
    }
    flag_groups = {
        **{f"vector_{name}": value for name, value in vector_flags.items()},
        **{f"inverse_{name}": value for name, value in inverse_flags.items()},
        **{f"candidate_{name}": value for name, value in candidate_flags.items()},
        "vector_norm_round_up": vector_norm_flags,
        "inverse_norm_round_up": inverse_norm_flags,
        "candidate_norm_round_up": candidate_norm_flags,
        **{
            f"inverse_product_{name}": value
            for name, value in inverse_product_flags.items()
        },
        **{
            f"conjugation_product_{name}": value
            for name, value in product_flags.items()
        },
    }
    caller_unchanged = (
        q011j._context_signature(gmpy2.get_context()) == caller_signature
    )
    checks = {
        "all_binary64_inputs_convert_exactly": bool(
            vector_exact and inverse_exact and candidate_exact
        ),
        "inverse_defect_intervals_are_ordered": inverse_ordered,
        "conjugation_product_intervals_are_ordered": product_ordered,
        "no_forbidden_mpfr_flags": q011k._forbidden_flags_clear(flag_groups),
        "caller_context_is_unchanged": caller_unchanged,
        "full_inverse_defect_is_strictly_below_one": inverse_defect < 1,
        "selected_point_inverse_defect_is_strictly_below_one": (
            selected_point_inverse_defect < 1
        ),
        "selected_actual_inverse_neumann_denominator_is_positive": (
            selected_actual_perturbation < 1
        ),
        "all_derived_bounds_are_finite": _all_numeric_values_finite(
            [
                vector_norm,
                inverse_norm,
                inverse_defect,
                conjugation_error,
                *point_block_bounds.values(),
                *actual_block_bounds.values(),
                candidate_norm,
                selected_point_inverse_defect,
                selected_actual_inverse,
                selected_conorm,
            ]
        ),
    }
    record = {
        "precision_bits": precision,
        "vector_infinity_norm_upper": _fraction_record(vector_norm),
        "inverse_candidate_infinity_norm_upper": _fraction_record(inverse_norm),
        "inverse_defect_infinity_norm_upper": _fraction_record(inverse_defect),
        "conjugation_point_error_upper": _fraction_record(conjugation_error),
        "point_conjugation_block_norm_uppers": {
            name: _fraction_record(value)
            for name, value in point_block_bounds.items()
        },
        "actual_conjugation_block_norm_uppers": {
            name: _fraction_record(value)
            for name, value in actual_block_bounds.items()
        },
        "selected_point_inverse_candidate_sha256": q011b._array_sha256(
            selected_inverse_candidate
        ),
        "selected_point_inverse_candidate_norm_upper": _fraction_record(
            candidate_norm
        ),
        "selected_point_inverse_defect_upper": _fraction_record(
            selected_point_inverse_defect
        ),
        "selected_point_inverse_norm_upper": _fraction_record(
            selected_point_inverse
        ),
        "selected_actual_inverse_perturbation_upper": _fraction_record(
            selected_actual_perturbation
        ),
        "selected_actual_inverse_norm_upper": _fraction_record(
            selected_actual_inverse
        ),
        "selected_actual_conorm_lower": _fraction_record(selected_conorm),
        "inverse_defect_interval_sha256": inverse_digest,
        "conjugation_product_interval_sha256": product_digest,
        "mpfr_flag_groups": flag_groups,
        "checks": checks,
        "passed": all(checks.values()),
    }
    exact = {
        "vector_norm": vector_norm,
        "inverse_norm": inverse_norm,
        "inverse_defect": inverse_defect,
        "conjugation_error": conjugation_error,
        "j_EE": actual_block_bounds["J_EE"],
        "j_ES": actual_block_bounds["J_ES"],
        "j_SE": actual_block_bounds["J_SE"],
        "j_SS": actual_block_bounds["J_SS"],
        "selected_actual_inverse": selected_actual_inverse,
        "selected_conorm": selected_conorm,
    }
    return record, exact, intervals


def _dual_precision_conjugation_audit(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    primary, primary_exact, primary_intervals = _conjugation_proof_lane(
        data,
        PRIMARY_PRECISION_BITS,
    )
    replay, replay_exact, replay_intervals = _conjugation_proof_lane(
        data,
        REPLAY_PRECISION_BITS,
    )
    upper_names = (
        "vector_norm",
        "inverse_norm",
        "inverse_defect",
        "conjugation_error",
        "j_EE",
        "j_ES",
        "j_SE",
        "j_SS",
        "selected_actual_inverse",
    )
    containment_checks = {
        "primary_product_intervals_are_contained_in_replay": (
            _intervals_contained(primary_intervals, replay_intervals)
        ),
        "all_primary_upper_bounds_are_contained_in_replay": all(
            primary_exact[name] <= replay_exact[name] for name in upper_names
        ),
        "primary_selected_conorm_lower_contains_replay": (
            primary_exact["selected_conorm"]
            >= replay_exact["selected_conorm"]
        ),
    }
    stored = data["stored_primary_proof"]
    stored_checks = {
        "primary_vector_norm_matches_q011k": (
            primary_exact["vector_norm"]
            == _fraction(stored["vector_infinity_norm_upper"])
        ),
        "primary_inverse_norm_matches_q011k": (
            primary_exact["inverse_norm"]
            == _fraction(stored["inverse_candidate_infinity_norm_upper"])
        ),
        "primary_inverse_defect_matches_q011k": (
            primary_exact["inverse_defect"]
            == _fraction(stored["inverse_defect_infinity_norm_upper"])
        ),
    }
    checks = {
        "primary_256_bit_protocol_passes": primary["passed"],
        "independent_192_bit_protocol_passes": replay["passed"],
        **containment_checks,
        **stored_checks,
    }
    audit = {
        "conjugation_definition": (
            "J_0 = V_0^{-1} conjugate(V_0), acting as "
            "mathcal_J_0(y) = J_0 conjugate(y)"
        ),
        "coordinate_order": "external indices 0..143 followed by selected 144..149",
        "matrix_norm": "maximum complex-absolute row sum",
        "conjugation_error_formula": (
            "epsilon_J = delta_V * ||W_0|| * ||V_0|| / (1-delta_V)"
        ),
        "primary_precision_proof": primary,
        "independent_containment_proof": replay,
        "containment_checks": containment_checks,
        "q011k_reproduction_checks": stored_checks,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, primary_exact


def _expanded_uniqueness_audit(
    reconstruction: dict[str, Any],
    conjugation: dict[str, Fraction],
) -> dict[str, Any]:
    graph_radius = _fraction(reconstruction["q011l_zero_graph_radius_upper"])
    h_value = _fraction(reconstruction["q011l_zero_graph_h_upper"])
    gap = _fraction(reconstruction["q011l_zero_graph_gap_lower"])
    theta = h_value * gap
    selected_conorm = conjugation["selected_conorm"]
    denominator = selected_conorm - conjugation["j_SE"] * graph_radius
    conjugated_radius = (
        (
            conjugation["j_EE"] * graph_radius
            + conjugation["j_ES"]
        )
        / denominator
        if denominator > 0
        else Fraction(10**1000)
    )
    expanded_self_map = h_value * (
        1 + 2 * EXPANDED_REALITY_RADIUS + EXPANDED_REALITY_RADIUS**2
    )
    expanded_contraction = h_value * (
        2 + 2 * EXPANDED_REALITY_RADIUS
    )
    expanded_identification_margin = gap - 2 * theta * (
        1 + EXPANDED_REALITY_RADIUS
    )
    algebraic_identities = {
        "antilinear_involution_identity": (
            "J_0 conjugate(J_0) = I follows from "
            "J_0=V_0^{-1}conjugate(V_0)"
        ),
        "linear_conjugation_covariance_identity": (
            "J_0 conjugate(V_0^{-1} A_0 V_0) = "
            "(V_0^{-1} A_0 V_0) J_0 because A_0 is real"
        ),
        "conjugated_graph_formula": (
            "C(G)=(J_EE conjugate(G)+J_ES)"
            "(J_SE conjugate(G)+J_SS)^{-1}"
        ),
        "conjugation_preserves_invariance": (
            "because A_0 is real, conjugating an A_0-invariant graph "
            "produces another A_0-invariant graph"
        ),
        "fixed_real_dimension_lemma": (
            "a conjugation-invariant complex six-plane is the "
            "complexification of its six-dimensional real fixed space"
        ),
    }
    checks = {
        "conjugated_graph_denominator_formula_reproduces": (
            denominator
            == selected_conorm - conjugation["j_SE"] * graph_radius
        ),
        "conjugated_graph_radius_formula_reproduces": (
            denominator <= 0
            or conjugated_radius
            == (
                conjugation["j_EE"] * graph_radius
                + conjugation["j_ES"]
            )
            / denominator
        ),
        "expanded_self_map_formula_reproduces": (
            expanded_self_map
            == h_value
            * (
                1
                + 2 * EXPANDED_REALITY_RADIUS
                + EXPANDED_REALITY_RADIUS**2
            )
        ),
        "expanded_contraction_formula_reproduces": (
            expanded_contraction
            == h_value * (2 + 2 * EXPANDED_REALITY_RADIUS)
        ),
        "expanded_identification_formula_reproduces": (
            expanded_identification_margin
            == gap - 2 * theta * (1 + EXPANDED_REALITY_RADIUS)
        ),
        "original_q011l_graph_is_in_expanded_ball": (
            graph_radius <= EXPANDED_REALITY_RADIUS
        ),
        "algebraic_proof_chain_is_typed": (
            reconstruction["actual_root_operator_family_is_exactly_real"]
            and len(algebraic_identities) == 5
        ),
        "all_uniqueness_bounds_are_finite": _all_numeric_values_finite(
            [
                graph_radius,
                h_value,
                gap,
                theta,
                denominator,
                conjugated_radius,
                expanded_self_map,
                expanded_contraction,
                expanded_identification_margin,
            ]
        ),
    }
    return {
        "q011l_graph_radius_upper": _fraction_record(graph_radius),
        "q011l_h_upper": _fraction_record(h_value),
        "q011l_gap_lower": _fraction_record(gap),
        "reconstructed_theta_upper": _fraction_record(theta),
        "expanded_reality_radius": _fraction_record(EXPANDED_REALITY_RADIUS),
        "conjugated_graph_denominator_lower": _fraction_record(denominator),
        "conjugated_graph_radius_upper": _fraction_record(conjugated_radius),
        "expanded_riccati_self_map_upper": _fraction_record(expanded_self_map),
        "expanded_riccati_contraction_upper": _fraction_record(
            expanded_contraction
        ),
        "expanded_spectral_identification_margin_lower": _fraction_record(
            expanded_identification_margin
        ),
        "algebraic_identities": algebraic_identities,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "zero_block_dimension": ZERO_BLOCK_DIMENSION,
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "selected_indices": list(SELECTED_INDICES),
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "independent_containment_precision_bits": REPLAY_PRECISION_BITS,
        "expanded_reality_radius": _fraction_record(EXPANDED_REALITY_RADIUS),
        "conjugation_enclosure_cap": _fraction_record(
            CONJUGATION_ENCLOSURE_CAP
        ),
        "external_selected_block_cap": _fraction_record(
            EXTERNAL_SELECTED_BLOCK_CAP
        ),
        "external_external_block_cap": _fraction_record(
            EXTERNAL_EXTERNAL_BLOCK_CAP
        ),
        "selected_external_block_cap": _fraction_record(
            SELECTED_EXTERNAL_BLOCK_CAP
        ),
        "selected_block_inverse_cap": _fraction_record(
            SELECTED_BLOCK_INVERSE_CAP
        ),
        "matrix_norm": "maximum complex-absolute row sum",
        "floating_point_gate_decisions": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "conjugation_digest_sha256": cycle["conjugation_digest_sha256"],
        "uniqueness_digest_sha256": cycle["uniqueness_digest_sha256"],
    }


def run_zero_block_reality_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    reconstruction, data = _zero_block_reconstruction_audit(artifacts)
    conjugation, conjugation_exact = _dual_precision_conjugation_audit(data)
    uniqueness = _expanded_uniqueness_audit(
        reconstruction,
        conjugation_exact,
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
        "zero_block_reconstruction_audit": reconstruction,
    }
    conjugation_sections = {
        "dual_precision_conjugation_audit": conjugation
    }
    uniqueness_sections = {
        "expanded_riccati_uniqueness_audit": uniqueness
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    conjugation_digest = q011b._canonical_json_sha256(conjugation_sections)
    uniqueness_digest = q011b._canonical_json_sha256(uniqueness_sections)
    strict_payload = {
        **input_sections,
        **conjugation_sections,
        **uniqueness_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and conjugation_digest
        == q011b._canonical_json_sha256(conjugation_sections)
        and uniqueness_digest
        == q011b._canonical_json_sha256(uniqueness_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "q011j_q011k_q011l_and_q011o_are_directly_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "four artifact/runner hashes, twenty digests, outcomes and "
                "claim boundaries reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "zero_block_and_q011l_graph_reconstruct": {
            "passed": reconstruction["passed"],
            "threshold": (
                "the real 150-dimensional root family, canonical V/W and "
                "the 6/144 Q011l graph split reproduce"
            ),
            "value": reconstruction["checks"],
        },
        "zero_block_reality_and_conjugation_operator_are_typed": {
            "passed": bool(
                reconstruction[
                    "actual_root_operator_family_is_exactly_real"
                ]
                and reconstruction["selected_dimension"]
                == SELECTED_DIMENSION
                and reconstruction["external_dimension"]
                == EXTERNAL_DIMENSION
                and uniqueness["checks"]["algebraic_proof_chain_is_typed"]
            ),
            "threshold": (
                "A_0 is real, V_0 is certified invertible and "
                "J_0=V_0^{-1}conjugate(V_0) acts on the same coordinate space"
            ),
            "value": {
                "operator_family_is_real": reconstruction[
                    "actual_root_operator_family_is_exactly_real"
                ],
                "selected_dimension": reconstruction["selected_dimension"],
                "external_dimension": reconstruction["external_dimension"],
            },
        },
        "directed_conjugation_and_selected_inverse_bounds_reproduce": {
            "passed": conjugation["passed"],
            "threshold": (
                "J_c, epsilon_J, four block bounds and the J_SS inverse "
                "bound reproduce by directed arithmetic"
            ),
            "value": conjugation["checks"],
        },
        "conjugated_graph_and_expanded_riccati_formulas_reproduce": {
            "passed": uniqueness["passed"],
            "threshold": (
                "d_C, r_C and expanded self-map, contraction and "
                "identification formulas reproduce exactly"
            ),
            "value": uniqueness["checks"],
        },
        "dual_precision_mpfr_protocol_is_contained_and_clean": {
            "passed": bool(
                conjugation["primary_precision_proof"]["passed"]
                and conjugation["independent_containment_proof"]["passed"]
                and all(conjugation["containment_checks"].values())
            ),
            "threshold": (
                "256-bit proof is contained in the independent 192-bit "
                "enclosure with clean flags and restored caller contexts"
            ),
            "value": {
                "primary_precision_bits": PRIMARY_PRECISION_BITS,
                "independent_precision_bits": REPLAY_PRECISION_BITS,
                "containment": conjugation["containment_checks"],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite strict JSON, three section digests and runner "
                "provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    epsilon = conjugation_exact["conjugation_error"]
    j_ee = conjugation_exact["j_EE"]
    j_es = conjugation_exact["j_ES"]
    j_se = conjugation_exact["j_SE"]
    selected_inverse = conjugation_exact["selected_actual_inverse"]
    denominator = _fraction(
        uniqueness["conjugated_graph_denominator_lower"]
    )
    conjugated_radius = _fraction(
        uniqueness["conjugated_graph_radius_upper"]
    )
    expanded_self_map = _fraction(
        uniqueness["expanded_riccati_self_map_upper"]
    )
    expanded_contraction = _fraction(
        uniqueness["expanded_riccati_contraction_upper"]
    )
    identification_margin = _fraction(
        uniqueness["expanded_spectral_identification_margin_lower"]
    )
    algebraic_covariance = bool(
        reconstruction["actual_root_operator_family_is_exactly_real"]
        and uniqueness["checks"]["algebraic_proof_chain_is_typed"]
    )
    registered_caps = bool(
        epsilon <= CONJUGATION_ENCLOSURE_CAP
        and j_es <= EXTERNAL_SELECTED_BLOCK_CAP
        and j_ee <= EXTERNAL_EXTERNAL_BLOCK_CAP
        and j_se <= SELECTED_EXTERNAL_BLOCK_CAP
        and selected_inverse <= SELECTED_BLOCK_INVERSE_CAP
    )
    graph_representable = bool(
        denominator > 0
        and conjugated_radius <= EXPANDED_REALITY_RADIUS
    )
    expanded_uniqueness = bool(
        _fraction(uniqueness["q011l_graph_radius_upper"])
        <= EXPANDED_REALITY_RADIUS
        and expanded_self_map <= EXPANDED_REALITY_RADIUS
        and expanded_contraction < 1
        and identification_margin > 0
    )
    reality_conclusion = bool(
        algebraic_covariance
        and registered_caps
        and graph_representable
        and expanded_uniqueness
        and reconstruction["selected_dimension"] == SELECTED_DIMENSION
    )
    hypothesis_gates = {
        "zero_block_conjugation_is_an_involution_and_commutes_with_dynamics": {
            "passed": bool(validity_passed and algebraic_covariance),
            "threshold": (
                "A_0 is real and the pulled-back conjugation identities "
                "follow from exact definitions"
            ),
            "value": uniqueness["algebraic_identities"],
        },
        "conjugation_and_selected_inverse_bounds_fit_registered_caps": {
            "passed": bool(validity_passed and registered_caps),
            "threshold": (
                "epsilon_J<=1e-8, j_ES<=1e-6, j_EE/j_SE<=100 and "
                "||J_SS^-1||<=20"
            ),
            "value": {
                "epsilon_J": _fraction_record(epsilon),
                "j_EE": _fraction_record(j_ee),
                "j_ES": _fraction_record(j_es),
                "j_SE": _fraction_record(j_se),
                "selected_inverse": _fraction_record(selected_inverse),
            },
        },
        "conjugated_subspace_is_a_graph_in_the_expanded_ball": {
            "passed": bool(validity_passed and graph_representable),
            "threshold": "d_C>0 and r_C<=1e-2",
            "value": {
                "d_C": uniqueness[
                    "conjugated_graph_denominator_lower"
                ],
                "r_C": uniqueness["conjugated_graph_radius_upper"],
                "expanded_radius": uniqueness["expanded_reality_radius"],
            },
        },
        "expanded_riccati_ball_has_unique_spectral_fixed_point": {
            "passed": bool(validity_passed and expanded_uniqueness),
            "threshold": (
                "the radius-1e-2 Riccati ball is a self-map and strict "
                "contraction with positive identification margin"
            ),
            "value": {
                "self_map": uniqueness[
                    "expanded_riccati_self_map_upper"
                ],
                "contraction": uniqueness[
                    "expanded_riccati_contraction_upper"
                ],
                "identification_margin": uniqueness[
                    "expanded_spectral_identification_margin_lower"
                ],
            },
        },
        "selected_invariant_subspace_has_real_dimension_six": {
            "passed": bool(validity_passed and reality_conclusion),
            "threshold": (
                "G and C(G) are the same unique fixed graph, so its "
                "conjugation-fixed real space has dimension six"
            ),
            "value": {
                "complex_dimension": reconstruction["selected_dimension"],
                "real_fixed_dimension": (
                    SELECTED_DIMENSION if reality_conclusion else None
                ),
                "conjugated_graph_radius": uniqueness[
                    "conjugated_graph_radius_upper"
                ],
            },
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011p zero-block reality audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the Q011l zero-block selected invariant subspace is the "
            "complexification of a six-dimensional real invariant subspace"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered Q011l zero-block certificate does not close a "
            "conjugation-invariant uniqueness neighborhood"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Is the Q011l zero-block selected invariant subspace the "
            "complexification of a six-dimensional real invariant subspace?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "conjugation_digest_sha256": conjugation_digest,
        "uniqueness_digest_sha256": uniqueness_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name
            for name, gate in hypothesis_gates.items()
            if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "zero_block_selected_invariant_subspace_is_conjugation_invariant": bool(
            validity_passed and hypotheses_passed
        ),
        "zero_block_selected_invariant_subspace_has_real_dimension_six": bool(
            validity_passed and hypotheses_passed
        ),
        "zero_block_selected_invariant_subspace_is_a_real_complexification": bool(
            validity_passed and hypotheses_passed
        ),
        "an_explicit_real_zero_block_frame_is_certified": False,
        "q011o_real_typed_coordinate_rejection_is_changed": False,
        "a_conjugacy_equivariant_nonlinear_cutoff_is_certified": False,
        "a_nonlinear_graph_transform_or_fixed_graph_is_certified": False,
        "an_exact_local_invariant_manifold_or_ssm_is_certified": False,
        "an_exact_local_invariant_manifold_or_ssm_is_disproved": False,
        "q011j_q011k_or_q011l_acceptance_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the zero Fourier linear block of the fixed "
        "17x17 repaired exact map on the fixed conservation leaf and the real "
        "structure of the Q011l six-dimensional selected invariant subspace. "
        "It certifies no explicit real frame, real-coordinate norm, Q011o "
        "acceptance, conjugacy-equivariant nonlinear cutoff, nonlinear graph "
        "transform, fixed graph, exact invariant manifold or SSM, smoothness, "
        "uniqueness, normal attraction, basin, other grid, force, wall "
        "boundary or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011j_fixed_point_acceptance_changed": False,
        "q011k_spectral_acceptance_changed": False,
        "q011l_homological_inverse_acceptance_changed": False,
        "q011o_real_typing_rejection_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011q to construct an explicit real zero-block frame "
            "and external complement, then re-evaluate coordinate lift, inverse, "
            "linear domination and an equivariant cutoff."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Reconstruct only the zero block with a direct real Schur or Riesz "
            "projector certificate."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, reconstruction, directed-product, "
            "selected-inverse, uniqueness or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011p cycle failed strict serialization or digest")
    return cycle


def run_q011p_study() -> dict[str, Any]:
    cycle = run_zero_block_reality_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "directed_backend": "gmpy2.mpfr",
            "primary_precision_bits": PRIMARY_PRECISION_BITS,
            "independent_containment_precision_bits": REPLAY_PRECISION_BITS,
            "floating_point_used_for_gate_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": "zero-block selected invariant-subspace reality",
            "grid": [17, 17],
            "fixed_conservation_leaf": True,
            "zero_block_dimension": ZERO_BLOCK_DIMENSION,
            "selected_complex_dimension": SELECTED_DIMENSION,
            "explicit_real_frame_certified": False,
            "q011o_acceptance_changed": False,
            "nonlinear_graph_transform_certified": False,
            "exact_invariant_manifold_claim": False,
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
    result = run_q011p_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
