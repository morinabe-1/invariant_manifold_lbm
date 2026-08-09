"""Q011n a posteriori correction-readiness and scalar-obstruction audit."""

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
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OUTPUT_SECTORS = (0, 1, 16, 2, 15)
EXPECTED_SECTOR_PAIR_COUNTS = {0: 102, 1: 54, 16: 54, 2: 45, 15: 45}
EXPECTED_PAIR_COUNT = 300
EXPECTED_RADIUS_COUNT = 8
EXPECTED_RADIUS_RECORD_DIGEST = (
    "dd14364d4c60d8c47bf593538a414178db440a6a25e226088a69332188618f52"
)
EXPECTED_SELECTED_RADIUS = Fraction(1, 10**11)

ZERO_BLOCK_LIFT_NORM = 186
AMBIENT_INVERSE_ENVELOPES = {
    0: Fraction(3_400_000),
    1: Fraction(24_000),
    16: Fraction(24_000),
    2: Fraction(2_300_000),
    15: Fraction(2_300_000),
}
TOTAL_INVERSE_SURROGATE = Fraction(637_048_000)
SECOND_DERIVATIVE_CAP = Fraction(145)
HALF_THIRD_DERIVATIVE_CAP = Fraction(2000)
CONTRACTION_CAP = Fraction(1, 2)
STATE_DOMAIN_CAP = Fraction(1, 10**4)
ROOT_POPULATION_FLOOR = Fraction(27, 1000)
ROOT_DENSITY_FLOOR = Fraction(999, 1000)
POPULATION_THRESHOLD = Fraction(1, 50)
DENSITY_THRESHOLD = Fraction(99, 100)

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
        (
            "q011m",
            directory / "q011m_quadratic_jet_majorant.json",
            Path(q011m.__file__).resolve(),
            Q011M_ARTIFACT_SHA256,
            Q011M_RUNNER_SHA256,
            Q011M_DIGESTS,
            Q011M_CLASSIFICATION,
            (
                "input_digest_sha256",
                "derivative_digest_sha256",
                "coefficient_digest_sha256",
                "majorant_digest_sha256",
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

    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    l_theorem = artifacts["q011l"]["cycle"]["theorem_consequence"]
    m_theorem = artifacts["q011m"]["cycle"]["theorem_consequence"]
    checks["q011k_claim_boundary_is_preserved"] = (
        k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
        and not k_theorem["nonnormal_homological_inverse_is_certified"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011l_claim_boundary_is_preserved"] = (
        l_theorem["all_five_quadratic_sector_homological_operators_are_invertible"]
        and not l_theorem["repaired_quadratic_jet_or_coefficients_are_certified"]
        and not l_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011m_claim_boundary_is_preserved"] = (
        m_theorem["unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors"]
        and m_theorem["registered_uniform_cubic_defect_majorant_is_rigorous"]
        and not m_theorem["finite_cubic_defect_implies_exact_invariance"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    m_sealed = artifacts["q011m"]["cycle"]["sealed_input_audit"]
    checks["q011m_nested_q011k_and_q011l_seals_reproduce"] = (
        m_sealed["passed"]
        and m_sealed["q011k"]["artifact_sha256"] == Q011K_ARTIFACT_SHA256
        and m_sealed["q011l"]["artifact_sha256"] == Q011L_ARTIFACT_SHA256
    )
    audit = {**records, "checks": checks, "passed": all(checks.values())}
    return audit, artifacts["q011k"], artifacts["q011l"], artifacts["q011m"]


def _operator_typing_audit(
    q011k_artifact: dict[str, Any],
    q011l_artifact: dict[str, Any],
    q011m_artifact: dict[str, Any],
) -> dict[str, Any]:
    l_cycle = q011l_artifact["cycle"]
    m_cycle = q011m_artifact["cycle"]
    sector_records = l_cycle["sector_homological_inverse_audit"]["sector_records"]
    sector_counts = {
        record["output_sector"]: record["pair_dimension"] for record in sector_records
    }
    proof_objects = {
        "exact_repaired_fixed_point": q011k_artifact["cycle"]["theorem_consequence"][
            "exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"
        ],
        "exact_selected_external_spectral_split": q011k_artifact["cycle"][
            "theorem_consequence"
        ]["selected_and_external_spectral_unions_do_not_exchange"],
        "exact_selected_linear_invariant_graph": l_cycle["theorem_consequence"][
            "exact_selected_invariant_graphs_are_certified"
        ],
        "degree_two_homological_inverse": l_cycle["theorem_consequence"][
            "all_five_quadratic_sector_homological_operators_are_invertible"
        ],
        "implicit_quadratic_jet": m_cycle["theorem_consequence"][
            "unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors"
        ],
        "finite_cubic_defect_majorant": m_cycle["theorem_consequence"][
            "registered_uniform_cubic_defect_majorant_is_rigorous"
        ],
        "specified_a_posteriori_theorem": False,
        "banach_function_space_and_norm": False,
        "full_linearized_invariance_inverse": False,
        "all_degree_or_analytic_tail_bound": False,
        "self_contained_graph_transform_contraction": False,
        "typed_defect_to_correction_map": False,
    }
    available = [name for name, value in proof_objects.items() if value]
    missing = [name for name, value in proof_objects.items() if not value]
    checks = {
        "degree_two_pair_and_sector_domains_reproduce": (
            sector_counts == EXPECTED_SECTOR_PAIR_COUNTS
            and sum(sector_counts.values()) == EXPECTED_PAIR_COUNT
        ),
        "q011l_operator_is_explicitly_degree_two_only": (
            l_cycle["registered_parameters"]["symmetric_basis"]
            == "unscaled lexicographic i <= j"
            and l_cycle["quadratic_pair_family_audit"]["unordered_pair_count"]
            == EXPECTED_PAIR_COUNT
        ),
        "q011m_defect_is_a_function_with_degree_three_remainder": (
            m_cycle["cubic_defect_radius_audit"]["uniform_conclusion"].startswith(
                "D(t) <="
            )
            and not m_cycle["theorem_consequence"][
                "finite_cubic_defect_implies_exact_invariance"
            ]
        ),
        "degree_two_inverse_is_not_declared_a_full_function_inverse": (
            not proof_objects["full_linearized_invariance_inverse"]
            and not proof_objects["typed_defect_to_correction_map"]
        ),
        "both_registered_theorem_routes_are_marked_missing": (
            not proof_objects["all_degree_or_analytic_tail_bound"]
            and not proof_objects["self_contained_graph_transform_contraction"]
        ),
    }
    return {
        "q011l_operator": {
            "name": "H_q^(2)(Z) = E_q Z - Z K_q(S)",
            "degree": 2,
            "total_monomial_columns": EXPECTED_PAIR_COUNT,
            "sector_pair_dimensions": {
                str(key): value for key, value in sector_counts.items()
            },
            "domain": "five external-by-degree-two-monomial matrix spaces",
            "codomain": "the same five external-by-degree-two-monomial matrix spaces",
        },
        "q011m_defect": {
            "name": "E^[2](a) = Phi(W^[2](a)) - W^[2](R^[2](a))",
            "minimum_degree": 3,
            "domain": "the registered 24-coordinate reduced l-infinity ball",
            "codomain": "full repaired fixed-leaf population state",
            "bound": "uniform scalar D(r) in physical population l-infinity norm",
        },
        "invalid_unregistered_composition": "(H^(2))^(-1) E^[2] is undefined",
        "acceptable_future_routes": [
            "full linearized invariance inverse plus analytic coefficient tail",
            "self-contained selected/external graph-transform contraction",
        ],
        "proof_object_matrix": proof_objects,
        "available_proof_objects": available,
        "missing_proof_objects": missing,
        "first_missing_proof_object": missing[0],
        "checks": checks,
        "passed": all(checks.values()),
    }


def _inverse_surrogate_audit(q011m_artifact: dict[str, Any]) -> dict[str, Any]:
    m_cycle = q011m_artifact["cycle"]
    observed = _fraction(
        m_cycle["implicit_quadratic_jet_coefficient_audit"][
            "ambient_inverse_sector_sum"
        ]
    )
    reconstructed = (
        ZERO_BLOCK_LIFT_NORM * AMBIENT_INVERSE_ENVELOPES[0]
        + sum(
            (AMBIENT_INVERSE_ENVELOPES[sector] for sector in OUTPUT_SECTORS[1:]),
            Fraction(0),
        )
    )
    checks = {
        "five_registered_sector_envelopes_are_present": (
            tuple(AMBIENT_INVERSE_ENVELOPES) == OUTPUT_SECTORS
        ),
        "zero_sector_population_lift_is_included": ZERO_BLOCK_LIFT_NORM == 186,
        "registered_formula_reproduces": reconstructed == TOTAL_INVERSE_SURROGATE,
        "q011m_inverse_sum_reproduces_exactly": observed == reconstructed,
        "surrogate_is_not_typed_as_a_function_inverse": True,
    }
    return {
        "zero_block_population_lift": ZERO_BLOCK_LIFT_NORM,
        "sector_envelopes": {
            str(key): _fraction_record(value)
            for key, value in AMBIENT_INVERSE_ENVELOPES.items()
        },
        "formula": "C_I = 186*3.4e6 + 2*2.4e4 + 2*2.3e6",
        "reconstructed_total_inverse_surrogate": _fraction_record(reconstructed),
        "q011m_observed_total_inverse_surrogate": _fraction_record(observed),
        "interpretation": (
            "cross-sector scalar triangle surrogate assembled from degree-two output "
            "bounds; not a full function-space inverse"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _scalar_surrogate_audit(q011m_artifact: dict[str, Any]) -> dict[str, Any]:
    campaign = q011m_artifact["cycle"]["cubic_defect_radius_audit"]
    input_records = campaign["radius_records"]
    records: list[dict[str, Any]] = []
    exact_records: list[dict[str, Any]] = []
    passing: list[Fraction] = []
    failure_counter: Counter[str] = Counter()
    for source in input_records:
        radius = _fraction(source["radius"])
        displacement = _fraction(source["state_displacement_upper"])
        defect = _fraction(source["cubic_defect_upper"])
        derivative_variation = (
            SECOND_DERIVATIVE_CAP * displacement
            + HALF_THIRD_DERIVATIVE_CAP * displacement**2
        )
        newton_y = TOTAL_INVERSE_SURROGATE * defect
        contraction_z = TOTAL_INVERSE_SURROGATE * derivative_variation
        correction_radius = 2 * newton_y
        state_with_correction = displacement + correction_radius
        population_lower = ROOT_POPULATION_FLOOR - state_with_correction
        density_lower = ROOT_DENSITY_FLOOR - 9 * state_with_correction
        radii_margin = correction_radius - (
            newton_y + contraction_z * correction_radius
        )
        correction_utilization = correction_radius / displacement
        checks = {
            "q011m_original_candidate_passed": source["passed"],
            "formal_contraction_is_below_one_half": contraction_z < CONTRACTION_CAP,
            "formal_radii_inequality_is_strict": radii_margin > 0,
            "corrected_state_is_in_derivative_domain": (
                state_with_correction <= STATE_DOMAIN_CAP
            ),
            "corrected_population_and_density_buffers_are_positive": (
                population_lower >= POPULATION_THRESHOLD
                and density_lower >= DENSITY_THRESHOLD
            ),
            "correction_does_not_exceed_chart_state": correction_radius <= displacement,
        }
        passed = all(checks.values())
        if passed:
            passing.append(radius)
        for name, value in checks.items():
            if not value:
                failure_counter[name] += 1
        exact_record = {
            "radius": _fraction_record(radius),
            "q011m_original_candidate_passed": source["passed"],
            "state_displacement_upper": _fraction_record(displacement),
            "cubic_defect_upper": _fraction_record(defect),
            "derivative_variation_surrogate": _fraction_record(derivative_variation),
            "newton_y_surrogate": _fraction_record(newton_y),
            "contraction_z_surrogate": _fraction_record(contraction_z),
            "correction_radius_tau": _fraction_record(correction_radius),
            "state_with_correction_upper": _fraction_record(state_with_correction),
            "population_with_correction_lower": _fraction_record(population_lower),
            "density_with_correction_lower": _fraction_record(density_lower),
            "radii_inequality_margin": _fraction_record(radii_margin),
            "correction_to_chart_state_utilization": _fraction_record(
                correction_utilization
            ),
        }
        exact_records.append(exact_record)
        records.append({**exact_record, "checks": checks, "passed": passed})

    selected = max(passing) if passing else None
    minimum_z = min(records, key=lambda item: _fraction(item["contraction_z_surrogate"]))
    minimum_utilization = min(
        records,
        key=lambda item: _fraction(item["correction_to_chart_state_utilization"]),
    )
    first_record = records[0]
    first_failed_constraints = [
        name for name, value in first_record["checks"].items() if not value
    ]
    source_radii = [_fraction(record["radius"]) for record in input_records]
    checks = {
        "all_eight_q011m_radius_records_are_reused": (
            len(records) == len(source_radii) == EXPECTED_RADIUS_COUNT
        ),
        "q011m_radius_order_is_unchanged": source_radii == list(q011m.RADIUS_CANDIDATES),
        "q011m_selected_radius_is_unchanged": (
            _fraction(campaign["selected_radius"]) == EXPECTED_SELECTED_RADIUS
        ),
        "q011m_exact_radius_digest_is_unchanged": (
            campaign["exact_radius_record_digest_sha256"]
            == EXPECTED_RADIUS_RECORD_DIGEST
        ),
        "all_surrogate_formulas_are_exact": all(
            _fraction(record["correction_radius_tau"])
            == 2 * _fraction(record["newton_y_surrogate"])
            for record in records
        ),
        "failure_counts_cover_every_nonpassing_condition": (
            sum(failure_counter.values())
            == sum(
                1
                for record in records
                for value in record["checks"].values()
                if not value
            )
        ),
    }
    return {
        "scalar_surrogate_only": True,
        "typed_a_posteriori_theorem_consequence": False,
        "formulas": {
            "V": "145 U + 2000 U^2",
            "Y": "C_I D",
            "Z": "C_I V",
            "tau": "2 Y",
            "radii_margin": "tau - (Y + Z tau)",
        },
        "radius_records": records,
        "exact_scalar_record_digest_sha256": q011b._canonical_json_sha256(exact_records),
        "passing_radius_count": len(passing),
        "selected_radius": _fraction_record(selected) if selected is not None else None,
        "first_candidate_record": first_record,
        "first_candidate_failed_constraints": first_failed_constraints,
        "minimum_contraction_z": minimum_z["contraction_z_surrogate"],
        "minimum_contraction_z_radius": minimum_z["radius"],
        "minimum_correction_utilization": minimum_utilization[
            "correction_to_chart_state_utilization"
        ],
        "minimum_correction_utilization_radius": minimum_utilization["radius"],
        "constraint_failure_counts": dict(sorted(failure_counter.items())),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "output_sectors": list(OUTPUT_SECTORS),
        "expected_sector_pair_counts": {
            str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()
        },
        "expected_pair_count": EXPECTED_PAIR_COUNT,
        "expected_radius_count": EXPECTED_RADIUS_COUNT,
        "expected_q011m_selected_radius": _fraction_record(EXPECTED_SELECTED_RADIUS),
        "total_inverse_surrogate": _fraction_record(TOTAL_INVERSE_SURROGATE),
        "second_derivative_cap": _fraction_record(SECOND_DERIVATIVE_CAP),
        "half_third_derivative_cap": _fraction_record(
            HALF_THIRD_DERIVATIVE_CAP
        ),
        "formal_contraction_cap": _fraction_record(CONTRACTION_CAP),
        "state_domain_cap": _fraction_record(STATE_DOMAIN_CAP),
        "root_population_floor": _fraction_record(ROOT_POPULATION_FLOOR),
        "root_density_floor": _fraction_record(ROOT_DENSITY_FLOOR),
        "population_threshold": _fraction_record(POPULATION_THRESHOLD),
        "density_threshold": _fraction_record(DENSITY_THRESHOLD),
        "correction_radius_rule": "tau = 2Y",
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "typing_digest_sha256": cycle["typing_digest_sha256"],
        "scalar_digest_sha256": cycle["scalar_digest_sha256"],
    }


def run_correction_readiness_audit() -> dict[str, Any]:
    sealed, k_artifact, l_artifact, m_artifact = _sealed_input_audit()
    typing = _operator_typing_audit(k_artifact, l_artifact, m_artifact)
    inverse = _inverse_surrogate_audit(m_artifact)
    scalar = _scalar_surrogate_audit(m_artifact)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    typing_sections = {
        "operator_typing_audit": typing,
        "inverse_surrogate_audit": inverse,
    }
    scalar_sections = {"scalar_correction_obstruction_audit": scalar}
    input_digest = q011b._canonical_json_sha256(input_sections)
    typing_digest = q011b._canonical_json_sha256(typing_sections)
    scalar_digest = q011b._canonical_json_sha256(scalar_sections)
    strict_payload = {
        **input_sections,
        **typing_sections,
        **scalar_sections,
        "runner_source": runner,
    }
    digests_reproduce = (
        input_digest == q011b._canonical_json_sha256(input_sections)
        and typing_digest == q011b._canonical_json_sha256(typing_sections)
        and scalar_digest == q011b._canonical_json_sha256(scalar_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "q011k_q011l_q011m_inputs_and_claim_boundaries_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "three artifact/runner hashes, fifteen digests, accepted outcomes, nested seals and claim boundaries reproduce",
            "value": sealed["checks"],
        },
        "degree_two_operator_and_function_defect_types_are_distinguished": {
            "passed": typing["passed"],
            "threshold": "Q011l degree-two matrix spaces and Q011m degree-three-and-higher function defect have separate domains/codomains",
            "value": typing["checks"],
        },
        "five_sector_total_inverse_surrogate_reproduces": {
            "passed": inverse["passed"],
            "threshold": "registered sector envelopes and zero-wave lift give C_I=637048000 exactly",
            "value": inverse["checks"],
        },
        "all_q011m_radius_records_are_reused_unchanged": {
            "passed": bool(
                scalar["checks"]["all_eight_q011m_radius_records_are_reused"]
                and scalar["checks"]["q011m_radius_order_is_unchanged"]
                and scalar["checks"]["q011m_selected_radius_is_unchanged"]
                and scalar["checks"]["q011m_exact_radius_digest_is_unchanged"]
            ),
            "threshold": "all eight exact radius records, order, selected radius and source digest reproduce",
            "value": {
                key: scalar["checks"][key]
                for key in (
                    "all_eight_q011m_radius_records_are_reused",
                    "q011m_radius_order_is_unchanged",
                    "q011m_selected_radius_is_unchanged",
                    "q011m_exact_radius_digest_is_unchanged",
                )
            },
        },
        "all_scalar_surrogate_records_and_conditions_are_exact": {
            "passed": scalar["passed"],
            "threshold": "V, Y, Z, tau, six conditions and failure counts use exact Fraction arithmetic",
            "value": scalar["checks"],
        },
        "scalar_surrogate_is_not_promoted_to_a_theorem": {
            "passed": bool(
                scalar["scalar_surrogate_only"]
                and not scalar["typed_a_posteriori_theorem_consequence"]
                and typing["invalid_unregistered_composition"]
                == "(H^(2))^(-1) E^[2] is undefined"
            ),
            "threshold": "the scalar pass/fail is explicitly neither an existence nor a nonexistence theorem",
            "value": {
                "scalar_surrogate_only": scalar["scalar_surrogate_only"],
                "typed_theorem_consequence": scalar[
                    "typed_a_posteriori_theorem_consequence"
                ],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": "finite strict JSON, three section digests and runner provenance reproduce",
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    proof_objects = typing["proof_object_matrix"]
    scalar_candidate_exists = scalar["passing_radius_count"] > 0
    selected_record = (
        next(
            record
            for record in scalar["radius_records"]
            if scalar["selected_radius"] is not None
            and record["radius"] == scalar["selected_radius"]
        )
        if scalar_candidate_exists
        else None
    )
    selected_buffers_pass = bool(
        selected_record is not None
        and selected_record["checks"]["corrected_state_is_in_derivative_domain"]
        and selected_record["checks"][
            "corrected_population_and_density_buffers_are_positive"
        ]
        and selected_record["checks"]["correction_does_not_exceed_chart_state"]
    )
    theorem_specified = bool(
        proof_objects["specified_a_posteriori_theorem"]
        and proof_objects["banach_function_space_and_norm"]
    )
    typed_contraction = bool(
        proof_objects["full_linearized_invariance_inverse"]
        and proof_objects["all_degree_or_analytic_tail_bound"]
        or proof_objects["self_contained_graph_transform_contraction"]
    )
    typed_hypothesis_mapping = bool(
        theorem_specified
        and typed_contraction
        and proof_objects["typed_defect_to_correction_map"]
    )
    hypothesis_gates = {
        "a_posteriori_theorem_banach_space_norm_domain_and_gauge_are_fixed": {
            "passed": bool(validity_passed and theorem_specified),
            "threshold": "one applicable theorem and its Banach space, norm, domain and graph gauge are explicit",
            "value": {
                "specified_theorem": proof_objects["specified_a_posteriori_theorem"],
                "banach_space_and_norm": proof_objects[
                    "banach_function_space_and_norm"
                ],
            },
        },
        "typed_full_inverse_with_tail_or_graph_transform_contraction_exists": {
            "passed": bool(validity_passed and typed_contraction),
            "threshold": "either a full invariance inverse plus tail or a self-contained graph transform is rigorous",
            "value": {
                "full_inverse": proof_objects["full_linearized_invariance_inverse"],
                "analytic_tail": proof_objects["all_degree_or_analytic_tail_bound"],
                "graph_transform": proof_objects[
                    "self_contained_graph_transform_contraction"
                ],
            },
        },
        "at_least_one_registered_radius_passes_all_scalar_conditions": {
            "passed": bool(validity_passed and scalar_candidate_exists),
            "threshold": "at least one of the unchanged eight radii passes all six formal scalar conditions",
            "value": {
                "passing_radius_count": scalar["passing_radius_count"],
                "selected_radius": scalar["selected_radius"],
            },
        },
        "same_candidate_has_strict_chart_and_correction_buffers": {
            "passed": bool(validity_passed and selected_buffers_pass),
            "threshold": "the selected scalar candidate retains state, population, density and relative-correction buffers",
            "value": selected_record,
        },
        "defect_derivative_and_arithmetic_map_to_typed_theorem_hypotheses": {
            "passed": bool(validity_passed and typed_hypothesis_mapping),
            "threshold": "defect, derivative variation and exact arithmetic have a type-correct map to every theorem hypothesis",
            "value": {
                "theorem_specified": theorem_specified,
                "typed_contraction": typed_contraction,
                "typed_defect_to_correction_map": proof_objects[
                    "typed_defect_to_correction_map"
                ],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011n correction-readiness audit is invalid"
    elif hypotheses_passed:
        outcome = "ready"
        classification = (
            "the registered repaired quadratic chart is ready for an a posteriori "
            "invariant-manifold proof"
        )
    else:
        outcome = "not_ready"
        classification = (
            "the registered Q011l/Q011m certificates are not sufficient for an "
            "a posteriori invariant-manifold proof"
        )
    failed_hypotheses = [
        name for name, gate in hypothesis_gates.items() if not gate["passed"]
    ]
    cycle: dict[str, Any] = {
        "question": (
            "Do the Q011l degree-two inverse and Q011m finite cubic defect form a "
            "type-correct, quantitatively closed a posteriori invariant-manifold proof?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "typing_digest_sha256": typing_digest,
        "scalar_digest_sha256": scalar_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": failed_hypotheses,
        "first_missing_proof_object": typing["first_missing_proof_object"],
        "first_scalar_candidate_failed_constraints": scalar[
            "first_candidate_failed_constraints"
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "q011l_degree_two_inverse_and_q011m_function_defect_are_type_compatible": False,
        "registered_scalar_surrogate_closes_on_a_q011m_radius": bool(
            validity_passed and scalar_candidate_exists
        ),
        "registered_inputs_are_ready_for_an_a_posteriori_manifold_proof": bool(
            validity_passed and hypotheses_passed
        ),
        "an_exact_local_invariant_manifold_or_ssm_is_certified": False,
        "an_exact_local_invariant_manifold_or_ssm_is_disproved": False,
        "q011l_homological_inverse_acceptance_is_changed": False,
        "q011m_quadratic_majorant_acceptance_is_changed": False,
        "nonlinear_normal_attraction_or_a_basin_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only theorem readiness of the fixed 17x17 repaired exact "
        "map using the Q011k split, Q011l degree-two homological inverse and Q011m "
        "quadratic chart/finite defect. The scalar surrogate is neither a full "
        "function-space inverse nor an existence or nonexistence theorem. This gate "
        "constructs no higher-degree coefficient, analytic tail, graph transform, "
        "exact invariant manifold or SSM, smoothness, nonlinear normal attraction, "
        "basin, other grid, force, wall boundary or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_acceptance_changed": False,
        "q011l_homological_inverse_acceptance_changed": False,
        "q011m_quadratic_majorant_acceptance_changed": False,
    }
    if outcome == "ready":
        cycle["next_change"] = (
            "Instantiate the registered theorem with a separately sealed correction "
            "solve without changing the Q011n radius or thresholds."
        )
    elif outcome == "not_ready":
        cycle["next_change"] = (
            "Preregister Q011o for a type-correct selected/external graph-transform "
            "space with coordinate lift/inverse, linear conorm/external norm and "
            "cutoff/localization bounds before tightening scalar forcing estimates."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, operator-typing, radius-reproduction, "
            "scalar-arithmetic or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011n cycle failed strict serialization or digest")
    return cycle


def run_q011n_study() -> dict[str, Any]:
    cycle = run_correction_readiness_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "sealed_inputs": "Q011k--Q011m exact rational records",
            "scalar_candidate_count": EXPECTED_RADIUS_COUNT,
            "floating_point_used_for_gate_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": "a posteriori theorem readiness and scalar obstruction",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "exact_rational_repaired_map": True,
            "degree_two_inverse_only": True,
            "full_function_space_inverse": False,
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
    result = run_q011n_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
