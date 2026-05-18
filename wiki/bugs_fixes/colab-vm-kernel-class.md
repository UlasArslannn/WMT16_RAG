---
title: "Colab VM: google.colab._kernel.Kernel import failure on venv"
tags: [jupyter, kernel, colab, venv, ipython, vscode]
source: conversation-2026-05-18
date: 2026-05-18
status: fixed
---

# Colab VM: google.colab._kernel.Kernel import failure on venv

## Symptom

VSCode'da kendi venv'ini kernel olarak seçince kernel başlamıyor:

```
[IPKernelApp] CRITICAL | Bad config encountered during initialization:
The 'kernel_class' trait of <ipykernel.kernelapp.IPKernelApp object> instance
must be a type, but 'google.colab._kernel.Kernel' could not be imported
```

`ipykernel` kurulu olsa bile hata devam eder. Sistem Python'u (`Jupyter Kernel → python3`) ise sorunsuz çalışır.

## Root Cause

Bu ortam Google Colab altyapısı üzerinde çalışan bir VM (`~/.antigravity-server/` varlığı bunu gösterir). Google, `/etc/ipython/ipython_config.py` dosyasına sistem genelinde şu satırı eklemiş:

```python
c.IPKernelApp.kernel_class = 'google.colab._kernel.Kernel'
```

Sistem Python'unda `google.colab` paketi kurulu olduğu için çalışır. Venv'de bu paket olmadığı için import başarısız olur ve kernel patlıyor.

VSCode, venv kernel'ını kendi mekanizmasıyla doğrudan başlatır (`python -m ipykernel_launcher`); bu yüzden kernel spec'e eklenen `IPYTHONDIR` gibi env var override'ları işe yaramaz — sistem config her zaman yüklenir.

## Fix

`/etc/ipython/ipython_config.py` dosyasındaki kernel_class ve extensions atamalarını `try/except ImportError` ile koşullu hale getir:

```python
# Önce (bozuk):
c.IPKernelApp.kernel_class = 'google.colab._kernel.Kernel'
c.InteractiveShellApp.extensions = ['google.colab']
c.InteractiveShellApp.reraise_ipython_extension_failures = True

# Sonra (düzeltilmiş):
try:
    import google.colab._kernel
    c.IPKernelApp.kernel_class = 'google.colab._kernel.Kernel'
except ImportError:
    pass

try:
    import google.colab
    c.InteractiveShellApp.extensions = ['google.colab']
    c.InteractiveShellApp.reraise_ipython_extension_failures = True
except ImportError:
    pass
```

Bu sayede:
- Sistem Python'u (`google.colab` mevcut) → Colab kernel kullanılır, davranış değişmez
- Venv (`google.colab` yok) → varsayılan `ipykernel.ipkernel.IPythonKernel` kullanılır

## Normal Sistemlerde Durum

Bu sorun **sadece Colab VM'e özgüdür**. Normal Ubuntu/Debian sistemlerinde `/etc/ipython/ipython_config.py` ya yoktur ya da bu satırları içermez. Normal sistemde `uv venv .venv` + `uv pip install -r requirements.txt` + VSCode'da venv seçimi sorunsuz çalışır.

## İşe Yaramayan Yaklaşımlar

- `~/.ipython/profile_default/ipython_kernel_config.py`'ye override eklemek → VSCode kernel'ı doğrudan başlattığı için sistem config sonradan yüklenir, user config ezilir
- Kernel spec'e `"env": {"IPYTHONDIR": "..."}` eklemek → VSCode kayıtlı kernel spec'i kullanmayıp venv'i kendi başlatır, env var devreye girmez

## Related

- [[bugs_fixes/venv-ensurepip-ubuntu]]
- [[entities/notebooks]]
