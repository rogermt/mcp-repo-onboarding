# Static Analysis Extraction Methods

This document outlines the various methods for extracting information from repository files using static analysis techniques. These methods are used by the mcp-repo-onboarding analyzer to generate evidence-based onboarding documentation.

## 1. Code Structure Analysis

### Class and Function Definitions
- **Method**: Parse Python files using the `ast` module to identify class and function definitions
- **Implementation**: Use `ast.parse()` to create an Abstract Syntax Tree, then traverse nodes to find `ast.ClassDef` and `ast.FunctionDef` nodes
- **Output**: List of classes and functions with their names, line numbers, and file locations

### Import Dependencies
- **Method**: Parse Python files using the `ast` module to identify import statements
- **Implementation**: Look for `ast.Import` and `ast.ImportFrom` nodes in the AST
- **Output**: Mapping of dependencies between modules and external packages

### Framework Usage Patterns
- **Method**: Use regex patterns to identify common framework patterns
- **Implementation**: Search for patterns like `@app.route` (Flask), `@router.get` (FastAPI), `def test_*` (pytest)
- **Output**: List of detected framework usage patterns

## 2. Configuration File Analysis

### YAML Configuration Parsing
- **Method**: Parse YAML files using PyYAML library
- **Implementation**: Use `yaml.safe_load()` to extract configuration data from files like `.pre-commit-config.yaml`
- **Output**: Structured data representing the configuration settings

### TOML Configuration Parsing
- **Method**: Parse TOML files using `tomllib` (Python 3.11+) or `tomli` library
- **Implementation**: Use `tomllib.load()` to extract configuration data from `pyproject.toml`
- **Output**: Structured data representing tool settings and dependencies

### JSON Configuration Parsing
- **Method**: Parse JSON files using the built-in `json` module
- **Implementation**: Use `json.load()` to extract configuration data
- **Output**: Structured data representing configuration settings

## 3. File Type Categorization

### Extension-Based Classification
- **Method**: Use `pathlib.Path.suffix` to identify file types
- **Implementation**: Categorize files based on extensions (`.py`, `.md`, `.yaml`, etc.)
- **Output**: Mapping of files to their respective categories

### Content Pattern Analysis
- **Method**: Use regex patterns to identify file purposes
- **Implementation**: Look for patterns like `if __name__ == "__main__"` to identify entry points
- **Output**: Classification of files by purpose (entry points, libraries, tests, etc.)

## 4. Dependency Relationship Mapping

### Dependency File Parsing
- **Method**: Parse dependency files (pyproject.toml, requirements.txt, setup.py)
- **Implementation**: Extract package names and version constraints using appropriate parsers
- **Output**: List of dependencies with version constraints

### Version Constraint Analysis
- **Method**: Use the `packaging` library to analyze version specifications
- **Implementation**: Parse version strings using `packaging.specifiers` to understand compatibility
- **Output**: Structured representation of version requirements

### Dependency Group Identification
- **Method**: Parse pyproject.toml `[dependency-groups]` section
- **Implementation**: Extract optional dependency groups and their contents
- **Output**: Mapping of dependency groups to their packages

## 5. Code Pattern Recognition

### Test Pattern Detection
- **Method**: Use AST parsing to identify test functions
- **Implementation**: Look for functions with `assert` statements, test decorators, or test naming patterns
- **Output**: List of test functions with their locations

### Fixture Pattern Detection
- **Method**: Identify common fixture patterns in test files
- **Implementation**: Look for pytest fixture decorators (`@pytest.fixture`) or similar patterns
- **Output**: List of fixtures with their purposes

## 6. Security Configuration Analysis

### Security Package Detection
- **Method**: Scan for security-related package names in dependencies
- **Implementation**: Check dependency lists for packages like `safety`, `bandit`, `pip-audit`
- **Output**: List of security-related tools and their configurations

### Security Setting Extraction
- **Method**: Parse configuration files for security-related settings
- **Implementation**: Look for security-related keys in configuration files
- **Output**: List of security configurations

## 7. Documentation Analysis

### Docstring Detection
- **Method**: Parse Python files with AST to identify functions/classes with docstrings
- **Implementation**: Check if `ast.FunctionDef` and `ast.ClassDef` nodes have docstring literals
- **Output**: Count of documented functions/classes

### Documentation File Identification
- **Method**: Identify documentation files by extension and content
- **Implementation**: Look for `.md`, `.rst`, and other documentation formats
- **Output**: List of documentation files with their purposes

## 8. Build and Deployment Configuration

### Build Script Detection
- **Method**: Look for common build script names and patterns
- **Implementation**: Identify files like Makefile, build.py, setup.py, etc.
- **Output**: List of build scripts with their purposes

### CI/CD Configuration Analysis
- **Method**: Parse CI/CD configuration files to identify deployment steps
- **Implementation**: Extract deployment-related steps from workflow files
- **Output**: List of deployment configurations and steps

### Packaging Settings Extraction
- **Method**: Parse pyproject.toml `[build-system]` section
- **Implementation**: Extract build backend and package settings
- **Output**: Structured representation of packaging configuration

## 9. Version Control Pattern Analysis

### Git Ignore Pattern Analysis
- **Method**: Parse .gitignore files to understand project structure
- **Implementation**: Extract ignore patterns and categorize them
- **Output**: List of ignored file patterns with explanations

### Pre-commit Hook Detection
- **Method**: Parse .pre-commit-config.yaml to identify hooks
- **Implementation**: Extract hook configurations and their purposes
- **Output**: List of pre-commit hooks with their functions

### Workflow File Analysis
- **Method**: Parse GitHub Actions workflow files in .github/workflows/
- **Implementation**: Extract workflow steps and triggers
- **Output**: List of CI/CD workflows with their purposes

## 10. Performance and Optimization Indicators

### Performance Tool Detection
- **Method**: Identify performance-related packages in dependencies
- **Implementation**: Look for packages like `cProfile`, `line_profiler`, `memory_profiler`
- **Output**: List of performance analysis tools

### Performance Configuration Extraction
- **Method**: Parse configuration files for performance-related settings
- **Implementation**: Look for performance-related keys in configuration files
- **Output**: List of performance configurations

### Caching Mechanism Detection
- **Method**: Identify caching libraries in dependencies
- **Implementation**: Look for packages like `redis`, `memcached`, or caching decorators
- **Output**: List of caching mechanisms used in the project

## Implementation Notes

All extraction methods should follow these principles:
- Use only static analysis (no code execution)
- Respect .gitignore and other ignore patterns
- Handle large files efficiently (with size limits)
- Maintain deterministic output for reproducible results
- Provide clear error handling for malformed files