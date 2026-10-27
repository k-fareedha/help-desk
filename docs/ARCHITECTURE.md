# Architecture and Workflow

```text
User → React frontend (:5173)
       ├─ GET /tickets ───────┐
       ├─ POST /tickets ──────┤ FastAPI (:8000) → SQLite
       └─ POST /assistant ────┘       └─ OpenAI API (optional)
```

## Components
- `frontend/src.tsx`: ticket form, ticket list, AI question form, response panel.
- `backend/main.py`: REST API, input schemas, database access, AI integration.
- `backend/requirements.txt`: Python dependencies.

## Ticket workflow
User submits title and description → FastAPI validates schema → parameterized SQLite INSERT → ticket returned → UI refreshes.

## AI workflow
User submits a question → backend checks configuration → calls model when key exists → returns answer. Starter does not retrieve documents or call tools.

## Next iteration
Add ticket categories, permissions, a knowledge ingestion pipeline, chunking, vector search, grounded answers, and evaluation datasets.
