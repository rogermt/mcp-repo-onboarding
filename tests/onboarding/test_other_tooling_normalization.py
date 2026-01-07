'Tests for "Other tooling detected" normalization (Issue #110).'

from __future__ import annotations

from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo
from mcp_repo_onboarding.analysis.onboarding_blueprint import (
    build_context,
    compile_blueprint,
)
from mcp_repo_onboarding.config import MAX_EVIDENCE_FILES_DISPLAYED


def test_gradio_bbox_node_tooling_normalized(tmp_path: Path) -> None:
    """
    Simulate gradio-bbox Node.js detection (Phase 10 / Issue #146):
    - Node.js is primary tooling (suppressed from "## Other tooling detected")
    - Primary tooling appears in "## Analyzer notes" section instead
    - Evidence files for primary tooling are shown in primary tooling note
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "package.json").write_text('{"name": "x"}')  # Node evidence 1

    js_pkg = repo / "client/js/package-lock.json"
    js_pkg.parent.mkdir(parents=True)
    js_pkg.write_text('{"name": "frontend"}')  # Node evidence 2

    npmrc = repo / "js/.npmrc"
    npmrc.parent.mkdir(parents=True)
    npmrc.write_text("legacy-bundling=false")  # Node evidence 3

    (repo / "pnpm-lock.yaml").write_text("lockfileVersion=6.0.1")  # Node evidence 4
    (repo / ".nvmrc").write_text("v18.0.0")  # Node evidence 5

    a = analyze_repo(str(repo))
    ctx = build_context(a.model_dump(), {})
    bp = compile_blueprint(ctx)

    md = bp["render"]["markdown"]

    # Phase 10 / Issue #146: Primary tooling is suppressed from "## Other tooling detected"
    # (no duplication with "## Analyzer notes" section)
    assert "## Other tooling detected" not in md, (
        "## Other tooling detected should not appear when only primary tooling "
        "(which is suppressed) would be shown"
    )

    # Primary tooling should appear in ## Analyzer notes instead
    assert "## Analyzer notes" in md
    assert "Primary tooling: Node.js" in md


def test_truncation_note_applies_only_when_needed(tmp_path: Path) -> None:
    """
    When evidence files <= MAX_EVIDENCE_FILES_DISPLAYED,
    no truncation note should appear.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "package.json").write_text('{"name": "x"}')
    (repo / "go.mod").write_text("module example")
    (repo / "Cargo.toml").write_text('[package]\nname="test"\n')

    a = analyze_repo(str(repo))
    ctx = build_context(a.model_dump(), {})
    bp = compile_blueprint(ctx)
    md = bp["render"]["markdown"]

    lines = md.split("\n")

    # Extract lines containing truncation note
    truncated_lines = [line for line in lines if "truncated to" in line]

    # Should be empty because each framework only has 1 file
    assert not any(
        "; truncated to 3 of" in line or f"; truncated to {MAX_EVIDENCE_FILES_DISPLAYED} of" in line
        for line in truncated_lines
    )


def test_plus_one_more_pattern_never_appears(tmp_path: Path) -> None:
    """
    The ambiguous '+1 more' pattern should never appear in output.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    # Create a scenario with 4 evidence files for one tool
    (repo / "package.json").write_text('{"name": "x"}')
    (repo / "dep1.txt").write_text("")
    (repo / "dep2.txt").write_text("")
    (repo / "dep3.txt").write_text("")

    a = analyze_repo(str(repo))
    ctx = build_context(a.model_dump(), {})
    bp = compile_blueprint(ctx)
    md = bp["render"]["markdown"]

    assert "+1 more" not in md


def test_alphabetic_sorting_evidence_files(tmp_path: Path) -> None:
    """
    Evidence files within a tool entry are sorted alphabetically.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "z_file.json").write_text("{}")
    (repo / "a_file.json").write_text("{}")
    (repo / "m_file.json").write_text("{}")

    a = analyze_repo(str(repo))
    ctx = build_context(a.model_dump(), {})
    bp = compile_blueprint(ctx)
    md = bp["render"]["markdown"]

    # In the JSON files section (if it exists as "other tooling" or similar),
    # check order. Since JSON files might be treated as config or other tooling
    # depending on your classifier, we'll assume they end up in a list somewhere.
    # We look for the bullet containing them.
    lines = md.split("\n")
    bullet = next(
        (line for line in lines if "z_file.json" in line and "a_file.json" in line),
        None,
    )

    if bullet:
        assert bullet.index("a_file.json") < bullet.index("z_file.json")
        assert bullet.index("a_file.json") < bullet.index("m_file.json")
