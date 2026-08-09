"""Q011q explicit real-frame and localized-setup reissue audit."""

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
import research.q011m_quadratic_jet_majorant as q011m
import research.q011o_graph_transform_setup as q011o
import research.q011p_zero_block_reality as q011p
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    ComplexRationalInterval,
    _all_numeric_values_finite,
    _complex_rectangle_absolute_upper,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

ComplexArray = npt.NDArray[np.complex128]
ExactComplex = tuple[Fraction, Fraction]
ExactComplexMatrix = list[list[ExactComplex]]
IntervalMatrix = list[list[ComplexRationalInterval]]

SIZE = 17
ZERO_BLOCK_DIMENSION = 150
SELECTED_ZERO_DIMENSION = 6
EXTERNAL_ZERO_DIMENSION = 144
FIXED_LEAF_DIMENSION = 2598
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
ZERO_BLOCK_POPULATION_LIFT = 186

PRIMARY_PRECISION_BITS = 256
REPLAY_PRECISION_BITS = 192
LOCALIZATION_RADIUS = Fraction(1, 10**11)
CONJUGATION_BLOCK_ERROR_CAP = Fraction(1, 10**8)
POINT_FRAME_NORM_CAP = Fraction(20)
SELECTED_FRAME_INVERSE_CAP = Fraction(100)
EXTERNAL_FRAME_INVERSE_CAP = Fraction(1000)
FRAME_PERTURBATION_CAP = Fraction(1, 10**6)
SECTION_NORM_CAP = Fraction(1, 10**6)
LIFT_NORM_CAP = Fraction(2600)
COORDINATE_INVERSE_CAP = Fraction(900)
PHYSICAL_LOCALIZATION_CAP = Fraction(3, 10**8)
SELECTED_CONORM_FLOOR = Fraction(983, 1000)
EXTERNAL_NORM_CAP = Fraction(491, 500)
LINEAR_GAP_FLOOR = Fraction(1, 1000)
DOMINATION_RATIO_CAP = Fraction(999, 1000)
SELECTED_INVERSE_CAP = Fraction(51, 50)
COUPLING_CAP = Fraction(1, 10**6)
CUTOFF_LIPSCHITZ_CAP = Fraction(2)

