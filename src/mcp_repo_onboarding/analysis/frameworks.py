"""
Framework detection (extensible registry-based).

Supports:
- pyproject.toml classifiers (Django, Wagtail)
- pyproject.toml Poetry dependencies (Flask, Django, FastAPI)
- requirements*.txt explicit names (Streamlit, Gradio, FastAPI, Flask, Django)

Deterministic and static-only (no subprocess, no commands).
"""

from __future__ import annotations

import re
import tomllib
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..schema import FrameworkInfo, PythonEnvFile

_MAX_BYTES = 256_000


# -----------------------------------------------------------------------------
# Base Detector Interface
# -----------------------------------------------------------------------------


class FrameworkDetector(ABC):
    """Abstract base for framework detectors."""

    @abstractmethod
    def detect(
        self,
        repo_root: Path,
        dep_files: list[PythonEnvFile] | None,
        pyproject_data: dict[str, Any] | None,
    ) -> list[FrameworkInfo]:
        """
        Detect frameworks from available data.

        Args:
            repo_root: Repository root.
            dep_files: List of dependency file objects.
            pyproject_data: Parsed pyproject.toml data (if exists).

        Returns:
            List of FrameworkInfo objects.
        """


# -----------------------------------------------------------------------------
# Pyproject Classifier Detector
# -----------------------------------------------------------------------------


@dataclass
class _ClassifierMatch:
    """Internal representation of a classifier match."""

    name: str
    classifiers: tuple[str, ...]
    evidence: str


class PyprojectClassifierDetector(FrameworkDetector):
    """Detects frameworks from pyproject.toml classifiers (PEP 621, Poetry)."""

    # Registry of known classifiers -> framework mapping
    _CLASSIFIER_REGISTRY: list[_ClassifierMatch] = [
        _ClassifierMatch(
            name="Django",
            classifiers=("Framework :: Django",),
            evidence="Detected via pyproject.toml classifiers",
        ),
        _ClassifierMatch(
            name="Wagtail",
            classifiers=("Framework :: Wagtail",),
            evidence="Detected via pyproject.toml classifiers",
        ),
    ]

    def detect(
        self,
        repo_root: Path,
        dep_files: list[PythonEnvFile] | None,
        pyproject_data: dict[str, Any] | None,
    ) -> list[FrameworkInfo]:
        if not pyproject_data:
            return []

        root = repo_root.resolve()
        p = (root / "pyproject.toml").resolve()
        try:
            p.relative_to(root)
        except Exception:
            return []

        # Extract classifiers
        cls_list: list[str] = []

        project = pyproject_data.get("project") or {}
        project_classifiers = project.get("classifiers") or []
        if isinstance(project_classifiers, list):
            cls_list.extend([c for c in project_classifiers if isinstance(c, str)])

        tool = pyproject_data.get("tool") or {}
        poetry = tool.get("poetry") or {}
        poetry_classifiers = poetry.get("classifiers") or []
        if isinstance(poetry_classifiers, list):
            cls_list.extend([c for c in poetry_classifiers if isinstance(c, str)])

        if not cls_list:
            return []

        found: dict[str, FrameworkInfo] = {}

        for match in self._CLASSIFIER_REGISTRY:
            if self._has_prefix(match.classifiers, cls_list):
                found[match.name] = FrameworkInfo(
                    name=match.name,
                    detectionReason=match.evidence,
                    keySymbols=list(match.classifiers),
                    evidencePath="pyproject.toml",
                )

        return [found[k] for k in sorted(found.keys())]

    @staticmethod
    def _has_prefix(prefixes: Iterable[str], class_list: Iterable[str]) -> bool:
        return any(
            c.strip() == p or c.strip().startswith(p + " :: ") for c in class_list for p in prefixes
        )


# -----------------------------------------------------------------------------
# Poetry Dependency Detector (Refactored for Phase 9)
# -----------------------------------------------------------------------------


# Registry for Poetry dependency reason strings.
# Format: (framework_name, dependency_key, reason_template, supports_optional)
_POETRY_DEP_REGISTRY: list[tuple[str, str, str, bool]] = [
    (
        "Flask",
        "flask",
        "Detected via pyproject.toml (Poetry) dependency key 'flask'.",
        True,  # supports optional annotation
    ),
    (
        "Django",
        "django",
        "Detected via pyproject.toml (Poetry) dependency key 'django'.",
        True,
    ),
    (
        "FastAPI",
        "fastapi",
        "Detected via pyproject.toml (Poetry) dependency key 'fastapi'.",
        True,
    ),
]


