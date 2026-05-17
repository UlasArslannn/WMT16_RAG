# Persistent Project Wiki — Setup & Usage Guide

A cross-platform, Git-synced knowledge base for use with Claude Code on remote Linux servers (Colab, SSH, etc.). No GUI required on the server. Obsidian GUI is used only on your local Windows/Mac machine.

---

## Why This System Exists

When working on Linux servers (e.g., Google Colab via SSH):
- Servers restart and lose all local state
- Claude starts each session fresh with no memory of previous work
- Re-reading entire codebases every session wastes context and time

This system solves that by maintaining a structured wiki inside the Git repo. Claude reads only what is relevant to the current question — not everything at once.

---

## How It Works (Big Picture)

```
Linux Server                          Your Local Machine
─────────────────────────────         ──────────────────────────────
/project-root/                        C:\Users\you\Desktop\project\
├── wiki/          ← vault            ├── wiki/        ← same vault
│   ├── INDEX.md   ← map              │   ├── INDEX.md
│   └── ...                           │   └── ...
└── CLAUDE.md      ← auto-loaded      └── CLAUDE.md
        │
        │  git push / git pull
        ▼
    GitHub repo   ←────────────────── git clone / git pull
```

- Claude Code automatically loads `CLAUDE.md` at the project root every session
- That file is kept minimal (3 lines) — it just tells Claude where the real instructions are
- Claude reads `wiki/CLAUDE.md` and `wiki/INDEX.md` only when needed
- All detailed knowledge lives inside `wiki/` and travels via Git

---

## Folder Structure

```
/project-root/
├── CLAUDE.md                  ← AUTO-LOADED each session (keep it short)
│
└── wiki/                      ← Entire vault lives here
    ├── CLAUDE.md              ← Full instructions for Claude (workflows, rules)
    ├── INDEX.md               ← Master catalog of all pages by category
    ├── log.md                 ← Append-only timestamped event log
    │
    ├── raw/                   ← Source materials — NEVER modified
    │   └── .gitkeep
    │
    ├── sources/               ← One summary page per raw source
    │   └── .gitkeep           ← Format: YYYY-MM-DD-slug.md
    │
    ├── entities/              ← Files, functions, classes, services, APIs
    │   └── .gitkeep
    │
    ├── concepts/              ← Abstract ideas (e.g., RAG, BM25, chunking)
    │   └── .gitkeep
    │
    ├── decisions/             ← Architecture decisions — one page per decision
    │   └── .gitkeep
    │
    ├── bugs_fixes/            ← Issues: root cause + fix + affected files
    │   └── .gitkeep
    │
    ├── syntheses/             ← High-level overviews spanning multiple sources
    │   └── .gitkeep
    │
    └── archive/               ← Deprecated pages — moved here, never deleted
        └── .gitkeep
```

**Why `wiki/` as a subfolder?**
As the project grows, `src/`, `data/`, `notebooks/` etc. will appear at root. The vault should not mix with code.

---

## The Two-Layer CLAUDE.md System

### Layer 1 — `/project-root/CLAUDE.md` (3 lines, always loaded)

```markdown
# Project Wiki
Context and instructions are in wiki/CLAUDE.md
Always read wiki/INDEX.md before answering questions — fetch only relevant pages.
```

This file is loaded automatically by Claude Code on every session start.
It must stay short to avoid wasting context on every single interaction.

### Layer 2 — `/project-root/wiki/CLAUDE.md` (full instructions, loaded on demand)

Contains:
- Project purpose and scope
- Language and naming conventions
- Page format specification
- INGEST, QUERY, and LINT workflow definitions
- Hard rules Claude must follow

Claude reads this file only when it needs to perform a wiki operation — not on every message.

---

## Page Format

Every wiki page starts with YAML frontmatter:

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

**Status values:** `active` | `draft` | `archived`

**File naming:** kebab-case (e.g., `bm25-retriever.md`, `chunking-strategy.md`)

---

## Three Operations

### INGEST — When a new source arrives

Trigger: "ingest this file" or "add this to the wiki"

Steps Claude follows:
1. Read the file from `raw/`
2. Extract main topic, decisions, entities, issues, open questions
3. Write `sources/YYYY-MM-DD-slug.md` with: goal, what was done, files changed, decisions made, issues found, open threads
4. Create or update pages in `entities/`, `concepts/`, `decisions/`, `bugs_fixes/` as needed
5. Set up bidirectional links between all related pages
6. Append an entry to `log.md`
7. Update `INDEX.md`

