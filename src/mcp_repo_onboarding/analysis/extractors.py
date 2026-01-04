import logging
import re
import tomllib
from pathlib import Path
from typing import Any

from ..config import KNOWN_PACKAGE_MANAGERS
from ..describers import COMMAND_DESCRIBER_REGISTRY
from ..schema import CommandInfo

logger = logging.getLogger(__name__)


def extract_makefile_commands(root: Path, makefile_path: str) -> dict[str, list[CommandInfo]]:
    """
    Extract commands from a Makefile.

    Args:
        root: The repository root path.
        makefile_path: Relative path to the Makefile.

    Returns:
        A dictionary mapping categories (test, dev, etc.) to lists of CommandInfo objects.
    """
    commands: dict[str, list[CommandInfo]] = {}
    try:
        content = (root / makefile_path).read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        logger.warning(f"Failed to read Makefile at {makefile_path}: {e}")
        return {}

    target_pattern = re.compile(r"^([a-zA-Z0-9_-]+(?:\s+[a-zA-Z0-9_-]+)*):")

    def _fallback_make_desc(target: str) -> str:
        # Deterministic, grounded in Makefile target existence (not invented behavior).
        if target == "install":
            return "Install dependencies via Makefile target."
        if target == "test":
            return "Run the test suite via Makefile target."
        if target == "lint":
            return "Run linting via Makefile target."
        if target == "format":
            return "Run formatting via Makefile target."
        if target in ("run", "start"):
            return "Run the application via Makefile target."
        return f"Run Makefile target '{target}'."

    target_mapping = {
        "test": "test",
        "lint": "lint",
        "format": "format",
        "dev": "dev",
        "install": "install",
        "run": "start",
        "start": "start",
        "check": "test",
    }

    for line in content.splitlines():
        match = target_pattern.match(line)
        if match:
            targets_str = match.group(1)
            targets = targets_str.split()
            for target in targets:
                if target in target_mapping:
                    category = target_mapping[target]
                    command_str = f"make {target}"
                    cmd_info = CommandInfo(command=command_str, source=f"{makefile_path}:{target}")

                    if command_str in COMMAND_DESCRIBER_REGISTRY:
                        cmd_info = COMMAND_DESCRIBER_REGISTRY[command_str].describe(cmd_info)

                    # Ensure Makefile-derived commands always have a description to prevent LLM drift
                    # (keeps ONBOARDING compliant with the "command bullets always include (Description.)" prompt rule).
                    if not cmd_info.description:
                        cmd_info.description = _fallback_make_desc(target)

                    if category not in commands:
                        commands[category] = []
                    commands[category].append(cmd_info)
    return commands


def _is_safe_description(line: str) -> bool:
    """Check if a comment line is a safe, non-command-like description."""
    line = line.strip()

    # Empty comment is not a description
    if not line:
        return False

    if "export" in line or "=" in line:
        return False

    if line.startswith(("cd ", "bash ", "python ", "make ")):
        return False

    separators = " -_=#"
    separator_count = sum(c in separators for c in line)
    total_chars = len(line)

    if total_chars > 4 and (separator_count / total_chars) > 0.5:
        return False

    if len(line.split()) < 2:
        if line.upper() in ["CONFIG", "SETUP", "MAIN", "TEST", "BUILD", "START", "END"]:
            return False

    return True


_HELPER_SCRIPT_DESC = "Helper script used by other repo scripts."


def _is_helper_script(script_rel_path: str) -> bool:
    name = Path(script_rel_path).name.lower()

    helper_exact = {
        "helper.sh",
        "helpers.sh",
        "util.sh",
        "utils.sh",
        "common.sh",
        "shared.sh",
    }
    helper_prefixes = ("helper", "helpers", "util", "utils", "common", "shared")

    return (
        name in helper_exact
        or name.startswith(helper_prefixes)
        or "helpers" in name
        or "utils" in name
    )


def _fallback_script_description(script_rel_path: str) -> str:
    """
    Deterministic fallback descriptions for repo scripts when no safe header
    description is available.
    """
    if _is_helper_script(script_rel_path):
        return _HELPER_SCRIPT_DESC

    return "Run repo script entrypoint."


