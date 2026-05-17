---
title: "Jupyter Notebooks"
tags: [entity, notebook, jupyter]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# Jupyter Notebooks

Six notebooks covering all homework parts. Run in order listed below.

## Execution Order

| # | File | Part | Content |
|---|---|---|---|
| 1 | `part1_dataset.ipynb` | Part 1 | WMT16 stats, preprocessing, sample pairs |
| 2 | `part2_model.ipynb` | Part 2 | GPU info, model loading, sanity check |
| 3 | `part3d_prompting.ipynb` | Part 3-D | Zero-shot vs paper strategy + COMET |
| 4 | `part4a_architecture.ipynb` | Part 4-A | RAG architecture diagram (no model needed) |
| 5 | `part4b_implementation.ipynb` | Part 4-B | FAISS index + RAG translation + COMET |
| 6 | `part5_comparison.ipynb` | Part 5 | 3-way comparison, charts, discussion |

## Dependencies Between Notebooks

```
part1 (standalone)
part2 (standalone)
part3d → produces: results/zero_shot_translations.json
                   results/paper_strategy_translations.json
                   results/part3_comet_scores.json
part4a (standalone — diagram only)
part4b → produces: data/faiss_index.*
                   results/rag_translations.json
                   results/part4_comet_scores.json
part5  → reads:    all results/*.json from parts 3d and 4b
```

## Common Imports Pattern

Every notebook begins with:
```python
import sys
sys.path.insert(0, '..')  # make modules/ importable
```

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[entities/modules-package]]
- [[concepts/rag-architecture]]
