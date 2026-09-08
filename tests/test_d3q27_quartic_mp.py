"""Artificial arithmetic controls; these are not real-pilot validity receipts."""

from copy import deepcopy
from itertools import combinations_with_replacement, permutations
from math import factorial

import gmpy2 as mp
import numpy as np
import pytest
from scipy.linalg import block_diag

from research import d3q27 as lattice
from research import d3q27_quartic_lbm as old
from research import d3q27_quartic_mp as primary
from research import d3q27_quartic_mp_numbers as numbers
from research import d3q27_quartic_mp_reference as reference


def inventory(*, n=6, tiny=None):
    rng = np.random.default_rng(2026090901)
    waves = np.repeat(np.array([[-1, 0, 0], [0, 0, 0], [1, 0, 0]], dtype=np.int64), 2, axis=0)
    if n == 1:
        waves = np.zeros((1, 3), dtype=np.int64)
    indices = {
        degree: np.array(list(combinations_with_replacement(range(n), degree)), dtype=np.int64)
        for degree in (2, 3)
    }

    def random(shape):
        return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / 17

    width = 1 if n == 1 else 2
    h = {degree: random((len(ids), 27)) for degree, ids in indices.items()}
    g = {degree: random((len(ids), width)) for degree, ids in indices.items()}
    for degree, ids in indices.items():
        output = waves[ids].sum(axis=1)
        g[degree][np.abs(output[:, 0]) > 1] = 0
    basis = random((27, n))
    linear = block_diag(*(np.array([[0.6 + 0.1j, 0.3], [0, 0.7 - 0.1j]]) for _ in range(3)))
    if n == 1:
        linear = np.array([[0.6 + 0.1j]])
    if tiny is not None:
        assert n == 1
        basis[:] = 0
        basis[[0, 1, 3, 4], 0] = (1, -1, -1, 1)
        basis[2, 0] = tiny
        for mapping in (h, g):
            for value in mapping.values():
                value[:] = 0
    return {
        "size": 9,
        "omega": 1.5,
        "eta": 0.02,
        "power": 2,
        "waves": waves,
        "basis": basis,
        "linear": linear,
        "indices": indices,
        "h": h,
        "g": g,
    }


@pytest.fixture(scope="module")
def data():
    return old.TaylorData(**inventory())


def relative(actual, expected):
    """No absolute floor in artificial tiny-nonzero arithmetic controls."""
    numerator = numbers.norm(np.asarray(actual).ravel() - np.asarray(expected).ravel())
    denominator = numbers.norm(np.asarray(expected).ravel())
    if denominator == 0:
        return mp.mpfr(0) if numerator == 0 else mp.mpfr("inf")
    return numerator / denominator


@pytest.mark.parametrize("bits", numbers.PRECISIONS)
def test_binary64_exact_import_and_lossless_codec(bits):
    source = np.array([[0, 0.1 + 0.3j], [2**-100 + 2**100j, -3.7 - 1.1j]], dtype=complex)
    with numbers.context(bits):
        actual = numbers.exact64(source)
        for value, original in zip(actual.flat, source.flat, strict=True):
            assert mp.mpq(value.real) == mp.mpq(*float(original.real).as_integer_ratio())
            assert mp.mpq(value.imag) == mp.mpq(*float(original.imag).as_integer_ratio())
        actual[-1, -1] += mp.mpc(mp.mpfr(2) ** (-bits + 5), mp.mpfr(2) ** (-bits + 7))
        record = numbers.encode(actual, bits)
        decoded = numbers.decode(record)
        assert numbers.encode(decoded, bits) == record
        np.testing.assert_array_equal(decoded, actual)
        assert decoded[-1, -1] != numbers.exact64(numbers.rounded(decoded))[-1, -1]


