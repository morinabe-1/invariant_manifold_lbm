from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ak_reentry_factor_audit as q007ak
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ak_cycle() -> dict:
    return q007ak.run_reentry_factor_audit()


def test_q007ak_reproduces_q007aj_and_q007w_oracles(
    q007ak_cycle: dict,
) -> None:
    inputs = q007ak_cycle["input_artifacts"]
    binary64 = q007ak_cycle["q007aj_exact_reproduction"]
    old_precision = q007ak_cycle["q007w_oracle_reproduction"]

    assert set(inputs) == {"q007aj", "q007w"}
    assert all(record["passed"] for record in inputs.values())
    assert binary64["stored_cycle_reproduced_exactly"]
    assert binary64["observed_digests"] == (q007ak.REGISTERED_Q007AJ_DIGESTS)
    assert binary64["failed_hypothesis_names"] == [
        "base_coordinate_roundoff_reentry",
        "normal_coordinate_roundoff_reentry",
    ]
    assert binary64["one_step_outcome"] == "accepted"
    assert binary64["base_reentry_outcome"] == "not_certified"
    assert binary64["normal_reentry_outcome"] == "not_certified"
    assert binary64["implementation_sources_match"]
    assert binary64["passed"]
    assert old_precision["stored_cycle_reproduced_exactly"]
    assert old_precision["old_selected_precision_bits"] == 85
    assert old_precision["old_previous_precision_bits"] == 84
    assert old_precision["candidate_digest_sha256"] == (q007ak.REGISTERED_Q007W_CANDIDATE_DIGEST)
    assert old_precision["candidate_digest_matches"]
    assert old_precision["ties_to_even_control_passed"]
    assert old_precision["p53_q007v_control_passed"]
    assert old_precision["passed"]


def test_q007ak_p53_exactly_reproduces_q007aj(
    q007ak_cycle: dict,
) -> None:
    control = q007ak_cycle["p53_q007aj_control"]

    assert control["precision_bits"] == 53
    assert control["all_population_target_and_error_records_match"]
    assert control["all_stage_summaries_match"]
    assert control["weight_dyadics_match"]
    assert control["filter_scalar_dyadics_match"]
    assert control["all_reentry_quantities_match"]
    assert control["operation_counts"] == q007ak.q007aj.EXPECTED_OPERATION_COUNTS
    assert control["operation_counts_match"]
    assert control["split_outcome_reproduced"]
    assert control["passed"]


def test_q007ak_exact_factorization_and_counterfactuals(
    q007ak_cycle: dict,
) -> None:
    audit = q007ak_cycle["factor_audit"]
    wave_count = q007ak_cycle["registered_parameters"]["normalized_dft_wave_count"]

    assert audit["factorization_formula"] == "U_X = K_X * N * E_53 / m_X"
    assert wave_count == 289
    for record in audit["coordinates"].values():
        analysis = _fraction(record["analysis_upper"])
        error = _fraction(record["local_component_error_sum"])
        margin = _fraction(record["strict_margin"])
        coordinate_error = _fraction(record["coordinate_error_upper"])
        utilization = _fraction(record["margin_utilization"])
        maximum_error = _fraction(record["maximum_local_component_error_at_boundary"])
        maximum_analysis = _fraction(record["maximum_analysis_factor_at_boundary"])
        maximum_wave = _fraction(record["maximum_wave_factor_at_boundary"])
        minimum_margin = _fraction(record["minimum_margin_at_boundary"])

        assert coordinate_error == analysis * wave_count * error
        assert utilization == coordinate_error / margin
        assert maximum_error == margin / (analysis * wave_count)
        assert maximum_analysis == margin / (wave_count * error)
        assert maximum_wave == margin / (analysis * error)
        assert minimum_margin == coordinate_error
        assert _fraction(record["strict_single_factor_improvement_required"]) == utilization
        assert all(record["exact_identity_checks"].values())
        assert record["all_exact_identity_checks_pass"]
        assert record["passed"]

    base = audit["coordinates"]["base"]
    normal = audit["coordinates"]["normal"]
    assert float(_fraction(base["margin_utilization"])) == pytest.approx(35399902.97837664)
    assert float(_fraction(normal["margin_utilization"])) == pytest.approx(38.16743540245316)
    assert float(_fraction(base["maximum_local_component_error_at_boundary"])) == pytest.approx(
        1.1403927055836785e-22
    )
    assert float(_fraction(normal["maximum_local_component_error_at_boundary"])) == pytest.approx(
        1.0577024814278182e-16
    )
    assert not base["unit_wave_counterfactual"]["strict_reentry_passed"]
    assert normal["unit_wave_counterfactual"]["strict_reentry_passed"]
    assert not base["unit_analysis_counterfactual"]["strict_reentry_passed"]
    assert not normal["unit_analysis_counterfactual"]["strict_reentry_passed"]
    assert audit["passed"]


