from abc import ABC, abstractmethod
from typing import Any, Dict

from .schema import ConfigFileInfo, CommandInfo, PythonEnvFile


# Base Class for the Strategy Pattern
class MetadataDescriber(ABC):
    """Abstract base class for a metadata description strategy."""

    @abstractmethod
    def describe(self, target: Any) -> Any:
        pass


# --- Concrete Strategy Implementations ---


# Configuration File Describers
class MakefileDescriber(MetadataDescriber):
    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        target.description = (
            "Primary task runner for development and build orchestration."
        )
        return target


class GitHubWorkflowDescriber(MetadataDescriber):
    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        target.description = "CI/CD automation workflow."
        return target


class ToxIniDescriber(MetadataDescriber):
    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        target.description = "Test environment orchestrator (tox)."
        return target


class NoxfileDescriber(MetadataDescriber):
    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        target.description = "Test automation sessions (nox)."
        return target


class PreCommitDescriber(MetadataDescriber):
    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        target.description = "Pre-commit hooks configuration (code quality automation)."
        return target


class SetuptoolsDescriber(MetadataDescriber):
    def describe(self, target: ConfigFileInfo) -> ConfigFileInfo:
        target.description = "Packaging/build configuration (setuptools)."
        return target


# Dependency File Describers
class RequirementsTxtDescriber(MetadataDescriber):
    def describe(self, target: PythonEnvFile) -> PythonEnvFile:
        target.description = "Python dependency manifest."
        return target


class PyprojectTomlDescriber(MetadataDescriber):
    def describe(self, target: PythonEnvFile) -> PythonEnvFile:
        target.description = (
            "Project configuration and dependency management (PEP 518/621)."
        )
        return target


# Command Describers
class MakeTestDescriber(MetadataDescriber):
    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run the test suite via Makefile target."
        return target


class MakeFormatDescriber(MetadataDescriber):
    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run formatting via Makefile target."
        return target


class MakeRunDescriber(MetadataDescriber):
    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run the application via Makefile target."
        return target


class ToxDescriber(MetadataDescriber):
    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run tests via tox."
        return target


class ToxEnvDescriber(MetadataDescriber):
    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run specific tox environment."
        return target


class BashScriptDescriber(MetadataDescriber):
    def describe(self, target: CommandInfo) -> CommandInfo:
        target.description = "Run repo script entrypoint."
        return target


# --- Central Registry ---

# Using filename/command string as keys for the lookup
FILE_DESCRIBER_REGISTRY: Dict[str, MetadataDescriber] = {
    "makefile": MakefileDescriber(),
    "tox.ini": ToxIniDescriber(),
    "noxfile.py": NoxfileDescriber(),
    ".pre-commit-config.yaml": PreCommitDescriber(),
    "setup.py": SetuptoolsDescriber(),
    "setup.cfg": SetuptoolsDescriber(),
    ".github/workflows": GitHubWorkflowDescriber(),
    "requirements.txt": RequirementsTxtDescriber(),
    "pyproject.toml": PyprojectTomlDescriber(),
}

COMMAND_DESCRIBER_REGISTRY: Dict[str, MetadataDescriber] = {
    "make test": MakeTestDescriber(),
    "make format": MakeFormatDescriber(),
    "make run": MakeRunDescriber(),
    "tox": ToxDescriber(),
    "tox -e": ToxEnvDescriber(),  # Prefix for tox environments
    "bash scripts/": BashScriptDescriber(),  # Prefix for shell scripts
}
