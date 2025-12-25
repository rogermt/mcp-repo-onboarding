import logging
from pathlib import Path
from typing import Any

from ..config import (
    DEFAULT_MAX_FILES,
    DEPENDENCY_FILE_TYPES,
    DOC_EXCLUDED_EXTENSIONS,
    DOC_HUMAN_EXTENSIONS,
    MAX_CONFIG_CAP,
    MAX_DOCS_CAP,
    SAFETY_IGNORES,
)
from ..describers import FILE_DESCRIBER_REGISTRY
from ..schema import (
    ConfigFileInfo,
    DocInfo,
    ProjectLayout,
    PythonEnvFile,
    PythonInfo,
    RepoAnalysis,
    RepoAnalysisScriptGroup,
    TestSetup,
)
from .extractors import (
    detect_workflow_python_version,
    extract_makefile_commands,
    extract_pyproject_metadata,
    extract_shell_scripts,
    extract_tox_commands,
)
from .prioritization import get_config_priority, get_doc_priority
from .scanning import scan_repo_files
from .structs import IgnoreMatcher
from .utils import classify_python_version

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


def _perform_targeted_scan(root: Path, safety_ignores: list[str]) -> list[str]:
    targeted_files = []
    # Targeted scan should bypass .gitignore but respect safety ignores
    safety_only_ignore = IgnoreMatcher(
        repo_root=root, safety_ignores=safety_ignores, gitignore_patterns=[]
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


def _categorize_files(
    all_files: list[str],
) -> tuple[list[DocInfo], list[ConfigFileInfo], list[PythonEnvFile], list[str]]:
    docs = []
    configs = []
    dep_files = []
    notes: list[str] = []

    for f_path in all_files:
        name = f_path.split("/")[-1].lower() if "/" in f_path else f_path.lower()

        # Docs
        is_doc_candidate = (
            name.startswith("readme")
            or name.startswith("contributing")
            or f_path.startswith("docs/")
        )

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
        is_dep = False
        if name in DEPENDENCY_FILE_TYPES or (
            name.startswith("requirements") and name.endswith((".txt", ".in"))
        ):
            desc_key = "requirements.txt" if name.startswith("requirements") else name
            dep_describer = FILE_DESCRIBER_REGISTRY.get(desc_key)
            dep_file = PythonEnvFile(path=f_path, type=name)
            if dep_describer:
                dep_file = dep_describer.describe(dep_file)
            dep_files.append(dep_file)
            is_dep = True

        # Config Files (Only if not already a dependency)
        if is_dep:
            continue

        is_workflow = f_path.startswith(".github/workflows/")
        describer = FILE_DESCRIBER_REGISTRY.get(name) or (
            FILE_DESCRIBER_REGISTRY.get(".github/workflows") if is_workflow else None
        )

        if describer or name in ["pytest.ini", "pytest.cfg"]:
            if not (name.startswith("requirements") and name.endswith((".txt", ".in"))):
                config_file = ConfigFileInfo(path=f_path, type=name)
                if describer:
                    config_file = describer.describe(config_file)
                configs.append(config_file)

    return docs, configs, dep_files, notes


def _prioritize_and_cap(
    docs: list[DocInfo], configs: list[ConfigFileInfo]
) -> tuple[list[DocInfo], list[ConfigFileInfo], list[str]]:
    notes = []
    docs.sort(key=lambda x: get_doc_priority(x.path), reverse=True)
    if len(docs) > MAX_DOCS_CAP:
        notes.append(f"docs list truncated to {MAX_DOCS_CAP} entries (total={len(docs)})")
        docs = docs[:MAX_DOCS_CAP]

    configs.sort(key=lambda x: get_config_priority(x.path), reverse=True)
    if len(configs) > MAX_CONFIG_CAP:
        notes.append(
            f"configurationFiles list truncated to {MAX_CONFIG_CAP} entries (total={len(configs)})"
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

        if "pip" in package_managers:
            reqs = [d.path for d in dep_files if d.path.startswith("requirements")]
            if reqs:
                main_req = next((r for r in reqs if r == "requirements.txt"), reqs[0])
                install_instructions.append(f"pip install -r {main_req}")

        if any(Path(d.path).name.lower() == "setup.py" for d in dep_files):
            install_instructions.append("pip install -e .")
        elif any(Path(d.path).name.lower() == "pyproject.toml" for d in dep_files):
            install_instructions.append("pip install .")

        # Process version hints
        final_pin = None
        comments = []

        all_hints = sorted(
            set(
                workflow_versions
                + (
                    [pyproject_metadata["python_version"]]
                    if pyproject_metadata["python_version"]
                    else []
                )
            )
        )

        for hint in all_hints:
            pin, comment = classify_python_version(hint)
            if pin and not final_pin:
                final_pin = pin
            if comment:
                comments.append(comment)

        python_info = PythonInfo(
            packageManagers=package_managers,
            dependencyFiles=dep_files,
            envSetupInstructions=env_setup_instructions,
            installInstructions=install_instructions,
            pythonVersionHints=all_hints,
            pythonVersionPin=final_pin,
            pythonVersionComments=", ".join(comments) if comments else None,
        )

        python_info.dependencyFiles.sort(key=lambda d: 0 if d.path == "requirements.txt" else 1)
        return python_info

    return None


def analyze_repo(repo_path: str, max_files: int = DEFAULT_MAX_FILES) -> RepoAnalysis:
    """
    Analyze the repository and return a structured report.

    Args:
        repo_path: Path to the repository to analyze.
        max_files: Maximum files to scan (default: DEFAULT_MAX_FILES).

    Returns:
        RepoAnalysis object containing collected metadata.
    """
    root = Path(repo_path).resolve()

    ignore = _setup_ignore_matcher(root)

    # 1. Targeted scan
    targeted_files = _perform_targeted_scan(root, SAFETY_IGNORES)

    # 2. Broad scan
    all_other_files, py_files = scan_repo_files(root, ignore, max_files)

    # 3. Combine
    all_files = sorted(set(all_other_files + targeted_files))

    # 4. Categorize
    docs, configs, dep_files, cat_notes = _categorize_files(all_files)

    # 5. Prioritize & Cap
    docs, configs, cap_notes = _prioritize_and_cap(docs, configs)
    notes = cat_notes + cap_notes

    # 6. Extract Scripts
    scripts = _aggregate_scripts(root, configs, all_files)

    # 7. Infer Python Env
    python_info = _infer_python_environment(root, py_files, dep_files)

    logger.info(f"Analyzed repo at {root}: {len(all_files)} files found.")

    return RepoAnalysis(
        repoPath=str(root),
        docs=docs,
        configurationFiles=configs,
        scripts=scripts,
        notes=notes,
        python=python_info,
        projectLayout=ProjectLayout(),
        testSetup=TestSetup(),
    )
