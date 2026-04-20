# Workflow Execution Plan: project-setup

**Repository:** `intel-agency/workflow-orchestration-queue-india38-a`
**Branch:** `dynamic-workflow-project-setup`
**Plan Created:** 2026-04-20

---

## 1. Overview

| Field | Value |
|-------|-------|
| **Dynamic Workflow** | `project-setup` |
| **Workflow File** | `ai-workflow-assignments/dynamic-workflows/project-setup.md` (remote canonical) |
| **Project Name** | workflow-orchestration-queue |
| **Total Main Assignments** | 6 |
| **Event Assignments** | 3 (create-workflow-plan, validate-assignment-completion, report-progress) |
| **Post-Script Event** | Apply `orchestration:plan-approved` label |

### Project Description

**workflow-orchestration-queue** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous Execution Orders. It replaces the traditional "human-in-the-loop" AI coding paradigm with a persistent, event-driven infrastructure where AI agents autonomously clone repositories, generate code, run tests, and submit Pull Requests — all triggered by labeling a GitHub Issue.

The system is built on a 4-pillar architecture:
- **The Ear** (Notifier) — FastAPI webhook receiver for event-driven task intake
- **The State** (Queue) — GitHub Issues as a distributed task state machine ("Markdown as a Database")
- **The Brain** (Sentinel) — Persistent Python polling service for task discovery, claiming, and dispatch
- **The Hands** (Worker) — DevContainer-based LLM execution environment via shell-bridge

### High-Level Workflow Summary

The `project-setup` workflow initializes the repository, creates an application plan from the seeded plan documents, scaffolds the project structure, generates an `AGENTS.md` file, captures debrief learnings, and merges the setup PR. This is a **planning + scaffolding** workflow — no feature implementation occurs.

---

## 2. Project Context Summary

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.12+ |
| **Web Framework** | FastAPI + Uvicorn |
| **Data Validation** | Pydantic v2 |
| **HTTP Client** | httpx (async) |
| **Package Manager** | uv (Rust-based) |
| **Dependency Lock** | uv.lock |
| **Containerization** | Docker + DevContainer |
| **Agent Runtime** | opencode CLI (v1.2.24) |
| **AI Models** | ZhipuAI GLM-5 (primary), others optional |
| **Shell Scripts** | PowerShell Core (pwsh) + Bash |
| **CI/CD** | GitHub Actions |
| **Project Management** | GitHub Issues + Labels + Milestones |

### Repository Details

- **Owner:** `intel-agency`
- **Repo:** `workflow-orchestration-queue-india38-a`
- **Type:** GitHub template clone (from `intel-agency/workflow-orchestration-queue-india38-a`)
- **Default Branch:** `main`
- **Working Branch:** `dynamic-workflow-project-setup`

### Key Constraints

1. **SHA Pinning Directive:** All GitHub Actions workflows MUST pin actions to specific commit SHAs (not version tags like `@v3` or `@main`).
2. **Self-Bootstrapping System:** The project is designed to build itself — Phase 1 (Sentinel) is manually seeded, then the system uses its own orchestration to build Phases 2 and 3.
3. **Python-First:** No `.NET` or `global.json` — all dependency management via `pyproject.toml` and `uv`.
4. **Template Repository:** This repo was cloned from a template. Files like `ai-new-app-template.md` may need renaming to match the project name.
5. **Reference Implementation Included:** `plan_docs/` contains scaffold code (`orchestrator_sentinel.py`, `notifier_service.py`, `src/`) that serves as reference, not as the final implementation.

### Key Plan Documents

| Document | Purpose |
|----------|---------|
| OS-APOW Development Plan v4.2 | Phased roadmap, user stories, risk assessment |
| OS-APOW Architecture Guide v3.2 | System diagrams, ADRs, data flow, security model |
| OS-APOW Implementation Specification v1.2 | Detailed requirements, tech stack, test cases |
| OS-APOW Plan Review | Code review findings (I-1 through I-10), recommendations (R-1 through R-9) |
| OS-APOW Simplification Report v1 | Applied simplifications (S-3 through S-11 implemented) |
| orchestrator_sentinel.py | Reference implementation of the Sentinel Orchestrator |
| notifier_service.py | Reference implementation of the webhook Notifier |
| interactive-report.html | Presentation dashboard for the architecture |
| src/models/work_item.py | Unified data model (TaskType, WorkItemStatus, WorkItem, scrub_secrets) |
| src/queue/github_queue.py | Consolidated GitHub queue (ITaskQueue ABC + GitHubQueue) |

