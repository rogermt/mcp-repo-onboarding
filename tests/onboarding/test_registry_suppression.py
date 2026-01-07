"""
Tests for registry suppression logic (Issue #146).

Verifies that _other_tooling_lines() suppresses primary tooling from the
"## Other tooling detected" section and ensures deterministic sorting.
"""

from __future__ import annotations

from mcp_repo_onboarding.analysis.onboarding_blueprint_engine.context import Context
from mcp_repo_onboarding.analysis.onboarding_blueprint_engine.registry import (
    _other_tooling_lines,
)


def test_suppresses_primary_tooling() -> None:
    """Primary tooling should not appear in ## Other tooling detected section."""
    analyze = {
        "primaryTooling": "Node.js",
        "otherTooling": [
            {"name": "Node.js", "evidenceFiles": ["package.json"]},
            {"name": "Go", "evidenceFiles": ["go.mod"]},
        ],
    }
    ctx = Context(analyze=analyze, commands={})
    lines = _other_tooling_lines(ctx)

    # Should contain Go
    assert any("Go" in line for line in lines), f"Go not found in {lines}"
    # Should NOT contain Node.js (suppressed as primary)
    assert not any("Node.js" in line for line in lines), f"Node.js should be suppressed in {lines}"


def test_no_suppression_if_primary_differs() -> None:
    """If primary tooling is different, other tooling should appear normally."""
    analyze = {
        "primaryTooling": "Python",
        "otherTooling": [{"name": "Node.js", "evidenceFiles": ["package.json"]}],
    }
    ctx = Context(analyze=analyze, commands={})
    lines = _other_tooling_lines(ctx)

    assert any("Node.js" in line for line in lines), f"Node.js not found in {lines}"


def test_deterministic_sorting_by_name() -> None:
    """Tooling items should be sorted alphabetically by name."""
    analyze = {
        "primaryTooling": "Python",
        "otherTooling": [
            {"name": "Node.js", "evidenceFiles": ["package.json"]},
            {"name": "Docker", "evidenceFiles": ["Dockerfile"]},
            {"name": "Go", "evidenceFiles": ["go.mod"]},
        ],
    }
    ctx = Context(analyze=analyze, commands={})
    lines = _other_tooling_lines(ctx)

    # Extract tooling names in order they appear
    names = []
    for line in lines:
        # Lines are like "* Docker (Dockerfile)"
        stripped = line.strip("* ").split(" (")[0]
        names.append(stripped)

    # Should be in alphabetical order: Docker, Go, Node.js
    assert names == ["Docker", "Go", "Node.js"], f"Expected sorted order, got {names}"


def test_evidence_file_sorting() -> None:
    """Evidence files within a tooling entry should be sorted lexicographically."""
    analyze = {
        "primaryTooling": "Python",
        "otherTooling": [
            {
                "name": "Go",
                "evidenceFiles": ["go.sum", "go.mod", "Dockerfile"],
            }
        ],
    }
    ctx = Context(analyze=analyze, commands={})
    lines = _other_tooling_lines(ctx)

    assert len(lines) == 1
    line = lines[0]

    # Evidence should be sorted: Dockerfile, go.mod, go.sum
    assert "Dockerfile" in line
    assert "go.mod" in line
    assert "go.sum" in line

    # Check order in string
    dockerfile_idx = line.index("Dockerfile")
    go_mod_idx = line.index("go.mod")
    go_sum_idx = line.index("go.sum")

    assert dockerfile_idx < go_mod_idx < go_sum_idx, (
        f"Evidence files should be sorted, but got order: "
        f"Dockerfile@{dockerfile_idx}, go.mod@{go_mod_idx}, go.sum@{go_sum_idx}"
    )


def test_empty_other_tooling() -> None:
    """Empty otherTooling should return empty lines list."""
    analyze = {
        "primaryTooling": "Python",
        "otherTooling": [],
    }
    ctx = Context(analyze=analyze, commands={})
    lines = _other_tooling_lines(ctx)

    assert lines == []


def test_primary_tooling_case_sensitive_match() -> None:
    """Suppression should match primary tooling exactly (case-sensitive)."""
    analyze = {
        "primaryTooling": "node.js",  # lowercase
        "otherTooling": [
            {"name": "Node.js", "evidenceFiles": ["package.json"]},  # mixed case
        ],
    }
    ctx = Context(analyze=analyze, commands={})
    lines = _other_tooling_lines(ctx)

    # Names are different cases, so Node.js should NOT be suppressed
    assert any("Node.js" in line for line in lines), (
        "Node.js should appear (primary is 'node.js' which is different case)"
    )
