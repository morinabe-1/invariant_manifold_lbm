"""Independent exact squared-norm checks of every saved precision column.

Fraction decodes finite binary values directly; it neither calls the GMP codec
nor the production norm/decision routines. This audits arithmetic on the saved
rounded inputs, not exact LBM coefficients or a bound on truncation error.
"""

import json
from contextlib import ExitStack
from fractions import Fraction
from math import isclose, sqrt
from zipfile import ZipFile

import numpy as np
import pytest

from research import q012h2a_d3q27_quartic_precision as run

OUTPUT = run.OUTPUT.with_name("q012h2a_d3q27_quartic_precision_attempt03.json")
COMPONENTS = ("forcing", "collision", "composition")
FLOOR_SQUARED = Fraction(1, 10**28)


def dyadic(pair):
    mantissa, exponent = pair
    assert type(mantissa) is str and type(exponent) is int
    value = int(mantissa)
    assert str(value) == mantissa and abs(exponent) <= 16384
    assert (value == 0 and exponent == 0) or value % 2 != 0
    return Fraction(value) * Fraction(2) ** exponent


def lossless_columns(record):
    assert set(record) == {"shape", "bits", "values"}
    rows, columns = record["shape"]
    assert rows == 27 and 0 < columns <= 16 and record["bits"] in (128, 192)
    assert len(record["values"]) == rows * columns
    flat = [tuple(dyadic(part) for part in value) for value in record["values"]]
    assert all(len(z) == 2 for z in flat)
    return [flat[j::columns] for j in range(columns)]


def binary64_columns(value):
    assert value.dtype == np.dtype("complex128") and np.isfinite(value).all()
    assert value.ndim == 2 and value.shape[0] == 27 and 0 < value.shape[1] <= 16
    return [
        [(Fraction(float(z.real)), Fraction(float(z.imag))) for z in value[:, j]]
        for j in range(value.shape[1])
    ]


