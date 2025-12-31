from __future__ import annotations

from typing import Any

import pytest

from mcp_repo_onboarding.analysis.onboarding_blueprint_v2 import (
    build_context,
    compile_blueprint_v2,
    render_blueprint_to_markdown,
)


def _mk_analyze(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    base: dict[str, Any] = {
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
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
        "testSetup": {"commands": []},
    }
    if overrides:
        for k, v in overrides.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k].update(v)
            else:
                base[k] = v
    return base


def _mk_cmds(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    base: dict[str, Any] = {"devCommands": [], "testCommands": [], "buildCommands": []}
    if overrides:
        base.update(overrides)
    return base


def _bp(analyze: dict[str, Any], cmds: dict[str, Any]) -> dict[str, Any]:
    ctx = build_context(analyze, cmds)
    return compile_blueprint_v2(ctx)


def test_shape_and_format():
    bp = _bp(_mk_analyze(), _mk_cmds())
    assert bp["format"] == "onboarding_blueprint_v2"
    assert bp["render"]["mode"] == "verbatim"
    assert isinstance(bp["render"]["markdown"], str)
    assert isinstance(bp["sections"], list)


def test_internal_consistency_renderer_equals_markdown():
    bp = _bp(_mk_analyze(), _mk_cmds())
    assert render_blueprint_to_markdown(bp) == bp["render"]["markdown"]


def test_required_headings_present_in_order():
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]

    required = [
        "# ONBOARDING.md",
        "## Overview",
        "## Environment setup",
        "## Install dependencies",
        "## Run / develop locally",
        "## Run tests",
        "## Lint / format",
        "## Dependency files detected",
        "## Useful configuration files",
        "## Useful docs",
    ]

    pos = -1
    for h in required:
        p = md.find(h)
        assert p != -1, f"missing heading: {h}"
        assert p > pos, f"heading out of order: {h}"
        pos = p


def test_repo_path_line_present():
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]
    assert "Repo path: /test/repo" in md


def test_v3_forbidden_pattern_never_emitted():
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]
    assert "Python version: No Python version pin detected." not in md


def test_venv_strict_rules():
    # Case B: no pin + no explicit env => must include generic snippet + label
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]
    assert "No Python version pin detected." in md
    assert "(Generic suggestion)" in md
    assert "python3 -m venv .venv" in md

    # Case C: pin exists + no explicit env => no venv snippet
    analyze = _mk_analyze()
    analyze["python"]["pythonVersionHints"] = ["3.12"]
    bp2 = _bp(analyze, _mk_cmds())
    md2 = bp2["render"]["markdown"]
    assert "Python version: 3.12" in md2
    assert "(Generic suggestion)" not in md2
    assert "python3 -m venv .venv" not in md2
    assert "source .venv/bin/activate" not in md2


def test_command_section_formatting():
    analyze = _mk_analyze()
    analyze["scripts"]["test"] = [{"command": "tox", "description": "Run tests via tox."}]
    bp = _bp(analyze, _mk_cmds())
    md = bp["render"]["markdown"]
    assert "* `tox` (Run tests via tox.)" in md


def test_v7_only_one_pip_install_r_line():
    analyze = _mk_analyze()
    analyze["python"]["installInstructions"] = [
        "pip install -r requirements.txt",
        "pip install -r requirements-dev.txt",
    ]
    bp = _bp(analyze, _mk_cmds())
    md = bp["render"]["markdown"]
    assert md.count("pip install -r") == 1


def test_no_provenance_strings():
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]
    assert "source:" not in md
    assert "evidence:" not in md


def test_bullet_style_star_only():
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]
    assert "\n- " not in md


def test_best_effort_validator_import(tmp_path):
    """
    Optional: run validator if importable. Skip if not importable.
    """
    bp = _bp(_mk_analyze(), _mk_cmds())
    md = bp["render"]["markdown"]

    p = tmp_path / "ONBOARDING.md"
    p.write_text(md, encoding="utf-8")

    try:
        from docs.evaluation import validate_onboarding  # type: ignore
    except Exception:
        pytest.skip("Validator module not importable in unit test environment.")

    if hasattr(validate_onboarding, "validate_file"):
        validate_onboarding.validate_file(str(p))  # type: ignore[attr-defined]
    else:
        pytest.skip("validate_file entrypoint not found.")


def test_file_description_sanitizes_double_period():
    analyze = _mk_analyze()
    analyze["configurationFiles"] = [
        {"path": "tox.ini", "description": "Test environment orchestrator (tox).."}
    ]
    bp = _bp(analyze, _mk_cmds())
    md = bp["render"]["markdown"]
    assert "* tox.ini (Test environment orchestrator (tox).)" in md
    assert ".." not in md


def test_file_description_strips_non_ascii_garbage():
    analyze = _mk_analyze()
    analyze["configurationFiles"] = [
        {
            "path": ".pre-commit-config.yaml",
            "description": "Pre-commit hooks configuration (code quality automation). Вас",
        }
    ]
    bp = _bp(analyze, _mk_cmds())
    md = bp["render"]["markdown"]
    assert "Вас" not in md
    assert (
        "* .pre-commit-config.yaml (Pre-commit hooks configuration (code quality automation).)"
        in md
    )
