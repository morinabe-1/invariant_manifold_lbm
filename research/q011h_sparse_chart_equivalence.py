"""Q011h natural Fourier-sparse 64-step chart equivalence audit."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

import research.q011g_forced_representation_audit as q011g
from ttim_lbm.d2q9 import global_conserved_quantities
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
IntegerArray = npt.NDArray[np.int64]

q011e = q011g.q011e
SIZE = q011g.SIZE
STATE_DIMENSION = q011g.STATE_DIMENSION
SELECTED_DIMENSION = q011g.SELECTED_DIMENSION
PAIR_COUNT = q011g.PAIR_COUNT
OUTPUT_SECTOR_ORDER = q011g.OUTPUT_SECTOR_ORDER
SELECTED_BLOCK_ORDER = q011g.SELECTED_BLOCK_ORDER
SELECTED_OFFSETS = q011g.SELECTED_OFFSETS

Q011G_ARTIFACT_SHA256 = "842ddbae2a28ccd2f11a112f23205cb049668b82691fdd180edc5ac20fecaa25"
Q011G_RUNNER_SHA256 = "84ed56dabd0b0f870f1c6b27c9907c9566439ff03affe5aacc61ba611f4678fe"
Q011G_INPUT_DIGEST = "0632be40fccc212f23a271fa00ed80696f9a146a1b107e513b3a47edb9870a20"
Q011G_COEFFICIENT_DIGEST = "fc9edec10ee22abfaa2b763be9f69c9d72bfc59543aa34faea6ab206c35ab264"
Q011G_FIDELITY_DIGEST = "30dabea285da9070e2ebc0b351afde4695deb275d5f96ee66de1b1ca0468fcad"
Q011G_COST_DIGEST = "222a42321f4ae814478cc65102afcbc8926754d8cb7c48ed8ca2952e350767a7"
Q011G_RESULT_DIGEST = "e0874eabe2c5b924d0b5d7b56533cd695406166d4370b493a0dabdc0b22dbb2a"
SEALED_PACKAGE_SOURCE_SHA256 = q011g.SEALED_PACKAGE_SOURCE_SHA256

PAIR_INDICES_SHA256 = "a8917518620a67b9a2e3cbc2bddde81d0e4cb72033265e6a0c863cf0bdc02327"
OUTPUT_SECTORS_SHA256 = "c47ee20550188307589755188d2d856e763e466430acadeb0e3342bd93db3114"
W_FIBERS_SHA256 = "3b1e553bee7a9231087639fdd8d72524eae93347175a393bb3d48d207f144d66"
R_FIBER_SHA256 = {
    0: "6689974b4f081a51a347930e5a74128b532a0727b27bd7f6de7a4b9348a89c40",
    1: "7b49bd25f1eff1c2347e3493797113a2d3023417d9c4e970528562b5c4f275b6",
    16: "0c66ebad5cc3a86048a8c6caeb38da081700cce37cfeea9d17380d395bec0678",
}
PROJECTED_W_TENSOR_SHA256 = "a0b14a224a6f4d5921c4e21894821018d1df6badca8dd6b5d21d571756515ddc"
PROJECTED_R_TENSOR_SHA256 = "b450cba9d58d0853bed95acaa9b4f2a69659e5c24b943708c0700d11c8962ee9"

DIRECTION_SEED = 20260906
DIRECTION_COUNT = 24
DIRECTION_SHA256 = "25fec4f35db569404d83f20f45bb510c226679999e1fa8bc21aa4e96d22926c8"
AMPLITUDES = (4.0e-4, 9.6e-4, 2.4e-3)
AMPLITUDE_SHA256 = "ee39c1d89f58484222107e494e8e2b87525544708f7c0067e18268ed9fb5b8a5"
MAXIMUM_STEP = 64
CHECKPOINTS = (0, 1, 2, 4, 8, 16, 32, 64)
TRAJECTORY_COUNT = DIRECTION_COUNT * len(AMPLITUDES)
STATE_RECORD_COUNT = TRAJECTORY_COUNT * (MAXIMUM_STEP + 1)
UPDATE_COUNT_PER_IMPLEMENTATION = TRAJECTORY_COUNT * MAXIMUM_STEP
ACTION_COMPARISON_COUNT = 2 * STATE_RECORD_COUNT
CHECKPOINT_COUNT_PER_IMPLEMENTATION = TRAJECTORY_COUNT * len(CHECKPOINTS)

MAXIMUM_ACTION_RELATIVE_ERROR = 1.0e-11
MAXIMUM_IMAGINARY_LEAKAGE = 1.0e-11
MAXIMUM_COORDINATE_SCALED_ERROR = 1.0e-11
MAXIMUM_STATE_SCALED_ERROR = 1.0e-11
MAXIMUM_DEFECT_SCALED_ERROR = 1.0e-10
MAXIMUM_DEFECT_NORM_SCALED_DIFFERENCE = 1.0e-10
MAXIMUM_CONSERVATION_DRIFT = 1.0e-10

PRIOR_DIRECTION_CAMPAIGNS = (
    *q011g.PRIOR_DIRECTION_CAMPAIGNS,
    (q011g.ACTION_SEED, q011g.ACTION_DIRECTION_COUNT),
    (q011g.INVARIANCE_SEED, q011g.INVARIANCE_DIRECTION_COUNT),
)


@dataclass(frozen=True)
class SparseRuntimeData:
    """Natural representation with no ordered-dense quadratic coefficients."""

    base: Array
    tangent: Array
    reduced_linear: Array
    coordinate_map: ComplexArray
    pairs: IntegerArray
    sectors: IntegerArray
    w_fibers: ComplexArray
    r_fibers: dict[int, ComplexArray]


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011e.q011c.OMEGA,
        "eta": q011e.q011c.ETA,
        "fixed_conservation_leaf": True,
        "zero_wave_center_coordinates_included": False,
        "selected_dimension": SELECTED_DIMENSION,
        "pair_count": PAIR_COUNT,
        "direction_seed": DIRECTION_SEED,
        "direction_count": DIRECTION_COUNT,
        "direction_sha256": DIRECTION_SHA256,
        "amplitudes": list(AMPLITUDES),
        "amplitude_sha256": AMPLITUDE_SHA256,
        "maximum_step": MAXIMUM_STEP,
        "checkpoints": list(CHECKPOINTS),
        "registered_counts": {
            "trajectory_count": TRAJECTORY_COUNT,
            "state_record_count": STATE_RECORD_COUNT,
            "reduced_update_count_per_implementation": UPDATE_COUNT_PER_IMPLEMENTATION,
            "common_input_action_comparison_count": ACTION_COMPARISON_COUNT,
            "checkpoint_defect_count_per_implementation": (CHECKPOINT_COUNT_PER_IMPLEMENTATION),
        },
        "thresholds": {
            "maximum_common_input_joint_action_relative_error": (MAXIMUM_ACTION_RELATIVE_ERROR),
            "maximum_sparse_realification_imaginary_leakage": (MAXIMUM_IMAGINARY_LEAKAGE),
            "maximum_coordinate_error_over_initial_coordinate_norm": (
                MAXIMUM_COORDINATE_SCALED_ERROR
            ),
            "maximum_state_error_over_initial_tangent_perturbation_norm": (
                MAXIMUM_STATE_SCALED_ERROR
            ),
            "maximum_defect_vector_error_over_initial_coordinate_norm": (
                MAXIMUM_DEFECT_SCALED_ERROR
            ),
            "maximum_defect_norm_difference_over_initial_coordinate_norm": (
                MAXIMUM_DEFECT_NORM_SCALED_DIFFERENCE
            ),
            "minimum_population": 0.0,
            "maximum_global_conservation_drift": MAXIMUM_CONSERVATION_DRIFT,
        },
        "scope_controls": {
            "q011f_or_q011f1_shadowing_is_regraded": False,
            "shadowing_slopes_are_fitted": False,
            "full_state_orbit_is_propagated_for_64_steps": False,
            "one_step_defects_are_evaluated_at_checkpoints": True,
            "dense_and_sparse_reduced_paths_are_updated_independently": True,
        },
    }


def _sealed_q011g_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011g.__file__).resolve().parent
        / "artifacts"
        / "q011g_forced_representation_audit.json"
    )
    runner_path = Path(q011g.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    observed_digests = (
        cycle["input_digest_sha256"],
        cycle["coefficient_digest_sha256"],
        cycle["fidelity_digest_sha256"],
        cycle["cost_digest_sha256"],
        cycle["result_digest_sha256"],
    )
    registered_digests = (
        Q011G_INPUT_DIGEST,
        Q011G_COEFFICIENT_DIGEST,
        Q011G_FIDELITY_DIGEST,
        Q011G_COST_DIGEST,
        Q011G_RESULT_DIGEST,
    )
    selection = cycle["selection_audit"]
    decision = cycle["decision_consequence"]
    q011f1_audit = cycle["sealed_q011f1_artifact_audit"]
    checks = {
        "q011g_artifact_sha256_matches": _file_sha256(artifact_path) == Q011G_ARTIFACT_SHA256,
        "q011g_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011G_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011G_RUNNER_SHA256
        ),
        "q011g_package_source_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "q011g_five_digests_match": observed_digests == registered_digests,
        "q011g_valid_rejected_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "rejected"
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and sum(gate["passed"] for gate in cycle["hypothesis_gates"].values()) == 1
        ),
        "q011g_selection_and_tt_cross_decision_reproduce": (
            selection["storage_winner_ids"] == []
            and selection["joint_winner_ids"] == []
            and selection["joint_winner_count"] == 0
            and selection["selected_candidate_id"] is None
            and not decision["registered_tt_svd_bundle_is_selected"]
            and not decision["tt_cross_followup_is_authorized"]
            and decision["natural_fourier_sparse_remains_mandatory_baseline"]
        ),
        "q011f1_and_q011f_outcomes_remain_sealed": (
            q011f1_audit["passed"]
            and q011f1_audit["artifact"]["hypothesis_outcome"] == "accepted"
            and q011f1_audit["preserved_q011f_artifact"]["hypothesis_outcome"] == "rejected"
            and not decision["q011f1_accepted_outcome_changed"]
            and not decision["q011f_rejected_outcome_changed"]
        ),
        "q011g_artifact_is_strict_finite_json": bool(
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
            "coefficient_digest_sha256": observed_digests[1],
            "fidelity_digest_sha256": observed_digests[2],
            "cost_digest_sha256": observed_digests[3],
            "result_digest_sha256": observed_digests[4],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        },
        "preserved_q011f1_outcome": q011f1_audit["artifact"],
        "preserved_q011f_outcome": q011f1_audit["preserved_q011f_artifact"],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return q011e._json_native(audit), artifact


def _coefficient_reconstruction_audit(
    q011g_artifact: dict[str, Any],
) -> tuple[q011g.CoefficientData, dict[str, Any]]:
    q011f1_audit, q011f1_artifact = q011g._sealed_q011f1_artifact_audit()
    data = q011g._coefficient_data(q011f1_artifact)
    stored_cycle = q011g_artifact["cycle"]
    observed = data.coefficient_audit
    stored = stored_cycle["natural_fourier_coefficient_audit"]
    storage = observed["natural_storage"]
    observed_r_hashes = {
        int(sector): digest for sector, digest in observed["r_fiber_sha256"].items()
    }
    checks = {
        "q011f1_seal_reproduces_q011g_input": (
            q011f1_audit == stored_cycle["sealed_q011f1_artifact_audit"]
        ),
        "q011e_reconstruction_reproduces_q011g": (
            data.reconstruction_audit == stored_cycle["q011e_coefficient_reconstruction_audit"]
            and data.reconstruction_audit["passed"]
        ),
        "pair_sector_and_fiber_hashes_reproduce": (
            observed["pair_indices_sha256"] == PAIR_INDICES_SHA256
            and observed["output_sectors_sha256"] == OUTPUT_SECTORS_SHA256
            and observed["w_fibers_sha256"] == W_FIBERS_SHA256
            and observed_r_hashes == R_FIBER_SHA256
        ),
        "projected_dense_hashes_reproduce": (
            observed["projected_w_tensor_sha256"] == PROJECTED_W_TENSOR_SHA256
            and observed["projected_r_tensor_sha256"] == PROJECTED_R_TENSOR_SHA256
        ),
        "registered_pair_sector_shapes_reproduce": (
            observed["pair_count"] == 300
            and observed["sector_pair_counts"] == {"0": 102, "1": 54, "16": 54, "2": 45, "15": 45}
            and observed["w_fibers_shape"] == [300, 17, 9]
            and observed["r_fiber_shapes"] == {"0": [102, 6], "1": [54, 9], "16": [54, 9]}
        ),
        "registered_storage_and_projection_reproduce": (
            storage["coefficient_stored_real_scalar_count"] == 94_968
            and storage["raw_array_payload_bytes"] == 760_644
            and storage["serialization_roundtrip_bitwise_equal"]
            and observed["w_projection_relative_loss"] <= 1.0e-12
            and observed["r_projection_relative_loss"] <= 1.0e-12
        ),
        "fresh_coefficient_audit_matches_sealed_deterministic_fields": (
            observed["pair_indices_sha256"] == stored["pair_indices_sha256"]
            and observed["output_sectors_sha256"] == stored["output_sectors_sha256"]
            and observed["w_fibers_sha256"] == stored["w_fibers_sha256"]
            and observed["r_fiber_sha256"] == stored["r_fiber_sha256"]
            and observed["projected_w_tensor_sha256"] == stored["projected_w_tensor_sha256"]
            and observed["projected_r_tensor_sha256"] == stored["projected_r_tensor_sha256"]
            and storage["coefficient_stored_real_scalar_count"]
            == stored["natural_storage"]["coefficient_stored_real_scalar_count"]
            and storage["raw_array_payload_bytes"]
            == stored["natural_storage"]["raw_array_payload_bytes"]
        ),
        "fresh_coefficient_audit_passes": (observed["passed"] and all(observed["checks"].values())),
    }
    audit = {
        "q011f1_input_audit": q011f1_audit,
        "q011e_reconstruction_audit": data.reconstruction_audit,
        "natural_coefficient_audit": observed,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return data, q011e._json_native(audit)


def _readonly_copy(value: npt.ArrayLike, dtype: npt.DTypeLike) -> npt.NDArray[Any]:
    result = np.array(value, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _sparse_runtime_data(
    data: q011g.CoefficientData,
) -> tuple[SparseRuntimeData, dict[str, Any]]:
    runtime = SparseRuntimeData(
        base=_readonly_copy(data.model.base, np.float64),
        tangent=_readonly_copy(data.model.tangent, np.float64),
        reduced_linear=_readonly_copy(data.model.reduced_linear, np.float64),
        coordinate_map=_readonly_copy(data.coordinate_map, np.complex128),
        pairs=_readonly_copy(data.pairs, np.int64),
        sectors=_readonly_copy(data.sectors, np.int64),
        w_fibers=_readonly_copy(data.w_fibers, np.complex128),
        r_fibers={
            sector: _readonly_copy(data.r_fibers[sector], np.complex128)
            for sector in SELECTED_BLOCK_ORDER
        },
    )
    field_names = list(SparseRuntimeData.__dataclass_fields__)
    forbidden_fields = {
        "hessian",
        "reduced_hessian",
        "w_tensor",
        "r_tensor",
        "native_chart_hessian",
        "native_reduced_hessian",
    }
    sparse_code_names = set(_sparse_complex_action.__code__.co_names) | set(
        _sparse_real_action.__code__.co_names
    )
    forbidden_code_names = {
        "_dense_real_action",
        "_dense_action",
        "hessian",
        "reduced_hessian",
        "w_tensor",
        "r_tensor",
    }
    hashes = {
        "pair_indices_sha256": q011e.q011c._array_sha256(runtime.pairs),
        "output_sectors_sha256": q011e.q011c._array_sha256(runtime.sectors),
        "w_fibers_sha256": q011e.q011c._array_sha256(runtime.w_fibers),
        "r_fiber_sha256": {
            str(sector): q011e.q011c._array_sha256(runtime.r_fibers[sector])
            for sector in SELECTED_BLOCK_ORDER
        },
    }
    checks = {
        "sparse_runtime_has_only_registered_fields": field_names
        == [
            "base",
            "tangent",
            "reduced_linear",
            "coordinate_map",
            "pairs",
            "sectors",
            "w_fibers",
            "r_fibers",
        ],
        "sparse_runtime_has_no_dense_quadratic_fields": not (forbidden_fields & set(field_names)),
        "sparse_action_code_has_no_dense_quadratic_references": not (
            forbidden_code_names & sparse_code_names
        ),
        "sparse_runtime_arrays_are_read_only": all(
            not value.flags.writeable
            for value in (
                runtime.base,
                runtime.tangent,
                runtime.reduced_linear,
                runtime.coordinate_map,
                runtime.pairs,
                runtime.sectors,
                runtime.w_fibers,
                *runtime.r_fibers.values(),
            )
        ),
        "sparse_runtime_hashes_reproduce": (
            hashes["pair_indices_sha256"] == PAIR_INDICES_SHA256
            and hashes["output_sectors_sha256"] == OUTPUT_SECTORS_SHA256
            and hashes["w_fibers_sha256"] == W_FIBERS_SHA256
            and hashes["r_fiber_sha256"]
            == {str(sector): digest for sector, digest in R_FIBER_SHA256.items()}
        ),
    }
    audit = {
        "runtime_type": SparseRuntimeData.__name__,
        "field_names": field_names,
        "forbidden_dense_field_names": sorted(forbidden_fields),
        "sparse_action_code_names": sorted(sparse_code_names),
        "forbidden_dense_code_names": sorted(forbidden_code_names),
        "array_hashes": hashes,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return runtime, q011e._json_native(audit)


def _direction_audit() -> tuple[Array, Array, dict[str, Any]]:
    directions = q011g._normalized_directions(DIRECTION_SEED, DIRECTION_COUNT)
    amplitudes = np.asarray(AMPLITUDES, dtype=np.float64)
    prior_records: list[dict[str, Any]] = []
    exact_duplicate_count = 0
    for seed, count in PRIOR_DIRECTION_CAMPAIGNS:
        prior = q011g._normalized_directions(seed, count)
        duplicates = sum(
            np.array_equal(direction, prior_direction)
            for direction in directions
            for prior_direction in prior
        )
        exact_duplicate_count += duplicates
        prior_records.append(
            {
                "seed": seed,
                "direction_count": count,
                "direction_sha256": q011e.q011c._array_sha256(prior),
                "exact_duplicate_count": duplicates,
            }
        )
    prior_amplitudes = np.asarray(
        (*q011g.q011f1.MERGED_AMPLITUDES, q011g.INVARIANCE_AMPLITUDE),
        dtype=np.float64,
    )
    amplitude_duplicate_count = int(
        sum(value == prior_value for value in amplitudes for prior_value in prior_amplitudes)
    )
    direction_hash = q011e.q011c._array_sha256(directions)
    amplitude_hash = q011e.q011c._array_sha256(amplitudes)
    norms = np.linalg.norm(directions, axis=1)
    checks = {
        "direction_seed_count_and_hash_match": (
            directions.shape == (DIRECTION_COUNT, SELECTED_DIMENSION)
            and direction_hash == DIRECTION_SHA256
        ),
        "directions_are_finite_unique_and_normalized": (
            np.all(np.isfinite(directions))
            and np.unique(directions, axis=0).shape[0] == DIRECTION_COUNT
            and float(np.max(np.abs(norms - 1.0))) <= 1.0e-14
        ),
        "prior_direction_exact_duplicate_count_is_zero": exact_duplicate_count == 0,
        "amplitudes_are_registered_finite_positive_and_unique": (
            amplitudes.shape == (3,)
            and amplitude_hash == AMPLITUDE_SHA256
            and np.all(np.isfinite(amplitudes))
            and np.all(amplitudes > 0.0)
            and np.unique(amplitudes).size == amplitudes.size
        ),
        "registered_amplitudes_are_held_out": amplitude_duplicate_count == 0,
    }
    audit = {
        "seed": DIRECTION_SEED,
        "direction_count": DIRECTION_COUNT,
        "direction_sha256": direction_hash,
        "maximum_direction_norm_deviation": float(np.max(np.abs(norms - 1.0))),
        "prior_campaigns": prior_records,
        "prior_direction_exact_duplicate_count": exact_duplicate_count,
        "amplitudes": amplitudes.tolist(),
        "amplitude_sha256": amplitude_hash,
        "prior_amplitudes": prior_amplitudes.tolist(),
        "prior_amplitude_exact_duplicate_count": amplitude_duplicate_count,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return directions, amplitudes, q011e._json_native(audit)


def _dense_real_action(
    data: q011g.CoefficientData,
    coordinates: npt.ArrayLike,
) -> tuple[Array, Array]:
    value = np.asarray(coordinates, dtype=np.float64)
    w_action = 0.5 * np.einsum(
        "nij,i,j->n",
        data.model.hessian,
        value,
        value,
        optimize=True,
    )
    r_action = 0.5 * np.einsum(
        "rij,i,j->r",
        data.model.reduced_hessian,
        value,
        value,
        optimize=True,
    )
    return np.asarray(w_action, dtype=np.float64), np.asarray(r_action, dtype=np.float64)


def _sparse_complex_action(
    runtime: SparseRuntimeData,
    coordinates: npt.ArrayLike,
) -> tuple[ComplexArray, ComplexArray]:
    value = np.asarray(coordinates, dtype=np.complex128)
    products = value[runtime.pairs[:, 0]] * value[runtime.pairs[:, 1]]
    w_output = np.zeros((SIZE, SIZE, 9), dtype=np.complex128)
    r_output = np.zeros(SELECTED_DIMENSION, dtype=np.complex128)
    for sector in OUTPUT_SECTOR_ORDER:
        mask = runtime.sectors == sector
        w_output[sector] = np.einsum(
            "p,pyq->yq",
            products[mask],
            runtime.w_fibers[mask],
            optimize=True,
        )
    for sector in SELECTED_BLOCK_ORDER:
        mask = runtime.sectors == sector
        r_output[SELECTED_OFFSETS[sector]] = np.einsum(
            "p,pr->r",
            products[mask],
            runtime.r_fibers[sector],
            optimize=True,
        )
    return w_output, r_output


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).tiny)
    )


def _sparse_real_action(
    runtime: SparseRuntimeData,
    coordinates: npt.ArrayLike,
) -> tuple[Array, Array, float]:
    real_value = np.asarray(coordinates, dtype=np.float64)
    complex_value = runtime.coordinate_map @ real_value
    w_fourier, r_complex = _sparse_complex_action(runtime, complex_value)
    w_physical = np.fft.ifft(w_fourier.transpose(1, 0, 2), axis=1) * np.sqrt(SIZE)
    r_real = runtime.coordinate_map.conj().T @ r_complex
    imaginary_leakage = max(
        _relative_norm(w_physical.imag, w_physical.real),
        _relative_norm(r_real.imag, r_real.real),
    )
    return (
        np.asarray(w_physical.real.ravel(), dtype=np.float64),
        np.asarray(r_real.real, dtype=np.float64),
        imaginary_leakage,
    )


def _joint_relative_error(
    observed: tuple[npt.ArrayLike, npt.ArrayLike],
    reference: tuple[npt.ArrayLike, npt.ArrayLike],
) -> float:
    return q011g._joint_relative_error(observed, reference)


def _lift(
    base: Array,
    tangent: Array,
    coordinates: Array,
    w_action: Array,
) -> Array:
    return np.asarray(base + tangent @ coordinates + w_action, dtype=np.float64)


def _next_coordinate(linear: Array, coordinates: Array, r_action: Array) -> Array:
    return np.asarray(linear @ coordinates + r_action, dtype=np.float64)


def _state_conservation_drift(state: Array, base_conserved: Array) -> float:
    return float(
        np.linalg.norm(global_conserved_quantities(state.reshape(SIZE, SIZE, 9)) - base_conserved)
    )


def _trajectory_campaign(
    data: q011g.CoefficientData,
    runtime: SparseRuntimeData,
    directions: Array,
    amplitudes: Array,
) -> dict[str, Any]:
    base_conserved = global_conserved_quantities(runtime.base.reshape(SIZE, SIZE, 9))
    checkpoint_set = set(CHECKPOINTS)
    state_metric_rows: list[list[float]] = []
    checkpoint_metric_rows: list[list[float]] = []
    trajectory_records: list[dict[str, Any]] = []
    action_comparison_count = 0
    dense_update_count = 0
    sparse_update_count = 0
    all_arrays_finite = True
    global_minimum_population = float("inf")
    global_maximum_conservation = 0.0
    global_maximum_action_error = 0.0
    global_maximum_imaginary = 0.0
    global_maximum_coordinate_error = 0.0
    global_maximum_state_error = 0.0
    global_maximum_defect_error = 0.0
    global_maximum_defect_norm_difference = 0.0

    for direction_index, direction in enumerate(directions):
        for amplitude_index, amplitude in enumerate(amplitudes):
            initial_coordinate = np.asarray(amplitude * direction, dtype=np.float64)
            initial_coordinate_norm = float(np.linalg.norm(initial_coordinate))
            initial_tangent_norm = float(np.linalg.norm(runtime.tangent @ initial_coordinate))
            dense_coordinate = initial_coordinate.copy()
            sparse_coordinate = initial_coordinate.copy()
            trajectory_state_rows: list[list[float]] = []
            trajectory_checkpoint_rows: list[list[float]] = []
            checkpoint_records: list[dict[str, Any]] = []
            trajectory_minimum_population = float("inf")
            trajectory_maximum_conservation = 0.0
            trajectory_maximum_action_error = 0.0
            trajectory_maximum_imaginary = 0.0
            trajectory_maximum_coordinate_error = 0.0
            trajectory_maximum_state_error = 0.0
            trajectory_maximum_defect_error = 0.0
            trajectory_maximum_defect_norm_difference = 0.0

            for step in range(MAXIMUM_STEP + 1):
                dense_on_dense = _dense_real_action(data, dense_coordinate)
                sparse_on_dense = _sparse_real_action(runtime, dense_coordinate)
                dense_on_sparse = _dense_real_action(data, sparse_coordinate)
                sparse_on_sparse = _sparse_real_action(runtime, sparse_coordinate)
                action_error_dense_input = _joint_relative_error(
                    sparse_on_dense[:2], dense_on_dense
                )
                action_error_sparse_input = _joint_relative_error(
                    sparse_on_sparse[:2], dense_on_sparse
                )
                action_comparison_count += 2
                maximum_step_action_error = max(
                    action_error_dense_input,
                    action_error_sparse_input,
                )
                maximum_step_imaginary = max(sparse_on_dense[2], sparse_on_sparse[2])

                dense_state = _lift(
                    runtime.base,
                    runtime.tangent,
                    dense_coordinate,
                    dense_on_dense[0],
                )
                sparse_state = _lift(
                    runtime.base,
                    runtime.tangent,
                    sparse_coordinate,
                    sparse_on_sparse[0],
                )
                coordinate_scaled_error = float(
                    np.linalg.norm(sparse_coordinate - dense_coordinate) / initial_coordinate_norm
                )
                state_scaled_error = float(
                    np.linalg.norm(sparse_state - dense_state) / initial_tangent_norm
                )
                dense_conservation = _state_conservation_drift(dense_state, base_conserved)
                sparse_conservation = _state_conservation_drift(sparse_state, base_conserved)
                step_minimum_population = min(
                    float(np.min(dense_state)),
                    float(np.min(sparse_state)),
                )
                step_maximum_conservation = max(dense_conservation, sparse_conservation)
                row = [
                    float(direction_index),
                    float(amplitude_index),
                    float(step),
                    float(np.linalg.norm(dense_coordinate)),
                    float(np.linalg.norm(sparse_coordinate)),
                    coordinate_scaled_error,
                    float(np.linalg.norm(dense_state - runtime.base)),
                    float(np.linalg.norm(sparse_state - runtime.base)),
                    state_scaled_error,
                    action_error_dense_input,
                    action_error_sparse_input,
                    sparse_on_dense[2],
                    sparse_on_sparse[2],
                    step_minimum_population,
                    step_maximum_conservation,
                ]
                state_metric_rows.append(row)
                trajectory_state_rows.append(row)

                next_dense_coordinate = _next_coordinate(
                    runtime.reduced_linear,
                    dense_coordinate,
                    dense_on_dense[1],
                )
                next_sparse_coordinate = _next_coordinate(
                    runtime.reduced_linear,
                    sparse_coordinate,
                    sparse_on_sparse[1],
                )

                if step in checkpoint_set:
                    next_dense_action = _dense_real_action(data, next_dense_coordinate)
                    next_sparse_action = _sparse_real_action(runtime, next_sparse_coordinate)
                    dense_next_lift = _lift(
                        runtime.base,
                        runtime.tangent,
                        next_dense_coordinate,
                        next_dense_action[0],
                    )
                    sparse_next_lift = _lift(
                        runtime.base,
                        runtime.tangent,
                        next_sparse_coordinate,
                        next_sparse_action[0],
                    )
                    dense_full_next = data.model.full_map(dense_state)
                    sparse_full_next = data.model.full_map(sparse_state)
                    dense_defect = np.asarray(
                        dense_full_next - dense_next_lift,
                        dtype=np.float64,
                    )
                    sparse_defect = np.asarray(
                        sparse_full_next - sparse_next_lift,
                        dtype=np.float64,
                    )
                    defect_scaled_error = float(
                        np.linalg.norm(sparse_defect - dense_defect) / initial_coordinate_norm
                    )
                    defect_norm_scaled_difference = float(
                        abs(np.linalg.norm(sparse_defect) - np.linalg.norm(dense_defect))
                        / initial_coordinate_norm
                    )
                    checkpoint_minimum_population = min(
                        step_minimum_population,
                        float(np.min(dense_full_next)),
                        float(np.min(sparse_full_next)),
                        float(np.min(dense_next_lift)),
                        float(np.min(sparse_next_lift)),
                    )
                    checkpoint_maximum_conservation = max(
                        step_maximum_conservation,
                        _state_conservation_drift(dense_full_next, base_conserved),
                        _state_conservation_drift(sparse_full_next, base_conserved),
                        _state_conservation_drift(dense_next_lift, base_conserved),
                        _state_conservation_drift(sparse_next_lift, base_conserved),
                    )
                    maximum_step_imaginary = max(
                        maximum_step_imaginary,
                        next_sparse_action[2],
                    )
                    checkpoint_row = [
                        float(direction_index),
                        float(amplitude_index),
                        float(step),
                        float(np.linalg.norm(dense_defect)),
                        float(np.linalg.norm(sparse_defect)),
                        defect_scaled_error,
                        defect_norm_scaled_difference,
                        checkpoint_minimum_population,
                        checkpoint_maximum_conservation,
                        next_sparse_action[2],
                    ]
                    checkpoint_metric_rows.append(checkpoint_row)
                    trajectory_checkpoint_rows.append(checkpoint_row)
                    checkpoint_state_array = np.concatenate(
                        (
                            dense_coordinate,
                            sparse_coordinate,
                            next_dense_coordinate,
                            next_sparse_coordinate,
                            dense_state,
                            sparse_state,
                            dense_full_next,
                            sparse_full_next,
                            dense_next_lift,
                            sparse_next_lift,
                            dense_defect,
                            sparse_defect,
                        )
                    )
                    checkpoint_records.append(
                        {
                            "step": step,
                            "dense_defect_norm": float(np.linalg.norm(dense_defect)),
                            "sparse_defect_norm": float(np.linalg.norm(sparse_defect)),
                            "defect_vector_error_over_initial_coordinate_norm": (
                                defect_scaled_error
                            ),
                            "defect_norm_difference_over_initial_coordinate_norm": (
                                defect_norm_scaled_difference
                            ),
                            "minimum_population": checkpoint_minimum_population,
                            "maximum_global_conservation_drift": (checkpoint_maximum_conservation),
                            "state_bundle_sha256": q011e.q011c._array_sha256(
                                checkpoint_state_array
                            ),
                        }
                    )
                    trajectory_maximum_defect_error = max(
                        trajectory_maximum_defect_error,
                        defect_scaled_error,
                    )
                    trajectory_maximum_defect_norm_difference = max(
                        trajectory_maximum_defect_norm_difference,
                        defect_norm_scaled_difference,
                    )
                    step_minimum_population = checkpoint_minimum_population
                    step_maximum_conservation = checkpoint_maximum_conservation
                    all_arrays_finite = bool(
                        all_arrays_finite
                        and all(
                            np.all(np.isfinite(value))
                            for value in (
                                next_dense_coordinate,
                                next_sparse_coordinate,
                                dense_full_next,
                                sparse_full_next,
                                dense_next_lift,
                                sparse_next_lift,
                                dense_defect,
                                sparse_defect,
                            )
                        )
                    )

                trajectory_minimum_population = min(
                    trajectory_minimum_population,
                    step_minimum_population,
                )
                trajectory_maximum_conservation = max(
                    trajectory_maximum_conservation,
                    step_maximum_conservation,
                )
                trajectory_maximum_action_error = max(
                    trajectory_maximum_action_error,
                    maximum_step_action_error,
                )
                trajectory_maximum_imaginary = max(
                    trajectory_maximum_imaginary,
                    maximum_step_imaginary,
                )
                trajectory_maximum_coordinate_error = max(
                    trajectory_maximum_coordinate_error,
                    coordinate_scaled_error,
                )
                trajectory_maximum_state_error = max(
                    trajectory_maximum_state_error,
                    state_scaled_error,
                )
                all_arrays_finite = bool(
                    all_arrays_finite
                    and all(
                        np.all(np.isfinite(value))
                        for value in (
                            dense_coordinate,
                            sparse_coordinate,
                            dense_on_dense[0],
                            dense_on_dense[1],
                            sparse_on_dense[0],
                            sparse_on_dense[1],
                            dense_on_sparse[0],
                            dense_on_sparse[1],
                            sparse_on_sparse[0],
                            sparse_on_sparse[1],
                            dense_state,
                            sparse_state,
                        )
                    )
                )

                if step < MAXIMUM_STEP:
                    dense_coordinate = next_dense_coordinate
                    sparse_coordinate = next_sparse_coordinate
                    dense_update_count += 1
                    sparse_update_count += 1

            state_rows_array = np.asarray(trajectory_state_rows, dtype=np.float64)
            checkpoint_rows_array = np.asarray(
                trajectory_checkpoint_rows,
                dtype=np.float64,
            )
            trajectory_records.append(
                {
                    "direction_index": direction_index,
                    "amplitude_index": amplitude_index,
                    "amplitude": float(amplitude),
                    "initial_coordinate_sha256": q011e.q011c._array_sha256(initial_coordinate),
                    "initial_coordinate_norm": initial_coordinate_norm,
                    "initial_tangent_perturbation_norm": initial_tangent_norm,
                    "state_record_count": len(trajectory_state_rows),
                    "checkpoint_record_count": len(trajectory_checkpoint_rows),
                    "state_metric_sha256": q011e.q011c._array_sha256(state_rows_array),
                    "checkpoint_metric_sha256": q011e.q011c._array_sha256(checkpoint_rows_array),
                    "maximum_common_input_joint_action_relative_error": (
                        trajectory_maximum_action_error
                    ),
                    "maximum_sparse_realification_imaginary_leakage": (
                        trajectory_maximum_imaginary
                    ),
                    "maximum_coordinate_error_over_initial_coordinate_norm": (
                        trajectory_maximum_coordinate_error
                    ),
                    "maximum_state_error_over_initial_tangent_perturbation_norm": (
                        trajectory_maximum_state_error
                    ),
                    "maximum_defect_vector_error_over_initial_coordinate_norm": (
                        trajectory_maximum_defect_error
                    ),
                    "maximum_defect_norm_difference_over_initial_coordinate_norm": (
                        trajectory_maximum_defect_norm_difference
                    ),
                    "minimum_population": trajectory_minimum_population,
                    "maximum_global_conservation_drift": (trajectory_maximum_conservation),
                    "checkpoint_records": checkpoint_records,
                }
            )
            global_minimum_population = min(
                global_minimum_population,
                trajectory_minimum_population,
            )
            global_maximum_conservation = max(
                global_maximum_conservation,
                trajectory_maximum_conservation,
            )
            global_maximum_action_error = max(
                global_maximum_action_error,
                trajectory_maximum_action_error,
            )
            global_maximum_imaginary = max(
                global_maximum_imaginary,
                trajectory_maximum_imaginary,
            )
            global_maximum_coordinate_error = max(
                global_maximum_coordinate_error,
                trajectory_maximum_coordinate_error,
            )
            global_maximum_state_error = max(
                global_maximum_state_error,
                trajectory_maximum_state_error,
            )
            global_maximum_defect_error = max(
                global_maximum_defect_error,
                trajectory_maximum_defect_error,
            )
            global_maximum_defect_norm_difference = max(
                global_maximum_defect_norm_difference,
                trajectory_maximum_defect_norm_difference,
            )

    state_metrics = np.asarray(state_metric_rows, dtype=np.float64)
    checkpoint_metrics = np.asarray(checkpoint_metric_rows, dtype=np.float64)
    checks = {
        "trajectory_and_state_counts_are_complete": (
            len(trajectory_records) == TRAJECTORY_COUNT
            and state_metrics.shape == (STATE_RECORD_COUNT, 15)
            and all(
                record["state_record_count"] == MAXIMUM_STEP + 1 for record in trajectory_records
            )
        ),
        "independent_update_counts_are_complete": (
            dense_update_count == UPDATE_COUNT_PER_IMPLEMENTATION
            and sparse_update_count == UPDATE_COUNT_PER_IMPLEMENTATION
        ),
        "common_input_action_comparison_count_is_complete": (
            action_comparison_count == ACTION_COMPARISON_COUNT
        ),
        "checkpoint_counts_are_complete": (
            checkpoint_metrics.shape == (CHECKPOINT_COUNT_PER_IMPLEMENTATION, 10)
            and all(
                record["checkpoint_record_count"] == len(CHECKPOINTS)
                for record in trajectory_records
            )
            and all(
                [checkpoint["step"] for checkpoint in record["checkpoint_records"]]
                == list(CHECKPOINTS)
                for record in trajectory_records
            )
        ),
        "all_campaign_arrays_and_metrics_are_finite": bool(
            all_arrays_finite
            and np.all(np.isfinite(state_metrics))
            and np.all(np.isfinite(checkpoint_metrics))
        ),
        "initial_coordinates_are_unique": (
            len({record["initial_coordinate_sha256"] for record in trajectory_records})
            == TRAJECTORY_COUNT
        ),
    }
    return q011e._json_native(
        {
            "trajectory_count": len(trajectory_records),
            "state_record_count": int(state_metrics.shape[0]),
            "dense_reduced_update_count": dense_update_count,
            "sparse_reduced_update_count": sparse_update_count,
            "common_input_action_comparison_count": action_comparison_count,
            "dense_checkpoint_defect_count": int(checkpoint_metrics.shape[0]),
            "sparse_checkpoint_defect_count": int(checkpoint_metrics.shape[0]),
            "state_metric_columns": [
                "direction_index",
                "amplitude_index",
                "step",
                "dense_coordinate_norm",
                "sparse_coordinate_norm",
                "coordinate_error_over_initial_coordinate_norm",
                "dense_state_perturbation_norm",
                "sparse_state_perturbation_norm",
                "state_error_over_initial_tangent_perturbation_norm",
                "action_error_at_dense_coordinate",
                "action_error_at_sparse_coordinate",
                "imaginary_leakage_at_dense_coordinate",
                "imaginary_leakage_at_sparse_coordinate",
                "minimum_population",
                "maximum_global_conservation_drift",
            ],
            "checkpoint_metric_columns": [
                "direction_index",
                "amplitude_index",
                "step",
                "dense_defect_norm",
                "sparse_defect_norm",
                "defect_vector_error_over_initial_coordinate_norm",
                "defect_norm_difference_over_initial_coordinate_norm",
                "minimum_population",
                "maximum_global_conservation_drift",
                "next_sparse_action_imaginary_leakage",
            ],
            "state_metric_sha256": q011e.q011c._array_sha256(state_metrics),
            "checkpoint_metric_sha256": q011e.q011c._array_sha256(checkpoint_metrics),
            "maximum_common_input_joint_action_relative_error": (global_maximum_action_error),
            "maximum_sparse_realification_imaginary_leakage": (global_maximum_imaginary),
            "maximum_coordinate_error_over_initial_coordinate_norm": (
                global_maximum_coordinate_error
            ),
            "maximum_state_error_over_initial_tangent_perturbation_norm": (
                global_maximum_state_error
            ),
            "maximum_defect_vector_error_over_initial_coordinate_norm": (
                global_maximum_defect_error
            ),
            "maximum_defect_norm_difference_over_initial_coordinate_norm": (
                global_maximum_defect_norm_difference
            ),
            "minimum_population": global_minimum_population,
            "maximum_global_conservation_drift": global_maximum_conservation,
            "trajectory_records": trajectory_records,
            "checks": checks,
            "passed": all(checks.values()),
        }
    )


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "coefficient_digest_sha256": cycle["coefficient_digest_sha256"],
        "campaign_digest_sha256": cycle["campaign_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_sparse_chart_equivalence_audit() -> dict[str, Any]:
    registered_parameters = _registered_parameters()
    sealed_q011g, q011g_artifact = _sealed_q011g_artifact_audit()
    data, coefficient_audit = _coefficient_reconstruction_audit(q011g_artifact)
    runtime, runtime_path_audit = _sparse_runtime_data(data)
    directions, amplitudes, direction_audit = _direction_audit()
    campaign = _trajectory_campaign(data, runtime, directions, amplitudes)
    runner = _runner_source_metadata()

    input_sections = q011e._json_native(
        {
            "registered_parameters": registered_parameters,
            "sealed_q011g_artifact_audit": sealed_q011g,
        }
    )
    coefficient_sections = q011e._json_native(
        {
            "coefficient_reconstruction_audit": coefficient_audit,
            "sparse_runtime_path_audit": runtime_path_audit,
        }
    )
    campaign_sections = q011e._json_native(
        {
            "direction_and_amplitude_audit": direction_audit,
            "trajectory_campaign": campaign,
        }
    )
    input_digest = q011e.q011c._canonical_json_sha256(input_sections)
    coefficient_digest = q011e.q011c._canonical_json_sha256(coefficient_sections)
    campaign_digest = q011e.q011c._canonical_json_sha256(campaign_sections)
    strict_payload = {
        **input_sections,
        **coefficient_sections,
        **campaign_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(strict_payload) and _strict_json_serializable(strict_payload)
    )
    digests_reproduce = bool(
        input_digest == q011e.q011c._canonical_json_sha256(input_sections)
        and coefficient_digest == q011e.q011c._canonical_json_sha256(coefficient_sections)
        and campaign_digest == q011e.q011c._canonical_json_sha256(campaign_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
    )
    validity_gates = {
        "q011g_and_prior_outcomes_are_sealed": {
            "passed": sealed_q011g["passed"],
            "threshold": (
                "Q011g artifact, runner, package source, five digests, rejected "
                "outcome and no-TT-cross decision reproduce while Q011f1 and Q011f remain sealed"
            ),
            "value": sealed_q011g["checks"],
        },
        "natural_coefficients_reconstruct_once": {
            "passed": coefficient_audit["passed"],
            "threshold": (
                "one fresh natural coefficient reconstruction reproduces registered "
                "pair, sector, shape, storage, projection, serialization and array hashes"
            ),
            "value": coefficient_audit["checks"],
        },
        "independent_campaign_inputs_are_complete": {
            "passed": direction_audit["passed"],
            "threshold": (
                "seeded 24-direction and three-amplitude hashes reproduce with zero "
                "exact prior duplicates"
            ),
            "value": direction_audit["checks"],
        },
        "sparse_path_and_campaign_protocol_are_complete": {
            "passed": bool(runtime_path_audit["passed"] and campaign["passed"]),
            "threshold": (
                "sparse runtime owns no dense quadratic fields and all registered "
                "trajectory, update, action and checkpoint records are finite and complete"
            ),
            "value": {
                "runtime_path_checks": runtime_path_audit["checks"],
                "campaign_checks": campaign["checks"],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "finite strict JSON, three section digests and newline-normalized "
                "runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    action_passed = bool(
        campaign["maximum_common_input_joint_action_relative_error"]
        <= MAXIMUM_ACTION_RELATIVE_ERROR
        and campaign["maximum_sparse_realification_imaginary_leakage"] <= MAXIMUM_IMAGINARY_LEAKAGE
    )
    trajectory_passed = bool(
        campaign["maximum_coordinate_error_over_initial_coordinate_norm"]
        <= MAXIMUM_COORDINATE_SCALED_ERROR
        and campaign["maximum_state_error_over_initial_tangent_perturbation_norm"]
        <= MAXIMUM_STATE_SCALED_ERROR
    )
    defect_passed = bool(
        campaign["maximum_defect_vector_error_over_initial_coordinate_norm"]
        <= MAXIMUM_DEFECT_SCALED_ERROR
        and campaign["maximum_defect_norm_difference_over_initial_coordinate_norm"]
        <= MAXIMUM_DEFECT_NORM_SCALED_DIFFERENCE
    )
    physical_passed = bool(
        campaign["passed"]
        and campaign["minimum_population"] > 0.0
        and campaign["maximum_global_conservation_drift"] <= MAXIMUM_CONSERVATION_DRIFT
    )
    hypothesis_gates = {
        "all_common_input_actions_and_realification_agree": {
            "passed": bool(validity_passed and action_passed),
            "threshold": (
                "all 9,360 common-input joint actions have relative error <=1e-11 "
                "and all sparse realifications have imaginary leakage <=1e-11"
            ),
            "value": {
                "maximum_common_input_joint_action_relative_error": campaign[
                    "maximum_common_input_joint_action_relative_error"
                ],
                "maximum_sparse_realification_imaginary_leakage": campaign[
                    "maximum_sparse_realification_imaginary_leakage"
                ],
            },
        },
        "all_reduced_coordinates_and_lifted_states_agree": {
            "passed": bool(validity_passed and trajectory_passed),
            "threshold": (
                "all 4,680 state records have coordinate and lifted-state scaled errors <=1e-11"
            ),
            "value": {
                "maximum_coordinate_error_over_initial_coordinate_norm": campaign[
                    "maximum_coordinate_error_over_initial_coordinate_norm"
                ],
                "maximum_state_error_over_initial_tangent_perturbation_norm": campaign[
                    "maximum_state_error_over_initial_tangent_perturbation_norm"
                ],
            },
        },
        "all_checkpoint_defects_agree": {
            "passed": bool(validity_passed and defect_passed),
            "threshold": (
                "all 576 checkpoint defect-vector and defect-norm scaled differences are <=1e-10"
            ),
            "value": {
                "maximum_defect_vector_error_over_initial_coordinate_norm": campaign[
                    "maximum_defect_vector_error_over_initial_coordinate_norm"
                ],
                "maximum_defect_norm_difference_over_initial_coordinate_norm": campaign[
                    "maximum_defect_norm_difference_over_initial_coordinate_norm"
                ],
            },
        },
        "campaign_is_finite_positive_and_conservative": {
            "passed": bool(validity_passed and physical_passed),
            "threshold": (
                "all registered records are complete and finite, minimum population "
                "is strictly positive and global conservation drift is <=1e-10"
            ),
            "value": {
                "campaign_checks": campaign["checks"],
                "minimum_population": campaign["minimum_population"],
                "maximum_global_conservation_drift": campaign["maximum_global_conservation_drift"],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011h sparse chart equivalence audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the natural Fourier-sparse chart reproduces the dense forced "
            "quadratic reduced trajectory through 64 steps"
        )
    else:
        outcome = "rejected"
        classification = (
            "the natural Fourier-sparse chart does not reproduce the dense "
            "forced quadratic reduced trajectory through 64 steps"
        )

    cycle: dict[str, Any] = q011e._json_native(
        {
            "question": (
                "Does the mandatory natural Fourier-sparse W2/R2 action reproduce "
                "the ordered-dense real quadratic chart and reduced map through "
                "64 independently updated reduced steps?"
            ),
            **strict_payload,
            "input_digest_sha256": input_digest,
            "coefficient_digest_sha256": coefficient_digest,
            "campaign_digest_sha256": campaign_digest,
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
        "natural_fourier_sparse_is_selected_for_subsequent_chart_work": bool(
            validity_passed and hypotheses_passed
        ),
        "q011g_rejected_tt_svd_outcome_changed": False,
        "tt_cross_followup_is_authorized": False,
        "q011f1_accepted_shadowing_outcome_changed": False,
        "q011f_rejected_shadowing_outcome_changed": False,
        "full_state_64_step_shadowing_is_newly_certified": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This finite audit covers the sealed 17x17 zero-mean-forced fixed-leaf "
        "quadratic chart, 72 independent initial reduced coordinates, 64 reduced "
        "steps and eight one-step-defect checkpoints in binary64. It does not "
        "regrade Q011f or Q011f1 shadowing, propagate a full LBM orbit for 64 "
        "steps, establish all-time equivalence, a uniform remainder, higher-order "
        "coefficients, other grids, forces or walls, D3Q27, SSM existence or "
        "uniqueness, normal attraction or a basin. Q011g remains rejected and "
        "TT-cross remains unauthorized."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011g_rejected_representation_audit_changed": False,
        "q011f1_accepted_shadowing_reissue_changed": False,
        "q011f_rejected_shadowing_window_changed": False,
        "q011e1_accepted_residual_window_changed": False,
        "q011e_rejected_original_window_changed": False,
    }
    cycle["next_change"] = (
        "Use the sealed natural Fourier-sparse chart as the implementation "
        "baseline and preregister a mathematical forced-SSM existence, uniqueness "
        "or normal-attraction gate."
        if outcome == "accepted"
        else (
            "Localize the first valid trajectory, action, realification or "
            "checkpoint-defect divergence without changing the registered campaign."
            if outcome == "rejected"
            else (
                "Localize the first failed sealing, coefficient, campaign, path "
                "separation or serialization validity gate."
            )
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011e.q011c._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011h cycle failed strict serialization or digest")
    return cycle


def run_q011h_study() -> dict[str, Any]:
    cycle = run_sparse_chart_equivalence_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "natural Fourier-sparse versus ordered-dense forced quadratic "
                "reduced-chart 64-step equivalence"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011e.q011c.OMEGA,
            "eta": q011e.q011c.ETA,
            "fixed_conservation_leaf": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "trajectory_count": TRAJECTORY_COUNT,
            "maximum_reduced_step": MAXIMUM_STEP,
            "checkpoint_count_per_implementation": CHECKPOINT_COUNT_PER_IMPLEMENTATION,
            "claim": (
                "finite binary64 sparse/dense reduced-chart and checkpoint "
                "one-step-defect equivalence only"
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
    result = run_q011h_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
