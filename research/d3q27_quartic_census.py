"""Exact structural counts and array payloads; no quartic solver claims.

Counting is generic for blocks of positive dimension. Sector and payload
summaries use the registered D3Q27 fixed-leaf layout, with four selected
coordinates per nonzero wave and 23 zero-wave kinetic directions.
"""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement
from math import comb, prod
from numbers import Integral


@dataclass(frozen=True)
class Block:
    wave: tuple[int, int, int]
    label: str
    dimension: int


def positive_integer(value):
    return isinstance(value, Integral) and not isinstance(value, bool) and value > 0


def validate_degree(degree):
    if not positive_integer(degree) or degree > 4:
        raise ValueError("degree must be an integer from 1 through 4")
    return int(degree)


def wave_tuple(wave):
    try:
        wave = tuple(wave)
    except TypeError as error:
        raise ValueError("three integer wave components required") from error
    if len(wave) != 3 or any(not isinstance(x, Integral) or isinstance(x, bool) for x in wave):
        raise ValueError("three integer wave components required")
    return tuple(int(x) for x in wave)


def validate(blocks, degree):
    validate_degree(degree)
    try:
        blocks = tuple(blocks)
    except TypeError as error:
        raise ValueError("block inventory must be iterable") from error
    if not blocks:
        raise ValueError("at least one block required")
    keys, result = set(), []
    for block in blocks:
        if not isinstance(block, Block) or not positive_integer(block.dimension):
            raise ValueError("positive block dimension required")
        if not isinstance(block.label, str) or not block.label:
            raise ValueError("nonempty block label required")
        wave = wave_tuple(block.wave)
        key = (wave, block.label)
        if key in keys:
            raise ValueError("duplicate block key")
        keys.add(key)
        result.append(Block(wave, block.label, int(block.dimension)))
    return tuple(result)


def inventory(blocks):
    return [
        {"wave": list(b.wave), "label": b.label, "dimension": b.dimension}
        for b in validate(blocks, 1)
    ]


def restore_inventory(rows):
    try:
        rows = tuple(rows)
    except TypeError as error:
        raise ValueError("inventory rows required") from error
    if any(not isinstance(r, dict) or set(r) != {"wave", "label", "dimension"} for r in rows):
        raise ValueError("inventory fields differ")
    return validate((Block(r["wave"], r["label"], r["dimension"]) for r in rows), 1)


def symmetric_columns(blocks, group):
    """Internal kernel for a validated inventory and an enumerated block tuple."""
    return prod(
        comb(blocks[index].dimension + multiplicity - 1, multiplicity)
        for index, multiplicity in Counter(group).items()
    )


def enumerate_joint(blocks, degree):
    """Stream unordered block tuples without materializing the full tuple list."""
    blocks = validate(blocks, degree)
    result = Counter()
    for group in combinations_with_replacement(range(len(blocks)), int(degree)):
        wave = tuple(sum(blocks[i].wave[j] for i in group) for j in range(3))
        result[(*wave, symmetric_columns(blocks, group))] += 1
    return dict(result)


def block_generating_function(blocks, degree):
    """Independent finite product: no unordered tuple enumeration or shared kernel."""
    blocks = validate(blocks, degree)
    degree = int(degree)
    coefficients = [Counter() for _ in range(degree + 1)]
    coefficients[0][(0, 0, 0, 1)] = 1
    for block in blocks:
        updated = [Counter() for _ in range(degree + 1)]
        wx, wy, wz = block.wave
        for used, states in enumerate(coefficients):
            for (x, y, z, columns), count in states.items():
                for copies in range(degree - used + 1):
                    local = comb(block.dimension + copies - 1, copies)
                    key = (x + copies * wx, y + copies * wy, z + copies * wz, columns * local)
                    updated[used + copies][key] += count
        coefficients = updated
    return dict(coefficients[degree])


