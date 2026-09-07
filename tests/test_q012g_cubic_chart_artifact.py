"""All-row audits of CLOSED Q012g main grids, not a fresh full-field rerun.

Pins are added only after a grid file closes. This audit does not turn a partial
campaign into three-grid acceptance or treat a failed scientific gate as bad data.
The separate worker replays 48 physical cases per grid, not all 416 cases.
"""

import re
from itertools import permutations, product

import numpy as np
import pytest

from research import d3q27 as d3
from research import q012g_d3q27_cubic_chart as runner
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

DIRECTORY = runner.foundation.ARTIFACT_DIRECTORY
CLOSED_GRIDS = {
    17: "369b471c53f01b8e3a88ae7451e5d93bdaef3c10345186b90e092cf27bb1e2e4",
    33: "d859b3ea1d39e9c3f3a9d07f03642b2fa95ea1b6e4b62eb87b266f04d31f63bc",
}
WORKER_SHA = "84e4d6f9ce241b0eab4a6eda380dbf242a83c084e4fc4bc872291bb48ef56891"
AMPLITUDES = (0.008, 0.004, 0.002, 0.001)
METHODS = ("W2", "W3", "R2", "R3", "Phi_W3")


def directions(seed, count):
    raw = np.random.default_rng(seed).standard_normal((count, 104))
    return raw / np.linalg.norm(raw, axis=1)[:, None]


def check_array(value, shape, dtype="<f8"):
    assert set(value) == {"shape", "dtype", "bytes", "sha256"}
    assert value["shape"] == list(shape) and value["dtype"] == dtype
    assert value["bytes"] == int(np.prod(shape)) * np.dtype(dtype).itemsize
    assert re.fullmatch("[0-9a-f]{64}", value["sha256"])


def check_realness(value):
    assert value["real_norm"] >= 0 and value["imaginary_norm"] >= 0
    assert value["scaled_imaginary_norm"] == value["imaginary_norm"] / max(1, value["real_norm"])
    assert value["passed"] == (value["imaginary_norm"] <= 1e-9 * max(1, value["real_norm"]))
    assert value["passed"]  # Real-valued fields may only be returned after this check.


@pytest.fixture(scope="module")
def worker():
    path = DIRECTORY / "q012g_d3q27_cubic_chart_replay.json"
    assert _file_sha256(path) == WORKER_SHA
    result = runner.prior.read_json(path)
    assert runner.foundation._digest(result["evidence"]) == result["evidence_digest_sha256"]
    assert result["source_unchanged_after"] and _all_numeric_values_finite(result)
    return result


@pytest.fixture(scope="module", params=tuple(CLOSED_GRIDS), ids=lambda n: f"n{n}")
def grid(request):
    path = DIRECTORY / f"q012g_d3q27_cubic_chart_n{request.param}.json"
    assert _file_sha256(path) == CLOSED_GRIDS[request.param]
    document = runner.prior.read_json(path)
    assert document["kind"] == "Q012g grid evidence"
    assert document["grid_digest_sha256"] == runner.foundation._digest(document["grid"])
    assert runner.source_equal(document, runner.metadata())
    assert _all_numeric_values_finite(document)
    assert document["grid"]["size"] == request.param
    # roundtrip_passed is added to the parent, never silently inserted in the child.
    assert "roundtrip_passed" not in document["grid"]
    return document


def test_sealed_inputs_and_all_48_fresh_worker_cases(grid, worker):
    g = grid["grid"]
    assert runner.source_equal(grid, worker) and grid["process_id"] != worker["process_id"]
    old = runner.prior.read_json(runner.PRIOR_PATH)
    original = next(row for row in old["cycle"]["grids"] if row["size"] == g["size"])
    assert g["input_rebuild"] == original["input_rebuild"] and g["input_rebuild"]["passed"]
    assert g["fiber_load"]["entries"] == original["fiber_archive"]["entries"]
    assert g["fiber_load"]["sha256"] == original["fiber_archive"]["sha256"]
    assert g["fiber_load"]["passed"]
    reference = next(row for row in worker["evidence"]["grids"] if row["size"] == g["size"])
    assert {k: g[k] for k in ("size", "input_rebuild", "fiber_load")} == {
        k: reference[k] for k in ("size", "input_rebuild", "fiber_load")
    }
    replayed = [
        row
        for row in g["records"]
        if row["kind"] in ("order", "amplitude") and row["direction_index"] < 8
    ]
    assert len(replayed) == 48 and replayed == reference["records"]


