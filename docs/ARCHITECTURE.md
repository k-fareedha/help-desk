# Application Architecture

## Status

Prompt 007's additive PostgreSQL migration and multi-product prototype have been implemented and validated. The live database reports Alembic revision `0002_multi_product_tickets (head)` and contains `alembic_version`, `assignees`, `customer_products`, `customers`, `product_modules`, `products`, `ticket_comments`, `ticket_history`, and `tickets`. It has three seeded products and 17 modules. The application still has no authentication or authorization.

## Components and flow

```text
React + TypeScript + Vite (localhost:5173)
    → FastAPI REST API (localhost:8000)
        → SQLAlchemy 2.x session / transaction
            → PostgreSQL 17 (Docker, host 127.0.0.1:5433)

Optional standalone assistant route → OpenAI Responses API
```

- `frontend/src/`: single-page local prototype, typed API client, ticket form, pages and view components.
- `backend/main.py`: FastAPI routes, validation calls, database session dependency, transactional write helpers, response assembly.
- `backend/models.py` / `backend/schemas.py`: SQLAlchemy entities and Pydantic request/response contracts.
- `backend/migrations/`: Alembic schema revisions. The initial migration created `tickets`; Prompt 007 adds product-aware schema and seeds.
- `backend/migrate_sqlite.py`: read-only and repeatable legacy SQLite ticket import, including default category/priority and deterministic ticket number.
- `tests/`: backend API, database, and importer tests. Frontend tests are under `frontend/src/` and run with Vitest.

The application reads `DATABASE_URL`; Compose reads database settings from local `.env`. Alembic, rather than application startup, creates/updates the schema.

## Data model

- `products` owns `product_modules`; product name and code are unique. Initial seeded products are VF/Vanforces, TF/Taskforce, and SO/Speak Order.
- `customers` has a many-to-many relationship with products through `customer_products`.
- `assignees` is a demo directory and is not an authenticated-user table.
- `tickets` has a unique `ticket_no`, classification, product/module/customer links, optional assignee, timestamps, and optional `resolved_at`. Composite foreign keys ensure a module belongs to its product and a customer is associated with the ticket's product. Product/module/customer links remain nullable for legacy/unassigned tickets; the v1 creation API requires product, category, and priority.
- `ticket_comments` and `ticket_history` are append-only application records linked to tickets. Ticket edits and history rows are committed in the same transaction. The demo attribution is the fixed label `Local demo operator`.
- No application operation deletes tickets, products, customers, modules, or assignees; catalog entities are deactivated.

Initial categories: Bug, Feature Request, Technical Support, Integration Issue, Performance Issue, General. Priorities: Low, Medium, High, Critical. Status values accepted by the v1 API: Open, Triaged, In Progress, Testing, Resolved, Closed. Any valid transition is accepted. `resolved_at` is set when entering Resolved or Closed, retained across terminal states, and cleared when a ticket is reopened to a nonterminal status.

The dashboard's `resolved_tickets` count includes both Resolved and Closed states.

## Migration and legacy data

Revision `0002_multi_product_tickets` follows `0001_initial_tickets`. It adds catalog, membership, assignee, comment, and history tables; extends existing tickets; backfills ticket numbers, category/priority, and timestamps; normalizes known lowercase `open` and `closed` statuses; preserves unknown statuses; and seeds initial products/modules without overwriting existing matching rows. Legacy tickets retain IDs, titles, and descriptions and are not arbitrarily associated with a product, module, or customer. The live upgrade was checked: all four pre-existing ticket IDs (1, 10001, 10005, 10006) remain, their ID/title/description checksum is unchanged, and their statuses are now two `Open` and two `Closed`. One separately identified HTTP validation ticket, ID 10007 / `TEX-010007`, was created and intentionally retained during the live API smoke test. The SQLite importer also supplies required ticket number/category/priority fields for imported rows.

This revision's downgrade drops the added tables and columns and therefore can destroy Prompt 007 data. Never execute it on persistent data without explicit human approval. Do not reset the PostgreSQL database or delete its Docker volume.

## API contracts

New endpoints use `/api/v1`:

- Products: list/create, retrieve, and patch; modules list/create under a product and patch by module ID.
- Customers: list/create, retrieve, and patch. `PATCH /customers/{id}` can update profile fields and `product_ids` atomically; `PUT /customers/{id}/products` remains as a membership-only operation.
- Assignees: list/create/patch; inactive entries are omitted by default.
- Tickets: paginated/searchable/filterable list, create, detail, patch, comments, and history. Search covers ticket number, title, and description. Filters include product, status, and priority. Lists sort newest first and default to 25 per page, maximum 100.
- Dashboard: `GET /api/v1/dashboard/summary`, optionally filtered by product.

The original `GET/POST /tickets`, `PATCH /tickets/{id}`, and `POST /assistant` paths remain. The legacy ticket routes retain their original response shape. Legacy `POST /tickets` can still create an unassigned General/Medium ticket with only title and description; the v1 ticket endpoint requires product, category, and priority. The assistant receives only the submitted question and does not access ticket data.

## Identity, permissions, and AI boundaries

There is no login, actor identity, tenant isolation, or authorization middleware. Catalog and ticket APIs are open to any client that can reach FastAPI; local browser CORS is not authorization. The UI identifies itself as a local prototype. Do not expose it or use it for real customer records.

Future authorization proposal (not implemented or tested): Super Admin has global access; Product Admin, Support Engineer, and Developer are scoped to assigned products; Customer User is restricted to their own customer and associated products. Enforcement must be server-side on every list/detail/create/update/comment path before production. Future AI recommendations must remain separate from verified ticket state and must not mutate tickets without an authorized human action. RAG and product-system integrations are not included in this milestone.

## Local configuration

- PostgreSQL database/user: `texol_support` / `texol_user`; host `127.0.0.1:5433`, container `5432`.
- FastAPI: port `8000` by default.
- Vite: port `5173`; optional `VITE_API_BASE_URL`, defaulting to `http://localhost:8000`.
- Optional backend assistant: `OPENAI_API_KEY`, `OPENAI_MODEL`.

Use [README.md](../README.md) for setup/API examples and [TESTING.md](TESTING.md) for observed validation evidence. The audited starter SQLite file was empty. The live PostgreSQL database retains four tickets from prior local validation plus Prompt 007's explicitly identified smoke ticket 10007; preserve all of them.
