# Challenges and Fixes

Record verified errors, causes, and resolutions. The following entries describe actual events from the PostgreSQL migration session.

## 2026-10-27 — Alembic could not import the backend package

- **Symptom:** `ModuleNotFoundError: No module named 'backend'` when running Alembic from the repository root.
- **Root cause:** Alembic's `env.py` did not have the repository root on `sys.path`; the config path setting alone did not make the package import reliable in this invocation.
- **Fix:** Added the repository root, resolved relative to `backend/migrations/env.py`, to the import path before importing model metadata.
- **Verification:** `backend/.venv/bin/alembic -c backend/alembic.ini upgrade head` succeeded against the project PostgreSQL service.

## 2026-10-27 — Console pytest entry point omitted the package root

- **Symptom:** Running `backend/.venv/bin/pytest -q` failed test collection with `ModuleNotFoundError: No module named 'backend'`.
- **Root cause:** The console-script invocation did not include the repository root on the import path in this environment.
- **Fix:** Use the module invocation from the repository root: `backend/.venv/bin/python -m pytest ...`.
- **Verification:** The module invocation ran the full suite successfully.

## 2026-10-27 — In-process ASGI requests stalled on synchronous route dispatch

- **Symptom:** Starlette `TestClient` stalled during startup in this environment. A minimal FastAPI app reproduced a stall for a synchronous route; an async minimal route completed. An `httpx.ASGITransport` request to the synchronous endpoint also stalled.
- **Root cause:** Environment/runtime interaction in the installed Python 3.14, AnyIO, and Starlette stack; a definitive upstream root cause was not established.
- **Mitigation:** Unit tests call the synchronous endpoint functions directly using isolated SQLAlchemy sessions. Separately, a real Uvicorn process was exercised over local HTTP against PostgreSQL for create, list, update, and persistence checks.
- **Verification:** The earlier migration-session run had eight tests; it later grew to ten after adding two PostgreSQL connectivity/rollback checks and to eleven after adding the NULL-status importer regression. The final **11 passed** result is recorded in `TESTING.md`; live HTTP smoke checks also passed through Uvicorn on port 18080.

## 2026-10-27 — Backend default port was already occupied

- **Symptom:** Uvicorn could not bind to `127.0.0.1:8000` (`Errno 98: address already in use`).
- **Resolution:** Left the existing process untouched and ran the project backend on port 18080 for the smoke check.
- **Verification:** Uvicorn logged that it was running on `127.0.0.1:18080`, and HTTP ticket requests succeeded.

## 2026-10-27 — Initial dependency download could not resolve PyPI

- **Symptom:** The first sandboxed `pip install -r backend/requirements.txt` attempt failed DNS resolution for `pypi.org`.
- **Resolution:** Retried the explicitly requested dependency installation with network access; all required packages installed in `backend/.venv`.
- **Verification:** The dependency installation completed successfully and tests/migrations then ran.

No unresolved code-level runtime failure remains known from these events. Keep security and product-scope limitations in `SESSION_CONTEXT.md`; do not present them as resolved incidents.

## 2026-10-27 — Codex CLI custom-agent spawn did not complete

- **Symptom:** A read-only `codex exec` prompt asking for the project `architecture_reviewer` agent produced `failed to load model context ... no rollout found` and a wait event with no receiver thread IDs.
- **Root cause:** The installed CLI collaboration/runtime store did not provide a rollout for the spawned thread. A definitive underlying cause was not established.
- **Resolution:** TOML syntax and project config acceptance were checked separately. Three requested read-only review tasks did complete through the current session's collaboration agent tool, but those are not evidence that the project-local CLI profile executed.
- **Verification:** The profile spawn is recorded as unverified; do not count the CLI's parent-generated review text as subagent output.

## 2026-10-27 — Context-handoff CLI warning

- **Observed:** The read-only fresh Codex CLI review emitted `UnexpectedServerResponse("HTTP 504: error code: 504")` from an RMCP transport worker, then continued and returned the requested review.
- **Root cause:** Unknown; the output does not establish why the server returned 504.
- **Resolution:** None claimed. The handoff was corrected based on the review's stale path-count finding. Retry only if future skill calls fail; do not treat this warning as a resolved infrastructure issue.

## 2026-10-27 — Malformed SQLite row could fail during ticket import

- **Finding:** The Architecture Reviewer found that a legacy row with `status = NULL` passed source-column checks but violated PostgreSQL's non-null constraint.
- **Fix:** `backend/migrate_sqlite.py` now detects a NULL status and raises an error naming the ticket ID inside the destination transaction. Added a regression test that verifies no partial rows are imported.
- **Verification:** Final backend test run: **11 passed in 1.01s**; see `TESTING.md`.

## 2026-10-27 — Prompt 007 frontend path and UI test setup

- **Observed:** The first frontend build found an incorrect stylesheet import after the UI files were moved under `frontend/src/`. Initial UI tests also exposed a missing React import in the test JSX setup and ambiguous Testing Library queries/cleanup.
- **Fix:** Corrected the stylesheet path, imported React in the affected test module, and made test cleanup and queries explicit.
- **Verification:** The final frontend suite passed **11 tests across 3 files**; strict TypeScript checking and the Vite production build passed.

## 2026-10-27 — Customer profile and product memberships needed atomic updates

- **Finding:** Submitting customer profile edits and product membership as separate API operations could leave a partial update if the second request failed.
- **Fix:** `PATCH /api/v1/customers/{id}` now accepts both profile fields and `product_ids` and validates/replaces them in one transaction. The frontend submits one patch; the membership-only PUT route remains available.
- **Verification:** Backend tests confirm invalid/duplicate membership values roll back the profile change; frontend success/failure coverage passes. Final suite totals are in `TESTING.md`.

## 2026-10-27 — Starlette/httpx deprecation warning remains

- **Observed:** Final backend test runs each emitted one Starlette/httpx deprecation warning while all tests passed.
- **Root cause:** The warning indicates a deprecated interface in the installed dependency stack; no application test failure or definitive upstream source was established in this session.
- **Resolution:** No dependency change was made as part of this milestone. Reassess when updating the compatible FastAPI/Starlette/httpx versions.

## 2026-10-27 — Closing directly did not set the resolution timestamp

- **Finding:** QA tested an Open-to-Closed transition without first entering Resolved. The original implementation left `resolved_at` empty in this valid transition.
- **Fix:** Set `resolved_at` when entering either Resolved or Closed, retain it across terminal states, and clear it when a ticket reopens to a nonterminal state.
- **Verification:** Added an API regression test for direct close, dashboard resolved counts, and reopening. Final backend test results are recorded in `TESTING.md`.

## 2026-10-27 — Ticket detail save control was not wired

- **Finding:** Frontend interaction review found the ticket detail Save changes button did not call its existing update handler.
- **Fix:** Wired the button to save status, priority, and assignee; added editable title, description, and category fields using the same PATCH flow.
- **Verification:** Added UI interaction assertions for update payloads. Final frontend tests and production build passed; see `TESTING.md`.
