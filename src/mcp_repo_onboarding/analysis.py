import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

import pathspec

from .schema import (
    RepoAnalysis, RepoAnalysisScriptGroup, CommandInfo, DocInfo, ConfigFileInfo, 
    ProjectLayout, TestSetup, PythonInfo, PythonEnvFile
)
from .describers import FILE_DESCRIBER_REGISTRY, COMMAND_DESCRIBER_REGISTRY

# Reference: docs/design/SOFTWARE_DESIGN_GUIDE.md#1.3-domain-driven-design-ddd-approach
# Separate registries for Config and Dependency files to ensure strict classification.
# This prevents accidental overlap (e.g. requirements.txt in configurationFiles).

CONFIG_FILE_TYPES = {
    "makefile", "tox.ini", "noxfile.py", ".pre-commit-config.yaml", 
    ".pre-commit-config.yml", "pytest.ini", "pytest.cfg", "pyproject.toml",
    "setup.cfg", "setup.py"
}

DEPENDENCY_FILE_TYPES = {
    "requirements.txt", "requirements-dev.txt", "requirements-server.txt",
    "pyproject.toml", "setup.py", "setup.cfg"
}

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
            resolved_path = path.resolve()
            rel_path = resolved_path.relative_to(self.repo_root)
            rel_path_str = str(rel_path.as_posix())
            
            if is_dir and not rel_path_str.endswith("/"):
                rel_path_str += "/"

            for si in self.safety_ignores:
                if f"/{si}/" in f"/{rel_path_str}":
                    return True
                if rel_path_str.startswith(f"{si}/") or rel_path_str == si:
                    return True

            if self._pathspec:
                return self._pathspec.match_file(rel_path_str)
            
            return False
        except (ValueError, OSError):
            return False

    def should_descend(self, dir_path: Path) -> bool:
        return not self.should_ignore(dir_path, is_dir=True)

def scan_repo_files(root: Path, ignore: IgnoreMatcher, max_files: int = 5000) -> Tuple[List[str], List[str]]:
    all_files: List[str] = []
    py_files: List[str] = []
    
    try:
        with os.scandir(root) as entries:
            sorted_entries = sorted(entries, key=lambda e: e.name)
            dirs_to_visit = []
            for entry in sorted_entries:
                entry_path = Path(entry.path)
                
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

    queue = dirs_to_visit
    while queue and len(all_files) < max_files:
        current_dir = queue.pop(0)
        try:
            with os.scandir(current_dir) as entries:
                sorted_entries = sorted(entries, key=lambda e: e.name)
                for entry in sorted_entries:
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

