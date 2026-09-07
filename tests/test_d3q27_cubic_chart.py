"""Q012g implementation controls; synthetic fibers are NOT LBM evidence."""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as quadratic
from research import d3q27_cubic_chart as chart
from research import d3q27_refined_cubic as refined
from research import q012a_d3q27_foundation as foundation
from research import q012f2_d3q27_refined_cubic as preflight
from ttim_lbm.rational_spectrum import _file_sha256


def test_grouped_engine_uses_taylor_monomials_without_factorials():
    indices = np.array(((0, 0, 0), (0, 0, 1), (0, 1, 2), (1, 1, 1)))
    groups = np.array((2, 0, 2, 0))  # Intentionally noncontiguous support order.
    coefficients = np.array(((1 + 2j, 3), (4, 5j), (6, 7), (8j, 9)))
    engine = chart.GroupedPolynomial(indices, groups, coefficients, dimension=3, group_count=4)
    z = np.array((0.2 + 0.3j, -0.4 + 0.1j, 0.6 - 0.5j))
    expected = np.zeros((4, 2), dtype=complex)
    expected[2] = coefficients[0] * z[0] ** 3 + coefficients[2] * z[0] * z[1] * z[2]
    expected[0] = coefficients[1] * z[0] ** 2 * z[1] + coefficients[3] * z[1] ** 3
    np.testing.assert_allclose(engine.evaluate(z), expected, rtol=1e-15, atol=1e-15)
    np.testing.assert_allclose(engine.evaluate(-z), -expected, rtol=1e-15, atol=1e-15)
    np.testing.assert_allclose(engine.evaluate(2 * z), 8 * expected, rtol=1e-15, atol=1e-15)
    np.testing.assert_array_equal(engine.evaluate(np.zeros(3)), np.zeros((4, 2)))
    # Caller mutation must not silently replace prepared coefficients or support.
    coefficients[:] = 99
    indices[:] = 2
    groups[:] = 3
    np.testing.assert_allclose(engine.evaluate(z), expected, rtol=1e-15, atol=1e-15)
    for value in (engine.coefficients, engine.indices, engine.starts, engine.outputs):
        assert not value.flags.writeable
    storage = engine.storage()
    assert storage["monomial_rows"] == 4 and storage["degree"] == 3
    assert storage["coefficient_scalars"] == 8 and storage["coefficient_bytes"] == 128
    assert storage["sparse_index_bytes"] == sum(
        v.nbytes for v in (engine.indices, engine.starts, engine.outputs)
    )


def test_empty_known_support_is_a_zero_polynomial():
    engine = chart.GroupedPolynomial(
        np.empty((0, 3), dtype=np.int64),
        np.empty(0, dtype=np.int64),
        np.empty((0, 4), dtype=complex),
        dimension=104,
        group_count=26,
    )
    np.testing.assert_array_equal(engine.evaluate(np.ones(104)), np.zeros((26, 4)))
    assert engine.storage()["coefficient_bytes"] == 0


@pytest.mark.parametrize(
    "change",
    (
        {"monomials": np.array([[0.0, 1.0, 1.0]])},
        {"monomials": np.array([[-1, 1, 1]])},
        {"monomials": np.array([[0, 1, 2]])},
        {"monomials": np.array([0, 1, 1])},
        {"monomials": np.empty((1, 0), dtype=int)},
        {"groups": np.array([0.0])},
        {"groups": np.array([-1])},
        {"groups": np.array([1])},
        {"groups": np.array([[0]])},
        {"coefficients": np.array([[np.nan]])},
        {"coefficients": np.array([[np.inf]])},
        {"coefficients": np.ones((2, 1))},
        {"coefficients": np.empty((1, 0))},
        {"dimension": True},
        {"dimension": 2.0},
        {"group_count": 0},
    ),
)
def test_grouped_engine_rejects_bad_inputs(change):
    arguments = {
        "monomials": np.array([[0, 1, 1]]),
        "groups": np.array([0]),
        "coefficients": np.ones((1, 1)),
        "dimension": 2,
        "group_count": 1,
    }
    arguments.update(change)
    with pytest.raises(ValueError):
        chart.GroupedPolynomial(**arguments)


