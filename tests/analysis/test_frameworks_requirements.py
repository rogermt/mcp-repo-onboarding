"""Tests for framework detection via requirements.txt files."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_detects_frameworks_from_requirements_txt(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("fw-requirements-txt")
    _write(
        repo / "requirements.txt",
        """
django>=4.2
flask
fastapi
# something else
requests
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Django" in fw
    assert fw["Django"].evidencePath == "requirements.txt"
    assert "Flask" in fw
    assert fw["Flask"].evidencePath == "requirements.txt"
    assert "FastAPI" in fw
    assert fw["FastAPI"].evidencePath == "requirements.txt"


def test_detects_frameworks_from_multiple_requirements(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("fw-multi-requirements")
    _write(repo / "requirements.txt", "django\n")
    _write(repo / "requirements-dev.txt", "flask\n")

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Django" in fw
    assert "Flask" in fw
    assert fw["Django"].evidencePath == "requirements.txt"
    assert fw["Flask"].evidencePath == "requirements-dev.txt"
    assert fw["Django"].detectionReason == "Detected via requirements.txt dependency 'django'."
