# Site theme design — babissimo.github.io

**Date:** 2026-08-23
**Status:** Approved design, ready for implementation planning

## Context

The site is a Quarto 1.10.18 website with five surfaces: an empty landing page,
a blog listing over `blog/posts/`, a projects listing driven by
`projects/projects.yml`, an about page using Quarto's `trestles` template, and
individual posts. It currently uses the stock Bootswatch pair `flatly`/`darkly`
with an empty `styles.css`. A `post-render` hook (`tools/clean-urls.py`)
rewrites output to clean URLs.

The goal is a theme that reads as **warm, simple, and beautiful**, with room for
quirky accents — mathematical character and small animations — that the site
owner will add later.

## Decisions

Every choice below was made against rendered alternatives rather than described
in the abstract.

| Decision | Choice | Rationale |
|---|---|---|
| Typographic direction | Fraunces headings over Source Sans 3 body | Personality in the headings; reading text stays quiet |
| Dark mode | Keep, rebuilt warm | Ink-brown dark reads as the same site at night, not a stock inversion |
| Post layout | Single centred 640px column, no margin gutter | Essays, not documents |
| Table of contents | Ambient right-edge rail, frosted panel on hover | Keeps the centred column intact while the section list stays reachable |
| Landing page | Baseline poster wordmark, bottom-left | All the air sits above the name, where a future animation wants to live |
| Blog listing | One-line index, no post count | Reads as an archive; scales to many posts |
| Projects listing | Stacked entries | No dates or images to fill an index row |
| About page | Portrait left, circular, split-name masthead | Least disruptive to what exists, while adopting the new type |
| 404 | Poster numeral with the cartographic line | Reuses the landing treatment; pays off the tagline |
| Favicon | Anchor | The only piratical option that survives 16px |
| Anchor motif | Section breaks, end mark, footer, 404 watermark | Carries the favicon through the site |
| Math engine | MathJax, unchanged | Sanely version-pinned; best coverage and accessibility |

## Scope

**In:** theme layer (brand, SCSS, code highlighting) across every page; blog
listing; projects listing; about page; landing page; 404 page; favicon.

**Out:** the owner's later mathematical accents and animation; any content
writing beyond the tagline.

## 1. Foundations — `_brand.yml`

