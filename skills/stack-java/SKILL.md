---
name: stack-java
description: Java/Kotlin code generation best practices for the AGENTS.md workflow — Spring Boot layered backends. Use when the project stack is Java or Kotlin with Spring Boot and Phase 03 code must be generated.
---

# Stack — Java/Kotlin (Spring Boot)

Best practices applied when generating Java/Kotlin Spring Boot code in Phase 03 Construction.

## Precondition

- Stack confirmed: Java or Kotlin + Spring Boot; build tool Maven or Gradle.
- Architecture confirmed (Layered / Hexagonal / Clean).
- Requirements traceable to a use case in `docs/02-elaboration/`.

## Structure (layered)

- Package by layer or by feature depending on the chosen architecture:
  - Layered: `controller` → `service` → `repository` + `dto`/`model`.
  - Hexagonal/Clean: `application` (ports, use cases) / `domain` (entities, value objects) / `infrastructure` (adapters, controllers, persistence).
- One controller per aggregate/domain; thin controllers — business logic in services/use cases.
- `@RestController` + DTOs in/out; never expose entities directly as API responses.

## Domain & persistence

- JPA entities for the relational model; map to the entity model from `docs/02-elaboration/`.
- Flyway (or Liquibase) migrations as the only schema change path — never `ddl-auto=update` in production.
- Repositories: Spring Data interfaces for simple queries; explicit `@Query` (or criteria) for complex ones; return DTOs/projections when the full entity is not needed.
- Transactions: `@Transactional` at the service boundary, never at the controller; keep transactions short.

## API rules

- Versioned endpoints `/api/v1/...`.
- Input validation: bean validation (`@Valid` + Jakarta annotations) on request DTOs; never trust client data.
- Errors: a `@ControllerAdvice` maps domain exceptions to problem responses (RFC 9457) with generic messages — no stack traces to the client.
- Pagination: Spring Data `Pageable`, never unbounded lists.

## Kotlin specifics

- Data classes for DTOs and value objects; null-safety via types (`?`), avoid `Optional`/null patterns.
- `spring-kotlin` idioms (constructor injection via `@Autowired` on primary constructor) where the codebase follows them.

## Security (non-negotiable)

- Spring Security enabled by default on every endpoint; authorization explicit per endpoint — never assume a route is public.
- Passwords: bcrypt/Argon2 only. Secrets via env vars or a vault, never in code/config files. `.env.example` for local dev only.
- Validate and sanitize all inputs; be explicit about CORS origins in production.

## Testing rules

- JUnit 5 + Mockito; MockMvc for controller tests, `@DataJpaTest`/Testcontainers for repository tests.
- One test file per source file, mirrored under `src/test/java`.
- Every Gherkin scenario of the current use case has a passing test.
- `done` = `mvn test` (or `./gradlew test`) passes && lint (Checkstyle/Spotless) clean.

## Validation checklist (used by reviewer)

- [ ] Package structure matches the confirmed architecture (no logic in controllers)
- [ ] Entities map to the entity model; migrations (Flyway) used
- [ ] Every endpoint validates input, returns DTOs, versioned `/api/v1`
- [ ] Domain exceptions mapped to problem responses, no stack traces
- [ ] Spring Security explicit per endpoint; no default/implied auth
- [ ] No secrets in code or config; env vars only
- [ ] One test file per source file; Gherkin scenarios covered
- [ ] Tests and lint pass (reviewer RUNS them)

## Do / Don't

- DO keep controllers thin; business logic in services/use cases.
- DO return DTOs, never entities, from the API.
- DO make security explicit on every route.
- DON'T use `ddl-auto=update` in production — Flyway only.
- DON'T return raw exceptions or stack traces to the client.
- DON'T generate a whole feature — one use case at a time.