def relative_squared(actual, reference):
    assert len(actual) == len(reference) > 0
    result = []
    for left, right in zip(actual, reference, strict=True):
        assert len(left) == len(right) == 27
        difference = sum(
            (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 for a, b in zip(left, right, strict=True)
        )
        denominator = max(FLOOR_SQUARED, sum(z[0] ** 2 + z[1] ** 2 for z in right))
        result.append(difference / denominator)
    return result


def verify_diagnostics(record, actual, reference):
    exact = relative_squared(actual, reference)
    for digits, name in ((8, "passed_1e8"), (10, "passed_1e10")):
        assert record[name] == [v <= Fraction(1, 10 ** (2 * digits)) for v in exact]
    assert len(record["relative"]) == len(exact)
    assert all(
        isclose(observed, sqrt(float(value)), rel_tol=3e-15, abs_tol=0)
        for observed, value in zip(record["relative"], exact, strict=True)
    )


def arrays(saved, name):
    with saved.open(name) as stream, np.load(stream, allow_pickle=False) as packed:
        return {key: packed[key] for key in packed.files}


@pytest.fixture(scope="module")
def manifest():
    assert (
        run.archive.file_sha(OUTPUT)
        == "e6a853b2176857e217570b26947096ea3325a55095815cdc9527a1b6c50d0189"
    )
    value = run.common.read_json(OUTPUT)
    run.common.unseal(value)
    assert run.same(value["source"], run.metadata())
    assert value["source_commit"] == "3ec22a16ac357e9f23017e25f8fc1d02b4b07fd5"
    run.oracle.verify_source_commit(value["source_commit"], value["source"])
    assert [g["size"] for g in value["grids"]] == [17, 33, 65]
    assert [g["columns"] for g in value["grids"]] == [1826] * 3
    return value


@pytest.mark.parametrize("size", [17, 33, 65])
def test_every_lossless_and_rounded_column_has_independent_exact_decisions(size, manifest):
    grid = next(row for row in manifest["grids"] if row["size"] == size)
    assert len(grid["comparisons"]) == 698
    count, old_failures = 0, 0
    with ExitStack() as stack:
        new = {
            route: stack.enter_context(ZipFile(run.read_grid(OUTPUT, size, route)[1]))
            for route in ("primary", "worker")
        }
        old = {
            route: stack.enter_context(
                ZipFile(run.parent.read_grid(run.parent.OUTPUT, size, route)[1])
            )
            for route in ("primary", "worker")
        }
        for ordinal, comparison in enumerate(grid["comparisons"]):
            name = f"tuple_{ordinal:04d}"
            documents = {route: json.loads(z.read(name + ".json")) for route, z in new.items()}
            stored = {route: arrays(z, name + ".npz") for route, z in new.items()}
            earlier = {route: arrays(z, name + ".npz") for route, z in old.items()}
            assert all(doc["group"] == comparison["group"] for doc in documents.values())
            assert all(
                np.array_equal(a["keys"], stored["primary"]["keys"])
                for a in (*stored.values(), *earlier.values())
            )
            assert comparison["columns"] == len(stored["primary"]["keys"])
            count += comparison["columns"]
            for component in COMPONENTS:
                high = {
                    route: {
                        bits: lossless_columns(doc["precision"][str(bits)][component])
                        for bits in (128, 192)
                    }
                    for route, doc in documents.items()
                }
                binary = {route: binary64_columns(a[component]) for route, a in earlier.items()}
                verify_diagnostics(
                    comparison["agreement_192"][component],
                    high["primary"][192],
                    high["worker"][192],
                )
                for route in new:
                    verify_diagnostics(
                        comparison["precision_stability"][route][component],
                        high[route][128],
                        high[route][192],
                    )
                    for bits in (128, 192):
                        for old_route in old:
                            verify_diagnostics(
                                comparison["old_to_high_precision"][
                                    f"{route}_{bits}_vs_{old_route}"
                                ][component],
                                binary[old_route],
                                high[route][bits],
                            )
                verify_diagnostics(
                    comparison["moment_only"][component],
                    binary64_columns(stored["primary"][f"moment_{component}"]),
                    high["primary"][192],
                )
                rounded = relative_squared(
                    binary64_columns(stored["primary"][f"rounded192_{component}"]),
                    binary64_columns(stored["worker"][f"rounded192_{component}"]),
                )
                assert [v <= Fraction(1, 10**16) for v in rounded] == [
                    v <= 1e-8 for v in comparison["rounded_agreement"][component]
                ]
                if component == "forcing":
                    original = relative_squared(binary["primary"], binary["worker"])
                    failed = [j for j, v in enumerate(original) if v > Fraction(1, 10**16)]
                    assert failed == comparison["original_failed_columns"]
                    old_failures += len(failed)
    assert count == 1826
    assert old_failures == {17: 182, 33: 174, 65: 158}[size]


def test_original_six_execution_receipts_and_unfinished_scope(manifest):
    run.verify_execution(OUTPUT, manifest["execution"])
    assert manifest["decision"]["original_H1_passed"] is False
    assert manifest["decision"]["q012h2_outcome"] == "not_evaluated"
    assert manifest["decision"]["H2"] == "not_evaluated"
    assert manifest["decision"]["H3_with_solves"] == "not_evaluated"


def test_all_saved_diagnostics_and_summary_rebuild(manifest):
    rebuilt = run.audit_manifest(OUTPUT, full=False)
    assert run.same(rebuilt["decision"], manifest["decision"])
    assert rebuilt["fresh_execution"] == []  # This is not a fresh-input CLI audit.


def test_rounded_population_values_agree_without_norm_underflow(manifest):
    count = 0
    for grid in manifest["grids"]:
        size = grid["size"]
        with (
            ZipFile(run.read_grid(OUTPUT, size, "primary")[1]) as left,
            ZipFile(run.read_grid(OUTPUT, size, "worker")[1]) as right,
        ):
            for ordinal in range(698):
                name = f"tuple_{ordinal:04d}.npz"
                a = arrays(left, name)["rounded192_forcing"]
                b = arrays(right, name)["rounded192_forcing"]
                assert np.array_equal(a, b)
                count += a.shape[1]
    assert count == 5478


def test_independent_cli_receipt_matches_the_observed_completed_audit(manifest):
    path = OUTPUT.with_name(OUTPUT.stem + "_fresh_audit.json")
    assert (
        run.archive.file_sha(path)
        == "e781d8760b0da4b61412f01767f72b52391f2acda6542fa034808ef042d93aa4"
    )
    receipt = run.common.read_json(path)
    assert receipt["observed_cli"]["process_id"] == 29016
    assert receipt["observed_cli"]["exit_code"] == 0
    assert receipt["manifest"] == {"filename": OUTPUT.name, "sha256": run.archive.file_sha(OUTPUT)}
    assert receipt["source_commit"] == manifest["source_commit"]
    assert receipt["audit_result"]["decision"] == manifest["decision"]
    fresh = receipt["audit_result"]["fresh_execution"]
    assert [row["process_id"] for row in fresh] == [27932, 10076, 28792, 5100, 37984, 28396]
    expected = [(size, route) for size in (17, 33, 65) for route in ("primary", "worker")]
    assert [(row["size"], row["route"]) for row in fresh] == expected
    for row in fresh:
        resource = row["completion_resources"]
        assert row["exit_code"] == 0 and resource["stage"] == "fresh_read_only_full_audit_complete"
        assert resource["new_file_bytes"] == 214820233  # Before the observer saved this receipt.
        assert all(resource["checks"].values())
        assert resource["checks"] == run.resources.limit_checks(
            resource, resource["wall_seconds"], resource["new_file_bytes"]
        )


@pytest.mark.parametrize(
    "pair,value", [(["0", 0], 0), (["-3", -2], Fraction(-3, 4)), (["5", 4], 80)]
)
def test_independent_dyadic_controls(pair, value):
    assert dyadic(pair) == value


@pytest.mark.parametrize("pair", [["0", 1], ["2", 0], ["01", 0], ["1", True]])
def test_independent_dyadic_rejects_noncanonical_values(pair):
    with pytest.raises(AssertionError):
        dyadic(pair)


def test_exact_squared_threshold_zero_floor_tail_and_complex_controls():
    zero = [[(Fraction(0), Fraction(0))] * 27]
    tiny = [[*zero[0][:-1], (Fraction(1, 10**22), Fraction(0))]]
    assert relative_squared(tiny, zero) == [Fraction(1, 10**16)]
    smaller = [[*zero[0][:-1], (Fraction(1, 10**22) - Fraction(1, 10**40), Fraction(0))]]
    larger = [[*zero[0][:-1], (Fraction(1, 10**22), Fraction(1, 10**40))]]
    assert relative_squared(smaller, zero)[0] < Fraction(1, 10**16)
    assert relative_squared(larger, zero)[0] > Fraction(1, 10**16)
    assert relative_squared(zero, zero) == [0]
    with pytest.raises(AssertionError):
        relative_squared(tiny, [zero[0][:-1]])


def test_independent_lossless_row_order_and_last_component():
    record = {
        "bits": 192,
        "shape": [27, 2],
        "values": [[["0", 0], ["0", 0]] for _ in range(54)],
    }
    record["values"][0] = [["1", 0], ["0", 0]]
    record["values"][-1] = [["-3", -2], ["5", -3]]
    decoded = lossless_columns(record)
    assert decoded[0][0] == (1, 0)
    assert decoded[1][-1] == (Fraction(-3, 4), Fraction(5, 8))
    zero = [[(Fraction(0), Fraction(0))] * 27] * 2
    assert relative_squared(zero, decoded) == [1, 1]
    record["values"].pop()
    with pytest.raises(AssertionError):
        lossless_columns(record)


@pytest.mark.parametrize("corruption", ["decision", "relative", "length"])
def test_independent_diagnostic_check_rejects_fabricated_results(corruption):
    reference = [[(Fraction(0), Fraction(0))] * 27]
    actual = [[*reference[0][:-1], (Fraction(1, 10**21), Fraction(0))]]
    record = {"relative": [1e-7], "passed_1e8": [False], "passed_1e10": [False]}
    verify_diagnostics(record, actual, reference)
    if corruption == "decision":
        record["passed_1e8"][-1] = True
    elif corruption == "relative":
        record["relative"][-1] = 0
    else:
        record["relative"].pop()
    with pytest.raises(AssertionError):
        verify_diagnostics(record, actual, reference)
