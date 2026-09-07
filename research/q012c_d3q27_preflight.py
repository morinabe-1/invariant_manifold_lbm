"""Q012c: first-shell D3Q27 quadratic sectors and full-grid normal ordering."""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from research import d3q27 as d3
from research import d3q27_quadratic as quadratic
from research import d3q27_spectra as spectra
from research import q012a_d3q27_foundation as q012a
from research import q012b_d3q27_spectral as q012b
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

GRID_SIZES = (17, 33, 65)
OMEGAS = (1.0, 1.2, 1.5, 1.8)
SHELLS = (1, 2, 3)
Q012B_ARTIFACT_SHA256 = "53753f2d2344d5ec308a7498875703f0c89ae8d184ade1d8f19377ffbc10b870"
Q012B_RESULT_SHA256 = "b26abf59676f6689216f9143068d7a06dfad432faf7c723e9ab4b3fec3fa632d"


def input_audit() -> dict[str, Any]:
    path = q012a.ARTIFACT_DIRECTORY / "q012b_d3q27_spectral.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    checks = {
        "artifact_seal": _file_sha256(path) == Q012B_ARTIFACT_SHA256,
        "result_digest": q012a._digest(cycle) == digest == Q012B_RESULT_SHA256,
        "runner_seal": _file_sha256(Path(q012b.__file__)) == artifact["runner_source"]["sha256"],
        "all_prior_hypotheses_accepted": artifact["scientific_outcome"] == "accepted"
        and artifact["study_gate"] == "passed"
        and all(cycle["hypothesis_gates"].values()),
        "q012b_prerequisites_still_sealed": q012b.input_audit()["passed"],
    }
    for name, module in (("lattice", d3), ("spectra", spectra), ("foundation_runner", q012a)):
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
        )
    return {"filename": path.name, "checks": checks, "passed": all(checks.values())}


def algebra_controls() -> dict[str, Any]:
    rng = np.random.default_rng(2026090706)
    inputs = np.array(((0.74 * np.exp(0.21j), 0.035j), (0, 0.68 * np.exp(-0.31j))))
    external = np.array(((0.23, 0.07j), (0, 0.29)), dtype=complex)
    symmetric = quadratic.symmetric_square_basis(2)
    full_product = np.kron(inputs, inputs)
    reduced_product = symmetric.T @ full_product @ symmetric
    a = np.array((0.37 + 0.1j, -0.23 + 0.2j))
    aa = symmetric.T @ np.kron(a, a)
    sym_action = float(
        np.linalg.norm(reduced_product @ aa - symmetric.T @ np.kron(inputs @ a, inputs @ a))
    )
    known = rng.standard_normal((2, 3)) + 1j * rng.standard_normal((2, 3))
    forcing = known @ reduced_product - external @ known
    recovered, manufactured = quadratic.solve_homological(external, reduced_product, forcing)
    known_error = float(np.linalg.norm(recovered - known) / np.linalg.norm(known))
    operator = quadratic.homological_operator(external, reduced_product)
    vector_error = float(
        np.linalg.norm(
            operator @ known.reshape(-1, order="F")
            - (external @ known - known @ reduced_product).reshape(-1, order="F")
        )
    )
    singular = np.diag((0.49, 0.2)).astype(complex)
    _, compatible = quadratic.solve_homological(
        singular, np.array([[0.49]]), np.array([[0.0], [1.0]])
    )
    _, incompatible = quadratic.solve_homological(
        singular, np.array([[0.49]]), np.array([[1.0], [0.0]])
    )

    # This finite difference uses the nonlinear physical-space map, not the
    # homological right-hand-side assembly being checked.
    base = d3.uniform_equilibrium((3, 3, 3), np.zeros(4))
    left, right = rng.standard_normal((2, 3, 3, 3, 27))
    left /= np.linalg.norm(left)
    right /= np.linalg.norm(right)
    moments = d3.conserved_moment_matrix()
    hessian = d3.equilibrium_hessian_at_rest()
    analytic = d3.stream_periodic(
        1.2
        * np.einsum(
            "qab,...a,...b->...q",
            hessian,
            np.einsum("aq,...q->...a", moments, left),
            np.einsum("aq,...q->...a", moments, right),
        )
    )
    differences = []
    for step in (1e-3, 5e-4, 2.5e-4):
        mixed = (
            d3.bgk_periodic_step(base + step * (left + right), 1.2)
            - d3.bgk_periodic_step(base + step * (left - right), 1.2)
            - d3.bgk_periodic_step(base + step * (-left + right), 1.2)
            + d3.bgk_periodic_step(base - step * (left + right), 1.2)
        ) / (4 * step**2)
        differences.append(
            {
                "step": step,
                "relative_error": float(
                    np.linalg.norm(mixed - analytic) / np.linalg.norm(analytic)
                ),
            }
        )
    conservation = float(np.linalg.norm(np.einsum("aq,qij->aij", moments, hessian)))

    frames, frame_audit = quadratic.build_frames(17, 1.2)
    shear = frames[(0, 0, 1)].blocks[0]
    output = (0, 0, 2)
    sector = quadratic.external_sector(output, 17, 1.2, None)
    original = quadratic.audit_pair(shear, shear, 17, 1.2, sector, None)
    unitary = np.array(((1, 1j), (1j, 1))) / np.sqrt(2)
    rotated = replace(
        shear, basis=shear.basis @ unitary, dynamics=unitary.conj().T @ shear.dynamics @ unitary
    )
    changed = quadratic.audit_pair(rotated, rotated, 17, 1.2, sector, None)
    basis_keys = (
        "smallest_singular_value",
        "largest_singular_value",
        "forcing_norm",
        "response_local_norm",
    )
    basis_error = max(
        abs(original[key] - changed[key]) / max(1, abs(original[key])) for key in basis_keys
    )
    gates = {
        "symmetric_square_action": sym_action <= 1e-12,
        "column_major_sylvester_action": vector_error <= 1e-12,
        "known_complex_block_solution": manufactured["passed"] and known_error <= 1e-12,
        "singular_compatible_is_not_prequalified": compatible["status"] == "singular_compatible"
        and not compatible["passed"],
        "singular_incompatible_is_rejected": incompatible["status"] == "singular_incompatible"
        and not incompatible["passed"],
        "independent_physical_mixed_derivative": differences[-1]["relative_error"] <= 1e-5,
        "analytic_hessian_conserves": conservation <= 5e-12,
        "shear_unitary_basis_invariance": frame_audit["passed"] and basis_error <= 5e-12,
    }
    return {
        "gates": gates,
        "symmetric_square_action_error": sym_action,
        "vectorization_error": vector_error,
        "known_solution_relative_error": known_error,
        "manufactured_operator": manufactured,
        "singular_compatible": compatible,
        "singular_incompatible": incompatible,
        "mixed_derivative_records": differences,
        "hessian_moment_error": conservation,
        "shear_basis_change_error": basis_error,
        "passed": all(gates.values()),
    }


