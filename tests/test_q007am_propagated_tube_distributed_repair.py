from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007am_propagated_tube_distributed_repair as q007am
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007am_cycle() -> dict:
    return q007am.run_propagated_tube_distributed_repair_audit()


def test_q007am_reproduces_q007al_and_q007y(q007am_cycle: dict) -> None:
    inputs = q007am_cycle["input_artifacts"]
    bridge = q007am_cycle["q007al_reproduction"]
    old_repair = q007am_cycle["q007y_reproduction"]

    assert set(inputs) == {"q007al", "q007y"}
    assert all(record["passed"] for record in inputs.values())
    assert bridge["stored_cycle_reproduced_exactly"]
    assert bridge["observed_digests"] == q007am.REGISTERED_Q007AL_DIGESTS
    assert bridge["all_validity_gates_pass"]
    assert bridge["all_hypothesis_gates_pass"]
    assert bridge["p85_candidate_passed"]
    assert bridge["source_context_and_probes_passed"]
    assert bridge["registered_conservation_nonclosure_reproduced"]
    assert bridge["passed"]
    assert old_repair["stored_cycle_reproduced_exactly"]
    assert old_repair["failed_hypothesis_names"] == (
        q007am.EXPECTED_Q007Y_FAILED_HYPOTHESES
    )
    assert old_repair["old_tube_utilizations"] == {
        "base_margin_utilization": 2.326054260951996,
        "normal_margin_utilization": 2.507922842743146e-7,
    }
    assert old_repair["probe_digest_matches"]
    assert old_repair["finite_result_digest_matches"]
    assert old_repair["finite_summary"] == q007am.EXPECTED_FINITE_SUMMARY
    assert old_repair["passed"]


def test_q007am_recomputes_the_registered_coarse_repair_bound(
    q007am_cycle: dict,
) -> None:
    bound = q007am_cycle["tube_wide_repair_bound"]
    raw = _fraction(bound["raw_wiener_error_upper"])
    repair = _fraction(bound["repair_wiener_addition_upper"])
    total = _fraction(bound["repaired_wiener_error_upper"])
    base_error = _fraction(bound["base_coordinate_error_upper"])
    normal_error = _fraction(bound["normal_coordinate_error_upper"])
    base_margin = _fraction(bound["base_margin"])
    normal_margin = _fraction(bound["normal_margin"])

    assert bound["fresh_p85_candidate_reproduced_exactly"]
    assert bound["registered_float_values_match"]
    assert bound["observed_float_values"] == q007am.REGISTERED_NEW_TUBE_FLOATS
    assert total == raw + repair
    assert float(raw) == pytest.approx(2.7067398403858536e-22)
    assert float(repair) == pytest.approx(4.959477728036884e-22)
    assert float(total) == pytest.approx(7.666217568422737e-22)
    assert float(total / raw) == pytest.approx(2.8322698229209555)
    assert float(base_error) == pytest.approx(1.1581233824834727e-21)
    assert float(base_error / base_margin) == pytest.approx(0.02326102601246388)
    assert float(normal_error) == pytest.approx(2.2935127565743277e-20)
    assert float(normal_error / normal_margin) == pytest.approx(
        2.5079552005207522e-8
    )
    assert bound["base_reentry_budget_passed"]
    assert bound["normal_reentry_budget_passed"]
    assert bound["repair_map_well_defined_on_registered_component_tube"]
    assert all(bound["arithmetic_identities"].values())
    assert bound["all_arithmetic_identities_pass"]
    assert not bound["triangle_bound_uses_center_cancellation"]
    assert not bound["triangle_bound_uses_spatial_fourier_phase"]
    assert not bound["q007z_selected_wave_bound_used"]
    assert bound["passed"]


def test_q007am_seals_sources_context_and_new_box_probes(
    q007am_cycle: dict,
) -> None:
    sources = q007am_cycle["source_registration"]
    context = q007am_cycle["context_audit"]
    probes = q007am_cycle["probe_registration"]

    assert sources["observed_sha256"] == q007am.REGISTERED_SOURCE_SHA256
    assert sources["sha256_match"]
    assert sources["passed"]
    assert context["runtime"]["gmpy2_version"] == "2.3.1"
    assert context["runtime"]["mpfr_version"] == "MPFR 4.2.2"
    assert context["runtime"]["gmp_version"] == "GMP 6.3.0"
    assert context["runtime"]["precision_bits"] == 85
    assert context["context_restored"]
    assert context["passed"]
    assert probes["probe_count"] == 4
    assert probes["probe_digest_sha256"] == q007am.REGISTERED_Q007Y_PROBE_DIGEST
    assert all(
        probe["fixed_leaf_exact"]
        and probe["component_box_strict"]
        and _fraction(probe["minimum_population"]) > 0
        and probe["passed"]
        for probe in probes["probes"]
    )
    assert probes["passed"]


