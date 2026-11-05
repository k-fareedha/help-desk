---
name: weekly-documentation
description: Prepare factual Wednesday development records, prompt history, evidence summaries, and demo outlines from repository changes and observed checks.
---

# Weekly development documentation workflow

Use this skill to prepare a weekly session record or submission summary.

1. Inspect `git status`, relevant diffs/commits, prompt history, and current session context.
2. Identify implemented work and distinguish it from plans, experiments, and unfinished items.
3. Collect test and tool outputs that actually exist. Do not infer passing tests from code or configuration.
4. Record only agents and skills that were actually invoked; include tool/model details only when known.
5. Update `docs/WEEKLY_LOG.md` and relevant testing, session, challenge, architecture, or agent/skill docs.
6. Prepare a concise presentation outline and demo checklist from verified behavior. Mark any unrun demo steps clearly.
7. Run `git diff --check` and summarize changed docs and evidence.

Never invent prompts, errors, agent or skill executions, test results, or context compaction events. Never include credentials or personal data.
