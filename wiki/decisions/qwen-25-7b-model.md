---
title: "Model Selection: Qwen 2.5 7B Instruct"
tags: [decision, model, qwen, llm, quantization]
source: sources/2026-05-17-hw2-implementation.md
date: 2026-05-17
status: active
---

# Decision: Use Qwen 2.5 7B Instruct

**Status:** active  
**Date:** 2026-05-17

## Decision

Use `Qwen/Qwen2.5-7B-Instruct` with 4-bit NF4 quantization (bitsandbytes) as the translation LLM.

## Rationale

| Criterion | Justification |
|---|---|
| Hardware fit | 4-bit NF4 reduces memory to ~4-5GB VRAM → fits in 8-12GB |
| Multilingual support | Trained on 29+ languages including Turkish |
| Instruction-following | Reliably follows structured multi-step prompts (paper strategy) |
| Chat template | Official template via `apply_chat_template` |
| Context length | 128K tokens — handles long RAG prompts |
| Open weights | Available on HuggingFace, no API key |

## Quantization Config

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)
```

## Alternatives Considered

- **Mistral 7B Instruct** — good general instruction model but weaker on Turkish (primarily European language focus).
- **Qwen 2.5 14B** — better quality but doesn't fit in 8-12GB VRAM even with 4-bit quant.
- **GPT-4 via API** — would require API key and costs money; assignment requires local model.

## Sources
- [[sources/2026-05-17-hw2-implementation.md]]

## Related
- [[entities/modules-package]]
- [[decisions/faiss-over-chromadb]]
