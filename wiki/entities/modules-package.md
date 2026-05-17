---
title: "modules/ — Python Package"
tags: [entity, python, package, module]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# modules/ — Python Package

Importable Python package shared across all notebooks. Each module has a single responsibility and can be imported independently.

## Module Map

| File | Key exports | Responsibility |
|---|---|---|
| `dataset.py` | `load_wmt16`, `get_samples`, `get_corpus`, `dataset_stats` | WMT16 loading and preprocessing |
| `model.py` | `load_model`, `generate`, `gpu_info` | Qwen 2.5 7B loading and inference |
| `prompts.py` | `zero_shot_prompt`, `paper_strategy_prompt`, `rag_prompt`, `extract_final_translation` | All prompt templates |
| `translation.py` | `translate_zero_shot`, `translate_paper_strategy`, `translate_with_rag`, `load_cached_translations` | Translation strategy functions |
| `retrieval.py` | `load_embedding_model`, `build_faiss_index`, `retrieve_examples`, `make_retriever` | FAISS index and retrieval |
| `evaluation.py` | `load_comet_model`, `compute_comet`, `evaluate_all`, `print_results_table` | COMET evaluation |

## Usage from Notebooks

```python
import sys
sys.path.insert(0, '..')  # notebooks/ → project root

from modules.dataset import load_wmt16, get_samples
from modules.model import load_model, generate
from modules.prompts import zero_shot_prompt
from modules.translation import translate_zero_shot
from modules.retrieval import load_embedding_model, build_faiss_index, make_retriever
from modules.evaluation import load_comet_model, compute_comet
```

## Caching Convention

- Translations cached to `results/<approach>_translations.json`
- COMET scores cached to `results/part<n>_comet_scores.json`
- FAISS index cached to `data/faiss_index.faiss` + `data/faiss_index.pkl`

All cache paths are relative to the project root (one level above `notebooks/`).

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[concepts/rag-architecture]]
- [[concepts/prompting-strategies]]
- [[entities/notebooks]]
