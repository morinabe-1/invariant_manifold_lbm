"""Follow-on research studies for branch tracking and manufactured oracles."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

import numpy as np

from .d2q9 import (
    fourier_symbol,
    quarter_turn_population_matrix,
    spectrum_audit,
)
from .manifold import solve_general_quadratic_parameterization
from .manufactured import (
    make_manufactured_quadratic_map,
    real_basis_from_dominant_complex_pair,
)
from .nonresonance import (
    NULL_FORCING_TOLERANCE,
    PRACTICAL_CONDITION_CEILING,
    orthogonal_acoustic_resonance_witness,
    radial_band_normal_dominance,
    stripe_quadratic_audit,
    wave_vector_from_index,
)
from .provenance import runtime_metadata, source_metadata
from .spectra import (
    TrackedHydrodynamicCluster,
    maximum_principal_angle,
    path_reversal_subspace_error,
    track_hydrodynamic_cluster_path,
)


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
