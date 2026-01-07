# Test Design for Agent-Based Architecture

## Overview

This document outlines the testing strategy for the agent-based architecture in the mcp-repo-onboarding project. Given that the agent system will be treated as integration and evaluation testing, this document defines the required test types, acceptance criteria, and testing approaches.

## Test Categories

### 1. Unit Tests for Individual Agents

#### Purpose
Test each agent in isolation to ensure it correctly processes inputs and generates expected outputs.

#### Scope
- BaseAgent interface implementation
- Each specific agent (Analysis, Environment, Dependencies, Scripts, Testing, Linting, Configuration, Documentation, Notes)
- Agent context processing
- Error handling within agents

#### Test Cases
- Agent can_handle() method returns correct boolean for different contexts
- Agent execute() method generates correct output for valid inputs
- Agent handles edge cases gracefully (missing data, unexpected formats)
- Agent follows validation rules (V1-V8 compliance)
- Agent respects safety ignore rules
- Agent applies ranking and truncation correctly

#### Acceptance Criteria
- Each agent class has 90%+ unit test coverage
- All validation rules are tested for each relevant agent
- Error handling paths are covered
- Performance benchmarks are met (agents complete within acceptable timeframes)

### 2. Integration Tests for Agent Orchestration

#### Purpose
Test the interaction between agents and the orchestrator to ensure proper execution order and data flow.

#### Scope
- Agent dependency resolution
- Execution order determination
- Data passing between agents
- Orchestrator error handling
- Fallback mechanism activation

#### Test Cases
- Agents execute in correct dependency order
- Data flows correctly between dependent agents
- Orchestrator handles agent failures gracefully
- Fallback to existing functionality works when agent system fails
- Multiple agents can run in parallel where dependencies allow

#### Acceptance Criteria
- All agent dependencies are resolved correctly
- Data integrity maintained throughout orchestration
- Fallback mechanism activates properly when needed
- Parallel execution works without conflicts

### 3. System Integration Tests for MCP Tools

#### Purpose
Test the new `/analyze_repo_with_agents` MCP tool and its integration with the existing MCP infrastructure.

#### Scope
- MCP tool registration and invocation
- Parameter handling (path, sections, mode)
- JSON output format compatibility
- Integration with existing MCP tools
- Backward compatibility with existing tools

#### Test Cases
- New MCP tool accepts parameters correctly
- Tool generates valid JSON output matching existing schema
- Tool integrates properly with Gemini CLI
- Existing MCP tools continue to work alongside new agent system
- Error responses follow MCP protocol

#### Acceptance Criteria
- MCP tool follows protocol specifications
- JSON output is compatible with existing consumers
- Performance is comparable to or better than existing tools
- All existing functionality remains intact

### 4. Validation Compliance Tests

#### Purpose
Ensure the agent-generated ONBOARDING.md content complies with all existing validation rules (V1-V8).

#### Scope
- All validation rules (V1-V8)
- Edge cases that might violate validation rules
- Truncation and ranking compliance
- Safety ignore rule compliance

#### Test Cases
- Generated content passes all V1-V8 validation rules
- Repo path line is present and correctly formatted (V2)
- Venv snippets are properly labeled (V4)
- Command formatting follows requirements (V5)
- Analyzer notes section policy followed (V6)
- Install policy compliance (V7)
- No provenance printed by default (V8)
- Truncation notes are properly generated when lists are truncated

#### Acceptance Criteria
- 100% of validation rules pass consistently
- All edge cases that could violate rules are handled
- Generated content is indistinguishable from existing system output
- Validation performance is acceptable

### 5. Evaluation Tests Using Real Repositories

#### Purpose
Evaluate the agent system against real-world repositories to ensure it produces useful, accurate onboarding documentation.

#### Scope
- Various repository types (different frameworks, tools, structures)
- Performance evaluation
- Accuracy comparison with existing system
- User experience assessment

#### Test Cases
- Django project analysis and documentation generation
- Flask project with multiple configuration files
- Poetry-based project with complex dependencies
- Project with extensive documentation files
- Minimal Python project with basic setup
- Project with multiple testing frameworks
- Project with various linting tools configured
- Repository with Node.js components (for polyglot testing)

#### Acceptance Criteria
- Agent system produces equivalent or better quality documentation than existing system
- Performance is acceptable for typical repository sizes
- Generated documentation is accurate and useful
- System handles diverse repository types appropriately

### 6. Regression Tests

#### Purpose
Ensure the new agent system doesn't break existing functionality.

#### Scope
- All existing MCP tools continue to work
- Existing analysis logic remains functional
- Validation system continues to work correctly
- All existing test fixtures pass

#### Test Cases
- Existing `analyze_repo` tool works as before
- Existing `get_run_and_test_commands` tool works as before
- Existing `write_onboarding` and `read_onboarding` tools work as before
- All existing test suites pass
- Backward compatibility maintained

#### Acceptance Criteria
- No regressions in existing functionality
- All existing tests continue to pass
- Performance degradation is minimal (less than 10%)
- All existing integrations continue to work

### 7. Performance and Load Tests

#### Purpose
Ensure the agent system performs well under various load conditions.

#### Scope
- Response time for different repository sizes
- Memory usage during analysis
- Concurrent request handling
- Resource utilization

#### Test Cases
- Small repositories (< 100 files) processed within 5 seconds
- Medium repositories (100-1000 files) processed within 30 seconds
- Large repositories (> 1000 files) processed within 2 minutes
- Multiple concurrent requests handled appropriately
- Memory usage stays within acceptable bounds

#### Acceptance Criteria
- Response times meet defined thresholds
- Memory usage is reasonable for repository size
- System handles concurrent requests without degradation
- Performance is comparable to or better than existing system

### 8. Security and Safety Tests

#### Purpose
Ensure the agent system follows all safety rules and doesn't introduce security vulnerabilities.

#### Scope
- Safety ignore rules enforcement
- File system access controls
- Input validation
- Protection against malicious repository structures

#### Test Cases
- Safety ignore rules applied correctly in all agents
- Files in ignored paths are not processed
- No unauthorized file system access occurs
- Malformed repository structures handled safely
- Large files are processed safely (size limits enforced)

#### Acceptance Criteria
- All safety rules are enforced consistently
- No security vulnerabilities introduced
- System handles malicious inputs safely
- File access is properly sandboxed

## Test Implementation Strategy

### 1. Test-Driven Development Approach
- Write tests before implementing agent functionality
- Ensure each agent meets its specific requirements
- Validate integration points early in development

### 2. Fixture-Based Testing
- Create diverse repository fixtures for different scenarios
- Include fixtures that test edge cases and validation boundaries
- Maintain fixtures for regression testing

### 3. Automated Testing Pipeline
- Integrate tests into CI/CD pipeline
- Run unit tests on every commit
- Run integration tests on pull requests
- Run evaluation tests periodically on real repositories

### 4. Quality Gates
- Unit test coverage threshold: 90%
- Validation compliance: 100%
- Performance benchmarks: within defined thresholds
- Regression tests: all must pass

## Acceptance Criteria Summary

For the agent-based architecture to be considered ready for production:

1. All unit tests pass with 90%+ coverage
2. All integration tests pass
3. Generated ONBOARDING.md passes all V1-V8 validation rules
4. Performance benchmarks are met
5. No regressions in existing functionality
6. Security and safety requirements are satisfied
7. Evaluation tests show improvement or equivalence to existing system
8. All GitHub issues related to the agent system are resolved