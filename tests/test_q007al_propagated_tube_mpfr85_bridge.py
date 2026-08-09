from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007al_propagated_tube_mpfr85_bridge as q007al
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007al_cycle() -> dict:
    return q007al.run_propagated_tube_mpfr85_bridge_audit()


def test_q007al_reproduces_both_sealed_inputs(q007al_cycle: dict) -> None:
    inputs = q007al_cycle["input_artifacts"]
    factor = q007al_cycle["q007ak_reproduction"]
    old_backend = q007al_cycle["q007x_reproduction"]

    assert set(inputs) == {"q007ak", "q007x"}
    assert all(record["passed"] for record in inputs.values())
    assert factor["stored_cycle_reproduced_exactly"]
    assert factor["observed_digests"] == q007al.REGISTERED_Q007AK_DIGESTS
    assert factor["selection_thresholds"] == {
        "base": 79,
        "normal": 59,
        "joint": 79,
    }
    assert factor["p85_candidate_count"] == 1
    assert factor["p85_candidate_passed"]
    assert factor["passed"]
    assert old_backend["stored_cycle_reproduced_exactly"]
    assert old_backend["observed_digests"] == q007al.REGISTERED_Q007X_DIGESTS
    assert old_backend["failed_hypothesis_names"] == (
        q007al.EXPECTED_Q007X_FAILED_HYPOTHESES
    )
    assert old_backend["registered_summary"] == q007al.EXPECTED_Q007X_SUMMARY
    assert old_backend["passed"]


def test_q007al_exactly_replays_the_new_tube_p85_candidate(
    q007al_cycle: dict,
) -> None:
    certificate = q007al_cycle["ideal_p85_certificate"]
    candidate = certificate["candidate"]

    assert certificate["precision_bits"] == 85
    assert certificate["joint_threshold_bits"] == 79
    assert certificate["precision_exceeds_joint_threshold"]
    assert certificate["stored_candidate_reproduced_exactly"]
    assert certificate["candidate_digests_match"]
    assert candidate["operation_counts_match"]
    assert candidate["one_step_stage_positivity_passed"]
    assert candidate["base_reentry_passed"]
    assert candidate["normal_reentry_passed"]
    assert candidate["passed"]
    assert float(_fraction(candidate["post_filter_component_error_sum"])) == pytest.approx(
        9.365881800643092e-25
    )
    assert float(_fraction(candidate["wiener_error_upper"])) == pytest.approx(
        2.7067398403858536e-22
    )
    assert float(_fraction(candidate["base_coordinate_error_upper"])) == pytest.approx(
        4.08902913525762e-22
    )
    assert float(_fraction(candidate["normal_coordinate_error_upper"])) == pytest.approx(
        8.097790464783468e-21
    )
    assert float(_fraction(candidate["base_margin_utilization"])) == pytest.approx(
        0.008212856636827946
    )
    assert float(_fraction(candidate["normal_margin_utilization"])) == pytest.approx(
        8.8549303467643e-09
    )
    assert float(_fraction(candidate["minimum_stage_lower"])) == pytest.approx(
        0.027777777145968227
    )
    assert certificate["strict_base_budget"]
    assert certificate["strict_normal_budget"]
    assert certificate["passed"]


def test_q007al_seals_sources_context_constants_and_new_box_probes(
    q007al_cycle: dict,
) -> None:
    source = q007al_cycle["source_audit"]
    context = q007al_cycle["context_audit"]
    algebra = q007al_cycle["constant_algebra"]
    probes = q007al_cycle["probe_registration"]

    assert {
        name: record["sha256"] for name, record in source["files"].items()
    } == q007al.REGISTERED_SOURCE_SHA256
    assert all(record["sha256_matches"] for record in source["files"].values())
    assert source["q007w_operation_schedule_matches_backend"]
    assert source["passed"]
    assert context["runtime"]["gmpy2_version"] == "2.3.1"
    assert context["runtime"]["mpfr_version"] == "MPFR 4.2.2"
    assert context["runtime"]["gmp_version"] == "GMP 6.3.0"
    assert context["runtime"]["precision_bits"] == 85
    assert context["context_restored"]
    assert not any(context["dangerous_construction_flags"].values())
    assert context["passed"]
    assert algebra["constants_match_q007w_selected_candidate"]
    assert algebra["nonzero_mass_and_filter_obstructions_reproduced"]
    assert algebra["passed"]
    assert probes["probe_count"] == 4
    assert probes["probe_digest_sha256"] == q007al.REGISTERED_Q007X_DIGESTS["probe"]
    assert all(
        probe["fixed_leaf_exact"]
        and probe["component_box_strict"]
        and _fraction(probe["minimum_population"]) > 0
        and probe["passed"]
        for probe in probes["probes"]
    )
    assert probes["passed"]


