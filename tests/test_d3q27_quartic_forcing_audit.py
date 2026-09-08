"""Norm/coverage diagnostics must preserve, not dismiss, tiny-column failures."""

import numpy as np
import pytest

from research import d3q27_quartic_forcing_audit as audit


def arrays():
    right = np.zeros((27, 2), dtype=complex)
    right[0] = [1e-16, 1]
    left = right.copy()
    left[-1] = [1e-19, 1e-9]
    main = {
        "forcing": left,
        "collision": left,
        "composition": np.zeros_like(left),
        "keys": np.array([[0, 0, 0, 0], [100, 101, 102, 103]], dtype=np.int64),
        "terms": np.vstack((left, np.zeros((6 * 27, 2), dtype=complex))),
    }
    return main, {"forcing": right, "collision": right, "composition": np.zeros_like(left)}


def test_tiny_absolute_error_remains_a_failure_at_the_original_floor():
    main, other = arrays()
    row = audit.column(main, other, 0)
    assert row["reference_below_floor"] and row["failed_original_H1_bound"]
    assert row["relative_error"] == pytest.approx(1e-5)
    assert row["difference_norm"] == pytest.approx(1e-19)


def test_larger_absolute_error_can_pass_without_reclassifying_tiny_case():
    main, other = arrays()
    rows = [{"group": (0, 0, 0, 0), **audit.column(main, other, j)} for j in range(2)]
    result = audit.summarize(rows)
    assert result["failed_columns"] == result["failed_below_floor_columns"] == 1
    assert result["failed_at_or_above_floor_columns"] == 0
    assert result["maximum_absolute_difference"] > rows[0]["difference_norm"]
    assert result["maximum_relative_error_location"]["column"] == 0
    assert result["maximum_absolute_difference_location"]["column"] == 1
    assert result["failure_cause"] == "not_established_by_stored_vector_comparison"


def test_last_population_and_last_input_coordinate_are_included():
    main, other = arrays()
    row = audit.column(main, other, 1)
    assert row["coordinates"][-1] == 103
    assert row["difference_norm"] == pytest.approx(1e-9)
    main["forcing"][-1, -1] = 1e-6j
    assert audit.column(main, other, 1)["failed_original_H1_bound"]


@pytest.mark.parametrize(
    "bad", [np.zeros(26), np.r_[np.zeros(26), np.nan], np.r_[np.zeros(26), np.inf]]
)
def test_incomplete_or_nonfinite_vectors_cannot_be_normed(bad):
    with pytest.raises(ValueError):
        audit.norm(bad)


def test_exact_zero_and_compensated_complex_norm():
    assert audit.norm(np.zeros(27)) == 0
    value = np.zeros(27, dtype=complex)
    value[0] = 3 + 4j
    value[-1] = 12j
    assert audit.norm(value) == 13
    with pytest.raises(ValueError, match="complete column"):
        audit.summarize([])
