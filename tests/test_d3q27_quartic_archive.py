"""Exclusive persistence and resealed-tampering controls for full numeric entries."""

import io
import json
from zipfile import ZipFile

import numpy as np
import pytest

from research import d3q27_quartic_archive as a
from research import q012h0_d3q27_quartic_census as census


def test_full_arrays_and_exact_json_round_trip_without_loss(tmp_path):
    path = tmp_path / "fresh.zip"
    arrays = {
        "complex": np.array([[1 + 2j, -3j]], dtype=np.complex128),
        "float": np.array([1 / 3], dtype=np.float64),
        "integer": np.array([2**60, -9], dtype=np.int64),
    }
    document = {"fraction": ["135791357913579", "12345678901234"], "bool": True, "int": 1}
    with a.Archive(path, "x", ("record.json", "arrays.npz")) as archive:
        archive.put_document("record.json", document)
        archive.put_arrays("arrays.npz", arrays)
    with a.Archive(path, "r", ("record.json", "arrays.npz")) as archive:
        assert census.same(archive.document("record.json"), document)
        assert a.arrays_equal(archive.arrays("arrays.npz"), arrays)
    checksum = a.file_sha(path)
    with pytest.raises(FileExistsError):
        a.Archive(path, "x", ("record.json", "arrays.npz"))
    assert a.file_sha(path) == checksum


@pytest.mark.parametrize("mutation", ("missing", "extra", "duplicate"))
def test_archive_inventory_rejects_missing_extra_and_duplicate_entries(tmp_path, mutation):
    path = tmp_path / "invalid.zip"
    with ZipFile(path, "x") as archive:
        archive.writestr("one.json", "{}")
        if mutation == "extra":
            archive.writestr("other.json", "{}")
        if mutation == "duplicate":
            with pytest.warns(UserWarning, match="Duplicate"):
                archive.writestr("one.json", "{}")
    with pytest.raises(ValueError, match="coverage"):
        a.Archive(path, "r", ("one.json", "two.json") if mutation == "missing" else ("one.json",))


def test_duplicate_and_partial_writes_preserve_the_failed_archive(tmp_path):
    path = tmp_path / "partial.zip"
    with pytest.raises(ValueError, match="duplicate"):
        with a.Archive(path, "x", ("one.json",)) as archive:
            archive.put_document("one.json", {"value": 1})
            archive.put_document("one.json", {"value": 2})
    assert path.exists()
    other = tmp_path / "incomplete.zip"
    with pytest.raises(ValueError, match="incomplete"):
        with a.Archive(other, "x", ("one.json", "two.json")) as archive:
            archive.put_document("one.json", {"value": 1})
    assert other.exists()


@pytest.mark.parametrize("name", ("../escape.json", "/absolute.json", "bad\\path.json"))
def test_unsafe_names_are_rejected_without_creating_files(tmp_path, name):
    path = tmp_path / "unsafe.zip"
    with pytest.raises(ValueError, match="unsafe"):
        a.Archive(path, "x", (name,))
    assert not path.exists()


@pytest.mark.parametrize(
    "raw",
    (
        '{"x":1,"x":2,"sha256":"x"}',
        '{"value":NaN,"sha256":"x"}',
        '{"value":1,"sha256":"fabricated"}',
    ),
)
def test_json_duplicates_nonfinite_and_bad_seals_are_rejected(raw):
    with pytest.raises(ValueError):
        a.parse_json(raw)


@pytest.mark.parametrize(
    "value",
    (
        np.array([np.nan]),
        np.array([np.inf]),
        np.array(["text"]),
        np.array([object()]),
        np.array([]),
        np.ones((1, 1, 1)),
        np.array([1], dtype=np.float32),
    ),
)
def test_unsupported_or_nonfinite_arrays_are_rejected(value):
    with pytest.raises(ValueError):
        a.validate_arrays({"value": value})


def test_pickle_payload_cannot_be_read(tmp_path):
    path = tmp_path / "pickle.zip"
    stream = io.BytesIO()
    np.savez(stream, value=np.array([{}], dtype=object))
    with ZipFile(path, "x") as archive:
        archive.writestr("arrays.npz", stream.getvalue())
    with a.Archive(path, "r", ("arrays.npz",)) as archive:
        with pytest.raises(ValueError):
            archive.arrays("arrays.npz")


def test_resealing_true_as_one_does_not_make_them_equal():
    left = a.parse_json(json.dumps(census.sealed({"value": True})))
    right = a.parse_json(json.dumps(census.sealed({"value": 1})))
    assert not census.same(left, right)
