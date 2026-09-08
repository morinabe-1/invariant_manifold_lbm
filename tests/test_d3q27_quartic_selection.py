"""S0 integer inventory, full tiny algebra, and independent-route controls."""

from collections import Counter
from copy import deepcopy
from itertools import combinations_with_replacement, permutations, product

import numpy as np
import pytest

from research import d3q27_quartic_operator as artificial
from research import d3q27_quartic_selection as primary
from research import d3q27_quartic_selection_reference as reference


def toy_spectra(dimensions=(2, 1, 2, 1)):
    blocks = np.zeros((4, 2), dtype=complex)
    for i, n in enumerate(dimensions):
        values = np.linalg.eigvals(artificial.dynamics(i, n))
        blocks[i] = values[0]
        blocks[i, :n] = values
    output = np.tile(np.linspace(-0.6, 0.99, 27) + 0.011j, (729, 1))
    waves = np.array(((-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0)), dtype=np.int64)
    return {
        "block_eigenvalues": blocks,
        "block_dimensions": np.array(dimensions),
        "block_waves": waves,
        "external_eigenvalues": output,
        "external_dimensions": np.full(729, 27),
        "external_waves": np.array(primary.OUTPUT_WAVES),
    }


def test_full_seed_inventory_conjugacy_and_maximum_operator():
    groups = primary.seed_groups()
    assert len(groups) == 652 and groups == tuple(sorted(set(groups)))
    assert {b for g in groups for b in g} == set(range(78))
    assert Counter(primary.pattern(g) for g in groups) == {
        (4,): 78,
        (3, 1): 156,
        (2, 2): 130,
        (2, 1, 1): 130,
        (1, 1, 1, 1): 158,
    }
    for group in groups:
        partner = primary.conjugate(group)
        assert partner in groups and primary.conjugate(partner) == group
        assert primary.group_wave(partner) == tuple(-v for v in primary.group_wave(group))
        assert primary.column_count(partner) == primary.column_count(group)
    assert primary.conjugate(primary.MANDATORY) == (66, 69, 72, 75)
    assert primary.group_wave(primary.MANDATORY) == (-4, -3, -1)
    assert primary.column_count(primary.MANDATORY) == 16
    assert primary.sector(primary.group_wave(primary.MANDATORY)) == "other"
    assert sum((2 if b % 3 == 0 else 1) for b in range(78)) == 104


@pytest.mark.parametrize("dimensions", tuple(product((1, 2), repeat=4)))
def test_all_artificial_inventory_scores_against_symmetric_operator_eigenvalues(dimensions):
    data = toy_spectra(dimensions)
    groups = np.array(artificial.GROUPS)
    scores = primary.distances_for_groups(
        data["block_eigenvalues"], data["external_eigenvalues"], data["block_waves"], groups
    )
    other = reference.scan(data)
    expected = []
    for group in groups:
        matrix = artificial.build_product(dimensions, tuple(group)).dynamics
        eigs = np.linalg.eigvals(matrix)
        expected.append(np.min(np.abs(data["external_eigenvalues"][0, :, None] - eigs[None, :])))
    assert np.max(np.abs(scores - expected)) <= 1e-13
    assert np.max(np.abs(scores - other)) <= 1e-13


def test_slot_permutations_and_wave_lookup():
    data = toy_spectra()
    data["external_eigenvalues"] += np.arange(729)[:, None] / 7290
    groups = np.array(list(permutations((0, 1, 2, 3))))
    scores = primary.distances_for_groups(
        data["block_eigenvalues"], data["external_eigenvalues"], data["block_waves"], groups
    )
    assert np.ptp(scores) < 1e-14
    canonical = np.array(list(combinations_with_replacement(range(4), 4)))
    scores = primary.distances_for_groups(
        data["block_eigenvalues"], data["external_eigenvalues"], data["block_waves"], canonical
    )
    assert np.max(np.abs(scores - reference.scan(data))) < 1e-13


def test_reference_does_not_use_primary_enumeration_distance_or_reducer(monkeypatch):
    data = toy_spectra()
    expected = reference.scan(data)

    def forbidden(*args, **kwargs):
        raise AssertionError("primary kernel used by independent route")

    for name in ("tuple_chunks", "distances_for_groups", "bin_summary", "scan"):
        monkeypatch.setattr(primary, name, forbidden)
    assert np.array_equal(reference.scan(data), expected)


@pytest.mark.parametrize("chunk_size", (1, 7, 35, 4096))
def test_chunked_enumeration_coverage_and_ordinal(chunk_size):
    chunks = list(primary.tuple_chunks(7, chunk_size))
    actual = np.vstack(chunks)
    expected = np.array(list(combinations_with_replacement(range(7), 4)))
    assert np.array_equal(actual, expected)
    assert max(map(len, chunks)) <= chunk_size
    for index, group in enumerate(combinations_with_replacement(range(78), 4)):
        if index > 1200:
            break
        assert primary.group_ordinal(group) == index
    assert primary.group_ordinal((77, 77, 77, 77)) == primary.TUPLE_COUNT - 1


