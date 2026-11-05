---
name: database-migration
description: Design, create, review, and validate PostgreSQL schema changes and Alembic migrations for this repository.
---

# PostgreSQL migration workflow

Use this skill for schema changes, data migrations, or migration review.

1. Read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/DEVELOPMENT_WORKFLOW.md`; inspect SQLAlchemy models, migration history, and relevant data paths.
2. State the schema and compatibility impact. Keep migration scope limited to requirements; do not add speculative product tables.
3. Create a versioned Alembic migration and review upgrade and downgrade behavior. Treat downgrade/drop/reset operations as destructive and obtain human approval before running them.
4. Preserve existing rows and IDs. For data transfer, define repeat behavior, conflict handling, transaction boundaries, value/count verification, and sequence handling.
5. Add migration validation tests where feasible. Run the backend suite and, when configured, validate against the project PostgreSQL service.
6. Never delete Docker volumes, databases, backups, or source data. Document exact commands, outcomes, and remaining limits.
