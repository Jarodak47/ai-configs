---
name: stack-media
description: Media generation and editing best practices for the AGENTS.md workflow — Remotion (programmatic video in React) and DaVinci Resolve (editing and color grading). Use when the project involves programmatic video generation, video editing, or color grading.
---

# Stack — Media (Remotion / DaVinci Resolve)

Best practices for programmatic video generation (Remotion) and video editing/color grading (DaVinci Resolve).

## Precondition

- Use case defined: what video, for whom, output spec (resolution, fps, duration, platforms).
- Asset inventory known (footage, audio, fonts, brand assets).

## Remotion (programmatic video in React)

- Structure: one composition per video/segment; components for reusable visual elements; `Composition` registered with `id`, `durationInFrames`, `fps`, `width`, `height`.
- Drive everything from **data**, not hardcoded values: scene data (text, numbers, images) as typed props; rendering stays data-driven and testable.
- Time: use `useCurrentFrame()` and `interpolate()` for animation — never animate with state/effects; every animation is a pure function of time.
- Fonts, images, audio: import and preload explicitly; avoid runtime network fetches in compositions.
- Performance: keep compositions lightweight; memoize heavy components; render in chunks/parallel workers for long videos.
- Brand/consistency: define a `theme` object (colors, fonts, spacing) matching the project design tokens — reuse `design-figma` tokens if they exist.
- Rendering: `npx remotion render` to mp4; audio via `Audio`/`Sequence`; export specs locked before rendering (resolution, fps, codec).

## DaVinci Resolve (editing / color grading)

- Project setup: timeline resolution and framerate match delivery spec from the start — changing later breaks conforms.
- Edit: cut by story beats, not by clip; use the source/record workflow; keep a clean timeline structure (video/audio tracks organized).
- Color: grade in a logical order — primary correction → secondary → looks; use nodes with clear naming (never one giant node).
- Scopes (waveform, vectorscope) drive decisions, not the monitor; skin tones on the correct luma line.
- Export: match the platform deliverable (codec, bitrate, LUT/color space) — use the project's export preset and name outputs by convention.
- AI-assisted editing (where applicable): use it for rough cuts/selects, but human review of every cut point remains mandatory.

## Integration with the project loop

- Remotion code is normal React/TS code: it goes through Phase 03 like any feature — unit tests where logic exists (interpolation, data transforms), lint clean, one use case at a time.
- Video specs (resolution, fps, duration, audience) are traceable to the FR/use case in `docs/02-elaboration/`.
- DaVinci assets/timeline: document the deliverable spec in the project docs; keep graded/edited exports versioned by name+version.

## Validation checklist (used by reviewer)

- [ ] Composition registered with explicit `durationInFrames`, `fps`, resolution matching the spec
- [ ] Animations are pure functions of time (`useCurrentFrame`/`interpolate`), no state-based animation
- [ ] Scene content data-driven, not hardcoded
- [ ] Assets preloaded; no runtime fetches in composition
- [ ] Theme/tokens consistent with project design tokens
- [ ] Render spec locked (resolution, fps, codec) and documented
- [ ] Remotion code: tests where logic, lint clean
- [ ] Deliverable spec (codec, color space) documented for DaVinci exports

## Do / Don't

- DO make every animation a pure function of time.
- DO drive scenes from data.
- DON'T animate with state/effects in Remotion.
- DON'T change resolution/fps mid-project.
- DON'T generate a whole video feature in one shot — one composition/use case at a time.
