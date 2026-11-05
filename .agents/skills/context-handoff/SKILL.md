---
name: context-handoff
description: Capture verified repository and session state, decisions, test evidence, open work, and a concise continuation prompt before ending or resuming substantial Codex development sessions.
---

# Context Handoff

Use this skill before ending substantial work or when preparing a fresh Codex session. Keep the handoff factual, brief, and useful for the next action.

## Workflow

1. Read `AGENTS.md`, `docs/SESSION_CONTEXT.md`, the relevant development plan, and task-specific requirements.
2. Inspect `git status --short --branch`, recent commits, and the relevant diff. Separate pre-existing changes from work performed in this task.
3. Verify implementation state from source, tests, and documentation. Preserve decisions, limitations, and known errors that still affect the next task.
4. Record only commands and test results actually observed. Label checks that were not run and why.
5. Update `docs/SESSION_CONTEXT.md` with milestone, branch/commit, changed files, decisions, validation, unresolved work, and one precise next step.
6. If Codex native compaction ran, record the actual command and session/date in `docs/CONTEXT_COMPACTION_LOG.md`. Otherwise state that no compaction occurred; a Markdown handoff is manual summarization.
7. Prepare a fresh-session prompt that tells Codex to re-read `AGENTS.md`, `SESSION_CONTEXT.md`, the development plan, task context, and current Git state before editing.
8. Compare the handoff against the current repository state and remove stale, repetitive, secret, or personal information.

## Expected output

- Updated session handoff, when substantial state changed.
- Verified decisions and actual validation evidence.
- Open questions or blockers and the exact next task.
- A copy-ready continuation prompt.
- A clear statement distinguishing manual summary, native compaction, and fresh-session testing.

Do not claim compaction, fresh-session recovery, test execution, agent execution, or skill execution unless it actually occurred and can be evidenced.