### QUERY — When you ask a question

Trigger: any question about the project

Steps Claude follows:
1. Read `wiki/INDEX.md`
2. Identify which pages are relevant to the question
3. Read only those pages
4. Answer using sourced information

Claude does NOT read the entire vault. It fetches selectively based on the index.

### LINT — Periodic cleanup check

Trigger: "run a lint pass on the wiki"

Steps Claude follows:
1. Scan all pages for: orphan pages (no incoming links), missing cross-references, conflicting decisions, concepts without their own page
2. Write `wiki/lint-report.md` with findings
3. Does NOT auto-fix — reports only, you decide what to act on

---

## Hard Rules Claude Must Follow

| Rule | Detail |
|------|--------|
| `raw/` is immutable | Never write, edit, or delete files inside `raw/`. Read only. |
| No unsourced claims | Every statement in a wiki page must reference a source page |
| No deletion | Outdated pages are moved to `archive/`, never deleted |
| Mark conflicts | If two sources contradict each other, add a `## CONFLICT` section — do not silently resolve |
| No symbolic links | Always copy files into `raw/` directly. Symlinks break on Windows after `git pull` |
| Selective reading | Never read the entire vault at once. Always go through `INDEX.md` first |

---

## Why No Symbolic Links

The example instruction used `ln -s` to link raw files without copying them. This breaks the cross-platform workflow:

- On Linux: symlinks work fine
- After `git push` + `git pull` on Windows: Git cannot resolve symlinks without admin privileges — results in broken or empty files

**Solution:** Copy source files directly into `wiki/raw/`. The immutability rule is enforced by Claude's behavior (never writing there), not by the file system.

---

## Cross-Platform Workflow

### Setting up on a new Linux server

```bash
git clone <your-repo-url>
cd project-root
# wiki/ is already there from previous session — no reinstall needed
```

### Syncing changes from server to Windows

```bash
# On Linux server after making wiki changes:
git add wiki/
git commit -m "wiki: update after session"
git push

# On Windows:
git pull
# Open Obsidian → Open Folder as Vault → select project-root/wiki/
```

### Obsidian on Windows — setup once

1. Install Obsidian on Windows (one time only)
2. `git clone <repo>` to `C:\Users\you\Desktop\project-name`
3. Open Obsidian → **Open folder as vault** → select the `wiki/` subfolder
4. From now on: `git pull` to get latest, Obsidian auto-refreshes

You never install Obsidian on the Linux server. The server only needs Git.

---

## How to Start a New Project With This System

Copy and paste the following prompt to Claude at the start of a new project:

---

```
Set up a persistent wiki for this project following the WIKI_SETUP_GUIDE.md structure.

Steps:
1. Create wiki/ folder with subfolders: raw, sources, entities, concepts, decisions,
   bugs_fixes, syntheses, archive — each with a .gitkeep file
2. Create wiki/INDEX.md — empty skeleton with category sections
3. Create wiki/log.md — empty skeleton, append-only format
4. Write wiki/CLAUDE.md with:
   - Project purpose (ask me if unclear)
   - Language: English for all wiki pages
   - Naming: kebab-case filenames
   - Page format: YAML frontmatter (title, tags, source, date, status) + H1 + content + Sources + Related
   - INGEST, QUERY, LINT workflow definitions as described in WIKI_SETUP_GUIDE.md
   - Hard rules (raw/ immutable, no symlinks, no deletion, conflict marking)
5. Write root CLAUDE.md (3 lines max) pointing to wiki/CLAUDE.md and wiki/INDEX.md
6. Do NOT ingest anything yet — I will trigger the first ingest manually

Report: which folders were created, which files were written, line count of wiki/CLAUDE.md
```

---

## Summary

| What | Where |
|------|-------|
| Vault root | `project-root/wiki/` |
| Auto-loaded by Claude | `project-root/CLAUDE.md` (short) |
| Claude's full instructions | `project-root/wiki/CLAUDE.md` |
| Master map | `project-root/wiki/INDEX.md` |
| Event log | `project-root/wiki/log.md` |
| Raw sources (read-only) | `project-root/wiki/raw/` |
| Obsidian vault path (Windows) | `C:\...\project-root\wiki\` |
| Sync method | Git (no symlinks, no special tools) |
