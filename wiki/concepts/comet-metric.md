---
title: "COMET Evaluation Metric"
tags: [evaluation, metric, machine-translation, comet, bleu]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# COMET Evaluation Metric

## Definition

COMET (Crosslingual Optimized Metric for Evaluation of Translation) is a neural MT evaluation metric trained on human quality judgments (Direct Assessment scores from WMT campaigns).

**Model used:** `Unbabel/wmt22-comet-da`  
**Input:** source sentence + MT hypothesis + reference translation  
**Output:** scalar score ∈ [0, 1] (higher = better quality)

## How COMET Works

1. A multilingual encoder (XLM-R based) encodes all three inputs (source, hypothesis, reference).
2. A regression head predicts a quality score calibrated against human DA annotations.
3. System-level score = mean of all sentence-level scores.

COMET captures:
- **Semantic faithfulness** — is the meaning preserved?
- **Fluency** — does it read naturally in the target language?
- **Adequacy** — are all source elements translated?

## COMET vs. BLEU

| Aspect | BLEU | COMET |
|---|---|---|
| Approach | n-gram overlap (lexical) | Neural regression on human DA scores |
| Reference needed | Yes | Yes (reference-based variant) |
| Source used | No | Yes |
| Semantic understanding | No | Yes (XLM-R embeddings) |
| Correlation with humans | Moderate | High (state-of-the-art) |
| Score range | 0–100 | ~0–1 |
| Handles paraphrase | No (penalizes valid alternatives) | Yes |
| Morphologically rich languages | Degrades | Robust |

**Key point:** BLEU penalizes valid translations that use different words than the reference. COMET's neural approach captures semantic equivalence, making it far more reliable for Turkish (agglutinative, morphologically rich).

## Implementation

```python
from modules.evaluation import load_comet_model, compute_comet

comet_model = load_comet_model()
result = compute_comet(sources, hypotheses, references, comet_model)
print(result['system_score'])
```

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[concepts/rag-architecture]]
- [[concepts/prompting-strategies]]
