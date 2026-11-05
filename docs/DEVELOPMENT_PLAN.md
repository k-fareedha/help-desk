# Incremental Development Plan

This roadmap separates current implementation from work that remains proposed. Check `docs/TESTING.md` and `docs/SESSION_CONTEXT.md` before treating a milestone as complete.

## Completed foundation

### PostgreSQL starter — 2026-10-27

- PostgreSQL 17 Docker Compose service, local-only port mapping, health check, persistent volume.
- SQLAlchemy session handling and Alembic initial `tickets` schema.
- Repeatable read-only SQLite importer and ticket update endpoint.
- Migration and API test coverage. See `TESTING.md` for exact evidence.

## Prompt 007 — Multi-product ticket management

**Implementation status:** complete on 2026-10-27. Alembic `0002_multi_product_tickets` is at head in the local PostgreSQL database, existing ticket IDs and text were verified, and backend/frontend tests plus the production build passed. Exact evidence and remaining test limits are in `TESTING.md`.

- Products/modules, customers with product memberships, and a local demo assignee directory.
- Product-aware ticket creation, legacy route compatibility, searching/filtering/pagination, comments/history, and dashboard summary.
- React prototype views for dashboard, tickets, products/modules, customers, and assignees.
- Existing ticket rows remain unassigned; there is no authentication/authorization. The application is a local prototype and is not production-ready.

## Remaining milestones

1. **Choose identity and enforce authorization:** select identity provider and user model; finalize permissions for the proposed product-scoped internal roles and enforce customer isolation on every route. The matrix in `ARCHITECTURE.md` remains a proposal, not an implemented policy.
2. **Complete operational workflows:** confirm notifications, retention, backups, assignment policy, and deployment requirements.
3. **Configure production readiness:** establish least-privilege DB roles, secrets management, observability, deployment and recovery procedures; current frontend API-base configuration is available but still environment-specific.
4. **Add bounded AI assistance:** consider classification/priority recommendations and troubleshooting drafts only after ticket-data handling rules are approved. Keep outputs separate from verified ticket state and require human action before mutation.
5. **Add retrieval and integrations:** define approved knowledge sources, access controls, citations, and product-system integration contracts before adding RAG, GitHub, or MCP tools.
6. **Maintain quality automation:** broaden integration/evaluation coverage and add CI once deployment and test environments are selected. Browser end-to-end coverage is not present in Prompt 007.

## Delivery rules

Keep changes small and independently reviewable. Never reset PostgreSQL or delete its volume. For every milestone, update tests and relevant docs, run documented checks, and record observed outcomes in `TESTING.md`, `WEEKLY_LOG.md`, and `prompts/PROMPT_HISTORY.md` as appropriate. Do not mark work complete based solely on files existing or a configured agent/skill.
