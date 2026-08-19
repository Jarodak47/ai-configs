---
name: stack-js-ts
description: TypeScript/JavaScript code generation best practices for the AGENTS.md workflow — React, Next.js, Angular, state management (RxJS, Redux, RTK Query), Microfrontends, Module Federation. Use when the project stack is JS/TS and Phase 03 code must be generated.
---

# Stack — JS/TS (React / Next.js / Angular / Microfrontends)

Best practices applied when generating TypeScript/JavaScript code in Phase 03 Construction.

## Precondition

- Stack confirmed: React (SPA), Next.js (SSR/SSG), Angular, or Microfrontends (Module Federation).
- Architecture confirmed; state strategy agreed (RxJS / Redux / RTK Query).
- Requirements traceable to a use case in `docs/02-elaboration/`.

## React (SPA)

- Function components + hooks only; no class components unless legacy.
- One component per file; `PascalCase` for components, `camelCase` for functions/variables, `kebab-case` for files.
- Props typed with interfaces; define a single source of truth for data shapes (from the entity model).
- Server/API calls in dedicated hooks (`useGetUser`) or RTK Query — never inline `fetch` scattered across components.
- State: local (`useState`/`useReducer`) for UI state; global (Redux/RTK Query) for cross-cutting data; derived data via memoization.
- Tests: Vitest + React Testing Library; one test file per component; test behavior, not implementation.

## Next.js (SSR/SSG)

- App Router as default; server components for data fetching where possible, client components only when interactivity requires it.
- Route handlers / Server Actions for mutations with input validation (zod).
- `"use client"` only when needed — default to server components to minimize client JS.
- Data fetching: cache and revalidate explicitly; never fetch in useEffect when a server approach exists.
- Typed APIs end to end (zod schemas shared between server and client) — no `any` crossing the wire.

## Angular

- Feature modules or standalone components; one component/service per feature.
- Services injectable and scoped (providedIn); HTTP via typed services, not inline `HttpClient` in components.
- State via RxJS (BehaviorSubject for current state, subscriptions with async pipe; `takeUntilDestroyed` to unsubscribe). Signals where the codebase already uses them.
- `snake_case` for files, `camelCase` for properties, `PascalCase` for classes/components.
- Tests: Jasmine/Karma or Vitest — unit tests for services and components; test the observable outputs, not implementation.

## Microfrontends & Module Federation

- Each microfrontend is an independently deployable app with its own data and lifecycle; shared code ONLY via shared modules, never copy-paste.
- Module Federation: share only stable, versioned packages (UI kit, core); define `exposes`/`remotes` explicitly; keep shared runtime singleton.
- Contracts between apps defined in a shared types package, versioned.
- Routing: one host shell + remote apps; document the navigation contract.
- Never couple microfrontends to each other's internals — only to the shared contract.

## State Management

- **RxJS (Observables)**: BehaviorSubject for current state; subscriptions in components via async pipe or explicit unsubscribe; keep state logic in services.
- **Redux**: single store, actions/reducers, selectors; Redux Toolkit (createSlice, createAsyncThunk) — no hand-written boilerplate.
- **RTK Query**: endpoints for server state with auto caching/invalidation; tags (`providesTags`/`invalidatesTags`) instead of manual refetch.

## Testing rules

- One test file per source file, mirrored under `tests/` (or `*.test.tsx` alongside).
- Component tests assert behavior (roles, rendered output), not internals.
- Every Gherkin scenario of the current use case has a passing test.
- `done` = `tests pass && lint clean` (eslint) && typecheck (tsc).

## Validation checklist (used by reviewer)

- [ ] Framework structure matches the confirmed stack/architecture
- [ ] Components typed (no `any` crossing boundaries); props typed
- [ ] State strategy respected (local / Redux / RTK Query / RxJS per contract)
- [ ] Data fetching centralized (hooks / services / RTK Query), not scattered
- [ ] Microfrontends respect shared contracts; no internal coupling
- [ ] No secrets in code; env vars via `NEXT_PUBLIC_`/`import.meta.env` only for non-secrets
- [ ] One test file per source file; Gherkin scenarios covered
- [ ] Tests, lint, and typecheck pass (reviewer RUNS them)

## Do / Don't

- DO type everything that crosses a boundary (props, API, store).
- DO put data fetching in hooks/services/RTK Query, not in component bodies.
- DON'T mix state strategies in the same feature.
- DON'T copy code between microfrontends — share only via modules.
- DON'T generate a whole feature — one use case at a time.
