"""Q011g forced-quadratic Fourier-sparse versus TT-SVD audit."""

from __future__ import annotations

import argparse
import gc
import json
import math
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Any

import numpy as np
import numpy.typing as npt

import research.q011e_forced_quadratic_chart as q011e
import research.q011f1_heldout_amplitude_reissue as q011f1
from ttim_lbm.d2q9 import D2Q9_VELOCITIES, global_conserved_quantities
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)
from ttim_lbm.tensor_train import (
    contract_tt,
    reconstruct,
    tt_ranks,
    tt_svd_with_diagnostics,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
IntegerArray = npt.NDArray[np.int64]

SIZE = q011e.SIZE
STATE_DIMENSION = q011e.STATE_DIMENSION
SELECTED_DIMENSION = q011e.SELECTED_DIMENSION
PAIR_COUNT = q011e.PAIR_COUNT
OUTPUT_SECTOR_ORDER = q011e.OUTPUT_SECTOR_ORDER
SELECTED_BLOCK_ORDER = q011e.SELECTED_BLOCK_ORDER
STRIPE_DIMENSION = q011e.STRIPE_DIMENSION
SELECTED_OFFSETS = {0: slice(0, 6), 1: slice(6, 15), 16: slice(15, 24)}
EXPECTED_SECTOR_PAIR_COUNTS = {0: 102, 1: 54, 16: 54, 2: 45, 15: 45}

Q011F1_ARTIFACT_SHA256 = "79ddb64e0965b5b87b7ad68c6dc8698efdd2281540c798ed27f355747d265bc1"
Q011F1_RUNNER_SHA256 = "eab2d63a075f2c43b4c6adfaa7941e9c23bf85a351427057130f68945346ce62"
Q011F1_INPUT_DIGEST = "101adcdc6fc2d40dc984e6ba900d234b913f7c78aa34381a08d0a77aa9e23000"
Q011F1_CHART_DIGEST = "ba50ee295551dae970d33e1bba735ac0502987aef0f4a82987f2998ae884f732"
Q011F1_HELDOUT_DIGEST = "243c41522a9eb7d7b78b2031bdbe8f55eb23b447e8d84162b1aae2f53b651829"
Q011F1_MERGED_DIGEST = "2e3fcee7bebec5c82f2fbd2b78ddac8c44401fd0681ad5d9feb60c7257a8326e"
Q011F1_RESULT_DIGEST = "484580786b6c535856f0693b14c58815462e1de979759057dc3b402d475bcbc7"
SEALED_PACKAGE_SOURCE_SHA256 = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"

Q011E_ARTIFACT_SHA256 = "45d563103678d790aa3df4db692bbe781c9c86ed550c7499c61b397688666fca"
Q011E_RUNNER_SHA256 = "3aa608852be7a1df7dbe37b4d3c7e1bb3fbf125eae115260fc45a223e0757955"
Q011E_INPUT_DIGEST = "f0bd65361d0cdc39e6499b8b0065ce6d7705945927ed77af5d2b231d0572bc9c"
Q011E_DERIVATIVE_DIGEST = "d017d3ea204ad337f538b6f1819e215b6ab8a69f89090cc51ca9eb4885b75fce"
Q011E_CHART_DIGEST = "6d4ee0102a6df052fac857890468ed911cff994e07c573dde837eb54a4a22e05"
NATIVE_CHART_HESSIAN_SHA256 = "0b4c2f6967624e62b8b45a1fde67d0a092894ff367ed402a076c15c46a2206db"
NATIVE_REDUCED_HESSIAN_SHA256 = "b450cba9d58d0853bed95acaa9b4f2a69659e5c24b943708c0700d11c8962ee9"
COORDINATE_MAP_SHA256 = "ba7e73e99f82b5c14fb0d96005d7952248c4f6da9a48e1430b7c389ba42674f1"
REAL_ARRAY_HASHES = {
    "real_tangent_sha256": ("e0b6fb929d49a1371d1eebf836308a795a7f0e9dbad44f55b2386add9f3d0628"),
    "real_extractor_sha256": ("e77d149787d187ca756a23efcf6b833cfd6ab15b5fd617b5d3ae3ba5c0859f6f"),
    "real_reduced_linear_sha256": (
        "b6521e3090b61c72d0689b765e1fad0a0318029a0ab5767bd3c7679d4ce2c525"
    ),
    "analytic_second_derivative_sha256": (
        "6bfea17a7bbfa1dcdded5dadec15296ec2f478aefe7984dd1e4885498a186221"
    ),
    "real_chart_hessian_sha256": (
        "ab55a8b50f2565be494fcf3d5f140f93fc0112484da56e1333ce58dfd220a6c2"
    ),
    "real_reduced_hessian_sha256": (
        "7ae45cbabda8da17ec73d6779761077a67e19fae4dc53ca11fe98b78bcf074e2"
    ),
}

TT_RELATIVE_TOLERANCE = 1.0e-13
MAXIMUM_PROJECTION_RELATIVE_LOSS = 1.0e-12
MAXIMUM_SPARSE_DENSE_ACTION_ERROR = 1.0e-12
MAXIMUM_TT_RECONSTRUCTION_ERROR = 2.0e-13
MAXIMUM_TT_ACTION_ERROR = 1.0e-11
MAXIMUM_REALIFICATION_ACTION_ERROR = 1.0e-11
MAXIMUM_INVARIANCE_DEFECT_PERTURBATION = 1.0e-4
MAXIMUM_CONSERVATION_DRIFT = 1.0e-10
MAXIMUM_CHECKSUM_RELATIVE_ERROR = 1.0e-11

ACTION_SEED = 20260902
ACTION_DIRECTION_COUNT = 32
INVARIANCE_SEED = 20260903
INVARIANCE_DIRECTION_COUNT = 16
INVARIANCE_AMPLITUDE = 2.56e-3
PRIOR_DIRECTION_CAMPAIGNS = (
    (q011e.RESIDUAL_SEED, q011e.RESIDUAL_DIRECTION_COUNT),
    (q011f1.q011e1.DIRECTION_SEED, q011f1.q011e1.DIRECTION_COUNT),
    (q011f1.q011f.DIRECTION_SEED, q011f1.q011f.DIRECTION_COUNT),
)

OFFLINE_WARMUP_BLOCKS = 1
OFFLINE_MEASURED_BLOCKS = 3
ONLINE_WARMUP_BLOCKS = 1
ONLINE_MEASURED_BLOCKS = 5

SPARSE_METHOD_ID = "natural-fourier-sparse"
DENSE_METHOD_ID = "ordered-dense-control"
TT_CANDIDATE_IDS = (
    "flat-output-first",
    "flat-output-last",
    "fourier-output-first",
    "fourier-output-last",
    "d1q3-output-first",
    "d1q3-output-last",
)
METHOD_IDS = (SPARSE_METHOD_ID, DENSE_METHOD_ID, *TT_CANDIDATE_IDS)


@dataclass(frozen=True)
class CoefficientData:
    model: q011e.RealForcedQuadraticModel
    coordinate_map: ComplexArray
    native_chart_hessian: ComplexArray
    native_reduced_hessian: ComplexArray
    pairs: IntegerArray
    sectors: IntegerArray
    w_fibers: ComplexArray
    r_fibers: dict[int, ComplexArray]
    w_tensor: ComplexArray
    r_tensor: ComplexArray
    reconstruction_audit: dict[str, Any]
    coefficient_audit: dict[str, Any]


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).tiny)
    )


def _normalized_directions(seed: int, count: int) -> Array:
    generator = np.random.default_rng(seed)
    directions = generator.standard_normal((count, SELECTED_DIMENSION))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    return np.asarray(directions, dtype=np.float64)


def _median_absolute_deviation(values: list[float]) -> float:
    center = median(values)
    return float(median(abs(value - center) for value in values))


