import json
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import configure_logging
from .analysis import analyze_repo as analysis_mod_analyze_repo
from .analysis.onboarding_blueprint import build_onboarding_blueprint_v1
from .analysis.onboarding_blueprint_v2 import build_context as build_blueprint_v2_context
from .analysis.onboarding_blueprint_v2 import compile_blueprint_v2
from .config import DEFAULT_MAX_FILES
from .onboarding import read_onboarding as read_onboarding_svc
from .onboarding import write_onboarding as write_onboarding_svc
from .resources import load_mcp_prompt
from .schema import ErrorResponse, RunAndTestCommands

"""
MCP Server implementation for Repo Onboarding.

This module defines the MCP tools exposed by the server.
"""

mcp = FastMCP("repo-onboarding")
logger = logging.getLogger(__name__)


@mcp.prompt()
def generate_onboarding() -> str:
    """
    Returns the authoritative instructions for generating ONBOARDING.md.
    This enables the slash command usage: /generate_onboarding
    """
    return load_mcp_prompt()


@mcp.tool()
def get_onboarding_template() -> str:
    """
    Returns the authoritative instructions (prompt) for generating ONBOARDING.md.
    Useful for retrieving the prompt content programmatically.
    """
    try:
        return load_mcp_prompt()
    except Exception as e:
        logger.error(f"Failed to read prompt file: {e}")
        return f"Error reading prompt file: {str(e)}"


def _resolve_under_repo_root(repo_root: str, subpath: str | None) -> Path:
    """
    Resolve an optional user-provided subpath under REPO_ROOT.

    Security invariant:
      - The resolved path MUST remain under REPO_ROOT (no .. escape, no absolute escape).
    """
    root = Path(repo_root).resolve()
    target = (root / subpath).resolve() if subpath else root
    try:
        target.relative_to(root)
    except ValueError as e:
        raise ValueError(f"path escapes REPO_ROOT: {subpath}") from e
    return target


def _validate_rel_file_path(repo_root: str, rel_path: str) -> str:
    """
    Validate a file path argument intended to be repo-root-relative (e.g. ONBOARDING.md).

    Returns a normalized repo-relative POSIX path string if valid.
    Raises ValueError if the path is absolute or escapes REPO_ROOT.
    """
    if not rel_path:
        raise ValueError("path must be non-empty")

    p = Path(rel_path)
    if p.is_absolute():
        raise ValueError(f"path must be repo-relative, got absolute: {rel_path}")

    root = Path(repo_root).resolve()
    resolved = (root / p).resolve()
    try:
        rel = resolved.relative_to(root)
    except ValueError as e:
        raise ValueError(f"path escapes REPO_ROOT: {rel_path}") from e

    return rel.as_posix()


@mcp.tool()
def ping() -> str:
    """Sanity check: returns a small JSON payload to verify MCP connectivity."""
    logger.debug("Ping tool called")
    return '{"ok": true, "tool": "ping"}'


def _derive_run_and_test_commands_dict(analysis: Any) -> dict[str, Any]:
    """
    Derive a RunAndTestCommands payload from a RepoAnalysis-like object.
    This is deterministic and uses the already-computed analysis object (no re-scan).
    """
    combined_test_cmds: list[Any] = []

    scripts = getattr(analysis, "scripts", None)
    test_setup = getattr(analysis, "testSetup", None)

    if scripts is not None and getattr(scripts, "test", None):
        combined_test_cmds.extend(scripts.test)

    # Some schemas may or may not have testSetup.commands; handle defensively.
    ts_cmds = getattr(test_setup, "commands", None) if test_setup is not None else None
    if ts_cmds:
        combined_test_cmds.extend(ts_cmds)

    # Deduplicate by command string (only for items that have `.command`)
    unique: dict[str, Any] = {}
    for cmd in combined_test_cmds:
        c = getattr(cmd, "command", None)
        if isinstance(c, str) and c:
            unique[c] = cmd

    result = RunAndTestCommands(
        devCommands=getattr(scripts, "dev", []) if scripts is not None else [],
        testCommands=list(unique.values()),
        buildCommands=getattr(scripts, "start", []) if scripts is not None else [],
    )
    return result.model_dump(exclude_none=True)


