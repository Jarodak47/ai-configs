---
name: stack-data
description: Database design and access best practices for the AGENTS.md workflow — PostgreSQL, MySQL, MongoDB, SQLite, Supabase, and Prisma/SQLAlchemy/SQLModel. Use when the project needs schema design, migrations, indexing, or data-layer code in Phase 02/03.
---

# Stack — Data (Databases & ORM)

Best practices for schema design, migrations, and data access. Choose the database from the entity model and project needs, never by habit.

## Precondition

- Entity model defined (`docs/02-elaboration/entity-model.md`).
- Database confirmed: PostgreSQL (primary), MySQL, MongoDB, SQLite (embedded), or Supabase (BaaS on Postgres).
- ORM confirmed: SQLAlchemy / SQLModel (Python) or Prisma (TS/JS).

## Choosing the database (if free)

- **PostgreSQL** — default for relational, transactional, JSONB needs. (Primary recommendation.)
- **MySQL** — existing infra / hosting constraints.
- **SQLite** — embedded, local-only, prototypes, tests.
- **MongoDB** — document/NoSQL fits a schema-flexible model; justify vs relational.
- **Supabase** — when BaaS (auth + storage + Postgres) matches scope and avoids self-hosting.
- Decision must be recorded in the project docs with justification.

## Schema design rules

- Model the entity model 1:1; normalize to the level the access patterns need (3NF by default, denormalize deliberately).
- Primary keys: `bigint`/UUID; prefer UUID for distributed/async, bigserial for simple cases.
- Foreign keys everywhere relationships exist; always define them.
- Constraints: `NOT NULL` where the domain requires, `CHECK` for invariants, `UNIQUE` for business-unique fields.
- Naming: `snake_case` tables/columns; table names plural where the team does; explicit singular/plural choice recorded once.
- Timestamps: `created_at` / `updated_at` on tables that need audit; define `updated_at` trigger behavior once (vs manual).
- Soft deletes, enums-as-types (Postgres enum vs `varchar` + CHECK): decide once and document.

## Indexing

- Index foreign keys used in joins and filters; composite indexes ordered by the query's filter/order usage.
- Partial indexes for filtered queries; `UNIQUE` indexes back unique constraints.
- Never index "just in case" — index for measured query patterns; avoid over-indexing write-heavy tables.
- `EXPLAIN ANALYZE` to validate that queries use the intended index.

## Migrations

- Migrations are the only schema-change path — never raw SQL sync in production.
- SQLAlchemy/SQLModel: Alembic. Prisma: `prisma migrate dev`/`deploy`. Supabase: `supabase db push` + migrations.
- Every migration is reviewable, reversible (down), and maps to the entity model change.
- Seed data goes in a dedicated, idempotent seed script — not in migrations.

## Access patterns & ORM

- Write queries through the ORM/repository layer of the app stack (see `stack-python` / `stack-js-ts`).
- Use transactions for multi-step writes; keep them short; never hold a transaction across user input or I/O.
- N+1: eager-load related data (joinedload/selectin / Prisma include) — never lazy-load in loops.
- Return only needed columns (projections) for hot paths.
- Raw SQL only when the ORM cannot express it; still parameterized — never string-interpolated.

## Validation checklist (used by reviewer)

- [ ] Schema matches the entity model 1:1
- [ ] FKs, constraints (NOT NULL/CHECK/UNIQUE) in place per domain
- [ ] Migrations are the only schema path; reversible; reviewed
- [ ] Indexes justified by query patterns (EXPLAIN ANALYZE), no index overkill
- [ ] Queries parameterized; no string-interpolated SQL
- [ ] Transactions short and at the service boundary; no N+1
- [ ] Naming consistent (snake_case), decision on timestamps/soft-deletes documented
- [ ] Database choice justified and recorded

## Do / Don't

- DO model the entity model exactly; add constraints the domain requires.
- DO use migrations and parameterized queries always.
- DON'T string-interpolate user input into SQL.
- DON'T index speculatively.
- DON'T hold long transactions or lazy-load in loops.
