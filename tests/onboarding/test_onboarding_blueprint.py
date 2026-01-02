from __future__ import annotations

from typing import Any

from mcp_repo_onboarding.analysis.onboarding_blueprint import (
    build_onboarding_blueprint_v1,
    render_blueprint_to_markdown,
)


def _base_analyze_payload() -> dict[str, Any]:
    return {
        "repoPath": "/tmp/repo",
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
        },
        "notes": [],
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
    }


def test_required_headings_order_repo_path_and_no_provenance() -> None:
    analyze = _base_analyze_payload()

    bp = build_onboarding_blueprint_v1(analyze)
    md = render_blueprint_to_markdown(bp)

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

    # Order check (simple monotonic index)
    idxs = [md.index(h) for h in required]
    assert idxs == sorted(idxs)

    # V2
    assert "Repo path: /tmp/repo" in md

    # V3 forbidden pattern
    assert "Python version: No Python version pin detected." not in md

    # V8
    assert "source:" not in md.lower()
    assert "evidence:" not in md.lower()

    # command fallback exact string must appear (since no commands)
    assert "No explicit commands detected." in md


def test_generic_venv_snippet_has_label_immediately_above_first_venv_command() -> None:
    analyze = _base_analyze_payload()
    # No pin + no explicit env setup => generic venv snippet required
    analyze["python"]["pythonVersionHints"] = []
    analyze["python"]["envSetupInstructions"] = []

    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    lines = md.splitlines()

    venv_idx = next(
        i
        for i, ln in enumerate(lines)
        if "python3 -m venv .venv" in ln or "python -m venv .venv" in ln
    )
    assert lines[venv_idx - 1].strip() == "(Generic suggestion)"


def test_no_venv_snippet_when_pin_present_and_no_explicit_env_instructions() -> None:
    analyze = _base_analyze_payload()
    analyze["python"]["pythonVersionHints"] = ["3.11"]
    analyze["python"]["envSetupInstructions"] = []

    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    assert "python3 -m venv .venv" not in md
    assert "python -m venv .venv" not in md
    assert "source .venv/bin/activate" not in md


def test_install_pip_install_r_is_capped_to_one_occurrence() -> None:
    analyze = _base_analyze_payload()
    analyze["python"]["installInstructions"] = [
        "pip install -r requirements.txt",
        "pip install -r requirements-dev.txt",
    ]

    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    assert md.count("pip install -r") == 1


def test_install_make_install_is_sole_install_command() -> None:
    analyze = _base_analyze_payload()
    analyze["scripts"]["install"] = [
        {"command": "make install", "description": "Install deps"},
        {"command": "pip install -r requirements.txt", "description": "Install deps"},
    ]

    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))

    # must contain make install bullet
    assert "* `make install`" in md
    # must NOT contain other install commands if make install exists
    assert "pip install -r" not in md


def test_analyzer_notes_framework_reason_rules_single_and_multi() -> None:
    analyze = _base_analyze_payload()

    # single framework => include reason
    analyze["frameworks"] = [
        {"name": "Flask", "detectionReason": "Detected via pyproject.toml classifiers"}
    ]
    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    assert "## Analyzer notes" in md
    assert (
        "* Frameworks detected (from analyzer): Flask. (Detected via pyproject.toml classifiers.)"
        in md
    )

    # multi frameworks, same reason => include reason
    analyze = _base_analyze_payload()
    analyze["frameworks"] = [
        {"name": "Django", "detectionReason": "Detected via pyproject.toml classifiers"},
        {"name": "Wagtail", "detectionReason": "Detected via pyproject.toml classifiers"},
    ]
    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    assert (
        "* Frameworks detected (from analyzer): Django, Wagtail. (Detected via pyproject.toml classifiers.)"
        in md
    )

    # multi frameworks, different reasons => omit parentheses
    analyze = _base_analyze_payload()
    analyze["frameworks"] = [
        {"name": "Django", "detectionReason": "Detected via classifiers"},
        {"name": "Flask", "detectionReason": "Detected via Poetry deps"},
    ]
    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    assert "* Frameworks detected (from analyzer): Django, Flask." in md
    assert "Frameworks detected (from analyzer): Django, Flask. (" not in md


def test_analyzer_notes_notebooks_adds_dirs_and_avoids_duplicate_note() -> None:
    analyze = _base_analyze_payload()
    analyze["notebooks"] = ["notebooks/examples/", "."]  # analyzer may output "." for root
    analyze["notes"] = [
        "docs list truncated to 10 entries (total=99)",
        "Notebook-centric repo detected; core logic may reside in Jupyter notebooks.",
    ]

    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))
    # should not duplicate notebook-centric note
    assert (
        md.count("Notebook-centric repo detected; core logic may reside in Jupyter notebooks.") == 1
    )
    # dirs line must exist and must end with / for each
    assert "Notebooks found in: notebooks/examples/, ./" in md


def test_env_setup_never_outputs_v3_forbidden_pattern_even_if_hints_corrupted() -> None:
    analyze = {
        "repoPath": "/tmp/repo",
        "python": {
            # Simulate corrupted upstream data:
            "pythonVersionHints": ["No Python version pin detected."],
            "envSetupInstructions": [],
            "installInstructions": [],
            "dependencyFiles": [],
        },
        "scripts": {"dev": [], "start": [], "test": [], "lint": [], "format": [], "install": []},
        "notes": [],
        "notebooks": [],
        "frameworks": [],
        "configurationFiles": [],
        "docs": [],
    }

    md = render_blueprint_to_markdown(build_onboarding_blueprint_v1(analyze))

    assert "Python version: No Python version pin detected." not in md
    assert "No Python version pin detected." in md
