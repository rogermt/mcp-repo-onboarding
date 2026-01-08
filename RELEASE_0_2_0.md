# Release 0.2.0: Phase 10 - Enhanced Polyglot Support

## Release Overview

We're excited to announce the release of mcp-repo-onboarding version 0.2.0, featuring the completion of Phase 10 with enhanced polyglot repository support and improved primary tooling detection.

## What's New in Phase 10

### Enhanced Primary Tooling Detection
- **Intelligent Language Detection**: The system now intelligently determines if a repository is primarily Python, Node.js, or mixed based on evidence scoring
- **Evidence-Based Scoring**: 
  - Python evidence: pyproject.toml, requirements*.txt, setup.py, etc. (+ scores)
  - Node.js evidence: package.json, lockfiles (package-lock.json, yarn.lock, etc.) (+ scores)
  - Automatic classification as "Python", "Node.js", or "Unknown"

### Node.js Primary Repository Support
- **Node.js Command Derivation**: Static-only extraction of commands from package.json scripts
- **Package Manager Detection**: Automatic detection of npm, pnpm, yarn, or bun based on lockfiles
- **Command Generation**: Proper command suggestions for install, dev, start, test, lint, and format scripts
- **Node-primary Fixtures**: Added evaluation fixtures to ensure validator compliance

### Improved User Experience
- **Reduced Redundancy**: The "Other tooling detected" section now hides evidence for the primary ecosystem to eliminate duplicate information
- **Clearer Analyzer Notes**: Explicit indication of primary tooling in analyzer notes
- **No Python Venv Snippets**: For Node-primary repos, no longer suggests Python virtual environments

### Validation Compliance
- **Maintained Standards**: All V1-V8 validation rules continue to pass
- **Deterministic Output**: ONBOARDING.md generation remains consistent across runs
- **Backward Compatibility**: All existing Python-primary repos continue to work unchanged

## Key Features

### 1. Primary Tooling Detection
The system now analyzes repository evidence to determine the primary technology stack:
```
## Analyzer notes
* Primary tooling: Node.js (package.json, package-lock.json present)
```

### 2. Node.js Command Support
For Node.js primary repositories, the system now generates appropriate commands:
- Install commands based on detected package manager
- Dev, start, test, lint, and format commands from package.json scripts

### 3. Cleaner Output
- Eliminated redundant information between "Analyzer notes" and "Other tooling detected"
- Only secondary/non-primary ecosystems appear in "Other tooling detected"

## Technical Improvements

### Architecture Enhancements
- Updated onboarding blueprint engine to support primary tooling awareness
- Enhanced evidence extraction for multi-language repositories
- Improved ranking and classification logic

### Validation Updates
- Updated EXTRACT_OUTPUT_RULES.md to reflect new "Other tooling detected" behavior
- Maintained all existing validation rules (V1-V8)

## Breaking Changes (None)
This release maintains full backward compatibility with existing functionality. All previous features continue to work as before.

## Migration Guide
No migration is required. The system automatically detects repository characteristics and applies the appropriate logic.

## Known Issues
- For mixed-language repositories, the primary tooling detection uses a deterministic scoring system that may occasionally classify a repository differently than expected. This is by design to ensure consistent behavior.

## Contributors
Thanks to all contributors who helped make Phase 10 possible.

## Documentation
- Updated EXTRACT_OUTPUT_RULES.md with Phase 10 analyzer behavior
- Enhanced SOFTWARE_DESIGN_GUIDE.md with polyglot repository considerations

## Next Steps
Future releases will build upon this polyglot foundation with:
- Enhanced support for additional languages (Go, Rust, etc.)
- Improved command suggestion accuracy
- More sophisticated multi-language project handling

---
Release Date: January 7, 2026
Version: 0.2.0