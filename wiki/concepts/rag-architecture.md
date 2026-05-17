---
title: "RAG Architecture for Machine Translation"
tags: [rag, retrieval, architecture, machine-translation]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# RAG Architecture for Machine Translation

## Overview

Retrieval-Augmented Generation (RAG) enhances LLM translation by dynamically selecting relevant example pairs from a corpus and injecting them as in-context demonstrations. Instead of static few-shot examples, each input sentence gets its own tailored set of examples based on semantic similarity.

## Two-Phase Pipeline

### Phase 1: Offline Indexing (one-time)

```
WMT16 Train Corpus (207K en-tr pairs)
        ↓
Multilingual Embedding Model (MiniLM)
        ↓ embed English side only
FAISS IndexFlatIP (384-dim, cosine similarity)
        ↓
Saved to disk: data/faiss_index.faiss + .pkl
```

Indexing cost: ~15-30 min on CPU for 207K pairs.

### Phase 2: Online Translation (per sentence)

```
Input EN sentence
        ↓
Embed with same MiniLM model
        ↓
FAISS search → Top-5 most similar EN sentences
        ↓
Retrieve corresponding (EN, TR) pairs
        ↓
Construct RAG prompt (5 examples + query)
        ↓
Qwen 2.5 7B Instruct → Turkish translation
```

Retrieval cost: <1ms per query (exact FAISS search).

## Key Components

| Component | Choice | Rationale |
|---|---|---|
| Vector DB | FAISS (faiss-cpu) | Pure pip install, no server, persistent |
| Embedding model | paraphrase-multilingual-MiniLM-L12-v2 | 50+ languages, 384-dim, fast |
| Similarity | Cosine (IndexFlatIP + L2-norm) | Standard for semantic similarity |
| k (examples) | 5 | Balances context richness vs. prompt length |
| LLM | Qwen 2.5 7B Instruct | Strong multilingual, fits in 8-12GB VRAM |

## Prompt Template

```
You are an expert English-to-Turkish translator.
Here are 5 similar translation examples for reference:

Example 1:
English: [retrieved_en_1]
Turkish: [retrieved_tr_1]
...
Example 5:
English: [retrieved_en_5]
Turkish: [retrieved_tr_5]

Now translate the following sentence. Output only the translation.

English: [query_sentence]
Turkish:
```

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[concepts/comet-metric]]
- [[concepts/prompting-strategies]]
- [[entities/modules-package]]
- [[decisions/faiss-over-chromadb]]
