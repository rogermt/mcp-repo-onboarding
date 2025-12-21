import os
import re
from pathlib import Path
from typing import List, Tuple
import pathspec

from .schema import (
    RepoAnalysis, RepoAnalysisScriptGroup, CommandInfo, DocInfo, ConfigFileInfo, 
    ProjectLayout, TestSetup, PythonInfo, PythonEnvFile
)

MAX_DOCS_CAP = 10
MAX_CONFIG_CAP = 15

SAFETY_IGNORES = [
    ".git/", ".venv/", "venv/", "env/", "__pycache__/", "node_modules/",
    "site-packages/", "dist/", "build/", ".pytest_cache/", ".mypy_cache/", ".coverage"
]

class IgnoreMatcher:
    def __init__(
        self,
        repo_root: Path,
        safety_ignores: List[str],
        gitignore_patterns: List[str],
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.safety_ignores = [p.rstrip("/") for p in safety_ignores]
        
        if gitignore_patterns:
            self._pathspec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, 
                gitignore_patterns
            )
        else:
            self._pathspec = None

    def should_ignore(self, path: Path, is_dir: bool = False) -> bool:
        try:
            # Normalize to repo-root-relative POSIX style
            resolved_path = path.resolve()
            rel_path = resolved_path.relative_to(self.repo_root)
            rel_path_str = str(rel_path.as_posix())
            
            if is_dir and not rel_path_str.endswith("/"):
                rel_path_str += "/"

            # 1. Safety ignores (always win)
            # Check if any safety ignore pattern is a prefix of the relative path
            for si in self.safety_ignores:
                if f"/{si}/" in f"/{rel_path_str}":
                    return True
                if rel_path_str.startswith(f"{si}/") or rel_path_str == si:
                    return True

            # 2. Repo ignore rules (pathspec)
            if self._pathspec:
                return self._pathspec.match_file(rel_path_str)
            
            return False
        except (ValueError, OSError):
            # Fail closed -> ignore = False (per design: "No exceptions (fail closed -> ignore = False)")
            return False

    def should_descend(self, dir_path: Path) -> bool:
        return not self.should_ignore(dir_path, is_dir=True)

def scan_repo_files(root: Path, ignore: IgnoreMatcher, max_files: int = 5000) -> Tuple[List[str], List[str]]:
    """
    Scans repo files using IgnoreMatcher for pruning.
    Strategy: Scan root dir FIRST (to find config files), then BFS subdirectories.
    """
    all_files: List[str] = []
    py_files: List[str] = []
    
    # 1. Process root directory first
    try:
        with os.scandir(root) as entries:
            dirs_to_visit = []
            for entry in entries:
                entry_path = Path(entry.path)
                
                # Check ignores (file or dir)
                if ignore.should_ignore(entry_path, is_dir=entry.is_dir()):
                    continue
                
                if entry.is_dir():
                    if ignore.should_descend(entry_path):
                        dirs_to_visit.append(entry.path)
                elif entry.is_file():
                    rel_path = entry.name
                    all_files.append(rel_path)
                    if rel_path.endswith(".py"):
                        py_files.append(rel_path)
    except OSError:
        return [], []

    # 2. BFS for subdirectories
    queue = dirs_to_visit
    while queue and len(all_files) < max_files:
        current_dir = queue.pop(0)
        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if len(all_files) >= max_files:
                        break
                    
                    entry_path = Path(entry.path)
                    
                    if ignore.should_ignore(entry_path, is_dir=entry.is_dir()):
                        continue
                        
                    if entry.is_dir():
                        if ignore.should_descend(entry_path):
                            queue.append(entry.path)
                    elif entry.is_file():
                        try:
                            rel_path = str(entry_path.relative_to(root))
                            all_files.append(rel_path)
                            if rel_path.endswith(".py"):
                                py_files.append(rel_path)
                        except ValueError:
                            continue
        except OSError:
            continue
            
    return all_files, py_files

