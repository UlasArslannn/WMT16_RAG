"""
Dataset loading and preprocessing for WMT16 English-Turkish.

Usage:
    from modules.dataset import load_wmt16, get_samples, get_corpus
"""

import random
from datasets import load_dataset


def load_wmt16(split="test"):
    """
    Load WMT16 tr-en dataset from HuggingFace.

    Note: HuggingFace uses "tr-en" as the language pair key (alphabetical order).
    This function loads English ↔ Turkish data.

    Args:
        split: "train", "validation", or "test"

    Returns:
        HuggingFace Dataset object
    """
    print(f"Loading WMT16 tr-en [{split}] split...")
    ds = load_dataset("wmt16", "tr-en", split=split)
    print(f"  Loaded {len(ds)} sentence pairs.")
    return ds


def preprocess_pair(en: str, tr: str) -> tuple[str, str]:
    """
    Basic preprocessing for an English-Turkish sentence pair.
    - Strip leading/trailing whitespace
    - Collapse multiple spaces

    Args:
        en: English sentence
        tr: Turkish sentence

    Returns:
        (en_clean, tr_clean)
    """
    en = " ".join(en.strip().split())
    tr = " ".join(tr.strip().split())
    return en, tr


def get_samples(dataset, n: int = 200, seed: int = 42) -> tuple[list, list]:
    """
    Randomly sample n sentence pairs from a dataset split.

    Args:
        dataset: HuggingFace Dataset
        n: number of samples
        seed: random seed for reproducibility

    Returns:
        (en_sentences, tr_sentences) — two lists of strings
    """
    random.seed(seed)
    total = len(dataset)
    indices = random.sample(range(total), min(n, total))

    en_sentences, tr_sentences = [], []
    for idx in indices:
        item = dataset[idx]
        en, tr = preprocess_pair(
            item["translation"]["en"],
            item["translation"]["tr"],
        )
        if en and tr:
            en_sentences.append(en)
            tr_sentences.append(tr)

    print(f"Sampled {len(en_sentences)} pairs (seed={seed}).")
    return en_sentences, tr_sentences


def get_corpus(dataset, max_size: int = None) -> list[tuple[str, str]]:
    """
    Extract the full corpus as a list of (en, tr) tuples.
    Used for building the RAG retrieval index.

    Args:
        dataset: HuggingFace Dataset
        max_size: optional cap on corpus size

    Returns:
        list of (en, tr) tuples
    """
    pairs = []
    for item in dataset:
        en, tr = preprocess_pair(
            item["translation"]["en"],
            item["translation"]["tr"],
        )
        if en and tr:
            pairs.append((en, tr))
        if max_size and len(pairs) >= max_size:
            break

    print(f"Corpus size: {len(pairs)} pairs.")
    return pairs


def dataset_stats(dataset) -> dict:
    """
    Compute basic statistics for a dataset split.

    Returns:
        dict with keys: size, avg_en_len, avg_tr_len, max_en_len, max_tr_len
    """
    en_lens, tr_lens = [], []
    for item in dataset:
        en_lens.append(len(item["translation"]["en"].split()))
        tr_lens.append(len(item["translation"]["tr"].split()))

    return {
        "size": len(dataset),
        "avg_en_tokens": round(sum(en_lens) / len(en_lens), 1),
        "avg_tr_tokens": round(sum(tr_lens) / len(tr_lens), 1),
        "max_en_tokens": max(en_lens),
        "max_tr_tokens": max(tr_lens),
        "min_en_tokens": min(en_lens),
        "min_tr_tokens": min(tr_lens),
    }
