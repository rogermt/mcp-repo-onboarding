import json
import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import configure_logging
from .analysis import analyze_repo as analysis_mod_analyze_repo
from .analysis.onboarding_blueprint import build_onboarding_blueprint_v1
from .config import DEFAULT_MAX_FILES
from .onboarding import read_onboarding as read_onboarding_svc
from .onboarding import write_onboarding as write_onboarding_svc
from .resources import load_mcp_prompt
from .schema import ErrorResponse, RunAndTestCommands

"""
MCP Server implementation for Repo Onboarding.

This module defines the MCP tools exposed by the server.
"""

# Initialize FastMCP Server
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

    # Always return repo-relative POSIX form for determinism.
    return rel.as_posix()


@mcp.tool()
def ping() -> str:
    """Sanity check: returns a small JSON payload to verify MCP connectivity."""
    logger.debug("Ping tool called")
    return '{"ok": true, "tool": "ping"}'


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
        JSON string representation of RepoAnalysis.
    """
    # Resolve root from env var (standard MCP pattern) or CWD
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

    data = analysis.model_dump(exclude_none=True)
    try:
        data["onboarding_blueprint_v1"] = build_onboarding_blueprint_v1(data)
    except Exception as e:
        logger.warning(f"Failed to build onboarding blueprint: {e}")

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
    # Reuse analyze_repo logic
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

    # Map to RunAndTestCommands schema
    # Logic ported from deriveRunAndTestCommands in TS

    # Combine extracted scripts.test + testSetup.commands
    combined_test_cmds = []
    if analysis.scripts.test:
        combined_test_cmds.extend(analysis.scripts.test)
    if analysis.testSetup.commands:
        combined_test_cmds.extend(analysis.testSetup.commands)

    # Deduplicate by command string
    unique_test = {cmd.command: cmd for cmd in combined_test_cmds}.values()

    result = RunAndTestCommands(
        devCommands=analysis.scripts.dev,
        testCommands=list(unique_test),
        buildCommands=analysis.scripts.start,  # TS version mapped scripts.start to buildCommands mostly
    )

    return result.model_dump_json(exclude_none=True, indent=2)


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
            error="Content is required", error_code="INVALID_ARGUMENT"
        ).model_dump_json()

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
            error=str(e), error_code="INVALID_ARGUMENT", details={"path": path}
        ).model_dump_json()


def main() -> None:
    """Entry point for the MCP server."""
    configure_logging()
    logger.info("Starting mcp-repo-onboarding server")
    mcp.run()


if __name__ == "__main__":
    main()
