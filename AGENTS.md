# Tasty Bytes Knowledge Base

## Purpose
Maintain a self-updating Markdown wiki
about Snowflake Tasty Bytes.

## Sources
- snowflake_contents/ is the source of truth.
- Never modify source files.
- Preserve original URLs and version information.

## Wiki
- Generate Markdown files under wiki/.
- Write explanations in Japanese.
- Preserve original technical identifiers.
- Organize knowledge by entity, concept,
  data model, and tutorial.
- Merge knowledge from multiple sources.
- Add cross-references between related pages.

## Provenance
- Every factual claim must be traceable
  to source files or original URLs.
- Distinguish verified facts from inference.
- Preserve conflicting information when
  source versions differ.

## Incremental Updates
- Detect newly added, changed, and deleted sources.
- Update only affected wiki pages.
- Update cross-references and indexes.
- Remove unsupported claims from affected pages.

## Validation
- Check broken Markdown links.
- Check missing source references.
- Check duplicate entities.
- Check version conflicts.
- Never invent database schemas or SQL behavior.

## Repository Layout
- snowflake_contents/: upstream snapshots (read-only).
  Update only with snowflake_contents/_tools/import_contents.py
  and build_index.py (see snowflake_contents/_tools/README.md).
- wiki/: the Japanese knowledge base.
  - wiki/data-model/: entities, tables, data shapes, ER diagram.
  - wiki/tutorials/: per-tutorial views.
  - wiki/_meta/sources.json: cited sources and checksums
    (generated; do not edit by hand).
- notebooks/: Snowflake Notebooks built from the sources.
- tools/: shared helper scripts (Python standard library only).
- Only a small part of snowflake_contents/ is about Tasty Bytes.
  Start from snowflake_contents/catalog.json and
  wiki/tutorials/data-sources-by-tutorial.md.
  Most of github/common_resources/sfquickstarts/ is unrelated.
- Never cite files listed in PUSH_EXCLUSIONS.md;
  they are not in the GitHub checkout.

## Commands
- python3 tools/validate_wiki.py
  Check links, anchors, pinned commits, missing sources,
  duplicate titles. Must report 0 errors before committing.
- python3 tools/source_link.py <path> --from <page dir>
  Print a citation for a file under snowflake_contents/.
- python3 tools/wiki_sources.py diff
  List changed/deleted sources and the wiki pages they affect.
- python3 tools/wiki_sources.py snapshot
  Record cited sources after updating the wiki.

## Wiki Conventions
- Cite with tools/source_link.py. The format is
  [`file`](local path)（[原本](URL pinned to the commit)）.
- Mark statements not written in the sources with **[推測]**.
- Keep both sides of a version conflict and record it in
  wiki/data-model/version-differences.md.
- For in-page link targets, add <a id="..."></a>
  before the heading instead of relying on heading slugs.
- End each page with a 関連ページ list.
- Add every new page to wiki/README.md.
- Mermaid diagrams: solid lines only for joins used in
  source SQL or code; dotted lines for inferred relations.

## Notebook Conventions
- Copy DDL and COPY INTO options exactly from the sources,
  and name the source file in each section.
- If the notebook was not run on Snowflake, say so in the
  PR and the summary.

## Incremental Update Procedure
1. python3 tools/wiki_sources.py diff
2. Update only the listed pages; remove claims the new
   sources no longer support.
3. python3 tools/validate_wiki.py
4. python3 tools/wiki_sources.py snapshot
