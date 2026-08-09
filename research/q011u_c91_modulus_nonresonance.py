"""Q011u C91 localization and modulus-only nonresonance audit."""

from __future__ import annotations

import argparse
import json
from bisect import bisect_right
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011j_interval_fixed_point as q011j
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011m_quadratic_jet_majorant as q011m
import research.q011o_graph_transform_setup as q011o
import research.q011t_c1_tangent_graph as q011t
import ttim_lbm.direct_nonresonance as q007i
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574

SMOOTHNESS_ORDER = 91
CUTOFF_POWER = 16
CUTOFF_INNER_SCALE = 2
CUTOFF_TRANSITION_END = 4
CUTOFF_SUPPORT_FACTOR = 4
EXPECTED_CUTOFF_COEFFICIENT_COUNT = 92

DEGREE_START = 3
DEGREE_END = 90
TAIL_DEGREE = 91
EXPECTED_DEGREE_COUNT = 88
EXPECTED_AGGREGATE_COUNT = 3_049_486
EXPECTED_EXPANDED_PRODUCT_COUNT = 927_048_276
EXPECTED_SELECTED_GROUP_COUNT = 4
EXPECTED_SELECTED_MULTIPLICITIES = (8, 4, 4, 8)
EXPECTED_EXTERNAL_GROUP_COUNT = 186

LOG_SERIES_TERMS = 96
LOG_INTERNAL_DECIMAL_DIGITS = 110
LOG_FINAL_DECIMAL_DIGITS = 60
MAXIMUM_LOG_TAIL_BOUND = Fraction(1, 10**90)
MINIMUM_LOG_GAP = Fraction(1, 10**12)
TAIL_RATIO_CAP = Fraction(999, 1000)

Q007I_SOURCE_SHA256 = "22209c56184eff9556db13b553cb89644eea11ffd77a3af69d0316a747118294"

