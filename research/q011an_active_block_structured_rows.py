"""Q011an active-block structured-row eigendisc refinement audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from math import comb, inf
from math import prod as integer_product
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np

import research.q011am_degree16_hybrid_sweep as q011am
from research.q007x_mpfr_backend import fraction_from_mpfr
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011al = q011am.q011al
q011ak = q011am.q011al.q011ak
q011ag = q011am.q011ag
q011b = q011am.q011b
q011k = q011al.q011k
q011z = q011am.q011z

SIZE = 17
DIMENSION = 153
DEGREE = 16
PRIMARY_PRECISION_BITS = 256
REPLAY_PRECISION_BITS = 384
REPRESENTATIVE_BLOCKS = (1, 4)
TRANSPORTED_BLOCKS = {1: 16, 4: 13}
ACTIVE_INDICES = {
    1: (142, 143, 144, 145, 148, 149, 150, 151),
    4: (114, 115, 116, 117),
    13: (114, 115, 116, 117),
    16: (142, 143, 144, 145, 148, 149, 150, 151),
}
OBSTRUCTION_AGGREGATE_INDEX = 55

EXPECTED_ACTIVE_IDENTIFIER_COUNT = 24
EXPECTED_Q011AL_RELABEL_IDENTIFIER_COUNT = 6
EXPECTED_HYBRID_IDENTIFIER_COUNT = 204
EXPECTED_UNMODIFIED_IDENTIFIER_COUNT = 174
EXPECTED_FAMILY_ENTRY_COUNT = DIMENSION**2
EXPECTED_BASIS_STREAM_COUNT = 2 * DIMENSION**2
EXPECTED_SPARSE_NONZEROS_PER_ROW = 27
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_CLASS_DIGEST = "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
EXPECTED_HYBRID_RECORD_DIGEST = "53f84832595e7fd46c88778c35389bf2ce530d3b5e2d37a5f72deeb74ad65ad9"
EXPECTED_ACTIVE_RECORD_DIGEST = "18703d817246c705fbfdc6b195ba306f9b06c879f5642f793fe834b97c907acc"
EXPECTED_Q011AL_RELABEL_RECORD_DIGEST = (
    "7fc8e285c0f737b0f154ee854c08b77976ad7d589c7c65e5d3b5ed763aa67fee"
)

EXPECTED_BLOCK_RECORDS = {
    1: {
        "transported_block": 16,
        "family_digest": "d0f1c026613f59efec0ffa1d70f6d05182457272f9045b89fce661fc2e20145f",
        "primary_basis_digest": (
            "b96f3098ab2eb610fa9b9c21b2cd844c6f4ead1b5bab0691033728bb59fcc9e7"
        ),
        "replay_basis_digest": ("6ae4b6b32c14e68dc11f77fe4440a8e719df62997a993431e6ae21ce2d9412c3"),
        "primary_row_digest": ("4722f6383bf3e925a9336131ac0c638697b3420d2c6a905e49d25e1c6b644e6c"),
        "replay_row_digest": ("697ed5d2415bfabe4c6145c977fa1ab25ad141adde0efa87b5679d8d00b0d8a3"),
        "maximum_row_radius_index": 95,
        "maximum_row_radius_hex": "0x1.66e37547d73acp-35",
        "neumann_correction_hex": "0x1.0892c5566fb86p-77",
        "component_count": 96,
        "component_digest": ("d884728455a0caafe43cf935fc2c7aa36c199fb45bd0b19fc9394d4fc8715bc9"),
        "active_components": (
            (142,),
            (143,),
            (144,),
            (145,),
            (148,),
            (149,),
            (150, 151),
        ),
        "gap_pair": (151, 152),
        "gap_hex": "0x1.fd8363e29a48cp-8",
        "gap_digest": "015897fb41eff306d2c95ba8ade84d3801ead868c0ce85cd16a5617d24cd352f",
    },
    4: {
        "transported_block": 13,
        "family_digest": "5ca9d1bd018fcd9d6b13216f5c31462dda74949ac66dd086cfc65c1710fdf387",
        "primary_basis_digest": (
            "e98283eaef5a4812789364a3e588b111abe1f5876a89e4dbe8f6bf22119bde27"
        ),
        "replay_basis_digest": ("09104ea6b052efa341eb83c245650c21ea22eda5cffe2f90c77c0ca386490895"),
        "primary_row_digest": ("ea3006ca6421f4ffd814ddf4c82c63e4a9ddcdf53be943a6b7776e7c8d7b7fee"),
        "replay_row_digest": ("4e12fd5321ee15afc35bbd7d6918553d3978b3cbe238e4d128f6be803ad60f6a"),
        "maximum_row_radius_index": 138,
        "maximum_row_radius_hex": "0x1.0fac306f306aap-30",
        "neumann_correction_hex": "0x1.8d25920c52235p-69",
        "component_count": 98,
        "component_digest": ("864649df456f79af3d99cdbbdf0a903dd673ad5f636fb3d510780246581e22b7"),
        "active_components": ((114, 116), (115, 117)),
        "gap_pair": (115, 123),
        "gap_hex": "0x1.3faaabade11c4p-4",
        "gap_digest": "6f75e77076817dc40857d7ab1694b674e2bddb041112b83ffb509c0999104943",
    },
}

EXPECTED_OBSTRUCTION_COUNTS = (3, 12, 0, 1)
EXPECTED_OBSTRUCTION_TARGET_COUNT = 24
EXPECTED_OBSTRUCTION_ORIGINAL_MONOMIAL_COUNT = 436_800
EXPECTED_OBSTRUCTION_SIGNATURE_COUNT = 1_560
EXPECTED_OBSTRUCTION_COMPATIBLE_MONOMIAL_COUNT = 204_240
EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT = 37_440
EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT = 602_720
EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS = {
    "product_below_target": 24_960,
    "target_below_product": 12_480,
    "overlap": 0,
}
EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS = {
    "product_below_target": 388_480,
    "target_below_product": 214_240,
    "overlap": 0,
}
EXPECTED_OBSTRUCTION_AGGREGATE_DIGEST = (
    "37d0eddaa8e56a7e4424a8d687fc2d2323c5a10afa1794afc1a14e42fdd7cfc7"
)
EXPECTED_OBSTRUCTION_BOUND_DIGEST = (
    "4f7d8b87a62834291441090752638a31e12193459786eb7d9691b91d19b800a2"
)
EXPECTED_OBSTRUCTION_COEFFICIENT_DIGEST = (
    "30c3ce2f5dceb8c466fb851a948fd1f39f0e2794be7b7b5d190e3c3d9b1f0487"
)
EXPECTED_OBSTRUCTION_CLASSIFICATION_DIGEST = (
    "fbbd943591a15c93ce4f9ba550a4e08deaa95fde4ecde6f496b18f289793909e"
)
EXPECTED_MINIMUM_TARGET = "block=15;center=112"
EXPECTED_MINIMUM_LEFT_INDEX = 248
EXPECTED_MINIMUM_RIGHT_INDEX = 3
EXPECTED_MINIMUM_CLASS_COUNTS = (
    (3, 0, 0, 0),
    (1, 11),
    (0, 0, 0),
    (0, 0, 1, 0, 0, 0),
)
EXPECTED_MINIMUM_SOURCES = (
    "block=1;center=142",
    "block=1;center=142",
    "block=1;center=142",
    "block=1;center=150",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=0;center=146",
)
EXPECTED_MINIMUM_OUTWARD_GAP_HEX = "0x1.3a6e2ffffffffp-33"
EXPECTED_MINIMUM_EXACT_GAP_HEX = "0x1.3a73831f778dap-33"
EXPECTED_MINIMUM_WITNESS_DIGEST = "203d5b2e200f65fb27daed6053f6b44f5ec5bc6d0bab3870a3f20f0f8609d9cb"

EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 815
EXPECTED_OVERLAP_INVENTORY_AGGREGATE_COUNT = 154
EXPECTED_DEGREE_AGGREGATE_COUNT = 969
EXPECTED_FULLY_SEPARATED_AGGREGATE_COUNT = 154
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 7_593_735_887
EXPECTED_MODULUS_SIGNATURE_COUNT = 27_206_049
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 23_173_623
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 1_649_206_077
EXPECTED_DISTINCT_COMPARISON_COUNT = 136_891_880
EXPECTED_WEIGHTED_COMPARISON_COUNT = 3_521_974_412
EXPECTED_DISTINCT_RELATIONS = {
    "overlap": 0,
    "product_below_target": 72_338_736,
    "target_below_product": 64_553_144,
}
EXPECTED_WEIGHTED_RELATIONS = {
    "overlap": 0,
    "product_below_target": 1_901_835_848,
    "target_below_product": 1_620_138_564,
}
EXPECTED_CLASS_POWER_COUNT = 228
EXPECTED_CLASS_POWER_DIGEST = "485cae3e7851912f0eb974ff4f061847c8b8cc085eb1d49be4e62e3b6b6e6c0d"
EXPECTED_GROUP_SIGNATURE_COUNT = 77_927
EXPECTED_GROUP_SIGNATURE_DIGEST = "995779c85370afe55b2e44fc1c6dd952410d32d0eecf676959bc99f5a60f31ff"
EXPECTED_PAIR_POOL_COUNT = 85
EXPECTED_PAIR_POOL_DIGEST = "af927b867976521fd1827e509821bc03a399d52f8fce3f32642b1ebccea8773c"
EXPECTED_CONVOLUTION_CALL_COUNT = 973_967
EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND = 1_734
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 900_900
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 1_142
EXPECTED_MAXIMUM_FOURIER_CRUDE_BOUND = 8_330
EXPECTED_FULL_AGGREGATE_DIGEST = "d4982c1aac88d02db6adf03796280739e9505c66d2e9ac278034506274a836e1"
EXPECTED_FULL_BOUND_DIGEST = "2fb019ed012cdd18fe43e8be54d4707fde95cca8d30f3a5d532e88787035c223"
EXPECTED_FULL_COEFFICIENT_DIGEST = (
    "ea542f6e28fef27ed8da24bcb02af28eab59190dac4ba41c40bf8a8c7682edd9"
)
EXPECTED_FULL_CLASSIFICATION_DIGEST = (
    "ec967923474b9d434592207247c642ce798dd942b5f8221573476f3f062bec39"
)

ACCEPTED_CLASSIFICATION = (
    "the conjugacy-closed active-block refinement certifies degree-16 external nonresonance"
)
INCONCLUSIVE_CLASSIFICATION = (
    "the degree-16 component-safe active-block clearance audit is inconclusive"
)
ACTUAL_RESONANCE_OUTCOME = "ruled_out_within_registered_degree_sixteen_scope"

Q011AM_ARTIFACT_SHA256 = "c4808edd49dec80cb613834d829b6f411c516838f7183c13f6a1e01371cf8f51"
Q011AM_RUNNER_SHA256 = "c703511110165f66ebcc24ddb93b309c94a2e7b8e7e7372d4fa492e54ee25e53"
Q011AM_DIGEST_NAMES = (
    "input_digest_sha256",
    "factorization_digest_sha256",
    "enumeration_digest_sha256",
    "obstruction_digest_sha256",
    "result_digest_sha256",
)
Q011AM_DIGESTS = (
    "5378793ad9b9f0f681fbcf145e10a32ec217939ab4daa5f5014b1ba0d7b465ba",
    "894ad9beb5d5bbd6bf72d3f82b8c303d669d7dc344ce044c4651af20e499d5f1",
    "24a2c1bd3efd8a9d82c25323c4c379b727c022dc2af084cf1e949bd1bade614c",
    "ce39bfbc7ef0de8320782de9b8108408cac5359524d9b3ab8339d3be9518dc6d",
    "1daa072b1a92ed2582a44cde106fa9dc06697d39b6985f99ca9643409d1285a8",
)


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011am._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011am_degree16_hybrid_sweep.json"
    runner_path = Path(q011am.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AM_DIGEST_NAMES)
    checks = {
        "q011am_seventeen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"] and prior["direct_digest_count"] == 88 and all(prior["checks"].values())
        ),
        "q011am_artifact_sha256_matches": _file_sha256(artifact_path) == Q011AM_ARTIFACT_SHA256,
        "q011am_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AM_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AM_RUNNER_SHA256
        ),
        "q011am_digests_match": digests == Q011AM_DIGESTS,
        "q011am_registered_rejection_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["scientific_classification"] == q011am.REJECTED_CLASSIFICATION
            and cycle["theorem_consequence"][
                "aggregate_fifty_five_is_the_sole_remaining_interval_obstruction"
            ]
            and not cycle["theorem_consequence"][
                "degree_sixteen_external_nonresonance_is_certified"
            ]
        ),
        "q011am_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011am_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011am_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "ninety_three_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 93
        ),
    }
    artifacts["q011am"] = artifact
    return (
        {
            "prior_q011am_sealed_input_audit": prior,
            "q011am": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AM_DIGEST_NAMES),
                "digests": list(digests),
                "scientific_classification": cycle["scientific_classification"],
            },
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _family_differences(
    block_index: int,
    family_collision: list[list[list[RationalInterval]]],
    proposal: np.ndarray,
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
) -> tuple[list[list[Fraction]], dict[str, Any]]:
    sine, cosine = trig[block_index]
    del sine
    filter_center = RationalInterval.point(Fraction(1) - q011k.q011j.ETA) + cosine.scale(
        q011k.q011j.ETA / 2
    )
    filter_neighbour = RationalInterval.point(q011k.q011j.ETA / 4)
    phases = []
    for cx, _ in q011k.q011j.VELOCITIES:
        phase_sine, phase_cosine = trig[q011k._canonical_index(block_index * cx)]
        phases.append(q011k.ComplexRationalInterval(phase_cosine, -phase_sine))

    digest = q011al._FramedRecordDigest(f"Q011an/block-{block_index}-entrywise-family-l1/v1")
    differences: list[list[Fraction]] = []
    nonzero_counts = []
    zero = q011k.ComplexRationalInterval.zero()
    for site in range(SIZE):
        for population, (_, cy) in enumerate(q011k.q011j.VELOCITIES):
            output_row = site * 9 + population
            family_entries: dict[int, q011k.ComplexRationalInterval] = {}
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
                    family_entries[column] = phases[population] * (
                        q011k.ComplexRationalInterval(family_real, RationalInterval.point(0))
                    )
            nonzero_counts.append(len(family_entries))
            row = []
            for column in range(DIMENSION):
                interval = family_entries.get(column, zero)
                difference = q011k._complex_interval_difference(
                    interval, proposal[output_row, column]
                )
                absolute_upper = q011k._complex_rectangle_l1_upper(difference)
                row.append(absolute_upper)
                digest.update(
                    {
                        "block": block_index,
                        "row": output_row,
                        "column": column,
                        "complex_l1_difference_upper": (
                            q011z._exact_fraction_record(absolute_upper)
                        ),
                    }
                )
            differences.append(row)
    row_sums = [sum(row, Fraction(0)) for row in differences]
    return differences, {
        "block_index": block_index,
        "entry_count": digest.count,
        "entry_digest_sha256": digest.hexdigest(),
        "minimum_sparse_nonzeros_per_row": min(nonzero_counts),
        "maximum_sparse_nonzeros_per_row": max(nonzero_counts),
        "maximum_row_sum": q011z._exact_fraction_record(max(row_sums)),
    }


def _row_protocol(
    *,
    block_index: int,
    vectors: np.ndarray,
    inverse: np.ndarray,
    differences: list[list[Fraction]],
    active_indices: tuple[int, ...],
    point_residual: Fraction,
    inverse_defect: Fraction,
    common_radius: Fraction,
    precision_bits: int,
) -> tuple[dict[str, Any], list[Fraction]]:
    caller_signature = q011k.q011j._context_signature(gmpy2.get_context())
    context = q011k.q011j._proof_context(precision_bits, gmpy2.RoundUp)
    basis_digest = q011al._FramedRecordDigest(
        f"Q011an/block-{block_index}-eigenbasis-absolute-mpfr{precision_bits}/v1"
    )
    conversions_exact = True
    family_conversion_contains = True
    with context:
        vector_row_sums = []
        for row_index in range(DIMENSION):
            total = gmpy2.mpfr(0)
            for column_index in range(DIMENSION):
                value = vectors[row_index, column_index]
                real = gmpy2.mpfr(float(value.real))
                imaginary = gmpy2.mpfr(float(value.imag))
                conversions_exact = bool(
                    conversions_exact
                    and fraction_from_mpfr(real) == Fraction.from_float(float(value.real))
                    and fraction_from_mpfr(imaginary) == Fraction.from_float(float(value.imag))
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
        for row_index in range(DIMENSION):
            row = []
            total = gmpy2.mpfr(0)
            for column_index in range(DIMENSION):
                value = inverse[row_index, column_index]
                real = gmpy2.mpfr(float(value.real))
                imaginary = gmpy2.mpfr(float(value.imag))
                conversions_exact = bool(
                    conversions_exact
                    and fraction_from_mpfr(real) == Fraction.from_float(float(value.real))
                    and fraction_from_mpfr(imaginary) == Fraction.from_float(float(value.imag))
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
        for difference_row in differences:
            output_row = []
            for value in difference_row:
                upper = q011al._mpfr_upper(value)
                family_conversion_contains = bool(
                    family_conversion_contains and fraction_from_mpfr(upper) >= value
                )
                output_row.append(upper)
            difference_uppers.append(output_row)

        weighted_family_rows = []
        for row_index in range(DIMENSION):
            total = gmpy2.mpfr(0)
            for column_index in range(DIMENSION):
                total += difference_uppers[row_index][column_index] * vector_row_sums[column_index]
            weighted_family_rows.append(total)

        structured_family_rows = []
        for row_index in range(DIMENSION):
            total = gmpy2.mpfr(0)
            for inner_index in range(DIMENSION):
                total += (
                    inverse_absolutes[row_index][inner_index] * weighted_family_rows[inner_index]
                )
            structured_family_rows.append(total)

        point_residual_upper = q011al._mpfr_upper(point_residual)
        point_rows = [row_sum * point_residual_upper for row_sum in inverse_row_sums]
        pre_neumann_rows = [
            point + structured
            for point, structured in zip(point_rows, structured_family_rows, strict=True)
        ]
        neumann_factor = q011al._mpfr_upper(inverse_defect / (1 - inverse_defect))
        correction = neumann_factor * max(pre_neumann_rows)
        radius_mpfr = [value + correction for value in pre_neumann_rows]

    flags = q011k.q011j._context_flags(context)
    caller_unchanged = q011k.q011j._context_signature(gmpy2.get_context()) == caller_signature
    radii = [fraction_from_mpfr(value) for value in radius_mpfr]
    active_set = frozenset(active_indices)
    row_records = [
        {
            "center_index": center_index,
            "active": center_index in active_set,
            "row_eigendisc_radius_upper": q011z._exact_fraction_record(radii[center_index]),
            "row_eigendisc_radius_binary64_hex": float(radii[center_index]).hex(),
            "contained_in_q011y_block_radius": (radii[center_index] <= common_radius),
        }
        for center_index in range(DIMENSION)
    ]
    maximum_index = max(range(DIMENSION), key=radii.__getitem__)
    checks = {
        "all_binary64_eigenbasis_inputs_convert_exactly": conversions_exact,
        "all_exact_family_entries_are_rounded_up": family_conversion_contains,
        "basis_stream_is_complete": basis_digest.count == 2 * DIMENSION**2,
        "all_row_bounds_are_positive_and_common_radius_contained": all(
            0 < radius <= common_radius for radius in radii
        ),
        "inverse_defect_neumann_factor_is_valid": 0 < inverse_defect < 1,
        "no_forbidden_mpfr_flags": q011al._forbidden_flags_clear(flags),
        "caller_context_is_unchanged": caller_unchanged,
    }
    return {
        "block_index": block_index,
        "precision_bits": precision_bits,
        "basis_absolute_stream_count": basis_digest.count,
        "basis_absolute_stream_digest_sha256": basis_digest.hexdigest(),
        "row_records": row_records,
        "row_record_digest_sha256": q011b._canonical_json_sha256(row_records),
        "maximum_row_radius_index": maximum_index,
        "maximum_row_radius_binary64_hex": float(radii[maximum_index]).hex(),
        "neumann_correction_binary64_hex": float(fraction_from_mpfr(correction)).hex(),
        "checks": checks,
        "passed": all(checks.values()),
    }, radii


def _component_audit(
    block_index: int,
    centers: list[tuple[Fraction, Fraction]],
    active_indices: tuple[int, ...],
    radii: list[Fraction],
) -> dict[str, Any]:
    parent = list(range(DIMENSION))

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

    for left in range(DIMENSION):
        for right in range(left):
            delta_real = centers[left][0] - centers[right][0]
            delta_imaginary = centers[left][1] - centers[right][1]
            if (
                delta_real * delta_real + delta_imaginary * delta_imaginary
                <= (radii[left] + radii[right]) ** 2
            ):
                union(left, right)
    groups: dict[int, list[int]] = {}
    for index in range(DIMENSION):
        groups.setdefault(find(index), []).append(index)
    active_set = frozenset(active_indices)
    records = []
    for indices in sorted(groups.values(), key=lambda values: values[0]):
        active = [index for index in indices if index in active_set]
        inactive = [index for index in indices if index not in active_set]
        records.append(
            {
                "center_indices": indices,
                "active_center_indices": active,
                "inactive_center_indices": inactive,
                "membership": (
                    "active"
                    if active and not inactive
                    else "inactive"
                    if inactive and not active
                    else "mixed"
                ),
            }
        )
    active_components = [r for r in records if r["membership"] == "active"]
    mixed_components = [r for r in records if r["membership"] == "mixed"]
    inactive_indices = set(range(DIMENSION)) - active_set
    minimum_gap: Fraction | None = None
    minimum_pair: tuple[int, int] | None = None
    for active_index in active_indices:
        for inactive_index in inactive_indices:
            gap = (
                max(
                    abs(centers[active_index][0] - centers[inactive_index][0]),
                    abs(centers[active_index][1] - centers[inactive_index][1]),
                )
                - radii[active_index]
                - radii[inactive_index]
            )
            if minimum_gap is None or gap < minimum_gap:
                minimum_gap = gap
                minimum_pair = (active_index, inactive_index)
    if minimum_gap is None or minimum_pair is None:
        raise RuntimeError("Q011an found no active/inactive disc pair")
    gap_record = {
        "active_center_index": minimum_pair[0],
        "inactive_center_index": minimum_pair[1],
        "maximum_coordinate_distance_minus_radii": (q011z._exact_fraction_record(minimum_gap)),
        "gap_binary64_hex": float(minimum_gap).hex(),
    }
    return {
        "block_index": block_index,
        "component_count": len(records),
        "component_records": records,
        "component_digest_sha256": q011b._canonical_json_sha256(records),
        "active_component_memberships": [record["center_indices"] for record in active_components],
        "active_disc_count": sum(len(record["center_indices"]) for record in active_components),
        "mixed_component_count": len(mixed_components),
        "minimum_active_inactive_gap": gap_record,
        "minimum_active_inactive_gap_digest_sha256": (q011b._canonical_json_sha256(gap_record)),
    }


def _single_aggregate_relations(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    counts: tuple[int, ...],
    target_group: tuple[str, ...],
) -> dict[str, Any]:
    pools = q011am._HierarchicalPools(classes, lookup)
    group_pools = tuple(
        pools.group_pool(group_index, count) for group_index, count in enumerate(counts)
    )
    left = pools.pair_pool(0, counts[0], 1, counts[1])
    right = pools.pair_pool(2, counts[2], 3, counts[3])
    left_wave = np.stack([record.wave for record in left])
    right_wave = np.stack([record.wave for record in right])
    product_lower, product_upper = q011ag._product_bound_matrices(left, right)
    relation_counts: Counter[str] = Counter()
    first: dict[str, Any] | None = None
    minimum: tuple[Any, ...] | None = None
    compatible = np.zeros(product_lower.shape, dtype=bool)
    compatible_monomials = 0
    weighted_comparisons = 0
    distinct_comparisons = 0
    coefficient_records = []
    classification_records = []
    target_by_block = q011ag._target_groups_by_block(target_group)
    for output_block in sorted(target_by_block):
        target_identifiers = sorted(target_by_block[output_block])
        wave_matrix, _ = q011ag._wave_matrix(left_wave, right_wave, output_block)
        active = wave_matrix > 0
        compatible |= active
        compatible_monomials += int(wave_matrix.sum())
        weighted_comparisons += int(wave_matrix.sum()) * len(target_identifiers)
        distinct_comparisons += int(active.sum()) * len(target_identifiers)
        coefficient_records.append(
            {
                "output_block": output_block,
                "shape": list(wave_matrix.shape),
                "coefficient_sha256": q011b._array_sha256(wave_matrix.astype(">i8")),
            }
        )
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
            codes = np.zeros(wave_matrix.shape, dtype=np.uint8)
            codes[product_below] = 1
            codes[target_below] = 2
            codes[unresolved] = 3
            classification_records.append(
                {
                    "output_block": output_block,
                    "target_identifier": target_identifier,
                    "shape": list(codes.shape),
                    "classification_sha256": q011b._array_sha256(codes),
                }
            )
            for relation, mask in (
                ("product_below_target", product_below),
                ("target_below_product", target_below),
                ("overlap", unresolved),
            ):
                relation_counts[f"{relation}_distinct"] += int(mask.sum())
                relation_counts[f"{relation}_weighted"] += int(wave_matrix[mask].sum())
            if first is None and unresolved.any():
                flat = int(np.flatnonzero(unresolved)[0])
                left_index, right_index = map(int, np.unravel_index(flat, unresolved.shape))
                first = {
                    "target_identifier": target_identifier,
                    "output_block": output_block,
                    "left_index": left_index,
                    "right_index": right_index,
                    "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                    "class_counts": [
                        list(group)
                        for group in (
                            *left[left_index].class_counts,
                            *right[right_index].class_counts,
                        )
                    ],
                }
            for relation, gaps, mask in (
                ("product_below_target", product_below_gap, product_below),
                ("target_below_product", target_below_gap, target_below),
            ):
                if not mask.any():
                    continue
                candidates = np.where(mask, gaps, inf)
                flat = int(candidates.argmin())
                left_index, right_index = map(int, np.unravel_index(flat, candidates.shape))
                gap = float(candidates[left_index, right_index])
                key = (gap, target_identifier, left_index, right_index)
                raw = {
                    "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
                    "selected_type_counts": list(counts),
                    "target_identifier": target_identifier,
                    "output_block": output_block,
                    "left_index": left_index,
                    "right_index": right_index,
                    "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                    "relation": relation,
                    "class_counts": [
                        list(group)
                        for group in q011ag._signature_counts(left, right, left_index, right_index)
                    ],
                    "outward_gap": gap,
                }
                if minimum is None or key < minimum[0]:
                    minimum = (key, raw)
    if minimum is None:
        raise RuntimeError("Q011an aggregate has no separated comparison")
    minimum_witness = q011am._exact_witness(classes, lookup, minimum[1])
    original_monomials = sum(record.fiber_multiplicity for record in left) * sum(
        record.fiber_multiplicity for record in right
    )
    signature_count = len(left) * len(right)
    distinct_relations = {
        key: relation_counts[f"{key}_distinct"]
        for key in (
            "product_below_target",
            "target_below_product",
            "overlap",
        )
    }
    weighted_relations = {
        key: relation_counts[f"{key}_weighted"]
        for key in (
            "product_below_target",
            "target_below_product",
            "overlap",
        )
    }
    aggregate_record = {
        "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
        "selected_type_counts": list(counts),
        "target_identifier_count": len(target_group),
        "original_monomial_count": original_monomials,
        "modulus_signature_count": signature_count,
        "compatible_modulus_signature_count": int(compatible.sum()),
        "compatible_original_monomial_count": compatible_monomials,
        "weighted_comparison_count": weighted_comparisons,
        "distinct_comparison_count": distinct_comparisons,
        "weighted_relation_counts": weighted_relations,
        "distinct_relation_counts": distinct_relations,
        "minimum_certified_gap_lower": q011am._float_record(minimum[0][0]),
    }
    return {
        "group_pool_sizes": [len(pool) for pool in group_pools],
        "left_pool_size": len(left),
        "right_pool_size": len(right),
        "aggregate_record": aggregate_record,
        "aggregate_record_digest_sha256": q011b._canonical_json_sha256(aggregate_record),
        "bound_matrix_digest_sha256": q011b._canonical_json_sha256(
            {
                "shape": list(product_lower.shape),
                "lower_sha256": q011b._array_sha256(product_lower.astype(">f8")),
                "upper_sha256": q011b._array_sha256(product_upper.astype(">f8")),
            }
        ),
        "coefficient_matrix_digest_sha256": q011b._canonical_json_sha256(coefficient_records),
        "classification_matrix_digest_sha256": q011b._canonical_json_sha256(classification_records),
        "distinct_relation_counts": distinct_relations,
        "weighted_relation_counts": weighted_relations,
        "minimum_separated_witness": minimum_witness,
        "first_unresolved": first,
    }


def _full_component_safe_sweep(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_indices: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    pools = q011am._HierarchicalPools(classes, lookup)
    aggregate_records = []
    bound_records = []
    coefficient_records = []
    classification_records = []
    total_relations: Counter[str] = Counter()
    total_original_monomials = 0
    total_signatures = 0
    total_compatible_signatures = 0
    total_compatible_monomials = 0
    total_weighted_comparisons = 0
    total_distinct_comparisons = 0
    maximum_live_signatures = 0
    maximum_wave_coefficient = 0
    maximum_fourier_crude_bound = 0
    all_arrays_finite = True
    all_bounds_ordered = True
    all_original_monomial_counts_exact = True
    all_modulus_signature_counts_exact = True
    first_unresolved: tuple[Any, ...] | None = None
    global_minimum: tuple[Any, ...] | None = None

    for aggregate_index, (counts, group_indices, target_group) in enumerate(
        zip(overlap_counts, external_indices, target_groups, strict=True)
    ):
        left = pools.pair_pool(0, counts[0], 1, counts[1])
        right = pools.pair_pool(2, counts[2], 3, counts[3])
        left_wave = np.stack([record.wave for record in left])
        right_wave = np.stack([record.wave for record in right])
        product_lower, product_upper = q011ag._product_bound_matrices(left, right)
        signature_count = len(left) * len(right)
        maximum_live_signatures = max(maximum_live_signatures, signature_count)
        all_arrays_finite = bool(
            all_arrays_finite
            and np.isfinite(product_lower).all()
            and np.isfinite(product_upper).all()
        )
        all_bounds_ordered = bool(
            all_bounds_ordered
            and np.all(product_lower >= 0)
            and np.all(product_lower <= product_upper)
        )
        bound_records.append(
            {
                "aggregate_index": aggregate_index,
                "selected_type_counts": list(counts),
                "shape": list(product_lower.shape),
                "lower_sha256": q011b._array_sha256(product_lower.astype(">f8")),
                "upper_sha256": q011b._array_sha256(product_upper.astype(">f8")),
            }
        )
        compatible = np.zeros(product_lower.shape, dtype=bool)
        aggregate_relations: Counter[str] = Counter()
        compatible_monomials = 0
        weighted_comparisons = 0
        distinct_comparisons = 0
        aggregate_minimum: tuple[Any, ...] | None = None
        aggregate_first_overlap: tuple[Any, ...] | None = None
        target_by_block = q011ag._target_groups_by_block(target_group)
        for output_block in sorted(target_by_block):
            target_identifiers = sorted(target_by_block[output_block])
            wave_matrix, crude_bound = q011ag._wave_matrix(left_wave, right_wave, output_block)
            active = wave_matrix > 0
            compatible |= active
            compatible_monomials += int(wave_matrix.sum())
            weighted_comparisons += int(wave_matrix.sum()) * len(target_identifiers)
            distinct_comparisons += int(active.sum()) * len(target_identifiers)
            maximum_wave_coefficient = max(
                maximum_wave_coefficient, int(wave_matrix.max(initial=0))
            )
            maximum_fourier_crude_bound = max(maximum_fourier_crude_bound, crude_bound)
            coefficient_records.append(
                {
                    "aggregate_index": aggregate_index,
                    "output_block": output_block,
                    "shape": list(wave_matrix.shape),
                    "coefficient_sha256": q011b._array_sha256(wave_matrix.astype(">i8")),
                }
            )
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
                codes = np.zeros(wave_matrix.shape, dtype=np.uint8)
                codes[product_below] = 1
                codes[target_below] = 2
                codes[unresolved] = 3
                classification_records.append(
                    {
                        "aggregate_index": aggregate_index,
                        "output_block": output_block,
                        "target_identifier": target_identifier,
                        "shape": list(codes.shape),
                        "classification_sha256": q011b._array_sha256(codes),
                    }
                )
                for relation, mask in (
                    ("product_below_target", product_below),
                    ("target_below_product", target_below),
                    ("overlap", unresolved),
                ):
                    aggregate_relations[f"{relation}_distinct"] += int(mask.sum())
                    aggregate_relations[f"{relation}_weighted"] += int(wave_matrix[mask].sum())
                if unresolved.any():
                    flat_index = int(np.flatnonzero(unresolved)[0])
                    left_index, right_index = map(
                        int, np.unravel_index(flat_index, unresolved.shape)
                    )
                    key = (target_identifier, left_index, right_index)
                    raw = {
                        "aggregate_index": aggregate_index,
                        "selected_type_counts": list(counts),
                        "target_identifier": target_identifier,
                        "output_block": output_block,
                        "left_index": left_index,
                        "right_index": right_index,
                        "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                        "relation": "overlap",
                        "class_counts": [
                            list(group)
                            for group in q011ag._signature_counts(
                                left, right, left_index, right_index
                            )
                        ],
                    }
                    if aggregate_first_overlap is None or key < aggregate_first_overlap[0]:
                        aggregate_first_overlap = (key, raw)
                for relation, gaps, mask in (
                    ("product_below_target", product_below_gap, product_below),
                    ("target_below_product", target_below_gap, target_below),
                ):
                    if not mask.any():
                        continue
                    candidates = np.where(mask, gaps, inf)
                    flat_index = int(candidates.argmin())
                    left_index, right_index = map(
                        int, np.unravel_index(flat_index, candidates.shape)
                    )
                    gap = float(candidates[left_index, right_index])
                    key = (gap, target_identifier, left_index, right_index)
                    raw = {
                        "aggregate_index": aggregate_index,
                        "selected_type_counts": list(counts),
                        "target_identifier": target_identifier,
                        "output_block": output_block,
                        "left_index": left_index,
                        "right_index": right_index,
                        "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                        "relation": relation,
                        "class_counts": [
                            list(group)
                            for group in q011ag._signature_counts(
                                left, right, left_index, right_index
                            )
                        ],
                        "outward_gap": gap,
                    }
                    if aggregate_minimum is None or key < aggregate_minimum[0]:
                        aggregate_minimum = (key, raw)
        if aggregate_minimum is None:
            raise RuntimeError("Q011an aggregate has no separated comparison")
        if aggregate_first_overlap is not None:
            unresolved_key = (aggregate_index, *aggregate_first_overlap[0])
            if first_unresolved is None or unresolved_key < first_unresolved[0]:
                first_unresolved = (unresolved_key, aggregate_first_overlap[1])
        minimum_key = (
            aggregate_minimum[0][0],
            aggregate_index,
            *aggregate_minimum[0][1:],
        )
        if global_minimum is None or minimum_key < global_minimum[0]:
            global_minimum = (minimum_key, aggregate_minimum[1])
        original_monomials = sum(record.fiber_multiplicity for record in left) * sum(
            record.fiber_multiplicity for record in right
        )
        expected_original_monomials = integer_product(
            comb(count + sum(map(len, classes[group_index])) - 1, count)
            for group_index, count in enumerate(counts)
        )
        expected_signatures = integer_product(
            comb(count + len(classes[group_index]) - 1, count)
            for group_index, count in enumerate(counts)
        )
        all_original_monomial_counts_exact = bool(
            all_original_monomial_counts_exact and original_monomials == expected_original_monomials
        )
        all_modulus_signature_counts_exact = bool(
            all_modulus_signature_counts_exact and signature_count == expected_signatures
        )
        weighted_relations = q011am._relation_counts(aggregate_relations, "weighted")
        distinct_relations = q011am._relation_counts(aggregate_relations, "distinct")
        total_relations.update(aggregate_relations)
        total_original_monomials += original_monomials
        total_signatures += signature_count
        total_compatible_signatures += int(compatible.sum())
        total_compatible_monomials += compatible_monomials
        total_weighted_comparisons += weighted_comparisons
        total_distinct_comparisons += distinct_comparisons
        aggregate_records.append(
            {
                "aggregate_index": aggregate_index,
                "selected_type_counts": list(counts),
                "external_group_indices": list(group_indices),
                "target_identifier_count": len(target_group),
                "original_monomial_count": original_monomials,
                "modulus_signature_count": signature_count,
                "compatible_modulus_signature_count": int(compatible.sum()),
                "compatible_original_monomial_count": compatible_monomials,
                "weighted_comparison_count": weighted_comparisons,
                "distinct_comparison_count": distinct_comparisons,
                "weighted_relation_counts": weighted_relations,
                "distinct_relation_counts": distinct_relations,
                "minimum_certified_gap_lower": q011am._float_record(aggregate_minimum[0][0]),
                "minimum_witness": {
                    key: value
                    for key, value in aggregate_minimum[1].items()
                    if key != "outward_gap"
                },
            }
        )
    if global_minimum is None:
        raise RuntimeError("Q011an did not find a global separated comparison")

    power_records = pools.power_records()
    group_record_count, factor_digest, pair_records = pools.factorization_digest()
    first_witness = (
        q011am._exact_witness(classes, lookup, first_unresolved[1])
        if first_unresolved is not None
        else None
    )
    minimum_witness = q011am._exact_witness(classes, lookup, global_minimum[1])
    fully_separated = sum(
        record["distinct_relation_counts"]["overlap"] == 0 for record in aggregate_records
    )
    overlap_indices = [
        record["aggregate_index"]
        for record in aggregate_records
        if record["distinct_relation_counts"]["overlap"] > 0
    ]
    return {
        "degree": 16,
        "audited_overlap_aggregate_count": len(aggregate_records),
        "fully_separated_overlap_aggregate_count": fully_separated,
        "remaining_overlap_aggregate_count": len(overlap_indices),
        "remaining_overlap_aggregate_indices": overlap_indices,
        "original_monomial_count": total_original_monomials,
        "modulus_signature_count": total_signatures,
        "compatible_modulus_signature_count": total_compatible_signatures,
        "compatible_original_monomial_count": total_compatible_monomials,
        "weighted_comparison_count": total_weighted_comparisons,
        "distinct_comparison_count": total_distinct_comparisons,
        "weighted_relation_counts": q011am._relation_counts(total_relations, "weighted"),
        "distinct_relation_counts": q011am._relation_counts(total_relations, "distinct"),
        "aggregate_records": aggregate_records,
        "aggregate_record_digest_sha256": q011b._canonical_json_sha256(aggregate_records),
        "class_power_record_count": len(power_records),
        "class_power_record_digest_sha256": q011b._canonical_json_sha256(power_records),
        "group_signature_record_count": group_record_count,
        "group_signature_digest_sha256": factor_digest,
        "pair_pool_record_count": len(pair_records),
        "pair_pool_record_digest_sha256": q011b._canonical_json_sha256(pair_records),
        "bound_matrix_record_count": len(bound_records),
        "bound_matrix_digest_sha256": q011b._canonical_json_sha256(bound_records),
        "coefficient_matrix_record_count": len(coefficient_records),
        "coefficient_matrix_digest_sha256": q011b._canonical_json_sha256(coefficient_records),
        "classification_matrix_record_count": len(classification_records),
        "classification_matrix_digest_sha256": q011b._canonical_json_sha256(classification_records),
        "global_minimum_separated_witness": minimum_witness,
        "first_unresolved_witness": first_witness,
        "maximum_live_combined_signature_count": maximum_live_signatures,
        "maximum_wave_coefficient": maximum_wave_coefficient,
        "maximum_fourier_crude_int64_bound": maximum_fourier_crude_bound,
        "convolution_call_count": pools.ledger.call_count,
        "maximum_convolution_crude_int64_bound": pools.ledger.maximum_crude_bound,
        "all_convolutions_nonnegative": pools.ledger.all_nonnegative,
        "all_convolution_fiber_sums_exact": pools.ledger.all_fiber_sums_exact,
        "all_product_bound_arrays_are_finite": all_arrays_finite,
        "all_product_bound_arrays_are_nonnegative_and_ordered": all_bounds_ordered,
        "all_original_monomial_counts_match_multiset_coefficients": (
            all_original_monomial_counts_exact
        ),
        "all_modulus_signature_counts_match_weak_compositions": (
            all_modulus_signature_counts_exact
        ),
        "streaming_contract": {
            "full_degree_sixteen_monomial_list_retained": False,
            "full_classification_matrices_retained": False,
            "aggregate_summary_count": len(aggregate_records),
            "peak_live_combined_signature_count": maximum_live_signatures,
            "hierarchical_class_power_cache_count": len(power_records),
            "group_pool_cache_count": len(pools.group_cache),
            "pair_pool_cache_count": len(pools.pair_cache),
        },
    }


def run_q011an_pilot(*, full_sweep: bool = True) -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    hybrid, base_lookup, _, counts, _, targets = q011am._hybrid_input_audit(artifacts)
    k_sealed, q011j_artifact, _ = q011k._sealed_input_audit()
    coordinate, lifted, lift_matrix, state_box, _, _root = q011k._root_enclosure_audit(
        q011j_artifact
    )
    del coordinate, lift_matrix
    state_float = np.asarray([float(value) for value in lifted], dtype=np.float64).reshape(
        SIZE, 1, 9
    )
    proposals = {
        block_index: q011b._block_matrix(state_float, 2.0 * np.pi * block_index / SIZE)
        for block_index in REPRESENTATIVE_BLOCKS
    }
    stored_family_records = {
        record["block_index"]: record
        for record in artifacts["q011k"]["cycle"]["exact_interval_block_family_audit"][
            "block_records"
        ]
    }
    family_distances = {
        block_index: q011z._fraction(
            stored_family_records[block_index]["interval_family_distance_infinity_upper"]
        )
        for block_index in REPRESENTATIVE_BLOCKS
    }
    centers, _selected, _, metrics, spectral = q011z.q011l._spectral_data(artifacts["q011k"])
    family_collision, _ = q011k._collision_derivative_blocks(state_box)
    trig = q011k.trigonometric_intervals(q011k.machin_pi_interval())
    proof_records = {
        record["block_index"]: record
        for record in artifacts["q011k"]["cycle"]["dual_precision_bauer_fike_audit"][
            "representative_block_records"
        ]
    }
    blocks: dict[int, Any] = {}
    radii_by_block: dict[int, list[Fraction]] = {}
    for block_index in REPRESENTATIVE_BLOCKS:
        differences, family = _family_differences(
            block_index,
            family_collision,
            proposals[block_index],
            trig,
        )
        values, vectors, inverse, eig = q011k._canonical_eigendecomposition(proposals[block_index])
        proof = proof_records[block_index]
        primary_proof = proof["primary_precision_proof"]
        point_residual = q011z._fraction(
            primary_proof["point_eigendecomposition_residual_infinity_upper"]
        )
        inverse_defect = q011z._fraction(primary_proof["inverse_defect_infinity_norm_upper"])
        transported = TRANSPORTED_BLOCKS[block_index]
        active = ACTIVE_INDICES[block_index]
        primary, primary_radii = _row_protocol(
            block_index=block_index,
            vectors=vectors,
            inverse=inverse,
            differences=differences,
            active_indices=active,
            point_residual=point_residual,
            inverse_defect=inverse_defect,
            common_radius=metrics[block_index]["theta"],
            precision_bits=PRIMARY_PRECISION_BITS,
        )
        replay, replay_radii = _row_protocol(
            block_index=block_index,
            vectors=vectors,
            inverse=inverse,
            differences=differences,
            active_indices=active,
            point_residual=point_residual,
            inverse_defect=inverse_defect,
            common_radius=metrics[block_index]["theta"],
            precision_bits=REPLAY_PRECISION_BITS,
        )
        radii_by_block[block_index] = primary_radii
        radii_by_block[transported] = primary_radii
        transported_family = stored_family_records[transported]
        blocks[block_index] = {
            "transported_block": transported,
            "family": family,
            "family_distance_matches": q011z._fraction(family["maximum_row_sum"])
            == family_distances[block_index],
            "transport_metadata_matches": bool(
                transported_family["transported_from"] == block_index
                and q011z._fraction(transported_family["interval_family_distance_infinity_upper"])
                == family_distances[block_index]
            ),
            "proposal_matches": q011b._array_sha256(proposals[block_index])
            == stored_family_records[block_index]["proposal_sha256"],
            "eigendecomposition_matches": eig == proof["eigendecomposition"],
            "centers_match": [
                (
                    Fraction.from_float(float(value.real)),
                    Fraction.from_float(float(value.imag)),
                )
                for value in values
            ]
            == centers[block_index],
            "transported_centers_are_exact_conjugates": all(
                centers[transported][center_index]
                == (
                    centers[block_index][center_index][0],
                    -centers[block_index][center_index][1],
                )
                for center_index in range(DIMENSION)
            ),
            "primary": primary,
            "replay": replay,
            "replay_strict": all(
                replay_radius < primary_radius
                for primary_radius, replay_radius in zip(primary_radii, replay_radii, strict=True)
            ),
            "representative_component": _component_audit(
                block_index,
                centers[block_index],
                active,
                primary_radii,
            ),
            "transported_component": _component_audit(
                transported,
                centers[transported],
                ACTIVE_INDICES[transported],
                primary_radii,
            ),
        }

    active_set = frozenset(
        f"block={block_index};center={center_index}"
        for block_index, indices in ACTIVE_INDICES.items()
        for center_index in indices
    )
    component_audits = {
        1: blocks[1]["representative_component"],
        16: blocks[1]["transported_component"],
        4: blocks[4]["representative_component"],
        13: blocks[4]["transported_component"],
    }
    active_component_hulls: dict[str, tuple[RationalInterval, tuple[int, ...]]] = {}
    for block_index, component in component_audits.items():
        for members_raw in component["active_component_memberships"]:
            members = tuple(members_raw)
            individual_intervals = []
            for center_index in members:
                identifier = f"block={block_index};center={center_index}"
                base = base_lookup[identifier]
                radius = radii_by_block[block_index][center_index]
                individual_intervals.append(
                    RationalInterval(
                        max(Fraction(0), base.center_modulus.lower - radius),
                        base.center_modulus.upper + radius,
                    )
                )
            hull = RationalInterval(
                min(interval.lower for interval in individual_intervals),
                max(interval.upper for interval in individual_intervals),
            )
            for center_index in members:
                active_component_hulls[f"block={block_index};center={center_index}"] = (
                    hull,
                    members,
                )
    if frozenset(active_component_hulls) != active_set:
        raise RuntimeError("Q011an active Gershgorin components do not cover the active set")

    q011al_component_hulls: dict[str, tuple[RationalInterval, tuple[int, ...]]] = {}
    q011al_components = artifacts["q011al"]["cycle"]["block_zero_gershgorin_component_audit"][
        "selected_component_records"
    ]
    for component in q011al_components:
        members = tuple(component["center_indices"])
        identifiers = tuple(f"block=0;center={center_index}" for center_index in members)
        hull = RationalInterval(
            min(base_lookup[identifier].modulus.lower for identifier in identifiers),
            max(base_lookup[identifier].modulus.upper for identifier in identifiers),
        )
        for identifier in identifiers:
            q011al_component_hulls[identifier] = (hull, members)
    q011al_relabel_set = frozenset(q011al_component_hulls)
    q011al_records = {
        record["identifier"]: record
        for record in artifacts["q011al"]["cycle"]["hybrid_selected_block_zero_envelope_audit"][
            "hybrid_disc_records"
        ]
    }
    blockwise_records = {
        record["identifier"]: record
        for record in artifacts["q011ak"]["cycle"]["blockwise_transformed_residual_envelope_audit"][
            "blockwise_disc_records"
        ]
    }

    refined_lookup: dict[str, q011z._UniformDisc] = {}
    hybrid_records = []
    unmodified_intervals_match = True
    for identifier, base in base_lookup.items():
        block_index, center_index = q011z._identifier_indices(identifier)
        active_refined = identifier in active_set
        q011al_relabelled = identifier in q011al_relabel_set
        if active_refined:
            radius = radii_by_block[block_index][center_index]
            modulus, component_members = active_component_hulls[identifier]
            radius_kind = "active_block_component_hull"
        elif q011al_relabelled:
            radius = q011z._fraction(q011al_records[identifier]["radius_upper"])
            modulus, component_members = q011al_component_hulls[identifier]
            radius_kind = "q011al_component_relabel_hull"
        else:
            radius = None
            component_members = None
            modulus = base.modulus
            radius_kind = "q011am_hybrid"
            unmodified_intervals_match = bool(
                unmodified_intervals_match and modulus == base.modulus
            )
        contained_in_q011am = bool(
            modulus.lower >= base.modulus.lower and modulus.upper <= base.modulus.upper
        )
        blockwise_record = blockwise_records[identifier]
        blockwise_modulus = RationalInterval(
            q011z._fraction(blockwise_record["blockwise_modulus_lower"]),
            q011z._fraction(blockwise_record["blockwise_modulus_upper"]),
        )
        contained_in_q011ak = bool(
            modulus.lower >= blockwise_modulus.lower and modulus.upper <= blockwise_modulus.upper
        )
        refined_lookup[identifier] = q011z._UniformDisc(
            identifier=identifier,
            block_index=block_index,
            center_index=center_index,
            center_modulus=base.center_modulus,
            modulus=modulus,
        )
        hybrid_records.append(
            {
                "identifier": identifier,
                "block_index": block_index,
                "center_index": center_index,
                "radius_kind": radius_kind,
                "gershgorin_component_center_indices": (
                    list(component_members) if component_members is not None else None
                ),
                "row_radius_upper": (
                    q011z._exact_fraction_record(radius) if radius is not None else None
                ),
                "modulus_lower": q011z._exact_fraction_record(modulus.lower),
                "modulus_upper": q011z._exact_fraction_record(modulus.upper),
                "contained_in_q011am_hybrid_interval": contained_in_q011am,
                "contained_in_q011ak_blockwise_interval": contained_in_q011ak,
            }
        )
    refined_identifiers = sorted(active_set, key=q011z._identifier_indices)
    selected_groups = tuple(
        tuple(group)
        for group in artifacts["q011aj"]["cycle"]["degree16_modulus_inventory_audit"][
            "selected_source_group_memberships"
        ]
    )
    refined_classes, class_records = q011ag._modulus_classes(selected_groups, refined_lookup)
    class_interval_consistency = all(
        len(
            {
                (
                    refined_lookup[identifier].modulus.lower,
                    refined_lookup[identifier].modulus.upper,
                )
                for identifier in identifiers
            }
        )
        == 1
        for group in refined_classes
        for identifiers in group
    )
    relation = _single_aggregate_relations(
        refined_classes,
        refined_lookup,
        counts[OBSTRUCTION_AGGREGATE_INDEX],
        targets[OBSTRUCTION_AGGREGATE_INDEX],
    )
    external_indices = tuple(
        tuple(record["external_group_indices"])
        for record in artifacts["q011aj"]["cycle"]["degree16_modulus_inventory_audit"][
            "overlap_records"
        ]
    )
    full_sweep_result = (
        _full_component_safe_sweep(
            refined_classes,
            refined_lookup,
            counts,
            external_indices,
            targets,
        )
        if full_sweep
        else None
    )
    result = {
        "sealed_input_audit": sealed,
        "q011am_hybrid_input_audit": hybrid,
        "q011k_inputs_pass": k_sealed["passed"],
        "q011l_spectral_pass": spectral["passed"],
        "q011am_hybrid_pass": hybrid["passed"],
        "active_identifiers": refined_identifiers,
        "active_identifier_count": len(refined_identifiers),
        "q011al_component_relabel_identifiers": sorted(
            q011al_relabel_set, key=q011z._identifier_indices
        ),
        "q011al_component_relabel_identifier_count": len(q011al_relabel_set),
        "hybrid_identifier_count": len(hybrid_records),
        "hybrid_records": hybrid_records,
        "hybrid_record_digest_sha256": q011b._canonical_json_sha256(hybrid_records),
        "active_record_digest_sha256": q011b._canonical_json_sha256(
            [record for record in hybrid_records if record["identifier"] in active_set]
        ),
        "q011al_component_relabel_record_digest_sha256": q011b._canonical_json_sha256(
            [record for record in hybrid_records if record["identifier"] in q011al_relabel_set]
        ),
        "all_active_refined_intervals_are_contained_in_q011am": all(
            record["contained_in_q011am_hybrid_interval"]
            for record in hybrid_records
            if record["identifier"] in active_set
        ),
        "all_component_safe_intervals_are_contained_in_q011ak": all(
            record["contained_in_q011ak_blockwise_interval"] for record in hybrid_records
        ),
        "all_unmodified_intervals_match_q011am": unmodified_intervals_match,
        "conjugate_active_intervals_match": all(
            refined_lookup[f"block={left};center={center}"].modulus
            == refined_lookup[f"block={right};center={center}"].modulus
            for left, right, indices in (
                (1, 16, ACTIVE_INDICES[1]),
                (4, 13, ACTIVE_INDICES[4]),
            )
            for center in indices
        ),
        "representative_blocks": blocks,
        "refined_class_counts": [len(group) for group in refined_classes],
        "refined_class_digest_sha256": q011b._canonical_json_sha256(class_records),
        "class_interval_consistency": class_interval_consistency,
        "aggregate_fifty_five": relation,
        "full_component_safe_sweep": full_sweep_result,
    }
    if not (
        _all_numeric_values_finite(result)
        and _strict_json_serializable(result)
        and json.dumps(result, allow_nan=False)
    ):
        raise RuntimeError("Q011an pilot failed strict serialization")
    return result


def _registered_parameters() -> dict[str, Any]:
    return {
        "grid_size": [SIZE, SIZE],
        "fixed_conservation_leaf": True,
        "degree": DEGREE,
        "dimension_per_nonzero_fourier_block": DIMENSION,
        "representative_blocks": list(REPRESENTATIVE_BLOCKS),
        "transported_blocks": {
            str(block): transported for block, transported in TRANSPORTED_BLOCKS.items()
        },
        "active_indices": {str(block): list(indices) for block, indices in ACTIVE_INDICES.items()},
        "q011al_component_relabel_memberships": [
            [144, 146],
            [145, 147],
            [148, 149],
        ],
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "replay_precision_bits": REPLAY_PRECISION_BITS,
        "rounding_mode": "RoundUp",
        "complex_family_difference_norm": "entrywise complex rectangle L1 upper",
        "active_component_interval_rule": (
            "every identifier in an isolated active Gershgorin component receives "
            "the common modulus hull of every row disc in that component"
        ),
        "q011al_relabel_interval_rule": (
            "the six selected block-zero identifiers receive the common modulus hull "
            "of their pre-existing Q011al component row discs"
        ),
        "old_separation_parent_envelope": "Q011ak blockwise modulus intervals",
        "full_sweep_protocol": "Q011am hierarchical exact-multiplicity protocol",
        "disc_label_logic": (
            "no one-to-one eigenvalue/disc label is assumed: every source factor may "
            "choose any certified disc independently with repetition, and every target "
            "disc is audited"
        ),
        "registered_hybrid_record_digest_sha256": EXPECTED_HYBRID_RECORD_DIGEST,
        "registered_full_aggregate_digest_sha256": EXPECTED_FULL_AGGREGATE_DIGEST,
        "registered_full_classification_digest_sha256": (EXPECTED_FULL_CLASSIFICATION_DIGEST),
        "registered_classification": ACCEPTED_CLASSIFICATION,
    }


def _component_matches_expected(component: dict[str, Any], expected: dict[str, Any]) -> bool:
    gap = component["minimum_active_inactive_gap"]
    pair = (gap["active_center_index"], gap["inactive_center_index"])
    memberships = tuple(tuple(values) for values in component["active_component_memberships"])
    return bool(
        component["component_count"] == expected["component_count"]
        and component["component_digest_sha256"] == expected["component_digest"]
        and memberships == expected["active_components"]
        and component["active_disc_count"] == sum(map(len, expected["active_components"]))
        and component["mixed_component_count"] == 0
        and pair == expected["gap_pair"]
        and q011z._fraction(gap["maximum_coordinate_distance_minus_radii"]) > 0
        and gap["gap_binary64_hex"] == expected["gap_hex"]
        and component["minimum_active_inactive_gap_digest_sha256"] == expected["gap_digest"]
    )


def _active_block_structured_row_audit(raw: dict[str, Any]) -> dict[str, Any]:
    blocks = raw["representative_blocks"]
    exact_family_checks = []
    row_checks = []
    component_checks = []
    for block_index in REPRESENTATIVE_BLOCKS:
        block = blocks[block_index]
        expected = EXPECTED_BLOCK_RECORDS[block_index]
        family = block["family"]
        primary = block["primary"]
        replay = block["replay"]
        exact_family_checks.append(
            bool(
                block["transported_block"] == expected["transported_block"]
                and block["family_distance_matches"]
                and block["transport_metadata_matches"]
                and block["proposal_matches"]
                and block["eigendecomposition_matches"]
                and block["centers_match"]
                and block["transported_centers_are_exact_conjugates"]
                and family["entry_count"] == EXPECTED_FAMILY_ENTRY_COUNT
                and family["entry_digest_sha256"] == expected["family_digest"]
                and family["minimum_sparse_nonzeros_per_row"] == EXPECTED_SPARSE_NONZEROS_PER_ROW
                and family["maximum_sparse_nonzeros_per_row"] == EXPECTED_SPARSE_NONZEROS_PER_ROW
            )
        )
        row_checks.append(
            bool(
                primary["passed"]
                and replay["passed"]
                and all(primary["checks"].values())
                and all(replay["checks"].values())
                and primary["precision_bits"] == PRIMARY_PRECISION_BITS
                and replay["precision_bits"] == REPLAY_PRECISION_BITS
                and primary["basis_absolute_stream_count"]
                == replay["basis_absolute_stream_count"]
                == EXPECTED_BASIS_STREAM_COUNT
                and primary["basis_absolute_stream_digest_sha256"]
                == expected["primary_basis_digest"]
                and replay["basis_absolute_stream_digest_sha256"] == expected["replay_basis_digest"]
                and primary["row_record_digest_sha256"] == expected["primary_row_digest"]
                and replay["row_record_digest_sha256"] == expected["replay_row_digest"]
                and len(primary["row_records"]) == len(replay["row_records"]) == DIMENSION
                and block["replay_strict"]
                and primary["maximum_row_radius_index"] == expected["maximum_row_radius_index"]
                and primary["maximum_row_radius_binary64_hex"] == expected["maximum_row_radius_hex"]
                and primary["neumann_correction_binary64_hex"] == expected["neumann_correction_hex"]
            )
        )
        component_checks.append(
            bool(
                _component_matches_expected(block["representative_component"], expected)
                and _component_matches_expected(block["transported_component"], expected)
            )
        )
    checks = {
        "q011k_root_spectral_and_proof_inputs_reconstruct": bool(
            raw["q011k_inputs_pass"] and raw["q011l_spectral_pass"]
        ),
        "two_representative_exact_families_and_conjugate_transports_reproduce": bool(
            set(blocks) == set(REPRESENTATIVE_BLOCKS) and all(exact_family_checks)
        ),
        "dual_precision_structured_row_protocols_reproduce": all(row_checks),
        "active_gershgorin_components_are_isolated_with_exact_multiplicity": all(component_checks),
    }
    return {
        "representative_block_count": len(blocks),
        "active_identifier_count": raw["active_identifier_count"],
        "representative_block_records": blocks,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _component_safe_envelope_audit(raw: dict[str, Any]) -> dict[str, Any]:
    records = raw["hybrid_records"]
    active_identifiers = raw["active_identifiers"]
    relabel_identifiers = raw["q011al_component_relabel_identifiers"]
    active_set = frozenset(active_identifiers)
    relabel_set = frozenset(relabel_identifiers)
    unmodified = [record for record in records if record["radius_kind"] == "q011am_hybrid"]
    component_interval_consistency = True
    for selected_set in (active_set, relabel_set):
        component_groups: dict[tuple[int, tuple[int, ...]], set[tuple[Any, Any]]] = {}
        for record in records:
            if record["identifier"] not in selected_set:
                continue
            key = (
                record["block_index"],
                tuple(record["gershgorin_component_center_indices"]),
            )
            component_groups.setdefault(key, set()).add(
                (
                    q011z._fraction(record["modulus_lower"]),
                    q011z._fraction(record["modulus_upper"]),
                )
            )
        component_interval_consistency = bool(
            component_interval_consistency
            and all(len(intervals) == 1 for intervals in component_groups.values())
        )
    checks = {
        "registered_identifier_sets_are_disjoint_and_complete": bool(
            len(active_set) == EXPECTED_ACTIVE_IDENTIFIER_COUNT
            and len(relabel_set) == EXPECTED_Q011AL_RELABEL_IDENTIFIER_COUNT
            and not active_set.intersection(relabel_set)
            and len(records) == EXPECTED_HYBRID_IDENTIFIER_COUNT
            and len(unmodified) == EXPECTED_UNMODIFIED_IDENTIFIER_COUNT
        ),
        "registered_component_safe_record_digests_reproduce": bool(
            raw["hybrid_record_digest_sha256"] == EXPECTED_HYBRID_RECORD_DIGEST
            and raw["active_record_digest_sha256"] == EXPECTED_ACTIVE_RECORD_DIGEST
            and raw["q011al_component_relabel_record_digest_sha256"]
            == EXPECTED_Q011AL_RELABEL_RECORD_DIGEST
        ),
        "active_intervals_are_q011am_contained_and_all_intervals_are_q011ak_contained": bool(
            raw["all_active_refined_intervals_are_contained_in_q011am"]
            and raw["all_component_safe_intervals_are_contained_in_q011ak"]
            and raw["all_unmodified_intervals_match_q011am"]
        ),
        "common_component_hulls_and_conjugate_transports_are_consistent": bool(
            component_interval_consistency and raw["conjugate_active_intervals_match"]
        ),
        "modulus_classes_and_intervals_reproduce": bool(
            tuple(raw["refined_class_counts"]) == EXPECTED_CLASS_COUNTS
            and raw["refined_class_digest_sha256"] == EXPECTED_CLASS_DIGEST
            and raw["class_interval_consistency"]
        ),
        "q011am_hybrid_input_reconstructs": bool(
            raw["q011am_hybrid_pass"]
            and raw["q011am_hybrid_input_audit"]["passed"]
            and all(raw["q011am_hybrid_input_audit"]["checks"].values())
        ),
    }
    return {
        "identifier_record_count": len(records),
        "active_identifier_count": len(active_set),
        "q011al_component_relabel_identifier_count": len(relabel_set),
        "unmodified_identifier_count": len(unmodified),
        "active_identifiers": active_identifiers,
        "q011al_component_relabel_identifiers": relabel_identifiers,
        "component_safe_records": records,
        "component_safe_record_digest_sha256": raw["hybrid_record_digest_sha256"],
        "active_record_digest_sha256": raw["active_record_digest_sha256"],
        "q011al_component_relabel_record_digest_sha256": raw[
            "q011al_component_relabel_record_digest_sha256"
        ],
        "selected_modulus_class_counts": raw["refined_class_counts"],
        "class_membership_digest_sha256": raw["refined_class_digest_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
    }


def _minimum_witness_matches(witness: dict[str, Any]) -> bool:
    return bool(
        witness["aggregate_index"] == OBSTRUCTION_AGGREGATE_INDEX
        and tuple(witness["selected_type_counts"]) == EXPECTED_OBSTRUCTION_COUNTS
        and witness["target_identifier"] == EXPECTED_MINIMUM_TARGET
        and witness["left_index"] == EXPECTED_MINIMUM_LEFT_INDEX
        and witness["right_index"] == EXPECTED_MINIMUM_RIGHT_INDEX
        and witness["wave_multiplicity"] == 1
        and witness["relation"] == "product_below_target"
        and witness["block_zero_multiplicity"] == 1
        and tuple(tuple(group) for group in witness["class_counts"])
        == EXPECTED_MINIMUM_CLASS_COUNTS
        and tuple(witness["source_identifiers"]) == EXPECTED_MINIMUM_SOURCES
        and witness["outward_gap_lower"]["binary64_hex"] == EXPECTED_MINIMUM_OUTWARD_GAP_HEX
        and witness["exact_gap_hex"] == EXPECTED_MINIMUM_EXACT_GAP_HEX
        and q011z._fraction(witness["exact_gap"]) > 0
        and witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    )


def _aggregate_fifty_five_audit(raw: dict[str, Any]) -> dict[str, Any]:
    relation = raw["aggregate_fifty_five"]
    record = relation["aggregate_record"]
    minimum = relation["minimum_separated_witness"]
    checks = {
        "registered_pool_and_comparison_counts_reproduce": bool(
            relation["group_pool_sizes"] == [20, 13, 1, 6]
            and relation["left_pool_size"] == 260
            and relation["right_pool_size"] == 6
            and tuple(record["selected_type_counts"]) == EXPECTED_OBSTRUCTION_COUNTS
            and record["target_identifier_count"] == EXPECTED_OBSTRUCTION_TARGET_COUNT
            and record["original_monomial_count"] == EXPECTED_OBSTRUCTION_ORIGINAL_MONOMIAL_COUNT
            and record["modulus_signature_count"] == EXPECTED_OBSTRUCTION_SIGNATURE_COUNT
            and record["compatible_modulus_signature_count"] == EXPECTED_OBSTRUCTION_SIGNATURE_COUNT
            and record["compatible_original_monomial_count"]
            == EXPECTED_OBSTRUCTION_COMPATIBLE_MONOMIAL_COUNT
            and record["distinct_comparison_count"]
            == EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT
            and record["weighted_comparison_count"]
            == EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT
        ),
        "registered_relation_counts_and_matrix_digests_reproduce": bool(
            relation["distinct_relation_counts"]
            == record["distinct_relation_counts"]
            == EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS
            and relation["weighted_relation_counts"]
            == record["weighted_relation_counts"]
            == EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS
            and relation["aggregate_record_digest_sha256"] == EXPECTED_OBSTRUCTION_AGGREGATE_DIGEST
            and relation["bound_matrix_digest_sha256"] == EXPECTED_OBSTRUCTION_BOUND_DIGEST
            and relation["coefficient_matrix_digest_sha256"]
            == EXPECTED_OBSTRUCTION_COEFFICIENT_DIGEST
            and relation["classification_matrix_digest_sha256"]
            == EXPECTED_OBSTRUCTION_CLASSIFICATION_DIGEST
        ),
        "all_comparisons_are_separated": bool(
            relation["first_unresolved"] is None
            and relation["distinct_relation_counts"]["overlap"] == 0
            and relation["weighted_relation_counts"]["overlap"] == 0
        ),
        "registered_positive_minimum_witness_reproduces": _minimum_witness_matches(minimum),
    }
    return {
        **relation,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _full_degree_sixteen_sweep_audit(
    raw: dict[str, Any], aggregate_fifty_five: dict[str, Any]
) -> dict[str, Any]:
    sweep = raw["full_component_safe_sweep"]
    if sweep is None:
        raise RuntimeError("Q011an official audit requires the full sweep")
    minimum = sweep["global_minimum_separated_witness"]
    obstruction = sweep["aggregate_records"][OBSTRUCTION_AGGREGATE_INDEX]
    checks = {
        "registered_hierarchical_resource_values_reproduce": bool(
            sweep["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and sweep["class_power_record_digest_sha256"] == EXPECTED_CLASS_POWER_DIGEST
            and sweep["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
            and sweep["group_signature_digest_sha256"] == EXPECTED_GROUP_SIGNATURE_DIGEST
            and sweep["pair_pool_record_count"] == EXPECTED_PAIR_POOL_COUNT
            and sweep["pair_pool_record_digest_sha256"] == EXPECTED_PAIR_POOL_DIGEST
            and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
            and sweep["maximum_convolution_crude_int64_bound"]
            == EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND
            and sweep["maximum_live_combined_signature_count"]
            == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
            and sweep["maximum_wave_coefficient"] == EXPECTED_MAXIMUM_WAVE_COEFFICIENT
            and sweep["maximum_fourier_crude_int64_bound"] == EXPECTED_MAXIMUM_FOURIER_CRUDE_BOUND
        ),
        "all_exact_integer_and_outward_array_invariants_hold": bool(
            sweep["all_convolutions_nonnegative"]
            and sweep["all_convolution_fiber_sums_exact"]
            and sweep["all_product_bound_arrays_are_finite"]
            and sweep["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and sweep["all_original_monomial_counts_match_multiset_coefficients"]
            and sweep["all_modulus_signature_counts_match_weak_compositions"]
        ),
        "independent_disc_choices_with_repetition_are_exhaustive": bool(
            sweep["all_original_monomial_counts_match_multiset_coefficients"]
            and sweep["all_modulus_signature_counts_match_weak_compositions"]
            and sweep["classification_matrix_record_count"] == 1_464
        ),
        "registered_full_sweep_counts_and_relations_reproduce": bool(
            sweep["audited_overlap_aggregate_count"] == EXPECTED_OVERLAP_INVENTORY_AGGREGATE_COUNT
            and sweep["fully_separated_overlap_aggregate_count"]
            == EXPECTED_FULLY_SEPARATED_AGGREGATE_COUNT
            and sweep["remaining_overlap_aggregate_count"] == 0
            and sweep["remaining_overlap_aggregate_indices"] == []
            and sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and sweep["compatible_modulus_signature_count"] == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and sweep["compatible_original_monomial_count"] == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and sweep["distinct_comparison_count"] == EXPECTED_DISTINCT_COMPARISON_COUNT
            and sweep["weighted_comparison_count"] == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and sweep["distinct_relation_counts"] == EXPECTED_DISTINCT_RELATIONS
            and sweep["weighted_relation_counts"] == EXPECTED_WEIGHTED_RELATIONS
        ),
        "registered_full_sweep_matrix_digests_reproduce": bool(
            sweep["aggregate_record_digest_sha256"] == EXPECTED_FULL_AGGREGATE_DIGEST
            and sweep["bound_matrix_record_count"] == EXPECTED_OVERLAP_INVENTORY_AGGREGATE_COUNT
            and sweep["bound_matrix_digest_sha256"] == EXPECTED_FULL_BOUND_DIGEST
            and sweep["coefficient_matrix_record_count"] == 643
            and sweep["coefficient_matrix_digest_sha256"] == EXPECTED_FULL_COEFFICIENT_DIGEST
            and sweep["classification_matrix_record_count"] == 1_464
            and sweep["classification_matrix_digest_sha256"] == EXPECTED_FULL_CLASSIFICATION_DIGEST
        ),
        "aggregate_fifty_five_local_and_full_records_agree": bool(
            tuple(obstruction["selected_type_counts"]) == EXPECTED_OBSTRUCTION_COUNTS
            and obstruction["distinct_relation_counts"]
            == aggregate_fifty_five["distinct_relation_counts"]
            == EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS
            and obstruction["weighted_relation_counts"]
            == aggregate_fifty_five["weighted_relation_counts"]
            == EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS
            and sweep["first_unresolved_witness"] is None
        ),
        "registered_global_positive_minimum_reproduces": _minimum_witness_matches(minimum),
        "old_modulus_and_full_overlap_inventory_cover_degree_sixteen": bool(
            raw["q011am_hybrid_input_audit"]["old_modulus_separated_aggregate_count"]
            == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and raw["all_component_safe_intervals_are_contained_in_q011ak"]
            and EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            + sweep["fully_separated_overlap_aggregate_count"]
            == EXPECTED_DEGREE_AGGREGATE_COUNT
        ),
    }
    return {
        **sweep,
        "degree_sixteen_bridge": {
            "old_modulus_separated_aggregate_count": (EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT),
            "directly_separated_overlap_inventory_aggregate_count": (
                sweep["fully_separated_overlap_aggregate_count"]
            ),
            "degree_sixteen_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
            "remaining_degree_sixteen_aggregate_count": 0,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "row_digest_sha256": cycle["row_digest_sha256"],
        "envelope_digest_sha256": cycle["envelope_digest_sha256"],
        "sweep_digest_sha256": cycle["sweep_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_active_block_component_safe_audit() -> dict[str, Any]:
    raw = run_q011an_pilot(full_sweep=True)
    registered = _registered_parameters()
    rows = _active_block_structured_row_audit(raw)
    envelope = _component_safe_envelope_audit(raw)
    aggregate_fifty_five = _aggregate_fifty_five_audit(raw)
    full_sweep = _full_degree_sixteen_sweep_audit(raw, aggregate_fifty_five)
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": raw["sealed_input_audit"],
        "q011am_hybrid_input_audit": raw["q011am_hybrid_input_audit"],
    }
    row_sections = {"active_block_structured_row_audit": rows}
    envelope_sections = {"component_safe_envelope_audit": envelope}
    sweep_sections = {
        "aggregate_fifty_five_clearance_audit": aggregate_fifty_five,
        "full_component_safe_degree_sixteen_sweep_audit": full_sweep,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    row_digest = q011b._canonical_json_sha256(row_sections)
    envelope_digest = q011b._canonical_json_sha256(envelope_sections)
    sweep_digest = q011b._canonical_json_sha256(sweep_sections)

    validity_gates = {
        "q011am_and_all_prior_proof_objects_are_sealed": {
            "passed": raw["sealed_input_audit"]["passed"],
            "threshold": "18 artifacts and 93 direct digests reproduce",
            "value": raw["sealed_input_audit"]["checks"],
        },
        "representative_exact_families_and_q011k_proof_inputs_reproduce": {
            "passed": bool(
                rows["checks"]["q011k_root_spectral_and_proof_inputs_reconstruct"]
                and rows["checks"][
                    "two_representative_exact_families_and_conjugate_transports_reproduce"
                ]
            ),
            "threshold": "block 1/4 exact families, proposals and transports reproduce",
            "value": {
                "inputs": rows["checks"]["q011k_root_spectral_and_proof_inputs_reconstruct"],
                "families": rows["checks"][
                    "two_representative_exact_families_and_conjugate_transports_reproduce"
                ],
            },
        },
        "dual_precision_structured_row_protocols_reproduce": {
            "passed": rows["checks"]["dual_precision_structured_row_protocols_reproduce"],
            "threshold": "256/384-bit row records and strict replay containment reproduce",
            "value": rows["checks"]["dual_precision_structured_row_protocols_reproduce"],
        },
        "active_gershgorin_components_reproduce": {
            "passed": rows["checks"][
                "active_gershgorin_components_are_isolated_with_exact_multiplicity"
            ],
            "threshold": "active components are isolated with positive external gaps",
            "value": rows["checks"][
                "active_gershgorin_components_are_isolated_with_exact_multiplicity"
            ],
        },
        "component_safe_envelope_and_containment_chain_reproduce": {
            "passed": envelope["passed"],
            "threshold": "24 active, 6 relabel and 174 unchanged intervals reproduce",
            "value": envelope["checks"],
        },
        "aggregate_fifty_five_clearance_reproduces": {
            "passed": aggregate_fifty_five["passed"],
            "threshold": "37440 distinct comparisons separate with a positive minimum",
            "value": aggregate_fifty_five["checks"],
        },
        "all_one_hundred_fifty_four_component_safe_aggregates_reproduce": {
            "passed": full_sweep["passed"],
            "threshold": "all 154 aggregates and 969-degree bridge comparisons separate",
            "value": full_sweep["checks"],
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(
                    len(digest) == 64
                    for digest in (
                        input_digest,
                        row_digest,
                        envelope_digest,
                        sweep_digest,
                    )
                )
                and runner["filename"] == "q011an_active_block_structured_rows.py"
            ),
            "threshold": "strict finite JSON, four section digests and runner metadata",
            "value": {
                "input": input_digest,
                "row": row_digest,
                "envelope": envelope_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    minimum = full_sweep["global_minimum_separated_witness"]
    hypothesis_gates = {
        "structured_row_formula_encloses_the_representative_families": {
            "passed": bool(validity_passed and rows["passed"]),
            "threshold": "both transformed-matrix row families have rigorous radii",
            "value": rows["passed"],
        },
        "active_components_cover_exactly_twenty_four_eigenvalues": {
            "passed": bool(
                validity_passed
                and rows["active_identifier_count"] == EXPECTED_ACTIVE_IDENTIFIER_COUNT
                and rows["checks"][
                    "active_gershgorin_components_are_isolated_with_exact_multiplicity"
                ]
            ),
            "threshold": "isolated component disc counts sum to 24",
            "value": rows["active_identifier_count"],
        },
        "component_hulls_preserve_conjugacy_classes_and_parent_containment": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": "all 204 intervals are label-safe and Q011ak-contained",
            "value": envelope["checks"],
        },
        "aggregate_fifty_five_is_fully_separated": {
            "passed": bool(
                validity_passed
                and aggregate_fifty_five["distinct_relation_counts"]["overlap"] == 0
                and aggregate_fifty_five["weighted_relation_counts"]["overlap"] == 0
            ),
            "threshold": "all 37440 distinct and 602720 weighted comparisons separate",
            "value": {
                "distinct": aggregate_fifty_five["distinct_relation_counts"],
                "weighted": aggregate_fifty_five["weighted_relation_counts"],
            },
        },
        "all_nine_hundred_sixty_nine_degree_sixteen_aggregates_are_separated": {
            "passed": bool(
                validity_passed
                and full_sweep["remaining_overlap_aggregate_count"] == 0
                and full_sweep["degree_sixteen_bridge"]["degree_sixteen_aggregate_count"]
                == EXPECTED_DEGREE_AGGREGATE_COUNT
            ),
            "threshold": "815 old plus 154 direct-safe aggregates all separate",
            "value": full_sweep["degree_sixteen_bridge"],
        },
        "registered_global_minimum_is_strictly_positive": {
            "passed": bool(
                validity_passed
                and minimum["outward_gap_lower"]["float"] > 0
                and q011z._fraction(minimum["exact_gap"]) > 0
            ),
            "threshold": "outward and exact gaps are both strictly positive",
            "value": {
                "outward_gap_hex": minimum["outward_gap_lower"]["binary64_hex"],
                "exact_gap_hex": minimum["exact_gap_hex"],
            },
        },
        "claim_is_limited_to_degree_sixteen_external_nonresonance": {
            "passed": validity_passed,
            "threshold": "no degree 17--90, all-order, SSM or basin extrapolation",
            "value": "registered claim boundary only",
        },
    }
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    accepted = bool(validity_passed and hypothesis_passed)
    cycle = {
        "question": (
            "Does the component-label-safe conjugacy-closed active-block refinement "
            "certify every degree-sixteen external nonresonance comparison?"
        ),
        **input_sections,
        **row_sections,
        **envelope_sections,
        **sweep_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "row_digest_sha256": row_digest,
        "envelope_digest_sha256": envelope_digest,
        "sweep_digest_sha256": sweep_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": "accepted" if accepted else "inconclusive",
        "actual_resonance_outcome": (ACTUAL_RESONANCE_OUTCOME if accepted else "inconclusive"),
        "scientific_classification": (
            ACCEPTED_CLASSIFICATION if accepted else INCONCLUSIVE_CLASSIFICATION
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "component_label_safe_eigendisc_inclusion_is_certified": accepted,
        "active_block_eigenvalues_are_covered_with_exact_component_multiplicity": accepted,
        "q011al_block_zero_row_discs_are_relabelled_by_safe_component_hulls": accepted,
        "old_modulus_separated_aggregate_count": (
            EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT if accepted else 0
        ),
        "directly_separated_overlap_inventory_aggregate_count": (
            EXPECTED_OVERLAP_INVENTORY_AGGREGATE_COUNT if accepted else 0
        ),
        "degree_sixteen_external_nonresonance_is_certified": accepted,
        "an_actual_degree_sixteen_external_resonance_is_ruled_out": accepted,
        "certified_external_nonresonance_degrees": (
            list(range(2, 17)) if accepted else list(range(2, 16))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(17 if accepted else 16, 91)),
        "degrees_17_through_90_are_certified": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011am_recorded_six_source_rejection_is_rewritten": False,
        "q011an_closes_the_degree_sixteen_open_status": accepted,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only degree-sixteen external spectral relations for "
        "the fixed 17x17 repaired exact map on one fixed conservation leaf, the six "
        "Q011al block-zero row discs relabelled by their three common component hulls, "
        "the conjugacy-closed 24-identifier active-block component-hull refinement, "
        "independent source-disc choices with repetition, every target disc, exact "
        "x-Fourier multiplicities and the registered hierarchical outward-dyadic product "
        "protocol. It rules out an actual external resonance only within those "
        "registered degree-sixteen relations. It establishes no result for degrees 17 "
        "through 90, all-order nonresonance, higher graph smoothness, SSM existence or "
        "uniqueness, normal attraction, basin, other grid, force, wall or D3Q27 case."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ai_certificates_and_diagnostics_changed": False,
        "q011aj_and_q011ak_recorded_rejections_changed": False,
        "q011al_recorded_obstruction_clearance_changed": False,
        "q011am_recorded_six_source_rejection_changed": False,
    }
    if accepted:
        cycle["next_change"] = (
            "Preregister Q011ao only after a design-only degree-seventeen resource "
            "estimate confirms that the hierarchical exact-multiplicity sweep is feasible."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first seal, exact-family, row, component, envelope, "
            "aggregate, full-sweep or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011an cycle failed strict serialization or digest")
    return cycle


def run_q011an_study() -> dict[str, Any]:
    cycle = run_active_block_component_safe_audit()
    sweep = cycle["full_component_safe_degree_sixteen_sweep_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "row_enclosure_type": "MPFR RoundUp structured transformed-matrix rows",
            "primary_precision_bits": PRIMARY_PRECISION_BITS,
            "replay_precision_bits": REPLAY_PRECISION_BITS,
            "product_enclosure_type": "outward-rounded IEEE-754 binary64 interval products",
            "fourier_convolution_type": (
                "exact numpy.int64 17x17 cyclic convolution with checked bounds"
            ),
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "convolution_call_count": sweep["convolution_call_count"],
            "weighted_comparison_count": sweep["weighted_comparison_count"],
            "distinct_comparison_count": sweep["distinct_comparison_count"],
        },
        "mathematical_scope": {
            "diagnostic": "component-label-safe degree-16 external nonresonance certificate",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "active_block_identifier_count": EXPECTED_ACTIVE_IDENTIFIER_COUNT,
            "q011al_component_relabel_identifier_count": (EXPECTED_Q011AL_RELABEL_IDENTIFIER_COUNT),
            "audited_overlap_inventory_aggregate_count": (
                EXPECTED_OVERLAP_INVENTORY_AGGREGATE_COUNT
            ),
            "degree_sixteen_external_nonresonance_claim": True,
            "actual_degree_sixteen_external_resonance_ruled_out_claim": True,
            "degrees_17_through_90_claim": False,
            "all_order_nonresonance_claim": False,
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
    result = run_q011an_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
