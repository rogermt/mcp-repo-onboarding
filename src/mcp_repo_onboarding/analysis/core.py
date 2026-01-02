import logging
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..config import (
    CONFIG_FILE_TYPES,
    DEFAULT_MAX_FILES,
    DOC_EXCLUDED_EXTENSIONS,
    DOC_HUMAN_EXTENSIONS,
    MAX_CONFIG_CAP,
    MAX_DOCS_CAP,
    SAFETY_IGNORES,
)
from ..describers import FILE_DESCRIBER_REGISTRY
from ..effective_config import EffectiveConfig
from ..schema import (
    ConfigFileInfo,
    DocInfo,
    ProjectLayout,
    PythonEnvFile,
    PythonInfo,
    RepoAnalysis,
    RepoAnalysisScriptGroup,
    TestSetup,
    ToolingEvidence,
)
from .catalog import is_dependency_file
from .extractors import (
    detect_workflow_python_version,
    extract_makefile_commands,
    extract_pyproject_metadata,
    extract_shell_scripts,
    extract_tox_commands,
)
from .frameworks import detect_frameworks_from_pyproject
from .install_commands import merge_python_install_instructions_into_scripts
from .notebook_hygiene import precommit_has_notebook_hygiene
from .prioritization import get_config_priority, get_dep_priority, get_doc_priority
from .scanning import scan_repo_files
from .structs import IgnoreMatcher
from .tooling import detect_other_tooling

logger = logging.getLogger(__name__)


def _setup_ignore_matcher(root: Path) -> IgnoreMatcher:
    gitignore_patterns = []
    gitignore = root / ".gitignore"
    if gitignore.is_file():
        try:
            with open(gitignore, encoding="utf-8") as f:
                gitignore_patterns.extend(f.readlines())
        except OSError as e:
            logger.warning(f"Failed to read .gitignore at {gitignore}: {e}")
            pass

    return IgnoreMatcher(
        repo_root=root,
        safety_ignores=SAFETY_IGNORES,
        gitignore_patterns=gitignore_patterns,
    )


def _perform_targeted_scan(root: Path, safety_ignores: list[str] | tuple[str, ...]) -> list[str]:
    targeted_files = []
    # Targeted scan should bypass .gitignore but respect safety ignores
    safety_only_ignore = IgnoreMatcher(
        repo_root=root, safety_ignores=list(safety_ignores), gitignore_patterns=[]
    )

    for pattern in [
        "pyproject.toml",
        "tox.ini",
        "noxfile.py",
        "setup.py",
        "setup.cfg",
        "Makefile",
        ".pre-commit-config.yaml",
    ]:
        p = root / pattern
        if p.is_file() and not safety_only_ignore.should_ignore(p):
            targeted_files.append(p.name)

    for pattern in ["requirements*.txt", ".github/workflows/*.yml"]:
        for p in root.glob(pattern):
            if p.is_file() and not safety_only_ignore.should_ignore(p):
                targeted_files.append(str(p.relative_to(root)))
    return targeted_files


def _is_workflow_file(rel_path: str) -> bool:
    """
    GitHub Actions workflow file detection (repo-relative POSIX path).
    """
    p = rel_path.replace("\\", "/")
    if not p.startswith(".github/workflows/"):
        return False
    lower = p.lower()
    return lower.endswith(".yml") or lower.endswith(".yaml")


def _categorize_files(
    root: Path,
    all_files: list[str],
) -> tuple[list[DocInfo], list[ConfigFileInfo], list[PythonEnvFile], list[str]]:
    docs = []
    configs = []
    dep_files = []
    notes: list[str] = []

    for f_path in all_files:
        # f_path is expected to be repo-relative with "/" separators, but normalize defensively.
        f_path = f_path.replace("\\", "/").lstrip("/")
        name = Path(f_path).name.lower()

        # Docs
        is_doc_candidate = name.startswith(
            ("readme", "contributing", "license", "security")
        ) or f_path.startswith("docs/")

        if is_doc_candidate:
            suffix = Path(f_path).suffix.lower()

            # Exception: Always include top-level README/CONTRIBUTING regardless of extension
            is_top_level_readme = (
                name.startswith("readme") or name.startswith("contributing")
            ) and "/" not in f_path

            if not is_top_level_readme:
                # Rule A: Exclude binary/asset extensions entirely
                if suffix in DOC_EXCLUDED_EXTENSIONS:
                    continue

                # Rule B: Specific allowlist under docs/
                if f_path.startswith("docs/"):
                    if suffix not in DOC_HUMAN_EXTENSIONS:
                        continue

            docs.append(DocInfo(path=f_path, type="doc"))
            continue

        # Dependencies
        is_dep = is_dependency_file(f_path)
        if is_dep:
            desc_key = "requirements.txt" if name.startswith("requirements") else name
            dep_describer = FILE_DESCRIBER_REGISTRY.get(desc_key)
            dep_file = PythonEnvFile(path=f_path, type=name)
            if dep_describer:
                dep_file = dep_describer.describe(dep_file)
            dep_files.append(dep_file)
            continue

        # Config files (classification MUST NOT depend on describer presence)
        is_workflow = _is_workflow_file(f_path)
        is_named_config = name in CONFIG_FILE_TYPES

        if is_workflow or is_named_config:
            config_file = ConfigFileInfo(path=f_path, type=name)

            # Enrichment only (optional descriptions)
            describer = None
            if is_workflow:
                describer = FILE_DESCRIBER_REGISTRY.get(".github/workflows")
            else:
                describer = FILE_DESCRIBER_REGISTRY.get(name)

            if describer:
                config_file = describer.describe(config_file)

            # P7-02: Notebook hygiene detection in pre-commit config
            # Acceptance: if nbstripout/nb-clean/jupyter-notebook-cleanup is found,
            # override the description with the required text.
            if name in (".pre-commit-config.yaml", ".pre-commit-config.yml"):
                if precommit_has_notebook_hygiene(root, f_path):
                    config_file.description = "Pre-commit config for cleaning Jupyter notebooks (e.g. stripping outputs) for cleaner diffs."

            configs.append(config_file)

    # Sort dependency files deterministically
    dep_files.sort(key=lambda x: (-get_dep_priority(x.path), x.path))

    return docs, configs, dep_files, notes


