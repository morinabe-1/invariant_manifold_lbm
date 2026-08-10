"""Q011aq component-safe hierarchical degree-eighteen nonresonance audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011ap_degree18_resource_estimate as q011ap
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011an = q011ap.q011ao.q011an
q011b = q011ap.q011b
q011z = q011ap.q011z

SIZE = 17
DEGREE = 18

EXPECTED_DEGREE_AGGREGATE_COUNT = 1_330
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 1_078
EXPECTED_OVERLAP_AGGREGATE_COUNT = 252
EXPECTED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_TARGET_IDENTIFIER_COUNT = 164
EXPECTED_FINAL_IDENTIFIER_COUNT = 188
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_CLASS_POWER_COUNT = 268
EXPECTED_GROUP_SIGNATURE_COUNT = 139_922
EXPECTED_PAIR_POOL_KEY_COUNT = 125
EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT = 1_450_127
EXPECTED_CONVOLUTION_CALL_COUNT = 2_277_951
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 50_931_347_136
EXPECTED_MODULUS_SIGNATURE_COUNT = 112_289_821
EXPECTED_PEAK_LIVE_SIGNATURE_COUNT = 2_102_100
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 33_633_600
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 996_565_068
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 485_076_664_408
EXPECTED_SAFE_INT64_CRUDE_BOUND = 20_023_660_800

ACCEPTED_CLASSIFICATION = (
    "the component-safe hierarchical sweep certifies degree-18 external nonresonance"
)
REJECTED_CLASSIFICATION = (
    "the component-safe hierarchical degree-18 sufficient certificate is rejected"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011aq degree-18 hierarchical audit is inconclusive"
ACCEPTED_ACTUAL_RESONANCE_OUTCOME = "ruled_out_within_registered_degree_eighteen_scope"

Q011AP_ARTIFACT_SHA256 = "e0e50ce2ffbfd94389d7e446948fe4a04b7a9aac47213ba8a5ec0717aa78317b"
Q011AP_RUNNER_SHA256 = "1a3049db74228754189b8abaf7514ac28780260e9e5d18629589d415628ab313"
Q011AP_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "envelope_digest_sha256",
    "resource_digest_sha256",
    "result_digest_sha256",
)
Q011AP_DIGESTS = (
    "e39b183a97916bb1c108a23ea6cf9ae3328f7423c8d83199154f37e4e1dc306c",
    "ffc0d158333068d535a71f2dbb1cfaec3d495c7a2ee169dda9aff5cf07727141",
    "9cdc661ff2354b1dfb7655c5819ec7ecdb655dd8369886af0609cc7df3b68379",
    "87679bf4427084316b0686cf362c03e25fdb0b7f57be01f9fd34d310381c386b",
    "90139ef58140152924ba0629094dd21099ef0d4df05f26651a719d1877c181d4",
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
    prior, artifacts = q011ap._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ap_degree18_resource_estimate.json"
    runner_path = Path(q011ap.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AP_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    checks = {
        "q011ap_twenty_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 103
            and len(artifacts) == 20
            and all(prior["checks"].values())
        ),
        "q011ap_artifact_sha256_matches": _file_sha256(artifact_path) == Q011AP_ARTIFACT_SHA256,
        "q011ap_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AP_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AP_RUNNER_SHA256
        ),
        "q011ap_digests_match": digests == Q011AP_DIGESTS,
        "q011ap_registered_resource_go_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["resource_decision"] == q011ap.GO_DECISION
            and artifact["scientific_outcome"] == q011ap.SCIENTIFIC_OUTCOME
            and artifact["actual_resonance_outcome"] == q011ap.ACTUAL_RESONANCE_OUTCOME
            and theorem["degree_eighteen_full_sweep_preregistration_is_resource_supported"]
            and not theorem["degree_eighteen_external_nonresonance_is_certified"]
            and theorem["missing_external_nonresonance_degrees"] == list(range(18, 91))
        ),
        "q011ap_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ap_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ap_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 108
        ),
    }
    artifacts["q011ap"] = artifact
    return (
        {
            "prior_q011ap_sealed_input_audit": prior,
            "q011ap": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AP_DIGEST_NAMES),
                "digests": list(digests),
                "resource_decision": cycle["resource_decision"],
                "scientific_outcome": cycle["scientific_outcome"],
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
    dict[str, q011z._UniformDisc],
    tuple[tuple[tuple[str, ...], ...], ...],
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
    ) = q011ap._degree_eighteen_inventory_audit(artifacts)
    envelope, lookup, classes = q011ap._degree_eighteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = q011ap._degree_eighteen_resource_audit(
        classes, selected_groups, overlap_counts, target_groups
    )
    stored_cycle = artifacts["q011ap"]["cycle"]
    stored_inventory = stored_cycle["degree_eighteen_inventory_audit"]
    stored_envelope = stored_cycle["degree_eighteen_envelope_inventory_audit"]
    stored_resource = stored_cycle["degree_eighteen_hierarchical_resource_audit"]
    checks = {
        "q011ap_inventory_recomputes_bitwise": bool(
            inventory["passed"] and inventory == stored_inventory
        ),
        "q011ap_envelope_recomputes_bitwise": bool(
            envelope["passed"] and envelope == stored_envelope
        ),
        "q011ap_resource_contract_recomputes_bitwise": bool(
            resource["passed"] and resource == stored_resource
        ),
        "registered_inventory_counts_reproduce": bool(
            inventory["degree_aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and inventory["old_modulus_separated_aggregate_count"]
            == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and inventory["old_modulus_overlap_aggregate_count"]
            == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(overlap_counts) == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(external_indices) == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(target_groups) == EXPECTED_OVERLAP_AGGREGATE_COUNT
        ),
        "registered_envelope_counts_reproduce": bool(
            envelope["selected_source_identifier_count"] == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and envelope["external_target_identifier_count"] == EXPECTED_TARGET_IDENTIFIER_COUNT
            and envelope["final_identifier_count"] == EXPECTED_FINAL_IDENTIFIER_COUNT
            and tuple(envelope["selected_modulus_class_counts"]) == EXPECTED_CLASS_COUNTS
            and tuple(map(len, classes)) == EXPECTED_CLASS_COUNTS
        ),
        "registered_resource_identity_reproduces": bool(
            resource["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and resource["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
            and resource["pair_pool_cache_key_count"] == EXPECTED_PAIR_POOL_KEY_COUNT
            and resource["cached_pair_signature_entry_count"]
            == EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT
            and resource["exact_convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
            and resource["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and resource["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and resource["peak_live_combined_signature_count"]
            == EXPECTED_PEAK_LIVE_SIGNATURE_COUNT
            and resource["peak_two_product_bound_array_bytes"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
            and resource["distinct_comparison_upper_bound"]
            == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and resource["weighted_comparison_upper_bound"]
            == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
        ),
        "label_safe_disc_logic_is_preserved": bool(
            envelope["product_target_relation_evaluation_count"] == 0
            and envelope["checks"]["selected_and_target_intervals_are_q011u_contained"]
            and envelope["checks"]["q011ao_reused_modulus_records_are_bitwise_identical"]
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_aggregate_count": inventory["degree_aggregate_count"],
        "old_modulus_separated_aggregate_count": inventory[
            "old_modulus_separated_aggregate_count"
        ],
        "direct_overlap_inventory_aggregate_count": inventory[
            "old_modulus_overlap_aggregate_count"
        ],
        "selected_source_identifier_count": envelope["selected_source_identifier_count"],
        "external_target_identifier_count": envelope["external_target_identifier_count"],
        "final_identifier_count": envelope["final_identifier_count"],
        "selected_modulus_class_counts": envelope["selected_modulus_class_counts"],
        "overlap_count_tuple_digest_sha256": inventory[
            "overlap_count_tuple_digest_sha256"
        ],
        "external_group_index_tuple_digest_sha256": inventory[
            "external_group_index_tuple_digest_sha256"
        ],
        "exact_inventory_digest_sha256": inventory["exact_inventory_digest_sha256"],
        "final_disc_record_digest_sha256": envelope["final_disc_record_digest_sha256"],
        "selected_class_membership_digest_sha256": envelope[
            "selected_class_membership_digest_sha256"
        ],
        "aggregate_resource_record_digest_sha256": resource[
            "aggregate_resource_record_digest_sha256"
        ],
        "registered_resource_identity": {
            "class_power_record_count": resource["class_power_record_count"],
            "group_signature_record_count": resource["group_signature_record_count"],
            "pair_pool_cache_key_count": resource["pair_pool_cache_key_count"],
            "cached_pair_signature_entry_count": resource[
                "cached_pair_signature_entry_count"
            ],
            "exact_convolution_call_count": resource["exact_convolution_call_count"],
            "original_monomial_count": resource["original_monomial_count"],
            "modulus_signature_count": resource["modulus_signature_count"],
            "peak_live_combined_signature_count": resource[
                "peak_live_combined_signature_count"
            ],
            "peak_two_product_bound_array_bytes": resource[
                "peak_two_product_bound_array_bytes"
            ],
            "distinct_comparison_upper_bound": resource[
                "distinct_comparison_upper_bound"
            ],
            "weighted_comparison_upper_bound": resource[
                "weighted_comparison_upper_bound"
            ],
        },
        "disc_label_logic": (
            "each source factor independently selects any certified selected disc with "
            "repetition and every registered external target disc is checked; no "
            "component-internal eigenvalue-to-disc label is assumed"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, classes, overlap_counts, external_indices, target_groups


def _degree_eighteen_sweep(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_indices: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    sweep = q011an._full_component_safe_sweep(
        classes, lookup, overlap_counts, external_indices, target_groups
    )
    sweep["degree"] = DEGREE
    streaming = sweep["streaming_contract"]
    streaming["full_degree_eighteen_monomial_list_retained"] = streaming.pop(
        "full_degree_sixteen_monomial_list_retained"
    )
    streaming["full_degree_eighteen_classification_matrices_retained"] = streaming.pop(
        "full_classification_matrices_retained"
    )
    return sweep


def _degree_eighteen_sweep_audit(sweep: dict[str, Any]) -> dict[str, Any]:
    witness = sweep["global_minimum_separated_witness"]
    first_overlap = sweep["first_unresolved_witness"]
    streaming = sweep["streaming_contract"]
    bridge = {
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "directly_separated_overlap_inventory_aggregate_count": sweep[
            "fully_separated_overlap_aggregate_count"
        ],
        "degree_eighteen_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "remaining_degree_eighteen_aggregate_count": sweep["remaining_overlap_aggregate_count"],
    }
    checks = {
        "registered_hierarchical_resource_identity_reproduces": bool(
            sweep["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and sweep["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
            and sweep["pair_pool_record_count"] == EXPECTED_PAIR_POOL_KEY_COUNT
            and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
            and sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and sweep["maximum_live_combined_signature_count"]
            == EXPECTED_PEAK_LIVE_SIGNATURE_COUNT
            and 2 * 8 * sweep["maximum_live_combined_signature_count"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
        ),
        "all_exact_integer_and_outward_array_invariants_hold": bool(
            sweep["all_convolutions_nonnegative"]
            and sweep["all_convolution_fiber_sums_exact"]
            and sweep["all_product_bound_arrays_are_finite"]
            and sweep["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and sweep["all_original_monomial_counts_match_multiset_coefficients"]
            and sweep["all_modulus_signature_counts_match_weak_compositions"]
            and sweep["maximum_convolution_crude_int64_bound"]
            <= EXPECTED_SAFE_INT64_CRUDE_BOUND
            and sweep["maximum_fourier_crude_int64_bound"] <= EXPECTED_SAFE_INT64_CRUDE_BOUND
        ),
        "registered_aggregate_order_and_comparison_bounds_hold": bool(
            sweep["degree"] == DEGREE
            and sweep["audited_overlap_aggregate_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(sweep["aggregate_records"]) == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and [record["aggregate_index"] for record in sweep["aggregate_records"]]
            == list(range(EXPECTED_OVERLAP_AGGREGATE_COUNT))
            and sweep["distinct_comparison_count"]
            <= EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and sweep["weighted_comparison_count"]
            <= EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
        ),
        "streaming_matrix_summaries_are_complete_and_hashed": bool(
            sweep["bound_matrix_record_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and sweep["coefficient_matrix_record_count"] > 0
            and sweep["classification_matrix_record_count"] > 0
            and all(
                len(sweep[name]) == 64
                for name in (
                    "aggregate_record_digest_sha256",
                    "class_power_record_digest_sha256",
                    "group_signature_digest_sha256",
                    "pair_pool_record_digest_sha256",
                    "bound_matrix_digest_sha256",
                    "coefficient_matrix_digest_sha256",
                    "classification_matrix_digest_sha256",
                )
            )
        ),
        "global_separated_witness_is_exact_and_positive": bool(
            witness["relation"] in {"product_below_target", "target_below_product"}
            and witness["outward_gap_lower"]["float"] > 0
            and q011z._fraction(witness["exact_gap"]) > 0
            and len(witness["witness_digest_sha256"]) == 64
        ),
        "first_overlap_witness_is_exact_if_present": bool(
            first_overlap is None
            or (
                first_overlap["relation"] == "overlap"
                and len(first_overlap["witness_digest_sha256"]) == 64
                and "intersection_interval" in first_overlap
            )
        ),
        "old_and_direct_inventory_accounting_is_exact": bool(
            bridge["old_modulus_separated_aggregate_count"]
            + bridge["directly_separated_overlap_inventory_aggregate_count"]
            + bridge["remaining_degree_eighteen_aggregate_count"]
            == bridge["degree_eighteen_aggregate_count"]
        ),
        "streaming_contract_retains_no_full_expansion": bool(
            not streaming["full_degree_eighteen_monomial_list_retained"]
            and not streaming["full_degree_eighteen_classification_matrices_retained"]
            and streaming["aggregate_summary_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
        ),
        "sweep_is_finite_strict_json": bool(
            _all_numeric_values_finite(sweep)
            and _strict_json_serializable(sweep)
            and json.dumps(sweep, allow_nan=False)
        ),
    }
    return {
        **sweep,
        "degree_eighteen_bridge": bridge,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "direct_overlap_inventory_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
        "selected_source_identifier_count": EXPECTED_SELECTED_IDENTIFIER_COUNT,
        "external_target_identifier_count": EXPECTED_TARGET_IDENTIFIER_COUNT,
        "final_identifier_count": EXPECTED_FINAL_IDENTIFIER_COUNT,
        "selected_modulus_class_counts": list(EXPECTED_CLASS_COUNTS),
        "source_disc_choice_logic": "independent with repetition",
        "target_disc_choice_logic": "every registered certified target disc",
        "full_monomial_list_retained": False,
        "full_classification_matrices_retained": False,
        "wall_time_is_an_acceptance_threshold": False,
        "measured_process_memory_is_an_acceptance_threshold": False,
        "accepted_classification": ACCEPTED_CLASSIFICATION,
        "rejected_classification": REJECTED_CLASSIFICATION,
        "actual_resonance_outcome_if_accepted": ACCEPTED_ACTUAL_RESONANCE_OUTCOME,
        "unobserved_relation_counts_are_preregistered_thresholds": False,
        "unobserved_matrix_digests_are_preregistered_thresholds": False,
        "unobserved_minimum_witness_is_a_preregistered_threshold": False,
        "degrees_nineteen_through_ninety_claimed": False,
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
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_degree_eighteen_hierarchical_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        preparation,
        lookup,
        classes,
        overlap_counts,
        external_indices,
        target_groups,
    ) = _fixed_input_audit(artifacts)
    sweep = _degree_eighteen_sweep_audit(
        _degree_eighteen_sweep(
            classes, lookup, overlap_counts, external_indices, target_groups
        )
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    preparation_sections = {"fixed_degree_eighteen_input_audit": preparation}
    sweep_sections = {"degree_eighteen_hierarchical_sweep_audit": sweep}
    input_digest = q011b._canonical_json_sha256(input_sections)
    preparation_digest = q011b._canonical_json_sha256(preparation_sections)
    sweep_digest = q011b._canonical_json_sha256(sweep_sections)
    validity_gates = {
        "q011ap_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "21 artifacts and 108 direct digests reproduce",
            "value": sealed["checks"],
        },
        "fixed_inventory_envelope_and_resource_contract_reproduce": {
            "passed": preparation["passed"],
            "threshold": "Q011ap deterministic preparation reproduces bitwise",
            "value": preparation["checks"],
        },
        "full_hierarchical_enumeration_and_arithmetic_are_valid": {
            "passed": sweep["passed"],
            "threshold": "252 aggregates obey every exact integer and outward invariant",
            "value": sweep["checks"],
        },
        "registered_resource_identity_and_comparison_bounds_hold": {
            "passed": bool(
                sweep["checks"]["registered_hierarchical_resource_identity_reproduces"]
                and sweep["checks"]["registered_aggregate_order_and_comparison_bounds_hold"]
            ),
            "threshold": "registered counts reproduce and comparisons stay below upper bounds",
            "value": {
                "original_monomials": sweep["original_monomial_count"],
                "modulus_signatures": sweep["modulus_signature_count"],
                "convolutions": sweep["convolution_call_count"],
                "peak_live_signatures": sweep["maximum_live_combined_signature_count"],
                "distinct_comparisons": sweep["distinct_comparison_count"],
                "weighted_comparisons": sweep["weighted_comparison_count"],
            },
        },
        "streamed_matrix_summaries_are_complete_and_hashed": {
            "passed": sweep["checks"]["streaming_matrix_summaries_are_complete_and_hashed"],
            "threshold": "aggregate, bound, coefficient and classification digests exist",
            "value": {
                "bound": sweep["bound_matrix_record_count"],
                "coefficient": sweep["coefficient_matrix_record_count"],
                "classification": sweep["classification_matrix_record_count"],
            },
        },
        "registered_witnesses_are_exactly_reconstructed": {
            "passed": bool(
                sweep["checks"]["global_separated_witness_is_exact_and_positive"]
                and sweep["checks"]["first_overlap_witness_is_exact_if_present"]
            ),
            "threshold": "global separated and optional first-overlap witnesses are exact",
            "value": {
                "global": sweep["global_minimum_separated_witness"][
                    "witness_digest_sha256"
                ],
                "first_overlap": (
                    sweep["first_unresolved_witness"]["witness_digest_sha256"]
                    if sweep["first_unresolved_witness"] is not None
                    else None
                ),
            },
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(len(digest) == 64 for digest in (input_digest, preparation_digest, sweep_digest))
                and runner["filename"] == "q011aq_degree18_hierarchical_sweep.py"
            ),
            "threshold": "strict finite JSON, three section digests and runner metadata",
            "value": {
                "input": input_digest,
                "preparation": preparation_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    witness = sweep["global_minimum_separated_witness"]
    all_direct_separated = bool(
        sweep["fully_separated_overlap_aggregate_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
        and sweep["remaining_overlap_aggregate_count"] == 0
        and sweep["remaining_overlap_aggregate_indices"] == []
    )
    bridge_complete = bool(
        sweep["degree_eighteen_bridge"]["old_modulus_separated_aggregate_count"]
        + sweep["degree_eighteen_bridge"][
            "directly_separated_overlap_inventory_aggregate_count"
        ]
        == EXPECTED_DEGREE_AGGREGATE_COUNT
        and sweep["degree_eighteen_bridge"]["remaining_degree_eighteen_aggregate_count"] == 0
    )
    hypothesis_gates = {
        "all_selected_and_target_eigenvalues_have_label_safe_disc_coverage": {
            "passed": bool(validity_passed and preparation["passed"]),
            "threshold": "24 selected sources and 164 external targets are covered",
            "value": {
                "selected": preparation["selected_source_identifier_count"],
                "targets": preparation["external_target_identifier_count"],
            },
        },
        "all_two_hundred_fifty_two_overlap_inventory_aggregates_are_separated": {
            "passed": bool(validity_passed and all_direct_separated),
            "threshold": "every compatible comparison has overlap count zero",
            "value": {
                "fully_separated": sweep["fully_separated_overlap_aggregate_count"],
                "remaining": sweep["remaining_overlap_aggregate_count"],
                "relations": sweep["distinct_relation_counts"],
            },
        },
        "all_one_thousand_three_hundred_thirty_degree_eighteen_aggregates_are_separated": {
            "passed": bool(validity_passed and bridge_complete),
            "threshold": "1078 old plus 252 direct aggregates separate",
            "value": sweep["degree_eighteen_bridge"],
        },
        "global_minimum_is_strictly_positive": {
            "passed": bool(
                validity_passed
                and witness["outward_gap_lower"]["float"] > 0
                and q011z._fraction(witness["exact_gap"]) > 0
            ),
            "threshold": "outward and exact gaps are both strictly positive",
            "value": {
                "outward_gap_hex": witness["outward_gap_lower"]["binary64_hex"],
                "exact_gap_hex": witness["exact_gap_hex"],
            },
        },
        "claim_is_limited_to_degree_eighteen_external_nonresonance": {
            "passed": validity_passed,
            "threshold": "no degree 19--90, all-order, SSM or basin extrapolation",
            "value": "registered claim boundary only",
        },
    }
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    accepted = bool(validity_passed and hypothesis_passed)
    rejected = bool(validity_passed and not hypothesis_passed)
    cycle = {
        "question": (
            "Does the preregistered component-safe hierarchical exact-multiplicity sweep "
            "certify every degree-eighteen external nonresonance comparison?"
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
        "hypothesis_outcome": (
            "accepted" if accepted else "rejected" if rejected else "inconclusive"
        ),
        "actual_resonance_outcome": (
            ACCEPTED_ACTUAL_RESONANCE_OUTCOME
            if accepted
            else "not_established"
            if rejected
            else "inconclusive"
        ),
        "scientific_classification": (
            ACCEPTED_CLASSIFICATION
            if accepted
            else REJECTED_CLASSIFICATION
            if rejected
            else INCONCLUSIVE_CLASSIFICATION
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "degree_eighteen_external_nonresonance_is_certified": accepted,
        "an_actual_degree_eighteen_external_resonance_is_ruled_out": accepted,
        "old_modulus_separated_aggregate_count": (
            EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT if accepted else 0
        ),
        "directly_separated_overlap_inventory_aggregate_count": (
            EXPECTED_OVERLAP_AGGREGATE_COUNT if accepted else 0
        ),
        "certified_external_nonresonance_degrees": (
            list(range(2, 19)) if accepted else list(range(2, 18))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(19 if accepted else 18, 91)),
        "degrees_nineteen_through_ninety_are_certified": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011ao_degree_seventeen_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only degree-eighteen external spectral relations for "
        "the fixed 17x17 repaired exact map on one fixed conservation leaf, the Q011ap "
        "188-identifier component-safe envelope, independent source-disc choices with "
        "repetition, every registered target disc, exact x-Fourier multiplicities and "
        "the preregistered hierarchical outward-dyadic product protocol. An accepted "
        "outcome rules out an actual external resonance only within those registered "
        "degree-eighteen relations. It establishes no result for degrees 19 through 90, "
        "all-order nonresonance, higher graph smoothness, SSM existence or uniqueness, "
        "normal attraction, basin, other grid, force, wall or D3Q27 case."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011u_modulus_only_rejection_changed": False,
        "q011an_degree_sixteen_certificate_changed": False,
        "q011ao_degree_seventeen_certificate_changed": False,
        "q011ap_resource_decision_changed": False,
    }
    if accepted:
        cycle["next_change"] = (
            "Run a design-only Q011ar degree-nineteen resource estimate before "
            "preregistering any degree-nineteen full sweep."
        )
    elif rejected:
        cycle["next_change"] = (
            "Audit only the first registered degree-eighteen overlap before choosing "
            "any further eigendisc refinement."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first seal, preparation, sweep, resource, witness or "
            "serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011aq cycle failed strict serialization or digest")
    return cycle


def run_q011aq_study() -> dict[str, Any]:
    cycle = run_degree_eighteen_hierarchical_audit()
    sweep = cycle["degree_eighteen_hierarchical_sweep_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "inventory_arithmetic": "exact integer log-grid intervals",
            "source_multiplicity_arithmetic": "exact numpy.int64 17-point cyclic convolution",
            "product_enclosure": "outward-rounded IEEE-754 binary64 interval products",
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "convolution_call_count": sweep["convolution_call_count"],
            "weighted_comparison_count": sweep["weighted_comparison_count"],
            "distinct_comparison_count": sweep["distinct_comparison_count"],
        },
        "mathematical_scope": {
            "diagnostic": "component-safe degree-18 external nonresonance certificate",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_eighteen_external_nonresonance_claim": cycle["hypothesis_outcome"]
            == "accepted",
            "actual_degree_eighteen_external_resonance_ruled_out_claim": cycle[
                "hypothesis_outcome"
            ]
            == "accepted",
            "degrees_19_through_90_claim": False,
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
    result = run_q011aq_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
