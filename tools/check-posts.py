#!/usr/bin/env python3
"""Fail the render if two posts would publish to the same page.

blog/posts/_metadata.yml writes every page under blog/posts/ to index.html
in its own folder, so each folder may hold one page, and blog/posts/ itself
none. Anything else would silently overwrite a post.

Wired up via `pre-render` in _quarto.yml.
"""

import collections
import pathlib
import sys

POSTS = pathlib.Path(__file__).resolve().parent.parent / "blog" / "posts"
PAGES = {".md", ".qmd", ".ipynb"}


def main() -> int:
    folders = collections.defaultdict(list)
    for path in POSTS.rglob("*"):
        rel = path.relative_to(POSTS)
        # Quarto renders nothing whose path has a `_` or `.` segment.
        if path.suffix in PAGES and not any(p.startswith(("_", ".")) for p in rel.parts):
            folders[path.parent].append(rel.as_posix())

    clashes = 0
    for folder, pages in sorted(folders.items()):
        names = ", ".join(sorted(pages))
        if folder == POSTS:
            print(f"check-posts: {names} sits directly in blog/posts/; "
                  "give each post a folder of its own", file=sys.stderr)
        elif len(pages) > 1:
            print(f"check-posts: {names} would publish as one index.html; "
                  "keep one page per post folder", file=sys.stderr)
        else:
            continue
        clashes += 1
    return 1 if clashes else 0


if __name__ == "__main__":
    raise SystemExit(main())