def test_all_416_registered_coordinates_and_full_diagnostic_coverage(grid):
    g = grid["grid"]
    specs = []
    for kind, seed, count, ladder in (
        ("order", 2026090724, 64, AMPLITUDES),
        ("amplitude", 2026090725, 32, (0.008, 0.032)),
    ):
        for index, direction in enumerate(directions(seed, count)):
            for amplitude in ladder:
                specs.append(
                    {
                        "kind": kind,
                        "direction_index": index,
                        "amplitude": amplitude,
                        "a": (amplitude * direction).tolist(),
                    }
                )
    positive_waves = [
        w for w in product((-1, 0, 1), repeat=3) if any(w) and next(v for v in w if v) > 0
    ]
    for wave in ((1, 0, 0), (1, 1, 0), (1, 1, 1)):
        for component in range(8):
            axis = 8 * positive_waves.index(wave) + component
            for amplitude in AMPLITUDES:
                a = np.zeros(104)
                a[axis] = amplitude
                specs.append(
                    {
                        "kind": "special",
                        "wave": list(wave),
                        "real_component": component,
                        "amplitude": amplitude,
                        "a": a.tolist(),
                    }
                )
    assert len(g["records"]) == len(specs) == 416
    for row, spec in zip(g["records"], specs, strict=True):
        assert {k: row[k] for k in spec} == spec
    assert runner.coverage(g, worker=False) and runner.diagnostic_coverage(g)


def check_physical_rows(g):
    size = g["size"]
    base = d3.uniform_equilibrium((size,) * 3, np.zeros(4))
    base_sums = d3.global_conserved_quantities(base)
    floor = float(100 * np.finfo(float).eps * max(1, np.linalg.norm(base)))
    del base
    for row in g["records"]:
        assert row["finite"] and set(row["models"]) == {"2", "3"}
        assert row["roundoff_floor"] == floor
        resolved = all(v["defect_norm"] > floor for v in row["models"].values())
        ratio = (
            row["models"]["3"]["defect_norm"] / row["models"]["2"]["defect_norm"]
            if resolved
            else None
        )
        assert row["resolved"] == resolved and row["cubic_to_quadratic_defect_ratio"] == ratio
        for degree in (2, 3):
            value = row["models"][str(degree)]
            assert value["status"] == "computed" and value["degree"] == degree
            check_array(value["defect_array"], (size, size, size, 27))
            assert value["defect_norm"] >= 0 and len(value["reduced_coordinates"]) == 104
            assert set(value["fields"]) == {"W", "Phi_W", "W_R"}
            for field in value["fields"].values():
                check_array(field["array"], (size, size, size, 27))
                assert field["finite"] and field["norm"] >= 0 and field["perturbation_norm"] >= 0
                assert field["maximum_local_density_deviation"] >= 0
                assert len(field["global_conserved_sums"]) == 4
            assert value["positive"] == all(
                f["minimum_population"] > 0 for f in value["fields"].values()
            )
            sums = {k: np.asarray(v["global_conserved_sums"]) for k, v in value["fields"].items()}
            errors = {
                "W_leaf": sums["W"] - base_sums,
                "W_R_leaf": sums["W_R"] - base_sums,
                "Phi_conservation": sums["Phi_W"] - sums["W"],
            }
            assert value["global_conservation_errors"] == {k: v.tolist() for k, v in errors.items()}
            means = {k: v / size**3 for k, v in errors.items()}
            assert value["site_average_conservation_errors"] == {
                k: v.tolist() for k, v in means.items()
            }
            assert value["maximum_site_average_conservation_error"] == max(
                float(np.max(np.abs(v))) for v in means.values()
            )
            for name in ("W", "W_R"):
                check_realness(value["realification"][name])
            internal = value["realification"]["R"]["cubic_realification"]
            assert (internal is None) == (degree == 2)
            if internal is not None:
                check_realness(internal)
        expected = (
            bool(
                resolved
                and ratio <= 0.5
                and all(
                    v["positive"] and v["maximum_site_average_conservation_error"] <= 5e-13
                    for v in row["models"].values()
                )
            )
            if row["kind"] == "amplitude"
            else None
        )
        assert row["amplitude_passed"] == expected


def test_every_full_map_row_and_all_four_conservation_components(grid):
    check_physical_rows(grid["grid"])