@pytest.mark.parametrize("value", (np.zeros(3), np.full(2, np.nan), np.full(2, np.inf)))
def test_grouped_engine_rejects_bad_coordinates(value):
    engine = chart.GroupedPolynomial(
        np.array([[0, 1, 1]]), np.array([0]), np.ones((1, 1)), dimension=2, group_count=1
    )
    with pytest.raises(ValueError):
        engine.evaluate(value)


def test_overflow_cannot_pass_a_realness_gate():
    for bad in (np.array([np.nan]), np.array([np.inf]), np.array([1e308 + 1e308j])):
        with np.errstate(over="ignore", invalid="ignore"), pytest.raises(ValueError):
            chart.checked_real(bad, "overflow control")
    engine = chart.GroupedPolynomial(
        np.array([[0, 0, 0]]), np.array([0]), np.ones((1, 1)), dimension=1, group_count=1
    )
    with pytest.raises((FloatingPointError, ValueError)):
        engine.evaluate(np.array([1e300]))


def test_manual_realification_checks_both_partners_and_acoustic_swap():
    a = np.linspace(-0.2, 0.3, 104)
    transform, partners = quadratic.realification()
    z = chart.manual_complex_coordinates(a)
    np.testing.assert_allclose(z, transform @ a, rtol=1e-15, atol=1e-16)
    np.testing.assert_array_equal(z[partners], z.conj())
    restored, audit = chart.manual_real_coordinates(z)
    np.testing.assert_allclose(restored, a, rtol=1e-15, atol=1e-16)
    assert audit["passed"] and audit["imaginary_norm"] == 0
    z[partners[4 * quadratic.WAVES.index(quadratic.POSITIVE_WAVES[0]) + 2]] += 0.01j
    with pytest.raises(ValueError, match="imaginary"):
        chart.manual_real_coordinates(z)


@pytest.mark.parametrize(
    "value",
    (
        np.zeros(103),
        np.zeros((104, 1)),
        np.zeros(104, dtype=complex),
        np.full(104, np.nan),
        np.full(104, np.inf),
    ),
)
def test_public_real_coordinates_do_not_coerce_invalid_inputs(value):
    with pytest.raises(ValueError):
        chart.manual_complex_coordinates(value)


def test_realification_records_nonzero_error_before_returning_an_owned_real_array():
    original = np.array((2 + 1e-10j, -3 - 2e-10j))
    value, audit = chart.checked_real(original, "test")
    assert value.dtype == np.float64 and not np.shares_memory(value, original)
    assert audit["imaginary_norm"] > 0 and audit["passed"]
    assert audit["scaled_imaginary_norm"] == audit["imaginary_norm"] / audit["real_norm"]
    with pytest.raises(ValueError, match="imaginary"):
        chart.checked_real(np.array([1 + 1e-4j]), "test")


