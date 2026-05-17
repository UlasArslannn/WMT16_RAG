# WMT16 RAG — Wiki Instructions for Claude

## Project Purpose

A Retrieval-Augmented Generation (RAG) system built on the WMT16 machine translation dataset.
Goal: index WMT16 translation pairs and related corpora, build a retrieval pipeline,
and serve relevant segments as context for a language model.

## Language & Naming

- All wiki pages are written in English
- File names: kebab-case (e.g., `bm25-retriever.md`, `chunking-strategy.md`)
- Dates: ISO 8601 (YYYY-MM-DD)

## Page Format

Every wiki page must follow this structure:

```markdown
---
title: "Page Title"
tags: [tag1, tag2, category]
source: sources/YYYY-MM-DD-slug.md
date: YYYY-MM-DD
status: active
---

# Page Title

Content here.

## Sources
- [[sources/YYYY-MM-DD-slug]]

## Related
- [[concepts/related-concept]]
- [[decisions/related-decision]]
```

Status values: `active` | `draft` | `archived`

---

## Operations

### INGEST

Trigger: user says "ingest", "add to wiki", or provides a file/script/log to process.

Steps:
1. Read the file from `wiki/raw/`
2. Extract: main topic, what was done, files touched, decisions made, issues encountered, open questions
3. Write `wiki/sources/YYYY-MM-DD-<slug>.md` with sections:
   - **Goal** — what this source was trying to accomplish
   - **What was done** — concrete actions taken
   - **Files changed** — list of files with one-line descriptions
   - **Decisions** — choices made and the reasoning behind them
   - **Issues** — problems encountered
   - **Open threads** — unresolved questions or next steps
4. For each entity mentioned (file path, function, class, service, API): create or update `wiki/entities/<name>.md`, add bidirectional link to this source
5. For each architectural/design decision: create `wiki/decisions/<slug>.md` (one decision per page)
6. For each bug or fix: create `wiki/bugs_fixes/<slug>.md` with root cause + fix + affected files
7. For each abstract concept (retrieval strategy, model type, metric, etc.): create or update `wiki/concepts/<slug>.md`
8. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <slug>
   - Pages touched: [list]
   ```
9. Update `wiki/INDEX.md` — add the new source and any new entities/concepts/decisions

### QUERY

Trigger: any question about the project.

Steps:
1. Read `wiki/INDEX.md`
2. Identify which categories and pages are relevant to the question
3. Read only those pages — do not read the entire vault
4. Answer using sourced information, citing page names

### LINT

Trigger: user says "lint the wiki" or "run a lint pass".

Steps:
1. Scan all pages for:
   - Orphan pages — pages with no incoming links from other wiki pages
   - Missing cross-references — entities/concepts mentioned in text but not linked
   - Conflicting decisions — two decision pages that contradict each other
   - Concepts referenced in sources but without their own concepts/ page
2. Write `wiki/lint-report.md` with findings grouped by category
3. Do NOT auto-fix anything — report only, user decides what to act on

---

## Hard Rules

| Rule | Detail |
|------|--------|
| `wiki/raw/` is immutable | Never write, edit, or delete files in raw/. Read only. |
| No unsourced claims | Every factual statement must reference a source page |
| No deletion | Move outdated pages to `wiki/archive/` — never delete |
| Mark conflicts | If sources contradict each other, add `## CONFLICT` section — do not silently resolve |
| No symbolic links | Files in raw/ are direct copies — symlinks break on Windows after git pull |
| Selective reading | Always go through INDEX.md first — never read entire vault at once |
| One decision per page | Each decisions/ page covers exactly one decision |
| Bidirectional links | When page A references page B, page B must also reference page A |

---

## Folder Reference

```
wiki/
├── raw/          source files (read-only)
├── sources/      one summary per raw file  →  YYYY-MM-DD-slug.md
├── entities/     files, functions, classes, services, APIs
├── concepts/     abstract ideas (retrieval, chunking, evaluation, etc.)
├── decisions/    architectural decisions — one page per decision
├── bugs_fixes/   issues: root cause + fix + affected files
├── syntheses/    high-level overviews spanning multiple sources
├── archive/      deprecated pages — moved here, never deleted
├── INDEX.md      master catalog — always read this first
├── log.md        append-only event log
└── CLAUDE.md     this file
```