@pytest.mark.parametrize(
    "change",
    ["missing", "shape", "bits", "nan", "even", "precision", "zero", "boolean", "extra", "huge"],
)
def test_codec_rejects_noncanonical_or_incomplete_values(change):
    with numbers.context(128):
        record = numbers.encode(numbers.exact64(np.ones((27, 2), dtype=complex)), 128)
    if change == "missing":
        record["values"].pop()
    elif change == "shape":
        record["shape"] = [27, 3]
    elif change == "bits":
        record["bits"] = 64
    elif change == "nan":
        record["values"][-1][-1] = ["nan", 0]
    elif change == "even":
        record["values"][-1][-1] = ["2", 0]
    elif change == "precision":
        record["values"][-1][-1] = [str(2**128 + 1), 0]
    elif change == "zero":
        record["values"][-1][-1] = ["0", 1]
    elif change == "boolean":
        record["values"][-1][-1] = ["1", True]
    elif change == "extra":
        record["extra"] = "unregistered"
    else:
        record["values"][-1][-1] = ["1", 1000000]
    with pytest.raises(ValueError):
        numbers.decode(record)


def test_full_column_diagnostics_detect_last_component_and_small_floor():
    with numbers.context(192):
        expected = numbers.exact64(np.ones((27, 16), dtype=complex))
        correct = numbers.errors(expected, expected)
        assert correct["passed_1e8"] == [True] * 16
        changed = expected.copy()
        changed[-1, -1] += 1j
        assert numbers.errors(changed, expected)["passed_1e8"] == [True] * 15 + [False]
        tiny = expected * mp.mpfr("1e-40")
        wrong = tiny.copy()
        wrong[-1, -1] += mp.mpc("1e-21")
        assert numbers.errors(wrong, tiny)["passed_1e8"] == [True] * 15 + [False]
    with pytest.raises(ValueError):
        numbers.errors(expected[:, :0], expected[:, :0])
    with pytest.raises(ValueError):
        numbers.errors(expected[:-1], expected[:-1])


def test_binary64_cannot_silently_enter_high_precision_diagnostics():
    values = np.ones((27, 2), dtype=complex)
    with pytest.raises(ValueError, match="context"):
        numbers.exact64(values)
    with numbers.context(192):
        with pytest.raises(ValueError, match="finite MP columns"):
            numbers.errors(values, values)
        with pytest.raises(ValueError, match="complex128"):
            numbers.exact64(values.real)
    with (
        mp.context(precision=192, real_prec=53, imag_prec=53),
        pytest.raises(ValueError, match="context"),
    ):
        numbers.exact64(values)


@pytest.mark.parametrize("bits", [53, 128.0, True])
def test_only_registered_integer_precision_is_accepted(bits):
    with pytest.raises(ValueError):
        numbers.context(bits)


@pytest.mark.parametrize("bits", numbers.PRECISIONS)
def test_nilpotent_factorial_and_inverse_are_independent_exact_arithmetic(bits):
    with numbers.context(bits):
        z = {1 << i: mp.mpc(1j) for i in range(4)}
        power = z
        for _ in range(3):
            power = reference.multiply(power, z)
        assert power == {15: mp.mpc(factorial(4))}
        density = {0: mp.mpc(1), **z}
        assert reference.multiply(density, reference.inverse_density(density)) == {0: mp.mpc(1)}


@pytest.mark.parametrize("bits", numbers.PRECISIONS)
def test_all_126_mixed_coefficients_and_seven_nonzero_terms(data, bits):
    with numbers.context(bits):
        maxima = [mp.mpfr(0)] * 7
        tolerance = mp.mpfr("1e-30" if bits == 128 else "1e-48")
        for slots in combinations_with_replacement(range(data.dimension), 4):
            terms = primary.raw_terms(primary.Inputs(data), slots)
            other = reference.raw_forcing(data, slots)
            for value, name in (
                (terms[:4].sum(axis=0), "collision"),
                (terms[4:].sum(axis=0), "composition"),
                (terms[:4].sum(axis=0) - terms[4:].sum(axis=0), "forcing"),
            ):
                assert relative(value, other[name]) < tolerance, (slots, name)
            maxima = [max(a, numbers.norm(b)) for a, b in zip(maxima, terms, strict=True)]
        assert all(value > mp.mpfr("1e-6") for value in maxima)


