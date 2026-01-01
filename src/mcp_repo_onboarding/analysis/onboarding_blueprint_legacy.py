from __future__ import annotations

from typing import Any

__all__ = ["build_onboarding_blueprint_v1", "render_blueprint_to_markdown"]

# The ONLY allowed no-commands sentence anywhere in ONBOARDING.md:
_NO_COMMANDS_LINE = "No explicit commands detected."

# Exact fallback sentences required by the prompt:
_DEP_EMPTY_LINE = "No dependency files detected."
_CFG_EMPTY_LINE = "No useful configuration files detected."
_DOCS_EMPTY_LINE = "No useful docs detected."

_NOTEBOOK_CENTRIC_NOTE = (
    "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."
)

_GENERIC_VENV_LABEL = "(Generic suggestion)"
_GENERIC_VENV_SNIPPET = [
    _GENERIC_VENV_LABEL,
    "* `python3 -m venv .venv` (Create virtual environment.)",
    "* `source .venv/bin/activate` (Activate virtual environment.)",
]


def build_onboarding_blueprint_v1(analyze: dict[str, Any]) -> dict[str, Any]:
    """
    Build a deterministic ONBOARDING blueprint from analyze_repo JSON.

    This blueprint is intentionally "render-only": the LLM can output it verbatim.

    Guarantees (matches prompt + validate_onboarding.py):
    - Required headings exist, exact, and ordered (V1).
    - "Repo path: <non-empty>" under Overview (V2).
    - Never outputs "Python version: No Python version pin detected." (V3).
    - Venv snippet labeling rule satisfied if venv commands appear (V4).
    - Command sections: either bullets "* `cmd` (Desc.)" or exact "No explicit commands detected." (V5).
    - Analyzer notes only included if non-empty; bullets only (V6).
    - Max ONE "pip install -r" occurrence in the whole document (V7).
    - No "source:" / "evidence:" substrings (V8).
    """
    repo_path = _safe_str(analyze.get("repoPath")) or "."

    python_raw = analyze.get("python")
    python = python_raw if isinstance(python_raw, dict) else None

    scripts_raw = analyze.get("scripts")
    scripts = scripts_raw if isinstance(scripts_raw, dict) else {}

    notes_raw = analyze.get("notes")
    notes = notes_raw if isinstance(notes_raw, list) else []

    notebooks_raw = analyze.get("notebooks")
    notebooks = notebooks_raw if isinstance(notebooks_raw, list) else []

    frameworks_raw = analyze.get("frameworks")
    frameworks = frameworks_raw if isinstance(frameworks_raw, list) else []

    sections: list[dict[str, Any]] = []

    # Required headings (exact, ordered)
    sections.append(_sec("# ONBOARDING.md", []))

    sections.append(_sec("## Overview", [f"Repo path: {repo_path}"]))

    sections.append(_sec("## Environment setup", _build_environment_setup_lines(python)))

    install_lines = _build_install_lines(python, scripts)
    sections.append(_sec("## Install dependencies", install_lines or [_NO_COMMANDS_LINE]))

    # "Run / develop locally" uses scripts.dev and scripts.start
    dev_lines = _build_command_section_lines(_collect_commands(scripts, keys=["dev", "start"]))
    sections.append(_sec("## Run / develop locally", dev_lines or [_NO_COMMANDS_LINE]))

    test_lines = _build_command_section_lines(_collect_commands(scripts, keys=["test"]))
    sections.append(_sec("## Run tests", test_lines or [_NO_COMMANDS_LINE]))

    # Lint / format combined
    lint_fmt_lines = _build_command_section_lines(
        _collect_commands(scripts, keys=["lint", "format"])
    )
    sections.append(_sec("## Lint / format", lint_fmt_lines or [_NO_COMMANDS_LINE]))

    # Optional Analyzer notes: include only if non-empty, and must be bullets
    analyzer_note_lines = _build_analyzer_notes_lines(notes, notebooks, frameworks)
    if analyzer_note_lines:
        sections.append(_sec("## Analyzer notes", analyzer_note_lines))

    dep_lines = _build_dependency_files_lines(python)
    sections.append(_sec("## Dependency files detected", dep_lines or [_DEP_EMPTY_LINE]))

    cfg_lines = _build_config_files_lines(analyze)
    sections.append(_sec("## Useful configuration files", cfg_lines or [_CFG_EMPTY_LINE]))

    docs_lines = _build_docs_lines(analyze)
    sections.append(_sec("## Useful docs", docs_lines or [_DOCS_EMPTY_LINE]))

    return {"format": "onboarding_blueprint_v1", "sections": sections}


