# LabQubit design system

Source of truth: `styles/tailwind.css`. A live preview of every component is at
`/styleguide` (visible to System Managers only).

## Brand

- **Name:** always written "LabQubit" (capital L and Q).
- **Idea:** a qubit is a superposition. The palette blends **Qubit blue** into **Superposition
  violet**, with **Signal cyan** used sparingly for live data such as stats, "online" dots and
  uptime figures.
- **Mood:** calm, precise, engineered. Dark navy canvas, glass surfaces, one bright accent per view.

## Color

| Token | Dark (default) | Light | Use |
|---|---|---|---|
| `canvas` | `#05070F` | `#FFFFFF` | page background |
| `canvas-soft` | `#0A0F1E` | `#F5F7FC` | alternating sections, inputs |
| `surface` | white 4% | white 72% | glass cards (with backdrop blur) |
| `line` / `line-strong` | white 8% / 16% | ink 9% / 18% | borders, dividers |
| `fg` | `#E8ECF8` | `#0A0F1E` | headings, primary text |
| `muted` | `#9AA4BF` | `#4B5570` | body copy |
| `subtle` | `#8A94B0` | `#5F6985` | captions, meta |
| `link` | `#A3ADFF` | `#3A3FD4` | inline links |

Fixed scales: `brand-50…950` (500 = `#5B6CFF`), `accent-300…600` (500 = `#A855F7`),
`signal-300…500` (400 = `#22D3EE`), `ink-50…950`.

Every text/background pair above passes **WCAG AA** (the lowest is 5.1:1). Primary buttons use
`brand-600` with white text (5.7:1). `brand-500` is only used for hover and decoration.

Theme: dark first. `<html data-theme="dark|light">` is set before the first paint, from
`localStorage` (`lq-theme`), defaulting to dark. Use semantic classes (`bg-canvas`,
`text-muted`, `border-line`), so that components flip theme on their own without `dark:`
variants.

## Typography

| Role | Class | Size (mobile → desktop) |
|---|---|---|
| Display (hero) | `.lq-display` | 36 → 60 px, weight 600, tight tracking |
| Section title | `.lq-h2` | 30 → 36 px |
| Card title | `.lq-h3` | 18 px |
| Lead paragraph | `.lq-lead` | 18 → 20 px, `muted` |
| Body | default | 16 px / 28 px line height |
| Eyebrow | `.lq-eyebrow` | 12 px pill above section titles |

- English uses **Inter** (variable, self-hosted, Latin + Latin Extended).
- Arabic uses **IBM Plex Sans Arabic** (400/500/600/700, self-hosted, Arabic code points only).
  Both sit in one font stack, so mixed-script text renders correctly.
- In RTL, letter-spacing is forced to 0, because tracking breaks joined Arabic letters.

## Spacing and shape

- Container: `.lq-container`, max width 1280 px, 20/24/32 px gutters.
- Section rhythm: `.lq-section` (80/96/112 px vertical), `.lq-section-tight` (56/64 px).
- Radius: inputs and buttons `xl` (14 px), cards `2xl` (20 px), hero panels `3xl` (28 px).
- Shadows: `shadow-glow` (brand halo, primary buttons and hovered cards), `shadow-soft` (light mode).

## Components (CSS)

`.lq-btn` + `-primary | -secondary | -ghost`, sizes `-sm | -lg` ·
`.lq-card` (+ `.lq-card-hover`) · `.lq-glass` · `.lq-icon-tile` · `.lq-badge` + `-brand | -success | -warning | -danger` ·
`.lq-label` `.lq-input` `.lq-help` `.lq-error` `.lq-check` · `.lq-prose` (rich text) ·
`.lq-table` · `.lq-grid-bg` `.lq-mesh` `.lq-circuit` `.lq-hairline` · `.lq-nav` `.lq-mega` ·
`.lq-marquee` `.lq-slider` · `.lq-icon` (`.lq-icon-flip` for arrows in RTL).

Jinja macros that combine them (hero, section header, card, CTA band, stats, testimonial,
logo strip) live in `labqubit/templates/components/` (Phase 3).

## Motion

- Scroll reveal: add `data-reveal` (slide up and fade) or `data-reveal="fade"`. Stagger items
  with `style="--reveal-delay: 120ms"`. About 1 KB of IntersectionObserver code, no library.
- Hero: drifting blurred gradient blobs (`.lq-mesh`) over a masked grid, plus animated circuit
  traces drawn in SVG. Pure CSS, GPU-friendly transforms only.
- Counters: `data-count-to="250"` animates once when visible.
- `prefers-reduced-motion` disables all animation and reveals content immediately.

## Icons

Lucide (ISC license), 1.75 px stroke, 20 px default. Icons are bundled into one SVG sprite
(`/assets/labqubit/icons/sprite.svg`) by `scripts/vendor-assets.mjs`. The sprite contains only:

- icons used in templates through `icon("name")`, and
- the editor-selectable list in `styles/icons.json`.

Social icons (LinkedIn, X, Instagram, YouTube, Facebook, WhatsApp) are drawn in the same stroke
style in `styles/icons/`, since Lucide removed brand icons.

## RTL rules

- Use logical utilities only: `ms-* me-* ps-* pe-* start-* end-* text-start text-end border-s border-e`.
- Never use `ml-*`, `mr-*`, `left-*`, `right-*` or `text-left` for layout.
- Arrows and chevrons get `.lq-icon-flip`.
- Layout direction comes from `<html dir>`; no separate RTL stylesheet is needed.

## Performance budget

| Asset | Budget |
|---|---|
| CSS | < 60 KB minified (one file, cached by content hash) |
| JS | < 10 KB (`site.js`, no frameworks); Frappe's 400 KB web bundle is not loaded on our pages |
| Fonts | 1 Latin file (48 KB) is preloaded; Arabic weights load only on Arabic pages |
| Images | WebP, explicit width/height, `loading="lazy"` below the fold |