@mcp.tool()
def analyze_repo(
    path: str | None = None,
    max_files: int = DEFAULT_MAX_FILES,
) -> str:
    """
    Analyze the current repository (Python-first) and return a structured summary.

    Args:
        path: Optional sub-path within the repo to analyze. Defaults to repo root.
        max_files: Optional safety cap on number of files to scan.

    Returns:
        JSON string representation of RepoAnalysis (plus blueprint keys).
    """
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())
    try:
        target = _resolve_under_repo_root(repo_root, path)
    except ValueError as e:
        return ErrorResponse(
            error=str(e),
            error_code="INVALID_ARGUMENT",
            details={"path": path, "repo_root": repo_root},
        ).model_dump_json(exclude_none=True, indent=2)

    analysis = analysis_mod_analyze_repo(str(target), max_files=max_files)
    logger.info(f"Analyzed repo at {target}")

    data: dict[str, Any] = analysis.model_dump(exclude_none=True)

    # Blueprint v1 (existing)
    try:
        data["onboarding_blueprint_v1"] = build_onboarding_blueprint_v1(data)
    except Exception as e:
        logger.warning(f"Failed to build onboarding blueprint v1: {e}")

    # Blueprint v2 (new)
    try:
        commands_payload = _derive_run_and_test_commands_dict(analysis)
        ctx = build_blueprint_v2_context(data, commands_payload)
        data["onboarding_blueprint_v2"] = compile_blueprint_v2(ctx)
    except Exception as e:
        logger.warning(f"Failed to build onboarding blueprint v2: {e}")

    return json.dumps(data, indent=2)


@mcp.tool()
def get_run_and_test_commands(path: str | None = None) -> str:
    """
    Return the main dev, test, and build commands for this repository.

    Args:
        path: Optional sub-path within the repo to analyze.

    Returns:
        JSON string representation of RunAndTestCommands.
    """
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())
    try:
        target = _resolve_under_repo_root(repo_root, path)
    except ValueError as e:
        return ErrorResponse(
            error=str(e),
            error_code="INVALID_ARGUMENT",
            details={"path": path, "repo_root": repo_root},
        ).model_dump_json(exclude_none=True, indent=2)

    analysis = analysis_mod_analyze_repo(str(target))
    payload = _derive_run_and_test_commands_dict(analysis)
    return RunAndTestCommands(**payload).model_dump_json(exclude_none=True, indent=2)


@mcp.tool()
def read_onboarding(path: str = "ONBOARDING.md") -> str:
    """
    Read the ONBOARDING.md file (or a specified path).

    Args:
        path: Relative path to the onboarding file.

    Returns:
        JSON string representation of OnboardingDocument.
    """
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())
    try:
        safe_rel = _validate_rel_file_path(repo_root, path)
    except ValueError as e:
        return ErrorResponse(
            error=str(e),
            error_code="INVALID_ARGUMENT",
            details={"path": path, "repo_root": repo_root},
        ).model_dump_json(exclude_none=True, indent=2)

    result = read_onboarding_svc(repo_root, safe_rel)
    return result.model_dump_json(exclude_none=True, indent=2)


@mcp.tool()
def write_onboarding(
    content: str | None = None,
    path: str = "ONBOARDING.md",
    mode: str = "overwrite",
    create_backup: bool = True,
) -> str:
    """
    Create or update the ONBOARDING.md file.

    Args:
        content: Markdown content to write.
        path: Relative path to file (default ONBOARDING.md).
        mode: 'create', 'overwrite', or 'append'.
        create_backup: Whether to create a .bak file on overwrite.

    Returns:
        JSON string representation of WriteOnboardingResult or error object.
    """
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())

    if content is None:
        return ErrorResponse(
            error="Content is required",
            error_code="INVALID_ARGUMENT",
        ).model_dump_json(exclude_none=True, indent=2)

    try:
        safe_rel = _validate_rel_file_path(repo_root, path)
    except ValueError as e:
        return ErrorResponse(
            error=str(e),
            error_code="INVALID_ARGUMENT",
            details={"path": path, "repo_root": repo_root},
        ).model_dump_json(exclude_none=True, indent=2)

    try:
        result = write_onboarding_svc(
            repo_root=repo_root,
            content=content,
            path=safe_rel,
            mode=mode,
            create_backup=create_backup,
        )
        return result.model_dump_json(exclude_none=True, indent=2)
    except ValueError as e:
        logger.error(f"Error writing onboarding file: {e}")
        return ErrorResponse(
            error=str(e),
            error_code="INVALID_ARGUMENT",
            details={"path": path},
        ).model_dump_json(exclude_none=True, indent=2)


def main() -> None:
    """Entry point for the MCP server."""
    configure_logging()
    logger.info("Starting mcp-repo-onboarding server")
    mcp.run()


if __name__ == "__main__":
    main()
