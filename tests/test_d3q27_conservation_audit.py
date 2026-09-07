"""Exact arithmetic controls; no real candidate LBM campaign is run here."""

from copy import deepcopy
from fractions import Fraction

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_conservation_audit as audit


def reference(values):
    return sum((Fraction.from_float(float(x)) for x in np.ravel(values)), Fraction(0))


@pytest.mark.parametrize("backend", audit.BACKENDS)
@pytest.mark.parametrize("count", [0, 1, 1023, 1024, 1025, 2049])
def test_chunk_limits_with_maximum_signed_mantissas(backend, count):
    maximum = np.finfo(np.float64).max
    values = np.full(count, maximum)
    assert audit.exact_sum(values, backend=backend) == reference(values)
    assert audit.exact_sum(-values, backend=backend) == -reference(values)
    values = np.concatenate((values, -values, [np.nextafter(0.0, 1.0)]))
    assert audit.exact_sum(values, backend=backend) == reference(values)


@pytest.mark.parametrize("backend", audit.BACKENDS)
def test_all_finite_exponent_bins_strides_signed_zero_and_single_ulp(backend):
    rng = np.random.default_rng(213)
    mantissas = rng.integers(0, 1 << 52, size=2047, dtype=np.uint64)
    bits = (np.arange(2047, dtype=np.uint64) << 52) | mantissas
    signs = rng.integers(0, 2, size=2047, dtype=np.uint64) << 63
    values = (bits | signs).view(np.float64)
    assert audit.exact_sum(values, backend=backend) == reference(values)
    assert audit.exact_sum(values[::3], backend=backend) == reference(values[::3])
    assert audit.exact_sum(np.array([0.0, -0.0]), backend=backend) == 0
    assert audit.exact_sum(np.array([1.0, -1.0]), backend=backend) == 0
    changed = np.array([np.nextafter(1.0, 2.0), -1.0])
    assert audit.exact_sum(changed, backend=backend) == Fraction(1, 1 << 52)
    assert audit.exact_sum(changed, backend=backend) != 0


@pytest.mark.parametrize("backend", audit.BACKENDS)
@pytest.mark.parametrize("dtype", [np.float32, np.int64, np.complex128, bool, ">f8"])
def test_no_implicit_input_conversion(backend, dtype):
    with pytest.raises(TypeError):
        audit.exact_sum(np.ones(5, dtype=dtype), backend=backend)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_values_and_unknown_backends_are_rejected(value):
    for backend in audit.BACKENDS:
        with pytest.raises(ValueError):
            audit.exact_sum(np.array([value]), backend=backend)
    with pytest.raises(ValueError):
        audit.exact_sum(np.array([1.0]), backend="numpy")


def test_artificial_reference_controls_and_exact_threshold():
    controls = audit.artificial_controls()
    assert controls["passed"] and len(controls["sums"]) == 11
    assert len(controls["rejections"]) == 6
    assert audit.decode(controls["threshold"]) == Fraction.from_float(5e-13)
    assert audit.THRESHOLD != Fraction("5e-13")


@pytest.mark.parametrize("value", [Fraction(0), Fraction(-7, 93), Fraction(1, 1 << 1074)])
def test_canonical_rational_serialization(value):
    encoded = audit.encode(value)
    assert audit.decode(encoded) == value
    for key, replacement in (
        ("numerator", "0" + encoded["numerator"]),
        ("denominator", "0"),
        ("denominator", "-1"),
        ("float", np.nextafter(encoded["float"], np.inf)),
        ("float", True),
        ("numerator", 0),
    ):
        damaged = {**encoded, key: replacement}
        with pytest.raises((ValueError, TypeError)):
            audit.decode(damaged)
    with pytest.raises(ValueError):
        audit.decode({**encoded, "extra": 0})
    with pytest.raises(ValueError):
        audit.encode(Fraction(1 << 1100))


@pytest.fixture
def field():
    return np.broadcast_to(d3.WEIGHTS, (2, 3, 5, 27)).copy()


def test_full_population_and_moment_witnesses_match_independent_site_loops(field):
    rng = np.random.default_rng(318)
    field += 0.001 * rng.standard_normal(field.shape)
    record = audit.field_record(field)
    assert record == audit.field_record(field, backend="gmp")
    assert audit.validate_field_record(record)
    populations = [reference(field[..., q]) for q in range(27)]
    for i, saved in enumerate(record["conserved_sums"]):
        expected = sum(
            (int(c) * s for c, s in zip(audit.MOMENTS[i], populations, strict=True)), Fraction(0)
        )
        assert audit.decode(saved) == expected
    assert record["coverage"] == {"populations": 27, "sites_per_population": 30, "values": 810}


