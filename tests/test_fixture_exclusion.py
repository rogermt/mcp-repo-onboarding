from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str = "x") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _assert_no_fixture_paths(items: list[Any] | None, label: str) -> None:
    for it in items or []:
        rel = it.path.replace("\\", "/")
        if "tests/fixtures/" in rel or "test/fixtures/" in rel:
            raise AssertionError(f"Found fixture path in {label}: {it.path}")


def test_fixtures_are_invisible_everywhere(temp_repo: Callable[[str], Path]) -> None:
    """
    Regression test for Issue #64.
    Ensures that content within 'tests/fixtures/' or 'test/fixtures/' is excluded
    from analysis results (docs, configurationFiles, dependencyFiles), even if
    files inside match known patterns (e.g. pyproject.toml, requirements.txt).
    """
    repo = temp_repo("fixture-exclusion-test")

    # Legit files at root/docs that SHOULD be detected
    _write(repo / "README.md", "# readme\n")
    _write(repo / "docs" / "index.md", "# docs\n")
    _write(repo / ".pre-commit-config.yaml", "repos: []\n")
    _write(repo / ".github" / "workflows" / "ci.yml", "name: ci\non: [push]\njobs: {}\n")
    _write(
        repo / "pyproject.toml",
        '[project]\nname="fixture-exclusion-test"\nversion="0.0.0"\n',
    )

    # Noise that MUST be invisible (would pollute docs/config/deps if safety ignore is broken)
    _write(
        repo / "tests" / "fixtures" / "noise" / "pyproject.toml",
        '[project]\nname="noise"\nversion="0.0.0"\n',
    )
    _write(repo / "tests" / "fixtures" / "noise" / "requirements.txt", "requests\n")
    _write(repo / "tests" / "fixtures" / "noise" / "README.md", "# fixture readme\n")
    _write(repo / "tests" / "fixtures" / "noise" / "Makefile", "test:\n\t@echo test\n")
    _write(repo / "test" / "fixtures" / "noise" / "setup.py", "from setuptools import setup\n")

    analysis = analyze_repo(repo_path=str(repo))

    # Must not contain fixtures anywhere
    _assert_no_fixture_paths(analysis.docs, "docs")
    _assert_no_fixture_paths(analysis.configurationFiles, "configurationFiles")
    if analysis.python:
        _assert_no_fixture_paths(analysis.python.dependencyFiles, "python.dependencyFiles")

    # Sanity: ensure legit files are still detected (otherwise the test can pass trivially)
    doc_paths = {d.path.replace("\\", "/") for d in (analysis.docs or [])}
    assert "README.md" in doc_paths
    assert "docs/index.md" in doc_paths

    dep_paths = set()
    if analysis.python:
        dep_paths = {d.path.replace("\\", "/") for d in (analysis.python.dependencyFiles or [])}
    assert (
        "pyproject.toml" in dep_paths
    ), f"Expected root pyproject.toml in deps, got: {sorted(dep_paths)}"
