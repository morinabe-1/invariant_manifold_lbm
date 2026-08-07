"""Command-line entry point for reproducible D2Q9 research studies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .experiments import run_d2q9_baseline
from .studies import (
    run_q004b_and_manufactured_study,
    run_q005_study,
    run_q006r_study,
    run_q006s_study,
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
        choices=("baseline", "q004b", "q005", "q006s", "q006r"),
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
    else:
        result = run_q006r_study()
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
