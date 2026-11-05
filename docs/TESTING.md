# Testing and Validation

## Repeatable checks

From the repository root, with backend dependencies installed:

```bash
backend/.venv/bin/python -m pytest tests -q
docker compose config --quiet
```

Run `npm test` and `npm run build` from `frontend/` when frontend code changes.

For a local PostgreSQL integration check, copy `.env.example` to `.env`, set a private random `POSTGRES_PASSWORD`, start the service, load environment variables, and apply the migration:

```bash
docker compose up -d postgres
docker compose ps
set -a
. ./.env
set +a
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
backend/.venv/bin/python -m backend.migrate_sqlite --sqlite-path backend/helpdesk.db
```

Run the frontend build with `npm run build` from `frontend/` when frontend code changes.

## Current automated coverage

- `tests/test_api.py`: FastAPI TestClient requests over an isolated in-memory SQLite schema. Covers product/module/customer/assignee CRUD validation, ticket create/detail/update, filtering and pagination, comments/history, transaction rollback, legacy route behavior, customer membership integrity, dashboard counts, and relationship constraints.
- `tests/test_sqlite_migration.py`: ID/value preservation, repeatable import, conflicting-ID rollback, source-file immutability, legacy schema compatibility, and required defaults/status normalization.
- `tests/test_database.py`: when `DATABASE_URL` is set, checks PostgreSQL connectivity, rollback of temporary transactional work, migration/catalog tables, seeded products/modules, and schema availability. These checks do not change ticket records.
- `frontend/src/**/*.test.tsx`: Vitest and React Testing Library coverage for API handling, ticket form choices/validation, workspace loading/errors, ticket update/comments, and customer membership editing.
- `npm run build`: runs strict TypeScript checking followed by the Vite production build.

The live PostgreSQL migration and Uvicorn smoke test provide separate evidence beyond the isolated SQLite-backed API test fixture. No browser end-to-end runner is configured.

## Validation results — 2026-10-27

- `backend/.venv/bin/pip install -r backend/requirements.txt`: passed after the initial sandboxed attempt could not resolve PyPI. Installed SQLAlchemy, Alembic, psycopg, and declared requirements into the ignored project venv.
- `docker compose config --quiet`: passed.
- `docker compose up -d postgres`: passed; PostgreSQL 17 started with status `healthy`, bound to `127.0.0.1:5433`.
- `backend/.venv/bin/alembic -c backend/alembic.ini upgrade head`: passed after correcting the Alembic package import path. Created `tickets` and `alembic_version`.
- `backend/.venv/bin/python -m backend.migrate_sqlite --sqlite-path backend/helpdesk.db`: passed; `source=0, inserted=0, already_present=0, verified=0`. The original SQLite database had no ticket rows and was opened read-only.
- Synthetic SQLite import: two records with IDs 10001 and 10005 were imported and verified. Repeating the import reported `inserted=0, already_present=2, verified=2`.
- Live Uvicorn HTTP smoke check on port 18080: POST returned ID 1, PATCH changed it to `closed`, and GET returned it. After restarting the PostgreSQL container, GET still returned the same row. After the synthetic IDs were imported, a subsequent POST received ID 10006, confirming sequence adjustment.
- PostgreSQL CLI checks confirmed `current_database() = texol_support`, `current_user = texol_user`, and the expected public tables `alembic_version` and `tickets`.
- `backend/.venv/bin/python -m pytest tests -q` with `.env` loaded: **11 passed in 1.01s** on the final Prompt 005 run. This includes the NULL-status SQLite import regression test.
- `git diff --check`: passed after the final documentation update.

### Actual PostgreSQL commands used

The local password is not shown here. Commands were run from the repository root:

```bash
docker compose up -d postgres
docker compose ps
set -a
. ./.env
set +a
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
backend/.venv/bin/python -m backend.migrate_sqlite --sqlite-path backend/helpdesk.db
backend/.venv/bin/python -m backend.migrate_sqlite --sqlite-path /tmp/texol_pg_sequence_fixture.db
docker compose restart postgres
docker compose exec -T postgres psql -U texol_user -d texol_support -c "select current_database(), current_user; select version_num from alembic_version; select count(*) as ticket_count, max(id) as max_ticket_id from tickets;"
```

Uvicorn ran on `127.0.0.1:18080` because port 8000 was occupied. The HTTP checks were:

```bash
curl http://127.0.0.1:18080/tickets
curl -X POST http://127.0.0.1:18080/tickets -H 'Content-Type: application/json' --data '{"title":"PostgreSQL smoke check","description":"Created to verify API persistence across a container restart."}'
curl -X PATCH http://127.0.0.1:18080/tickets/1 -H 'Content-Type: application/json' --data '{"status":"closed"}'
curl http://127.0.0.1:18080/tickets
curl -X POST http://127.0.0.1:18080/tickets -H 'Content-Type: application/json' --data '{"title":"PostgreSQL sequence check","description":"API-generated ID after importing IDs 10001 and 10005."}'
```