def test_q007ak_precision_campaign_is_complete_and_monotone(
    q007ak_cycle: dict,
) -> None:
    campaign = q007ak_cycle["precision_campaign"]
    candidates = campaign["candidates"]

    assert campaign["registered_precisions"] == list(range(53, 129))
    assert campaign["candidate_count"] == 76
    assert len(candidates) == 76
    assert [candidate["precision_bits"] for candidate in candidates] == list(range(53, 129))
    assert campaign["candidate_digest_sha256"] == (
        "eacc824a8f0fc891971c210883d05f7178e4fe5848ab3b2432dc94adf289e567"
    )
    assert campaign["coverage_match"]
    assert all(campaign["monotonicity_checks"].values())
    assert campaign["all_monotonicity_checks_pass"]
    assert campaign["all_candidate_domains_pass"]
    assert all(
        candidate["operation_counts"] == q007ak.q007aj.EXPECTED_OPERATION_COUNTS
        and candidate["operation_counts_match"]
        and candidate["one_step_stage_positivity_passed"]
        for candidate in candidates
    )


def test_q007ak_separates_base_normal_and_joint_thresholds(
    q007ak_cycle: dict,
) -> None:
    selection = q007ak_cycle["selection"]
    expected = {"base": 79, "normal": 59, "joint": 79}
    for name, precision in expected.items():
        record = selection[name]
        assert record["selected_precision_bits"] == precision
        assert record["selected_candidate"]["precision_bits"] == precision
        assert record["previous_precision_candidate"]["precision_bits"] == (precision - 1)
        assert record["first_pass_matches_selection"]
        assert record["selection_boundary_reproduced"]

    base = selection["base"]
    normal = selection["normal"]
    joint = selection["joint"]
    assert base["selected_candidate"]["base_reentry_passed"]
    assert not base["previous_precision_candidate"]["base_reentry_passed"]
    assert normal["selected_candidate"]["normal_reentry_passed"]
    assert not normal["previous_precision_candidate"]["normal_reentry_passed"]
    assert not normal["selected_candidate"]["base_reentry_passed"]
    assert joint["selected_candidate"]["passed"]
    assert not joint["previous_precision_candidate"]["passed"]
    assert selection["dominance_audit"]["passed"]
    assert selection["all_selection_boundaries_reproduced"]
    assert selection["passed"]


def test_q007ak_accepts_base_as_the_dominant_obstruction(
    q007ak_cycle: dict,
) -> None:
    assert q007ak_cycle["study_validity"] == "passed"
    assert q007ak_cycle["hypothesis_outcome"] == "accepted"
    assert q007ak_cycle["scientific_classification"] == (
        "registered factor audit isolates base re-entry as the dominant Q007ag binary64 obstruction"
    )
    assert len(q007ak_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q007ak_cycle["validity_gates"].values())
    assert len(q007ak_cycle["hypothesis_gates"]) == 7
    assert all(gate["passed"] for gate in q007ak_cycle["hypothesis_gates"].values())
    theorem = q007ak_cycle["theorem_consequence"]
    assert all(
        value
        for name, value in theorem.items()
        if name != "implemented_mpfr85_new_tube_reentry_certified"
    )
    assert not theorem["implemented_mpfr85_new_tube_reentry_certified"]
    assert "sufficient within this worst-case enclosure" in (q007ak_cycle["claim_boundary"])
    assert not any(q007ak_cycle["preserved_prior_outcomes"].values())


def test_q007ak_records_provenance_and_deterministic_digests(
    q007ak_cycle: dict,
) -> None:
    runner_path = Path(q007ak.__file__).resolve()

    assert q007ak._runner_source_metadata() == {
        "filename": "q007ak_reentry_factor_audit.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert source_metadata()["package_version"] == "0.1.0"
    assert q007ak_cycle["input_digest_sha256"] == (
        "333ce7e6b4537947808a369f1c218c2d930a11df4b826994df0947fa42489d46"
    )
    assert q007ak_cycle["candidate_digest_sha256"] == (
        "eacc824a8f0fc891971c210883d05f7178e4fe5848ab3b2432dc94adf289e567"
    )
    assert q007ak_cycle["result_digest_sha256"] == (
        "a4d10df4c1d6edd83488115d501af21ad6727dd6321e159e37b2b0e434858644"
    )
    json.dumps(q007ak_cycle, allow_nan=False)
