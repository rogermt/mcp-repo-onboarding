from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import build_context, compile_blueprint


def _mk_analyze(notebooks: list[str]) -> dict[str, Any]:
    # Minimal shape required by blueprint builder
    return {
        "repoPath": "/test/repo",
        "python": {
            "pythonVersionHints": [],
            "envSetupInstructions": [],
            "installInstructions": [],
            "dependencyFiles": [],
        },
        "scripts": {
            "dev": [],
            "start": [],
            "test": [],
            "lint": [],
            "format": [],
            "install": [],
            "other": [],
        },
        "notes": [],
        "notebooks": notebooks,
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
        "testSetup": {"commands": []},
    }


def _mk_commands() -> dict[str, Any]:
    return {"devCommands": [], "testCommands": [], "buildCommands": []}


def test_notebook_dirs_truncated_when_over_cap() -> None:
    # 25 dirs should truncate to 20
    nb = [f"demo/nb{i:02d}/" for i in range(25)]
    analyze = _mk_analyze(nb)
    commands = _mk_commands()

    bp = compile_blueprint(build_context(analyze, commands))
    md = bp["render"]["markdown"]

    assert "## Analyzer notes" in md
    assert "Notebook-centric repo detected; core logic may reside in Jupyter notebooks." in md

    # Deterministic truncation note
    assert "* notebooks list truncated to 20 entries (total=25)" in md

    # Included up to nb19, excluded nb20+
    assert "demo/nb19/" in md
    assert "demo/nb20/" not in md

    # Notebook-centric note should not duplicate
    assert (
        md.count("Notebook-centric repo detected; core logic may reside in Jupyter notebooks.") == 1
    )


def test_notebook_dirs_not_truncated_when_under_cap() -> None:
    nb = [f"demo/nb{i:02d}/" for i in range(3)]
    analyze = _mk_analyze(nb)
    commands = _mk_commands()

    bp = compile_blueprint(build_context(analyze, commands))
    md = bp["render"]["markdown"]

    assert "## Analyzer notes" in md
    assert "notebooks list truncated to" not in md
    assert "demo/nb00/" in md
    assert "demo/nb01/" in md
    assert "demo/nb02/" in md
