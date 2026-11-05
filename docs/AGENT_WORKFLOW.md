# Agent Workflow

## Recommended coordination

```text
Requirement
   ↓
Architecture Reviewer (scope and API/data risks)
   ↓
Backend Engineer ───── Frontend Engineer (only when both are required; distinct files)
   ↓
QA Engineer ────────── Security Reviewer (independent read-only review)
   ↓
Documentation Engineer
   ↓
Main Codex agent integrates findings, validates, and reports to the user
```

The main agent decides whether delegation helps. Assign independent, narrow questions; avoid simultaneous edits to the same files. Reviewers return evidence and findings for the implementation agent or main agent to act on. Subagents inherit parent permissions, so select the parent sandbox/approval settings before spawning them.

## Use skills with agents

- Backend Engineer: `$fastapi-feature`; use `$database-migration` for schema/data work.
- Frontend Engineer: `$react-feature`.
- Architecture Reviewer: `$database-migration` as review guidance when reviewing schema changes.
- QA Engineer: `$test-validation`.
- Any role investigating a failure: `$bug-investigation`.
- Documentation Engineer: `$weekly-documentation`.

Invoke a skill by name in the task prompt, such as `$test-validation Verify ticket create/list/update against these acceptance criteria.` Skills provide repeatable task guidance; custom agents provide a role and delegated context.

## Parent responsibilities

The main Codex agent owns scope, approvals, cross-layer integration, and the final outcome. It must independently review delegated output, run relevant validation, and distinguish actual agent/skill executions from configured profiles. Never treat a profile or skill file as proof that it ran.

For destructive database or filesystem work, stop and obtain human approval. Agent TOML cannot enforce a different sandbox or approval policy for a subagent.

## Prompt 007 coordination

The multi-product feature used separate backend, frontend, and documentation session subagents after the API/schema contract was written in `docs/task-context/P-2026-10-27-007.md`. Backend scope was `backend/**` and `tests/**`; frontend scope was `frontend/**`; docs and the live migration were integrated by the main session. Architecture, QA, and Security reviewers provided planning reviews; QA and Security also performed post-implementation read-only reviews. QA findings led to timestamp edge-case tests and a fix for the ticket-detail save handler. These are real delegated session executions; loading the project `.codex/agents/*.toml` profiles was not verified.

The main session applied the additive Alembic migration, verified the four original ticket IDs and content checksum, and retained the separate live API smoke ticket. Final backend/frontend tests, TypeScript build, Compose config, and migration-head validation passed. Coverage does not include browser end-to-end checks or production/authentication security testing. See `TESTING.md` for evidence.

The implementation delegates followed `database-migration`, `fastapi-feature`, `react-feature`, and `weekly-documentation` workflows; the parent applied `test-validation` and `context-handoff` workflows. No separate native `$skill` CLI invocation occurred for Prompt 007. Skill-guided subagent work and native skill invocation are distinct forms of evidence.

## Prompt 005 evidence

Three actual read-only host-session subagents reviewed the migration: architecture, QA, and security. The Architecture Reviewer found no migration blocker and identified possible large-file scaling and status-enum concerns. QA confirmed evidence consistency, then identified and helped resolve a stale test-count note; it also documented automated/API/PostgreSQL coverage gaps. Security confirmed local port binding and credential handling, and flagged missing `.sqlite`/some backup ignore patterns; the ignore rules were expanded. The main agent incorporated these findings.

A native Codex CLI `$test-validation` skill invocation succeeded in read-only mode. Native Codex CLI custom-profile spawning was attempted but its collab backend returned a missing-rollout error; that attempt is documented as unverified. See `TESTING.md` and `CHALLENGES.md` for command evidence.