def render_blueprint_to_markdown(blueprint: dict[str, Any]) -> str:
    """
    Deterministic renderer for tests/debug.

    Rendering contract (matches the "Blueprint mode" prompt rule you will add):
    - Print each section.heading exactly
    - Then each line in section.lines exactly
    - Separate sections with exactly one blank line
    """
    sections = blueprint.get("sections")
    if not isinstance(sections, list):
        return ""

    blocks: list[str] = []
    for sec in sections:
        if not isinstance(sec, dict):
            continue

        heading = _safe_str(sec.get("heading"))
        if not heading:
            continue

        lines = sec.get("lines")
        if not isinstance(lines, list):
            lines = []

        clean_lines: list[str] = []
        for ln in lines:
            s = _safe_str(ln)
            if s is None:
                continue
            clean_lines.append(s)

        block = heading if not clean_lines else heading + "\n" + "\n".join(clean_lines)
        blocks.append(block)

    out = "\n\n".join(blocks).rstrip()
    return (out + "\n") if out else ""


# -----------------------------------------------------------------------------
# Internals


def _sec(heading: str, lines: list[str]) -> dict[str, Any]:
    return {"heading": heading, "lines": lines}


def _safe_str(x: Any) -> str | None:
    if x is None:
        return None
    if isinstance(x, str):
        return x.rstrip()
    return str(x).rstrip()


def _build_environment_setup_lines(python: dict[str, Any] | None) -> list[str]:
    """
    Implements mcp_prompt.txt environment rules, with extra hardening for V3.

    V3 hardening:
    - Never allow a "hint" equal to "No Python version pin detected."
    - Never allow a "hint" that begins with "Python version:" to pass through unmodified.
    """
    hints_raw: list[str] = []
    env_instr: list[str] = []

    if python:
        hv = python.get("pythonVersionHints")
        if isinstance(hv, list):
            hints_raw = [h for h in hv if isinstance(h, str) and h.strip()]

        ei = python.get("envSetupInstructions")
        if isinstance(ei, list):
            env_instr = [s.strip() for s in ei if isinstance(s, str) and s.strip()]

    # --- V3 hardening: sanitize hints ---
    hints: list[str] = []
    for h in hints_raw:
        hs = h.strip()

        # If something upstream ever injected the no-pin sentence as a "hint", drop it
        if hs.lower() == "no python version pin detected.":
            continue

        # If upstream ever sent "Python version: X" as a hint, normalize it
        if hs.lower().startswith("python version:"):
            hs = hs.split(":", 1)[1].strip()
            if hs.lower() == "no python version pin detected." or not hs:
                continue

        hints.append(hs)

    lines: list[str] = []

    # First line rule (hard):
    if hints:
        lines.append(f"Python version: {hints[0]}")
    else:
        lines.append("No Python version pin detected.")

    # Case A — explicit instructions exist
    if env_instr:
        bullets = [f"* {s}" for s in env_instr]

        venv_markers = ("python -m venv .venv", "python3 -m venv .venv")
        first_venv_idx = next(
            (i for i, b in enumerate(bullets) if any(m in b for m in venv_markers)),
            None,
        )
        if first_venv_idx is not None:
            bullets.insert(first_venv_idx, _GENERIC_VENV_LABEL)

        lines.extend(bullets)
        return lines

    # Case B — no explicit instructions, no pin
    if not hints:
        lines.extend(_GENERIC_VENV_SNIPPET)
        return lines

    # Case C — pin exists, no explicit instructions
    return lines


def _collect_commands(scripts: dict[str, Any], keys: list[str]) -> list[dict[str, Any]]:
    """
    Collect CommandInfo-like dicts from analyze_repo.scripts.<key> lists.

    Expected items: {"command": "...", "description": "...", ...}
    """
    out: list[dict[str, Any]] = []
    for k in keys:
        items = scripts.get(k)
        if not isinstance(items, list):
            continue
        for it in items:
            if isinstance(it, dict) and isinstance(it.get("command"), str):
                out.append(it)
    return out


def _build_command_section_lines(cmds: list[dict[str, Any]]) -> list[str]:
    """
    Command bullet formatting (V5-friendly):
      * `command` (Brief description.)

    Description policy:
    - if MCP output has a description: use it
    - else: "No description provided by analyzer."
    """
    seen: set[str] = set()
    lines: list[str] = []

    for it in cmds:
        cmd = it.get("command")
        if not isinstance(cmd, str):
            continue
        cmd = cmd.strip()
        if not cmd or cmd in seen:
            continue
        seen.add(cmd)

        desc = it.get("description")
        # Ensure it's a string, defaulting to empty if None
        desc_str = desc if isinstance(desc, str) else ""

        if not desc_str.strip():
            desc_str = "No description provided by analyzer."

        desc_str = _ensure_period(desc_str)

        lines.append(f"* `{cmd}` ({desc_str})")

    return lines