def brute_force_control() -> dict[str, Any]:
    # No first-shell classification is assumed at this coarse control grid.
    # It verifies orbit multiplicity and the full fixed-leaf external inventory.
    quotient = quadratic.normal_ordering(quadratic.grid_spectrum(5, 1.2), None)
    brute = quadratic.normal_ordering(quadratic.grid_spectrum(5, 1.2, brute_force=True), None)
    error = abs(quotient["slowest_external"]["modulus"] - brute["slowest_external"]["modulus"])
    norm_error = abs(
        quotient["maximum_external_one_step_norm"] - brute["maximum_external_one_step_norm"]
    )
    return {
        "size": 5,
        "scope": "full fixed-leaf spectrum; no coarse-grid hydrodynamic candidate",
        "orbit": quotient,
        "brute_force": brute,
        "maximum_modulus_error": error,
        "maximum_one_step_norm_error": norm_error,
        "passed": quotient["coverage_passed"]
        and brute["coverage_passed"]
        and error <= 5e-12
        and norm_error <= 5e-12,
    }


def pack_pairs(screen: dict[str, Any]) -> dict[str, Any]:
    """Store every metric without repeating its name thousands of times."""
    screen = dict(screen)
    records = screen.pop("pair_records")
    columns = list(records[0])
    if any(list(record) != columns for record in records):
        raise ValueError("pair records have inconsistent columns")
    screen["pair_columns"] = columns
    screen["pair_rows"] = [[record[column] for column in columns] for record in records]
    return screen


def unpack_pairs(screen: dict[str, Any]) -> list[dict[str, Any]]:
    columns = screen["pair_columns"]
    if any(len(row) != len(columns) for row in screen["pair_rows"]):
        raise ValueError("pair table width is inconsistent")
    return [dict(zip(columns, row)) for row in screen["pair_rows"]]


def classify_families(conditions: list[dict[str, Any]]) -> tuple[list[dict], dict | None]:
    families = []
    for shell in SHELLS:
        for omega in OMEGAS:
            selected = [r for r in conditions if r["shell"] == shell and r["omega"] == omega]
            coverage = tuple(r["size"] for r in selected) == GRID_SIZES
            families.append(
                {
                    "shell": shell,
                    "omega": omega,
                    "real_coordinate_count": 4 * len(quadratic.shell_waves(shell)),
                    "coefficient_all_grids": coverage
                    and all(r["coefficient_screen"]["coefficient_prequalified"] for r in selected),
                    "normal_ordering_all_grids": coverage
                    and all(r["normal_ordering"]["normal_ordering_prequalified"] for r in selected),
                    "jointly_viable": coverage and all(r["jointly_prequalified"] for r in selected),
                }
            )
    chosen = next((copy.deepcopy(f) for f in families if f["jointly_viable"]), None)
    return families, chosen


