# Site theme design — babissimo.github.io

**Date:** 2026-08-23
**Status:** Approved design, ready for implementation planning

## Context

The site is a Quarto 1.10.18 website with four surfaces: an empty landing page,
a blog listing over `blog/posts/`, a projects listing, and an about page. It
currently uses the stock Bootswatch pair `flatly`/`darkly` with an empty
`styles.css`. A `post-render` hook (`tools/clean-urls.py`) rewrites output to
clean URLs.

The goal is a theme that reads as **warm, simple, and beautiful**, with room for
quirky accents — mathematical character and small animations — that the site
owner will add later.

## Decisions

Each was chosen from rendered alternatives rather than described in the
abstract.

| Decision | Choice | Rationale |
|---|---|---|
| Typographic direction | Fraunces headings over Source Sans 3 body | Personality lives in the headings; reading text stays quiet |
| Dark mode | Keep, rebuilt warm | An ink-brown dark palette reads as the same site at night, not a stock inversion |
| Post layout | Single centred 640px column, no margin gutter | Essays, not documents |
| Table of contents | Ambient right-edge rail, frosted panel on hover | Keeps the centred column intact while the section list stays reachable |
| Landing page | Baseline poster wordmark, bottom-left | All the air sits above the name, which is where a future animation wants to live |

## Scope

**In:** theme layer (brand, SCSS, code highlighting) across every page; blog and
projects listings; landing page; 404 page.

**Out:** favicon; the owner's later mathematical accents and animation; any
content writing beyond placeholder tagline text.

## 1. Foundations — `_brand.yml`

