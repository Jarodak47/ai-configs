# Independent gates

## Common verdict rules

- Review the artifact against its declared phase contract and acceptance criteria.
- Cite commands, files, lines, test results, screenshots, or other reproducible evidence.
- Return FAIL for any unmet required item; do not average away blocking defects.
- Limit repair loops to three attempts unless the user explicitly authorizes more.
- Keep security findings compatible with Codex Security's severity and evidence model.

## Functional reviewer

Check completeness, correctness, FR traceability, tests, documentation, and acceptance criteria.

## Architecture reviewer

Check dependency direction, domain boundaries, pattern consistency, SOLID where relevant, data/event contracts, and whether complexity is justified.

## Security reviewer

Use the applicable `codex-security:*` skills. Check trust boundaries, authentication, authorization/IDOR, injection, SSRF/CSRF, deserialization, secrets, dependencies, and error/data exposure. Never inspect `.env` contents.

## Design reviewer

Use the applicable design/Figma skills. Check semantic tokens, component variants/states, responsive constraints, interaction behavior, accessibility, exact copy, and handoff evidence.

## Self-challenge before completion

Answer explicitly:

1. Quelles hypothèses restent non vérifiées ?
2. Quels cas limites n'ont pas été testés ?
3. Quelles alternatives importantes n'ont pas été évaluées ?
4. Quels éléments manquent de traçabilité ?

