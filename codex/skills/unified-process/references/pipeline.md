# Resumable pipeline

## State machine

1. Inspect the repository and existing `docs/` evidence. Never overwrite accepted artifacts.
2. Initialize missing workflow files with `scripts/init_project.py` only after the project path is explicit.
3. Validate `docs/dependency-graph.json`; execute only nodes classified `runnable`.
4. For each node, produce one bounded deliverable, run its deterministic checks, then request the applicable independent gate.
5. Accept only a valid structured verdict. On PASS, mark the node `done`. On FAIL, record the cause and repair it, up to three attempts. On exhausted attempts, mark it `blocked`.
6. Reclassify the graph after every state change. Mark downstream nodes `skipped` only when their required dependency is blocked and no alternative path exists.
7. End when every node is `done`, `blocked`, or `skipped`. Report achieved phase, evidence, blockers, and remaining risk.

## Concurrency

Run nodes concurrently only when the graph proves they have no unfinished dependency relationship and they do not write overlapping files. Keep a single owner per artifact. Serialize integration, shared-schema, migration, and final-gate work.

## Agent roles

- Use the main agent as orchestrator and maker unless a bounded task benefits from delegation.
- Give reviewers raw artifacts, phase contract, checklist, and commands; do not give them the intended verdict.
- Use a fresh reviewer context for calibration. Do not reuse a maker's reasoning as evidence.
- Treat timeouts, permission failures, unavailable tools, and malformed verdicts as infrastructure errors—not PASS or FAIL.

## Mode interaction

- Rapide: do not start this pipeline.
- Standard: use the same states but collapse gates to the final relevant review unless risk requires more.
- Rigoureux: require every phase and major-deliverable gate plus explicit user validation between phases.

