"""Small exhaustive integer oracles, not the full Q012h0 census."""

from collections import Counter
from copy import deepcopy
from itertools import combinations_with_replacement
from math import comb

import numpy as np
import pytest

from research import d3q27_quartic_census as c

TOY = (
    c.Block((1, 0, -1), "a", 2),
    c.Block((-1, 1, 0), "b", 1),
    c.Block((0, -1, 1), "c", 3),
    c.Block((1, 1, 0), "d", 2),
    c.Block((0, 0, 0), "e", 1),
)
PHYSICAL = tuple(
    c.Block(wave, label, dimension)
    for wave in ((-1, 0, 0), (0, -1, 0), (0, 1, 0), (1, 0, 0))
    for label, dimension in (("shear", 2), ("plus", 1), ("minus", 1))
)


def direct_coordinate_oracle(blocks, degree):
    owners = [i for i, block in enumerate(blocks) for _ in range(block.dimension)]
    coordinates, groups = Counter(), Counter()
    for monomial in combinations_with_replacement(range(len(owners)), degree):
        group = tuple(owners[j] for j in monomial)
        wave = tuple(sum(blocks[i].wave[axis] for i in group) for axis in range(3))
        coordinates[wave] += 1
        groups[group] += 1
    joint = Counter()
    for group, column_count in groups.items():
        wave = tuple(sum(blocks[i].wave[axis] for i in group) for axis in range(3))
        joint[(*wave, column_count)] += 1
    return dict(joint), dict(coordinates), groups


@pytest.mark.parametrize("degree", (1, 2, 3, 4))
@pytest.mark.parametrize("blocks", (TOY, TOY[::-1], TOY[:1]))
def test_all_counting_routes_match_direct_coordinate_monomials(blocks, degree):
    joint, coordinates, _ = direct_coordinate_oracle(blocks, degree)
    assert c.enumerate_joint(iter(blocks), degree) == joint
    assert c.block_generating_function(iter(blocks), degree) == joint
    assert c.coordinate_generating_function(iter(blocks), degree) == coordinates
    assert c.weighted_coordinates(joint) == coordinates
    audit = c.coverage(joint, blocks, degree)
    assert audit["passed"]
    assert audit["block_tuples"] == comb(len(blocks) + degree - 1, degree)
    assert audit["coordinate_columns"] == len(
        list(combinations_with_replacement(range(sum(b.dimension for b in blocks)), degree))
    )


@pytest.mark.parametrize(
    "group, expected",
    [
        ((0, 1, 2, 3), 12),
        ((0, 0, 1, 2), 9),
        ((0, 0, 2, 2), 18),
        ((1, 2, 2, 2), 10),
        ((2, 2, 2, 2), 15),
    ],
)
def test_all_five_quartic_multiplicity_patterns(group, expected):
    _, _, groups = direct_coordinate_oracle(TOY, 4)
    assert c.symmetric_columns(TOY, group) == groups[group] == expected


def test_dynamic_programs_do_not_call_the_enumerator_or_symmetric_kernel(monkeypatch):
    joint, coordinates, _ = direct_coordinate_oracle(TOY, 4)

    def forbidden(*args, **kwargs):
        raise AssertionError("independent route called the enumeration kernel")

    monkeypatch.setattr(c, "combinations_with_replacement", forbidden)
    monkeypatch.setattr(c, "enumerate_joint", forbidden)
    monkeypatch.setattr(c, "symmetric_columns", forbidden)
    assert c.block_generating_function(TOY, 4) == joint
    monkeypatch.setattr(c, "comb", forbidden)
    assert c.coordinate_generating_function(TOY, 4) == coordinates


def test_inventory_round_trip_consumes_an_iterator_once_and_normalizes_integer_types():
    rows = c.inventory(TOY)
    assert c.restore_inventory(iter(rows)) == TOY
    raw = c.Block([np.int64(1), np.int64(-1), np.int64(0)], "x", np.int64(2))
    normalized = c.validate(iter([raw]), np.int64(4))
    assert normalized == (c.Block((1, -1, 0), "x", 2),)
    assert type(normalized[0].dimension) is int
    assert all(type(x) is int for x in normalized[0].wave)
    rows[0]["wave"][0] = 8
    assert TOY[0].wave == (1, 0, -1)


