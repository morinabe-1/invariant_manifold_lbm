"""Full-entry Q012h1 records, with independent reference arithmetic.

Main derivative/product imports are local to main functions. The reference
route never calls them, even when it checks rounded numerical witnesses.
"""

from fractions import Fraction
from itertools import combinations_with_replacement, product
from math import sqrt

import numpy as np

from research import d3q27_cubic_precision as precision
from research import d3q27_exact_residual as exact
from research import d3q27_quartic_fraction as fraction
from research import d3q27_quartic_reference as reference

METHODS = ("svd", "sylvester", "refined")
GROUP_NAMES = (
    "B_V_H3",
    "B_H2_H2",
    "C_V_V_H2",
    "D_V4",
    "minus_H2_L_G3",
    "minus_H2_G2_G2",
    "minus_H3_L_L_G2",
)
OPERATOR_CASES = tuple(
    (dims, groups, p)
    for dims in product((1, 2), repeat=4)
    for groups in combinations_with_replacement(range(4), 4)
    for p in (23, 27)
)
FORCING_CASES = ((23, "real"), (23, "complex"), (27, "real"), (27, "complex"))


def scaled_error(value, target):
    return float(np.linalg.norm(np.asarray(value) - target) / max(1, np.linalg.norm(target)))


def main_operator(case):
    from research import d3q27_quartic_operator as operator
    from research import d3q27_quartic_solve as solve

    dims, groups, p = case
    record, arrays = solve.solve_known(dims, groups, p)
    value = operator.build_product(dims, groups)
    arrays.update(
        {
            "orbit_basis": value.basis,
            "full_input_dynamics": value.full_dynamics,
            "taylor_factors": value.factors,
            "orbit_multiplicities": value.multiplicities,
            "raw_coordinates": np.asarray(value.full_coordinates, dtype=np.int64),
            "homological_operator": solve.fallback.q.homological_operator(arrays["a"], arrays["d"]),
        }
    )
    return record, arrays


def reference_matrix(a, d):
    """Assemble AX-XD entry by entry, without the Kronecker kernel."""
    p, q = len(a), len(d)
    matrix = np.zeros((p * q, p * q), dtype=complex)
    for column in range(q):
        for row in range(p):
            for k in range(p):
                matrix[row + p * column, k + p * column] += a[row, k]
            for k in range(q):
                matrix[row + p * column, row + p * k] -= d[k, column]
    return matrix


def reference_svd(a, d, f):
    p, q = f.shape
    matrix = reference_matrix(a, d)
    u, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    threshold = 100 * np.finfo(float).eps * (p * q) * singular[0]
    keep = singular > threshold
    null = float(np.linalg.norm(u[:, ~keep].conj().T @ f.reshape(-1, order="F")))
    condition = float(singular[0] / singular[-1]) if np.all(keep) else None
    status = (
        ("nonsingular_practical" if condition <= 1e8 else "nonsingular_ill_conditioned")
        if condition is not None
        else (
            "singular_compatible"
            if null <= 1e-10 * max(1, np.linalg.norm(f))
            else "singular_incompatible"
        )
    )
    return {
        "operator_dimension": p * q,
        "numerical_rank": int(np.count_nonzero(keep)),
        "rank_threshold": float(threshold),
        "smallest_singular_value": float(singular[-1]),
        "largest_singular_value": float(singular[0]),
        "condition_number": condition,
        "left_null_forcing_norm": null,
        "status": status,
    }


def witness(a, d, f, x, low, high):
    recalculated_low = a @ x - x @ d + f
    recalculated_high = precision.residual_mpc(a, d, f, x)
    proof = exact.audit_gmp(
        a, d, f, x, recalculated_low, recalculated_high, max(1e-14, float(np.linalg.norm(f)))
    )
    return {
        "proof": proof,
        "saved_r64_equal": bool(np.array_equal(low, recalculated_low)),
        "saved_r128_equal": bool(np.array_equal(high, recalculated_high)),
        "full_1e9_passed": exact.rational(proof["norms_squared"]["exact_residual_norm_squared"])
        * 10**18
        <= exact.rational(proof["decimal_denominator_squared"]),
    }