---

## 3. Assignment Execution Plan

### Assignment 1: `create-workflow-plan` (Pre-Script Event)

| Field | Content |
|-------|---------|
| **Assignment** | `create-workflow-plan`: Create Workflow Plan |
| **Goal** | Create a comprehensive workflow execution plan for the dynamic workflow before any other assignments begin executing. |
| **Key Acceptance Criteria** | Dynamic workflow fully read; all assignments traced; all plan_docs read; plan document produced with each assignment's short ID, goal, and acceptance criteria; plan committed to `plan_docs/workflow-plan.md`. |
| **Project-Specific Notes** | This IS the current assignment. The plan_docs directory contains exceptionally detailed specifications (Development Plan, Architecture Guide, Implementation Spec, Plan Review, Simplification Report) plus reference Python implementations. The project is a Python-based headless orchestration system — not a typical CRUD application. |
| **Prerequisites** | Access to remote canonical repository for assignment files; `plan_docs/` directory exists with seeded documents. |
| **Dependencies** | None — this is the first assignment executed (pre-script event). |
| **Risks / Challenges** | Plan documents are extensive (1000+ lines total). The reference code in plan_docs is scaffold, not final — later assignments must not treat it as production-ready. |
| **Events** | `pre-script-begin` — fires before the main script assignments begin. |

---

### Assignment 2: `init-existing-repository`

| Field | Content |
|-------|---------|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Initialize the repository with proper GitHub configuration: branch, labels, project board, branch protection ruleset, and a setup PR. |
| **Key Acceptance Criteria** | (0) Branch `dynamic-workflow-project-setup` created; (1) Branch protection ruleset imported; (2) GitHub Project created for issue tracking; (3) Project linked to repo with columns (Not Started, In Progress, In Review, Done); (4) Labels imported from `.github/.labels.json`; (5) Filenames changed to match project name; (6) PR created from branch to `main`. |
| **Project-Specific Notes** | The repo is a template clone that already has `.github/.labels.json` and `.github/protected-branches_ruleset.json`. The devcontainer name in `.devcontainer/devcontainer.json` should be renamed to `workflow-orchestration-queue-india38-a-devcontainer`. The workspace file `ai-new-app-template.code-workspace` should be renamed to `workflow-orchestration-queue-india38-a.code-workspace`. Branch protection requires `GH_ORCHESTRATION_AGENT_TOKEN` (PAT with `administration: write` scope). |
| **Prerequisites** | GitHub authentication with `repo`, `project`, `read:project`, `read:user`, `user:email` scopes. `administration: write` scope on the repo for ruleset import. |
| **Dependencies** | None — this is the first main assignment. |
| **Risks / Challenges** | (1) Branch protection import may fail if `GH_ORCHESTRATION_AGENT_TOKEN` is not set or lacks `administration: write` scope — the assignment says to stop and report, not silently skip. (2) GitHub Project creation may fail if OAuth scopes are insufficient. (3) The repo may already have some configuration from the template — steps must be idempotent where possible. |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

### Assignment 3: `create-app-plan`

