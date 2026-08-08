"""Sealed Q010 TT-SVD representation cost and break-even audit."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import platform
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Any

import numpy as np
import numpy.typing as npt

from ttim_lbm.cubic_chart import _array_hash
from ttim_lbm.cubic_continuation import (
    _all_numeric_values_finite,
    _normalized_directions,
    _strict_json_serializable,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.quartic_chart import build_full2d_quartic_model
from ttim_lbm.rational_spectrum import (
    _default_artifact_directory,
    _file_sha256,
)
from ttim_lbm.tensor_train import reconstruct, tt_svd_with_diagnostics
from ttim_lbm.tt_storage_prequalification import (
    MAXIMUM_TENSOR_RECONSTRUCTION_ERROR,
    MAXIMUM_TT_ACTION_ERROR,
    REGISTERED_FIBER_COUNTS,
    REGISTERED_INPUT_HASHES,
    TENSORIZATION_IDS,
    TT_RELATIVE_TOLERANCE,
    _candidate_decomposition,
    _coefficient_families,
    _dense_action,
    _median_absolute_deviation,
    _ordered_tensor,
    _relative_norm,
    _serialized_arrays,
    _sparse_action,
    _sparse_storage,
    _tensorize,
    _tt_action,
    _tt_storage,
)
from ttim_lbm.wave_qtt_prequalification import (
    CANDIDATE_IDS,
    _einsum_path,
    _tensorize_wave_qtt,
    _tt_candidate_action,
    _tt_candidate_arguments,
    _untensorize_wave_qtt,
)

ComplexArray = npt.NDArray[np.complex128]

Q008A_ARTIFACT = "q008a_tt_storage_prequalification.json"
Q008C_ARTIFACT = "q008c_wave_qtt_prequalification.json"
REGISTERED_ARTIFACT_SHA256 = {
    "q008a": "97dd1614dc62a1f58bafb74ddb7ee980763247ddc7e91686637a55f3be05d6f3",
    "q008c": "058dd425504fd0cd003d50e7b7c4a118b0200cb3ac6a15e556468af425a0b73e",
}
REGISTERED_PACKAGE_SOURCE_SHA256 = (
    "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"
)
REGISTERED_QUARTIC_COEFFICIENT_SHA256 = (
    "9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b"
)

FLAT_CANDIDATE_IDS = tuple(TENSORIZATION_IDS)
WAVE_CANDIDATE_IDS = tuple(CANDIDATE_IDS)
TT_CANDIDATE_IDS = FLAT_CANDIDATE_IDS + WAVE_CANDIDATE_IDS
SPARSE_METHOD_ID = "sparse-fiber"
DENSE_METHOD_ID = "ordered-dense-control"
METHOD_IDS = (SPARSE_METHOD_ID, DENSE_METHOD_ID, *TT_CANDIDATE_IDS)

HOLDOUT_SEED = 20260901
HOLDOUT_DIRECTION_COUNT = 16
PRIOR_DIRECTION_CAMPAIGNS = (
    (20260827, 64),
    (20260828, 128),
    (20260829, 64),
    (20260830, 128),
)
OFFLINE_WARMUP_BLOCKS = 1
OFFLINE_MEASURED_BLOCKS = 3
ONLINE_WARMUP_BLOCKS = 1
ONLINE_MEASURED_BLOCKS = 5
MAXIMUM_CHECKSUM_RELATIVE_ERROR = 1.0e-11
MINIMUM_MEDIAN_ONLINE_SLOWDOWN = 2.0


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }


def _digest_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(
        gate.get("passed", False) for gate in gates.values()
    )


def _all_candidate_fidelity_passes(payload: dict[str, Any]) -> bool:
    records = payload.get("cycle", {}).get("degree_records", [])
    return bool(records) and all(
        candidate.get("fidelity_passed", False)
        for record in records
        for candidate in record.get("candidate_records", [])
    )


def _load_registered_inputs(
    artifact_directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    specifications = {
        "q008a": {
            "filename": Q008A_ARTIFACT,
            "diagnostic": (
                "local Fourier coefficient TT storage prequalification"
            ),
            "classification": (
                "registered TT tensorizations do not beat natural quartic "
                "sparse-fiber storage"
            ),
        },
        "q008c": {
            "filename": Q008C_ARTIFACT,
            "diagnostic": (
                "wave-branch and wave-QTT storage prequalification"
            ),
            "classification": (
                "registered wave-factorized TTs do not beat natural quartic "
                "sparse-fiber storage"
            ),
        },
    }
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    current_source = source_metadata()
    for name, specification in specifications.items():
        path = artifact_directory / specification["filename"]
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads[name] = payload
        artifact_sha = _file_sha256(path)
        scope = payload.get("mathematical_scope", {})
        cycle = payload.get("cycle", {})
        record = {
            "filename": specification["filename"],
            "registered_sha256": REGISTERED_ARTIFACT_SHA256[name],
            "sha256": artifact_sha,
            "sha256_matches": (
                artifact_sha == REGISTERED_ARTIFACT_SHA256[name]
            ),
            "source_match": bool(
                payload.get("source") == current_source
                and current_source.get("package_source_sha256")
                == REGISTERED_PACKAGE_SOURCE_SHA256
            ),
            "scope_match": bool(
                scope.get("diagnostic") == specification["diagnostic"]
                and scope.get("construction_grid") == [17, 17]
                and scope.get("omega") == 1.5
                and scope.get("eta") == 0.01
                and scope.get("degrees") == [2, 3, 4]
                and scope.get("complex_mode_count") == 24
                and scope.get("local_output_count") == 9
                and scope.get("tensorization_count") == 4
            ),
            "schema_version": payload.get("schema_version"),
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "cycle_study_validity": cycle.get("study_validity"),
            "cycle_hypothesis_outcome": cycle.get("hypothesis_outcome"),
            "classification_match": (
                cycle.get("scientific_classification")
                == specification["classification"]
            ),
            "all_validity_gates_pass": _all_gates_pass(
                payload,
                "validity_gates",
            ),
            "all_candidate_fidelity_passes": (
                _all_candidate_fidelity_passes(payload)
            ),
            "selected_candidate_is_none": (
                cycle.get("selected_candidate") is None
            ),
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["source_match"]
            and record["scope_match"]
            and record["schema_version"] == 1
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == "rejected"
            and record["cycle_study_validity"] == "passed"
            and record["cycle_hypothesis_outcome"] == "rejected"
            and record["classification_match"]
            and record["all_validity_gates_pass"]
            and record["all_candidate_fidelity_passes"]
            and record["selected_candidate_is_none"]
        )
        records[name] = record
    return payloads, {
        "artifacts": records,
        "registered_package_source_sha256": (
            REGISTERED_PACKAGE_SOURCE_SHA256
        ),
        "observed_package_source_sha256": current_source.get(
            "package_source_sha256"
        ),
        "passed": all(record["passed"] for record in records.values()),
    }


def _quartic_record(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload["cycle"]["degree_records"]
    return next(record for record in records if record["degree"] == 4)


def _registered_storage_by_candidate(
    payloads: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    flat_record = _quartic_record(payloads["q008a"])
    wave_record = _quartic_record(payloads["q008c"])
    sparse = flat_record["natural_sparse_fiber_storage"]
    if sparse != wave_record["natural_sparse_fiber_storage"]:
        raise ValueError("Q008a and Q008c sparse storage records disagree")
    candidates = {
        candidate["candidate_id"]: candidate["storage"]
        for candidate in flat_record["candidate_records"]
    }
    candidates.update(
        {
            candidate["candidate_id"]: candidate["storage"]
            for candidate in wave_record["candidate_records"]
        }
    )
    if tuple(candidates) != TT_CANDIDATE_IDS:
        raise ValueError("registered TT candidate order does not match Q010")
    return sparse, candidates


def _common_input_audit() -> tuple[Any, dict[str, Any], ComplexArray, dict[str, Any]]:
    model = build_full2d_quartic_model()
    families, observed_hashes = _coefficient_families(model)
    family = next(item for item in families if item["degree"] == 4)
    tensor = _ordered_tensor(
        family["indices"],
        family["coefficients"],
        degree=4,
    )
    audit = {
        "registered_hashes": REGISTERED_INPUT_HASHES,
        "observed_hashes": observed_hashes,
        "all_registered_hashes_match": (
            observed_hashes == REGISTERED_INPUT_HASHES
        ),
        "registered_quartic_coefficient_sha256": (
            REGISTERED_QUARTIC_COEFFICIENT_SHA256
        ),
        "observed_quartic_coefficient_sha256": observed_hashes[
            "quartic_chart_coefficients_sha256"
        ],
        "quartic_coefficient_hash_matches": bool(
            observed_hashes["quartic_chart_coefficients_sha256"]
            == REGISTERED_QUARTIC_COEFFICIENT_SHA256
        ),
        "registered_fiber_count": REGISTERED_FIBER_COUNTS[4],
        "observed_fiber_count": len(family["indices"]),
        "ordered_dense_shape": list(tensor.shape),
        "ordered_dense_complex_entry_count": int(tensor.size),
        "ordered_dense_all_finite": bool(np.all(np.isfinite(tensor))),
    }
    audit["passed"] = bool(
        audit["all_registered_hashes_match"]
        and audit["quartic_coefficient_hash_matches"]
        and audit["observed_fiber_count"] == audit["registered_fiber_count"]
        and audit["ordered_dense_shape"] == [9, 24, 24, 24, 24]
        and audit["ordered_dense_all_finite"]
    )
    return model, family, tensor, audit


def _direction_audit(model: Any) -> tuple[ComplexArray, dict[str, Any]]:
    directions = _normalized_directions(
        HOLDOUT_SEED,
        HOLDOUT_DIRECTION_COUNT,
        24,
    )
    prior = np.vstack(
        [
            _normalized_directions(seed, count, 24)
            for seed, count in PRIOR_DIRECTION_CAMPAIGNS
        ]
    )
    duplicate_count = sum(
        any(np.array_equal(direction, previous) for previous in prior)
        for direction in directions
    )
    norm_errors = np.abs(np.linalg.norm(directions, axis=1) - 1.0)
    vectors = np.asarray(
        directions @ model.coordinate_map.T,
        dtype=np.complex128,
    )
    audit = {
        "seed": HOLDOUT_SEED,
        "direction_count": HOLDOUT_DIRECTION_COUNT,
        "direction_sha256": _array_hash(directions),
        "prior_direction_campaigns": [
            {"seed": seed, "count": count}
            for seed, count in PRIOR_DIRECTION_CAMPAIGNS
        ],
        "prior_direction_count": len(prior),
        "exact_duplicate_count_vs_prior": duplicate_count,
        "maximum_norm_error": float(np.max(norm_errors)),
        "vectors_all_finite": bool(np.all(np.isfinite(vectors))),
    }
    audit["passed"] = bool(
        duplicate_count == 0
        and audit["maximum_norm_error"] <= 5.0e-15
        and audit["vectors_all_finite"]
    )
    return vectors, audit


def _dense_storage(tensor: ComplexArray) -> dict[str, Any]:
    dense = np.asarray(tensor, dtype=np.complex128)
    serialized_bytes, roundtrip = _serialized_arrays({"tensor": dense})
    return {
        "complex_entry_count": int(dense.size),
        "stored_real_scalar_count": int(2 * dense.size),
        "raw_array_payload_bytes": int(dense.nbytes),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "serialization_roundtrip_bitwise_equal": roundtrip,
    }


def _fresh_sparse_family(family: dict[str, Any]) -> dict[str, Any]:
    return {
        "degree": 4,
        "indices": np.array(family["indices"], dtype=np.int64, copy=True),
        "multiplicities": np.array(
            family["multiplicities"],
            dtype=np.int64,
            copy=True,
        ),
        "coefficients": np.array(
            family["coefficients"],
            dtype=np.complex128,
            copy=True,
        ),
    }


def _prepare_method(
    method_id: str,
    family: dict[str, Any],
    tensor: ComplexArray,
) -> dict[str, Any]:
    if method_id == SPARSE_METHOD_ID:
        fresh = _fresh_sparse_family(family)
        return {
            "representation": fresh,
            "storage": _sparse_storage(fresh),
        }
    if method_id == DENSE_METHOD_ID:
        dense = np.array(tensor, dtype=np.complex128, copy=True)
        return {
            "representation": dense,
            "storage": _dense_storage(dense),
        }
    if method_id in FLAT_CANDIDATE_IDS:
        _, cores, diagnostics = _candidate_decomposition(
            tensor,
            method_id,
        )
        return {
            "representation": cores,
            "storage": _tt_storage(cores),
            "diagnostics": diagnostics,
        }
    if method_id in WAVE_CANDIDATE_IDS:
        candidate = _tensorize_wave_qtt(tensor, method_id)
        cores, diagnostics = tt_svd_with_diagnostics(
            candidate,
            relative_tolerance=TT_RELATIVE_TOLERANCE,
            max_rank=None,
        )
        return {
            "representation": cores,
            "storage": _tt_storage(cores),
            "diagnostics": diagnostics,
        }
    raise ValueError(f"unknown Q010 method: {method_id}")


def _timed_prepare(
    method_id: str,
    family: dict[str, Any],
    tensor: ComplexArray,
) -> tuple[int, dict[str, Any]]:
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        started = perf_counter_ns()
        prepared = _prepare_method(method_id, family, tensor)
        elapsed = perf_counter_ns() - started
    finally:
        if was_enabled:
            gc.enable()
    return elapsed, prepared


def _offline_campaign(
    family: dict[str, Any],
    tensor: ComplexArray,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    for _ in range(OFFLINE_WARMUP_BLOCKS):
        for method_id in METHOD_IDS:
            elapsed, prepared = _timed_prepare(method_id, family, tensor)
            if elapsed <= 0:
                raise RuntimeError(
                    "offline warmup returned a nonpositive time"
                )
            if not prepared["storage"][
                "serialization_roundtrip_bitwise_equal"
            ]:
                raise RuntimeError("offline warmup serialization failed")
            del prepared
            gc.collect()

    durations: dict[str, list[int]] = {
        method_id: [] for method_id in METHOD_IDS
    }
    storages: dict[str, dict[str, Any]] = {}
    retained: dict[str, dict[str, Any]] = {}
    order_by_block: list[list[str]] = []
    method_ids = list(METHOD_IDS)
    for block in range(OFFLINE_MEASURED_BLOCKS):
        offset = block % len(method_ids)
        order = method_ids[offset:] + method_ids[:offset]
        order_by_block.append(order)
        for method_id in order:
            elapsed, prepared = _timed_prepare(
                method_id,
                family,
                tensor,
            )
            storage = prepared["storage"]
            if method_id in storages and storages[method_id] != storage:
                raise RuntimeError("offline storage record changed by block")
            storages[method_id] = storage
            durations[method_id].append(elapsed)
            retained[method_id] = prepared
            gc.collect()

    records: dict[str, Any] = {}
    for method_id in METHOD_IDS:
        samples = durations[method_id]
        storage = storages[method_id]
        records[method_id] = {
            "nanoseconds_by_block": samples,
            "minimum_nanoseconds": min(samples),
            "maximum_nanoseconds": max(samples),
            "median_nanoseconds": float(median(samples)),
            "median_absolute_deviation_nanoseconds": (
                _median_absolute_deviation(
                    [float(sample) for sample in samples]
                )
            ),
            "all_times_positive_and_finite": bool(
                all(
                    sample > 0 and math.isfinite(float(sample))
                    for sample in samples
                )
            ),
            "storage": storage,
        }
    audit = {
        "timer": "perf_counter_ns",
        "common_model_coefficient_and_dense_materialization_excluded": True,
        "exclusion_is_tt_favorable": True,
        "warmup_block_count": OFFLINE_WARMUP_BLOCKS,
        "measured_block_count": OFFLINE_MEASURED_BLOCKS,
        "order_by_block": order_by_block,
        "method_records": records,
    }
    return audit, retained


def _candidate_action(
    candidate_id: str,
    cores: list[npt.NDArray[Any]],
    vector: ComplexArray,
    wave_paths: dict[str, list[Any]],
) -> ComplexArray:
    if candidate_id in FLAT_CANDIDATE_IDS:
        return _tt_action(cores, vector, candidate_id)
    return _tt_candidate_action(
        cores,
        vector,
        candidate_id,
        path=wave_paths[candidate_id],
    )


def _wave_paths(
    retained: dict[str, dict[str, Any]],
    first_vector: ComplexArray,
) -> dict[str, list[Any]]:
    return {
        candidate_id: _einsum_path(
            _tt_candidate_arguments(
                retained[candidate_id]["representation"],
                first_vector,
                candidate_id,
            )
        )
        for candidate_id in WAVE_CANDIDATE_IDS
    }


def _fidelity_audit(
    family: dict[str, Any],
    tensor: ComplexArray,
    vectors: ComplexArray,
    retained: dict[str, dict[str, Any]],
    registered_sparse: dict[str, Any],
    registered_candidates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    sparse_actions = np.asarray(
        [
            _sparse_action(
                family["indices"],
                family["multiplicities"],
                family["coefficients"],
                vector,
            )
            for vector in vectors
        ],
        dtype=np.complex128,
    )
    dense_actions = np.asarray(
        [_dense_action(tensor, vector) for vector in vectors],
        dtype=np.complex128,
    )
    dense_vs_sparse = max(
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(
            dense_actions,
            sparse_actions,
            strict=True,
        )
    )
    wave_paths = _wave_paths(retained, vectors[0])
    records: dict[str, Any] = {}
    for candidate_id in TT_CANDIDATE_IDS:
        cores = retained[candidate_id]["representation"]
        if candidate_id in FLAT_CANDIDATE_IDS:
            candidate_tensor = _prepare_flat_tensor(
                tensor,
                candidate_id,
            )
            mapping_roundtrip = True
        else:
            candidate_tensor = _tensorize_wave_qtt(tensor, candidate_id)
            mapping_roundtrip = bool(
                np.array_equal(
                    _untensorize_wave_qtt(
                        candidate_tensor,
                        candidate_id,
                    ),
                    tensor,
                )
            )
        reconstruction = reconstruct(cores)
        reconstruction_error = _relative_norm(
            reconstruction - candidate_tensor,
            candidate_tensor,
        )
        observed_actions = np.asarray(
            [
                _candidate_action(
                    candidate_id,
                    cores,
                    vector,
                    wave_paths,
                )
                for vector in vectors
            ],
            dtype=np.complex128,
        )
        action_error_sparse = max(
            _relative_norm(observed - reference, reference)
            for observed, reference in zip(
                observed_actions,
                sparse_actions,
                strict=True,
            )
        )
        action_error_dense = max(
            _relative_norm(observed - reference, reference)
            for observed, reference in zip(
                observed_actions,
                dense_actions,
                strict=True,
            )
        )
        storage = retained[candidate_id]["storage"]
        storage_match = storage == registered_candidates[candidate_id]
        finite = bool(
            np.all(np.isfinite(reconstruction))
            and np.all(np.isfinite(observed_actions))
            and all(np.all(np.isfinite(core)) for core in cores)
        )
        passed = bool(
            mapping_roundtrip
            and reconstruction_error
            <= MAXIMUM_TENSOR_RECONSTRUCTION_ERROR
            and action_error_sparse <= MAXIMUM_TT_ACTION_ERROR
            and action_error_dense <= MAXIMUM_TT_ACTION_ERROR
            and storage_match
            and finite
        )
        records[candidate_id] = {
            "mapping_roundtrip_bitwise_equal": mapping_roundtrip,
            "relative_tensor_reconstruction_error": reconstruction_error,
            "maximum_relative_action_error_vs_sparse": (
                action_error_sparse
            ),
            "maximum_relative_action_error_vs_dense": action_error_dense,
            "fresh_storage_matches_registered": storage_match,
            "all_values_finite": finite,
            "passed": passed,
        }
        del candidate_tensor, reconstruction, observed_actions
    sparse_storage_match = bool(
        retained[SPARSE_METHOD_ID]["storage"] == registered_sparse
    )
    return {
        "dense_maximum_relative_action_error_vs_sparse": (
            dense_vs_sparse
        ),
        "sparse_storage_matches_registered": sparse_storage_match,
        "candidate_records": records,
        "all_candidate_records_passed": all(
            record["passed"] for record in records.values()
        ),
        "passed": bool(
            dense_vs_sparse <= 5.0e-14
            and sparse_storage_match
            and all(record["passed"] for record in records.values())
        ),
    }


def _prepare_flat_tensor(
    tensor: ComplexArray,
    candidate_id: str,
) -> ComplexArray:
    return _tensorize(tensor, candidate_id)


def _online_methods(
    family: dict[str, Any],
    tensor: ComplexArray,
    retained: dict[str, dict[str, Any]],
    vectors: ComplexArray,
) -> dict[str, Callable[[ComplexArray], ComplexArray]]:
    paths = _wave_paths(retained, vectors[0])
    methods: dict[str, Callable[[ComplexArray], ComplexArray]] = {
        SPARSE_METHOD_ID: lambda vector: _sparse_action(
            family["indices"],
            family["multiplicities"],
            family["coefficients"],
            vector,
        ),
        DENSE_METHOD_ID: lambda vector: _dense_action(tensor, vector),
    }
    for candidate_id in TT_CANDIDATE_IDS:
        cores = retained[candidate_id]["representation"]
        methods[candidate_id] = (
            lambda vector,
            name=candidate_id,
            candidate_cores=cores: _candidate_action(
                name,
                candidate_cores,
                vector,
                paths,
            )
        )
    return methods


def _timed_action_block(
    method: Callable[[ComplexArray], ComplexArray],
    vectors: ComplexArray,
) -> tuple[int, float]:
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        started = perf_counter_ns()
        checksum = 0.0
        for vector in vectors:
            checksum += float(np.linalg.norm(method(vector)))
        elapsed = perf_counter_ns() - started
    finally:
        if was_enabled:
            gc.enable()
    return elapsed, checksum


def _online_campaign(
    family: dict[str, Any],
    tensor: ComplexArray,
    vectors: ComplexArray,
    retained: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    methods = _online_methods(family, tensor, retained, vectors)
    method_ids = list(METHOD_IDS)
    for _ in range(ONLINE_WARMUP_BLOCKS):
        for method_id in method_ids:
            elapsed, _ = _timed_action_block(methods[method_id], vectors)
            if elapsed <= 0:
                raise RuntimeError(
                    "online warmup returned a nonpositive time"
                )

    durations: dict[str, list[float]] = {
        method_id: [] for method_id in method_ids
    }
    checksums: dict[str, list[float]] = {
        method_id: [] for method_id in method_ids
    }
    order_by_block: list[list[str]] = []
    for block in range(ONLINE_MEASURED_BLOCKS):
        offset = block % len(method_ids)
        order = method_ids[offset:] + method_ids[:offset]
        order_by_block.append(order)
        for method_id in order:
            elapsed, checksum = _timed_action_block(
                methods[method_id],
                vectors,
            )
            durations[method_id].append(
                elapsed / HOLDOUT_DIRECTION_COUNT
            )
            checksums[method_id].append(checksum)

    reference_checksum = median(checksums[SPARSE_METHOD_ID])
    records: dict[str, Any] = {}
    for method_id in method_ids:
        samples = durations[method_id]
        checksum_errors = [
            _relative_norm(value - reference_checksum, reference_checksum)
            for value in checksums[method_id]
        ]
        records[method_id] = {
            "nanoseconds_per_sample_by_block": samples,
            "minimum_nanoseconds_per_sample": min(samples),
            "maximum_nanoseconds_per_sample": max(samples),
            "median_nanoseconds_per_sample": float(median(samples)),
            "median_absolute_deviation_nanoseconds_per_sample": (
                _median_absolute_deviation(samples)
            ),
            "checksum_by_block": checksums[method_id],
            "maximum_checksum_relative_error_vs_sparse": max(
                checksum_errors
            ),
            "all_times_positive_and_finite": bool(
                all(
                    sample > 0 and math.isfinite(sample)
                    for sample in samples
                )
            ),
        }
    return {
        "seed": HOLDOUT_SEED,
        "direction_count": HOLDOUT_DIRECTION_COUNT,
        "warmup_block_count": ONLINE_WARMUP_BLOCKS,
        "measured_block_count": ONLINE_MEASURED_BLOCKS,
        "order_by_block": order_by_block,
        "timer": "perf_counter_ns",
        "scope": "local homogeneous quartic 9-vector action only",
        "method_records": records,
    }


def _first_median_break_even(
    candidate_offline: float,
    candidate_online: float,
    reference_offline: float,
    reference_online: float,
) -> int | None:
    if candidate_offline <= reference_offline:
        return 0
    if candidate_online >= reference_online:
        return None
    numerator = candidate_offline - reference_offline
    denominator = reference_online - candidate_online
    return max(0, math.ceil(numerator / denominator))


def _break_even_audit(
    offline: dict[str, Any],
    online: dict[str, Any],
) -> dict[str, Any]:
    offline_records = offline["method_records"]
    online_records = online["method_records"]
    sparse_offline = offline_records[SPARSE_METHOD_ID]
    sparse_online = online_records[SPARSE_METHOD_ID]
    dense_offline = offline_records[DENSE_METHOD_ID]
    dense_online = online_records[DENSE_METHOD_ID]
    sparse_storage = sparse_offline["storage"]
    records: dict[str, Any] = {}
    for candidate_id in TT_CANDIDATE_IDS:
        candidate_offline = offline_records[candidate_id]
        candidate_online = online_records[candidate_id]
        storage = candidate_offline["storage"]
        scalar_dominated = bool(
            storage["core_stored_real_scalar_count"]
            > sparse_storage["coefficient_stored_real_scalar_count"]
        )
        raw_payload_dominated = bool(
            storage["raw_array_payload_bytes"]
            > sparse_storage["raw_array_payload_bytes"]
        )
        serialized_dominated = bool(
            storage["uncompressed_npz_serialized_bytes"]
            > sparse_storage["uncompressed_npz_serialized_bytes"]
        )
        storage_beats_sparse = bool(
            storage["core_stored_real_scalar_count"]
            < sparse_storage["coefficient_stored_real_scalar_count"]
            and storage["raw_array_payload_bytes"]
            < sparse_storage["raw_array_payload_bytes"]
            and storage["uncompressed_npz_serialized_bytes"]
            < sparse_storage["uncompressed_npz_serialized_bytes"]
        )
        offline_envelope_dominated = bool(
            candidate_offline["minimum_nanoseconds"]
            > sparse_offline["maximum_nanoseconds"]
        )
        online_envelope_dominated = bool(
            candidate_online["minimum_nanoseconds_per_sample"]
            > sparse_online["maximum_nanoseconds_per_sample"]
        )
        median_online_slowdown = (
            candidate_online["median_nanoseconds_per_sample"]
            / sparse_online["median_nanoseconds_per_sample"]
        )
        robust_no_break_even = bool(
            offline_envelope_dominated and online_envelope_dominated
        )
        median_break_even_sparse = _first_median_break_even(
            candidate_offline["median_nanoseconds"],
            candidate_online["median_nanoseconds_per_sample"],
            sparse_offline["median_nanoseconds"],
            sparse_online["median_nanoseconds_per_sample"],
        )
        median_break_even_dense = _first_median_break_even(
            candidate_offline["median_nanoseconds"],
            candidate_online["median_nanoseconds_per_sample"],
            dense_offline["median_nanoseconds"],
            dense_online["median_nanoseconds_per_sample"],
        )
        records[candidate_id] = {
            "core_stored_real_scalars_exceed_sparse_coefficients": (
                scalar_dominated
            ),
            "raw_array_payload_bytes_exceed_sparse": (
                raw_payload_dominated
            ),
            "serialized_bytes_exceed_sparse": serialized_dominated,
            "storage_strictly_dominated_in_all_registered_metrics": bool(
                scalar_dominated
                and raw_payload_dominated
                and serialized_dominated
            ),
            "storage_strictly_beats_sparse_in_all_registered_metrics": (
                storage_beats_sparse
            ),
            "offline_best_tt_exceeds_worst_sparse": (
                offline_envelope_dominated
            ),
            "online_best_tt_exceeds_worst_sparse": (
                online_envelope_dominated
            ),
            "median_online_slowdown_vs_sparse": (
                median_online_slowdown
            ),
            "minimum_registered_median_slowdown": (
                MINIMUM_MEDIAN_ONLINE_SLOWDOWN
            ),
            "median_slowdown_gate_passed": bool(
                median_online_slowdown
                >= MINIMUM_MEDIAN_ONLINE_SLOWDOWN
            ),
            "robust_no_finite_sparse_baseline_time_break_even": (
                robust_no_break_even
            ),
            "median_time_break_even_vs_sparse_action_count": (
                median_break_even_sparse
            ),
            "median_time_break_even_vs_ordered_dense_action_count": (
                median_break_even_dense
            ),
        }
    storage_dominated = all(
        record["storage_strictly_dominated_in_all_registered_metrics"]
        for record in records.values()
    )
    offline_dominated = all(
        record["offline_best_tt_exceeds_worst_sparse"]
        for record in records.values()
    )
    online_dominated = all(
        record["online_best_tt_exceeds_worst_sparse"]
        and record["median_slowdown_gate_passed"]
        for record in records.values()
    )
    no_break_even = all(
        record[
            "robust_no_finite_sparse_baseline_time_break_even"
        ]
        for record in records.values()
    )
    selected = [
        candidate_id
        for candidate_id, record in records.items()
        if record[
            "storage_strictly_beats_sparse_in_all_registered_metrics"
        ]
        and record["median_time_break_even_vs_sparse_action_count"]
        is not None
    ]
    return {
        "cost_line_definition": "T_m(N)=B_m+N*t_m for integer N>=0",
        "robust_envelope_definition": (
            "candidate minimum offline/online versus sparse maximum "
            "offline/online"
        ),
        "sparse_offline_maximum_nanoseconds": sparse_offline[
            "maximum_nanoseconds"
        ],
        "sparse_online_maximum_nanoseconds_per_sample": sparse_online[
            "maximum_nanoseconds_per_sample"
        ],
        "candidate_records": records,
        "all_tt_storage_strictly_dominated": storage_dominated,
        "all_tt_offline_envelopes_strictly_dominated": offline_dominated,
        "all_tt_online_envelopes_and_slowdowns_strictly_dominated": (
            online_dominated
        ),
        "all_tt_have_robust_no_finite_sparse_time_break_even": (
            no_break_even
        ),
        "candidate_beating_time_and_storage_count": len(selected),
        "candidate_beating_time_and_storage_ids": selected,
        "ordered_dense_control_is_not_full_dense_lbm": True,
        "passed": bool(
            storage_dominated
            and offline_dominated
            and online_dominated
            and no_break_even
            and not selected
        ),
    }


def _protocol_audit(
    offline: dict[str, Any],
    online: dict[str, Any],
) -> dict[str, Any]:
    offline_records = offline["method_records"]
    online_records = online["method_records"]
    all_method_ids_match = bool(
        tuple(offline_records) == METHOD_IDS
        and tuple(online_records) == METHOD_IDS
    )
    offline_counts_match = all(
        len(record["nanoseconds_by_block"])
        == OFFLINE_MEASURED_BLOCKS
        for record in offline_records.values()
    )
    online_counts_match = all(
        len(record["nanoseconds_per_sample_by_block"])
        == ONLINE_MEASURED_BLOCKS
        for record in online_records.values()
    )
    all_times_valid = bool(
        all(
            record["all_times_positive_and_finite"]
            for record in offline_records.values()
        )
        and all(
            record["all_times_positive_and_finite"]
            for record in online_records.values()
        )
    )
    all_roundtrips = all(
        record["storage"]["serialization_roundtrip_bitwise_equal"]
        for record in offline_records.values()
    )
    checksum_passed = all(
        record["maximum_checksum_relative_error_vs_sparse"]
        <= MAXIMUM_CHECKSUM_RELATIVE_ERROR
        for record in online_records.values()
    )
    offline_orders_match = bool(
        len(offline["order_by_block"]) == OFFLINE_MEASURED_BLOCKS
        and all(
            len(order) == len(METHOD_IDS)
            and set(order) == set(METHOD_IDS)
            for order in offline["order_by_block"]
        )
    )
    online_orders_match = bool(
        len(online["order_by_block"]) == ONLINE_MEASURED_BLOCKS
        and all(
            len(order) == len(METHOD_IDS)
            and set(order) == set(METHOD_IDS)
            for order in online["order_by_block"]
        )
    )
    return {
        "all_method_ids_match": all_method_ids_match,
        "offline_counts_match": offline_counts_match,
        "online_counts_match": online_counts_match,
        "all_times_positive_and_finite": all_times_valid,
        "all_serialization_roundtrips_bitwise_equal": all_roundtrips,
        "all_checksum_errors_within_registered_bound": checksum_passed,
        "offline_orders_are_complete_cyclic_permutations": (
            offline_orders_match
        ),
        "online_orders_are_complete_cyclic_permutations": (
            online_orders_match
        ),
        "passed": bool(
            all_method_ids_match
            and offline_counts_match
            and online_counts_match
            and all_times_valid
            and all_roundtrips
            and checksum_passed
            and offline_orders_match
            and online_orders_match
        ),
    }


def run_representation_cost_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_audit = _load_registered_inputs(directory)
    registered_sparse, registered_candidates = (
        _registered_storage_by_candidate(payloads)
    )
    model, family, tensor, common_input = _common_input_audit()
    vectors, direction = _direction_audit(model)
    offline, retained = _offline_campaign(family, tensor)
    fidelity = _fidelity_audit(
        family,
        tensor,
        vectors,
        retained,
        registered_sparse,
        registered_candidates,
    )
    online = _online_campaign(family, tensor, vectors, retained)
    protocol = _protocol_audit(offline, online)
    break_even = _break_even_audit(offline, online)

    input_digest_payload = {
        "artifact_sha256": {
            name: record["sha256"]
            for name, record in input_audit["artifacts"].items()
        },
        "package_source_sha256": REGISTERED_PACKAGE_SOURCE_SHA256,
        "quartic_coefficient_sha256": (
            REGISTERED_QUARTIC_COEFFICIENT_SHA256
        ),
        "candidate_ids": list(TT_CANDIDATE_IDS),
        "method_ids": list(METHOD_IDS),
        "holdout": direction,
        "offline_protocol": {
            "warmup_blocks": OFFLINE_WARMUP_BLOCKS,
            "measured_blocks": OFFLINE_MEASURED_BLOCKS,
        },
        "online_protocol": {
            "warmup_blocks": ONLINE_WARMUP_BLOCKS,
            "measured_blocks": ONLINE_MEASURED_BLOCKS,
            "checksum_tolerance": MAXIMUM_CHECKSUM_RELATIVE_ERROR,
            "minimum_median_slowdown": (
                MINIMUM_MEDIAN_ONLINE_SLOWDOWN
            ),
        },
    }
    input_digest = _digest_payload(input_digest_payload)
    result_digest_payload = {
        "input_digest": input_digest,
        "common_input": common_input,
        "fidelity": fidelity,
        "offline": offline,
        "online": online,
        "protocol": protocol,
        "break_even": break_even,
    }
    result_digest = _digest_payload(result_digest_payload)
    digests_reproducible = bool(
        input_digest == _digest_payload(input_digest_payload)
        and result_digest == _digest_payload(result_digest_payload)
        and len(input_digest) == 64
        and len(result_digest) == 64
    )
    serializable_probe = {
        "input_audit": input_audit,
        "common_input": common_input,
        "direction": direction,
        "fidelity": fidelity,
        "offline": offline,
        "online": online,
        "protocol": protocol,
        "break_even": break_even,
    }
    strict_json = bool(
        _all_numeric_values_finite(serializable_probe)
        and _strict_json_serializable(serializable_probe)
    )

    validity_gates = {
        "registered_q008a_q008c_inputs": {
            "passed": input_audit["passed"],
            "threshold": (
                "artifact SHA, package source, scope, rejected outcome, "
                "validity, fidelity and null selection match"
            ),
            "value": input_audit["passed"],
        },
        "fresh_quartic_build_and_storage": {
            "passed": bool(common_input["passed"] and fidelity["passed"]),
            "threshold": (
                "coefficient hash, fiber count, dense expansion, mappings, "
                "ranks, storage and fresh fidelity reproduce"
            ),
            "value": {
                "common_input": common_input["passed"],
                "fidelity": fidelity["passed"],
            },
        },
        "independent_holdout_directions": {
            "passed": direction["passed"],
            "threshold": (
                "16 normalized seed-20260901 directions, exact duplicate "
                "count zero versus all Q008a/Q008c campaigns"
            ),
            "value": direction["passed"],
        },
        "finite_sparse_dense_tt_actions": {
            "passed": bool(
                fidelity["passed"]
                and all(
                    record[
                        "maximum_checksum_relative_error_vs_sparse"
                    ]
                    <= MAXIMUM_CHECKSUM_RELATIVE_ERROR
                    for record in online["method_records"].values()
                )
            ),
            "threshold": (
                "fresh action fidelity and every block checksum relative "
                "error <=1e-11"
            ),
            "value": fidelity["all_candidate_records_passed"],
        },
        "registered_cost_protocol": {
            "passed": protocol["passed"],
            "threshold": (
                "offline 1+3 and online 1+5 blocks, cyclic orders, positive "
                "times, storage records and serialization reproduce"
            ),
            "value": protocol["passed"],
        },
        "finite_strict_json_and_digests": {
            "passed": bool(strict_json and digests_reproducible),
            "threshold": (
                "all records are finite strict JSON and input/result "
                "digests reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests": digests_reproducible,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "all_tt_storage_metrics_exceed_sparse": {
            "passed": bool(
                validity_passed
                and break_even["all_tt_storage_strictly_dominated"]
            ),
            "threshold": (
                "all eight TT stored scalars, raw payload bytes and "
                "serialized bytes exceed natural sparse-fiber"
            ),
            "value": break_even["all_tt_storage_strictly_dominated"],
        },
        "all_tt_offline_envelopes_exceed_sparse": {
            "passed": bool(
                validity_passed
                and break_even[
                    "all_tt_offline_envelopes_strictly_dominated"
                ]
            ),
            "threshold": "min TT offline > max sparse offline",
            "value": break_even[
                "all_tt_offline_envelopes_strictly_dominated"
            ],
        },
        "all_tt_online_envelopes_and_slowdowns_exceed_sparse": {
            "passed": bool(
                validity_passed
                and break_even[
                    "all_tt_online_envelopes_and_slowdowns_strictly_dominated"
                ]
            ),
            "threshold": (
                "min TT online > max sparse online and median slowdown >=2"
            ),
            "value": break_even[
                "all_tt_online_envelopes_and_slowdowns_strictly_dominated"
            ],
        },
        "all_tt_have_no_finite_sparse_time_break_even": {
            "passed": bool(
                validity_passed
                and break_even[
                    "all_tt_have_robust_no_finite_sparse_time_break_even"
                ]
            ),
            "threshold": (
                "best registered TT cost line exceeds worst registered "
                "sparse cost line for every integer N>=0"
            ),
            "value": break_even[
                "all_tt_have_robust_no_finite_sparse_time_break_even"
            ],
        },
        "no_candidate_beats_sparse_time_and_storage": {
            "passed": bool(
                validity_passed
                and break_even[
                    "candidate_beating_time_and_storage_count"
                ]
                == 0
            ),
            "threshold": "joint time-and-storage passing candidate count=0",
            "value": break_even[
                "candidate_beating_time_and_storage_count"
            ],
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    any_sparse_median_break_even = any(
        record["median_time_break_even_vs_sparse_action_count"]
        is not None
        for record in break_even["candidate_records"].values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q010 representation cost audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "sealed TT-SVD path is cost-dominated by natural quartic "
            "sparse-fiber"
        )
    elif any_sparse_median_break_even:
        outcome = "not_certified"
        classification = (
            "time break-even observed but sparse storage still dominates"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered timing envelope does not certify TT-SVD cost "
            "dominance"
        )

    return {
        "question": (
            "Does any of the eight sealed faithful quartic TT-SVD "
            "representations have a finite total-time break-even and lower "
            "payload than the natural sparse-fiber baseline?"
        ),
        "registered_parameters": {
            "grid": [17, 17],
            "omega": 1.5,
            "eta": 0.01,
            "degree": 4,
            "complex_input_mode_count": 24,
            "local_output_count": 9,
            "natural_fiber_count": 17550,
            "tt_relative_tolerance": TT_RELATIVE_TOLERANCE,
            "tt_maximum_rank": None,
            "tt_candidate_ids": list(TT_CANDIDATE_IDS),
            "holdout_seed": HOLDOUT_SEED,
            "holdout_direction_count": HOLDOUT_DIRECTION_COUNT,
            "offline_warmup_measured_blocks": [
                OFFLINE_WARMUP_BLOCKS,
                OFFLINE_MEASURED_BLOCKS,
            ],
            "online_warmup_measured_blocks": [
                ONLINE_WARMUP_BLOCKS,
                ONLINE_MEASURED_BLOCKS,
            ],
            "maximum_checksum_relative_error": (
                MAXIMUM_CHECKSUM_RELATIVE_ERROR
            ),
            "minimum_median_online_slowdown": (
                MINIMUM_MEDIAN_ONLINE_SLOWDOWN
            ),
        },
        "input_audit": input_audit,
        "common_input_audit": common_input,
        "direction_audit": direction,
        "fresh_fidelity_audit": fidelity,
        "offline_cost_campaign": offline,
        "online_cost_campaign": online,
        "protocol_audit": protocol,
        "break_even_audit": break_even,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "selected_candidate": None,
        "decision_consequence": {
            "fixed_q007c1_tt_svd_path_cost_dominated_in_campaign": bool(
                validity_passed and hypotheses_passed
            ),
            "q009_tt_cross_remains_held_for_fixed_coefficients": True,
            "natural_sparse_fiber_remains_mandatory_baseline": True,
            "ordered_dense_control_interpreted_as_full_lbm": False,
        },
        "claim_boundary": (
            "This is an environment-specific finite cost campaign for one "
            "local homogeneous quartic 9-vector action and eight full-rank "
            "TT-SVD tensorizations of the fixed Q007c1 coefficients. Common "
            "model/coefficient construction and ordered-dense materialization "
            "are excluded in a TT-favorable way. Stored core scalars are not "
            "called independent degrees of freedom. The ordered-dense "
            "coefficient oracle is not full dense LBM. This does not certify "
            "a full reduced-chart or LBM rollout, MPFR cost, GPU or threaded "
            "scaling, compressed rounding, TT-cross, another tensorization, "
            "grid, machine, asymptotic complexity, D3Q27, or energy use."
        ),
        "preserved_prior_outcomes": {
            "q008a_storage_rejection_changed": False,
            "q008c_storage_rejection_changed": False,
            "q009_hold_changed": False,
            "q007ab_forward_shadowing_changed": False,
        },
        "next_change": (
            "If accepted, close Q010 for the sealed TT-SVD path and return "
            "to the remaining non-TT mathematical or boundary/forcing gates; "
            "any new representation requires a separately preregistered "
            "candidate family."
        ),
    }


def run_q010_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_representation_cost_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": {
            **runtime_metadata(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_implementation": platform.python_implementation(),
            "garbage_collector_disabled_inside_timed_blocks": True,
        },
        "mathematical_scope": {
            "diagnostic": (
                "environment-specific TT-SVD representation cost and "
                "break-even audit"
            ),
            "construction_grid": [17, 17],
            "omega": 1.5,
            "eta": 0.01,
            "coefficient_family": (
                "fixed Q007c1 local homogeneous quartic 9-vector correction"
            ),
            "candidate_count": len(TT_CANDIDATE_IDS),
            "mandatory_baseline": "natural quartic sparse-fiber",
            "timing_scope": (
                "offline representation preparation and in-memory local "
                "quartic action"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q010_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
