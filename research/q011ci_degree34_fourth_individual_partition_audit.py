"""Q011ci individual-disc partition audit for Q011cb flatten ordinal three."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011cg_degree34_third_individual_partition_audit as q011cg
import research.q011ch_degree34_third_component_safe_phase_discs as q011ch
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011cg.q011b
q011z = q011cg.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_FLAT_ORDINAL = 3
PARENT_LEFT_INDEX = 0
PARENT_RIGHT_INDEX = 3
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 13),
    (0, 9),
    (5,),
    (3, 4),
)
OCCUPIED_SPEC = (
    (0, 3, 13),
    (1, 1, 9),
    (2, 0, 5),
    (3, 0, 3),
    (3, 1, 4),
)
EXPECTED_IDENTIFIER_ORDER = q011cg.EXPECTED_IDENTIFIER_ORDER
EXPECTED_SOURCE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 3, 0, 4)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 9, 0, 5, 1, 2, 4, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 3, 0, 4)
EXPECTED_PARENT_ALLOCATION_INDEX = 16_680
EXPECTED_PARENT_COMPATIBLE_INDEX = 944
EXPECTED_ALLOCATION_COUNT = 16_800
EXPECTED_COMPATIBLE_COUNT = 945

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = q011cg.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
EXPECTED_OCCUPIED_RECORD_DIGEST = (
    "2ec2449ed38bb80b4ab6265b681f964d51b5ccd919f372b03632b6b542ac0ae5"
)
EXPECTED_IDENTIFIER_ORDER_DIGEST = q011cg.EXPECTED_IDENTIFIER_ORDER_DIGEST
EXPECTED_ALLOCATION_DIGEST = (
    "2ca0da1bc360abb84f6f6062059e22c14dd7f232a774e9731755fb8b984f6202"
)
EXPECTED_COMPATIBLE_DIGEST = (
    "2dbdedc591941d50bc3029fae69135bce675da8b74f369e7c2228ed7f12ca3ca"
)

EXPECTED_PARENT_WAVE_MULTIPLICITY = 945
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.9d4971545863bp-32"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.3aa0393a29573p-28"
EXPECTED_PARENT_WITNESS_DIGEST = (
    "20896b071ab67e2be3f8c214727a0600ddb45987dcee0da4fdd3edf64d84bd14"
)
EXPECTED_PARENT_PRODUCT_DIGEST = (
    "22266084469c53df1fdf3e583fec6f1727a6e543ac158ea78e4c2fc74e1f3318"
)
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "e155fd6fbdbfc78a9c8c5a006d335a365b536b308ac1e7c8c68a3e4c4a0c2374"
)
EXPECTED_PARENT_TARGET_DIGEST = q011cg.EXPECTED_PARENT_TARGET_DIGEST
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "695ea79d90eb41053f8a299b16958af0f114f5cc6df67a31ce5c50bf49fd16ba"
)
EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST = (
    "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"
)

Q011CH_ARTIFACT_SHA256 = "26941b40908a64c32ec529a996a687fe64d9257d993faecf45619712fb38a4bd"
Q011CH_RUNNER_SHA256 = "17f85796df17fc8cc06f961421ad5a76fa19af7502d22fd552c4315227774c24"
Q011CH_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011CH_DIGESTS = (
    "0501ac79003012b0bc0eed0ba358e161bbd58985b719c2ed559f25dce87a6d98",
    "374f286a7b816058d445fe5e80b04fdb6d84f31538c1e9fe335d29fca7b00364",
    "b8757924d92579525263a161ac7b6416690f2a139d2292dfac212c41a2c29136",
    "a5079f4feecc58031ffee55ec2638f2822131423c3917d81741ec20c03c4cd67",
    "328aae2da9afbfe8d69e919cddf0d9459b1c921ac546f2b6f7ee19044c10b322",
)
EXPECTED_Q011CH_STREAM_DIGEST = (
    "ff113285c032296966864a9cb8984527a516d75583b7e4d7e1462e2255a10ba2"
)

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the fourth Q011cb witness"
)
RESOLVED_CLASSIFICATION = "the fourth Q011cb witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the fourth Q011cb witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ci individual-disc partition audit is inconclusive"

_PROTOCOL_OVERRIDES: dict[str, Any] = {
    "PARENT_FLAT_ORDINAL": PARENT_FLAT_ORDINAL,
    "PARENT_LEFT_INDEX": PARENT_LEFT_INDEX,
    "PARENT_RIGHT_INDEX": PARENT_RIGHT_INDEX,
    "PARENT_CLASS_COUNTS": PARENT_CLASS_COUNTS,
    "OCCUPIED_SPEC": OCCUPIED_SPEC,
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
    "EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY": (
        EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY
    ),
    "EXPECTED_PARENT_INTERSECTION_WIDTH_HEX": (
        EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    ),
    "EXPECTED_PARENT_CENTER_RELATION": EXPECTED_PARENT_CENTER_RELATION,
    "EXPECTED_PARENT_CENTER_GAP_HEX": EXPECTED_PARENT_CENTER_GAP_HEX,
    "EXPECTED_PARENT_WITNESS_DIGEST": EXPECTED_PARENT_WITNESS_DIGEST,
    "INERT_CLASSIFICATION": INERT_CLASSIFICATION,
    "RESOLVED_CLASSIFICATION": RESOLVED_CLASSIFICATION,
    "EFFECTIVE_PERSISTENT_CLASSIFICATION": EFFECTIVE_PERSISTENT_CLASSIFICATION,
    "INCONCLUSIVE_CLASSIFICATION": INCONCLUSIVE_CLASSIFICATION,
}
_PROTOCOL_BASELINE = {
    name: getattr(q011cg, name) for name in _PROTOCOL_OVERRIDES
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
    original = {name: getattr(q011cg, name) for name in _PROTOCOL_OVERRIDES}
    try:
        for name, value in _PROTOCOL_OVERRIDES.items():
            setattr(q011cg, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(q011cg, name, value)


def _protocol_globals_are_restored() -> bool:
    return all(
        getattr(q011cg, name) == value
        for name, value in _PROTOCOL_BASELINE.items()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011ch._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011ch_degree34_third_component_safe_phase_discs.json"
    )
    runner_path = Path(q011ch.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CH_DIGEST_NAMES)
    checks = {
        "q011ch_sixty_four_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 64
            and prior["direct_digest_count"] == 300
            and len(artifacts) == 64
            and all(prior["checks"].values())
        ),
        "q011ch_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CH_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CH_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CH_RUNNER_SHA256
        ),
        "q011ch_section_digests_match": digests == Q011CH_DIGESTS,
        "q011ch_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "component_safe_complex_phase_discs_resolve_third_q011cb_witness"
            ]
            and theorem["q011cf_ordinal_one_phase_resolution_is_preserved"]
            and theorem["q011cd_ordinal_zero_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011ch_registered_ordinal_two_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 18_718
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 18_718,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"]
            == EXPECTED_Q011CH_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011ch_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_five_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 305
        ),
    }
    artifacts["q011ch"] = artifact
    return (
        {
            "prior_q011ch_sealed_input_audit": prior,
            "q011ch": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CH_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (
                    EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST
                ),
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


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
    selection["previous_phase_resolved_ordinals"] = [0, 1, 2]
    selection["ordinal_two_resolution_digest_sha256"] = (
        EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST
    )
    selection["checks"]["ordinal_two_is_the_sealed_q011ch_phase_resolution"] = bool(
        artifacts["q011ch"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_third_q011cb_witness"
        ]
        and artifacts["q011ch"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST
    )
    selection["checks"]["registered_ordinal_three_parent_witness_reproduces"] = (
        selection["checks"].pop("registered_ordinal_two_parent_witness_reproduces")
    )
    selection["fourth_parent_witness"] = selection.pop("third_parent_witness")
    selection["fourth_parent_witness_digest_sha256"] = selection.pop(
        "third_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["fourth_parent_witness_selection_audit"] = selection
    fixed["checks"]["registered_fourth_parent_selection_reproduces"] = fixed[
        "checks"
    ].pop("registered_third_parent_selection_reproduces")
    fixed["checks"]["q011cg_protocol_globals_are_restored"] = (
        _protocol_globals_are_restored()
    )
    fixed["passed"] = all(fixed["checks"].values())
    return fixed, lookup, compatible, parent


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    with _q011cg_protocol_context():
        partition = q011cg._individual_partition_audit(lookup, compatible, parent)
    partition["checks"]["q011cg_protocol_globals_are_restored"] = (
        _protocol_globals_are_restored()
    )
    partition["passed"] = all(partition["checks"].values())
    return partition


def _registered_parameters() -> dict[str, Any]:
    with _q011cg_protocol_context():
        registered = q011cg._registered_parameters()
    registered["q011cg_protocol_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011cg.__file__).resolve()),
        "temporary_override_names": sorted(_PROTOCOL_OVERRIDES),
        "globals_restored_after_use": _protocol_globals_are_restored(),
    }
    return registered


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "partition_input_digest_sha256": cycle["partition_input_digest_sha256"],
        "allocation_audit_digest_sha256": cycle["allocation_audit_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "diagnostic_gates": cycle["diagnostic_gates"],
        "study_validity": cycle["study_validity"],
        "refinement_outcome": cycle["refinement_outcome"],
        "diagnostic_classification": cycle["diagnostic_classification"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_thirty_four_fourth_individual_partition_audit() -> dict[str, Any]:
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
    selection = fixed["fourth_parent_witness_selection_audit"]
    validity_gates = {
        "q011ch_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "65 artifacts and 305 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_fourth_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 3, class counts, 945 multiplicity and exact witness",
            "value": selection["fourth_parent_witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "five occupied pairs, ten identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "16800 total and 945 output-block-7 compatible allocations",
            "value": {
                "full": fixed["full_allocation_count"],
                "compatible": fixed["compatible_allocation_count"],
            },
        },
        "all_count_degree_and_output_constraints_close": {
            "passed": bool(
                fixed[
                    "compatible_allocations_exactly_partition_parent_wave_multiplicity"
                ]
                and partition["checks"][
                    "all_degree_and_output_block_constraints_close"
                ]
            ),
            "threshold": "945 unit allocations, degree 34 and output block 7",
            "value": partition["compatible_allocation_count"],
        },
        "all_exact_interval_and_classification_invariants_pass": {
            "passed": partition["passed"],
            "threshold": "exact/outward exclusive relations and strict finite records",
            "value": partition["checks"],
        },
        "strict_section_digests_runner_and_protocol_provenance_reproduce": {
            "passed": bool(
                len(input_digest) == len(partition_digest) == len(allocation_digest) == 64
                and runner["filename"]
                == "q011ci_degree34_fourth_individual_partition_audit.py"
                and partition["first_allocation_record"] is not None
                and partition["last_allocation_record"] is not None
                and _protocol_globals_are_restored()
            ),
            "threshold": (
                "three section digests, endpoint records, runner and restored protocol"
            ),
            "value": {
                "input": input_digest,
                "partition": partition_digest,
                "allocation": allocation_digest,
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
            record["exact_gap_positive"] and record["binary64_outward_gap_positive"]
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
        "only_the_registered_fourth_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 3 only, one target and no other aggregate",
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
            "threshold": "945 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 3 into ten singleton identifiers "
            "change any compatible exact product interval or classification?"
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
        "actual_resonance_outcome": "not_established",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_fourth_q011cb_witness": inert,
        "fourth_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_fourth_q011cb_witness_persists": (
            effective_persistent
        ),
        "q011ch_ordinal_two_phase_resolution_is_preserved": True,
        "q011cf_ordinal_one_phase_resolution_is_preserved": True,
        "q011cd_ordinal_zero_phase_resolution_is_preserved": True,
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
        "This diagnostic concerns only Q011cb flatten ordinal 3, its 945 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 2 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44796 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cj to expand only the 945 registered wave allocations into "
        "component-safe complex phase discs."
        if inert
        else "Preregister Q011cj for the next Q011cb refined overlap."
        if resolved
        else "Preregister Q011cj to apply component-safe complex phase discs only to "
        "the first remaining individual overlap."
        if effective_persistent
        else "Repair only the first Q011ci validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011ci cycle failed strict serialization or digest")
    return cycle


def run_q011ci_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_fourth_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "ten registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "full_allocation_target_matrix_retained": False,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "fourth Q011cb witness individual-disc partition invariance",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
            "target_identifier": TARGET_IDENTIFIER,
            "complex_phase_claim": False,
            "degree_thirty_four_nonresonance_claim": False,
            "actual_resonance_claim": False,
            "all_order_nonresonance_claim": False,
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
    result = run_q011ci_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
