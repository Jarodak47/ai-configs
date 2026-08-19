# Phase contracts

## 01 — Inception

Produce `docs/01-inception/brc.md` with context, measurable objectives, actors, numbered `FR-XX` requirements, constraints, and success criteria. If a specification exists, first extract ambiguities, contradictions, gaps, and traceability. Advance only after business approval.

## 02 — Elaboration

Produce:

- `business-use-cases.md`
- `entity-model.md`
- `system-use-cases.md`
- `test-cases.md` in Gherkin

Map every `FR-XX` to at least one business use case, entity, system behavior, and Gherkin scenario. Advance only after model and traceability validation.

## 03 — Construction

Implement one use case or cohesive feature at a time. Produce its detailed system-use-case specification, code, unit/integration tests, review evidence, and incremental documentation. Apply the confirmed stack and architecture. Require functional review; add architecture and security gates when the change touches their risk surface.

## 04 — Transition

Produce an FR-traceable UAT plan, deployment checklist, rollback/monitoring evidence, stakeholder-feedback structure, and prioritized improvement backlog. Refer to environment variables by name only.

## Project records

Maintain:

- `docs/status.md` for attempts, verdicts, failure causes, fixes, and evidence.
- `docs/dependency-graph.json` when multiple deliverables or agents depend on one another.
- `docs/pipeline-report.md` for autonomous or full-pipeline runs.

