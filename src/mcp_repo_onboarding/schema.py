from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CommandInfo(BaseModel):
    command: str
    source: str
    name: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[Literal["detected", "derived", "heuristic"]] = None

class LanguageStat(BaseModel):
    name: str
    fileCount: int
    approxLines: Optional[int] = None

class PythonEnvFile(BaseModel):
    path: str
    type: str # pyproject, requirements, etc.
    toolGuess: Optional[str] = None

class PythonInfo(BaseModel):
    pythonVersionHints: List[str] = Field(default_factory=list)
    packageManagers: List[str] = Field(default_factory=list)
    dependencyFiles: List[PythonEnvFile] = Field(default_factory=list)
    envSetupInstructions: List[str] = Field(default_factory=list)

class ProjectLayout(BaseModel):
    sourceDirs: List[str] = Field(default_factory=list)
    testDirs: List[str] = Field(default_factory=list)
    hasSrcLayout: bool = False
    notablePackages: List[str] = Field(default_factory=list)

class FrameworkInfo(BaseModel):
    name: str
    detectionReason: str

class TestSetup(BaseModel):
    framework: Optional[str] = None
    locations: Optional[List[str]] = None
    commands: Optional[List[CommandInfo]] = None
    usesTox: bool = False
    usesNox: bool = False
    toxConfigPath: Optional[str] = None
    noxConfigPath: Optional[str] = None

class ConfigFileInfo(BaseModel):
    path: str
    type: str
    description: Optional[str] = None

class DeploymentHint(BaseModel):
    type: str
    path: str
    notes: Optional[str] = None

class DocInfo(BaseModel):
    path: str
    type: str

class GitInfo(BaseModel):
    isGitRepo: bool

class RepoAnalysisScriptGroup(BaseModel):
    dev: List[CommandInfo] = Field(default_factory=list)
    start: List[CommandInfo] = Field(default_factory=list)
    test: List[CommandInfo] = Field(default_factory=list)
    lint: List[CommandInfo] = Field(default_factory=list)
    format: List[CommandInfo] = Field(default_factory=list)
    install: List[CommandInfo] = Field(default_factory=list)
    other: List[CommandInfo] = Field(default_factory=list)

class RepoAnalysis(BaseModel):
    repoPath: str
    languages: List[LanguageStat] = Field(default_factory=list)
    python: Optional[PythonInfo] = None
    projectLayout: ProjectLayout = Field(default_factory=ProjectLayout)
    scripts: RepoAnalysisScriptGroup = Field(default_factory=RepoAnalysisScriptGroup)
    frameworks: List[FrameworkInfo] = Field(default_factory=list)
    testSetup: TestSetup = Field(default_factory=TestSetup)
    configurationFiles: List[ConfigFileInfo] = Field(default_factory=list)
    deploymentHints: List[DeploymentHint] = Field(default_factory=list)
    docs: List[DocInfo] = Field(default_factory=list)
    gitInfo: Optional[GitInfo] = None
    notes: List[str] = Field(default_factory=list)

class OnboardingDocument(BaseModel):
    exists: bool
    path: str
    content: Optional[str] = None
    sizeBytes: Optional[int] = None

class WriteOnboardingResult(BaseModel):
    path: str
    bytesWritten: int
    backupPath: Optional[str] = None

class RunAndTestCommands(BaseModel):
    devCommands: List[CommandInfo] = Field(default_factory=list)
    testCommands: List[CommandInfo] = Field(default_factory=list)
    buildCommands: List[CommandInfo] = Field(default_factory=list)
