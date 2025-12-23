    1 # Onboarding Guide for imgix-python
    2
    3 This document provides essential information to get new contributors up and running with the `imgix-python` project.
    4
    5 ## 🐍 Python Version
    6
    7 No single Python version pin detected. However, the project's CI (via `.circleci/config.yml`) and `setup.py` classifiers indicate compatibility and testing against Python versions **3.7, 3.8, 3.9, 3.10,
      and 3.11**.
    8
    9 ## 🚀 Installation
   10
   11 To install the library for development, first create a virtual environment, then install the package along with its development dependencies.
   12
   13 1.  **Install the package:**
      pip install imgix
   1     *(Source: `README.md`)*
   2
   3 2.  **For development (including test dependencies):**
      pip install ".[dev,test]"

   1     *(Source: `setup.py` extras_require, `tox.ini` deps)*
   2
   3 ## 🧪 Testing
   4
   5 The project uses `tox` to manage testing environments and `pytest` for running tests.
   6
   7 1.  **Run all tests and linter via tox:**
      tox
   1     *(Source: `README.md`, `tox.ini`)*
   2
   3 2.  **Run pytest directly:**
      pytest --cov=imgix

   1     *(Source: `tox.ini` `[testenv]` section)*
   2
   3 3.  **Run doctests from README:**
      python -m doctest -v README.md

   1     *(Source: `README.md`)*
   2
   3 ## 🔍 Linting
   4
   5 Linting is configured using `flake8` and can be run via `tox`.
   6
   7 1.  **Run linter via tox:**
      tox -e flake8

   1     *(Source: `tox.ini` `envlist` and `[testenv:flake8]` section)*
   2
   3 2.  **Run flake8 directly:**
      flake8 setup.py imgix tests
   1     *(Source: `tox.ini` `[testenv:flake8]` section)*

  3) Uncertainties / follow-ups:
   * Formatting commands: No explicit dedicated formatting commands (like black or isort) were found. Linting is handled by flake8. I'd check pyproject.toml (if it existed) or Makefile/Taskfile/package.json
     (if this were a JS project) for common formatting tools.
   * Build commands: No explicit separate build command (like python setup.py sdist bdist_wheel) was found documented in README.md or tox.ini for general use. Installation is covered.

  4) Token usage: unknown (145,542)
