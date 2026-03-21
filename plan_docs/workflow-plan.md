# Workflow Execution Plan: project-setup

**Generated:** 2026-03-21
**Workflow File:** `ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`
**Repository:** intel-agency/workflow-orchestration-queue-india38-a

---

## 1. Overview

### Workflow Name
**project-setup** — Dynamic workflow for initiating a new repository and establishing project infrastructure.

### Project Description
**workflow-orchestration-queue (OS-APOW)** is a headless agentic orchestration platform that transforms interactive AI coding into an autonomous background production service. It leverages GitHub Issues as "Execution Orders" that are autonomously fulfilled by specialized AI agents, moving from a passive co-pilot role to a persistent, event-driven infrastructure.

### Total Assignments
- **Main Script:** 6 assignments
- **Pre-script-begin Event:** 1 assignment (create-workflow-plan — already executing)
- **Post-assignment-complete Event:** 2 assignments per main assignment

### High-Level Summary
This workflow initializes the repository, creates the application plan, establishes project structure, generates documentation, and performs a comprehensive debrief. It transforms the seeded template repository into a fully configured development environment ready for autonomous agent operation.

---

## 2. Project Context Summary

### Key Facts from plan_docs/

| Category | Details |
|----------|---------|
| **Project Name** | workflow-orchestration-queue (OS-APOW) |
| **Primary Language** | Python 3.12+ |
| **Framework** | FastAPI (webhook receiver), Uvicorn (ASGI server) |
| **Package Manager** | uv (Rust-based, fast dependency management) |
| **Containerization** | Docker, Docker Compose, DevContainers |
| **Target Repo** | `intel-agency/workflow-orchestration-queue` (configurable via env vars) |
| **Architecture** | 4-Pillar: Ear (Notifier), State (Queue), Brain (Sentinel), Hands (Worker) |

### Technology Stack
- **Backend:** Python 3.12+, FastAPI, Uvicorn, Pydantic, HTTPX
- **Package Management:** uv, pyproject.toml
- **Containerization:** Docker, Docker Compose, DevContainers
- **Agent Runtime:** opencode CLI, ZhipuAI GLM models
- **MCP Servers:** sequential-thinking, memory
- **Infrastructure:** GitHub Actions, GitHub App webhooks, GHCR

### Key Constraints
- **Security:** HMAC webhook verification, credential scrubbing, network isolation
- **Concurrency:** Assign-then-verify locking pattern using GitHub Assignees
- **Resiliency:** Polling-first with jittered exponential backoff
- **State:** "Markdown as a Database" — GitHub Issues/Labels for persistence

### Known Risks (from Plan Review)
1. **I-1:** Divergent WorkItem models between sentinel and notifier — needs unification
2. **I-2:** Race condition in task claiming — needs assign-then-verify implementation
3. **I-6:** No heartbeat implementation — long-running tasks appear frozen
4. **I-10:** No environment reset between tasks — state bleed risk

### Repository State (Pre-Workflow)
- Template cloned from `workflow-orchestration-queue-india38-a`
- Plan docs seeded in `plan_docs/` directory
- Reference implementations provided: `notifier_service.py`, `orchestrator_sentinel.py`, `src/` modules
- DevContainer infrastructure exists but not yet configured for this specific project

---

## 3. Assignment Execution Plan

### Assignment 1: init-existing-repository

| Field | Content |
|-------|---------|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Initialize the repository with GitHub Project, labels, milestones, and workspace configuration |
| **Key Acceptance Criteria** | • PR and new branch created (must be first) • GitHub Project created for issue tracking • Labels imported from `.github/.labels.json` • Workspace/devcontainer files renamed to match project name |
| **Project-Specific Notes** | Project name is `workflow-orchestration-queue`. Branch should be `dynamic-workflow-project-setup`. Manual step required for GitHub Project creation after first orchestrator run. |
| **Prerequisites** | GitHub CLI installed and authenticated with `repo`, `project`, `read:project`, `read:user`, `user:email` scopes |
| **Dependencies** | None (first assignment) |
| **Risks / Challenges** | • DevContainer image may not exist on first run — manual project creation required • GitHub App permissions may need adjustment • `.github/.labels.json` must exist in repo |
| **Events** | None declared |