def sort_by_score_then_path(items: list[Any], score_fn: Callable[[str], int]) -> list[Any]:
    """Sort items by score (descending) then path (ascending)."""
    return sorted(items, key=lambda x: (-score_fn(x.path), x.path))


def _prioritize_and_cap(
    docs: list[DocInfo], configs: list[ConfigFileInfo]
) -> tuple[list[DocInfo], list[ConfigFileInfo], list[str]]:
    notes = []
    docs = sort_by_score_then_path(docs, get_doc_priority)
    if len(docs) > MAX_DOCS_CAP:
        total = len(docs)
        notes.append(f"docs list truncated to {MAX_DOCS_CAP} entries (total={total})")
        docs = docs[:MAX_DOCS_CAP]

    configs = sort_by_score_then_path(configs, get_config_priority)
    if len(configs) > MAX_CONFIG_CAP:
        total = len(configs)
        notes.append(
            f"configurationFiles list truncated to {MAX_CONFIG_CAP} entries (total={total})"
        )
        configs = configs[:MAX_CONFIG_CAP]
    return docs, configs, notes


def _aggregate_scripts(
    root: Path, configs: list[ConfigFileInfo], all_files: list[str]
) -> RepoAnalysisScriptGroup:
    scripts = RepoAnalysisScriptGroup()
    makefile = next((c.path for c in configs if Path(c.path).name.lower() == "makefile"), None)
    if makefile:
        mk_cmds = extract_makefile_commands(root, makefile)
        for category, cmd_list in mk_cmds.items():
            if category in RepoAnalysisScriptGroup.model_fields:
                getattr(scripts, category).extend(cmd_list)

    sh_cmds = extract_shell_scripts(all_files, root)
    scripts.dev.extend(sh_cmds["dev"])
    scripts.test.extend(sh_cmds["test"])

    tox_ini = next((c.path for c in configs if Path(c.path).name.lower() == "tox.ini"), None)
    if tox_ini:
        tox_cmds = extract_tox_commands(root, tox_ini)
        scripts.test.extend(tox_cmds["test"])
        scripts.lint.extend(tox_cmds["lint"])

    return scripts


