# AI Prompt History

Record prompts actually used for repository work. Preserve exact user prompts when requested; separate generated examples from executed prompts. Never store credentials or personal data.

## P-2026-10-27-01 — Documentation setup

- **Date:** 2026-10-27
- **Tool / model / settings:** Codex-assisted repository session; exact model and settings are not available from repository evidence.
- **Context files:** `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/CONTEXT_MANAGEMENT.md`, `docs/TESTING.md`, `docs/WEEKLY_LOG.md`, `prompts/PROMPT_HISTORY.md`; repository audit findings.
- **Purpose:** Establish maintainable AI-assisted development documentation from verified repository facts, without changing application source.
- **Exact prompt:**

> Set up documentation for AI-assisted development in this repository.
>
> Create the necessary files under docs/ and prompts/.
>
> Requirements:
>
> 1. ARCHITECTURE.md – verified application structure and workflow.
> 2. DEVELOPMENT_PLAN.md – incremental development milestones.
> 3. SESSION_CONTEXT.md – current development state and next steps.
> 4. CONTEXT_MANAGEMENT.md – context handling and compaction log.
> 5. AI_TOOLS.md – AI tools, models, configurations, and integrations actually used.
> 6. TESTING.md – test commands, test results, and validation evidence.
> 7. CHALLENGES.md – errors, root causes, and fixes.
> 8. WEEKLY_LOG.md – weekly implementation records.
> 9. PROMPT_HISTORY.md – prompt ID, exact prompt, purpose, improvements, outputs, and verification.
>
> Populate documents using facts established in the repository audit.
>
> Do not invent completed features, test results, executed agents, or context compaction events.
>
> Record this task itself as a prompt-history entry.
>
> Do not modify application source code.

- **Improvements requested:** None; this is the original task prompt.
- **Output:** Documentation files under `docs/` and this prompt-history entry under `prompts/`. No application source was changed for this task.
- **Verification:** `git diff --check` and manual review of the documentation diff. Application tests/build were not run because no application code changed.
- **Follow-up:** Replace this entry's model/settings with exact values only if they become available; record test outcomes after actual runs.

## P-2026-10-27-02 — PostgreSQL migration

- **Date:** 2026-10-27
- **Tool / model / settings:** Codex-assisted repository session; exact model/settings are not available from repository evidence.
- **Context files:** `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`, backend source, requirements, SQLite database metadata, existing tests, environment example, and Git ignore rules.
- **Purpose:** Move the app's runtime database to PostgreSQL in Docker, migrate the schema and any existing tickets safely, verify behavior, and document the result.
- **Exact prompt:**

