#!/bin/bash
# Script to create GitHub issues for mcp-repo-onboarding
# Run with: bash create_issues.sh

echo "Creating GitHub issues..."

# Issue 2: Add complete type hints
gh issue create --title "Add complete type hints and enable mypy strict mode" --label "enhancement" --body "Several functions are missing return type hints, and mypy is not configured in strict mode.

## Problem
- Some functions still need complete type hints
- No mypy strict mode enforcement

## Proposed Solution
1. Add explicit return type hints to all functions
2. Enable mypy strict mode in \`pyproject.toml\`
3. Fix all type errors revealed by strict mode

## Files to Update
- \`src/mcp_repo_onboarding/describers.py\`
- \`pyproject.toml\` (enable strict mode)

## Acceptance Criteria
- [ ] All functions have complete type hints
- [ ] mypy strict mode enabled
- [ ] All mypy errors resolved"

# Issue 3: Refactor analyze_repo
gh issue create --title "Refactor analyze_repo function to reduce cyclomatic complexity" --label "enhancement" --body "The \`analyze_repo\` function is 189 lines long with high cyclomatic complexity, making it difficult to maintain and test.

## Problem
- \`analyze_repo()\` in \`analysis.py\` (lines 380-568) is too long
- Multiple responsibilities in one function
- Hard to test individual components

## Proposed Solution
Break down into smaller, focused functions:
1. \`_scan_and_categorize_files()\`
2. \`_extract_all_commands()\`
3. \`_infer_python_environment()\`
4. \`_build_repo_analysis()\`

## Acceptance Criteria
- [ ] \`analyze_repo\` is under 50 lines
- [ ] Each extracted function has a single responsibility
- [ ] All existing tests still pass
- [ ] New unit tests for extracted functions"

# Issue 4: Add docstrings
gh issue create --title "Add comprehensive docstrings to all public functions" --label "documentation" --body "Many functions lack docstrings or have incomplete documentation.

## Problem
- Missing docstrings in \`get_config_priority()\`, \`get_doc_priority()\`
- Incomplete docstrings missing Args, Returns, Examples
- No module-level docstrings

## Proposed Solution
1. Add Google-style docstrings to all public functions
2. Include Args, Returns, Raises, and Examples sections
3. Add module-level docstrings
4. Configure pydocstyle to enforce standards

## Acceptance Criteria
- [ ] All public functions have complete docstrings
- [ ] pydocstyle configured and passing
- [ ] Module-level docstrings added"

# Issue 5: Add error scenario tests
gh issue create --title "Add comprehensive error scenario test coverage" --label "enhancement" --body "Current tests focus on happy paths. Need tests for error scenarios and edge cases.

## Missing Test Coverage
1. **Error scenarios:** Permission denied, corrupted files, large repos, symbolic links
2. **Edge cases:** Empty repo, binary-only repo, circular symlinks, invalid UTF-8
3. **Performance:** \`max_files\` limit behavior, benchmarks

## Proposed Solution
1. Add error scenario tests
2. Add edge case tests
3. Add performance benchmarks
4. Consider property-based testing with \`hypothesis\`

## Acceptance Criteria
- [ ] Test coverage > 85%
- [ ] All error paths tested
- [ ] Edge cases covered"

# Issue 6: Extract configuration
gh issue create --title "Extract configuration to dedicated config module" --label "enhancement" --body "Magic numbers and configuration are scattered throughout the codebase.

## Problem
Configuration constants like \`MAX_DOCS_CAP = 10\`, \`MAX_CONFIG_CAP = 15\`, \`max_files = 5000\` are scattered in the code.

## Proposed Solution
Create \`src/mcp_repo_onboarding/config.py\` with a configuration dataclass.

## Acceptance Criteria
- [ ] All configuration in dedicated module
- [ ] No magic numbers in code
- [ ] Configuration is type-safe"

# Issue 7: Dependency bounds
gh issue create --title "Add dependency upper bounds and security scanning" --label "dependencies" --body "Dependencies have no upper bounds, risking breaking changes from major updates.

## Problem
All dependencies use only lower bounds (e.g., \`mcp[cli]>=1.25.0\`), no upper bounds.

## Proposed Solution
1. Add upper bounds for major versions
2. Set up Dependabot or Renovate
3. Add security scanning with \`pip-audit\` or \`safety\`

## Acceptance Criteria
- [ ] All dependencies have upper bounds
- [ ] Dependabot configured
- [ ] Security scanning in CI"

# Issue 8: Pydantic error responses
gh issue create --title "Use Pydantic models for error responses instead of manual JSON" --label "enhancement" --body "Server error responses use manual JSON string formatting, which is error-prone.

## Problem
\`server.py\` manually formats JSON error strings instead of using Pydantic models.

## Proposed Solution
1. Create error response Pydantic models in \`schema.py\`
2. Use consistent error response format
3. Include error codes and details

## Acceptance Criteria
- [ ] Error response models defined
- [ ] All error responses use models
- [ ] Tests for error responses"

# Issue 9: Performance benchmarks
gh issue create --title "Add performance benchmarks and optional caching layer" --label "enhancement" --body "No performance benchmarks or caching for repeated analysis operations.

## Proposed Solution
1. Add performance benchmarks using \`pytest-benchmark\`
2. Implement optional caching layer
3. Add progress callbacks for large repositories
4. Consider async I/O for file operations

## Acceptance Criteria
- [ ] Performance benchmarks added
- [ ] Optional caching implemented
- [ ] Progress callbacks for long operations"

# Issue 10: Symbolic link protection
gh issue create --title "Add symbolic link detection and protection" --label "enhancement" --body "Current path sandboxing doesn't protect against symbolic link attacks.

## Problem
- No symbolic link detection in \`resolve_path_inside_repo()\`
- Potential for symbolic link traversal attacks

## Proposed Solution
1. Add symbolic link detection
2. Use \`Path.is_relative_to()\` (Python 3.9+)
3. Document security assumptions
4. Add security tests

## Acceptance Criteria
- [ ] Symbolic links detected and handled
- [ ] Security tests added
- [ ] Security assumptions documented"

echo "Done! All issues created."