| Field | Content |
|-------|---------|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Analyze the application template and supporting documents in `plan_docs/` to create a comprehensive application plan documented as a GitHub Issue, with milestones created and linked. |
| **Key Acceptance Criteria** | (1) Application template thoroughly analyzed; (2) Plan's project structure documented; (3) Template from Appendix A used; (4) Detailed breakdown of all phases; (5) All required components and dependencies planned; (6) Specified tech stack followed (Python 3.12+, FastAPI, Pydantic, httpx, uv); (7) Mandatory requirements addressed (testing, docs, containerization); (8) Risks and mitigations identified; (9) Plan documented in an issue; (10) Milestones created and issues linked; (11) Issue added to GitHub Project; (12) Labels applied (`planning`, `documentation`). |
| **Project-Specific Notes** | The `plan_docs/` directory already contains extremely detailed specifications — Development Plan v4.2, Architecture Guide v3.2, Implementation Spec v1.2, Plan Review, and Simplification Report. The "application template" is effectively the combination of these documents. There is no single `ai-new-app-template.md` file; the primary app spec is the Implementation Specification. The plan should cover Phase 0 (Seeding), Phase 1 (Sentinel MVP), Phase 2 (Ear/Webhook), and Phase 3 (Deep Orchestration) as documented. Key risks from the Plan Review (I-1 through I-10) and simplifications already applied (S-3 through S-11) must be incorporated. Tech stack document should go in `plan_docs/tech-stack.md` and architecture in `plan_docs/architecture.md`. |
| **Prerequisites** | `init-existing-repository` completed — labels and project board exist. |
| **Dependencies** | Output of `init-existing-repository` (labels available, project board created). |
| **Risks / Challenges** | (1) The plan docs are very detailed — the agent must avoid simply copying them verbatim and instead create a structured, actionable implementation plan. (2) The reference code in `plan_docs/orchestrator_sentinel.py` and `notifier_service.py` has known issues (Plan Review I-1 through I-10) that the plan must address. (3) Phase 3 features should be noted as future work, not included in the MVP plan (per Simplification Report S-9). (4) This is PLANNING ONLY — no code or project files should be created. |
| **Events** | `pre-assignment-begin` → `gather-context`; `on-assignment-failure` → `recover-from-error`; `post-assignment-complete` → `report-progress` |

---

### Assignment 4: `create-project-structure`

| Field | Content |
|-------|---------|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create the actual project structure and scaffolding for the workflow-orchestration-queue application based on the application plan. |
| **Key Acceptance Criteria** | (1) Solution/project structure created per the plan's tech stack (Python + uv); (2) All required project files and directories established; (3) Initial configuration files created (pyproject.toml, Dockerfile, docker-compose.yml, .python-version); (4) Basic CI/CD pipeline structure established; (5) Documentation structure created (README.md, docs/); (6) Development environment configured and validated; (7) Initial commit made with scaffolding; (8) Stakeholder approval obtained; (9) Repository summary document created (`.ai-repository-summary.md`); (10) All GitHub Actions pinned to SHA. |
| **Project-Specific Notes** | The target structure should follow the Implementation Spec's project layout: `pyproject.toml` at root, `src/` with `notifier_service.py`, `orchestrator_sentinel.py`, `models/work_item.py`, `queue/github_queue.py`. The reference code in `plan_docs/` can serve as a starting point but must incorporate all Plan Review fixes (I-1 through I-10, R-1 through R-9). Dockerfile should use Python 3.12 base image with uv installed. Health check commands must NOT use curl (use Python stdlib instead). No `global.json` needed (not .NET). `pyproject.toml` should declare dependencies: fastapi, uvicorn, pydantic, httpx. Tests should use pytest. |
| **Prerequisites** | `create-app-plan` completed — application plan exists as an issue and `plan_docs/tech-stack.md` and `plan_docs/architecture.md` are available. |
| **Dependencies** | Output of `create-app-plan` (plan issue, milestones, tech-stack.md, architecture.md). |
| **Risks / Challenges** | (1) The reference code in `plan_docs/src/` has intentional simplifications — agents must not blindly copy but instead create proper implementations. (2) Docker health checks must avoid curl (use Python urllib instead). (3) Editable installs (`uv pip install -e .`) require the source directory to be copied before the install command in the Dockerfile. (4) CI workflows must use SHA-pinned actions. (5) The `.ai-repository-summary.md` must be created per the referenced instructions. |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

### Assignment 5: `create-agents-md-file`

