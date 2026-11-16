# Project tags: design

**Date:** 2026-11-16
**Status:** Approved

## Intent

Let a visitor to `/projects/` narrow the list by what kind of project it is,
and see each project's kind at a glance. The list is expected to grow, so the
tags are broad.

## Tags

| Tag | Projects |
|---|---|
| Tools | Ratchet, Therapy Search, Timeywimey |
| Data | Trials Trophies, World Happiness Visualisation |
| Learning | Strandbeest Simulator |
| Play | Torus Chess |

Timeywimey (`https://timeywimey.babissimo.net/`) is live but unlisted; it joins
the page at the top, with the description "Watch a video sliced through time at
an angle".

## Approaches

- **Quarto's built-in categories** (`categories: true`): filtering for free,
  but it draws a plain category list in the margin. The blog already turns it
  off (`categories: false`) in favour of inline labels, so it would sit at odds
  with the site.
- **Own filter in the listing template** (chosen): a row of tag buttons above
  the list and an inline label per card, styled like the blog's `.index-cat`.
  Full control of placement and look for a few lines of script.

## Design

- Each entry in `projects/projects.yml` carries `categories: [<Tag>]`; an entry
  may carry several.
- `_listing-projects.ejs` draws an *All* button plus one button per tag, in
  alphabetical order, and gives each row its tags as a data attribute and as
  labels beside the title.
- A small script shows only the rows carrying the chosen tag and records it in
  the URL fragment (`#tools`), so a filtered view can be linked. The fragment
  is replaced rather than pushed, so filtering adds nothing to history.
- Without script the buttons stay hidden and every card shows.

## Left to the builder

Button styling within the existing palette and type; mobile wrapping of the
button row.