def _build_install_lines(python: dict[str, Any] | None, scripts: dict[str, Any]) -> list[str]:
    """
    Install commands priority (prompt hard rules):
    - Allowed sources:
      - python.installInstructions (strings)
      - scripts.install (CommandInfo list)
    - If "make install" detected as an install command:
      it MUST be the primary and SOLE install command.
    - Enforce max ONE "pip install -r" line in the entire doc (V7) by filtering here.
    """
    install_cmd_infos = _collect_commands(scripts, keys=["install"])

    install_instr_cmds: list[dict[str, Any]] = []
    if python:
        ii = python.get("installInstructions")
        if isinstance(ii, list):
            for s in ii:
                if isinstance(s, str) and s.strip():
                    install_instr_cmds.append({"command": s.strip(), "description": None})

    combined = install_cmd_infos + install_instr_cmds

    make_install = [c for c in combined if _safe_str(c.get("command")) == "make install"]
    if make_install:
        return _build_command_section_lines(make_install[:1])

    pip_install_r_seen = False
    filtered: list[dict[str, Any]] = []
    for c in combined:
        cmd = _safe_str(c.get("command")) or ""
        if "pip install -r" in cmd:
            if pip_install_r_seen:
                continue
            pip_install_r_seen = True
        filtered.append(c)

    return _build_command_section_lines(filtered)


def _build_dependency_files_lines(python: dict[str, Any] | None) -> list[str]:
    """
    - List python.dependencyFiles[*].path as bullets.
    - If description exists, include in parentheses.
    - If empty/missing, caller uses exact fallback "No dependency files detected."
    """
    dep_files = python.get("dependencyFiles") if python else None
    if not isinstance(dep_files, list) or not dep_files:
        return []

    lines: list[str] = []
    for f in dep_files:
        if not isinstance(f, dict):
            continue
        path = _safe_str(f.get("path"))
        if not path:
            continue
        desc = _safe_str(f.get("description"))
        if desc:
            lines.append(f"- {path} ({desc})")
        else:
            lines.append(f"- {path}")
    return lines


def _build_config_files_lines(analyze: dict[str, Any]) -> list[str]:
    cfgs = analyze.get("configurationFiles")
    if not isinstance(cfgs, list) or not cfgs:
        return []

    lines: list[str] = []
    for c in cfgs:
        if not isinstance(c, dict):
            continue
        path = _safe_str(c.get("path"))
        if not path:
            continue
        desc = _safe_str(c.get("description"))
        if desc:
            lines.append(f"- {path} ({desc})")
        else:
            lines.append(f"- {path}")
    return lines


def _build_docs_lines(analyze: dict[str, Any]) -> list[str]:
    docs = analyze.get("docs")
    if not isinstance(docs, list) or not docs:
        return []

    lines: list[str] = []
    for d in docs:
        if not isinstance(d, dict):
            continue
        path = _safe_str(d.get("path"))
        if path:
            lines.append(f"- {path}")
    return lines


def _build_analyzer_notes_lines(
    notes: list[Any], notebooks: list[Any], frameworks: list[Any]
) -> list[str]:
    """
    Analyzer notes (optional) — ordering and formatting (hard rules):
    1) notes verbatim as bullets, same order
    2) notebook bullets if notebooks present:
       - add notebook-centric note (only if not already in notes)
       - "Notebooks found in: <comma-separated directories ending with />"
    3) frameworks bullet LAST (if frameworks exist), template:
       * Frameworks detected (from analyzer): <names>. (<reason>.)
    """
    out: list[str] = []

    # 1) notes verbatim
    note_strs: list[str] = []
    for n in notes:
        if isinstance(n, str) and n.strip():
            note_strs.append(n.strip())
    out.extend([f"* {n}" for n in note_strs])

    # 2) notebooks present?
    nb_dirs: list[str] = []
    for x in notebooks:
        if not isinstance(x, str) or not x.strip():
            continue
        d = x.strip()
        # Ensure dirs end with "/"; map "." => "./"
        if d == ".":
            d = "./"
        elif not d.endswith("/"):
            d = d + "/"
        nb_dirs.append(d)

    if nb_dirs:
        if _NOTEBOOK_CENTRIC_NOTE not in note_strs:
            out.append(f"* {_NOTEBOOK_CENTRIC_NOTE}")
        out.append(f"* Notebooks found in: {', '.join(nb_dirs)}")

    # 3) frameworks bullet LAST
    fw = [f for f in frameworks if isinstance(f, dict) and isinstance(f.get("name"), str)]
    if fw:
        names = [f["name"].strip() for f in fw if f["name"].strip()]
        if names:
            names_joined = ", ".join(names) + "."

            reasons_raw = []
            for f in fw:
                reason = f.get("detectionReason")
                if isinstance(reason, str) and reason.strip():
                    reasons_raw.append(reason)

            reasons = [r.strip() for r in reasons_raw]

            line = f"* Frameworks detected (from analyzer): {names_joined}"

            if len(names) == 1 and reasons:
                line += f" ({_ensure_period(reasons[0])})"
            elif len(names) > 1 and reasons:
                if all(r == reasons[0] for r in reasons):
                    line += f" ({_ensure_period(reasons[0])})"
                # else omit parentheses entirely

            out.append(line)

    return out


def _ensure_period(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    return s if s.endswith(".") else (s + ".")