> You are a senior Python FastAPI, PostgreSQL, Docker, and database migration engineer.
>
> **Project:** Texol AI Support Hub
>
> **Task:** Migrate the existing application database from SQLite to PostgreSQL using Docker, and ensure the application works correctly with PostgreSQL.
>
> I am using Codex for AI-assisted development. Follow the existing AGENTS.md and project documentation.
>
> ## Phase 1 — Analyze existing database
>
> 1. Inspect the existing FastAPI backend.
> 2. Identify the current SQLite connection, tables, queries, models, and database initialization logic.
> 3. Inspect existing data and identify potential migration issues.
> 4. Check whether Docker and Docker Compose are installed.
> 5. Check the existing environment configuration.
> 6. Identify the necessary backend changes.
>
> ## Phase 2 — Configure PostgreSQL using Docker
>
> 1. Create a docker-compose.yml file using PostgreSQL 17.
> 2. Configure:
>    - Database: texol_support
>    - Username: texol_user
>    - Host port: 5433
>    - Container port: 5432
> 3. Use a persistent Docker volume for database storage.
> 4. Configure environment variables using .env and .env.example.
> 5. Never hardcode passwords or credentials.
> 6. Add a PostgreSQL health check.
> 7. Bind the database port to localhost for local development.
>
> ## Phase 3 — Migrate the Python backend
>
> 1. Replace SQLite-specific database access with PostgreSQL-compatible access.
> 2. Prefer SQLAlchemy 2.x for database operations.
> 3. Use psycopg for PostgreSQL connectivity.
> 4. Use Alembic for database schema migrations.
> 5. Preserve existing FastAPI endpoints and JSON response formats.
> 6. Maintain proper database session management.
> 7. Use DATABASE_URL from environment variables.
> 8. Add transaction handling and rollback on errors.
> 9. Ensure existing functionality remains compatible.
>
> ## Phase 4 — Database schema and data migration
>
> 1. Create an initial PostgreSQL schema matching the existing application's data model.
> 2. Implement Alembic migrations.
> 3. Create a repeatable migration procedure for transferring existing SQLite records.
> 4. Preserve ticket IDs and relationships where applicable.
> 5. Validate record counts and migrated values.
> 6. Ensure PostgreSQL ID sequences are updated correctly.
> 7. Do not delete or modify the original SQLite database.
> 8. Prevent duplicate records if migration is repeated.
> 9. Do not generate unrelated future product-management tables yet.
>
> ## Phase 5 — Run and validate Docker
>
> If Docker is available:
>
> 1. Start the PostgreSQL container.
> 2. Verify container health.
> 3. Apply database migrations.
> 4. Run the SQLite-to-PostgreSQL data migration.
> 5. Start the FastAPI backend.
> 6. Test database connectivity.
> 7. Verify existing ticket APIs.
> 8. Confirm data persists after a container restart.
>
> If Docker is unavailable, create and validate the configuration as far as possible, and clearly report what remains untested.
>
> ## Phase 6 — DBeaver integration
>
> Document the following DBeaver connection configuration:
>
> - Driver: PostgreSQL
> - Host: localhost
> - Port: 5433
> - Database: texol_support
> - Username: texol_user
> - Password: From local .env
>
> Provide SQL queries to verify tables, ticket records, and database connectivity.
>
> ## Phase 7 — Testing and security
>
> 1. Add database connectivity tests.
> 2. Add migration validation tests where feasible.
> 3. Test ticket creation, retrieval, and updates.
> 4. Verify that failed transactions roll back.
> 5. Run relevant backend tests.
> 6. Check that .env files, passwords, and database backups are excluded from Git.
> 7. Review docker-compose.yml for security issues.
> 8. Do not delete Docker volumes or existing databases.
>
> ## Phase 8 — AI development documentation
>
> Update:
>
> - README.md
> - AGENTS.md if needed
> - docs/ARCHITECTURE.md
> - docs/DEVELOPMENT_WORKFLOW.md
> - docs/SESSION_CONTEXT.md
> - docs/CONTEXT_MANAGEMENT.md
> - docs/TESTING.md
> - docs/CHALLENGES.md
> - docs/WEEKLY_LOG.md
> - prompts/PROMPT_HISTORY.md
>
> Document:
> - The PostgreSQL migration objective
> - The implementation approach
> - Important prompts and improvements
> - Actual commands executed
> - Errors and solutions
> - Files modified
> - Tests executed and their results
> - Important architectural decisions
> - Remaining limitations
>
> Do not invent test results, errors, compaction events, or agent executions.
>
> ## Execution instructions
>
> 1. First inspect the existing project and give a concise implementation plan.
> 2. Then proceed with implementation without waiting for additional confirmation for safe, non-destructive local changes.
> 3. Ask for approval before any destructive operation or change to an existing non-project database/container.
> 4. Run tests and fix errors.
> 5. Update documentation after implementation.
> 6. Provide a final summary.
>
> ## Expected final output
>
> Explain:
> 1. Previous SQLite architecture
> 2. New PostgreSQL architecture
> 3. Docker configuration
> 4. Database tables
> 5. Alembic migrations
> 6. Existing data migration results
> 7. DBeaver connection instructions
> 8. FastAPI execution commands
> 9. Tests passed and failed
> 10. Modified files
> 11. Git commit recommendation
> 12. Next development task
>
> **Important:** Prioritize a working PostgreSQL integration while preserving all existing application functionality.
>
> Begin implementation now.

