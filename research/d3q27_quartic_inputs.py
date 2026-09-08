"""Hash-pinned S0 selection and unchanged full Q012f2 lower-order inputs."""

import gc
from time import perf_counter

import numpy as np

from research import d3q27_chart as chart
from research import d3q27_cubic_chart as cubic
from research import d3q27_quartic_lbm as lbm
from research import q012f2_d3q27_refined_cubic as lower
from research import q012g_d3q27_cubic_chart as cubic_runner
from research import q012h2_d3q27_quartic_selection as selected

SELECTION_SHA = "4f7d196552311338691af9116106f79242a3af126aec3f94d9b7e96089d9bb1f"
SELECTION_COMMIT = "85f0d2e3eafd62055f973ff33492c3eae9dd5f2d"
BLOCK_INDICES = tuple(
    tuple(range(4 * (b // 3) + (0, 2, 3)[b % 3], 4 * (b // 3) + (2, 3, 4)[b % 3]))
    for b in range(78)
)
require, same = selected.require, selected.same


def selection_state(*, full=False):
    raw = selected.DEFAULT_OUTPUT.read_bytes()
    require(selected.oracle.normalized_sha(raw) == SELECTION_SHA, "fixed S0 artifact changed")
    require(
        selected.oracle.normalized_sha(
            selected.oracle.git_bytes(
                "show", f"{SELECTION_COMMIT}:research/artifacts/{selected.DEFAULT_OUTPUT.name}"
            )
        )
        == SELECTION_SHA,
        "S0 selection is not the committed input",
    )
    value = selected.common.read_json(selected.DEFAULT_OUTPUT)
    selected.common.unseal(value)
    require(same(value["source"], selected.metadata()), "sealed S0 source/runtime changed")
    selected.oracle.verify_source_commit(value["source_commit"], value["source"])
    require(
        same(
            value["decision"],
            {"stage": "S0_selection_only", "passed": True, "q012h2_outcome": "not_evaluated"},
        ),
        "S0 did not pass or its scope changed",
    )
    require(
        value["selection"]["groups_per_grid"] == 698
        and value["selection"]["columns_per_grid"] == 1826,
        "fixed pilot size differs",
    )
    rows = value["selection"]["groups"]
    groups = [tuple(row["group"]) for row in rows]
    require(groups == sorted(set(groups)) and len(groups) == 698, "fixed group coverage differs")
    require(sum(row["columns"] for row in rows) == 1826, "fixed column coverage differs")
    if full:
        require(
            same(selected.audit_manifest(selected.DEFAULT_OUTPUT), value["decision"]),
            "full S0/parent saved-entry audit differs",
        )
    return value


def fingerprint(data):
    return {
        "dimension": data.dimension,
        "wave_count": len(data.wave_indices),
        "arrays": {
            **{
                name: chart.array_metadata(getattr(data, name))
                for name in ("waves", "basis", "linear")
            },
            **{
                f"{name}{degree}": chart.array_metadata(getattr(data, name)[degree])
                for name in ("indices", "h", "g")
                for degree in (2, 3)
            },
        },
    }


def load(size, *, sample=None):
    require(type(size) is int and size in (17, 33, 65), "registered grid required")
    source = selection_state()
    start = perf_counter()
    model, rebuilt, old_rows, old_exact = lower.fresh_input(size)
    if sample is not None:
        sample("full_quadratic_rebuild_and_old_audits")
    del old_rows, old_exact
    gc.collect()
    grid = next(
        g for g in lower.read_json(cubic_runner.PRIOR_PATH)["cycle"]["grids"] if g["size"] == size
    )
    require(
        same(rebuilt, grid["input_rebuild"]) and rebuilt["passed"],
        "full paired lower input changed",
    )
    rebuild_seconds = perf_counter() - start
    start = perf_counter()
    arrays, loaded = cubic.load_fibers(
        lower.sibling(cubic_runner.PRIOR_PATH.parent, grid["fiber_archive"]["filename"]),
        grid["fiber_archive"],
    )
    if sample is not None:
        sample("all_192920_cubic_fibers_loaded_and_audited")
    load_seconds = perf_counter() - start
    data = lbm.from_model(model, arrays)
    del model
    gc.collect()
    # Rounded frames and Lambda must be exactly the ones used before selecting
    # difficult tuples. No fresh relabelling or post-selection averaging.
    record, spectra = selected.read_record(selected.DEFAULT_OUTPUT, size, "primary")
    for b, ids in enumerate(BLOCK_INDICES):
        dim = len(ids)
        require(
            np.array_equal(data.basis[:, ids], spectra["block_basis"][b, :, :dim]),
            "selected block basis differs from lower-order input",
        )
        require(
            np.array_equal(data.linear[np.ix_(ids, ids)], spectra["block_dynamics"][b, :dim, :dim]),
            "selected block dynamics differs from lower-order input",
        )
    require(
        data.dimension == 104 and len(data.wave_indices) == 26 and data.width == 4,
        "full 104-coordinate input required",
    )
    receipt = {
        "size": size,
        "selection_sha256": SELECTION_SHA,
        "selection_source_commit": source["source_commit"],
        "input_rebuild": rebuilt,
        "fiber_load": loaded,
        "selection_grid_record_sha256": record["sha256"],
        "lower_arrays": fingerprint(data),
        "fresh_rebuild_seconds": rebuild_seconds,
        "cubic_load_and_audit_seconds": load_seconds,
        "array_storage_bytes_not_RSS": sum(a.nbytes for a in arrays.values()),
        "passed": True,
    }
    del spectra
    if sample is not None:
        sample("full_Taylor_input_and_S0_frame_match")
    # All five original cubic arrays remain resident, including the unused
    # forcing field; the caller can repeat every hash before releasing them.
    return data, arrays, receipt
