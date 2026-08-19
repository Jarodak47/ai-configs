---
name: stack-python
description: Python code generation best practices for the AGENTS.md workflow — Django, FastAPI, SQLAlchemy/SQLModel, pytest. Use when the project stack is Python and Phase 03 code must be generated for a use case.
---

# Stack — Python (Django / FastAPI)

Best practices applied when generating Python code in Phase 03 Construction. Two main frameworks: Django (full-stack, batteries-included, MVT) and FastAPI (async APIs, microservices, SQLModel).

## Precondition

- Stack confirmed: Django OR FastAPI (or plain Python scripts/automation).
- Architecture confirmed (Monolithic / Microservices / Clean / Hexagonal...).
- Requirements traceable to a use case in `docs/02-elaboration/`.

## Django (MVT)

- Structure: `manage.py` at root; apps per domain (`apps/<domain>/`), not per feature.
- Models: one model per entity from the entity model; fields named with `snake_case`; explicit `db_index` and `unique` where the ER model requires.
- Use Django migrations (`makemigrations` + `migrate`) as the only schema change path — never sync with raw SQL.
- Views: class-based views (or viewsets if DRF) mapped to the use case; business logic in services, not in views/viewsets.
- Forms/validation in `forms.py` or serializers (DRF); never trust client data.
- Tests: `pytest` with `pytest-django`, `tests/` mirroring the app structure, one test file per source file.

## FastAPI (+ SQLModel/SQLAlchemy)

- Structure: layered (`api/routes.py`, `core/`, `domain/`, `infra/`) adapted to the chosen architecture.
- Endpoints under `/api/v1/...`; versioned from day one.
- Use Pydantic (via FastAPI) for input validation on every endpoint; `response_model` for typed outputs.
- SQLModel models for the entity layer; `session` dependency for DB access; commit/rollback explicit.
- Async: `async def` endpoints with async drivers (asyncpg) when the stack requires it; never block the event loop.
- Tests: `pytest` + `httpx`/`TestClient` (ASGITransport) for API tests; isolated test DB per run.

## Common Python rules

- `snake_case` for variables, functions, columns; `PascalCase` for classes.
- Type hints everywhere; `dataclasses` for value objects.
- Docstrings only for non-obvious logic; no redundant comments.
- Errors: raise domain exceptions; a global exception handler maps them to HTTP responses without exposing stack traces.
- Secrets: environment variables only (`os.environ.get("SECRET")`), `.env.example` committed, `.env` never.
- Dependencies: explicit in `pyproject.toml` (or `requirements.txt`), pinned or range-pinned.

## Testing rules

- One test file per source file, mirrored under `tests/`.
- Unit tests for services/domain logic; integration tests for API + DB.
- Every Gherkin scenario of the current use case must have a passing test.
- `pytest` + coverage for the use case; "done" = `tests pass && lint clean` (ruff).

## Validation checklist (used by reviewer)

- [ ] Framework structure matches the confirmed stack/architecture
- [ ] Models/entities match the entity model; migrations used
- [ ] Every endpoint validates input and returns typed responses
- [ ] Business logic in services, not in views/routes
- [ ] No secrets in code; `.env.example` present
- [ ] Errors mapped to responses without stack traces
- [ ] One test file per source file; Gherkin scenarios covered
- [ ] Tests and lint pass (reviewer RUNS them)

## Do / Don't

- DO put business logic in services/domain, not in views or routes.
- DO use type hints and `snake_case` throughout.
- DON'T return raw exceptions or stack traces to the client.
- DON'T hardcode config or secrets; use env vars.
- DON'T generate a whole feature — one use case at a time.