@pytest.fixture(scope="module")
def full_tie_bins():
    scores = np.ones(primary.TUPLE_COUNT)
    first = primary.bin_summary(scores)
    second = reference.bin_summary(scores)
    assert first == second
    assert sum(row["count"] for row in first) == 1663740
    return first


def test_full_bin_counts_empty_bins_and_common_selection(full_tie_bins):
    assert len(full_tie_bins) == 15
    empty = [row for row in full_tie_bins if row["count"] == 0]
    # 4w and 3w+v cannot be zero/first-shell; 2w+2v cannot be first-shell.
    assert {(tuple(row["pattern"]), row["sector"]) for row in empty} == {
        ((4,), "zero"),
        ((4,), "selected"),
        ((3, 1), "zero"),
        ((3, 1), "selected"),
        ((2, 2), "selected"),
    }
    assert all(
        row["group"] is None and row["minimum"] is None and row["ordinal"] is None for row in empty
    )
    selected = primary.select_groups({n: full_tie_bins for n in primary.SIZES})
    assert 652 <= len(selected) <= 742
    assert max(row["operator_dimension"] for row in selected) == 432
    groups = {tuple(row["group"]) for row in selected}
    assert all(primary.conjugate(g) in groups for g in groups)


@pytest.mark.parametrize(
    "mutation",
    ("missing_grid", "missing_bin", "false_count", "wrong_ordinal", "nan", "wrong_sector"),
)
def test_selection_cannot_accept_partial_or_inconsistent_bins(full_tie_bins, mutation):
    data = {n: deepcopy(full_tie_bins) for n in primary.SIZES}
    nonempty = next(row for row in data[17] if row["count"])
    if mutation == "missing_grid":
        del data[65]
    elif mutation == "missing_bin":
        data[65].pop()
    elif mutation == "false_count":
        nonempty["count"] += 1
    elif mutation == "wrong_ordinal":
        nonempty["ordinal"] += 1
    elif mutation == "nan":
        nonempty["minimum"] = float("nan")
    else:
        nonempty["sector"] = "selected"
    with pytest.raises(ValueError):
        primary.select_groups(data)


@pytest.mark.parametrize(
    "group", ((0, 1, 2), (0, 1, 2, 78), (0, 1, 2, -1), (0, 1, 2, True), (0, 1, 2, 3.0))
)
def test_invalid_groups_are_rejected(group):
    with pytest.raises(ValueError):
        primary.normalized_group(group)


@pytest.mark.parametrize("count, chunk", ((0, 5), (79, 5), (True, 5), (4, 0), (4, 4097), (4, True)))
def test_invalid_chunk_configuration_is_rejected(count, chunk):
    with pytest.raises(ValueError):
        list(primary.tuple_chunks(count, chunk))


@pytest.fixture(scope="module")
def physical_inputs():
    return primary.spectral_inputs(17)


def test_all_actual_input_sectors_and_independent_population_symbol(physical_inputs):
    arrays, audit = physical_inputs
    assert audit["frames"]["passed"]
    assert reference.direct_input_audit(arrays, 17)["passed"]
    assert Counter(arrays["external_dimensions"]) == {23: 27, 27: 702}
    assert arrays["block_dimensions"].sum() == 104


@pytest.mark.parametrize(
    "name,index",
    (
        ("block_dynamics", (77, 0, 0)),
        ("external_eigenvalues", (728, 26)),
        ("block_basis", (1, 0, 1)),
    ),
)
def test_spectral_entry_and_padding_mutations_are_rejected(physical_inputs, name, index):
    arrays = {k: v.copy() for k, v in physical_inputs[0].items()}
    arrays[name][index] += 0.001
    with pytest.raises(ValueError):
        primary.validate_spectra(arrays)


def test_independent_input_audit_detects_symbol_and_basis_errors(physical_inputs):
    for name, index in (
        ("block_basis", (0, 0, 0)),
        ("external_dynamics", (0, 0, 0)),
        ("external_projection", (364, 0, 0)),
    ):
        arrays = {k: v.copy() for k, v in physical_inputs[0].items()}
        arrays[name][index] += 0.001
        assert not reference.direct_input_audit(arrays, 17)["passed"]


def test_interrupted_primary_scan_preserves_completed_prefix(physical_inputs):
    def stop(count):
        raise RuntimeError("deliberate resource-stop control")

    with pytest.raises(RuntimeError, match="resource-stop") as observed:
        primary.scan(physical_inputs[0], stop)
    kept = observed.value.partial_distances
    assert kept.shape == (4096,) and np.isfinite(kept).all()


def test_reference_scalar_failure_preserves_only_completed_values(monkeypatch):
    original = reference.scalar_distance
    counter = 0

    def fail_after_five(*args, **kwargs):
        nonlocal counter
        counter += 1
        if counter == 6:
            raise RuntimeError("deliberate scalar failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(reference, "scalar_distance", fail_after_five)
    with pytest.raises(RuntimeError, match="scalar failure") as observed:
        reference.scan(toy_spectra())
    assert observed.value.partial_distances.shape == (5,)
