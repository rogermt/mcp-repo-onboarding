import os
from mcp.server.fastmcp import FastMCP
from typing import Optional

from .analysis import analyze_repo as analysis_mod_analyze_repo
from .onboarding import read_onboarding as read_onboarding_svc
from .onboarding import write_onboarding as write_onboarding_svc
from .schema import RunAndTestCommands

# Initialize FastMCP Server
mcp = FastMCP("repo-onboarding")


@mcp.tool()
def ping() -> str:
    """Sanity check: returns a small JSON payload to verify MCP connectivity."""
    return '{"ok": true, "tool": "ping"}'


@mcp.tool()
def analyze_repo(path: Optional[str] = None, max_files: int = 5000) -> str:
    """
    Analyze the current repository (Python-first) and return a structured summary.

    Args:
        path: Optional sub-path within the repo to analyze. Defaults to repo root.
        max_files: Optional safety cap on number of files to scan.
    """
    # Resolve root from env var (standard MCP pattern) or CWD
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())

    if path:
        target_path = os.path.join(repo_root, path)
    else:
        target_path = repo_root

    analysis = analysis_mod_analyze_repo(target_path, max_files=max_files)

    # Return JSON string via Pydantic
    return analysis.model_dump_json(exclude_none=True, indent=2)


@mcp.tool()
def get_run_and_test_commands(path: Optional[str] = None) -> str:
    """
    Return the main dev, test, and build commands for this repository.
    """
    # Reuse analyze_repo logic
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())
    if path:
        target_path = os.path.join(repo_root, path)
    else:
        target_path = repo_root

    analysis = analysis_mod_analyze_repo(target_path)

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
    """Read the ONBOARDING.md file (or a specified path)."""
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())
    result = read_onboarding_svc(repo_root, path)
    return result.model_dump_json(exclude_none=True, indent=2)


@mcp.tool()
def write_onboarding(
    content: Optional[str] = None,
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
    """
    repo_root = os.environ.get("REPO_ROOT", os.getcwd())

    if content is None:
        return '{"error": "Content is required"}'

    try:
        result = write_onboarding_svc(
            repo_root=repo_root,
            content=content,
            path=path,
            mode=mode,
            create_backup=create_backup,
        )
        return result.model_dump_json(exclude_none=True, indent=2)
    except ValueError as e:
        return f'{{"error": "{str(e)}"}}'


def main():
    mcp.run()


if __name__ == "__main__":
    main()
