#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


def validate_onboarding(content: str, allow_provenance: bool = False) -> list[str]:
    errors = []
    lines = content.splitlines()

    # V1: Required headings must exist (exact) and in order
    required_headings = [
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

    found_headings = []
    for line in lines:
        if line.startswith("#"):
            heading = line.strip()
            if heading in required_headings:
                found_headings.append(heading)
            elif heading == "## Analyzer notes":
                # Optional, don't check order here but check V6 later
                continue

    # Order check
    if found_headings != required_headings:
        missing = [h for h in required_headings if h not in found_headings]
        if missing:
            errors.append(f"V1: Missing required headings: {missing}")
        else:
            # Check for duplicates or wrong order
            errors.append(
                f"V1: Headings out of order or duplicated. Expected: {required_headings}, Found: {found_headings}"
            )

    # V2: Repo path line must be present
    overview_found = False
    repo_path_found = False
    for i, line in enumerate(lines):
        if line.strip() == "## Overview":
            overview_found = True
            # Check next few lines for Repo path
            for j in range(i + 1, min(i + 6, len(lines))):
                if re.match(r"^Repo path:\s+\S+", lines[j].strip()):
                    repo_path_found = True
                    break
                if lines[j].startswith("#"):  # Hit next heading
                    break
    if overview_found and not repo_path_found:
        errors.append("V2: Missing or empty 'Repo path: <path>' line under ## Overview.")

    # V3: “No pin” phrasing must be exact and standalone
    for i, line in enumerate(lines):
        if "No Python version pin detected." in line:
            if "Python version:" in line:
                errors.append(
                    f"V3: Forbidden pattern found on line {i + 1}: '{line.strip()}'. The phrase must be exact and standalone."
                )

    # V4: Venv snippet labeling
    venv_commands = ["python -m venv .venv", "python3 -m venv .venv"]
    for i, line in enumerate(lines):
        if any(cmd in line for cmd in venv_commands):
            # Check preceding 3 lines for (Generic suggestion)
            label_found = False
            for j in range(max(0, i - 3), i):
                if "(Generic suggestion)" in lines[j]:
                    label_found = True
                    break
            if not label_found:
                errors.append(
                    f"V4: Venv snippet found on line {i + 1} without '(Generic suggestion)' label within 3 lines above."
                )

    # V5: Command formatting
    command_sections = [
        "## Install dependencies",
        "## Run / develop locally",
        "## Run tests",
        "## Lint / format",
    ]
    current_section = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped in command_sections:
            current_section = stripped
        elif line.startswith("#"):
            current_section = None

        if current_section and (stripped.startswith("*") or stripped.startswith("-")):
            content_line = stripped.lstrip("*-").strip()
            if not content_line or content_line == "No explicit commands detected.":
                continue

            # Check for backticks
            if not re.search(r"`[^`]+`", content_line):
                # Heuristic: if it looks like a command, it must be backticked
                if re.match(
                    r"^(pip|python|make|tox|gh|npm|yarn|go|cargo|pytest|ruff|mypy|bash|sh|./)\b",
                    content_line.lower(),
                ):
                    errors.append(
                        f"V5: Command on line {i + 1} must be wrapped in backticks: '{content_line}'"
                    )

            # Check for description parentheses: `command` (Description.)
            # Match backticked command and then check what's after it
            match = re.search(r"(`[^`]+`)\s*(.*)", content_line)
            if match:
                desc = match.group(2).strip()
                if desc:
                    if not (desc.startswith("(") and desc.endswith(")")):
                        errors.append(
                            f"V5: Description on line {i + 1} must be in parentheses: '{desc}'"
                        )

    # V6: Analyzer notes section policy
    for i, line in enumerate(lines):
        if line.strip() == "## Analyzer notes":
            has_notes = False
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#"):
                    break
                stripped_j = lines[j].strip()
                if stripped_j.startswith(("*", "-")):
                    note_content = stripped_j.lstrip("*-").strip()
                    if note_content and not re.search(r"\(empty\)", note_content, re.I):
                        has_notes = True
                        break
            if not has_notes:
                errors.append(
                    "V6: ## Analyzer notes section exists but is empty or contains placeholder text."
                )

    # V7: Install policy guard
    install_section = False
    pip_install_r_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped == "## Install dependencies":
            install_section = True
        elif line.startswith("#") and stripped != "## Install dependencies":
            install_section = False

        if install_section and "pip install -r" in line:
            pip_install_r_count += 1

    if pip_install_r_count > 1:
        errors.append(
            f"V7: Multiple 'pip install -r' lines found ({pip_install_r_count}). Max 1 allowed unless explicitly detected."
        )

    # V8: No provenance hidden (standard mode)
    if not allow_provenance:
        for i, line in enumerate(lines):
            if re.search(r"\b(source|evidence):", line, re.I):
                errors.append(
                    f"V8: Provenance found on line {i + 1}: '{line.strip()}'. Provenance is forbidden in standard mode."
                )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ONBOARDING.md formatting rules.")
    parser.add_argument("file", help="Path to ONBOARDING.md file")
    parser.add_argument(
        "--allow-provenance", action="store_true", help="Allow 'source:' or 'evidence:' strings"
    )
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    errors = validate_onboarding(content, allow_provenance=args.allow_provenance)

    if errors:
        print(f"Validation failed for {file_path}:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"Validation passed for {file_path}.")
        sys.exit(0)


if __name__ == "__main__":
    main()