def extract_makefile_commands(root: Path, makefile_path: str) -> dict:
    """Parses Makefile for targets, strictly ignoring recipe lines."""
    commands = {}
    try:
        content = (root / makefile_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}

    target_pattern = re.compile(r"^([a-zA-Z0-9_-]+):")
    common_targets = {"test", "lint", "format", "dev", "run", "start", "check", "install"}
    
    for line in content.splitlines():
        match = target_pattern.match(line)
        if match:
            target = match.group(1)
            if target in common_targets:
                cmd_info = CommandInfo(command=f"make {target}", source=f"{makefile_path}:{target}")
                if target not in commands:
                    commands[target] = []
                commands[target].append(cmd_info)
    return commands

def extract_shell_scripts(all_files: List[str]) -> dict:
    """Finds scripts/*.sh and returns them as commands."""
    commands = {"dev": [], "test": []}
    
    # Filter for scripts/ directory AND .sh extension
    # normalize path separators
    script_files = [f for f in all_files if f.replace('\\', '/').startswith("scripts/") and f.endswith(".sh")]
    
    for script in script_files:
        name = Path(script).name
        cmd = CommandInfo(
            command=f"bash {script}",
            source=script,
            name=name,
            confidence="derived"
        )
        
        if "test" in name:
            commands["test"].append(cmd)
        else:
            commands["dev"].append(cmd)
            
    return commands

def get_config_priority(path: str) -> int:
    name = Path(path).name.lower()
    
    if name == "makefile":
        return 100
    if name in ["pyproject.toml", "setup.cfg", "setup.py"]:
        return 90
    if name in ["tox.ini", "noxfile.py"]:
        return 80
    if name in [".pre-commit-config.yaml", ".pre-commit-config.yml"]:
        return 70
    
    if path.startswith(".github/workflows/") or path.startswith(".github\\workflows\\"):
        ci_keywords = ["ci", "test", "lint", "build", "checker", "integration", "release", "publish", "deploy"]
        if any(k in name for k in ci_keywords):
            return 60
        automation_patterns = ["add-", "labeler", "stale", "lock", "auto-", "project"]
        if any(p in name for p in automation_patterns):
            return 5
        return 20

    return 10

def get_doc_priority(path: str) -> int:
    name = Path(path).name.lower()
    if name.startswith("readme"):
        return 100
    if name.startswith("contributing"):
        return 100
    # TS logic prioritized docs/index and keywords
    if "quickstart" in name or "install" in name or "setup" in name:
        return 80
    return 50

