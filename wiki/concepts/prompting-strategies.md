---
title: "Prompting Strategies for Machine Translation"
tags: [prompting, machine-translation, zero-shot, few-shot, chain-of-thought]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# Prompting Strategies for Machine Translation

## Three Strategies Implemented

### 1. Zero-Shot Prompting

Direct instruction with no examples. The model relies entirely on its pre-trained multilingual knowledge.

```
Translate the following English sentence to Turkish.
Output only the translation, with no explanation.

English: {source}
Turkish:
```

**Pros:** Fast, minimal tokens.  
**Cons:** No domain grounding, may miss terminology.

### 2. Paper's Multi-Step Strategy (MAPS)

Based on: *"Exploring Human-Like Translation Strategy with Large Language Models"*

Mimics how professional human translators work — analyze before translating, then refine.

**Stage 1 — Pre-translation Analysis:** identify key terms, cultural references, domain, difficulties.  
**Stage 2 — Draft Translation:** initial translation with context from Stage 1.  
**Stage 3 — Review & Refine (LLM-as-Judge):** evaluate draft against accuracy/fluency/register, produce final version.

Output is extracted via `FINAL TRANSLATION:` marker.

**Pros:** Catches terminology errors, improves fluency on complex sentences.  
**Cons:** ~2.5× slower than zero-shot, ~2× longer output.

### 3. RAG Dynamic 5-Shot

Retrieves 5 semantically similar (EN, TR) pairs from the WMT16 train corpus and uses them as in-context demonstrations.

**Pros:** Domain-grounded vocabulary, consistent terminology, only ~1.1× slower than zero-shot.  
**Cons:** Requires index build; quality depends on corpus quality.

## Patterns

### Break Complex Tasks into Simpler Subtasks
The paper strategy implements this by decomposing translation into 3 sequential prompts (analyze → draft → refine), reducing the cognitive load of each step.

### LLM as a Judge
Stage 3 of the paper strategy uses the LLM to evaluate and critique its own draft, then rewrite. Advantages: no reference needed, holistic evaluation. Limitations: positional bias, no calibration, adds inference pass.

## Implementation

```python
from modules.prompts import zero_shot_prompt, paper_strategy_prompt, rag_prompt
from modules.translation import translate_zero_shot, translate_paper_strategy, translate_with_rag
```

## Sources
- [[sources/2026-05-17-hw2-implementation]]

## Related
- [[concepts/rag-architecture]]
- [[concepts/comet-metric]]
