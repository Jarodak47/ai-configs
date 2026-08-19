---
name: prompt-optimizer
description: Compress and optimize prompts to reduce token usage with LOSSLESS fidelity — every fact, requirement, number, and term is preserved, nothing is invented, meaning never shifts. Use when the user asks to optimize/shorten/compress a prompt, or when a prompt is verbose before being sent.
---

# Prompt Optimizer — Lossless Compression

Rewrite a prompt to consume fewer tokens while preserving 100% of its meaning. This is lossless compression: nothing is removed except wasted tokens, and nothing is added.

## The non-negotiable contract

1. **No invention** — never add a requirement, constraint, example, or specificity that is not in the original. If the original is vague, keep it vague.
2. **No meaning shift** — the optimized prompt must be interpretable in exactly the same way as the original by a reader with the same context.
3. **No information loss** — every fact, number, name, term, path, and constraint survives verbatim or with equivalent phrasing.
4. **When in doubt, keep the longer version** — brevity that introduces ambiguity is a failed optimization.

## What to remove (safe to cut)

- Fillers and hedges: "please", "I'd like you to", "it would be great if", "basically", "just", "kind of".
- Politeness framing that carries no instruction ("thanks in advance", "if you don't mind").
- Redundancy: restating the same requirement twice, rephrasing what the context already establishes.
- Self-evident context already available to the model (AGENTS.md, system prompt, current file/scope) — reference it instead of restating it.
- Elaborations that add no constraint ("a clean and professional design that looks good").

## What to preserve (never touch)

- All facts, numbers, dates, percentages, budgets, versions, thresholds.
- All proper nouns, technical terms, identifiers, file paths, function names, URLs.
- All constraints and negative constraints ("do not X" must survive).
- All stated requirements — however oddly phrased.
- The tone of the instruction when tone is itself a requirement (formal vs casual output).

## How to compress (techniques)

1. Read the full prompt; identify every discrete fact/requirement/constraint (this is the fact list).
2. Rewrite with: imperative verbs, active voice, direct statements, compact clause structure.
   - "If it is possible for you to provide a solution that will..." → "Provide a solution that..."
   - "You need to make sure that the code we write does not include any kind of secrets" → "Write code with no secrets."
3. Merge parallel sentences into one clause when the meaning is identical.
4. Drop articles, hedges, and repetition; keep technical words intact (never abbreviate a term).
5. Keep the original structure (intro / steps / constraints) if the prompt has one — do not merge sections that are logically separate.

## Process

1. Run `self-challenge` on your own rewrite: map each original fact to its optimized counterpart.
2. Output the optimized prompt.
3. Report the token delta (before → after) and list ONLY what was removed (structural categories, not every word).

## Verification checklist (must all pass)

- [ ] Every original fact present in the optimized prompt
- [ ] Nothing added — no invented requirement, constraint, or example
- [ ] No meaning shift on any statement
- [ ] Identifiers, numbers, terms, and paths verbatim
- [ ] All constraints (including "do not") survive
- [ ] Nothing removed that a reader could not reconstruct from context

## Do / Don't

- DO optimize for tokens while keeping meaning identical.
- DON'T "clarify" by adding specificity the user did not give.
- DON'T remove an ambiguity — flag it and ask, or leave it as-is.
- DON'T compress at the cost of readability when the prompt is short anyway (diminishing returns).
