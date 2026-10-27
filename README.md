# HelpDesk AI — Wednesday AI Development Lab

A learning-focused full-stack support ticket application with an optional OpenAI-powered assistant. This is an original starter implementation inspired by helpdesk products, not a copy of proprietary source code.

## Features
- Create and list tickets using a SQLite database.
- Ask questions using the OpenAI Responses API when configured.
- Responsive React frontend.
- AI-off mode with a clear configuration message.

## Stack
React 18, TypeScript, Vite, FastAPI, SQLite, OpenAI Python SDK.

## Setup
Prerequisites: Python 3.10+ and Node.js 20+.

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp ../.env.example .env # Optional reference; export environment variables to your shell
export OPENAI_API_KEY='your-key' # Optional. Never commit a real key.
uvicorn main:app --reload
```
Open http://localhost:8000/docs to inspect the API.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## API
- `GET /tickets`: list tickets
- `POST /tickets`: `{ "title": "Login issue", "description": "Password reset fails" }`
- `POST /assistant`: `{ "question": "How do I troubleshoot login issues?" }`

## Architecture
Browser React UI → FastAPI REST endpoints → SQLite for tickets; optional OpenAI Responses API for assistant. No ticket content is sent to the model automatically in the starter.

## Weekly learning roadmap
1. Add AI ticket classification and suggested replies.
2. Add PDF knowledge base and RAG with citations.
3. Add safe agent tools and explicit approval for writes.
4. Expose read-only tools via an MCP server.
5. Add chat history, summaries, context compaction, and token metrics.
6. Add evaluation, tests, CI, and model comparison.

## Security
Use `.env` or exported variables for secrets, never commit keys, add authentication and per-user authorization before production, and validate AI outputs before making changes. CORS is limited to local Vite development.

## Documentation
See `docs/ARCHITECTURE.md`, `docs/WEEKLY_LOG.md`, `docs/TESTING.md`, `docs/CONTEXT_MANAGEMENT.md`, `prompts/PROMPT_HISTORY.md`, `AGENTS.md`, and `CLAUDE.md`.

## Status
Starter code is supplied for learning; run setup and tests in your environment before presenting it as validated.
