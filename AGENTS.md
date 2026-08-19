# AI Development Methodology — Unified Process AI

## Overview

This file defines the global methodology to follow for ALL development projects.
It applies to every AI tool: Claude, Claude Code, Cursor, Codex, Windsurf, Copilot, etc.

The development cycle is: **Requirements → AI Generation → Business Review → Repeat**

---

## Working Style

- Work in **pair programming mode**: propose code step by step, explain each decision.
- Apply validation checkpoints according to the selected Execution Mode.
- In Standard Mode, implement the approved scope completely and request validation only for structural decisions.
- In Rigorous Mode, validate each phase and major deliverable before advancing.
- If something is ambiguous, ask before generating.

---

## Execution Modes

Trois niveaux d'exécution régissent toute interaction, de la question ponctuelle au projet complet. Le niveau définit le formalisme attendu : plan, checkpoints, livrables, validations.

### Mode Rapide

Explications, diagnostics, petites corrections.
- Pas de plan formel.
- Vérification immédiate.
- Pas de checkpoint sauf risque.

### Mode Standard (défaut)

- Plan compact.
- Implémentation complète dans le périmètre approuvé.
- Tests et auto-évaluation.
- **Validation aux décisions structurantes uniquement** : une fois le périmètre approuvé, implémenter sans checkpoint intermédiaire ; ne solliciter de validation qu'en cas de décision structurante (architecture, contrat, portée).

### Mode Rigoureux

Processus Unified Process AI complet.
- Quatre phases, livrables et validations obligatoires.
- Adapté aux nouveaux produits, fonctionnalités complexes, systèmes sensibles et changements architecturaux.
- **Validation de chaque phase et de chaque livrable majeur avant d'avancer** — aucun livrable suivant n'est engagé tant que le précédent n'est pas validé.

### Règle de sélection

Si aucun mode n'est indiqué, choisir automatiquement le niveau **proportionnel à la complexité, au risque et à la réversibilité** :

| Situation | Mode |
|---|---|
| Nouveau projet, décision structurante, système sensible, changement d'architecture | **Rigoureux** |
| Tâche locale à faible risque, réversible (diagnostic, correction ciblée, explication) | **Rapide** |
| Tout le reste | **Standard** |

L'utilisateur peut imposer un autre mode à tout moment. Les règles du projet (AGENTS.md local) peuvent compléter ou remplacer les préférences globales.

---

## Stacks in Use

The following stacks are used across projects. Adapt code generation accordingly:

- **Python** — scripts, APIs, data processing, automation
  - **Django** — full-stack web framework
  - **FastAPI** — async APIs, microservices
- **JavaScript / TypeScript** — general frontend and backend
  - **React** — component-based SPA
  - **Next.js** — SSR / SSG / fullstack React
  - **Angular** — enterprise frontend
  - **Microfrontends** — frontend composed of independently deployed apps
  - **Module Federation** — Webpack/Rspack plugin for sharing code between microfrontend apps
- **Java / Kotlin** — backend services, Android
  - **Spring Boot** — backend services
- **PHP (Laravel, CodeIgniter)** — web backend; CodeIgniter legacy
- **C** — low-level / embedded / systems

### Databases & ORM
- **PostgreSQL** — primary relational database
- **MySQL** — relational database
- **MongoDB** — NoSQL document database
- **SQLite** — lightweight embedded database
- **Supabase** — BaaS / backend-as-a-service (Postgres + auth + storage)
- **SQLAlchemy** — ORM (Python)
- **SQLModel** — ORM (Python, FastAPI-native, built on SQLAlchemy + Pydantic)
- **Prisma** — ORM (Node.js/TypeScript)

### Infrastructure & Tooling
- **Redis** — cache, queues, in-memory data store
- **Docker** — containerization
- **Docker Compose** — multi-container orchestration and local dev environments
- **Postman** — API testing and documentation

### Media
- **Remotion** — programmatic video generation in React
- **DaVinci Resolve** — video editing and color grading