def extract_makefile_commands(root: Path, makefile_path: str) -> Dict[str, List[CommandInfo]]:
    # Reference: docs/design/SOFTWARE_DESIGN_GUIDE.md#3.3-functional-programming-emphasis
    commands = {}
    try:
        content = (root / makefile_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}

    # Improved regex to handle multiple targets per line (e.g., 'install uninstall:')
    target_pattern = re.compile(r"^([a-zA-Z0-9_-]+(?:\s+[a-zA-Z0-9_-]+)*):")
    
    target_mapping = {
        "test": "test",
        "lint": "lint",
        "format": "format",
        "dev": "dev",
        "install": "install",
        "run": "start",
        "start": "start",
        "check": "test"
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
                    
                    if category not in commands:
                        commands[category] = []
                    commands[category].append(cmd_info)
    return commands

def _is_safe_description(line: str) -> bool:

    """Checks if a comment line is a safe, non-command-like description."""

    line = line.strip()



    # Rule: Reject env var exports, assignments, or command-like lines

    if 'export' in line or '=' in line:

        return False

    if line.startswith(('cd ', 'bash ', 'python ', 'make ')):

        return False



    # Rule #26: Reject decorative "divider" lines based on character ratios.

    # A line is likely a divider if it has a high ratio of separator characters.

    separators = " -_=#"

    separator_count = sum(c in separators for c in line)

    total_chars = len(line)

    

    if total_chars > 4 and (separator_count / total_chars) > 0.5:

        # If over 50% of the line is made of separators, it's likely decorative.

        return False



    # Rule #26: Reject if it's a very short, non-linguistic word.

    if len(line.split()) < 2:

        # If it's a single word, check if it's a common non-descriptive keyword

        if line.upper() in ["CONFIG", "SETUP", "MAIN", "TEST", "BUILD", "START", "END"]:

             return False



    return True

def extract_shell_scripts(all_files: List[str], repo_root: Path) -> dict:
    commands = {"dev": [], "test": []}
    
    script_files = [f for f in all_files if f.replace('\\', '/').startswith("scripts/") and f.endswith(".sh")]
    
    for script in script_files:
        name = Path(script).name
        command_str = f"bash {script}"
        
        description = None
        try:
            with open(repo_root / script, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    # Stop scanning if we hit a non-comment, non-empty line (code has started)
                    if not line.startswith("#") and line:
                        break

                    if line.startswith("#") and not line.startswith("#!"):
                        candidate = line.lstrip("#").strip()
                        if _is_safe_description(candidate):
                            description = candidate
                            break # Found the first safe description, stop.
        except OSError:
            pass
            
        cmd_info = CommandInfo(
            command=command_str,
            source=script,
            name=name,
            description=description,
            confidence="derived"
        )
        
        if description is None and "bash scripts/" in COMMAND_DESCRIBER_REGISTRY:
             cmd_info = COMMAND_DESCRIBER_REGISTRY["bash scripts/"].describe(cmd_info)
        
        if "test" in name:
            commands["test"].append(cmd_info)
        else:
            commands["dev"].append(cmd_info)
            
    return commands

def extract_tox_commands(repo_root: Path, tox_path: str) -> dict:
    commands = {"test": [], "lint": []}
    try:
        content = (repo_root / tox_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return commands
    
    commands["test"].append(CommandInfo(command="tox", source=tox_path, description="Run tests via tox"))
    
    if "flake8" in content:
        commands["lint"].append(CommandInfo(command="tox -e flake8", source=tox_path, description="Run flake8 linting via tox"))
        
    return commands

def detect_workflow_python_version(repo_root: Path) -> List[str]:
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
        except OSError:
            continue
            
    return sorted(list(versions))

def get_config_priority(path: str) -> int:
    name = Path(path).name.lower()
    if name == "makefile": return 100
    if name in ["pyproject.toml", "setup.cfg", "setup.py"]: return 90
    if name in ["tox.ini", "noxfile.py"]: return 80
    if name in [".pre-commit-config.yaml", ".pre-commit-config.yml"]: return 70
    if path.startswith(".github/workflows/"): return 60
    return 10

def get_doc_priority(path: str) -> int:
    name = Path(path).name.lower()
    if name.startswith("readme"): return 100
    if name.startswith("contributing"): return 100
    if "quickstart" in name or "install" in name or "setup" in name: return 80
    return 50

def analyze_repo(repo_path: str, max_files: int = 5000) -> RepoAnalysis:
    root = Path(repo_path).resolve()
    
    gitignore_patterns = []
    gitignore = root / ".gitignore"
    if gitignore.is_file():
        try:
            with open(gitignore, 'r', encoding='utf-8') as f:
                gitignore_patterns.extend(f.readlines())
        except OSError: pass

    ignore = IgnoreMatcher(repo_root=root, safety_ignores=SAFETY_IGNORES, gitignore_patterns=gitignore_patterns)
    
    # 1. Targeted scan
    targeted_files = []
    safety_only_ignore = IgnoreMatcher(repo_root=root, safety_ignores=SAFETY_IGNORES, gitignore_patterns=[])
    
    for pattern in ["pyproject.toml", "tox.ini", "noxfile.py", "setup.py", "setup.cfg", "Makefile", ".pre-commit-config.yaml"]:
        p = root / pattern
        if p.is_file() and not safety_only_ignore.should_ignore(p):
            targeted_files.append(p.name)

    for pattern in ["requirements*.txt", ".github/workflows/*.yml"]:
        for p in root.glob(pattern):
            if p.is_file() and not safety_only_ignore.should_ignore(p):
                targeted_files.append(str(p.relative_to(root)))

    # 2. Broad scan
    all_other_files, py_files = scan_repo_files(root, ignore, max_files)

    # 3. Combine and categorize
    all_files = sorted(list(set(all_other_files + targeted_files)))
    
    docs = []
    configs = []
    dep_files = []
    
    for f_path in all_files:
        name = Path(f_path).name.lower()
        
        # Docs
        if name.startswith("readme") or name.startswith("contributing") or f_path.startswith("docs/"):
            docs.append(DocInfo(path=f_path, type="doc"))
            continue

        # Strict Categorization: Check Dependency Files First
        is_dep = False
        if name in DEPENDENCY_FILE_TYPES or (name.startswith("requirements") and name.endswith((".txt", ".in"))):
            desc_key = "requirements.txt" if name.startswith("requirements") else name
            dep_describer = FILE_DESCRIBER_REGISTRY.get(desc_key)
            dep_file = PythonEnvFile(path=f_path, type=name)
            if dep_describer:
                dep_file = dep_describer.describe(dep_file)
            dep_files.append(dep_file)
            is_dep = True

        # Config Files (Only if not already a dependency)
        # Reference: docs/design/SOFTWARE_DESIGN_GUIDE.md#1.3-domain-driven-design-ddd-approach
        # Strictly exclude dependency files from configurationFiles.
        if is_dep:
            continue

        is_workflow = f_path.startswith(".github/workflows/")
        describer = FILE_DESCRIBER_REGISTRY.get(name) or \
                    (FILE_DESCRIBER_REGISTRY.get(".github/workflows") if is_workflow else None)
        
        if describer or name in ["pytest.ini", "pytest.cfg"]:
            # Final check: NEVER include requirements.txt in configs
            if not (name.startswith("requirements") and name.endswith((".txt", ".in"))):
                config_file = ConfigFileInfo(path=f_path, type=name)
                if describer:
                    config_file = describer.describe(config_file)
                configs.append(config_file)

    # 4. Prioritize & Cap
    docs.sort(key=lambda x: get_doc_priority(x.path), reverse=True)
    notes = []
    if len(docs) > MAX_DOCS_CAP:
        notes.append(f"docs list truncated to {MAX_DOCS_CAP} entries (total={len(docs)})")
        docs = docs[:MAX_DOCS_CAP]

    configs.sort(key=lambda x: get_config_priority(x.path), reverse=True)
    if len(configs) > MAX_CONFIG_CAP:
        notes.append(f"configurationFiles list truncated to {MAX_CONFIG_CAP} entries (total={len(configs)})")
        configs = configs[:MAX_CONFIG_CAP]

    # 5. Extract Commands
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

    # 6. Infer Python Environment
    workflow_versions = detect_workflow_python_version(root)
    has_python_files = bool(py_files)
    has_dep_files = bool(dep_files)
    
    python_info = None
    if has_python_files or has_dep_files or workflow_versions:
        package_managers = []
        if any(d.path.startswith("requirements") for d in dep_files):
            package_managers.append("pip")
        elif any(Path(d.path).name.lower() in ["setup.py", "setup.cfg", "pyproject.toml"] for d in dep_files):
            package_managers.append("pip") # Default to pip for setuptools
        
        env_setup_instructions = [] # This will be for venv creation, etc. (currently empty)
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

        python_info = PythonInfo(
            packageManagers=package_managers,
            dependencyFiles=dep_files,
            envSetupInstructions=env_setup_instructions, # This remains empty for now
            installInstructions=install_instructions,
            pythonVersionHints=workflow_versions
        )
        
        # Sort dependencyFiles to prioritize requirements.txt
        # Reference: User request "requirements.txt appearing at the bottom of dependency list which is wrong"
        python_info.dependencyFiles.sort(key=lambda d: 0 if d.path == "requirements.txt" else 1)

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