| Field | Content |
|-------|---------|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create a comprehensive `AGENTS.md` file at the repository root that provides AI coding agents with the context and instructions they need to work effectively on the project. |
| **Key Acceptance Criteria** | (1) `AGENTS.md` exists at repository root; (2) Contains project overview section; (3) Contains setup/build/test commands that have been verified; (4) Contains code style and conventions section; (5) Contains project structure/directory layout section; (6) Contains testing instructions; (7) Contains PR/commit guidelines; (8) Written in standard Markdown with agent-focused language; (9) Commands validated by running them; (10) Committed and pushed; (11) Stakeholder approval obtained. |
| **Project-Specific Notes** | The AGENTS.md should reference the Python/uv tech stack, the 4-pillar architecture, the `src/` directory layout, and the test/devcontainer infrastructure already in the repo. Build commands will use `uv` (e.g., `uv run pytest`, `uv run uvicorn`). The existing `AGENTS.md` in the repo root (from the template) targets the orchestration system itself — it must be replaced with project-specific content for the workflow-orchestration-queue application. Cross-reference with README.md and plan docs but don't duplicate. |
| **Prerequisites** | `create-project-structure` completed — project scaffolding exists, build/test tooling is in place. |
| **Dependencies** | Output of `create-project-structure` (project files, directory structure, build/test commands). |
| **Risks / Challenges** | (1) Build/test commands must be verified to actually work — the agent must run them, not just document assumed commands. (2) The AGENTS.md must replace the existing template version, not coexist with it. (3) Must be concise and agent-optimized — avoid verbose prose. |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

### Assignment 6: `debrief-and-document`

| Field | Content |
|-------|---------|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Perform a comprehensive debriefing that captures key learnings, insights, deviations, and areas for improvement from the project setup workflow. |
| **Key Acceptance Criteria** | (1) Detailed report created following the structured 12-section template; (2) Report in .md format; (3) All sections complete; (4) All deviations documented; (5) Report reviewed and approved; (6) Committed and pushed; (7) Execution trace saved. |
| **Project-Specific Notes** | The debrief should capture any issues encountered during repository initialization, plan creation, project scaffolding, and AGENTS.md generation. It should note the self-bootstrapping nature of the project and any unique challenges that arose from building an "orchestration system that orchestrates itself." Action items for Phase 1 implementation should be identified. The execution trace should be saved to `debrief-and-document/trace.md`. |
| **Prerequisites** | All prior main assignments completed. |
| **Dependencies** | Outputs from all prior assignments (repository state, plan issue, project structure, AGENTS.md). |
| **Risks / Challenges** | (1) The debrief must be thorough — all 12 sections required. (2) Deviations from any assignment must be explicitly documented. (3) Plan-impacting findings must be flagged as ACTION ITEMS. (4) Must recommend filing issues for any newly discovered required work. |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

### Assignment 7: `pr-approval-and-merge`

| Field | Content |
|-------|---------|
| **Assignment** | `pr-approval-and-merge`: PR Approval and Merge |
| **Goal** | Complete the full PR approval and merge process for the setup PR created during `init-existing-repository`. |
| **Key Acceptance Criteria** | (CI) All required CI checks pass with remediation loop (up to 3 attempts); (Review) Code review delegated to `code-reviewer` subagent; (Comments) All review comments resolved per `ai-pr-comment-protocol.md`; (Approval) Stakeholder approval obtained; (Merge) PR merged; (Post-merge) Source branch deleted, related issues closed. |
| **Project-Specific Notes** | The `$pr_num` input comes from the PR created during `init-existing-repository` (recorded as `#initiate-new-repository.init-existing-repository`). Per the project-setup workflow, this is an automated setup PR — self-approval by the orchestrator is acceptable. No human stakeholder approval is required. However, the CI remediation loop MUST still be executed. On successful merge: delete the `dynamic-workflow-project-setup` branch and close any related setup issues. Must read and follow `ai-pr-comment-protocol.md` before beginning. |
| **Prerequisites** | All prior main assignments completed and committed to the PR branch. |
| **Dependencies** | Output of `init-existing-repository` (`$pr_num`); all subsequent assignment outputs committed to the PR branch. |
| **Risks / Challenges** | (1) CI checks may fail due to the new project scaffolding — the remediation loop must handle this. (2) Auto-reviewer bots (Copilot, CodeQL) may post comments that need resolution. (3) All local changes must be committed and pushed before merge to avoid data loss. (4) Branch deletion after merge will remove the working branch — ensure everything is merged. |
| **Events** | `post-assignment-complete` → `validate-assignment-completion`, `report-progress` |