### State Management
- **Observables** — reactive state change handling. JS: RxJS (BehaviorSubject for current state, subscriptions for change notifications). R: Shiny reactive values / `observeEvent` for state changes.
- **Redux** — predictable state container for JS apps (single store, actions, reducers). Use with React/React-Redux or Redux Toolkit.
- **RTK Query** — data fetching and caching layer built on Redux Toolkit (auto caching, invalidation, loading/error states).

### Architecture & Design
- **Microservices** — independently deployable services, each with its own data and lifecycle
- **Architecture hexagonale** — ports & adapters, domain isolated from infrastructure
- **MVC** — Model-View-Controller (Spring Boot, ASP.NET, Laravel)
- **MVT** — Model-View-Template (Django)
- **Clean Architecture** — dependency rule, layers isolated inward
- **Layered Architecture** — presentation / business / data layers
- **Event-Driven** — asynchronous communication via events/messages
- **CQRS** — separate read and write models
- **Modularité** — code organized in independent, cohesive, loosely coupled modules
- **POO** — Object-Oriented Programming (encapsulation, inheritance, polymorphism)
- **DDD** — Domain-Driven Design (bounded contexts, ubiquitous language, aggregates)
- **SOLID** — single responsibility, open/closed, Liskov, interface segregation, dependency inversion
- **Clean Code** — readable, maintainable, self-documenting code (naming, small functions, no duplication)
- **TDD** — test-driven development: red → green → refactor
- **BDD** — behavior-driven development: given/when/then scenarios (Gherkin), business-readable acceptance tests
- **Design Patterns** — standard reusable solutions (GoF, etc.)

When the project stack is not specified, ask before generating code.

---

## Methodology — 4 Phases

### Default behavior
Always start a new project in **Phase 01 — Inception** unless explicitly told otherwise.

---

### Phase 01 — Inception

**Goal**: Define the project scope and align all stakeholders before any code is written.

**Deliverables to generate:**
- Business Requirements Catalog (BRC)
- Stakeholder list and alignment notes
- Test strategy overview
- Quick iteration plan with feedback loops

**Prompt pattern:**
> "Generate a Business Requirements Catalog for this project. Include: objectives, actors, functional requirements, constraints, and success criteria."

**Validation checkpoint:** BRC must be reviewed and approved before moving to Phase 02.

---

### Phase 02 — Elaboration

**Goal**: Model the system before building it.

**Deliverables to generate:**
- Business Use Case Diagrams (text or Mermaid format)
- Entity-Relationship Models
- System Use Case Diagrams with business validation
- Test cases in Gherkin format (Given / When / Then)

**Prompt pattern:**
> "Based on the provided BRC, generate the use case diagrams, entity model, and test cases in Gherkin format."

**Validation checkpoint:** Models and test cases must be validated before moving to Phase 03.

---

### Phase 03 — Construction

**Goal**: Generate and review the application code iteratively.

**Deliverables to generate:**
- Detailed System Use Case Specifications
- Application code (adapted to the project stack)
- Unit tests and integration tests
- Developer review checklist per feature

**Prompt pattern:**
> "Generate the [stack] code for use case [X] based on the provided specs. Include unit tests and a developer review checklist."

**Rules:**
- Generate one use case or feature at a time.
- Always include tests alongside the code.
- Flag any architectural decision that needs developer review.

**Validation checkpoint:** Each feature must pass review before the next one is generated.

---

### Phase 04 — Transition

**Goal**: Deliver to users and continuously improve.

**Deliverables to generate:**
- User Acceptance Testing (UAT) plan
- Production deployment checklist
- Stakeholder feedback report template
- Optimization and improvement backlog

**Prompt pattern:**
> "Generate a UAT plan, a production deployment checklist, and a structured stakeholder feedback report for this project."

---

## Phase Transition Rules

Ces règles s'appliquent en **Mode Rigoureux** (processus complet) : dans les Modes Standard et Rapide, le rythme et la portée des validations sont définis par les modes d'exécution ci-dessus.

- Never skip a phase.
- Always produce and validate the deliverables of the current phase before advancing.
- If a review reveals issues, return to the appropriate phase — do not patch forward.
- The cycle (Requirements → AI Generation → Business Review → Repeat) applies within each phase.