def coordinate_generating_function(blocks, degree):
    """Individual-coordinate product; no symmetric block-column factors."""
    blocks = validate(blocks, degree)
    degree = int(degree)
    coefficients = [Counter() for _ in range(degree + 1)]
    coefficients[0][(0, 0, 0)] = 1
    for block in blocks:
        wx, wy, wz = block.wave
        for _ in range(block.dimension):
            updated = [Counter() for _ in range(degree + 1)]
            for used, states in enumerate(coefficients):
                for (x, y, z), count in states.items():
                    for copies in range(degree - used + 1):
                        key = (x + copies * wx, y + copies * wy, z + copies * wz)
                        updated[used + copies][key] += count
            coefficients = updated
    return dict(coefficients[degree])


def validate_joint(joint):
    if not isinstance(joint, dict) or not joint:
        raise ValueError("nonempty joint histogram required")
    result = {}
    for key, count in joint.items():
        if not isinstance(key, tuple) or len(key) != 4:
            raise ValueError("joint keys require a wave and a column count")
        wave = wave_tuple(key[:3])
        if not positive_integer(key[3]) or not positive_integer(count):
            raise ValueError("histogram counts must be positive integers")
        result[(*wave, int(key[3]))] = int(count)
    return result


def joint_records(joint):
    return [
        {"wave": list(key[:3]), "input_columns": key[3], "blocks": count}
        for key, count in sorted(validate_joint(joint).items())
    ]


