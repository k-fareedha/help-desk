# Texol AI Support Hub

Texol AI Support Hub is a local internal prototype for managing support tickets across Vanforces, Taskforce, and Speak Order. It includes product/module and customer directories, ticket triage, comments, activity history, and a dashboard. The prototype has **no authentication or authorization**; do not expose it to customers or deploy it with real customer data.

## Stack

- React 18, TypeScript, Vite, Vitest, and React Testing Library (`frontend/`)
- FastAPI, Pydantic, SQLAlchemy 2.x, psycopg, and Alembic (`backend/`)
- PostgreSQL 17 in Docker Compose
- Optional backend-only OpenAI Responses API assistant; it receives the submitted question only, not ticket data

## Local setup

Prerequisites: Python 3.10+, Node.js 20+, npm, and Docker Compose.

1. Create `.env` from the template and replace the placeholder with a private local password. `.env` is ignored by Git.

   ```bash
   cp .env.example .env
   python -c "import secrets; print(secrets.token_hex(24))"
   ```

2. Install dependencies and start the database:

   ```bash
   python -m venv backend/.venv
   backend/.venv/bin/pip install -r backend/requirements.txt
   docker compose up -d postgres
   docker compose ps
   cd frontend && npm ci && cd ..
   ```

   PostgreSQL is published only on `127.0.0.1:5433`; persistent data lives in `postgres_data`. Compose does not start FastAPI.

3. Apply Alembic migrations and, if needed, import the original SQLite tickets. The import opens SQLite read-only and is repeatable.

   ```bash
   set -a
   . ./.env
   set +a
   backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
   backend/.venv/bin/python -m backend.migrate_sqlite --sqlite-path backend/helpdesk.db
   ```

   Revision `0002_multi_product_tickets` seeds the initial products/modules, backfills existing tickets without assigning products or customers, and preserves their IDs, titles, and descriptions. It was applied to the local development database; the four existing IDs remained present. Never reset the database or remove its volume to apply migrations.

4. Start FastAPI from the repository root:

   ```bash
   set -a
   . ./.env
   set +a
   backend/.venv/bin/uvicorn backend.main:app --reload --port 8000
   ```

   API docs: <http://localhost:8000/docs>.

5. In another terminal, start the frontend:

   ```bash
   cd frontend
   npm run dev
   ```

   Open <http://localhost:5173>. The optional API base is `VITE_API_BASE_URL`; it defaults to `http://localhost:8000`.

## Application behavior

- Dashboard: ticket totals, priority/status indicators, product counts, recent tickets, optional product filter.
- Products: create/edit/deactivate products and manage their modules.
- Customers: create/edit/deactivate customers and associate them with multiple products.
- Tickets: search and filter a paginated queue; create product-scoped tickets; view details, comments, and history; update ticket fields.
- Assignees: maintain a local demo directory. Assignees are not authenticated users.
- AI assistant: optional standalone question/answer flow; it does not query ticket records.

The new API is under `/api/v1`. Existing `/tickets` and `/assistant` endpoints remain for compatibility. Customer profile fields and `product_ids` can be changed atomically through `PATCH /api/v1/customers/{id}`; `PUT /api/v1/customers/{id}/products` is also available for membership-only replacement. The legacy `POST /tickets` accepts `{ "title": "Login issue", "description": "Password reset fails" }` and creates an explicitly unassigned General/Medium ticket. New ticket requests should use `/api/v1/tickets` and include product, category, and priority.

Example v1 request (replace `product_id` with an ID returned by `GET /api/v1/products`):

```json
{
  "product_id": 1,
  "module_id": 1,
  "title": "Invoice export is failing",
  "description": "CSV export returns an error for this account.",
  "category": "Bug",
  "priority": "High"
}
```

Ticket status values are `Open`, `Triaged`, `In Progress`, `Testing`, `Resolved`, and `Closed`. `resolved_at` is set on entering Resolved or Closed, retained across terminal states, and cleared if reopened. Product/module/customer/assignee records are deactivated rather than deleted. Ticket history records field changes, and comments/history identify their actor as `Local demo operator` because no authenticated identity exists.

## API and database verification

Use DBeaver's PostgreSQL driver:

- Host: `localhost`
- Port: `5433`
- Database: `texol_support`
- Username: `texol_user`
- Password: local `.env`

```sql
SELECT 1, current_database(), current_user;
SELECT version_num FROM alembic_version;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
SELECT id, ticket_no, product_id, module_id, customer_id, title, category, priority, status
FROM tickets ORDER BY id;
SELECT COUNT(*) AS ticket_count,
       COUNT(*) FILTER (WHERE product_id IS NULL) AS unassigned_legacy_count
FROM tickets;
SELECT p.code, p.name, m.code AS module_code, m.name AS module_name
FROM products AS p LEFT JOIN product_modules AS m ON m.product_id = p.id
ORDER BY p.name, m.name;
SELECT c.code, c.name, array_agg(p.code ORDER BY p.code) AS product_codes
FROM customers AS c JOIN customer_products AS cp ON cp.customer_id = c.id
JOIN products AS p ON p.id = cp.product_id
GROUP BY c.id, c.code, c.name ORDER BY c.name;
```

## Checks

From the repository root, run the backend suite and Compose validation:

```bash
backend/.venv/bin/python -m pytest tests -q
docker compose config --quiet
```

From `frontend/`, run:

```bash
npm test
npm run build
```

See [docs/TESTING.md](docs/TESTING.md) for actual test evidence and coverage limitations.

## Security and production boundary

This prototype has no login, roles, or server-side user authorization. Local CORS and localhost database binding are development safeguards, not API authorization. Do not expose the API or use it with real customer data. The future role/visibility model in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) is a proposal only. Authentication, authorization, production secrets, database least-privilege roles, backups, and deployment hardening must be designed before production use.

## Development references

See [AGENTS.md](AGENTS.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md), [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md), [docs/AI_AGENTS.md](docs/AI_AGENTS.md), [docs/AI_SKILLS.md](docs/AI_SKILLS.md), [docs/AGENT_WORKFLOW.md](docs/AGENT_WORKFLOW.md), [docs/TESTING.md](docs/TESTING.md), [docs/CHALLENGES.md](docs/CHALLENGES.md), [docs/SESSION_CONTEXT.md](docs/SESSION_CONTEXT.md), [docs/CONTEXT_MANAGEMENT.md](docs/CONTEXT_MANAGEMENT.md), and [prompts/PROMPT_HISTORY.md](prompts/PROMPT_HISTORY.md).
