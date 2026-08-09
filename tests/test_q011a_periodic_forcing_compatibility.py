from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

import research.q011a_periodic_forcing_compatibility as q011a
from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    global_conserved_quantities,
    uniform_equilibrium,
)
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

forcing = q011a


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q011a_cycle() -> dict:
    return forcing.run_periodic_forcing_compatibility_audit()


def test_q011a_public_source_and_step_have_registered_moments() -> None:
    source = forcing.rest_linear_body_force_source(forcing.FORCE)
    moments = np.asarray(
        [
            np.sum(source),
            source @ D2Q9_VELOCITIES[:, 0],
            source @ D2Q9_VELOCITIES[:, 1],
        ]
    )
    np.testing.assert_array_equal(
        moments,
        np.asarray([0.0, forcing.FORCE[0], forcing.FORCE[1]]),
    )

    state = uniform_equilibrium(5, 7, np.zeros(3))
    unforced = forcing._unforced_filtered_step(state)
    forced = forcing.forced_filtered_bgk_periodic_step(
        state,
        forcing.OMEGA,
        forcing.ETA,
        forcing.FORCE,
    )
    increment = global_conserved_quantities(forced - unforced)
    np.testing.assert_allclose(
        increment,
        np.asarray([0.0, 35.0 * forcing.FORCE[0], 0.0]),
        atol=2.0e-15,
        rtol=0.0,
    )

    for invalid in ([1.0], [1.0, 2.0, 3.0], [np.nan, 0.0]):
        with pytest.raises(ValueError, match="body force"):
            forcing.rest_linear_body_force_source(invalid)


def test_q011a_exact_source_and_global_ledger_are_rational(
    q011a_cycle: dict,
) -> None:
    source = q011a_cycle["exact_source_audit"]
    exact_populations = [
        _fraction(record) for record in source["exact_source_populations"]
    ]
    exact_moments = [
        _fraction(record) for record in source["exact_source_moments"]
    ]
    global_increment = [
        _fraction(record)
        for record in source["exact_global_moment_increment"]
    ]

    assert exact_populations == [
        Fraction(0),
        Fraction(1, 2**40),
        Fraction(0),
        -Fraction(1, 2**40),
        Fraction(0),
        Fraction(1, 2**42),
        -Fraction(1, 2**42),
        -Fraction(1, 2**42),
        Fraction(1, 2**42),
    ]
    assert exact_moments == [
        Fraction(0),
        Fraction(3, 2**40),
        Fraction(0),
    ]
    assert global_increment == [
        Fraction(0),
        Fraction(867, 2**40),
        Fraction(0),
    ]
    assert source["source_population_bitwise_matches_exact_dyadics"]
    assert source["maximum_source_moment_residual"] == 0.0
    assert source["all_exact_identities_pass"]
    assert source["passed"]


def test_q011a_ten_probes_reproduce_the_source_and_momentum_increment(
    q011a_cycle: dict,
) -> None:
    audit = q011a_cycle["finite_probe_audit"]

    assert audit["probe_seed"] == 20260809
    assert audit["probe_count"] == 10
    assert audit["seeded_probe_count"] == 8
    assert len(audit["direction_sha256"]) == 64
    assert audit["maximum_state_difference_error"] <= (
        forcing.STATE_DIFFERENCE_TOLERANCE
    )
    assert audit["maximum_compensated_global_difference_error"] <= (
        forcing.GLOBAL_MOMENT_TOLERANCE
    )
    assert audit["all_probe_states_and_outputs_positive"]
    assert audit["all_helpers_match_shared_collision_path"]
    assert all(
        record["helper_matches_shared_collision_path"]
        for record in audit["records"]
    )
    assert audit["passed"]


def test_q011a_source_derivative_and_reference_spectrum_pass(
    q011a_cycle: dict,
) -> None:
    audit = q011a_cycle["derivative_and_spectrum_audit"]

    assert audit["derivative_direction_count"] == 4
    assert audit["derivative_steps"] == list(forcing.DERIVATIVE_STEPS)
    assert audit[
        "maximum_best_forced_unforced_relative_discrepancy"
    ] <= forcing.DERIVATIVE_RELATIVE_TOLERANCE
    assert audit["all_source_derivative_zero_checks_pass"]
    assert audit["maximum_forced_unforced_symbol_entry_difference"] == 0.0
    assert audit["unit_circle_tolerance"] == 1.0e-10
    assert audit["strict_unit_circle_count"] == 3
    assert all(
        record["wave_index"] == [0, 0]
        for record in audit["strict_unit_circle_records"]
    )
    assert audit["rest_is_not_a_forced_fixed_point"]
    assert audit["spectrum_is_reference_state_not_fixed_point_stability"]
    assert audit["spectrum_passed"]
    assert audit["passed"]