def parse_joint(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty histogram row list required")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"wave", "input_columns", "blocks"}:
            raise ValueError("joint histogram fields differ")
        wave = wave_tuple(row["wave"])
        if not positive_integer(row["input_columns"]) or not positive_integer(row["blocks"]):
            raise ValueError("histogram counts must be positive integers")
        key = (*wave, int(row["input_columns"]))
        if key in result:
            raise ValueError("duplicate histogram bin")
        result[key] = int(row["blocks"])
    if joint_records(result) != rows:
        raise ValueError("histogram order or representation differs")
    return result


def coordinate_records(counts):
    if not isinstance(counts, dict) or not counts:
        raise ValueError("nonempty coordinate histogram required")
    result = []
    for wave, count in counts.items():
        if not positive_integer(count):
            raise ValueError("positive coordinate count required")
        result.append({"wave": list(wave_tuple(wave)), "columns": int(count)})
    return sorted(result, key=lambda row: row["wave"])


def parse_coordinates(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty coordinate row list required")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"wave", "columns"}:
            raise ValueError("coordinate histogram fields differ")
        wave = wave_tuple(row["wave"])
        if wave in result or not positive_integer(row["columns"]):
            raise ValueError("duplicate wave or invalid coordinate count")
        result[wave] = int(row["columns"])
    if coordinate_records(result) != rows:
        raise ValueError("coordinate order or representation differs")
    return result


def weighted_coordinates(joint):
    result = Counter()
    for (*wave, columns), count in validate_joint(joint).items():
        result[tuple(wave)] += columns * count
    return dict(result)


def coverage(joint, blocks, degree):
    blocks = validate(blocks, degree)
    joint = validate_joint(joint)
    actual_blocks = sum(joint.values())
    actual_columns = sum(key[3] * n for key, n in joint.items())
    expected_blocks = comb(len(blocks) + int(degree) - 1, int(degree))
    expected_columns = comb(sum(b.dimension for b in blocks) + int(degree) - 1, int(degree))
    return {
        "block_tuples": actual_blocks,
        "coordinate_columns": actual_columns,
        "expected_block_tuples": expected_blocks,
        "expected_coordinate_columns": expected_columns,
        "passed": actual_blocks == expected_blocks and actual_columns == expected_columns,
    }


def canonical_wave(wave, size):
    if not positive_integer(size) or size < 3 or size % 2 == 0:
        raise ValueError("odd grid size at least three required")
    size = int(size)
    return tuple((x + size // 2) % size - size // 2 for x in wave_tuple(wave))


def sector_summary(joint, blocks, degree, size):
    blocks = validate(blocks, degree)
    joint = validate_joint(joint)
    canonical_wave((0, 0, 0), size)
    selected_dimensions = Counter()
    for block in blocks:
        if block.wave == (0, 0, 0) or block.wave != canonical_wave(block.wave, size):
            raise ValueError("selected waves must be nonzero canonical waves")
        selected_dimensions[block.wave] += block.dimension
    if any(dimension != 4 for dimension in selected_dimensions.values()):
        raise ValueError("D3Q27 layout requires four selected coordinates per wave")
    support = sorted({key[:3] for key in joint})
    seen, aliases = {}, []
    for wave in support:
        folded = canonical_wave(wave, size)
        if folded in seen:
            aliases.append([list(seen[folded]), list(wave)])
        else:
            seen[folded] = wave
    sectors = {name: Counter() for name in ("zero_kinetic", "selected_external", "outside")}
    for (*raw_wave, columns), count in joint.items():
        wave = canonical_wave(raw_wave, size)
        name = (
            "zero_kinetic"
            if wave == (0, 0, 0)
            else "selected_external"
            if wave in selected_dimensions
            else "outside"
        )
        sectors[name][columns] += count
    records, operators = [], Counter()
    for name, sizes in sectors.items():
        external = 27 if name == "outside" else 23
        records.append(
            {
                "sector": name,
                "external_dimension": external,
                "block_tuples": sum(sizes.values()),
                "coordinate_columns": sum(q * n for q, n in sizes.items()),
                "input_column_histogram": [
                    {"columns": q, "blocks": n} for q, n in sorted(sizes.items())
                ],
            }
        )
        for q, n in sizes.items():
            operators[external * q] += n
    return {
        "size": int(size),
        "degree": int(degree),
        "raw_support_count": len(support),
        "canonical_support_count": len(seen),
        "alias_pairs": aliases,
        "non_aliasing": not aliases,
        "sectors": records,
        "operator_dimension_histogram": [
            {"dimension": n, "blocks": count} for n, count in sorted(operators.items())
        ],
    }


def payload(degree, coordinates, columns, size, operator_histogram, chunk_columns=65536):
    degree = validate_degree(degree)
    if any(not positive_integer(v) for v in (coordinates, columns, chunk_columns)):
        raise ValueError("positive integer layout sizes required")
    canonical_wave((0, 0, 0), size)
    coordinates, columns, size, chunk_columns = map(
        int, (coordinates, columns, size, chunk_columns)
    )
    if columns != comb(coordinates + degree - 1, degree):
        raise ValueError("full symmetric coordinate column coverage required")
    if not isinstance(operator_histogram, list) or not operator_histogram:
        raise ValueError("nonempty operator histogram required")
    operators = {}
    for row in operator_histogram:
        if not isinstance(row, dict) or set(row) != {"dimension", "blocks"}:
            raise ValueError("operator histogram fields differ")
        if not positive_integer(row["dimension"]) or not positive_integer(row["blocks"]):
            raise ValueError("positive operator dimensions and counts required")
        dimension, count = int(row["dimension"]), int(row["blocks"])
        if dimension in operators:
            raise ValueError("duplicate operator dimension")
        operators[dimension] = count
    if list(operators) != sorted(operators):
        raise ValueError("operator histogram must be sorted")
    per_column = {
        "input_indices_int64": degree * 8,
        "wave_indices_int64": 3 * 8,
        "response_complex128": 27 * 16,
        "forcing_complex128": 27 * 16,
        "reduced_complex128": 4 * 16,
    }
    parts = {key: value * columns for key, value in per_column.items()}
    max_dimension = max(operators)
    return {
        "meaning": "uncompressed array payload only; not RSS, runtime, compressed bytes or independent DOF",
        "dtype_bytes": {"complex128": 16, "float64": 8, "int64": 8},
        "sparse_layout_bytes": parts,
        "sparse_payload_bytes": sum(parts.values()),
        "chunk_columns": chunk_columns,
        "chunk_count": (columns + chunk_columns - 1) // chunk_columns,
        "maximum_chunk_payload_bytes": min(columns, chunk_columns) * sum(per_column.values()),
        "physical_ordered_real_W_bytes": 27 * size**3 * coordinates**degree * 8,
        "physical_symmetric_real_W_bytes": 27 * size**3 * columns * 8,
        "maximum_operator_dimension": max_dimension,
        "single_maximum_operator_complex128_bytes": 16 * max_dimension**2,
        "dense_operator_entry_proxy": sum(count * n**2 for n, count in operators.items()),
        "dense_factorization_cubic_proxy": sum(count * n**3 for n, count in operators.items()),
        "full_solver_resource_feasibility": None,
    }
