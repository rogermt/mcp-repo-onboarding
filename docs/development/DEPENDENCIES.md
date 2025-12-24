# Dependency Management and Security

## Dependency Configuration

All dependencies are defined in `pyproject.toml` with both lower and upper version bounds. Upper bounds are set to the next major version to prevent breaking changes.

Example:
```toml
dependencies = [
    "mcp[cli]>=1.25.0,<2.0.0",
]
```

## Security Scanning

We use `pip-audit` to scan for known vulnerabilities in our dependencies.

### Local Scanning
You can run a security scan locally using:
```bash
uv run pip-audit
```

### Automated Scanning
A GitHub Actions workflow (`.github/workflows/security.yml`) runs `pip-audit` on:
- Every push to `main` and `feature/*` branches.
- Every pull request to `main`.
- A weekly schedule (every Monday).

## Automated Updates

Dependabot is configured (`.github/dependabot.yml`) to check for weekly updates for:
- Python dependencies (pip)
- GitHub Actions

When a new version is available, Dependabot will create a pull request.

## Updating Dependencies

To manually update a dependency:
1. Update the version range in `pyproject.toml`.
2. Run `uv sync --all-groups` to update the `uv.lock` file.
3. Run tests to ensure no regressions.
4. Commit both `pyproject.toml` and `uv.lock`.