@pytest.mark.parametrize(
    "damage", ["sum", "coverage", "rounding", "shape", "missing_population", "hash"]
)
def test_saved_field_corruption_is_not_accepted(field, damage):
    row = audit.field_record(field)
    if damage == "sum":
        row["population_sums"][0] = audit.encode(audit.decode(row["population_sums"][0]) + 1)
    elif damage == "coverage":
        row["coverage"]["values"] -= 1
    elif damage == "rounding":
        row["sum_rounding"][0] = audit.encode(Fraction(2))
    elif damage == "shape":
        row["array"]["shape"][0] += 1
    elif damage == "missing_population":
        row["population_sums"].pop()
    else:
        row["array"]["sha256"] = "invalid"
    with pytest.raises(ValueError):
        audit.validate_field_record(row)


def test_signed_decomposition_rounds_each_original_operation_and_keeps_counterfactuals():
    sa, sb = Fraction(1), Fraction(1, 1 << 55)
    la, lb, sites = 1.0, 2.0**-54, 3
    dl = float(np.float64(la) - np.float64(lb))
    el = float(np.float64(dl) / sites)
    row = audit.decompose_component(sa, sb, la, lb, dl, el, sites, leaf=True)
    terms = {k: audit.decode(v) for k, v in row["terms"].items()}
    assert sum(
        terms[k] for k in ("exact_field_error", "sum_rounding", "sub_rounding", "mean_rounding")
    ) == Fraction.from_float(el)
    assert terms["sum_rounding"] == terms["sum_rounding_A"] + terms["sum_rounding_minus_B"]
    assert terms["sub_rounding"] != 0 and terms["mean_rounding"] != 0
    assert row["identity_exact"] and not row["exact_field_error_passed"]
    assert row["base_only_counterfactual"] is not None
    nonleaf = audit.decompose_component(sa, sb, la, lb, dl, el, sites, leaf=False)
    assert nonleaf["base_only_counterfactual"] is None
    for incorrect_dl, incorrect_el in ((np.nextafter(dl, 2.0), el), (dl, np.nextafter(el, 2.0))):
        with pytest.raises(ValueError):
            audit.decompose_component(sa, sb, la, lb, incorrect_dl, incorrect_el, sites, leaf=True)


def test_threshold_is_inclusive_without_erasing_one_ulp_violation():
    for error, passed in ((5e-13, True), (np.nextafter(5e-13, np.inf), False)):
        row = audit.decompose_component(
            Fraction.from_float(error), Fraction(0), error, 0.0, error, error, 1, leaf=True
        )
        assert row["exact_field_error_passed"] is passed
        assert row["legacy_passed"] is passed
        assert row["sum_only_counterfactual"]["passed"] is passed


def test_all_four_negative_controls_detect_exact_violation_and_preserve_baseline(field):
    original = field.copy()
    baseline = audit.baseline_record(field, backend="integer")
    assert baseline == audit.baseline_record(field, backend="gmp")
    first = audit.negative_controls(field, baseline, backend="integer")
    assert first == audit.negative_controls(field, baseline, backend="gmp")
    assert first["passed"] and [r["component"] for r in first["records"]] == list(range(4))
    for i, row in enumerate(first["records"]):
        actual = [audit.decode(v) for v in row["actual_site_average_change"]]
        assert actual[i] == Fraction.from_float(audit.DELTA) * (1 if i == 0 else 2)
        assert all(v == 0 for j, v in enumerate(actual) if j != i)
        assert row["detected_violation"] and row["additions_exact"] and row["passed"]
    np.testing.assert_array_equal(field, original)
    damaged = deepcopy(baseline)
    damaged["field"]["array"]["sha256"] = "0" * 64
    with pytest.raises(ValueError):
        audit.negative_controls(field, damaged, backend="integer")
    field[1, 2, 4, 13] += 1e-8
    with pytest.raises(ValueError):
        audit.negative_controls(
            field, audit.baseline_record(field, backend="integer"), backend="integer"
        )


@pytest.mark.parametrize("shape", [(1, 1, 27), (1, 1, 1, 9), (0, 1, 1, 27)])
def test_field_shape_is_checked(shape):
    with pytest.raises(ValueError):
        audit.field_record(np.ones(shape))
