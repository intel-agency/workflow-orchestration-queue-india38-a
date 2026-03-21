# OS-APOW Workflow Orchestration Queue

A headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders.

## Overview

OS-APOW (Open Source - Agentic Project Orchestration Workflow) represents a paradigm shift from **Interactive AI Coding** to **Headless Agentic Orchestration**. Instead of requiring a human-in-the-loop to navigate files, provide context, and trigger executions, OS-APOW uses a persistent, event-driven infrastructure that transforms standard project management artifacts (GitHub Issues) into "Execution Orders" autonomously fulfilled by specialized AI agents.

## Architecture

The system is built on a **4-pillar architecture**:

| Pillar | Component | Technology | Purpose |
|--------|-----------|------------|---------|
| **EAR** | Notifier | FastAPI | Event reception and webhook handling |
| **STATE** | Queue | GitHub Issues + Labels | State management and persistence |
| **BRAIN** | Sentinel | Async Python | Decision making and orchestration |
| **HANDS** | Worker | opencode CLI + DevContainer | Action execution |

```
┌─────────────────────────────────────────────────────────────────┐
│                        OS-APOW System                           │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   EAR       │   STATE     │   BRAIN     │      HANDS          │
│  (Notifier) │   (Queue)   │ (Sentinel)  │     (Worker)        │
├─────────────┼─────────────┼─────────────┼─────────────────────┤
│ FastAPI     │ GitHub      │ Async       │ DevContainer        │
│ Webhook     │ Issues +    │ Python      │ + opencode CLI      │
│ Receiver    │ Labels      │ Service     │                     │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/intel-agency/workflow-orchestration-queue-india38-a.git
cd workflow-orchestration-queue-india38-a
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the API server:
```bash
uv run uvicorn workflow_orchestration_queue.main:app --reload
```

### Docker Deployment

```bash
# Build and run
docker compose up -d

# View logs
docker compose logs -f api
```

## Project Structure

```
src/workflow_orchestration_queue/
├── __init__.py
├── main.py                    # FastAPI entry point
├── ear/                       # Event reception
│   ├── __init__.py
│   ├── routes/
│   └── handlers/
├── state/                     # State management
│   ├── __init__.py
│   ├── models/
│   │   └── work_item.py
│   └── store/
│       └── github_queue.py
├── brain/                     # Decision/orchestration
│   ├── __init__.py
│   ├── orchestrator.py
│   └── sentinel.py
├── hands/                     # Action execution
│   ├── __init__.py
│   ├── notifier.py
│   └── executor.py
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── health.py
│   │   └── webhooks.py
│   └── dependencies.py
└── config/
    ├── __init__.py
    └── settings.py
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Linting
uv run ruff check src/ tests/

# Formatting
uv run ruff format src/ tests/

# Type checking
uv run mypy src/
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |
| `/webhooks/github` | POST | GitHub webhook receiver |

## Configuration

Environment variables are documented in `.env.example`. Key settings:

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API token | Yes |
| `GITHUB_ORG` | Organization name | Yes |
| `GITHUB_REPO` | Repository name | Yes |
| `WEBHOOK_SECRET` | HMAC secret for webhooks | For Notifier |

## License

MIT License - see [LICENSE](LICENSE) for details.
