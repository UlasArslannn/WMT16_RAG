---
title: "COMET: CUDA Out of Memory when Qwen model is loaded"
tags: [comet, cuda, oom, gpu, memory, qwen, evaluation]
source: conversation-2026-05-19
date: 2026-05-19
status: fixed
---

# COMET: CUDA Out of Memory when Qwen model is loaded

## Symptom

`compute_comet()` çağrısı `OutOfMemoryError` ile patlıyor:

```
OutOfMemoryError: CUDA out of memory. Tried to allocate 72.00 MiB.
GPU 0 has a total capacity of 22.03 GiB of which 53.69 MiB is free.
Process 15361 has 6.89 GiB memory in use.
Process 16545 has 6.88 GiB memory in use.
```

Hata `comet_model.predict()` → `trainer.predict()` → `model_to_device()` → `self.model.to(self.root_device)` zincirinde oluşur; COMET modeli GPU'ya taşınmaya çalışırken yer bulamıyor.

## Root Cause

GPU (22 GiB), Qwen 2.5 7B modeli yüklenmiş olduğu için dolmuş durumdadır (~13.7 GiB başka süreçlerde + mevcut process'in PyTorch allocations ~7.7 GiB). COMET modeli (XLM-R tabanlı, ~2 GiB) için yeterli alan kalmıyor.

Sorun şu sıralamayla oluşur:
1. Qwen modeli GPU'ya yüklenir ve çeviriler yapılır.
2. Qwen modeli bellekten silinmeden `load_comet_model()` çağrılır.
3. COMET modeli GPU'ya taşınmaya çalışır → OOM.

## Fix — Seçenek A: Qwen'i bellekten boşalt (önerilen)

COMET çağrısından önce Qwen modelini sil ve CUDA önbelleğini temizle:

```python
import torch, gc

del translation_model   # Qwen model değişken adı
gc.collect()
torch.cuda.empty_cache()

# Ardından COMET'i GPU'da çalıştır (hızlı)
rag_result = compute_comet(en_sentences, rag_translations, tr_references, comet_model)
```

Qwen'e tekrar ihtiyaç varsa evaluation bittikten sonra yeniden yükle.

## Fix — Seçenek B: COMET'i CPU'da çalıştır

GPU'yu serbest bırakmak istemiyorsan `gpus=0` ile CPU'da çalıştır:

```python
rag_result = compute_comet(
    en_sentences, rag_translations, tr_references, comet_model, gpus=0
)
```

`modules/evaluation.py`'deki `compute_comet` fonksiyonu `gpus` parametresini destekler (varsayılan: 1). CPU'da yavaş çalışır ama güvenilirdir.

## İşe Yaramayan / Kısmi Yaklaşımlar

- `batch_size` düşürmek: Modeli GPU'ya taşıma aşamasında OOM oluşuyor, batch boyutu bu noktada etkisiz.
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`: Fragmentation azaltır ama kök neden olan yetersiz toplam alan değişmez.

## Affected Files

- `modules/evaluation.py` — `compute_comet()` fonksiyonu, satır 42–76
- `notebooks/part4b_implementation.ipynb` — COMET evaluation hücresi

## Related

- [[decisions/qwen-25-7b-model]]
- [[concepts/comet-metric]]
- [[entities/modules-package]]