@pytest.mark.parametrize("bits", numbers.PRECISIONS)
@pytest.mark.parametrize("tiny", [0, 2.0**-80])
def test_exact_zero_and_tiny_nonzero_moments_have_distinct_forcing(bits, tiny):
    data = old.TaylorData(**inventory(n=1, tiny=tiny))
    with numbers.context(bits):
        inputs = primary.Inputs(data)
        moments = inputs.moment((0,))
        eps = mp.mpfr(tiny)
        assert list(moments) == [mp.mpc(eps * value) for value in (1, -1, -1, 1)]
        terms = primary.raw_terms(inputs, (0, 0, 0, 0))
        actual = terms[:4].sum(axis=0) - terms[4:].sum(axis=0)
        independent = reference.raw_forcing(data, (0, 0, 0, 0))["forcing"]
        if tiny == 0:
            assert all(v == 0 for v in actual) and all(v == 0 for v in independent)
        else:
            exact = np.array(
                [
                    mp.mpc(
                        12
                        * eps**4
                        * mp.mpfr(float(w))
                        * (9 * int(-c[0] - c[1] + c[2]) ** 2 - 9)
                        * mp.mpfr(1.5)
                        / mp.sqrt(mp.mpfr(data.size) ** 3) ** 3
                    )
                    for c, w in zip(lattice.VELOCITIES, lattice.WEIGHTS, strict=True)
                ],
                dtype=object,
            )
            assert numbers.norm(actual) > 0 and numbers.norm(independent) > 0
            assert relative(actual, exact) < mp.mpfr("1e-30")
            assert relative(independent, exact) < mp.mpfr("1e-30")
            assert relative(np.full(27, mp.mpc(0), dtype=object), exact) == 1


def test_raw_factor_applied_before_high_precision_moment_sum():
    source = inventory(n=1, tiny=0)
    source["h"][3][0, [0, 1, 3, 4]] = [0.1, 0.2, -0.3, -(2.0**-55)]
    source["h"][3][0, 2] = 2.0**-80
    data = old.TaylorData(**source)
    with numbers.context(192):
        value = primary.Inputs(data).moment((0, 0, 0))
        exact = primary.moments(numbers.exact64(data.h[3][0])) * 6
        np.testing.assert_array_equal(value, exact)
        assert value[0] == mp.mpc(6 * mp.mpfr(2) ** -80)
        assert primary.moments(numbers.exact64(data.h[3][0] * 6))[0] != value[0]


@pytest.mark.parametrize("groups", [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2)])
def test_orbit_normalization_and_precision_stability(data, groups):
    blocks = ((0, 1), (2, 3), (4, 5))
    previous = {}
    for bits in numbers.PRECISIONS:
        main = primary.group(data, groups, blocks, bits)
        other = reference.group(data, groups, blocks, bits)
        assert all(numbers.errors(main["forcing"], other["forcing"])["passed_1e10"])
        if previous:
            assert all(numbers.errors(previous["forcing"], main["forcing"])["passed_1e10"])
        previous = main
    for order in set(permutations(groups)):
        changed = reference.group(data, order, blocks, 192)
        assert all(numbers.errors(changed["forcing"], main["forcing"])["passed_1e10"])


def test_full_sixteen_columns_and_last_component():
    source = inventory()
    # Eight artificial coordinates: all-distinct four 2D blocks have 16 columns.
    n = 8
    source["waves"] = np.zeros((n, 3), dtype=np.int64)
    rng = np.random.default_rng(754)
    source["basis"] = (rng.standard_normal((27, n)) + 1j * rng.standard_normal((27, n))) / 17
    source["linear"] = np.diag(np.full(n, 0.7 + 0.1j))
    source["indices"] = {
        d: np.array(list(combinations_with_replacement(range(n), d)), dtype=np.int64)
        for d in (2, 3)
    }
    for name, width in (("h", 27), ("g", n)):
        source[name] = {
            d: (
                rng.standard_normal((len(ids), width)) + 1j * rng.standard_normal((len(ids), width))
            )
            / 17
            for d, ids in source["indices"].items()
        }
    data = old.TaylorData(**source)
    blocks = ((0, 1), (2, 3), (4, 5), (6, 7))
    actual = primary.group(data, (0, 1, 2, 3), blocks, 192)
    independent = reference.group(data, (0, 1, 2, 3), blocks, 192)
    assert actual["forcing"].shape == (27, 16)
    assert all(numbers.errors(actual["forcing"], independent["forcing"])["passed_1e10"])
    with numbers.context(192):
        tampered = actual["forcing"].copy()
        tampered[-1, -1] += 1
    assert not numbers.errors(tampered, independent["forcing"])["passed_1e8"][-1]


