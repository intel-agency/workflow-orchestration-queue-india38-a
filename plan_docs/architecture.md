# OS-APOW Architecture

> **Document Version:** 1.0  
> **Last Updated:** March 2026  
> **Status:** Planning

This document describes the architecture of the **OS-APOW (Workflow Orchestration Queue)** system — a headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders.

---

## Executive Summary

OS-APOW represents a paradigm shift from **Interactive AI Coding** to **Headless Agentic Orchestration**. Instead of requiring a human-in-the-loop to navigate files, provide context, and trigger executions, OS-APOW uses a persistent, event-driven infrastructure that transforms standard project management artifacts (GitHub Issues) into "Execution Orders" autonomously fulfilled by specialized AI agents.

**Key Innovation:** The system is **Self-Bootstrapping** — once the initial Sentinel is deployed, the system uses its own orchestration capabilities to build its own remaining features.

---

## The Four-Pillar Architecture

The system is built on four conceptual pillars, each handling a distinct domain:

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

### 1. The EAR (Work Event Notifier)

**Technology:** Python 3.12, FastAPI, Pydantic, HTTPX

**Role:** The system's sensory input for external stimuli and asynchronous triggers.

**Responsibilities:**
- **Secure Webhook Ingestion:** Exposes `/webhooks/github` endpoint for GitHub events
- **Cryptographic Verification:** HMAC SHA256 validation against `WEBHOOK_SECRET`
- **Intelligent Event Triage:** Parses issue bodies and labels into unified `WorkItem` objects
- **Queue Initialization:** Applies `agent:queued` label to valid tasks

**Key Security:** Prevents "Prompt Injection via Webhook" by ensuring only verified GitHub events can trigger agent actions.

### 2. The STATE (Work Queue)

**Technology:** GitHub Issues, Labels, Milestones

**Philosophy:** "Markdown as a Database" — leveraging GitHub as the persistence layer provides:
- World-class audit logs
- Transparent versioning
- Built-in UI for human supervision
- Real-time intervention via commenting

**State Machine:**

```
┌──────────────┐     claim      ┌──────────────┐
│ agent:queued │───────────────▶│agent:in-     │
└──────────────┘                │  progress    │
       ▲                        └──────┬───────┘
       │                               │
       │                               ├──────────▶ ┌──────────────┐
       │           reconcile           │            │ agent:success│
       │       ◀───────────────────────┤            └──────────────┘
       │                               │
┌──────┴───────┐                       ├──────────▶ ┌──────────────┐
│agent:recon-  │                       │            │ agent:error  │
│  ciling      │◀──────────────────────┤            └──────────────┘
└──────────────┘  stale task recovery  │
                                        │
                                        ├──────────▶ ┌────────────────┐
                                        │            │agent:infra-    │
                                        │            │   failure      │
                                        │            └────────────────┘
                                        │
                                        └──────────▶ ┌────────────────┐
                                                     │agent:stalled-  │
                                                     │   budget       │
                                                     └────────────────┘
```

**Concurrency Control:** GitHub Assignees act as a distributed lock via the **assign-then-verify** pattern.

### 3. The BRAIN (Sentinel Orchestrator)

**Technology:** Python (Async), PowerShell, Docker CLI

**Role:** Persistent supervisor managing the lifecycle of Worker environments.

