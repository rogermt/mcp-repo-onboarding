"""
Blueprint section registry.

Contains all section builders (copied verbatim from v2).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ...config import MAX_EVIDENCE_FILES_DISPLAYED
from .context import Context
from .specs import SectionSpec

# Constants (copied from v2)
BULLET = "* "

NO_COMMANDS = "No explicit commands detected."
NO_DEPS = "No dependency files detected."
NO_CONFIG = "No useful configuration files detected."
NO_DOCS = "No useful docs detected."

NOTEBOOK_CENTRIC = "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."

# Phase 9: Python-only scope note
PYTHON_ONLY_SCOPE_NOTE = (
    "Python tooling not detected; this release generates Python-focused onboarding only."
)

# How many notebook directories to print in ONBOARDING.md (deterministic cap).
MAX_NOTEBOOK_DIRS = 20

GENERIC_LABEL = "(Generic suggestion)"
GENERIC_VENV_LINES = [
    GENERIC_LABEL,
    f"{BULLET}`python3 -m venv .venv` (Create virtual environment.)",
    f"{BULLET}`source .venv/bin/activate` (Activate virtual environment.)",
]

VENV_MARKERS = ("python -m venv .venv", "python3 -m venv .venv")


# Helper functions (copied from v2, verbatim)


def _repo_path(ctx: Context) -> str:
    rp = ctx.analyze.get("repoPath")
    return rp if isinstance(rp, str) and rp.strip() else "."


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
    cleaned = "".join(ch for ch in desc if 32 <= ord(ch) < 127)  # noqa: PLR2004
    cleaned = " ".join(cleaned.split()).strip()

    # remove provenance markers defensively
    cleaned = cleaned.replace("source:", "").replace("evidence:", "")
    cleaned = " ".join(cleaned.split()).strip()

    if not cleaned:
        return ""

    return _ensure_single_trailing_period(cleaned)


def _format_cmd(c: dict[str, Any]) -> str:
    cmd = (c.get("command") or "").strip()

    desc = c.get("description")
    if not isinstance(desc, str) or not desc.strip():
        desc = "No description provided by analyzer."
    desc_clean = _sanitize_desc(desc) or "No description provided by analyzer."

    return f"{BULLET}`{cmd}` ({desc_clean})"


def _first_index_matching(lines: list[str], markers: Iterable[str]) -> int | None:
    for i, ln in enumerate(lines):
        for m in markers:
            if m in ln:
                return i
    return None


def _desc_for(cmd: str, candidates: list[dict[str, Any]]) -> str | None:
    for c in candidates:
        if (c.get("command") or "").strip() == cmd:
            d = c.get("description")
            if isinstance(d, str) and d.strip():
                return d.strip()
    return None


def _normalize_env_instruction(s: str) -> str:
    st = s.strip()
    if st.startswith(("* ", "- ")):
        st = st[2:].strip()
    if st.startswith("`") and st.endswith("`"):
        return st
    return f"`{st}`"


def _python_evidence_present(ctx: Context) -> bool:
    py = ctx.analyze.get("python")
    if not isinstance(py, dict):
        return False

    # Treat an empty python dict as "not detected"
    for k in (
        "dependencyFiles",
        "pythonVersionHints",
        "installInstructions",
        "envSetupInstructions",
        "packageManagers",
    ):
        v = py.get(k)
        if isinstance(v, list) and len(v) > 0:
            return True

    return False


def _primary_tooling(ctx: Context) -> str | None:
    """Get the primaryTooling field from the analyze dict."""
    pt = ctx.analyze.get("primaryTooling")
    return pt if isinstance(pt, str) and pt.strip() else None


def _node_version_pin_line(ctx: Context) -> str:  # noqa: C901
    """
    Evidence-only Node version pin messaging.
    Grounded in presence of .nvmrc / .node-version (no file reads).
    """
    tooling = ctx.analyze.get("otherTooling")
    evidence_paths: list[str] = []

    if isinstance(tooling, list):
        for t in tooling:
            if not isinstance(t, dict):
                continue
            name = t.get("name")
            if not isinstance(name, str) or name.strip() != "Node.js":
                continue
            ev = t.get("evidenceFiles")
            if isinstance(ev, list):
                for p in ev:
                    if isinstance(p, str) and p.strip():
                        evidence_paths.append(p.strip().replace("\\", "/").lstrip("/"))

    basenames = {Path(p).name for p in evidence_paths}

    pins = []
    if ".nvmrc" in basenames:
        pins.append(".nvmrc")
    if ".node-version" in basenames:
        pins.append(".node-version")

    if pins:
        pins_str = ", ".join(pins)  # deterministic order as constructed above
        return f"Node version pin file detected: {pins_str}."
    return "No Node.js version pin file detected."


# Section builders (copied from v2, verbatim)


def _env_setup_lines(ctx: Context) -> list[str]:
    py_obj = ctx.analyze.get("python")
    python_detected = isinstance(py_obj, dict)
    py = _python_dict(ctx)
    hints = [h for h in (py.get("pythonVersionHints") or []) if isinstance(h, str) and h.strip()]
    env_instr = [
        s for s in (py.get("envSetupInstructions") or []) if isinstance(s, str) and s.strip()
    ]

    lines: list[str] = []

    if hints:
        lines.append(f"Python version: {hints[0]}")
    else:
        pt = _primary_tooling(ctx)
        if pt == "Node.js":
            lines.append(_node_version_pin_line(ctx))
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
        # Phase 10: if Python tooling is not detected, do NOT print Python venv snippet.
        if not python_detected:
            return lines

        # Phase 10: If Python evidence is absent and primary tooling is not Python,
        # do NOT emit the generic Python venv snippet (avoids misleading Node-primary repos).
        pt = _primary_tooling(ctx)
        if pt is not None and pt != "Python" and not _python_evidence_present(ctx):
            return lines

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


def _other_tooling_lines(ctx: Context) -> list[str]:
    """
    Build other tooling section lines (Phase 9 - Issue #110, Phase 10 - Issue #146).

    Evidence-only, deterministically sorted, truncated, and suppresses primary tooling.
    """
    tooling = ctx.analyze.get("otherTooling")
    if not isinstance(tooling, list) or not tooling:
        return []

    lines: list[str] = []

    # Phase 10 / Issue #146: Get primary tooling to suppress from this section
    primary = _primary_tooling(ctx)

    # Filter and collect valid tooling items
    valid_tooling: list[dict[str, Any]] = []
    for t in tooling:
        if not isinstance(t, dict):
            continue
        name = t.get("name")
        if not name:
            continue

        # Phase 10: Suppress primary tooling from "Other tooling detected" section
        if primary and name == primary:
            continue

        valid_tooling.append(t)

    # Phase 10: Deterministic sort by tooling name
    valid_tooling.sort(key=lambda x: x.get("name", ""))

    for t in valid_tooling:
        name = t.get("name")  # Known valid from filter above
        evidence = t.get("evidenceFiles", [])

        if evidence:
            # Phase 10: Sort evidence files deterministically (lexicographically)
            sorted_evidence = sorted(evidence)

            # Truncate display
            shown = sorted_evidence[:MAX_EVIDENCE_FILES_DISPLAYED]

            files_str = ", ".join(shown)

            # Append truncation note if needed
            if len(sorted_evidence) > MAX_EVIDENCE_FILES_DISPLAYED:
                files_str += (
                    f"; truncated to {MAX_EVIDENCE_FILES_DISPLAYED} of {len(sorted_evidence)}"
                )

            lines.append(f"{BULLET}{name} ({files_str})")

        else:
            lines.append(f"{BULLET}{name}")

    return lines


def _primary_tooling_value(ctx: Context) -> str | None:
    """Get primaryTooling field, or None if absent/empty."""
    v = ctx.analyze.get("primaryTooling")
    return v.strip() if isinstance(v, str) and v.strip() else None


def _primary_tooling_evidence_summary(ctx: Context, tool: str) -> str | None:  # noqa: C901, PLR0911, PLR0912
    """
    Deterministic evidence summary for the Primary tooling note.

    Examples:
    - Node.js: "package.json present"
    - Python: "pyproject.toml, poetry.lock present"
    """
    tool = tool.strip()

    if tool == "Python":
        py = ctx.analyze.get("python")
        if not isinstance(py, dict):
            return None

        dep_files = py.get("dependencyFiles")
        if not isinstance(dep_files, list) or not dep_files:
            return None

        basenames: list[str] = []
        for f in dep_files:
            if not isinstance(f, dict):
                continue
            p = f.get("path")
            if isinstance(p, str) and p.strip():
                basenames.append(Path(p.strip().replace("\\", "/")).name)

        if not basenames:
            return None

        # Prefer common primary-evidence names in deterministic order
        prefer = [
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
            "requirements.txt",
            "setup.py",
            "setup.cfg",
        ]
        uniq = set(basenames)
        chosen = [n for n in prefer if n in uniq]
        if not chosen:
            chosen = sorted(uniq)

        shown = chosen[:2]
        return f"{', '.join(shown)} present"

    if tool == "Node.js":
        tooling = ctx.analyze.get("otherTooling")
        if not isinstance(tooling, list):
            tooling = ctx.analyze.get("otherToolingDetected")

        evidence_paths: list[str] = []
        if isinstance(tooling, list):
            for t in tooling:
                if not isinstance(t, dict):
                    continue
                n = t.get("name")
                if not isinstance(n, str):
                    continue
                if n.strip().lower() not in ("node.js", "nodejs", "node"):
                    continue

                ev = t.get("evidenceFiles")
                if not isinstance(ev, list):
                    ev = t.get("evidencePaths")

                if isinstance(ev, list):
                    for p in ev:
                        if isinstance(p, str) and p.strip():
                            evidence_paths.append(p.strip().replace("\\", "/"))

        if not evidence_paths:
            return None

        basenames = sorted({Path(p).name for p in evidence_paths})

        prefer = [
            "package.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "package-lock.json",
            "npm-shrinkwrap.json",
            "bun.lockb",
            ".nvmrc",
            ".node-version",
        ]
        chosen = [n for n in prefer if n in basenames]
        if not chosen:
            chosen = basenames

        shown = chosen[:2]
        if len(shown) == 1:
            return f"{shown[0]} present"
        return f"{', '.join(shown)} present"

    return None


def _primary_tooling_note_line(ctx: Context) -> str | None:
    """Generate primary tooling note line, or None if not applicable."""
    tool = _primary_tooling_value(ctx)
    if tool is None:
        return None

    summary = _primary_tooling_evidence_summary(ctx, tool)
    if summary:
        return f"Primary tooling: {tool} ({summary})."
    return f"Primary tooling: {tool}."


def _analyzer_notes_lines(ctx: Context) -> list[str]:  # noqa: C901, PLR0912
    notes = ctx.analyze.get("notes")
    notebooks = ctx.analyze.get("notebooks")
    frameworks = ctx.analyze.get("frameworks")

    out: list[str] = []
    note_strs: list[str] = []

    # Phase 9: Python-only scope message when Python evidence is absent/weak
    # Phase 10 / Issue #149: Do NOT show this note for Node-primary repos
    pt = _primary_tooling_value(ctx)
    if not _python_evidence_present(ctx) and pt != "Node.js":
        out.append(f"{BULLET}{PYTHON_ONLY_SCOPE_NOTE}")

    # Phase 10 / #127: Primary tooling note (deterministic, neutral)
    pt_line = _primary_tooling_note_line(ctx)
    if pt_line:
        out.append(f"{BULLET}{pt_line}")

    if isinstance(notes, list):
        for n in notes:
            if isinstance(n, str) and n.strip():
                s = n.strip()
                note_strs.append(s)
                # sanitize notes lightly (ASCII + whitespace) to avoid stray garbage
                cleaned = "".join(ch for ch in s if 32 <= ord(ch) < 127)  # noqa: PLR2004
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

        total = len(nb_dirs)
        if total > MAX_NOTEBOOK_DIRS:
            out.append(
                f"{BULLET}notebooks list truncated to {MAX_NOTEBOOK_DIRS} entries (total={total})"
            )

        shown = nb_dirs[:MAX_NOTEBOOK_DIRS]
        out.append(f"{BULLET}Notebooks found in: {', '.join(shown)}")

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
    """Get the registry of all sections in order.

    Order matches v2 exactly.
    """
    return [
        SectionSpec(
            section_id="title",
            heading="# ONBOARDING.md",
            order=0,
            build_lines=lambda ctx: [],
        ),
        SectionSpec(
            section_id="overview",
            heading="## Overview",
            order=1,
            build_lines=lambda ctx: [f"Repo path: {_repo_path(ctx)}"],
        ),
        SectionSpec(
            section_id="env_setup",
            heading="## Environment setup",
            order=2,
            build_lines=_env_setup_lines,
        ),
        SectionSpec(
            section_id="install",
            heading="## Install dependencies",
            order=3,
            build_lines=_install_lines,
        ),
        SectionSpec(
            section_id="run_local",
            heading="## Run / develop locally",
            order=4,
            build_lines=_dev_lines,
        ),
        SectionSpec(
            section_id="run_tests",
            heading="## Run tests",
            order=5,
            build_lines=_test_lines,
        ),
        SectionSpec(
            section_id="lint_format",
            heading="## Lint / format",
            order=6,
            build_lines=_lint_format_lines,
        ),
        SectionSpec(
            section_id="other_tooling",
            heading="## Other tooling detected",
            order=7,
            build_lines=_other_tooling_lines,
            include_if=lambda ctx: bool(_other_tooling_lines(ctx)),
        ),
        SectionSpec(
            section_id="analyzer_notes",
            heading="## Analyzer notes",
            order=8,
            build_lines=_analyzer_notes_lines,
            include_if=lambda ctx: bool(_analyzer_notes_lines(ctx)),
        ),
        SectionSpec(
            section_id="deps",
            heading="## Dependency files detected",
            order=9,
            build_lines=_dep_lines,
        ),
        SectionSpec(
            section_id="config",
            heading="## Useful configuration files",
            order=10,
            build_lines=_config_lines,
        ),
        SectionSpec(
            section_id="docs",
            heading="## Useful docs",
            order=11,
            build_lines=_docs_lines,
        ),
    ]
