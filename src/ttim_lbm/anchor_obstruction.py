"""Sealed Q006m equivariant unique-anchor obstruction audit."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import conservative_checkerboard_filter
from .d2q9 import (
    collide_bgk,
    quarter_turn_population_matrix,
    stream_periodic,
    uniform_equilibrium,
)
from .full2d_chart import (
    SHADOW_SEED,
    Full2DQuadraticModel,
    build_full2d_quadratic_model,
)

Array = npt.NDArray[np.float64]
Site = tuple[int, int]

REGISTERED_SIZE = 17
REGISTERED_DIRECTION_COUNT = 32
REGISTERED_AMPLITUDES = (1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5, 1.0e-6, 1.0e-7)
REGISTERED_CHARTS = ("linear", "quadratic")
REGISTERED_STAGES = ("collision", "filter")
REGISTERED_SIGNS = ("plus", "minus")
REGISTERED_RECORD_COUNT = 384
REGISTERED_SIGNED_STATE_COUNT = 768
REGISTERED_STAGE_OBSERVATION_COUNT = 1536
GAP_SHRINK_RATIO_LIMIT = 1.0e-4

TRANSLATION_GENERATORS: tuple[tuple[str, Site], ...] = (
    ("translation_y", (1, 0)),
    ("translation_x", (0, 1)),
)


def _normalized_directions() -> Array:
    rng = np.random.default_rng(SHADOW_SEED)
    directions = rng.normal(size=(REGISTERED_DIRECTION_COUNT, 24))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
    )


def anchor_metrics(state: npt.ArrayLike) -> dict[str, Any]:
    """Return the row-major q0 argmax, exact multiplicity, and top-two gap."""

    populations = np.asarray(state, dtype=np.float64)
    if populations.ndim != 3 or populations.shape[-1] != 9:
        raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
    rest = populations[..., 0]
    flat = rest.ravel()
    if flat.size < 2:
        raise ValueError("anchor audit requires at least two lattice sites")
    maximum = float(np.max(flat))
    maximum_index = int(np.argmax(flat))
    largest_two = np.partition(flat, -2)[-2:]
    anchor = tuple(
        int(value) for value in np.unravel_index(maximum_index, rest.shape)
    )
    return {
        "anchor": list(anchor),
        "maximum_q0": maximum,
        "maximum_multiplicity": int(np.count_nonzero(flat == maximum)),
        "top_two_gap": float(np.max(largest_two) - np.min(largest_two)),
    }


def _translate_state(state: Array, shift: Site) -> Array:
    return np.roll(state, shift=shift, axis=(0, 1))


def _translate_site(site: Site, shift: Site, size: int) -> Site:
    return (site[0] + shift[0]) % size, (site[1] + shift[1]) % size


def _quarter_turn(state: Array) -> Array:
    size = state.shape[0]
    target_y, target_x = np.indices((size, size))
    pulled_back = state[(-target_x) % size, target_y]
    rotation = quarter_turn_population_matrix()
    return np.einsum("qr,xyr->xyq", rotation, pulled_back)


def _quarter_turn_site(site: Site, size: int) -> Site:
    return site[1], (-site[0]) % size


def _fixed_sites(size: int, shift: Site) -> list[list[int]]:
    sites = [
        (y, x)
        for y in range(size)
        for x in range(size)
        if _translate_site((y, x), shift, size) == (y, x)
    ]
    return [[y, x] for y, x in sites]


def _translation_action_audit(base: Array) -> dict[str, Any]:
    size = base.shape[0]
    generator_records: dict[str, Any] = {}
    fixed_site_sets: list[set[Site]] = []
    base_anchor = tuple(anchor_metrics(base)["anchor"])
    for name, shift in TRANSLATION_GENERATORS:
        fixed_sites = _fixed_sites(size, shift)
        fixed_site_sets.append({tuple(site) for site in fixed_sites})
        mapped_sites = [
            _translate_site((y, x), shift, size)
            for y in range(size)
            for x in range(size)
        ]
        transformed = _translate_state(base, shift)
        transformed_anchor = tuple(anchor_metrics(transformed)["anchor"])
        expected_anchor = _translate_site(base_anchor, shift, size)
        cycled = base.copy()
        for _ in range(size):
            cycled = _translate_state(cycled, shift)
        generator_records[name] = {
            "shift": list(shift),
            "fixed_sites": fixed_sites,
            "fixed_site_count": len(fixed_sites),
            "mapped_site_count": len(set(mapped_sites)),
            "expected_mapped_site_count": size * size,
            "full_cycle_bitwise_identity": bool(np.array_equal(cycled, base)),
            "uniform_bitwise_invariant": bool(np.array_equal(transformed, base)),
            "uniform_invariance_error": float(np.max(np.abs(transformed - base))),
            "row_major_anchor": list(base_anchor),
            "expected_transformed_anchor": list(expected_anchor),
            "actual_transformed_anchor": list(transformed_anchor),
            "row_major_anchor_covariant": transformed_anchor == expected_anchor,
        }
    common_fixed_sites = set.intersection(*fixed_site_sets)
    transformed_c4 = _quarter_turn(base)
    c4_anchor = tuple(anchor_metrics(transformed_c4)["anchor"])
    expected_c4_anchor = _quarter_turn_site(base_anchor, size)
    return {
        "site_set": f"Z_{size} x Z_{size}",
        "site_count": size * size,
        "generators": generator_records,
        "common_translation_fixed_sites": [
            list(site) for site in sorted(common_fixed_sites)
        ],
        "common_translation_fixed_site_count": len(common_fixed_sites),
        "row_major_translation_covariance_failure_count": sum(
            not record["row_major_anchor_covariant"]
            for record in generator_records.values()
        ),
        "quarter_turn_auxiliary": {
            "uniform_bitwise_invariant": bool(np.array_equal(transformed_c4, base)),
            "uniform_invariance_error": float(
                np.max(np.abs(transformed_c4 - base))
            ),
            "row_major_anchor": list(base_anchor),
            "expected_transformed_anchor": list(expected_c4_anchor),
            "actual_transformed_anchor": list(c4_anchor),
            "row_major_anchor_covariant": c4_anchor == expected_c4_anchor,
            "gating": False,
        },
    }


def _raw_stages(state: Array, omega: float, eta: float) -> dict[str, Array]:
    collision = collide_bgk(state, omega)
    filtered = conservative_checkerboard_filter(stream_periodic(collision), eta)
    return {"collision": collision, "filter": filtered}


def _signed_state_record(
    state: Array,
    omega: float,
    eta: float,
) -> dict[str, Any]:
    stages = _raw_stages(state, omega, eta)
    observed = [state, *stages.values()]
    return {
        "initial_minimum_population": float(np.min(state)),
        "minimum_population_over_initial_and_stages": float(
            min(np.min(value) for value in observed)
        ),
        "all_values_finite": bool(
            all(np.all(np.isfinite(value)) for value in observed)
        ),
        "stages": {
            stage: anchor_metrics(stage_state)
            for stage, stage_state in stages.items()
        },
    }


def _amplitude_records(model: Full2DQuadraticModel) -> list[dict[str, Any]]:
    directions = _normalized_directions()
    records = []
    for chart_name in REGISTERED_CHARTS:
        chart = model.linear_chart if chart_name == "linear" else model.chart
        for direction_index, direction in enumerate(directions):
            for amplitude in REGISTERED_AMPLITUDES:
                signed_states = {}
                for sign_name, sign in (("plus", 1.0), ("minus", -1.0)):
                    state = chart.evaluate(sign * amplitude * direction).reshape(
                        model.size,
                        model.size,
                        9,
                    )
                    signed_states[sign_name] = _signed_state_record(
                        state,
                        model.omega,
                        model.eta,
                    )
                records.append(
                    {
                        "chart": chart_name,
                        "direction_index": direction_index,
                        "direction": direction.tolist(),
                        "amplitude": amplitude,
                        "signed_states": signed_states,
                        "plus_minus_anchor_match": {
                            stage: (
                                signed_states["plus"]["stages"][stage]["anchor"]
                                == signed_states["minus"]["stages"][stage]["anchor"]
                            )
                            for stage in REGISTERED_STAGES
                        },
                    }
                )
    return records


def _ladder_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ladders = []
    for chart in REGISTERED_CHARTS:
        for stage in REGISTERED_STAGES:
            for sign in REGISTERED_SIGNS:
                amplitude_records = []
                for amplitude in REGISTERED_AMPLITUDES:
                    selected = [
                        record
                        for record in records
                        if record["chart"] == chart
                        and record["amplitude"] == amplitude
                    ]
                    gaps = np.asarray(
                        [
                            record["signed_states"][sign]["stages"][stage][
                                "top_two_gap"
                            ]
                            for record in selected
                        ],
                        dtype=np.float64,
                    )
                    anchors = {
                        tuple(
                            record["signed_states"][sign]["stages"][stage][
                                "anchor"
                            ]
                        )
                        for record in selected
                    }
                    multiplicities = [
                        record["signed_states"][sign]["stages"][stage][
                            "maximum_multiplicity"
                        ]
                        for record in selected
                    ]
                    amplitude_records.append(
                        {
                            "amplitude": amplitude,
                            "direction_count": len(selected),
                            "minimum_gap": float(np.min(gaps)),
                            "median_gap": float(np.median(gaps)),
                            "maximum_gap": float(np.max(gaps)),
                            "all_gaps_finite": bool(np.all(np.isfinite(gaps))),
                            "maximum_multiplicity": max(multiplicities),
                            "distinct_anchor_count": len(anchors),
                        }
                    )
                largest_amplitude_gap = amplitude_records[0]["maximum_gap"]
                smallest_amplitude_gap = amplitude_records[-1]["maximum_gap"]
                ratio = float(smallest_amplitude_gap / largest_amplitude_gap)
                finite = all(
                    item["all_gaps_finite"] for item in amplitude_records
                ) and np.isfinite(ratio)
                ladders.append(
                    {
                        "chart": chart,
                        "stage": stage,
                        "sign": sign,
                        "amplitudes": amplitude_records,
                        "smallest_to_largest_maximum_gap_ratio": ratio,
                        "ratio_limit": GAP_SHRINK_RATIO_LIMIT,
                        "passed": bool(
                            finite and ratio <= GAP_SHRINK_RATIO_LIMIT
                        ),
                    }
                )
    return ladders


def _anchor_match_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for chart in REGISTERED_CHARTS:
        for stage in REGISTERED_STAGES:
            for amplitude in REGISTERED_AMPLITUDES:
                selected = [
                    record
                    for record in records
                    if record["chart"] == chart
                    and record["amplitude"] == amplitude
                ]
                match_count = sum(
                    record["plus_minus_anchor_match"][stage]
                    for record in selected
                )
                summary.append(
                    {
                        "chart": chart,
                        "stage": stage,
                        "amplitude": amplitude,
                        "match_count": match_count,
                        "direction_count": len(selected),
                        "match_rate": float(match_count / len(selected)),
                    }
                )
    return summary


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_anchor_obstruction_audit() -> dict[str, Any]:
    """Run the sealed Q006m group-action and shrinking-gap audit."""

    model = build_full2d_quadratic_model()
    base = model.chart.base.reshape(model.size, model.size, 9)
    uniform_reference = uniform_equilibrium(model.size, model.size, [0.0, 0.0, 0.0])
    base_reference_error = float(np.max(np.abs(base - uniform_reference)))
    base_reference_bitwise_equal = bool(np.array_equal(base, uniform_reference))
    base_stages = _raw_stages(base, model.omega, model.eta)
    uniform_records = {
        "base": anchor_metrics(base),
        "collision": anchor_metrics(base_stages["collision"]),
        "filter": anchor_metrics(base_stages["filter"]),
        "chart_base_reference_error": base_reference_error,
        "chart_base_reference_bitwise_equal": base_reference_bitwise_equal,
    }
    group_action = _translation_action_audit(base)
    records = _amplitude_records(model)
    ladders = _ladder_records(records)
    anchor_matches = _anchor_match_summary(records)
    signed_state_count = sum(len(record["signed_states"]) for record in records)
    stage_observation_count = sum(
        len(signed_state["stages"])
        for record in records
        for signed_state in record["signed_states"].values()
    )
    minimum_population = min(
        signed_state["minimum_population_over_initial_and_stages"]
        for record in records
        for signed_state in record["signed_states"].values()
    )
    all_registered_values_finite = all(
        signed_state["all_values_finite"]
        for record in records
        for signed_state in record["signed_states"].values()
    )
    maximum_uniform_translation_error = max(
        record["uniform_invariance_error"]
        for record in group_action["generators"].values()
    )
    uniform_translation_bitwise_invariant = all(
        record["uniform_bitwise_invariant"]
        for record in group_action["generators"].values()
    )
    maximum_gap_ratio = max(
        record["smallest_to_largest_maximum_gap_ratio"] for record in ladders
    )
    failed_gap_ladders = [
        {
            "chart": record["chart"],
            "stage": record["stage"],
            "sign": record["sign"],
        }
        for record in ladders
        if not record["passed"]
    ]
    summary = {
        "direction_amplitude_record_count": len(records),
        "signed_state_count": signed_state_count,
        "stage_observation_count": stage_observation_count,
        "minimum_population": minimum_population,
        "all_registered_values_finite": all_registered_values_finite,
        "uniform_q0_maximum_multiplicity": uniform_records["base"][
            "maximum_multiplicity"
        ],
        "uniform_q0_top_two_gap": uniform_records["base"]["top_two_gap"],
        "translation_fixed_site_counts": {
            name: record["fixed_site_count"]
            for name, record in group_action["generators"].items()
        },
        "common_translation_fixed_site_count": group_action[
            "common_translation_fixed_site_count"
        ],
        "maximum_uniform_translation_invariance_error": (
            maximum_uniform_translation_error
        ),
        "uniform_translation_bitwise_invariant": (
            uniform_translation_bitwise_invariant
        ),
        "row_major_translation_covariance_failure_count": group_action[
            "row_major_translation_covariance_failure_count"
        ],
        "gap_ladder_count": len(ladders),
        "failed_gap_ladder_count": len(failed_gap_ladders),
        "failed_gap_ladders": failed_gap_ladders,
        "maximum_smallest_to_largest_gap_ratio": maximum_gap_ratio,
    }
    serializable_probe = {
        "uniform_records": uniform_records,
        "group_action": group_action,
        "records": records,
        "gap_ladders": ladders,
        "anchor_match_summary": anchor_matches,
        "summary": summary,
    }
    validity_gates = {
        "registered_enumeration": {
            "value": {
                "direction_amplitude_record_count": len(records),
                "signed_state_count": signed_state_count,
                "stage_observation_count": stage_observation_count,
            },
            "threshold": {
                "direction_amplitude_record_count": REGISTERED_RECORD_COUNT,
                "signed_state_count": REGISTERED_SIGNED_STATE_COUNT,
                "stage_observation_count": REGISTERED_STAGE_OBSERVATION_COUNT,
            },
            "passed": (
                len(records) == REGISTERED_RECORD_COUNT
                and signed_state_count == REGISTERED_SIGNED_STATE_COUNT
                and stage_observation_count == REGISTERED_STAGE_OBSERVATION_COUNT
            ),
        },
        "uniform_reference_consistency": {
            "value": {
                "maximum_error": base_reference_error,
                "bitwise_equal": base_reference_bitwise_equal,
            },
            "threshold": {"maximum_error": 0.0, "bitwise_equal": True},
            "passed": base_reference_error == 0.0 and base_reference_bitwise_equal,
        },
        "translation_action_consistency": {
            "value": {
                name: {
                    "mapped_site_count": record["mapped_site_count"],
                    "full_cycle_bitwise_identity": record[
                        "full_cycle_bitwise_identity"
                    ],
                }
                for name, record in group_action["generators"].items()
            },
            "threshold": {
                "mapped_site_count": model.size * model.size,
                "full_cycle_bitwise_identity": True,
            },
            "passed": all(
                record["mapped_site_count"] == model.size * model.size
                and record["full_cycle_bitwise_identity"]
                for record in group_action["generators"].values()
            ),
        },
        "positive_finite_registered_states": {
            "value": {
                "minimum_population": minimum_population,
                "all_values_finite": all_registered_values_finite,
            },
            "threshold": {
                "minimum_population_strictly_greater_than": 0.0,
                "all_values_finite": True,
            },
            "passed": minimum_population > 0.0 and all_registered_values_finite,
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    hypothesis_gates = {
        "uniform_maximum_tie": {
            "value": {
                "maximum_multiplicity": summary[
                    "uniform_q0_maximum_multiplicity"
                ],
                "top_two_gap": summary["uniform_q0_top_two_gap"],
            },
            "threshold": {
                "maximum_multiplicity": model.size * model.size,
                "top_two_gap": 0.0,
            },
            "passed": (
                summary["uniform_q0_maximum_multiplicity"]
                == model.size * model.size
                and summary["uniform_q0_top_two_gap"] == 0.0
            ),
        },
        "free_translation_action": {
            "value": {
                "generator_fixed_site_counts": summary[
                    "translation_fixed_site_counts"
                ],
                "common_fixed_site_count": summary[
                    "common_translation_fixed_site_count"
                ],
            },
            "threshold": {
                "generator_fixed_site_counts": {
                    name: 0 for name, _ in TRANSLATION_GENERATORS
                },
                "common_fixed_site_count": 0,
            },
            "passed": (
                all(
                    count == 0
                    for count in summary["translation_fixed_site_counts"].values()
                )
                and summary["common_translation_fixed_site_count"] == 0
            ),
        },
        "uniform_translation_invariance": {
            "value": {
                "maximum_error": maximum_uniform_translation_error,
                "bitwise_invariant": uniform_translation_bitwise_invariant,
            },
            "threshold": {"maximum_error": 0.0, "bitwise_invariant": True},
            "passed": (
                maximum_uniform_translation_error == 0.0
                and uniform_translation_bitwise_invariant
            ),
        },
        "row_major_translation_covariance_failure": {
            "value": summary[
                "row_major_translation_covariance_failure_count"
            ],
            "threshold": len(TRANSLATION_GENERATORS),
            "passed": (
                summary["row_major_translation_covariance_failure_count"]
                == len(TRANSLATION_GENERATORS)
            ),
        },
        "shrinking_anchor_gap": {
            "value": {
                "ladder_count": len(ladders),
                "failed_ladder_count": len(failed_gap_ladders),
                "maximum_ratio": maximum_gap_ratio,
            },
            "threshold": {
                "ladder_count": 8,
                "failed_ladder_count": 0,
                "maximum_ratio": GAP_SHRINK_RATIO_LIMIT,
            },
            "passed": len(ladders) == 8 and not failed_gap_ladders,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006m obstruction audit validity failure"
        decision = (
            "A registered enumeration, uniform-reference, group-action, "
            "positivity, finiteness, or serialization validity gate failed."
        )
        next_change = "Repair the first Q006m validity failure without tuning it."
    elif hypothesis_passed:
        outcome = "accepted"
        classification = "equivariant unique-anchor obstruction confirmed"
        decision = (
            "The translation-fixed uniform state has no translation-fixed site, "
            "so an equivariant unique-site selector has no value there; the "
            "registered finite ladder additionally shows the q0 anchor gap "
            "collapsing toward that tie."
        )
        next_change = (
            "Preregister a comparison between an anchor-free smooth correction "
            "and an explicit floating-point forward-error budget."
        )
    else:
        outcome = "rejected"
        classification = "unique-anchor obstruction not established"
        decision = (
            "The valid audit did not establish every registered fixed-point, "
            "row-major covariance, and shrinking-gap witness."
        )
        next_change = "Stop continuation and isolate the first failed Q006m gate."
    return {
        "question": (
            "Can a periodic translation-equivariant unique-site anchor selector "
            "extend continuously or differentiably to the uniform equilibrium?"
        ),
        "hypothesis": (
            "The uniform state is fixed by translations while the periodic site "
            "action has no fixed site, obstructing any equivariant unique anchor."
        ),
        "registered_setup": {
            "size": model.size,
            "omega": model.omega,
            "eta": model.eta,
            "site_set": f"Z_{model.size} x Z_{model.size}",
            "translation_generators": [
                {"name": name, "shift": list(shift)}
                for name, shift in TRANSLATION_GENERATORS
            ],
            "direction_seed": SHADOW_SEED,
            "direction_count": REGISTERED_DIRECTION_COUNT,
            "chart_types": list(REGISTERED_CHARTS),
            "amplitudes": list(REGISTERED_AMPLITUDES),
            "signs": list(REGISTERED_SIGNS),
            "raw_stages": list(REGISTERED_STAGES),
            "filter_input": "uncorrected collision followed by periodic streaming",
            "anchor_rule": "row-major maximum q0 site",
            "gap_gate_ratio_limit": GAP_SHRINK_RATIO_LIMIT,
        },
        "uniform_records": uniform_records,
        "group_action": group_action,
        "direction_amplitude_records": records,
        "gap_ladders": ladders,
        "plus_minus_anchor_match_summary": anchor_matches,
        "summary": summary,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "The exact fixed-point contradiction rules out only unique-site "
            "selectors at the uniform equilibrium. The finite amplitude ladder "
            "is diagnostic, not an asymptotic proof, and this result neither "
            "rules out anchor-free equivariant arithmetic nor revises Q006i-Q006l."
        ),
    }
