from __future__ import annotations

from fractions import Fraction

import pytest

import research.q007x_mpfr_backend as backend
import research.q007x_mpfr_fixed_leaf as q007x
from research.q007y_distributed_conservation_repair import (
    REPAIR_QUANTUM,
    TARGET_CONSERVED,
    balanced_unit_distribution,
    repair_conserved_state,
    run_q007y_study,
    solve_diagonal_repair_units,
)


@pytest.mark.parametrize(
    ("moments", "expected_free", "expected_diagonal"),
    [
        ((0, 0, 0), 0, (0, 0, 0, 0)),
        ((2312, 0, 0), 0, (578, 578, 578, 578)),
        ((1, 1, 1), 1, (1, 0, 0, 0)),
        ((2, 0, 0), -2, (0, 1, 0, 1)),
        (
            (-12949, 37, -21),
            -19,
            (-3238, -3247, -3246, -3218),
        ),
    ],
)
def test_q007y_integer_solver_reproduces_moments_and_registered_optimum(
    moments: tuple[int, int, int],
    expected_free: int,
    expected_diagonal: tuple[int, int, int, int],
) -> None:
    solution = solve_diagonal_repair_units(*moments)
    a, b, c, d = solution.diagonal_units

    assert solution.free_unit == expected_free
    assert solution.diagonal_units == expected_diagonal
    assert (a + b + c + d, a - b - c + d, a + b - c - d) == moments
    assert solution.objective == (
        sum(abs(value) for value in solution.diagonal_units),
        max(abs(value) for value in solution.diagonal_units),
        abs(solution.free_unit),
        solution.free_unit,
    )
    assert solution.objective[0] <= sum(abs(value) for value in moments) + 2

    for free_unit in range(-solution.search_limit, solution.search_limit + 1):
        numerators = (
            moments[0] + moments[1] + moments[2] + free_unit,
            moments[0] - moments[1] + moments[2] - free_unit,
            moments[0] - moments[1] - moments[2] + free_unit,
            moments[0] + moments[1] - moments[2] - free_unit,
        )
        if any(value % 4 for value in numerators):
            continue
        candidate = tuple(value // 4 for value in numerators)
        candidate_objective = (
            sum(abs(value) for value in candidate),
            max(abs(value) for value in candidate),
            abs(free_unit),
            free_unit,
        )
        assert solution.objective <= candidate_objective


def test_q007y_integer_solver_rejects_wrong_types_and_parity() -> None:
    with pytest.raises(TypeError, match="integer"):
        solve_diagonal_repair_units(True, 0, 0)
    with pytest.raises(TypeError, match="integer"):
        solve_diagonal_repair_units(0, 0.0, 0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="parity"):
        solve_diagonal_repair_units(1, 0, 0)


@pytest.mark.parametrize(
    ("total", "count", "expected"),
    [
        (3, 5, (1, 1, 1, 0, 0)),
        (-3, 5, (0, 0, -1, -1, -1)),
        (10, 5, (2, 2, 2, 2, 2)),
        (-1, 1, (-1,)),
    ],
)
def test_q007y_balanced_distribution_is_row_major_and_exact(
    total: int,
    count: int,
    expected: tuple[int, ...],
) -> None:
    observed = balanced_unit_distribution(total, count)

    assert observed == expected
    assert sum(observed) == total
    assert max(observed) - min(observed) <= 1


def test_q007y_balanced_distribution_rejects_invalid_arguments() -> None:
    with pytest.raises(TypeError, match="integer"):
        balanced_unit_distribution(1, True)
    with pytest.raises(ValueError, match="positive"):
        balanced_unit_distribution(1, 0)


def test_q007y_repair_restores_the_encoded_rest_probe_exactly() -> None:
    rest = q007x._build_probes()[0][1]
    concrete = backend.MPFRD2Q9Backend()
    encoded, _audit = concrete.encode_fraction_state(rest)
    repaired, record = repair_conserved_state(encoded)

    assert REPAIR_QUANTUM == Fraction(1, 2**90)
    assert record["requested_units"] == {
        "mass": -2312,
        "momentum_x": 0,
        "momentum_y": 0,
    }
    assert record["solution"]["diagonal_units"] == [-578] * 4
    assert record["addition_count"] == 4 * 17 * 17
    assert record["exact_addition_count"] == record["addition_count"]
    assert record["same_binade_count"] == record["addition_count"]
    assert record["strict_positive_count"] == record["addition_count"]
    assert record["exact_conservation_restored"]
    assert record["passed"]
    assert q007x._global_conserved(
        q007x._mpfr_to_fraction_array(repaired)
    ) == TARGET_CONSERVED


def test_q007y_study_separates_finite_repair_from_the_base_budget() -> None:
    artifact = run_q007y_study()
    cycle = artifact["cycle"]

    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "not_certified"
    assert cycle["scientific_classification"] == (
        "distributed MPFR-85 repair restores the registered fixed-leaf "
        "probes but not the Q007w tube-wide base budget"
    )
    assert len(cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 7
    assert sum(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    ) == 5
    campaign = cycle["finite_campaign"]
    assert campaign["passed"]
    assert campaign["probe_count"] == 4
    assert all(campaign["summary"].values())
    tube = cycle["tube_wide_repair_bound"]
    assert tube["passed"]
    assert tube["repair_map_well_defined_on_registered_tube"]
    assert tube["normal_reentry_passed"]
    assert not tube["base_reentry_passed"]
    assert tube["raw_wiener_error_upper"]["float"] == pytest.approx(
        2.706739822688458e-22
    )
    assert tube["repair_wiener_addition_upper"]["float"] == pytest.approx(
        4.959477689155467e-22
    )
    assert tube["base_margin_utilization"]["float"] == pytest.approx(
        2.326054260951996
    )
    assert tube["normal_margin_utilization"]["float"] == pytest.approx(
        2.507922842743146e-7
    )
    assert not cycle["theorem_consequence"][
        "all_iterate_repaired_mpfr85_q007s_tube_invariance"
    ]