---

### Event Assignment A: `validate-assignment-completion`

| Field | Content |
|-------|---------|
| **Assignment** | `validate-assignment-completion`: Validate Assignment Completion |
| **Goal** | Validate that each completed assignment has successfully met all its acceptance criteria. Executed after every main assignment via the `post-assignment-complete` event. |
| **Key Acceptance Criteria** | (1) All required files exist; (2) All verification commands pass; (3) Validation report created; (4) Pass/fail status determined; (5) Remediation steps provided if failed. |
| **Project-Specific Notes** | Must be delegated to an independent QA agent (not the one who implemented the assignment). For Python assignments, run `uv run pytest`, `uv run ruff check`, etc. For GitHub operations, verify via `gh api` queries. Validation reports go to `docs/validation/`. |
| **Prerequisites** | A main assignment has just completed. |
| **Dependencies** | The just-completed assignment's outputs. |
| **Risks / Challenges** | (1) Must be objective — no self-validation. (2) Must check actual GitHub state, not just local files. (3) Must be fast (< 5 minutes per validation). |
| **Events** | None — this is itself an event handler. |

---

### Event Assignment B: `report-progress`

| Field | Content |
|-------|---------|
| **Assignment** | `report-progress`: Report Progress |
| **Goal** | Generate structured progress reports, capture outputs, validate acceptance criteria, and create checkpoints after each workflow step. |
| **Key Acceptance Criteria** | (1) Structured progress report generated; (2) All step outputs captured; (3) Expected outputs validated; (4) Workflow state saved for checkpoint recovery; (5) Action items filed as GitHub issues. |
| **Project-Specific Notes** | Reports should track progress against the 6 main assignments. Deviations and findings must be documented. Plan-impacting discoveries must be flagged. Any action items must be filed as GitHub issues (not left as text notes). |
| **Prerequisites** | A main assignment has just completed (and been validated). |
| **Dependencies** | The just-completed assignment's outputs and validation results. |
| **Risks / Challenges** | (1) Action items MUST be filed as GitHub issues — this is non-negotiable per the assignment spec. (2) Reports should be quick to avoid slowing the workflow. |
| **Events** | None — this is itself an event handler. |

---

### Post-Script Event: Apply `orchestration:plan-approved` Label