---

### Assignment 2: create-app-plan

| Field | Content |
|-------|---------|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Create a comprehensive application plan documented as a GitHub Issue, based on the application template and supporting documents |
| **Key Acceptance Criteria** | • Application template analyzed and understood • Plan documented in GitHub Issue using template • Milestones created and issues linked • `implementation:ready` label applied • Planning only — no code implementation |
| **Project-Specific Notes** | Application template is in `plan_docs/` with Architecture Guide, Development Plan, Implementation Spec, Plan Review, and Simplification Report. Key phases: 0 (Seeding), 1 (Sentinel MVP), 2 (Ear/Webhooks), 3 (Deep Orchestration). |
| **Prerequisites** | Repository initialized (Assignment 1 complete), Application template exists in `plan_docs/` |
| **Dependencies** | Outputs from `init-existing-repository`: labels, project, branch |
| **Risks / Challenges** | • Complex 4-phase architecture may require clarification • Multiple plan docs need synthesis • Phase 3 features should be moved to "Future Work" appendix (Simplification Report S-9) |
| **Events** | `pre-assignment-begin`: gather-context • `on-assignment-failure`: recover-from-error • `post-assignment-complete`: report-progress |

---

### Assignment 3: create-project-structure

| Field | Content |
|-------|---------|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create the actual project structure and scaffolding based on the application plan |
| **Key Acceptance Criteria** | • Solution/project structure created • Docker and docker-compose.yml configured • CI/CD pipeline structure established • Documentation structure created • Repository summary document created |
| **Project-Specific Notes** | Python project with `pyproject.toml`, `uv` for dependencies. Structure: `src/` (main code), `tests/`, `scripts/` (shell bridge), `local_ai_instruction_modules/`. Key files: `notifier_service.py`, `orchestrator_sentinel.py`, `src/models/work_item.py`, `src/queue/github_queue.py`. |
| **Prerequisites** | Application plan complete (Assignment 2), tech stack documented |
| **Dependencies** | Application plan from `create-app-plan`, milestones from Assignment 2 |
| **Risks / Challenges** | • Reference implementations exist but need proper integration • Healthcheck commands should use Python stdlib, not curl • Editable installs (`uv pip install -e .`) require source directory to be copied first |
| **Events** | None declared |

---

### Assignment 4: create-repository-summary

| Field | Content |
|-------|---------|
| **Assignment** | `create-repository-summary`: Create Repository Summary |
| **Goal** | Create `.ai-repository-summary.md` file at repository root with build/test commands, project layout, and agent onboarding information |
| **Key Acceptance Criteria** | • `.ai-repository-summary.md` exists at repo root • Build, test, lint commands documented and validated • Project layout documented • File under 32K tokens (preferably 8-16K) |
| **Project-Specific Notes** | Commands: `uv sync` (install), `uv run pytest` (test), `uv run ruff check` (lint). Project uses `pyproject.toml`, no `global.json`. DevContainer with opencode CLI, ZhipuAI integration. |
| **Prerequisites** | Project structure created (Assignment 3), build/test commands validated |
| **Dependencies** | Project structure from `create-project-structure` |
| **Risks / Challenges** | • Build commands must be validated by running them • Must not duplicate entire README.md content • Should cross-reference with plan docs |
| **Events** | None declared |

---

### Assignment 5: create-agents-md-file

