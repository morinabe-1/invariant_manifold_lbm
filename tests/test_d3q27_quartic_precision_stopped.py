"""Preserve the second precision attempt and reproduce its normalization stop."""

import numpy as np
import pytest

from research import d3q27_quartic_mp_numbers as numbers
from research import d3q27_quartic_mp_reference as reference
from research import q012h2a_d3q27_quartic_precision as run

OUTPUT = run.OUTPUT.with_name("q012h2a_d3q27_quartic_precision_attempt02.json")
HASHES = {
    "_failure.json": "9e7debac708bd8a8c707fb42111a0b5da43fc40bb2f3c96d74165849ffa8ef54",
    "_n17_primary.json": "340913c9769a57d123fe51226abacf7fca98454baca73b888ed312f059101758",
    "_n17_primary.zip": "04ba4f0bdf68898aaa0bd9008e4f4dc614ed051103d3dca08a6601b420471da6",
    "_n17_worker_failure.json": "4bd9ec19e938ad3f6a65a151d2753e6684e828fcc9efc1bdaf0f32f9cda9481d",
    "_n17_worker.zip": "b82d3e63d9abb94293ef5eb8901d04c8974b677206c9db4b5841611f41d87b9f",
}


def path(suffix):
    return OUTPUT.with_name(OUTPUT.stem + suffix)


@pytest.fixture(scope="module")
def evidence():
    for suffix, checksum in HASHES.items():
        assert run.archive.file_sha(path(suffix)) == checksum
    records = {
        suffix: run.common.read_json(path(suffix)) for suffix in HASHES if suffix.endswith(".json")
    }
    for record in records.values():
        run.common.unseal(record)
    return records


def test_stopped_attempt_keeps_actual_failure_and_available_resources(evidence):
    main, worker = evidence["_failure.json"], evidence["_n17_worker_failure.json"]
    assert main["process_id"] == 30092
    assert main["error"] == "grid 17/worker process 14312 exited 1"
    assert worker["process_id"] == 14312 and worker["completed_tuple_prefix"] == 7
    assert worker["error"] == "saved F4 collision/composition identity differs"
    assert worker["resources"][0]["available_physical_bytes"] == 5994995712
    assert worker["resources"][0]["free_disk_bytes"] == 14515384320
    assert all(all(row["checks"].values()) for row in worker["resources"])
    assert worker["partial_archive_preserved"]
    for record in (main, worker):
        assert record["q012h2a_outcome"] == "inconclusive"
        assert record["q012h2_outcome"] == "not_evaluated"


def test_complete_primary_and_partial_worker_are_not_mixed_into_acceptance(evidence):
    groups = run.selected_groups()
    primary = evidence["_n17_primary.json"]
    assert primary["process_id"] == 36488
    assert primary["groups"] == 698 and primary["columns"] == 1826
    assert primary["source_commit"] == "95a002e3a932cff18935c54e54361a6f1dc3d2c0"
    run.oracle.verify_source_commit(primary["source_commit"], primary["source"])
    run.selection.validate_resources(
        primary["resources"], "all_saved_entries_rebuilt_and_input_rehashed"
    )
    for route, count, expected_columns in (("primary", 698, 1826), ("worker", 7, 25)):
        columns = 0
        with run.archive.Archive(path(f"_n17_{route}.zip"), "r", run.names(count)) as saved:
            header = saved.document("header.json")
            assert header["groups"] == [list(group) for group in groups]
            assert header["source"] == primary["source"]
            for ordinal in range(count):
                group = groups[ordinal]
                document = saved.document(f"tuple_{ordinal:04d}.json")
                values = saved.arrays(f"tuple_{ordinal:04d}.npz")
                run.validation.validate_payload(
                    document,
                    values,
                    group,
                    run.inputs.BLOCK_INDICES,
                    104,
                    route,
                    tuple(document["mutations"]),
                )
                columns += len(values["keys"])
        assert columns == expected_columns
    assert not OUTPUT.exists()
    with pytest.raises(ValueError, match="incomplete manifest marker"):
        run.audit_manifest(OUTPUT, full=False)


@pytest.fixture(scope="module")
def actual_data(evidence):
    data, original, receipt = run.inputs.load(17)
    assert run.same(
        run.parent.static_lower_receipt(receipt),
        run.parent.static_lower_receipt(evidence["_n17_primary.json"]["lower_input"]),
    )
    yield data
    run.parent.recheck_lower(data, original, receipt)


@pytest.mark.parametrize("bits,mismatches", [(128, 22), (192, 21)])
def test_actual_stopping_tuple_reproduces_rounding_order_not_tolerance_failure(
    actual_data, bits, mismatches
):
    group = run.selected_groups()[7]
    assert group == (0, 0, 77, 77)
    with numbers.context(bits):
        current = reference.group(actual_data, group, run.inputs.BLOCK_INDICES, bits)
        columns = reference.columns(group, run.inputs.BLOCK_INDICES, 104)
        assert columns[1] == ((0, 1, 103, 103), 2)
        rows = [
            (reference.raw_forcing(actual_data, slots), reference.mp.sqrt(count))
            for slots, count in columns
        ]
        previous = {
            name: np.column_stack([value[name] * scale for value, scale in rows])
            for name in ("forcing", "collision", "composition")
        }
        for name in ("collision", "composition"):
            assert np.array_equal(current[name], previous[name])
        assert np.count_nonzero(current["forcing"] != previous["forcing"]) == mismatches
        assert np.array_equal(current["forcing"], current["collision"] - current["composition"])
        error = numbers.errors(previous["forcing"], current["forcing"])
        assert 0 < max(error["relative"]) < (1e-37 if bits == 128 else 1e-56)
        assert all(error["passed_1e8"]) and all(error["passed_1e10"])
