from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_detects_django_and_wagtail_from_classifiers(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("fw-pyproject-classifiers")

    _write(
        repo / "pyproject.toml",
        """
[project]
name = "x"
version = "0.0.0"
classifiers = [
  "Framework :: Django",
  "Framework :: Wagtail",
]
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Django" in fw
    assert fw["Django"].evidencePath == "pyproject.toml"
    assert fw["Django"].keySymbols == ["Framework :: Django"]

    assert "Wagtail" in fw
    assert fw["Wagtail"].evidencePath == "pyproject.toml"
    assert fw["Wagtail"].keySymbols == ["Framework :: Wagtail"]