def _infer_python_environment(
    root: Path, py_files: list[str], dep_files: list[PythonEnvFile]
) -> PythonInfo | None:
    # 1. GitHub Workflows
    workflow_versions = detect_workflow_python_version(root)

    # 2. pyproject.toml (tomllib)
    pyproject_metadata: dict[str, Any] = {
        "python_version": None,
        "package_managers": [],
        "build_backend": None,
    }
    pyproject_file = next(
        (d.path for d in dep_files if Path(d.path).name == "pyproject.toml"), None
    )
    if pyproject_file:
        pyproject_metadata = extract_pyproject_metadata(root, pyproject_file)

    has_python_files = bool(py_files)
    has_dep_files = bool(dep_files)

    if (
        has_python_files
        or has_dep_files
        or workflow_versions
        or pyproject_metadata["python_version"]
    ):
        package_managers: list[str] = list(pyproject_metadata["package_managers"])
        if any(d.path.startswith("requirements") for d in dep_files) or any(
            Path(d.path).name.lower() in ["setup.py", "setup.cfg", "pyproject.toml"]
            for d in dep_files
        ):
            if "pip" not in package_managers:
                package_managers.append("pip")

        env_setup_instructions: list[str] = []
        install_instructions = []

        has_pyproject = any(Path(d.path).name.lower() == "pyproject.toml" for d in dep_files)
        has_setup_py = any(Path(d.path).name.lower() == "setup.py" for d in dep_files)

        if has_pyproject:
            install_instructions.append("pip install .")
        elif has_setup_py:
            install_instructions.append("pip install -e .")
        elif "pip" in package_managers:
            reqs = [d.path for d in dep_files if d.path.startswith("requirements")]
            if reqs:
                main_req = next((r for r in reqs if r == "requirements.txt"), reqs[0])
                install_instructions.append(f"pip install -r {main_req}")

        raw_hints = sorted(
            set(
                workflow_versions
                + (
                    [pyproject_metadata["python_version"]]
                    if pyproject_metadata["python_version"]
                    else []
                )
            )
        )
        python_version_hints = [v for v in raw_hints if _is_exact_version(v)]

        python_info = PythonInfo(
            packageManagers=package_managers,
            dependencyFiles=dep_files,
            envSetupInstructions=env_setup_instructions,
            installInstructions=install_instructions,
            pythonVersionHints=python_version_hints,
        )

        python_info.dependencyFiles.sort(
            key=lambda d: (
                0 if d.path == "requirements.txt" else 1,  # pin requirements.txt first
                -get_dep_priority(d.path),  # then follow normal dependency ranking
                d.path,  # then tie-break by path
            )
        )
        return python_info

    return None


def analyze_repo(
    repo_path: str,
    max_files: int = DEFAULT_MAX_FILES,
    effective_config: EffectiveConfig | None = None,
) -> RepoAnalysis:
    """
    Analyze the repository and return a structured report.

    Args:
        repo_path: Path to the repository to analyze.
        max_files: Maximum files to scan (default: DEFAULT_MAX_FILES).
        effective_config: Config overrides (default: None uses defaults).

    Returns:
        RepoAnalysis object containing collected metadata.
    """
    if effective_config is None:
        effective_config = EffectiveConfig()

    root = Path(repo_path).resolve()

    ignore = _setup_ignore_matcher(root)

    # 1. Targeted scan
    targeted_files = _perform_targeted_scan(root, effective_config.safety_ignores)

    # 2. Broad scan
    all_other_files, py_files = scan_repo_files(root, ignore, max_files)

    # 3. Combine
    all_files = sorted(set(all_other_files + targeted_files))

    # 4. Categorize
    docs, configs, dep_files, cat_notes = _categorize_files(root, all_files)

    # 5. Prioritize & Cap
    docs, configs, cap_notes = _prioritize_and_cap(docs, configs)
    notes = cat_notes + cap_notes

    # 6. Extract Scripts
    scripts = _aggregate_scripts(root, configs, all_files)

    # Framework detection (cheap, deterministic): pyproject classifiers
    frameworks = detect_frameworks_from_pyproject(root)

    # 7. Infer Python Env
    python_info = _infer_python_environment(root, py_files, dep_files)

    # NEW: mirror python.installInstructions into scripts.install with descriptions
    merge_python_install_instructions_into_scripts(scripts, python_info)

    # 8. Notebook Detection (P7-01 / Issue #60)
    notebook_dirs = set()
    for f_path in all_files:
        if f_path.lower().endswith(".ipynb"):
            # If at root, use '.', otherwise parent directory
            rel_dir = str(Path(f_path).parent)
            if rel_dir == ".":
                notebook_dirs.add(".")
            else:
                posix_dir = rel_dir.replace("\\", "/")
                # Ensure trailing slash for directories
                if not posix_dir.endswith("/"):
                    posix_dir += "/"
                notebook_dirs.add(posix_dir)

    notebooks_field = sorted(notebook_dirs)
    if notebooks_field:
        notes.append("Notebook-centric repo detected; core logic may reside in Jupyter notebooks.")

    # 9. Other tooling detection (Phase 8 - #81)
    other_tooling_detections = detect_other_tooling(all_files)
    other_tooling = [
        ToolingEvidence(
            name=d.name,
            evidenceFiles=list(d.evidence_files),
            note=d.note,
        )
        for d in other_tooling_detections
    ]

    logger.info(f"Analyzed repo at {root}: {len(all_files)} files found.")

    return RepoAnalysis(
        repoPath=str(root),
        docs=docs,
        configurationFiles=configs,
        scripts=scripts,
        frameworks=frameworks,
        notes=notes,
        python=python_info,
        notebooks=notebooks_field,
        projectLayout=ProjectLayout(),
        testSetup=TestSetup(),
        otherTooling=other_tooling,
    )


def _is_exact_version(v: str) -> bool:
    """
    Check if a version string is an exact version (X.Y or X.Y.Z) and not a range.
    Matches digits only separated by dots.
    """
    if not v:
        return False
    return bool(re.match(r"^\d+\.\d+(\.\d+)?$", v))