- **Improvements / implementation decisions:** Added a repeatable importer that treats exact existing rows as already migrated and aborts on same-ID conflicts; added synthetic non-empty migration verification because the actual SQLite source contains zero rows. Added PATCH support because the task explicitly requested update coverage. Used a generated, ignored local password; no credential value is recorded here.
- **Output:** Added Docker Compose PostgreSQL 17 service, SQLAlchemy models/session usage, Alembic initial migration, SQLite importer, ticket update API, tests, `.env.example`, `.gitignore` protections, README, and development docs. See Git changes for the exact file list.
- **Verification:** PostgreSQL health and migration were checked; actual source import reported zero records; synthetic import, repeat import, sequence, live API, and restart persistence were exercised. Backend test suite and `git diff --check` results are recorded in `docs/TESTING.md` after final verification.
- **Follow-up:** Define authentication, authorization, and product visibility rules before implementing multi-product data or integrations.

## P-2026-10-27-005 — Codex custom agents and skills

- **Date:** 2026-10-27
- **Tool / model / settings:** Codex CLI `0.164.0`; user config model `gpt-6-luna`, medium reasoning. Exact settings for the current host session are not available.
- **Context files:** `AGENTS.md`, README and development docs, PostgreSQL/Alembic implementation, tests, Codex CLI help/features/config, and official OpenAI Codex subagent/skill documentation.
- **Purpose:** Add supported project Codex agent profiles and reusable skills, demonstrate real delegated reviews and a skill invocation, and document actual evidence and limitations.
- **Exact prompt:**

