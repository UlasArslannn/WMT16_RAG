"""
Prompt templates for all three translation strategies.

Strategies:
    1. zero_shot_prompt      — simple direct instruction
    2. paper_strategy_prompt — human-like 3-stage (analyze → draft → refine)
    3. rag_prompt            — 5-shot with dynamically retrieved examples

Usage:
    from modules.prompts import zero_shot_prompt, paper_strategy_prompt, rag_prompt
"""


def zero_shot_prompt(src: str, direction: str = "en->tr") -> str:
    """
    Zero-shot translation prompt.
    Instructs the model to translate and output only the translation.
    """
    src_lang = "English" if direction.startswith("en") else "Turkish"
    tgt_lang = "Turkish" if direction.endswith("tr") else "English"

    return (
        f"Translate the following {src_lang} sentence to {tgt_lang}. "
        f"Output only the translation, with no explanation or additional text.\n\n"
        f"{src_lang}: {src}\n"
        f"{tgt_lang}:"
    )


def paper_strategy_prompt(src: str, direction: str = "en->tr") -> str:
    """
    Multi-step human-like translation strategy.

    Based on: "Exploring Human-Like Translation Strategy with Large Language Models"

    Stage 1 — Pre-translation analysis: identify key terms, cultural refs, domain.
    Stage 2 — Draft translation: produce initial translation.
    Stage 3 — Review & refine (LLM-as-judge): evaluate draft and produce final version.

    The final translation is marked with "FINAL TRANSLATION: " for easy extraction.
    """
    src_lang = "English" if direction.startswith("en") else "Turkish"
    tgt_lang = "Turkish" if direction.endswith("tr") else "English"

    return (
        f"You are an expert {src_lang}-to-{tgt_lang} professional translator. "
        f"Follow the three steps below to produce a high-quality translation.\n\n"
        f"**Step 1 — Pre-translation Analysis**\n"
        f"Briefly note: key terminology, any cultural references, "
        f"the register/domain, and potential translation difficulties.\n\n"
        f"**Step 2 — Draft Translation**\n"
        f"Produce an initial {tgt_lang} translation of the sentence.\n\n"
        f"**Step 3 — Review and Refine**\n"
        f"Acting as an expert judge, evaluate your draft for: "
        f"(a) semantic accuracy, (b) fluency and naturalness in {tgt_lang}, "
        f"(c) appropriate register. "
        f"Then produce an improved final translation.\n\n"
        f"Write your final translation on its own line, "
        f'prefixed exactly with "FINAL TRANSLATION: "\n\n'
        f"{src_lang} text: {src}"
    )


def rag_prompt(
    src: str,
    examples: list[tuple[str, str]],
    direction: str = "en->tr",
) -> str:
    """
    RAG-based few-shot translation prompt.

    Args:
        src: source sentence to translate
        examples: list of (src_example, tgt_example) tuples retrieved from vector store
        direction: translation direction

    Returns:
        Prompt string with k-shot examples followed by the query sentence
    """
    src_lang = "English" if direction.startswith("en") else "Turkish"
    tgt_lang = "Turkish" if direction.endswith("tr") else "English"

    examples_block = "\n\n".join(
        f"Example {i + 1}:\n{src_lang}: {ex[0]}\n{tgt_lang}: {ex[1]}"
        for i, ex in enumerate(examples)
    )

    return (
        f"You are an expert {src_lang}-to-{tgt_lang} translator. "
        f"Here are {len(examples)} similar translation examples for reference:\n\n"
        f"{examples_block}\n\n"
        f"Now translate the following sentence. "
        f"Output only the translation, with no explanation.\n\n"
        f"{src_lang}: {src}\n"
        f"{tgt_lang}:"
    )


def extract_final_translation(output: str) -> str:
    """
    Extract the final translation from the paper strategy output.

    Looks for a line containing "FINAL TRANSLATION:" (case-insensitive).
    Handles Qwen's natural tendency to bold the marker: **FINAL TRANSLATION:**
    Also handles the translation being on the next line after the marker.
    Falls back to the last non-empty, non-markdown line if no marker is found.
    """
    import re

    lines = output.strip().splitlines()

    for i, line in enumerate(lines):
        if re.search(r"FINAL TRANSLATION\s*:", line, re.IGNORECASE):
            # Split on the marker and take everything after the colon
            after = re.split(r"FINAL TRANSLATION\s*:", line, maxsplit=1, flags=re.IGNORECASE)[1]
            # Strip any surrounding bold/markdown asterisks
            after = re.sub(r"^\s*\*+\s*", "", after)
            after = re.sub(r"\s*\*+\s*$", "", after).strip()

            if after:
                return after

            # Translation is on the line immediately after the marker
            if i + 1 < len(lines):
                next_line = re.sub(r"^\s*\*+\s*", "", lines[i + 1]).strip()
                if next_line:
                    return next_line

    # Fallback: last non-empty line that isn't pure markdown / step headers
    for line in reversed(lines):
        stripped = line.strip()
        if stripped and not re.fullmatch(r"[\*\s\-_#:]+", stripped):
            return stripped

    return output.strip()
