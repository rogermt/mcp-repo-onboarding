from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

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
class Context:
    analyze: dict[str, Any]
    commands: dict[str, Any]


def build_context(analyze: dict[str, Any], commands: dict[str, Any]) -> Context:
    return Context(analyze=analyze or {}, commands=commands or {})


def compile_blueprint_v2(ctx: Context) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []

    sections.append(_sec("title", "# ONBOARDING.md", []))
    sections.append(_sec("overview", "## Overview", [f"Repo path: {_repo_path(ctx)}"]))
    sections.append(_sec("env_setup", "## Environment setup", _env_setup_lines(ctx)))
    sections.append(_sec("install", "## Install dependencies", _install_lines(ctx)))
    sections.append(_sec("run_local", "## Run / develop locally", _dev_lines(ctx)))
    sections.append(_sec("run_tests", "## Run tests", _test_lines(ctx)))
    sections.append(_sec("lint_format", "## Lint / format", _lint_format_lines(ctx)))

    notes = _analyzer_notes_lines(ctx)
    if notes:
        sections.append(_sec("analyzer_notes", "## Analyzer notes", notes))

    sections.append(_sec("deps", "## Dependency files detected", _dep_lines(ctx)))
    sections.append(_sec("config", "## Useful configuration files", _config_lines(ctx)))
    sections.append(_sec("docs", "## Useful docs", _docs_lines(ctx)))

    blueprint: dict[str, Any] = {
        "format": "onboarding_blueprint_v2",
        "render": {"mode": "verbatim", "markdown": ""},
        "sections": sections,
    }

    blueprint["render"]["markdown"] = render_blueprint_to_markdown(blueprint)
    return blueprint


def render_blueprint_to_markdown(blueprint: dict[str, Any]) -> str:
    secs = blueprint.get("sections")
    if not isinstance(secs, list):
        return ""

    blocks: list[str] = []
    for sec in secs:
        if not isinstance(sec, dict):
            continue

        heading = sec.get("heading")
        if not isinstance(heading, str) or not heading.strip():
            continue

        lines = sec.get("lines")
        if not isinstance(lines, list):
            lines = []

        clean_lines: list[str] = []
        for ln in lines:
            if isinstance(ln, str):
                clean_lines.append(ln.rstrip())
            else:
                clean_lines.append(str(ln).rstrip())

        block = heading.rstrip()
        if clean_lines:
            block += "\n" + "\n".join(clean_lines)
        blocks.append(block)

    out = "\n\n".join(blocks).rstrip()
    return (out + "\n") if out else ""


def _sec(section_id: str, heading: str, lines: list[str]) -> dict[str, Any]:
    return {"id": section_id, "heading": heading, "lines": lines}


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
    cleaned = "".join(ch for ch in desc if 32 <= ord(ch) < 127)
    cleaned = " ".join(cleaned.split()).strip()

    # remove provenance markers defensively
    cleaned = cleaned.replace("source:", "").replace("evidence:", "")
    cleaned = " ".join(cleaned.split()).strip()

    if not cleaned:
        return ""

    return _ensure_single_trailing_period(cleaned)


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


def _desc_for(cmd: str, candidates: list[dict[str, Any]]) -> str | None:
    for c in candidates:
        if (c.get("command") or "").strip() == cmd:
            d = c.get("description")
            if isinstance(d, str) and d.strip():
                return d.strip()
    return None


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


def _first_index_matching(lines: list[str], markers: Iterable[str]) -> int | None:
    for i, ln in enumerate(lines):
        for m in markers:
            if m in ln:
                return i
    return None
