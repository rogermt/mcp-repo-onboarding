"""Tests for primaryTooling note in analyzer notes section (Issue #127)."""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import (
    build_context,
    compile_blueprint,
)


def _base_commands() -> dict[str, Any]:
    return {"devCommands": [], "testCommands": [], "buildCommands": []}


def test_primary_tooling_note_order_node_without_python() -> None:
    """
    Test that primaryTooling note appears in correct order:
    1. Python-only scope note (if python not detected)
    2. Primary tooling note
    3. Other analyzer notes
    """
    analyze: dict[str, Any] = {
        "repoPath": "/test/repo",
        "primaryTooling": "Node.js",
        "python": None,
        "scripts": {
            "dev": [],
            "start": [],
            "test": [],
            "lint": [],
            "format": [],
            "install": [],
            "other": [],
        },
        "notes": ["docs list truncated to 10 entries (total=99)"],
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
        "testSetup": {"commands": []},
        "otherTooling": [
            {
                "name": "Node.js",
                "evidenceFiles": ["package.json", "yarn.lock"],
                "confidence": "detected",
            }
        ],
    }

    md = compile_blueprint(build_context(analyze, _base_commands()))["render"]["markdown"]
    lines = md.splitlines()

    # Locate Analyzer notes section
    start = lines.index("## Analyzer notes")
    bullets = []
    for ln in lines[start + 1 :]:
        if ln.startswith("## "):
            break
        if ln.startswith("* "):
            bullets.append(ln)

    assert (
        bullets[0]
        == "* Python tooling not detected; this release generates Python-focused onboarding only."
    )
    assert bullets[1] == "* Primary tooling: Node.js (package.json, yarn.lock present)."
    assert bullets[2] == "* docs list truncated to 10 entries (total=99)"
