---
name: test-validation
description: Validate a feature or fix against acceptance criteria using the repository's existing backend, PostgreSQL, migration, and frontend checks.
---

# Test validation workflow

Use this skill when asked to test, verify, or review implementation evidence.

1. Read the acceptance criteria and relevant test/docs setup; identify which checks apply.
2. Run the backend suite from the repository root with `backend/.venv/bin/python -m pytest tests -q` when the project venv is available.
3. For configured PostgreSQL checks, load `.env` without printing it; verify Compose health, connectivity, migration state, and relevant data/API behavior only when safe.
4. Run `npm run build` from `frontend/` for frontend changes.
5. Report each check as passed, failed, skipped, or not run, with the exact command and reason. Identify coverage gaps separately from failures.

Do not modify implementation files during a review-only validation. Never drop databases or volumes, reset records, or claim results that were not observed.
