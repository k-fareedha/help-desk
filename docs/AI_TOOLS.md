# AI Tools and Integrations

## Application integrations

- **OpenAI Python SDK** is declared in `backend/requirements.txt`. `POST /assistant` uses the Responses API if `OPENAI_API_KEY` is configured.
- **Model configuration:** `OPENAI_MODEL`, defaulting in code to `gpt-4.1-mini`.
- The assistant sends only the submitted question. No ticket retrieval, document retrieval, tools, agent framework, MCP integration, or model evaluation harness is implemented.
- **Database tooling:** SQLAlchemy 2.x, psycopg, and Alembic are used for PostgreSQL access and schema migrations; Docker Compose runs PostgreSQL 17 locally.

## Environment configuration

`.env.example` includes `OPENAI_API_KEY`, `OPENAI_MODEL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `DATABASE_URL`. The real `.env` is local and ignored by Git. Do not copy credentials into docs, prompts, logs, or source.

## Development tools actually used in this task

- Codex CLI `0.164.0` was installed. The user config selected `gpt-6-luna` with medium reasoning effort. The separate application assistant default remains `gpt-4.1-mini`.
- Docker 29.7.2, Docker Compose 5.5.0, Python 3.14.7, and PostgreSQL `17-alpine` were available in this environment.
- Three read-only host-session subagents completed architecture, QA, and security reviews. Their findings are in `docs/AGENT_WORKFLOW.md`.
- The native Codex `$test-validation` skill was invoked in a read-only CLI session. Six project skills were created and validated.
- Prompt 006 added the seventh project skill, `$context-handoff`; a fresh read-only `codex exec --ephemeral` invocation reviewed the handoff against Git state.
- In the interactive CLI, `/status` was executed and `/compact` was executed once in a separate read-only session, followed by a state-recall check. See `CONTEXT_COMPACTION_LOG.md` and `TESTING.md`.
- Project custom agent profiles are configured but not counted as executed: native CLI spawn attempts failed with a missing-rollout error and no receiver IDs.
- For Prompt 007, separate live session subagents completed backend, frontend, and documentation implementation; Architecture Reviewer, QA Engineer, and Security Reviewer also completed read-only planning/post-implementation reviews. These were real collaboration-tool delegations, but no native load of the project `.codex/agents/*.toml` profiles is claimed.
- Prompt 007 delegates followed the repository `database-migration`, `fastapi-feature`, `react-feature`, and `weekly-documentation` skill workflows. The main session followed `test-validation` and `context-handoff`; no separate native Codex CLI `$skill-name` invocation was run for Prompt 007.
- Frontend test development dependencies were installed with npm as explicitly authorized by the task; npm reported zero vulnerabilities. The installed UI checks are Vitest and React Testing Library.
- No project-configured MCP integration or Figma tool was used. The fresh CLI skill invocation logged a transient RMCP transport HTTP 504 warning before completing; no root cause or fix is known.

See `../prompts/PROMPT_HISTORY.md` for the task prompt and `TESTING.md` for actual commands and results.
