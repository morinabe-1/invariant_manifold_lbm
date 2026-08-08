from __future__ import annotations

import json
from pathlib import Path

from ttim_lbm.experiments import run_d2q9_baseline
from ttim_lbm.provenance import source_metadata

ARTIFACT_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "research" / "artifacts"
)


def test_committed_artifact_matches_current_package_source() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "d2q9_baseline.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    fresh = run_d2q9_baseline()

    assert artifact["schema_version"] == fresh["schema_version"]
    assert artifact["source"] == fresh["source"]
    assert artifact["baseline_gate"] == "passed"


def test_q004b_artifact_preserves_registered_scope_and_passed_gates() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q004b_and_manufactured.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["mathematical_scope"] == {
        "construction_grid_parity": "odd periodic square grids only",
        "even_grids": "diagnostic parity and obstruction analysis only",
        "conservation_treatment": (
            "fixed global mass and momentum leaf for future nonzero-mode charts"
        ),
        "manifold_claim": (
            "candidate until Q005 nonresonance and normal-attraction gates pass"
        ),
    }
    branch_tracking, manufactured = artifact["cycles"]
    assert branch_tracking["outcome"] == "accepted"
    assert branch_tracking["superseded_question_outcome"]["outcome"] == "rejected"
    assert manufactured["outcome"] == "accepted"
    assert all(gate["passed"] for gate in branch_tracking["gates"].values())
    assert all(gate["passed"] for gate in manufactured["gates"].values())


def test_q005_artifact_records_a_valid_falsification() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q005_nonresonance.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["cycle"]["study_validity"] == "passed"
    assert artifact["cycle"]["hypothesis_outcome"] == "rejected"
    assert all(
        gate["passed"] for gate in artifact["cycle"]["gates"].values()
    )
    assert (
        artifact["cycle"]["summary"]["minimum_shell_compatible_nonunique_count"]
        == 16
    )
    assert (
        artifact["cycle"]["summary"][
            "falsified_registered_isotropic_candidate_count"
        ]
        == 16
    )


