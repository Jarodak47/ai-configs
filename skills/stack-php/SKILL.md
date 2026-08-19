---
name: stack-php
description: PHP code generation best practices for the AGENTS.md workflow — Laravel (modern) and CodeIgniter (legacy). Use when the project stack is PHP and Phase 03 code must be generated.
---

# Stack — PHP (Laravel / CodeIgniter)

Best practices applied when generating PHP code in Phase 03 Construction.

## Precondition

- Stack confirmed: Laravel (modern) OR CodeIgniter (legacy).
- Architecture confirmed (MVC for both).
- Requirements traceable to a use case in `docs/02-elaboration/`.

## Laravel (modern, best practices)

- MVC structure: `app/Http/Controllers`, `app/Models`, `app/Services` for business logic, `routes/` for web/api.
- Models: Eloquent, one model per entity from the entity model; migrations as the only schema path (never `schema:dump` sync).
- Controllers thin: validation in Form Requests, business logic in Services/Actions, Eloquent in repositories when complexity requires it.
- API: `routes/api.php` under `/api/v1/...`; resources/transformers for output; validation on every endpoint.
- Auth: Laravel Sanctum/Passport for API tokens; Gate/Policy for authorization — never assume a route is protected.
- Error handling: Laravel exceptions map to JSON responses without stack traces in production.
- Tests: PHPUnit (Laravel's default) — Feature tests for endpoints, Unit tests for services. One test file per source file. Every Gherkin scenario of the current use case covered.
- Secrets: env vars only (`env()`/config), `.env.example` committed, `.env` never.
- `done` = `php artisan test` passes && `pint`/`php-cs-fixer` clean.

## CodeIgniter (legacy, respect the existing)

- Respect the existing CodeIgniter structure and conventions — do not retrofit Laravel patterns into it.
- Apply the Legacy Projects Policy: never refactor working code to match modern conventions.
- Within the existing structure, still apply best approaches: business logic out of controllers into models/services, input validation (`validation` library), prepared queries / Query Builder (no raw string interpolation into SQL), CSRF on forms, `esc()` on output to prevent XSS.
- If the codebase is being migrated: propose a progressive, use-case-by-use-case path toward a modern structure — never a big-bang rewrite.

## Common PHP rules

- `camelCase` for methods/properties, `PascalCase` for classes, files per PSR-4.
- Type hints on every method where the PHP version allows; strict_types in new files.
- Never trust client data: validate all input, sanitize output (`esc()`/`e()`).
- Never log or expose secrets, tokens, or PII; log levels consistent (debug/info/warning/error).

## Validation checklist (used by reviewer)

- [ ] Framework structure matches the confirmed stack (Laravel vs CodeIgniter)
- [ ] Controllers thin; business logic in services/models (or existing pattern respected)
- [ ] Migrations used (Laravel); Query Builder/prepared queries in CodeIgniter
- [ ] Every endpoint validates input and returns typed/structured output
- [ ] Auth and authorization explicit per route
- [ ] No secrets in code; `.env.example` present
- [ ] No XSS/SQL injection vectors (esc()/prepared queries)
- [ ] One test file per source file; Gherkin scenarios covered
- [ ] Tests and lint pass (reviewer RUNS them)

## Do / Don't

- DO respect CodeIgniter legacy choices; apply best approaches within them.
- DO use Eloquent + migrations in Laravel.
- DON'T mix Laravel idioms into a CodeIgniter codebase.
- DON'T do big-bang rewrites of legacy code.
- DON'T generate a whole feature — one use case at a time.
