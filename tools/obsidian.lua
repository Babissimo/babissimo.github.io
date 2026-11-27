-- Render the Obsidian-only markdown that Pandoc would otherwise print verbatim:
--
-- - `%%comments%%` are dropped, as Obsidian hides them: inline, across
--   paragraphs, and unclosed to the end of the page (or of a footnote). A `%%`
--   the walk cannot reach (a table cell, a title, an attribute) fails the
--   render rather than print the note. The source stays readable in the
--   public repository.
-- - `> [!type] Title` callouts become Quarto callouts.
--
-- `==highlights==` need no filter: `from: markdown+mark` in _quarto.yml.

local MARK = "%%"

-- Obsidian's callout types, folded onto Quarto's five.
local CALLOUTS = {
  note = "note", info = "note", todo = "note", abstract = "note",
  summary = "note", tldr = "note", question = "note", help = "note",
  faq = "note", example = "note", quote = "note", cite = "note",
  tip = "tip", hint = "tip", success = "tip", check = "tip", done = "tip",
  important = "important", danger = "important", error = "important",
  failure = "important", fail = "important", missing = "important",
  bug = "important",
  warning = "warning", caution = "warning", attention = "warning",
}

-- Comments are lexical, so the walk runs in document order with one flag for
-- the whole page, and descends into every container a comment can cross.
local open = false

