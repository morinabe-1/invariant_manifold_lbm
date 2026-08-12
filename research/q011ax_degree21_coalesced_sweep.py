"""Q011ax block-support-coalesced degree-twenty-one nonresonance audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011aw_degree21_resource_estimate as q011aw
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011av = q011aw.q011av
q011an = q011av.q011an
q011b = q011aw.q011b
q011z = q011aw.q011z

SIZE = 17
DEGREE = 21

EXPECTED_DEGREE_AGGREGATE_COUNT = 2_024
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 1_660
EXPECTED_OVERLAP_AGGREGATE_COUNT = 364
EXPECTED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_TARGET_IDENTIFIER_COUNT = 228
EXPECTED_FINAL_IDENTIFIER_COUNT = 252
EXPECTED_MERGED_CLASS_COUNTS = (1, 1, 2, 2)
EXPECTED_CLASS_POWER_COUNT = 121
EXPECTED_GROUP_SIGNATURE_COUNT = 482
EXPECTED_PAIR_POOL_KEY_COUNT = 192
EXPECTED_CONVOLUTION_CALL_COUNT = 6_448
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 294_674_427_372
EXPECTED_MODULUS_SIGNATURE_COUNT = 12_458
EXPECTED_PEAK_LIVE_SIGNATURE_COUNT = 126
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 2_016
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 146_928
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 3_951_865_509_552
EXPECTED_SAFE_INT64_CRUDE_BOUND = 133_491_072_000

ACCEPTED_CLASSIFICATION = (
    "the block-support-coalesced component-safe sweep certifies degree-21 "
    "external nonresonance"
)
REJECTED_CLASSIFICATION = (
    "the block-support-coalesced degree-21 sufficient certificate is rejected"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ax degree-21 coalesced audit is inconclusive"
ACCEPTED_ACTUAL_RESONANCE_OUTCOME = (
    "ruled_out_within_registered_degree_twenty_one_scope"
)

Q011AW_ARTIFACT_SHA256 = "0228b387f0308e98051085bdf68e16c7baef4326467c102e152e7ae3f189425e"
Q011AW_RUNNER_SHA256 = "ece845c00b7a49bd9bd12e7c30b763150d18b64fa68539b03c43c3748ca827cc"
Q011AW_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "envelope_digest_sha256",
    "resource_digest_sha256",
    "result_digest_sha256",
)
Q011AW_DIGESTS = (
    "9e76ca9a07ca6eb442a9fdb397f72ace03084f7e3f2c0b30fa312660c49455c2",
    "2d1cdd3aaff4b3b224b212b8baf719293ce4595552a2da40da54d7e3592af0ce",
    "e4e7435a47e12a262a7ca6f2fc56125d4d18cbf3f0c0b348f3ff6cbee3c2ad49",
    "16ae0966509a3f9d4a608b025dfac11de996f9613e1a2f8f198a41e495d5f488",
    "599143be7991dbebfe6f2da0cc1d3883d5a83985e02fd3685a71cca82aae3f71",
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
    prior, artifacts = q011aw._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011aw_degree21_resource_estimate.json"
    runner_path = Path(q011aw.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AW_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    resource = cycle["degree_twenty_one_coalesced_resource_audit"]
    checks = {
        "q011aw_twenty_seven_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 135
            and len(artifacts) == 27
            and all(prior["checks"].values())
        ),
        "q011aw_artifact_sha256_matches": _file_sha256(artifact_path)
        == Q011AW_ARTIFACT_SHA256,
        "q011aw_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AW_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AW_RUNNER_SHA256
        ),
        "q011aw_section_digests_match": digests == Q011AW_DIGESTS,
        "q011aw_registered_resource_go_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["resource_decision"] == q011aw.GO_DECISION
            and artifact["scientific_outcome"] == q011aw.SCIENTIFIC_OUTCOME
            and artifact["actual_resonance_outcome"] == q011aw.ACTUAL_RESONANCE_OUTCOME
            and cycle["failed_validity_order"] == []
            and cycle["failed_resource_limit_order"] == []
            and theorem[
                "degree_twenty_one_coalesced_full_sweep_preregistration_is_resource_supported"
            ]
            and not theorem["degree_twenty_one_external_nonresonance_is_certified"]
            and resource["product_target_relation_evaluation_count"] == 0
        ),
        "q011aw_preserves_q011av_accepted_certificate": bool(
            theorem["q011av_degree_twenty_certificate_is_preserved"]
            and artifacts["q011av"]["scientific_outcome"] == "accepted"
            and artifacts["q011av"]["cycle"]["theorem_consequence"][
                "degree_twenty_external_nonresonance_is_certified"
            ]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 21))
            and theorem["missing_external_nonresonance_degrees"] == list(range(21, 91))
        ),
        "q011aw_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011aw_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011aw_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_forty_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 140
        ),
    }
    artifacts["q011aw"] = artifact
    return (
        {
            "prior_q011aw_sealed_input_audit": prior,
            "q011aw": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AW_DIGEST_NAMES),
                "digests": list(digests),
                "resource_decision": cycle["resource_decision"],
                "degree_twenty_one_relation_evaluation_count": resource[
                    "product_target_relation_evaluation_count"
                ],
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _fixed_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
    dict[str, q011z._UniformDisc],
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[str, ...], ...],
]:
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        external_indices,
        target_groups,
    ) = q011aw._degree_twenty_one_inventory_audit(artifacts)
    envelope, merged_classes, hull_lookup = q011aw._degree_twenty_one_envelope_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = q011aw._degree_twenty_one_resource_audit(
        merged_classes, selected_groups, overlap_counts, target_groups
    )
    stored_cycle = artifacts["q011aw"]["cycle"]
    stored_inventory = stored_cycle["degree_twenty_one_inventory_audit"]
    stored_envelope = stored_cycle["degree_twenty_one_envelope_audit"]
    stored_resource = stored_cycle["degree_twenty_one_coalesced_resource_audit"]
    selected_identifiers = set().union(*map(set, selected_groups))
    target_identifiers = set().union(*map(set, target_groups))
    checks = {
        "q011aw_degree_twenty_one_inventory_recomputes_bitwise": bool(
            inventory["passed"] and inventory == stored_inventory
        ),
        "q011aw_degree_twenty_one_envelope_recomputes_bitwise": bool(
            envelope["passed"] and envelope == stored_envelope
        ),
        "q011aw_degree_twenty_one_resource_contract_recomputes_bitwise": bool(
            resource["passed"] and resource == stored_resource
        ),
        "registered_inventory_and_identifier_counts_reproduce": bool(
            inventory["degree_aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and inventory["old_modulus_separated_aggregate_count"]
            == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and inventory["old_modulus_overlap_aggregate_count"]
            == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(selected_identifiers) == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and len(target_identifiers) == EXPECTED_TARGET_IDENTIFIER_COUNT
            and len(selected_identifiers | target_identifiers) == EXPECTED_FINAL_IDENTIFIER_COUNT
        ),
        "registered_hull_membership_reproduces": bool(
            envelope["merged_source_class_counts"] == list(EXPECTED_MERGED_CLASS_COUNTS)
            and envelope["source_hull_record_digest_sha256"]
            == q011aw.EXPECTED_HULL_RECORD_DIGEST
            and envelope["source_merged_membership_digest_sha256"]
            == q011aw.EXPECTED_MERGED_MEMBERSHIP_DIGEST
        ),
        "all_targets_are_retained_without_folding": bool(
            not envelope["target_lookup_changed"]
            and envelope["external_target_identifier_count"]
            == EXPECTED_TARGET_IDENTIFIER_COUNT
            and envelope["product_target_relation_evaluation_count"] == 0
        ),
        "fixed_inputs_are_finite_strict_json": bool(
            _all_numeric_values_finite(inventory)
            and _all_numeric_values_finite(envelope)
            and _strict_json_serializable(inventory)
            and _strict_json_serializable(envelope)
            and json.dumps({"inventory": inventory, "envelope": envelope}, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_aggregate_count": inventory["degree_aggregate_count"],
        "old_modulus_separated_aggregate_count": inventory[
            "old_modulus_separated_aggregate_count"
        ],
        "direct_overlap_aggregate_count": inventory["old_modulus_overlap_aggregate_count"],
        "selected_identifier_count": len(selected_identifiers),
        "target_identifier_count": len(target_identifiers),
        "final_identifier_count": len(selected_identifiers | target_identifiers),
        "merged_class_counts": envelope["merged_source_class_counts"],
        "inventory_digest_sha256": inventory["exact_inventory_digest_sha256"],
        "final_disc_record_digest_sha256": envelope["final_disc_record_digest_sha256"],
        "hull_record_digest_sha256": envelope["source_hull_record_digest_sha256"],
        "merged_class_membership_digest_sha256": envelope[
            "source_merged_membership_digest_sha256"
        ],
        "resource_result_digest_sha256": q011b._canonical_json_sha256(resource),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        merged_classes,
        hull_lookup,
        overlap_counts,
        external_indices,
        target_groups,
    )


def _registered_full_sweep(
    merged_classes: tuple[tuple[tuple[str, ...], ...], ...],
    hull_lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_indices: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    sweep = dict(
        q011an._full_component_safe_sweep(
            merged_classes,
            hull_lookup,
            overlap_counts,
            external_indices,
            target_groups,
        )
    )
    sweep["degree"] = DEGREE
    total_target_comparison_upper = sum(
        record["modulus_signature_count"] * record["target_identifier_count"]
        for record in sweep["aggregate_records"]
    )
    total_weighted_comparison_upper = sum(
        record["original_monomial_count"] * record["target_identifier_count"]
        for record in sweep["aggregate_records"]
    )
    all_invariants = all(
        sweep[name]
        for name in (
            "all_convolutions_nonnegative",
            "all_convolution_fiber_sums_exact",
            "all_product_bound_arrays_are_finite",
            "all_product_bound_arrays_are_nonnegative_and_ordered",
            "all_original_monomial_counts_match_multiset_coefficients",
            "all_modulus_signature_counts_match_weak_compositions",
        )
    )
    checks = {
        "all_registered_aggregates_are_processed_once": bool(
            sweep["audited_overlap_aggregate_count"] == len(overlap_counts)
            == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(sweep["aggregate_records"]) == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and [record["aggregate_index"] for record in sweep["aggregate_records"]]
            == list(range(EXPECTED_OVERLAP_AGGREGATE_COUNT))
        ),
        "registered_factorization_resources_reproduce": bool(
            sweep["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and sweep["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
            and sweep["pair_pool_record_count"] == EXPECTED_PAIR_POOL_KEY_COUNT
            and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
        ),
        "registered_monomial_signature_and_peak_resources_reproduce": bool(
            sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and sweep["maximum_live_combined_signature_count"]
            == EXPECTED_PEAK_LIVE_SIGNATURE_COUNT
            and 2 * 8 * sweep["maximum_live_combined_signature_count"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
        ),
        "registered_comparison_upper_bounds_reproduce": bool(
            total_target_comparison_upper == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and total_weighted_comparison_upper == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            and sweep["distinct_comparison_count"] <= total_target_comparison_upper
            and sweep["weighted_comparison_count"] <= total_weighted_comparison_upper
        ),
        "all_integer_and_outward_interval_invariants_hold": bool(
            all_invariants
            and sweep["maximum_convolution_crude_int64_bound"]
            <= EXPECTED_SAFE_INT64_CRUDE_BOUND
            and sweep["maximum_fourier_crude_int64_bound"] < 2**63
        ),
        "matrix_summaries_and_witnesses_are_present": bool(
            sweep["bound_matrix_record_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and sweep["coefficient_matrix_record_count"] > 0
            and sweep["classification_matrix_record_count"] > 0
            and sweep["global_minimum_separated_witness"] is not None
        ),
        "full_sweep_is_finite_strict_json": bool(
            _all_numeric_values_finite(sweep)
            and _strict_json_serializable(sweep)
            and json.dumps(sweep, allow_nan=False)
        ),
    }
    return {
        **sweep,
        "distinct_comparison_upper_bound": total_target_comparison_upper,
        "weighted_comparison_upper_bound": total_weighted_comparison_upper,
        "registered_checks": checks,
        "registered_passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "direct_overlap_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
        "selected_identifier_count": EXPECTED_SELECTED_IDENTIFIER_COUNT,
        "target_identifier_count": EXPECTED_TARGET_IDENTIFIER_COUNT,
        "merged_class_counts": list(EXPECTED_MERGED_CLASS_COUNTS),
        "target_folding_used": False,
        "target_merge_used": False,
        "full_monomial_list_retained": False,
        "full_classification_matrices_retained": False,
        "accepted_classification": ACCEPTED_CLASSIFICATION,
        "rejected_classification": REJECTED_CLASSIFICATION,
        "actual_resonance_outcome_if_accepted": ACCEPTED_ACTUAL_RESONANCE_OUTCOME,
        "degree_twenty_two_or_higher_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "preparation_digest_sha256": cycle["preparation_digest_sha256"],
        "sweep_digest_sha256": cycle["sweep_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "scientific_outcome": cycle["scientific_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_twenty_one_coalesced_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        fixed,
        merged_classes,
        hull_lookup,
        overlap_counts,
        external_indices,
        target_groups,
    ) = _fixed_input_audit(artifacts)
    sweep = _registered_full_sweep(
        merged_classes, hull_lookup, overlap_counts, external_indices, target_groups
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    preparation_sections = {"fixed_coalesced_input_audit": fixed}
    sweep_sections = {"degree_twenty_one_block_support_coalesced_sweep": sweep}
    input_digest = q011b._canonical_json_sha256(input_sections)
    preparation_digest = q011b._canonical_json_sha256(preparation_sections)
    sweep_digest = q011b._canonical_json_sha256(sweep_sections)
    minimum = sweep["global_minimum_separated_witness"]
    first_overlap = sweep["first_unresolved_witness"]
    minimum_outward_positive = bool(
        minimum
        and minimum["relation"] != "overlap"
        and minimum["outward_gap_lower"]["float"] > 0
    )
    minimum_exact_positive = bool(
        minimum
        and minimum["relation"] != "overlap"
        and q011z._fraction(minimum["exact_gap"]) > 0
    )
    validity_gates = {
        "q011aw_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "28 artifacts and 140 direct digests reproduce",
            "value": sealed["checks"],
        },
        "fixed_inventory_hulls_targets_and_resource_contract_reproduce": {
            "passed": fixed["passed"],
            "threshold": "registered inventory, six hulls, all targets and resource identity",
            "value": fixed["checks"],
        },
        "all_registered_aggregates_and_arithmetic_invariants_pass": {
            "passed": sweep["registered_passed"],
            "threshold": "364 aggregates, exact integer convolutions and outward arrays",
            "value": sweep["registered_checks"],
        },
        "registered_resource_counts_reproduce": {
            "passed": bool(
                sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
                and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
                and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
                and sweep["maximum_live_combined_signature_count"]
                == EXPECTED_PEAK_LIVE_SIGNATURE_COUNT
                and sweep["distinct_comparison_upper_bound"]
                == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
                and sweep["weighted_comparison_upper_bound"]
                == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            ),
            "threshold": "all preregistered degree-21 coalesced resource identities",
            "value": {
                "original_monomial_count": sweep["original_monomial_count"],
                "modulus_signature_count": sweep["modulus_signature_count"],
                "convolution_call_count": sweep["convolution_call_count"],
                "peak_live_signature_count": sweep[
                    "maximum_live_combined_signature_count"
                ],
            },
        },
        "matrix_summaries_are_strict_and_digestible": {
            "passed": bool(
                sweep["bound_matrix_record_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
                and sweep["coefficient_matrix_record_count"] > 0
                and sweep["classification_matrix_record_count"] > 0
                and len(sweep["bound_matrix_digest_sha256"]) == 64
                and len(sweep["coefficient_matrix_digest_sha256"]) == 64
                and len(sweep["classification_matrix_digest_sha256"]) == 64
            ),
            "threshold": "aggregate, bound, coefficient and classification streams are sealed",
            "value": {
                "aggregate": sweep["aggregate_record_digest_sha256"],
                "bound": sweep["bound_matrix_digest_sha256"],
                "coefficient": sweep["coefficient_matrix_digest_sha256"],
                "classification": sweep["classification_matrix_digest_sha256"],
            },
        },
        "registered_witness_protocol_is_satisfied": {
            "passed": bool(
                minimum is not None
                and (first_overlap is None or first_overlap["relation"] == "overlap")
            ),
            "threshold": "global separated minimum and optional first overlap exact witness",
            "value": {
                "minimum_witness_digest": minimum["witness_digest_sha256"],
                "first_overlap_witness_digest": (
                    first_overlap["witness_digest_sha256"] if first_overlap else None
                ),
            },
        },
        "q011av_certificate_sections_and_runner_provenance_reproduce": {
            "passed": bool(
                artifacts["q011av"]["scientific_outcome"] == "accepted"
                and artifacts["q011av"]["cycle"]["theorem_consequence"][
                    "degree_twenty_external_nonresonance_is_certified"
                ]
                and len(input_digest) == len(preparation_digest) == len(sweep_digest) == 64
                and runner["filename"] == "q011ax_degree21_coalesced_sweep.py"
            ),
            "threshold": "degree-20 certificate, three section digests and runner metadata",
            "value": {
                "input": input_digest,
                "preparation": preparation_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "six_hulls_cover_sources_and_all_targets_are_preserved": {
            "passed": bool(
                fixed["merged_class_counts"] == list(EXPECTED_MERGED_CLASS_COUNTS)
                and fixed["selected_identifier_count"] == EXPECTED_SELECTED_IDENTIFIER_COUNT
                and fixed["target_identifier_count"] == EXPECTED_TARGET_IDENTIFIER_COUNT
            ),
            "threshold": "six source hulls, 24 selected identifiers and 228 unchanged targets",
            "value": fixed["checks"],
        },
        "every_direct_comparison_is_strictly_separated": {
            "passed": sweep["distinct_relation_counts"]["overlap"] == 0,
            "threshold": "every compatible comparison has overlap count zero",
            "value": sweep["distinct_relation_counts"],
        },
        "old_and_direct_aggregates_cover_degree_twenty_one": {
            "passed": bool(
                EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
                + sweep["fully_separated_overlap_aggregate_count"]
                == EXPECTED_DEGREE_AGGREGATE_COUNT
            ),
            "threshold": "1660 preserved plus 364 direct equals 2024",
            "value": {
                "old": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
                "direct": sweep["fully_separated_overlap_aggregate_count"],
            },
        },
        "global_minimum_outward_and_exact_gaps_are_positive": {
            "passed": minimum_outward_positive and minimum_exact_positive,
            "threshold": "strictly positive outward and exact rational minimum gap",
            "value": {
                "outward": minimum["outward_gap_lower"],
                "exact_gap_hex": minimum.get("exact_gap_hex"),
            },
        },
        "claim_is_limited_to_registered_degree_twenty_one_scope": {
            "passed": True,
            "threshold": "no degree 22--90, all-order, SSM or basin extrapolation",
            "value": "fixed 17x17 leaf and registered degree-21 external relation only",
        },
    }
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    accepted = validity_passed and hypothesis_passed
    rejected = validity_passed and not hypothesis_passed
    classification = (
        ACCEPTED_CLASSIFICATION
        if accepted
        else REJECTED_CLASSIFICATION
        if rejected
        else INCONCLUSIVE_CLASSIFICATION
    )
    scientific_outcome = "accepted" if accepted else "rejected" if rejected else "inconclusive"
    actual_resonance_outcome = (
        ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        if accepted
        else "not_established"
        if rejected
        else "not_evaluated"
    )
    cycle = {
        "question": (
            "Does the preregistered block-support-coalesced component-safe sweep separate "
            "every degree-twenty-one external product-target relation?"
        ),
        **input_sections,
        **preparation_sections,
        **sweep_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "preparation_digest_sha256": preparation_digest,
        "sweep_digest_sha256": sweep_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_validity_order": [
            name for name, gate in validity_gates.items() if not gate["passed"]
        ],
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "scientific_outcome": scientific_outcome,
        "scientific_classification": classification,
        "actual_resonance_outcome": actual_resonance_outcome,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    certified_degrees = list(range(2, 22)) if accepted else list(range(2, 21))
    missing_degrees = list(range(22, 91)) if accepted else list(range(21, 91))
    cycle["theorem_consequence"] = {
        "degree_twenty_one_external_nonresonance_is_certified": accepted,
        "an_actual_degree_twenty_one_external_resonance_is_ruled_out": accepted,
        "registered_degree_twenty_one_sufficient_certificate_is_rejected": rejected,
        "certified_external_nonresonance_degrees": certified_degrees,
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": missing_degrees,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011av_degree_twenty_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only the registered degree-twenty-one external "
        "product-target relations for the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf, using the six Q011as source hulls, all 228 Q011aw target "
        "discs, exact Fourier multiplicities and outward-rounded hierarchical product "
        "intervals. It makes no claim for degrees 22--90, all-order nonresonance, higher "
        "graph smoothness, SSM existence or uniqueness, normal attraction, a basin, "
        "other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Run a design-only Q011ay degree-twenty-two resource estimate before "
        "preregistering any degree-twenty-two full sweep."
        if accepted
        else "Audit only the first registered degree-twenty-one overlap witness before "
        "changing any hull or target representation."
        if rejected
        else "Repair only the first Q011ax validity failure before changing the sweep."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ax cycle failed strict serialization or digest")
    return cycle


def run_q011ax_study() -> dict[str, Any]:
    cycle = run_degree_twenty_one_coalesced_audit()
    sweep = cycle["degree_twenty_one_block_support_coalesced_sweep"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_hulls": "exact rational endpoint hulls fixed by Q011as",
            "product_enclosure": "outward-rounded binary64 hierarchical products",
            "fourier_multiplicity": "exact int64 cyclic convolution",
            "target_comparisons": "all 228 registered target discs without folding",
            "full_monomial_list_retained": False,
            "full_classification_matrices_retained": False,
            "convolution_call_count": sweep["convolution_call_count"],
            "peak_live_signature_count": sweep["maximum_live_combined_signature_count"],
        },
        "mathematical_scope": {
            "diagnostic": "degree-21 block-support-coalesced external nonresonance",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_twenty_two_or_higher_claim": False,
            "all_order_nonresonance_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011ax_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