**Lifecycle:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SENTINEL LIFECYCLE                        │
├─────────────────────────────────────────────────────────────┤
│  1. POLLING DISCOVERY                                        │
│     └─▶ Query GitHub for agent:queued issues (60s interval) │
│         └─▶ Jittered exponential backoff on rate limits     │
│                                                              │
│  2. AUTH SYNCHRONIZATION                                     │
│     └─▶ Run scripts/gh-auth.ps1 for installation tokens     │
│                                                              │
│  3. TASK CLAIMING (Assign-then-Verify)                      │
│     └─▶ POST assignees → GET issue → verify assignee        │
│                                                              │
│  4. SHELL-BRIDGE EXECUTION                                   │
│     ├─▶ ./scripts/devcontainer-opencode.sh up               │
│     ├─▶ ./scripts/devcontainer-opencode.sh start            │
│     └─▶ ./scripts/devcontainer-opencode.sh prompt "{...}"   │
│                                                              │
│  5. TELEMETRY                                                │
│     └─▶ Heartbeat comments every 5 minutes                   │
│                                                              │
│  6. ENVIRONMENT RESET                                        │
│     └─▶ Stop container between tasks (prevent state bleed)  │
│                                                              │
│  7. GRACEFUL SHUTDOWN                                        │
│     └─▶ SIGTERM/SIGINT → finish current task → exit         │
└─────────────────────────────────────────────────────────────┘
```

### 4. The HANDS (Opencode Worker)

**Technology:** opencode CLI, LLM Core (GLM-5)

**Environment:** High-fidelity DevContainer

**Capabilities:**
- **Contextual Awareness:** Vector-indexed view of codebase
- **Instructional Logic:** Executes `.md` workflow modules from `/local_ai_instruction_modules/`
- **Verification:** Runs local test suites before PR submission

---

## Key Architectural Decisions (ADRs)

### ADR 07: Standardized Shell-Bridge Execution

**Decision:** The Orchestrator interacts with the agentic environment *exclusively* via `./scripts/devcontainer-opencode.sh`.

**Rationale:** Reusing the shell scripts ensures perfect environment parity between AI agent and human developer. Avoids "Configuration Drift."

**Consequence:** Python code remains lightweight (logic/state) while Shell handles "Heavy Lifting" (container orchestration).

### ADR 08: Polling-First Resiliency Model

**Decision:** Sentinel uses polling as primary discovery; Webhooks are an optimization.

**Rationale:** Webhooks are "Fire and Forget." If the server is down during an event, it's lost forever. Polling ensures "State Reconciliation" on every restart.

### ADR 09: Provider-Agnostic Interface Layer

**Decision:** All queue interactions abstracted behind `ITaskQueue` interface.

**Rationale:** Enables future support for Linear, Notion, or SQL queues without rewriting orchestrator logic.

---

## Data Flow (Happy Path)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. STIMULUS                                                         │
│     User opens GitHub Issue with [Application Plan] template         │
│                           │                                          │
│                           ▼                                          │
│  2. NOTIFICATION                                                     │
│     GitHub Webhook → Notifier (FastAPI)                              │
│                           │                                          │
│                           ▼                                          │
│  3. TRIAGE                                                           │
│     Notifier verifies signature → adds agent:queued label            │
│                           │                                          │
│                           ▼                                          │
│  4. CLAIM                                                            │
│     Sentinel poller detects label → assigns issue → in-progress      │
│                           │                                          │
│                           ▼                                          │
│  5. SYNC                                                             │
│     Sentinel runs git clone/pull on target repo                      │
│                           │                                          │
│                           ▼                                          │
│  6. ENVIRONMENT CHECK                                                │
│     devcontainer-opencode.sh up                                      │
│                           │                                          │
│                           ▼                                          │
│  7. DISPATCH                                                         │
│     devcontainer-opencode.sh prompt "Run workflow: create-app-plan"  │
│                           │                                          │
│                           ▼                                          │
│  8. EXECUTION                                                        │
│     Worker (Opencode) reads issue → creates child Epic issues        │
│                           │                                          │
│                           ▼                                          │
│  9. FINALIZE                                                         │
│     Sentinel removes in-progress → adds agent:success                │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Network Isolation

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOST NETWORK                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               SENTINEL / NOTIFIER                          │ │
│  │               (Python Services)                            │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │ Shell Bridge                          │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            ISOLATED DOCKER BRIDGE NETWORK                   │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              WORKER CONTAINER                         │  │ │
│  │  │  • 2 CPUs, 4GB RAM limits                            │  │ │
│  │  │  • No host subnet access                             │  │ │
│  │  │  • Ephemeral credentials (env vars)                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Credential Lifecycle

1. Sentinel generates/refreshes GitHub Installation Token
2. Token injected as temporary environment variable
3. Worker container receives token (in-memory only)
4. Token destroyed when container exits

### Credential Scrubbing

All worker output is piped through `scrub_secrets()` before posting to GitHub:

```python
# Patterns scrubbed:
ghp_*          # GitHub PAT (classic)
ghs_*          # GitHub App installation token
gho_*          # GitHub OAuth token
github_pat_*   # GitHub fine-grained PAT
Bearer ...     # Bearer tokens
sk-*           # OpenAI-style API keys
*.zhipu*       # ZhipuAI keys
```

---

## Self-Bootstrapping Lifecycle

```
┌────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP STAGES                             │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Stage 0: SEEDING                                               │
│  └─▶ Developer clones template repo                             │
│      └─▶ Plan docs added to /docs                               │
│                                                                 │
│  Stage 1: MANUAL LAUNCH                                         │
│  └─▶ Developer runs devcontainer-opencode.sh up                 │
│                                                                 │
│  Stage 2: PROJECT SETUP                                         │
│  └─▶ orchestrate-project-setup workflow runs                    │
│      └─▶ Agent configures env vars, indexes codebase            │
│                                                                 │
│  Stage 3: HANDOVER                                              │
│  └─▶ Developer starts sentinel.py service                       │
│      └─▶ System builds Phase 2 & 3 via its own orchestration    │
│                                                                 │
│  Stage 4: AUTONOMOUS PHASE                                      │
│  └─▶ AI manages all further development via GitHub Issues       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
                    GitHub
                      │
        ┌─────────────┼─────────────┐
        │ Webhooks    │ REST API    │ Labels/Issues
        ▼             │             ▲
┌───────────────┐     │     ┌───────────────┐
│   NOTIFIER    │     │     │   SENTINEL    │
│  (FastAPI)    │     │     │  (Async Py)   │
└───────┬───────┘     │     └───────┬───────┘
        │             │             │
        │ WorkItem    │             │ Shell Bridge
        ▼             │             ▼
┌───────────────┐     │     ┌───────────────┐
│  GitHubQueue  │─────┴────▶│ devcontainer- │
│  (ITaskQueue) │           │ opencode.sh   │
└───────────────┘           └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │    WORKER     │
                            │  (DevContainer│
                            │  + opencode)  │
                            └───────────────┘
```

---

## Unified Data Model

All components share a single `WorkItem` model defined in `src/models/work_item.py`:

```python
class TaskType(str, Enum):
    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    BUGFIX = "BUGFIX"

class WorkItemStatus(str, Enum):
    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    RECONCILING = "agent:reconciling"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    STALLED_BUDGET = "agent:stalled-budget"

class WorkItem(BaseModel):
    id: str
    issue_number: int
    source_url: str
    context_body: str
    target_repo_slug: str
    task_type: TaskType
    status: WorkItemStatus
    node_id: str
```

---

## References

- [Technology Stack](./tech-stack.md)
- [Development Plan v4.2](./OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Specification v1.2](./OS-APOW%20Implementation%20Specification%20v1.2.md)
- [Architecture Guide v3.2](./OS-APOW%20Architecture%20Guide%20v3.2.md)
