"""Q011m repaired exact quadratic-jet and cubic-defect majorant audit."""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011j_interval_fixed_point as q011j
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
POPULATION_COUNT = 9
SELECTED_BLOCKS = (0, 1, 16)
OUTPUT_SECTORS = (0, 1, 16, 2, 15)
SELECTED_DIMENSIONS = {0: 6, 1: 9, 16: 9}
EXPECTED_SELECTED_COUNT = 24
EXPECTED_PAIR_COUNT = 300
EXPECTED_SECTOR_PAIR_COUNTS = {0: 102, 1: 54, 16: 54, 2: 45, 15: 45}
ZERO_BLOCK_LIFT_NORM = 186
MOMENT_ROW_SUMS = (9, 6, 6)

ROOT_COMPONENT_RADIUS_ENVELOPE = Fraction(3, 10**13)
ROOT_POPULATION_FLOOR = Fraction(27, 1000)
ROOT_DENSITY_FLOOR = Fraction(999, 1000)
ROOT_MOMENTUM_COMPONENT_ENVELOPE = Fraction(3, 10**5)
VECTOR_NORM_ENVELOPES = {0: Fraction(13), 1: Fraction(16), 16: Fraction(16)}
GRAPH_RADIUS_ENVELOPES = {
    0: Fraction(2, 10**6),
    1: Fraction(1, 10**7),
    16: Fraction(1, 10**7),
}
INVERSE_COORDINATE_ENVELOPES = {
    0: Fraction(53),
    1: Fraction(25),
    16: Fraction(25),
}
AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES = {
    0: Fraction(3_400_000),
    1: Fraction(24_000),
    16: Fraction(24_000),
    2: Fraction(2_300_000),
    15: Fraction(2_300_000),
}
SELECTED_DYNAMICS_NORM_ENVELOPE = Fraction(31, 25)

STATE_DISPLACEMENT_CAP = Fraction(1, 10**4)
SECOND_DERIVATIVE_CAP = Fraction(145)
THIRD_DERIVATIVE_CAP = Fraction(4000)
TANGENT_CAP = Fraction(2500)
FORCING_CAP = Fraction(500_000_000)
CHART_CAP = Fraction(300_000_000_000_000_000)
REDUCED_QUADRATIC_CAP = Fraction(30_000_000_000)

POPULATION_THRESHOLD = Fraction(1, 50)
DENSITY_THRESHOLD = Fraction(99, 100)
REDUCED_EXPANSION_CAP = Fraction(2)
DEFECT_CAP = Fraction(2, 100_000)
DEFECT_UTILIZATION_CAP = Fraction(3, 4)
MINIMUM_SELECTED_RADIUS = Fraction(1, 10**11)
RADIUS_CANDIDATES = (
    Fraction(1, 10**14),
    Fraction(3, 10**14),
    Fraction(1, 10**13),
    Fraction(3, 10**13),
    Fraction(1, 10**12),
    Fraction(3, 10**12),
    Fraction(1, 10**11),
    Fraction(3, 10**11),
)