def _sealed_q011f1_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011f1.__file__).resolve().parent
        / "artifacts"
        / "q011f1_heldout_amplitude_reissue.json"
    )
    runner_path = Path(q011f1.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    q011f_record = cycle["sealed_q011f_artifact_audit"]["artifact"]
    observed_digests = (
        cycle["input_digest_sha256"],
        cycle["chart_reconstruction_digest_sha256"],
        cycle["heldout_trajectory_digest_sha256"],
        cycle["merged_fit_digest_sha256"],
        cycle["result_digest_sha256"],
    )
    registered_digests = (
        Q011F1_INPUT_DIGEST,
        Q011F1_CHART_DIGEST,
        Q011F1_HELDOUT_DIGEST,
        Q011F1_MERGED_DIGEST,
        Q011F1_RESULT_DIGEST,
    )
    checks = {
        "q011f1_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011F1_ARTIFACT_SHA256),
        "q011f1_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011F1_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011F1_RUNNER_SHA256
        ),
        "q011f1_package_source_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "q011f1_five_digests_match": observed_digests == registered_digests,
        "q011f1_valid_accepted_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        ),
        "q011f_rejected_outcome_remains_sealed": (
            q011f_record["hypothesis_outcome"] == "rejected"
            and q011f_record["sha256"] == q011f1.Q011F_ARTIFACT_SHA256
            and not cycle["numerical_consequence"]["q011f_original_rejected_outcome_changed"]
        ),
        "q011f1_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact) and _strict_json_serializable(artifact)
        ),
    }
    audit = {
        "artifact": {
            "filename": artifact_path.name,
            "sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "input_digest_sha256": observed_digests[0],
            "chart_reconstruction_digest_sha256": observed_digests[1],
            "heldout_trajectory_digest_sha256": observed_digests[2],
            "merged_fit_digest_sha256": observed_digests[3],
            "result_digest_sha256": observed_digests[4],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        },
        "preserved_q011f_artifact": q011f_record,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return q011e._json_native(audit), artifact


def _load_q011e_artifact() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011e.__file__).resolve().parent / "artifacts" / "q011e_forced_quadratic_chart.json"
    )
    runner_path = Path(q011e.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    checks = {
        "q011e_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011E_ARTIFACT_SHA256),
        "q011e_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011E_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011E_RUNNER_SHA256
        ),
        "q011e_digests_match": (
            (
                cycle["input_digest_sha256"],
                cycle["derivative_digest_sha256"],
                cycle["chart_digest_sha256"],
            )
            == (Q011E_INPUT_DIGEST, Q011E_DERIVATIVE_DIGEST, Q011E_CHART_DIGEST)
        ),
        "q011e_valid_rejected_window_is_preserved": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "rejected"
        ),
    }
    return {
        "artifact": {
            "filename": artifact_path.name,
            "sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }, artifact


def _reconstruct_native_coefficients(
    q011f1_artifact: dict[str, Any],
) -> tuple[
    q011e.RealForcedQuadraticModel,
    q011e.ComplexLinearData,
    ComplexArray,
    ComplexArray,
    ComplexArray,
    dict[str, Any],
]:
    q011e_artifact_audit, q011e_artifact = _load_q011e_artifact()
    artifact_cycle = q011e_artifact["cycle"]
    sealed_input, stripe_state, fixed_leaf_basis, q011d_artifact = q011e._sealed_input_audit()
    linear = q011e._complex_linear_data(
        stripe_state,
        fixed_leaf_basis,
        q011d_artifact,
    )
    (
        real_tangent,
        real_extractor,
        real_reduced_linear,
        coordinate_map,
        real_linear_audit,
    ) = q011e._real_linear_coordinates(linear)
    (
        analytic_hessian,
        chart_hessian,
        reduced_hessian,
        quadratic_construction,
    ) = q011e._quadratic_construction(linear)
    model, real_quadratic_audit = q011e._realify_quadratic_model(
        linear,
        real_tangent,
        real_extractor,
        real_reduced_linear,
        coordinate_map,
        analytic_hessian,
        chart_hessian,
        reduced_hessian,
    )
    independent_hessian = q011e._independent_hessian_audit(model)

    input_sections = q011e._json_native(
        {
            "registered_parameters": q011e._registered_parameters(),
            "sealed_input_audit": sealed_input,
        }
    )
    derivative_sections = q011e._json_native(
        {
            "complex_linear_coordinate_audit": linear.audit,
            "real_linear_coordinate_audit": real_linear_audit,
            "independent_hessian_audit": independent_hessian,
        }
    )
    chart_sections = q011e._json_native(
        {
            "quadratic_construction_audit": quadratic_construction,
            "real_quadratic_audit": real_quadratic_audit,
        }
    )
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    derivative_digest = q011e.q011c._canonical_json_sha256(derivative_sections)
    chart_digest = q011e.q011c._canonical_json_sha256(chart_sections)
    real_hashes = {
        "real_tangent_sha256": q011e.q011c._array_sha256(model.tangent),
        "real_extractor_sha256": q011e.q011c._array_sha256(model.extractor),
        "real_reduced_linear_sha256": q011e.q011c._array_sha256(model.reduced_linear),
        "analytic_second_derivative_sha256": q011e.q011c._array_sha256(model.second_derivative),
        "real_chart_hessian_sha256": q011e.q011c._array_sha256(model.hessian),
        "real_reduced_hessian_sha256": q011e.q011c._array_sha256(model.reduced_hessian),
    }
    native_hashes = {
        "native_chart_hessian_sha256": q011e.q011c._array_sha256(chart_hessian),
        "native_reduced_hessian_sha256": q011e.q011c._array_sha256(reduced_hessian),
        "coordinate_map_sha256": q011e.q011c._array_sha256(coordinate_map),
    }
    stored_q011f1_reconstruction = q011f1_artifact["cycle"]["q011e_chart_reconstruction_audit"]
    checks = {
        "q011e_artifact_is_sealed": q011e_artifact_audit["passed"],
        "q011e_input_sections_reproduce": (
            input_digest == Q011E_INPUT_DIGEST
            and input_sections["registered_parameters"] == artifact_cycle["registered_parameters"]
            and input_sections["sealed_input_audit"] == artifact_cycle["sealed_input_audit"]
        ),
        "q011e_derivative_sections_reproduce": (
            derivative_digest == Q011E_DERIVATIVE_DIGEST
            and derivative_sections["complex_linear_coordinate_audit"]
            == artifact_cycle["complex_linear_coordinate_audit"]
            and derivative_sections["real_linear_coordinate_audit"]
            == artifact_cycle["real_linear_coordinate_audit"]
            and derivative_sections["independent_hessian_audit"]
            == artifact_cycle["independent_hessian_audit"]
        ),
        "q011e_chart_sections_reproduce": (
            chart_digest == Q011E_CHART_DIGEST
            and chart_sections["quadratic_construction_audit"]
            == artifact_cycle["quadratic_construction_audit"]
            and chart_sections["real_quadratic_audit"] == artifact_cycle["real_quadratic_audit"]
        ),
        "six_real_array_hashes_reproduce": real_hashes == REAL_ARRAY_HASHES,
        "native_complex_and_coordinate_hashes_reproduce": (
            native_hashes
            == {
                "native_chart_hessian_sha256": NATIVE_CHART_HESSIAN_SHA256,
                "native_reduced_hessian_sha256": (NATIVE_REDUCED_HESSIAN_SHA256),
                "coordinate_map_sha256": COORDINATE_MAP_SHA256,
            }
        ),
        "q011f1_stored_chart_hashes_reproduce": (
            stored_q011f1_reconstruction["array_hashes"] == real_hashes
            and stored_q011f1_reconstruction["q011f_chart_reconstruction_digest_sha256"]
            == q011f1.Q011F_CHART_DIGEST
            and stored_q011f1_reconstruction["passed"]
        ),
        "all_reconstructed_chart_gates_pass": (
            linear.audit["passed"]
            and real_linear_audit["passed"]
            and independent_hessian["structural_passed"]
            and independent_hessian["hypothesis_passed"]
            and quadratic_construction["structural_passed"]
            and quadratic_construction["hypothesis_passed"]
            and real_quadratic_audit["structural_passed"]
            and real_quadratic_audit["hypothesis_passed"]
        ),
    }
    audit = q011e._json_native(
        {
            "q011e_artifact_audit": q011e_artifact_audit,
            "input_digest_sha256": input_digest,
            "derivative_digest_sha256": derivative_digest,
            "chart_digest_sha256": chart_digest,
            "real_array_hashes": real_hashes,
            "native_array_hashes": native_hashes,
            "maximum_complex_linear_structural_residual": linear.audit[
                "maximum_structural_residual"
            ],
            "maximum_sector_sylvester_relative_residual": (
                quadratic_construction["maximum_sector_sylvester_relative_residual"]
            ),
            "maximum_pairwise_homological_relative_residual": (
                quadratic_construction["maximum_pairwise_homological_relative_residual"]
            ),
            "checks": checks,
            "passed": all(checks.values()),
        }
    )
    return (
        model,
        linear,
        np.asarray(coordinate_map, dtype=np.complex128),
        np.asarray(chart_hessian, dtype=np.complex128),
        np.asarray(reduced_hessian, dtype=np.complex128),
        audit,
    )


def _polynomial_coefficients(
    hessian: npt.ArrayLike,
    pairs: npt.ArrayLike,
) -> ComplexArray:
    values = np.asarray(hessian, dtype=np.complex128)
    pair_table = np.asarray(pairs, dtype=np.int64)
    coefficients = np.empty((values.shape[0], len(pair_table)), dtype=np.complex128)
    for pair_index, (left, right) in enumerate(pair_table):
        factor = 0.5 if left == right else 1.0
        coefficients[:, pair_index] = factor * values[:, left, right]
    return coefficients


def _hessian_from_polynomial(
    coefficients: npt.ArrayLike,
    pairs: npt.ArrayLike,
    output_shape: tuple[int, ...],
) -> ComplexArray:
    fibers = np.asarray(coefficients, dtype=np.complex128)
    pair_table = np.asarray(pairs, dtype=np.int64)
    tensor = np.zeros(
        (*output_shape, SELECTED_DIMENSION, SELECTED_DIMENSION),
        dtype=np.complex128,
    )
    reshaped = fibers.reshape((*output_shape, len(pair_table)))
    for pair_index, (left, right) in enumerate(pair_table):
        factor = 2.0 if left == right else 1.0
        coefficient = factor * reshaped[..., pair_index]
        tensor[..., left, right] = coefficient
        tensor[..., right, left] = coefficient
    return tensor


def _serialized_arrays(
    arrays: dict[str, npt.ArrayLike],
) -> tuple[int, bool]:
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


def _owned_object_bytes(arrays: dict[str, npt.ArrayLike]) -> int:
    return int(
        sys.getsizeof(arrays)
        + sum(
            sys.getsizeof(name) + sys.getsizeof(np.asarray(value)) for name, value in arrays.items()
        )
    )


def _natural_arrays(data: CoefficientData) -> dict[str, npt.NDArray[Any]]:
    return {
        "pair_indices": np.asarray(data.pairs, dtype=np.uint8),
        "output_sectors": np.asarray(data.sectors, dtype=np.uint8),
        "w_fibers": np.asarray(data.w_fibers, dtype=np.complex128),
        **{
            f"r_sector_{sector}": np.asarray(data.r_fibers[sector], dtype=np.complex128)
            for sector in SELECTED_BLOCK_ORDER
        },
    }


def _scalar_sparse_diagnostic(
    arrays: dict[str, npt.NDArray[Any]],
) -> dict[str, Any]:
    coefficient_names = [
        "w_fibers",
        *(f"r_sector_{sector}" for sector in SELECTED_BLOCK_ORDER),
    ]
    group_ids: list[np.ndarray] = []
    linear_indices: list[np.ndarray] = []
    values: list[np.ndarray] = []
    for group_id, name in enumerate(coefficient_names):
        flat = np.asarray(arrays[name], dtype=np.complex128).ravel()
        indices = np.flatnonzero(flat != 0.0)
        group_ids.append(np.full(len(indices), group_id, dtype=np.uint8))
        linear_indices.append(np.asarray(indices, dtype=np.uint32))
        values.append(np.asarray(flat[indices], dtype=np.complex128))
    scalar_arrays = {
        "group_ids": np.concatenate(group_ids),
        "linear_indices": np.concatenate(linear_indices),
        "values": np.concatenate(values),
        "pair_indices": np.asarray(arrays["pair_indices"], dtype=np.uint8),
        "output_sectors": np.asarray(arrays["output_sectors"], dtype=np.uint8),
    }
    serialized_bytes, roundtrip = _serialized_arrays(scalar_arrays)
    value_count = int(scalar_arrays["values"].size)
    return {
        "bitwise_nonzero_complex_coefficient_count": value_count,
        "coefficient_stored_real_scalar_count": 2 * value_count,
        "raw_array_payload_bytes": int(sum(value.nbytes for value in scalar_arrays.values())),
        "in_memory_object_bytes": _owned_object_bytes(scalar_arrays),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "serialization_roundtrip_bitwise_equal": roundtrip,
    }


def _natural_storage(
    arrays: dict[str, npt.NDArray[Any]],
    *,
    scalar_sparse_diagnostic: dict[str, Any] | None = None,
) -> dict[str, Any]:
    serialized_bytes, roundtrip = _serialized_arrays(arrays)
    coefficient_names = [
        "w_fibers",
        *(f"r_sector_{sector}" for sector in SELECTED_BLOCK_ORDER),
    ]
    coefficient_complex_count = int(sum(arrays[name].size for name in coefficient_names))
    coefficient_bytes = int(sum(arrays[name].nbytes for name in coefficient_names))
    metadata_bytes = int(arrays["pair_indices"].nbytes + arrays["output_sectors"].nbytes)
    return {
        "w_fiber_count": int(arrays["w_fibers"].shape[0]),
        "r_active_fiber_count": int(
            sum(arrays[f"r_sector_{sector}"].shape[0] for sector in SELECTED_BLOCK_ORDER)
        ),
        "coefficient_complex_entry_count": coefficient_complex_count,
        "coefficient_stored_real_scalar_count": 2 * coefficient_complex_count,
        "coefficient_payload_bytes": coefficient_bytes,
        "index_and_sector_metadata_bytes": metadata_bytes,
        "raw_array_payload_bytes": int(sum(value.nbytes for value in arrays.values())),
        "in_memory_object_bytes": _owned_object_bytes(arrays),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "serialization_roundtrip_bitwise_equal": roundtrip,
        "scalar_sparse_lossless_diagnostic": (
            _scalar_sparse_diagnostic(arrays)
            if scalar_sparse_diagnostic is None
            else scalar_sparse_diagnostic
        ),
    }


def _dense_storage(arrays: dict[str, npt.NDArray[Any]]) -> dict[str, Any]:
    serialized_bytes, roundtrip = _serialized_arrays(arrays)
    complex_count = int(sum(value.size for value in arrays.values()))
    return {
        "complex_entry_count": complex_count,
        "stored_real_scalar_count": 2 * complex_count,
        "raw_array_payload_bytes": int(sum(value.nbytes for value in arrays.values())),
        "in_memory_object_bytes": _owned_object_bytes(arrays),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "serialization_roundtrip_bitwise_equal": roundtrip,
    }


def _tt_bundle_storage(
    w_cores: list[npt.NDArray[Any]],
    r_cores: list[npt.NDArray[Any]],
) -> dict[str, Any]:
    w_ranks = np.asarray(tt_ranks(w_cores), dtype=np.int64)
    r_ranks = np.asarray(tt_ranks(r_cores), dtype=np.int64)
    w_shape = np.asarray([core.shape[1] for core in w_cores], dtype=np.int64)
    r_shape = np.asarray([core.shape[1] for core in r_cores], dtype=np.int64)
    arrays = {
        **{f"w_core_{index:03d}": np.asarray(core) for index, core in enumerate(w_cores)},
        **{f"r_core_{index:03d}": np.asarray(core) for index, core in enumerate(r_cores)},
        "w_ranks": w_ranks,
        "r_ranks": r_ranks,
        "w_mode_shape": w_shape,
        "r_mode_shape": r_shape,
    }
    serialized_bytes, roundtrip = _serialized_arrays(arrays)
    core_entries = int(sum(core.size for core in (*w_cores, *r_cores)))
    gauge_complex_dimension = core_entries - int(
        sum(rank * rank for rank in w_ranks[1:-1]) + sum(rank * rank for rank in r_ranks[1:-1])
    )
    return {
        "tt_count": 2,
        "w_core_count": len(w_cores),
        "r_core_count": len(r_cores),
        "w_tt_ranks": w_ranks.tolist(),
        "r_tt_ranks": r_ranks.tolist(),
        "w_mode_shape": w_shape.tolist(),
        "r_mode_shape": r_shape.tolist(),
        "complex_core_entry_count": core_entries,
        "core_stored_real_scalar_count": 2 * core_entries,
        "core_payload_bytes": int(sum(core.nbytes for core in (*w_cores, *r_cores))),
        "rank_and_shape_metadata_bytes": int(
            w_ranks.nbytes + r_ranks.nbytes + w_shape.nbytes + r_shape.nbytes
        ),
        "raw_array_payload_bytes": int(sum(value.nbytes for value in arrays.values())),
        "in_memory_object_bytes": _owned_object_bytes(arrays),
        "uncompressed_npz_serialized_bytes": serialized_bytes,
        "nominal_gauge_adjusted_real_dimension": 2 * gauge_complex_dimension,
        "serialization_roundtrip_bitwise_equal": roundtrip,
    }


def _coefficient_data(
    q011f1_artifact: dict[str, Any],
) -> CoefficientData:
    (
        model,
        linear,
        coordinate_map,
        native_w,
        native_r,
        reconstruction_audit,
    ) = _reconstruct_native_coefficients(q011f1_artifact)
    pairs = np.asarray(linear.pairs, dtype=np.int64)
    pair_to_sector = {
        pair_index: sector
        for sector, pair_indices in linear.sector_indices.items()
        for pair_index in pair_indices
    }
    sectors = np.asarray(
        [pair_to_sector[pair_index] for pair_index in range(PAIR_COUNT)],
        dtype=np.int64,
    )

    w_polynomial = _polynomial_coefficients(native_w, pairs)
    r_polynomial = _polynomial_coefficients(native_r, pairs)
    w_field = w_polynomial.reshape(
        SIZE,
        SIZE,
        9,
        PAIR_COUNT,
    )
    w_fourier_polynomial = np.asarray(
        np.transpose(
            np.fft.fft(w_field, axis=1) / np.sqrt(SIZE),
            (1, 0, 2, 3),
        ),
        dtype=np.complex128,
    )
    w_fibers = np.empty((PAIR_COUNT, SIZE, 9), dtype=np.complex128)
    projected_w_polynomial = np.zeros_like(w_fourier_polynomial)
    r_fibers: dict[int, ComplexArray] = {}
    projected_r_polynomial = np.zeros_like(r_polynomial)
    for pair_index, sector in enumerate(sectors):
        w_fibers[pair_index] = w_fourier_polynomial[sector, :, :, pair_index]
        projected_w_polynomial[sector, :, :, pair_index] = w_fibers[pair_index]
    for sector in SELECTED_BLOCK_ORDER:
        pair_indices = np.flatnonzero(sectors == sector)
        output_slice = SELECTED_OFFSETS[sector]
        fibers = np.asarray(
            r_polynomial[output_slice, :][:, pair_indices].T,
            dtype=np.complex128,
        )
        r_fibers[sector] = fibers
        projected_r_polynomial[output_slice, pair_indices] = fibers.T

    w_tensor = _hessian_from_polynomial(
        projected_w_polynomial.reshape(-1, PAIR_COUNT),
        pairs,
        (SIZE, SIZE, 9),
    )
    r_tensor = _hessian_from_polynomial(
        projected_r_polynomial,
        pairs,
        (SELECTED_DIMENSION,),
    )
    native_w_tensor = np.asarray(
        np.transpose(
            np.fft.fft(
                native_w.reshape(
                    SIZE,
                    SIZE,
                    9,
                    SELECTED_DIMENSION,
                    SELECTED_DIMENSION,
                ),
                axis=1,
            )
            / np.sqrt(SIZE),
            (1, 0, 2, 3, 4),
        ),
        dtype=np.complex128,
    )
    w_projection_loss = _relative_norm(w_tensor - native_w_tensor, native_w_tensor)
    r_projection_loss = _relative_norm(r_tensor - native_r, native_r)
    natural_arrays = {
        "pair_indices": np.asarray(pairs, dtype=np.uint8),
        "output_sectors": np.asarray(sectors, dtype=np.uint8),
        "w_fibers": w_fibers,
        **{f"r_sector_{sector}": r_fibers[sector] for sector in SELECTED_BLOCK_ORDER},
    }
    natural_storage = _natural_storage(natural_arrays)
    sector_counts = {
        str(sector): int(np.count_nonzero(sectors == sector)) for sector in OUTPUT_SECTOR_ORDER
    }
    checks = {
        "three_hundred_pairs_are_complete": (
            pairs.shape == (PAIR_COUNT, 2)
            and np.array_equal(
                pairs,
                np.asarray(linear.pairs, dtype=np.int64),
            )
        ),
        "registered_sector_counts_reproduce": sector_counts
        == {str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()},
        "natural_array_shapes_are_registered": (
            w_fibers.shape == (300, 17, 9)
            and r_fibers[0].shape == (102, 6)
            and r_fibers[1].shape == (54, 9)
            and r_fibers[16].shape == (54, 9)
            and w_tensor.shape == (17, 17, 9, 24, 24)
            and r_tensor.shape == (24, 24, 24)
        ),
        "projection_losses_are_within_tolerance": (
            w_projection_loss <= MAXIMUM_PROJECTION_RELATIVE_LOSS
            and r_projection_loss <= MAXIMUM_PROJECTION_RELATIVE_LOSS
        ),
        "natural_storage_counts_are_preregistered": (
            natural_storage["coefficient_complex_entry_count"] == 47_484
            and natural_storage["coefficient_stored_real_scalar_count"] == 94_968
            and natural_storage["raw_array_payload_bytes"] == 760_644
        ),
        "natural_serialization_roundtrip_is_bitwise_equal": (
            natural_storage["serialization_roundtrip_bitwise_equal"]
            and natural_storage["scalar_sparse_lossless_diagnostic"][
                "serialization_roundtrip_bitwise_equal"
            ]
        ),
        "all_projected_coefficients_are_finite": bool(
            np.all(np.isfinite(w_fibers))
            and all(np.all(np.isfinite(value)) for value in r_fibers.values())
            and np.all(np.isfinite(w_tensor))
            and np.all(np.isfinite(r_tensor))
        ),
    }
    audit = q011e._json_native(
        {
            "pair_count": PAIR_COUNT,
            "pair_indices_sha256": q011e.q011c._array_sha256(pairs),
            "output_sector_order": list(OUTPUT_SECTOR_ORDER),
            "sector_pair_counts": sector_counts,
            "output_sectors_sha256": q011e.q011c._array_sha256(sectors),
            "w_fibers_shape": list(w_fibers.shape),
            "w_fibers_sha256": q011e.q011c._array_sha256(w_fibers),
            "r_fiber_shapes": {
                str(sector): list(r_fibers[sector].shape) for sector in SELECTED_BLOCK_ORDER
            },
            "r_fiber_sha256": {
                str(sector): q011e.q011c._array_sha256(r_fibers[sector])
                for sector in SELECTED_BLOCK_ORDER
            },
            "projected_w_tensor_shape": list(w_tensor.shape),
            "projected_r_tensor_shape": list(r_tensor.shape),
            "projected_w_tensor_sha256": q011e.q011c._array_sha256(w_tensor),
            "projected_r_tensor_sha256": q011e.q011c._array_sha256(r_tensor),
            "w_projection_relative_loss": w_projection_loss,
            "r_projection_relative_loss": r_projection_loss,
            "natural_storage": natural_storage,
            "checks": checks,
            "passed": all(checks.values()),
        }
    )
    return CoefficientData(
        model=model,
        coordinate_map=coordinate_map,
        native_chart_hessian=native_w,
        native_reduced_hessian=native_r,
        pairs=pairs,
        sectors=sectors,
        w_fibers=w_fibers,
        r_fibers=r_fibers,
        w_tensor=w_tensor,
        r_tensor=r_tensor,
        reconstruction_audit=reconstruction_audit,
        coefficient_audit=audit,
    )


def _velocity_permutation() -> IntegerArray:
    velocities = np.asarray(D2Q9_VELOCITIES, dtype=np.int64)
    return np.asarray(
        np.lexsort((velocities[:, 0], velocities[:, 1])),
        dtype=np.int64,
    )


def _tensorize_w(w_tensor: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    tensor = np.asarray(w_tensor, dtype=np.complex128)
    if tensor.shape != (17, 17, 9, 24, 24):
        raise ValueError("Q011g W tensor has the wrong canonical shape")
    if candidate_id == "flat-output-first":
        return np.asarray(tensor.reshape(2601, 24, 24), dtype=np.complex128)
    if candidate_id == "flat-output-last":
        return np.asarray(
            tensor.transpose(3, 4, 0, 1, 2).reshape(24, 24, 2601),
            dtype=np.complex128,
        )
    if candidate_id == "fourier-output-first":
        return tensor.copy()
    if candidate_id == "fourier-output-last":
        return np.asarray(tensor.transpose(3, 4, 0, 1, 2), dtype=np.complex128)
    reordered = tensor[:, :, _velocity_permutation(), :, :]
    if candidate_id == "d1q3-output-first":
        return np.asarray(
            reordered.reshape(17, 17, 3, 3, 24, 24),
            dtype=np.complex128,
        )
    if candidate_id == "d1q3-output-last":
        return np.asarray(
            reordered.transpose(3, 4, 0, 1, 2).reshape(24, 24, 17, 17, 3, 3),
            dtype=np.complex128,
        )
    raise ValueError(f"unknown Q011g candidate: {candidate_id}")


def _untensorize_w(tensorized: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    tensor = np.asarray(tensorized, dtype=np.complex128)
    if candidate_id == "flat-output-first":
        return np.asarray(tensor.reshape(17, 17, 9, 24, 24))
    if candidate_id == "flat-output-last":
        return np.asarray(tensor.reshape(24, 24, 17, 17, 9).transpose(2, 3, 4, 0, 1))
    if candidate_id == "fourier-output-first":
        return tensor.copy()
    if candidate_id == "fourier-output-last":
        return np.asarray(tensor.transpose(2, 3, 4, 0, 1))
    if candidate_id == "d1q3-output-first":
        lexicographic = tensor.reshape(17, 17, 9, 24, 24)
    elif candidate_id == "d1q3-output-last":
        lexicographic = tensor.reshape(24, 24, 17, 17, 9).transpose(2, 3, 4, 0, 1)
    else:
        raise ValueError(f"unknown Q011g candidate: {candidate_id}")
    result = np.empty_like(lexicographic)
    result[:, :, _velocity_permutation(), :, :] = lexicographic
    return result


def _tensorize_r(r_tensor: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    tensor = np.asarray(r_tensor, dtype=np.complex128)
    if tensor.shape != (24, 24, 24):
        raise ValueError("Q011g R tensor has the wrong canonical shape")
    if candidate_id.endswith("output-first"):
        return tensor.copy()
    if candidate_id.endswith("output-last"):
        return np.asarray(tensor.transpose(1, 2, 0), dtype=np.complex128)
    raise ValueError(f"unknown Q011g candidate: {candidate_id}")


def _untensorize_r(tensorized: npt.ArrayLike, candidate_id: str) -> ComplexArray:
    tensor = np.asarray(tensorized, dtype=np.complex128)
    if candidate_id.endswith("output-first"):
        return tensor.copy()
    if candidate_id.endswith("output-last"):
        return np.asarray(tensor.transpose(2, 0, 1), dtype=np.complex128)
    raise ValueError(f"unknown Q011g candidate: {candidate_id}")


def _natural_action(
    data: CoefficientData,
    coordinates: npt.ArrayLike,
) -> tuple[ComplexArray, ComplexArray]:
    value = np.asarray(coordinates, dtype=np.complex128)
    products = value[data.pairs[:, 0]] * value[data.pairs[:, 1]]
    w_output = np.zeros((SIZE, SIZE, 9), dtype=np.complex128)
    r_output = np.zeros(SELECTED_DIMENSION, dtype=np.complex128)
    for sector in OUTPUT_SECTOR_ORDER:
        mask = data.sectors == sector
        w_output[sector] = np.einsum(
            "p,pyq->yq",
            products[mask],
            data.w_fibers[mask],
            optimize=True,
        )
    for sector in SELECTED_BLOCK_ORDER:
        mask = data.sectors == sector
        r_output[SELECTED_OFFSETS[sector]] = np.einsum(
            "p,pr->r",
            products[mask],
            data.r_fibers[sector],
            optimize=True,
        )
    return w_output, r_output


def _dense_action(
    data: CoefficientData,
    coordinates: npt.ArrayLike,
) -> tuple[ComplexArray, ComplexArray]:
    value = np.asarray(coordinates, dtype=np.complex128)
    w_output = 0.5 * np.einsum(
        "xyqab,a,b->xyq",
        data.w_tensor,
        value,
        value,
        optimize=True,
    )
    r_output = 0.5 * np.einsum(
        "rab,a,b->r",
        data.r_tensor,
        value,
        value,
        optimize=True,
    )
    return (
        np.asarray(w_output, dtype=np.complex128),
        np.asarray(r_output, dtype=np.complex128),
    )


def _tt_action(
    w_cores: list[npt.NDArray[Any]],
    r_cores: list[npt.NDArray[Any]],
    coordinates: npt.ArrayLike,
    candidate_id: str,
) -> tuple[ComplexArray, ComplexArray]:
    value = np.asarray(coordinates, dtype=np.complex128)
    output_first = candidate_id.endswith("output-first")
    if candidate_id.startswith("flat-"):
        w_modes = [None, value, value] if output_first else [value, value, None]
        w_raw = np.asarray(contract_tt(w_cores, w_modes)).reshape(17, 17, 9)
    elif candidate_id.startswith("fourier-"):
        w_modes = (
            [None, None, None, value, value] if output_first else [value, value, None, None, None]
        )
        w_raw = np.asarray(contract_tt(w_cores, w_modes)).reshape(17, 17, 9)
    elif candidate_id.startswith("d1q3-"):
        w_modes = (
            [None, None, None, None, value, value]
            if output_first
            else [value, value, None, None, None, None]
        )
        lexicographic = np.asarray(contract_tt(w_cores, w_modes)).reshape(17, 17, 9)
        w_raw = np.empty_like(lexicographic)
        w_raw[:, :, _velocity_permutation()] = lexicographic
    else:
        raise ValueError(f"unknown Q011g candidate: {candidate_id}")
    r_modes = [None, value, value] if output_first else [value, value, None]
    r_raw = np.asarray(contract_tt(r_cores, r_modes)).reshape(24)
    return (
        np.asarray(0.5 * w_raw, dtype=np.complex128),
        np.asarray(0.5 * r_raw, dtype=np.complex128),
    )


def _physical_actions(
    data: CoefficientData,
    action: tuple[npt.ArrayLike, npt.ArrayLike],
) -> tuple[Array, Array, float]:
    w_fourier = np.asarray(action[0], dtype=np.complex128)
    r_complex = np.asarray(action[1], dtype=np.complex128)
    w_physical_complex = np.fft.ifft(w_fourier.transpose(1, 0, 2), axis=1) * np.sqrt(SIZE)
    r_real_complex = data.coordinate_map.conj().T @ r_complex
    imaginary_leakage = max(
        _relative_norm(w_physical_complex.imag, w_physical_complex.real),
        _relative_norm(r_real_complex.imag, r_real_complex.real),
    )
    return (
        np.asarray(w_physical_complex.real.ravel(), dtype=np.float64),
        np.asarray(r_real_complex.real, dtype=np.float64),
        imaginary_leakage,
    )


def _state_conservation_drift(state: Array, base_conserved: Array) -> float:
    return float(
        np.linalg.norm(global_conserved_quantities(state.reshape(SIZE, SIZE, 9)) - base_conserved)
    )


def _method_defect(
    data: CoefficientData,
    action_method: Callable[[ComplexArray], tuple[ComplexArray, ComplexArray]],
    coordinates: npt.ArrayLike,
) -> tuple[Array, dict[str, float]]:
    value = np.asarray(coordinates, dtype=np.float64)
    complex_value = data.coordinate_map @ value
    w_action, r_action, first_imaginary = _physical_actions(
        data,
        action_method(complex_value),
    )
    state = data.model.base + data.model.tangent @ value + w_action
    reduced = data.model.reduced_linear @ value + r_action
    next_complex = data.coordinate_map @ reduced
    next_w, _, second_imaginary = _physical_actions(
        data,
        action_method(next_complex),
    )
    full_next = data.model.full_map(state)
    lifted_next = data.model.base + data.model.tangent @ reduced + next_w
    base_conserved = global_conserved_quantities(data.model.base.reshape(SIZE, SIZE, 9))
    return (
        np.asarray(full_next - lifted_next, dtype=np.float64),
        {
            "minimum_population": min(
                float(np.min(state)),
                float(np.min(full_next)),
                float(np.min(lifted_next)),
            ),
            "maximum_global_conservation_drift": max(
                _state_conservation_drift(state, base_conserved),
                _state_conservation_drift(full_next, base_conserved),
                _state_conservation_drift(lifted_next, base_conserved),
            ),
            "maximum_imaginary_leakage_relative_norm": max(
                first_imaginary,
                second_imaginary,
            ),
        },
    )


def _prepare_method(
    method_id: str,
    data: CoefficientData,
) -> dict[str, Any]:
    subphase: dict[str, int] = {}
    if method_id == SPARSE_METHOD_ID:
        started = perf_counter_ns()
        arrays = {name: np.array(value, copy=True) for name, value in _natural_arrays(data).items()}
        subphase["fresh_copy_nanoseconds"] = perf_counter_ns() - started
        started = perf_counter_ns()
        scalar_diagnostic = data.coefficient_audit["natural_storage"][
            "scalar_sparse_lossless_diagnostic"
        ]
        storage = _natural_storage(
            arrays,
            scalar_sparse_diagnostic=scalar_diagnostic,
        )
        subphase["storage_and_serialization_nanoseconds"] = perf_counter_ns() - started
        return {
            "method_id": method_id,
            "representation": arrays,
            "storage": storage,
            "subphase_nanoseconds": subphase,
        }
    if method_id == DENSE_METHOD_ID:
        started = perf_counter_ns()
        arrays = {
            "w_tensor": np.array(data.w_tensor, copy=True),
            "r_tensor": np.array(data.r_tensor, copy=True),
        }
        subphase["fresh_copy_nanoseconds"] = perf_counter_ns() - started
        started = perf_counter_ns()
        storage = _dense_storage(arrays)
        subphase["storage_and_serialization_nanoseconds"] = perf_counter_ns() - started
        return {
            "method_id": method_id,
            "representation": arrays,
            "storage": storage,
            "subphase_nanoseconds": subphase,
        }
    if method_id not in TT_CANDIDATE_IDS:
        raise ValueError(f"unknown Q011g method: {method_id}")

    started = perf_counter_ns()
    w_tensorized = _tensorize_w(data.w_tensor, method_id)
    r_tensorized = _tensorize_r(data.r_tensor, method_id)
    subphase["tensorization_nanoseconds"] = perf_counter_ns() - started
    mapping_roundtrip = bool(
        np.array_equal(_untensorize_w(w_tensorized, method_id), data.w_tensor)
        and np.array_equal(_untensorize_r(r_tensorized, method_id), data.r_tensor)
    )
    started = perf_counter_ns()
    w_cores, w_diagnostics = tt_svd_with_diagnostics(
        w_tensorized,
        relative_tolerance=TT_RELATIVE_TOLERANCE,
        max_rank=None,
    )
    w_cores = [np.array(core, copy=True, order="C") for core in w_cores]
    subphase["w_tt_svd_rounding_nanoseconds"] = perf_counter_ns() - started
    started = perf_counter_ns()
    r_cores, r_diagnostics = tt_svd_with_diagnostics(
        r_tensorized,
        relative_tolerance=TT_RELATIVE_TOLERANCE,
        max_rank=None,
    )
    r_cores = [np.array(core, copy=True, order="C") for core in r_cores]
    subphase["r_tt_svd_rounding_nanoseconds"] = perf_counter_ns() - started
    started = perf_counter_ns()
    storage = _tt_bundle_storage(w_cores, r_cores)
    subphase["storage_and_serialization_nanoseconds"] = perf_counter_ns() - started
    return {
        "method_id": method_id,
        "representation": {
            "w_cores": w_cores,
            "r_cores": r_cores,
        },
        "mapping_roundtrip_bitwise_equal": mapping_roundtrip,
        "w_tt_svd_diagnostics": w_diagnostics,
        "r_tt_svd_diagnostics": r_diagnostics,
        "storage": storage,
        "subphase_nanoseconds": subphase,
    }


def _timed_prepare(
    method_id: str,
    data: CoefficientData,
) -> tuple[int, dict[str, Any]]:
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        started = perf_counter_ns()
        prepared = _prepare_method(method_id, data)
        elapsed = perf_counter_ns() - started
    finally:
        if was_enabled:
            gc.enable()
    return elapsed, prepared


def _offline_campaign(
    data: CoefficientData,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    for _ in range(OFFLINE_WARMUP_BLOCKS):
        for method_id in METHOD_IDS:
            elapsed, prepared = _timed_prepare(method_id, data)
            if elapsed <= 0:
                raise RuntimeError("Q011g offline warmup returned nonpositive time")
            if not prepared["storage"]["serialization_roundtrip_bitwise_equal"]:
                raise RuntimeError("Q011g offline warmup serialization failed")
            del prepared
            gc.collect()

    durations: dict[str, list[int]] = {method_id: [] for method_id in METHOD_IDS}
    subphases: dict[str, dict[str, list[int]]] = {method_id: {} for method_id in METHOD_IDS}
    storages: dict[str, dict[str, Any]] = {}
    retained: dict[str, dict[str, Any]] = {}
    order_by_block: list[list[str]] = []
    method_ids = list(METHOD_IDS)
    for block in range(OFFLINE_MEASURED_BLOCKS):
        offset = block % len(method_ids)
        order = method_ids[offset:] + method_ids[:offset]
        order_by_block.append(order)
        for method_id in order:
            elapsed, prepared = _timed_prepare(method_id, data)
            storage = prepared["storage"]
            if method_id in storages and storages[method_id] != storage:
                raise RuntimeError("Q011g offline storage changed between blocks")
            storages[method_id] = storage
            durations[method_id].append(elapsed)
            for name, value in prepared["subphase_nanoseconds"].items():
                subphases[method_id].setdefault(name, []).append(value)
            retained[method_id] = prepared
            gc.collect()

    records: dict[str, Any] = {}
    for method_id in METHOD_IDS:
        samples = durations[method_id]
        subphase_records = {
            name: {
                "nanoseconds_by_block": values,
                "minimum_nanoseconds": min(values),
                "maximum_nanoseconds": max(values),
                "median_nanoseconds": float(median(values)),
            }
            for name, values in subphases[method_id].items()
        }
        records[method_id] = {
            "nanoseconds_by_block": samples,
            "minimum_nanoseconds": min(samples),
            "maximum_nanoseconds": max(samples),
            "median_nanoseconds": float(median(samples)),
            "median_absolute_deviation_nanoseconds": (
                _median_absolute_deviation([float(value) for value in samples])
            ),
            "subphase_records": subphase_records,
            "all_times_positive_and_finite": bool(
                all(value > 0 and math.isfinite(float(value)) for value in samples)
                and all(
                    value > 0 and math.isfinite(float(value))
                    for record in subphase_records.values()
                    for value in record["nanoseconds_by_block"]
                )
            ),
            "storage": storages[method_id],
        }
    return (
        {
            "timer": "perf_counter_ns",
            "common_chart_coefficient_projection_and_dense_materialization_excluded": True,
            "common_input_exclusion_is_tt_favorable": True,
            "warmup_block_count": OFFLINE_WARMUP_BLOCKS,
            "measured_block_count": OFFLINE_MEASURED_BLOCKS,
            "order_by_block": order_by_block,
            "method_records": records,
        },
        retained,
    )


def _direction_audit() -> tuple[Array, ComplexArray, dict[str, Any]]:
    directions = _normalized_directions(ACTION_SEED, ACTION_DIRECTION_COUNT)
    complex_directions = np.asarray(
        directions @ np.eye(SELECTED_DIMENSION),
        dtype=np.complex128,
    )
    norm_errors = np.abs(np.linalg.norm(directions, axis=1) - 1.0)
    prior_directions = [
        _normalized_directions(seed, count) for seed, count in PRIOR_DIRECTION_CAMPAIGNS
    ]
    duplicate_count = sum(
        int(np.array_equal(direction, prior))
        for direction in directions
        for campaign in prior_directions
        for prior in campaign
    )
    audit = {
        "seed": ACTION_SEED,
        "direction_count": ACTION_DIRECTION_COUNT,
        "direction_sha256": q011e.q011c._array_sha256(directions),
        "maximum_unit_norm_error": float(np.max(norm_errors)),
        "prior_campaigns": [
            {"seed": seed, "direction_count": count} for seed, count in PRIOR_DIRECTION_CAMPAIGNS
        ],
        "exact_duplicate_count_vs_prior": duplicate_count,
        "checks": {
            "direction_shape_is_registered": directions.shape
            == (ACTION_DIRECTION_COUNT, SELECTED_DIMENSION),
            "all_directions_are_unit_norm": float(np.max(norm_errors)) <= 1.0e-14,
            "no_direction_duplicates_prior_campaigns": duplicate_count == 0,
            "all_direction_values_are_finite": bool(np.all(np.isfinite(directions))),
        },
    }
    audit["passed"] = all(audit["checks"].values())
    return directions, complex_directions, q011e._json_native(audit)


def _complex_directions(data: CoefficientData, directions: Array) -> ComplexArray:
    return np.asarray(
        (data.coordinate_map @ directions.T).T,
        dtype=np.complex128,
    )


def _joint_relative_error(
    observed: tuple[npt.ArrayLike, npt.ArrayLike],
    reference: tuple[npt.ArrayLike, npt.ArrayLike],
) -> float:
    numerator = float(
        np.hypot(
            np.linalg.norm(np.asarray(observed[0]) - np.asarray(reference[0])),
            np.linalg.norm(np.asarray(observed[1]) - np.asarray(reference[1])),
        )
    )
    denominator = float(
        np.hypot(
            np.linalg.norm(np.asarray(reference[0])),
            np.linalg.norm(np.asarray(reference[1])),
        )
    )
    return numerator / max(denominator, np.finfo(float).tiny)


def _candidate_method(
    prepared: dict[str, Any],
    candidate_id: str,
) -> Callable[[ComplexArray], tuple[ComplexArray, ComplexArray]]:
    representation = prepared["representation"]
    return lambda vector: _tt_action(
        representation["w_cores"],
        representation["r_cores"],
        vector,
        candidate_id,
    )


def _fidelity_audit(
    data: CoefficientData,
    directions: Array,
    complex_directions: ComplexArray,
    retained: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    sparse_actions = [_natural_action(data, value) for value in complex_directions]
    dense_actions = [_dense_action(data, value) for value in complex_directions]
    dense_sparse_errors = [
        _joint_relative_error(dense, sparse)
        for dense, sparse in zip(dense_actions, sparse_actions, strict=True)
    ]
    sparse_realification_errors: list[float] = []
    sparse_imaginary_leakages: list[float] = []
    for direction, sparse_action in zip(directions, sparse_actions, strict=True):
        w_real, r_real, imaginary = _physical_actions(data, sparse_action)
        reference_w = 0.5 * np.einsum(
            "nij,i,j->n",
            data.model.hessian,
            direction,
            direction,
            optimize=True,
        )
        reference_r = 0.5 * np.einsum(
            "rij,i,j->r",
            data.model.reduced_hessian,
            direction,
            direction,
            optimize=True,
        )
        sparse_realification_errors.append(
            _joint_relative_error((w_real, r_real), (reference_w, reference_r))
        )
        sparse_imaginary_leakages.append(imaginary)

    candidate_records: dict[str, Any] = {}
    for candidate_id in TT_CANDIDATE_IDS:
        prepared = retained[candidate_id]
        representation = prepared["representation"]
        w_reconstructed = _untensorize_w(
            reconstruct(representation["w_cores"]),
            candidate_id,
        )
        r_reconstructed = _untensorize_r(
            reconstruct(representation["r_cores"]),
            candidate_id,
        )
        w_reconstruction_error = _relative_norm(
            w_reconstructed - data.w_tensor,
            data.w_tensor,
        )
        r_reconstruction_error = _relative_norm(
            r_reconstructed - data.r_tensor,
            data.r_tensor,
        )
        method = _candidate_method(prepared, candidate_id)
        observed_actions = [method(value) for value in complex_directions]
        sparse_errors = [
            _joint_relative_error(observed, reference)
            for observed, reference in zip(
                observed_actions,
                sparse_actions,
                strict=True,
            )
        ]
        dense_errors = [
            _joint_relative_error(observed, reference)
            for observed, reference in zip(
                observed_actions,
                dense_actions,
                strict=True,
            )
        ]
        realification_errors: list[float] = []
        imaginary_leakages: list[float] = []
        for direction, observed in zip(directions, observed_actions, strict=True):
            w_real, r_real, imaginary = _physical_actions(data, observed)
            reference_w = 0.5 * np.einsum(
                "nij,i,j->n",
                data.model.hessian,
                direction,
                direction,
                optimize=True,
            )
            reference_r = 0.5 * np.einsum(
                "rij,i,j->r",
                data.model.reduced_hessian,
                direction,
                direction,
                optimize=True,
            )
            realification_errors.append(
                _joint_relative_error((w_real, r_real), (reference_w, reference_r))
            )
            imaginary_leakages.append(imaginary)
        finite = bool(
            np.all(np.isfinite(w_reconstructed))
            and np.all(np.isfinite(r_reconstructed))
            and all(np.all(np.isfinite(value)) for action in observed_actions for value in action)
            and all(
                np.all(np.isfinite(core))
                for core in (
                    *representation["w_cores"],
                    *representation["r_cores"],
                )
            )
        )
        passed = bool(
            prepared["mapping_roundtrip_bitwise_equal"]
            and max(w_reconstruction_error, r_reconstruction_error)
            <= MAXIMUM_TT_RECONSTRUCTION_ERROR
            and max(sparse_errors) <= MAXIMUM_TT_ACTION_ERROR
            and max(dense_errors) <= MAXIMUM_TT_ACTION_ERROR
            and max(realification_errors) <= MAXIMUM_REALIFICATION_ACTION_ERROR
            and prepared["storage"]["serialization_roundtrip_bitwise_equal"]
            and finite
        )
        candidate_records[candidate_id] = {
            "mapping_roundtrip_bitwise_equal": prepared["mapping_roundtrip_bitwise_equal"],
            "w_relative_tensor_reconstruction_error": w_reconstruction_error,
            "r_relative_tensor_reconstruction_error": r_reconstruction_error,
            "maximum_relative_action_error_vs_sparse": max(sparse_errors),
            "maximum_relative_action_error_vs_dense": max(dense_errors),
            "maximum_realification_action_error": max(realification_errors),
            "maximum_imaginary_leakage_relative_norm": max(imaginary_leakages),
            "all_values_finite": finite,
            "passed": passed,
        }
        del w_reconstructed, r_reconstructed, observed_actions

    checks = {
        "natural_and_dense_actions_agree": max(dense_sparse_errors)
        <= MAXIMUM_SPARSE_DENSE_ACTION_ERROR,
        "natural_actions_realify_to_sealed_hessians": max(sparse_realification_errors)
        <= MAXIMUM_REALIFICATION_ACTION_ERROR,
        "all_candidate_fidelity_records_pass": all(
            record["passed"] for record in candidate_records.values()
        ),
    }
    return q011e._json_native(
        {
            "maximum_dense_vs_sparse_relative_action_error": max(dense_sparse_errors),
            "maximum_sparse_realification_action_error": max(sparse_realification_errors),
            "maximum_sparse_imaginary_leakage_relative_norm": max(sparse_imaginary_leakages),
            "candidate_records": candidate_records,
            "checks": checks,
            "passed": all(checks.values()),
        }
    )


def _invariance_audit(
    data: CoefficientData,
    retained: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    directions = _normalized_directions(
        INVARIANCE_SEED,
        INVARIANCE_DIRECTION_COUNT,
    )
    scaled = INVARIANCE_AMPLITUDE * directions
    sparse_method = lambda vector: _natural_action(data, vector)
    dense_defects = [data.model.invariance_defect(value, quadratic=True) for value in scaled]
    sparse_records = [_method_defect(data, sparse_method, value) for value in scaled]
    sparse_defects = [record[0] for record in sparse_records]
    sparse_relative_differences = [
        _relative_norm(sparse - dense, dense)
        for sparse, dense in zip(sparse_defects, dense_defects, strict=True)
    ]
    sparse_minimum_population = min(record[1]["minimum_population"] for record in sparse_records)
    sparse_maximum_conservation = max(
        record[1]["maximum_global_conservation_drift"] for record in sparse_records
    )
    sparse_maximum_imaginary = max(
        record[1]["maximum_imaginary_leakage_relative_norm"] for record in sparse_records
    )
    candidate_records: dict[str, Any] = {}
    for candidate_id in TT_CANDIDATE_IDS:
        method = _candidate_method(retained[candidate_id], candidate_id)
        observed_records = [_method_defect(data, method, value) for value in scaled]
        observed_defects = [record[0] for record in observed_records]
        relative_differences = [
            _relative_norm(observed - sparse, sparse)
            for observed, sparse in zip(
                observed_defects,
                sparse_defects,
                strict=True,
            )
        ]
        minimum_population = min(record[1]["minimum_population"] for record in observed_records)
        maximum_conservation = max(
            record[1]["maximum_global_conservation_drift"] for record in observed_records
        )
        maximum_imaginary = max(
            record[1]["maximum_imaginary_leakage_relative_norm"] for record in observed_records
        )
        passed = bool(
            max(relative_differences) <= MAXIMUM_INVARIANCE_DEFECT_PERTURBATION
            and minimum_population > 0.0
            and maximum_conservation <= MAXIMUM_CONSERVATION_DRIFT
            and np.all(np.isfinite(observed_defects))
        )
        candidate_records[candidate_id] = {
            "maximum_defect_vector_relative_difference_vs_sparse": max(relative_differences),
            "minimum_population": minimum_population,
            "maximum_global_conservation_drift": maximum_conservation,
            "maximum_imaginary_leakage_relative_norm": maximum_imaginary,
            "passed": passed,
        }
    prior_directions = [
        _normalized_directions(seed, count) for seed, count in PRIOR_DIRECTION_CAMPAIGNS
    ]
    duplicate_count = sum(
        int(np.array_equal(direction, prior))
        for direction in directions
        for campaign in prior_directions
        for prior in campaign
    )
    natural_passed = bool(
        max(sparse_relative_differences) <= MAXIMUM_INVARIANCE_DEFECT_PERTURBATION
        and sparse_minimum_population > 0.0
        and sparse_maximum_conservation <= MAXIMUM_CONSERVATION_DRIFT
        and np.all(np.isfinite(sparse_defects))
    )
    checks = {
        "invariance_direction_campaign_is_registered": (
            directions.shape == (INVARIANCE_DIRECTION_COUNT, SELECTED_DIMENSION)
            and duplicate_count == 0
        ),
        "natural_projected_chart_preserves_dense_defects": natural_passed,
        "all_tt_charts_preserve_natural_defects": all(
            record["passed"] for record in candidate_records.values()
        ),
    }
    return q011e._json_native(
        {
            "seed": INVARIANCE_SEED,
            "direction_count": INVARIANCE_DIRECTION_COUNT,
            "amplitude": INVARIANCE_AMPLITUDE,
            "direction_sha256": q011e.q011c._array_sha256(directions),
            "exact_duplicate_count_vs_prior": duplicate_count,
            "natural_maximum_defect_vector_relative_difference_vs_dense": max(
                sparse_relative_differences
            ),
            "natural_minimum_population": sparse_minimum_population,
            "natural_maximum_global_conservation_drift": (sparse_maximum_conservation),
            "natural_maximum_imaginary_leakage_relative_norm": (sparse_maximum_imaginary),
            "candidate_records": candidate_records,
            "checks": checks,
            "passed": all(checks.values()),
        }
    )


def _online_methods(
    data: CoefficientData,
    retained: dict[str, dict[str, Any]],
) -> dict[str, Callable[[ComplexArray], tuple[ComplexArray, ComplexArray]]]:
    return {
        SPARSE_METHOD_ID: lambda vector: _natural_action(data, vector),
        DENSE_METHOD_ID: lambda vector: _dense_action(data, vector),
        **{
            candidate_id: _candidate_method(retained[candidate_id], candidate_id)
            for candidate_id in TT_CANDIDATE_IDS
        },
    }


def _timed_action_block(
    method: Callable[[ComplexArray], tuple[ComplexArray, ComplexArray]],
    vectors: ComplexArray,
) -> tuple[int, float]:
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        checksum = 0.0
        started = perf_counter_ns()
        for vector in vectors:
            w_output, r_output = method(vector)
            checksum += float(np.hypot(np.linalg.norm(w_output), np.linalg.norm(r_output)))
        elapsed = perf_counter_ns() - started
    finally:
        if was_enabled:
            gc.enable()
    return elapsed, checksum


def _online_campaign(
    data: CoefficientData,
    vectors: ComplexArray,
    retained: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    methods = _online_methods(data, retained)
    for _ in range(ONLINE_WARMUP_BLOCKS):
        for method_id in METHOD_IDS:
            elapsed, _ = _timed_action_block(methods[method_id], vectors)
            if elapsed <= 0:
                raise RuntimeError("Q011g online warmup returned nonpositive time")

    durations: dict[str, list[float]] = {method_id: [] for method_id in METHOD_IDS}
    checksums: dict[str, list[float]] = {method_id: [] for method_id in METHOD_IDS}
    order_by_block: list[list[str]] = []
    method_ids = list(METHOD_IDS)
    for block in range(ONLINE_MEASURED_BLOCKS):
        offset = block % len(method_ids)
        order = method_ids[offset:] + method_ids[:offset]
        order_by_block.append(order)
        for method_id in order:
            elapsed, checksum = _timed_action_block(methods[method_id], vectors)
            durations[method_id].append(elapsed / ACTION_DIRECTION_COUNT)
            checksums[method_id].append(checksum)

    sparse_checksum = float(median(checksums[SPARSE_METHOD_ID]))
    records: dict[str, Any] = {}
    for method_id in METHOD_IDS:
        samples = durations[method_id]
        checksum_errors = [
            abs(value - sparse_checksum) / max(abs(sparse_checksum), np.finfo(float).tiny)
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
            "maximum_checksum_relative_error_vs_sparse": max(checksum_errors),
            "all_times_positive_and_finite": bool(
                all(value > 0.0 and math.isfinite(value) for value in samples)
            ),
        }
    return q011e._json_native(
        {
            "seed": ACTION_SEED,
            "direction_count": ACTION_DIRECTION_COUNT,
            "warmup_block_count": ONLINE_WARMUP_BLOCKS,
            "measured_block_count": ONLINE_MEASURED_BLOCKS,
            "order_by_block": order_by_block,
            "timer": "perf_counter_ns",
            "scope": "joint homogeneous quadratic W2/R2 action only",
            "method_records": records,
        }
    )


def _conservative_break_even(
    candidate_offline_maximum: float,
    candidate_online_maximum: float,
    sparse_offline_minimum: float,
    sparse_online_minimum: float,
) -> int | None:
    if candidate_online_maximum >= sparse_online_minimum:
        return None
    if candidate_offline_maximum <= sparse_offline_minimum:
        return 0
    numerator = candidate_offline_maximum - sparse_offline_minimum
    denominator = sparse_online_minimum - candidate_online_maximum
    return max(0, math.ceil(numerator / denominator))


def _selection_audit(
    fidelity: dict[str, Any],
    invariance: dict[str, Any],
    offline: dict[str, Any],
    online: dict[str, Any],
) -> dict[str, Any]:
    offline_records = offline["method_records"]
    online_records = online["method_records"]
    sparse_storage = offline_records[SPARSE_METHOD_ID]["storage"]
    sparse_offline = offline_records[SPARSE_METHOD_ID]
    sparse_online = online_records[SPARSE_METHOD_ID]
    records: dict[str, Any] = {}
    for candidate_id in TT_CANDIDATE_IDS:
        candidate_storage = offline_records[candidate_id]["storage"]
        storage_checks = {
            "core_stored_real_scalars_are_smaller": (
                candidate_storage["core_stored_real_scalar_count"]
                < sparse_storage["coefficient_stored_real_scalar_count"]
            ),
            "raw_array_payload_is_smaller": (
                candidate_storage["raw_array_payload_bytes"]
                < sparse_storage["raw_array_payload_bytes"]
            ),
            "in_memory_object_bytes_are_smaller": (
                candidate_storage["in_memory_object_bytes"]
                < sparse_storage["in_memory_object_bytes"]
            ),
            "uncompressed_npz_is_smaller": (
                candidate_storage["uncompressed_npz_serialized_bytes"]
                < sparse_storage["uncompressed_npz_serialized_bytes"]
            ),
        }
        storage_winner = all(storage_checks.values())
        candidate_online = online_records[candidate_id]
        candidate_offline = offline_records[candidate_id]
        robust_time_advantage = bool(
            candidate_online["maximum_nanoseconds_per_sample"]
            < sparse_online["minimum_nanoseconds_per_sample"]
        )
        break_even = _conservative_break_even(
            candidate_offline["maximum_nanoseconds"],
            candidate_online["maximum_nanoseconds_per_sample"],
            sparse_offline["minimum_nanoseconds"],
            sparse_online["minimum_nanoseconds_per_sample"],
        )
        fidelity_passed = fidelity["candidate_records"][candidate_id]["passed"]
        invariance_passed = invariance["candidate_records"][candidate_id]["passed"]
        joint_winner = bool(
            fidelity_passed
            and invariance_passed
            and storage_winner
            and robust_time_advantage
            and break_even is not None
        )
        records[candidate_id] = {
            "fidelity_passed": fidelity_passed,
            "invariance_residual_preservation_passed": invariance_passed,
            "storage_checks": storage_checks,
            "strict_storage_winner": storage_winner,
            "robust_online_time_advantage": robust_time_advantage,
            "conservative_break_even_vs_sparse_action_count": break_even,
            "median_online_ratio_vs_sparse": (
                candidate_online["median_nanoseconds_per_sample"]
                / sparse_online["median_nanoseconds_per_sample"]
            ),
            "joint_winner": joint_winner,
        }
    winners = [candidate_id for candidate_id, record in records.items() if record["joint_winner"]]
    winners.sort(
        key=lambda candidate_id: (
            records[candidate_id]["conservative_break_even_vs_sparse_action_count"],
            offline_records[candidate_id]["storage"]["raw_array_payload_bytes"],
            online_records[candidate_id]["maximum_nanoseconds_per_sample"],
            candidate_id,
        )
    )
    storage_winners = [
        candidate_id for candidate_id, record in records.items() if record["strict_storage_winner"]
    ]
    timing_winners = [
        candidate_id
        for candidate_id, record in records.items()
        if record["robust_online_time_advantage"]
    ]
    return q011e._json_native(
        {
            "storage_baseline_method_id": SPARSE_METHOD_ID,
            "natural_sparse_stored_real_scalars": sparse_storage[
                "coefficient_stored_real_scalar_count"
            ],
            "candidate_records": records,
            "storage_winner_ids": storage_winners,
            "robust_timing_winner_ids": timing_winners,
            "joint_winner_ids": winners,
            "joint_winner_count": len(winners),
            "selected_candidate_id": winners[0] if winners else None,
            "selection_order": [
                "conservative_break_even",
                "raw_array_payload_bytes",
                "online_maximum_nanoseconds_per_sample",
                "candidate_id",
            ],
            "natural_sparse_baseline_remains_mandatory": True,
            "ordered_dense_control_is_not_full_dense_lbm": True,
        }
    )


def _protocol_audit(
    offline: dict[str, Any],
    online: dict[str, Any],
) -> dict[str, Any]:
    offline_records = offline["method_records"]
    online_records = online["method_records"]
    checks = {
        "method_ids_and_order_are_registered": (
            tuple(offline_records) == METHOD_IDS and tuple(online_records) == METHOD_IDS
        ),
        "offline_block_counts_are_registered": all(
            len(record["nanoseconds_by_block"]) == OFFLINE_MEASURED_BLOCKS
            for record in offline_records.values()
        ),
        "online_block_counts_are_registered": all(
            len(record["nanoseconds_per_sample_by_block"]) == ONLINE_MEASURED_BLOCKS
            for record in online_records.values()
        ),
        "all_times_are_positive_and_finite": (
            all(record["all_times_positive_and_finite"] for record in offline_records.values())
            and all(record["all_times_positive_and_finite"] for record in online_records.values())
        ),
        "all_serialization_roundtrips_are_bitwise_equal": all(
            record["storage"]["serialization_roundtrip_bitwise_equal"]
            for record in offline_records.values()
        ),
        "all_checksum_errors_are_within_tolerance": all(
            record["maximum_checksum_relative_error_vs_sparse"] <= MAXIMUM_CHECKSUM_RELATIVE_ERROR
            for record in online_records.values()
        ),
        "offline_orders_are_complete_cyclic_permutations": (
            len(offline["order_by_block"]) == OFFLINE_MEASURED_BLOCKS
            and all(
                len(order) == len(METHOD_IDS) and set(order) == set(METHOD_IDS)
                for order in offline["order_by_block"]
            )
        ),
        "online_orders_are_complete_cyclic_permutations": (
            len(online["order_by_block"]) == ONLINE_MEASURED_BLOCKS
            and all(
                len(order) == len(METHOD_IDS) and set(order) == set(METHOD_IDS)
                for order in online["order_by_block"]
            )
        ),
    }
    return {"checks": checks, "passed": all(checks.values())}


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011e.q011c.OMEGA,
        "eta": q011e.q011c.ETA,
        "fixed_conservation_leaf": True,
        "selected_dimension": SELECTED_DIMENSION,
        "pair_count": PAIR_COUNT,
        "output_sector_order": list(OUTPUT_SECTOR_ORDER),
        "selected_block_order": list(SELECTED_BLOCK_ORDER),
        "expected_sector_pair_counts": {
            str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()
        },
        "tt_relative_tolerance": TT_RELATIVE_TOLERANCE,
        "tt_max_rank": None,
        "tt_candidate_ids": list(TT_CANDIDATE_IDS),
        "method_ids": list(METHOD_IDS),
        "action_seed": ACTION_SEED,
        "action_direction_count": ACTION_DIRECTION_COUNT,
        "invariance_seed": INVARIANCE_SEED,
        "invariance_direction_count": INVARIANCE_DIRECTION_COUNT,
        "invariance_amplitude": INVARIANCE_AMPLITUDE,
        "offline_warmup_blocks": OFFLINE_WARMUP_BLOCKS,
        "offline_measured_blocks": OFFLINE_MEASURED_BLOCKS,
        "online_warmup_blocks": ONLINE_WARMUP_BLOCKS,
        "online_measured_blocks": ONLINE_MEASURED_BLOCKS,
        "thresholds": {
            "maximum_projection_relative_loss": (MAXIMUM_PROJECTION_RELATIVE_LOSS),
            "maximum_sparse_dense_action_error": (MAXIMUM_SPARSE_DENSE_ACTION_ERROR),
            "maximum_tt_reconstruction_error": (MAXIMUM_TT_RECONSTRUCTION_ERROR),
            "maximum_tt_action_error": MAXIMUM_TT_ACTION_ERROR,
            "maximum_realification_action_error": (MAXIMUM_REALIFICATION_ACTION_ERROR),
            "maximum_invariance_defect_perturbation": (MAXIMUM_INVARIANCE_DEFECT_PERTURBATION),
            "minimum_population": 0.0,
            "maximum_conservation_drift": MAXIMUM_CONSERVATION_DRIFT,
            "maximum_checksum_relative_error": (MAXIMUM_CHECKSUM_RELATIVE_ERROR),
        },
        "natural_sparse_registered_counts": {
            "coefficient_complex_entry_count": 47_484,
            "coefficient_stored_real_scalar_count": 94_968,
            "raw_array_payload_bytes": 760_644,
        },
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "coefficient_digest_sha256": cycle["coefficient_digest_sha256"],
        "fidelity_digest_sha256": cycle["fidelity_digest_sha256"],
        "cost_digest_sha256": cycle["cost_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_forced_representation_audit() -> dict[str, Any]:
    registered_parameters = _registered_parameters()
    sealed_q011f1, q011f1_artifact = _sealed_q011f1_artifact_audit()
    data = _coefficient_data(q011f1_artifact)
    directions, _, direction_audit = _direction_audit()
    complex_directions = _complex_directions(data, directions)
    offline, retained = _offline_campaign(data)
    fidelity = _fidelity_audit(
        data,
        directions,
        complex_directions,
        retained,
    )
    invariance = _invariance_audit(data, retained)
    online = _online_campaign(data, complex_directions, retained)
    protocol = _protocol_audit(offline, online)
    selection = _selection_audit(
        fidelity,
        invariance,
        offline,
        online,
    )
    runner = _runner_source_metadata()

    input_sections = q011e._json_native(
        {
            "registered_parameters": registered_parameters,
            "sealed_q011f1_artifact_audit": sealed_q011f1,
        }
    )
    coefficient_sections = q011e._json_native(
        {
            "q011e_coefficient_reconstruction_audit": (data.reconstruction_audit),
            "natural_fourier_coefficient_audit": data.coefficient_audit,
        }
    )
    fidelity_sections = q011e._json_native(
        {
            "direction_audit": direction_audit,
            "fidelity_audit": fidelity,
            "invariance_residual_preservation_audit": invariance,
        }
    )
    cost_sections = q011e._json_native(
        {
            "offline_cost_campaign": offline,
            "online_cost_campaign": online,
            "protocol_audit": protocol,
            "selection_audit": selection,
        }
    )
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    coefficient_digest = q011e.q011c._canonical_json_sha256(coefficient_sections)
    fidelity_digest = q011e.q011c._canonical_json_sha256(fidelity_sections)
    cost_digest = q011e.q011c._canonical_json_sha256(cost_sections)
    strict_payload = {
        **input_sections,
        **coefficient_sections,
        **fidelity_sections,
        **cost_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(strict_payload) and _strict_json_serializable(strict_payload)
    )
    digest_reproduction = bool(
        input_digest == q011e.q011c._canonical_json_sha256(input_sections)
        and coefficient_digest == q011e.q011c._canonical_json_sha256(coefficient_sections)
        and fidelity_digest == q011e.q011c._canonical_json_sha256(fidelity_sections)
        and cost_digest == q011e.q011c._canonical_json_sha256(cost_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
    )
    validity_gates = {
        "q011f1_and_prior_outcomes_are_sealed": {
            "passed": sealed_q011f1["passed"],
            "threshold": (
                "Q011f1 artifact, runner, package source, five digests and "
                "accepted outcome reproduce while Q011f remains rejected"
            ),
            "value": sealed_q011f1["checks"],
        },
        "q011e_native_and_real_coefficients_reconstruct_once": {
            "passed": data.reconstruction_audit["passed"],
            "threshold": (
                "one fresh Q011e reconstruction reproduces native complex, "
                "coordinate-map and six real array hashes"
            ),
            "value": data.reconstruction_audit["checks"],
        },
        "natural_fourier_projection_and_storage_are_complete": {
            "passed": data.coefficient_audit["passed"],
            "threshold": (
                "300 pairs, registered sector counts, projection loss <=1e-12, "
                "94,968 stored real scalars, 760,644 raw bytes and serialization"
            ),
            "value": data.coefficient_audit["checks"],
        },
        "all_registered_tt_bundles_preserve_coefficients_and_defects": {
            "passed": bool(fidelity["passed"] and invariance["passed"]),
            "threshold": (
                "all six reversible uncapped TT-SVD bundles pass registered "
                "reconstruction, action, realification and invariance thresholds"
            ),
            "value": {
                "fidelity_checks": fidelity["checks"],
                "invariance_checks": invariance["checks"],
            },
        },
        "independent_directions_and_cost_protocol_are_complete": {
            "passed": bool(direction_audit["passed"] and protocol["passed"]),
            "threshold": (
                "held-out directions have no prior duplicates and registered "
                "offline/online blocks, checksums, subphase times and storage pass"
            ),
            "value": {
                "direction_checks": direction_audit["checks"],
                "protocol_checks": protocol["checks"],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digest_reproduction and runner_reproduces),
            "threshold": (
                "finite strict JSON, four section digests and newline-normalized "
                "runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digest_reproduction,
                "runner_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    storage_winner_exists = bool(selection["storage_winner_ids"])
    robust_joint_time_exists = any(
        selection["candidate_records"][candidate_id]["robust_online_time_advantage"]
        and selection["candidate_records"][candidate_id][
            "conservative_break_even_vs_sparse_action_count"
        ]
        is not None
        for candidate_id in selection["storage_winner_ids"]
    )
    joint_winner_exists = selection["joint_winner_count"] > 0
    hypothesis_gates = {
        "all_candidate_fidelity_and_residual_gates_pass": {
            "passed": bool(validity_passed and fidelity["passed"] and invariance["passed"]),
            "threshold": (
                "all six candidates preserve coefficient actions and registered "
                "one-step invariance defects"
            ),
            "value": {
                "fidelity_passed": fidelity["passed"],
                "invariance_passed": invariance["passed"],
            },
        },
        "at_least_one_candidate_strictly_beats_sparse_storage": {
            "passed": bool(validity_passed and storage_winner_exists),
            "threshold": (
                "one candidate is strictly smaller in core scalars, raw bytes, "
                "in-memory object bytes and uncompressed NPZ bytes"
            ),
            "value": selection["storage_winner_ids"],
        },
        "a_storage_winner_has_robust_time_advantage": {
            "passed": bool(validity_passed and robust_joint_time_exists),
            "threshold": (
                "the same storage winner has TT online maximum below sparse "
                "online minimum and a conservative finite break-even"
            ),
            "value": selection["candidate_records"],
        },
        "joint_winner_is_selected_by_registered_order": {
            "passed": bool(validity_passed and joint_winner_exists),
            "threshold": "at least one joint winner and one deterministic selected candidate",
            "value": {
                "joint_winner_ids": selection["joint_winner_ids"],
                "selected_candidate_id": selection["selected_candidate_id"],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011g forced representation audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "a registered TT-SVD bundle beats the natural Fourier-sparse forced-quadratic baseline"
        )
    else:
        outcome = "rejected"
        classification = (
            "registered TT-SVD bundles do not beat the natural Fourier-sparse "
            "forced-quadratic baseline"
        )

    cycle: dict[str, Any] = q011e._json_native(
        {
            "question": (
                "Does one registered uncapped TT-SVD W2/R2 bundle beat the "
                "mandatory natural Fourier-sparse baseline in fidelity, storage "
                "and robust finite-environment joint-action time?"
            ),
            **strict_payload,
            "input_digest_sha256": input_digest,
            "coefficient_digest_sha256": coefficient_digest,
            "fidelity_digest_sha256": fidelity_digest,
            "cost_digest_sha256": cost_digest,
            "validity_gates": validity_gates,
            "hypothesis_gates": hypothesis_gates,
            "study_validity": "passed" if validity_passed else "failed",
            "hypothesis_outcome": outcome,
            "scientific_classification": classification,
        }
    )
    result_digest = q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["decision_consequence"] = {
        "natural_fourier_sparse_remains_mandatory_baseline": True,
        "registered_tt_svd_bundle_is_selected": bool(validity_passed and hypotheses_passed),
        "selected_candidate_id": (
            selection["selected_candidate_id"] if validity_passed and hypotheses_passed else None
        ),
        "tt_cross_followup_is_authorized": bool(validity_passed and hypotheses_passed),
        "q011f1_accepted_outcome_changed": False,
        "q011f_rejected_outcome_changed": False,
        "q011e1_accepted_outcome_changed": False,
        "q011e_rejected_outcome_changed": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This finite audit covers the sealed 17x17 zero-mean-forced fixed-leaf "
        "quadratic W2/R2 coefficients, six uncapped TT-SVD tensorizations and "
        "the recorded CPU/NumPy/BLAS environment. It does not establish a result "
        "for TT generally, TT-cross, rank-capped rounding, GPU or parallel cost, "
        "full 64-step TT rollout, higher coefficients, other grids, forces or "
        "walls, D3Q27, SSM existence or uniqueness, normal attraction or a basin."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011f1_accepted_shadowing_reissue_changed": False,
        "q011f_rejected_shadowing_window_changed": False,
        "q011e1_accepted_residual_window_changed": False,
        "q011e_rejected_original_window_changed": False,
        "q011d_accepted_homological_family_changed": False,
        "q008c_unforced_tt_rejection_changed": False,
        "q010_unforced_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister an independent TT-cross and full-chart rollout gate for the "
        "selected Q011g bundle."
        if outcome == "accepted"
        else (
            "Retain the natural Fourier-sparse forced quadratic representation "
            "and do not start TT-cross for these sealed coefficients."
            if outcome == "rejected"
            else (
                "Localize the first failed sealing, coefficient, fidelity, "
                "invariance, timing or serialization validity gate."
            )
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011g cycle failed strict serialization or digest")
    return cycle


def run_q011g_study() -> dict[str, Any]:
    cycle = run_forced_representation_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "natural Fourier-sparse versus registered uncapped TT-SVD "
                "representation audit for sealed forced quadratic coefficients"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011e.q011c.OMEGA,
            "eta": q011e.q011c.ETA,
            "fixed_conservation_leaf": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "pair_count": PAIR_COUNT,
            "coefficient_families": ["W2", "R2"],
            "candidate_count": len(TT_CANDIDATE_IDS),
            "natural_fourier_sparse_is_mandatory": True,
            "claim": (
                "finite binary64 coefficient fidelity, storage and current-"
                "environment joint-action cost only"
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
    result = run_q011g_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
