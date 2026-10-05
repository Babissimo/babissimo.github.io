#!/usr/bin/env python3
"""Stop the rest of the rendered site linking to the blog.

The blog stays published at /blog/; this only removes the ways in. Switched by
BLOG_LINKS in _environment. With BLOG_LINKS=false it strips:

- navbar items that lead into the blog, on every page;
- other links into the blog, feed autodiscovery included, on pages outside it;
- blog pages from search.json and sitemap.xml.

It then fails the render if any of those links survive, as they would if
Quarto's markup drifted from the patterns below. With BLOG_LINKS=true the
render is left as Quarto wrote it.

Wired up via `post-render` in _quarto.yml, after clean-urls.py.
"""

import json
import os
import pathlib
import posixpath
import re
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
# Absolute links (feed autodiscovery, the sitemap) name the site by this host.
HOST = (ROOT / "CNAME").read_text(encoding="utf-8").strip().lower()

# A tag's attributes, allowing `>` inside quoted values.
ATTRS = r"""(?:[^>"']|"[^"]*"|'[^']*')*"""
NAV_ITEM = re.compile(r'[ \t]*<li class="nav-item[^"]*">.*?</li>[ \t]*\n?', re.S)
LINK = re.compile(rf"[ \t]*<link\b{ATTRS}>\n?")
ANCHOR = re.compile(rf"(<a\b{ATTRS}>)(.*?)</a>", re.S)
HREF = re.compile(r'\bhref="([^"]*)"')
HEADER = re.compile(r'<header id="quarto-header".*?</header>', re.S)
SITEMAP_URL = re.compile(r"[ \t]*<url>.*?</url>\n?", re.S)
LOC = re.compile(r"<loc>([^<]*)</loc>")


def site_path(href: str, page: str) -> str | None:
    """Resolve a link on `page` to a path within the site, or None if it leaves."""
    url = urlsplit(href)
    path = url.path
    if url.scheme or url.netloc:
        if url.hostname not in {HOST, f"www.{HOST}"}:
            return None
        path = path or "/"
    elif not path:
        return None  # a fragment on the same page
    return posixpath.normpath(posixpath.join(posixpath.dirname(page), path)).lstrip("/")


def in_blog(path: str | None) -> bool:
    return path is not None and (path == "blog" or path.startswith("blog/"))


def links_blog(markup: str, page: str) -> bool:
    href = HREF.search(markup)
    return href is not None and in_blog(site_path(href.group(1), page))


def drop_blog(pattern: re.Pattern, text: str, page: str) -> str:
    """Remove each match of `pattern` whose first href leads into the blog."""
    return pattern.sub(lambda m: "" if links_blog(m.group(0), page) else m.group(0), text)


def clean_page(text: str, page: str) -> str:
    # The navbar is shared, so its blog items go everywhere, the blog included.
    text = drop_blog(NAV_ITEM, text, page)
    if in_blog(page):
        return text
    text = drop_blog(LINK, text, page)
    # Navbar links only ever go as whole items, so one NAV_ITEM misses stays
    # live for stray_links to catch instead of being unwrapped into dead text.
    header = HEADER.search(text)
    start = header.end() if header else 0
    body = ANCHOR.sub(lambda m: m.group(2) if links_blog(m.group(1), page) else m.group(0), text[start:])
    return text[:start] + body


def stray_links(text: str, page: str) -> bool:
    """Whether a link into the blog survives where clean_page should have removed it."""
    scope = "".join(HEADER.findall(text)) if in_blog(page) else text
    return any(in_blog(site_path(href, page)) for href in HREF.findall(scope))


def clean_search(text: str) -> str:
    entries = json.loads(text)
    kept = [e for e in entries if not in_blog(site_path(e["href"], ""))]
    if len(kept) == len(entries):
        return text
    return json.dumps(kept, indent=2, ensure_ascii=False)


def clean_sitemap(text: str) -> str:
    def drop(m: re.Match) -> str:
        loc = LOC.search(m.group(0))
        return "" if loc and in_blog(site_path(loc.group(1), "")) else m.group(0)

    return SITEMAP_URL.sub(drop, text)


def main() -> int:
    flag = os.environ.get("BLOG_LINKS")
    if flag not in {"true", "false"}:
        print(f"unlink-blog: BLOG_LINKS must be true or false, got {flag!r}", file=sys.stderr)
        return 1
    if flag == "true":
        print("unlink-blog: BLOG_LINKS=true, nothing to do")
        return 0
    if not SITE.is_dir():
        print(f"unlink-blog: no {SITE}, nothing to do", file=sys.stderr)
        return 0

    changed = 0
    stray = []
    for path in sorted(SITE.rglob("*")):
        if "site_libs" in path.parts:
            continue
        page = path.relative_to(SITE).as_posix()
        if path.suffix != ".html" and page not in {"search.json", "sitemap.xml"}:
            continue
        original = path.read_text(encoding="utf-8")
        if page == "search.json":
            cleaned = clean_search(original)
        elif page == "sitemap.xml":
            cleaned = clean_sitemap(original)
        else:
            cleaned = clean_page(original, page)
            if stray_links(cleaned, page):
                stray.append(page)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            changed += 1

    print(f"unlink-blog: rewrote {changed} file(s)")
    if stray:
        print(f"unlink-blog: links into the blog survive in {', '.join(stray)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