Quarto 1.10's `brand` key accepts separate light and dark definitions
(confirmed in `document-options.yml`: *"an object with light and dark brand
paths or definitions"*). Branding is declared once in `_quarto.yml`, pointing at
`_brand.yml` and `_brand-dark.yml`.

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
to hold contrast.

## 2. Page furniture

- Posts render at a **640px measure, centred**. The margin column collapses to
  zero width so the text is genuinely centred rather than centred-minus-a-gutter.
- **Navbar** loses Bootstrap's slab background: paper-coloured, one hairline
  rule beneath, Fraunces wordmark left, existing links and icons right.
- **Title blocks** drop `title-block-banner`, which is currently set both in
  `blog/posts/_metadata.yml` and on the two listing pages. Date in letterspaced
  small caps above, Fraunces title, hairline below.

**Trade-off, accepted:** collapsing the margin column forecloses sidenotes and
`.column-margin` figures, following from the plain essay layout. Reversing it is
a one-line change, at the cost of shifting body text left of centre.

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
| ≥ 1200px | Rail sits in empty margin; frost off, marks bare |
| 900–1200px | Frost fades in with the labels, so they never sit on prose |
| < 900px | Rail hidden; Quarto's built-in collapsible "On this page" takes over |

The last row matters because hover is meaningless on touch devices.

`backdrop-filter` needs a `-webkit-` prefix and a solid-colour fallback for
browsers that lack it — without the fallback the panel is transparent and the
clash returns.

## 4. Landing page

`index.qmd` becomes a full-viewport stage. Wordmark **Babissimo** in Fraunces,
sat on the baseline at bottom-left: weight 700, `opsz 144`, low `SOFT` for
sharper terminals, `WONK 1`; the `-issimo` tail in Fraunces italic at light
weight and high `SOFT`, in the accent — the Italian superlative set the way a
musical dynamic is.

Beneath it, left-aligned to the wordmark: the tagline **"Here lay dragons."** in
letterspaced Source Sans small caps, muted tone.

Sizing via `clamp()`; `white-space: nowrap` on the wordmark with a documented
minimum viewport below which it may wrap.

An empty `<div class="landing-stage">` occupies the air above the wordmark,
reserved for the owner's later animation.

The existing `include-in-header` RSS `<link>` in `index.qmd` is preserved.

*Open alternative:* the tagline could instead sit at the right end of the same
baseline, spanning the bottom edge. One-line change; decide once live.

## 5. Blog listing

A one-line index, not a feed:

- date, letterspaced small caps, fixed ~96px column
- Fraunces title, flexible column
- categories trailing, in the accent, text-only — no pills
- hairline rule between rows
- **no post count** beneath the page title

`feed: true`, `sort: "date desc"` and `categories: true` are retained.

**Trade-off, accepted:** an index tells a new reader nothing about any post; the
categories are the only signal. Posts carry a `subtitle` that this layout
discards. If it reads too bare in practice, the subtitle can fade in on hover
above 1200px without altering the layout — deferred, not designed in.

## 6. Projects listing

Projects carry only `title`, `description`, and an external `path` — no date, no
image — so they cannot reuse the blog index row, whose left column would be
empty. Instead, stacked entries:

- Fraunces title on its own line, followed by a small `↗` marking the external
  destination
- description beneath in the muted tone
- hairline rule between entries

**This means two listing templates, not one.** An earlier draft of this spec
assumed a single shared template; the differing field sets make that a false
economy.

## 7. About page

Keeps the existing `profile.jpg` and the LinkedIn/GitHub links. Portrait left,
text right:

- **Portrait:** circular, 158px, left column
- **Links:** stacked vertically beneath the portrait, accent-coloured, each
  prefixed with a small `→`
- **Name:** "Alexander *Charters*" heading the text column — upright, with the
  surname in Fraunces italic in the accent, echoing the landing wordmark's split
- **Body:** flows in the right column at reading size

This is closest in bones to the current `trestles` template, so it may be
achievable by restyling `about: template: trestles` rather than replacing it.
Determine during implementation; a hand-built layout is the fallback.

**Trade-off, accepted:** the portrait leads the eye before the name does.

## 8. 404 page

The landing page's baseline-poster treatment, reused wholesale: `404` set large
in Fraunces bottom-left, with the middle `0` in italic and the accent, mirroring
the `Bab`/`issimo` split.

Beneath it: *"You have sailed off the edge of the map."* and a link reading
**Back to charted water**.

The parenthetical "(404)" from the earlier mockup is dropped — the numeral is
already set 100px tall immediately above the line.

## 9. Favicon

An anchor: rust `#B4553A`, 2.6–4px stroke on a 32×32 viewBox, transparent
background, `stroke-linecap`/`linejoin: round`. Ring, stem, crossbar, and a
curved fluke sweep. Stroke weight increases as size decreases; at 16px the ring
radius is reduced so it does not fill in.

Delivered as an SVG (`website: favicon:`), with a 32×32 PNG fallback and a
180×180 `apple-touch-icon` on the paper background, both via
`include-in-header`.

A single rust mark on a transparent ground reads acceptably against both light
and dark browser chrome, so no `prefers-color-scheme` variant is planned. If it
proves weak against dark chrome, add a second `<link rel="icon" media="(prefers-color-scheme: dark)">`
using the dark accent.

**Trade-off, accepted:** the anchor is the most legible of the options
considered and the most generic — it is nautical rather than piratical, and
widely used.

## 10. Anchor motif

The favicon's anchor recurs in four places. **Hierarchy is carried by colour,
not size:** the end mark is the only accent-coloured anchor and the only one not
sitting on a rule, so it reads as terminal against the grey structural marks
above and below it.

| Use | Size | Colour | Treatment |
|---|---|---|---|
| Section break (`---`/`<hr>`) | 14px | foreground, 34% | Centred on a hairline rule, gap either side |
| End of post | 19px | accent, 45% | Floating, centred, no rule, generous space above |
| Page footer | 10px | foreground, 30% | Right-aligned in the footer bar |
| 404 watermark | ~150px | foreground, 6% | Behind the numeral; reads as texture |

Dark mode substitutes the dark foreground and accent tokens at the same
opacities.

One shared inline SVG (32×32 viewBox, round caps and joins), sized and coloured
by CSS. The end mark and footer mark are inserted by CSS pseudo-elements rather
than authored per page.

**Rejected:** the anchor on heading links, and at the foot of the contents rail.
The heading-link version was the neatest pun available — Quarto already loads
AnchorJS and calls them anchor links — but four uses is already the ceiling for
a motif, and the rail is the one piece of custom code in the design, so it stays
uncomplicated.

## 11. Code and math

- Paired `.theme` files for light and dark highlighting, tuned to the palette:
  warm, low-contrast, no neon.
- Code blocks on `surface` with a 2px accent left border.
- **Math stays on MathJax.** No change to `html-math-method`.

An earlier draft of this spec proposed switching to KaTeX for speed and for
faces that sit better beside Fraunces. Testing both engines against a rendered
probe page withdrew that recommendation:

```
mathjax → <script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js">
katex   → <script src="https://cdn.jsdelivr.net/npm/katex@latest/dist/katex.min.js">
```

Two findings. First, **neither engine is self-hosted** — both load from
jsdelivr, and KaTeX fetches its fonts from there too, so the switch would not
have helped the no-external-requests goal as implied. Second, Quarto pins
MathJax to a major version (`@4`) but pins KaTeX to **`@latest`**, meaning the
site would silently track whatever KaTeX ships next.

MathJax also has materially better accessibility (speech text, subexpression
exploration) and broader LaTeX coverage, including autoloaded extension
packages. The visual gain from KaTeX did not justify the exposure.

**Known limitation, accepted:** math therefore depends on a CDN at page load. If
that becomes unacceptable, `html-math-method` accepts an object form —
`{method: mathjax, url: "/lib/mathjax"}` (schema confirmed in
`document-options.yml`) — allowing a pinned copy to be vendored into the repo.
Not planned now.

## 12. File manifest

| File | Action | Contents |
|---|---|---|
| `_brand.yml` | new | Light palette, typography |
| `_brand-dark.yml` | new | Dark palette |
| `_quarto.yml` | edit | `brand:`, layout, `favicon:`, page-footer |
| `custom.scss` | new | Rail, navbar, listings, title blocks, landing, about, 404, anchor motif |
| `custom-dark.scss` | new | Dark-only overrides |
| `theme-light.theme` | new | Code highlighting, light |
| `theme-dark.theme` | new | Code highlighting, dark |
| `_listing-blog.ejs` | new | Blog index template |
| `_listing-projects.ejs` | new | Projects stacked-entry template |
| `index.qmd` | edit | Landing wordmark and tagline |
| `about/index.qmd` | edit | Portrait-left layout |
| `blog/posts/_metadata.yml` | edit | Remove `title-block-banner` |
| `404.qmd` | new | Poster numeral, cartographic line |
| `assets/anchor.svg` + PNGs | new | Favicon set; same path reused by the motif |
| `styles.css` | delete | Empty; folded into SCSS |

## 13. Risks and unknowns

Four items are designed but not proven. Verify these early rather than at the
end:

1. **Zero-width margin column.** The mechanism for a genuinely centred 640px
   body — `grid: margin-width: 0px` under `page-layout: article`, versus
   `page-layout: full` with an explicit `max-width` on `main.content` — has not
   been tested against Quarto's grid. Settle this first; the rail's positioning
   depends on it.
2. **About page mechanism.** Whether `about: template: trestles` can be restyled
   into the portrait-left layout, or whether it must be hand-built.
3. **EJS templates.** Field availability for both listings needs checking
   against actual front-matter and `projects.yml`.
4. **Rail across Quarto upgrades.** The CSS depends on Quarto's TOC markup
   (`#quarto-margin-sidebar`, `nav#TOC`, `a.nav-link.active`). This is stable
   public structure, but a future release could change it. Being CSS-only, the
   failure mode is cosmetic, not broken.

## 14. Verification

The theme is done when, on a rendered site:

- Both palettes render correctly and the toggle switches cleanly between them.
- No network requests leave the origin for fonts. (Math is the documented
  exception — MathJax loads from jsdelivr; see §11.)
- The rail shows marks, tracks the active section on scroll, reveals frosted
  labels on hover, and hands off to the collapsible TOC below 900px.
- At 620px viewport width, rail labels never sit unbacked on body text.
- Landing wordmark holds its line from 1600px down to 380px.
- A post containing display and inline math renders under MathJax with no
  console errors, in both palettes.
- Blog and projects listings render through their own templates, and the RSS
  feed still validates.
- The favicon is identifiable at 16px against both light and dark browser
  chrome.
- On a post containing two `---` breaks, all four anchor uses are visible at
  once and the end mark still reads as terminal — it is the only accent-coloured
  anchor and the only one off a rule.
- `tools/clean-urls.py` still runs and its output is unaffected by the new
  pages.

## 15. Non-goals, restated

The owner's mathematical accents and animation are out of scope. The rail's
reveal establishes a motion vocabulary — roughly 260ms, soft easing — worth
reusing when those arrive.
