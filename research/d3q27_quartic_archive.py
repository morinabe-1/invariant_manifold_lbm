"""Exclusive, full-entry ZIP persistence for Q012h1. Never extract paths."""

import io
import json
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np

from research import q012h0_d3q27_quartic_census as census


def file_sha(path):
    value = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def parse_json(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            census.require(key not in value, "duplicate JSON key")
            value[key] = item
        return value

    value = json.loads(raw, object_pairs_hook=unique)
    census.unseal(value)
    return {key: item for key, item in value.items() if key != "sha256"}


class Archive:
    def __init__(self, path, mode, names):
        census.require(mode in ("r", "x"), "read or exclusive creation only")
        self.names = tuple(names)
        census.require(len(set(self.names)) == len(self.names), "duplicate expected archive name")
        census.require(
            all(
                name and not name.startswith(("/", "\\")) and ".." not in name and "\\" not in name
                for name in self.names
            ),
            "unsafe archive name",
        )
        self.mode = mode
        self.file = ZipFile(path, mode, compression=ZIP_DEFLATED, compresslevel=6)
        self.written = set()
        if mode == "r":
            actual = self.file.namelist()
            if len(actual) != len(self.names) or set(actual) != set(self.names):
                self.file.close()
                raise ValueError("archive full-entry coverage mismatch")

    def __enter__(self):
        return self

    def __exit__(self, kind, value, trace):
        self.file.close()
        if kind is None and self.mode == "x":
            census.require(self.written == set(self.names), "incomplete exclusive archive")

    def put(self, name, content):
        census.require(
            self.mode == "x" and name in self.names and name not in self.written,
            "unregistered or duplicate archive write",
        )
        self.file.writestr(name, content)
        self.written.add(name)

    def put_document(self, name, document):
        self.put(
            name,
            json.dumps(
                census.sealed(document),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8"),
        )

    def document(self, name):
        census.require(name in self.names, "unregistered archive read")
        return parse_json(self.file.read(name))

    def put_arrays(self, name, arrays):
        validate_arrays(arrays)
        stream = io.BytesIO()
        np.savez(stream, **arrays)
        self.put(name, stream.getvalue())

    def arrays(self, name):
        census.require(name in self.names, "unregistered archive array read")
        with np.load(io.BytesIO(self.file.read(name)), allow_pickle=False) as data:
            census.require(len(set(data.files)) == len(data.files), "duplicate array key")
            arrays = {key: data[key] for key in data.files}
        validate_arrays(arrays)
        return arrays


def validate_arrays(arrays):
    census.require(isinstance(arrays, dict) and bool(arrays), "nonempty array mapping required")
    for key, value in arrays.items():
        census.require(type(key) is str and key.isidentifier(), "invalid array key")
        census.require(
            isinstance(value, np.ndarray) and value.ndim in (1, 2) and value.size > 0,
            "nonempty vector or matrix required",
        )
        census.require(
            value.dtype in (np.dtype("complex128"), np.dtype("float64"), np.dtype("int64"))
            and np.isfinite(value).all(),
            "only finite 64-bit numeric arrays accepted",
        )


def arrays_equal(left, right):
    return set(left) == set(right) and all(
        left[name].dtype == right[name].dtype
        and left[name].shape == right[name].shape
        and np.array_equal(left[name], right[name])
        for name in left
    )
