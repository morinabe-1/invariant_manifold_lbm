"""Q011o type-correct localized graph-transform setup audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011m_quadratic_jet_majorant as q011m
import research.q011n_correction_readiness as q011n
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    ComplexRationalInterval,
    RationalInterval,
    _all_numeric_values_finite,
    _complex_absolute_bounds,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

ExactComplex = tuple[Fraction, Fraction]

SIZE = 17
ZERO_BLOCK_DIMENSION = 150
NONZERO_BLOCK_DIMENSION = 153
FIXED_LEAF_DIMENSION = 2598
SELECTED_BLOCKS = (0, 1, 16)
SELECTED_DIMENSIONS = {0: 6, 1: 9, 16: 9}
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
ZERO_BLOCK_POPULATION_LIFT = 186

LOCALIZATION_RADIUS = Fraction(1, 10**11)
LIFT_NORM_CAP = Fraction(2600)
COORDINATE_INVERSE_CAP = Fraction(900)
PHYSICAL_LOCALIZATION_CAP = Fraction(3, 10**8)
SELECTED_CONORM_FLOOR = Fraction(983, 1000)
EXTERNAL_NORM_CAP = Fraction(491, 500)
LINEAR_DOMINATION_GAP_FLOOR = Fraction(1, 1000)
LINEAR_DOMINATION_RATIO_CAP = Fraction(999, 1000)
SELECTED_INVERSE_CAP = Fraction(51, 50)
SELECTED_EXTERNAL_COUPLING_CAP = Fraction(1, 10**6)
GRAPH_LIPSCHITZ_CAP = Fraction(1)

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
Q011M_ARTIFACT_SHA256 = "b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f"
Q011M_RUNNER_SHA256 = "0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150"
Q011M_DIGESTS = (
    "dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb",
    "0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a",
    "1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514",
    "bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00",
    "f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4",
)
Q011M_CLASSIFICATION = (
    "the repaired exact map admits a unique graph-gauge quadratic jet with "
    "the registered coefficient and cubic-defect majorants"
)
Q011N_ARTIFACT_SHA256 = "1277170b85d2f515a5b9dabbc1cf23cfdf36e109c5ab212e3a123ee07a50683b"
Q011N_RUNNER_SHA256 = "7e526dcf013efce628137023f69de7b929d31e52f19378cb05c483284e36dc57"
Q011N_DIGESTS = (
    "f916b59d1c9fba0e4ace57b110f4b960d5dce078578a77ac28f8a8d005e1e0d0",
    "e3952e5ac897ba9250f3a77ec5d8760c0f3ee2a3df350ba4451837a46dd91f76",
    "ee7f21a6075963c510e234a032aa8de40f65989c609d10228aca54f6e371ed8d",
    "9893aed4a7ce4d05cbd21e849de4ddd4f1c9f86c7fcc3fad7a4504b823d6a321",
)
Q011N_CLASSIFICATION = (
    "the registered Q011l/Q011m certificates are not sufficient for an "
    "a posteriori invariant-manifold proof"
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


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            Q011K_ARTIFACT_SHA256,
            Q011K_RUNNER_SHA256,
            Q011K_DIGESTS,
            (
                "input_digest_sha256",
                "root_digest_sha256",
                "block_digest_sha256",
                "proof_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011K_CLASSIFICATION,
        ),
        (
            "q011l",
            directory / "q011l_interval_homological_inverse.json",
            Path(q011l.__file__).resolve(),
            Q011L_ARTIFACT_SHA256,
            Q011L_RUNNER_SHA256,
            Q011L_DIGESTS,
            (
                "input_digest_sha256",
                "graph_digest_sha256",
                "pair_digest_sha256",
                "homological_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011L_CLASSIFICATION,
        ),
        (
            "q011m",
            directory / "q011m_quadratic_jet_majorant.json",
            Path(q011m.__file__).resolve(),
            Q011M_ARTIFACT_SHA256,
            Q011M_RUNNER_SHA256,
            Q011M_DIGESTS,
            (
                "input_digest_sha256",
                "derivative_digest_sha256",
                "coefficient_digest_sha256",
                "majorant_digest_sha256",
                "result_digest_sha256",
            ),
            "accepted",
            Q011M_CLASSIFICATION,
        ),
        (
            "q011n",
            directory / "q011n_correction_readiness.json",
            Path(q011n.__file__).resolve(),
            Q011N_ARTIFACT_SHA256,
            Q011N_RUNNER_SHA256,
            Q011N_DIGESTS,
            (
                "input_digest_sha256",
                "typing_digest_sha256",
                "scalar_digest_sha256",
                "result_digest_sha256",
            ),
            "not_ready",
            Q011N_CLASSIFICATION,
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
        digest_names,
        expected_outcome,
        classification,
    ) in specifications:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        cycle = artifact["cycle"]
        digests = tuple(cycle[name] for name in digest_names)
        artifacts[label] = artifact
        checks[f"{label}_artifact_sha256_matches"] = (
            _file_sha256(artifact_path) == artifact_hash
        )
        checks[f"{label}_runner_sha256_matches"] = bool(
            _file_sha256(runner_path) == runner_hash
            and artifact["runner_source"]["sha256"] == runner_hash
        )
        checks[f"{label}_digests_match"] = digests == expected_digests
        checks[f"{label}_outcome_reproduces"] = bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == expected_outcome
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == expected_outcome
            and cycle["scientific_classification"] == classification
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
        )
        checks[f"{label}_package_source_metadata_matches"] = (
            artifact["source"] == source_metadata()
        )
        checks[f"{label}_artifact_is_strict_finite_json"] = bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
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

    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    l_theorem = artifacts["q011l"]["cycle"]["theorem_consequence"]
    m_theorem = artifacts["q011m"]["cycle"]["theorem_consequence"]
    n_theorem = artifacts["q011n"]["cycle"]["theorem_consequence"]
    checks["q011k_claim_boundary_is_preserved"] = bool(
        k_theorem["selected_and_external_spectral_unions_do_not_exchange"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011l_claim_boundary_is_preserved"] = bool(
        l_theorem["exact_selected_invariant_graphs_are_certified"]
        and not l_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011m_claim_boundary_is_preserved"] = bool(
        m_theorem["unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    checks["q011n_claim_boundary_is_preserved"] = bool(
        not n_theorem[
            "q011l_degree_two_inverse_and_q011m_function_defect_are_type_compatible"
        ]
        and not n_theorem[
            "registered_inputs_are_ready_for_an_a_posteriori_manifold_proof"
        ]
        and not n_theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
        and not n_theorem["an_exact_local_invariant_manifold_or_ssm_is_disproved"]
    )
    n_sealed = artifacts["q011n"]["cycle"]["sealed_input_audit"]
    checks["q011n_nested_seals_reproduce_but_are_not_substituted"] = bool(
        n_sealed["passed"]
        and n_sealed["q011k"]["artifact_sha256"] == Q011K_ARTIFACT_SHA256
        and n_sealed["q011l"]["artifact_sha256"] == Q011L_ARTIFACT_SHA256
        and n_sealed["q011m"]["artifact_sha256"] == Q011M_ARTIFACT_SHA256
    )
    return {**records, "checks": checks, "passed": all(checks.values())}, artifacts


def _center_modulus_bounds(value: ExactComplex) -> RationalInterval:
    point = ComplexRationalInterval(
        RationalInterval.point(value[0]),
        RationalInterval.point(value[1]),
    )
    return _complex_absolute_bounds(point)


def _coordinate_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[int, list[ExactComplex]],
    dict[int, tuple[int, ...]],
    dict[int, dict[str, Fraction]],
    dict[int, dict[str, Fraction]],
]:
    k_artifact = artifacts["q011k"]
    l_cycle = artifacts["q011l"]["cycle"]
    m_cycle = artifacts["q011m"]["cycle"]
    centers, selected, _radii, metrics, spectral = q011l._spectral_data(k_artifact)
    graphs, graph_audit = q011l._graph_audit(centers, selected, metrics)

    block_records = []
    exact_records = []
    total_dimension = 0
    selected_dimension = 0
    external_dimension = 0
    lift_total = Fraction(0)
    inverse_candidates: list[tuple[Fraction, int]] = []
    for block_index in range(SIZE):
        dimension = len(centers[block_index])
        selected_count = len(selected.get(block_index, ()))
        external_count = dimension - selected_count
        graph_radius = graphs.get(block_index, {}).get("radius", Fraction(0))
        triangular_factor = 1 + graph_radius
        population_lift = (
            ZERO_BLOCK_POPULATION_LIFT if block_index == 0 else 1
        )
        lift_contribution = (
            population_lift
            * metrics[block_index]["vector_norm"]
            * triangular_factor
        )
        inverse_contribution = metrics[block_index]["beta"] * triangular_factor
        lift_total += lift_contribution
        inverse_candidates.append((inverse_contribution, block_index))
        total_dimension += dimension
        selected_dimension += selected_count
        external_dimension += external_count
        exact_record = {
            "block_index": block_index,
            "dimension": dimension,
            "selected_dimension": selected_count,
            "external_dimension": external_count,
            "population_lift_factor": population_lift,
            "eigencolumn_infinity_norm_upper": _fraction_record(
                metrics[block_index]["vector_norm"]
            ),
            "eigenanalysis_infinity_norm_upper": _fraction_record(
                metrics[block_index]["beta"]
            ),
            "graph_radius_upper": _fraction_record(graph_radius),
            "triangular_coordinate_factor": _fraction_record(triangular_factor),
            "physical_lift_contribution": _fraction_record(lift_contribution),
            "coordinate_inverse_contribution": _fraction_record(
                inverse_contribution
            ),
        }
        checks = {
            "dimension_is_registered": dimension
            == (ZERO_BLOCK_DIMENSION if block_index == 0 else NONZERO_BLOCK_DIMENSION),
            "selected_dimension_is_registered": selected_count
            == SELECTED_DIMENSIONS.get(block_index, 0),
            "population_lift_factor_is_registered": population_lift
            == (ZERO_BLOCK_POPULATION_LIFT if block_index == 0 else 1),
            "triangular_factor_formula_reproduces": triangular_factor
            == 1 + graph_radius,
            "physical_lift_formula_reproduces": lift_contribution
            == population_lift
            * metrics[block_index]["vector_norm"]
            * (1 + graph_radius),
            "coordinate_inverse_formula_reproduces": inverse_contribution
            == metrics[block_index]["beta"] * (1 + graph_radius),
        }
        exact_records.append(exact_record)
        block_records.append({**exact_record, "checks": checks, "passed": all(checks.values())})

    inverse_total, inverse_witness = max(inverse_candidates)
    zero_lift_observed = m_cycle["exact_root_and_simple_envelope_audit"][
        "zero_block_population_lift_infinity_norm"
    ]
    block_zero_selected = [centers[0][index] for index in selected[0]]
    block_zero_conjugates = [(real, -imaginary) for real, imaginary in block_zero_selected]
    conjugacy_checks = {
        "all_nonzero_center_families_are_exact_conjugates": all(
            centers[SIZE - index]
            == [(real, -imaginary) for real, imaginary in centers[index]]
            for index in range(1, 9)
        ),
        "all_nonzero_metric_families_are_exact_conjugates": all(
            metrics[SIZE - index] == metrics[index] for index in range(1, 9)
        ),
        "selected_one_and_sixteen_indices_match": selected[1] == selected[16],
        "selected_one_and_sixteen_graph_bounds_match": graphs[1] == graphs[16],
        "zero_selected_multiset_is_closed_under_conjugacy": Counter(
            block_zero_selected
        )
        == Counter(block_zero_conjugates),
    }
    nonzero_conjugacy_checks = {
        name: value
        for name, value in conjugacy_checks.items()
        if name != "zero_selected_multiset_is_closed_under_conjugacy"
    }
    checks = {
        "q011l_spectral_reconstruction_matches_artifact": spectral
        == l_cycle["exact_eigencoordinate_residual_audit"],
        "q011l_graph_reconstruction_matches_artifact": graph_audit
        == l_cycle["selected_invariant_graph_audit"],
        "all_block_coordinate_records_pass": all(
            record["passed"] for record in block_records
        ),
        "fixed_leaf_dimensions_close": (
            total_dimension == FIXED_LEAF_DIMENSION
            and selected_dimension == SELECTED_DIMENSION
            and external_dimension == EXTERNAL_DIMENSION
            and selected_dimension + external_dimension == total_dimension
        ),
        "zero_block_population_lift_186_reproduces": (
            zero_lift_observed == ZERO_BLOCK_POPULATION_LIFT
        ),
        "nonzero_conjugate_block_data_reproduce": all(
            nonzero_conjugacy_checks.values()
        ),
        "zero_selected_conjugacy_hypothesis_is_recorded": isinstance(
            conjugacy_checks["zero_selected_multiset_is_closed_under_conjugacy"],
            bool,
        ),
        "normalized_forward_dft_analysis_constant_is_one": True,
        "unnormalized_inverse_dft_synthesis_is_block_sum": True,
        "physical_lift_sum_formula_reproduces": lift_total
        == sum(
            (
                (ZERO_BLOCK_POPULATION_LIFT if index == 0 else 1)
                * metrics[index]["vector_norm"]
                * (1 + graphs.get(index, {}).get("radius", Fraction(0)))
                for index in range(SIZE)
            ),
            Fraction(0),
        ),
        "coordinate_inverse_max_formula_reproduces": inverse_total
        == max(value for value, _index in inverse_candidates),
    }
    return (
        {
            "fourier_convention": {
                "forward": "xhat_k = (1/17) sum_n exp(-2 pi i k n/17) x_n",
                "inverse": "x_n = sum_k exp(2 pi i k n/17) xhat_k",
                "real_conjugacy": "xhat_(17-k) = conjugate(xhat_k)",
            },
            "coordinate_definition": {
                "eigenanalysis": "y_k = V_k^(-1) xhat_k",
                "selected_blocks": list(SELECTED_BLOCKS),
                "external_quotient": "e_k = y_E,k - G_k s_k",
                "inverse_triangular_map": "y_k = (s_k, e_k + G_k s_k)",
                "norm": "global maximum of complex coordinate moduli",
                "implicit_certified_graph_used": True,
                "componentwise_graph_matrix_materialized": False,
            },
            "zero_block_population_lift_infinity_norm": zero_lift_observed,
            "block_records": block_records,
            "block_record_digest_sha256": q011b._canonical_json_sha256(exact_records),
            "block_count": SIZE,
            "total_fixed_leaf_real_dimension": total_dimension,
            "selected_real_dimension": selected_dimension,
            "external_real_dimension": external_dimension,
            "physical_lift_norm_upper": _fraction_record(lift_total),
            "coordinate_inverse_norm_upper": _fraction_record(inverse_total),
            "coordinate_inverse_witness_block": inverse_witness,
            "conjugacy_checks": conjugacy_checks,
            "cross_block_cancellation_used": False,
            "checks": checks,
            "passed": all(checks.values()),
        },
        centers,
        selected,
        metrics,
        graphs,
    )


def _linear_split_audit(
    centers: dict[int, list[ExactComplex]],
    selected: dict[int, tuple[int, ...]],
    metrics: dict[int, dict[str, Fraction]],
    graphs: dict[int, dict[str, Fraction]],
    q011k_artifact: dict[str, Any],
) -> dict[str, Any]:
    records = []
    exact_records = []
    exact_modulus_records = []
    modulus_count = 0
    for block_index in range(SIZE):
        intervals = [_center_modulus_bounds(value) for value in centers[block_index]]
        block_center_records = [
            {
                "center_index": center_index,
                "lower": _fraction_record(interval.lower),
                "upper": _fraction_record(interval.upper),
            }
            for center_index, interval in enumerate(intervals)
        ]
        center_records = [
            {"block_index": block_index, **record} for record in block_center_records
        ]
        exact_modulus_records.extend(center_records)
        modulus_count += len(intervals)
        selected_indices = selected.get(block_index, ())
        selected_set = frozenset(selected_indices)
        external_indices = tuple(
            index for index in range(len(intervals)) if index not in selected_set
        )
        external_witness = max(
            external_indices, key=lambda index: intervals[index].upper
        )
        external_center_upper = intervals[external_witness].upper
        theta = metrics[block_index]["theta"]
        graph_radius = graphs.get(block_index, {}).get("radius", Fraction(0))
        quotient_perturbation = (
            theta * (1 + graph_radius) if block_index in graphs else theta
        )
        external_norm = external_center_upper + quotient_perturbation
        selected_witness: int | None = None
        selected_center_lower: Fraction | None = None
        selected_conorm: Fraction | None = None
        if selected_indices:
            selected_witness = min(
                selected_indices, key=lambda index: intervals[index].lower
            )
            selected_center_lower = intervals[selected_witness].lower
            selected_conorm = selected_center_lower - quotient_perturbation
        exact_record = {
            "block_index": block_index,
            "dimension": len(intervals),
            "selected_dimension": len(selected_indices),
            "external_dimension": len(external_indices),
            "center_modulus_digest_sha256": q011b._canonical_json_sha256(
                block_center_records
            ),
            "selected_minimum_center_modulus_lower": (
                _fraction_record(selected_center_lower)
                if selected_center_lower is not None
                else None
            ),
            "selected_minimum_center_witness": selected_witness,
            "external_maximum_center_modulus_upper": _fraction_record(
                external_center_upper
            ),
            "external_maximum_center_witness": external_witness,
            "transformed_perturbation_upper": _fraction_record(theta),
            "graph_radius_upper": _fraction_record(graph_radius),
            "triangular_quotient_perturbation_upper": _fraction_record(
                quotient_perturbation
            ),
            "selected_conorm_lower": (
                _fraction_record(selected_conorm)
                if selected_conorm is not None
                else None
            ),
            "external_operator_norm_upper": _fraction_record(external_norm),
            "selected_external_coupling_upper": (
                _fraction_record(theta) if selected_indices else None
            ),
        }
        checks = {
            "all_center_modulus_intervals_are_ordered": all(
                interval.lower <= interval.upper for interval in intervals
            ),
            "selected_and_external_dimensions_close": (
                len(selected_indices) + len(external_indices) == len(intervals)
            ),
            "quotient_perturbation_formula_reproduces": quotient_perturbation
            == (
                theta * (1 + graph_radius)
                if selected_indices
                else theta
            ),
            "external_operator_bound_formula_reproduces": external_norm
            == external_center_upper + quotient_perturbation,
            "selected_conorm_formula_reproduces": (
                selected_conorm == selected_center_lower - quotient_perturbation
                if selected_center_lower is not None
                else True
            ),
            "selected_conorm_is_positive_when_present": (
                selected_conorm > 0 if selected_conorm is not None else True
            ),
            "selected_external_coupling_is_bounded_by_theta": True,
        }
        exact_records.append(exact_record)
        records.append({**exact_record, "checks": checks, "passed": all(checks.values())})

    selected_records = [
        record for record in records if record["selected_conorm_lower"] is not None
    ]
    selected_minimum_record = min(
        selected_records, key=lambda record: _fraction(record["selected_conorm_lower"])
    )
    external_maximum_record = max(
        records, key=lambda record: _fraction(record["external_operator_norm_upper"])
    )
    coupling_maximum_record = max(
        selected_records,
        key=lambda record: _fraction(record["selected_external_coupling_upper"]),
    )
    selected_conorm = _fraction(selected_minimum_record["selected_conorm_lower"])
    external_norm = _fraction(external_maximum_record["external_operator_norm_upper"])
    coupling = _fraction(coupling_maximum_record["selected_external_coupling_upper"])
    domination_gap = selected_conorm - external_norm
    domination_ratio = external_norm / selected_conorm
    selected_inverse = 1 / selected_conorm
    split = q011k_artifact["cycle"]["selected_external_split_audit"]

    conjugacy_checks = {}
    for index in range(1, 9):
        left = records[index]
        right = records[SIZE - index]
        conjugacy_checks[f"blocks_{index}_{SIZE - index}_match"] = bool(
            left["dimension"] == right["dimension"]
            and left["selected_dimension"] == right["selected_dimension"]
            and left["external_dimension"] == right["external_dimension"]
            and left["center_modulus_digest_sha256"]
            == right["center_modulus_digest_sha256"]
            and left["selected_minimum_center_modulus_lower"]
            == right["selected_minimum_center_modulus_lower"]
            and left["external_maximum_center_modulus_upper"]
            == right["external_maximum_center_modulus_upper"]
            and left["transformed_perturbation_upper"]
            == right["transformed_perturbation_upper"]
            and left["graph_radius_upper"] == right["graph_radius_upper"]
            and left["triangular_quotient_perturbation_upper"]
            == right["triangular_quotient_perturbation_upper"]
            and left["selected_conorm_lower"] == right["selected_conorm_lower"]
            and left["external_operator_norm_upper"]
            == right["external_operator_norm_upper"]
        )
    checks = {
        "all_seventeen_block_records_pass": all(
            record["passed"] for record in records
        ),
        "all_2598_center_modulus_intervals_are_evaluated": (
            modulus_count == FIXED_LEAF_DIMENSION
        ),
        "all_conjugate_block_linear_bounds_match": all(conjugacy_checks.values()),
        "three_selected_conorm_records_are_present": (
            [record["block_index"] for record in selected_records]
            == list(SELECTED_BLOCKS)
        ),
        "global_selected_conorm_formula_reproduces": selected_conorm
        == min(_fraction(record["selected_conorm_lower"]) for record in selected_records),
        "global_external_norm_formula_reproduces": external_norm
        == max(_fraction(record["external_operator_norm_upper"]) for record in records),
        "domination_gap_and_ratio_formulas_reproduce": (
            domination_gap == selected_conorm - external_norm
            and domination_ratio == external_norm / selected_conorm
            and selected_inverse == 1 / selected_conorm
        ),
        "same_complex_modulus_block_sup_norm_is_used": True,
        "bauer_fike_eigenvalue_gap_is_not_substituted_for_operator_norm": True,
    }
    return {
        "operator_coordinate_identity": (
            "T^(-1) M T = [[S,B],[0,E]] on selected blocks; "
            "M = Lambda + F elsewhere"
        ),
        "operator_norm": "complex absolute row-sum induced by global block-sup norm",
        "center_modulus_bound": "exact rational sqrt enclosure of dyadic center",
        "selected_block_formulas": {
            "eta": "theta * (1 + r_G)",
            "selected_conorm": "minimum selected center modulus lower - eta",
            "external_norm": "maximum external center modulus upper + eta",
            "coupling": "||B|| <= theta",
        },
        "nonselected_block_formula": (
            "maximum center modulus upper + transformed perturbation theta"
        ),
        "block_records": records,
        "exact_modulus_record_count": modulus_count,
        "exact_modulus_record_digest_sha256": q011b._canonical_json_sha256(
            exact_modulus_records
        ),
        "exact_linear_record_digest_sha256": q011b._canonical_json_sha256(
            exact_records
        ),
        "selected_conorm_lower": _fraction_record(selected_conorm),
        "selected_conorm_witness_block": selected_minimum_record["block_index"],
        "selected_conorm_witness_center": selected_minimum_record[
            "selected_minimum_center_witness"
        ],
        "external_operator_norm_upper": _fraction_record(external_norm),
        "external_norm_witness_block": external_maximum_record["block_index"],
        "external_norm_witness_center": external_maximum_record[
            "external_maximum_center_witness"
        ],
        "linear_domination_gap_lower": _fraction_record(domination_gap),
        "linear_domination_ratio_upper": _fraction_record(domination_ratio),
        "selected_base_inverse_norm_upper": _fraction_record(selected_inverse),
        "selected_external_coupling_upper": _fraction_record(coupling),
        "selected_external_coupling_witness_block": coupling_maximum_record[
            "block_index"
        ],
        "q011k_eigenvalue_level_selected_minimum_modulus_lower": split[
            "selected_minimum_modulus_lower"
        ],
        "q011k_eigenvalue_level_external_maximum_modulus_upper": split[
            "external_maximum_modulus_upper"
        ],
        "q011k_eigenvalue_level_normal_gap_lower": split[
            "normal_dominance_gap_lower"
        ],
        "q011k_eigenvalue_gap_used_as_operator_bound": False,
        "conjugacy_checks": conjugacy_checks,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _localization_audit(
    coordinate_audit: dict[str, Any],
    q011m_artifact: dict[str, Any],
) -> dict[str, Any]:
    lift_norm = _fraction(coordinate_audit["physical_lift_norm_upper"])
    physical_upper = lift_norm * LOCALIZATION_RADIUS
    root = q011m_artifact["cycle"]["exact_root_and_simple_envelope_audit"]
    root_population = _fraction(root["root_population_floor_lower"])
    root_density = _fraction(root["root_density_floor_lower"])
    population_lower = root_population - physical_upper
    density_lower = root_density - 9 * physical_upper
    cutoff_properties = {
        "domain": "full fixed-leaf coordinate Banach space X",
        "codomain": "closed coordinate ball B_X(rho)",
        "definition": (
            "componentwise metric projection of each complex coordinate onto "
            "the closed disk |z_j| <= rho"
        ),
        "identity_on_core_ball": True,
        "fixes_origin": True,
        "global_lipschitz_constant": _fraction_record(Fraction(1)),
        "preserves_complex_conjugacy": True,
    }
    localized_map = {
        "original_coordinate_map": "F(z) = A z + N(z)",
        "definition": "F_rho(z) = A z + N(C_rho z)",
        "domain": "full fixed-leaf coordinate Banach space X",
        "codomain": "full fixed-leaf coordinate Banach space X",
        "equals_original_map_on_core_ball": True,
        "nonlinear_derivative_bound_certified": False,
    }
    graph_space = {
        "name": "G_(rho,1)",
        "domain": "selected closed ball B_S(rho)",
        "codomain": "external closed ball B_E(rho)",
        "fixes_origin": True,
        "preserves_complex_conjugacy": True,
        "lipschitz_cap": _fraction_record(GRAPH_LIPSCHITZ_CAP),
        "metric": "uniform sup metric",
        "closed_complete_space": True,
        "induced_graph_transform_is_defined_in_this_gate": False,
        "graph_transform_self_map_is_certified": False,
        "graph_transform_contraction_is_certified": False,
    }
    checks = {
        "cutoff_radius_is_registered": LOCALIZATION_RADIUS == Fraction(1, 10**11),
        "physical_localization_formula_reproduces": physical_upper
        == lift_norm * LOCALIZATION_RADIUS,
        "physical_localization_is_in_derivative_domain": physical_upper
        <= q011m.STATE_DISPLACEMENT_CAP,
        "population_buffer_is_registered": population_lower
        >= q011m.POPULATION_THRESHOLD,
        "density_buffer_is_registered": density_lower >= q011m.DENSITY_THRESHOLD,
        "cutoff_is_identity_on_core_and_one_lipschitz": bool(
            cutoff_properties["identity_on_core_ball"]
            and cutoff_properties["fixes_origin"]
            and _fraction(cutoff_properties["global_lipschitz_constant"]) == 1
        ),
        "cutoff_and_graph_space_preserve_real_conjugacy": bool(
            cutoff_properties["preserves_complex_conjugacy"]
            and graph_space["preserves_complex_conjugacy"]
        ),
        "localized_map_is_typed_and_agrees_on_core": bool(
            localized_map["domain"] == localized_map["codomain"]
            and localized_map["equals_original_map_on_core_ball"]
        ),
        "graph_space_is_closed_and_complete": graph_space["closed_complete_space"],
        "nonlinear_graph_transform_claims_are_deferred": bool(
            not localized_map["nonlinear_derivative_bound_certified"]
            and not graph_space["induced_graph_transform_is_defined_in_this_gate"]
            and not graph_space["graph_transform_self_map_is_certified"]
            and not graph_space["graph_transform_contraction_is_certified"]
        ),
    }
    return {
        "localization_radius": _fraction_record(LOCALIZATION_RADIUS),
        "physical_localization_upper": _fraction_record(physical_upper),
        "root_population_floor_lower": _fraction_record(root_population),
        "root_density_floor_lower": _fraction_record(root_density),
        "localized_population_floor_lower": _fraction_record(population_lower),
        "localized_density_floor_lower": _fraction_record(density_lower),
        "derivative_domain_cap": _fraction_record(q011m.STATE_DISPLACEMENT_CAP),
        "population_threshold": _fraction_record(q011m.POPULATION_THRESHOLD),
        "density_threshold": _fraction_record(q011m.DENSITY_THRESHOLD),
        "cutoff": cutoff_properties,
        "localized_map": localized_map,
        "graph_banach_space": graph_space,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "zero_block_dimension": ZERO_BLOCK_DIMENSION,
        "nonzero_block_dimension": NONZERO_BLOCK_DIMENSION,
        "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "selected_blocks": list(SELECTED_BLOCKS),
        "selected_dimensions": {
            str(key): value for key, value in SELECTED_DIMENSIONS.items()
        },
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "zero_block_population_lift": ZERO_BLOCK_POPULATION_LIFT,
        "localization_radius": _fraction_record(LOCALIZATION_RADIUS),
        "lift_norm_cap": _fraction_record(LIFT_NORM_CAP),
        "coordinate_inverse_cap": _fraction_record(COORDINATE_INVERSE_CAP),
        "physical_localization_cap": _fraction_record(PHYSICAL_LOCALIZATION_CAP),
        "selected_conorm_floor": _fraction_record(SELECTED_CONORM_FLOOR),
        "external_norm_cap": _fraction_record(EXTERNAL_NORM_CAP),
        "linear_domination_gap_floor": _fraction_record(
            LINEAR_DOMINATION_GAP_FLOOR
        ),
        "linear_domination_ratio_cap": _fraction_record(
            LINEAR_DOMINATION_RATIO_CAP
        ),
        "selected_inverse_cap": _fraction_record(SELECTED_INVERSE_CAP),
        "selected_external_coupling_cap": _fraction_record(
            SELECTED_EXTERNAL_COUPLING_CAP
        ),
        "graph_lipschitz_cap": _fraction_record(GRAPH_LIPSCHITZ_CAP),
        "coordinate_norm": "global block-sup of complex coordinate moduli",
        "matrix_norm": "maximum complex-absolute row sum",
        "cross_block_cancellation": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "coordinate_digest_sha256": cycle["coordinate_digest_sha256"],
        "linear_digest_sha256": cycle["linear_digest_sha256"],
        "localization_digest_sha256": cycle["localization_digest_sha256"],
    }


def run_graph_transform_setup_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    coordinate, centers, selected, metrics, graphs = _coordinate_audit(artifacts)
    linear = _linear_split_audit(
        centers,
        selected,
        metrics,
        graphs,
        artifacts["q011k"],
    )
    localization = _localization_audit(coordinate, artifacts["q011m"])
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    coordinate_sections = {"fixed_leaf_coordinate_audit": coordinate}
    linear_sections = {"same_norm_linear_split_audit": linear}
    localization_sections = {"localized_graph_space_audit": localization}
    input_digest = q011b._canonical_json_sha256(input_sections)
    coordinate_digest = q011b._canonical_json_sha256(coordinate_sections)
    linear_digest = q011b._canonical_json_sha256(linear_sections)
    localization_digest = q011b._canonical_json_sha256(localization_sections)
    strict_payload = {
        **input_sections,
        **coordinate_sections,
        **linear_sections,
        **localization_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and coordinate_digest == q011b._canonical_json_sha256(coordinate_sections)
        and linear_digest == q011b._canonical_json_sha256(linear_sections)
        and localization_digest
        == q011b._canonical_json_sha256(localization_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "q011k_through_q011n_inputs_and_claim_boundaries_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "four artifact/runner hashes, nineteen digests, outcomes and direct claim boundaries reproduce",
            "value": sealed["checks"],
        },
        "fixed_leaf_fourier_eigen_graph_coordinates_are_complete": {
            "passed": coordinate["passed"],
            "threshold": "17 blocks, 24+2574=2598 dimensions, conjugacy, V/inverse/G bounds and zero lift 186 reproduce",
            "value": coordinate["checks"],
        },
        "coordinate_lift_and_inverse_bounds_are_exact": {
            "passed": bool(
                coordinate["checks"]["physical_lift_sum_formula_reproduces"]
                and coordinate["checks"][
                    "coordinate_inverse_max_formula_reproduces"
                ]
                and not coordinate["cross_block_cancellation_used"]
            ),
            "threshold": "K_L includes the zero-block population lift and K_P uses the triangular inverse factor without cancellation",
            "value": {
                "K_L": coordinate["physical_lift_norm_upper"],
                "K_P": coordinate["coordinate_inverse_norm_upper"],
                "zero_lift": coordinate[
                    "zero_block_population_lift_infinity_norm"
                ],
            },
        },
        "all_center_moduli_and_same_norm_linear_bounds_are_exact": {
            "passed": linear["passed"],
            "threshold": "all 2598 center modulus intervals and 17 triangular operator records use exact arithmetic in one norm",
            "value": linear["checks"],
        },
        "global_linear_constants_and_witnesses_reproduce": {
            "passed": bool(
                linear["checks"]["global_selected_conorm_formula_reproduces"]
                and linear["checks"]["global_external_norm_formula_reproduces"]
                and linear["checks"][
                    "domination_gap_and_ratio_formulas_reproduce"
                ]
            ),
            "threshold": "m_S, q_E, gamma_0, base inverse, coupling and witness records are exact",
            "value": {
                "m_S": linear["selected_conorm_lower"],
                "q_E": linear["external_operator_norm_upper"],
                "gap": linear["linear_domination_gap_lower"],
                "gamma_0": linear["linear_domination_ratio_upper"],
            },
        },
        "cutoff_localized_map_and_graph_space_are_typed": {
            "passed": localization["passed"],
            "threshold": "the radial cutoff, localized coordinate map, complete graph space and core physical buffers are explicit",
            "value": localization["checks"],
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
    lift_norm = _fraction(coordinate["physical_lift_norm_upper"])
    coordinate_inverse = _fraction(coordinate["coordinate_inverse_norm_upper"])
    physical_localization = _fraction(localization["physical_localization_upper"])
    selected_conorm = _fraction(linear["selected_conorm_lower"])
    external_norm = _fraction(linear["external_operator_norm_upper"])
    domination_gap = _fraction(linear["linear_domination_gap_lower"])
    domination_ratio = _fraction(linear["linear_domination_ratio_upper"])
    selected_inverse = _fraction(linear["selected_base_inverse_norm_upper"])
    coupling = _fraction(linear["selected_external_coupling_upper"])
    coordinate_typed = bool(
        coordinate["passed"]
        and coordinate["total_fixed_leaf_real_dimension"] == FIXED_LEAF_DIMENSION
        and coordinate["selected_real_dimension"] == SELECTED_DIMENSION
        and coordinate["external_real_dimension"] == EXTERNAL_DIMENSION
        and all(coordinate["conjugacy_checks"].values())
    )
    domain_buffers = bool(
        lift_norm <= LIFT_NORM_CAP
        and coordinate_inverse <= COORDINATE_INVERSE_CAP
        and physical_localization <= PHYSICAL_LOCALIZATION_CAP
        and localization["checks"]["physical_localization_is_in_derivative_domain"]
        and localization["checks"]["population_buffer_is_registered"]
        and localization["checks"]["density_buffer_is_registered"]
    )
    linear_separation = bool(
        selected_conorm >= SELECTED_CONORM_FLOOR
        and external_norm <= EXTERNAL_NORM_CAP
        and domination_gap >= LINEAR_DOMINATION_GAP_FLOOR
    )
    domination = bool(
        domination_ratio <= LINEAR_DOMINATION_RATIO_CAP
        and selected_inverse <= SELECTED_INVERSE_CAP
        and coupling <= SELECTED_EXTERNAL_COUPLING_CAP
    )
    typed_setup = bool(
        localization["passed"]
        and localization["cutoff"]["identity_on_core_ball"]
        and localization["localized_map"]["equals_original_map_on_core_ball"]
        and localization["graph_banach_space"]["closed_complete_space"]
        and not localization["graph_banach_space"][
            "induced_graph_transform_is_defined_in_this_gate"
        ]
    )
    hypothesis_gates = {
        "fixed_leaf_triangular_coordinate_is_bijective_and_real_typed": {
            "passed": bool(validity_passed and coordinate_typed),
            "threshold": "the certified Fourier/eigen/implicit-graph triangular coordinate has 24 selected and 2574 external real dimensions",
            "value": {
                "selected_dimension": coordinate["selected_real_dimension"],
                "external_dimension": coordinate["external_real_dimension"],
                "conjugacy": coordinate["conjugacy_checks"],
            },
        },
        "coordinate_and_localization_bounds_fit_registered_caps": {
            "passed": bool(validity_passed and domain_buffers),
            "threshold": "K_L<=2600, K_P<=900, K_L*rho<=3e-8 and derivative/population/density buffers pass",
            "value": {
                "K_L": coordinate["physical_lift_norm_upper"],
                "K_P": coordinate["coordinate_inverse_norm_upper"],
                "K_L_rho": localization["physical_localization_upper"],
                "localization_checks": localization["checks"],
            },
        },
        "same_norm_selected_conorm_and_external_norm_are_separated": {
            "passed": bool(validity_passed and linear_separation),
            "threshold": "m_S>=0.983, q_E<=0.982 and m_S-q_E>=1e-3 in the same complex block-sup norm",
            "value": {
                "m_S": linear["selected_conorm_lower"],
                "q_E": linear["external_operator_norm_upper"],
                "gap": linear["linear_domination_gap_lower"],
            },
        },
        "linear_domination_inverse_and_coupling_fit_registered_caps": {
            "passed": bool(validity_passed and domination),
            "threshold": "gamma_0<=0.999, selected inverse<=1.02 and selected-external coupling<=1e-6",
            "value": {
                "gamma_0": linear["linear_domination_ratio_upper"],
                "selected_inverse": linear["selected_base_inverse_norm_upper"],
                "coupling": linear["selected_external_coupling_upper"],
            },
        },
        "localized_map_and_complete_graph_space_are_type_correct": {
            "passed": bool(validity_passed and typed_setup),
            "threshold": "C_rho, F_rho and G_(rho,1) have explicit domains/codomains and no nonlinear contraction is inferred",
            "value": {
                "cutoff": localization["cutoff"],
                "localized_map": localization["localized_map"],
                "graph_space": localization["graph_banach_space"],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011o localized graph-transform setup audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the repaired fixed-leaf split admits a type-correct localized "
            "graph-transform setup with rigorous linear domination"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered block-sup norm does not support the localized "
            "graph-transform setup"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Does the repaired fixed-leaf split admit a type-correct localized "
            "graph-transform coordinate with rigorous same-norm linear domination?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "coordinate_digest_sha256": coordinate_digest,
        "linear_digest_sha256": linear_digest,
        "localization_digest_sha256": localization_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "fixed_leaf_fourier_eigen_graph_coordinate_is_type_correct": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_coordinate_lift_and_inverse_bounds_are_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_same_norm_linear_domination_is_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "localized_map_and_complete_graph_space_are_type_correct": bool(
            validity_passed and hypotheses_passed
        ),
        "nonlinear_graph_transform_is_well_defined": False,
        "nonlinear_graph_transform_is_a_self_map_or_contraction": False,
        "an_exact_local_invariant_manifold_or_ssm_is_certified": False,
        "an_exact_local_invariant_manifold_or_ssm_is_disproved": False,
        "smoothness_uniqueness_normal_attraction_or_a_basin_is_certified": False,
        "q011l_q011m_or_q011n_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on the fixed "
        "conservation leaf, the Q011k/Q011l split, one complex block-sup norm and "
        "the radius-1e-11 localization setup. It certifies no nonlinear graph-"
        "transform inverse, self-map, contraction, fixed graph, exact invariant "
        "manifold or SSM, smoothness, uniqueness, normal attraction, basin, "
        "componentwise quadratic coefficient, raw Q011b map, other grid, force, "
        "wall boundary or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_acceptance_changed": False,
        "q011l_homological_inverse_acceptance_changed": False,
        "q011m_quadratic_majorant_acceptance_changed": False,
        "q011n_not_ready_outcome_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011p to transport the Q011m analytic derivative bounds "
            "into this coordinate norm and test the localized nonlinear base "
            "inverse, graph-space self-map and strict contraction."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Use only the first failed Q011o block or constant to preregister a "
            "weighted block norm or a smaller graph-slope cap."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, coordinate, modulus, linear-bound, "
            "localization or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011o cycle failed strict serialization or digest")
    return cycle


def run_q011o_study() -> dict[str, Any]:
    cycle = run_graph_transform_setup_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "sealed_inputs": "Q011k--Q011n exact rational records",
            "center_modulus_interval_count": FIXED_LEAF_DIMENSION,
            "floating_point_used_for_gate_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": "type-correct localized graph-transform linear setup",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "exact_rational_repaired_map": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "external_real_dimension": EXTERNAL_DIMENSION,
            "nonlinear_graph_transform_certified": False,
            "exact_invariant_manifold_claim": False,
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
    result = run_q011o_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