---

## General Rules for All Phases

- **Always ask for the current phase** if it is not mentioned and context is unclear.
- **Stack decisions** — the stack is never assumed and never locked:
  - **Stack not fixed**: propose the best choice for the project (framework, architecture, tooling) with justification and alternatives, then validate before generating.
  - **Stack already chosen / legacy**: respect the existing choice, but always apply the best practices of that stack — "it's legacy" is not a license for mediocre code.
- **Code quality**: follow clean code principles, add comments for non-obvious logic.
- **Security**: flag any security concern immediately (auth, input validation, data exposure).
- **Incremental delivery**: structure work in reviewable increments. In Standard Mode, validate only structural decisions; in Rigorous Mode, validate each major increment before advancing.
- **Self-challenge before done**: before declaring any deliverable complete, challenge your own output — declare unverified assumptions, untested edge cases, alternatives not evaluated, and missing traceability. A conclusion without a self-challenge is not done.
- Prefer generating **one artifact at a time** (one diagram, one model, one feature).

### Self-challenge — checklist

Before declaring any deliverable complete, answer these four questions explicitly:

1. **Quelles hypothèses restent non vérifiées ?**
2. **Quels cas limites n'ont pas été testés ?**
3. **Quelles alternatives importantes n'ont pas été évaluées ?**
4. **Quels éléments manquent de traçabilité ?**

Une conclusion sans ces quatre réponses n'est pas un livrable terminé.

---

## Naming Conventions

Apply the correct convention based on context — never mix styles within the same scope.

| Context | Convention | Example |
|---|---|---|
| Variables, functions | camelCase | `getUserData`, `isLoading` |
| Classes, components, interfaces | PascalCase | `UserService`, `LoginForm` |
| Files, folders, CSS classes | kebab-case | `user-profile.ts`, `btn-primary` |
| Python variables, functions, DB columns | snake_case | `get_user_data`, `created_at` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private class members | `_camelCase` | `_internalState` |

**Rules:**
- Names must be explicit and self-documenting — no abbreviations unless universally known (`id`, `url`, `api`).
- Booleans always start with `is`, `has`, `can`, `should` — e.g. `isAuthenticated`, `hasPermission`.
- Functions must express an action — start with a verb: `get`, `set`, `fetch`, `create`, `update`, `delete`, `handle`, `on`.
- Never use generic names: `data`, `info`, `temp`, `obj`, `foo`.

---

## Commit Convention — Conventional Commits

Every commit message must follow this format:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

**Types:**

| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructure, no feature/fix |
| `test` | Add or update tests |
| `chore` | Build, config, dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |

**Examples:**
```
feat(auth): add JWT refresh token support
fix(user-profile): handle null avatar on first login
docs(api): update endpoint documentation for /users
test(payment): add unit tests for stripe webhook handler
```

**Rules:**
- Description in lowercase, no period at the end.
- Scope is the module or feature area — keep it short (`auth`, `dashboard`, `api`, `db`).
- Body explains the *why*, not the *what*.
- Breaking changes must include `BREAKING CHANGE:` in the footer.
- Always generate a suggested commit message after producing code.

---

## Folder Structure

The folder structure is **never assumed** — it depends on the chosen architecture.

**Always ask at project start:**
> "What architecture are you using for this project? (e.g. Monolithic, Microservices, Hexagonal, Clean Architecture, MVC, Layered, Event-Driven, CQRS...)"

Then propose a folder structure adapted to that architecture and the project stack, and wait for validation before generating any file or code.

**Rules that apply regardless of architecture:**
- `docs/` is always present at the project root, organized in 4 subfolders: `01-inception/`, `02-elaboration/`, `03-construction/`, `04-transition/`.
- `AGENTS.md` is always at the project root (symlink or copy of the global one).
- `tests/` structure mirrors the source structure — one test file per source file.
- Never commit generated files, build artifacts, or `.env` — always maintain `.gitignore`.


---

