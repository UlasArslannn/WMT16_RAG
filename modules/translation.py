"""
Translation generation functions for all three strategies.

Each function takes a list of source sentences and returns a list of translations.

Usage:
    from modules.translation import translate_zero_shot, translate_paper_strategy, translate_with_rag
"""

import json
import os
from tqdm import tqdm

from .model import generate
from .prompts import (
    zero_shot_prompt,
    paper_strategy_prompt,
    rag_prompt,
    extract_final_translation,
)


def translate_zero_shot(
    model,
    tokenizer,
    sentences: list[str],
    direction: str = "en->tr",
    save_path: str = None,
) -> list[str]:
    """
    Translate sentences using zero-shot prompting.

    Args:
        model: loaded LLM
        tokenizer: loaded tokenizer
        sentences: list of source sentences
        direction: "en->tr" or "tr->en"
        save_path: optional .json path to cache results

    Returns:
        list of translated strings
    """
    translations = []
    for sent in tqdm(sentences, desc="[Zero-shot] Translating"):
        prompt = zero_shot_prompt(sent, direction=direction)
        output = generate(model, tokenizer, prompt, max_new_tokens=256)
        translations.append(output)

    if save_path:
        _save_results(translations, save_path)

    return translations


def translate_paper_strategy(
    model,
    tokenizer,
    sentences: list[str],
    direction: str = "en->tr",
    save_path: str = None,
) -> list[str]:
    """
    Translate using the paper's 3-stage human-like strategy.
    Automatically extracts the final translation from the structured output.

    Args:
        model: loaded LLM
        tokenizer: loaded tokenizer
        sentences: list of source sentences
        direction: "en->tr" or "tr->en"
        save_path: optional .json path to cache results

    Returns:
        list of final translated strings
    """
    translations = []
    for sent in tqdm(sentences, desc="[Paper strategy] Translating"):
        prompt = paper_strategy_prompt(sent, direction=direction)
        final = ""
        for _attempt in range(3):
            # Longer output allowed to accommodate the 3-stage response
            output = generate(model, tokenizer, prompt, max_new_tokens=512)
            final = extract_final_translation(output)
            if final:
                break
        translations.append(final)

    if save_path:
        _save_results(translations, save_path)

    return translations


def translate_with_rag(
    model,
    tokenizer,
    sentences: list[str],
    retriever,
    direction: str = "en->tr",
    save_path: str = None,
) -> list[str]:
    """
    Translate using RAG-based dynamic few-shot prompting.

    Args:
        model: loaded LLM
        tokenizer: loaded tokenizer
        sentences: list of source sentences
        retriever: callable — retriever(query) → list of (src, tgt) examples
        direction: "en->tr" or "tr->en"
        save_path: optional .json path to cache results

    Returns:
        list of translated strings
    """
    translations = []
    for sent in tqdm(sentences, desc="[RAG] Translating"):
        examples = retriever(sent)
        prompt = rag_prompt(sent, examples, direction=direction)
        output = generate(model, tokenizer, prompt, max_new_tokens=256)
        translations.append(output)

    if save_path:
        _save_results(translations, save_path)

    return translations


def load_cached_translations(path: str) -> list[str]:
    """Load previously saved translations from a JSON file."""
    with open(path) as f:
        return json.load(f)


def _save_results(translations: list[str], path: str) -> None:
    """Save translations list to a JSON file."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(translations)} translations → {path}")
