# Development Workflow

This workflow targets the local React/FastAPI/PostgreSQL prototype. Keep `.env` private and never expose this unauthenticated application to untrusted networks.

## Start the application

From the repository root:

```bash
docker compose up -d postgres
docker compose ps
set -a
. ./.env
set +a
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
backend/.venv/bin/uvicorn backend.main:app --reload --port 8000
```

In a separate terminal:

```bash
cd frontend
npm ci
npm run dev
```

The frontend uses `VITE_API_BASE_URL` if configured and otherwise calls `http://localhost:8000`. Local API documentation is at `/docs`.

For the original SQLite starter only, import after Alembic upgrade:

```bash
set -a
. ./.env
set +a
backend/.venv/bin/python -m backend.migrate_sqlite --sqlite-path backend/helpdesk.db
```

The importer is read-only against SQLite, preserves IDs and ticket text/status meaning, supplies required ticket number/category/priority values, checks conflicts, and adjusts the PostgreSQL sequence. Review its reported counts. Do not reset PostgreSQL or delete its volume.

## DBeaver verification

Use Driver `PostgreSQL`, host `localhost`, port `5433`, database `texol_support`, user `texol_user`, and the local `.env` password.

```sql
SELECT 1, current_database(), current_user, version();
SELECT version_num FROM alembic_version;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
SELECT id, ticket_no, product_id, module_id, customer_id, title, category, priority, status
FROM tickets ORDER BY id;
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE product_id IS NULL) AS unassigned
FROM tickets;
SELECT p.code, p.name, m.code AS module_code, m.name AS module_name
FROM products p LEFT JOIN product_modules m ON m.product_id = p.id
ORDER BY p.name, m.name;
SELECT COUNT(*) AS comments FROM ticket_comments;
SELECT COUNT(*) AS history_entries FROM ticket_history;
```

## Change and review loop

1. Read `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/SESSION_CONTEXT.md`, the development plan, task context, and relevant source/tests.
2. Inspect current branch, recent commits, dirty files, and relevant diffs. Keep inherited user changes separate from current task work.
3. Use SQLAlchemy sessions and transactional writes; use Alembic for schema changes. Use `/api/v1` for new APIs and retain documented compatibility behavior.
4. Run the backend suite and `docker compose config --quiet` from the repository root. Run `npm test` and `npm run build` from `frontend/` when frontend code changes.
5. For DB changes, review the migration upgrade/downgrade, backfill, constraints, and repeatability before applying. Verify current record counts/IDs before and after. Never run a destructive downgrade against persistent data without human approval.
6. Update architecture, testing, challenges, weekly, prompt, and session docs with observed results only.

## Agent and skill coordination

Use independent scopes and avoid parallel edits to shared files. Architecture review should precede schema/API decisions; backend and frontend may work in parallel after agreeing the contract; QA and security review should then check acceptance/security gaps; the main session integrates and decides. See [AI agents](AI_AGENTS.md), [skills](AI_SKILLS.md), and [agent workflow](AGENT_WORKFLOW.md).

Invoke relevant project skills such as `$database-migration`, `$fastapi-feature`, `$react-feature`, `$test-validation`, and `$weekly-documentation`. Use `$bug-investigation` for reproducible faults and `$context-handoff` for substantial session handoffs. A profile or skill file is not proof it was executed.

## Context handoff

For substantial work, read the current handoff and task brief before editing. Before stopping, update `docs/SESSION_CONTEXT.md` with verified branch/commit, changes, decisions, results, limitations, and one exact next step. Distinguish manual Markdown summarization from native `/compact`; record only compaction events that actually occurred. Continue from the copy-ready prompt and verify live Git/source state before implementation.

## Production boundary

There is no authentication or authorization. Product/customer IDs from a client are validated for relationship integrity, not user access. The API is unrestricted to clients that can reach it. Do not expose it, seed real customer data, or describe future role rules as enforced. Production use requires identity, role and customer authorization, least-privilege DB access, secrets/backup/monitoring policy, and deployment review.
