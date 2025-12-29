  Project Overview
  SearXNG is a free internet metasearch engine which aggregates results from various search services and databases. Users are neither tracked nor profiled.

  Development Environment Setup

  Python Version
  The project explicitly pins Python 3.14.

  Note: While some CI tests run against older Python versions (3.10-3.13) for compatibility, new development and primary CI occurs with Python 3.14.

  Node.js Version
  The project explicitly pins Node.js 24.

  Getting Started

   1. Clone the repository:
   1     git clone https://github.com/searxng/searxng.git
   2     cd searxng

   2. Install Python dependencies:
      This command sets up a Python virtual environment and installs necessary packages.
   1     make install

   3. Install Node.js dependencies (for frontend development):
      First, ensure you have Node.js version 24 installed (e.g., using nvm install 24). Then navigate to the client directory and install dependencies.
   1     cd client/simple
   2     npm install
   3     cd ../..

  Common Development Commands

  Running the Application
  To run a local developer instance:
   1 make run

  Testing

  Run all Python tests (including linting and formatting checks):
   1 make test

  Run CI-specific Python tests:
   1 make ci.test

  Run shell script tests:
   1 make test.shell

  Check search engines (utility):

   1 make search.checker

  Run container tests:
   1 make container.test

  Building

  Build documentation:
   1 make docs.html

  Build frontend themes:
   1 make themes.all

  Build container images (e.g., with Podman):
   1 make podman.build

  Linting and Formatting

  Format Python and shell code:
   1 make format

  Lint frontend themes:
   1 cd client/simple
   2 npm run lint

  Fix frontend formatting issues:

   1 cd client/simple
   2 npm run fix

  Cleaning

  Clean up Python, Node.js, Go, and build artifacts:
   1 make clean

  Clean Node.js modules (frontend):
   1 cd client/simple
   2 npm run clean

  ---
  Evidence used:

   * .github/workflows/checker.yml: Identified Python version 3.14 (env.PYTHON_VERSION) and commands make V=1 install, make search.checker.
   * .github/workflows/container.yml: Confirmed Python version 3.14 (env.PYTHON_VERSION) and commands make podman.build, make container.test.
   * .github/workflows/data-update.yml: Confirmed Python version 3.14 (env.PYTHON_VERSION).
   * .github/workflows/documentation.yml: Confirmed Python version 3.14 (env.PYTHON_VERSION) and command make V=1 docs.clean docs.html.
   * .github/workflows/integration.yml: Confirmed Python version 3.14 (env.PYTHON_VERSION) and also showed testing against 3.10-3.13. Identified commands make V=1 ci.test, make themes.lint, make themes.all.
     Indicated Node.js version source via .nvmrc.
   * .github/workflows/l10n.yml: Confirmed Python version 3.14 (env.PYTHON_VERSION).
   * .nvmrc: Explicitly states Node.js version 24.
   * Makefile: Provides definitions for many make targets, including run, install, clean, search.checker, test, ci.test, test.shell, format, docs.html, themes.all, podman.build, container.test, themes.lint.
     It also shows the underlying commands executed by these make targets (e.g., ./manage webapp.run).
   * client/simple/package.json: Provides frontend-specific npm scripts for build, build:icons, build:vite, clean, fix, fix:biome, fix:package, fix:stylelint, lint, lint:biome, lint:tsc.

  Uncertainties / follow-ups:

   * Python Version Explanation: While PYTHON_VERSION: "3.14" is used consistently in most GitHub Actions workflows, integration.yml tests against multiple Python versions (3.10-3.14). The ONBOARDING.md
     reflects that 3.14 is the pinned version for development, but further clarity on the exact minimum supported Python version for local development or production might be beneficial.
   * `./manage` script functionality: The Makefile heavily relies on ./manage. I did not inspect the manage script itself. A deeper understanding of its subcommands could provide more granular insights into
     project operations.
   * More specific build/deploy steps: The Makefile and container.yml hint at container builds (make podman.build, make container.build) and releases (make container.push), but full end-to-end deployment
     instructions would likely involve more details beyond just these commands.

  Token usage: unknown (278,715)
