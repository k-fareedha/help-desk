# Context Management

Use three small context layers. Keep project rules in one place and give agents only the task context they need.

## Context layers

1. **Permanent project context:** `AGENTS.md` holds concise development and safety rules; `docs/ARCHITECTURE.md` and `docs/DEVELOPMENT_PLAN.md` hold verified structure and roadmap. Do not copy these documents into every task note.
2. **Session context:** `docs/SESSION_CONTEXT.md` is the current handoff. Refresh it after substantial work with Git state, decisions, changed files, actual validation, unresolved tasks, and one next step.
3. **Task context:** For substantial tasks only, keep a concise task brief with its ID, objective, acceptance criteria, relevant files/API contracts/database dependencies, tests, constraints, and completion state. Store it alongside the task documentation and link it from the session handoff. Prompt 006's example is `task-context/P-2026-10-27-006.md`. Do not create task briefs for trivial edits.

## Start and resume

Before editing, read `AGENTS.md`, `docs/SESSION_CONTEXT.md`, `docs/DEVELOPMENT_PLAN.md`, and the task-specific brief if one exists. Then inspect `git status --short --branch`, the relevant diff, recent commits, and relevant code/tests. Confirm that recorded state still matches the repository. Separate inherited/uncommitted user work from changes made in the current task.

Copy the continuation prompt from `SESSION_CONTEXT.md` for a fresh CLI session. For a saved Codex thread, `codex resume` or the interactive `/fork` command can continue or branch the conversation; recheck the filesystem either way.

## Handoff before ending substantial work

Review Git changes, verified implementation, current decisions and limitations, actual test output, and open questions. Update `SESSION_CONTEXT.md`; place detailed test evidence in `TESTING.md`, actual prompt and execution evidence in `../prompts/PROMPT_HISTORY.md`, and issues in `CHALLENGES.md`. Keep obsolete errors only when their resolution explains a continuing constraint. Never record secrets, personal data, or unsupported assumptions as facts.

## Compaction

In interactive Codex CLI `0.164.0`, `/status` and `/compact` appeared in the native slash-command menu. `/status` ran and displayed session configuration. A separate fresh, read-only interactive session read the handoff/plan and ran `/compact`; a follow-up turn correctly recovered branch/HEAD, the PostgreSQL milestone, unresolved prerequisites, and next task without reopening files. The session changed no files. See the actual event in `CONTEXT_COMPACTION_LOG.md`.

Use `/status` to inspect the active CLI session and `/compact` when the same task should continue but accumulated conversation history is crowding the useful state. The command acts on the Codex conversation; it is distinct from manually writing `SESSION_CONTEXT.md`. Interactive manual compaction is verified. Automatic compaction behavior is not independently verified in this CLI session; in `features list`, `context_management` and `async_compaction` were marked under development and disabled. No project setting was changed to enable them.

After compaction, verify the retained objective, constraints, decisions, current state, validation evidence, and next step against repository files. Keep durable project facts in docs and Git, not only in model context. Do not add a compaction log entry unless the command actually ran.

## Custom agent context

Use the task brief and relevant durable documents rather than forwarding the full prompt history:

- Architecture Reviewer: architecture, plan, task brief, and affected source.
- Backend Engineer: API/database context, acceptance criteria, affected source and tests.
- Frontend Engineer: UI requirements and the relevant API contract.
- QA Engineer: acceptance criteria, test history, and current diff.
- Security Reviewer: applicable security rules and only the assigned safe files.
- Documentation Engineer: current session state and evidence supporting each claim.

Agent profiles include these routing reminders. They do not create permission boundaries; the main Codex session remains responsible for safe delegation and integration.

## Actual evidence for Prompt 006

- `codex --version` reported `codex-cli 0.164.0`; `codex features list` reported `multi_agent` stable/enabled, `context_management` under development/disabled, and `async_compaction` under development/disabled.
- An interactive CLI probe showed `/status` and `/compact` in the command picker. Running `/status` returned session configuration. A separate meaningful read-only CLI session completed one actual `/compact` and retained the facts listed in the compaction log.
- A fresh `codex exec --ephemeral` session invoked `$context-handoff`, read the durable context and live Git state, and confirmed branch/HEAD plus the next requirements task. It found a stale path count, which was corrected in `SESSION_CONTEXT.md`. It concluded the handoff is sufficient for requirements clarification, while product implementation still requires human policy decisions.
- No token measurements, automatic compaction, or manual-to-native equivalence are claimed. Skill validation and exact command output are recorded in `TESTING.md`.