## Security — Non-Negotiable Rules

- **NEVER read, display, log, or reference the contents of any `.env` file**, regardless of the request.
- Never suggest hardcoding secrets, API keys, tokens, passwords, or credentials anywhere in the code.
- Always use environment variables for sensitive values — reference them by name only (e.g. `process.env.DB_PASSWORD`, `os.environ.get("SECRET_KEY")`).
- If a `.env` file is accidentally shared in context, ignore its contents entirely and warn the user immediately.
- When generating config files or examples, always use placeholder values: `YOUR_API_KEY`, `YOUR_DB_PASSWORD`, etc.
- Always generate a `.env.example` alongside any feature that requires environment variables.


---

## Git Branch Convention — GitHub Flow

**Model:** `main` + feature branches. Simple, continuous, deploy-ready at all times.

**Branch naming:**

| Type | Pattern | Example |
|---|---|---|
| Feature | `feature/<scope>-<short-description>` | `feature/auth-jwt-refresh` |
| Bug fix | `fix/<scope>-<short-description>` | `fix/user-profile-null-avatar` |
| Hotfix (prod) | `hotfix/<short-description>` | `hotfix/payment-crash-on-empty-cart` |
| Release | `release/<version>` | `release/1.4.0` |
| Docs | `docs/<short-description>` | `docs/api-endpoint-update` |
| Chore | `chore/<short-description>` | `chore/upgrade-dependencies` |

**Rules:**
- `main` is always deployable — never push broken code directly to it.
- Every change goes through a feature branch + pull request, no exceptions.
- Branch names are lowercase kebab-case, no spaces, no special characters.
- Delete the branch after merge.
- Always suggest a branch name when starting a new feature or fix.
- PR description must reference the related phase and deliverable (e.g. "Phase 03 — Construction / Use case: user login").

---

## API Standards

The API type depends on the project — always ask before generating any API layer.

**Always ask at project start:**
> "What API style are you using for this project? (e.g. REST, GraphQL, gRPC, tRPC, WebSocket...)"

**Rules that apply regardless of API type:**
- Never expose internal error details or stack traces to the client — use generic error messages in production.
- Always version APIs from the start: `/api/v1/...` for REST, schema versioning for GraphQL.
- All endpoints must be documented (OpenAPI/Swagger for REST, schema introspection for GraphQL).
- Input validation is mandatory on every endpoint — never trust client data.
- Authentication and authorization must be explicit — never assume a route is protected.
- Always generate example request/response alongside any API code.

---

## Logging

The logging format depends on the project and environment — always ask before generating any logging setup.

**Always ask at project start:**
> "What logging format do you want for this project? (e.g. structured JSON, plain text, or both depending on environment)"

**Rules that apply regardless of format:**
- Never log sensitive data: passwords, tokens, API keys, personal user data (PII).
- Always use log levels consistently: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`.
- Errors must always include: timestamp, log level, context (module/function), and a clear message.
- Production logs must never expose stack traces to end users.
- Always suggest a logging library appropriate to the stack (e.g. `winston` for Node.js, `loguru` for Python, `slf4j` for Java).


---

## Setup & Deployment
> Claude, Claude Code, and Codex read `AGENTS.md` automatically — no extra config needed.

---

### Project Initialization:
Per project — run once per new project.
At the start of every new project, automatically generate the following setup script and ask the developer to run it:

```bash
#!/bin/bash
# Run this at the root of your project

mkdir -p docs/01-inception \
         docs/02-elaboration \
         docs/03-construction \
         docs/04-transition

# .gitignore : idempotent — n'ajoute que les entrées manquantes, sans doublon
touch .gitignore
while IFS= read -r entry; do
  grep -qxF -- "$entry" .gitignore || echo "$entry" >> .gitignore
done << 'GITIGNORE'
.env
*.env
build/
dist/
__pycache__/
node_modules/
*.log
.loop-trace/
GITIGNORE