> # Prompt 005 — Codex Custom Agents & Skills Implementation
>
> You are a senior AI software engineering architect specializing in Codex, multi-agent development, agent orchestration, and reusable skills.
>
> ## Project context
>
> Project: Texol AI Support Hub
>
> Technology:
> - Frontend: React
> - Backend: Python FastAPI
> - Database: PostgreSQL 17 in Docker
> - ORM: SQLAlchemy 2.x
> - Migration: Alembic
> - AI development tool: Codex
>
> Completed:
> - Repository analysis
> - Development documentation setup
> - SQLite-to-PostgreSQL migration
> - Database migration testing
>
> I am developing this project to learn and demonstrate AI-assisted software development, including custom agents, skills, prompt engineering, context management, testing, and automation.
>
> ## Phase 1 — Analyze existing Codex environment
>
> 1. Inspect the existing AGENTS.md and project documentation.
> 2. Check the installed Codex CLI version.
> 3. Determine the currently supported native Codex subagent and skill configuration formats.
> 4. Check whether multi-agent functionality is enabled.
> 5. Review project architecture and test commands.
> 6. Do not assume another AI coding tool's configuration works in Codex.
>
> ## Phase 2 — Create six specialized agents
>
> Configure the following agents using Codex-supported conventions.
>
> ### Agent 1 — Architecture Reviewer
>
> Responsibilities:
> - Analyze feature requirements.
> - Review React, FastAPI, SQLAlchemy, and PostgreSQL architecture.
> - Recommend API contracts and database changes.
> - Identify risks and dependencies.
> - Avoid unnecessary architectural changes.
>
> Prefer read-only access.
>
> ### Agent 2 — Backend Engineer
>
> Responsibilities:
> - Implement FastAPI endpoints.
> - Develop SQLAlchemy models.
> - Create Alembic migrations.
> - Implement validation and error handling.
> - Write backend tests.
> - Follow backend architecture and coding standards.
>
> Do not modify frontend files unless explicitly authorized.
>
> ### Agent 3 — Frontend Engineer
>
> Responsibilities:
> - Implement React components.
> - Integrate backend APIs.
> - Add validation, loading states, and error handling.
> - Implement responsive layouts.
> - Run available frontend checks.
>
> Do not modify backend files unless explicitly authorized.
>
> ### Agent 4 — QA Engineer
>
> Responsibilities:
> - Review implementation against requirements.
> - Run unit and integration tests.
> - Detect regressions.
> - Identify missing test coverage.
> - Report errors with reproduction steps.
>
> Prefer read-only review. Report fixes for the implementation agent.
>
> ### Agent 5 — Security Reviewer
>
> Responsibilities:
> - Review database access.
> - Identify exposed credentials.
> - Check input validation and authorization.
> - Identify insecure API design.
> - Inspect Docker and environment configuration.
> - Report vulnerabilities and recommended corrections.
>
> Do not access unrelated secrets or modify production systems.
>
> ### Agent 6 — Documentation Engineer
>
> Responsibilities:
> - Maintain README.md.
> - Update architecture documentation.
> - Record prompt history and development evidence.
> - Document agent and skill executions.
> - Maintain testing and challenge logs.
> - Prepare weekly submission summaries.
>
> Never invent test results, errors, prompts, or tool executions.
>
> ## Phase 3 — Configure native agent orchestration
>
> 1. Create the appropriate project-level Codex configuration for supported custom agents.
> 2. Give each agent a clear role, scope, instructions, and tool restrictions where supported.
> 3. Enable multi-agent execution only through a supported mechanism.
> 4. Use subagents for independent tasks.
> 5. Avoid simultaneous edits to the same files.
> 6. Route final implementation decisions through the main Codex agent.
> 7. Require human approval before destructive actions.
> 8. Validate that the configurations can actually be loaded.
>
> If the installed Codex environment does not support a requested capability, document the limitation and implement the closest supported alternative.
>
> Do not claim agents are active merely because configuration files exist.
>
> ## Phase 4 — Create six reusable skills
>
> Use the Codex-compatible project skill directory:
>
> .agents/skills/
>
> Create:
>
> ### Skill 1 — fastapi-feature
>
> Purpose: Implement FastAPI features.
>
> Workflow:
> 1. Inspect existing APIs and schemas.
> 2. Review requirements.
> 3. Design the endpoint.
> 4. Implement validation and business logic.
> 5. Write relevant tests.
> 6. Execute tests.
> 7. Document results.
>
> ### Skill 2 — react-feature
>
> Purpose: Implement React features.
>
> Workflow:
> 1. Inspect existing components.
> 2. Define interface behavior.
> 3. Implement UI changes.
> 4. Integrate backend APIs.
> 5. Handle loading and error states.
> 6. Run build and available tests.
>
> ### Skill 3 — database-migration
>
> Purpose: Safely manage PostgreSQL schema changes.
>
> Workflow:
> 1. Review existing SQLAlchemy models.
> 2. Identify database changes.
> 3. Create an Alembic migration.
> 4. Review schema upgrade behavior.
> 5. Validate data preservation.
> 6. Test migration and rollback strategies safely.
> 7. Document results.
>
> Never delete database volumes or existing data automatically.
>
> ### Skill 4 — bug-investigation
>
> Purpose: Debug application failures.
>
> Workflow:
> 1. Reproduce the issue.
> 2. Collect relevant error details.
> 3. Identify the likely root cause.
> 4. Propose the smallest appropriate fix.
> 5. Implement the approved fix.
> 6. Run regression tests.
> 7. Record the issue and resolution.
>
> ### Skill 5 — test-validation
>
> Purpose: Verify implemented functionality.
>
> Workflow:
> 1. Read acceptance criteria.
> 2. Identify applicable tests.
> 3. Run automated tests.
> 4. Check integration behavior.
> 5. Report passed, failed, and unexecuted tests.
> 6. Identify coverage gaps.
>
> ### Skill 6 — weekly-documentation
>
> Purpose: Generate evidence for Wednesday development sessions.
>
> Workflow:
> 1. Inspect Git changes and commits.
> 2. Read prompt history.
> 3. Review completed features.
> 4. Collect available test results.
> 5. Document AI agents and skills actually used.
> 6. Record context-management activities.
> 7. Update weekly documentation.
> 8. Prepare a presentation outline and demo checklist.
>
> Each skill must include:
> - Valid SKILL.md front matter
> - Clear description and invocation criteria
> - Reusable implementation workflow
> - Validation steps
> - Expected outputs
>
> Avoid duplicated or unnecessarily long instructions.
>
> ## Phase 5 — Integrate agents and skills into development
>
> Define how the main Codex agent should coordinate these components.
>
> Example workflow:
>
> User requirement
> → Architecture Reviewer
> → Backend Engineer and Frontend Engineer, with non-overlapping responsibilities
> → QA Engineer
> → Security Reviewer
> → Documentation Engineer
> → Human verification
>
> Agents should use appropriate skills for their work.
>
> Update AGENTS.md with concise guidelines explaining when to delegate and when to invoke skills.
>
> ## Phase 6 — Validate with the PostgreSQL migration
>
> Use the existing completed PostgreSQL migration as the first practical validation task.
>
> 1. Ask Architecture Reviewer to inspect migration design.
> 2. Ask QA Engineer to review database tests and available results.
> 3. Ask Security Reviewer to inspect Docker configuration and credential handling.
> 4. Invoke the test-validation skill.
> 5. Record actual agent and skill execution evidence.
>
> Do not modify the database schema or delete any existing records.
>
> Run additional nondestructive tests when necessary.
>
> ## Phase 7 — Documentation
>
> Create or update:
>
> - docs/AI_AGENTS.md
> - docs/AI_SKILLS.md
> - docs/AGENT_WORKFLOW.md
> - docs/DEVELOPMENT_WORKFLOW.md
> - docs/SESSION_CONTEXT.md
> - docs/TESTING.md
> - docs/CHALLENGES.md
> - docs/WEEKLY_LOG.md
> - prompts/PROMPT_HISTORY.md
>
> Document:
> - Agent name and purpose
> - Actual configuration location
> - Skill name and purpose
> - How agents and skills were invoked
> - Actual execution evidence
> - Tool and model settings, when available
> - Errors encountered and resolutions
> - What is implemented versus only planned
> - Lessons learned
>
> Record this request as Prompt 005 in the prompt history.
>
> ## Phase 8 — Validation and final output
>
> 1. Validate all created configuration files.
> 2. Confirm skills are discoverable in Codex, where supported.
> 3. Demonstrate at least one real agent delegation.
> 4. Demonstrate at least one real skill invocation.
> 5. Run applicable tests.
> 6. Report any unsupported capabilities.
> 7. Update documentation.
>
> Provide:
> - Complete created file list
> - Agent configurations
> - Skill configurations
> - Commands or prompts to invoke each agent and skill
> - Actual execution evidence
> - Tests executed and results
> - Remaining limitations
> - Recommended next development task
>
> ## Important constraints
>
> - Preserve existing PostgreSQL data.
> - Do not change application business logic unnecessarily.
> - Do not expose credentials.
> - Do not make destructive changes without approval.
> - Do not invent agent execution or testing evidence.
> - Avoid unnecessarily complex agent configurations.
> - Do not push to GitHub without my approval.
>
> Start by inspecting the installed Codex environment, then implement and validate the supported agent and skill configurations.

