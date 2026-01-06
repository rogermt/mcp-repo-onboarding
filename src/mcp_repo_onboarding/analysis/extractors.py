import json
import logging
import re
import tomllib
from abc import ABC, abstractmethod
from dataclasses import dataclass
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


_NODE_PKG_JSON_MAX_BYTES = 256_000


def _norm_rel(path: str) -> str:
    return path.replace("\\", "/").lstrip("/")


def _read_text_capped(path: Path, max_bytes: int) -> str | None:
    try:
        if not path.is_file():
            return None
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


@dataclass
class PMContext:
    """Context for package manager detection."""

    all_files: list[str]
    file_names: set[str]  # basename lookup
    pkg_dir: str  # directory of the active package.json
    package_json_data: dict[str, Any]


class PackageManagerStrategy(ABC):
    """Strategy for detecting and using a Node.js package manager."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def detect(self, ctx: PMContext) -> bool:
        """Return True if this package manager is detected."""

    @abstractmethod
    def get_install_command(self, has_lockfile: bool) -> str:
        """Return the install command (e.g. 'npm ci', 'yarn install')."""

    def get_run_command(self, script_name: str) -> str:
        """Return the run command (default: 'pm run script')."""
        return f"{self.name} run {script_name}"


class NpmStrategy(PackageManagerStrategy):
    """Strategy for npm (checks package-lock.json or npm-shrinkwrap.json)."""

    @property
    def name(self) -> str:
        return "npm"

    def detect(self, ctx: PMContext) -> bool:
        return self._has_lockfile(ctx, ("package-lock.json", "npm-shrinkwrap.json"))

    def get_install_command(self, has_lockfile: bool) -> str:
        return "npm ci" if has_lockfile else "npm install"

    def _has_lockfile(self, ctx: PMContext, filenames: tuple[str, ...]) -> bool:
        # 1. Local dir match
        prefix = ctx.pkg_dir.rstrip("/") + "/" if ctx.pkg_dir else ""
        for name in filenames:
            expected = f"{prefix}{name}"
            if any(_norm_rel(f) == expected for f in ctx.all_files):
                return True
        # 2. Global fallback
        return any(name in ctx.file_names for name in filenames)


class LockfileBasedStrategy(PackageManagerStrategy):
    """Generic strategy for lockfile-based PMs (yarn, pnpm, bun)."""

    def __init__(self, pm_name: str, lockfile: str, install_cmd: str) -> None:
        self._pm_name = pm_name
        self._lockfile = lockfile
        self._install_cmd = install_cmd

    @property
    def name(self) -> str:
        return self._pm_name

    def detect(self, ctx: PMContext) -> bool:
        # 1. Local dir
        prefix = ctx.pkg_dir.rstrip("/") + "/" if ctx.pkg_dir else ""
        expected = f"{prefix}{self._lockfile}"
        if any(_norm_rel(f) == expected for f in ctx.all_files):
            return True
        # 2. Global fallback
        return self._lockfile in ctx.file_names

    def get_install_command(self, has_lockfile: bool) -> str:
        return self._install_cmd


# Registry of strategies in priority order
_PM_STRATEGIES: list[PackageManagerStrategy] = [
    LockfileBasedStrategy("pnpm", "pnpm-lock.yaml", "pnpm install"),
    LockfileBasedStrategy("yarn", "yarn.lock", "yarn install"),
    LockfileBasedStrategy("bun", "bun.lockb", "bun install"),
    NpmStrategy(),  # npm is last (default/fallback behavior)
]


def _select_node_package_manager(ctx: PMContext) -> tuple[PackageManagerStrategy | None, bool]:
    """
    Select best strategy. Returns (strategy, has_lockfile).
    """
    # 1. Explicit packageManager field (highest priority)
    pm_field = ctx.package_json_data.get("packageManager")
    if isinstance(pm_field, str) and pm_field.strip():
        name = pm_field.split("@", 1)[0].strip().lower()
        # Find matching strategy by name
        for strategy in _PM_STRATEGIES:
            if strategy.name == name:
                # Trust the field, check lockfile for 'npm ci' behavior
                has_lock = strategy.detect(ctx)
                return strategy, has_lock

    # 2. Lockfile detection
    for strategy in _PM_STRATEGIES:
        if strategy.detect(ctx):
            return strategy, True

    return None, False


def extract_node_package_json_commands(
    repo_root: Path,
    all_files: list[str],
) -> dict[str, list[CommandInfo]]:
    """
    Extract deterministic Node.js commands from package.json + lockfiles.
    """
    root = repo_root.resolve()
    norm = [_norm_rel(p) for p in all_files if isinstance(p, str)]
    names = {Path(p).name for p in norm}

    pkg_candidates = [p for p in norm if Path(p).name == "package.json"]
    if not pkg_candidates:
        return {}

    # Deterministic selection: root preferred, else alphabetical
    pkg_rel = "package.json" if "package.json" in pkg_candidates else sorted(pkg_candidates)[0]
    pkg_dir = str(Path(pkg_rel).parent).replace("\\", "/")
    if pkg_dir == ".":
        pkg_dir = ""

    pkg_abs = (root / pkg_rel).resolve()
    raw = _read_text_capped(pkg_abs, _NODE_PKG_JSON_MAX_BYTES)
    if raw is None:
        return {}

    try:
        data = json.loads(raw)
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    # Build Context
    ctx = PMContext(all_files=norm, file_names=names, pkg_dir=pkg_dir, package_json_data=data)

    # Select Strategy
    strategy, has_lockfile = _select_node_package_manager(ctx)
    if not strategy:
        return {}

    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        scripts = {}

    out: dict[str, list[CommandInfo]] = {
        "install": [],
        "dev": [],
        "start": [],
        "test": [],
        "lint": [],
        "format": [],
    }

    # Install Command
    install_cmd = strategy.get_install_command(has_lockfile)
    if install_cmd:
        out["install"].append(
            CommandInfo(
                command=install_cmd,
                source=f"{pkg_rel}:lockfile",
                description="Install dependencies using the detected Node.js package manager.",
                confidence="derived",
            )
        )

    # Script Commands
    wanted = ("dev", "start", "test", "lint", "format")
    for key in wanted:
        if key in scripts:
            out[key].append(
                CommandInfo(
                    command=strategy.get_run_command(key),
                    source=f"{pkg_rel}:scripts.{key}",
                    description=f"Run the '{key}' script from package.json.",
                    confidence="derived",
                )
            )

    return {k: v for (k, v) in out.items() if v}
