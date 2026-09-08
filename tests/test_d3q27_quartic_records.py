"""Full scientific record controls, not the formal all-1120 campaign."""

from copy import deepcopy

import numpy as np
import pytest

from research import d3q27_quartic_jets as jets
from research import d3q27_quartic_operator as operator
from research import d3q27_quartic_records as r
from research import d3q27_quartic_solve as solve
from research import q012h0_d3q27_quartic_census as census


@pytest.fixture(
    scope="module",
    params=[
        (p, groups)
        for p in (23, 27)
        for groups in ((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2), (0, 1, 2, 3))
    ],
)
def numeric(request):
    p, groups = request.param
    case = ((2, 2, 2, 2), groups, p)
    main, arrays = r.main_operator(case)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(operator, "build_product", lambda *a: pytest.fail("used orbit kernel"))
        patch.setattr(solve, "solve_known", lambda *a: pytest.fail("used main solve"))
        patch.setattr(np, "kron", lambda *a: pytest.fail("used Kronecker kernel"))
        worker = r.reference_operator(case, arrays)
    return case, main, arrays, worker


def test_full_operator_witnesses_are_independently_checked(numeric):
    _, main, arrays, worker = numeric
    comparison = r.compare_operator(main, arrays, worker)
    assert all(
        comparison[key]
        for key in (
            "identity_equal",
            "independent_witnesses_equal",
            "diagnostics_equal",
            "H1",
            "H3",
        )
    )
    assert comparison["taylor_scaled_error"] <= 5e-12
    for method in r.METHODS:
        assert census.same(
            main["methods"][method]["exact_full"], worker["methods"][method]["full"]["proof"]
        )


def test_primary_full_records_reproduce_deterministically(numeric):
    case, main, arrays, _ = numeric
    again, other = r.main_operator(case)
    assert census.same(main, again)
    assert set(arrays) == set(other)
    for key in arrays:
        assert np.array_equal(arrays[key], other[key]), key


def test_altered_last_numerical_witness_is_detected(numeric):
    case, main, original, _ = numeric
    arrays = {key: value.copy() for key, value in original.items()}
    arrays["refined"][-1, -1] += 0.01
    altered = r.reference_operator(case, arrays)
    comparison = r.compare_operator(main, arrays, altered)
    assert not comparison["independent_witnesses_equal"]
    assert not comparison["H3"]


def test_saved_full_homological_matrix_is_not_implicit_or_unchecked(numeric):
    case, main, original, worker = numeric
    dimension = worker["svd"]["operator_dimension"]
    assert original["homological_operator"].shape == (dimension, dimension)
    assert worker["input_errors"]["homological_operator"] <= 5e-12
    arrays = {key: value.copy() for key, value in original.items()}
    arrays["homological_operator"][-1, -1] += 0.01
    altered = r.reference_operator(case, arrays)
    assert not r.compare_operator(main, arrays, altered)["H1"]


@pytest.fixture(scope="module", params=r.FORCING_CASES)
def forcing(request):
    main = r.main_forcing(request.param)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(jets, "Manufactured", lambda *a: pytest.fail("used main map"))
        patch.setattr(jets, "Jet", lambda *a: pytest.fail("used main derivative"))
        patch.setattr(operator, "build_product", lambda *a: pytest.fail("used orbit kernel"))
        patch.setattr(np, "kron", lambda *a: pytest.fail("used Kronecker kernel"))
        worker = r.reference_forcing(request.param)
    return main, worker


def test_all_known_and_forcing_columns_have_independent_full_evidence(forcing):
    main, worker = forcing
    compared = r.compare_forcing(main, worker)
    assert compared["H2"] and compared["nonzero_and_mutation_coverage"]
    assert all(compared["all_coefficients_equal"].values())
    assert len(main["forcing"]["columns"]) == 330
    assert [len(main["known"][str(d)]["h"]) for d in (2, 3, 4)] == [36, 120, 330]
    assert main["controls"]["forcing_conjugacy"]
    assert set(main["groups"]) == set(r.GROUP_NAMES)


@pytest.mark.parametrize("field", ("forcing", "known", "transform", "inverse"))
def test_last_exact_coefficient_or_basis_entry_is_not_ignored(forcing, field):
    main, original = forcing
    worker = deepcopy(original)
    value = (
        worker[field]["columns"][-1][-1]
        if field == "forcing"
        else worker[field]["4"]["h"][-1][-1]
        if field == "known"
        else worker[field][-1][-1]
    )
    value[0] = str(int(value[0]) + 1)
    assert not r.compare_forcing(main, worker)["H2"]


def test_nonzero_coverage_and_exact_multiplicity_are_not_optional(forcing):
    main, worker = forcing
    altered = deepcopy(main)
    altered["controls"]["mutation_counts"]["omit_G3"] = 0
    assert not r.compare_forcing(altered, worker)["nonzero_and_mutation_coverage"]
    altered = deepcopy(main)
    altered["group_norms_squared"][r.GROUP_NAMES[-1]] = ["0", "1"]
    assert not r.compare_forcing(altered, worker)["H2"]


def test_independent_svd_classifies_all_three_negative_problems(monkeypatch):
    monkeypatch.setattr(np, "kron", lambda *a: pytest.fail("negative reference used Kronecker"))
    values = r.reference_negatives()
    assert [value["status"] for value in values] == [
        "singular_compatible",
        "singular_incompatible",
        "nonsingular_ill_conditioned",
    ]
    assert values[0]["numerical_rank"] == values[1]["numerical_rank"] == 1
    assert values[2]["numerical_rank"] == 2 and values[2]["condition_number"] > 1e8


def test_inventory_is_full_and_has_no_duplicate_case_identifiers():
    assert len(r.OPERATOR_CASES) == len(set(r.OPERATOR_CASES)) == 1120
    assert len(r.FORCING_CASES) == len(set(r.FORCING_CASES)) == 4
