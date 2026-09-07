"""Q012g3 coverage, saved-value audits and unchanged preregistered predicates.

These checks do not build physical charts or substitute for source seals,
fresh full-vector comparisons, worker replay, or final artifact readback.
Scientific failure is retained as evidence, not raised as a data error.
"""

from __future__ import annotations

import re
from math import prod

import numpy as np

from research import d3q27_cubic_defect as defect
from research import q012g1_d3q27_conservation as conservation
from research import q012g_d3q27_cubic_chart as parent
from ttim_lbm.rational_spectrum import _all_numeric_values_finite

SIZES = (17, 33, 65)
WORKER_INDICES = {"order": (*range(8), 34, 51, 52), "amplitude": (*range(8), 16, 21)}
FIELDS = ("W", "Phi_W", "W_R")
require = conservation.require
digest = conservation.digest


def direction_schedule(*, worker=False):
    """Regenerate u directly; never recover it by dividing rounded a by t."""
    schedule = []
    for kind, seed, count, amplitudes in (
        ("order", parent.ORDER_SEED, 64, parent.AMPLITUDES),
        ("amplitude", parent.AMPLITUDE_SEED, 32, parent.HOLDOUT_AMPLITUDES),
    ):
        directions = parent.quadratic.normalized_directions(seed, count)
        indices = WORKER_INDICES[kind] if worker else range(count)
        for index in indices:
            direction = directions[index]
            schedule.append(
                {
                    "kind": kind,
                    "direction_index": index,
                    "direction": direction.tolist(),
                    "specifications": [
                        {
                            "kind": kind,
                            "direction_index": index,
                            "amplitude": amplitude,
                            "a": (amplitude * direction).tolist(),
                        }
                        for amplitude in amplitudes
                    ],
                }
            )
    return schedule


def case_key(row):
    return row["kind"], row["direction_index"], row["amplitude"]


def array_record(record, shape, dtype, *, with_norm=True):
    keys = {"shape", "dtype", "bytes", "sha256"} | ({"norm"} if with_norm else set())
    require(set(record) == keys, "array metadata keys differ")
    require(record["shape"] == list(shape), "array shape differs")
    require(record["dtype"] == np.dtype(dtype).str, "array dtype differs")
    require(record["bytes"] == prod(shape) * np.dtype(dtype).itemsize, "array byte count differs")
    require(
        isinstance(record["sha256"], str)
        and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is not None,
        "invalid array hash",
    )
    if with_norm:
        require(np.isfinite(record["norm"]) and record["norm"] >= 0, "invalid array norm")


def bare(record):
    return {k: record[k] for k in ("shape", "dtype", "bytes", "sha256")}


def realification(record):
    require(_all_numeric_values_finite(record), "nonfinite realification evidence")
    require(record["real_norm"] >= 0 and record["imaginary_norm"] >= 0, "negative realness norm")
    scale = max(1.0, record["real_norm"])
    require(
        record["scaled_imaginary_norm"] == record["imaginary_norm"] / scale
        and record["passed"] is (record["imaginary_norm"] <= 1e-9 * scale),
        "realification arithmetic differs",
    )
    require(record["passed"], "unrealified coefficient field")


