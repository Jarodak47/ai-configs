---
name: phase-inception
description: Generate the Phase 01 Inception deliverables of the AGENTS.md methodology, primarily the Business Requirements Catalog (BRC). Use when the user asks for a BRC, business requirements, inception phase, or a new project kickoff.
---

# Phase 01 — Inception: Business Requirements Catalog

Use this skill when starting a new project or when the user requests a BRC.

## Precondition

- If a cahier de charge / spec / PRD / requirements document exists, load the `spec-analysis` skill FIRST: analyze the cahier de charge, resolve ambiguities with the user, and produce `docs/01-inception/cahier-de-charge-analysis.md` with full traceability before writing the BRC.
- The BRC must trace back to the cahier de charge (or to the user's stated requirements) — no invented scope.

## Deliverable

One file: `docs/01-inception/brc.md`

## BRC Structure

The BRC must contain exactly these sections:

1. **Titre et contexte** — one-line goal, background, date.
2. **Objectifs** — bullet list of business objectives, measurable where possible.
3. **Acteurs** — every actor (human or system) with a one-line role description.
4. **Exigences Fonctionnelles (FR)** — numbered `FR-01`, `FR-02`, ... Each FR is a single verifiable capability written as "Le système doit <verbe> ...".
5. **Contraintes** — technical, legal, and operational constraints.
6. **Critères de succès** — verifiable success criteria mapped to objectives.
7. **Hors périmètre / Contraintes négatives** — what the system explicitly will NOT do (negative requirements), giving the reviewer a boundary to catch scope creep.

## Rules

- FRs must be atomic: one capability per FR, no "et" combining behaviors.
- FRs are numbered and stable — never renumber after review; append instead.
- Write in the project's language (ask if ambiguous, default French).
- Do not invent actors: ask the user when the actor set is unclear.
- State the negative constraints explicitly — behaviors the system must NOT have — so the loop can refuse scope creep with evidence.

## Validation checklist (used by the reviewer agent)

- [ ] Objectives present and measurable
- [ ] All actors identified with role descriptions
- [ ] FRs numbered, atomic, verifiable
- [ ] Each objective covered by at least one FR (traceability)
- [ ] Constraints section present
- [ ] Success criteria present and verifiable
- [ ] Negative constraints present (what the system must NOT do)
- [ ] No invented scope beyond what the user stated

## Loop behavior

When invoked as part of a goal loop:
1. Read `docs/status.md` (if present) for context and resume point.
2. Generate the BRC in `docs/01-inception/brc.md`.
3. Run the `self-challenge` skill against the BRC (assumptions, edge cases, alternatives, traceability, security).
4. Spawn a reviewer subagent to run the validation checklist against the file.
5. If the checklist has failures, fix them and re-verify.
6. Write the result to `docs/status.md` under `done` / `next`.
