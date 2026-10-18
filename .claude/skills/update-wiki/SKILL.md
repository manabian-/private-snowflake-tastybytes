---
name: update-wiki
description: Update the Tasty Bytes wiki after snowflake_contents/ changes. Finds changed or deleted sources, updates only the affected wiki pages, validates, and records the new snapshot. Use when sources were re-imported or the user asks to refresh the wiki.
---

# Update the wiki incrementally

Follow "Incremental Update Procedure" and "Wiki Conventions" in AGENTS.md. Steps:

1. Run `python3 tools/wiki_sources.py diff` and read the list of affected pages.
   - Exit code 0 means nothing changed: stop and say so.
2. For each affected page, re-read the changed source files and update only the statements that depend on them.
   - Remove claims the new source no longer supports.
   - If the old and new versions disagree, keep both and add the difference to `wiki/data-model/version-differences.md`.
   - Write citations with `python3 tools/source_link.py <path> --from <page dir>`.
3. For links newly added to `catalog.json`, decide whether they need a new page (use the `add-wiki-page` skill) or a change to an existing page.
4. Run `python3 tools/validate_wiki.py` until it reports 0 errors.
5. Run `python3 tools/wiki_sources.py snapshot` and commit `wiki/_meta/sources.json` with the page changes.
6. Report which pages changed and why, and anything left unresolved.