def test_q007am_finite_repairs_restore_conservation_exactly(
    q007am_cycle: dict,
) -> None:
    campaign = q007am_cycle["finite_campaign"]

    assert campaign["probe_count"] == 4
    assert campaign["summary"] == q007am.EXPECTED_FINITE_SUMMARY
    assert campaign["passed"]
    for probe in campaign["probes"]:
        assert probe["input_repair"]["solver_and_distribution_passed"]
        assert probe["input_repair"]["operations_exact_and_positive"]
        assert probe["input_repair"]["exact_conservation_restored"]
        assert probe["input_repair"]["passed"]
        assert probe["output_repair"]["solver_and_distribution_passed"]
        assert probe["output_repair"]["operations_exact_and_positive"]
        assert probe["output_repair"]["exact_conservation_restored"]
        assert probe["output_repair"]["passed"]
        conservation = probe["conservation"]
        assert conservation["repaired_input_exact"]
        assert conservation["exact_map_preserves_leaf"]
        assert conservation["repaired_output_exact"]
        for stage in ("repaired_input", "repaired_post_filter"):
            assert _fraction(conservation[stage]["mass"]) == 289
            assert _fraction(conservation[stage]["momentum_x"]) == 0
            assert _fraction(conservation[stage]["momentum_y"]) == 0
        assert probe["repair_solver_and_operations_passed"]
        assert probe["exact_conservation_restored"]
        assert probe["passed"]


def test_q007am_finite_stages_fit_new_bounds_and_reproduce_old_observations(
    q007am_cycle: dict,
) -> None:
    campaign = q007am_cycle["finite_campaign"]
    regression = q007am_cycle["finite_campaign_regression"]

    for probe in campaign["probes"]:
        assert probe["backend_operation_domain"]["passed"]
        assert probe["raw_stages_pass_q007w_bounds_and_positivity"]
        assert probe["finite_stage_bound_and_positivity_passed"]
        for stage in probe["raw_stage_comparisons"].values():
            observed = _fraction(stage["maximum_observed_component_error"])
            upper = _fraction(stage["registered_component_error_upper"])
            assert observed <= upper
            assert _fraction(stage["minimum_mpfr_population"]) > 0
            assert stage["passed"]
        repaired = probe["repaired_output_comparison"]
        assert _fraction(repaired["maximum_observed_component_error"]) <= _fraction(
            repaired["registered_component_error_upper"]
        )
        assert _fraction(repaired["minimum_mpfr_population"]) > 0
        assert repaired["passed"]

    assert regression["probe_names_match"]
    assert regression["exact_repair_operation_and_conservation_sections_match"]
    assert regression["raw_observed_stage_records_match"]
    assert regression["repaired_output_observed_records_match"]
    assert regression["distribution_digests_match"]
    assert regression["summary_matches"]
    assert regression["passed"]


def test_q007am_accepts_repair_and_budgets_without_induction(
    q007am_cycle: dict,
) -> None:
    assert q007am_cycle["study_validity"] == "passed"
    assert q007am_cycle["hypothesis_outcome"] == "accepted"
    assert q007am_cycle["scientific_classification"] == (
        "distributed MPFR-85 repair restores the Q007ag fixed leaf and "
        "fits both registered one-step budgets"
    )
    assert len(q007am_cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in q007am_cycle["validity_gates"].values())
    assert len(q007am_cycle["hypothesis_gates"]) == 7
    assert all(gate["passed"] for gate in q007am_cycle["hypothesis_gates"].values())
    theorem = q007am_cycle["theorem_consequence"]
    assert theorem["registered_finite_input_repairs_restore_exact_fixed_leaf"]
    assert theorem["registered_finite_output_repairs_restore_exact_fixed_leaf"]
    assert theorem["distributed_repair_is_defined_on_q007ag_component_tube"]
    assert theorem["repair_aware_base_and_normal_budgets_fit_q007ag_margins"]
    assert not theorem["q007ag_repaired_mpfr85_tube_self_map_certified"]
    assert not theorem["all_iterate_repaired_mpfr85_q007ag_invariance_certified"]
    assert not theorem["same_initial_q007ag_shadowing_certified"]
    assert "does not compose" in q007am_cycle["claim_boundary"]
    assert "Finite probes are implementation regressions" in (
        q007am_cycle["claim_boundary"]
    )
    assert not any(q007am_cycle["preserved_prior_outcomes"].values())


def test_q007am_records_provenance_and_deterministic_digests(
    q007am_cycle: dict,
) -> None:
    runner_path = Path(q007am.__file__).resolve()

    assert q007am._runner_source_metadata() == {
        "filename": "q007am_propagated_tube_distributed_repair.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    digest_keys = (
        "input_digest_sha256",
        "probe_digest_sha256",
        "finite_result_digest_sha256",
        "result_digest_sha256",
    )
    assert all(
        isinstance(q007am_cycle[key], str) and len(q007am_cycle[key]) == 64
        for key in digest_keys
    )
    assert q007am_cycle["probe_digest_sha256"] == (
        q007am_cycle["probe_registration"]["probe_digest_sha256"]
    )
    assert q007am_cycle["finite_result_digest_sha256"] == (
        q007am_cycle["finite_campaign"]["result_digest_sha256"]
    )
    json.dumps(q007am_cycle, allow_nan=False)


def test_q007am_artifact_reproduces_the_accepted_repair_audit(
    q007am_cycle: dict,
) -> None:
    runner_path = Path(q007am.__file__).resolve()
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q007am_propagated_tube_distributed_repair.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007am_propagated_tube_distributed_repair.py",
        "sha256": "a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q007am_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5"
    )
    assert artifact["cycle"]["probe_digest_sha256"] == (
        "a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329"
    )
    assert artifact["cycle"]["finite_result_digest_sha256"] == (
        "905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2"
    )
