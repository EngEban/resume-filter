# TalentScope design direction

## North star

TalentScope should feel like a high-signal instrument for hiring decisions: precise, calm, and quietly confident. The interface should make dense resume intelligence feel legible in seconds, with indigo reserved for moments of action and insight.

## Visual mood

**Signal-rich · calm · editorial · precise · quietly optimistic**

This is not a neon AI dashboard and not a monochrome developer tool. It is a bright workspace with deep ink navigation, soft mineral surfaces, and one unmistakable indigo signal.

## Typography

- **Display:** large, tight, slightly editorial headings for page promises and major outcomes.
- **UI headings:** compact semibold titles with restrained tracking; hierarchy comes from scale and spacing rather than uppercase everywhere.
- **Body:** neutral slate, 15–16px, generous line height for explanation and confidence.
- **Data:** tabular numerals for scores, counts, and progress; use weight and color to convey meaning.
- **Eyebrows:** 10–11px uppercase labels only for context (“workspace”, “signal”, “next move”), never as the primary way to create hierarchy.

## Color rules

- Preserve brand indigo `#4F46E5` as the primary action and active signal.
- Use deep ink `#0F172A` / `#111827` for navigation chrome and high-emphasis text.
- Use warm mineral surfaces (`#F7F8FC`, `#EEF1F7`) for page background and subtle grouping.
- Use violet/cyan only as restrained data accents or ambient gradients; never as competing CTA colors.
- Use semantic green/amber/red only for status and score meaning.
- Avoid coloring every card border. Let whitespace, shadow, and small signal rules create hierarchy.

## Motion philosophy

Motion should explain state, not decorate stillness. Use 180–260ms for controls, 420–700ms for page entry and progress, and one soft continuous ambient loop per major surface at most. Stagger related content by 40–60ms. All motion is disabled or reduced under `prefers-reduced-motion: reduce`; critical information must never depend on animation.

## Component personality

- **Buttons:** confident, compact, slightly rounded; primary buttons have a small signal glow and directional arrow, secondary buttons are quiet and solid.
- **Cards:** low-contrast borders, layered backgrounds, 18–24px radii, and hover lift only where the surface is actionable.
- **Badges:** short, semantic, and pill-shaped with a small dot instead of visual noise.
- **Inputs:** tall enough for touch, strong focus ring, clear placeholder, and a visible error state that does not rely on color alone.
- **Lists:** dense enough for scanning but with one clear leading identity block and one clear decision metric.
- **Empty states:** a calm illustration/motif, one sentence of context, and one next action.

## Signature interaction

The TalentScope signature is the **Signal Reveal**: when an analysis or batch becomes ready, a restrained indigo scan ring resolves into the score, then the score breakdown bars fill in sequence. The effect is CSS-only, short, and meaningful. It should feel like the product is bringing signal into focus—not like a celebration animation pasted onto a dashboard.

## Application pattern

Every route follows the same skeleton:

1. Responsive shell with clear workspace context.
2. Page header with eyebrow, title, supporting sentence, and a single primary action.
3. One focal insight or task surface.
4. Supporting data grouped into quiet surfaces.
5. Purposeful loading, empty, error, and retry states.

This direction is intentionally compatible with the existing API and route contracts. It is implemented with CSS and small React state changes only; no animation library is required.