@pytest.fixture(scope="module")
def synthetic_arrays():
    """Full monomial shape, but only four conjugate pairs of invented coefficients."""
    triples = np.array(list(combinations_with_replacement(range(104), 3)), dtype=np.int64)
    waves = np.asarray(quadratic.WAVES, dtype=np.int64)[triples // 4].sum(axis=1)
    arrays = {
        "input_triples": triples,
        "output_waves": waves,
        "response": np.zeros((len(triples), 27), dtype=complex),
        "forcing": np.zeros((len(triples), 27), dtype=complex),
        "reduced": np.zeros((len(triples), 4), dtype=complex),
    }
    _, partners = quadratic.realification()
    lookup = {tuple(t): index for index, t in enumerate(triples)}
    for monomial in ((0, 0, 0), (0, 0, int(partners[0])), (2, 2, 2), (2, 2, int(partners[2]))):
        row = lookup[monomial]
        opposite = lookup[tuple(sorted(partners[list(monomial)]))]
        arrays["response"][row, 4:7] = (1 + 2j, -3j, 0.4 - 0.2j)
        arrays["response"][opposite] = arrays["response"][row].conj()
        arrays["forcing"][row] = 2 * arrays["response"][row]
        arrays["forcing"][opposite] = arrays["forcing"][row].conj()
        if tuple(waves[row]) in quadratic.WAVES:
            arrays["reduced"][row] = (1 + 1j, 0.3 - 0.2j, 2j, 1 - 0.4j)
            arrays["reduced"][opposite] = arrays["reduced"][row].conj()[[0, 1, 3, 2]]
    for value in arrays.values():
        value.setflags(write=False)
    return arrays


class ToyQuadratic:
    """A deliberately simple NOT-LBM quadratic chart for orchestration tests."""

    size, omega, eta, power = 17, 1.5, 0.02, 2

    def __init__(self):
        self.transform, _ = quadratic.realification()
        self.base = np.zeros((17, 17, 17, 27))
        self.real_linear = 0.5 * np.eye(104)

    def complex_coordinates(self, a):
        return self.transform @ chart.real_coordinates(a, 104)

    def linear_fourier(self, a):
        a = chart.real_coordinates(a, 104)
        result = np.zeros(self.base.shape, dtype=complex)
        result[0, 0, 1, 0] = result[0, 0, -1, 0] = a[0]
        return result

    def quadratic_fourier(self, a):
        a = chart.real_coordinates(a, 104)
        result = np.zeros(self.base.shape, dtype=complex)
        result[0, 0, 2, 1] = result[0, 0, -2, 1] = a[0] * a[1]
        return result

    def reduced(self, a):
        a = chart.real_coordinates(a, 104)
        result = self.real_linear @ a
        result[0] += a[0] * a[1]
        return result


@pytest.fixture(scope="module")
def synthetic_model(synthetic_arrays):
    return chart.CubicChart(ToyQuadratic(), synthetic_arrays)


def test_complete_synthetic_fibers_match_independent_sum(synthetic_model, synthetic_arrays):
    model = synthetic_model
    a = np.linspace(-0.2, 0.3, 104)
    h, g = chart.direct_cubic_sum(synthetic_arrays, a, 17)
    np.testing.assert_allclose(model.cubic_fourier(a), h, atol=2e-16, rtol=2e-15)
    np.testing.assert_allclose(model.cubic_fourier(a, forcing=True), 2 * h, atol=4e-16, rtol=2e-15)
    manual_g, manual_audit = chart.manual_real_coordinates(g)
    np.testing.assert_allclose(model.reduced_cubic(a), manual_g, atol=2e-16, rtol=2e-15)
    physical, audit = model.cubic_field_with_audit(a)
    reference = np.fft.ifftn(h, axes=(0, 1, 2), norm="ortho")
    np.testing.assert_allclose(physical, reference.real, atol=2e-17)
    assert audit["passed"] and manual_audit["passed"]
    assert model.input_audit["complete_monomials"] == 192920
    assert model.response.storage()["monomial_rows"] == 192920
    assert (
        model.internal.storage()["monomial_rows"] == model.input_audit["reduced_first_shell_rows"]
    )


def test_cubic_composition_zero_and_homogeneity_are_not_an_LBM_claim(synthetic_model):
    model = synthetic_model
    for a in (np.linspace(-0.2, 0.3, 104), *np.eye(104)):
        z = model.quadratic.complex_coordinates(a)
        for engine in (model.response, model.internal):
            value = engine.evaluate(z)
            np.testing.assert_allclose(engine.evaluate(-z), -value, atol=1e-15)
            np.testing.assert_allclose(engine.evaluate(2 * z), 8 * value, atol=1e-15)
    zero = np.zeros(104)
    np.testing.assert_array_equal(model.embed(zero), model.quadratic.base)
    np.testing.assert_array_equal(model.reduced(zero), zero)
    a = np.linspace(-0.2, 0.3, 104)
    w2 = (
        model.quadratic.base
        + np.fft.ifftn(
            model.quadratic.linear_fourier(a) + model.quadratic.quadratic_fourier(a),
            axes=(0, 1, 2),
            norm="ortho",
        ).real
    )
    np.testing.assert_array_equal(model.embed(a, degree=2), w2)
    np.testing.assert_allclose(model.embed(a) - w2, model.cubic_field(a), atol=2e-17)
    np.testing.assert_array_equal(model.reduced(a, degree=2), model.quadratic.reduced(a))
    np.testing.assert_allclose(
        model.reduced(a) - model.reduced(a, degree=2), model.reduced_cubic(a), atol=2e-17
    )
    storage = model.storage()
    assert storage["coefficient_bytes"] == sum(
        v["coefficient_bytes"] for v in storage["engines"].values()
    )
    assert all(v["degree"] == 3 for v in storage["engines"].values())


@pytest.mark.parametrize("degree", (1, 4, True, 3.0, None))
def test_only_registered_degrees_are_exposed(synthetic_model, degree):
    for method in (synthetic_model.embed, synthetic_model.reduced):
        with pytest.raises(ValueError):
            method(np.zeros(104), degree=degree)


@pytest.mark.parametrize(
    "value",
    (np.zeros(103), np.zeros(104, dtype=complex), np.full(104, np.nan), np.full(104, np.inf)),
)
def test_chart_wrappers_reject_invalid_coordinates(synthetic_model, value):
    for method in (
        synthetic_model.embed,
        synthetic_model.reduced,
        synthetic_model.cubic_field,
        synthetic_model.reduced_cubic,
    ):
        with pytest.raises(ValueError):
            method(value)


def test_chart_rejects_wrong_spectrum_and_nonreal_field(synthetic_model):
    with pytest.raises(ValueError):
        synthetic_model.physical_with_audit(np.zeros((3, 3, 3, 27)))
    spectrum = np.zeros(synthetic_model.quadratic.base.shape, dtype=complex)
    spectrum[1, 1, 1, 0] = 1j
    with pytest.raises(ValueError, match="imaginary"):
        synthetic_model.physical_with_audit(spectrum)


@pytest.mark.parametrize(
    "mutation",
    ("missing", "shape", "dtype", "nan", "duplicate", "order", "range", "wave", "reduced_support"),
)
def test_full_fiber_validation_rejects_bad_archives(synthetic_arrays, mutation):
    arrays = dict(synthetic_arrays)
    if mutation == "missing":
        del arrays["forcing"]
    elif mutation == "shape":
        arrays["response"] = arrays["response"][:-1]
    elif mutation == "dtype":
        arrays["input_triples"] = arrays["input_triples"].astype(np.int32)
    elif mutation == "nan":
        arrays["response"] = arrays["response"].copy()
        arrays["response"][0, 0] = np.nan
    elif mutation in ("duplicate", "order", "range"):
        arrays["input_triples"] = arrays["input_triples"].copy()
        arrays["input_triples"][0] = {
            "duplicate": (0, 0, 1),
            "order": (1, 0, 0),
            "range": (0, 0, 104),
        }[mutation]
    elif mutation == "wave":
        arrays["output_waves"] = arrays["output_waves"].copy()
        arrays["output_waves"][0, 0] += 1
    else:
        arrays["reduced"] = arrays["reduced"].copy()
        arrays["reduced"][0, 0] = 1e-300  # Even an extremely small NONZERO is forbidden.
    with pytest.raises(ValueError):
        chart.validate_fibers(arrays)


@pytest.mark.parametrize(
    "attribute,value", (("size", 16), ("omega", 1.0), ("eta", 0.0), ("power", 1))
)
def test_chart_does_not_silently_change_the_registered_map(synthetic_arrays, attribute, value):
    model = ToyQuadratic()
    setattr(model, attribute, value)
    with pytest.raises(ValueError, match="registered"):
        chart.CubicChart(model, synthetic_arrays)


def test_nonunitary_or_mismatched_realification_is_rejected(synthetic_arrays):
    model = ToyQuadratic()
    model.transform[0] *= 2
    with pytest.raises(ValueError, match="realification"):
        chart.CubicChart(model, synthetic_arrays)


def test_archive_byte_array_and_completeness_seals(tmp_path, synthetic_arrays):
    path = tmp_path / "synthetic.npz"
    expected = refined.save_fibers(path, synthetic_arrays)
    arrays, audit = chart.load_fibers(path, expected)
    assert audit["passed"] and audit["entries"] == expected["entries"]
    assert all(not a.flags.writeable for a in arrays.values())
    forged = deepcopy(expected)
    forged["entries"]["response"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="metadata"):
        chart.load_fibers(path, forged)
    with pytest.raises(ValueError, match="filename"):
        chart.load_fibers(path, {**expected, "filename": "somewhere_else.npz"})
    with pytest.raises(FileNotFoundError):
        chart.load_fibers(tmp_path / "gone" / path.name, expected)
    with path.open("ab") as target:
        target.write(b"corruption")
    with pytest.raises(ValueError, match="byte seal"):
        chart.load_fibers(path, expected)
    incomplete = tmp_path / "incomplete.npz"
    missing = {k: v for k, v in synthetic_arrays.items() if k != "forcing"}
    metadata = refined.save_fibers(incomplete, missing)
    with pytest.raises(ValueError, match="missing"):
        chart.load_fibers(incomplete, metadata)


def test_manufactured_polynomials_and_nondiagonal_complex_pairs():
    model = chart.ManufacturedChart()
    expected_b = np.array(
        ((0.64, -0.48, 0, 0), (0.48, 0.64, 0, 0), (0, 0, 0.42, 0.56), (0, 0, -0.56, 0.42))
    )
    np.testing.assert_allclose(
        model.transform.conj().T @ model.linear @ model.transform, expected_b, atol=2e-16
    )
    np.testing.assert_allclose(np.abs(np.diag(model.linear)), (0.8, 0.8, 0.7, 0.7), atol=1e-16)
    for a in (np.array((0.08, -0.06, 0.04, -0.02)), *np.eye(4), -np.ones(4)):
        explicit, compiled = chart.manufactured_explicit(a), model.parts(a)
        for name in ("h2", "h3", "r2", "r3"):
            value = model.transform.conj().T @ compiled[name] if name[0] == "r" else compiled[name]
            np.testing.assert_allclose(value, explicit[name], atol=1e-16)
        np.testing.assert_allclose(
            chart.manufactured_map(model.embed(a)), model.embed(model.reduced(a)), atol=3e-16
        )
    at = chart.manufactured_explicit(np.array((0.08, -0.06, 0.04, -0.02)))
    assert all(np.linalg.norm(at[name]) > 0 for name in ("h2", "h3", "r2", "r3"))


def test_registered_manufactured_eight_directions_and_negative_controls():
    result = chart.manufactured_controls()
    assert result["passed"] and len(result["records"]) == 8
    assert result["seed"] == 2026090723 and result["amplitude"] == 0.1
    assert [r["direction_index"] for r in result["records"]] == list(range(8))
    assert all(max(r["errors"].values()) <= 1e-12 for r in result["records"])
    negative = result["negative_controls"]
    assert negative["a"] == [0.08, -0.06, 0.04, -0.02]
    assert negative["omitted_R3_defect"] > 1e-10
    assert negative["doubled_H3_defect"] > 1e-10
    assert result == chart.manufactured_controls()


@pytest.mark.parametrize(
    "terms,transform,complex_output",
    (
        ({}, np.eye(2), False),
        ({(0,): (1,)}, np.ones((2, 3)), False),
        ({(0,): (1,)}, 2 * np.eye(2), False),
        ({(2,): (1,)}, np.eye(2), False),
        ({(0,): (1,), (1, 1): (1,)}, np.eye(2), False),
        ({(0,): (1,)}, np.eye(2), True),
        ({(0,): (np.nan,)}, np.eye(2), False),
    ),
)
def test_manufactured_expansion_rejects_inconsistent_specifications(
    terms, transform, complex_output
):
    with pytest.raises(ValueError):
        chart.transformed_polynomial(terms, transform, complex_output=complex_output)


@pytest.mark.parametrize("size", (17, 33, 65))
def test_all_real_archives_can_be_loaded_without_changing_or_evaluating_them(size):
    path = foundation.ARTIFACT_DIRECTORY / "q012f2_d3q27_refined_cubic.json"
    assert _file_sha256(path) == "65a0046d2b54c1192a84fbce481da0e804364cf62566d2e9c18204e372158ec1"
    result = preflight.read_json(path)
    grid = next(g for g in result["cycle"]["grids"] if g["size"] == size)
    expected = grid["fiber_archive"]
    archive_path = path.parent / expected["filename"]
    arrays, audit = chart.load_fibers(archive_path, expected)
    assert audit["passed"] and audit["complete_monomials"] == 192920
    assert audit["entries"] == expected["entries"]
    assert all(not a.flags.writeable for a in arrays.values())
    assert refined.file_hash(archive_path) == expected["sha256"]
    # This is a read/shape/support/hash audit, NOT a finite-amplitude chart test.


def test_old_preflight_sources_and_input_chain_are_unchanged():
    path = foundation.ARTIFACT_DIRECTORY / "q012f2_d3q27_refined_cubic.json"
    result = preflight.read_json(path)
    current = preflight.metadata()
    assert all(result[k] == current[k] for k in ("source", "runner_source", "helper_sources"))
    assert preflight.input_audit() == result["cycle"]["input_audit"]
    assert result["cycle"]["input_audit"]["passed"]
    assert _file_sha256(Path(preflight.__file__)) == result["runner_source"]["sha256"]