def analyze_repo(repo_path: str, max_files: int = 5000) -> RepoAnalysis:
    root = Path(repo_path).resolve()
    
    # Initialize IgnoreMatcher
    gitignore_patterns = []
    
    gitignore = root / ".gitignore"
    if gitignore.is_file():
        try:
            with open(gitignore, 'r', encoding='utf-8') as f:
                gitignore_patterns.extend(f.readlines())
        except OSError:
            pass

    info_exclude = root / ".git" / "info" / "exclude"
    if info_exclude.is_file():
        try:
            with open(info_exclude, 'r', encoding='utf-8') as f:
                gitignore_patterns.extend(f.readlines())
        except OSError:
            pass

    ignore = IgnoreMatcher(
        repo_root=root,
        safety_ignores=SAFETY_IGNORES,
        gitignore_patterns=gitignore_patterns
    )
    
    # --- Start of new implementation ---

    # 1. Targeted scan for signal files (not blocked by gitignore)
    targeted_files = []
    signal_patterns = [
        "pyproject.toml", "requirements*.txt", "tox.ini", "noxfile.py", 
        "setup.py", "setup.cfg", "Makefile", ".pre-commit-config.yaml", 
        ".github/workflows/*.yml"
    ]
    
    # Safety-only matcher for the targeted scan
    safety_only_ignore = IgnoreMatcher(repo_root=root, safety_ignores=SAFETY_IGNORES, gitignore_patterns=[])

    # Check for specific files at the root
    for pattern in ["pyproject.toml", "tox.ini", "noxfile.py", "setup.py", "setup.cfg", "Makefile", ".pre-commit-config.yaml"]:
        p = root / pattern
        if p.is_file() and not safety_only_ignore.should_ignore(p):
            targeted_files.append(pattern)

    # Glob for requirements files and GH workflows
    for pattern in ["requirements*.txt", ".github/workflows/*.yml"]:
        for p in root.glob(pattern):
            if p.is_file() and not safety_only_ignore.should_ignore(p):
                targeted_files.append(str(p.relative_to(root)))

    # 2. Broad scan for other files (respects gitignore)
    all_other_files, py_files = scan_repo_files(root, ignore, max_files)

    # Combine and unique the file lists
    all_files = sorted(list(set(all_other_files + targeted_files)))
    
    # --- End of new implementation ---
    
    docs = []
    configs = []
    dep_files = []
    
    # Categorize files
    for f in all_files:
        name = Path(f).name.lower()
        
        # Docs
        if name.startswith("readme") or name.startswith("contributing") or f.startswith("docs/"):
            docs.append(DocInfo(path=f, type="doc"))
        
        # Configs
        is_config = False
        if name in ["makefile", "pyproject.toml", "tox.ini", "setup.cfg", "setup.py", "noxfile.py"]:
            is_config = True
        elif name in ["pytest.ini", "pytest.cfg"]:
            is_config = True
        elif name in [".pre-commit-config.yaml", ".pre-commit-config.yml"]:
            is_config = True
        elif f.startswith(".github/workflows/") or f.startswith(".github\\workflows\\"):
            is_config = True
            
        if is_config:
            configs.append(ConfigFileInfo(path=f, type=name))

        # Dependencies
        if name == "pyproject.toml":
            dep_files.append(PythonEnvFile(path=f, type="pyproject"))
        elif name.startswith("requirements") and (name.endswith(".txt") or name.endswith(".in")):
            dep_files.append(PythonEnvFile(path=f, type="requirements"))
        elif name == "setup.py":
            dep_files.append(PythonEnvFile(path=f, type="setup.py"))

    # Prioritize & Cap
    docs.sort(key=lambda x: get_doc_priority(x.path), reverse=True)
    notes = []
    
    if len(docs) > MAX_DOCS_CAP:
        notes.append(f"docs list truncated to {MAX_DOCS_CAP} entries (total={len(docs)})")
        docs = docs[:MAX_DOCS_CAP]

    configs.sort(key=lambda x: get_config_priority(x.path), reverse=True)
    if len(configs) > MAX_CONFIG_CAP:
        notes.append(f"configurationFiles list truncated to {MAX_CONFIG_CAP} entries (total={len(configs)})")
        configs = configs[:MAX_CONFIG_CAP]

    # Extract Commands
    scripts = RepoAnalysisScriptGroup()
    
    # Makefile
    makefile = next((c.path for c in configs if Path(c.path).name.lower() == "makefile"), None)
    if makefile:
        mk_cmds = extract_makefile_commands(root, makefile)
        if "test" in mk_cmds:
            scripts.test.extend(mk_cmds["test"])
        if "lint" in mk_cmds:
            scripts.lint.extend(mk_cmds["lint"])
        if "dev" in mk_cmds:
            scripts.dev.extend(mk_cmds["dev"])
        if "install" in mk_cmds:
            scripts.install.extend(mk_cmds["install"])

    # Shell Scripts
    sh_cmds = extract_shell_scripts(all_files)
    scripts.dev.extend(sh_cmds["dev"])
    scripts.test.extend(sh_cmds["test"])

    # Infer Python Environment & Install Commands
    python_info = None
    if py_files or dep_files:
        env_instructions = []
        package_managers = []
        
        has_reqs = any(d.type == "requirements" for d in dep_files)
        
        if has_reqs:
            package_managers.append("pip")
        
        python_info = PythonInfo(
            packageManagers=package_managers,
            dependencyFiles=dep_files,
            envSetupInstructions=env_instructions
        )

    return RepoAnalysis(
        repoPath=str(root),
        docs=docs,
        configurationFiles=configs,
        scripts=scripts,
        notes=notes,
        python=python_info,
        projectLayout=ProjectLayout(),
        testSetup=TestSetup()
    )