def validate_profile(profile, schedule, degree, size, *, arm, dimension=104):
    require(_all_numeric_values_finite(profile), "nonfinite profile")
    require(
        profile["degree"] == degree
        and profile["arm"] == arm
        and profile["direction"] == schedule["direction"],
        "profile degree, arm or direction differs",
    )
    shape = (size, size, size, 27)
    require(len(profile["state_path"]) == degree + 1, "incomplete state path")
    for record in profile["state_path"]:
        array_record(record, shape, np.float64)
    reduced = np.asarray(profile["reduced_path_values"], dtype=float)
    require(
        reduced.shape == (degree + 1, dimension) and np.all(reduced[0] == 0), "reduced path differs"
    )
    require(profile["reduced_path"] == defect.metadata(reduced), "reduced path values/hash differ")
    support = profile["compact_composition_waves"]["shape"]
    require(
        len(support) == 2 and support[1] == 3 and support[0] > 0, "invalid compact wave support"
    )
    array_record(profile["compact_composition_waves"], support, np.int64, with_norm=False)
    array_record(profile["compact_composition"], (10, support[0], 27), np.complex128)
    local = profile["local"]
    array_record(local["rho"], (degree + 1, size, size, size), np.float64)
    array_record(local["momentum"], (degree + 1, size, size, size, 3), np.float64)
    require(
        local["numerator_has_population_weights"] is (arm == "independent"),
        "numerator convention differs",
    )
    density_range = local["constant_density_range"]
    require(
        len(density_range) == 2 and 0 < density_range[0] <= density_range[1],
        "constant density invalid",
    )
    momentum_range = local["constant_momentum_component_ranges"]
    require(
        len(momentum_range) == 3 and all(len(r) == 2 and r[0] <= r[1] for r in momentum_range),
        "constant momentum invalid",
    )
    for key, length in (
        ("numerator", 2 * degree + 1),
        ("quotient", 10),
        ("remainder", 10 + degree),
    ):
        require(len(local[key]) == length, "incomplete local coefficient sequence")
        for record in local[key]:
            array_record(record, shape, np.float64)
    for key in ("mapped_coefficients", "composition_coefficients", "defect_coefficients"):
        require(len(profile[key]) == 10, "incomplete coefficient sequence")
        for record in profile[key]:
            array_record(record, shape, np.float64)
    require(
        profile["composition_coefficients"][0] == profile["state_path"][0],
        "composition base changed",
    )
    reals = profile["composition_realification"]
    require(
        len(reals) == 10 and reals[0] == {"passed": True, "constant_is_original_base": True},
        "incomplete composition realification",
    )
    for record in reals[1:]:
        realification(record)
    gram = np.asarray(profile["gram"], dtype=float)
    require(
        gram.shape == (10, 10) and np.array_equal(gram, gram.T), "Gram shape or symmetry differs"
    )
    require(np.all(np.diag(gram) >= 0), "negative coefficient squared norm")


def validate_sample(sample, profile, original, degree):
    """Recompute saved scalar arithmetic; actual vector errors need the worker."""
    require(_all_numeric_values_finite(sample), "nonfinite sample")
    old = original["models"][str(degree)]
    t, floor = original["amplitude"], original["roundoff_floor"]
    raw_norm = old["defect_norm"]
    require(
        sample["parameter"] == t
        and sample["degree"] == degree
        and sample["roundoff_floor"] == floor
        and sample["raw_defect_norm"] == raw_norm
        and sample["raw_resolved"] is (raw_norm > floor),
        "original comparison scalars differ",
    )
    fields = sample["reconstruction_fields"]
    require(
        set(fields)
        == {
            "W_path",
            "R_path",
            "W_R_path",
            "P9",
            "tail",
            "defect_reconstructed",
            "Phi_reconstructed",
        },
        "incomplete reconstruction fields",
    )
    dimension = profile["reduced_path"]["shape"][1]
    for key, record in fields.items():
        shape = [dimension] if key == "R_path" else profile["state_path"][0]["shape"]
        array_record(record, shape, np.float64)
    reduced = defect.poly.evaluate(np.asarray(profile["reduced_path_values"]), t)
    require(
        sample["reconstructed_reduced_coordinates"] == reduced.tolist()
        and fields["R_path"] == defect.metadata(reduced),
        "saved reduced reconstruction differs",
    )
    errors = sample["reconstruction_errors"]
    require(
        set(errors) == {"W_path", "W_R_path", "Phi_reconstructed", "defect_reconstructed"}
        and all(v >= 0 for v in errors.values()),
        "invalid reconstruction errors",
    )
    require(
        sample["H1_reconstruction_passed"] is all(v <= floor for v in errors.values()),
        "H1 predicate differs",
    )
    difference = sample["P9_vector_difference_norm"]
    require(
        difference >= 0
        and sample["P9_norm"] == fields["P9"]["norm"]
        and sample["tail_norm"] == fields["tail"]["norm"],
        "P9/tail scalar evidence differs",
    )
    require(
        sample["P9_vector_relative_error"] == (difference / raw_norm if raw_norm > 0 else None),
        "P9 relative error differs",
    )
    require(
        sample["P9_vector_passed"] is (raw_norm > floor and difference <= 1e-3 * raw_norm),
        "P9 vector predicate differs",
    )
    realification(sample["composition_realification"])
    gram = np.asarray(profile["gram"])
    powers = t ** np.arange(10)
    weighted = gram * np.outer(powers, powers)
    require(sample["weighted_gram"] == weighted.tolist(), "weighted Gram differs")
    require(
        sample["signed_cross_terms"] == (2 * np.triu(weighted, k=1)).tolist(),
        "signed cross terms differ",
    )
    rows = sample["truncations"]
    require(
        [r["degree"] for r in rows] == list(range(degree + 1, 10)),
        "incomplete or reordered truncations",
    )
    for row in rows:
        n = row["degree"]
        by_gram = float(powers[: n + 1] @ gram[: n + 1, : n + 1] @ powers[: n + 1])
        direct = row["norm"] ** 2
        tolerance = 1e-9 * max(floor**2, direct)
        require(row["norm"] >= 0 and row["vector_difference_norm"] >= 0, "negative truncation norm")
        require(
            row["gram_norm_squared"] == by_gram
            and row["direct_norm_squared"] == direct
            and row["gram_error"] == abs(by_gram - direct)
            and row["gram_tolerance"] == tolerance
            and row["gram_passed"] is (by_gram >= 0 and abs(by_gram - direct) <= tolerance),
            "truncation Gram arithmetic or predicate differs",
        )
        require(
            row["relative_vector_error"]
            == (row["vector_difference_norm"] / raw_norm if raw_norm > 0 else None),
            "truncation relative error differs",
        )
    require(
        sample["group_order"] == ["low_0_to_d", "leading_d_plus_1", "higher_d_plus_2_to_9"]
        and len(sample["group_contribution_norms"]) == 3
        and all(v >= 0 for v in sample["group_contribution_norms"]),
        "degree groups differ",
    )


