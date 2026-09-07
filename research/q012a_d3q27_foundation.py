"""Q012a: D2Q9 prerequisite audit and tensor-product D3Q27 foundation."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
from typing import Any

import numpy as np

from research import d3q27 as d3
from ttim_lbm import d2q9 as d2
from ttim_lbm.manifold import (
    QuadraticChart,
    second_derivative_tensor,
    solve_identity_center_quadratic,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

ARTIFACT_DIRECTORY = Path(__file__).resolve().parent / "artifacts"
EXPECTED_PACKAGE_SOURCE = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"
INPUT_SEALS = {
    "q004b_and_manufactured": "4ef466985f9db18381ac6a50d8a93d9d7d228eeb8d0f5d6275831d3b21d27ab4",
    "q005_nonresonance": "bbd81b5e0d899804dd23cec719a55398e9d82631637ab39b689ae916fafcb4aa",
    "q006h_cluster_complete": "71ff668cbc247450029840bf5de71e6ecbd364c5fcca21c9e8ec8085a5ee956c",
    "q006i_full2d_quadratic": "347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89",
    "q006p_dual_reporting": "aa19ac5ed6273005345957bbd07b15067b3f0362723789b4023bec67ea14a953",
    "q006q_forward_error_holdout": "c024a7c578c7b32c4fc6694dc14edc9f4b8ed66d52ffbbe50f9f5f4ba388cb08",
    "q007ap_forward_shadowing": "3b35ad0c3f8979f295214ae16c7be09f6a1047b2779f9eeabe3dabec759e49f0",
    "q011g_forced_representation_audit": "842ddbae2a28ccd2f11a112f23205cb049668b82691fdd180edc5ac20fecaa25",
    "q011h_sparse_chart_equivalence": "2cfcf5cb76698ae8e451f448a3048e3d29a1b8aed034d3afa5c25f7fd66038f5",
    "q010_representation_cost": "2885a029ecfe2c17aebe3b05b305caebd927d78476971e4ab186455d0ee30b7f",
}
OMEGAS = (1.0, 1.2, 1.5, 1.8)


def _digest(value: Any) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _error(actual: np.ndarray, expected: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))


def _relative(actual: np.ndarray, expected: np.ndarray) -> float:
    return float(np.linalg.norm(actual - expected) / max(np.linalg.norm(expected), 1e-30))


def _all_pass(gates: dict[str, dict[str, Any]]) -> bool:
    return bool(gates) and all(g["passed"] is True for g in gates.values())


def prerequisite_decisions(artifacts: dict[str, Any]) -> dict[str, bool]:
    """Interpret scientific outcomes and individual gates, not just validity flags."""
    branch = artifacts["q004b_and_manufactured"]["cycles"]
    original = artifacts["q005_nonresonance"]["cycle"]
    family = artifacts["q006h_cluster_complete"]["cycle"]
    old_chart = artifacts["q006i_full2d_quadratic"]["cycle"]
    policy = artifacts["q006p_dual_reporting"]["cycle"]
    holdout = artifacts["q006q_forward_error_holdout"]["cycle"]
    shadow = artifacts["q007ap_forward_shadowing"]["cycle"]
    representation = artifacts["q011g_forced_representation_audit"]["cycle"]
    sparse = artifacts["q011h_sparse_chart_equivalence"]["cycle"]
    cost = artifacts["q010_representation_cost"]["cycle"]
    return {
        "branch_cluster_and_manufactured_oracle": (
            len(branch) == 2
            and all(c["outcome"] == "accepted" and _all_pass(c["gates"]) for c in branch)
        ),
        "original_isotropic_candidate_rejection_preserved": original["hypothesis_outcome"]
        == "rejected",
        "repaired_sector_aware_family": (
            family["hypothesis_outcome"] == "accepted"
            and family["selected_family"]["eta"] == 0.01
            and family["selected_family"]["omega"] == 1.5
            and _all_pass(family["selected_family"]["coefficient_gates"])
            and _all_pass(family["selected_family"]["spectral_gates"])
        ),
        "quadratic_fixed_leaf_policy_and_independent_holdout": (
            old_chart["hypothesis_outcome"] == "rejected"
            and policy["hypothesis_outcome"] == holdout["hypothesis_outcome"] == "accepted"
            and _all_pass(policy["policy_column"]["gates"])
            and _all_pass(holdout["holdout_policy_gates"])
        ),
        "registered_same_initial_repaired_mpfr_shadowing": (
            shadow["hypothesis_outcome"] == "accepted"
            and _all_pass(shadow["validity_gates"])
            and _all_pass(shadow["hypothesis_gates"])
            and shadow["theorem_consequence"][
                "same_initial_forward_coordinate_error_is_uniform_all_iterate"
            ]
            is True
        ),
        "representation_fidelity_and_sparse_multistep_equivalence": (
            representation["hypothesis_outcome"] == "rejected"
            and representation["hypothesis_gates"][
                "all_candidate_fidelity_and_residual_gates_pass"
            ]["passed"]
            is True
            and sparse["hypothesis_outcome"] == "accepted"
            and _all_pass(sparse["hypothesis_gates"])
        ),
        "tt_cross_branch_inapplicable_without_storage_winner": (
            representation["decision_consequence"]["selected_candidate_id"] is None
            and representation["decision_consequence"]["tt_cross_followup_is_authorized"] is False
            and sparse["decision_consequence"]["tt_cross_followup_is_authorized"] is False
        ),
        "finite_campaign_positivity_and_conservation": (
            policy["policy_column"]["gates"]["positive_populations"]["passed"] is True
            and policy["policy_column"]["gates"]["global_conservation"]["passed"] is True
            and sparse["hypothesis_gates"]["campaign_is_finite_positive_and_conservative"]["passed"]
            is True
        ),
        "sparse_baseline_cost_report": (
            cost["hypothesis_outcome"] == "accepted"
            and _all_pass(cost["hypothesis_gates"])
            and cost["decision_consequence"]["natural_sparse_fiber_remains_mandatory_baseline"]
            is True
        ),
    }


def audit_prerequisites(directory: Path = ARTIFACT_DIRECTORY) -> dict[str, Any]:
    artifacts, records = {}, {}
    for name, expected in INPUT_SEALS.items():
        path = directory / (name + ".json")
        artifact = json.loads(path.read_text(encoding="utf-8"))
        actual = _file_sha256(path)
        runner = artifact.get("runner_source")
        runner_match = None
        if runner is not None:
            runner_match = (
                _file_sha256(Path(__file__).resolve().parent / runner["filename"])
                == runner["sha256"]
            )
        records[name] = {
            "filename": path.name,
            "artifact_sha256": actual,
            "artifact_seal_matches": actual == expected,
            "runner_seal_matches": runner_match,
            "study_validity": artifact["study_gate"],
            "mathematical_scope": artifact["mathematical_scope"],
            "passed": actual == expected
            and runner_match is not False
            and artifact["study_gate"] == "passed",
        }
        artifacts[name] = artifact
    decisions = prerequisite_decisions(artifacts)
    source_match = source_metadata()["package_source_sha256"] == EXPECTED_PACKAGE_SOURCE
    return {
        "evidence_mode": "sealed stored results and current runner hashes; no historical trajectory rerun",
        "records": records,
        "decisions": decisions,
        "d2q9_package_fingerprint_matches": source_match,
        "passed": source_match
        and all(r["passed"] for r in records.values())
        and all(decisions.values()),
        "scope": "readiness for D3Q27 foundation only; no transfer of 2D theorems, radius or precision to 3D",
        "repaired_map_degrees_34_through_90_remain_open": True,
    }


def _gaussian_moment(power: int) -> Fraction:
    return Fraction(0) if power % 2 else Fraction(prod(range(1, power, 2)), 3 ** (power // 2))


def quadrature_audit() -> dict[str, Any]:
    records = []
    for powers in product(range(6), repeat=3):
        actual = sum(
            w * prod(int(c) ** p for c, p in zip(v, powers))
            for v, w in zip(d3.VELOCITIES, d3.EXACT_WEIGHTS)
        )
        expected = prod(_gaussian_moment(p) for p in powers)
        records.append(
            {
                "powers": list(powers),
                "actual": str(actual),
                "expected": str(expected),
                "passed": actual == expected,
            }
        )
    sixth = sum(w * int(v[0]) ** 6 for v, w in zip(d3.VELOCITIES, d3.EXACT_WEIGHTS))
    face_sixth = sum(
        w * Fraction(int(v[0] + v[1]) ** 6, 8) for v, w in zip(d3.VELOCITIES, d3.EXACT_WEIGHTS)
    )
    shell_counts = Counter(int(v @ v) for v in d3.VELOCITIES)
    shell_expected = {
        0: Fraction(8, 27),
        1: Fraction(2, 27),
        2: Fraction(1, 54),
        3: Fraction(1, 216),
    }
    descriptor_pass = (
        len(set(map(tuple, d3.VELOCITIES))) == 27
        and sum(d3.EXACT_WEIGHTS) == 1
        and min(d3.EXACT_WEIGHTS) > 0
        and shell_counts == {0: 1, 1: 6, 2: 12, 3: 8}
        and all(w == shell_expected[int(v @ v)] for v, w in zip(d3.VELOCITIES, d3.EXACT_WEIGHTS))
    )
    return {
        "monomial_count": len(records),
        "monomials": records,
        "velocity_count": len(d3.VELOCITIES),
        "descriptor_passed": descriptor_pass,
        "rank_two_and_four_isotropy_exact": all(
            r["passed"] for r in records if sum(r["powers"]) in (2, 4)
        ),
        "sixth_order_negative_control": {
            "axis_discrete": str(sixth),
            "axis_gaussian": "5/9",
            "mismatch_detected": sixth != Fraction(5, 9),
            "unit_face_diagonal_discrete": str(face_sixth),
            "axis_and_face_differ": sixth != face_sixth,
        },
        "passed": descriptor_pass and all(r["passed"] for r in records) and sixth == Fraction(1, 3),
    }


def moments_and_streaming_audit() -> dict[str, Any]:
    rng = np.random.default_rng(2026090701)
    shape = (3, 5, 7)
    rho, j = rng.uniform(0.98, 1.02, shape), rng.uniform(-0.01, 0.01, shape + (3,))
    f = d3.equilibrium(rho, j)
    measured_rho, measured_j = d3.macroscopic(f)
    pressure = np.einsum("...q,qi,qj->...ij", f, d3.VELOCITIES, d3.VELOCITIES)
    expected = (
        rho[..., None, None] * np.eye(3) / 3
        + np.einsum("...i,...j->...ij", j, j) / rho[..., None, None]
    )
    errors = {
        "density": _error(measured_rho, rho),
        "momentum": _error(measured_j, j),
        "pressure": _error(pressure, expected),
    }
    impulses = []
    for q, velocity in enumerate(d3.VELOCITIES):
        source = np.zeros(shape + (27,))
        source[1, 2, 3, q] = q + 1
        expected_state = np.zeros_like(source)
        destination = (np.array((1, 2, 3)) + velocity[::-1]) % shape
        expected_state[tuple(destination) + (q,)] = q + 1
        impulses.append(bool(np.array_equal(d3.stream_periodic(source), expected_state)))
    random_state = rng.standard_normal(shape + (27,))
    streaming_bijection = np.array_equal(
        np.sort(random_state.reshape(-1, 27), axis=0),
        np.sort(d3.stream_periodic(random_state).reshape(-1, 27), axis=0),
    )
    return {
        "moment_errors": errors,
        "impulse_count": 27,
        "impulse_passes": impulses,
        "streaming_population_multisets_unchanged": bool(streaming_bijection),
        "passed": max(errors.values()) <= 5e-15 and all(impulses) and bool(streaming_bijection),
    }


def conservation_audit() -> dict[str, Any]:
    rng = np.random.default_rng(2026090702)
    records = []
    for size, omega, direction in product((3, 5), OMEGAS, range(2)):
        delta = d3.project_to_fixed_leaf(1e-4 * rng.standard_normal((size, size, size, 27)))
        projection_error = max(
            _error(d3.project_to_fixed_leaf(delta), delta),
            float(np.max(np.abs(d3.global_conserved_quantities(delta)))),
        )
        state = d3.uniform_equilibrium((size, size, size), np.zeros(4)) + delta
        initial = d3.global_conserved_quantities(state)
        min_population, max_drift = float(state.min()), 0.0
        for _ in range(32):
            state = d3.bgk_periodic_step(state, omega)
            min_population = min(min_population, float(state.min()))
            max_drift = max(
                max_drift, _error(d3.global_conserved_quantities(state), initial) / size**3
            )
        records.append(
            {
                "size": size,
                "omega": omega,
                "direction": direction,
                "steps": 32,
                "maximum_per_site_conservation_drift": max_drift,
                "minimum_population": min_population,
                "projection_error": projection_error,
                "passed": max_drift <= 2e-13 and min_population > 0 and projection_error <= 5e-14,
            }
        )
    return {
        "trajectory_count": len(records),
        "step_count": 32 * len(records),
        "records": records,
        "passed": all(r["passed"] for r in records),
    }


def lift_audit() -> dict[str, Any]:
    rng = np.random.default_rng(2026090703)
    initial = d2.uniform_equilibrium(5, 7, (0.01, 0.003, -0.002)) + 1e-4 * rng.standard_normal(
        (5, 7, 9)
    )
    records = []
    for nz, omega in product((1, 3, 5), OMEGAS):
        f2, f3 = initial.copy(), d3.lift_d2q9(initial, nz)
        stage_error = max(
            _error(d3.collide_bgk(f3, omega), d3.lift_d2q9(d2.collide_bgk(f2, omega), nz)),
            _error(d3.stream_periodic(f3), d3.lift_d2q9(d2.stream_periodic(f2), nz)),
        )
        rho2, j2 = d2.macroscopic(f2)
        rho3, j3 = d3.macroscopic(f3)
        moment_error = max(
            _error(rho3, rho2), _error(j3[..., :2], j2), _error(j3[..., 2], np.zeros_like(rho3))
        )
        maximum_error = _error(d3.d2q9_marginal(f3), initial)
        for _ in range(16):
            f2, f3 = d2.bgk_periodic_step(f2, omega), d3.bgk_periodic_step(f3, omega)
            maximum_error = max(
                maximum_error, _error(f3, d3.lift_d2q9(f2, nz)), _error(d3.d2q9_marginal(f3), f2)
            )
        records.append(
            {
                "nz": nz,
                "omega": omega,
                "steps": 16,
                "stage_error": stage_error,
                "moment_error": moment_error,
                "maximum_rollout_and_marginal_error": maximum_error,
                "passed": max(stage_error, moment_error, maximum_error) <= 2e-14,
            }
        )
    matrix = d3.d2q9_lift_matrix()
    symbols = [
        _error(
            d3.fourier_symbol((kx, ky, 0), omega) @ matrix,
            matrix @ d2.fourier_symbol(kx, ky, omega),
        )
        for kx, ky in ((0, 0), (0.37, -0.22), (np.pi, 0))
        for omega in OMEGAS
    ]
    wrong = np.zeros_like(matrix)
    wrong[d3.VELOCITIES[:, 2] == 0] = matrix[d3.VELOCITIES[:, 2] == 0] * 1.5
    wrong_state = np.einsum("qr,...r->...q", wrong, initial)[None, ...]
    wrong_error = _error(
        d3.bgk_periodic_step(wrong_state, 1.2),
        np.einsum("qr,...r->...q", wrong, d2.bgk_periodic_step(initial, 1.2))[None, ...],
    )
    return {
        "trajectory_count": len(records),
        "records": records,
        "symbol_errors": symbols,
        "wrong_z_weight_intertwining_error": wrong_error,
        "passed": all(r["passed"] for r in records)
        and max(symbols) <= 2e-14
        and wrong_error > 1e-4,
    }


def symmetry_audit() -> dict[str, Any]:
    rng = np.random.default_rng(2026090701)
    state = d3.uniform_equilibrium(
        (3, 3, 3), (0.01, 0.004, -0.003, 0.002)
    ) + 1e-4 * rng.standard_normal((3, 3, 3, 27))
    k = np.array((0.31, -0.27, 0.19))
    records = []
    for rotation in d3.cubic_symmetries():
        p = d3.population_permutation(rotation)
        closure = np.array_equal(p @ d3.VELOCITIES, d3.VELOCITIES @ rotation) and np.array_equal(
            p @ d3.WEIGHTS, d3.WEIGHTS
        )
        symbol_error = max(
            _error(p @ d3.fourier_symbol(k, o) @ p.T, d3.fourier_symbol(rotation @ k, o))
            for o in OMEGAS
        )
        step_error = max(
            _error(
                d3.rotate_periodic_state(d3.bgk_periodic_step(state, o), rotation),
                d3.bgk_periodic_step(d3.rotate_periodic_state(state, rotation), o),
            )
            for o in OMEGAS
        )
        records.append(
            {
                "rotation": rotation.tolist(),
                "determinant": round(float(np.linalg.det(rotation))),
                "closure_exact": bool(closure),
                "symbol_error": symbol_error,
                "step_error": step_error,
                "passed": bool(closure) and max(symbol_error, step_error) <= 2e-14,
            }
        )
    return {
        "symmetry_count": len(records),
        "proper_rotation_count": sum(r["determinant"] == 1 for r in records),
        "records": records,
        "passed": all(r["passed"] for r in records),
    }


def linearization_audit() -> dict[str, Any]:
    rng = np.random.default_rng(2026090704)
    base = d3.uniform_equilibrium((3, 3, 3), np.zeros(4))
    delta = rng.standard_normal(base.shape)
    steps = (1e-4, 5e-5, 2.5e-5)
    records = []
    for omega in (1.2, 1.5):
        exact = d3.linearized_periodic_step(delta, omega)
        fd_errors = [
            _relative(
                (
                    d3.bgk_periodic_step(base + h * delta, omega)
                    - d3.bgk_periodic_step(base - h * delta, omega)
                )
                / (2 * h),
                exact,
            )
            for h in steps
        ]
        ratios = [fd_errors[i] / fd_errors[i + 1] for i in range(2)]
        transformed = np.fft.fftn(delta, axes=(0, 1, 2))
        advanced = np.empty_like(transformed)
        k = 2 * np.pi * np.fft.fftfreq(3)
        for iz, iy, ix in product(range(3), repeat=3):
            advanced[iz, iy, ix] = (
                d3.fourier_symbol((k[ix], k[iy], k[iz]), omega) @ transformed[iz, iy, ix]
            )
        fft_error = _relative(np.fft.ifftn(advanced, axes=(0, 1, 2)), exact)
        collision = d3.collision_symbol(omega)
        e, m = d3.equilibrium_tangent_matrix(), d3.conserved_moment_matrix()
        algebra_error = max(
            _error(m @ e, np.eye(4)),
            _error(collision @ e, e),
            _error(m @ collision, m),
            _error(collision @ (np.eye(27) - e @ m), (1 - omega) * (np.eye(27) - e @ m)),
        )
        records.append(
            {
                "omega": omega,
                "fd_steps": list(steps),
                "fd_relative_errors": fd_errors,
                "error_halving_ratios": ratios,
                "fft_symbol_relative_error": fft_error,
                "four_conserved_and_twenty_three_kinetic_algebra_error": algebra_error,
                "passed": fd_errors[-1] <= 1e-7
                and all(3.5 <= r <= 4.5 for r in ratios)
                and fft_error <= 2e-14
                and algebra_error <= 2e-14,
            }
        )
    return {"records": records, "passed": all(r["passed"] for r in records)}


def center_oracle_audit() -> dict[str, Any]:
    omega = 1.2
    e, m, analytic = (
        d3.equilibrium_tangent_matrix(),
        d3.conserved_moment_matrix(),
        d3.equilibrium_hessian_at_rest(),
    )
    hessian, reduced, diagnostics = solve_identity_center_quadratic(
        d3.collision_symbol(omega), e, m, omega * analytic
    )
    fd_bilinear = second_derivative_tensor(
        lambda f: d3.collide_bgk(f.reshape(1, 1, 1, 27), omega).ravel(), d3.WEIGHTS, e
    )
    hessian_error = _relative(hessian, analytic)
    derivative_error = _relative(fd_bilinear, omega * analytic)
    shape, sites = (3, 3, 3), 27
    base = d3.uniform_equilibrium(shape, np.zeros(4)).ravel()
    tangent, extractor = d3.uniform_center_basis(shape)
    linear = QuadraticChart(base, tangent, np.zeros((base.size, 4, 4)))
    quadratic = QuadraticChart(base, tangent, np.tile(hessian, (sites, 1, 1)))
    rng = np.random.default_rng(2026090705)
    directions = []
    while len(directions) < 32:
        a = rng.standard_normal(4)
        a /= np.linalg.norm(a)
        if abs(a[0]) >= 0.1 and np.linalg.norm(a[1:]) >= 0.1:
            directions.append(a)
    amplitudes = np.array((1e-2, 5e-3, 2.5e-3, 1.25e-3))
    records = []
    for direction in directions:
        defects = []
        for chart in (linear, quadratic):
            values = []
            for a in amplitudes[:, None] * direction:
                state = chart.evaluate(a).reshape(shape + (27,))
                values.append(float(np.linalg.norm(d3.bgk_periodic_step(state, omega) - state)))
            defects.append(values)
        slopes = [float(np.polyfit(np.log(amplitudes), np.log(values), 1)[0]) for values in defects]
        records.append(
            {
                "direction": direction.tolist(),
                "linear_defects": defects[0],
                "quadratic_defects": defects[1],
                "linear_slope": slopes[0],
                "quadratic_slope": slopes[1],
                "passed": 1.9 <= slopes[0] <= 2.1 and 2.9 <= slopes[1] <= 3.1,
            }
        )
    reduced_norm = float(np.linalg.norm(reduced))
    exact_state = d3.uniform_equilibrium(shape, (0.02, 0.01, -0.012, 0.008))
    fixed_family_error = _error(d3.bgk_periodic_step(exact_state, omega), exact_state)
    return {
        "scope": "homogeneous four-coordinate invariant family only; no nonzero-wave chart or full-grid unit-circle classification",
        "hessian_relative_error": hessian_error,
        "independent_fd_second_derivative_error": derivative_error,
        "reduced_hessian_norm": reduced_norm,
        "homological_diagnostics": asdict(diagnostics),
        "fixed_family_error": fixed_family_error,
        "coordinate_gauge_error": _error(extractor @ tangent, np.eye(4)),
        "direction_count": len(records),
        "amplitudes": amplitudes.tolist(),
        "records": records,
        "passed": hessian_error <= 1e-12
        and reduced_norm <= 1e-12
        and derivative_error <= 5e-7
        and diagnostics.global_equation_relative_residual <= 1e-12
        and diagnostics.maximum_gauge_residual <= 1e-12
        and _error(extractor @ tangent, np.eye(4)) <= 1e-12
        and fixed_family_error <= 2e-14
        and all(r["passed"] for r in records),
    }


def run_study() -> dict[str, Any]:
    prerequisites = audit_prerequisites()
    if prerequisites["passed"]:
        audits = {
            "quadrature": quadrature_audit(),
            "moments_and_streaming": moments_and_streaming_audit(),
            "conservation": conservation_audit(),
            "d2q9_lift": lift_audit(),
            "cubic_symmetry": symmetry_audit(),
            "linearization": linearization_audit(),
            "center_oracle": center_oracle_audit(),
        }
    else:
        audits = {}
    coverage = bool(audits) and (
        audits["quadrature"]["monomial_count"] == 216
        and audits["moments_and_streaming"]["impulse_count"] == 27
        and audits["conservation"]["trajectory_count"] == 16
        and audits["conservation"]["step_count"] == 512
        and audits["d2q9_lift"]["trajectory_count"] == 12
        and audits["cubic_symmetry"]["symmetry_count"] == 48
        and audits["cubic_symmetry"]["proper_rotation_count"] == 24
        and len(audits["linearization"]["records"]) == 2
        and audits["center_oracle"]["direction_count"] == 32
    )
    validity_gates = {
        "prerequisites": prerequisites["passed"],
        "registered_coverage": coverage,
        "finite_numeric_evidence": _all_numeric_values_finite(audits),
    }
    validity = all(validity_gates.values())
    outcome = (
        "inconclusive"
        if not validity
        else "accepted"
        if all(a["passed"] for a in audits.values())
        else "rejected"
    )
    cycle = {
        "question": "Does tensor-product D3Q27 preserve quadrature, cubic symmetry, the D2Q9 lift and the local center oracle?",
        "prerequisites": prerequisites,
        "audits": audits,
        "validity_gates": validity_gates,
        "study_validity": "passed" if validity else "failed",
        "scientific_outcome": outcome,
        "failed_audits": [name for name, a in audits.items() if not a["passed"]],
        "claim_boundary": "periodic unforced D3Q27 algebra and registered binary64 oracle tests; no nonzero-mode manifold or 3D SSM theorem",
        "next_question": "Q012b: track the four-dimensional low-wave cluster, its two-dimensional shear part and odd/even Nyquist obstruction"
        if outcome == "accepted"
        else "Diagnose the first failed Q012a gate before 3D branch tracking",
    }
    cycle["result_digest_sha256"] = _digest(cycle)
    runner = Path(__file__).resolve()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "runner_source": {"filename": runner.name, "sha256": _file_sha256(runner)},
        "helper_source": {
            "filename": Path(d3.__file__).name,
            "sha256": _file_sha256(Path(d3.__file__)),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_study()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "study_gate": result["study_gate"],
                "scientific_outcome": result["scientific_outcome"],
                "failed_audits": result["cycle"]["failed_audits"],
            }
        )
    )
    if result["scientific_outcome"] != "accepted":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
