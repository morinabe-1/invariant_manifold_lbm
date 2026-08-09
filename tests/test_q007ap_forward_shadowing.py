from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ap_forward_shadowing as q007ap
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ap_cycle() -> dict:
    return q007ap.run_forward_shadowing_audit()


def test_q007ap_seals_inputs_and_replays_required_cycles(
    q007ap_cycle: dict,
) -> None:
    inputs = q007ap_cycle["input_artifacts"]
    reproduction = q007ap_cycle["fresh_reproductions"]

    assert set(inputs) == {"q007ab", "q007ag", "q007am", "q007ao"}
    assert all(record["passed"] for record in inputs.values())
    assert reproduction["q007ab"]["stored_cycle_reproduced_exactly"]
    assert reproduction["q007ab"]["validity_gate_count"] == 6
    assert reproduction["q007ab"]["hypothesis_gate_count"] == 6
    assert reproduction["q007ab"]["passed"]
    assert reproduction["q007ao"]["stored_cycle_reproduced_exactly"]
    assert reproduction["q007ao"]["validity_gate_count"] == 7
    assert reproduction["q007ao"]["hypothesis_gate_count"] == 6
    assert reproduction["q007ao"]["q007an_transitive_reproduction_pass"]
    assert reproduction["q007ao"]["q007an_nested_cycle_names"] == [
        "q007ag",
        "q007ai",
        "q007am",
    ]
    assert reproduction["q007ao"]["passed"]
    assert reproduction["passed"]


def test_q007ap_aligns_fixed_coordinate_and_both_tube_trajectories(
    q007ap_cycle: dict,
) -> None:
    alignment = q007ap_cycle["scope_alignment"]

    assert alignment["coordinate_definition"] == (
        "C x=(L x,JQ x) with direct-sum selected-l1 plus registered "
        "external-coordinate norm"
    )
    assert alignment["coordinate_is_fixed_linear_not_graph_relative"]
    assert alignment["comparison_times"] == (
        "sampling times after every repair"
    )
    assert alignment[
        "only_rho_and_tau_changed_from_q007ab_constant_family"
    ]
    assert alignment["exact_q007ag_trajectory_stays_in_tube"]
    assert alignment["repaired_q007ao_trajectory_stays_in_tube"]
    assert alignment["fixed_leaf_target_alignment"]
    assert alignment["outer_and_initial_radius_alignment"]
    assert alignment["passed"]


def test_q007ap_fixed_coordinate_lipschitz_formula_is_exact(
    q007ap_cycle: dict,
) -> None:
    audit = q007ap_cycle["coordinate_lipschitz_audit"]
    selected_linear = _fraction(
        audit["selected_linear_contraction_upper"]
    )
    external_linear = _fraction(
        audit["external_linear_contraction_upper"]
    )
    selected_synthesis = _fraction(audit["selected_synthesis_upper"])
    external_synthesis = _fraction(audit["external_synthesis_upper"])
    selected_analysis = _fraction(
        audit["selected_nonlinear_analysis_upper"]
    )
    external_analysis = _fraction(
        audit["external_nonlinear_analysis_upper"]
    )
    derivative = _fraction(
        audit["nonlinear_derivative_at_tube_state_upper"]
    )
    nonlinear = _fraction(
        audit["nonlinear_coordinate_lipschitz_increment_upper"]
    )
    lipschitz = _fraction(
        audit["fixed_coordinate_full_map_lipschitz_upper"]
    )

    assert nonlinear == (
        selected_analysis + external_analysis
    ) * derivative * max(selected_synthesis, external_synthesis)
    assert lipschitz == max(selected_linear, external_linear) + nonlinear
    assert _fraction(audit["fixed_coordinate_contraction_gap"]) == (
        1 - lipschitz
    )
    assert lipschitz < 1
    assert audit["fixed_coordinate_full_map_lipschitz_upper"][
        "float"
    ] == pytest.approx(0.9920957426381974)
    assert audit["only_q007ag_state_radius_and_nonlinear_derivative_substituted"]
    assert audit["all_arithmetic_identities_pass"]
    assert audit["registered_float_values_match"]
    assert audit["passed"]


def test_q007ap_combines_initial_and_local_defects_without_double_counting(
    q007ap_cycle: dict,
) -> None:
    coordinate = q007ap_cycle["coordinate_lipschitz_audit"]
    defects = q007ap_cycle["defect_audit"]
    selected = _fraction(
        defects["initial_selected_coordinate_error_upper"]
    )
    physical = _fraction(defects["initial_physical_wiener_error_upper"])
    external = _fraction(
        defects["initial_external_coordinate_error_upper"]
    )
    initial = _fraction(defects["initial_coordinate_error_upper"])
    graph_shift = _fraction(
        defects["initial_graph_shift_membership_upper_not_added"]
    )
    step_selected = _fraction(
        defects["step_selected_coordinate_defect_upper"]
    )
    step_external = _fraction(
        defects["step_external_coordinate_defect_upper"]
    )
    step = _fraction(defects["step_coordinate_defect_upper"])

    assert external == _fraction(
        coordinate["external_nonlinear_analysis_upper"]
    ) * physical
    assert initial == selected + external
    assert graph_shift > 0
    assert initial != selected + external + graph_shift
    assert step == step_selected + step_external
    assert defects["initial_graph_shift_not_double_counted"]
    assert defects["q007ao_initial_bound_ready"]
    assert defects["q007am_step_bound_ready"]
    assert defects["all_arithmetic_identities_pass"]
    assert defects["registered_float_values_match"]
    assert defects["passed"]