The HTTP smoke check left clearly named local validation tickets in the project development database; no database or volume was removed. The original SQLite database remains intact.

## Checks not run during the PostgreSQL foundation milestone

- Frontend build: not run in the earlier database-only milestone because frontend files did not change. Prompt 007 later ran and passed the frontend test suite and production build as recorded below.
- OpenAI live assistant call: not run; no provider key was configured.
- Production deployment, concurrent load, and authentication/security testing: not run; these are outside the current starter implementation.

## Prompt 005 agent and skill validation — 2026-10-27

- `codex --version`: `codex-cli 0.164.0`.
- `codex features list`: `multi_agent` reported **stable, enabled**.
- Python `tomllib` parsed `.codex/config.toml` and all six `.codex/agents/*.toml` files; required profile fields were present.
- `codex exec --strict-config --ephemeral --sandbox read-only ...` loaded project instructions and reported the configured maximum of three concurrent agents. This confirms project config loading, not custom profile execution.
- `python3 /home/texol/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>` passed for all six skills.
- Three read-only host-session review subagents (architecture, QA, security) completed. The native CLI attempt to spawn a project custom profile failed with a missing-rollout error; it is not counted as custom-profile execution.
- A separate read-only Codex CLI task explicitly invoked `$test-validation` and completed successfully. It did not rerun tests, edit files, or inspect the database; it reviewed the recorded evidence and found the stale test-count note that has since been corrected.
- `git diff --check` and `.env`/database-backup ignore checks passed. No PostgreSQL migration, schema, record, or volume operation was performed for Prompt 005.

## Prompt 006 context handoff and compaction — 2026-10-27

- `codex --version`: `codex-cli 0.164.0`.
- `codex features list`: `multi_agent` stable/enabled; `context_management` and `async_compaction` under development/disabled.
- Interactive Codex slash-command picker exposed `/status` and `/compact`. `/status` ran and showed session configuration. No credentials/account details from the status view were copied into project docs.
- **Native compaction demonstration:** started a separate read-only interactive CLI session with `codex --no-alt-screen --sandbox read-only --ask-for-approval never`; asked it to inspect `AGENTS.md`, `SESSION_CONTEXT.md`, and `DEVELOPMENT_PLAN.md`, ran `/compact`, then asked it to recall project state without rereading files. It recovered the branch/HEAD, PostgreSQL milestone, product ownership/identity/roles/visibility prerequisite, and exact next task. The probe changed no files. This was one actual native manual compaction; it was not an automatic compaction or token-reduction measurement. See `CONTEXT_COMPACTION_LOG.md`.
- **Fresh-session/skill demonstration:** Executed `codex exec --ephemeral --sandbox read-only -C . '$context-handoff Read AGENTS.md, docs/SESSION_CONTEXT.md, docs/DEVELOPMENT_PLAN.md, docs/CONTEXT_MANAGEMENT.md, and current Git status. Perform a read-only handoff review: report whether the stated branch/HEAD and next task match, identify any stale or unverified item, and say whether this is sufficient context for a fresh implementation session. Do not edit files, run tests, or access the database.'` in a fresh read-only CLI session. It read the project context and Git state, confirmed branch and HEAD, and verified the next task. It found the current dirty-tree count was 31 paths (12 tracked modified, 19 untracked), not the earlier 30-path baseline; `SESSION_CONTEXT.md` now distinguishes the two. It concluded the handoff supports requirements clarification, while implementation still requires human policy decisions. The check made no file changes and did not run tests or access the database.
- The fresh CLI skill session emitted a transient RMCP transport warning: `UnexpectedServerResponse("HTTP 504: error code: 504")`. The requested review still completed; the warning's root cause is unknown and no fix is claimed.
- `python3 /home/texol/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/context-handoff`: **passed** (`Skill is valid!`).
- Local Markdown links in 13 Prompt 006 Markdown files: **no broken links**.
- `git diff --check`: **passed**.
- Secret-pattern scan found no credential; its only textual match was the historical prompt wording “Password: From local .env”. No `.env` content was read.
- Application backend tests were **not rerun** because this task changes documentation/agent instructions and adds a documentation skill only. The earlier Prompt 005 backend result remains 11 passed in 1.01s; see above. No database or Docker volume operation occurred.

## Prompt 007 — Multi-product ticketing validation — 2026-10-27

### Applied migration and preserved records