# AGENTS.md : ne jamais écraser un fichier ou lien déjà présent
AGENTS_SRC="$HOME/AGENTS.md"
if [ -e ./AGENTS.md ] || [ -L ./AGENTS.md ]; then
  if [ -L ./AGENTS.md ] && [ "$(readlink ./AGENTS.md)" = "$AGENTS_SRC" ]; then
    echo "ℹ️ AGENTS.md déjà lié vers $AGENTS_SRC."
  else
    echo "⚠️ AGENTS.md existe déjà — non touché."
  fi
else
  ln -s "$AGENTS_SRC" ./AGENTS.md
fi

echo "✅ Project structure initialized."
```

Do not proceed with any code generation until the developer confirms the script has been run.

---

## Plan Mode — According to Execution Level

The plan-first rule applies according to the **Execution Modes** above: a formal plan is required in **Mode Standard** and **Mode Rigoureux**, not in **Mode Rapide**.

### The plan-first rule
Before any generation in Mode Standard or Rigoureux, present a structured plan:

1. **What** you are going to generate (list of artifacts, files, or actions)
2. **In what order** (step by step)
3. **Assumptions** made (stack, architecture, scope)
4. **Questions** if anything is ambiguous

Then wait for explicit approval before proceeding.

**Accepted approval signals:** "go", "ok", "proceed", "yes", "continue", "do it" — or any clear confirmation.

If no approval is given, do not generate anything.

### Example plan format
```
## Plan — [Feature or task name]

Phase: 03 Construction
Stack: Next.js / TypeScript

Steps:
1. Generate the UserService with login and logout methods
2. Generate unit tests for UserService
3. Generate the LoginForm component
4. Suggest a commit message and branch name

Assumptions:
- JWT-based authentication
- Supabase as the database

Questions:
- Should the session be stored in cookies or localStorage?

Waiting for your approval to proceed.
```

### Exceptions
No plan required for (Mode Rapide):
- Simple factual questions or explanations
- Fixing a typo or a single-line bug when explicitly asked
- Generating a commit message or branch name suggestion only

---

## Legacy Projects Policy

For existing projects that predate this methodology, **never apply changes retroactively**.

**Rule: "Don't touch what works, apply to what's new."**

### Minimal adoption (for any active legacy project)
Run this once at the project root to plug in the methodology without touching existing code:

```bash
# Idempotent : ne crée le lien que si rien n'existe déjà (fichier ou lien)
AGENTS_SRC="$HOME/AGENTS.md"
if [ -e ./AGENTS.md ] || [ -L ./AGENTS.md ]; then
  echo "ℹ️ AGENTS.md déjà présent — non touché."
else
  ln -s "$AGENTS_SRC" ./AGENTS.md
fi
mkdir -p docs/01-inception \
         docs/02-elaboration \
         docs/03-construction \
         docs/04-transition
```

From that point, the AI follows this methodology for all new work on the project.

### Progressive adoption (for projects under active development)
Apply conventions only to the parts you actively work on:
- New code → follow naming conventions
- New commits → follow Conventional Commits format
- New branches → follow GitHub Flow
- New features → document in the appropriate `docs/` phase folder

### What to never do on legacy projects
- Do not rename existing files, variables, or functions in bulk — it breaks the codebase.
- Do not rewrite Git history — dangerous in a team context.
- Do not retroactively apply Phase 01 Inception to a project already in construction.
- Do not refactor working code just to match conventions — wait for a natural touch point.

### Phase to start from on a legacy project
When starting a session on a legacy project, identify the current state and start from the matching phase:
- No specs or docs exist yet → start from Phase 02 Elaboration (document what exists)
- Specs exist, code is in progress → start from Phase 03 Construction
- Code is done, not yet in production → start from Phase 04 Transition
- Already in production → stay in Phase 04, focus on feedback and improvement

---

## Quick Reference

| Phase | Key Output | Moves to next when |
|---|---|---|
| 01 Inception | BRC + stakeholder alignment | BRC approved |
| 02 Elaboration | Use cases + entity model + test cases | Models validated |
| 03 Construction | Code + tests + review checklist | Feature reviewed |
| 04 Transition | UAT + deployment + feedback | Released + feedback collected |
