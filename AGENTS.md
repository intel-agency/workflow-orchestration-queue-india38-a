---
file: AGENTS.md
description: Project instructions for coding agents
scope: repository
---

<instructions>
  <purpose>
    <summary>
      OS-APOW (Workflow Orchestration Queue) — a headless agentic orchestration platform
      that transforms GitHub Issues into autonomous execution orders. The system uses a
      4-pillar architecture (EAR/STATE/BRAIN/HANDS) implemented in Python/FastAPI, with
      GitHub Actions triggering AI orchestration via devcontainers and the opencode CLI.
    </summary>
  </purpose>

  <template_usage>
    <summary>
      This repository is a **GitHub template repo** (`intel-agency/workflow-orchestration-queue-india38-a`).
      New project repositories are created from it using automation scripts in the
      `nam20485/workflow-launch2` repo. The scripts clone this template, seed plan docs,
      replace template placeholders, and push — producing a ready-to-go AI-orchestrated repo.
    </summary>

    <template-clone-instances>
      Once the template has been cloned into a new instance, this file must be updated to match the new repo's specifics (e.g., name, links, instructions). 
    </template-clone-instances>

    <creation_workflow>
      <step>1. Run `./scripts/create-repo-from-slug.ps1 -Slug &lt;project-slug&gt; -Yes` from the `workflow-launch2` repo.</step>
      <step>2. That delegates to `./scripts/create-repo-with-plan-docs.ps1` which:
        - Creates a new GitHub repo from this template via `gh repo create --template intel-agency/workflow-orchestration-queue-india38-a`
        - Generates a random suffix for the repo name (e.g., `project-slug-bravo84`)
        - Creates repo secrets (`GEMINI_API_KEY`) and variables (`VERSION_PREFIX`)
        - Clones the new repo locally
        - Copies plan docs from `./plan_docs/&lt;slug&gt;/` into the clone's `plan_docs/` directory
        - Replaces all template placeholders (`workflow-orchestration-queue-india38-a` → new repo name, `intel-agency` → new owner)
        - Commits and pushes the seeded repo
      </step>
      <step>3. On push, the clone's `validate` workflow runs CI (lint, scan, tests, devcontainer build) and the `publish-docker` workflow builds and pushes the base Docker image to GHCR.</step>
      <step>4. On successful `publish-docker` completion, the `prebuild-devcontainer` workflow is triggered (via `workflow_run`) to build and push the prebuilt devcontainer image. Together, `publish-docker` → `prebuild-devcontainer` form the devcontainer prebuild caching pipeline that the `orchestrator-agent` workflow relies on to quickly spin up devcontainers.</step>
    </creation_workflow>

    <template_design_constraints>
      <rule>Template placeholders (`workflow-orchestration-queue-india38-a`, `intel-agency`) in file contents and paths are replaced by the creation script. Keep them consistent.</rule>
      <rule>The `validate` workflow must tolerate fresh clones where no prebuilt GHCR devcontainer image exists yet (fallback build from Dockerfile + image aliasing).</rule>
      <rule>The `plan_docs/` directory contains external-generated documents seeded at clone time. Exclude it from strict linting (markdown lint, etc.).</rule>
      <rule>The consumer `.devcontainer/devcontainer.json` references a prebuilt GHCR image. On fresh clones the image won't exist until `publish-docker` and `prebuild-devcontainer` workflows complete their first run.</rule>
    </template_design_constraints>

    <automation_scripts>
      <entry><repo>nam20485/workflow-launch2</repo><path>scripts/create-repo-from-slug.ps1</path><description>Entry point — takes a slug, resolves plan docs dir, delegates to create-repo-with-plan-docs.ps1</description></entry>
      <entry><repo>nam20485/workflow-launch2</repo><path>scripts/create-repo-with-plan-docs.ps1</path><description>Full pipeline: repo create, clone, seed docs, placeholder replace, commit, push</description></entry>
    </automation_scripts>
  </template_usage>

  <tech_stack>
    <summary>Primary language is Python 3.12+ with FastAPI. Devcontainer includes additional runtimes for AI agent tooling.</summary>

    <languages_and_frameworks>
      <item>**Python 3.12+** — Primary language for all system logic</item>
      <item>**FastAPI 0.110+** — High-performance async web framework for webhook receiver</item>
      <item>**Pydantic v2** — Data validation, settings management, schema definitions</item>
      <item>**HTTPX** — Async HTTP client for GitHub REST API calls</item>
      <item>**pytest** — Testing framework with async support</item>
    </languages_and_frameworks>

    <ai_runtime>
      <item>**opencode CLI v1.2.24** — AI agent runtime (`opencode --model zai-coding-plan/glm-5 --agent Orchestrator`)</item>
      <item>**ZhipuAI GLM-5** — Primary LLM model via `ZHIPU_API_KEY`</item>
      <item>**Kimi (Moonshot)** — Alternative LLM via `KIMI_CODE_ORCHESTRATOR_AGENT_API_KEY`</item>
      <item>**MCP servers**: `@modelcontextprotocol/server-sequential-thinking`, `@modelcontextprotocol/server-memory`</item>
    </ai_runtime>

    <devcontainer_tools>
      <item>**uv 0.10.9** — Rust-based Python package manager (fast dependency resolution)</item>
      <item>**Node.js 24 LTS** — For MCP server packages (`npx`)</item>
      <item>**Bun 1.3.10** — Fast JavaScript/TypeScript runtime</item>
      <item>**.NET SDK 10** — Included for cross-platform tooling compatibility</item>
      <item>**GitHub CLI (gh)** — Repository, issue, and PR management</item>
    </devcontainer_tools>

    <infrastructure>
      <item>**GitHub Actions** — Workflow trigger, runner, CI/CD</item>
      <item>**DevContainers** — Reproducible containerized development environment</item>
      <item>**Docker** — Worker container lifecycle management</item>
    </infrastructure>
  </tech_stack>

  <four_pillar_architecture>
    <summary>
      The system is built on four conceptual pillars, each handling a distinct domain.
      See `plan_docs/architecture.md` for detailed diagrams.
    </summary>

    <pillar name="EAR" component="Notifier" location="src/workflow_orchestration_queue/ear/">
      <description>FastAPI webhook receiver for GitHub events</description>
      <responsibilities>
        <item>Secure webhook ingestion at `/webhooks/github`</item>
        <item>HMAC SHA256 validation against `WEBHOOK_SECRET`</item>
        <item>Event triage into unified `WorkItem` objects</item>
        <item>Queue initialization with `agent:queued` label</item>
      </responsibilities>
    </pillar>

    <pillar name="STATE" component="Queue" location="src/workflow_orchestration_queue/state/">
      <description>GitHub Issues + Labels as state machine ("Markdown as a Database")</description>
      <responsibilities>
        <item>Persistent state via GitHub Issues</item>
        <item>State machine labels: `agent:queued` → `agent:in-progress` → terminal states</item>
        <item>Distributed locking via assign-then-verify pattern</item>
      </responsibilities>
      <state_labels>
        <label name="agent:queued">Task awaiting Sentinel pickup</label>
        <label name="agent:in-progress">Sentinel actively processing</label>
        <label name="agent:reconciling">Stale task being recovered</label>
        <label name="agent:success">Terminal success state</label>
        <label name="agent:error">Logic/implementation error</label>
        <label name="agent:infra-failure">Infrastructure failure</label>
        <label name="agent:stalled-budget">Budget/token limit exceeded</label>
      </state_labels>
    </pillar>

    <pillar name="BRAIN" component="Sentinel" location="src/workflow_orchestration_queue/brain/">
      <description>Async Python service managing Worker lifecycle</description>
      <responsibilities>
        <item>Polling discovery of queued tasks (60s interval)</item>
        <item>Auth synchronization via `scripts/gh-auth.ps1`</item>
        <item>Task claiming with assign-then-verify pattern</item>
        <item>Shell-bridge execution to Worker containers</item>
        <item>Heartbeat telemetry every 5 minutes</item>
      </responsibilities>
    </pillar>

    <pillar name="HANDS" component="Worker" location="src/workflow_orchestration_queue/hands/">
      <description>Action execution via devcontainer + opencode CLI</description>
      <responsibilities>
        <item>Execute instruction modules from `local_ai_instruction_modules/`</item>
        <item>Run verification tests before PR submission</item>
        <item>Isolated container environment (2 CPUs, 4GB RAM limits)</item>
      </responsibilities>
    </pillar>
  </four_pillar_architecture>

  <repository_map>
    <!-- Python Application (4-Pillar) -->
    <entry><path>src/workflow_orchestration_queue/</path><description>Main Python package — all application logic</description></entry>
    <entry><path>src/workflow_orchestration_queue/main.py</path><description>FastAPI application entry point</description></entry>
    <entry><path>src/workflow_orchestration_queue/ear/</path><description>EAR pillar — webhook handlers and routes</description></entry>
    <entry><path>src/workflow_orchestration_queue/state/</path><description>STATE pillar — models and GitHub queue store</description></entry>
    <entry><path>src/workflow_orchestration_queue/brain/</path><description>BRAIN pillar — sentinel and orchestrator</description></entry>
    <entry><path>src/workflow_orchestration_queue/hands/</path><description>HANDS pillar — executor and notifier</description></entry>
    <entry><path>src/workflow_orchestration_queue/config/</path><description>Configuration management (Pydantic settings)</description></entry>
    <entry><path>src/workflow_orchestration_queue/api/</path><description>FastAPI routes and dependencies</description></entry>

    <!-- Configuration -->
    <entry><path>pyproject.toml</path><description>Project config, dependencies, tool settings (ruff, mypy, pytest)</description></entry>
    <entry><path>uv.lock</path><description>Deterministic lockfile for exact package versions</description></entry>
    <entry><path>opencode.json</path><description>opencode CLI config with MCP server definitions</description></entry>

    <!-- Workflows -->
    <entry><path>.github/workflows/orchestrator-agent.yml</path><description>Primary workflow — assembles prompt, logs into GHCR, runs opencode in devcontainer</description></entry>
    <entry><path>.github/workflows/prompts/orchestrator-agent-prompt.md</path><description>Prompt template with `__EVENT_DATA__` placeholder (sed-substituted at runtime)</description></entry>
    <entry><path>.github/workflows/publish-docker.yml</path><description>Builds Dockerfile, pushes to GHCR with branch-latest and branch-&lt;VERSION_PREFIX.run_number&gt; tags</description></entry>
    <entry><path>.github/workflows/prebuild-devcontainer.yml</path><description>Layers devcontainer Features on published Docker image (triggered by workflow_run)</description></entry>

    <!-- Agent definitions -->
    <entry><path>.opencode/agents/orchestrator.md</path><description>Orchestrator — coordinates specialists, never writes code directly</description></entry>
    <entry><path>.opencode/agents/</path><description>All specialist agents (developer, code-reviewer, planner, devops-engineer, github-expert, etc.)</description></entry>
    <entry><path>.opencode/commands/</path><description>Reusable command prompts (orchestrate-new-project, grind-pr-reviews, fix-failing-workflows, etc.)</description></entry>

    <!-- Devcontainer -->
    <entry><path>.github/.devcontainer/Dockerfile</path><description>Devcontainer image — Python, .NET SDK, Bun, uv, opencode CLI (build context for publish-docker)</description></entry>
    <entry><path>.github/.devcontainer/devcontainer.json</path><description>Build-time devcontainer config (Dockerfile + Features: node, python, gh CLI)</description></entry>
    <entry><path>.devcontainer/devcontainer.json</path><description>Consumer devcontainer — pulls prebuilt GHCR image, forwards port 4096, and auto-starts `opencode serve` on container start</description></entry>
    <entry><path>scripts/start-opencode-server.sh</path><description>Guarded `opencode serve` bootstrapper used by the devcontainer lifecycle and workflow attach path</description></entry>
    <entry><path>scripts/run-devcontainer-orchestrator.sh</path><description>One-shot script: brings up the devcontainer, ensures the opencode server is running, and executes the orchestrator agent. Used by the workflow and can be invoked directly locally.</description></entry>

    <!-- Tests -->
    <entry><path>tests/</path><description>Python unit tests (pytest)</description></entry>
    <entry><path>test/</path><description>Shell-based tests: devcontainer build, tool availability, prompt assembly</description></entry>
    <entry><path>test/fixtures/</path><description>Sample webhook payloads for local testing</description></entry>

    <!-- Instruction modules -->
    <entry><path>local_ai_instruction_modules/</path><description>Local instruction modules (development rules, workflows, delegation, terminal commands)</description></entry>

    <opencode_server>
      <summary>
        The consumer devcontainer auto-starts `opencode serve` through `scripts/start-opencode-server.sh`.
        The server listens on port `4096` by default so host or in-container clients can attach with
        `opencode run --attach http://127.0.0.1:4096 ...` (or the forwarded host port when connecting from outside the container).
      </summary>
    </opencode_server>
  </repository_map>

  <instruction_source>
    <repository>
      <name>nam20485/agent-instructions</name>
      <branch>main</branch>
    </repository>
    <guidance>
      Remote instructions are the single source of truth. Fetch from raw URLs:
      replace `github.com/` with `raw.githubusercontent.com/` and remove `blob/`.
      Core instructions: `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-core-instructions.md`
    </guidance>
    <modules>
      <module type="core" required="true" link="https://github.com/nam20485/agent-instructions/blob/main/ai_instruction_modules/ai-core-instructions.md">Core Instructions</module>
      <module type="local" required="true" path="local_ai_instruction_modules">Local AI Instructions</module>
      <module type="local" required="true" path="local_ai_instruction_modules/ai-dynamic-workflows.md">Dynamic Workflow Orchestration</module>
      <module type="local" required="true" path="local_ai_instruction_modules/ai-workflow-assignments.md">Workflow Assignments</module>
      <module type="local" required="true" path="local_ai_instruction_modules/ai-development-instructions.md">Development Instructions</module>
      <module type="optional" path="local_ai_instruction_modules/ai-terminal-commands.md">Terminal Commands</module>
    </modules>
  </instruction_source>

  <environment_setup>
    <prerequisites>
      <item>**Python 3.12+** (managed via uv)</item>
      <item>**Docker** (for devcontainer)</item>
      <item>**PowerShell Core (pwsh)** for validation scripts</item>
    </prerequisites>

    <secrets>
      <item>`GITHUB_TOKEN` — GitHub API authentication (required)</item>
      <item>`GITHUB_ORG` — Target organization (e.g., `intel-agency`)</item>
      <item>`GITHUB_REPO` — Target repository name</item>
      <item>`WEBHOOK_SECRET` — HMAC validation for webhooks (EAR component)</item>
      <item>`ZHIPU_API_KEY` — ZhipuAI model access; set in repo Settings → Secrets</item>
      <item>`KIMI_CODE_ORCHESTRATOR_AGENT_API_KEY` — Kimi (Moonshot) model access; set in repo Settings → Secrets</item>
    </secrets>

    <devcontainer_cache>
      Image at `ghcr.io/${{ github.repository }}/devcontainer`. `publish-docker.yml` builds the raw Dockerfile;
      `prebuild-devcontainer.yml` layers Features. Login via `docker/login-action` with `GITHUB_TOKEN`.
      Set repo variable `VERSION_PREFIX` (e.g., `1.0`) for versioned tags emitted by both image publishing workflows.
    </devcontainer_cache>
  </environment_setup>

  <setup_commands>
    <summary>Quick reference for setting up and running the project.</summary>

    <bootstrap>
      <step>**Install Python dependencies (with dev tools):**
        ```bash
        uv sync --extra dev
        ```
        > ⚠️ **Important:** Use `--extra dev` to include dev dependencies (pytest, ruff, mypy). Plain `uv sync` only installs runtime dependencies.
      </step>
      <step>**Install lint/scan tools (optional, for local validation):**
        ```bash
        pwsh -NoProfile -File ./scripts/install-dev-tools.ps1
        ```
      </step>
    </bootstrap>

    <development_server>
      <command>**Run FastAPI server with hot reload:**
        ```bash
        uv run uvicorn workflow_orchestration_queue.main:app --reload
        ```
        Server runs at `http://localhost:8000` by default.
      </command>
      <command>**Run via entry point script:**
        ```bash
        uv run woq-api
        ```
      </command>
      <command>**Run in Docker:**
        ```bash
        docker compose up -d
        ```
      </command>
    </development_server>

    <entry_points>
      <entry name="woq-api">`uv run woq-api` — FastAPI development server</entry>
      <entry name="woq-sentinel">`uv run woq-sentinel` — Sentinel background service</entry>
    </entry_points>
  </setup_commands>

  <testing>
    <python_tests>
      <guidance>Python tests use pytest with async support. Tests are in `tests/` directory.</guidance>
      <commands>
        <command>Run all Python tests: `uv run pytest`</command>
        <command>Run with verbose output: `uv run pytest -v`</command>
        <command>Run with coverage: `uv run pytest --cov=src --cov-report=term-missing`</command>
        <command>Run specific test file: `uv run pytest tests/test_main.py`</command>
        <command>Collect tests only (dry run): `uv run pytest --collect-only`</command>
      </commands>
    </python_tests>

    <shell_tests>
      <guidance>Shell tests in `test/` validate devcontainer build, tool availability, and prompt assembly.</guidance>
      <commands>
        <command>All shell tests: `bash test/test-devcontainer-build.sh && bash test/test-devcontainer-tools.sh && bash test/test-prompt-assembly.sh`</command>
        <command>Prompt assembly tests: `bash test/test-prompt-assembly.sh`</command>
        <command>Dockerfile/tool tests: `bash test/test-devcontainer-tools.sh`</command>
        <command>Image tag logic tests: `bash test/test-image-tag-logic.sh`</command>
      </commands>
      <guidance>Add new fixture payloads to `test/fixtures/` when testing new event types.</guidance>
    </shell_tests>
  </testing>

  <code_quality>
    <linting>
      <command>**Ruff linting:**
        ```bash
        uv run ruff check src/ tests/      # Check for issues
        uv run ruff check --fix src/ tests/  # Auto-fix issues
        ```
      </command>
    </linting>

    <formatting>
      <command>**Ruff formatting:**
        ```bash
        uv run ruff format src/ tests/     # Format files
        uv run ruff format --check src/ tests/  # Check formatting without modifying
        ```
      </command>
    </formatting>

    <type_checking>
      <command>**MyPy type checking (strict mode):**
        ```bash
        uv run mypy src/
        ```
      </command>
    </type_checking>
  </code_quality>

  <coding_conventions>
    <general>
      <rule>Keep changes minimal and targeted.</rule>
      <rule>Do not hardcode secrets/tokens.</rule>
      <rule>Preserve the `__EVENT_DATA__` placeholder in `orchestrator-agent-prompt.md`.</rule>
      <rule>Pin action versions by SHA in workflow files.</rule>
      <rule>Never add duplicate top-level `name:`, `on:`, or `jobs:` keys in workflow YAML.</rule>
      <rule>Run `./scripts/validate.ps1 -All` before committing non-trivial changes.</rule>
      <rule>Monitor CI after push: `gh run list --limit 5`, `gh run watch &lt;id&gt;`</rule>
    </general>

    <python_specific>
      <rule>Use **Pydantic v2** for all data models and settings.</rule>
      <rule>Follow **strict MyPy** typing (configured in `pyproject.toml`).</rule>
      <rule>Use **async/await** for all I/O operations (FastAPI, HTTPX).</rule>
      <rule>Imports should be at top-level of file (ruff `PLC0415`).</rule>
      <rule>Line length limit: 100 characters (ruff config).</rule>
      <rule>Use `logging.exception()` instead of `logging.error()` in exception handlers.</rule>
      <rule>Use `enum.StrEnum` for string enums (Python 3.11+).</rule>
    </python_specific>

    <infrastructure>
      <rule>`.opencode/` is checked out by `actions/checkout`; do not COPY it in the Dockerfile.</rule>
      <rule>Dockerfile lives at `.github/.devcontainer/Dockerfile`. Consumer devcontainer uses `"image:"` — no local build.</rule>
      <rule>Repository labels are defined in `.github/.labels.json`. Use `scripts/import-labels.ps1` to sync them to a repo instance. When adding new labels, add them to this file — it is the single source of truth for the label set.</rule>
    </infrastructure>
  </coding_conventions>

  <common_pitfalls>
    <pitfall name="uv sync without --extra dev">
      <symptom>Commands like `uv run pytest` or `uv run ruff` fail with "module not found"</symptom>
      <solution>Always use `uv sync --extra dev` to install development dependencies. The `dev` extra contains pytest, ruff, mypy, and other tools needed for development.</solution>
    </pitfall>

    <pitfall name="pwsh not available outside devcontainer">
      <symptom>`scripts/validate.ps1` fails with "pwsh: command not found"</symptom>
      <solution>The validation script requires PowerShell Core. Either run inside the devcontainer, or install `pwsh` locally. Individual lint tools can be run directly instead.</solution>
    </pitfall>

    <pitfall name="prebuilt devcontainer image not found">
      <symptom>Fresh clone fails to start devcontainer with image pull error</symptom>
      <solution>Wait for `publish-docker` and `prebuild-devcontainer` workflows to complete their first run. The image is built on first push to main.</solution>
    </pitfall>

    <pitfall name="linting errors in existing code">
      <symptom>`uv run ruff check src/ tests/` reports errors</symptom>
      <solution>The codebase has some existing linting issues. When making changes, ensure your new code passes linting. Consider fixing existing issues incrementally.</solution>
    </pitfall>
  </common_pitfalls>

  <agent_specific_guardrails>
    <rule>The Orchestrator agent delegates to specialists via the `task` tool — never writes code directly.</rule>
    <rule>Prompt assembly pipeline:
      1. Read template from `.github/workflows/prompts/orchestrator-agent-prompt.md`.
      2. Prepend structured event context (event name, action, actor, repo, ref, SHA).
      3. Append raw event JSON from `${{ toJson(github.event) }}`.
      4. Write to `.assembled-orchestrator-prompt.md` and export path via `GITHUB_ENV`.
    </rule>
  </agent_specific_guardrails>

  <agent_readiness>
    <verification_protocol>
      For any non-trivial change (logic, behavior, refactors, dependency updates, config changes, multi-file edits):
      run verification, fix all failures, re-run until clean. Do not skip or suppress errors.
    </verification_protocol>

    <verification_commands>
      <!--
        MANDATORY: After every non-trivial change, run validation BEFORE commit/push.
        Do NOT commit or push until it passes. Do NOT skip steps.

        Local (runs all checks sequentially — lint, scan, test):
          pwsh -NoProfile -File ./scripts/validate.ps1 -All

        This is the SAME script that CI calls with individual switches:
          ./scripts/validate.ps1 -Lint   (CI: lint job)
          ./scripts/validate.ps1 -Scan   (CI: scan job)
          ./scripts/validate.ps1 -Test   (CI: test job)

        If a check is skipped due to a missing local tool, run:
          pwsh -NoProfile -File ./scripts/install-dev-tools.ps1

        | Check                  | Command                                              | When to run              |
        |========================|======================================================|==========================|
        | All (local default)    | ./scripts/validate.ps1 -All                           | Every task               |
        | Lint only              | ./scripts/validate.ps1 -Lint                           | Quick check              |
        | Scan only              | ./scripts/validate.ps1 -Scan                           | Secrets concern          |
        | Test only              | ./scripts/validate.ps1 -Test                           | After lint passes        |
        | Devcontainer tests     | bash test/test-devcontainer-tools.sh                   | Dockerfile changes       |
        | Python tests           | uv run pytest                                          | Python code changes      |
        | Python lint            | uv run ruff check src/ tests/                          | Python code changes      |
        | Python format          | uv run ruff format --check src/ tests/                 | Python code changes      |
        | Type check             | uv run mypy src/                                       | Type annotation changes  |
      -->
      <rule>When adding a CI workflow check, add its equivalent to scripts/validate.ps1.</rule>
    </verification_commands>

    <post_commit_monitoring>
      After push, monitor CI until green: `gh run list --limit 5`, `gh run watch <id>`, `gh run view <id> --log-failed`.
      If any workflow fails, stop feature work, triage, fix, re-verify, push. Do not mark work complete while CI is failing.
    </post_commit_monitoring>

    <pipeline_speed_policy>
      <lane name="fast_readiness" blocking="true">Build, lint/format, unit tests — keep fast for merge readiness.</lane>
      <lane name="extended_validation" blocking="false">Integration suites, security scans, dependency audits.</lane>
      <rule>Protect the fast lane from slow steps.</rule>
    </pipeline_speed_policy>
  </agent_readiness>

  <validation_before_handoff>
    <step>Run applicable tests: `uv run pytest` and `bash test/test-prompt-assembly.sh`</step>
    <step>Run linting: `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/`</step>
    <step>Validate workflow YAML: `grep -c "^name:" .github/workflows/orchestrator-agent.yml  # expect 1`</step>
    <step>Summarize: what changed, what was validated, remaining risks (secret-dependent paths, image cache misses).</step>
  </validation_before_handoff>

  <tool_use_instructions>
    <instruction id="querying_microsoft_documentation">
      <applyTo>**</applyTo>
      <title>Querying Microsoft Documentation</title>
      <tools><tool>microsoft_docs_search</tool><tool>microsoft_docs_fetch</tool><tool>microsoft_code_sample_search</tool></tools>
      <guidance>
        Use these MCP tools for Microsoft technologies (C#, ASP.NET Core, .NET, EF, NuGet).
        Prioritize retrieved info over training data for newer features.
      </guidance>
    </instruction>
    <instruction id="sequential_thinking_default_usage">
      <applyTo>*</applyTo>
      <title>Sequential Thinking</title>
      <tools><tool>sequential_thinking</tool></tools>
      <guidance>
        Use for all non-trivial requests. Enables step-by-step analysis with revision, branching, and dynamic adjustment.
        Use when: breaking down complex problems, planning, architectural decisions, debugging, multi-step context.
      </guidance>
    </instruction>
    <instruction id="memory_default_usage">
      <applyTo>*</applyTo>
      <title>Knowledge Graph Memory</title>
      <tools><tool>create_entities</tool><tool>create_relations</tool><tool>add_observations</tool><tool>delete_entities</tool><tool>delete_observations</tool><tool>delete_relations</tool><tool>read_graph</tool><tool>search_nodes</tool><tool>open_nodes</tool></tools>
      <guidance>
        Use for non-trivial requests. Persist user/project context (preferences, configs, decisions, challenges, solutions).
        Entities have names, types, and observations. Relations connect entities. Search/read at task start; update after significant work.
      </guidance>
    </instruction>
  </tool_use_instructions>

  <available_tools>
    <summary>
      Tools available inside the devcontainer at runtime. Installed via
      `.github/.devcontainer/Dockerfile` unless noted otherwise.
    </summary>

    <runtimes_and_package_managers>
      <tool name="python" version="3.12+">`Python` — Primary language for all application logic.</tool>
      <tool name="uv" version="0.10.9">`uv` — Rust-based Python package manager. Use `uv sync --extra dev` for full setup. Also provides `uvx` for ephemeral tool runs.</tool>
      <tool name="node" version="24.14.0 LTS">`Node.js` — JavaScript runtime. Required for MCP server packages (`npx`).</tool>
      <tool name="npm">`npm` — Node package manager (bundled with Node.js).</tool>
      <tool name="bun" version="1.3.10">`Bun` — fast JavaScript/TypeScript runtime, bundler, and package manager.</tool>
      <tool name="dotnet" version="10.0.102">`.NET SDK` — build, test, publish C#/F# projects. Includes Avalonia Templates 11.3.12.</tool>
    </runtimes_and_package_managers>

    <cli_tools>
      <tool name="gh">`GitHub CLI` — interact with GitHub API (issues, PRs, repos, releases, actions). Authenticated automatically via `GITHUB_TOKEN` env var in CI; use `gh auth login --with-token` otherwise.</tool>
      <tool name="opencode" version="1.2.24">`opencode CLI` — AI agent runtime. Runs agents defined in `.opencode/agents/` with MCP server support.</tool>
      <tool name="git">`Git` — version control (system package + devcontainer feature).</tool>
      <tool name="docker">`Docker CLI` — container lifecycle management for Worker environments.</tool>
    </cli_tools>

    <python_dev_tools>
      <tool name="pytest" version="8.0+">`pytest` — Python testing framework with async support.</tool>
      <tool name="ruff" version="0.2+">`ruff` — Fast Python linter and formatter (replaces flake8, isort, black).</tool>
      <tool name="mypy" version="1.8+">`mypy` — Static type checker with strict mode enabled.</tool>
    </python_dev_tools>

    <github_authentication>
      <summary>
        GitHub API access is configured at multiple layers to support both `gh` CLI and MCP GitHub server operations.
      </summary>
      <layer name="GITHUB_TOKEN">Provided automatically by GitHub Actions. Passed into the devcontainer via `--remote-env`.</layer>
      <layer name="GITHUB_PERSONAL_ACCESS_TOKEN">Bridged from `GITHUB_TOKEN` for the `@modelcontextprotocol/server-github` MCP server, which requires this specific env var name. Set in `opencode.json` via the MCP `env` block, in `devcontainer.json` `remoteEnv`, and exported in `run_opencode_prompt.sh`.</layer>
      <layer name="gh auth login">`run_opencode_prompt.sh` authenticates the `gh` CLI via `echo "$GITHUB_TOKEN" | gh auth login --with-token` before launching opencode.</layer>
    </github_authentication>

    <scripts_directory>
      <summary>PowerShell helper scripts in `scripts/` for GitHub setup and management tasks.</summary>
      <script name="scripts/common-auth.ps1">Shared `Initialize-GitHubAuth` function — checks `gh auth status`, authenticates via PAT token (`$env:GITHUB_AUTH_TOKEN`) or interactive login.</script>
      <script name="scripts/gh-auth.ps1">Extended GitHub auth helper — supports PAT token auth via `--with-token` and interactive fallback.</script>
      <script name="scripts/import-labels.ps1">Imports labels from `.github/.labels.json` into the repository.</script>
      <script name="scripts/create-milestones.ps1">Creates project milestones from plan docs.</script>
      <script name="scripts/test-github-permissions.ps1">Verifies `GITHUB_TOKEN` has required permissions (contents, issues, PRs, packages).</script>
      <script name="scripts/query.ps1">PR review thread manager — fetches unresolved review threads from a PR, summarizes them, and can batch-reply and resolve them. Supports `--AutoResolve`, `--DryRun`, `--Interactive`, `--ReplyEach`, `--Path`, `--BodyContains` filtering. Use this instead of writing ad-hoc scripts to resolve PR review comments.</script>
      <script name="scripts/update-remote-indices.ps1">Updates remote instruction module indices.</script>
      <script name="scripts/install-dev-tools.ps1">Installs local dev tools (actionlint, hadolint, shellcheck, gitleaks) for validation.</script>
      <script name="scripts/validate.ps1">Main validation script — runs lint, scan, and test checks. Used by CI and local development.</script>
    </scripts_directory>
  </available_tools>
</instructions>
