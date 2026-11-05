# Codex Skills

## Location and discovery

The six repository skills live under `.agents/skills/`, the native project skill directory. Each is an instruction-only folder containing `SKILL.md` with valid `name` and `description` YAML front matter. Codex can discover skills implicitly from their description or invoke them explicitly with `$skill-name`; `/skills` lists available skills in Codex CLI. Restart Codex if a skill edit does not appear.

| Skill | Path | Use for |
|---|---|---|
| `fastapi-feature` | `.agents/skills/fastapi-feature/SKILL.md` | FastAPI endpoints, validation, SQLAlchemy work, backend tests, and API docs. |
| `react-feature` | `.agents/skills/react-feature/SKILL.md` | React UI, API integration, user feedback states, responsiveness, and build checks. |
| `database-migration` | `.agents/skills/database-migration/SKILL.md` | PostgreSQL schema/data changes and Alembic migration review. |
| `bug-investigation` | `.agents/skills/bug-investigation/SKILL.md` | Reproducing, diagnosing, fixing, and documenting application bugs. |
| `test-validation` | `.agents/skills/test-validation/SKILL.md` | Selecting checks and reporting exact pass/fail/skipped evidence. |
| `weekly-documentation` | `.agents/skills/weekly-documentation/SKILL.md` | Factual weekly records and demo/presentation outlines. |
| `context-handoff` | `.agents/skills/context-handoff/SKILL.md` | Verify session/Git state, prepare concise handoffs, capture actual checks, and write a fresh-session continuation prompt. |

Invoke explicitly with prompts such as `$fastapi-feature Add a validated ticket endpoint with tests.` or `$database-migration Review this Alembic migration for data safety.`
For substantial work ending or starting in a new session, invoke `$context-handoff`.

## Validation and actual use

The original six skills passed the installed `skill-creator` `quick_validate.py` validator using Python 3 (`python3 .../quick_validate.py <skill-directory>`). The new `context-handoff` skill also passed that validator during Prompt 006. Each contains an invocation description, a short workflow, relevant validation steps, and expected reporting behavior.

During Prompt 005, a fresh read-only `codex exec` session was explicitly asked to use `$test-validation`. The CLI read the skill and reviewed testing evidence without running tests or accessing the database. It found a stale test-count note in `CHALLENGES.md`; that record was corrected. This is the one verified native CLI skill invocation in the task.

During Prompt 006, a fresh read-only `codex exec --ephemeral` session invoked `$context-handoff`, checked the live Git state and handoff, and returned a review without edits or tests. The other five skills were not invoked in Prompt 006. Across Prompt 005 and 006, `$test-validation` and `$context-handoff` have actual CLI invocation evidence. Skill files provide workflow guidance; they do not grant tools or permissions.

## Prompt 007 skill-guided work

- The backend implementation subagent followed the `database-migration` and `fastapi-feature` workflows; the frontend implementation subagent followed `react-feature`; this Documentation Engineer followed `weekly-documentation`. The parent followed the `test-validation` and `context-handoff` workflows while validating and refreshing session state.
- No native Codex CLI `$skill-name` invocation was separately executed during Prompt 007. The actual evidence is skill-directed work in the live session plus the recorded test commands and results; do not report a CLI skill invocation.
- The bug-investigation skill was not invoked as a separate workflow for Prompt 007. Frontend implementation reported and corrected its own CSS path and UI test setup issues; those fixes are listed in `CHALLENGES.md`.

OpenAI's official Codex skill documentation describes `SKILL.md`, the `.agents/skills` project path, and explicit `$` invocation: [Codex skills](https://developers.openai.com/codex/skills).