def test_input_external_internal_coordinates_and_no_hermitian_product(data):
    slots = (0, 0, 4, 5)
    source = inventory()
    for degree in (2, 3):
        zero = np.all(source["waves"][source["indices"][degree]].sum(axis=1) == 0, axis=1)
        source["g"][degree][zero] = 0
    truncated = old.TaylorData(**source)
    with numbers.context(192):
        correct = reference.raw_forcing(data, slots)["forcing"]
        wrong = primary.raw_terms(primary.Inputs(truncated), slots)
        assert relative(wrong[:4].sum(axis=0) - wrong[4:].sum(axis=0), correct) > mp.mpfr("1e-4")
        u = numbers.exact64(np.array([0.2, 0.3j, -0.4j, 0.7j], dtype=complex))
        assert relative(primary.b(u, u.conjugate()), primary.b(u, u)) > 1


@pytest.mark.parametrize("mutation", old.MUTATIONS)
def test_nonzero_mutation_witness(data, mutation):
    with numbers.context(192):
        errors = []
        for slots in ((0, 0, 0, 0), (0, 0, 2, 4), (0, 2, 4, 5)):
            terms = primary.raw_terms(primary.Inputs(data), slots, mutation=mutation)
            correct = reference.raw_forcing(data, slots)["forcing"]
            errors.append(relative(terms[:4].sum(axis=0) - terms[4:].sum(axis=0), correct))
        assert max(errors) > mp.mpfr("1e-8")


def test_reference_does_not_share_primary_arithmetic(data, monkeypatch):
    with numbers.context(192):
        expected = reference.raw_forcing(data, (0, 0, 2, 5))

        def forbidden(*args, **kwargs):
            raise AssertionError("reference used primary arithmetic")

        for name in ("raw_terms", "raw_factors", "block_product", "local_b", "local_c", "local_d"):
            monkeypatch.setattr(old, name, forbidden)
        for name in ("raw_terms", "moments", "b", "c", "d", "group"):
            monkeypatch.setattr(primary, name, forbidden)
        for name in ("derivative", "rows", "contract", "internal", "linear_argument"):
            monkeypatch.setattr(data, name, forbidden)
        actual = reference.raw_forcing(data, (0, 0, 2, 5))
        assert numbers.encode(actual["forcing"], 192) == numbers.encode(expected["forcing"], 192)


def test_moment_only_retains_binary64_formula_and_composition(data):
    slots = (0, 0, 2, 5)
    old_terms = old.raw_terms(data, slots)
    np.testing.assert_array_equal(primary.moment_only(data, slots, promote=False), old_terms)
    promoted = primary.moment_only(data, slots)
    assert promoted.dtype == np.dtype("complex128")
    np.testing.assert_array_equal(promoted[4:], old_terms[4:])
    stable = primary.group(data, (0, 0, 1, 2), ((0, 1), (2, 3), (4, 5)), 192)
    arm = primary.moment_group(data, (0, 0, 1, 2), ((0, 1), (2, 3), (4, 5)))
    np.testing.assert_allclose(
        arm["forcing"], numbers.rounded(stable["forcing"]), rtol=1e-12, atol=0
    )


def test_original_coefficients_unchanged(data):
    before = deepcopy((data.basis, data.linear, data.h, data.g))
    primary.group(data, (0, 0, 1, 2), ((0, 1), (2, 3), (4, 5)), 192)
    reference.group(data, (0, 0, 1, 2), ((0, 1), (2, 3), (4, 5)), 192)
    for actual, expected in zip((data.basis, data.linear), before[:2], strict=True):
        np.testing.assert_array_equal(actual, expected)
    for actual, expected in zip((data.h, data.g), before[2:], strict=True):
        for degree in (2, 3):
            np.testing.assert_array_equal(actual[degree], expected[degree])