def reference_operator(case, arrays):
    dims, groups, p = case
    value = reference.substitute(dims, groups)
    a, d, f = (arrays[name] for name in ("a", "d", "f"))
    q = len(value["keys"])
    known = (np.arange(p)[:, None] + 1) / 32 + 1j * (np.arange(q)[None, :] + 1) / 32
    reference_a = np.asarray(
        [
            [
                float(-Fraction(1, 5) - Fraction(i, 10 * p))
                if i == k
                else float(Fraction(1, 100))
                if k == i + 1
                else 0
                for k in range(p)
            ]
            for i in range(p)
        ],
        dtype=complex,
    )
    m = sum(dims)
    full = np.zeros((m + p + 4, m + p + 4), dtype=complex)
    offset = 0
    for b, size in enumerate(dims):
        full[offset : offset + size, offset : offset + size] = np.asarray(
            reference.matrix(b, size), dtype=complex
        )
        offset += size
    full[m : m + p, m : m + p], full[-4:, -4:] = a, np.eye(4)
    full_f = np.vstack((np.zeros((m, q)), f, np.zeros((4, q))))
    methods = {}
    for method in METHODS:
        x = arrays[method]
        full_x = np.vstack((np.zeros((m, q)), x, np.zeros((4, q))))
        methods[method] = {
            "known_error": scaled_error(x, known),
            "graph_embedding_equal": bool(np.array_equal(full_x, arrays[method + "_full"])),
            "external": witness(a, d, f, x, arrays[method + "_r64"], arrays[method + "_r128"]),
            "full": witness(
                arrays["full_a"],
                d,
                arrays["full_f"],
                arrays[method + "_full"],
                arrays[method + "_full_r64"],
                arrays[method + "_full_r128"],
            ),
        }
    return {
        "dimensions": list(dims),
        "groups": list(groups),
        "external_dimension": p,
        "coordinate_keys": [list(key) for key in value["keys"]],
        "exact_substitution": [
            [[str(v.numerator), str(v.denominator)] for v in row] for row in value["coefficients"]
        ],
        "normalized_dynamics": value["normalized"],
        "multiplicities": list(value["multiplicities"]),
        "taylor_denominators": list(value["taylor_denominators"]),
        "input_errors": {
            "homological_operator": scaled_error(
                arrays["homological_operator"], reference_matrix(a, d)
            ),
            "a": scaled_error(a, reference_a),
            "d": scaled_error(d, value["normalized"]),
            "full_a": scaled_error(arrays["full_a"], full),
            "known": scaled_error(arrays["known"], known),
            "f": scaled_error(f, known @ d - a @ known),
            "full_f": scaled_error(arrays["full_f"], full_f),
        },
        "svd": reference_svd(a, d, f),
        "methods": methods,
    }


