# Agent-Based Architecture Design Schema

## Overview
This schema defines the structure for implementing an agent-based system for repository analysis that maintains compatibility with existing validation rules and design principles.

## Core Architecture Components

### 1. Agent Interface Definition
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

class AgentContext(BaseModel):
    """Context passed to each agent containing repository analysis data"""
    repo_path: str
    repo_analysis: Dict
    extracted_data: Dict
    config: Dict

class AgentResult(BaseModel):
    """Result returned by each agent"""
    section_content: str
    metadata: Dict
    success: bool
    errors: List[str]

class BaseAgent(ABC):
    """Base interface for all agents in the system"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the agent"""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """List of agent names this agent depends on"""
        pass
    
    @abstractmethod
    def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can process the given context"""
        pass
    
    @abstractmethod
    def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's logic and return results"""
        pass
```

### 2. Agent Types and Responsibilities

#### 2.1 Analysis Agent
- **Purpose**: Performs initial repository analysis using existing code
- **Input**: Repository path
- **Output**: Structured analysis data following `RepoAnalysis` schema
- **Dependencies**: None
- **Validation**: Must produce data compatible with existing validation rules

#### 2.2 Environment Agent
- **Purpose**: Extracts Python environment information
- **Input**: Analysis data from Analysis Agent
- **Output**: Environment setup section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow V2 (Repo path line) and V4 (Venv snippet labeling) rules

#### 2.3 Dependencies Agent
- **Purpose**: Identifies and formats dependency information
- **Input**: Analysis data from Analysis Agent
- **Output**: Dependencies section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow V5 (Command formatting) and V7 (Install policy) rules

#### 2.4 Scripts Agent
- **Purpose**: Processes run/develop commands
- **Input**: Analysis data from Analysis Agent
- **Output**: Run/develop section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow V5 (Command formatting) rules

#### 2.5 Testing Agent
- **Purpose**: Generates test commands based on detected frameworks
- **Input**: Analysis data from Analysis Agent
- **Output**: Test section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow V5 (Command formatting) rules

#### 2.6 Linting Agent
- **Purpose**: Creates lint/format commands based on configuration
- **Input**: Analysis data from Analysis Agent
- **Output**: Lint/format section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow V5 (Command formatting) rules

#### 2.7 Configuration Agent
- **Purpose**: Lists useful configuration files with descriptions
- **Input**: Analysis data from Analysis Agent
- **Output**: Configuration files section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow classification boundaries (Section 3 of EXTRACT_OUTPUT_RULES)

#### 2.8 Documentation Agent
- **Purpose**: Processes documentation files
- **Input**: Analysis data from Analysis Agent
- **Output**: Documentation section content
- **Dependencies**: Analysis Agent
- **Validation**: Must follow ranking rules (Section 4.1 of EXTRACT_OUTPUT_RULES)

#### 2.9 Notes Agent
- **Purpose**: Handles analyzer notes and metadata
- **Input**: Analysis data from Analysis Agent
- **Output**: Notes section content when needed
- **Dependencies**: Analysis Agent
- **Validation**: Must follow V6 (Analyzer notes section policy) rules

### 3. Orchestrator Schema

```python
class AgentOrchestrator:
    """Manages the execution of agents in the correct order"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_order: List[str] = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
    
    def determine_execution_order(self) -> List[str]:
        """Determine the correct order to execute agents based on dependencies"""
        # Topological sort based on dependencies
        pass
    
    def execute_agents(self, context: AgentContext) -> Dict[str, AgentResult]:
        """Execute all agents in the correct order"""
        pass
    
    def validate_results(self, results: Dict[str, AgentResult]) -> bool:
        """Validate that results meet all requirements"""
        pass
```

### 4. Data Flow Schema

```
Repository Path
       ↓
Analysis Agent (extracts repo structure, dependencies, etc.)
       ↓
Environment Agent → Dependencies Agent → Scripts Agent → Testing Agent → Linting Agent → Configuration Agent → Documentation Agent → Notes Agent
       ↓              ↓                    ↓                ↓              ↓              ↓                     ↓                  ↓
   Environment      Dependencies        Scripts         Testing       Linting       Configuration        Documentation    Notes
   Section          Section            Section         Section       Section       Section              Section          Section
       ↓              ↓                    ↓                ↓              ↓              ↓                     ↓                  ↓
              ONBOARDING.md Assembly
                       ↓
              Validation (V1-V8 compliance)
                       ↓
              Final ONBOARDING.md Output
```

### 5. Validation Compliance Schema

Each agent must ensure its output complies with the validation rules:

- **V1**: All required headings must exist in correct order
- **V2**: Repo path line must be present after Overview
- **V3**: "No pin" must be exact and not prefixed
- **V4**: Venv snippet labeling requirements
- **V5**: Command formatting in command sections
- **V6**: Analyzer notes section policy
- **V7**: Install policy (prevent invented multi-requirements installs)
- **V8**: No provenance printed by default

### 6. Safety and Ignore Rules Compliance

All agents must respect the safety ignore rules:
- Hardcoded safety ignore blocklist (Section 2.1)
- Normalized repo-relative POSIX paths
- Safety ignore applied before any analysis

### 7. Ranking and Truncation Schema

Agents handling ranked lists must follow the specified ranking rules:
- Docs ranking (Section 4.1)
- Configuration ranking (Section 4.2)
- Dependency files ranking (Section 4.3)
- Required truncation notes format (Section 5)

### 8. Configuration Enrichment Schema

Agents may apply enrichment rules as specified:
- Pre-commit notebook hygiene detection (Section 6.1)
- Notebook-centric detection (Section 7)
- Framework key symbols (Section 8)
- Primary tooling detection (Section 9)

### 9. Implementation Requirements

#### 9.1 File Structure
```
src/mcp_repo_onboarding/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── orchestrator.py
│   ├── analysis_agent.py
│   ├── environment_agent.py
│   ├── dependencies_agent.py
│   ├── scripts_agent.py
│   ├── testing_agent.py
│   ├── linting_agent.py
│   ├── configuration_agent.py
│   ├── documentation_agent.py
│   └── notes_agent.py
├── schema.py
├── analysis/
├── onboarding.py
└── server.py
```

#### 9.2 MCP Tool Integration
The new slash command `/analyze_repo_with_agents` should:
- Accept parameters: path, sections, mode
- Use existing analysis code as the foundation
- Leverage the agent system for section generation
- Maintain backward compatibility with existing tools
- Return JSON output compatible with current MCP interface

#### 9.3 Error Handling
- Each agent should handle errors gracefully
- Fallback to existing functionality if agent system fails
- Maintain detailed logging for debugging
- Preserve existing error handling patterns