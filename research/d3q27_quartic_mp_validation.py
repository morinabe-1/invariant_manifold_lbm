"""Full-entry Q012h2a persistence validation and unchanged per-column decisions."""

import gmpy2 as mp
import numpy as np

from research import d3q27_quartic_mp as primary
from research import d3q27_quartic_mp_numbers as numbers
from research import d3q27_quartic_mp_reference as reference
from research import q012h2_d3q27_quartic_forcing as parent

require, same = parent.require, parent.same
COMPONENTS = ("forcing", "collision", "composition")


def payload(data, group, blocks, route, mutations=()):
    require(route in ("primary", "worker"), "registered precision route required")
    require(not mutations or route == "primary", "mutations belong to the primary route")
    require(
        len(set(mutations)) == len(mutations) and set(mutations) <= set(parent.primary.MUTATIONS),
        "registered unique mutations required",
    )
    if route == "primary":
        keys = parent.primary.block_product(data, group, blocks).keys
    else:
        keys = tuple(ids for ids, _ in reference.columns(group, blocks, data.dimension))
    document = {"group": list(group), "precision": {}, "mutations": {}}
    arrays = {"keys": np.asarray(keys, dtype=np.int64)}
    for bits in numbers.PRECISIONS:
        values = (primary if route == "primary" else reference).group(data, group, blocks, bits)
        document["precision"][str(bits)] = {
            name: numbers.encode(value, bits) for name, value in values.items()
        }
        arrays.update(
            {f"rounded{bits}_{name}": numbers.rounded(value) for name, value in values.items()}
        )
    if route == "primary":
        arrays.update(
            {
                f"moment_{name}": value
                for name, value in primary.moment_group(data, group, blocks).items()
            }
        )
        for mutation in mutations:
            wrong = primary.group(data, group, blocks, 192, mutation=mutation)["forcing"]
            document["mutations"][mutation] = numbers.encode(wrong, 192)
            arrays[f"without_{mutation}"] = numbers.rounded(wrong)
    return document, arrays


def validate_payload(document, arrays, group, blocks, dimension, route, mutations=()):
    """Exact schema, canonical values, every column, and all algebraic identities."""
    require(route in ("primary", "worker"), "registered precision route required")
    require(
        set(document) == {"group", "precision", "mutations"} and same(document["group"], group),
        "saved group/schema differs",
    )
    require(set(document["precision"]) == {"128", "192"}, "both precisions required")
    require(set(document["mutations"]) == set(mutations), "old observable mutation cases differ")
    keys = np.asarray(
        [ids for ids, _ in reference.columns(group, blocks, dimension)], dtype=np.int64
    )
    require(np.array_equal(arrays["keys"], keys), "complete canonical column coverage required")
    names = (*COMPONENTS, "terms") if route == "primary" else COMPONENTS
    expected_arrays = {
        "keys",
        *(f"rounded{bits}_{name}" for bits in numbers.PRECISIONS for name in names),
    }
    if route == "primary":
        expected_arrays |= {f"moment_{name}" for name in names} | {
            f"without_{name}" for name in mutations
        }
    require(set(arrays) == expected_arrays, "full rounded/diagnostic array coverage required")
    parent.archive.validate_arrays(arrays)
    require(arrays["keys"].dtype == np.dtype("int64"), "integer keys required")
    require(
        all(
            value.dtype == np.dtype("complex128")
            for name, value in arrays.items()
            if name != "keys"
        ),
        "complex128 rounded values required",
    )
    decoded = {}
    for bits in numbers.PRECISIONS:
        records = document["precision"][str(bits)]
        require(set(records) == set(names), "full high precision component coverage required")
        with numbers.context(bits):
            values = {}
            for name in names:
                require(records[name]["bits"] == bits, "recorded precision changed")
                value = numbers.decode(records[name])
                require(
                    value.shape == (189 if name == "terms" else 27, len(keys)),
                    "full high precision shape required",
                )
                require(
                    np.array_equal(numbers.rounded(value), arrays[f"rounded{bits}_{name}"]),
                    "saved rounding differs from lossless coefficient",
                )
                values[name] = value
            require(
                np.array_equal(values["collision"] - values["composition"], values["forcing"]),
                "saved F4 collision/composition identity differs",
            )
            if route == "primary":
                terms = values["terms"].reshape(7, 27, -1)
                require(
                    np.array_equal(terms[:4].sum(axis=0), values["collision"])
                    and np.array_equal(terms[4:].sum(axis=0), values["composition"]),
                    "seven high precision groups differ",
                )
            decoded[bits] = values
    if route == "primary":
        require(arrays["moment_terms"].shape == (189, len(keys)), "all moment-only terms required")
        terms = arrays["moment_terms"].reshape(7, 27, -1)
        for name, expected in (
            ("collision", terms[:4].sum(axis=0)),
            ("composition", terms[4:].sum(axis=0)),
            ("forcing", parent.primary.forcing(terms)),
        ):
            require(
                np.array_equal(arrays[f"moment_{name}"], expected), "moment-only identities differ"
            )
    wrong = {}
    for name in mutations:
        record = document["mutations"][name]
        require(record["bits"] == 192, "192-bit negative control required")
        wrong[name] = numbers.decode(record)
        require(
            wrong[name].shape == (27, len(keys))
            and np.array_equal(numbers.rounded(wrong[name]), arrays[f"without_{name}"]),
            "full mutation values/rounding differ",
        )
    return decoded, wrong


