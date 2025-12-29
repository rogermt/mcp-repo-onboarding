---

## Issue #75 — Feature: Enable installation as a Gemini CLI Extension

**Title:** Feature: Enable installation as a Gemini CLI Extension

**Labels:** `enhancement`, `priority: high`, `packaging`

**Description:**

To simplify distribution and usage, the `mcp-repo-onboarding` server should be packaged as a Gemini CLI extension. This will allow users to install it directly with a single command, instead of manually cloning the repository and configuring `settings.json`.

### Problem
- Current setup requires manual cloning, dependency installation, and JSON configuration.
- This process is error-prone and creates a barrier to entry for new users.

### Proposed Solution
1.  **Create a `gemini-extension.json` manifest file** in the project root. This file will define the extension's metadata and the command required to run the MCP server.
2.  **Update `pyproject.toml`** to ensure the manifest file and all required scripts and source files are included in the final package distribution.
3.  **Structure the package** so that all paths referenced in the manifest (`command`, `args`, `cwd`) are valid relative to the extension's root directory after installation.

#### Example `gemini-extension.json`:
```json
{
  "name": "repo-onboarding",
  "version": "0.2.0",
  "description": "Analyzes a Python repository to generate ONBOARDING.md.",
  "mcpServer": {
    "command": "uv",
    "args": [
      "--directory",
      ".",
      "run",
      "mcp-repo-onboarding"
    ],
    "cwd": "./"
  }
}
```

### Files to Update
- `gemini-extension.json` (create new)
- `pyproject.toml` (to include the new manifest in the package)
- `README.md` (to update installation instructions)

### Acceptance Criteria
- [ ] A `gemini-extension.json` manifest is present in the project root.
- [ ] The server can be successfully installed and run as a Gemini CLI extension.
- [ ] All paths in the manifest are correct and resolve properly after installation.
- [ ] The `README.md` is updated with the new, simpler installation instructions.
