import os
import re
from pathlib import Path
from typing import List, Tuple

from .schema import (
    RepoAnalysis, RepoAnalysisScriptGroup, CommandInfo, DocInfo, ConfigFileInfo, 
    ProjectLayout, TestSetup
)

MAX_DOCS_CAP = 10
MAX_CONFIG_CAP = 15

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__",
    "dist", "build", ".mypy_cache", ".pytest_cache", "site-packages"
}

def scan_repo_files(root: Path, max_files: int = 5000) -> Tuple[List[str], List[str]]:
    """
    Scans repo files.
    Strategy: Scan root dir FIRST (to find config files), then BFS subdirectories.
    """
    all_files: List[str] = []
    py_files: List[str] = []
    
    # 1. Process root directory first
    try:
        with os.scandir(root) as entries:
            dirs_to_visit = []
            for entry in entries:
                if entry.name in SKIP_DIRS:
                    continue
                if entry.is_dir():
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
                    
                    if entry.name in SKIP_DIRS:
                        continue
                        
                    if entry.is_dir():
                        queue.append(entry.path)
                    elif entry.is_file():
                        # Calculate relative path from repo root
                        try:
                            rel_path = str(Path(entry.path).relative_to(root))
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

    # Regex: Capture target at start of line, ignore indented lines
    target_pattern = re.compile(r"^([a-zA-Z0-9_-]+):")
    
    common_targets = {"test", "lint", "format", "dev", "run", "start", "check", "install"}
    
    for line in content.splitlines():
        match = target_pattern.match(line)
        if match:
            target = match.group(1)
            if target in common_targets:
                cmd_info = CommandInfo(
                    command=f"make {target}",
                    source=f"{makefile_path}:{target}"
                )
                if target not in commands:
                    commands[target] = []
                commands[target].append(cmd_info)
    return commands

def get_config_priority(path: str) -> int:
    """Ports getConfigFilePriorityScore from TS."""
    name = Path(path).name.lower()
    
    if name == "makefile":
        return 100
    if name in ["pyproject.toml", "setup.cfg", "setup.py"]:
        return 90
    if name in ["tox.ini", "noxfile.py"]:
        return 80
    if name in [".pre-commit-config.yaml", ".pre-commit-config.yml"]:
        return 70
    
    # Github Workflows
    if path.startswith(".github/workflows/"):
        ci_keywords = ["ci", "test", "lint", "build", "checker", "integration", "release", "publish", "deploy"]
        if any(k in name for k in ci_keywords):
            return 60
        
        automation_patterns = ["add-", "labeler", "stale", "lock", "auto-", "project"]
        if any(p in name for p in automation_patterns):
            return 5
            
        return 20

    return 10

def get_doc_priority(path: str) -> int:
    """Ports getDocPriorityScore from TS."""
    name = Path(path).name.lower()
    if name.startswith("readme"):
        return 100
    if name.startswith("contributing"):
        return 100
    return 50

def analyze_repo(repo_path: str, max_files: int = 5000) -> RepoAnalysis:
    root = Path(repo_path).resolve()
    all_files, py_files = scan_repo_files(root, max_files)
    
    docs = []
    configs = []
    
    # Categorize files
    for f in all_files:
        name = Path(f).name.lower()
        
        # Docs classification
        if name.startswith("readme") or name.startswith("contributing") or f.startswith("docs/"):
            docs.append(DocInfo(path=f, type="doc"))
        
        # Config classification
        is_config = False
        if name in ["makefile", "pyproject.toml", "tox.ini", "setup.cfg", "setup.py", "noxfile.py"]:
            is_config = True
        elif name in ["pytest.ini", "pytest.cfg"]:
            is_config = True
        elif name in [".pre-commit-config.yaml", ".pre-commit-config.yml"]:
            is_config = True
        elif f.startswith(".github/workflows/"):
            is_config = True
            
        if is_config:
            # For schema simplicity we use the filename/path as type or a generic one
            # The TS version often used the exact filename as type for specific configs
            configs.append(ConfigFileInfo(path=f, type=name))

    # Prioritize & Cap Docs
    docs.sort(key=lambda x: get_doc_priority(x.path), reverse=True)
    notes = []
    
    if len(docs) > MAX_DOCS_CAP:
        notes.append(f"docs list truncated to {MAX_DOCS_CAP} entries (total={len(docs)})")
        docs = docs[:MAX_DOCS_CAP]

    # Prioritize & Cap Configs
    configs.sort(key=lambda x: get_config_priority(x.path), reverse=True)
    
    if len(configs) > MAX_CONFIG_CAP:
        notes.append(f"configurationFiles list truncated to {MAX_CONFIG_CAP} entries (total={len(configs)})")
        configs = configs[:MAX_CONFIG_CAP]

    # Extract Commands (Makefile)
    scripts = RepoAnalysisScriptGroup()
    
    # Find makefile (case insensitive check)
    makefile = next((c.path for c in configs if Path(c.path).name.lower() == "makefile"), None)
    
    if makefile:
        mk_cmds = extract_makefile_commands(root, makefile)
        if "test" in mk_cmds:
            scripts.test.extend(mk_cmds["test"])
        if "lint" in mk_cmds:
            scripts.lint.extend(mk_cmds["lint"])
        if "dev" in mk_cmds:
            scripts.dev.extend(mk_cmds["dev"])

    return RepoAnalysis(
        repoPath=str(root),
        docs=docs,
        configurationFiles=configs,
        scripts=scripts,
        notes=notes,
        projectLayout=ProjectLayout(), # Simplified for initial pass
        testSetup=TestSetup()
    )