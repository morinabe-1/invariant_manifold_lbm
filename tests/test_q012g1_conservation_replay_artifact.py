"""Full saved-worker audit, with independently written rational identities.

The numerical identity checks use no implementation decomposition/validation
helpers; runner readiness is also checked separately. No physical campaign is
executed. Missing worker evidence is an error.
"""

from copy import deepcopy
from fractions import Fraction
from itertools import product
from math import isfinite, prod

import numpy as np
import pytest

from research import q012g1_d3q27_conservation as runner
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = runner.PARENT_PATH.with_name("q012g1_d3q27_conservation_replay.json")
# Completed on 2026-09-08 at 00:08:34 JST; never a seal of partial evidence.
WORKER_SHA = "b745e66a011972ecd10a76429b827456c21690ddd5bd7291a643a5629cc7c1e5"
VELOCITIES = list(product((-1, 0, 1), repeat=3))
MOMENTS = [[1] * 27] + [[v[i] for v in VELOCITIES] for i in range(3)]
TOLERANCE = Fraction.from_float(5e-13)


def rational(record):
    assert set(record) == {"numerator", "denominator", "float"}
    assert isinstance(record["numerator"], str) and isinstance(record["denominator"], str)
    value = Fraction(int(record["numerator"]), int(record["denominator"]))
    assert str(value.numerator) == record["numerator"]
    assert str(value.denominator) == record["denominator"]
    assert isinstance(record["float"], float) and isfinite(record["float"])
    assert float(value) == record["float"]
    return value


def field_values(field, size):
    assert field["array"]["shape"] == [size, size, size, 27]
    assert field["array"]["dtype"] == "<f8" and field["array"]["bytes"] == 8 * 27 * size**3
    assert len(field["array"]["sha256"]) == 64
    assert field["site_count"] == size**3
    assert field["coverage"] == {
        "populations": 27,
        "sites_per_population": size**3,
        "values": 27 * size**3,
    }
    populations = list(map(rational, field["population_sums"]))
    assert len(populations) == 27
    moments = [
        sum((c * s for c, s in zip(row, populations, strict=True)), Fraction(0)) for row in MOMENTS
    ]
    assert list(map(rational, field["conserved_sums"])) == moments
    legacy = list(map(Fraction.from_float, field["legacy_conserved_sums"]))
    assert len(legacy) == 4
    assert list(map(rational, field["sum_rounding"])) == [
        a - b for a, b in zip(legacy, moments, strict=True)
    ]
    return populations, moments, legacy


@pytest.fixture(scope="module")
def saved():
    assert _file_sha256(PATH) == WORKER_SHA
    document = runner.read_json(PATH)
    assert document["kind"] == runner.WORKER_KIND and document["backend"] == "gmp"
    assert document["source_unchanged_after"] is True
    assert runner.parent.source_equal(document, runner.metadata())
    assert (
        document["runner_source"]["sha256"]
        == "a697d255cb2c2c697d1b98c06cc5d54c8a346e50929d05a3c793f2f09bdeb7dd"
    )
    assert (
        document["helper_sources"]["conservation_audit"]["sha256"]
        == "665247de3962bdd6475caf0d96e726fa663e8fa8c9faa6e27362601961b91375"
    )
    assert document["evidence_digest_sha256"] == runner.digest(document["evidence"])
    assert _all_numeric_values_finite(document)
    assert [g["size"] for g in document["evidence"]["grids"]] == [17, 33, 65]
    assert len(document["grid_artifacts"]) == 3
    return document


def test_worker_retains_all_parent_inputs_and_its_separate_source_seal(saved):
    evidence = saved["evidence"]
    assert evidence["input_audit"] == runner.input_audit()
    assert evidence["input_audit"]["passed"]
    assert len(evidence["input_audit"]["legacy_counterexamples"]) == 256
    assert evidence["artificial_controls"] == runner.exact.artificial_controls()
    assert evidence["artificial_controls"]["passed"]
    parent = runner.read_json(runner.PARENT_PATH)
    assert saved["process_id"] != parent["process_id"]
    assert parent["study_gate"] == "passed" and parent["scientific_outcome"] == "rejected"


