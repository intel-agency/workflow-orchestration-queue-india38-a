# AGENTS.md

OS-APOW (Workflow Orchestration Queue) — a headless agentic orchestration platform
that transforms GitHub Issues into autonomous execution orders. The system uses a
4-pillar architecture (EAR/STATE/BRAIN/HANDS) implemented in Python/FastAPI, with
GitHub Actions triggering AI orchestration via devcontainers and the opencode CLI.

## Project Overview

A headless orchestration platform that listens for GitHub events (issues, PRs, etc.),
queues them as work items using GitHub Issues + Labels as a state machine, and dispatches
them to isolated devcontainer workers running AI agents via the opencode CLI.

### Tech Stack

- **Python 3.12+** — Primary language for all system logic
- **FastAPI 0.110+** — High-performance async web framework (webhook receiver)
- **Pydantic v2** — Data validation, settings management, schema definitions
- **HTTPX** — Async HTTP client for GitHub REST API calls
- **pytest** — Testing framework with async support
- **Ruff** — Fast Python linter and formatter (replaces flake8, isort, black)
- **MyPy** — Static type checker (strict mode)
- **uv** — Rust-based Python package manager
- **GitHub Actions** — CI/CD, workflow triggers
- **DevContainers** — Reproducible containerized development environment
- **opencode CLI v1.2.24** — AI agent runtime with MCP server support

### Architecture (4 Pillars)

| Pillar | Component | Location | Purpose |
|--------|-----------|----------|---------|
| EAR | Notifier | `src/workflow_orchestration_queue/ear/` | FastAPI webhook receiver for GitHub events |
| STATE | Queue | `src/workflow_orchestration_queue/state/` | GitHub Issues + Labels as state machine |
| BRAIN | Sentinel | `src/workflow_orchestration_queue/brain/` | Async service managing Worker lifecycle |
| HANDS | Worker | `src/workflow_orchestration_queue/hands/` | Action execution via devcontainer + opencode CLI |

State machine labels: `agent:queued` → `agent:in-progress` → terminal states (`agent:success`, `agent:error`, `agent:infra-failure`, `agent:stalled-budget`).

## Setup Commands

### Install Dependencies

```bash
uv sync --extra dev
```

> **Important:** Use `--extra dev` to include dev dependencies (pytest, ruff, mypy). Plain `uv sync` only installs runtime dependencies.

### Install Optional Lint/Scan Tools

```bash
pwsh -NoProfile -File ./scripts/install-dev-tools.ps1
```

### Run Development Server

```bash
# FastAPI server with hot reload (http://localhost:8000)
uv run uvicorn workflow_orchestration_queue.main:app --reload

# Or via entry point
uv run woq-api

# Or in Docker
docker compose up -d
```

### Entry Points

| Entry Point | Command | Description |
|-------------|---------|-------------|
| `woq-api` | `uv run woq-api` | FastAPI development server |
| `woq-sentinel` | `uv run woq-sentinel` | Sentinel background service |

## Project Structure

```
src/workflow_orchestration_queue/     # Main Python package
├── main.py                           # FastAPI application entry point
├── ear/                              # EAR pillar — webhook handlers and routes
│   ├── handlers/                     # GitHub event handlers
│   └── routes/                       # FastAPI route definitions
├── state/                            # STATE pillar — models and GitHub queue store
│   ├── models/                       # WorkItem and related models
│   └── store/                        # GitHub-backed queue store
├── brain/                            # BRAIN pillar — sentinel and orchestrator
│   ├── sentinel.py                   # Sentinel polling service
│   └── orchestrator.py              # Task orchestration logic
├── hands/                            # HANDS pillar — executor and notifier
│   ├── executor.py                   # Devcontainer worker execution
│   └── notifier.py                   # Status notification logic
├── config/                           # Configuration management (Pydantic settings)
└── api/                              # FastAPI routes and dependencies

tests/                                # Python unit tests (pytest)
test/                                 # Shell-based tests (devcontainer, tools, prompts)
test/fixtures/                        # Sample webhook payloads

.github/workflows/                    # CI/CD workflows
├── orchestrator-agent.yml            # Primary agent workflow
├── validate.yml                      # CI validation (lint, scan, test)
├── publish-docker.yml                # Build and push Docker image to GHCR
├── prebuild-devcontainer.yml         # Build prebuilt devcontainer image
└── prompts/                          # Prompt templates

.opencode/                            # AI agent definitions and commands
├── agents/                           # Agent definitions (orchestrator, developer, etc.)
└── commands/                         # Reusable command prompts

scripts/                              # PowerShell helper scripts
local_ai_instruction_modules/         # Local instruction modules for AI agents
plan_docs/                            # Project planning documents
```

