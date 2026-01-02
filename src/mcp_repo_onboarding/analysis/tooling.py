"""Other tooling detection (non-Python).

Static-only detection. No subprocess calls, no network, no file content reads.
Reports evidence files only — does NOT suggest commands.

Phase 8 scaffolding for future polyglot support (#81).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Evidence file patterns for each tooling ecosystem
# Each entry: tooling_name -> {files: tuple, note: str}
TOOLING_EVIDENCE_REGISTRY: dict[str, dict[str, Any]] = {
    "Node.js": {
        "files": (
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            ".nvmrc",
            ".node-version",
            ".npmrc",
        ),
        "note": "Node.js tooling detected. See package.json for details.",
    },
    "Go": {
        "files": (
            "go.mod",
            "go.sum",
        ),
        "note": "Go module detected.",
    },
    "Rust": {
        "files": (
            "Cargo.toml",
            "Cargo.lock",
        ),
        "note": "Rust crate detected.",
    },
    "Ruby": {
        "files": (
            "Gemfile",
            "Gemfile.lock",
            ".ruby-version",
        ),
        "note": "Ruby project detected.",
    },
    "Java": {
        "files": (
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "settings.gradle",
            "settings.gradle.kts",
        ),
        "note": "Java/JVM project detected.",
    },
    "Docker": {
        "files": (
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        ),
        "note": "Docker configuration detected.",
    },
}


@dataclass(frozen=True)
class ToolingDetection:
    """Result of tooling detection."""

    name: str
    evidence_files: tuple[str, ...]
    note: str | None = None


def detect_other_tooling(all_files: list[str]) -> list[ToolingDetection]:
    """Detect non-Python tooling from file list.

    Static-only. No subprocess, no file content reads.
    Returns evidence files only — does NOT suggest commands.

    Args:
        all_files: List of repo-relative file paths.

    Returns:
        List of ToolingDetection results, sorted by name.
    """
    # Build lookup set of lowercase filenames for matching
    file_names_lower: dict[str, str] = {}
    for f in all_files:
        name_lower = Path(f).name.lower()
        if name_lower not in file_names_lower:
            file_names_lower[name_lower] = f  # Keep first occurrence

    detections: list[ToolingDetection] = []

    for tooling_name, config in TOOLING_EVIDENCE_REGISTRY.items():
        evidence_patterns = config["files"]
        note = config.get("note")

        # Find which evidence files are present
        found: list[str] = []
        for ev in evidence_patterns:
            ev_lower = ev.lower()
            if ev_lower in file_names_lower:
                found.append(file_names_lower[ev_lower])

        if found:
            detections.append(
                ToolingDetection(
                    name=tooling_name,
                    evidence_files=tuple(sorted(found)),
                    note=note,
                )
            )

    # Deterministic order by name
    return sorted(detections, key=lambda d: d.name)