- PostgreSQL Compose service remained healthy. The parent applied the additive Alembic upgrade from `0001_initial_tickets` to `0002_multi_product_tickets`; `alembic current` reported `0002_multi_product_tickets (head)`.
- The verified public tables are `alembic_version`, `assignees`, `customer_products`, `customers`, `product_modules`, `products`, `ticket_comments`, `ticket_history`, and `tickets`.
- Three products and 17 product modules were seeded. The four pre-existing ticket IDs (1, 10001, 10005, 10006) remained. A pre/post checksum of ID/title/description was `f4d501934cc63bf44fbca786cfe82684`. Their known lowercase statuses were normalized to two `Open` and two `Closed`; all four remain unassigned to product/module/customer.
- A live Uvicorn run on `127.0.0.1:18081` created ticket ID 10007 / `TEX-010007`, filtered it, patched status `Open` → `Triaged` and priority `Low` → `Medium`, then read its creation/field history. This clearly identified smoke-test record was intentionally retained; no existing record or volume was deleted/reset.

### Automated checks

- Backend with `DATABASE_URL` configured: `backend/.venv/bin/python -m pytest tests -q` — **23 passed**, with one Starlette/httpx deprecation warning.
- Backend with `DATABASE_URL` unset: `backend/.venv/bin/python -m pytest tests -q` — **20 passed, 3 skipped**, with the same deprecation warning. The skipped cases require a configured PostgreSQL URL.
- Frontend: `npm test -- --reporter=dot` from `frontend/` — **11 passed across 3 test files**.
- Frontend: `npm run build` from `frontend/` — passed. The script runs strict TypeScript type checking and the Vite production build.
- `docker compose config --quiet` — passed.
- `backend/.venv/bin/alembic -c backend/alembic.ini current` (with local environment loaded) — reported `0002_multi_product_tickets (head)`.
- `npm install` added frontend test development dependencies; npm reported zero vulnerabilities.

### Prompt 007 commands and live API evidence

The parent applied the migration with local variables loaded without printing them:

```bash
set -a
. ./.env
set +a
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
```

Frontend test dependencies were added as development dependencies:

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom jsdom
```

The live API smoke check ran with Uvicorn bound to loopback on port 18081:

```bash
set -a
. ./.env
set +a
backend/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 18081
```

The actual HTTP operations were:

```bash
curl -X POST http://127.0.0.1:18081/api/v1/tickets \
  -H 'Content-Type: application/json' \
  --data '{"product_id":1,"module_id":1,"title":"Prompt 007 PostgreSQL validation","description":"Local API smoke-check record; intentionally retained.","category":"General","priority":"Low"}'
curl 'http://127.0.0.1:18081/api/v1/tickets?product_id=1&page=1&page_size=2'
curl -X PATCH http://127.0.0.1:18081/api/v1/tickets/10007 \
  -H 'Content-Type: application/json' \
  --data '{"status":"Triaged","priority":"Medium"}'
curl http://127.0.0.1:18081/api/v1/tickets/10007/history
```

The smoke ticket was retained; no cleanup or deletion request was run.

### Coverage and limits

Backend tests cover products/modules and duplicate handling, customer-product membership and relationship constraints, assignees, ticket validation/detail/filtering/pagination/dashboard, comments/history and rollback atomicity, legacy route shape/normalization, atomic customer profile/membership updates and validation rollback, and PostgreSQL connectivity/schema/seeds/rollback. The four original development tickets were verified separately on the live database; backend API unit/integration fixtures otherwise use an isolated in-memory SQLite database.

Frontend tests cover API client paths/errors, ticket form product-dependent selections/validation, application-level flows including loading/error feedback, and customer membership update success/failure. The Vite build and strict type check passed. No browser-based end-to-end run, production deployment, authentication/authorization test, concurrency/load test, or live OpenAI call was performed. The assistant endpoint remains unauthenticated and sends only the submitted question to OpenAI when configured.

### DBeaver verification queries

```sql
SELECT current_database(), current_user, version();
SELECT version_num FROM alembic_version;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
SELECT code, name, is_active FROM products ORDER BY code;
SELECT p.code AS product_code, m.code AS module_code, m.name AS module_name
FROM products p JOIN product_modules m ON m.product_id = p.id
ORDER BY p.code, m.name;
SELECT id, ticket_no, product_id, module_id, customer_id, title, priority, status
FROM tickets ORDER BY id;
SELECT COUNT(*) AS ticket_count,
       COUNT(*) FILTER (WHERE product_id IS NULL) AS unassigned_count
FROM tickets;
SELECT COUNT(*) AS comment_count FROM ticket_comments;
SELECT COUNT(*) AS history_count FROM ticket_history;
```
