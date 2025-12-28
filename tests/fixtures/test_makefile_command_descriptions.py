from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_make_install_has_description(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("make-install-desc")
    _write(repo / "pyproject.toml", '[project]\nname="x"\nversion="0.0.0"\n')

    _write(repo / "Makefile", "install:\n\t@echo install\n")
    a = analyze_repo(repo_path=str(repo))

    install_cmds = [c for c in a.scripts.install if c.command == "make install"]
    assert install_cmds, "Expected make install command to be detected"
    assert install_cmds[0].description == "Install dependencies via Makefile target."


def test_make_lint_has_description(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("make-lint-desc")
    _write(repo / "pyproject.toml", '[project]\nname="x"\nversion="0.0.0"\n')

    _write(repo / "Makefile", "lint:\n\t@echo lint\n")
    a = analyze_repo(repo_path=str(repo))

    lint_cmds = [c for c in a.scripts.lint if c.command == "make lint"]
    assert lint_cmds, "Expected make lint command to be detected"
    assert lint_cmds[0].description == "Run linting via Makefile target."


def test_make_format_has_description(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("make-format-desc")
    _write(repo / "pyproject.toml", '[project]\nname="x"\nversion="0.0.0"\n')

    _write(repo / "Makefile", "format:\n\t@echo format\n")
    a = analyze_repo(repo_path=str(repo))

    fmt_cmds = [c for c in a.scripts.format if c.command == "make format"]
    assert fmt_cmds, "Expected make format command to be detected"
    assert fmt_cmds[0].description == "Run formatting via Makefile target."
