"""Sealed Q008a Fourier-coefficient TT storage prequalification audit."""

from __future__ import annotations

import gc
from io import BytesIO
from itertools import combinations_with_replacement, permutations
from math import factorial
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
from .d2q9 import D2Q9_VELOCITIES
from .full2d_chart import MODE_ORDER, REDUCED_DIMENSION, _complex_coefficients
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model
from .tensor_train import contract_tt, reconstruct, tt_ranks, tt_svd_with_diagnostics

ComplexArray = npt.NDArray[np.complex128]
IntegerArray = npt.NDArray[np.int64]

REGISTERED_INPUT_HASHES = {
    "mode_table_sha256": (
        "6e08a2706a44965143944b692615c6a8525799d3e01ca06a636d852d6610d4d9"
    ),
    "quadratic_chart_coefficients_sha256": (
        "4d0ddc917c3b722496b918f38f8e810e0f200c5fd2ffa138025a93aa2571f8db"
    ),
    "cubic_indices_sha256": (
        "e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c"
    ),
    "cubic_chart_coefficients_sha256": (
        "ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b"
    ),
    "quartic_indices_sha256": (
        "968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16"
    ),
    "quartic_chart_coefficients_sha256": (
        "9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b"
    ),
}

REGISTERED_FIBER_COUNTS = {2: 300, 3: 2600, 4: 17550}
TENSORIZATION_IDS = (
    "flat-q-first",
    "flat-q-last",
    "d1q3-q-first",
    "d1q3-q-last",
)
TT_RELATIVE_TOLERANCE = 1.0e-13
ACTION_SEED = 20260827
ACTION_DIRECTION_COUNT = 64
TIMING_SEED = 20260828
TIMING_DIRECTION_COUNT = 128
TIMING_WARMUP_BLOCKS = 2
TIMING_MEASURED_BLOCKS = 7
MAXIMUM_DENSE_ACTION_ERROR = 5.0e-14
MAXIMUM_TENSOR_RECONSTRUCTION_ERROR = 2.0e-13
MAXIMUM_TT_ACTION_ERROR = 1.0e-11


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).eps)
    )


def _permutation_multiplicity(indices: npt.ArrayLike) -> int:
    _, counts = np.unique(np.asarray(indices, dtype=np.int64), return_counts=True)
    result = factorial(int(np.sum(counts)))
    for count in counts:
        result //= factorial(int(count))
    return result


def _mode_table(model: Full2DQuarticModel) -> IntegerArray:
    label_index = {label: index for index, label in enumerate(MODE_ORDER)}
    return np.asarray(
        [
            [
                int(mode.wave_index[0]),
                int(mode.wave_index[1]),
                label_index[mode.label],
            ]
            for mode in model.modes
        ],
        dtype=np.int64,
    )


