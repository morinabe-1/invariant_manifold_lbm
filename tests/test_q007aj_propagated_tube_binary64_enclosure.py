from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007aj_propagated_tube_binary64_enclosure as q007aj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007aj_cycle() -> dict:
    return q007aj.run_propagated_tube_binary64_enclosure_audit()


def test_q007aj_reproduces_all_sealed_inputs_and_oracles(
    q007aj_cycle: dict,
) -> None:
    inputs = q007aj_cycle["input_artifacts"]
    propagated = q007aj_cycle["q007ag_exact_reproduction"]
    exact_stages = q007aj_cycle["q007ai_exact_reproduction"]
    old_binary64 = q007aj_cycle["q007v_oracle_reproduction"]

    assert set(inputs) == {"q007ag", "q007ai", "q007v"}
    assert all(record["passed"] for record in inputs.values())
    assert propagated["stored_cycle_reproduced_exactly"]
    assert propagated["observed_digests"] == (q007aj.REGISTERED_Q007AG_DIGESTS)
    assert propagated["all_selected_candidate_gates_pass"]
    assert propagated["only_rho_and_tau_changed_from_q007s"]
    assert propagated["passed"]
    assert exact_stages["stored_cycle_reproduced_exactly"]
    assert exact_stages["observed_digests"] == (q007aj.REGISTERED_Q007AI_DIGESTS)
    assert exact_stages["all_exact_stage_population_lowers_positive"]
    assert exact_stages["passed"]
    assert old_binary64["stored_cycle_reproduced_exactly"]
    assert old_binary64["all_validity_gates_pass"]
    assert old_binary64["old_one_step_outcome"] == "accepted"
    assert old_binary64["old_robust_reentry_outcome"] == "not_certified"
    assert old_binary64["old_roundoff_reentry_rejected"]
    assert old_binary64["passed"]


def test_q007aj_replays_binary64_model_schedule_and_sources(
    q007aj_cycle: dict,
) -> None:
    model = q007aj_cycle["binary64_model_audit"]
    primitive = q007aj_cycle["primitive_interval_audit"]
    enclosure = q007aj_cycle["paired_stage_enclosure"]
    sources = q007aj_cycle["implementation_source_audit"]
    replay = q007aj_cycle["deterministic_implementation_replay"]

    assert model["passed"]
    assert _fraction(model["unit_roundoff"]) == Fraction(1, 2**53)
    assert _fraction(model["subnormal_absolute_fallback"]) == Fraction(1, 2**1075)
    assert primitive["passed"]
    assert enclosure["operation_counts"] == q007aj.EXPECTED_OPERATION_COUNTS
    assert enclosure["registered_operation_counts"] == (q007aj.EXPECTED_OPERATION_COUNTS)
    assert enclosure["operation_counts_match"]
    assert _fraction(enclosure["minimum_computed_density_denominator"]) > 0
    assert _fraction(enclosure["maximum_intermediate_magnitude_upper"]) < 2
    assert sources["d2q9_source"]["sha256"] == (q007aj.REGISTERED_D2Q9_SOURCE_SHA256)
    assert sources["filter_source"]["sha256"] == (q007aj.REGISTERED_FILTER_SOURCE_SHA256)
    assert sources["q007ai_stage_order_match"]
    assert sources["streaming_is_population_permutation_without_arithmetic"]
    assert sources["passed"]
    assert replay["all_stage_dtypes_float64"]
    assert replay["all_stage_shapes_match"]
    assert replay["all_stage_values_finite"]
    assert replay["all_stage_values_inside_registered_enclosures"]
    assert replay["wrapped_composition_bitwise_match"]
    assert replay["passed"]


def test_q007aj_new_tube_binary64_stage_lowers_are_strict(
    q007aj_cycle: dict,
) -> None:
    stages = q007aj_cycle["paired_stage_enclosure"]["stages"]
    lowers: dict[str, Fraction] = {}
    for name, stage in stages.items():
        reconstructed = min(
            _fraction(record["target_lower"]) - _fraction(record["forward_error_upper"])
            for record in stage["population_records"]
        )
        stored = _fraction(stage["binary64_population_lower"])
        assert stored == reconstructed
        assert stored > 0
        lowers[name] = stored

    assert stages["post_streaming"] == stages["post_collision"]
    assert lowers["post_filter"] < lowers["post_collision"]
    assert float(lowers["equilibrium"]) == pytest.approx(0.02777777759726066)
    assert float(lowers["post_collision"]) == pytest.approx(0.027777777145968068)
    assert float(lowers["post_filter"]) == pytest.approx(0.02777777714596806)


