---
name: self-challenge
description: "Adversarial self-review checklist that must run BEFORE any deliverable is declared done in the AGENTS.md workflow. Challenges the AI's own output: unverified assumptions, untested edge cases, alternatives not evaluated, traceability gaps, and risk introduced. Use before concluding, finalizing, or handing to the reviewer."
---

# Self-Challenge — Challenge Your Own Output Before Done

You are your own adversarial reviewer. Before declaring any deliverable complete (a BRC, models, code, tests, design, an answer), run this checklist against YOUR output. A conclusion that skips self-challenge is, by rule, not done.

## The challenge checklist

1. **Assumptions** — Which assumptions did I make that are not verified? (stack, scope, actor set, data shape, environment.) Which would invalidate my deliverable if wrong?
2. **Edge cases** — What happens on empty / error / loading / boundary / concurrent / malformed input? Did I handle them or silently ignore them?
3. **Alternatives** — What options did I reject, and why? Is my choice still justified, or did I stop at the first solution that worked?
4. **Traceability** — Does every piece map to a requirement (FR → use case → entity → scenario → test)? What is unconnected to a requirement?
5. **Verifiability** — Could a skeptical reviewer prove me wrong with evidence? Where is the evidence for each claim?
6. **Security** — Did I introduce auth, input-validation, data-exposure, or secrets risk? (Cross-check AGENTS.md security rules.)
7. **Consistency** — Does this contradict anything already in the project (status.md, earlier deliverables, conventions)?
8. **Cost of being wrong** — What is the most expensive thing to redo if I am wrong? Should I stop and confirm it before proceeding?

## Output format

Before declaring done, return the self-challenge block:

```
SELF-CHALLENGE:
- Hypothèses non vérifiées: <list or "none">
- Cas limites ignorés: <list or "none">
- Alternatives rejetées: <list or "none">
- Traçabilité manquante: <list or "none">
- Risque sécurité: <list or "none">
- Contradictions connues: <list or "none">
Verdict: READY | NOT READY
```

## Rules

- Honesty beats confidence: an empty "none" because you didn't look is a failed self-challenge.
- If any item exposes a real gap, FIX it now — do not forward it to the reviewer.
- The reviewer/architect/design-reviewer agents are separate from this: self-challenge is YOUR pre-check, they are the independent check.
- When the deliverable is a short conversational answer, run the checklist mentally and answer only if a gap is material — do not pad small answers with a full block.
