from __future__ import annotations

import json
from pathlib import Path

from mcp_repo_onboarding.analysis.extractors import extract_node_package_json_commands


def test_node_commands_no_package_json(tmp_path: Path) -> None:
    """If no package.json exists, returns empty dict."""
    repo = tmp_path / "repo"
    repo.mkdir()
    out = extract_node_package_json_commands(repo, all_files=[])
    assert out == {}


def test_node_commands_no_scripts_no_invented_script_commands(tmp_path: Path) -> None:
    """If package.json has no scripts, only install command is emitted (if pm detected)."""
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "package.json").write_text(
        json.dumps({"name": "x", "version": "0.0.0"}), encoding="utf-8"
    )
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "package-lock.json"])

    # Install may exist (grounded by lockfile)
    assert "install" in out
    assert out["install"][0].command == "npm ci"
    assert (
        out["install"][0].description
        == "Install dependencies using the detected Node.js package manager."
    )

    # But NO dev/test/lint/format unless scripts exist
    for k in ("dev", "start", "test", "lint", "format"):
        assert k not in out


def test_node_commands_with_scripts_pnpm(tmp_path: Path) -> None:
    """Verify script extraction works with pnpm lockfile."""
    repo = tmp_path / "repo"
    repo.mkdir()

    pkg = {
        "name": "x",
        "version": "0.0.0",
        "scripts": {
            "dev": "vite",
            "test": "vitest",
            "lint": "eslint .",
            "format": "prettier -w .",
            "start": "node dist/index.js",
        },
    }
    (repo / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
    (repo / "pnpm-lock.yaml").write_text("lockfileVersion: 6", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "pnpm-lock.yaml"])

    # Install
    assert out["install"][0].command == "pnpm install"

    # Scripts
    assert out["dev"][0].command == "pnpm run dev"
    assert out["dev"][0].description == "Run the 'dev' script from package.json."

    assert out["test"][0].command == "pnpm run test"
    assert out["lint"][0].command == "pnpm run lint"
    assert out["format"][0].command == "pnpm run format"
    assert out["start"][0].command == "pnpm run start"


def test_node_commands_with_scripts_yarn(tmp_path: Path) -> None:
    """Verify yarn command generation."""
    repo = tmp_path / "repo"
    repo.mkdir()

    pkg = {"scripts": {"test": "jest"}}
    (repo / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
    (repo / "yarn.lock").write_text("", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "yarn.lock"])

    assert out["install"][0].command == "yarn install"
    assert out["test"][0].command == "yarn run test"


def test_node_commands_with_scripts_bun(tmp_path: Path) -> None:
    """Verify bun command generation."""
    repo = tmp_path / "repo"
    repo.mkdir()

    pkg = {"scripts": {"dev": "bun index.ts"}}
    (repo / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
    (repo / "bun.lockb").write_text("", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "bun.lockb"])

    assert out["install"][0].command == "bun install"
    assert out["dev"][0].command == "bun run dev"


def test_node_commands_package_manager_field_priority(tmp_path: Path) -> None:
    """packageManager field in package.json takes precedence over lockfiles."""
    repo = tmp_path / "repo"
    repo.mkdir()

    pkg = {
        "scripts": {"test": "echo test"},
        "packageManager": "pnpm@8.0.0",
    }
    (repo / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
    # Even if package-lock.json exists, pnpm field wins
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "package-lock.json"])

    assert out["install"][0].command == "pnpm install"
    assert out["test"][0].command == "pnpm run test"


def test_node_commands_size_cap(tmp_path: Path) -> None:
    """Oversized package.json should be ignored deterministically."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Oversized package.json
    big = "x" * (256_000 + 10)
    (repo / "package.json").write_text(big, encoding="utf-8")
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "package-lock.json"])
    assert out == {}


def test_node_commands_malformed_json(tmp_path: Path) -> None:
    """Malformed package.json does not crash analysis."""
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "package.json").write_text("{broken", encoding="utf-8")
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    out = extract_node_package_json_commands(repo, all_files=["package.json", "package-lock.json"])
    assert out == {}
