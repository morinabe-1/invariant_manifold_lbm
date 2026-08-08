"""Sealed Q008c wave/branch and wave-QTT storage prequalification audit."""

from __future__ import annotations

import gc
from collections.abc import Sequence
from statistics import median
from time import perf_counter_ns
from typing import Any

import numpy as np
import numpy.typing as npt

from .cubic_chart import _array_hash
from .cubic_continuation import (
    _all_numeric_values_finite,
    _normalized_directions,
    _strict_json_serializable,
)
from .full2d_chart import MODE_ORDER, REDUCED_DIMENSION, WAVE_ORDER
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model
from .tensor_train import reconstruct, tt_svd_with_diagnostics
from .tt_storage_prequalification import (
    MAXIMUM_DENSE_ACTION_ERROR,
    MAXIMUM_TENSOR_RECONSTRUCTION_ERROR,
    MAXIMUM_TT_ACTION_ERROR,
    REGISTERED_FIBER_COUNTS,
    REGISTERED_INPUT_HASHES,
    TT_RELATIVE_TOLERANCE,
    _candidate_decomposition,
    _coefficient_families,
    _dense_action,
    _median_absolute_deviation,
    _ordered_tensor,
    _relative_norm,
    _sparse_action,
    _sparse_storage,
    _tt_storage,
)

ComplexArray = npt.NDArray[np.complex128]
IntegerArray = npt.NDArray[np.int64]

CANDIDATE_IDS = (
    "wave-branch-tuple-major",
    "wave-branch-factor-major",
    "wave-qtt-tuple-major",
    "wave-qtt-scale-interleaved",
)
ACTION_SEED = 20260829
ACTION_DIRECTION_COUNT = 64
TIMING_SEED = 20260830
TIMING_DIRECTION_COUNT = 128
TIMING_WARMUP_BLOCKS = 2
TIMING_MEASURED_BLOCKS = 7
UPSTREAM_ACTION_SEED = 20260827
UPSTREAM_TIMING_SEED = 20260828
UPSTREAM_FLAT_Q_LAST_RANKS = {
    2: [1, 24, 9, 1],
    3: [1, 24, 216, 9, 1],
    4: [1, 24, 300, 216, 9, 1],
}
UPSTREAM_FLAT_Q_LAST_CORE_REAL_SCALARS = {
    2: 11682,
    3: 343458,
    4: 3550626,
}
UPSTREAM_FLAT_Q_LAST_SERIALIZED_BYTES = {
    2: 94772,
    3: 2749244,
    4: 28406852,
}
REGISTERED_QUARTIC_SPARSE_REAL_SCALARS = 315900
REGISTERED_QUARTIC_SPARSE_SERIALIZED_BYTES = 2615734


def _input_mode_spec(degree: int, candidate_id: str) -> list[tuple[int, str]]:
    if degree <= 0:
        raise ValueError("degree must be positive")
    if candidate_id == "flat-q-last":
        return [(coordinate, "flat") for coordinate in range(degree)]
    if candidate_id == "wave-branch-tuple-major":
        return [
            item
            for coordinate in range(degree)
            for item in ((coordinate, "wave"), (coordinate, "branch"))
        ]
    if candidate_id == "wave-branch-factor-major":
        return [
            *((coordinate, "wave") for coordinate in range(degree)),
            *((coordinate, "branch") for coordinate in range(degree)),
        ]
    if candidate_id == "wave-qtt-tuple-major":
        return [
            item
            for coordinate in range(degree)
            for item in (
                (coordinate, "s2"),
                (coordinate, "s1"),
                (coordinate, "s0"),
                (coordinate, "branch"),
            )
        ]
    if candidate_id == "wave-qtt-scale-interleaved":
        return [
            *(
                (coordinate, bit)
                for bit in ("s2", "s1", "s0")
                for coordinate in range(degree)
            ),
            *((coordinate, "branch") for coordinate in range(degree)),
        ]
    raise ValueError(f"unknown registered tensorization: {candidate_id}")


def _candidate_mode_shape(degree: int, candidate_id: str) -> tuple[int, ...]:
    sizes = {"flat": 24, "wave": 8, "branch": 3, "s2": 2, "s1": 2, "s0": 2}
    return tuple(sizes[component] for _, component in _input_mode_spec(degree, candidate_id)) + (
        9,
    )


