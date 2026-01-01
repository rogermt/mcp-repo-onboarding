"""
Registry of section builders and shared constants for blueprint engine.

All helpers and logic copied verbatim from reference v2 implementation.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .context import Context

# Constants (copied verbatim from reference)
BULLET = "* "

NO_COMMANDS = "No explicit commands detected."
NO_DEPS = "No dependency files detected."
NO_CONFIG = "No useful configuration files detected."
NO_DOCS = "No useful docs detected."

NOTEBOOK_CENTRIC = "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."

GENERIC_LABEL = "(Generic suggestion)"
GENERIC_VENV_LINES = [
    GENERIC_LABEL,
    f"{BULLET}`python3 -m venv .venv` (Create virtual environment.)",
    f"{BULLET}`source .venv/bin/activate` (Activate virtual environment.)",
]

VENV_MARKERS = ("python -m venv .venv", "python3 -m venv .venv")


@dataclass(frozen=True)
class SectionSpec:
    """Specification for a blueprint section."""

    section_id: str
    heading: str
    builder: Any  # Callable[[Context], dict[str, Any] | None]


# ============================================================================
# Helpers (copied verbatim from reference)
# ============================================================================


def _python_dict(ctx: Context) -> dict[str, Any]:
    py = ctx.analyze.get("python")
    return py if isinstance(py, dict) else {}


def _scripts_dict(ctx: Context) -> dict[str, Any]:
    s = ctx.analyze.get("scripts")
    return s if isinstance(s, dict) else {}


def _as_cmdinfo_list(x: Any) -> list[dict[str, Any]]:
    if not isinstance(x, list):
        return []
    out: list[dict[str, Any]] = []
    for it in x:
        if isinstance(it, dict) and isinstance(it.get("command"), str) and it["command"].strip():
            out.append(it)
    return out


def _dedupe_cmds(cmds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for c in cmds:
        if not isinstance(c, dict):
            continue
        cmd = (c.get("command") or "").strip()
        if not cmd or cmd in seen:
            continue
        seen.add(cmd)
        out.append(c)
    return out


def _ensure_single_trailing_period(s: str) -> str:
    """
    Deterministic punctuation:
    - remove any trailing '.' chars
    - add exactly one '.'
    """
    s = s.strip()
    if not s:
        return s
    while s.endswith("."):
        s = s[:-1].rstrip()
    return s + "."


def _sanitize_desc(desc: str) -> str:
    """
    Sanitize DESCRIPTION text only (not paths):
    - drop non-ASCII (prevents random 'Вас' garbage)
    - normalize whitespace
    - strip provenance substrings
    - ensure exactly one trailing period
    """
    # keep basic ASCII printable only
    cleaned = "".join(ch for ch in desc if 32 <= ord(ch) < 127)
    cleaned = " ".join(cleaned.split()).strip()

    # remove provenance markers defensively
    cleaned = cleaned.replace("source:", "").replace("evidence:", "")
    cleaned = " ".join(cleaned.split()).strip()

    if not cleaned:
        return ""

    return _ensure_single_trailing_period(cleaned)


def _first_index_matching(lines: list[str], markers: Iterable[str]) -> int | None:
    for i, ln in enumerate(lines):
        for m in markers:
            if m in ln:
                return i
    return None


def _normalize_env_instruction(s: str) -> str:
    st = s.strip()
    if st.startswith(("* ", "- ")):
        st = st[2:].strip()
    if st.startswith("`") and st.endswith("`"):
        return st
    return f"`{st}`"


def _format_cmd(c: dict[str, Any]) -> str:
    cmd = (c.get("command") or "").strip()

    desc = c.get("description")
    if not isinstance(desc, str) or not desc.strip():
        desc = "No description provided by analyzer."
    desc_clean = _sanitize_desc(desc) or "No description provided by analyzer."

    return f"{BULLET}`{cmd}` ({desc_clean})"


def _desc_for(cmd: str, candidates: list[dict[str, Any]]) -> str | None:
    for c in candidates:
        if (c.get("command") or "").strip() == cmd:
            d = c.get("description")
            if isinstance(d, str) and d.strip():
                return d.strip()
    return None


def _repo_path(ctx: Context) -> str:
    rp = ctx.analyze.get("repoPath")
    return rp if isinstance(rp, str) and rp.strip() else "."


# ============================================================================
# Section builders (copied verbatim from reference, with minimal refactoring)
# ============================================================================


def _sec(section_id: str, heading: str, lines: list[str]) -> dict[str, Any]:
    return {"id": section_id, "heading": heading, "lines": lines}


def build_title_section(ctx: Context) -> dict[str, Any] | None:
    """Build title section."""
    return _sec("title", "# ONBOARDING.md", [])


def build_overview_section(ctx: Context) -> dict[str, Any] | None:
    """Build overview section."""
    return _sec("overview", "## Overview", [f"Repo path: {_repo_path(ctx)}"])


def build_env_setup_section(ctx: Context) -> dict[str, Any] | None:
    """Build environment setup section."""
    lines = _env_setup_lines(ctx)
    return _sec("env_setup", "## Environment setup", lines)


def build_install_section(ctx: Context) -> dict[str, Any] | None:
    """Build install dependencies section."""
    lines = _install_lines(ctx)
    return _sec("install", "## Install dependencies", lines)


def build_run_local_section(ctx: Context) -> dict[str, Any] | None:
    """Build run/develop locally section."""
    lines = _dev_lines(ctx)
    return _sec("run_local", "## Run / develop locally", lines)


def build_run_tests_section(ctx: Context) -> dict[str, Any] | None:
    """Build run tests section."""
    lines = _test_lines(ctx)
    return _sec("run_tests", "## Run tests", lines)


def build_lint_format_section(ctx: Context) -> dict[str, Any] | None:
    """Build lint/format section."""
    lines = _lint_format_lines(ctx)
    return _sec("lint_format", "## Lint / format", lines)


def build_analyzer_notes_section(ctx: Context) -> dict[str, Any] | None:
    """Build analyzer notes section (only if content exists)."""
    lines = _analyzer_notes_lines(ctx)
    if not lines:
        return None
    return _sec("analyzer_notes", "## Analyzer notes", lines)


def build_deps_section(ctx: Context) -> dict[str, Any] | None:
    """Build dependency files section."""
    lines = _dep_lines(ctx)
    return _sec("deps", "## Dependency files detected", lines)


def build_config_section(ctx: Context) -> dict[str, Any] | None:
    """Build configuration files section."""
    lines = _config_lines(ctx)
    return _sec("config", "## Useful configuration files", lines)


def build_docs_section(ctx: Context) -> dict[str, Any] | None:
    """Build docs section."""
    lines = _docs_lines(ctx)
    return _sec("docs", "## Useful docs", lines)


# ============================================================================
# Helper functions for section content (copied verbatim from reference)
# ============================================================================


def _env_setup_lines(ctx: Context) -> list[str]:
    py = _python_dict(ctx)
    hints = [h for h in (py.get("pythonVersionHints") or []) if isinstance(h, str) and h.strip()]
    env_instr = [
        s for s in (py.get("envSetupInstructions") or []) if isinstance(s, str) and s.strip()
    ]

    lines: list[str] = []

    if hints:
        lines.append(f"Python version: {hints[0]}")
    else:
        lines.append("No Python version pin detected.")

    if env_instr:
        bullets = [f"{BULLET}{_normalize_env_instruction(s)}" for s in env_instr]
        first_venv_idx = _first_index_matching(bullets, VENV_MARKERS)
        if first_venv_idx is not None:
            bullets.insert(first_venv_idx, GENERIC_LABEL)
        lines.extend(bullets)
        return lines

    if not hints:
        lines.extend(GENERIC_VENV_LINES)
        return lines

    # strict: no gratuitous venv when pin exists and no explicit env
    return lines


def _install_lines(ctx: Context) -> list[str]:
    py = _python_dict(ctx)
    scripts = _scripts_dict(ctx)

    install_cmds = _as_cmdinfo_list(scripts.get("install"))
    for s in py.get("installInstructions") or []:
        if isinstance(s, str) and s.strip():
            install_cmds.append({"command": s.strip(), "description": None})

    if any((c.get("command") or "").strip() == "make install" for c in install_cmds):
        return [
            _format_cmd(
                {"command": "make install", "description": _desc_for("make install", install_cmds)}
            )
        ]

    # V7: max one pip install -r
    filtered: list[dict[str, Any]] = []
    pip_r_seen = False
    for c in install_cmds:
        cmd = (c.get("command") or "").strip()
        if "pip install -r" in cmd:
            if pip_r_seen:
                continue
            pip_r_seen = True
        filtered.append(c)

    filtered = _dedupe_cmds(filtered)
    return [_format_cmd(c) for c in filtered] if filtered else [NO_COMMANDS]


def _dev_lines(ctx: Context) -> list[str]:
    scripts = _scripts_dict(ctx)
    cmds = _as_cmdinfo_list(scripts.get("dev")) + _as_cmdinfo_list(scripts.get("start"))
    cmds += _as_cmdinfo_list(ctx.commands.get("devCommands"))
    cmds = _dedupe_cmds(cmds)
    return [_format_cmd(c) for c in cmds] if cmds else [NO_COMMANDS]


def _test_lines(ctx: Context) -> list[str]:
    scripts = _scripts_dict(ctx)

    test_setup = ctx.analyze.get("testSetup")
    test_setup_cmds: list[dict[str, Any]] = []
    if isinstance(test_setup, dict):
        test_setup_cmds = _as_cmdinfo_list(test_setup.get("commands"))

    cmds = _as_cmdinfo_list(scripts.get("test")) + test_setup_cmds
    cmds += _as_cmdinfo_list(ctx.commands.get("testCommands"))
    cmds = _dedupe_cmds(cmds)
    return [_format_cmd(c) for c in cmds] if cmds else [NO_COMMANDS]


def _lint_format_lines(ctx: Context) -> list[str]:
    scripts = _scripts_dict(ctx)
    cmds = _as_cmdinfo_list(scripts.get("lint")) + _as_cmdinfo_list(scripts.get("format"))
    cmds = _dedupe_cmds(cmds)
    return [_format_cmd(c) for c in cmds] if cmds else [NO_COMMANDS]


def _analyzer_notes_lines(ctx: Context) -> list[str]:
    notes = ctx.analyze.get("notes")
    notebooks = ctx.analyze.get("notebooks")
    frameworks = ctx.analyze.get("frameworks")

    out: list[str] = []
    note_strs: list[str] = []

    if isinstance(notes, list):
        for n in notes:
            if isinstance(n, str) and n.strip():
                s = n.strip()
                note_strs.append(s)
                # sanitize notes lightly (ASCII + whitespace) to avoid stray garbage
                cleaned = "".join(ch for ch in s if 32 <= ord(ch) < 127)
                cleaned = " ".join(cleaned.split()).strip()
                if cleaned and "source:" not in cleaned and "evidence:" not in cleaned:
                    out.append(f"{BULLET}{cleaned}")

    nb_dirs: list[str] = []
    if isinstance(notebooks, list):
        for d in notebooks:
            if isinstance(d, str) and d.strip():
                dd = d.strip()
                if dd == ".":
                    dd = "./"
                elif not dd.endswith("/"):
                    dd += "/"
                nb_dirs.append(dd)

    if nb_dirs:
        if NOTEBOOK_CENTRIC not in note_strs:
            out.append(f"{BULLET}{NOTEBOOK_CENTRIC}")
        out.append(f"{BULLET}Notebooks found in: {', '.join(nb_dirs)}")

    fw: list[dict[str, Any]] = []
    if isinstance(frameworks, list):
        for f in frameworks:
            if isinstance(f, dict) and isinstance(f.get("name"), str) and f["name"].strip():
                fw.append(f)

    if fw:
        names = ", ".join(f["name"].strip() for f in fw) + "."
        reasons: list[str] = []
        for f in fw:
            dr = f.get("detectionReason")
            if isinstance(dr, str) and dr.strip():
                reasons.append(dr)
        line = f"{BULLET}Frameworks detected (from analyzer): {names}"
        if len(fw) == 1 and reasons:
            r = _sanitize_desc(str(reasons[0]))  # already ends with exactly one period
            if r:
                line += f" ({r})"
        elif len(fw) > 1 and reasons:
            r0 = str(reasons[0]).strip()
            if all(str(r).strip() == r0 for r in reasons):
                r = _sanitize_desc(r0)
                if r:
                    line += f" ({r})"
        out.append(line)

    return out


def _dep_lines(ctx: Context) -> list[str]:
    py = _python_dict(ctx)
    dep_files = py.get("dependencyFiles")
    if not isinstance(dep_files, list) or not dep_files:
        return [NO_DEPS]

    lines: list[str] = []
    seen: set[str] = set()
    for f in dep_files:
        if not isinstance(f, dict):
            continue
        path = f.get("path")
        if not isinstance(path, str) or not path.strip():
            continue
        p = path.strip()
        if p in seen:
            continue
        seen.add(p)

        desc = f.get("description")
        if isinstance(desc, str) and desc.strip():
            d = _sanitize_desc(desc)
            lines.append(f"{BULLET}{p} ({d})" if d else f"{BULLET}{p}")
        else:
            lines.append(f"{BULLET}{p}")

    return lines or [NO_DEPS]


def _config_lines(ctx: Context) -> list[str]:
    cfgs = ctx.analyze.get("configurationFiles")
    if not isinstance(cfgs, list) or not cfgs:
        return [NO_CONFIG]

    lines: list[str] = []
    seen: set[str] = set()
    for f in cfgs:
        if not isinstance(f, dict):
            continue
        path = f.get("path")
        if not isinstance(path, str) or not path.strip():
            continue
        p = path.strip()
        if p in seen:
            continue
        seen.add(p)

        desc = f.get("description")
        if isinstance(desc, str) and desc.strip():
            d = _sanitize_desc(desc)
            lines.append(f"{BULLET}{p} ({d})" if d else f"{BULLET}{p}")
        else:
            lines.append(f"{BULLET}{p}")

    return lines or [NO_CONFIG]


def _docs_lines(ctx: Context) -> list[str]:
    docs = ctx.analyze.get("docs")
    if not isinstance(docs, list) or not docs:
        return [NO_DOCS]

    lines: list[str] = []
    seen: set[str] = set()
    for d in docs:
        if not isinstance(d, dict):
            continue
        path = d.get("path")
        if not isinstance(path, str) or not path.strip():
            continue
        p = path.strip()
        if p in seen:
            continue
        seen.add(p)
        lines.append(f"{BULLET}{p}")

    return lines or [NO_DOCS]


def get_section_registry() -> list[SectionSpec]:
    """Return ordered list of section specifications.

    Order MUST match reference v2 exactly for output consistency.
    """
    return [
        SectionSpec("title", "# ONBOARDING.md", build_title_section),
        SectionSpec("overview", "## Overview", build_overview_section),
        SectionSpec("env_setup", "## Environment setup", build_env_setup_section),
        SectionSpec("install", "## Install dependencies", build_install_section),
        SectionSpec("run_local", "## Run / develop locally", build_run_local_section),
        SectionSpec("run_tests", "## Run tests", build_run_tests_section),
        SectionSpec("lint_format", "## Lint / format", build_lint_format_section),
        SectionSpec("analyzer_notes", "## Analyzer notes", build_analyzer_notes_section),
        SectionSpec("deps", "## Dependency files detected", build_deps_section),
        SectionSpec("config", "## Useful configuration files", build_config_section),
        SectionSpec("docs", "## Useful docs", build_docs_section),
    ]
