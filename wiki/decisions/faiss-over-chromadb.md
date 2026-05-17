---
title: "Use FAISS over ChromaDB for Vector Store"
tags: [decision, vector-db, faiss, chromadb]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# Decision: Use FAISS over ChromaDB

**Status:** active  
**Date:** 2026-05-17

## Decision

Use `faiss-cpu` as the vector database for the RAG retrieval pipeline.

## Rationale

Both FAISS and ChromaDB are pure pip-install libraries — no system service required. FAISS was chosen because:

- **Lighter dependency tree** — faiss-cpu has minimal dependencies; ChromaDB pulls in SQLite, HTTP server components, and more.
- **Performance** — FAISS is a battle-tested library optimized for high-dimensional similarity search; for 50-207K vectors at 384 dim, `IndexFlatIP` gives exact results in milliseconds.
- **Persistence** — FAISS indexes are saved/loaded with `faiss.write_index / faiss.read_index`; corpus pairs are pickled alongside. Simple and transparent.
- **No server abstractions** — FAISS is a pure in-process library, which simplifies debugging and matches the research-notebook environment.

## Trade-offs

ChromaDB would offer a higher-level API with built-in metadata filtering and a more polished developer experience. For this project, those features are unnecessary.

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[concepts/rag-architecture]]
- [[entities/modules-package]]