def main_forcing(case):
    from research import d3q27_quartic_jets as jets

    p, representation = case
    model = jets.Manufactured(p, representation)

    def encode(vector):
        return [v.record() for v in vector]

    known, conjugate_ok, lower_conservation = {}, True, True
    for degree in (2, 3, 4):
        keys = tuple(combinations_with_replacement(range(8), degree))
        h, g = [], []
        for key in keys:
            directions = tuple(model.units[i] for i in key)
            hh, gg = model.h(directions), model.g(directions)
            lower_conservation &= not any((*hh[:8], *hh[-4:]))
            h.append(encode(hh))
            g.append(encode(gg))
            if representation == "complex":
                partner = tuple(model.units[i ^ 1] for i in key)
                partner_g = model.g(partner)
                conjugate_ok &= model.h(partner) == tuple(v.conjugate() for v in hh)
                conjugate_ok &= tuple(partner_g[i ^ 1] for i in range(8)) == tuple(
                    v.conjugate() for v in gg
                )
            else:
                conjugate_ok &= all(not v.imag for v in (*hh, *gg))
        known[str(degree)] = {"keys": [list(k) for k in keys], "h": h, "g": g}
    columns, expected, terms = [], [], {name: [] for name in GROUP_NAMES}
    norms = dict.fromkeys(GROUP_NAMES, Fraction(0))
    omissions, conjugations = dict.fromkeys(GROUP_NAMES, 0), dict.fromkeys(GROUP_NAMES, 0)
    mutation_counts = {"composition_sign": 0, "omit_G2": 0, "omit_G3": 0}
    identity, gauge, conservation = True, True, lower_conservation
    forcing_by_key = {}
    for key in combinations_with_replacement(range(8), 4):
        groups = model.forcing_groups(key)
        actual = jets.add(*groups.values())
        forcing_by_key[key] = actual
        hh, gg, target = model.known_identity(key)
        columns.append(encode(actual))
        expected.append(encode(target))
        identity &= actual == target
        gauge &= jets.matvec(model.inverse, actual[:8]) == gg
        conservation &= not any((*actual[-4:], *hh[:8], *hh[-4:]))
        for name, vector in groups.items():
            terms[name].append(encode(vector))
            norms[name] += sum((Fraction(v.real**2 + v.imag**2) for v in vector), Fraction(0))
            omissions[name] += int(any(vector))
            conjugations[name] += int(any(v.imag for v in vector))
        mutation_counts["composition_sign"] += int(
            any(jets.add(*(v for name, v in groups.items() if name.startswith("minus_"))))
        )
        mutation_counts["omit_G2"] += int(
            any(jets.add(groups["minus_H2_G2_G2"], groups["minus_H3_L_L_G2"]))
        )
        mutation_counts["omit_G3"] += int(any(groups["minus_H2_L_G3"]))
    left_inverse = all(
        jets.matvec(model.inverse, jets.matvec(model.transform, e)) == e for e in model.units
    )
    forcing_conjugacy = all(
        forcing_by_key[tuple(sorted(i ^ 1 for i in key))] == tuple(v.conjugate() for v in vector)
        if representation == "complex"
        else all(not v.imag for v in vector)
        for key, vector in forcing_by_key.items()
    )
    return {
        "external_dimension": p,
        "representation": representation,
        "transform": [encode(row) for row in model.transform],
        "inverse": [encode(row) for row in model.inverse],
        "known": known,
        "forcing": {"keys": known["4"]["keys"], "columns": columns},
        "identity_forcing": expected,
        "groups": terms,
        "group_norms_squared": {
            k: [str(v.numerator), str(v.denominator)] for k, v in norms.items()
        },
        "group_float_norms": {k: sqrt(float(v)) for k, v in norms.items()},
        "controls": {
            "identity": identity,
            "gauge": gauge,
            "conservation": conservation,
            "left_inverse": left_inverse,
            "conjugacy": conjugate_ok,
            "forcing_conjugacy": forcing_conjugacy,
            "group_omission_counts": omissions,
            "group_conjugation_counts": conjugations,
            "mutation_counts": mutation_counts,
        },
    }


def reference_forcing(case):
    data = fraction.manufactured(*case)

    def encode(vector):
        return [fraction.record(v) for v in vector]

    return {
        "external_dimension": data["external_dimension"],
        "representation": data["representation"],
        "transform": [encode(row) for row in data["transform"]],
        "inverse": [encode(row) for row in data["inverse"]],
        "known": {
            str(degree): {
                "keys": [list(k) for k in values["h"][0]],
                "h": [encode(v) for v in values["h"][1]],
                "g": [encode(v) for v in values["g"][1]],
            }
            for degree, values in data["known"].items()
        },
        "forcing": {
            "keys": [list(k) for k in data["forcing"][0]],
            "columns": [encode(v) for v in data["forcing"][1]],
        },
        "known_graph_identity": data["known_graph_identity"],
        "full_coefficient_realification": data["full_coefficient_realification"],
    }