def _coefficient_families(
    model: Full2DQuarticModel,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    quadratic, _, _, _ = _complex_coefficients(
        list(model.modes),
        model.lookup,
        model.size,
        model.cubic.quadratic.omega,
        model.cubic.quadratic.eta,
    )
    pair_indices = np.asarray(
        list(combinations_with_replacement(range(REDUCED_DIMENSION), 2)),
        dtype=np.int64,
    )
    pair_coefficients = quadratic[
        pair_indices[:, 0],
        pair_indices[:, 1],
    ]
    pair_multiplicities = np.asarray(
        [_permutation_multiplicity(indices) for indices in pair_indices],
        dtype=np.int64,
    )
    families = [
        {
            "degree": 2,
            "indices": pair_indices,
            "multiplicities": pair_multiplicities,
            "coefficients": np.asarray(pair_coefficients, dtype=np.complex128),
        },
        {
            "degree": 3,
            "indices": np.asarray(model.cubic.triple_indices, dtype=np.int64),
            "multiplicities": np.asarray(model.cubic.multiplicities, dtype=np.int64),
            "coefficients": np.asarray(
                model.cubic.cubic_coefficients,
                dtype=np.complex128,
            ),
        },
        {
            "degree": 4,
            "indices": np.asarray(model.quartet_indices, dtype=np.int64),
            "multiplicities": np.asarray(model.multiplicities, dtype=np.int64),
            "coefficients": np.asarray(
                model.quartic_coefficients,
                dtype=np.complex128,
            ),
        },
    ]
    observed_hashes = {
        "mode_table_sha256": _array_hash(_mode_table(model)),
        "quadratic_chart_coefficients_sha256": _array_hash(quadratic),
        "cubic_indices_sha256": _array_hash(model.cubic.triple_indices),
        "cubic_chart_coefficients_sha256": _array_hash(
            model.cubic.cubic_coefficients
        ),
        "quartic_indices_sha256": _array_hash(model.quartet_indices),
        "quartic_chart_coefficients_sha256": _array_hash(
            model.quartic_coefficients
        ),
    }
    return families, observed_hashes


def _ordered_tensor(
    indices: npt.ArrayLike,
    coefficients: npt.ArrayLike,
    degree: int,
) -> ComplexArray:
    multi_indices = np.asarray(indices, dtype=np.int64)
    fibers = np.asarray(coefficients, dtype=np.complex128)
    if multi_indices.shape != (len(fibers), degree) or fibers.shape[1:] != (9,):
        raise ValueError("coefficient family shapes do not match its degree")
    tensor = np.zeros(
        (9,) + (REDUCED_DIMENSION,) * degree,
        dtype=np.complex128,
    )
    for multi_index, coefficient in zip(multi_indices, fibers, strict=True):
        for ordered in set(permutations(int(value) for value in multi_index)):
            tensor[(slice(None), *ordered)] = coefficient
    return tensor


def _sparse_action(
    indices: npt.ArrayLike,
    multiplicities: npt.ArrayLike,
    coefficients: npt.ArrayLike,
    vector: npt.ArrayLike,
) -> ComplexArray:
    multi_indices = np.asarray(indices, dtype=np.int64)
    weights = np.asarray(multiplicities, dtype=np.float64)
    fibers = np.asarray(coefficients, dtype=np.complex128)
    value = np.asarray(vector, dtype=np.complex128)
    products = np.prod(value[multi_indices], axis=1)
    return np.asarray(
        np.einsum("t,tq->q", weights * products, fibers),
        dtype=np.complex128,
    )


def _dense_action(tensor: npt.ArrayLike, vector: npt.ArrayLike) -> ComplexArray:
    result = np.asarray(tensor, dtype=np.complex128)
    value = np.asarray(vector, dtype=np.complex128)
    while result.ndim > 1:
        result = np.tensordot(result, value, axes=([1], [0]))
    return np.asarray(result, dtype=np.complex128)


def _velocity_permutation() -> IntegerArray:
    velocities = np.asarray(D2Q9_VELOCITIES, dtype=np.int64)
    return np.asarray(
        np.lexsort((velocities[:, 0], velocities[:, 1])),
        dtype=np.int64,
    )


def _tensorize(tensor: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    dense = np.asarray(tensor, dtype=np.complex128)
    degree = dense.ndim - 1
    if dense.shape != (9,) + (REDUCED_DIMENSION,) * degree:
        raise ValueError("ordered tensor must have a local D2Q9 output axis")
    if candidate_id == "flat-q-first":
        return dense
    if candidate_id == "flat-q-last":
        return np.asarray(np.moveaxis(dense, 0, -1), dtype=np.complex128)
    reordered = dense[_velocity_permutation()]
    if candidate_id == "d1q3-q-first":
        return np.asarray(
            reordered.reshape((3, 3) + (REDUCED_DIMENSION,) * degree),
            dtype=np.complex128,
        )
    if candidate_id == "d1q3-q-last":
        return np.asarray(
            np.moveaxis(reordered, 0, -1).reshape(
                (REDUCED_DIMENSION,) * degree + (3, 3)
            ),
            dtype=np.complex128,
        )
    raise ValueError(f"unknown registered tensorization: {candidate_id}")


def _tt_action(
    cores: list[npt.NDArray[Any]],
    vector: npt.ArrayLike,
    candidate_id: str,
) -> ComplexArray:
    value = np.asarray(vector, dtype=np.complex128)
    if candidate_id == "flat-q-first":
        contracted = contract_tt(cores, [None] + [value] * (len(cores) - 1))
        return np.asarray(contracted, dtype=np.complex128)
    if candidate_id == "flat-q-last":
        contracted = contract_tt(cores, [value] * (len(cores) - 1) + [None])
        return np.asarray(contracted, dtype=np.complex128)
    if candidate_id == "d1q3-q-first":
        contracted = contract_tt(
            cores,
            [None, None] + [value] * (len(cores) - 2),
        )
    elif candidate_id == "d1q3-q-last":
        contracted = contract_tt(
            cores,
            [value] * (len(cores) - 2) + [None, None],
        )
    else:
        raise ValueError(f"unknown registered tensorization: {candidate_id}")
    lexicographic = np.asarray(contracted, dtype=np.complex128).reshape(9)
    result = np.empty(9, dtype=np.complex128)
    result[_velocity_permutation()] = lexicographic
    return result


def _serialized_arrays(arrays: dict[str, npt.ArrayLike]) -> tuple[int, bool]:
    stream = BytesIO()
    converted = {name: np.asarray(value) for name, value in arrays.items()}
    np.savez(stream, **converted)
    payload = stream.getvalue()
    with np.load(BytesIO(payload), allow_pickle=False) as loaded:
        roundtrip = all(
            loaded[name].dtype == value.dtype
            and loaded[name].shape == value.shape
            and np.array_equal(loaded[name], value)
            for name, value in converted.items()
        )
    return len(payload), roundtrip


def _sparse_storage(family: dict[str, Any]) -> dict[str, Any]:
    indices = np.asarray(family["indices"], dtype=np.uint8)
    multiplicities = np.asarray(family["multiplicities"], dtype=np.uint8)
    coefficients = np.asarray(family["coefficients"], dtype=np.complex128)
    arrays = {
        "indices": indices,
        "multiplicities": multiplicities,
        "coefficients": coefficients,
    }
    serialized_bytes, roundtrip = _serialized_arrays(arrays)
    rows, components = np.nonzero(coefficients != 0.0)
    scalar_arrays = {
        "indices": indices[rows],
        "multiplicities": multiplicities[rows],
        "components": np.asarray(components, dtype=np.uint8),
        "coefficients": coefficients[rows, components],
    }
    scalar_serialized_bytes, scalar_roundtrip = _serialized_arrays(scalar_arrays)
    return {
        "fiber_count": len(indices),
        "coefficient_stored_real_scalar_count": int(2 * coefficients.size),
        "coefficient_payload_bytes": int(coefficients.nbytes),
        "index_and_multiplicity_metadata_bytes": int(
            indices.nbytes + multiplicities.nbytes
        ),
        "raw_array_payload_bytes": int(
            indices.nbytes + multiplicities.nbytes + coefficients.nbytes
        ),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "serialization_roundtrip_bitwise_equal": roundtrip,
        "scalar_sparse_lossless_diagnostic": {
            "bitwise_nonzero_coefficient_count": len(rows),
            "coefficient_stored_real_scalar_count": int(2 * len(rows)),
            "index_and_multiplicity_metadata_bytes": int(
                scalar_arrays["indices"].nbytes
                + scalar_arrays["multiplicities"].nbytes
                + scalar_arrays["components"].nbytes
            ),
            "raw_array_payload_bytes": int(
                sum(value.nbytes for value in scalar_arrays.values())
            ),
            "uncompressed_npz_serialized_bytes": scalar_serialized_bytes,
            "serialization_roundtrip_bitwise_equal": scalar_roundtrip,
        },
    }


def _tt_storage(cores: list[npt.NDArray[Any]]) -> dict[str, Any]:
    ranks = np.asarray(tt_ranks(cores), dtype=np.int64)
    mode_shape = np.asarray([core.shape[1] for core in cores], dtype=np.int64)
    arrays = {
        **{f"core_{index:03d}": core for index, core in enumerate(cores)},
        "ranks": ranks,
        "mode_shape": mode_shape,
    }
    serialized_bytes, roundtrip = _serialized_arrays(arrays)
    complex_core_entries = int(sum(core.size for core in cores))
    gauge_complex_dimension = complex_core_entries - int(
        sum(rank * rank for rank in ranks[1:-1])
    )
    return {
        "core_count": len(cores),
        "tt_ranks": ranks.tolist(),
        "mode_shape": mode_shape.tolist(),
        "complex_core_entry_count": complex_core_entries,
        "core_stored_real_scalar_count": 2 * complex_core_entries,
        "core_payload_bytes": int(sum(core.nbytes for core in cores)),
        "rank_and_shape_metadata_bytes": int(ranks.nbytes + mode_shape.nbytes),
        "raw_array_payload_bytes": int(
            sum(core.nbytes for core in cores) + ranks.nbytes + mode_shape.nbytes
        ),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "nominal_gauge_adjusted_real_dimension": 2 * gauge_complex_dimension,
        "serialization_roundtrip_bitwise_equal": roundtrip,
    }


def _split_d1q3_output_core(
    cores: list[npt.NDArray[Any]],
    *,
    output_first: bool,
) -> tuple[list[npt.NDArray[Any]], dict[str, Any]]:
    if output_first:
        output_core = np.asarray(cores[0], dtype=np.complex128)
        if output_core.shape[:2] != (1, 9):
            raise ValueError("flat-q-first output core has the wrong shape")
        right_rank = output_core.shape[2]
        matrix = output_core.reshape(3, 3 * right_rank)
        u, singular_values, vh = np.linalg.svd(matrix, full_matrices=False)
        split_rank = singular_values.size
        first = u.reshape(1, 3, split_rank)
        second = (singular_values[:, None] * vh).reshape(
            split_rank,
            3,
            right_rank,
        )
        result = [first, second, *cores[1:]]
    else:
        output_core = np.asarray(cores[-1], dtype=np.complex128)
        if output_core.shape[1:] != (9, 1):
            raise ValueError("flat-q-last output core has the wrong shape")
        left_rank = output_core.shape[0]
        matrix = output_core.reshape(left_rank * 3, 3)
        u, singular_values, vh = np.linalg.svd(matrix, full_matrices=False)
        split_rank = singular_values.size
        first = u.reshape(left_rank, 3, split_rank)
        second = (singular_values[:, None] * vh).reshape(split_rank, 3, 1)
        result = [*cores[:-1], first, second]
    all_finite = bool(
        np.all(np.isfinite(singular_values))
        and all(np.all(np.isfinite(core)) for core in result)
    )
    return result, {
        "method": "full-rank SVD of the validated flat velocity output core",
        "matrix_shape": list(matrix.shape),
        "retained_rank": split_rank,
        "discarded_frobenius_norm": 0.0,
        "maximum_singular_value": float(singular_values[0]),
        "minimum_singular_value": float(singular_values[-1]),
        "all_singular_values_finite": all_finite,
    }


def _candidate_decomposition(
    tensor: ComplexArray,
    candidate_id: str,
) -> tuple[ComplexArray, list[npt.NDArray[Any]], dict[str, Any]]:
    candidate_tensor = _tensorize(tensor, candidate_id)
    if candidate_id in {"flat-q-first", "flat-q-last"}:
        cores, diagnostics = tt_svd_with_diagnostics(
            candidate_tensor,
            relative_tolerance=TT_RELATIVE_TOLERANCE,
            max_rank=None,
        )
        diagnostics["construction_method"] = "direct registered TT-SVD"
        return candidate_tensor, cores, diagnostics

    flat_id = (
        "flat-q-first" if candidate_id == "d1q3-q-first" else "flat-q-last"
    )
    lexicographic_tensor = np.asarray(
        tensor[_velocity_permutation()],
        dtype=np.complex128,
    )
    flat_tensor = (
        lexicographic_tensor
        if candidate_id == "d1q3-q-first"
        else np.asarray(
            np.moveaxis(lexicographic_tensor, 0, -1),
            dtype=np.complex128,
        )
    )
    flat_cores, flat_diagnostics = tt_svd_with_diagnostics(
        flat_tensor,
        relative_tolerance=TT_RELATIVE_TOLERANCE,
        max_rank=None,
    )
    cores, split_diagnostics = _split_d1q3_output_core(
        flat_cores,
        output_first=candidate_id == "d1q3-q-first",
    )
    diagnostics = {
        "construction_method": (
            "registered flat TT-SVD followed by a full-rank D1Q3 output-core split"
        ),
        "input_dtype": str(candidate_tensor.dtype),
        "mode_shape": list(candidate_tensor.shape),
        "tensor_frobenius_norm": flat_diagnostics["tensor_frobenius_norm"],
        "requested_relative_tolerance": TT_RELATIVE_TOLERANCE,
        "maximum_rank": None,
        "flat_tensorization_id": f"lexicographic-{flat_id}",
        "flat_tt_svd": flat_diagnostics,
        "output_core_split": split_diagnostics,
        "discarded_frobenius_norm": flat_diagnostics[
            "discarded_frobenius_norm"
        ],
        "relative_discarded_frobenius_norm": flat_diagnostics[
            "relative_discarded_frobenius_norm"
        ],
        "tt_ranks": tt_ranks(cores),
        "all_singular_values_finite": bool(
            flat_diagnostics["all_singular_values_finite"]
            and split_diagnostics["all_singular_values_finite"]
        ),
    }
    return candidate_tensor, cores, diagnostics


def _candidate_audit(
    tensor: ComplexArray,
    candidate_id: str,
    vectors: ComplexArray,
    sparse_actions: ComplexArray,
    dense_actions: ComplexArray,
) -> tuple[dict[str, Any], list[npt.NDArray[Any]]]:
    started = perf_counter_ns()
    candidate_tensor, cores, diagnostics = _candidate_decomposition(
        tensor,
        candidate_id,
    )
    elapsed = perf_counter_ns() - started
    reconstruction = reconstruct(cores)
    tensor_error = _relative_norm(
        reconstruction - candidate_tensor,
        candidate_tensor,
    )
    tt_actions = np.asarray(
        [_tt_action(cores, vector, candidate_id) for vector in vectors],
        dtype=np.complex128,
    )
    sparse_errors = [
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(tt_actions, sparse_actions, strict=True)
    ]
    dense_errors = [
        _relative_norm(observed - reference, reference)
        for observed, reference in zip(tt_actions, dense_actions, strict=True)
    ]
    storage = _tt_storage(cores)
    all_finite = bool(
        all(np.all(np.isfinite(core)) for core in cores)
        and np.all(np.isfinite(reconstruction))
        and np.all(np.isfinite(tt_actions))
        and diagnostics["all_singular_values_finite"]
        and _all_numeric_values_finite(diagnostics)
    )
    record = {
        "candidate_id": candidate_id,
        "tensor_shape": list(candidate_tensor.shape),
        "relative_tensor_reconstruction_error": tensor_error,
        "maximum_relative_action_error_vs_sparse": max(sparse_errors),
        "maximum_relative_action_error_vs_dense": max(dense_errors),
        "all_values_finite": all_finite,
        "tt_svd_wall_time_ns": elapsed,
        "tt_svd_diagnostics": diagnostics,
        "storage": storage,
        "fidelity_passed": bool(
            tensor_error <= MAXIMUM_TENSOR_RECONSTRUCTION_ERROR
            and max(sparse_errors) <= MAXIMUM_TT_ACTION_ERROR
            and max(dense_errors) <= MAXIMUM_TT_ACTION_ERROR
            and storage["serialization_roundtrip_bitwise_equal"]
            and all_finite
        ),
    }
    del reconstruction
    return record, cores


def _median_absolute_deviation(values: list[float]) -> float:
    center = median(values)
    return float(median(abs(value - center) for value in values))


def _evaluation_benchmark(
    family: dict[str, Any],
    model: Full2DQuarticModel,
    quartic_cores: dict[str, list[npt.NDArray[Any]]],
) -> dict[str, Any]:
    directions = _normalized_directions(
        TIMING_SEED,
        TIMING_DIRECTION_COUNT,
        REDUCED_DIMENSION,
    )
    vectors = np.asarray(
        directions @ model.coordinate_map.T,
        dtype=np.complex128,
    )
    methods = {
        "sparse-fiber": lambda vector: _sparse_action(
            family["indices"],
            family["multiplicities"],
            family["coefficients"],
            vector,
        ),
        **{
            candidate_id: (
                lambda vector, name=candidate_id, cores=cores: _tt_action(
                    cores,
                    vector,
                    name,
                )
            )
            for candidate_id, cores in quartic_cores.items()
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


def run_tt_storage_prequalification_audit() -> dict[str, Any]:
    """Run the preregistered Q008a sparse-fiber versus TT-SVD audit."""

    model = build_full2d_quartic_model()
    families, observed_hashes = _coefficient_families(model)
    directions = _normalized_directions(
        ACTION_SEED,
        ACTION_DIRECTION_COUNT,
        REDUCED_DIMENSION,
    )
    vectors = np.asarray(directions @ model.coordinate_map.T, dtype=np.complex128)
    degree_records = []
    quartic_cores: dict[str, list[npt.NDArray[Any]]] = {}
    maximum_dense_action_error = 0.0
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
        dense_actions = np.asarray(
            [_dense_action(tensor, vector) for vector in vectors],
            dtype=np.complex128,
        )
        dense_action_errors = [
            _relative_norm(observed - reference, reference)
            for observed, reference in zip(dense_actions, sparse_actions, strict=True)
        ]
        maximum_dense_action_error = max(
            maximum_dense_action_error,
            max(dense_action_errors),
        )
        sparse_storage = _sparse_storage(family)
        candidate_records = []
        for candidate_id in TENSORIZATION_IDS:
            record, cores = _candidate_audit(
                tensor,
                candidate_id,
                vectors,
                sparse_actions,
                dense_actions,
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
                "maximum_dense_vs_sparse_relative_action_error": max(
                    dense_action_errors
                ),
                "natural_sparse_fiber_storage": sparse_storage,
                "candidate_records": candidate_records,
            }
        )

    quartic_family = next(family for family in families if family["degree"] == 4)
    timing = _evaluation_benchmark(quartic_family, model, quartic_cores)
    quartic_record = next(
        record for record in degree_records if record["degree"] == 4
    )
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
    dense_expansion_passed = maximum_dense_action_error <= MAXIMUM_DENSE_ACTION_ERROR
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
        "registered_input_identity": {
            "value": {
                "hashes_match": hash_match,
                "fiber_counts_match": counts_match,
                "observed_hashes": observed_hashes,
            },
            "threshold": {
                "hashes_match": True,
                "fiber_counts_match": True,
                "registered_hashes": REGISTERED_INPUT_HASHES,
                "registered_fiber_counts": REGISTERED_FIBER_COUNTS,
            },
            "passed": hash_match and counts_match,
        },
        "ordered_dense_expansion": {
            "value": maximum_dense_action_error,
            "threshold": MAXIMUM_DENSE_ACTION_ERROR,
            "passed": dense_expansion_passed,
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
        "quartic_tt_beats_natural_sparse_storage": {
            "value": {
                "passing_candidate_count": len(winning_candidates),
                "passing_candidate_ids": [
                    record["candidate_id"] for record in winning_candidates
                ],
                "selected_candidate": selected_candidate,
            },
            "threshold": {
                "minimum_passing_candidate_count": 1,
                "core_stored_real_scalars_strictly_less_than": 315900,
                "serialized_bytes_strictly_less_than_natural_sparse": True,
            },
            "passed": storage_passed,
        }
    }
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q008a TT storage prequalification validity failure"
        decision = (
            "An input, dense expansion, TT fidelity, serialization, finiteness, "
            "or strict-JSON validity gate failed."
        )
        next_change = (
            "Repair the first validity failure without changing the four registered "
            "tensorizations or the storage thresholds."
        )
    elif storage_passed:
        outcome = "accepted"
        classification = (
            "registered TT tensorization beats natural quartic sparse-fiber storage"
        )
        decision = (
            "At least one registered degree-4 TT passes fidelity and is strictly "
            "smaller than the natural sparse fiber in both registered storage metrics."
        )
        next_change = (
            "Freeze the lexicographically selected candidate and preregister Q008b "
            "full-chart residual and rollout preservation on independent directions."
        )
    else:
        outcome = "rejected"
        classification = (
            "registered TT tensorizations do not beat natural quartic sparse-fiber storage"
        )
        decision = (
            "All registered tensors are valid, but none beats the natural quartic "
            "sparse fiber in both core real scalars and uncompressed serialized bytes."
        )
        next_change = (
            "Stop Q008b and Q009 for these four tensorizations. Any wave/branch QTT "
            "factorization requires a new sealed candidate set before computation."
        )
    return {
        "question": (
            "Does any of four fixed TT output-axis layouts preserve the degree-2 to "
            "degree-4 local Fourier chart coefficients and beat the natural degree-4 "
            "sparse-fiber storage baseline?"
        ),
        "hypothesis": (
            "At least one faithful degree-4 TT uses fewer than 315900 core-stored real "
            "scalars and fewer uncompressed NPZ bytes than the natural sparse fiber."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.cubic.quadratic.omega,
            "eta": model.cubic.quadratic.eta,
            "complex_mode_count": len(model.modes),
            "local_output_count": 9,
            "degrees": [2, 3, 4],
            "tensorization_ids": list(TENSORIZATION_IDS),
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
            "The result concerns four registered local coefficient tensorizations at "
            "degrees two through four. It is not an asymptotic rank bound, online-speed, "
            "full-chart invariance, rollout, TT-cross, other-shell, other-grid, or "
            "physical full-dense-tensor claim. Timing is diagnostic only."
        ),
    }