- **Improvements / implementation decisions:** Used native `.codex/agents/*.toml` and `[agents]` config instead of another tool's agent format. Used `.agents/skills/*/SKILL.md`. Documented that custom agent instructions cannot enforce a separate read-only sandbox. Kept PostgreSQL/database state unchanged. Fixed the reviewed NULL-status import edge case and expanded backup ignore rules.
- **Output:** Six project agent profiles, six reusable skills, Codex workflow documentation, concise AGENTS.md delegation guidance, one importer validation guard and regression test, and updated security ignore patterns.
- **Actual execution evidence:** Three read-only host-session subagents completed architecture, QA, and security reviews. One native Codex CLI `$test-validation` skill invocation completed in read-only mode. Two native CLI custom-profile spawn attempts logged a missing-rollout error and no receiver IDs; they are not counted as profile execution.
- **Verification:** Codex CLI version/features inspected; agent TOML parsed; skills validated with `quick_validate.py`; one skill invoked in Codex CLI; backend tests run. Exact final outputs are recorded in `docs/TESTING.md`.
- **Follow-up:** Resolve/verify the Codex CLI rollout-store issue in a future session before claiming native custom agent profile execution. Define product access roles and authentication before adding multi-product behavior.

## P-2026-10-27-006 — Context engineering, compaction, and session recovery