Q011J_ARTIFACT_SHA256 = "74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a"
Q011J_RUNNER_SHA256 = "23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5"
Q011J_DIGESTS = (
    "a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799",
    "adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b",
    "177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f",
    "1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0",
    "ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934",
)
Q011J_DIGEST_NAMES = (
    "input_digest_sha256",
    "coordinate_digest_sha256",
    "oracle_digest_sha256",
    "proof_digest_sha256",
    "result_digest_sha256",
)
Q011J_CLASSIFICATION = (
    "the repaired periodic forcing admits a locally unique exact fixed-leaf fixed point "
    "in the registered rational box"
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
Q011K_DIGEST_NAMES = (
    "input_digest_sha256",
    "root_digest_sha256",
    "block_digest_sha256",
    "proof_digest_sha256",
    "result_digest_sha256",
)
Q011K_CLASSIFICATION = (
    "the exact repaired fixed point has a rigorously stable and quadratically "
    "nonresonant selected/external spectral split"
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
Q011M_DIGEST_NAMES = (
    "input_digest_sha256",
    "derivative_digest_sha256",
    "coefficient_digest_sha256",
    "majorant_digest_sha256",
    "result_digest_sha256",
)
Q011M_CLASSIFICATION = (
    "the repaired exact map admits a unique graph-gauge quadratic jet with the "
    "registered coefficient and cubic-defect majorants"
)

Q011T_ARTIFACT_SHA256 = "7848a915f384a4b51c93fa8201bf357b01cedcec52590defacd15ba22bf99fe2"
Q011T_RUNNER_SHA256 = "b6eff63f29a4274502923a31b98fd774b89d1f21512c5e181c124f493efc8f10"
Q011T_DIGESTS = (
    "79864489c522a7d50e7534091c283167de3b11d9af58365164b7084095a972eb",
    "5c194baab4c8be74cba91c398037839c6b313f80123416819cc6aedf7bf027d2",
    "6d7e09295d3b60d07d4abe9d658fea506752e20300e87e8d1c4158f5f0772bec",
    "ba1cf6a77e95a52cba33d360632bfae0967a4d8b947daf04761dbfbd7926fcb9",
    "d899cf7872d69b5adf75cddc9c0dafe42930ff53130099a8bdb5b7cb1b04559c",
    "ac1019fd526cd4f21caddfb27d4cd8e0c4f7b312a742b84dbc3b3605ee827231",
)
Q011T_DIGEST_NAMES = (
    "input_digest_sha256",
    "cutoff_digest_sha256",
    "graph_digest_sha256",
    "radius_digest_sha256",
    "spectral_digest_sha256",
    "result_digest_sha256",
)
Q011T_CLASSIFICATION = (
    "the original repaired exact map has a certified C1 forward-invariant graph patch "
    "tangent to the selected real spectral subspace"
)

ACCEPTED_CLASSIFICATION = (
    "the repaired exact map satisfies the registered C91 spectral-subspace "
    "nonresonance certificate"
)
REJECTED_CLASSIFICATION = (
    "the C91 localization and degree-91 tail are certified, but modulus-only "
    "nonresonance through degree 90 is obstructed"
)


@dataclass(frozen=True, slots=True)
class _ModulusEntry:
    lower: Fraction
    upper: Fraction
    identifier: str
    selected: bool


@dataclass(slots=True)
class _MergedModulusInterval:
    lower: Fraction
    upper: Fraction
    identifiers: list[str]


@dataclass(frozen=True, slots=True)
class _ScaledLogInterval:
    lower: int
    upper: int


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


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011j",
            directory / "q011j_interval_fixed_point.json",
            Path(q011j.__file__).resolve(),
            Q011J_ARTIFACT_SHA256,
            Q011J_RUNNER_SHA256,
            Q011J_DIGESTS,
            Q011J_DIGEST_NAMES,
            Q011J_CLASSIFICATION,
        ),
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            Q011K_ARTIFACT_SHA256,
            Q011K_RUNNER_SHA256,
            Q011K_DIGESTS,
            Q011K_DIGEST_NAMES,
            Q011K_CLASSIFICATION,
        ),
        (
            "q011m",
            directory / "q011m_quadratic_jet_majorant.json",
            Path(q011m.__file__).resolve(),
            Q011M_ARTIFACT_SHA256,
            Q011M_RUNNER_SHA256,
            Q011M_DIGESTS,
            Q011M_DIGEST_NAMES,
            Q011M_CLASSIFICATION,
        ),
        (
            "q011t",
            directory / "q011t_c1_tangent_graph.json",
            Path(q011t.__file__).resolve(),
            Q011T_ARTIFACT_SHA256,
            Q011T_RUNNER_SHA256,
            Q011T_DIGESTS,
            Q011T_DIGEST_NAMES,
            Q011T_CLASSIFICATION,
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
        classification,
    ) in specifications:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        cycle = artifact["cycle"]
        digests = _digest_tuple(cycle, digest_names)
        artifacts[label] = artifact
        checks[f"{label}_artifact_sha256_matches"] = (
            _file_sha256(artifact_path) == artifact_hash
        )
        checks[f"{label}_runner_sha256_matches"] = bool(
            _file_sha256(runner_path) == runner_hash
            and artifact["runner_source"]["sha256"] == runner_hash
        )
        checks[f"{label}_digests_match"] = digests == expected_digests
        checks[f"{label}_accepted_outcome_reproduces"] = bool(
            cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and cycle["scientific_classification"] == classification
        )
        checks[f"{label}_package_source_metadata_matches"] = (
            artifact["source"] == source_metadata()
        )
        checks[f"{label}_artifact_is_strict_finite_json"] = bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        )
        records[label] = {
            "filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_sha256": _file_sha256(runner_path),
            "digests": list(digests),
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        }

    j_theorem = artifacts["q011j"]["cycle"]["theorem_consequence"]
    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    m_theorem = artifacts["q011m"]["cycle"]["theorem_consequence"]
    t_theorem = artifacts["q011t"]["cycle"]["theorem_consequence"]
    checks["q011j_fixed_point_scope_is_preserved"] = bool(
        j_theorem["repaired_exact_full_17x17_x_independent_fixed_point_exists"]
        and not j_theorem["rigorous_fixed_leaf_spectrum_is_certified"]
        and not j_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011k_spectral_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011m_analytic_derivative_scope_is_preserved"] = bool(
        m_theorem["repaired_exact_map_second_and_third_derivative_bounds_are_certified"]
        and m_theorem["registered_uniform_cubic_defect_majorant_is_rigorous"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    checks["q011t_c1_graph_and_missing_degree_scope_is_preserved"] = bool(
        t_theorem["the_original_map_has_a_forward_invariant_c1_graph_patch"]
        and t_theorem["a_rigorous_spectral_quotient_bracket_is_certified"]
        and not t_theorem["c2_or_higher_smoothness_is_certified"]
        and not t_theorem["all_nonresonances_through_the_spectral_quotient_are_certified"]
        and not t_theorem["spectral_quotient_ssm_uniqueness_is_certified"]
    )
    log_source_path = Path(q007i.__file__).resolve()
    log_source_hash = _file_sha256(log_source_path)
    checks["q007i_rational_log_source_sha256_matches"] = (
        log_source_hash == Q007I_SOURCE_SHA256
    )
    checks["q007i_registered_log_parameters_match"] = bool(
        q007i.LOG_SERIES_TERMS == LOG_SERIES_TERMS
        and q007i.LOG_INTERNAL_DECIMAL_DIGITS == LOG_INTERNAL_DECIMAL_DIGITS
        and q007i.LOG_FINAL_DECIMAL_DIGITS == LOG_FINAL_DECIMAL_DIGITS
        and q007i.MAXIMUM_LOG_TAIL_BOUND == MAXIMUM_LOG_TAIL_BOUND
        and q007i.MINIMUM_LOG_GAP == MINIMUM_LOG_GAP
    )
    checks["twenty_one_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 21
    )
    audit = {
        **records,
        "q007i_rational_log_source": {
            "filename": log_source_path.name,
            "sha256": log_source_hash,
            "series_terms": q007i.LOG_SERIES_TERMS,
            "internal_outward_decimal_digits": q007i.LOG_INTERNAL_DECIMAL_DIGITS,
            "final_outward_decimal_digits": q007i.LOG_FINAL_DECIMAL_DIGITS,
        },
        "direct_digest_count": 21,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _falling_factorial(value: int, order: int) -> int:
    if order > value:
        return 0
    return factorial(value) // factorial(value - order)


def _polynomial_derivative_at(
    coefficients: dict[int, Fraction],
    order: int,
    point: int,
) -> Fraction:
    return sum(
        coefficient * _falling_factorial(exponent, order) * point ** (exponent - order)
        for exponent, coefficient in coefficients.items()
        if exponent >= order
    )


def _c91_cutoff_audit() -> dict[str, Any]:
    p = SMOOTHNESS_ORDER
    normalizer = Fraction(factorial(2 * p + 1), factorial(p) ** 2)
    coefficients = {
        p + index + 1: (
            normalizer * (-1) ** index * comb(p, index) / (p + index + 1)
        )
        for index in range(p + 1)
    }
    coefficient_records = [
        {
            "exponent": exponent,
            "coefficient": _fraction_record(coefficient),
        }
        for exponent, coefficient in sorted(coefficients.items())
    ]
    derivative_identity = all(
        coefficients[p + index + 1] * (p + index + 1)
        == normalizer * (-1) ** index * comb(p, index)
        for index in range(p + 1)
    )
    endpoint_records = [
        {
            "derivative_order": order,
            "at_zero": _fraction_record(_polynomial_derivative_at(coefficients, order, 0)),
            "at_one": _fraction_record(_polynomial_derivative_at(coefficients, order, 1)),
        }
        for order in range(1, p + 1)
    ]
    endpoint_flat = all(
        _fraction(record["at_zero"]) == 0 and _fraction(record["at_one"]) == 0
        for record in endpoint_records
    )
    value_at_zero = _polynomial_derivative_at(coefficients, 0, 0)
    value_at_one = _polynomial_derivative_at(coefficients, 0, 1)
    identity_ratio = Fraction(COORDINATE_SLOT_COUNT, 2**CUTOFF_POWER)
    exact_record = {
        "smoothness_order": p,
        "normalizer": _fraction_record(normalizer),
        "coefficient_records": coefficient_records,
        "endpoint_derivative_record_digest_sha256": q011b._canonical_json_sha256(
            endpoint_records
        ),
        "identity_ratio_upper": _fraction_record(identity_ratio),
        "support_factor": CUTOFF_SUPPORT_FACTOR,
    }
    polynomial = {
        "definition": (
            "S_91(y)=c_91*integral_0^y u^91(1-u)^91 du, "
            "c_91=183!/(91!)^2"
        ),
        "normalizer": _fraction_record(normalizer),
        "coefficient_count": len(coefficient_records),
        "coefficient_records": coefficient_records,
        "value_at_zero": _fraction_record(value_at_zero),
        "value_at_one": _fraction_record(value_at_one),
        "factored_derivative": "S_91'(y)=c_91*y^91*(1-y)^91",
        "derivative_identity_reproduces": derivative_identity,
        "endpoint_derivative_order_range": [1, p],
        "endpoint_derivative_count": len(endpoint_records),
        "all_endpoint_derivatives_are_zero": endpoint_flat,
        "endpoint_derivative_record_digest_sha256": q011b._canonical_json_sha256(
            endpoint_records
        ),
        "monotone_on_closed_unit_interval_by_factored_derivative": True,
        "range_on_closed_unit_interval": [0, 1],
    }
    cutoff = {
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "coordinate_norm": (
            "complex-modulus block-sup norm restricted to the conjugacy-fixed real space"
        ),
        "scalar_power_function": "t_r(z)=sum_j (abs(z_j)/(2r))^16",
        "transition_definition": "chi_91(t)=1-S_91((t-1)/3) for 1<t<4",
        "localized_map": "C_r^(91)(z)=chi_91(t_r(z))*z",
        "identity_ratio_upper": _fraction_record(identity_ratio),
        "identity_on_closed_radius_r_ball": True,
        "support_factor_upper": CUTOFF_SUPPORT_FACTOR,
        "support_is_contained_in_closed_radius_four_r_ball": True,
        "is_c91_across_both_transition_endpoints": endpoint_flat,
        "preserves_conjugacy_fixed_real_space": True,
        "preserves_selected_and_external_real_subspaces": True,
        "quantitative_high_derivative_graph_transform_cap_is_claimed": False,
        "q011t_graph_equality_is_claimed": False,
    }
    checks = {
        "registered_order_and_ninety_two_coefficients_reproduce": bool(
            p == 91 and len(coefficient_records) == EXPECTED_CUTOFF_COEFFICIENT_COUNT
        ),
        "normalizer_and_integrated_derivative_identity_are_exact": bool(
            normalizer == Fraction(factorial(183), factorial(91) ** 2)
            and derivative_identity
        ),
        "endpoint_values_are_zero_and_one": value_at_zero == 0 and value_at_one == 1,
        "derivatives_one_through_ninety_one_are_flat_at_both_endpoints": endpoint_flat,
        "factored_derivative_proves_unit_interval_range": bool(
            polynomial["monotone_on_closed_unit_interval_by_factored_derivative"]
            and value_at_zero == 0
            and value_at_one == 1
        ),
        "identity_ratio_is_strict_and_support_factor_is_four": bool(
            identity_ratio < 1
            and COORDINATE_SLOT_COUNT <= 2**CUTOFF_POWER
            and CUTOFF_INNER_SCALE == 2
            and CUTOFF_TRANSITION_END == 4
            and CUTOFF_SUPPORT_FACTOR == 4
        ),
        "scalar_symmetric_cutoff_is_c91_and_preserves_real_typing": bool(
            cutoff["is_c91_across_both_transition_endpoints"]
            and cutoff["preserves_conjugacy_fixed_real_space"]
            and cutoff["preserves_selected_and_external_real_subspaces"]
        ),
        "no_high_derivative_cap_or_q011t_graph_equality_is_substituted": bool(
            not cutoff["quantitative_high_derivative_graph_transform_cap_is_claimed"]
            and not cutoff["q011t_graph_equality_is_claimed"]
        ),
        "exact_cutoff_record_is_finite_strict_json": bool(
            _all_numeric_values_finite(exact_record)
            and _strict_json_serializable(exact_record)
            and json.dumps(exact_record, allow_nan=False)
        ),
    }
    return {
        "beta_polynomial": polynomial,
        "scalar_c91_localization": cutoff,
        "exact_cutoff_record_digest_sha256": q011b._canonical_json_sha256(exact_record),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _merge_modulus_entries(
    entries: list[_ModulusEntry],
) -> tuple[_MergedModulusInterval, ...]:
    ordered = sorted(entries, key=lambda item: (item.lower, item.upper, item.identifier))
    merged: list[_MergedModulusInterval] = []
    for entry in ordered:
        if merged and entry.lower <= merged[-1].upper:
            merged[-1].upper = max(merged[-1].upper, entry.upper)
            merged[-1].identifiers.append(entry.identifier)
        else:
            merged.append(
                _MergedModulusInterval(
                    lower=entry.lower,
                    upper=entry.upper,
                    identifiers=[entry.identifier],
                )
            )
    return tuple(merged)


def _merged_modulus_records(
    merged: tuple[_MergedModulusInterval, ...],
) -> list[dict[str, Any]]:
    records = []
    for index, interval in enumerate(merged):
        membership = sorted(interval.identifiers)
        records.append(
            {
                "merged_index": index,
                "modulus_lower": _fraction_record(interval.lower),
                "modulus_upper": _fraction_record(interval.upper),
                "source_interval_count": len(membership),
                "membership_digest_sha256": q011b._canonical_json_sha256(membership),
                "first_identifiers": membership[:8],
            }
        )
    return records


def _spectral_compression_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[_MergedModulusInterval, ...],
    tuple[_MergedModulusInterval, ...],
]:
    k_artifact = artifacts["q011k"]
    centers, selected, radii, _metrics, reconstruction = q011l._spectral_data(k_artifact)
    selected_sets = {
        block_index: set(center_indices) for block_index, center_indices in selected.items()
    }
    entries: list[_ModulusEntry] = []
    digest_records: list[dict[str, Any]] = []
    block_records: list[dict[str, Any]] = []
    modulus_cache: dict[tuple[Fraction, Fraction], RationalInterval] = {}
    for block_index in range(SIZE):
        block_entries: list[dict[str, Any]] = []
        selected_count = 0
        for center_index, center in enumerate(centers[block_index]):
            modulus_key = (abs(center[0]), abs(center[1]))
            if modulus_key not in modulus_cache:
                modulus_cache[modulus_key] = q011o._center_modulus_bounds(center)
            center_modulus = modulus_cache[modulus_key]
            radius = radii[block_index]
            lower = max(Fraction(0), center_modulus.lower - radius)
            upper = center_modulus.upper + radius
            is_selected = center_index in selected_sets.get(block_index, set())
            selected_count += int(is_selected)
            identifier = f"block={block_index};center={center_index}"
            entry = _ModulusEntry(lower, upper, identifier, is_selected)
            entries.append(entry)
            record = {
                "block_index": block_index,
                "center_index": center_index,
                "selected": is_selected,
                "modulus_lower": _fraction_record(lower),
                "modulus_upper": _fraction_record(upper),
            }
            digest_records.append(record)
            block_entries.append(record)
        block_records.append(
            {
                "block_index": block_index,
                "dimension": len(centers[block_index]),
                "selected_count": selected_count,
                "external_count": len(centers[block_index]) - selected_count,
                "bauer_fike_radius_upper": _fraction_record(radii[block_index]),
                "modulus_interval_digest_sha256": q011b._canonical_json_sha256(
                    block_entries
                ),
            }
        )

    selected_entries = [entry for entry in entries if entry.selected]
    external_entries = [entry for entry in entries if not entry.selected]
    selected_merged = _merge_modulus_entries(selected_entries)
    external_merged = _merge_modulus_entries(external_entries)
    selected_records = _merged_modulus_records(selected_merged)
    external_records = _merged_modulus_records(external_merged)
    selected_gaps = [
        selected_merged[index + 1].lower - selected_merged[index].upper
        for index in range(len(selected_merged) - 1)
    ]
    external_gaps = [
        external_merged[index + 1].lower - external_merged[index].upper
        for index in range(len(external_merged) - 1)
    ]
    selected_multiplicities = tuple(len(group.identifiers) for group in selected_merged)
    all_strictly_positive_and_stable = all(0 < entry.lower <= entry.upper < 1 for entry in entries)
    exact_compression_record = {
        "individual_interval_digest_sha256": q011b._canonical_json_sha256(digest_records),
        "selected_merged_records": selected_records,
        "external_merged_records": external_records,
    }
    checks = {
        "q011l_reconstructs_all_seventeen_blocks": bool(
            reconstruction["passed"]
            and len(centers) == SIZE
            and [len(centers[index]) for index in range(SIZE)] == [150] + [153] * 16
        ),
        "all_2598_modulus_intervals_reconstruct": len(entries) == COORDINATE_SLOT_COUNT,
        "selected_and_external_counts_are_24_and_2574": bool(
            len(selected_entries) == SELECTED_DIMENSION
            and len(external_entries) == EXTERNAL_DIMENSION
        ),
        "every_modulus_interval_is_strictly_positive_and_stable": (
            all_strictly_positive_and_stable
        ),
        "selected_intervals_merge_to_four_registered_multiplicities": bool(
            len(selected_merged) == EXPECTED_SELECTED_GROUP_COUNT
            and selected_multiplicities == EXPECTED_SELECTED_MULTIPLICITIES
        ),
        "external_intervals_merge_to_186_components": (
            len(external_merged) == EXPECTED_EXTERNAL_GROUP_COUNT
        ),
        "all_selected_and_external_component_gaps_are_strict": bool(
            selected_gaps
            and external_gaps
            and min(selected_gaps) > 0
            and min(external_gaps) > 0
        ),
        "compression_record_is_finite_strict_json": bool(
            _all_numeric_values_finite(exact_compression_record)
            and _strict_json_serializable(exact_compression_record)
            and json.dumps(exact_compression_record, allow_nan=False)
        ),
    }
    audit = {
        "modulus_interval_formula": (
            "[center_modulus_lower-r_BF,center_modulus_upper+r_BF]"
        ),
        "block_records": block_records,
        "individual_modulus_interval_count": len(entries),
        "selected_individual_interval_count": len(selected_entries),
        "external_individual_interval_count": len(external_entries),
        "selected_merged_interval_count": len(selected_merged),
        "selected_group_multiplicities": list(selected_multiplicities),
        "external_merged_interval_count": len(external_merged),
        "selected_merged_records": selected_records,
        "external_merged_records": external_records,
        "minimum_selected_component_gap": _fraction_record(min(selected_gaps)),
        "minimum_external_component_gap": _fraction_record(min(external_gaps)),
        "exact_individual_modulus_interval_digest_sha256": q011b._canonical_json_sha256(
            digest_records
        ),
        "exact_compression_record_digest_sha256": q011b._canonical_json_sha256(
            exact_compression_record
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, selected_merged, external_merged


def _scaled_log_interval(modulus: _MergedModulusInterval) -> tuple[_ScaledLogInterval, Fraction]:
    lower_proof = q007i.rational_log_point(modulus.lower)
    upper_proof = q007i.rational_log_point(modulus.upper)
    log_interval = RationalInterval(
        lower_proof.interval.lower,
        upper_proof.interval.upper,
    )
    scale = 10**LOG_FINAL_DECIMAL_DIGITS
    lower_scaled = log_interval.lower * scale
    upper_scaled = log_interval.upper * scale
    if lower_scaled.denominator != 1 or upper_scaled.denominator != 1:
        raise RuntimeError("Q011u logarithm endpoint is not on the registered grid")
    return (
        _ScaledLogInterval(int(lower_scaled), int(upper_scaled)),
        max(lower_proof.tail_bound, upper_proof.tail_bound),
    )


def _scaled_log_record(value: _ScaledLogInterval) -> dict[str, Any]:
    return {
        "lower_scaled_integer": str(value.lower),
        "upper_scaled_integer": str(value.upper),
        "scale_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
    }


def _rational_log_audit(
    selected_merged: tuple[_MergedModulusInterval, ...],
    external_merged: tuple[_MergedModulusInterval, ...],
) -> tuple[
    dict[str, Any],
    tuple[_ScaledLogInterval, ...],
    tuple[_ScaledLogInterval, ...],
]:
    maximum_tail = Fraction(0)
    selected_logs: list[_ScaledLogInterval] = []
    selected_records = []
    for index, group in enumerate(selected_merged):
        scaled, tail = _scaled_log_interval(group)
        maximum_tail = max(maximum_tail, tail)
        selected_logs.append(scaled)
        selected_records.append(
            {
                "selected_type_index": index,
                "source_interval_count": len(group.identifiers),
                "modulus_lower": _fraction_record(group.lower),
                "modulus_upper": _fraction_record(group.upper),
                "log_interval": _scaled_log_record(scaled),
                "maximum_endpoint_tail_bound": _fraction_record(tail),
                "membership_digest_sha256": q011b._canonical_json_sha256(
                    sorted(group.identifiers)
                ),
            }
        )

    external_logs: list[_ScaledLogInterval] = []
    external_records = []
    for index, group in enumerate(external_merged):
        scaled, tail = _scaled_log_interval(group)
        maximum_tail = max(maximum_tail, tail)
        external_logs.append(scaled)
        external_records.append(
            {
                "external_group_index": index,
                "source_interval_count": len(group.identifiers),
                "modulus_lower": _fraction_record(group.lower),
                "modulus_upper": _fraction_record(group.upper),
                "log_interval": _scaled_log_record(scaled),
                "maximum_endpoint_tail_bound": _fraction_record(tail),
                "membership_digest_sha256": q011b._canonical_json_sha256(
                    sorted(group.identifiers)
                ),
                "first_identifiers": sorted(group.identifiers)[:8],
            }
        )

    selected_strict = all(
        selected_logs[index].upper < selected_logs[index + 1].lower
        for index in range(len(selected_logs) - 1)
    )
    external_strict = all(
        external_logs[index].upper < external_logs[index + 1].lower
        for index in range(len(external_logs) - 1)
    )
    exact_record = {
        "selected_log_records": selected_records,
        "external_log_records": external_records,
    }
    checks = {
        "sealed_q007i_log_parameters_reproduce": bool(
            q007i.LOG_SERIES_TERMS == LOG_SERIES_TERMS
            and q007i.LOG_INTERNAL_DECIMAL_DIGITS == LOG_INTERNAL_DECIMAL_DIGITS
            and q007i.LOG_FINAL_DECIMAL_DIGITS == LOG_FINAL_DECIMAL_DIGITS
        ),
        "all_190_merged_modulus_intervals_are_logged": bool(
            len(selected_logs) == EXPECTED_SELECTED_GROUP_COUNT
            and len(external_logs) == EXPECTED_EXTERNAL_GROUP_COUNT
        ),
        "all_log_endpoints_are_ordered_negative_grid_integers": all(
            interval.lower <= interval.upper < 0
            for interval in (*selected_logs, *external_logs)
        ),
        "log_transport_preserves_all_strict_component_gaps": bool(
            selected_strict and external_strict
        ),
        "maximum_endpoint_tail_fits_registered_cap": maximum_tail <= MAXIMUM_LOG_TAIL_BOUND,
        "log_record_is_finite_strict_json": bool(
            _all_numeric_values_finite(exact_record)
            and _strict_json_serializable(exact_record)
            and json.dumps(exact_record, allow_nan=False)
        ),
    }
    audit = {
        "series_terms": LOG_SERIES_TERMS,
        "internal_outward_decimal_digits": LOG_INTERNAL_DECIMAL_DIGITS,
        "final_outward_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
        "maximum_endpoint_tail_bound": _fraction_record(maximum_tail),
        "selected_log_records": selected_records,
        "external_log_records": external_records,
        "exact_log_record_digest_sha256": q011b._canonical_json_sha256(exact_record),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, tuple(selected_logs), tuple(external_logs)


def _overlap_witness(
    degree: int,
    counts: tuple[int, int, int, int],
    aggregate_lower: int,
    aggregate_upper: int,
    external_index: int,
    external_logs: tuple[_ScaledLogInterval, ...],
    external_merged: tuple[_MergedModulusInterval, ...],
) -> dict[str, Any]:
    membership = sorted(external_merged[external_index].identifiers)
    return {
        "degree": degree,
        "selected_type_counts": list(counts),
        "aggregate_log_interval": _scaled_log_record(
            _ScaledLogInterval(aggregate_lower, aggregate_upper)
        ),
        "external_group_index": external_index,
        "external_log_interval": _scaled_log_record(external_logs[external_index]),
        "external_source_interval_count": len(membership),
        "external_membership_digest_sha256": q011b._canonical_json_sha256(membership),
        "external_first_identifiers": membership[:8],
    }


def _enumeration_audit(
    selected_logs: tuple[_ScaledLogInterval, ...],
    external_logs: tuple[_ScaledLogInterval, ...],
    external_merged: tuple[_MergedModulusInterval, ...],
) -> tuple[dict[str, Any], Fraction]:
    if len(selected_logs) != EXPECTED_SELECTED_GROUP_COUNT:
        raise ValueError("Q011u requires four selected log-modulus types")
    if len(external_logs) != len(external_merged):
        raise ValueError("Q011u external log and modulus groups disagree")
    starts = [interval.lower for interval in external_logs]
    total_aggregates = 0
    total_expanded = 0
    total_overlaps = 0
    global_minimum_gap_scaled: int | None = None
    global_minimum_gap_witness: dict[str, Any] | None = None
    first_overlap: dict[str, Any] | None = None
    degree_records = []
    l0, l1, l2, l3 = (value.lower for value in selected_logs)
    u0, u1, u2, u3 = (value.upper for value in selected_logs)

    for degree in range(DEGREE_START, DEGREE_END + 1):
        degree_aggregates = 0
        degree_overlaps = 0
        degree_minimum_gap_scaled: int | None = None
        degree_minimum_gap_witness: dict[str, Any] | None = None
        degree_first_overlap: dict[str, Any] | None = None
        for n0 in range(degree + 1):
            for n1 in range(degree - n0 + 1):
                for n2 in range(degree - n0 - n1 + 1):
                    n3 = degree - n0 - n1 - n2
                    counts = (n0, n1, n2, n3)
                    aggregate_lower = n0 * l0 + n1 * l1 + n2 * l2 + n3 * l3
                    aggregate_upper = n0 * u0 + n1 * u1 + n2 * u2 + n3 * u3
                    degree_aggregates += 1
                    insertion = bisect_right(starts, aggregate_upper)
                    overlap_index = (
                        insertion - 1
                        if insertion
                        and external_logs[insertion - 1].upper >= aggregate_lower
                        else None
                    )
                    if overlap_index is not None:
                        degree_overlaps += 1
                        if degree_first_overlap is None:
                            degree_first_overlap = _overlap_witness(
                                degree,
                                counts,
                                aggregate_lower,
                                aggregate_upper,
                                overlap_index,
                                external_logs,
                                external_merged,
                            )
                        if first_overlap is None:
                            first_overlap = degree_first_overlap
                        continue

                    candidates: list[tuple[int, str, int]] = []
                    if insertion:
                        candidates.append(
                            (
                                aggregate_lower - external_logs[insertion - 1].upper,
                                "left",
                                insertion - 1,
                            )
                        )
                    if insertion < len(external_logs):
                        candidates.append(
                            (
                                external_logs[insertion].lower - aggregate_upper,
                                "right",
                                insertion,
                            )
                        )
                    if not candidates:
                        raise RuntimeError("Q011u found no neighboring external interval")
                    gap_scaled, side, external_index = min(candidates)
                    witness = {
                        "degree": degree,
                        "selected_type_counts": list(counts),
                        "external_side": side,
                        "external_group_index": external_index,
                        "external_first_identifiers": sorted(
                            external_merged[external_index].identifiers
                        )[:8],
                    }
                    if (
                        degree_minimum_gap_scaled is None
                        or gap_scaled < degree_minimum_gap_scaled
                    ):
                        degree_minimum_gap_scaled = gap_scaled
                        degree_minimum_gap_witness = witness
                    if (
                        global_minimum_gap_scaled is None
                        or gap_scaled < global_minimum_gap_scaled
                    ):
                        global_minimum_gap_scaled = gap_scaled
                        global_minimum_gap_witness = witness

        expected_aggregates = comb(degree + 3, 3)
        expected_expanded = comb(degree + 5, 5)
        degree_records.append(
            {
                "degree": degree,
                "aggregate_count": degree_aggregates,
                "expected_aggregate_count": expected_aggregates,
                "expanded_product_control_count": expected_expanded,
                "expected_expanded_product_control_count": expected_expanded,
                "overlap_count": degree_overlaps,
                "nonoverlap_count": degree_aggregates - degree_overlaps,
                "minimum_nonoverlap_log_gap": (
                    None
                    if degree_minimum_gap_scaled is None
                    else _fraction_record(
                        Fraction(degree_minimum_gap_scaled, 10**LOG_FINAL_DECIMAL_DIGITS)
                    )
                ),
                "minimum_nonoverlap_gap_witness": degree_minimum_gap_witness,
                "first_overlap": degree_first_overlap,
                "count_checks_passed": degree_aggregates == expected_aggregates,
            }
        )
        total_aggregates += degree_aggregates
        total_expanded += expected_expanded
        total_overlaps += degree_overlaps

    if global_minimum_gap_scaled is None:
        minimum_gap = Fraction(0)
        minimum_gap_record = None
    else:
        minimum_gap = Fraction(global_minimum_gap_scaled, 10**LOG_FINAL_DECIMAL_DIGITS)
        minimum_gap_record = _fraction_record(minimum_gap)
    degree_record_digest = q011b._canonical_json_sha256(degree_records)
    checks = {
        "all_88_registered_degrees_are_present": bool(
            len(degree_records) == EXPECTED_DEGREE_COUNT
            and [record["degree"] for record in degree_records]
            == list(range(DEGREE_START, DEGREE_END + 1))
        ),
        "all_aggregate_counts_reproduce_per_degree": all(
            record["count_checks_passed"] for record in degree_records
        ),
        "registered_total_aggregate_count_reproduces": (
            total_aggregates == EXPECTED_AGGREGATE_COUNT
        ),
        "registered_expanded_control_count_reproduces": (
            total_expanded == EXPECTED_EXPANDED_PRODUCT_COUNT
        ),
        "overlap_and_nonoverlap_counts_partition_every_degree": all(
            record["overlap_count"] + record["nonoverlap_count"]
            == record["aggregate_count"]
            for record in degree_records
        ),
        "first_overlap_and_per_degree_witnesses_reproduce": bool(
            (first_overlap is None) == (total_overlaps == 0)
            and all(
                (record["first_overlap"] is None) == (record["overlap_count"] == 0)
                for record in degree_records
            )
        ),
        "degree_record_digest_reproduces": (
            degree_record_digest == q011b._canonical_json_sha256(degree_records)
        ),
        "enumeration_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(degree_records)
            and _strict_json_serializable(degree_records)
            and json.dumps(degree_records, allow_nan=False)
        ),
    }
    audit = {
        "degree_range": [DEGREE_START, DEGREE_END],
        "degree_count": len(degree_records),
        "aggregate_count": total_aggregates,
        "expanded_product_control_count": total_expanded,
        "overlap_count": total_overlaps,
        "nonoverlap_count": total_aggregates - total_overlaps,
        "global_minimum_nonoverlap_log_gap": minimum_gap_record,
        "global_minimum_nonoverlap_gap_witness": global_minimum_gap_witness,
        "first_overlap": first_overlap,
        "degree_records": degree_records,
        "degree_record_digest_sha256": degree_record_digest,
        "overlap_interpretation": (
            "closed modulus interval overlap obstructs this modulus-only certificate; "
            "it does not prove an actual complex resonance"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, minimum_gap


def _tail_audit(
    artifacts: dict[str, dict[str, Any]],
    spectrum: dict[str, Any],
    selected_merged: tuple[_MergedModulusInterval, ...],
    external_merged: tuple[_MergedModulusInterval, ...],
) -> dict[str, Any]:
    k_cycle = artifacts["q011k"]["cycle"]
    m_cycle = artifacts["q011m"]["cycle"]
    t_cycle = artifacts["q011t"]["cycle"]
    selected_upper = max(group.upper for group in selected_merged)
    external_lower = min(group.lower for group in external_merged)
    tail_ratio = selected_upper**TAIL_DEGREE / external_lower
    t_quotient = t_cycle["rigorous_spectral_quotient_audit"][
        "spectral_quotient_record"
    ]
    q011t_selected_upper = _fraction(t_quotient["selected_spectral_radius_upper"])
    q011t_external_lower = _fraction(t_quotient["external_minimum_modulus_lower"])
    quadratic = k_cycle["quadratic_spectral_nonresonance_audit"]
    derivative = m_cycle["analytic_map_derivative_audit"]
    derivative_invertible = spectrum["checks"][
        "every_modulus_interval_is_strictly_positive_and_stable"
    ]
    analytic_local_diffeomorphism = bool(
        derivative["passed"]
        and derivative["checks"]["registered_domain_has_positive_density"]
        and derivative_invertible
    )
    checks = {
        "q011t_selected_upper_and_external_lower_reproduce": bool(
            selected_upper == q011t_selected_upper
            and external_lower == q011t_external_lower
            and t_quotient["sufficient_upper_quotient"] == 90
        ),
        "q011k_degree_two_certificate_reproduces": bool(
            quadratic["passed"]
            and quadratic["selected_eigenvalue_count"] == SELECTED_DIMENSION
            and quadratic["unordered_pair_count"] == 300
        ),
        "degree_91_product_is_strictly_below_external_minimum": (
            selected_upper**TAIL_DEGREE < external_lower
        ),
        "degree_91_tail_ratio_fits_registered_cap": tail_ratio <= TAIL_RATIO_CAP,
        "selected_upper_below_one_propagates_tail_to_all_later_degrees": (
            0 < selected_upper < 1
        ),
        "analytic_positive_density_and_invertible_derivative_assumptions_hold": (
            analytic_local_diffeomorphism
        ),
    }
    return {
        "degree_two_certificate": {
            "certified": quadratic["passed"],
            "unordered_pair_count": quadratic["unordered_pair_count"],
        },
        "selected_modulus_upper": _fraction_record(selected_upper),
        "external_modulus_lower": _fraction_record(external_lower),
        "tail_start_degree": TAIL_DEGREE,
        "degree_91_tail_ratio": _fraction_record(tail_ratio),
        "registered_tail_ratio_cap": _fraction_record(TAIL_RATIO_CAP),
        "all_degrees_at_least_91_are_modulus_separated": bool(
            selected_upper**TAIL_DEGREE < external_lower and selected_upper < 1
        ),
        "analytic_local_diffeomorphism_assumptions": {
            "q011m_analytic_derivative_audit_passed": derivative["passed"],
            "positive_density_domain": derivative["checks"][
                "registered_domain_has_positive_density"
            ],
            "fixed_point_derivative_is_invertible": derivative_invertible,
            "analytic_inverse_function_theorem_applies_locally": (
                analytic_local_diffeomorphism
            ),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "smoothness_order": SMOOTHNESS_ORDER,
        "cutoff_power": CUTOFF_POWER,
        "cutoff_inner_scale": CUTOFF_INNER_SCALE,
        "cutoff_transition_end": CUTOFF_TRANSITION_END,
        "cutoff_support_factor": CUTOFF_SUPPORT_FACTOR,
        "degree_range": [DEGREE_START, DEGREE_END],
        "tail_degree": TAIL_DEGREE,
        "selected_group_count": EXPECTED_SELECTED_GROUP_COUNT,
        "selected_group_multiplicities": list(EXPECTED_SELECTED_MULTIPLICITIES),
        "external_group_count": EXPECTED_EXTERNAL_GROUP_COUNT,
        "log_series_terms": LOG_SERIES_TERMS,
        "log_internal_decimal_digits": LOG_INTERNAL_DECIMAL_DIGITS,
        "log_final_decimal_digits": LOG_FINAL_DECIMAL_DIGITS,
        "maximum_log_tail_bound": _fraction_record(MAXIMUM_LOG_TAIL_BOUND),
        "minimum_log_gap": _fraction_record(MINIMUM_LOG_GAP),
        "tail_ratio_cap": _fraction_record(TAIL_RATIO_CAP),
        "floating_point_used_for_gate_decisions": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "cutoff_digest_sha256": cycle["cutoff_digest_sha256"],
        "spectrum_digest_sha256": cycle["spectrum_digest_sha256"],
        "log_digest_sha256": cycle["log_digest_sha256"],
        "enumeration_digest_sha256": cycle["enumeration_digest_sha256"],
        "tail_digest_sha256": cycle["tail_digest_sha256"],
    }


def run_c91_modulus_nonresonance_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    cutoff = _c91_cutoff_audit()
    spectrum, selected_merged, external_merged = _spectral_compression_audit(artifacts)
    logarithms, selected_logs, external_logs = _rational_log_audit(
        selected_merged,
        external_merged,
    )
    enumeration, minimum_gap = _enumeration_audit(
        selected_logs,
        external_logs,
        external_merged,
    )
    tail = _tail_audit(artifacts, spectrum, selected_merged, external_merged)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    cutoff_sections = {"c91_scalar_localization_audit": cutoff}
    spectrum_sections = {"exact_modulus_compression_audit": spectrum}
    log_sections = {"rational_log_enclosure_audit": logarithms}
    enumeration_sections = {"degree_3_through_90_enumeration_audit": enumeration}
    tail_sections = {"degree_2_and_91_tail_audit": tail}
    input_digest = q011b._canonical_json_sha256(input_sections)
    cutoff_digest = q011b._canonical_json_sha256(cutoff_sections)
    spectrum_digest = q011b._canonical_json_sha256(spectrum_sections)
    log_digest = q011b._canonical_json_sha256(log_sections)
    enumeration_digest = q011b._canonical_json_sha256(enumeration_sections)
    tail_digest = q011b._canonical_json_sha256(tail_sections)
    strict_payload = {
        **input_sections,
        **cutoff_sections,
        **spectrum_sections,
        **log_sections,
        **enumeration_sections,
        **tail_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and cutoff_digest == q011b._canonical_json_sha256(cutoff_sections)
        and spectrum_digest == q011b._canonical_json_sha256(spectrum_sections)
        and log_digest == q011b._canonical_json_sha256(log_sections)
        and enumeration_digest == q011b._canonical_json_sha256(enumeration_sections)
        and tail_digest == q011b._canonical_json_sha256(tail_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "four_direct_inputs_twenty_one_digests_and_q007i_source_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011j/k/m/t artifacts, runners, 21 digests, outcomes, claim "
                "boundaries and the Q007i rational-log source reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "c91_beta_polynomial_endpoint_flatness_and_real_typing_reproduce": {
            "passed": cutoff["passed"],
            "threshold": (
                "92 exact coefficients, normalization, derivatives 1--91 flat at both "
                "endpoints, C91 identity/support and real typing reproduce"
            ),
            "value": cutoff["checks"],
        },
        "all_modulus_intervals_and_registered_compressions_reproduce": {
            "passed": spectrum["passed"],
            "threshold": "2598 intervals, selected 24->4 and external 2574->186 reproduce",
            "value": spectrum["checks"],
        },
        "registered_rational_log_enclosures_and_tail_bound_reproduce": {
            "passed": logarithms["passed"],
            "threshold": "96 terms, 110/60 outward grids and endpoint tail <=1e-90",
            "value": logarithms["checks"],
        },
        "all_registered_degree_and_combinatorial_counts_reproduce": {
            "passed": bool(
                enumeration["passed"]
                and enumeration["degree_count"] == EXPECTED_DEGREE_COUNT
                and enumeration["aggregate_count"] == EXPECTED_AGGREGATE_COUNT
                and enumeration["expanded_product_control_count"]
                == EXPECTED_EXPANDED_PRODUCT_COUNT
            ),
            "threshold": (
                "88 degrees, 3,049,486 aggregates and 927,048,276 expanded controls"
            ),
            "value": {
                "degree_count": enumeration["degree_count"],
                "aggregate_count": enumeration["aggregate_count"],
                "expanded_product_control_count": enumeration[
                    "expanded_product_control_count"
                ],
            },
        },
        "overlap_partition_first_witness_and_record_digest_reproduce": {
            "passed": enumeration["passed"],
            "threshold": (
                "overlap/nonoverlap partition, first witnesses and exact degree-record "
                "digest reproduce"
            ),
            "value": enumeration["checks"],
        },
        "q011k_degree_two_and_degree_91_tail_reproduce": {
            "passed": tail["passed"],
            "threshold": (
                "300 quadratic pairs, exact degree-91 ratio <=0.999 and all later "
                "degrees by selected modulus <1"
            ),
            "value": tail["checks"],
        },
        "strict_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite strict JSON, six section digests, result digest and runner "
                "provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    zero_overlaps = enumeration["overlap_count"] == 0
    cutoff_hypothesis = bool(
        cutoff["passed"]
        and cutoff["scalar_c91_localization"][
            "is_c91_across_both_transition_endpoints"
        ]
        and cutoff["scalar_c91_localization"]["identity_on_closed_radius_r_ball"]
        and cutoff["scalar_c91_localization"][
            "support_is_contained_in_closed_radius_four_r_ball"
        ]
    )
    compression_hypothesis = bool(
        spectrum["passed"]
        and spectrum["selected_merged_interval_count"] == EXPECTED_SELECTED_GROUP_COUNT
        and spectrum["selected_group_multiplicities"]
        == list(EXPECTED_SELECTED_MULTIPLICITIES)
        and spectrum["external_merged_interval_count"] == EXPECTED_EXTERNAL_GROUP_COUNT
    )
    complete_theorem_assumptions = bool(
        tail["passed"]
        and zero_overlaps
        and tail["degree_two_certificate"]["certified"]
        and tail["all_degrees_at_least_91_are_modulus_separated"]
        and tail["analytic_local_diffeomorphism_assumptions"][
            "analytic_inverse_function_theorem_applies_locally"
        ]
    )
    hypothesis_gates = {
        "scalar_localization_is_c91_real_and_matches_the_original_map_near_origin": {
            "passed": bool(validity_passed and cutoff_hypothesis),
            "threshold": "registered C91 real localization is identity near the origin",
            "value": cutoff["scalar_c91_localization"],
        },
        "selected_and_external_modulus_compressions_have_registered_strict_gaps": {
            "passed": bool(validity_passed and compression_hypothesis),
            "threshold": "selected 4 types with 8/4/4/8 and external 186 strict components",
            "value": {
                "selected_count": spectrum["selected_merged_interval_count"],
                "selected_multiplicities": spectrum["selected_group_multiplicities"],
                "external_count": spectrum["external_merged_interval_count"],
            },
        },
        "all_degree_3_through_90_aggregates_have_zero_external_modulus_overlap": {
            "passed": bool(validity_passed and zero_overlaps),
            "threshold": "zero overlaps among all 3,049,486 aggregate intervals",
            "value": enumeration["overlap_count"],
        },
        "zero_overlap_global_minimum_log_gap_fits_registered_floor": {
            "passed": bool(validity_passed and zero_overlaps and minimum_gap >= MINIMUM_LOG_GAP),
            "threshold": "zero overlaps and global rational log gap >=1e-12",
            "value": enumeration["global_minimum_nonoverlap_log_gap"],
        },
        "degree_two_middle_degrees_tail_and_local_diffeomorphism_are_complete": {
            "passed": bool(validity_passed and complete_theorem_assumptions),
            "threshold": (
                "degree 2, degrees 3--90, degree 91 tail and analytic local "
                "diffeomorphism assumptions all hold"
            ),
            "value": {
                "degree_two": tail["degree_two_certificate"]["certified"],
                "degrees_3_through_90": zero_overlaps,
                "degree_91_tail": tail["all_degrees_at_least_91_are_modulus_separated"],
                "analytic_local_diffeomorphism": tail[
                    "analytic_local_diffeomorphism_assumptions"
                ]["analytic_inverse_function_theorem_applies_locally"],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011u C91 modulus nonresonance audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Do an exact C91 scalar localization, rational log-modulus intervals and "
            "complete enumeration certify external nonresonance for degrees 3 through 90?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "cutoff_digest_sha256": cutoff_digest,
        "spectrum_digest_sha256": spectrum_digest,
        "log_digest_sha256": log_digest,
        "enumeration_digest_sha256": enumeration_digest,
        "tail_digest_sha256": tail_digest,
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
    theorem_applies = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified": bool(
            validity_passed and cutoff_hypothesis
        ),
        "the_degree_91_and_higher_modulus_tail_is_certified": bool(
            validity_passed and tail["all_degrees_at_least_91_are_modulus_separated"]
        ),
        "degree_two_phase_sensitive_nonresonance_is_preserved": bool(
            validity_passed and tail["degree_two_certificate"]["certified"]
        ),
        "degrees_3_through_90_modulus_only_nonresonance_is_certified": bool(
            theorem_applies
        ),
        "the_registered_c91_spectral_subspace_theorem_applies": theorem_applies,
        "an_analytic_local_invariant_manifold_is_established_by_this_gate": theorem_applies,
        "c91_class_local_uniqueness_is_established_by_this_gate": theorem_applies,
        "an_actual_complex_resonance_is_established": False,
        "an_analytic_invariant_manifold_is_disproved": False,
        "the_q011t_c1_graph_is_disproved_or_shown_nonsmooth": False,
        "the_theorem_manifold_is_identified_with_the_q011t_graph": False,
        "an_explicit_higher_smoothness_radius_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011j_q011k_q011m_or_q011t_acceptance_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf, the registered C91 scalar localization, all 2598 Q011k "
        "eigendisc moduli, degrees 3 through 90 modulus-only aggregates and the "
        "degree-91 tail. A modulus overlap is only a failure of this sufficient "
        "certificate: it is not an actual complex resonance and does not disprove an "
        "analytic invariant manifold or smoothness of the Q011t graph. No complex "
        "phase, Fourier output sector, phase-sensitive product disk, homological "
        "inverse norm, equality with the Q011t graph, explicit higher-smoothness "
        "radius, normal attraction, basin, other grid, force, wall or D3Q27 result is "
        "certified."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011j_exact_fixed_point_acceptance_changed": False,
        "q011k_spectral_split_acceptance_changed": False,
        "q011m_quadratic_jet_acceptance_changed": False,
        "q011t_c1_tangent_graph_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Identify the theorem manifold with the Q011t graph and validate an "
            "explicit higher-smoothness neighborhood."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Preregister Q011v for a phase-sensitive product audit restricted by "
            "Fourier output sector, beginning with the first modulus-overlap witness."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, polynomial, compression, logarithm, "
            "enumeration, tail or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011u cycle failed strict serialization or digest")
    return cycle


def run_q011u_study() -> dict[str, Any]:
    cycle = run_c91_modulus_nonresonance_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "modulus_interval_count": COORDINATE_SLOT_COUNT,
            "selected_modulus_group_count": EXPECTED_SELECTED_GROUP_COUNT,
            "external_modulus_group_count": EXPECTED_EXTERNAL_GROUP_COUNT,
            "aggregate_count": EXPECTED_AGGREGATE_COUNT,
        },
        "mathematical_scope": {
            "diagnostic": "C91 localization and modulus-only degree-90 nonresonance",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "external_real_dimension": EXTERNAL_DIMENSION,
            "c91_scalar_localization_claim": cycle["study_validity"] == "passed",
            "modulus_only_nonresonance_claim": cycle["hypothesis_outcome"] == "accepted",
            "actual_complex_resonance_claim": False,
            "q011t_graph_equality_claim": False,
            "normal_attraction_claim": False,
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
    result = run_q011u_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