@pytest.mark.parametrize("size", [17, 33, 65])
def test_rounded_analytic_baselines_and_all_twelve_uniform_negative_controls(saved, size):
    grid = next(g for g in saved["evidence"]["grids"] if g["size"] == size)
    baseline = grid["baseline"]
    populations, moments, _ = field_values(baseline["field"], size)
    weights = [
        float(prod(Fraction(2, 3) if c == 0 else Fraction(1, 6) for c in v)) for v in VELOCITIES
    ]
    assert populations == [Fraction.from_float(w) * size**3 for w in weights]
    analytic = [Fraction(size**3), Fraction(0), Fraction(0), Fraction(0)]
    assert list(map(rational, baseline["analytic_conserved_sums"])) == analytic
    assert list(map(rational, baseline["rounded_baseline_minus_analytic_site_average"])) == [
        (a - b) / size**3 for a, b in zip(moments, analytic, strict=True)
    ]
    controls = grid["negative_controls"]
    assert controls["delta"] == 2.0**-36 and controls["passed"] is True
    assert [r["component"] for r in controls["records"]] == list(range(4))
    for component, row in enumerate(controls["records"]):
        p, m, _ = field_values(row["field"], size)
        population_changes = [Fraction(0)] * 27
        if component == 0:
            population_changes[VELOCITIES.index((0, 0, 0))] = Fraction(1, 1 << 36) * size**3
        else:
            direction = tuple(int(i == component - 1) for i in range(3))
            population_changes[VELOCITIES.index(direction)] = Fraction(1, 1 << 36) * size**3
            population_changes[VELOCITIES.index(tuple(-v for v in direction))] = (
                -Fraction(1, 1 << 36) * size**3
            )
        assert [a - b for a, b in zip(p, populations, strict=True)] == population_changes
        expected = [Fraction(0)] * 4
        expected[component] = Fraction(1, 1 << (36 if component == 0 else 35))
        assert [(a - b) / size**3 for a, b in zip(m, moments, strict=True)] == expected
        assert list(map(rational, row["actual_site_average_change"])) == expected
        assert list(map(rational, row["expected_site_average_change"])) == expected
        assert max(map(abs, expected)) > TOLERANCE
        assert row["additions_exact"] is row["detected_violation"] is row["passed"] is True


def check_grid_case_values(saved, size, *, direction_count):
    grid = next(g for g in saved["evidence"]["grids"] if g["size"] == size)
    previous = next(
        g for g in runner.read_json(runner.PARENT_PATH)["cycle"]["grids"] if g["size"] == size
    )
    assert grid["status"] == "computed"
    assert grid["input_rebuild"] == previous["input_rebuild"] and grid["input_rebuild"]["passed"]
    assert grid["fiber_load"] == previous["fiber_load"] and grid["fiber_load"]["passed"]
    original = {
        (r["direction_index"], r["amplitude"]): r
        for r in previous["records"]
        if r["kind"] == "amplitude"
    }
    directions = np.random.default_rng(2026090725).standard_normal((32, 104))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    expected_specs = [
        {
            "kind": "amplitude",
            "direction_index": i,
            "amplitude": a,
            "a": (a * directions[i]).tolist(),
        }
        for i in range(direction_count)
        for a in (0.008, 0.032)
    ]
    assert [r["specification"] for r in grid["records"]] == expected_specs
    fields_count, comparison_count = 0, 0
    for row in grid["records"]:
        spec = row["specification"]
        old = original[spec["direction_index"], spec["amplitude"]]
        assert row["status"] == "computed" and row["original_record_reproduced"] is True
        assert row["original"] == old and row["original_record_digest_sha256"] == runner.digest(old)
        assert set(row["models"]) == {"2", "3"}
        for degree, data in row["models"].items():
            assert set(data["fields"]) == {"W", "Phi_W", "W_R"}
            values = {"baseline": field_values(grid["baseline"]["field"], size)}
            for name, field in data["fields"].items():
                assert field["array"] == old["models"][degree]["fields"][name]["array"]
                assert (
                    field["legacy_conserved_sums"]
                    == old["models"][degree]["fields"][name]["global_conserved_sums"]
                )
                values[name] = field_values(field, size)
                fields_count += 1
            assert set(data["comparisons"]) == {"W_leaf", "W_R_leaf", "Phi_conservation"}
            for name, a_name, b_name in (
                ("W_leaf", "W", "baseline"),
                ("W_R_leaf", "W_R", "baseline"),
                ("Phi_conservation", "Phi_W", "W"),
            ):
                _, sa, la = values[a_name]
                _, sb, lb = values[b_name]
                entries = data["comparisons"][name]
                assert [c["component"] for c in entries] == list(range(4))
                for i, c in enumerate(entries):
                    dl = old["models"][degree]["global_conservation_errors"][name][i]
                    el = old["models"][degree]["site_average_conservation_errors"][name][i]
                    dlq, elq = Fraction.from_float(dl), Fraction.from_float(el)
                    expected = {
                        "exact_field_error": (sa[i] - sb[i]) / size**3,
                        "sum_rounding_A": (la[i] - sa[i]) / size**3,
                        "sum_rounding_minus_B": (sb[i] - lb[i]) / size**3,
                        "sum_rounding": (la[i] - sa[i] - lb[i] + sb[i]) / size**3,
                        "sub_rounding": (dlq - la[i] + lb[i]) / size**3,
                        "mean_rounding": elq - dlq / size**3,
                    }
                    assert {k: rational(v) for k, v in c["terms"].items()} == expected
                    assert (
                        sum(
                            expected[k]
                            for k in (
                                "exact_field_error",
                                "sum_rounding",
                                "sub_rounding",
                                "mean_rounding",
                            )
                        )
                        == elq
                    )
                    assert dl == float(la[i]) - float(lb[i]) and el == dl / size**3
                    assert c["legacy_global_error"] == dl and c["legacy_site_average_error"] == el
                    assert c["legacy_passed"] == (abs(elq) <= TOLERANCE)
                    assert c["exact_field_error_passed"] == (
                        abs(expected["exact_field_error"]) <= TOLERANCE
                    )
                    assert c["identity_exact"] is True
                    for key, a in (
                        ("sum_only_counterfactual", float(sa[i])),
                        ("base_only_counterfactual", float(la[i])),
                    ):
                        if key == "base_only_counterfactual" and b_name != "baseline":
                            assert c[key] is None
                            continue
                        alternative = a - float(sb[i])
                        mean = alternative / size**3
                        assert c[key] == {
                            "global_error": alternative,
                            "site_average_error": mean,
                            "passed": abs(Fraction.from_float(mean)) <= TOLERANCE,
                        }
                    comparison_count += 1
    assert (fields_count, comparison_count) == (direction_count * 12, direction_count * 48)


