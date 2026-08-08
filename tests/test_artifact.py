from __future__ import annotations

import json
from pathlib import Path

from ttim_lbm.experiments import run_d2q9_baseline
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

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


def test_q007e_artifact_records_valid_equilibrium_metric_prequalification() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007e_adapted_metric.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "equilibrium Fourier-Riesz Stein metric prequalification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "selected_complex_dimension": 24,
        "wave_block_count": 289,
        "fixed_leaf_dimension": 2598,
        "horizons": [1, 10],
        "claim": (
            "registered equilibrium single-grid adapted-metric "
            "prequalification only; no finite-radius normal attraction, "
            "true invariant-normal-bundle, grid-uniform bound, existence, "
            "or uniqueness theorem"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "equilibrium Riesz/Stein metric prequalified for finite-radius testing"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["metric_construction"]["summary"]["wave_block_count"] == 289
    assert cycle["metric_construction"]["summary"][
        "fixed_leaf_dimension"
    ] == 2598
    assert cycle["metric_construction"]["summary"][
        "selected_complex_dimension"
    ] == 24
    assert cycle["q007d_reproduction"]["maximum_relative_error"] <= 1.0e-10
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert "not finite-radius normal attraction" in cycle["claim_boundary"]


def test_q007f_artifact_records_valid_fixed_metric_finite_sample_acceptance() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007f_adapted_finite_cocycle.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "fixed-metric finite-radius projected normal cocycle",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "real_reduced_dimension": 24,
        "adapted_fixed_leaf_dimension": 2598,
        "direction_count_per_amplitude": 16,
        "amplitudes": [0.004, 0.01],
        "starting_point_count": 33,
        "steps": 10,
        "metric_reestimated_at_finite_radius": False,
        "claim": (
            "same-direction comparative finite-sample fixed-metric "
            "diagnostic only; no independent holdout, full-ball, true "
            "invariant-normal-bundle, grid-uniform attraction, existence, "
            "or uniqueness theorem"
        ),
    }
    cycle = artifact["cycle"]
    campaign = cycle["adapted_cocycle_campaign"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered finite-sample adapted-metric projected normal-cocycle "
        "dominance observed"
    )
    assert len(cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert campaign["starting_point_count"] == 33
    assert campaign["equilibrium_control"]["gamma_10"] < 1.0
    assert all(
        record["summary"]["maximum_gamma_10"] < 1.0
        and record["summary"]["gamma_10_failure_count"] == 0
        for record in campaign["amplitude_records"]
    )
    assert campaign["summary"]["maximum_tangent_leakage"] <= 1.0e-3
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert "not an independent holdout" in cycle["claim_boundary"]


def test_q007g_artifact_records_the_valid_theorem_readiness_gap() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007g_theorem_readiness.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "not_ready"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "nonresonant-manifold theorem-readiness audit",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "fixed_leaf_real_dimension": 2598,
        "selected_real_dimension": 24,
        "complexified_selected_dimension": 24,
        "registered_theorem": "Cabré--Fontich--de la Llave Theorem 1.2",
        "new_direction_or_defect_campaign": False,
        "claim": (
            "theorem-applicability inventory only; no existence, uniqueness, "
            "nonexistence, proof radius, full-ball normal attraction, or "
            "independent finite-sample claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "not_ready"
    assert cycle["scientific_classification"] == (
        "current evidence is not theorem-ready"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert cycle["spectral_quotient"]["observed_L"] == 89
    assert cycle["order_evidence"]["sector_aware_float64_orders"] == [2, 3, 4]
    assert cycle["order_evidence"]["certified_direct_theorem_orders"] == []
    assert cycle["order_evidence"]["uncertified_direct_theorem_order_count"] == 88
    assert not cycle["readiness"]["qualitative_theorem_ready"]
    assert not cycle["readiness"]["quantitative_chart_ready"]
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert "not an invariant-manifold nonexistence result" in cycle[
        "claim_boundary"
    ]


def test_q007h_artifact_records_the_sealed_symmetry_inconclusive_result() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007h_rational_spectrum.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "failed"
    assert artifact["scientific_outcome"] == "inconclusive"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational-interval linear spectral certification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "fixed_leaf_complex_dimension": 2598,
        "selected_complex_dimension": 24,
        "excluded_complex_dimension": 2574,
        "nonzero_fourier_block_count": 288,
        "tail_degree": 90,
        "claim": (
            "linear fixed-grid certification attempt only; no degrees 2--89 "
            "nonresonance, Riesz projector norm, nonlinear proof radius, "
            "manifold existence, uniqueness, or grid-uniform claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "failed"
    assert cycle["hypothesis_outcome"] == "inconclusive"
    assert not cycle["validity_gates"]["conjugate_and_c4_symmetry"]["passed"]
    assert all(
        gate["passed"]
        for name, gate in cycle["validity_gates"].items()
        if name != "conjugate_and_c4_symmetry"
    )
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["eigencertification"]["selected_count"] == 24
    assert cycle["eigencertification"]["excluded_count"] == 2574
    assert cycle["global_bounds"]["tail_ratio"]["float"] < 1.0
    assert "does not certify degrees 2--89" in cycle["claim_boundary"]


def test_q007h1_artifact_records_the_equivariant_linear_certificate() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007h1_equivariant_spectrum.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "C4-transported rational-interval linear certification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "fixed_leaf_complex_dimension": 2598,
        "selected_complex_dimension": 24,
        "excluded_complex_dimension": 2574,
        "nonzero_fourier_block_count": 288,
        "nonzero_c4_representative_count": 72,
        "tail_degree": 90,
        "claim": (
            "symmetry-equivariant linear fixed-grid certification only; no "
            "degrees 2--89 nonresonance, Riesz projector norm, nonlinear "
            "proof radius, manifold existence, uniqueness, or grid-uniform claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["symbol_covariance"]["mismatch_entry_count"] == 0
    assert cycle["symmetry"][
        "maximum_quarter_turn_endpoint_difference"
    ]["float"] == 0.0
    assert cycle["orbit_transport"][
        "maximum_exact_transport_parameter_difference"
    ]["float"] == 0.0
    assert cycle["global_bounds"]["tail_ratio"]["float"] < 1.0
    assert cycle["sealed_predecessor_outcome"] == {
        "q007h_study_gate": "failed",
        "q007h_scientific_outcome": "inconclusive",
    }
    assert "does not certify degrees 2--89" in cycle["claim_boundary"]


def test_q007i_artifact_records_direct_nonresonance_and_theorem_use() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007i_direct_nonresonance.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational-log direct external nonresonance certification",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "fixed_leaf_real_dimension": 2598,
        "selected_real_dimension": 24,
        "excluded_complex_dimension": 2574,
        "degree_range": [2, 89],
        "selected_disk_count": 6,
        "selected_modulus_type_count": 4,
        "aggregate_count": 2_919_730,
        "expanded_product_count": 869_107_778,
        "claim": (
            "direct external nonresonance and qualitative local theorem "
            "applicability for the fixed conservation leaf only; no explicit "
            "radius, rigorous quartic-jet identification, finite-ball "
            "attraction, grid-uniformity, or continuum limit"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["enumeration"]["aggregate_count"] == 2_919_730
    assert cycle["enumeration"]["expanded_product_count"] == 869_107_778
    assert cycle["enumeration"]["overlap_count"] == 0
    assert cycle["enumeration"]["global_minimum_log_gap"]["float"] >= 1.0e-12
    assert cycle["enumeration"]["global_minimum_gap_witness"]["degree"] == 51
    assert cycle["theorem_consequence"]["theorem_applies"]
    assert cycle["theorem_consequence"]["existence_conclusion"]
    assert not cycle["theorem_consequence"][
        "explicit_neighborhood_radius_available"
    ]
    assert "no explicit neighborhood radius" in cycle["claim_boundary"]


def test_q007j_artifact_records_the_rational_eigencoordinate_bridge() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007j_eigencoordinate_bridge.json"
    runner_path = artifact_path.parents[1] / "q007j_eigencoordinate_bridge.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007j_eigencoordinate_bridge.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational Krawczyk selected-eigencoordinate bridge",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "representative_eigenpair_count": 6,
        "right_left_system_count": 12,
        "claim": (
            "linear eigencoordinate identification only; no Taylor-jet, "
            "explicit-radius, finite-ball, grid-uniform, or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["krawczyk_certification"]["system_count"] == 12
    assert cycle["disc_association"]["unique_membership_count"] == 6
    assert cycle["disc_association"]["assignment_collision_count"] == 0
    assert cycle["transport_and_normalization"][
        "transported_mode_count"
    ] == 24
    assert cycle["transport_and_normalization"][
        "conjugate_label_mismatch_count"
    ] == 0
    assert "does not certify any quadratic" in cycle["claim_boundary"]


def test_q007k_artifact_records_the_rational_quadratic_jet_bridge() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007k_quadratic_jet_bridge.json"
    runner_path = artifact_path.parents[1] / "q007k_quadratic_jet_bridge.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007k_quadratic_jet_bridge.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational graph-gauge quadratic-jet bridge",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "unordered_pair_count": 300,
        "complex_unknown_count": 3024,
        "claim": (
            "degree-two Taylor-jet identification only; no cubic, quartic, "
            "explicit-radius, finite-ball, grid-uniform, or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["eigencoordinate_reconstruction"][
        "proof_digest_mismatch_count"
    ] == 0
    assert cycle["enumeration"]["pair_count"] == 300
    assert cycle["enumeration"]["complex_unknown_count"] == 3024
    assert cycle["krawczyk_certification"]["included_count"] == 300
    assert cycle["krawczyk_certification"][
        "zero_wave_structural_fixed_leaf_count"
    ] == 36
    assert cycle["krawczyk_certification"][
        "internal_graph_gauge_inclusion_count"
    ] == 108
    assert "does not certify cubic or quartic" in cycle["claim_boundary"]


def test_q007l_artifact_records_the_rational_cubic_jet_bridge() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007l_cubic_jet_bridge.json"
    runner_path = artifact_path.parents[1] / "q007l_cubic_jet_bridge.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007l_cubic_jet_bridge.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational graph-gauge cubic-jet bridge",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "unordered_triple_count": 2600,
        "complex_unknown_count": 26532,
        "claim": (
            "degree-three Taylor-jet identification only; no quartic, "
            "explicit-radius, finite-ball, grid-uniform, or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["quadratic_jet_reconstruction"][
        "q007j_proof_digest_mismatch_count"
    ] == 0
    assert cycle["quadratic_jet_reconstruction"][
        "q007k_proof_digest_mismatch_count"
    ] == 0
    assert cycle["enumeration"]["triple_count"] == 2600
    assert cycle["enumeration"]["complex_unknown_count"] == 26532
    assert cycle["krawczyk_certification"]["included_count"] == 2600
    assert cycle["krawczyk_certification"][
        "zero_wave_structural_fixed_leaf_count"
    ] == 108
    assert cycle["krawczyk_certification"][
        "internal_graph_gauge_inclusion_count"
    ] == 1044
    assert "does not certify quartic" in cycle["claim_boundary"]


def test_q007m_artifact_records_the_rational_quartic_jet_bridge() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007m_quartic_jet_bridge.json"
    runner_path = artifact_path.parents[1] / "q007m_quartic_jet_bridge.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007m_quartic_jet_bridge.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational graph-gauge quartic-jet bridge",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "unordered_quartet_count": 17550,
        "complex_unknown_count": 171558,
        "claim": (
            "degree-four Taylor-jet identification only; no explicit-radius, "
            "finite-ball, grid-uniform, or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["lower_jet_reconstruction"][
        "q007j_proof_digest_mismatch_count"
    ] == 0
    assert cycle["lower_jet_reconstruction"][
        "q007k_proof_digest_mismatch_count"
    ] == 0
    assert cycle["lower_jet_reconstruction"][
        "q007l_proof_digest_mismatch_count"
    ] == 0
    assert cycle["enumeration"]["quartet_count"] == 17550
    assert cycle["enumeration"]["complex_unknown_count"] == 171558
    assert cycle["krawczyk_certification"]["included_count"] == 17550
    assert cycle["krawczyk_certification"][
        "zero_wave_structural_fixed_leaf_count"
    ] == 846
    assert cycle["krawczyk_certification"][
        "internal_graph_gauge_inclusion_count"
    ] == 4536
    assert "does not change Q007c1" in cycle["claim_boundary"]


def test_q007n_artifact_records_the_explicit_local_radius() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007n_explicit_local_radius.json"
    runner_path = artifact_path.parents[1] / "q007n_explicit_local_radius.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007n_explicit_local_radius.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational quartic-centered explicit local radius",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "selected_complexified_dimension": 24,
        "claim": (
            "explicit analytic existence radius only; no finite-ball "
            "normal-attraction, forward-invariance, positivity, grid-uniform, "
            "or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["radius_search"]["candidate_count"] == 119
    assert cycle["radius_search"]["passing_candidate_count"] == 46
    assert cycle["radius_search"]["selected_candidate"][
        "candidate_exponent"
    ] == 75
    assert cycle["theorem_consequence"][
        "explicit_modal_l1_radius_certified"
    ]
    assert "deliberately coarse" in cycle["claim_boundary"]


def test_q007o_artifact_records_the_external_complement_refinement() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007o_external_complement_radius.json"
    runner_path = (
        artifact_path.parents[1]
        / "q007o_external_complement_radius.py"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007o_external_complement_radius.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "rational exact-external-complement explicit-radius refinement"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "selected_complex_dimension": 24,
        "claim": (
            "sharper explicit analytic existence radius only; no finite-ball "
            "normal-attraction, forward-invariance, positivity, grid-uniform, "
            "or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    search = cycle["radius_comparison"]["refined_radius_search"]
    assert search["candidate_count"] == 119
    assert search["passing_candidate_count"] == 103
    assert search["selected_candidate"]["candidate_exponent"] == 18
    assert cycle["theorem_consequence"][
        "refined_explicit_modal_l1_radius_certified"
    ]
    assert "individual external eigenvectors" in cycle["claim_boundary"]


def test_q007p_artifact_records_the_finite_tube_attraction() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007p_finite_tube_attraction.json"
    runner_path = artifact_path.parents[1] / "q007p_finite_tube_attraction.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007p_finite_tube_attraction.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational finite-tube normal-attraction certificate",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "selected_real_dimension": 24,
        "external_complex_dimension": 2574,
        "base_modal_l1_radius": 1e-19,
        "normal_coordinate_radius": 1e-20,
        "claim": (
            "registered finite-tube forward invariance and normal "
            "attraction in one fixed external-coordinate norm only; no "
            "Euclidean, positivity, larger-tube, basin, grid-uniform, or "
            "continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["external_coordinate_certification"][
        "represented_wave_count"
    ] == 289
    assert cycle["external_coordinate_certification"][
        "external_complex_dimension"
    ] == 2574
    assert cycle["theorem_consequence"]["registered_tube_forward_invariant"]
    assert "not a Euclidean contraction result" in cycle["claim_boundary"]


def test_q007q_artifact_records_full_map_population_positivity() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007q_population_positivity.json"
    runner_path = artifact_path.parents[1] / "q007q_population_positivity.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007q_population_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational population-positivity certificate",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "base_modal_l1_radius": 1e-19,
        "normal_coordinate_radius": 1e-20,
        "sampling_times": "full one-step map input/output only",
        "claim": (
            "strict D2Q9 population and density positivity on the fixed "
            "Q007p tube only; no stagewise, entropy, larger-domain, "
            "grid-uniform, or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["theorem_consequence"] == {
        "registered_tube_population_strictly_positive": True,
        "registered_tube_density_strictly_positive": True,
        "all_full_map_iterates_population_strictly_positive": True,
    }
    assert "input/output times" in cycle["claim_boundary"]
    assert "does not certify positivity after collision" in cycle[
        "claim_boundary"
    ]


def test_q007r_artifact_records_exact_stagewise_population_positivity() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007r_stagewise_positivity.json"
    runner_path = artifact_path.parents[1] / "q007r_stagewise_positivity.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007r_stagewise_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational exact stagewise-positivity certificate",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "base_modal_l1_radius": 1e-19,
        "normal_coordinate_radius": 1e-20,
        "stages": [
            "equilibrium evaluation",
            "BGK collision output",
            "periodic streaming output",
            "five-point filter output",
        ],
        "arithmetic_scope": (
            "exact mathematical map; no IEEE-754 intermediate roundoff enclosure"
        ),
        "claim": (
            "strict D2Q9 population positivity at every exact internal "
            "one-step stage on the fixed Q007p tube only"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert all(cycle["theorem_consequence"].values())
    assert cycle["stage_structure_audit"]["passed"]
    assert "IEEE-754" in cycle["claim_boundary"]


def test_q007s_artifact_records_the_finite_grid_tube_enlargement() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007s_finite_tube_enlargement.json"
    runner_path = artifact_path.parents[1] / "q007s_finite_tube_enlargement.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007s_finite_tube_enlargement.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational finite-tube enlargement certificate",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold": "Q007o exact graph-gauge manifold",
        "norm": "Q007p Fourier external-coordinate block-sum l1",
        "candidate_grid": "9 base radii by 99 normal radii",
        "selection": "lexicographically maximize base then normal radius",
        "claim": (
            "forward invariance, one-step normal contraction, and strict "
            "normal domination for one selected registered tube only"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["selection"]["passing_candidate_count"] == 676
    assert cycle["selection"]["selection_boundary_reproduced"]
    assert all(cycle["theorem_consequence"].values())
    assert "Q007q/Q007r positivity remains sealed" in cycle["claim_boundary"]


def test_q007t_artifact_records_larger_tube_population_positivity() -> None:
    artifact_path = (
        ARTIFACT_DIRECTORY
        / "q007t_larger_tube_population_positivity.json"
    )
    runner_path = (
        artifact_path.parents[1]
        / "q007t_larger_tube_population_positivity.py"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007t_larger_tube_population_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "rational larger-tube population-positivity certificate"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "base_modal_l1_radius": 9e-19,
        "normal_coordinate_radius": 5e-12,
        "sampling_times": "full one-step map input/output only",
        "claim": (
            "strict D2Q9 population and density positivity on the fixed "
            "Q007s selected tube only; no stagewise, entropy, continuous-"
            "optimum, grid-uniform, or continuum claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert all(cycle["theorem_consequence"].values())
    assert cycle["q007s_tube_reuse"]["q007s_forward_invariance"]
    assert "Q007r stagewise positivity remains sealed" in cycle[
        "claim_boundary"
    ]


def test_q007u_artifact_records_larger_tube_stagewise_positivity() -> None:
    artifact_path = (
        ARTIFACT_DIRECTORY / "q007u_larger_tube_stagewise_positivity.json"
    )
    runner_path = (
        artifact_path.parents[1]
        / "q007u_larger_tube_stagewise_positivity.py"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007u_larger_tube_stagewise_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "rational larger-tube exact stagewise-positivity certificate"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "base_modal_l1_radius": 9e-19,
        "normal_coordinate_radius": 5e-12,
        "stages": [
            "equilibrium evaluation",
            "BGK collision output",
            "periodic streaming output",
            "five-point filter output",
        ],
        "arithmetic_scope": (
            "exact mathematical map; no IEEE-754 intermediate roundoff "
            "enclosure"
        ),
        "claim": (
            "strict D2Q9 population positivity at every exact internal "
            "one-step stage on the fixed Q007s selected tube only"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert len(cycle["validity_gates"]) == 6
    assert len(cycle["hypothesis_gates"]) == 5
    assert len(cycle["theorem_consequence"]) == 5
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert all(cycle["theorem_consequence"].values())
    assert cycle["q007s_tube_reuse"]["q007s_forward_invariance"]
    assert "IEEE-754" in cycle["claim_boundary"]


def test_q007v_artifact_records_binary64_partial_certificate() -> None:
    artifact_path = (
        ARTIFACT_DIRECTORY / "q007v_binary64_stage_enclosure.json"
    )
    runner_path = (
        artifact_path.parents[1] / "q007v_binary64_stage_enclosure.py"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007v_binary64_stage_enclosure.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "not_certified"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "rational binary64 stage-roundoff enclosure and tube-reentry audit"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "base_modal_l1_radius": 9e-19,
        "normal_coordinate_radius": 5e-12,
        "input_encoding": (
            "correctly rounded binary64 encoding of an exact real Q007s tube state"
        ),
        "rounding_model": (
            "IEEE-754 binary64 round-to-nearest ties-to-even with u=2^-53 "
            "and absolute subnormal fallback h=2^-1075"
        ),
        "claim": (
            "separate one-step internal-stage positivity and robust-tube "
            "re-entry decisions for the registered implementation only"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["one_step_outcome"] == "accepted"
    assert cycle["robust_reentry_outcome"] == "not_certified"
    assert cycle["hypothesis_outcome"] == "not_certified"
    assert len(cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 6
    assert sum(
        not gate["passed"] for gate in cycle["hypothesis_gates"].values()
    ) == 1
    assert not cycle["roundoff_reentry_audit"]["passed"]
    assert cycle["theorem_consequence"][
        "one_step_binary64_stagewise_population_strictly_positive"
    ]
    assert not cycle["theorem_consequence"][
        "all_iterate_roundoff_robust_q007s_tube_invariance"
    ]


def test_q007w_artifact_records_the_ideal_precision_threshold() -> None:
    artifact_path = (
        ARTIFACT_DIRECTORY / "q007w_ideal_precision_threshold.json"
    )
    runner_path = (
        artifact_path.parents[1] / "q007w_ideal_precision_threshold.py"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007w_ideal_precision_threshold.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": "rational ideal-binary precision-threshold certificate",
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": "fixed global mass and momentum leaf",
        "precision_candidates": "all integer significand bits 53 through 128",
        "minimum_normal_exponent": -1022,
        "rounding_model": "ideal binary round-to-nearest ties-to-even",
        "claim": (
            "minimum sufficient registered precision for the unchanged "
            "Q007v worst-case re-entry enclosure; no implemented backend"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert len(cycle["validity_gates"]) == 7
    assert len(cycle["hypothesis_gates"]) == 6
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert all(cycle["theorem_consequence"].values())
    assert cycle["selection"]["selected_precision_bits"] == 85
    assert cycle["selection"]["selection_boundary_reproduced"]


def test_q007x_artifact_records_the_mpfr_fixed_leaf_boundary() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007x_mpfr_fixed_leaf.json"
    runner_path = artifact_path.parents[1] / "q007x_mpfr_fixed_leaf.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007x_mpfr_fixed_leaf.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "not_certified"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "concrete MPFR-85 operation bridge and fixed-leaf closure audit"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": (
            "exact global mass and momentum equality on the fixed leaf"
        ),
        "input_encoding": (
            "Fraction to exact mpq to 85-bit MPFR componentwise rounding"
        ),
        "rounding_model": (
            "gmpy2 2.3.1 with MPFR 4.2.2 round-to-nearest ties-to-even"
        ),
        "claim": (
            "separate operation-semantic, one-step-bound, and exact "
            "fixed-leaf closure decisions for the registered backend"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "not_certified"
    assert len(cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 6
    assert sum(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    ) == 2
    assert cycle["backend_campaign"]["summary"][
        "all_streaming_conserves"
    ]
    assert not cycle["backend_campaign"]["summary"][
        "all_encodings_conserve"
    ]
    assert not cycle["backend_campaign"]["summary"][
        "all_filters_conserve"
    ]


def test_q007y_artifact_records_the_distributed_repair_boundary() -> None:
    artifact_path = (
        ARTIFACT_DIRECTORY / "q007y_distributed_conservation_repair.json"
    )
    runner_path = (
        artifact_path.parents[1]
        / "q007y_distributed_conservation_repair.py"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007y_distributed_conservation_repair.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "not_certified"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "distributed dyadic fixed-leaf repair and repair-aware "
            "Wiener-budget audit"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": (
            "fixed global mass and momentum leaf with exact diagonal "
            "post-stage repair"
        ),
        "repair_lattice": "four diagonal populations on h=2^-90",
        "rounding_model": (
            "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
        ),
        "claim": (
            "separate finite exact repair feasibility from the unchanged "
            "Q007w tube-wide base and normal margin decisions"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "not_certified"
    assert len(cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 7
    assert sum(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    ) == 5
    assert cycle["finite_campaign"]["passed"]
    assert cycle["tube_wide_repair_bound"]["normal_reentry_passed"]
    assert not cycle["tube_wide_repair_bound"]["base_reentry_passed"]
    assert cycle["theorem_consequence"][
        "registered_finite_output_repairs_restore_exact_fixed_leaf"
    ]
    assert not cycle["theorem_consequence"][
        "all_iterate_repaired_mpfr85_q007s_tube_invariance"
    ]


def test_q007z_artifact_records_the_selected_wave_certificate() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q007z_selected_wave_repair.json"
    runner_path = artifact_path.parents[1] / "q007z_selected_wave_repair.py"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007z_selected_wave_repair.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["mathematical_scope"] == {
        "diagnostic": (
            "selected-wave Fourier certificate for the sealed balanced "
            "dyadic conservation repair"
        ),
        "construction_grid": [17, 17],
        "omega": 1.5,
        "eta": 0.01,
        "conservation_treatment": (
            "fixed global mass and momentum leaf with exact diagonal "
            "post-stage repair"
        ),
        "selected_wave_count": 8,
        "repair_distribution": (
            "sealed row-major balanced quotient-plus-prefix remainder"
        ),
        "claim": (
            "conditional all-iterate Q007s tube re-entry and stage "
            "positivity for already repaired MPFR-85 states"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert len(cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 7
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["phase_histogram_audit"][
        "phase_histogram_case_count"
    ] == 2312
    assert cycle["selected_repair_bound"]["base_reentry_passed"]
    assert cycle["selected_repair_bound"]["normal_reentry_passed"]
    assert all(cycle["theorem_consequence"].values())