def test_q007al_matches_all_mpfr_operations_and_new_stage_bounds(
    q007al_cycle: dict,
) -> None:
    campaign = q007al_cycle["backend_campaign"]
    utilizations: list[Fraction] = []

    assert campaign["probe_count"] == 4
    assert campaign["expected_trace_records_per_probe"] == 70824
    assert campaign["expected_map_trace_records_per_probe"] == 70805
    assert campaign["aggregate_trace_digest_sha256"] == (
        q007al.REGISTERED_Q007X_DIGESTS["trace"]
    )
    assert campaign["summary"]["all_traces_match"]
    assert campaign["summary"]["all_operation_domains_pass"]
    assert campaign["summary"]["all_stage_bounds_and_positivity_pass"]
    assert campaign["summary"]["context_restored"]
    for probe in campaign["probes"]:
        assert probe["trace"]["record_count"] == 70824
        assert probe["trace"]["map_record_count"] == 70805
        assert probe["trace"]["mismatch_count"] == 0
        assert probe["trace"]["first_mismatch"] is None
        assert probe["trace"]["passed"]
        assert probe["operation_domain"]["operation_counts_match"]
        assert probe["operation_domain"]["passed"]
        for stage in probe["stage_comparisons"].values():
            observed = _fraction(stage["maximum_observed_component_error"])
            bound = _fraction(stage["registered_component_error_upper"])
            utilization = _fraction(stage["error_bound_utilization"])
            assert observed <= bound
            assert utilization == observed / bound
            assert utilization < 1
            assert _fraction(stage["minimum_mpfr_population"]) > 0
            assert stage["error_enclosed"]
            assert stage["strictly_positive"]
            assert stage["passed"]
            utilizations.append(utilization)

    assert max(utilizations) < 1


def test_q007al_keeps_fixed_leaf_closure_outside_the_acceptance_claim(
    q007al_cycle: dict,
) -> None:
    campaign = q007al_cycle["backend_campaign"]
    regression = q007al_cycle["conservation_regression"]
    diagnostic = q007al_cycle["conservation_diagnostic"]
    theorem = q007al_cycle["theorem_consequence"]

    assert campaign["summary"] == q007al.EXPECTED_Q007X_SUMMARY
    assert regression["conservation_records_match_q007x"]
    assert regression["observed_stage_records_match_q007x"]
    assert regression["summary_matches"]
    assert regression["aggregate_trace_digest_matches_q007x"]
    assert not regression["fixed_leaf_closure_certified"]
    assert regression["passed"]
    assert not diagnostic["all_encodings_conserve"]
    assert not diagnostic["all_collisions_conserve"]
    assert diagnostic["all_streaming_conserves"]
    assert not diagnostic["all_filters_conserve"]
    assert not diagnostic["all_full_steps_conserve"]
    assert not diagnostic["fixed_leaf_closure_certified"]
    assert not diagnostic["acceptance_hypothesis"]
    assert not theorem["rounded_output_is_on_the_fixed_conservation_leaf"]
    assert not theorem["actual_q007ag_tube_reentry_is_certified"]
    assert not theorem["all_iterate_mpfr85_q007ag_tube_invariance_is_certified"]


def test_q007al_accepts_only_the_one_step_arithmetic_bridge(
    q007al_cycle: dict,
) -> None:
    assert q007al_cycle["study_validity"] == "passed"
    assert q007al_cycle["hypothesis_outcome"] == "accepted"
    assert q007al_cycle["scientific_classification"] == (
        "registered MPFR-85 backend realizes the Q007ag one-step arithmetic "
        "and complement-coordinate error budgets"
    )
    assert len(q007al_cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in q007al_cycle["validity_gates"].values())
    assert len(q007al_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q007al_cycle["hypothesis_gates"].values())
    theorem = q007al_cycle["theorem_consequence"]
    assert theorem["concrete_backend_realizes_registered_mpfr85_semantics"]
    assert theorem["concrete_backend_one_step_stages_are_enclosed_and_positive"]
    assert theorem["ideal_p85_base_and_normal_error_budgets_fit_q007ag_margins"]
    assert "actual rounded fixed-leaf membership" in q007al_cycle["claim_boundary"]
    assert "Finite probes are not a tube-wide sampling proof" in (
        q007al_cycle["claim_boundary"]
    )
    assert not any(q007al_cycle["preserved_prior_outcomes"].values())


def test_q007al_records_provenance_and_deterministic_digests(
    q007al_cycle: dict,
) -> None:
    runner_path = Path(q007al.__file__).resolve()

    assert q007al._runner_source_metadata() == {
        "filename": "q007al_propagated_tube_mpfr85_bridge.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    digest_keys = (
        "input_digest_sha256",
        "candidate_digest_sha256",
        "probe_digest_sha256",
        "trace_digest_sha256",
        "campaign_result_digest_sha256",
        "result_digest_sha256",
    )
    assert all(
        isinstance(q007al_cycle[key], str) and len(q007al_cycle[key]) == 64
        for key in digest_keys
    )
    assert q007al_cycle["candidate_digest_sha256"] == (
        q007al_cycle["ideal_p85_certificate"]["fresh_candidate_digest_sha256"]
    )
    assert q007al_cycle["probe_digest_sha256"] == (
        q007al_cycle["probe_registration"]["probe_digest_sha256"]
    )
    assert q007al_cycle["trace_digest_sha256"] == (
        q007al_cycle["backend_campaign"]["aggregate_trace_digest_sha256"]
    )
    assert q007al_cycle["campaign_result_digest_sha256"] == (
        q007al_cycle["backend_campaign"]["result_digest_sha256"]
    )
    json.dumps(q007al_cycle, allow_nan=False)
