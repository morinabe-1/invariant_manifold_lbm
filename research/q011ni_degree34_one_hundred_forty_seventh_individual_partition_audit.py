"""Q011ni individual-disc partition audit for Q011cb flatten ordinal 146."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q011cg_degree34_third_individual_partition_audit as q011cg
import research.q011nh_degree34_one_hundred_forty_sixth_component_safe_phase_discs as q011nh
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ag = q011cg.q011ag
q011b = q011cg.q011b
q011z = q011cg.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_FLAT_ORDINAL = 146
PARENT_LEFT_INDEX = 18
PARENT_RIGHT_INDEX = 2
PARENT_CLASS_COUNTS = (
    (0, 0, 1, 12),
    (8, 1),
    (5,),
    (2, 5),
)
OCCUPIED_SPEC = (
    (0, 2, 1),
    (0, 3, 12),
    (1, 0, 8),
    (1, 1, 1),
    (2, 0, 5),
    (3, 0, 2),
    (3, 1, 5),
)
EXPECTED_IDENTIFIER_ORDER = (
    "block=16;center=144",
    "block=1;center=144",
    "block=16;center=145",
    "block=1;center=145",
    "block=16;center=150",
    "block=1;center=150",
    "block=16;center=151",
    "block=1;center=151",
    "block=16;center=152",
    "block=1;center=152",
    "block=16;center=148",
    "block=1;center=148",
    "block=16;center=149",
    "block=1;center=149",
)
EXPECTED_CLASS_TOTALS = (1, 12, 8, 1, 5, 2, 5)
EXPECTED_SOURCE_COUNTS = (1, 0, 12, 0, 8, 0, 1, 0, 0, 5, 0, 2, 0, 5)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (
    0,
    1,
    0,
    12,
    0,
    8,
    0,
    1,
    0,
    5,
    0,
    2,
    5,
    0,
)
EXPECTED_LAST_COMPATIBLE_COUNTS = EXPECTED_SOURCE_COUNTS
EXPECTED_PARENT_ALLOCATION_INDEX = 50_436
EXPECTED_PARENT_COMPATIBLE_INDEX = 2_798
EXPECTED_ALLOCATION_COUNT = 50_544
EXPECTED_COMPATIBLE_COUNT = 2_799

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "8c192189449f149db3b3786d791a4fc262ff9ff3c89d831307cbab2faa614734",
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "e5b5ce415bac811880fc0ccaa97743c37d7e2510a679d48e627a6eaad2c05399",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "aea681cab5d2a0c4176e23896038ecfc3433ebb73dfc9ecd3567248e73d989db",
    "66a6c269ac137479694f186884d49ca3a4d11070e69132bab822391a557075d8",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = "e1c38d53c3cfab289229070273dfb483a1c408da91e5b442c5ce017afed8c349"
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "c90ea70931e0bb67733cb9179566e166baf2a67756933394db785fb4f941276a"
)
EXPECTED_ALLOCATION_DIGEST = "6cd441e005b01b465684601e19ace36baa7ec67aa072c072aef7a2b26743cf42"
EXPECTED_COMPATIBLE_DIGEST = "3df75c64a04d2fc4da83173544a6932c431032726097f61b163751596caf0042"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 2_799
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.4b3329e1117b2p-31"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.32d7515995964p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "ee4ff088c181aaeea95577771a0f7fe5472ba7452a2a31d3ca006bb560d1ac7c"
EXPECTED_PARENT_PRODUCT_DIGEST = "1515374b8cc39a2ca2612f9f19f4734e2f6831e88de57dd2de7ef3b41582306c"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "9173dcd888c978c05198da502ad62ac6f9ee43330af3924498e92ebae7df8478"
)
EXPECTED_PARENT_TARGET_DIGEST = "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "b19987d0b83cf33075a520e19de6f7dac8e3cdaf312f6a1a5c27953fb7af094f"
)

Q011NH_ARTIFACT_SHA256 = "bae0da5210fbe056852b5045ed237d3a6975f93f85bfc8fb1f5256bf07bb10c4"
Q011NH_RUNNER_SHA256 = "609dec025547a39e15c045045df214eb5d43105b395134c3ef864c311d87d1b6"
Q011NH_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011NH_DIGESTS = (
    "35dfd4bb81d6de12d13e82c922a924ab46100255564c7feee3eef2e6d4e851e9",
    "9573ff2142198ac2ce572d9ed6be4efc26eacf871cfdde04c56c8b380ab586f6",
    "e8269a3660fb124ee53aaad623a4ad9a89256f02cdef2b7a45fa09a2e2d98a72",
    "995044ed2ca9851d75017a6c51dbe515fd1dfaa8b615457e5b6be77e35e55f3a",
    "feaeeaeec21a3277fbdf7347d64ca14b8c4839fba3a4cc8738b01502661499cf",
)
EXPECTED_Q011NH_STREAM_DIGEST = "65399715ceb4f18d03aed0036adee018ac9680f761f5f42996e0782480a18ca8"
EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST = (
    "9d542b49c39fd1540ca85a454354fb568fed3d9fabd5fb55e44188171d03875d"
)
ALLOCATION_STREAM_DOMAIN = "q011ni-individual-partition-allocation-records-v1"

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the one-hundred-forty-seventh "
    "Q011cb witness"
)
RESOLVED_CLASSIFICATION = (
    "the one-hundred-forty-seventh Q011cb witness is resolved by individual partition"
)
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the one-hundred-forty-seventh "
    "Q011cb witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ni individual-disc partition audit is inconclusive"

_Q011CG_PROTOCOL_OVERRIDE: dict[str, Any] = {
    "PARENT_FLAT_ORDINAL": PARENT_FLAT_ORDINAL,
    "PARENT_LEFT_INDEX": PARENT_LEFT_INDEX,
    "PARENT_RIGHT_INDEX": PARENT_RIGHT_INDEX,
    "PARENT_CLASS_COUNTS": PARENT_CLASS_COUNTS,
    "OCCUPIED_SPEC": OCCUPIED_SPEC,
    "EXPECTED_IDENTIFIER_ORDER": EXPECTED_IDENTIFIER_ORDER,
    "EXPECTED_SOURCE_COUNTS": EXPECTED_SOURCE_COUNTS,
    "EXPECTED_FIRST_COMPATIBLE_COUNTS": EXPECTED_FIRST_COMPATIBLE_COUNTS,
    "EXPECTED_LAST_COMPATIBLE_COUNTS": EXPECTED_LAST_COMPATIBLE_COUNTS,
    "EXPECTED_PARENT_ALLOCATION_INDEX": EXPECTED_PARENT_ALLOCATION_INDEX,
    "EXPECTED_PARENT_COMPATIBLE_INDEX": EXPECTED_PARENT_COMPATIBLE_INDEX,
    "EXPECTED_ALLOCATION_COUNT": EXPECTED_ALLOCATION_COUNT,
    "EXPECTED_COMPATIBLE_COUNT": EXPECTED_COMPATIBLE_COUNT,
    "EXPECTED_OCCUPIED_INTERVAL_DIGESTS": EXPECTED_OCCUPIED_INTERVAL_DIGESTS,
    "EXPECTED_OCCUPIED_RECORD_DIGEST": EXPECTED_OCCUPIED_RECORD_DIGEST,
    "EXPECTED_IDENTIFIER_ORDER_DIGEST": EXPECTED_IDENTIFIER_ORDER_DIGEST,
    "EXPECTED_ALLOCATION_DIGEST": EXPECTED_ALLOCATION_DIGEST,
    "EXPECTED_COMPATIBLE_DIGEST": EXPECTED_COMPATIBLE_DIGEST,
    "EXPECTED_PARENT_WAVE_MULTIPLICITY": EXPECTED_PARENT_WAVE_MULTIPLICITY,
    "EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY": EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY,
    "EXPECTED_PARENT_INTERSECTION_WIDTH_HEX": EXPECTED_PARENT_INTERSECTION_WIDTH_HEX,
    "EXPECTED_PARENT_CENTER_RELATION": EXPECTED_PARENT_CENTER_RELATION,
    "EXPECTED_PARENT_CENTER_GAP_HEX": EXPECTED_PARENT_CENTER_GAP_HEX,
    "EXPECTED_PARENT_WITNESS_DIGEST": EXPECTED_PARENT_WITNESS_DIGEST,
}
_Q011CG_PROTOCOL_BASELINE = {
    name: getattr(q011cg, name) for name in _Q011CG_PROTOCOL_OVERRIDE
}


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


@contextmanager
def _q011cg_protocol_context() -> Iterator[None]:
    original = {name: getattr(q011cg, name) for name in _Q011CG_PROTOCOL_OVERRIDE}
    try:
        for name, value in _Q011CG_PROTOCOL_OVERRIDE.items():
            setattr(q011cg, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(q011cg, name, value)


def _protocol_globals_are_restored() -> bool:
    return bool(
        all(
            getattr(q011cg, name) == value
            for name, value in _Q011CG_PROTOCOL_BASELINE.items()
        )
        and q011nh._protocol_globals_are_restored()
    )


@lru_cache(maxsize=1)
def _sealed_input_audit_cached() -> tuple[
    dict[str, Any], dict[str, dict[str, Any]]
]:
    prior, artifacts = q011nh._sealed_input_audit()
    artifacts = dict(artifacts)
    artifact_path = _artifact_directory() / (
        "q011nh_degree34_one_hundred_forty_sixth_component_safe_phase_discs.json"
    )
    runner_path = Path(q011nh.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011NH_DIGEST_NAMES)
    checks = {
        "q011nh_three_hundred_fifty_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 350
            and prior["direct_digest_count"] == 1_587
            and len(artifacts) == 350
            and all(prior["checks"].values())
        ),
        "q011nh_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011NH_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011NH_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011NH_RUNNER_SHA256
        ),
        "q011nh_section_digests_match": digests == Q011NH_DIGESTS,
        "q011nh_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "component_safe_complex_phase_discs_resolve_one_hundred_forty_sixth_q011cb_witness"
            ]
            and theorem[
                "q011ng_ordinal_one_hundred_forty_five_interval_inert_diagnostic_is_preserved"
            ]
            and all(
                value
                for name, value in theorem.items()
                if name.endswith("_is_preserved") and isinstance(value, bool)
            )
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"]
            == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"]
            == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011nh_registered_ordinal_one_hundred_forty_five_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 26_644
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 26_644,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"]
            == EXPECTED_Q011NH_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"][
                "witness_digest_sha256"
            ]
            == EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011nh_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_thousand_five_hundred_ninety_two_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 1_592
        ),
    }
    artifacts["q011nh"] = artifact
    return (
        {
            "prior_q011nh_sealed_input_audit": prior,
            "q011nh": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011NH_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (
                    EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST
                ),
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    return _sealed_input_audit_cached()


def _fixed_individual_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[dict[str, Any], ...],
    dict[str, Any],
]:
    with _q011cg_protocol_context():
        fixed, lookup, compatible, parent = q011cg._fixed_individual_input_audit(
            artifacts
        )
    selection = fixed.pop("third_parent_witness_selection_audit")
    previous_check = selection["checks"].pop(
        "ordinal_zero_and_one_are_sealed_phase_resolutions"
    )
    registered_check = selection["checks"].pop(
        "registered_ordinal_two_parent_witness_reproduces"
    )
    q011nh_cycle = artifacts["q011nh"]["cycle"]
    q011nh_comparison = q011nh_cycle["complex_phase_product_disc_audit"]
    selection["checks"][
        "ordinals_zero_through_one_hundred_forty_five_are_sealed_phase_resolutions"
    ] = bool(
        previous_check
        and q011nh_cycle["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_one_hundred_forty_sixth_q011cb_witness"
        ]
        and q011nh_comparison["global_minimum_margin_witness"][
            "witness_digest_sha256"
        ]
        == EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST
    )
    selection["checks"][
        "registered_ordinal_one_hundred_forty_six_parent_witness_reproduces"
    ] = registered_check
    selection["checks"]["registered_parent_interval_subdigests_reproduce"] = bool(
        q011b._canonical_json_sha256(parent["hybrid_product_interval"])
        == EXPECTED_PARENT_PRODUCT_DIGEST
        and q011b._canonical_json_sha256(parent["center_product_interval"])
        == EXPECTED_PARENT_CENTER_PRODUCT_DIGEST
        and q011b._canonical_json_sha256(parent["hybrid_target_interval"])
        == EXPECTED_PARENT_TARGET_DIGEST
        and q011b._canonical_json_sha256(parent["intersection_interval"])
        == EXPECTED_PARENT_INTERSECTION_DIGEST
    )
    selection["previous_phase_resolved_ordinals"] = list(range(146))
    selection["ordinal_one_hundred_forty_five_resolution_digest_sha256"] = (
        EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_FIVE_RESOLUTION_DIGEST
    )
    selection["one_hundred_forty_seventh_parent_witness"] = selection.pop(
        "third_parent_witness"
    )
    selection["one_hundred_forty_seventh_parent_witness_digest_sha256"] = (
        selection.pop("third_parent_witness_digest_sha256")
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["one_hundred_forty_seventh_parent_witness_selection_audit"] = selection
    fixed["checks"].pop("registered_third_parent_selection_reproduces")
    fixed["checks"][
        "registered_one_hundred_forty_seventh_parent_selection_reproduces"
    ] = selection["passed"]
    fixed["checks"]["q011cg_protocol_globals_are_restored"] = (
        _protocol_globals_are_restored()
    )
    fixed["passed"] = all(fixed["checks"].values())
    return fixed, lookup, compatible, parent


def _interval_record(lower: Fraction, upper: Fraction) -> dict[str, Any]:
    if not lower <= upper:
        raise RuntimeError("Q011ni constructed an unordered interval")
    return {
        "lower": q011z._exact_fraction_record(lower),
        "upper": q011z._exact_fraction_record(upper),
    }


def _class_totals(counts: list[int]) -> list[int]:
    return [counts[index] + counts[index + 1] for index in range(0, len(counts), 2)]


def _allocation_stream_digest(records: list[dict[str, Any]]) -> str:
    digest = sha256()
    encoded_domain = ALLOCATION_STREAM_DOMAIN.encode("utf-8")
    digest.update(len(encoded_domain).to_bytes(8, "big"))
    digest.update(encoded_domain)
    for record in records:
        encoded = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    class_totals = tuple(
        _class_totals(allocation["individual_counts"]) for allocation in compatible
    )
    class_totals_are_registered = all(
        totals == list(EXPECTED_CLASS_TOTALS) for totals in class_totals
    )
    equal_interval_pairs = all(
        lookup[EXPECTED_IDENTIFIER_ORDER[index]].center_modulus
        == lookup[EXPECTED_IDENTIFIER_ORDER[index + 1]].center_modulus
        and lookup[EXPECTED_IDENTIFIER_ORDER[index]].modulus
        == lookup[EXPECTED_IDENTIFIER_ORDER[index + 1]].modulus
        for index in range(0, len(EXPECTED_IDENTIFIER_ORDER), 2)
    )
    with _q011cg_protocol_context():
        product_record, center_record = q011cg._exact_product_records(
            lookup, list(EXPECTED_SOURCE_COUNTS)
        )
    exact_product_evaluation_count = 1

    target = lookup[TARGET_IDENTIFIER]
    parent_product = parent["hybrid_product_interval"]
    parent_center = parent["center_product_interval"]
    parent_target = parent["hybrid_target_interval"]
    parent_center_target = parent["center_target_interval"]
    parent_intersection = parent["intersection_interval"]
    parent_center_diagnostic = parent["center_only_diagnostic"]
    target_record = _interval_record(target.modulus.lower, target.modulus.upper)
    center_target_record = _interval_record(
        target.center_modulus.lower, target.center_modulus.upper
    )
    product_lower = q011z._fraction(product_record["lower"])
    product_upper = q011z._fraction(product_record["upper"])
    target_lower = target.modulus.lower
    target_upper = target.modulus.upper
    intersection = None
    if product_upper < target_lower:
        relation = "product_below_target"
        exact_gap = target_lower - product_upper
    elif target_upper < product_lower:
        relation = "target_below_product"
        exact_gap = product_lower - target_upper
    else:
        relation = "overlap"
        exact_gap = Fraction(0)
        lower = max(product_lower, target_lower)
        upper = min(product_upper, target_upper)
        intersection = {
            **_interval_record(lower, upper),
            "width": q011z._exact_fraction_record(upper - lower),
            "width_hex": float(upper - lower).hex(),
        }
    center_lower = q011z._fraction(center_record["lower"])
    center_upper = q011z._fraction(center_record["upper"])
    if center_upper < target.center_modulus.lower:
        center_relation = "product_below_target"
        center_gap = target.center_modulus.lower - center_upper
    elif target.center_modulus.upper < center_lower:
        center_relation = "target_below_product"
        center_gap = center_lower - target.center_modulus.upper
    else:
        center_relation = "overlap"
        center_gap = Fraction(0)
    binary64_relation, binary64_gap = q011cg._binary64_relation_and_gap(
        product_lower, product_upper, target_lower, target_upper
    )
    product_digest = q011b._canonical_json_sha256(product_record)
    center_digest = q011b._canonical_json_sha256(center_record)
    target_digest = q011b._canonical_json_sha256(target_record)
    product_equals_parent = product_record == parent_product
    center_equals_parent = center_record == parent_center
    target_equals_parent = bool(
        target_record == parent_target and center_target_record == parent_center_target
    )
    intersection_equals_parent = intersection == parent_intersection
    center_diagnostic_equals_parent = bool(
        center_relation == parent_center_diagnostic["relation"]
        and q011z._exact_fraction_record(center_gap)
        == parent_center_diagnostic["gap"]
        and float(center_gap).hex() == parent_center_diagnostic["gap_hex"]
    )

    records = []
    exact_relations: Counter[str] = Counter()
    binary64_relations: Counter[str] = Counter()
    for allocation_index, (allocation, totals) in enumerate(
        zip(compatible, class_totals, strict=True)
    ):
        counts = allocation["individual_counts"]
        record = {
            "compatible_allocation_index": allocation_index,
            "individual_counts": counts,
            "class_totals": totals,
            "class_totals_equal_registered": totals == list(EXPECTED_CLASS_TOTALS),
            "degree": sum(counts),
            "output_block": allocation["output_block"],
            "exact_relation": relation,
            "binary64_outward_relation": binary64_relation,
            "exact_gap_positive": exact_gap > 0,
            "exact_gap_hex": float(exact_gap).hex(),
            "binary64_outward_gap_positive": binary64_gap > 0,
            "binary64_outward_gap_hex": binary64_gap.hex(),
            "product_interval_digest_sha256": product_digest,
            "center_product_interval_digest_sha256": center_digest,
            "target_interval_digest_sha256": target_digest,
            "intersection_width_hex": (
                intersection["width_hex"] if intersection is not None else None
            ),
            "center_only_relation": center_relation,
            "center_only_gap_hex": float(center_gap).hex(),
            "product_equals_parent": product_equals_parent,
            "center_product_equals_parent": center_equals_parent,
            "target_equals_parent": target_equals_parent,
            "intersection_equals_parent": intersection_equals_parent,
            "center_diagnostic_equals_parent": center_diagnostic_equals_parent,
        }
        exact_relations[relation] += 1
        binary64_relations[binary64_relation] += 1
        records.append(record)
    relation_order = ("product_below_target", "target_below_product", "overlap")
    exact_relation_counts = {
        name: exact_relations[name] for name in relation_order
    }
    binary64_relation_counts = {
        name: binary64_relations[name] for name in relation_order
    }
    all_parent_equal = all(
        record["product_equals_parent"]
        and record["center_product_equals_parent"]
        and record["target_equals_parent"]
        and record["intersection_equals_parent"]
        and record["center_diagnostic_equals_parent"]
        for record in records
    )
    stream_digest = _allocation_stream_digest(records)
    checks = {
        "all_registered_compatible_allocations_are_processed": bool(
            len(records) == EXPECTED_COMPATIBLE_COUNT
            and [record["compatible_allocation_index"] for record in records]
            == list(range(EXPECTED_COMPATIBLE_COUNT))
        ),
        "all_registered_class_totals_are_preserved": bool(
            class_totals_are_registered
            and all(record["class_totals_equal_registered"] for record in records)
        ),
        "all_singleton_pairs_have_equal_exact_intervals": equal_interval_pairs,
        "common_exact_product_is_evaluated_once": exact_product_evaluation_count == 1,
        "all_degree_and_output_block_constraints_close": all(
            record["degree"] == DEGREE and record["output_block"] == OUTPUT_BLOCK
            for record in records
        ),
        "exact_relation_partition_is_exclusive_and_complete": (
            sum(exact_relation_counts.values()) == EXPECTED_COMPATIBLE_COUNT
        ),
        "binary64_relation_partition_is_exclusive_and_complete": (
            sum(binary64_relation_counts.values()) == EXPECTED_COMPATIBLE_COUNT
        ),
        "all_exact_and_binary64_relations_agree": bool(
            exact_relation_counts == binary64_relation_counts
            and all(
                record["exact_relation"] == record["binary64_outward_relation"]
                for record in records
            )
        ),
        "all_strict_gap_flags_match_relations": all(
            (record["exact_gap_positive"] and record["binary64_outward_gap_positive"])
            == (record["exact_relation"] != "overlap")
            for record in records
        ),
        "allocation_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
            and len(stream_digest) == 64
        ),
        "q011cg_protocol_globals_are_restored": _protocol_globals_are_restored(),
    }
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "target_identifier": TARGET_IDENTIFIER,
        "compatible_allocation_count": len(records),
        "registered_class_totals": list(EXPECTED_CLASS_TOTALS),
        "all_compatible_allocations_preserve_registered_class_totals": (
            class_totals_are_registered
        ),
        "exact_product_evaluation_count": exact_product_evaluation_count,
        "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs": bool(
            equal_interval_pairs and class_totals_are_registered
        ),
        "exact_relation_counts": exact_relation_counts,
        "binary64_outward_relation_counts": binary64_relation_counts,
        "all_product_target_intersection_and_center_records_equal_parent": (
            all_parent_equal
        ),
        "parent_product_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_product
        ),
        "parent_center_product_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_center
        ),
        "parent_target_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_target
        ),
        "parent_intersection_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_intersection
        ),
        "allocation_stream_domain": ALLOCATION_STREAM_DOMAIN,
        "allocation_classification_records": records,
        "allocation_classification_record_digest_sha256": (
            q011b._canonical_json_sha256(records)
        ),
        "allocation_classification_stream_digest_sha256": stream_digest,
        "first_allocation_record": records[0],
        "last_allocation_record": records[-1],
        "full_allocation_target_matrix_retained": False,
        "previous_q011cb_refined_signatures_recomputed": False,
        "later_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "complex_phase_product_evaluated": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "target_identifier": TARGET_IDENTIFIER,
        "output_block": OUTPUT_BLOCK,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "parent_left_index": PARENT_LEFT_INDEX,
        "parent_right_index": PARENT_RIGHT_INDEX,
        "parent_class_counts": [list(group) for group in PARENT_CLASS_COUNTS],
        "occupied_spec": [list(record) for record in OCCUPIED_SPEC],
        "singleton_identifier_order": list(EXPECTED_IDENTIFIER_ORDER),
        "registered_class_totals": list(EXPECTED_CLASS_TOTALS),
        "full_allocation_count": EXPECTED_ALLOCATION_COUNT,
        "compatible_allocation_count": EXPECTED_COMPATIBLE_COUNT,
        "exact_product_evaluation_strategy": (
            "one exact evaluation after equal singleton intervals and fixed class totals"
        ),
        "expected_exact_product_evaluation_count": 1,
        "allocation_stream_domain": ALLOCATION_STREAM_DOMAIN,
        "temporary_q011cg_override_names": sorted(_Q011CG_PROTOCOL_OVERRIDE),
        "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        "previous_q011cb_refined_signatures_recomputed": False,
        "later_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "complex_phase_product_evaluated": False,
        "degree_thirty_four_nonresonance_claimed": False,
        "actual_resonance_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


_result_digest_sections = q011cg._result_digest_sections


def run_degree_thirty_four_one_hundred_forty_seventh_individual_partition_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    fixed, lookup, compatible, parent = _fixed_individual_input_audit(artifacts)
    partition = _individual_partition_audit(lookup, compatible, parent)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    partition_sections = {"fixed_individual_partition_input_audit": fixed}
    allocation_sections = {"individual_allocation_interval_audit": partition}
    input_digest = q011b._canonical_json_sha256(input_sections)
    partition_digest = q011b._canonical_json_sha256(partition_sections)
    allocation_digest = q011b._canonical_json_sha256(allocation_sections)
    selection = fixed["one_hundred_forty_seventh_parent_witness_selection_audit"]
    validity_gates = {
        "q011nh_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "351 artifacts and 1592 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_one_hundred_forty_seventh_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 146, class counts, 2799 multiplicity and exact witness",
            "value": selection[
                "one_hundred_forty_seventh_parent_witness_digest_sha256"
            ],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
                and partition["checks"][
                    "all_singleton_pairs_have_equal_exact_intervals"
                ]
            ),
            "threshold": "seven occupied pairs, fourteen identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "50544 total and 2799 output-block-7 compatible allocations",
            "value": {
                "full": fixed["full_allocation_count"],
                "compatible": fixed["compatible_allocation_count"],
            },
        },
        "all_class_total_degree_and_output_constraints_close": {
            "passed": bool(
                fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
                and partition["checks"]["all_registered_class_totals_are_preserved"]
                and partition["checks"]["all_degree_and_output_block_constraints_close"]
            ),
            "threshold": "2799 allocations, fixed class totals, degree 34 and output block 7",
            "value": partition["compatible_allocation_count"],
        },
        "registered_common_exact_evaluation_contract_is_obeyed": {
            "passed": bool(
                partition["exact_product_evaluation_count"] == 1
                and partition[
                    "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs"
                ]
            ),
            "threshold": "one exact product evaluation after both invariance proofs",
            "value": partition["exact_product_evaluation_count"],
        },
        "all_exact_interval_and_classification_invariants_pass": {
            "passed": partition["passed"],
            "threshold": "exact/outward exclusive relations and strict finite records",
            "value": partition["checks"],
        },
        "strict_section_digests_runner_and_protocol_provenance_reproduce": {
            "passed": bool(
                len(input_digest) == len(partition_digest) == len(allocation_digest) == 64
                and len(partition["allocation_classification_stream_digest_sha256"])
                == 64
                and runner["filename"]
                == "q011ni_degree34_one_hundred_forty_seventh_individual_partition_audit.py"
                and partition["first_allocation_record"] is not None
                and partition["last_allocation_record"] is not None
                and _protocol_globals_are_restored()
            ),
            "threshold": "three section digests, framed stream, endpoints, runner and restored protocol",
            "value": {
                "input": input_digest,
                "partition": partition_digest,
                "allocation": allocation_digest,
                "stream": partition[
                    "allocation_classification_stream_digest_sha256"
                ],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    all_parent_equal = partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    exact_counts = partition["exact_relation_counts"]
    binary_counts = partition["binary64_outward_relation_counts"]
    strict_count = exact_counts["product_below_target"] + exact_counts["target_below_product"]
    all_overlap = bool(
        exact_counts["overlap"] == EXPECTED_COMPATIBLE_COUNT
        and binary_counts == exact_counts
    )
    all_strict = bool(
        strict_count == EXPECTED_COMPATIBLE_COUNT
        and binary_counts["overlap"] == 0
        and all(
            record["exact_gap_positive"]
            and record["binary64_outward_gap_positive"]
            for record in partition["allocation_classification_records"]
        )
    )
    inert = validity_passed and all_parent_equal and all_overlap
    resolved = validity_passed and all_strict
    effective_persistent = bool(
        validity_passed and not inert and not resolved and exact_counts["overlap"] > 0
    )
    outcome_flags = (inert, resolved, effective_persistent)
    refinement_outcome = (
        "partition_inert_persistent"
        if inert
        else "resolved_by_individual_partition"
        if resolved
        else "partition_effective_but_persistent"
        if effective_persistent
        else "inconclusive"
    )
    classification = (
        INERT_CLASSIFICATION
        if inert
        else RESOLVED_CLASSIFICATION
        if resolved
        else EFFECTIVE_PERSISTENT_CLASSIFICATION
        if effective_persistent
        else INCONCLUSIVE_CLASSIFICATION
    )
    diagnostic_gates = {
        "only_the_registered_one_hundred_forty_seventh_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 146 only, one target and no other aggregate",
            "value": fixed["parent_class_counts"],
        },
        "parent_interval_comparison_is_complete": {
            "passed": bool(
                len(partition["allocation_classification_records"])
                == EXPECTED_COMPATIBLE_COUNT
                and all(
                    isinstance(record["product_equals_parent"], bool)
                    and isinstance(record["intersection_equals_parent"], bool)
                    for record in partition["allocation_classification_records"]
                )
            ),
            "threshold": "2799 complete parent-comparison records",
            "value": all_parent_equal,
        },
        "registered_stopping_rule_is_exclusive_and_reproduces": {
            "passed": bool(validity_passed and sum(outcome_flags) == 1),
            "threshold": "exactly one inert, resolved or effective-persistent branch",
            "value": {
                "inert": inert,
                "resolved": resolved,
                "effective_persistent": effective_persistent,
            },
        },
        "scientific_boundary_is_preserved": {
            "passed": True,
            "threshold": "no phase, degree-34, actual-resonance or SSM claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    cycle = {
        "question": (
            "Does splitting Q011cb flatten ordinal 146 into fourteen singleton "
            "identifiers change any compatible exact product interval or classification?"
        ),
        **input_sections,
        **partition_sections,
        **allocation_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "partition_input_digest_sha256": partition_digest,
        "allocation_audit_digest_sha256": allocation_digest,
        "validity_gates": validity_gates,
        "diagnostic_gates": diagnostic_gates,
        "failed_validity_order": [
            name for name, gate in validity_gates.items() if not gate["passed"]
        ],
        "failed_diagnostic_order": [
            name for name, gate in diagnostic_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "refinement_outcome": refinement_outcome,
        "diagnostic_classification": classification,
        "scientific_outcome": "not_evaluated",
        "actual_resonance_outcome": (
            "not_established" if validity_passed else "inconclusive"
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    prior_theorem = artifacts["q011nh"]["cycle"]["theorem_consequence"]
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_one_hundred_forty_seventh_q011cb_witness": inert,
        "one_hundred_forty_seventh_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_one_hundred_forty_seventh_q011cb_witness_persists": (
            effective_persistent
        ),
        "q011nh_ordinal_one_hundred_forty_five_phase_resolution_is_preserved": True,
        **{
            name: value
            for name, value in prior_theorem.items()
            if name.endswith("_is_preserved")
        },
        "q011cb_persistent_diagnostic_is_preserved": True,
        "q011bx_degree_thirty_four_sufficient_certificate_remains_rejected": True,
        "degree_thirty_four_external_nonresonance_is_certified": False,
        "an_actual_degree_thirty_four_external_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 34)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(34, 91)),
        "complex_phase_product_is_audited": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This diagnostic concerns only Q011cb flatten ordinal 146, its 2799 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 145 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44653 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011nj to expand only the registered 2799 wave allocations into component-safe complex phase discs."
        if inert
        else "Preregister Q011nj to audit flatten ordinal 147 in registered order."
        if resolved
        else (
            "Preregister Q011nj to refine only the first remaining individual-allocation overlap by component-safe complex phase."
        )
        if effective_persistent
        else "Repair only the first Q011ni validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011ni cycle failed strict serialization or digest")
    return cycle


def run_q011ni_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_one_hundred_forty_seventh_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "fourteen registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "exact_product_evaluations": partition[
                "exact_product_evaluation_count"
            ],
            "common_evaluation_contract": (
                "equal singleton intervals plus invariant class totals"
            ),
            "binary64_outward_enclosure": True,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "one-hundred-forty-seventh Q011cb witness individual-disc partition"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
            "target_identifier": TARGET_IDENTIFIER,
            "complex_phase_claim": False,
            "degree_thirty_four_nonresonance_claim": False,
            "actual_resonance_claim": False,
            "ssm_uniqueness_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "refinement_outcome": cycle["refinement_outcome"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011ni_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
