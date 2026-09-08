"""Post-run checks of the sealed full census, not a quartic-solver certification.

These tests are deliberately separate from the runner's frozen control sources.
Individual-coordinate monomials are enumerated directly, without either
generating-function implementation or the symmetric block-column kernel.
"""

import json
import subprocess
import sys
from collections import Counter
from copy import deepcopy
from itertools import combinations_with_replacement, product
from math import comb

import numpy as np
import pytest

from research import q012h0_d3q27_quartic_census as r

SEALS = {
    "": "4c7c20a6dbde1aa8c9e7317a7b7750c000d81e429759af51ddfebc836064a0d8",
    "_primary": "15896d87310f64ecaf5cff30e5b6a5e38f44f9b1ea3a5d9fdfc9944fc9699be8",
    "_worker": "8b83a9c6be10352f86351ba47527916647242a50acb9d0262e7b5df8175fe406",
}
WAVES = tuple(wave for wave in product((-1, 0, 1), repeat=3) if any(wave))


@pytest.fixture(scope="module")
def evidence():
    documents = {}
    for suffix, expected in SEALS.items():
        name = "q012h0_d3q27_quartic_census" + suffix + ".json"
        path = r.DEFAULT_OUTPUT.with_name(name)
        assert r.prior._file_sha256(path) == expected
        documents[name] = r.read_json(path)
        r.unseal(documents[name])
    manifest = documents[r.DEFAULT_OUTPUT.name]
    primary = documents[r.child_path(r.DEFAULT_OUTPUT, "enumeration").name]
    worker = documents[r.child_path(r.DEFAULT_OUTPUT, "generating_functions").name]
    assert manifest["source"] == primary["source"] == worker["source"] == r.metadata()
    assert manifest["input"] == primary["input"] == worker["input"] == r.input_state()
    assert primary["process_id"] == 16132 and worker["process_id"] == 36920
    assert manifest["worker_execution"]["process_id"] == worker["process_id"]
    assert manifest["worker_execution"]["exit_code"] == 0
    assert manifest["decision"]["study_gate"] == "passed"
    assert manifest["decision"]["scientific_outcome"] == "accepted"
    assert all(value is True for value in manifest["decision"]["validity_gates"].values())
    assert all(value is True for value in manifest["decision"]["hypothesis_gates"].values())
    return manifest, primary, worker


