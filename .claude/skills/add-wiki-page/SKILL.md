---
name: add-wiki-page
description: Add a new page to the Tasty Bytes wiki with source citations, cross-references, and an index entry. Use when the user asks to document a new topic, table, tutorial, or concept in wiki/.
---

# Add a wiki page

Follow "Wiki Conventions" in AGENTS.md. Steps:

1. Find the sources. Start from `snowflake_contents/catalog.json` and `wiki/tutorials/data-sources-by-tutorial.md`; search `snowflake_contents/` for the identifiers involved. Read the files you will cite.
2. Check for an existing page on the same entity or concept (`wiki/README.md`, `grep -r` in `wiki/`). Extend it instead of creating a duplicate.
3. Write the page in Japanese under `wiki/data-model/` (entities, tables, data) or `wiki/tutorials/` (per-tutorial).
   - Keep technical identifiers in their original spelling.
   - Cite every fact with `python3 tools/source_link.py <path> --from <page dir>`.
   - Mark anything not written in the sources with **[推測]**. Never invent schemas or SQL behavior.
   - Add `<a id="..."></a>` before headings that other pages will link to.
   - End with a 関連ページ list, and add a link back from the related pages.
4. Add the page to `wiki/README.md`.
5. Run `python3 tools/validate_wiki.py` (0 errors), then `python3 tools/wiki_sources.py snapshot`.