def check_fits(g):
    x = np.log(AMPLITUDES)
    centered_x = x - x.mean()
    for name, kind, count in (("generic_fits", "order", 64), ("special_fits", "special", 24)):
        assert len(g[name]) == count
        keys = (
            list(range(64))
            if kind == "order"
            else [[list(w), c] for w in ((1, 0, 0), (1, 1, 0), (1, 1, 1)) for c in range(8)]
        )
        for fit, key in zip(g[name], keys, strict=True):
            assert fit["direction_key"] == key
            rows = [
                r
                for r in g["records"]
                if r["kind"] == kind
                and (
                    r["direction_index"] == key
                    if kind == "order"
                    else r["wave"] == key[0] and r["real_component"] == key[1]
                )
            ]
            assert fit["complete"] and len(rows) == 4
            assert tuple(r["amplitude"] for r in rows) == AMPLITUDES
            resolved = all(r["resolved"] for r in rows)
            assert fit["resolved"] == resolved
            if resolved:
                for degree in (2, 3):
                    y = np.log([r["models"][str(degree)]["defect_norm"] for r in rows])
                    slope = np.dot(centered_x, y - y.mean()) / np.dot(centered_x, centered_x)
                    np.testing.assert_allclose(
                        fit["slopes"][str(degree)], slope, atol=1e-12, rtol=0
                    )
                assert (
                    fit["smallest_amplitude_ratio"] == rows[-1]["cubic_to_quadratic_defect_ratio"]
                )
            else:
                assert fit["slopes"] == {"2": None, "3": None}
                assert fit["smallest_amplitude_ratio"] is None
            if kind == "special":
                assert fit["passed"] is None and fit["scope"] == "diagnostic only"
            else:
                expected = bool(
                    resolved
                    and 2.9 <= fit["slopes"]["2"] <= 3.1
                    and 3.9 <= fit["slopes"]["3"] <= 4.1
                    and fit["smallest_amplitude_ratio"] <= 0.1
                )
                assert fit["passed"] == expected and fit["scope"] == "registered generic gate"


def test_all_64_generic_and_24_diagnostic_fits_are_rederived(grid):
    check_fits(grid["grid"])


def check_direction_phase(phase, seed, count, key="directions"):
    assert phase["status"] == "computed" and phase["seed"] == seed
    assert phase[key] == directions(seed, count).tolist()


def test_independent_evaluation_errors_and_all_field_witnesses(grid):
    g = grid["grid"]
    phase = g["evaluation"]
    check_direction_phase(phase, 2026090723, 8)
    assert len(phase["records"]) == 8
    for i, row in enumerate(phase["records"]):
        assert row["direction_index"] == i
        assert set(row["errors"]) == {
            "cubic_H3_direct_sum",
            "cubic_G3_manual_realification",
            "paired_H2_loop",
            "paired_G2_loop",
            "paired_G2_real_hessian",
        }
        assert all(v >= 0 for v in row["errors"].values())
        assert row["passed"] == (max(row["errors"].values()) <= 1e-10)
        for value in row["realification"].values():
            check_realness(value)
        assert set(row["realification"]) == {"grouped", "manual"}
        shapes = {
            **{
                k: ((g["size"],) * 3 + (27,), "<c16")
                for k in ("actual_h", "reference_h", "pair_h", "fiber_h")
            },
            **{k: ((104,), "<f8") for k in ("actual_g", "manual_g", "dense_g")},
            **{k: ((104,), "<c16") for k in ("reference_complex_g", "pair_g", "fiber_g")},
        }
        assert row["fields"].keys() == shapes.keys()
        for name, (shape, dtype) in shapes.items():
            check_array(row["fields"][name], shape, dtype)
    assert phase["passed"] == all(r["passed"] for r in phase["records"])


def test_all_112_homogeneity_witnesses_and_separate_complex_support(grid):
    phase = grid["grid"]["homogeneity"]
    check_direction_phase(phase, 2026090723, 8, "generic_directions")
    assert len(phase["records"]) == 112
    for i, row in enumerate(phase["records"]):
        assert row["kind"] == ("generic" if i < 8 else "coordinate_axis")
        assert row["direction_index"] == (i if i < 8 else i - 8)
        assert set(row["errors"]) == {"H3_odd", "H3_cubic", "G3_odd", "G3_cubic"}
        assert all(v >= 0 for v in row["errors"].values())
        assert row["passed"] == (max(row["errors"].values()) <= 1e-12)
        assert set(row["fields"]) == {"H3", "G3"}
        for name, shape in (("H3", (343, 27)), ("G3", (26, 4))):
            assert set(row["fields"][name]) == {"reference", "negative", "doubled"}
            for value in row["fields"][name].values():
                check_array(value, shape, "<c16")
    assert phase["passed"] == all(r["passed"] for r in phase["records"])