- **Date:** 2026-10-27
- **Tool / model / settings:** Codex CLI `0.164.0`; GPT-6-Luna, medium reasoning. A read-only interactive CLI session demonstrated `/compact`; a separate read-only ephemeral CLI session invoked `$context-handoff`.
- **Context files:** `AGENTS.md`, `.codex/agents/*.toml`, `.agents/skills/*/SKILL.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_PLAN.md`, `docs/DEVELOPMENT_WORKFLOW.md`, `docs/SESSION_CONTEXT.md`, `docs/CONTEXT_MANAGEMENT.md`, `docs/TESTING.md`, `docs/AI_AGENTS.md`, `docs/AI_SKILLS.md`, `docs/AI_TOOLS.md`, `docs/WEEKLY_LOG.md`, and existing prompt history.
- **Purpose:** Establish durable project/session/task context, native compaction guidance, a repeatable handoff, and evidence-based fresh-session recovery.
- **Exact prompt:**

> # Prompt 006 — Context Engineering, Compaction & Session Recovery
>
> You are a senior AI context engineering specialist experienced in Codex CLI, AI coding agents, context compaction, and long-running software development workflows.
>
> ## Project
>
> Name: Texol AI Support Hub
>
> Stack:
> - React frontend
> - Python FastAPI backend
> - PostgreSQL 17 in Docker
> - SQLAlchemy 2.x
> - Alembic migrations
> - Codex for AI-assisted development
>
> Previously completed:
> - Prompt 001: Repository analysis
> - Prompt 003: Documentation setup
> - Prompt 004: PostgreSQL migration
> - Prompt 005: Custom AI agents and reusable skills
>
> Verify these milestones against the repository and prompt history before treating them as completed.
>
> ## Objective
>
> Implement a practical context-management system so that Codex and its specialized agents can continue development across long sessions without losing critical requirements, architecture decisions, implementation progress, or unresolved problems.
>
> I also want to demonstrate real context compaction and session recovery for my AI-assisted software development submission.
>
> ## Phase 1 — Inspect current context configuration
>
> 1. Read AGENTS.md.
> 2. Inspect existing custom agents and skills.
> 3. Read the architecture and development plans.
> 4. Review prompt history and session documentation.
> 5. Inspect recent Git commits and working changes.
> 6. Check the installed Codex version.
> 7. Determine whether the environment supports native context compaction, automatic compaction, /compact, and /status.
> 8. Do not assume features exist without verification.
>
> ## Phase 2 — Define three context layers
>
> ### Layer 1: Permanent project context
>
> Preserve:
> - Project objectives
> - Application architecture
> - Technology stack
> - Coding conventions
> - Database architecture
> - Security requirements
> - Agent responsibilities
> - Skill usage conventions
>
> Use AGENTS.md and existing architecture documentation.
>
> Avoid duplicating lengthy instructions.
>
> ### Layer 2: Development session context
>
> Maintain docs/SESSION_CONTEXT.md containing:
> - Current development milestone
> - Current Git branch and relevant commit
> - Completed features
> - Files modified
> - Important decisions
> - Tests executed and results
> - Known errors
> - Unresolved tasks
> - Next implementation step
>
> ### Layer 3: Task-specific context
>
> Maintain concise task context for substantial development tasks.
>
> Include:
> - Task ID and objective
> - Acceptance criteria
> - Relevant files
> - Applicable API contracts
> - Database dependencies
> - Required tests
> - Important constraints
> - Completion status
>
> Do not create unnecessary context files for trivial changes.
>
> ## Phase 3 — Implement context handoff
>
> Create a repeatable context handoff workflow.
>
> Before ending a substantial development session:
>
> 1. Review current Git changes.
> 2. Record completed functionality.
> 3. Record important architecture decisions.
> 4. Preserve known bugs and limitations.
> 5. Record actual test evidence.
> 6. Identify the exact next task.
> 7. Update SESSION_CONTEXT.md.
> 8. Keep the handoff concise.
>
> Create a reusable session continuation prompt.
>
> The continuation prompt must instruct a fresh Codex session to read AGENTS.md, SESSION_CONTEXT.md, the development plan, and relevant Git state before modifying code.
>
> ## Phase 4 — Context compaction
>
> Study the compaction capabilities available in the installed Codex CLI.
>
> 1. Determine the correct native compaction mechanism.
> 2. Explain manual summarization versus native compaction.
> 3. Document when compaction is useful.
> 4. Define what information should survive compaction.
> 5. Avoid preserving obsolete errors and unnecessary repetitive logs.
> 6. Record actual compaction execution only if it occurs.
>
> If a supported native compaction command exists, provide exact instructions for its use.
>
> Do not simulate compaction by simply claiming that a Markdown summary is native compaction.
>
> Do not modify unsupported Codex internal settings.
>
> ## Phase 5 — Integration with custom agents
>
> Review the agents created in Prompt 005.
>
> Ensure:
> - Architecture Reviewer reads relevant architecture decisions.
> - Backend Engineer reads database and API context.
> - Frontend Engineer reads UI and API contracts.
> - QA Engineer reads acceptance criteria and test history.
> - Security Reviewer reads relevant security requirements.
> - Documentation Engineer maintains verified development records.
>
> Agents should receive task-relevant context rather than the entire history whenever possible.
>
> Keep AGENTS.md short and use referenced documents for detailed information.
>
> ## Phase 6 — Create a reusable context-management skill
>
> Create a Codex-compatible skill named:
>
> .agents/skills/context-handoff/SKILL.md
>
> The skill must support:
> 1. Inspecting current development state.
> 2. Producing a concise session summary.
> 3. Recording important decisions.
> 4. Capturing actual test results.
> 5. Listing unresolved work.
> 6. Preparing a fresh-session continuation prompt.
> 7. Documenting whether native compaction occurred.
>
> Follow the installed Codex skill conventions.
>
> Validate that the skill is discoverable and demonstrate an actual invocation if supported.
>
> ## Phase 7 — Practical context recovery test
>
> Perform a non-destructive demonstration:
>
> 1. Capture the current project state.
> 2. Generate a session handoff.
> 3. Compare the handoff against the current code and Git state.
> 4. Prepare a fresh-session continuation prompt.
> 5. Validate that the handoff contains sufficient information to identify the next development task.
> 6. If feasible, test restoration using a genuinely fresh Codex session or subagent.
>
> Do not change production or application business logic.
>
> ## Phase 8 — Documentation
>
> Create or update:
>
> - docs/CONTEXT_MANAGEMENT.md
> - docs/SESSION_CONTEXT.md
> - docs/CONTEXT_COMPACTION_LOG.md
> - docs/DEVELOPMENT_WORKFLOW.md
> - docs/AI_AGENTS.md
> - docs/AI_SKILLS.md
> - docs/WEEKLY_LOG.md
> - prompts/PROMPT_HISTORY.md
>
> Record this request as Prompt 006.
>
> Include:
> - Context management approach
> - Context layers
> - Actual Codex capabilities verified
> - Manual context summaries
> - Native compaction events, if any
> - Session recovery process
> - Skill invocation evidence
> - Challenges and lessons learned
>
> Do not invent automatic compaction events, token measurements, or successful agent invocations.
>
> ## Phase 9 — Validation
>
> Validate:
> 1. Documentation consistency
> 2. Correct file references
> 3. Skill structure
> 4. Context restoration instructions
> 5. Preservation of important development decisions
> 6. Absence of passwords and sensitive information
> 7. No unintended application modifications
>
> Provide a final report with:
> - Files created or modified
> - How context is managed
> - How native compaction works in this Codex version
> - Whether compaction actually occurred
> - How to resume development in a new session
> - Skill execution results
> - Known limitations
> - Recommended next development task
>
> Do not stop after planning.
>
> Implement and validate the context-management workflow now.

