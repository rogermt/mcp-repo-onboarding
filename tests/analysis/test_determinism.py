from __future__ import annotations

from pathlib import Path

import pytest

from mcp_repo_onboarding.schema import RepoAnalysis


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _analyze(repo_root: Path) -> RepoAnalysis:
    # Uses the project contract: REPO_ROOT overrides cwd
    from mcp_repo_onboarding.analysis import analyze_repo

    return analyze_repo(repo_path=".")


def test_analyze_repo_is_deterministic_across_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Minimal but representative repo layout
    _write(repo / "README.md", "# X\n")
    _write(repo / "pyproject.toml", "[project]\nname='x'\nversion='0.0.0'\n")
    _write(repo / "requirements.txt", "requests\n")
    _write(repo / "requirements-dev.txt", "pytest\n")

    _write(repo / "docs" / "b.md", "B\n")
    _write(repo / "docs" / "a.md", "A\n")

    _write(repo / ".github" / "workflows" / "b.yml", "name: b\n")
    _write(repo / ".github" / "workflows" / "a.yml", "name: a\n")

    monkeypatch.setenv("REPO_ROOT", str(repo))
    monkeypatch.chdir(repo)

    out1 = _analyze(repo)
    out2 = _analyze(repo)

    d1 = out1.model_dump()
    d2 = out2.model_dump()

    assert d1 == d2


def test_tie_break_ordering_is_path_ascending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _write(repo / "README.md", "# X\n")
    _write(repo / "pyproject.toml", "[project]\nname='x'\nversion='0.0.0'\n")

    # Same-score docs (both under docs/, same bucket) => order by path asc
    _write(repo / "docs" / "b.md", "B\n")
    _write(repo / "docs" / "a.md", "A\n")

    # Same-score configs (both in test/lint tooling bucket) => order by path asc
    _write(repo / "tox.ini", "[tox]\n")
    _write(repo / "pytest.ini", "[pytest]\n")

    # Dependencies: requirements.txt pinned first; rest deterministic
    _write(repo / "requirements-dev.txt", "pytest\n")
    _write(repo / "requirements.txt", "requests\n")

    monkeypatch.setenv("REPO_ROOT", str(repo))
    monkeypatch.chdir(repo)  # critical: prevents accidentally analyzing the real repo

    from mcp_repo_onboarding.analysis import analyze_repo

    out = analyze_repo(repo_path=".")
    d = out.model_dump()

    # Access fields from the dict directly
    # Docs
    docs_list = d.get("docs", [])
    assert isinstance(docs_list, list)
    doc_paths = [x["path"] if isinstance(x, dict) else x.path for x in docs_list]
    assert doc_paths.index("docs/a.md") < doc_paths.index("docs/b.md")

    # Configs
    cfg_list = d.get("configurationFiles", [])
    assert isinstance(cfg_list, list)
    cfg_paths = [x["path"] if isinstance(x, dict) else x.path for x in cfg_list]
    assert cfg_paths.index("pytest.ini") < cfg_paths.index("tox.ini")

    # Python Deps
    py = d.get("python")
    if py and isinstance(py, dict):
        dep_entries = py.get("dependencyFiles", [])
        if isinstance(dep_entries, list):
            dep_paths = [x["path"] if isinstance(x, dict) else x.path for x in dep_entries]
            assert dep_paths[0] == "requirements.txt"