@pytest.mark.parametrize("degree", (0, -1, 5, 1.0, True, None))
@pytest.mark.parametrize(
    "method", (c.enumerate_joint, c.block_generating_function, c.coordinate_generating_function)
)
def test_invalid_degree_is_rejected(method, degree):
    with pytest.raises(ValueError):
        method(TOY, degree)


@pytest.mark.parametrize(
    "blocks",
    [
        None,
        [],
        [None],
        [c.Block((0, 0, 0), "a", 0)],
        [c.Block((0, 0, 0), "a", -1)],
        [c.Block((0, 0, 0), "a", True)],
        [c.Block((0, 0, 0), "a", 2.0)],
        [c.Block((0, 0, 0), "", 1)],
        [c.Block((0, 0, 0), None, 1)],
        [TOY[0], TOY[0]],
    ],
)
def test_invalid_blocks_are_rejected(blocks):
    with pytest.raises(ValueError):
        c.validate(blocks, 4)


@pytest.mark.parametrize(
    "wave",
    (None, 1, (), (1, 2), (1, 2, 3, 4), (True, 0, 0), (1.0, 0, 0), (float("nan"), 0, 0), "123"),
)
def test_invalid_waves_are_rejected_by_inventory_and_grid_map(wave):
    with pytest.raises(ValueError):
        c.validate((c.Block(wave, "a", 1),), 4)
    with pytest.raises(ValueError):
        c.canonical_wave(wave, 17)


@pytest.mark.parametrize("rows", (None, [], [{}], [None], [{"wave": [0, 0, 0], "label": "a"}]))
def test_invalid_inventory_records_are_rejected(rows):
    with pytest.raises(ValueError):
        c.restore_inventory(rows)


def test_histogram_round_trips_and_incomplete_coverage_cannot_pass():
    joint, coordinates, _ = direct_coordinate_oracle(TOY, 4)
    records = c.joint_records(joint)
    assert c.parse_joint(records) == joint
    assert c.parse_coordinates(c.coordinate_records(coordinates)) == coordinates
    missing = c.parse_joint(records[1:])
    assert not c.coverage(missing, TOY, 4)["passed"]
    changed = deepcopy(records)
    changed[0]["blocks"] += 1
    assert not c.coverage(c.parse_joint(changed), TOY, 4)["passed"]
    changed = deepcopy(records)
    changed[-1]["wave"][0] += 1
    altered = c.parse_joint(changed)
    assert c.coverage(altered, TOY, 4)["passed"]
    assert altered != c.block_generating_function(TOY, 4)
    assert c.weighted_coordinates(altered) != c.coordinate_generating_function(TOY, 4)


@pytest.mark.parametrize(
    "kind", ("duplicate", "reversed", "extra", "wave", "bool", "float", "zero")
)
def test_joint_histogram_damage_is_rejected(kind):
    rows = c.joint_records(c.enumerate_joint(TOY, 2))
    if kind == "duplicate":
        rows.insert(0, deepcopy(rows[0]))
    elif kind == "reversed":
        rows.reverse()
    elif kind == "extra":
        rows[0]["unexpected"] = 1
    elif kind == "wave":
        rows[0]["wave"] = [0, 0]
    elif kind == "bool":
        rows[0]["blocks"] = True
    elif kind == "float":
        rows[0]["input_columns"] = 1.0
    else:
        rows[0]["blocks"] = 0
    with pytest.raises(ValueError):
        c.parse_joint(rows)