- **Improvements / implementation decisions:** Kept permanent context in existing AGENTS/architecture docs, made session state the current handoff, and reserved task briefs for substantial work. Added a self-contained handoff skill and task-scoped context reminders to the six existing profiles. Verified TUI `/status` and `/compact`; used actual compaction in a read-only session and tested recovery afterward. No unsupported feature settings were changed. Checked prompt history as it exists: the user-referenced Prompt 001 and Prompt 003 IDs are not separate exact entries; preserved existing history IDs rather than inventing missing records.
- **Output:** Added `context-handoff` skill, `CONTEXT_COMPACTION_LOG.md`, and `docs/task-context/P-2026-10-27-006.md`; updated AGENTS.md, context/session/development workflow docs, agent profiles, AI agent/skill guides, testing/challenge/weekly records, and this prompt history.
- **Actual execution evidence:** One native `/status` command ran. One native `/compact` event ran in a separate read-only interactive CLI session; a follow-up turn retained project state and reported no file changes. A fresh read-only ephemeral Codex session invoked `$context-handoff` and reviewed live Git state and handoff. That review found stale session status, which was corrected. The skill process emitted a transient RMCP HTTP 504 warning but still returned its review; cause is unknown.
- **Verification:** Skill validator passed; local Markdown link check passed for the reviewed docs; `git diff --check` passed; secret-pattern scan found only historical prompt wording, no credential. Application tests were not rerun because application behavior did not change. Full evidence is in `docs/TESTING.md`.
- **Follow-up:** Before schema work for multi-product tickets, agree with the human owner on identity, product roles, ownership, and cross-product visibility.