local function visible(text)
  local kept = ""
  while true do
    local at = text:find(MARK, 1, true)
    if not at then break end
    if not open then kept = kept .. text:sub(1, at - 1) end
    open = not open
    text = text:sub(at + #MARK)
  end
  if not open then kept = kept .. text end
  return kept
end

local function has_mark(text)
  return text:find(MARK, 1, true) ~= nil
end

local function fail(near)
  io.stderr:write(("obsidian.lua: %s has a %%%% comment where it cannot be stripped, "
    .. "near %q. Move it, or put a literal %%%% in `code`.\n"):format(
    quarto.doc.input_file, near))
  -- Quarto's `error` only logs and lets the render publish the page.
  os.exit(1)
end

local INLINE_HOLDERS = {
  Emph = true, Strong = true, Underline = true, Strikeout = true,
  Superscript = true, Subscript = true, SmallCaps = true, Span = true,
  Link = true, Quoted = true, Cite = true,
}

-- Code and raw text are never split: inside an open comment, a `%%` there may
-- or may not be its close, so the render stops rather than guess.
local VERBATIM = {
  Code = true, Math = true, RawInline = true, CodeBlock = true, RawBlock = true,
}

-- A draft publishes as an empty page, so a stray `%%` in it need not block
-- the deploy.
local draft = false

local function check_verbatim(el)
  if open and not draft and VERBATIM[el.t] and has_mark(el.text) then
    fail(el.text:match("[^\n]*%%%%[^\n]*"))
  end
end

local strip_blocks

-- Strip a container's children, and say whether the container stays. One that
-- was empty to begin with (`[]{.hook}`) is markup, and goes only inside a comment.
local function strip_children(el, strip)
  local had, was_open = #el.content, open
  el.content = strip(el.content)
  return #el.content > 0 or (had == 0 and not was_open)
end

local function strip_inlines(list)
  local out = pandoc.Inlines {}
  for _, el in ipairs(list) do
    if el.t == "Str" then
      local kept = visible(el.text)
      if kept ~= "" then out:insert(pandoc.Str(kept)) end
    elseif INLINE_HOLDERS[el.t] then
      if strip_children(el, strip_inlines) then out:insert(el) end
    elseif el.t == "Note" then
      -- The AST holds a note at its reference, but its source sits apart, so a
      -- comment left open inside it ends with the note.
      if not open then
        if strip_children(el, strip_blocks) then out:insert(el) end
        open = false
      end
    else
      check_verbatim(el)
      if not open then out:insert(el) end
    end
  end
  return out
end

local function contains_mark(block)
  local found = false
  block:walk { Str = function(el) found = found or has_mark(el.text) end }
  return found
end

-- Heading text as the reader slugs it, footnotes aside.
local function heading_text(inlines)
  return pandoc.utils.stringify(inlines:filter(function(el) return el.t ~= "Note" end))
end

-- Escaped, so text such as `<div>` from inline code is read back literally.
local function slug(text)
  local parsed = pandoc.read("# " .. (text:gsub("%p", "\\%0")), "markdown").blocks[1]
  return parsed and parsed.identifier or ""
end

-- Ids already on the page, so a renamed heading cannot collide with one.
local taken = {}

local function unique(id)
  local candidate, n = id, 0
  while id ~= "" and taken[candidate] do
    n = n + 1
    candidate = id .. "-" .. n
  end
  taken[candidate] = true
  return candidate
end

-- The reader derived the id from the text with its comment. An explicit
-- `{#id}` stays.
local function reslug(header, before)
  local auto, id = slug(before), header.identifier
  if id == auto or id:match("^" .. (auto:gsub("%p", "%%%0")) .. "%-%d+$") then
    header.identifier = unique(slug(heading_text(header.content)))
  end
end

function strip_blocks(list)
  local out = pandoc.Blocks {}
  for _, el in ipairs(list) do
    local t = el.t
    if t == "Para" or t == "Plain" or t == "Header" then
      local before = t == "Header" and heading_text(el.content)
      local stays = strip_children(el, strip_inlines)
      if before and heading_text(el.content) ~= before then reslug(el, before) end
      if stays then out:insert(el) end
    elseif t == "BlockQuote" or t == "Div" or t == "Figure" then
      if strip_children(el, strip_blocks) then out:insert(el) end
    elseif t == "BulletList" or t == "OrderedList" then
      local had, was_open, items = #el.content, open, pandoc.List {}
      for _, item in ipairs(el.content) do
        local was_open_item, kept = open, strip_blocks(item)
        if #kept > 0 or (#item == 0 and not was_open_item) then items:insert(kept) end
      end
      el.content = items
      if #items > 0 or (had == 0 and not was_open) then out:insert(el) end
    else
      check_verbatim(el)
      -- A table or similar is not walked, so one holding a `%%` is kept for
      -- the guard rather than dropped with the comment's close inside it.
      if not open or contains_mark(el) then out:insert(el) end
    end
  end
  return out
end

local function check_attrs(el)
  for _, value in pairs(el.attributes) do
    if has_mark(value) then fail(value) end
  end
end

local function check_target(el)
  check_attrs(el)
  if has_mark(el.title) then fail(el.title) end
end

local function comments(doc)
  local function take(el) taken[el.identifier] = true end
  doc:walk {
    Header = take, Div = take, Span = take, Figure = take, Table = take,
    CodeBlock = take, Code = take, Image = take, Link = take,
  }
  open, draft = false, doc.meta.draft == true
  doc.blocks = strip_blocks(doc.blocks)
  if draft then return doc end
  doc:walk {
    Str = function(el) if has_mark(el.text) then fail(el.text) end end,
    Link = check_target,
    Image = check_target,
    Span = check_attrs,
    Div = check_attrs,
    Header = check_attrs,
  }
  return doc
end

local function callout(quote)
  local first = quote.content[1]
  if not first or (first.t ~= "Para" and first.t ~= "Plain") then return nil end
  local head = first.content[1]
  if not head or head.t ~= "Str" then return nil end
  local kind, fold = head.text:match("^%[!([%w_-]+)%]([+-]?)$")
  if not kind then return nil end
  kind = kind:lower()

  -- The title runs to the end of the first line; the rest of it is body.
  local title, body = pandoc.Inlines {}, pandoc.Inlines {}
  local target = title
  for i = 2, #first.content do
    local el = first.content[i]
    if target == title and (el.t == "SoftBreak" or el.t == "LineBreak") then
      target = body
    elseif not (target == title and #title == 0 and el.t == "Space") then
      target:insert(el)
    end
  end
  if #title == 0 then
    title = pandoc.Inlines(kind:sub(1, 1):upper() .. kind:sub(2))
  end

  local blocks = pandoc.Blocks { pandoc.Header(2, title) }
  if #body > 0 then blocks:insert(pandoc.Para(body)) end
  for i = 2, #quote.content do blocks:insert(quote.content[i]) end

  local attrs = {}
  if fold == "-" then attrs.collapse = "true" end
  if fold == "+" then attrs.collapse = "false" end
  local class = "callout-" .. (CALLOUTS[kind] or "note")
  return pandoc.Div(blocks, pandoc.Attr("", { class }, attrs))
end

return {
  { Pandoc = comments },
  { BlockQuote = callout },
}