@pytest.mark.parametrize("size", [17, 33, 65])
def test_all_48_old_cases_288_field_hashes_and_1152_signed_identities(saved, size):
    check_grid_case_values(saved, size, direction_count=8)


def test_every_child_and_all_saved_exact_values_are_in_final_worker(saved):
    for grid, entry in zip(saved["evidence"]["grids"], saved["grid_artifacts"], strict=True):
        path = PATH.with_name(f"{PATH.stem}_n{grid['size']}.json")
        assert entry["filename"] == path.name and entry["sha256"] == _file_sha256(path)
        child = runner.read_json(path)
        assert child["grid"] == grid and child["grid_digest_sha256"] == runner.digest(grid)
        assert child["process_id"] == saved["process_id"]
        assert runner.parent.source_equal(child, saved)
        assert entry["roundtrip_passed"] is True
        assert entry["full_saved_audit"] == {
            "passed": True,
            "cases": 16,
            "fields": 96,
            "population_sums": 2592,
            "component_comparisons": 384,
            "negative_controls": 4,
        }
    assert saved["summary"] == runner.summary(saved["evidence"]["grids"])
    assert saved["summary"]["legacy"]["components"] == 1152
    assert saved["summary"]["base_only"]["components"] == 768
    current = runner.metadata()
    assert runner.worker_readiness(
        saved,
        PATH,
        current,
        saved["evidence"]["input_audit"],
        saved["evidence"]["artificial_controls"],
        runner.read_json(runner.PARENT_PATH)["cycle"]["grids"],
    )["passed"]


def independent_failure_summary(grids):
    categories = ("legacy", "exact_field", "sum_only", "base_only")
    failures = {k: [] for k in categories}
    maxima = {k: Fraction(0) for k in categories}
    counts = dict.fromkeys(categories, 0)
    for grid in grids:
        for row in grid["records"]:
            spec = row["specification"]
            for degree, data in row["models"].items():
                for name, entries in data["comparisons"].items():
                    for c in entries:
                        values = {
                            "legacy": Fraction.from_float(c["legacy_site_average_error"]),
                            "exact_field": rational(c["terms"]["exact_field_error"]),
                            "sum_only": Fraction.from_float(
                                c["sum_only_counterfactual"]["site_average_error"]
                            ),
                        }
                        if c["base_only_counterfactual"] is not None:
                            values["base_only"] = Fraction.from_float(
                                c["base_only_counterfactual"]["site_average_error"]
                            )
                        for key, value in values.items():
                            counts[key] += 1
                            maxima[key] = max(maxima[key], abs(value))
                            if abs(value) > TOLERANCE:
                                failures[key].append(
                                    {
                                        "size": grid["size"],
                                        "direction_index": spec["direction_index"],
                                        "amplitude": spec["amplitude"],
                                        "degree": int(degree),
                                        "comparison": name,
                                        "component": c["component"],
                                        "site_average_error": {
                                            "numerator": str(value.numerator),
                                            "denominator": str(value.denominator),
                                            "float": float(value),
                                        },
                                    }
                                )
    return {
        key: {
            "components": counts[key],
            "maximum_absolute_site_average_error": float(maxima[key]),
            "failures": failures[key],
            "failed_components": len(failures[key]),
        }
        for key in categories
    }


def test_failure_summary_is_rebuilt_independently_from_every_component(saved):
    rebuilt = independent_failure_summary(saved["evidence"]["grids"])
    assert {k: v["components"] for k, v in rebuilt.items()} == {
        "legacy": 1152,
        "exact_field": 1152,
        "sum_only": 1152,
        "base_only": 768,
    }
    assert saved["summary"] == rebuilt
    # A first-eight-direction worker does not adjudicate the full 192-case H1.
    assert "scientific_outcome" not in saved and "hypothesis_gates" not in saved
    assert "Q012g rejection" in saved["claim_boundary"]


def test_independent_rational_reader_rejects_noncanonical_and_one_ulp_display():
    original = {"numerator": "1", "denominator": "3", "float": 1.0 / 3}
    assert rational(original) == Fraction(1, 3)
    for key, value in (
        ("numerator", "01"),
        ("denominator", "03"),
        ("float", np.nextafter(1.0 / 3, 1.0)),
    ):
        damaged = deepcopy(original)
        damaged[key] = value
        with pytest.raises(AssertionError):
            rational(damaged)
