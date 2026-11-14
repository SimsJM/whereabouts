# AGENTS.md

This repository is built through a software factory: AI agents work on tickets under the maintainer's supervision, and the maintainer merges every PR. Agents' rules are in their instructions; this file tells them how to work with **this codebase**.

## Status
There is no application code yet. The stack is decided: FastAPI and SQLite, server-rendered Jinja2 with HTMX and two small script islands (decisions D-05 to D-07, and ADR-0002 in `docs/agents/decisions/`). The decision log, `docs/agents/decision-log.md`, is binding: read it before designing or building anything.

## Build and test
<!-- Keep in step with commands in .factory/factory.yaml. -->
- **Install:** `python3 -m venv .venv`, then the development requirements into it (`requirements-dev.txt`, or the `dev` extra of `pyproject.toml`) once they exist. The exact command is `commands.install` in `.factory/factory.yaml`.
- **Check:** `sh tools/factory-check.sh`. Run it before every hand-off. It is what the factory runs on your pull request.
  - Until `pyproject.toml` exists it checks the repository only and says so.
  - From then on it runs `ruff check .` and `pytest`. A change with no tests collected fails.
- **End-to-end tests:** not set up yet.
- The virtual environment lives in `.venv/` and is never committed.

## Protected paths
You may not change these without an exception the maintainer has approved in the specification: `.factory/`, `.github/`, `AGENTS.md`, `CODEOWNERS`, `SECURITY.md`, `tools/factory-check.sh`, `docs/agents/decision-log.md`, `migrations/`, `Dockerfile`, the compose files, `pyproject.toml`, the requirements files and `.importlinter`. The first ticket that creates `pyproject.toml` or the requirements files needs that exception. If your work needs one, say so and stop; do not work around it.

## Layout
- Tests: `tests/`
- Migrations: `migrations/`
- Application code: *to be decided in the design*

## Contributing
All changes reach `main` through a pull request. See `.github/CODEOWNERS` for paths the maintainer must approve.
