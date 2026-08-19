---
name: design-stitch
description: Generate mobile and web UI designs with Google Stitch (stitch.withgoogle.com), the AI text-to-UI / vibe-design tool based on Gemini. Use when the user mentions Stitch, vibe design, text-to-UI, UI generation, DESIGN.md, or when UI/UX mockups are needed before Phase 03 construction.
---

# Design — Google Stitch (AI UI Generation)

Generate high-quality mobile/web UI designs with Stitch and wire them into the project loop (Phase 02/03 boundary). Stitch turns text prompts, images, or existing design systems into editable UI on an infinite canvas, with export to static HTML and Figma, and an MCP server for agent workflows.

## When to use

- During Elaboration, when UI mockups are needed before coding a use case.
- When the user asks for a design system, UI variants, or "vibe design".
- When a Figma-importable or HTML-exportable UI is required fast.

## Precondition

- The use case / FR is defined (`docs/02-elaboration/`). Never design without a functional target.
- Confirm the target platform (web / mobile / both) and the device breakpoints.

## Stitch workflow

1. **Define the design system first** via `DESIGN.md` (Stitch's design-rules file):
   - Color palette: semantic tokens (`color.primary`, `color.background`...), not raw hexes in prompts.
   - Typography scale (display / heading / body / caption), spacing scale (4/8/12/16/24/32), radius, shadow, elevation.
   - Component inventory: buttons, inputs, cards, nav, modals.
   - This file drives consistency across every screen and is exportable/importable between tools and codebases.
2. **Prompt per screen** — structure prompts as: layout + components + content + style + constraints:

   ```
   Screen: <name> (web/mobile)
   Goal: <what the user does on this screen>
   Components: <ordered list, reuse design-system names>
   Content: <real copy, not lorem ipsum; from the BRC>
   State: <default / empty / error / loading — one prompt per state>
   Style: <tokens from DESIGN.md; avoid adjectives like "modern", be specific>
   Constraint: <breakpoints, max width, a11y contrast AA>
   ```

3. **Iterate on the canvas**: generate multiple variants in parallel (Agent Manager), compare, refine the best — do not settle for the first output.
4. **Validate states & flows**: generate the happy path AND the error/empty/loading states of each screen; a flow with one state only is incomplete.
5. **Export**: HTML (static frontend) or Figma (for further design work). Re-import the same `DESIGN.md` to keep the system consistent.

## Prompting best practices (Stitch)

- Be concrete, not aesthetic: "left-aligned card grid, 2 columns, 16px gap" beats "beautiful modern layout".
- Reuse the exact component names defined in `DESIGN.md` so Stitch returns consistent components.
- Provide real business content from the BRC — UI with placeholder text fails acceptance.
- Give reference images (existing screens, brand assets) when brand fidelity matters.
- For accessibility: request visible focus states, AA contrast, and semantic ordering in the prompt.

## Integration with the project loop

1. Read `docs/status.md` and the target use case from `docs/02-elaboration/`.
2. Produce `docs/02-elaboration/ui-ux/<use-case>-<screen>.md` or `.html` per screen, including the `DESIGN.md` used.
3. Map every screen to its FR and Gherkin scenario.
4. Spawn the `design-reviewer` subagent to verify: design-system consistency, FR ↔ screen traceability, all states covered, a11y, responsiveness.
5. Iterate until PASS (max 3 iterations), then record in `docs/status.md`.

## Validation checklist (used by design-reviewer)

- [ ] `DESIGN.md` present and consistent (tokens, not raw values)
- [ ] Every FR target has at least one screen
- [ ] All states covered: default, empty, error, loading
- [ ] Real content from the BRC, not lorem ipsum
- [ ] Components reuse the design system (no ad-hoc styling per screen)
- [ ] Responsive constraints respected (breakpoints, max width)
- [ ] Accessibility: AA contrast, visible focus, semantic order
- [ ] Export format usable in the project stack (HTML / Figma)

## Do / Don't

- DO define the design system before generating screens.
- DO design state-by-state, one screen at a time.
- DON'T use vague aesthetic words in prompts — specify structure and tokens.
- DON'T ship a first-pass generation without variant comparison and review.
- DON'T generate UI without a functional target (FR/use case).