def test_q007aj_roundoff_exceeds_both_q007ag_reentry_margins(
    q007aj_cycle: dict,
) -> None:
    filtered = q007aj_cycle["paired_stage_enclosure"]["stages"]["post_filter"]["population_records"]
    cross = q007aj_cycle["cross_input_consistency"]
    audit = q007aj_cycle["roundoff_reentry_audit"]
    component_sum = sum(
        (_fraction(record["forward_error_upper"]) for record in filtered),
        Fraction(0),
    )
    wiener_error = q007aj.WAVE_COUNT * component_sum
    selected_analysis = _fraction(cross["selected_analysis_from_wiener_l1_upper"])
    external_analysis = _fraction(cross["external_analysis_from_wiener_l1_upper"])
    base_margin = _fraction(cross["base_forward_invariance_margin"])
    normal_margin = _fraction(cross["normal_tube_forward_invariance_margin"])

    assert _fraction(audit["component_forward_error_sum_upper"]) == (component_sum)
    assert _fraction(audit["wiener_error_upper"]) == wiener_error
    assert _fraction(audit["base_coordinate_error_upper"]) == (selected_analysis * wiener_error)
    assert _fraction(audit["normal_coordinate_error_upper"]) == (external_analysis * wiener_error)
    assert _fraction(audit["base_coordinate_error_upper"]) > base_margin
    assert _fraction(audit["normal_coordinate_error_upper"]) > normal_margin
    assert float(_fraction(audit["base_margin_utilization"])) == pytest.approx(35399902.97837664)
    assert float(_fraction(audit["normal_margin_utilization"])) == pytest.approx(38.16743540245316)
    assert not audit["base_reentry_passed"]
    assert not audit["normal_reentry_passed"]
    assert not audit["passed"]


def test_q007aj_accepts_one_step_but_rejects_both_reentry_gates(
    q007aj_cycle: dict,
) -> None:
    assert q007aj_cycle["study_validity"] == "passed"
    assert q007aj_cycle["one_step_outcome"] == "accepted"
    assert q007aj_cycle["base_reentry_outcome"] == "not_certified"
    assert q007aj_cycle["normal_reentry_outcome"] == "not_certified"
    assert q007aj_cycle["robust_reentry_outcome"] == "not_certified"
    assert q007aj_cycle["hypothesis_outcome"] == "not_certified"
    assert q007aj_cycle["scientific_classification"] == (
        "binary64 one-step stages remain positive, but the registered Q007ag "
        "tube is not certified roundoff-invariant"
    )
    assert len(q007aj_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q007aj_cycle["validity_gates"].values())
    assert len(q007aj_cycle["hypothesis_gates"]) == 7
    assert all(
        gate["passed"]
        for name, gate in q007aj_cycle["hypothesis_gates"].items()
        if name
        not in {
            "base_coordinate_roundoff_reentry",
            "normal_coordinate_roundoff_reentry",
        }
    )
    assert not q007aj_cycle["hypothesis_gates"]["base_coordinate_roundoff_reentry"]["passed"]
    assert not q007aj_cycle["hypothesis_gates"]["normal_coordinate_roundoff_reentry"]["passed"]
    theorem = q007aj_cycle["theorem_consequence"]
    assert all(
        theorem[name]
        for name in (
            "binary64_equilibrium_population_strictly_positive",
            "binary64_post_collision_population_strictly_positive",
            "binary64_post_streaming_population_strictly_positive",
            "binary64_post_filter_population_strictly_positive",
            "one_step_binary64_stagewise_population_strictly_positive",
        )
    )
    assert not theorem["roundoff_robust_base_coordinate_reentry"]
    assert not theorem["roundoff_robust_normal_coordinate_reentry"]
    assert not theorem["all_iterate_roundoff_robust_q007ag_tube_invariance"]
    assert not theorem["all_iterate_binary64_stagewise_population_strictly_positive"]
    assert (
        "neither a counterexample nor an observed tube escape" in (q007aj_cycle["claim_boundary"])
    )
    assert not any(q007aj_cycle["preserved_prior_outcomes"].values())


def test_q007aj_records_provenance_and_deterministic_digests(
    q007aj_cycle: dict,
) -> None:
    study = q007aj.run_q007aj_study()
    runner_path = Path(q007aj.__file__).resolve()

    assert study["schema_version"] == 1
    assert study["source"] == source_metadata()
    assert study["runner_source"] == {
        "filename": "q007aj_propagated_tube_binary64_enclosure.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert study["cycle"] == q007aj_cycle
    assert study["study_gate"] == "passed"
    assert study["scientific_outcome"] == "not_certified"
    assert study["mathematical_scope"]["base_modal_l1_radius"] == float(q007aj.BASE_RADIUS)
    assert study["mathematical_scope"]["normal_coordinate_radius"] == float(q007aj.NORMAL_RADIUS)
    assert len(q007aj_cycle["input_digest_sha256"]) == 64
    assert len(q007aj_cycle["result_digest_sha256"]) == 64
    assert q007aj_cycle["input_digest_sha256"] == (
        "040bf7e2c62094ea66a4cf8a6190ea78e53745e30c70a3b3ce856a7e4d1c5284"
    )
    assert q007aj_cycle["result_digest_sha256"] == (
        "517846a3a99f1e684f40c2ea6d5a8ae7b3db8c0849dae3097fc7f380f4eca923"
    )
    json.dumps(study, allow_nan=False)