## P-2026-10-27-007 — Multi-product ticket management implementation

- **Exact execution prompt:** `Implement the plan.`
- **Purpose:** Execute the previously agreed Prompt 007 multi-product ticketing plan. The requirements, acceptance criteria, API contract, and decisions are captured in [`docs/task-context/P-2026-10-27-007.md`](../docs/task-context/P-2026-10-27-007.md).
- **Accepted decisions:** `/api/v1` APIs plus legacy route compatibility; legacy POST creates unassigned General/Medium tickets; existing tickets remain product/module/customer-unassigned; v1 tickets require product/category/priority; customers may use multiple products; demo assignees remain distinct from authenticated users; valid status transitions are unrestricted; future internal roles are proposed as product-scoped and customer users as customer-scoped. No authentication, RAG, or autonomous ticket mutation was implemented.
- **Implementation:** Added products, modules, customers/customer-product membership, demo assignees, comments, history, and ticket metadata with Alembic revision `0002_multi_product_tickets`; extended API/UI workflows and tests; made customer profile plus membership changes atomic. Legacy statuses `open`/`closed` normalize to `Open`/`Closed`. `resolved_at` is set when entering Resolved or Closed, retained across terminal states, and cleared on reopen.
- **Agent execution:** Separate backend and frontend implementation session subagents and a documentation subagent completed assigned scopes. Read-only Architecture Reviewer, QA Engineer, and Security Reviewer sessions provided planning reviews. These were live collaboration subagents; the project `.codex/agents/*.toml` profiles were not verified as loaded. No custom-profile execution is claimed.
- **Skill evidence:** Backend work followed `database-migration` and `fastapi-feature`, frontend followed `react-feature`, documentation followed `weekly-documentation`, and the parent applied `test-validation` and `context-handoff` workflows. No native Codex `$skill` CLI invocation was separately run for Prompt 007.
- **Database evidence:** PostgreSQL migration `0002_multi_product_tickets` applied and is at head. Three products and 17 modules exist. Four earlier tickets (IDs 1, 10001, 10005, 10006) remain, with the same ID/title/description checksum `f4d501934cc63bf44fbca786cfe82684`; all are unassigned to product/module/customer. Live Uvicorn smoke testing created ticket 10007 / `TEX-010007`, verified filtering, status/priority updates, and history. It was intentionally retained.
- **Validation:** Backend **23 passed** with `DATABASE_URL`; **20 passed, 3 skipped** without it. Each run emitted one Starlette/httpx deprecation warning. Frontend **11 passed across 3 files**; strict TypeScript and Vite production build passed. `docker compose config --quiet` passed; `alembic current` reported `0002_multi_product_tickets (head)`. `npm install` added the frontend test development dependencies and reported zero vulnerabilities. See [`docs/TESTING.md`](../docs/TESTING.md).
- **Challenges/fixes:** Corrected a frontend stylesheet import and UI test JSX/query cleanup issues. Changed customer edits from separate profile/membership requests to one atomic PATCH with rollback validation. Details are in [`docs/CHALLENGES.md`](../docs/CHALLENGES.md).
- **Limits and next work:** No browser end-to-end check, live OpenAI call, production deployment, authentication, or authorization testing was performed. The unauthenticated API and assistant are for local development only. Next implement identity and server-side product/customer authorization after choosing an identity provider and finalizing role permissions.
- **Context compaction:** No native compaction event was recorded for Prompt 007; session state was maintained in Markdown.
