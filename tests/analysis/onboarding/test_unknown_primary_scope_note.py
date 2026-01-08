"""Test Unknown primary tooling scope note messaging."""

from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import build_context, compile_blueprint


def test_unknown_primary_repo_scope_note_mentions_python_and_node() -> None:
    """Verify Unknown-primary repos show Python/Node.js scope note."""
    analyze: dict[str, Any] = {
        "repoPath": ".",
        "primaryTooling": "Unknown",
        "python": None,
        "scripts": {},
        "otherTooling": [{"name": "Go", "evidenceFiles": ["go.mod", "go.sum"]}],
        "notes": [],
        "docs": [],
        "configurationFiles": [],
        "frameworks": [],
        "notebooks": [],
        "testSetup": {},
    }

    md = compile_blueprint(build_context(analyze, {}))["render"]["markdown"]

    assert "## Analyzer notes" in md
    assert (
        "Python/Node.js tooling not detected; this release generates onboarding for Python and Node.js repos only."
        in md
    )
    # Verify Go still appears in Other tooling detected
    assert "## Other tooling detected" in md
    assert "Go (go.mod, go.sum)" in md