def test_q007ap_geometric_recurrence_closes_the_accuracy_gate(
    q007ap_cycle: dict,
) -> None:
    shadow = q007ap_cycle["shadow_recurrence_audit"]
    initial = _fraction(shadow["initial_coordinate_error_upper"])
    step = _fraction(shadow["step_coordinate_defect_upper"])
    lipschitz = _fraction(shadow["fixed_coordinate_lipschitz_upper"])
    gap = _fraction(shadow["fixed_coordinate_contraction_gap"])
    stationary = _fraction(shadow["stationary_coordinate_error_upper"])
    uniform = _fraction(
        shadow["uniform_all_iterate_coordinate_error_upper"]
    )
    synthesis = _fraction(shadow["direct_sum_synthesis_upper"])
    physical = _fraction(
        shadow["uniform_all_iterate_physical_wiener_error_upper"]
    )
    state_radius = _fraction(shadow["tube_state_wiener_radius"])
    ratio = _fraction(
        shadow["uniform_physical_to_tube_state_radius_ratio"]
    )

    assert gap == 1 - lipschitz
    assert gap * stationary == step
    assert lipschitz * stationary + step == stationary
    assert uniform == max(initial, stationary)
    assert physical == synthesis * uniform
    assert ratio == physical / state_radius
    assert ratio < q007ap.RELATIVE_TUBE_ACCURACY_THRESHOLD
    assert physical < _fraction(
        shadow["registered_absolute_wiener_accuracy_threshold"]
    )
    assert physical == pytest.approx(8.803831096064757e-18)
    assert ratio == pytest.approx(6.096261293035372e-8)
    assert shadow["fixed_coordinate_map_is_contractive"]
    assert shadow["fixed_point_identity_passed"]
    assert shadow["recurrence_interval_invariant"]
    assert shadow["registered_accuracy_threshold_passed"]
    assert shadow["passed"]


def test_q007ap_accepts_only_same_initial_sampling_time_forward_shadowing(
    q007ap_cycle: dict,
) -> None:
    assert q007ap_cycle["study_validity"] == "passed"
    assert q007ap_cycle["hypothesis_outcome"] == "accepted"
    assert q007ap_cycle["scientific_classification"] == (
        "propagated-tube fixed-coordinate contraction certifies "
        "all-iterate MPFR-85 forward shadowing"
    )
    assert len(q007ap_cycle["validity_gates"]) == 7
    assert all(
        gate["passed"] for gate in q007ap_cycle["validity_gates"].values()
    )
    assert len(q007ap_cycle["hypothesis_gates"]) == 6
    assert all(
        gate["passed"]
        for gate in q007ap_cycle["hypothesis_gates"].values()
    )
    theorem = q007ap_cycle["theorem_consequence"]
    assert theorem["fixed_coordinate_exact_map_is_contractive_on_q007ag"]
    assert theorem[
        "same_initial_forward_coordinate_error_is_uniform_all_iterate"
    ]
    assert theorem[
        "same_initial_forward_physical_error_meets_tube_scale_gate"
    ]
    assert theorem["q007ao_exact_initialization_to_all_iterate_shadowing"]
    assert not theorem["bi_infinite_shadowing_certified"]
    assert not theorem["intermediate_stage_distance_certified"]
    assert not theorem["arbitrary_q007ag_boundary_initialization_certified"]
    assert "sampling-time forward-error bound" in q007ap_cycle[
        "claim_boundary"
    ]
    assert "not a bi-infinite shadowing lemma" in q007ap_cycle[
        "claim_boundary"
    ]
    assert not any(q007ap_cycle["preserved_prior_outcomes"].values())


def test_q007ap_records_provenance_and_deterministic_digests(
    q007ap_cycle: dict,
) -> None:
    runner_path = Path(q007ap.__file__).resolve()
    recurrence_sections = {
        key: q007ap_cycle[key]
        for key in (
            "fresh_reproductions",
            "scope_alignment",
            "coordinate_lipschitz_audit",
            "defect_audit",
            "shadow_recurrence_audit",
        )
    }
    result_sections = {
        **recurrence_sections,
        "validity_gates": q007ap_cycle["validity_gates"],
        "hypothesis_gates": q007ap_cycle["hypothesis_gates"],
        "study_validity": q007ap_cycle["study_validity"],
        "hypothesis_outcome": q007ap_cycle["hypothesis_outcome"],
        "scientific_classification": q007ap_cycle[
            "scientific_classification"
        ],
    }

    assert q007ap._runner_source_metadata() == {
        "filename": "q007ap_forward_shadowing.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert source_metadata()["package_version"] == "0.1.0"
    assert q007ap_cycle["input_digest_sha256"] == (
        q007ap._canonical_json_sha256(
            {
                "input_artifacts": q007ap_cycle["input_artifacts"],
                "registered_parameters": q007ap_cycle[
                    "registered_parameters"
                ],
            }
        )
    )
    assert q007ap_cycle["recurrence_digest_sha256"] == (
        q007ap._canonical_json_sha256(recurrence_sections)
    )
    assert q007ap_cycle["result_digest_sha256"] == (
        q007ap._canonical_json_sha256(result_sections)
    )
    assert all(
        len(q007ap_cycle[key]) == 64
        for key in (
            "input_digest_sha256",
            "recurrence_digest_sha256",
            "result_digest_sha256",
        )
    )
    json.dumps(q007ap_cycle, allow_nan=False)
