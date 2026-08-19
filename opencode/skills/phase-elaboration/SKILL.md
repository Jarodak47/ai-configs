---
name: phase-elaboration
description: "Generate the Phase 02 Elaboration deliverables of the AGENTS.md methodology: Business Use Case Diagrams (Mermaid), Entity-Relationship models, System Use Case Diagrams, and Gherkin test cases. Use when the user asks for use cases, entity model, Gherkin tests, elaboration, or Phase 02."
---

# Phase 02 — Elaboration

Use this skill after a BRC exists (`docs/01-inception/brc.md`) and when the user requests use cases, entity models, or test cases.

## Precondition

The BRC must exist and be approved. If not, return to Phase 01 first.

## Deliverables

Written under `docs/02-elaboration/`:

1. `business-use-cases.md` — Business Use Case Diagrams in Mermaid.
2. `entity-model.md` — Entity-Relationship model in Mermaid `erDiagram`.
3. `system-use-cases.md` — System Use Case Diagrams in Mermaid with business validation notes.
4. `test-cases.md` — Test cases in Gherkin (Given / When / Then).

## Traceability rule (the verifiable condition)

Every functional requirement `FR-XX` from the BRC must map to:
- at least one business use case
- at least one entity involved
- at least one Gherkin scenario

Produce a **traceability matrix** at the end of `test-cases.md`:

| FR | Use case | Entity | Gherkin scenario |
|----|----------|--------|------------------|

A missing row means the loop is NOT done.

## Gherkin format

```gherkin
Fonctionnalité: <FR label>
  Afin de <bénéfice>
  En tant que <acteur>
  Je veux <capacité>

  Scénario: <name>
    Étant donné <context>
    Quand <action>
    Alors <résultat attendu>
```

- One `Fonctionnalité` block per FR.
- Cover the happy path plus at least one error/edge scenario per FR.
- **Contraintes négatives du BRC** : chaque contrainte négative de la section
  « Hors périmètre » est soit couverte par un scénario Gherkin explicite (un
  scénario qui vérifie que le système NE fait PAS X), soit documentée comme
  hors périmètre dans `system-use-cases.md` avec une raison. Une absence
  silencieuse est un FAIL.

## Validation checklist (used by the reviewer agent)

- [ ] `docs/02-elaboration/` contains the four files: `business-use-cases.md`, `entity-model.md`, `system-use-cases.md`, `test-cases.md`
- [ ] Business use case diagrams (Mermaid) cover all actors from the BRC
- [ ] Entity-relationship model exists (`erDiagram`) and covers the entities involved by the use cases
- [ ] System use cases exist with business validation notes
- [ ] Gherkin test cases: one `Fonctionnalité` block per FR, happy path + at least one error/edge scenario per FR
- [ ] Negative BRC constraints covered by a Gherkin scenario or explicitly documented as out-of-scope with a reason
- [ ] Traceability matrix complete: every `FR-XX` maps to ≥1 use case, ≥1 entity, ≥1 Gherkin scenario — no missing rows

## Loop behavior

When invoked as part of a goal loop:
1. Read `docs/status.md` and the approved BRC.
2. Generate the four files above.
3. Verify the traceability matrix: every FR has use case + entity + scenario.
4. Run the `self-challenge` skill against the deliverables (assumptions, edge cases, alternatives, traceability, security).
5. Spawn a reviewer subagent to check coverage and quality.
6. If gaps exist, fix and re-verify. Iterate until the matrix is complete.
7. Write the result to `docs/status.md`.
