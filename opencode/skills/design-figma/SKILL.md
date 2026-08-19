---
name: design-figma
description: Create and maintain Figma design systems, components, variants, auto layout, and responsive constraints, and hand off design tokens to code (CSS/JSON) in the AI workflow. Use when the user mentions Figma, maquette, design system, tokens, components, variants, auto layout, handoff, or when UI deliverables must be translated into the project stack.
---

# Design — Figma (Design System & Handoff)

Produce maintainable Figma work and translate it into code-ready artifacts (tokens, components, layouts) that feed Phase 03 Construction. The goal is a single source of truth: what the designer sees and what the developer codes must come from the same tokens and structures.

## When to use

- Building a new design system (tokens, components, patterns).
- Structuring screens/flow for a use case before code.
- Handoff: converting Figma structure into CSS/JSON tokens and component specs.

## Precondition

- The use case / FR is defined. Design system decisions must be traceable to the BRC (brand, users, success criteria).
- Confirm the target stack (CSS variables, Tailwind, styled-components, React Native...) — tokens export format depends on it.

## Figma structure rules

1. **Tokens are the source of truth** — build them as Figma variables (not raw hex/number styles):
   - Color: semantic variables (`color/primary`, `color/background`, `color/text-muted`), never brand hexes scattered in layers.
   - Typography: type scale with role names (display / heading-1... / body / caption), linked to a text style.
   - Spacing: 4px base scale (4/8/12/16/24/32/48/64). Radius, border width, shadow/elevation, motion duration.
   - Export these as CSS custom properties and JSON so the code and the design cannot drift.
2. **Components over one-off frames** — every repeated UI element is a component:
   - Buttons, inputs, cards, nav, badges, modals, empty states.
   - Use **variants** for states (default/hover/disabled/loading/error) and sizes — not duplicate components.
   - Name components with the design-system vocabulary so devs and the AI reuse the same names (`Button/Primary`, `Input/Text`).
3. **Auto layout everywhere** — use auto layout + constraints for every frame so resizing is deterministic. Layout should be responsive, never fixed-positioned.
4. **Frames map to screens, screens map to FRs** — name frames after the use case + screen; a flow is a set of frames with the interactions between them.

## Handoff to code (the AI contract)

- Produce a `tokens.css` (or `tokens.json`) from the Figma variables: colors, type scale, spacing, radius, shadows.
- Produce a **component spec** per component: props, variants, states, slot structure, spacing used, a11y notes (roles, focus, contrast).
- Produce the **layout spec** per screen: breakpoints, auto-layout structure (direction, gap, padding), responsive behavior.
- The developer / AI in Phase 03 must be able to recreate the UI from tokens + component specs + layout specs WITHOUT opening Figma.

## Integration with the project loop

1. Read `docs/status.md` and the target use case from `docs/02-elaboration/`.
2. Produce `docs/02-elaboration/ui-ux/<use-case>-tokens.css|json`, `-components.md`, `-layout.md`.
3. Map every screen/component to its FR and Gherkin scenario.
4. Spawn the `design-reviewer` subagent to verify: token-only styling, component reuse, responsive structure, handoff completeness, a11y, traceability.
5. Iterate until PASS (max 3 iterations), then record in `docs/status.md`.

## Validation checklist (used by design-reviewer)

- [ ] Tokens exist as variables and are exported (CSS/JSON), no raw values in specs
- [ ] Semantic naming for colors/type/spacing (no `blue-500`, no `font-16`)
- [ ] Repeated elements are components with variants, not duplicated frames
- [ ] Auto layout + constraints used; no fixed absolute positioning
- [ ] Handoff complete: tokens + component specs + layout specs recreate the UI without Figma
- [ ] Every screen maps to an FR and a Gherkin scenario
- [ ] Accessibility covered: roles, focus states, AA contrast
- [ ] Design-system vocabulary reused in the code step

## Do / Don't

- DO build tokens before components, components before screens.
- DO export tokens so design and code can't drift.
- DON'T style with raw values inside frames.
- DON'T duplicate a UI element as a new frame when a component exists.
- DON'T hand off a screen without its responsive layout spec.