def compare_columns(group, left, right, a, b, old_a, old_b):
    """Keep all values/errors, including every originally failing column."""
    require(
        np.array_equal(a["keys"], b["keys"])
        and np.array_equal(a["keys"], old_a["keys"])
        and np.array_equal(a["keys"], old_b["keys"]),
        "old/new column identity differs",
    )
    old_errors = {
        name: parent.column_errors(old_a[name], old_b[name]).tolist() for name in COMPONENTS
    }
    result = {
        "group": list(group),
        "columns": len(a["keys"]),
        "original_binary64_errors": old_errors,
        "original_failed_columns": [i for i, v in enumerate(old_errors["forcing"]) if v > 1e-8],
        "agreement_192": {
            name: numbers.errors(left[192][name], right[192][name]) for name in COMPONENTS
        },
        "rounded_agreement": {
            name: parent.column_errors(a[f"rounded192_{name}"], b[f"rounded192_{name}"]).tolist()
            for name in COMPONENTS
        },
        "precision_stability": {
            route: {
                name: numbers.errors(values[128][name], values[192][name]) for name in COMPONENTS
            }
            for route, values in (("primary", left), ("worker", right))
        },
    }
    with numbers.context(192):
        result["moment_only"] = {
            name: numbers.errors(numbers.exact64(a[f"moment_{name}"]), left[192][name])
            for name in COMPONENTS
        }
        result["old_to_high_precision"] = {
            f"{route}_{bits}_vs_{old_route}": {
                name: numbers.errors(numbers.exact64(old[name]), values[bits][name])
                for name in COMPONENTS
            }
            for route, values in (("primary", left), ("worker", right))
            for bits in numbers.PRECISIONS
            for old_route, old in (("primary", old_a), ("worker", old_b))
        }
    return result


def mutation_witness(wrong, expected, case):
    j = case["column"]
    with numbers.context(192):
        error = numbers.errors(wrong, expected)["relative"][j]
        difference = numbers.norm(wrong[:, j] - expected[:, j])
        reference_norm = numbers.norm(expected[:, j])
        passed = (
            error > 1e-8 and difference > mp.mpfr("1e-14") and reference_norm > mp.mpfr("1e-14")
        )
    return {
        "group": list(case["group"]),
        "column": j,
        "relative_error": error,
        "difference_norm": float(difference),
        "reference_norm": float(reference_norm),
        "passed": bool(passed),
    }


def summarize(comparisons, physics, witnesses):
    require(
        len(comparisons) == 698 and sum(c["columns"] for c in comparisons) == 1826,
        "all fixed-pilot groups/columns required",
    )
    require(
        len(physics) == 20 and set(witnesses) == set(parent.primary.MUTATIONS),
        "all fixed physical and negative controls required",
    )
    agreement = sum(not v for c in comparisons for v in c["agreement_192"]["forcing"]["passed_1e8"])
    rounded = sum(v > 1e-8 for c in comparisons for v in c["rounded_agreement"]["forcing"])
    unstable = {
        route: sum(
            not v
            for c in comparisons
            for v in c["precision_stability"][route]["forcing"]["passed_1e10"]
        )
        for route in ("primary", "worker")
    }
    moment_failed = sum(
        not v for c in comparisons for v in c["moment_only"]["forcing"]["passed_1e8"]
    )
    physical_passed = all(p["passed"] for p in physics)
    mutations_passed = all(w["passed"] for w in witnesses.values())
    return {
        "original_failed_columns": sum(len(c["original_failed_columns"]) for c in comparisons),
        "agreement_192_failed_columns": agreement,
        "rounded_agreement_failed_columns": rounded,
        "precision_unstable_columns": unstable,
        "moment_only_failed_columns": moment_failed,
        "moment_only_explanation_passed": moment_failed == 0,
        "physical_passed": physical_passed,
        "negative_controls_passed": mutations_passed,
        "high_precision_forcing_candidate": agreement == rounded == 0
        and all(v == 0 for v in unstable.values())
        and physical_passed
        and mutations_passed,
    }


def decision(grids):
    require([g["size"] for g in grids] == [17, 33, 65], "three registered grids required")
    require(
        [g["summary"]["original_failed_columns"] for g in grids] == [182, 174, 158],
        "original 514 failures must be preserved",
    )
    return {
        "stage": "Q012h2a arithmetic diagnosis only",
        "validity": "passed",
        "high_precision_forcing_candidate": all(
            g["summary"]["high_precision_forcing_candidate"] for g in grids
        ),
        "moment_only_explanation_passed": all(
            g["summary"]["moment_only_explanation_passed"] for g in grids
        ),
        "original_H1_passed": False,
        "q012h2_outcome": "not_evaluated",
        "H2": "not_evaluated",
        "H3_with_solves": "not_evaluated",
    }
