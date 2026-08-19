---
name: stack-arch
description: Apply architectural patterns and design principles when generating code in the AGENTS.md workflow — Hexagonal, Clean, Layered, MVC/MVT, Microservices, Event-Driven, CQRS, DDD, SOLID, Design Patterns. Use when a project's architecture must be applied or chosen during Phase 03, or when an architectural decision needs to be flagged.
---

# Architecture — Applying Patterns to Code Generation

Translate the project's chosen architecture into concrete code structure, and flag any decision that needs developer review.

## Precondition

- Architecture confirmed for the project (ask if not: Monolithic, Microservices, Hexagonal, Clean, Layered, MVC, Event-Driven, CQRS...).
- The chosen architecture is recorded in the project docs before Phase 03.

## Choosing the architecture (if free)

Recommend based on project reality, not fashion. Record the choice with justification:
- **MVC / MVT** — small-to-medium web apps where the framework dictates it (Laravel, Django, Spring MVC).
- **Layered** — classic enterprise apps: presentation / business / data, strict dependency direction.
- **Hexagonal (ports & adapters)** — domain isolated from infrastructure; when the domain must be testable without I/O and frameworks should be swappable.
- **Clean** — dependency rule inward; heavy testability requirements; large teams/domains.
- **Microservices** — independently deployable teams/services with clear bounded contexts; ONLY when the monolith is provably the bottleneck — not by default.
- **Event-Driven / CQRS** — async flows, high-write systems, or when read/write models differ meaningfully.
- **DDD** — complex business domains: bounded contexts, ubiquitous language, aggregates. It is a domain-design tool, not a packaging scheme.

## Applying the pattern in code (Phase 03)

- Generate the structure that matches the recorded architecture for the current stack — and ONLY that structure:
  - Hexagonal/Clean: `application`/`domain`/`infrastructure` (adapters at the edge); controllers/persistence are adapters, never domain logic.
  - Layered: controllers → services → repositories; one-way dependency; no cross-layer shortcuts.
  - MVC/MVT: framework convention respected (controllers/views thin, models rich).
  - Microservices: service owns its data, its lifecycle, its own contract; shared contracts versioned (see `stack-js-ts` for module federation).
  - Event-Driven: events named in past tense, published at the end of the transaction, consumers handle idempotency and replay.
  - CQRS: separate write model and read model; write model enforces invariants, read model optimized for queries.
- Apply SOLID per class/component: single responsibility, dependency inversion via interfaces/ports, open/closed via extension.
- Design patterns: use GoF patterns only where they solve a real constraint — never pattern-farming.

## Flagging decisions

- Every architectural decision made during generation that is not dictated by the recorded architecture must be **flagged for developer review** in the feature's review checklist (inversion of control, event schema, aggregate boundaries, bounded context splits...).
- Do NOT silently change the project architecture.

## Validation checklist (used by reviewer)

- [ ] Code structure matches the recorded architecture for the project/stack
- [ ] Dependency direction respected (no cross-layer shortcuts, no infra in domain)
- [ ] SOLID applied; dependency inversion via interfaces/ports where architecture requires
- [ ] Design patterns used only where justified
- [ ] Architecture deviations flagged for developer review, not silent
- [ ] For microservices: data + lifecycle owned per service; contracts versioned
- [ ] For event-driven/CQRS: idempotency, replay, and read/write separation present

## Do / Don't

- DO apply the recorded architecture strictly; it was validated in Phase 02.
- DO flag deviations instead of improvising.
- DON'T invent a new architecture mid-generation.
- DON'T use patterns for their own sake.
- DON'T choose microservices because it "sounds scalable".
