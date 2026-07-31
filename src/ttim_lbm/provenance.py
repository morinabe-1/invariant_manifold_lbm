"""Reproducibility metadata shared by research studies."""

from __future__ import annotations

import platform
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from ._version import __version__


def package_source_fingerprint() -> str:
    """Hash every Python source file in the installed research package."""

    digest = sha256()
    package_root = Path(__file__).resolve().parent
    for source in sorted(package_root.glob("*.py")):
        digest.update(source.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def source_metadata() -> dict[str, str]:
    return {
        "package_version": __version__,
        "package_source_sha256": package_source_fingerprint(),
    }


def runtime_metadata() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
    }
