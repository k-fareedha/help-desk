# Codex Agents

## Supported project configuration

This repository uses native Codex project configuration:

- `.codex/config.toml`: `[agents] enabled = true` and `max_concurrent_threads_per_session = 3`.
- `.codex/agents/*.toml`: one profile per custom agent, each with required `name`, `description`, and `developer_instructions`.
- Codex CLI inspected: `codex-cli 0.164.0`. `codex features list` reported `multi_agent` as stable and enabled. The existing user model is `gpt-6-luna` with medium reasoning; agent profiles inherit the parent model unless a request selects otherwise.

Six project profiles are configured:

| Agent | Profile | Scope |
|---|---|---|
| Architecture Reviewer | `.codex/agents/architecture-reviewer.toml` | Read-only architecture/API/schema review and risk analysis. |
| Backend Engineer | `.codex/agents/backend-engineer.toml` | FastAPI, SQLAlchemy, Alembic, and backend tests; no frontend edits without authorization. |
| Frontend Engineer | `.codex/agents/frontend-engineer.toml` | React/TypeScript UI and frontend checks; no backend edits without authorization. |
| QA Engineer | `.codex/agents/qa-engineer.toml` | Requirements, test, regression, and coverage review; no implementation edits. |
| Security Reviewer | `.codex/agents/security-reviewer.toml` | Read-only security review; do not inspect actual `.env` or unrelated secrets. |
| Documentation Engineer | `.codex/agents/documentation-engineer.toml` | Evidence-based project docs, prompts, test records, and weekly summaries. |

## Scope and safety limits

Codex custom agents inherit the parent session's sandbox, approval policy, provider, and MCP servers. Their TOML instructions cannot create an independent read-only sandbox. Reviewer profiles are instructed not to edit, but that is behavioral guidance, not a separate filesystem permission boundary. Select a safe parent permission mode before delegation, keep implementation scopes separate, and have the main agent integrate findings.

Agent instructions cannot substitute for human approval of destructive work. Do not ask a subagent to delete data, drop schema, reset a database, or remove a Docker volume. The main agent must stop and obtain human approval before such operations.

## Invocation

In Codex, ask for an agent by its `name`, for example:

```text
Ask architecture_reviewer to review the proposed API and database changes. Return findings only; do not edit files.
```

For independent review, request separate agents and wait for each result. Keep work on distinct files, and route final implementation choices through the main agent.

## Validation and evidence

The TOML files parse with Python `tomllib`. Codex CLI accepted the project configuration under `--strict-config`. During Prompt 005, three host-session subagents actually completed read-only reviews: Architecture Reviewer, QA Engineer, and Security Reviewer. Their findings were consolidated by the main agent and are summarized in `AGENT_WORKFLOW.md`.

A separate Codex CLI attempt to spawn the project `architecture_reviewer` profile returned `failed to load model context ... no rollout found`; the CLI emitted a review-like final message but had no receiver thread IDs. That attempt is not counted as a verified custom-profile execution. The profiles are configured, but a future CLI session should verify profile loading after the local rollout-store error is resolved.

OpenAI's official Codex documentation describes `.codex/agents/*.toml`, the required profile fields, inherited parent permissions, and `[agents]` controls: [Codex subagents](https://developers.openai.com/codex/subagents). The CLI feature list independently reported the multi-agent feature enabled in this installation.

## Prompt 007 execution evidence

- The main session delegated backend implementation and frontend implementation to separate live session subagents with disjoint ownership (`backend/**` and `tests/**` vs `frontend/**`). A Documentation Engineer handled documentation. The parent integrated their work and independently ran final checks.
- Read-only Architecture Reviewer, QA Engineer, and Security Reviewer sessions reviewed the architecture and proposed design before implementation. Separate post-implementation QA and Security reviews examined the implementation. QA findings led to timestamp edge-case/API tests and a missing UI save-handler fix; Security findings confirmed that the app must remain local-only until authentication and authorization exist.
- These are actual session subagent executions, but do not prove that the corresponding `.codex/agents/*.toml` custom profiles were loaded by native Codex profile spawning. No native custom-profile load is claimed for Prompt 007. Prior CLI custom-profile spawning remains unverified.
- The backend and frontend delegates followed the database-migration/FastAPI and React skill workflows; the Documentation Engineer followed weekly-documentation. The parent followed test-validation and context-handoff workflows. No native `$skill` CLI invocation was separately run for Prompt 007; see `AI_SKILLS.md` for this distinction.

## Context given to agents

Pass acceptance criteria and only the durable context needed for the assigned scope. Profiles route agents to relevant material: architecture plus plan for architecture review; API/database context for backend work; UI requirements and API contract for frontend work; acceptance criteria and test history for QA; applicable security rules and assigned safe files for security review; and `SESSION_CONTEXT.md` plus evidence for documentation. Avoid forwarding full prompt history by default. See `CONTEXT_MANAGEMENT.md` for the context layers and handoff procedure.