Quarto 1.10's `brand` key accepts separate light and dark definitions
(confirmed in `document-options.yml`: *"an object with light and dark brand
paths or definitions"*). Branding is therefore declared once in `_quarto.yml`,
pointing at `_brand.yml` and `_brand-dark.yml`, rather than being scattered
through per-format theme options.

### Typography

| Role | Family | Notes |
|---|---|---|
| Headings | Fraunces | Variable; `SOFT 50`, `WONK 1`, weight 600 |
| Body | Source Sans 3 | 17px, line-height 1.65 |
| Code | JetBrains Mono | — |

All three are `source: google`, so Quarto downloads and self-hosts them. The
built site must make **no external font requests at runtime**.

### Palettes

| Role | Light | Dark |
|---|---|---|
| background | `#FDFBF7` | `#191614` |
| surface (code, cards) | `#F5F1E8` | `#221E1B` |
| rule | `#EAE3D8` | `#332D28` |
| foreground | `#1F1D1A` | `#EDE7DC` |
| muted | `#6B6459` | `#A69C8D` |
| accent | `#B4553A` | `#E08A63` |

Dark is warm ink-brown rather than grey-black. The accent lightens in dark mode
to hold contrast against it.

## 2. Page furniture

- Posts render at a **640px measure, centred**. The margin column collapses to
  zero width so the text is genuinely centred, rather than Quarto's default
  centred-minus-a-gutter.
- **Navbar** loses Bootstrap's slab background: paper-coloured, one hairline
  rule beneath, Fraunces wordmark on the left, existing links and icons right.
- **Title blocks** drop `title-block-banner` on the blog listing. Date in
  letterspaced small caps above, Fraunces title, hairline below.

**Trade-off, accepted:** collapsing the margin column forecloses sidenotes and
`.column-margin` figures. This follows directly from choosing the plain essay
layout. Reversing it is a one-line change, at the cost of shifting body text
left of centre.

## 3. The contents rail

Quarto emits the TOC as:

```html
<div id="quarto-margin-sidebar" class="sidebar margin-sidebar">
  <nav id="TOC" role="doc-toc" class="toc-active">
    <ul><li><a href="#alpha" class="nav-link active" data-scroll-target="#alpha">Alpha</a></li></ul>
  </nav>
</div>
```

Quarto's own scroll-spy toggles `.active`. The rail is therefore **pure CSS over
existing markup — no JavaScript**:

- `#quarto-margin-sidebar` becomes `position: fixed`, right edge, vertically
  centred.
- `#toc-title` is visually hidden.
- Each `a.nav-link` gets `color: transparent` (label invisible but still
  occupying width, so nothing reflows on reveal) plus an `::after` mark with an
  explicit background colour.
- `a.nav-link.active` gets a longer mark in the accent, and its label in the
  accent once revealed.
- Nested `ul` (h3 and below) get shorter, indented marks.
- The frosted panel is a `::before` on the sidebar: `rgba(253,251,247,.72)` with
  `backdrop-filter: blur(7px)`, `opacity` 0 → 1 on `:hover`. Dark mode swaps to
  `rgba(25,22,20,.72)`.

### Breakpoints

| Viewport | Behaviour |
|---|---|
| ≥ 1200px | Rail sits in empty margin; frost stays off, marks bare |
| 900–1200px | Frost fades in with the labels, so they never sit on prose |
| < 900px | Rail hidden; Quarto's built-in collapsible "On this page" takes over |

The last row matters because hover is meaningless on touch devices.

`backdrop-filter` needs a `-webkit-` prefix and a solid-colour fallback for
browsers that lack it — without the fallback the panel is transparent and the
clash returns.

## 4. Landing page

`index.qmd` becomes a full-viewport stage. Wordmark **Babissimo** in Fraunces,
sat on the baseline at bottom-left: weight 700, `opsz 144`, low `SOFT` for
sharper terminals, `WONK 1`; the `-issimo` tail set in Fraunces italic at light
weight and high `SOFT`, in the accent — the Italian superlative set the way a
musical dynamic is.

Directly beneath, left-aligned to the wordmark: the tagline **"Here lay
dragons."** in letterspaced Source Sans small caps, muted tone.

Sizing via `clamp()` so it scales without breaking; `white-space: nowrap` on the
wordmark with a documented minimum viewport below which it may wrap.

An empty `<div class="landing-stage">` occupies the air above the wordmark,
reserved for the owner's later animation, so nothing needs restructuring when it
arrives.

The existing `include-in-header` RSS `<link>` in `index.qmd` is preserved.

*Open alternative:* the tagline could instead sit at the right end of the same
baseline, spanning the bottom edge. One-line change; decide once it is live.

## 5. Listings

Blog and projects share one custom EJS template. Quarto's default cards are
replaced by a plain reading list:

- date in letterspaced small caps
- Fraunces title
- one-line excerpt in muted tone
- categories as small text-only tags in the accent, not pills
- hairline rule between entries

Projects uses the same template, with the description carrying more weight than
the date.

`feed: true`, `sort: "date desc"`, and `categories: true` are retained on the
blog listing.

## 6. 404 page

`404.qmd`, same chrome as any page: Fraunces heading, one short line, a link
home. Deliberately unclever.

## 7. Code and math

- Paired `.theme` files for light and dark highlighting, tuned to the palette:
  warm, low-contrast, no neon.
- Code blocks on `surface` with a 2px accent left border.
- **Switch `html-math-method` from MathJax to KaTeX.** It renders faster, ships
  Computer Modern-derived faces that sit well beside Fraunces, and is far easier
  to style — the main lever on "beautiful mathematical character."

**Risk:** KaTeX supports a narrower slice of LaTeX than MathJax; macro-heavy
markup can fail to render. `blog/posts/` currently holds a single post
(`welcome`), so exposure today is near zero, but this constrains what can be
written later. Reverting is a one-line change in `_quarto.yml`.

## 8. File manifest

| File | Action | Contents |
|---|---|---|
| `_brand.yml` | new | Light palette, typography |
| `_brand-dark.yml` | new | Dark palette |
| `_quarto.yml` | edit | `brand:`, layout, `html-math-method: katex`, 404 |
| `custom.scss` | new | Rail, navbar, listings, title blocks, landing |
| `custom-dark.scss` | new | Dark-only overrides |
| `theme-light.theme` | new | Code highlighting, light |
| `theme-dark.theme` | new | Code highlighting, dark |
| `_listing.ejs` | new | Shared blog/projects template |
| `index.qmd` | edit | Landing wordmark and tagline |
| `404.qmd` | new | Themed not-found page |
| `styles.css` | delete | Empty; folded into SCSS |

## 9. Risks and unknowns

Three items are designed but not yet proven, and should be verified early in
implementation rather than at the end:

1. **Zero-width margin column.** The mechanism for a genuinely centred 640px
   body — `grid: margin-width: 0px` under `page-layout: article`, versus
   `page-layout: full` with an explicit `max-width` on `main.content` — has not
   been tested against Quarto's grid. Settle this first; the rail's positioning
   depends on it.
2. **EJS listing template.** Field availability for the projects listing needs
   checking against actual project front-matter.
3. **Rail across Quarto upgrades.** The CSS depends on Quarto's TOC markup
   (`#quarto-margin-sidebar`, `nav#TOC`, `a.nav-link.active`). This is stable
   public structure, but a future Quarto release could change it. Being
   CSS-only, the failure mode is cosmetic, not broken.

## 10. Verification

The theme is done when, on a rendered site:

- Both palettes render correctly and the toggle switches cleanly between them.
- No network requests leave the origin for fonts.
- The rail shows marks, tracks the active section on scroll, reveals frosted
  labels on hover, and hands off to the collapsible TOC below 900px.
- At 620px viewport width, rail labels never sit unbacked on body text.
- Landing wordmark holds its line from 1600px down to 380px.
- A post containing display and inline math renders under KaTeX without errors
  in the console.
- Blog and projects listings both render through the shared template, and the
  RSS feed still validates.

## Non-goals, restated

Favicon, landing-page copy beyond the tagline, and the owner's mathematical
accents and animation are out of scope. The rail's reveal establishes a motion
vocabulary — roughly 260ms, soft easing — worth reusing when those arrive.