def comparison_arrays(profile):
    rows = [(f"v{n}", v) for n, v in enumerate(profile["state_path"])]
    rows.extend(
        (
            ("reduced_path", profile["reduced_path"]),
            ("rho", profile["local"]["rho"]),
            ("momentum", profile["local"]["momentum"]),
        )
    )
    for n in range(10):
        rows.extend(
            (
                (f"mapped{n}", profile["mapped_coefficients"][n]),
                (f"composed{n}", profile["composition_coefficients"][n]),
                (f"C{n}", profile["defect_coefficients"][n]),
            )
        )
    return rows


def validate_comparison(report, primary, independent):
    require(_all_numeric_values_finite(report), "nonfinite arm comparison")
    first, second = comparison_arrays(primary), comparison_arrays(independent)
    require(
        report["full_vector_comparisons"] == len(report["rows"]) == len(first) == len(second),
        "incomplete full-vector comparisons",
    )
    for row, (name, a), (other, b) in zip(report["rows"], first, second, strict=True):
        tolerance = 1e-10 * max(1.0, b["norm"])
        require(
            row["name"] == name == other
            and row["primary"] == bare(a)
            and row["independent"] == bare(b),
            "comparison array linkage differs",
        )
        require(
            row["difference_norm"] >= 0
            and row["reference_norm"] == b["norm"]
            and row["tolerance"] == tolerance
            and row["passed"] is (row["difference_norm"] <= tolerance),
            "comparison arithmetic differs",
        )
    require(
        report["passed"] is all(r["passed"] for r in report["rows"]), "comparison aggregate differs"
    )


def holdout_prediction(original, samples):
    require(
        original["kind"] == "amplitude" and set(samples) == {"2", "3"},
        "holdout model coverage differs",
    )
    resolved = bool(original["resolved"] and all(s["raw_resolved"] for s in samples.values()))
    norm2, norm3 = (samples[str(d)]["P9_norm"] for d in (2, 3))
    require(
        norm2 >= 0 and norm3 >= 0 and _all_numeric_values_finite(samples), "invalid predicted norms"
    )
    ratio = norm3 / norm2 if resolved and norm2 > 0 else None
    old_ratio = original["cubic_to_quadratic_defect_ratio"]
    half_match = bool(
        ratio is not None and old_ratio is not None and (ratio <= 0.5) == (old_ratio <= 0.5)
    )
    worse_match = bool(
        ratio is not None and old_ratio is not None and (ratio > 1) == (old_ratio > 1)
    )
    vector_passed = resolved and all(s["P9_vector_passed"] for s in samples.values())
    return {
        "original_defect_only_ratio": old_ratio,
        "original_composite_H5": original["amplitude_passed"],
        "predicted_ratio": ratio,
        "vector_passed": vector_passed,
        "half_predicate_matches": half_match,
        "worse_than_quadratic_predicate_matches": worse_match,
        "H2_passed": vector_passed and half_match and worse_match,
    }


def fit_prediction(originals, samples, original_fit):
    """Four original amplitudes; predicted values below the old floor stay null."""
    require(len(originals) == len(samples) == 4, "a full four-amplitude fit is required")
    index = originals[0]["direction_index"]
    require(
        all(r["kind"] == "order" and r["direction_index"] == index for r in originals),
        "mixed fit directions",
    )
    require(
        tuple(r["amplitude"] for r in originals) == parent.AMPLITUDES,
        "fit amplitudes changed or reordered",
    )
    require(
        original_fit == parent.fits(originals)[index],
        "original fit differs from sealed case values",
    )
    require(
        all(set(s) == {"2", "3"} for s in samples) and _all_numeric_values_finite(samples),
        "incomplete or nonfinite predicted fit",
    )
    resolved = bool(
        original_fit["resolved"]
        and all(
            s[str(d)]["P9_norm"] > r["roundoff_floor"]
            for r, s in zip(originals, samples, strict=True)
            for d in (2, 3)
        )
    )
    slopes = {
        str(d): float(
            np.polyfit(
                np.log(parent.AMPLITUDES), np.log([s[str(d)]["P9_norm"] for s in samples]), 1
            )[0]
        )
        if resolved
        else None
        for d in (2, 3)
    }
    ratio = samples[-1]["3"]["P9_norm"] / samples[-1]["2"]["P9_norm"] if resolved else None
    old_ratio = original_fit["smallest_amplitude_ratio"]
    slope_errors = {
        str(d): abs(slopes[str(d)] - original_fit["slopes"][str(d)]) if resolved else None
        for d in (2, 3)
    }
    ratio_error = (
        abs(ratio - old_ratio) / old_ratio
        if resolved and old_ratio is not None and old_ratio > 0
        else None
    )
    passed = bool(
        resolved and 2.9 <= slopes["2"] <= 3.1 and 3.9 <= slopes["3"] <= 4.1 and ratio <= 0.1
    )
    match = bool(resolved and passed == original_fit["passed"])
    return {
        "original_fit": original_fit,
        "resolved": resolved,
        "predicted_slopes": slopes,
        "slope_absolute_errors": slope_errors,
        "smallest_amplitude_ratio": ratio,
        "ratio_relative_error": ratio_error,
        "predicted_original_H4_predicate": passed,
        "original_H4_predicate_matches": match,
        "H3_passed": bool(
            resolved
            and all(e <= 0.01 for e in slope_errors.values())
            and ratio_error is not None
            and ratio_error <= 0.01
            and match
        ),
    }


def validate_direction(
    row, schedule, originals, original_fit, conservation_rows, *, size, worker, dimension=104
):
    """Audit a complete direction without loading all physical fields in memory."""
    require(_all_numeric_values_finite(row), "nonfinite direction evidence")
    require(
        row["status"] == "computed" and row["schedule"] == schedule, "direction failed or changed"
    )
    require(set(row["profiles"]) == {"2", "3"}, "missing profile degree")
    require(
        [r["specification"] for r in row["cases"]] == schedule["specifications"],
        "incomplete, duplicate or reordered cases",
    )
    for degree in (2, 3):
        profiles = row["profiles"][str(degree)]
        require(
            set(profiles) == ({"primary", "independent", "comparison"} if worker else {"primary"}),
            "profile arm coverage differs",
        )
        for arm in ("primary", "independent") if worker else ("primary",):
            validate_profile(profiles[arm], schedule, degree, size, arm=arm, dimension=dimension)
        if worker:
            validate_comparison(
                profiles["comparison"], profiles["primary"], profiles["independent"]
            )
    for case in row["cases"]:
        spec = case["specification"]
        original = originals[case_key(spec)]
        require(
            case["status"] == "computed" and case["original_record_reproduced"] is True,
            "original case was not replayed",
        )
        require(
            case["original"] == original
            and case["original_record_digest_sha256"] == digest(original),
            "original record differs",
        )
        require(set(case["models"]) == {"2", "3"}, "case degree coverage differs")
        for degree in (2, 3):
            data, old = case["models"][str(degree)], original["models"][str(degree)]
            require(set(data["original_fields"]) == set(FIELDS), "original field coverage differs")
            require(
                data["original_fields"] == {name: old["fields"][name]["array"] for name in FIELDS}
                and data["defect_array"] == old["defect_array"],
                "original field or defect hash differs",
            )
            if schedule["kind"] == "amplitude":
                expected = conservation_rows[case_key(spec)]["models"][str(degree)]["fields"]
                require(
                    data["conservation_fields"] == expected,
                    "exact holdout fields differ from Q012g1",
                )
                for field in data["conservation_fields"].values():
                    conservation.exact.validate_field_record(field)
            else:
                require(
                    data["conservation_fields"] is None,
                    "generic conservation gate was not registered",
                )
            arms = ("primary", "independent") if worker else ("primary",)
            require(set(data["samples"]) == set(arms), "sample arm coverage differs")
            require(
                set(data["R_path_difference_norms"]) == set(arms),
                "reduced comparison arm coverage differs",
            )
            for arm in arms:
                sample = data["samples"][arm]
                validate_sample(sample, row["profiles"][str(degree)][arm], original, degree)
                difference = defect.norm(
                    np.asarray(sample["reconstructed_reduced_coordinates"])
                    - old["reduced_coordinates"]
                )
                require(
                    data["R_path_difference_norms"][arm] == difference,
                    "reduced path difference norm differs",
                )
        if schedule["kind"] == "amplitude":
            predicted = holdout_prediction(
                original, {str(d): case["models"][str(d)]["samples"]["primary"] for d in (2, 3)}
            )
            require(case["holdout_prediction"] == predicted, "saved H2 differs")
        else:
            require(case["holdout_prediction"] is None, "H2 was assigned to a generic case")
    if schedule["kind"] == "order":
        prediction = fit_prediction(
            [r["original"] for r in row["cases"]],
            [
                {str(d): r["models"][str(d)]["samples"]["primary"] for d in (2, 3)}
                for r in row["cases"]
            ],
            original_fit,
        )
        require(row["fit_prediction"] == prediction, "saved H3 differs")
    else:
        require(row["fit_prediction"] is None, "generic fit assigned to holdout")
    ncases = len(row["cases"])
    return {
        "passed": True,
        "cases": ncases,
        "profiles": 2,
        "original_fields": 6 * ncases,
        "original_defects": 2 * ncases,
        "independent_vector_comparisons": 73 if worker else 0,
    }


def direction_gates(row, *, worker):
    """Call after validate_direction; keep Gram validity separate from H1--H3."""
    require(row["status"] == "computed" and bool(row["cases"]), "no computed direction")
    arms = ("primary", "independent") if worker else ("primary",)
    primary_h1 = all(
        case["models"][str(d)]["samples"]["primary"]["H1_reconstruction_passed"]
        for case in row["cases"]
        for d in (2, 3)
    )
    worker_h1 = all(
        case["models"][str(d)]["samples"][arm]["H1_reconstruction_passed"]
        for case in row["cases"]
        for d in (2, 3)
        for arm in arms
    )
    gram = all(
        truncation["gram_passed"]
        for case in row["cases"]
        for d in (2, 3)
        for arm in arms
        for truncation in case["models"][str(d)]["samples"][arm]["truncations"]
    )
    comparison = (
        all(row["profiles"][str(d)]["comparison"]["passed"] for d in (2, 3)) if worker else None
    )
    kind = row["schedule"]["kind"]
    return {
        "all_gram_comparisons_passed": gram,
        "independent_vectors_passed": comparison,
        "worker_both_arm_reconstruction_passed": worker_h1 if worker else None,
        "H1": primary_h1,
        "H2": all(case["holdout_prediction"]["H2_passed"] for case in row["cases"])
        if kind == "amplitude"
        else None,
        "H3": row["fit_prediction"]["H3_passed"] if kind == "order" else None,
    }


def primary_record(row):
    """Canonical scientific primary-arm record for exact worker/main equality."""
    require(row["status"] == "computed", "incomplete direction cannot establish replay")
    cases = []
    for case in row["cases"]:
        models = {}
        for degree, data in case["models"].items():
            models[degree] = {
                **data,
                "samples": {"primary": data["samples"]["primary"]},
                "R_path_difference_norms": {"primary": data["R_path_difference_norms"]["primary"]},
            }
        cases.append({**case, "models": models})
    return {
        "schedule": row["schedule"],
        "status": row["status"],
        "profiles": {d: {"primary": v["primary"]} for d, v in row["profiles"].items()},
        "cases": cases,
        "fit_prediction": row["fit_prediction"],
    }
