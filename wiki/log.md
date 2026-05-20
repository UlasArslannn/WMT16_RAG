# Event Log

Append-only. Never edit or delete past entries. Always add new entries at the bottom.
Format: `## [YYYY-MM-DD] operation | slug`

---

## [2026-05-17] setup | wiki-initialized
- Created wiki/ folder structure: raw, sources, entities, concepts, decisions, bugs_fixes, syntheses, archive
- Created INDEX.md, log.md, wiki/CLAUDE.md
- Created root CLAUDE.md
- No sources ingested yet — awaiting first manual ingest trigger

## [2026-05-17] ingest | hw2-implementation
- Pages touched: sources/2026-05-17-hw2-implementation.md, concepts/rag-architecture.md, concepts/comet-metric.md, concepts/prompting-strategies.md, decisions/faiss-over-chromadb.md, decisions/qwen-25-7b-model.md, entities/modules-package.md, entities/notebooks.md, INDEX.md
- Full HW2 RAG pipeline scaffolded: 6 modules, 6 notebooks, part3_summary.md, requirements.txt

## [2026-05-18] bug | venv-ensurepip-ubuntu
- Pages touched: bugs_fixes/venv-ensurepip-ubuntu.md, INDEX.md
- Ubuntu 22.04'te python3 -m venv ensurepip hatası ve çözümü: --without-pip + get-pip.py

## [2026-05-18] bug | colab-vm-kernel-class
- Pages touched: bugs_fixes/colab-vm-kernel-class.md, INDEX.md
- Colab VM'de venv kernel'ı google.colab._kernel import hatasıyla başlamıyor
- Çözüm: /etc/ipython/ipython_config.py'deki kernel_class atamasını try/except ile koşullu hale getir

## [2026-05-20] bug | maps-extraction-failure
- Pages touched: bugs_fixes/maps-extraction-failure.md, concepts/prompting-strategies.md, INDEX.md
- MAPS yöntemi zero-shot'tan daha kötü çıkıyordu (0.7194 vs 0.7509 COMET)
- Kök neden: Qwen `**FINAL TRANSLATION:**` bold format kullanıyor, extract_final_translation bunu parse edemiyordu
- 200 çevirinin 40'ı (%20) bozuktu: 27 adet `****`, 3 boş, 10 adet `** text`
- Çözüm: regex ile case-insensitive arama, `**` strip, bir sonraki satıra bakış, max_new_tokens 512→768
- Düzeltme sonrası MAPS'ın ~0.82 COMET ile zero-shot'u geçmesi bekleniyor

## [2026-05-19] bug | comet-cuda-oom
- Pages touched: bugs_fixes/comet-cuda-oom.md, concepts/comet-metric.md, INDEX.md
- COMET evaluation sırasında Qwen modeli GPU'da yüklü olduğu için OOM hatası
- Çözüm A: Qwen'i del + gc.collect() + torch.cuda.empty_cache() ile boşalt
- Çözüm B: compute_comet(..., gpus=0) ile CPU'da çalıştır

