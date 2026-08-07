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