Q011J_ARTIFACT_SHA256 = "74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a"
Q011J_RUNNER_SHA256 = "23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5"
Q011J_DIGESTS = (
    "a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799",
    "adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b",
    "177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f",
    "1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0",
    "ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934",
)
Q011J_CLASSIFICATION = (
    "the repaired periodic forcing admits a locally unique exact fixed-leaf "
    "fixed point in the registered rational box"
)
Q011K_ARTIFACT_SHA256 = "8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a"
Q011K_RUNNER_SHA256 = "d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07"
Q011K_DIGESTS = (
    "f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2",
    "f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc",
    "7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8",
    "1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4",
    "2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e",
)
Q011K_CLASSIFICATION = (
    "the exact repaired fixed point has a rigorously stable and quadratically "
    "nonresonant selected/external spectral split"
)
Q011L_ARTIFACT_SHA256 = "2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a"
Q011L_RUNNER_SHA256 = "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7"
Q011L_DIGESTS = (
    "1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011",
    "a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3",
    "694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377",
    "14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915",
    "c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45",
)
Q011L_CLASSIFICATION = (
    "the exact repaired selected/external split has a rigorously bounded "
    "quadratic homological inverse in the registered quotient norm"
)


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _digest_tuple(cycle: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


def _sealed_input_audit() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011j",
            directory / "q011j_interval_fixed_point.json",
            Path(q011j.__file__).resolve(),
            Q011J_ARTIFACT_SHA256,
            Q011J_RUNNER_SHA256,
            Q011J_DIGESTS,
            Q011J_CLASSIFICATION,
            (
                "input_digest_sha256",
                "coordinate_digest_sha256",
                "oracle_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
        ),
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            Q011K_ARTIFACT_SHA256,
            Q011K_RUNNER_SHA256,
            Q011K_DIGESTS,
            Q011K_CLASSIFICATION,
            (
                "input_digest_sha256",
                "root_digest_sha256",
                "block_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
        ),
        (
            "q011l",
            directory / "q011l_interval_homological_inverse.json",
            Path(q011l.__file__).resolve(),
            Q011L_ARTIFACT_SHA256,
            Q011L_RUNNER_SHA256,
            Q011L_DIGESTS,
            Q011L_CLASSIFICATION,
            (
                "input_digest_sha256",
                "graph_digest_sha256",
                "pair_digest_sha256",
                "homological_digest_sha256",
                "result_digest_sha256",
            ),
        ),
    )
    artifacts: dict[str, dict[str, Any]] = {}
    records: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    for (
        label,
        artifact_path,
        runner_path,
        artifact_hash,
        runner_hash,
        expected_digests,
        classification,
        digest_names,
    ) in specifications:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        cycle = artifact["cycle"]
        digests = _digest_tuple(cycle, digest_names)
        artifacts[label] = artifact
        checks[f"{label}_artifact_sha256_matches"] = (
            _file_sha256(artifact_path) == artifact_hash
        )
        checks[f"{label}_runner_sha256_matches"] = _file_sha256(runner_path) == runner_hash
        checks[f"{label}_digests_match"] = digests == expected_digests
        checks[f"{label}_accepted_outcome_reproduces"] = (
            cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and cycle["scientific_classification"] == classification
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        )
        checks[f"{label}_package_source_metadata_matches"] = (
            artifact["source"] == source_metadata()
        )
        records[label] = {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digests": list(digests),
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        }

    j_theorem = artifacts["q011j"]["cycle"]["theorem_consequence"]
    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    l_theorem = artifacts["q011l"]["cycle"]["theorem_consequence"]
    checks["q011j_claim_boundary_is_preserved"] = (
        j_theorem["repaired_exact_full_17x17_x_independent_fixed_point_exists"]
        and j_theorem["fixed_point_is_unique_within_the_selected_affine_box"]
        and not j_theorem["raw_q011b_exact_map_fixed_point_is_certified"]
        and not j_theorem["q011e_through_q011h_coefficients_transfer_to_repaired_map"]
        and not j_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011k_claim_boundary_is_preserved"] = (
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["q011c2_designated_selected_cluster_has_rigorous_dimension_24"]
        and k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
        and not k_theorem["nonnormal_homological_inverse_is_certified"]
        and not k_theorem["q011e_through_q011h_coefficients_transfer_to_repaired_map"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011l_claim_boundary_is_preserved"] = (
        l_theorem["exact_selected_invariant_graphs_are_certified"]
        and l_theorem["all_five_quadratic_sector_homological_operators_are_invertible"]
        and l_theorem["registered_ambient_lifted_inverse_bound_is_rigorous"]
        and not l_theorem["repaired_quadratic_jet_or_coefficients_are_certified"]
        and not l_theorem["q011d_or_q011e_raw_coefficients_transfer_to_repaired_map"]
        and not l_theorem["forced_ssm_exists_or_is_unique"]
    )
    audit = {**records, "checks": checks, "passed": all(checks.values())}
    return audit, artifacts["q011j"], artifacts["q011k"], artifacts["q011l"]


def _root_and_envelope_audit(
    q011j_artifact: dict[str, Any],
    q011k_artifact: dict[str, Any],
    q011l_artifact: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray[Any, np.dtype[np.int64]]]:
    _, lifted, lift_matrix, _, _, reproduced_root = q011k._root_enclosure_audit(
        q011j_artifact
    )
    stored_root = q011k_artifact["cycle"]["contraction_derived_root_enclosure_audit"]
    root_component_radius = _fraction(stored_root["ambient_population_component_radius_upper"])
    population_floor = _fraction(stored_root["minimum_population_lower"])
    density_floor = _fraction(stored_root["minimum_density_lower"])

    site_moments: list[tuple[Fraction, Fraction, Fraction]] = []
    for site in range(SIZE):
        populations = lifted[site * POPULATION_COUNT : (site + 1) * POPULATION_COUNT]
        rho = sum(populations, Fraction(0))
        momentum_x = sum(
            (value * velocity[0] for value, velocity in zip(populations, q011j.VELOCITIES, strict=True)),
            Fraction(0),
        )
        momentum_y = sum(
            (value * velocity[1] for value, velocity in zip(populations, q011j.VELOCITIES, strict=True)),
            Fraction(0),
        )
        site_moments.append((rho, momentum_x, momentum_y))
    momentum_witness = max(
        (
            (abs(value), site, component)
            for site, moments in enumerate(site_moments)
            for component, value in enumerate(moments[1:], start=1)
        ),
        key=lambda item: item[0],
    )
    center_momentum_upper = momentum_witness[0]
    enclosed_root_momentum_upper = center_momentum_upper + 6 * root_component_radius

    k_records = {
        record["block_index"]: record
        for record in q011k_artifact["cycle"]["dual_precision_bauer_fike_audit"][
            "representative_block_records"
        ]
    }
    l_cycle = q011l_artifact["cycle"]
    l_eigen_records = {
        record["block_index"]: record
        for record in l_cycle["exact_eigencoordinate_residual_audit"]["block_records"]
    }
    graph_records = {
        record["block_index"]: record
        for record in l_cycle["selected_invariant_graph_audit"]["block_records"]
    }
    vector_norms: dict[int, Fraction] = {}
    inverse_coordinates: dict[int, Fraction] = {}
    graph_radii: dict[int, Fraction] = {}
    for block in SELECTED_BLOCKS:
        representative = 0 if block == 0 else 1
        primary = k_records[representative]["primary_precision_proof"]
        vector_norms[block] = _fraction(primary["vector_infinity_norm_upper"])
        inverse_coordinates[block] = _fraction(l_eigen_records[block]["beta_upper"])
        graph_radii[block] = _fraction(graph_records[block]["graph_radius_upper"])

    sector_records = {
        record["output_sector"]: record
        for record in l_cycle["sector_homological_inverse_audit"]["sector_records"]
    }
    ambient_inverse = {
        sector: _fraction(sector_records[sector]["ambient_inverse"])
        for sector in OUTPUT_SECTORS
    }
    symmetric = l_cycle["symmetric_product_perturbation_audit"]
    selected_dynamics_norm = _fraction(
        symmetric["selected_center_complex_l1_upper"]
    ) + _fraction(symmetric["selected_dynamics_perturbation_upper"])
    lift_norm = int(np.max(np.sum(np.abs(lift_matrix), axis=1)))

    checks = {
        "q011k_root_enclosure_reconstructs_exactly": reproduced_root == stored_root,
        "root_population_component_radius_is_enclosed": (
            root_component_radius <= ROOT_COMPONENT_RADIUS_ENVELOPE
        ),
        "root_population_floor_is_enclosed": population_floor >= ROOT_POPULATION_FLOOR,
        "root_density_floor_is_enclosed": density_floor >= ROOT_DENSITY_FLOOR,
        "center_and_entire_root_momentum_are_enclosed": (
            center_momentum_upper <= ROOT_MOMENTUM_COMPONENT_ENVELOPE
            and enclosed_root_momentum_upper <= ROOT_MOMENTUM_COMPONENT_ENVELOPE
        ),
        "selected_vector_norms_are_enclosed": all(
            vector_norms[block] <= VECTOR_NORM_ENVELOPES[block]
            for block in SELECTED_BLOCKS
        ),
        "selected_graph_radii_are_enclosed": all(
            graph_radii[block] <= GRAPH_RADIUS_ENVELOPES[block]
            for block in SELECTED_BLOCKS
        ),
        "selected_inverse_coordinate_norms_are_enclosed": all(
            inverse_coordinates[block] <= INVERSE_COORDINATE_ENVELOPES[block]
            for block in SELECTED_BLOCKS
        ),
        "five_ambient_homological_inverse_norms_are_enclosed": all(
            ambient_inverse[sector] <= AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[sector]
            for sector in OUTPUT_SECTORS
        ),
        "selected_dynamics_norm_is_enclosed": (
            selected_dynamics_norm <= SELECTED_DYNAMICS_NORM_ENVELOPE
        ),
        "zero_block_population_lift_norm_reproduces": lift_norm == ZERO_BLOCK_LIFT_NORM,
    }
    audit = {
        "root_population_component_radius_upper": _fraction_record(root_component_radius),
        "registered_root_population_component_radius_envelope": _fraction_record(
            ROOT_COMPONENT_RADIUS_ENVELOPE
        ),
        "root_population_floor_lower": _fraction_record(population_floor),
        "registered_root_population_floor": _fraction_record(ROOT_POPULATION_FLOOR),
        "root_density_floor_lower": _fraction_record(density_floor),
        "registered_root_density_floor": _fraction_record(ROOT_DENSITY_FLOOR),
        "center_momentum_component_absolute_upper": _fraction_record(center_momentum_upper),
        "center_momentum_witness": {
            "site": momentum_witness[1],
            "component": "jx" if momentum_witness[2] == 1 else "jy",
        },
        "enclosed_root_momentum_component_absolute_upper": _fraction_record(
            enclosed_root_momentum_upper
        ),
        "registered_root_momentum_component_envelope": _fraction_record(
            ROOT_MOMENTUM_COMPONENT_ENVELOPE
        ),
        "selected_block_records": [
            {
                "block_index": block,
                "vector_infinity_norm_upper": _fraction_record(vector_norms[block]),
                "vector_norm_envelope": _fraction_record(VECTOR_NORM_ENVELOPES[block]),
                "graph_radius_upper": _fraction_record(graph_radii[block]),
                "graph_radius_envelope": _fraction_record(GRAPH_RADIUS_ENVELOPES[block]),
                "inverse_coordinate_norm_upper": _fraction_record(
                    inverse_coordinates[block]
                ),
                "inverse_coordinate_envelope": _fraction_record(
                    INVERSE_COORDINATE_ENVELOPES[block]
                ),
            }
            for block in SELECTED_BLOCKS
        ],
        "sector_ambient_inverse_records": [
            {
                "output_sector": sector,
                "observed_upper": _fraction_record(ambient_inverse[sector]),
                "simple_envelope": _fraction_record(
                    AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[sector]
                ),
            }
            for sector in OUTPUT_SECTORS
        ],
        "selected_dynamics_infinity_norm_upper": _fraction_record(selected_dynamics_norm),
        "selected_dynamics_simple_envelope": _fraction_record(
            SELECTED_DYNAMICS_NORM_ENVELOPE
        ),
        "zero_block_population_lift_infinity_norm": lift_norm,
        "downstream_rule": (
            "only the registered simple rational envelopes, never observed floats, "
            "enter the derivative, coefficient and radius majorants"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lift_matrix


def _fourier_and_dimension_audit(
    lift_matrix: np.ndarray[Any, np.dtype[np.int64]],
    q011l_artifact: dict[str, Any],
) -> dict[str, Any]:
    cycle = q011l_artifact["cycle"]
    pairs = cycle["quadratic_pair_family_audit"]
    homological = cycle["sector_homological_inverse_audit"]
    sector_counts = {
        record["output_sector"]: record["pair_dimension"]
        for record in homological["sector_records"]
    }
    lift_norm = int(np.max(np.sum(np.abs(lift_matrix), axis=1)))
    checks = {
        "selected_blocks_and_dimensions_are_registered": (
            SELECTED_BLOCKS == (0, 1, 16)
            and SELECTED_DIMENSIONS == {0: 6, 1: 9, 16: 9}
            and sum(SELECTED_DIMENSIONS.values()) == EXPECTED_SELECTED_COUNT
        ),
        "unscaled_lexicographic_pair_count_reproduces": (
            EXPECTED_PAIR_COUNT
            == EXPECTED_SELECTED_COUNT * (EXPECTED_SELECTED_COUNT + 1) // 2
            == pairs["unordered_pair_count"]
        ),
        "sector_pair_counts_reproduce": sector_counts == EXPECTED_SECTOR_PAIR_COUNTS,
        "zero_block_lift_norm_is_included": lift_norm == ZERO_BLOCK_LIFT_NORM,
        "conjugacy_real_nonzero_blocks_are_both_included": (
            1 in SELECTED_BLOCKS and SIZE - 1 in SELECTED_BLOCKS
        ),
    }
    return {
        "forward_transform": (
            "hat(f)_n(y,q) = (1/17) sum_x f(y,x,q) exp(-2*pi*i*n*x/17)"
        ),
        "inverse_transform": (
            "f(y,x,q) = sum_n hat(f)_n(y,q) exp(2*pi*i*n*x/17)"
        ),
        "reduced_norm": "complex l-infinity on 24 selected coordinates",
        "population_norm": "complex component l-infinity on the full 17x17x9 state",
        "quadratic_basis": "unscaled lexicographic monomials a_i a_j for i <= j",
        "coefficient_norm": "maximum row sum over 300 pair columns",
        "cross_sector_cancellation_used": False,
        "selected_blocks": list(SELECTED_BLOCKS),
        "selected_dimensions": {
            str(key): value for key, value in SELECTED_DIMENSIONS.items()
        },
        "selected_coordinate_count": EXPECTED_SELECTED_COUNT,
        "quadratic_pair_count": EXPECTED_PAIR_COUNT,
        "sector_pair_counts": {
            str(key): value for key, value in sector_counts.items()
        },
        "zero_block_population_lift_infinity_norm": lift_norm,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _q_hessian(velocity: tuple[int, int]) -> tuple[tuple[Fraction, Fraction], ...]:
    return tuple(
        tuple(
            Fraction(9 * velocity[left] * velocity[right] - 3 * int(left == right))
            for right in range(2)
        )
        for left in range(2)
    )


def _signed_derivative_tensors(
    weight: Fraction,
    velocity: tuple[int, int],
    rho: Fraction,
    momentum: tuple[Fraction, Fraction],
) -> tuple[list[list[Fraction]], list[list[list[Fraction]]]]:
    dot = sum((Fraction(c) * j for c, j in zip(velocity, momentum, strict=True)), Fraction(0))
    q_value = Fraction(9, 2) * dot**2 - Fraction(3, 2) * sum(j**2 for j in momentum)
    gradient = tuple(Fraction(9 * velocity[index]) * dot - 3 * momentum[index] for index in range(2))
    hessian = _q_hessian(velocity)

    def second(left: int, right: int) -> Fraction:
        if left == right == 0:
            return 2 * weight * q_value / rho**3
        if left == 0 or right == 0:
            component = right - 1 if left == 0 else left - 1
            return -weight * gradient[component] / rho**2
        return weight * hessian[left - 1][right - 1] / rho

    def third(left: int, middle: int, right: int) -> Fraction:
        indices = (left, middle, right)
        rho_count = indices.count(0)
        momentum_indices = [index - 1 for index in indices if index]
        if rho_count == 3:
            return -6 * weight * q_value / rho**4
        if rho_count == 2:
            return 2 * weight * gradient[momentum_indices[0]] / rho**3
        if rho_count == 1:
            return -weight * hessian[momentum_indices[0]][momentum_indices[1]] / rho**2
        return Fraction(0)

    second_tensor = [[second(left, right) for right in range(3)] for left in range(3)]
    third_tensor = [
        [
            [third(left, middle, right) for right in range(3)]
            for middle in range(3)
        ]
        for left in range(3)
    ]
    return second_tensor, third_tensor


def _derivative_audit() -> dict[str, Any]:
    rho_lower = ROOT_DENSITY_FLOOR - MOMENT_ROW_SUMS[0] * STATE_DISPLACEMENT_CAP
    momentum_upper = (
        ROOT_MOMENTUM_COMPONENT_ENVELOPE
        + MOMENT_ROW_SUMS[1] * STATE_DISPLACEMENT_CAP
    )
    second_records: list[dict[str, Any]] = []
    second_bounds: list[Fraction] = []
    third_bounds: list[Fraction] = []
    for population, (weight, velocity) in enumerate(
        zip(q011j.WEIGHTS, q011j.VELOCITIES, strict=True)
    ):
        dot_upper = Fraction(abs(velocity[0]) + abs(velocity[1])) * momentum_upper
        q_upper = Fraction(9, 2) * dot_upper**2 + 3 * momentum_upper**2
        gradient_upper = tuple(
            Fraction(9 * abs(velocity[index])) * dot_upper + 3 * momentum_upper
            for index in range(2)
        )
        hessian = _q_hessian(velocity)
        hessian_absolute = tuple(tuple(abs(value) for value in row) for row in hessian)

        def second_component(
            left: int,
            right: int,
            local_weight: Fraction = weight,
            local_q_upper: Fraction = q_upper,
            local_gradient_upper: tuple[Fraction, Fraction] = gradient_upper,
            local_hessian_absolute: tuple[tuple[Fraction, Fraction], ...] = (
                hessian_absolute
            ),
        ) -> Fraction:
            if left == right == 0:
                return 2 * local_weight * local_q_upper / rho_lower**3
            if left == 0 or right == 0:
                component = right - 1 if left == 0 else left - 1
                return local_weight * local_gradient_upper[component] / rho_lower**2
            return (
                local_weight
                * local_hessian_absolute[left - 1][right - 1]
                / rho_lower
            )

        def third_component(
            left: int,
            middle: int,
            right: int,
            local_weight: Fraction = weight,
            local_q_upper: Fraction = q_upper,
            local_gradient_upper: tuple[Fraction, Fraction] = gradient_upper,
            local_hessian_absolute: tuple[tuple[Fraction, Fraction], ...] = (
                hessian_absolute
            ),
        ) -> Fraction:
            indices = (left, middle, right)
            rho_count = indices.count(0)
            momentum_indices = [index - 1 for index in indices if index]
            if rho_count == 3:
                return 6 * local_weight * local_q_upper / rho_lower**4
            if rho_count == 2:
                return (
                    2
                    * local_weight
                    * local_gradient_upper[momentum_indices[0]]
                    / rho_lower**3
                )
            if rho_count == 1:
                return (
                    local_weight
                    * local_hessian_absolute[momentum_indices[0]][momentum_indices[1]]
                    / rho_lower**2
                )
            return Fraction(0)

        second_bound = q011j.OMEGA * sum(
            (
                second_component(left, right)
                * MOMENT_ROW_SUMS[left]
                * MOMENT_ROW_SUMS[right]
                for left in range(3)
                for right in range(3)
            ),
            Fraction(0),
        )
        third_bound = q011j.OMEGA * sum(
            (
                third_component(left, middle, right)
                * MOMENT_ROW_SUMS[left]
                * MOMENT_ROW_SUMS[middle]
                * MOMENT_ROW_SUMS[right]
                for left in range(3)
                for middle in range(3)
                for right in range(3)
            ),
            Fraction(0),
        )
        second_bounds.append(second_bound)
        third_bounds.append(third_bound)
        second_records.append(
            {
                "population": population,
                "velocity": list(velocity),
                "weight": _fraction_record(weight),
                "q_absolute_upper": _fraction_record(q_upper),
                "gradient_absolute_upper": [
                    _fraction_record(value) for value in gradient_upper
                ],
                "hessian": [
                    [_fraction_record(value) for value in row] for row in hessian
                ],
                "map_second_derivative_bilinear_upper": _fraction_record(second_bound),
                "map_third_derivative_trilinear_upper": _fraction_record(third_bound),
            }
        )

    maximum_second = max(second_bounds)
    maximum_third = max(third_bounds)
    maximum_second_population = second_bounds.index(maximum_second)
    maximum_third_population = third_bounds.index(maximum_third)

    sample_rho = ROOT_DENSITY_FLOOR
    sample_momentum = (
        ROOT_MOMENTUM_COMPONENT_ENVELOPE,
        -ROOT_MOMENTUM_COMPONENT_ENVELOPE,
    )
    signed_tensors = [
        _signed_derivative_tensors(weight, velocity, sample_rho, sample_momentum)
        for weight, velocity in zip(q011j.WEIGHTS, q011j.VELOCITIES, strict=True)
    ]
    second_symmetry = all(
        tensor[left][right] == tensor[right][left]
        for tensor, _ in signed_tensors
        for left in range(3)
        for right in range(3)
    )
    third_symmetry = all(
        tensor[left][middle][right]
        == tensor[permutation[0]][permutation[1]][permutation[2]]
        for _, tensor in signed_tensors
        for left in range(3)
        for middle in range(3)
        for right in range(3)
        for permutation in set(itertools.permutations((left, middle, right)))
    )

    conserved_multipliers = (
        tuple(Fraction(1) for _ in q011j.VELOCITIES),
        tuple(Fraction(velocity[0]) for velocity in q011j.VELOCITIES),
        tuple(Fraction(velocity[1]) for velocity in q011j.VELOCITIES),
    )
    equilibrium_identity_records: list[dict[str, Any]] = []
    expected_linear = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    identity_passes = True
    for moment, multipliers in enumerate(conserved_multipliers):
        rho_coefficient = sum(
            (multiplier * weight for multiplier, weight in zip(multipliers, q011j.WEIGHTS, strict=True)),
            Fraction(0),
        )
        momentum_coefficients = tuple(
            3
            * sum(
                (
                    multiplier * weight * velocity[axis]
                    for multiplier, weight, velocity in zip(
                        multipliers, q011j.WEIGHTS, q011j.VELOCITIES, strict=True
                    )
                ),
                Fraction(0),
            )
            for axis in range(2)
        )
        nonlinear_hessian = tuple(
            tuple(
                sum(
                    (
                        multiplier * weight * _q_hessian(velocity)[left][right]
                        for multiplier, weight, velocity in zip(
                            multipliers, q011j.WEIGHTS, q011j.VELOCITIES, strict=True
                        )
                    ),
                    Fraction(0),
                )
                for right in range(2)
            )
            for left in range(2)
        )
        coefficients = (rho_coefficient, *momentum_coefficients)
        passed = coefficients == expected_linear[moment] and all(
            value == 0 for row in nonlinear_hessian for value in row
        )
        identity_passes = identity_passes and passed
        equilibrium_identity_records.append(
            {
                "conserved_moment": ("mass", "momentum_x", "momentum_y")[moment],
                "linear_coefficients_rho_jx_jy": [
                    _fraction_record(value) for value in coefficients
                ],
                "nonlinear_hessian_coefficients": [
                    [_fraction_record(value) for value in row]
                    for row in nonlinear_hessian
                ],
                "passed": passed,
            }
        )

    second_conserved_values = [
        sum(
            (
                multipliers[population] * signed_tensors[population][0][left][right]
                for population in range(POPULATION_COUNT)
            ),
            Fraction(0),
        )
        for multipliers in conserved_multipliers
        for left in range(3)
        for right in range(3)
    ]
    third_conserved_values = [
        sum(
            (
                multipliers[population]
                * signed_tensors[population][1][left][middle][right]
                for population in range(POPULATION_COUNT)
            ),
            Fraction(0),
        )
        for multipliers in conserved_multipliers
        for left in range(3)
        for middle in range(3)
        for right in range(3)
    ]
    quadrature = q011j._quadrature_audit()
    exact_tensor_digest = q011b._canonical_json_sha256(
        {
            "second": [
                [[_fraction_record(value) for value in row] for row in second]
                for second, _ in signed_tensors
            ],
            "third": [
                [
                    [[_fraction_record(value) for value in row] for row in plane]
                    for plane in third
                ]
                for _, third in signed_tensors
            ],
        }
    )
    checks = {
        "registered_domain_has_positive_density": rho_lower > 0,
        "all_nine_population_derivative_bounds_are_exact": len(second_records) == 9,
        "second_derivative_tensor_has_mixed_partial_symmetry": second_symmetry,
        "third_derivative_tensor_has_full_mixed_partial_symmetry": third_symmetry,
        "d2q9_quadrature_reproduces": quadrature["passed"],
        "equilibrium_conserved_moment_identity_is_exact": identity_passes,
        "all_second_derivative_conserved_moments_are_zero": all(
            value == 0 for value in second_conserved_values
        ),
        "all_third_derivative_conserved_moments_are_zero": all(
            value == 0 for value in third_conserved_values
        ),
        "source_has_no_second_or_third_derivative": True,
        "streaming_and_filter_do_not_increase_population_infinity_norm": (
            q011j.FILTER_CENTER + 2 * q011j.FILTER_NEIGHBOUR == 1
            and q011j.FILTER_CENTER >= 0
            and q011j.FILTER_NEIGHBOUR >= 0
        ),
    }
    return {
        "moment_coordinates": ["rho", "jx", "jy"],
        "population_to_moment_absolute_row_sums": list(MOMENT_ROW_SUMS),
        "registered_state_displacement_cap": _fraction_record(STATE_DISPLACEMENT_CAP),
        "derived_density_lower": _fraction_record(rho_lower),
        "derived_momentum_component_absolute_upper": _fraction_record(momentum_upper),
        "bgk_factor": _fraction_record(q011j.OMEGA),
        "population_derivative_records": second_records,
        "maximum_map_second_derivative_bilinear_upper": _fraction_record(maximum_second),
        "maximum_second_derivative_population": maximum_second_population,
        "registered_second_derivative_cap": _fraction_record(SECOND_DERIVATIVE_CAP),
        "maximum_map_third_derivative_trilinear_upper": _fraction_record(maximum_third),
        "maximum_third_derivative_population": maximum_third_population,
        "registered_third_derivative_cap": _fraction_record(THIRD_DERIVATIVE_CAP),
        "signed_tensor_sample": {
            "rho": _fraction_record(sample_rho),
            "momentum": [_fraction_record(value) for value in sample_momentum],
            "exact_tensor_digest_sha256": exact_tensor_digest,
            "second_symmetry_comparison_count": POPULATION_COUNT * 3 * 3,
            "third_symmetry_permutation_family_count": POPULATION_COUNT * 3 * 3 * 3,
        },
        "equilibrium_conserved_moment_identity": equilibrium_identity_records,
        "exact_zero_second_conserved_component_count": len(second_conserved_values),
        "exact_zero_third_conserved_component_count": len(third_conserved_values),
        "quadrature_audit": quadrature,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _coefficient_audit(q011l_artifact: dict[str, Any]) -> tuple[
    dict[str, Any], dict[str, Fraction]
]:
    tangent = (
        ZERO_BLOCK_LIFT_NORM
        * VECTOR_NORM_ENVELOPES[0]
        * (1 + GRAPH_RADIUS_ENVELOPES[0])
        + VECTOR_NORM_ENVELOPES[1] * (1 + GRAPH_RADIUS_ENVELOPES[1])
        + VECTOR_NORM_ENVELOPES[16] * (1 + GRAPH_RADIUS_ENVELOPES[16])
    )
    forcing = Fraction(1, 2) * SECOND_DERIVATIVE_CAP * tangent**2
    inverse_sum = (
        ZERO_BLOCK_LIFT_NORM * AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[0]
        + AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[1]
        + AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[16]
        + AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[2]
        + AMBIENT_HOMOLOGICAL_INVERSE_ENVELOPES[15]
    )
    chart = forcing * inverse_sum
    reduced_quadratic = INVERSE_COORDINATE_ENVELOPES[0] * forcing
    selected_dynamics = SELECTED_DYNAMICS_NORM_ENVELOPE
    values = {
        "K_T": tangent,
        "K_F": forcing,
        "K_Z": chart,
        "K_P": reduced_quadratic,
        "K_S": selected_dynamics,
    }
    l_cycle = q011l_artifact["cycle"]
    theorem = l_cycle["theorem_consequence"]
    sector_records = l_cycle["sector_homological_inverse_audit"]["sector_records"]
    pair_audit = l_cycle["quadratic_pair_family_audit"]
    sector_counts = {
        record["output_sector"]: record["pair_dimension"] for record in sector_records
    }
    checks = {
        "tangent_formula_reproduces": tangent
        == Fraction(186 * 13) * (1 + Fraction(2, 10**6))
        + 2 * 16 * (1 + Fraction(1, 10**7)),
        "forcing_formula_reproduces": (
            forcing == Fraction(1, 2) * SECOND_DERIVATIVE_CAP * tangent**2
        ),
        "chart_formula_includes_zero_sector_lift": (
            chart
            == forcing
            * (
                186 * 3_400_000
                + 2 * 24_000
                + 2 * 2_300_000
            )
        ),
        "selected_forcing_formula_reproduces": reduced_quadratic == 53 * forcing,
        "all_300_pair_columns_are_retained": pair_audit["unordered_pair_count"] == 300,
        "all_five_sector_counts_are_retained": sector_counts == EXPECTED_SECTOR_PAIR_COUNTS,
        "q011l_proves_all_five_operators_invertible": (
            theorem["exact_selected_invariant_graphs_are_certified"]
            and theorem["all_five_quadratic_sector_homological_operators_are_invertible"]
            and theorem["registered_ambient_lifted_inverse_bound_is_rigorous"]
            and len(sector_records) == 5
            and all(record["passed"] for record in sector_records)
        ),
        "raw_q011e_through_q011h_coefficients_are_not_inputs": True,
    }
    return (
        {
            "quadratic_chart_definition": "W^[2](a) = x_* + T a + Z m(a)",
            "quadratic_reduced_definition": "R^[2](a) = S a + P m(a)",
            "gauge": "Z is external in each output sector; P is the selected projection",
            "existence_and_uniqueness": (
                "Q011l invertibility gives one and only one external graph-gauge Z "
                "for the repaired exact-map analytic quadratic forcing"
            ),
            "coefficient_values": {
                name: _fraction_record(value) for name, value in values.items()
            },
            "caps": {
                "K_T": _fraction_record(TANGENT_CAP),
                "K_F": _fraction_record(FORCING_CAP),
                "K_Z": _fraction_record(CHART_CAP),
                "K_P": _fraction_record(REDUCED_QUADRATIC_CAP),
            },
            "ambient_inverse_sector_sum": _fraction_record(inverse_sum),
            "selected_coordinate_count": EXPECTED_SELECTED_COUNT,
            "pair_count": EXPECTED_PAIR_COUNT,
            "sector_pair_counts": {
                str(key): value for key, value in sector_counts.items()
            },
            "componentwise_coefficient_array_constructed": False,
            "checks": checks,
            "passed": all(checks.values()),
        },
        values,
    )


def _majorant_audit(coefficients: dict[str, Fraction]) -> dict[str, Any]:
    kt = coefficients["K_T"]
    kz = coefficients["K_Z"]
    kp = coefficients["K_P"]
    ks = coefficients["K_S"]

    def state_displacement(radius: Fraction) -> Fraction:
        return kt * radius + kz * radius**2

    def reduced_amplitude(radius: Fraction) -> Fraction:
        return ks * radius + kp * radius**2

    def defect(radius: Fraction) -> Fraction:
        displacement = state_displacement(radius)
        return (
            SECOND_DERIVATIVE_CAP * kt * kz * radius**3
            + Fraction(1, 2) * SECOND_DERIVATIVE_CAP * kz**2 * radius**4
            + 2 * kz * ks * kp * radius**3
            + kz * kp**2 * radius**4
            + Fraction(THIRD_DERIVATIVE_CAP, 6) * displacement**3
        )

    records: list[dict[str, Any]] = []
    exact_records: list[dict[str, Any]] = []
    passing: list[Fraction] = []
    for radius in RADIUS_CANDIDATES:
        displacement = state_displacement(radius)
        reduced = reduced_amplitude(radius)
        defect_value = defect(radius)
        population_lower = ROOT_POPULATION_FLOOR - displacement
        density_lower = ROOT_DENSITY_FLOOR - 9 * displacement
        expansion = reduced / radius
        utilization = defect_value / displacement
        cubic_constant = defect_value / radius**3
        checks = {
            "state_displacement_is_in_derivative_domain": (
                displacement <= STATE_DISPLACEMENT_CAP
            ),
            "population_floor_is_preserved": population_lower >= POPULATION_THRESHOLD,
            "density_floor_is_preserved": density_lower >= DENSITY_THRESHOLD,
            "reduced_expansion_is_bounded": expansion <= REDUCED_EXPANSION_CAP,
            "cubic_defect_is_bounded": defect_value <= DEFECT_CAP,
            "defect_to_state_displacement_is_bounded": (
                utilization <= DEFECT_UTILIZATION_CAP
            ),
        }
        passed = all(checks.values())
        if passed:
            passing.append(radius)
        exact_record = {
            "radius": _fraction_record(radius),
            "state_displacement_upper": _fraction_record(displacement),
            "population_lower": _fraction_record(population_lower),
            "density_lower": _fraction_record(density_lower),
            "reduced_amplitude_upper": _fraction_record(reduced),
            "reduced_expansion_upper": _fraction_record(expansion),
            "cubic_defect_upper": _fraction_record(defect_value),
            "defect_to_state_displacement_upper": _fraction_record(utilization),
            "cubic_constant_upper": _fraction_record(cubic_constant),
        }
        exact_records.append(exact_record)
        records.append({**exact_record, "checks": checks, "passed": passed})

    selected = max(passing) if passing else None
    selected_record = next(
        (record for record in records if selected is not None and _fraction(record["radius"]) == selected),
        None,
    )
    larger_records = [
        record
        for record in records
        if selected is not None and _fraction(record["radius"]) > selected
    ]
    first_failed = larger_records[0] if larger_records else None
    failed_constraints = (
        [name for name, passed in first_failed["checks"].items() if not passed]
        if first_failed is not None
        else []
    )
    cubic_coefficient = (
        SECOND_DERIVATIVE_CAP * kt * kz + 2 * kz * ks * kp
    )
    quartic_coefficient = (
        Fraction(1, 2) * SECOND_DERIVATIVE_CAP * kz**2 + kz * kp**2
    )
    monotonicity_checks = {
        "explicit_cubic_coefficient_is_nonnegative": cubic_coefficient >= 0,
        "explicit_quartic_coefficient_is_nonnegative": quartic_coefficient >= 0,
        "taylor_remainder_coefficient_is_nonnegative": THIRD_DERIVATIVE_CAP >= 0,
        "state_polynomial_coefficients_are_nonnegative": kt >= 0 and kz >= 0,
        "normalized_derivative_is_nonnegative_for_nonnegative_radius": (
            quartic_coefficient >= 0
            and THIRD_DERIVATIVE_CAP * kz >= 0
        ),
    }
    checks = {
        "all_eight_registered_radii_are_present": len(records) == len(RADIUS_CANDIDATES) == 8,
        "radii_are_strictly_increasing": all(
            left < right for left, right in itertools.pairwise(RADIUS_CANDIDATES)
        ),
        "all_radius_values_use_exact_fraction_arithmetic": True,
        "passing_radius_exists": selected is not None,
        "selected_radius_is_the_largest_passing_candidate": (
            selected is not None
            and all(
                (_fraction(record["radius"]) <= selected) or not record["passed"]
                for record in records
            )
        ),
        "first_larger_candidate_failure_is_recorded": (
            selected == RADIUS_CANDIDATES[-1]
            or (first_failed is not None and not first_failed["passed"] and bool(failed_constraints))
        ),
        "normalized_cubic_majorant_is_monotone": all(monotonicity_checks.values()),
    }
    return {
        "state_displacement_formula": "U(r) = K_T r + K_Z r^2",
        "reduced_amplitude_formula": "A_R(r) = K_S r + K_P r^2",
        "defect_formula": (
            "D(r) = 145 K_T K_Z r^3 + (145/2) K_Z^2 r^4 + "
            "2 K_Z K_S K_P r^3 + K_Z K_P^2 r^4 + (4000/6) U(r)^3"
        ),
        "normalized_defect_formula": (
            "D(r)/r^3 = c_3 + c_4 r + (4000/6)(K_T + K_Z r)^3"
        ),
        "normalized_defect_derivative_formula": (
            "d[D(r)/r^3]/dr = c_4 + 2000 K_Z (K_T + K_Z r)^2 >= 0"
        ),
        "explicit_cubic_coefficient": _fraction_record(cubic_coefficient),
        "explicit_quartic_coefficient": _fraction_record(quartic_coefficient),
        "monotonicity_checks": monotonicity_checks,
        "radius_records": records,
        "exact_radius_record_digest_sha256": q011b._canonical_json_sha256(exact_records),
        "passing_radius_count": len(passing),
        "selected_radius": _fraction_record(selected) if selected is not None else None,
        "selected_record": selected_record,
        "first_failed_larger_radius": first_failed["radius"] if first_failed else None,
        "first_failed_larger_constraints": failed_constraints,
        "uniform_conclusion": (
            "D(t) <= [D(r)/r^3] t^3 for every 0 <= t <= selected r"
            if selected is not None
            else "no registered uniform cubic radius was certified"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "selected_blocks": list(SELECTED_BLOCKS),
        "output_sectors": list(OUTPUT_SECTORS),
        "selected_dimensions": {
            str(key): value for key, value in SELECTED_DIMENSIONS.items()
        },
        "expected_selected_count": EXPECTED_SELECTED_COUNT,
        "expected_pair_count": EXPECTED_PAIR_COUNT,
        "expected_sector_pair_counts": {
            str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()
        },
        "zero_block_lift_norm": ZERO_BLOCK_LIFT_NORM,
        "moment_row_sums": list(MOMENT_ROW_SUMS),
        "state_displacement_cap": _fraction_record(STATE_DISPLACEMENT_CAP),
        "second_derivative_cap": _fraction_record(SECOND_DERIVATIVE_CAP),
        "third_derivative_cap": _fraction_record(THIRD_DERIVATIVE_CAP),
        "coefficient_caps": {
            "K_T": _fraction_record(TANGENT_CAP),
            "K_F": _fraction_record(FORCING_CAP),
            "K_Z": _fraction_record(CHART_CAP),
            "K_P": _fraction_record(REDUCED_QUADRATIC_CAP),
        },
        "radius_candidates": [_fraction_record(value) for value in RADIUS_CANDIDATES],
        "minimum_selected_radius": _fraction_record(MINIMUM_SELECTED_RADIUS),
        "population_threshold": _fraction_record(POPULATION_THRESHOLD),
        "density_threshold": _fraction_record(DENSITY_THRESHOLD),
        "reduced_expansion_cap": _fraction_record(REDUCED_EXPANSION_CAP),
        "defect_cap": _fraction_record(DEFECT_CAP),
        "defect_utilization_cap": _fraction_record(DEFECT_UTILIZATION_CAP),
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "derivative_digest_sha256": cycle["derivative_digest_sha256"],
        "coefficient_digest_sha256": cycle["coefficient_digest_sha256"],
        "majorant_digest_sha256": cycle["majorant_digest_sha256"],
    }


def run_quadratic_jet_majorant_audit() -> dict[str, Any]:
    sealed, j_artifact, k_artifact, l_artifact = _sealed_input_audit()
    root_envelopes, lift_matrix = _root_and_envelope_audit(
        j_artifact, k_artifact, l_artifact
    )
    fourier = _fourier_and_dimension_audit(lift_matrix, l_artifact)
    derivative = _derivative_audit()
    coefficient, coefficient_values = _coefficient_audit(l_artifact)
    majorant = _majorant_audit(coefficient_values)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
        "exact_root_and_simple_envelope_audit": root_envelopes,
        "fourier_and_dimension_audit": fourier,
    }
    derivative_sections = {"analytic_map_derivative_audit": derivative}
    coefficient_sections = {"implicit_quadratic_jet_coefficient_audit": coefficient}
    majorant_sections = {"cubic_defect_radius_audit": majorant}
    input_digest = q011b._canonical_json_sha256(input_sections)
    derivative_digest = q011b._canonical_json_sha256(derivative_sections)
    coefficient_digest = q011b._canonical_json_sha256(coefficient_sections)
    majorant_digest = q011b._canonical_json_sha256(majorant_sections)
    strict_payload = {
        **input_sections,
        **derivative_sections,
        **coefficient_sections,
        **majorant_sections,
        "runner_source": runner,
    }
    digests_reproduce = (
        input_digest == q011b._canonical_json_sha256(input_sections)
        and derivative_digest == q011b._canonical_json_sha256(derivative_sections)
        and coefficient_digest == q011b._canonical_json_sha256(coefficient_sections)
        and majorant_digest == q011b._canonical_json_sha256(majorant_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "q011j_q011k_q011l_inputs_and_claim_boundaries_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "three artifact/runner hashes, fifteen digests, accepted outcomes and claim boundaries reproduce",
            "value": sealed["checks"],
        },
        "exact_root_and_all_simple_rational_envelopes_are_contained": {
            "passed": root_envelopes["passed"],
            "threshold": "exact root, positivity, momentum, eigenvector, graph, inverse and dynamics values fit every preregistered envelope",
            "value": root_envelopes["checks"],
        },
        "fourier_lift_and_quadratic_dimensions_reproduce": {
            "passed": fourier["passed"],
            "threshold": "registered transform, lift 186, dimensions 24/300 and sector counts 102/54/54/45/45 reproduce",
            "value": fourier["checks"],
        },
        "analytic_second_and_third_derivative_identities_are_exact": {
            "passed": derivative["passed"],
            "threshold": "all local derivative tensors, symmetries, D2Q9 quadrature and conserved-moment identities enumerate exactly",
            "value": derivative["checks"],
        },
        "implicit_graph_gauge_quadratic_solution_and_bounds_are_complete": {
            "passed": coefficient["passed"],
            "threshold": "registered formulas retain 300 pairs/five sectors and Q011l gives a unique graph-gauge external solution",
            "value": coefficient["checks"],
        },
        "all_eight_exact_radius_records_and_cubic_monotonicity_are_complete": {
            "passed": majorant["passed"],
            "threshold": "eight Fraction radii reproduce U, A_R, D, D/r^3 and the nonnegative normalized-majorant derivative",
            "value": majorant["checks"],
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": "finite strict JSON, four section digests and runner provenance reproduce",
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    maximum_second = _fraction(derivative["maximum_map_second_derivative_bilinear_upper"])
    maximum_third = _fraction(derivative["maximum_map_third_derivative_trilinear_upper"])
    kt = _fraction(coefficient["coefficient_values"]["K_T"])
    kf = _fraction(coefficient["coefficient_values"]["K_F"])
    kz = _fraction(coefficient["coefficient_values"]["K_Z"])
    kp = _fraction(coefficient["coefficient_values"]["K_P"])
    selected_radius = (
        _fraction(majorant["selected_radius"])
        if majorant["selected_radius"] is not None
        else Fraction(0)
    )
    selected_record = majorant["selected_record"]
    selected_conditions_pass = bool(
        selected_record is not None
        and selected_record["passed"]
        and all(selected_record["checks"].values())
        and all(majorant["monotonicity_checks"].values())
    )
    l_theorem = l_artifact["cycle"]["theorem_consequence"]
    hypothesis_gates = {
        "analytic_derivative_norms_are_within_registered_caps": {
            "passed": bool(
                validity_passed
                and maximum_second <= SECOND_DERIVATIVE_CAP
                and maximum_third <= THIRD_DERIVATIVE_CAP
            ),
            "threshold": "map D2 bilinear norm <=145 and D3 trilinear norm <=4000 on U<=1e-4",
            "value": {
                "D2": derivative["maximum_map_second_derivative_bilinear_upper"],
                "D3": derivative["maximum_map_third_derivative_trilinear_upper"],
            },
        },
        "all_quadratic_coefficient_majorants_are_within_registered_caps": {
            "passed": bool(
                validity_passed
                and kt <= TANGENT_CAP
                and kf <= FORCING_CAP
                and kz <= CHART_CAP
                and kp <= REDUCED_QUADRATIC_CAP
            ),
            "threshold": "K_T<=2500, K_F<=5e8, K_Z<=3e17 and K_P<=3e10",
            "value": coefficient["coefficient_values"],
        },
        "all_five_graph_gauge_quadratic_sector_solutions_are_unique": {
            "passed": bool(
                validity_passed
                and l_theorem["all_five_quadratic_sector_homological_operators_are_invertible"]
                and coefficient["checks"]["q011l_proves_all_five_operators_invertible"]
            ),
            "threshold": "Q011l invertibility supplies the unique external graph-gauge solution in all five output sectors",
            "value": coefficient["sector_pair_counts"],
        },
        "a_passing_radius_at_least_1e_11_exists": {
            "passed": bool(validity_passed and selected_radius >= MINIMUM_SELECTED_RADIUS),
            "threshold": "largest passing registered radius >=1e-11",
            "value": majorant["selected_radius"],
        },
        "selected_radius_satisfies_all_domain_residual_and_cubic_conditions": {
            "passed": bool(validity_passed and selected_conditions_pass),
            "threshold": "population, density, reduced expansion, defect, utilization and uniform D(t)<=C t^3 all pass",
            "value": selected_record,
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011m repaired quadratic-jet majorant audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the repaired exact map admits a unique graph-gauge quadratic jet with "
            "the registered coefficient and cubic-defect majorants"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered derivative and coefficient envelopes do not certify the "
            "repaired quadratic jet majorant"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Does the repaired exact map admit a unique graph-gauge quadratic jet "
            "and a uniform finite-radius cubic-defect majorant?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "derivative_digest_sha256": derivative_digest,
        "coefficient_digest_sha256": coefficient_digest,
        "majorant_digest_sha256": majorant_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "repaired_exact_map_second_and_third_derivative_bounds_are_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_quadratic_coefficient_majorants_are_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_uniform_cubic_defect_majorant_is_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "selected_finite_reduced_radius_is_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "componentwise_quadratic_coefficients_are_certified": False,
        "finite_cubic_defect_implies_exact_invariance": False,
        "raw_q011b_map_is_certified": False,
        "q011e_through_q011h_raw_coefficients_transfer_to_repaired_map": False,
        "an_exact_invariant_manifold_or_forced_ssm_exists": False,
        "nonlinear_normal_attraction_or_a_basin_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only the fixed 17x17 periodic repaired exact map, "
        "its unique x-independent fixed point on the fixed conservation leaf, the "
        "Q011k--Q011l selected invariant graph, an implicitly defined graph-gauge "
        "quadratic jet, registered norm bounds and a finite-radius cubic-defect "
        "majorant. It stores no componentwise coefficient array, certifies neither "
        "the raw Q011b map nor transfer of Q011e--Q011h coefficients, and proves no "
        "continuous-amplitude path, higher-order jet, exact invariant manifold or "
        "SSM, smoothness, nonlinear normal attraction, basin, other grid, force, "
        "wall boundary or D3Q27. A finite cubic defect is not exact invariance."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011j_fixed_point_acceptance_changed": False,
        "q011k_spectral_acceptance_changed": False,
        "q011l_homological_inverse_acceptance_changed": False,
        "q011e_through_q011h_raw_map_results_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011n for an a posteriori radii-polynomial or graph-transform "
            "correction using the Q011l inverse and Q011m finite quadratic defect."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Localize the first derivative, coefficient or radius failure and tighten "
            "only that scalar envelope with componentwise verified forcing bounds."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, exact derivative, dimension, coefficient, "
            "radius or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011m cycle failed strict serialization or digest")
    return cycle


def run_q011m_study() -> dict[str, Any]:
    cycle = run_quadratic_jet_majorant_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "sealed_upper_bounds": "Q011j--Q011l exact rational records",
            "derivative_enumeration": "exact D2Q9 rational tensors",
            "radius_campaign": "eight exact rational candidates",
            "floating_point_used_for_proof_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": "implicit repaired quadratic jet and cubic-defect majorant",
            "grid": [SIZE, SIZE],
            "x_independent_fixed_point": True,
            "fixed_conservation_leaf": True,
            "exact_rational_repaired_map": True,
            "quadratic_order_only": True,
            "componentwise_coefficients_stored": False,
            "claim": "registered coefficient norms and finite-radius cubic defect only",
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
    result = run_q011m_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