### Key Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project config, dependencies, tool settings (ruff, mypy, pytest) |
| `uv.lock` | Deterministic lockfile for exact package versions |
| `opencode.json` | opencode CLI config with MCP server definitions |
| `.devcontainer/devcontainer.json` | Consumer devcontainer (pulls prebuilt GHCR image) |
| `.github/.devcontainer/Dockerfile` | Devcontainer image definition |
| `.github/.labels.json` | Repository label definitions (single source of truth) |

## Code Style

- **Pydantic v2** for all data models and settings
- **Strict MyPy** typing (configured in `pyproject.toml`)
- **async/await** for all I/O operations (FastAPI, HTTPX)
- Imports at top-level of file (ruff `PLC0415`)
- Line length limit: **100 characters** (ruff config)
- Use `logging.exception()` instead of `logging.error()` in exception handlers
- Use `enum.StrEnum` for string enums (Python 3.11+)
- Double quotes, spaces for indentation (ruff formatter defaults)

## Testing Instructions

### Python Tests (pytest)

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run a specific test file
uv run pytest tests/test_main.py

# Collect tests only (dry run)
uv run pytest --collect-only
```

Tests live in the `tests/` directory. Use `pytest-asyncio` with `asyncio_mode = "auto"`.
Markers: `@pytest.mark.slow`, `@pytest.mark.integration`.

### Shell Tests

```bash
# All shell tests
bash test/test-devcontainer-build.sh && bash test/test-devcontainer-tools.sh && bash test/test-prompt-assembly.sh

# Individual shell tests
bash test/test-prompt-assembly.sh     # Prompt assembly validation
bash test/test-devcontainer-tools.sh  # Dockerfile/tool availability
bash test/test-image-tag-logic.sh     # Image tag logic
```

Add new fixture payloads to `test/fixtures/` when testing new event types.

### Full Validation

```bash
# Run all checks (lint, scan, test) — requires pwsh
pwsh -NoProfile -File ./scripts/validate.ps1 -All

# Individual checks
pwsh -NoProfile -File ./scripts/validate.ps1 -Lint
pwsh -NoProfile -File ./scripts/validate.ps1 -Scan
pwsh -NoProfile -File ./scripts/validate.ps1 -Test
```

## PR and Commit Guidelines

- **Commit messages**: Use imperative mood, focus on the "why" not the "what" (e.g., "Fix webhook HMAC validation for missing signature header")
- **PR titles**: Descriptive and concise; prefix with scope if applicable
- **Required checks before committing**:
  - `uv run ruff check src/ tests/` — no lint errors
  - `uv run ruff format --check src/ tests/` — formatting passes
  - `uv run mypy src/` — no type errors
  - `uv run pytest` — all tests pass
  - `bash test/test-prompt-assembly.sh` — prompt assembly tests pass
- **Branch naming**: Use descriptive names (e.g., `feature/webhook-validation`, `fix/sentinel-polling`)
- **Do not push** until local validation passes
- **Monitor CI** after push: `gh run list --limit 5`, `gh run watch <id>`
- **Pin action versions by SHA** in workflow files
- **Never add duplicate** top-level `name:`, `on:`, or `jobs:` keys in workflow YAML
- **Preserve** the `__EVENT_DATA__` placeholder in `orchestrator-agent-prompt.md`

## Common Pitfalls

- **`uv sync` without `--extra dev`**: Commands like `uv run pytest` or `uv run ruff` fail with "module not found". Always use `uv sync --extra dev`.
- **`pwsh` not available outside devcontainer**: `scripts/validate.ps1` requires PowerShell Core. Run individual lint/test tools directly, or install `pwsh`.
- **Prebuilt devcontainer image not found**: Fresh clones fail to start devcontainer until `publish-docker` and `prebuild-devcontainer` workflows complete their first run.
- **Existing linting errors**: The codebase has some existing lint issues. Ensure new code passes linting; fix existing issues incrementally.
- **Environment variables**: Sentinel (`woq-sentinel`) requires `GITHUB_ORG` and `GITHUB_REPO` env vars. FastAPI webhooks require `WEBHOOK_SECRET`.
- **`.opencode/` directory**: Checked out by `actions/checkout` — do not COPY it in the Dockerfile.
