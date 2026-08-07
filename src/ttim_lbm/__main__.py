"""Command-line entry point for reproducible D2Q9 research studies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .experiments import run_d2q9_baseline
from .studies import (
    run_q004b_and_manufactured_study,
    run_q005_study,
    run_q006c_study,
    run_q006f_study,
    run_q006g_study,
    run_q006h_study,
    run_q006i_study,
    run_q006j_study,
    run_q006k_study,
    run_q006l_study,
    run_q006m_study,
    run_q006n_study,
    run_q006o_study,
    run_q006p_study,
    run_q006q_study,
    run_q006r_study,
    run_q006s_study,
    run_q007a_study,
    run_q007b1_study,
    run_q007b_study,
    run_q007c1_study,
    run_q007c2_study,
    run_q007c_study,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--omega",
        type=float,
        help=(
            "BGK relaxation for the baseline study; follow-on studies use "
            "their registered sweeps"
        ),
    )
    parser.add_argument(
        "--study",
        choices=(
            "baseline",
            "q004b",
            "q005",
            "q006s",
            "q006r",
            "q006n",
            "q006c",
            "q006f",
            "q006g",
            "q006h",
            "q006i",
            "q006j",
            "q006k",
            "q006l",
            "q006m",
            "q006o",
            "q006p",
            "q006q",
            "q007a",
            "q007b",
            "q007b1",
            "q007c",
            "q007c1",
            "q007c2",
        ),
        default="baseline",
    )
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.study != "baseline" and arguments.omega is not None:
        parser.error("--omega is only valid with --study baseline")
    if arguments.study == "baseline":
        result = run_d2q9_baseline(
            omega=1.2 if arguments.omega is None else arguments.omega
        )
    elif arguments.study == "q004b":
        result = run_q004b_and_manufactured_study()
    elif arguments.study == "q005":
        result = run_q005_study()
    elif arguments.study == "q006s":
        result = run_q006s_study()
    elif arguments.study == "q006r":
        result = run_q006r_study()
    elif arguments.study == "q006n":
        result = run_q006n_study()
    elif arguments.study == "q006c":
        result = run_q006c_study()
    elif arguments.study == "q006f":
        result = run_q006f_study()
    elif arguments.study == "q006g":
        result = run_q006g_study()
    elif arguments.study == "q006h":
        result = run_q006h_study()
    elif arguments.study == "q006i":
        result = run_q006i_study()
    elif arguments.study == "q006j":
        result = run_q006j_study()
    elif arguments.study == "q006k":
        result = run_q006k_study()
    elif arguments.study == "q006l":
        result = run_q006l_study()
    elif arguments.study == "q006m":
        result = run_q006m_study()
    elif arguments.study == "q006o":
        result = run_q006o_study()
    elif arguments.study == "q006p":
        result = run_q006p_study()
    elif arguments.study == "q006q":
        result = run_q006q_study()
    elif arguments.study == "q007a":
        result = run_q007a_study()
    elif arguments.study == "q007b":
        result = run_q007b_study()
    elif arguments.study == "q007b1":
        result = run_q007b1_study()
    elif arguments.study == "q007c":
        result = run_q007c_study()
    elif arguments.study == "q007c1":
        result = run_q007c1_study()
    else:
        result = run_q007c2_study()
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