| Field | Content |
|-------|---------|
| **Action** | Apply `orchestration:plan-approved` label to the application plan issue |
| **Trigger** | After all assignments and post-assignment events complete successfully |
| **Details** | Locate the application plan issue created during `create-app-plan` (recorded as `#initiate-new-repository.create-app-plan`). Apply the label `orchestration:plan-approved` to signal the plan is ready for epic creation. This triggers the next phase of the orchestration pipeline. |
| **Prerequisites** | All main assignments and events completed. PR merged. Setup branch deleted. |
| **Risks** | The label may not exist in `.github/.labels.json` — must be created if missing. |

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   PRE-SCRIPT-BEGIN EVENT                        │
│  ┌──────────────────────────┐                                    │
│  │  create-workflow-plan    │  ← THIS ASSIGNMENT                │
│  └────────────┬─────────────┘                                    │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                     MAIN ASSIGNMENTS                              │
│                                                                   │
│  ┌──────────────────────────┐                                     │
│  │ init-existing-repository │  → branch, labels, project, PR     │
│  └────────────┬─────────────┘                                     │
│               │                                                   │
│       ┌───────┴──────────┐                                        │
│       │ post-assignment  │                                        │
│       │   validate       │                                        │
│       │   report-progress│                                        │
│       └───────┬──────────┘                                        │
│               │                                                   │
│  ┌──────────────────────────┐                                     │
│  │    create-app-plan       │  → plan issue, milestones          │
│  └────────────┬─────────────┘                                     │
│               │                                                   │
│       ┌───────┴──────────┐                                        │
│       │ post-assignment  │                                        │
│       │   validate       │                                        │
│       │   report-progress│                                        │
│       └───────┬──────────┘                                        │
│               │                                                   │
│  ┌──────────────────────────┐                                     │
│  │ create-project-structure │  → scaffolding, Dockerfile, CI     │
│  └────────────┬─────────────┘                                     │
│               │                                                   │
│       ┌───────┴──────────┐                                        │
│       │ post-assignment  │                                        │
│       │   validate       │                                        │
│       │   report-progress│                                        │
│       └───────┬──────────┘                                        │
│               │                                                   │
│  ┌──────────────────────────┐                                     │
│  │  create-agents-md-file   │  → AGENTS.md at repo root          │
│  └────────────┬─────────────┘                                     │
│               │                                                   │
│       ┌───────┴──────────┐                                        │
│       │ post-assignment  │                                        │
│       │   validate       │                                        │
│       │   report-progress│                                        │
│       └───────┬──────────┘                                        │
│               │                                                   │
│  ┌──────────────────────────┐                                     │
│  │  debrief-and-document    │  → debrief report, execution trace │
│  └────────────┬─────────────┘                                     │
│               │                                                   │
│       ┌───────┴──────────┐                                        │
│       │ post-assignment  │                                        │
│       │   validate       │                                        │
│       │   report-progress│                                        │
│       └───────┬──────────┘                                        │
│               │                                                   │
│  ┌──────────────────────────┐                                     │
│  │  pr-approval-and-merge   │  → CI check, review, merge, cleanup│
│  └────────────┬─────────────┘                                     │
│               │                                                   │
│       ┌───────┴──────────┐                                        │
│       │ post-assignment  │                                        │
│       │   validate       │                                        │
│       │   report-progress│                                        │
│       └───────┬──────────┘                                        │
│               │                                                   │
└───────────────┼───────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                  POST-SCRIPT-COMPLETE EVENT                       │
│  ┌─────────────────────────────────────────────┐                  │
│  │  Apply `orchestration:plan-approved` label   │                 │
│  │  to the application plan issue               │                 │
│  └─────────────────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 5. Open Questions

### Q1: Application Template File Location

The `create-app-plan` assignment references a primary app spec file (`ai-new-app-template.md` or equivalent). This file does not exist in `plan_docs/`. The closest equivalent is the **OS-APOW Implementation Specification v1.2**, which contains the app title, description, requirements, tech stack, and project structure. **Recommendation:** Treat the Implementation Specification as the primary app spec and reference the Development Plan and Architecture Guide as supporting documents.

### Q2: Existing AGENTS.md Replacement

The repository root already contains an `AGENTS.md` from the orchestration template. The `create-agents-md-file` assignment will need to **replace** this file with project-specific content. Should the template AGENTS.md content be preserved anywhere (e.g., moved to a different location), or is a clean replacement acceptable?

### Q3: Branch Protection Ruleset — PAT Availability

The `init-existing-repository` assignment requires importing a branch protection ruleset via the GitHub API, which needs `GH_ORCHESTRATION_AGENT_TOKEN` with `administration: write` scope. If this token is not available in the environment, the step must be skipped with an explicit error. **Needs confirmation:** Is this token available in the current execution environment?

### Q4: Reference Code Disposition

The `plan_docs/` directory contains reference implementation files (`orchestrator_sentinel.py`, `notifier_service.py`, `src/`). Should `create-project-structure` copy/adapt these into the actual project `src/` directory, or should the project structure be created fresh with these as reference only? **Recommendation:** Use as reference — create fresh implementations that incorporate the Plan Review fixes.

### Q5: Phase Scope for Application Plan

The Development Plan describes 4 phases (0-3). The `create-app-plan` assignment should create a plan with milestones. Should all 4 phases be included as milestones, or should the plan focus only on Phase 1 (MVP) with Phases 2-3 deferred to the "Future Work" appendix (per Simplification Report S-9)? **Recommendation:** Include Phase 0 and Phase 1 as active milestones; list Phases 2-3 in a Future Work section.

### Q6: `orchestration:plan-approved` Label Existence

The post-script-complete event requires applying the `orchestration:plan-approved` label. This label may not exist in `.github/.labels.json`. If it doesn't, it will need to be created during or after the `init-existing-repository` assignment's label import step.

---

*End of Workflow Execution Plan*