class PoetryDependencyDetector(FrameworkDetector):
    """
    Detects frameworks from [tool.poetry.dependencies] in pyproject.toml.

    Uses a registry mapping to determine framework name, key symbol, and reason string,
    avoiding if/else branching for reason construction.
    """

    def detect(
        self,
        repo_root: Path,
        dep_files: list[PythonEnvFile] | None,
        pyproject_data: dict[str, Any] | None,
    ) -> list[FrameworkInfo]:
        if not pyproject_data:
            return []

        # We can use pyproject_data directly
        data = pyproject_data

        tool = data.get("tool") or {}
        poetry = tool.get("poetry") or {}

        if not isinstance(poetry, dict):
            return []

        poetry_deps = poetry.get("dependencies")
        if not isinstance(poetry_deps, dict):
            return []

        found: dict[str, FrameworkInfo] = {}

        for fw_name, dep_key, template, supports_optional in _POETRY_DEP_REGISTRY:
            if dep_key in poetry_deps:
                is_optional = isinstance(poetry_deps[dep_key], dict) and bool(
                    poetry_deps[dep_key].get("optional")
                )

                reason = template
                if supports_optional and is_optional:
                    reason += " (optional)"

                found[fw_name] = FrameworkInfo(
                    name=fw_name,
                    detectionReason=reason,
                    keySymbols=[f"tool.poetry.dependencies.{dep_key}"],
                    evidencePath="pyproject.toml",
                )

        return [found[k] for k in sorted(found.keys())]


# -----------------------------------------------------------------------------
# Requirements File Detector
# -----------------------------------------------------------------------------


def _norm_pkg_name(name: str) -> str:
    return name.strip().lower().replace("_", "-").replace(".", "-")


_REQ_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*")


def _extract_req_names(text: str) -> set[str]:
    """
    Parse requirement names conservatively:
    - ignore comments, empty lines
    - ignore -r/-c includes and editable/path/git installs
    - extract leading distribution name token
    """
    out: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        # Drop inline comments
        if " #" in line:
            line = line.split(" #", 1)[0].strip()

        low = line.lower()

        # Ignore includes / options / editable / urls
        if low.startswith(("-r ", "--requirement", "-c ", "--constraint", "--", "-e ")):
            continue
        if "://" in low or low.startswith(("git+", "svn+", "hg+", "bzr+")):
            continue
        if low.startswith((".", "/")):
            continue

        # Remove environment marker portion
        if ";" in line:
            line = line.split(";", 1)[0].strip()

        # Extract leading name token
        m = _REQ_NAME_RE.match(line)
        if not m:
            continue
        name = m.group(0)

        # Strip extras if they appear as name[extra]
        if "[" in name:
            name = name.split("[", 1)[0].strip()

        if name:
            out.add(_norm_pkg_name(name))
    return out


class RequirementsDetector(FrameworkDetector):
    """
    Detects frameworks from requirements*.txt files (Phase 9).

    Explicit dependency name matching only (e.g., "streamlit", "gradio").
    No subprocess calls. No commands inferred.
    """

    # (framework_name, key_symbol_suffix)
    _REQ_PKG_REGISTRY: list[tuple[str, str]] = [
        ("Streamlit", "streamlit"),
        ("Gradio", "gradio"),
        ("FastAPI", "fastapi"),
        ("Flask", "flask"),
        ("Django", "django"),
    ]

    def detect(
        self,
        repo_root: Path,
        dep_files: list[PythonEnvFile] | None,
        pyproject_data: dict[str, Any] | None,
    ) -> list[FrameworkInfo]:
        if not dep_files:
            return []

        root = repo_root.resolve()
        req_paths = [
            d.path
            for d in dep_files
            if isinstance(d.path, str)
            and Path(d.path).name.lower().startswith("requirements")
            and Path(d.path).suffix.lower() in (".txt", ".in")
        ]

        found: dict[str, FrameworkInfo] = {}

        for rel in req_paths:
            p = (root / rel).resolve()
            try:
                p.relative_to(root)
            except Exception:
                continue

            try:
                if not p.is_file():
                    continue
                if p.stat().st_size > _MAX_BYTES:
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            names = _extract_req_names(text)
            for fw_name, key_suffix in self._REQ_PKG_REGISTRY:
                if fw_name.lower() in names and fw_name not in found:
                    found[fw_name] = FrameworkInfo(
                        name=fw_name,
                        detectionReason=f"Detected via {Path(rel).name} dependency '{fw_name.lower()}'.",
                        keySymbols=[f"{Path(rel).name}:{key_suffix}"],
                        evidencePath=rel,
                    )

        return [found[k] for k in sorted(found.keys())]


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------


# Registry of detectors (extensible: add new detectors here to support new sources/frameworks)
DETECTORS: list[FrameworkDetector] = [
    PyprojectClassifierDetector(),
    PoetryDependencyDetector(),
    RequirementsDetector(),
]


def detect_frameworks(
    repo_root: Path,
    dep_files: list[PythonEnvFile] | None = None,
) -> list[FrameworkInfo]:
    """
    Detect frameworks using the extensible registry of detectors.

    Iterates over detectors and aggregates results.
    """
    pyproject_data = None

    p = (repo_root / "pyproject.toml").resolve()
    try:
        p.relative_to(repo_root)
        if p.is_file() and p.stat().st_size <= _MAX_BYTES:
            pyproject_data = tomllib.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        pass

    all_found: dict[str, FrameworkInfo] = {}

    for detector in DETECTORS:
        try:
            results = detector.detect(repo_root, dep_files, pyproject_data)
            for fw in results:
                # De-duplicate by name (last one wins for simple merging)
                all_found[fw.name] = fw
        except Exception:
            # Detector failures should not crash analysis
            continue

    return [all_found[k] for k in sorted(all_found.keys())]
