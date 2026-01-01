import sys
from pathlib import Path

# Add the directory containing validate_onboarding.py to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

from validate_onboarding import validate_onboarding

VALID_ONBOARDING = """# ONBOARDING.md

## Overview
Repo path: /home/user/repo
Summary of the project.

## Environment setup
Python version: 3.14

## Install dependencies
* `pip install -r requirements.txt` (Install dependencies via pip.)

## Run / develop locally
* `python main.py` (Run the main application.)

## Run tests
* `pytest` (Run tests using pytest.)

## Lint / format
* `ruff check .` (Lint code using Ruff.)

## Dependency files detected
* requirements.txt

## Useful configuration files
* pyproject.toml

## Useful docs
* README.md
"""


def test_valid_onboarding() -> None:
    errors = validate_onboarding(VALID_ONBOARDING)
    assert not errors


def test_v1_missing_heading() -> None:
    content = VALID_ONBOARDING.replace("## Run tests", "## Testing")
    errors = validate_onboarding(content)
    assert any("V1: Missing required headings" in e for e in errors)


def test_v1_wrong_order() -> None:
    # Physically swap the titles to ensure they are out of order
    content = (
        VALID_ONBOARDING.replace("## Overview", "TEMP")
        .replace("## Environment setup", "## Overview")
        .replace("TEMP", "## Environment setup")
    )
    errors = validate_onboarding(content)
    assert any("V1: Headings out of order" in e for e in errors)


def test_v2_missing_repo_path() -> None:
    content = VALID_ONBOARDING.replace("Repo path: /home/user/repo", "Repository: /home/user/repo")
    errors = validate_onboarding(content)
    assert any("V2: Missing or empty 'Repo path:" in e for e in errors)


def test_v3_forbidden_prefix() -> None:
    content = VALID_ONBOARDING.replace(
        "Python version: 3.14", "Python version: No Python version pin detected."
    )
    errors = validate_onboarding(content)
    assert any("V3: Forbidden pattern found" in e for e in errors)


def test_v4_venv_unlabeled() -> None:
    bad_venv = """## Environment setup
Python version: 3.14
* `python -m venv .venv`"""
    content = VALID_ONBOARDING.replace("## Environment setup\nPython version: 3.14", bad_venv)
    errors = validate_onboarding(content)
    assert any("V4: Venv snippet found" in e for e in errors)


def test_v4_venv_labeled() -> None:
    good_venv = """## Environment setup
Python version: 3.14
(Generic suggestion)
* `python -m venv .venv`"""
    content = VALID_ONBOARDING.replace("## Environment setup\nPython version: 3.14", good_venv)
    errors = validate_onboarding(content)
    # Filter for V4 errors only as VALID_ONBOARDING might have shifted
    v4_errors = [e for e in errors if "V4" in e]
    assert not v4_errors


def test_v5_command_no_backticks() -> None:
    content = VALID_ONBOARDING.replace(
        "`pytest` (Run tests using pytest.)", "pytest (Run tests using pytest.)"
    )
    errors = validate_onboarding(content)
    assert any("V5: Command on line" in e for e in errors)


def test_v5_description_no_parens() -> None:
    content = VALID_ONBOARDING.replace(
        "`pytest` (Run tests using pytest.)", "`pytest` Run tests using pytest."
    )
    errors = validate_onboarding(content)
    assert any("V5: Description on line" in e for e in errors)


def test_v6_empty_analyzer_notes() -> None:
    content = VALID_ONBOARDING + "\n## Analyzer notes\n"
    errors = validate_onboarding(content)
    assert any("V6: ## Analyzer notes section exists but is empty" in e for e in errors)


def test_v6_placeholder_analyzer_notes() -> None:
    content = VALID_ONBOARDING + "\n## Analyzer notes\n* (empty)\n"
    errors = validate_onboarding(content)
    assert any("V6: ## Analyzer notes section exists but is empty" in e for e in errors)


def test_v7_multiple_pip_install() -> None:
    content = VALID_ONBOARDING.replace(
        "## Install dependencies\n* `pip install -r requirements.txt` (Install dependencies via pip.)",
        "## Install dependencies\n* `pip install -r requirements.txt`\n* `pip install -r dev-requirements.txt`",
    )
    errors = validate_onboarding(content)
    assert any("V7: Multiple 'pip install -r' lines found" in e for e in errors)


def test_v8_provenance_forbidden() -> None:
    content = VALID_ONBOARDING + "\n* source: pyproject.toml"
    errors = validate_onboarding(content)
    assert any("V8: Provenance found" in e for e in errors)


def test_v8_provenance_allowed() -> None:
    content = VALID_ONBOARDING + "\n* source: pyproject.toml"
    errors = validate_onboarding(content, allow_provenance=True)
    v8_errors = [e for e in errors if "V8" in e]
    assert not v8_errors
