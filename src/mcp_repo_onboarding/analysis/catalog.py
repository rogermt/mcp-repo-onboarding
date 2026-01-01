"""
Canonical definitions for file categorization.

This module breaks a circular dependency between core and other modules
by providing a neutral location for classification functions.
"""

from __future__ import annotations

from pathlib import Path

from ..config import classify_filename


def is_dependency_file(path: str) -> bool:
    """
    Check if a file is canonically a dependency manifest.

    Behavior preserved:
    - exact-name dependency classification via config.classify_filename
    - requirements*.txt / requirements*.in treated as dependency manifests
    """
    path = path.replace("\\", "/").lstrip("/")
    name = Path(path).name
    return classify_filename(name) == "dependency"
