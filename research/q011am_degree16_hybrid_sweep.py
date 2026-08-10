"""Q011am full degree-sixteen six-source hybrid-envelope audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from itertools import product
from math import comb, inf
from math import prod as integer_product
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

import research.q011al_block_zero_structured_rows as q011al
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ak = q011al.q011ak
q011ag = q011al.q011ag
q011af = q011al.q011af
q011b = q011al.q011b
q011z = q011al.q011z

SIZE = 17
DEGREE = 16
EXPECTED_OVERLAP_AGGREGATE_COUNT = 154
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 815
EXPECTED_DEGREE_AGGREGATE_COUNT = 969
EXPECTED_OBSTRUCTION_AGGREGATE_INDEX = 55
EXPECTED_FULLY_SEPARATED_AGGREGATE_COUNT = 153
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 7_593_735_887
EXPECTED_MODULUS_SIGNATURE_COUNT = 27_206_049
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 23_173_623
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 1_649_206_077
EXPECTED_WEIGHTED_COMPARISON_COUNT = 3_521_974_412
EXPECTED_DISTINCT_COMPARISON_COUNT = 136_891_880
EXPECTED_WEIGHTED_RELATIONS = {
    "overlap": 388_480,
    "product_below_target": 1_901_447_368,
    "target_below_product": 1_620_138_564,
}
EXPECTED_DISTINCT_RELATIONS = {
    "overlap": 24_960,
    "product_below_target": 72_313_776,
    "target_below_product": 64_553_144,
}
EXPECTED_CLASS_POWER_COUNT = 228
EXPECTED_CLASS_POWER_DIGEST = "20865e41cb0341d21ee6bb9eaba49bf4565dd44a34a9ed6ebbf14624efc3c2ce"
EXPECTED_GROUP_SIGNATURE_COUNT = 77_927
EXPECTED_GROUP_SIGNATURE_DIGEST = "ceee86d86e7250a806b296673f282b0c596d3b56db83f0a585efe70d8f2abe26"
EXPECTED_PAIR_POOL_COUNT = 85
EXPECTED_PAIR_POOL_DIGEST = "af927b867976521fd1827e509821bc03a399d52f8fce3f32642b1ebccea8773c"
EXPECTED_AGGREGATE_DIGEST = "295f5eb4a8e3d794d09bef8d552f92bca6b96a3db51749b51b355c05f1e40415"
EXPECTED_BOUND_MATRIX_COUNT = 154
EXPECTED_BOUND_MATRIX_DIGEST = "2d1b0ce829e42f87b96793d0f1a4208be1cb2a8215989b4d5485873725b544a6"
EXPECTED_COEFFICIENT_MATRIX_COUNT = 643
EXPECTED_COEFFICIENT_MATRIX_DIGEST = (
    "ea542f6e28fef27ed8da24bcb02af28eab59190dac4ba41c40bf8a8c7682edd9"
)
EXPECTED_CLASSIFICATION_MATRIX_COUNT = 1_464
EXPECTED_CLASSIFICATION_MATRIX_DIGEST = (
    "db97ba016821788462c728153a7603272a8d97cc0c45f88582ca13a360b12fba"
)
EXPECTED_CONVOLUTION_CALL_COUNT = 973_967
EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND = 1_734
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 900_900
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 1_142
EXPECTED_MAXIMUM_FOURIER_CRUDE_BOUND = 8_330

EXPECTED_OBSTRUCTION_COUNTS = (3, 12, 0, 1)
EXPECTED_OBSTRUCTION_TARGET_COUNT = 24
EXPECTED_OBSTRUCTION_SIGNATURE_COUNT = 1_560
EXPECTED_OBSTRUCTION_COMPATIBLE_MONOMIAL_COUNT = 204_240
EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT = 602_720
EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT = 37_440
EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS = {
    "overlap": 388_480,
    "product_below_target": 0,
    "target_below_product": 214_240,
}
EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS = {
    "overlap": 24_960,
    "product_below_target": 0,
    "target_below_product": 12_480,
}
EXPECTED_OBSTRUCTION_RECORD_DIGEST = (
    "6cdad15994824c17bca2ad7a33c133e3565b6b09c33090d601f4d1e922ba4ea8"
)
EXPECTED_FIRST_UNRESOLVED_COUNTS = (
    (0, 0, 0, 3),
    (0, 12),
    (0, 0, 0),
    (0, 0, 0, 0, 0, 1),
)
EXPECTED_FIRST_UNRESOLVED_SOURCES = (
    "block=16;center=145",
    "block=16;center=145",
    "block=16;center=145",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=149",
)
EXPECTED_FIRST_INTERSECTION_WIDTH_HEX = "0x1.cec36b55f92c1p-26"
EXPECTED_FIRST_CENTER_GAP_HEX = "0x1.4739f17e09ca8p-29"
EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST = (
    "f73644b63995be065528cd9a16ea1044036491d3f3a23ae61f233058b3f58576"
)
EXPECTED_GLOBAL_MINIMUM_GAP_HEX = "0x1.2de9e89ffffffp-26"
EXPECTED_GLOBAL_EXACT_GAP_HEX = "0x1.2de9f1c1d911ep-26"
EXPECTED_GLOBAL_WITNESS_DIGEST = "8e3dfea54c4a6b486a05a58e48ceb1fccbf48197a6e96ca3d91cdcb39fcabc9f"

REJECTED_CLASSIFICATION = (
    "the six-source hybrid degree-16 certificate is rejected at the sole "
    "remaining overlap aggregate 55"
)
INCONCLUSIVE_CLASSIFICATION = "the full degree-16 six-source hybrid-envelope audit is inconclusive"

Q011AL_ARTIFACT_SHA256 = "b0fe7be52da885e28b9e29d580a187d232ef6fe4c233be2db3cf7a18974420dc"
Q011AL_RUNNER_SHA256 = "72211072fdc657ba1931dda983b167d2ac44a8f71e18aa016b22ea3f7a7cedf2"
Q011AL_DIGEST_NAMES = (
    "input_digest_sha256",
    "family_digest_sha256",
    "row_digest_sha256",
    "clearance_digest_sha256",
    "result_digest_sha256",
)
Q011AL_DIGESTS = (
    "97bfc790c2a761d63678b3396e2f1f6ba1b28be1605d0e0b9dae6b63f2f57a93",
    "79f442ff7bbb874c79f7692b58f3986a34a6df0f0ee9ffc618fa21608ef6e41c",
    "6d4a96cb71535048f34e6a3e1cb9c1afe895cc87558bb98cb791288336aa5816",
    "708e866d675f2328cca388191c35062f1dd0f7dbee46aa7355976bb31461db31",
    "9befdd9e0b81914e1f18c7b7aff772471b17d1454d81725f44d3736625f8c7c1",
)


@dataclass(frozen=True)
class _PowerRecord:
    wave: npt.NDArray[np.int64]
    bounds: tuple[np.float64, np.float64, np.float64, np.float64]
    exact: tuple[Fraction, Fraction, Fraction]
    fiber_multiplicity: int


@dataclass(frozen=True)
class _GroupRecord:
    class_counts: tuple[int, ...]
    wave: npt.NDArray[np.int64]
    bounds: tuple[np.float64, np.float64, np.float64, np.float64]
    fiber_multiplicity: int


class _ConvolutionLedger:
    def __init__(self) -> None:
        indices = np.arange(SIZE)
        self.indices = (indices[:, None] - indices[None, :]) % SIZE
        self.maximum_crude_bound = 0
        self.call_count = 0
        self.all_nonnegative = True
        self.all_fiber_sums_exact = True

    def convolve(
        self,
        left: npt.NDArray[np.int64],
        right: npt.NDArray[np.int64],
        *,
        expected_sum: int,
    ) -> npt.NDArray[np.int64]:
        crude = SIZE * int(left.max(initial=0)) * int(right.max(initial=0))
        if crude > np.iinfo(np.int64).max:
            raise OverflowError("Q011am int64 convolution bound failed")
        result = right[self.indices] @ left
        nonnegative = bool(np.all(result >= 0))
        exact_sum = int(result.sum()) == expected_sum
        self.maximum_crude_bound = max(self.maximum_crude_bound, crude)
        self.call_count += 1
        self.all_nonnegative = self.all_nonnegative and nonnegative
        self.all_fiber_sums_exact = self.all_fiber_sums_exact and exact_sum
        if not nonnegative or not exact_sum:
            raise RuntimeError("Q011am exact cyclic convolution invariant failed")
        return result


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
    prior, artifacts = q011al._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011al_block_zero_structured_rows.json"
    runner_path = Path(q011al.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AL_DIGEST_NAMES)
    checks = {
        "q011al_sixteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"] and prior["direct_digest_count"] == 83 and all(prior["checks"].values())
        ),
        "q011al_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011AL_ARTIFACT_SHA256),
        "q011al_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AL_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AL_RUNNER_SHA256
        ),
        "q011al_digests_match": digests == Q011AL_DIGESTS,
        "q011al_registered_clearance_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["scientific_classification"] == q011al.ACCEPTED_CLASSIFICATION
            and cycle["theorem_consequence"]["registered_degree_sixteen_obstruction_is_cleared"]
            and not cycle["theorem_consequence"][
                "degree_sixteen_external_nonresonance_is_certified"
            ]
        ),
        "q011al_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011al_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011al_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "eighty_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 88
        ),
    }
    artifacts["q011al"] = artifact
    return (
        {
            "prior_q011al_sealed_input_audit": prior,
            "q011al": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AL_DIGEST_NAMES),
                "digests": list(digests),
                "scientific_classification": cycle["scientific_classification"],
            },
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _hybrid_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[tuple[tuple[str, ...], ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[str, ...], ...],
]:
    al_cycle = artifacts["q011al"]["cycle"]
    ak_cycle = artifacts["q011ak"]["cycle"]
    aj_cycle = artifacts["q011aj"]["cycle"]
    hybrid = al_cycle["hybrid_selected_block_zero_envelope_audit"]
    blockwise = ak_cycle["blockwise_transformed_residual_envelope_audit"]
    inventory = aj_cycle["degree16_modulus_inventory_audit"]
    hybrid_records = hybrid["hybrid_disc_records"]
    blockwise_records = {
        record["identifier"]: record for record in blockwise["blockwise_disc_records"]
    }
    lookup: dict[str, q011z._UniformDisc] = {}
    containment = True
    for record in hybrid_records:
        identifier = record["identifier"]
        base = blockwise_records[identifier]
        center = RationalInterval(
            q011z._fraction(base["center_modulus_lower"]),
            q011z._fraction(base["center_modulus_upper"]),
        )
        modulus = RationalInterval(
            q011z._fraction(record["hybrid_modulus_lower"]),
            q011z._fraction(record["hybrid_modulus_upper"]),
        )
        base_modulus = RationalInterval(
            q011z._fraction(base["blockwise_modulus_lower"]),
            q011z._fraction(base["blockwise_modulus_upper"]),
        )
        containment = bool(
            containment
            and modulus.lower >= base_modulus.lower
            and modulus.upper <= base_modulus.upper
        )
        lookup[identifier] = q011z._UniformDisc(
            identifier=identifier,
            block_index=record["block_index"],
            center_index=record["center_index"],
            center_modulus=center,
            modulus=modulus,
        )
    selected_groups = tuple(
        tuple(group) for group in inventory["selected_source_group_memberships"]
    )
    overlap_records = tuple(inventory["overlap_records"])
    overlap_counts = tuple(tuple(record["selected_type_counts"]) for record in overlap_records)
    external_indices = tuple(tuple(record["external_group_indices"]) for record in overlap_records)
    target_groups = tuple(
        tuple(record["identifiers"]) for record in inventory["external_target_groups"]
    )
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    hybrid_digest = q011b._canonical_json_sha256(hybrid_records)
    checks = {
        "q011al_hybrid_envelope_is_accepted_and_reconstructs": bool(
            hybrid["passed"]
            and hybrid_digest == q011al.EXPECTED_HYBRID_RECORD_DIGEST
            and len(hybrid_records) == len(lookup) == 204
        ),
        "hybrid_intervals_reconstruct_inside_q011ak_blockwise_intervals": containment,
        "selected_modulus_classes_and_membership_reproduce": bool(
            tuple(len(group) for group in classes) == q011al.EXPECTED_CLASS_COUNTS
            and class_digest == q011al.EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "degree_sixteen_overlap_inventory_reconstructs": bool(
            inventory["passed"]
            and len(overlap_counts)
            == len(external_indices)
            == len(target_groups)
            == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and inventory["old_modulus_separated_aggregate_count"]
            == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and inventory["degree_modulus_aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
        ),
        "hybrid_inputs_are_finite_strict_json": bool(
            _all_numeric_values_finite(hybrid_records)
            and _strict_json_serializable(hybrid_records)
            and json.dumps(hybrid_records, allow_nan=False)
        ),
    }
    audit = {
        "hybrid_identifier_count": len(lookup),
        "hybrid_record_digest_sha256": hybrid_digest,
        "selected_modulus_class_counts": [len(group) for group in classes],
        "class_membership_digest_sha256": class_digest,
        "old_modulus_separated_aggregate_count": inventory["old_modulus_separated_aggregate_count"],
        "old_modulus_overlap_aggregate_count": inventory["old_modulus_overlap_aggregate_count"],
        "overlap_inventory_digest_sha256": inventory["exact_inventory_digest_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        lookup,
        classes,
        overlap_counts,
        external_indices,
        target_groups,
    )


def _combine_bounds(
    left: tuple[np.float64, np.float64, np.float64, np.float64],
    right: tuple[np.float64, np.float64, np.float64, np.float64],
) -> tuple[np.float64, np.float64, np.float64, np.float64]:
    return (
        q011ag._down_multiply(left[0], right[0]),
        q011ag._down_multiply(left[1], right[1]),
        q011ag._up_multiply(left[2], right[2]),
        q011ag._up_multiply(left[3], right[3]),
    )


class _HierarchicalPools:
    def __init__(
        self,
        classes: tuple[tuple[tuple[str, ...], ...], ...],
        lookup: dict[str, q011z._UniformDisc],
    ) -> None:
        self.classes = classes
        self.lookup = lookup
        self.ledger = _ConvolutionLedger()
        self.power_cache: dict[tuple[int, int, int], _PowerRecord] = {}
        self.group_cache: dict[tuple[int, int], tuple[_GroupRecord, ...]] = {}
        self.pair_cache: dict[tuple[int, int, int, int], tuple[q011ag._PairSignature, ...]] = {}

    def _power(self, group_index: int, class_index: int, count: int) -> _PowerRecord:
        key = (group_index, class_index, count)
        if key in self.power_cache:
            return self.power_cache[key]
        identifiers = self.classes[group_index][class_index]
        wave = np.zeros(SIZE, dtype=np.int64)
        for allocation in q011af._weak_compositions(count, len(identifiers)):
            output_wave = (
                sum(
                    multiplicity * q011z._identifier_indices(identifier)[0]
                    for multiplicity, identifier in zip(allocation, identifiers, strict=True)
                )
                % SIZE
            )
            wave[output_wave] += 1
        disc = self.lookup[identifiers[0]]
        factors = (
            q011ag._fraction_lower(disc.center_modulus.lower),
            q011ag._fraction_lower(disc.center_modulus.upper),
            q011ag._fraction_upper(disc.center_modulus.upper),
            q011ag._fraction_upper(disc.modulus.upper),
        )
        bounds = [np.float64(1.0)] * 4
        for _ in range(count):
            bounds[0] = q011ag._down_multiply(bounds[0], factors[0])
            bounds[1] = q011ag._down_multiply(bounds[1], factors[1])
            bounds[2] = q011ag._up_multiply(bounds[2], factors[2])
            bounds[3] = q011ag._up_multiply(bounds[3], factors[3])
        exact = (
            disc.center_modulus.lower**count,
            disc.center_modulus.upper**count,
            disc.modulus.upper**count,
        )
        fiber = comb(count + len(identifiers) - 1, len(identifiers) - 1)
        if not (
            Fraction.from_float(float(bounds[0])) <= exact[0]
            and Fraction.from_float(float(bounds[1])) <= exact[1]
            and Fraction.from_float(float(bounds[2])) >= exact[1]
            and Fraction.from_float(float(bounds[3])) >= exact[2]
            and int(wave.sum()) == fiber
            and np.all(wave >= 0)
        ):
            raise RuntimeError("Q011am class-power containment failed")
        record = _PowerRecord(
            wave=wave,
            bounds=(bounds[0], bounds[1], bounds[2], bounds[3]),
            exact=exact,
            fiber_multiplicity=fiber,
        )
        self.power_cache[key] = record
        return record

    def group_pool(self, group_index: int, source_count: int) -> tuple[_GroupRecord, ...]:
        key = (group_index, source_count)
        if key in self.group_cache:
            return self.group_cache[key]
        records = []
        for class_counts in q011af._weak_compositions(source_count, len(self.classes[group_index])):
            wave = np.zeros(SIZE, dtype=np.int64)
            wave[0] = 1
            fiber = 1
            bounds = (
                np.float64(1.0),
                np.float64(1.0),
                np.float64(1.0),
                np.float64(1.0),
            )
            for class_index, count in enumerate(class_counts):
                power_record = self._power(group_index, class_index, count)
                wave = self.ledger.convolve(
                    wave,
                    power_record.wave,
                    expected_sum=fiber * power_record.fiber_multiplicity,
                )
                fiber *= power_record.fiber_multiplicity
                if count:
                    bounds = _combine_bounds(bounds, power_record.bounds)
            records.append(
                _GroupRecord(
                    class_counts=class_counts,
                    wave=wave,
                    bounds=bounds,
                    fiber_multiplicity=fiber,
                )
            )
        self.group_cache[key] = tuple(records)
        return self.group_cache[key]

    def pair_pool(
        self,
        left_group: int,
        left_count: int,
        right_group: int,
        right_count: int,
    ) -> tuple[q011ag._PairSignature, ...]:
        key = (left_group, left_count, right_group, right_count)
        if key in self.pair_cache:
            return self.pair_cache[key]
        records = []
        for left, right in product(
            self.group_pool(left_group, left_count),
            self.group_pool(right_group, right_count),
        ):
            wave = self.ledger.convolve(
                left.wave,
                right.wave,
                expected_sum=left.fiber_multiplicity * right.fiber_multiplicity,
            )
            bounds = _combine_bounds(left.bounds, right.bounds)
            records.append(
                q011ag._PairSignature(
                    class_counts=(left.class_counts, right.class_counts),
                    wave=wave,
                    bounds=bounds,
                    fiber_multiplicity=int(wave.sum()),
                )
            )
        self.pair_cache[key] = tuple(records)
        return self.pair_cache[key]

    def power_records(self) -> list[dict[str, Any]]:
        records = []
        for (group_index, class_index, count), power_record in sorted(self.power_cache.items()):
            records.append(
                {
                    "selected_group_index": group_index,
                    "modulus_class_index": class_index,
                    "source_count": count,
                    "identifiers": list(self.classes[group_index][class_index]),
                    "wave_coefficients": [int(value) for value in power_record.wave],
                    "fiber_multiplicity": power_record.fiber_multiplicity,
                    "bounds_hex": [float(value).hex() for value in power_record.bounds],
                    "exact_center_lower": q011z._exact_fraction_record(power_record.exact[0]),
                    "exact_center_upper": q011z._exact_fraction_record(power_record.exact[1]),
                    "exact_full_upper": q011z._exact_fraction_record(power_record.exact[2]),
                }
            )
        return records

    def factorization_digest(self) -> tuple[int, str, list[dict[str, Any]]]:
        stream = q011al._FramedRecordDigest("Q011am hierarchical group signatures v1")
        for (group_index, source_count), records in sorted(self.group_cache.items()):
            for record_index, record in enumerate(records):
                stream.update(
                    {
                        "selected_group_index": group_index,
                        "source_count": source_count,
                        "group_signature_index": record_index,
                        "class_counts": list(record.class_counts),
                        "wave_coefficients": [int(value) for value in record.wave],
                        "fiber_multiplicity": record.fiber_multiplicity,
                        "bounds_hex": [float(value).hex() for value in record.bounds],
                    }
                )
        pair_records = [
            {
                "left_group": key[0],
                "left_count": key[1],
                "right_group": key[2],
                "right_count": key[3],
                "pair_signature_count": len(records),
            }
            for key, records in sorted(self.pair_cache.items())
        ]
        return stream.count, stream.hexdigest(), pair_records


def _float_record(value: float) -> dict[str, Any]:
    return {"float": value, "binary64_hex": value.hex()}


def _relation_counts(counter: Counter[str], suffix: str) -> dict[str, int]:
    return {
        relation: counter[f"{relation}_{suffix}"]
        for relation in ("overlap", "product_below_target", "target_below_product")
    }


def _exact_witness(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    raw: dict[str, Any],
) -> dict[str, Any]:
    class_counts = tuple(tuple(group) for group in raw["class_counts"])
    sources = q011af._source_witness_for_signature(classes, class_counts, raw["output_block"])
    product_interval, center_interval = q011ak._exact_blockwise_product_interval(
        classes, lookup, class_counts
    )
    target_disc = lookup[raw["target_identifier"]]
    witness = {
        "aggregate_index": raw["aggregate_index"],
        "selected_type_counts": list(raw["selected_type_counts"]),
        "target_identifier": raw["target_identifier"],
        "output_block": raw["output_block"],
        "left_index": raw["left_index"],
        "right_index": raw["right_index"],
        "wave_multiplicity": raw["wave_multiplicity"],
        "relation": raw["relation"],
        "block_zero_multiplicity": q011ak._block_zero_multiplicity(classes, class_counts),
        "class_counts": [list(group) for group in class_counts],
        "source_identifiers": list(sources),
        "hybrid_product_interval": {
            "lower": q011z._exact_fraction_record(product_interval.lower),
            "upper": q011z._exact_fraction_record(product_interval.upper),
        },
        "hybrid_target_interval": {
            "lower": q011z._exact_fraction_record(target_disc.modulus.lower),
            "upper": q011z._exact_fraction_record(target_disc.modulus.upper),
        },
        "center_product_interval": {
            "lower": q011z._exact_fraction_record(center_interval.lower),
            "upper": q011z._exact_fraction_record(center_interval.upper),
        },
        "center_target_interval": {
            "lower": q011z._exact_fraction_record(target_disc.center_modulus.lower),
            "upper": q011z._exact_fraction_record(target_disc.center_modulus.upper),
        },
    }
    if raw["relation"] == "overlap":
        intersection = RationalInterval(
            max(product_interval.lower, target_disc.modulus.lower),
            min(product_interval.upper, target_disc.modulus.upper),
        )
        witness["intersection_interval"] = {
            "lower": q011z._exact_fraction_record(intersection.lower),
            "upper": q011z._exact_fraction_record(intersection.upper),
            "width": q011z._exact_fraction_record(intersection.upper - intersection.lower),
            "width_hex": float(intersection.upper - intersection.lower).hex(),
        }
        if center_interval.upper < target_disc.center_modulus.lower:
            center_relation = "product_below_target"
            center_gap = target_disc.center_modulus.lower - center_interval.upper
        elif target_disc.center_modulus.upper < center_interval.lower:
            center_relation = "target_below_product"
            center_gap = center_interval.lower - target_disc.center_modulus.upper
        else:
            center_relation = "overlap"
            center_gap = Fraction(0)
        witness["center_only_diagnostic"] = {
            "relation": center_relation,
            "gap": q011z._exact_fraction_record(center_gap),
            "gap_hex": float(center_gap).hex(),
        }
    else:
        exact_gap = (
            target_disc.modulus.lower - product_interval.upper
            if raw["relation"] == "product_below_target"
            else product_interval.lower - target_disc.modulus.upper
        )
        witness["outward_gap_lower"] = _float_record(raw["outward_gap"])
        witness["exact_gap"] = q011z._exact_fraction_record(exact_gap)
        witness["exact_gap_hex"] = float(exact_gap).hex()
    witness["witness_digest_sha256"] = q011b._canonical_json_sha256(witness)
    return witness


def _hierarchical_sweep_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_indices: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    pools = _HierarchicalPools(classes, lookup)
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
            raise RuntimeError("Q011am aggregate has no separated comparison")
        if aggregate_first_overlap is not None:
            unresolved_key = (aggregate_index, *aggregate_first_overlap[0])
            if first_unresolved is None or unresolved_key < first_unresolved[0]:
                first_unresolved = (unresolved_key, aggregate_first_overlap[1])
        minimum_key = (aggregate_minimum[0][0], aggregate_index, *aggregate_minimum[0][1:])
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
        weighted_relations = _relation_counts(aggregate_relations, "weighted")
        distinct_relations = _relation_counts(aggregate_relations, "distinct")
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
                "minimum_certified_gap_lower": _float_record(aggregate_minimum[0][0]),
                "minimum_witness": {
                    key: value
                    for key, value in aggregate_minimum[1].items()
                    if key != "outward_gap"
                },
            }
        )
    if first_unresolved is None or global_minimum is None:
        raise RuntimeError("Q011am did not reproduce both registered outcomes")

    power_records = pools.power_records()
    group_record_count, factor_digest, pair_records = pools.factorization_digest()
    first_witness = _exact_witness(classes, lookup, first_unresolved[1])
    minimum_witness = _exact_witness(classes, lookup, global_minimum[1])
    aggregate_digest = q011b._canonical_json_sha256(aggregate_records)
    power_digest = q011b._canonical_json_sha256(power_records)
    pair_digest = q011b._canonical_json_sha256(pair_records)
    bound_digest = q011b._canonical_json_sha256(bound_records)
    coefficient_digest = q011b._canonical_json_sha256(coefficient_records)
    classification_digest = q011b._canonical_json_sha256(classification_records)
    fully_separated = sum(
        record["distinct_relation_counts"]["overlap"] == 0 for record in aggregate_records
    )
    overlap_indices = [
        record["aggregate_index"]
        for record in aggregate_records
        if record["distinct_relation_counts"]["overlap"] > 0
    ]
    return {
        "degree": DEGREE,
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
        "weighted_relation_counts": _relation_counts(total_relations, "weighted"),
        "distinct_relation_counts": _relation_counts(total_relations, "distinct"),
        "aggregate_records": aggregate_records,
        "aggregate_record_digest_sha256": aggregate_digest,
        "class_power_record_count": len(power_records),
        "class_power_record_digest_sha256": power_digest,
        "group_signature_record_count": group_record_count,
        "group_signature_digest_sha256": factor_digest,
        "pair_pool_record_count": len(pair_records),
        "pair_pool_record_digest_sha256": pair_digest,
        "bound_matrix_record_count": len(bound_records),
        "bound_matrix_digest_sha256": bound_digest,
        "coefficient_matrix_record_count": len(coefficient_records),
        "coefficient_matrix_digest_sha256": coefficient_digest,
        "classification_matrix_record_count": len(classification_records),
        "classification_matrix_digest_sha256": classification_digest,
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


def _prefix_and_q011al_bridge_audit(
    artifacts: dict[str, dict[str, Any]],
    sweep: dict[str, Any],
) -> dict[str, Any]:
    prefix = artifacts["q011aj"]["cycle"]["first_uniform_envelope_obstruction_audit"][
        "prefix_records"
    ]
    current = sweep["aggregate_records"]
    count_fields = (
        "selected_type_counts",
        "external_group_indices",
        "target_identifier_count",
        "modulus_signature_count",
        "compatible_modulus_signature_count",
        "compatible_original_monomial_count",
        "weighted_comparison_count",
        "distinct_comparison_count",
    )
    prefix_bridge_records = [
        {
            "aggregate_index": index,
            **{field: current[index][field] for field in count_fields},
        }
        for index in range(len(prefix))
    ]
    prefix_counts_match = all(
        all(current[index][field] == record[field] for field in count_fields)
        for index, record in enumerate(prefix)
    )

    clearance = artifacts["q011al"]["cycle"]["registered_obstruction_clearance_audit"][
        "clearance_record"
    ]
    registered = current[q011al.OBSTRUCTION_AGGREGATE_INDEX]
    current_witness = sweep["global_minimum_separated_witness"]
    stored_witness = clearance["minimum_outward_witness"]
    witness_fields = (
        "target_identifier",
        "output_block",
        "left_index",
        "right_index",
        "wave_multiplicity",
        "relation",
        "block_zero_multiplicity",
        "class_counts",
        "source_identifiers",
        "exact_gap_hex",
    )
    q011al_counts_match = all(
        registered[field] == clearance[field]
        for field in (
            "selected_type_counts",
            "modulus_signature_count",
            "weighted_comparison_count",
            "distinct_comparison_count",
            "weighted_relation_counts",
            "distinct_relation_counts",
        )
    )
    q011al_witness_matches = all(
        current_witness[field] == stored_witness[field] for field in witness_fields
    )
    current_outward = current_witness["outward_gap_lower"]["float"]
    stored_outward = float.fromhex(stored_witness["outward_gap_hex"])
    checks = {
        "q011aj_first_hundred_relation_independent_counts_reproduce": bool(
            len(prefix) == 100 and prefix_counts_match
        ),
        "q011al_index_ninety_nine_all_separated_counts_reproduce": bool(
            q011al_counts_match and registered["distinct_relation_counts"]["overlap"] == 0
        ),
        "q011al_global_exact_minimum_witness_reproduces": bool(
            q011al_witness_matches
            and 0 < current_outward <= stored_outward
            and current_witness["exact_gap_hex"] == EXPECTED_GLOBAL_EXACT_GAP_HEX
        ),
    }
    bridge_record = {
        "q011aj_prefix_record_count": len(prefix_bridge_records),
        "q011aj_prefix_bridge_digest_sha256": q011b._canonical_json_sha256(prefix_bridge_records),
        "q011al_registered_aggregate_index": q011al.OBSTRUCTION_AGGREGATE_INDEX,
        "q011al_hierarchical_outward_gap_hex": current_witness["outward_gap_lower"]["binary64_hex"],
        "q011al_original_outward_gap_hex": stored_witness["outward_gap_hex"],
        "q011al_exact_gap_hex": current_witness["exact_gap_hex"],
    }
    return {
        **bridge_record,
        "bridge_record_digest_sha256": q011b._canonical_json_sha256(bridge_record),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_sweep_checks(sweep: dict[str, Any]) -> dict[str, bool]:
    obstruction = sweep["aggregate_records"][EXPECTED_OBSTRUCTION_AGGREGATE_INDEX]
    first = sweep["first_unresolved_witness"]
    minimum = sweep["global_minimum_separated_witness"]
    first_digest = q011b._canonical_json_sha256(
        {key: value for key, value in first.items() if key != "witness_digest_sha256"}
    )
    minimum_digest = q011b._canonical_json_sha256(
        {key: value for key, value in minimum.items() if key != "witness_digest_sha256"}
    )
    return {
        "registered_resource_and_factorization_values_reproduce": bool(
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
            and sweep["maximum_convolution_crude_int64_bound"] < np.iinfo(np.int64).max
            and sweep["maximum_fourier_crude_int64_bound"] < np.iinfo(np.int64).max
        ),
        "registered_full_sweep_counts_reproduce": bool(
            sweep["audited_overlap_aggregate_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and sweep["compatible_modulus_signature_count"] == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and sweep["compatible_original_monomial_count"] == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and sweep["weighted_comparison_count"] == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and sweep["distinct_comparison_count"] == EXPECTED_DISTINCT_COMPARISON_COUNT
            and sweep["weighted_relation_counts"] == EXPECTED_WEIGHTED_RELATIONS
            and sweep["distinct_relation_counts"] == EXPECTED_DISTINCT_RELATIONS
        ),
        "registered_matrix_and_aggregate_digests_reproduce": bool(
            sweep["aggregate_record_digest_sha256"] == EXPECTED_AGGREGATE_DIGEST
            and sweep["bound_matrix_record_count"] == EXPECTED_BOUND_MATRIX_COUNT
            and sweep["bound_matrix_digest_sha256"] == EXPECTED_BOUND_MATRIX_DIGEST
            and sweep["coefficient_matrix_record_count"] == EXPECTED_COEFFICIENT_MATRIX_COUNT
            and sweep["coefficient_matrix_digest_sha256"] == EXPECTED_COEFFICIENT_MATRIX_DIGEST
            and sweep["classification_matrix_record_count"] == EXPECTED_CLASSIFICATION_MATRIX_COUNT
            and sweep["classification_matrix_digest_sha256"]
            == EXPECTED_CLASSIFICATION_MATRIX_DIGEST
        ),
        "sole_remaining_obstruction_record_reproduces": bool(
            sweep["fully_separated_overlap_aggregate_count"]
            == EXPECTED_FULLY_SEPARATED_AGGREGATE_COUNT
            and sweep["remaining_overlap_aggregate_count"] == 1
            and sweep["remaining_overlap_aggregate_indices"]
            == [EXPECTED_OBSTRUCTION_AGGREGATE_INDEX]
            and tuple(obstruction["selected_type_counts"]) == EXPECTED_OBSTRUCTION_COUNTS
            and obstruction["target_identifier_count"] == EXPECTED_OBSTRUCTION_TARGET_COUNT
            and obstruction["modulus_signature_count"] == EXPECTED_OBSTRUCTION_SIGNATURE_COUNT
            and obstruction["compatible_modulus_signature_count"]
            == EXPECTED_OBSTRUCTION_SIGNATURE_COUNT
            and obstruction["compatible_original_monomial_count"]
            == EXPECTED_OBSTRUCTION_COMPATIBLE_MONOMIAL_COUNT
            and obstruction["weighted_comparison_count"]
            == EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT
            and obstruction["distinct_comparison_count"]
            == EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT
            and obstruction["weighted_relation_counts"] == EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS
            and obstruction["distinct_relation_counts"] == EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS
            and q011b._canonical_json_sha256(obstruction) == EXPECTED_OBSTRUCTION_RECORD_DIGEST
        ),
        "registered_first_unresolved_exact_witness_reproduces": bool(
            first["aggregate_index"] == EXPECTED_OBSTRUCTION_AGGREGATE_INDEX
            and first["target_identifier"] == "block=13;center=114"
            and first["output_block"] == 13
            and first["left_index"] == first["right_index"] == 0
            and first["wave_multiplicity"] == 8
            and first["relation"] == "overlap"
            and first["block_zero_multiplicity"] == 0
            and tuple(tuple(group) for group in first["class_counts"])
            == EXPECTED_FIRST_UNRESOLVED_COUNTS
            and tuple(first["source_identifiers"]) == EXPECTED_FIRST_UNRESOLVED_SOURCES
            and first["intersection_interval"]["width_hex"] == EXPECTED_FIRST_INTERSECTION_WIDTH_HEX
            and q011z._fraction(first["intersection_interval"]["width"]) > 0
            and first["center_only_diagnostic"]["relation"] == "product_below_target"
            and first["center_only_diagnostic"]["gap_hex"] == EXPECTED_FIRST_CENTER_GAP_HEX
            and q011z._fraction(first["center_only_diagnostic"]["gap"]) > 0
            and first_digest
            == first["witness_digest_sha256"]
            == EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST
        ),
        "registered_positive_global_minimum_reproduces": bool(
            minimum["aggregate_index"] == q011al.OBSTRUCTION_AGGREGATE_INDEX
            and minimum["target_identifier"] == "block=11;center=4"
            and minimum["left_index"] == 385
            and minimum["right_index"] == 0
            and minimum["wave_multiplicity"] == 35
            and minimum["relation"] == "product_below_target"
            and minimum["outward_gap_lower"]["binary64_hex"] == EXPECTED_GLOBAL_MINIMUM_GAP_HEX
            and minimum["outward_gap_lower"]["float"] > 0
            and minimum["exact_gap_hex"] == EXPECTED_GLOBAL_EXACT_GAP_HEX
            and q011z._fraction(minimum["exact_gap"]) > 0
            and minimum_digest == minimum["witness_digest_sha256"] == EXPECTED_GLOBAL_WITNESS_DIGEST
        ),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "grid": [SIZE, SIZE],
        "fixed_conservation_leaf": True,
        "degree": DEGREE,
        "old_modulus_overlap_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
        "expected_remaining_aggregate_index": EXPECTED_OBSTRUCTION_AGGREGATE_INDEX,
        "q011al_artifact_sha256": Q011AL_ARTIFACT_SHA256,
        "q011al_runner_sha256": Q011AL_RUNNER_SHA256,
        "q011al_digests": list(Q011AL_DIGESTS),
        "aggregate_record_digest_sha256": EXPECTED_AGGREGATE_DIGEST,
        "classification_matrix_digest_sha256": EXPECTED_CLASSIFICATION_MATRIX_DIGEST,
        "first_unresolved_witness_digest_sha256": (EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST),
        "registered_classification": REJECTED_CLASSIFICATION,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "factorization_digest_sha256": cycle["factorization_digest_sha256"],
        "enumeration_digest_sha256": cycle["enumeration_digest_sha256"],
        "obstruction_digest_sha256": cycle["obstruction_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_degree16_hybrid_sweep_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    hybrid, lookup, classes, counts, external_indices, targets = _hybrid_input_audit(artifacts)
    sweep = _hierarchical_sweep_audit(classes, lookup, counts, external_indices, targets)
    bridge = _prefix_and_q011al_bridge_audit(artifacts, sweep)
    sweep_checks = _registered_sweep_checks(sweep)

    input_sections = {
        "sealed_input_audit": sealed,
        "hybrid_input_audit": hybrid,
    }
    factorization_sections = {
        key: sweep[key]
        for key in (
            "class_power_record_count",
            "class_power_record_digest_sha256",
            "group_signature_record_count",
            "group_signature_digest_sha256",
            "pair_pool_record_count",
            "pair_pool_record_digest_sha256",
            "convolution_call_count",
            "maximum_convolution_crude_int64_bound",
            "all_convolutions_nonnegative",
            "all_convolution_fiber_sums_exact",
        )
    }
    enumeration_sections = {
        key: sweep[key]
        for key in (
            "audited_overlap_aggregate_count",
            "fully_separated_overlap_aggregate_count",
            "remaining_overlap_aggregate_count",
            "remaining_overlap_aggregate_indices",
            "original_monomial_count",
            "modulus_signature_count",
            "compatible_modulus_signature_count",
            "compatible_original_monomial_count",
            "weighted_comparison_count",
            "distinct_comparison_count",
            "weighted_relation_counts",
            "distinct_relation_counts",
            "aggregate_record_digest_sha256",
            "bound_matrix_digest_sha256",
            "coefficient_matrix_digest_sha256",
            "classification_matrix_digest_sha256",
            "maximum_live_combined_signature_count",
            "maximum_wave_coefficient",
            "maximum_fourier_crude_int64_bound",
        )
    }
    obstruction_sections = {
        "aggregate_fifty_five": sweep["aggregate_records"][EXPECTED_OBSTRUCTION_AGGREGATE_INDEX],
        "global_minimum_separated_witness": sweep["global_minimum_separated_witness"],
        "first_unresolved_witness": sweep["first_unresolved_witness"],
        "bridge_audit": bridge,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    factorization_digest = q011b._canonical_json_sha256(factorization_sections)
    enumeration_digest = q011b._canonical_json_sha256(enumeration_sections)
    obstruction_digest = q011b._canonical_json_sha256(obstruction_sections)

    validity_gates = {
        "q011al_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "17 artifacts and 88 direct digests reproduce",
            "value": sealed["checks"],
        },
        "hybrid_envelope_and_degree_sixteen_inventory_reconstruct": {
            "passed": hybrid["passed"],
            "threshold": "204 hybrid identifiers and 154 overlap aggregates reproduce",
            "value": hybrid["checks"],
        },
        "hierarchical_exact_multiplicity_protocol_is_valid": {
            "passed": bool(
                sweep_checks["registered_resource_and_factorization_values_reproduce"]
                and sweep_checks["all_exact_integer_and_outward_array_invariants_hold"]
            ),
            "threshold": "class powers are outward and every int64 convolution is exact",
            "value": {
                "resource": sweep_checks["registered_resource_and_factorization_values_reproduce"],
                "arithmetic": sweep_checks["all_exact_integer_and_outward_array_invariants_hold"],
            },
        },
        "all_one_hundred_fifty_four_aggregates_and_matrix_hashes_reproduce": {
            "passed": bool(
                sweep_checks["registered_full_sweep_counts_reproduce"]
                and sweep_checks["registered_matrix_and_aggregate_digests_reproduce"]
            ),
            "threshold": "all registered totals and matrix digests reproduce",
            "value": {
                "counts": sweep_checks["registered_full_sweep_counts_reproduce"],
                "digests": sweep_checks["registered_matrix_and_aggregate_digests_reproduce"],
            },
        },
        "q011aj_prefix_and_q011al_clearance_bridges_reproduce": {
            "passed": bridge["passed"],
            "threshold": "indices 0--99 counts and index 99 exact witness reproduce",
            "value": bridge["checks"],
        },
        "registered_obstruction_and_witnesses_reproduce": {
            "passed": bool(
                sweep_checks["sole_remaining_obstruction_record_reproduces"]
                and sweep_checks["registered_first_unresolved_exact_witness_reproduces"]
                and sweep_checks["registered_positive_global_minimum_reproduces"]
            ),
            "threshold": "sole index 55, positive intersection and global gap reproduce",
            "value": {
                "obstruction": sweep_checks["sole_remaining_obstruction_record_reproduces"],
                "unresolved_witness": sweep_checks[
                    "registered_first_unresolved_exact_witness_reproduces"
                ],
                "global_minimum": sweep_checks["registered_positive_global_minimum_reproduces"],
            },
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(
                    len(digest) == 64
                    for digest in (
                        input_digest,
                        factorization_digest,
                        enumeration_digest,
                        obstruction_digest,
                    )
                )
                and _runner_source_metadata()["filename"] == "q011am_degree16_hybrid_sweep.py"
            ),
            "threshold": "strict finite JSON, four section digests and runner metadata",
            "value": {
                "input": input_digest,
                "factorization": factorization_digest,
                "enumeration": enumeration_digest,
                "obstruction": obstruction_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    first = sweep["first_unresolved_witness"]
    hypothesis_gates = {
        "eight_hundred_fifteen_old_modulus_separations_are_preserved": {
            "passed": bool(
                validity_passed
                and hybrid["old_modulus_separated_aggregate_count"]
                == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            ),
            "threshold": "815 old separations survive hybrid containment",
            "value": hybrid["old_modulus_separated_aggregate_count"],
        },
        "all_old_overlap_aggregates_are_completely_classified": {
            "passed": bool(
                validity_passed
                and sweep["audited_overlap_aggregate_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            ),
            "threshold": "all 154 old overlaps are audited",
            "value": sweep["audited_overlap_aggregate_count"],
        },
        "one_hundred_fifty_three_aggregates_are_fully_separated": {
            "passed": bool(
                validity_passed
                and sweep["fully_separated_overlap_aggregate_count"]
                == EXPECTED_FULLY_SEPARATED_AGGREGATE_COUNT
            ),
            "threshold": "153 aggregates contain zero interval overlaps",
            "value": sweep["fully_separated_overlap_aggregate_count"],
        },
        "aggregate_fifty_five_is_the_sole_remaining_overlap": {
            "passed": bool(
                validity_passed
                and sweep["remaining_overlap_aggregate_indices"]
                == [EXPECTED_OBSTRUCTION_AGGREGATE_INDEX]
                and sweep["distinct_relation_counts"]["overlap"]
                == EXPECTED_DISTINCT_RELATIONS["overlap"]
                and sweep["weighted_relation_counts"]["overlap"]
                == EXPECTED_WEIGHTED_RELATIONS["overlap"]
            ),
            "threshold": "only index 55 retains 24960 distinct overlaps",
            "value": {
                "indices": sweep["remaining_overlap_aggregate_indices"],
                "distinct": sweep["distinct_relation_counts"]["overlap"],
                "weighted": sweep["weighted_relation_counts"]["overlap"],
            },
        },
        "first_overlap_and_center_only_separation_are_both_strict": {
            "passed": bool(
                validity_passed
                and q011z._fraction(first["intersection_interval"]["width"]) > 0
                and first["center_only_diagnostic"]["relation"] == "product_below_target"
                and q011z._fraction(first["center_only_diagnostic"]["gap"]) > 0
            ),
            "threshold": "hybrid intervals overlap while center-only intervals separate",
            "value": {
                "intersection_width_hex": first["intersection_interval"]["width_hex"],
                "center_relation": first["center_only_diagnostic"]["relation"],
                "center_gap_hex": first["center_only_diagnostic"]["gap_hex"],
            },
        },
        "remaining_interval_overlap_is_not_promoted_to_actual_resonance": {
            "passed": validity_passed,
            "threshold": "an enclosure overlap is reported only as certificate failure",
            "value": "actual complex resonance is not established",
        },
    }
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    registered_rejection = bool(validity_passed and hypothesis_passed)
    cycle = {
        "question": (
            "Does the Q011al six-source hybrid envelope certify all 154 "
            "degree-sixteen modulus-overlap aggregates?"
        ),
        "registered_parameters": _registered_parameters(),
        **input_sections,
        "hierarchical_degree_sixteen_sweep_audit": sweep,
        "q011aj_prefix_and_q011al_clearance_bridge_audit": bridge,
        "registered_sweep_checks": sweep_checks,
        "runner_source": _runner_source_metadata(),
        "input_digest_sha256": input_digest,
        "factorization_digest_sha256": factorization_digest,
        "enumeration_digest_sha256": enumeration_digest,
        "obstruction_digest_sha256": obstruction_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": "rejected" if registered_rejection else "inconclusive",
        "actual_resonance_outcome": ("not_established" if registered_rejection else "inconclusive"),
        "scientific_classification": (
            REJECTED_CLASSIFICATION if registered_rejection else INCONCLUSIVE_CLASSIFICATION
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "q011al_hybrid_eigendisc_inclusion_is_preserved": registered_rejection,
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "newly_fully_separated_overlap_aggregate_count": (
            EXPECTED_FULLY_SEPARATED_AGGREGATE_COUNT if registered_rejection else 0
        ),
        "aggregate_fifty_five_is_the_sole_remaining_interval_obstruction": (registered_rejection),
        "six_source_hybrid_degree_sixteen_certificate_is_rejected": (registered_rejection),
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
        "q011k_through_q011al_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the 154 Q011aj degree-sixteen modulus-overlap "
        "aggregates for the fixed 17x17 repaired exact map on one fixed conservation "
        "leaf, the Q011al six-source hybrid eigendisc envelope, exact x-Fourier "
        "multiplicities and the registered hierarchical outward-dyadic product "
        "protocol. The sole aggregate-55 interval overlap is not an actual complex "
        "resonance. This audit establishes no degree-sixteen external nonresonance, "
        "result for degrees 17 through 90, all-order nonresonance, higher graph "
        "smoothness, SSM existence or uniqueness, normal attraction, basin, other "
        "grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ai_certificates_and_diagnostics_changed": False,
        "q011aj_and_q011ak_rejections_changed": False,
        "q011al_registered_obstruction_clearance_changed": False,
    }
    if registered_rejection:
        cycle["next_change"] = (
            "Preregister Q011an to construct row-specific contained eigendiscs for "
            "the block-1, block-13 and block-16 identifiers active in aggregate 55."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first seal, hybrid-input, hierarchical-factorization, "
            "full-enumeration, bridge, witness or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011am cycle failed strict serialization or digest")
    return cycle


def run_q011am_pilot() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    hybrid, lookup, classes, counts, external_indices, targets = _hybrid_input_audit(artifacts)
    sweep = _hierarchical_sweep_audit(classes, lookup, counts, external_indices, targets)
    result = {
        "sealed_input_audit": sealed,
        "hybrid_input_audit": hybrid,
        "hierarchical_degree_sixteen_sweep_audit": sweep,
    }
    if not (
        _all_numeric_values_finite(result)
        and _strict_json_serializable(result)
        and json.dumps(result, allow_nan=False)
    ):
        raise RuntimeError("Q011am pilot failed strict serialization")
    return result


def run_q011am_study() -> dict[str, Any]:
    cycle = run_degree16_hybrid_sweep_audit()
    sweep = cycle["hierarchical_degree_sixteen_sweep_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "proof_enclosure_type": ("outward-rounded IEEE-754 binary64 interval products"),
            "fourier_convolution_type": (
                "exact numpy.int64 17x17 cyclic convolution with checked bounds"
            ),
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "class_power_record_count": sweep["class_power_record_count"],
            "group_signature_record_count": sweep["group_signature_record_count"],
            "pair_pool_record_count": sweep["pair_pool_record_count"],
            "convolution_call_count": sweep["convolution_call_count"],
            "maximum_convolution_crude_int64_bound": sweep["maximum_convolution_crude_int64_bound"],
            "weighted_comparison_count": sweep["weighted_comparison_count"],
            "distinct_comparison_count": sweep["distinct_comparison_count"],
        },
        "mathematical_scope": {
            "diagnostic": (
                "full degree-16 six-source hybrid-envelope sweep over the "
                "Q011aj modulus-overlap aggregates"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "audited_overlap_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
            "registered_hybrid_certificate_claim": True,
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
    result = run_q011am_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
