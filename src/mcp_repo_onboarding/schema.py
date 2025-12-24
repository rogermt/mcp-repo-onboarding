from typing import Literal

from pydantic import BaseModel, Field

"""
Pydantic schemas for the MCP Repo Onboarding API.

These models define the structure of data exchanged between the MCP server and client.
"""


class CommandInfo(BaseModel):
    """Information about a detected command."""

    command: str
    source: str
    name: str | None = None
    description: str | None = None
    confidence: Literal["detected", "derived", "heuristic"] | None = None


class LanguageStat(BaseModel):
    """Statistics about a programming language in the repo."""

    name: str
    fileCount: int
    approxLines: int | None = None


class PythonEnvFile(BaseModel):
    """Information about a Python environment/dependency file."""

    path: str
    type: str  # pyproject, requirements, etc.
    toolGuess: str | None = None
    description: str | None = None


class PythonInfo(BaseModel):
    """Aggregated information about the Python environment."""

    pythonVersionHints: list[str] = Field(default_factory=list)
    packageManagers: list[str] = Field(default_factory=list)
    dependencyFiles: list[PythonEnvFile] = Field(default_factory=list)
    envSetupInstructions: list[str] = Field(default_factory=list)
    installInstructions: list[str] = Field(default_factory=list)


class ProjectLayout(BaseModel):
    """Information about the project directory structure."""

    sourceDirs: list[str] = Field(default_factory=list)
    testDirs: list[str] = Field(default_factory=list)
    hasSrcLayout: bool = False
    notablePackages: list[str] = Field(default_factory=list)


class FrameworkInfo(BaseModel):
    """Information about a detected framework."""

    name: str
    detectionReason: str


class TestSetup(BaseModel):
    """Information about the test configuration."""

    framework: str | None = None
    locations: list[str] | None = None
    commands: list[CommandInfo] | None = None
    usesTox: bool = False
    usesNox: bool = False
    toxConfigPath: str | None = None
    noxConfigPath: str | None = None


class ConfigFileInfo(BaseModel):
    """Information about a configuration file."""

    path: str
    type: str
    description: str | None = None


class DeploymentHint(BaseModel):
    """Hint about deployment configuration."""

    type: str
    path: str
    notes: str | None = None


class DocInfo(BaseModel):
    """Information about a documentation file."""

    path: str
    type: str


class GitInfo(BaseModel):
    """Information about git status."""

    isGitRepo: bool


class RepoAnalysisScriptGroup(BaseModel):
    """Grouped scripts found in the repository."""

    dev: list[CommandInfo] = Field(default_factory=list)
    start: list[CommandInfo] = Field(default_factory=list)
    test: list[CommandInfo] = Field(default_factory=list)
    lint: list[CommandInfo] = Field(default_factory=list)
    format: list[CommandInfo] = Field(default_factory=list)
    install: list[CommandInfo] = Field(default_factory=list)
    other: list[CommandInfo] = Field(default_factory=list)


class RepoAnalysis(BaseModel):
    """Top-level analysis result for a repository."""

    repoPath: str
    languages: list[LanguageStat] = Field(default_factory=list)
    python: PythonInfo | None = None
    projectLayout: ProjectLayout = Field(default_factory=ProjectLayout)
    scripts: RepoAnalysisScriptGroup = Field(default_factory=RepoAnalysisScriptGroup)
    frameworks: list[FrameworkInfo] = Field(default_factory=list)
    testSetup: TestSetup = Field(default_factory=TestSetup)
    configurationFiles: list[ConfigFileInfo] = Field(default_factory=list)
    deploymentHints: list[DeploymentHint] = Field(default_factory=list)
    docs: list[DocInfo] = Field(default_factory=list)
    gitInfo: GitInfo | None = None
    notes: list[str] = Field(default_factory=list)


class OnboardingDocument(BaseModel):
    """Representation of the ONBOARDING.md file."""

    exists: bool
    path: str
    content: str | None = None
    sizeBytes: int | None = None


class WriteOnboardingResult(BaseModel):
    """Result of a write operation."""

    path: str
    bytesWritten: int
    backupPath: str | None = None


class RunAndTestCommands(BaseModel):
    """Simplified view for the get_run_and_test_commands tool."""

    devCommands: list[CommandInfo] = Field(default_factory=list)
    testCommands: list[CommandInfo] = Field(default_factory=list)
    buildCommands: list[CommandInfo] = Field(default_factory=list)
