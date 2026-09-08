"""Q012h1 known-solution controls using the existing, unmodified solvers."""

import numpy as np
from scipy.linalg import block_diag

from research import d3q27_cubic_precision as precision
from research import d3q27_exact_residual as exact
from research import d3q27_quartic_operator as products
from research import d3q27_svd_fallback as fallback


def error(value, reference):
    return float(np.linalg.norm(value - reference) / max(1, np.linalg.norm(reference)))


def residual_evidence(a, d, f, x):
    low = a @ x - x @ d + f
    high = precision.residual_mpc(a, d, f, x)
    denominator = max(1e-14, float(np.linalg.norm(f)))
    integer = exact.audit_integer(a, d, f, x, low, high, denominator)
    rational = exact.audit_gmp(a, d, f, x, low, high, denominator)
    if integer != rational:
        raise ValueError("independent exact residual implementations disagree")
    return integer, low, high


def full_residual_passed(proof):
    """The registered full-equation bound is 1e-9, not the external 1e-10."""
    squared = exact.rational(proof["norms_squared"]["exact_residual_norm_squared"])
    denominator = exact.rational(proof["decimal_denominator_squared"])
    return squared * 10**18 <= denominator


def solve_known(dimensions, groups, external):
    product, a, f, known = products.known_problem(dimensions, groups, external)
    d = product.dynamics
    structural = products.structural_audit(product)
    svd, diagnosis, backend = fallback.solve_with_fallback(a, d, f)
    sylvester, refinement = precision.structured_solutions(a, d, f)
    m = sum(product.dimensions)
    full_a = block_diag(
        *(products.dynamics(b, s) for b, s in enumerate(product.dimensions)), a, np.eye(4)
    )
    full_f = np.vstack((np.zeros((m, len(d))), f, np.zeros((4, len(d)))))
    values = {"svd": svd, **sylvester}
    records, arrays = (
        {},
        {"a": a, "d": d, "f": f, "known": known, "full_a": full_a, "full_f": full_f},
    )
    for method, x in values.items():
        proof, low, high = residual_evidence(a, d, f, x)
        full_x = np.vstack((np.zeros((m, len(d))), x, np.zeros((4, len(d)))))
        full_proof, full_low, full_high = residual_evidence(full_a, d, full_f, full_x)
        # The manufactured graph embedding has zero selected and conserved
        # components; no tiny numerical values are projected away here.
        gauge = float(np.linalg.norm(full_x[:m]))
        conservation = float(np.linalg.norm(full_x[-4:]) + np.linalg.norm(full_f[-4:]))
        known_error = error(x, known)
        records[method] = {
            "known_solution_scaled_error": known_error,
            "graph_gauge_error": gauge,
            "conserved_components_error": conservation,
            "exact_external": proof,
            "exact_full": full_proof,
            "full_relative_tolerance": "1e-9",
            "full_residual_passed": full_residual_passed(full_proof),
            "passed": known_error <= 1e-10
            and gauge <= 5e-12
            and conservation <= 5e-12
            and all(proof["gates"][name] for name in exact.EXACT_GATES)
            and full_residual_passed(full_proof),
        }
        arrays.update(
            {
                method: x,
                method + "_r64": low,
                method + "_r128": high,
                method + "_full": full_x,
                method + "_full_r64": full_low,
                method + "_full_r128": full_high,
            }
        )
    return {
        "dimensions": list(product.dimensions),
        "groups": list(product.groups),
        "external_dimension": external,
        "coordinate_keys": [list(key) for key in product.keys],
        "structural": structural,
        "svd_diagnosis": diagnosis,
        "backend": backend,
        "refinement_history": refinement,
        "methods": records,
        "passed": structural["passed"]
        and backend["passed"]
        and diagnosis["status"] == "nonsingular_practical"
        and len(refinement) == 4
        and records["svd"]["passed"]
        and records["refined"]["passed"],
        "initial_sylvester_is_diagnostic_only": True,
    }, arrays


def negative_controls():
    records = []
    for expected, gap, f in (
        ("singular_compatible", 0.0, [[0.0], [1.0]]),
        ("singular_incompatible", 0.0, [[1.0], [0.0]]),
        ("nonsingular_ill_conditioned", 2**-36, [[1.0], [1.0]]),
    ):
        a, d, f = np.diag([0.5 + gap, 0.125]), np.array([[0.5]]), np.asarray(f)
        x, observed, backend = fallback.solve_with_fallback(a, d, f)
        records.append(
            {
                "expected": expected,
                "gap": gap,
                "forcing": f.tolist(),
                "response_real": x.real.tolist(),
                "response_imag": x.imag.tolist(),
                "observed": observed,
                "backend": backend,
                "passed": observed["status"] == expected
                and not observed["passed"]
                and backend["passed"],
            }
        )
    return {"cases": records, "passed": all(row["passed"] for row in records)}