def test_q006s_artifact_records_only_the_finite_grid_stripe_claim() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006s_stripe.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["mathematical_scope"] == {
        "construction": "finite-grid y-independent stripe solver oracle",
        "construction_grid": [1, 17],
        "square_grid_lift": [17, 17],
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "local quadratic candidate chart only; no full 2D or "
            "grid-uniform SSM existence claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["gates"].values())
    assert cycle["registered_scope"]["residual_seed"] == 20260802
    assert cycle["registered_scope"]["shadow_seed"] == 20260803
    assert (
        cycle["non_gating_domain_stress"][
            "maximum_directional_residual_ratio_at_0p1"
        ]
        > 0.1
    )


def test_q006r_artifact_separates_coefficient_and_normal_dominance_outcomes() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006r_mode_closure.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "construction": "finite-grid quadratic spectral closure audit",
        "construction_grid": [17, 17],
        "omega": 1.2,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "coefficient and linear spectral prequalification only; no "
            "existence, uniqueness, or nonlinear normal-attraction claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert cycle["coefficient_solvability"]["passed"]
    assert all(
        gate["passed"]
        for gate in cycle["coefficient_solvability"]["gates"].values()
    )
    assert not cycle["linear_normal_dominance_prequalification"]["passed"]
    assert (
        cycle["linear_normal_dominance_prequalification"][
            "normal_dominance_gap"
        ]
        < 0.0
    )
    assert cycle["terminal_summary"]["nonempty_additions"] == 0
    assert cycle["terminal_summary"]["terminal_pair_count"] == 136


def test_q006n_artifact_records_the_preregistered_mixed_refinement_outcome() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006n_normal_refinement.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "inconclusive"
    assert artifact["mathematical_scope"] == {
        "construction": "finite registered odd-grid refinement audit",
        "grid_sizes": [9, 17, 33, 65, 129],
        "omegas": [1.0, 1.2, 1.5, 1.8],
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "finite-ladder obstruction classification only; no theorem for "
            "all odd grids and no invariant-manifold existence claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "inconclusive"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["conditions"]) == 20
    assert cycle["summary"]["refinement_negative_gap_count"] == 16
    assert cycle["summary"]["refinement_axial_near_nyquist_worst_count"] == 16
    assert cycle["summary"]["refinement_coefficient_and_blockwise_pass_count"] == 13
    assert not cycle["summary"]["registered_obstruction_supported"]
    assert cycle["summary"]["viable_omegas"] == []


def test_q006c_artifact_records_only_the_finite_ladder_scaling_claim() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006c_coefficient_scaling.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "construction": "finite registered small-wave coefficient scaling audit",
        "grid_sizes": [17, 33, 65, 129, 257],
        "fit_grid_sizes": [33, 65, 129, 257],
        "omegas": [1.0, 1.2, 1.5, 1.8],
        "conservation_treatment": "fixed global mass and momentum leaf",
        "coordinate_normalizations": [
            "symbol-local Fourier amplitude",
            "global-L2-isometric Fourier coefficient",
        ],
        "manifold_claim": (
            "finite-ladder coefficient scaling diagnosis only; no asymptotic "
            "theorem, normal-attraction repair, or manifold existence claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["conditions"]) == 20
    assert len(cycle["fits"]) == 8
    assert cycle["summary"]["all_registered_scaling_windows_passed"]
    assert cycle["summary"]["n257_materially_forced_near_witness_count"] == 56
    assert cycle["summary"]["n257_outside_target_witness_count"] == 0


def test_q006f_artifact_records_the_valid_filtered_family_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006f_checkerboard_filter.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "construction": "finite registered conservative checkerboard-filter audit",
        "grid_sizes": [17, 33, 65, 129, 257],
        "etas": [0.0, 0.01, 0.02, 0.03, 0.05],
        "omegas": [1.0, 1.2, 1.5, 1.8],
        "filter_order": "post-BGK-step population-wise five-point convolution",
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "filtered finite-ladder prequalification only; no all-grid "
            "theorem, nonlinear normal-attraction proof, or invariant-"
            "manifold existence or uniqueness claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["selected_family"] is None
    assert cycle["summary"]["viable_family_count"] == 0
    assert len(cycle["conditions"]) == 100
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(family["coefficient_passed"] for family in cycle["families"])
    assert all(
        not family["spectral_gates"]["normal_dominance_gap"]["passed"]
        for family in cycle["families"]
    )


def test_q006g_artifact_records_only_the_symbol_level_tangency_claim() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006g_low_wave_tangency.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "construction": "diagonal low-wave symbol-level tangency audit",
        "grid_sizes": [33, 65, 129, 257, 513, 1025, 2049],
        "fit_grid_sizes": [129, 257, 513, 1025, 2049],
        "etas": [0.0, 0.01, 0.02, 0.03, 0.05],
        "omegas": [1.0, 1.2, 1.5, 1.8],
        "wave_orbit": [[1, 1], [-1, 1], [-1, -1], [1, -1]],
        "manifold_claim": (
            "same-sector finite-ladder scaling diagnosis only; no full-zone "
            "prequalification, threshold relaxation, or invariant-manifold "
            "existence or uniqueness claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert len(cycle["conditions"]) == 140
    assert len(cycle["fits"]) == 20
    assert cycle["summary"]["fit_pass_count"] == 20
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(fit["passed"] for fit in cycle["fits"])


def test_q006h_artifact_records_only_the_finite_ladder_prequalification() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006h_cluster_complete.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "construction": (
            "first-shell 24-mode cluster-complete filtered-family audit"
        ),
        "grid_sizes": [17, 33, 65, 129, 257],
        "etas": [0.0, 0.01, 0.02, 0.03, 0.05],
        "omegas": [1.0, 1.2, 1.5, 1.8],
        "selected_real_dimension": 24,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "cluster-complete filtered finite-ladder prequalification only; "
            "no all-grid theorem, nonlinear normal-attraction proof, or "
            "invariant-manifold existence or uniqueness claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["conditions"]) == 100
    assert len(cycle["fits"]) == 40
    assert len(cycle["families"]) == 20
    assert len(cycle["viable_families"]) == 6
    assert cycle["selected_family"]["eta"] == 0.01
    assert cycle["selected_family"]["omega"] == 1.5
    assert cycle["summary"]["selected_material_witness_class_counts"] == {
        "axial_acoustic_self_second_harmonic": 16,
        "axial_shear_diagonal_mixed_harmonic": 16,
        "diagonal_acoustic_self_second_harmonic": 8,
    }


def test_q006i_artifact_records_the_valid_single_gate_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006i_full2d_quadratic.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "construction": "filtered full-2D dense quadratic candidate chart",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "selected_real_dimension": 24,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "registered finite-direction N=17 candidate-chart verification "
            "only; no all-grid theorem, coordinate-ball guarantee, or "
            "invariant-manifold existence or uniqueness claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    failed = [
        name
        for name, gate in cycle["hypothesis_gates"].items()
        if not gate["passed"]
    ]
    assert failed == ["global_conservation"]
    assert cycle["construction"]["diagnostics"]["pair_count"] == 300
    assert cycle["construction"]["diagnostics"][
        "numerical_singular_block_count"
    ] == 0


def test_q006j_artifact_records_the_valid_unresolved_projection_failure() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006j_conservation_drift.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "Q006i float64 global-conservation drift source audit",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "trajectory_count": 64,
        "steps": 100,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "claim": (
            "finite registered-trajectory arithmetic diagnosis only; the "
            "Q006i rejection and threshold remain unchanged, with no exact "
            "all-state or all-time conservation claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["scientific_classification"] == (
        "structural or unresolved conservation defect"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    failed_projection_gates = [
        name
        for name, gate in cycle["projection_gates"].items()
        if not gate["passed"]
    ]
    assert failed_projection_gates == ["projected_conservation"]
    assert cycle["summary"]["trajectory_count"] == 64
    assert cycle["summary"]["stage_record_count"] == 6400


def test_q006k_artifact_records_only_the_symmetry_breaking_diagnostic() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006k_projection_representability.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "Q006j fixed-leaf projection representability audit",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "trajectory_count": 64,
        "steps": 100,
        "controls": ["standard", "uniform", "localized"],
        "claim": (
            "finite registered-trajectory arithmetic diagnosis only; the "
            "fixed-site control is symmetry breaking and is not adopted as "
            "the production map or used to revise Q006i or Q006j"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "uniform projection representability failure localized"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert "symmetry-breaking diagnostic only" in cycle["claim_boundary"]
    assert cycle["summary"]["trajectory_count"] == 64
    assert cycle["summary"]["total_control_step_count"] == 19200


def test_q006l_artifact_records_only_the_unique_anchor_arithmetic_audit() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006l_covariant_correction.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "stagewise state-covariant conservative arithmetic",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "trajectory_count": 64,
        "steps": 100,
        "corrected_stages": ["collision", "filter"],
        "symmetry_generators": [
            "translation_y",
            "translation_x",
            "quarter_turn",
        ],
        "claim": (
            "finite unique-anchor trajectory audit only; the nonsmooth "
            "global-residual control is not adopted as the production map "
            "and does not revise Q006i-Q006k"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "covariant anchor correction controls registered drift"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert "nonsmooth at anchor switches" in cycle["claim_boundary"]
    assert cycle["summary"]["trajectory_count"] == 64
    assert cycle["summary"]["total_control_step_count"] == 19200


def test_q006m_artifact_records_only_the_unique_anchor_obstruction() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006m_anchor_obstruction.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "equivariant unique-site anchor obstruction",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "translation_group": "Z_17 x Z_17",
        "direction_count": 32,
        "amplitudes": [1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5, 1.0e-6, 1.0e-7],
        "claim": (
            "exact uniform-state fixed-point obstruction for unique-site "
            "selectors plus a finite shrinking-gap diagnostic only; no "
            "exclusion of anchor-free equivariant arithmetic and no revision "
            "of Q006i-Q006l"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "equivariant unique-anchor obstruction confirmed"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["summary"]["direction_amplitude_record_count"] == 384
    assert cycle["summary"]["failed_gap_ladder_count"] == 0
    assert "only unique-site selectors" in cycle["claim_boundary"]


def test_q006o_artifact_records_only_the_anchor_free_policy_audit() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006o_forward_error_budget.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "anchor-free arithmetic-policy comparison",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "trajectory_count": 64,
        "steps": 100,
        "controls": ["unmodified_standard", "uniform_projection"],
        "claim": (
            "finite registered-trajectory operational ULP envelope and "
            "uniform-control selection only; no all-state roundoff theorem "
            "and no revision of the sealed Q006i-Q006j outcomes"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "unmodified equivariant map with registered forward-error budget preferred"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["standard_policy_gates"].values())
    assert not any(gate["passed"] for gate in cycle["uniform_policy_gates"].values())
    assert cycle["summary"]["component_budget_check_count"] == 19200
    assert cycle["summary"]["budget_violation_count"] == 0
    assert "not an all-state" in cycle["claim_boundary"]


def test_q006p_artifact_preserves_original_and_policy_columns() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006p_dual_reporting.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "Q006i/Q006o dual-reporting integration",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "trajectory_count": 64,
        "steps": 100,
        "original_threshold": 1.0e-12,
        "claim": (
            "same-trajectory integration audit only; the sealed Q006i "
            "rejection remains unchanged and an independent holdout is "
            "required before degree continuation"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "dual reporting supports unmodified-map chart continuation"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["dual_decision_gates"].values())
    assert cycle["summary"]["original_failed_gate_count"] == 1
    assert cycle["summary"]["policy_failed_gate_count"] == 0
    assert cycle["original_column"]["sealed_hypothesis_outcome"] == "rejected"
    assert "independent holdout" in cycle["claim_boundary"]


def test_q006q_artifact_records_the_independent_holdout() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006q_forward_error_holdout.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "independent forward-error-policy holdout",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "trajectory_count": 128,
        "trajectory_step_count": 16000,
        "component_check_count": 48000,
        "scenarios": [
            {
                "name": "long_horizon",
                "direction_seed": 20260811,
                "amplitude": 0.005,
                "steps": 200,
            },
            {
                "name": "large_amplitude",
                "direction_seed": 20260812,
                "amplitude": 0.02,
                "steps": 50,
            },
        ],
        "claim": (
            "two finite-trajectory holdout scenarios only; no all-state or "
            "all-horizon theorem and no invariance claim at amplitude 0.02"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "independent holdout supports registered forward-error policy"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["scenario_policy_gates"].values())
    assert all(gate["passed"] for gate in cycle["holdout_policy_gates"].values())
    assert cycle["summary"]["trajectory_count"] == 128
    assert cycle["summary"]["component_budget_check_count"] == 48000
    assert cycle["summary"]["budget_violation_count"] == 0
    assert "not an all-state" in cycle["claim_boundary"]


def test_q007a_artifact_records_only_operator_prequalification() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007a_cubic_prequalification.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "order-three homological-family prequalification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "complex_mode_count": 24,
        "unordered_pair_control_count": 300,
        "unordered_triple_count": 2600,
        "claim": (
            "operator-only finite-grid prequalification; no cubic forcing, "
            "coefficient, residual-order, shadowing, or SSM claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "order-three homological family prequalified on registered grid"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["triple_summary"]["record_count"] == 2600
    assert cycle["triple_summary"]["numerically_singular_block_count"] == 0
    assert "operator-only" in cycle["claim_boundary"]


def test_q007b_artifact_records_the_valid_finite_amplitude_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007b_cubic_continuation.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "cubic coefficient and residual continuation",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "unordered_triple_count": 2600,
        "residual_direction_count": 32,
        "shadowing_direction_count": 32,
        "shadowing_steps": 100,
        "claim": (
            "registered finite-grid, direction, amplitude, and 100-step "
            "comparison only; no quartic, TT, all-radius, grid-uniform, "
            "existence, uniqueness, or normal-attraction claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["scientific_classification"] == (
        "cubic continuation does not improve the registered chart"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert cycle["hypothesis_gates"]["held_out_residual_orders"]["passed"]
    assert not cycle["hypothesis_gates"]["held_out_residual_ratio"]["passed"]
    assert cycle["hypothesis_gates"][
        "held_out_directional_shadowing_ratios"
    ]["passed"]
    assert cycle["hypothesis_gates"][
        "cubic_shadowing_forward_error_budget"
    ]["passed"]
    assert (
        cycle["residual_order_campaign"]["summary"][
            "residual_ratio_failure_count"
        ]
        == 9
    )
    assert not cycle["preserved_prior_outcome"]["revised"]
    assert "not a quartic" in cycle["claim_boundary"]


def test_q007b1_artifact_records_only_the_sampled_radius_acceptance() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007b1_cubic_radius.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "independent cubic-radius and immersion audit",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "acceptance_radius": 0.004,
        "residual_direction_count": 64,
        "immersion_direction_count": 64,
        "shadowing_direction_count": 32,
        "shadowing_steps": 100,
        "claim": (
            "registered finite-direction radius and radial-immersion "
            "prequalification only; no full-ball, injectivity, quartic, TT, "
            "grid-uniform, existence, uniqueness, or normal-attraction claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered cubic improvement radius localized without fold signature"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert (
        cycle["radius_campaign"]["summary"][
            "maximum_acceptance_radius_ratio"
        ]
        <= 0.10
    )
    assert (
        cycle["immersion_campaign"]["summary"][
            "minimum_normalized_singular_value"
        ]
        >= 0.8
    )
    assert not cycle["preserved_prior_outcomes"]["revised"]
    assert "does not cover the full" in cycle["claim_boundary"]


def test_q007c_artifact_records_only_quartic_operator_prequalification() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007c_quartic_prequalification.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "order-four homological-family prequalification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "complex_mode_count": 24,
        "unordered_pair_control_count": 300,
        "unordered_triple_control_count": 2600,
        "unordered_quartic_tuple_count": 17550,
        "claim": (
            "operator-only finite-grid prequalification; no quartic forcing, "
            "coefficient, residual-order, radius, shadowing, or invariant-"
            "manifold existence claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "order-four homological family prequalified on registered grid"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["quartic_summary"]["record_count"] == 17550
    assert cycle["quartic_summary"]["numerically_singular_block_count"] == 0
    assert "operator-only" in cycle["claim_boundary"]


def test_q007c1_artifact_records_valid_quartic_performance_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007c1_quartic_continuation.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "quartic coefficient and sampled-radius continuation",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "unordered_quartic_tuple_count": 17550,
        "residual_direction_count": 32,
        "shadowing_direction_count": 32,
        "shadowing_steps": 100,
        "acceptance_radius": 0.01,
        "claim": (
            "registered finite-grid, direction, amplitude, and 100-step "
            "comparison only; no all-ball, injectivity, TT, grid-uniform, "
            "existence, uniqueness, or normal-attraction claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["scientific_classification"] == (
        "quartic continuation does not restore registered radius"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert cycle["hypothesis_gates"]["held_out_residual_orders"]["passed"]
    assert cycle["hypothesis_gates"][
        "held_out_radius_residual_ratios"
    ]["passed"]
    assert not cycle["hypothesis_gates"][
        "held_out_directional_shadowing_ratios"
    ]["passed"]
    assert cycle["hypothesis_gates"][
        "quartic_shadowing_forward_error_budget"
    ]["passed"]
    assert cycle["coefficient_construction"]["summary"]["quartet_count"] == 17550
    assert not cycle["preserved_prior_outcomes"]["revised"]
    assert "32 residual directions" in cycle["claim_boundary"]


def test_q007c2_artifact_records_only_localized_shadow_domain() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007c2_quartic_shadow_radius.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "quartic shadow amplitude-horizon localization",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "direction_count": 64,
        "amplitudes": [0.004, 0.007, 0.01],
        "prefix_horizons": [10, 25, 50, 100],
        "maximum_steps": 100,
        "claim": (
            "registered finite-direction amplitude-horizon localization "
            "only; no all-ball, other-horizon, injectivity, grid-uniform, "
            "existence, uniqueness, normal-attraction, or TT claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "quartic shadowing domain localized on independent directions"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["shadow_domain_campaign"]["trajectory_count"] == 384
    assert cycle["shadow_domain_campaign"]["chart_step_count"] == 38400
    assert cycle["shadow_domain_campaign"]["summary"][
        "quartic_budget_component_check_count"
    ] == 57600
    assert not cycle["preserved_prior_outcomes"][
        "q007c1_radius_0p01_horizon_100_revised"
    ]
    assert "two preregistered" in cycle["claim_boundary"]


def test_q008a_artifact_records_valid_sparse_storage_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q008a_tt_storage_prequalification.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "local Fourier coefficient TT storage prequalification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "complex_mode_count": 24,
        "local_output_count": 9,
        "degrees": [2, 3, 4],
        "tensorization_count": 4,
        "physical_full_dense_tensor_materialized": False,
        "claim": (
            "registered local coefficient storage and fidelity only; no "
            "asymptotic-rank, online-speed, full-chart, rollout, TT-cross, "
            "other-shell, other-grid, existence, or uniqueness claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["selected_candidate"] is None
    assert cycle["scientific_classification"] == (
        "registered TT tensorizations do not beat natural quartic sparse-fiber storage"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    quartic = next(record for record in cycle["degree_records"] if record["degree"] == 4)
    sparse = quartic["natural_sparse_fiber_storage"]
    assert sparse["coefficient_stored_real_scalar_count"] == 315900
    assert all(
        candidate["storage"]["core_stored_real_scalar_count"] > 10 * 315900
        and candidate["storage"]["uncompressed_npz_serialized_bytes"]
        > 10 * sparse["uncompressed_npz_serialized_bytes"]
        and not candidate["storage_hypothesis_passed"]
        for candidate in quartic["candidate_records"]
    )
    assert "four registered local coefficient tensorizations" in cycle[
        "claim_boundary"
    ]


def test_q008c_artifact_records_valid_wave_factorization_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q008c_wave_qtt_prequalification.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "wave-branch and wave-QTT storage prequalification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "complex_mode_count": 24,
        "wave_count": 8,
        "branch_count": 3,
        "local_output_count": 9,
        "degrees": [2, 3, 4],
        "tensorization_count": 4,
        "physical_full_dense_tensor_materialized": False,
        "claim": (
            "registered local coefficient storage and fidelity only; no "
            "asymptotic-rank, online-speed, full-chart, rollout, TT-cross, "
            "other-shell, other-grid, existence, uniqueness, or "
            "normal-attraction claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["selected_candidate"] is None
    assert cycle["scientific_classification"] == (
        "registered wave-factorized TTs do not beat natural quartic sparse-fiber storage"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    quartic = next(record for record in cycle["degree_records"] if record["degree"] == 4)
    sparse = quartic["natural_sparse_fiber_storage"]
    assert sparse["coefficient_stored_real_scalar_count"] == 315900
    assert sparse["uncompressed_npz_serialized_bytes"] == 2615734
    assert all(
        candidate["storage"]["core_stored_real_scalar_count"] > 14 * 315900
        and candidate["storage"]["uncompressed_npz_serialized_bytes"]
        > 13 * sparse["uncompressed_npz_serialized_bytes"]
        and not candidate["storage_hypothesis_passed"]
        for candidate in quartic["candidate_records"]
    )
    assert "four preregistered wave/branch tensorizations" in cycle["claim_boundary"]


def test_q007d_artifact_records_valid_euclidean_normal_dominance_rejection() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007d_normal_cocycle.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "finite-radius projected tangent/normal cocycle",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "direction_count_per_amplitude": 16,
        "amplitudes": [0.004, 0.01],
        "starting_point_count": 33,
        "steps": 10,
        "claim": (
            "registered finite-sample Euclidean-projector diagnostic only; "
            "no full-ball, adapted-norm, true invariant-normal-bundle, grid-"
            "uniform normal-attraction, existence, or uniqueness theorem"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "rejected"
    assert cycle["scientific_classification"] == (
        "registered finite-sample projected normal-cocycle dominance not observed"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert not any(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["coefficient_reproduction"]["match"]
    assert cycle["cocycle_campaign"]["starting_point_count"] == 33
    assert cycle["cocycle_campaign"]["equilibrium_control"]["gamma_10"] > 2.0
    assert all(
        record["summary"]["gamma_10_failure_count"] == 16
        for record in cycle["cocycle_campaign"]["amplitude_records"]
    )
    assert cycle["cocycle_campaign"]["summary"]["maximum_tangent_leakage"] <= 1.0e-3
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert "not a full-ball" in cycle["claim_boundary"]
