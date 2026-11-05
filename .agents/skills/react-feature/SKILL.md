---
name: react-feature
description: Implement React and TypeScript UI features in this repository, including API integration, validation, loading/error states, and responsive behavior.
---

# React feature workflow

Use this skill for scoped frontend changes.

1. Read `AGENTS.md`, `README.md`, and relevant frontend components/styles. Check the API contract before wiring requests.
2. Define the visible states and expected interaction, including validation, loading, success, empty, and failure states where applicable.
3. Implement with the existing React, TypeScript, and Vite setup; keep components consistent with the current app.
4. Add or update frontend tests only if a test framework already exists or the task explicitly adds one. Do not install dependencies without authorization.
5. Run `npm run build` from `frontend/` when frontend code changes; report the actual result.
6. Update docs if behavior or API usage changes, and summarize the files changed.

Do not modify backend files unless explicitly authorized. Keep API keys and server credentials out of browser code.