def test_q011a_exact_momentum_ledger_excludes_a_fixed_point(
    q011a_cycle: dict,
) -> None:
    audit = q011a_cycle["fixed_point_obstruction_audit"]
    increment = _fraction(
        audit["exact_global_mass_momentum_increment"][1]
    )
    residual_lower = _fraction(
        audit["exact_population_l1_fixed_point_residual_lower"]
    )

    assert increment == Fraction(867, 2**40)
    assert residual_lower == increment
    assert increment > 0
    assert audit["finite_probe_residuals_exceed_exact_lower_float"]
    assert audit["all_no_momentum_sink_checks_pass"]
    assert all(audit["no_momentum_sink_audit"].values())
    assert audit["all_exact_identities_pass"]
    assert audit["passed"]


def test_q011a_accepts_only_the_periodic_fixed_point_obstruction(
    q011a_cycle: dict,
) -> None:
    assert q011a_cycle["study_validity"] == "passed"
    assert q011a_cycle["hypothesis_outcome"] == "accepted"
    assert q011a_cycle["scientific_classification"] == (
        "nonzero-mean periodic body force is incompatible with a "
        "fixed point of the registered conservative map"
    )
    assert len(q011a_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"] for gate in q011a_cycle["validity_gates"].values()
    )
    assert len(q011a_cycle["hypothesis_gates"]) == 4
    assert all(
        gate["passed"]
        for gate in q011a_cycle["hypothesis_gates"].values()
    )
    consequence = q011a_cycle["theorem_consequence"]
    assert consequence["registered_exact_periodic_map_has_no_fixed_point"]
    assert not consequence["registered_fixed_point_newton_solve_should_start"]
    assert consequence[
        "rest_reference_jacobian_is_unchanged_by_additive_source"
    ]
    assert not consequence[
        "rest_reference_spectrum_is_forced_fixed_point_stability"
    ]
    assert not consequence["zero_mean_periodic_forcing_is_obstructed"]
    assert not consequence["wall_bounded_forcing_is_obstructed"]
    assert "not a bitwise finite-precision" in q011a_cycle["claim_boundary"]
    assert "non-fixed reference-state" in q011a_cycle["claim_boundary"]
    assert not any(q011a_cycle["preserved_prior_outcomes"].values())


def test_q011a_records_provenance_and_deterministic_digests(
    q011a_cycle: dict,
) -> None:
    runner_path = Path(q011a.__file__).resolve()
    source_sections = {
        "registered_parameters": q011a_cycle["registered_parameters"],
        "exact_source_audit": q011a_cycle["exact_source_audit"],
    }
    probe_sections = {
        "finite_probe_audit": q011a_cycle["finite_probe_audit"],
        "derivative_and_spectrum_audit": q011a_cycle[
            "derivative_and_spectrum_audit"
        ],
    }
    result_sections = {
        **source_sections,
        **probe_sections,
        "fixed_point_obstruction_audit": q011a_cycle[
            "fixed_point_obstruction_audit"
        ],
        "validity_gates": q011a_cycle["validity_gates"],
        "hypothesis_gates": q011a_cycle["hypothesis_gates"],
        "study_validity": q011a_cycle["study_validity"],
        "hypothesis_outcome": q011a_cycle["hypothesis_outcome"],
        "scientific_classification": q011a_cycle[
            "scientific_classification"
        ],
    }

    assert q011a._runner_source_metadata() == {
        "filename": "q011a_periodic_forcing_compatibility.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert source_metadata()["package_version"] == "0.1.0"
    assert q011a_cycle["source_digest_sha256"] == (
        forcing._canonical_json_sha256(source_sections)
    )
    assert q011a_cycle["probe_digest_sha256"] == (
        forcing._canonical_json_sha256(probe_sections)
    )
    assert q011a_cycle["result_digest_sha256"] == (
        forcing._canonical_json_sha256(result_sections)
    )
    assert all(
        len(q011a_cycle[key]) == 64
        for key in (
            "source_digest_sha256",
            "probe_digest_sha256",
            "result_digest_sha256",
        )
    )
    json.dumps(q011a_cycle, allow_nan=False)