def reference_negatives():
    return [
        reference_svd(np.diag([0.5 + gap, 0.125]), np.array([[0.5]]), np.asarray(f))
        for gap, f in ((0.0, [[0.0], [1.0]]), (0.0, [[1.0], [0.0]]), (2**-36, [[1.0], [1.0]]))
    ]


def compare_operator(main, arrays, worker):
    from research import q012h0_d3q27_quartic_census as census

    identity = all(
        census.same(main[name], worker[name])
        for name in ("dimensions", "groups", "external_dimension", "coordinate_keys")
    )
    multiplicities = census.same(arrays["orbit_multiplicities"].tolist(), worker["multiplicities"])
    taylor = np.ones(len(arrays["orbit_basis"])) @ arrays["orbit_basis"] * arrays["taylor_factors"]
    expected = np.asarray([1 / n for n in worker["taylor_denominators"]])
    taylor_error = scaled_error(taylor, expected)
    diagnostics_equal = all(
        census.same(main["svd_diagnosis"][key], value)
        if type(value) is not float
        else abs(main["svd_diagnosis"][key] - value) <= 5e-12 * max(1, abs(value))
        for key, value in worker["svd"].items()
    )
    witness_equal, solved = True, True
    for method in METHODS:
        checked, previous = worker["methods"][method], main["methods"][method]
        witness_equal &= checked["graph_embedding_equal"]
        for part in ("external", "full"):
            witness_equal &= census.same(checked[part]["proof"], previous["exact_" + part])
            witness_equal &= checked[part]["saved_r64_equal"] and checked[part]["saved_r128_equal"]
        if method in ("svd", "refined"):
            solved &= checked["known_error"] <= 1e-10 and checked["full"]["full_1e9_passed"]
            solved &= all(checked["external"]["proof"]["gates"][name] for name in exact.EXACT_GATES)
    return {
        "identity_equal": identity,
        "independent_witnesses_equal": bool(witness_equal),
        "diagnostics_equal": diagnostics_equal,
        "taylor_scaled_error": taylor_error,
        "uniform_1_over_24_detected": scaled_error(
            np.ones(len(arrays["orbit_basis"])) @ arrays["orbit_basis"] / 24, expected
        )
        > 5e-12,
        "H1": identity
        and multiplicities
        and taylor_error <= 5e-12
        and all(v <= 5e-12 for v in worker["input_errors"].values())
        and main["structural"]["passed"],
        "H3": bool(solved)
        and main["passed"]
        and diagnostics_equal
        and worker["svd"]["status"] == "nonsingular_practical",
    }


def compare_forcing(main, worker):
    from research import q012h0_d3q27_quartic_census as census

    fields = ("external_dimension", "representation", "transform", "inverse", "known", "forcing")
    compared = {key: census.same(main[key], worker[key]) for key in fields}
    controls = main["controls"]
    covered = set(main["groups"]) == set(GROUP_NAMES) and all(
        controls["group_omission_counts"][name] > 0
        and Fraction(*map(int, main["group_norms_squared"][name])) > 0
        for name in GROUP_NAMES
    )
    covered &= all(value > 0 for value in controls["mutation_counts"].values())
    if main["representation"] == "complex":
        covered &= all(controls["group_conjugation_counts"][name] > 0 for name in GROUP_NAMES)
    return {
        "all_coefficients_equal": compared,
        "nonzero_and_mutation_coverage": covered,
        "H2": all(compared.values())
        and covered
        and all(
            controls[name] is True
            for name in (
                "identity",
                "gauge",
                "conservation",
                "left_inverse",
                "conjugacy",
                "forcing_conjugacy",
            )
        )
        and worker["known_graph_identity"]
        and worker["full_coefficient_realification"],
    }
