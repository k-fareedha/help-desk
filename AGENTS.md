# Codex Development Instructions

## Project purpose

Texol AI Support Hub is a learning-focused support ticket starter intended to grow into a centralized ticket system for Vanforces, Taskforce, and Speak Order. Keep changes incremental and grounded in the existing repository; do not assume product workflows or integrations that have not been specified.

## Technology and repository layout

- Frontend: React 18, TypeScript, and Vite in `frontend/`.
- Backend: FastAPI and Python in `backend/`.
- Persistence: PostgreSQL through SQLAlchemy 2.x and psycopg; Alembic manages schema versions. `backend/migrate_sqlite.py` reads and imports the legacy SQLite ticket data.
- Optional AI: OpenAI Python SDK, called from backend code only.
- `tests/`: backend API tests.
- `backend/migrations/`: Alembic environment and versioned schema migrations.
- `docker-compose.yml`: local PostgreSQL 17 service and persistent volume.
- `docs/`: architecture, testing, weekly development, and context-management notes.
- `prompts/PROMPT_HISTORY.md`: actual prompts, outcomes, and debugging notes.

Read `README.md` and `docs/ARCHITECTURE.md` before changing application code. Inspect the relevant source and tests before deciding how to change them. Do not treat roadmap items or examples in documentation as implemented features.

## Coding conventions

- Keep changes small, focused, and consistent with the existing code and project dependencies.
- Prefer clear, maintainable code over unnecessary abstractions or new dependencies.
- Validate and normalize user input at the API boundary. Keep frontend validation for usability, not as a substitute for backend validation.
- Handle API and external-service failures explicitly; do not silently present failed operations as successful.
- Keep secrets and environment-specific configuration out of source code. Follow the existing environment-variable configuration pattern.

## API and database standards

- Keep external AI calls in backend code only. Never expose provider credentials to the browser.
- Use parameterized SQL for every query containing values; never build SQL by interpolating user input.
- Use SQLAlchemy sessions for application database work and Alembic for schema changes. Read `DATABASE_URL` from the environment; never commit local `.env` credentials.
- Validate request data and return appropriate HTTP errors for invalid or unavailable operations.
- Preserve existing API behavior unless a change is intentional and documented. Update the frontend and tests when API contracts change.
- Make schema changes deliberate and safe for existing data. Keep the original SQLite database read-only during imports. Do not drop, overwrite, or reset user data or Docker volumes without explicit human approval.
- Require human confirmation before an agent changes ticket state. AI output alone must not trigger a ticket mutation.

## Testing and validation

- Add or update tests for behavior changes and bug fixes. Keep tests focused on observable behavior and regression risks.
- Run the relevant existing automated tests and validation commands before marking work complete. The documented commands are in `docs/TESTING.md`; use the commands appropriate to the changed area.
- If a check cannot be run, state which check was not run and why. Report actual results; never claim tests or builds pass without running them.
- Do not install packages unless the task requires it and installation is authorized. Do not invent test commands; check project documentation and manifests.

## Security restrictions

- Never commit API keys, credentials, personal data, or other secrets. Do not copy real secrets into examples, tests, logs, or prompt history.
- Keep database access parameterized and enforce validation on the backend.
- Do not send ticket content to an AI provider unless the feature explicitly requires it and the data flow is documented.
- Do not allow an agent or AI response to change ticket state without human confirmation.
- Obtain explicit human approval before destructive actions, including deleting or resetting data, dropping schema, or overwriting user work.

## Documentation and context preservation

- Update relevant documentation when behavior, API contracts, data structures, setup, or development workflow changes. Keep documentation consistent with code.
- Record major prompts, outcomes, and debugging in `prompts/PROMPT_HISTORY.md`. Do not record secrets or personal data.
- For substantial work, preserve a concise summary of decisions, changed files, validation results, and open issues in the relevant context notes so future sessions can continue accurately.
- Implement one small feature per commit. Keep each commit focused; do not combine unrelated changes.

## Codex agents and skills

- Project agents live in `.codex/agents/`; reusable task skills live in `.agents/skills/`. Read `docs/AI_AGENTS.md`, `docs/AI_SKILLS.md`, and `docs/AGENT_WORKFLOW.md` for roles and invocation guidance.
- Delegate independent work with a clear question and expected result. Keep implementation scopes separate and avoid concurrent edits to the same files. The main agent integrates findings and owns final decisions.
- Invoke relevant skills by name (for example `$fastapi-feature`, `$database-migration`, or `$test-validation`). Use `$context-handoff` for substantial session handoffs. A configuration file is not evidence that an agent or skill ran; record actual execution evidence. See `docs/CONTEXT_MANAGEMENT.md` for the detailed workflow.
- Custom agents inherit the parent sandbox and approval settings. Read-only wording does not create a separate permission boundary. Obtain human approval before destructive changes.

## Definition of Done

A task is complete only when:

1. The requested change is implemented without unrelated application changes.
2. Relevant tests and validation have been run, and their actual results are reported; any unrun checks are identified with a reason.
3. Tests are added or updated for changed behavior, and relevant documentation is updated.
4. No secrets or personal data were introduced, and destructive changes have explicit human approval.
5. The final summary states what changed, the files affected, and the validation performed.
