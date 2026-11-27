# babissimo.net

The Quarto source for [babissimo.net](https://babissimo.net). Every push to `main` runs `.github/workflows/publish.yml`, which renders the site into the `gh-pages` branch, and GitHub Pages serves that branch.

## Writing from Obsidian

The repository root opens as an Obsidian vault, and the [Obsidian Git](https://github.com/Vinzent03/obsidian-git) plugin commits and pushes from it, so a post can be written and published from a laptop or a phone.

### Setting up a device

1. Install the Obsidian Git community plugin. On a laptop, open a clone of this repository as a vault. On a phone, create an empty vault (not in iCloud), give the plugin your GitHub username and a fine-grained token limited to this repository with *Contents: Read and write*, then run **Git: Clone an existing remote repo** with `https://github.com/Babissimo/babissimo.github.io.git`. When it asks, say the repository has no `.obsidian` directory (see below).
2. Under *Settings → Files and links*, set **Default location for new attachments** to *Same folder as current file*, so a post's images stay with it. Links work in either format; with **Use [[Wikilinks]]** off, also set **New link format** to *Relative path to file*, the only Markdown links Quarto resolves.
3. Enable the core **Templates** plugin and set its folder to `_templates`.

`.obsidian/` is gitignored, so each device keeps its own settings.

### Writing a post

A post is a folder holding a note of the same name and its images, such as `my-post/my-post.md`, so every note's name is unique in Obsidian. Keep other notes out of post folders: the build stops if one holds two. Start it in `blog/_drafts/`, which Quarto never builds, and fill in the front matter with **Templates: Insert template**, choosing `post`. To publish, move the folder to `blog/posts/`; it goes live at `/blog/posts/my-post/` on the next push. The slug is the URL, so renaming a published post means renaming both folder and note, and breaks links to it from elsewhere. With **Automatically update internal links** on (*Settings → Files and links*), Obsidian rewrites links to the post as it moves.

`draft: true` in the front matter also keeps a post in `blog/posts/` off the site: Quarto renders it as an empty page and leaves it out of the listing, feed and search.

### What carries over

`tools/obsidian.lua` translates the Obsidian syntax that Pandoc would otherwise print verbatim:

| Obsidian | On the site |
|---|---|
| `> [!note] Title` callouts, folding included | Quarto callouts, with Obsidian's other types mapped onto note, tip, important and warning |
| `%%comments%%`, inline or across paragraphs | removed; outside a draft, one the filter cannot reach, such as in a table cell, fails the render |
| `==highlights==` | highlighted text |
| `[[wikilinks]]`, with aliases and `#headings` | links to the page, showing its title when there is no alias; one to nothing, or to a draft, is plain text |
| `![[image.png]]`, sized with `\|200` | images; an embedded note becomes a link to it |
| ` ```mermaid ` blocks | diagrams in the site's colours |

The repository is public: drafts and comments stay off the site but can be read on GitHub.