def _tensorize_wave_qtt(tensor: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    dense = np.asarray(tensor, dtype=np.complex128)
    degree = dense.ndim - 1
    if dense.shape != (9,) + (REDUCED_DIMENSION,) * degree:
        raise ValueError("ordered tensor must have a local D2Q9 output axis")
    q_last = np.moveaxis(dense, 0, -1)
    wave_branch = q_last.reshape((8, 3) * degree + (9,))
    if candidate_id == "wave-branch-tuple-major":
        candidate = wave_branch
    elif candidate_id == "wave-branch-factor-major":
        axes = [2 * coordinate for coordinate in range(degree)]
        axes += [2 * coordinate + 1 for coordinate in range(degree)]
        candidate = np.transpose(wave_branch, axes + [2 * degree])
    else:
        wave_qtt = wave_branch.reshape((2, 2, 2, 3) * degree + (9,))
        if candidate_id == "wave-qtt-tuple-major":
            candidate = wave_qtt
        elif candidate_id == "wave-qtt-scale-interleaved":
            axes = [4 * coordinate + bit for bit in range(3) for coordinate in range(degree)]
            axes += [4 * coordinate + 3 for coordinate in range(degree)]
            candidate = np.transpose(wave_qtt, axes + [4 * degree])
        else:
            raise ValueError(f"unknown registered tensorization: {candidate_id}")
    return np.asarray(candidate, dtype=np.complex128)


def _untensorize_wave_qtt(tensor: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    candidate = np.asarray(tensor, dtype=np.complex128)
    input_mode_count = candidate.ndim - 1
    if candidate_id.startswith("wave-branch-"):
        if input_mode_count % 2:
            raise ValueError("wave-branch tensor must have two modes per coordinate")
        degree = input_mode_count // 2
        if candidate.shape != _candidate_mode_shape(degree, candidate_id):
            raise ValueError("wave-branch tensor has the wrong registered shape")
        if candidate_id == "wave-branch-factor-major":
            axes = [coordinate for pair in range(degree) for coordinate in (pair, degree + pair)]
            candidate = np.transpose(candidate, axes + [2 * degree])
        q_last = candidate.reshape((REDUCED_DIMENSION,) * degree + (9,))
    elif candidate_id.startswith("wave-qtt-"):
        if input_mode_count % 4:
            raise ValueError("wave-QTT tensor must have four modes per coordinate")
        degree = input_mode_count // 4
        if candidate.shape != _candidate_mode_shape(degree, candidate_id):
            raise ValueError("wave-QTT tensor has the wrong registered shape")
        if candidate_id == "wave-qtt-scale-interleaved":
            source_spec = _input_mode_spec(degree, candidate_id)
            target_spec = _input_mode_spec(degree, "wave-qtt-tuple-major")
            positions = {item: index for index, item in enumerate(source_spec)}
            axes = [positions[item] for item in target_spec]
            candidate = np.transpose(candidate, axes + [4 * degree])
        q_last = candidate.reshape((REDUCED_DIMENSION,) * degree + (9,))
    else:
        raise ValueError(f"unknown registered tensorization: {candidate_id}")
    return np.asarray(np.moveaxis(q_last, -1, 0), dtype=np.complex128)


def _coordinate_feature(vector: ComplexArray, candidate_id: str) -> ComplexArray:
    if candidate_id == "flat-q-last":
        return vector
    if candidate_id.startswith("wave-branch-"):
        return vector.reshape(8, 3)
    if candidate_id.startswith("wave-qtt-"):
        return vector.reshape(2, 2, 2, 3)
    raise ValueError(f"unknown registered tensorization: {candidate_id}")


def _coordinate_component_order(candidate_id: str) -> tuple[str, ...]:
    if candidate_id == "flat-q-last":
        return ("flat",)
    if candidate_id.startswith("wave-branch-"):
        return ("wave", "branch")
    if candidate_id.startswith("wave-qtt-"):
        return ("s2", "s1", "s0", "branch")
    raise ValueError(f"unknown registered tensorization: {candidate_id}")


def _feature_operands(
    vector: npt.ArrayLike,
    candidate_id: str,
    degree: int,
    physical_labels: Sequence[int],
) -> list[Any]:
    value = np.asarray(vector, dtype=np.complex128)
    if value.shape != (REDUCED_DIMENSION,):
        raise ValueError("action vector must have length 24")
    spec = _input_mode_spec(degree, candidate_id)
    order = _coordinate_component_order(candidate_id)
    feature = _coordinate_feature(value, candidate_id)
    operands: list[Any] = []
    for coordinate in range(degree):
        labels = [
            physical_labels[spec.index((coordinate, component))]
            for component in order
        ]
        operands.extend((feature, labels))
    return operands


def _dense_candidate_arguments(
    tensor: npt.ArrayLike,
    vector: npt.ArrayLike,
    candidate_id: str,
) -> list[Any]:
    dense = np.asarray(tensor, dtype=np.complex128)
    spec_length = dense.ndim - 1
    if candidate_id == "flat-q-last":
        degree = spec_length
    elif candidate_id.startswith("wave-branch-"):
        degree = spec_length // 2
    else:
        degree = spec_length // 4
    if dense.shape != _candidate_mode_shape(degree, candidate_id):
        raise ValueError("candidate tensor has the wrong registered shape")
    physical_labels = list(range(dense.ndim))
    arguments: list[Any] = [dense, physical_labels]
    arguments.extend(
        _feature_operands(vector, candidate_id, degree, physical_labels[:-1])
    )
    arguments.append([physical_labels[-1]])
    return arguments


def _tt_candidate_arguments(
    cores: Sequence[npt.ArrayLike],
    vector: npt.ArrayLike,
    candidate_id: str,
) -> list[Any]:
    converted = [np.asarray(core, dtype=np.complex128) for core in cores]
    input_mode_count = len(converted) - 1
    if candidate_id == "flat-q-last":
        degree = input_mode_count
    elif candidate_id.startswith("wave-branch-"):
        if input_mode_count % 2:
            raise ValueError("wave-branch TT must have two input cores per coordinate")
        degree = input_mode_count // 2
    else:
        if input_mode_count % 4:
            raise ValueError("wave-QTT must have four input cores per coordinate")
        degree = input_mode_count // 4
    if tuple(core.shape[1] for core in converted) != _candidate_mode_shape(
        degree, candidate_id
    ):
        raise ValueError("TT cores have the wrong registered mode shape")
    physical_labels = list(range(len(converted)))
    bond_labels = list(range(len(converted), 2 * len(converted) + 1))
    arguments: list[Any] = []
    for index, core in enumerate(converted):
        arguments.extend(
            (core, [bond_labels[index], physical_labels[index], bond_labels[index + 1]])
        )
    arguments.extend(
        _feature_operands(vector, candidate_id, degree, physical_labels[:-1])
    )
    arguments.append([physical_labels[-1]])
    return arguments


def _einsum_path(arguments: list[Any]) -> list[Any]:
    path, _ = np.einsum_path(*arguments, optimize="greedy")
    return path


def _dense_candidate_action(
    tensor: npt.ArrayLike,
    vector: npt.ArrayLike,
    candidate_id: str,
    *,
    path: list[Any] | str = "greedy",
) -> ComplexArray:
    return np.asarray(
        np.einsum(*_dense_candidate_arguments(tensor, vector, candidate_id), optimize=path),
        dtype=np.complex128,
    )


def _tt_candidate_action(
    cores: Sequence[npt.ArrayLike],
    vector: npt.ArrayLike,
    candidate_id: str,
    *,
    path: list[Any] | str = "greedy",
) -> ComplexArray:
    return np.asarray(
        np.einsum(*_tt_candidate_arguments(cores, vector, candidate_id), optimize=path),
        dtype=np.complex128,
    )


def _direction_duplicate_count(directions: ComplexArray) -> int:
    prior = np.vstack(
        (
            _normalized_directions(
                UPSTREAM_ACTION_SEED,
                ACTION_DIRECTION_COUNT,
                REDUCED_DIMENSION,
            ),
            _normalized_directions(
                UPSTREAM_TIMING_SEED,
                TIMING_DIRECTION_COUNT,
                REDUCED_DIMENSION,
            ),
        )
    )
    return sum(
        any(np.array_equal(direction, previous) for previous in prior)
        for direction in directions
    )


def _flat_control_audit(
    tensor: ComplexArray,
    degree: int,
    vectors: ComplexArray,
    sparse_actions: ComplexArray,
) -> tuple[dict[str, Any], list[npt.NDArray[Any]]]:
    candidate_tensor, cores, diagnostics = _candidate_decomposition(
        tensor,
        "flat-q-last",
    )
    reconstruction = reconstruct(cores)
    tensor_error = _relative_norm(reconstruction - candidate_tensor, candidate_tensor)
    arguments = _tt_candidate_arguments(cores, vectors[0], "flat-q-last")
    path = _einsum_path(arguments)
    actions = np.asarray(
        [
            _tt_candidate_action(cores, vector, "flat-q-last", path=path)
            for vector in vectors
        ],
        dtype=np.complex128,
    )
    action_error = max(
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(actions, sparse_actions, strict=True)
    )
    storage = _tt_storage(cores)
    exact_identity = bool(
        storage["tt_ranks"] == UPSTREAM_FLAT_Q_LAST_RANKS[degree]
        and storage["core_stored_real_scalar_count"]
        == UPSTREAM_FLAT_Q_LAST_CORE_REAL_SCALARS[degree]
        and storage["uncompressed_npz_serialized_bytes"]
        == UPSTREAM_FLAT_Q_LAST_SERIALIZED_BYTES[degree]
    )
    all_finite = bool(
        all(np.all(np.isfinite(core)) for core in cores)
        and np.all(np.isfinite(reconstruction))
        and np.all(np.isfinite(actions))
        and diagnostics["all_singular_values_finite"]
        and _all_numeric_values_finite(diagnostics)
    )
    del reconstruction
    return (
        {
            "candidate_id": "flat-q-last",
            "degree": degree,
            "relative_tensor_reconstruction_error": tensor_error,
            "maximum_relative_action_error_vs_sparse": action_error,
            "tt_svd_diagnostics": diagnostics,
            "storage": storage,
            "registered_identity_exact": exact_identity,
            "fidelity_passed": bool(
                tensor_error <= MAXIMUM_TENSOR_RECONSTRUCTION_ERROR
                and action_error <= MAXIMUM_TT_ACTION_ERROR
                and storage["serialization_roundtrip_bitwise_equal"]
                and all_finite
            ),
            "all_values_finite": all_finite,
        },
        cores,
    )


def _candidate_audit(
    tensor: ComplexArray,
    candidate_id: str,
    vectors: ComplexArray,
    sparse_actions: ComplexArray,
    canonical_dense_actions: ComplexArray,
) -> tuple[dict[str, Any], list[npt.NDArray[Any]]]:
    started = perf_counter_ns()
    candidate_tensor = _tensorize_wave_qtt(tensor, candidate_id)
    cores, diagnostics = tt_svd_with_diagnostics(
        candidate_tensor,
        relative_tolerance=TT_RELATIVE_TOLERANCE,
        max_rank=None,
    )
    elapsed = perf_counter_ns() - started
    mapping_roundtrip = _untensorize_wave_qtt(candidate_tensor, candidate_id)
    mapping_bitwise_equal = bool(np.array_equal(mapping_roundtrip, tensor))
    dense_path = _einsum_path(
        _dense_candidate_arguments(candidate_tensor, vectors[0], candidate_id)
    )
    candidate_dense_actions = np.asarray(
        [
            _dense_candidate_action(
                candidate_tensor,
                vector,
                candidate_id,
                path=dense_path,
            )
            for vector in vectors
        ],
        dtype=np.complex128,
    )
    dense_mapping_errors = [
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(
            candidate_dense_actions,
            canonical_dense_actions,
            strict=True,
        )
    ]
    reconstruction = reconstruct(cores)
    tensor_error = _relative_norm(reconstruction - candidate_tensor, candidate_tensor)
    tt_path = _einsum_path(_tt_candidate_arguments(cores, vectors[0], candidate_id))
    tt_actions = np.asarray(
        [
            _tt_candidate_action(cores, vector, candidate_id, path=tt_path)
            for vector in vectors
        ],
        dtype=np.complex128,
    )
    sparse_errors = [
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(tt_actions, sparse_actions, strict=True)
    ]
    dense_errors = [
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(
            tt_actions,
            candidate_dense_actions,
            strict=True,
        )
    ]
    storage = _tt_storage(cores)
    all_finite = bool(
        all(np.all(np.isfinite(core)) for core in cores)
        and np.all(np.isfinite(reconstruction))
        and np.all(np.isfinite(candidate_dense_actions))
        and np.all(np.isfinite(tt_actions))
        and diagnostics["all_singular_values_finite"]
        and _all_numeric_values_finite(diagnostics)
    )
    maximum_mapping_error = max(dense_mapping_errors)
    record = {
        "candidate_id": candidate_id,
        "tensor_shape": list(candidate_tensor.shape),
        "mapping_roundtrip_bitwise_equal": mapping_bitwise_equal,
        "maximum_relative_dense_mapping_action_error": maximum_mapping_error,
        "relative_tensor_reconstruction_error": tensor_error,
        "maximum_relative_action_error_vs_sparse": max(sparse_errors),
        "maximum_relative_action_error_vs_candidate_dense": max(dense_errors),
        "all_values_finite": all_finite,
        "tt_svd_wall_time_ns": elapsed,
        "tt_svd_diagnostics": diagnostics,
        "storage": storage,
        "fidelity_passed": bool(
            mapping_bitwise_equal
            and maximum_mapping_error <= MAXIMUM_DENSE_ACTION_ERROR
            and tensor_error <= MAXIMUM_TENSOR_RECONSTRUCTION_ERROR
            and max(sparse_errors) <= MAXIMUM_TT_ACTION_ERROR
            and max(dense_errors) <= MAXIMUM_TT_ACTION_ERROR
            and storage["serialization_roundtrip_bitwise_equal"]
            and all_finite
        ),
    }
    del mapping_roundtrip, candidate_dense_actions, reconstruction, tt_actions
    return record, cores


def _evaluation_benchmark(
    family: dict[str, Any],
    model: Full2DQuarticModel,
    flat_control_cores: list[npt.NDArray[Any]],
    quartic_cores: dict[str, list[npt.NDArray[Any]]],
) -> dict[str, Any]:
    directions = _normalized_directions(
        TIMING_SEED,
        TIMING_DIRECTION_COUNT,
        REDUCED_DIMENSION,
    )
    vectors = np.asarray(directions @ model.coordinate_map.T, dtype=np.complex128)
    method_cores = {"flat-q-last-control": ("flat-q-last", flat_control_cores)}
    method_cores.update(
        {candidate_id: (candidate_id, cores) for candidate_id, cores in quartic_cores.items()}
    )
    paths = {
        method_id: _einsum_path(
            _tt_candidate_arguments(cores, vectors[0], candidate_id)
        )
        for method_id, (candidate_id, cores) in method_cores.items()
    }
    methods = {
        "sparse-fiber": lambda vector: _sparse_action(
            family["indices"],
            family["multiplicities"],
            family["coefficients"],
            vector,
        ),
        **{
            method_id: (
                lambda vector,
                candidate_id=candidate_id,
                cores=cores,
                path=paths[method_id]: _tt_candidate_action(
                    cores,
                    vector,
                    candidate_id,
                    path=path,
                )
            )
            for method_id, (candidate_id, cores) in method_cores.items()
        },
    }
    method_ids = list(methods)
    checksums = {method_id: [] for method_id in method_ids}
    durations = {method_id: [] for method_id in method_ids}

    def run_block(method_id: str) -> tuple[int, float]:
        was_enabled = gc.isenabled()
        gc.disable()
        started = perf_counter_ns()
        checksum = 0.0
        for vector in vectors:
            checksum += float(np.linalg.norm(methods[method_id](vector)))
        elapsed = perf_counter_ns() - started
        if was_enabled:
            gc.enable()
        return elapsed, checksum

    for warmup in range(TIMING_WARMUP_BLOCKS):
        offset = warmup % len(method_ids)
        for method_id in method_ids[offset:] + method_ids[:offset]:
            run_block(method_id)

    order_by_block = []
    for block in range(TIMING_MEASURED_BLOCKS):
        offset = block % len(method_ids)
        order = method_ids[offset:] + method_ids[:offset]
        order_by_block.append(order)
        for method_id in order:
            elapsed, checksum = run_block(method_id)
            durations[method_id].append(elapsed / TIMING_DIRECTION_COUNT)
            checksums[method_id].append(checksum)

    records = {}
    reference_checksum = median(checksums["sparse-fiber"])
    for method_id in method_ids:
        samples = durations[method_id]
        records[method_id] = {
            "nanoseconds_per_sample_by_block": samples,
            "median_nanoseconds_per_sample": float(median(samples)),
            "median_absolute_deviation_nanoseconds_per_sample": (
                _median_absolute_deviation(samples)
            ),
            "checksum_by_block": checksums[method_id],
            "median_checksum_relative_error_vs_sparse": _relative_norm(
                median(checksums[method_id]) - reference_checksum,
                reference_checksum,
            ),
        }
    return {
        "seed": TIMING_SEED,
        "direction_count": TIMING_DIRECTION_COUNT,
        "direction_sha256": _array_hash(directions),
        "warmup_block_count": TIMING_WARMUP_BLOCKS,
        "measured_block_count": TIMING_MEASURED_BLOCKS,
        "order_by_block": order_by_block,
        "scope": "local homogeneous quartic 9-vector action only",
        "acceptance_role": "diagnostic only",
        "method_records": records,
    }


def run_wave_qtt_prequalification_audit() -> dict[str, Any]:
    """Run the preregistered Q008c wave-factorized TT-SVD audit."""

    model = build_full2d_quartic_model()
    families, observed_hashes = _coefficient_families(model)
    directions = _normalized_directions(
        ACTION_SEED,
        ACTION_DIRECTION_COUNT,
        REDUCED_DIMENSION,
    )
    vectors = np.asarray(directions @ model.coordinate_map.T, dtype=np.complex128)
    duplicate_count = _direction_duplicate_count(directions)
    degree_records = []
    flat_control_records = []
    quartic_cores: dict[str, list[npt.NDArray[Any]]] = {}
    quartic_flat_control_cores: list[npt.NDArray[Any]] | None = None
    maximum_canonical_dense_action_error = 0.0
    for family in families:
        degree = int(family["degree"])
        tensor = _ordered_tensor(
            family["indices"],
            family["coefficients"],
            degree,
        )
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
        canonical_dense_actions = np.asarray(
            [_dense_action(tensor, vector) for vector in vectors],
            dtype=np.complex128,
        )
        canonical_dense_errors = [
            _relative_norm(observed - reference, reference)
            for observed, reference in zip(
                canonical_dense_actions,
                sparse_actions,
                strict=True,
            )
        ]
        maximum_canonical_dense_action_error = max(
            maximum_canonical_dense_action_error,
            max(canonical_dense_errors),
        )
        sparse_storage = _sparse_storage(family)
        control_record, control_cores = _flat_control_audit(
            tensor,
            degree,
            vectors,
            sparse_actions,
        )
        flat_control_records.append(control_record)
        candidate_records = []
        for candidate_id in CANDIDATE_IDS:
            record, cores = _candidate_audit(
                tensor,
                candidate_id,
                vectors,
                sparse_actions,
                canonical_dense_actions,
            )
            record["storage_comparison"] = {
                "core_real_scalars_less_than_natural_sparse": (
                    record["storage"]["core_stored_real_scalar_count"]
                    < sparse_storage["coefficient_stored_real_scalar_count"]
                ),
                "serialized_bytes_less_than_natural_sparse": (
                    record["storage"]["uncompressed_npz_serialized_bytes"]
                    < sparse_storage["uncompressed_npz_serialized_bytes"]
                ),
                "core_real_scalar_ratio_over_natural_sparse": (
                    record["storage"]["core_stored_real_scalar_count"]
                    / sparse_storage["coefficient_stored_real_scalar_count"]
                ),
                "serialized_byte_ratio_over_natural_sparse": (
                    record["storage"]["uncompressed_npz_serialized_bytes"]
                    / sparse_storage["uncompressed_npz_serialized_bytes"]
                ),
            }
            record["storage_hypothesis_passed"] = bool(
                record["fidelity_passed"]
                and record["storage_comparison"][
                    "core_real_scalars_less_than_natural_sparse"
                ]
                and record["storage_comparison"][
                    "serialized_bytes_less_than_natural_sparse"
                ]
            )
            candidate_records.append(record)
            if degree == 4:
                quartic_cores[candidate_id] = cores
        degree_records.append(
            {
                "degree": degree,
                "fiber_count": len(family["indices"]),
                "ordered_tensor_shape": list(tensor.shape),
                "ordered_tensor_complex_entry_count": int(tensor.size),
                "ordered_tensor_stored_real_scalar_count": int(2 * tensor.size),
                "ordered_tensor_payload_bytes": int(tensor.nbytes),
                "maximum_canonical_dense_vs_sparse_relative_action_error": max(
                    canonical_dense_errors
                ),
                "natural_sparse_fiber_storage": sparse_storage,
                "flat_q_last_control": control_record,
                "candidate_records": candidate_records,
            }
        )
        if degree == 4:
            quartic_flat_control_cores = control_cores

    if quartic_flat_control_cores is None:
        raise RuntimeError("quartic flat-q-last control was not constructed")
    quartic_family = next(family for family in families if family["degree"] == 4)
    timing = _evaluation_benchmark(
        quartic_family,
        model,
        quartic_flat_control_cores,
        quartic_cores,
    )
    quartic_record = next(record for record in degree_records if record["degree"] == 4)
    winning_candidates = [
        record
        for record in quartic_record["candidate_records"]
        if record["storage_hypothesis_passed"]
    ]
    winning_candidates.sort(
        key=lambda record: (
            record["storage"]["uncompressed_npz_serialized_bytes"],
            record["storage"]["core_stored_real_scalar_count"],
            record["candidate_id"],
        )
    )
    selected_candidate = (
        None if not winning_candidates else winning_candidates[0]["candidate_id"]
    )
    all_candidate_records = [
        candidate
        for degree_record in degree_records
        for candidate in degree_record["candidate_records"]
    ]
    hash_match = observed_hashes == REGISTERED_INPUT_HASHES
    counts_match = all(
        record["fiber_count"] == REGISTERED_FIBER_COUNTS[record["degree"]]
        for record in degree_records
    )
    sparse_baseline_match = bool(
        quartic_record["natural_sparse_fiber_storage"][
            "coefficient_stored_real_scalar_count"
        ]
        == REGISTERED_QUARTIC_SPARSE_REAL_SCALARS
        and quartic_record["natural_sparse_fiber_storage"][
            "uncompressed_npz_serialized_bytes"
        ]
        == REGISTERED_QUARTIC_SPARSE_SERIALIZED_BYTES
    )
    control_passed = all(
        record["registered_identity_exact"] and record["fidelity_passed"]
        for record in flat_control_records
    )
    mapping_passed = bool(
        maximum_canonical_dense_action_error <= MAXIMUM_DENSE_ACTION_ERROR
        and all(
            record["mapping_roundtrip_bitwise_equal"]
            and record["maximum_relative_dense_mapping_action_error"]
            <= MAXIMUM_DENSE_ACTION_ERROR
            for record in all_candidate_records
        )
    )
    candidate_fidelity_passed = all(
        record["fidelity_passed"] for record in all_candidate_records
    )
    serialization_passed = bool(
        all(
            record["natural_sparse_fiber_storage"][
                "serialization_roundtrip_bitwise_equal"
            ]
            and record["natural_sparse_fiber_storage"][
                "scalar_sparse_lossless_diagnostic"
            ]["serialization_roundtrip_bitwise_equal"]
            and record["flat_q_last_control"]["storage"][
                "serialization_roundtrip_bitwise_equal"
            ]
            for record in degree_records
        )
        and all(
            record["storage"]["serialization_roundtrip_bitwise_equal"]
            for record in all_candidate_records
        )
    )
    serializable_probe = {
        "degree_records": degree_records,
        "evaluation_benchmark": timing,
    }
    finite = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)
    validity_gates = {
        "registered_input_and_independent_campaign": {
            "value": {
                "hashes_match": hash_match,
                "fiber_counts_match": counts_match,
                "quartic_sparse_baseline_match": sparse_baseline_match,
                "action_direction_duplicate_count_vs_q008a": duplicate_count,
                "observed_hashes": observed_hashes,
            },
            "threshold": {
                "hashes_match": True,
                "fiber_counts_match": True,
                "quartic_sparse_baseline_match": True,
                "maximum_action_direction_duplicate_count_vs_q008a": 0,
                "registered_hashes": REGISTERED_INPUT_HASHES,
                "registered_fiber_counts": REGISTERED_FIBER_COUNTS,
            },
            "passed": bool(
                hash_match and counts_match and sparse_baseline_match and duplicate_count == 0
            ),
        },
        "q008a_flat_q_last_control_reproduction": {
            "value": {
                "all_registered_identities_exact": control_passed,
                "records": flat_control_records,
            },
            "threshold": {
                "all_registered_identities_exact": True,
                "maximum_tensor_reconstruction_error": (
                    MAXIMUM_TENSOR_RECONSTRUCTION_ERROR
                ),
                "maximum_action_error_vs_sparse": MAXIMUM_TT_ACTION_ERROR,
            },
            "passed": control_passed,
        },
        "tensorization_mapping": {
            "value": {
                "maximum_canonical_dense_vs_sparse_action_error": (
                    maximum_canonical_dense_action_error
                ),
                "maximum_candidate_dense_mapping_action_error": max(
                    record["maximum_relative_dense_mapping_action_error"]
                    for record in all_candidate_records
                ),
                "all_mapping_roundtrips_bitwise_equal": all(
                    record["mapping_roundtrip_bitwise_equal"]
                    for record in all_candidate_records
                ),
            },
            "threshold": {
                "maximum_relative_action_error": MAXIMUM_DENSE_ACTION_ERROR,
                "all_mapping_roundtrips_bitwise_equal": True,
            },
            "passed": mapping_passed,
        },
        "tt_reconstruction_and_action": {
            "value": {
                "maximum_tensor_reconstruction_error": max(
                    record["relative_tensor_reconstruction_error"]
                    for record in all_candidate_records
                ),
                "maximum_action_error_vs_sparse": max(
                    record["maximum_relative_action_error_vs_sparse"]
                    for record in all_candidate_records
                ),
                "all_candidates_passed": candidate_fidelity_passed,
            },
            "threshold": {
                "maximum_tensor_reconstruction_error": (
                    MAXIMUM_TENSOR_RECONSTRUCTION_ERROR
                ),
                "maximum_action_error_vs_sparse": MAXIMUM_TT_ACTION_ERROR,
                "all_candidates_passed": True,
            },
            "passed": candidate_fidelity_passed,
        },
        "serialization_finiteness_and_strict_json": {
            "value": {
                "all_roundtrips_bitwise_equal": serialization_passed,
                "all_values_finite": finite,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "all_roundtrips_bitwise_equal": True,
                "all_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": serialization_passed and finite and strict_json,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    storage_passed = bool(winning_candidates)
    hypothesis_gates = {
        "quartic_wave_factorized_tt_beats_natural_sparse_storage": {
            "value": {
                "passing_candidate_count": len(winning_candidates),
                "passing_candidate_ids": [
                    record["candidate_id"] for record in winning_candidates
                ],
                "selected_candidate": selected_candidate,
            },
            "threshold": {
                "minimum_passing_candidate_count": 1,
                "core_stored_real_scalars_strictly_less_than": (
                    REGISTERED_QUARTIC_SPARSE_REAL_SCALARS
                ),
                "serialized_bytes_strictly_less_than": (
                    REGISTERED_QUARTIC_SPARSE_SERIALIZED_BYTES
                ),
            },
            "passed": storage_passed,
        }
    }
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q008c wave-factorized TT prequalification validity failure"
        decision = (
            "An input, control, tensor mapping, TT fidelity, serialization, finiteness, "
            "or strict-JSON validity gate failed."
        )
        next_change = (
            "Repair the first validity failure without changing the four registered "
            "tensorizations or either storage threshold."
        )
    elif storage_passed:
        outcome = "accepted"
        classification = (
            "registered wave-factorized TT beats natural quartic sparse-fiber storage"
        )
        decision = (
            "At least one registered degree-4 wave-factorized TT is faithful and "
            "strictly smaller than the natural sparse fiber in both storage metrics."
        )
        next_change = (
            "Freeze the lexicographically selected candidate and preregister an "
            "independent full-chart residual and rollout-preservation gate."
        )
    else:
        outcome = "rejected"
        classification = (
            "registered wave-factorized TTs do not beat natural quartic sparse-fiber storage"
        )
        decision = (
            "All registered wave-factorized tensors are valid, but none beats the "
            "natural quartic sparse fiber in both registered storage metrics."
        )
        next_change = (
            "Close the TT-SVD compression path for the fixed Q007c1 coefficients and "
            "do not start Q009 TT-cross. Return to the unresolved invariant-manifold "
            "mathematical gates before considering a newly preregistered representation."
        )
    return {
        "question": (
            "Does explicit 24=8-wave-by-3-branch structure or a three-bit wave QTT "
            "preserve the local degree-2 to degree-4 Fourier coefficients and beat "
            "the natural quartic sparse-fiber storage baseline?"
        ),
        "hypothesis": (
            "At least one faithful registered degree-4 wave-factorized TT uses fewer "
            "than 315900 core-stored real scalars and fewer than 2615734 uncompressed "
            "NPZ bytes."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.cubic.quadratic.omega,
            "eta": model.cubic.quadratic.eta,
            "complex_mode_count": len(model.modes),
            "wave_count": len(WAVE_ORDER),
            "branch_count": len(MODE_ORDER),
            "mode_index_mapping": "i = 3*w + b",
            "wave_bit_mapping": "w = 4*s2 + 2*s1 + s0",
            "wave_order": [list(wave) for wave in WAVE_ORDER],
            "branch_order": list(MODE_ORDER),
            "local_output_count": 9,
            "degrees": [2, 3, 4],
            "tensorization_ids": list(CANDIDATE_IDS),
            "tt_relative_discarded_frobenius_budget": TT_RELATIVE_TOLERANCE,
            "maximum_rank": None,
            "physical_full_dense_tensor_materialized": False,
        },
        "input_registration": {
            "registered_hashes": REGISTERED_INPUT_HASHES,
            "observed_hashes": observed_hashes,
            "match": hash_match,
            "action_seed": ACTION_SEED,
            "action_direction_count": ACTION_DIRECTION_COUNT,
            "action_direction_sha256": _array_hash(directions),
            "action_direction_duplicate_count_vs_q008a": duplicate_count,
        },
        "degree_records": degree_records,
        "evaluation_benchmark": timing,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "selected_candidate": selected_candidate,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "The result concerns four preregistered wave/branch tensorizations of the "
            "fixed local degree-two through degree-four coefficients. It is not an "
            "asymptotic-rank, full-chart invariance, rollout, online-speed, TT-cross, "
            "other-shell, other-grid, existence, uniqueness, or normal-attraction "
            "claim. Timing is diagnostic only."
        ),
    }
