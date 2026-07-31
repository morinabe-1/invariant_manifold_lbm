"""Command-line entry point for the reproducible D2Q9 baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .experiments import run_d2q9_baseline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--omega", type=float, default=1.2)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_d2q9_baseline(omega=arguments.omega)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
