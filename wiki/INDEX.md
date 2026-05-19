# WMT16 RAG — Wiki Index

Master catalog of all wiki pages. Claude reads this first before fetching any page.
Last updated: 2026-05-17

---

## Sources
- [2026-05-17 hw2-implementation](sources/2026-05-17-hw2-implementation.md) — Full HW2 RAG MT pipeline implementation: modules, notebooks, decisions

---

## Entities
- [modules-package](entities/modules-package.md) — Six importable Python modules shared across all notebooks
- [notebooks](entities/notebooks.md) — Six Jupyter notebooks covering Parts 1–5, execution order and dependencies

---

## Concepts
- [rag-architecture](concepts/rag-architecture.md) — FAISS-based RAG pipeline: offline indexing + online retrieval + Qwen translation
- [comet-metric](concepts/comet-metric.md) — COMET neural MT metric: how it works, comparison with BLEU
- [prompting-strategies](concepts/prompting-strategies.md) — Zero-shot, paper strategy (MAPS), and RAG 5-shot prompting patterns

---

## Decisions
- [faiss-over-chromadb](decisions/faiss-over-chromadb.md) — status: active — chose faiss-cpu over ChromaDB for vector store
- [qwen-25-7b-model](decisions/qwen-25-7b-model.md) — status: active — chose Qwen 2.5 7B Instruct with 4-bit NF4 quantization

---

## Bugs & Fixes
- [venv-ensurepip-ubuntu](bugs_fixes/venv-ensurepip-ubuntu.md) — status: fixed — `python3 -m venv` ensurepip hatası Ubuntu/Debian'da, çözüm: `--without-pip` + `get-pip.py`
- [colab-vm-kernel-class](bugs_fixes/colab-vm-kernel-class.md) — status: fixed — Colab VM'de venv kernel'ı `google.colab._kernel` import hatasıyla başlamıyor, çözüm: `/etc/ipython/ipython_config.py`'yi koşullu hale getir
- [comet-cuda-oom](bugs_fixes/comet-cuda-oom.md) — status: fixed — COMET evaluation sırasında Qwen GPU'da yüklüyken OOM hatası; çözüm: Qwen'i boşalt veya `gpus=0` kullan

---

## Syntheses
<!-- High-level overviews spanning multiple sources -->

---

## Archive
<!-- Deprecated pages moved here — never deleted -->