def extract_shell_scripts(all_files: list[str], repo_root: Path) -> dict[str, list[CommandInfo]]:
    """
    Find and analyze shell scripts in the scripts/ directory.

    Args:
        all_files: List of all file paths in the repo.
        repo_root: Path to the repository root.

    Returns:
        Dictionary mapping categories to lists of CommandInfo.
    """
    commands: dict[str, list[CommandInfo]] = {"dev": [], "test": []}

    script_files = [
        f for f in all_files if f.replace("\\", "/").startswith("scripts/") and f.endswith(".sh")
    ]

    for script in script_files:
        name = Path(script).name
        command_str = f"bash {script}"

        description = None
        try:
            with open(repo_root / script, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()

                    if not line.startswith("#") and line:
                        break

                    if line.startswith("#") and not line.startswith("#!"):
                        candidate = line.lstrip("#").strip()
                        if _is_safe_description(candidate):
                            description = candidate
                            break
        except OSError as e:
            logger.debug(f"Could not read script {script}: {e}")
            pass

        # Helper scripts should always be described neutrally as helpers,
        # even if they contain "safe" header comments. They are typically not
        # direct user entrypoints.
        if _is_helper_script(script):
            description = _HELPER_SCRIPT_DESC
        else:
            # Normalize empty to None
            if description is not None and not description.strip():
                description = None

            # Deterministic fallback if no safe header description was found
            if description is None:
                description = _fallback_script_description(script)

        cmd_info = CommandInfo(
            command=command_str,
            source=script,
            name=name,
            description=description,
            confidence="derived",
        )

        # Allow registry describer to enrich only when we are using the generic fallback.
        # Helper scripts keep their more specific helper description.
        if (
            cmd_info.description == "Run repo script entrypoint."
            and "bash scripts/" in COMMAND_DESCRIBER_REGISTRY
        ):
            cmd_info = COMMAND_DESCRIBER_REGISTRY["bash scripts/"].describe(cmd_info)

        if "test" in name:
            commands["test"].append(cmd_info)
        else:
            commands["dev"].append(cmd_info)

    return commands


def extract_tox_commands(repo_root: Path, tox_path: str) -> dict[str, list[CommandInfo]]:
    """
    Extract commands from tox.ini.

    Args:
        repo_root: Repository root path.
        tox_path: Relative path to tox.ini.

    Returns:
        Dictionary mapping categories to CommandInfo lists.
    """
    commands: dict[str, list[CommandInfo]] = {"test": [], "lint": []}
    try:
        content = (repo_root / tox_path).read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        logger.warning(f"Failed to read tox.ini at {tox_path}: {e}")
        return commands

    commands["test"].append(
        CommandInfo(command="tox", source=tox_path, description="Run tests via tox")
    )

    if "flake8" in content:
        commands["lint"].append(
            CommandInfo(
                command="tox -e flake8",
                source=tox_path,
                description="Run flake8 linting via tox",
            )
        )

    return commands


def detect_workflow_python_version(repo_root: Path) -> list[str]:
    """
    Detect Python versions specified in GitHub Actions workflows.

    Args:
        repo_root: Repository root path.

    Returns:
        List of detected Python versions (e.g., "3.11").
    """
    versions = set()
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []

    for wf in workflows_dir.glob("*.yml"):
        try:
            content = wf.read_text(encoding="utf-8", errors="ignore")
            env_matches = re.findall(r'PYTHON_VERSION:\s*["\\]?([\d\.]+)["\\]?', content)
            versions.update(env_matches)

            step_matches = re.findall(r'python-version:\s*["\\]?([\d\.]+)["\\]?', content)
            for v in step_matches:
                if not v.startswith("$"):
                    versions.add(v)
        except OSError as e:
            logger.debug(f"Failed to read workflow {wf}: {e}")
            continue

    return sorted(versions)


def extract_pyproject_metadata(repo_root: Path, pyproject_path: str) -> dict[str, Any]:
    """
    Extract metadata from pyproject.toml using tomllib.

    Args:
        repo_root: The repository root path.
        pyproject_path: Relative path to pyproject.toml.

    Returns:
        A dictionary containing extracted metadata (python_version, package_managers, build_backend).
    """
    metadata: dict[str, Any] = {
        "python_version": None,
        "package_managers": [],
        "build_backend": None,
    }

    try:
        content = (repo_root / pyproject_path).read_text(encoding="utf-8", errors="ignore")
        data = tomllib.loads(content)

        # 1. Python Version Hints
        project = data.get("project", {})
        metadata["python_version"] = project.get("requires-python")

        # 2. Build Backend
        build_system = data.get("build-system", {})
        metadata["build_backend"] = build_system.get("build-backend")

        # 3. Package Manager Detection
        tools = data.get("tool", {})
        backend = str(metadata["build_backend"] or "")
        pm_list: list[str] = metadata["package_managers"]

        for key, manager in KNOWN_PACKAGE_MANAGERS.items():
            # Check if manager is explicitly in [tool.X]
            if key in tools:
                if manager not in pm_list:
                    pm_list.append(manager)

            # Check if manager is mentioned in build-backend
            if key in backend.lower():
                if manager not in pm_list:
                    pm_list.append(manager)

    except Exception as e:
        logger.warning(f"Failed to parse pyproject.toml at {pyproject_path}: {e}")

    return metadata
