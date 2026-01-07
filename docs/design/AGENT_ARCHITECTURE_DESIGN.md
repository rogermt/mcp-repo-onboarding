# Agent-Based Architecture for Repository Analysis

## Overview

This document outlines the design for a new agent-based architecture for the mcp-repo-onboarding project. The goal is to enhance the existing analysis capabilities by introducing a modular, agent-based system that maintains the evidence-based, static analysis approach while improving maintainability and extensibility.

## Current Architecture

The current system consists of:
- MCP tools: `analyze_repo`, `write_onboarding`, `read_onboarding`, `get_run_and_test_commands`
- Analysis code in `src/mcp_repo_onboarding/` that performs static analysis
- Prompt logic in `mcp_prompt.txt` that orchestrates the MCP tools
- JSON output format that represents repository structure and detected elements

## Proposed Agent-Based Architecture

### New Slash Command: `/analyze_repo_with_agents`

#### Command Interface
```
/analyze_repo_with_agents
  Parameters:
    - path (optional): Repository path (default: current directory)
    - sections (optional): Comma-separated list of sections to generate
    - mode (optional): "full", "minimal", or "custom"
```

#### Architecture Components

##### 1. Orchestrator Agent
- Coordinates the overall analysis process
- Manages dependencies between sections
- Ensures consistent output format
- Handles fallback procedures when agents fail
- Assembles final ONBOARDING.md from agent outputs

##### 2. Section-Specific Agents
- **Environment Agent**: Processes Python version and environment setup information
- **Dependencies Agent**: Handles dependency files and installation commands
- **Scripts Agent**: Processes run/develop commands from scripts directory
- **Testing Agent**: Generates test commands based on detected frameworks and testing tools
- **Linting Agent**: Creates lint/format commands based on configuration files (ruff, mypy, etc.)
- **Configuration Agent**: Lists useful configuration files with descriptions
- **Documentation Agent**: Processes documentation files and organizes them appropriately
- **Notes Agent**: Handles analyzer notes and metadata about the analysis process

### Data Flow

1. **Initial Analysis**: Use existing analysis code to extract repository information
2. **JSON Output**: Generate structured JSON similar to current `analyze_repo` output
3. **Agent Distribution**: Distribute relevant data to appropriate agents based on their capabilities
4. **Section Generation**: Each agent generates its section based on the provided data
5. **Assembly**: Orchestrator assembles sections into final ONBOARDING.md format
6. **Validation**: Validate output against existing requirements using the existing validation logic

### Agent Interface

```python
class SectionAgent:
    def can_handle(self, repo_data: dict) -> bool:
        """Check if agent can process this data"""
        pass
    
    def generate_content(self, repo_data: dict) -> str:
        """Generate section content based on repo data"""
        pass
    
    def get_dependencies(self) -> list:
        """List other agents this agent depends on"""
        pass
    
    def get_required_data_keys(self) -> list:
        """List the keys from repo_data that this agent needs"""
        pass
```

### Implementation Plan

#### Phase 1: Core Infrastructure
- Create orchestrator agent framework
- Implement basic agent interface and registration system
- Maintain existing analysis functionality as a fallback
- Ensure backward compatibility with existing MCP tools

#### Phase 2: Agent Development
- Develop individual section agents based on existing analysis logic
- Implement data extraction methods as documented in STATIC_ANALYSIS_EXTRACTION_METHODS.md
- Add dependency management between agents
- Create agent-specific configuration and customization options

#### Phase 3: Integration
- Create the new slash command `/analyze_repo_with_agents`
- Add fallback to existing functionality when agent system fails
- Ensure validator compliance with existing validation rules
- Add comprehensive logging and error handling

#### Phase 4: Enhancement
- Add dynamic agent loading based on repository characteristics
- Implement agent performance metrics and monitoring
- Add support for custom user-defined agents
- Create agent marketplace or registry for community contributions

### Benefits

1. **Modularity**: Each section can be updated independently without affecting others
2. **Extensibility**: New agents can be added for additional functionality without modifying core logic
3. **Maintainability**: Clear separation of concerns makes the codebase easier to understand and modify
4. **Backward Compatibility**: Existing functionality remains intact and available
5. **Evidence-Based**: Maintains the static analysis approach that's fundamental to the project
6. **Customization**: Allows for custom agents for specific project types or requirements
7. **Testability**: Individual agents can be tested in isolation
8. **Performance**: Agents can be run in parallel where dependencies allow

### Integration with Existing Code

The agent-based system will leverage the existing analysis code:
- Use existing file scanning and categorization logic
- Reuse framework detection algorithms
- Maintain the same evidence-based approach
- Keep the same JSON output structure for compatibility
- Preserve existing validation requirements

### Error Handling and Fallbacks

- If any agent fails, the orchestrator will attempt to use a fallback approach
- If the entire agent system fails, fall back to the existing analysis logic
- Maintain detailed logging for debugging agent failures
- Provide clear error messages when agents cannot process certain repository types

### Security and Safety

- All agents will follow the same safety rules as the current system (no code execution, no network calls)
- Maintain the deterministic, static analysis approach
- Respect .gitignore and other ignore patterns
- Implement agent sandboxing if needed for custom agents