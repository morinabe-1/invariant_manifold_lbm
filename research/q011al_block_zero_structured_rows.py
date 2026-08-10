"""Q011al block-zero structured-row eigendisc clearance certificate."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from math import inf
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np

import research.q011ak_degree16_blockwise_obstruction as q011ak
import research.q011k_interval_spectral_split as q011k
from research.q007x_mpfr_backend import fraction_from_mpfr
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ag = q011ak.q011ag
q011b = q011ak.q011b
q011z = q011ak.q011z
q011af = q011ak.q011af

SIZE = 17
BLOCK_ZERO_DIMENSION = 150
DEGREE = 16
OBSTRUCTION_AGGREGATE_INDEX = 99
PRIMARY_PRECISION_BITS = 256
REPLAY_PRECISION_BITS = 384
EXPECTED_SELECTED_INDICES = tuple(range(144, 150))
EXPECTED_SELECTED_COMPONENTS = (
    (144, 146),
    (145, 147),
    (148, 149),
)
EXPECTED_COMPONENT_COUNT = 73
EXPECTED_MIXED_COMPONENT_COUNT = 0
EXPECTED_REFINED_IDENTIFIER_COUNT = 6
EXPECTED_UNCHANGED_IDENTIFIER_COUNT = 198

EXPECTED_BASIS_STREAM_COUNT = 45_000
EXPECTED_FAMILY_STREAM_COUNT = 22_500
EXPECTED_PRIMARY_BASIS_DIGEST = (
    "b8001ad3de3b7b0ef129559e97be9e175c2196547e781d9c3c18e111e55afac4"
)
EXPECTED_REPLAY_BASIS_DIGEST = (
    "7813ce8790beb47b159116b472c809af4429e5688bc7bd6ce8914488082fea02"
)
EXPECTED_FAMILY_DIGEST = (
    "8271e94081187efb1b864e43cd2425255217e3ac77238804b839bb44dd26b491"
)
EXPECTED_PRIMARY_ROW_DIGEST = (
    "f298ebda4edf3f47226c6a3dc5c5c37d7e8e8da82f92c91e44af607e495db1f6"
)
EXPECTED_REPLAY_ROW_DIGEST = (
    "1eb0794a1063c488cd86eea08a6a8a05711c3cd11a82f063b384e242bde93fb9"
)
EXPECTED_SELECTED_ROW_DIGEST = (
    "247b63924428434d2f73ec7d8a74955126845e29678082e95f9f7a77b3e2bfed"
)
EXPECTED_NEUMANN_CORRECTION_HEX = "0x1.0a55a6c03e205p-71"
EXPECTED_MAXIMUM_ROW_RADIUS_INDEX = 34
EXPECTED_MAXIMUM_ROW_RADIUS_HEX = "0x1.331a87c57c090p-31"
EXPECTED_COMMON_BLOCK_ZERO_RADIUS_HEX = "0x1.5cbff506e79d2p-26"
EXPECTED_SELECTED_RADIUS_HEX = (
    "0x1.ce2c730243e12p-35",
    "0x1.d3b4549712506p-35",
    "0x1.14c4118741b29p-34",
    "0x1.087daaa7f30b9p-34",
    "0x1.12db20142d612p-36",
    "0x1.384c1f0aea1b4p-35",
)
EXPECTED_COMPONENT_DIGEST = (
    "afd18241199f27fd43eaae643ed4c64b3d76e9ffad880a502fc9cf84354a4d5f"
)
EXPECTED_SELECTED_EXTERNAL_GAP_PAIR = (149, 143)
EXPECTED_SELECTED_EXTERNAL_GAP_HEX = "0x1.900710b9c775fp-6"
EXPECTED_SELECTED_EXTERNAL_GAP_DIGEST = (
    "ac6dd0cedd3230e10a9e0b054eeb354f3d7c239ca2dae974927a0dbd5c651bcc"
)

EXPECTED_HYBRID_RECORD_DIGEST = (
    "a7d56141743bc62f3684d54975ad7d74f6274b3a3da7078d6ce1ce7a31f8092e"
)
EXPECTED_CLASS_MEMBERSHIP_DIGEST = q011ak.EXPECTED_CLASS_MEMBERSHIP_DIGEST
EXPECTED_CLASS_COUNTS = q011ak.EXPECTED_CLASS_COUNTS
EXPECTED_RELATIONS_WEIGHTED = {
    "overlap": 0,
    "product_below_target": 3_465_728,
    "target_below_product": 0,
}
EXPECTED_RELATIONS_DISTINCT = {
    "overlap": 0,
    "product_below_target": 141_120,
    "target_below_product": 0,
}
EXPECTED_MINIMUM_GAP_HEX = "0x1.2de9e9dffffffp-26"
EXPECTED_EXACT_GAP_HEX = "0x1.2de9f1c1d911ep-26"
EXPECTED_MINIMUM_CLASS_COUNTS = (
    (5, 0, 0, 0),
    (0, 6),
    (0, 0, 4),
    (0, 0, 0, 0, 0, 1),
)
EXPECTED_MINIMUM_SOURCES = (
    "block=16;center=142",
    "block=16;center=142",
    "block=16;center=142",
    "block=16;center=142",
    "block=16;center=142",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=1;center=152",
    "block=1;center=152",
    "block=1;center=152",
    "block=1;center=152",
    "block=1;center=149",
)
EXPECTED_MINIMUM_WITNESS_DIGEST = (
    "6349dc3528e2081b202100712fae40b43fd36792c1867818d2f0cd9ddc0a1096"
)
EXPECTED_CLEARANCE_RECORD_DIGEST = (
    "93d6bb29d30ac44364e021f84b3f8b82ce98c68a36106d9c55dc59f915a86ac6"
)

Q011AK_ARTIFACT_SHA256 = "21d99ca113c5c71b573134d075dc0f01bdc03f0eeea4157dd1a62b1689e7ae59"
Q011AK_RUNNER_SHA256 = "140a4631da777450fbbe5eb3462579c9d2f5b64f3970eeda26511502ea1302f4"
Q011AK_DIGEST_NAMES = (
    "input_digest_sha256",
    "radius_digest_sha256",
    "interval_digest_sha256",
    "obstruction_digest_sha256",
    "result_digest_sha256",
)
Q011AK_DIGESTS = (
    "710bcb6b724112bcf8f7c6cc166009accb176d325c5f6b2b911621d6a4b0ff42",
    "2c6fc37c40262ba5b76121ca1e3655e1ecd760b88ad27063f932bda532ff62ab",
    "25174294bfe13f1de5124793594bb14702617337d41f69e8ff9b43afd3c12386",
    "984f9cd6c4d2db107385e500f64f89e242f2764a826d44f78bb56cbd283e3ec4",
    "e95e11a93a688170e0538d16d9956e487dbd5a1e7a9262b823cb60d0e1b0166a",
)

ACCEPTED_CLASSIFICATION = (
    "the registered degree-16 obstruction is cleared by rigorously contained "
    "block-zero structured-row eigendiscs"
)
INCONCLUSIVE_CLASSIFICATION = (
    "the registered block-zero structured-row clearance audit is inconclusive"
)


class _FramedRecordDigest:
    """Hash an ordered exact record stream without retaining the payload."""

    def __init__(self, domain: str) -> None:
        self._digest = sha256()
        encoded_domain = domain.encode("utf-8")
        self._digest.update(len(encoded_domain).to_bytes(8, "big"))
        self._digest.update(encoded_domain)
        self.count = 0

    def update(self, record: dict[str, Any]) -> None:
        encoded = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        self._digest.update(len(encoded).to_bytes(8, "big"))
        self._digest.update(encoded)
        self.count += 1

    def hexdigest(self) -> str:
        return self._digest.hexdigest()


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011ak._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ak_degree16_blockwise_obstruction.json"
    runner_path = Path(q011ak.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AK_DIGEST_NAMES)
    checks = {
        "q011ak_fifteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 78
            and all(prior["checks"].values())
        ),
        "q011ak_artifact_sha256_matches": (
            _file_sha256(artifact_path) == Q011AK_ARTIFACT_SHA256
        ),
        "q011ak_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AK_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AK_RUNNER_SHA256
        ),
        "q011ak_digests_match": digests == Q011AK_DIGESTS,
        "q011ak_registered_dual_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["scientific_classification"] == q011ak.COMBINED_CLASSIFICATION
        ),
        "q011ak_scope_and_prior_rejection_are_preserved": bool(
            cycle["theorem_consequence"][
                "degree_sixteen_blockwise_radius_certificate_is_rejected_at_the_registered_obstruction"
            ]
            and not cycle["theorem_consequence"][
                "degree_sixteen_external_nonresonance_is_certified"
            ]
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(16, 91))
        ),
        "q011ak_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ak_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ak_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "eighty_three_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 83
        ),
    }
    artifacts["q011ak"] = artifact
    audit = {
        "prior_q011ak_sealed_input_audit": prior,
        "q011ak": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AK_DIGEST_NAMES),
            "digests": list(digests),
            "scientific_classification": cycle["scientific_classification"],
        },
        "direct_digest_count": prior["direct_digest_count"] + len(digests),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _block_zero_family_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    np.ndarray,
    np.ndarray,
    list[list[Fraction]],
    dict[int, list[tuple[Fraction, Fraction]]],
    dict[int, tuple[int, ...]],
    dict[int, dict[str, Fraction]],
]:
    k_sealed, q011j_artifact, _ = q011k._sealed_input_audit()
    _coordinate, lifted, lift_matrix, state_box, _, root = q011k._root_enclosure_audit(
        q011j_artifact
    )
    stored_root = artifacts["q011k"]["cycle"][
        "contraction_derived_root_enclosure_audit"
    ]
    point_state = [RationalInterval.point(value) for value in lifted]
    family_sparse, family_pivot, _ = q011k.q011j._reduced_derivative_factors(
        state_box
    )
    point_sparse, point_pivot, _ = q011k.q011j._reduced_derivative_factors(
        point_state
    )
    family_zero = q011k.q011j._combine_reduced_factors(
        family_sparse, family_pivot, lift_matrix
    )
    point_zero = q011k.q011j._point_matrix(
        q011k.q011j._combine_reduced_factors(
            point_sparse, point_pivot, lift_matrix
        )
    )
    proposal = np.asarray(point_zero, dtype=np.float64) + np.eye(
        BLOCK_ZERO_DIMENSION, dtype=np.float64
    )
    values, vectors, inverse, eigendecomposition = q011k._canonical_eigendecomposition(
        proposal.astype(np.complex128)
    )
    proof_record = artifacts["q011k"]["cycle"]["dual_precision_bauer_fike_audit"][
        "representative_block_records"
    ][0]
    block_record = artifacts["q011k"]["cycle"]["exact_interval_block_family_audit"][
        "block_records"
    ][0]
    centers, selected, _, metrics, spectral = q011z.q011l._spectral_data(
        artifacts["q011k"]
    )
    family_digest = _FramedRecordDigest(
        "Q011al/block-zero-entrywise-family/v1"
    )
    differences: list[list[Fraction]] = []
    for row_index, row in enumerate(family_zero):
        output_row = []
        for column_index, interval in enumerate(row):
            proposal_value = Fraction.from_float(
                float(proposal[row_index, column_index].real)
            )
            lower = (
                interval.lower
                + int(row_index == column_index)
                - proposal_value
            )
            upper = (
                interval.upper
                + int(row_index == column_index)
                - proposal_value
            )
            difference = max(abs(lower), abs(upper))
            output_row.append(difference)
            family_digest.update(
                {
                    "row": row_index,
                    "column": column_index,
                    "absolute_difference_upper": q011z._exact_fraction_record(
                        difference
                    ),
                }
            )
        differences.append(output_row)
    exact_values = [
        (
            Fraction.from_float(float(value.real)),
            Fraction.from_float(float(value.imag)),
        )
        for value in values
    ]
    checks = {
        "q011k_nested_inputs_and_root_reproduce": bool(
            k_sealed["passed"]
            and root == stored_root
            and q011b._canonical_json_sha256(root)
            == q011b._canonical_json_sha256(stored_root)
        ),
        "block_zero_proposal_reproduces_q011k": bool(
            proposal.shape == (BLOCK_ZERO_DIMENSION, BLOCK_ZERO_DIMENSION)
            and q011b._array_sha256(proposal.astype(np.complex128))
            == block_record["proposal_sha256"]
        ),
        "canonical_eigendecomposition_reproduces_q011k": bool(
            eigendecomposition["passed"]
            and eigendecomposition == proof_record["eigendecomposition"]
        ),
        "exact_center_ordering_reproduces": exact_values == centers[0],
        "selected_indices_reproduce": tuple(selected[0])
        == EXPECTED_SELECTED_INDICES,
        "entrywise_family_stream_is_complete_and_registered": bool(
            family_digest.count == EXPECTED_FAMILY_STREAM_COUNT
            and family_digest.hexdigest() == EXPECTED_FAMILY_DIGEST
        ),
        "q011l_exact_spectral_reconstruction_reproduces": spectral["passed"],
    }
    audit = {
        "block_index": 0,
        "dimension": BLOCK_ZERO_DIMENSION,
        "proposal_sha256": q011b._array_sha256(proposal.astype(np.complex128)),
        "eigenvalue_sha256": eigendecomposition["eigenvalues_sha256"],
        "eigenvector_sha256": eigendecomposition["eigenvectors_sha256"],
        "inverse_candidate_sha256": eigendecomposition["inverse_candidate_sha256"],
        "selected_center_indices": list(selected[0]),
        "entrywise_family_record_count": family_digest.count,
        "entrywise_family_digest_sha256": family_digest.hexdigest(),
        "root_digest_sha256": q011b._canonical_json_sha256(root),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, vectors, inverse, differences, centers, selected, metrics


def _mpfr_upper(value: Fraction) -> gmpy2.mpfr:
    return gmpy2.mpfr(q011k.q011j._mpq(value))


def _forbidden_flags_clear(flags: dict[str, bool]) -> bool:
    return all(
        not flags[name]
        for name in ("underflow", "overflow", "invalid", "division_by_zero", "erange")
    )


def _structured_row_protocol(
    vectors: np.ndarray,
    inverse: np.ndarray,
    differences: list[list[Fraction]],
    selected_indices: tuple[int, ...],
    point_residual: Fraction,
    inverse_defect: Fraction,
    common_radius: Fraction,
    precision_bits: int,
) -> tuple[dict[str, Any], list[Fraction]]:
    caller_signature = q011k.q011j._context_signature(gmpy2.get_context())
    context = q011k.q011j._proof_context(precision_bits, gmpy2.RoundUp)
    basis_digest = _FramedRecordDigest(
        f"Q011al/block-zero-eigenbasis-absolute-mpfr{precision_bits}/v1"
    )
    conversions_exact = True
    family_conversion_contains = True
    with context:
        vector_row_sums = []
        for row_index in range(BLOCK_ZERO_DIMENSION):
            total = gmpy2.mpfr(0)
            for column_index in range(BLOCK_ZERO_DIMENSION):
                value = vectors[row_index, column_index]
                real = gmpy2.mpfr(float(value.real))
                imaginary = gmpy2.mpfr(float(value.imag))
                conversions_exact = bool(
                    conversions_exact
                    and fraction_from_mpfr(real)
                    == Fraction.from_float(float(value.real))
                    and fraction_from_mpfr(imaginary)
                    == Fraction.from_float(float(value.imag))
                )
                absolute = gmpy2.sqrt(real * real + imaginary * imaginary)
                total += absolute
                basis_digest.update(
                    {
                        "matrix": "V",
                        "row": row_index,
                        "column": column_index,
                        "absolute_upper": q011z._exact_fraction_record(
                            fraction_from_mpfr(absolute)
                        ),
                    }
                )
            vector_row_sums.append(total)

        inverse_absolutes = []
        inverse_row_sums = []
        for row_index in range(BLOCK_ZERO_DIMENSION):
            row = []
            total = gmpy2.mpfr(0)
            for column_index in range(BLOCK_ZERO_DIMENSION):
                value = inverse[row_index, column_index]
                real = gmpy2.mpfr(float(value.real))
                imaginary = gmpy2.mpfr(float(value.imag))
                conversions_exact = bool(
                    conversions_exact
                    and fraction_from_mpfr(real)
                    == Fraction.from_float(float(value.real))
                    and fraction_from_mpfr(imaginary)
                    == Fraction.from_float(float(value.imag))
                )
                absolute = gmpy2.sqrt(real * real + imaginary * imaginary)
                row.append(absolute)
                total += absolute
                basis_digest.update(
                    {
                        "matrix": "W",
                        "row": row_index,
                        "column": column_index,
                        "absolute_upper": q011z._exact_fraction_record(
                            fraction_from_mpfr(absolute)
                        ),
                    }
                )
            inverse_absolutes.append(row)
            inverse_row_sums.append(total)

        difference_uppers = []
        for row in differences:
            output_row = []
            for value in row:
                upper = _mpfr_upper(value)
                family_conversion_contains = bool(
                    family_conversion_contains
                    and fraction_from_mpfr(upper) >= value
                )
                output_row.append(upper)
            difference_uppers.append(output_row)

        weighted_family_rows = []
        for row_index in range(BLOCK_ZERO_DIMENSION):
            total = gmpy2.mpfr(0)
            for column_index in range(BLOCK_ZERO_DIMENSION):
                total += (
                    difference_uppers[row_index][column_index]
                    * vector_row_sums[column_index]
                )
            weighted_family_rows.append(total)

        structured_family_rows = []
        for row_index in range(BLOCK_ZERO_DIMENSION):
            total = gmpy2.mpfr(0)
            for inner_index in range(BLOCK_ZERO_DIMENSION):
                total += (
                    inverse_absolutes[row_index][inner_index]
                    * weighted_family_rows[inner_index]
                )
            structured_family_rows.append(total)

        point_residual_upper = _mpfr_upper(point_residual)
        point_rows = [
            row_sum * point_residual_upper for row_sum in inverse_row_sums
        ]
        pre_neumann_rows = [
            point + structured
            for point, structured in zip(
                point_rows, structured_family_rows, strict=True
            )
        ]
        neumann_factor = _mpfr_upper(inverse_defect / (1 - inverse_defect))
        correction = neumann_factor * max(pre_neumann_rows)
        radius_mpfr = [value + correction for value in pre_neumann_rows]

    flags = q011k.q011j._context_flags(context)
    caller_unchanged = (
        q011k.q011j._context_signature(gmpy2.get_context()) == caller_signature
    )
    inverse_row_fractions = [
        fraction_from_mpfr(value) for value in inverse_row_sums
    ]
    point_fractions = [fraction_from_mpfr(value) for value in point_rows]
    structured_fractions = [
        fraction_from_mpfr(value) for value in structured_family_rows
    ]
    pre_neumann_fractions = [
        fraction_from_mpfr(value) for value in pre_neumann_rows
    ]
    correction_fraction = fraction_from_mpfr(correction)
    radii = [fraction_from_mpfr(value) for value in radius_mpfr]
    selected_set = frozenset(selected_indices)
    row_records = []
    for center_index in range(BLOCK_ZERO_DIMENSION):
        row_records.append(
            {
                "center_index": center_index,
                "selected": center_index in selected_set,
                "inverse_row_sum_upper": q011z._exact_fraction_record(
                    inverse_row_fractions[center_index]
                ),
                "point_residual_row_upper": q011z._exact_fraction_record(
                    point_fractions[center_index]
                ),
                "structured_family_row_upper": q011z._exact_fraction_record(
                    structured_fractions[center_index]
                ),
                "pre_neumann_row_upper": q011z._exact_fraction_record(
                    pre_neumann_fractions[center_index]
                ),
                "neumann_correction_upper": q011z._exact_fraction_record(
                    correction_fraction
                ),
                "row_eigendisc_radius_upper": q011z._exact_fraction_record(
                    radii[center_index]
                ),
                "row_eigendisc_radius_binary64_hex": float(
                    radii[center_index]
                ).hex(),
                "contained_in_q011y_block_radius": radii[center_index]
                <= common_radius,
            }
        )
    row_digest = q011b._canonical_json_sha256(row_records)
    maximum_index = max(range(BLOCK_ZERO_DIMENSION), key=radii.__getitem__)
    checks = {
        "all_binary64_eigenbasis_inputs_convert_exactly": conversions_exact,
        "all_exact_family_entries_are_rounded_up": family_conversion_contains,
        "basis_stream_is_complete": basis_digest.count
        == EXPECTED_BASIS_STREAM_COUNT,
        "all_row_bounds_are_positive_and_common_radius_contained": all(
            0 < radius <= common_radius for radius in radii
        ),
        "inverse_defect_neumann_factor_is_valid": 0 < inverse_defect < 1,
        "no_forbidden_mpfr_flags": _forbidden_flags_clear(flags),
        "caller_context_is_unchanged": caller_unchanged,
        "row_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(row_records)
            and _strict_json_serializable(row_records)
            and json.dumps(row_records, allow_nan=False)
        ),
    }
    audit = {
        "precision_bits": precision_bits,
        "rounding_mode": "RoundUp",
        "basis_absolute_stream_count": basis_digest.count,
        "basis_absolute_stream_digest_sha256": basis_digest.hexdigest(),
        "row_records": row_records,
        "row_record_digest_sha256": row_digest,
        "neumann_correction_upper": q011z._exact_fraction_record(
            correction_fraction
        ),
        "neumann_correction_binary64_hex": float(correction_fraction).hex(),
        "maximum_row_radius_index": maximum_index,
        "maximum_row_radius_upper": q011z._exact_fraction_record(
            radii[maximum_index]
        ),
        "maximum_row_radius_binary64_hex": float(radii[maximum_index]).hex(),
        "mpfr_flags": flags,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, radii


def _dual_precision_row_audit(
    family: dict[str, Any],
    vectors: np.ndarray,
    inverse: np.ndarray,
    differences: list[list[Fraction]],
    selected: dict[int, tuple[int, ...]],
    metrics: dict[int, dict[str, Fraction]],
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[Fraction]]:
    primary_proof = artifacts["q011k"]["cycle"]["dual_precision_bauer_fike_audit"][
        "representative_block_records"
    ][0]["primary_precision_proof"]
    point_residual = q011z._fraction(
        primary_proof["point_eigendecomposition_residual_infinity_upper"]
    )
    inverse_defect = q011z._fraction(
        primary_proof["inverse_defect_infinity_norm_upper"]
    )
    common_radius = metrics[0]["theta"]
    primary, primary_radii = _structured_row_protocol(
        vectors,
        inverse,
        differences,
        selected[0],
        point_residual,
        inverse_defect,
        common_radius,
        PRIMARY_PRECISION_BITS,
    )
    replay, replay_radii = _structured_row_protocol(
        vectors,
        inverse,
        differences,
        selected[0],
        point_residual,
        inverse_defect,
        common_radius,
        REPLAY_PRECISION_BITS,
    )
    selected_rows = [
        record for record in primary["row_records"] if record["selected"]
    ]
    selected_radius_hex = tuple(
        record["row_eigendisc_radius_binary64_hex"] for record in selected_rows
    )
    checks = {
        "block_zero_family_input_audit_passes": family["passed"],
        "primary_and_replay_protocols_pass": bool(
            primary["passed"] and replay["passed"]
        ),
        "registered_basis_stream_digests_reproduce": bool(
            primary["basis_absolute_stream_digest_sha256"]
            == EXPECTED_PRIMARY_BASIS_DIGEST
            and replay["basis_absolute_stream_digest_sha256"]
            == EXPECTED_REPLAY_BASIS_DIGEST
        ),
        "registered_row_record_digests_reproduce": bool(
            primary["row_record_digest_sha256"] == EXPECTED_PRIMARY_ROW_DIGEST
            and replay["row_record_digest_sha256"] == EXPECTED_REPLAY_ROW_DIGEST
        ),
        "all_replay_radii_are_strictly_contained": all(
            replay_radius < primary_radius
            for primary_radius, replay_radius in zip(
                primary_radii, replay_radii, strict=True
            )
        ),
        "registered_primary_extrema_reproduce": bool(
            primary["neumann_correction_binary64_hex"]
            == EXPECTED_NEUMANN_CORRECTION_HEX
            and primary["maximum_row_radius_index"]
            == EXPECTED_MAXIMUM_ROW_RADIUS_INDEX
            and primary["maximum_row_radius_binary64_hex"]
            == EXPECTED_MAXIMUM_ROW_RADIUS_HEX
            and float(common_radius).hex()
            == EXPECTED_COMMON_BLOCK_ZERO_RADIUS_HEX
        ),
        "registered_selected_rows_reproduce": bool(
            tuple(record["center_index"] for record in selected_rows)
            == EXPECTED_SELECTED_INDICES
            and selected_radius_hex == EXPECTED_SELECTED_RADIUS_HEX
            and q011b._canonical_json_sha256(selected_rows)
            == EXPECTED_SELECTED_ROW_DIGEST
        ),
        "structured_row_bound_algebra_is_applicable": bool(
            0 < inverse_defect < 1
            and point_residual > 0
            and all(value >= 0 for row in differences for value in row)
        ),
    }
    audit = {
        "matrix_identity": (
            "F=(I+E)^-1 W {R0+(A-A0)V}, with E=WV-I and R0=A0V-VD"
        ),
        "row_radius_formula": (
            "r_i=b_i+epsilon/(1-epsilon)*max_l b_l, "
            "b_i=||row_i(W)||_1*p+sum_p |W_ip| sum_q Delta_pq sum_j |V_qj|"
        ),
        "gershgorin_consequence": "spectrum(A0-family) subset union_i D(D_ii,r_i)",
        "point_residual_upper": q011z._exact_fraction_record(point_residual),
        "inverse_defect_upper": q011z._exact_fraction_record(inverse_defect),
        "q011y_common_block_zero_radius": q011z._exact_fraction_record(
            common_radius
        ),
        "primary_protocol": primary,
        "replay_protocol": replay,
        "selected_primary_row_records": selected_rows,
        "selected_primary_row_digest_sha256": q011b._canonical_json_sha256(
            selected_rows
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, primary_radii


def _gershgorin_component_audit(
    centers: list[tuple[Fraction, Fraction]],
    selected_indices: tuple[int, ...],
    radii: list[Fraction],
) -> dict[str, Any]:
    parent = list(range(BLOCK_ZERO_DIMENSION))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left in range(BLOCK_ZERO_DIMENSION):
        for right in range(left):
            delta_real = centers[left][0] - centers[right][0]
            delta_imaginary = centers[left][1] - centers[right][1]
            if (
                delta_real * delta_real + delta_imaginary * delta_imaginary
                <= (radii[left] + radii[right]) ** 2
            ):
                union(left, right)
    groups: dict[int, list[int]] = {}
    for center_index in range(BLOCK_ZERO_DIMENSION):
        groups.setdefault(find(center_index), []).append(center_index)
    selected_set = frozenset(selected_indices)
    component_records = []
    for component_index, indices in enumerate(
        sorted(groups.values(), key=lambda values: values[0])
    ):
        selected_members = [index for index in indices if index in selected_set]
        external_members = [index for index in indices if index not in selected_set]
        membership = (
            "selected"
            if selected_members and not external_members
            else "external"
            if external_members and not selected_members
            else "mixed"
        )
        component_records.append(
            {
                "component_index": component_index,
                "center_indices": indices,
                "disc_count": len(indices),
                "selected_center_indices": selected_members,
                "external_center_indices": external_members,
                "membership": membership,
            }
        )
    component_digest = q011b._canonical_json_sha256(component_records)
    selected_components = [
        record for record in component_records if record["membership"] == "selected"
    ]
    mixed_components = [
        record for record in component_records if record["membership"] == "mixed"
    ]
    minimum_gap: Fraction | None = None
    minimum_pair: tuple[int, int] | None = None
    external_indices = set(range(BLOCK_ZERO_DIMENSION)) - selected_set
    for selected_index in selected_indices:
        for external_index in external_indices:
            delta_real = abs(
                centers[selected_index][0] - centers[external_index][0]
            )
            delta_imaginary = abs(
                centers[selected_index][1] - centers[external_index][1]
            )
            gap = (
                max(delta_real, delta_imaginary)
                - radii[selected_index]
                - radii[external_index]
            )
            if minimum_gap is None or gap < minimum_gap:
                minimum_gap = gap
                minimum_pair = (selected_index, external_index)
    if minimum_gap is None or minimum_pair is None:
        raise RuntimeError("Q011al found no selected/external disc pair")
    gap_record = {
        "selected_center_index": minimum_pair[0],
        "external_center_index": minimum_pair[1],
        "maximum_coordinate_distance_minus_radii": q011z._exact_fraction_record(
            minimum_gap
        ),
        "gap_binary64_hex": float(minimum_gap).hex(),
    }
    gap_digest = q011b._canonical_json_sha256(gap_record)
    selected_component_memberships = tuple(
        tuple(record["center_indices"]) for record in selected_components
    )
    checks = {
        "registered_component_count_and_digest_reproduce": bool(
            len(component_records) == EXPECTED_COMPONENT_COUNT
            and component_digest == EXPECTED_COMPONENT_DIGEST
        ),
        "no_component_mixes_selected_and_external_discs": len(mixed_components)
        == EXPECTED_MIXED_COMPONENT_COUNT,
        "registered_three_selected_components_reproduce": (
            selected_component_memberships == EXPECTED_SELECTED_COMPONENTS
        ),
        "selected_components_have_exactly_six_discs": sum(
            record["disc_count"] for record in selected_components
        )
        == len(EXPECTED_SELECTED_INDICES),
        "registered_selected_external_gap_reproduces": bool(
            minimum_pair == EXPECTED_SELECTED_EXTERNAL_GAP_PAIR
            and minimum_gap > 0
            and float(minimum_gap).hex() == EXPECTED_SELECTED_EXTERNAL_GAP_HEX
            and gap_digest == EXPECTED_SELECTED_EXTERNAL_GAP_DIGEST
        ),
        "gershgorin_component_counting_theorem_is_applicable": bool(
            not mixed_components and minimum_gap > 0
        ),
    }
    return {
        "disc_intersection_rule": (
            "connect i,j unless exact squared center distance exceeds (r_i+r_j)^2"
        ),
        "component_records": component_records,
        "component_record_digest_sha256": component_digest,
        "selected_component_records": selected_components,
        "mixed_component_count": len(mixed_components),
        "minimum_selected_external_gap": gap_record,
        "minimum_selected_external_gap_digest_sha256": gap_digest,
        "eigenvalue_counting_consequence": (
            "each isolated k-disc Gershgorin component contains exactly k eigenvalues; "
            "the three selected components therefore contain all six selected eigenvalues"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _hybrid_envelope_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    selected_indices: tuple[int, ...],
    primary_radii: list[Fraction],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[tuple[tuple[str, ...], ...], ...],
]:
    blockwise, base_lookup, theta = q011ak._blockwise_envelope_audit(
        artifacts, selected_groups
    )
    selected_set = frozenset(selected_indices)
    lookup: dict[str, q011z._UniformDisc] = {}
    records = []
    refined_identifiers = []
    unchanged_identifiers = []
    for identifier, base in base_lookup.items():
        block, center_index = q011z._identifier_indices(identifier)
        refined = block == 0 and center_index in selected_set
        radius = primary_radii[center_index] if refined else theta[block]
        radius_kind = (
            "block_zero_selected_structured_row"
            if refined
            else "q011y_blockwise"
        )
        modulus = RationalInterval(
            max(Fraction(0), base.center_modulus.lower - radius),
            base.center_modulus.upper + radius,
        )
        contained = bool(
            modulus.lower >= base.modulus.lower
            and modulus.upper <= base.modulus.upper
        )
        lookup[identifier] = q011z._UniformDisc(
            identifier=identifier,
            block_index=block,
            center_index=center_index,
            center_modulus=base.center_modulus,
            modulus=modulus,
        )
        records.append(
            {
                "identifier": identifier,
                "block_index": block,
                "center_index": center_index,
                "radius_kind": radius_kind,
                "radius_upper": q011z._exact_fraction_record(radius),
                "hybrid_modulus_lower": q011z._exact_fraction_record(modulus.lower),
                "hybrid_modulus_upper": q011z._exact_fraction_record(modulus.upper),
                "contained_in_q011ak_blockwise_interval": contained,
            }
        )
        if refined:
            refined_identifiers.append(identifier)
        else:
            unchanged_identifiers.append(identifier)
    record_digest = q011b._canonical_json_sha256(records)
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    class_radius_consistency = True
    for group_classes in classes:
        for identifiers in group_classes:
            radii = {
                lookup[identifier].modulus.upper
                - lookup[identifier].center_modulus.upper
                for identifier in identifiers
            }
            class_radius_consistency = class_radius_consistency and len(radii) == 1
    checks = {
        "q011ak_blockwise_envelope_reconstructs": blockwise["passed"],
        "exactly_six_selected_block_zero_identifiers_are_refined": bool(
            len(refined_identifiers) == EXPECTED_REFINED_IDENTIFIER_COUNT
            and refined_identifiers
            == [f"block=0;center={index}" for index in EXPECTED_SELECTED_INDICES]
        ),
        "remaining_one_hundred_ninety_eight_identifiers_are_unchanged": bool(
            len(unchanged_identifiers) == EXPECTED_UNCHANGED_IDENTIFIER_COUNT
            and all(
                lookup[identifier].modulus == base_lookup[identifier].modulus
                for identifier in unchanged_identifiers
            )
        ),
        "all_hybrid_intervals_are_contained_in_q011ak_intervals": all(
            record["contained_in_q011ak_blockwise_interval"] for record in records
        ),
        "registered_hybrid_record_digest_reproduces": bool(
            len(records) == q011ak.q011aj.EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and record_digest == EXPECTED_HYBRID_RECORD_DIGEST
        ),
        "modulus_classes_and_membership_digest_are_preserved": bool(
            tuple(len(group) for group in classes) == EXPECTED_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_MEMBERSHIP_DIGEST
            and class_radius_consistency
        ),
        "hybrid_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    audit = {
        "identifier_record_count": len(records),
        "refined_identifier_count": len(refined_identifiers),
        "unchanged_identifier_count": len(unchanged_identifiers),
        "refined_identifiers": refined_identifiers,
        "hybrid_disc_records": records,
        "hybrid_record_digest_sha256": record_digest,
        "selected_modulus_class_counts": [len(group) for group in classes],
        "class_membership_digest_sha256": class_digest,
        "containment_chain": (
            "selected block-zero row discs subset Q011y blockwise discs subset "
            "Q011aj uniform discs subset Q011k discs"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, classes


def _clearance_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    target_group: tuple[str, ...],
) -> dict[str, Any]:
    group_pools = tuple(
        q011ak._blockwise_group_signature(classes, lookup, group_index, count)
        for group_index, count in enumerate(q011ak.EXPECTED_OBSTRUCTION_COUNTS)
    )
    left = q011ag._pair_signatures(group_pools[0], group_pools[1])
    right = q011ag._pair_signatures(group_pools[2], group_pools[3])
    left_wave = np.stack([record.wave for record in left])
    right_wave = np.stack([record.wave for record in right])
    product_lower, product_upper = q011ag._product_bound_matrices(left, right)
    compatible = np.zeros(product_lower.shape, dtype=bool)
    compatible_monomial_count = 0
    weighted_comparison_count = 0
    distinct_comparison_count = 0
    relations: Counter[str] = Counter()
    minimum: tuple[Any, ...] | None = None
    maximum_wave_coefficient = 0
    maximum_crude_bound = 0
    all_arrays_finite = bool(
        np.isfinite(product_lower).all() and np.isfinite(product_upper).all()
    )
    all_bounds_ordered = bool(
        np.all(product_lower >= 0) and np.all(product_lower <= product_upper)
    )
    for output_block, target_identifiers in q011ag._target_groups_by_block(
        target_group
    ).items():
        wave_matrix, crude_bound = q011ag._wave_matrix(
            left_wave, right_wave, output_block
        )
        active = wave_matrix > 0
        compatible |= active
        compatible_monomial_count += int(wave_matrix.sum())
        weighted_comparison_count += int(wave_matrix.sum()) * len(target_identifiers)
        distinct_comparison_count += int(active.sum()) * len(target_identifiers)
        maximum_wave_coefficient = max(
            maximum_wave_coefficient, int(wave_matrix.max(initial=0))
        )
        maximum_crude_bound = max(maximum_crude_bound, crude_bound)
        for target_identifier in target_identifiers:
            target = lookup[target_identifier]
            product_below_gap = q011ag._down_subtract(
                q011ag._fraction_lower(target.modulus.lower), product_upper
            )
            target_below_gap = q011ag._down_subtract(
                product_lower, q011ag._fraction_upper(target.modulus.upper)
            )
            product_below = active & (product_below_gap > 0)
            target_below = active & (target_below_gap > 0)
            unresolved = active & ~(product_below | target_below)
            for relation, mask, gaps in (
                ("product_below_target", product_below, product_below_gap),
                ("target_below_product", target_below, target_below_gap),
                ("overlap", unresolved, None),
            ):
                relations[f"{relation}_distinct"] += int(mask.sum())
                relations[f"{relation}_weighted"] += int(wave_matrix[mask].sum())
                if relation == "overlap" or not mask.any() or gaps is None:
                    continue
                candidate = np.where(mask, gaps, inf)
                flat_index = int(candidate.argmin())
                left_index, right_index = map(
                    int, np.unravel_index(flat_index, candidate.shape)
                )
                key = (
                    float(gaps[left_index, right_index]),
                    target_identifier,
                    left_index,
                    right_index,
                )
                if minimum is None or key < minimum[0]:
                    minimum = (
                        key,
                        target_identifier,
                        output_block,
                        left_index,
                        right_index,
                        int(wave_matrix[left_index, right_index]),
                        relation,
                        q011ag._signature_counts(
                            left, right, left_index, right_index
                        ),
                    )
    if minimum is None:
        raise RuntimeError("Q011al reconstructed no separated comparison")
    (
        key,
        target_identifier,
        output_block,
        left_index,
        right_index,
        wave_multiplicity,
        relation,
        class_counts,
    ) = minimum
    source_identifiers = q011af._source_witness_for_signature(
        classes, class_counts, output_block
    )
    product, _ = q011ak._exact_blockwise_product_interval(
        classes, lookup, class_counts
    )
    target = lookup[target_identifier].modulus
    exact_gap = (
        target.lower - product.upper
        if relation == "product_below_target"
        else product.lower - target.upper
    )
    witness = {
        "target_identifier": target_identifier,
        "output_block": output_block,
        "left_index": left_index,
        "right_index": right_index,
        "wave_multiplicity": wave_multiplicity,
        "relation": relation,
        "block_zero_multiplicity": q011ak._block_zero_multiplicity(
            classes, class_counts
        ),
        "class_counts": [list(group) for group in class_counts],
        "source_identifiers": list(source_identifiers),
        "outward_gap_hex": key[0].hex(),
        "hybrid_product_interval": {
            "lower": q011z._exact_fraction_record(product.lower),
            "upper": q011z._exact_fraction_record(product.upper),
        },
        "hybrid_target_interval": {
            "lower": q011z._exact_fraction_record(target.lower),
            "upper": q011z._exact_fraction_record(target.upper),
        },
        "exact_gap": q011z._exact_fraction_record(exact_gap),
        "exact_gap_hex": float(exact_gap).hex(),
    }
    witness_digest = q011b._canonical_json_sha256(witness)
    weighted_relations = {
        relation_name: relations[f"{relation_name}_weighted"]
        for relation_name in (
            "overlap",
            "product_below_target",
            "target_below_product",
        )
    }
    distinct_relations = {
        relation_name: relations[f"{relation_name}_distinct"]
        for relation_name in (
            "overlap",
            "product_below_target",
            "target_below_product",
        )
    }
    record = {
        "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
        "selected_type_counts": list(q011ak.EXPECTED_OBSTRUCTION_COUNTS),
        "target_identifiers": list(target_group),
        "modulus_signature_count": len(left) * len(right),
        "weighted_comparison_count": weighted_comparison_count,
        "distinct_comparison_count": distinct_comparison_count,
        "weighted_relation_counts": weighted_relations,
        "distinct_relation_counts": distinct_relations,
        "minimum_outward_witness": witness,
        "minimum_outward_witness_digest_sha256": witness_digest,
    }
    record_digest = q011b._canonical_json_sha256(record)
    checks = {
        "registered_signature_and_fourier_counts_reproduce": bool(
            len(left) * len(right) == q011ak.EXPECTED_MODULUS_SIGNATURE_COUNT
            and int(compatible.sum()) == q011ak.EXPECTED_MODULUS_SIGNATURE_COUNT
            and compatible_monomial_count
            == q011ak.EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and weighted_comparison_count
            == q011ak.EXPECTED_WEIGHTED_COMPARISON_COUNT
            and distinct_comparison_count
            == q011ak.EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "all_registered_comparisons_are_product_below_target": bool(
            weighted_relations == EXPECTED_RELATIONS_WEIGHTED
            and distinct_relations == EXPECTED_RELATIONS_DISTINCT
        ),
        "registered_minimum_witness_reproduces": bool(
            target_identifier == "block=11;center=4"
            and output_block == 11
            and left_index == 385
            and right_index == 0
            and wave_multiplicity == 35
            and relation == "product_below_target"
            and witness["block_zero_multiplicity"] == 0
            and class_counts == EXPECTED_MINIMUM_CLASS_COUNTS
            and tuple(source_identifiers) == EXPECTED_MINIMUM_SOURCES
            and witness["outward_gap_hex"] == EXPECTED_MINIMUM_GAP_HEX
            and witness["exact_gap_hex"] == EXPECTED_EXACT_GAP_HEX
            and exact_gap > 0
            and witness_digest == EXPECTED_MINIMUM_WITNESS_DIGEST
        ),
        "registered_clearance_record_digest_reproduces": (
            record_digest == EXPECTED_CLEARANCE_RECORD_DIGEST
        ),
        "all_outward_arrays_are_finite_nonnegative_and_ordered": bool(
            all_arrays_finite and all_bounds_ordered
        ),
        "fourier_int64_bound_is_safe": maximum_crude_bound
        < np.iinfo(np.int64).max,
    }
    return {
        "clearance_record": record,
        "clearance_record_digest_sha256": record_digest,
        "compatible_modulus_signature_count": int(compatible.sum()),
        "compatible_original_monomial_count": compatible_monomial_count,
        "maximum_wave_coefficient": maximum_wave_coefficient,
        "maximum_crude_int64_dot_product_bound": maximum_crude_bound,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "grid": [SIZE, SIZE],
        "fixed_conservation_leaf": True,
        "degree": DEGREE,
        "obstruction_aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "replay_precision_bits": REPLAY_PRECISION_BITS,
        "selected_block_zero_indices": list(EXPECTED_SELECTED_INDICES),
        "q011ak_artifact_sha256": Q011AK_ARTIFACT_SHA256,
        "q011ak_runner_sha256": Q011AK_RUNNER_SHA256,
        "family_stream_digest_sha256": EXPECTED_FAMILY_DIGEST,
        "primary_row_digest_sha256": EXPECTED_PRIMARY_ROW_DIGEST,
        "replay_row_digest_sha256": EXPECTED_REPLAY_ROW_DIGEST,
        "component_digest_sha256": EXPECTED_COMPONENT_DIGEST,
        "hybrid_record_digest_sha256": EXPECTED_HYBRID_RECORD_DIGEST,
        "clearance_record_digest_sha256": EXPECTED_CLEARANCE_RECORD_DIGEST,
        "accepted_classification": ACCEPTED_CLASSIFICATION,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "failed_hypothesis_order": cycle["failed_hypothesis_order"],
    }


def run_block_zero_structured_row_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    obstruction_input, selected_groups, target_group = (
        q011ak._registered_obstruction_input_audit(artifacts)
    )
    (
        family,
        vectors,
        inverse,
        differences,
        centers,
        selected,
        metrics,
    ) = _block_zero_family_audit(artifacts)
    rows, primary_radii = _dual_precision_row_audit(
        family,
        vectors,
        inverse,
        differences,
        selected,
        metrics,
        artifacts,
    )
    components = _gershgorin_component_audit(
        centers[0], selected[0], primary_radii
    )
    hybrid, lookup, classes = _hybrid_envelope_audit(
        artifacts, selected_groups, selected[0], primary_radii
    )
    clearance = _clearance_audit(classes, lookup, target_group)

    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    family_sections = {"block_zero_exact_family_audit": family}
    row_sections = {
        "block_zero_structured_row_audit": rows,
        "block_zero_gershgorin_component_audit": components,
    }
    clearance_sections = {
        "registered_obstruction_input_audit": obstruction_input,
        "hybrid_selected_block_zero_envelope_audit": hybrid,
        "registered_obstruction_clearance_audit": clearance,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    family_digest = q011b._canonical_json_sha256(family_sections)
    row_digest = q011b._canonical_json_sha256(row_sections)
    clearance_digest = q011b._canonical_json_sha256(clearance_sections)
    strict_payload = {
        **input_sections,
        **family_sections,
        **row_sections,
        **clearance_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and family_digest == q011b._canonical_json_sha256(family_sections)
        and row_digest == q011b._canonical_json_sha256(row_sections)
        and clearance_digest == q011b._canonical_json_sha256(clearance_sections)
    )
    clearance_record = clearance["clearance_record"]
    exact_gap = q011z._fraction(
        clearance_record["minimum_outward_witness"]["exact_gap"]
    )
    validity_gates = {
        "sixteen_artifacts_eighty_three_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae/af/ag/ah/ai/aj/ak artifacts, "
                "runners, 83 digests, outcomes, boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "block_zero_exact_family_proposal_and_eigenbasis_reproduce": {
            "passed": family["passed"],
            "threshold": (
                "the Q011k block-zero exact family, proposal, eigenbasis, inverse "
                "and selected indices reproduce"
            ),
            "value": family["checks"],
        },
        "dual_precision_streams_flags_and_digests_reproduce": {
            "passed": bool(
                rows["checks"]["primary_and_replay_protocols_pass"]
                and rows["checks"]["registered_basis_stream_digests_reproduce"]
                and family["checks"][
                    "entrywise_family_stream_is_complete_and_registered"
                ]
            ),
            "threshold": (
                "256/384-bit RoundUp, 45000 basis absolutes, 22500 family entries "
                "and no forbidden MPFR flags"
            ),
            "value": rows["checks"],
        },
        "all_row_bounds_replay_containment_and_common_radius_containment_reproduce": {
            "passed": rows["passed"],
            "threshold": (
                "150 registered row bounds, strict replay containment and containment "
                "inside the Q011y common block-zero radius"
            ),
            "value": rows["checks"],
        },
        "gershgorin_components_and_selected_external_gap_reproduce": {
            "passed": components["passed"],
            "threshold": (
                "73 components, no mixed component, three selected components and "
                "a positive selected/external gap"
            ),
            "value": components["checks"],
        },
        "six_identifier_hybrid_envelope_and_classes_reproduce": {
            "passed": bool(hybrid["passed"] and obstruction_input["passed"]),
            "threshold": (
                "six selected block-zero discs refined, 198 unchanged, 204 contained "
                "records and preserved 4/2/3/6 classes"
            ),
            "value": hybrid["checks"],
        },
        "registered_obstruction_all_separation_and_witness_reproduce": {
            "passed": clearance["passed"],
            "threshold": (
                "all 141120 distinct and 3465728 weighted comparisons separate "
                "with the registered positive witness"
            ),
            "value": clearance["checks"],
        },
        "strict_serialization_section_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "strict finite JSON, four section digests and runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "structured_row_formula_bounds_every_actual_transformed_row": {
            "passed": bool(
                validity_passed
                and rows["checks"]["structured_row_bound_algebra_is_applicable"]
                and rows["primary_protocol"]["passed"]
            ),
            "threshold": "the registered row formula upper-bounds every row sum of F",
            "value": rows["row_radius_formula"],
        },
        "selected_gershgorin_components_contain_exactly_six_eigenvalues": {
            "passed": bool(validity_passed and components["passed"]),
            "threshold": (
                "three isolated selected components contain exactly six block-zero eigenvalues"
            ),
            "value": components["selected_component_records"],
        },
        "six_refined_sources_are_contained_and_all_other_records_are_unchanged": {
            "passed": bool(validity_passed and hybrid["passed"]),
            "threshold": "six refined source intervals are contained and 198 stay exact",
            "value": {
                "refined": hybrid["refined_identifier_count"],
                "unchanged": hybrid["unchanged_identifier_count"],
            },
        },
        "all_registered_comparisons_are_classified_exactly_once": {
            "passed": bool(
                validity_passed
                and sum(clearance_record["distinct_relation_counts"].values())
                == q011ak.EXPECTED_DISTINCT_COMPARISON_COUNT
                and sum(clearance_record["weighted_relation_counts"].values())
                == q011ak.EXPECTED_WEIGHTED_COMPARISON_COUNT
            ),
            "threshold": "141120 distinct and 3465728 weighted comparisons",
            "value": {
                "distinct": clearance_record["distinct_relation_counts"],
                "weighted": clearance_record["weighted_relation_counts"],
            },
        },
        "every_registered_comparison_is_product_below_target": {
            "passed": bool(
                validity_passed
                and clearance_record["distinct_relation_counts"]
                == EXPECTED_RELATIONS_DISTINCT
                and clearance_record["weighted_relation_counts"]
                == EXPECTED_RELATIONS_WEIGHTED
            ),
            "threshold": "all comparisons separate and zero overlaps remain",
            "value": clearance_record["distinct_relation_counts"],
        },
        "minimum_outward_and_exact_gaps_are_positive": {
            "passed": bool(
                validity_passed
                and clearance_record["minimum_outward_witness"]["outward_gap_hex"]
                == EXPECTED_MINIMUM_GAP_HEX
                and exact_gap > 0
            ),
            "threshold": "the registered outward and exact witness gaps are positive",
            "value": clearance_record["minimum_outward_witness"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if validity_passed and hypotheses_passed:
        hypothesis_outcome = "accepted"
        actual_resonance_outcome = "not_established"
        classification = ACCEPTED_CLASSIFICATION
    else:
        hypothesis_outcome = "inconclusive"
        actual_resonance_outcome = "inconclusive"
        classification = INCONCLUSIVE_CLASSIFICATION
    cycle: dict[str, Any] = {
        "question": (
            "Do rigorously contained block-zero structured-row eigendiscs clear "
            "the registered degree-sixteen obstruction?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "family_digest_sha256": family_digest,
        "row_digest_sha256": row_digest,
        "clearance_digest_sha256": clearance_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": hypothesis_outcome,
        "actual_resonance_outcome": actual_resonance_outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    accepted = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "block_zero_structured_row_eigendisc_inclusion_is_certified": accepted,
        "selected_block_zero_eigenvalues_are_covered_with_exact_multiplicity": accepted,
        "registered_degree_sixteen_obstruction_is_cleared": accepted,
        "q011ak_block_common_radius_rejection_is_preserved": True,
        "all_degree_sixteen_overlap_aggregates_are_cleared": False,
        "degree_sixteen_external_nonresonance_is_certified": False,
        "an_actual_degree_sixteen_complex_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 16)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(16, 91)),
        "degrees_16_through_90_are_certified": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011ak_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only block zero of the Q011k exact root family, selected "
        "centers 144 through 149 and Q011aj aggregate index 99 at degree sixteen for "
        "the fixed 17x17 repaired exact map on one fixed conservation leaf. It uses "
        "Q011y nonzero-block radii, exact x-Fourier multiplicities and outward-rounded "
        "dyadic products. It does not reidentify block-zero external components with "
        "Q011u modulus groups and establishes no result for the other 153 degree-sixteen "
        "overlap aggregates, degree-sixteen external nonresonance, degrees 17 through "
        "90, all-order nonresonance, higher graph smoothness, SSM existence or "
        "uniqueness, normal attraction, basin, other grid, force, wall or D3Q27 setting."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ai_certificates_and_diagnostics_changed": False,
        "q011aj_uniform_obstruction_rejection_changed": False,
        "q011ak_blockwise_obstruction_rejection_changed": False,
    }
    if accepted:
        cycle["next_change"] = (
            "Preregister Q011am to apply the contained six-source hybrid envelope "
            "to all 154 degree-sixteen overlap aggregates."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first seal, family, directed-row, component, hybrid, "
            "clearance-witness or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011al cycle failed strict serialization or digest")
    return cycle


def run_q011al_study() -> dict[str, Any]:
    cycle = run_block_zero_structured_row_audit()
    clearance = cycle["registered_obstruction_clearance_audit"][
        "clearance_record"
    ]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "directed_transcendental_type": "gmpy2.mpfr RoundUp at 256/384 bits",
            "proof_enclosure_type": "exact rational and outward-rounded IEEE-754 binary64",
            "fourier_coefficient_type": "numpy.int64 with checked crude bound",
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "basis_absolute_stream_count_per_precision": EXPECTED_BASIS_STREAM_COUNT,
            "entrywise_family_stream_count": EXPECTED_FAMILY_STREAM_COUNT,
            "registered_weighted_comparison_count": clearance[
                "weighted_comparison_count"
            ],
            "registered_distinct_comparison_count": clearance[
                "distinct_comparison_count"
            ],
        },
        "mathematical_scope": {
            "diagnostic": "block-zero structured-row clearance of one degree-16 obstruction",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
            "registered_obstruction_clearance_claim": True,
            "degree_sixteen_external_nonresonance_claim": False,
            "actual_complex_resonance_claim": False,
            "degrees_17_through_90_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011al_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
