---
name: stack-infra
description: Infrastructure and tooling best practices for the AGENTS.md workflow — Docker, Docker Compose, Redis, and Postman for local dev and API testing. Use when the project needs containerization, local environments, caching, or API documentation/tests.
---

# Stack — Infra (Docker / Compose / Redis / Postman)

Best practices for containerized local dev environments, Redis usage, and API testing.

## Precondition

- Project stack and services known (app, db, cache, queue...).
- Local dev environment is the target (Docker Compose) unless a prod deployment is being designed.

## Docker

- Base images: pin major/minor (`python:3.12-slim`, `node:22-alpine`), prefer slim/distroless; never `latest`.
- Multi-stage builds for compiled apps (build in one stage, copy artifacts to a slim runtime stage).
- Non-root user in the image; read-only filesystem where feasible.
- `.dockerignore` mirrors `.gitignore` (node_modules, build, dist, .env, logs).
- One process per container; healthchecks (`HEALTHCHECK`) for services that others depend on.
- Never bake secrets into images — env vars at runtime only.

## Docker Compose (local dev)

- Compose = the single documented way to run the project locally (`docker compose up`).
- Services: app, db (Postgres/MySQL), cache (Redis), plus the tooling the project needs.
- Volumes for persistent data (db, redis) — data must survive restarts.
- Named profiles for optional services (e.g. `--profile extra`).
- DB/Redis credentials via `.env` + `.env.example` placeholders; no hardcoded values in compose files.
- Depends_on with healthcheck conditions, not just ordering.

## Redis

- Use cases: cache, queues/jobs, sessions, rate limiting, pub/sub — pick consciously.
- Keys: namespaced (`<app>:<domain>:<id>`), TTL on everything cache-like; keyspace must not grow unbounded.
- Cache strategy: cache-aside with explicit invalidation; version keys on schema/format change.
- Connections via the app stack's client with pooling; never a new connection per request.
- Persistence: RDB/AOF only if the data must survive restart — else treat Redis as ephemeral and document that assumption.

## Postman

- Collections organized per domain/feature; each request documents example request AND response.
- Environment variables for base URL, tokens (named, never values in shared collections).
- Tests embedded (status codes, schema, time) so the collection is a runnable API test suite.
- Export collections to the repo (`postman/` folder) so they're versioned with the API; keep the OpenAPI spec as the source of truth, Postman as the runnable layer.

## Validation checklist (used by reviewer)

- [ ] Images pinned, slim/base justified, no `latest`
- [ ] Multi-stage where compiled; non-root user; healthchecks present
- [ ] `.dockerignore` present; no secrets in images or compose files
- [ ] Compose is the documented local-dev path; volumes for persistent data
- [ ] Redis keys namespaced with TTL; connection pooling; cache invalidation defined
- [ ] Postman collections versioned in repo with examples and tests
- [ ] `.env.example` present with placeholders only

## Do / Don't

- DO make `docker compose up` the single onboarding command.
- DO set TTL and namespaces on every Redis key.
- DON'T bake secrets into images or compose files.
- DON'T use `latest` tags or unpinned images.
- DON'T generate a whole infra setup — one service/use case at a time.