def test_full_saved_artifacts_reaudit_in_another_process(evidence):
    completed = subprocess.run(
        [sys.executable, "-W", "error", "-m", r.MODULE, "--audit-only"],
        cwd=r.ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.returncode == 0, (completed.stdout, completed.stderr)
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == evidence[0]["decision"]


@pytest.mark.parametrize("degree", (2, 3, 4))
def test_every_coordinate_monomial_matches_both_saved_routes(evidence, degree):
    # Equal wave values occupy distinct coordinate positions, including the
    # two formal coordinates of each shear plane. No eigenvectors are split.
    coordinates = tuple(wave for wave in WAVES for _ in range(4))
    actual = Counter()
    for monomial in combinations_with_replacement(coordinates, degree):
        actual[tuple(map(sum, zip(*monomial, strict=True)))] += 1
    assert len(coordinates) == 104
    assert sum(actual.values()) == comb(104 + degree - 1, degree)
    assert set(actual) == set(product(range(-degree, degree + 1), repeat=3))
    for route in evidence[1:]:
        record = route["degrees"][degree - 2]
        saved = {tuple(row["wave"]): row["columns"] for row in record["coordinates"]}
        assert actual == saved
        weighted = Counter()
        for row in record["joint"]:
            weighted[tuple(row["wave"])] += row["input_columns"] * row["blocks"]
        assert actual == weighted
        assert record["coverage"] == {
            "block_tuples": comb(78 + degree - 1, degree),
            "coordinate_columns": sum(actual.values()),
            "expected_block_tuples": comb(78 + degree - 1, degree),
            "expected_coordinate_columns": sum(actual.values()),
            "passed": True,
        }
        assert sum(row["blocks"] for row in record["joint"]) == comb(78 + degree - 1, degree)


@pytest.mark.parametrize("degree", (2, 3, 4))
@pytest.mark.parametrize("size", (17, 33, 65))
def test_each_grid_sector_and_every_payload_component(evidence, degree, size):
    record = evidence[1]["degrees"][degree - 2]
    grid = record["grids"][(17, 33, 65).index(size)]
    sectors = {name: Counter() for name in ("zero_kinetic", "selected_external", "outside")}
    operators = Counter()
    for row in record["joint"]:
        wave = tuple(row["wave"])
        assert all(abs(component) <= degree < size // 2 for component in wave)
        name = (
            "zero_kinetic" if not any(wave) else "selected_external" if wave in WAVES else "outside"
        )
        sectors[name][row["input_columns"]] += row["blocks"]
        dimension = (27 if name == "outside" else 23) * row["input_columns"]
        operators[dimension] += row["blocks"]
    expected_sectors = [
        {
            "sector": name,
            "external_dimension": 27 if name == "outside" else 23,
            "block_tuples": sum(counts.values()),
            "coordinate_columns": sum(q * count for q, count in counts.items()),
            "input_column_histogram": [
                {"columns": q, "blocks": count} for q, count in sorted(counts.items())
            ],
        }
        for name, counts in sectors.items()
    ]
    assert r.same(
        grid["sectors"],
        {
            "size": size,
            "degree": degree,
            "raw_support_count": (2 * degree + 1) ** 3,
            "canonical_support_count": (2 * degree + 1) ** 3,
            "alias_pairs": [],
            "non_aliasing": True,
            "sectors": expected_sectors,
            "operator_dimension_histogram": [
                {"dimension": n, "blocks": count} for n, count in sorted(operators.items())
            ],
        },
    )
    columns = comb(104 + degree - 1, degree)
    assert sum(sector["coordinate_columns"] for sector in expected_sectors) == columns
    # Allocate only one column per component, never the multi-GiB full arrays.
    per_column = {
        "input_indices_int64": np.empty(degree, dtype=np.int64).nbytes,
        "wave_indices_int64": np.empty(3, dtype=np.int64).nbytes,
        "response_complex128": np.empty(27, dtype=np.complex128).nbytes,
        "forcing_complex128": np.empty(27, dtype=np.complex128).nbytes,
        "reduced_complex128": np.empty(4, dtype=np.complex128).nbytes,
    }
    parts = {name: columns * length for name, length in per_column.items()}
    maximum = max(operators)
    expected_payload = {
        "meaning": (
            "uncompressed array payload only; not RSS, runtime, compressed bytes or independent DOF"
        ),
        "dtype_bytes": {
            name: np.dtype(name).itemsize for name in ("complex128", "float64", "int64")
        },
        "sparse_layout_bytes": parts,
        "sparse_payload_bytes": sum(parts.values()),
        "chunk_columns": 65536,
        "chunk_count": len(range(0, columns, 65536)),
        "maximum_chunk_payload_bytes": min(columns, 65536) * sum(per_column.values()),
        "physical_ordered_real_W_bytes": 27 * size**3 * 104**degree * np.dtype("float64").itemsize,
        "physical_symmetric_real_W_bytes": 27 * size**3 * columns * np.dtype("float64").itemsize,
        "maximum_operator_dimension": maximum,
        "single_maximum_operator_complex128_bytes": maximum**2 * np.dtype("complex128").itemsize,
        "dense_operator_entry_proxy": sum(count * n**2 for n, count in operators.items()),
        "dense_factorization_cubic_proxy": sum(count * n**3 for n, count in operators.items()),
        "full_solver_resource_feasibility": None,
    }
    assert r.same(grid["payload"], expected_payload)
    assert record["all_three_grids_sparse_payload_bytes"] == 3 * sum(parts.values())


@pytest.mark.parametrize("damage", ("summary", "decision", "worker_pid", "extra_field"))
def test_resealed_manifest_tampering_is_not_accepted(tmp_path, evidence, damage):
    manifest, primary, worker = deepcopy(evidence)
    output = tmp_path / r.DEFAULT_OUTPUT.name
    # Keep names and child bytes unchanged; only the root content/seal changes.
    r.save_exclusive(r.child_path(output, "enumeration"), primary)
    r.save_exclusive(r.child_path(output, "generating_functions"), worker)
    if damage == "summary":
        manifest["summary"][2]["all_three_grids_sparse_payload_bytes"] -= 1
    elif damage == "decision":
        manifest["decision"]["hypothesis_gates"]["H1"] = False
    elif damage == "worker_pid":
        manifest["worker_execution"]["process_id"] = primary["process_id"]
    else:
        manifest["unregistered_solver_feasibility"] = True
    r.save_exclusive(output, r.sealed({k: v for k, v in manifest.items() if k != "sha256"}))
    with pytest.raises(ValueError, match="manifest content or derived decision"):
        r.audit_manifest(output)