def test_independent_physical_identity_and_fixed_leaf_structure(grid):
    g = grid["grid"]
    phase, size = g["physical_structure"], g["size"]
    check_direction_phase(phase, 2026090723, 8)
    assert len(phase["records"]) == 8
    for i, row in enumerate(phase["records"]):
        assert row["direction_index"] == i
        assert set(row["realification"]) == {"H3", "G3"}
        for value in row["realification"].values():
            check_realness(value)
        assert set(row["structural_errors"]) == {"graph_gauge", "zero_wave_conserved_moment"}
        assert (
            len(row["global_H3_conserved_sums"]) == len(row["zero_wave_H3_conserved_moments"]) == 4
        )
        moments = np.asarray(row["global_H3_conserved_sums"])
        np.testing.assert_array_equal(row["zero_wave_H3_conserved_moments"], moments / size**1.5)
        expected = (
            np.linalg.norm(moments) / size**1.5 / max(1, row["realification"]["H3"]["real_norm"])
        )
        assert row["structural_errors"]["zero_wave_conserved_moment"] == expected
        assert all(v >= 0 for v in row["structural_errors"].values())
        assert row["structure_passed"] == (max(row["structural_errors"].values()) <= 1e-9)
        assert (
            row["forcing_relative_error"] >= 0 and row["physical_homological_relative_error"] >= 0
        )
        assert row["physics_passed"] == (
            row["forcing_relative_error"] <= 1e-8
            and row["physical_homological_relative_error"] <= 1e-9
        )
        assert set(row["fields"]) == {
            "h",
            "g",
            "gauge",
            "contracted_forcing",
            "direct_forcing",
            "homological_defect",
        }
        for name, value in row["fields"].items():
            shape = (104,) if name in ("g", "gauge") else (size, size, size, 27)
            check_array(value, shape, "<c16" if name == "contracted_forcing" else "<f8")
    for name in ("structure_passed", "physics_passed"):
        assert phase[name] == all(r[name] for r in phase["records"])


def test_all_48_signed_permutations_per_direction(grid):
    g = grid["grid"]
    phase = g["symmetry"]
    check_direction_phase(phase, 2026090726, 4)
    # Independent construction of the complete signed-permutation group.
    rotations = [
        np.diag(signs) @ np.eye(3, dtype=int)[list(axes)]
        for axes in permutations(range(3))
        for signs in product((-1, 1), repeat=3)
    ]
    assert len(phase["records"]) == 192
    for ordinal, row in enumerate(phase["records"]):
        i, r = divmod(ordinal, 48)
        assert (row["direction_index"], row["rotation_index"]) == (i, r)
        assert row["rotation"] == rotations[r].tolist()
        assert set(row["errors"]) == set(row["realification"]) == {"H3", "G3"}
        assert all(v >= 0 for v in row["errors"].values())
        assert row["passed"] == (max(row["errors"].values()) <= 1e-8)
        for value in row["realification"].values():
            check_realness(value)
        assert set(row["fields"]) == {"actual_h", "reference_h", "actual_g", "reference_g"}
        for name, value in row["fields"].items():
            check_array(value, (104,) if name.endswith("_g") else (g["size"],) * 3 + (27,))
    assert phase["passed"] == all(r["passed"] for r in phase["records"])


def check_timing(g):
    phase = g["timing"]
    check_direction_phase(phase, 2026090727, 8)
    assert phase["amplitude"] == 0.008
    assert len(phase["warmups"]) == 15 and len(phase["records"]) == 440
    expected = [
        (r, i, method)
        for r in range(11)
        for i in range(8)
        for method in (METHODS if r % 2 == 0 else METHODS[::-1])
    ]
    references = {}
    for row, key in zip(phase["records"], expected, strict=True):
        r, i, method = key
        assert (row["repetition"], row["direction_index"], row["method"]) == key
        check_array(row["output"], (104,) if method.startswith("R") else (g["size"],) * 3 + (27,))
        assert row["wall_seconds"] >= 0 and row["output_norm"] >= 0 and row["finite"]
        reference = references.setdefault((i, method), (row["output"], row["output_norm"]))
        assert row["same_output"] and reference == (row["output"], row["output_norm"])
    for row, (r, method) in zip(phase["warmups"], product(range(3), METHODS), strict=True):
        assert (row["repetition"], row["method"]) == (r, method)
        assert row["output"] == references[(r, method)][0]
    assert phase["median_wall_seconds"] == {
        method: float(
            np.median([r["wall_seconds"] for r in phase["records"] if r["method"] == method])
        )
        for method in METHODS
    }
    assert phase["valid"] and "no timing threshold" in phase["scope"]


