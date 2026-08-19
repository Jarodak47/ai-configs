---
name: unified-process
description: "Apply Jarod's Unified Process AI to software work: select Rapide, Standard, or Rigoureux mode; run Inception, Elaboration, Construction, and Transition; enforce traceability, independent review gates, structured verdicts, dependency gates, and workflow metrics. Use for new projects, complex features, architecture changes, phase deliverables, autonomous pipelines, business reviews, workflow calibration, or when the user mentions Unified Process, BRC, phase 01-04, gates, pipeline, self-challenge, or migration from the OpenCode workflow."
---

# Unified Process AI

Apply the smallest amount of process proportional to complexity, risk, and reversibility. Treat `/Users/jarodak47/AGENTS.md` as the canonical policy; read it completely when this skill triggers.

## Select the execution mode

- Use **Rapide** for explanations, diagnostics, and small reversible corrections. Skip the formal plan; verify immediately.
- Use **Standard** by default. Present a compact plan, implement the approved scope, test it, and pause only for structural decisions.
- Use **Rigoureux** for new products, sensitive systems, complex features, and architecture changes. Execute the four phases and require approval at each phase or major deliverable.
- Obey an explicit user-selected mode.

## Route the work

1. Identify whether the project is new or legacy and determine its current phase from evidence. Never retroactively force Phase 01 onto working legacy code.
2. For Standard or Rigoureux work, state the artifacts, order, assumptions, and blocking questions before implementation.
3. In Rigoureux mode, read [phase-contracts.md](references/phase-contracts.md) and [gates.md](references/gates.md). Do not advance while a required predecessor is unapproved or failed.
4. Delegate domain work to installed skills instead of reproducing their guidance:
   - security: `codex-security:*`
   - frontend/React: `build-web-apps:*`
   - architecture/testing/review/docs: `engineering:*`
   - design/Figma: `design:*`, `product-design:*`, `figma:*`
   - Remotion: `remotion:*`
   - database/Supabase: `supabase:*` and data skills
5. Keep maker and checker roles independent. A checker must review raw artifacts and evidence, not the maker's conclusions.
6. Record each gate result in `docs/status.md`. For machine consumption, emit the contract in [verdict.schema.json](references/verdict.schema.json) between `VERDICT_JSON_BEGIN` and `VERDICT_JSON_END`.
7. Before completion, answer the four self-challenge questions in [gates.md](references/gates.md), run relevant tests, and distinguish verified facts from remaining uncertainty.

## Deterministic controls

- Validate a verdict: `python3 scripts/validate_verdict.py --file <verdict-file>`.
- Validate/classify a dependency graph: `python3 scripts/dependency_gate.py --file docs/dependency-graph.json`.
- Initialize a project idempotently: `python3 scripts/init_project.py --project-dir <path>`.
- Compute loop metrics: `python3 scripts/loop_metrics.py --project-dir <path>`.
- Score reviewer calibration results: `python3 scripts/calibrate.py --results <results.json>`.
- After modifying this skill, run `python3 scripts/integration_test.py`.
- Keep deterministic tool output as evidence. Do not replace failed tools with an unlabelled LLM guess.

For a complete or autonomous run, read [pipeline.md](references/pipeline.md). For reviewer evaluation or prompt changes, read [calibration.md](references/calibration.md). Apply [reasoning-policy.md](references/reasoning-policy.md) when choosing effort for makers and reviewers.

## Boundaries

- Never read, display, log, or quote any `.env` contents. Refer to variable names only.
- Do not let Superpowers silently replace the Unified Process phase model. Use its debugging, TDD, planning, and verification skills only when compatible with the selected mode.
- Do not duplicate installed domain skills inside this skill.
- Do not declare PASS without evidence or while a required checklist item is false.
