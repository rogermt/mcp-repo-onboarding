from __future__ import annotations

from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_primary_tooling_node_first(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Node evidence (stronger than Python)
    (repo / "package.json").write_text('{"name":"x","version":"0.0.0"}', encoding="utf-8")
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    a = analyze_repo(str(repo))
    assert a.primaryTooling == "Node.js"


def test_primary_tooling_python_first(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Python evidence (stronger than Node)
    (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0.0.0'\n", encoding="utf-8")

    a = analyze_repo(str(repo))
    assert a.primaryTooling == "Python"


def test_primary_tooling_tie_breaks_to_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Tie: Python +10 (pyproject.toml) vs Node +10 (lockfile only)
    (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0.0.0'\n", encoding="utf-8")
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    a = analyze_repo(str(repo))
    assert a.primaryTooling == "Python"


def test_primary_tooling_unknown_when_no_evidence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    a = analyze_repo(str(repo))
    assert a.primaryTooling == "Unknown"


def test_primary_tooling_deterministic_across_runs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "package.json").write_text('{"name":"x"}', encoding="utf-8")
    (repo / "pnpm-lock.yaml").write_text("lockfileVersion: 6", encoding="utf-8")
    (repo / "requirements.txt").write_text("requests\n", encoding="utf-8")

    a1 = analyze_repo(str(repo))
    a2 = analyze_repo(str(repo))

    assert a1.primaryTooling == a2.primaryTooling
