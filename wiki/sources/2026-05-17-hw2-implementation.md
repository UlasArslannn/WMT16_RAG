---
title: "HW2 Implementation — RAG MT Pipeline"
tags: [implementation, rag, machine-translation, wmt16]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# HW2 Implementation — RAG MT Pipeline

## Goal

Build a full RAG-based machine translation pipeline for WMT16 English-Turkish as required by Homework 2. Implement three approaches (zero-shot, paper strategy, RAG 5-shot) and evaluate with COMET.

## What was done

- Created `requirements.txt` with all dependencies
- Built `modules/` package with 6 importable Python modules
- Created 6 Jupyter notebooks covering Parts 1–5
- Wrote `part3_summary.md` as literature review document
- Set up `data/` and `results/` directories (gitignored)

## Files changed

- `requirements.txt` — all Python dependencies
- `modules/__init__.py` — package marker
- `modules/dataset.py` — WMT16 loading, preprocessing, sampling
- `modules/model.py` — Qwen 2.5 7B loading with 4-bit quantization
- `modules/prompts.py` — zero-shot, paper strategy, RAG prompt templates
- `modules/translation.py` — three translation strategy functions
- `modules/retrieval.py` — FAISS index build/load, embedding, retrieval
- `modules/evaluation.py` — COMET scoring and multi-approach evaluation
- `notebooks/part1_dataset.ipynb` — dataset stats and preprocessing demo
- `notebooks/part2_model.ipynb` — model loading and hardware info
- `notebooks/part3d_prompting.ipynb` — zero-shot vs paper strategy evaluation
- `notebooks/part4a_architecture.ipynb` — RAG architecture diagram
- `notebooks/part4b_implementation.ipynb` — FAISS + RAG full pipeline
- `notebooks/part5_comparison.ipynb` — 3-way COMET comparison
- `part3_summary.md` — literature review (3-A, 3-B.1, 3-B.2, 3-C)
- `.gitignore` — excludes data/ and results/

## Decisions

- Use `faiss-cpu` (pure pip install, no server) over ChromaDB
- Use `Qwen/Qwen2.5-7B-Instruct` with 4-bit NF4 quantization for 8-12GB VRAM
- Use `paraphrase-multilingual-MiniLM-L12-v2` for multilingual embedding (EN + TR)
- Evaluate on 200 random test samples (seed=42) across all approaches for comparability
- Cache translations to `results/*.json` so Part 5 can load without re-running inference
- Cache FAISS index to `data/faiss_index.*` to avoid 15-30 min re-embedding

## Issues

- None during scaffolding. Actual COMET and model inference times unknown until runtime.

## Open threads

- Install `pip install -r requirements.txt` before running notebooks
- Run notebooks in order: 1 → 2 → 3d → 4a → 4b → 5
- Qwen model download (~15GB) requires HuggingFace access and disk space

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[entities/modules-package]]
- [[entities/notebooks]]
- [[concepts/rag-architecture]]
- [[concepts/comet-metric]]
- [[decisions/faiss-over-chromadb]]
- [[decisions/qwen-25-7b-model]]
