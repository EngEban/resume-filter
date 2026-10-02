# Contributing to ResumeFilter

First off, thank you for considering contributing! 🎉

This document covers the workflow, coding standards, and conventions
used in this project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Testing](#testing)
- [Pull Requests](#pull-requests)

---

## Code of Conduct

Be respectful, inclusive, and constructive. Harassment or discrimination
of any kind will not be tolerated.

---

## Getting Started

### 1. Fork & clone

```bash
git clone https://github.com/YOUR-USERNAME/resume-filter.git
cd resume-filter
git remote add upstream https://github.com/your-username/resume-filter.git
2. Set up a virtual environment
bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
3. Install dev dependencies
bash
pip install -r requirements-dev.txt
4. Set up pre-commit (optional but recommended)
bash
pre-commit install
Development Workflow
Create a feature branch from develop:

bash
git checkout develop
git pull upstream develop
git checkout -b feature/my-awesome-feature
Make your changes, following the coding standards below.

Write tests for new functionality.

Run checks locally:

bash
ruff check app ui tests
mypy app ui
pytest tests/ -v
Commit with a clear message (see below).

Push and open a Pull Request against develop.

Coding Standards
Python
Python 3.12+ syntax.

Line length: 100 characters.

Formatting: enforced by Ruff.

Type hints: required for all public functions.

Docstrings: required for all modules, classes, and public functions.

Style rules
Use async def wherever I/O is involved.

Prefer pathlib over os.path.

Prefer f-strings over .format().

Avoid mutable default arguments (def f(x=[]) ❌).

Never swallow exceptions silently (except: pass ❌).

Naming
Element	Convention	Example
Modules	snake_case	api_client.py
Classes	PascalCase	UnifiedLLMProvider
Functions	snake_case	calculate_ats_score
Constants	UPPER_SNAKE	MAX_RETRIES
Private	_leading_underscore	_internal_helper
Architecture principles
Separation of concerns — Keep API handlers thin; put logic in services/.

Dependency injection — Use FastAPI Depends for shared resources.

Async by default — Only use sync where unavoidable (e.g., Celery tasks).

Fail loudly — Raise specific exceptions, let global handlers format them.

Commit Messages
We follow Conventional Commits:

text
<type>(<scope>): <subject>

<body>

<footer>
Types
Type	    Description
feat	    A new feature
fix  	    A bug fix
docs	    Documentation only
style	    Formatting, no code change
refactor    Code change that is neither feature nor fix
perf	    Performance improvement
test	    Adding tests
chore	    Build, CI, tooling
security	Security-related fix
Examples
text
feat(auth): add password reset endpoint

fix(ats): correct keyword normalization for Arabic text

docs(readme): update quick start instructions

refactor(providers): extract resolve_llm_config helper
Testing
Write tests for every new feature and every bug fix.

Aim for 80%+ coverage on the files you touch.

Place unit tests in tests/test_*.py.

Use fixtures from tests/conftest.py.

bash
# Run all tests
pytest

# Run a specific file
pytest tests/test_ats_engine.py -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
Pull Requests
Before submitting, ensure:

□ Your branch is up to date with develop.
□ All tests pass locally.
□ Ruff + Mypy pass locally.
□ New code has tests.
□ Documentation is updated if needed.
□ Commit messages follow Conventional Commits.
PR template
Fill out the PR template that appears when you open a PR.

Review process
A maintainer reviews within ~3 days.

Address any requested changes.

Once approved, the PR is squash-merged into develop.

🎉 Thank You!
Your contributions make this project better. Every PR, issue, and
suggestion is appreciated.

If you have questions, open a Discussion.