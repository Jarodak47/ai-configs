---
name: phase-transition
description: "Generate the Phase 04 Transition deliverables of the AGENTS.md methodology: UAT plan, production deployment checklist, stakeholder feedback report template, and improvement backlog. Use when the user asks for UAT, deployment, transition, feedback report, Phase 04, or release."
---

# Phase 04 — Transition

Use this skill when the construction phase is complete (all use cases reviewed and passed) and the product is ready to reach users.

## Precondition

- Phase 03 completed: all use cases implemented, tests passing, lint clean.

## Deliverables

Written under `docs/04-transition/`:

1. `uat-plan.md` — User Acceptance Testing plan: scope, actors, entry/exit criteria, UAT scenarios mapped to FRs.
2. `deployment-checklist.md` — Production deployment checklist (env vars, migrations, backups, rollback, monitoring, secrets handling).
3. `feedback-report-template.md` — Structured stakeholder feedback report template.
4. `improvement-backlog.md` — Optimization and improvement backlog with priorities.

## Rules

- Every UAT scenario must map to an FR and a success criterion from the BRC.
- The deployment checklist must reference environment variables by name only — never values.
- The feedback report template must separate: what works / what fails / improvement ideas / priority.
- The improvement backlog must be prioritized (P0/P1/P2) and traceable to feedback sources.

## Validation checklist (used by the reviewer agent)

- [ ] UAT plan has scope, actors, entry/exit criteria
- [ ] Every UAT scenario maps to an FR and a success criterion
- [ ] Deployment checklist covers env, migrations, backups, rollback, monitoring
- [ ] No secret values anywhere in the deliverables — placeholders only
- [ ] Feedback report template structured (works / fails / ideas / priority)
- [ ] Improvement backlog prioritized and traceable to feedback
- [ ] Loop log (`docs/status.md`) shows all prior phases passed

## Loop behavior

When invoked as part of a goal loop:
1. Read `docs/status.md` and confirm Phase 03 is complete.
2. Generate the four files above.
3. Run the `self-challenge` skill against the deliverables (assumptions, edge cases, traceability, security).
4. Spawn a reviewer subagent to run the validation checklist against the files.
5. If FAIL, fix and re-verify. Iterate until PASS (max 3 iterations).
6. Write the result to `docs/status.md` (`done: transition` / `next: release`).
7. Suggest a branch name and a Conventional Commit message (`docs(transition): ...`).