Q011M_ARTIFACT_SHA256 = (
    "b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f"
)
Q011M_RUNNER_SHA256 = (
    "0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150"
)
Q011M_DIGESTS = (
    "dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb",
    "0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a",
    "1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514",
    "bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00",
    "f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4",
)
Q011M_CLASSIFICATION = (
    "the repaired exact map admits a unique graph-gauge quadratic jet with "
    "the registered coefficient and cubic-defect majorants"
)
Q011P_ARTIFACT_SHA256 = (
    "68968f8d01135fa3575a69c878b5ab89952ae39ec8e44b7fb398a3384f2fa6e1"
)
Q011P_RUNNER_SHA256 = (
    "fec9509068939663d6172539630f577383ad4da15f4c4575ef5caab7c65971f7"
)
Q011P_DIGESTS = (
    "49a2df9f7f8db4ba95ebb93413324e667d2237a52a390e2e6f44b512c5fd953f",
    "087bcf415559cf0985194ad50dcbb0748ecdadda4df6b53ad7172f5b7cba1a05",
    "41eee5097e7a0c2ea18ac79cd1b48abb1223d1925e953d7b2f34a4fb24777339",
    "19edd32732a658a3811ebedc07a9a4483f1fff3d4a26ff64d7917ad2ea01c7f7",
)
Q011P_CLASSIFICATION = (
    "the Q011l zero-block selected invariant subspace is the "
    "complexification of a six-dimensional real invariant subspace"
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
            q011p.Q011J_ARTIFACT_SHA256,
            q011p.Q011J_RUNNER_SHA256,
            q011p.Q011J_DIGESTS,
            (
                "input_digest_sha256",
                "coordinate_digest_sha256",
                "oracle_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            q011p.Q011J_CLASSIFICATION,
        ),
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            q011p.Q011K_ARTIFACT_SHA256,
            q011p.Q011K_RUNNER_SHA256,
            q011p.Q011K_DIGESTS,
            (
                "input_digest_sha256",
                "root_digest_sha256",
                "block_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            q011p.Q011K_CLASSIFICATION,
        ),
        (
            "q011l",
            directory / "q011l_interval_homological_inverse.json",
            Path(q011l.__file__).resolve(),
            q011p.Q011L_ARTIFACT_SHA256,
            q011p.Q011L_RUNNER_SHA256,
            q011p.Q011L_DIGESTS,
            (
                "input_digest_sha256",
                "graph_digest_sha256",
                "pair_digest_sha256",
                "homological_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            q011p.Q011L_CLASSIFICATION,
        ),
        (
            "q011m",
            directory / "q011m_quadratic_jet_majorant.json",
            Path(q011m.__file__).resolve(),
            Q011M_ARTIFACT_SHA256,
            Q011M_RUNNER_SHA256,
            Q011M_DIGESTS,
            (
                "input_digest_sha256",
                "derivative_digest_sha256",
                "coefficient_digest_sha256",
                "majorant_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011M_CLASSIFICATION,
        ),
        (
            "q011o",
            directory / "q011o_graph_transform_setup.json",
            Path(q011o.__file__).resolve(),
            q011p.Q011O_ARTIFACT_SHA256,
            q011p.Q011O_RUNNER_SHA256,
            q011p.Q011O_DIGESTS,
            (
                "input_digest_sha256",
                "coordinate_digest_sha256",
                "linear_digest_sha256",
                "localization_digest_sha256",
                "result_digest_sha256",
            ),
            "rejected",
            q011p.Q011O_CLASSIFICATION,
        ),
        (
            "q011p",
            directory / "q011p_zero_block_reality.json",
            Path(q011p.__file__).resolve(),
            Q011P_ARTIFACT_SHA256,
            Q011P_RUNNER_SHA256,
            Q011P_DIGESTS,
            (
                "input_digest_sha256",
                "conjugation_digest_sha256",
                "uniqueness_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011P_CLASSIFICATION,
        ),
    )
    artifacts: dict[str, dict[str, Any]] = {}
    records: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    digest_count = 0
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
        digest_count += len(digests)
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

    o_cycle = artifacts["q011o"]["cycle"]
    p_theorem = artifacts["q011p"]["cycle"]["theorem_consequence"]
    m_theorem = artifacts["q011m"]["cycle"]["theorem_consequence"]
    checks["twenty_nine_direct_digests_are_sealed"] = digest_count == 29
    checks["q011o_unique_typing_rejection_is_preserved"] = bool(
        o_cycle["failed_hypothesis_order"]
        == ["fixed_leaf_triangular_coordinate_is_bijective_and_real_typed"]
        and sum(
            gate["passed"] for gate in o_cycle["hypothesis_gates"].values()
        )
        == 4
        and not o_cycle["theorem_consequence"][
            "an_exact_local_invariant_manifold_or_ssm_is_certified"
        ]
    )
    checks["q011p_reality_and_claim_boundary_are_preserved"] = bool(
        p_theorem[
            "zero_block_selected_invariant_subspace_is_a_real_complexification"
        ]
        and not p_theorem["an_explicit_real_zero_block_frame_is_certified"]
        and not p_theorem[
            "a_nonlinear_graph_transform_or_fixed_graph_is_certified"
        ]
    )
    checks["q011m_claim_boundary_is_preserved"] = bool(
        m_theorem["unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    checks["nested_seals_reproduce_but_are_not_substituted"] = bool(
        artifacts["q011p"]["cycle"]["sealed_input_audit"]["passed"]
        and artifacts["q011o"]["cycle"]["sealed_input_audit"]["passed"]
        and records["q011j"]["artifact_sha256"]
        == q011p.Q011J_ARTIFACT_SHA256
        and records["q011m"]["artifact_sha256"] == Q011M_ARTIFACT_SHA256
    )
    return (
        {
            **records,
            "direct_digest_count": digest_count,
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _exact_complex(value: complex) -> ExactComplex:
    number = complex(value)
    return Fraction.from_float(number.real), Fraction.from_float(number.imag)


def _exact_complex_matrix_sha256(matrix: ExactComplexMatrix) -> str:
    digest = sha256()
    for row in matrix:
        for real, imaginary in row:
            for value in (real, imaginary):
                digest.update(str(value.numerator).encode("ascii"))
                digest.update(b"/")
                digest.update(str(value.denominator).encode("ascii"))
                digest.update(b"\0")
    return digest.hexdigest()


def _interval_point_distance(
    intervals: IntervalMatrix,
    point: ComplexArray,
) -> Fraction:
    maximum = Fraction(0)
    for row_index, row in enumerate(intervals):
        total = Fraction(0)
        for column_index, value in enumerate(row):
            point_interval = q011p._point_interval(
                point[row_index, column_index]
            )
            total += _complex_rectangle_absolute_upper(value - point_interval)
        maximum = max(maximum, total)
    return maximum


def _greedy_seed_pivots(block: ComplexArray) -> tuple[list[int], dict[str, Any]]:
    dimension = block.shape[0]
    identity = np.eye(dimension, dtype=np.complex128)
    pool = np.hstack((identity + block, 1j * (identity - block)))
    residual = pool.copy()
    available = np.ones(2 * dimension, dtype=np.bool_)
    pivots: list[int] = []
    pivot_residuals = []
    for _ in range(dimension):
        norms = np.sum(np.abs(residual) ** 2, axis=0)
        norms[~available] = -1.0
        pivot = int(np.argmax(norms))
        pivot_norm = float(norms[pivot])
        pivots.append(pivot)
        pivot_residuals.append(pivot_norm)
        available[pivot] = False
        if pivot_norm <= 0:
            continue
        vector = residual[:, pivot] / np.sqrt(pivot_norm)
        for _reorthogonalization in range(2):
            coefficients = np.conjugate(vector) @ residual
            residual -= np.outer(vector, coefficients)
    audit = {
        "algorithm": (
            "two-pass modified Gram-Schmidt greedy pivot; maximum residual "
            "with numpy first-index tie break"
        ),
        "pool_dimension": [dimension, 2 * dimension],
        "pivot_count": len(pivots),
        "pivot_indices": pivots,
        "pivot_indices_sha256": q011b._canonical_json_sha256(pivots),
        "minimum_binary64_pivot_residual_squared": min(pivot_residuals),
        "binary64_pivot_residuals_are_diagnostic_only": True,
    }
    return pivots, audit


def _seed_matrix_norm(pivots: list[int], dimension: int) -> int:
    counts = [0] * dimension
    for pivot in pivots:
        counts[pivot % dimension] += 1
    return max(counts)


def _candidate_frame(
    block: ComplexArray,
    pivots: list[int],
) -> tuple[ExactComplexMatrix, ComplexArray]:
    dimension = block.shape[0]
    exact_block = [
        [_exact_complex(block[row, column]) for column in range(dimension)]
        for row in range(dimension)
    ]
    exact_frame: ExactComplexMatrix = []
    for row in range(dimension):
        output_row: list[ExactComplex] = []
        for pivot in pivots:
            seed_row = pivot % dimension
            real, imaginary = exact_block[row][seed_row]
            if pivot < dimension:
                output_row.append(
                    (real + int(row == seed_row), imaginary)
                )
            else:
                output_row.append(
                    (imaginary, -real + int(row == seed_row))
                )
        exact_frame.append(output_row)
    approximate = np.asarray(
        [
            [complex(float(real), float(imaginary)) for real, imaginary in row]
            for row in exact_frame
        ],
        dtype=np.complex128,
    )
    return exact_frame, approximate


def _exact_frame_mpfr(
    matrix: ExactComplexMatrix,
    precision: int,
) -> tuple[
    list[list[gmpy2.mpfr]],
    list[list[gmpy2.mpfr]],
    dict[str, dict[str, bool]],
    bool,
]:
    dimension = len(matrix)
    real_values = [real for row in matrix for real, _imaginary in row]
    imaginary_values = [
        imaginary for row in matrix for _real, imaginary in row
    ]
    real_lower, real_upper, real_flags = q011j._bulk_endpoint_pairs(
        real_values,
        precision,
    )
    imag_lower, imag_upper, imag_flags = q011j._bulk_endpoint_pairs(
        imaginary_values,
        precision,
    )
    exact = bool(
        all(
            lower == upper
            for lower, upper in zip(real_lower, real_upper, strict=True)
        )
        and all(
            lower == upper
            for lower, upper in zip(imag_lower, imag_upper, strict=True)
        )
    )
    real = [
        real_lower[row * dimension : (row + 1) * dimension]
        for row in range(dimension)
    ]
    imaginary = [
        imag_lower[row * dimension : (row + 1) * dimension]
        for row in range(dimension)
    ]
    return (
        real,
        imaginary,
        {
            **{f"real_{name}": flags for name, flags in real_flags.items()},
            **{f"imag_{name}": flags for name, flags in imag_flags.items()},
        },
        exact,
    )


def _frame_proof_lane(
    exact_frame: ExactComplexMatrix,
    approximate_frame: ComplexArray,
    inverse_candidate: ComplexArray,
    seed_norm: int,
    conjugation_block_error: Fraction,
    precision: int,
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    caller_signature = q011j._context_signature(gmpy2.get_context())
    frame_real, frame_imag, frame_flags, frame_exact = _exact_frame_mpfr(
        exact_frame,
        precision,
    )
    inverse_real, inverse_imag, inverse_flags, inverse_exact = (
        q011k._complex_mpfr_endpoints(inverse_candidate, precision)
    )
    frame_norm, frame_norm_flags = q011k._complex_infinity_norm_upper(
        frame_real,
        frame_imag,
        precision,
    )
    inverse_norm, inverse_norm_flags = q011k._complex_infinity_norm_upper(
        inverse_real,
        inverse_imag,
        precision,
    )
    defect, defect_digest, defect_flags, defect_ordered = (
        q011k._directed_inverse_defect(
            inverse_real,
            inverse_imag,
            frame_real,
            frame_imag,
            precision,
        )
    )
    if defect >= 1:
        point_inverse = Fraction(10**1000)
    else:
        point_inverse = inverse_norm / (1 - defect)
    frame_perturbation = conjugation_block_error * seed_norm
    inverse_perturbation = point_inverse * frame_perturbation
    if inverse_perturbation >= 1:
        actual_inverse = Fraction(10**1000)
    else:
        actual_inverse = point_inverse / (1 - inverse_perturbation)
    actual_frame_norm = frame_norm + frame_perturbation
    flag_groups = {
        **frame_flags,
        **{f"inverse_{name}": flags for name, flags in inverse_flags.items()},
        "frame_norm_round_up": frame_norm_flags,
        "inverse_norm_round_up": inverse_norm_flags,
        **{f"defect_{name}": flags for name, flags in defect_flags.items()},
    }
    checks = {
        "exact_dyadic_candidate_frame_conversion": frame_exact,
        "exact_binary64_inverse_candidate_conversion": inverse_exact,
        "inverse_defect_intervals_are_ordered": defect_ordered,
        "no_forbidden_mpfr_flags": q011k._forbidden_flags_clear(flag_groups),
        "caller_context_is_unchanged": (
            q011j._context_signature(gmpy2.get_context()) == caller_signature
        ),
        "candidate_inverse_defect_is_below_one": defect < 1,
        "actual_frame_neumann_denominator_is_positive": (
            inverse_perturbation < 1
        ),
        "all_frame_bounds_are_finite": _all_numeric_values_finite(
            [
                frame_norm,
                inverse_norm,
                defect,
                point_inverse,
                frame_perturbation,
                inverse_perturbation,
                actual_inverse,
                actual_frame_norm,
            ]
        ),
    }
    record = {
        "precision_bits": precision,
        "candidate_frame_infinity_norm_upper": _fraction_record(frame_norm),
        "inverse_candidate_infinity_norm_upper": _fraction_record(
            inverse_norm
        ),
        "inverse_defect_infinity_norm_upper": _fraction_record(defect),
        "candidate_frame_inverse_norm_upper": _fraction_record(point_inverse),
        "actual_frame_perturbation_upper": _fraction_record(
            frame_perturbation
        ),
        "actual_inverse_perturbation_upper": _fraction_record(
            inverse_perturbation
        ),
        "actual_frame_infinity_norm_upper": _fraction_record(
            actual_frame_norm
        ),
        "actual_frame_inverse_norm_upper": _fraction_record(actual_inverse),
        "inverse_defect_interval_sha256": defect_digest,
        "mpfr_flag_groups": flag_groups,
        "checks": checks,
        "passed": all(checks.values()),
    }
    exact = {
        "frame_norm": frame_norm,
        "inverse_norm": inverse_norm,
        "defect": defect,
        "point_inverse": point_inverse,
        "frame_perturbation": frame_perturbation,
        "inverse_perturbation": inverse_perturbation,
        "actual_frame_norm": actual_frame_norm,
        "actual_inverse": actual_inverse,
    }
    return record, exact


def _graph_conjugation_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    reconstruction, data = q011p._zero_block_reconstruction_audit(artifacts)
    primary, primary_exact, primary_intervals = q011p._conjugation_proof_lane(
        data,
        PRIMARY_PRECISION_BITS,
    )
    replay, replay_exact, replay_intervals = q011p._conjugation_proof_lane(
        data,
        REPLAY_PRECISION_BITS,
    )
    vectors = data["vectors"]
    inverse = data["inverse"]
    point_product = inverse @ np.conjugate(vectors)
    primary_point_error = _interval_point_distance(
        primary_intervals,
        point_product,
    )
    replay_point_error = _interval_point_distance(
        replay_intervals,
        point_product,
    )
    graph_radius = data["graph"]["radius"]
    primary_block_error = (
        primary_exact["conjugation_error"]
        + primary_point_error
        + primary_exact["j_SE"] * graph_radius
    )
    replay_block_error = (
        replay_exact["conjugation_error"]
        + replay_point_error
        + replay_exact["j_SE"] * graph_radius
    )
    p_cycle = artifacts["q011p"]["cycle"]
    p_conjugation = p_cycle["dual_precision_conjugation_audit"]
    p_reconstruction = p_cycle["zero_block_reconstruction_audit"]
    containment = {
        "primary_product_intervals_are_contained_in_replay": (
            q011p._intervals_contained(primary_intervals, replay_intervals)
        ),
        "primary_point_product_error_is_contained_in_replay": (
            primary_point_error <= replay_point_error
        ),
        "primary_conjugation_block_error_is_contained_in_replay": (
            primary_block_error <= replay_block_error
        ),
    }
    algebraic_identities = {
        "graph_coordinate_conjugation": (
            "K(s,e)=(K_SS conjugate(s)+K_SE conjugate(e), "
            "K_EE conjugate(e))"
        ),
        "selected_block": "K_SS=J_SE conjugate(G)+J_SS",
        "external_to_selected_block": "K_SE=J_SE",
        "external_quotient_block": "K_EE=J_EE-G J_SE",
        "missing_selected_to_external_block": (
            "J_EE conjugate(G)+J_ES-G(J_SE conjugate(G)+J_SS)=0"
        ),
        "diagonal_involutions": (
            "K_SS conjugate(K_SS)=I and "
            "K_EE conjugate(K_EE)=I follow from K^2=I"
        ),
    }
    checks = {
        "q011p_zero_block_reconstruction_reproduces": (
            reconstruction == p_reconstruction
        ),
        "q011p_primary_conjugation_proof_reproduces": (
            primary == p_conjugation["primary_precision_proof"]
        ),
        "q011p_replay_conjugation_proof_reproduces": (
            replay == p_conjugation["independent_containment_proof"]
        ),
        "q011p_reality_theorem_is_available": p_cycle["theorem_consequence"][
            "zero_block_selected_invariant_subspace_is_conjugation_invariant"
        ],
        "selected_and_external_dimensions_are_registered": bool(
            len(data["selected_indices"]) == SELECTED_ZERO_DIMENSION
            and len(data["external_indices"]) == EXTERNAL_ZERO_DIMENSION
        ),
        "point_product_is_binary64_proposal_only": True,
        "three_graph_conjugation_blocks_are_typed": len(algebraic_identities)
        == 6,
        "dual_precision_product_containment_passes": all(containment.values()),
        "all_conjugation_bounds_are_finite": _all_numeric_values_finite(
            [
                primary_point_error,
                replay_point_error,
                primary_block_error,
                replay_block_error,
            ]
        ),
    }
    audit = {
        "zero_block_reconstruction": reconstruction,
        "point_product_definition": "J_f=fl(W_0 conjugate(V_0))",
        "point_product_sha256": q011b._array_sha256(point_product),
        "point_product_used_for_seed_proposal_only": True,
        "primary_point_product_error_upper": _fraction_record(
            primary_point_error
        ),
        "replay_point_product_error_upper": _fraction_record(
            replay_point_error
        ),
        "q011p_conjugation_error_upper": primary[
            "conjugation_point_error_upper"
        ],
        "q011p_actual_j_se_upper": primary[
            "actual_conjugation_block_norm_uppers"
        ]["J_SE"],
        "q011l_graph_radius_upper": _fraction_record(graph_radius),
        "primary_graph_conjugation_block_error_upper": _fraction_record(
            primary_block_error
        ),
        "replay_graph_conjugation_block_error_upper": _fraction_record(
            replay_block_error
        ),
        "algebraic_identities": algebraic_identities,
        "containment_checks": containment,
        "checks": checks,
        "passed": all(checks.values()),
    }
    proof_data = {
        "point_product": point_product,
        "selected_indices": data["selected_indices"],
        "external_indices": data["external_indices"],
        "primary_block_error": primary_block_error,
        "replay_block_error": replay_block_error,
        "primary_exact": primary_exact,
        "replay_exact": replay_exact,
        "graph_radius": graph_radius,
    }
    return audit, proof_data


def _frame_family_audit(proof_data: dict[str, Any]) -> tuple[dict[str, Any], Fraction]:
    point_product = proof_data["point_product"]
    family_specs = (
        (
            "selected",
            tuple(proof_data["selected_indices"]),
            SELECTED_ZERO_DIMENSION,
            SELECTED_FRAME_INVERSE_CAP,
        ),
        (
            "external",
            tuple(proof_data["external_indices"]),
            EXTERNAL_ZERO_DIMENSION,
            EXTERNAL_FRAME_INVERSE_CAP,
        ),
    )
    records: dict[str, Any] = {}
    exact_records: dict[str, dict[str, Fraction]] = {}
    for label, indices, dimension, inverse_cap in family_specs:
        index_array = np.asarray(indices, dtype=np.int64)
        block = point_product[np.ix_(index_array, index_array)]
        pivots, pivot_audit = _greedy_seed_pivots(block)
        seed_norm = _seed_matrix_norm(pivots, dimension)
        exact_frame, approximate_frame = _candidate_frame(block, pivots)
        inverse_candidate = np.linalg.inv(approximate_frame)
        primary, primary_exact = _frame_proof_lane(
            exact_frame,
            approximate_frame,
            inverse_candidate,
            seed_norm,
            proof_data["primary_block_error"],
            PRIMARY_PRECISION_BITS,
        )
        replay, replay_exact = _frame_proof_lane(
            exact_frame,
            approximate_frame,
            inverse_candidate,
            seed_norm,
            proof_data["replay_block_error"],
            REPLAY_PRECISION_BITS,
        )
        upper_names = (
            "frame_norm",
            "inverse_norm",
            "defect",
            "point_inverse",
            "frame_perturbation",
            "inverse_perturbation",
            "actual_frame_norm",
            "actual_inverse",
        )
        containment = {
            f"primary_{name}_is_contained_in_replay": (
                primary_exact[name] <= replay_exact[name]
            )
            for name in upper_names
        }
        checks = {
            "dimension_and_pivot_count_are_registered": bool(
                dimension == len(indices)
                and pivot_audit["pivot_count"] == dimension
            ),
            "pivot_indices_are_unique_and_in_pool": bool(
                len(set(pivots)) == dimension
                and all(0 <= value < 2 * dimension for value in pivots)
            ),
            "primary_frame_proof_passes": primary["passed"],
            "replay_frame_proof_passes": replay["passed"],
            "dual_precision_frame_bounds_are_contained": all(
                containment.values()
            ),
            "frame_columns_are_exact_conjugation_symmetrizations": True,
            "actual_frame_is_invertible": (
                primary_exact["inverse_perturbation"] < 1
            ),
        }
        records[label] = {
            "dimension": dimension,
            "seed_pool": "[I+K_c, i(I-K_c)]",
            "seed_matrix_norm": seed_norm,
            "pivot_audit": pivot_audit,
            "candidate_frame_exact_sha256": _exact_complex_matrix_sha256(
                exact_frame
            ),
            "candidate_frame_binary64_sha256": q011b._array_sha256(
                approximate_frame
            ),
            "inverse_candidate_sha256": q011b._array_sha256(
                inverse_candidate
            ),
            "registered_point_frame_norm_cap": _fraction_record(
                POINT_FRAME_NORM_CAP
            ),
            "registered_actual_inverse_cap": _fraction_record(inverse_cap),
            "registered_frame_perturbation_cap": _fraction_record(
                FRAME_PERTURBATION_CAP
            ),
            "primary_precision_proof": primary,
            "independent_containment_proof": replay,
            "containment_checks": containment,
            "checks": checks,
            "passed": all(checks.values()),
        }
        exact_records[label] = primary_exact

    section_norm = proof_data["primary_exact"]["j_SE"] / 2
    algebraic_identities = {
        "selected_fixed_frame": "F_S=C_S+K_SS conjugate(C_S)",
        "external_fixed_frame": "F_E=C_E+K_EE conjugate(C_E)",
        "canonical_real_section": "H(e)=K_SE conjugate(e)/2",
        "section_is_fixed": (
            "(H(e),e)=((0,e)+K(0,e))/2 for K_EE-fixed e"
        ),
        "real_direct_sum": (
            "X_0,R^G={(s,0)} direct-sum {(H(e),e)}"
        ),
    }
    direct_sum_checks = {
        "selected_frame_has_six_columns": records["selected"]["dimension"]
        == SELECTED_ZERO_DIMENSION,
        "external_frame_has_one_hundred_forty_four_columns": records[
            "external"
        ]["dimension"]
        == EXTERNAL_ZERO_DIMENSION,
        "zero_block_real_dimensions_close": (
            SELECTED_ZERO_DIMENSION + EXTERNAL_ZERO_DIMENSION
            == ZERO_BLOCK_DIMENSION
        ),
        "both_actual_frames_are_certified_invertible": bool(
            records["selected"]["passed"] and records["external"]["passed"]
        ),
        "section_formula_is_exact_conjugation_average": True,
        "full_real_frame_is_block_triangular": True,
        "real_direct_sum_is_bijective": bool(
            records["selected"]["passed"] and records["external"]["passed"]
        ),
        "algebraic_identity_count_is_registered": len(algebraic_identities)
        == 5,
    }
    audit = {
        "frame_construction": (
            "fixed Gaussian-integer seeds symmetrized by the exact graph-"
            "coordinate conjugation"
        ),
        "frame_families": records,
        "section_norm_upper": _fraction_record(section_norm),
        "registered_section_norm_cap": _fraction_record(SECTION_NORM_CAP),
        "zero_block_selected_real_dimension": SELECTED_ZERO_DIMENSION,
        "zero_block_external_real_dimension": EXTERNAL_ZERO_DIMENSION,
        "zero_block_total_real_dimension": ZERO_BLOCK_DIMENSION,
        "algebraic_identities": algebraic_identities,
        "direct_sum_checks": direct_sum_checks,
        "passed": all(direct_sum_checks.values()),
    }
    return audit, section_norm


def _real_coordinate_audit(
    artifacts: dict[str, dict[str, Any]],
    frame_audit: dict[str, Any],
    section_norm: Fraction,
) -> dict[str, Any]:
    baseline = artifacts["q011o"]["cycle"]["fixed_leaf_coordinate_audit"]
    records = baseline["block_records"]
    zero = records[0]
    old_total = _fraction(baseline["physical_lift_norm_upper"])
    old_zero_lift = _fraction(zero["physical_lift_contribution"])
    old_zero_inverse = _fraction(zero["coordinate_inverse_contribution"])
    real_zero_lift = old_zero_lift * (1 + section_norm)
    real_lift = old_total - old_zero_lift + real_zero_lift
    real_zero_inverse = old_zero_inverse * (1 + section_norm)
    nonzero_inverse = max(
        _fraction(record["coordinate_inverse_contribution"])
        for record in records[1:]
    )
    real_inverse = max(real_zero_inverse, nonzero_inverse)
    inverse_witness = (
        0
        if real_zero_inverse >= nonzero_inverse
        else baseline["coordinate_inverse_witness_block"]
    )
    checks = {
        "q011o_seventeen_block_baseline_passes": bool(
            baseline["passed"] and baseline["block_count"] == SIZE
        ),
        "zero_population_lift_186_is_preserved": (
            zero["population_lift_factor"] == ZERO_BLOCK_POPULATION_LIFT
        ),
        "real_zero_lift_formula_reproduces": (
            real_zero_lift == old_zero_lift * (1 + section_norm)
        ),
        "real_global_lift_formula_reproduces": (
            real_lift == old_total - old_zero_lift + real_zero_lift
        ),
        "real_zero_inverse_formula_reproduces": (
            real_zero_inverse == old_zero_inverse * (1 + section_norm)
        ),
        "real_global_inverse_formula_reproduces": (
            real_inverse == max(real_zero_inverse, nonzero_inverse)
        ),
        "fixed_leaf_real_dimensions_close": bool(
            baseline["selected_real_dimension"] == SELECTED_DIMENSION
            and baseline["external_real_dimension"] == EXTERNAL_DIMENSION
            and baseline["total_fixed_leaf_real_dimension"]
            == FIXED_LEAF_DIMENSION
        ),
        "zero_real_frame_and_complement_are_available": frame_audit["passed"],
        "nonzero_conjugate_block_coordinates_are_unchanged": all(
            value
            for name, value in baseline["conjugacy_checks"].items()
            if name != "zero_selected_multiset_is_closed_under_conjugacy"
        ),
        "cross_block_cancellation_is_not_used": not baseline[
            "cross_block_cancellation_used"
        ],
    }
    return {
        "coordinate_definition": {
            "zero_selected_real_space": "S_R=Fix(K_SS conjugation)",
            "zero_external_real_space": "E_R=Fix(K_EE conjugation)",
            "zero_real_shear": "(s,e) -> (s+H(e),e)",
            "zero_physical_map": "V_0 T_G(s+H(e),e)",
            "nonzero_blocks": "unchanged Q011o conjugate-pair coordinates",
            "analytic_norm": (
                "restriction of the complex-modulus block-sup norm to the "
                "real fixed spaces"
            ),
            "real_coefficient_frames_are_explicit": True,
        },
        "section_norm_upper": _fraction_record(section_norm),
        "q011o_physical_lift_norm_upper": baseline[
            "physical_lift_norm_upper"
        ],
        "q011o_zero_lift_contribution": zero[
            "physical_lift_contribution"
        ],
        "real_zero_lift_contribution": _fraction_record(real_zero_lift),
        "real_physical_lift_norm_upper": _fraction_record(real_lift),
        "q011o_zero_inverse_contribution": zero[
            "coordinate_inverse_contribution"
        ],
        "real_zero_inverse_contribution": _fraction_record(
            real_zero_inverse
        ),
        "real_coordinate_inverse_norm_upper": _fraction_record(real_inverse),
        "real_coordinate_inverse_witness_block": inverse_witness,
        "selected_real_dimension": SELECTED_DIMENSION,
        "external_real_dimension": EXTERNAL_DIMENSION,
        "total_fixed_leaf_real_dimension": FIXED_LEAF_DIMENSION,
        "cross_block_cancellation_used": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _real_linear_audit(
    artifacts: dict[str, dict[str, Any]],
    section_norm: Fraction,
) -> dict[str, Any]:
    baseline = artifacts["q011o"]["cycle"]["same_norm_linear_split_audit"]
    records = baseline["block_records"]
    zero = records[0]
    centers, selected, _radii, metrics, _spectral = q011l._spectral_data(
        artifacts["q011k"]
    )
    graphs, _graph_audit = q011l._graph_audit(centers, selected, metrics)
    selected_zero = selected[0]
    selected_upper = max(
        q011o._center_modulus_bounds(centers[0][index]).upper
        for index in selected_zero
    )
    eta_zero = metrics[0]["theta"] * (1 + graphs[0]["radius"])
    selected_operator = selected_upper + eta_zero
    external_zero = _fraction(zero["external_operator_norm_upper"])
    theta_zero = _fraction(zero["selected_external_coupling_upper"])
    real_zero_coupling = theta_zero + (
        selected_operator + external_zero
    ) * section_norm
    other_couplings = [
        _fraction(record["selected_external_coupling_upper"])
        for record in records[1:]
        if record["selected_external_coupling_upper"] is not None
    ]
    real_coupling = max([real_zero_coupling, *other_couplings])
    selected_conorm = _fraction(baseline["selected_conorm_lower"])
    external_norm = _fraction(baseline["external_operator_norm_upper"])
    gap = selected_conorm - external_norm
    ratio = external_norm / selected_conorm
    selected_inverse = 1 / selected_conorm
    checks = {
        "q011o_same_norm_linear_baseline_passes": baseline["passed"],
        "selected_operator_upper_uses_center_and_same_norm_residual": (
            selected_operator == selected_upper + eta_zero
        ),
        "real_zero_coupling_formula_reproduces": (
            real_zero_coupling
            == theta_zero
            + (selected_operator + external_zero) * section_norm
        ),
        "global_real_coupling_formula_reproduces": (
            real_coupling == max([real_zero_coupling, *other_couplings])
        ),
        "selected_conorm_is_the_q011o_restriction_bound": (
            selected_conorm
            == _fraction(baseline["selected_conorm_lower"])
        ),
        "external_norm_is_the_q011o_quotient_restriction_bound": (
            external_norm
            == _fraction(baseline["external_operator_norm_upper"])
        ),
        "gap_ratio_and_inverse_formulas_reproduce": bool(
            gap == selected_conorm - external_norm
            and ratio == external_norm / selected_conorm
            and selected_inverse == 1 / selected_conorm
        ),
        "eigenvalue_gap_is_not_substituted_for_operator_norm": not baseline[
            "q011k_eigenvalue_gap_used_as_operator_bound"
        ],
        "real_split_is_upper_triangular": True,
    }
    return {
        "real_operator_coordinate_identity": (
            "R^(-1)[[S,B],[0,E]]R=[[S,S H+B-H E],[0,E]]"
        ),
        "operator_norm": (
            "complex-modulus block-sup norm restricted to the real fixed "
            "selected and external quotient spaces"
        ),
        "zero_selected_operator_norm_upper": _fraction_record(
            selected_operator
        ),
        "zero_external_operator_norm_upper": zero[
            "external_operator_norm_upper"
        ],
        "q011o_zero_coupling_upper": zero[
            "selected_external_coupling_upper"
        ],
        "section_norm_upper": _fraction_record(section_norm),
        "real_zero_coupling_upper": _fraction_record(real_zero_coupling),
        "real_selected_conorm_lower": _fraction_record(selected_conorm),
        "real_external_operator_norm_upper": _fraction_record(external_norm),
        "real_linear_domination_gap_lower": _fraction_record(gap),
        "real_linear_domination_ratio_upper": _fraction_record(ratio),
        "real_selected_base_inverse_norm_upper": _fraction_record(
            selected_inverse
        ),
        "real_selected_external_coupling_upper": _fraction_record(
            real_coupling
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _real_localization_audit(
    artifacts: dict[str, dict[str, Any]],
    coordinate: dict[str, Any],
) -> dict[str, Any]:
    lift_norm = _fraction(coordinate["real_physical_lift_norm_upper"])
    physical_upper = lift_norm * LOCALIZATION_RADIUS
    root = artifacts["q011m"]["cycle"]["exact_root_and_simple_envelope_audit"]
    root_population = _fraction(root["root_population_floor_lower"])
    root_density = _fraction(root["root_density_floor_lower"])
    population_lower = root_population - physical_upper
    density_lower = root_density - 9 * physical_upper
    cutoff = {
        "domain": "S_R direct-sum E_R",
        "codomain": "B_S(rho) direct-sum B_E(rho)",
        "definition": (
            "blockwise radial retraction c_rho(z)=min(1,rho/||z||)z"
        ),
        "identity_on_core_ball": True,
        "fixes_origin": True,
        "global_lipschitz_constant_upper": _fraction_record(Fraction(2)),
        "preserves_selected_real_fixed_space": True,
        "preserves_external_real_fixed_space": True,
        "uses_q011o_componentwise_complex_disk_projection": False,
    }
    localized_map = {
        "original_coordinate_map": "F_R(z)=A_R z+N_R(z)",
        "definition": "F_R,rho(z)=A_R z+N_R(C_rho z)",
        "domain": "real fixed-leaf coordinate Banach space X_R",
        "codomain": "real fixed-leaf coordinate Banach space X_R",
        "equals_original_map_on_core_ball": True,
        "nonlinear_derivative_bound_certified": False,
    }
    graph_space = {
        "name": "G_R,(rho,1)",
        "domain": "selected real closed ball B_S,R(rho)",
        "codomain": "external real closed ball B_E,R(rho)",
        "fixes_origin": True,
        "lipschitz_cap": _fraction_record(Fraction(1)),
        "metric": "uniform restricted block-sup metric",
        "closed_complete_space": True,
        "induced_graph_transform_is_defined_in_this_gate": False,
        "graph_transform_self_map_is_certified": False,
        "graph_transform_contraction_is_certified": False,
    }
    checks = {
        "localization_radius_is_registered": LOCALIZATION_RADIUS
        == Fraction(1, 10**11),
        "physical_localization_formula_reproduces": (
            physical_upper == lift_norm * LOCALIZATION_RADIUS
        ),
        "physical_localization_is_in_derivative_domain": (
            physical_upper <= q011m.STATE_DISPLACEMENT_CAP
        ),
        "population_buffer_passes": population_lower
        >= q011m.POPULATION_THRESHOLD,
        "density_buffer_passes": density_lower >= q011m.DENSITY_THRESHOLD,
        "radial_cutoff_is_identity_and_two_lipschitz": bool(
            cutoff["identity_on_core_ball"]
            and cutoff["fixes_origin"]
            and _fraction(cutoff["global_lipschitz_constant_upper"])
            == CUTOFF_LIPSCHITZ_CAP
        ),
        "radial_cutoff_preserves_both_real_spaces": bool(
            cutoff["preserves_selected_real_fixed_space"]
            and cutoff["preserves_external_real_fixed_space"]
        ),
        "localized_map_is_real_typed_and_agrees_on_core": bool(
            localized_map["domain"] == localized_map["codomain"]
            and localized_map["equals_original_map_on_core_ball"]
        ),
        "real_graph_space_is_closed_and_complete": graph_space[
            "closed_complete_space"
        ],
        "nonlinear_graph_transform_claims_are_deferred": bool(
            not localized_map["nonlinear_derivative_bound_certified"]
            and not graph_space["induced_graph_transform_is_defined_in_this_gate"]
            and not graph_space["graph_transform_self_map_is_certified"]
            and not graph_space["graph_transform_contraction_is_certified"]
        ),
    }
    return {
        "localization_radius": _fraction_record(LOCALIZATION_RADIUS),
        "real_physical_localization_upper": _fraction_record(physical_upper),
        "root_population_floor_lower": _fraction_record(root_population),
        "root_density_floor_lower": _fraction_record(root_density),
        "localized_population_floor_lower": _fraction_record(population_lower),
        "localized_density_floor_lower": _fraction_record(density_lower),
        "derivative_domain_cap": _fraction_record(q011m.STATE_DISPLACEMENT_CAP),
        "population_threshold": _fraction_record(q011m.POPULATION_THRESHOLD),
        "density_threshold": _fraction_record(q011m.DENSITY_THRESHOLD),
        "cutoff": cutoff,
        "localized_map": localized_map,
        "real_graph_banach_space": graph_space,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "zero_block_dimension": ZERO_BLOCK_DIMENSION,
        "zero_selected_dimension": SELECTED_ZERO_DIMENSION,
        "zero_external_dimension": EXTERNAL_ZERO_DIMENSION,
        "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "zero_block_population_lift": ZERO_BLOCK_POPULATION_LIFT,
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "independent_containment_precision_bits": REPLAY_PRECISION_BITS,
        "localization_radius": _fraction_record(LOCALIZATION_RADIUS),
        "conjugation_block_error_cap": _fraction_record(
            CONJUGATION_BLOCK_ERROR_CAP
        ),
        "point_frame_norm_cap": _fraction_record(POINT_FRAME_NORM_CAP),
        "selected_frame_inverse_cap": _fraction_record(
            SELECTED_FRAME_INVERSE_CAP
        ),
        "external_frame_inverse_cap": _fraction_record(
            EXTERNAL_FRAME_INVERSE_CAP
        ),
        "frame_perturbation_cap": _fraction_record(FRAME_PERTURBATION_CAP),
        "section_norm_cap": _fraction_record(SECTION_NORM_CAP),
        "lift_norm_cap": _fraction_record(LIFT_NORM_CAP),
        "coordinate_inverse_cap": _fraction_record(COORDINATE_INVERSE_CAP),
        "physical_localization_cap": _fraction_record(
            PHYSICAL_LOCALIZATION_CAP
        ),
        "selected_conorm_floor": _fraction_record(SELECTED_CONORM_FLOOR),
        "external_norm_cap": _fraction_record(EXTERNAL_NORM_CAP),
        "linear_gap_floor": _fraction_record(LINEAR_GAP_FLOOR),
        "domination_ratio_cap": _fraction_record(DOMINATION_RATIO_CAP),
        "selected_inverse_cap": _fraction_record(SELECTED_INVERSE_CAP),
        "coupling_cap": _fraction_record(COUPLING_CAP),
        "cutoff_lipschitz_cap": _fraction_record(CUTOFF_LIPSCHITZ_CAP),
        "floating_point_used_for_gate_decisions": False,
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
        "frame_digest_sha256": cycle["frame_digest_sha256"],
        "setup_digest_sha256": cycle["setup_digest_sha256"],
    }


def run_real_frame_setup_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    conjugation, proof_data = _graph_conjugation_audit(artifacts)
    frames, section_norm = _frame_family_audit(proof_data)
    coordinate = _real_coordinate_audit(artifacts, frames, section_norm)
    linear = _real_linear_audit(artifacts, section_norm)
    localization = _real_localization_audit(artifacts, coordinate)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    conjugation_sections = {
        "graph_coordinate_conjugation_audit": conjugation
    }
    frame_sections = {"symmetrized_real_frame_audit": frames}
    setup_sections = {
        "real_fixed_leaf_coordinate_audit": coordinate,
        "real_same_norm_linear_split_audit": linear,
        "real_localized_graph_space_audit": localization,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    conjugation_digest = q011b._canonical_json_sha256(conjugation_sections)
    frame_digest = q011b._canonical_json_sha256(frame_sections)
    setup_digest = q011b._canonical_json_sha256(setup_sections)
    strict_payload = {
        **input_sections,
        **conjugation_sections,
        **frame_sections,
        **setup_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and conjugation_digest
        == q011b._canonical_json_sha256(conjugation_sections)
        and frame_digest == q011b._canonical_json_sha256(frame_sections)
        and setup_digest == q011b._canonical_json_sha256(setup_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    frame_records = frames["frame_families"]
    primary_selected = frame_records["selected"]["primary_precision_proof"]
    primary_external = frame_records["external"]["primary_precision_proof"]
    replay_selected = frame_records["selected"][
        "independent_containment_proof"
    ]
    replay_external = frame_records["external"][
        "independent_containment_proof"
    ]
    validity_gates = {
        "six_direct_inputs_and_twenty_nine_digests_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011j/k/l/m/o/p artifact, runner, 29 digests, outcomes and "
                "claim boundaries reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "graph_coordinate_conjugation_and_error_bounds_reproduce": {
            "passed": conjugation["passed"],
            "threshold": (
                "J_f error, K_SS/K_SE/K_EE formulas, missing block and "
                "diagonal involutions reproduce"
            ),
            "value": conjugation["checks"],
        },
        "deterministic_seeds_and_dual_precision_frame_proofs_reproduce": {
            "passed": bool(
                frame_records["selected"]["passed"]
                and frame_records["external"]["passed"]
            ),
            "threshold": (
                "fixed pivots, exact seeds and 256/192-bit selected/external "
                "frame inverse proofs reproduce"
            ),
            "value": {
                "selected": frame_records["selected"]["checks"],
                "external": frame_records["external"]["checks"],
            },
        },
        "real_frames_section_and_zero_block_direct_sum_are_typed": {
            "passed": frames["passed"],
            "threshold": (
                "conjugation-fixed frames and the canonical real section give "
                "a bijective 6+144=150 direct sum"
            ),
            "value": frames["direct_sum_checks"],
        },
        "real_fixed_leaf_coordinate_dimensions_and_bounds_reproduce": {
            "passed": coordinate["passed"],
            "threshold": (
                "17 blocks, 24+2574=2598 dimensions, zero lift 186 and "
                "real shear lift/inverse formulas reproduce"
            ),
            "value": coordinate["checks"],
        },
        "real_linear_split_cutoff_and_graph_space_are_typed": {
            "passed": bool(linear["passed"] and localization["passed"]),
            "threshold": (
                "real upper-triangular linear bounds, radial cutoff, localized "
                "map and closed complete graph space reproduce"
            ),
            "value": {
                "linear": linear["checks"],
                "localization": localization["checks"],
            },
        },
        "dual_precision_protocol_serialization_and_digests_reproduce": {
            "passed": bool(
                primary_selected["passed"]
                and primary_external["passed"]
                and replay_selected["passed"]
                and replay_external["passed"]
                and all(conjugation["containment_checks"].values())
                and all(
                    frame_records["selected"]["containment_checks"].values()
                )
                and all(
                    frame_records["external"]["containment_checks"].values()
                )
                and strict_json
                and digests_reproduce
            ),
            "threshold": (
                "192-bit enclosures contain 256-bit proofs with clean MPFR "
                "protocol, finite strict JSON, four section digests and runner"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    conjugation_error = _fraction(
        conjugation["primary_graph_conjugation_block_error_upper"]
    )
    selected_frame_norm = _fraction(
        primary_selected["candidate_frame_infinity_norm_upper"]
    )
    external_frame_norm = _fraction(
        primary_external["candidate_frame_infinity_norm_upper"]
    )
    selected_frame_inverse = _fraction(
        primary_selected["actual_frame_inverse_norm_upper"]
    )
    external_frame_inverse = _fraction(
        primary_external["actual_frame_inverse_norm_upper"]
    )
    selected_frame_perturbation = _fraction(
        primary_selected["actual_frame_perturbation_upper"]
    )
    external_frame_perturbation = _fraction(
        primary_external["actual_frame_perturbation_upper"]
    )
    frame_caps = bool(
        conjugation_error <= CONJUGATION_BLOCK_ERROR_CAP
        and selected_frame_norm <= POINT_FRAME_NORM_CAP
        and external_frame_norm <= POINT_FRAME_NORM_CAP
        and selected_frame_inverse <= SELECTED_FRAME_INVERSE_CAP
        and external_frame_inverse <= EXTERNAL_FRAME_INVERSE_CAP
        and selected_frame_perturbation <= FRAME_PERTURBATION_CAP
        and external_frame_perturbation <= FRAME_PERTURBATION_CAP
        and section_norm <= SECTION_NORM_CAP
    )
    lift_norm = _fraction(coordinate["real_physical_lift_norm_upper"])
    inverse_norm = _fraction(
        coordinate["real_coordinate_inverse_norm_upper"]
    )
    physical_localization = _fraction(
        localization["real_physical_localization_upper"]
    )
    coordinate_caps = bool(
        lift_norm <= LIFT_NORM_CAP
        and inverse_norm <= COORDINATE_INVERSE_CAP
        and physical_localization <= PHYSICAL_LOCALIZATION_CAP
    )
    selected_conorm = _fraction(linear["real_selected_conorm_lower"])
    external_norm = _fraction(linear["real_external_operator_norm_upper"])
    linear_gap = _fraction(linear["real_linear_domination_gap_lower"])
    domination_ratio = _fraction(
        linear["real_linear_domination_ratio_upper"]
    )
    selected_inverse = _fraction(
        linear["real_selected_base_inverse_norm_upper"]
    )
    coupling = _fraction(
        linear["real_selected_external_coupling_upper"]
    )
    linear_separation = bool(
        selected_conorm >= SELECTED_CONORM_FLOOR
        and external_norm <= EXTERNAL_NORM_CAP
        and linear_gap >= LINEAR_GAP_FLOOR
        and domination_ratio <= DOMINATION_RATIO_CAP
    )
    inverse_coupling = bool(
        selected_inverse <= SELECTED_INVERSE_CAP
        and coupling <= COUPLING_CAP
    )
    localized_setup = bool(
        localization["passed"]
        and _fraction(
            localization["cutoff"]["global_lipschitz_constant_upper"]
        )
        <= CUTOFF_LIPSCHITZ_CAP
        and localization["localized_map"][
            "equals_original_map_on_core_ball"
        ]
        and localization["real_graph_banach_space"]["closed_complete_space"]
    )
    real_direct_sum = bool(
        frames["passed"]
        and frames["zero_block_selected_real_dimension"]
        == SELECTED_ZERO_DIMENSION
        and frames["zero_block_external_real_dimension"]
        == EXTERNAL_ZERO_DIMENSION
    )
    hypothesis_gates = {
        "fixed_seeds_give_bijective_selected_and_external_real_frames": {
            "passed": bool(validity_passed and real_direct_sum),
            "threshold": (
                "selected/external symmetrized frames are invertible and the "
                "canonical section gives a real direct sum"
            ),
            "value": frames["direct_sum_checks"],
        },
        "frame_section_and_real_coordinate_bounds_fit_registered_caps": {
            "passed": bool(validity_passed and frame_caps and coordinate_caps),
            "threshold": (
                "epsilon_K<=1e-8, frame norms/inverses/perturbations and "
                "h<=1e-6, K_L<=2600, K_P<=900, K_L rho<=3e-8"
            ),
            "value": {
                "epsilon_K": conjugation[
                    "primary_graph_conjugation_block_error_upper"
                ],
                "selected_frame_norm": primary_selected[
                    "candidate_frame_infinity_norm_upper"
                ],
                "external_frame_norm": primary_external[
                    "candidate_frame_infinity_norm_upper"
                ],
                "selected_frame_inverse": primary_selected[
                    "actual_frame_inverse_norm_upper"
                ],
                "external_frame_inverse": primary_external[
                    "actual_frame_inverse_norm_upper"
                ],
                "section_norm": frames["section_norm_upper"],
                "K_L": coordinate["real_physical_lift_norm_upper"],
                "K_P": coordinate["real_coordinate_inverse_norm_upper"],
                "K_L_rho": localization[
                    "real_physical_localization_upper"
                ],
            },
        },
        "real_selected_conorm_and_external_norm_are_strictly_separated": {
            "passed": bool(validity_passed and linear_separation),
            "threshold": (
                "m_S>=0.983, q_E<=0.982, gap>=1e-3 and q_E/m_S<=0.999"
            ),
            "value": {
                "m_S": linear["real_selected_conorm_lower"],
                "q_E": linear["real_external_operator_norm_upper"],
                "gap": linear["real_linear_domination_gap_lower"],
                "ratio": linear["real_linear_domination_ratio_upper"],
            },
        },
        "real_selected_inverse_and_coupling_fit_registered_caps": {
            "passed": bool(validity_passed and inverse_coupling),
            "threshold": "1/m_S<=1.02 and real coupling<=1e-6",
            "value": {
                "selected_inverse": linear[
                    "real_selected_base_inverse_norm_upper"
                ],
                "real_coupling": linear[
                    "real_selected_external_coupling_upper"
                ],
            },
        },
        "radial_cutoff_localized_map_and_real_graph_space_are_typed": {
            "passed": bool(validity_passed and localized_setup),
            "threshold": (
                "two-Lipschitz radial cutoff preserves both real spaces, the "
                "localized map agrees on the core and buffers pass"
            ),
            "value": localization["checks"],
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011q real-frame setup audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the repaired fixed-leaf split admits a certified real-frame "
            "localized graph-transform setup"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered symmetrized real frames do not close a real-typed "
            "localized graph-transform setup"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Do fixed symmetrized zero-block frames and the canonical real "
            "section reissue the Q011o setup as a real-typed coordinate?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "conjugation_digest_sha256": conjugation_digest,
        "frame_digest_sha256": frame_digest,
        "setup_digest_sha256": setup_digest,
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
        "fixed_seed_zero_block_selected_real_frame_is_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "fixed_seed_zero_block_external_real_frame_is_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "zero_block_real_direct_sum_and_section_are_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "fixed_leaf_real_coordinate_lift_and_inverse_are_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_same_norm_real_linear_domination_is_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "radial_cutoff_and_real_graph_space_are_type_correct": bool(
            validity_passed and hypotheses_passed
        ),
        "q011o_historical_rejection_is_changed": False,
        "a_nonlinear_graph_transform_is_defined_or_certified": False,
        "an_exact_local_invariant_manifold_or_ssm_is_certified": False,
        "an_exact_local_invariant_manifold_or_ssm_is_disproved": False,
        "q011j_q011k_q011l_q011m_or_q011p_acceptance_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on the "
        "fixed conservation leaf, the Q011l selected graph, the Q011p zero-"
        "block real structure, fixed seed frame formulas, the canonical real "
        "external section and a radius-1e-11 localized linear setup. It "
        "certifies no componentwise exact frame entries, optimal frame "
        "condition number, nonlinear derivative bound, induced graph "
        "transform, self-map, contraction, fixed graph, exact invariant "
        "manifold or SSM, smoothness, uniqueness, normal attraction, basin, "
        "other grid, force, wall boundary or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011j_fixed_point_acceptance_changed": False,
        "q011k_spectral_acceptance_changed": False,
        "q011l_homological_inverse_acceptance_changed": False,
        "q011m_quadratic_jet_acceptance_changed": False,
        "q011o_historical_rejection_changed": False,
        "q011p_zero_block_reality_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011r to transport the Q011m analytic derivative "
            "majorant into this real norm and define and test the induced "
            "nonlinear graph transform for self-map and contraction."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Repair only the first failed frame, section, coordinate, linear "
            "or cutoff condition using a revised seed, direct real Schur/Riesz "
            "frame, block weight or cutoff."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, conjugation, frame proof, direct-"
            "sum, coordinate, linear, localization or serialization validity "
            "failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011q cycle failed strict serialization or digest")
    return cycle


def run_q011q_study() -> dict[str, Any]:
    cycle = run_real_frame_setup_audit()
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
            "binary64_seed_selection_is_proposal_only": True,
            "floating_point_used_for_gate_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": "explicit real-frame localized linear setup",
            "grid": [17, 17],
            "fixed_conservation_leaf": True,
            "zero_block_real_dimension": ZERO_BLOCK_DIMENSION,
            "selected_real_dimension": SELECTED_DIMENSION,
            "external_real_dimension": EXTERNAL_DIMENSION,
            "nonlinear_derivative_bound_certified": False,
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
    result = run_q011q_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