def test_all_440_cost_samples_warmups_output_identity_and_medians(grid):
    check_timing(grid["grid"])


def test_coefficient_index_preparation_and_reachable_memory_scopes(grid):
    g = grid["grid"]
    cost = g["offline_cost"]
    assert all(
        cost[k] > 0
        for k in (
            "fresh_quadratic_rebuild_seconds",
            "cubic_archive_load_and_audit_seconds",
            "cubic_evaluator_preparation_seconds",
        )
    )
    entries = g["fiber_load"]["entries"]
    assert (
        cost["cubic_original_array_bytes"] == sum(v["bytes"] for v in entries.values()) == 188289920
    )
    assert cost["cubic_original_coefficient_bytes"] == sum(
        entries[k]["bytes"] for k in ("response", "forcing", "reduced")
    )
    assert cost["cubic_original_sparse_index_bytes"] == sum(
        entries[k]["bytes"] for k in ("input_triples", "output_waves")
    )
    previous = runner.prior.read_json(runner.PRIOR_PATH)
    old = next(row for row in previous["cycle"]["grids"] if row["size"] == g["size"])
    assert cost["cubic_serialized_bytes"] == old["fiber_archive"]["bytes"]
    prepared = cost["prepared_cubic_buffers"]
    assert set(prepared["engines"]) == {"response", "forcing", "internal"}
    for name, engine in prepared["engines"].items():
        rows, outputs, width = (61008, 26, 4) if name == "internal" else (192920, 343, 27)
        assert engine["degree"] == 3 and engine["monomial_rows"] == rows
        assert engine["coefficient_scalars"] == rows * width
        arrays = engine["prepared_arrays"]
        assert set(arrays) == {"indices", "coefficients", "starts", "outputs"}
        check_array(arrays["indices"], (rows, 3), "<i8")
        check_array(arrays["coefficients"], (rows, width), "<c16")
        for key in ("starts", "outputs"):
            check_array(arrays[key], (outputs,), "<i8")
        assert engine["coefficient_bytes"] == arrays["coefficients"]["bytes"]
        assert engine["sparse_index_bytes"] == sum(
            arrays[k]["bytes"] for k in ("indices", "starts", "outputs")
        )
    assert prepared["coefficient_bytes"] == sum(
        e["coefficient_bytes"] for e in prepared["engines"].values()
    )
    # Own both the signed wave table and its three modulo-grid coordinate arrays.
    assert (
        prepared["sparse_index_bytes"]
        == sum(e["sparse_index_bytes"] for e in prepared["engines"].values())
        + (343 * 3 + 3 * 343) * 8
    )
    inventory = cost["resident_numpy_buffers"]
    assert inventory["bytes"] == sum(v["bytes_added"] for v in inventory["groups"].values())
    assert inventory["unique_buffers"] == sum(
        v["unique_buffers_added"] for v in inventory["groups"].values()
    )
    assert (
        inventory["groups"]["cubic_prepared"]["bytes_added"]
        == prepared["coefficient_bytes"] + prepared["sparse_index_bytes"]
    )
    assert (
        inventory["groups"]["original_cubic_archives"]["bytes_added"]
        == cost["cubic_original_array_bytes"]
    )
    assert (
        "allocator overhead" in inventory["scope"]
        and "not a claimed total RSS" in cost["memory_scope"]
    )


@pytest.mark.parametrize("mutation", ("ratio_gate", "slope", "timing_hash"))
def test_saved_value_auditors_reject_corruption(mutation):
    # Fresh JSON object: do not mutate the shared fixture or any saved artifact.
    g = runner.prior.read_json(DIRECTORY / "q012g_d3q27_cubic_chart_n17.json")["grid"]
    if mutation == "ratio_gate":
        row = next(r for r in g["records"] if r["kind"] == "amplitude")
        row["amplitude_passed"] = not row["amplitude_passed"]
        audit = check_physical_rows
    elif mutation == "slope":
        g["generic_fits"][0]["slopes"]["3"] += 0.01
        audit = check_fits
    else:
        g["timing"]["records"][40]["output"]["sha256"] = "0" * 64
        audit = check_timing
    with pytest.raises(AssertionError):
        audit(g)
