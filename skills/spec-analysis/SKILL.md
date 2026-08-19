---
name: spec-analysis
description: Analyze a cahier de charge (specification / PRD / requirements document) to understand it fully and structure it for the AGENTS.md workflow — extract objectives, actors, functional requirements, constraints, success criteria; detect ambiguities, contradictions, gaps, and implicit assumptions; produce traceable FRs for the BRC. Use when the user provides a cahier de charge, spec, PRD, or requirements document at project start.
---

# Spec Analysis — Understand the Cahier de Charge

Analyze the cahier de charge so the project deliverables are built from what is ACTUALLY written, not from what is assumed. The output feeds Phase 01 (BRC) with full traceability back to the source document.

## Precondition

- The cahier de charge is provided: a file path (`.md`, `.txt`, `.docx`, `.pdf`) or pasted text.
- For `.pdf`/`.docx`: extract the text first (e.g. `pdftotext`, `pandoc`) or ask the user to provide the text — never generate from an unread binary.

## Steps

1. **Read fully** — read the entire cahier de charge before structuring anything; do not skim or guess from a fragment.
2. **Normalize** — build a structured understanding:
   - **Contexte & objectifs** — what the system is for, measurable goals where possible.
   - **Acteurs** — every human/system actor with a one-line role (do not invent actors).
   - **Besoins fonctionnels** — extract and dedupe; re-express each as a single verifiable capability "Le système doit <verbe> ..." while preserving the source wording reference.
   - **Contraintes** — technical, legal, operational, and business constraints.
   - **Critères de succès / exigences non fonctionnelles** — verifiable criteria.
3. **Detect issues** (the value-add of this skill):
   - **Ambiguities** — statements open to multiple interpretations (flag the interpretations).
   - **Contradictions** — two requirements that conflict (surface both, propose a resolution, ask).
   - **Gaps** — requirements stated vaguely ("gérer les utilisateurs") without verifiable behavior.
   - **Implicit assumptions** — things the cahier de charge implies but never states (auth model, scaling, language, deployment). Flag as "à confirmer" — never invent silently.
4. **Produce the deliverable** `docs/01-inception/cahier-de-charge-analysis.md`:
   - Structured understanding (objectifs, acteurs, FR normalisées, contraintes, critères).
   - **Traceability table**: each source requirement → proposed FR reference.
   - **Issues list**: ambiguities, contradictions, gaps, implicit assumptions — each with a question to the user.
5. **Ask before BRC** — resolve the flagged issues with the user BEFORE generating the BRC. Unresolved items are recorded as open questions, not silently decided.
6. **Self-challenge** before declaring done: did I map every source requirement? Did I invent anything? Did I fully read the document?

## Traceability rule (the verifiable condition)

- Every requirement stated in the cahier de charge maps to at least one proposed FR.
- Every FR maps back to a source section/paragraph of the cahier de charge.
- A requirement with no FR, or a FR with no source, means the loop is NOT done.
- Implied requirements are marked `à confirmer` and never become FRs without user approval.

## Validation checklist (used by reviewer)

- [ ] Cahier de charge read fully (not a fragment)
- [ ] Every source requirement mapped to a FR (and vice versa)
- [ ] Ambiguities surfaced with interpretations, not silently resolved
- [ ] Contradictions surfaced with proposed resolution
- [ ] Implicit assumptions flagged as "à confirmer", not invented
- [ ] Actors complete, none invented
- [ ] Understanding written in the project's language
- [ ] Open questions recorded for user resolution before BRC

## Do / Don't

- DO trace every requirement to the source document.
- DO ask about ambiguities and contradictions.
- DON'T invent requirements, actors, or scope the cahier de charge does not state.
- DON'T generate the BRC from an unread binary or a skimmed fragment.
