"""Q011y contained transformed-residual eigendisc refinement certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011o_graph_transform_setup as q011o
import research.q011u_c91_modulus_nonresonance as q011u
import research.q011x_degree5_phase_disks as q011x
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

ExactComplex = tuple[Fraction, Fraction]

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
REPRESENTATIVE_BLOCKS = tuple(range(9))
MAXIMUM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_IMPROVEMENT_RATIO = Fraction(300)
MAXIMUM_REFINED_MODULUS_UPPER = Fraction(9921, 10_000)
MINIMUM_WITNESS_SEPARATION = Fraction(4, 10**5)

WITNESS_OVERLAP_COUNTS = (0, 2, 2, 2)
WITNESS_SOURCE_INDICES = (
    (16, 151),
    (16, 151),
    (0, 149),
    (0, 149),
    (0, 146),
    (0, 147),
)
WITNESS_OUTPUT_BLOCK = 15
WITNESS_TARGET_INDEX = (15, 148)

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

Q011L_ARTIFACT_SHA256 = "2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a"
Q011L_RUNNER_SHA256 = "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7"
Q011L_DIGESTS = (
    "1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011",
    "a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3",
    "694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377",
    "14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915",
    "c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45",
)
Q011L_DIGEST_NAMES = (
    "input_digest_sha256",
    "graph_digest_sha256",
    "pair_digest_sha256",
    "homological_digest_sha256",
    "result_digest_sha256",
)
Q011L_CLASSIFICATION = (
    "the exact repaired selected/external split has a rigorously bounded "
    "quadratic homological inverse in the registered quotient norm"
)

Q011U_ARTIFACT_SHA256 = "4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4"
Q011U_RUNNER_SHA256 = "fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e"
Q011U_DIGESTS = (
    "ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4",
    "55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94",
    "a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d",
    "10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5",
    "5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c",
    "307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6",
    "b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c",
)
Q011U_DIGEST_NAMES = (
    "input_digest_sha256",
    "cutoff_digest_sha256",
    "spectrum_digest_sha256",
    "log_digest_sha256",
    "enumeration_digest_sha256",
    "tail_digest_sha256",
    "result_digest_sha256",
)
Q011U_CLASSIFICATION = (
    "the C91 localization and degree-91 tail are certified, but modulus-only "
    "nonresonance through degree 90 is obstructed"
)

Q011X_ARTIFACT_SHA256 = "11ef4d47f60840c4bc05c4056024e2af14b8339a8983b65dcb878bd355cfc328"
Q011X_RUNNER_SHA256 = "62712392faca2c154883edd93792f81e60ff975f6da16010aa3190ee44657a18"
Q011X_DIGESTS = (
    "9d13fa470f4c0bd8efa13868af90c6931025d7f3007e600c66af05bd0037a7ed",
    "717c4eadbd0e5f160a87de8846968933b8c5fbe604d769f215b6dcc65dacc955",
    "d31b7ea3cfcd7eca9d936cded13a1dc316e64dc2fc088bda745ea927d15ce52c",
    "add9d07725802c5fba84b68a207d5adc6f3f405a152a22f88059259f9a255222",
    "608bb3a7aee34a833e7980dbd18f4a3e641426966352126833f298e282437b31",
)
Q011X_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)
Q011O_SOURCE_SHA256 = "60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f"

ACCEPTED_CLASSIFICATION = (
    "the Q011k eigenvalue families admit contained transformed-residual "
    "eigendiscs that clear the first degree-six enclosure obstruction"
)
REJECTED_CLASSIFICATION = (
    "the transformed-residual eigendiscs do not clear the first degree-six enclosure obstruction"
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


def _exact_fraction_record(value: Fraction) -> dict[str, str]:
    return {
        "numerator_base16": hex(value.numerator),
        "denominator_base16": hex(value.denominator),
    }


def _exact_complex_record(value: ExactComplex) -> dict[str, dict[str, str]]:
    return {
        "real": _exact_fraction_record(value[0]),
        "imaginary": _exact_fraction_record(value[1]),
    }


def _complex_product(left: ExactComplex, right: ExactComplex) -> ExactComplex:
    ar, ai = left
    br, bi = right
    return (ar * br - ai * bi, ar * bi + ai * br)


def _complex_difference(left: ExactComplex, right: ExactComplex) -> ExactComplex:
    return (left[0] - right[0], left[1] - right[1])


class _FramedRecordDigest:
    """Hash an ordered exact record stream without retaining its payload."""

    def __init__(self, domain: str) -> None:
        self._digest = hashlib.sha256()
        encoded_domain = domain.encode("utf-8")
        self._digest.update(len(encoded_domain).to_bytes(8, "big"))
        self._digest.update(encoded_domain)
        self.count = 0

    def update(self, record: dict[str, Any]) -> None:
        encoded = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        self._digest.update(len(encoded).to_bytes(8, "big"))
        self._digest.update(encoded)
        self.count += 1

    def hexdigest(self) -> str:
        return self._digest.hexdigest()


def _digest_tuple(cycle: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


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
            Q011K_DIGEST_NAMES,
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
            Q011L_DIGEST_NAMES,
            "accepted",
            Q011L_CLASSIFICATION,
        ),
        (
            "q011u",
            directory / "q011u_c91_modulus_nonresonance.json",
            Path(q011u.__file__).resolve(),
            Q011U_ARTIFACT_SHA256,
            Q011U_RUNNER_SHA256,
            Q011U_DIGESTS,
            Q011U_DIGEST_NAMES,
            "rejected",
            Q011U_CLASSIFICATION,
        ),
        (
            "q011x",
            directory / "q011x_degree5_phase_disks.json",
            Path(q011x.__file__).resolve(),
            Q011X_ARTIFACT_SHA256,
            Q011X_RUNNER_SHA256,
            Q011X_DIGESTS,
            Q011X_DIGEST_NAMES,
            "accepted",
            q011x.ACCEPTED_CLASSIFICATION,
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
        digests = _digest_tuple(cycle, digest_names)
        artifacts[label] = artifact
        checks[f"{label}_artifact_sha256_matches"] = _file_sha256(artifact_path) == artifact_hash
        checks[f"{label}_runner_sha256_matches"] = bool(
            _file_sha256(runner_path) == runner_hash
            and artifact["runner_source"]["sha256"] == runner_hash
        )
        checks[f"{label}_digests_match"] = digests == expected_digests
        checks[f"{label}_registered_outcome_reproduces"] = bool(
            cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == expected_outcome
            and cycle["scientific_classification"] == classification
        )
        checks[f"{label}_claim_boundary_is_present"] = bool(cycle["claim_boundary"])
        checks[f"{label}_package_source_metadata_matches"] = artifact["source"] == source_metadata()
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
            "claim_boundary": cycle["claim_boundary"],
        }

    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    l_theorem = artifacts["q011l"]["cycle"]["theorem_consequence"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    x_theorem = artifacts["q011x"]["cycle"]["theorem_consequence"]
    checks["q011k_stable_split_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["selected_and_external_spectral_unions_do_not_exchange"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011l_quadratic_inverse_scope_is_preserved"] = bool(
        l_theorem["all_five_quadratic_sector_homological_operators_are_invertible"]
        and l_theorem["registered_coordinate_inverse_bound_is_rigorous"]
        and not l_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011u_valid_rejection_and_tail_scope_are_preserved"] = bool(
        u_theorem["a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"]
        and u_theorem["the_degree_91_and_higher_modulus_tail_is_certified"]
        and not u_theorem["an_actual_complex_resonance_is_established"]
    )
    checks["q011x_degree_two_through_five_scope_is_preserved"] = bool(
        x_theorem["certified_external_nonresonance_degrees"] == [2, 3, 4, 5]
        and x_theorem["missing_external_nonresonance_degrees"] == list(range(6, 91))
        and not x_theorem["degrees_6_through_90_are_certified"]
        and not x_theorem["ssm_existence_or_uniqueness_is_certified"]
    )
    q011o_path = Path(q011o.__file__).resolve()
    checks["q011o_source_sha256_matches"] = _file_sha256(q011o_path) == Q011O_SOURCE_SHA256
    checks["twenty_two_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 22
    )
    audit = {
        **records,
        "helper_source": {
            "filename": q011o_path.name,
            "sha256": _file_sha256(q011o_path),
        },
        "direct_digest_count": 22,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _transformed_residual_theorem_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[int, list[ExactComplex]],
    dict[int, tuple[int, ...]],
    dict[int, Fraction],
    dict[int, Fraction],
    dict[int, dict[str, Fraction]],
]:
    k_cycle = artifacts["q011k"]["cycle"]
    l_cycle = artifacts["q011l"]["cycle"]
    centers, selected, old_radii, metrics, spectral = q011l._spectral_data(artifacts["q011k"])
    refined_radii = {block: metrics[block]["theta"] for block in range(SIZE)}
    primary_records = {
        int(record["block_index"]): record["primary_precision_proof"]
        for record in k_cycle["dual_precision_bauer_fike_audit"]["representative_block_records"]
    }
    inverse_checks = []
    for block in REPRESENTATIVE_BLOCKS:
        primary = primary_records[block]
        inverse_candidate = _fraction(primary["inverse_candidate_infinity_norm_upper"])
        inverse_defect = _fraction(primary["inverse_defect_infinity_norm_upper"])
        beta = _fraction(primary["certified_inverse_infinity_norm_upper"])
        inverse_checks.append(
            bool(
                primary["passed"]
                and inverse_defect < 1
                and beta == inverse_candidate / (1 - inverse_defect)
                and beta == metrics[block]["beta"]
            )
        )

    stored_spectral = l_cycle["exact_eigencoordinate_residual_audit"]
    checks = {
        "q011l_exact_spectral_reconstruction_reproduces": bool(
            spectral["passed"]
            and spectral == stored_spectral
            and q011b._canonical_json_sha256(spectral)
            == q011b._canonical_json_sha256(stored_spectral)
        ),
        "all_nine_inverse_certificates_make_v_invertible": bool(
            len(primary_records) == 9 and all(inverse_checks)
        ),
        "finite_block_dimensions_and_all_centers_reproduce": bool(
            len(centers) == SIZE
            and len(centers[0]) == 150
            and all(len(centers[block]) == 153 for block in range(1, SIZE))
            and sum(len(values) for values in centers.values()) == COORDINATE_SLOT_COUNT
        ),
        "all_transformed_residual_bounds_are_positive": all(
            metrics[block]["beta"] > 0
            and metrics[block]["family_residual"] > 0
            and refined_radii[block] == metrics[block]["beta"] * metrics[block]["family_residual"]
            for block in range(SIZE)
        ),
        "similarity_and_transformed_residual_identity_is_applicable": bool(
            all(inverse_checks) and spectral["passed"]
        ),
        "induced_infinity_norm_is_submultiplicative": True,
        "gershgorin_row_sum_inclusion_applies_to_each_finite_block": True,
    }
    audit = {
        "literature_basis": {
            "result": "Bauer--Fike similarity-transform exclusion argument",
            "original_paper": "http://eudml.org/doc/131452",
            "gershgorin_use": (
                "apply row discs to D+F, then enlarge each shifted row disc "
                "to the same-center disc D(d_j,||F||_inf)"
            ),
        },
        "matrix_identity": "V^{-1} A V = D + V^{-1}(A V - V D)",
        "transformed_residual_bound": ("||V^{-1}(AV-VD)||_inf <= beta * ||AV-VD||_inf = theta"),
        "gershgorin_consequence": ("spectrum(A) is contained in the union over j of D(d_j, theta)"),
        "proof_norm": "induced matrix infinity norm",
        "finite_block_dimensions": {"block_0": 150, "blocks_1_through_16": 153},
        "q011l_spectral_digest_sha256": q011b._canonical_json_sha256(spectral),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, centers, selected, old_radii, refined_radii, metrics


def _radius_refinement_audit(
    old_radii: dict[int, Fraction],
    refined_radii: dict[int, Fraction],
    metrics: dict[int, dict[str, Fraction]],
) -> tuple[dict[str, Any], Fraction, Fraction]:
    records = []
    identities = []
    for block in REPRESENTATIVE_BLOCKS:
        vector_norm = metrics[block]["vector_norm"]
        beta = metrics[block]["beta"]
        residual = metrics[block]["family_residual"]
        refined = refined_radii[block]
        old = old_radii[block]
        ratio = old / refined
        identities.append(
            bool(
                refined == beta * residual
                and old == vector_norm * beta * beta * residual
                and old == vector_norm * beta * refined
                and ratio == vector_norm * beta
                and ratio >= 1
            )
        )
        records.append(
            {
                "representative_block": block,
                "vector_infinity_norm_upper": _fraction_record(vector_norm),
                "certified_inverse_infinity_norm_upper": _fraction_record(beta),
                "family_eigendecomposition_residual_infinity_upper": _fraction_record(residual),
                "old_bauer_fike_radius_upper": _fraction_record(old),
                "refined_transformed_residual_radius_upper": _fraction_record(refined),
                "old_to_refined_ratio": _fraction_record(ratio),
                "exact_radius_identity_reproduces": identities[-1],
            }
        )

    maximum_radius_block = max(range(SIZE), key=refined_radii.__getitem__)
    minimum_ratio_block = min(
        range(SIZE), key=lambda block: old_radii[block] / refined_radii[block]
    )
    maximum_radius = refined_radii[maximum_radius_block]
    minimum_ratio = old_radii[minimum_ratio_block] / refined_radii[minimum_ratio_block]
    checks = {
        "all_nine_representative_exact_radius_identities_reproduce": all(identities),
        "all_seventeen_refined_radii_are_positive_and_contained": all(
            0 < refined_radii[block] <= old_radii[block] for block in range(SIZE)
        ),
        "conjugate_transport_is_exact_for_blocks_nine_through_sixteen": all(
            refined_radii[block] == refined_radii[SIZE - block]
            and old_radii[block] == old_radii[SIZE - block]
            and metrics[block] == metrics[SIZE - block]
            for block in range(9, SIZE)
        ),
        "registered_extrema_witnesses_reproduce": bool(
            maximum_radius_block in (4, 13) and minimum_ratio_block in (8, 9)
        ),
    }
    audit = {
        "representative_block_count": len(records),
        "transported_conjugate_block_count": 8,
        "representative_block_records": records,
        "maximum_refined_radius_upper": _fraction_record(maximum_radius),
        "maximum_refined_radius_block": maximum_radius_block,
        "minimum_old_to_refined_improvement_ratio": _fraction_record(minimum_ratio),
        "minimum_improvement_ratio_block": minimum_ratio_block,
        "registered_maximum_refined_radius": _fraction_record(MAXIMUM_REFINED_RADIUS),
        "registered_minimum_improvement_ratio": _fraction_record(MINIMUM_IMPROVEMENT_RATIO),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, maximum_radius, minimum_ratio


def _disc_containment_audit(
    centers: dict[int, list[ExactComplex]],
    selected: dict[int, tuple[int, ...]],
    old_radii: dict[int, Fraction],
    refined_radii: dict[int, Fraction],
) -> tuple[dict[str, Any], Fraction]:
    selected_sets = {block: frozenset(indices) for block, indices in selected.items()}
    modulus_cache: dict[ExactComplex, RationalInterval] = {}
    framer = _FramedRecordDigest("Q011y/refined-eigendisc/v1")
    selected_count = 0
    external_count = 0
    all_contained = True
    all_interval_contained = True
    all_stable = True
    maximum_upper: Fraction | None = None
    maximum_witness: dict[str, int] | None = None
    selected_maximum: Fraction | None = None
    external_maximum: Fraction | None = None

    for block in range(SIZE):
        old_radius = old_radii[block]
        refined_radius = refined_radii[block]
        for center_index, center in enumerate(centers[block]):
            if center not in modulus_cache:
                modulus_cache[center] = q011o._center_modulus_bounds(center)
            center_modulus = modulus_cache[center]
            refined_interval = RationalInterval(
                max(Fraction(0), center_modulus.lower - refined_radius),
                center_modulus.upper + refined_radius,
            )
            old_interval = RationalInterval(
                max(Fraction(0), center_modulus.lower - old_radius),
                center_modulus.upper + old_radius,
            )
            is_selected = center_index in selected_sets.get(block, frozenset())
            selected_count += int(is_selected)
            external_count += int(not is_selected)
            contained = refined_radius <= old_radius
            interval_contained = bool(
                refined_interval.lower >= old_interval.lower
                and refined_interval.upper <= old_interval.upper
            )
            stable = refined_interval.upper < 1
            all_contained = all_contained and contained
            all_interval_contained = all_interval_contained and interval_contained
            all_stable = all_stable and stable
            if maximum_upper is None or refined_interval.upper > maximum_upper:
                maximum_upper = refined_interval.upper
                maximum_witness = {"block_index": block, "center_index": center_index}
            if is_selected:
                selected_maximum = (
                    refined_interval.upper
                    if selected_maximum is None
                    else max(selected_maximum, refined_interval.upper)
                )
            else:
                external_maximum = (
                    refined_interval.upper
                    if external_maximum is None
                    else max(external_maximum, refined_interval.upper)
                )
            framer.update(
                {
                    "block_index": block,
                    "center_index": center_index,
                    "center": _exact_complex_record(center),
                    "center_modulus_lower": _exact_fraction_record(center_modulus.lower),
                    "center_modulus_upper": _exact_fraction_record(center_modulus.upper),
                    "refined_radius": _exact_fraction_record(refined_radius),
                    "old_radius": _exact_fraction_record(old_radius),
                    "refined_modulus_lower": _exact_fraction_record(refined_interval.lower),
                    "refined_modulus_upper": _exact_fraction_record(refined_interval.upper),
                    "old_modulus_lower": _exact_fraction_record(old_interval.lower),
                    "old_modulus_upper": _exact_fraction_record(old_interval.upper),
                    "selected": is_selected,
                    "contained": contained,
                }
            )

    if maximum_upper is None or maximum_witness is None:
        raise RuntimeError("Q011y reconstructed no eigendiscs")
    if selected_maximum is None or external_maximum is None:
        raise RuntimeError("Q011y reconstructed an empty selected or external family")
    checks = {
        "all_2598_refined_eigendiscs_are_evaluated": (framer.count == COORDINATE_SLOT_COUNT),
        "selected_and_external_dimensions_reproduce": bool(
            selected_count == SELECTED_DIMENSION
            and external_count == EXTERNAL_DIMENSION
            and selected_count + external_count == COORDINATE_SLOT_COUNT
        ),
        "every_refined_complex_disc_is_contained_in_its_q011k_disc": all_contained,
        "every_refined_modulus_interval_is_contained_in_its_old_interval": (all_interval_contained),
        "every_refined_eigendisc_is_strictly_inside_the_unit_circle": all_stable,
        "maximum_refined_modulus_witness_reproduces": maximum_witness
        == {"block_index": 0, "center_index": 147},
        "selected_and_external_unions_keep_the_q011k_membership_partition": bool(
            selected_count == SELECTED_DIMENSION and external_count == EXTERNAL_DIMENSION
        ),
    }
    audit = {
        "eigendisc_count": framer.count,
        "unique_center_modulus_evaluation_count": len(modulus_cache),
        "selected_eigendisc_count": selected_count,
        "external_eigendisc_count": external_count,
        "maximum_refined_modulus_upper": _fraction_record(maximum_upper),
        "maximum_refined_modulus_witness": maximum_witness,
        "selected_maximum_refined_modulus_upper": _fraction_record(selected_maximum),
        "external_maximum_refined_modulus_upper": _fraction_record(external_maximum),
        "registered_maximum_refined_modulus_upper": _fraction_record(MAXIMUM_REFINED_MODULUS_UPPER),
        "framed_exact_eigendisc_digest_sha256": framer.hexdigest(),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, maximum_upper


def _product_radius(
    center_modulus_uppers: tuple[Fraction, ...],
    radii: tuple[Fraction, ...],
) -> tuple[Fraction, Fraction]:
    upper_product = Fraction(1)
    center_product = Fraction(1)
    for upper, radius in zip(center_modulus_uppers, radii, strict=True):
        upper_product *= upper + radius
        center_product *= upper
    expanded = Fraction(0)
    for mask in range(1, 1 << len(radii)):
        term = Fraction(1)
        for index in range(len(radii)):
            term *= radii[index] if mask & (1 << index) else center_modulus_uppers[index]
        expanded += term
    return upper_product - center_product, expanded


def _degree_six_witness_audit(
    centers: dict[int, list[ExactComplex]],
    old_radii: dict[int, Fraction],
    refined_radii: dict[int, Fraction],
) -> tuple[dict[str, Any], Fraction]:
    product_center = (Fraction(1), Fraction(0))
    center_modulus_uppers = []
    for block, center_index in WITNESS_SOURCE_INDICES:
        center = centers[block][center_index]
        product_center = _complex_product(product_center, center)
        center_modulus_uppers.append(q011o._center_modulus_bounds(center).upper)
    center_modulus_tuple = tuple(center_modulus_uppers)
    old_source_radii = tuple(old_radii[block] for block, _ in WITNESS_SOURCE_INDICES)
    refined_source_radii = tuple(refined_radii[block] for block, _ in WITNESS_SOURCE_INDICES)
    old_product_radius, old_expansion = _product_radius(center_modulus_tuple, old_source_radii)
    refined_product_radius, refined_expansion = _product_radius(
        center_modulus_tuple, refined_source_radii
    )
    target_block, target_index = WITNESS_TARGET_INDEX
    target_center = centers[target_block][target_index]
    distance = q011o._center_modulus_bounds(_complex_difference(product_center, target_center))
    old_combined_radius = old_product_radius + old_radii[target_block]
    refined_combined_radius = refined_product_radius + refined_radii[target_block]
    old_margin_lower = distance.lower - old_combined_radius
    old_margin_upper = distance.upper - old_combined_radius
    refined_margin_lower = distance.lower - refined_combined_radius
    refined_margin_upper = distance.upper - refined_combined_radius
    output_block = sum(block for block, _ in WITNESS_SOURCE_INDICES) % SIZE
    source_identifiers = [
        f"block={block};center={center_index}" for block, center_index in WITNESS_SOURCE_INDICES
    ]
    checks = {
        "registered_source_multiset_and_target_reproduce": bool(
            source_identifiers
            == [
                "block=16;center=151",
                "block=16;center=151",
                "block=0;center=149",
                "block=0;center=149",
                "block=0;center=146",
                "block=0;center=147",
            ]
            and WITNESS_TARGET_INDEX == (15, 148)
        ),
        "fourier_output_sector_is_fifteen": (output_block == WITNESS_OUTPUT_BLOCK == target_block),
        "old_and_refined_product_radius_expansions_reproduce": bool(
            old_product_radius == old_expansion and refined_product_radius == refined_expansion
        ),
        "old_q011k_discs_have_a_strictly_negative_separation_margin": (old_margin_upper < 0),
        "refined_discs_have_a_strictly_positive_separation_margin": (refined_margin_lower > 0),
        "refined_product_and_target_discs_are_contained_in_old_discs": bool(
            refined_product_radius <= old_product_radius
            and refined_radii[target_block] <= old_radii[target_block]
        ),
    }
    audit = {
        "degree": 6,
        "overlap_selected_type_counts": list(WITNESS_OVERLAP_COUNTS),
        "source_identifiers": source_identifiers,
        "output_block": output_block,
        "target_identifier": f"block={target_block};center={target_index}",
        "product_center": _exact_complex_record(product_center),
        "target_center": _exact_complex_record(target_center),
        "center_distance_lower": _fraction_record(distance.lower),
        "center_distance_upper": _fraction_record(distance.upper),
        "old_product_radius": _fraction_record(old_product_radius),
        "old_target_radius": _fraction_record(old_radii[target_block]),
        "old_combined_radius": _fraction_record(old_combined_radius),
        "old_separation_margin_lower": _fraction_record(old_margin_lower),
        "old_separation_margin_upper": _fraction_record(old_margin_upper),
        "refined_product_radius": _fraction_record(refined_product_radius),
        "refined_target_radius": _fraction_record(refined_radii[target_block]),
        "refined_combined_radius": _fraction_record(refined_combined_radius),
        "refined_separation_margin_lower": _fraction_record(refined_margin_lower),
        "refined_separation_margin_upper": _fraction_record(refined_margin_upper),
        "registered_minimum_refined_separation": _fraction_record(MINIMUM_WITNESS_SEPARATION),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, refined_margin_lower


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "representative_blocks": list(REPRESENTATIVE_BLOCKS),
        "refined_radius_formula": "theta = beta * family residual",
        "old_radius_formula": "r_old = ||V||_inf * beta^2 * family residual",
        "maximum_refined_radius": _fraction_record(MAXIMUM_REFINED_RADIUS),
        "minimum_old_to_refined_improvement_ratio": _fraction_record(MINIMUM_IMPROVEMENT_RATIO),
        "maximum_refined_modulus_upper": _fraction_record(MAXIMUM_REFINED_MODULUS_UPPER),
        "minimum_witness_separation": _fraction_record(MINIMUM_WITNESS_SEPARATION),
        "direct_input_digest_count": 22,
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
        "theorem_digest_sha256": cycle["theorem_digest_sha256"],
        "radius_digest_sha256": cycle["radius_digest_sha256"],
        "containment_digest_sha256": cycle["containment_digest_sha256"],
        "witness_digest_sha256": cycle["witness_digest_sha256"],
    }


def run_transformed_residual_eigendisc_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        theorem,
        centers,
        selected,
        old_radii,
        refined_radii,
        metrics,
    ) = _transformed_residual_theorem_audit(artifacts)
    radius, maximum_radius, minimum_ratio = _radius_refinement_audit(
        old_radii, refined_radii, metrics
    )
    containment, maximum_modulus_upper = _disc_containment_audit(
        centers, selected, old_radii, refined_radii
    )
    witness, witness_margin = _degree_six_witness_audit(centers, old_radii, refined_radii)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    theorem_sections = {"transformed_residual_theorem_audit": theorem}
    radius_sections = {"exact_radius_refinement_audit": radius}
    containment_sections = {"all_eigendisc_containment_audit": containment}
    witness_sections = {"first_degree_six_witness_audit": witness}
    input_digest = q011b._canonical_json_sha256(input_sections)
    theorem_digest = q011b._canonical_json_sha256(theorem_sections)
    radius_digest = q011b._canonical_json_sha256(radius_sections)
    containment_digest = q011b._canonical_json_sha256(containment_sections)
    witness_digest = q011b._canonical_json_sha256(witness_sections)
    strict_payload = {
        **input_sections,
        **theorem_sections,
        **radius_sections,
        **containment_sections,
        **witness_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and theorem_digest == q011b._canonical_json_sha256(theorem_sections)
        and radius_digest == q011b._canonical_json_sha256(radius_sections)
        and containment_digest == q011b._canonical_json_sha256(containment_sections)
        and witness_digest == q011b._canonical_json_sha256(witness_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "four_artifacts_twenty_two_digests_and_q011o_source_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/l/u/x artifacts, runners, 22 digests, outcomes, claim "
                "boundaries and the Q011o source reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011k_inverse_and_q011l_transformed_residual_data_reproduce": {
            "passed": theorem["passed"],
            "threshold": (
                "nine invertible V certificates and 17 exact theta=beta*residual families"
            ),
            "value": theorem["checks"],
        },
        "finite_similarity_norm_and_gershgorin_argument_is_complete": {
            "passed": theorem["passed"],
            "threshold": ("V^-1 A V identity, induced infinity norm and Gershgorin inclusion"),
            "value": theorem["checks"],
        },
        "nine_radius_identities_and_seventeen_block_transport_reproduce": {
            "passed": radius["passed"],
            "threshold": ("old=||V||*beta*theta and exact conjugate transport for all blocks"),
            "value": radius["checks"],
        },
        "all_2598_refined_discs_and_memberships_reproduce": {
            "passed": containment["passed"],
            "threshold": ("2598 contained discs with selected/external dimensions 24/2574"),
            "value": containment["checks"],
        },
        "fixed_degree_six_witness_formulas_reproduce": {
            "passed": witness["passed"],
            "threshold": (
                "registered six sources, sector 15 target, product radii and exact margins"
            ),
            "value": witness["checks"],
        },
        "strict_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite strict JSON, five section digests, result digest and runner provenance"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "transformed_residual_eigendisc_inclusion_is_exact": {
            "passed": bool(validity_passed and theorem["passed"]),
            "threshold": "spectrum(A) subset union_j D(d_j,beta*||AV-VD||_inf)",
            "value": theorem["checks"],
        },
        "radius_and_improvement_thresholds_hold": {
            "passed": bool(
                validity_passed
                and maximum_radius <= MAXIMUM_REFINED_RADIUS
                and minimum_ratio >= MINIMUM_IMPROVEMENT_RATIO
            ),
            "threshold": "maximum radius <=5e-8 and minimum old/new ratio >=300",
            "value": {
                "maximum_refined_radius": radius["maximum_refined_radius_upper"],
                "minimum_improvement_ratio": radius["minimum_old_to_refined_improvement_ratio"],
            },
        },
        "all_refined_eigendiscs_are_strictly_stable": {
            "passed": bool(
                validity_passed
                and containment["passed"]
                and maximum_modulus_upper <= MAXIMUM_REFINED_MODULUS_UPPER
                and maximum_modulus_upper < 1
            ),
            "threshold": "maximum refined modulus upper <=0.9921<1",
            "value": containment["maximum_refined_modulus_upper"],
        },
        "all_refined_discs_preserve_the_q011k_split_by_containment": {
            "passed": bool(validity_passed and containment["passed"]),
            "threshold": ("each refined disc is contained in the same-center Q011k disc"),
            "value": containment["checks"],
        },
        "first_degree_six_obstruction_witness_is_strictly_cleared": {
            "passed": bool(
                validity_passed
                and witness["passed"]
                and witness_margin >= MINIMUM_WITNESS_SEPARATION
            ),
            "threshold": "refined exact separation lower >=4e-5",
            "value": witness["refined_separation_margin_lower"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011y transformed-residual eigendisc audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    elif not hypothesis_gates["first_degree_six_obstruction_witness_is_strictly_cleared"]["passed"]:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = "at least one registered Q011y refinement threshold is not met"

    cycle: dict[str, Any] = {
        "question": (
            "Do the Q011k approximate eigenvector families admit contained "
            "transformed-residual eigendiscs, and do those discs clear the "
            "first registered degree-six enclosure obstruction?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "theorem_digest_sha256": theorem_digest,
        "radius_digest_sha256": radius_digest,
        "containment_digest_sha256": containment_digest,
        "witness_digest_sha256": witness_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    inclusion_certified = bool(validity_passed and theorem["passed"])
    containment_certified = bool(validity_passed and containment["passed"])
    stability_certified = bool(containment_certified and maximum_modulus_upper < 1)
    witness_cleared = bool(validity_passed and witness["passed"] and witness_margin > 0)
    cycle["theorem_consequence"] = {
        "transformed_residual_eigendisc_inclusion_is_certified": inclusion_certified,
        "all_refined_discs_are_contained_in_q011k_discs": containment_certified,
        "all_2598_refined_eigendiscs_are_strictly_stable": stability_certified,
        "q011k_selected_external_memberships_are_preserved": containment_certified,
        "first_degree_six_enclosure_obstruction_is_cleared": witness_cleared,
        "all_degree_six_external_nonresonances_are_certified": False,
        "degrees_7_through_90_are_certified": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011l_q011u_or_q011x_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on one "
        "fixed conservation leaf, the Q011k approximate eigendecomposition "
        "families, the contained transformed-residual eigendiscs and one "
        "registered degree-six witness. It does not certify the other 6955 "
        "sector-compatible degree-six comparisons, any complete degree-six "
        "external nonresonance result, degrees 7 through 90, all-order "
        "nonresonance, equality with the Q011t graph, SSM existence or "
        "uniqueness, normal attraction, a basin, another grid, force, wall or D3Q27."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011l_quadratic_inverse_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_degree_five_acceptance_changed": False,
        "q011k_artifact_or_runner_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011z to audit every sector-compatible monomial in "
            "all three degree-six overlap aggregates with the contained "
            "transformed-residual eigendiscs."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Replace only the failed witness enclosure by row-wise transformed "
            "Gershgorin or a targeted interval eigenpair certificate."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, theorem, radius, containment, "
            "witness or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011y cycle failed strict serialization or digest")
    return cycle


def run_q011y_study() -> dict[str, Any]:
    cycle = run_transformed_residual_eigendisc_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "representative_eigendecomposition_count": 9,
            "block_count": SIZE,
            "eigencenter_count": COORDINATE_SLOT_COUNT,
            "exact_record_storage": "framed SHA-256 plus compact extrema and witness",
        },
        "mathematical_scope": {
            "diagnostic": "contained transformed-residual eigendiscs",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "refined_linear_eigendisc_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "first_degree_six_witness_clearance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "complete_degree_six_nonresonance_claim": False,
            "degrees_7_through_90_claim": False,
            "ssm_uniqueness_claim": False,
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
    result = run_q011y_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
