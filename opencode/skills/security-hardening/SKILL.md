---
name: security-hardening
description: Security attack checklist and remediation patterns for the AGENTS.md workflow — OWASP-informed review and fixes (injection, authN/authZ, IDOR, SSRF, CSRF, secrets, deserialization, dependencies). Use when hardening generated code, fixing findings from the security-reviewer, or when any code touching auth, input, or data is generated.
---

# Security Hardening — Attack Checklist & Fix Patterns

Used by the maker to fix findings reported by the `security-reviewer` agent, and as the attack checklist the reviewer runs. Every generated feature must be hardened before it is declared done.

## Attack checklist (what the security-reviewer attempts)

1. **Secrets**: hardcoded keys/tokens/passwords in code, config, or logs; secrets in repo history; `.env` referenced instead of env vars. **Preuve déterministe** : le scan `security_scan.py` (voir skill `security-scan`) détecte les secrets commits et les `.env` traqués — le reviewer s'appuie sur son rapport, pas seulement sur l'œil.
2. **Injection**:
   - SQL/NoSQL: is any query built by string interpolation of user input?
   - XSS: is any user input rendered without encoding? (React escapes by default — check `dangerouslySetInnerHTML`, Angular `innerHTML`, raw template strings, `eval`.)
   - Command injection: shell strings or `child_process`/`os.system`/`subprocess` built from input.
3. **AuthN/AuthZ**: protected routes missing authentication; IDOR (object owned by user A accessed by user B); role checks missing; token/session validation weak.
4. **Input validation**: every entry point validates type, length, range, and allow-list values; no path traversal (`../`); no mass assignment (unexpected fields accepted).
5. **SSRF**: user-supplied URLs fetched server-side without allow-list/deny of internal hosts.
6. **CSRF**: state-changing requests protected (tokens) when cookie-based auth is used.
7. **Deserialization**: no unsafe deserialization of untrusted data (`pickle`, `yaml.load`, `JSON.parse` on untrusted with dangerous types).
8. **Error handling**: generic messages in production, no stack traces/schema leaks, no sensitive data in logs.
9. **Dependencies**: audit clean or known-risk dependencies flagged. **Preuve déterministe** : exécute `python3 ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/tools/security-scan/security_scan.py` (pip-audit/npm audit/composer audit) et cite son rapport comme evidence.

## Fix patterns (per class)

- **Secrets** → env vars only, `.env.example` placeholders, secrets manager for prod; `gitleaks` in CI.
- **SQL injection** → parameterized queries / ORM (Prisma, SQLAlchemy, Eloquent); NEVER string-interpolated SQL.
- **XSS** → framework-default escaping; sanitize before `innerHTML`/`dangerouslySetInnerHTML`; CSP header.
- **Command injection** → no shell strings from input; use argument-array APIs (`execFile`, `execve` arg arrays), allow-list commands.
- **IDOR** → ownership check on every object access (the actor owns/has access to the resource), not just auth.
- **Auth** → explicit, per-route; centralized guard/middleware; role checks on the resource, not the route.
- **SSRF** → validate protocol, allow-list hosts, block private/loopback/link-local ranges.
- **CSRF** → tokens on state-changing requests; SameSite=Strict cookies.
- **Deserialization** → type-safe parsing only; never pickle/yaml.load untrusted data.
- **Error handling** → generic responses in prod; structured logging without PII; never log tokens/passwords.
- **Dependencies** → pin versions; run audit tools in CI; update policy documented.

## Rules

- Security applies to EVERY feature, not just "security features". Auth, input, and data paths are always security-critical.
- Never generate code that logs or exposes secrets, tokens, or PII.
- Every fix must be **prouvé**, pas affirmé : re-exécute le scan déterministe (`security_scan.py`) et re-lance le `security-reviewer` sur le code corrigé. L'evidence (rapport de scan + verdict reviewer) est citée dans le log d'itérations.
- Si un fix est impossible dans le périmètre, le flag comme **bloqué** dans `docs/status.md` — ne pas l'accepter en silence.

## Validation checklist (used by security-reviewer)

- [ ] No secrets in code/config/logs; `.env.example` present
- [ ] All queries parameterized; no injection vectors
- [ ] Output encoded; no unsafe innerHTML
- [ ] Auth explicit on protected routes; ownership checks (no IDOR)
- [ ] Input validated at every entry point; no path traversal/mass assignment
- [ ] No SSRF/CSRF/deserialization vectors
- [ ] Errors generic in prod; no info leak
- [ ] Dependency audit clean (or flagged)
