# OS-APOW Technology Stack

> **Document Version:** 1.0  
> **Last Updated:** March 2026  
> **Status:** Planning

This document defines the complete technology stack for the **OS-APOW (Workflow Orchestration Queue)** system.

---

## Core Languages

| Language | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.12+ | Primary language for Orchestrator, API Webhook receiver, and all system logic |
| **PowerShell Core (pwsh)** | 7.x | Shell Bridge scripts, Auth synchronization, cross-platform CLI interactions |
| **Bash** | 5.x | Shell Bridge scripts, container orchestration utilities |

---

## Web Framework & Server

| Component | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.110+ | High-performance async web framework for Webhook Notifier |
| **Uvicorn** | 0.27+ | ASGI web server for production FastAPI deployment |
| **Pydantic** | 2.x | Data validation, settings management, schema definitions |

---

## HTTP & API Clients

| Component | Purpose |
|-----------|---------|
| **HTTPX** | Fully asynchronous HTTP client for GitHub REST API calls (chosen over `requests` for async support) |

---

## Package Management

| Tool | Version | Purpose |
|------|---------|---------|
| **uv** | 0.10+ | Rust-based Python package installer and dependency resolver (orders of magnitude faster than pip/poetry) |
| **pyproject.toml** | - | Core definition file for dependencies and metadata |
| **uv.lock** | - | Deterministic lockfile for exact package versions |

---

## Containerization & Infrastructure

| Component | Purpose |
|-----------|---------|
| **Docker CLI** | Worker container lifecycle management |
| **DevContainers** | Isolated, reproducible execution environment for AI agents |
| **Docker Compose** | Multi-container orchestration for complex workflows |

### Container Resource Constraints

| Resource | Limit | Purpose |
|----------|-------|---------|
| CPU | 2 cores | Prevent rogue agents from causing DoS |
| RAM | 4 GB | Ensure orchestrator stability |
| Network | Isolated bridge network | Prevent lateral movement to host |

---

## AI/LLM Runtime

| Component | Purpose |
|-----------|---------|
| **opencode CLI** | 1.2.24+ | AI agent runtime for executing instruction modules |
| **ZhipuAI GLM** | GLM-5 | Primary LLM model for agent reasoning |
| **Kimi (Moonshot)** | - | Alternative LLM provider (via `KIMI_CODE_ORCHESTRATOR_AGENT_API_KEY`) |

---

## State Management

| Component | Purpose |
|-----------|---------|
| **GitHub Issues** | Primary state persistence ("Markdown as a Database") |
| **GitHub Labels** | State machine indicators (`agent:queued`, `agent:in-progress`, etc.) |
| **GitHub Milestones** | Phase tracking and progress visualization |
| **GitHub Assignees** | Distributed locking mechanism for concurrency control |

### State Labels

| Label | Description |
|-------|-------------|
| `agent:queued` | Task awaiting Sentinel pickup |
| `agent:in-progress` | Sentinel actively processing |
| `agent:reconciling` | Stale task being recovered |
| `agent:success` | Terminal success state |
| `agent:error` | Logic/implementation error |
| `agent:infra-failure` | Infrastructure failure |
| `agent:stalled-budget` | Budget/token limit exceeded |

---

## Security Components

| Component | Purpose |
|-----------|---------|
| **HMAC SHA256** | Webhook signature verification |
| **GitHub App Installation Tokens** | Scoped API authentication (5,000 req/hr) |
| **Credential Scrubber** | Regex-based sanitization of secrets in public logs |

### Secret Patterns Scrubbed

- `ghp_*` — GitHub PAT (classic)
- `ghs_*` — GitHub App installation token
- `gho_*` — GitHub OAuth token
- `github_pat_*` — GitHub fine-grained PAT
- `Bearer` tokens
- `sk-*` — OpenAI-style API keys
- ZhipuAI keys

---

## MCP (Model Context Protocol) Servers

| Server | Purpose |
|--------|---------|
| `@modelcontextprotocol/server-sequential-thinking` | Step-by-step reasoning for complex problems |
| `@modelcontextprotocol/server-memory` | Knowledge graph for context persistence |

---

## Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **GitHub CLI (gh)** | Repository, issue, and PR management |
| **ngrok / Tailscale** | Local-to-cloud tunneling for webhook development |

---

## Logging & Observability

| Component | Purpose |
|-----------|---------|
| **Python logging** | Structured console logging via StreamHandler |
| **Docker logs** | Container stdout capture |
| **GitHub Issue Comments** | Public telemetry and heartbeat updates |
| **Local JSONL files** | Worker output (black box forensic logs) |

---

## Directory Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # Core dependencies (uv)
├── uv.lock                      # Lockfile
├── src/
│   ├── notifier_service.py      # FastAPI Webhook receiver
│   ├── orchestrator_sentinel.py # Background polling service
│   ├── models/
│   │   ├── work_item.py         # Unified WorkItem, TaskType, scrub_secrets()
│   │   └── github_events.py     # Webhook payload schemas
│   └── queue/
│       └── github_queue.py      # ITaskQueue + GitHubQueue implementation
├── scripts/
│   ├── devcontainer-opencode.sh # Core shell bridge
│   ├── gh-auth.ps1              # GitHub auth sync
│   └── update-remote-indices.ps1
├── local_ai_instruction_modules/
│   ├── create-app-plan.md
│   ├── perform-task.md
│   └── analyze-bug.md
└── docs/
```

---

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub App installation token or PAT |
| `GITHUB_ORG` | Organization name (e.g., `intel-agency`) |
| `GITHUB_REPO` | Repository name (e.g., `workflow-orchestration-queue`) |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTINEL_BOT_LOGIN` | - | Bot account login for assign-then-verify locking |
| `WEBHOOK_SECRET` | - | HMAC secret for webhook validation (Notifier only) |
| `ZHIPU_API_KEY` | - | ZhipuAI model access |
| `KIMI_CODE_ORCHESTRATOR_AGENT_API_KEY` | - | Kimi model access |

---

## References

- [Architecture Guide](./architecture.md)
- [Development Plan v4.2](./OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Specification v1.2](./OS-APOW%20Implementation%20Specification%20v1.2.md)
