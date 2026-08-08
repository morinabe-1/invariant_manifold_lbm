from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007w_ideal_precision_threshold as q007w
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007w_artifact() -> dict:
    artifact_path = (
        Path(q007w.__file__).resolve().parent
        / "artifacts"
        / "q007w_ideal_precision_threshold.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def q007v_artifact() -> dict:
    artifact_path = (
        Path(q007w.__file__).resolve().parent
        / "artifacts"
        / "q007v_binary64_stage_enclosure.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007w_accepts_the_minimum_ideal_precision_threshold(
    q007w_artifact,
) -> None:
    cycle = q007w_artifact["cycle"]

    assert cycle == q007w.run_ideal_precision_threshold_audit()
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered ideal binary precision threshold restores "
        "roundoff-robust Q007s tube re-entry"
    )
    assert cycle["selection"]["selected_precision_bits"] == 85
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    )
    assert all(cycle["theorem_consequence"].values())


def test_q007w_rounds_halfway_cases_to_even_exactly(q007w_artifact) -> None:
    audit = q007w_artifact["cycle"]["ties_to_even_audit"]

    assert q007w._round_to_binary_precision(Fraction(9, 8), 3) == 1
    assert q007w._round_to_binary_precision(Fraction(11, 8), 3) == Fraction(
        3, 2
    )
    assert q007w._round_to_binary_precision(Fraction(-9, 8), 3) == -1
    assert q007w._round_to_binary_precision(
        Fraction(-11, 8), 3
    ) == Fraction(-3, 2)
    assert len(audit["halfway_cases"]) == 4
    assert all(record["passed"] for record in audit["halfway_cases"])
    assert audit["passed"]


def test_q007w_reproduces_every_q007v_p53_quantity(
    q007w_artifact,
    q007v_artifact,
) -> None:
    cycle = q007w_artifact["cycle"]
    control = cycle["p53_control_audit"]
    p53 = cycle["precision_campaign"]["candidates"][0]
    q007v_cycle = q007v_artifact["cycle"]

    assert control == {
        "precision_bits": 53,
        "weight_dyadics_match": True,
        "filter_scalar_dyadics_match": True,
        "all_population_target_and_error_records_match": True,
        "all_stage_summaries_match": True,
        "all_reentry_quantities_match": True,
        "operation_counts_match": True,
        "passed": True,
    }
    assert p53["precision_bits"] == 53
    assert p53["stage_bounds"]["post_filter"]["population_lower"] == (
        q007v_cycle["paired_stage_enclosure"]["stages"]["post_filter"]
        ["binary64_population_lower"]
    )
    assert p53["wiener_error_upper"] == q007v_cycle[
        "roundoff_reentry_audit"
    ]["wiener_error_upper"]
    assert p53["base_margin_utilization"] == q007v_cycle[
        "roundoff_reentry_audit"
    ]["base_margin_utilization"]
    assert p53["one_step_stage_positivity_passed"]
    assert not p53["base_reentry_passed"]
    assert not p53["normal_reentry_passed"]
    assert not p53["passed"]


def test_q007w_evaluates_the_complete_monotone_precision_campaign(
    q007w_artifact,
) -> None:
    campaign = q007w_artifact["cycle"]["precision_campaign"]
    candidates = campaign["candidates"]

    assert campaign["registered_precisions"] == list(range(53, 129))
    assert campaign["candidate_count"] == 76
    assert [candidate["precision_bits"] for candidate in candidates] == list(
        range(53, 129)
    )
    assert campaign["candidate_digest_sha256"] == (
        "440a08dc36990d3e34edf1886fd7e47eacb4766c4a42352022897fd79dbb3ce2"
    )
    assert campaign["coverage_match"]
    assert all(campaign["monotonicity_checks"].values())
    assert campaign["all_monotonicity_checks_pass"]
    assert campaign["all_candidate_domains_pass"]
    assert all(
        candidate["one_step_stage_positivity_passed"]
        and candidate["operation_counts_match"]
        for candidate in candidates
    )


def test_q007w_selection_boundary_is_84_fail_85_pass(
    q007w_artifact,
) -> None:
    selection = q007w_artifact["cycle"]["selection"]
    previous = selection["previous_precision_candidate"]
    selected = selection["selected_candidate"]

    assert selection["candidate_count"] == 76
    assert selection["passing_candidate_count"] == 44
    assert selection["selected_precision_bits"] == 85
    assert selection["first_pass_matches_selection"]
    assert selection["selection_boundary_reproduced"]
    assert previous["precision_bits"] == 84
    assert previous["one_step_stage_positivity_passed"]
    assert not previous["base_reentry_passed"]
    assert previous["normal_reentry_passed"]
    assert not previous["passed"]
    assert selected["precision_bits"] == 85
    assert selected["one_step_stage_positivity_passed"]
    assert selected["base_reentry_passed"]
    assert selected["normal_reentry_passed"]
    assert selected["passed"]
    assert _fraction(previous["base_margin_utilization"]) > 1
    assert _fraction(selected["base_margin_utilization"]) < 1
    assert _fraction(previous["normal_margin_utilization"]) < 1


def test_q007w_selected_reentry_values_reconstruct_from_fixed_norms(
    q007w_artifact,
) -> None:
    cycle = q007w_artifact["cycle"]
    fixed = cycle["fixed_q007v_values"]
    selected = cycle["selection"]["selected_candidate"]
    wiener = _fraction(selected["wiener_error_upper"])
    selected_analysis = _fraction(fixed["selected_analysis_upper"])
    external_analysis = _fraction(fixed["external_analysis_upper"])
    base_margin = _fraction(fixed["base_forward_invariance_margin"])
    normal_margin = _fraction(
        fixed["normal_tube_forward_invariance_margin"]
    )

    assert _fraction(selected["base_coordinate_error_upper"]) == (
        selected_analysis * wiener
    )
    assert _fraction(selected["normal_coordinate_error_upper"]) == (
        external_analysis * wiener
    )
    assert _fraction(selected["base_margin_utilization"]) == (
        selected_analysis * wiener / base_margin
    )
    assert _fraction(selected["normal_margin_utilization"]) == (
        external_analysis * wiener / normal_margin
    )
    assert _fraction(selected["wiener_error_upper"]) == pytest.approx(
        2.706739822688458e-22
    )


def test_q007w_records_provenance_and_ideal_only_claim_boundary(
    q007w_artifact,
) -> None:
    cycle = q007w_artifact["cycle"]
    runner_path = Path(q007w.__file__).resolve()

    assert q007w_artifact["schema_version"] == 1
    assert q007w_artifact["source"] == source_metadata()
    assert q007w_artifact["runner_source"] == {
        "filename": "q007w_ideal_precision_threshold.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert cycle["input_artifact"]["sha256"] == (
        q007w.REGISTERED_Q007V_ARTIFACT_SHA256
    )
    assert cycle["input_artifact"]["observed_runner_sha256"] == (
        q007w.REGISTERED_Q007V_RUNNER_SHA256
    )
    assert cycle["input_artifact"]["passed"]
    assert cycle["fixed_q007v_values"]["passed"]
    assert "ideal p-bit" in cycle["claim_boundary"]
    assert "does not certify" in cycle["claim_boundary"]
    assert "not a necessary" in cycle["claim_boundary"]
    assert not any(cycle["preserved_prior_outcomes"].values())
    json.dumps(q007w_artifact, allow_nan=False)