| Field | Content |
|-------|---------|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create `AGENTS.md` file at repository root following the open [agents.md](https://agents.md/) specification, optimized for AI coding agents |
| **Key Acceptance Criteria** | • `AGENTS.md` exists at repo root • Setup/build/test commands validated • Code style and conventions documented • Project structure section included • PR/commit guidelines documented |
| **Project-Specific Notes** | Complements README.md (human-focused) and `.ai-repository-summary.md` (Copilot-focused). Should include: Python 3.12+ conventions, Pydantic models, async patterns, credential scrubbing rules, shell-bridge usage. |
| **Prerequisites** | Project structure created, build commands validated |
| **Dependencies** | Repository summary from `create-repository-summary`, project structure from Assignment 3 |
| **Risks / Challenges** | • Must not duplicate README.md content • All commands must be validated by running them • Must be agent-focused, not human-focused |
| **Events** | None declared |

---

### Assignment 6: debrief-and-document

| Field | Content |
|-------|---------|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Capture key learnings, insights, and areas for improvement; document in structured format |
| **Key Acceptance Criteria** | • Detailed report created using structured template • All deviations from assignment documented • Report committed to repo • Execution trace saved as `debrief-and-document/trace.md` |
| **Project-Specific Notes** | Should capture: issues with WorkItem model divergence (I-1), race condition fixes (I-2), heartbeat implementation needs (I-6), environment reset needs (I-10), simplification decisions (S-3 through S-11). |
| **Prerequisites** | All main assignments complete |
| **Dependencies** | All outputs from Assignments 1-5 |
| **Risks / Challenges** | • Must document all deviations honestly • Execution trace must capture actual commands run and outputs • Report must be reviewed by stakeholder |
| **Events** | None declared |

---

## 4. Event Assignments

### pre-script-begin Event (Currently Executing)

| Field | Content |
|-------|---------|
| **Assignment** | `create-workflow-plan`: Create Workflow Plan |
| **Goal** | Create comprehensive workflow execution plan before any other assignments begin |
| **Key Acceptance Criteria** | • Dynamic workflow file read completely • Every referenced assignment traced and read • All `plan_docs/` files read and summarized • Plan committed as `plan_docs/workflow-plan.md` |
| **Notes** | This is the current assignment. It does NOT execute other assignments — only plans. |

### post-assignment-complete Event (Fires After Each Main Assignment)

| Assignment | Goal | Key Criteria |
|------------|------|--------------|
| `validate-assignment-completion` | Validate that completed assignment met all acceptance criteria | • All required files exist • Verification commands pass • Validation report created • Pass/fail status determined |
| `report-progress` | Report progress and checkpoint state after each step | • Progress report generated • Step outputs captured • Workflow state saved for recovery |

---

## 5. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        project-setup WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────┐                                            │
│  │  pre-script-begin           │                                            │
│  │  ┌─────────────────────┐    │                                            │
│  │  │ create-workflow-plan│────┼──► plan_docs/workflow-plan.md             │
│  │  └─────────────────────┘    │                                            │
│  └─────────────────────────────┘                                            │
│               │                                                              │
│               ▼                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  MAIN SCRIPT                                                        │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────┐    ┌────────────────────────────┐      │    │
│  │  │ 1. init-existing-repo   │───►│ post-assignment-complete   │      │    │
│  │  └─────────────────────────┘    │  • validate-completion     │      │    │
│  │               │                  │  • report-progress         │      │    │
│  │               ▼                  └────────────────────────────┘      │    │
│  │  ┌─────────────────────────┐    ┌────────────────────────────┐      │    │
│  │  │ 2. create-app-plan      │───►│ post-assignment-complete   │      │    │
│  │  └─────────────────────────┘    │  • validate-completion     │      │    │
│  │               │                  │  • report-progress         │      │    │
│  │               ▼                  └────────────────────────────┘      │    │
│  │  ┌─────────────────────────┐    ┌────────────────────────────┐      │    │
│  │  │ 3. create-project-      │───►│ post-assignment-complete   │      │    │
│  │  │    structure            │    │  • validate-completion     │      │    │
│  │  └─────────────────────────┘    │  • report-progress         │      │    │
│  │               │                  └────────────────────────────┘      │    │
│  │               ▼                  ┌────────────────────────────┐      │    │
│  │  ┌─────────────────────────┐    │ post-assignment-complete   │      │    │
│  │  │ 4. create-repository-   │───►│  • validate-completion     │      │    │
│  │  │    summary              │    │  • report-progress         │      │    │
│  │  └─────────────────────────┘    └────────────────────────────┘      │    │
│  │               │                  ┌────────────────────────────┐      │    │
│  │               ▼                  │ post-assignment-complete   │      │    │
│  │  ┌─────────────────────────┐    │  • validate-completion     │      │    │
│  │  │ 5. create-agents-md-file│───►│  • report-progress         │      │    │
│  │  └─────────────────────────┘    └────────────────────────────┘      │    │
│  │               │                  ┌────────────────────────────┐      │    │
│  │               ▼                  │ post-assignment-complete   │      │    │
│  │  ┌─────────────────────────┐    │  • validate-completion     │      │    │
│  │  │ 6. debrief-and-document │───►│  • report-progress         │      │    │
│  │  └─────────────────────────┘    └────────────────────────────┘      │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Dependency Graph

```
init-existing-repository
         │
         ├──► create-app-plan
         │         │
         │         └──► create-project-structure
         │                   │
         │                   ├──► create-repository-summary
         │                   │         │
         │                   │         └──► create-agents-md-file
         │                   │                   │
         │                   │                   └──► debrief-and-document
         │                   │
         │                   └───────────────────┘
         │
         └───────────────────────────────────────┘

Each assignment also triggers:
  post-assignment-complete
    ├── validate-assignment-completion
    └── report-progress
```

---

## 7. Open Questions

Before proceeding with workflow execution, the following questions should be addressed:

1. **GitHub Project Creation:** The `init-existing-repository` assignment notes that GitHub Project creation is a manual step. Should this be:
   - Performed manually before the workflow continues?
   - Skipped for now and added as a follow-up task?

2. **Reference Implementation Files:** The `plan_docs/` directory contains reference implementations (`notifier_service.py`, `orchestrator_sentinel.py`, `src/` modules). Should these be:
   - Moved to `src/` during `create-project-structure`?
   - Treated as reference only and re-implemented from scratch?
   - Used as the starting point with modifications?

3. **Simplification Report Decisions:** Several simplifications were marked as IMPLEMENTED in the Simplification Report (S-3, S-4, S-5, S-6, S-7, S-8, S-9, S-10, S-11). Should the `create-project-structure` assignment:
   - Start from the reference implementations and apply these simplifications?
   - Build fresh implementations that incorporate these decisions from the start?

4. **Environment Variables:** The sentinel requires `GITHUB_TOKEN`, `GITHUB_ORG`, `GITHUB_REPO`, and optionally `SENTINEL_BOT_LOGIN`. Should `.env.example` be created during `create-project-structure`?

5. **Testing Strategy:** The plan docs mention test cases (TC-01 through TC-04) but no test framework is specified. Should `pytest` be used (as implied by Python stack)?

---

## 8. Files Read

### Dynamic Workflow
- `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`

### Workflow Assignments
- `init-existing-repository.md`
- `create-app-plan.md`
- `create-project-structure.md`
- `create-repository-summary.md` (embedded in create-repository-summary response)
- `create-agents-md-file.md`
- `debrief-and-document.md`
- `validate-assignment-completion.md`
- `report-progress.md`
- `create-workflow-plan.md`

### Plan Documents
- `plan_docs/OS-APOW Architecture Guide v3.2.md`
- `plan_docs/OS-APOW Development Plan v4.2.md`
- `plan_docs/OS-APOW Implementation Specification v1.2.md`
- `plan_docs/OS-APOW Plan Review.md`
- `plan_docs/OS-APOW Simplification Report v1.md`
- `plan_docs/notifier_service.py`
- `plan_docs/orchestrator_sentinel.py`
- `plan_docs/src/` directory structure

---

## 9. Summary

This workflow execution plan covers the complete `project-setup` dynamic workflow for the workflow-orchestration-queue (OS-APOW) project. The workflow will:

1. Initialize the repository with GitHub Project, labels, and workspace configuration
2. Create a comprehensive application plan documented as a GitHub Issue
3. Establish the project structure with Python/FastAPI scaffolding
4. Generate repository documentation (`.ai-repository-summary.md`, `AGENTS.md`)
5. Perform a thorough debrief capturing learnings and deviations

**Total Main Assignments:** 6
**Total Event Assignments:** 3 (1 pre-script + 2 post-assignment)
**Estimated Duration:** Multiple hours depending on complexity of plan synthesis and structure creation

**Approval Status:** ⏳ Pending stakeholder approval
