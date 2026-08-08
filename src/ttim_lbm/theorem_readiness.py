"""Sealed Q007g nonresonant-manifold theorem-readiness audit."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from .adapted_metric import (
    ETA,
    EXPECTED_SELECTED_WAVE_COUNT,
    FIXED_LEAF_DIMENSION,
    OMEGA,
    SELECTED_COMPLEX_DIMENSION,
    SIZE,
    _raw_wave_splits,
)
from .provenance import source_metadata

ComplexArray = npt.NDArray[np.complex128]

THEOREM_REFERENCE = {
    "authors": "Xavier Cabre, Ernest Fontich, and Rafael de la Llave",
    "title": (
        "The Parameterization Method for Invariant Manifolds I: "
        "Manifolds Associated to Non-Resonant Subspaces"
    ),
    "result": "Theorem 1.2 and Remark 5",
    "url": "https://upcommons.upc.edu/bitstream/handle/2117/876/0202cabre.pdf",
}

INPUT_ARTIFACTS = {
    "q006i": "q006i_full2d_quadratic.json",
    "q007a": "q007a_cubic_prequalification.json",
    "q007c": "q007c_quartic_prequalification.json",
    "q007e": "q007e_adapted_metric.json",
    "q007f": "q007f_adapted_finite_cocycle.json",
}

EXPECTED_ARTIFACT_OUTCOMES = {
    "q006i": "rejected",
    "q007a": "accepted",
    "q007c": "accepted",
    "q007e": "accepted",
    "q007f": "accepted",
}

EXPECTED_MONOMIAL_COUNTS = {2: 300, 3: 2600, 4: 17550}
EXPECTED_SPECTRAL_QUOTIENT = 89
MAXIMUM_REPRODUCTION_RELATIVE_ERROR = 1.0e-10
MINIMUM_QUOTIENT_BOUNDARY_MARGIN = 1.0e-6
MAXIMUM_SPLIT_RESIDUAL = 1.0e-10


def _default_artifact_directory() -> Path:
    return Path(__file__).resolve().parents[2] / "research" / "artifacts"


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("r", encoding="utf-8", newline=None) as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), ""):
            digest.update(chunk.encode("utf-8"))
    return digest.hexdigest()


def _relative_scalar_error(observed: float, registered: float) -> float:
    return abs(float(observed) - float(registered)) / max(
        abs(float(registered)),
        np.finfo(float).eps,
    )


def _all_numeric_values_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_numeric_values_finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_all_numeric_values_finite(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return bool(np.isfinite(value))
    if isinstance(value, (complex, np.complexfloating)):
        return bool(np.isfinite(value.real) and np.isfinite(value.imag))
    return True


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def _load_input_artifacts(
    artifact_directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    current_source = source_metadata()
    artifacts: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    for identifier, filename in INPUT_ARTIFACTS.items():
        path = artifact_directory / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        scope = payload["mathematical_scope"]
        parameter_match = (
            scope["construction_grid"] == [SIZE, SIZE]
            and float(scope["omega"]) == OMEGA
            and float(scope["eta"]) == ETA
        )
        dimension_match = True
        if identifier == "q006i":
            dimension_match = scope["selected_real_dimension"] == 24
        elif identifier in {"q007a", "q007c"}:
            dimension_match = scope["complex_mode_count"] == 24
        elif identifier == "q007e":
            dimension_match = (
                scope["selected_complex_dimension"] == SELECTED_COMPLEX_DIMENSION
                and scope["fixed_leaf_dimension"] == FIXED_LEAF_DIMENSION
                and scope["wave_block_count"] == SIZE * SIZE
            )
        elif identifier == "q007f":
            dimension_match = (
                scope["real_reduced_dimension"] == 24
                and scope["adapted_fixed_leaf_dimension"] == FIXED_LEAF_DIMENSION
            )
        records[identifier] = {
            "filename": filename,
            "sha256": _file_sha256(path),
            "sha256_newline_normalization": "UTF-8 text with universal newlines",
            "schema_version": payload.get("schema_version"),
            "source_match": payload.get("source") == current_source,
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "expected_scientific_outcome": EXPECTED_ARTIFACT_OUTCOMES[identifier],
            "parameter_match": bool(parameter_match),
            "dimension_match": bool(dimension_match),
            "passed": bool(
                payload.get("schema_version") == 1
                and payload.get("source") == current_source
                and payload.get("study_gate") == "passed"
                and payload.get("scientific_outcome")
                == EXPECTED_ARTIFACT_OUTCOMES[identifier]
                and parameter_match
                and dimension_match
            ),
        }
        artifacts[identifier] = payload
    return artifacts, records


def _map_structure_audit() -> dict[str, Any]:
    filter_lower_bound = 1.0 - 2.0 * ETA
    collision_kinetic_eigenvalue = 1.0 - OMEGA
    collision_site_determinant = collision_kinetic_eigenvalue**6
    checks = {
        "equilibrium_analytic_near_unit_density": True,
        "collision_derivative_invertible": collision_kinetic_eigenvalue != 0.0,
        "streaming_is_a_permutation": True,
        "filter_has_positive_uniform_multiplier_lower_bound": filter_lower_bound > 0.0,
        "fixed_global_mass_momentum_leaf_is_invariant": True,
        "conserved_quotient_derivative_is_identity": True,
    }
    return {
        "equilibrium_density_at_fixed_point": 1.0,
        "equilibrium_singularity": "a local density equal to zero",
        "omega": OMEGA,
        "eta": ETA,
        "collision_kinetic_eigenvalue": collision_kinetic_eigenvalue,
        "collision_derivative_determinant_per_site": collision_site_determinant,
        "filter_multiplier_uniform_lower_bound": filter_lower_bound,
        "streaming_inverse": "opposite periodic shift",
        "fixed_leaf_inverse_argument": (
            "the full derivative is invertible, the conserved quotient is the "
            "identity, and the fixed-leaf tangent is invariant"
        ),
        "checks": checks,
        "local_diffeomorphism_structurally_proved": all(checks.values()),
    }


def _eigenvalues() -> tuple[ComplexArray, ComplexArray, int, float]:
    splits = _raw_wave_splits()
    selected = np.concatenate(
        [
            np.linalg.eigvals(split.selected_matrix)
            for split in splits
            if split.selected_dimension
        ]
    ).astype(np.complex128, copy=False)
    excluded = np.concatenate(
        [np.linalg.eigvals(split.external_matrix) for split in splits]
    ).astype(np.complex128, copy=False)
    maximum_split_residual = max(
        split.block_diagonalization_residual for split in splits
    )
    selected_wave_count = sum(split.selected_dimension > 0 for split in splits)
    return selected, excluded, selected_wave_count, float(maximum_split_residual)


def _spectral_audit(q007e: dict[str, Any]) -> dict[str, Any]:
    selected, excluded, selected_wave_count, maximum_split_residual = _eigenvalues()
    selected_moduli = np.abs(selected)
    excluded_moduli = np.abs(excluded)
    registered = q007e["cycle"]["metric_construction"]["spectral_gap"]
    selected_minimum = float(np.min(selected_moduli))
    selected_maximum = float(np.max(selected_moduli))
    excluded_minimum = float(np.min(excluded_moduli))
    excluded_maximum = float(np.max(excluded_moduli))
    finite = bool(
        np.all(np.isfinite(selected.real))
        and np.all(np.isfinite(selected.imag))
        and np.all(np.isfinite(excluded.real))
        and np.all(np.isfinite(excluded.imag))
    )
    nonzero = bool(excluded_minimum > 0.0 and selected_minimum > 0.0)
    return {
        "wave_block_count": SIZE * SIZE,
        "selected_complex_dimension": int(selected.size),
        "excluded_complex_dimension": int(excluded.size),
        "fixed_leaf_complex_dimension": int(selected.size + excluded.size),
        "selected_wave_count": selected_wave_count,
        "selected_minimum_modulus": selected_minimum,
        "selected_maximum_modulus": selected_maximum,
        "excluded_minimum_modulus": excluded_minimum,
        "excluded_maximum_modulus": excluded_maximum,
        "all_eigenvalues_finite": finite,
        "all_eigenvalues_nonzero": nonzero,
        "selected_spectrum_strictly_stable_numerically": selected_maximum < 1.0,
        "maximum_block_diagonalization_relative_residual": maximum_split_residual,
        "q007e_reproduction": {
            "selected_minimum_relative_error": _relative_scalar_error(
                selected_minimum,
                registered["minimum_selected_modulus"],
            ),
            "excluded_maximum_relative_error": _relative_scalar_error(
                excluded_maximum,
                registered["maximum_excluded_modulus"],
            ),
        },
        "certification_level": (
            "float64 block eigenspectrum and Riesz-split reproduction; not an "
            "outward-rounded spectral enclosure"
        ),
    }


def _spectral_quotient_audit(spectral: dict[str, Any]) -> dict[str, Any]:
    selected_radius = float(spectral["selected_maximum_modulus"])
    excluded_minimum = float(spectral["excluded_minimum_modulus"])
    quotient = 1
    while selected_radius ** (quotient + 1) / excluded_minimum >= 1.0:
        quotient += 1
        if quotient > 100_000:
            raise RuntimeError("failed to locate the finite spectral quotient")
    tail_ratio = selected_radius ** (quotient + 1) / excluded_minimum
    previous_ratio = selected_radius**quotient / excluded_minimum
    tail_margin = 1.0 - tail_ratio
    previous_margin = previous_ratio - 1.0
    return {
        "definition": (
            "minimum L >= 1 with rho(A1)^(L+1) / "
            "min(abs(Spec(A2))) < 1"
        ),
        "selected_spectral_radius": selected_radius,
        "excluded_minimum_modulus": excluded_minimum,
        "observed_L": quotient,
        "registered_L": EXPECTED_SPECTRAL_QUOTIENT,
        "registered_L_match": quotient == EXPECTED_SPECTRAL_QUOTIENT,
        "tail_ratio_at_L": float(tail_ratio),
        "tail_margin_below_one": float(tail_margin),
        "previous_ratio": float(previous_ratio),
        "previous_margin_above_one": float(previous_margin),
        "tail_separation_starts_at_degree": quotient + 1,
        "boundary_gate_passed": bool(
            quotient == EXPECTED_SPECTRAL_QUOTIENT
            and tail_ratio < 1.0
            and previous_ratio >= 1.0
            and tail_margin >= MINIMUM_QUOTIENT_BOUNDARY_MARGIN
            and previous_margin >= MINIMUM_QUOTIENT_BOUNDARY_MARGIN
        ),
        "certification_level": (
            "float64 spectral-quotient prequalification; not an interval proof"
        ),
    }


def _summary_record(
    degree: int,
    summary: dict[str, Any],
    artifact_identifier: str,
    artifact_sha256: str,
) -> dict[str, Any]:
    return {
        "degree": degree,
        "artifact": artifact_identifier,
        "artifact_sha256": artifact_sha256,
        "record_count": int(summary["record_count"]),
        "expected_record_count": EXPECTED_MONOMIAL_COUNTS[degree],
        "numerically_singular_block_count": int(
            summary["numerically_singular_block_count"]
        ),
        "minimum_operator_singular_value": float(
            summary["minimum_operator_singular_value"]
        ),
        "maximum_operator_condition_number": float(
            summary["maximum_operator_condition_number"]
        ),
        "sector_counts": summary["sector_counts"],
        "numerical_gate_passed": bool(
            summary["record_count"] == EXPECTED_MONOMIAL_COUNTS[degree]
            and summary["numerically_singular_block_count"] == 0
            and summary["minimum_operator_singular_value"] > 0.0
            and np.isfinite(summary["maximum_operator_condition_number"])
        ),
        "direct_theorem_condition_certified": False,
        "evidence_scope": (
            "float64 Fourier-selection-rule sector operator only; it neither "
            "compares each product with every eigenvalue of A2 nor supplies "
            "an interval/algebraic nonresonance certificate"
        ),
    }


def _order_evidence(
    artifacts: dict[str, dict[str, Any]],
    artifact_records: dict[str, dict[str, Any]],
    spectral_quotient: int,
) -> dict[str, Any]:
    q006i_diagnostics = artifacts["q006i"]["cycle"]["construction"]["diagnostics"]
    q007a_cycle = artifacts["q007a"]["cycle"]
    q007c_cycle = artifacts["q007c"]["cycle"]
    degree_records = [
        _summary_record(
            2,
            q007a_cycle["pair_control_summary"],
            "q007a",
            artifact_records["q007a"]["sha256"],
        ),
        _summary_record(
            3,
            q007a_cycle["triple_summary"],
            "q007a",
            artifact_records["q007a"]["sha256"],
        ),
        _summary_record(
            4,
            q007c_cycle["quartic_summary"],
            "q007c",
            artifact_records["q007c"]["sha256"],
        ),
    ]
    pair_summary = q007a_cycle["pair_control_summary"]
    triple_summary = q007a_cycle["triple_summary"]
    q007c_pair = q007c_cycle["pair_control_summary"]
    q007c_triple = q007c_cycle["triple_control_summary"]
    control_reproduction = {
        "q006i_q007a_pair_count_match": (
            q006i_diagnostics["pair_count"] == pair_summary["record_count"]
        ),
        "q006i_q007a_pair_minimum_singular_relative_error": _relative_scalar_error(
            q006i_diagnostics["minimum_operator_singular_value"],
            pair_summary["minimum_operator_singular_value"],
        ),
        "q006i_q007a_pair_maximum_condition_relative_error": _relative_scalar_error(
            q006i_diagnostics["maximum_operator_condition_number"],
            pair_summary["maximum_operator_condition_number"],
        ),
        "q007a_q007c_pair_minimum_singular_relative_error": _relative_scalar_error(
            pair_summary["minimum_operator_singular_value"],
            q007c_pair["minimum_operator_singular_value"],
        ),
        "q007a_q007c_pair_maximum_condition_relative_error": _relative_scalar_error(
            pair_summary["maximum_operator_condition_number"],
            q007c_pair["maximum_operator_condition_number"],
        ),
        "q007a_q007c_triple_minimum_singular_relative_error": _relative_scalar_error(
            triple_summary["minimum_operator_singular_value"],
            q007c_triple["minimum_operator_singular_value"],
        ),
        "q007a_q007c_triple_maximum_condition_relative_error": _relative_scalar_error(
            triple_summary["maximum_operator_condition_number"],
            q007c_triple["maximum_operator_condition_number"],
        ),
    }
    required_orders = list(range(2, spectral_quotient + 1))
    sector_numerical_orders = [2, 3, 4]
    global_theorem_numerical_orders: list[int] = []
    certified_orders: list[int] = []
    return {
        "degree_records": degree_records,
        "control_reproduction": control_reproduction,
        "required_orders": required_orders,
        "required_order_count": len(required_orders),
        "sector_aware_float64_orders": sector_numerical_orders,
        "global_direct_theorem_float64_orders": global_theorem_numerical_orders,
        "certified_direct_theorem_orders": certified_orders,
        "missing_sector_aware_float64_orders": list(range(5, spectral_quotient + 1)),
        "missing_sector_aware_float64_order_count": max(spectral_quotient - 4, 0),
        "uncertified_direct_theorem_orders": required_orders,
        "uncertified_direct_theorem_order_count": len(required_orders),
        "first_missing_sector_aware_float64_order": (
            5 if spectral_quotient >= 5 else None
        ),
        "first_uncertified_direct_theorem_order": 2,
        "all_existing_numerical_gates_passed": bool(
            all(record["numerical_gate_passed"] for record in degree_records)
            and control_reproduction["q006i_q007a_pair_count_match"]
            and all(
                value <= MAXIMUM_REPRODUCTION_RELATIVE_ERROR
                for key, value in control_reproduction.items()
                if key.endswith("relative_error")
            )
        ),
        "direct_theorem_evidence_gap": (
            "the existing homological audits are translation-sector-aware, "
            "whereas the fixed Theorem 1.2 hypothesis is stated for the full "
            "Spec(A1)^i versus Spec(A2) product set"
        ),
    }


def _readiness_audit(
    structure: dict[str, Any],
    spectral: dict[str, Any],
    quotient: dict[str, Any],
    orders: dict[str, Any],
) -> dict[str, Any]:
    qualitative_requirements = {
        "analytic_map_and_fixed_leaf": {
            "satisfied": structure["local_diffeomorphism_structurally_proved"],
            "evidence": "structural algebra at the rest equilibrium",
        },
        "local_diffeomorphism": {
            "satisfied": structure["local_diffeomorphism_structurally_proved"],
            "evidence": structure["fixed_leaf_inverse_argument"],
        },
        "certified_selected_stability_and_invariant_split": {
            "satisfied": False,
            "evidence": spectral["certification_level"],
        },
        "certified_spectral_quotient_tail": {
            "satisfied": False,
            "evidence": quotient["certification_level"],
        },
        "certified_external_nonresonance_degrees_2_through_L": {
            "satisfied": (
                len(orders["uncertified_direct_theorem_orders"]) == 0
            ),
            "evidence": orders["direct_theorem_evidence_gap"],
        },
    }
    qualitative_ready = all(
        record["satisfied"] for record in qualitative_requirements.values()
    )
    quantitative_objects = {
        "banach_function_space_and_norm": False,
        "chart_domain_and_range_buffer": False,
        "graph_gauge": True,
        "rigorous_linearized_inverse_bound": False,
        "domain_uniform_defect_majorant": False,
        "domain_uniform_derivative_variation_majorant": False,
        "finite_taylor_tail_majorant": False,
        "roundoff_enclosure": False,
        "theorem_specific_strict_sufficient_inequality": False,
    }
    quantitative_ready = bool(
        qualitative_ready and all(quantitative_objects.values())
    )
    return {
        "qualitative_requirements": qualitative_requirements,
        "qualitative_theorem_ready": qualitative_ready,
        "quantitative_proof_objects": quantitative_objects,
        "quantitative_chart_ready": quantitative_ready,
        "state_adapted_norm_available_numerically": True,
        "state_adapted_norm_is_not_a_banach_function_norm": True,
        "first_missing_layer": (
            "outward-rounded eigenvalue and Riesz-projector enclosures for all "
            "289 Fourier blocks, followed by a full-theorem or explicitly "
            "equivariant nonresonance condition"
        ),
        "ready_for_computer_assisted_existence_proof": bool(
            qualitative_ready and quantitative_ready
        ),
    }


def run_theorem_readiness_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Audit the exact gap between Q007 evidence and the fixed theorem."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    artifacts, artifact_records = _load_input_artifacts(directory)
    structure = _map_structure_audit()
    spectral = _spectral_audit(artifacts["q007e"])
    quotient = _spectral_quotient_audit(spectral)
    orders = _order_evidence(
        artifacts,
        artifact_records,
        int(quotient["observed_L"]),
    )
    readiness = _readiness_audit(structure, spectral, quotient, orders)

    artifact_gate_passed = all(record["passed"] for record in artifact_records.values())
    spectral_gate_passed = bool(
        spectral["selected_complex_dimension"] == SELECTED_COMPLEX_DIMENSION
        and spectral["selected_wave_count"] == EXPECTED_SELECTED_WAVE_COUNT
        and spectral["excluded_complex_dimension"]
        == FIXED_LEAF_DIMENSION - SELECTED_COMPLEX_DIMENSION
        and spectral["fixed_leaf_complex_dimension"] == FIXED_LEAF_DIMENSION
        and spectral["all_eigenvalues_finite"]
        and spectral["all_eigenvalues_nonzero"]
        and spectral["selected_spectrum_strictly_stable_numerically"]
        and spectral["maximum_block_diagonalization_relative_residual"]
        <= MAXIMUM_SPLIT_RESIDUAL
        and max(spectral["q007e_reproduction"].values())
        <= MAXIMUM_REPRODUCTION_RELATIVE_ERROR
    )
    validity_gates: dict[str, dict[str, Any]] = {
        "registered_artifact_provenance": {
            "passed": artifact_gate_passed,
            "threshold": "all five artifacts match source, scope, and outcome",
            "value": artifact_gate_passed,
        },
        "analytic_local_diffeomorphism_structure": {
            "passed": structure["local_diffeomorphism_structurally_proved"],
            "threshold": True,
            "value": structure["local_diffeomorphism_structurally_proved"],
        },
        "fixed_leaf_spectrum_reproduction": {
            "passed": spectral_gate_passed,
            "threshold": {
                "selected_dimension": SELECTED_COMPLEX_DIMENSION,
                "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
                "maximum_reproduction_relative_error": (
                    MAXIMUM_REPRODUCTION_RELATIVE_ERROR
                ),
                "maximum_split_residual": MAXIMUM_SPLIT_RESIDUAL,
            },
            "value": {
                "selected_dimension": spectral["selected_complex_dimension"],
                "fixed_leaf_dimension": spectral["fixed_leaf_complex_dimension"],
                "maximum_reproduction_relative_error": max(
                    spectral["q007e_reproduction"].values()
                ),
                "maximum_split_residual": spectral[
                    "maximum_block_diagonalization_relative_residual"
                ],
            },
        },
        "spectral_quotient_boundary": {
            "passed": quotient["boundary_gate_passed"],
            "threshold": {
                "registered_L": EXPECTED_SPECTRAL_QUOTIENT,
                "minimum_boundary_margin": MINIMUM_QUOTIENT_BOUNDARY_MARGIN,
            },
            "value": {
                "observed_L": quotient["observed_L"],
                "tail_margin": quotient["tail_margin_below_one"],
                "previous_margin": quotient["previous_margin_above_one"],
            },
        },
        "existing_degree_evidence_reproduction": {
            "passed": orders["all_existing_numerical_gates_passed"],
            "threshold": {
                "degrees": [2, 3, 4],
                "record_counts": EXPECTED_MONOMIAL_COUNTS,
                "singular_block_count": 0,
            },
            "value": {
                "degrees": [record["degree"] for record in orders["degree_records"]],
                "record_counts": {
                    str(record["degree"]): record["record_count"]
                    for record in orders["degree_records"]
                },
                "singular_block_counts": {
                    str(record["degree"]): record[
                        "numerically_singular_block_count"
                    ]
                    for record in orders["degree_records"]
                },
            },
        },
    }
    preliminary = {
        "question": (
            "Do the current fixed-leaf Q007 artifacts satisfy the fixed "
            "nonresonant-manifold theorem and quantitative a posteriori "
            "readiness requirements?"
        ),
        "registered_theorem": THEOREM_REFERENCE,
        "registered_setup": {
            "grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "fixed_leaf_real_dimension": FIXED_LEAF_DIMENSION,
            "selected_real_dimension": 24,
            "complexified_selected_dimension": SELECTED_COMPLEX_DIMENSION,
            "complexified_excluded_dimension": (
                FIXED_LEAF_DIMENSION - SELECTED_COMPLEX_DIMENSION
            ),
            "new_direction_or_defect_campaign": False,
            "metric_retuned": False,
        },
        "input_artifacts": artifact_records,
        "map_structure": structure,
        "spectral_audit": spectral,
        "spectral_quotient": quotient,
        "order_evidence": orders,
        "readiness": readiness,
        "validity_gates": validity_gates,
    }
    finite = _all_numeric_values_finite(preliminary)
    strict_json = _strict_json_serializable(preliminary)
    validity_gates["strict_json_finite_values"] = {
        "passed": bool(finite and strict_json),
        "threshold": True,
        "value": bool(finite and strict_json),
    }
    study_validity = (
        "passed"
        if all(gate["passed"] for gate in validity_gates.values())
        else "inconclusive"
    )
    ready = readiness["ready_for_computer_assisted_existence_proof"]
    if study_validity != "passed":
        outcome = "inconclusive"
        classification = "registered theorem-readiness audit is inconclusive"
        decision = (
            "At least one audit-validity gate failed, so no theorem-readiness "
            "classification is made."
        )
    elif ready:
        outcome = "accepted"
        classification = "ready for a computer-assisted existence proof"
        decision = (
            "Every qualitative and quantitative theorem-readiness requirement "
            "is certified."
        )
    else:
        outcome = "not_ready"
        classification = "current evidence is not theorem-ready"
        decision = (
            "The structural map checks and numerical reproductions pass, but "
            "the direct theorem requires certified full-spectrum "
            "nonresonance through degree 89, while the current degree-2--4 "
            "evidence is sector-aware float64 evidence only; the quantitative "
            "inverse, domain, defect, variation, tail, and roundoff objects are "
            "also absent."
        )

    result = {
        **preliminary,
        "study_validity": study_validity,
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "preserved_prior_outcomes": {
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_storage_rejection_changed": False,
        },
        "claim_boundary": (
            "This is a theorem-applicability inventory, not an invariant-"
            "manifold nonexistence result, an a posteriori radius, a full-ball "
            "normal-attraction bound, or a replacement for the Q007f finite-"
            "sample comparison."
        ),
        "next_change": (
            "Q007h must resolve the direct-full-spectrum versus translation-"
            "equivariant nonresonance mismatch and produce outward-rounded "
            "linear spectral enclosures before any high-order or nonlinear "
            "a posteriori proof campaign."
        ),
    }
    if not _all_numeric_values_finite(result) or not _strict_json_serializable(result):
        raise RuntimeError("Q007g produced a non-finite or non-JSON result")
    return result
