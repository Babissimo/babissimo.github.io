#!/usr/bin/env python3
"""Strip `index.html` from links in the rendered site.

Every page is emitted as `<name>/index.html`, so `foo/index.html` and `foo/`
address the same resource. Quarto writes file-relative links, which carry the
`index.html` even though the shorter form works. This rewrites them so
visitors see `/blog/` rather than `/blog/index.html`.

Wired up via `post-render` in _quarto.yml, so it runs on every render.
"""

import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent / "_site"

# href="…/index.html" -> href="…/", and a bare href="index.html" -> href="./"
HREF = re.compile(r'(href=")([^"]*?)index\.html(["#])')
# Absolute URLs in the feed and sitemap.
LOC = re.compile(r'(https?://[^\s"<]*?/)index\.html')


def clean(text: str) -> str:
    text = HREF.sub(lambda m: f'{m.group(1)}{m.group(2) or "./"}{m.group(3)}', text)
    return LOC.sub(r"\1", text)


def main() -> int:
    if not SITE.is_dir():
        print(f"clean-urls: no {SITE}, nothing to do", file=sys.stderr)
        return 0

    changed = 0
    for path in SITE.rglob("*"):
        if path.suffix not in {".html", ".xml", ".json"} or "site_libs" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        cleaned = clean(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            changed += 1

    print(f"clean-urls: rewrote {changed} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
