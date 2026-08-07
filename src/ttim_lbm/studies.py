"""Follow-on research studies for branch tracking and manufactured oracles."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

import numpy as np

from .checkerboard_filter import run_checkerboard_filter_audit
from .coefficient_scaling import run_coefficient_scaling_audit
from .d2q9 import (
    bgk_periodic_step,
    fourier_symbol,
    global_conserved_quantities,
    quarter_turn_population_matrix,
    spectrum_audit,
)
from .manifold import (
    log_log_slope,
    second_derivative_tensor,
    solve_general_quadratic_parameterization,
)
from .manufactured import (
    make_manufactured_quadratic_map,
    real_basis_from_dominant_complex_pair,
)
from .mode_closure import run_mode_added_closure_audit
from .nonresonance import (
    NULL_FORCING_TOLERANCE,
    PRACTICAL_CONDITION_CEILING,
    orthogonal_acoustic_resonance_witness,
    radial_band_normal_dominance,
    stripe_quadratic_audit,
    wave_vector_from_index,
)
from .normal_refinement import run_normal_gap_refinement_audit
from .provenance import runtime_metadata, source_metadata
from .spectra import (
    TrackedHydrodynamicCluster,
    maximum_principal_angle,
    path_reversal_subspace_error,
    track_hydrodynamic_cluster_path,
)
from .stripe import StripeQuadraticModel, build_stripe_quadratic_model


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _failed_validity_gates(
    point: TrackedHydrodynamicCluster,
    thresholds: dict[str, float],
) -> list[str]:
    failures = []
    if point.equilibrium_subspace_alignment < thresholds["minimum_equilibrium_alignment"]:
        failures.append("equilibrium_subspace_alignment")
    if point.external_spectral_separation < thresholds["minimum_external_eigenvalue_gap"]:
        failures.append("external_eigenvalue_gap")
    if point.schur_separation < thresholds["minimum_schur_separation"]:
        failures.append("schur_separation")
    if point.maximum_principal_angle_from_previous > thresholds["maximum_step_angle"]:
        failures.append("step_principal_angle")
    if point.spectral_projector_norm > thresholds["maximum_spectral_projector_norm"]:
        failures.append("spectral_projector_norm")
    if (
        point.spectral_projector_idempotency_residual
        > thresholds["maximum_spectral_projector_residual"]
        or point.spectral_projector_commutator_residual
        > thresholds["maximum_spectral_projector_residual"]
    ):
        failures.append("spectral_projector_residual")
    if point.schur_invariance_residual > thresholds["maximum_schur_invariance_residual"]:
        failures.append("schur_invariance_residual")
    return failures


def _valid_prefix(
    points: list[TrackedHydrodynamicCluster],
    thresholds: dict[str, float],
) -> tuple[list[TrackedHydrodynamicCluster], list[str]]:
    for index, point in enumerate(points):
        failures = _failed_validity_gates(point, thresholds)
        if failures:
            if index == 0:
                raise RuntimeError("the first low-wave-number cluster fails its validity gates")
            return points[:index], failures
    return points, []


def _accepted_path_record(
    points: list[TrackedHydrodynamicCluster],
    failures: list[str],
    backward_error: float,
    rotation_error: float,
    next_wave_number: float | None,
) -> dict[str, Any]:
    cutoff = points[-1]
    magnitudes = [float(np.hypot(*point.wave_vector)) for point in points]
    return {
        "validated_k_c": magnitudes[-1],
        "validated_k_c_semantics": "last passing sampled wave number; a lower bound",
        "cutoff_transition_bracket": {
            "last_passing_wave_number": magnitudes[-1],
            "first_failing_wave_number": next_wave_number,
        },
        "accepted_point_count": len(points),
        "next_rejected_wave_number": next_wave_number,
        "first_rejected_gates": failures,
        "path_reversal_maximum_principal_angle": backward_error,
        "quarter_turn_maximum_principal_angle": rotation_error,
        "minimum_external_eigenvalue_gap": min(
            point.external_spectral_separation for point in points
        ),
        "minimum_schur_separation": min(point.schur_separation for point in points),
        "minimum_equilibrium_subspace_alignment": min(
            point.equilibrium_subspace_alignment for point in points
        ),
        "maximum_spectral_projector_norm": max(
            point.spectral_projector_norm for point in points
        ),
        "maximum_spectral_projector_idempotency_residual": max(
            point.spectral_projector_idempotency_residual for point in points
        ),
        "maximum_spectral_projector_commutator_residual": max(
            point.spectral_projector_commutator_residual for point in points
        ),
        "maximum_eigenvector_condition_number": max(
            point.eigenvector_condition_number for point in points
        ),
        "maximum_schur_invariance_residual": max(
            point.schur_invariance_residual for point in points
        ),
        "simple_branch_point_count": sum(
            point.classification == "simple_branches" for point in points
        ),
        "invariant_cluster_point_count": sum(
            point.classification == "invariant_cluster" for point in points
        ),
        "cutoff_cluster_eigenvalues": [
            _complex_record(complex(value)) for value in cutoff.eigenvalues
        ],
    }


def _nyquist_record(omega: float) -> dict[str, Any]:
    direct = {}
    for label, wave_vector in {
        "pi_0": (np.pi, 0.0),
        "0_pi": (0.0, np.pi),
    }.items():
        eigenvalues = np.linalg.eigvals(fourier_symbol(*wave_vector, omega))
        matches = [value for value in eigenvalues if abs(value + 1.0) < 1.0e-10]
        direct[label] = {
            "minus_one_count": len(matches),
            "minimum_distance_to_minus_one": float(np.min(np.abs(eigenvalues + 1.0))),
        }
    return direct


def _individual_label_reversal_error(
    forward: list[TrackedHydrodynamicCluster],
    backward: list[TrackedHydrodynamicCluster],
) -> tuple[float | None, str | None]:
    paired = list(zip(forward, reversed(backward), strict=True))
    if any(
        left.classification != "simple_branches"
        or right.classification != "simple_branches"
        for left, right in paired
    ):
        return None, "individual labels are undefined at an eigenvalue collision"
    labels = ("shear", "acoustic_positive", "acoustic_negative")
    error = max(
        abs(left.branch_eigenvalues[label] - right.branch_eigenvalues[label])
        for left, right in paired
        for label in labels
    )
    return float(error), None


def run_q004b_branch_tracking_study() -> dict[str, Any]:
    """Determine a validated low-wave-number prefix for the D2Q9 cluster."""

    thresholds = {
        "minimum_equilibrium_alignment": 0.75,
        "minimum_external_eigenvalue_gap": 0.05,
        "minimum_schur_separation": 0.02,
        "maximum_step_angle": 0.20,
        "maximum_spectral_projector_norm": 100.0,
        "maximum_spectral_projector_residual": 1.0e-12,
        "maximum_schur_invariance_residual": 1.0e-12,
        "maximum_reversal_angle": 1.0e-6,
        "maximum_rotation_angle": 1.0e-6,
    }
    omegas = [1.0, 1.2, 1.5, 1.8]
    angles = [0.0, float(np.pi / 8.0), float(np.pi / 4.0)]
    magnitudes = np.linspace(1.0e-3, 1.8, 145)
    population_rotation = quarter_turn_population_matrix().astype(np.complex128)
    path_records = []
    for omega in omegas:
        for angle in angles:
            wave_vectors = [
                (
                    float(magnitude * np.cos(angle)),
                    float(magnitude * np.sin(angle)),
                )
                for magnitude in magnitudes
            ]
            forward = track_hydrodynamic_cluster_path(wave_vectors, omega)
            accepted, failures = _valid_prefix(forward, thresholds)
            accepted_wave_vectors = wave_vectors[: len(accepted)]
            backward = track_hydrodynamic_cluster_path(
                list(reversed(accepted_wave_vectors)),
                omega,
                initial_reference_basis=accepted[-1].right_basis,
            )
            backward_error = path_reversal_subspace_error(accepted, backward)
            rotated_wave_vectors = [
                (-wave_vector[1], wave_vector[0])
                for wave_vector in accepted_wave_vectors
            ]
            rotated = track_hydrodynamic_cluster_path(
                rotated_wave_vectors,
                omega,
                initial_reference_basis=population_rotation @ accepted[0].right_basis,
            )
            rotation_error = float(
                max(
                    maximum_principal_angle(
                        population_rotation @ original.right_basis,
                        rotated_point.right_basis,
                    )
                    for original, rotated_point in zip(accepted, rotated, strict=True)
                )
            )
            next_wave_number = (
                float(magnitudes[len(accepted)])
                if len(accepted) < len(magnitudes)
                else None
            )
            path_records.append(
                {
                    "omega": omega,
                    "angle_radians": angle,
                    **_accepted_path_record(
                        accepted,
                        failures,
                        backward_error,
                        rotation_error,
                        next_wave_number,
                    ),
                }
            )

    all_zone_wave_vectors = [
        (float(magnitude), 0.0)
        for magnitude in np.linspace(1.0e-3, np.pi, 129)
    ]
    original_global_claim: dict[str, Any]
    try:
        all_zone_forward = track_hydrodynamic_cluster_path(
            all_zone_wave_vectors,
            1.5,
        )
        all_zone_backward = track_hydrodynamic_cluster_path(
            list(reversed(all_zone_wave_vectors)),
            1.5,
            initial_reference_basis=all_zone_forward[-1].right_basis,
        )
        all_zone_error = path_reversal_subspace_error(
            all_zone_forward,
            all_zone_backward,
        )
        label_error, label_failure = _individual_label_reversal_error(
            all_zone_forward,
            all_zone_backward,
        )
        original_global_claim = {
            "outcome": (
                "rejected"
                if label_failure is not None
                or label_error is None
                or label_error > 1.0e-6
                else "not_rejected"
            ),
            "individual_label_reversal_error": label_error,
            "cluster_subspace_reversal_angle": all_zone_error,
            "failure": label_failure,
        }
    except np.linalg.LinAlgError as error:
        if "ordered Schur decomposition did not preserve" not in str(error):
            raise
        original_global_claim = {
            "outcome": "rejected",
            "individual_label_reversal_error": None,
            "cluster_subspace_reversal_angle": None,
            "failure": str(error),
        }

    grid_audits = {
        str(size): spectrum_audit(size, 1.2)
        for size in (16, 17, 32, 33)
    }
    nyquist = _nyquist_record(1.2)
    minimum_k_c = min(record["validated_k_c"] for record in path_records)
    maximum_reversal = max(
        record["path_reversal_maximum_principal_angle"]
        for record in path_records
    )
    maximum_rotation = max(
        record["quarter_turn_maximum_principal_angle"]
        for record in path_records
    )
    gates = {
        "all_paths_have_nontrivial_valid_prefix": {
            "value": minimum_k_c,
            "threshold": 0.5,
            "passed": minimum_k_c >= 0.5,
        },
        "path_reversal_cluster_consistency": {
            "value": maximum_reversal,
            "threshold": thresholds["maximum_reversal_angle"],
            "passed": maximum_reversal < thresholds["maximum_reversal_angle"],
        },
        "quarter_turn_cluster_consistency": {
            "value": maximum_rotation,
            "threshold": thresholds["maximum_rotation_angle"],
            "passed": maximum_rotation < thresholds["maximum_rotation_angle"],
        },
        "odd_construction_grids_have_only_three_unit_modes": {
            "value": [grid_audits["17"]["strict_unit_count"], grid_audits["33"]["strict_unit_count"]],
            "threshold": [3, 3],
            "passed": all(grid_audits[str(size)]["strict_unit_count"] == 3 for size in (17, 33)),
        },
        "even_regression_grids_expose_five_unit_modes": {
            "value": [grid_audits["16"]["strict_unit_count"], grid_audits["32"]["strict_unit_count"]],
            "threshold": [5, 5],
            "passed": all(grid_audits[str(size)]["strict_unit_count"] == 5 for size in (16, 32)),
        },
        "direct_nyquist_symbols_contain_minus_one": {
            "value": [nyquist["pi_0"]["minus_one_count"], nyquist["0_pi"]["minus_one_count"]],
            "threshold": [1, 1],
            "passed": all(record["minus_one_count"] == 1 for record in nyquist.values()),
        },
    }
    accepted = all(gate["passed"] for gate in gates.values())
    return {
        "question": (
            "What is the largest low-wave-number prefix on which the D2Q9 "
            "hydrodynamic invariant cluster remains physically identifiable "
            "and separated from the kinetic complement?"
        ),
        "superseded_question": (
            "Can individual shear/acoustic/kinetic labels be made unique over "
            "the entire Brillouin zone?"
        ),
        "superseded_question_outcome": original_global_claim,
        "hypothesis": (
            "A three-dimensional ordered-Schur cluster has a nontrivial, "
            "path- and quarter-turn-consistent validated prefix for every "
            "registered omega and direction."
        ),
        "construction_scope": {
            "odd_periodic_grid_sizes": [17, 33],
            "continuous_path_sample_count": int(magnitudes.size),
            "continuous_path_maximum_wave_number": float(magnitudes[-1]),
            "omega_values": omegas,
            "path_angles_radians": angles,
            "even_grid_sizes_are_diagnostic_only": [16, 32],
            "parity_and_direct_nyquist_audit_omega": 1.2,
        },
        "validity_thresholds": thresholds,
        "paths": path_records,
        "grid_parity_audits": grid_audits,
        "direct_nyquist_audit": nyquist,
        "gates": gates,
        "outcome": "accepted" if accepted else "rejected",
        "analysis": (
            "The full-zone individual-label requirement is too strong. The "
            "accepted object is a low-k invariant cluster; individual labels "
            "are diagnostic only at simple eigenvalues. Each reported k_c is "
            "the last passing sampled wave number and therefore a lower bound; "
            "the adjacent transition bracket, not an exact maximum, is recorded. "
            "It is a threshold-dependent empirical boundary, not an existence theorem."
        ),
        "known_limitations": [
            (
                "The current cluster candidate is seeded from a diagonalizable "
                "eigendecomposition before ordered-Schur reordering. A defective "
                "or non-semisimple collision requires Schur-native continuation."
            ),
            (
                "The simple-label condition uses the full eigenvector-matrix "
                "condition number and is therefore conservative when only an "
                "excluded kinetic cluster is ill-conditioned."
            ),
        ],
        "next_change": (
            "Use each accepted k_c as input to the sector-aware quadratic "
            "nonresonance and nonnormality audit in Q005."
        ),
    }


def run_manufactured_quadratic_study() -> dict[str, Any]:
    """Validate the general real-block quadratic solver before nonzero-mode LBM."""

    model = make_manufactured_quadratic_map()
    hessian, reduced_hessian, diagnostics = solve_general_quadratic_parameterization(
        model.jacobian,
        model.tangent,
        model.extractor,
        model.reduced_linear,
        model.second_derivative,
    )
    hessian_error = float(
        np.linalg.norm(hessian - model.chart_hessian)
        / np.linalg.norm(model.chart_hessian)
    )
    reduced_error = float(
        np.linalg.norm(reduced_hessian - model.reduced_hessian)
        / np.linalg.norm(model.reduced_hessian)
    )
    real_pair = real_basis_from_dominant_complex_pair(model.jacobian)
    coordinates = [
        np.array([0.10, 0.05]),
        np.array([-0.08, 0.03]),
        np.array([0.02, -0.11]),
    ]
    invariance_residual = max(
        float(
            np.linalg.norm(
                model.full_map(model.chart.evaluate(coordinate))
                - model.chart.evaluate(model.reduced_map(coordinate))
            )
        )
        for coordinate in coordinates
    )
    multipliers = [0.25, 0.60, 0.66, 0.671, 0.6723]
    near_resonance_sweep = []
    for multiplier in multipliers:
        candidate = make_manufactured_quadratic_map(multiplier)
        candidate_hessian, _, candidate_diagnostics = (
            solve_general_quadratic_parameterization(
                candidate.jacobian,
                candidate.tangent,
                candidate.extractor,
                candidate.reduced_linear,
                candidate.second_derivative,
            )
        )
        near_resonance_sweep.append(
            {
                "mean_multiplier": multiplier,
                "distance_to_quadratic_resonance": abs(0.82**2 - multiplier),
                "condition_number": candidate_diagnostics.condition_number,
                "smallest_singular_value": candidate_diagnostics.smallest_singular_value,
                "chart_hessian_relative_error": float(
                    np.linalg.norm(candidate_hessian - candidate.chart_hessian)
                    / np.linalg.norm(candidate.chart_hessian)
                ),
            }
        )
    exact_resonance_rejected = False
    exact_resonance_rejection_message: str | None = None
    try:
        resonant = make_manufactured_quadratic_map(0.82**2)
        solve_general_quadratic_parameterization(
            resonant.jacobian,
            resonant.tangent,
            resonant.extractor,
            resonant.reduced_linear,
            resonant.second_derivative,
        )
    except np.linalg.LinAlgError as error:
        exact_resonance_rejection_message = str(error)
        exact_resonance_rejected = "rank deficient" in str(error)
    gates = {
        "known_chart_hessian_recovered": {
            "value": hessian_error,
            "threshold": 1.0e-12,
            "passed": hessian_error < 1.0e-12,
        },
        "nontrivial_reduced_hessian_recovered": {
            "value": reduced_error,
            "threshold": 1.0e-12,
            "passed": reduced_error < 1.0e-12,
        },
        "homological_equation_and_gauge": {
            "value": max(
                diagnostics.global_equation_relative_residual,
                diagnostics.maximum_gauge_residual,
                diagnostics.tangent_relative_residual,
                diagnostics.left_invariance_relative_residual,
                diagnostics.raw_symmetry_relative_residual,
            ),
            "threshold": 1.0e-12,
            "passed": max(
                diagnostics.global_equation_relative_residual,
                diagnostics.maximum_gauge_residual,
                diagnostics.tangent_relative_residual,
                diagnostics.left_invariance_relative_residual,
                diagnostics.raw_symmetry_relative_residual,
            )
            < 1.0e-12,
        },
        "manufactured_model_duality_and_graph_gauge": {
            "value": max(
                float(np.linalg.norm(model.extractor @ model.tangent - np.eye(2))),
                float(
                    np.linalg.norm(
                        model.extractor @ model.chart_hessian.reshape(5, -1)
                    )
                ),
            ),
            "threshold": 1.0e-12,
            "passed": max(
                float(np.linalg.norm(model.extractor @ model.tangent - np.eye(2))),
                float(
                    np.linalg.norm(
                        model.extractor @ model.chart_hessian.reshape(5, -1)
                    )
                ),
            )
            < 1.0e-12,
        },
        "real_complex_pair_conversion_and_normalization": {
            "value": max(
                real_pair.right_invariance_residual,
                real_pair.left_invariance_residual,
                real_pair.duality_residual,
                real_pair.conjugacy_error,
            ),
            "threshold": 1.0e-12,
            "passed": max(
                real_pair.right_invariance_residual,
                real_pair.left_invariance_residual,
                real_pair.duality_residual,
                real_pair.conjugacy_error,
            )
            < 1.0e-12,
        },
        "exact_manifold_invariance": {
            "value": invariance_residual,
            "threshold": 1.0e-13,
            "passed": invariance_residual < 1.0e-13,
        },
        "near_resonance_condition_growth": {
            "value": (
                near_resonance_sweep[-1]["condition_number"]
                / near_resonance_sweep[0]["condition_number"]
            ),
            "threshold": 1.0e3,
            "passed": (
                near_resonance_sweep[-1]["condition_number"]
                / near_resonance_sweep[0]["condition_number"]
            )
            > 1.0e3,
        },
        "exact_resonance_rejected": {
            "value": exact_resonance_rejected,
            "threshold": True,
            "passed": exact_resonance_rejected,
        },
    }
    accepted = all(gate["passed"] for gate in gates.values())
    return {
        "question": (
            "Can the general real-block quadratic homological solver recover a "
            "known nonidentity stable manifold and expose a controlled resonance?"
        ),
        "hypothesis": (
            "The solver recovers known H and nonzero G, preserves the real "
            "biorthogonal conjugate block under a nonorthogonal similarity "
            "transform, and its conditioning diverges near mu=rho^2."
        ),
        "model": {
            "full_dimension": 5,
            "reduced_dimension": 2,
            "sectors": ["master_complex_pair", "mean_complement", "second_harmonic_pair"],
            "reduced_linear_block": real_pair.block.tolist(),
            "mean_quadratic_resonance": 0.82**2,
            "state_transform_condition_number": float(
                np.linalg.cond(model.state_transform)
            ),
            "model_left_right_duality_residual": float(
                np.linalg.norm(model.extractor @ model.tangent - np.eye(2))
            ),
        },
        "chart_hessian_relative_error": hessian_error,
        "reduced_hessian_relative_error": reduced_error,
        "invariance_residual": invariance_residual,
        "real_block_conversion": {
            "right_invariance_residual": real_pair.right_invariance_residual,
            "left_invariance_residual": real_pair.left_invariance_residual,
            "duality_residual": real_pair.duality_residual,
            "conjugacy_error": real_pair.conjugacy_error,
        },
        "homological_diagnostics": asdict(diagnostics),
        "near_resonance_sweep": near_resonance_sweep,
        "exact_resonance_rejected": exact_resonance_rejected,
        "exact_resonance_rejection_message": exact_resonance_rejection_message,
        "gates": gates,
        "outcome": "accepted" if accepted else "rejected",
        "analysis": (
            "This separates homological-solver failures from LBM branch "
            "classification. It is an algebraic oracle, not evidence that the "
            "nonzero-wave D2Q9 candidate manifold exists."
        ),
        "next_change": (
            "Proceed to Q005 before constructing the fixed-conservation-leaf "
            "nonzero-mode D2Q9 quadratic chart."
        ),
    }


def run_q004b_and_manufactured_study() -> dict[str, Any]:
    """Run the revised Q004b and its required nontrivial algebraic oracle."""

    branch_tracking = run_q004b_branch_tracking_study()
    manufactured = run_manufactured_quadratic_study()
    passed = (
        branch_tracking["outcome"] == "accepted"
        and branch_tracking["superseded_question_outcome"]["outcome"] == "rejected"
        and manufactured["outcome"] == "accepted"
    )
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "construction_grid_parity": "odd periodic square grids only",
            "even_grids": "diagnostic parity and obstruction analysis only",
            "conservation_treatment": "fixed global mass and momentum leaf for future nonzero-mode charts",
            "manifold_claim": "candidate until Q005 nonresonance and normal-attraction gates pass",
        },
        "cycles": [branch_tracking, manufactured],
        "study_gate": "passed" if passed else "failed",
        "next_question": (
            "Q005: do the accepted k_c values retain quadratic sector-aware "
            "nonresonance and acceptable nonnormality under grid refinement?"
        ),
    }


def run_q005_nonresonance_study() -> dict[str, Any]:
    """Falsify or qualify the registered isotropic quadratic slow-set candidate."""

    cutoffs = {
        1.0: 0.763076388888889,
        1.2: 0.925486111111111,
        1.5: 1.1628541666666665,
        1.8: 1.375236111111111,
    }
    grid_sizes = (9, 17, 33, 65)
    campaign = []
    for size in grid_sizes:
        fundamental = 2.0 * np.pi / size
        for omega, cutoff in cutoffs.items():
            minimal_shell = orthogonal_acoustic_resonance_witness(
                size,
                omega,
            )
            boundary_index = max(1, int(np.floor(cutoff / fundamental + 1.0e-12)))
            boundary = orthogonal_acoustic_resonance_witness(
                size,
                omega,
                radial_index=boundary_index,
            )
            boundary_output = wave_vector_from_index(
                tuple(boundary["output_wave_index"]),
                size,
            )
            boundary["input_radial_index"] = boundary_index
            boundary["output_wave_magnitude"] = float(np.hypot(*boundary_output))
            boundary["output_is_external_to_registered_radial_band"] = bool(
                np.hypot(*boundary_output) > cutoff + 1.0e-12
            )
            campaign.append(
                {
                    "grid_size": size,
                    "omega": omega,
                    "registered_cutoff": cutoff,
                    "minimum_shell_resonance_witness": minimal_shell,
                    "registered_boundary_resonance_witness": boundary,
                    "radial_band_normal_dominance": radial_band_normal_dominance(
                        size,
                        omega,
                        cutoff,
                    ),
                    "stripe_finite_grid_audit": stripe_quadratic_audit(size, omega),
                }
            )

    minimal_homological = [
        record["minimum_shell_resonance_witness"]["homological"]
        for record in campaign
    ]
    external_boundary = [
        record["registered_boundary_resonance_witness"]
        for record in campaign
        if record["registered_boundary_resonance_witness"][
            "output_is_external_to_registered_radial_band"
        ]
    ]
    normal_records = [
        record["radial_band_normal_dominance"] for record in campaign
    ]
    stripe_records = [record["stripe_finite_grid_audit"] for record in campaign]
    maximum_null_forcing = max(
        record["null_forcing_ratio"] or 0.0
        for record in minimal_homological
        + [record["homological"] for record in external_boundary]
    )
    maximum_realification_error = max(
        record["complex_realification_singular_value_relative_error"]
        for record in stripe_records
    )
    maximum_conservation_residual = max(
        record["maximum_zero_wave_conservation_residual"]
        for record in stripe_records
    )
    maximum_kinetic_invariance_residual = max(
        record["fixed_leaf_kinetic_invariance_residual"]
        for record in stripe_records
    )
    maximum_stripe_condition = max(
        max(
            record["second_harmonic_maximum_condition_number"],
            record["zero_wave_maximum_condition_number"],
        )
        for record in stripe_records
    )
    minimum_schur_separation = min(
        record["minimum_ordered_schur_separation"] for record in normal_records
    )
    maximum_split_residual = max(
        max(
            record["maximum_master_projector_residual"],
            record["maximum_schur_invariance_residual"],
        )
        for record in normal_records
    )
    maximum_projector_norm = max(
        record["maximum_master_spectral_projector_norm"]
        for record in normal_records
    )
    candidate_falsification_flags = [
        (
            record["registered_boundary_resonance_witness"][
                "output_is_external_to_registered_radial_band"
            ]
            and record["registered_boundary_resonance_witness"]["homological"][
                "status"
            ]
            == "compatible_nonunique"
        )
        or not record["radial_band_normal_dominance"][
            "finite_grid_normal_attraction"
        ]
        for record in campaign
    ]
    gates = {
        "registered_radial_spectral_splits_are_resolved": {
            "value": {
                "minimum_schur_separation": minimum_schur_separation,
                "maximum_projector_norm": maximum_projector_norm,
                "maximum_invariance_or_projector_residual": maximum_split_residual,
            },
            "threshold": {
                "minimum_schur_separation": 0.02,
                "maximum_projector_norm": 100.0,
                "maximum_invariance_or_projector_residual": 1.0e-12,
            },
            "passed": minimum_schur_separation >= 0.02
            and maximum_projector_norm <= 100.0
            and maximum_split_residual <= 1.0e-12,
        },
        "every_registered_isotropic_candidate_is_falsified": {
            "value": sum(candidate_falsification_flags),
            "threshold": len(campaign),
            "passed": all(candidate_falsification_flags),
        },
        "minimum_nonempty_isotropic_shell_resonance_detected": {
            "value": sum(
                record["status"] == "compatible_nonunique"
                for record in minimal_homological
            ),
            "threshold": len(campaign),
            "passed": all(
                record["status"] == "compatible_nonunique"
                for record in minimal_homological
            ),
        },
        "registered_radial_boundary_external_resonance_detected": {
            "value": sum(
                record["homological"]["status"] == "compatible_nonunique"
                for record in external_boundary
            ),
            "threshold": len(external_boundary),
            "passed": bool(external_boundary)
            and all(
                record["homological"]["status"] == "compatible_nonunique"
                for record in external_boundary
            ),
        },
        "resonant_forcing_compatibility_resolved": {
            "value": maximum_null_forcing,
            "threshold": NULL_FORCING_TOLERANCE,
            "passed": maximum_null_forcing <= NULL_FORCING_TOLERANCE,
        },
        "registered_radial_normal_attraction_is_falsified": {
            "value": sum(
                not record["finite_grid_normal_attraction"]
                for record in normal_records
            ),
            "threshold": 1,
            "passed": any(
                not record["finite_grid_normal_attraction"]
                for record in normal_records
            ),
        },
        "stripe_complex_realification_consistency": {
            "value": maximum_realification_error,
            "threshold": 1.0e-10,
            "passed": maximum_realification_error <= 1.0e-10,
        },
        "stripe_fixed_leaf_conservation_and_invariance": {
            "value": max(
                maximum_conservation_residual,
                maximum_kinetic_invariance_residual,
            ),
            "threshold": 1.0e-12,
            "passed": max(
                maximum_conservation_residual,
                maximum_kinetic_invariance_residual,
            )
            <= 1.0e-12,
        },
        "stripe_finite_grid_practical_conditioning": {
            "value": maximum_stripe_condition,
            "threshold": PRACTICAL_CONDITION_CEILING,
            "passed": maximum_stripe_condition <= PRACTICAL_CONDITION_CEILING
            and all(
                record["all_sector_statuses"] == ["nonsingular_practical"]
                for record in stripe_records
            ),
        },
    }
    study_valid = all(gate["passed"] for gate in gates.values())
    reference_stripe = next(
        record
        for record in stripe_records
        if record["grid_size"] == 17 and record["omega"] == 1.2
    )
    stripe_refinement = {}
    for omega in cutoffs:
        omega_records = sorted(
            (
                record
                for record in stripe_records
                if record["omega"] == omega
            ),
            key=lambda record: record["grid_size"],
        )
        log_sizes = np.log(
            np.array(
                [record["grid_size"] for record in omega_records],
                dtype=np.float64,
            )
        )
        log_singular_values = np.log(
            np.array(
                [
                    record["second_harmonic_minimum_smallest_singular_value"]
                    for record in omega_records
                ],
                dtype=np.float64,
            )
        )
        log_condition_numbers = np.log(
            np.array(
                [
                    record["second_harmonic_maximum_condition_number"]
                    for record in omega_records
                ],
                dtype=np.float64,
            )
        )
        stripe_refinement[str(omega)] = {
            "log_smallest_singular_value_vs_log_N_slope": float(
                np.polyfit(log_sizes, log_singular_values, 1)[0]
            ),
            "log_condition_number_vs_log_N_slope": float(
                np.polyfit(log_sizes, log_condition_numbers, 1)[0]
            ),
        }
    return {
        "question": (
            "Do the Q004b radial low-wave-number candidates satisfy quadratic "
            "external nonresonance and finite-grid normal attraction?"
        ),
        "hypothesis": (
            "At least one registered radial candidate remains strictly "
            "quadratically nonresonant, normally attracting, and practically "
            "conditioned under the registered odd-grid refinement."
        ),
        "registered_scope": {
            "polynomial_degree": 2,
            "grid_sizes": list(grid_sizes),
            "omega_to_cutoff": {
                str(omega): cutoff for omega, cutoff in cutoffs.items()
            },
            "conservation_treatment": (
                "fixed global mass and momentum leaf; zero-wave output is "
                "restricted to the six-dimensional kinetic sector"
            ),
            "refinement_semantics": (
                "sampling-density/domain-size diagnostic, not fixed-domain "
                "continuum convergence"
            ),
        },
        "campaign": campaign,
        "summary": {
            "campaign_count": len(campaign),
            "minimum_shell_compatible_nonunique_count": sum(
                record["status"] == "compatible_nonunique"
                for record in minimal_homological
            ),
            "external_registered_boundary_witness_count": len(external_boundary),
            "radial_normal_attraction_failure_count": sum(
                not record["finite_grid_normal_attraction"]
                for record in normal_records
            ),
            "falsified_registered_isotropic_candidate_count": sum(
                candidate_falsification_flags
            ),
            "maximum_resonant_null_forcing_ratio": maximum_null_forcing,
            "maximum_stripe_condition_number": maximum_stripe_condition,
            "maximum_stripe_realification_error": maximum_realification_error,
            "stripe_refinement_slopes": stripe_refinement,
            "reference_stripe_N17_omega1p2": {
                "second_harmonic_smallest_singular_value": (
                    reference_stripe[
                        "second_harmonic_minimum_smallest_singular_value"
                    ]
                ),
                "second_harmonic_condition_number": (
                    reference_stripe["second_harmonic_maximum_condition_number"]
                ),
                "zero_wave_smallest_singular_value": (
                    reference_stripe["zero_wave_minimum_smallest_singular_value"]
                ),
            },
        },
        "gates": gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": "rejected" if study_valid else "unresolved",
        "decision": (
            "Reject the registered two-dimensional isotropic candidate as a "
            "standard nonresonant, normally attracting SSM. The detected "
            "rank-deficient sectors are forcing-compatible at quadratic order, "
            "so this does not prove that no resonant invariant chart exists; it "
            "does remove the standard uniqueness claim."
        ),
        "repair_comparison": {
            "cutoff_shrink": (
                "rejected: the minimum nonempty C4-complete shell already has "
                "the compatible external resonance"
            ),
            "mode_addition": (
                "a diagonal shear orbit internalizes the first witness, but "
                "requires a new additive-closure and conditioning audit before "
                "it can be accepted"
            ),
            "stripe_solver_oracle": (
                "accepted only as a finite-grid algebraic oracle on the "
                "nonlinearly invariant y-independent subspace"
            ),
        },
        "limitations": [
            (
                "The resonance identity is established to the registered "
                "floating-point rank threshold across the campaign; a symbolic "
                "or high-precision proof remains open."
            ),
            (
                "The full quadratic pair table was not enumerated after a "
                "decisive external witness falsified strict nonresonance."
            ),
            (
                "Pointwise simple-mode diagnostics are used for the witness. "
                "Future mode-added clusters require Schur-block operators."
            ),
            (
                "The stripe condition numbers grow under refinement, so no "
                "grid-uniform bound is claimed."
            ),
        ],
        "next_change": (
            "Use N=17, omega=1.2 and the y-independent first-shell conjugate "
            "pair for a fixed-leaf dense quadratic solver oracle before any "
            "full two-dimensional mode-added construction."
        ),
    }


def run_q005_study() -> dict[str, Any]:
    """Run the registered Q005 falsification campaign."""

    cycle = run_q005_nonresonance_study()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "construction_grid_parity": "odd periodic square grids only",
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold_claim": (
                "registered isotropic nonresonant SSM candidate rejected; "
                "stripe retained only as a finite-grid solver oracle"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "next_question": (
            "Q006s: does the N=17, omega=1.2 fixed-leaf stripe quadratic chart "
            "raise the invariance-residual order from two to three?"
        ),
    }


def _normalized_directions(seed: int, count: int, dimension: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, dimension))
    return directions / np.linalg.norm(directions, axis=1)[:, None]


def _stripe_residual_campaign(
    model: StripeQuadraticModel,
    directions: np.ndarray,
    amplitudes: np.ndarray,
) -> dict[str, Any]:
    records = []
    for direction in directions:
        linear_residuals = []
        quadratic_residuals = []
        minimum_population = np.inf
        for amplitude in amplitudes:
            coordinates = amplitude * direction
            linear_residuals.append(
                float(
                    np.linalg.norm(
                        model.invariance_defect(coordinates, quadratic=False)
                    )
                )
            )
            quadratic_residuals.append(
                float(
                    np.linalg.norm(
                        model.invariance_defect(coordinates, quadratic=True)
                    )
                )
            )
            lifted = model.chart.evaluate(coordinates)
            minimum_population = min(
                minimum_population,
                float(np.min(lifted)),
                float(np.min(model.full_map(lifted))),
            )
        records.append(
            {
                "direction": direction.tolist(),
                "linear_residuals": linear_residuals,
                "quadratic_residuals": quadratic_residuals,
                "linear_slope": log_log_slope(amplitudes, linear_residuals),
                "quadratic_slope": log_log_slope(
                    amplitudes,
                    quadratic_residuals,
                ),
                "maximum_amplitude_residual_ratio": (
                    quadratic_residuals[-1] / linear_residuals[-1]
                ),
                "minimum_population": minimum_population,
            }
        )
    linear_slopes = [record["linear_slope"] for record in records]
    quadratic_slopes = [record["quadratic_slope"] for record in records]
    maximum_amplitude_linear = [
        record["linear_residuals"][-1] for record in records
    ]
    maximum_amplitude_quadratic = [
        record["quadratic_residuals"][-1] for record in records
    ]
    return {
        "amplitudes": amplitudes.tolist(),
        "direction_records": records,
        "summary": {
            "minimum_linear_slope": min(linear_slopes),
            "maximum_linear_slope": max(linear_slopes),
            "minimum_quadratic_slope": min(quadratic_slopes),
            "maximum_quadratic_slope": max(quadratic_slopes),
            "maximum_directional_residual_ratio": max(
                record["maximum_amplitude_residual_ratio"] for record in records
            ),
            "maximum_residual_ratio": (
                max(maximum_amplitude_quadratic) / max(maximum_amplitude_linear)
            ),
            "minimum_population": min(
                record["minimum_population"] for record in records
            ),
        },
    }


def _stripe_shadow_campaign(
    model: StripeQuadraticModel,
    directions: np.ndarray,
    amplitude: float,
    steps: int,
    *,
    quadratic: bool,
) -> dict[str, Any]:
    chart = model.chart if quadratic else model.linear_chart
    records = []
    for direction in directions:
        coordinates = amplitude * direction
        state = chart.evaluate(coordinates)
        initial_conserved = global_conserved_quantities(
            state.reshape(1, model.size, 9)
        )
        maximum_absolute_error = 0.0
        maximum_relative_error = 0.0
        maximum_coordinate_drift = 0.0
        maximum_conservation_drift = 0.0
        minimum_population = np.inf
        maximum_absolute_error_step = 0
        maximum_relative_error_step = 0
        final_absolute_error = 0.0
        final_relative_error = 0.0
        for step in range(steps + 1):
            predicted = chart.evaluate(coordinates)
            absolute_error = float(np.linalg.norm(state - predicted))
            perturbation_scale = max(
                float(np.linalg.norm(state - chart.base)),
                float(np.linalg.norm(predicted - chart.base)),
                np.finfo(float).eps,
            )
            relative_error = absolute_error / perturbation_scale
            coordinate_drift = float(
                np.linalg.norm(
                    model.extractor @ (state - chart.base) - coordinates
                )
            )
            conservation_drift = float(
                np.linalg.norm(
                    global_conserved_quantities(
                        state.reshape(1, model.size, 9)
                    )
                    - initial_conserved
                )
            )
            if absolute_error > maximum_absolute_error:
                maximum_absolute_error = absolute_error
                maximum_absolute_error_step = step
            if relative_error > maximum_relative_error:
                maximum_relative_error = relative_error
                maximum_relative_error_step = step
            maximum_coordinate_drift = max(
                maximum_coordinate_drift,
                coordinate_drift,
            )
            maximum_conservation_drift = max(
                maximum_conservation_drift,
                conservation_drift,
            )
            minimum_population = min(
                minimum_population,
                float(np.min(state)),
                float(np.min(predicted)),
            )
            if step == steps:
                final_absolute_error = absolute_error
                final_relative_error = relative_error
            else:
                state = model.full_map(state)
                coordinates = model.reduced_map(coordinates)
        records.append(
            {
                "direction": direction.tolist(),
                "maximum_absolute_error": maximum_absolute_error,
                "maximum_absolute_error_step": maximum_absolute_error_step,
                "maximum_perturbation_relative_error": maximum_relative_error,
                "maximum_relative_error_step": maximum_relative_error_step,
                "final_absolute_error": final_absolute_error,
                "final_perturbation_relative_error": final_relative_error,
                "maximum_projected_coordinate_drift": maximum_coordinate_drift,
                "maximum_conservation_drift": maximum_conservation_drift,
                "minimum_population": minimum_population,
            }
        )
    return {
        "chart": "quadratic" if quadratic else "linear",
        "amplitude": amplitude,
        "steps": steps,
        "direction_records": records,
        "summary": {
            "maximum_absolute_error": max(
                record["maximum_absolute_error"] for record in records
            ),
            "maximum_perturbation_relative_error": max(
                record["maximum_perturbation_relative_error"] for record in records
            ),
            "maximum_final_absolute_error": max(
                record["final_absolute_error"] for record in records
            ),
            "maximum_final_perturbation_relative_error": max(
                record["final_perturbation_relative_error"] for record in records
            ),
            "maximum_projected_coordinate_drift": max(
                record["maximum_projected_coordinate_drift"] for record in records
            ),
            "maximum_conservation_drift": max(
                record["maximum_conservation_drift"] for record in records
            ),
            "minimum_population": min(
                record["minimum_population"] for record in records
            ),
        },
    }


def _stripe_quotient_lift_check(model: StripeQuadraticModel) -> dict[str, float | int]:
    direction = np.arange(1.0, 7.0)
    direction /= np.linalg.norm(direction)
    stripe = model.chart.evaluate(0.01 * direction).reshape(1, model.size, 9)
    lifted = np.repeat(stripe, model.size, axis=0)
    quotient_step = model.full_map(stripe.ravel()).reshape(1, model.size, 9)
    lifted_step = bgk_periodic_step(lifted, model.omega)
    expected = np.repeat(quotient_step, model.size, axis=0)
    difference = lifted_step - expected
    return {
        "quotient_shape_y": 1,
        "lifted_shape_y": model.size,
        "maximum_absolute_difference": float(np.max(np.abs(difference))),
        "relative_difference": float(
            np.linalg.norm(difference)
            / max(float(np.linalg.norm(expected)), np.finfo(float).eps)
        ),
    }


def run_q006s_stripe_study() -> dict[str, Any]:
    """Validate the preregistered finite-grid stripe quadratic solver oracle."""

    model = build_stripe_quadratic_model(size=17, omega=1.2)
    diagnostics = asdict(model.diagnostics)

    coarse_difference = second_derivative_tensor(
        model.full_map,
        model.chart.base,
        model.chart.tangent,
        0.006,
    )
    fine_difference = second_derivative_tensor(
        model.full_map,
        model.chart.base,
        model.chart.tangent,
        0.003,
    )
    richardson_difference = (4.0 * fine_difference - coarse_difference) / 3.0
    finite_difference_discrepancy = float(
        np.linalg.norm(richardson_difference - model.second_derivative)
        / np.linalg.norm(model.second_derivative)
    )

    residual_seed = 20260802
    residual_directions = _normalized_directions(residual_seed, 64, 6)
    amplitudes = np.array(
        [0.000625, 0.00125, 0.0025, 0.005, 0.01],
        dtype=np.float64,
    )
    residual_campaign = _stripe_residual_campaign(
        model,
        residual_directions,
        amplitudes,
    )
    residual_summary = residual_campaign["summary"]

    shadow_seed = 20260803
    shadow_directions = _normalized_directions(shadow_seed, 32, 6)
    linear_shadow = _stripe_shadow_campaign(
        model,
        shadow_directions,
        0.01,
        100,
        quadratic=False,
    )
    quadratic_shadow = _stripe_shadow_campaign(
        model,
        shadow_directions,
        0.01,
        100,
        quadratic=True,
    )
    linear_shadow_summary = linear_shadow["summary"]
    quadratic_shadow_summary = quadratic_shadow["summary"]
    shadow_improvement_ratio = (
        quadratic_shadow_summary["maximum_absolute_error"]
        / linear_shadow_summary["maximum_absolute_error"]
    )

    quotient_lift = _stripe_quotient_lift_check(model)
    stress_residual = _stripe_residual_campaign(
        model,
        residual_directions,
        np.array([0.025, 0.05, 0.1], dtype=np.float64),
    )
    stress_summary = stress_residual["summary"]

    construction_residual = max(
        diagnostics["tangent_relative_residual"],
        diagnostics["left_invariance_relative_residual"],
        diagnostics["duality_residual"],
        diagnostics["raw_symmetry_relative_residual"],
        diagnostics["homological_relative_residual"],
        diagnostics["maximum_homological_residual"],
        diagnostics["graph_gauge_relative_residual"],
        diagnostics["tangent_conservation_relative_residual"],
        diagnostics["hessian_conservation_relative_residual"],
        diagnostics["zero_wave_conserved_moment_relative_residual"],
        diagnostics["predicted_reduced_hessian_relative_norm"],
        diagnostics["output_sector_invariance_relative_residual"],
        diagnostics["forcing_sector_leakage_relative_norm"],
        diagnostics["hessian_fourier_leakage_relative_norm"],
    )
    gates = {
        "registered_sector_operator_regression": {
            "value": {
                "smallest_singular_value": diagnostics["smallest_singular_value"],
                "condition_number": diagnostics["condition_number"],
            },
            "threshold": {
                "minimum_smallest_singular_value": 0.0193,
                "maximum_condition_number": 96.1,
            },
            "passed": diagnostics["smallest_singular_value"] >= 0.0193
            and diagnostics["condition_number"] <= 96.1,
        },
        "algebraic_chart_consistency": {
            "value": construction_residual,
            "threshold": 1.0e-10,
            "passed": construction_residual <= 1.0e-10,
        },
        "independent_analytic_hessian_check": {
            "value": finite_difference_discrepancy,
            "threshold": 1.0e-8,
            "passed": finite_difference_discrepancy <= 1.0e-8,
        },
        "linear_residual_order": {
            "value": {
                "minimum": residual_summary["minimum_linear_slope"],
                "maximum": residual_summary["maximum_linear_slope"],
            },
            "threshold": {"minimum": 1.9, "maximum": 2.1},
            "passed": residual_summary["minimum_linear_slope"] >= 1.9
            and residual_summary["maximum_linear_slope"] <= 2.1,
        },
        "quadratic_residual_order": {
            "value": {
                "minimum": residual_summary["minimum_quadratic_slope"],
                "maximum": residual_summary["maximum_quadratic_slope"],
            },
            "threshold": {"minimum": 2.9, "maximum": 3.1},
            "passed": residual_summary["minimum_quadratic_slope"] >= 2.9
            and residual_summary["maximum_quadratic_slope"] <= 3.1,
        },
        "maximum_amplitude_directional_improvement": {
            "value": residual_summary["maximum_directional_residual_ratio"],
            "threshold": 0.1,
            "passed": residual_summary["maximum_directional_residual_ratio"] < 0.1,
        },
        "quadratic_shadowing_absolute_error": {
            "value": quadratic_shadow_summary["maximum_absolute_error"],
            "threshold": 1.0e-5,
            "passed": quadratic_shadow_summary["maximum_absolute_error"] < 1.0e-5,
        },
        "quadratic_shadowing_perturbation_relative_error": {
            "value": quadratic_shadow_summary[
                "maximum_perturbation_relative_error"
            ],
            "threshold": 1.0e-2,
            "passed": quadratic_shadow_summary[
                "maximum_perturbation_relative_error"
            ]
            < 1.0e-2,
        },
        "quadratic_shadowing_improvement": {
            "value": shadow_improvement_ratio,
            "threshold": 0.1,
            "passed": shadow_improvement_ratio < 0.1,
        },
        "quotient_to_square_lift": {
            "value": quotient_lift["maximum_absolute_difference"],
            "threshold": 1.0e-12,
            "passed": quotient_lift["maximum_absolute_difference"] <= 1.0e-12,
        },
    }
    passed = all(gate["passed"] for gate in gates.values())
    return {
        "question": (
            "Does the N=17, omega=1.2 fixed-leaf y-independent stripe chart "
            "solve the quadratic homological equation and raise the local "
            "invariance-residual order from two to three?"
        ),
        "hypothesis": (
            "The registered sector-restricted solve yields R2=0, satisfies "
            "the fixed-leaf algebraic gates, and passes residual-order and "
            "100-step local shadowing gates on held-out directions."
        ),
        "registered_scope": {
            "grid": [1, 17],
            "omega": 1.2,
            "master_wave_indices": [[1, 0], [-1, 0]],
            "mode_order": list(model.mode_order),
            "real_coordinate_order": "interleaved real/imaginary part per mode",
            "complex_lift_scale": float(1.0 / np.sqrt(2.0 * model.size)),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "quadratic_output_wave_indices": [[0, 0], [2, 0], [-2, 0]],
            "reduced_quadratic_hessian": "zero by the Fourier selection rule",
            "pilot_seed_not_used_for_gates": 20260801,
            "residual_seed": residual_seed,
            "shadow_seed": shadow_seed,
        },
        "construction": {
            "state_dimension": int(model.chart.base.size),
            "reduced_dimension": model.reduced_dimension,
            "hessian_shape": list(model.chart.hessian.shape),
            "solver_condition_space": (
                "ordered 6-by-6 tensor-product coefficient space (36 columns)"
            ),
            "diagnostics": diagnostics,
        },
        "finite_difference_hessian": {
            "coarse_step": 0.006,
            "fine_step": 0.003,
            "method": "centered finite difference with Richardson extrapolation",
            "analytic_relative_discrepancy": finite_difference_discrepancy,
            "coarse_to_fine_relative_change": float(
                np.linalg.norm(fine_difference - coarse_difference)
                / np.linalg.norm(richardson_difference)
            ),
        },
        "residual_order_campaign": residual_campaign,
        "shadowing_campaign": {
            "linear": linear_shadow,
            "quadratic": quadratic_shadow,
            "maximum_absolute_error_improvement_ratio": shadow_improvement_ratio,
        },
        "quotient_lift_check": quotient_lift,
        "non_gating_domain_stress": {
            "amplitudes": stress_residual["amplitudes"],
            "maximum_directional_residual_ratio_at_0p1": stress_summary[
                "maximum_directional_residual_ratio"
            ],
            "maximum_residual_ratio_at_0p1": stress_summary[
                "maximum_residual_ratio"
            ],
            "minimum_population": stress_summary["minimum_population"],
            "interpretation": (
                "Amplitude 0.1 is outside the registered local gate and is "
                "retained only to expose finite-domain degradation."
            ),
        },
        "gates": gates,
        "study_validity": "passed" if passed else "failed",
        "hypothesis_outcome": "accepted" if passed else "rejected",
        "decision": (
            "Accept the N=17 stripe construction as a finite-grid dense "
            "quadratic solver oracle on the y-independent invariant subspace."
            if passed
            else "Do not use the stripe construction as the Q006 solver oracle."
        ),
        "limitations": [
            (
                "This is a one-direction stripe oracle, not a full two-dimensional "
                "slow spectral subspace or SSM existence result."
            ),
            (
                "The Q005 isotropic candidate remains rejected, and the stripe "
                "conditioning is not claimed to be uniform under grid refinement."
            ),
            (
                "The evidence is limited to the registered sampled directions "
                "and amplitudes no larger than 0.01; it is not a uniform "
                "guarantee over the Euclidean coordinate ball."
            ),
        ],
        "next_change": (
            "Before a full 2D Q006 chart, audit whether capped resonant and "
            "near-resonant mode addition leaves every external quadratic "
            "Schur block resolved and passes a finite-grid linear "
            "normal-dominance prequalification."
        ),
    }


def run_q006s_study() -> dict[str, Any]:
    """Run and package the registered Q006s stripe oracle campaign."""

    cycle = run_q006s_stripe_study()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "construction": "finite-grid y-independent stripe solver oracle",
            "construction_grid": [1, 17],
            "square_grid_lift": [17, 17],
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold_claim": (
                "local quadratic candidate chart only; no full 2D or "
                "grid-uniform SSM existence claim"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "next_question": (
            "Q006r: does capped resonant and near-resonant mode addition resolve "
            "every external quadratic Schur block and pass finite-grid linear "
            "normal-dominance prequalification?"
        ),
    }


def run_q006r_study() -> dict[str, Any]:
    """Run and package the sealed Q006r mode-closure audit."""

    cycle = run_mode_added_closure_audit(size=17, omega=1.2)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "construction": "finite-grid quadratic spectral closure audit",
            "construction_grid": [17, 17],
            "omega": 1.2,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold_claim": (
                "coefficient and linear spectral prequalification only; no "
                "existence, uniqueness, or nonlinear normal-attraction claim"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def run_q006n_study() -> dict[str, Any]:
    """Run and package the sealed Q006n normal-gap refinement campaign."""

    cycle = run_normal_gap_refinement_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "construction": "finite registered odd-grid refinement audit",
            "grid_sizes": [9, 17, 33, 65, 129],
            "omegas": [1.0, 1.2, 1.5, 1.8],
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold_claim": (
                "finite-ladder obstruction classification only; no theorem for "
                "all odd grids and no invariant-manifold existence claim"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def run_q006c_study() -> dict[str, Any]:
    """Run and package the sealed Q006c coefficient-scaling campaign."""

    cycle = run_coefficient_scaling_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
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
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def run_q006f_study() -> dict[str, Any]:
    """Run and package the sealed Q006f checkerboard-filter campaign."""

    cycle = run_checkerboard_filter_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "construction": (
                "finite registered conservative checkerboard-filter audit"
            ),
            "grid_sizes": [17, 33, 65, 129, 257],
            "etas": [0.0, 0.01, 0.02, 0.03, 0.05],
            "omegas": [1.0, 1.2, 1.5, 1.8],
            "filter_order": (
                "post-BGK-step population-wise five-point convolution"
            ),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold_claim": (
                "filtered finite-ladder prequalification only; no all-grid "
                "theorem, nonlinear normal-attraction proof, or invariant-"
                "manifold existence or uniqueness claim"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }
