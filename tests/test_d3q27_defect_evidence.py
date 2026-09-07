"""Saved-value controls; injected old norms are not real Q012g3 predictions."""

import json
from copy import deepcopy

import numpy as np
import pytest

from research import d3q27_defect_evidence as evidence
from tests.test_d3q27_cubic_defect import ToyChart

defect, parent, exact = evidence.defect, evidence.parent, evidence.conservation.exact


@pytest.fixture(scope="module")
def toy_rows():
    toy, direction = ToyChart(), np.array((0.6, -0.8))
    profiles = {
        (d, a): defect.build_profile(toy, direction, d, arm=a) for d in (2, 3) for a in defect.ARMS
    }
    results = {}
    for kind in ("order", "amplitude"):
        amplitudes = parent.AMPLITUDES if kind == "order" else parent.HOLDOUT_AMPLITUDES
        schedule = {
            "kind": kind,
            "direction_index": 3,
            "direction": direction.tolist(),
            "specifications": [
                {"kind": kind, "direction_index": 3, "amplitude": t, "a": (t * direction).tolist()}
                for t in amplitudes
            ],
        }
        row = {"schedule": schedule, "status": "computed", "profiles": {}, "cases": []}
        for d in (2, 3):
            row["profiles"][str(d)] = {a: profiles[d, a].audit for a in defect.ARMS}
            row["profiles"][str(d)]["comparison"] = defect.compare_profiles(
                profiles[d, "primary"], profiles[d, "independent"]
            )
        conservation_rows = {}
        for spec in schedule["specifications"]:
            original = {
                **spec,
                "models": {},
                "finite": True,
                "roundoff_floor": float(
                    100 * np.finfo(float).eps * max(1.0, defect.norm(toy.quadratic.base))
                ),
            }
            case = {
                "specification": spec,
                "status": "computed",
                "models": {},
                "original_record_reproduced": True,
            }
            conserved = {"models": {}}
            for d in (2, 3):
                a = np.asarray(spec["a"])
                fields = {"W": toy.embed(a, d), "W_R": toy.embed(toy.reduced(a, d), d)}
                fields["Phi_W"] = defect.damping.periodic_step(fields["W"], 1.5, 0.02, 2)
                raw = fields["Phi_W"] - fields["W_R"]
                old = {
                    "degree": d,
                    "status": "computed",
                    "defect_norm": defect.norm(raw),
                    "defect_array": parent.quadratic.array_metadata(raw),
                    "fields": {
                        name: {"array": parent.quadratic.array_metadata(v)}
                        for name, v in fields.items()
                    },
                    "reduced_coordinates": toy.reduced(a, d).tolist(),
                }
                original["models"][str(d)] = old
                samples = {
                    arm: defect.sample_diagnostics(profiles[d, arm], spec["amplitude"], fields)
                    for arm in defect.ARMS
                }
                conservation_fields = (
                    {name: exact.field_record(v, backend="integer") for name, v in fields.items()}
                    if kind == "amplitude"
                    else None
                )
                conserved["models"][str(d)] = {"fields": conservation_fields}
                case["models"][str(d)] = {
                    "original_fields": {
                        name: old["fields"][name]["array"] for name in evidence.FIELDS
                    },
                    "defect_array": old["defect_array"],
                    "conservation_fields": conservation_fields,
                    "samples": samples,
                    "R_path_difference_norms": {
                        arm: defect.norm(
                            np.asarray(s["reconstructed_reduced_coordinates"])
                            - old["reduced_coordinates"]
                        )
                        for arm, s in samples.items()
                    },
                }
            original["resolved"] = all(
                r["defect_norm"] > original["roundoff_floor"] for r in original["models"].values()
            )
            original["cubic_to_quadratic_defect_ratio"] = (
                original["models"]["3"]["defect_norm"] / original["models"]["2"]["defect_norm"]
            )
            # Toy chart is deliberately off-equilibrium, not a successful LBM jet.
            original["amplitude_passed"] = False if kind == "amplitude" else None
            case.update(
                original=original,
                original_record_digest_sha256=evidence.digest(original),
                holdout_prediction=evidence.holdout_prediction(
                    original, {d: v["samples"]["primary"] for d, v in case["models"].items()}
                )
                if kind == "amplitude"
                else None,
            )
            row["cases"].append(case)
            conservation_rows[evidence.case_key(spec)] = conserved
        originals = {evidence.case_key(c["original"]): c["original"] for c in row["cases"]}
        original_fit = parent.fits(list(originals.values()))[3] if kind == "order" else None
        row["fit_prediction"] = (
            evidence.fit_prediction(
                list(originals.values()),
                [
                    {d: v["samples"]["primary"] for d, v in c["models"].items()}
                    for c in row["cases"]
                ],
                original_fit,
            )
            if kind == "order"
            else None
        )
        results[kind] = row, originals, original_fit, conservation_rows
    return results


def validate(item, *, worker=True):
    row, originals, fit, conserved = item
    return evidence.validate_direction(
        row, row["schedule"], originals, fit, conserved, size=7, worker=worker, dimension=2
    )


@pytest.mark.parametrize(
    "kind,worker", [(k, w) for k in ("order", "amplitude") for w in (False, True)]
)
def test_all_toy_direction_evidence_and_json_readback(toy_rows, kind, worker):
    item = deepcopy(toy_rows[kind])
    if not worker:
        item = (evidence.primary_record(item[0]), *item[1:])
    row = json.loads(json.dumps(item[0], allow_nan=False))
    result = validate((row, *item[1:]), worker=worker)
    n = 4 if kind == "order" else 2
    assert result == {
        "passed": True,
        "cases": n,
        "profiles": 2,
        "original_fields": n * 6,
        "original_defects": n * 2,
        "independent_vector_comparisons": 73 if worker else 0,
    }
    gates = evidence.direction_gates(row, worker=worker)
    assert gates["all_gram_comparisons_passed"] and gates["H1"]
    assert gates["H2" if kind == "amplitude" else "H3"]
    assert evidence.primary_record(row) == evidence.primary_record(toy_rows[kind][0])


def test_registered_schedule_exactly_matches_old_coordinates_and_counterexamples():
    main, worker = evidence.direction_schedule(), evidence.direction_schedule(worker=True)
    old = [s for s in parent.case_specifications() if s["kind"] != "special"]
    assert [s for d in main for s in d["specifications"]] == old
    assert len(main) * 2 * 3 == 576 and len(worker) * 2 * 3 == 126
    assert 3 * sum(len(d["specifications"]) for d in main) == 960
    assert 3 * sum(len(d["specifications"]) for d in worker) == 192
    for kind in ("order", "amplitude"):
        assert [d["direction_index"] for d in worker if d["kind"] == kind] == list(
            evidence.WORKER_INDICES[kind]
        )
    assert all(d in main for d in worker)
    # In general this inverse loses bits; the actual schedule uses the original RNG u.
    assert any(
        not np.array_equal(np.asarray(s["a"]) / s["amplitude"], d["direction"])
        for d in main
        for s in d["specifications"]
    )


@pytest.mark.parametrize(
    "damage",
    [
        "last_case",
        "duplicate",
        "last_degree",
        "original",
        "original_hash",
        "field_hash",
        "defect_hash",
        "tail_norm",
        "last_truncation",
        "cross_sign",
        "gram_predicate",
        "H1",
        "P9",
        "r_value",
        "r_difference",
        "last_comparison",
        "independent_hash",
        "comparison_tolerance",
        "nonfinite",
        "H3",
    ],
)
def test_last_case_coefficient_and_predicate_damage_is_rejected(toy_rows, damage):
    item = deepcopy(toy_rows["order"])
    row = item[0]
    case, profile = row["cases"][-1], row["profiles"]["3"]
    data = case["models"]["3"]
    sample = data["samples"]["primary"]
    if damage == "last_case":
        row["cases"].pop()
    elif damage == "duplicate":
        row["cases"][-1] = deepcopy(row["cases"][0])
    elif damage == "last_degree":
        del case["models"]["3"]
    elif damage == "original":
        case["original"] = {**case["original"], "resolved": False}
    elif damage == "original_hash":
        case["original_record_digest_sha256"] = "0" * 64
    elif damage == "field_hash":
        data["original_fields"]["W_R"] = {**data["original_fields"]["W_R"], "sha256": "0" * 64}
    elif damage == "defect_hash":
        data["defect_array"] = {**data["defect_array"], "sha256": "0" * 64}
    elif damage == "tail_norm":
        sample["tail_norm"] += 1
    elif damage == "last_truncation":
        sample["truncations"].pop()
    elif damage == "cross_sign":
        sample["signed_cross_terms"][8][9] += 0.1
    elif damage == "gram_predicate":
        sample["truncations"][-1]["gram_passed"] = False
    elif damage == "H1":
        sample["H1_reconstruction_passed"] = False
    elif damage == "P9":
        sample["P9_vector_difference_norm"] += 1
    elif damage == "r_value":
        sample["reconstructed_reduced_coordinates"][-1] += 0.1
    elif damage == "r_difference":
        data["R_path_difference_norms"]["primary"] += 1
    elif damage == "last_comparison":
        profile["comparison"]["rows"].pop()
    elif damage == "independent_hash":
        profile["comparison"]["rows"][-1]["independent"]["sha256"] = "0" * 64
    elif damage == "comparison_tolerance":
        profile["comparison"]["rows"][-1]["tolerance"] = 1.0
    elif damage == "nonfinite":
        sample["group_contribution_norms"][-1] = float("nan")
    elif damage == "H3":
        row["fit_prediction"]["H3_passed"] = False
    with pytest.raises(ValueError):
        validate(item)


@pytest.mark.parametrize(
    "damage",
    [
        "shape",
        "dtype",
        "bytes",
        "hash",
        "reduced_constant",
        "tail_coefficient",
        "base",
        "realification",
    ],
)
def test_profile_structural_damage_is_rejected(toy_rows, damage):
    item = deepcopy(toy_rows["order"])
    p = item[0]["profiles"]["3"]["primary"]
    if damage == "shape":
        p["mapped_coefficients"][-1]["shape"][-1] = 26
    elif damage == "dtype":
        p["mapped_coefficients"][-1]["dtype"] = "<f4"
    elif damage == "bytes":
        p["mapped_coefficients"][-1]["bytes"] -= 8
    elif damage == "hash":
        p["mapped_coefficients"][-1]["sha256"] = "bad"
    elif damage == "reduced_constant":
        p["reduced_path_values"][0][-1] = 0.01
    elif damage == "tail_coefficient":
        p["local"]["remainder"].pop()
    elif damage == "base":
        p["composition_coefficients"][0]["norm"] += 1
    elif damage == "realification":
        p["composition_realification"][-1]["scaled_imaginary_norm"] += 1
    with pytest.raises(ValueError):
        validate(item)


@pytest.mark.parametrize("damage", ["conservation", "H2", "extra_generic_gate"])
def test_holdout_exact_and_generic_scope_are_not_conflated(toy_rows, damage):
    item = deepcopy(toy_rows["order" if damage == "extra_generic_gate" else "amplitude"])
    case = item[0]["cases"][-1]
    if damage == "conservation":
        case["models"]["3"]["conservation_fields"] = {}
    elif damage == "H2":
        case["holdout_prediction"]["H2_passed"] = False
    else:
        case["models"]["3"]["conservation_fields"] = {}
    with pytest.raises(ValueError):
        validate(item)


@pytest.fixture(scope="module")
def saved_parent():
    # Read only: these are frozen old results, not fresh physical predictions.
    return evidence.conservation.read_json(evidence.conservation.PARENT_PATH)


def perfect_norm_injection(original):
    return {
        str(d): {
            "P9_norm": original["models"][str(d)]["defect_norm"],
            "raw_resolved": original["resolved"],
            "P9_vector_passed": True,
        }
        for d in (2, 3)
    }


def test_old_all_192_fits_can_be_reproduced_without_relabeling_the_three_failures(saved_parent):
    failures = []
    for grid in saved_parent["cycle"]["grids"]:
        for fit in grid["generic_fits"]:
            rows = [
                r
                for r in grid["records"]
                if r["kind"] == "order" and r["direction_index"] == fit["direction_key"]
            ]
            result = evidence.fit_prediction(rows, [perfect_norm_injection(r) for r in rows], fit)
            assert result["H3_passed"]
            assert result["predicted_original_H4_predicate"] == fit["passed"]
            if not fit["passed"]:
                failures.append((grid["size"], fit["direction_key"]))
    assert failures == [(65, 34), (65, 51), (65, 52)]


def test_old_holdout_predicates_keep_ratio_failures_separate_from_composite_H5(saved_parent):
    half_failures = worse = predictions = 0
    for grid in saved_parent["cycle"]["grids"]:
        for row in grid["records"]:
            if row["kind"] != "amplitude":
                continue
            result = evidence.holdout_prediction(row, perfect_norm_injection(row))
            assert result["H2_passed"]  # This asserts the harness, not an actual prediction.
            assert result["original_composite_H5"] == row["amplitude_passed"]
            half_failures += result["original_defect_only_ratio"] > 0.5
            worse += result["original_defect_only_ratio"] > 1
            predictions += 1
    assert (predictions, half_failures, worse) == (192, 81, 37)


@pytest.mark.parametrize(
    "ratio,predicted",
    [(0.5, np.nextafter(0.5, 1)), (1.0, np.nextafter(1.0, 2)), (0.5, 0.5), (1.0, 1.0)],
)
def test_holdout_boundaries_use_the_exact_registered_inequalities(ratio, predicted):
    original = {
        "kind": "amplitude",
        "resolved": True,
        "cubic_to_quadratic_defect_ratio": ratio,
        "amplitude_passed": False,
    }
    samples = {
        str(d): {
            "P9_norm": 1.0 if d == 2 else float(predicted),
            "raw_resolved": True,
            "P9_vector_passed": True,
        }
        for d in (2, 3)
    }
    assert evidence.holdout_prediction(original, samples)["H2_passed"] is bool(predicted == ratio)


@pytest.mark.parametrize(
    "damage", ["floor", "zero", "missing", "reorder", "bad_fit", "shift_slope", "shift_ratio"]
)
def test_unresolved_and_inaccurate_predictions_do_not_pass(saved_parent, damage):
    grid = saved_parent["cycle"]["grids"][0]
    rows = [r for r in grid["records"] if r["kind"] == "order" and r["direction_index"] == 0]
    fit, samples = deepcopy(grid["generic_fits"][0]), [perfect_norm_injection(r) for r in rows]
    if damage in ("missing", "reorder", "bad_fit"):
        if damage == "missing":
            samples.pop()
        elif damage == "reorder":
            rows = list(reversed(rows))
        else:
            fit["passed"] = not fit["passed"]
        with pytest.raises(ValueError):
            evidence.fit_prediction(rows, samples, fit)
        return
    if damage in ("floor", "zero"):
        samples[-1]["3"]["P9_norm"] = rows[-1]["roundoff_floor"] if damage == "floor" else 0.0
    elif damage == "shift_slope":
        samples[0]["3"]["P9_norm"] *= 1.1
    else:
        samples[-1]["3"]["P9_norm"] *= 1.02
    result = evidence.fit_prediction(rows, samples, fit)
    assert not result["H3_passed"]
    if damage in ("floor", "zero"):
        assert result["predicted_slopes"] == {"2": None, "3": None}
        assert result["smallest_amplitude_ratio"] is None


def test_consistent_scientific_failure_is_retained_not_rejected_as_corrupt_data(toy_rows):
    item = deepcopy(toy_rows["order"])
    sample = item[0]["cases"][-1]["models"]["3"]["samples"]["primary"]
    sample["reconstruction_errors"]["defect_reconstructed"] = 2 * sample["roundoff_floor"]
    sample["H1_reconstruction_passed"] = False
    assert validate(item)["passed"]
    gates = evidence.direction_gates(item[0], worker=True)
    assert not gates["H1"] and not gates["worker_both_arm_reconstruction_passed"]
    assert gates["all_gram_comparisons_passed"]


def test_unresolved_holdout_is_not_excluded_or_accepted():
    old = {
        "kind": "amplitude",
        "resolved": False,
        "cubic_to_quadratic_defect_ratio": None,
        "amplitude_passed": False,
    }
    samples = {
        str(d): {"P9_norm": 0.0, "raw_resolved": False, "P9_vector_passed": False} for d in (2, 3)
    }
    result = evidence.holdout_prediction(old, samples)
    assert result["predicted_ratio"] is None and not result["H2_passed"]


def test_negative_gram_prediction_remains_negative_and_fails_validity(toy_rows):
    item = deepcopy(toy_rows["order"])
    profile = item[0]["profiles"]["3"]["primary"]
    gram = np.asarray(profile["gram"])
    gram[0, 1] = gram[1, 0] = -1e10
    profile["gram"] = gram.tolist()
    for case in item[0]["cases"]:
        sample = case["models"]["3"]["samples"]["primary"]
        powers = sample["parameter"] ** np.arange(10)
        weighted = gram * np.outer(powers, powers)
        sample["weighted_gram"] = weighted.tolist()
        sample["signed_cross_terms"] = (2 * np.triu(weighted, k=1)).tolist()
        for truncation in sample["truncations"]:
            n = truncation["degree"] + 1
            value = float(powers[:n] @ gram[:n, :n] @ powers[:n])
            assert value < 0
            truncation["gram_norm_squared"] = value
            truncation["gram_error"] = abs(value - truncation["direct_norm_squared"])
            truncation["gram_passed"] = False
    assert validate(item)["passed"]  # The recorded failure is internally consistent.
    assert not evidence.direction_gates(item[0], worker=True)["all_gram_comparisons_passed"]


def test_consistent_full_vector_failure_is_not_converted_to_success(toy_rows):
    item = deepcopy(toy_rows["order"])
    comparison = item[0]["profiles"]["3"]["comparison"]
    last = comparison["rows"][-1]
    last["difference_norm"] = last["tolerance"] * 2
    last["passed"] = comparison["passed"] = False
    assert validate(item)["passed"]
    gates = evidence.direction_gates(item[0], worker=True)
    assert not gates["independent_vectors_passed"] and gates["H1"]


def test_holdout_ratio_match_does_not_replace_full_vector_accuracy():
    old = {
        "kind": "amplitude",
        "resolved": True,
        "cubic_to_quadratic_defect_ratio": 0.25,
        "amplitude_passed": True,
    }
    samples = {
        str(d): {
            "P9_norm": 1.0 if d == 2 else 0.25,
            "raw_resolved": True,
            "P9_vector_passed": d == 2,
        }
        for d in (2, 3)
    }
    result = evidence.holdout_prediction(old, samples)
    assert result["half_predicate_matches"] and result["worse_than_quadratic_predicate_matches"]
    assert not result["H2_passed"]


def test_absolute_P9_threshold_and_relative_display_use_the_same_saved_numerator(toy_rows):
    row = deepcopy(toy_rows["order"][0])
    case = row["cases"][-1]
    sample = case["models"]["3"]["samples"]["primary"]
    raw = sample["raw_defect_norm"]
    difference = float(np.nextafter(1e-3 * raw, np.inf))
    sample["P9_vector_difference_norm"] = difference
    sample["P9_vector_relative_error"] = difference / raw
    sample["P9_vector_passed"] = False
    evidence.validate_sample(sample, row["profiles"]["3"]["primary"], case["original"], 3)
    sample["P9_vector_difference_norm"] = 1e-3 * raw
    sample["P9_vector_relative_error"] = sample["P9_vector_difference_norm"] / raw
    sample["P9_vector_passed"] = True
    evidence.validate_sample(sample, row["profiles"]["3"]["primary"], case["original"], 3)
