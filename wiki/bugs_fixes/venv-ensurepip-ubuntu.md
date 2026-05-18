---
title: "venv ensurepip failure on Ubuntu/Debian"
tags: [venv, python, ubuntu, debian, setup, pip]
source: conversation-2026-05-18
date: 2026-05-18
status: fixed
---

# venv ensurepip failure on Ubuntu/Debian

## Symptom

```
Error: Command '['/path/.venv/bin/python3', '-m', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1.
```

`python3 -m venv .venv` komutu çalışmıyor. `python3-venv` ve `python3-pip` kurulu olsa bile hata devam ediyor.

## Root Cause

Ubuntu/Debian'da `python3-venv` metapackage bazen Python sürümüne özel `ensurepip` modülünü içermiyor. Python 3.10 kullanan sistemlerde `python3.10-venv` paketi ayrıca kurulması gerekiyor.

## Fix

**Önce sürüme özel paketi dene:**

```bash
sudo apt install python3.10-venv
rm -rf .venv
python3 -m venv .venv
```

**Hâlâ çalışmazsa — pip olmadan oluştur, sonradan ekle:**

```bash
python3 -m venv .venv --without-pip
source .venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python3
```

> `--without-pip`: venv'i `ensurepip` çağırmadan oluşturur. `get-pip.py` pip'i manuel olarak kurar.

## Affected Environment

- Ubuntu 22.04 (apt package: `python3-venv 3.10.6-1~22.04.1`)
- Python 3.10 ve 3.12

## Sonraki Adım: requirements.txt

### Yöntem 1 — uv (önerilen)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env   # ya da yeni terminal aç
uv venv .venv
source .venv/bin/activate
uv pip install ipykernel
uv pip install -r requirements.txt
```

> `uv` ile venv kurmak için ensurepip/pip kurulumuna gerek yok — doğrudan `uv venv` ile oluşturulur.

### Yöntem 2 — pip (fallback, uv çalışmazsa)

Önce ensurepip sorununu çöz (yukarıdaki Fix adımları), sonra:

```bash
source .venv/bin/activate
pip install ipykernel
pip install -r requirements.txt
```

Kurulum **uzun sürer** (torch+transformers ağır paketler, 10-20 dk).

---

`requirements.txt` içeriği (bu proje):
- `torch`, `transformers`, `accelerate`, `bitsandbytes` — model
- `datasets` — HuggingFace WMT16 verisi
- `sentence-transformers`, `faiss-cpu` — RAG retrieval
- `unbabel-comet` — MT değerlendirme metriği
- `jupyter`, `matplotlib`, `seaborn`, `pandas`, `numpy`, `scikit-learn`, `tqdm` — notebook/görselleştirme

## Related

- [[entities/notebooks]]
- [[sources/2026-05-17-hw2-implementation]]
