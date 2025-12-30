from __future__ import annotations

import shlex

from ..schema import CommandInfo, PythonInfo, RepoAnalysisScriptGroup


def describe_install_command(command: str) -> str:
    """
    Deterministic, grounded description for an install command string.

    Hard constraints:
    - Never invent commands.
    - Only describes the provided command string.
    - Should remain stable across runs for the same input string.

    Note: This pattern (describe_command per family and mirroring into scripts.<group>)
    is intended to be reused for future inferred dev/test/lint commands to ensure
    grounded, static descriptions across all command groups.
    """
    cmd = " ".join(command.strip().split())
    if not cmd:
        return "Install dependencies (from analyzer)."

    low = cmd.lower()

    # --- Makefile / task runners (safe, deterministic) ---
    if low == "make install":
        return "Install dependencies via Makefile target."

    # --- Modern Python PMs (possible future analyzer outputs) ---
    if low == "uv sync" or low.startswith("uv sync "):
        return "Install dependencies using uv."
    if low == "poetry install" or low.startswith("poetry install "):
        return "Install dependencies using Poetry."
    if low == "pdm install" or low.startswith("pdm install "):
        return "Install dependencies using PDM."
    if low == "pipenv install" or low.startswith("pipenv install "):
        return "Install dependencies using Pipenv."

    # --- Parse pip-like commands deterministically ---
    tokens = _safe_shlex_split(cmd)
    # Support: python -m pip install ...
    pip_tokens = _normalize_to_pip_tokens(tokens)

    if pip_tokens:
        return _describe_pip_install(pip_tokens)

    # --- Generic “install” patterns (optional, conservative) ---
    # Keep these neutral; don’t assume more than the command literally says.
    if low in ("npm install", "npm ci") or low.startswith("npm install "):
        return "Install dependencies using npm."
    if low == "yarn install" or low.startswith("yarn install "):
        return "Install dependencies using Yarn."
    if low == "pnpm install" or low.startswith("pnpm install "):
        return "Install dependencies using pnpm."

    return "Install dependencies (from analyzer)."


def _safe_shlex_split(cmd: str) -> list[str]:
    try:
        return shlex.split(cmd)
    except Exception:
        # Deterministic fallback
        return cmd.split()


def _normalize_to_pip_tokens(tokens: list[str]) -> list[str] | None:
    """
    Return tokens starting with pip tool name, or None if not pip-like.

    Supports:
      - pip install ...
      - pip3 install ...
      - python -m pip install ...
      - python3 -m pip install ...
    """
    if not tokens:
        return None

    t0 = tokens[0].lower()

    # pip / pip3 direct
    if t0 in ("pip", "pip3"):
        return tokens

    # python -m pip ...
    if (
        len(tokens) >= 3
        and t0 in ("python", "python3")
        and tokens[1] == "-m"
        and tokens[2].lower() == "pip"
    ):
        return ["pip", *tokens[3:]]

    return None


def _describe_pip_install(pip_tokens: list[str]) -> str:
    """
    Describe pip install commands deterministically.

    Input starts with "pip" (normalized).
    """
    # Expect: pip install ...
    if len(pip_tokens) < 2:
        return "Install Python packages via pip."

    verb = pip_tokens[1].lower()

    # Only handle install here; everything else stays generic
    if verb != "install":
        if verb in ("freeze", "list", "show"):
            return f"Inspect installed packages via pip ({verb})."
        if verb in ("download",):
            return "Download Python packages via pip."
        return "Manage Python packages via pip."

    args = pip_tokens[2:]

    # Common upgrades
    if _has_flag(args, "-u") or _has_flag(args, "-U") or _has_flag(args, "--upgrade"):
        # If upgrading pip itself
        if any(a.lower() == "pip" for a in args):
            return "Upgrade pip."
        return "Upgrade Python package(s) via pip."

    # Editable install
    if _has_flag(args, "-e") or _has_flag(args, "--editable"):
        # If the target is the current project (.)
        if "." in args:
            return "Install the project in editable mode."
        return "Install package(s) in editable mode via pip."

    # Requirements file install
    req = _flag_value(args, "-r") or _flag_value(args, "--requirement")
    if req:
        return f"Install dependencies from {req}."

    # Direct project install (.)
    if args == ["."] or (args and args[0] == "."):
        # Covers: pip install . and pip install .[extra]
        if args[0].startswith(".[") and args[0].endswith("]"):
            return "Install the project package with extras."
        return "Install the project package."

    # If it looks like a single named requirement, describe that without claiming behavior
    first_req = next((a for a in args if a and not a.startswith("-")), None)
    if first_req:
        return "Install Python package(s) via pip."

    return "Install Python packages via pip."


def _has_flag(args: list[str], flag: str) -> bool:
    return any(a == flag for a in args)


def _flag_value(args: list[str], flag: str) -> str | None:
    """
    Return the value associated with a flag, supporting:
      - -r requirements.txt
      - --requirement requirements.txt
    Does NOT support --flag=value (keep simple & deterministic).
    """
    for i, a in enumerate(args):
        if a == flag and i + 1 < len(args):
            v = args[i + 1].strip()
            return v or None
    return None


def _ensure_period(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    return s if s.endswith(".") else (s + ".")


def merge_python_install_instructions_into_scripts(
    scripts: RepoAnalysisScriptGroup,
    python_info: PythonInfo | None,
) -> None:
    """
    Copy python_info.installInstructions (strings) into scripts.install as CommandInfo,
    adding deterministic descriptions, with guards aligned to your prompt/validator:

    - If "make install" already exists in scripts.install, do NOT add anything else.
      (Prompt rule: if make install detected, it must be sole install command.)
    - Enforce max ONE "pip install -r ..." across the merged install commands (V7 guard).
    - Deduplicate by exact command string.
    """
    if python_info is None:
        return

    install_instr = python_info.installInstructions or []
    if not install_instr:
        return

    if not hasattr(scripts, "install"):
        return

    existing_cmds = set()
    for ci in scripts.install:
        if isinstance(ci, CommandInfo) and isinstance(ci.command, str):
            existing_cmds.add(ci.command.strip())

    if "make install" in existing_cmds:
        return

    pip_install_r_seen = any("pip install -r" in c for c in existing_cmds)

    for raw in install_instr:
        if not isinstance(raw, str):
            continue
        cmd = raw.strip()
        if not cmd:
            continue
        if cmd in existing_cmds:
            continue

        if "pip install -r" in cmd:
            if pip_install_r_seen:
                continue
            pip_install_r_seen = True

        desc = _ensure_period(describe_install_command(cmd))

        scripts.install.append(
            CommandInfo(
                command=cmd,
                source="python.installInstructions",
                description=desc,
            )
        )
        existing_cmds.add(cmd)
