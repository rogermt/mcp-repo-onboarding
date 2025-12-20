1 # Project Onboarding Guide                                                                                        │
│  2                                                                                                                   │
│  3 This document provides essential information to get started with the project.                                     │
│  4                                                                                                                   │
│  5 ## 🐍 Python Version                                                                                              │
│  6                                                                                                                   │
│  7 **Python 3.13**                                                                                                   │
│  8 (Cited from: `README.md` badge: `img                                                                              │
│    src="https://img.shields.io/badge/🐍Python-3.13-4ecdc4?style=for-the-badge&logo=python&logoColor=white&labelColor │
│    =1a1a2e"`)                                                                                                        │
│  9                                                                                                                   │
│ 10 ## 🚀 Installation and Setup                                                                                      │
│ 11                                                                                                                   │
│ 12 ### Recommended Setup (Using UV)                                                                                  │
│ 13                                                                                                                   │
│ 14 1.  **Clone the repository:**                                                                                     │
│ 15     ```bash                                                                                                       │
│ 16     git clone https://github.com/HKUDS/DeepCode.git                                                               │
│ 17     cd DeepCode/                                                                                                  │
│ 18     ```                                                                                                           │
│ 19     (Cited from: `README.md`, "Development Installation (From Source) - Using UV" section)                        │
│ 20                                                                                                                   │
│ 21 2.  **Install UV package manager:**                                                                               │
│ 22     ```bash                                                                                                       │
│ 23     curl -LsSf https://astral.sh/uv/install.sh | sh                                                               │
│ 24     ```                                                                                                           │
│ 25     (Cited from: `README.md`, "Development Installation (From Source) - Using UV" section)                        │
│ 26                                                                                                                   │
│ 27 3.  **Create virtual environment and install dependencies:**                                                      │
│ 28     ```bash                                                                                                       │
│ 29     uv venv --python=3.13                                                                                         │
│ 30     source .venv/bin/activate                                                                                     │
│ 31     uv pip install -r requirements.txt                                                                            │
│ 32     ```                                                                                                           │
│ 33     (Cited from: `README.md`, "Development Installation (From Source) - Using UV" section)                        │
│ 34                                                                                                                   │
│ 35 ### Direct Installation (for end-users)                                                                           │
│ 36                                                                                                                   │
│ 37 ```bash                                                                                                           │
│ 38 pip install deepcode-hku                                                                                          │
│ 39 ```                                                                                                               │
│ 40 (Cited from: `README.md`, "Direct Installation (Recommended)" section)                                            │
│ 41                                                                                                                   │
│ 42 ## ▶️ How to Run the Application                                                                                  │
│ 43                                                                                                                   │
│ 44 The application can be run in several ways:                                                                       │
│ 45                                                                                                                   │
│ 46 ### Web Interface (Recommended)                                                                                   │
│ 47                                                                                                                   │
│ 48 ```bash                                                                                                           │
│ 49 # If using UV                                                                                                     │
│ 50 uv run streamlit run ui/streamlit_app.py                                                                          │
│ 51 # Or using traditional Python                                                                                     │
│ 52 streamlit run ui/streamlit_app.py                                                                                 │
│ 53 ```                                                                                                               │
│ 54 (Cited from: `README.md`, "Launch Application - Web Interface" section)                                           │
│ 55                                                                                                                   │
│ 56 ### CLI Interface (Advanced Users)                                                                                │
│ 57                                                                                                                   │
│ 58 ```bash                                                                                                           │
│ 59 # If using UV                                                                                                     │
│ 60 uv run python cli/main_cli.py                                                                                     │
│ 61 # Or using traditional Python                                                                                     │
│ 62 python cli/main_cli.py                                                                                            │
│ 63 ```                                                                                                               │
│ 64 (Cited from: `README.md`, "Launch Application - CLI Interface" section)                                           │
│ 65                                                                                                                   │
│ 66 ### Installed Package                                                                                             │
│ 67                                                                                                                   │
│ 68 ```bash                                                                                                           │
│ 69 deepcode                                                                                                          │
│ 70 ```                                                                                                               │
│ 71 (Cited from: `README.md`, "Launch Application - Using Installed Package" section and `setup.py` entry point)      │
│ 72                                                                                                                   │
│ 73 ## 🧹 Linting and Formatting                                                                                      │
│ 74                                                                                                                   │
│ 75 This project uses `pre-commit` hooks for linting and formatting, powered by `ruff`.                               │
│ 76                                                                                                                   │
│ 77 ### Run pre-commit checks                                                                                         │
│ 78                                                                                                                   │
│ 79 ```bash                                                                                                           │
│ 80 pre-commit run --all-files --show-diff-on-failure                                                                 │
│ 81 ```                                                                                                               │
│ 82 (Cited from: `.pre-commit-config.yaml` and `.github/workflows/linting.yaml`)                                      │
│ 83                                                                                                                   │
│ 84 ## 🧪 Testing                                                                                                     │
│ 85                                                                                                                   │
│ 86 No explicit test command was found within the examined files.                                                     │
│ 87                                                                                                                   │
│ 88 ## 🏗️ Build Commands                                                                                              │
│ 89                                                                                                                   │
│ 90 For building release distributions:                                                                               │
│ 91                                                                                                                   │
│ 92 ```bash                                                                                                           │
│ 93 python -m pip install build                                                                                       │
│ 94 python -m build                                                                                                   │
│ 95 ```                                                                                                               │
│ 96 (Cited from: `.github/workflows/pypi-publish.yml`, "Build release distributions" step)  

✦ 1) Evidence used (bullet list of the exact files you inspected and what each contributed)
   * README.md: Provided Python version pin (3.13), run commands for installed package, web interface, and CLI
     interface, and installation steps.
   * .github/workflows/pypi-publish.yml: Indicated Python 3.x is used in CI, confirming Python dependency. Also showed
     build commands python -m pip install build and python -m build for release distributions.
   * setup.py: Confirmed deepcode as a console script and python_requires=">=3.9".
   * .pre-commit-config.yaml: Provided explicit formatting (ruff-format) and linting (ruff) commands via pre-commit.
   * .github/workflows/linting.yaml: Confirmed pre-commit workflow for linting and formatting.

  2) ONBOARDING.md content (single Markdown document, ready to save as ONBOARDING.md)
  Content written to `ONBOARDING.md` above.

  3) Uncertainties / follow-ups (what you could not confirm, and which file(s) to check)

   * Testing Commands: No explicit commands for running tests were found within the examined files. To confirm, one
     might look for:
       * A tests/ directory and check for common testing frameworks (e.g., pytest, unittest) usage within those files.
       * Any Makefile or custom build scripts that might contain test commands.
       * Further documentation beyond the README.md.
   * Specific build commands for development: The build commands found (python -m pip install build and python -m build)
     are specifically for PyPI release distributions. There might be other build steps relevant for local development
     that were not explicitly found.
   * Python version pin: While README.md explicitly states 3.13, setup.py has >=3.9 and CI files use 3.x. The 3.13 in
     README.md is assumed to be the intended development version, but this could be clarified.