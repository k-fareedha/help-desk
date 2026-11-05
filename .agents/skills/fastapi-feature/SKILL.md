---
name: fastapi-feature
description: Implement or change Python FastAPI endpoints and backend behavior in this repository, including validation, SQLAlchemy persistence, and backend tests.
---

# FastAPI feature workflow

Use this skill for scoped FastAPI feature work. Keep the change within the requested backend scope.

1. Read `AGENTS.md`, `README.md`, and `docs/ARCHITECTURE.md`; inspect the affected routes, schemas, models, and tests.
2. Confirm the expected request/response contract and identify any database or migration impact before editing.
3. Implement validation and business behavior using the existing FastAPI and SQLAlchemy 2.x patterns. Keep sessions request-scoped and writes transactional.
4. Add focused tests for success, invalid input, errors, and rollback behavior where relevant.
5. Run `backend/.venv/bin/python -m pytest tests -q` from the repository root when dependencies are available. If a test needs PostgreSQL, load local `.env` and explain that dependency; do not expose its values.
6. Update relevant API and architecture documentation. Report changed files and exact validation results.

Do not modify frontend files unless explicitly authorized. Do not run destructive database operations or delete Docker volumes. Ask for human approval before destructive data/schema actions.
