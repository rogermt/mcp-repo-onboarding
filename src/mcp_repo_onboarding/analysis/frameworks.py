from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ..schema import FrameworkInfo

_MAX_BYTES = 256_000  # size cap for deterministic/cheap reads


def detect_frameworks_from_pyproject(
    repo_root: Path, rel_path: str = "pyproject.toml"
) -> list[FrameworkInfo]:
    """
    Detect frameworks using pyproject.toml metadata.

    Deterministic:
    - size-capped read
    - parse via tomllib
    - prefers explicit framework classifiers when available
    - otherwise uses dependency presence as a conservative hint (e.g. Poetry deps)
    """
    root = repo_root.resolve()
    p = (root / rel_path).resolve()
    try:
        p.relative_to(root)
    except Exception:
        return []

    try:
        if not p.is_file():
            return []
        if p.stat().st_size > _MAX_BYTES:
            return []
        raw = p.read_text(encoding="utf-8", errors="ignore")
        data: dict[str, Any] = tomllib.loads(raw)
    except OSError:
        return []
    except Exception:
        # tomllib parse errors should not crash analysis
        return []

    # --- Collect classifiers from both PEP 621 and Poetry ---
    cls: list[str] = []

    project = data.get("project") or {}
    project_classifiers = project.get("classifiers") or []
    if isinstance(project_classifiers, list):
        cls.extend([c for c in project_classifiers if isinstance(c, str)])

    tool = data.get("tool") or {}
    poetry = tool.get("poetry") or {}
    poetry_classifiers = poetry.get("classifiers") or []
    if isinstance(poetry_classifiers, list):
        cls.extend([c for c in poetry_classifiers if isinstance(c, str)])

    found: dict[str, FrameworkInfo] = {}

    def _has(prefix: str) -> bool:
        return any(c.strip() == prefix or c.strip().startswith(prefix + " ::") for c in cls)

    # Minimal, conservative detections from explicit classifiers
    if _has("Framework :: Django"):
        found["Django"] = FrameworkInfo(
            name="Django",
            detectionReason="Detected via pyproject.toml classifiers",
            keySymbols=["Framework :: Django"],
            evidencePath=rel_path,
        )

    if _has("Framework :: Wagtail"):
        found["Wagtail"] = FrameworkInfo(
            name="Wagtail",
            detectionReason="Detected via pyproject.toml classifiers",
            keySymbols=["Framework :: Wagtail"],
            evidencePath=rel_path,
        )

    def _poetry_dep_is_optional(dep_val: Any) -> bool:
        """
        Poetry dependency values can be:
        - string version (e.g. "^3.9")
        - dict/table (e.g. {version=">=2", optional=true, extras=[...]} )
        We only treat it as optional when explicitly declared optional=true.
        """
        return isinstance(dep_val, dict) and bool(dep_val.get("optional") is True)

    # --- If classifiers did not cover everything, fall back to dependency presence ---
    # Poetry deps: [tool.poetry.dependencies] is a table/map. Connexion declares flask as optional extra there.
    poetry_deps = poetry.get("dependencies") or {}
    if isinstance(poetry_deps, dict):
        dep_keys = {str(k).lower() for k in poetry_deps}

        # Flask support (often optional, but still a valid "framework present" hint)
        if "flask" in dep_keys and "Flask" not in found:
            flask_optional = _poetry_dep_is_optional(poetry_deps.get("flask"))
            found["Flask"] = FrameworkInfo(
                name="Flask",
                detectionReason=(
                    "Flask support detected via pyproject.toml (Poetry) dependency key 'flask' (optional)."
                    if flask_optional
                    else "Detected via pyproject.toml (Poetry) dependency key 'flask'"
                ),
                keySymbols=["tool.poetry.dependencies.flask"],
                evidencePath=rel_path,
            )

        # Django dependency (for Poetry-format projects)
        if "django" in dep_keys and "Django" not in found:
            django_optional = _poetry_dep_is_optional(poetry_deps.get("django"))
            found["Django"] = FrameworkInfo(
                name="Django",
                detectionReason=(
                    "Django support detected via pyproject.toml (Poetry) dependency key 'django' (optional)."
                    if django_optional
                    else "Detected via pyproject.toml (Poetry) dependency key 'django'"
                ),
                keySymbols=["tool.poetry.dependencies.django"],
                evidencePath=rel_path,
            )

        # FastAPI dependency (Poetry-format projects)
        if "fastapi" in dep_keys and "FastAPI" not in found:
            fastapi_optional = _poetry_dep_is_optional(poetry_deps.get("fastapi"))
            found["FastAPI"] = FrameworkInfo(
                name="FastAPI",
                detectionReason=(
                    "FastAPI support detected via pyproject.toml (Poetry) dependency key 'fastapi' (optional)."
                    if fastapi_optional
                    else "Detected via pyproject.toml (Poetry) dependency key 'fastapi'"
                ),
                keySymbols=["tool.poetry.dependencies.fastapi"],
                evidencePath=rel_path,
            )

    # Deterministic output order
    return [found[k] for k in sorted(found.keys())]
