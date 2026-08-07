from __future__ import annotations

import json

from ttim_lbm.studies import (
    run_manufactured_quadratic_study,
    run_q004b_branch_tracking_study,
    run_q005_nonresonance_study,
    run_q006r_study,
    run_q006s_stripe_study,
)


def test_q004b_rejects_global_labels_and_accepts_valid_cluster_prefixes() -> None:
    result = run_q004b_branch_tracking_study()
    assert result["outcome"] == "accepted"
    assert result["superseded_question_outcome"]["outcome"] == "rejected"
    assert len(result["paths"]) == 12
    assert min(path["validated_k_c"] for path in result["paths"]) > 0.7
    assert max(
        path["path_reversal_maximum_principal_angle"]
        for path in result["paths"]
    ) < 1.0e-6
    assert max(
        path["quarter_turn_maximum_principal_angle"]
        for path in result["paths"]
    ) < 1.0e-6
    json.dumps(result)


def test_manufactured_study_passes_nontrivial_and_resonance_gates() -> None:
    result = run_manufactured_quadratic_study()
    assert result["outcome"] == "accepted"
    assert result["reduced_hessian_relative_error"] < 1.0e-12
    assert result["exact_resonance_rejected"] is True
    assert result["near_resonance_sweep"][-1]["condition_number"] > 1.0e4
    json.dumps(result)


def test_q005_validly_rejects_isotropic_candidate_and_qualifies_stripe() -> None:
    result = run_q005_nonresonance_study()
    assert result["study_validity"] == "passed"
    assert result["hypothesis_outcome"] == "rejected"
    assert result["summary"]["campaign_count"] == 16
    assert result["summary"]["minimum_shell_compatible_nonunique_count"] == 16
    assert (
        result["summary"]["falsified_registered_isotropic_candidate_count"]
        == 16
    )
    assert result["summary"]["radial_normal_attraction_failure_count"] > 0
    assert result["summary"]["maximum_stripe_condition_number"] < 1.0e8
    assert all(gate["passed"] for gate in result["gates"].values())
    json.dumps(result, allow_nan=False)


def test_q006s_accepts_only_the_registered_finite_grid_stripe_oracle() -> None:
    result = run_q006s_stripe_study()

    assert result["study_validity"] == "passed"
    assert result["hypothesis_outcome"] == "accepted"
    assert result["registered_scope"]["grid"] == [1, 17]
    assert result["registered_scope"]["pilot_seed_not_used_for_gates"] == 20260801
    assert result["registered_scope"]["residual_seed"] == 20260802
    assert result["registered_scope"]["shadow_seed"] == 20260803
    assert all(gate["passed"] for gate in result["gates"].values())
    assert result["residual_order_campaign"]["amplitudes"] == [
        0.000625,
        0.00125,
        0.0025,
        0.005,
        0.01,
    ]
    assert len(result["residual_order_campaign"]["direction_records"]) == 64
    assert result["shadowing_campaign"]["quadratic"]["steps"] == 100
    assert (
        len(result["shadowing_campaign"]["quadratic"]["direction_records"])
        == 32
    )
    assert (
        result["residual_order_campaign"]["summary"][
            "maximum_directional_residual_ratio"
        ]
        < 0.1
    )
    assert (
        result["shadowing_campaign"]["quadratic"]["summary"][
            "maximum_absolute_error"
        ]
        < 1.0e-5
    )
    assert (
        result["shadowing_campaign"]["quadratic"]["summary"][
            "maximum_perturbation_relative_error"
        ]
        < 1.0e-2
    )
    assert (
        result["shadowing_campaign"]["maximum_absolute_error_improvement_ratio"]
        < 0.1
    )
    assert result["quotient_lift_check"]["maximum_absolute_difference"] < 1.0e-12
    json.dumps(result, allow_nan=False)


def test_q006r_validly_rejects_only_the_normal_dominance_axis() -> None:
    result = run_q006r_study()
    cycle = result["cycle"]

    assert result["study_gate"] == "passed"
    assert result["scientific_outcome"] == "rejected"
    assert cycle["coefficient_solvability"]["passed"]
    assert not cycle["linear_normal_dominance_prequalification"]["passed"]
    assert cycle["terminal_summary"]["nonempty_additions"] == 0
    assert cycle["terminal_summary"]["final_real_dimension"] == 16
    json.dumps(result, allow_nan=False)