def run_study(progress: Callable[[dict], None] | None = None) -> dict[str, Any]:
    inputs = input_audit()
    algebra = brute = None
    conditions, frames_evidence = [], []
    if inputs["passed"]:
        algebra, brute = algebra_controls(), brute_force_control()
        for size in GRID_SIZES:
            for omega in OMEGAS:
                frames, diagnostics = quadratic.build_frames(size, omega)
                frames_evidence.append({"size": size, "omega": omega, **diagnostics})
                coefficient_screens = quadratic.coefficient_campaign(size, omega, frames)
                grid = quadratic.grid_spectrum(size, omega, frames)
                for screen in coefficient_screens:
                    normal = quadratic.normal_ordering(grid, screen["shell"])
                    condition = {
                        "size": size,
                        "omega": omega,
                        "shell": screen["shell"],
                        "coefficient_screen": pack_pairs(screen),
                        "normal_ordering": normal,
                        "jointly_prequalified": screen["coefficient_prequalified"]
                        and normal["normal_ordering_prequalified"],
                    }
                    conditions.append(condition)
                    if progress is not None:
                        progress(
                            {
                                "size": size,
                                "omega": omega,
                                "shell": screen["shell"],
                                "pair_statuses": screen["status_counts"],
                                "normal_gap": normal["normal_modulus_gap"],
                                "jointly_prequalified": condition["jointly_prequalified"],
                            }
                        )
    coverage = (
        len(conditions) == 36
        and len(frames_evidence) == 12
        and {(r["size"], r["omega"], r["shell"]) for r in conditions}
        == {(n, w, s) for n in GRID_SIZES for w in OMEGAS for s in SHELLS}
    )
    gates = {
        "sealed_inputs": inputs["passed"],
        "registered_coverage": coverage,
        "independent_algebra_controls": algebra is not None and algebra["passed"],
        "brute_force_grid_control": brute is not None and brute["passed"],
        "cluster_frame_structure": bool(frames_evidence)
        and all(r["passed"] for r in frames_evidence),
        "every_pair_and_fixed_leaf_dimension": bool(conditions)
        and all(
            r["coefficient_screen"]["coverage_passed"] and r["normal_ordering"]["coverage_passed"]
            for r in conditions
        ),
        "coefficient_structure": bool(conditions)
        and all(r["coefficient_screen"]["maximum_structural_error"] <= 5e-12 for r in conditions),
        "finite_evidence": _all_numeric_values_finite(
            (conditions, frames_evidence, algebra, brute)
        ),
    }
    families, chosen = classify_families(conditions)
    outcome = (
        "inconclusive"
        if not all(gates.values())
        else "accepted"
        if chosen is not None
        else "rejected"
    )
    cycle = {
        "question": "Does an unmodified D3Q27 first-shell family pass quadratic nonresonance and linear normal ordering across three odd grids?",
        "map": "unmodified periodic D3Q27 BGK, fixed four-conservation leaf",
        "input_audit": inputs,
        "algebra_controls": algebra,
        "brute_force_control": brute,
        "frame_audits": frames_evidence,
        "conditions": conditions,
        "families": families,
        "selected_family": chosen,
        "validity_gates": gates,
        "study_validity": "passed" if all(gates.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite-degree floating prequalification only; neither actual exact resonance nor 3D manifold existence, uniqueness or nonlinear normal attraction is certified",
        "next_question": "Q012d: dense quadratic chart for the selected family"
        if outcome == "accepted"
        else "Diagnose coefficient and normal-ordering failures separately; preregister a repair without replacing the unmodified BGK result",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "runner_source": {"filename": Path(__file__).name, "sha256": _file_sha256(Path(__file__))},
        "helper_sources": {
            name: {
                "filename": Path(module.__file__).name,
                "sha256": _file_sha256(Path(module.__file__)),
            }
            for name, module in (
                ("lattice", d3),
                ("spectra", spectra),
                ("quadratic", quadratic),
                ("foundation_runner", q012a),
                ("spectral_runner", q012b),
            )
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_study(lambda record: print(json.dumps(record), flush=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Table rows are compact JSON; the concise scientific narrative lives in docs.
    args.output.write_text(
        json.dumps(result, allow_nan=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "study_gate": result["study_gate"],
                "scientific_outcome": result["scientific_outcome"],
                "selected_family": result["cycle"]["selected_family"],
            }
        )
    )
    if result["study_gate"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
