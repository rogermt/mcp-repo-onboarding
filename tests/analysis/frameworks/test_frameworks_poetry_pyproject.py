"""Tests for Flask detection via Poetry dependencies (Poetry detector registry)."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _create_temp_repo() -> Path:
    """Create a temporary repository directory."""
    return Path(tempfile.mkdtemp(prefix="mcp-poetry-test-"))


def test_detects_flask_from_poetry_dependencies(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("fw-poetry-flask")
    _write(
        repo / "pyproject.toml",
        """
[tool.poetry]
name = "connexion"
version = "0.0.0"

[tool.poetry.dependencies]
python = "^3.9"
flask = { version = ">= 2.2", extras = ["async"], optional = true }

[build-system]
requires = ["poetry-core>=1.2.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Flask" in fw
    assert fw["Flask"].evidencePath == "pyproject.toml"
    assert fw["Flask"].keySymbols == ["tool.poetry.dependencies.flask"]
    # optional=true in Poetry deps should be reflected in the detection reason (neutral, non-prescriptive)
    expected = (
        "Flask support detected via pyproject.toml (Poetry) dependency key 'flask' (optional)."
    )
    assert fw["Flask"].detectionReason == expected

    # Guard against malformed punctuation pattern (regression for #132)
    assert "'. (optional" not in fw["Flask"].detectionReason


def test_detects_flask_from_poetry_non_optional() -> None:
    """Test non-optional Flask dependency (ensures reason has no trailing period in field)."""
    repo = _create_temp_repo()
    _write(
        repo / "pyproject.toml",
        """
[tool.poetry]
name = "connexion"
version = "0.0.0"

[tool.poetry.dependencies]
python = "^3.9"
flask = ">= 2.2"

[build-system]
requires = ["poetry-core>=1.2.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Flask" in fw
    assert fw["Flask"].evidencePath == "pyproject.toml"
    assert fw["Flask"].keySymbols == ["tool.poetry.dependencies.flask"]
    # Non-optional reason should have NO trailing period in the stored field
    # (blueprint sanitizer will add exactly one period during rendering)
    expected = "Flask support detected via pyproject.toml (Poetry) dependency key 'flask'"
    assert fw["Flask"].detectionReason == expected


def test_detects_django_from_poetry_dependencies() -> None:
    """Test Django detection from Poetry dependencies."""
    repo = _create_temp_repo()
    _write(
        repo / "pyproject.toml",
        """
[tool.poetry]
name = "test-app"
version = "0.0.0"

[tool.poetry.dependencies]
python = "^3.9"
django = { version = ">= 4.0", optional = true }

[build-system]
requires = ["poetry-core>=1.2.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Django" in fw
    expected = (
        "Django support detected via pyproject.toml (Poetry) dependency key 'django' (optional)."
    )
    assert fw["Django"].detectionReason == expected
    # Guard against malformed punctuation
    assert "'. (optional" not in fw["Django"].detectionReason


def test_detects_fastapi_from_poetry_dependencies() -> None:
    """Test FastAPI detection from Poetry dependencies."""
    repo = _create_temp_repo()
    _write(
        repo / "pyproject.toml",
        """
[tool.poetry]
name = "test-app"
version = "0.0.0"

[tool.poetry.dependencies]
python = "^3.9"
fastapi = ">= 0.95"

[build-system]
requires = ["poetry-core>=1.2.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "FastAPI" in fw
    expected = "FastAPI support detected via pyproject.toml (Poetry) dependency key 'fastapi'"
    assert fw["FastAPI"].detectionReason == expected