@pytest.mark.parametrize(
    "kind", ("duplicate", "reversed", "extra", "wave", "bool", "float", "zero")
)
def test_coordinate_histogram_damage_is_rejected(kind):
    rows = c.coordinate_records(c.coordinate_generating_function(TOY, 2))
    if kind == "duplicate":
        rows.append(deepcopy(rows[-1]))
    elif kind == "reversed":
        rows.reverse()
    elif kind == "extra":
        rows[0]["unexpected"] = 1
    elif kind == "wave":
        rows[0]["wave"] = [0, 0]
    else:
        rows[0]["columns"] = {"bool": True, "float": 1.0, "zero": 0}[kind]
    with pytest.raises(ValueError):
        c.parse_coordinates(rows)


@pytest.mark.parametrize("size", (0, 1, 2, 16, 3.0, True, None))
def test_invalid_grid_sizes_are_rejected(size):
    with pytest.raises(ValueError):
        c.canonical_wave((0, 0, 0), size)


@pytest.mark.parametrize("size", (3, 17, 33, 65))
def test_grid_map_and_sector_counts_have_an_independent_coordinate_oracle(size):
    joint, _, _ = direct_coordinate_oracle(PHYSICAL, 4)
    saved = c.sector_summary(joint, PHYSICAL, 4, size)
    # Regression for the pre-publication draft: validate() consumed this iterator.
    assert c.sector_summary(joint, iter(PHYSICAL), 4, size) == saved
    selected = {b.wave for b in PHYSICAL}
    expected = {name: Counter() for name in ("zero_kinetic", "selected_external", "outside")}
    folded_support = set()
    for (x, y, z, q), count in joint.items():
        wave = tuple(v % size if v % size <= size // 2 else v % size - size for v in (x, y, z))
        assert wave == c.canonical_wave((x, y, z), size)
        folded_support.add(wave)
        name = (
            "zero_kinetic"
            if not any(wave)
            else "selected_external"
            if wave in selected
            else "outside"
        )
        expected[name][q] += count
    for row in saved["sectors"]:
        bins = expected[row["sector"]]
        assert row["block_tuples"] == sum(bins.values())
        assert row["coordinate_columns"] == sum(q * count for q, count in bins.items())
        assert row["external_dimension"] == (27 if row["sector"] == "outside" else 23)
    assert saved["canonical_support_count"] == len(folded_support)
    assert saved["non_aliasing"] == (size != 3)
    assert bool(saved["alias_pairs"]) == (size == 3)


@pytest.mark.parametrize(
    "blocks",
    (
        (c.Block((0, 0, 0), "a", 4),),
        (c.Block((17, 0, 0), "a", 4),),
        (c.Block((1, 0, 0), "a", 2),),
    ),
)
def test_sector_layout_rejects_noncanonical_center_or_incomplete_selected_wave(blocks):
    with pytest.raises(ValueError):
        c.sector_summary(c.enumerate_joint(blocks, 2), blocks, 2, 17)


@pytest.mark.parametrize("degree", (2, 3, 4))
@pytest.mark.parametrize("chunk_columns", (7, 65536))
def test_payload_matches_actual_array_dtypes_and_explicit_operator_proxies(degree, chunk_columns):
    joint = c.enumerate_joint(PHYSICAL, degree)
    summary = c.sector_summary(joint, PHYSICAL, degree, 17)
    columns = comb(16 + degree - 1, degree)
    histogram = summary["operator_dimension_histogram"]
    saved = c.payload(degree, 16, columns, 17, histogram, chunk_columns)
    arrays = {
        "input_indices_int64": np.empty((columns, degree), dtype=np.int64),
        "wave_indices_int64": np.empty((columns, 3), dtype=np.int64),
        "response_complex128": np.empty((columns, 27), dtype=np.complex128),
        "forcing_complex128": np.empty((columns, 27), dtype=np.complex128),
        "reduced_complex128": np.empty((columns, 4), dtype=np.complex128),
    }
    assert saved["sparse_layout_bytes"] == {name: a.nbytes for name, a in arrays.items()}
    assert saved["sparse_payload_bytes"] == sum(a.nbytes for a in arrays.values())
    assert saved["dtype_bytes"] == {name: np.dtype(name).itemsize for name in saved["dtype_bytes"]}
    assert saved["chunk_count"] == len(range(0, columns, chunk_columns))
    assert saved["maximum_chunk_payload_bytes"] == min(columns, chunk_columns) * (degree * 8 + 952)
    assert saved["physical_ordered_real_W_bytes"] == 27 * 17**3 * 16**degree * 8
    assert saved["physical_symmetric_real_W_bytes"] == 27 * 17**3 * columns * 8
    dimensions = [r["dimension"] for r in histogram for _ in range(r["blocks"])]
    assert saved["maximum_operator_dimension"] == max(dimensions)
    assert saved["single_maximum_operator_complex128_bytes"] == max(dimensions) ** 2 * 16
    assert saved["dense_operator_entry_proxy"] == sum(n * n for n in dimensions)
    assert saved["dense_factorization_cubic_proxy"] == sum(n * n * n for n in dimensions)
    assert saved["full_solver_resource_feasibility"] is None
    assert "not RSS" in saved["meaning"] and "independent DOF" in saved["meaning"]


@pytest.mark.parametrize(
    "field,value",
    (
        ("degree", 5),
        ("degree", True),
        ("coordinates", 0),
        ("columns", 11),
        ("size", 16),
        ("chunk_columns", 0),
        ("chunk_columns", 1.5),
    ),
)
def test_bad_payload_parameters_are_rejected(field, value):
    kwargs = {
        "degree": 2,
        "coordinates": 4,
        "columns": 10,
        "size": 17,
        "operator_histogram": [{"dimension": 23, "blocks": 10}],
    }
    kwargs[field] = value
    with pytest.raises(ValueError):
        c.payload(**kwargs)


@pytest.mark.parametrize(
    "histogram",
    (
        None,
        [],
        [{}],
        [None],
        [{"dimension": 23, "blocks": 0}],
        [{"dimension": True, "blocks": 1}],
        [{"dimension": 23.0, "blocks": 1}],
        [{"dimension": 23, "blocks": 1}, {"dimension": 23, "blocks": 2}],
        [{"dimension": 27, "blocks": 1}, {"dimension": 23, "blocks": 2}],
    ),
)
def test_bad_operator_histograms_are_rejected(histogram):
    with pytest.raises(ValueError):
        c.payload(2, 4, 10, 17, histogram)


@pytest.mark.parametrize(
    "joint",
    (
        None,
        {},
        {(0, 0, 0): 1},
        {(True, 0, 0, 1): 1},
        {(0, 0, 0, True): 1},
        {(0, 0, 0, -1): 1},
        {(0, 0, 0, 1): 1.0},
        {(0, 0, 0, 1): False},
    ),
)
def test_raw_joint_histograms_cannot_bypass_integer_validation(joint):
    with pytest.raises(ValueError):
        c.joint_records(joint)
    with pytest.raises(ValueError):
        c.weighted_coordinates(joint)


@pytest.mark.parametrize(
    "counts", (None, {}, {(0, 0): 1}, {(0, 0, 0): True}, {(0, 0, 0): 1.0}, {(0, 0, 0): -1})
)
def test_raw_coordinate_histograms_cannot_bypass_integer_validation(counts):
    with pytest.raises(ValueError):
        c.coordinate_records(counts)


def test_large_integers_remain_exact_and_numpy_integers_do_not_overflow():
    huge = 10**90
    joint = {(0, 0, 0, huge): huge}
    assert c.weighted_coordinates(joint) == {(0, 0, 0): huge**2}
    assert c.parse_joint(c.joint_records(joint)) == joint
    assert c.canonical_wave((huge, -huge, 0), 17) == ((huge + 8) % 17 - 8, (-huge + 8) % 17 - 8, 0)
    numpy_joint = {(np.int64(0), np.int64(0), np.int64(0), np.int64(2**40)): np.int64(2**40)}
    assert c.weighted_coordinates(numpy_joint) == {(0, 0, 0): 2**80}
    assert type(next(iter(c.weighted_coordinates(numpy_joint).values()))) is int
